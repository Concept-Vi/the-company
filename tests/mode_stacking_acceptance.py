"""tests/mode_stacking_acceptance.py — WS3 acceptance: mode stacking (base + overlays).

A presence mode can be STACKED: a base mode + a list of OVERLAYS, where an overlay is a PARTIAL axis-
override dict (declares only what it changes). resolve_mode_stack folds base+overlays → one resolved mode
row; every per-mode consumer reads the fold, so an overlay can refine ANY axis. DEPTH-1 (no overlays) is
BYTE-IDENTICAL to pre-WS3 — the load-bearing safety property.

THE GOLDEN MASTER (the gate): the precomputed MODE_SPECS / PART_GRAIN / ACTIVATION_ALLOCATION /
MODE_DIRECTIVES are KEPT as the oracle; for ALL 8 modes × the 7 consumers, the fold-derived value with
overlays=[] must equal the precomputed value. This is what makes the reroute of live per-turn reads safe.

WS3's honest bar (no consumer pushes overlays yet): MECHANISM correct + depth-1 byte-identical + fold
unit-tested. NOT "proven on real operational use" (nothing stacks in production yet).

Run: `python3 tests/mode_stacking_acceptance.py`  (exit 0 = all green).
"""
import os
import sys
import tempfile
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "ops", "cli"))

PASS, FAIL = [], []


def ok(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  — {detail}" if detail and not cond else ""))


os.environ["COMPANY_CAP_LOAD_FROM_LEDGER"] = "0"

from runtime.suite import Suite
from runtime.registry import NodeRegistry
from store.fs_store import FsStore

NODES = os.path.join(ROOT, "nodes")
store_dir = tempfile.mkdtemp(prefix="mode-stack-test-")
exit_code = 1
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    # ── T1 — depth-1 row identity ────────────────────────────────────────────────────────────────────
    print("\n[T1] resolve_mode_stack(mode) with NO overlays == mode_registry(mode) (structural identity)")
    bad = [m for m in suite.MODES if suite.resolve_mode_stack(m) != suite.mode_registry(m)]
    ok("T1a all 8 modes: folded row (depth-1) deep-equals the base row", not bad, f"differ: {bad}")

    # ── T2 — _stack_spec depth-1 == precomputed MODE_SPECS (resolution_spec_for/set_submode source) ──
    print("\n[T2] _stack_spec(mode) (depth-1) value-equals the precomputed MODE_SPECS[mode]")
    badspec = [m for m in suite.MODES if suite._stack_spec(m) != suite.MODE_SPECS[m]]
    ok("T2a all 8 modes: folded ModeSpec equals the oracle ModeSpec", not badspec, f"differ: {badspec}")

    # ── T3 — derived-slice identity vs the precomputed dicts ─────────────────────────────────────────
    print("\n[T3] fold-derived slices equal the precomputed PART_GRAIN/ACTIVATION_ALLOCATION/MODE_DIRECTIVES")
    d3 = []
    for m in suite.MODES:
        row = suite.resolve_mode_stack(m)
        if row["directive"] != suite.MODE_DIRECTIVES[m]:
            d3.append(f"{m}:directive")
        pg = suite.PART_GRAIN[m]
        if (row["grain"], row["shape"], row["stage"]) != (pg["grain"], pg["shape"], pg["stage"]):
            d3.append(f"{m}:grain/shape/stage")
        aa = suite.ACTIVATION_ALLOCATION[m]
        if {k: row[k] for k in aa} != aa:
            d3.append(f"{m}:allocation")
    ok("T3a all derived slices match the oracle", not d3, f"differ: {d3}")

    # ── T4 — THE GOLDEN MASTER: the consumer METHODS match the precomputed oracle (all 8 × 7) ────────
    print("\n[T4] GOLDEN MASTER — every consumer method (depth-1) equals the precomputed oracle")
    g = []
    for m in suite.MODES:
        if suite._mode_directive(m) != suite.MODE_DIRECTIVES[m]:
            g.append(f"{m}:_mode_directive")
        pg = suite.PART_GRAIN[m]
        if suite.grain_for(m) != pg["grain"]:
            g.append(f"{m}:grain_for")
        if suite.shape_for(m) != dict(suite.THOUGHT_SHAPES[pg["shape"]]):
            g.append(f"{m}:shape_for")
        if suite.mode_stages(m) != bool(pg["stage"]):
            g.append(f"{m}:mode_stages")
        raw = suite.ACTIVATION_ALLOCATION[m]
        exp = {k: (list(v) if isinstance(v, list) else v) for k, v in raw.items()}
        if "per-turn" not in exp["live"]:
            exp["live"] = ["per-turn"] + exp["live"]
        if suite.activation_allocation(m) != exp:
            g.append(f"{m}:activation_allocation")
        spec = suite.MODE_SPECS[m]
        base = dict(spec.resolution or {})
        exp_res = {"strata": base.get("strata"), "howto_detail": base.get("howto_detail", "full"),
                   "budget": base.get("budget")}
        # set this mode (clears overlays + submode is None on a fresh node) then read the live resolver
        suite.set_mode(m)
        if suite.resolution_spec_for(m, None) != exp_res:
            g.append(f"{m}:resolution_spec_for")
    ok("T4a all 8 modes × 7 consumers equal the oracle (reroute preserved)", not g, f"DRIFT: {g}")

    # ── T5 — the FOLD actually applies an overlay ────────────────────────────────────────────────────
    print("\n[T5] an overlay refines the resolved stack (resolution merge + non-overlaid axis unchanged)")
    suite.set_mode("listening")
    base_grain = suite.grain_for("listening")
    suite.push_overlay({"resolution": {"budget": 4321}})
    folded = suite.resolve_mode_stack("listening")
    ok("T5a overlay merged resolution.budget", folded["resolution"].get("budget") == 4321, f"{folded['resolution']}")
    ok("T5b resolution_spec_for reflects the overlay", suite.resolution_spec_for("listening", None).get("budget") == 4321)
    ok("T5c a non-overlaid axis (grain) is unchanged", suite.grain_for("listening") == base_grain)
    ok("T5d resolution MERGE kept the base sub-keys (howto_detail still 'full')",
       folded["resolution"].get("howto_detail") == "full", f"{folded['resolution']}")
    suite.push_overlay({"directive": "OVERLAID"})
    ok("T5e a scalar axis (directive) is REPLACED by the overlay", suite._mode_directive("listening") == "OVERLAID")

    # ── T6 — subtypes merge per sub-key ──────────────────────────────────────────────────────────────
    print("\n[T6] subtypes dict-merge per sub-key (overlay adds/changes one subtype, keeps the rest)")
    suite.set_mode("listening")     # clears overlays
    suite.push_overlay({"subtypes": {"general": {"budget": 77}}})
    folded = suite.resolve_mode_stack("listening")
    ok("T6a overlay set subtypes.general.budget", folded["subtypes"].get("general") == {"budget": 77}, f"{folded['subtypes']}")
    ok("T6b the base subtype 'deep' is preserved (per-sub-key merge, not replace)",
       folded["subtypes"].get("deep") == {"budget": 8000}, f"{folded['subtypes']}")

    # ── T7 — unknown overlay axis fails loud ─────────────────────────────────────────────────────────
    print("\n[T7] an overlay touching an unknown axis FAILS LOUD (no silent no-op)")
    try:
        suite.push_overlay({"not_an_axis": 1})
        ok("T7a unknown axis RAISES", False, "did not raise")
    except ValueError as e:
        ok("T7a unknown axis RAISES", "unknown axis" in str(e), f"msg={str(e)[:120]!r}")

    # ── T8 — set_mode clears overlays ────────────────────────────────────────────────────────────────
    print("\n[T8] a mode switch clears overlays (fresh presence gesture)")
    suite.set_mode("listening")
    suite.push_overlay({"directive": "X"})
    ok("T8a overlay present before switch", len(suite.get_overlays()) == 1)
    suite.set_mode("focus")
    ok("T8b overlays cleared after set_mode", suite.get_overlays() == [])
    ok("T8c resolved stack is back to the bare base", suite.resolve_mode_stack("focus") == suite.mode_registry("focus"))

    # ── T9 — overlay API (push/pop/clear/get) ────────────────────────────────────────────────────────
    print("\n[T9] overlay API: push/pop/clear/get are consistent")
    suite.set_mode("listening")
    suite.push_overlay({"directive": "a"}); suite.push_overlay({"directive": "b"})
    ok("T9a push grows the stack", len(suite.get_overlays()) == 2)
    suite.pop_overlay()
    ok("T9b pop shrinks the stack", len(suite.get_overlays()) == 1)
    suite.clear_overlays()
    ok("T9c clear empties the stack", suite.get_overlays() == [])

    print(f"\n[RESULT] {len(PASS)} pass / {len(FAIL)} fail")
    exit_code = 1 if FAIL else 0
    if FAIL:
        print("FAILED: " + ", ".join(FAIL))
finally:
    shutil.rmtree(store_dir, ignore_errors=True)

sys.exit(exit_code)
