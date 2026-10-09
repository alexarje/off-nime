"""Assemble output/nime-atlas.html from the template and the generated data.

Every number in the page text is read from data/*.json here, never typed.
"""
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent


def e(s):
    return html.escape(str(s if s is not None else ""))


def main():
    g = json.loads((HERE / "data" / "graph.json").read_text())
    st = json.loads((HERE / "data" / "stats.json").read_text())
    ci = g.get("citations") or {}
    loc = json.loads((HERE / "data" / "local_candidates.json").read_text())
    cs = ci.get("stats", {})

    n_off = sum(1 for p in g["papers"] if p["ar"] == "off-nime")
    n_nime = len(g["papers"]) - n_off
    g["subtitle"] = (f"{len(g['papers'])} entries: {n_nime} from the NIME proceedings "
                     f"({st['year_range']['nime'][0]}–{st['year_range']['nime'][1]}) and {n_off} from the off-NIME archive "
                     f"({st['year_range']['off-nime'][0]}–{st['year_range']['off-nime'][1]}), with {st['authors']} authors "
                     f"and {cs.get('internal_edges', 0)} citation links between them.")
    g["cnodes"], g["cedges"] = ci.pop("cnodes", []), ci.pop("cedges", [])
    g["side"] = {
        "papers": f"<h2>Paper map</h2><p class='meta'>Each point is an entry, placed so that entries with similar "
                  f"wording in title, keywords and abstract lie close together (t-SNE on TF-IDF). Off-NIME entries "
                  f"have titles only, so their positions are less certain. The {len(g['topics'])} topics come from "
                  f"a non-negative matrix factorisation of the same text; choose one under Colour by.</p>"
                  f"<p class='meta'>Click an entry to see what it cites, and is cited by, within the two archives.</p>",
        "authors": f"<h2>Co-author network</h2><p class='meta'>The {st['mapped_authors']} authors with at least two "
                   f"entries, of {st['authors']} in all. {st['authors_both']} authors appear in both archives. "
                   f"Names are matched on surname and first initial, so a few different people share a node.</p>",
        "cites": f"<h2>Citation network</h2><p class='meta'>{cs.get('cnodes', 0)} entries joined by "
                 f"{cs.get('cedges', 0)} citation links, from reference lists parsed out of the paper texts and from "
                 f"Semantic Scholar. Green nodes are works cited by at least eight archive papers that are in neither "
                 f"archive.</p>",
    }

    topics = "".join(f"<tr><td>{t['id'] + 1}</td><td>{e(', '.join(t['terms']))}</td><td class='n'>{t['n_off']}</td>"
                     f"<td class='n'>{t['n_nime']}</td></tr>" for t in st["topics"])
    bridges = "".join(f"<tr><td>{e(b[0])}</td><td class='n'>{b[1]}</td><td class='n'>{b[2]}</td><td class='n'>{b[3]}</td></tr>"
                      for b in st["bridges"][:20])
    internal = "".join(f"<tr><td>{e(t)}</td><td class='n'>{y}</td><td>{e(c)}</td><td class='n'>{n}</td></tr>"
                       for t, y, c, n in ci.get("most_cited_internal", [])[:25])
    g["trend_html"] = f"""
<section><h3>Entries per year</h3><p>Off-NIME entries end around 2012; the NIME proceedings start in 2001.</p>
<div class="legend" style="padding:0 0 6px"><span><i style="background:var(--s2)"></i>Off-NIME archive</span><span><i style="background:var(--s1)"></i>NIME papers</span><span><i style="background:var(--s3)"></i>NIME music and installations</span></div>
<div class="chartbox">{{{{years}}}}</div></section>
<section><h3>Topic share by five-year period, off-NIME archive</h3><p>Mean topic weight of the entries in each period; darker is a larger share. Periods with fewer than 10 entries are left out.</p><div class="chartbox">{{{{heat_off}}}}</div></section>
<section><h3>Topic share by five-year period, NIME proceedings</h3><div class="chartbox">{{{{heat_nime}}}}</div></section>
<section><h3>Topics</h3><p>Entries counted by their strongest topic.</p><div class="chartbox"><table><tr><th>#</th><th>Terms</th><th>Off-NIME</th><th>NIME</th></tr>{topics}</table></div></section>
<section><h3>Authors in both archives</h3><p>{st['authors_both']} of {st['authors']} authors have entries in both archives. These are the ones with the most entries in the smaller of the two.</p><div class="chartbox"><table><tr><th>Author</th><th>Off-NIME</th><th>NIME</th><th>First entry</th></tr>{bridges}</table></div></section>
<section><h3>Most cited entries within the archives</h3><div class="chartbox"><table><tr><th>Title</th><th>Year</th><th>Channel</th><th>Cited by</th></tr>{internal}</table></div></section>
"""
    cited = "".join(f"<tr><td class='n'>{c['n']}</td><td>{e(c['first'])}</td><td class='n'>{e(c['year'])}</td><td>{e(c['title'])}</td>"
                    f"<td class='n'>{c['n_off']}</td><td class='n'>{c['n_nime']}</td></tr>" for c in ci.get("cited", [])[:100])
    citing = "".join(f"<tr><td class='n'>{c['n']}</td><td class='n'>{e(c['year'])}</td><td>{e(c['title'])}</td><td>{e(c['venue'])}</td></tr>"
                     for c in ci.get("citing", [])[:100])
    local = "".join(f"<tr><td class='n'>{r['score']:.3f}</td><td>{e(r['set'])}</td><td class='n'>{e(r['year'])}</td><td>{e(r['title'][:140])}</td>"
                    f"<td>{e(r['nearest'][0][:90])}</td></tr>" for r in loc["top"][:100])
    chk = loc["check"]
    g["missing_html"] = f"""
<section><h3>Cited by the archives, but in neither</h3><p>Works cited by at least five archive papers, from {cs.get('parsed', {}).get('entries', 0)} parsed references. Titles are parsed from reference strings and may be imperfect. The full list is in <code>candidates_cited.tsv</code>.</p>
<div class="chartbox"><table><tr><th>Cited by</th><th>First author</th><th>Year</th><th>Title</th><th>Off-NIME citers</th><th>NIME citers</th></tr>{cited}</table></div></section>
<section><h3>Outside NIME, citing many archive entries</h3><p>Journal articles, chapters and conference papers outside NIME that cite at least five archive entries (Semantic Scholar forward citations). These are candidates for extending off-NIME past 2012.</p>
<div class="chartbox"><table><tr><th>Cites</th><th>Year</th><th>Title</th><th>Venue</th></tr>{citing}</table></div></section>
<section><h3>NIME-related papers in the local conference archive</h3><p>Papers in the local ICMC, DAFx, SMC, ISMIR, ICMPC and workshop folders that are in neither archive, ranked by similarity to their ten nearest archive entries. As a check, the {chk['curated_found_locally']} curated off-NIME ICMC papers found locally rank at a median percentile of {chk['curated_median_percentile']} among {chk['icmc_texts']} ICMC texts, and {chk['curated_share_in_top_quarter']}% of them fall in the top quarter. Titles are guessed from the first page.</p>
<div class="chartbox"><table><tr><th>Score</th><th>Set</th><th>Year</th><th>Title (guessed)</th><th>Nearest archive entry</th></tr>{local}</table></div></section>
"""
    data = json.dumps(g, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    tpl = (HERE / "tools" / "viewer_template.html").read_text()
    out = HERE / "output" / "nime-atlas.html"
    out.write_text(tpl.replace("/*DATA*/null", data))
    print(f"{out} {out.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
