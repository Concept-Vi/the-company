"""tests/cognition_info_registries_acceptance.py — the 6 corpus registries projected into the live
cognition VIEW (Cognition Engine, COGNITION-INFO lane).

`build_cognition_info` is the SIBLING-of-object_info serializer the FE/agent read as the live
cognition view (contracts/cognition_info.py). Before this lane it projected roles/rules/edge-kinds/
thought-shapes/activation-contexts/casts/node-states + the cognition.* event-contract — but NOT the
6 file-discovered CORPUS registries (lifters/mark_types/generation_policies/relation_types/ai_tics/
forms) nor projections via the contract. So the agent/FE could not SEE those vocabularies in the
live view. This suite proves, BY USE, that the contract now does — and stays registry-is-truth.

  1. THE PROJECTION (build_cognition_info called DIRECTLY with the live registries):
     - the 6 keys (lifters/mark_types/generation_policies/relation_types/ai_tics/forms) + projections
       + spaces are PRESENT and EQUAL each registry's OWN as_records()/embeddable() (registry-is-truth —
       the discovered set verbatim, NEVER a hand-listed literal). No second projection style.
     - SCHEMA-ADDITIVE / OPTIONAL: a caller that passes NONE of them still gets a valid shape (each
       absent key => [], the existing suite.py call-site stays valid until SUITE-2 passes the kwargs).
  2. REGISTRY-IS-TRUTH (the PART 4.3 add-a-row=a-FILE bar): drop a NEW mark_types/<id>.py → rediscover
     → re-call → the new type APPEARS in the projection with ZERO code change; remove + rediscover → gone.
  3. THE +9 _serialize_role DIFF IS PRESERVED (built ON TOP, not reverted): a role declaring the
     full-schema config fields (thinking/tools/knobs/context/model_binding) projects them present-only.
  4. THE FLOOR (C9.2): build_cognition_info is a pure READ projection — it emits no resolve/approve/
     dispatch (it returns a plain dict; it imports nothing from the runtime that could act).

Run: PYTHONPATH=. python tests/cognition_info_registries_acceptance.py
(Pure backend — needs no model/embedder. The 6 registries are file-discovered from the repo dirs.)
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from store.fs_store import FsStore                       # noqa: E402
from runtime.registry import NodeRegistry                # noqa: E402
from runtime.roles import RoleRegistry, Role             # noqa: E402
from runtime.suite import Suite                           # noqa: E402
from contracts.cognition_info import build_cognition_info, SCHEMA_VER  # noqa: E402

NODES = os.path.join(ROOT, "nodes")

PASS = 0


def ok(cond, label):
    global PASS
    if not cond:
        print(f"  FAIL {label}")
        raise SystemExit(1)
    PASS += 1
    print(f"  ok  {label}")


def fresh_suite(tmp):
    store = FsStore(os.path.join(tmp, "store"))
    reg = NodeRegistry().discover([NODES])
    return Suite(store, reg, nodes_dir=NODES)


# The 6 corpus registries + their Suite attribute name (the live discovered registry objects).
REGISTRIES = [
    ("lifters", "lifter_registry"),
    ("mark_types", "mark_type_registry"),
    ("generation_policies", "generation_policy_registry"),
    ("relation_types", "relation_type_registry"),
    ("ai_tics", "ai_tic_registry"),
    ("forms", "form_registry"),
]


def run():
    tmp = tempfile.mkdtemp(prefix="cog-info-reg-")
    s = fresh_suite(tmp)

    # ---------------------------------------------------------------------------------------------
    # 1. THE PROJECTION — build_cognition_info called DIRECTLY with the live registries returns the
    #    6 keys + projections + spaces, each EQUAL its registry's own as_records()/embeddable().
    # ---------------------------------------------------------------------------------------------
    kwargs = {
        "lifters": s.lifter_registry,
        "mark_types": s.mark_type_registry,
        "generation_policies": s.generation_policy_registry,
        "relation_types": s.relation_type_registry,
        "ai_tics": s.ai_tic_registry,
        "forms": s.form_registry,
        "projections": s.projection_registry,
    }
    info = build_cognition_info(roles=s.role_registry, **kwargs)

    for key, attr in REGISTRIES:
        reg = getattr(s, attr)
        ok(key in info, f"projection carries '{key}'")
        ok(info[key] == reg.as_records(),
           f"'{key}' == {attr}.as_records() (registry-is-truth, the discovered set verbatim)")
        ok(len(info[key]) == len(reg) and len(reg) > 0,
           f"'{key}' projects all {len(reg)} discovered seeds")

    # SCHEMA_VER bumped to 2 (rule 2: a serialization-shape change bumps the marker so a v2-aware FE
    # keys off schema_ver>=2 to expect the 6 registries). The 6 keys being present IS the v2 shape.
    ok(info["schema_ver"] == SCHEMA_VER and SCHEMA_VER >= 2,
       "schema_ver bumped to 2 for the additive 6-registry shape (rule 2: add fields + bump schema_ver)")

    # projections + spaces ride the SAME contract kwarg home (the uniform serialization home).
    ok("projections" in info and info["projections"] == s.projection_registry.as_records(),
       "'projections' == projection_registry.as_records() (via the contract kwarg, not only the suite augment)")
    ok("spaces" in info and info["spaces"] == [p.id for p in s.projection_registry.embeddable()],
       "'spaces' == projection_registry.embeddable() ids (the Group-L vector spaces)")

    # The mark_type VOCABULARY is what's projected (the registry), NOT per-target mark store data —
    # a mark targets a claim/span and is per-target store data (STORE-2); the view carries the TYPES.
    ok(all(isinstance(r, dict) and "id" in r for r in info["mark_types"]),
       "mark_types projects the TYPE vocabulary (id-bearing records), not per-target marks")

    # ---------------------------------------------------------------------------------------------
    # 2. SCHEMA-ADDITIVE / OPTIONAL — a caller that passes NONE of them still gets a valid shape:
    #    each absent key => [] (so the existing suite.py call-site stays valid pre-SUITE-2-wiring).
    # ---------------------------------------------------------------------------------------------
    bare = build_cognition_info(roles=s.role_registry)
    for key, _ in REGISTRIES:
        ok(bare.get(key) == [], f"absent '{key}' defaults to [] (schema-additive, optional kwarg)")
    ok(bare.get("projections") == [] and bare.get("spaces") == [],
       "absent projections/spaces default to [] (existing call-site without kwargs stays valid)")
    # roles/rules/event_kinds still present in the bare call (no regression on the prior shape).
    ok("roles" in bare and "event_kinds" in bare and "node_states" in bare,
       "prior projection keys (roles/event_kinds/node_states) unchanged in the bare call")

    # ---------------------------------------------------------------------------------------------
    # 3. REGISTRY-IS-TRUTH (PART 4.3 add-a-row=a-FILE): drop a NEW mark_types/<id>.py → rediscover →
    #    re-call → the new type APPEARS with ZERO code change; remove + rediscover → gone.
    # ---------------------------------------------------------------------------------------------
    new_id = "cog_info_proof_marktype"
    path = os.path.join(s.mark_types_dir, f"{new_id}.py")
    ok(new_id not in s.mark_type_registry, "proof mark_type not present before the file is dropped")
    try:
        with open(path, "w") as f:
            f.write(
                f'MARK_TYPE = {{"id": "{new_id}", "value_shape": "bool", "direction": "positive",\n'
                f'              "desc": "a proof mark-type dropped by the registry-is-truth test"}}\n')
        s.mark_type_registry.rediscover([s.mark_types_dir])
        info2 = build_cognition_info(roles=s.role_registry, mark_types=s.mark_type_registry)
        ok(any(r.get("id") == new_id for r in info2["mark_types"]),
           "DROP A FILE → rediscover → re-call → the new mark_type APPEARS (registry-is-truth, no code edit)")
    finally:
        if os.path.exists(path):
            os.remove(path)
    s.mark_type_registry.rediscover([s.mark_types_dir])
    info3 = build_cognition_info(roles=s.role_registry, mark_types=s.mark_type_registry)
    ok(not any(r.get("id") == new_id for r in info3["mark_types"]),
       "REMOVE the file → rediscover → re-call → it is GONE (rediscover un-registers, not append-only)")

    # ---------------------------------------------------------------------------------------------
    # 4. THE +9 _serialize_role DIFF IS PRESERVED (built ON TOP) — a role declaring the full-schema
    #    config fields projects them PRESENT-ONLY (thinking/tools/knobs/context/model_binding).
    # ---------------------------------------------------------------------------------------------
    full_spec = {
        "id": "_cog_info_full_role", "label": "Full", "description": "full-schema role",
        "thinking": "high", "tools": ["x"], "knobs": {"temperature": 0.2},
        "context": ["context://foo"],
        "model_binding": {"requires": ["chat", "json"], "default_model": None},
    }
    reg = RoleRegistry()
    reg.roles["_cog_info_full_role"] = Role(id="_cog_info_full_role", spec=full_spec)
    info4 = build_cognition_info(roles=reg)
    row = info4["roles"]["_cog_info_full_role"]
    for fld in ("thinking", "tools", "knobs", "context", "model_binding"):
        ok(fld in row and row[fld] == full_spec[fld],
           f"_serialize_role +9 diff preserved: full-schema field '{fld}' projected verbatim")
    # present-only: a role NOT declaring them omits the keys (the diff's `if ... in spec` guard).
    bare_role_info = build_cognition_info(roles=s.role_registry)
    role_ids = sorted(s.role_registry.roles)
    if role_ids:
        rid = role_ids[0]
        sample = bare_role_info["roles"][rid]
        spec = s.role_registry[rid].spec
        ok(all((k in sample) == (k in spec)
               for k in ("thinking", "tools", "knobs", "context", "model_binding")),
           "full-schema fields are PRESENT-ONLY (a role projects a field iff it declares it)")

    # ---------------------------------------------------------------------------------------------
    # 5. THE FLOOR (C9.2) — build_cognition_info is a pure READ projection: a plain JSON dict, no
    #    resolve/approve/dispatch. (Structural: the module imports nothing from runtime that could act.)
    # ---------------------------------------------------------------------------------------------
    import contracts.cognition_info as ci_mod
    src = open(ci_mod.__file__).read()
    # Strip docstrings/comments before the action-token scan: the module's floor-PROSE legitimately
    # NAMES the forbidden verbs ("the claude -p floor is lead-only", "a cognition.* event can never
    # forge an operator action") — that is the floor being DOCUMENTED, not exercised. The teeth are:
    # no executable resolve/approve/dispatch/subprocess CALL exists. (Same distinction every other
    # lane's floor scan draws — cf. SURFACE.report "the only 'claude -p' matches are floor-DESCRIPTION".)
    code_lines = []
    in_doc = False
    for ln in src.splitlines():
        st = ln.strip()
        if st.startswith("#"):
            continue
        if '"""' in st:
            in_doc = not in_doc if st.count('"""') % 2 else in_doc
            continue
        if in_doc:
            continue
        code_lines.append(ln)
    code = "\n".join(code_lines)
    for forbidden in (".resolve(", ".approve(", "dispatch_decision", "subprocess", "os.system", "claude -p"):
        ok(forbidden not in code,
           f"FLOOR: no executable '{forbidden}' in build_cognition_info code (read-only projection, reflects-never-owns)")

    print(f"\nPASS {PASS} checks — the 6 corpus registries + projections/spaces are projected into the "
          f"live cognition view; registry-is-truth proven by drop-a-file; the +9 role diff preserved.")


if __name__ == "__main__":
    run()
