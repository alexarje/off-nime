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
