"""Split the older SBCM proceedings volumes (whole-volume PDFs, text in data/sbcm_text/) into papers.

A page starts a paper when an "Abstract" heading appears near its top; the title is the first
lines of that page after the running header, and the abstract is the text after the heading up
to the next heading. The 1994–1998 volumes are scans without a text layer, and the 2007 volume
did not extract, so they are not covered. Writes data/sbcm_volumes.json in the shape of
data/journals.json, which score_journals.py scores with the sweep.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
HEADER = re.compile(r"simp[óo]sio brasileiro|computa[çc][ãa]o musical|brazilian symposium|sbcm|^\s*\d+\s*$|proceedings", re.I)


def main():
    out = []
    for f in sorted((HERE / "data" / "sbcm_text").glob("*.txt")):
        year = int(f.stem)
        pages = f.read_text(errors="replace").split("\f")
        for page in pages:
            head = page[:3000]
            m = re.search(r"^\s*(Abstract|ABSTRACT)\b[.:]?", head, re.M)
            if not m:
                continue
            lines = [l.strip() for l in head[:m.start()].splitlines() if l.strip() and not HEADER.search(l)]
            if not lines:
                continue
            title = []
            for l in lines[:4]:
                # authors and affiliations follow the title: stop at an e-mail, a footnote mark or a university
                if re.search(r"@|universi|institut|faculdade|departamento|^\d|\b[A-Z]\. [A-Z]", l, re.I) and title:
                    break
                title.append(l)
            abstract = re.split(r"\n\s*(Resumo|RESUMO|1\.?\s+Introdu|1\.?\s+INTRODU|Keywords|Palavras)", page[m.end():])[0]
            out.append({"source": "SBCM (Brazilian Symposium on Computer Music)", "doi": "", "url": "",
                        "title": " ".join(title)[:250], "title_orig": " ".join(title)[:250],
                        "abstract": re.sub(r"\s+", " ", abstract).strip()[:3000], "year": year,
                        "authors": [l for l in lines[len(title):len(title) + 3] if not re.search(r"@|universi", l, re.I)][:2],
                        "container": f"SBCM {year}", "type": "proceedings-article", "volume": None, "issue": None,
                        "pages": None})
    (HERE / "data" / "sbcm_volumes.json").write_text(json.dumps(out, ensure_ascii=False))
    from collections import Counter
    print(len(out), dict(Counter(r["year"] for r in out)))
    for r in out[:8]:
        print(r["year"], "|", r["title"][:90], "|", r["abstract"][:80])


if __name__ == "__main__":
    main()
