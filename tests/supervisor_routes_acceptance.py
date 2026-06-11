"""tests/supervisor_routes_acceptance.py — the contract corpus's MACHINE INVENTORY teeth (F1.5).

CONTRACT-FORMAT.md imposes code-side obligations so the corpus's reality checks (V21/V22) have
real registries to read (§9 — adopted into the contract lane's scope, scaffolding-not-spec law):

  §9.3  the supervisor ships SUPERVISOR_ROUTES before any supervisor binding is contracted —
        a (method, path) STRUCTURED registry (the §9.1 bridge shape from birth). This test is
        the bidirectional drift teeth (the bridge_routes_acceptance pattern): a path dispatched
        in do_GET/do_POST but absent from the registry fails loud, and a registry row that
        nothing dispatches fails loud (a phantom binding advertised to the contract).
  §9.2  every consolidated MCP tool module exports a closed OPS constant —
        mcp_face/tools/sessions.py exports OPS, and the tool's own dispatch handles exactly
        that set (no phantom op, no undispatched op).

Run: ./.venv/bin/python tests/supervisor_routes_acceptance.py    (exit 0 = pass)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

PASS = 0
FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}  {detail}")


# ── §9.3 — SUPERVISOR_ROUTES ↔ the dispatch literals, both directions ─────────────────────────
from runtime import session_supervisor as sup

declared = set(sup.SUPERVISOR_ROUTES)
src = open(os.path.join(ROOT, "runtime", "session_supervisor.py"), encoding="utf-8").read()

check("SUPERVISOR_ROUTES is a non-empty tuple of (method, path) pairs",
      isinstance(sup.SUPERVISOR_ROUTES, tuple) and len(declared) > 0
      and all(isinstance(r, tuple) and len(r) == 2 and r[0] in ("GET", "POST")
              and r[1].startswith("/") for r in declared))
check("SUPERVISOR_ROUTES has no duplicates", len(declared) == len(sup.SUPERVISOR_ROUTES))

get_body = src[src.index("def do_GET"):src.index("def _watch")]
post_body = src[src.index("def do_POST"):src.index("def main")]
dispatched = set()
for m in re.finditer(r'u\.path\s*==\s*"(/[^"]*)"', get_body):
    dispatched.add(("GET", m.group(1)))
for m in re.finditer(r'u\.path\s*==\s*"(/[^"]*)"', post_body):
    dispatched.add(("POST", m.group(1)))
for m in re.finditer(r'u\.path\s+in\s+\(([^)]*)\)', post_body):
    for p in re.findall(r'"(/[^"]*)"', m.group(1)):
        dispatched.add(("POST", p))

check("every dispatched route is DECLARED in SUPERVISOR_ROUTES (nothing invisible to the contract)",
      dispatched <= declared, f"undeclared: {sorted(dispatched - declared)}")
check("every declared route is DISPATCHED (no phantom binding advertised)",
      declared <= dispatched, f"phantom: {sorted(declared - dispatched)}")

# ── §9.2 — the consolidated tool's exported closed OPS set ────────────────────────────────────
sys.path.insert(0, os.path.join(ROOT, "mcp_face"))
import importlib
sessions_mod = importlib.import_module("mcp_face.tools.sessions")

ops = getattr(sessions_mod, "OPS", None)
check("mcp_face/tools/sessions.py EXPORTS a closed OPS constant (§9.2 — extract_reality's read)",
      isinstance(ops, tuple) and len(ops) > 0 and all(isinstance(o, str) for o in ops))
check("OPS has no duplicates", ops is not None and len(set(ops)) == len(ops))

tool_src = open(os.path.join(ROOT, "mcp_face", "tools", "sessions.py"), encoding="utf-8").read()
handled = set(re.findall(r'if op == "([a-z]+)"', tool_src))
check("every exported op is dispatched in the tool body (no phantom op)",
      ops is not None and set(ops) == handled,
      f"OPS={sorted(ops or [])} vs dispatched={sorted(handled)}")
literal = re.search(r'op:\s*Literal\[([^\]]*)\]', tool_src)
sig_ops = set(re.findall(r'"([a-z]+)"', literal.group(1))) if literal else set()
check("the tool signature's Literal[...] equals OPS (one vocabulary, no drift)",
      ops is not None and sig_ops == set(ops),
      f"signature={sorted(sig_ops)} vs OPS={sorted(ops or [])}")

print(f"\n{'PASS' if FAIL == 0 else 'FAIL'} — {PASS} ok, {FAIL} failed")
sys.exit(0 if FAIL == 0 else 1)
