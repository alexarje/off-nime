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
