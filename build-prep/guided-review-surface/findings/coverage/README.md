# Coverage Sweep Index

> **What this is.** Full territory coverage of the design corpus (repo + vault, 250+ documents) mapping all relations to the Guided Review Surface. Completed 2026-06-08.

## Navigation

### Primary Synthesis
- **[DESIGN-CORPUS-INTEGRATION.md](../DESIGN-CORPUS-INTEGRATION.md)** — integration summary across all six territory sweeps (this is the entry point)

### Territory Sweeps (by location)
1. **[design-corpus.md](design-corpus.md)** — Design corpus (`build-prep/` repo + vault design docs)
   - The APPLICATION-STRUCTURE-PACK.md analysis
   - Five unifications identified (Walkthrough Organ primary)
   - ~17-surface map coverage

2. **[substrate.md](substrate.md)** — Substrate layer (`contracts/` + `store/` + `fabric/`)
   - Address grammar (schemes, gaps, proposals)
   - Store layer (fs safety, concurrency, registry)
   - Fabric layer (transport, emit contracts, state)

3. **[runtime.md](runtime.md)** — Runtime system (`runtime/` core + `suite.py` + `bridge.py`)
   - Walkthrough engine (READY for wire)
   - Batch compose + inbox lifecycle
   - Governance layer + voice paths

4. **[canvas.md](canvas.md)** — Frontend (`canvas/` React + `Studio` room)
   - Monolith structure (1660 lines, F0 prerequisite)
   - SSE dispatch + component render
   - IAS prerequisites (S0–S5, I1–I6, R1–R2, F9)

5. **[cognition.md](cognition.md)** — Perception layer (`runtime/cognition.py` + Concurrent Cognition)
   - Swarm executor (G0–G1 proven)
   - Injection edge (C1.3)
   - Context-assembly cascade

6. **[voice.md](voice.md)** — Input channel (`voice/` stack + speech)
   - Kokoro TTS (ready)
   - whisper.cpp STT (ready)
   - Focus passthrough (one seam missing)

## Key Findings at a Glance

### The Single Largest Finding
**The RHM Walkthrough Organ (vault) and the Guided Review Surface (repo) ARE THE SAME DESIGN.**
- Merge their criteria before loop-prep runs
- The merged doc is loop-prep's completion criteria

### Five Unifications
1. RHM Walkthrough Organ = this build (parent spec)
2. Operable Interface Group C = FE show-me lane (build once, both satisfied)
3. Standalone mockup studio superseded by this in-app rebuild
4. Project→Product Pipeline's first human-review instantiation
5. IAS corpus-import + FORM gate is hard prerequisite

### Build Shape (After IAS Phase 0)
```
Bucket A: Walkthrough engine (wire show-me lane) — READY
Bucket B: Text-streaming (wire CC chat_parts, voice focus) — design phase
Bucket C: Mockup-aware + generate (6 items, resolve_scope branch, batch approve)
Schema:   T0-WIRE / T0-KEYSTONE / T0-CARD (resolve this build), T1-EMIT (prerequisite)
```

## Evidence Marks

Throughout these documents:
- **Observed(file:line)** = read directly from source docs/code
- **Inferred** = pattern-matched from architectural intent
- **Unification-opportunity** = explicitly names where this build subsumes designed work

## Relation Summary

| Territory | Use | Touch | Unify | Relate |
|-----------|-----|-------|-------|--------|
| Design corpus | RHM Organ / IAS floor / OCS dispatch / CC perception / Voice / Wire | 17-surface / Operable Interface / Remediation / Mockups | **RHM = this build** / FE lane = both / Studio → in-app / Pipeline opener / FORM required | CC scale / Dispatch / Coherence / Twin / Ideas |
| Substrate | Address grammar / Event-stamp / Resolver / Context / Safety | Gram extension / Mockup scheme / Scope path | `doc://`/`area://` formalize / `mockup://` register | Coherence |
| Runtime | Walk engine / Batch / Inbox / Voice / Governance | Stop / Entry / Comments | **Engine READY** / Show-me mounts / Stops RAISE | Twin / Generative |
| Canvas | SSE dispatch / Studio room / Generic render | IAS prereqs / FORM gate | **F0 prerequisite** / Group C = lane / Portal | — |
| Cognition | Swarm / Injection / Context / Parts / Explain | Routing / Stream / Cancel | **Don't duplicate** / wire chat_parts / resolve→cascade | — |
| Voice | Kokoro / Whisper / Barge-in | Focus passthrough | **One arg** → Bucket B step | — |

## How to Use These Findings

### For Loop-Prep Planning
1. Read DESIGN-CORPUS-INTEGRATION.md (this provides the roadmap)
2. Identify the merged Walkthrough Organ + GRS criteria (primary unification)
3. Map Bucket A/B/C sequencing against IAS Phase 0 dependencies
4. Confirm T1-EMIT fix is in scope (prerequisite for safe dispatch)

### For Build Sequencing
1. **Prerequisite:** IAS Phase 0 (C0 corpus-import through R1–R2)
2. **Parallel:** Buckets A/B/C in dependency order
3. **Schema:** T0-WIRE/T0-KEYSTONE/T0-CARD resolutions (parallel or step 1)
4. **Guard:** T1-EMIT fixed before Bucket C-a/b dispatch enabled

### For Verification
- Each territory sweep carries acceptance criteria and code paths
- Runtime.md has function signatures for every walk-engine call
- Canvas.md maps FE prerequisites (components, state shape)
- Cognition.md details the CC cascade inputs for per-stop comprehension
- Voice.md confirms ready paths (Kokoro stream, whisper, VAD loop)

## Forward-Design Points (Not Blockers)

- **`doc://` / `area://` grammar extension** — enables RHM walking vault notes as tour stops (forward, not prerequisite)
- **Mockup-stop unregistered tolerance** — design choice (extend registry vs. allow HTML-injected narration)
- **Part grain for streaming** — sentence/beat/paragraph? Mode-dependent? (CC registry first-cast decision)
- **R (reserved slots)** — concurrency trade (R=4 proposed, tunable by mode)

---

**Sweep completed 2026-06-08.** This index is the entry point for all coverage findings. The integrated summary (DESIGN-CORPUS-INTEGRATION.md) is the operational document for build planning.
