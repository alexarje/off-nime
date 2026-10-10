"""Download whole-volume proceedings PDFs and keep their text, with OCR for scanned volumes.

Currently the CIM (Colloquio di Informatica Musicale) proceedings, 1979–2024, listed on the AIMI
website and served by the LIM in Milan. Each volume's text goes to data/volumes_text/CIM_<year>.txt
with form feeds between pages; the PDF is deleted. A volume whose text layer yields under
TEXT_MIN characters per page is read with tesseract (Italian and English; needs the tesseract-ocr-ita package).
Volumes already extracted are skipped, so the job can be stopped and resumed.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "data" / "volumes_text"
OUT.mkdir(parents=True, exist_ok=True)
TEXT_MIN = 300
CIM = {
    1979: "1979_CIM_III_Atti.pdf", 1981: "1981_CIM_IV_Atti.pdf", 1983: "1983_CIM_V_Atti.pdf",
    1985: "1985_CIM_VI_Atti.pdf", 1988: "1988_CIM_VII_Atti.pdf", 1989: "1989_CIM_VIII_Atti.pdf",
    1991: "1991_CIM_IX_Atti.pdf", 1993: "1993_CIM_X_Atti.pdf", 1995: "1995_CIM_XI_Atti.pdf",
    1998: "1998_CIM_XII_Atti.pdf", 2000: "2000_CIM_XIII_Atti.pdf", 2003: "2003_CIM_XIV_Atti.pdf",
    2006: "2006_CIM_XVI_Atti.pdf", 2008: "2008_CIM_XVII_Atti.pdf", 2010: "2010_CIM_XVIII_Atti.pdf",
    2012: "2012_CIM_XIX_Atti.pdf", 2014: "2014_CIM_XX_Atti.pdf", 2016: "2016_CIM_XXI_Atti.pdf",
    2018: "2018_CIM_XXII_Atti.pdf", 2022: "2022_CIM_XXIII_Atti.pdf", 2024: "2024_CIM_XXIV_Atti.pdf",
}


def extract(pdf, dest):
    subprocess.run(["pdftotext", "-enc", "UTF-8", str(pdf), str(dest)], capture_output=True, timeout=1800)
    text = dest.read_text(errors="replace") if dest.exists() else ""
    pages = max(text.count("\f"), 1)
    if len(re.sub(r"\s", "", text)) / pages >= TEXT_MIN:
        return "text", pages
    # scanned volume: render each page and read it
    with tempfile.TemporaryDirectory(dir=OUT) as tmp:
        subprocess.run(["pdftoppm", "-r", "200", "-gray", str(pdf), f"{tmp}/p"], check=True, timeout=7200)
        imgs = sorted(Path(tmp).glob("p-*.pgm"))
        with open(dest, "w") as f:
            for img in imgs:
                r = subprocess.run(["tesseract", str(img), "-", "-l", "ita+eng"], capture_output=True, text=True,
                                   timeout=600)
                f.write(r.stdout + "\f")
                img.unlink()
    return "ocr", len(imgs)


def main():
    for year, name in CIM.items():
        dest = OUT / f"CIM_{year}.txt"
        if dest.exists() and dest.stat().st_size > 10000:
            continue
        with tempfile.NamedTemporaryFile(suffix=".pdf", dir=OUT) as tmp:
            r = requests.get(f"https://cim.lim.di.unimi.it/{name}", timeout=600)
            if r.status_code != 200 or r.content[:4] != b"%PDF":
                print(f"CIM {year}: {r.status_code}", file=sys.stderr, flush=True)
                continue
            tmp.write(r.content)
            tmp.flush()
            how, pages = extract(Path(tmp.name), dest)
        print(f"CIM {year}: {how}, {pages} pages", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
