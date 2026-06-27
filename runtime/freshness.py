"""runtime/freshness.py — keep a vector SPACE fresh against its source corpus (the auto-reindex loop).

THE GAP (recollection diagnosed 2026-06-22, harvested): the bridge's _warm_vector_cache daemon only WARMS
existing vectors — nothing AUTO-REINDEXES when source content changes. New/changed content embeds only via a
manual ops/embed_extractions.py run, and (until store.remove_vector, 2026-06-27) orphaned vectors could never
be retracted. So recall silently drifted from the source as it grew/changed.

THE LOOP (reuse-don't-parallel — every leg is an already-proven primitive):
  • store.vector_index.index_staleness(store, corpus, space) → {missing, changed, extra}  (READ-ONLY, no embed)
  • embed missing+changed via cognition.embed_corpus_to_spaces (the SAME incremental build_index the capture
    uses — content_hash diff means a re-embed touches only what changed)
  • RETRACT extra via store.remove_vector (the 2026-06-27 capability — closes the retraction half so the loop
    is COMPLETE: add-missing · re-embed-changed · drop-orphaned, not add-only)

`corpus` = [{address, text}] (the staleness shape) AND each record also carries the `text` to embed — so the
caller passes the CURRENT source corpus once and reconcile does the rest. Fail-loud honest report; never a
silent partial. The embed leg needs the embedder (:8007); the staleness + retract legs do not.
"""
from __future__ import annotations


def reconcile_space(store, space: str, corpus: list, *, emb: str | None = None,
                    embed_fn=None, dim=None, model=None, base_url=None, retract_extra: bool = True) -> dict:
    """Make `space` reflect `corpus` — embed missing/changed, retract orphaned. Returns an honest report
    {space, fresh_before, embedded, retracted, fresh_after, counts}. PURE on a fresh space (no-op + a clean
    report). `corpus` = [{address, text}, ...] (address = the bare source item; text = what to embed).

    retract_extra=True drops index entries no longer in the corpus (uses store.remove_vector). Set False to
    only ADD/UPDATE (the conservative half) when the corpus might be a partial view of the space."""
    from store import vector_index as _vx
    from runtime import cognition as _cog

    if not isinstance(corpus, list):
        raise ValueError("reconcile_space: `corpus` must be a list of {address, text}.")
    for r in corpus:
        if not isinstance(r, dict) or not r.get("address") or r.get("text") is None:
            raise ValueError(f"reconcile_space: every corpus item needs address+text — bad item {r!r}")

    before = _vx.index_staleness(store, corpus, space=space, emb=emb)
    embedded = retracted = 0
    degraded = False

    # ADD missing + RE-EMBED changed — group as embed_corpus_to_spaces records (only the stale subset, so the
    # embed cost is O(changed), not O(corpus)). projection == the space (registry-is-truth: it must be embeddable).
    stale_addrs = set(before["missing"]) | set(before["changed"])
    if stale_addrs:
        by_addr = {r["address"]: r for r in corpus}
        records = [{"source_address": a, "text": by_addr[a]["text"], "projection": space}
                   for a in stale_addrs if a in by_addr]
        if records:
            import os as _os
            from runtime.projections import ProjectionRegistry
            _pdir = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "projections")
            projs = ProjectionRegistry().discover([_pdir]).embeddable()
            kw = {"emb": emb} if emb is not None else {}
            if embed_fn is not None: kw["embed_fn"] = embed_fn
            if dim is not None: kw["dim"] = dim
            if model is not None: kw["model"] = model
            if base_url is not None: kw["base_url"] = base_url
            _res = _cog.embed_corpus_to_spaces(store, records, projs, **kw)
            # HONEST count: what was ACTUALLY embedded (the build result), NOT how many records we sent — a
            # degraded build (embedder down) writes 0, and the report must say so, never claim a phantom write.
            embedded = (_res.get("spaces", {}).get(space, {}) or {}).get("embedded", 0)
            if _res.get("degraded"):
                degraded = True

    # RETRACT orphaned index keys (the 2026-06-27 capability completes the loop). `extra` are VERBATIM index
    # keys (store.space_address(addr, space, emb) form) → remove_vector takes them directly.
    if retract_extra and before["extra"]:
        retracted = store.remove_vectors(before["extra"])

    after = _vx.index_staleness(store, corpus, space=space, emb=emb)
    return {"space": space, "fresh_before": before["fresh"], "embedded": embedded,
            "retracted": retracted, "degraded": degraded, "fresh_after": after["fresh"],
            "counts": {"before": before["counts"], "after": after["counts"]}}


def extractions_corpus(assets=("full", "visual-dna", "theorem")) -> list:
    """The CURRENT extractions source corpus as [{address, text}] — the staleness/reconcile input for the
    'extractions' space. Reuses ops.embed_extractions.build_records (the SAME source-of-truth the bake embeds
    from), so freshness compares the live index against exactly what the asset files now hold."""
    from ops import embed_extractions as _ee
    out = []
    for asset in assets:
        for r in _ee.build_records(asset):                      # [{source_address, text}, ...]
            out.append({"address": r["source_address"], "text": r["text"]})
    return out


def reconcile_extractions(store, *, emb="pplx", retract_extra=True, **kw) -> dict:
    """Convenience: reconcile the 'extractions' space against its live asset files. The high-value default
    (the main recall corpus; the space whose drift recollection diagnosed)."""
    return reconcile_space(store, "extractions", extractions_corpus(), emb=emb,
                           retract_extra=retract_extra, **kw)
