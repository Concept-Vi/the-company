"""runtime/decision_memory.py — the COMMON-MEMORY seam for the Live Decision Surface (recollection's piece).

THE SEAM (DECISION-SURFACE-BUILD.md): the surface SHOWS a pending decision → the RHM EXPLAINS it using
the common company memory → Tim decides → write-back. This module is the EXPLAIN-half's memory retrieve:
given a decision (its text + optional address), return the CONTEXT BUNDLE the RHM draws on — prior
discussion, related units, the why, provenance — as ONE shared memory across the channels.

REUSE-DON'T-PARALLEL (the union law): composes the pieces already built into the centre —
  • suite.query_corpus(text, space) — semantic retrieve over the embeddable spaces (the shared corpus)
  • runtime.corpus_rerank.rerank_hits — the jina-v3 precision pass (recollection's committed stage)
  • runtime.corpus_neighbours.neighbours — recall-under-a-unit, when the decision has an address
No new memory, no second store — the corpus IS the shared memory; this is the decision-shaped read of it.

CHANNEL-NATIVE: the bridge exposes this as /api/cognition/recall-for-decision (projection's lane); the
RHM (fork's run_turn) calls it to compose the explanation; every channel member draws on the SAME corpus.

PROVENANCE / LEGIBILITY: every context item carries its source address + space + score, so the RHM's
explanation is GROUNDED (cite-able), and the surface renders MEANING (the digest), never machine ids.
"""
from __future__ import annotations

# the spaces a decision's context can come from, broadest-meaning first. common_knowledge = comprehended
# project/design content; principles/worldview/topics = the why-layer; history = prior discussion; repo =
# the code it touches. Registry-is-truth: this list is the embeddable set (cognition_info().spaces).
DEFAULT_DECISION_SPACES = ("common_knowledge", "principles", "worldview", "topics", "history", "repo")


def prior_decisions_about(suite, topic_text: str, *, k: int = 6) -> list[dict]:
    """"Decisions made about X resurfacing" (the lead's step-6 framing) — surface PRIOR decision-content
    about a topic so Tim sees "you've decided about this before." Decision-FRAMED recall over the
    history + common_knowledge spaces (where decision-notes/comprehended-choices live). Returns
    [{source, space, score}] (rerank-precision when available). Read-only; degrade-clean (a down space →
    fewer items, never fabricated).

    FUTURE (when the decision-surface produces decision-ARTIFACTS — write-backs with scope/kind=decision):
    this filters to those artifacts (find_corpus by the decision kind), so "prior decisions" becomes the
    real decided-artifact set, not just decision-shaped prose. Today it's the decision-framed recall —
    the same compute, a richer source once the surface runs."""
    if not (isinstance(topic_text, str) and topic_text.strip()):
        return []
    framed = f"prior decision, ruling, or chosen approach about: {topic_text}"
    pooled: list[dict] = []
    for sp in ("history", "common_knowledge"):                   # where decisions/choices are recorded
        try:
            out = suite.query_corpus(framed, space=sp, k=k)
        except Exception:
            continue
        for h in out.get("ranked", []):
            pooled.append({"source": h.get("id") or h.get("address"), "space": sp,
                           "score": round(h.get("score", 0.0), 4)})
    if not pooled:
        return []
    try:                                                          # precision pass (reuse the committed stage)
        from runtime import corpus_rerank as _cr
        rr = _cr.rerank_hits(suite.store, framed,
                             [{"id": p["source"], "score": p["score"]} for p in pooled], top_n=k)
        by = {p["source"]: p for p in pooled}
        return [{**by.get(r["address"], {}), "source": r["address"], "rerank_score": r["rerank_score"]}
                for r in rr["reranked"]]
    except Exception:
        return sorted(pooled, key=lambda p: -p["score"])[:k]


def recall_for_decision(suite, decision_text: str, *, address: str | None = None,
                        spaces: tuple | list | None = None, k_per_space: int = 4,
                        rerank: bool = True, top_n: int = 10,
                        include_prior_decisions: bool = True) -> dict:
    """The decision's memory-context bundle for the RHM's explanation.

    `decision_text` — the decision/question text (what the RHM explains). `address` — optional code://
    /run:// of the decision's subject (adds its neighbour node-field). `spaces` — which corpus spaces to
    draw context from (default = the why+content+history set). `include_prior_decisions` — add the
    "decisions made about this before" leg (step-6 framing). Returns
    {decision, context:[{source, space, score, ...}], neighbours:[...]?, prior_decisions:[...]?, note}.
    Read-only.

    DEGRADE-CLEAN (the no-silent-failure floor): a down embedder / empty space yields a smaller bundle +
    an honest note, never a fabricated context. FAIL-LOUD only on a malformed call."""
    if not (isinstance(decision_text, str) and decision_text.strip()):
        raise ValueError("recall_for_decision: decision_text required (the decision/question to explain).")

    spaces = tuple(spaces) if spaces else DEFAULT_DECISION_SPACES
    notes = []
    pooled: list[dict] = []
    for sp in spaces:
        try:
            out = suite.query_corpus(decision_text, space=sp, k=k_per_space)
        except Exception as e:                                   # a space may be unembedded/down — honest, not fatal
            notes.append(f"{sp}: {type(e).__name__}")
            continue
        for h in out.get("ranked", []):
            pooled.append({"source": h.get("id") or h.get("address"), "space": sp,
                           "score": round(h.get("score", 0.0), 4)})
        if out.get("note") and not out.get("ranked"):
            notes.append(f"{sp}: empty")

    # rerank the POOLED cross-space context against the decision (precision over the union of spaces) —
    # reuse the committed stage; it fetches each hit's CAS digest text (fail-loud on a blank).
    if rerank and pooled:
        try:
            from runtime import corpus_rerank as _cr
            rr = _cr.rerank_hits(suite.store, decision_text,
                                 [{"id": p["source"], "score": p["score"]} for p in pooled], top_n=top_n)
            by_src = {p["source"]: p for p in pooled}
            context = [{**by_src.get(r["address"], {}), "source": r["address"],
                        "rerank_score": r["rerank_score"], "cosine": r.get("cosine")}
                       for r in rr["reranked"]]
            notes.append(f"reranked {len(context)} (jina-v3)")
        except Exception as e:
            # rerank is precision, not correctness — degrade to cosine order, named
            context = sorted(pooled, key=lambda p: -p["score"])[:top_n]
            notes.append(f"rerank-degraded: {type(e).__name__}")
    else:
        context = sorted(pooled, key=lambda p: -p["score"])[:top_n]

    result = {"decision": decision_text, "context": context}

    # if the decision names an addressed subject, add its neighbour node-field (recall-under-the-unit)
    if address:
        try:
            from runtime import corpus_neighbours as _nb
            nb = _nb.neighbours(suite.store, address, space="common_knowledge", k=6)
            result["neighbours"] = nb.get("neighbours", [])
            if nb.get("note"):
                notes.append(f"neighbours: {nb['note'][:60]}")
        except Exception as e:
            notes.append(f"neighbours: {type(e).__name__}")

    # "decisions made about X resurfacing" (step-6) — prior decision-content on the same topic
    if include_prior_decisions:
        try:
            pd = prior_decisions_about(suite, decision_text, k=6)
            if pd:
                result["prior_decisions"] = pd
                notes.append(f"prior_decisions: {len(pd)}")
        except Exception as e:
            notes.append(f"prior_decisions: {type(e).__name__}")

    if notes:
        result["note"] = " · ".join(notes)
    return result


if __name__ == "__main__":
    # verify-by-use self-test: a real pending-decision-shaped query → the context bundle
    import sys, os, json
    sys.path.insert(0, "/home/tim/company"); os.chdir("/home/tim/company")
    from runtime.suite import Suite
    from runtime.registry import NodeRegistry
    from store.fs_store import FsStore
    s = Suite(FsStore(".data/store"), NodeRegistry().discover(["nodes"]), nodes_dir="nodes")
    q = "should file/content identity be addressed by path or by content hash — the union's identity decision"
    out = recall_for_decision(s, q, k_per_space=4, top_n=8)
    print(f"decision: {out['decision'][:60]}…")
    print(f"note: {out.get('note','')}")
    print(f"context ({len(out['context'])} items, the RHM's grounding):")
    for c in out["context"][:8]:
        sc = c.get("rerank_score", c.get("score"))
        print(f"  [{sc:+.3f}] ({c.get('space','?')}) {(c.get('source') or '')[:62]}")
