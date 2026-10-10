"""Fill tools/report_template.md from the generated data and write REPORT.md.

Every number in the report comes from data/*.json through this script. An unresolved
{{placeholder}} stops the build.
"""
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(str(c).replace("|", "/") for c in r) + " |" for r in rows]
    return "\n".join(out)


def pct(a, b):
    return f"{100 * a / b:.1f}%"


def main():
    corpus = json.loads((HERE / "data" / "corpus.json").read_text())
    by_id = {r["id"]: r for r in corpus}
    st = json.loads((HERE / "data" / "stats.json").read_text())
    ci = json.loads((HERE / "data" / "citations.json").read_text())
    cs = ci["stats"]
    loc = json.loads((HERE / "data" / "local_candidates.json").read_text())
    pr = cs["parsed"]
    ds = st["by_dataset"]
    n_off = sum(v for k, v in ds.items() if not k.startswith("NIME"))
    n_nime_papers = ds["NIME papers"]
    s2_papers = sum(1 for rid in ci["cc"] if by_id[rid]["dataset"] == "NIME papers")
    eb = cs["edges_by_direction"]
    nime_out = eb.get("nime->nime", 0) + eb.get("nime->off-nime", 0)
    dups = [(r["id"], r["dup_of"]) for r in corpus
            if r["dup_of"] and r["archive"] == "off-nime" and r["dup_of"].startswith("off-nime")]
    cross = st["cross_archive_title_clashes"]
    citing_types = Counter()
    for line in (HERE / "output" / "candidates_citing.tsv").read_text().splitlines()[1:]:
        f = line.split("\t")
        citing_types["thesis or untyped" if not f[4] else "with a venue"] += 1
    T = st["topics"]
    name = lambda k: ", ".join(T[k]["terms"][:2])
    sh_off, sh_n = st["topic_share"]["off-nime"], st["topic_share"]["nime"]
    po, pn = sorted(sh_off, key=int), sorted(sh_n, key=int)
    first_off = sh_off[po[0]]["share"]
    top_off = sorted(range(len(T)), key=lambda k: -first_off[k])[:2]
    delta = [sh_n[pn[-1]]["share"][k] - sh_n[pn[0]]["share"][k] for k in range(len(T))]
    up, down = sorted(range(len(T)), key=lambda k: -delta[k])[:2], sorted(range(len(T)), key=lambda k: delta[k])[:2]
    f = lambda x: f"{100 * x:.1f}%"
    trend = (f"In the off-NIME archive, the earliest period ({po[0]}–{int(po[0]) + 4}) is dominated by "
             f"{name(top_off[0])} ({f(first_off[top_off[0]])}) and {name(top_off[1])} ({f(first_off[top_off[1]])}). "
             f"In NIME, from {pn[0]}–{int(pn[0]) + 4} to {pn[-1]}–{int(pn[-1]) + 4}, the largest rises are in "
             f"{name(up[0])} ({f(sh_n[pn[0]]['share'][up[0]])} to {f(sh_n[pn[-1]]['share'][up[0]])}) and "
             f"{name(up[1])} ({f(sh_n[pn[0]]['share'][up[1]])} to {f(sh_n[pn[-1]]['share'][up[1]])}), and the largest falls in "
             f"{name(down[0])} ({f(sh_n[pn[0]]['share'][down[0]])} to {f(sh_n[pn[-1]]['share'][down[0]])}) and "
             f"{name(down[1])} ({f(sh_n[pn[0]]['share'][down[1]])} to {f(sh_n[pn[-1]]['share'][down[1]])}).")
    jc = json.loads((HERE / "data" / "journal_candidates.json").read_text())
    from crossref import PROCEEDINGS
    journals = sorted(k for k in jc["by_source"] if k not in PROCEEDINGS)
    procs = list(PROCEEDINGS)
    resolved = json.loads((HERE / "data" / "cited_resolved.json").read_text())
    cr_ok = sum(1 for r in resolved if r.get("doi"))
    cst = json.loads((HERE / "data" / "cited_stats.json").read_text())
    import csv as _csv
    with open(HERE / "output" / "collection.csv") as fh:
        x_rows = sum(1 for _ in _csv.reader(fh)) - 1
    from build_cited import MIN_CITED, MIN_CITING
    sb = json.loads((HERE / "data" / "snowball.json").read_text())
    sb_rows = [l.split("\t") for l in (HERE / "output" / "candidates_snowball.tsv").read_text().splitlines()[1:]]
    th = json.loads((HERE / "data" / "theses_stats.json").read_text())
    ne = json.loads((HERE / "data" / "nonenglish_stats.json").read_text())
    jim = next(v for k, v in ne.items() if k.startswith("JIM"))
    sbcm = next(v for k, v in ne.items() if k.startswith("SBCM"))
    from theses import QUERIES
    tp = json.loads((HERE / "data" / "topic_stats.json").read_text())
    trs = json.loads((HERE / "data" / "trl_stats.json").read_text())
    per = trs["nime_papers_trl_band_by_period"]
    pk = sorted(per, key=int)
    share = lambda p, b: pct(per[p].get(b, 0), sum(per[p].values()))
    import books as _books
    bk = json.loads((HERE / "data" / "books.json").read_text())
    vols = json.loads((HERE / "data" / "sbcm_volumes.json").read_text())
    hist = re.findall(r"note = \{([^}]*)\}", (HERE.parent / "bibs" / "Historical" / "historical.bib").read_text())
    v = {
        "hi_n": len(hist), "hi_ok": sum("Found in" in n for n in hist), "hi_cited": sum("Cited by" in n for n in hist),
        "hi_pat": sum(n.startswith("Patent") for n in hist),
        "hi_refs": len((HERE / "output" / "candidates_historical.tsv").read_text().splitlines()) - 1,
        "vol_sbcm": sum(r["source"].startswith("SBCM") for r in vols), "vol_cim": sum(r["source"].startswith("CIM") for r in vols),
        "bk_q": len(_books.QUERIES), "bk_n": len(bk), "bk_adm": sum(b["admit"] for b in bk), "bk_p": _books.MIN_P,
        "tr_76": sum(1 for x in json.loads((HERE / "data" / "trl.json").read_text())
                     if x["dataset"] in ("NIME papers", "NIME alt") and x["trl"] == 6 and x["arl"] == 7),
        "tr_n": trs["checks"]["estimates"], "tr_title": trs["basis"].get("title", 0),
        "tr_art": trs["checks"]["artworks_arl_7_plus_pct"], "tr_bg": trs["checks"]["background_trl_1_3_pct"],
        "tr_noarl": trs["checks"]["nime_papers_without_arl_pct"],
        "tr_p0": pk[0], "tr_p0e": int(pk[0]) + 4, "tr_p1": pk[-2], "tr_p1e": int(pk[-2]) + 4,
        "tr_f0": share(pk[0], "fundamental"), "tr_f1": share(pk[-2], "fundamental"),
        "tr_a0": share(pk[0], "applied"), "tr_a1": share(pk[-2], "applied"),
        "tp_acc": tp["cv_accuracy"], "tp_auc": tp["cv_auc"], "c_bg": cst["background"],
        "rel_n": jc["related"],
        "ne_jim": jim["records"], "ne_jim_en": jim["with_english"], "ne_sbcm": sbcm["records"],
        "ne_sbcm_en": sbcm["with_english"],
        "th_q": len(QUERIES), "th_n": th["theses"], "th_ne": th["non_english"], "th_cal": th["calibration_theses"],
        "th_known": th["check"]["found_by_searches"], "th_off": th["check"]["off_nime_theses"],
        "th_adm": th["check"]["would_admit"], "th_pct": th["check"]["would_admit_pct"],
        "th_admitted": th["admitted"], "th_cites": th["admitted_by_cites"],
        "sb_refs": sb["with_reference_lists"], "sb_cited": sb["cited_works"], "sb_cands": len(sb_rows),
        "sb_min": sb["min_sources"],
        "sb_table": table(["Cited by Cited works", "Year", "First author", "Title"], [r[:4] for r in sb_rows[:15]]),
        "c_adm": cst["admitted"], "c_border": cst["borderline"], "c_by_cited": cst["admitted_by"]["cited_by"],
        "c_by_cites": cst["admitted_by"]["cites"], "c_by_sweep": cst["admitted_by"]["sweep"],
        "c_min_cited": MIN_CITED, "c_min_citing": MIN_CITING, "x_rows": x_rows,
        "j_procs": ", ".join(procs[:-1]) + " and " + procs[-1],
        "j_cands": jc["n_candidates"], "j_nsources": len(journals),
        "j_sources": ", ".join(journals[:-1]) + " and " + journals[-1],
        "j_items": jc["items"], "j_abs": jc["with_abstract"], "j_cur": jc["check"]["curated_cmj"],
        "j_med": jc["check"]["curated_median_percentile"], "j_cmj": jc["check"]["cmj_articles"],
        "j_q": jc["check"]["curated_share_in_top_quarter"],
        "j_by_source": ", ".join(f"{n} from {k}" for k, n in sorted(jc["candidates"].items(), key=lambda x: -x[1])),
        "j_table": table(["Score", "Source", "Year", "Title"],
                         [[f"{r['score']:.3f}", r["source"], r["year"], r["title"]] for r in jc["top"][:20]]),
        "cr_ok": cr_ok, "cr_pct": pct(cr_ok, len(resolved)),
        "trend": trend,
        "records": st["records"], "n_off": n_off, "n_nime": st["records"] - n_off, "n_nime_papers": n_nime_papers,
        "n_music": ds.get("NIME music", 0), "n_inst": ds.get("NIME installations", 0), "n_alt": ds.get("NIME alt", 0),
        "n_cmj": ds["CMJ"], "n_icmc": ds["ICMC"], "n_isidm": ds["ISIDM"], "n_extras": ds["Extras"],
        "off_y0": st["year_range"]["off-nime"][0], "off_y1": st["year_range"]["off-nime"][1],
        "nime_y0": st["year_range"]["nime"][0], "nime_y1": st["year_range"]["nime"][1],
        "channels_table": table(["Channel", "Entries"], list(st["off_channels"].items())),
        "authors": st["authors"], "authors_off": st["authors_off"], "authors_nime": st["authors_nime"],
        "authors_both": st["authors_both"], "authors_both_pct": pct(st["authors_both"], st["authors"]),
        "single": st["single_paper_authors"], "single_pct": pct(st["single_paper_authors"], st["authors"]),
        "giant": st["giant_component"], "giant_pct": pct(st["giant_component"], st["authors"]),
        "coedges": st["coauthor_edges"], "mapped": st["mapped_authors"], "communities": st["communities"],
        "bridges_table": table(["Author", "Off-NIME", "NIME", "First entry"], st["bridges"][:12]),
        "topics_table": table(["#", "Strongest terms", "Off-NIME", "NIME"],
                              [[t["id"] + 1, ", ".join(t["terms"][:6]), t["n_off"], t["n_nime"]] for t in st["topics"]]),
        "k_topics": len(st["topics"]),
        "texts": pr["texts"], "src_web": pr.get("source_web", 0), "src_ocr": pr.get("source_ocr", 0),
        "src_icmc": pr.get("source_icmc-local", 0), "with_entries": pr["with_entries"], "entries": pr["entries"],
        "no_head": pr.get("no_reference_heading", 0), "unkeyed": pr["unkeyed"], "unkeyed_pct": pct(pr["unkeyed"], pr["entries"]),
        "s2_found": cs["s2_found"], "s2_papers": s2_papers, "s2_papers_pct": pct(s2_papers, n_nime_papers),
        "s2_off": cs["s2_found_by_archive"].get("off-nime", 0), "s2_refs": cs["s2_with_references"],
        "edges": cs["internal_edges"], "e_nn": eb.get("nime->nime", 0), "e_no": eb.get("nime->off-nime", 0),
        "e_on": eb.get("off-nime->nime", 0), "e_oo": eb.get("off-nime->off-nime", 0),
        "e_no_pct": pct(eb.get("nime->off-nime", 0), nime_out),
        "later": cs["checks"]["parsed_to_later_paper"], "parsed_edges": cs["checks"]["parsed_edges"],
        "recall": cs["checks"]["recall_against_s2"], "recall_n": cs["checks"]["s2_edges_in_parsed_papers"],
        "most_cited_table": table(["Title", "Year", "Channel", "Cited by"], ci["most_cited_internal"][:15]),
        "n_cited": cs["cited_candidates"],
        "cited_table": table(["Cited by", "First author", "Year", "Title"],
                             [[c["n"], c["first"], c["year"] or "", c["title"]] for c in ci["cited"][:30]]),
        "n_citing": cs["citing_candidates"], "citing_untyped": citing_types["thesis or untyped"],
        "citing_table": table(["Cites", "Year", "Title", "Venue"],
                              [[c["n"], c["year"] or "", c["title"], c["venue"]] for c in ci["citing"][:20]]),
        "loc_texts": loc["texts"], "loc_icmc": loc["check"]["icmc_texts"], "loc_cur": loc["check"]["curated_found_locally"],
        "loc_med": loc["check"]["curated_median_percentile"], "loc_q": loc["check"]["curated_share_in_top_quarter"],
        "loc_above": sum(loc["candidates_above"].values()), "loc_above_icmc": loc["candidates_above"].get("ICMC", 0),
        "loc_table": table(["Score", "Set", "Year", "Title (guessed from the first page)"],
                           [[f"{r['score']:.3f}", r["set"], r["year"] or "", r["title"][:110]] for r in loc["top"][:15]]),
        "n_dups": len(dups),
        "dups_table": table(["Entry", "Same title as", "Title"], [[a, b, by_id[a]["title"]] for a, b in dups]),
        "n_cross": len(cross),
        "cross_table": table(["NIME entry", "Off-NIME entry", "Title"], [[a, b, by_id[a]["title"]] for a, b in cross]),
    }
    tpl = (HERE / "tools" / "report_template.md").read_text()
    out = re.sub(r"\{\{(\w+)\}\}", lambda m: str(v[m.group(1)]) if m.group(1) in v else m.group(0), tpl)
    left = re.findall(r"\{\{\w+\}\}", out)
    if left:
        raise SystemExit(f"unresolved placeholders: {left}")
    (HERE / "REPORT.md").write_text(out)
    print(f"REPORT.md written, {len(out.split())} words")


if __name__ == "__main__":
    main()
