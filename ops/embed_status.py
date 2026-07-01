#!/usr/bin/env python3
"""ops/embed_status.py — the embedding-space status/verify surface (loop criterion V1).

Reports, per vector SPACE in the FsStore, the count · dim · model · a real top-k query — using the store's
own space index (NOT a slow per-file JSON scan). The honest, navigable status of the multi-model/multi-scale
embedding layer: which spaces exist, how big, which model, and does retrieval actually work.

Run:  python ops/embed_status.py                      # per-space table
      python ops/embed_status.py --query "resolve the brain model"   # + a top-k in each queryable space
"""
from __future__ import annotations
import argparse, os, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

# space -> (embedder kind, endpoint, model, dim, emb-layer) — the known query configs (mirror build_embeddings)
QUERY_CFG = {
    "code":   ("ollama", "http://127.0.0.1:11434", "nomic-embed-code", 3584, "nomic-code"),
    "symbol": ("ollama", "http://127.0.0.1:11434", "nomic-embed-code", 3584, "nomic-code"),
    "docs":   ("fabric", "http://127.0.0.1:8007/v1", "perplexity-ai/pplx-embed-context-v1-4b", 2560, "pplx"),
    "desc":   ("fabric", "http://127.0.0.1:8007/v1", "perplexity-ai/pplx-embed-context-v1-4b", 2560, "pplx"),
}


def _store():
    from store.fs_store import FsStore
    return FsStore(os.path.join(REPO, ".data", "store"))


def _spaces(store):
    """Discover every (space, emb) present + its count, via the store's space listing (indexed, not a scan)."""
    from store import vector_index as vi
    st = getattr(store, "store", store)
    seen = {}
    # the store keys vectors by space_address; enumerate per known space + emb, and also the default.
    for space in list(QUERY_CFG) + ["extractions", "history", "repo", "topics", "code_archaeology"]:
        for emb in ("nomic-code", "pplx", "bge", None):
            try:
                addrs = vi.index_addresses(st, space=space)
            except Exception:
                addrs = []
            if addrs:
                seen[(space, emb)] = len(addrs)
                break
    return seen


def _embed_query(cfg, text):
    kind, base, model, dim, emb = cfg
    if kind == "ollama":
        import json, urllib.request
        body = json.dumps({"model": model, "input": text, "options": {"num_ctx": 32768}}).encode()
        req = urllib.request.Request(base + "/api/embed", data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())["embeddings"][0]
    from fabric import transport, client
    t = transport.openai_embeddings_transport(base_url=base)
    return client.complete_embeddings(t, [text], model=model, dim=dim)[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", default="")
    a = ap.parse_args()
    from store import vector_index as vi
    store = _store()
    st = getattr(store, "store", store)
    print(f"{'space':22} {'count':>7}  model / emb-layer")
    spaces = _spaces(store)
    for space in list(QUERY_CFG) + ["extractions", "history", "repo", "topics", "code_archaeology"]:
        cfg = QUERY_CFG.get(space)
        for emb in ("nomic-code", "pplx", "bge", None):
            try:
                n = len(vi.index_addresses(st, space=space))
            except Exception:
                n = 0
            if n:
                model = cfg[2] if cfg else "?"
                print(f"{space:22} {n:>7}  {model}")
                if a.query and cfg:
                    try:
                        qv = _embed_query(cfg, a.query)
                        hits = vi.query_index(st, qv, k=5, space=space, emb=cfg[4])
                        for h in hits[:5]:
                            print(f"    {h.get('score',0):.3f}  {h.get('id','')}")
                    except Exception as e:
                        print(f"    (query failed: {str(e)[:80]})")
                break


if __name__ == "__main__":
    raise SystemExit(main())
