---
type: constitution
register: prescriptive
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

**Structured output + generation metadata (additive, schema-additive):** `_apply_response_format` is the ONE structured-output decision shared by both chat transports — `opts["json_schema"]` → `response_format {type:json_schema, json_schema:{name,schema}}` (server-side grammar-CONSTRAINED decode, vLLM xgrammar; VERIFIED the resident 4B both ACCEPTS *and* CONSTRAINS — a no-JSON prompt still returns conformant JSON) › `opts["schema"]`/`opts["json"]` → `json_object` (the unchanged existing path) › neither → free text. **WIRED END-TO-END (G24 — schema-guided decoding):** `client.complete(schema=<PydanticModel>)` now DERIVES `opts["json_schema"]` = `{"name": <class name>, "schema": schema.model_json_schema()}` itself (unless the caller passed `json_schema` explicitly — even `None`, the opt-out), so EVERY schema-declared call (a role's `output_schema` via `run_role`, coa's `CoaFraming`) gets the server-side constraint and the decoder CANNOT emit schema-invalid JSON — the G24 class (the resident 4B deterministically emitting unparseable role-JSON on some file contents, burning all retries into FabricError) is structurally closed; proven by re-firing `repo_digest` over the 3 known-failing files (runtime/bridge.py · roles/check.py · nodes/portal.py — all valid in ~0.5–0.7s vs ~15s of retry burn). Callers passing NO schema are byte-identical (the derivation keys on the `schema=` param alone); an endpoint that REJECTS json_schema errors → retry → FabricError (fail loud, never a silent downgrade); client-side parse/validate/retry in `complete()` REMAINS the guarantee (F9) — the constraint strengthens the decode, the guard stays the contract. `_fill_meta` is the ADDITIVE finish_reason + token-usage passthrough (O3): a caller passing `meta={}` in opts gets it filled IN PLACE from the response envelope (`choices[0].finish_reason` — `length`=truncated=invalid grammar output, the O3 signal; `usage` token counts) — invisible to the 12+ bare-content-string callers (no `meta` → no-op), never enters the request body, rides `**opts` straight through `client.complete()`. Enforcement stays client-side (`complete()` parse/validate/retry, F9); json_schema is a decode strengthening, `meta` is decoration — neither is the guarantee. Proven: `tests/json_schema_transport_acceptance.py`.

**Sampling-family passthrough (additive, single-source, allowlist-gated):** both chat transports forward sampling params into the request body through ONE shared helper — `_apply_sampling(body, opts)` over the `_SAMPLING_KEYS` **ordered tuple** (`temperature · max_tokens · top_p · repetition_penalty · frequency_penalty · presence_penalty · top_k · min_p · stop · seed · n`). It is an **ALLOWLIST, never a denylist** — the out-params + structured-output triggers (`meta`/`tools`/`tool_choice`/`json_schema`/`schema`/`json`) are NOT in the set, so they can never leak into the body (the meta-no-leak guarantee `_fill_meta` documents holds by construction); they are handled by `_apply_response_format`/`_fill_meta`/the tools branch. A key **absent** from `opts` is not added → the request is **byte-identical** for any caller not passing it (behaviour-preserving). It is an **ordered tuple with the original three first** ON PURPOSE: `_apply_sampling` inserts in this order and `json.dumps` serializes in dict-insertion order, so a call passing none of the new keys serializes byte-for-byte identically to the pre-change inline `(temperature, max_tokens, top_p)` loop (a hash-ordered set would reorder the bytes of any ≥2-key call — request-equivalent, but not literally byte-identical). This is the seam the generation-policy **rep_penalty LADDER** (`runtime/cognition.run_role(policy=)`) rides through to vLLM — the ladder selects the rung, the transport delivers it (vLLM accepts `repetition_penalty` — proven live); the rest of the family rides the SAME seam, so a policy declaring any of them reaches the REQUEST BODY with no further transport edit (registry-driven/general, not a single hardcoded key; an endpoint that doesn't recognise a field ignores it). No current caller passes any of the widened keys, so the broadening is inert for today's callers (verified). Replaced the two duplicated inline `(temperature, max_tokens, top_p)` copy-loops (reuse, not parallel — the two transports agree by construction). Proven: `tests/transport_rep_penalty_acceptance.py` (real-transport body capture + live :8000 accept + end-to-end ladder→body).
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
