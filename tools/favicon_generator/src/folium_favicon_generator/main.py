"""Generate Folium favicon assets from the approved standalone logo."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / "frontend" / "public" / "logo-icon.png"
PUBLIC = ROOT / "frontend" / "public"
APP = ROOT / "frontend" / "src" / "app"
PNG_SIZES = (32, 180, 192, 512)
FAVICON_FILL_RATIO = 0.72


def resized_logo(
    source: Image.Image, size: int, fill_ratio: float = 1.0
) -> Image.Image:
    canvas = Image.new("RGBA", (size, size))
    logo = source.copy()
    logo_max_size = round(size * fill_ratio)
    logo.thumbnail((logo_max_size, logo_max_size), Image.Resampling.LANCZOS)
    offset = ((size - logo.width) // 2, (size - logo.height) // 2)
    canvas.alpha_composite(logo, offset)
    return canvas


def main() -> None:
    if not SOURCE.is_file():
        raise FileNotFoundError(f"Approved logo asset not found: {SOURCE}")

    with Image.open(SOURCE) as image:
        source = image.convert("RGBA")
        variants = {size: resized_logo(source, size) for size in PNG_SIZES}

    resized_logo(source, 32, FAVICON_FILL_RATIO).save(PUBLIC / "favicon-32x32.png")
    variants[180].save(PUBLIC / "apple-touch-icon.png")
    variants[192].save(PUBLIC / "icon-192.png")
    variants[512].save(PUBLIC / "icon-512.png")
    resized_logo(source, 64, FAVICON_FILL_RATIO).save(
        APP / "favicon.ico",
        sizes=((16, 16), (32, 32), (48, 48), (64, 64)),
    )

    manifest = {
        "name": "Folium",
        "short_name": "Folium",
        "icons": [
            {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"},
        ],
    }
    (PUBLIC / "site.webmanifest").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )