"""Fetch Semantic Scholar records, with reference lists, for every corpus entry.

NIME entries are looked up by their Zenodo DOI in batches; off-NIME entries by DOI where
one exists, otherwise by title match. Results are cached in data/s2/ so a rerun only asks
for what is missing. No API key is used, so the script backs off on HTTP 429.
"""
import json
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent.parent
CACHE = HERE / "data" / "s2"
CACHE.mkdir(parents=True, exist_ok=True)
API = "https://api.semanticscholar.org/graph/v1"
REF = "paperId,title,year,venue,externalIds,authors,citationCount,publicationTypes"
FIELDS = "paperId,title,year,venue,externalIds,citationCount,authors,references." + ",references.".join(REF.split(","))


def call(method, url, **kw):
    wait = 5
    for _ in range(12):
        try:
            r = requests.request(method, url, timeout=60, **kw)
        except requests.RequestException as ex:
            print("network:", ex, file=sys.stderr)
            r = None
        if r is not None and r.status_code == 200:
            return r.json()
        if r is not None and r.status_code in (400, 404):
            return None
        code = r.status_code if r is not None else "-"
        print(f"  {code}, waiting {wait} s", file=sys.stderr)
        time.sleep(wait)
        wait = min(wait * 2, 120)
    raise RuntimeError(f"gave up on {url}")


def cache_path(rid):
    return CACHE / (rid.replace(":", "__").replace("/", "_") + ".json")


def main():
    corpus = json.loads((HERE / "data" / "corpus.json").read_text())
    todo = [r for r in corpus if not cache_path(r["id"]).exists()]
    by_doi = [r for r in todo if r["doi"]]
    by_title = [r for r in todo if not r["doi"] and r["title"]]
    print(f"{len(by_doi)} by DOI, {len(by_title)} by title", file=sys.stderr)

    for i in range(0, len(by_doi), 100):
        chunk = by_doi[i:i + 100]
        res = call("POST", f"{API}/paper/batch", params={"fields": FIELDS},
                   json={"ids": [f"DOI:{r['doi']}" for r in chunk]})
        if res is None:
            # a malformed id rejects the whole batch; fall back to one request per entry
            res = []
            for r in chunk:
                res.append(call("GET", f"{API}/paper/DOI:{r['doi']}", params={"fields": FIELDS}))
                time.sleep(1.2)
        for r, p in zip(chunk, res):
            cache_path(r["id"]).write_text(json.dumps({"query": "doi", "paper": p}))
        print(f"DOI batch {i // 100 + 1}: {sum(p is not None for p in res)}/{len(chunk)} found", file=sys.stderr)
        time.sleep(3)

    if "--doi-only" in sys.argv:
        return
    for n, r in enumerate(by_title):
        hit = call("GET", f"{API}/paper/search/match", params={"query": r["title"][:300], "fields": "paperId,title,year"})
        p = None
        if hit and hit.get("data"):
            cand = hit["data"][0]
            # accept only when the year agrees within one, since title match is fuzzy
            if cand.get("year") is None or r["year"] is None or abs(cand["year"] - r["year"]) <= 1:
                p = call("GET", f"{API}/paper/{cand['paperId']}", params={"fields": FIELDS})
                if p:
                    p["matchScore"] = cand.get("matchScore")
        cache_path(r["id"]).write_text(json.dumps({"query": "title", "paper": p}))
        if n % 25 == 0:
            print(f"title {n}/{len(by_title)}", file=sys.stderr)
        time.sleep(1.2)


if __name__ == "__main__":
    main()
