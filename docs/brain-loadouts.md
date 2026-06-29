---
type: howto
register: descriptive
aliases: ["Brain Loadouts", "FP8 brain how-to", "how to use the local brain"]
tags: [brain, loadout, fp8, vllm, rhm, ops]
status: confirmed
relations:
  operated-by: "[[company — console]]"
  serves: "[[runtime/bridge — the RHM surface]]"
  declared-in: "ops/services.json (combos + chat-4b-fp8 / chat-9b-fp8)"
  resolved-by: "[[runtime/capabilities — the resolver]]"
coverage: {verified_live: "2026-06-30", by: "real bridge /api/chat + /api/cognition/run_role turns + company gpu measured; enable_thinking both directions on the FP8"}
---

# Brain Loadouts — how to use (and extend) the local RHM brain

*The everyday brain is the **FP8 Qwen3.5-4B**, thinking + tools, with strong recall + voice co-resident. Everything below is operated through the `company` console + the bridge `/api` — no scripts, no raw `vllm`. Verified live 2026-06-30.*

**One active brain.** Whatever brain service is *loaded* is THE active brain, and everything that fires a brain resolves to it — the RHM chat AND the swarm/`run_role`/cascades (via `cognition.active_brain()`, which reads the running brain service). A loadout switch moves which brain runs → everything follows it the next call; no port is ever pinned to a stale default. So you never have to point sub-systems at the brain by hand — load it, and it's used.

## TL;DR (the two loadouts)
| Loadout | Brain | Context | Co-resident | Bring up |
|---|---|---|---|---|
| **`@interaction-fp8`** (everyday) | Qwen3.5-4B-FP8 (:8001), thinking+tools | **4×16K = 65,536** (fp8-KV) | strong recall embedder (pplx) + voice + ear | `company up @interaction-fp8` |
| **`@quality-9b`** (the better brain, solo) | Qwen3.5-9B-FP8 (:8002), thinking+tools | 16K (raise as needed) | none — fills the card | `company up @quality-9b --evict` |

"16K = your 1 unit." The everyday brain is at **4 of those**; the 9B and a solo deep loadout can go much higher (see *Context*).

## Bring it up
- **Everyday brain + recall + voice:** `company up @interaction-fp8` — resource-gated; brings up the FP8-4B brain (:8001), embed-pplx (recall), tts-kokoro (voice), stt-moonshine (ear). ~15.1/16 GB. The RHM is already pointed at it.
- **Switch to the 9B (quality/judging):** `company up @quality-9b --evict` — evicts the interaction loadout (the 9B fills the card), starts the 9B solo, **and auto-repoints the RHM to the loadout's brain** (the [[project-loadout-resolution|atomic loadout-switch]] — the RHM brain now FOLLOWS the loadout, on both the `company up @loadout` CLI door and the confirm-gated mode→loadout door). The switch is verified by a live probe and **reverts** if the new brain doesn't answer (fail-loud, never a silent broken brain). Switching back is symmetric: `company up @interaction-fp8 --evict`. If the bridge is down during a CLI switch the repoint can't happen (the RHM pointer is persisted + read at next start) — the CLI prints the exact manual fix (`curl :8770/api/rhm-config -d '{"model":…,"base_url":…}'`) rather than leaving a silent stale pointer.
- **Status / budget:** `company status`, `company gpu` (measured VRAM), `company combos` (list loadouts).

## Talk to it
Through the surface (canvas) or the bridge API — `POST :8770/api/chat {"message":"…","graph_id":"codebase"}`. **Response shape differs by surface** (the trap to know): the **bridge `/api/chat`** returns the reply at the **TOP LEVEL** — `{reply, action, proposal, mode, model, history}` (NO `message` wrapper); the **MCP `chat` tool** wraps it under `message` (`message.reply`/`message.reasoning`). When thinking is on, the private reasoning rides `reasoning` (NOT `reasoning_content`). Tools fire natively (the brain acts through governed verbs).

## Thinking (on/off) — per-run, per-role, per-family
The brain thinks **per-turn**, gated to a model that DECLARES the `thinking` capability (the FP8 does; the no-think AWQ doesn't). The everyday chat default is OFF (snappy). Verified live on the FP8: `enable_thinking:false` → 0 reasoning + a direct answer; `enable_thinking:true` → a full reasoning trace (and a hard multi-step task went wrong→right with it on — so reserve thinking for judge/act/decide, keep chat snappy). Three ways to turn it on, finest to coarsest:
- **Per RUN (an agent, one fire):** `run_role(role=…, think=true)` — the MCP tool + `cognition.run_role` both take `think`; it routes to `enable_thinking` on vLLM (or `body.think` on ollama). The easiest knob.
- **Per ROLE (persistent):** declare `"thinking": true` in the role's spec (`roles/<id>.py`) or via `edit_role`. A thinking role then reasons every fire (e.g. `refine_decision`).
- **Resting chat default:** `POST :8770/api/rhm-config {"think": true|false}`.

## Sampling — per-FAMILY defaults, per-role / per-run override (the "Both")
Sampling is **model-family-bound, not hand-set per call**. A family declares its recommended profile ONCE in `runtime/capabilities/family_capabilities.json` (`qwen3.5` → `default {0.7/0.8/20}` + `thinking {1.0/0.95/20}`, presence_penalty 0 = the precise/structured profile for a tool-caller). At call-time the active brain's family supplies the BASE (think-aware), and per-role knobs + per-call kwargs OVERRIDE it (override wins). So:
- **A Qwen3.5 thinking role automatically samples at temp 1.0/0.95/20** (no per-role re-declaration); a non-thinking role keeps temp 0 (deterministic swarm); a kimi role gets kimi's sampling, not Qwen3.5's.
- **Override per role:** `"knobs": {…}` in the role spec (top_p/top_k/min_p/presence_penalty/frequency_penalty/repetition_penalty/temperature/max_tokens). **Per run:** pass them to `run_role`. **Chat resting:** `POST :8770/api/rhm-config {"brain_knobs": {…}}`.
- The chat everyday knobs are LIVE-set to the qwen3.5 non-thinking spec; verify with `GET :8770/api/rhm-config`.

## Context (the "units" lever)
- Set the window: `company config chat-4b-fp8 max_model_len <N>` then `company restart chat-4b-fp8`. Capped by the model's 262,144 ceiling AND by VRAM (the KV-cache grows with context).
- The everyday brain is **65,536 (4 units)**, co-resident. **fp8-KV** (`kv_cache_dtype: fp8`, on) halves the per-token KV → ~2× the context per GB (measured KV budget 92,698→149,211 tokens at gpu_util 0.6, near-lossless; tiny long-prompt prefill cost on this Ada card, decode unaffected).
- **For more context:** solo (`@quality-9b` or a deep-4B loadout) frees the VRAM the embedder eats → ~10–16 units. Co-resident with the strong embedder caps it (~4–5 units) — context and co-residence trade against each other on the 16 GB card.

## Work declares the loadout it requires (loadout-resolution — BUILT)
A unit of work (a saved cascade/action) can declare `requires: <loadout_class>`. On invocation the system resolves it against the LIVE loadout; if a needed service is missing it SURFACES a `loadout_swap` confirm (the governed door that loads + **repoints the RHM**) and FAILS LOUD — the work never runs against the wrong loadout (no silent degrade). The operator approves, then re-runs. So the "first uses" are now a declaration, not a manual step: a recall-heavy action `requires: <a loadout with the reranker>`, a judging action `requires: quality-9b`, etc. (Manual pulls still work: `company up rerank-jina` / `company up tts-kokoro` — the resource gate checks fit. The everyday loadout drops the reranker to fit the FP8-4B; pull it in on demand.)

## It's all through the system
Serving is `serve_model.sh` via systemd (launched by `company up`, resource-gated). The serve flags (incl. `--kv-cache-dtype fp8`, `--reasoning-parser qwen3`) are **generated by the resolver from the registry** (`runtime/capabilities/` + the service's `family qwen3.5` + `capability_overrides`) — not hardcoded; tune with `company config` + `company restart`. Talking, thinking, loadout switches = the `company` console + the bridge `/api`. The only non-repo dependency is the benchmark script (`~/vllm-tests/bench.py`, wrapped by `company bench`).

## Easy to extend — the registry seams (add a thing = one edit, no code)
Everything above resolves from declared registries; extending is a row, not a rewrite:
- **A new model / family** → add a `family: <name>` row in `runtime/capabilities/family_capabilities.json` (its `capabilities`/`serve_params` → serve flags via the resolver, its `sampling.{default,thinking}` → the per-request base). A model declares `family: <name>` in `ops/services.json` and inherits the whole set. No code edit lights up its serve flags + sampling.
- **A new loadout** → add a combo in `ops/services.json` (or a `extends`/`swap`/`add`/`remove` variant). `company up @<name>` brings it up; the brain in it becomes the active brain (RHM + swarm follow).
- **Tune a brain's sampling for everyone on its family** → edit that family's `sampling` block (registry-is-truth; every model on the family inherits). Override for one role via its `knobs`; for one run via `run_role` kwargs.
- **Make a role reason** → `"thinking": true` (+ optional `knobs`) in its spec, or `run_role(think=true)` for one fire.
- **Gate work on a loadout** → add `requires: <loadout_class>` to the cascade/action; the resolve-gate + the repointing switch are already wired.
- **The acceptance suites that lock this in:** `tests/{family_sampling,role_knobs,active_brain_resolution,loadout_switch_repoint,action_requires_gate,capability_resolver}_acceptance.py`.
