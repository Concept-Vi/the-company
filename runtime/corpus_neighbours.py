"""runtime/corpus_neighbours.py — the NEIGHBOUR NODE-FIELD: given a corpus unit's address, the units
AROUND it in a space, ranked by meaning (the recall-UNDER-a-unit seam the FACE drill-in stands on).

Each neighbour's `source` is itself a code:// address — directly projection:select-able — so the
field is a RELATIONAL GRAPH where every surrounding node re-drills into its own face (the constellation
a drilled unit sits in, not a flat list). Requested by DNA (2026-06-16, t-1781603317) for the gallery's
neighbour node-field; shape `{source, score}` per node confirmed with her.

MECHANISM (reuse-don't-parallel — NO cosine reimplemented, NO new transport): the unit's OWN persisted
per-space vector (store.get_vector @ space_address) → store/vector_index.query_index over that space →
drop self. This is byte-identical to how find_relations gets its `near` set (suite.py:10907,
_vx.query_index(store, near_rec['vector'], space=...)) — a single-space neighbours read, not the
near∩¬far inversion find_relations layers on top (which requires TWO anchors).

LAYER DISCIPLINE (projection, MULTI-LAYER-CONSULT.md): emb is named EXPLICITLY ('pplx'), never leaning
on a global omit-emb default (which silently mismatches on bare-only spaces). The vector and the query
are the SAME layer/dim by construction, so the dim guard never fires falsely.

FAIL-LOUD (no fabrication): a unit with no persisted vector at (address, space, emb) returns an HONEST
note + empty field — never a fabricated/zero-vector nearest. (This is the .md-units-pending case until
the lead's paths/roots key-normalization + the dedupe land — DNA renders only resolved neighbours.)

PROVEN (verify-by-use, ch-83e2cque): the EXACT unit the FACE rendered live —
code:///home/tim/company/recollection/src/distill/harness.ts → its field: index.ts 0.75 · distill.test.ts 0.68
· distill-cli.ts 0.66 · unit-types.ts 0.62 · extractor.ts 0.55 · recall-cli.ts 0.55 = the whole distill
module, semantically clustered.
"""
from __future__ import annotations


def neighbours(store, address: str, *, space: str = "common_knowledge", k: int = 8,
               emb: str = "pplx", min_score: float = 0.0, query: str | None = None,
               rerank: bool = False) -> dict:
    """The neighbour node-field for `address` in `space`. Returns
    {unit, space, emb, neighbours: [{source, score}, ...], note?}.

    `k` = how many to rank (self is dropped, so up to k-1 returned). `min_score` optionally thresholds
    out near-zero ghosts (default 0.0 = return all ranked; the caller maps score→prominence). `rerank`
    (default OFF) runs the jina-v3 precision pass over the field (reuse runtime/corpus_rerank) — pass
    `query` (e.g. the unit's own digest/title) as the rerank anchor; without it rerank is skipped with
    a note. Read-only; no resolve/approve/dispatch."""
    from store import vector_index as _vx
    key = store.space_address(address, space, emb)
    rec = store.get_vector(key)
    if not (rec and rec.get("vector")):
        # FAIL-LOUD honest empty — never a fabricated nearest. The unit isn't embedded at this
        # (space, emb): either never ingested into `space`, or the .md-key-split pending the dedupe.
        return {"unit": address, "space": space, "emb": emb, "neighbours": [],
                "note": f"no persisted vector at ({address}, space={space}, emb={emb}) — the unit is "
                        f"not embedded in this space/layer (never ingested here, or a key-spelling "
                        f"split pending normalization). No neighbours to rank (honest empty)."}

    hits = _vx.query_index(store, rec["vector"], k=k, space=space, emb=emb, with_note=True)
    ranked = hits.get("ranked", []) if isinstance(hits, dict) else hits
    field = [{"source": (h.get("address") or h.get("id")), "score": round(h.get("score", 0.0), 4)}
             for h in ranked
             if (h.get("address") or h.get("id")) != address and h.get("score", 0.0) >= min_score]

    note = (hits.get("note") if isinstance(hits, dict) else None) or ""
    if rerank and field:
        if not query:
            note = (note + " · rerank skipped: no `query` anchor supplied").strip(" ·")
        else:
            from runtime import corpus_rerank as _cr
            # reuse the proven precision stage; rerank_hits wants [{id|address, score}] shape
            rr = _cr.rerank_hits(store, query, [{"id": f["source"], "score": f["score"]} for f in field])
            field = [{"source": r["address"], "score": round(r["rerank_score"], 4),
                      "cosine": r["cosine"]} for r in rr["reranked"]]
            note = (note + f" · reranked (jina-v3, {rr['backend']})").strip(" ·")

    return {"unit": address, "space": space, "emb": emb, "neighbours": field,
            **({"note": note} if note else {})}


if __name__ == "__main__":
    # verify-by-use self-test: the proven distill/harness.ts constellation
    import sys, os, json
    sys.path.insert(0, "/home/tim/company"); os.chdir("/home/tim/company")
    from runtime.suite import Suite
    from runtime.registry import NodeRegistry
    from store.fs_store import FsStore
    s = Suite(FsStore(".data/store"), NodeRegistry().discover(["nodes"]), nodes_dir="nodes")
    out = neighbours(s.store, "code:///home/tim/company/recollection/src/distill/harness.ts",
                     space="common_knowledge", k=7)
    print(json.dumps(out, indent=2))
    # the .md-pending honest-empty case
    md = neighbours(s.store, "code:///home/tim/company/recollection/README.md", space="common_knowledge", k=5)
    print("\n.md (absolute key, pending dedupe):", md.get("note", "")[:80])
