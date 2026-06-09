---
type: constitution
module: fabric
aliases: ["fabric — constitution"]
tags: [company, constitution, fabric, models]
governs: [S6]
relates-to: ["[[Company Map]]", "[[runtime — constitution]]", "[[nodes — constitution]]"]
status: living
---

# fabric/ — module constitution

**Is:** the model binding — one endpoint over LiteLLM + llama-swap + adapters, with the reliability guards. The "engine beneath" the runtime calls (S6).
**Guarantees:** **every** model call is guarded — non-empty-content check + JSON-repair-retry + cloud backoff (the `fabric.py` lessons; kimi/glm return empty). VRAM decisions read **live `nvidia-smi`**, never an internal ledger. Structured output validated or **fails loud** (LiteLLM+ollama can silently drop `response_format` — probe `supports_response_schema`). **NO Gemini.**

**Structured output + generation metadata (additive, schema-additive):** `_apply_response_format` is the ONE structured-output decision shared by both chat transports — `opts["json_schema"]` → `response_format {type:json_schema, json_schema:{name,schema}}` (server-side grammar-CONSTRAINED decode, vLLM xgrammar; VERIFIED the resident 4B both ACCEPTS *and* CONSTRAINS — a no-JSON prompt still returns conformant JSON) › `opts["schema"]`/`opts["json"]` → `json_object` (the unchanged existing path) › neither → free text. `_fill_meta` is the ADDITIVE finish_reason + token-usage passthrough (O3): a caller passing `meta={}` in opts gets it filled IN PLACE from the response envelope (`choices[0].finish_reason` — `length`=truncated=invalid grammar output, the O3 signal; `usage` token counts) — invisible to the 12+ bare-content-string callers (no `meta` → no-op), never enters the request body, rides `**opts` straight through `client.complete()`. Enforcement stays client-side (`complete()` parse/validate/retry, F9); json_schema is a decode strengthening, `meta` is decoration — neither is the guarantee. Proven: `tests/json_schema_transport_acceptance.py`.
**Where new things go:** a new model/provider = a **config entry generated from the registry** (not hand-edited); a new capability-type = an adapter (rerank/layout/etc.).
**To extend:** add to the generated LiteLLM/llama-swap config via the registry; or add a capability adapter behind the unified verb.
**Seam:** called by [[runtime — constitution]]; configured from the type/model registry; the RHM brain is one swappable model slot here (D2).
**Never:** call a model without the guards · hardcode a provider/key · trust a VRAM ledger over the card · use Gemini.

## What's in here

The model binding itself: the guarded call path, plus the **model registry** that backs
`list_models`. The binding speaks **OpenAI-compatible** to whatever sits behind it —
ollama / LiteLLM / cloud providers — so the rest of the system names a model and never
learns which backend serves it. Around that sit the **guards** (non-empty-content check,
JSON-repair-retry, cloud backoff, structured-output validation) and the **VRAM
semaphore**, which gates local model loads against **live `nvidia-smi`** so two heavy
models don't collide on the card. The registry is the single source the authoring prompts
read to know what they may call; the **live, complete model list lives in [[Company Map]]**
(do not duplicate it here — that's the rule in [[Vault Conventions]]).

## Relates to

- **Called by** [[runtime — constitution]] — the scheduler dispatches every model call
  through this binding when a node needs one.
- **Called by** the AI nodes in [[nodes — constitution]] (`llm`, `ask`, `pair`…) — they
  call models through these guards rather than reaching a provider directly.
- **Provides** the model registry that the authoring prompts read, so an authoring step
  picks from what actually exists rather than guessing.

## Read next
[[Company Map]] (the live model list + the whole picture) · [[runtime — constitution]] (what dispatches these calls) · [[Concepts and Principles]] (why the binding is shaped this way).
