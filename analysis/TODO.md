# TODO

## Now

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
- [ME] Audio Mostly and MOCO (ACM, Crossref) are not on Zenodo; add them to the Crossref sweep.
- [ME] Theses (#5): resolve the theses on the forward list to repository records.
- [ME] Non-English sources (#4): SBCM, JIM and CIM proceedings.

## Later

- [ME] Improve the reference parser's recall (53% against Semantic Scholar); GROBID would help.
