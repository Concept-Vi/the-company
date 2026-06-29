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
coverage: {verified_live: "2026-06-29", by: "real bridge /api/chat turns + company gpu measured"}
---

# Brain Loadouts — how to use the local RHM brain

*The everyday brain is the **FP8 Qwen3.5-4B**, thinking + tools, with strong recall + voice co-resident. Everything below is operated through the `company` console + the bridge `/api` — no scripts, no raw `vllm`. Verified live 2026-06-29.*

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
Through the surface (canvas) or the bridge API — `POST :8770/api/chat {"message":"…","graph_id":"codebase"}`. The reply is `message.reply`; when thinking is on, the private reasoning is `message.reasoning` (NOT `reasoning_content`). Tools fire natively (the brain acts through governed verbs).

## Thinking (on/off)
The brain thinks **per-turn**, controlled by a `think` flag (the snappy everyday default is OFF):
- Set the resting default: `POST :8770/api/rhm-config {"think": true|false}`.
- Per role/mode: a role that should reason (judge / act / decide) carries `think` in its declaration; the use-gate sends it **only if the model declares the `reasoning` capability** (qwen3.5 does).
- Verify it's live: a `think:true` turn returns non-empty `message.reasoning` (e.g. "Is 91 prime?" → ~600 chars of reasoning). Thinking + tools coexist on one turn.

## Context (the "units" lever)
- Set the window: `company config chat-4b-fp8 max_model_len <N>` then `company restart chat-4b-fp8`. Capped by the model's 262,144 ceiling AND by VRAM (the KV-cache grows with context).
- The everyday brain is **65,536 (4 units)**, co-resident. **fp8-KV** (`kv_cache_dtype: fp8`, on) halves the per-token KV → ~2× the context per GB (measured KV budget 92,698→149,211 tokens at gpu_util 0.6, near-lossless; tiny long-prompt prefill cost on this Ada card, decode unaffected).
- **For more context:** solo (`@quality-9b` or a deep-4B loadout) frees the VRAM the embedder eats → ~10–16 units. Co-resident with the strong embedder caps it (~4–5 units) — context and co-residence trade against each other on the 16 GB card.

## On-demand pieces (rerank, voice, the bigger brain)
The everyday loadout drops the **reranker** to fit the FP8-4B (fp8-KV got it within ~0.6 GB; rerank was the tip-over). To pull a dropped piece in for a recall-heavy or spoken task: `company up rerank-jina` / `company up tts-kokoro` (the gate checks fit). This is the **first use-case of [[project-loadout-resolution]]** — the planned capability where work *declares* the loadout it needs and the system prompts+switches automatically (confirm or exit, never silent degrade). Until that's built, pull pieces in manually.

## It's all through the system
Serving is `serve_model.sh` via systemd (launched by `company up`, resource-gated). The serve flags (incl. `--kv-cache-dtype fp8`, `--reasoning-parser qwen3`) are **generated by the resolver from the registry** (`runtime/capabilities/` + the service's `family qwen3.5` + `capability_overrides`) — not hardcoded; tune with `company config` + `company restart`. Talking, thinking, loadout switches = the `company` console + the bridge `/api`. The only non-repo dependency is the benchmark script (`~/vllm-tests/bench.py`, wrapped by `company bench`).
