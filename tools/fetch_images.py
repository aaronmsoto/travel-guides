#!/usr/bin/env python3
"""
fetch_images.py — download, license-check-friendly, and process guide images.

Reads guides/<slug>/img/sources.json, a list of:
  {
    "file": "angels-landing.jpg",
    "url": "<direct image url>",
    "sourceUrl": "<page the image came from>",
    "title": "...",
    "author": "...",
    "license": "...",
    "licenseUrl": "..."
  }

For each entry it:
  - downloads the image (sends a descriptive User-Agent, retries with backoff)
  - converts it to JPEG, strips EXIF
  - resizes so the width is at most 1600px (2000px if file == "hero.jpg"),
    preserving aspect ratio (never upscales)
  - writes guides/<slug>/img/<file> at quality 82
  - writes a 480px-wide guides/<slug>/img/thumb-<file> (quality 82)
  - updates guides/<slug>/img/manifest.json, mapping file -> metadata
    { title, author, license, licenseUrl, sourceUrl, width, height, bytes }

Idempotent: skips files that already exist (both the main image and the
thumb) unless --force is given.

Usage:
    python3 tools/fetch_images.py <slug> [--force]
    python3 tools/fetch_images.py zion
    python3 tools/fetch_images.py death-valley --force
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps

USER_AGENT = "travel-guides-builder/0.1 (https://github.com/aaronmsoto/travel-guides)"

MAIN_MAX_WIDTH = 1600
HERO_MAX_WIDTH = 2000
THUMB_WIDTH = 480
JPEG_QUALITY = 82
MAX_RETRIES = 6
RETRY_BACKOFF_SECONDS = 5.0
PACING_SECONDS = 2.0  # polite delay between successive downloads


def fetch_bytes(url: str) -> bytes:
    """Download bytes from url with UA header, retrying with backoff."""
    last_err = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return resp.read()
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            last_err = e
            if attempt < MAX_RETRIES:
                wait = RETRY_BACKOFF_SECONDS * attempt
                print(f"    retry {attempt}/{MAX_RETRIES} after error ({e}); waiting {wait:.1f}s", file=sys.stderr)
                time.sleep(wait)
    raise RuntimeError(f"failed to fetch {url} after {MAX_RETRIES} attempts: {last_err}")


def process_image(raw_bytes: bytes, max_width: int) -> Image.Image:
    """Open, auto-orient (using EXIF, then strip it), convert to RGB, resize down to max_width."""
    im = Image.open(BytesIO(raw_bytes))
    # Apply EXIF orientation before stripping it.
    im = ImageOps.exif_transpose(im)
    if im.mode not in ("RGB",):
        im = im.convert("RGB")
    w, h = im.size
    if w > max_width:
        new_h = round(h * (max_width / w))
        im = im.resize((max_width, new_h), Image.LANCZOS)
    return im


def save_jpeg(im: Image.Image, path: Path) -> int:
    """Save image as JPEG with no EXIF, return byte size on disk."""
    im.save(path, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    return path.stat().st_size


def main():
    parser = argparse.ArgumentParser(description="Fetch and process guide images.")
    parser.add_argument("slug", help="Guide slug, e.g. 'zion' or 'death-valley'")
    parser.add_argument("--force", action="store_true", help="Re-download and reprocess even if files exist")
    args = parser.parse_args()

    guide_dir = Path("guides") / args.slug
    img_dir = guide_dir / "img"
    sources_path = img_dir / "sources.json"
    manifest_path = img_dir / "manifest.json"

    if not sources_path.exists():
        print(f"ERROR: {sources_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(sources_path, "r", encoding="utf-8") as f:
        sources = json.load(f)

    manifest = {}
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

    ok_count = 0
    fail_count = 0

    for entry in sources:
        file_name = entry["file"]
        out_path = img_dir / file_name
        thumb_path = img_dir / f"thumb-{file_name}"

        if out_path.exists() and thumb_path.exists() and not args.force:
            print(f"skip (exists): {file_name}")
            if file_name not in manifest:
                # Backfill manifest entry from sources.json + existing file if missing.
                try:
                    with Image.open(out_path) as im:
                        w, h = im.size
                    manifest[file_name] = {
                        "title": entry.get("title", ""),
                        "author": entry.get("author", ""),
                        "license": entry.get("license", ""),
                        "licenseUrl": entry.get("licenseUrl", ""),
                        "sourceUrl": entry.get("sourceUrl", ""),
                        "width": w,
                        "height": h,
                        "bytes": out_path.stat().st_size,
                    }
                except Exception:
                    pass
            ok_count += 1
            continue

        print(f"fetching: {file_name} <- {entry['url']}")
        try:
            time.sleep(PACING_SECONDS)
            raw = fetch_bytes(entry["url"])
            max_w = HERO_MAX_WIDTH if file_name == "hero.jpg" else MAIN_MAX_WIDTH
            im_main = process_image(raw, max_w)
            main_bytes = save_jpeg(im_main, out_path)
            w, h = im_main.size

            im_thumb = process_image(raw, THUMB_WIDTH)
            save_jpeg(im_thumb, thumb_path)

            manifest[file_name] = {
                "title": entry.get("title", ""),
                "author": entry.get("author", ""),
                "license": entry.get("license", ""),
                "licenseUrl": entry.get("licenseUrl", ""),
                "sourceUrl": entry.get("sourceUrl", ""),
                "width": w,
                "height": h,
                "bytes": main_bytes,
            }
            print(f"    saved {file_name} ({w}x{h}, {main_bytes/1024:.0f} KB) + thumb-{file_name}")
            ok_count += 1
        except Exception as e:
            print(f"    FAILED: {file_name}: {e}", file=sys.stderr)
            fail_count += 1

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
        f.write("\n")

    print(f"\nDone: {ok_count} ok, {fail_count} failed. Manifest: {manifest_path}")
    if fail_count:
        sys.exit(2)


if __name__ == "__main__":
    main()
