"""Split the reference lists of the NIME paper texts into entries and match them.

Each reference is matched against the titles of the two archives (giving citation edges
inside the corpus); the rest are clustered by a title key, giving the external works the
NIME papers cite most often. Writes data/refs.json.
"""
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
TEXT = HERE / "data" / "text"

STOP = {"a", "an", "the", "of", "and", "for", "in", "on", "to", "with", "by", "from", "as", "at",
        "or", "its", "into", "towards", "toward", "via", "using", "some", "do", "is", "are"}
NOT_SENTENCE_END = {"al", "proc", "eds", "ed", "pp", "vol", "no", "vs", "dr", "st", "jr", "inc", "ch",
                    "intl", "int", "conf", "symp", "univ", "dept", "trans", "comput", "j", "mus", "e.g", "i.e"}


def ascii_fold(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def letters(s):
    return re.sub(r"[^a-z0-9]", "", ascii_fold(s).lower())


def title_key(t, n=32):
    """Significant words run together and cut at n letters, so that "Open SoundControl" and
    "Open Sound Control" share a key."""
    words = [w for w in re.findall(r"[a-z0-9]+", ascii_fold(t).lower()) if w not in STOP]
    return "".join(words)[:n] if len(words) >= 3 else None


def readable(text):
    """True when the text is mostly real words, false for PDFs with broken font encodings."""
    words = re.findall(r"[A-Za-z]{2,}", text[:20000])
    common = sum(w.lower() in {"the", "and", "of", "to", "in", "is", "for", "that", "with", "this"} for w in words)
    return len(words) > 200 and common / len(words) > 0.04


def reference_section(text):
    heads = list(re.finditer(r"^\s*(?:\d+\.?|[A-Z]\.)?\s*(REFERENCES|References|Bibliography|BIBLIOGRAPHY|"
                             r"Works Cited|R E F E R E N C E S)\s*$", text, re.M))
    if not heads:
        return None
    sec = text[heads[-1].end():]
    sec = re.split(r"^\s*(?:APPENDIX|Appendix|A\.\s+APPENDIX|ETHICAL STANDARDS|Ethical Standards)\b", sec, flags=re.M)[0]
    # page furniture: running heads, page numbers, conference footers
    sec = re.sub(r"^.*(Proceedings of the|NIME\s?'?\d\d|New Interfaces for Musical Expression).*$", "", sec, flags=re.M)
    sec = re.sub(r"^\s*\d{1,4}\s*$", "", sec, flags=re.M)
    return sec


def split_entries(sec):
    if len(re.findall(r"^\s*\[\d{1,3}\]", sec, re.M)) >= 3:
        parts = re.split(r"^\s*\[\d{1,3}\]\s*", sec, flags=re.M)[1:]
    elif len(re.findall(r"^\s*\d{1,3}\.\s+[A-Z]", sec, re.M)) >= 3:
        parts = re.split(r"^\s*\d{1,3}\.\s+(?=[A-Z])", sec, flags=re.M)[1:]
    else:
        # author–year lists: a new entry starts with "Surname, I." after a line that ended a sentence
        parts, cur = [], []
        for line in sec.splitlines():
            starts = re.match(r"^\s*[A-Z][\w'’\-]+(?: [a-z]{1,3} [A-Z][\w\-]+)?,\s+(?:[A-Z]\.|[A-Z][a-z]+)", line)
            if starts and cur and re.search(r"[.)]\s*$", cur[-1]):
                parts.append(" ".join(cur))
                cur = []
            if line.strip():
                cur.append(line.strip())
            elif cur and len(" ".join(cur)) > 40:
                parts.append(" ".join(cur))
                cur = []
        if cur:
            parts.append(" ".join(cur))
    out = []
    for p in parts:
        p = re.sub(r"-\s*\n\s*", "", p)
        p = re.sub(r"\s+", " ", p).strip()
        # an entry that runs on has usually swallowed the other column's body text; its start is
        # still the reference
        p = p[:400]
        if len(p) >= 25 and re.search(r"(19[4-9]\d|20[0-2]\d)", p):
            out.append(p)
    return out


def sentences(s):
    out, cur = [], ""
    for tok in re.split(r"(?<=[.?!])\s+", s):
        cur = f"{cur} {tok}".strip()
        last = re.findall(r"([\w.]+)[.?!]$", tok)
        word = last[0].lower() if last else ""
        # an initial ("T.") or abbreviation does not end a sentence
        if re.fullmatch(r"[a-z]", word) or word in NOT_SENTENCE_END or re.fullmatch(r"(?:[a-z]\.)+[a-z]", word):
            continue
        out.append(cur)
        cur = ""
    if cur:
        out.append(cur)
    return out


def parse(entry):
    year = re.search(r"\b(19[4-9]\d|20[0-2]\d)[a-z]?\b", entry)
    q = re.search(r"[“\"']{1,2}([^”\"]{12,250}?)[,.]?[”\"']{1,2}", entry)
    if q and len(q.group(1).split()) >= 2:
        title = q.group(1)
    else:
        sents = sentences(entry)
        title = None
        for s in sents[1:4]:
            core = re.sub(r"^\(?\s*(19|20)\d\d[a-z]?\s*\)?[.,]?\s*", "", s).strip(" .,")
            if len(core) >= 8 and len(core.split()) >= 2 and not re.match(r"^(In|Proc|http|URL|doi|Retrieved)", core):
                title = core
                break
    title = re.sub(r"\s*(In:?|In Proceedings.*|Proceedings.*)$", "", title or "").strip(" .,") or None
    return {"year": int(year.group(1)) if year else None, "title": title, "first": first_author(entry)}


def first_author(entry):
    """Surname of the first author, for "Surname, I.", "I. Surname" and "Given Surname" styles."""
    chunk = re.split(r",|\s(?:and|&)\s|(?<![A-Z])\.\s|\(", entry, maxsplit=1)[0].strip()
    words = [w for w in chunk.split() if not re.fullmatch(r"(?:[A-Z]\.-?)+", w)]
    if not words:
        return ""
    return ascii_fold(words[-1]).lower().strip(".")


LOCAL = HERE / "data" / "local_text"


def text_sources(corpus):
    """Map each corpus id to the best available text: the nime.org download, else the OCR copy
    from the local archive (for early PDFs with broken fonts), else a local ICMC file matched
    on year, first author and title."""
    icmc = defaultdict(list)
    for f in (LOCAL / "ICMC").rglob("*.txt"):
        m = re.match(r"ICMC(\d{4})_([^.]+?)\d?\.pdf\.txt$", f.name)
        if m:
            icmc[(int(m.group(1)), letters(m.group(2)))].append(f)
    src, how = {}, Counter()
    for r in corpus:
        cands = []
        f = TEXT / (r["id"].replace(":", "__").replace("/", "_") + ".txt")
        if f.exists():
            cands.append(("web", f))
        if r["url"] and r["archive"] == "nime":
            o = LOCAL / "NIME" / "nime-PDFs" / "OCR" / (r["url"].split("/")[-1] + ".txt")
            if o.exists():
                cands.append(("ocr", o))
        if r["archive"] == "off-nime" and r["names"]:
            sur = letters(r["names"][0].split()[-1])
            title = letters(r["title"])[:40]
            for g in icmc.get((r["year"], sur), []):
                if title[:25] in letters(g.read_text(errors="replace")[:3000]):
                    cands.append(("icmc-local", g))
        for kind, path in cands:
            if readable(path.read_text(errors="replace")):
                src[r["id"]] = path
                how[kind] += 1
                break
    return src, how


def main():
    corpus = json.loads((HERE / "data" / "corpus.json").read_text())
    sources, how = text_sources(corpus)
    titles = [(letters(r["title"]), r["id"], r["year"]) for r in corpus if len(letters(r["title"])) >= 28]
    tkeys = defaultdict(list)
    for r in corpus:
        k = title_key(r["title"])
        if k:
            tkeys[k].append(r["id"])

    stats = Counter()
    edges = set()
    clusters = defaultdict(list)
    per_paper = {}
    stats.update({f"source_{k}": v for k, v in how.items()})
    for r in corpus:
        f = sources.get(r["id"])
        if not f:
            continue
        stats["texts"] += 1
        text = f.read_text(errors="replace")
        sec = reference_section(text)
        if not sec:
            stats["no_reference_heading"] += 1
            continue
        entries = split_entries(sec)
        if not entries:
            stats["no_entries"] += 1
            continue
        stats["with_entries"] += 1
        stats["entries"] += len(entries)
        n_int = 0
        for e in entries:
            p = parse(e)
            le = letters(e)
            hit = None
            k = title_key(p["title"]) if p["title"] else None
            if k and k in tkeys:
                hit = tkeys[k][0]
            else:
                for t, tid, ty in titles:
                    if t in le and (p["year"] is None or abs(p["year"] - ty) <= 2):
                        hit = tid
                        break
            if hit and hit != r["id"]:
                edges.add((r["id"], hit))
                n_int += 1
                stats["internal"] += 1
            elif k:
                clusters[k].append({"citer": r["id"], "year": p["year"], "first": p["first"],
                                    "title": p["title"], "raw": e})
                stats["external_keyed"] += 1
            else:
                stats["unkeyed"] += 1
        per_paper[r["id"]] = {"n": len(entries), "internal": n_int}

    ext = []
    for k, items in clusters.items():
        citers = sorted({i["citer"] for i in items})
        if len(citers) < 3:
            continue
        ext.append({
            "key": k,
            "title": Counter(i["title"] for i in items).most_common(1)[0][0],
            "year": Counter(i["year"] for i in items if i["year"]).most_common(1)[0][0] if any(i["year"] for i in items) else None,
            "first": Counter(i["first"] for i in items if i["first"]).most_common(1)[0][0] if any(i["first"] for i in items) else "",
            "n": len(citers), "citers": citers,
            "example": items[0]["raw"],
        })
    ext.sort(key=lambda e: -e["n"])
    out = {"stats": dict(stats), "edges": sorted(edges), "external": ext, "per_paper": per_paper}
    (HERE / "data" / "refs.json").write_text(json.dumps(out, ensure_ascii=False))
    print(json.dumps(stats))
    for e in ext[:50]:
        print(e["n"], e["year"], e["first"], "|", e["title"][:80])


if __name__ == "__main__":
    main()
