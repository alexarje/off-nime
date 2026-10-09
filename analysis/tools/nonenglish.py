"""Fetch non-English conference proceedings: JIM (France, from HAL) and SBCM (Brazil, from SBC
OpenLib over OAI-PMH).

Both sources often carry an English title and abstract beside the original. Records with English
text go to data/nonenglish.json in the shape of data/journals.json, with the English text in the
title and abstract fields used for scoring and the original title kept beside it; score_journals.py
scores them with the journal sweep. Records with no English text are listed in
output/candidates_nonenglish_unscored.tsv. Responses are cached in data/nonenglish_cache/.
"""
import hashlib
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent.parent
CACHE = HERE / "data" / "nonenglish_cache"
CACHE.mkdir(parents=True, exist_ok=True)
EN = {"the", "and", "of", "to", "in", "is", "for", "that", "with", "this", "on", "as", "are", "by", "an", "be"}


def english_share(text):
    words = re.findall(r"[a-zA-ZÀ-ſ]+", (text or "").lower())
    return sum(w in EN for w in words) / len(words) if words else 0.0


def cached(url, params, as_text=False):
    key = hashlib.sha1((url + json.dumps(params, sort_keys=True)).encode()).hexdigest()
    f = CACHE / f"{key}.{'xml' if as_text else 'json'}"
    if f.exists():
        return f.read_text() if as_text else json.loads(f.read_text())
    wait = 5
    for _ in range(6):
        try:
            r = requests.get(url, params=params, timeout=120)
            if r.status_code == 200:
                f.write_text(r.text)
                time.sleep(1)
                return r.text if as_text else r.json()
            print(f"  {r.status_code}, waiting {wait} s", file=sys.stderr)
        except requests.RequestException as ex:
            print(f"  {ex}", file=sys.stderr)
        time.sleep(wait)
        wait *= 2
    return None


def hal_jim():
    out, start = [], 0
    fl = "halId_s,uri_s,doiId_s,title_s,en_title_s,authFullName_s,producedDateY_i,abstract_s,en_abstract_s,language_s,conferenceTitle_s"
    while True:
        d = cached("https://api.archives-ouvertes.fr/search/", {"q": "collCode_s:JIM", "fl": fl, "rows": 500,
                                                                  "start": start, "wt": "json", "sort": "docid asc"})
        docs = d["response"]["docs"]
        for x in docs:
            orig = (x.get("title_s") or [""])[0]
            en_title = (x.get("en_title_s") or [""])[0] or (orig if english_share(orig) >= 0.1 else "")
            abstracts = (x.get("en_abstract_s") or []) + [a for a in x.get("abstract_s", []) if english_share(a) >= 0.12]
            out.append({"source": "JIM (Journées d'Informatique Musicale)", "doi": (x.get("doiId_s") or "").lower(),
                        "url": x.get("uri_s"), "title_orig": orig, "title": en_title,
                        "abstract": abstracts[0] if abstracts else "", "year": x.get("producedDateY_i"),
                        "authors": x.get("authFullName_s", []), "container": (x.get("conferenceTitle_s") or "JIM"),
                        "type": "proceedings-article", "language": ",".join(x.get("language_s", [])),
                        "volume": None, "issue": None, "pages": None})
        start += len(docs)
        if not docs or start >= d["response"]["numFound"]:
            break
    return out


NS = {"oai": "http://www.openarchives.org/OAI/2.0/", "dc": "http://purl.org/dc/elements/1.1/",
      "oai_dc": "http://www.openarchives.org/OAI/2.0/oai_dc/", "xml": "http://www.w3.org/XML/1998/namespace"}
LANG = "{http://www.w3.org/XML/1998/namespace}lang"


def sol_sbcm():
    out, params = [], {"verb": "ListRecords", "metadataPrefix": "oai_dc"}
    while True:
        xml = cached("https://sol.sbc.org.br/index.php/sbcm/oai", params, as_text=True)
        root = ET.fromstring(xml)
        for rec in root.iterfind(".//oai:record", NS):
            md = rec.find(".//oai_dc:dc", NS)
            if md is None:
                continue
            titles = [(t.get(LANG, ""), t.text or "") for t in md.findall("dc:title", NS)]
            descs = [(t.get(LANG, ""), t.text or "") for t in md.findall("dc:description", NS)]
            orig = titles[0][1] if titles else ""
            en_t = next((t for l, t in titles if l.startswith("en")), "") or (orig if english_share(orig) >= 0.1 else "")
            en_d = next((t for l, t in descs if l.startswith("en")), "") or next((t for _, t in descs if english_share(t) >= 0.12), "")
            date = (md.findtext("dc:date", "", NS) or "")[:4]
            ids = [i.text or "" for i in md.findall("dc:identifier", NS)]
            doi = next((re.sub(r"^https?://(dx\.)?doi\.org/", "", i) for i in ids if "doi" in i), "")
            out.append({"source": "SBCM (Brazilian Symposium on Computer Music)", "doi": doi.lower(),
                        "url": next((i for i in ids if i.startswith("http")), ""), "title_orig": orig, "title": en_t,
                        "abstract": re.sub(r"<[^>]+>", " ", en_d), "year": int(date) if date.isdigit() else None,
                        "authors": [c.text or "" for c in md.findall("dc:creator", NS)], "container": "SBCM",
                        "type": "proceedings-article", "language": md.findtext("dc:language", "", NS),
                        "volume": None, "issue": None, "pages": None})
        tok = root.find(".//oai:resumptionToken", NS)
        if tok is None or not (tok.text or "").strip():
            break
        params = {"verb": "ListRecords", "resumptionToken": tok.text.strip()}
    return out


def main():
    recs = hal_jim() + sol_sbcm()
    scored = [r for r in recs if r["title"] and r["year"] and (r["abstract"] or len(r["title"].split()) >= 4)]
    unscored = [r for r in recs if r not in scored]
    (HERE / "data" / "nonenglish.json").write_text(json.dumps(scored, ensure_ascii=False))
    with open(HERE / "output" / "candidates_nonenglish_unscored.tsv", "w") as f:
        f.write("source\tyear\ttitle\tauthors\tlanguage\turl\n")
        for r in unscored:
            f.write("\t".join(re.sub(r"\s+", " ", str(x)) for x in
                              [r["source"], r["year"] or "", r["title_orig"], "; ".join(r["authors"][:3]),
                               r["language"], r["url"] or r["doi"]]) + "\n")
    by = {}
    for r in recs:
        s = by.setdefault(r["source"], {"records": 0, "with_english": 0})
        s["records"] += 1
        s["with_english"] += r in scored
    (HERE / "data" / "nonenglish_stats.json").write_text(json.dumps(by, indent=1))
    print(json.dumps(by, indent=1), file=sys.stderr)


if __name__ == "__main__":
    main()
