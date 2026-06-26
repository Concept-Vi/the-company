# Model-Routing Unification — Implementation Guide (the ONE mechanism)
*Provisional design. The principle (Tim): unify all model selection into ONE registry-is-truth mechanism resolved by INTENT. Build phased + backward-compatible; verify by use at each phase. The cognition engine is a HOT lane (R13's "run_swarm byte-identical" discipline holds).*

## THE PRINCIPLE — one resolver, intent in, {model, base_url, provider} out
Every model-selection point becomes a call to ONE entry:

```
resolve_model(intent) -> {model, base_url, provider, why}
  intent = {
    kind: "role" | "step" | "session" | "clone" | "service",
    role_id?,                # for role/step: the role (carries model_binding.requires + tier)
    requires?: [caps],       # explicit capability query (else from the role)
    tier?: "extractor" | "judge" | "build" | "wide",   # the extraction-vs-judgment axis
    context_tokens?,         # for session/clone: drives the window-aware pick
    service?,                # for service: embed | rerank | tts | stt
    explicit_model?,         # honoured verbatim if the caller pins one
  }
```
- It is the SINGLE place the registry (`model_capabilities.json` + `capability_providers()`) is consulted. It SUBSUMES `resolve_role`, the cc_clone context-picker, and the scattered consts.
- **registry-is-truth**: which model satisfies a (requires+tier) lives in `model_capabilities.json`, never in code. Re-tiering a role = a registry/role-binding edit, ZERO engine code.
- **fail-loud**: an unresolvable intent RAISES (never a silent wrong-model fallback). Reuse `resolve_binding`'s raise-on-no-match.

## THE EXTRACTION-VS-JUDGMENT AXIS (Tim's law, encoded as registry data)
The 4B is the **extractor** (fan-out, cheap, high-volume); a wide-knowledge cloud model is the **judge/builder** (central, few). Encode this as capabilities + tiers in the registry, NOT hardcode:
- Providers declare fine-grained `provides`: the 4B provider gets `[chat, json, fast, no-think]`; a cloud brain (kimi) gets `[chat, json, reasoning, wide, code]`.
- Roles declare their tier via `requires`: `focus`/extractors → `[chat, json, fast]` (resolve → 4B); `reduce_synth`/`triad_synth`/`judge`(build-judge) → `[chat, reasoning, wide]` (resolve → cloud).
- So routing is a capability match — change a role's `requires` and it re-tiers. Cost stays sane (many extractors local, few judges cloud).

## SEQUENCE OF OPERATIONS (one RHM turn, after the build)
1. `chat_parts` → `cast_for_mode` → roles.
2. `run_swarm(roles, …, resolve=resolve_model)` → per role: `resolve_model({kind:role, role_id})` → extractor roles → 4B (`:8000`), judge/synth roles → cloud (kimi via `:11434`/`:4100`).
3. Each role's call builds `openai_transport(base_url)` from the resolved base_url; `complete(transport, …, model)`.
4. `run_reduce(mode=role)`/`run_jury`/`run_composition` synth steps → `resolve_model({kind:role, role_id})` → cloud.
5. The `run://` trail records each step's model → verify-by-use shows extractors on 4B, judges on cloud in ONE turn.

## PHASED ADOPTION (backward-compatible; each phase shippable + verifiable)
**Phase 1 — the resolver + the registry tiers (foundation).**
- NEW `runtime/model_routing.py`: `resolve_model(intent)` wrapping `resolve_role`/`capability_providers`/`resolve_binding` (REUSE, no new logic) + the context-size pick (generalized from `cc_clone._pick_ollama_model`).
- Populate `ops/model_capabilities.json` provider `provides` with the fine-grained caps (fast/no-think/reasoning/wide); add tier guidance. Declare the 4B and the cloud brain(s) as providers in `capability_providers()`.
- NO behaviour change yet (nothing routes through it). Unit-verify the resolver returns 4B for extractor-intent, cloud for judge-intent, the right model for context-size.

**Phase 2 — route the cognition engine through it (the build-brain fix).**
- Add optional `resolve=None` kwarg to `run_role`/`run_swarm`/`run_jury`/`run_panel`/`run_reduce`/`run_composition` (cognition.py / minds.py). If `None` → RESIDENT defaults (BYTE-IDENTICAL — the R13 discipline). If passed → per-role `resolve_model({kind:role, role_id})` → unpack {model, base_url}.
- `chat_parts` (suite.py:6594) passes `resolve=resolve_model`. Now judge/synth roles run cloud, extractors stay 4B.
- Remove the outdated "N2 net-new" pin in `run_cascade` (2344) — thread the resolved base_url through.
- Verify by use: a real turn → `run://` trail shows the split; `run_swarm` diff shows only the kwarg added.

**Phase 3 — route the interactive/CC brains + clones through it.**
- Clones: fold `cc_clone._pick_ollama_model` INTO `resolve_model({kind:clone, context_tokens})` (one picker, not two). cc_clone calls the unified resolver.
- Loadable/builder brain (`run_turn`): give `/api/claude/turn` an intent → `resolve_model({kind:session, tier:build})` → pass `--model`/provider to the spawn (via the supervisor's ollama-launch path) so the builder runs on a wide brain (kimi) by default, not the account default. (This is what Tim's "build brain" directive ultimately wants on the FACE loadable brain.)
- Self-build (`implement.py`): same — resolve a build-tier model.

**Phase 4 — absorb the scattered knobs (the unification's tail).**
- `bridge.py:1064` hardcoded `-pro` → `resolve_model({kind:role, role_id:answer})` (registry-driven).
- The config consts (DEFAULT_BRAIN, RESIDENT_MODEL) become registry DEFAULTS that `resolve_model` reads, not independent knobs. litellm aliases stay as the transport routing, fed by the registry.
- The reranker URL (corpus_rerank.py:35) gets an env/registry entry.

## DO / DON'T (with the because)
- **DO reuse** `resolve_role`/`capability_providers`/`resolve_binding` — the mechanism exists; wrap, don't re-implement (reuse-don't-parallel; a 2nd router is the exact anti-pattern Tim's unifying away).
- **DON'T break `run_swarm` byte-identical** when no resolver is passed — R13's harness discipline; the default path must be unchanged (diff-verifiable).
- **DON'T route the WHOLE swarm to cloud** — only judge/synth tiers. Extractors stay 4B (cost + the extraction-vs-judgment law). Routing N fan-out roles to cloud per turn is the expensive mistake.
- **DON'T cross embedder dims** — the embed-layer selection (`resolve_emb_layer`) is the SAME shape (pick-by-intent) but stays its own resolver for now; do NOT merge dims (pplx-2560 ≠ bge-1024). Note the parallel; unify the *pattern*, not the *vectors*.
- **DON'T silently fall back** to a wrong model on no-match — RAISE (fail-loud), surface a Notice + Gap.
- **DO verify kimi via `/v1/chat` with adequate max_tokens** (it's a reasoning model; tiny max_tokens yields empty `content`). Verified working 2026-06-16.

## FILE PATHS + ROLES
- NEW `runtime/model_routing.py` — `resolve_model(intent)` (the one entry; wraps existing resolvers + the context-size pick).
- MODIFY `runtime/cognition.py` — add `resolve=None` to the 6 primitives; per-role resolve when passed; KEEP RESIDENT defaults.
- MODIFY `runtime/minds.py` — thread `resolve` through `run_composition` → `run_swarm`.
- MODIFY `runtime/suite.py` — `chat_parts` passes `resolve`; `run_cascade` per-step resolve; lift the RESIDENT_BASE_URL pin.
- MODIFY `ops/model_capabilities.json` + `capability_providers()` — declare providers + fine-grained `provides` + tiers (registry-is-truth).
- MODIFY (Phase 3) `runtime/cc_clone.py` (call the unified resolver), `runtime/ui_claude_session.py`/`bridge.py` (intent → model for the loadable brain), `runtime/implement.py`.
- MODIFY (Phase 4) `runtime/bridge.py:1064`, `fabric/config.py` (consts → registry defaults), `runtime/corpus_rerank.py:35`.
- REFERENCE (don't change): `roles/*.py` model_binding (the per-role `requires`/tier declarations — author these as the routing data), `fabric/client.py`/`transport.py` (transport already parametric — no change).

## OWNERSHIP / SEAMS (fabric)
Core engine (cognition.py/suite.py/minds.py) = lead/fork co-scoped (hot lane, R13 discipline). The registry/capabilities (model_capabilities.json, capability_providers) = composition/lead (registry-is-truth is composition's domain). The clone/interactive path = fork. The voice/embed/rerank service registries = already registry-driven (recollection/voice owners), folded into the *pattern* not rewritten. Meet at `resolve_model`.
