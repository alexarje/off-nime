"""Fetch abstracts for off-NIME entries, which carry titles only in the bib files.

Semantic Scholar is asked first, in batches, for every off-NIME entry it has matched; Crossref
fills gaps for entries with a DOI. Abstracts go to data/abstracts.json, which build_corpus.py
merges into the corpus; the curated bib files are not changed.
"""
import json
import re
import sys
import time
from pathlib import Path

from crossref import API as CR, get as cr_get
from fetch_s2 import API as S2, cache_path, call

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "data" / "abstracts.json"


def clean(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    s = re.sub(r"^\s*abstract\s*", "", s, flags=re.I)
    return re.sub(r"\s+", " ", s).strip()


def main():
    corpus = json.loads((HERE / "data" / "corpus.json").read_text())
    have = json.loads(OUT.read_text()) if OUT.exists() else {}
    off = [r for r in corpus if r["archive"] == "off-nime" and not r["abstract"] and r["id"] not in have]
    pids = []
    for r in off:
        c = cache_path(r["id"])
        if c.exists():
            p = json.loads(c.read_text())["paper"]
            if p and p.get("paperId"):
                pids.append((r["id"], p["paperId"]))
    for i in range(0, len(pids), 100):
        chunk = pids[i:i + 100]
        res = call("POST", f"{S2}/paper/batch", params={"fields": "abstract"}, json={"ids": [p for _, p in chunk]})
        for (rid, _), p in zip(chunk, res or []):
            a = clean((p or {}).get("abstract"))
            if len(a) > 80:
                have[rid] = {"abstract": a, "source": "Semantic Scholar"}
        time.sleep(3)
    print(f"Semantic Scholar: {len(have)}", file=sys.stderr)
    for r in off:
        if r["id"] in have or not r["doi"]:
            continue
        d = cr_get(f"{CR}/works/{r['doi']}", {})
        a = clean(((d or {}).get("message") or {}).get("abstract"))
        if len(a) > 80:
            have[r["id"]] = {"abstract": a, "source": "Crossref"}
    OUT.write_text(json.dumps(have, ensure_ascii=False, indent=0))
    n_off = sum(1 for r in corpus if r["archive"] == "off-nime")
    print(f"{len(have)} of {n_off} off-NIME entries have an abstract", file=sys.stderr)


if __name__ == "__main__":
    main()
