#!/usr/bin/env python3
"""Build SPHAERA OpenGraph image with the current sacred-geometry mark."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/img/og-sphaera.png"
MARK = ROOT / "assets/icons/sphaera-mark-512.png"
W, H = 1200, 630
BG = (7, 9, 18)
GOLD = (241, 213, 148)
GOLD_LINE = (216, 181, 109)
MUTED = (210, 199, 222)
WHITE = (247, 242, 232)
VIOLET = (136, 107, 216)
FONT_DIR = Path('/usr/share/fonts/truetype/dejavu')
SERIF_BOLD = ImageFont.truetype(str(FONT_DIR / 'DejaVuSerif-Bold.ttf'), 76)
SANS = ImageFont.truetype(str(FONT_DIR / 'DejaVuSans.ttf'), 36)
SANS_SMALL = ImageFont.truetype(str(FONT_DIR / 'DejaVuSans.ttf'), 31)

im = Image.new('RGB', (W, H), BG)
dr = ImageDraw.Draw(im, 'RGBA')
# quiet large construction circles
for r, alpha, off in [(540, 36, -90), (380, 32, 110), (270, 22, 0)]:
    dr.ellipse((W-r+off, H//2-r, W+r+off, H//2+r), outline=(*VIOLET, alpha), width=2)
# text block
dr.text((78, 122), 'SPHAERA', font=SERIF_BOLD, fill=GOLD)
dr.text((80, 218), 'Rhythmus, Bewusstsein', font=SANS, fill=WHITE)
dr.text((80, 262), '& zyklische Planung', font=SANS, fill=WHITE)
dr.line((80, 332, 510, 332), fill=(*GOLD_LINE, 230), width=2)
dr.text((80, 380), 'Kostenloser 7‑Tage‑Rhythmus‑Kompass', font=SANS_SMALL, fill=MUTED)
# mark panel, same sacred-geometry construct as logo/app/compass
mark = Image.open(MARK).convert('RGBA').resize((430, 430), Image.Resampling.LANCZOS)
# circular crop subtle; keep dark background of mark
mx, my = 720, 95
shadow = Image.new('RGBA', (470,470), (0,0,0,0))
sd = ImageDraw.Draw(shadow, 'RGBA')
sd.ellipse((14, 18, 456, 460), fill=(0,0,0,85))
im.paste(shadow, (mx-20, my-20), shadow)
im.paste(mark, (mx, my), mark)
# fine golden boundary around right symbol
cx, cy = mx + 215, my + 215
dr.ellipse((cx-218, cy-218, cx+218, cy+218), outline=(*GOLD_LINE, 88), width=1)
OUT.parent.mkdir(parents=True, exist_ok=True)
im.save(OUT, quality=95)
print(OUT, OUT.stat().st_size)
