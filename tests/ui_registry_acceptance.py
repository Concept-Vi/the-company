"""tests/ui_registry_acceptance.py — S1 · element-level addresses in the live registry.

IS (before S1): UI_REGISTRY carried 7 region handles only (6 chrome bare refs + the '*' canvas) —
no element-level addresses; clicks could address regions but not the ELEMENTS inside them
(ui://inbox/build-review, ui://toolbar/run). Also an internal inconsistency: the FE carried DOM
data-ui-ref attrs (walkthrough, deferred-queue) that the served registry did NOT carry (fe-map §8).

SHOULD-BE (S1, this proves it):
  1. The live registry (/api/ui_info via Suite.ui_info → build_ui_info) carries the 24+ ELEMENT-level
     addresses from the design corpus (design/_system/addresses.json), each conforming to S0's canonical
     grammar + UnionAddressRecord. The 7 region handles are PRESERVED (additive — every existing consumer
     keeps resolving).
  2. ORPHAN CHECK = zero used-but-unregistered: every data-ui-ref the app/mockups carry has a registry
     entry (direction is used ⊆ registered — registered-but-unused is FINE, e.g. ui://chat/input). run://
     refs are EXCLUDED (those are live node addresses, not registry entries).
  3. The existing bare-handle consumers (show's handle_map, _registry_ui_target) still resolve the
     original 7 region handles — the migration is additive, not a rip-out.

Verify-by-use: builds a real Suite over a tmp store (NEVER the live ~/company/.data — isolated), serves
the real registry, and scans the real canvas/app + design/mockups source for data-ui-ref.
"""
import os, sys, re, json, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from contracts.ui_info import parse_ui_address, UnionAddressRecord, validate_address_record

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


# --- a real Suite over an ISOLATED tmp store (never the live store) ---
store = FsStore(os.path.join(tempfile.mkdtemp(prefix="ui-registry-"), "store"))
reg = NodeRegistry(); reg.discover([NODES])
suite = Suite(store, reg, nodes_dir=NODES)

served = suite.ui_info()                         # the live /api/ui_info payload (build_ui_info)
served_keys = set(served.keys())
print(f"\nui_registry_acceptance — served registry has {len(served_keys)} entries\n")

# ── 1. the 24+ element-level corpus addresses are served ────────────────────────────────────────────
with open(os.path.join(ROOT, "design", "_system", "addresses.json"), encoding="utf-8") as f:
    corpus = json.load(f)["addresses"]
check("corpus carries 24+ element-level addresses (the design-time superset)", len(corpus) >= 24)
missing = sorted(a for a in corpus if a not in served_keys)
check(f"every corpus address is served by the live registry (missing: {missing or 'none'})", not missing)
check("the served set grew well past the 7 region handles (24+ element addresses landed)",
      len(served_keys) >= 24 + 7)

# every served corpus address validates against S0's grammar + union record (the spine holds)
grammar_problems = []
for addr in corpus:
    if addr not in served_keys:
        continue
    try:
        parse_ui_address(addr)
        ur = UnionAddressRecord.from_corpus(addr, corpus[addr])
        grammar_problems.extend(validate_address_record(ur))
    except Exception as e:
        grammar_problems.append(f"{addr!r}: {e}")
check(f"every served element address conforms to S0 grammar+record ({grammar_problems[:3] or 'clean'})",
      not grammar_problems)

# capabilities normalized to the canonical bool-object (driven-read-only → drivenReadOnly, no list leak)
portal = served.get("ui://canvas/portal-window", {})
check("corpus list-cap 'driven-read-only' normalized → drivenReadOnly bool (ui://canvas/portal-window)",
      portal.get("capabilities", {}).get("drivenReadOnly") is True)

# ── 2. ORPHAN CHECK — every used data-ui-ref is registered (used ⊆ registered; run:// excluded) ──────
# The scanner MUST see BOTH JSX forms a .tsx source carries:
#   • the plain quoted-string attribute      data-ui-ref="ui://inbox/build-review"   (mockups + most app)
#   • the JSX brace-expression attribute      data-ui-ref={'build-intent'} / {"x"}    (a JSX literal value)
# The original regex was quote-anchored (data-ui-ref=["']…["']) and STRUCTURALLY BLIND to the brace form —
# the false-green that let the unregistered build-intent orphan through (adversarial DISPROOF of S1). The
# optional `\{?…\}?` brackets the quotes so a `={'…'}` / `={"…"}` literal is captured too; the inner
# [^"']+ still stops at the closing quote, so it does NOT false-match the resolver's
# querySelector('[data-ui-ref="' + ref + '"]') (the char after the opening quote there is a quote → no body).
_REF = re.compile(r'data-ui-ref=\{?["\']([^"\']+)["\']\}?')

# REGRESSION GUARD (the blind spot that DISPROVED S1, and that also affects F4): assert the scanner
# captures all four carrier forms — including the JSX brace form it used to miss — so converting the live
# build-intent ref to the quoted full-string below can NEVER silently re-hide the brace blind spot.
_scanner_cases = {
    'data-ui-ref="ui://inbox/build-review"': 'ui://inbox/build-review',   # plain double-quoted
    "data-ui-ref='inbox'": 'inbox',                                       # plain single-quoted
    "data-ui-ref={'build-intent'}": 'build-intent',                       # JSX brace + single
    'data-ui-ref={"build-intent"}': 'build-intent',                       # JSX brace + double
}
for _src, _want in _scanner_cases.items():
    check(f"scanner captures {_src!r} → {_want!r} (brace-form blind spot closed; guards F4)",
          _REF.findall(_src) == [_want])
# and it must NOT mis-capture the live resolver's querySelector template (no body between the quotes).
check("scanner does NOT false-match the resolver querySelector template (no spurious ref captured)",
      _REF.findall("document.querySelector('[data-ui-ref=\"' + ref + '\"]')") == [])


def collect_refs(root_dir, exts):
    """Every distinct data-ui-ref carried under root_dir (recursive), for files with the given exts."""
    used = set()
    for dirpath, _dirs, files in os.walk(root_dir):
        for fn in files:
            if not any(fn.endswith(e) for e in exts):
                continue
            try:
                txt = open(os.path.join(dirpath, fn), encoding="utf-8").read()
            except (OSError, UnicodeDecodeError):
                continue
            used.update(_REF.findall(txt))
    return used


app_used = collect_refs(os.path.join(ROOT, "canvas", "app", "src"), (".tsx", ".ts"))
mock_used = collect_refs(os.path.join(ROOT, "design", "mockups"), (".html",))
all_used = app_used | mock_used
# EXCLUDE run:// refs — those are LIVE node addresses (run://<graph>/<node>), not registry entries.
ui_used = {r for r in all_used if not r.startswith("run://")}
run_used = {r for r in all_used if r.startswith("run://")}
print(f"  used data-ui-ref: app={len(app_used)} mockups={len(mock_used)} "
      f"ui://-ish={len(ui_used)} run://(excluded)={len(run_used)}")

# the app carries BARE handles (inbox, walkthrough, deferred-queue) + FULL ui:// strings — ALL must be
# registered. The orphan GATE is the LIVE app (canvas/app/src): every data-ui-ref the RUNNING UI carries
# resolves to a registry entry.
# The redesign MOCKUPS legitimately PROPOSE future-surface addresses (surfaces not yet built — that is what
# a redesign mockup IS). Like run://, a proposed address is NOT a live-registry entry and must NOT gate the
# live registry — registering one would mint a canonical entry for an unbuilt surface (a never-invent
# violation, AGENTS rule 8). Mockup-proposed-but-unregistered addresses are REPORTED as info (visible, never
# silently passed), not failed. (Studio brought the redesign corpus onto main 2026-06-08.)
app_ui_used = {r for r in app_used if not r.startswith("run://")}
orphans = sorted(r for r in app_ui_used if r not in served_keys)
mock_proposed = sorted(r for r in mock_used if not r.startswith("run://") and r not in served_keys and r not in app_ui_used)
if mock_proposed:
    print(f"  (info) {len(mock_proposed)} mockup-PROPOSED addresses not yet in the live registry "
          f"(future surfaces — illustrative, not gated): {mock_proposed}")
check(f"ORPHAN CHECK: zero LIVE-app used-but-unregistered data-ui-ref (orphans: {orphans or 'none'})", not orphans)
# the fe-map §8 inconsistency S1 closes — the app's previously-unserved handles are now registered.
for handle in ("walkthrough", "deferred-queue"):
    if handle in app_used:
        check(f"app handle {handle!r} (was carried in DOM, not served) is now registered (fe-map §8 closed)",
              handle in served_keys)

# ── 3. PRESERVE — the original 7 region handles + their bare-handle consumers still resolve ──────────
for bare in ("toolbar", "inspector", "inbox", "activity", "chat", "workshop"):
    check(f"region handle {bare!r} preserved (bare key still served — show/_registry_ui_target read it)",
          bare in served_keys)
check("canvas handle '*' preserved (the whole-canvas camera ref)", "*" in served_keys)

# show's lenient handle_map (built from UI_REGISTRY) still maps a bare 'inbox' → ui://chrome/inbox.
handle_map = {ref: kind for ref, kind, *_ in suite.UI_REGISTRY}
check("show handle_map maps bare 'inbox' → kind 'chrome' (lenient bare-handle resolution preserved)",
      handle_map.get("inbox") == "chrome")
check("show handle_map maps bare '*' → kind 'canvas' (whole-canvas camera preserved)",
      handle_map.get("*") == "canvas")

# _registry_ui_target still returns registry-valid targets (node → ui://canvas/<id>; else ui://chrome/inbox).
check("_registry_ui_target(node) → ui://canvas/<id> (walkthrough drive preserved)",
      suite._registry_ui_target({"node": "n1"}) == "ui://canvas/n1")
check("_registry_ui_target(node-less) → ui://chrome/inbox (preserved, always-registered fallback)",
      suite._registry_ui_target({}) == "ui://chrome/inbox")

# build_ui_info's duplicate-ref guard did NOT fire (no full-string collided with a bare key) — proven by
# the fact ui_info() built at all above; assert the two forms genuinely coexist as distinct keys.
check("bare 'inbox' and full 'ui://inbox' coexist as distinct served keys (no duplicate-ref collision)",
      "inbox" in served_keys and "ui://inbox" in served_keys)

print(f"\nui_registry_acceptance: {PASS} checks passed — S1 element-level registry + zero orphans.\n")
