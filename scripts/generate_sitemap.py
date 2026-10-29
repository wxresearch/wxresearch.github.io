#!/usr/bin/env python3
"""Update sitemap.xml using published article cards on the homepage."""
from html import unescape
from pathlib import Path
import re
from urllib.parse import quote

root = Path(__file__).resolve().parents[1]
home = (root / "index.html").read_text(encoding="utf-8")
base = "https://wxresearch.github.io/"

# Draft pages are excluded: they must be linked from a card marked "published".
urls = [base]
for card in re.findall(r'<article\b[^>]*class="[^"]*\bcard\b[^"]*"[^>]*>(.*?)</article>', home, re.I | re.S):
    if not re.search(r'class="[^"]*\bpublished\b', card, re.I):
        continue
    for raw_href in re.findall(r'href="([^"]+)"', card):
        href = unescape(raw_href).split("#")[0].split("?")[0]
        if not re.fullmatch(r'articles/[a-zA-Z0-9_./-]+\.html', href):
            continue
        file = (root / href).resolve()
        if file.is_relative_to(root) and file.is_file():
            urls.append(base + quote(href, safe="/"))
            break

lines = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for url in [urls[0]] + sorted(set(urls[1:])):
    lines.extend(["  <url>", f"    <loc>{url}</loc>", "  </url>"])
lines.append("</urlset>")
target = root / "sitemap.xml"
content = "\n".join(lines) + "\n"
if not target.exists() or target.read_text(encoding="utf-8") != content:
    target.write_text(content, encoding="utf-8")
    print(f"Updated sitemap with {len(urls)} pages")
else:
    print("Sitemap already up to date")
