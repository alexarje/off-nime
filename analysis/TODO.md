# TODO

## Now

- [ARJ] Vet the top of `output/candidates_cited.bib` and `output/candidates_journals.bib`; accepted
  entries go into a new `bibs/Cited/` dataset (recommended) or Extras. Anything under `bibs/`
  appears in the website's table.
- [ARJ] Decide whether to propose the analysis to IDMIL/off-nime as a pull request.
- [ARJ] Get a Semantic Scholar API key, then rerun `tools/fetch_s2.py` to finish the 1,059
  off-NIME title lookups (it resumes from the cache).

## Next

- [ME] Score the full ICMC archive at quod.lib.umich.edu with the local-candidates method.
- [ME] Cross-read the journal sweep against the forward-citation list; a paper on both is a
  strong candidate.

## Later

- [ME] Snowball: rerun the citation step over accepted candidates until few new works appear.
- [ME] Improve the reference parser's recall (53% against Semantic Scholar), mainly two-column
  interleaving from pdftotext; GROBID would be the stronger option.
