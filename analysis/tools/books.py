"""Search Crossref for books, edited volumes and monographs on NIME topics.

Books rarely carry abstracts, so they are judged by the title classifier (tools/topic.py) on
title and subtitle, after a filter that keeps only titles naming music or sound, at a strict probability (MIN_P), since a book found this way has no other
evidence behind it. Books already in the archives or in the rule-selected datasets are left out.
Writes data/books.json (every book found, with its probability) and output/candidates_books.tsv;
admitted books join bibs/Related/related.bib through score_journals.py.
"""
import json
import re
import sys
from pathlib import Path

from crossref import API, get, item_year
from parse_refs import title_key

HERE = Path(__file__).resolve().parent.parent
MIN_P = 0.8
# "about music" is not enough for a book: musicology and instrument history share the words, so a
# title must also name technology
TECH = re.compile(r"electronic|digital|computer|comput|interactive|interaction|interface|technolog|gesture|sensor|"
                  r"synthes|live coding|instrument design|machine|algorithm|network|virtual|haptic|robot|software|"
                  r"programming|\bai\b|artificial|data|cyber|media|electric|controller|wearable|mobile|web", re.I)
MUSIC = re.compile(r"\bmusic|musical|\bsonic|\bsound|\baudio|synthes|electroacoustic|composer|musician|organolog|"
                   r"live coding|laptop orchestra|\bdj\b|turntabl|\bnime\b|instrument design", re.I)
QUERIES = [
    "musical instruments digital", "digital musical instruments", "new interfaces for musical expression",
    "music interaction", "musical gesture", "sonic interaction design", "live coding", "electronic music performance",
    "computer music", "interactive music", "music technology", "sound and music computing", "embodied music",
    "musical haptics", "music and human-computer interaction", "laptop orchestra", "networked music",
    "electronic musical instruments", "synthesizer", "musical robotics", "instrument design", "sound art",
    "interactive sound installation", "musical expression technology", "mapping gesture sound", "audio programming",
    "algorithmic composition", "music and machine learning", "sensors music", "virtual reality music",
    "organology", "electroacoustic music", "experimental music technology", "hacking music hardware",
]
# reference-book records are mostly encyclopedia entries (Grove Music Online, national biographies)
TYPES = "type:book,type:edited-book,type:monograph"


def main():
    have = set()
    for r in json.loads((HERE / "data" / "corpus.json").read_text()):
        have.add(title_key(r["title"]))
    for name in ("Cited", "Background", "Theses", "Related"):
        f = HERE.parent / "bibs" / name / f"{name.lower()}.bib"
        if f.exists():
            for m in re.finditer(r"title = \{([^}]*)\}", f.read_text()):
                have.add(title_key(m.group(1)))
    books = {}
    for q in QUERIES:
        d = get(f"{API}/works", {"query.bibliographic": q, "filter": TYPES, "rows": 200,
                                 "select": "DOI,title,subtitle,author,editor,issued,published-print,published-online,type,publisher,ISBN"})
        for it in (d or {}).get("message", {}).get("items", []):
            if not it.get("title"):
                continue
            t = it["title"][0]
            sub = (it.get("subtitle") or [""])[0]
            full = re.sub(r"\s+", " ", f"{t}: {sub}" if sub and sub.lower() not in t.lower() else t).strip()
            books.setdefault(it["DOI"].lower(), {
                "doi": it["DOI"].lower(), "title": full, "year": item_year(it), "type": it.get("type"),
                "publisher": it.get("publisher", ""),
                "authors": [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in it.get("author", [])],
                "editors": [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in it.get("editor", [])],
                "query": q})
        print(f"{q}: {len(books)}", file=sys.stderr, flush=True)
    from topic import nime_probability
    # the classifier only knows music-technology and HCI titles; outside that domain words such as
    # "instrument" and "installation" mislead it, so a book must name music or sound first
    items = [b for b in books.values() if title_key(b["title"]) not in have and b["year"] and MUSIC.search(b["title"])
             and TECH.search(b["title"])]
    items = [b for b in items if b["type"] != "reference-book" and not re.match(r"(RP|ST|EG)\s?\d", b["title"])]
    for b, p in zip(items, nime_probability([b["title"] for b in items])):
        b["p_nime"] = round(float(p), 3)
        b["admit"] = bool(p >= MIN_P)
    # one copy of a title published in several editions: the latest
    latest = {}
    for b in items:
        k = title_key(b["title"])
        if k not in latest or (b["year"] or 0) > (latest[k]["year"] or 0):
            latest[k] = b
    for b in items:
        if latest[title_key(b["title"])] is not b:
            b["admit"] = False
    (HERE / "data" / "books.json").write_text(json.dumps(items, ensure_ascii=False))
    with open(HERE / "output" / "candidates_books.tsv", "w") as f:
        f.write("admitted\tp_nime\tyear\ttitle\tauthors_or_editors\tpublisher\tdoi\n")
        for b in sorted(items, key=lambda b: -b["p_nime"]):
            f.write("\t".join(re.sub(r"\s+", " ", str(x)) for x in
                              [b["admit"], b["p_nime"], b["year"], b["title"], "; ".join((b["authors"] or b["editors"])[:3]),
                               b["publisher"], b["doi"]]) + "\n")
    print(f"{len(items)} books, {sum(b['admit'] for b in items)} admitted", file=sys.stderr)


if __name__ == "__main__":
    main()
