"""Fetch publication records from the Zenodo communities of open music-technology conferences.

Writes data/zenodo.json in the same shape as data/journals.json, so that score_journals.py
scores both together. Only publications are kept (papers, articles, book chapters, theses),
not software, data or media. Responses are cached in data/zenodo/.
"""
import hashlib
import json
import re
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent.parent
CACHE = HERE / "data" / "zenodo"
CACHE.mkdir(parents=True, exist_ok=True)
API = "https://zenodo.org/api/records"
COMMUNITIES = {
    "iclc": "International Conference on Live Coding",
    "iclc2015": "International Conference on Live Coding",
    "livecode": "International Conference on Live Coding",
    "wac": "Web Audio Conference",
    "smc": "Sound and Music Computing",
    "nordicsmc": "Nordic Sound and Music Computing",
    "cmmr2023": "Computer Music Multidisciplinary Research",
    "cmmr2025": "Computer Music Multidisciplinary Research",
    "tenor": "TENOR (music notation)",
}
KEEP = {"publication"}
TYPES = {"conferencepaper": "proceedings-article", "article": "journal-article", "section": "book-chapter",
         "book": "book", "thesis": "dissertation", "report": "report", "preprint": "posted-content",
         "workingpaper": "report", "other": "other"}


def get(params):
    key = hashlib.sha1(json.dumps(params, sort_keys=True).encode()).hexdigest()
    f = CACHE / f"{key}.json"
    if f.exists():
        return json.loads(f.read_text())
    wait = 5
    for _ in range(8):
        try:
            r = requests.get(API, params=params, timeout=90, headers={"Accept": "application/json"})
            if r.status_code == 200:
                f.write_text(r.text)
                time.sleep(1.5)
                return r.json()
            print(f"  {r.status_code}, waiting {wait} s", file=sys.stderr)
        except requests.RequestException as ex:
            print(f"  {ex}", file=sys.stderr)
        time.sleep(wait)
        wait = min(wait * 2, 120)
    raise RuntimeError(params)


def main():
    out, seen = [], set()
    for slug, name in COMMUNITIES.items():
        page, n = 1, 0
        while True:
            d = get({"communities": slug, "size": 25, "page": page, "sort": "oldest"})
            hits = d.get("hits", {}).get("hits", [])
            for h in hits:
                m = h.get("metadata", {})
                rt = m.get("resource_type", {})
                if rt.get("type") not in KEEP:
                    continue
                doi = (h.get("doi") or m.get("doi") or "").lower()
                if not doi or doi in seen:
                    continue
                seen.add(doi)
                y = re.match(r"(\d{4})", m.get("publication_date", ""))
                out.append({"source": name, "doi": doi, "title": re.sub(r"\s+", " ", m.get("title", "")).strip(),
                            "year": int(y.group(1)) if y else None,
                            "authors": [re.sub(r"^(.*?), (.*)$", r"\2 \1", c.get("name", "")) for c in m.get("creators", [])],
                            "container": (m.get("meeting") or {}).get("title") or name,
                            "type": TYPES.get(rt.get("subtype"), "proceedings-article"),
                            "abstract": re.sub(r"<[^>]+>", " ", m.get("description") or "").strip(),
                            "volume": None, "issue": None, "pages": None})
                n += 1
            if len(hits) < 25 or page * 25 >= d.get("hits", {}).get("total", 0):
                break
            page += 1
        print(f"{slug}: {n}", file=sys.stderr, flush=True)
    (HERE / "data" / "zenodo.json").write_text(json.dumps(out, ensure_ascii=False))
    print(f"{len(out)} records", file=sys.stderr)


if __name__ == "__main__":
    main()
