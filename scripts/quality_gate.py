#!/usr/bin/env python3
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import sys, re
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
        required=['/assets/free/sphaera-rhythmus-kompass.pdf','/datenschutz.html','/impressum.html']
        for r in required:
            if r not in text: errors.append(f'index.html: missing {r}')
        if '/media/meta' in text: errors.append('index.html links hidden media folder')
if not (BASE/'media/meta/.gitkeep').exists(): errors.append('missing hidden media folder')
robots=(BASE/'robots.txt').read_text(encoding='utf-8') if (BASE/'robots.txt').exists() else ''
if 'Disallow: /media/meta/' not in robots: errors.append('robots does not hide /media/meta/')
if errors:
    print('\n'.join(errors)); sys.exit(1)
print('quality gate passed')
