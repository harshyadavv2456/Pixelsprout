#!/usr/bin/env python3
"""Write missing Pixel Sprout cover JPEGs.

A catalog entry must not point at a file that is not a JPEG. This script
draws the originals that have a built-in logo. Unknown missing covers are
reported, but a drawable cover is still written so one gap cannot block the rest.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "assets" / "originals.json"


def font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def stone(draw, cx, cy, rx, ry, base, hi):
    draw.ellipse((cx - rx, cy - ry + 8, cx + rx, cy + ry + 10), fill=(0, 0, 0, 80))
    draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=base)
    draw.ellipse((cx - rx * 0.55, cy - ry * 0.62, cx + rx * 0.15, cy - ry * 0.05), fill=hi)
    draw.ellipse((cx - rx * 0.18, cy - ry * 0.35, cx + rx * 0.05, cy - ry * 0.12), fill=(255, 255, 255, 90))


def draw_riverstone(path: Path):
    w = 800
    img = Image.new("RGB", (w, w), (8, 18, 32))
    px = img.load()
    for y in range(w):
        for x in range(w):
            t = y / w
            r = int(8 + 18 * t)
            g = int(22 + 28 * (1 - abs(t - 0.45)))
            b = int(42 + 40 * (1 - t))
            dx = (x - w / 2) / (w / 2)
            dy = (y - w / 2) / (w / 2)
            v = max(0, 1 - 0.55 * (dx * dx + dy * dy))
            px[x, y] = (int(r * v), int(g * v), int(b * v))
    img = img.filter(ImageFilter.SMOOTH).convert("RGBA")
    glow = Image.new("RGBA", (w, w), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((520, 16, 780, 270), fill=(255, 220, 150, 40))
    img = Image.alpha_composite(img, glow.filter(ImageFilter.GaussianBlur(24)))
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse((560, 48, 720, 208), fill=(255, 236, 190, 230))
    d.ellipse((598, 32, 758, 192), fill=(8, 22, 40, 255))
    for i, yy in enumerate((520, 575, 630, 690)):
        d.arc((60, yy, 740, yy + 80), 200, 340, fill=(140, 200, 210, 50 + i * 10), width=3)
    stone(d, 400, 470, 126, 58, (92, 78, 64, 255), (160, 140, 110, 200))
    stone(d, 358, 395, 100, 48, (70, 120, 118, 255), (150, 210, 200, 200))
    stone(d, 442, 336, 80, 42, (186, 98, 72, 255), (240, 170, 130, 200))
    stone(d, 392, 274, 60, 34, (214, 176, 92, 255), (255, 230, 160, 210))
    d.ellipse((358, 196, 442, 264), fill=(40, 30, 70, 180))
    d.ellipse((364, 190, 436, 256), fill=(230, 220, 255, 255))
    d.ellipse((378, 202, 416, 228), fill=(255, 255, 255, 180))
    d.rounded_rectangle((48, 48, 520, 176), radius=24, fill=(8, 16, 28, 180))
    d.text((72, 58), "RIVER", font=font(64, True), fill=(255, 236, 200, 255))
    d.text((72, 116), "STONE", font=font(64, True), fill=(140, 220, 210, 255))
    d.text((76, 188), "PIXEL SPROUT ORIGINAL", font=font(20), fill=(210, 200, 170, 220))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(path, "JPEG", quality=88, optimize=True)


DRAW = {"riverstone": draw_riverstone}


def is_jpeg(path: Path) -> bool:
    if not path.is_file() or path.stat().st_size < 4000:
        return False
    return path.read_bytes()[:3] == b"\xff\xd8\xff"


def main():
    games = json.loads(CATALOG.read_text(encoding="utf-8"))
    wrote = []
    missing = []
    for game in games:
        slug = game.get("slug") or ""
        thumb = game.get("thumbnail") or ""
        if "/assets/originals/" not in thumb:
            continue
        rel = thumb.split("/assets/originals/", 1)[1].split("?", 1)[0]
        path = ROOT / "assets" / "originals" / rel
        if is_jpeg(path):
            continue
        drawer = DRAW.get(slug)
        if drawer is None:
            missing.append(slug)
            continue
        drawer(path)
        if not is_jpeg(path):
            raise SystemExit(f"drew {slug} but it is not a JPEG")
        wrote.append(str(path.relative_to(ROOT)))
    print("wrote", ", ".join(wrote) or "nothing")
    if missing:
        print("still missing covers:", ", ".join(missing), file=sys.stderr)


if __name__ == "__main__":
    main()
