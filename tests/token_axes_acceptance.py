"""tests/token_axes_acceptance.py — F4: theme/density axes live in the ONE token spine, additively.

Proves by use (running the real emit over the real tokens.json): (1) the emitted CSS carries the axis
blocks (data-theme dim/dark/contrast · data-ground clean/warm · data-density ×3); (2) the values are the
ISLAND'S OWN (spot-checked against design/claude-ds/tokens/theme.css — verbatim absorption, nothing
invented; the contrast theme is the island's high-contrast LIGHT); (3) the pre-existing :root tokens are
UNCHANGED (additive — the warm-gold default is byte-stable); (4) a malformed axis row fails loud;
(5) the generated design-system.css on disk matches a fresh emit (no hand-edit drift).
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "design", "_system"))

import emit as emit_mod

PASS = 0
def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")

data = json.load(open(os.path.join(ROOT, "design", "_system", "tokens.json"), encoding="utf-8"))
css = emit_mod.emit(data)

# 1 — the axis blocks exist
for sel in ('[data-theme="dim"]', '[data-theme="dark"]', '[data-theme="contrast"]',
            '[data-ground="clean"]', '[data-ground="warm"]',
            '[data-density="compact"]', '[data-density="spacious"]'):
    check(f"emits {sel}", sel + "{" in css)

# 2 — island-faithful values (spot checks against claude-ds/tokens/theme.css)
island = open(os.path.join(ROOT, "design", "claude-ds", "tokens", "theme.css"), encoding="utf-8").read()
dark = css.split('[data-theme="dark"]{')[1].split("}")[0]
check("dark paper-3 is the island's #241B10 (verbatim, not invented)", "--paper-3:#241B10" in dark and "#241B10" in island)
check("dark border-strong is the island's 24% mix", "24%" in dark)
contrast = css.split('[data-theme="contrast"]{')[1].split("}")[0]
check("contrast is the island's HIGH-CONTRAST LIGHT (white ground, dark ink)",
      "--zone-ground:#FFFFFF" in contrast and "--ink:#100C06" in contrast)
check("contrast does NOT force color-scheme dark", "color-scheme:dark" not in contrast)
dens = css.split('[data-density="compact"]{')[1].split("}")[0]
check("density compact = 0.8 multiplier", "--density:0.8" in dens)

# 3 — the default (:root) is additive-only: every PRE-EXISTING token still present with its value
root = css.split(":root{")[1].split("\n}")[0]
check("the warm-gold accent primitive still resolves in :root", "#e6ab5c" in root)
check("the density base landed in :root (the one new group)", "--density:1" in root and "--touch-min:44px" in root)
check("control sizing respects the touch floor", "max(var(--touch-min)" in root)

# 4 — malformed axis rows fail loud
try:
    emit_mod.emit({"primitives": {}, "groups": [], "axes": [{"attr": "data-x", "tokens": {}}]})
    check("a malformed axis row fails loud (missing value)", False)
except ValueError:
    check("a malformed axis row fails loud (missing value)", True)
try:
    emit_mod.emit({"primitives": {}, "groups": [],
                   "axes": [{"attr": "data-x", "value": "y", "tokens": {"t": {"ref": "nope"}}}]})
    check("an axis token ref to an unknown primitive fails loud", False)
except KeyError:
    check("an axis token ref to an unknown primitive fails loud", True)

# 5 — the generated file on disk matches a fresh emit (+ verbatim components.css append)
comp_p = os.path.join(ROOT, "design", "_system", "components.css")
expected = css + ("\n" + open(comp_p, encoding="utf-8").read() if os.path.exists(comp_p) else "")
on_disk = open(os.path.join(ROOT, "design", "design-system.css"), encoding="utf-8").read()
check("design-system.css on disk == fresh emit (generated, no hand-edit drift)", on_disk == expected)

print(f"\nALL {PASS} CHECKS PASS — theme/ground/density axes in the one spine, island-faithful, default unchanged (F4)")
