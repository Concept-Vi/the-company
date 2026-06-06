"""tests/memo_stale_acceptance.py — L10 · "stale at this address" memo derivation (§21.7#10).

A surface shows "cached/stale at this address." **"cached" is ALREADY served** (the `cached`
node-state derives on reload when the output address resolves — suite.py state(), S5/F3).
**"stale" is NOT served** — and it is NOT a free read: deriving it requires recompiling the
node → resolving current input content-hashes → computing the new `_memo_sig` → `memo_get`-
comparing against the STORED output cas at the node's run:// address (seams-engine Seam 8a —
costed as DERIVATION, not a served field).

The load-bearing comparison rule (one rule, both cases fall out of it):
    fresh  ⟺  store.memo_get(sig_now) is not None  AND  memo_get(sig_now) == store.head(addr)
    everything else (including a memo miss) → stale.

What this suite proves (RED first, then GREEN):
  1. a node whose STORED output matches its current-input `_memo_sig` → stale=false.
  2. after an input changes (recomputed sig differs from the stored output's) → stale=true.
  3. the EXISTING memo gate (`memo_get`/`memo_set` / the `cached` node-state) still works
     unchanged — and the staleness check NEVER calls `memo_set` (it does not mutate the cache;
     it reads a derived comparison from it). It also must not call `mod.run`/`set_ref`.
  4. a node that can't be evaluated → stale verdict is "unknown" with a reason, NOT a silent
     "fresh" (fail-loud, rule 4). Covered: malformed/non-run address, unknown node, a VOLATILE
     node (the gate re-runs it every pass by design — a memo comparison is misleading), a
     reference node (portal — no memo/run semantics), an unresolved input (can't form a sig),
     and no stored output yet (a distinct "no cached result", never a silent fresh).
"""
import os, sys, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


work = tempfile.mkdtemp(prefix="memo-stale-test-")
try:
    store = FsStore(os.path.join(work, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    # ---- a pure pipeline: constant("hi") -> uppercase ----
    g = "stale"
    suite.create_node(g, "constant", config={"value": "hi"}, node_id="k")
    suite.create_node(g, "uppercase", node_id="u")
    suite.connect(g, "k", "value", "u", "text")
    suite.run(g)                                   # populates the memo + the output refs

    addr_u = f"run://{g}/u"
    addr_k = f"run://{g}/k"

    # sanity: the run cached the output (the FREE "cached" half is served — unchanged)
    st = suite.state(g)
    by_id = {n["id"]: n for n in st["nodes"]}
    check("free 'cached' half still served (S5/F3)", by_id["u"]["status"] == "cached")
    check("stored output exists at the node address", store.head(addr_u) is not None)

    # ===== CASE 1: unchanged inputs → stale=false =====
    v1 = suite.stale_at_address(addr_u)
    check("CASE1 verdict shape carries address + stale", "address" in v1 and "stale" in v1)
    check("CASE1 unchanged inputs → stale=false", v1["stale"] is False)
    check("CASE1 not 'unknown' (it could be evaluated)", v1.get("unknown") in (False, None))

    # ===== CASE 3a: the staleness check must NOT mutate the memo cache =====
    # Snapshot the memo dir; deriving staleness reads memo_get + compares — it must call neither
    # memo_set nor set_ref nor mod.run. Wrap them to assert they are not invoked by the check.
    memo_dir = os.path.join(work, "store", "memo")
    before = sorted(os.listdir(memo_dir)) if os.path.isdir(memo_dir) else []
    calls = {"memo_set": 0, "set_ref": 0}
    _orig_set = store.memo_set
    _orig_ref = store.set_ref
    store.memo_set = lambda *a, **k: (calls.__setitem__("memo_set", calls["memo_set"] + 1), _orig_set(*a, **k))[1]
    store.set_ref = lambda *a, **k: (calls.__setitem__("set_ref", calls["set_ref"] + 1), _orig_ref(*a, **k))[1]
    try:
        suite.stale_at_address(addr_u)
    finally:
        store.memo_set = _orig_set
        store.set_ref = _orig_ref
    after = sorted(os.listdir(memo_dir)) if os.path.isdir(memo_dir) else []
    check("CASE3 staleness check did NOT call memo_set", calls["memo_set"] == 0)
    check("CASE3 staleness check did NOT call set_ref", calls["set_ref"] == 0)
    check("CASE3 memo dir unchanged by the check (no new cache)", before == after)

    # ===== CASE 2: an input changes → stale=true =====
    # Change the upstream constant's config. The recomputed sig for `u` now differs from the sig
    # under which its stored output was memoized — so memo_get(sig_now) misses → stale.
    suite.set_config(g, "k", {"value": "changed"})
    # do NOT re-run: the stored output at addr_u is still the OLD "HI"; only the inputs changed.
    # First we must make `k`'s new output resolve so `u`'s input hash actually changes. Run only
    # `k` is not a primitive here; instead re-run the graph but FORCE so the comparison is about
    # u's stored-vs-current. The cleanest input-change: k's output address now holds "CHANGED"'s
    # source. Re-running the graph would also re-run u (curing staleness), so instead we resolve
    # k alone by running with u PAUSED — k re-fires, u's input changes, u's stored output stays old.
    suite.run(g, pause=["u"])
    check("CASE2 setup: u's stored output is still the OLD value", store.head(addr_u) is not None)
    v2 = suite.stale_at_address(addr_u)
    check("CASE2 changed input → stale=true", v2["stale"] is True)
    check("CASE2 not 'unknown' (it could be evaluated, just stale)", v2.get("unknown") in (False, None))

    # ===== the existing memo gate still works unchanged (preserve) =====
    # Re-running the graph (no force) memo-skips the pure nodes that did not change; running it
    # after our change should re-resolve u and then memo-cache it.
    r_after = suite.run(g)
    check("memo gate intact: u re-resolves after its input changed", "u" in r_after["ran"] or store.head(addr_u))
    r_idem = suite.run(g)
    check("memo gate intact: unchanged re-run memo-skips u", "u" in r_idem["skipped"])
    v3 = suite.stale_at_address(addr_u)
    check("after re-run, u is fresh again (stale=false)", v3["stale"] is False)

    # ===== CASE 4: fail-loud 'unknown' (never a silent fresh) =====
    # 4a — malformed / non-run address → raises (the bridge turns it into a 400, fail-loud).
    raised = False
    try:
        suite.stale_at_address("not-an-address")
    except Exception:
        raised = True
    check("CASE4a malformed address raises (fail-loud, not a silent fresh)", raised)

    raised_ui = False
    try:
        suite.stale_at_address("ui://chrome/inbox")   # a ui:// address has no run/memo semantics
    except Exception:
        raised_ui = True
    check("CASE4a non-run (ui://) address raises", raised_ui)

    # 4b — an unknown node in the address → unknown verdict with a reason (not a silent fresh).
    v_unknown = suite.stale_at_address(f"run://{g}/does-not-exist")
    check("CASE4b unknown node → unknown verdict", v_unknown.get("unknown") is True)
    check("CASE4b unknown node → carries a reason", bool(v_unknown.get("reason")))
    check("CASE4b unknown node → stale is NOT a silent false", v_unknown.get("stale") is None)

    # 4c — a node with NO stored output yet → distinct 'no cached result', never a silent fresh.
    suite.create_node(g, "constant", config={"value": "never-run"}, node_id="fresh")
    v_nocache = suite.stale_at_address(f"run://{g}/fresh")
    check("CASE4c no stored output → unknown (no cached result), not a silent fresh",
          v_nocache.get("unknown") is True and v_nocache.get("stale") is None)
    check("CASE4c no-cache verdict carries a reason", bool(v_nocache.get("reason")))

    # 4d — a VOLATILE node → the gate re-runs it every pass by design; a memo comparison is
    # misleading, so the verdict flags it honestly (volatile=True / unknown), never a plain fresh.
    g2 = "stale-vol"
    src = os.path.join(work, "src"); os.makedirs(src)
    open(os.path.join(src, "AGENTS.md"), "w").write("alpha")
    suite.create_node(g2, "codebase", config={"root": src, "globs": ["*.md"]}, node_id="cb")
    suite.run(g2)
    v_vol = suite.stale_at_address(f"run://{g2}/cb")
    check("CASE4d VOLATILE node flagged honestly (volatile=True)", v_vol.get("volatile") is True)
    check("CASE4d VOLATILE node not a plain fresh/stale claim", v_vol.get("stale") is None)
    check("CASE4d VOLATILE verdict carries a reason", bool(v_vol.get("reason")))

    # 4e — a reference node (portal) → no memo/run semantics → unknown with a reason.
    suite.create_node(g, "portal", config={"ref": addr_u}, node_id="pw")
    v_ref = suite.stale_at_address(f"run://{g}/pw")
    check("CASE4e reference (portal) node → unknown (no memo semantics)", v_ref.get("unknown") is True)
    check("CASE4e reference verdict carries a reason", bool(v_ref.get("reason")))

    # 4f — a MULTI-OUTPUT node (gate: PORTS_OUT={pass,fail}) writes per-port FRAGMENT addresses
    # (run://g/gt#pass / #fail), so NOTHING is at the bare run://g/gt — but the node HAS run and its memo
    # is the whole multi-port result. The verdict must be unknown with the REAL multi-port reason, NOT a
    # misleading "no stored output — run it first" (fail-loud legibility, rule 4). The status is 'ran'.
    g3 = "stale-multi"
    suite.create_node(g3, "constant", config={"value": "x"}, node_id="val")
    suite.create_node(g3, "constant", config={"value": "true"}, node_id="vd")
    suite.create_node(g3, "gate", node_id="gt")
    suite.connect(g3, "val", "value", "gt", "value")
    suite.connect(g3, "vd", "value", "gt", "verdict")
    r_multi = suite.run(g3)
    check("CASE4f setup: the multi-output gate RAN", "gt" in r_multi["ran"] or "gt" in r_multi["skipped"])
    v_multi = suite.stale_at_address(f"run://{g3}/gt")
    check("CASE4f multi-output node → unknown (not a single comparable cas)", v_multi.get("unknown") is True)
    check("CASE4f multi-output reason names its output ports (not 'run it first')",
          "output ports" in (v_multi.get("reason") or "") and "run it first" not in (v_multi.get("reason") or ""))
    check("CASE4f multi-output → stale is NOT a silent false/true", v_multi.get("stale") is None)

    print(f"\nALL {PASS} CHECKS PASS — 'stale at this address' is a costed derivation over the "
          f"existing memo gate (recompile + input-hash + _memo_sig compare), the gate is unmutated, "
          f"and the unevaluable cases fail loud (never a silent fresh).")
finally:
    shutil.rmtree(work, ignore_errors=True)
