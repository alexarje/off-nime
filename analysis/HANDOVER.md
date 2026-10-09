# Handover: NIME literature analysis

An analysis of the NIME proceedings (`~/github/NIME-bibliography`) and this off-NIME archive
together: who wrote what, on which topics, who cites whom, and which works are missing from both.
It lives in `analysis/` inside the off-NIME fork so that the parent repository stays untouched.

## Where things are

- `REPORT.md`: the findings, generated from `tools/report_template.md` by `tools/report.py`.
- `output/nime-atlas.html`: the interactive atlas (paper map, co-author network, citation
  network, trends, missing works). Self-contained; open it in a browser.
- `output/candidates_cited.tsv`: works cited by five or more archive papers, in neither archive.
- `output/candidates_citing.tsv`: works outside NIME citing five or more archive entries.
- `output/candidates_local.tsv`: NIME-related papers in the local conference archive.
- `tools/`: the pipeline; `run.sh` runs it in order.
- `data/` (not committed): the corpus, the Semantic Scholar cache (`s2/`, `s2_citing/`), the
  paper texts from nime.org (`text/`) and from the local archive (`local_text/`), and the
  intermediate JSON.

## Sources

- nime.org PDFs, reduced to text; the PDFs are not kept.
- `/media/alexanje/Seagate Hub/arkiv/Conferences`: OCR copies of early NIME papers, ICMC
  (curated pre-2000 papers and full volumes for 2000, 2001, 2002, 2005 and 2008), DAFx, SMC,
  ISMIR, ICMPC and workshops. 406 files there are zero bytes, mostly `ICMC/2000/Authors`.
- Semantic Scholar Graph API, without a key. NIME reference lists are elided by the publisher;
  forward citations are not.

## Running

    cd analysis && python3 -m venv .venv && .venv/bin/pip install -r tools/requirements.txt
    ./run.sh

Run the scripts without `python -I`, since they import each other from `tools/`.
