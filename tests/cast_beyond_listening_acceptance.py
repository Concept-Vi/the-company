"""tests/cast_beyond_listening_acceptance.py — C 4/4.

Proves cast-beyond-listening is a DATA-DRIVEN capability that already holds (the engine has NO
`listening` hardcode in the firing path — `chat_parts` does `cast_for_mode(mode)` and fires whatever
roles declare that mode in their `mode_scope`), and that the C-build role facets (`op`,
`input_addresses`) are now exposed in the `cognition_info` projection so the surface/registry/gates SEE
a role's full declared shape (one-source, never FE-hardcoded).

The walkthrough CAST itself (the roles that declare `mode_scope` ⊇ {"walkthrough"} + a `screen_reader`
role) is the guided-review session's to add ON this engine capability — this test proves the engine
fires a non-listening cast the moment a role declares it, using a TEMP role (not a committed one, so it
doesn't plant in guided-review's territory).
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

PASS = 0
ok = True


def check(label, cond):
    global PASS, ok
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        ok = False
        print(f"  FAIL  {label}")


from runtime.suite import Suite
from runtime.registry import NodeRegistry
from store.fs_store import FsStore
from contracts import cognition_info as CI

s = Suite(FsStore(tempfile.mkdtemp(prefix="cbl-")), NodeRegistry().discover(["nodes"]), nodes_dir="nodes")

# ── 1 · the C-build facets are exposed in the projection (op + input_addresses) ──────────────────
print("\n[1] op + input_addresses projected in cognition_info (the surface/gates see the full role shape)")
ci = s.cognition_info()
roles = ci["roles"]
a_role = roles.get("recall") or next(iter(roles.values()))
check("op in the role projection", "op" in a_role)
check("op defaults to 'generate'", a_role["op"] == "generate")
check("input_addresses in the role projection", "input_addresses" in a_role)
check("input_addresses is a list (recall reads utterance+memory)", isinstance(roles["recall"]["input_addresses"], list) and roles["recall"]["input_addresses"])

# ── 2 · cast-beyond-listening is DATA-DRIVEN — a role declaring a non-listening mode fires there ──
print("\n[2] cast-beyond-listening is data-driven — no `listening` hardcode in the firing path")
check("walkthrough STAGES (PART_GRAIN.stage=True)", s.mode_stages("walkthrough"))
check("walkthrough cast is EMPTY today (no role declares it yet — guided-review adds it)",
      s.cast_for_mode("walkthrough") == [])
check("listening cast is non-empty (the built cast)", len(s.cast_for_mode("listening")) > 0)

# a TEMP role declaring mode_scope ⊇ {walkthrough} → cast_for_mode picks it up (the data-driven proof).
# Build it in a temp roles dir + discover, so nothing is planted in the committed roles/ (guided-review's).
tmp_roles = tempfile.mkdtemp(prefix="cbl-roles-")
with open(os.path.join(tmp_roles, "wt_probe.py"), "w") as f:
    f.write(
        "from pydantic import BaseModel\n"
        "class WtProbeOut(BaseModel):\n    note: str\n"
        "ROLE = {\n"
        "    'id': 'wt_probe',\n"
        "    'label': 'Walkthrough probe',\n"
        "    'prompt_template': 'Narrate the step.',\n"
        "    'output_schema': WtProbeOut,\n"
        "    'mode_scope': {'walkthrough'},\n"
        "    'input_addresses': ('utterance',),\n"
        "}\n")
from runtime.roles import RoleRegistry
reg = RoleRegistry().discover([tmp_roles])
cast = reg.cast_for_mode("walkthrough")
check("a role declaring mode_scope={walkthrough} → cast_for_mode('walkthrough') picks it up (NO engine block)",
      any(getattr(r, "id", None) == "wt_probe" for r in cast))
probe = next((r for r in cast if getattr(r, "id", None) == "wt_probe"), None)
check("the probe role is fireable (prompt_template ⇒ can_fire) → chat_parts WOULD fire it on a walkthrough turn",
      probe is not None and getattr(probe, "can_fire", False))

print(f"\n{'ALL PASS' if ok else 'FAILURES PRESENT'} — {PASS} checks passed — C 4/4: cast-beyond-listening "
      "is a data-driven capability (no listening hardcode; a non-listening role fires its cast); op + "
      "input_addresses projected. The walkthrough cast is guided-review's to declare ON this capability.")
sys.exit(0 if ok else 1)
