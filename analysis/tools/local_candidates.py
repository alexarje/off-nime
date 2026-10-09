"""Rank papers in the local conference archive by how close they are to the NIME literature.

Every local text not already in either archive is represented by its first page (title and
abstract), and scored by its mean cosine similarity to its ten nearest entries in the joined
archives. As a check that the score can fail, the curated off-NIME ICMC papers that exist
locally are scored the same way, and their percentile among all ICMC texts is reported: a
score that ranks them no better than chance would be no basis for a candidate list.
Writes output/candidates_local.tsv and data/local_candidates.json.
"""
import json
import re
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer

from parse_refs import letters, readable

HERE = Path(__file__).resolve().parent.parent
LOCAL = HERE / "data" / "local_text"
K = 10


def first_page(text):
    page = text.split("\f")[0]
    return re.sub(r"\s+", " ", page)[:3000]


def guess_title(text):
    lines = [l.strip() for l in text.split("\f")[0].splitlines() if l.strip()]
    out = []
    for l in lines[:6]:
        if re.search(r"@|universit|institut|department|abstract|\b(19|20)\d\d\b|proceedings|^page", l, re.I):
            break
        out.append(l)
        if len(" ".join(out)) > 60:
            break
    return " ".join(out)[:200]


def main():
    corpus = json.loads((HERE / "data" / "corpus.json").read_text())
    ctext = [f"{r['title']}. {r['keywords']}. {r['abstract']}" for r in corpus]
    clet = [letters(r["title"])[:30] for r in corpus]
    title_index = {t: r["id"] for t, r in zip(clet, corpus) if len(t) >= 20}

    rows, seen = [], set()
    for f in sorted(LOCAL.rglob("*.txt")):
        rel = f.relative_to(LOCAL)
        if rel.parts[:3] == ("NIME", "nime-PDFs", "OCR"):
            continue
        text = f.read_text(errors="replace")
        pages = text.count("\f")
        # papers only: whole volumes, programme books and one-page index sheets are skipped
        if not readable(text) or not 2 <= pages <= 20:
            continue
        fp = first_page(text)
        lf = letters(fp)
        if re.match(r"(topic|program|programme|proceedings|table of contents|index)\b", guess_title(text), re.I):
            continue
        dupkey = lf[:120]
        if dupkey in seen:
            continue
        seen.add(dupkey)
        in_corpus = next((cid for t, cid in title_index.items() if t in lf), None)
        y = re.search(r"(19[5-9]\d|20[0-2]\d)", str(rel))
        rows.append({"file": str(rel), "set": rel.parts[0], "year": int(y.group(1)) if y else None,
                     "title": guess_title(text), "text": fp, "in_corpus": in_corpus})

    vec = TfidfVectorizer(stop_words=list(ENGLISH_STOP_WORDS), min_df=3, max_df=0.4, sublinear_tf=True,
                          token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z\-]{2,}\b")
    C = vec.fit_transform(ctext)
    L = vec.transform([r["text"] for r in rows])
    S = (L @ C.T).toarray()
    top = np.sort(S, axis=1)[:, -K:]
    score = top.mean(1)
    nn = S.argsort(axis=1)[:, -3:][:, ::-1]
    for r, s, n in zip(rows, score, nn):
        r["score"] = round(float(s), 4)
        r["nearest"] = [corpus[j]["title"] for j in n]

    # the check: curated ICMC papers among all ICMC texts
    icmc = [r for r in rows if r["set"] == "ICMC"]
    curated = [r for r in icmc if r["in_corpus"]]
    allscores = np.array([r["score"] for r in icmc])
    pct = [float((allscores < r["score"]).mean() * 100) for r in curated]
    check = {"icmc_texts": len(icmc), "curated_found_locally": len(curated),
             "curated_median_percentile": round(float(np.median(pct)), 1) if pct else None,
             "curated_share_in_top_quarter": round(float(np.mean([p >= 75 for p in pct]) * 100), 1) if pct else None}

    cands = sorted([r for r in rows if not r["in_corpus"]], key=lambda r: -r["score"])
    thresh = float(np.percentile([r["score"] for r in curated], 25)) if curated else None
    for r in cands:
        r["above_curated_q1"] = thresh is not None and r["score"] >= thresh
    with open(HERE / "output" / "candidates_local.tsv", "w") as f:
        f.write("score\tabove_curated_q1\tset\tyear\tguessed_title\tfile\tnearest_archive_entry\n")
        for r in cands:
            f.write("\t".join(str(x) for x in [r["score"], r["above_curated_q1"], r["set"], r["year"] or "",
                                                 r["title"], r["file"], r["nearest"][0]]) + "\n")
    summary = {"check": check, "threshold": thresh, "texts": len(rows),
               "by_set": dict(Counter(r["set"] for r in rows)),
               "candidates_above": dict(Counter(r["set"] for r in cands if r["above_curated_q1"])),
               "top": [{k: r[k] for k in ["score", "set", "year", "title", "file", "nearest"]} for r in cands[:300]]}
    (HERE / "data" / "local_candidates.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1))
    print(json.dumps({k: summary[k] for k in ["check", "threshold", "texts", "by_set", "candidates_above"]}, indent=1))
    for r in cands[:30]:
        print(r["score"], r["set"], r["year"], "|", r["title"][:80])


if __name__ == "__main__":
    main()
