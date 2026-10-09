"""Download each NIME paper PDF from nime.org, keep its text only, and discard the PDF.

The text goes to data/text/<id>.txt (pdftotext, reading order). The PDFs are not kept,
to save disk; rerunning skips any entry whose text already exists.
"""
import json
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "data" / "text"
OUT.mkdir(parents=True, exist_ok=True)


def target(r):
    return OUT / (r["id"].replace(":", "__").replace("/", "_") + ".txt")


def fetch(r):
    url = r["url"].replace("http://", "https://")
    for attempt in range(4):
        try:
            resp = requests.get(url, timeout=120)
            if resp.status_code == 200 and resp.content[:4] == b"%PDF":
                break
            if resp.status_code == 404:
                return r["id"], "404"
        except requests.RequestException:
            pass
        time.sleep(5 * (attempt + 1))
    else:
        return r["id"], "failed"
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(resp.content)
        f.flush()
        res = subprocess.run(["pdftotext", "-enc", "UTF-8", f.name, str(target(r))],
                             capture_output=True, timeout=120)
    time.sleep(0.5)
    return r["id"], "ok" if res.returncode == 0 else "pdftotext"


def main():
    corpus = json.loads((HERE / "data" / "corpus.json").read_text())
    todo = [r for r in corpus if r["dataset"] == "NIME papers" and r["url"] and r["url"].endswith(".pdf")
            and not target(r).exists()]
    print(f"{len(todo)} to fetch", file=sys.stderr)
    status = {}
    with ThreadPoolExecutor(max_workers=3) as ex:
        for n, (rid, st) in enumerate(ex.map(fetch, todo)):
            status[rid] = st
            if n % 100 == 0:
                print(n, rid, st, file=sys.stderr, flush=True)
    (HERE / "data" / "fetch_texts_status.json").write_text(json.dumps(status, indent=0))
    print({s: sum(v == s for v in status.values()) for s in set(status.values())}, file=sys.stderr)


if __name__ == "__main__":
    main()
