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

- [ME] Sweep the Zenodo communities of open music-technology conferences (ICLC, WAC, SMC,
  Audio Mostly) through the Zenodo API, scored like the journal sweep.
- [ME] Abstracts for off-NIME entries from Crossref and Semantic Scholar, to sharpen the topic map.
- [ME] Snowball: fetch the reference lists of the Cited entries from Crossref and count what they
  cite that neither archive holds.

## Later

- [ME] Improve the reference parser's recall (53% against Semantic Scholar); GROBID would help.
- [ME] Non-English sources: SBCM (Brazil), JIM (France) and CIM (Italy) proceedings.
