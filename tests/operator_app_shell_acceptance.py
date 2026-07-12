"""operator_app_shell_acceptance — static teeth for the operator app shell (B1+B2, K0 contract).

Three gates, all structural (no server needed):
  (a) K0 ZERO raw hex/px: no hardcoded colour (#hex / rgb(a)) or px literal in any operator/app
      source file (.ts/.tsx/.css/.html under src/ + index.html). var(--x) references, CSS keywords,
      and token names are the only styling vocabulary. (design/_system/check.py --target only scans
      .tsx/.css — this app is mostly .ts/.tsx/.html, so this is a focused grep with the same law.)
  (b) B1 the bridge mount exists: /app, /app/, /ds/ are DECLARED in bridge.BRIDGE_ROUTES (the
      registry-is-truth route table; tests/bridge_routes_acceptance.py separately proves declared ==
      dispatched, so declaration here implies the routes are real).
  (c) K0 ONE stylesheet chain: operator/app/index.html links EXACTLY ONE stylesheet — /ds/styles.css
      (the DS's single entry) — and carries no <style> block or style= attribute.

Run: ./.venv/bin/python tests/operator_app_shell_acceptance.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

APP = os.path.join(ROOT, "operator", "app")

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}  {detail}")


print("=== operator_app_shell_acceptance — the shell obeys K0 + B1 (static teeth) ===")

# ---- (a) zero raw hex/px in the app's sources --------------------------------------------------
_HEX = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b")
_PX = re.compile(r"\b\d+px\b")
_RGBA = re.compile(r"rgba?\([^)]*\)")

sources = [os.path.join(APP, "index.html")]
for dirpath, dirnames, filenames in os.walk(os.path.join(APP, "src")):
    for fn in filenames:
        if fn.endswith((".ts", ".tsx", ".css", ".html", ".jsx")):
            sources.append(os.path.join(dirpath, fn))

check("app sources found (src/ is not empty)", len(sources) > 3, f"only {len(sources)} files")

offenders = []
for fp in sources:
    text = open(fp, encoding="utf-8").read()
    for rx, kind in ((_HEX, "hex"), (_PX, "px"), (_RGBA, "rgb")):
        for m in rx.finditer(text):
            # var(--x, fallback) ghosts count too — there is no allowance for a literal ANYWHERE
            offenders.append(f"{os.path.relpath(fp, ROOT)}: {kind} literal {m.group(0)!r}")
check("ZERO raw hex/px/rgb literals in operator/app sources (K0)", not offenders,
      "\n    " + "\n    ".join(offenders[:12]))

# ---- (b) the bridge mount is declared (registry-is-truth) --------------------------------------
from runtime import bridge  # noqa: E402

declared = set(bridge.BRIDGE_ROUTES)
check('"/app" is a declared bridge route (B1)', "/app" in declared)
check('"/app/" is a declared bridge route (B1 assets/SPA)', "/app/" in declared)
check('"/ds/" is a declared bridge route (the DS home, K0 one-chain serving)', "/ds/" in declared)
check("the served paths exist: APP_DIST + DS_DIR constants point where they claim",
      bridge.APP_DIST == os.path.join(ROOT, "operator", "app", "dist")
      and bridge.DS_DIR == os.path.join(ROOT, "design", "claude-ds")
      and os.path.isdir(bridge.DS_DIR))

# ---- (c) index.html links ONLY the DS chain -----------------------------------------------------
html = open(os.path.join(APP, "index.html"), encoding="utf-8").read()
links = re.findall(r'<link\s[^>]*rel="stylesheet"[^>]*>', html)
hrefs = [re.search(r'href="([^"]+)"', l).group(1) for l in links if re.search(r'href="([^"]+)"', l)]
check("index.html has EXACTLY ONE stylesheet link", len(hrefs) == 1, f"found {hrefs}")
check("…and it is the DS chain (/ds/styles.css)", hrefs == ["/ds/styles.css"], f"found {hrefs}")
check("index.html carries no <style> block (no second styling home)", "<style" not in html)
check("index.html carries no style= attribute", not re.search(r'\sstyle="', html))

print(f"\n{'PASS' if FAIL == 0 else 'FAIL'} — {PASS} passed, {FAIL} failed")
sys.exit(0 if FAIL == 0 else 1)
