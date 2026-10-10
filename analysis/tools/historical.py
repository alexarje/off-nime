"""Build bibs/Historical/historical.bib: precursors of NIME topics published before 1957, the year of
the first MUSIC program, from tools/historical_seeds.txt.

The seeds are works on musical instruments, their classification and electronic or mechanical
sound production: those found in the archives' reference lists (output/candidates_historical.tsv
and output/candidates_cited.tsv) and standard precursors chosen by hand. General science that
archive papers cite (Shannon, Wiener, Fitts) belongs to Background, and musical works to neither.

Each seed is checked against a catalogue: Crossref for articles (which also gives the DOI), Open
Library for books, Google Patents for patents (title and issue year come from there when it has
them). A seed that fails its check stays in the dataset, with a note asking for vetting. Lookups
are cached in data/historical_lookup.json. The number of archive papers citing each work is
counted from the candidate lists by first author and year.
"""
import json
import re
import sys
import time
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

import requests

from crossref import API, get, item_year
from parse_refs import letters

HERE = Path(__file__).resolve().parent.parent
SEEDS = HERE / "tools" / "historical_seeds.txt"
CACHE = HERE / "data" / "historical_lookup.json"
OUT = HERE.parent / "bibs" / "Historical" / "historical.bib"
LAST_YEAR = 1956
HEAD = {"User-Agent": "off-nime-analysis/0.1 (https://github.com/alexarje/off-nime)"}
FIELDS = ["origin", "type", "author", "year", "title", "container", "volume", "number", "pages"]


def plain(s):
    return letters(unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode())


def surnames(author):
    return [plain(a.split(",")[0].split()[-1]) for a in author.split(" and ") if a.strip()]


def similar(a, b):
    a, b = plain(a), plain(b)
    n = min(len(a), len(b), 40)
    return SequenceMatcher(None, a[:n], b[:n]).ratio() if n else 0


def check_article(s):
    d = get(f"{API}/works", {"query.bibliographic": f"{s['title']} {s['author'].split(',')[0]} {s['container']}",
                             "rows": 5, "select": "DOI,title,author,issued,published-print,container-title"})
    for it in (d or {}).get("message", {}).get("items", []):
        t = (it.get("title") or [""])[0]
        y = item_year(it)
        names = {plain(a.get("family", "")) for a in it.get("author") or []}
        if similar(t, s["title"]) >= 0.85 and y and abs(y - int(s["year"])) <= 1 and \
                (not names or set(surnames(s["author"])) & names or s["author"] == "Anonymous"):
            return {"ok": True, "by": "Crossref", "doi": it["DOI"].lower()}
    return {"ok": False, "by": "Crossref"}


def check_book(s):
    time.sleep(1)
    r = requests.get("https://openlibrary.org/search.json", headers=HEAD, timeout=60,
                     params={"title": s["title"].split(":")[0], "author": s["author"].split(",")[0],
                             "limit": 10, "fields": "key,title,author_name,first_publish_year"})
    for doc in r.json().get("docs", []) if r.ok else []:
        names = {plain(n.split()[-1]) for n in doc.get("author_name", []) if n.split()}
        if similar(doc.get("title", ""), s["title"]) >= 0.75 and set(surnames(s["author"])) & names:
            return {"ok": True, "by": "Open Library", "url": f"https://openlibrary.org{doc['key']}",
                    "first_year": doc.get("first_publish_year")}
    return {"ok": False, "by": "Open Library"}


def check_patent(s):
    num = s["container"]
    if not re.match(r"(US|GB)\d+$", num):
        return {"ok": False, "by": "Google Patents"}
    time.sleep(1)
    r = requests.get(f"https://patents.google.com/patent/{num}A/en", headers=HEAD, timeout=60)
    if not r.ok:
        return {"ok": False, "by": "Google Patents"}
    meta = lambda pat: re.findall(pat, r.text)
    title = (meta(r'name="DC.title" content="([^"]*)"') or [""])[0].strip()
    issued = meta(r'name="DC.date" content="(\d{4})-[\d-]+" scheme="issue"')
    inventors = " ".join(meta(r'name="DC.contributor" content="([^"]*)" scheme="inventor"'))
    found = set(plain(w) for w in inventors.split())
    ok = not inventors or bool(set(surnames(s["author"])) & found)
    return {"ok": ok, "by": "Google Patents", "url": f"https://patents.google.com/patent/{num}A/en",
            # old scans carry only the inventor's name, in lower case, as their title
            "title": title if title[:1].isupper() else "", "year": int(issued[0]) if issued else None}


def cited_by():
    counts = {}
    for name, cols in (("candidates_historical.tsv", (0, 1, 2)), ("candidates_cited.tsv", (0, 4, 3))):
        lines = (HERE / "output" / name).read_text().splitlines()[1:]
        for l in lines:
            f = l.split("\t")
            n, first, year = f[cols[0]], f[cols[1]], f[cols[2]]
            if year.isdigit():
                k = (plain(first), int(year))
                counts[k] = max(counts.get(k, 0), int(n))
    return counts


def main():
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    seeds = []
    for line in SEEDS.read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            vals = [v.strip() for v in line.split("|")]
            seeds.append(dict(zip(FIELDS, vals + [""] * (len(FIELDS) - len(vals)))))
    for s in seeds:
        key = f"{s['type']}|{s['author']}|{s['title']}|{s['container']}"
        if key not in cache:
            cache[key] = {"article": check_article, "book": check_book, "patent": check_patent}[s["type"]](s)
            CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1))
        s["check"] = cache[key]
        if s["type"] == "patent":
            s["title"] = s["check"].get("title") or s["title"]
            s["year"] = str(s["check"].get("year") or s["year"])
    counts = cited_by()
    for s in seeds:
        y = int(s["year"])
        # the parsed first author is a surname, or a given name when a reference puts it first
        names = {plain(w) for w in re.split(r"[ ,]+", s["author"].split(" and ")[0]) if len(plain(w)) >= 3} \
            if s["author"] != "Anonymous" else {"unknown"}
        near = lambda d: max([n for (c, yy), n in counts.items() if abs(yy - y) <= d and c in names] + [0])
        # a found work gives its own year; a seed taken from the reference lists may be dated by
        # another edition there (Russolo's manifesto of 1913, the book of 1916)
        s["cited_by"] = near(0) or (near(3) if s["origin"] == "cited" else 0)
        s["names"] = names
    # counts go by first author and year, so a hand-chosen work by the same author in the same year
    # as a work from the reference lists (Dudley's vocoder and his synthetic speaker, 1939) gets none
    taken = {(n, s["year"]) for s in seeds if s["origin"] == "cited" for n in s["names"]}
    for s in seeds:
        if s["origin"] == "canonical" and any((n, s["year"]) in taken for n in s["names"]):
            s["cited_by"] = 0
    problems = [f"{s['author']} {s['year']}: {why}" for s in seeds for why in
                (["after %d" % LAST_YEAR] if int(s["year"]) > LAST_YEAR else []) + (["no title"] if not s["title"] else [])
                + (["from the reference lists, but no citing paper counted"] if s["origin"] == "cited" and not s["cited_by"] else [])]
    write_bib(seeds)
    ok = sum(s["check"]["ok"] for s in seeds)
    print(f"{len(seeds)} works, {ok} found in a catalogue, {sum(s['cited_by'] > 0 for s in seeds)} cited by archive papers",
          file=sys.stderr)
    for s in seeds:
        if not s["check"]["ok"]:
            print(f"  not found ({s['check']['by']}): {s['author']} {s['year']} {s['title'][:60]}", file=sys.stderr)
    for p in problems:
        print("  problem:", p, file=sys.stderr)
    return 1 if problems else 0


def write_bib(seeds):
    OUT.parent.mkdir(exist_ok=True)
    keys = set()
    with open(OUT, "w") as f:
        for s in sorted(seeds, key=lambda s: int(s["year"])):
            key = f"historical:{surnames(s['author'])[0] or 'anon'}{s['year']}{plain(s['title'])[:12]}"
            while key in keys:
                key += "b"
            keys.add(key)
            c = s["check"]
            kind = {"article": "article", "book": "book", "patent": "misc"}[s["type"]]
            note = "; ".join(x for x in [
                f"Patent {s['container']}" if s["type"] == "patent" else "",
                f"Cited by {s['cited_by']} archive papers" if s["cited_by"] > 1 else
                "Cited by 1 archive paper" if s["cited_by"] == 1 else "Chosen by hand as a precursor",
                f"Found in {c['by']}" if c["ok"] else f"Not found in {c['by']}: vet",
            ] if x)
            fields = [("author", "" if s["author"] == "Anonymous" else s["author"]), ("title", s["title"]),
                      ("journal" if kind == "article" else "publisher", "" if kind == "misc" else s["container"]),
                      ("year", s["year"]), ("volume", s["volume"]), ("number", s["number"]),
                      ("pages", s["pages"].replace("-", "--")), ("doi", c.get("doi")),
                      ("url", c.get("url") if not c.get("doi") else None), ("collection", "Historical"), ("note", note)]
            f.write(f"@{kind}{{{key},\n" + ",\n".join(f"  {k} = {{{re.sub(r'[{}]', '', str(v))}}}" for k, v in fields if v)
                    + "\n}\n\n")


if __name__ == "__main__":
    sys.exit(main())
