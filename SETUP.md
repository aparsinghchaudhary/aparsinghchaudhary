# Cipher Stack Profile — Setup

## 1. Fill in your details
Before running anything, edit the placeholders:
- `README.md` — name, title, location, project links, socials, bio table
- `scripts/make_info_card.py` — the `CONFIG` dict at the top (OS, host, role, stack, links)
- `.github/workflows/update-profile-art.yml` — set the `GH_PROFILE_USERNAME` repository
  variable (Settings → Secrets and variables → Actions → Variables) to your GitHub username

## 2. Add your portrait
Drop a portrait photo in the repo root as `hero.png`.

## 3. Local run (one-time / whenever you update your photo or info)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
python -m pip install -r scripts/requirements.txt

python scripts/prep_photo.py hero.png
python scripts/make_ascii_svg.py
python scripts/make_info_card.py
python scripts/fetch_contributions.py --username YOUR_GITHUB_USERNAME
python scripts/render_heatmap_svg.py
```

This produces:
- `source-prepped.png` — background-removed, contrast-enhanced portrait
- `hxni-ascii.svg` — animated gold ASCII portrait
- `info-card.svg` — animated terminal info card
- `data/contributions.json` — scraped contribution calendar + streak metrics
- `contrib-heatmap.svg` — custom contribution heatmap

Commit and push all of these (including `hero.png` and `source-prepped.png` if you want them
versioned) to your **profile repository** — the one named exactly like your GitHub username.

## 4. Automate the heatmap
The workflow in `.github/workflows/update-profile-art.yml` re-runs the contribution
scrape + heatmap render daily at 06:17 UTC (and on manual dispatch), then commits the
result back with `[skip ci]` so it doesn't re-trigger itself. It intentionally does
**not** re-run the photo/ASCII steps — those only need to happen when your photo changes,
since `rembg` is too heavy for a lightweight CI job.

## Notes
- `rembg` downloads the U2Net model (~170MB) on first run — this only happens locally,
  never in CI, since the workflow uses `requirements-ci.txt` (just `requests` +
  `beautifulsoup4`).
- The contribution scraper reads GitHub's public calendar HTML directly — no token
  needed, but it depends on GitHub's markup staying stable. If GitHub changes their
  contribution graph markup, `fetch_contributions.py` will need small selector updates.
- All SVGs use CSS `@keyframes` (for opacity/wipe reveals) plus one SMIL `<animate>`
  (for the clip-path wipe), which GitHub's `<img>`-tag sandbox renders reliably.
