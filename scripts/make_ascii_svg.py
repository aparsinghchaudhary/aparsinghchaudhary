#!/usr/bin/env python3
"""Convert source-prepped.png into an animated gold ASCII-art SVG portrait.

Reads:  source-prepped.png
Writes: hxni-ascii.svg
"""
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageOps

INPUT = Path("source-prepped.png")
OUTPUT = Path("hxni-ascii.svg")

# Brightness -> character density ramp (dark to light)
RAMP = " .`:-=+*cs#%@"
COLS, ROWS = 82, 46
FG = "#D4AF37"   # gold
BG = "#0d0d0d"   # near-black terminal background
BORDER = "#3b3320"


def build_ascii(path: Path) -> list[str]:
    with Image.open(path) as im:
        im = im.convert("RGBA")
        # Flatten transparency onto the terminal background color so
        # cutout edges read cleanly as ASCII rather than noise.
        flat = Image.new("RGBA", im.size, (13, 13, 13, 255))
        flat.alpha_composite(im)

        gray = ImageOps.grayscale(flat).resize((COLS, ROWS), Image.Resampling.LANCZOS)
        px = list(gray.getdata())

        lines = []
        for y in range(ROWS):
            row_px = px[y * COLS:(y + 1) * COLS]
            row = "".join(RAMP[p * (len(RAMP) - 1) // 255] for p in row_px)
            lines.append(row.rstrip() or " ")
        return lines


def render(lines: list[str]) -> str:
    width = 720
    line_h = 15
    top = 34
    height = top + ROWS * line_h + 20

    texts = []
    for i, line in enumerate(lines):
        delay = i * 0.035
        y = top + i * line_h
        texts.append(
            f'<text x="20" y="{y}" class="ascii" '
            f'style="animation-delay:{delay:.3f}s">{escape(line)}</text>'
        )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<defs>
  <clipPath id="wipe">
    <rect x="0" y="0" width="0" height="{height}">
      <animate attributeName="width" from="0" to="{width}" dur="2.8s" fill="freeze"/>
    </rect>
  </clipPath>
  <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="1.2" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <style>
    .ascii {{
      font: 12px "SFMono-Regular", "Consolas", monospace;
      fill: {FG};
      letter-spacing: .5px;
      opacity: 0;
      animation: fin .55s ease forwards;
    }}
    .frame {{ fill: {BG}; stroke: {BORDER}; stroke-width: 2; }}
    @keyframes fin {{
      from {{ opacity: 0; transform: translateX(-5px); }}
      to   {{ opacity: 1; transform: translateX(0); }}
    }}
  </style>
</defs>
<rect class="frame" x="1" y="1" width="{width - 2}" height="{height - 2}" rx="18"/>
<g clip-path="url(#wipe)" filter="url(#glow)">
{''.join(texts)}
</g>
</svg>"""


def main() -> None:
    if not INPUT.exists():
        raise SystemExit(
            "source-prepped.png not found. Run: python scripts/prep_photo.py hero.png"
        )
    OUTPUT.write_text(render(build_ascii(INPUT)), encoding="utf-8")
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()
