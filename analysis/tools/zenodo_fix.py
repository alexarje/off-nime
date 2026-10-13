"""Correct the titles and descriptions of NIME Zenodo records that differ from the published papers.

The fixes are those of NIME-conference/NIME-bibliography#128: three records with an earlier title,
four descriptions that still hold a review placeholder. A title is set to the one in the
bibliography (data/corpus.json); a placeholder is replaced by the name in the published paper.

Without --apply the script only reads the public records and prints each change. With --apply it
needs a Zenodo token with edit rights on the records (read from the file given by --token-file,
never printed), opens an edit draft of each record, changes the one field and publishes it. The DOI
stays the same. --only <key> limits the run to one record, for a first test.
Usage: tools/zenodo_fix.py [--apply --token-file <path>] [--only <key>]
"""
import argparse
import json
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent.parent
API = "https://zenodo.org/api/records"
RDM = {"Accept": "application/vnd.inveniordm.v1+json"}

TITLES = ["nime2014_ncollins", "nime2019_Bown", "nime2023_56"]
PLACEHOLDERS = {
    "nime2013_Andersson": ("XXXXX.The", "RHYME. The"),
    "nime2018_VillicañaShaw": ("xxxxx (xxxx)", "California Institute of the Arts (CalArts)"),
    "nime2020_26": ("named ANON,", "named Shimon,"),
    "nime2026_121": ("[Anonymous]", "Phosphene"),
}


def changes(corpus):
    """Yield (key, record id, field, old value, new value) for every fix still needed."""
    for key in TITLES + list(PLACEHOLDERS):
        rec = corpus["nime:" + key]
        rid = rec["doi"].rsplit(".", 1)[-1]
        meta = requests.get(f"{API}/{rid}", headers=RDM, timeout=60).json()["metadata"]
        if key in TITLES:
            if meta["title"] != rec["title"]:
                yield key, rid, "title", meta["title"], rec["title"]
        else:
            old, new = PLACEHOLDERS[key]
            desc = meta.get("description", "")
            if desc.count(old) == 1:
                yield key, rid, "description", desc, desc.replace(old, new)
            elif old in desc:
                raise SystemExit(f"{key}: '{old}' occurs {desc.count(old)} times; fix by hand")


def apply(rid, field, new, token):
    s = requests.Session()
    s.headers.update({"Authorization": f"Bearer {token}", "Content-Type": "application/json", **RDM})
    r = s.post(f"{API}/{rid}/draft", timeout=60)
    r.raise_for_status()
    draft = r.json()
    draft["metadata"][field] = new
    r = s.put(f"{API}/{rid}/draft", data=json.dumps(draft), timeout=60)
    r.raise_for_status()
    if r.json().get("errors"):
        raise SystemExit(f"{rid}: draft not valid: {r.json()['errors']}")
    r = s.post(f"{API}/{rid}/draft/actions/publish", timeout=60)
    r.raise_for_status()
    return requests.get(f"{API}/{rid}", headers=RDM, timeout=60).json()["metadata"][field] == new


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true")
    p.add_argument("--token-file")
    p.add_argument("--only")
    a = p.parse_args()
    corpus = {r["id"]: r for r in json.loads((HERE / "data" / "corpus.json").read_text())}
    token = Path(a.token_file).expanduser().read_text().strip() if a.apply else None
    for key, rid, field, old, new in changes(corpus):
        if a.only and key != a.only:
            continue
        if field == "title":
            print(f"{key} ({rid}) title:\n  - {old}\n  + {new}")
        else:
            i = next(j for j in range(len(old)) if old[j] != new[j])
            print(f"{key} ({rid}) description:\n  - ...{old[max(0, i - 40):i + 40]}...\n"
                  f"  + ...{new[max(0, i - 40):i + 60]}...")
        if a.apply:
            print("  published, verified" if apply(rid, field, new, token) else "  NOT VERIFIED")


if __name__ == "__main__":
    main()
