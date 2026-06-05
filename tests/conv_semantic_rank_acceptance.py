"""tests/conv_semantic_rank_acceptance.py — X13 · R2 SEMANTIC ranking term (Convergence).

WHAT X13 IS (Convergence Completion Criteria X13 + Implementation Guide X13 + Research Synthesis
Round 5): R2 already ranks attached context by recency·proximity·pin (addr_context_acceptance, the
keystone). But it ranks by LOCATION + AGE, not by RELEVANCE to what the operator is actually asking.
X13 adds a SEMANTIC term:

    score = recency·(1/(1+W·proximity)) + pin_bonus + R2_SEMANTIC_WEIGHT·cosine(intent, item)

so the gathered context ranks by RELEVANCE to the operator's intent/comment, not just location+age.
This is Tim's "gather by relevance" — the dispatch (and chat) context becomes semantically ranked.

THE INTENT QUERY SOURCE (stated): the operator's current chat MESSAGE — literally "what the operator
is actually asking" (the spec phrasing). It is threaded `chat(message) → _chat_context(intent=message)
→ _resolve_context_at(intent) → _r2_score_and_cap(intent)`. The locus comment is the SAME mechanism on
the annotate path (any text the operator emits at the locus can be the intent); the chat message is the
production source because the chat turn is when the RHM context is composed.

THE THREE PROOFS (the spec's named cases):

  1. EMBEDDER UP — semantic term WORKS: given an intent and TWO attached items at EQUAL recency/proximity
     (one semantically relevant to the intent, one not), the RELEVANT item ranks higher and SURVIVES the
     budget cap while the irrelevant one is DROPPED. We do NOT hit a live embedder — we MOCK the embed
     call with a deterministic stub whose cosine is high for the relevant text and low for the irrelevant
     one. (The cosine reuse mirrors nodes/similarity.py's dot/(‖a‖·‖b‖); the fabric reach mirrors
     nodes/embed.py — suite.py already reaches the embed fabric, suite.py:904.)

  2. EMBEDDER DOWN — the CRITICAL degrade case: the embed call RAISES (mock) → the semantic term degrades
     to 0 with a LOUD warning (mirror suite.py:906 "embed model registry unreachable") → `_r2_score`/the
     gather does NOT crash → the result == the PRE-X13 recency·proximity·pin ranking (the proven
     fallback). DEGRADE-WITH-WARNING, never a silent zero-vector, never a wrong cosine, never a crash.

  3. PRESERVE — semantic weight 0 ⇒ pre-X13 ordering UNCHANGED: with `semantic=0.0` (the `_r2_score`
     default), the recency·proximity·pin ordering is byte-for-byte the old one. This is what guarantees
     addr_context_acceptance (34) still passes: the existing 3-arg `_r2_score(item, locus, now)` call is
     identical to `_r2_score(item, locus, now, semantic=0.0)`.

The semantic term is gated by a NAMED config constant `R2_SEMANTIC_WEIGHT` (beside R2_LAMBDA /
R2_PROXIMITY_WEIGHT / R2_PIN_WEIGHT / R2_BUDGET; X17 will env-wire it later — a sane default now).

COMPANY_TEST_RUN is set for inbox-hygiene parity with the sibling suites. No live model is hit — the
embed transport is MOCKED in both directions (a deterministic stub vector for UP, a raise for DOWN).
"""
import os, sys, tempfile, math
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["COMPANY_TEST_RUN"] = "1"

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


# Real registered element/region addresses (S1 UI_REGISTRY). One locus; the two test items share it
# (EQUAL proximity) and we stamp EQUAL ts (EQUAL recency) so the SEMANTIC term is the ONLY discriminator.
LOCUS = "ui://chrome/inbox"

# ---------------------------------------------------------------------------------------------------
# Deterministic embed stubs (no live model). The "intent" and the two item texts are mapped to fixed
# unit vectors so cosine(intent, relevant) is HIGH and cosine(intent, irrelevant) is LOW — a stand-in
# for a real embedder's relevance signal, fully deterministic.
# ---------------------------------------------------------------------------------------------------
INTENT = "why is the build stuck and how do I unstick it"
RELEVANT_TEXT = "[comment @ ui://chrome/inbox] the build is stuck waiting on approval"
IRRELEVANT_TEXT = "[comment @ ui://chrome/inbox] the kitchen ran out of coffee this morning"

# unit-ish vectors: intent ~ relevant (small angle); intent ⟂ irrelevant (orthogonal → cosine 0)
_VECS = {
    INTENT:          [1.0, 1.0, 0.0],
    RELEVANT_TEXT:   [1.0, 0.9, 0.0],   # near-parallel to intent → high cosine
    IRRELEVANT_TEXT: [0.0, 0.0, 1.0],   # orthogonal to intent    → cosine 0
}


def _stub_embeddings_up(transport, inputs, model, **kw):
    """Stand-in for fabric.client.complete_embeddings: return a deterministic vector per input text.
    An unknown text degrades to a zero-relevance orthogonal vector (never raises — UP means reachable)."""
    out = []
    for s in inputs:
        out.append(_VECS.get(s, [0.0, 0.0, 1.0]))
    return out


def _stub_embeddings_down(transport, inputs, model, **kw):
    """Stand-in for the embedder being DOWN (:8001 unreachable): raise, exactly as the guarded fabric
    does when the endpoint errors. The X13 code MUST catch this, warn, and degrade the semantic term to 0."""
    raise RuntimeError("embed endpoint unreachable (simulated :8001 down)")


def _cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb)


store_dir = tempfile.mkdtemp(prefix="conv-semantic-rank-test-")
try:
    reg = NodeRegistry(); reg.discover([NODES])

    # ============================================================================================
    # PART 0 — the named config constant exists (D2/X17-configurable, not a bare literal)
    # ============================================================================================
    suite0 = Suite(FsStore(os.path.join(store_dir, "s0")), reg, nodes_dir=NODES)
    check("R2_SEMANTIC_WEIGHT is a named class constant (beside LAMBDA/PROXIMITY/PIN)",
          hasattr(suite0, "R2_SEMANTIC_WEIGHT"))
    check("R2_SEMANTIC_WEIGHT default is a positive float (semantic term has real weight)",
          isinstance(suite0.R2_SEMANTIC_WEIGHT, (int, float)) and suite0.R2_SEMANTIC_WEIGHT > 0)

    # ============================================================================================
    # PART 1 — PRESERVE: _r2_score with semantic=0 (the default) == the pre-X13 ranking, byte-for-byte
    # ============================================================================================
    now = datetime.now(timezone.utc)
    def iso(dt): return dt.isoformat()
    rel_item = {"text": RELEVANT_TEXT, "address": LOCUS, "ts": iso(now), "kind": "annotation",
                "_raw": "the build is stuck waiting on approval"}
    irr_item = {"text": IRRELEVANT_TEXT, "address": LOCUS, "ts": iso(now), "kind": "annotation",
                "_raw": "the kitchen ran out of coffee this morning"}
    # equal recency + equal proximity → with NO semantic term they score IDENTICALLY (the pre-X13 truth)
    s_rel_base = suite0._r2_score(rel_item, LOCUS, now)
    s_irr_base = suite0._r2_score(irr_item, LOCUS, now)
    check("PRESERVE: at equal recency+proximity the pre-X13 score (semantic default 0) is identical",
          abs(s_rel_base - s_irr_base) < 1e-12)
    # the default-0 path is the SAME as explicitly passing semantic=0 (backward-compatible signature)
    check("PRESERVE: _r2_score(item,locus,now) == _r2_score(item,locus,now,semantic=0.0)",
          abs(suite0._r2_score(rel_item, LOCUS, now)
              - suite0._r2_score(rel_item, LOCUS, now, semantic=0.0)) < 1e-12)
    # a POSITIVE semantic term raises the score above the base (the term is additive + weighted)
    bumped = suite0._r2_score(rel_item, LOCUS, now, semantic=1.0)
    check("the semantic term is ADDITIVE: a positive cosine raises the score above the base",
          bumped > s_rel_base
          and abs(bumped - (s_rel_base + suite0.R2_SEMANTIC_WEIGHT * 1.0)) < 1e-9)

    # ============================================================================================
    # PART 2 — EMBEDDER UP: the semantic term WORKS — the RELEVANT item outranks + survives the cap;
    #          the IRRELEVANT one is dropped. Two items, EQUAL recency+proximity → semantic is the
    #          ONLY discriminator. The cap is squeezed so exactly one survives (proves drop, not just order).
    # ============================================================================================
    su = Suite(FsStore(os.path.join(store_dir, "s_up")), reg, nodes_dir=NODES)
    su.annotate(LOCUS, "the build is stuck waiting on approval")
    su.annotate(LOCUS, "the kitchen ran out of coffee this morning")
    gathered = su._r2_gather(LOCUS)
    # locate the two gathered items (the gather re-wraps the raw text into the bracketed `text` form)
    rel = [it for it in gathered if "build is stuck" in it.get("text", "")][0]
    irr = [it for it in gathered if "kitchen ran out" in it.get("text", "")][0]
    # squeeze the budget so only ONE item can survive (forces the cap to DROP the loser)
    su.R2_BUDGET = max(len(rel.get("text", "")), len(irr.get("text", ""))) + 5
    import fabric.client as _fc
    _orig = _fc.complete_embeddings
    _fc.complete_embeddings = _stub_embeddings_up
    try:
        capped_up = su._r2_score_and_cap(gathered, LOCUS, now, intent=INTENT)
    finally:
        _fc.complete_embeddings = _orig
    cap_text_up = " ".join(it.get("text", "") for it in capped_up)
    check("UP: the budget actually drops one item (cap squeezed to a single survivor)",
          len(capped_up) == 1)
    check("UP: the RELEVANT item survives the cap (semantic term ranked it first)",
          "build is stuck" in cap_text_up)
    check("UP: the IRRELEVANT item is DROPPED (semantic term ranked it below the cap)",
          "kitchen ran out" not in cap_text_up)
    # and directly on the score: relevant outscores irrelevant ONLY because of the semantic term
    sem_rel = _cosine(_VECS[INTENT], _VECS[RELEVANT_TEXT])
    sem_irr = _cosine(_VECS[INTENT], _VECS[IRRELEVANT_TEXT])
    check("UP: cosine(intent, relevant) > cosine(intent, irrelevant) (the discriminator is real)",
          sem_rel > sem_irr)
    check("UP: relevant score (with its real cosine) > irrelevant score (with its)",
          su._r2_score(rel, LOCUS, now, semantic=sem_rel)
          > su._r2_score(irr, LOCUS, now, semantic=sem_irr))

    # ============================================================================================
    # PART 3 — EMBEDDER DOWN (THE CRITICAL TEST): the embed call RAISES → no crash, semantic degrades
    #          to 0 with a warning, and the result == the PRE-X13 recency·proximity·pin ranking.
    # ============================================================================================
    sd = Suite(FsStore(os.path.join(store_dir, "s_down")), reg, nodes_dir=NODES)
    sd.annotate(LOCUS, "the build is stuck waiting on approval")
    sd.annotate(LOCUS, "the kitchen ran out of coffee this morning")
    gathered_d = sd._r2_gather(LOCUS)
    n_warn_before = len(sd.store.recent_events(500))

    # the PRE-X13 baseline ranking: the SAME gather scored with NO intent at all (pure recency·proximity·pin)
    baseline = sd._r2_score_and_cap(list(gathered_d), LOCUS, now)
    baseline_order = [it.get("text", "") for it in baseline]

    _fc.complete_embeddings = _stub_embeddings_down
    try:
        # MUST NOT raise — the down-endpoint must degrade, not crash the per-turn gather
        capped_down = sd._r2_score_and_cap(list(gathered_d), LOCUS, now, intent=INTENT)
    finally:
        _fc.complete_embeddings = _orig
    down_order = [it.get("text", "") for it in capped_down]
    check("DOWN: the per-turn score+cap does NOT crash when the embedder raises",
          capped_down is not None)
    check("DOWN: the result == the pre-X13 recency·proximity·pin ranking (proven fallback)",
          down_order == baseline_order)
    # a LOUD warning was emitted (mirror suite.py:906 'embed ... unreachable') — never a silent zero
    evs_after = sd.store.recent_events(500)
    warned = any(e.get("kind") == "warning"
                 and ("embed" in (e.get("summary", "").lower())
                      or "semantic" in (e.get("summary", "").lower()))
                 for e in evs_after)
    check("DOWN: a LOUD warning was emitted (degrade-with-warning, never a silent zero-vector)", warned)

    # full end-to-end DOWN: _resolve_context_at with an intent + a down embedder still returns the
    # bounded slice and does NOT crash the turn (mirrors _chat_context's never-crash discipline)
    sd._chat_context("g", focus={"selected": [LOCUS]})       # set the R1 locus
    _fc.complete_embeddings = _stub_embeddings_down
    try:
        block_down = sd._resolve_context_at(LOCUS, now=now, intent=INTENT)
    finally:
        _fc.complete_embeddings = _orig
    check("DOWN: _resolve_context_at still returns the bounded R2 block (degraded, not crashed)",
          "CONTEXT RESOLVED AT YOUR LOCUS" in block_down)

    # ============================================================================================
    # PART 4 — INTEGRATION: chat() threads the operator MESSAGE as the intent (the stated query source).
    #          We don't hit the chat model; we assert the seam exists end-to-end via _chat_context.
    # ============================================================================================
    si = Suite(FsStore(os.path.join(store_dir, "s_int")), reg, nodes_dir=NODES)
    si.annotate(LOCUS, "the build is stuck waiting on approval")
    si._chat_context("g", focus={"selected": [LOCUS]})       # set the R1 locus
    _fc.complete_embeddings = _stub_embeddings_up
    try:
        ctx = si._chat_context("g", focus={"selected": [LOCUS]}, intent=INTENT)
    finally:
        _fc.complete_embeddings = _orig
    check("INTEGRATION: _chat_context accepts an intent and still injects the R2 locus block",
          "CONTEXT RESOLVED AT YOUR LOCUS" in ctx and "build is stuck" in ctx)

    print(f"\nPASS — {PASS} checks green (X13 R2 semantic ranking term: up + down + preserve)")
finally:
    import shutil
    shutil.rmtree(store_dir, ignore_errors=True)
