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
