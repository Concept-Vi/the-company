"""tests/space_embed_acceptance.py — SPACE-KEYED EMBED, end-to-end (Cognition Engine GROUP L · L1/D2 + O3).

THE GAP THIS CLOSES (the SURFACE-flagged end-to-end break): run_role(op=embed) PRODUCES a vector but the
result was never put_vector'd into a SPACE — so the corpus's embedded records never populated a queryable
space and find_relations (the cross-space inversion-finder) had nothing to read end-to-end. Its own
docstring says the item "must be embedded in both spaces first (run the capture+embed pass)" — that pass
did NOT exist. `runtime.cognition.embed_corpus_to_spaces` IS that pass.

Proven BY USE (no live model — :8001 is DOWN, so the embed is a SEEDED stub exactly as
conv_index_space_acceptance does; the wiring + the persisted-query path are the unit under test):

  L1/D2 — THE END-TO-END WIRE (the headline):
    1. corpus records (per-space DISTINCT text) → embed_corpus_to_spaces(embed_fn=stub) → the vectors land
       at store.space_address(source, space) — the SAME key find_relations reads. NOT a direct put_vector
       seed: the vectors are written BY THE EMBED PATH (build_index's space-keyed put_vector).
    2. find_relations(item, near=principles, far=topics) reads those EMBED-PATH-written vectors and returns
       the near∩¬far inversion (A: same principle, different topic) — and the TEETH hold: B (near in far)
       and C (near in BOTH) are excluded; the geometry DIFFERS per space (else near==far, trivially empty).
    3. REUSE-DON'T-PARALLEL: the persist IS store.put_vector via vector_index.build_index(space=) — one
       embed path (complete_embeddings), one vector index, one key (space_address). No 2nd vector path.

  FAIL LOUD (rule 4):
    4. a record missing source_address / text / projection RAISES before any write.
    5. a record naming a NON-EMBEDDABLE projection RAISES (registry-is-truth — only embeds==True is a space).
    6. EMBEDDER-DOWN: a raising embed_fn → degrade-with-warning (a LOUD durable `warning` event, NO vectors
       written, degraded=True, NO crash) — the sanctioned batch-path degrade (still fail-loud: never a
       silent [], never a fabricated vector). A re-embed when :8001 is up then populates the space.

  O3 — finish_reason OUT-PARAM (in-lane half):
    7. run_role's DEFAULT path, given meta={}, surfaces the transport's finish_reason WITHOUT changing the
       returned shape (meta=None is byte-identical to before). PERSISTING it into the op.run record is the
       MCP wrapper's emit (server.py — a DIFFERENT lane; flagged needs-coordination, not edited here).

  THE FLOOR (C9.2): embed_corpus_to_spaces is a store WRITE (put_vector) — it emits NO op.run /
    resolve / approve / dispatch; not on the MCP face, not in RHM_VERBS.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from store.fs_store import FsStore                                          # noqa: E402
from runtime.registry import NodeRegistry                                   # noqa: E402
from runtime.suite import Suite                                             # noqa: E402
from runtime import cognition as cog                                        # noqa: E402

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def raises(label, fn, exc=Exception):
    try:
        fn()
    except exc:
        check(label, True)
        return
    check(label, False)


def new_suite(root):
    store = FsStore(os.path.join(root, "store"))
    reg = NodeRegistry().discover([os.path.join(ROOT, "nodes")])
    return Suite(store, reg)


_DIM = 2

# The SAME three source items, embedded at TWO lenses with DIFFERENT per-space geometry (the teeth):
#   PRINCIPLES: ITEM≈A≈C ([1,0]); B orthogonal ([0,1]).
#   TOPICS:     ITEM≈B≈C ([1,0]); A orthogonal ([0,1]).
# So near=principles ∩ ¬(far=topics) for ITEM = {A} — shares the PRINCIPLE, diverges in TOPIC.
#   B is excluded trivially (not near in principle-space).
#   C is the ¬far TEETH: near in BOTH — excluded ONLY by the far subtraction.
_PRINCIPLE = {
    "ITEM principle text": [1.0, 0.0],
    "A principle text":    [1.0, 0.0],   # near ITEM in principle-space
    "B principle text":    [0.0, 1.0],   # orthogonal in principle-space
    "C principle text":    [1.0, 0.0],   # near ITEM in principle-space (the teeth)
}
_TOPIC = {
    "ITEM topic text": [1.0, 0.0],
    "A topic text":    [0.0, 1.0],       # orthogonal in topic-space (the inversion)
    "B topic text":    [1.0, 0.0],       # near ITEM in topic-space (not an inversion)
    "C topic text":    [1.0, 0.0],       # near ITEM in topic-space (the teeth)
}


def _stub(table):
    # build_index's embed_fn seam: (transport, inputs, model, dim) -> [vector,...]
    def _embed(transport, inputs, model, dim=None, **kw):
        return [table.get(s, [0.0, 1.0]) for s in inputs]
    return _embed


PRINCIPLE_RECORDS = [
    {"source_address": "ITEM", "projection": "principles", "text": "ITEM principle text"},
    {"source_address": "A",    "projection": "principles", "text": "A principle text"},
    {"source_address": "B",    "projection": "principles", "text": "B principle text"},
    {"source_address": "C",    "projection": "principles", "text": "C principle text"},
]
TOPIC_RECORDS = [
    {"source_address": "ITEM", "projection": "topics", "text": "ITEM topic text"},
    {"source_address": "A",    "projection": "topics", "text": "A topic text"},
    {"source_address": "B",    "projection": "topics", "text": "B topic text"},
    {"source_address": "C",    "projection": "topics", "text": "C topic text"},
]


store_dir = tempfile.mkdtemp(prefix="space-embed-test-")
try:
    suite = new_suite(store_dir)
    store = suite.store
    embeddable = suite.projection_registry.embeddable()   # registry-is-truth (the declared space set)
    embeddable_ids = {p.id for p in embeddable}
    check("the seed projections registry declares principles+topics as EMBEDDABLE spaces (embeds==True)",
          {"principles", "topics"} <= embeddable_ids)

    # =============================================================================================
    # L1/D2 (1) — THE EMBED PATH WRITES the vectors (NOT a direct put_vector seed)
    # =============================================================================================
    # nothing in the spaces yet
    check("principles space is empty before the embed pass",
          store.index_addresses(space="principles") == [])

    rp = cog.embed_corpus_to_spaces(store, PRINCIPLE_RECORDS, embeddable,
                                    embed_fn=_stub(_PRINCIPLE), dim=_DIM, model="seed")
    rt = cog.embed_corpus_to_spaces(store, TOPIC_RECORDS, embeddable,
                                    embed_fn=_stub(_TOPIC), dim=_DIM, model="seed")
    check("embed pass embedded all 4 principle records (not degraded)",
          rp["spaces"]["principles"]["embedded"] == 4 and rp["degraded"] is False)
    check("embed pass embedded all 4 topic records (not degraded)",
          rt["spaces"]["topics"]["embedded"] == 4 and rt["degraded"] is False)

    # the vectors landed at the SAME key find_relations reads: store.space_address(item, space).
    pv = store.get_vector(store.space_address("ITEM", "principles"))
    check("the EMBED PATH wrote ITEM's principle vector at space_address(ITEM, principles)",
          pv is not None and pv["vector"] == [1.0, 0.0] and pv["space"] == "principles" and pv["source"] == "ITEM")
    check("the indexed principle space holds exactly the 4 SOURCE items (round-trips by source)",
          set(store.index_corpus(space="principles") and
              [r["id"] for r in store.index_corpus(space="principles")]) == {"ITEM", "A", "B", "C"})
    check("a spaced vector did NOT leak into the DEFAULT/unspaced index (no pollution)",
          store.index_addresses() == [])

    # =============================================================================================
    # L2 (2) — find_relations reads the EMBED-PATH-written vectors → the near∩¬far inversion
    # =============================================================================================
    rel = suite.find_relations("ITEM", near_space="principles", far_space="topics", k=10)
    check("END-TO-END: find_relations(near=principles, far=topics) over EMBED-PATH vectors → A is the "
          "inversion (same principle, different topic)", "A" in rel["relations"])
    check("TEETH: B excluded (near in far_space=topics — not an inversion)", "B" not in rel["relations"])
    check("TEETH: C excluded by the ¬far subtraction (near in BOTH spaces)", "C" not in rel["relations"])
    check("find_relations excludes the item itself", "ITEM" not in rel["relations"])

    # =============================================================================================
    # (3) REUSE — embed_corpus_to_spaces is a thin delegate to build_index(space=) (no 2nd path)
    # =============================================================================================
    import inspect
    src = inspect.getsource(cog.embed_corpus_to_spaces)
    # strip the docstring (it MENTIONS build_index/put_vector for documentation); assert the CODE BODY
    # calls build_index(space=) and never makes a `.put_vector(` CALL itself (build_index owns persist).
    body = src.split('"""', 2)[-1] if src.count('"""') >= 2 else src
    check("embed_corpus_to_spaces CODE calls build_index(space=) (reuse — the existing space-keyed persist)",
          "build_index(store" in body and "space=proj" in body)
    check("embed_corpus_to_spaces makes NO .put_vector( call itself (no 2nd vector path — build_index owns it)",
          ".put_vector(" not in body)

    # incremental: re-running the SAME records is all-skipped (build_index's content-hash diff, free reuse)
    rp2 = cog.embed_corpus_to_spaces(store, PRINCIPLE_RECORDS, embeddable,
                                     embed_fn=_stub(_PRINCIPLE), dim=_DIM, model="seed")
    check("re-embedding unchanged records is all-SKIPPED (incremental diff inherited from build_index)",
          rp2["spaces"]["principles"]["embedded"] == 0 and rp2["spaces"]["principles"]["skipped"] == 4)

    # =============================================================================================
    # (4)/(5) FAIL LOUD — bad records RAISE before any write
    # =============================================================================================
    raises("a record missing source_address RAISES",
           lambda: cog.embed_corpus_to_spaces(store, [{"projection": "principles", "text": "x"}],
                                               embeddable, embed_fn=_stub({}), dim=_DIM), exc=ValueError)
    raises("a record with empty text RAISES (never embed an empty string)",
           lambda: cog.embed_corpus_to_spaces(store, [{"source_address": "Z", "projection": "principles",
                                                       "text": "  "}], embeddable, embed_fn=_stub({}),
                                              dim=_DIM), exc=ValueError)
    raises("a record missing projection RAISES",
           lambda: cog.embed_corpus_to_spaces(store, [{"source_address": "Z", "text": "x"}],
                                               embeddable, embed_fn=_stub({}), dim=_DIM), exc=ValueError)
    raises("a record naming a NON-EMBEDDABLE projection RAISES (registry-is-truth — only a space is embeddable)",
           lambda: cog.embed_corpus_to_spaces(store, [{"source_address": "Z", "projection": "what",
                                                       "text": "x"}], embeddable, embed_fn=_stub({}),
                                              dim=_DIM), exc=ValueError)

    # =============================================================================================
    # (6) EMBEDDER-DOWN — degrade-with-warning (loud durable event, no vectors, no crash)
    # =============================================================================================
    down_store_dir = tempfile.mkdtemp(prefix="space-embed-down-")
    try:
        ds = FsStore(os.path.join(down_store_dir, "store"))

        def _down(transport, inputs, model, dim=None, **kw):
            raise RuntimeError("connection refused (:8001 down)")

        ev_before = len(ds.events_since(-1))
        res = cog.embed_corpus_to_spaces(ds, PRINCIPLE_RECORDS, embeddable,
                                         embed_fn=_down, dim=_DIM, model="seed")
        check("embedder-DOWN: degraded=True (build_index's sanctioned degrade — NOT a crash)",
              res["degraded"] is True and res["spaces"]["principles"]["degraded"] is True)
        check("embedder-DOWN: NO vectors written (never a fabricated/zero vector, never a silent [])",
              ds.index_addresses(space="principles") == [])
        warnings = [e for e in ds.events_since(-1) if e.get("kind") == "warning"]
        check("embedder-DOWN: a LOUD durable `warning` event was emitted (fail-loud detectable channel)",
              len(warnings) >= 1 and "embed endpoint unreachable" in warnings[-1].get("summary", ""))
    finally:
        import shutil
        shutil.rmtree(down_store_dir, ignore_errors=True)

    # =============================================================================================
    # O3 (7) — run_role default path surfaces finish_reason via the meta out-param (in-lane half)
    # =============================================================================================
    from pydantic import BaseModel
    import fabric.client as _client
    import fabric.transport as _transport

    class _Out(BaseModel):
        answer: str

    class _Role:
        id = "o3_probe"
        op = "generate"
        prompt_template = "you are a probe"
        output_schema = _Out
        input_addresses = ["utterance"]

    # stub the transport so it fills meta exactly as the real openai_transport does (via _fill_meta) —
    # proving meta={} reaches the transport unchanged on the DEFAULT path. cognition.run_role calls
    # `transport.openai_transport(...)` via the module ref, so patching the module attr is the seam.
    _orig_openai_transport = _transport.openai_transport

    def _fake_transport(base_url=None, timeout=None, **kw):
        def _t(model, messages, **opts):
            # mimic fabric.transport._fill_meta: populate the caller's meta out-param (finish_reason+usage)
            meta = opts.get("meta")
            if meta is not None:
                meta["finish_reason"] = "stop"
                meta["usage"] = {"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8}
            return '{"answer": "ok"}'
        return _t

    _transport.openai_transport = _fake_transport
    try:
        # DEFAULT path (policy=None), meta supplied → finish_reason surfaces, return shape unchanged.
        meta = {}
        out = cog.run_role(_Role(), {"utterance": "hi"}, meta=meta)
        check("O3: run_role(default path, meta={}) surfaces finish_reason from the completion",
              meta.get("finish_reason") == "stop")
        check("O3: meta also carries the token usage (the O3 telemetry)",
              meta.get("usage", {}).get("total_tokens") == 8)
        check("O3: the RETURN shape is unchanged (the validated dict — finish_reason is an OUT-PARAM, "
              "never folded into the return; run_swarm/dry_run_role/run_cascade depend on this)",
              out == {"answer": "ok"})
        # meta=None (every current caller) is byte-identical — no finish_reason read, same return.
        out2 = cog.run_role(_Role(), {"utterance": "hi"})
        check("O3: meta=None (every current caller) is byte-identical — same return, no meta needed",
              out2 == {"answer": "ok"})
    finally:
        _transport.openai_transport = _orig_openai_transport       # restore the real transport

    # =============================================================================================
    # THE FLOOR — embed_corpus_to_spaces is not on the MCP face / RHM_VERBS, emits no engine run-record
    # =============================================================================================
    check("embed_corpus_to_spaces is NOT in RHM_VERBS (the floor — a store write, never a verb)",
          "embed_corpus_to_spaces" not in suite.RHM_VERBS)
    # the embed pass over the live store emitted NO op.run / resolve / dispatch (only the down-store warned)
    floor_evs = [e for e in store.events_since(-1)
                 if e.get("kind") in ("op.run", "decision.dispatch", "decision.resolve")]
    check("the embed pass emitted NO op.run / dispatch / resolve over the live store (computation-floor)",
          floor_evs == [])

    print(f"\nPASS ({PASS} checks) — SPACE-EMBED end-to-end: the corpus capture path embeds records into "
          f"their projection spaces (reuse of build_index(space=) → put_vector), find_relations reads them "
          f"end-to-end (near∩¬far, teeth), fail-loud + embedder-down degrade, O3 finish_reason out-param, "
          f"the floor held.")
finally:
    import shutil
    shutil.rmtree(store_dir, ignore_errors=True)
