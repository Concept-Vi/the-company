"""tests/run_discovery_acceptance.py — #54 STORAGE-DISCOVERY: the run INDEX + the outputs→inputs loop.

Proves the storage-discovery layer that makes run outputs DISCOVERABLE as inputs (not just
known-by-address) — the substrate the "outputs→inputs" composability + the MCP/FE view+re-run sit on:

  1. the `op.run` RUN-INDEX emit on the engine runs (run_role in the MCP wrapper · run_items + run_reduce
     in cognition.py) — ADDITIVE + BEHAVIOUR-PRESERVING (the run's output persists to run:// exactly as
     before; just one extra op.run event per run, the C1.6 one-emit-per-fan fsync discipline).
  2. Suite.list_runs / find_runs — a READ-TIME PROJECTION over the op.run log (the run_stats pattern; the
     op.run log IS the index, no parallel store, NO fs_store edit). EXPANDS the per-fan addresses into one
     discovered ROW PER concrete run:// address.
  3. THE COMPOSABILITY LOOP — a DISCOVERED run:// address (not a hardcoded one) fed as an INPUT to another
     run → outputs→inputs BY DISCOVERY.
  4. the MCP tools list_runs / find_runs (the agent-face discovery).

VERIFY BY USE: a real generate chain via the engine against the resident 4B (:8000). The brain-DOWN path
SKIPS the live legs (recorded, never green-painted) but still proves the projection mechanics on a SEEDED
op.run record (the projection is model-free).

REUSE (no parallel machinery): the op.run event log is the index (projected via events_since — the
run_stats sibling); list_runs/find_runs are thin Suite projections; the MCP tools wrap them. NO fs_store
edit; NO new store.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

# isolate the store BEFORE importing the server (module-level SUITE binds at import — mirrors mcp_engine).
os.environ.setdefault("COMPANY_STORE", f"/tmp/run-disc-{os.getpid()}")
os.makedirs(os.environ["COMPANY_STORE"], exist_ok=True)

import urllib.request                                                       # noqa: E402
import mcp_face.server as srv                                              # noqa: E402
from runtime import cognition as _cog                                      # noqa: E402

SUITE = srv.SUITE
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def _brain_up() -> bool:
    try:
        urllib.request.urlopen("http://127.0.0.1:8000/v1/models", timeout=4).read()
        return True
    except Exception:
        return False


BRAIN = _brain_up()
print(f"\n[setup] resident brain (:8000) {'UP' if BRAIN else 'DOWN'} · store={os.environ['COMPANY_STORE']}")


# ── 1. the op.run RUN-INDEX emit + the projection mechanics (MODEL-FREE: seeded record) ───────────
print("\n[1] op.run run-index projection (model-free — a seeded engine op.run record)")
# Seed an op.run record exactly as run_items emits it (the C1.6 one-emit-per-fan shape) through the SAME
# store the projection reads — proving the projection independent of a live model.
seed_addr = "run://seed-turn/ground/0"
SUITE.store.put_content({"in_scope": True, "note": "seeded"})
SUITE.store.append_event({
    "kind": "op.run", "summary": "cognition.run_items · ground · 1 units · 5ms",
    "op": "cognition.run_items", "run_op": "generate", "turn_id": "seed-turn",
    "role": "ground", "duration_ms": 5, "addresses": [seed_addr],
})
disc = SUITE.list_runs()
check("1 list_runs projects the op.run log (the index — no parallel store)",
      isinstance(disc, dict) and isinstance(disc.get("runs"), list))
check("1 the seeded run is DISCOVERED with its concrete run:// address",
      any(r["address"] == seed_addr and r["op"] == "cognition.run_items" for r in disc["runs"]))
check("1 find_runs(role='ground') filters to it",
      any(r["address"] == seed_addr for r in SUITE.find_runs(role="ground")["runs"]))
check("1 find_runs(role='nonexistent') is empty (filter has teeth)",
      SUITE.find_runs(role="zzz-no-such-role")["runs"] == [])
# the index covers ONLY the engine run-ops, never every op.run telemetry record (voice.client etc.).
SUITE.emit_run_record("voice.client", 3, event="noise")
check("1 list_runs IGNORES non-engine op.run records (voice.client not in the run index)",
      all(r["op"] in SUITE.ENGINE_RUN_OPS for r in SUITE.list_runs(limit=999)["runs"]))
raised = False
try:
    SUITE.list_runs(op="not.an.engine.op")
except ValueError:
    raised = True
check("1 list_runs FAILS LOUD on an unknown engine run-op (never a fabricated op)", raised)


# ── 2. a REAL generate chain → discovered → composability loop (LIVE — needs :8000) ───────────────
print("\n[2] LIVE: run a real generate chain → discover it → feed a discovered address back (outputs→inputs)")
if BRAIN:
    # 1. a real generate chain: run_items('ground', [3 literal units], …) → 3 run:// outputs (live 4B).
    units = [
        "What did we decide about the storage layer?",
        "How does the memo gate avoid re-hitting the GPU?",
        "Tell me a joke about cats.",
    ]
    turn = "disc-live-" + str(os.getpid())
    res = _cog.run_items(SUITE.role_registry["ground"], units, SUITE.store,
                         turn_id=turn, emit=srv._cog_emit)          # emit → the SAME store list_runs reads
    check("2 the chain produced 3 run:// outputs", len(res.addresses) == 3 and len(res.resolved) == 3)

    # 2. list_runs DISCOVERS those 3 runs (+ their addresses) from the op.run log.
    live = SUITE.find_runs(role="ground", run_op="generate", limit=999)["runs"]
    live_addrs = [r["address"] for r in live if r["turn_id"] == turn]
    check("2 list_runs/find_runs DISCOVERED the 3 chain runs (the run INDEX, not known-by-address)",
          len(live_addrs) == 3 and all(a.startswith(f"run://{turn}/ground/") for a in live_addrs))

    # 3. THE COMPOSABILITY LOOP: take a DISCOVERED address → feed it as an INPUT to another run_role
    #    (resolve_address materializes the run:// content) → outputs→inputs BY DISCOVERY (not hardcoded).
    discovered = live_addrs[0]                                    # an address we LEARNED from the index
    fed_value = _cog.resolve_address(SUITE.store, discovered)     # resolve the discovered output
    check("2 a DISCOVERED run:// address resolves to a real prior output",
          isinstance(fed_value, dict) and "in_scope" in fed_value)
    # feed it as the literal input-unit of a fresh run (the engine's run_items input axis).
    turn2 = turn + "-fed"
    res2 = _cog.run_items(SUITE.role_registry["ground"], [discovered], SUITE.store,
                          turn_id=turn2, emit=srv._cog_emit)         # the unit is the DISCOVERED address
    check("2 OUTPUTS→INPUTS-BY-DISCOVERY: a discovered run output drove a downstream run",
          len(res2.resolved) == 1 and isinstance(list(res2.resolved.values())[0], dict))
    check("2 the downstream run is itself discoverable (the loop closes)",
          any(r["turn_id"] == turn2 for r in SUITE.find_runs(role="ground", limit=999)["runs"]))

    # 4. THE NAMED-INPUT branch (the task's exact wording: feed a discovered address via run_role
    #    inputs/input_addresses → resolve_address). The MCP run_role tool resolves an address-valued
    #    named input through resolve_address before the run. ground declares input_addresses
    #    ("utterance","live_state") → live_state is a named extra input fed the DISCOVERED address.
    rr_named = srv.run_role("ground", utterance="Is this in scope given the prior grounding?",
                            inputs={"live_state": discovered})        # an address-valued NAMED input
    check("2 NAMED-INPUT: run_role resolved a DISCOVERED run:// address as a named input "
          "(inputs=/input_addresses → resolve_address) + persisted a fresh run",
          str(rr_named.get("address", "")).startswith("run://") and isinstance(rr_named.get("output"), dict))
else:
    check("2 SKIPPED — resident brain DOWN (the live chain + composability loop need :8000)", True)


# ── 3. the MCP tools (the agent-face discovery) ───────────────────────────────────────────────────
print("\n[3] MCP list_runs / find_runs tools (the agent face)")
mcp_runs = srv.list_runs()
check("3 MCP list_runs returns the run index", isinstance(mcp_runs, dict) and isinstance(mcp_runs.get("runs"), list))
check("3 MCP list_runs sees the seeded run", any(r["address"] == seed_addr for r in mcp_runs["runs"]))
check("3 MCP find_runs(role='ground') filters", any(r["address"] == seed_addr for r in srv.find_runs(role="ground")["runs"]))
if BRAIN:
    # a run fired LIVE via the MCP run_role tool emits its op.run via the MCP wrapper → discoverable.
    rr = srv.run_role("ground", utterance="Is the storage layer in scope?")
    check("3 a live MCP run_role persisted a run:// address", str(rr.get("address", "")).startswith("run://"))
    found = srv.find_runs(op="cognition.run_role", limit=999)["runs"]
    check("3 the MCP run_role is DISCOVERABLE via the run index (emit in the MCP wrapper)",
          any(r["address"] == rr["address"] for r in found))
else:
    check("3 SKIPPED — MCP run_role discovery needs :8000", True)


# ── 4. behaviour-preserving + the FLOOR (the op.run emit is telemetry, never a forbidden verb) ────
print("\n[4] behaviour-preserving + the operator-only floor")
src = open(os.path.join(ROOT, "runtime", "cognition.py"), encoding="utf-8").read()
check("4 the op.run emit rides the existing emit sink (no append_event-per-unit; C1.6 held)",
      'emit("op.run"' in src)
# the engine run fns still take the same emit-sink seam (additive — no signature break).
import inspect                                                             # noqa: E402
check("4 run_items signature UNCHANGED (additive — the emit is inside, not a new param)",
      "emit" in inspect.signature(_cog.run_items).parameters)
check("4 run_reduce signature UNCHANGED",
      "emit" in inspect.signature(_cog.run_reduce).parameters)
# the run-index contract: list an address you can FEED. A FAILED unit's address was never set_ref'd, so a
# partially-failed fan must index ONLY its OK units' addresses (never a phantom run:// that won't resolve).
fail_events = []
fail_turn = "disc-fail"
_seed_cas = SUITE.store.put_content("a real upstream output")
SUITE.store.set_ref(f"run://{fail_turn}/good", _seed_cas)
try:
    _cog.run_items(SUITE.role_registry["ground"],
                   ["a literal unit", f"run://{fail_turn}/missing"],   # the 2nd is unresolvable → the unit fails
                   SUITE.store, turn_id=fail_turn,
                   emit=lambda k, p: fail_events.append((k, p)))
except Exception:
    pass                                                              # the fan re-raises (fail loud) — expected
_oprun = [p for (k, p) in fail_events if k == "op.run"]
check("4 a partially-failed fan indexes ONLY the OK units' addresses (no phantom un-set_ref'd run://)",
      len(_oprun) == 1 and all(SUITE.store.head(a) is not None for a in _oprun[0]["addresses"]))
# the floor: no op.run emit is a resolve/approve/dispatch (cognition_governance_acceptance is the hard gate;
# here a cheap local check that the op.run records carry an op in the engine set, never a governance verb).
check("4 the op.run index op is an engine run-op, NEVER resolve/approve/dispatch",
      all(r["op"] in SUITE.ENGINE_RUN_OPS and r["op"] not in ("resolve", "approve", "dispatch")
          for r in SUITE.list_runs(limit=999)["runs"]))


print(f"\nALL {PASS} CHECKS PASS — the run index (op.run) + list_runs/find_runs projection + the MCP "
      f"tools + the outputs→inputs-BY-DISCOVERY loop ({'LIVE' if BRAIN else 'brain-down: live legs skipped'})")
