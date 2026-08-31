from pathlib import Path
import textwrap, zipfile

root = Path("/mnt/data/github-profile-cipher")
for d in ["scripts", ".github/workflows", "data", "assets"]:
    (root / d).mkdir(parents=True, exist_ok=True)

files = {}

files["scripts/prep_photo.py"] = r'''#!/usr/bin/env python3
"""Prepare a portrait for GitHub profile artwork.

Usage:
    python scripts/prep_photo.py hero.png
"""
from __future__ import annotations
import argparse
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageEnhance
from rembg import remove


def clahe_rgb(img: Image.Image) -> Image.Image:
    arr = np.asarray(img.convert("RGB"))
    lab = cv2.cvtColor(arr, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(l)
    return Image.fromarray(cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2RGB))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("-o", "--output", type=Path, default=Path("source-prepped.png"))
    ap.add_argument("--size", type=int, default=900)
    args = ap.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Input not found: {args.input}")

    with Image.open(args.input) as src:
        src = src.convert("RGBA")
        cutout = remove(src)
        bbox = cutout.getbbox()
        if bbox:
            cutout = cutout.crop(bbox)

        cutout.thumbnail((args.size - 60, args.size - 60), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (args.size, args.size), (0, 0, 0, 0))
        canvas.alpha_composite(cutout, ((args.size-cutout.width)//2, (args.size-cutout.height)//2))

        rgb = clahe_rgb(canvas.convert("RGB"))
        rgb = ImageEnhance.Contrast(rgb).enhance(1.12)
        rgb = ImageEnhance.Sharpness(rgb).enhance(1.08)
        final = rgb.convert("RGBA")
        final.putalpha(canvas.getchannel("A"))
        final.save(args.output, "PNG", optimize=True)

    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
'''

files["scripts/make_ascii_svg.py"] = r'''#!/usr/bin/env python3
"""Generate an animated gold ASCII portrait from source-prepped.png."""
from __future__ import annotations
from pathlib import Path
from xml.sax.saxutils import escape
from PIL import Image, ImageOps

INPUT = Path("source-prepped.png")
OUTPUT = Path("hxni-ascii.svg")
RAMP = " .`:-=+*cs#%@"
COLS, ROWS = 82, 46
FG, BG = "#D4AF37", "#0d0d0d"


def build_ascii(path: Path) -> list[str]:
    with Image.open(path) as im:
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (0, 0, 0, 255))
        bg.alpha_composite(im)
        gray = ImageOps.grayscale(bg).resize((COLS, ROWS), Image.Resampling.LANCZOS)
        px = list(gray.getdata())
        return [
            "".join(RAMP[p * (len(RAMP)-1) // 255] for p in px[y*COLS:(y+1)*COLS]).rstrip()
            for y in range(ROWS)
        ]


def render(lines: list[str]) -> str:
    width, line_h, top = 720, 15, 34
    height = top + ROWS * line_h + 20
    texts = []
    for i, line in enumerate(lines):
        delay = i * 0.035
        y = top + i * line_h
        texts.append(
            f'<text x="20" y="{y}" class="ascii" style="animation-delay:{delay:.3f}s">'
            f'{escape(line)}</text>'
        )

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<defs>
  <clipPath id="wipe"><rect x="0" y="0" width="0" height="{height}">
    <animate attributeName="width" from="0" to="{width}" dur="2.8s" fill="freeze"/>
  </rect></clipPath>
  <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="1.2" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <style>
    .ascii {{ font: 12px monospace; fill: {FG}; letter-spacing: .5px; opacity: 0;
              animation: fin .55s ease forwards; }}
    .frame {{ fill: {BG}; stroke: #3b3320; stroke-width: 2; }}
    @keyframes fin {{
      from {{ opacity: 0; transform: translateX(-5px); }}
      to {{ opacity: 1; transform: translateX(0); }}
    }}
  </style>
</defs>
<rect class="frame" x="1" y="1" width="{width-2}" height="{height-2}" rx="18"/>
<g clip-path="url(#wipe)" filter="url(#glow)">
{''.join(texts)}
</g>
</svg>'''


def main() -> None:
    if not INPUT.exists():
        raise SystemExit("source-prepped.png not found. Run: python scripts/prep_photo.py hero.png")
    OUTPUT.write_text(render(build_ascii(INPUT)), encoding="utf-8")
    print(f"Saved {OUTPUT}")


if __name__ == "__main__":
    main()
'''

files["scripts/make_info_card.py"] = r'''#!/usr/bin/env python3
"""Generate the Cipher Stack terminal info card."""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path("info-card.svg")
WIDTH, HEIGHT = 760, 520

INFO = [
    ("OS", "Windows / Linux"),
    ("Host", "Nepal • NPT (UTC+5:45)"),
    ("Role", "Full-Stack Web Developer"),
    ("Stack", "React • Next.js • Node.js • PHP • Laravel"),
    ("DB", "MySQL • Firebase • Supabase"),
    ("Tools", "Git • GitHub • VS Code • Postman • Vercel"),
    ("Social", "github.com/aparsinghchaudhary"),
    ("Web", "YOUR_PORTFOLIO_URL"),
    ("GitHub", "github.com/aparsinghchaudhary"),
]


def make_svg() -> str:
    rows = []
    for i, (key, value) in enumerate(INFO):
        y = 112 + i * 38
        delay = 0.25 + i * 0.12
        rows.append(
            f'<text x="40" y="{y}" class="key" style="animation-delay:{delay:.2f}s">{escape(key)}</text>'
            f'<text x="175" y="{y}" class="value" style="animation-delay:{delay:.2f}s">: {escape(value)}</text>'
        )

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
<defs>
<style>
.bg{{fill:#0d0d0d;stroke:#3b3320;stroke-width:2}}
.title{{font:bold 22px monospace;fill:#e8e8e8}}
.key{{font:bold 17px monospace;fill:#D4AF37;opacity:0;animation:fade .65s ease forwards}}
.value{{font:17px monospace;fill:#c9c9c9;opacity:0;animation:fade .65s ease forwards}}
@keyframes fade{{from{{opacity:0;transform:translateY(7px)}}to{{opacity:1;transform:translateY(0)}}}}
</style>
</defs>
<rect class="bg" x="1" y="1" width="{WIDTH-2}" height="{HEIGHT-2}" rx="18"/>
<circle cx="28" cy="28" r="6" fill="#ff5f56"/>
<circle cx="50" cy="28" r="6" fill="#ffbd2e"/>
<circle cx="72" cy="28" r="6" fill="#27c93f"/>
<text x="105" y="35" class="title">The Cipher Stack</text>
<line x1="32" y1="58" x2="{WIDTH-32}" y2="58" stroke="#3b3320"/>
{''.join(rows)}
</svg>'''


def main() -> None:
    OUT.write_text(make_svg(), encoding="utf-8")
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
'''

files["scripts/fetch_contributions.py"] = r'''#!/usr/bin/env python3
"""Fetch GitHub's public contribution calendar without an API key."""
from __future__ import annotations
import argparse, json, re
from datetime import date, datetime, timedelta
from pathlib import Path
import requests
from bs4 import BeautifulSoup

OUT = Path("data/contributions.json")
UA = "Mozilla/5.0 (compatible; GitHubProfileArt/1.0)"


def parse_count(text: str) -> int:
    m = re.search(r"([\d,]+)\s+contribution", text, re.I)
    return int(m.group(1).replace(",", "")) if m else 0


def fetch(username: str) -> list[dict]:
    url = f"https://github.com/users/{username}/contributions"
    r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    found = {}
    for cell in soup.select("td[data-date]"):
        d = cell.get("data-date")
        if not d:
            continue
        try:
            level = int(cell.get("data-level", "0"))
        except ValueError:
            level = 0
        tip = cell.find("tool-tip") or cell.find("span", class_="sr-only")
        text = tip.get_text(" ", strip=True) if tip else cell.get_text(" ", strip=True)
        found[d] = {"date": d, "count": parse_count(text), "level": level}
    return sorted(found.values(), key=lambda x: x["date"])


def calculate(days: list[dict]) -> dict:
    if not days:
        raise RuntimeError("No contribution cells found; GitHub may have changed its HTML.")
    counts = {date.fromisoformat(x["date"]): x["count"] for x in days}
    total = sum(counts.values())
    best = max(days, key=lambda x: x["count"])

    longest = run = 0
    prev = None
    for d in sorted(counts):
        if counts[d] > 0 and prev == d - timedelta(days=1):
            run += 1
        elif counts[d] > 0:
            run = 1
        else:
            run = 0
        longest = max(longest, run)
        prev = d

    anchor = min((d for d in counts if d <= date.today()), default=max(counts))
    current = 0
    d = anchor
    while counts.get(d, 0) > 0:
        current += 1
        d -= timedelta(days=1)

    return {
        "total_contributions": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "days": days,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--username", default="aparsinghchaudhary")
    args = ap.parse_args()
    days = fetch(args.username)
    data = {
        "username": args.username,
        "source": f"https://github.com/users/{args.username}/contributions",
        "updated_at": datetime.utcnow().isoformat() + "Z",
        **calculate(days),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
'''

files["scripts/render_heatmap_svg.py"] = r'''#!/usr/bin/env python3
"""Render a self-contained custom GitHub contribution heatmap."""
from __future__ import annotations
import datetime as dt
import json
from pathlib import Path

DATA = Path("data/contributions.json")
OUT = Path("contrib-heatmap.svg")
BG, BORDER, TEXT, GOLD = "#0d0d0d", "#3b3320", "#c9c9c9", "#D4AF37"
LEVELS = ["#161616", "#3b3216", "#67551d", "#9a7b25", "#D4AF37"]


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    days = data["days"]
    first = dt.date.fromisoformat(days[0]["date"])
    offset = (first.weekday() + 1) % 7
    cell, gap = 13, 4
    cells = []

    for i, x in enumerate(days):
        idx = offset + i
        col, row = idx // 7, idx % 7
        px, py = 50 + col * (cell + gap), 45 + row * (cell + gap)
        level = max(0, min(4, int(x.get("level", 0))))
        cells.append(
            f'<rect x="{px}" y="{py}" width="{cell}" height="{cell}" rx="3" fill="{LEVELS[level]}">'
            f'<title>{x["date"]}: {x["count"]} contributions</title></rect>'
        )

    width, height = 1120, 235
    legend = "".join(
        f'<rect x="{115+i*20}" y="181" width="13" height="13" rx="3" fill="{c}"/>'
        for i, c in enumerate(LEVELS)
    )
    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect x="1" y="1" width="{width-2}" height="{height-2}" rx="18" fill="{BG}" stroke="{BORDER}" stroke-width="2"/>
<text x="28" y="28" font-family="monospace" font-size="14" fill="{GOLD}">CONTRIBUTION MATRIX</text>
<text x="430" y="28" font-family="monospace" font-size="13" fill="{TEXT}">
Total: {data["total_contributions"]} • Streak: {data["current_streak"]} • Best: {data["best_day"]["count"]}
</text>
{''.join(cells)}
<text x="50" y="190" font-family="monospace" font-size="12" fill="{TEXT}">Less</text>
{legend}
<text x="225" y="190" font-family="monospace" font-size="12" fill="{TEXT}">More</text>
</svg>'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"Saved {OUT}")


if __name__ == "__main__":
    main()
'''

files["scripts/requirements.txt"] = """requests
beautifulsoup4
pillow
numpy
opencv-python-headless
rembg[cpu]
"""
files["scripts/requirements-ci.txt"] = """requests
beautifulsoup4
"""

files[".github/workflows/update-profile-art.yml"] = r'''name: Update profile art

on:
  schedule:
    - cron: "17 6 * * *"
  workflow_dispatch:

permissions:
  contents: write

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip

      - name: Install lightweight CI dependencies
        run: python -m pip install -r scripts/requirements-ci.txt

      - name: Fetch contributions
        run: python scripts/fetch_contributions.py --username aparsinghchaudhary

      - name: Render heatmap
        run: python scripts/render_heatmap_svg.py

      - name: Commit and push
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add contrib-heatmap.svg data/contributions.json
          git diff --cached --quiet || git commit -m "chore: update profile art [skip ci]"
          git push
'''

files["README.md"] = r'''<div align="center">

<h1><code>APAR SINGH CHAUDHARY</code></h1>
<h3><code>Full-Stack Web Developer • React • Node.js • PHP • Laravel</code></h3>

</div>

<h3><code>The Cipher Stack</code></h3>

<table>
<tr>
<td width="42%" valign="top">
<img src="./hxni-ascii.svg" width="370" alt="Animated ASCII portrait" />
</td>
<td width="58%" valign="top">
<img src="./info-card.svg" width="490" alt="The Cipher Stack terminal card" />
</td>
</tr>
</table>

---

<div align="center">

<img src="https://komarev.com/ghpvc/?username=aparsinghchaudhary&style=for-the-badge&label=PROFILE+VIEWS" alt="Profile views" />
<img src="https://img.shields.io/badge/OPEN%20TO%20WORK-D4AF37?style=for-the-badge&logo=github&logoColor=0d0d0d" alt="Open to work" />
<img src="https://img.shields.io/badge/LOCATION-Nepal%20%7C%20NPT%20UTC%2B5%3A45-D4AF37?style=for-the-badge&logoColor=0d0d0d" alt="Location" />

<br><br>

<img src="https://capsule-render.vercel.app/api?type=venom&color=0:0d0d0d,100:D4AF37&height=180&section=header&text=THE%20CIPHER%20STACK&fontColor=D4AF37&fontSize=38&animation=fadeIn" width="100%" alt="Cinematic header" />

<img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=20&duration=3000&pause=900&color=D4AF37&center=true&vCenter=true&width=900&lines=I+build+fast%2C+scalable+web+experiences.;React+%2B+Node.js+%2B+PHP+%2B+Laravel.;Turning+ideas+into+production-ready+products.;Clean+architecture.+Sharp+UI.+Reliable+systems." alt="Typing developer quotes" />

</div>

---

<h3><code>Contributions</code></h3>

<div align="center">
<img src="./contrib-heatmap.svg" width="860" alt="Custom GitHub contribution heatmap" />
</div>

---

<h3><code>Featured Projects</code></h3>

<table>
<tr>
<td width="50%" valign="top">

### 🛍️ Bhauka — Tharu Culture Attire
Cultural e-commerce platform for showcasing and selling traditional Tharu attire.

**Stack:** PHP • MySQL • JavaScript

[View Project](YOUR_PROJECT_1_URL)

</td>
<td width="50%" valign="top">

### 🎓 Academic Management System
Role-based student, teacher, assignment, notices and results management platform.

**Stack:** Laravel • MySQL • Bootstrap

[View Project](YOUR_PROJECT_2_URL)

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 🏫 School / Education Web Portal
Modern education website with news, events, notices, galleries and downloads.

**Stack:** PHP • MySQL • JavaScript

[View Project](YOUR_PROJECT_3_URL)

</td>
<td width="50%" valign="top">

### ⚡ Full-Stack Web Apps
Dashboards, APIs, authentication, payments and database-driven applications.

**Stack:** React • Node.js • PHP • Laravel

[View Project](YOUR_PROJECT_4_URL)

</td>
</tr>
</table>

---

<h3><code>Tech Arsenal</code></h3>

**Frontend / 3D**

<p><img src="https://skillicons.dev/icons?i=html,css,js,react,nextjs,typescript,vite,tailwind,threejs,framer" /></p>

**Backend / Database**

<p><img src="https://skillicons.dev/icons?i=nodejs,express,php,laravel,python,mysql,supabase,firebase" /></p>

**Mobile**

<p><img src="https://skillicons.dev/icons?i=react,flutter,dart" /></p>

**Tools / DevOps**

<p><img src="https://skillicons.dev/icons?i=git,github,vscode,postman,vercel,netlify,npm,linux" /></p>

---

<h3><code>What I'm Up To</code></h3>

| Signal | Current State |
|---|---|
| 🔨 Building | Production-ready full-stack web applications and e-commerce systems |
| 🧠 Learning | Advanced React / Next.js architecture, APIs, security and cloud deployment |
| 🎨 Exploring | Cinematic UI, animation, SVG graphics and interactive experiences |
| ⚡ Fun Fact | I enjoy turning complex requirements into simple, usable interfaces |

---

<h3><code>Achievements</code></h3>

<div align="center">
<img src="https://github-profile-trophy.vercel.app/?username=aparsinghchaudhary&theme=darkhub&no-frame=true&margin-w=10&row=1&column=4" alt="GitHub achievements" />
</div>

---

<h3><code>Socials</code></h3>

<div align="center">

<a href="YOUR_LINKEDIN_URL"><img src="https://img.shields.io/badge/LinkedIn-D4AF37?style=for-the-badge&logo=linkedin&logoColor=0d0d0d" /></a>
<a href="YOUR_INSTAGRAM_URL"><img src="https://img.shields.io/badge/Instagram-D4AF37?style=for-the-badge&logo=instagram&logoColor=0d0d0d" /></a>
<a href="YOUR_FACEBOOK_URL"><img src="https://img.shields.io/badge/Facebook-D4AF37?style=for-the-badge&logo=facebook&logoColor=0d0d0d" /></a>
<a href="mailto:YOUR_EMAIL"><img src="https://img.shields.io/badge/Gmail-D4AF37?style=for-the-badge&logo=gmail&logoColor=0d0d0d" /></a>
<a href="https://github.com/aparsinghchaudhary"><img src="https://img.shields.io/badge/GitHub-D4AF37?style=for-the-badge&logo=github&logoColor=0d0d0d" /></a>
<a href="YOUR_PORTFOLIO_URL"><img src="https://img.shields.io/badge/Portfolio-D4AF37?style=for-the-badge&logo=vercel&logoColor=0d0d0d" /></a>

<br><br>

<img src="https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=YOUR_PORTFOLIO_URL" width="150" alt="Portfolio QR code" />

</div>

---

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:D4AF37,100:0d0d0d&height=120&section=footer" width="100%" alt="Footer wave" />
<sub><code>Built with code, curiosity &amp; caffeine.</code></sub>
</div>
'''

files["SETUP.md"] = r'''# Cipher Stack Profile Setup

The repository is configured for the GitHub username `aparsinghchaudhary`.

## Local photo pipeline

Add your actual portrait as `hero.png` in the repository root, then:

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
python -m pip install -r scripts/requirements.txt
python scripts/prep_photo.py hero.png
python scripts/make_ascii_svg.py
python scripts/make_info_card.py
python scripts/fetch_contributions.py --username aparsinghchaudhary
python scripts/render_heatmap_svg.py
