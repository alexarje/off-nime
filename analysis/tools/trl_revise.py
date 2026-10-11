"""Write revision input batches (data/trl/rev_in_NN.jsonl) for estimates to be made again after a
change to tools/trl_rubric.md.

Selects merged estimates (data/trl.json) by dataset and current level, and splits them into
batches of SIZE. Each entry carries its previous estimate. With --kind trl the agent re-estimates
the TRL only and writes id, trl and trl_reason; merge_trl.py then keeps the ARL and its reason.

Usage: trl_revise.py --kind trl --datasets "NIME music,NIME installations" --levels 5,7
"""
import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
D = HERE / "data" / "trl"
SIZE = 95


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=("trl", "both"), default="both")
    ap.add_argument("--datasets", required=True)
    ap.add_argument("--levels", required=True, help="current levels of the scale being revised")
    a = ap.parse_args()
    datasets, levels = set(a.datasets.split(",")), {int(x) for x in a.levels.split(",")}
    scale = "trl" if a.kind == "trl" else "arl"
    todo = [{"id": m["id"], "dataset": m["dataset"], "year": m["year"], "title": m["title"],
             "venue": m.get("venue", ""), "abstract": m.get("abstract") or "", "revise": a.kind,
             "previous": {k: m.get(k) for k in ("trl", "arl", "confidence", "reason", "trl_reason") if m.get(k)}}
            for m in json.loads((HERE / "data" / "trl.json").read_text())
            if m["dataset"] in datasets and m[scale] in levels]
    n = 1 + max((int(re.sub(r"\D", "", f.stem)) for f in D.glob("rev_in_*.jsonl")), default=0)
    for i in range(0, len(todo), SIZE):
        out = D / f"rev_in_{n:02d}.jsonl"
        out.write_text("".join(json.dumps(t, ensure_ascii=False) + "\n" for t in todo[i:i + SIZE]))
        print(out.name, len(todo[i:i + SIZE]))
        n += 1


if __name__ == "__main__":
    main()
