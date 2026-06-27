#!/usr/bin/env python3
"""FastAPI server exposing perplexity-ai/pplx-embed-context-v1-4b on an
OpenAI-compatible /v1/embeddings endpoint.

WHY a custom transformers server (not serve_model.sh / vLLM):
  This model's architecture is `PPLXQwen3Model` (config model_type
  `bidirectional_pplx_qwen3`) — a CUSTOM arch shipped as remote code
  (auto_map → modeling.PPLXQwen3ContextualModel, trust_remote_code REQUIRED).
  vLLM 0.21.0 does NOT have this arch registered (verified: absent from the
  356 supported archs; `vllm serve` fails at load_model). So, exactly like
  the jina-embeddings-v4 precedent (serve_jina_v4.py), it runs via raw
  transformers behind a small FastAPI shell. This is the Company's standard
  pattern for a non-vLLM custom embedder.

MODEL FACTS (grounded in the HF model card + modeling.py):
  - dim = 2560 (the 4B tier)
  - native output is INT8, UNNORMALIZED → compare with COSINE similarity
  - mean pooling, no instruction prefix needed
  - the model is *contextual*: its .encode() takes list[list[str]] (documents
    of chunks) and returns one (n_chunks, 2560) int8 array per document, using
    late chunking. For a flat OpenAI-style /v1/embeddings call we treat each
    input string as a single-chunk document [[text]] and return that chunk's
    one 2560-d vector. (The richer per-document contextual mode is exposed via
    the optional `documents` field — see below.)

ENDPOINTS:
  POST /v1/embeddings   OpenAI-compatible. Body:
      {"input": ["text a", "text b"], "model": "...", "quantization": "int8"}
    Returns data[i].embedding = list of 2560 ints (int8 range, unnormalized).
    Optional `documents`: [["chunk1","chunk2"], ...] for native contextual
    late-chunking; when present it overrides `input` and the response carries
    one row per (document, chunk) flattened in order, each tagged in `meta`.
  GET  /v1/models       lists the served model id
  GET  /health          {"status": "ok"|"loading"}

ENV:
  PPLX_EMBED_MODEL  (default perplexity-ai/pplx-embed-context-v1-4b)
  PPLX_EMBED_PORT   (default 8007)
  PPLX_EMBED_DTYPE  (default bfloat16 — fits ~8GB; the card stores fp32)
  PPLX_EMBED_8BIT   (default unset/0 — OFF. When "1"/"true", load the model
                     weights via bitsandbytes BitsAndBytesConfig(load_in_8bit=True)
                     instead of the bf16 path. MEASURED saving = 2.86 GB of WEIGHT
                     footprint (bf16 weights 8.04GB → int8 weights 5.19GB; not 4GB
                     because bnb keeps layernorms/embeddings/outliers in fp16; this
                     is weight footprint, not total VRAM).
                     OPT-IN ONLY: when unset the bf16 load path below is byte-
                     identical to the long-running production behavior. The int8
                     OUTPUT quantization is unchanged either way; only the weight
                     dtype differs.
                     COMPATIBILITY (measured 2026-06-28, ops/measure_8bit_vs_bf16.py
                     FINDINGS block): 8-bit query vectors are COMPATIBLE with the
                     existing bf16-embedded 'extractions' corpus — mean cosine 0.996
                     (p10 0.9955) and top-k overlap 0.965@10 / 0.975@5 vs the real
                     packed space — so flipping this on does NOT require a re-embed;
                     the bf16 space can be queried with 8-bit query vectors as-is.
                     (Measured CPU-side; production runs 8-bit on CUDA, where the same
                     LLM.int8() makes a CPU pass conservative, not optimistic.))

Run:  python serve_pplx_embed.py
Test: curl localhost:8007/v1/embeddings -d '{"input":["hello","world"]}'
"""
import asyncio
import os
import time
from typing import List, Literal, Optional

import torch
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModel

MODEL_ID = os.environ.get("PPLX_EMBED_MODEL", "perplexity-ai/pplx-embed-context-v1-4b")
PORT = int(os.environ.get("PPLX_EMBED_PORT", "8007"))
DTYPE = os.environ.get("PPLX_EMBED_DTYPE", "bfloat16")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

_DTYPES = {"bfloat16": torch.bfloat16, "float16": torch.float16, "float32": torch.float32}

app = FastAPI(title="pplx-embed-context-v1-4b server")
_state = {"model": None, "lock": asyncio.Lock(), "dim": None}


class EmbeddingRequest(BaseModel):
    # OpenAI-style flat input: each string embedded as a single-chunk document.
    input: Optional[List[str]] = None
    # Native contextual mode: list of documents, each a list of chunk strings.
    documents: Optional[List[List[str]]] = None
    model: str = MODEL_ID
    quantization: Literal["int8", "binary", "ubinary"] = "int8"
    normalize: bool = False  # the model is natively UNNORMALIZED; keep default off


class EmbeddingData(BaseModel):
    object: str = "embedding"
    embedding: List[float]
    index: int
    meta: Optional[dict] = None


class EmbeddingResponse(BaseModel):
    object: str = "list"
    data: List[EmbeddingData]
    model: str
    usage: dict


def _truthy(v):
    return str(v).strip().lower() in ("1", "true", "yes", "on")


@app.on_event("startup")
def load_model():
    dt = _DTYPES.get(DTYPE, torch.bfloat16)
    use_8bit = _truthy(os.environ.get("PPLX_EMBED_8BIT", ""))
    t0 = time.time()
    if use_8bit:
        # OPT-IN 8-bit weight load (bitsandbytes). Measured saving ~2.86GB weight
        # footprint vs bf16 (8.04GB->5.19GB); see ops/measure_8bit_vs_bf16.py FINDINGS.
        # NOTE: load_in_8bit places weights via device_map — do NOT call .to(DEVICE)
        # afterward (bnb manages placement; an explicit .to() on an 8bit model errors).
        from transformers import BitsAndBytesConfig
        print(f"[pplx-embed] loading {MODEL_ID} in 8BIT (bitsandbytes) on {DEVICE}...", flush=True)
        bnb_cfg = BitsAndBytesConfig(load_in_8bit=True)
        model = AutoModel.from_pretrained(
            MODEL_ID,
            trust_remote_code=True,  # REQUIRED — custom PPLXQwen3ContextualModel
            quantization_config=bnb_cfg,
            device_map={"": DEVICE} if DEVICE == "cuda" else "cpu",
        )
    else:
        # DEFAULT bf16 path — byte-identical to the long-running production behavior.
        print(f"[pplx-embed] loading {MODEL_ID} on {DEVICE} dtype={DTYPE}...", flush=True)
        model = AutoModel.from_pretrained(
            MODEL_ID,
            trust_remote_code=True,  # REQUIRED — custom PPLXQwen3ContextualModel
            dtype=dt,
        ).to(DEVICE)
    model.eval()
    # MEMORY ENVELOPE BOUND (2026-06-15, lead) — ROOT CAUSE of the 8→15.5G balloon:
    # the model's encode() tokenizes with truncation=True but NO max_length (modeling.py:228-231),
    # so it truncates only at tokenizer.model_max_length, which defaults to 131072. A long transcript
    # = a ~30K-token sequence in one padded batch → the bidirectional (non-causal) forward's
    # MLP-intermediate activation (batch × seq × intermediate × 2B) spikes multi-GB → the CUDA
    # caching allocator reserves that peak as high-water (nvidia-smi 15.5G) and fragments → next
    # alloc stalls. Capping model_max_length makes truncation=True cut every input at EMBED_MAX_TOKENS,
    # hard-bounding the sequence (and thus the peak) for EVERY client — a server-side safety net under
    # any caller's own input cap. 8192 ≥ the backfill's ~6K-token input cap, so it only bites runaway inputs.
    max_tok = int(os.environ.get("PPLX_EMBED_MAX_TOKENS", "8192"))
    try:
        model.tokenizer.model_max_length = max_tok
    except Exception as e:  # fail loud — a silent un-cap is the balloon
        print(f"[pplx-embed] WARNING could not set model_max_length: {e}", flush=True)
    _state["model"] = model
    _state["max_tok"] = max_tok
    print(f"[pplx-embed] loaded in {time.time()-t0:.1f}s  model_max_length={getattr(model.tokenizer,'model_max_length',None)}", flush=True)


@app.get("/v1/models")
async def list_models():
    return {"object": "list",
            "data": [{"id": MODEL_ID, "object": "model", "owned_by": "perplexity-ai"}]}


@app.get("/health")
async def health():
    return {"status": "ok" if _state["model"] is not None else "loading",
            "dim": _state["dim"]}


@app.post("/v1/embeddings", response_model=EmbeddingResponse)
async def embed(req: EmbeddingRequest):
    if _state["model"] is None:
        raise HTTPException(503, "Model not loaded yet")

    # Build the documents-of-chunks structure the model requires.
    if req.documents is not None:
        docs = req.documents
        flat_meta = [(d_i, c_i) for d_i, doc in enumerate(docs)
                     for c_i in range(len(doc))]
    elif req.input is not None:
        # OpenAI flat mode: each input string = one single-chunk document.
        docs = [[t] for t in req.input]
        flat_meta = [(i, 0) for i in range(len(req.input))]
    else:
        raise HTTPException(422, "Provide either `input` (list[str]) or `documents` (list[list[str]]).")

    model = _state["model"]
    async with _state["lock"]:  # serialize GPU access
        # model.encode handles tokenization, late chunking, pooling, quantization.
        # batch_size bounds how many docs share one padded forward → bounds the activation peak
        # deterministically regardless of how many inputs a client sends (embeddings are identical
        # to any batch size — batching is purely a memory/throughput knob). Pairs with the
        # model_max_length cap to keep the forward's peak small enough for chat-4b co-residence.
        per_doc = model.encode(
            docs,
            batch_size=int(os.environ.get("PPLX_EMBED_BATCH", "8")),
            quantization=req.quantization,
            normalize_embeddings=req.normalize,
            convert_to_numpy=True,
        )  # list[np.ndarray], each (n_chunks, dim)
        # Return the spike's cached blocks to the driver so the reserved high-water drops back
        # between requests (with expandable_segments this lets embed give VRAM back to chat-4b).
        if DEVICE == "cuda":
            torch.cuda.empty_cache()

    # Flatten (document, chunk) → rows in input order.
    data = []
    idx = 0
    for d_i, doc_emb in enumerate(per_doc):
        for c_i in range(doc_emb.shape[0]):
            vec = doc_emb[c_i]
            if _state["dim"] is None:
                _state["dim"] = int(vec.shape[-1])
            data.append(EmbeddingData(
                embedding=[float(x) for x in vec.tolist()],
                index=idx,
                meta={"document": d_i, "chunk": c_i,
                      "quantization": req.quantization, "normalized": req.normalize},
            ))
            idx += 1

    n_inputs = len(docs)
    return EmbeddingResponse(
        data=data,
        model=MODEL_ID,
        usage={"prompt_tokens": n_inputs, "total_tokens": n_inputs},
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
