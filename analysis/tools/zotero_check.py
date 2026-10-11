"""Cross-check the collection against Alexander's Zotero library.

Reads a copy of ~/Zotero/zotero.sqlite (never the live file, which Zotero locks and owns), takes
every bibliographic item that is not in the trash, and matches it against the whole collection
(the two archives and every dataset in bibs/) by DOI and by title key. Unmatched items are ranked
as candidates: first those in a Zotero collection whose name mentions NIME, then by the title
classifier's NIME-topic probability (tools/topic.py). The library also holds works on other
fields (political science, medieval architecture), which the classifier keeps out.

Writes data/zotero_candidates.tsv and data/zotero_stats.json, which stay in data/ since they
describe a private library. The top tier (probability at least TIER_P, a scholarly item type and a
year) becomes bibs/Zotero/zotero.bib, after a second, looser check against the collection: the same
year within one and a title that agrees on its first 60 letters by a ratio of at least 0.8 (Birnbaum's
"Towards a Dimension Space for Musical Artifacts" is the NIME paper on "Musical Devices"). Items that
name the NIME proceedings as their venue are left out, since the NIME archive holds them.
"""
import json
import re
import shutil
import sqlite3
import sys
import tempfile
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path

import bibtexparser

from parse_refs import letters, title_key

HERE = Path(__file__).resolve().parent.parent
LIBRARY = Path.home() / "Zotero" / "zotero.sqlite"
SKIP_TYPES = ("attachment", "note", "annotation")
MIN_P = 0.5
TIER_P = 0.9
# A NIME tag or folder is the maintainer's own judgement, so such items join the dataset at any
# probability; "accompaniment" contains the letters, hence the word boundaries.
NIME_MARK = re.compile(r"\bnimes?\b|\bnime ?\d{2,4}\b|interfaces? for musical expression", re.I)
# tags that record reading or filing, not the topic
WORKFLOW = re.compile(r"^(#.*|unread|read|to read|qomop|am|obs|\d+)$", re.I)
# function words of the other languages in the library; the classifier is trained on English titles
# and scores some Norwegian and German ones high
FOREIGN = set("og av på til et som med det ikke eller und der die das ein eine zur zum für von mit über le la les des du "
              "pour une sur dans il della delle per nel el los las del para con em uma dos".split())
ENGLISH = set("the of and in on for to with a an from by as at is its towards toward using".split())
OUT = HERE.parent / "bibs" / "Zotero" / "zotero.bib"
KINDS = {"journalArticle": "article", "conferencePaper": "inproceedings", "bookSection": "incollection",
         "book": "book", "thesis": "phdthesis", "report": "techreport", "patent": "misc"}
FIELDS = ("title", "date", "DOI", "publicationTitle", "proceedingsTitle", "bookTitle", "publisher", "volume",
          "issue", "pages", "url", "abstractNote", "university", "institution", "place", "thesisType", "ISBN")


def library():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "zotero.sqlite"
        shutil.copy(LIBRARY, db)
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        q = lambda sql: con.execute(sql).fetchall()
        types = dict(q("select itemTypeID, typeName from itemTypes"))
        items = {i: {"key": k, "type": types[t]} for i, t, k in q(
            "select itemID, itemTypeID, key from items where itemID not in (select itemID from deletedItems)")
            if types[t] not in SKIP_TYPES}
        for i, field, value in q("select d.itemID, f.fieldName, v.value from itemData d join fields f using(fieldID) "
                                 "join itemDataValues v using(valueID) where f.fieldName in " + repr(FIELDS)):
            if i in items:
                items[i][field] = value
        for i, first, last, role in q("select ic.itemID, c.firstName, c.lastName, ct.creatorType from itemCreators ic "
                                      "join creators c using(creatorID) join creatorTypes ct using(creatorTypeID) "
                                      "order by ic.orderIndex"):
            if i in items:
                key = "editors" if role in ("editor", "seriesEditor", "bookAuthor") else "authors"
                if key == "authors" or role == "editor":
                    items[i].setdefault(key, []).append(last)
                    items[i].setdefault(key + "_full", []).append(f"{last}, {first}" if first else last)
        for i, tag in q("select it.itemID, t.name from itemTags it join tags t using(tagID)"):
            if i in items:
                items[i].setdefault("tags", []).append(tag.strip())
        cols = dict(q("select collectionID, collectionName from collections"))
        for c, i in q("select collectionID, itemID from collectionItems"):
            if i in items:
                items[i].setdefault("collections", []).append(cols[c])
        con.close()
    return [x for x in items.values() if x.get("title")]


def clean(t):
    """Zotero titles carry LaTeX and HTML from imports ("Gesture $\\approx$ Sound", "<sub>:</sub>")."""
    t = re.sub(r"\$[^$]*\$|\\[A-Za-z]+|<[^>]+>|[{}]", " ", t or "")
    return re.sub(r"\s+", " ", t).strip()


def prefix(t):
    """The first 40 letters, ignoring spaces, so that "emotio nal" matches "emotional"."""
    return letters(clean(t))[:40]


def collection(skip=()):
    """DOIs, title keys and (year, first 60 letters) of every entry outside the Zotero dataset and
    the bib files in skip."""
    dois, keys, dated = set(), set(), []
    entries = [(r["title"], r.get("doi"), r["year"]) for r in json.loads((HERE / "data" / "corpus.json").read_text())]
    for f in (HERE.parent / "bibs").glob("**/*.bib"):
        if f != OUT and f not in skip:
            entries += [(e.get("title", ""), e.get("doi"), e.get("year", "")) for e in bibtexparser.load(open(f)).entries]
    for t, doi, y in entries:
        keys |= {title_key(t), prefix(t)}
        if doi and doi != "None":
            dois.add(doi.lower())
        m = re.search(r"\d{4}", str(y))
        if m:
            dated.append((int(m.group(0)), letters(clean(t))[:60]))
    keys.discard("")
    keys.discard(None)
    return dois, keys, dated


def held(it, dois, keys, dated_set):
    doi = (it.get("DOI") or "").lower().strip()
    exact = {(y + d, letters(it["title"])[:60]) for d in (-1, 0, 1) for y in [int(it["year"] or 0)]}
    return bool(doi and doi in dois) or title_key(it["title"]) in keys or \
        (len(prefix(it["title"])) >= 25 and prefix(it["title"]) in keys) or \
        (len(letters(it["title"])) >= 5 and bool(exact & dated_set))


def near_match(it, dated):
    t = letters(it["title"])[:60]
    y = int(it["year"])
    return any(abs(yy - y) <= 1 and SequenceMatcher(None, t, tt).ratio() >= 0.8 for yy, tt in dated)


def main():
    items = library()
    dois, keys, dated = collection()
    dated_set = set(dated)
    for it in items:
        # Zotero stores "2023-05-00 May 2023", or "0000-00-00 Online first" when the year is unknown
        it["year"] = next((y for y in re.findall(r"\b\d{4}\b", it.get("date", "")) if "1500" < y < "2100"), "")
        it["title"] = clean(it["title"])
        # short titles ("AlphaSphere") have no title key; they match on the whole title and the year
        it["in_collection"] = held(it, dois, keys, dated_set)
        it["nime_folder"] = any(NIME_MARK.search(c) for c in it.get("collections", []))
        it["nime_tag"] = any(NIME_MARK.search(t) for t in it.get("tags", []))
    # one row per work: the library holds some works two or three times
    seen, out = set(), []
    for it in sorted((it for it in items if not it["in_collection"]), key=lambda it: not it.get("DOI")):
        k = prefix(it["title"])
        if k not in seen:
            seen.add(k)
            out.append(it)
    from topic import nime_probability
    for it, p in zip(out, nime_probability([it["title"] for it in out])):
        it["p"] = round(float(p), 3)
    marked = lambda it: it["nime_folder"] or it["nime_tag"]
    cands = sorted((it for it in out if marked(it) or it["p"] >= MIN_P), key=lambda it: (not marked(it), -it["p"]))
    with open(HERE / "data" / "zotero_candidates.tsv", "w") as f:
        f.write("nime_folder\tnime_tag\tp_nime\tyear\ttype\tfirst_author\ttitle\tvenue\tdoi\tzotero_collections\tzotero_key\n")
        for it in cands:
            f.write("\t".join(re.sub(r"\s+", " ", str(x)) for x in [
                it["nime_folder"], it["nime_tag"], it["p"], it["year"], it["type"], (it.get("authors") or [""])[0], it["title"],
                venue(it),
                it.get("DOI", ""), "; ".join(it.get("collections", [])), it["key"]]) + "\n")
    tier = [it for it in cands if (it["p"] >= TIER_P or marked(it)) and it["type"] in KINDS and it["year"]
            and not re.search(r"new interfaces for musical expression|\bnime\b", venue(it), re.I)]
    english = [it for it in tier if is_english(it["title"])]
    kept = [it for it in english if not near_match(it, dated)]
    write_bib(kept)
    # theses the collection lacks, for theses.py to score with its own rules; the Theses dataset is
    # left out of the comparison, since theses.py rebuilds it from this list among others
    tdois, tkeys, tdated = collection(skip=(HERE.parent / "bibs" / "Theses" / "theses.bib",))
    seen, theses = set(), []
    for it in sorted((it for it in items if it["type"] == "thesis" and it["year"]
                      and not held(it, tdois, tkeys, set(tdated))), key=lambda it: not it.get("DOI")):
        if prefix(it["title"]) not in seen:
            seen.add(prefix(it["title"]))
            theses.append(it)
    th = [{"id": it["key"], "doi": (it.get("DOI") or "").lower(), "url": it.get("url") or "", "title": it["title"],
           "year": int(it["year"]), "authors": it.get("authors_full", []), "school": it.get("university") or "",
           "abstract": clean(it.get("abstractNote", "")), "language": None}
          for it in theses]
    (HERE / "data" / "zotero_theses.json").write_text(json.dumps(th, ensure_ascii=False))
    stats = {"items": len(items), "in_collection": sum(it["in_collection"] for it in items),
             "candidates": len(cands), "candidates_in_nime_folders": sum(it["nime_folder"] for it in cands),
             "candidates_with_nime_tags": sum(it["nime_tag"] for it in cands),
             "candidate_types": dict(Counter(it["type"] for it in cands)), "min_p": MIN_P,
             "tier_p": TIER_P, "tier": len(tier), "tier_not_english": len(tier) - len(english),
             "tier_near_match": len(english) - len(kept),
             "tier_by_mark_only": sum(it["p"] < TIER_P for it in tier),
             "dataset_by_mark_only": sum(it["p"] < TIER_P for it in kept),
             "dataset_with_keywords": sum(bool(keywords(it)) for it in kept), "dataset": len(kept)}
    (HERE / "data" / "zotero_stats.json").write_text(json.dumps(stats, indent=1))
    print(json.dumps(stats, indent=1))


def keywords(it):
    """Topical tags, without the filing tags and the NIME marks, once each regardless of case."""
    seen, out = set(), []
    for t in it.get("tags", []):
        if t and not WORKFLOW.match(t) and not NIME_MARK.search(t) and len(t) <= 60 and t.lower() not in seen:
            seen.add(t.lower())
            out.append(t)
    return out[:15]


def is_english(t):
    words = re.findall(r"[a-zà-ÿ]+", t.lower())
    return sum(w in ENGLISH for w in words) >= sum(w in FOREIGN for w in words)


def venue(it):
    return it.get("publicationTitle") or it.get("proceedingsTitle") or it.get("bookTitle") or it.get("publisher") or ""


def write_bib(items):
    OUT.parent.mkdir(exist_ok=True)
    keys = set()
    with open(OUT, "w") as f:
        for it in sorted(items, key=lambda it: (it["year"], it["title"])):
            kind = KINDS[it["type"]]
            if kind == "phdthesis" and re.search(r"master|m\.?a\b|m\.?sc|msc", it.get("thesisType", ""), re.I):
                kind = "mastersthesis"
            first = letters((it.get("authors") or ["anon"])[0])[:20] or "anon"
            key = f"zotero:{first}{it['year']}{letters(it['title'])[:12]}"
            while key in keys:
                key += "b"
            keys.add(key)
            container = {"article": "journal", "inproceedings": "booktitle", "incollection": "booktitle"}.get(kind)
            fields = [("author", " and ".join(it.get("authors_full", []))),
                      ("editor", " and ".join(it.get("editors_full", [])) if kind in ("incollection", "book") else ""),
                      ("title", it["title"]),
                      (container, it.get("publicationTitle") or it.get("proceedingsTitle") or it.get("bookTitle"))
                      if container else ("", ""),
                      ("school", it.get("university")) if kind == "phdthesis" else
                      ("institution", it.get("institution") or it.get("publisher")) if kind == "techreport" else
                      ("publisher", it.get("publisher")) if kind in ("book", "incollection", "inproceedings") else ("", ""),
                      ("address", it.get("place") if kind != "article" else ""), ("year", it["year"]),
                      ("volume", it.get("volume")), ("number", it.get("issue")),
                      ("pages", re.sub(r"\s*[-–]+\s*", "--", it.get("pages", ""))), ("isbn", it.get("ISBN")),
                      ("doi", it.get("DOI")), ("url", it.get("url") if not it.get("DOI") else ""),
                      ("keywords", ", ".join(keywords(it))),
                      ("abstract", clean(it.get("abstractNote", ""))), ("collection", "Zotero"),
                      ("note", "Found in the maintainer's Zotero library"
                       + ("; tagged or filed as NIME there" if it["nime_folder"] or it["nime_tag"] else "")
                       + f"; NIME-topic probability {it['p']:.2f}")]
            f.write(f"@{kind}{{{key},\n" + ",\n".join(
                f"  {k} = {{{re.sub(r'[{}]', '', re.sub(r'\s+', ' ', str(v))).strip()}}}" for k, v in fields if k and v)
                + "\n}\n\n")


if __name__ == "__main__":
    sys.exit(main())
