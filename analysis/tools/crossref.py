"""Crossref lookups: resolve the cited-but-missing works to DOIs, and sweep journals by ISSN.

resolve: each work in output/candidates_cited.tsv is searched by title, first author and year;
a hit is accepted when its title matches closely (difflib ratio at least 0.9 on letters) and its
year is within two of the parsed year. Writes output/candidates_cited.bib.

sweep: every article in the journals below, and music-related papers in the CHI and TEI
proceedings, are fetched with their abstracts where Crossref has them. Writes data/journals.json.
Responses are cached in data/crossref/.
"""
import hashlib
import json
import re
import sys
import time
from difflib import SequenceMatcher
from pathlib import Path

import requests

from parse_refs import letters

HERE = Path(__file__).resolve().parent.parent
CACHE = HERE / "data" / "crossref"
CACHE.mkdir(parents=True, exist_ok=True)
API = "https://api.crossref.org"
HEAD = {"User-Agent": "off-nime-analysis/0.1 (https://github.com/alexarje/off-nime)"}
JOURNALS = {
    "Computer Music Journal": ["0148-9267", "1531-5169"],
    "Organised Sound": ["1355-7718", "1469-8153"],
    "Journal of New Music Research": ["0929-8215", "1744-5027"],
    "Leonardo Music Journal": ["0961-1215", "1531-4812"],
    "Contemporary Music Review": ["0749-4467", "1477-2256"],
    "ACM Transactions on Computer-Human Interaction": ["1073-0516", "1557-7325"],
    "Personal and Ubiquitous Computing": ["1617-4909", "1617-4917"],
}
PROCEEDINGS = {
    "CHI": "Human Factors in Computing Systems",
    "TEI": "Tangible Embedded and Embodied Interaction",
    "Audio Mostly": "Audio Mostly",
    "MOCO": "Movement and Computing",
    "DIS": "Designing Interactive Systems",
    "Creativity and Cognition": "Creativity and Cognition",
}


def get(url, params):
    key = hashlib.sha1((url + json.dumps(params, sort_keys=True)).encode()).hexdigest()
    f = CACHE / f"{key}.json"
    if f.exists():
        return json.loads(f.read_text())
    wait = 2
    for _ in range(8):
        try:
            r = requests.get(url, params=params, headers=HEAD, timeout=90)
            if r.status_code == 200:
                d = r.json()
                f.write_text(json.dumps(d))
                time.sleep(1.1)
                return d
            if r.status_code == 404:
                return None
            print(f"  {r.status_code}, waiting {wait} s", file=sys.stderr)
        except requests.RequestException as ex:
            print(f"  {ex}", file=sys.stderr)
        time.sleep(wait)
        wait = min(wait * 2, 60)
    raise RuntimeError(url)


def item_year(it):
    for k in ("published-print", "published-online", "issued", "created"):
        dp = (it.get(k) or {}).get("date-parts")
        if dp and dp[0] and dp[0][0]:
            return dp[0][0]
    return None


def bib_escape(s):
    return re.sub(r"[{}]", "", str(s))


def author_ok(it, first):
    """The parsed first author must be among the hit's authors or editors, since works with the
    same title by different people are common (a book and a review of it, for instance)."""
    if not first:
        return True
    names = {letters(a.get("family", "")) for a in (it.get("author") or []) + (it.get("editor") or [])}
    return letters(first.split()[-1]) in names


def resolve():
    rows = [l.split("\t") for l in (HERE / "output" / "candidates_cited.tsv").read_text().splitlines()[1:]]
    out, n_ok = [], 0
    for n, f in enumerate(rows):
        cited_by, _, _, year, first, title = f[:6]
        q = f"{title} {first} {year}"
        d = get(f"{API}/works", {"query.bibliographic": q, "rows": 3,
                                 "select": "DOI,title,author,issued,published-print,published-online,container-title,type,publisher,page,volume,issue"})
        best = None
        for it in (d or {}).get("message", {}).get("items", []):
            t = (it.get("title") or [""])[0]
            ratio = SequenceMatcher(None, letters(t), letters(title)).ratio()
            y = item_year(it)
            if ratio >= 0.9 and (not year or not y or abs(int(year) - y) <= 2) and author_ok(it, first):
                best = (it, ratio)
                break
        if not best and len(f) > 7 and f[7]:
            # second attempt with the raw reference string, which is what Crossref's bibliographic
            # query is built for; accept a hit whose whole title appears in the reference
            raw = letters(f[7])
            d = get(f"{API}/works", {"query.bibliographic": f[7][:400], "rows": 3,
                                     "select": "DOI,title,author,issued,published-print,published-online,container-title,type,publisher,page,volume,issue"})
            for it in (d or {}).get("message", {}).get("items", []):
                t = letters((it.get("title") or [""])[0])
                y = item_year(it)
                if len(t) >= 15 and t in raw and (not year or not y or abs(int(year) - y) <= 2) and author_ok(it, first):
                    best = (it, 1.0)
                    break
        rec = {"cited_by": int(cited_by), "title": title, "first": first, "year": year}
        if best:
            it = best[0]
            n_ok += 1
            rec.update({"doi": it["DOI"], "cr_title": it["title"][0], "cr_year": item_year(it), "type": it.get("type"),
                        "container": (it.get("container-title") or [""])[0], "publisher": it.get("publisher", ""),
                        "authors": [f"{a.get('family', '')}, {a.get('given', '')}".strip(", ") for a in it.get("author", [])],
                        "pages": it.get("page"), "volume": it.get("volume"), "issue": it.get("issue")})
        out.append(rec)
        if n % 50 == 0:
            print(f"resolve {n}/{len(rows)}", file=sys.stderr, flush=True)
    kinds = {"journal-article": "article", "proceedings-article": "inproceedings", "book": "book",
             "monograph": "book", "book-chapter": "incollection", "edited-book": "book"}
    with open(HERE / "output" / "candidates_cited.bib", "w") as f:
        f.write("% Works cited by at least five NIME or off-NIME papers and held by neither archive.\n"
                "% Generated by analysis/tools/crossref.py; entries without a DOI were not found in Crossref\n"
                "% and carry only what was parsed from the reference strings. Not curated.\n\n")
        for r in out:
            sur = re.sub(r"[^a-z]", "", (r.get("authors") or [r["first"]])[0].split(",")[0].lower()) or "anon"
            yr = r.get("cr_year") or r["year"] or ""
            key = f"{sur}{yr}{re.sub(r'[^a-z]', '', letters(r.get('cr_title') or r['title'])[:12])}"
            kind = kinds.get(r.get("type"), "misc")
            fields = [("author", " and ".join(r.get("authors") or []) or r["first"].title()),
                      ("title", r.get("cr_title") or r["title"]), ("year", yr)]
            if kind == "article":
                fields.append(("journal", r.get("container")))
            elif kind in ("inproceedings", "incollection"):
                fields.append(("booktitle", r.get("container")))
            fields += [("publisher", r.get("publisher") if kind in ("book", "incollection") else None),
                       ("volume", r.get("volume")), ("number", r.get("issue")),
                       ("pages", (r.get("pages") or "").replace("-", "--") or None),
                       ("doi", r.get("doi")), ("note", f"Cited by {r['cited_by']} archive papers")]
            f.write(f"@{kind}{{{key},\n" + ",\n".join(f"  {k} = {{{bib_escape(v)}}}" for k, v in fields if v) + "\n}\n\n")
    (HERE / "data" / "cited_resolved.json").write_text(json.dumps(out, ensure_ascii=False, indent=0))
    print(f"resolved {n_ok} of {len(out)}", file=sys.stderr)


def sweep():
    sel = "DOI,title,author,issued,published-print,published-online,container-title,type,abstract,volume,issue,page"
    items = []
    for name, issns in JOURNALS.items():
        seen = set()
        for issn in issns:
            cursor = "*"
            while True:
                d = get(f"{API}/journals/{issn}/works", {"rows": 1000, "cursor": cursor, "select": sel})
                if not d:
                    break
                msg = d["message"]
                for it in msg["items"]:
                    if it["DOI"] not in seen:
                        seen.add(it["DOI"])
                        items.append((name, it))
                if not msg["items"] or not msg.get("next-cursor") or len(msg["items"]) < 1000:
                    break
                cursor = msg["next-cursor"]
        print(f"{name}: {len(seen)}", file=sys.stderr, flush=True)
    for name, ct in PROCEEDINGS.items():
        n = 0
        for q in ["music", "musical", "sound"]:
            d = get(f"{API}/works", {"query.container-title": ct, "query.bibliographic": q, "rows": 1000,
                                     "filter": "type:proceedings-article", "select": sel})
            for it in (d or {}).get("message", {}).get("items", []):
                c = " ".join(it.get("container-title") or [])
                t = " ".join(it.get("title") or [])
                if re.search(ct.split()[0], c, re.I) and re.search(r"music|sound|sonic|audio|instrument", t, re.I):
                    items.append((name, it))
                    n += 1
        print(f"{name}: {n}", file=sys.stderr, flush=True)
    out, seen = [], set()
    for name, it in items:
        if it["DOI"] in seen or not it.get("title"):
            continue
        seen.add(it["DOI"])
        out.append({"source": name, "doi": it["DOI"], "title": it["title"][0], "year": item_year(it),
                    "authors": [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in it.get("author", [])],
                    "container": (it.get("container-title") or [""])[0], "type": it.get("type"),
                    "abstract": re.sub(r"<[^>]+>", " ", it.get("abstract") or "").strip(),
                    "volume": it.get("volume"), "issue": it.get("issue"), "pages": it.get("page")})
    (HERE / "data" / "journals.json").write_text(json.dumps(out, ensure_ascii=False))
    print(f"{len(out)} items", file=sys.stderr)


if __name__ == "__main__":
    {"resolve": resolve, "sweep": sweep}[sys.argv[1]]()
