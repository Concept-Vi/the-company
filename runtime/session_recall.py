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
import re
import sys
import urllib.request

from runtime.session_scan import scan_session

EMBED_URL = os.environ.get("PPLX_EMBED_URL", "http://127.0.0.1:8007/v1/embeddings")
EMBED_MODEL = os.environ.get("PPLX_EMBED_MODEL", "perplexity-ai/pplx-embed-context-v1-4b")
EMBED_DIM = 2560
RERANK_URL = os.environ.get("RERANK_URL", "http://127.0.0.1:8008/rerank")   # the lead's served jina-v3 (CPU, bridge-free)
RERANK_POOL = int(os.environ.get("RECALL_RERANK_POOL", "12"))               # CPU listwise: cap candidates sent to rerank
RERANK_TIMEOUT = int(os.environ.get("RECALL_RERANK_TIMEOUT", "180"))
# group turns into documents that stay within the embedder's context (late-chunking happens WITHIN a group);
# conservative char budget per group so a group never overflows the 32K-token window.
GROUP_CHAR_BUDGET = int(os.environ.get("RECALL_GROUP_CHARS", "16000"))
MAX_TURNS_PER_GROUP = int(os.environ.get("RECALL_GROUP_TURNS", "32"))


class RecallError(RuntimeError):
    """Fail-loud: a recall that cannot ground (embedder down, no chunks) raises — never returns silent empty."""


# ───────────────────────────── chunking (from the scan) ─────────────────────────────

SUB_CHUNK_CHARS = int(os.environ.get("RECALL_SUBCHUNK_CHARS", "700"))
SUB_CHUNK_OVERLAP = int(os.environ.get("RECALL_SUBCHUNK_OVERLAP", "150"))


MIN_CHUNK_CHARS = int(os.environ.get("RECALL_MIN_CHUNK_CHARS", "120"))
_DIM_BOUNDARY = re.compile(
    r"(?m)^(?:\s*#{1,6}\s+"          # markdown header
    r"|\s*[-*•]\s+"                  # bullet item
    r"|\s*\d+[.)]\s+"               # numbered item (1.  1))
    r"|\s*[A-Z][.)]\s+)"            # lettered item (A.  A)) — Tim's onboarding-question style
)


def _window_split(text: str, size: int, overlap: int) -> list[str]:
    """Size-window fallback (sentence/newline-boundary preferred) — used only WITHIN an over-large unit."""
    if len(text) <= size:
        return [text] if text else []
    out, i = [], 0
    while i < len(text):
        end = min(i + size, len(text))
        if end < len(text):
            cut = max(text.rfind(". ", i + size - overlap, end), text.rfind("\n", i + size - overlap, end))
            if cut > i:
                end = cut + 1
        out.append(text[i:end].strip())
        if end >= len(text):
            break
        i = max(end - overlap, i + 1)
    return [c for c in out if c]


CHUNK_MODE = os.environ.get("RECALL_CHUNK_MODE", "dimension")   # dimension | window (window = the old A/B baseline)


def _split(text: str, size: int = SUB_CHUNK_CHARS, overlap: int = SUB_CHUNK_OVERLAP) -> list[str]:
    """DIMENSION-AWARE split (Criteria 1.1; Tim: "my messages are very long and very dense and
    multidimensional" + CLAUDE.md "each line a dimension"). Split on the message's OWN STRUCTURE first —
    markdown headers, paragraphs (blank lines), bullet/numbered/lettered list items — so each dimension
    embeds as its OWN vector instead of averaging into a blur (the failure that sank the 5-decision turn
    L4335 to rank #51). Only within an over-large structural unit do we fall back to size-windowing.
    Tiny adjacent units are merged up to MIN so we don't over-fragment into one-word chunks.
    RECALL_CHUNK_MODE=window restores the pure size-window baseline (for A/B)."""
    text = text.strip()
    if CHUNK_MODE == "window":
        return _window_split(text, size, overlap)
    if len(text) <= size:
        return [text] if text else []
    # 1) cut at strong structural boundaries: blank-line paragraphs, then header/list markers
    units: list[str] = []
    for para in re.split(r"\n\s*\n", text):           # paragraphs first (double newline = strongest)
        para = para.strip()
        if not para:
            continue
        # within a paragraph, start a new unit at each header/list-item line (a dimension shift)
        cur, last = [], 0
        for mt in _DIM_BOUNDARY.finditer(para):
            if mt.start() > last:
                seg = para[last:mt.start()].strip()
                if seg:
                    cur.append(seg)
            last = mt.start()
        tail = para[last:].strip()
        if tail:
            cur.append(tail)
        units.extend(cur or [para])
    # 2) over-large unit → window-split it; keep others whole
    sized: list[str] = []
    for u in units:
        sized.extend(_window_split(u, size, overlap) if len(u) > size else [u])
    # 3) merge tiny adjacent units up to MIN (avoid one-line fragments while keeping dimensions distinct)
    merged: list[str] = []
    for s in sized:
        if merged and len(merged[-1]) < MIN_CHUNK_CHARS:
            merged[-1] = (merged[-1] + "\n" + s).strip()
        else:
            merged.append(s)
    return [c for c in merged if c]


def session_chunks(jsonl_path: str) -> list[dict]:
    """Genuine content turns as recall chunks, each with its structural handle. Reuses the scanner so
    chunking and the structural scan agree on attribution/boundaries. Skips inject/tool/empty events —
    we recall over what was SAID (human + assistant + compaction summaries), not tool plumbing. Long
    turns are split into overlapping SUB-chunks (sharing the turn's line handle) so multi-topic turns
    stay retrievable."""
    rows = scan_session(jsonl_path)["rows"]
    meta = [{"line": r["line"], "ts": r["ts"], "attr": r["attr"], "model": r.get("model"),
             "point": r.get("boundary_point"), "is_boundary": r.get("is_boundary")}
            for r in rows if r["attr"] in ("user", "assistant", "compaction", "channel")]
    texts = _texts_for_lines(jsonl_path, {m["line"] for m in meta})
    out = []
    for m in meta:
        t = (texts.get(m["line"]) or "").strip()
        if not t:
            continue
        parts = _split(t)
        for si, part in enumerate(parts):
            out.append({**m, "sub": si, "n_sub": len(parts), "text": part})
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


def _rerank_endpoint(query: str, texts: list[str], top_n: int) -> list[dict]:
    """POST the lead's served jina-v3 reranker (:8008, CPU). Returns ranking[{orig_rank, rerank_score,…}].
    Served, not in-process: no torch dep, no overlord bridge (Tim's direction)."""
    body = json.dumps({"query": query, "candidates": texts, "top_n": top_n}).encode()
    req = urllib.request.Request(RERANK_URL, data=body, headers={"Content-Type": "application/json"})
    r = json.loads(urllib.request.urlopen(req, timeout=RERANK_TIMEOUT).read())
    return r.get("ranking") or []


# ───────────────────────────── similarity + index ─────────────────────────────

def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)); nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0


def _index_paths(jsonl_path: str, out_dir: str | None):
    out_dir = out_dir or os.path.dirname(os.path.abspath(jsonl_path))
    stem = os.path.splitext(os.path.basename(jsonl_path))[0]
    return out_dir, os.path.join(out_dir, f"{stem}.recall.jsonl"), os.path.join(out_dir, f"{stem}.recall.meta.json")


def _source_stamp(jsonl_path: str) -> dict:
    st = os.stat(jsonl_path)
    return {"source_bytes": st.st_size, "source_mtime_ns": st.st_mtime_ns}


def index_freshness(jsonl_path: str, out_dir: str | None = None) -> dict:
    """Is the index current vs the (possibly LIVE/growing) source? Compares the source's size+mtime
    against the stamp recorded at build. A LIVE session's .jsonl grows → a build-once index goes stale
    silently (the advisor's flag); this surfaces it so recall can rebuild or declare — never serve stale
    silently ([[no-silent-failures]])."""
    _, vpath, mpath = _index_paths(jsonl_path, out_dir)
    if not os.path.exists(vpath) or not os.path.exists(mpath):
        return {"exists": False, "fresh": False, "why": "no index yet"}
    try:
        meta = json.load(open(mpath, encoding="utf-8"))
    except Exception:
        return {"exists": True, "fresh": False, "why": "meta unreadable — treat as stale"}
    cur = _source_stamp(jsonl_path)
    fresh = (meta.get("source_bytes") == cur["source_bytes"]
             and meta.get("source_mtime_ns") == cur["source_mtime_ns"])
    return {"exists": True, "fresh": fresh, "indexed_bytes": meta.get("source_bytes"),
            "current_bytes": cur["source_bytes"], "chunk_mode": meta.get("chunk_mode"),
            "embed_model": meta.get("embed_model"), "built_at": meta.get("built_at"),
            "why": "current" if fresh else
                   f"STALE — source grew {meta.get('source_bytes')}→{cur['source_bytes']} bytes since index build"}


def build_recall_index(jsonl_path: str, out_dir: str | None = None) -> dict:
    """Chunk + embed a session; persist vectors + a freshness meta sidecar so re-recall is fast AND
    staleness is detectable (build once, query many; rebuild on source change)."""
    chunks = session_chunks(jsonl_path)
    if not chunks:
        raise RecallError(f"recall: no content turns to index in {jsonl_path} (only plumbing/empty events).")
    stamp = _source_stamp(jsonl_path)          # stamp BEFORE embedding (a concurrent live write → next-recall stale, not a torn index)
    vecs = _embed_chunks([c["text"] for c in chunks])
    if len(vecs) != len(chunks):
        raise RecallError(f"recall: embedder returned {len(vecs)} vectors for {len(chunks)} chunks — "
                          f"index/embedding mismatch; refusing to build a misaligned index.")
    out_dir, vpath, mpath = _index_paths(jsonl_path, out_dir)
    os.makedirs(out_dir, exist_ok=True)
    with open(vpath, "w", encoding="utf-8") as f:
        for c, v in zip(chunks, vecs):
            f.write(json.dumps({**{k: c[k] for k in ("line", "ts", "attr", "model", "point", "is_boundary", "text")},
                                "vec": v}, ensure_ascii=False, separators=(",", ":")) + "\n")
    meta = {**stamp, "n_chunks": len(chunks), "dim": len(vecs[0]) if vecs else 0,
            "embed_model": EMBED_MODEL, "chunk_mode": CHUNK_MODE,
            "source_path": os.path.abspath(jsonl_path)}
    with open(mpath, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    return {"index": vpath, "meta": mpath, "n_chunks": len(chunks), "dim": meta["dim"]}


def _load_index(index_path: str) -> list[dict]:
    items = []
    with open(index_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items


def recall(jsonl_path: str, query: str, k: int = 8, *, rerank: bool = True,
           index_dir: str | None = None, fetch: int = 40, auto_rebuild: bool = True) -> dict:
    """Semantic recall: embed query in the index's space → cosine top-`fetch` → rerank → top-`k` handles.
    FRESHNESS (Criteria 2.4): if the source grew since the index was built (a LIVE session), rebuild
    (auto_rebuild) — or, if rebuild is off, DECLARE the staleness in the envelope. Never serve stale silently."""
    out_dir, index_path, _ = _index_paths(jsonl_path, index_dir)
    fresh = index_freshness(jsonl_path, index_dir)
    stale_note = None
    if not fresh["exists"]:
        build_recall_index(jsonl_path, out_dir)
    elif not fresh["fresh"]:
        if auto_rebuild:
            build_recall_index(jsonl_path, out_dir)               # rebuild to current state
            stale_note = f"index was stale ({fresh['why']}) — REBUILT to current source"
        else:
            stale_note = f"WARNING: serving a STALE index ({fresh['why']}); pass auto_rebuild=True to refresh"
    items = _load_index(index_path)
    qv = _embed_one(query)
    scored = sorted(({**it, "score": _cosine(qv, it["vec"])} for it in items),
                    key=lambda x: -x["score"])[:max(fetch, k)]
    if rerank and scored:
        try:
            # CPU listwise rerank: cap candidates + truncate text (the decisive signal is in the first ~600 chars).
            pool = scored[:RERANK_POOL]
            order = _rerank_endpoint(query, [s["text"][:600] for s in pool], top_n=k)
            # the endpoint returns ranking with orig_rank (1-based index into what we sent) → map back
            ranked = [{**pool[o["orig_rank"] - 1], "rerank_score": o["rerank_score"]} for o in order]
            rerank_note = f"jina-v3 (served :8008, CPU, pool={len(pool)})"
        except RecallError:
            raise
        except Exception as e:
            ranked = scored[:k]
            rerank_note = f"rerank UNAVAILABLE ({type(e).__name__}: {e}) — cosine order used (declared, not silent)"
    else:
        ranked, rerank_note = scored[:k], "cosine only"
    hits = [{"line": s["line"], "ts": s["ts"], "attr": s["attr"], "model": s.get("model"),
             "point": s.get("point"),
             "cosine": round(s["score"], 4), "rerank_score": round(s["rerank_score"], 4) if "rerank_score" in s else None,
             "text": " ".join(s["text"].split())[:300]} for s in ranked[:k]]
    out = {"query": query, "n_indexed": len(items), "rerank": rerank_note, "hits": hits}
    if stale_note:
        out["freshness"] = stale_note          # declared in the envelope — never silent (Criteria 2.4)
    return out


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    jsonl, query = sys.argv[1], sys.argv[2]
    a = sys.argv[3:]
    k = int(a[a.index("--k") + 1]) if "--k" in a else 8
    rr = "--no-rerank" not in a
    idx = a[a.index("--index-dir") + 1] if "--index-dir" in a else None
    print(json.dumps(recall(jsonl, query, k=k, rerank=rr, index_dir=idx), indent=2, ensure_ascii=False))
