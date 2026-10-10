# TODO

## Now

- [ARJ] Label `output/trl_validation_sheet.tsv` (30 entries, your TRL and ARL) so agreement can be measured.
- [ARJ] Vet `bibs/Historical/historical.bib`: 13 works not found in a catalogue carry a note
  (among them the Sax patent and the Hornbostel–Sachs article); add or remove seeds in
  `tools/historical_seeds.txt`.
- [ARJ] Read Cited and Background and move what is on the wrong side (title classifier, 88% accurate).
- [ARJ] NIME bibliography: review `output/nime_missing_abstracts.tsv`; check the 2005 "NIME papers" that look
  like artworks and the front-matter entries among the 2019 music entries.

- [ARJ] Vet `bibs/Cited/cited.bib` (170 works admitted by rule) and remove what does not belong.
- [ARJ] Read the top of `output/borderline.tsv`: relevant reviews with short titles miss the
  closeness bar there.
- [ARJ] Check `output/offnime_dois_review.tsv` (near-miss DOI matches for off-NIME entries).
- [ARJ] Ask the ICMA or Michigan Publishing for a metadata export of the ICMC proceedings
  (recommended); the online archive and DBLP both block scripts with bot checks.
- [ARJ] Pushes to the fork do not trigger the Pages workflow; enabling workflows in the fork's
  Actions tab may fix it. Until then, deploy with `gh workflow run` (see HANDOVER.md).
- [ARJ] Get a Semantic Scholar API key to finish the remaining off-NIME title lookups.
- Pull request to IDMIL/off-nime: on hold at Alexander's request.

## Next

- [ME] Second snowball round (#2): fetch reference lists of the accepted snowball works.
- [ME] Theses (#5): more OpenAlex queries on later days (daily allowance); fix aggregator
  school names (Zenodo, NORA, ERA, LA Referencia) from the thesis records.
- [ARJ] Skim `bibs/Theses/theses.bib` (416, selected by rule) and `output/candidates_theses.tsv`.
- [ME] 366 non-English theses are listed in `output/candidates_theses_non_english.tsv`;
  Portuguese OCR for SBCM 1994–1998 needs the tesseract Portuguese pack.
- [ME] One TRL estimate is duplicated in the batches (off-nime:Chadabe1975); harmless, the
  merge keeps the last.

## Later

- [ME] Improve the reference parser's recall (53% against Semantic Scholar); GROBID would help.
