"""Extract text from the local conference archive on the Seagate disk.

Covers ICMC, the OCR copies of early NIME papers, and the smaller conference sets. Texts go
to data/local_text/<relative path>.txt, mirroring the archive; existing texts are skipped.
"""
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path("/media/alexanje/Seagate Hub/arkiv/Conferences")
HERE = Path(__file__).resolve().parent.parent
OUT = HERE / "data" / "local_text"
SETS = ["ICMC", "NIME/nime-PDFs/OCR", "DAFx", "SMC", "ICMPC", "ISMIR", "M&G2", "GestureWorkshop", "CIM",
        "Enactive", "OSCC", "SoundMoves"]
MAX_MB = 40  # whole-proceedings volumes are skipped; they need splitting before they are useful


def one(pdf):
    dest = OUT / (str(pdf.relative_to(ROOT)) + ".txt")
    if dest.exists():
        return "skip"
    if pdf.stat().st_size > MAX_MB * 1e6:
        return "large"
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        r = subprocess.run(["pdftotext", "-enc", "UTF-8", str(pdf), str(dest)], capture_output=True, timeout=180)
        return "ok" if r.returncode == 0 else "error"
    except subprocess.TimeoutExpired:
        return "timeout"


def main():
    pdfs = [p for s in SETS for p in (ROOT / s).rglob("*") if p.suffix.lower() == ".pdf"]
    print(f"{len(pdfs)} PDFs", file=sys.stderr)
    status = {}
    with ThreadPoolExecutor(max_workers=4) as ex:
        for n, st in enumerate(ex.map(one, pdfs)):
            status[st] = status.get(st, 0) + 1
            if n % 500 == 0:
                print(n, status, file=sys.stderr, flush=True)
    print(status, file=sys.stderr)


if __name__ == "__main__":
    main()
