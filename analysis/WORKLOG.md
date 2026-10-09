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
