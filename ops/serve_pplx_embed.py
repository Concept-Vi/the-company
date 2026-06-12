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


@app.on_event("startup")
def load_model():
    dt = _DTYPES.get(DTYPE, torch.bfloat16)
    print(f"[pplx-embed] loading {MODEL_ID} on {DEVICE} dtype={DTYPE}...", flush=True)
    t0 = time.time()
    model = AutoModel.from_pretrained(
        MODEL_ID,
        trust_remote_code=True,  # REQUIRED — custom PPLXQwen3ContextualModel
        dtype=dt,
    ).to(DEVICE)
    model.eval()
    _state["model"] = model
    print(f"[pplx-embed] loaded in {time.time()-t0:.1f}s", flush=True)


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
        per_doc = model.encode(
            docs,
            quantization=req.quantization,
            normalize_embeddings=req.normalize,
            convert_to_numpy=True,
        )  # list[np.ndarray], each (n_chunks, dim)

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
