"""tests/gate_composition_step_acceptance.py — R13 bar 4: R15 gate/rewind fires on a COMPOSITION-STEP.

A composition-step is a run_composition leg's run:// address (run://<turn>/<member>[/<index>]) — NOT a
native session tool-step. Bar 4: the gate accepts + acts on it, AND run_composition ENFORCES it (halts
before a gated leg — the harness payoff: our driver, not claude's native loop, so a pre-leg pause is real).

Falsify-first floor:
  • is_composition_step_address is False for a session-step + a malformed run:// (the negative).
  • cc_gate.gate() STILL fails loud on a malformed step address (fail-loud preserved).
  • WITHOUT a gate, run_composition runs BOTH legs (the d6b693f baseline) — so a HALT is a real change.
Then: gate a composition-step → run_composition halts before that leg (gated_at set, the leg's output absent).

  ~/vllm-env/bin/python tests/gate_composition_step_acceptance.py   (uses the resident chat-4b for the judge-leg case)
"""
import os, sys, tempfile
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

from contracts.address import (is_step_address, is_composition_step_address,
                               parse_composition_step_address)
from runtime import cc_gate
from runtime import minds
from runtime.cognition import resolve_address, SlotBudget
from store.fs_store import FsStore

PASS, FAIL = [], []
def check(n, c, d=""):
    (PASS if c else FAIL).append(n)
    print(f"  {'ok ' if c else 'FAIL'} {n}" + (f"  — {d}" if d and not c else ""))
def raises(fn, exc=Exception):
    try: fn(); return False
    except exc: return True
    except Exception: return False

store = FsStore(os.path.join(REPO, ".data", "store"))
gates_dir = tempfile.mkdtemp(prefix="gate-comp-")

# ── 1. GRAMMAR (no model) — composition-step shapes recognized; negatives rejected ──
check("1 is_composition_step_address(run://t1/mine_exchange) [source leg]",
      is_composition_step_address("run://t1/mine_exchange"))
check("2 is_composition_step_address(run://t1/judge_mining/0) [downstream leg]",
      is_composition_step_address("run://t1/judge_mining/0"))
check("3 parse → {turn,member,index}", parse_composition_step_address("run://t1/judge_mining/0")
      == {"turn": "t1", "member": "judge_mining", "index": 0})
check("4 FALSIFY: a session-step is NOT a composition-step",
      not is_composition_step_address("session://sid-1/step/tuid-9"))
check("5 FALSIFY: a bare run://t1 (1 segment) is malformed → not a composition-step",
      not is_composition_step_address("run://t1"))
check("6 session-step grammar still works (is_step_address unbroken)",
      is_step_address("session://sid-1/step/tuid-9") and not is_step_address("run://t1/x"))

# ── 2. cc_gate ACCEPTS a composition-step (was rejected pre-bar-4); fail-loud preserved ──
comp_addr = "run://t1/judge_mining/0"
g = cc_gate.gate(comp_addr, session="sid-parent-1", note="gate the judge leg", gates_dir=gates_dir)
check("7 ★ cc_gate.gate(composition-step) SUCCEEDS (was rejected before bar 4)",
      g.get("state") == "gated" and g.get("step_address") == comp_addr)
check("8 fail-loud preserved: a MALFORMED step address still raises GateError",
      raises(lambda: cc_gate.gate("run://", session="s", gates_dir=gates_dir), cc_gate.GateError))
r = cc_gate.resume(g["id"], by="lead", note="ungate", gates_dir=gates_dir)
check("9 lifecycle: gate→resume on a composition-step (gated→resumed)", r.get("state") == "resumed")

# ── 3. ENFORCEMENT (the harness payoff) — run_composition HALTS before a gated leg ──
# gate-backed closure: a step is gated iff a 'gated' gate record targets it (cc_gate, temp dir)
def gate_check(addr):
    return any(rec.get("state") == "gated" for rec in cc_gate.list_gates(gates_dir=gates_dir)
              if rec.get("step_address") == addr)

pair = resolve_address(store, "mind://pair")
ctx = {"utterance": "Tim: capped model_max_length to 8192. Assistant: embed now peaks 9.4G, not 15.5G."}
budget = SlotBudget.from_registry()

# 3a — gate the SOURCE leg (extractor) → halt BEFORE any model call (deterministic, no chat-4b)
turn_a = "gate-comp-src"
cc_gate.gate(f"run://{turn_a}/mine_exchange", session="sid-a", note="gate source", gates_dir=gates_dir)
res_a = minds.run_composition(pair, ctx, store, turn_id=turn_a, budget=budget, gate_check=gate_check)
check("10 ★ ENFORCE: gate on the SOURCE leg halts run_composition before it runs (no model call)",
      res_a.get("gated_at") == "extractor" and res_a.get("outputs") == {} and res_a.get("final") is None,
      f"got gated_at={res_a.get('gated_at')} outputs_keys={list(res_a.get('outputs',{}))}")

# 3b — gate the JUDGE leg → extractor RUNS (1 chat-4b call), halt before judge
turn_b = "gate-comp-judge"
cc_gate.gate(f"run://{turn_b}/judge_mining/0", session="sid-b", note="gate judge", gates_dir=gates_dir)
res_b = minds.run_composition(pair, ctx, store, turn_id=turn_b, budget=budget, gate_check=gate_check)
check("11 ★ ENFORCE: gate on the JUDGE leg → extractor RAN, judge did NOT (selective leg gating)",
      res_b.get("gated_at") == "judge" and "extractor" in res_b.get("outputs", {})
      and "judge" not in res_b.get("outputs", {}),
      f"got gated_at={res_b.get('gated_at')} outputs_keys={list(res_b.get('outputs',{}))}")

# 3c — CONTROL (falsify-first baseline): NO gate → BOTH legs run (the d6b693f path)
turn_c = "gate-comp-none"
res_c = minds.run_composition(pair, ctx, store, turn_id=turn_c, budget=budget, gate_check=gate_check)
check("12 ★ CONTROL: ungated → BOTH legs run (extractor+judge), final present (halt is a real change)",
      "extractor" in res_c.get("outputs", {}) and "judge" in res_c.get("outputs", {})
      and res_c.get("gated_at") is None and res_c.get("final") is not None,
      f"got gated_at={res_c.get('gated_at')} outputs_keys={list(res_c.get('outputs',{}))}")

print(f"\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", FAIL); sys.exit(1)
print("ALL GREEN — R13 bar 4: a composition-step (run://<turn>/<member>) is gate-addressable on the shared\n"
      "grammar; cc_gate accepts + runs the lifecycle on it (fail-loud preserved); and run_composition\n"
      "ENFORCES the gate — halts before a gated leg (source→no model call; judge→extractor ran, judge didn't).\n"
      "The R15 gate fires on a composition leg, not only a native tool-step. The harness payoff is real.")
