# Model-Routing Unification — Research Synthesis (the CATCHMENT)
*Authored by the lead (ch-al7jdfdr) 2026-06-16, from a wide read of the codebase (5 parallel explorer waves). Tim's frame: "core … unify it into the ONE mechanism … getting the catchment is important and knowing what there is to build." This doc is the catchment: every place a model is chosen, today. Written confidently but provisional — Tim is the sole judge of "right"; verify each file:line before building on it.*

## THE FINDING IN ONE LINE
Model selection is scattered across ~50 points in 5 regions, **but a registry-is-truth foundation already exists** (`ops/model_capabilities.json` + `capability_providers()` + `resolve_role`/`resolve_binding`). The opportunity is not to BUILD a router — it's to make every selection point ROUTE THROUGH the one that's already there, and fill the gaps (the cognition engine bypasses it; the interactive brains don't use it; many knobs live outside it).

## THE TWO "BRAINS" (the core confusion Tim's instinct caught)
- **RESIDENT_MODEL** (`runtime/cognition.py:54`) = `cyankiwi/Qwen3.5-4B-AWQ-4bit` @ `:8000` (LOCAL 4B). Governs **the cognition engine** — `run_swarm` / `run_jury` / `run_panel` / `run_reduce` / `run_composition`. **This is the "too stupid to build complex" brain — it is doing JUDGE/SYNTHESIS work, not just extraction.**
- **DEFAULT_BRAIN** (`fabric/config.py:21`) = `deepseek-v4-pro:cloud` (CLOUD, strong). Governs the **conversation/RHM layer** — chat, consult, `ask`/`llm` nodes. NOT the problem; changing it does nothing for the engine (proven — it's a different layer). [Tim flagged `-pro`-as-default separately; that's a registry-default question, not this build's core.]

## REGION 1 — THE COGNITION ENGINE (the build-brain culprit)
`runtime/cognition.py`. Every primitive defaults to RESIDENT (4B) and the per-role bindings are **bypassed**:
- `run_role` (203), `run_swarm` (1056), `run_jury` (1730), `run_panel` (1811), `run_reduce` (1998), `run_composition` (minds.py:231) → all `base_url=RESIDENT_BASE_URL, model=RESIDENT_MODEL`.
- `run_cascade` (2244) ALREADY receives a `resolve_role` kwarg (suite.py:1267) but pins `RESIDENT_BASE_URL` (2344) with an **outdated** comment "cloud routing = N2 net-new transport."
- Caller `chat_parts` (suite.py:6594) fires `run_swarm` with **no** model/base_url → all cast roles on the 4B.
- **Extractor vs judge/synthesis roles** (the taxonomy that should drive routing): extractors e.g. `focus.py` (fan-out, 4B-fine); judges/synth e.g. `judge.py`, `reduce_synth.py`, `triad_synth.py`, `score_options.py` (need wide knowledge → cloud). They DECLARE `requires=[...]` but it is never queried in the swarm.

## REGION 2 — THE REGISTRY FOUNDATION (exists, partly used)
- `ops/model_capabilities.json` — THE model catalog (every model + provides-tags + window + local/cloud). Registry-is-truth (AGENTS.md rule 8).
- `capability_providers()` (suite.py:5849) — live providers {model, base_url, provides, resident} from services.json + capabilities.
- `resolve_binding(role, providers)` (roles.py:307) — capability-query matcher: `role.requires ⊆ provider.provides`, RAISES on no-match.
- `resolve_role(role_id)` (suite.py:5806) — precedence chain: config > env > role.default_model > brain. Returns {model, base_url, knobs, ...}.
- `resolve_role_binding()` (suite.py:5918) — wraps the two — **defined but NEVER CALLED by the engine.**
- Role `model_binding` schema (roles.py:71): `{requires:[caps], default_model, recommended_model, recommended_reason, env_model, env_url, env_knobs}`.
- **Gap:** providers don't declare fine-grained caps (`fast`/`no-think`/`reasoning`/`wide`) yet, so capability-queries can't distinguish tiers. The taxonomy isn't encoded in the registry.

## REGION 3 — INTERACTIVE / CC-SESSION / CLONE BRAINS
- **Loadable/builder brain**: `runtime/ui_claude_session.py:run_turn` → bare `claude -p`, **NO `--model`** → host Anthropic account model (capable). `/api/claude/turn` (bridge.py:1633). Model is NOT chosen in code.
- **Clones**: `runtime/cc_clone.py` — context-aware pick (`_pick_ollama_model` 193, `_estimate_context_tokens` 155): `KIMI_OLLAMA_MODEL=kimi-k2.7-code:cloud` (256K, 150), `OLLAMA_BIG_CTX_MODEL=deepseek-v4-flash:cloud` (1M, 152), `KIMI_MAX_CTX=262144` (151). Provider routing via supervisor `_build_spawn_cmd` (session_supervisor.py:613, ollama-launch path 651, PATH-fix 854). **This is the only context-size-aware router that exists — generalize it.**
- **Self-build**: `runtime/implement.py:320` → `claude -p`, NO `--model` → host account.
- **territory_for** (runtime/territory.py): model-agnostic (feeds context, doesn't pick the model).

## REGION 4 — NON-CHAT MODELS + LOADOUTS (mostly already registry-driven)
- **Embeddings**: `fabric/config.py` DEFAULT_EMBED_URL/MODEL/DIM + `DEFAULT_EMB_LAYER` + `resolve_emb_layer()` (the pplx switch, just landed). store/vector_index.py threads `emb`.
- **Rerank**: `ops/rerank.py` (jina-v3 + ms-marco), `runtime/corpus_rerank.py` (:8008, hardcoded URL line 35), CPU/0-VRAM.
- **Voice/TTS + STT**: `voice/personas.py` (persona→engine), `voice/stt.py` (STT_DEFAULT=whispercpp), per-engine model consts. Registry-style already (persona/engine registries).
- **Mode loadouts**: `ops/services.json` groups (small-pair, wake, xsession, xsession-brain, instrument) — which model SERVICES are resident per mode; `ops/cli/app.py` (up/down/restart/swap + gpu fit/evict). The resident-set selector.

## REGION 5 — THE SCATTERED KNOBS (what the ONE mechanism must absorb)
Config consts: `DEFAULT_BRAIN`, `DEFAULT_BASE_URL`, `LITELLM_PROXY`(:4100), `OLLAMA_DIRECT`(:11434), `DEFAULT_EMBED_*`, `RESIDENT_MODEL`/`RESIDENT_BASE_URL`. litellm.config.yaml aliases (brain/deepseek-v4-pro/deepseek-v4-flash/local-4b/…). Per-role env (only `judge` declares `COMPANY_JUDGE_MODEL`/`_URL`). **Hardcode: `bridge.py:1064` `deepseek-v4-pro:cloud`** in the "ask the codebase" node. Clone consts (cc_clone.py:150-152). CI scaffold defaults (ci_scaffold.py:32/53 `opus`). FABLE_MODEL (session_lens.py:44, legacy).

## CONFLICTS / DUPLICATES FLAGGED
- Two "brains" (RESIDENT vs DEFAULT_BRAIN) with different purposes, not obvious from names.
- `bridge.py:1064` hardcodes `-pro` (against Tim's "never default to -pro").
- Embedder: pplx (2560, live) vs bge (1024, dormant) — `resolve_emb_layer` adds a parallel selector to the model-selection problem (same shape: pick layer/model by intent).
- Clone model namespaces: ollama-cloud (kimi/deepseek-flash) vs Anthropic (opus/sonnet/haiku) vs legacy Fable — only ollama is context-aware.
- Reranker URL hardcoded (corpus_rerank.py:35), no env.

## THE TRANSPORT VERDICT (decides how hard C is)
**Thread-through, NOT net-new.** `fabric/client.py:complete(transport, ...)` takes a transport closure pre-bound to a base_url; `openai_transport(base_url)` (transport.py) builds it per-call. So routing a step to a cloud model = call `resolve_model(intent) → {model, base_url}` → `openai_transport(base_url)` → done. No new broker/endpoint/auth. The "N2 net-new" comment is outdated. (One caveat to verify by use: kimi-k2.7-code is a REASONING model — its `/v1/chat` returns content in `message.content` with a separate `reasoning` field; needs adequate max_tokens. Verified working 2026-06-16.)

## IMPLICATION FOR THE BUILD
The mechanism mostly EXISTS (resolve_role + capability_providers + the registry). The build is: (1) make it ONE entry point that resolves by INTENT (role/step/session/service + capabilities + tier + context-size); (2) encode the extractor/judge tiers in the registry (registry-is-truth); (3) route the bypassing points through it (the engine primitives, the interactive brains); (4) absorb the scattered knobs/hardcodes as registry defaults. See IMPLEMENTATION_GUIDE.md.
