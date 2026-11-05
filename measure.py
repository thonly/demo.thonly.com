#!/usr/bin/env python3
"""Measure every board's rendered height in headless Chrome and write heights.json (read by build-boards.py).

    python3 -m http.server 8333 &   python3 measure.py
A board's frame on the wall is max(844, its content), so a longer Khmer screen is shown whole, never cut.
"""
import glob, io, json, os, re, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# The board list comes from canvas.json, never a filename pattern: a pattern silently skipped every new prefix once.
_ab = json.load(io.open(os.path.join(HERE, "canvas.json"), encoding="utf-8"))["artboards"]
boards = [os.path.join(HERE, b["file"]) for b in _ab]
WIDTH = dict((b["file"], b["w"]) for b in _ab)  # a desktop board is measured at its own width, never 390
probe = "<!doctype html><meta charset=utf-8><body>" + "".join(
    '<iframe src="%s" style="width:%dpx;height:400px;border:0" data-f="%s"></iframe>' % (os.path.basename(f), WIDTH[os.path.basename(f)], os.path.basename(f)) for f in boards
) + """<pre id=out></pre><script>
onload=()=>{const o={};for(const i of document.querySelectorAll('iframe'))o[i.dataset.f]=i.contentDocument.documentElement.scrollHeight;
document.getElementById('out').textContent='H='+JSON.stringify(o)+'=H'}</script>"""
io.open(os.path.join(HERE, "_measure.html"), "w", encoding="utf-8").write(probe)
dom = subprocess.run([CHROME, "--headless", "--disable-gpu", "--virtual-time-budget=5000", "--dump-dom",
                      "http://localhost:8333/_measure.html"], capture_output=True, text=True).stdout
os.remove(os.path.join(HERE, "_measure.html"))
m = re.search(r"H=(\{.*?\})=H", dom)
assert m, "measurement failed: no heights in the dumped DOM"
h = json.loads(m.group(1))
assert len(h) == len(boards) and all(v > 0 for v in h.values()), h
io.open(os.path.join(HERE, "heights.json"), "w").write(json.dumps(h, sort_keys=True))
print("heights.json: %d boards, tallest %s" % (len(h), max(h.items(), key=lambda kv: kv[1])))
