"""The Zenodo version history of every NIME DOI in the bibliography, for NIME-bibliography#140.

For each Zenodo DOI in data/nime_dois.csv (tools/nime_dois.py), the public versions endpoint gives
the concept DOI and every version. A record with more than one version is where a version DOI and
the concept DOI part: the bibliography may hold an old version, and a switch to concept DOIs has to
know the concept DOI of each.

Writes data/zenodo_versions.json (every record, a cache that a stopped run resumes from) and
output/zenodo_versions.tsv (the records with more than one version, or whose bibliography DOI is
not the latest version). Read-only; no token.
"""
import csv
import json
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent.parent
CACHE = HERE / "data" / "zenodo_versions.json"
OUT = HERE / "output" / "zenodo_versions.tsv"
API = "https://zenodo.org/api/records/{}/versions"
HEAD = {"User-Agent": "off-nime-analysis/0.1 (https://github.com/alexarje/off-nime)"}


def versions(recid):
    for attempt in range(6):
        try:
            r = requests.get(API.format(recid), params={"size": 25, "allversions": "true"}, headers=HEAD, timeout=60)
        except requests.RequestException:
            time.sleep(30 * (attempt + 1))
            continue
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(30 * (attempt + 1))
            continue
        if r.status_code in (404, 410):
            return {"error": r.status_code}
        r.raise_for_status()
        # guests get at most 25 versions a page; "total" shows whether a record has more
        d = r.json()["hits"]
        hits = sorted(d["hits"], key=lambda h: h["created"])
        return {"concept": hits[0]["conceptdoi"] if hits else None, "total": d["total"],
                "versions": [h["doi"].lower() for h in hits]}
    return None


def main():
    rows = [r for r in csv.DictReader(open(HERE / "data" / "nime_dois.csv"))
            if r["doi"].startswith("10.5281/zenodo.")]
    cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
    todo = [r for r in rows if r["doi"] not in cache]
    print(f"{len(rows)} Zenodo DOIs, {len(todo)} to fetch", file=sys.stderr, flush=True)
    for n, r in enumerate(todo):
        v = versions(r["doi"].split(".")[-1])
        if v is not None:
            cache[r["doi"]] = v
        if n % 100 == 0:
            CACHE.write_text(json.dumps(cache))
            print(f"{n + 1}/{len(todo)}", file=sys.stderr, flush=True)
        time.sleep(0.6)
    CACHE.write_text(json.dumps(cache))

    out, multi, old, missing = [], 0, 0, 0
    for r in rows:
        v = cache.get(r["doi"])
        if not v or "error" in v or not v["versions"]:
            missing += 1
            out.append([r["key"], r["year"], r["doi"], "", 0, "", "not found"])
            continue
        n, latest = len(v["versions"]), v["versions"][-1]
        multi += n > 1
        old += r["doi"].lower() != latest
        if n > 1 or r["doi"].lower() != latest:
            note = "bibliography holds an older version" if r["doi"].lower() != latest else ""
            out.append([r["key"], r["year"], r["doi"], v["concept"], n, latest, note])
    with open(OUT, "w") as f:
        f.write("key\tyear\tdoi\tconcept_doi\tversions\tlatest_doi\tnote\n")
        for row in sorted(out):
            f.write("\t".join(map(str, row)) + "\n")
    print(f"{len(rows)} Zenodo DOIs: {multi} with more than one version, {old} not the latest, "
          f"{missing} not found", file=sys.stderr)


if __name__ == "__main__":
    main()
