"""List every NIME DOI with where OpenAlex currently files it, for a venue-mapping request.

Reads the NIME records of data/corpus.json (papers, music, installations, alt) and looks their
DOIs up in OpenAlex one by one. Writes data/nime_dois.csv with the DOI, the bibliography key,
the dataset, the year, the OpenAlex work id and the display name of the work's primary source
(empty when OpenAlex has no such work or files it under no source). Prints the counts by source.
"""
import collections
import csv
import json
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "data" / "nime_dois.csv"
API = "https://api.openalex.org/works"


def lookup(dois):
    """One request per DOI: the batched doi filter misses works that the single lookup finds."""
    found = {}
    for doi in dois:
        r = requests.get(f"{API}/doi:{doi}", params={"select": "id,primary_location"}, timeout=60)
        if r.status_code == 200:
            w = r.json()
            src = ((w.get("primary_location") or {}).get("source") or {}).get("display_name", "")
            found[doi] = (w["id"].rsplit("/", 1)[-1], src)
        elif r.status_code != 404:
            r.raise_for_status()
        time.sleep(0.1)
    return found


def main():
    corpus = json.loads((HERE / "data" / "corpus.json").read_text())
    rows = [r for r in corpus if r["dataset"].startswith("NIME") and r.get("doi")]
    found = lookup(sorted({r["doi"].lower() for r in rows}))
    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["doi", "key", "dataset", "year", "openalex_id", "openalex_source"])
        for r in rows:
            wid, src = found.get(r["doi"].lower(), ("", ""))
            w.writerow([r["doi"], r["id"], r["dataset"], r["year"], wid, src])
    sources = collections.Counter(found.get(r["doi"].lower(), ("", "not in OpenAlex"))[1] or "no source"
                                  for r in rows)
    print(f"{len(rows)} DOIs, {sum(r['doi'].lower() in found for r in rows)} in OpenAlex")
    for s, n in sources.most_common(8):
        print(f"  {n:5d}  {s}")


if __name__ == "__main__":
    main()
