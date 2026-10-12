"""Re-extract NIME texts that pdftotext returned font-shifted, by OCR.

Some PDFs (mostly NIME 2006 and 2008) embed fonts whose character maps are wrong, so pdftotext
turns letters into punctuation. A text whose non-space characters are under MIN_LETTERS letters is
taken as garbled: its PDF is downloaded again, rendered at 300 dpi with pdftoppm and read with
tesseract. The garbled text is kept in data/text_garbled/ and the OCR text replaces it in
data/text/. Rerunning skips texts that already pass the check.
"""
import json
import subprocess
import tempfile
from pathlib import Path

import requests

from fetch_texts import HERE, OUT, target

MIN_LETTERS = 0.75
KEEP = HERE / "data" / "text_garbled"


def letter_share(path):
    t = "".join(path.read_text(errors="ignore")[:30000].split())
    return sum(c.isalpha() for c in t) / len(t) if t else 0.0


def ocr(r):
    url = r["url"].replace("http://", "https://")
    resp = requests.get(url, timeout=120)
    if resp.status_code != 200 or resp.content[:4] != b"%PDF":
        return f"download {resp.status_code}"
    with tempfile.TemporaryDirectory() as d:
        pdf = Path(d) / "paper.pdf"
        pdf.write_bytes(resp.content)
        subprocess.run(["pdftoppm", "-r", "300", "-png", str(pdf), str(Path(d) / "p")], check=True, timeout=300)
        pages = []
        for png in sorted(Path(d).glob("p*.png")):
            res = subprocess.run(["tesseract", str(png), "-", "-l", "eng"], capture_output=True, text=True,
                                 timeout=300)
            pages.append(res.stdout)
    KEEP.mkdir(exist_ok=True)
    t = target(r)
    (KEEP / t.name).write_text(t.read_text(errors="ignore"))
    t.write_text("\n\f".join(pages))
    return f"ok {letter_share(t):.2f}"


def main():
    corpus = json.loads((HERE / "data" / "corpus.json").read_text())
    todo = [r for r in corpus if r["dataset"] == "NIME papers" and r.get("url", "").endswith(".pdf")
            and target(r).exists() and letter_share(target(r)) < MIN_LETTERS]
    print(f"{len(todo)} garbled texts", flush=True)
    for r in todo:
        print(r["id"], ocr(r), flush=True)


if __name__ == "__main__":
    main()
