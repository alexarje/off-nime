"""Draw the TRL against ARL heatmap as a static SVG for the report (output/trl_arl_heatmap.svg).

Two panels: all estimated entries, and the NIME papers. Cells are shaded on one blue ramp by the
square root of the count (so that small cells stay visible), with the count printed in cells
that hold at least 2% of the panel's entries.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
LO, HI = (0xcd, 0xe2, 0xfb), (0x0d, 0x36, 0x6b)


def shade(t):
    return "#" + "".join(f"{round(a + (b - a) * t):02x}" for a, b in zip(LO, HI))


def panel(m, x0, title):
    cw, rh, lw, top = 40, 26, 150, 66
    cols, rows = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0], [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    total = sum(m[a][t] for a in rows for t in cols)
    mx = max(m[a][t] for a in rows for t in cols) or 1
    out = [f'<text x="{x0 + lw}" y="20" font-weight="600" fill="#0b0b0b">{title} ({total} entries)</text>',
           f'<text x="{x0 + lw + 5 * cw}" y="38" text-anchor="middle" fill="#52514e">Technology readiness level (TRL)</text>']
    for c, t in enumerate(cols):
        out.append(f'<text x="{x0 + lw + c * cw + cw / 2}" y="{top - 2}" text-anchor="middle" fill="#52514e">{t or "none"}</text>')
    for r, a in enumerate(rows):
        y = top + 4 + r * rh
        out.append(f'<text x="{x0 + lw - 8}" y="{y + rh / 2 + 4}" text-anchor="end" fill="#52514e">ARL {a or "none"}</text>')
        for c, t in enumerate(cols):
            v = m[a][t]
            x = x0 + lw + c * cw
            fill = shade((v / mx) ** 0.5) if v else "#f5f4f0"
            out.append(f'<rect x="{x + 1}" y="{y + 1}" width="{cw - 2}" height="{rh - 2}" rx="2" fill="{fill}"/>')
            if v and v / total >= 0.02:
                ink = "#ffffff" if (v / mx) ** 0.5 > 0.55 else "#0b0b0b"
                out.append(f'<text x="{x + cw / 2}" y="{y + rh / 2 + 4}" text-anchor="middle" fill="{ink}">{v}</text>')
    for k in (3, 6):
        xk = x0 + lw + k * cw
        yk = top + 4 + (9 - k) * rh
        out.append(f'<line x1="{xk}" x2="{xk}" y1="{top + 4}" y2="{top + 4 + 9 * rh}" stroke="#7a7974" stroke-dasharray="3 3"/>')
        out.append(f'<line x1="{x0 + lw}" x2="{x0 + lw + 9 * cw}" y1="{yk}" y2="{yk}" stroke="#7a7974" stroke-dasharray="3 3"/>')
    return out


def main():
    est = json.loads((HERE / "data" / "trl.json").read_text())

    def matrix(keep):
        m = [[0] * 10 for _ in range(10)]
        for x in est:
            if keep(x):
                m[x["arl"] or 0][x["trl"] or 0] += 1
        return m
    w = 2 * 580
    body = panel(matrix(lambda x: True), 0, "All entries") + \
        panel(matrix(lambda x: x["dataset"] in ("NIME papers", "NIME alt")), 580, "NIME papers")
    note = ('<text x="150" y="364" fill="#52514e">Dashed lines separate the bands: TRL fundamental 1–3, applied 4–6, '
            'industrial 7–9; ARL exploration 1–3, development 4–6, dissemination 7–9. Estimates by language-model agents.</text>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="376" viewBox="0 0 {w} 376" '
           f'font-family="system-ui, sans-serif" font-size="12"><rect width="{w}" height="376" fill="#fcfcfb"/>'
           + "".join(body) + note + "</svg>")
    (HERE / "output" / "trl_arl_heatmap.svg").write_text(svg)
    print("output/trl_arl_heatmap.svg")


if __name__ == "__main__":
    main()
