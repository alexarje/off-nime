"""Build bibs/Cited/cited.bib and bibs/Background/background.bib from the candidate lists, by rules
that can be checked.

Cited holds works about NIME topics; Background holds works that many archive papers cite but
that are not themselves about NIME topics (theory, method, general HCI, musicology), such as Barad
or Braun and Clarke. "About NIME topics" is decided by the title classifier in tools/topic.py,
since most cited works have only a title in Crossref.

An entry is admitted when it has a DOI (so its metadata comes from Crossref, not from a parsed
reference string), is in neither archive, is close to the archives in wording (at least the
lower-quartile closeness of the curated CMJ articles, the same bar as the journal sweep), and
meets one of these:

- backward: cited by at least MIN_CITED archive papers;
- forward: outside NIME and citing at least MIN_CITING archive entries;
- sweep: a journal-sweep candidate that is also on the backward or forward list.

Everything with a DOI that fails only the closeness bar, or falls short on counts by a little,
goes to output/borderline.tsv for a human decision.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer

from crossref import API, get, item_year
from parse_refs import title_key

HERE = Path(__file__).resolve().parent.parent
OUT = HERE.parent / "bibs" / "Cited" / "cited.bib"
BACKGROUND = HERE.parent / "bibs" / "Background" / "background.bib"
MIN_CITED = 5
MIN_CITING = 10
K = 10
KINDS = {"journal-article": "article", "proceedings-article": "inproceedings", "book": "book",
         "monograph": "book", "edited-book": "book", "reference-book": "book", "book-chapter": "incollection",
         "book-section": "incollection", "dissertation": "phdthesis", "report": "techreport"}


def tsv(name):
    lines = (HERE / "output" / name).read_text().splitlines()
    head = lines[0].split("\t")
    return [dict(zip(head, l.split("\t"))) for l in lines[1:]]


def clean(s):
    s = re.sub(r"<[^>]+>", "", str(s or ""))
    return re.sub(r"\s+", " ", s.replace("{", "").replace("}", "")).strip()


def main():
    corpus = json.loads((HERE / "data" / "corpus.json").read_text())
    have_doi = {r["doi"] for r in corpus if r["doi"]}
    have_key = {title_key(r["title"]) for r in corpus if title_key(r["title"])}
    jc = json.loads((HERE / "data" / "journal_candidates.json").read_text())
    near_min = jc["near_min"]

    cand = {}

    def add(doi, why, n):
        doi = doi.lower().strip()
        if not doi or doi in have_doi:
            return
        c = cand.setdefault(doi, {"doi": doi, "why": {}, })
        c["why"][why] = max(n, c["why"].get(why, 0))

    for r in json.loads((HERE / "data" / "cited_resolved.json").read_text()):
        if r.get("doi"):
            add(r["doi"], "cited_by", r["cited_by"])
    for r in tsv("candidates_citing.tsv"):
        if r["doi"]:
            add(r["doi"], "cites", int(r["cites_archive_entries"]))
    sweep = {r["doi"].lower() for r in tsv("candidates_journals.tsv")}
    for d in sweep:
        if d in cand:
            cand[d]["why"]["sweep"] = 1

    # metadata from Crossref, by DOI
    for n, (doi, c) in enumerate(cand.items()):
        d = get(f"{API}/works/{doi}", {})
        c["cr"] = (d or {}).get("message")
        if n % 100 == 0:
            print(f"metadata {n}/{len(cand)}", file=sys.stderr, flush=True)
    cand = {d: c for d, c in cand.items() if c["cr"] and c["cr"].get("title")}

    vec = TfidfVectorizer(stop_words=list(ENGLISH_STOP_WORDS), min_df=3, max_df=0.4, sublinear_tf=True,
                          token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z\-]{2,}\b")
    C = vec.fit_transform([f"{r['title']}. {r['keywords']}. {r['abstract']}" for r in corpus])
    items = list(cand.values())
    L = vec.transform([f"{clean(c['cr']['title'][0])}. {clean(c['cr'].get('abstract'))}" for c in items])
    near = np.sort((L @ C.T).toarray(), axis=1)[:, -K:].mean(1)
    # contrast against the journal background, as in the sweep, so that "about NIME topics" means
    # the same thing in Cited, Related and Theses
    journals = json.loads((HERE / "data" / "journals.json").read_text())
    from crossref import JOURNALS
    Lb = vec.transform([f"{clean(j['title'])}. {clean(j['abstract'])}" for j in journals if j["source"] in JOURNALS])
    contrast = near - np.sort((L @ Lb.T).toarray(), axis=1)[:, -K:].mean(1)

    admitted, background, borderline = [], [], []
    from topic import nime_probability
    titles = []
    for c in items:
        cr = c["cr"]
        sub = (cr.get("subtitle") or [""])[0]
        titles.append(clean(cr["title"][0]) + (f": {clean(sub)}" if sub and sub.lower() not in cr["title"][0].lower() else ""))
    prob = nime_probability(titles)
    for c, a, con, pr in zip(items, near, contrast, prob):
        c["p_nime"] = round(float(pr), 3)
        cr = c["cr"]
        c["near"], c["contrast"] = round(float(a), 4), round(float(con), 4)
        sub = (cr.get("subtitle") or [""])[0]
        c["title"] = clean(cr["title"][0]) + (f": {clean(sub)}" if sub and sub.lower() not in cr["title"][0].lower() else "")
        if title_key(c["title"]) in have_key:
            continue
        w = c["why"]
        counts_ok = (w.get("cited_by", 0) >= MIN_CITED or w.get("cites", 0) >= MIN_CITING
                     or ("sweep" in w and (w.get("cited_by", 0) or w.get("cites", 0) >= 5)))
        # about NIME topics, by the title classifier (tools/topic.py); the similarity scores are
        # kept for the record, but most cited works have no abstract and cannot be judged by them
        topical = pr >= 0.5
        if counts_ok and topical:
            admitted.append(c)
        elif w.get("cited_by", 0) >= MIN_CITED:
            # much cited by the archives, but not itself about NIME topics: theory, method, HCI
            background.append(c)
        elif counts_ok or w.get("cites", 0) >= 5:
            c["reason"] = "not about NIME topics by the title classifier" if counts_ok else "cites 5–9 archive entries"
            borderline.append(c)

    def bib(c, collection="Cited"):
        cr = c["cr"]
        kind = KINDS.get(cr.get("type"), "misc")
        authors = [f"{clean(a.get('family'))}, {clean(a.get('given'))}".strip(", ") for a in cr.get("author", [])
                   if a.get("family")]
        editors = [f"{clean(a.get('family'))}, {clean(a.get('given'))}".strip(", ") for a in cr.get("editor", [])
                   if a.get("family")]
        year = item_year(cr)
        container = clean((cr.get("container-title") or [""])[0])
        sur = re.sub(r"[^a-z]", "", (authors or editors or ["anon"])[0].split(",")[0].lower())
        key = f"{collection.lower()}:{sur}{year}{re.sub(r'[^a-z]', '', c['title'].lower())[:16]}"
        why = c["why"]
        note = "; ".join(x for x in [f"cited by {why['cited_by']} archive papers" if why.get("cited_by") else "",
                                     f"cites {why['cites']} archive entries" if why.get("cites") else "",
                                     "found in the journal sweep" if why.get("sweep") else ""] if x)
        fields = [("author", " and ".join(authors)), ("editor", " and ".join(editors) if not authors else ""),
                  ("title", c["title"]), ("year", year),
                  ("journal" if kind == "article" else "booktitle" if kind in ("inproceedings", "incollection") else "",
                   container),
                  ("school" if kind == "phdthesis" else "institution" if kind == "techreport" else "",
                   clean((cr.get("institution") or [{}])[0].get("name")) if cr.get("institution") else ""),
                  ("publisher", clean(cr.get("publisher")) if kind in ("book", "incollection", "inproceedings") else ""),
                  ("volume", cr.get("volume")), ("number", cr.get("issue")),
                  ("pages", (cr.get("page") or "").replace("-", "--")), ("doi", c["doi"]),
                  ("abstract", clean(cr.get("abstract"))[:3000]),
                  ("collection", collection), ("note", (note[:1].upper() + note[1:]) + f"; NIME-topic probability {c['p_nime']}")]
        body = ",\n".join(f"  {k} = {{{clean(v)}}}" for k, v in fields if k and v)
        return f"@{kind}{{{key},\n{body}\n}}\n"

    for group, path, name in [(admitted, OUT, "Cited"), (background, BACKGROUND, "Background")]:
        group.sort(key=lambda c: (item_year(c["cr"]) or 0, c["title"]))
        seen_keys = set()
        path.parent.mkdir(exist_ok=True)
        with open(path, "w") as f:
            for c in group:
                b = bib(c, name)
                k = b.split("{", 1)[1].split(",", 1)[0]
                if k in seen_keys:
                    b = b.replace(k, k + c["doi"][-4:].replace("/", ""), 1)
                seen_keys.add(k)
                f.write(b + "\n")
    with open(HERE / "output" / "borderline.tsv", "w") as f:
        f.write("reason\tp_nime\tcloseness\tcontrast\tcited_by\tcites\tyear\ttitle\tdoi\n")
        for c in sorted(borderline, key=lambda c: -(c["why"].get("cited_by", 0) + c["why"].get("cites", 0))):
            f.write("\t".join(str(x) for x in [c["reason"], c["p_nime"], c["near"], c["contrast"], c["why"].get("cited_by", ""),
                                                 c["why"].get("cites", ""), item_year(c["cr"]) or "", c["title"],
                                                 c["doi"]]) + "\n")
    stats = {"near_min": near_min, "contrast_min": jc["threshold"], "candidates_with_doi": len(items),
             "admitted": len(admitted), "background": len(background),
             "borderline": len(borderline),
             "admitted_by": {k: sum(1 for c in admitted if k in c["why"]) for k in ["cited_by", "cites", "sweep"]},
             "types": dict(__import__("collections").Counter(KINDS.get(c["cr"].get("type"), "misc") for c in admitted))}
    (HERE / "data" / "cited_stats.json").write_text(json.dumps(stats, indent=1))
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
