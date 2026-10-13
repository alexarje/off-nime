# Worklog

## 2026-10-09

Built the analysis in `analysis/`. Parsed both archives into one corpus of 3,940 entries.
Semantic Scholar found 2,029 NIME entries by DOI but returns their reference lists elided, so
reference lists were parsed from the paper texts instead: 2,304 PDFs from nime.org, OCR copies
from the Seagate archive for early papers with broken fonts, and 21 local ICMC PDFs for curated
off-NIME papers. The Semantic Scholar title lookups for off-NIME were stopped after the API
throttled to one request per two minutes; the cache resumes.

Parser decisions: cutting entries at blank lines lowered internal links from 5,918 to 4,626, since
pdftotext puts blank lines inside references, so it was reverted in favour of truncating long
entries to 400 characters, which raised them to 6,062. Checks: no parsed link points more than a
year forward (an injected wrong link does flag); recall against Semantic Scholar's own lists is
53%.

Layouts: ForceAtlas2 with strong gravity and LinLog gave a uniform disc; default ForceAtlas2 put
linked authors closest (mean edge length 0.03 of mean node distance, against 0.11 for spring), so
it is used, with small co-author components packed below the main one.

The local-archive score was checked against the curated off-NIME ICMC papers: median 83rd
percentile among 685 ICMC texts, 66% in the top quarter.

## 2026-10-09, later

Committed the analysis (ef676f1). Of the nine off-NIME title clashes, four were true duplicates
(the 1980 Buxton conducting system twice in CMJ; three ISIDM entries repeating CMJ or Extras
entries) and were removed, keeping the richer entry; the other five are distinct publications.
This corrects the earlier note that eight looked like duplicates. Fixed the author
"Czeiszpergerm Michael" in CMJ/1992.bib.

Corrected the local-archive check: a curated paper was compared against its own archive entry,
which inflated its score. With that entry left out, the curated ICMC papers rank at a median
74th percentile (was 83rd) and 50% fall in the top quarter (was 66%), still well above chance.
The journal sweep was built leave-one-out from the start.

Crossref allows one request per second without a token; the resolver runs at that rate.
Added the Crossref resolver and journal sweep, and published the atlas at /atlas/ and the
report at /analysis/REPORT.html through the fork's GitHub Pages workflow.

Journal sweep scoring: closeness alone ranked CMJ record and product reviews first ("Computer
Music Currents 3"), since short titles share words with everything; a page-count filter did not
help, as Crossref lacks pages for most of them. Contrast against the sweep itself fixed the top
of the list (check: median 76th percentile, 53% in the top quarter) but let general HCI articles
through, and a curated lower-quartile threshold admitted 4,168 items. The final rule needs the
curated median contrast and the curated lower-quartile closeness: 459 candidates. The Crossref
resolver's second pass, with the raw reference string, raised DOIs from 174 to 206 of 352.

## 2026-10-09, evening

Built `bibs/Cited/cited.bib` with `tools/build_cited.py`: works with a DOI, in neither archive,
at least as close to the archives as the curated CMJ lower quartile, and either cited by five or
more archive papers, citing ten or more archive entries, or found in the journal sweep as well.
The site shows them under a Cited tab via a `collection` field. `build_corpus.py` skips
`bibs/Cited/`, so the curated archives remain the reference.

The Crossref resolver matched "The Technology of Computer Music" (Mathews 1969) to a 1971 review
with the same title; it now requires the first author to match, which removed 18 matches (206 to
188 of 352).

Added DOIs to 224 off-NIME entries with `tools/offnime_dois.py --apply` (275 of 916 now have one).
The first run converted the CRLF line endings of `ISIDM/theses-tech-reports.bib` and indented
lines in unindented files; it was reverted, and the script now keeps each file's endings and
indentation. A technical report took its journal version's DOI, so the script now also requires
the same kind of publication (242 to 224 accepted). Check: all 39 entries with a JSTOR URL agree
with their DOI (35 the JSTOR DOI, 4 the MIT Press DOI for the same CMJ article).

With the new DOIs, Semantic Scholar found 210 more off-NIME entries in three batch calls, and
their forward citations raised links within off-NIME from 68 to 335. The quod.lib.umich.edu ICMC
archive and dblp.org both answer scripts with bot challenges, so the full ICMC sweep is blocked.

The atlas lists search matches as keyboard-reachable buttons in the side panel, and Escape clears
a selection. Exports: `output/collection.csv` and CSL-JSON `output/collection.json`.

## 2026-10-09, night

Opened issues #1–#10 on alexarje/off-nime (issues were off on the fork and were switched on).
Closed #8 (suggest-an-entry form) and #10 (the table becomes cards under 700 px wide); the
dataset radio buttons shared one id, so each label now has its own. The front page no longer
calls Cited entries vetted.

#9: abstracts found for 67 of 916 off-NIME entries (Semantic Scholar 16, Crossref the rest); most
older CMJ and JSTOR records have none. They are merged into the corpus from data/abstracts.json.

#1: Zenodo communities iclc, livecode, wac, smc, nordicsmc, cmmr2023, cmmr2025 and tenor gave
2,584 publication records. The contrast score first used the whole sweep as its background, so
the 1,725 SMC records pulled each other's scores down (5 SMC candidates); the background is now
the journal sweep alone (137 SMC candidates; CMJ check median 75th percentile, 51% in the top
quarter).

#2: one snowball round from the Cited works' Crossref reference lists. Proceedings names pooled
unrelated papers under one key and journal versions of archive papers slipped through; both are
now excluded, and works counted by DOI and by title are merged. 120 candidates.

## 2026-10-09, late night: theses (#5)

`tools/theses.py`: 36 queries to OpenAlex (type dissertation; searches cost $0.001 against a
$0.10 daily allowance, so two pages of 200 per query) and DataCite, plus a DataCite title lookup
of the untyped forward-list works (37 resolved to theses): 6,122 distinct theses.

French abstracts scored high against the few French titles in the archives, since French
function words are not English stop words; a cancer thesis from Montréal scored 0.33. Theses are
now scored on their English abstract where a repository gives several, and non-English theses
(366) go to a separate list for #4. Journal-sweep thresholds admitted 3 of 9 known off-NIME
theses, so thresholds are calibrated on the 35 English theses that cite the archives. Contrast at
their lower quartile admitted 851, of which about a quarter looked off topic in my reading of 80
titles; contrast at the median admits 416 (my reading: roughly one in eight off topic, mostly
acoustics and dance studies), and 6 of the 9 known off-NIME theses. The school comes from the
author's institution in OpenAlex, or from the parenthesis in a repository name; aggregators
(Zenodo, NORA, ERA, LA Referencia) remain.

## 2026-10-09, non-English proceedings (#4)

`tools/nonenglish.py` fetches JIM from HAL (collection JIM, 823 records) and SBCM from SBC OpenLib
over OAI-PMH (131 records, recent editions only), and scores the ones with English text with the
journal sweep (JIM 28 candidates, SBCM 10; the CMJ check is unchanged). Older SBCM proceedings
(1994–2019) are whole-volume PDFs on compmus.ime.usp.br/sbcm; CIM is not yet covered.

Added Audio Mostly, MOCO, DIS and Creativity and Cognition to the Crossref proceedings queries
(888 records). The contrast background had been all of `journals.json`, so new proceedings would
have shifted every score; it is now the seven journals only (CMJ check: median 75th percentile,
51% in the top quarter). Sweep candidates 758; Cited 184; snowball 124.

## 2026-10-10

Theses (#5): 39 more OpenAlex queries and deeper pages for the capped ones, with a guard that
stops at the daily allowance: 13,257 distinct theses. The scoring step was killed by the 3 GB cap
(OOM, as intended) and reran at 8 GB. With closeness at the calibration lower quartile, 578 were
admitted, of which about half of the new ones looked off topic in a sample of 30 (the broader
queries bring in music education, performance practice and general computing); with closeness at
the median, 297 are admitted, about 5 of 30 off topic, and the check is unchanged (6 of 9).

SBCM (#4): volumes 2007, 2009, 2013, 2015 and 2017 split into 140 papers by their Abstract
headings (`tools/sbcm_volumes.py`); 1994–1998 are scans without text and need OCR. The PDFs were
not kept; the texts are in data/sbcm_text/.

On request, added ISMIR (2,593 papers from the ismir/conference-archive JSON), DAFx (1,706 from
the dafx.de archive, with abstracts), CMMR (401 Springer chapters in Crossref, by volume title;
2023 and 2025 from Zenodo); SMC was already complete on Zenodo (2004–2025). CHI and the other ACM
proceedings are now searched with 12 terms and cursor paging (CHI 511 to 1,262 papers; Audio
Mostly 2,607). The title filter matched "sing" inside "using"; it now matches whole words.
Sweep candidates 1,037; Cited 192; snowball 129.

Related dataset: the 1,037 sweep candidates read as roughly two in three on topic in a sample of
40; a strict tier (contrast at the curated CMJ upper quartile, closeness at the median) read as
roughly six in seven, 108 papers after removing what Cited and Theses hold.

Books: Sound Actions and A NIME Reader were on the backward list (16 and 8 citers) but not
resolved, because Crossref keeps subtitles apart and edited volumes have editors, not authors.
A book pass in the resolver fixes both (199 of 355 resolved).

Cited and Background, at Alexander's request to separate works about NIME topics from works
that are much cited but not about NIME. The similarity test put Sound Actions, Ocarina and Bela in
Background, because most cited works have only a title and a title alone scores low. A title
classifier (`tools/topic.py`: archive titles against TOCHI, Personal and Ubiquitous Computing,
Contemporary Music Review and ISMIR titles; 87.6% cross-validated accuracy, AUC 0.94) now decides:
Cited 318, Background 55. Visible errors: a gender-in-NIME paper in Background, The Physics of
Musical Instruments in Cited.

## 2026-10-10, readiness levels and abstracts

Abstracts: written into the rule-selected bibs from their sources (Theses 299 of 307, Cited
106 of 318, Background 21 of 55, Related 13 of 108), and found for more entries through OpenAlex by
DOI (385), local ICMC PDFs (19) and the NIME paper texts (59, uneven: some are body text, so they
stay in output/nime_missing_abstracts.tsv for review). 238 curated off-NIME entries now carry an
abstract field (`tools/write_abstracts.py`; the diff is two lines added and one removed per entry).

TRL and ARL: Alexander chose to estimate all entries in this session without a pilot. Rubric in
`tools/trl_rubric.md` (standard TRL adapted to music technology; ARL from his draft post "From TRL
to ARL"). 20 Sonnet agents classified 4,724 entries in batches of 237. Several agents shared
helper-script names in the scratch folder and overwrote each other's files; each reran in a
private folder, and every output file was checked to match its input id by id. Checks: artworks
at ARL 7+ 96.8%, Background at TRL 1–3 80.0%, NIME papers without ARL 52.0%. Agents reported data
problems in the NIME bibliography: "NIME papers" entries without abstracts that look like
artworks ("Thresholds", "Sensity", 2005), and front matter among the music entries ("NIME 2019
Concert Program", "Program Committee Members").

Books: a Crossref book search (34 queries) judged by the title classifier alone admitted
accounting manuals, flooring standards and dental guides, since the classifier only knows
music-technology and HCI titles. Requiring music or sound vocabulary still admitted mostly
musicology and Grove and ANB encyclopedia entries; requiring technology vocabulary as well, and
dropping reference-book records and standards, leaves 93 books (about four in five on topic in my
reading), added to Related as book entries and classified for TRL and ARL in a 21st batch.
Thesis schools: aggregator names (Zenodo, NORA, HAL, LA Referencia) are replaced by the
university where the repository domain names one, otherwise left empty (67 empty).
SBCM 1994–1998: OCR running (tesseract, English only; the Portuguese pack is not installed).

TRL against ARL: a heatmap in the atlas's Trends tab (selectable by group) and a static SVG in the
report (`tools/readiness_figure.py`), at Alexander's request. CIM: all 21 volumes on
cim.lim.di.unimi.it (1979–2024) have text layers; the splitter now reads Sommario and Riassunto
headings. History: the reference parser only accepts years from 1940, so pre-1940 works
(Hornbostel and Sachs 1914, Russolo 1913, Helmholtz 1863) are invisible to the citation counts.

SBCM 1994–1998 read by OCR (572 pages); CIM 1979–2024 (21 volumes, all with text layers). The
splitter gives 717 papers (SBCM 325, CIM 392); letter-spaced running headers were getting into
titles and are now dropped. Italian abstracts passed the sweep score as French ones had passed
the thesis score; the sweep now requires English text where there is an abstract and for the
non-English venues. A first version of that filter dropped title-only English CMJ items (1,623 to
1,359 in the check); the test now applies to abstracts only, and the check is back to 1,623.
The TRL merge now covers only entries currently in the collection (4,811).

Historical precursors, at Alexander's go-ahead: `tools/historical.py` builds
`bibs/Historical/historical.bib` from `tools/historical_seeds.txt` (60 works before 1957: 29 from
the reference lists, the rest chosen by hand). Checks: Crossref for articles, Open Library for
books, Google Patents for patents; 47 pass. Old Google Patents records carry only the inventor's
name in lower case as title, so the seed title is kept there. Citation counts go by first author
and year, which first gave Dudley's 1939 vocoder article and patent the count of his synthetic
speaker paper; hand-chosen works now get no count when a work from the reference lists shares
author and year. TRL and ARL for the 60 came from a 22nd agent batch (7 low confidence). New site
tab, report section and heatmap group.

Reference lists from OpenAlex for 452 entries with a DOI and no text (360 had lists, 7,187
references), and a chapter rule for edited books: A NIME Reader went from 8 to 29 citing archive
papers. The atlas paper panel lists each paper's other references. Portuguese OCR of SBCM
1994–1998 with the system language packs: the splitter finds the same 222 SBCM papers as the
English-only run. Crossref resolution of cited works now requires the cited first author to be
the record's first author; JSTOR book reviews (of Musicking, Flow, Mindstorms, Lakoff and
Johnson) had been taken for the books. The Zotero check at first counted every short title as in
the collection (both sides had no title key); fixed, the library has 2,358 of 9,251 items in the
collection. The top tier (probability at least 0.9) became the Zotero dataset at Alexander's
request; the classifier scored a Norwegian article on stave churches at 0.93, so titles not in
English are left out. TRL batches 23 and 24 cover the new entries.

The atlas paper map now places the six datasets built around the archives (1,522 works), with
topics fitted on the archives only, as Alexander asked: the curated off-NIME archives end in
2011–2013, so later off-NIME work was missing from the map. A topic labelled "icon · doi ·
journal" turned out to be MIT Press page menus that OpenAlex holds as abstracts for 17 CMJ and
ISIDM entries, written into the bibs in c36defd; those abstracts are removed and the filler now
rejects such pages. A second snowball round from the 95 round-1 candidates on NIME topics finds
only 5 new works cited by three or more of them. 26 more thesis queries reached only DataCite,
since the day's OpenAlex allowance was spent; the theses build also needs more than 3G of memory
now. GROBID (#7) is being set up by a separate agent.


Zotero tags: a NIME tag or folder now admits an item at any probability (4 more works), and topical tags go into the bib as keywords (70 works), which the paper map reads. Matching short titles on the whole title and year found 63 more library items already in the collection, most of them NIME papers with one- or two-word titles. Of the NIME-tagged items, only Fliperama (NIME 2020) is missing from the NIME bibliography, and it is absent on purpose: the paper was retracted from the proceedings (nime.org serves a retraction notice; Zenodo 10.5281/zenodo.15308623 is marked RETRACTED).

GROBID (#7), installed by a separate agent: recall against Semantic Scholar went from 53.0% to
85.5% on the same papers, and parsed links into the archives from about 6,000 to 10,300. The
Crossref resolution of cited works then had 742 clusters to match instead of 461; Cited grew to
443 and Background to 111, and A NIME Reader is cited by 36 archive papers. Alexander exported the
NIME 2021 proceedings from PubPub (the 2022 papers export failed); GROBID read the 81 papers that
match the bibliography, and `tools/pubpub_package.py` packs the export for Zenodo. The export of
the collection now says, per entry, whether a full text, an abstract and a reference list exist.


Theses come from four more sources: OpenAlex dissertations that cite archive works, OpenAlex
dissertations by authors with at least two archive works, theses.fr, and the theses in
Alexander's Zotero library. The first run stopped on OpenAlex authors without an id. With the
citing dissertations in the calibration set, both thresholds fell (contrast below zero) and
1,611 theses were admitted, many of them general HCI, web and materials work, so calibration is
back on the forward list. Contrast still did not separate the theses well, so every admitted
thesis also needs a NIME-topic probability of at least 0.7 from the title classifier; a reading
of samples found few off-topic titles above it and mostly off-topic ones below. Two French
titles that pass are about plant ecology and medicine and are excluded by hand. The Zotero thesis
list had been compared with the whole collection, Theses included, so a second run lost the Zotero
theses it had admitted; the comparison now leaves Theses out. That gives 409 theses, against 307
before, with the off-NIME check unchanged at 6 of 9. The run needs about 10 GB; it was killed at
6 GB. An agent estimated TRL and ARL for the 213 new theses (batch 28).
The TRL validation sheet is no longer rewritten once any row carries a label.

Thesis school names that were repositories now name the university where the repository belongs
to one (VTechWorks, KiltHub, TU/e Research Portal and others, and Bath Spa and Eindhoven by DOI
prefix), and are left empty for national aggregators (INIST, the Czech grey-literature
repository, RCAAP, Library and Archives Canada). The aggregator pattern matched "base" and "core"
inside words, which would have emptied a name such as University of Basel. The abstracts that
`fill_abstracts.py` finds by DOI for Cited, Background and Related were never written into those
bib files; the builders now use them, and abstract coverage rose from 31% to 65% in Cited, 31% to
46% in Background and 4% to 27% in Related (most of the rest of Related is books). Rerunning
`score_journals.py` on the current corpus moved 21 papers out of Related and 31 in near the
threshold. `books.py` excluded every title already in Related, which holds its own output, so a
rerun admitted 1 book instead of 92; Related is now left out of that comparison. Crossref runs
the place into some publisher names ("Oxford University PressNew York"); these are trimmed.

Theses whose abstract is not in English can now be admitted on an English title alone, at a
NIME-topic probability of at least 0.9 (the Zotero bar), when the title has an English word and
no Romance, Germanic or Scandinavian function words or accents; without that check the classifier
scored Brazilian music-education titles high. A sample of 40 read as nearly all on topic, but
the agent that estimated their TRL found 12 of 109 clearly off topic (robotics, animation,
multimedia, law). A title judged alone must now also name music, sound or an instrument, as in
`books.py`, and five more theses I read as off topic are excluded by hand. That admits 93 more
theses, most of them French, for 497 in all. In `bibs/ICMC/1975.bib` two papers shared the key
`Chadabe1975`; the Rosenboom paper is now `Rosenboom1975`, and its TRL estimate moved with it.
The key fix for the Rosenboom 1975 paper went to IDMIL as its own pull request (IDMIL/off-nime#7), from a branch on IDMIL's main.
Two more small pull requests went to IDMIL from branches on its main: #8 removes four duplicate entries and fixes an author name (the fork's commit 6b9b034), and #9 writes six abbreviated ISIDM page ranges in full ("113--30" read as running backwards) and trims a title; the fork has the same edits.

The ARL threshold moved, at Alexander's suggestion: a concert or installation at an academic
conference is a peer setting, ARL 5–6, and ARL 7 needs a stated presentation in a professional
artistic context (festival, concert series, gallery, release). The rubric, Table 1 of the paper and
the checks say so. Agents re-estimated the 1,061 entries that had been rated ARL 7 or higher, in
revision batches (`rev_in_NN`, `rev_out_NN`) that `merge_trl.py` applies after the originals.
They found that the earlier reasons for many entries described other works: batches `out_08` and
`out_14` had their judgements attached to the wrong ids, scrambled rather than shifted, from about
line 40 on. Those 474 entries were estimated again from scratch, and `merge_trl.py` now flags a
batch where more than 25% of the reasons share no word with their entry (about 4% elsewhere). The
input id of the Rosenboom paper is renamed too. NIME concerts and installations now sit at ARL 6
(91.4%), and 2.5% reach ARL 7 or more.

The TRL is aligned at the same 6/7 boundary as the ARL: the rubric now says that a device shown
only at a conference is TRL 6 (5 when the text calls it a study or work in progress), that TRL 7
needs stated use outside that setting, and that a concert or installation is rated on the setup
built for it, not on established tools such as Max or Kyma. `tools/trl_revise.py` wrote five
TRL-only revision batches (`rev_in_07` to `rev_in_11`, 366 entries): NIME music and installations
at TRL 5 or 7, and NIME papers at TRL 7. `merge_trl.py` applies a TRL-only revision without
touching the ARL, keeps its reason in a new `trl_reason` column, includes it in the mismatch
check, and adds the check `artworks_trl_6_pct`. Concerts and installations at TRL 6 went from
49.6% to 85.1%, and NIME papers at TRL 7 from 123 to 84. The report, Table 1 and the checks and
results in the paper say so; the paper compiles to 6 pages.

A literature search found precedents for estimating the TRL from text and by hand, and
adaptations of the scale; no arts readiness scale. Six are cited in the paper: Héder and Bruno and
colleagues under readiness scales, Britt and colleagues and Quilodrán-Casas and colleagues in the
method, Berkhout and colleagues in the results, and Quilodrán-Casas and Salvador-Carulla and
colleagues in the limitations. The paper still compiles to 6 pages.

Agents read every entry of the rule-selected datasets (Theses, Cited, Background, Zotero,
Related, Historical) and flagged 428 with a reason: removals (off topic, not a publication, a
duplicate), moves between Cited and Background, metadata fixes, and close calls. Each row was
checked against its entry, since one agent assigned verdicts by position; none was misplaced. The
rows are combined in `data/vetting_sheet.tsv` with a recommended action, for Alexander to confirm.
`tools/hand.py` (in `run.sh` after the last builder) will apply the decisions from `tools/hand.tsv`,
which is empty until then; with no decisions it leaves the bibs byte for byte as they are.
`merge_trl.py` carries an estimate over when an entry moves between Cited and Background.

The vetting recommendations are applied through `tools/hand.tsv`: 131 removals, 54 moves between
Cited and Background, and 57 corrections (chapters entered as books, titles holding author names,
names BibTeX misreads, wrong thesis schools, a mis-resolved Höök record, abstracts that belonged
elsewhere). Thesis years in Cited now come from the defence date Crossref records as "approved",
since theses.fr DOIs were registered in 2026; ten keys changed with the year and were estimated
again. `hand.py` gained a "type" action; `trl_batch.py` and `merge_trl.py` carry an estimate over
when an entry moves between Cited and Background.

At Alexander's point that the scales can be far apart (a fragile prototype on stage, a commercial
instrument in an experimental piece), the rubric says the two are judged independently and the
TRL rates what the text says about the technology, not where it was shown. The TRL of all 1,716
NIME papers and concert or installation entries with an ARL was estimated again by agents that
did not see the ARL or any earlier estimate (`trl_revise.py --blind`, `rev_in_12` to `rev_in_26`).
Papers with the same TRL and ARL fell from about 52% to 41.4%. Concert entries still agree at
78.9%, mostly at 6 and 6, since programme notes say little about the technology. The check that
expected concert entries at TRL 6 is dropped, as it contradicts independence; the agreement and the
number of gaps of three levels or more are reported instead, in the report and the paper.

`thesis:baez2016electroacoustica` is removed by hand. Its OpenAlex title was a keyword list; the
repository record names it "Di-ha para electroacústica", an undergraduate degree project for the
Licenciatura en música at Universidad Industrial de Santander, and Theses holds doctoral theses only.
Theses now has 429 entries and the paper's corpus 5,151.

The entries-per-year chart in the atlas ran from 1619 at one bar per year, about 4,500 pixels wide
with almost nothing before 1970. It now gives one bar per year from 1970, gathers the earlier
entries into one bar at the left, and scales to the width of the page.

Twenty-two NIME texts were font-shifted by pdftotext (letters as punctuation, mostly 2006 and 2008),
found by a letter share under 0.75. `tools/ocr_texts.py` downloads their PDFs again and reads them
with tesseract at 300 dpi; 21 now read cleanly (letter share 0.92–0.97), the garbled versions kept
in `data/text_garbled/`. `nime2020_117` returns 404 and is left.

The 404 for `nime2020_117` was transient: the PDF downloads again and `tools/ocr_texts.py` has read
it (letter share 0.96), so all 22 font-shifted texts are now OCR text. The Zenodo copies of the 22
are font-shifted too; posted as NIME-conference/NIME-bibliography#127.

Worked through the open NIME-bibliography issues. Pull requests: #129 points every nime.org link
at https://nime.org (#93); #130 stores nime2021.bib in articleno order (#117); #131 corrects three
wrong DOIs, two wrong links, the duplicate nime2012_Smith_b and four review placeholders in
abstracts, found by comparing every DOI's registered title with its entry; #132 adds 84 abstracts
cut from the PDFs or the OCR texts (#69); #133 adds the printed 2012 page ranges from the full
proceedings PDF at umich (#55). #131 and #132 build on #129, #133 on #131. Issue #128 lists what
needs a decision: the `nime20202_` keys of the 2022 installations, three Zenodo records with an
earlier or anonymised title, five with review placeholders, and the truncated full 2012 proceedings
on nime.org. The Seagate drive dropped off USB during a scan and was left unmounted; the kernel
asks for an fsck of its exFAT volume.

## 2026-10-13: the bibliography pull requests merged

Stefano Fasciani merged #129 to #133. #131, #132 and #133 were stacked and went into their base
branches after #129 had reached master, so their changes were not on master. #134 merges both base
branches into master (no conflicts; pytest and `nime_bib validate`, also with `--release`, pass).
`tools/nime_dois.py` lists every NIME DOI with its OpenAlex work and source: OpenAlex finds 2,829
of 2,830, many under the Zenodo concept DOI, which a batched `doi:` filter misses.
`tools/zenodo_fix.py` holds the seven Zenodo fixes of #128, waiting for edit access.

#134 is merged, so the fixes of #129 to #133 are all on master.

Stefano Fasciani fixed the #128 Zenodo records by hand and closed the issue; `tools/zenodo_fix.py`
now finds nothing to change.
