#!/usr/bin/env python3
"""transcript_search.py — INTERIM semantic search over the Claude-session
transcript corpus, embedded by the local pplx-embed-context-v1-4b service.

THROWAWAY INTERIM (Tim is building a real memory system elsewhere). Kept lean:
one file, no framework, numpy + JSONL on disk. But it WORKS and is verified by use.

WIRING (registry-is-truth):
  Embeddings come from the Company service `embed-pplx` (ops/services.json),
  an OpenAI-compatible endpoint at http://127.0.0.1:8007/v1/embeddings.
  Start it first:  company up embed-pplx
  The model emits INT8, UNNORMALIZED 2560-d vectors → we compare via COSINE
  (L2-normalize then dot), exactly as the model card requires.

CORPUS:
  ~/corpora/claude-sessions/**/*.md  — session transcripts with YAML frontmatter
  (session_id, project, title, turns) and `## Turn N — Speaker` sections.
  Written by ops/agent_sessions_exporter.py (the agent-sessions-exporter job).

USAGE:
  python transcript_search.py index             # build/refresh the index
  python transcript_search.py search "query"    # top-K semantic hits
  python transcript_search.py search "query" -k 8

FAIL LOUD: if the endpoint is down, or returns the wrong dim, it raises — no
silent fallback, no fake results (repo law).
"""
import argparse
import glob
import json
import os
import sys
import time
import urllib.request

import numpy as np

CORPUS = os.path.expanduser("~/corpora/claude-sessions")
INDEX_DIR = os.path.expanduser("~/.cache/company/transcript-search")
VEC_PATH = os.path.join(INDEX_DIR, "vectors.npy")
META_PATH = os.path.join(INDEX_DIR, "meta.jsonl")
ENDPOINT = os.environ.get("PPLX_EMBED_URL", "http://127.0.0.1:8007/v1/embeddings")
HEALTH = ENDPOINT.replace("/v1/embeddings", "/health")
EXPECT_DIM = 2560
MAX_CHARS = 4000  # per chunk; transcripts are short, this bounds the long ones


# ---------- embedding client (fail loud) ----------

def _check_up():
    try:
        with urllib.request.urlopen(HEALTH, timeout=5) as r:
            h = json.loads(r.read())
    except Exception as e:
        sys.exit(f"FAIL: pplx embedder not reachable at {HEALTH} ({type(e).__name__}: {e}).\n"
                 f"      Start it:  company up embed-pplx")
    if h.get("status") != "ok":
        sys.exit(f"FAIL: embedder at {HEALTH} not ready: {h}")


def embed(texts, batch=16):
    """POST texts to /v1/embeddings; return float32 array (n, EXPECT_DIM).
    Raises (no silent fallback) on transport/shape errors."""
    out = []
    for i in range(0, len(texts), batch):
        chunk = texts[i:i + batch]
        body = json.dumps({"input": chunk, "quantization": "int8"}).encode()
        req = urllib.request.Request(ENDPOINT, data=body,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                resp = json.loads(r.read())
        except Exception as e:
            raise RuntimeError(f"embed POST failed at batch {i}: {type(e).__name__}: {e}")
        rows = [d["embedding"] for d in sorted(resp["data"], key=lambda d: d["index"])]
        arr = np.asarray(rows, dtype=np.float32)
        if arr.shape[1] != EXPECT_DIM:
            raise RuntimeError(f"unexpected embedding dim {arr.shape[1]} (expected {EXPECT_DIM})")
        out.append(arr)
        print(f"  embedded {min(i+batch, len(texts))}/{len(texts)}", flush=True)
    return np.vstack(out)


def l2norm(a):
    n = np.linalg.norm(a, axis=-1, keepdims=True)
    n[n == 0] = 1.0
    return a / n


# ---------- corpus chunking ----------

def parse_transcript(path):
    """Yield (chunk_text, meta) for one transcript file. One chunk per turn-block,
    prefixed with the title for context. Frontmatter is parsed for metadata."""
    text = open(path, encoding="utf-8", errors="replace").read()
    fm = {}
    body = text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip().strip('"')
            body = text[end + 4:]
    title = fm.get("title", os.path.basename(path))
    project = fm.get("project", "")
    sid = fm.get("session_id", os.path.basename(path).replace(".md", ""))
    # split into turn blocks
    blocks, cur = [], []
    for line in body.splitlines():
        if line.startswith("## Turn ") and cur:
            blocks.append("\n".join(cur)); cur = [line]
        else:
            cur.append(line)
    if cur:
        blocks.append("\n".join(cur))
    if not blocks:
        blocks = [body]
    for bi, blk in enumerate(blocks):
        blk = blk.strip()
        if not blk:
            continue
        chunk = f"{title}\n\n{blk}"[:MAX_CHARS]
        yield chunk, {"path": path, "session_id": sid, "project": project,
                      "title": title, "block": bi}


# ---------- commands ----------

def cmd_index(_):
    _check_up()
    os.makedirs(INDEX_DIR, exist_ok=True)
    files = sorted(glob.glob(os.path.join(CORPUS, "**", "*.md"), recursive=True))
    if not files:
        sys.exit(f"FAIL: no transcripts under {CORPUS}")
    print(f"indexing {len(files)} transcript files from {CORPUS}", flush=True)
    texts, metas = [], []
    for f in files:
        for chunk, meta in parse_transcript(f):
            texts.append(chunk); metas.append(meta)
    print(f"{len(texts)} chunks → embedding via {ENDPOINT}", flush=True)
    t0 = time.time()
    vecs = embed(texts)
    vecs = l2norm(vecs).astype(np.float32)  # store normalized for cosine = dot
    np.save(VEC_PATH, vecs)
    with open(META_PATH, "w", encoding="utf-8") as fh:
        for m in metas:
            fh.write(json.dumps(m) + "\n")
    print(f"INDEXED {len(texts)} chunks in {time.time()-t0:.1f}s → {VEC_PATH}", flush=True)


def cmd_search(args):
    if not os.path.exists(VEC_PATH):
        sys.exit(f"FAIL: no index at {VEC_PATH}. Run: python transcript_search.py index")
    _check_up()
    vecs = np.load(VEC_PATH)
    metas = [json.loads(l) for l in open(META_PATH, encoding="utf-8")]
    q = l2norm(embed([args.query]))[0]
    sims = vecs @ q  # cosine (both normalized)
    top = np.argsort(-sims)[:args.k]
    print(f"\nTop {args.k} for: {args.query!r}\n" + "=" * 60)
    for rank, idx in enumerate(top, 1):
        m = metas[idx]
        snip = open(m["path"], encoding="utf-8", errors="replace").read()
        # pull a short snippet near the matched block
        print(f"\n#{rank}  cos={sims[idx]:.3f}  [{m['project']}]")
        print(f"     {m['title']}")
        print(f"     {m['path']}  (block {m['block']})")
    print()


def main():
    ap = argparse.ArgumentParser(description="interim transcript semantic search (pplx-embed)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("index").set_defaults(func=cmd_index)
    sp = sub.add_parser("search"); sp.add_argument("query"); sp.add_argument("-k", type=int, default=5)
    sp.set_defaults(func=cmd_search)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
