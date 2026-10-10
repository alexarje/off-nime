# Handover: NIME literature analysis

An analysis of the NIME proceedings (`~/github/NIME-bibliography`) and this off-NIME archive
together: who wrote what, on which topics, who cites whom, and which works are missing from both.
It lives in `analysis/` inside the off-NIME fork so that the parent repository stays untouched.

## Where things are

- `REPORT.md`: the findings, generated from `tools/report_template.md` by `tools/report.py`.
- `output/nime-atlas.html`: the interactive atlas (paper map, co-author network, citation
  network, trends, missing works). Self-contained; open it in a browser. The same page is written
  to `../atlas/index.html`, which the site's Pages workflow publishes at
  https://alexarje.github.io/off-nime/atlas/, with the report at /off-nime/analysis/REPORT.html.
- `output/candidates_cited.tsv` and `.bib`: works cited by five or more archive papers, in
  neither archive, with Crossref DOIs where found.
- `output/candidates_journals.tsv` and `.bib`: NIME-related articles from a Crossref sweep of
  seven journals and the CHI and TEI proceedings.
- `output/candidates_citing.tsv`: works outside NIME citing five or more archive entries.
- `output/candidates_local.tsv`: NIME-related papers in the local conference archive.
- `../bibs/Historical/historical.bib`: precursors before 1957, built by `tools/historical.py`
  from the hand-edited seed list `tools/historical_seeds.txt` (edit the seeds, not the bib);
  lookups cached in `data/historical_lookup.json`.
- `../bibs/Zotero/zotero.bib`: works on NIME topics from Alexander's Zotero library that the
  collection lacks, written by `tools/zotero_check.py` (title-classifier probability at least 0.9).
  It reads a copy of `~/Zotero/zotero.sqlite`, so `run.sh` skips it on other machines; the full
  candidate list, `data/zotero_candidates.tsv`, stays private.
- `tools/trl_batch.py` writes the next `data/trl/in_NN.jsonl` for entries without a TRL/ARL
  estimate; an agent following `tools/trl_rubric.md` writes `out_NN.jsonl`, and `merge_trl.py`
  merges them.
- The NIME paper draft on TRL and ARL is in
  `~/UiO Dropbox/alexanje@uio.no/writing/2-Artistic readyness level (NIME)/paper/`; its
  `analysis.py` reads `data/trl.json` and the validation sheet.
- GROBID 0.9.1 (CRF models only) in `~/tools/grobid-0.9.1`, with a portable JDK 21 in
  `~/tools/jdk-21.0.12.1+1`. Start with `~/tools/grobid-start.sh` (user unit `grobid`, 8G cap,
  127.0.0.1:8070 only; not started at boot), stop with `systemctl --user stop grobid`.
  `tools/grobid_refs.py` caches references in `data/grobid_refs.json`; parse_refs.py prefers them.
- PubPub exports of NIME 2021 and 2022 (made by hand from the PubPub community dashboard) are in
  `/media/alexanje/Seagate Hub/arkiv/Conferences/NIME/Paper proceedings/<year>/`.
  `tools/grobid_refs.py` reads their PDFs; `tools/pubpub_package.py <year>` writes a check
  (`zenodo/CHECK.md`), a manifest and one zip per collection for a Zenodo deposit.
- `output/collection.csv` records for every entry whether a full text, an abstract and a
  reference list were available, and where they came from.
- `tools/`: the pipeline; `run.sh` runs it in order.
- `data/` (not committed): the corpus, the Semantic Scholar cache (`s2/`, `s2_citing/`), the
  paper texts from nime.org (`text/`) and from the local archive (`local_text/`), and the
  intermediate JSON.

## Sources

- nime.org PDFs, reduced to text; the PDFs are not kept.
- `/media/alexanje/Seagate Hub/arkiv/Conferences`: OCR copies of early NIME papers, ICMC
  (curated pre-2000 papers and full volumes for 2000, 2001, 2002, 2005 and 2008), DAFx, SMC,
  ISMIR, ICMPC and workshops. 406 files there are zero bytes, mostly `ICMC/2000/Authors`.
- Crossref REST API, without a token (one request per second).
- Open Library search API (books) and Google Patents pages (patents), for the Historical checks.
- OpenAlex works API (`tools/openalex_refs.py`): reference lists for entries with a DOI and no
  text, including NIME 2021–2022, which are on PubPub (behind a bot check) and not on Zenodo.
  A small free daily allowance; the script stops early and resumes from its cache.
- tesseract with the system Portuguese and Italian packs (`tesseract-ocr-por`, `-ita`).
- Semantic Scholar Graph API, without a key. NIME reference lists are elided by the publisher;
  forward citations are not.

## Running

    cd analysis && python3 -m venv .venv && .venv/bin/pip install -r tools/requirements.txt
    ./run.sh

Run the scripts without `python -I`, since they import each other from `tools/`.

The candidate lists stay in `analysis/output/` until they are vetted, because every `.bib` under
`bibs/` appears in the website's table. `_config.yml` keeps the tools, data and tracking files
out of the site build.

## Deploying

Pushes to `main` on the fork do not start the Pages workflow; start it by hand with
`gh workflow run jekyll.yml -R alexarje/off-nime --ref main`. Pages is set to build from the
workflow.
