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
import json, os, re
from typing import List
from pydantic import BaseModel

_EXT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".data", "store", "extractions")
_STOP = {"the", "a", "an", "of", "to", "and", "or", "in", "on", "for", "is", "are", "how", "what", "which",
         "with", "by", "as", "at", "it", "its", "be", "this", "that", "from", "into", "about"}


def asset_path(name: str = "full") -> str:
    return os.path.join(_EXT_DIR, f"extractions-{name}.jsonl")


def _blob(r):
    return " ".join([r.get("about", ""), " ".join(r.get("touches", []) or []), r.get("summary", ""),
                     " ".join(r.get("claims", []) or []), " ".join(r.get("relations", []) or [])])


def topic_regex(topic_text: str):
    """Build a candidate-filter regex from a natural-language topic — the salient keywords OR'd. (The
    filter is the cheap recall-first cut over the stored extraction fields; the model never sees the
    topic-as-regex, only the resulting real claims.)"""
    words = [w for w in re.findall(r"[A-Za-z_][A-Za-z0-9_\-]{2,}", topic_text.lower()) if w not in _STOP]
    if not words:
        return re.compile(re.escape(topic_text), re.I)
    return re.compile("|".join(re.escape(w) for w in dict.fromkeys(words)), re.I)


def collect_claims(recs, topic_rx, *, max_claims=60):
    """Filter candidates by topic, collect their REAL claims (chunk-traced). Returns (cands, claims)."""
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
                claims.append({"n": len(claims), "claim": c.strip(), "chunk_id": r.get("chunk_id"),
                               "kind": r.get("kind")})
            if len(claims) >= max_claims:
                break
        if len(claims) >= max_claims:
            break
    return cands, claims


class _Clustering(BaseModel):
    themes: List[dict]   # [{theme, claim_indices}] — model groups BY INDEX, never writes claims


def determine(topic_text: str, *, asset: str = "full", store=None, max_claims: int = 60) -> dict:
    """The grounded determine: filter the extraction asset by `topic_text` → collect real claims → model
    clusters BY INDEX → reconstruct real chunk-traced claims per theme + the NO-FICTION check. Returns
    {topic, asset, n_candidates, n_claims, themes:[{theme, claims:[{claim, chunk_id, kind}]}], no_fiction}."""
    path = asset_path(asset)
    if not os.path.exists(path):
        return {"error": f"no extraction asset '{asset}' at {path} — the dragnet hasn't baked it yet. "
                "Assets: 'full' (session history), 'visual-dna' (the Visual-DNA vault)."}
    if store is None:
        from store.fs_store import FsStore
        from fabric import config as fcfg
        store = FsStore(fcfg.STORE_DIR)
    from runtime.roles import Role
    from runtime import cognition as cog

    recs = [json.loads(l) for l in open(path)]
    cands, claims = collect_claims(recs, topic_regex(topic_text), max_claims=max_claims)
    if not claims:
        return {"topic": topic_text, "asset": asset, "n_candidates": len(cands), "n_claims": 0,
                "themes": [], "no_fiction": True,
                "note": "no extractions matched the topic — honest no-match (not a fabricated theme)."}

    numbered = "\n".join(f"{c['n']}. {c['claim'][:140]}" for c in claims)
    role = Role(id="recall_determine_cluster", spec={}, prompt_template=(
        "Below are NUMBERED real claims extracted from the corpus about: " + topic_text + "\n"
        "GROUP them into 3-6 themes. For each theme give a short theme label and the LIST OF CLAIM NUMBERS "
        "that belong. DO NOT rewrite or invent claims — only reference them by their number.\n\n" + numbered +
        "\n\nReturn ONLY JSON: {\"themes\": [{\"theme\": \"label\", \"claim_indices\": [numbers]}]}"
    ), output_schema=_Clustering)
    # guard: never let the numbered block be address-classified (run_items :// trap)
    item = (" " + numbered) if re.match(r"\w+://", numbered) else numbered
    res = cog.run_items(role, [item], store, turn_id="recall-determine", max_tokens=500)
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
                real.append({"claim": valid[i]["claim"], "chunk_id": valid[i]["chunk_id"], "kind": valid[i]["kind"]})
                used.add(i)
            elif isinstance(i, int):
                bad.append(i)
        if real:
            themes_out.append({"theme": th.get("theme", ""), "claims": real})
    return {"topic": topic_text, "asset": asset, "n_candidates": len(cands), "n_claims": len(claims),
            "claims_grouped": len(used), "themes": themes_out, "no_fiction": (len(bad) == 0),
            "note": ("GROUNDED: every claim is a verbatim extraction, chunk-traced (model grouped by index, "
                     "invented nothing). The candidate-filter is the recall-first cut; rerank is the decisive "
                     "relevance gate when enacted." + (f" ⚠ {len(bad)} invalid indices dropped." if bad else ""))}
