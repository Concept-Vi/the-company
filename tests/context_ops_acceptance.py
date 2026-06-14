"""tests/context_ops_acceptance.py — S-R10.1 context ops + tool acceptance (no real claude here;
the live /context + /compact mechanics are lead-verified: ops/fabric_live_probe_r1.py leg 2 for
/context, and the 2026-06-14 compact probe showed /compact → system/compact_boundary + memory
survives). This suite covers the tool's register contract + op dispatch + fail-loud paths."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

PASS, FAIL = [], []
def check(n, c, d=""):
    (PASS if c else FAIL).append(n); print(f"  {'PASS' if c else 'FAIL'}  {n}" + (f"  — {d}" if d and not c else ""))
def raises(fn, sub=""):
    try: fn(); return False
    except Exception as e: return sub in str(e) if sub else True

# the context_ops module exports the two ops + the teaching error
import runtime.context_ops as C
check("1 context_ops exports read_context + compact_session + ContextOpError",
      hasattr(C, "read_context") and hasattr(C, "compact_session") and hasattr(C, "ContextOpError"))
check("2 unreachable supervisor fails loud (ContextOpError, never silent)",
      raises(lambda: C.read_context("x", base="http://127.0.0.1:1"), "unreachable"))

# the tool register + ops
import mcp_face.tools.context as CT
captured = {}
class MockMCP:
    def tool(self):
        def deco(fn): captured["context"] = fn; return fn
        return deco
CT.register(MockMCP(), suite=None)
tool = captured.get("context")
check("3 the context tool registered via the file-drop register() contract", tool is not None)
check("4 op without session fails loud", raises(lambda: tool(op="read"), "requires `session`"))
check("5 OPS export matches the dispatcher", CT.OPS == ("read", "compact"))
# unreachable-supervisor path returns a structured error (not a raise) through the tool
res = tool(op="read", session="nope")
check("6 a failed op surfaces a structured error (no silent failure)",
      res.get("ok") is False and "error" in res, d=str(res))

print(f"\n{'='*56}\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL: print("FAILED:", ", ".join(FAIL)); sys.exit(1)
print("ALL GREEN — S-R10.1 context ops + tool (live /context + /compact lead-verified by use).")
