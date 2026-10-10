"""Reference lists by GROBID for the papers whose text came from a nime.org PDF.

The text parser splits references on numbered markers or author–year line starts, and pdftotext
interleaves the two columns of a page, which breaks references in half; it finds about half of
the links that Semantic Scholar gives. GROBID reads the PDF's layout instead. This script downloads
each PDF again (sequentially, one second apart), posts it to a local GROBID service
(/api/processReferences, no consolidation, so nothing leaves the machine), keeps the title, year,
first author's surname, DOI and raw string of each reference, and deletes the PDF.

Results are cached per entry in data/grobid_refs.json, so a stopped run resumes. parse_refs.py
uses them in place of the text-split references where they exist.

The NIME papers of 2021 and 2022 are on PubPub, behind a bot check; for these the script reads
the PDFs from the PubPub community exports in EXPORTS/<year>/ (one zip per collection, a folder
per pub named by its slug), when they are there, and also writes their plain text to data/text/,
so that the rest of the pipeline counts them as read.

The service runs from ~/tools/grobid-0.9.1 as the user unit grobid (see HANDOVER.md).
"""
import json
import re
import subprocess
import sys
import zipfile
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "data" / "grobid_refs.json"
GROBID = "http://127.0.0.1:8070/api/processReferences"
HEAD = {"User-Agent": "off-nime-analysis/0.1 (https://github.com/alexarje/off-nime)"}
NS = {"t": "http://www.tei-c.org/ns/1.0"}
EXPORTS = Path("/media/alexanje/Seagate Hub/arkiv/Conferences/NIME/Paper proceedings")
TEXT = HERE / "data" / "text"


def pubpub_pdfs():
    """{slug: (zip path, member)} for every PDF in the PubPub exports."""
    out = {}
    for z in EXPORTS.glob("*/nime-nime-*.zip"):
        with zipfile.ZipFile(z) as zf:
            for m in zf.namelist():
                if m.endswith(".pdf"):
                    out[m.split("/")[-2].lower()] = (z, m)
    return out


def text(el):
    return " ".join("".join(el.itertext()).split()) if el is not None else ""


def parse_tei(xml):
    refs = []
    root = ET.fromstring(xml)
    for b in root.iter("{http://www.tei-c.org/ns/1.0}biblStruct"):
        a, m = b.find("t:analytic", NS), b.find("t:monogr", NS)
        title = text(a.find("t:title", NS)) if a is not None else ""
        if not title and m is not None:
            title = text(m.find("t:title", NS))
        year = None
        for d in b.iter("{http://www.tei-c.org/ns/1.0}date"):
            w = d.get("when") or ""
            if w[:4].isdigit():
                year = int(w[:4])
                break
        first = ""
        for part in (a, m):
            s = part.find(".//t:author/t:persName/t:surname", NS) if part is not None else None
            if s is not None:
                first = text(s).lower()
                break
        doi = text(b.find(".//t:idno[@type='DOI']", NS)).lower()
        raw = text(b.find("t:note[@type='raw_reference']", NS))
        refs.append({"title": title, "year": year, "first": first, "doi": doi, "raw": raw})
    return refs


def process(url=None, pdf=None, text_to=None):
    if pdf is None:
        r = requests.get(url.replace("http://", "https://"), headers=HEAD, timeout=120)
        if r.status_code != 200 or r.content[:4] != b"%PDF":
            return None, f"http {r.status_code}"
        pdf = r.content
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(pdf)
        f.flush()
        if text_to is not None:
            t = subprocess.run(["pdftotext", f.name, "-"], capture_output=True, text=True, timeout=300).stdout
            if t.strip():
                text_to.write_text(t)
        for attempt in range(5):
            with open(f.name, "rb") as fh:
                g = requests.post(GROBID, files={"input": fh},
                                  data={"consolidateCitations": "0", "includeRawCitations": "1"}, timeout=600)
            if g.status_code == 503:  # all GROBID workers busy
                time.sleep(5)
                continue
            break
    if g.status_code == 204:
        return [], "no references"
    if g.status_code != 200:
        return None, f"grobid {g.status_code}"
    return parse_tei(g.text), "ok"


def main():
    try:
        requests.get(GROBID.replace("processReferences", "isalive"), timeout=5).raise_for_status()
    except requests.RequestException:
        print("GROBID is not running on 127.0.0.1:8070; skipped (parse_refs.py uses the cache)", file=sys.stderr)
        return
    from parse_refs import text_sources
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    corpus = json.loads((HERE / "data" / "corpus.json").read_text())
    src, _ = text_sources(corpus)
    # the papers read from a nime.org download; the OCR and local ICMC texts come from scans
    # whose PDFs have broken fonts or are not online
    todo = [r for r in corpus if r["id"] in src and src[r["id"]].parent.name == "text"
            and (r.get("url") or "").lower().endswith(".pdf")]
    cache = json.loads(OUT.read_text()) if OUT.exists() else {}
    # PubPub papers, from the local exports
    pub = pubpub_pdfs() if EXPORTS.exists() else {}
    local = [(r, pub[m.group(1).lower()]) for r in corpus
             for m in [re.search(r"pubpub\.org/pub/([^/?#]+)", r.get("url") or "")]
             if m and m.group(1).lower() in pub and r["id"] not in cache]
    print(f"{len(local)} PubPub papers from the local exports", file=sys.stderr, flush=True)
    for r, (z, member) in local:
        with zipfile.ZipFile(z) as zf:
            data = zf.read(member)
        refs, status = process(pdf=data, text_to=TEXT / (r["id"].replace(":", "__").replace("/", "_") + ".txt"))
        if refs is not None:
            cache[r["id"]] = refs
    OUT.write_text(json.dumps(cache, ensure_ascii=False))
    todo = [r for r in todo if r["id"] not in cache][:limit]
    print(f"{len(todo)} to process, {len(cache)} cached", file=sys.stderr, flush=True)
    for n, r in enumerate(todo):
        try:
            refs, status = process(r["url"])
        except requests.RequestException as e:
            refs, status = None, type(e).__name__
        if refs is not None:
            cache[r["id"]] = refs
        if n % 25 == 0 or refs is None:
            OUT.write_text(json.dumps(cache, ensure_ascii=False))
            print(f"{n + 1}/{len(todo)} {r['id']} {status} {len(refs or [])}", file=sys.stderr, flush=True)
        time.sleep(1)
    OUT.write_text(json.dumps(cache, ensure_ascii=False))
    print(f"done: {len(cache)} entries, {sum(len(v) for v in cache.values())} references", file=sys.stderr)


if __name__ == "__main__":
    main()
