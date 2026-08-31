#!/usr/bin/env python3
"""Render a self-contained, theme-matched contribution heatmap SVG.

Reads:  data/contributions.json
Writes: contrib-heatmap.svg
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

DATA = Path("data/contributions.json")
OUT = Path("contrib-heatmap.svg")

BG = "#0d0d0d"
BORDER = "#3b3320"
TEXT = "#c9c9c9"
GOLD = "#D4AF37"
LEVELS = ["#161616", "#3b3216", "#67551d", "#9a7b25", "#D4AF37"]


def main() -> None:
    if not DATA.exists():
        raise SystemExit(
            "data/contributions.json not found. Run: "
            "python scripts/fetch_contributions.py --username YOUR_GITHUB_USERNAME"
        )

    data = json.loads(DATA.read_text(encoding="utf-8"))
    days = data["days"]
    first = dt.date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7  # align Sunday-first grid
    cell, gap = 13, 4
    cells = []

    for i, x in enumerate(days):
        idx = offset + i
        col, row = idx // 7, idx % 7
        px, py = 50 + col * (cell + gap), 45 + row * (cell + gap)
        level = max(0, min(4, int(x.get("level", 0))))
        cells.append(
            f'<rect x="{px}" y="{py}" width="{cell}" height="{cell}" rx="3" '
            f'fill="{LEVELS[level]}"><title>{x["date"]}: {x["count"]} contributions</title></rect>'
        )

    width = 50 + (offset + len(days)) // 7 * (cell + gap) + 40
    width = max(width, 1120)
    height = 235

    legend = "".join(
        f'<rect x="{115 + i * 20}" y="181" width="13" height="13" rx="3" fill="{c}"/>'
        for i, c in enumerate(LEVELS)
    )

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="18" fill="{BG}" stroke="{BORDER}" stroke-width="2"/>
<text x="28" y="28" font-family="monospace" font-size="14" fill="{GOLD}">CONTRIBUTION MATRIX</text>
<text x="430" y="28" font-family="monospace" font-size="13" fill="{TEXT}">
Total: {data["total_contributions"]} &#8226; Streak: {data["current_streak"]} &#8226; Best: {data["best_day"]["count"]}
</text>
{''.join(cells)}
<text x="50" y="190" font-family="monospace" font-size="12" fill="{TEXT}">Less</text>
{legend}
<text x="225" y="190" font-family="monospace" font-size="12" fill="{TEXT}">More</text>
</svg>"""

    OUT.write_text(svg, encoding="utf-8")
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
