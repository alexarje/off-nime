"""Apply hand decisions to the rule-selected bibs, after the rules have rebuilt them.

The rules rebuild bibs/{Cited,Background,Theses,Related,Historical,Zotero} on every run, so a
decision made by reading an entry is kept in tools/hand.tsv and applied here each time. Columns:
key, action, field, value, reason.
- remove: the entry is dropped.
- move: the entry goes to the dataset named in value (Cited or Background), with its key prefix
  and collection field changed.
- set: field is set to value (an empty value removes the field).
A move or set whose key is no longer in any bib (the rules no longer select it, or its key
changed) is listed as unmatched, so it can be checked. Writes data/hand_stats.json.
"""
import csv
import json
import re
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
BIBS = HERE.parent / "bibs"
NAMES = ("Cited", "Background", "Theses", "Related", "Historical", "Zotero")


def entries(text):
    """Split a bib file into (key, entry text) pairs, keeping each entry as written."""
    out = []
    for chunk in re.split(r"\n(?=@)", "\n" + text):
        m = re.match(r"@\w+\{([^,]+),", chunk)
        if m:
            out.append([m.group(1), chunk.strip() + "\n"])
    return out


def set_field(entry, field, value):
    """Every field is on its own line, as the builders write it."""
    lines = entry.strip().split("\n")
    fields = [l.rstrip(",") for l in lines[1:-1] if not l.startswith(f"  {field} = {{")]
    if value:
        fields.append(f"  {field} = {{{value}}}")
    return "\n".join([lines[0], ",\n".join(fields), lines[-1]]) + "\n"


def main():
    rows = list(csv.DictReader(open(HERE / "tools" / "hand.tsv"), delimiter="\t"))
    heads, bibs = {}, {}
    for n in NAMES:
        f = BIBS / n / f"{n.lower()}.bib"
        text = f.read_text() if f.exists() else ""
        heads[n] = re.match(r"(?:%.*\n|\s*\n)*", text).group(0)
        bibs[n] = entries(text)
    where = {k: n for n, es in bibs.items() for k, _ in es}
    done, unmatched = Counter(), []
    for r in rows:
        k, act = r["key"], r["action"]
        n = where.get(k)
        if act == "move":
            target = r["value"]
            new = f"{target.lower()}:{k.split(':', 1)[1]}"
            if n is None and where.get(new) == target:
                continue
        if n is None:
            if act == "remove":
                done["already absent"] += 1
            else:
                unmatched.append(k)
            continue
        i = next(i for i, (key, _) in enumerate(bibs[n]) if key == k)
        if act == "remove":
            bibs[n].pop(i)
            where.pop(k)
        elif act == "set":
            bibs[n][i][1] = set_field(bibs[n][i][1], r["field"], r["value"])
        elif act == "move":
            _, e = bibs[n].pop(i)
            e = set_field(e.replace("{" + k + ",", "{" + new + ",", 1), "collection", target)
            bibs[target].append([new, e])
            where.pop(k)
            where[new] = target
        done[f"{act} {n}"] += 1
    for n in NAMES:
        f = BIBS / n / f"{n.lower()}.bib"
        if f.exists():
            f.write_text(heads[n] + "\n".join(e for _, e in bibs[n]) + ("\n" if bibs[n] else ""))
    stats = {"decisions": len(rows), "applied": dict(done), "unmatched": unmatched}
    (HERE / "data" / "hand_stats.json").write_text(json.dumps(stats, indent=1))
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
