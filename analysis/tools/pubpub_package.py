"""Check and package the PubPub exports of the NIME 2021 and 2022 proceedings for a Zenodo deposit.

PubPub's community export gives one zip per collection (full papers, music, workshops and so on),
with a folder per pub holding its PDF and a JATS XML file. This script reads the zips in
<archive>/<year>/, takes title, authors, licence, abstract and keywords from the XML, and matches
each pub to the NIME bibliography (~/github/NIME-bibliography) by its PubPub slug, or else by title.

Writes to <archive>/<year>/zenodo/:
- manifest.csv: one row per pub (collection, slug, title, authors, licence, abstract, keywords,
  PDF size, the matching NIME bibliography key and DOI);
- CHECK.md: counts per collection, the bibliography entries that are missing from the export and
  the pubs that are not in the bibliography, for checking before the upload;
- nime<year>_<collection>.zip: the PDFs and XML files of one collection, with manifest.csv and
  README.md, ready to upload.

The exports are left untouched. Usage: pubpub_package.py 2021 [2022 ...]
"""
import csv
import io
import re
import sys
import zipfile
from difflib import SequenceMatcher
from pathlib import Path
from xml.etree import ElementTree as ET

import bibtexparser

from parse_refs import letters

ARCHIVE = Path("/media/alexanje/Seagate Hub/arkiv/Conferences/NIME/Paper proceedings")
NIMEBIB = Path.home() / "github" / "NIME-bibliography"
XL = "{http://www.w3.org/1999/xlink}href"


def bib(year):
    out = []
    for d in ("paper_proceedings", "music_proceedings", "installation_proceedings", "alt_proceedings"):
        f = NIMEBIB / d / f"nime{year}.bib"
        if f.exists():
            for e in bibtexparser.load(open(f)).entries:
                slug = (re.search(r"pubpub\.org/pub/([^/?#]+)", e.get("url", "")) or [None, ""])[1]
                out.append({"key": e["ID"], "part": d.split("_")[0], "title": e.get("title", ""),
                            "doi": e.get("doi", ""), "slug": slug.lower()})
    return out


def text(el):
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip() if el is not None else ""


def pubs(year):
    out = []
    for z in sorted((ARCHIVE / str(year)).glob("nime-nime-*.zip")):
        coll = re.match(rf"nime-nime-{year}-(.+?)-\d{{4}}-\d\d-\d\dT", z.name).group(1)
        with zipfile.ZipFile(z) as zf:
            names = zf.namelist()
            for x in [n for n in names if n.endswith(".xml")]:
                slug = x.split("/")[-2]
                root = ET.fromstring(zf.read(x))
                meta = root.find(".//article-meta")
                authors = [f"{text(c.find('name/surname'))}, {text(c.find('name/given-names'))}".strip(", ")
                           for c in meta.findall(".//contrib[@contrib-type='author']")]
                lic = meta.find(".//license")
                abstract = text(root.find(".//sec[@id='abstract']/p"))
                kw = text(root.find(".//sec[@id='author-keywords']/p"))
                pdf = x[:-4] + ".pdf"
                out.append({"collection": coll, "zip": z, "slug": slug, "xml": x,
                            "pdf": pdf if pdf in names else "", "pdf_bytes": zf.getinfo(pdf).file_size if pdf in names else 0,
                            "title": text(meta.find(".//article-title")), "authors": "; ".join(authors),
                            "licence": lic.get(XL, "") if lic is not None else "",
                            "abstract": "yes" if len(abstract) >= 80 else "", "keywords": kw})
    return out


def match(p, entries):
    for e in entries:
        if e["slug"] and e["slug"] == p["slug"].lower():
            return e
    t = letters(p["title"])[:80]
    best = max(entries, key=lambda e: SequenceMatcher(None, t, letters(e["title"])[:80]).ratio(), default=None)
    if best and SequenceMatcher(None, t, letters(best["title"])[:80]).ratio() >= 0.9:
        return best
    return None


def main(year):
    out = ARCHIVE / str(year) / "zenodo"
    out.mkdir(exist_ok=True)
    entries, ps = bib(year), pubs(year)
    for p in ps:
        e = match(p, entries)
        p["bib_key"], p["bib_part"], p["doi"] = (e["key"], e["part"], e["doi"]) if e else ("", "", "")
    cols = ["collection", "slug", "title", "authors", "licence", "abstract", "keywords", "pdf_bytes",
            "bib_key", "bib_part", "doi"]
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(cols)
    for p in sorted(ps, key=lambda p: (p["collection"], p["title"].lower())):
        w.writerow([p[c] for c in cols])
    (out / "manifest.csv").write_text(buf.getvalue())

    matched = {p["bib_key"] for p in ps if p["bib_key"]}
    colls = sorted({p["collection"] for p in ps})
    lines = [f"# NIME {year}: PubPub export against the NIME bibliography", "",
             f"{len(ps)} pubs in {len(colls)} collections; the NIME bibliography lists {len(entries)} entries for {year}.", "",
             "| Collection | Pubs | With PDF | With abstract | In the bibliography | Licences |",
             "|---|---:|---:|---:|---:|---|"]
    for c in colls:
        cp = [p for p in ps if p["collection"] == c]
        lic = ", ".join(sorted({re.sub(r"https?://creativecommons.org/licenses/", "CC ", p["licence"]).rstrip("/") or "none"
                                for p in cp}))
        lines.append(f"| {c} | {len(cp)} | {sum(bool(p['pdf']) for p in cp)} | {sum(bool(p['abstract']) for p in cp)} "
                     f"| {sum(bool(p['bib_key']) for p in cp)} | {lic} |")
    missing = [e for e in entries if e["key"] not in matched]
    lines += ["", f"## In the bibliography, not in the export ({len(missing)})", ""]
    lines += [f"- {e['key']} ({e['part']}): {e['title']}" for e in missing] or ["None."]
    extra = [p for p in ps if not p["bib_key"]]
    lines += ["", f"## In the export, not in the bibliography ({len(extra)})", ""]
    lines += [f"- {p['collection']}: {p['title']} ({p['slug']})" for p in extra] or ["None."]
    nopdf = [p for p in ps if not p["pdf"]]
    lines += ["", f"## Without a PDF ({len(nopdf)})", ""]
    lines += [f"- {p['collection']}: {p['title']} ({p['slug']})" for p in nopdf] or ["None."]
    (out / "CHECK.md").write_text("\n".join(lines) + "\n")

    for c in colls:
        cp = [p for p in ps if p["collection"] == c]
        readme = (f"# NIME {year}: {c.replace('-', ' ')}\n\n"
                  f"Archival copy of the {len(cp)} pubs in the '{c}' collection of the NIME {year} proceedings, "
                  f"published on PubPub (https://nime.pubpub.org). Each pub has its PDF and a JATS XML file, named by "
                  f"its PubPub slug; manifest.csv lists title, authors, licence and the DOI of the version of record.\n")
        sub = io.StringIO()
        sw = csv.writer(sub)
        sw.writerow(cols)
        for p in sorted(cp, key=lambda p: p["title"].lower()):
            sw.writerow([p[k] for k in cols])
        with zipfile.ZipFile(cp[0]["zip"]) as src, \
                zipfile.ZipFile(out / f"nime{year}_{c}.zip", "w", zipfile.ZIP_STORED) as dst:
            for p in cp:
                for member, kind in ((p["pdf"], "pdf"), (p["xml"], "xml")):
                    if member:
                        dst.writestr(f"nime{year}_{c}/{kind}/{p['slug']}.{kind}", src.read(member))
            dst.writestr(f"nime{year}_{c}/manifest.csv", sub.getvalue())
            dst.writestr(f"nime{year}_{c}/README.md", readme)
    print(f"{year}: {len(ps)} pubs, {len(matched)} of {len(entries)} bibliography entries matched, "
          f"{len(missing)} missing from the export, {len(extra)} not in the bibliography; written to {out}")


if __name__ == "__main__":
    for y in sys.argv[1:]:
        main(int(y))
