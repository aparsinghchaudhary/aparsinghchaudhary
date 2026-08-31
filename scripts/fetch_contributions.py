#!/usr/bin/env python3
"""Fetch a GitHub user's public contribution calendar without an API key.

Scrapes https://github.com/users/<username>/contributions, computes
total/streak/best-day metrics, and writes data/contributions.json.

Usage:
    python scripts/fetch_contributions.py --username YOUR_GITHUB_USERNAME
"""
from __future__ import annotations

import argparse
import json
import re
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

    found: dict[str, dict] = {}
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
        raise RuntimeError(
            "No contribution cells found. GitHub may have changed its markup, "
            "or the username has no public activity."
        )

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
    ap.add_argument("--username", required=True, help="GitHub username")
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
    print(f"Saved {OUT} ({data['total_contributions']} total contributions)")


if __name__ == "__main__":
    main()
