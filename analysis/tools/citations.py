"""Merge the citation evidence into data/citations.json and the candidate lists in output/.

Sources: reference lists parsed from the paper texts (data/refs.json), the few reference
lists Semantic Scholar does return (data/s2/), and forward citations (data/s2_citing/).

- Backward: works cited by at least MIN_CITES archive entries but present in neither archive,
  output/candidates_cited.tsv. These are the field's missing foundations.
- Forward: works outside NIME that cite at least MIN_CITING archive entries,
  output/candidates_citing.tsv. These are the field's missing continuations.
"""
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import networkx as nx
import numpy as np

from analyse import fa2
from parse_refs import letters, title_key

HERE = Path(__file__).resolve().parent.parent
MIN_CITES = 5
MIN_CITES_VIZ = 8
MIN_CITING = 5
SEED = 1


def load_s2(corpus):
    s2, citing = {}, {}
    for r in corpus:
        name = r["id"].replace(":", "__").replace("/", "_") + ".json"
        f, g = HERE / "data" / "s2" / name, HERE / "data" / "s2_citing" / name
        if f.exists():
            s2[r["id"]] = json.loads(f.read_text())["paper"]
        if g.exists():
            citing[r["id"]] = json.loads(g.read_text())["paper"]
    return s2, citing


def is_nime_venue(v):
    return bool(re.search(r"new interfaces for musical expression|\bnime\b", (v or "").lower()))


def main():
    corpus = json.loads((HERE / "data" / "corpus.json").read_text())
    by_id = {r["id"]: r for r in corpus}
    refs = json.loads((HERE / "data" / "refs.json").read_text())
    s2, citing = load_s2(corpus)
    tkeys = {title_key(r["title"]): r["id"] for r in corpus if title_key(r["title"])}
    pid2corpus = {p["paperId"]: rid for rid, p in s2.items() if p}

    # backward edges: parsed lists plus Semantic Scholar where it has them
    edges = {tuple(e) for e in refs["edges"]}
    parsed_edges, parsed_papers = set(edges), set(refs["per_paper"])
    s2_edges = set()
    ext = {e["key"]: dict(e, citers=set(e["citers"])) for e in refs["external"]}
    s2_ref_papers = 0
    for rid, p in s2.items():
        if not p or not p.get("references"):
            continue
        s2_ref_papers += 1
        for ref in p["references"]:
            tgt = pid2corpus.get(ref.get("paperId")) or tkeys.get(title_key(ref.get("title") or ""))
            if tgt and tgt != rid:
                edges.add((rid, tgt))
                s2_edges.add((rid, tgt))
            elif ref.get("title") and title_key(ref["title"]):
                k = title_key(ref["title"])
                e = ext.setdefault(k, {"key": k, "title": ref["title"], "year": ref.get("year"),
                                       "first": (ref.get("authors") or [{}])[0].get("name", ""), "citers": set(),
                                       "example": ""})
                e["citers"].add(rid)
    # forward edges inside the corpus, and external citing works
    outside = {}
    for rid, p in citing.items():
        if not p:
            continue
        for c in p.get("citations") or []:
            src = pid2corpus.get(c.get("paperId"))
            if src and src != rid:
                edges.add((src, rid))
                continue
            if not c.get("paperId") or not c.get("title"):
                continue
            o = outside.setdefault(c["paperId"], {"pid": c["paperId"], "title": c["title"], "year": c.get("year"),
                                                  "venue": c.get("venue") or "", "doi": (c.get("externalIds") or {}).get("DOI"),
                                                  "authors": [a.get("name") for a in (c.get("authors") or [])][:6],
                                                  "types": c.get("publicationTypes") or [], "cites": set()})
            o["cites"].add(rid)

    cited = []
    for e in ext.values():
        n = len(e["citers"])
        if n < MIN_CITES:
            continue
        cs = sorted(e["citers"])
        cited.append({"key": e["key"], "title": e["title"], "year": e["year"], "first": e["first"], "n": n,
                      "n_off": sum(by_id[c]["archive"] == "off-nime" for c in cs),
                      "n_nime": sum(by_id[c]["archive"] == "nime" for c in cs),
                      "first_cited": min(by_id[c]["year"] for c in cs), "citers": cs, "example": e.get("example", "")})
    cited.sort(key=lambda e: -e["n"])
    citing_out = sorted([dict(o, n=len(o["cites"]), cites=sorted(o["cites"])) for o in outside.values()
                         if len(o["cites"]) >= MIN_CITING and not is_nime_venue(o["venue"])
                         and title_key(o["title"]) not in tkeys],
                        key=lambda o: -o["n"])

    with open(HERE / "output" / "candidates_cited.tsv", "w") as f:
        f.write("cited_by\tcited_by_off_nime\tcited_by_nime\tyear\tfirst_author\ttitle\tfirst_cited\texample_reference\n")
        for c in cited:
            f.write("\t".join(re.sub(r"\s+", " ", str(x)) for x in [c["n"], c["n_off"], c["n_nime"], c["year"] or "", c["first"],
                                                 c["title"], c["first_cited"], c["example"]]) + "\n")
    with open(HERE / "output" / "candidates_citing.tsv", "w") as f:
        f.write("cites_archive_entries\tyear\ttitle\tauthors\tvenue\ttypes\tdoi\ts2_id\n")
        for o in citing_out:
            f.write("\t".join(re.sub(r"\s+", " ", str(x)) for x in [o["n"], o["year"] or "", o["title"], "; ".join(o["authors"]),
                                                 o["venue"], ",".join(o["types"]), o["doi"] or "", o["pid"]]) + "\n")

    # citation network for the viewer: archive entries with any citation link, plus the most cited missing works
    G = nx.DiGraph()
    for a, b in edges:
        G.add_edge(a, b)
    viz_ext = [c for c in cited if c["n"] >= MIN_CITES_VIZ]
    for c in viz_ext:
        for s in c["citers"]:
            G.add_edge(s, "ext:" + c["key"])
    U = G.to_undirected()
    pos = fa2(U)
    extd = {"ext:" + c["key"]: c for c in viz_ext}
    cnodes, idx = [], {}
    for n in G.nodes:
        x, y = pos[n]
        if n in extd:
            c = extd[n]
            node = {"t": c["title"], "a": c["first"].title(), "y0": c["year"], "g": 2, "d": c["n"], "c": c["citers"],
                    "s": f"{c['first'].split()[-1].title() if c['first'] else ''} {c['year'] or ''}".strip(),
                    "u": "https://scholar.google.com/scholar?q=" + re.sub(r"\s+", "+", c["title"])}
        else:
            r = by_id[n]
            node = {"t": r["title"], "a": ", ".join(r["names"][:3]), "y0": r["year"], "v": r["channel"],
                    "g": 1 if r["archive"] == "off-nime" else 0, "d": G.in_degree(n), "id": n,
                    "c": sorted(G.predecessors(n)),
                    "s": f"{r['names'][0].split()[-1] if r['names'] else ''} {r['year']}",
                    "u": r["url"] or (f"https://doi.org/{r['doi']}" if r["doi"] else None)}
        node["x"], node["y"] = round(float(x), 4), round(float(y), 4)
        idx[n] = len(cnodes)
        cnodes.append(node)
    cedges = [[idx[a], idx[b]] for a, b in G.edges]

    indeg = Counter(b for _, b in edges)
    # checks: a parsed link to a later paper is wrong (allowing one year for preprints and
    # same-volume citations), and Semantic Scholar's own lists give the parser's recall
    later = [(a, b) for a, b in parsed_edges if by_id[b]["year"] > by_id[a]["year"] + 1]
    both = {e for e in s2_edges if e[0] in parsed_papers}
    checks = {"parsed_edges": len(parsed_edges), "parsed_to_later_paper": len(later),
              "parsed_to_later_share": round(100 * len(later) / max(len(parsed_edges), 1), 2),
              "later_examples": [[by_id[a]["title"], by_id[a]["year"], by_id[b]["title"], by_id[b]["year"]] for a, b in later[:8]],
              "s2_edges_in_parsed_papers": len(both),
              "recall_against_s2": round(100 * len(both & parsed_edges) / max(len(both), 1), 1)}
    out = {
        "edges": sorted(edges),
        "cc": {rid: p.get("citationCount") for rid, p in s2.items() if p},
        "cnodes": cnodes, "cedges": cedges,
        "cited": [{k: c[k] for k in ["title", "year", "first", "n", "n_off", "n_nime", "first_cited"]} for c in cited[:150]],
        "citing": [{k: o[k] for k in ["title", "year", "venue", "authors", "n", "doi"]} for o in citing_out[:150]],
        "most_cited_internal": [[by_id[k]["title"], by_id[k]["year"], by_id[k]["channel"], v]
                                for k, v in indeg.most_common(40)],
        "stats": {"parsed": refs["stats"], "s2_found": sum(1 for p in s2.values() if p),
                  "s2_found_by_archive": dict(Counter(by_id[k]["archive"] for k, p in s2.items() if p)),
                  "s2_with_references": s2_ref_papers, "citing_fetched": sum(1 for p in citing.values() if p),
                  "internal_edges": len(edges),
                  "edges_by_direction": dict(Counter(f"{by_id[a]['archive']}->{by_id[b]['archive']}" for a, b in edges)),
                  "cited_candidates": len(cited), "citing_candidates": len(citing_out),
                  "cnodes": len(cnodes), "cedges": len(cedges), "checks": checks},
    }
    (HERE / "data" / "citations.json").write_text(json.dumps(out, ensure_ascii=False))
    print(json.dumps(out["stats"], indent=1))
    for c in cited[:30]:
        print(c["n"], c["year"], c["first"], "|", c["title"][:80])
    for o in citing_out[:15]:
        print("<-", o["n"], o["year"], o["venue"][:30], "|", o["title"][:70])


if __name__ == "__main__":
    main()
