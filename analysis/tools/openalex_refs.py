"""Reference lists from OpenAlex for entries whose text the reference parser cannot read.

The parser needs a full text, and three groups have none: the NIME papers of 2021 and 2022 (on
PubPub, behind a bot check), a few later NIME papers, and most of the off-NIME archive. OpenAlex
holds reference lists for many of them, keyed by DOI. This script fetches them for every corpus
entry with a DOI and no text, then the title, year, first author and DOI of each referenced work,
and writes data/openalex_refs.json ({entry id: [reference, ...]}), which parse_refs.py merges with
the parsed references.

OpenAlex charges list requests against a small free daily allowance; the remaining allowance is
read from the response headers and the script stops before it runs out. Results are cached in
data/openalex_refs_cache.json, so a stopped run resumes the next day.
"""
import json
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent.parent
CACHE = HERE / "data" / "openalex_refs_cache.json"
OUT = HERE / "data" / "openalex_refs.json"
API = "https://api.openalex.org/works"
HEAD = {"User-Agent": "off-nime-analysis/0.1 (https://github.com/alexarje/off-nime)"}
BATCH = 50
STOP_USD = 0.005


class Budget(Exception):
    pass


def fetch(params):
    for attempt in range(5):
        r = requests.get(API, params=params, headers=HEAD, timeout=120)
        left = r.headers.get("x-ratelimit-remaining-usd")
        if left is not None and float(left) < STOP_USD:
            raise Budget(left)
        if r.status_code == 429:
            time.sleep(10 * (attempt + 1))
            continue
        r.raise_for_status()
        time.sleep(0.2)
        return r.json()["results"]
    raise Budget("rate limited")


def main():
    from parse_refs import text_sources
    corpus = json.loads((HERE / "data" / "corpus.json").read_text())
    sources, _ = text_sources(corpus)
    todo = {r["doi"].lower(): r["id"] for r in corpus
            if r.get("doi") and r["id"] not in sources and r["dataset"] not in ("NIME music", "NIME installations")}
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {"refs": {}, "works": {}}
    try:
        dois = [d for d in todo if d not in cache["refs"]]
        for i in range(0, len(dois), BATCH):
            chunk = dois[i:i + BATCH]
            res = fetch({"filter": "doi:" + "|".join(chunk), "per-page": BATCH, "select": "id,doi,referenced_works"})
            for w in res:
                cache["refs"][(w.get("doi") or "").replace("https://doi.org/", "").lower()] = \
                    [x.rsplit("/", 1)[-1] for x in w.get("referenced_works") or []]
            for d in chunk:
                cache["refs"].setdefault(d, [])  # not in OpenAlex
            CACHE.write_text(json.dumps(cache))
            print(f"lists {i + len(chunk)}/{len(dois)}", file=sys.stderr, flush=True)
        wids = sorted({w for d in todo for w in cache["refs"].get(d, [])} - set(cache["works"]))
        for i in range(0, len(wids), BATCH):
            chunk = wids[i:i + BATCH]
            res = fetch({"filter": "openalex_id:" + "|".join(chunk), "per-page": BATCH,
                         "select": "id,doi,title,publication_year,authorships"})
            for w in res:
                a = (w.get("authorships") or [{}])[0].get("author", {}).get("display_name") or ""
                cache["works"][w["id"].rsplit("/", 1)[-1]] = {
                    "title": w.get("title") or "", "year": w.get("publication_year"),
                    "first": a.split()[-1].lower() if a.split() else "",
                    "doi": (w.get("doi") or "").replace("https://doi.org/", "").lower()}
            for w in chunk:
                cache["works"].setdefault(w, None)
            CACHE.write_text(json.dumps(cache))
            if i % 1000 == 0:
                print(f"works {i + len(chunk)}/{len(wids)}", file=sys.stderr, flush=True)
    except Budget as b:
        print(f"stopped: OpenAlex allowance low ({b}); run again tomorrow", file=sys.stderr)
    out = {}
    for d, rid in todo.items():
        refs = [cache["works"].get(w) for w in cache["refs"].get(d, [])]
        refs = [r for r in refs if r and r["title"]]
        if refs:
            out[rid] = refs
    OUT.write_text(json.dumps(out, ensure_ascii=False))
    print(f"{len(todo)} entries without text, {sum(1 for d in todo if d in cache['refs'])} looked up, "
          f"{len(out)} with references, {sum(len(v) for v in out.values())} references", file=sys.stderr)


if __name__ == "__main__":
    main()
