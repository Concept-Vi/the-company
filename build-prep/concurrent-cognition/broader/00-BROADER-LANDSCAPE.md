# Concurrent Cognition — Broader Landscape (wave 2, aggregated)

*Five broader research threads (B1–B5), aggregating the wider picture Tim asked for on top of the six codebase-reuse threads (`../00-LANDSCAPE.md`). Where wave 1 mapped "what's reusable," wave 2 maps "is the design right, how big does it reach, and how do we build it." Read alongside the per-thread docs B1–B5.*

---

## 1. Is the design right? (B1 — external architectures)

**Yes, and it's a genuine novel fusion.** On three axes — parallel-for-latency vs -**quality**, same-model-many-draws vs many-models, aggregate-at-end vs **interact-during** — our shape (parallel-for-quality · one-4B-many-roles · interact-during a streamed part-by-part reply) sits in a cell **no named pattern occupies.** It is anchored, not invented:

| External work | What it proves for us |
|---|---|
| **Compound AI Systems** (BAIR/Zaharia) | the umbrella thesis — system structure beats raw scale (AlphaCode 30%→80%) |
| **Mixture-of-Agents** | composition beats size empirically (open models 65.1% vs GPT-4o 57.5%) — *and* its weakness (slow time-to-first-token) is exactly what our **staged stream hides** |
| **Self-MoA** | counter-evidence that **vindicates one-4B-many-draws** — mixing different models *lowers* quality (+6.6% for the single best) |
| **Blackboard / Hearsay-II** (1980s) | maps 1:1 onto `swarm://`-addresses → synthesizer; a 40-year-proven control model to mine |
| **Skeleton-of-Thought** | our staging cousin; its router = our **mode-dial**; **SoT-R proves conditional staging is mandatory** (don't stage when it doesn't help) |
| **Branch-Solve-Merge** | literally our turn shape |
| **Chunked-cascade** (LiveKit/Pipecat) | our voice plan (TTS-on-first-sentence) generalised to part-grain; **Moshi** full-duplex is the rival no-cascade shape |

**Six "better shape" corrections to fold in:** rank-then-fuse the swarm (don't concatenate outputs) · interruptible/barge-in TTS (Moshi-like) · conditional staging is mandatory (the brevity bypass is not optional) · single-bounce debate for checker roles · mine blackboard control theory · gate weak role-outputs before fusion (Self-MoA). **Sharpest risk to prove at the spike:** can a *4B* aggregator synthesise 32 role-outputs as well as MoA's 110B aggregator? Unknown until measured.

## 2. The dual-use spine — what the node mechanism actually needs (B2)

The node-*type* system is already excellent and registry-driven (file-per-type, self-registering, generic compile/render). The roughness sits **exactly where cognition needs it**:
- **The "role" is a hardcoded one-entry dict in `suite.py` (`ROLE_REGISTRY`), not file-discovered** — the single biggest gap.
- **Edges have no type system** (`Edge` is a bare wire, no `kind`); branching/fan-in are *nodes* (gate/join). The injection/resolve edge is genuinely net-new (C6 machinery exists but is RHM-turn-scoped).
- **`output_schema` is declared-but-decorative** — `register_module` never reads it.
- Ports are free strings with an `Any` bypass; scheduler is strictly serial.

**Shape: one shared lower substrate + two thin drivers.** Registry · compile · readiness · a (new) wave executor · store · render machinery are shared; the app's governed `Suite.run` and cognition's off-MCP ephemeral `_run_swarm` are thin drivers that diverge on persistence · trigger · governance · namespace · per-node memo · render surface. That is the app-vs-cognition share/diverge line, precisely.

## 3. How far it reaches (B3 — broader applications)

A 15-use application map; the mechanism named once as a reusable primitive (resident-model + concurrent structured roles + outputs-as-addresses + chains-as-edges + mode-as-budget + self-instrumenting + live-rendered). **Five highest-leverage reuses:** codebase map-reduce · typed-triage classification · the altitude-translation layer · introspective-data rollups · background cognition. **The shape of the whole space:** one organ where the introspective-rollup role closes the loop, so each new field makes the others smarter — the literal "limitless."

**Four findings that reshape the core (the scout's real yield):**
- **R1 — a 7th piece: per-draw variation.** Juries/critic-quorums need N *different* draws; the `llm`-not-volatile memo gotcha means a "jury of N" silently returns one answer N times. A real primitive, not a config.
- **R2 — role vs `claude -p` subagent is a structural floor.** Roles may appraise/propose builds, **never dispatch** (bound by the autonomous-spawn-lead-only law). Make it architectural, not conventional.
- **R3 — `output_destination` is more load-bearing than thread 01 treats it.** Triage/consolidation/rollups need "propose/surface" and "typed-lane/channel" sinks beyond the simple four kinds.
- **R4 — "mode = the dial" must generalise to activation-contexts.** Background/sense/rollup swarms have no budget home if mode only means presence-modes.

## 4. Models as configurable types (B4)

The missing layer: a **`MODEL_CAPABILITIES` registry keyed by model-id** (tool-calling · json_schema · thinking · context-ceiling · **concurrency-knee** · speed), with provenance `declared`/`probed`/`measured`/`served` (live probe wins). The load-bearing move is keeping three keyings distinct and **joining** them: intrinsic capability (by model-id, net-new) ⨝ service deployment (by service-key — `services.json`, exists) ⨝ telemetry (by service — exists). A role binds a model-id → reads capabilities → if locally served, looks up the backing service for VRAM via `gpu.py`. Proof it works: `judge.recommended_model == chat-4b.config.model` (the same string is the bridge; `_local_brain_key` already does this match). **Cognition adds:** the swarm `Semaphore` reads `concurrency_knee` from the registry (not a hardcoded 32); model suitability (`role.requires ⊆ model.provides`) becomes a *query* replacing hand-written `recommended_model` prose; `resident_capable` is *derived* from the join, never declared.

## 5. How we build it (B5 — the coordination, the recursion)

**The trap, named: 32-way parallel cognition does NOT mean 32-way parallel build.** Nearly every net-new cognition piece converges on ONE file (`runtime/suite.py` + `bridge.py`), and with one branch, two agents can't co-own it. The honest structure:

- **1 serial spine** (S0→S6 on `suite.py`): proving spike → the slot scheduler (the make-or-break) → role registry → `_run_swarm` → the `chat()` part-loop → injection → brevity bypass. Forced ordering: **spike before fan-out; slot scheduler before all roles.**
- **3 genuinely-disjoint parallel lanes** flanking it: transport `json_schema`; `nodes/llm.py` VOLATILE; the `canvas/app` render FE.

**Method: specialise the proven loop, don't reinvent.** A `cognition-build` skill (sibling of `company-build`/`wire-build`/`voice-build`) drives the triad as the common reference: implementer → **separate** verifier (by-use + adversarial; design-critic + lint for FORM) → commit per criterion to the one branch → surface forks needs-tim. No self-passing. `chat()` is the highest-blast-radius edit — gated by the existing `rhm_*` regression suites.

**The recursion is an AFTER (bootstrapping).** Coordinating the build *through* the engine needs the engine's parallel scheduler — which is the very thing S1 builds — and Vi-Memory MCP is absent here. So: triad+plan coordinates the build now; the graph-coordination becomes the *celebrated second self-build proof* once S1 exists. A light visibility version (the plan mirrored as a company graph) is available immediately.

## 6. Net design deltas to fold into the triad (the aggregate yield)

1. **A 7th piece — per-draw variation** (juries/ensembles); fixes the volatile-memo collapse. *(B3-R1)*
2. **Rank-then-fuse** the swarm, and **gate weak outputs** before fusion — not concatenate. *(B1)*
3. **Conditional staging is mandatory**, not a nicety (SoT-R) — the brevity bypass is core. *(B1)*
4. **Edge type system + file-discovered roles + read `output_schema`** — the node-mechanism build-out. *(B2)*
5. **`output_destination` richer than four kinds** (propose/surface, typed-lane). *(B3-R3)*
6. **Mode → activation-contexts** (presence + background + sense + rollup). *(B3-R4)*
7. **`MODEL_CAPABILITIES` registry keyed by model-id**, concurrency-knee as data. *(B4)*
8. **Role≠dispatcher is a structural floor** (autonomous-spawn-lead-only). *(B3-R2)*
9. **Build = 1 serial spine + 3 disjoint lanes**, spike-gated, slot-scheduler-first — NOT 32-way parallel. *(B5)*
10. **THE spike risk: does a 4B aggregator fuse 32 outputs well?** Prove first. *(B1)*

## 7. Still Tim's to author (gate the triad)
**Part grain** · **first role cast** · R/swarm-cap bias · residency policy · cloud escape-hatch · tools-across-parts · the second proving target after voice · how big to scope the node-mechanism build-out now vs later.

*Next: this + `../00-LANDSCAPE.md` converge into the loop-prep triad (Completion Criteria · Implementation Guide · Research Synthesis) — the common reference for the sub-agent-driven build in this worktree.*
