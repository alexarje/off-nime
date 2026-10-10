"""Merge and check the TRL and ARL estimates (data/trl/out_*.jsonl, made with tools/trl_rubric.md).

Checks that can fail: every input id has exactly one estimate, levels lie in 1–9, bands agree with
levels; and three expectations from the rubric itself: concert and installation entries should
mostly reach ARL 7 or more, Background works should mostly sit at TRL 1–3, and papers with no
artistic component should have no ARL. Writes data/trl.json, output/trl_arl.tsv,
data/trl_stats.json and output/trl_validation_sheet.tsv (30 random publications for a human to
label, which is how agreement is measured).
"""
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
D = HERE / "data" / "trl"
TRL_BAND = {1: "fundamental", 2: "fundamental", 3: "fundamental", 4: "applied", 5: "applied", 6: "applied",
            7: "industrial", 8: "industrial", 9: "industrial"}
ARL_BAND = {1: "exploration", 2: "exploration", 3: "exploration", 4: "development", 5: "development",
            6: "development", 7: "dissemination", 8: "dissemination", 9: "dissemination"}


def level(v):
    try:
        v = int(v)
        return v if 1 <= v <= 9 else None
    except (TypeError, ValueError):
        return None


def main():
    inputs, outputs, problems = [], {}, Counter()
    for f in sorted(D.glob("in_*.jsonl")):
        inputs += [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
        o = D / f.name.replace("in_", "out_")
        if not o.exists():
            problems["missing batch"] += 1
            continue
        for l in o.read_text().splitlines():
            if not l.strip():
                continue
            try:
                x = json.loads(l)
            except json.JSONDecodeError:
                problems["unparseable line"] += 1
                continue
            if x.get("id") in outputs:
                problems["duplicate id"] += 1
            outputs[x.get("id")] = x
    merged = []
    for it in inputs:
        x = outputs.get(it["id"])
        if not x:
            problems["no estimate"] += 1
            continue
        t, a = level(x.get("trl")), level(x.get("arl"))
        if x.get("trl") is not None and t is None:
            problems["trl out of range"] += 1
        if t and x.get("trl_band") != TRL_BAND[t]:
            problems["trl band corrected"] += 1
        if a and x.get("arl_band") != ARL_BAND[a]:
            problems["arl band corrected"] += 1
        merged.append(dict(it, trl=t, trl_band=TRL_BAND.get(t), arl=a, arl_band=ARL_BAND.get(a),
                           confidence=x.get("confidence"), reason=x.get("reason", ""),
                           basis="abstract" if len(it.get("abstract") or "") > 80 else "title"))
    by = defaultdict(list)
    for m in merged:
        by[m["dataset"]].append(m)
    art = by["NIME music"] + by["NIME installations"]
    checks = {
        "inputs": len(inputs), "estimates": len(merged), "problems": dict(problems),
        "artworks_arl_7_plus_pct": round(100 * sum((m["arl"] or 0) >= 7 for m in art) / max(len(art), 1), 1),
        "background_trl_1_3_pct": round(100 * sum((m["trl"] or 1) <= 3 for m in by["Background"]) / max(len(by["Background"]), 1), 1),
        "nime_papers_without_arl_pct": round(100 * sum(m["arl"] is None for m in by["NIME papers"]) / max(len(by["NIME papers"]), 1), 1),
    }
    dist = {ds: {"n": len(ms),
                 "trl_band": dict(Counter(m["trl_band"] or "none" for m in ms)),
                 "arl_band": dict(Counter(m["arl_band"] or "none" for m in ms)),
                 "trl_mean": round(sum(m["trl"] for m in ms if m["trl"]) / max(sum(1 for m in ms if m["trl"]), 1), 2),
                 "confidence": dict(Counter(m["confidence"] for m in ms))}
            for ds, ms in sorted(by.items())}
    periods = defaultdict(Counter)
    for m in merged:
        if m["dataset"] in ("NIME papers",) and m["year"]:
            periods[(int(m["year"]) // 5) * 5][m["trl_band"] or "none"] += 1
    stats = {"checks": checks, "by_dataset": dist,
             "nime_papers_trl_band_by_period": {str(k): dict(v) for k, v in sorted(periods.items())},
             "basis": dict(Counter(m["basis"] for m in merged))}
    (HERE / "data" / "trl.json").write_text(json.dumps(merged, ensure_ascii=False))
    (HERE / "data" / "trl_stats.json").write_text(json.dumps(stats, indent=1))
    with open(HERE / "output" / "trl_arl.tsv", "w") as f:
        f.write("id\tdataset\tyear\ttitle\ttrl\ttrl_band\tarl\tarl_band\tconfidence\tbasis\treason\n")
        for m in merged:
            f.write("\t".join(re.sub(r"\s+", " ", str(x if x is not None else "")) for x in
                              [m["id"], m["dataset"], m["year"], m["title"], m["trl"], m["trl_band"], m["arl"],
                               m["arl_band"], m["confidence"], m["basis"], m["reason"]]) + "\n")
    random.seed(10)
    sample = random.sample([m for m in merged if m["basis"] == "abstract"], 30)
    with open(HERE / "output" / "trl_validation_sheet.tsv", "w") as f:
        f.write("id\tdataset\tyear\ttitle\tabstract\tyour_trl\tyour_arl\n")
        for m in sample:
            f.write("\t".join(re.sub(r"\s+", " ", str(x)) for x in
                              [m["id"], m["dataset"], m["year"], m["title"], m["abstract"][:1200], "", ""]) + "\n")
    print(json.dumps(checks, indent=1))
    for ds, d in dist.items():
        print(ds, d["n"], d["trl_band"], d["arl_band"])


if __name__ == "__main__":
    main()
