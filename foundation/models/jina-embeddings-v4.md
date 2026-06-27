---
type: model
id: jinaai/jina-embeddings-v4
filename: jina-embeddings-v4
status: deployed
runtime: jina-v4-env
port: 8002
date_added: 2026-05-26
date_last_characterised: 2026-05-27
tags: [foundation, models, embedding, multimodal, deployed]
---

# Jina Embeddings v4

> [[_models-index|← Models hub]] · linked from: multimodal text+image+visual-documents

## At a glance

| Field | Value |
|---|---|
| HF id | `jinaai/jina-embeddings-v4` |
| Disk | 7.4 GB |
| Quant | BF16 |
| Architecture | `JinaEmbeddingsV4Model` (dynamic HF module + peft LoRAs) |
| Embedding dim | 2048 |
| Tasks | `retrieval`, `text-matching`, `code` (LoRA-adapter-selected) |
| Prompt modes | `query`, `passage` (instruction-aware) |
| Native context | 32,768 tokens |
| Modality | text + image + visual documents (PDFs with layout, charts) |
| Service unit | `vllm-jina-v4.service` |
| Endpoint | `http://localhost:8002/v1` |

## Source

Pulled 2026-05-26 as the multimodal embedding option. Originally targeted vLLM, but vLLM 0.21 does not support the `JinaEmbeddingsV4Model` architecture (the v5 architecture is supported; v4 uses dynamic HF modules + peft LoRAs that vLLM's loader doesn't handle).

Resolved by serving via a dedicated Python venv (`~/jina-v4-env/`) pinning `transformers<5.0`, plus `Pillow` and `torchvision`. The v4 model's bundled `qwen2_5_vl.py` accesses a ROPE init key (`'default'`) that transformers 5.x removed — the version pin is the fix.

## Fits these needs

- [[_models-index#Multimodal: text + image|Multimodal: text + image]] — embedding-side; pairs naturally with [[qwen3_5-4b-awq]] for the generation-side
- [[_models-index#Multimodal: text + image + visual documents (charts, PDFs with layout)|Multimodal: text + image + visual documents]] — designed for this; the only model on the substrate explicitly built for it

## Tested performance

Verified loading and producing coherent embeddings 2026-05-27. Semantic check:

| Pair | Cosine sim |
|---|---|
| "hello world" vs "goodbye world" | 0.597 |
| "hello world" vs "some unrelated finance topic" | 0.433 |

2048-d embeddings, BF16 weights to CUDA. Single-stream encode of one text: ~5.4s on first call (model loading) — subsequent calls fast (not measured precisely).

Concurrent throughput: not benchmarked. The current FastAPI server (`~/vllm-tests/serve_jina_v4.py`) serialises GPU access with a global asyncio lock, which caps concurrency at 1; this is a deliberate simple-server choice, not a model limitation.

## Known-good launch config

Defined in `~/vllm-tests/serve_jina_v4.sh`; managed by `~/.config/systemd/user/vllm-jina-v4.service`.

The launcher activates `~/jina-v4-env/` (not the main vllm-env) and runs `python ~/vllm-tests/serve_jina_v4.py`. The server:

- Loads via `AutoModel.from_pretrained(MODEL_ID, trust_remote_code=True, torch_dtype=torch.bfloat16)`
- Exposes OpenAI-compat `/v1/embeddings` and `/v1/models`
- Accepts the OpenAI body plus `task: retrieval|text-matching|code` and `prompt_name: query|passage`
- Returns dense embeddings (multi-vector mode supported in the model but not exposed by this server yet)

## Quirks

- **Lives in its own venv** because of `transformers<5` requirement. Cannot share vLLM's venv. The two venvs share the system CUDA libraries but maintain independent Python deps.
- **Task adapters via LoRA.** Same base model loads three task-specific LoRAs (`retrieval`, `text-matching`, `code`). Wrong-task selection produces lower-quality embeddings for the use case.
- **Instruction-aware.** Query side uses `prompt_name: query`; document side uses `prompt_name: passage`. Asymmetric — applying query prompts to documents (or vice versa) is a quality bug.
- **Single-process GPU access.** The serving lock is a server-side simplification. For higher concurrency, batch larger lists into single requests (the model handles batches efficiently) or rewrite the server with proper request batching.
- **Co-resident with vLLM defaults.** Verified running alongside [[qwen3_5-4b-awq]] and [[bge-m3]] at ~15.5 GiB total VRAM.

## Open at this entry

- Concurrent throughput unmeasured. The server-lock pattern means this is a server-shape question, not a model question — measure with a request-batching server.
- Multi-vector output mode supported by the model but not exposed by this server. Adding it changes the JSON response shape.
- Visual-document use cases (PDFs with layout, charts, tables) not exercised end-to-end. The capability is what justifies this model's existence on the substrate.
- Comparison vs [[bge-m3]] on pure-text retrieval — open; v4 may be overkill for text-only use cases.
- Comparison vs [[jina-embeddings-v5-text-small]] on the v5-supported text-only variant.

## Connects to

- [[_models-index]] — hub
- [[../operations/runtimes]] — `jina-v4-env` runtime; why it exists
- [[qwen3_5-4b-awq]], [[bge-m3]] — co-resident services
- [[jina-embeddings-v5-text-small]] — text-only sibling, vLLM-compatible
- Source: server at `~/vllm-tests/serve_jina_v4.py`; launcher at `~/vllm-tests/serve_jina_v4.sh`
