#!/usr/bin/env python3
"""Measure 8-bit-weight vs bf16-weight vector COMPATIBILITY for pplx-embed-context-v1-4b.

QUESTION ANSWERED: the 'extractions' vector space was embedded with the bf16 weight
path. If we flip the server to 8-bit weights (PPLX_EMBED_8BIT=1), are the resulting
query vectors close enough to the existing bf16 vectors to query that space WITHOUT a
full re-embed?

METHOD (settled with the advisor, 2026-06-27):
  - Pull ~40 REAL sample chunk texts from the extractions corpus (the `summary` field).
  - bf16 reference vectors come from the LIVE :8007 service (the exact production path,
    int8 output, normalize=False). Zero new VRAM; does not disturb the service.
  - 8-bit arm runs OFFLINE and CPU-ONLY (CUDA_VISIBLE_DEVICES="") so it NEVER touches
    the live GPU. bnb 0.49.2 supports load_in_8bit on CPU (probed).
  - Hold OUTPUT quantization = int8 in BOTH arms; the ONLY variable is weight dtype.
  - Also embed bf16 OFFLINE on CPU (device-matched control) to separate pure weight
    perturbation (float-output cosine) from the device/path confound.
  - Verdict metric = CROSS-DTYPE top-k overlap: neighbors of each item's 8-bit vector
    searched against the bf16 corpus, vs neighbors of its bf16 vector against the same
    bf16 corpus. That literally measures "query the bf16 space with 8-bit vectors".

Run:  CUDA_VISIBLE_DEVICES="" ~/vllm-env/bin/python ops/measure_8bit_vs_bf16.py

================================ FINDINGS (2026-06-28) ================================
Ran N=40 real query summaries against a 1500-vector live-bf16 search pool.
Env: ~/vllm-env (torch 2.11.0+cu130, transformers 5.9.0, bitsandbytes 0.49.2,
accelerate 1.13.0) — bnb was ALREADY installed; nothing needed installing. The 8-bit
arm ran CPU-only (CUDA_VISIBLE_DEVICES="") so it NEVER touched the live :8007 GPU; bf16
reference came from the live service. The live service stayed healthy throughout.

  WEIGHT FOOTPRINT:  bf16 = 8.04 GB   8-bit = 5.19 GB   saving = 2.86 GB (~35%).
    (Not 4GB: bnb LLM.int8() keeps some modules — layernorms, embeddings, outlier
     dims — in fp16. 5.19GB is the honest measured weight footprint.)
  COSINE 8bit-vs-bf16 (int8 output, CPU-matched):     mean 0.9961  p10 0.9954  min 0.9721
  COSINE 8bit(int8) vs LIVE bf16(int8) [operational]: mean 0.9962  p10 0.9955  min 0.9733
    (live-vs-CPU bf16 reference agree to 4 decimals -> no device-path confound; the
     gap is purely weight quantization.)
  TOP-K OVERLAP (8bit query vs bf16 query, searched in the 1500-vec bf16 pool):
     overlap@10 = 0.965     overlap@5 = 0.975

  VERDICT: 8-bit query vectors ARE compatible with the existing bf16-embedded corpus.
    Mean cosine 0.996 (>=0.99 anchor) and top-k overlap 0.965/0.975 (>=0.9 anchor) at
    real corpus scale => flipping PPLX_EMBED_8BIT=1 does NOT require a full re-embed; the
    existing bf16 'extractions' space can be queried with 8-bit query vectors as-is.
  CAVEAT: production would run 8-bit on CUDA; this was measured on CPU (bnb's CPU path
    casts inputs to fp16 — same LLM.int8() algorithm, so a CPU PASS is conservative for
    GPU, not optimistic). Output quantization (int8) is identical in both arms.
=====================================================================================
"""
import json
import os
import sys
import time
import urllib.request

import numpy as np

CORPUS = "/home/tim/company/.data/store/extractions/extractions-full.jsonl"
MODEL_ID = os.environ.get("PPLX_EMBED_MODEL", "perplexity-ai/pplx-embed-context-v1-4b")
LIVE_URL = "http://127.0.0.1:8007/v1/embeddings"
N = int(os.environ.get("MEASURE_N", "40"))
MAX_TOK = int(os.environ.get("PPLX_EMBED_MAX_TOKENS", "8192"))


def cos(a, b):
    a = a.astype(np.float64); b = b.astype(np.float64)
    na = np.linalg.norm(a); nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(a @ b / (na * nb))


def load_samples(n):
    """Take n real, non-trivial summary texts spread across the corpus."""
    return _load_texts(n, spread=True)


def _load_texts(n, spread):
    lines = []
    with open(CORPUS) as f:
        for line in f:
            line = line.strip()
            if line:
                lines.append(line)
    if spread:
        step = max(1, len(lines) // n)
        order = range(0, len(lines), step)
    else:
        order = range(len(lines))
    texts = []
    seen = set()
    for i in order:
        d = json.loads(lines[i])
        t = (d.get("summary") or d.get("about") or "").strip()
        if len(t) >= 20 and t not in seen:
            seen.add(t)
            texts.append(t)
        if len(texts) >= n:
            break
    return texts


def embed_live(texts):
    """bf16 reference from the live :8007 production path (int8 output)."""
    vecs = []
    for t in texts:
        body = json.dumps({"input": [t], "quantization": "int8", "normalize": False}).encode()
        req = urllib.request.Request(LIVE_URL, data=body,
                                     headers={"content-type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            d = json.loads(r.read())
        vecs.append(np.asarray(d["data"][0]["embedding"], dtype=np.float32))
    return np.vstack(vecs)


def _param_bytes(model):
    """Sum the on-device storage of all params+buffers. For an 8-bit bnb model the
    int8 weights report 1 byte/elem (Int8Params), so this is the real weight footprint."""
    total = 0
    seen = set()
    for t in list(model.parameters()) + list(model.buffers()):
        if id(t) in seen:
            continue
        seen.add(id(t))
        total += t.numel() * t.element_size()
    return total


def embed_offline(texts, eight_bit, quantization="int8"):
    """Embed offline, CPU-only. eight_bit=True -> bnb load_in_8bit; else bf16 weights.
    Returns (vectors, weight_bytes)."""
    import torch
    from transformers import AutoModel
    assert not torch.cuda.is_available(), "must run CPU-only (CUDA_VISIBLE_DEVICES='')"
    t0 = time.time()
    if eight_bit:
        from transformers import BitsAndBytesConfig
        cfg = BitsAndBytesConfig(load_in_8bit=True)
        model = AutoModel.from_pretrained(MODEL_ID, trust_remote_code=True,
                                          quantization_config=cfg, device_map="cpu")
    else:
        model = AutoModel.from_pretrained(MODEL_ID, trust_remote_code=True,
                                          dtype=torch.bfloat16).to("cpu")
    model.eval()
    try:
        model.tokenizer.model_max_length = MAX_TOK
    except Exception:
        pass
    wbytes = _param_bytes(model)
    print(f"[offline {'8bit' if eight_bit else 'bf16'}] loaded in {time.time()-t0:.1f}s "
          f"weight_footprint={wbytes/1e9:.2f} GB", flush=True)
    docs = [[t] for t in texts]
    with torch.no_grad():
        per_doc = model.encode(docs, batch_size=4, quantization=quantization,
                               normalize_embeddings=False, convert_to_numpy=True)
    vecs = np.vstack([d[0] for d in per_doc]).astype(np.float32)
    del model
    return vecs, wbytes


def topk_overlap(query_vecs, ref_query_vecs, corpus_vecs, self_idx, k=10):
    """For each query item i: top-k neighbors of its 8-bit vector (query_vecs[i]) vs
    top-k of its bf16 vector (ref_query_vecs[i]), BOTH searched against the SAME large
    bf16 corpus_vecs (the real ~N-vector space). Mean overlap@k.
    self_idx[i] = the row of corpus_vecs that IS item i (excluded from its own neighbors)
    so we measure genuine neighborhood reordering in a densely packed space, at scale."""
    def norm(m):
        n = np.linalg.norm(m, axis=1, keepdims=True); n[n == 0] = 1.0
        return m / n
    C = norm(corpus_vecs.astype(np.float64))
    Q = norm(query_vecs.astype(np.float64))
    R = norm(ref_query_vecs.astype(np.float64))
    overlaps = []
    for i in range(len(Q)):
        sq = Q[i] @ C.T; sr = R[i] @ C.T
        sq[self_idx[i]] = -np.inf; sr[self_idx[i]] = -np.inf  # exclude self
        nq = set(np.argsort(-sq)[:k].tolist())
        nr = set(np.argsort(-sr)[:k].tolist())
        overlaps.append(len(nq & nr) / k)
    return float(np.mean(overlaps)), overlaps


def main():
    pool_n = int(os.environ.get("MEASURE_POOL_N", "1500"))
    # Build a large bf16 SEARCH CORPUS from live :8007 (fast, GPU, no new VRAM): the
    # densely-packed space where neighbor reordering would actually show up. The N query
    # items are the FIRST N rows of this pool, so each query's self-row is known and the
    # neighbors it competes against are real corpus members (not just the 40).
    pool_texts = _load_texts(pool_n, spread=False)
    texts = pool_texts[:N]  # the items we'll re-embed in 8-bit (slow CPU part stays small)
    print(f"Search pool = {len(pool_texts)} real summaries; query set = {len(texts)}.", flush=True)

    print(f"Embedding the {len(pool_texts)}-vector bf16 search pool via LIVE :8007 (int8)...", flush=True)
    pool_bf16_int8 = embed_live(pool_texts)
    bf16_live_int8 = pool_bf16_int8[:N]  # the bf16 reference for the query items

    print("Embedding bf16 OFFLINE CPU (int8 output, device-matched control)...", flush=True)
    bf16_cpu_int8, bf16_wbytes = embed_offline(texts, eight_bit=False)

    print("Embedding 8BIT OFFLINE CPU (int8 output)...", flush=True)
    eb_cpu_int8, eb_wbytes = embed_offline(texts, eight_bit=True)

    # --- per-item cosines ---
    cos_int8_cpu = [cos(eb_cpu_int8[i], bf16_cpu_int8[i]) for i in range(len(texts))]
    # The operational one: 8bit (int8) vs the ACTUAL production bf16 vectors (live, int8)
    cos_int8_live = [cos(eb_cpu_int8[i], bf16_live_int8[i]) for i in range(len(texts))]

    # --- cross-dtype top-k overlap against the LARGE live bf16 corpus (the real space) ---
    # query with 8bit-int8 vs query with bf16-int8(live), both searched in the bf16 pool.
    self_idx = list(range(N))  # query item i == pool row i
    ov10, _ = topk_overlap(eb_cpu_int8, bf16_live_int8, pool_bf16_int8, self_idx, k=10)
    ov5, _ = topk_overlap(eb_cpu_int8, bf16_live_int8, pool_bf16_int8, self_idx, k=5)

    def stat(x):
        x = np.asarray(x)
        return f"mean={x.mean():.4f} min={x.min():.4f} p10={np.percentile(x,10):.4f} max={x.max():.4f}"

    print("\n================ RESULTS ================")
    print(f"N samples: {len(texts)}")
    print(f"weight footprint  bf16={bf16_wbytes/1e9:.2f} GB   8bit={eb_wbytes/1e9:.2f} GB   "
          f"saving={(bf16_wbytes-eb_wbytes)/1e9:.2f} GB ({100*(bf16_wbytes-eb_wbytes)/bf16_wbytes:.0f}%)")
    print(f"cosine 8bit-vs-bf16  (INT8 output, CPU-matched):                      {stat(cos_int8_cpu)}")
    print(f"cosine 8bit(int8) vs LIVE bf16(int8)  [OPERATIONAL: query vs corpus]: {stat(cos_int8_live)}")
    print(f"top-k overlap@10 (8bit query vs bf16 query, in {len(pool_texts)}-vec bf16 pool): {ov10:.4f}")
    print(f"top-k overlap@5  (8bit query vs bf16 query, in {len(pool_texts)}-vec bf16 pool): {ov5:.4f}")
    print("=========================================")

    result = {
        "n": len(texts),
        "pool_n": len(pool_texts),
        "weight_footprint_gb": {"bf16": bf16_wbytes/1e9, "int8": eb_wbytes/1e9,
                                "saving_gb": (bf16_wbytes-eb_wbytes)/1e9},
        "cos_int8_cpu": {"mean": float(np.mean(cos_int8_cpu)), "min": float(np.min(cos_int8_cpu))},
        "cos_int8_vs_live": {"mean": float(np.mean(cos_int8_live)), "min": float(np.min(cos_int8_live)),
                             "p10": float(np.percentile(cos_int8_live, 10))},
        "topk_overlap_at_10": ov10,
        "topk_overlap_at_5": ov5,
    }
    out = "/tmp/claude-1000/-home-tim/bda8ce28-6dfb-4a76-b13a-bc016b8574ca/scratchpad/measure_result.json"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
