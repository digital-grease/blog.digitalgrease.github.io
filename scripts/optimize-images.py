#!/usr/bin/env python3
"""
Post-build image optimization for the site/ directory.

Runs after mkdocs build to:
  1. Resize images wider than MAX_WIDTH
  2. Convert JPG/PNG to WebP
  3. Update HTML <img> src references to point to .webp
  4. Add loading="lazy" to all <img> tags missing it
  5. Remove original JPG/PNG files (WebP replaces them)

Skips favicons and SVGs. Preserves directory structure.
"""

import os
import re
import sys
from pathlib import Path

from PIL import Image

MAX_WIDTH = 1200
WEBP_QUALITY = 80
SITE_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("site")

# Files to skip (by name, not path)
SKIP_FILES = {"favicon.png", "favicon.ico"}

# Image extensions to optimize
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def optimize_images(site_dir: Path) -> dict[str, str]:
    """Resize and convert images to WebP. Returns a map of old paths to new paths (relative to site_dir)."""
    remap = {}

    for img_path in site_dir.rglob("*"):
        if img_path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        if img_path.name in SKIP_FILES:
            continue

        # Skip social card images (auto-generated PNGs from the social plugin)
        rel = img_path.relative_to(site_dir)
        if str(rel).startswith(os.path.join("assets", "images", "social")):
            continue

        try:
            img = Image.open(img_path)
        except Exception as e:
            print(f"  SKIP {rel} (can't open: {e})")
            continue

        # Resize if wider than MAX_WIDTH
        if img.width > MAX_WIDTH:
            ratio = MAX_WIDTH / img.width
            new_size = (MAX_WIDTH, int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)
            print(f"  RESIZE {rel} -> {new_size[0]}x{new_size[1]}")

        # Convert to WebP
        webp_path = img_path.with_suffix(".webp")
        if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
            img = img.convert("RGBA")
        else:
            img = img.convert("RGB")

        img.save(webp_path, "WEBP", quality=WEBP_QUALITY)

        old_size = img_path.stat().st_size
        new_size_bytes = webp_path.stat().st_size
        savings = (1 - new_size_bytes / old_size) * 100 if old_size > 0 else 0
        print(f"  WEBP  {rel} -> {webp_path.name} ({old_size // 1024}KB -> {new_size_bytes // 1024}KB, {savings:.0f}% smaller)")

        # Track the remap for HTML rewriting
        old_rel = str(rel)
        new_rel = str(rel.with_suffix(".webp"))
        remap[old_rel] = new_rel

        # Remove original
        img_path.unlink()

    return remap


def rewrite_html(site_dir: Path, remap: dict[str, str]) -> None:
    """Update img src references and add loading='lazy' in all HTML files."""
    for html_path in site_dir.rglob("*.html"):
        text = html_path.read_text(encoding="utf-8")
        original = text

        # Rewrite image references (handles both relative and absolute paths)
        for old_path, new_path in remap.items():
            # Match the filename portion in src attributes (path may be relative)
            old_name = os.path.basename(old_path)
            new_name = os.path.basename(new_path)
            # Replace in src="..." attributes
            text = text.replace(old_name, new_name)

        # Add loading="lazy" to img tags that don't have it
        text = re.sub(
            r'<img(?![^>]*loading=)([^>]*?)(/?)>',
            r'<img loading="lazy"\1\2>',
            text,
        )

        if text != original:
            html_path.write_text(text, encoding="utf-8")
            rel = html_path.relative_to(site_dir)
            print(f"  HTML  {rel}")


def main():
    if not SITE_DIR.is_dir():
        print(f"Error: {SITE_DIR} is not a directory")
        sys.exit(1)

    print(f"Optimizing images in {SITE_DIR}/")
    print()

    remap = optimize_images(SITE_DIR)

    if remap:
        print()
        print(f"Rewriting HTML references ({len(remap)} images converted)...")
        rewrite_html(SITE_DIR, remap)
    else:
        print("  No images to optimize.")

    print()
    print("Done.")


if __name__ == "__main__":
    main()
