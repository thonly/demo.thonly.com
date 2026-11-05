#!/usr/bin/env python3
"""Generate the favicon set and the web app manifest from the brand layer's emblem (never a hand-made heart).

    python3 build-icons.py

Writes favicon.svg · favicon-96x96.png · apple-touch-icon.png (180) · icon-192.png · icon-512.png · site.webmanifest.
The PNGs are screenshots of one HTML tile in headless Chrome, so they cannot drift from the SVG.
"""
import io, json, os, subprocess, sys, tempfile
from brand import EMBLEM, tok

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ACCENT = "#0369a1"  # this surface's accent, declared once per generator (TH sky blue, provisional)
BG = tok("l-bg")
# The emblem fills 75.34% of its 24-unit box and sits off-centre (brand.json mark.geometry): centre it by its bbox.
GLYPH = '<path transform="translate(12 12) scale(.82) translate(-12.7237 -11.2776)" d="%s" fill="%s"/>' % (EMBLEM, ACCENT)

svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect width="24" height="24" rx="5" fill="%s"/>%s</svg>'
       % (BG, GLYPH))
io.open(os.path.join(HERE, "favicon.svg"), "w", encoding="utf-8").write(svg + "\n")

if not os.path.exists(CHROME):
    sys.exit("Chrome not found at %s" % CHROME)
for name, px, pad in (("favicon-96x96.png", 96, 0), ("apple-touch-icon.png", 180, .12), ("icon-192.png", 192, .12),
                      ("icon-512.png", 512, .12)):
    tile = ('<!doctype html><html><body style="margin:0;background:%s">'
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s %s %s %s" width="%d" height="%d">%s</svg></body></html>'
            % (BG, -24 * pad, -24 * pad, 24 * (1 + 2 * pad), 24 * (1 + 2 * pad), px, px, GLYPH))
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "t.html")
        io.open(src, "w", encoding="utf-8").write(tile)
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        "--window-size=%d,%d" % (px, px), "--screenshot=" + os.path.join(HERE, name), "file://" + src],
                       check=True, capture_output=True)
    print("%-22s %6d bytes" % (name, os.path.getsize(os.path.join(HERE, name))))

manifest = {
    "name": "billing.thonly.com drawings",
    "short_name": "demo.thonly.com",
    "description": "Drawings of billing.thonly.com, in English and Khmer. They charge nobody.",
    "start_url": "./", "scope": "./", "display": "standalone",
    "background_color": BG, "theme_color": ACCENT,
    "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
              {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
              {"src": "favicon.svg", "sizes": "any", "type": "image/svg+xml"}],
}
io.open(os.path.join(HERE, "site.webmanifest"), "w", encoding="utf-8").write(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
print("site.webmanifest written")
