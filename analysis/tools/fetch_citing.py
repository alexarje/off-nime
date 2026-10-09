"""Fetch, for every corpus entry found in Semantic Scholar, the works that cite it.

Forward citations are not elided for the Zenodo-hosted NIME papers, unlike reference lists,
so this is the route to the literature that builds on the archives: journals, conferences
and theses outside NIME that cite many NIME and off-NIME papers. Cached in data/s2_citing/.
"""
import json
import sys
import time
from pathlib import Path

from fetch_s2 import API, call, cache_path

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "data" / "s2_citing"
OUT.mkdir(parents=True, exist_ok=True)
FIELDS = "paperId,citationCount," + ",".join(
    f"citations.{f}" for f in ["paperId", "title", "year", "venue", "externalIds", "authors", "citationCount",
                               "publicationTypes"])


def main():
    corpus = json.loads((HERE / "data" / "corpus.json").read_text())
    todo = []
    for r in corpus:
        c = cache_path(r["id"])
        dest = OUT / c.name
        if not c.exists() or dest.exists():
            continue
        p = json.loads(c.read_text())["paper"]
        if p and p.get("paperId"):
            todo.append((r["id"], p["paperId"], dest))
    print(f"{len(todo)} to fetch", file=sys.stderr)
    for i in range(0, len(todo), 100):
        chunk = todo[i:i + 100]
        res = call("POST", f"{API}/paper/batch", params={"fields": FIELDS}, json={"ids": [c[1] for c in chunk]})
        for (rid, pid, dest), p in zip(chunk, res):
            dest.write_text(json.dumps({"id": rid, "paper": p}))
        print(f"batch {i // 100 + 1}", file=sys.stderr, flush=True)
        time.sleep(3)


if __name__ == "__main__":
    main()
