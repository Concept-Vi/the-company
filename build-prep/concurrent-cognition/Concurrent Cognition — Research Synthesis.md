# Concurrent Cognition — Research Synthesis

*Document 3 of the triad — the evidence base the Criteria + Guide rest on. Consolidates two research waves (11 thread docs) into what was explored, what was found, and what it means for the build.*

> **⚠ Hardened by Round-1 review — `review/R1-FOLD.md` is binding.** Ledger correction: **injection, `chat_parts` (a hot-path refactor), the G5 activation substrate, and the jury flow move from "reuse" to NET-NEW.** Resource correction: the resident 4B's `max_num_seqs=16` and its KV pool is shared with the main context → **real co-resident concurrency is well below 32 at usable context** (the c=32/2241 tok/s figure was 4K-context, not the voice config). The architecture + spine still hold; the reuse just shrank.

---

## Round 1 — codebase reuse (what we HAVE) · docs 01–06 + `00-LANDSCAPE.md`

**What was explored:** the role/judge machinery, the node-graph runtime, model concurrency + injection seam, the chat/mode path, the voice circuit, the canvas render — each with file:line evidence.

**Verified findings (the reuse spine):**
- **Role = node, chain = edge, view = canvas; the judge is role #0.** `ROLE_REGISTRY` (`suite.py:929`) already defines a role as "a named model-function of the collective cognition" and names this generalisation as intended growth. → *Criteria G2; Guide G2.*
- **The address→resolve→inject SHAPE exists, but injection is NET-NEW (R1-FOLD F3 / R2-FOLD H4):** `_chat_context`/`_resolve_context_at` resolves operator-notebook strata, NOT freshly-written role refs — so a role's `run://<turn>/<role>` JSON is invisible to it. Injection needs a net-new ref-read branch; addressing is `run://` (never `swarm://`). → *G3/G4.*
- **The scheduler has the right readiness shape but is STRICTLY SERIAL** (`scheduler.py:60-153`; zero async/threadpool). → *the make-or-break, G1.1.*
- **Concurrency mechanism is feasible on one resident model:** blocking transport + GIL-releases-on-IO + vLLM server-side batching → a ThreadPoolExecutor in the cognition driver; `fabric/vram.py:VramGate` exists unwired (`limit=1`). **But the WIDTH is KV-pool-bound, not 32** (R2-FOLD H1): `max_num_seqs=16` AND the shared KV pool → ~1–5 roles at the 64K voice brain, ~16 with a leaner swarm-mode config. → *G1.1/G1.2/C1.7.*
- **`json_schema` is one transport branch away** (`transport.py:37` does `json_object`; the 4B does strict schemas reliably — `BENCHMARK_FACTSHEET.md §5`); validate/retry exists (`client.py:75-87`). → *G1.4.*
- **The voice circuit today:** STT-batch → full-reply → per-sentence synth (`bridge.py:357-468`); the only overlap is synth↔playback. The PART becomes the synth unit with near-zero change to `speak()`. → *G6.*
- **The canvas is a generic reflects-never-owns renderer**; `decision.*` SSE branch (`useAppController.ts:384`) is the exact extension point for `cognition.*`; `build_object_info`/`ui_info` projects registries→UI. → *G7.*

## Round 2 — broader picture (is it right, how far, how to build) · `broader/B1–B5` + `00-BROADER-LANDSCAPE.md`

**B1 — external architectures.** Our shape (parallel-for-quality · one-model-many-roles · interact-during a streamed reply) occupies a literature cell **no named pattern fills** — a genuine fusion, but anchored: Compound AI Systems (system > scale), Mixture-of-Agents (composition beats size: 65% vs 57%), **Self-MoA (one-model-many-draws vindicated; mixing models LOWERS quality)**, Blackboard/Hearsay-II (maps 1:1 to `swarm://`→synthesizer), Skeleton-of-Thought (staging cousin; **conditional staging proven mandatory**), Branch-Solve-Merge (our turn shape), chunked-cascade (our voice plan). **Corrections folded in:** rank-then-fuse + gate weak outputs (not concatenate); interruptible TTS; conditional staging is core. **Risk → C0.3:** does a 4B aggregator fuse 32 well? — de-risked by L2 (routing-by-rules, not aggregation, is the spine).

**B2 — node-mechanism build-out.** The node-*type* half is excellent + registry-driven; roughness is exactly where cognition needs it: role = hardcoded one-entry dict (biggest gap) · edges have no `kind` · `output_schema` decorative · ports free-string · serial scheduler. Shape = one shared substrate + two thin drivers. → *all of G1; the share/diverge seam.*

**B3 — broader applications.** 15-use map; top-5 reuses (codebase map-reduce · typed-triage · altitude-translation · introspective rollups · background cognition — Tim: ALL FOUR after voice). Four reshapes: **R1** per-draw-variation primitive (a 7th piece — now C1.5/C2.4, built-in) · **R2** role≠dispatcher is a structural floor (now C9.2) · **R3** `output_destination` richer than 4 kinds (now C3.2, five destinations) · **R4** mode → activation-contexts (now G5).

**B4 — model+capability registry.** Capability registry keyed by model-id, JOINED to service-deployment + telemetry; `concurrency_knee` becomes data; suitability a query; `gpu.py` reused as the VRAM authority. Proof the join works: `judge.recommended_model == chat-4b.config.model`; `_local_brain_key` already does the match. → *G8.*

**B5 — SDD coordination (the recursion).** **32-way parallel cognition ≠ 32-way parallel build** — most net-new converges on `suite.py`, so: 1 serial spine (G0→G4) + 3 disjoint lanes (json_schema transport · `llm` volatile · canvas FE). Specialise the proven loop (a `cognition-build` skill, sibling of company/wire/voice-build); the triad is the common reference; implementer→separate verifier→commit-per-criterion→surface-forks. **The recursion is an AFTER** (bootstrapping: the engine's parallel scheduler is the very thing G1 builds; Vi-Memory MCP absent) — coordinate via the triad now; move coordination onto the engine once G1 exists (the celebrated second self-build). → *the build method; G0 spike-gate, G1-first ordering.*

## What exists → what's net-new (the one-line ledger)
- **Reuse near-wholesale:** node-type registry · ports/config · compile · store (single-writer) · `gate`/`join` · the resolve/inject path · the mode system · `complete()` validate-retry · `gpu.py` resource-manager · the canvas + `decision.*` SSE pattern · the judge as role template.
- **Net-new (the build):** parallel wave executor + slot semaphore (G1.1-1.2) · edge `kind`/injection edge (G1.3) · enforced `output_schema` (G1.4) · `llm` volatile + per-draw (G1.5) · file-discovered role registry (G2) · the declared-rule engine (G3) · the staged-part queue + thought-shapes + brevity bypass (G4) · activation-context triggers (G5) · parts-as-TTS-units (G6) · the cognition view + `cognition.*` events (G7) · `MODEL_CAPABILITIES` join (G8).

## Verified hardware facts (the foundation)
- The 4B is **resident-capable at 64K** co-resident with a 4-bit voice (the 2026-06-07 co-residence work). The swarm lives on this one resident model, but its **width is bound by the shared KV pool** (R2-FOLD H1): ~1–5 roles overlapping a 64K main context; ~16 with a mode-selected leaner swarm-brain config (~16K/util ~0.6). Slot budget + co-residence are owned by `gpu.py`.
- The 4B does tool-calls reliably + valid JSON (`json_object`; true `json_schema` server-side is a separate change — F9), ~100 tok/s decode. **Concurrency: `max_num_seqs=16` (services.json), KV pool SHARED with the main context** — the c=32/2241 tok/s benchmark was 4K-context on a higher util, NOT the co-resident voice config; the real swarm ceiling at the voice config is well below 16 at usable per-role context (measure at C0.5).

## Open dev-calls (carried; see DECISIONS.md)
Address scheme (reuse `run://`) · `swarm://` lifecycle (persist+GC) · tools-on-final-part · per-mode grain table. Decided as developer calls; surfaced, not buried.

*This synthesis + the Criteria + the Guide = the common reference. Next: plan-review rounds (agents compare the triad against the actual code + docs; findings fold back) before the spike-gated build.*
