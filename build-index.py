#!/usr/bin/env python3
"""Generate index.html from canvas.json: the front door cannot drift from the artboards.

    python3 build-index.py
"""
import hashlib, io, json, os, html
from brand import tok

HERE = os.path.dirname(os.path.abspath(__file__))
c = json.load(io.open(os.path.join(HERE, "canvas.json"), encoding="utf-8"))
boards = sorted(c["artboards"], key=lambda b: (b["y"], b["x"]))
rows = "".join(
    '<li><a href="%s?v=%s&w=%d">%s</a><span class="m">%d px wide</span></li>' % (b["file"], hashlib.sha256(io.open(os.path.join(HERE, b["file"]), "rb").read()).hexdigest()[:8], b["w"], html.escape(b["title"]), b["w"])
    for b in boards)
page = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light dark">
<meta name="googlebot" content="noindex,nofollow">
<meta name="bingbot" content="noindex,nofollow">
<meta name="slurp" content="noindex,nofollow">
<meta name="yandex" content="noindex,nofollow">
<script src="./analytics.js"></script>
<title>billing.thonly.com: drawings</title>
<meta property="og:type" content="website">
<meta property="og:url" content="https://demo.thonly.com/">
<meta property="og:site_name" content="billing.thonly.com: drawings">
<meta property="og:title" content="billing.thonly.com: drawings">
<meta property="og:description" content="The billing.thonly.com screens, drawn in English and Khmer. These are drawings. They charge nobody.">
<meta property="og:image" content="https://demo.thonly.com/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="billing.thonly.com on a dark ground.">
<link rel="manifest" href="site.webmanifest">
<link rel="icon" type="image/svg+xml" href="favicon.svg">
<link rel="icon" type="image/png" sizes="96x96" href="favicon-96x96.png">
<link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
<meta name="description" content="Drawings of billing.thonly.com, the balance for compute and storage. English and Khmer.">
<meta name="twitter:title" content="billing.thonly.com: drawings">
<meta name="twitter:description" content="The billing.thonly.com screens, drawn in English and Khmer. These are drawings. They charge nobody.">
<meta name="twitter:image" content="https://demo.thonly.com/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0369a1">
<style>[hidden]{display:none!important}
:root{--bg:@L_BG@;--fg:@L_INK@;--dim:@L_INK_DIM@;--line:@L_LINE@;--acc:#0369a1}
@media (prefers-color-scheme:dark){:root{--bg:@D_BG@;--fg:@D_INK@;--dim:@D_INK_DIM@;--line:@D_LINE@;--acc:#7cc4ec}}
body{margin:0;padding:2.5rem 16px 4rem;background:var(--bg);color:var(--fg);font:1rem/1.6 system-ui,sans-serif}
main{max-width:36rem;margin:0 auto}
h1{font-size:1.9rem;line-height:1.2;margin:0 0 .5rem}
.top{display:flex;justify-content:flex-end;margin:-1.5rem 0 1rem}
.share{display:inline-flex;align-items:center;gap:.4rem;border:1px solid var(--line);border-radius:999px;background:none;color:var(--fg);font:inherit;font-size:.9rem;padding:.4rem .9rem;cursor:pointer}
.share svg{width:18px;height:18px}
#toast{position:fixed;left:50%%;bottom:24px;transform:translateX(-50%%);background:var(--fg);color:var(--bg);border-radius:999px;padding:.5rem 1rem;font-size:.9rem}
p{color:var(--dim)}
.start{display:block;border:1px solid var(--acc);border-radius:1rem;padding:1rem 1.2rem;margin:1.5rem 0;color:var(--fg);text-decoration:none}
.start b{color:var(--acc)}
ul{list-style:none;margin:0;padding:0}
li{display:flex;justify-content:space-between;gap:1rem;padding:.8rem 0;border-top:1px solid var(--line)}
li a{color:var(--fg)} .m{color:var(--dim);font-size:.85rem;white-space:nowrap}
small{display:block;margin-top:2rem;color:var(--dim)}</style>
</head>
<body>
<main>
<div class="top"><button type="button" class="share" id="share" aria-label="Share this page"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3v12M7 8l5-5 5 5M5 13v6a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-6"/></svg>Share</button></div>
<h1>billing.thonly.com: drawings</h1>
<p>billing.thonly.com is where you keep money for compute and storage in our apps: your balance, your history, your receipts, and the way to get back what you haven't spent.</p>
<a class="start" href="wall.html"><b>Start here</b><br>Every screen on one wall. Drag to pan, pinch to zoom, tap a screen to open it.</a>
<ul>%s</ul>
<small>These are drawings. They charge nobody, and nothing here is live. The Khmer is our own placeholder until a native reader approves it. Visits are counted without cookies. Hidden from search by named crawler; shareable by link. This site counts visits without cookies.</small>
</main>
<div id="toast" hidden>Link copied</div>
<script>
document.getElementById("share").addEventListener("click", async () => {
  const url = location.href.split("?")[0], text = document.querySelector('meta[name="description"]').content;
  try { if (navigator.share) { await navigator.share({ title: document.title, text, url }); return; } }
  catch (e) { if (e && e.name === "AbortError") return; }
  try { await navigator.clipboard.writeText(url); const t = document.getElementById("toast"); t.hidden = false; setTimeout(() => { t.hidden = true; }, 2200); }
  catch { window.prompt("", url); }
});
</script>
</body>
</html>
""" % rows
for _p, _k in (("L", "bg"), ("L", "ink"), ("L", "ink-dim"), ("L", "line"), ("D", "bg"), ("D", "ink"), ("D", "ink-dim"), ("D", "line")):
    page = page.replace("@%s_%s@" % (_p, _k.upper().replace("-", "_")), tok("%s-%s" % (_p.lower(), _k)))
assert "@L_" not in page and "@D_" not in page, "unfilled brand placeholder"
io.open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(page)
print("index.html written: %d artboards" % len(boards))

# Re-stamp the tracker reference from the file's own hash so a change is never served stale.
import subprocess as _sp
_sp.run(["python3", os.path.join(HERE, "stamp-analytics.py")], check=True)
