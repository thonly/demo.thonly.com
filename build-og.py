#!/usr/bin/env python3
"""Render the Open Graph link-preview cards to PNG.

    python3 build-og.py     ->  og.png

Both are 1200x630, the size every platform crops from. They are rendered by
headless Chrome from the same tokens, fonts and emblem path the site uses, so a
preview card cannot drift from the pages it advertises — the alternative is a
hand-made image that silently goes stale.

Chrome needs the network on the first run (Google Fonts). If it is offline the
cards still render, in the fallback stack, and look wrong: check before shipping.
"""
import io, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

import re
from brand import EMBLEM, tok  # the vendored brand layer, never typed here

def brand_fill(css):
    for k in ("bg", "ink", "ink-dim"):
        css = css.replace("@D_%s@" % k.upper().replace("-", "_"), tok("d-" + k))
    assert not re.search(r"@[A-Z_]+@", css), "unfilled brand placeholder"
    return css


SHELL = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400;500&family=Noto+Sans+Khmer:wght@400;600&display=swap">
<style>
  *{box-sizing:border-box;margin:0}
  html,body{width:1200px;height:630px;overflow:hidden}
  body{background:@D_BG@;color:@D_INK@;
       font-family:"IBM Plex Sans",system-ui,sans-serif;
       display:flex;flex-direction:column;justify-content:center;
       padding:0 92px;position:relative;-webkit-font-smoothing:antialiased}
  /* one soft accent bloom, bottom-left, so the card is not a flat rectangle */
  body::before{content:"";position:absolute;left:-160px;bottom:-260px;width:760px;height:760px;
       border-radius:50%;background:radial-gradient(circle,rgba(124,196,236,.20),transparent 62%)}
  .inner{position:relative}
  h1{font-family:"Newsreader",Georgia,serif;font-weight:600;letter-spacing:-.022em;
     line-height:1.03;margin-bottom:26px}
  .em{display:inline-block;vertical-align:-.141em;color:#7cc4ec;
      margin-left:-.09em;margin-right:-.04em}
  .reg{font-size:.34em;vertical-align:1.3em;font-weight:500;margin-left:.06em}
  p{font-size:30px;line-height:1.5;color:@D_INK_DIM@;max-width:23ch}
  .km{font-family:"Noto Sans Khmer","IBM Plex Sans",sans-serif}
  .foot{position:absolute;left:92px;bottom:56px;display:flex;align-items:center;gap:14px;
        font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:22px;color:#7cc4ec}
  .rule{width:52px;height:2px;background:#7cc4ec;opacity:.5}
</style></head><body>{BODY}
<div class="foot"><span class="rule"></span>demo.thonly.com</div>
</body></html>"""


def emblem(size_em=".92em"):
    return ('<svg class="em" viewBox="0 0 24 24" style="width:%s;height:%s">'
            '<path fill="currentColor" d="%s"/></svg>' % (size_em, size_em, EMBLEM))


CARDS = {
    "og.png": '<div class="inner"><h1 style="font-size:84px">billing.thonly.com</h1>'
              '<p>Your balance for compute and storage. Drawings, in English and Khmer.</p></div>',
}


def main():
    if not os.path.exists(CHROME):
        sys.exit("Chrome not found at %s — render the cards elsewhere." % CHROME)
    only = set(sys.argv[1:])
    for name, body in CARDS.items():
        if only and name not in only:
            continue
        with tempfile.TemporaryDirectory() as tmp:
            src = os.path.join(tmp, "card.html")
            io.open(src, "w", encoding="utf-8").write(brand_fill(SHELL).replace("{BODY}", body))
            out = os.path.join(HERE, name)
            subprocess.run([CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
                            "--force-device-scale-factor=1", "--window-size=1200,630",
                            "--virtual-time-budget=4000",
                            "--screenshot=" + out, "file://" + src],
                           check=True, capture_output=True)
            print("%-22s %6d bytes" % (name, os.path.getsize(out)))


if __name__ == "__main__":
    main()
