"""Fill missing abstracts from three more sources, and record where each came from.

- OpenAlex, by DOI in batches of 50, for off-NIME entries and the rule-selected datasets;
- the first page of local ICMC PDFs, for the curated off-NIME ICMC papers found there;
- the downloaded paper texts, for NIME papers whose bib entry has no abstract.

Writes data/abstracts_extra.json ({key: {"abstract", "source"}}, keyed by corpus id or by DOI) and
output/nime_missing_abstracts.tsv (abstracts for the NIME-bibliography repository, for review).
"""
import json
import re
import sys
import time
from pathlib import Path

import bibtexparser
import requests

from parse_refs import letters, readable

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "data" / "abstracts_extra.json"


def inverted(ix):
    if not ix:
        return ""
    pos = sorted((p, w) for w, ps in ix.items() for p in ps)
    return " ".join(w for _, w in pos)


def from_text(text):
    """The abstract of a paper from its extracted text: after an Abstract heading, up to the
    keywords or the first numbered section."""
    head = text[:12000]
    m = re.search(r"(?im)^\s*(abstract|a b s t r a c t)\b[.:\s—-]*", head)
    if not m:
        return ""
    rest = head[m.end():]
    end = re.search(r"(?im)^\s*(keywords|key words|author keywords|index terms|categories and subject|"
                    r"1\.?\s+introduction|1\s+introduction|introduction\s*$|i\.\s+introduction)", rest)
    a = rest[:end.start()] if end else rest[:2000]
    a = re.sub(r"-\n(\w)", r"\1", a)
    a = re.sub(r"\s+", " ", a).strip()
    words = re.findall(r"[A-Za-z]{2,}", a)
    common = sum(w.lower() in {"the", "and", "of", "to", "in", "is", "for", "this", "with", "a"} for w in words)
    return a if 150 <= len(a) <= 3000 and words and common / len(words) > 0.04 else ""


def main():
    found = json.loads(OUT.read_text()) if OUT.exists() else {}
    corpus = json.loads((HERE / "data" / "corpus.json").read_text())
    ab = json.loads((HERE / "data" / "abstracts.json").read_text())

    # 1. DOIs lacking an abstract
    dois = {r["doi"]: r["id"] for r in corpus if r["archive"] == "off-nime" and r["doi"] and r["id"] not in ab}
    for name in ("Cited", "Background", "Related"):
        for e in bibtexparser.load(open(HERE.parent / "bibs" / name / f"{name.lower()}.bib")).entries:
            if e.get("doi") and len(e.get("abstract", "")) < 80:
                dois[e["doi"].lower()] = e["doi"].lower()
    todo = [d for d in dois if dois[d] not in found]
    for i in range(0, len(todo), 50):
        chunk = todo[i:i + 50]
        r = requests.get("https://api.openalex.org/works",
                         params={"filter": "doi:" + "|".join(chunk), "per-page": 50,
                                 "select": "doi,abstract_inverted_index"}, timeout=90)
        if r.status_code != 200:
            print("OpenAlex", r.status_code, file=sys.stderr)
            break
        for w in r.json()["results"]:
            d = (w.get("doi") or "").replace("https://doi.org/", "").lower()
            a = inverted(w.get("abstract_inverted_index"))
            if d in dois and len(a) > 80:
                found[dois[d]] = {"abstract": a, "source": "OpenAlex"}
        time.sleep(1)
    print(f"OpenAlex: {sum(v['source'] == 'OpenAlex' for v in found.values())}", file=sys.stderr)

    # 2. curated ICMC papers in the local archive
    from parse_refs import text_sources
    sources, _ = text_sources(corpus)
    for r in corpus:
        if r["archive"] == "off-nime" and r["id"] not in ab and r["id"] not in found and r["id"] in sources:
            a = from_text(sources[r["id"]].read_text(errors="replace"))
            if a:
                found[r["id"]] = {"abstract": a, "source": "local PDF"}
    # 3. NIME papers without an abstract in the bib
    rows = []
    for r in corpus:
        if r["archive"] == "nime" and r["dataset"] == "NIME papers" and not r["abstract"] and r["id"] in sources:
            a = from_text(sources[r["id"]].read_text(errors="replace"))
            if a:
                found[r["id"]] = {"abstract": a, "source": "paper text"}
                rows.append((r["id"], r["file"], r["title"], a))
    with open(HERE / "output" / "nime_missing_abstracts.tsv", "w") as f:
        f.write("id\tfile\ttitle\tabstract\n")
        for row in rows:
            f.write("\t".join(re.sub(r"\s+", " ", x) for x in row) + "\n")
    OUT.write_text(json.dumps(found, ensure_ascii=False, indent=0))
    from collections import Counter
    print(json.dumps(Counter(v["source"] for v in found.values())), file=sys.stderr)


if __name__ == "__main__":
    main()
