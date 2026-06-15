"""tests/cc_gate_acceptance.py — Heart R15 gate: per-step gate/abort/rewind (observer on native mechanism).
Supervisor + materialize are MOCKED (no live claude). Covers the bars: opaque step-address fail-loud
(bar 3), the gate->resume / gate->abort(interrupt+teardown no-orphan) / gate->rewind(materialize native)
lifecycle (bar 2/4), state fail-loud, opaque-target-never-parsed. Run: python3 tests/cc_gate_acceptance.py
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from runtime import cc_gate as cg

PASS, FAIL = [], []


def ok(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'ok ' if cond else 'FAIL'} {name}" + (f"  — {detail}" if detail and not cond else ""))


tmp = tempfile.mkdtemp(prefix="cc_gate_test_")
GD = os.path.join(tmp, "gates")
STEP = "session://as-7f3a/step/toolu_01abcDEF"      # the opaque step-address (the board:// pattern)

# ── spy the supervisor: record /interrupt + /teardown calls (the no-orphan abort path) ──
sup_calls = []
def _spy_sup(path, body=None, method="POST", timeout=30):
    sup_calls.append((path, body))
    return 200, {"ok": True}
cg._sup = _spy_sup

# 1. gate registers + stores the address OPAQUE + session as a separate field
g = cg.gate(STEP, "as-7f3a", note="gate the risky tool step", gates_dir=GD)
ok("gate registers state=gated with opaque step_address + separate session",
   g["state"] == "gated" and g["step_address"] == STEP and g["session"] == "as-7f3a"
   and g["id"].startswith("gate-"))
ok("gate stores the step_address VERBATIM (opaque — never parsed)", g["step_address"] == STEP)

# 2. bar 3 — fail-loud on a malformed step address (never silent / guessed-nearest)
for bad in ("not-an-address", "session://as-7f3a", "board://item-x", "session:///step/x"):
    try:
        cg.gate(bad, "as-7f3a", gates_dir=GD)
        ok(f"gate fails loud on malformed address {bad!r}", False)
        break
    except cg.GateError:
        pass
else:
    ok("gate fails loud on every malformed step address", True)
# gate needs a session (the abort/rewind handle) — fail loud without it
try:
    cg.gate(STEP, "", gates_dir=GD)
    ok("gate fails loud without a session", False)
except cg.GateError:
    ok("gate fails loud without a session", True)

# 3. RESUME lifecycle (gate->resumed); recorded, not enforced
gr = cg.gate("session://as-r/step/tu_r", "as-r", gates_dir=GD)
res = cg.resume(gr["id"], by="tim", gates_dir=GD)
ok("resume moves gated->resumed + records the decision",
   res["state"] == "resumed" and res["control"] == "resume" and res["by"] == "tim"
   and res["history"][-1]["to"] == "resumed")
# can't resume a non-gated gate
try:
    cg.resume(gr["id"], gates_dir=GD)
    ok("resume fails loud on an already-resumed gate", False)
except cg.GateError:
    ok("resume fails loud on an already-resumed gate", True)

# 4. ABORT lifecycle (bar 4 abort = interrupt + teardown, no-orphan)
sup_calls.clear()
ga = cg.gate("session://as-a/step/tu_a", "as-a", gates_dir=GD)
ab = cg.abort(ga["id"], by="tim", gates_dir=GD)
ok("abort moves gated->aborted", ab["state"] == "aborted" and ab["control"] == "abort")
ok("abort calls /interrupt THEN /teardown on the session (no-orphan law)",
   [c[0] for c in sup_calls] == ["/interrupt", "/teardown"]
   and all(c[1].get("session") == "as-a" for c in sup_calls))

# 5. REWIND = native materialize_at_point (bar 2, surface-don't-rebuild) — mock materialize, assert it's called
mat_calls = []
import runtime.session_pointintime as spt
_orig_mat = spt.materialize_at_point
spt.materialize_at_point = lambda jsonl, at, **k: (mat_calls.append((jsonl, at, k)) or
                                                   {"new_sid": "newsid-123", "source_untouched": True,
                                                    "new_path": os.path.join(tmp, "newsid-123.jsonl")})
src = os.path.join(tmp, "src.jsonl"); open(src, "w").write("{}\n")
gw = cg.gate("session://as-w/step/tu_w", "as-w", gates_dir=GD)
rw = cg.rewind(gw["id"], src, "compact:1", by="tim", gates_dir=GD)
ok("rewind invokes the NATIVE materialize_at_point (not a reimplemented restore)",
   len(mat_calls) == 1 and mat_calls[0][1] == "compact:1")
ok("rewind moves gated->rewound + records the new materialized sid",
   rw["state"] == "rewound" and rw["rewound_to"] == "newsid-123")
spt.materialize_at_point = _orig_mat

# 6. _find by id OR by step_address; fail-loud on unknown
ok("get_gate resolves by step_address (not just id)",
   cg.get_gate(STEP, gates_dir=GD)["id"] == g["id"])
try:
    cg.abort("gate-nope", gates_dir=GD)
    ok("ops fail loud on an unknown gate", False)
except cg.GateError:
    ok("ops fail loud on an unknown gate", True)

# 7. list filters
ok("list_gates filters by state",
   all(r["state"] == "aborted" for r in cg.list_gates(state="aborted", gates_dir=GD))
   and len(cg.list_gates(state="aborted", gates_dir=GD)) == 1)

import shutil
shutil.rmtree(tmp, ignore_errors=True)

print(f"\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", ", ".join(FAIL))
    sys.exit(1)
print("ALL GREEN — R15 gate/abort/rewind: opaque step-address fail-loud, gate->resume/abort(interrupt+"
      "teardown no-orphan)/rewind(native materialize) lifecycle, fail-loud throughout. "
      "Observer on the native mechanism — no hot-path edit, no parallel render. "
      "(Full LIVE round-trip on a real gated process is the documented live-pending bar.)")
