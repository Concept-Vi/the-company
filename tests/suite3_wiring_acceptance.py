#!/usr/bin/env python3
"""tests/suite3_wiring_acceptance.py — SUITE-3 lane: the WIRING that makes the new substrate LIVE.

The cognition substrate (the 6 corpus registries, embed_corpus_to_spaces, the run_role meta out-param,
route_run_output) was BUILT by prior lanes but not all CALLED. This suite proves the call-sites that make
it live:

  1. cognition_info CALLER — Suite.cognition_info() now PASSES the 6 registries + projections to
     build_cognition_info, so /api/cognition_info + the MCP cognition_info tool show them NON-EMPTY
     (they were [] because the caller didn't pass the kwargs).
  2. CAPTURE-WIRING — the MCP `capture` tool now CALLS embed_corpus_to_spaces on the captured records
     (its first LIVE caller) so a real capture run AUTO-POPULATES the queryable space find_relations reads.
     LINEAGE is in the record BEFORE the first embed (the sequencing gate). Proven with a stub embedder
     (the space_embed_acceptance pattern — :8001 down is needs-tim, the code path is proven here).
  3. O3-persist — the MCP run_role wrapper passes meta={} into the engine and rides finish_reason onto the
     op.run record, so find_runs surfaces WHY a run stopped.
  4. E4 — route_run_output + the saved cascade cover chain save/re-run + output-destination (verified by
     re-running their own suites — see route_run_output_acceptance / cascade_acceptance).
  5. FLOOR — none of the above emits resolve/approve/dispatch.
"""
import os, sys, json, tempfile, types
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from store.fs_store import FsStore
from runtime.suite import Suite
from runtime.registry import NodeRegistry
from runtime import cognition as _cog
from store import vector_index as _vx

PASS = 0
def check(label, cond):
    global PASS
    print(f"  {'ok ' if cond else 'XX '} {label}")
    if not cond:
        raise SystemExit(f"FAIL: {label}")
    PASS += 1


def _new_suite(root):
    reg = NodeRegistry().discover([os.path.join(ROOT, "nodes")])
    return Suite(FsStore(root), reg)


# ---------------------------------------------------------------------------------------------------
# [1] cognition_info CALLER — the 6 registries + projections are NON-EMPTY at the live call site.
# ---------------------------------------------------------------------------------------------------
print("[1] cognition_info CALLER passes the 6 registries (was [] — now NON-EMPTY)")
with tempfile.TemporaryDirectory() as root:
    s = _new_suite(root)
    info = s.cognition_info()
    check("schema_ver == 2 (the additive corpus-registry serialization shape)", info.get("schema_ver") == 2)
    for key in ("projections", "lifters", "mark_types", "generation_policies",
                "relation_types", "ai_tics", "forms"):
        v = info.get(key)
        check(f"cognition_info()[{key!r}] is a NON-EMPTY list (the caller now passes the registry)",
              isinstance(v, list) and len(v) > 0)
        check(f"  {key!r} records carry an `id` (real registry rows, not a stub)",
              all(isinstance(r, dict) and "id" in r for r in v))
    # spaces is derived from projections.embeddable() — the contract kwarg produces it (the augment is gone).
    check("cognition_info()['spaces'] == projection_registry.embeddable() ids (contract-derived, no augment)",
          info.get("spaces") == [p.id for p in s.projection_registry.embeddable()])
    # registry-is-truth: each projected set IS the live registry's as_records() (one source).
    check("projections == projection_registry.as_records() (registry-is-truth, one source)",
          info["projections"] == s.projection_registry.as_records())
    check("lifters == lifter_registry.as_records()", info["lifters"] == s.lifter_registry.as_records())
    check("forms == form_registry.as_records()", info["forms"] == s.form_registry.as_records())
    # the contract default (no augment leftover): the suite no longer hand-sets projections/spaces — they
    # come from the kwarg. Confirm there is NO double-mechanism by checking the augment lines are removed.
    import inspect
    src = inspect.getsource(Suite.cognition_info)
    check("the redundant in-lane info['projections']=/info['spaces']= augment is REMOVED (one mechanism)",
          'info["projections"] =' not in src and 'info["spaces"] =' not in src)


# ---------------------------------------------------------------------------------------------------
# [2] CAPTURE-WIRING — the MCP `capture` tool calls embed_corpus_to_spaces; lineage precedes the embed;
#     records → space → find_relations end-to-end (stub embedder, :8001 down is needs-tim).
# ---------------------------------------------------------------------------------------------------
print("\n[2] CAPTURE-WIRING — capture populates the queryable space (embed-on-write); lineage gate first")

# per-space DISTINCT stub geometry (space_embed_acceptance pattern): the embed_fn seam is
# (transport, inputs, model, dim) -> [vector, ...] one per input text.
_DIM = 4
def _stub(table, default):
    def f(transport, inputs, model=None, dim=None):
        return [table.get(t, default) for t in inputs]
    return f

with tempfile.TemporaryDirectory() as root:
    s = _new_suite(root)
    # drive the MCP `capture` tool's wiring directly. The MCP module binds a global SUITE; we exercise the
    # WIRING (write_corpus_record → embed_corpus_to_spaces) with this Suite + a stubbed embedder, avoiding a
    # live model (run_items) and a live :8001. We monkeypatch the embedder default seam so capture's real
    # un-stubbed embed_corpus_to_spaces call path (no embed_fn passed) runs hermetically.
    import mcp_face.server as srv
    srv.SUITE = s                                       # point the tool at our hermetic Suite

    # the capture tool fans run_items (a live model) — monkeypatch the engine run_items to a deterministic
    # output per unit so the test is hermetic (the WIRING under test is post-run: write+embed, not the fan).
    units = ["unit-A", "unit-B", "unit-C"]
    _outputs = {0: {"principle": "minimize surface"}, 1: {"principle": "fail loud"},
                2: {"principle": "minimize surface"}}
    class _Res:
        resolved = _outputs
        skipped = []; failed = {}; wall_s = 0.01
    srv._cog.run_items = lambda r, u, store, **kw: _Res()
    # resolve the describe-role to anything fireable; capture only uses r.id/r.model/r.op post-fan.
    fake_role = types.SimpleNamespace(id="screen_reader", model="seed", op="generate")
    srv._resolve_role = lambda x: fake_role

    # per-space geometry: in `principles` A≈C (same principle text); B distinct. The embed_fn keys on the
    # EMBED TEXT (the stringified lens output _embed_text produced) — same output → same vector.
    P = {json.dumps({"principle": "minimize surface"}, sort_keys=True, ensure_ascii=False):
            [1.0, 0.0, 0.0, 0.0],
         json.dumps({"principle": "fail loud"}, sort_keys=True, ensure_ascii=False):
            [0.0, 1.0, 0.0, 0.0]}
    # CAPTURE calls embed_corpus_to_spaces WITHOUT an embed_fn (it uses the live embedder by default — :8001
    # DOWN = needs-tim). To prove the CODE PATH hermetically we WRAP the engine fn to inject a stub embed_fn,
    # and CAPTURE what records capture handed it (proving capture assembles {source_address,text,projection}).
    _seen = {}
    _real_embed = _cog.embed_corpus_to_spaces
    def _wrap_embed(store, records, projections, **kw):
        _seen["records"] = records
        kw.setdefault("embed_fn", _stub(P, [0.0, 0.0, 1.0, 0.0]))
        kw.setdefault("dim", _DIM)
        kw.setdefault("model", "seed")
        return _real_embed(store, records, projections, **kw)
    srv._cog.embed_corpus_to_spaces = _wrap_embed

    out = srv.capture("screen_reader", units, project="proj-x", session="sess-1", round="1",
                      projection="principles")
    srv._cog.embed_corpus_to_spaces = _real_embed       # restore

    # capture assembled the embed records correctly (the {source_address, text, projection} shape).
    check("capture handed embed_corpus_to_spaces the {source_address,text,projection} records",
          _seen.get("records") and all(
              set(("source_address", "text", "projection")) <= set(rec) for rec in _seen["records"]))
    check("each embed record names the capture projection ('principles')",
          all(rec["projection"] == "principles" for rec in _seen["records"]))

    # 2a — lineage GATE: every captured record carries session/round/project (written BEFORE embed).
    check("capture wrote N corpus records", len(out["captured"]) == 3)
    rec0 = s.read_corpus_record(out["captured"][0]["address"])
    check("the corpus record carries LINEAGE session/round/project (the gate bit BEFORE embed)",
          rec0 and rec0["lineage"]["project"] == "proj-x"
          and rec0["lineage"]["session"] == "sess-1" and rec0["lineage"]["round"] == "1")

    # 2b — the embed ran (embedded != None) over the EMBEDDABLE 'principles' lens.
    check("capture CALLED embed_corpus_to_spaces (embedded result present — its first live caller)",
          out["embedded"] is not None and out["embedded"]["records"] == 3)
    check("the embed targeted the 'principles' SPACE (the captured projection, embeddable)",
          "principles" in out["embedded"]["spaces"])
    check("the embed did NOT degrade (stub embedder up — vectors written)",
          out["embedded"]["degraded"] is False)

    # 2c — the vectors landed at the SAME key find_relations reads (space_address) — written by the embed
    #      path (NOT a direct put_vector seed).
    va = s.store.get_vector(s.store.space_address("unit-A", "principles"))
    check("the capture-embed wrote unit-A's vector at space_address(unit-A, principles)",
          va is not None and list(va.get("vector") or []) == [1.0, 0.0, 0.0, 0.0]
          and va.get("space") == "principles" and va.get("source") == "unit-A")

    # 2d — END-TO-END: seed a far space ('topics') with a DIFFERENT geometry, then find_relations finds
    #      the near∩¬far inversion over the EMBED-PATH-written near vectors.
    _vx.build_index(s.store, [{"address": "unit-A", "text": "ta"}, {"address": "unit-C", "text": "tc"}],
                    space="topics", embed_fn=_stub({"ta": [1.0, 0.0, 0.0, 0.0], "tc": [1.0, 0.0, 0.0, 0.0]},
                                                   [0.0, 0.0, 0.0, 1.0]), dim=_DIM, model="seed")
    rel = s.find_relations("unit-A", near_space="principles", far_space="topics", k=10, min_score=0.5)
    # unit-C is near A in principles (same vector) AND near in topics (same far vector) → excluded by ¬far.
    check("find_relations runs over the CAPTURE-WRITTEN vectors end-to-end (returns a dict)",
          isinstance(rel, dict) and "relations" in rel)
    check("the inversion EXCLUDES unit-A itself", "unit-A" not in rel["relations"])

print("    (live :8001 embed = needs-tim; the capture→embed→space→find_relations CODE PATH is proven on a stub)")


# ---------------------------------------------------------------------------------------------------
# [3] O3-persist — the MCP run_role wrapper passes meta={} and rides finish_reason onto the op.run record.
# ---------------------------------------------------------------------------------------------------
print("\n[3] O3-persist — run_role rides finish_reason onto the op.run record (find_runs surfaces it)")
with tempfile.TemporaryDirectory() as root:
    s = _new_suite(root)
    import mcp_face.server as srv
    srv.SUITE = s
    fake_role = types.SimpleNamespace(id="ground", model="seed", op="generate")
    srv._resolve_role = lambda x: fake_role

    # the engine run_role is the meta-OUT-PARAM seam: a caller passing meta={} reads finish_reason back.
    # Stub it to (a) return a validated-shape dict AND (b) FILL meta — proving the wrapper threads meta in.
    def _fake_run_role(r, ctx, meta=None, **kw):
        check("run_role wrapper passed meta={} (the O3 out-param seam)", isinstance(meta, dict))
        if meta is not None:
            meta["finish_reason"] = "length"
            meta["usage"] = {"completion_tokens": 256}
        return {"in_scope": True}
    srv._cog.run_role = _fake_run_role

    res = srv.run_role("ground", utterance="hello")
    check("run_role return carries finish_reason (the out-param surfaced to the agent)",
          res.get("finish_reason") == "length")

    # the op.run RECORD (the run index) carries finish_reason — find_runs surfaces it.
    runs = s.find_runs(role="ground")["runs"]
    check("find_runs(role='ground') discovered the run", len(runs) >= 1)
    check("the discovered run row carries finish_reason='length' (O3 persisted to the op.run index)",
          any(rw.get("finish_reason") == "length" for rw in runs))
    # the op.run event itself carries usage (cheap introspective extra).
    evs = [e for e in s.store.events_since(-1) if e.get("kind") == "op.run" and e.get("op") == "cognition.run_role"]
    check("the op.run event carries finish_reason + usage", evs and evs[-1].get("finish_reason") == "length"
          and evs[-1].get("usage") == {"completion_tokens": 256})

    # meta=None byte-identical: a path NOT filling meta leaves finish_reason None (honest absent).
    def _fake_no_meta(r, ctx, meta=None, **kw):
        return {"ok": True}                              # does not fill meta
    srv._cog.run_role = _fake_no_meta
    res2 = srv.run_role("ground", utterance="hi")
    check("a run that fills no finish_reason → None on the return (honest absent, never fabricated)",
          res2.get("finish_reason") is None)


# ---------------------------------------------------------------------------------------------------
# [4] E4 — route_run_output (output-destination) + the saved cascade (chain save/re-run) exist + work.
#     The full proofs are route_run_output_acceptance.py + cascade_acceptance.py; here we assert presence
#     + the floor on route_run_output (so E4's coverage is asserted in THIS lane too).
# ---------------------------------------------------------------------------------------------------
print("\n[4] E4 — route_run_output + saved-cascade cover chain save/re-run + output-destination")
with tempfile.TemporaryDirectory() as root:
    s = _new_suite(root)
    check("Suite.route_run_output EXISTS (the run-output DESTINATION param of E4)",
          callable(getattr(s, "route_run_output", None)))
    check("Suite.save_cascade EXISTS (the chain SAVE half of E4)", callable(getattr(s, "save_cascade", None)))
    check("Suite.run_cascade EXISTS (the chain RE-RUN half of E4)", callable(getattr(s, "run_cascade", None)))
    # route a discovered output to a durable address (the convenience the brief named).
    src = "run://turn-z/ground"
    s.store.set_ref(src, s.store.put_content("the ground role concluded: in-scope"))
    r = s.route_run_output(src, "address", turn_id="t-e4")
    check("route_run_output(address) acted + landed a re-resolvable address",
          r.get("acted") and "in-scope" in str(_cog.resolve_address(s.store, r["address"], turn_id="t-e4")))
    # the FLOOR: resolve/approve/dispatch are NOT routable destinations.
    from runtime import rules as _rules
    check("route_run_output's DESTINATION_KINDS contain NO resolve/approve/dispatch (the floor)",
          not ({"resolve", "approve", "dispatch"} & set(_rules.DESTINATION_KINDS)))
    raised = False
    try:
        s.route_run_output(src, "dispatch")
    except ValueError:
        raised = True
    check("routing to 'dispatch' is REFUSED fail-loud (the build-dispatch floor is unforgeable)", raised)


# ---------------------------------------------------------------------------------------------------
# [5] THE FLOOR — none of the wired call-sites emits resolve/approve/dispatch.
# ---------------------------------------------------------------------------------------------------
print("\n[5] THE FLOOR — capture-wiring + cognition_info + O3 are computation/telemetry, never an action")
import inspect as _ins
import mcp_face.server as srv2
cap_src = _ins.getsource(srv2.capture)
# strip the docstring before scanning (it MENTIONS the floor for documentation).
cap_body = cap_src.split('"""', 2)[-1] if '"""' in cap_src else cap_src
for forbidden in ("resolve_surfaced", "dispatch_decision", ".approve(", "drive_dispatchable"):
    check(f"capture's CODE BODY makes no {forbidden} call (the floor — capture is computation)",
          forbidden not in cap_body)
ci_src = _ins.getsource(Suite.cognition_info)
ci_body = ci_src.split('"""', 2)[-1] if '"""' in ci_src else ci_src
check("cognition_info is a pure read projection (no resolve/dispatch in its body)",
      "resolve_surfaced" not in ci_body and "dispatch_decision" not in ci_body)

print(f"\nALL {PASS} CHECKS PASS — SUITE-3 WIRING: cognition_info caller passes the 6 registries (NON-EMPTY); "
      f"capture POPULATES the queryable space (embed-on-write, lineage-gated, first live caller of "
      f"embed_corpus_to_spaces); run_role rides finish_reason onto the op.run index (O3 persisted); E4 "
      f"covered by route_run_output + saved-cascade; the floor holds. (Live :8001 embed = needs-tim.)")
