"""Write the next TRL/ARL input batch (data/trl/in_NN.jsonl) for entries without an estimate.

Entries join the collection when the rule-selected datasets are rebuilt; they need estimates by
an agent following tools/trl_rubric.md, which writes the matching out_NN.jsonl. merge_trl.py
then merges every batch. Prints the batch name and its size, or nothing to do.
"""
import json
import re
from pathlib import Path

import bibtexparser

HERE = Path(__file__).resolve().parent.parent
D = HERE / "data" / "trl"


def main():
    done = set()
    for f in D.glob("out_*.jsonl"):
        done |= {json.loads(l)["id"] for l in f.read_text().splitlines() if l.strip()}
    todo = []
    for r in json.loads((HERE / "data" / "corpus.json").read_text()):
        if r["id"] not in done:
            todo.append({"id": r["id"], "dataset": r["dataset"], "year": r["year"], "title": r["title"],
                         "venue": r.get("venue") or r.get("channel") or "", "abstract": r.get("abstract") or ""})
    for name in ("Cited", "Background", "Theses", "Related", "Historical", "Zotero"):
        f = HERE.parent / "bibs" / name / f"{name.lower()}.bib"
        for e in bibtexparser.load(open(f)).entries if f.exists() else []:
            if e["ID"] not in done:
                todo.append({"id": e["ID"], "dataset": name, "year": int(re.sub(r"\D", "", e.get("year", "0")) or 0),
                             "title": e.get("title", ""),
                             "venue": e.get("journal") or e.get("booktitle") or e.get("publisher") or e.get("school") or "",
                             "abstract": e.get("abstract", "")})
    if not todo:
        print("nothing to do")
        return
    n = 1 + max(int(re.sub(r"\D", "", f.stem)) for f in D.glob("in_*.jsonl"))
    out = D / f"in_{n:02d}.jsonl"
    out.write_text("".join(json.dumps(t, ensure_ascii=False) + "\n" for t in todo))
    print(out.name, len(todo))


if __name__ == "__main__":
    main()
