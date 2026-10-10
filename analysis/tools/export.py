"""Export the joined collection (NIME proceedings, off-NIME and Cited) in open formats.

Writes output/collection.csv (one row per entry, for spreadsheets) and output/collection.json
(CSL-JSON, which Zotero, Mendeley and pandoc import). Each entry carries the archive and dataset
it comes from, and its strongest topic from the topic model.
"""
import csv
import json
import re
from pathlib import Path

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

from build_corpus import split_authors

HERE = Path(__file__).resolve().parent.parent
CSL = {"article": "article-journal", "inproceedings": "paper-conference", "book": "book",
       "incollection": "chapter", "phdthesis": "thesis", "mastersthesis": "thesis", "techreport": "report",
       "proceedings": "book", "misc": "document"}


def main():
    corpus = json.loads((HERE / "data" / "corpus.json").read_text())
    graph = json.loads((HERE / "data" / "graph.json").read_text())
    topic = {p["id"]: p["tp"] for p in graph["papers"]}
    labels = {t["id"]: ", ".join(t["terms"][:3]) for t in graph["topics"]}
    rows = [dict(r, collection=r["dataset"]) for r in corpus]
    for name in ("Cited", "Theses", "Related", "Background"):
        cited = HERE.parent / "bibs" / name / f"{name.lower()}.bib"
        if not cited.exists():
            continue
        parser = BibTexParser(common_strings=True)
        parser.customization = convert_to_unicode
        for e in bibtexparser.loads(cited.read_text(), parser=parser).entries:
            au = split_authors(e.get("author") or e.get("editor") or "")
            rows.append({"id": e["ID"], "archive": name.lower(), "dataset": name, "collection": name,
                         "type": e["ENTRYTYPE"], "year": int(e["year"]) if e.get("year", "").isdigit() else None,
                         "title": e.get("title", ""), "names": [n for _, n in au],
                         "venue": e.get("journal") or e.get("booktitle") or e.get("publisher") or e.get("school") or "",
                         "channel": "", "doi": e.get("doi"), "url": e.get("url"), "note": e.get("note", "")})
    with open(HERE / "output" / "collection.csv", "w", newline="") as f:
        w = csv.writer(f)
        trl = {m["id"]: m for m in json.loads((HERE / "data" / "trl.json").read_text())} if (HERE / "data" / "trl.json").exists() else {}
        w.writerow(["id", "archive", "dataset", "type", "year", "authors", "title", "venue", "channel", "doi", "url",
                     "topic", "trl_estimate", "trl_band", "arl_estimate", "arl_band", "estimate_confidence"])
        for r in rows:
            w.writerow([r["id"], r["archive"], r["dataset"], r["type"], r["year"] or "", "; ".join(r["names"]),
                        r["title"], r["venue"], r["channel"], r["doi"] or "", r["url"] or "",
                        labels.get(topic.get(r["id"]), "")] +
                       [(trl.get(r["id"]) or {}).get(k) or "" for k in ("trl", "trl_band", "arl", "arl_band", "confidence")])
    csl = []
    for r in rows:
        item = {"id": r["id"], "type": CSL.get(r["type"], "document"), "title": r["title"],
                "author": [{"family": n.split()[-1], "given": " ".join(n.split()[:-1])} for n in r["names"] if n.split()],
                "container-title": r["venue"] or None, "DOI": r["doi"] or None, "URL": r["url"] or None,
                "note": f"Collection: {r['collection']}" + (f". {r['note']}" if r.get("note") else "")}
        if r["year"]:
            item["issued"] = {"date-parts": [[r["year"]]]}
        csl.append({k: v for k, v in item.items() if v})
    (HERE / "output" / "collection.json").write_text(json.dumps(csl, ensure_ascii=False, indent=0))
    print(f"{len(rows)} entries exported")


if __name__ == "__main__":
    main()
