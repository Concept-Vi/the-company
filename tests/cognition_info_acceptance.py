"""tests/cognition_info_acceptance.py — the cognition VIEW backend (Concurrent Cognition L-fe-be).

The live cognition VIEW (build-prep/concurrent-cognition/06-rendering.md) renders from a SIBLING
projection of the cognition registries (build_cognition_info, the sibling of build_object_info) +
per-turn cognition.* LIFECYCLE events on /api/stream. This suite proves that backend by USE:

  1. THE PROJECTION (build_cognition_info → Suite.cognition_info → /api/cognition_info):
     - GENERATED FROM the live registries (roles/rules/edge-kinds/thought-shapes/activation-contexts/
       rule-ops/destination-kinds/casts/node-states + the cognition.* event-contract) — registry-is-truth.
     - REUSABLE/DYNAMIC: a role registry with an EXTRA role file (a tmp dir) appears in the projection
       with no code change (the ComfyUI generic-renderer pattern — Tim's "reusable and dynamic").
     - REUSE-DON'T-PARALLEL: cognition_capabilities() and cognition_info() share the SAME role serializer
       (no two role serializers that can drift).
     - FAIL LOUD: a role/rule key that disagrees with its own id RAISES (mirrors object_info.py:79-83);
       a malformed THOUGHT_SHAPES/ACTIVATION_CONTEXTS row RAISES.
  2. THE LIFECYCLE EVENTS (Suite.chat_parts, by USE against the resident 4B): a STAGED turn emits the
     cognition.* lifecycle with CAUSAL invariants (not a flat order — the wave is concurrent):
     turn.start first · role.fire×N before all role.ran · inject before the final part · turn.done last ·
     every event carries a TOP-LEVEL address · the existing cognition.wave rollup still emits.
  3. THE FLOOR (C9.2): no cognition.* kind is a resolve/approve/dispatch (narration, not an action).
  4. THE DRIFT HOME (C9.4 / R2-FOLD H5): every COGNITION_EVENT_KINDS entry is reflected in
     runtime/AGENTS.md (mirrors rules_acceptance → runtime/AGENTS.md, edge_kinds_acceptance → contracts/).

Run: PYTHONPATH=. python tests/cognition_info_acceptance.py
(The by-use lifecycle section needs the resident 4B at :8000; it SKIPS loud if absent, never false-passes.)
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from store.fs_store import FsStore                      # noqa: E402
from runtime.registry import NodeRegistry               # noqa: E402
from runtime.roles import RoleRegistry                  # noqa: E402
from runtime.suite import Suite                          # noqa: E402
from contracts.cognition_info import (                   # noqa: E402
    build_cognition_info, COGNITION_EVENT_KINDS, SCHEMA_VER, _serialize_role,
)
from contracts.node_record import EDGE_KINDS            # noqa: E402
from runtime import rules as _rules                      # noqa: E402
from runtime import activation as _act                   # noqa: E402

NODES = os.path.join(ROOT, "nodes")
ROLES = os.path.join(ROOT, "roles")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def _raises(fn):
    try:
        fn()
        return False
    except Exception:
        return True


def fresh_suite(tmp):
    store = FsStore(os.path.join(tmp, "store"))
    reg = NodeRegistry().discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)
    return suite, store


RESIDENT_BASE = "http://127.0.0.1:8000/v1"


def endpoint_up():
    import urllib.request
    try:
        with urllib.request.urlopen(RESIDENT_BASE + "/models", timeout=4) as r:
            return r.status == 200
    except Exception:
        return False


tmp = tempfile.mkdtemp(prefix="lfebe-")
try:
    suite, store = fresh_suite(tmp)

    # ============================================================================================
    # (1) THE PROJECTION — Suite.cognition_info() serializes the live cognition registries
    # ============================================================================================
    print("\n(1) the projection (build_cognition_info → Suite.cognition_info → /api/cognition_info)")
    ci = suite.cognition_info()
    expected_keys = {"schema_ver", "roles", "rules", "edge_kinds", "thought_shapes",
                     "activation_contexts", "rule_ops", "destination_kinds", "casts",
                     "node_states", "event_kinds"}
    check("the projection has every cognition block", expected_keys <= set(ci))
    check("schema_ver is carried (schema-additive marker)", ci["schema_ver"] == SCHEMA_VER)
    check("JSON-serializable (the bridge serves it raw)", json.dumps(ci) and True)

    # GENERATED FROM the live registries — every block equals the registry it came from
    check("roles == the file-discovered role registry",
          set(ci["roles"]) == set(suite.role_registry))
    check("edge_kinds == EDGE_KINDS", set(ci["edge_kinds"]) == set(EDGE_KINDS))
    check("thought_shapes == THOUGHT_SHAPES", set(ci["thought_shapes"]) == set(suite.THOUGHT_SHAPES))
    check("activation_contexts == ACTIVATION_CONTEXTS",
          set(ci["activation_contexts"]) == set(_act.ACTIVATION_CONTEXTS))
    check("rule_ops == RULE_OPS", set(ci["rule_ops"]) == set(_rules.RULE_OPS))
    check("destination_kinds == DESTINATION_KINDS",
          set(ci["destination_kinds"]) == set(_rules.DESTINATION_KINDS))
    check("casts is keyed by every presence mode", set(ci["casts"]) == set(suite.MODES))
    check("the cognition.* event CONTRACT ships in the projection (the FE binds to it)",
          set(ci["event_kinds"]) == set(COGNITION_EVENT_KINDS))
    # each role carries the FE's draw-truth (06 §C) — label/facet/mode_scope/rules
    focus = ci["roles"]["focus"]
    for f in ("id", "label", "can_fire", "is_jury", "draws", "mode_scope", "requires", "rules"):
        check(f"a role serializes its {f!r} (the cognition-node card)", f in focus)
    check("a role's declared rules are serialized AS DATA (the chain/inject edges G7 draws)",
          isinstance(focus["rules"], list))
    # the declared canonical injection rule serializes as an addressable record
    check("the canonical declared rule (recall-injects) is in the rules projection",
          "recall-injects" in ci["rules"])
    r = ci["rules"]["recall-injects"]
    for f in ("id", "when", "when_text", "destination", "inputs"):
        check(f"a rule serializes its {f!r} (the rule badge the view draws)", f in r)

    # ============================================================================================
    # (2) REUSE-DON'T-PARALLEL — cognition_capabilities() shares the SAME role serializer
    # ============================================================================================
    print("\n(2) reuse-don't-parallel — one role serializer (no fork)")
    cc = suite.cognition_capabilities()
    check("cognition_capabilities roles == cognition_info roles (one source)",
          set(cc["roles"]) == set(ci["roles"]))
    # the capabilities subset is a strict projection of the full serializer's fields (proves shared core)
    for rid, sub in cc["roles"].items():
        full = ci["roles"][rid]
        check(f"cap role {rid!r} is a subset of the full serialization (shared serializer)",
              all(sub[k] == full[k] for k in sub))
    # capabilities() exposes the cognition block + the new api verb (registry-is-truth)
    cap = suite.capabilities()
    check("capabilities().cognition is present", "cognition" in cap)
    check("/api/cognition_info is a declared api verb", "/api/cognition_info" in cap["api_verbs"])

    # ============================================================================================
    # (3) DYNAMIC + REUSABLE — a role dropped in a roles dir APPEARS in the projection, no code
    #     (the dynamic proof: the projection is GENERATED from the registry — Tim's directive).
    #     We do NOT pollute the repo roles/ — build a RoleRegistry over a tmp dir with an extra role.
    # ============================================================================================
    print("\n(3) dynamic + reusable — add a role file → it appears in the projection (no FE/code change)")
    extra_dir = os.path.join(tmp, "extra_roles")
    os.makedirs(extra_dir, exist_ok=True)
    # copy one real role so the registry has a baseline, then add a NEW role file
    import shutil
    shutil.copy(os.path.join(ROLES, "focus.py"), os.path.join(extra_dir, "focus.py"))
    with open(os.path.join(extra_dir, "mynewrole.py"), "w") as fh:
        fh.write(
            "from pydantic import BaseModel\n"
            "class Out(BaseModel):\n    ok: bool = True\n"
            "ROLE = {'id': 'mynewrole', 'label': 'My New Role',\n"
            "        'prompt_template': 'echo', 'output_schema': Out, 'mode_scope': {'listening'}}\n"
        )
    reg2 = RoleRegistry().discover([extra_dir])
    proj_before = build_cognition_info(roles=RoleRegistry().discover([ROLES]),
                                       edge_kinds=EDGE_KINDS, thought_shapes=suite.THOUGHT_SHAPES,
                                       activation_contexts=_act.ACTIVATION_CONTEXTS)
    proj_after = build_cognition_info(roles=reg2, edge_kinds=EDGE_KINDS,
                                      thought_shapes=suite.THOUGHT_SHAPES,
                                      activation_contexts=_act.ACTIVATION_CONTEXTS)
    check("a NEW role file appears in the projection with NO serializer change (dynamic)",
          "mynewrole" in proj_after["roles"] and "mynewrole" not in proj_before["roles"])
    check("the new role carries the full FE draw-truth (label/facet)",
          proj_after["roles"]["mynewrole"]["label"] == "My New Role"
          and proj_after["roles"]["mynewrole"]["can_fire"] is True)

    # ============================================================================================
    # (4) FAIL LOUD — a key/id disagreement RAISES (mirrors object_info.py:79-83); a malformed
    #     thought-shape / activation-context RAISES; never a silently-wrong projection.
    # ============================================================================================
    print("\n(4) fail loud — key/id disagreement + malformed registry rows RAISE")

    class _FakeRole:
        id = "real_id"
        spec = {"label": "x"}
        can_fire = False
        is_jury = False
        draws = 1
        mode_scope = frozenset()
        requires = []
    check("a role whose registry KEY disagrees with role.id RAISES (defense-in-depth)",
          _raises(lambda: _serialize_role("WRONG_KEY", _FakeRole())))
    check("a role whose key MATCHES its id serializes fine",
          _serialize_role("real_id", _FakeRole())["id"] == "real_id")
    check("a thought_shape whose value isn't a dict carrying 'archetype' RAISES",
          _raises(lambda: build_cognition_info(roles={}, thought_shapes={"bad": {"no": "archetype"}})))
    check("a thought_shape whose key disagrees with its archetype RAISES",
          _raises(lambda: build_cognition_info(
              roles={}, thought_shapes={"x": {"archetype": "y"}})))
    check("an activation_context whose value isn't a dict RAISES",
          _raises(lambda: build_cognition_info(roles={}, activation_contexts={"bad": "not-a-dict"})))

    # ============================================================================================
    # (5) THE FLOOR (C9.2) — no cognition.* event kind is a resolve/approve/dispatch (NARRATION)
    # ============================================================================================
    print("\n(5) the claude-p floor — cognition.* are NARRATION, never resolve/approve/dispatch")
    for k in COGNITION_EVENT_KINDS:
        check(f"event kind {k!r} is a cognition.* narration kind",
              k.startswith("cognition.") and not any(
                  v in k for v in ("resolve", "approve", "dispatch")))
    for k, spec in COGNITION_EVENT_KINDS.items():
        check(f"event kind {k!r} declares an address field (the locus, C7.2)",
              "address" in spec["fields"])

    # ============================================================================================
    # (6) THE DRIFT HOME (C9.4 / R2-FOLD H5) — COGNITION_EVENT_KINDS reflected in runtime/AGENTS.md
    # ============================================================================================
    print("\n(6) drift home — runtime/AGENTS.md reflects every cognition.* event kind")
    constitution = open(os.path.join(ROOT, "runtime", "AGENTS.md")).read()
    missing = [k for k in COGNITION_EVENT_KINDS if k not in constitution]
    check(f"every COGNITION_EVENT_KINDS entry is reflected in runtime/AGENTS.md (drift: {missing})",
          not missing)
    check("the projection module + endpoint are named in the drift home",
          "build_cognition_info" in constitution and "/api/cognition_info" in constitution)

    # ============================================================================================
    # (7) BY USE — a STAGED turn emits the cognition.* lifecycle with CAUSAL invariants on the log.
    #     (NOT a flat order — the wave fires concurrently; we assert the honest causal structure.)
    # ============================================================================================
    print("\n(7) by use — a staged turn emits the cognition.* lifecycle (causal invariants)")
    if not endpoint_up():
        print("  SKIP (LOUD) — resident 4B at :8000 is DOWN; the by-use lifecycle cannot be proven here.")
        print("              run with the resident pool up to prove the ordered emits.")
    else:
        suite2, store2 = fresh_suite(tmp + "-use")
        suite2.set_mode("listening")                      # a mode that STAGES + has a non-empty cast
        check("listening mode stages (PART_GRAIN.stage=True)", suite2.mode_stages("listening"))
        cast = [r for r in suite2.cast_for_mode("listening")
                if getattr(r, "can_fire", False) and not getattr(r, "is_jury", False)]
        check("listening has a non-empty fireable cast (the view will light up)", len(cast) >= 1)
        # a SUBSTANTIVE message (not a one-liner) so _should_stage stages it
        msg = "What did we decide about the storage layer, and how does the memo gate relate to it?"
        parts = list(suite2.chat_parts(msg, "g-use"))
        check("the staged turn produced >=2 parts (Part 1 base + Part 2 final)", len(parts) >= 2)
        turn_id = next((p.get("turn_id") for p in parts if p.get("turn_id")), None)
        check("the turn carries a turn_id", bool(turn_id))

        # recent_events is NEWEST-FIRST — reverse to CHRONOLOGICAL order (also sort by seq for safety)
        evs = [e for e in store2.recent_events(5000)
               if str(e.get("kind", "")).startswith("cognition.") and e.get("turn_id") == turn_id]
        evs = sorted(evs, key=lambda e: e.get("seq", 0))
        kinds = [e["kind"] for e in evs]
        print(f"      cognition.* event order: {kinds}")

        def idx(kind, last=False):
            ix = [i for i, e in enumerate(evs) if e["kind"] == kind]
            return (ix[-1] if last else ix[0]) if ix else None

        check("cognition.turn.start fired", "cognition.turn.start" in kinds)
        check("cognition.turn.done fired", "cognition.turn.done" in kinds)
        n_fire = kinds.count("cognition.role.fire")
        n_ran = kinds.count("cognition.role.ran")
        check(f"cognition.role.fire fired once per fireable role ({n_fire} == {len(cast)})",
              n_fire == len(cast))
        check(f"cognition.role.ran fired once per role ({n_ran} == {len(cast)})", n_ran == len(cast))
        n_part = kinds.count("cognition.part")
        check(f"cognition.part fired per emitted part ({n_part} >= 2)", n_part >= 2)

        # CAUSAL INVARIANTS (the honest structure under concurrency — not a flat sequence):
        check("INVARIANT: turn.start is FIRST", idx("cognition.turn.start") == 0)
        check("INVARIANT: turn.done is LAST",
              idx("cognition.turn.done", last=True) == len(evs) - 1)
        # every role.fire precedes EVERY role.ran (fires are synchronous pre-wave; rans are post-join)
        last_fire = idx("cognition.role.fire", last=True)
        first_ran = idx("cognition.role.ran")
        if n_fire and n_ran:
            check("INVARIANT: every role.fire precedes all role.ran (pre-wave vs post-join)",
                  last_fire < first_ran)
        # the final part follows all role.ran (the final part reads the wave's resolved injection)
        last_ran = idx("cognition.role.ran", last=True)
        last_part = idx("cognition.part", last=True)
        if n_ran:
            check("INVARIANT: the FINAL part follows the role.ran wave", last_part > last_ran)
        # if an inject fired, it precedes the final part AND identifies its SOURCE role (06 §F#3 — the
        # injection edge source→brain; L-fe cannot draw it from a None source).
        if "cognition.inject" in kinds:
            check("INVARIANT: cognition.inject precedes the final part",
                  idx("cognition.inject") < last_part)
            inj_ev = next(e for e in evs if e["kind"] == "cognition.inject")
            check("INVARIANT: cognition.inject identifies its SOURCE role (not None — the edge origin)",
                  bool(inj_ev.get("source")) and inj_ev.get("source") == inj_ev.get("role"))
            check("INVARIANT: a sourced inject is addressed run://<turn>/<source> (the source instance)",
                  inj_ev.get("address") == f"run://{turn_id}/{inj_ev['source']}")
        # EVERY cognition.* lifecycle event carries a TOP-LEVEL address (the locus, C7.2)
        check("INVARIANT: every cognition.* lifecycle event carries a top-level address",
              all(e.get("address") for e in evs))
        # the addresses are the declared loci: ui://cognition/<turn> + run://<turn>/<role>
        addrs = {e["address"] for e in evs}
        check(f"the turn frame is addressed ui://cognition/{turn_id}",
              f"ui://cognition/{turn_id}" in addrs)
        check("role events are addressed run://<turn>/<role>",
              any(a.startswith(f"run://{turn_id}/") for a in addrs))

        # PRESERVED: the per-WAVE cognition.wave rollup still emits (not removed by the lifecycle work)
        n_wave = len([e for e in store2.recent_events(5000) if e.get("kind") == "cognition.wave"])
        check("PRESERVED: the cognition.wave rollup still emits (additive, not replaced)", n_wave >= 1)

    print(f"\nPASS — {PASS} checks")
finally:
    import shutil as _sh
    _sh.rmtree(tmp, ignore_errors=True)
    _sh.rmtree(tmp + "-use", ignore_errors=True)
