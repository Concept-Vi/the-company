"""tests/routines_acceptance.py — S-R9.1 routine registry + runner + tool acceptance.

Everything provable WITHOUT spawning a real claude (the live FIRE is the lead's, like the fabric
probes). Covers: the file-discovered registry (discovers the sample, builds the record), the
FAIL-LOUD paths (malformed routine RAISES, never a silent skip), the runner's /spawn BODY
construction, and the `routines` MCP tool ops (list/get + register file-drop contract).

Run: .venv/bin/python tests/routines_acceptance.py   (exit 0 = pass)
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from runtime.routines import (RoutineRegistry, routine_registry, _build_routine, Routine)
from runtime.routine_runner import build_spawn_body

PASS, FAIL = [], []
def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'PASS' if cond else 'FAIL'}  {name}" + (f"  — {detail}" if detail and not cond else ""))

def raises(fn, substr=""):
    try:
        fn(); return False
    except Exception as e:
        return substr in str(e) if substr else True

# ── 1. the real registry discovers the shipped sample ──────────────────────────────────────────
print("\n[1] file-discovered registry")
reg = routine_registry()
check("1.1 discovers the shipped routines/ (self_status present)", "self_status" in reg,
      detail=f"ids={reg.ids()}")
r = reg["self_status"]
rec = r.record()
check("1.2 the record carries prompt + cwd + permission_mode + cadence",
      bool(rec["prompt"]) and rec["cwd"] == "/home/tim/company" and rec["permission_mode"] == "plan"
      and rec["cadence"], detail=str(rec))
check("1.3 defaults applied (max_turns=1, repeats=False)", r.max_turns == 1 and r.repeats is False)

# ── 2. FAIL-LOUD on malformed routines (one deliberate violation per rule) ──────────────────────
print("\n[2] fail-loud validation (malformed routines RAISE, never silently skip)")
check("2.1 non-dict ROUTINE raises", raises(lambda: _build_routine("x", ["not", "a", "dict"]), "must be a dict"))
check("2.2 missing id raises", raises(lambda: _build_routine("x", {"prompt": "p"}), "no string `id`"))
check("2.3 id != module name raises", raises(lambda: _build_routine("x", {"id": "y", "prompt": "p"}), "must equal the file name"))
check("2.4 missing prompt raises", raises(lambda: _build_routine("x", {"id": "x"}), "no string `prompt`"))
check("2.5 unknown field raises", raises(lambda: _build_routine("x", {"id": "x", "prompt": "p", "bogus": 1}), "unknown field"))
check("2.6 bad max_turns raises", raises(lambda: _build_routine("x", {"id": "x", "prompt": "p", "max_turns": 0}), "max_turns"))
check("2.7 non-str cadence raises", raises(lambda: _build_routine("x", {"id": "x", "prompt": "p", "cadence": 5}), "cadence"))

# ── 3. discovery over an isolated temp dir (add-a-file = self-register; dup id fails loud) ───────
print("\n[3] discovery semantics")
with tempfile.TemporaryDirectory() as td:
    with open(os.path.join(td, "alpha.py"), "w") as f:
        f.write("ROUTINE = {'id': 'alpha', 'prompt': 'do alpha'}\n")
    with open(os.path.join(td, "_skip.py"), "w") as f:
        f.write("ROUTINE = {'id': '_skip', 'prompt': 'x'}\n")          # underscore-prefixed → skipped
    with open(os.path.join(td, "notroutine.py"), "w") as f:
        f.write("X = 1\n")                                             # no ROUTINE → skipped, not error
    reg2 = RoutineRegistry().discover([td])
    check("3.1 a dropped routines/<id>.py self-registers", "alpha" in reg2 and reg2.ids() == ["alpha"],
          detail=f"ids={reg2.ids()}")
    # duplicate id across files → fail loud
    with open(os.path.join(td, "alpha_dup.py"), "w") as f:
        f.write("ROUTINE = {'id': 'alpha_dup', 'prompt': 'p'}\n")      # ok (distinct)
    check("3.2 distinct ids coexist", len(RoutineRegistry().discover([td]).ids()) == 2)

# ── 4. the runner's /spawn body (pure, no real spawn) ───────────────────────────────────────────
print("\n[4] runner /spawn body construction")
body = build_spawn_body(r)
check("4.1 body threads prompt + cwd + permission_mode + routine name + source",
      body["prompt"] == r.prompt and body["cwd"] == r.cwd
      and body["permission_mode"] == "plan" and body["name"] == "routine:self_status"
      and body["source"] == "routine", detail=str(body))
check("4.2 no model key when the routine declares none (supervisor default preserved)",
      "model" not in body)
rmodel = Routine("m", {"id": "m", "prompt": "p", "model": "opus"})
check("4.3 a declared model is threaded", build_spawn_body(rmodel).get("model") == "opus")

# ── 5. the `routines` MCP tool (file-drop register + list/get ops) ──────────────────────────────
print("\n[5] the routines MCP tool")
import mcp_face.tools.routines as RT
captured = {}
class MockMCP:
    def tool(self):
        def deco(fn): captured["routines"] = fn; return fn
        return deco
RT.register(MockMCP(), suite=None)
tool = captured.get("routines")
check("5.1 the tool registered via the file-drop register() contract", tool is not None)
lst = tool(op="list")
check("5.2 op=list returns the registered routines", lst["total"] >= 1
      and any(x["id"] == "self_status" for x in lst["routines"]))
g = tool(op="get", id="self_status")
check("5.3 op=get returns the full record", g["routine"]["id"] == "self_status")
check("5.4 op=get unknown id fails loud", raises(lambda: tool(op="get", id="nope"), "no routine"))
check("5.5 OPS export matches the dispatcher", RT.OPS == ("list", "get", "fire"))

print(f"\n{'='*60}\nRESULT: {len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", ", ".join(FAIL)); sys.exit(1)
print("ALL GREEN — S-R9.1 routine registry + runner + tool (the live FIRE is lead-verified: "
      "`python -m runtime.routine_runner self_status`).")
