"""Parse the off-NIME and NIME BibTeX archives into one table, data/corpus.json.

Each record carries an archive (off-nime or nime), a dataset (CMJ, ICMC, ISIDM, Extras,
NIME papers, NIME music, NIME installations), a normalised publication channel, the year,
the authors as normalised keys and display names, and the text used for topic modelling.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

HERE = Path(__file__).resolve().parent.parent
OFF = HERE.parent / "bibs"
NIME = Path.home() / "github" / "NIME-bibliography"


def load(path):
    parser = BibTexParser(common_strings=True)
    parser.customization = convert_to_unicode
    parser.ignore_nonstandard_types = False
    with open(path, encoding="utf-8") as f:
        return bibtexparser.load(f, parser=parser).entries


def clean(s):
    s = re.sub(r"[{}\\]", "", s or "")
    return re.sub(r"\s+", " ", s).strip()


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def split_authors(field):
    """Return (key, display) pairs. The key is surname plus first initial, without accents."""
    out = []
    for raw in re.split(r"\s+and\s+", clean(field)):
        raw = raw.strip().strip(",")
        if not raw or raw.lower() in {"others", "et al.", "et al"}:
            continue
        if "," in raw:
            last, first = [p.strip() for p in raw.split(",", 1)]
        else:
            parts = raw.split()
            # keep particles (van, de, von, da, dos) with the surname
            i = len(parts) - 1
            while i > 0 and parts[i - 1].lower() in {"van", "de", "von", "da", "dos", "der", "del", "di", "le", "la"}:
                i -= 1
            first, last = " ".join(parts[:i]), " ".join(parts[i:])
        initial = strip_accents(first)[:1].lower()
        surname = re.sub(r"[^a-z\- ]", "", strip_accents(last).lower()).strip()
        if not surname:
            continue
        out.append((f"{surname}_{initial}", f"{first} {last}".strip()))
    return out


CHANNELS = [
    (r"computer music journal", "Computer Music Journal"),
    (r"international computer music conference|\bicmc\b", "ICMC"),
    (r"new interfaces for musical expression|\bnime\b", "NIME"),
    (r"organi[sz]ed sound", "Organised Sound"),
    (r"journal of new music research|interface\b.*journal|^interface$", "Journal of New Music Research"),
    (r"leonardo", "Leonardo"),
    (r"human factors in computing|\bchi\b|computer[- ]human interaction|tochi", "CHI / HCI"),
    (r"sound and music computing|\bsmc\b", "Sound and Music Computing"),
    (r"digital audio effects|\bdafx\b", "DAFx"),
    (r"audio engineering society|\baes\b", "AES"),
    (r"acoustical society|\bjasa\b", "Acoustical Society"),
    (r"gesture", "Gesture workshops"),
    (r"ircam|trends in gestural control", "IRCAM publications"),
    (r"contemporary music review", "Contemporary Music Review"),
    (r"siggraph|graphics", "SIGGRAPH / graphics"),
    (r"ieee|acm|proceedings of the", "Other conference proceedings"),
]


def channel(e, dataset):
    if dataset.startswith("NIME"):
        return "NIME"
    t = e.get("ENTRYTYPE", "").lower()
    venue = clean(e.get("journal") or e.get("booktitle") or e.get("series") or "")
    if t in {"phdthesis", "mastersthesis"}:
        return "Theses"
    if t == "techreport":
        return "Technical reports"
    if t in {"book", "proceedings"}:
        return "Books"
    for pat, name in CHANNELS:
        if re.search(pat, venue.lower()):
            return name
    if t == "incollection":
        return "Book chapters"
    if t == "article":
        return "Other journals"
    return "Other conference proceedings" if venue else "Other"


def year(e):
    m = re.search(r"(1[89]\d\d|20\d\d)", e.get("year", ""))
    return int(m.group(1)) if m else None


def records():
    files = []
    for p in sorted(OFF.rglob("*.bib")):
        dataset = p.relative_to(OFF).parts[0]
        # Cited is derived from this analysis; the curated archives stay the reference it is measured against
        if dataset == "Cited":
            continue
        files.append(("off-nime", dataset, p))
    for sub, ds in [("paper_proceedings", "NIME papers"), ("music_proceedings", "NIME music"),
                    ("installation_proceedings", "NIME installations"), ("alt_proceedings", "NIME alt")]:
        for p in sorted((NIME / sub).glob("*.bib")):
            files.append(("nime", ds, p))
    for archive, dataset, path in files:
        for e in load(path):
            authors = split_authors(e.get("author") or e.get("editor") or "")
            yield {
                "id": f"{archive}:{e['ID']}",
                "archive": archive,
                "dataset": dataset,
                "file": str(path.relative_to(OFF.parent if archive == "off-nime" else NIME)),
                "type": e.get("ENTRYTYPE", "").lower(),
                "year": year(e),
                "title": clean(e.get("title")),
                "venue": clean(e.get("journal") or e.get("booktitle") or e.get("publisher") or e.get("school") or ""),
                "channel": channel(e, dataset),
                "authors": [a for a, _ in authors],
                "names": [n for _, n in authors],
                "doi": clean(e.get("doi")).lower() or None,
                "url": clean(e.get("url")) or None,
                "abstract": clean(e.get("abstract")),
                "keywords": clean(e.get("keywords")),
            }


def main():
    recs = list(records())
    # abstracts fetched for off-NIME entries (tools/fetch_abstracts.py) live in the analysis data
    ab = HERE / "data" / "abstracts.json"
    if ab.exists():
        found = json.loads(ab.read_text())
        for r in recs:
            if not r["abstract"] and r["id"] in found:
                r["abstract"] = found[r["id"]]["abstract"]
    # The ISIDM list was deduplicated against CMJ and ICMC, but not against NIME; flag title clashes.
    seen = {}
    for r in recs:
        k = re.sub(r"[^a-z0-9]", "", r["title"].lower())[:60]
        r["dup_of"] = seen.get(k)
        seen.setdefault(k, r["id"])
    out = HERE / "data" / "corpus.json"
    out.write_text(json.dumps(recs, ensure_ascii=False, indent=0))
    print(f"{len(recs)} records written to {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
