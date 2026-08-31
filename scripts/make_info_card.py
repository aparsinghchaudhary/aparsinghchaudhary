#!/usr/bin/env python3
"""Generate info-card.svg — a neofetch-style terminal card.

All the display values live in the CONFIG dict below. Edit it once with
your real details, then re-run this script whenever something changes.

Writes: info-card.svg
"""
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path("info-card.svg")
WIDTH, HEIGHT = 760, 520

BG = "#0d0d0d"
BORDER = "#3b3320"
KEY_COLOR = "#D4AF37"   # gold
VALUE_COLOR = "#c9c9c9"  # silver
TITLE_COLOR = "#e8e8e8"

# ---- EDIT THESE ----------------------------------------------------------
CONFIG = {
    "title": "The Cipher Stack",
    "OS": "[YOUR_OS]",
    "Host": "[YOUR_LOCATION] (e.g. Kathmandu, Nepal | NPT UTC+5:45)",
    "Role": "[YOUR_TITLE] (e.g. Full-Stack Web Developer)",
    "Stack": "[e.g. React, Node.js, PHP, Laravel]",
    "DB": "[e.g. MySQL, Firebase, Supabase]",
    "Tools": "[e.g. Git, GitHub, VS Code, Postman, Vercel]",
    "Social": "[YOUR_LINKEDIN_URL]",
    "Web": "[YOUR_PORTFOLIO_URL]",
    "GitHub": "github.com/[YOUR_GITHUB_USERNAME]",
}
# ---------------------------------------------------------------------------

ROWS = [(k, v) for k, v in CONFIG.items() if k != "title"]


def make_svg() -> str:
    rows_svg = []
    for i, (key, value) in enumerate(ROWS):
        y = 112 + i * 38
        delay = 0.25 + i * 0.12
        rows_svg.append(
            f'<text x="40" y="{y}" class="key" '
            f'style="animation-delay:{delay:.2f}s">{escape(key)}</text>'
            f'<text x="175" y="{y}" class="value" '
            f'style="animation-delay:{delay:.2f}s">: {escape(value)}</text>'
        )

    title = escape(CONFIG["title"])

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
<defs>
<style>
  .bg {{ fill: {BG}; stroke: {BORDER}; stroke-width: 2; }}
  .title {{ font: bold 22px monospace; fill: {TITLE_COLOR}; }}
  .key {{ font: bold 17px monospace; fill: {KEY_COLOR}; opacity: 0; animation: fade .65s ease forwards; }}
  .value {{ font: 17px monospace; fill: {VALUE_COLOR}; opacity: 0; animation: fade .65s ease forwards; }}
  @keyframes fade {{
    from {{ opacity: 0; transform: translateY(7px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
  }}
</style>
</defs>
<rect class="bg" x="1" y="1" width="{WIDTH - 2}" height="{HEIGHT - 2}" rx="18"/>
<circle cx="28" cy="28" r="6" fill="#ff5f56"/>
<circle cx="50" cy="28" r="6" fill="#ffbd2e"/>
<circle cx="72" cy="28" r="6" fill="#27c93f"/>
<text x="105" y="35" class="title">{title}</text>
<line x1="32" y1="58" x2="{WIDTH - 32}" y2="58" stroke="{BORDER}"/>
{''.join(rows_svg)}
</svg>"""


def main() -> None:
    OUT.write_text(make_svg(), encoding="utf-8")
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
