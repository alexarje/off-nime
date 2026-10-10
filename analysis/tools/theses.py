"""Collect PhD and master's theses related to NIME, and build bibs/Theses/theses.bib.

Sources:
- OpenAlex works of type dissertation, searched in title and abstract with NIME-related queries
  (OpenAlex charges searches against a small free daily allowance, so pages are capped);
- DataCite records of type Dissertation or Thesis, for the same queries;
- the untyped works on the forward-citation list (works citing the archives), looked up in
  DataCite by title, since most of them are theses.

Every English thesis is scored like the journal sweep (closeness to the archives and contrast
against the journal background), with thresholds set at the median closeness and median contrast of the theses
that cite the archives, and admitted when it passes both, or when it cites at least MIN_CITES archive
entries. Non-English theses go to a separate list. The check: the theses already in off-NIME that the
searches find are scored the same way, and the share of them the rules would admit is reported.
Writes bibs/Theses/theses.bib, output/candidates_theses.tsv and data/theses_stats.json.
"""
import hashlib
import json
import re
import sys
import time
from difflib import SequenceMatcher
from pathlib import Path

import numpy as np
import requests
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer

from parse_refs import letters, title_key

HERE = Path(__file__).resolve().parent.parent
CACHE = HERE / "data" / "theses_cache"
CACHE.mkdir(parents=True, exist_ok=True)
OUT = HERE.parent / "bibs" / "Theses" / "theses.bib"
K = 10
MIN_CITES = 3
NEAR_Q = 50  # percentile of the calibration theses used as the closeness threshold
OPENALEX_PAGES = 4
BUDGET = {"remaining": 1.0}  # OpenAlex's remaining daily allowance in USD, read from response headers
QUERIES = [
    "musical interface", "musical interfaces", "digital musical instrument", "digital musical instruments",
    "new interfaces for musical expression", "gestural control music", "musical gesture", "music interaction",
    "sonic interaction design", "interactive music system", "live electronics", "live coding",
    "electronic musical instrument", "augmented instrument", "hyperinstrument", "motion capture music",
    "sensors music performance", "haptic music", "music controller", "mapping sound synthesis",
    "networked music performance", "laptop orchestra", "interactive sound installation",
    "embodied music interaction", "accessible musical instruments", "instrument design music",
    "interactive sonification", "physical computing music", "machine learning musical instrument",
    "tangible music", "interactive dance sound", "virtual reality musical instrument", "mobile music",
    "robotic musical instrument", "music technology performance", "electroacoustic performance technology",
    "music performance technology design", "real-time audio interaction", "audio-visual performance",
    "sound art interaction", "music and dance technology", "body movement sound", "gesture recognition music",
    "music information retrieval interaction", "generative music interactive", "algorithmic composition interactive",
    "improvisation computer system", "musical agents", "co-creative music system", "collaborative music making technology",
    "music for children technology", "music therapy technology", "assistive music technology", "disability music technology",
    "wearable music", "e-textile sound", "biosignals music", "brain-computer interface music", "eye tracking music",
    "smartphone instrument", "web audio", "spatial audio interaction", "immersive audio performance",
    "electronic music performance", "turntablism DJ technology", "circuit bending", "modular synthesizer",
    "musical expression computer", "expressive performance control", "user study musical instrument",
    "evaluation digital musical instruments", "musician interaction design",
]


def cached(url, params, headers=None, pause=1.0):
    key = hashlib.sha1((url + json.dumps(params, sort_keys=True)).encode()).hexdigest()
    f = CACHE / f"{key}.json"
    if f.exists():
        return json.loads(f.read_text())
    wait = 5
    for _ in range(6):
        try:
            if "openalex" in url and BUDGET["remaining"] < 0.003:
                return None
            r = requests.get(url, params=params, headers=headers or {}, timeout=90)
            if "openalex" in url and r.headers.get("x-ratelimit-remaining-usd"):
                BUDGET["remaining"] = float(r.headers["x-ratelimit-remaining-usd"])
            if r.status_code == 200:
                f.write_text(r.text)
                time.sleep(pause)
                return r.json()
            if r.status_code in (400, 404):
                return None
            if r.status_code == 429 and "openalex" in url:
                print("  OpenAlex daily allowance used up", file=sys.stderr)
                return None
            print(f"  {r.status_code}, waiting {wait} s", file=sys.stderr)
        except requests.RequestException as ex:
            print(f"  {ex}", file=sys.stderr)
        time.sleep(wait)
        wait = min(wait * 2, 120)
    return None


def inverted(ix):
    if not ix:
        return ""
    pos = sorted((p, w) for w, ps in ix.items() for p in ps)
    return " ".join(w for _, w in pos)


def openalex(q):
    out = []
    for page in range(1, OPENALEX_PAGES + 1):
        d = cached("https://api.openalex.org/works",
                   {"filter": f"title_and_abstract.search:{q},type:dissertation", "per-page": 200, "page": page,
                    "select": "id,doi,title,publication_year,authorships,primary_location,abstract_inverted_index,language"})
        if not d:
            break
        for w in d["results"]:
            loc = (w.get("primary_location") or {})
            src = (loc.get("source") or {}).get("display_name") or ""
            # the awarding institution is the author's, where OpenAlex knows it; the source is
            # often a repository such as HAL rather than the university
            insts = [i.get("display_name") for a in w.get("authorships", [])[:1] for i in a.get("institutions", [])]
            src = insts[0] if insts and insts[0] else src
            out.append({"src": "OpenAlex", "id": w["id"], "doi": (w.get("doi") or "").replace("https://doi.org/", "").lower(),
                        "url": loc.get("landing_page_url") or w["id"], "title": w.get("title") or "",
                        "year": w.get("publication_year"),
                        "authors": [a["author"]["display_name"] for a in w.get("authorships", []) if a.get("author")],
                        "school": src, "abstract": inverted(w.get("abstract_inverted_index")),
                        "language": w.get("language")})
        if d["meta"]["count"] <= page * 200:
            break
    return out


EN = {"the", "and", "of", "to", "in", "is", "for", "that", "with", "this", "on", "as", "are", "by", "an", "be"}


def english_share(text):
    words = re.findall(r"[a-zA-Z\u00C0-\u017F]+", text.lower())
    return sum(w in EN for w in words) / len(words) if words else 0.0


def datacite_record(x):
    a = x["attributes"]
    abstracts = [d.get("description", "") for d in a.get("descriptions", []) if d.get("descriptionType") == "Abstract"]
    # repositories such as theses.fr and Montréal give one abstract per language; use the English one
    english = [d for d in abstracts if english_share(d) >= 0.12]
    desc = " ".join(english or abstracts)
    return {"src": "DataCite", "id": x["id"], "doi": x["id"].lower(), "url": a.get("url") or f"https://doi.org/{x['id']}",
            "title": (a.get("titles") or [{}])[0].get("title", ""), "year": int(a["publicationYear"]) if a.get("publicationYear") else None,
            "authors": [c.get("name", "") for c in a.get("creators", [])],
            "school": a.get("publisher") if isinstance(a.get("publisher"), str) else (a.get("publisher") or {}).get("name", ""),
            "abstract": desc, "language": a.get("language")}


def datacite(q):
    out = []
    words = " AND ".join(q.split())
    for rt in [{"resource-type-id": "dissertation"}, {"resource-type": "Thesis"}]:
        d = cached("https://api.datacite.org/dois",
                   dict(rt, **{"query": f"titles.title:({words}) OR descriptions.description:({words})", "page[size]": 1000}))
        for x in (d or {}).get("data", []):
            out.append(datacite_record(x))
    return out


def forward_theses():
    """Untyped works on the forward-citation list, resolved to thesis records in DataCite."""
    rows = [l.split("\t") for l in (HERE / "output" / "candidates_citing.tsv").read_text().splitlines()[1:]]
    found = []
    for r in rows:
        cites, year, title, venue, types = int(r[0]), r[1], r[2], r[4], r[5]
        if venue or (types and "JournalArticle" in types) or len(title) < 15:
            continue
        d = cached("https://api.datacite.org/dois", {"query": f'titles.title:"{title[:150]}"', "page[size]": 5}, pause=0.5)
        for x in (d or {}).get("data", []):
            rec = datacite_record(x)
            rtype = (x["attributes"].get("types") or {})
            kind = f"{rtype.get('resourceTypeGeneral', '')} {rtype.get('resourceType', '')}".lower()
            if ("dissertation" in kind or "thesis" in kind) and \
                    SequenceMatcher(None, letters(rec["title"]), letters(title)).ratio() >= 0.9:
                rec["cites"] = cites
                found.append(rec)
                break
    return found


def main():
    corpus = json.loads((HERE / "data" / "corpus.json").read_text())
    recs = []
    for q in QUERIES:
        a, b = openalex(q), datacite(q)
        recs += a + b
        print(f"{q}: OpenAlex {len(a)}, DataCite {len(b)}", file=sys.stderr, flush=True)
    fwd = forward_theses()
    recs += fwd
    print(f"forward list: {len(fwd)} theses resolved", file=sys.stderr)

    # merge by title and year; keep the record with the most information
    merged = {}
    for r in recs:
        if not r["title"] or not r["year"]:
            continue
        r["title"] = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", r["title"])).strip()
        k = (letters(r["title"])[:80], r["year"])
        m = merged.get(k)
        if m is None or len(r["abstract"]) > len(m["abstract"]):
            keep = r if m is None else dict(r, cites=max(r.get("cites", 0), m.get("cites", 0)))
            merged[k] = keep
        elif r.get("cites"):
            m["cites"] = max(m.get("cites", 0), r["cites"])
    theses = list(merged.values())

    # the check population: off-NIME theses the searches found
    off_theses = [r for r in corpus if r["archive"] == "off-nime" and r["type"] in ("phdthesis", "mastersthesis")]
    off_keys = {title_key(r["title"]): r["id"] for r in off_theses if title_key(r["title"])}
    have = {title_key(r["title"]) for r in corpus if title_key(r["title"])}
    for t in theses:
        t["known"] = off_keys.get(title_key(t["title"]))
        t["in_archive"] = title_key(t["title"]) in have

    jc = json.loads((HERE / "data" / "journal_candidates.json").read_text())
    vec = TfidfVectorizer(stop_words=list(ENGLISH_STOP_WORDS), min_df=3, max_df=0.4, sublinear_tf=True,
                          token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z\-]{2,}\b")
    C = vec.fit_transform([f"{r['title']}. {r['keywords']}. {r['abstract']}" for r in corpus])
    journals = json.loads((HERE / "data" / "journals.json").read_text())
    Lb = vec.transform([f"{re.sub(r'<[^>]+>', '', j['title'])}. {j['abstract']}" for j in journals])
    L = vec.transform([f"{t['title']}. {t['abstract'][:3000]}" for t in theses])
    S = (L @ C.T).toarray()
    col = {r["id"]: j for j, r in enumerate(corpus)}
    for i, t in enumerate(theses):
        if t["known"]:
            S[i, col[t["known"]]] = 0
    near = np.sort(S, axis=1)[:, -K:].mean(1)
    contrast = near - np.sort((L @ Lb.T).toarray(), axis=1)[:, -K:].mean(1)
    # only English text can be scored against the (English) archives; a non-English thesis goes to
    # the list for the non-English sources instead of being admitted by score
    for t in theses:
        t["english"] = english_share(f"{t['title']} {t['abstract'][:3000]}") >= 0.08
    nnz = np.diff(L.indptr)
    for t, a, c, n in zip(theses, near, contrast, nnz):
        t["near"], t["score"], t["terms"] = round(float(a), 4), round(float(c), 4), int(n)
    # thresholds calibrated on theses, not on journal articles: the lower quartile of closeness and
    # of contrast among the English theses known to cite the archives (the forward list). The
    # off-NIME theses are a separate population and serve as the check.
    calib = [t for t in theses if t.get("cites", 0) >= 1 and t["english"] and not t["known"]]
    near_min = float(np.percentile([t["near"] for t in calib], NEAR_Q))
    # contrast at the median: at the lower quartile, a reading of sampled titles found many off-topic
    # theses (music education, club culture, signal processing)
    con_min = float(np.percentile([t["score"] for t in calib], 50))
    for t in theses:
        t["by_score"] = bool(t["english"] and t["near"] >= near_min and t["score"] >= con_min)
        t["admit"] = not t["in_archive"] and (t["by_score"] or t.get("cites", 0) >= MIN_CITES)

    known = [t for t in theses if t["known"]]
    check = {"off_nime_theses": len(off_theses), "found_by_searches": len(known),
             "would_admit": int(sum(t["by_score"] for t in known)),
             "would_admit_pct": round(100 * sum(t["by_score"] for t in known) / max(len(known), 1), 1)}
    admitted = sorted([t for t in theses if t["admit"]], key=lambda t: (t["year"], t["title"]))

    OUT.parent.mkdir(exist_ok=True)
    seen = set()
    with open(OUT, "w") as f:
        for t in admitted:
            first = (t["authors"] or ["anon"])[0]
            sur = re.sub(r"[^a-z]", "", (first.split(",")[0] if "," in first else first.split()[-1]).lower()) or "anon"
            key = f"thesis:{sur}{t['year']}{re.sub(r'[^a-z]', '', t['title'].lower())[:16]}"
            if key in seen:
                continue
            seen.add(key)
            authors = [a if "," in a else (f"{a.split()[-1]}, {' '.join(a.split()[:-1])}" if a.split() else a)
                       for a in t["authors"]]
            why = "; ".join(x for x in [f"cites {t['cites']} archive entries" if t.get("cites") else "",
                                        "selected by similarity to the archives" if t["by_score"] else ""] if x)
            school = t["school"] or ""
            m = re.search(r"\(([^()]*(?:Univ|Institut|College|School|McGill|École|Hochschule)[^()]*)\)\s*$", school)
            school = m.group(1) if m else school
            fields = [("author", " and ".join(authors)), ("title", t["title"]), ("school", school),
                      ("year", t["year"]), ("doi", t["doi"] if t["doi"] else None),
                      ("url", t["url"] if not t["doi"] else None), ("collection", "Theses"),
                      ("note", f"Found in {t['src']}; {why}")]
            body = ",\n".join(f"  {k} = {{{re.sub(r'[{}]', '', str(v))}}}" for k, v in fields if v)
            f.write(f"@phdthesis{{{key},\n{body}\n}}\n\n")
    with open(HERE / "output" / "candidates_theses.tsv", "w") as f:
        f.write("admitted\tscore\tcloseness\tterms\tenglish\tcites\tyear\ttitle\tauthors\tschool\tsource\tdoi_or_url\n")
        for t in sorted(theses, key=lambda t: -t["score"]):
            if t["in_archive"]:
                continue
            f.write("\t".join(re.sub(r"\s+", " ", str(x)) for x in
                              [t["admit"], t["score"], t["near"], t["terms"], t["english"], t.get("cites", ""), t["year"], t["title"],
                               "; ".join(t["authors"][:3]), t["school"], t["src"], t["doi"] or t["url"]]) + "\n")
    with open(HERE / "output" / "candidates_theses_non_english.tsv", "w") as f:
        f.write("year\ttitle\tauthors\tschool\tsource\tdoi_or_url\n")
        for t in sorted((t for t in theses if not t["english"] and not t["in_archive"]), key=lambda t: t["year"]):
            f.write("\t".join(re.sub(r"\s+", " ", str(x)) for x in
                              [t["year"], t["title"], "; ".join(t["authors"][:3]), t["school"], t["src"],
                               t["doi"] or t["url"]]) + "\n")
    stats = {"calibration_theses": len(calib), "near_min": round(near_min, 4), "contrast_min": round(con_min, 4),
             "records": len(recs), "non_english": sum(1 for t in theses if not t["english"]), "theses": len(theses), "admitted": len(seen), "check": {k: int(v) if isinstance(v, (np.integer, np.bool_)) else v for k, v in check.items()},
             "by_source": {s: sum(1 for t in theses if t["src"] == s) for s in ["OpenAlex", "DataCite"]},
             "admitted_by_cites": int(sum(1 for t in admitted if t.get("cites", 0) >= MIN_CITES)),
             "forward_resolved": len(fwd)}
    (HERE / "data" / "theses_stats.json").write_text(json.dumps(stats, indent=1))
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
