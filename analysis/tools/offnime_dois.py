"""Find DOIs for off-NIME entries that have none, and add the certain ones to the bib files.

A Crossref hit is accepted when its title matches at a difflib ratio of at least 0.95 (letters
only), its year equals the entry's year (one year either way for conference papers, whose
proceedings often appear the year after), and the entry's first-author surname is among the
hit's authors, and the hit is the same kind of publication (a report does not take its
journal version's DOI). Accepted DOIs are inserted into the entry as a `doi` field; near misses go to
output/offnime_dois_review.tsv. Run with --apply to edit the bib files; without it, only the
lists are written.
"""
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

from crossref import API, get, item_year
from parse_refs import letters

HERE = Path(__file__).resolve().parent.parent
# a DOI must belong to the same kind of publication: a report's journal version is another work
TYPES = {"article": {"journal-article"}, "inproceedings": {"proceedings-article", "book-chapter"},
         "book": {"book", "monograph", "edited-book", "reference-book"},
         "incollection": {"book-chapter", "book-section", "proceedings-article"},
         "phdthesis": {"dissertation"}, "mastersthesis": {"dissertation"}, "techreport": {"report"},
         "proceedings": {"proceedings", "book"}, "misc": set()}
BIBS = HERE.parent / "bibs"


def main(apply):
    corpus = json.loads((HERE / "data" / "corpus.json").read_text())
    todo = [r for r in corpus if r["archive"] == "off-nime" and not r["doi"] and r["title"] and r["names"]]
    sel = "DOI,title,author,issued,published-print,published-online,container-title,type"
    accepted, review = [], []
    for n, r in enumerate(todo):
        sur = letters(r["names"][0].split()[-1])
        d = get(f"{API}/works", {"query.bibliographic": f"{r['title']} {r['names'][0]} {r['year']}", "rows": 3,
                                 "select": sel})
        best = None
        for it in (d or {}).get("message", {}).get("items", []):
            t = (it.get("title") or [""])[0]
            ratio = SequenceMatcher(None, letters(t), letters(r["title"])).ratio()
            y = item_year(it)
            fams = {letters(a.get("family", "")) for a in it.get("author", [])}
            slack = 1 if r["type"] == "inproceedings" else 0
            ok_year = y is not None and abs(y - r["year"]) <= slack
            ok_type = it.get("type") in TYPES.get(r["type"], set())
            if ratio >= 0.95 and ok_year and sur in fams and ok_type:
                best = it
                break
            if ratio >= 0.85 and best is None and not (ratio >= 0.95 and ok_year and sur in fams and ok_type):
                review.append([r["id"], r["file"], r["year"], r["title"], it["DOI"], y, t, round(ratio, 3),
                               "; ".join(a.get("family", "") for a in it.get("author", [])[:4])])
        if best:
            accepted.append((r, best["DOI"].lower()))
        if n % 100 == 0:
            print(f"{n}/{len(todo)}, {len(accepted)} accepted", file=sys.stderr, flush=True)

    with open(HERE / "output" / "offnime_dois.tsv", "w") as f:
        f.write("id\tfile\tyear\ttitle\tdoi\n")
        for r, doi in accepted:
            f.write("\t".join(str(x) for x in [r["id"], r["file"], r["year"], r["title"], doi]) + "\n")
    with open(HERE / "output" / "offnime_dois_review.tsv", "w") as f:
        f.write("id\tfile\tyear\ttitle\tcandidate_doi\tcandidate_year\tcandidate_title\tratio\tcandidate_authors\n")
        for row in review:
            f.write("\t".join(re.sub(r"\s+", " ", str(x)) for x in row) + "\n")
    summary = {"without_doi": len(todo), "accepted": len(accepted), "review": len(review)}
    if apply:
        edited = 0
        for r, doi in accepted:
            path = HERE.parent / r["file"]
            # keep the file's own line endings; some ISIDM files use CRLF
            with open(path, encoding="utf-8", newline="") as fh:
                s = fh.read()
            nl = "\r\n" if "\r\n" in s else "\n"
            key = r["id"].split(":", 1)[1]
            m = re.search(r"@\w+\{" + re.escape(key) + r",", s)
            if not m:
                continue
            depth, j = 0, s.index("{", m.start())
            for j in range(j, len(s)):
                depth += s[j] == "{"
                depth -= s[j] == "}"
                if depth == 0:
                    break
            entry = s[m.start():j]
            if re.search(r"^\s*doi\s*=", entry, re.M | re.I):
                continue
            indent = re.search(r"\n([ \t]*)[A-Za-z]+\s*=", entry)
            indent = indent.group(1) if indent else ""
            body = entry.rstrip()
            sep = "" if body.endswith(",") else ","
            s = s[:m.start()] + body + f"{sep}{nl}{indent}doi = {{{doi}}}{nl}" + s[j:]
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(s)
            edited += 1
        summary["edited"] = edited
    (HERE / "data" / "offnime_dois.json").write_text(json.dumps(summary))
    print(json.dumps(summary), file=sys.stderr)


if __name__ == "__main__":
    main("--apply" in sys.argv)
