"""Reads the vendored brand layer (brand/, guarded by scripts/check-brand.mjs). Shared by every generator here."""
import io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
EMBLEM = io.open(os.path.join(HERE, "brand", "emblem.path.txt"), encoding="utf-8").read().strip()
_TOK = io.open(os.path.join(HERE, "brand", "tokens.css"), encoding="utf-8").read()


def tok(name):
    m = re.search(r"^\s*--%s:\s*([^;]+);" % re.escape(name), _TOK, re.M)
    if not m:
        raise SystemExit("brand: brand/tokens.css has no --%s; sync the brand layer" % name)
    return re.sub(r"\s+", "", m.group(1))
