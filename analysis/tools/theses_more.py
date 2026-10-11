"""More sources of theses for theses.py, beyond its keyword searches.

- citing(): OpenAlex dissertations that cite archive works. The archive works are found in OpenAlex
  by DOI; each thesis gets the number of archive works it cites, which theses.py admits on.
- by_authors(): OpenAlex dissertations by authors with at least MIN_PAPERS archive works, written
  within a few years of those works, since a doctoral student's thesis follows their papers. These
  are admitted only by score, like the keyword results.
- thesesfr(q): defended theses in theses.fr (France), with the English title and abstract where the
  record has them.
- zotero(): theses in the maintainer's Zotero library that the collection lacks, as written by
  zotero_check.py to data/zotero_theses.json (private, not committed).

All network calls go through theses.cached(), which caches every response and stops OpenAlex
calls before the daily allowance runs out, so a stopped run resumes the next day.
"""
import json
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
OA = "https://api.openalex.org/works"
BATCH = 50
MIN_PAPERS = 2
BEFORE, AFTER = 3, 6  # thesis years allowed around an author's archive works
FIELDS = "id,doi,title,publication_year,authorships,primary_location,abstract_inverted_index,language"


def record(w, src, inverted):
    loc = w.get("primary_location") or {}
    insts = [i.get("display_name") for a in w.get("authorships", [])[:1] for i in a.get("institutions", [])]
    return {"src": src, "id": w["id"], "doi": (w.get("doi") or "").replace("https://doi.org/", "").lower(),
            "url": loc.get("landing_page_url") or w["id"], "title": w.get("title") or "",
            "year": w.get("publication_year"),
            "authors": [a["author"]["display_name"] for a in w.get("authorships", []) if a.get("author")],
            "school": (insts[0] if insts and insts[0] else ((loc.get("source") or {}).get("display_name") or "")),
            "abstract": inverted(w.get("abstract_inverted_index")), "language": w.get("language")}


def archive_works(corpus, cached):
    """OpenAlex ids, years and authors of the archive works that have a DOI there."""
    dois = sorted({r["doi"].lower() for r in corpus if r.get("doi") and r["doi"] != "None"})
    works = {}
    for i in range(0, len(dois), BATCH):
        d = cached(OA, {"filter": "doi:" + "|".join(dois[i:i + BATCH]), "per-page": BATCH,
                        "select": "id,doi,publication_year,authorships"})
        if not d:
            break
        for w in d["results"]:
            works[w["id"].rsplit("/", 1)[-1]] = {
                "year": w.get("publication_year"),
                "authors": [a["author"]["id"].rsplit("/", 1)[-1] for a in w.get("authorships", [])
                            if (a.get("author") or {}).get("id")]}
    return works


def citing(works, cached, inverted, pages=5):
    ids, out = sorted(works), {}
    for i in range(0, len(ids), BATCH):
        for page in range(1, pages + 1):
            d = cached(OA, {"filter": f"cites:{'|'.join(ids[i:i + BATCH])},type:dissertation", "per-page": 200,
                            "page": page, "select": FIELDS + ",referenced_works"})
            if not d:
                break
            for w in d["results"]:
                refs = {x.rsplit("/", 1)[-1] for x in w.get("referenced_works") or []}
                r = out.get(w["id"]) or record(w, "OpenAlex (citing)", inverted)
                r["cites"] = len(refs & set(works))
                out[w["id"]] = r
            if d["meta"]["count"] <= page * 200:
                break
    return list(out.values())


def by_authors(works, cached, inverted):
    years = defaultdict(list)
    for w in works.values():
        for a in w["authors"]:
            if w["year"]:
                years[a].append(w["year"])
    authors = sorted(a for a, ys in years.items() if len(ys) >= MIN_PAPERS)
    out = []
    for i in range(0, len(authors), BATCH):
        chunk = authors[i:i + BATCH]
        d = cached(OA, {"filter": f"authorships.author.id:{'|'.join(chunk)},type:dissertation", "per-page": 200,
                        "select": FIELDS})
        if not d:
            break
        for w in d["results"]:
            first = (((w.get("authorships") or [{}])[0].get("author") or {}).get("id") or "").rsplit("/", 1)[-1]
            ys, y = years.get(first), w.get("publication_year")
            if ys and y and min(ys) - BEFORE <= y <= max(ys) + AFTER:
                out.append(record(w, "OpenAlex (author)", inverted))
    return out, len(authors)


FR_QUERIES = ["interface musicale", "instrument de musique numérique", "lutherie numérique", "geste musical",
              "contrôle gestuel", "musique interactive", "interaction musicale", "synthèse sonore temps réel",
              "instrument augmenté", "captation du geste", "recherche-création musique", "dispositif musical interactif",
              "musique électroacoustique interactive", "performance musicale numérique", "informatique musicale"]


def thesesfr(q, cached):
    out = []
    d = cached("https://theses.fr/api/v1/theses/recherche/", {"q": q, "debut": 0, "nombre": 200}, pause=0.5)
    for t in (d or {}).get("theses", []):
        if t.get("status") != "soutenue" or not t.get("id"):
            continue
        full = cached(f"https://theses.fr/api/v1/theses/these/{t['id']}", {}, pause=0.5) or {}
        resumes = full.get("resumes") or {}
        m = re.search(r"(\d{4})$", t.get("dateSoutenance") or "")
        out.append({"src": "theses.fr", "id": t["id"], "doi": (t.get("doi") or "").lower(),
                    "url": f"https://theses.fr/{t['id']}", "title": t.get("titreEN") or t.get("titrePrincipal") or "",
                    "year": int(m.group(1)) if m else None,
                    "authors": [f"{a.get('nom', '')}, {a.get('prenom', '')}" for a in t.get("auteurs", [])],
                    "school": t.get("etabSoutenanceN") or "", "abstract": resumes.get("en") or resumes.get("fr") or "",
                    "language": "en" if resumes.get("en") else "fr"})
    return out


def zotero():
    f = HERE / "data" / "zotero_theses.json"
    return [dict(r, src="Zotero") for r in json.loads(f.read_text())] if f.exists() else []
