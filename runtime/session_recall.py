"""runtime/session_recall.py — SEMANTIC recall over a session (the embedding INTO the scanner system).

Tim's directive (2026-06-14): "you will be building the embedding into the scanner system." This is the
meaning-search layer on top of the structural scanner — answers "what did we decide / discuss about X in
THIS session?" by embedding the session's turns and the query in the SAME space, ranking by cosine, then
reranking. It is the fix for the recall-failure that motivated it (an agent could not recall the embedding
decision on 2026-06-14 though it sat findable in the transcript).

THE SEAM (co-designed with the lead, who SERVES; this module CONSUMES — loads NO models itself):
  • chunks come from runtime/session_scan (genuine content turns, with line/ts/attribution/point handles).
  • embeddings: POST the LEAD's served embedder at :8007/v1/embeddings, model pplx-embed-context-v1-4b,
    DOCUMENTS-mode {"documents":[[turn,turn,...]]} → per-turn CONTEXTUAL (late-chunking) vectors, dim 2560,
    int8/unnormalized → compare by COSINE. Index AND query embedded by the SAME maker (the golden rule).
  • rerank: ops/rerank.py Reranker(backend="jina-v3", device="cpu") — a CPU library, 0 VRAM, no GPU contention.
This path is SELF-CONTAINED: it does not depend on the substrate_mcp.embeddings bridge (which is currently
broken — see channel-memory + the lead). Embedder down ⇒ TEACHING error ("company up embed-pplx"), never a
silent empty result, never a silent fallback (repo law).

API:  build_recall_index(jsonl, out_dir) -> {index paths, n_chunks}
      recall(jsonl, query, k=8, rerank=True, index_dir=None) -> {query, hits:[{line,ts,attr,point,score,text}]}
CLI:  python3 -m runtime.session_recall <jsonl> "<query>" [--k N] [--no-rerank] [--index-dir DIR]
"""
from __future__ import annotations

import json
import math
import os
import sys
import urllib.request

from runtime.session_scan import scan_session

EMBED_URL = os.environ.get("PPLX_EMBED_URL", "http://127.0.0.1:8007/v1/embeddings")
EMBED_MODEL = os.environ.get("PPLX_EMBED_MODEL", "perplexity-ai/pplx-embed-context-v1-4b")
EMBED_DIM = 2560
# group turns into documents that stay within the embedder's context (late-chunking happens WITHIN a group);
# conservative char budget per group so a group never overflows the 32K-token window.
GROUP_CHAR_BUDGET = int(os.environ.get("RECALL_GROUP_CHARS", "16000"))
MAX_TURNS_PER_GROUP = int(os.environ.get("RECALL_GROUP_TURNS", "32"))


class RecallError(RuntimeError):
    """Fail-loud: a recall that cannot ground (embedder down, no chunks) raises — never returns silent empty."""


# ───────────────────────────── chunking (from the scan) ─────────────────────────────

def session_chunks(jsonl_path: str) -> list[dict]:
    """Genuine content turns as recall chunks, each with its structural handle. Reuses the scanner so
    chunking and the structural scan agree on attribution/boundaries. Skips inject/tool/empty events —
    we recall over what was SAID (human + assistant + compaction summaries), not tool plumbing."""
    rows = scan_session(jsonl_path)["rows"]
    chunks = []
    for r in rows:
        if r["attr"] not in ("user", "assistant", "compaction", "channel"):
            continue
        text = _row_text(jsonl_path, r["line"]) if False else None  # text pulled in bulk below
        chunks.append({"line": r["line"], "ts": r["ts"], "attr": r["attr"],
                       "model": r.get("model"), "point": r.get("boundary_point"),
                       "is_boundary": r.get("is_boundary")})
    # pull the actual text for those lines in one pass (avoids re-reading per row)
    wanted = {c["line"] for c in chunks}
    texts = _texts_for_lines(jsonl_path, wanted)
    out = []
    for c in chunks:
        t = (texts.get(c["line"]) or "").strip()
        if not t:
            continue
        c["text"] = t
        out.append(c)
    return out


def _texts_for_lines(jsonl_path: str, wanted: set) -> dict:
    from runtime.session_scan import _iter_jsonl  # reuse the tolerant reader
    res = {}
    for i, ev in _iter_jsonl(jsonl_path):
        if i not in wanted or ev is None:
            continue
        msg = ev.get("message") if isinstance(ev.get("message"), dict) else {}
        c = msg.get("content")
        if isinstance(c, str):
            t = c
        elif isinstance(c, list):
            t = " ".join(p.get("text", "") for p in c if isinstance(p, dict) and p.get("type") == "text")
        else:
            t = ""
        # strip the harness "Message sent at…UTC" marker so it doesn't pollute the embedding
        if t.lstrip().startswith("<system-reminder>Message sent at"):
            t = t.split("</system-reminder>", 1)[-1].strip()
        res[i] = t
    return res


# ───────────────────────────── embedding (the lead's served endpoint) ─────────────────────────────

def _embed_documents(groups: list[list[str]]) -> list[list[list[float]]]:
    """POST documents-mode → per-chunk contextual vectors. groups = [[chunk,…], …]; returns parallel
    [[vec,…], …]. Fail-loud on a down embedder (teaching error)."""
    body = json.dumps({"model": EMBED_MODEL, "documents": groups}).encode()
    req = urllib.request.Request(EMBED_URL, data=body, headers={"Content-Type": "application/json"})
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=180).read())
    except Exception as e:
        raise RecallError(
            f"recall: the embedder at {EMBED_URL} is unreachable ({type(e).__name__}: {e}). The query "
            f"and the index MUST be embedded in the same space — bring the embedder up: "
            f"`company up embed-pplx` (the lead's lane; GPU). No silent fallback.") from e
    data = r.get("data") or []
    # the endpoint returns a flat data[] of {embedding, index?}; we re-split by group lengths
    flat = [d.get("embedding") if isinstance(d, dict) else d for d in data]
    out, pos = [], 0
    for g in groups:
        out.append(flat[pos:pos + len(g)])
        pos += len(g)
    return out


def _embed_chunks(texts: list[str]) -> list[list[float]]:
    """Embed many chunks, batched into context-sized documents (late-chunking within each group)."""
    groups, cur, cur_chars = [], [], 0
    for t in texts:
        if cur and (len(cur) >= MAX_TURNS_PER_GROUP or cur_chars + len(t) > GROUP_CHAR_BUDGET):
            groups.append(cur); cur, cur_chars = [], 0
        cur.append(t[:GROUP_CHAR_BUDGET]); cur_chars += len(t)
    if cur:
        groups.append(cur)
    vecs = []
    for gi in range(0, len(groups), 8):                 # cap concurrency on the endpoint
        batch = groups[gi:gi + 8]
        for gv in _embed_documents(batch):
            vecs.extend(gv)
    return vecs


def _embed_one(q: str) -> list[float]:
    return _embed_documents([[q]])[0][0]


# ───────────────────────────── similarity + index ─────────────────────────────

def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def build_recall_index(jsonl_path: str, out_dir: str | None = None) -> dict:
    """Chunk + embed a session; persist vectors + chunk metadata so re-recall is fast (build once, query many)."""
    chunks = session_chunks(jsonl_path)
    if not chunks:
        raise RecallError(f"recall: no content turns to index in {jsonl_path} (only plumbing/empty events).")
    vecs = _embed_chunks([c["text"] for c in chunks])
    if len(vecs) != len(chunks):
        raise RecallError(f"recall: embedder returned {len(vecs)} vectors for {len(chunks)} chunks — "
                          f"index/embedding mismatch; refusing to build a misaligned index.")
    out_dir = out_dir or os.path.dirname(os.path.abspath(jsonl_path))
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(jsonl_path))[0]
    vpath = os.path.join(out_dir, f"{stem}.recall.jsonl")
    with open(vpath, "w", encoding="utf-8") as f:
        for c, v in zip(chunks, vecs):
            f.write(json.dumps({**{k: c[k] for k in ("line", "ts", "attr", "model", "point", "is_boundary", "text")},
                                "vec": v}, ensure_ascii=False, separators=(",", ":")) + "\n")
    return {"index": vpath, "n_chunks": len(chunks), "dim": len(vecs[0]) if vecs else 0}


def _load_index(index_path: str) -> list[dict]:
    items = []
    with open(index_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def recall(jsonl_path: str, query: str, k: int = 8, *, rerank: bool = True,
           index_dir: str | None = None, fetch: int = 40) -> dict:
    """Semantic recall: embed query in the index's space → cosine top-`fetch` → rerank → top-`k` handles."""
    out_dir = index_dir or os.path.dirname(os.path.abspath(jsonl_path))
    stem = os.path.splitext(os.path.basename(jsonl_path))[0]
    index_path = os.path.join(out_dir, f"{stem}.recall.jsonl")
    if not os.path.exists(index_path):
        build_recall_index(jsonl_path, out_dir)
    items = _load_index(index_path)
    qv = _embed_one(query)
    scored = sorted(({**it, "score": _cosine(qv, it["vec"])} for it in items),
                    key=lambda x: -x["score"])[:max(fetch, k)]
    if rerank and scored:
        try:
            from ops.rerank import Reranker
            rr = Reranker(backend="jina-v3", device="cpu")
            out = rr.rerank(query, scored, top_n=k, text_of=lambda c: c["text"])
            ranked = [{**o["item"], "rerank_score": o["rerank_score"]} for o in out]
            rerank_note = "jina-v3 listwise (CPU)"
        except Exception as e:
            ranked = scored[:k]
            rerank_note = f"rerank skipped ({type(e).__name__}: {e}) — cosine order used"
    else:
        ranked, rerank_note = scored[:k], "cosine only"
    hits = [{"line": s["line"], "ts": s["ts"], "attr": s["attr"], "model": s.get("model"),
             "point": s.get("point"),
             "cosine": round(s["score"], 4), "rerank_score": round(s["rerank_score"], 4) if "rerank_score" in s else None,
             "text": " ".join(s["text"].split())[:300]} for s in ranked[:k]]
    return {"query": query, "n_indexed": len(items), "rerank": rerank_note, "hits": hits}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    jsonl, query = sys.argv[1], sys.argv[2]
    a = sys.argv[3:]
    k = int(a[a.index("--k") + 1]) if "--k" in a else 8
    rr = "--no-rerank" not in a
    idx = a[a.index("--index-dir") + 1] if "--index-dir" in a else None
    print(json.dumps(recall(jsonl, query, k=k, rerank=rr, index_dir=idx), indent=2, ensure_ascii=False))
