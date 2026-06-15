"""store/vector_index.py — X12 · the PERSISTED VECTOR INDEX build + query path (Convergence).

WHAT THIS IS (Convergence X12; Research Synthesis Round 5 — STATE.md:47 "the next rung": embed-based
retrieval against a LIVE index; no index existed before). Embedding was on-the-fly and the repo
outgrew whole-repo context-stuffing (the `codebase` node fail-louds at 600k; the repo is 865k). X12
persists the index so retrieval reads it instead of recomputing.

  - the SUBSTRATE is the addressed store's NEW `vectors/` namespace (a SIBLING of objects/refs under
    the ONE store root — `store/fs_store.py` put_vector/get_vector/index_addresses/index_corpus). ONE
    substrate, keyed by the SAME `code://`/`ui://` addresses, NOT a parallel store, NO new DB, ext4.
  - THIS module is the ORCHESTRATION on top of it: the BUILD/REFRESH path (embed the corpus → persist
    {address: vector, content_hash}) and the QUERY path (rank by cosine). It is the ONLY layer here
    that touches the model fabric — fs_store.py stays fabric-free (store constitution: the store turns
    an address into bytes and back; it never calls a model).

GRANULARITY (stated): ONE index entry per ADDRESSED ITEM — the corpus unit is that item's TEXT. The
build path is corpus-AGNOSTIC: it takes `[{address, text}, ...]`. In PRODUCTION that corpus is fed by
X11's `design/_system/symbols.py` representative_text() over the code-symbols (code:// addresses) +
the `ui://` element addresses — so X12 is the DISTINCT persisted `{address:vector}` store, NOT a
parallel of X11's in-corpus `semantically_nearest[]` edges (X11 ranks symbols WITHIN the design
corpus; X12 is the queryable persisted index X13/consult read from). The granularity stays open: a
caller may pre-CHUNK a large item into several addressed units before passing them in.

REUSE, NO PARALLEL SYSTEM:
  - EMBED via the EXACT fabric path nodes/embed.py uses: `fabric.transport.openai_embeddings_transport`
    + `fabric.client.complete_embeddings` (the vector-guarded sibling of complete(); dim= enforces the
    dim contract — a wrong-length vector FAILS LOUD at the fabric, never a silent bad cosine). NO new
    embedding transport.
  - RANK via the EXISTING `nodes/retrieve` node (`retrieve.run` — the cosine is NOT reimplemented; its
    _cosine raises ValueError on a dim mismatch → the query dim guard is fail-loud by reuse).

CONTENT-HASH INCREMENTAL: each entry stores the blake2b hash of its text. A re-build re-embeds an
address ONLY when its content_hash CHANGED (or it is new). An all-UNCHANGED rebuild embeds NOTHING and
hits the endpoint ZERO times — so it emits NO degrade warning (a spurious 'embedder down' on an
unchanged rebuild would be a false fail-loud; mirrors suite.py's silent empty-intent case).

DEGRADE-WITH-WARNING (HARD CONSTRAINT — :8001 is DOWN right now): when the embed call RAISES (endpoint
unreachable), the build emits a LOUD warning (a durable `warning` event on the ONE event log — the
detectable channel conv_semantic_rank asserts; this module is not the Suite, it has no self._emit),
writes NO fabricated vectors (the index stays empty/partial HONESTLY), and does NOT crash. NEVER a
silent zero-vector, NEVER a fabricated nearest, NEVER a wrong cosine, NEVER a fallback to the chat
endpoint. LIVE population is the :8001-up follow-up. A QUERY over an empty index returns empty + an
HONEST note so the caller (X13/consult, which already falls back) can distinguish 'index empty
(embedder was down at build)' from 'populated, no match'.
"""
from __future__ import annotations
import hashlib


def content_hash(text: str) -> str:
    """The stable hash of an addressed item's text — the incremental key. blake2b mirrors the store's
    own cas hashing (fs_store._hash), so the hashing discipline is consistent across the substrate."""
    return "b2:" + hashlib.blake2b((text or "").encode("utf-8"), digest_size=16).hexdigest()


def _default_embed(transport, inputs, model, dim=None):
    """The real fabric embed call — the EXACT path nodes/embed.py uses. Separated so a test can inject a
    deterministic stub (the hermetic seam X11/conv_semantic_rank use) without a live model. Raises on
    endpoint-down (FabricError / URLError) — the BUILD treats that raise as the degrade signal."""
    from fabric import client
    return client.complete_embeddings(transport, inputs, model=model, dim=dim)


def build_index(store, corpus, *, embed_fn=_default_embed, dim=None, model=None, base_url=None,
                space=None, emb=None) -> dict:
    """BUILD/REFRESH the persisted vector index over `corpus` = `[{address, text}, ...]`.

    INCREMENTAL: an address is (re-)embedded ONLY when NEW or its content_hash CHANGED — unchanged items
    are SKIPPED (no re-embed). The changed batch is embedded in ONE round-trip (the per-build embed cost
    is O(changed)). On success each changed {address: vector, content_hash} is persisted via
    store.put_vector (atomic, crash-durable). dim= is passed through to complete_embeddings so a
    wrong-length vector FAILS LOUD at the fabric (rule 4) — never a silent bad cosine.

    SPACE-KEYED (cognition-engine GROUP L · additive — every prior caller is unchanged): `space=None` (the
    default) builds the DEFAULT/unspaced index exactly as before (keyed by the bare item address). A named
    `space="<projection>"` builds that PROJECTION space — the SAME item embedded at a different lens — keyed
    by the composed C1 address `vec://<item>#space=<projection>` (store.space_address), carrying the explicit
    `space`/`source` fields so a per-space query (query_index(space=...)) ranks WITHIN one space and returns
    the SOURCE item. Each space's incremental diff keys on its OWN composed address (so the same item in
    space A and space B are independent entries — changing one never false-skips the other).

    DEGRADE-WITH-WARNING: if the embed call RAISES (the embedder :8001 is unreachable — its state RIGHT
    NOW), NO vectors are written (the index stays empty/partial honestly), a LOUD durable `warning` event
    is emitted, and the build returns {"degraded": True, ...} WITHOUT crashing. An all-unchanged rebuild
    (nothing to embed) does NOT touch the endpoint and does NOT warn.

    Returns {"embedded": N, "skipped": M, "degraded": bool}.
    """
    from fabric import transport, config as fcfg
    model = model or fcfg.DEFAULT_EMBED_MODEL
    base_url = base_url or fcfg.DEFAULT_EMBED_URL
    dim = fcfg.DEFAULT_EMBED_DIM if dim is None else dim

    # 1) content-hash diff — which addresses are NEW or CHANGED (re-embed) vs UNCHANGED (skip).
    #    The KEY is the SPACE-composed address (store.space_address): for the default space this is the bare
    #    item address (back-compat); for a named space it is `vec://<item>#space=<proj>`. Keying the diff on
    #    the composed address is what makes the same item INDEPENDENT across spaces — comparing against the
    #    bare entry's content_hash (the bug the advisor flagged) would false-skip a space's first embed.
    to_embed, skipped = [], 0
    for item in corpus:
        source = item["address"]
        key = store.space_address(source, space, emb)      # bare addr (default) | vec://<item>#space=<proj>[#emb=<layer>]
        h = content_hash(item.get("text", ""))
        prior = store.get_vector(key)
        if prior is not None and prior.get("content_hash") == h:
            skipped += 1                                   # UNCHANGED — do NOT re-embed (incremental)
            continue
        to_embed.append((source, key, item.get("text", ""), h))

    # 2) NO-OP rebuild → no endpoint round-trip, no warning (a spurious 'embedder down' here would be a
    #    false fail-loud; mirror suite.py's silent empty case).
    if not to_embed:
        return {"embedded": 0, "skipped": skipped, "degraded": False}

    # 3) embed the changed batch in ONE round-trip via the EXISTING fabric path (NO new transport)
    texts = [t for (_s, _k, t, _h) in to_embed]
    try:
        t = transport.openai_embeddings_transport(base_url=base_url)
        vectors = embed_fn(t, texts, model=model, dim=dim)
    except Exception as e:
        # DEGRADE-WITH-WARNING (:8001 down): write NOTHING, warn LOUDLY (durable event — the detectable
        # channel, since this module is not the Suite), do NOT crash. NEVER a fabricated/zero vector.
        try:
            store.append_event({
                "kind": "warning",
                "summary": (f"X12: embed endpoint unreachable building the vector index "
                            f"({type(e).__name__}: {e}) — NO vectors written ({len(to_embed)} pending); "
                            "the index stays empty/partial honestly. Live population is the :8001-up follow-up."),
            })
        except Exception:
            pass                                           # the warning is best-effort; the degrade still holds
        return {"embedded": 0, "skipped": skipped, "degraded": True}

    # 4) persist — atomic, crash-durable, keyed by the SPACE-composed ADDRESS (one substrate). The space +
    #    source ride as explicit fields (the portable per-space filter key — see fs_store.put_vector). dim
    #    already enforced by the fabric. For the default space, key == source == the bare address (back-compat).
    for (source, key, _txt, h), vec in zip(to_embed, vectors):
        store.put_vector(key, vec, h, dim=dim, model=model, space=space, source=source, emb=emb)
    return {"embedded": len(to_embed), "skipped": skipped, "degraded": False}


def query_index(store, query_vector, *, k=5, with_note=False, space=None):
    """QUERY the persisted index: given a query VECTOR, return the top-K nearest ADDRESSES, REUSING the
    existing `nodes/retrieve` node (the cosine is NOT reimplemented; its _cosine raises ValueError on a
    dim mismatch → the query dim guard is FAIL-LOUD by reuse — never a wrong-but-plausible cosine).

    SPACE filter (cognition-engine GROUP L · L2 · additive — default unchanged): `space=None` (the default)
    ranks the DEFAULT/unspaced index EXACTLY as before — a spaced entry NEVER leaks in (so no polluted
    ranking, and no cross-dim cosine crash from two projections sharing the corpus; this is the regression
    the live callers — consult/R2 — depend on). `space="<projection>"` restricts the k-NN to that ONE
    projection space and returns the SOURCE items (k-NN WITHIN a space: nearest in principle-space ≠ in
    topic-space — the same item is cross-space distinguishable by its different neighbours). The dim guard
    still bites per-space (a query-dim mismatch raises). `space=FsStore.ALL_SPACES` ranks every entry.

    EMPTY index (the embedder was DOWN at build → nothing persisted, OR no entry in the named space):
    retrieve naturally returns [] over an empty corpus; with_note=True wraps it as {"ranked": [], "note":
    "..."} so the caller (X13/consult, which already falls back) can distinguish 'index empty' from
    'populated, no match'. with_note=False returns the bare ranked list (the nodes/retrieve shape:
    [{id: address, score}, ...]).
    """
    from nodes import retrieve                              # the existing cosine-ranking node — reused, not reimplemented
    corpus = store.index_corpus(space=space)                # [{id: <item>, vector}], the exact shape retrieve consumes
    ranked = retrieve.run({"query": query_vector, "corpus": corpus}, {"k": k})
    if not with_note:
        return ranked
    _scope = "default space" if space is None else (f"space '{space}'" if space is not store.ALL_SPACES else "all spaces")
    if not corpus:
        return {"ranked": [], "note": (f"the vector index is EMPTY ({_scope}) — it may have been built "
                                       "while the embedder :8001 was down, or no item is embedded in this "
                                       "space; no addresses to rank, the caller should fall back "
                                       "(e.g. keyword/consult). Live population is the :8001-up follow-up.")}
    return {"ranked": ranked, "note": f"ranked {len(ranked)} of {len(corpus)} indexed addresses by cosine ({_scope})"}


def index_staleness(store, corpus, *, model=None, space=None) -> dict:
    """READ-ONLY staleness check: does the persisted vector index still reflect `corpus`, WITHOUT a
    rebuild? A SIBLING of build_index/query_index — but it embeds NOTHING, touches NO network, never
    calls the :8001 embedder. It only compares content_hashes, so the caller (query_index / consult /
    R2 semantic ranking) can ASK 'is the index stale?' before trusting a ranking, instead of silently
    retrieving over a stale index as the corpus grows (STATE.md:47 — the gap the embedder-regen
    follow-up names: incremental build had no way to be INTERROGATED for staleness).

    `corpus` = `[{address, text}, ...]` — the SAME shape build_index consumes. Each item's content_hash
    is recomputed via the EXISTING content_hash() in this module (NOT reimplemented — same blake2b key
    the build path persisted), and compared against the persisted index. The persisted side is read by
    ADDRESS: store.index_addresses() enumerates every indexed address, store.get_vector(address) carries
    the stored content_hash (index_corpus() returns only {id, vector} — no hash — so it is NOT the read
    path here; the hash lives on the per-address record). `model=` is accepted for signature symmetry
    with build_index/query_index but does NOT enter the comparison — staleness is content_hash-only.

    SPACE (additive — default unchanged): `space=None` (the default) interrogates the DEFAULT/unspaced
    index, BYTE-IDENTICAL to before (store.space_address(a, None)==a, store.index_addresses(None)=the bare
    default set). `space="<proj>"` interrogates ONE projection space (Group L: topics/principles/worldview/
    repo/…): a corpus item's address `a` is mapped to its PERSISTED key store.space_address(a, space) (the
    `vec://<a>#space=<proj>` form build_index wrote), so a per-space freshness verdict reads the SAME keyed
    entries the capture pass persisted — never the default corpus (no cross-space leak). `missing` names the
    bare item addresses (human-readable); `extra` names the verbatim orphaned index keys.

    FAIL LOUD (rule 4): a corpus item missing `address` or `text` RAISES (KeyError-shaped ValueError
    naming the offending item) — NEVER a silent skip (build_index's tolerant item.get is the build
    path's choice; an honest staleness verdict cannot quietly drop an item it failed to read).

    Returns:
        {"fresh": bool,                      # True iff missing/changed/extra are ALL empty
         "missing": [addr, ...],             # in corpus but NOT in the index (never embedded)
         "changed": [addr, ...],             # in both, but the stored content_hash differs (re-embed due)
         "extra":   [key, ...],              # in the index but NO longer in the corpus (orphaned entry)
         "counts":  {"corpus": N, "indexed": M, "missing": .., "changed": .., "extra": ..}}
    All three lists are sorted (a stable, comparable verdict).
    """
    # 1) the corpus side — recompute each item's content_hash via the SHARED key (fail loud on a bad item)
    corpus_hashes = {}
    for item in corpus:
        if "address" not in item or "text" not in item:
            raise ValueError(f"index_staleness: malformed corpus item (needs 'address' and 'text'): {item!r}")
        corpus_hashes[item["address"]] = content_hash(item["text"])

    # 2) the persisted side — read by the SPACE-KEYED address (space=None → bare, byte-identical to before).
    #    Each corpus item address maps to the persisted key build_index wrote (store.space_address).
    indexed = set(store.index_addresses(space=space))
    keyed = {addr: store.space_address(addr, space) for addr in corpus_hashes}
    corpus_keys = set(keyed.values())

    missing = sorted(a for a, k in keyed.items() if k not in indexed)        # in corpus, never indexed
    extra = sorted(indexed - corpus_keys)                                    # indexed, no longer in corpus
    changed = sorted(a for a, k in keyed.items()
                     if k in indexed and (store.get_vector(k) or {}).get("content_hash") != corpus_hashes[a])

    fresh = not missing and not changed and not extra
    return {"fresh": fresh, "missing": missing, "changed": changed, "extra": extra,
            "counts": {"corpus": len(corpus_hashes), "indexed": len(indexed),
                       "missing": len(missing), "changed": len(changed), "extra": len(extra)}}


def index_addresses(store, space=None) -> list:
    """Convenience pass-through — every address currently in the persisted index (sorted). `space=None`
    (default) = the DEFAULT/unspaced entries (back-compat); a named space = that projection's entries;
    FsStore.ALL_SPACES = every entry."""
    return store.index_addresses(space=space)


def get_vector(store, address: str):
    """Convenience pass-through — the persisted {address, vector, content_hash, dim, model, ts} or None."""
    return store.get_vector(address)
