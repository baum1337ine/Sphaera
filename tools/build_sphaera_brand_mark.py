#!/usr/bin/env python3
"""Build the SPHAERA brand mark used on social, website favicons, and hero art."""
from __future__ import annotations

import math
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ICON_DIR = ROOT / "assets/icons"
ICON_DIR.mkdir(parents=True, exist_ok=True)

GOLD = "#b79a60"
GOLD_SOFT = "#8f7748"
BG = "#070c10"

# Geometry mirrors the social media mark: Tree-of-Life nodes, fine gold lines,
# open outer circle arcs, deliberately no invented flower/cross overlay.
NODES = {
    "top": (500, 145),
    "left_upper": (370, 268),
    "right_upper": (630, 268),
    "center": (500, 410),
    "left_mid": (345, 545),
    "right_mid": (655, 545),
    "middle_low": (500, 545),
    "left_lower": (405, 675),
    "right_lower": (595, 675),
    "bottom": (500, 810),
}
EDGES = [
    ("top", "left_upper"), ("top", "right_upper"),
    ("left_upper", "center"), ("right_upper", "center"),
    ("left_upper", "left_mid"), ("right_upper", "right_mid"),
    ("center", "left_mid"), ("center", "right_mid"),
    ("center", "middle_low"), ("middle_low", "bottom"),
    ("middle_low", "left_lower"), ("middle_low", "right_lower"),
    ("left_mid", "left_lower"), ("right_mid", "right_lower"),
    ("left_lower", "bottom"), ("right_lower", "bottom"),
]


def svg() -> str:
    lines = [
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1000 1000' role='img' aria-label='SPHAERA Symbol'>",
        "<defs><radialGradient id='halo' cx='50%' cy='50%' r='46%'><stop offset='0' stop-color='#d8b56d' stop-opacity='.12'/><stop offset='1' stop-color='#d8b56d' stop-opacity='0'/></radialGradient></defs>",
        "<circle cx='500' cy='510' r='390' fill='url(#halo)'/>",
        "<path d='M245 286 A390 390 0 0 1 755 286' fill='none' stroke='#b79a60' stroke-opacity='.48' stroke-width='1.25' stroke-linecap='round'/>",
        "<path d='M245 642 A390 390 0 0 0 755 642' fill='none' stroke='#b79a60' stroke-opacity='.42' stroke-width='1.25' stroke-linecap='round'/>",
    ]
    for a, b in EDGES:
        x1, y1 = NODES[a]; x2, y2 = NODES[b]
        lines.append(f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}' stroke='#b79a60' stroke-opacity='.56' stroke-width='1.35' stroke-linecap='round'/>")
    for name, (x, y) in NODES.items():
        r = 32 if name in {"top", "bottom"} else 28
        if name == "center": r = 30
        lines.append(f"<circle cx='{x}' cy='{y}' r='{r}' fill='none' stroke='#d8b56d' stroke-opacity='.82' stroke-width='2.3'/>")
        lines.append(f"<circle cx='{x}' cy='{y}' r='6.4' fill='#d8b56d' fill-opacity='.82'/>")
    lines.append("</svg>\n")
    return "\n".join(lines)


def draw_mark(size: int, dark_bg: bool = True) -> Image.Image:
    scale = size / 1000
    im = Image.new("RGBA", (size, size), BG if dark_bg else (0, 0, 0, 0))
    dr = ImageDraw.Draw(im, "RGBA")
    # Keep the icon line-based like the social posts; no decorative overlay.
    def pt(p): return (p[0]*scale, p[1]*scale)
    def color(hexv, alpha):
        h=hexv.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))+(alpha,)
    bbox = tuple(v*scale for v in (110, 120, 890, 900))
    dr.arc(bbox, start=218, end=322, fill=color(GOLD, 120), width=max(1, round(size/720)))
    dr.arc(bbox, start=38, end=142, fill=color(GOLD, 105), width=max(1, round(size/720)))
    for a,b in EDGES:
        dr.line((pt(NODES[a]), pt(NODES[b])), fill=color(GOLD, 142), width=max(1, round(size/520)))
    for name, p in NODES.items():
        x,y=pt(p); r=(32 if name in {'top','bottom'} else 28) * scale
        if name == 'center': r=30*scale
        dr.ellipse((x-r,y-r,x+r,y+r), outline=color('#d8b56d', 210), width=max(1, round(size/350)))
        rr=max(2, 6.4*scale)
        dr.ellipse((x-rr,y-rr,x+rr,y+rr), fill=color('#d8b56d', 220))
    return im


def main() -> None:
    (ICON_DIR / "sphaera-mark.svg").write_text(svg(), encoding="utf-8")
    for size in [16, 32, 48, 96, 180, 192, 512]:
        draw_mark(size, dark_bg=True).save(ICON_DIR / f"sphaera-mark-{size}.png")
    draw_mark(180, dark_bg=True).save(ICON_DIR / "apple-touch-icon.png")
    # multi-resolution favicon; start from the largest source so PIL embeds useful downsamples.
    draw_mark(256, dark_bg=True).save(ROOT / "favicon.ico", sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])

if __name__ == "__main__":
    main()
