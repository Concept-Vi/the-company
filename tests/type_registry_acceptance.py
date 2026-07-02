"""tests/type_registry_acceptance.py — ④ L3 · THE GENERATIVE TYPE REGISTRY (organ-studies/REGISTRY.md · C3.1–C3.6).

Proves BY USE the rebuilt organ: B's registration act driving A's cascade, the fan-out's completeness itself
registered + drift-tested + served to both faces from one function.

  C3.1  types/+cascades/ discovered; create(kind='type') GATES a trivial schema (teaching refusal, the REAL
        create() surface), writes+commits+rediscovers a real one; register a test type END-TO-END then DELETE
        it → the fan-out RETRACTS. (git commit stubbed so the acceptance is repeatable — the mechanism, not the log.)
  C3.2  generate_all per-cascade honesty {ok|error|skipped:reason}; completeness holds generated_from↔generates;
        a HAND-REMOVED artifact fails the drift test; a GHOST (artifact w/ no source type) fails loud; error isolated.
  C3.3  the 9 SOUND cloud types landed + regenerate their artifacts; count reconciliation vs cvi's cascade output.
  C3.4  the 7 HOLLOW dispositions traceable to evidence (RECONSTRUCT 4 / FUSE 3) + observation verdict; the FUSE 3
        are NEVER silently imported (absent from the registry); +2 ghost types registered (routing harvested).
  C3.5  law 11: illegal instance transition refused fail-loud; a resolver read VARIES BY STATE.
  C3.6  Suite.type_info() serves registry + fan-out state to both faces from one function.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from store.fs_store import FsStore                                      # noqa: E402
from runtime.registry import NodeRegistry                              # noqa: E402
from runtime.suite import Suite                                        # noqa: E402
from fabric import config as fcfg                                      # noqa: E402
from runtime import type_registry as TR                                # noqa: E402
from runtime.type_registry import (TypeRegistry, CascadeRegistry, MemoryArtifactStore,  # noqa: E402
                                   generate_all, completeness, validate_transition, state_view,
                                   _is_trivial_schema, artifact_address)

TYPES_DIR = os.path.join(ROOT, "types")
CASCADES_DIR = os.path.join(ROOT, "cascades")
SOUND = {"agent", "cognitive_guide", "deployment", "design", "issue", "model_provider",
         "proposal", "request", "system_graph"}
RECONSTRUCT = {"task", "milestone", "observation", "blocker"}
GHOST = {"research", "diagnostic"}
FUSE = {"decision", "design_proposal", "project_space"}
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def build_suite(mem=True):
    reg = NodeRegistry().discover([os.path.join(ROOT, "nodes")])
    store = MemoryArtifactStore() if mem else None
    s = Suite(FsStore(fcfg.STORE_DIR), reg, artifact_store=store)
    return s


print("── discovery + landing (C3.3/C3.4) ──")
tr = TypeRegistry().discover([TYPES_DIR])
cr = CascadeRegistry().discover([CASCADES_DIR])
check("types/ file-discovered (not a literal)", isinstance(tr, TypeRegistry) and len(tr) == 15)
check("the 9 SOUND cloud types landed as files", SOUND <= set(tr))
check("the 4 RECONSTRUCT types landed", RECONSTRUCT <= set(tr))
check("the 2 GHOST types registered (routing harvested)", GHOST <= set(tr))
check("the 3 FUSE types are NOT in the registry (never silently imported)", not (FUSE & set(tr)))
check("cascades/ file-discovered, priority-ordered",
      [c.id for c in cr.by_priority()][:3] == ["tool", "board", "theme_specs"])
check("6 cascades are cloud_only (honest decline), 4 real", sum(c.cloud_only for c in cr.by_priority()) == 6)

print("── the HOLLOW gate (C3.1) ──")
check("trivial schema {} is trivial", _is_trivial_schema({}))
check("trivial schema {'type':'object'} alone is trivial", _is_trivial_schema({"type": "object"}))
check("a schema with properties is NOT trivial", not _is_trivial_schema({"type": "object", "properties": {"x": {}}}))
try:
    TR._build_type("hollow", {"id": "hollow", "label": "H", "data_schema": {"type": "object"}})
    check("hollow type refused at discovery gate", False)
except ValueError as e:
    check("hollow type REFUSED at discovery gate with teaching msg (HOLLOW-TYPES.md named)",
          "HOLLOW-TYPES" in str(e) and "319" in str(e))

print("── per-cascade HONESTY + completeness (C3.2) ──")
mem = MemoryArtifactStore()
r_task = generate_all(tr["task"], cr, mem)
statuses = {x["cascade"]: x["status"] for x in r_task["results"]}
check("task: tool/board/routing/address = ok (declared faces)",
      all(statuses[c] == "ok" for c in ("tool", "board", "routing", "address")))
check("task: cloud-only cascades = skipped:reason",
      statuses["capability"] == "skipped" and any(x["cascade"] == "capability" and "cloud-only" in x["reason"]
                                                  for x in r_task["results"]))
r_guide = generate_all(tr["cognitive_guide"], cr, mem)
gs = {x["cascade"]: x["status"] for x in r_guide["results"]}
check("cognitive_guide: tool SKIPPED (declares no tool face — honest, matches cvi generates[])", gs["tool"] == "skipped")
check("cognitive_guide: board ok (has board face)", gs["board"] == "ok")
check("an ok artifact records generated_from = the type (the ONE stored edge direction)",
      all(x.get("generated_from") == "task" for x in r_task["results"] if x["status"] == "ok"))
# `generates` = the composed reverse (law 4): artifacts_for(type) reads them back, never a 2nd stored row
gen = mem.artifacts_for("task")
check("generates composed at read (artifacts_for) — law 4 reverse", len(gen) == 4 and all(a["type_id"] == "task" for a in gen))
check("artifact address = type://<type>/face/<cascade> (law 1)", artifact_address("task", "board") == "type://task/face/board")

# completeness after generating ALL types → clean
mem2 = MemoryArtifactStore()
for tid in tr:
    generate_all(tr[tid], cr, mem2)
comp = completeness(tr, cr, mem2)
check("completeness CLEAN after full generate (no drift, no ghosts)", comp["complete"] and not comp["drift"])
# hand-remove an artifact → DRIFT fails loud
mem2.retract_address("type://task/face/board")
comp_drift = completeness(tr, cr, mem2)
check("a HAND-REMOVED artifact FAILS the completeness drift test", not comp_drift["complete"]
      and any(d["type"] == "task" and d["cascade"] == "board" for d in comp_drift["drift"]))
# a GHOST (artifact whose source type is gone) fails loud
mem3 = MemoryArtifactStore()
mem3.put("type://gone/face/board", "gone", "board", "notice_board_types", {})
comp_ghost = completeness(tr, cr, mem3)
check("a GHOST artifact (no source type file) FAILS loud", not comp_ghost["complete"]
      and any(g["orphan_type"] == "gone" for g in comp_ghost["ghosts"]))
# error isolation: a cascade that RAISES → status=error, loop continues (per-cascade containment)
class BoomCascades(CascadeRegistry):
    pass
boom = CascadeRegistry().discover([CASCADES_DIR])
boom.cascades["board"].handle = lambda tr_row, ctx: (_ for _ in ()).throw(RuntimeError("boom"))
r_boom = generate_all(tr["task"], boom, MemoryArtifactStore())
bs = {x["cascade"]: x["status"] for x in r_boom["results"]}
check("a raising cascade → status=error, ISOLATED (other cascades still ok)",
      bs["board"] == "error" and bs["tool"] == "ok" and r_boom["counts"]["error"] == 1)

print("── C3.3 count reconciliation (vs cvi's cascade output) ──")
mem_all = MemoryArtifactStore()
for tid in tr:
    generate_all(tr[tid], cr, mem_all)
arts = mem_all.all_artifacts()
by_cascade = {}
for a in arts:
    by_cascade[a["cascade_id"]] = by_cascade.get(a["cascade_id"], 0) + 1
# tool: types WITH a tool face (SOUND minus cognitive_guide = 8; RECONSTRUCT 4) = 12. cvi = 30 = 15 types × 2
# verbs (create/list). ④ derives ONE tool artifact per type carrying the declared verb SET — a different
# granularity, reconciled: cognitive_guide has NO tool (matches cvi's generates[] lacking mcp_tool).
check("tool artifacts = 12 (types declaring a tool face; cognitive_guide correctly excluded, matches cvi generates[])",
      by_cascade["tool"] == 12)
check("board artifacts = 15 (every type has a board face)", by_cascade["board"] == 15)
check("address artifacts = 15", by_cascade["address"] == 15)
check("routing artifacts = 3 (task + 2 ghosts — the hand-made-powers-generator harvest)", by_cascade["routing"] == 3)
check("no cloud-only cascade produced an artifact (honest decline)",
      all(c not in by_cascade for c in ("capability", "queue_routing", "theme_specs", "embedding_flag")))

print("── C3.4 hollow dispositions traceable + none silently imported ──")
import importlib.util as _ilu                                          # noqa: E402
_s = _ilu.spec_from_file_location("_fm", os.path.join(TYPES_DIR, "_fusion_map.py"))
_fm = _ilu.module_from_spec(_s); _s.loader.exec_module(_fm)
check("FUSE 3 recorded with mapping + evidence (not imported)", set(_fm.FUSIONS) == FUSE
      and all("evidence" in _fm.FUSIONS[k] and _fm.FUSIONS[k]["disposition"] == "FUSE" for k in FUSE))
check("observation verdict = RECONSTRUCT, discriminator = 61-vs-0 posts, note.py+signal.py checked",
      _fm.OBSERVATION_VERDICT["verdict"] == "RECONSTRUCT" and "61" in _fm.OBSERVATION_VERDICT["discriminator"]
      and "item_types/note.py" in _fm.OBSERVATION_VERDICT["checked"])
check("RECONSTRUCT types carry de-facto schema + declared lifecycle (task closure block + 4 states)",
      "verified_by" in tr["task"].data_schema["properties"] and tr["task"].states == ["todo", "in_progress", "blocked", "done"])
check("ghost types carry the harvested routing face (research→Research Scout, diagnostic→QA & Verification)",
      tr["research"].faces["routing"]["agent"] == "Research Scout"
      and tr["diagnostic"].faces["routing"]["agent"] == "QA & Verification")

print("── C3.5 law 11 ──")
try:
    validate_transition(tr["task"], "done", "todo")
    check("illegal transition refused", False)
except ValueError as e:
    check("ILLEGAL instance transition (task done→todo) REFUSED fail-loud", "ILLEGAL" in str(e))
check("a LEGAL transition (task todo→in_progress) is accepted", validate_transition(tr["task"], "todo", "in_progress")["ok"])
check("observation new→validated legal; validated→new illegal (raw≠accepted)",
      validate_transition(tr["observation"], "new", "validated")["ok"])
try:
    validate_transition(tr["observation"], "validated", "new"); check("validated→new refused", False)
except ValueError:
    check("observation validated→new REFUSED (the validation gate is one-way)", True)
sv_done = state_view(tr["task"], "done")
sv_todo = state_view(tr["task"], "todo")
check("resolver read VARIES BY STATE: done requires the verification/closure block",
      sv_done["requires_closure_proof"] and sv_done["closure_required"] == ["resolution", "verified_by", "verified_at"])
check("resolver read VARIES BY STATE: todo requires NO closure proof",
      not sv_todo["requires_closure_proof"] and sv_todo["closure_required"] == [])

print("── C3.1 create()/delete() END-TO-END (real create surface; git stubbed for repeatability) ──")
s = build_suite(mem=True)
# 'type' is picked up by the create() enum (derives from Suite.create_* — path-of-least-resistance)
kinds = sorted(k[len("create_"):] for k in dir(s) if k.startswith("create_")
               and callable(getattr(s, k)) and k != "create_node")
check("create() enum picks up 'type' automatically (Suite.create_type exists)", "type" in kinds)

# the REAL create() tool surface (mcp_face/tools/create.py), captured via a fake mcp
from mcp_face.tools import create as create_tool                       # noqa: E402
_captured = {}
class FakeMCP:
    def tool(self):
        def deco(fn):
            _captured["create"] = fn
            return fn
        return deco
create_tool.register(FakeMCP(), s)
create = _captured["create"]

# gate: a trivial schema is REFUSED with a legible teaching message (NOT a traceback) through create()
refusal = create(kind="type", spec={"id": "zzz_probe", "label": "Probe", "data_schema": {"type": "object"}})
check("create(kind='type') with a trivial schema → LEGIBLE teaching refusal (not a traceback)",
      refusal.get("refused") is True and "HOLLOW-TYPES" in refusal.get("reason", ""))

# stub git + drift-home reflection so the acceptance is repeatable (proves the type mechanism, not the
# commit log / the separately-tested reflect helper — neither should leave a residue on a probe type).
s._git_self_commit = lambda paths, msg, **kw: "stubbedsha"
s._reflect_drift_home = lambda base, rid, kind, desc="": None
TEST_ID = "zzz_probe_type"
probe_path = os.path.join(TYPES_DIR, f"{TEST_ID}.py")
try:
    made = create(kind="type", spec={
        "id": TEST_ID, "label": "Probe Type",
        "data_schema": {"type": "object", "properties": {"title": {"type": "string"}}},
        "faces": {"board": {"status_values": ["open", "closed"], "renderer": "X", "icon": "i", "color": "#000"},
                  "address": {"template": "vi.{user}.zzz.{id}"}},
        "states": ["open", "closed"], "initial": "open", "transitions": {"open": ["closed"], "closed": []},
    })
    check("create(kind='type') with a real schema WRITES the file", os.path.exists(probe_path))
    check("...it is LIVE in the registry", TEST_ID in s.type_registry)
    check("...and FANS OUT (board+address ok, cloud-only skipped)",
          made["fanout"]["counts"]["ok"] == 2 and made["fanout"]["counts"]["skipped"] >= 6)
    check("...the fan-out produced artifacts in the store",
          len(s.artifact_store.artifacts_for(TEST_ID)) == 2)
    # DELETE it → the fan-out RETRACTS
    deleted = s.delete_type(TEST_ID)
    check("delete_type retracts the fan-out (artifacts gone)", deleted["artifacts_retracted"] == 2
          and s.artifact_store.artifacts_for(TEST_ID) == [])
    check("delete_type un-registers the type + removes the file",
          TEST_ID not in s.type_registry and not os.path.exists(probe_path))
finally:
    if os.path.exists(probe_path):                                     # belt-and-suspenders cleanup
        os.remove(probe_path)

print("── C3.6 type_info() serves both faces from one function ──")
s2 = build_suite(mem=True)
for tid in list(s2.type_registry):
    s2.generate_all(tid)
ti = s2.type_info()
check("type_info: types + cascades + completeness + dispositions in ONE envelope",
      {"types", "cascades", "completeness", "dispositions", "counts"} <= set(ti))
check("type_info counts: 15 types, 10 cascades", ti["counts"] == {"types": 15, "cascades": 10})
check("type_info completeness CLEAN", ti["completeness"]["complete"] is True)
check("type_info surfaces the hollow dispositions (not buried)",
      ti["dispositions"]["observation_verdict"]["verdict"] == "RECONSTRUCT"
      and set(ti["dispositions"]["fusions"]) == FUSE)
# BOTH faces (C3.6's defined term — MAP.md "two faces over one shared brain"): the bridge route is in
# BRIDGE_ROUTES and the MCP agent face carries a type_info tool. Both call the ONE Suite.type_info().
from runtime.bridge import BRIDGE_ROUTES                               # noqa: E402
check("UI face: /api/type_info is a BRIDGE_ROUTES entry", "/api/type_info" in BRIDGE_ROUTES)
from mcp_face.server import mcp as _mcp                                # noqa: E402
check("agent face: type_info is a registered MCP tool", "type_info" in _mcp._tool_manager._tools)

print("\nALL TYPE-REGISTRY CHECKS PASSED ✅  ({} checks)".format(PASS))
