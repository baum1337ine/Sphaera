#!/usr/bin/env python3
"""Build SPHAERA sacred-geometry brand marks for website, favicons, and hero art.

The mark is deliberately based on recognizable sacred geometry:
- Seed/Flower of Life: one central circle with six equal circles around it.
- Outer double circle: a calm mandala boundary.
- Subtle hexagonal connection lines: reinforces symmetry without becoming a random sigil.
"""
from __future__ import annotations

import math
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ICON_DIR = ROOT / "assets/icons"
ICON_DIR.mkdir(parents=True, exist_ok=True)

BG = "#070912"
GOLD = "#d8b56d"
GOLD_DEEP = "#b79a60"
VIOLET = "#8f7ae6"


def ring_points(cx: float, cy: float, r: float, n: int = 6, start_deg: float = -90) -> list[tuple[float, float]]:
    return [
        (cx + math.cos(math.radians(start_deg + i * 360 / n)) * r,
         cy + math.sin(math.radians(start_deg + i * 360 / n)) * r)
        for i in range(n)
    ]


def svg() -> str:
    cx = cy = 500
    seed_r = 158
    centers = [(cx, cy)] + ring_points(cx, cy, seed_r, 6, -90)
    outer = ring_points(cx, cy, seed_r, 6, -90)
    inner_hex = ring_points(cx, cy, seed_r * .86, 6, -90)

    lines: list[str] = [
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1000 1000' role='img' aria-label='SPHAERA heilige Geometrie'>",
        "<defs>",
        "<radialGradient id='halo' cx='50%' cy='50%' r='52%'><stop offset='0' stop-color='#d8b56d' stop-opacity='.13'/><stop offset='.55' stop-color='#886bd8' stop-opacity='.045'/><stop offset='1' stop-color='#070912' stop-opacity='0'/></radialGradient>",
        "</defs>",
        "<rect width='1000' height='1000' rx='210' fill='#070912'/>",
        "<circle cx='500' cy='500' r='405' fill='url(#halo)'/>",
        "<circle cx='500' cy='500' r='355' fill='none' stroke='#d8b56d' stroke-opacity='.56' stroke-width='4'/>",
        "<circle cx='500' cy='500' r='308' fill='none' stroke='#d8b56d' stroke-opacity='.24' stroke-width='2'/>",
    ]

    # Flower/Seed of Life: seven equal circles, exact recognizable construct.
    for x, y in centers:
        lines.append(f"<circle cx='{x:.3f}' cy='{y:.3f}' r='{seed_r:.3f}' fill='none' stroke='#d8b56d' stroke-opacity='.68' stroke-width='3.4'/>")

    # Fine construction geometry: hexagon + triangle pair + central axis.
    hex_path = " ".join(f"{x:.3f},{y:.3f}" for x, y in inner_hex)
    lines.append(f"<polygon points='{hex_path}' fill='none' stroke='#d8b56d' stroke-opacity='.30' stroke-width='2'/>")
    tri_a = [inner_hex[i] for i in [0, 2, 4]]
    tri_b = [inner_hex[i] for i in [1, 3, 5]]
    lines.append("<polygon points='" + " ".join(f"{x:.3f},{y:.3f}" for x, y in tri_a) + "' fill='none' stroke='#8f7ae6' stroke-opacity='.24' stroke-width='1.8'/>")
    lines.append("<polygon points='" + " ".join(f"{x:.3f},{y:.3f}" for x, y in tri_b) + "' fill='none' stroke='#8f7ae6' stroke-opacity='.22' stroke-width='1.8'/>")
    for x, y in outer:
        lines.append(f"<line x1='500' y1='500' x2='{x:.3f}' y2='{y:.3f}' stroke='#d8b56d' stroke-opacity='.18' stroke-width='1.5'/>")

    lines.extend([
        "<circle cx='500' cy='500' r='28' fill='none' stroke='#d8b56d' stroke-opacity='.72' stroke-width='3'/>",
        "<circle cx='500' cy='500' r='7' fill='#d8b56d' fill-opacity='.86'/>",
        "</svg>\n",
    ])
    return "\n".join(lines)


def hex_rgba(hexv: str, alpha: int) -> tuple[int, int, int, int]:
    h = hexv.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)


def draw_mark(size: int, dark_bg: bool = True) -> Image.Image:
    scale = size / 1000
    im = Image.new("RGBA", (size, size), BG if dark_bg else (0, 0, 0, 0))
    dr = ImageDraw.Draw(im, "RGBA")

    def sc(v: float) -> float:
        return v * scale

    def ellipse(cx: float, cy: float, r: float, outline: str, alpha: int, width: float = 2.0, fill=None):
        box = (sc(cx-r), sc(cy-r), sc(cx+r), sc(cy+r))
        dr.ellipse(box, outline=hex_rgba(outline, alpha), width=max(1, round(sc(width))), fill=fill)

    # No filled medallion: the construct must read as sacred geometry, not as a gold disk.

    ellipse(500, 500, 355, GOLD, 150, 7)
    ellipse(500, 500, 308, GOLD, 58, 3)

    seed_r = 158
    centers = [(500, 500)] + ring_points(500, 500, seed_r, 6, -90)
    for x, y in centers:
        ellipse(x, y, seed_r, GOLD, 174, 5)

    inner_hex = ring_points(500, 500, seed_r * .86, 6, -90)
    pts = [(sc(x), sc(y)) for x, y in inner_hex]
    dr.polygon(pts, outline=hex_rgba(GOLD, 76))
    # strengthen polygon lines because PIL polygon outline is 1px only
    for i in range(6):
        dr.line((pts[i], pts[(i+1) % 6]), fill=hex_rgba(GOLD, 76), width=max(1, round(sc(3))))
    for ids, col, alpha in [([0, 2, 4], VIOLET, 58), ([1, 3, 5], VIOLET, 52)]:
        tri = [pts[i] for i in ids]
        for i in range(3):
            dr.line((tri[i], tri[(i+1) % 3]), fill=hex_rgba(col, alpha), width=max(1, round(sc(2))))
    for x, y in ring_points(500, 500, seed_r, 6, -90):
        dr.line((sc(500), sc(500), sc(x), sc(y)), fill=hex_rgba(GOLD, 44), width=max(1, round(sc(2))))

    ellipse(500, 500, 28, GOLD, 190, 5)
    rr = max(1.5, sc(7))
    dr.ellipse((sc(500)-rr, sc(500)-rr, sc(500)+rr, sc(500)+rr), fill=hex_rgba(GOLD, 220))
    return im


def main() -> None:
    (ICON_DIR / "sphaera-mark.svg").write_text(svg(), encoding="utf-8")
    for size in [16, 32, 48, 96, 180, 192, 512]:
        draw_mark(size, dark_bg=True).save(ICON_DIR / f"sphaera-mark-{size}.png")
    draw_mark(180, dark_bg=True).save(ICON_DIR / "apple-touch-icon.png")
    draw_mark(256, dark_bg=True).save(ROOT / "favicon.ico", sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])


if __name__ == "__main__":
    main()
