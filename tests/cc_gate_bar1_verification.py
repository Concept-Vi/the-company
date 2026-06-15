"""tests/cc_gate_bar1_verification.py — R15 BAR 1, on REAL data: a gate's OPAQUE step_address RESOLVES
through the H1.1 resolver (the lead's session://<sid>/step/<tool_use_id>, 1cf5642) and the SAME address
comes back (round-trip). Proves the gate is addressed into the unified grammar, not a side-id.

Real-data: finds a real agent-session with a tool_use step in its transcript. If none is present it
SKIPS honestly (never green-paints). Run: python3 tests/cc_gate_bar1_verification.py
"""
import glob
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.cognition import resolve_address
from runtime.session_pointintime import _iter_jsonl
from runtime import cc_gate as cg

PASS, FAIL = [], []


def ok(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'ok ' if cond else 'FAIL'} {name}" + (f"  — {detail}" if detail and not cond else ""))


store = FsStore(os.path.join(REPO := ROOT, ".data", "store"))

# find a real agent-session whose transcript has a tool_use step
real_sid = real_step = None
for p in sorted(glob.glob(os.path.join(ROOT, ".data", "store", "agent_sessions", "*")))[:80]:
    sid = os.path.basename(p)
    sid = sid[:-5] if sid.endswith(".json") else sid
    try:
        rec = store.load_agent_session(sid)
    except Exception:
        continue
    if not rec:
        continue
    jsonl = rec.get("jsonl_path")
    if not jsonl or not os.path.exists(jsonl):
        continue
    for _, ev in _iter_jsonl(jsonl):
        if isinstance(ev, dict) and ev.get("type") == "assistant":
            for block in ((ev.get("message") or {}).get("content") or []):
                if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("id"):
                    real_sid, real_step = sid, block["id"]
                    break
        if real_step:
            break
    if real_step:
        break

if not real_step:
    print("  -- SKIPPED: no real agent-session with a tool_use step found (bar-1 needs live data) --")
    print("\nRESULT: skipped (no fixture) — not a failure, not green-paint")
    sys.exit(0)

STEP_ADDR = f"session://{real_sid}/step/{real_step}"
print(f"  (real step address: {STEP_ADDR})")

# 1. gate the REAL step address (my gate stores it opaque, format-validated)
g = cg.gate(STEP_ADDR, real_sid, note="bar-1 real-data verification", gates_dir=os.path.join("/tmp", "g_bar1"))
ok("gate accepts + stores the real step address opaque", g["step_address"] == STEP_ADDR and g["state"] == "gated")

# 2. ★ BAR 1: the gate's opaque step_address RESOLVES through the H1.1 resolver → the real step record
resolved = resolve_address(store, g["step_address"])
ok("BAR 1: gate's opaque step_address RESOLVES through resolve_address (H1.1) to the real step",
   isinstance(resolved, dict) and resolved.get("step") == real_step and resolved.get("session") == real_sid)

# 3. ROUND-TRIP: the SAME address comes back from the resolver (addressed into the grammar, not a side-id)
ok("BAR 1 round-trip: the resolved record carries back the SAME address",
   resolved.get("address") == g["step_address"] == STEP_ADDR)

# 4. fail-loud: a gate on a bogus step id RESOLVES to a loud raise (never silent / guessed-nearest)
bogus = cg.gate(f"session://{real_sid}/step/toolu_BOGUS_does_not_exist", real_sid,
                gates_dir=os.path.join("/tmp", "g_bar1"))
try:
    resolve_address(store, bogus["step_address"])
    ok("BAR 1 fail-loud: an unknown step address RAISES through the resolver", False)
except ValueError as e:
    ok("BAR 1 fail-loud: an unknown step address RAISES through the resolver", "unknown step" in str(e))

import shutil
shutil.rmtree(os.path.join("/tmp", "g_bar1"), ignore_errors=True)

print(f"\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", ", ".join(FAIL))
    sys.exit(1)
print("ALL GREEN — BAR 1 met on REAL data: the gate's opaque step_address resolves through the ONE "
      "resolver to the real tool-call step + the same address round-trips. The gate is addressed into the "
      "unified grammar (session://<sid>/step/<tool_use_id>), not a side-id. Both halves meet at the contract.")
