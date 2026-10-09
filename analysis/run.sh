#!/bin/sh
# Rebuild everything from the two archives. The fetch steps resume from their caches in data/.
# Each step runs memory-capped; the downloads are slow because Semantic Scholar rate-limits.
set -e
cd "$(dirname "$0")"
PY=".venv/bin/python"
cap() { systemd-run --user --scope -q -p MemoryMax="$1" "$PY" "tools/$2"; }
cap 1G build_corpus.py
cap 1G fetch_s2.py          # slow without an API key; Ctrl-C after the DOI phase is fine
cap 1G fetch_citing.py
cap 2G fetch_texts.py
cap 2G extract_local.py     # needs the Seagate Hub disk mounted
cap 2G parse_refs.py
cap 4G citations.py
cap 4G local_candidates.py
cap 4G analyse.py
cap 1G build_viewer.py
cap 1G report.py
