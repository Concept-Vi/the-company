#!/usr/bin/env python3
"""ops/dragnet_determine.py — the GROUNDED determine over the dragnet extraction layer (the trusted tool).

The determine half of #65: query the extract-once asset for a topic. PROVEN finding (2026-06-21, default-to-
wrong on the first determine): a free-SYNTHESIS reduce CONFABULATES — it smooths scattered extractions into a
coherent-sounding "design" with invented specifics. The CANDIDATE-FILTER (reads the real cheap extractions) is
reliable; the free reduce is not.

THE FIX (lead-endorsed, 4c57c01): a NO-FICTION GROUNDED reduce. The model CLUSTERS the REAL extraction claims
BY INDEX (it selects + groups + theme-labels; it NEVER generates claim text) → every output claim is a verbatim
real extraction claim with its chunk_id provenance. Confabulation is STRUCTURALLY impossible (the model can't
invent claim text, only group existing-by-number). A no-fiction check verifies every returned index is valid.

So: determine = candidate-filter (reliable) → claim-collect (real, chunk-traced) → GROUNDED cluster (model
groups by index, theme-labels only) → output = themes of REAL claims + provenance. Map-to-source, grounded.
"""
from __future__ import annotations
import argparse, json, os, re, sys, time
from typing import List
from pydantic import BaseModel

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
OUT_DIR = os.path.join(REPO, ".data", "store", "extractions")


def _blob(r):
    return " ".join([r.get("about", ""), " ".join(r.get("touches", []) or []), r.get("summary", ""),
                     " ".join(r.get("claims", []) or []), " ".join(r.get("relations", []) or [])])


def collect_claims(recs, topic_rx, *, max_claims=60):
    """Filter candidates by topic, collect their REAL claims (chunk-traced). Each claim = a verbatim
    extraction claim (or the `about` if a candidate has no claims). Returns [{n, claim, chunk_id, kind}]."""
    cands = [r for r in recs if topic_rx.search(_blob(r))]
    cands.sort(key=lambda r: (r.get("grain") == "fine", len(r.get("claims", []) or []) + len(r.get("relations", []) or [])),
               reverse=True)
    claims = []
    for r in cands:
        src = (r.get("claims") or []) + (r.get("relations") or [])
        if not src and r.get("about"):
            src = [r["about"]]
        for c in src:
            if isinstance(c, str) and c.strip():
                claims.append({"n": len(claims), "claim": c.strip(), "chunk_id": r.get("chunk_id"),
                               "kind": r.get("kind"), "about": r.get("about", "")[:60]})
            if len(claims) >= max_claims:
                break
        if len(claims) >= max_claims:
            break
    return cands, claims


class Clustering(BaseModel):
    themes: List[dict]   # [{theme: str, claim_indices: [int]}] — the model groups by INDEX, never writes claims


def grounded_determine(asset_path, topic_rx, topic_label, *, store=None, max_claims=60):
    """The grounded determine: filter → collect real claims → model clusters BY INDEX → reconstruct real
    claims per theme + the NO-FICTION check (every returned index is a valid candidate). Returns the result
    dict + a no_fiction bool."""
    from runtime.roles import Role
    from runtime import cognition as cog
    if store is None:
        from store.fs_store import FsStore
        from fabric import config as fcfg
        store = FsStore(fcfg.STORE_DIR)
    recs = [json.loads(l) for l in open(asset_path)]
    cands, claims = collect_claims(recs, topic_rx, max_claims=max_claims)
    if not claims:
        return {"topic": topic_label, "themes": [], "n_candidates": len(cands), "n_claims": 0}, True

    numbered = "\n".join(f"{c['n']}. {c['claim'][:140]}" for c in claims)
    role = Role(id="grounded_cluster", spec={}, prompt_template=(
        "Below are NUMBERED real claims extracted from the corpus about: " + topic_label + "\n"
        "GROUP them into 3-6 themes. For each theme give a short theme label and the LIST OF CLAIM NUMBERS that "
        "belong to it. DO NOT rewrite or invent claims — only reference them by their number.\n\n" + numbered +
        "\n\nReturn ONLY JSON: {\"themes\": [{\"theme\": \"label\", \"claim_indices\": [numbers]}]}"
    ), output_schema=Clustering)
    res = cog.run_items(role, [" " + numbered if re.match(r"\w+://", numbered) else numbered], store,
                        turn_id="grounded-determine", max_tokens=500)
    out = list(res.resolved.values())
    if not out:
        return {"topic": topic_label, "error": "cluster role returned nothing", "n_claims": len(claims)}, True
    clustering = out[0] if isinstance(out[0], dict) else out[0].dict()

    # RECONSTRUCT real claims per theme + NO-FICTION CHECK (every index valid → no invented claim)
    valid = {c["n"]: c for c in claims}
    themes_out, all_idx, bad_idx = [], set(), []
    for th in clustering.get("themes", []):
        idxs = [i for i in (th.get("claim_indices") or []) if isinstance(i, int)]
        real = []
        for i in idxs:
            if i in valid:
                real.append({"claim": valid[i]["claim"], "chunk_id": valid[i]["chunk_id"], "kind": valid[i]["kind"]})
                all_idx.add(i)
            else:
                bad_idx.append(i)
        if real:
            themes_out.append({"theme": th.get("theme", ""), "claims": real})
    no_fiction = (len(bad_idx) == 0)   # the model invented no index → every output claim is a real extraction
    return {"topic": topic_label, "n_candidates": len(cands), "n_claims": len(claims),
            "themes": themes_out, "claims_grouped": len(all_idx),
            "no_fiction": no_fiction, "invalid_indices": bad_idx[:10]}, no_fiction


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--asset", default=os.path.join(OUT_DIR, "extractions-full.jsonl"))
    ap.add_argument("--topic", required=True, help="topic label")
    ap.add_argument("--rx", required=True, help="regex to filter candidate extractions")
    ap.add_argument("--max-claims", type=int, default=60)
    a = ap.parse_args()
    t = time.time()
    result, nf = grounded_determine(a.asset, re.compile(a.rx, re.I), a.topic, max_claims=a.max_claims)
    print(json.dumps(result, indent=2)[:2500])
    print(f"\nNO-FICTION: {nf} (every output claim is a verbatim real extraction — model only grouped by index) | {time.time()-t:.1f}s")
