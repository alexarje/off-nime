# TODO

## Now

- [ARJ] Decide where cited works go: a separate `bibs/Cited/` dataset (recommended) or Extras.
- [ARJ] Decide whether to propose a joined NIME + off-NIME export to IDMIL as a pull request.
- [ARJ] Get a Semantic Scholar API key, then rerun `tools/fetch_s2.py` to finish the 1,059
  off-NIME title lookups (it resumes from the cache).
- [ARJ] Decide whether to publish the atlas as a private claude.ai artifact or on GitHub Pages.

## Next

- [ME] Curate the top of `candidates_cited.tsv` into BibTeX with DOIs (Crossref lookup by title).
- [ME] Resolve the nine off-NIME title clashes listed in REPORT.md (eight look like true duplicates).
- [ME] Score the full ICMC archive at quod.lib.umich.edu with `local_candidates.py`.
- [ME] Sweep CMJ, Organised Sound, JNMR, TOCHI, TEI and CHI by ISSN through Crossref and score.

## Later

- [ME] Snowball: rerun the citation step over accepted candidates until few new works appear.
- [ME] Improve the reference parser's recall (53% against Semantic Scholar), mainly two-column
  interleaving from pdftotext; GROBID would be the stronger option.
