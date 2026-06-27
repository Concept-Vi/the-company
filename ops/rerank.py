#!/usr/bin/env python3
"""rerank.py — a clean, REUSABLE cross-encoder rerank step for the Company.

WHAT THIS IS (and why it lives here, not in the substrate):
  After a semantic search returns top-N candidates by embedding cosine
  similarity (a bi-encoder: query and docs embedded SEPARATELY, compared by
  vector distance), a *reranker* re-scores each (query, candidate) pair with a
  model that reads the query and candidate TOGETHER and outputs a relevance
  score. It then sorts by that score. This catches relevance the bi-encoder
  misses (the embedder compresses each text to one vector in isolation; the
  reranker attends across the pair). Standard two-stage retrieval:
      EMBED + ANN search (fast, recall) → RERANK top-N (slow, precision).

  This is built as a standalone Company capability, NOT bolted onto the
  obsidian-overlord substrate, for grounded reasons:
    - The substrate venv (obsidian-overlord/.venv) carries only chromadb +
      httpx — NO torch/transformers (verified). The reranker is a multi-GB
      torch model; putting it in the lean throwaway substrate venv would
      pollute it. Here it runs in ~/vllm-env (torch 2.11+cu130, transformers
      5.9.0), the same venv that serves the embedder.
    - The reranker is meant to OUTLIVE this throwaway: the real memory system
      Tim is building will want the same step. A model-agnostic module that
      takes (query, list[candidate]) and returns a re-ordered list is reusable
      anywhere; a method welded onto SubstrateChroma is not.
  So the SEAM is: substrate-search returns candidates → THIS module reranks.
  The wiring is an OPTIONAL `--rerank` toggle on the search commands; default
  off, so the embedding-only path is unchanged.

BACKENDS (registry-is-truth — declared in RERANKERS, selectable by name/env):
  - "jina-v3"  jinaai/jina-reranker-v3 — 0.6B Qwen3 LISTWISE reranker
        (`last but not late interaction`: query+docs in one context window,
        relevance from each doc's last token). SOTA multilingual; runs on CPU.
        Verified: ~139 ms/doc amortized on CPU (20 docs ≈ 2.8 s), correct
        ordering on a controlled probe. trust_remote_code REQUIRED (custom
        JinaForRanking arch). API: model.rerank(query, docs, top_n) ->
        [{document, relevance_score, index, ...}] sorted desc.
  - "ms-marco" cross-encoder/ms-marco-MiniLM-L-6-v2 — 88 MB classic
        cross-encoder pair-scorer. FALLBACK when jina-v3 is too slow: verified
        ~56 ms/doc on CPU (~10x faster per-doc), correct ordering. Scores via
        AutoModelForSequenceClassification logits.

DEVICE: CPU by default (device="cpu") — Tim's call: keep the GPU for the
  embedder (pplx-embed-context-v1-4b) + voice. CUDA is hidden at import unless
  device="cuda" is explicitly requested.

FAIL LOUD (repo law): a requested backend that won't load raises; no silent
  fallback to "no rerank" and no fake scores. The CALLER decides whether to
  rerank (the toggle); once asked, it either reranks or fails loudly.

USAGE (as a library):
  from rerank import Reranker
  rr = Reranker("jina-v3")                 # lazy: weights load on first .rerank
  ranked = rr.rerank(query, candidates, top_n=8)
  # candidates: list[str] OR list[dict-with-a-text-field]
  # returns the SAME items re-ordered, each annotated with rerank_score + the
  # pre-rerank rank, so a caller can show BEFORE vs AFTER.

USAGE (self-test from the CLI):
  python ops/rerank.py selftest                 # jina-v3 on a controlled probe
  python ops/rerank.py selftest --backend ms-marco
  python ops/rerank.py rerank "query" "doc a" "doc b" "doc c"
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from typing import Any, Callable, List, Optional, Sequence, Union

# ---------------------------------------------------------------------------
# Registry of reranker backends (registry-is-truth). Add a row to extend.
#   load_kind: which transformers loader + rerank strategy to use.
#   hf_id:     the model id (must be present in ~/.cache/huggingface/hub).
# ---------------------------------------------------------------------------
RERANKERS: dict[str, dict[str, Any]] = {
    "jina-v3": {
        "hf_id": "jinaai/jina-reranker-v3",
        "load_kind": "jina_listwise",
        "trust_remote_code": True,
        "note": "0.6B Qwen3 listwise reranker; SOTA multilingual; ~139ms/doc CPU",
    },
    "ms-marco": {
        "hf_id": "cross-encoder/ms-marco-MiniLM-L-6-v2",
        "load_kind": "seqcls_crossencoder",
        "trust_remote_code": False,
        "note": "88MB cross-encoder fallback; ~56ms/doc CPU (~10x faster)",
    },
}

DEFAULT_BACKEND = os.environ.get("COMPANY_RERANKER", "jina-v3")


def _text_of(item: Union[str, dict]) -> str:
    """Pull the rerankable text out of a candidate (str or dict)."""
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        for k in ("text", "document", "content", "chunk", "body"):
            v = item.get(k)
            if isinstance(v, str) and v.strip():
                return v
        # last resort: stringify
        return str(item)
    return str(item)


class Reranker:
    """A lazily-loaded, model-agnostic reranker. Pick a backend by name from
    RERANKERS. Weights load on first .rerank() (or .load()), on CPU by default."""

    def __init__(self, backend: str = DEFAULT_BACKEND, device: str = "cpu"):
        if backend not in RERANKERS:
            raise ValueError(
                f"unknown reranker backend {backend!r}; "
                f"known: {sorted(RERANKERS)}"
            )
        self.backend = backend
        self.spec = RERANKERS[backend]
        self.device = device
        self._model = None
        self._tok = None
        self._loaded = False

    # -- loading --------------------------------------------------------------
    def load(self) -> "Reranker":
        if self._loaded:
            return self
        # Keep the GPU for the embedder + voice unless CUDA is explicitly asked.
        if self.device == "cpu":
            os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
        import torch
        torch.set_num_threads(max(1, (os.cpu_count() or 4)))
        kind = self.spec["load_kind"]
        hf_id = self.spec["hf_id"]
        trc = self.spec["trust_remote_code"]
        t0 = time.time()
        if kind == "jina_listwise":
            from transformers import AutoModel
            # dtype follows the device (2026-06-28, Tim): on GPU use bf16 — half the VRAM (~2.8GB fp32
            # → ~1.3GB) with near-zero quality loss (bf16 is the model's native inference precision);
            # on CPU keep fp32 (fp16/bf16 CPU kernels are often slower/unsupported). Overridable via
            # COMPANY_RERANK_DTYPE (float32|bfloat16|float16).
            _dt = os.environ.get("COMPANY_RERANK_DTYPE", "bfloat16" if self.device != "cpu" else "float32")
            _dtype = {"float32": torch.float32, "bfloat16": torch.bfloat16, "float16": torch.float16}[_dt]
            self._model = AutoModel.from_pretrained(
                hf_id, dtype=_dtype, trust_remote_code=trc
            ).to(self.device).eval()
        elif kind == "seqcls_crossencoder":
            from transformers import (AutoTokenizer,
                                      AutoModelForSequenceClassification)
            self._tok = AutoTokenizer.from_pretrained(hf_id)
            self._model = AutoModelForSequenceClassification.from_pretrained(
                hf_id, trust_remote_code=trc
            ).to(self.device).eval()
        else:  # fail loud — unknown load strategy
            raise NotImplementedError(f"load_kind {kind!r} not implemented")
        self._load_s = time.time() - t0
        self._loaded = True
        return self

    # -- scoring --------------------------------------------------------------
    def _score(self, query: str, texts: List[str]) -> List[float]:
        """Return a relevance score per text, in INPUT order (higher = better)."""
        import torch
        kind = self.spec["load_kind"]
        if kind == "jina_listwise":
            # rerank() returns results SORTED; recover input-order scores via index.
            res = self._model.rerank(query, texts, top_n=len(texts))
            scores = [0.0] * len(texts)
            for r in res:
                scores[int(r["index"])] = float(r["relevance_score"])
            return scores
        if kind == "seqcls_crossencoder":
            with torch.no_grad():
                feats = self._tok(
                    [query] * len(texts), texts,
                    padding=True, truncation=True,
                    max_length=512, return_tensors="pt",
                ).to(self.device)
                logits = self._model(**feats).logits.view(-1)
            return [float(x) for x in logits.cpu().tolist()]
        raise NotImplementedError(f"scoring for {kind!r} not implemented")

    def rerank(
        self,
        query: str,
        candidates: Sequence[Union[str, dict]],
        top_n: Optional[int] = None,
        text_of: Callable[[Any], str] = _text_of,
    ) -> List[dict]:
        """Re-order `candidates` by deeper (query, candidate) relevance.

        Returns a list of dicts (one per returned candidate), each carrying:
          item          - the ORIGINAL candidate (str or dict), untouched
          text          - the text that was scored
          rerank_score  - the cross-encoder relevance score (higher = better)
          orig_rank     - 1-based position BEFORE rerank (the search order in)
          rank          - 1-based position AFTER rerank
        Sorted by rerank_score desc, truncated to top_n (default: all). Fail
        loud: empty candidates raises (the caller asked to rerank nothing)."""
        if not candidates:
            raise ValueError("rerank() got 0 candidates")
        self.load()
        texts = [text_of(c) for c in candidates]
        scores = self._score(query, texts)
        order = sorted(range(len(candidates)), key=lambda i: scores[i], reverse=True)
        if top_n is not None:
            order = order[: min(top_n, len(order))]
        out: List[dict] = []
        for new_rank, i in enumerate(order, 1):
            out.append({
                "item": candidates[i],
                "text": texts[i],
                "rerank_score": scores[i],
                "orig_rank": i + 1,   # candidates arrive in search order
                "rank": new_rank,
            })
        return out


# ---------------------------------------------------------------------------
# CLI: self-test (verify-by-run) + ad-hoc rerank.
# ---------------------------------------------------------------------------

_PROBE_QUERY = "how does the GPU VRAM budget and model eviction work when loading a model"
# Deliberately mis-ordered: the most relevant doc is NOT first, so a working
# reranker MUST change the order.
_PROBE_DOCS = [
    "Bananas in Pyjamas are coming down the stairs.",
    "The company CLI resource-manager refuses a model load when VRAM is short "
    "and can --evict the largest resident model to free GPU memory.",
    "Voice synthesis with XTTS produces a wav file from text.",
    "gpu_memory_utilization sets the fraction of VRAM vLLM reserves; eviction "
    "frees a model so another fits.",
    "The cat sat on the warm windowsill in the afternoon sun.",
]


def cmd_selftest(args) -> int:
    rr = Reranker(args.backend, device=args.device)
    t0 = time.time()
    ranked = rr.rerank(_PROBE_QUERY, _PROBE_DOCS, top_n=len(_PROBE_DOCS))
    dt = time.time() - t0
    print(f"backend={args.backend} device={args.device} "
          f"load={getattr(rr,'_load_s',0):.1f}s rerank={dt*1000:.0f}ms "
          f"({dt/len(_PROBE_DOCS)*1000:.0f}ms/doc)")
    print("BEFORE (search/input order):")
    for i, d in enumerate(_PROBE_DOCS, 1):
        print(f"  {i}. {d[:64]}")
    print("AFTER (reranked):")
    for r in ranked:
        print(f"  {r['rank']}. (was #{r['orig_rank']})  "
              f"score={r['rerank_score']:.4f}  {r['text'][:64]}")
    top = ranked[0]
    if top["orig_rank"] == 1:
        print("WARN: top did not move — check the model")
        return 1
    # A relevant doc (the VRAM/eviction ones were inputs #2 or #4) must be on top.
    if top["orig_rank"] not in (2, 4):
        print(f"FAIL: expected a VRAM/eviction doc on top, got was-#{top['orig_rank']}")
        return 1
    print("SELFTEST_OK ordering changed and a relevant doc is on top")
    return 0


def cmd_rerank(args) -> int:
    rr = Reranker(args.backend, device=args.device)
    ranked = rr.rerank(args.query, args.docs, top_n=args.k)
    for r in ranked:
        print(f"#{r['rank']} (was #{r['orig_rank']}) score={r['rerank_score']:.4f}  {r['text'][:90]}")
    return 0


def cmd_rerank_file(args) -> int:
    """Stage 2 of the lean 2-stage seam: read a candidate pool dumped by the
    substrate search (`wire_substrate_claude_sessions.py search --json`) and
    rerank it. Keeps the substrate venv (chromadb, no torch) and the reranker
    venv (torch, no chromadb) cleanly separated. Prints BEFORE vs AFTER."""
    import json
    with open(args.path, encoding="utf-8") as fh:
        payload = json.load(fh)
    query = payload["query"]
    cand = payload["candidates"]
    k = args.k or payload.get("k") or len(cand)
    if not cand:
        print("FAIL: candidate file has 0 candidates"); return 1

    def _addr(c):
        return ((c.get("metadata") or {}).get("address")) if isinstance(c, dict) else None

    rr = Reranker(args.backend, device=args.device)
    t0 = time.time()
    ranked = rr.rerank(query, cand, top_n=k,
                       text_of=lambda c: (c.get("text") or "") if isinstance(c, dict) else str(c))
    dt = time.time() - t0
    print(f"Query: {query!r}")
    print(f"Reranker: {args.backend} (CPU) | {len(cand)} candidates → top {len(ranked)} "
          f"in {dt*1000:.0f}ms ({dt/len(cand)*1000:.0f}ms/cand)")
    print("\nBEFORE (embedding cosine order):\n" + "-" * 72)
    for i, c in enumerate(cand[:k], 1):
        dist = c.get("distance") if isinstance(c, dict) else None
        cos = f"cos~{1-dist:.3f}  " if isinstance(dist, (int, float)) else ""
        txt = ((c.get("text") if isinstance(c, dict) else str(c)) or "").strip().replace("\n", " ")
        print(f"  #{i}  {cos}{_addr(c) or ''}\n       {txt[:160]}")
    print("\nAFTER (reranked):\n" + "-" * 72)
    for r in ranked:
        txt = (r["text"] or "").strip().replace("\n", " ")
        print(f"  #{r['rank']} (was #{r['orig_rank']})  rerank={r['rerank_score']:.4f}  "
              f"{_addr(r['item']) or ''}\n       {txt[:160]}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Company reusable rerank step")
    ap.add_argument("--backend", default=DEFAULT_BACKEND, choices=sorted(RERANKERS))
    ap.add_argument("--device", default="cpu", choices=["cpu", "cuda"])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest").set_defaults(func=cmd_selftest)
    pr = sub.add_parser("rerank")
    pr.add_argument("query")
    pr.add_argument("docs", nargs="+")
    pr.add_argument("-k", type=int, default=None)
    pr.set_defaults(func=cmd_rerank)
    pf = sub.add_parser("rerank-file",
                        help="rerank a candidate pool JSON (stage 2 of the substrate seam)")
    pf.add_argument("path")
    pf.add_argument("-k", type=int, default=None)
    pf.set_defaults(func=cmd_rerank_file)
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
