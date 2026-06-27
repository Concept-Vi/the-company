"""runtime/recall_determine.py — the GROUNDED determine over the dragnet extraction layer (engine).

The query half of #65, in the engine layer so BOTH the CLI (ops/dragnet_extract → ops/dragnet_determine)
AND the MCP face (corpus op='determine') call ONE implementation (reuse-don't-parallel).

PROVEN (2026-06-21): a free-SYNTHESIS reduce CONFABULATES; the fix is a NO-FICTION GROUNDED reduce — the
model CLUSTERS the REAL extraction claims BY INDEX (groups + theme-labels only, NEVER generates claim text)
→ every output claim is a verbatim real extraction with its chunk_id provenance; a no-fiction check verifies
every returned index is valid. Confabulation is STRUCTURALLY impossible. The candidate-FILTER reads the cheap
stored extractions (no model); only the cluster touches a model.

THE ASSET: .data/store/extractions/extractions-<name>.jsonl (the dragnet's extract-once layer — session
history = 'full', the Visual-DNA vault = 'visual-dna'). extract-once / determine-many.
"""
from __future__ import annotations
import json, os, re, urllib.request
from typing import List
from pydantic import BaseModel

_EXT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".data", "store", "extractions")
_STOP = {"the", "a", "an", "of", "to", "and", "or", "in", "on", "for", "is", "are", "how", "what", "which",
         "with", "by", "as", "at", "it", "its", "be", "this", "that", "from", "into", "about"}

# Reuse the SAME served reranker the recollection recall uses (jina-v3, CPU, :8008) — reuse-don't-parallel.
# Env-configurable (no hardcoding): the URL, the timeout, and how much of each candidate to send (the
# decisive relevance signal sits in the lead characters, mirroring session_recall's 600-char truncation).
RERANK_URL = os.environ.get("RERANK_URL", "http://127.0.0.1:8008/rerank")
RERANK_TIMEOUT = float(os.environ.get("RERANK_TIMEOUT", "30"))
RERANK_TRUNC = int(os.environ.get("DETERMINE_RERANK_TRUNC", "600"))
# The grouping model's context window. The old 4096 was an inherited assumption, NOT a real limit — chat-4b's
# ceiling is 262144 (max_model_len_ceiling). Raised the served context to 16384 (Tim 2026-06-27) by trading
# concurrent slots for length within the same VRAM, so prompt+output have real room and full claims fit
# without auto-trim. Env-configurable; should track the chat-4b config (DETERMINE_GROUP_CTX) — and ideally
# read the served max_model_len directly later (jotted) rather than re-encode a number here.
CHAT_CTX = int(os.environ.get("DETERMINE_GROUP_CTX", "16384"))


def asset_path(name: str = "full") -> str:
    return os.path.join(_EXT_DIR, f"extractions-{name}.jsonl")


def _blob(r):
    return " ".join([r.get("about", ""), " ".join(r.get("touches", []) or []), r.get("summary", ""),
                     " ".join(r.get("claims", []) or []), " ".join(r.get("relations", []) or [])])


_READ_CACHE: dict = {}


def read_extraction(source_address: str) -> dict | None:
    """Read ONE extraction record by its `extraction://<asset>/<chunk_id>` id — the asset's READ path so the
    WHOLE fabric (not just the embedding session) can read a chunk's content, not only RANK it (fork's by-use
    seam 2026-06-21: extraction:// was op='query'-able but not op='read'-able). Returns the full superset
    record (about/kind/touches/summary/entities/claims/relations + chunk_id) or None. Cached per asset."""
    if not isinstance(source_address, str) or not source_address.startswith("extraction://"):
        return None
    asset, _, cid = source_address[len("extraction://"):].partition("/")
    if not asset or not cid:
        return None
    path = asset_path(asset)
    # mtime-keyed cache: a rebake rewrites the asset jsonl, so cache on (mtime,size) and rebuild when the
    # file changes — else a long-lived Suite would serve a stale chunk after a rebake (the resolver branch
    # built on this read must never return a stale record; staleness here is a real error, not a hit).
    sig = None
    if os.path.exists(path):
        st = os.stat(path)
        sig = (st.st_mtime_ns, st.st_size)
    cached = _READ_CACHE.get(asset)
    if cached is None or cached[0] != sig:
        idx = {}
        if os.path.exists(path):
            for line in open(path):
                try:
                    r = json.loads(line)
                    idx[str(r.get("chunk_id"))] = r
                except Exception:
                    continue
        _READ_CACHE[asset] = (sig, idx)
        cached = _READ_CACHE[asset]
    return cached[1].get(str(cid))


def asset_freshness(asset: str, n_records: int, *, stale_after_days: float = 7.0) -> dict | None:
    """A cheap, PURE staleness signal for the determine() envelope (unify-exercise Q6: a DECLARED computed
    flag, never a resolver-side reindex and never auto-rebake — extract-once/query-many economics). Reports
    the asset's bake age + record count and flags a (Notice) when older than stale_after_days. The DEEP
    source-vs-asset comparison + (Gap) is OWNED by the freshness routine (routines/dragnet_freshness.py),
    not this read path — determine()/resolve_address stay side-effect-free. Returns None if the asset is
    absent."""
    import time as _t
    path = asset_path(asset)
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        return None
    age_days = (_t.time() - mtime) / 86400.0
    fr = {"baked_epoch": int(mtime), "age_days": round(age_days, 1), "n_records": n_records,
          "stale": age_days > stale_after_days}
    if fr["stale"]:
        fr["notice"] = (f"(Notice) extraction asset {asset!r} baked {fr['age_days']}d ago (> {stale_after_days}d) — "
                        f"may be stale vs newer source. Rebake via the dragnet_extract flow / --confirm door. "
                        f"The dragnet_freshness routine owns the source-vs-asset check; NO auto-rebake.")
    return fr


def topic_regex(topic_text: str):
    """Build a candidate-filter regex from a natural-language topic — the salient keywords OR'd. (The
    filter is the cheap recall-first cut over the stored extraction fields; the model never sees the
    topic-as-regex, only the resulting real claims.)"""
    words = [w for w in re.findall(r"[A-Za-z_][A-Za-z0-9_\-]{2,}", topic_text.lower()) if w not in _STOP]
    if not words:
        return re.compile(re.escape(topic_text), re.I)
    return re.compile("|".join(re.escape(w) for w in dict.fromkeys(words)), re.I)


def semantic_candidates(topic_text, recs, asset, *, suite=None, k=60):
    """SEMANTIC candidate-filter (the precision fix, proven 2026-06-21): query the embedded 'extractions'
    space for `topic_text` → the meaning-nearest extractions (NOT keyword-match, which catches homonyms).
    Maps the space hits (extraction://<asset>/<chunk_id>) back to the records by chunk_id. Returns the
    ranked candidate records, or None if the space is empty/unavailable (caller falls back to keyword)."""
    try:
        from store.fs_store import FsStore
        from fabric import config as fcfg
        from runtime.suite import Suite
        from runtime.registry import NodeRegistry
        import os as _os
        if suite is None:
            suite = Suite(FsStore(fcfg.STORE_DIR), NodeRegistry().discover([_os.path.join(fcfg.REPO_ROOT if hasattr(fcfg, "REPO_ROOT") else _os.getcwd(), "nodes")]))
        out = suite.query_corpus(topic_text, space="extractions", k=k)
        ranked = out.get("ranked", [])
        if not ranked:
            return None
        by_chunk = {}
        for r in recs:
            by_chunk[str(r.get("chunk_id"))] = r
        cands = []
        for h in ranked:
            sid = h.get("id") or ""
            cid = sid.rsplit("/", 1)[-1] if "/" in sid else None
            rec = by_chunk.get(cid)
            if rec is not None:
                cands.append(rec)
        return cands or None
    except Exception:
        return None


def rerank_candidates(topic_text, cands, *, top_n=None, floor=None):
    """The SHARP relevance gate the embedding nearest-k can't give: re-score each (topic, candidate) pair
    with the served jina-v3 reranker (reads query+candidate TOGETHER), reusing the recollection recall's
    endpoint (reuse-don't-parallel — NOT a second reranker). This is the fix for the generic-filler problem:
    nearest-by-meaning always returns SOMETHING, even for a nonsense query; the reranker scores true
    relevance, so `floor` can drop the filler (and let a meaningless query correctly come back empty).

    Returns (candidates, note). NO-SILENT-FAILURE: if the reranker is down it returns the candidates
    unchanged with a DECLARED note (never a silent skip). `floor` drops candidates scoring below it (the
    filler gate — when set, an all-filler result correctly returns []); `top_n` caps how many survive.
    Each surviving record carries `_rerank_score` so the caller can see the separation and calibrate."""
    if not cands:
        return cands, "rerank skipped (no candidates)"
    texts = [(_blob(r) or "")[:RERANK_TRUNC] for r in cands]
    try:
        body = json.dumps({"query": topic_text, "candidates": texts, "top_n": top_n or len(cands)}).encode()
        req = urllib.request.Request(RERANK_URL, data=body, headers={"Content-Type": "application/json"})
        ranking = json.loads(urllib.request.urlopen(req, timeout=RERANK_TIMEOUT).read()).get("ranking") or []
    except Exception as e:
        return cands, f"rerank UNAVAILABLE ({type(e).__name__}: {str(e)[:80]}) — embedding order kept (declared, not silent)"
    if not ranking:
        return cands, "rerank returned nothing — embedding order kept (declared)"
    out = []
    for o in ranking:
        idx = (o.get("orig_rank") or 0) - 1               # endpoint is 1-indexed (mirrors session_recall)
        if not (0 <= idx < len(cands)):
            continue
        score = o.get("rerank_score")
        if floor is not None and score is not None and score < floor:
            continue                                       # the filler gate
        r = dict(cands[idx]); r["_rerank_score"] = score
        out.append(r)
    scores = [c["_rerank_score"] for c in out if c.get("_rerank_score") is not None]
    rng = f"; score range {min(scores):.3f}..{max(scores):.3f}" if scores else ""
    return out, f"reranked (jina-v3 :8008): kept {len(out)}/{len(cands)}{rng}"


def collect_claims(recs, topic_rx, *, max_claims=60, cands=None):
    """Collect REAL claims (chunk-traced) from candidates. `cands` may be pre-filtered (semantic); else
    keyword-filter by `topic_rx`. Returns (cands, claims)."""
    if cands is None:
        cands = [r for r in recs if topic_rx.search(_blob(r))]
        cands.sort(key=lambda r: (r.get("grain") == "fine",
                                  len(r.get("claims", []) or []) + len(r.get("relations", []) or [])), reverse=True)
    claims = []
    for r in cands:
        src = (r.get("claims") or []) + (r.get("relations") or [])
        if not src and r.get("about"):
            src = [r["about"]]
        for c in src:
            if isinstance(c, str) and c.strip():
                # carry the FULL provenance, not just the chunk id: rel_path = the source file (for a
                # transcript that's the session file; for a repo it's the repo-relative path), anchor = the
                # position within it (e.g. turn-1-claude). So a returned claim traces to where it came from,
                # not merely to an opaque chunk number. (+ the rerank score, if the candidate was reranked.)
                claims.append({"n": len(claims), "claim": c.strip(), "chunk_id": r.get("chunk_id"),
                               "kind": r.get("kind"), "rel_path": r.get("rel_path"), "anchor": r.get("anchor"),
                               "date": r.get("date"), "rerank_score": r.get("_rerank_score")})
            if len(claims) >= max_claims:
                break
        if len(claims) >= max_claims:
            break
    return cands, claims


class _Clustering(BaseModel):
    themes: List[dict]   # [{theme, claim_indices}] — model groups BY INDEX, never writes claims


def determine(topic_text: str, *, asset: str = "full", store=None, suite=None, max_claims: int = 60,
              claim_trim: int | None = None, group_max_tokens: int = 4096,
              rerank: bool = True, rerank_top: int | None = None, rerank_floor: float | None = None) -> dict:
    """The grounded determine: filter the extraction asset by `topic_text` → (rerank) → collect real claims →
    model clusters BY INDEX → reconstruct real provenance-traced claims per theme + the NO-FICTION check.

    De-hardcoded knobs (were fixed 140/500 literals; now parameters, defaulted OFF per Tim 2026-06-27):
      claim_trim — chars each claim is trimmed to when shown to the grouping model. None (default) = NO trim
        (full claim text → better grouping; the old fixed 140 mis-grouped long/prefix-similar claims). The
        RETURNED claim text was always full regardless; this only affects what the grouping model sees.
      group_max_tokens — cap on the grouping model's output. The grouping model's context was raised to
        16384 (was a falsely-assumed 4096), so this is now generous (4096) — far more than the tiny grouping
        output (labels + index lists) ever needs, while leaving ~12k of context for the prompt. Still an int
        because prompt+output must fit the window; lift further only if the served context is raised again.
      rerank / rerank_top / rerank_floor — the jina-v3 relevance gate over the embedding candidates (the
        filler fix). rerank on by default; floor None = reorder only (set a floor to drop filler / let a
        nonsense query return empty — calibrate from the surfaced score range).

    Returns {topic, asset, filter, n_candidates, n_claims, themes:[{theme, claims:[{claim, chunk_id, kind,
    rel_path, anchor, rerank_score}]}], no_fiction, rerank, freshness, note}."""
    path = asset_path(asset)
    if not os.path.exists(path):
        return {"error": f"no extraction asset '{asset}' at {path} — the dragnet hasn't baked it yet. "
                "Assets: 'full' (session history), 'visual-dna' (the Visual-DNA vault)."}
    if store is None:
        store = getattr(suite, "store", None)            # prefer the warm suite's store (no cold rebuild)
    if store is None:
        from store.fs_store import FsStore
        from fabric import config as fcfg
        store = FsStore(fcfg.STORE_DIR)
    from runtime.roles import Role
    from runtime import cognition as cog

    recs = [json.loads(l) for l in open(path)]
    # SEMANTIC candidate-filter first (precision — concept-match over the embedded 'extractions' space);
    # fall back to keyword if the space isn't populated yet (the embed-extraction-layer may be mid-bake).
    # reuse a WARM suite when the caller passes one (the bridge's resident suite) — else semantic_candidates
    # cold-constructs (NodeRegistry.discover + warm_vector_cache over 44k vectors) PER CALL = the >60s HTTP
    # timeout fork+I hit on the /api/transcript-search determine route. store→suite if only store given.
    sem = semantic_candidates(topic_text, recs, asset, suite=suite, k=max_claims)
    _filter = "semantic" if sem is not None else "keyword"
    rerank_note = None
    if sem and rerank:                                    # the relevance gate over the embedding candidates
        sem, rerank_note = rerank_candidates(topic_text, sem, top_n=rerank_top, floor=rerank_floor)
        _filter = "semantic+rerank"
    cands, claims = collect_claims(recs, topic_regex(topic_text), max_claims=max_claims, cands=sem)
    if not claims:
        return {"topic": topic_text, "asset": asset, "filter": _filter, "n_candidates": len(cands), "n_claims": 0,
                "themes": [], "no_fiction": True, "rerank": rerank_note, "freshness": asset_freshness(asset, len(recs)),
                "note": ("no extractions matched the topic — honest no-match (not a fabricated theme)."
                         + (" [rerank floor filtered all candidates — correct empty for an off-topic query]"
                            if (rerank_note and "kept 0/" in rerank_note) else ""))}

    # claim_trim defaults OFF (full claim text → best grouping; the RETURNED claim text is full either way).
    # Fit-to-context guard: chat-4b's window is only ~CHAT_CTX tokens, so a fully-untrimmed 60-claim prompt
    # can overflow it (the request then fails — that's behavioural, not arbitrary). If trim is off and the
    # prompt would exceed the room left after the output cap, auto-trim each claim to fit and DECLARE it
    # (no silent overflow, no silent failure). A bigger-context grouping model would let claims stay full.
    def _numbered(trim):
        return "\n".join(f"{c['n']}. {c['claim'][:trim] if trim else c['claim']}" for c in claims)
    numbered = _numbered(claim_trim)
    _oversize = ""
    budget_chars = max(2000, (CHAT_CTX - group_max_tokens - 256) * 4)   # ~4 chars/token; leave output + overhead
    if claim_trim is None and len(numbered) > budget_chars:
        auto = max(60, budget_chars // max(1, len(claims)))
        numbered = _numbered(auto)
        _oversize = (f" [Notice: claim_trim off, but the {len(claims)} full claims exceeded chat-4b's "
                     f"~{CHAT_CTX}-tok context; auto-trimmed to ~{auto} chars/claim to fit — use a bigger-"
                     f"context grouping model to keep them full]")
    role = Role(id="recall_determine_cluster", spec={}, prompt_template=(
        "Below are NUMBERED real claims extracted from the corpus about: " + topic_text + "\n"
        "GROUP them into 3-6 themes. For each theme give a short theme label and the LIST OF CLAIM NUMBERS "
        "that belong. DO NOT rewrite or invent claims — only reference them by their number.\n\n" + numbered +
        "\n\nReturn ONLY JSON: {\"themes\": [{\"theme\": \"label\", \"claim_indices\": [numbers]}]}"
    ), output_schema=_Clustering)
    # guard: never let the numbered block be address-classified (run_items :// trap)
    item = (" " + numbered) if re.match(r"\w+://", numbered) else numbered
    res = cog.run_items(role, [item], store, turn_id="recall-determine", max_tokens=group_max_tokens)
    out = list(res.resolved.values())
    if not out:
        return {"topic": topic_text, "asset": asset, "n_claims": len(claims),
                "error": "cluster step returned nothing (model/transport)."}
    clustering = out[0] if isinstance(out[0], dict) else out[0].dict()

    valid = {c["n"]: c for c in claims}
    themes_out, used, bad = [], set(), []
    for th in clustering.get("themes", []):
        real = []
        for i in (th.get("claim_indices") or []):
            if isinstance(i, int) and i in valid:
                real.append({"claim": valid[i]["claim"], "chunk_id": valid[i]["chunk_id"], "kind": valid[i]["kind"],
                             "rel_path": valid[i].get("rel_path"), "anchor": valid[i].get("anchor"),
                             "date": valid[i].get("date"), "rerank_score": valid[i].get("rerank_score")})
                used.add(i)
            elif isinstance(i, int):
                bad.append(i)
        if real:
            themes_out.append({"theme": th.get("theme", ""), "claims": real})
    return {"topic": topic_text, "asset": asset, "filter": _filter, "n_candidates": len(cands), "n_claims": len(claims),
            "claims_grouped": len(used), "themes": themes_out, "no_fiction": (len(bad) == 0),
            "rerank": rerank_note, "freshness": asset_freshness(asset, len(recs)),
            "note": (f"GROUNDED ({_filter}): every claim is a verbatim extraction, traced to its source (rel_path + anchor) "
                     "and grouped by index (invented nothing). Embedding finds candidates; the jina-v3 reranker is the "
                     "relevance gate over them." + (f" ⚠ {len(bad)} invalid indices dropped." if bad else "") + _oversize)}
