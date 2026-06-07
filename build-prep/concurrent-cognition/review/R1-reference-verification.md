# R1 — Reference Verification (Concurrent Cognition triad vs. the real code)

*Read-only review. Verifies the Completion Criteria + Implementation Guide + Research Synthesis against the actual source in `~/company-cognition`. No code or plan was modified. Ranked by impact: structural (exists-differently / missed) first, then citation drift (cosmetic but matters to an automated build agent that trusts line numbers — which is this plan's consumer).*

---

## Verdict in one line

The plan's **architecture is sound and its net-new ledger is accurate** — every "net-new" piece (`runtime/cognition.py`, `roles/`, `cognition/rules.py`, `chat_parts`, `THOUGHT_SHAPES`, `_run_swarm`, `MODEL_CAPABILITIES`, `concurrency_knee`, the parallel executor, edge `kind`, enforced `output_schema`) genuinely does not exist yet. The reuse spine (the injection path, `complete()` validate/retry, `gate.py`, `VramGate`, the `decision.*` SSE pattern, `gpu.py`) genuinely does exist. The defects are: **two substantive reconciliations the plan misses**, **one scheduler shape the plan slightly mis-describes**, and **a systemic ~+14-line staleness in all `suite.py` citations**.

---

## TIER 1 — Substantive (exists-differently / missed; could mislead the build)

### 1. G8.1 `MODEL_CAPABILITIES` is presented as wholly net-new, but a sibling already exists in-code

- **Claim (Guide G8 / Criteria C8.1):** "NEW: `MODEL_CAPABILITIES` + `model_capabilities()` resolver (provenance declared/probed/measured/served; live probe wins)." The plan never references reusing or extending anything for this.
- **Reality:** `runtime/suite.py` already has **`MODEL_KNOBS`** (suite.py:1011) and **`knobs_for()`** (suite.py:3212), *tagged "G8.1" in the code itself*. `knobs_for` already resolves `tools` by **live probe** (`source="probed"`, via `_model_supports_tools`), and `thinking` / `structured_output` (incl. a `json_schema` option) as `source="declared"`. That is exactly the provenance model (`declared` vs `probed`) the plan reinvents under a new name.
- **Holds?** PARTIAL / MISSED. The two are plausibly orthogonal (per-request *knobs* vs intrinsic *capability by model-id*), but the plan should explicitly reconcile them — at minimum reuse the `declared/probed` provenance machinery and the `tools`-probe rather than build a parallel one, or it risks two overlapping capability surfaces (a law-L1 "one registry per type" smell). **Action: the plan should name `knobs_for`/`MODEL_KNOBS` in G8 and state the share/diverge seam.**

### 2. C1.5 "mark `llm` VOLATILE" contradicts documented app-surface behaviour

- **Claim (Guide G1.5 / Criteria C1.5):** "MODIFY `nodes/llm.py`: mark VOLATILE (or a sampling-aware draw id) so identical config+input don't collapse at the memo gate."
- **Reality:** `nodes/llm.py`'s own docstring (line 4–5) sells memoization as a **feature**: *"Memoised like any node, so an identical prompt+config reuses the cached call (don't re-hit the model)."* And `nodes/gate.py` explicitly documents the opposite design choice (`gate.py:14`: "NOT VOLATILE — run() is a pure function… the memo gate may cache it"). Blanket-VOLATILE on `llm` **breaks the app-side memo reuse it was built to provide** (a node graph re-run would re-hit every model call).
- **Holds?** CONFLICTS. The plan already hedges with "(or a sampling-aware draw id)" — that branch is the correct one. **Action: the jury/per-draw path (C2.4/C1.5) needs per-draw cache-key variation (a draw-id salt into `_memo_sig`), NOT global `VOLATILE`.** The Criteria/Guide should drop "mark VOLATILE" as the lead and lead with the draw-id approach.

### 3. The scheduler has no materialized "ready-set" — C1.1 must build one first

- **Claim (Criteria C1.1 / Guide G1.1):** "The scheduler runs a ready-set CONCURRENTLY… dispatch the ready-set via a `ThreadPoolExecutor`."
- **Reality:** `runtime/scheduler.py:59-153` is a **re-scanning single-pass loop** with a `progress` flag — it iterates `by_id.items()`, fires the first ready node it meets, and loops again. There is no collected ready-set object to hand to an executor. The readiness *predicate* exists (lines 72-77) and is correct, but "the ready-set" is a notion the build must first materialize (gather all currently-ready nodes per pass) before it can dispatch them concurrently with a per-wave barrier.
- **Holds?** EXISTS-DIFFERENTLY. The Synthesis phrase "the scheduler has the right readiness *shape* but is strictly serial" is fair; the Guide's "dispatch the ready-set" understates that the ready-set is net-new structure. Low-risk but affects how C1.1 actually lands.

---

## TIER 2 — Citation drift (cosmetic for a human; non-trivial for a line-trusting build agent)

### 4. All `runtime/suite.py` line citations are ~+14 stale (systemic, all locatable)

| Plan citation | Real location | Note |
|---|---|---|
| `ROLE_REGISTRY` @ `suite.py:929` | comment at 927-942; **dict literal at 943** | 929 is mid-comment; substantive claim ("hardcoded one-entry dict — only `judge`") **HOLDS**. |
| `_chat_context` @ `suite.py:1322` | **def at 1336** | resolves correctly. |
| `_resolve_context_at` @ `suite.py:1461,1943` | **single def at 1957**; 1461 is inside the R2 block of `_chat_context` | the two cited lines are *regions* of the resolve/inject path, not the def; the def is at 1957, not 1943. |
| `chat()` @ `suite.py:3333` | **def at 3347** | resolves correctly. |

All four resolve to the correct method/region; the drift is roughly consistent (~+14). **Risk: low for a human, real for an automated build agent that seeks by line number** (the stated consumer of this triad). Recommend the build agent locate by symbol name, not line.

### 5. `node_record.py` — path unstated, but the claim is correct

- **Claim (Guide G1.3 / file-territory):** "MODIFY `node_record.py:35-40` (`Edge`): add a declared `kind`." Bare filename, no directory.
- **Reality:** the file is `contracts/node_record.py` (NOT `runtime/`). `class Edge` is at **line 35**, fields `from_node/from_port/to_node/to_port` span **35-39**. The `35-40` range and the `Edge` target are **CORRECT**; only the directory is unstated.
- **Holds?** YES (minor: prefix with `contracts/` to disambiguate, since `node_record` is the one referenced file not living under `runtime/`).

---

## TIER 3 — Confirmed accurate (the reuse spine holds)

| Claim | Location | Holds? |
|---|---|---|
| Injection path `_chat_context → _resolve_context_at` is address→resolve→inject; judge bypasses it | suite.py:1336 / 1957 | YES — resolve-at-locus is real; `is_finished_thought` (3266) is utterance-only, confirming the judge bypasses it |
| `complete()` validate/retry exists for `output_schema` enforcement | `fabric/client.py:75-87` | YES — exact lines; `schema.model_validate` + retry on mismatch |
| `json_schema` is "one transport branch away" — transport does `json_object` | `fabric/transport.py:37` | YES — line 37 emits `response_format:{type:"json_object"}`; `json_schema` not yet emitted |
| `VramGate` exists, `limit=1`, unwired | `fabric/vram.py:14` | YES — `limit:int=1`; only caller is `tests/e3_fabric.py:88` (never in a dispatch path) |
| `gate.py` is the selective-emit / predicate precedent for the rule engine | `nodes/gate.py` | YES — single-key dict = one branch taken; clean precedent |
| `decision.*` SSE branch is the extension point for `cognition.*` | `useAppController.ts:390` (`openStream` @ 363) | YES — plan says `:384`; the dispatch block is at 390, `k.startsWith('decision.')` present |
| `playCursorRef` (in-order playback), `primeAudio` (iOS unlock) to PRESERVE | `useAppController.ts:158/1198`, `1180` | YES — both real |
| `/api/voice/stream` = STT→full-reply→per-sentence synth, the part becomes the synth unit | `bridge.py:357` (`_voice_stream`), route @ 631 | YES — sentence-chunked streaming confirmed; plan's `~357-468` is the synth/emit body |
| `context_variables.py` (the C6 registry) is the promote-to-edge substrate | `runtime/context_variables.py:49-95` | YES — Protocol + `register`/`resolve_context`; a real universal var-type registry |
| `registry.py` `register_module` reads node descriptors (extend for `output_schema`) | `runtime/registry.py:55-64` | YES — exact block; reads `PORTS_IN/OUT/CONFIG/VERSION`, would add `output_schema` here |
| `gpu.py` is the VRAM authority (reuse, don't copy) | `ops/cli/gpu.py` | YES — `budget_vram/check_fit/fit_report/plan_eviction/read_gpu` present; **no `concurrency_knee`** (correctly net-new data for G8) |
| `MODEL_CAPABILITIES`, `concurrency_knee`, `chat_parts`, `THOUGHT_SHAPES`, `_run_swarm`, `runtime/cognition.py`, `roles/`, `cognition/` | — | CORRECTLY ABSENT — all genuinely net-new |
| `drift_acceptance.py` (the gate the FORM rubric leans on) | `tests/drift_acceptance.py` | YES — exists |

---

## Unverified / out-of-scope (noted, not blocking)

- **G6 "one chat-event regardless of N parts"** — a PRESERVE *design note*, not a file:line claim. The chat-append lives in `chat()` (suite.py:3355/3357), not `_voice_stream`; the voice stream path does not itself append the chat row. Whether the parts path keeps exactly one chat-event is a build-time invariant to hold, not a current code fact to verify. Left unverified by design.
- **`resolve_role`** — the plan names it bare in Guide G2 (no line), so no drift to flag; for reference it is at suite.py:3186 and already resolves model+knobs from `ROLE_REGISTRY` (the generalisation seam G2 builds on).

---

## Highest-risk inaccuracies, ranked

1. **G8 misses the existing `knobs_for`/`MODEL_KNOBS` (G8.1-in-code)** — risk of building a second, overlapping capability surface against law L1. *(Tier 1, #1.)*
2. **C1.5 "mark `llm` VOLATILE" contradicts the node's documented memo-as-feature** — would break app-side reuse; the draw-id branch is the correct one and should lead. *(Tier 1, #2.)*
3. **C1.1 ready-set is net-new structure, not a re-scan to parallelize** — minor framing, affects the executor design. *(Tier 1, #3.)*
4. **Systemic ~+14-line drift on every `suite.py` citation** — harmless to a human, a real snag for a line-seeking build agent; locate by symbol. *(Tier 2, #4.)*
5. **`node_record.py` directory unstated** (`contracts/`, not `runtime/`) — the only referenced file outside its expected module. *(Tier 2, #5.)*
