"""tests/conv_index_acceptance.py — X12 · the PERSISTED VECTOR INDEX (Convergence).

WHAT X12 IS (Convergence Completion Criteria X12 + Implementation Guide X12 + Research Synthesis
Round 5 — STATE.md:47 names this "the next rung": embed-based retrieval against a LIVE index; no
index exists today). Embedding is on-the-fly and the repo has outgrown whole-repo context-stuffing
(the `codebase` node fail-louds at 600k; the repo is 865k). X12 builds the PERSISTED vector index:

  - a NEW namespace in the addressed store (`vectors/`, a SIBLING of objects/refs/surfaced under
    STORE_DIR — ONE substrate, NOT a parallel store), keyed by the SAME `code://`/`ui://` addresses,
    holding `{address: vector, content_hash, dim, model}`.
  - a BUILD/REFRESH path: for each addressed corpus unit (granularity = ONE entry per addressed item,
    the corpus unit = its text), embed its text via the EXISTING fabric embed path
    (`fabric.client.complete_embeddings` + `fabric.transport.openai_embeddings_transport` — the exact
    path nodes/embed.py uses, NO new transport) → store `{address: vector, content_hash}`. The
    content-hash makes a re-build INCREMENTAL: only CHANGED content re-embeds.
  - a QUERY path: given a query vector, return the top-K nearest addresses — REUSING nodes/retrieve
    (the cosine is NOT reimplemented).

THE HARD CONSTRAINT — DEGRADE-WITH-WARNING when :8001 is DOWN (it is down RIGHT NOW): the build path
emits a LOUD warning + writes NO fabricated vectors (the index stays empty/partial HONESTLY); it does
NOT crash, does NOT write zero-vectors. LIVE population is the :8001-up follow-up. The query over an
empty index returns empty + an HONEST note (the caller — X13/consult — already falls back).

THE PROOFS (mock-up + live-down — mirrors the honest pattern X11 used):

  1. MOCKED-UP build: build over a small fixture corpus → the `vectors/` namespace holds {address:
     vector} keyed by address; a query vector returns the NEAREST address (top-K ranking, reusing
     nodes/retrieve).
  2. INCREMENTAL: a re-build with UNCHANGED content does NOT re-embed (content-hash); a CHANGED item
     DOES re-embed (and, per the no-op rule, an all-unchanged rebuild hits the endpoint ZERO times and
     emits NO warning — a spurious 'embedder down' on an unchanged rebuild would be a false fail-loud).
  3. EMBEDDER-DOWN — verified TWO ways (so the suite stays green now AND when :8001 recovers):
       (a) MOCK down (always-green logic proof): the embed call RAISES → the build emits a warning,
           writes NO vectors, does NOT crash; the query returns empty + an honest note.
       (b) LIVE down (reachability-GATED): probe :8001 — if genuinely unreachable (it is now), run the
           REAL degrade against the real fabric and assert it; if :8001 is UP, SKIP-with-note (so this
           suite never flips RED the moment the embedder recovers — that is the documented follow-up,
           not a regression).
  4. dim guard FAIL-LOUD: a query vector whose dim != a stored vector's dim RAISES (reuses
     nodes/retrieve._cosine's dim guard — never a wrong-but-plausible cosine).
  5. ext4 store namespace, ADDRESSES as keys, persistence-survives-reload (a second store over the
     same root sees the first's vectors).

No live model is hit in the mock paths — the embed transport is MOCKED (a deterministic stub vector
for UP, a raise for DOWN), exactly the hermetic seam X11/conv_semantic_rank use.
"""
import os, sys, tempfile, socket, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["COMPANY_TEST_RUN"] = "1"

from store.fs_store import FsStore
from store import vector_index
from fabric import config as fcfg

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


# ---------------------------------------------------------------------------------------------------
# Deterministic embed stubs (no live model). A tiny 3-dim concept axis: each known text maps to a
# fixed vector so cosine relevance is deterministic. UP returns a vector per input; DOWN raises.
# ---------------------------------------------------------------------------------------------------
_VECS = {
    "the conversational chat reply organ":        [1.0, 0.0, 0.0],
    "the voice synthesis text-to-speech engine":  [0.9, 0.1, 0.0],   # near chat
    "the finance ledger and invoice accounting":  [0.0, 0.0, 1.0],   # orthogonal
}
_DIM = 3


def _stub_embed_up(transport, inputs, model, dim=None, **kw):
    """Stand-in for fabric.client.complete_embeddings (UP): a deterministic vector per input text.
    An unknown text degrades to an orthogonal zero-relevance vector (never raises — UP = reachable)."""
    return [_VECS.get(s, [0.0, 0.0, 1.0]) for s in inputs]


def _stub_embed_down(transport, inputs, model, dim=None, **kw):
    """Stand-in for :8001 DOWN: raise, exactly as the guarded fabric does when the endpoint errors."""
    raise RuntimeError("embed endpoint unreachable (simulated :8001 down)")


def _live_8001_reachable() -> bool:
    """Probe the real embed endpoint. Used to GATE the live-down assertion so this suite never flips
    RED when :8001 recovers (the documented :8001-up follow-up is NOT a regression)."""
    try:
        req = urllib.request.Request(fcfg.DEFAULT_EMBED_URL.rstrip("/") + "/models",
                                     headers={"Authorization": "Bearer none"})
        urllib.request.urlopen(req, timeout=3)
        return True
    except Exception:
        return False


# The fixture corpus — addressed items (granularity: ONE entry per addressed item, corpus unit = text).
# Mixed code:// and ui:// addresses prove the index is keyed by the SAME address grammar (one substrate).
CORPUS = [
    {"address": "code://suite/chat",   "text": "the conversational chat reply organ"},
    {"address": "code://voice/tts",    "text": "the voice synthesis text-to-speech engine"},
    {"address": "ui://finance/ledger", "text": "the finance ledger and invoice accounting"},
]


store_dir = tempfile.mkdtemp(prefix="conv-index-test-")
try:
    # =================================================================================================
    # PART 1 — MOCKED-UP BUILD: the namespace holds {address: vector} keyed by address; query ranks.
    # =================================================================================================
    s = FsStore(os.path.join(store_dir, "s_up"))
    # the vectors/ namespace is a SIBLING of objects/refs (ext4, one substrate)
    check("vectors/ namespace dir is created under the store root (sibling of objects/refs)",
          (s.root / "vectors").is_dir())
    check("objects/ and refs/ still exist (additive — not a parallel store)",
          (s.root / "objects").is_dir() and (s.root / "refs").is_dir())

    res = vector_index.build_index(s, CORPUS, embed_fn=_stub_embed_up, dim=_DIM,
                                   model="stub", base_url="stub://")
    check("build reports the number embedded (all 3 fixture items, embedder up)",
          res.get("embedded") == 3 and res.get("skipped") == 0)
    check("build did NOT degrade (embedder up → no degrade flag)", not res.get("degraded"))

    # the namespace holds {address: vector} keyed by ADDRESS
    addrs = set(vector_index.index_addresses(s))
    check("the index is keyed by the corpus ADDRESSES (code:// and ui://, the same grammar)",
          addrs == {"code://suite/chat", "code://voice/tts", "ui://finance/ledger"})
    rec = vector_index.get_vector(s, "code://suite/chat")
    check("a stored entry holds {address, vector, content_hash, dim, model}",
          rec is not None and rec["address"] == "code://suite/chat"
          and rec["vector"] == _VECS["the conversational chat reply organ"]
          and "content_hash" in rec and rec["dim"] == _DIM)

    # QUERY path: a query vector returns the NEAREST address (top-K), REUSING nodes/retrieve
    q = _VECS["the conversational chat reply organ"]                 # query ~ chat
    ranked = vector_index.query_index(s, q, k=2)
    check("query returns a ranked list of nearest ADDRESSES (reuses nodes/retrieve)",
          isinstance(ranked, list) and len(ranked) == 2)
    check("query top result is the NEAREST address (code://suite/chat)",
          ranked[0]["id"] == "code://suite/chat")
    check("the semantically-near voice item outranks the orthogonal finance item",
          [r["id"] for r in ranked] == ["code://suite/chat", "code://voice/tts"])

    # PERSISTENCE-SURVIVES-RELOAD: a SECOND store over the same root sees the first's vectors
    s2 = FsStore(os.path.join(store_dir, "s_up"))
    check("a second store over the same root sees the persisted vectors (ext4, survives reload)",
          set(vector_index.index_addresses(s2)) == addrs)

    # =================================================================================================
    # PART 2 — INCREMENTAL (content-hash): unchanged content does NOT re-embed; changed DOES.
    # =================================================================================================
    embed_calls = {"n": 0}

    def _counting_embed(transport, inputs, model, dim=None, **kw):
        embed_calls["n"] += len(inputs)
        return [_VECS.get(t, [0.0, 0.0, 1.0]) for t in inputs]

    si = FsStore(os.path.join(store_dir, "s_inc"))
    vector_index.build_index(si, CORPUS, embed_fn=_counting_embed, dim=_DIM, model="stub", base_url="stub://")
    first = embed_calls["n"]
    check("first build embeds every item (content-hash empty → all new)", first == 3)

    # rebuild, UNCHANGED corpus → NO re-embed (content-hash match) AND the endpoint is NOT hit at all
    n_warn_before = len([e for e in si.recent_events(500) if e.get("kind") == "warning"])
    res2 = vector_index.build_index(si, CORPUS, embed_fn=_counting_embed, dim=_DIM, model="stub", base_url="stub://")
    check("rebuild with UNCHANGED content re-embeds NOTHING (content-hash incremental)",
          embed_calls["n"] == first)
    check("an all-unchanged rebuild reports embedded=0, skipped=3", res2.get("embedded") == 0 and res2.get("skipped") == 3)
    n_warn_after = len([e for e in si.recent_events(500) if e.get("kind") == "warning"])
    check("an all-unchanged rebuild emits NO warning (no endpoint round-trip → no false fail-loud)",
          n_warn_after == n_warn_before)

    # change ONE item's text → ONLY that one re-embeds
    changed = [dict(c) for c in CORPUS]
    changed[0]["text"] = "the conversational chat reply organ — now updated and reworded"
    before_change = embed_calls["n"]
    res3 = vector_index.build_index(si, changed, embed_fn=_counting_embed, dim=_DIM, model="stub", base_url="stub://")
    check("a CHANGED item re-embeds (and ONLY it — content-hash diff)",
          embed_calls["n"] == before_change + 1 and res3.get("embedded") == 1 and res3.get("skipped") == 2)

    # =================================================================================================
    # PART 3 — EMBEDDER DOWN (the CRITICAL constraint).
    # (a) MOCK down: build emits a warning, writes NO vectors, does NOT crash; query → empty + honest note.
    # =================================================================================================
    sd = FsStore(os.path.join(store_dir, "s_down"))
    res_d = vector_index.build_index(sd, CORPUS, embed_fn=_stub_embed_down, dim=_DIM, model="stub", base_url="stub://")
    check("DOWN(mock): the build does NOT crash (returns a result)", res_d is not None)
    check("DOWN(mock): the build reports degraded + embedded 0 (no fabricated vectors)",
          res_d.get("degraded") and res_d.get("embedded") == 0)
    check("DOWN(mock): NO vectors were written (index stays empty/honest, no zero-vectors)",
          vector_index.index_addresses(sd) == [])
    warned = any(e.get("kind") == "warning"
                 and ("embed" in e.get("summary", "").lower() or "vector index" in e.get("summary", "").lower())
                 for e in sd.recent_events(500))
    check("DOWN(mock): a LOUD warning was emitted (degrade-with-warning, never silent)", warned)
    # query over the empty index → empty + an HONEST note (the caller falls back)
    qd = vector_index.query_index(sd, [1.0, 0.0, 0.0], k=5, with_note=True)
    check("DOWN(mock): query over the empty index returns empty ranked + an honest note",
          qd["ranked"] == [] and "empty" in qd["note"].lower())

    # =================================================================================================
    # PART 3b — EMBEDDER DOWN, LIVE (reachability-GATED so it never flips RED when :8001 recovers).
    # =================================================================================================
    if _live_8001_reachable():
        print("  ..  SKIP live-down: :8001 is UP — live population is the documented follow-up, not a regression")
    else:
        sl = FsStore(os.path.join(store_dir, "s_live_down"))
        # NO embed_fn → the REAL default fabric path (openai_embeddings_transport → :8001), which is DOWN now
        res_l = vector_index.build_index(sl, CORPUS, dim=fcfg.DEFAULT_EMBED_DIM)
        check("DOWN(LIVE :8001): the build does NOT crash against the real down endpoint", res_l is not None)
        check("DOWN(LIVE :8001): degraded + 0 embedded + NO vectors written (honest empty index)",
              res_l.get("degraded") and res_l.get("embedded") == 0 and vector_index.index_addresses(sl) == [])
        live_warned = any(e.get("kind") == "warning" for e in sl.recent_events(500))
        check("DOWN(LIVE :8001): a LOUD warning was emitted against the real down endpoint", live_warned)

    # =================================================================================================
    # PART 4 — dim guard FAIL-LOUD (reuses nodes/retrieve._cosine's guard; never a bad cosine).
    # =================================================================================================
    raised = False
    try:
        vector_index.query_index(s, [1.0, 0.0], k=2)   # query dim 2 vs stored dim 3 → must raise
    except ValueError:
        raised = True
    check("dim guard: a query vector of the wrong dim RAISES (fail-loud, never a wrong cosine)", raised)

    print(f"\nPASS — {PASS} checks green (X12 persisted vector index: mock-up + incremental + down(mock+live) + dim-guard)")
finally:
    import shutil
    shutil.rmtree(store_dir, ignore_errors=True)
