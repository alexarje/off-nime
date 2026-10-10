"""Topic model, paper map, author network and summary statistics for the joined archives.

Reads data/corpus.json (and data/citations.json when present) and writes data/graph.json,
which the viewer in output/ embeds, and data/stats.json, which the report quotes.
"""
import json
import re
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

import community as louvain
import networkx as nx
import numpy as np
from sklearn.decomposition import NMF, TruncatedSVD
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.manifold import TSNE

HERE = Path(__file__).resolve().parent.parent
K_TOPICS = 16
SEED = 1

EXTRA_STOP = {"paper", "music", "musical", "new", "using", "based", "use", "work", "approach",
              "present", "presents", "presented", "describe", "describes", "discuss", "discussed",
              "nime", "proceedings", "conference", "international", "computer", "design", "designed",
              "project", "research", "study", "piece", "performance", "performances", "performer",
              "performers", "system", "systems", "instrument", "instruments", "interface", "interfaces",
              "different", "way", "ways", "also", "allows", "allow", "results", "new", "explore",
              "explores", "exploring", "developed", "development", "provide", "provides", "including",
              "article", "examine", "context", "propose", "proposed", "time", "art", "real-time", "real",
              "interactive", "digital", "audio", "sound", "university", "electronic", "control", "data",
              "technology", "technologies", "application", "applications", "user", "users", "creative",
              "make", "making", "focus", "paper describes", "paper presents", "artistic", "practice",
              "practices", "novel", "general", "survey", "techniques", "technique", "methods", "method"}


def text_of(r):
    # Off-NIME entries carry titles only; sublinear term frequency keeps abstracts from swamping them.
    return f"{r['title']}. {r['keywords']}. {r['abstract']}"


def topic_model(recs):
    vec = TfidfVectorizer(stop_words=list(ENGLISH_STOP_WORDS | EXTRA_STOP), min_df=4, max_df=0.3,
                          ngram_range=(1, 2), token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z\-]{2,}\b",
                          sublinear_tf=True)
    # Fit on papers only, since concert and installation notes describe pieces rather than research,
    # then project the notes onto the same topics.
    # The datasets added around the archives (Cited, Related and so on) are placed on the map but
    # do not shape the topics, which describe the two archives.
    is_paper = np.array([not r["dataset"].startswith(("NIME music", "NIME installations")) and r["archive"] != "added"
                         for r in recs])
    texts = [text_of(r) for r in recs]
    vec.fit([t for t, ok in zip(texts, is_paper) if ok])
    X = vec.transform(texts)
    nmf = NMF(n_components=K_TOPICS, random_state=SEED, init="nndsvda", max_iter=800)
    nmf.fit(X[is_paper])
    W = nmf.transform(X)
    terms = np.array(vec.get_feature_names_out())
    topics = []
    for k, comp in enumerate(nmf.components_):
        top = [t for t in terms[comp.argsort()[::-1]][:12]]
        # drop a bigram's parts when the bigram is already listed
        words = []
        for t in top:
            if not any(t != w and t in w.split() for w in top if " " in w):
                words.append(t)
        topics.append({"id": k, "terms": words[:8], "label": " · ".join(words[:3])})
    dom = W.argmax(axis=1)
    dom[W.max(axis=1) == 0] = -1
    return X, W, dom, topics


def paper_map(X):
    Z = TruncatedSVD(n_components=50, random_state=SEED).fit_transform(X)
    Z /= np.linalg.norm(Z, axis=1, keepdims=True) + 1e-9
    Y = TSNE(n_components=2, perplexity=35, init="pca", random_state=SEED, metric="cosine").fit_transform(Z)
    Y = (Y - Y.min(0)) / (Y.max(0) - Y.min(0))
    return Y


def author_network(recs):
    G = nx.Graph()
    names = defaultdict(Counter)
    for r in recs:
        for a, n in zip(r["authors"], r["names"]):
            names[a][n] += 1
            if a not in G:
                G.add_node(a, papers=0, off=0, nime=0, first=r["year"], last=r["year"])
            d = G.nodes[a]
            d["papers"] += 1
            d["off" if r["archive"] == "off-nime" else "nime"] += 1
            d["first"] = min(d["first"], r["year"])
            d["last"] = max(d["last"], r["year"])
        for a, b in combinations(sorted(set(r["authors"])), 2):
            w = G[a][b]["weight"] + 1 if G.has_edge(a, b) else 1
            G.add_edge(a, b, weight=w)
    for a in G:
        G.nodes[a]["name"] = names[a].most_common(1)[0][0]
    return G


def layout_authors(G):
    """Lay out authors with at least two entries, or one entry in both archives' neighbourhood."""
    keep = [a for a, d in G.nodes(data=True) if d["papers"] >= 2]
    H = G.subgraph(keep).copy()
    comms = louvain.best_partition(H, random_state=SEED, weight="weight")
    pos = pack_components(H)
    return H, comms, pos


def pack_components(H):
    """Lay out the largest component with ForceAtlas2 in the unit square, and pack the smaller
    components, each with its own spring layout, in rows in a band below it."""
    comps = sorted(nx.connected_components(H), key=len, reverse=True)
    pos = fa2(H.subgraph(comps[0]), weight="weight")
    rest = comps[1:]
    per_row = int(np.ceil(np.sqrt(len(rest) * 3))) if rest else 1
    cell = 1.0 / per_row
    for i, comp in enumerate(rest):
        sub = H.subgraph(comp)
        local = nx.spring_layout(sub, seed=SEED) if len(comp) > 1 else {next(iter(comp)): np.zeros(2)}
        xy = np.array(list(local.values()))
        span = max(np.ptp(xy, axis=0).max(), 1e-9)
        r, c = divmod(i, per_row)
        for n, v in local.items():
            pos[n] = np.array([c * cell + cell / 2, 1.08 + r * cell + cell / 2]) + (v - xy.mean(0)) / span * cell * 0.6
    ys = np.array([v[1] for v in pos.values()])
    top = ys.max() + 0.02
    return {n: np.array([v[0], v[1] / top]) for n, v in pos.items()}


def fa2(G, weight=None):
    """ForceAtlas2 with default forces, which placed linked nodes closest in a comparison with
    spring and LinLog layouts. Scaled to the unit square with the outermost 2% clipped, since
    small components drift far from the main one."""
    pos = nx.forceatlas2_layout(G, max_iter=1000, weight=weight, seed=SEED)
    xy = np.array(list(pos.values()))
    lo, hi = np.percentile(xy, 1, axis=0), np.percentile(xy, 99, axis=0)
    return {n: np.clip((v - lo) / (hi - lo), -0.03, 1.03) for n, v in pos.items()}


ADDED = ("Cited", "Related", "Theses", "Background", "Historical", "Zotero")


def added_records():
    """The datasets built around the archives, read from bibs/, for the paper map only."""
    import bibtexparser
    from bibtexparser.bparser import BibTexParser
    from bibtexparser.customization import convert_to_unicode
    from build_corpus import split_authors
    out = []
    for name in ADDED:
        f = HERE.parent / "bibs" / name / f"{name.lower()}.bib"
        if not f.exists():
            continue
        parser = BibTexParser(common_strings=True)
        parser.customization = convert_to_unicode
        for e in bibtexparser.loads(f.read_text(), parser=parser).entries:
            m = re.search(r"\d{4}", e.get("year", ""))
            if not e.get("title") or not m:
                continue
            venue = e.get("journal") or e.get("booktitle") or e.get("publisher") or e.get("school") or ""
            out.append({"id": e["ID"], "archive": "added", "dataset": name, "year": int(m.group(0)),
                        "title": e["title"], "keywords": "", "abstract": e.get("abstract", ""),
                        "names": [n for _, n in split_authors(e.get("author") or e.get("editor") or "")],
                        "authors": [], "channel": venue, "venue": venue, "doi": e.get("doi"), "url": e.get("url")})
    return out


def main():
    recs = json.loads((HERE / "data" / "corpus.json").read_text())
    recs = [r for r in recs if r["title"]]
    added = added_records()
    X, W, dom, topics = topic_model(recs + added)
    Y = paper_map(X)
    W, dom_all, dom = W[:len(recs)], dom, dom[:len(recs)]

    # topic share by five-year period and archive, from the topic weights rather than the argmax
    Wn = W / (W.sum(1, keepdims=True) + 1e-12)
    periods = sorted({(r["year"] // 5) * 5 for r in recs})
    share = {}
    for arch in ["off-nime", "nime"]:
        rows = {}
        for p in periods:
            idx = [i for i, r in enumerate(recs) if r["archive"] == arch and (r["year"] // 5) * 5 == p]
            if len(idx) >= 10:
                rows[p] = {"n": len(idx), "share": (Wn[idx].mean(0)).round(4).tolist()}
        share[arch] = rows

    G = author_network(recs)
    H, comms, pos = layout_authors(G)

    cites = {}
    cpath = HERE / "data" / "citations.json"
    if cpath.exists():
        cites = json.loads(cpath.read_text())

    trl = {}
    tp = HERE / "data" / "trl.json"
    if tp.exists():
        trl = {m["id"]: m for m in json.loads(tp.read_text())}
    papers = []
    for i, r in enumerate(recs + added):
        papers.append({
            "id": r["id"], "t": r["title"], "y": r["year"], "a": r["names"], "ak": r["authors"],
            "ds": r["dataset"], "ch": r["channel"], "v": r["venue"], "ar": r["archive"],
            "tp": int(dom_all[i]), "x": round(float(Y[i, 0]), 4), "yy": round(float(Y[i, 1]), 4),
            "u": r["url"] or (f"https://doi.org/{r['doi']}" if r["doi"] else None),
            "trl": (trl.get(r["id"]) or {}).get("trl"), "arl": (trl.get(r["id"]) or {}).get("arl"),
        })
    authors = [{"k": a, "n": H.nodes[a]["name"], "p": H.nodes[a]["papers"], "o": H.nodes[a]["off"],
                "ni": H.nodes[a]["nime"], "f": H.nodes[a]["first"], "l": H.nodes[a]["last"],
                "c": comms[a], "x": round(float(pos[a][0]), 4), "y": round(float(pos[a][1]), 4)}
               for a in H.nodes]
    aedges = [[u, v, d["weight"]] for u, v, d in H.edges(data=True)]

    # statistics for the report
    both = [a for a, d in G.nodes(data=True) if d["off"] and d["nime"]]
    comp = max(nx.connected_components(G), key=len)
    by_ds = Counter(r["dataset"] for r in recs)
    ch_off = Counter(r["channel"] for r in recs if r["archive"] == "off-nime")
    years = Counter((r["archive"], r["year"]) for r in recs)
    bridges = sorted(both, key=lambda a: -(min(G.nodes[a]["off"], G.nodes[a]["nime"])))[:25]
    top_auth = sorted(G.nodes, key=lambda a: -G.nodes[a]["papers"])[:25]
    stats = {
        "records": len(recs),
        "by_dataset": dict(by_ds),
        "off_channels": dict(ch_off.most_common()),
        "year_range": {a: [min(y for (ar, y) in years if ar == a), max(y for (ar, y) in years if ar == a)]
                       for a in ["off-nime", "nime"]},
        "per_year": {a: {y: n for (ar, y), n in sorted(years.items()) if ar == a} for a in ["off-nime", "nime"]},
        "authors": G.number_of_nodes(),
        "authors_off": sum(1 for _, d in G.nodes(data=True) if d["off"]),
        "authors_nime": sum(1 for _, d in G.nodes(data=True) if d["nime"]),
        "authors_both": len(both),
        "coauthor_edges": G.number_of_edges(),
        "giant_component": len(comp),
        "single_paper_authors": sum(1 for _, d in G.nodes(data=True) if d["papers"] == 1),
        "mapped_authors": H.number_of_nodes(),
        "communities": len(set(comms.values())),
        "top_authors": [[G.nodes[a]["name"], G.nodes[a]["papers"], G.nodes[a]["off"], G.nodes[a]["nime"]] for a in top_auth],
        "bridges": [[G.nodes[a]["name"], G.nodes[a]["off"], G.nodes[a]["nime"], G.nodes[a]["first"]] for a in bridges],
        "topics": [dict(t, n_off=int(((dom == t["id"]) & np.array([r["archive"] == "off-nime" for r in recs])).sum()),
                        n_nime=int(((dom == t["id"]) & np.array([r["archive"] == "nime" for r in recs])).sum()))
                   for t in topics],
        "topic_share": share,
        "cross_archive_title_clashes": [[r["id"], r["dup_of"]] for r in recs
                                        if r["dup_of"] and r["archive"] != r["dup_of"].split(":")[0]],
    }
    (HERE / "data" / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=1))
    graph = {"papers": papers, "topics": topics, "authors": authors, "aedges": aedges,
             "share": share, "citations": cites}
    (HERE / "data" / "graph.json").write_text(json.dumps(graph, ensure_ascii=False, separators=(",", ":")))
    print(json.dumps({k: stats[k] for k in ["records", "authors", "authors_both", "giant_component",
                                             "mapped_authors", "communities"]}))
    for t in stats["topics"]:
        print(t["id"], t["n_off"], t["n_nime"], ", ".join(t["terms"]))


if __name__ == "__main__":
    main()
