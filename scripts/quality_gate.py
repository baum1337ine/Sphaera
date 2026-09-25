#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import json, sys, re
BASE = Path(__file__).resolve().parents[1]
errors=[]
class P(HTMLParser):
    def __init__(self):
        super().__init__(); self.links=[]; self.scripts=[]; self.ids=set(); self.forms=0
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if 'id' in a: self.ids.add(a['id'])
        if tag=='a' and 'href' in a: self.links.append(a['href'])
        if tag=='script': self.scripts.append(a)
        if tag=='form': self.forms += 1
for html in BASE.glob('*.html'):
    text=html.read_text(encoding='utf-8')
    p=P(); p.feed(text)
    if 'Obsidian' in text or 'Rohimport' in text or 'Werkstatt' in text:
        errors.append(f'{html.name}: internal wording leak')
    if 'https://cloud.umami.is/script.js' in text and 'localStorage.getItem' not in text:
        errors.append(f'{html.name}: eager Umami load')
    for href in p.links:
        if href.startswith(('mailto:','tel:','http://','https://')): continue
        if href.startswith('#'):
            if href[1:] and href[1:] not in p.ids: errors.append(f'{html.name}: missing anchor {href}')
            continue
        target,_,frag = href.partition('#')
        target = target.lstrip('/') or 'index.html'
        local = BASE/target
        if target.endswith('/'):
            local = BASE/target/'index.html'
        if not local.exists(): errors.append(f'{html.name}: broken local link {href}')
        elif frag:
            pp=P(); pp.feed(local.read_text(encoding='utf-8'))
            if frag not in pp.ids: errors.append(f'{html.name}: missing fragment {href}')
    if html.name=='index.html':
        required=['/assets/free/sphaera-rhythmus-kompass.pdf','/assets/free/sphaera-wochenkreis-journal-prototyp.pdf','/datenschutz.html','/impressum.html','/assets/icons/sphaera-mark.svg','/favicon.ico','/site.webmanifest']
        for r in required:
            if r not in text: errors.append(f'index.html: missing {r}')
        forbidden=['Free Produkt','free produkt','Kompass holen']
        for f in forbidden:
            if f in text: errors.append(f'index.html: stale public copy {f!r}')
        if '7‑Tage‑Kompass' not in text: errors.append('index.html: missing 7-Tage-Kompass nav/copy')
        if '/media/meta' in text: errors.append('index.html links hidden media folder')
asset_expectations = {
    'assets/free/sphaera-rhythmus-kompass.pdf': 100_000,
    'assets/free/sphaera-wochenkreis-journal-prototyp.pdf': 100_000,
    'assets/img/og-sphaera.png': 30_000,
    'assets/icons/sphaera-mark.svg': 1_000,
    'assets/icons/sphaera-mark-16.png': 100,
    'assets/icons/sphaera-mark-32.png': 200,
    'assets/icons/sphaera-mark-48.png': 400,
    'assets/icons/sphaera-mark-96.png': 1_000,
    'assets/icons/sphaera-mark-180.png': 2_000,
    'assets/icons/apple-touch-icon.png': 2_000,
    'assets/icons/sphaera-mark-192.png': 2_000,
    'assets/icons/sphaera-mark-512.png': 6_000,
    'favicon.ico': 1_000,
    'site.webmanifest': 100,
}
for rel, min_size in asset_expectations.items():
    p = BASE / rel
    if not p.exists():
        errors.append(f'missing asset {rel}')
    elif p.stat().st_size < min_size:
        errors.append(f'asset too small {rel}')
manifest_path = BASE / 'site.webmanifest'
if manifest_path.exists():
    try:
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        icon_srcs = {icon.get('src') for icon in manifest.get('icons', [])}
        for src in ['/assets/icons/sphaera-mark-192.png', '/assets/icons/sphaera-mark-512.png']:
            if src not in icon_srcs:
                errors.append(f'site.webmanifest missing icon {src}')
    except json.JSONDecodeError as exc:
        errors.append(f'site.webmanifest invalid json: {exc}')
if not (BASE/'media/meta/.gitkeep').exists(): errors.append('missing hidden media folder')
robots=(BASE/'robots.txt').read_text(encoding='utf-8') if (BASE/'robots.txt').exists() else ''
if 'Disallow: /media/meta/' not in robots: errors.append('robots does not hide /media/meta/')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print('quality gate passed')
