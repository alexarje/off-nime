"""Fetch ISMIR, DAFx and CMMR proceedings for the sweep. (SMC comes from Zenodo, in zenodo.py.)

- ISMIR: the per-year proceedings files of the ismir/conference-archive repository on GitHub.
- DAFx: the "browse all papers" pages of the DAFx paper archive at dafx.de, which carry abstracts.
- CMMR: Springer LNCS chapters in Crossref, found by the title of each year's volume; the 2023 and
  2025 proceedings come from Zenodo.

Writes data/proceedings_extra.json in the shape of data/journals.json; score_journals.py scores it.
Responses are cached in data/proceedings_cache/.
"""
import hashlib
import html
import json
import re
import sys
import time
from difflib import SequenceMatcher
from pathlib import Path

import requests

from crossref import API as CR, get as cr_get, item_year

HERE = Path(__file__).resolve().parent.parent
CACHE = HERE / "data" / "proceedings_cache"
CACHE.mkdir(parents=True, exist_ok=True)
CMMR_VOLUMES = [
    "Computer Music Modeling and Retrieval", "Sense of Sounds", "Genesis of Meaning in Sound and Music",
    "Auditory Display", "Exploring Music Contents", "Speech, Sound and Music Processing: Embracing Research in India",
    "From Sounds to Music and Emotions", "Sound, Music, and Motion", "Music, Mind, and Embodiment",
    "Bridging People and Sound", "Perception, Representations, Image, Sound, Music", "Music in the AI Era",
]


def cached(url, params=None, pause=1.0):
    key = hashlib.sha1((url + json.dumps(params or {}, sort_keys=True)).encode()).hexdigest()
    f = CACHE / key
    if f.exists():
        return f.read_text()
    wait = 5
    for _ in range(6):
        try:
            r = requests.get(url, params=params, timeout=90, headers={"User-Agent": "off-nime-analysis/0.1"})
            if r.status_code == 200:
                f.write_text(r.text)
                time.sleep(pause)
                return r.text
            if r.status_code == 404:
                return None
            print(f"  {r.status_code}, waiting {wait} s", file=sys.stderr)
        except requests.RequestException as ex:
            print(f"  {ex}", file=sys.stderr)
        time.sleep(wait)
        wait *= 2
    return None


def rec(source, title, year, authors, abstract="", doi="", url="", container=None):
    return {"source": source, "doi": (doi or "").lower(), "url": url, "title": re.sub(r"\s+", " ", title or "").strip(),
            "year": int(year) if str(year).isdigit() else None, "authors": authors,
            "abstract": "" if abstract in (None, "None") else re.sub(r"\s+", " ", abstract).strip(),
            "container": container or source, "type": "proceedings-article", "volume": None, "issue": None,
            "pages": None}


def ismir():
    out = []
    listing = json.loads(cached("https://api.github.com/repos/ismir/conference-archive/contents/database/proceedings"))
    for f in listing:
        if not f["name"].endswith(".json"):
            continue
        for p in json.loads(cached(f["download_url"])):
            au = p.get("author")
            if isinstance(au, str):
                au = re.findall(r"'([^']+)'", au) or [au]
            out.append(rec("ISMIR", p.get("title"), p.get("year"), au or [], p.get("abstract"), p.get("doi"),
                           p.get("url") or p.get("ee")))
    print(f"ISMIR: {len(out)}", file=sys.stderr)
    return out


def dafx():
    out, page = [], 1
    while True:
        h = cached("https://www.dafx.de/paper-archive/search", {"q": "", "w": "anywhere", "p": page}, pause=2.0)
        if not h:
            break
        hits = h.split('class="panel panel-default hit-entry"')[1:]
        for x in hits:
            t = re.search(r'class="title"[^>]*>([^<]+)</a>', x)
            authors = [html.unescape(a) for a in re.findall(r'class="author"[^>]*>([^<]+)</a>', x)]
            y = re.search(r'class="year"[^>]*>DAFx-(\d{4})', x)
            ab = re.search(r'class="details collapse"[^>]*>\s*<div>(.*?)</div>', x, re.S)
            pdf = re.search(r'href="([^"]+\.pdf)" class="download-link"', x)
            if t:
                out.append(rec("DAFx", html.unescape(t.group(1)), y.group(1) if y else None, authors,
                               html.unescape(re.sub(r"<[^>]+>", " ", ab.group(1))) if ab else "",
                               url=f"https://www.dafx.de/paper-archive/{pdf.group(1)}" if pdf else ""))
        m = re.search(r"page (\d+) of (\d+)", h)
        if not hits or not m or int(m.group(1)) >= int(m.group(2)):
            break
        page += 1
    print(f"DAFx: {len(out)}", file=sys.stderr)
    return out


def cmmr():
    out, seen = [], set()
    for vol in CMMR_VOLUMES:
        d = cr_get(f"{CR}/works", {"query.container-title": vol, "filter": "type:book-chapter", "rows": 1000,
                                    "select": "DOI,title,author,issued,published-print,published-online,container-title,abstract"})
        for it in (d or {}).get("message", {}).get("items", []):
            cont = " ".join(it.get("container-title") or [])
            if SequenceMatcher(None, vol.lower(), cont.lower()[:len(vol) + 20]).ratio() < 0.8 and vol.lower() not in cont.lower():
                continue
            if it["DOI"] in seen or not it.get("title"):
                continue
            seen.add(it["DOI"])
            out.append(rec("CMMR", it["title"][0], item_year(it),
                           [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in it.get("author", [])],
                           re.sub(r"<[^>]+>", " ", it.get("abstract") or ""), it["DOI"], container=cont))
    print(f"CMMR: {len(out)}", file=sys.stderr)
    return out


def main():
    recs = ismir() + dafx() + cmmr()
    (HERE / "data" / "proceedings_extra.json").write_text(json.dumps(recs, ensure_ascii=False))
    print(f"{len(recs)} records", file=sys.stderr)


if __name__ == "__main__":
    main()
