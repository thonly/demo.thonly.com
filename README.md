# demo.thonly.com

Drawings of `billing.thonly.com`: the balance for compute and storage, in English and Khmer, with one dark pass. These are drawings. They charge nobody, nothing here is live, and every name and amount is made up.

**Front door:** <https://demo.thonly.com/> · **The wall** (every screen at once): <https://demo.thonly.com/wall.html>

## Rebuild

```sh
python3 -m http.server 8333 &      # measure.py reads the boards over HTTP
python3 build-boards.py            # the boards + board.css + canvas.json, from the brand layer
python3 measure.py                 # each board's real height → heights.json
python3 build-boards.py            # again, so canvas.json carries the measured heights
python3 build-index.py && python3 build-wall.py   # the front door and the wall, generated from canvas.json
python3 build-og.py && python3 build-icons.py     # the link-preview card, the icons, the manifest
node scripts/check-brand.mjs       # the vendored brand layer still matches brand.lock
```

⛔ Never hand-edit a generated file (`*.html`, `board.css`, `canvas.json`, `heights.json`). Edit `build-boards.py` or `board.base.css`.

## What the build refuses

*Sign in*, the regulated words, a named currency, *running low*, *free*, and any internal name, in the rendered text of every board. In Khmer, the word for a bank is allowed only of the reader's own bank.

The Khmer is our own draft until a native reader approves it, and every Khmer board says so. Where a drawing and the memory disagree, memory is canonical. The spec these follow is private. This repo is public.
