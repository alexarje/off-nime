"""Split whole-volume proceedings into papers: older SBCM (text in data/sbcm_text/) and CIM (text in
data/volumes_text/, from fetch_volumes.py).

A page starts a paper when an "Abstract" heading appears near its top; the title is the first
lines of that page after the running header, and the abstract is the text after the heading up
to the next heading ("Sommario" or "Riassunto" for Italian papers without an English abstract).
Scanned volumes (SBCM 1994–1998, early CIM) are read by OCR first (tools/sbcm_ocr.sh,
tools/fetch_volumes.py). Older papers often have no abstract heading and are missed. Writes
data/sbcm_volumes.json in the shape of data/journals.json, which score_journals.py scores.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
HEADER = re.compile(r"simp[óo]sio brasileiro|computa[çc][ãa]o musical|brazilian symposium|sbcm|^\s*\d+\s*$|proceedings|"
                    r"colloquio di informatica musicale|\bcim\b|atti del|informatica musicale", re.I)


def letter_spaced(line):
    """Running headers in some volumes come out letter-spaced ("Pro cee di n gs of th e")."""
    toks = line.split()
    return len(toks) >= 4 and sum(len(t) <= 2 for t in toks) / len(toks) > 0.5


SOURCES = [("SBCM (Brazilian Symposium on Computer Music)", "SBCM", "sbcm_text", "*.txt"),
           ("CIM (Colloquio di Informatica Musicale)", "CIM", "volumes_text", "CIM_*.txt")]


def main():
    out = []
    files = [(src, short, f) for src, short, d, pat in SOURCES for f in sorted((HERE / "data" / d).glob(pat))]
    for source, short, f in files:
        year = int(re.sub(r"\D", "", f.stem))
        pages = f.read_text(errors="replace").split("\f")
        for page in pages:
            head = page[:3000]
            m = re.search(r"^\s*(Abstract|ABSTRACT)\b[.:]?", head, re.M) or \
                re.search(r"^\s*(Sommario|SOMMARIO|Riassunto|RIASSUNTO)\b[.:]?", head, re.M)
            if not m:
                continue
            lines = [l.strip() for l in head[:m.start()].splitlines()
                     if l.strip() and not HEADER.search(l) and not letter_spaced(l)]
            if not lines:
                continue
            title = []
            for l in lines[:4]:
                # authors and affiliations follow the title: stop at an e-mail, a footnote mark or a university
                if re.search(r"@|universi|institut|faculdade|departamento|^\d|\b[A-Z]\. [A-Z]", l, re.I) and title:
                    break
                title.append(l)
            abstract = re.split(r"\n\s*(Resumo|RESUMO|Sommario|SOMMARIO|1\.?\s+Introdu|1\.?\s+INTRODU|Keywords|Parole chiave|Palavras)",
                                page[m.end():])[0]
            out.append({"source": source, "doi": "", "url": "",
                        "title": " ".join(title)[:250], "title_orig": " ".join(title)[:250],
                        "abstract": re.sub(r"\s+", " ", abstract).strip()[:3000], "year": year,
                        "authors": [l for l in lines[len(title):len(title) + 3] if not re.search(r"@|universi", l, re.I)][:2],
                        "container": f"{short} {year}", "type": "proceedings-article", "volume": None, "issue": None,
                        "pages": None})
    (HERE / "data" / "sbcm_volumes.json").write_text(json.dumps(out, ensure_ascii=False))
    from collections import Counter
    print(len(out), dict(Counter(r["year"] for r in out)))
    for r in out[:8]:
        print(r["year"], "|", r["title"][:90], "|", r["abstract"][:80])


if __name__ == "__main__":
    main()
