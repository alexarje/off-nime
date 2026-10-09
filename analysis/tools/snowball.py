"""One round of snowballing from the reference lists of the Cited works.

The Crossref records fetched for bibs/Cited/ include reference lists where publishers deposit
them. Every cited work is keyed by DOI, or by title when no DOI is given, and counted once per
citing Cited work. Works already in either archive or in Cited are left out. Writes
output/candidates_snowball.tsv (works cited by at least MIN_SOURCES Cited works) and
data/snowball.json.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

import bibtexparser

from crossref import API, get
from parse_refs import title_key

HERE = Path(__file__).resolve().parent.parent
MIN_SOURCES = 3
VENUE = re.compile(r"proceedings|conference|symposium|workshop|extended abstracts|journal|transactions|"
                   r"\bacm\b|\bieee\b|\bicmc\b|\bnime\b|\bchi\b", re.I)


def main():
    corpus = json.loads((HERE / "data" / "corpus.json").read_text())
    have_doi = {r["doi"] for r in corpus if r["doi"]}
    have_key = {title_key(r["title"]) for r in corpus if title_key(r["title"])}
    cited = bibtexparser.load(open(HERE.parent / "bibs" / "Cited" / "cited.bib")).entries
    for e in cited:
        have_doi.add(e.get("doi", "").lower())
        have_key.add(title_key(e.get("title", "")))

    counts, meta = defaultdict(set), {}
    with_refs = 0
    for e in cited:
        doi = e.get("doi", "").lower()
        rec = (get(f"{API}/works/{doi}", {}) or {}).get("message") or {}
        refs = rec.get("reference") or []
        if refs:
            with_refs += 1
        for ref in refs:
            rdoi = (ref.get("DOI") or "").lower()
            title = ref.get("article-title") or ""
            vt = ref.get("volume-title") or ""
            # a volume title names a book when it stands alone, but a proceedings or journal name
            # would pool unrelated papers under one key
            if not title and vt and not VENUE.search(vt):
                title = vt
            if not title and not rdoi and ref.get("unstructured"):
                m = re.search(r"[“\"]([^”\"]{15,200})[”\"]", ref["unstructured"])
                title = m.group(1) if m else ""
            key = rdoi or title_key(title)
            if not key or rdoi in have_doi or (title and title_key(title) in have_key):
                continue
            counts[key].add(doi)
            m = meta.setdefault(key, {"doi": rdoi, "title": title, "author": ref.get("author", ""),
                                      "year": ref.get("year", ""), "raw": ref.get("unstructured", "")})
            if not m["title"] and title:
                m["title"] = title
    # works keyed by DOI with no title in the reference: look the title up (for those that could
    # reach the threshold once merged with a title-keyed twin)
    for k in [k for k, s in counts.items() if len(s) >= 2]:
        m = meta[k]
        if m["doi"] and not m["title"]:
            rec = (get(f"{API}/works/{m['doi']}", {}) or {}).get("message") or {}
            m["title"] = re.sub(r"<[^>]+>", "", (rec.get("title") or [""])[0])
            m["year"] = m["year"] or str(((rec.get("issued") or {}).get("date-parts") or [[""]])[0][0])
            fam = [a.get("family", "") for a in rec.get("author", [])]
            m["author"] = m["author"] or (fam[0] if fam else "")
    # merge works counted under both a DOI and a title, now that DOI-keyed works have titles
    merged = {}
    for k, srcs in counts.items():
        tk = title_key(meta[k]["title"]) or k
        if tk in merged:
            merged[tk]["src"] |= srcs
            if meta[k]["doi"] and not merged[tk]["k_doi"]:
                merged[tk]["k_doi"] = k
        else:
            merged[tk] = {"src": set(srcs), "k": k, "k_doi": k if meta[k]["doi"] else None}
    rows = sorted(((len(v["src"]), v["k_doi"] or v["k"]) for v in merged.values() if len(v["src"]) >= MIN_SOURCES),
                  reverse=True)
    # titles looked up after counting can reveal a version of an archive entry; drop those
    rows = [(n, k) for n, k in rows if not (meta[k]["title"] and title_key(meta[k]["title"]) in have_key)
            and not VENUE.match(meta[k]["title"] or "")]
    with open(HERE / "output" / "candidates_snowball.tsv", "w") as f:
        f.write("cited_by_cited_works\tyear\tfirst_author\ttitle\tdoi\n")
        for n, k in rows:
            m = meta[k]
            f.write("\t".join(re.sub(r"\s+", " ", str(x)) for x in [n, m["year"], m["author"], m["title"] or m["raw"][:200],
                                                                  m["doi"]]) + "\n")
    stats = {"cited_works": len(cited), "with_reference_lists": with_refs, "distinct_cited": len(counts),
             "candidates": len(rows), "min_sources": MIN_SOURCES}
    (HERE / "data" / "snowball.json").write_text(json.dumps(stats))
    print(json.dumps(stats))
    for n, k in rows[:25]:
        print(n, meta[k]["year"], meta[k]["author"], "|", (meta[k]["title"] or meta[k]["raw"])[:80])


if __name__ == "__main__":
    main()
