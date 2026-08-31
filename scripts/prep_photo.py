#!/usr/bin/env python3
"""Prepare a portrait for GitHub profile artwork.

Removes the background with rembg (U2Net), enhances contrast with CLAHE,
crops to content, and centers the result on a square transparent canvas.

Usage:
    python scripts/prep_photo.py hero.png
    python scripts/prep_photo.py hero.png -o source-prepped.png --size 900
"""
from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageEnhance
from rembg import remove


def clahe_rgb(img: Image.Image) -> Image.Image:
    """Apply CLAHE contrast enhancement on the L channel of LAB color space."""
    arr = np.asarray(img.convert("RGB"))
    lab = cv2.cvtColor(arr, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(l)
    merged = cv2.merge((l, a, b))
    return Image.fromarray(cv2.cvtColor(merged, cv2.COLOR_LAB2RGB))


def main() -> None:
    ap = argparse.ArgumentParser(description="Prep a portrait photo for the profile pipeline.")
    ap.add_argument("input", type=Path, help="Path to the source portrait (e.g. hero.png)")
    ap.add_argument("-o", "--output", type=Path, default=Path("source-prepped.png"))
    ap.add_argument("--size", type=int, default=900, help="Output canvas size in px (square)")
    args = ap.parse_args()

    if not args.input.exists():
        raise SystemExit(f"Input not found: {args.input}")

    with Image.open(args.input) as src:
        src = src.convert("RGBA")

        print("Removing background (rembg / U2Net)...")
        cutout = remove(src)

        bbox = cutout.getbbox()
        if bbox:
            cutout = cutout.crop(bbox)

        cutout.thumbnail((args.size - 60, args.size - 60), Image.Resampling.LANCZOS)

        canvas = Image.new("RGBA", (args.size, args.size), (0, 0, 0, 0))
        paste_at = ((args.size - cutout.width) // 2, (args.size - cutout.height) // 2)
        canvas.alpha_composite(cutout, paste_at)

        print("Applying CLAHE contrast + sharpening...")
        rgb = clahe_rgb(canvas.convert("RGB"))
        rgb = ImageEnhance.Contrast(rgb).enhance(1.12)
        rgb = ImageEnhance.Sharpness(rgb).enhance(1.08)

        final = rgb.convert("RGBA")
        final.putalpha(canvas.getchannel("A"))
        final.save(args.output, "PNG", optimize=True)

    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
