#!/bin/sh
# Rebuild everything from the two archives. The fetch steps resume from their caches in data/.
# Each step runs memory-capped; the downloads are slow because Semantic Scholar rate-limits.
set -e
cd "$(dirname "$0")"
PY=".venv/bin/python"
cap() { systemd-run --user --scope -q -p MemoryMax="$1" "$PY" tools/$2; }
cap 1G build_corpus.py
cap 1G fetch_abstracts.py
cap 2G fill_abstracts.py
cap 1G build_corpus.py      # again, to merge the abstracts
cap 1G fetch_s2.py          # slow without an API key; Ctrl-C after the DOI phase is fine
cap 1G fetch_citing.py
cap 2G fetch_texts.py
cap 2G extract_local.py     # needs the Seagate Hub disk mounted
cap 2G parse_refs.py
cap 4G citations.py
cap 1G "crossref.py resolve"
cap 2G "crossref.py sweep"
cap 1G zenodo.py
cap 1G nonenglish.py
cap 1G sbcm_volumes.py      # needs data/sbcm_text/ (see HANDOVER)
cap 1G more_proceedings.py
cap 4G local_candidates.py
cap 2G books.py
cap 4G score_journals.py
cap 2G topic.py
cap 2G build_cited.py
cap 1G snowball.py
cap 3G theses.py
cap 1G "offnime_dois.py --apply"
cap 1G merge_trl.py         # after the TRL/ARL agents have written data/trl/out_*.jsonl
cap 4G analyse.py
cap 1G export.py
cap 1G build_viewer.py
cap 1G report.py
