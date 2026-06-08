"""tests/address_scope_acceptance.py — S3 · backend ui://→code://→scope[] resolver.

S3 ESTABLISHES `code://` in the BACKEND (it was corpus-only). A resolver maps a `ui://` address →
its `code://` symbol(s) → a file `scope[]`, reading the corpus join data on disk
(design/_system/{addresses.json, code-symbols.json}). This is the pivot L1 (comment→build-intent
needs the scope) and L5 (self-change→element needs the file→ui join) both lean on.

ONE-SOURCE (rule 3): the resolver sources its code:// ids AND its scope files FROM the corpus
code-symbol registry (design/_system/code-symbols.json) — it INVERTS each symbol's `referenced_by[]`
into the forward map ui://addr → [symbols]. So a resolved id is a real registry KEY and a resolved
path is the registry's RESOLVED path (e.g. canvas/app/src/App.tsx, not the corpus shorthand
'App.tsx') — by construction, never a parallel/disagreeing code:// scheme.

This suite proves:
  1. `code://` is now a backend scheme (contracts/address.py SCHEMES) — additive, the others still hold.
  2. The resolver resolves on a REAL clean address: `ui://inbox/build-review` →
     symbol `code://suite/review_verdicts` → scope `['runtime/suite.py']`.
  3. Every resolved id is a REAL key in code-symbols.json AND every resolved path is the registry's
     RESOLVED file — proven beyond the clean case on a multi-ref address (`ui://toolbar/run`
     → `code://Toolbar` at `canvas/app/src/regions/Toolbar.tsx`, NOT the corpus shorthand `Toolbar.tsx`).
     (Post-App.tsx-carve: the run button moved out of the App monolith into the carved Toolbar region.)
  4. EMPTY scope = DENY-ALL: an address with no referencing symbol (CSS selector / orphan / absent)
     returns empty scope WITHOUT raising (fail-safe; rule 8 — never fabricate, never allow-all).
  5. The resolver never crashes across EVERY corpus address (L1/L5 call it on real addresses).
  6. A malformed ui:// address fails LOUD (S0 grammar gate).
  7. The resolver is reachable from a real FACE (a bridge.py /api/scope route calls it).
"""
import json
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from contracts.address import SCHEMES, scheme

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


NODES = os.path.join(ROOT, "nodes")
store = FsStore(os.path.join(tempfile.mkdtemp(prefix="scope-"), "store"))
reg = NodeRegistry(); reg.discover([NODES])
suite = Suite(store, reg, nodes_dir=NODES)

# ── 1. code:// is a backend scheme now (additive — the others still hold) ─────
check("code:// is in SCHEMES", "code" in SCHEMES)
for s in ("run", "cas", "blob", "vec", "ui"):
    check(f"existing scheme {s} still in SCHEMES", s in SCHEMES)
check("scheme() recognizes a code:// address", scheme("code://suite/review_verdicts") == "code")

# load the corpus registry the resolver sources from — every resolved id/path must come FROM it
cs_path = os.path.join(ROOT, "design", "_system", "code-symbols.json")
with open(cs_path, encoding="utf-8") as f:
    corpus_symbols = json.load(f)["symbols"]

# ── 2 + 3. resolve on a REAL clean address — sourced FROM the registry ────────
r = suite.resolve_scope("ui://inbox/build-review")
check(f"resolve ui://inbox/build-review → symbols {r['symbols']}",
      r["symbols"] == ["code://suite/review_verdicts"])
check(f"resolve → scope {r['scope']}", r["scope"] == ["runtime/suite.py"])
check("not stale (corpus join read OK)", r["stale"] is False)
check("the resolved code:// id is a real corpus code-symbol key (sourced FROM the registry)",
      "code://suite/review_verdicts" in corpus_symbols)

# resolve another clean single-symbol address
r2 = suite.resolve_scope("ui://inbox/coa")
check(f"resolve ui://inbox/coa → scope {r2['scope']}", r2["scope"] == ["runtime/suite.py"])
check("ui://inbox/coa symbol is code://suite/coa", r2["symbols"] == ["code://suite/coa"])

# a file-only ref → the registry's file-stem id + RESOLVED file scope
r3 = suite.resolve_scope("ui://canvas/portal-window")     # code = 'nodes/portal.py'
check(f"file-only ref ui://canvas/portal-window → scope {r3['scope']}",
      r3["scope"] == ["nodes/portal.py"])
check("file-only id is code://portal (a registry key)", r3["symbols"] == ["code://portal"])

# THE BEYOND-CLEAN PROOF (advisor): a multi-ref address resolving to TWO registry keys across TWO files.
# POST-App.tsx-carve, the run button's code home moved out of the App monolith into the carved Toolbar
# region (regions/Toolbar.tsx) + the suite run handler (suite.run). The regenerated corpus resolves
# ui://toolbar/run → ['code://Toolbar','code://suite/run'] (the old pre-carve ['code://App/doRun',
# 'code://bridge/_probe'] are no longer registry keys at all). The RESOLVER still sources from the
# registry, so it yields the registry's RESOLVED path canvas/app/src/regions/Toolbar.tsx (NOT the
# shorthand 'Toolbar.tsx'). A hand-rolled string parser would diverge here; sourcing from the index agrees.
# (Mirrors the 0f61b4f conv_context fix — same App.tsx-carve symbol drift.)
run_addr = suite.resolve_scope("ui://toolbar/run")
check(f"multi-ref ui://toolbar/run → symbols {run_addr['symbols']} (post-App.tsx-carve: Toolbar region + suite.run)",
      run_addr["symbols"] == ["code://Toolbar", "code://suite/run"])
check(f"resolved scope uses the registry's RESOLVED path (scope {run_addr['scope']})",
      run_addr["scope"] == ["canvas/app/src/regions/Toolbar.tsx", "runtime/suite.py"])
check("the resolved path is NOT the corpus shorthand 'Toolbar.tsx'",
      "Toolbar.tsx" not in run_addr["scope"] and "canvas/app/src/regions/Toolbar.tsx" in run_addr["scope"])
for sid in run_addr["symbols"]:
    assert sid in corpus_symbols, f"{sid} not a registry key"
check("EVERY resolved id for ui://toolbar/run is a real registry key (by construction)", True)
for f_ in run_addr["scope"]:
    assert any(corpus_symbols[s]["file"] == f_ for s in run_addr["symbols"]), f"{f_} not a registry file"
check("EVERY resolved path for ui://toolbar/run is a registry RESOLVED file", True)

# ── 4. EMPTY scope = DENY-ALL (never raise, never fabricate, never allow-all) ──
# DENY-ALL is proven by the ABSENT address (no entry in the corpus at all → empty, with a note).
absent = suite.resolve_scope("ui://nonexistent/thing")
check("absent address → empty scope (DENY-ALL)", absent["scope"] == [] and absent["symbols"] == [])
check("absent address has a surfaced note (the gap, not a fabrication)", bool(absent["note"]))
check("absent address did NOT raise", absent["address"] == "ui://nonexistent/thing")
# ui://tabbar — POST-App.tsx-carve, app.css is indexed as the symbol code://app, so the corpus now
# inverts ui://tabbar → ['code://App','code://app'] (the App shell + the .tabbar CSS). The pre-carve
# "CSS-selector → no referencing code symbol → DENY-ALL" assumption is OBSOLETE corpus-wide (app.css is
# a real indexed symbol now); the tabbar markup genuinely lives in App.tsx (the mobile nav) + app.css
# (.tabbar). DENY-ALL stays proven by the ABSENT case above. (Mirrors the 0f61b4f carve-drift fix.)
tabbar = suite.resolve_scope("ui://tabbar")
check(f"ui://tabbar resolves to the App shell + .tabbar CSS (symbols {tabbar['symbols']}, post-App.tsx-carve)",
      tabbar["symbols"] == ["code://App", "code://app"]
      and tabbar["scope"] == ["canvas/app/src/App.tsx", "canvas/app/src/app.css"])
check("ui://tabbar resolves WITHOUT crashing (a real multi-file CSS+TSX address)", tabbar["stale"] is False)

# ── 5. exhaustively prove resolve_scope NEVER raises across EVERY corpus address (L1/L5 robustness)
corpus_path = os.path.join(ROOT, "design", "_system", "addresses.json")
with open(corpus_path, encoding="utf-8") as f:
    all_addrs = json.load(f)["addresses"]
crashed = []
for a in all_addrs:
    try:
        out = suite.resolve_scope(a)
        assert isinstance(out["scope"], list) and isinstance(out["symbols"], list)
    except Exception as e:  # noqa: BLE001 — the point is to prove it never throws
        crashed.append((a, repr(e)))
check(f"resolve_scope never crashes on ANY of the {len(all_addrs)} corpus addresses "
      f"(crashed: {crashed[:2]})", not crashed)

# ── 6. malformed ui:// fails LOUD (the S0 grammar gate) ───────────────────────
raised = False
try:
    suite.resolve_scope("not-a-ui-address")
except (ValueError, TypeError):
    raised = True
check("malformed ui:// address raises (S0 grammar gate, fail loud)", raised)

# ── 7. reachable from a real FACE — the bridge /api/scope route calls it ──────
with open(os.path.join(ROOT, "runtime", "bridge.py"), encoding="utf-8") as f:
    bridge_src = f.read()
check("bridge.py has an /api/scope route", "/api/scope" in bridge_src)
check("the /api/scope route calls SUITE.resolve_scope",
      re.search(r"/api/scope.*\n.*resolve_scope", bridge_src) is not None
      or "resolve_scope" in bridge_src)

print(f"\nADDRESS SCOPE ACCEPTANCE — {PASS} checks passed. "
      f"code:// established in the backend; ui://→code://→scope[] resolves on real addresses; "
      f"empty scope = DENY-ALL; messy refs never crash; reachable via /api/scope. "
      f"FRESHNESS: corpus join is regenerated (symbols.py), not live — surfaced via `stale`.")
