"""Write the abstracts found for curated off-NIME entries into their bib files.

Sources are data/abstracts.json (Crossref, Semantic Scholar) and data/abstracts_extra.json
(OpenAlex, local PDFs). An entry that already has an abstract field is left alone. Each file keeps
its own line endings and indentation, as in offnime_dois.py.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent


def main():
    corpus = {r["id"]: r for r in json.loads((HERE / "data" / "corpus.json").read_text())}
    found = json.loads((HERE / "data" / "abstracts.json").read_text())
    found.update({k: v for k, v in json.loads((HERE / "data" / "abstracts_extra.json").read_text()).items()
                  if k.startswith("off-nime:")})
    from fill_abstracts import page_chrome
    found = {k: v for k, v in found.items() if not page_chrome(v["abstract"])}
    edited = 0
    for rid, v in found.items():
        r = corpus.get(rid)
        if not r or r["archive"] != "off-nime":
            continue
        path = HERE.parent / r["file"]
        with open(path, encoding="utf-8", newline="") as fh:
            s = fh.read()
        nl = "\r\n" if "\r\n" in s else "\n"
        key = rid.split(":", 1)[1]
        m = re.search(r"@\w+\{" + re.escape(key) + r",", s)
        if not m:
            continue
        depth, j = 0, s.index("{", m.start())
        for j in range(j, len(s)):
            depth += s[j] == "{"
            depth -= s[j] == "}"
            if depth == 0:
                break
        entry = s[m.start():j]
        if re.search(r"^\s*abstract\s*=", entry, re.M | re.I):
            continue
        text = re.sub(r"\s+", " ", v["abstract"]).replace("{", "(").replace("}", ")").strip()
        indent = re.search(r"\n([ \t]*)[A-Za-z]+\s*=", entry)
        indent = indent.group(1) if indent else ""
        body = entry.rstrip()
        sep = "" if body.endswith(",") else ","
        s = s[:m.start()] + body + f"{sep}{nl}{indent}abstract = {{{text}}}{nl}" + s[j:]
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write(s)
        edited += 1
    print(f"{edited} abstracts written")


if __name__ == "__main__":
    main()
