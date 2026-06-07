# R1 — Flow Trace: the plan's flows vs the real code

*Plan-review artefact. Read-only trace of the three flows the Completion Criteria / Implementation Guide describe, walked step-by-step through the ACTUAL worktree code (`~/company-cognition`, branch `concurrent-cognition`). Every claim is file:line-anchored. Evidence classification per the repo's law: **Observed** = read directly in code; **Inferred** = pattern-matched, marked as such; nothing here is execution-Verified (this is a static trace).*

## Headline (read this first)

**None of the Concurrent-Cognition build exists yet** — this is confirmed, not assumed. `STATE.md:15` names it as *"Next loop"*. Absent in the worktree: `runtime/cognition.py`, `cognition/rules.py`, `roles/` (Observed — `ls` errors), `chat_parts` / `_run_swarm` / `THOUGHT_SHAPES` / `MODEL_CAPABILITIES` / `concurrency_knee` (Observed — zero grep hits). So the trace is necessarily of the **reuse spine the plan rests on** — and the finding is that the spine is real but the plan over-credits how much of each flow is "free reuse." The genuinely net-new wiring is concentrated in three places, and each is the riskiest step of one flow.

The Implementation Guide's own file:line refs have **drifted from the worktree** (e.g. it cites `_resolve_context_at` at `suite.py:1461/1943`; it actually lives at `suite.py:1957`; `chat()` cited at `:3333`, actually `:3347`). The seams it names all still exist — but the line numbers are stale, so an implementer following them blind will land in the wrong place. Worth a refresh pass before the build.

---

## Flow 1 — a live voice turn under the staged-parts design

**Plan's described flow (Guide G4/G6, Criteria C4.1–C4.5, C6.1–C6.2):**
utterance → STT → `focus` role fires (selects cast + Part-1 shape) → Part 1 emits from base context instantly → concurrent roles (`recall`/`ground`/…) run, each writing JSON to `swarm://<turn>/<role>` → declared rules resolve those addresses → injected into Part 2's context → Part 2 emits enriched → each completed PART is the TTS streaming unit (synth part N while brain generates N+1).

**What the code actually does today** (`bridge.py:_voice_stream`, 357–488; `suite.py:chat`, 3347+):

1. **utterance → STT.** `bridge.py:428` `voice_stt.transcribe(audio, …)` → `transcript`. ✅ holds (real, unchanged).
2. **think.** `bridge.py:435` — **`thought = SUITE.chat(transcript, gid)`** — a SINGLE blocking call that returns the **WHOLE reply** (`thought["reply"]`, line 436). Observed: `chat()` (3347–3550) is one `complete_with_tools` round-trip (3438) → one `reply` string. There is **no part grain, no Part-1-instant, no `focus` role, no concurrent role fire, no `swarm://` write, no rule, no injection-into-Part-2.** The entire middle of the plan's flow is a single synchronous LLM call.
3. **synth/stream.** Only AFTER the full reply exists, `bridge.py:449` splits it by regex `(?<=[.!?])\s+` into sentences, then loops (452–460) synthesising each and emitting `{type:chunk,…}`. The "overlap" today is **synth↔playback only** — exactly what the Research Synthesis states (`05`). There is no brain↔TTS overlap because the brain has already fully finished before TTS starts.
4. **playback.** FE `useAppController.ts:1198` `playCursorRef` schedules chunks in-order (C6.2's preserve-target — Observed, real). iOS unlock (`primeAudio`) + trial recording (`bridge.py:439`) + one done-event are real and must be preserved.

**Concrete gaps (Flow 1):**
- **C4.2 / C6.1 are net-new mechanism, not reuse.** "Part 1 fires instantly, later parts resolve `swarm://`" requires a `chat_parts()` generator that *yields parts*, and a `/api/voice/stream` that consumes a **sequence** (Guide G6). Today `bridge.py:435` consumes ONE string. This is the structural change the whole voice flow depends on.
- **THE RISKIEST MISSING STEP (Flow 1): the injection step is hand-waved.** The plan repeatedly claims Part-2 injection is "the existing `_chat_context → _resolve_context_at` path" (Guide principle 3, C4.2, Synthesis line 13). **Observed: `_resolve_context_at` (suite.py:1957–1996) resolves the operator's LOCUS** — `ui://canvas/<node>`→`run://` (1965-1968), ranked by recency/proximity/semantic-cosine (`_r2_gather`/`_r2_score_and_cap`, 1981/1984). It does **not** resolve an arbitrary `swarm://<turn>/<role>` address into a prompt. The resolve *machinery* (address→content) exists in the store, but pulling a specific role's output into the next part's context is **new wiring** (a new address scheme `swarm://` + a resolver step keyed by turn/role), not a free call into the locus-scoped R2 path. The plan presents new plumbing as reuse.
- **C4.3 brevity bypass is absent** — there is no cheap judge between STT and the brain; every turn would spin the (not-yet-existing) machine. The pattern to mirror (`is_finished_thought`, suite.py:3266) exists as a template but the bypass role does not.
- **C4.5 tools-on-final-part-only:** today `chat()` offers tools on the one-and-only reply (3421/3438). With parts, intermediate parts must suppress the tools array — net-new control, not present.

**Determinism caveat the plan must state precisely (C0.2 vs C1.5):** C0.2 wants identical *routing* on re-run; C1.5 wants *varied* role draws (volatile, temp>0). These only co-exist if stated exactly: a **rule is deterministic GIVEN a role's output**; the role output itself is not. "Re-running routes identically" is a **rule-layer** property, not an end-to-end-turn property. If the spike's C0.2 test re-runs the whole turn (including the role generation) it will NOT be byte-identical — the test must freeze the role output and re-run only the rule.

---

## Flow 2 — a non-per-turn activation (background / sense-triggered)

**Plan's described flow (Criteria G5, Guide G5):** between-turn background cognition + screen/app/state-change sense-triggered cognition fire a mode's cast with **no spoken reply**, destinations = surface/address; rollups fire on schedule.

**What fires it today: NOTHING. (Observed, repo-wide sweep — not a single-file grep.)**
- `background` is a MODE string only — `suite.py:921` `MODES = (… "background" …)`; it changes the chat *directive*, nothing more. There is no trigger that activates it without a user turn.
- **No periodic tick anywhere in the backend.** Repo-wide sweep for `setInterval|threading.Timer|APScheduler|crontab|while True|OnCalendar|systemd timer`: the ONLY `while True` in `runtime/` is the SSE keepalive loop (`bridge.py:343`). The `setInterval`s are all FE cosmetics (`useAppController.ts:1047` run-elapsed counter; `extensions/live_clock_widget.tsx:15` a clock). The `threading` hits in `suite.py` (192/265/277/4009) are event-log/store **locks**, not a loop.
- **No scheduled unit in ops.** `ops/systemd/` holds only service units (`company-bridge`, `vllm-*`, `company-tts-kokoro`, …) — **zero `.timer` files**, no cron. `ops/services.json` has no schedule/interval/background entry. So "rollups fire on schedule" (C5.4) has no host mechanism at all.
- **No sense-trigger pathway.** Every cognition entry today is request-driven (a `do_POST` handler in `bridge.py`). There is no screen/app/state-change event bus that fires a cast. The FE emits `voice.client` telemetry *to* the backend (`/api/voice/log`), but nothing on the backend subscribes to state-changes to *fire* cognition.

**What the cast does with no spoken reply:** undefined in code. The only "act without speaking" precedent is the wire's `surface_review` / inbox path (reused per Guide G3 for the `surface` destination) and `decide-for-me` autonomous_dispatch — these exist and are the right reuse targets, but nothing routes a background role's output to them today.

**Concrete gaps (Flow 2):**
- **THE RISKIEST MISSING STEP (Flow 2): there is no activation substrate at all.** G5 is described as "generalise mode" but mode is a *directive selector*, not a *scheduler of casts*. A background trigger needs (a) a host loop or systemd timer, (b) an in-process dispatcher that builds a `TurnContext`-like activation without an utterance, (c) a budget gate so a background swarm can't starve the live floor (C1.2, also unbuilt). All three are net-new. The plan's "the others are triggers that fire a cast without a user turn" (Guide G5) understates this to one clause.
- **Budget floor for background is doubly-missing:** C1.2's slot semaphore doesn't exist (see Flow 3 / VramGate), AND there's no trigger to spend it — so "don't let a background swarm exceed its mode's budget" guards a thing that can neither fire nor be bounded yet.

---

## Flow 3 — a jury role (N draws → verdict) through the memo gate + the volatile fix

**Plan's described flow (C1.5, C2.4, Guide G1.5/G2):** a role declares `draws:N`; identical role+config no longer collapses to one memo-cached result; the jury produces N varied generations; a verdict rule (quorum/vote) resolves them.

**What the code does today** (`runtime/scheduler.py:run`, 37–184; `nodes/llm.py`):

1. **The memo gate is real and WOULD collapse a jury.** Observed: `scheduler.py:94` `volatile = getattr(mod, "VOLATILE", False)`; `:96` the MEMO GATE — `if nid not in force and not volatile and cached and store.exists(cached): … skipped`. The signature `_memo_sig` (26–34) is `hash(type, version, config, input_map)`. **`nodes/llm.py` has NO `VOLATILE` attribute** (Observed — the module defines `VERSION/PORTS_IN/PORTS_OUT/CONFIG/run`, nothing else; scheduler's `getattr` → `False`). So N identical `llm` nodes with identical config+input → ONE cached result reused N−1 times. The collapse the plan names (C1.5) is real.

2. **The "mark VOLATILE" fix has app-wide blast radius (Guide G1.5 as written).** Observed: `VOLATILE` is read as a **module-level** attribute (`getattr(mod, …)`, scheduler:94) — it is per node-TYPE, not per node-instance or per-config. Marking `nodes/llm.py` VOLATILE makes **every `llm` node in every app graph skip the memo gate forever** — defeating the scheduler's own promised guarantee (docstring lines 1–16: *"re-run only what changed / resume"*). The Guide's parenthetical *"(or a sampling-aware draw id)"* is the only option that preserves the app-surface guarantee; the literal "MODIFY `nodes/llm.py`: mark VOLATILE" is the one with collateral damage. **This tension is a concrete design gap the build must resolve** (likely: a per-config `draw_id`/nonce folded into `_memo_sig` so distinct draws get distinct signatures while ordinary identical nodes still cache).

3. **Two execution paths are conflated — pin which one the jury rides.** The Guide routes jury through the **scheduler's** memo gate (C1.5 cites `scheduler.py:96`), yet describes the swarm as `_run_swarm`, an *"off-MCP, ephemeral driver"* separate from `Suite.run` (Guide principle 5, G9). The volatile lever only bites on the **scheduler** path. If `_run_swarm` calls a `run_role()` helper directly (as the G0 spike sketch implies — Guide G0 step 1 "add a minimal `run_role`"), it bypasses the scheduler AND its memo gate entirely — making the whole VOLATILE discussion moot for the swarm and relevant only for app-graph juries. **The plan has not decided whether the swarm goes through the scheduler.** This is the load-bearing ambiguity for G1 vs G2.

4. **THE RISKIEST MISSING STEP (Flow 3): `draws:N` issuance, N storage addresses, and verdict aggregation are ALL unbuilt — removing the memo block produces none of them.** Observed: the scheduler runs each node **once** and writes **one** output address per port (`out_ports`, scheduler:48; the single per-port `set_ref` at 144-150). Defeating the memo gate makes a node *re-run on a second pass* — it does **not** issue N concurrent draws, does **not** create N distinct addresses to hold them (`swarm://<turn>/<role>#<draw>` doesn't exist), and there is **no verdict/quorum/vote evaluator** anywhere (`cognition/rules.py` absent). So "a 3-run quorum returns 3 distinct generations" (C1.5) needs: a fan-out that issues N requests, N addressed slots, varied sampling per draw, AND an aggregation rule — four net-new pieces. The volatile fix is necessary but is maybe 10% of the jury flow.

**Supporting gaps for Flow 3:**
- **C1.2 slot budget is unwired** (the concurrency this flow needs to issue N draws in parallel): `VramGate` (`fabric/vram.py`) is only ever instantiated in a **test** (`tests/e3_fabric.py:88`) — never in the runtime dispatch path (Observed — `grep VramGate(` → one test hit). And the scheduler is **strictly serial** (Observed — zero `ThreadPool/asyncio/httpx` in `runtime/`; the run loop is a single `while…for`). So N draws can't even fire concurrently today.
- **C1.4 output_schema is decorative — worse than the plan says.** `registry.py:register_module` (57-64) builds `NodeType` from `KIND/PORTS_IN/PORTS_OUT/CONFIG/VERSION` and **does not read `output_schema` at all** — it isn't even carried onto the type. (The only `output_schema` in runtime is a hardcoded literal in `compile.py:159`.) The transport does `response_format={"type":"json_object"}` (`transport.py:38/68`) — **not** the `json_schema` strict mode the plan wants (Synthesis line 16 calls it "one branch away," which is fair, but it's a real branch). A jury verdict over structured fields presumes enforced schemas that today don't exist end-to-end.

---

## Cross-cutting confirmations (the reuse spine — what the plan CAN lean on)

- **`Edge` has no `kind`** (C1.3 net-new): `contracts/node_record.py:35-39` — `Edge(from_node, from_port, to_node, to_port)`, no `kind` field. The injection-edge is genuinely new.
- **Injection primitive to promote exists** (Guide C1.3 reuse target): `runtime/context_variables.py` (C6) is real — a register-once variable-resolution engine ("a turn runs when its context variables resolve"). It is the right thing to promote from RHM-turn scope to a graph-edge, as the plan says. ✅
- **FE extension point for G7 is real:** `useAppController.ts:390` already branches `k.startsWith('decision.')` — the exact mirror site for a `cognition.*` branch. ✅ (C7 render is a clean extension, the least-risky net-new piece.)
- **Role registry is a hardcoded one-entry dict** (C2.1/C2.3 net-new): `suite.py:943` `ROLE_REGISTRY = {"judge": {…}}` — only `judge`. `resolve_role` (3186) + the binding precedence are real and reusable; the *file-discovery* + the 6-role `listening` cast are net-new.
- **The judge-as-role-template is real** (C2.2): `is_finished_thought` (3266) calls `resolve_role('judge')` → `client.complete` — the exact pattern a `run_role` would generalise. ✅
- **Governance reuse targets are real** (G9): the verb whitelist (`RHM_VERB_SPECS`, 2026), `surface_review`/inbox, `decide-for-me` autonomous_dispatch all exist. C9.2 (no role reaches `claude -p`) is structurally satisfied *today only because the swarm doesn't exist* — it must be re-verified once `_run_swarm` is built and confirmed OFF the MCP face.

---

## Summary of the three riskiest missing steps (one per flow)

| Flow | Riskiest missing step | Why it's the risk |
|---|---|---|
| **1 — live voice turn** | `swarm://<role>` → Part-2 prompt **injection** | Sold as "existing `_resolve_context_at` reuse"; that path is LOCUS-scoped (suite.py:1957) and resolves nothing keyed by turn/role. New address scheme + resolver — the load-bearing new plumbing of the whole staged design. |
| **2 — background / sense** | There is **no activation substrate** | `background` is a directive string; no tick, no timer, no sense-event bus, no budget gate. "Mode generalises to triggers" understates it to one clause; it's three net-new subsystems. |
| **3 — jury (N→verdict)** | `draws:N` fan-out + N addresses + verdict evaluator | The VOLATILE fix (itself app-wide-blast-radius as written) only un-caches a re-run; it does NOT issue N draws, allocate N slots, or aggregate. ~90% of the jury flow is unbuilt, and the serial scheduler + unwired `VramGate` mean N can't even fire concurrently yet. |

**Also flag to Tim / the build:** (a) the Guide's file:line refs have drifted from the worktree — refresh before the spike; (b) decide explicitly whether the swarm runs THROUGH the scheduler (memo-gated) or via a direct `run_role` (bypasses it) — this fork governs G1↔G2; (c) state the C0.2-vs-C1.5 determinism scope precisely (rules deterministic given output; draws not) or the spike's replay test contradicts the jury requirement.
