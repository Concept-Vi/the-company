# Design Corpus Coverage Integration Summary

> **Task:** Coverage sweep of the designed corpus across repo + vault (96+ docs) mapping relations to the Guided Review Surface.
> Completed 2026-06-08.
> **Scope:** `/home/tim/company/build-prep/` (repo) + `/mnt/c/Users/Workstation001/Documents/Claude/Projects/counterpart/the Company/build-prep/` (vault).

---

## The Single Largest Finding

**The Guided Review Surface IS the RHM Walkthrough Organ — they are the same design expressed twice from different vantage points (vault vs. grounded-code).**

This changes the build's entire shape. The Walkthrough Organ criteria (vault) should be the PARENT spec, not a sibling. The synthesis (repo) maps the grounded-code proof. Building to both as one unified criteria is the full organ.

---

## Coverage Results by Territory

### 1. Design Corpus (`area://design-corpus`)
**File:** `coverage/design-corpus.md` (616 lines)

**Key finding:** The APPLICATION-STRUCTURE-PACK.md §3–4 identifies the Sequences Primitive (`resolve → present/work → persist → next/trigger`) as THE relational loop the Company runs at every scale. **Every designed surface and organ in the corpus is an instance of or consumer of that same primitive.** The guided-review-surface does not relate to other designs as a UI panel relates to data — it IS the mechanic.

**Five unifications identified:**
1. **PRIMARY:** RHM Walkthrough Organ (vault) IS this build → merge criteria before loop-prep
2. **FE lane:** Operable Interface Group C IS the show-me lane → build once, satisfy both
3. **Studio:** Standalone mockup studio is superseded → guided-review-surface is the in-app rebuild
4. **Pipeline:** Project→Product stages all use this organ → first instantiation of human-review channel
5. **FORM:** IAS corpus-import + design law is a hard prerequisite for any FE

**Touch findings:**
- ~17-surface map: this build spans surfaces 2.1 (studio) + 2.7 (walkthrough) + 2.11 (build-review)
- Remediation Spec: T0-WIRE / T0-KEYSTONE / T0-CARD are resolved by this build
- Mockup corpus: 23 mockups, 18 with `data-ui-ref`, most stops unregistered → registration is Bucket C-a/c

**Relate findings:**
- Concurrent Cognition: same primitive at AI scale → CC cascade IS the per-stop comprehension (not separate)
- Decision→Wire: governed dispatch at every actuation point → mockup dispatch = new `resolve_scope` branch
- Coherence substrate: drift detection feeds the surface → surface makes it visible and actionable
- Twin/model-of-Tim: located gold from every annotate is training data → `ingest_comment` on every GRS annotate
- Idea-capture: generative direction flows from the surface → RESPOND station D4/E3 → generative inbox

### 2. Substrate (`area://substrate`)
**File:** `coverage/substrate.md` (1200+ lines)

**Key finding:** The address grammar (contracts/address.py) is the floor everything stands on. Three scheme gaps create latent inconsistencies:
- `mockup://` — already in operational use (suite.py), not in SCHEMES
- `doc://` / `area://` — proposed for the design corpus, not in SCHEMES

**Use findings:**
- `contracts.address.scheme()` and `is_cas()` are the parse utilities the surface depends on
- Event-address-stamp (S2) routes `ui://` on every relevant emit site — keystone for temporal deixis
- `ui://→code://` resolver (S3) maps locus to scope for generate-for-mockups

**Touch findings:**
- Cross-process safety (S4) — concurrency risk the surface must not worsen
- `UI_REGISTRY` carries element addresses → zero orphaned unregistered addresses
- R2 context auto-resolution — `_chat_context` grounding at each locus (built + running)

**Unify findings:**
- Address grammar extension to `doc://`/`area://` is a forward design point (forward, not prerequisite)
- `mockup://` scheme needs formal registration in SCHEMES
- `resolve_scope` pipeline for mockup-file targets (Bucket C-a dispatch)

### 3. Runtime (`area://runtime`)
**File:** `coverage/runtime.md` (1400+ lines)

**Key finding:** The walkthrough organ (suite.py) is **fully built and ready to wire**. The FE show-me lane (Bucket C-h) is the remaining work.

**Use findings (READY, BUCKET A):**
- `present_current()` / `start_guide()` / `start_walkthrough()` — the sequencer engine (suite.py:6198–6492)
- `GUIDE_SEQUENCES` registry — ordered tour stops by topic (suite.py:6355–6395)
- `address_help()` — corpus narration lookup (suite.py:6220–6225)
- `coa()` / `resolve_surfaced()` — the inbox record+decide circuit (suite.py:789, 1153)
- Voice-first STT→RHM→TTS (suite.py voice endpoints)
- `guard()` / `POLICY` / `walkthrough` mode — the governance layer

**Touch findings:**
- Batch compose path — synthesis Bucket C-b (generate button + show-through UX)
- Mockup-aware stop — must resolve locus carrier correctly (Bucket C-c / T0-KEYSTONE fix)
- Dispatch entry seam — `surface_build_intent` → `dispatch_decision` (suite.py:7895 empty scope)
- `ingest_comment()` path — twin data collection on every annotate (suite.py:3995)

**Unify findings:**
- Walkthrough mode connection to tour-start (G2: dial-select → `start_walkthrough`)
- FE show-me lane mounts the walkthrough engine (not building a new one)
- Mockup-aware RAISES on unregistered addresses — registry extension or HTML tolerance

### 4. Canvas/FE (`area://canvas`)
**File:** `coverage/canvas.md` (1100+ lines)

**Key finding:** The FE is 1660-line monolith; IAS Phase 0 (F0 restructure) is a prerequisite for any parallel build.

**Use findings:**
- `useAppController.ts` — SSE dispatch-by-kind (decision/cognition events)
- Studio room (Review.tsx + StudioKit.tsx) — where the guided-review-surface lives
- Node shape, edges, canvas render — generic renderers (reflects-never-owns principle)

**Touch findings (IAS prerequisites):**
- F0: FE componentized + state container + layout shell
- F9: design-lint + design-critic gates (form = half of done)
- S0–S5: address grammar + registry + event-stamp + resolver + safety
- I1–I6: interaction model (click=indicate+consent)
- R1–R2: context auto-resolution + mock portal/DOM rendering

**Unify findings:**
- Operable Interface Group C = FE show-me lane → build once, share both
- FORM gate binds all surfaces in the studio room
- Portal mechanism (R1) enables live-window narration

### 5. Cognition (`area://cognition`)
**File:** `coverage/cognition.md` (1000+ lines)

**Key finding:** Concurrent Cognition (G0–G1 proven) is the perception layer — the engine behind per-stop comprehension.

**Use findings:**
- `_run_swarm()` — ~32 concurrent role runs batched on one 4B resident
- Injection edge (C1.3) — roles write to `run://<turn>/<role>`, inject into next part
- `_chat_context` / `_resolve_context_at` — the context-assembly half (suite.py:1322,1461,1943)
- `chat_parts()` — staged-response queue / streaming generator (suite.py:5264–5312)
- CC cascade produces the RHM's per-locus explanation (verified in synthesis §0)

**Touch findings:**
- Rule-based routing (C3.1) — deterministic gates, not confidence
- Part-queue is the substrate for text-streaming (Bucket B)
- Injection-edge is the architecture behind cancel path (Bucket C-d)

**Unify findings:**
- Don't duplicate text-stream — wire to CC's `chat_parts` streaming
- Streaming text-cancel extends the injection-edge cancel mechanism
- `_resolve_context_at` at each walkthrough stop triggers the CC cascade

### 6. Voice (`area://voice`)
**File:** `coverage/voice.md` (350+ lines)

**Key finding:** Voice is ready (Kokoro TTS + whisper.cpp STT + VAD/barge-in). One gap: voice focus passthrough.

**Use findings (BUCKET A, READY):**
- Kokoro TTS — running, streaming-capable
- whisper.cpp STT — local default, built
- VAD/barge-in loop — bridge.py:780–793

**Unify findings:**
- Voice focus passthrough — `/api/voice/stream` needs `focus` arg (chat_parts accepts it) → one-seam fix
- Step 2 of synthesis sequence: walkthrough↔chat + voice focus

---

## Relation Summary Table

| Territory | Use | Touch | Unify | Relate |
|-----------|-----|-------|-------|--------|
| **Design Corpus** | RHM Organ / IAS substrate / OCS dispatch / CC perception / Voice / Wire | 17-surface map / Operable Interface / Remediation Spec / Mockup corpus | RHM=this build / FE lane=both / Studio superseded / Pipeline opener / FORM prerequisite | CC scale / Wire dispatch / Coherence / Twin data / Idea-capture |
| **Substrate** | Address grammar / Event-stamp / ui→code resolver / R2 context / Safety | Gram extension / Mockup scheme / resolve_scope | `doc://`/`area://` formalize / `mockup://` register / mockup dispatcher | Coherence detection |
| **Runtime** | Walk engine / Batch compose / Inbox record / Voice STT→RHM / Governance | Mockup stop / Dispatch entry / Comment ingestion | Walkthrough ready / Show-me mounts / Mockup RAISES | Twin training / Generative WHY |
| **Canvas** | SSE dispatch / Studio room / Generic render | IAS F0/F9/S0–S5/I/R / FORM gate | One monolith → F0 prerequisite / Group C = lane / Portal mechanism | — |
| **Cognition** | Swarm executor / Injection edge / Context-assembly / Part-queue / Explanation | Routing rules / Streaming substrate / Cancel path | Don't duplicate stream / Wire to chat_parts / Resolve→cascade | — |
| **Voice** | Kokoro TTS / whisper STT / Barge-in | Focus passthrough | One arg → Bucket B step | — |

---

## Build Dependency Graph

```
PREREQUISITE (IAS Phase 0):
  └─ C0: corpus-import (design-system.css, tokens.json, check.py)
  └─ F0: FE restructure (componentize, state container, layout shell)
  └─ S0–S5: address floor (grammar, registry, event-stamp, resolver, safety)
  └─ I1–I6: interaction model (click=indicate+consent)
  └─ R1–R2: context + rendering (auto-resolve, portal, DOM)
     ├─ S3 (`ui://→code://`) for generate-for-mockups scope
     └─ F9: design-lint + critic gates

GRS MAIN BUILD (parallel after IAS Phase 0):
  ├─ Bucket A: walkthrough engine (READY, wire FE show-me lane)
  │  ├─ A1: Queue / A2: idea-capture / A3: start_guide entry
  │  ├─ B1–B5: sequencer / B2: annotate / B3: mark-up
  │  ├─ C1–C4: present-anywhere (portal, HTML injection, element-level)
  │  ├─ D1–D5: inbox record + COA lifecycle
  │  ├─ E1–E5: channel-back (voice in, dialogue, moderation)
  │  └─ F1–F4: voice STT→RHM→TTS
  │
  ├─ Bucket B: text-streaming walkthrough
  │  ├─ B1: wire CC chat_parts() to each stop
  │  ├─ B2: voice focus passthrough (one arg to chat_parts)
  │  └─ B3: streaming cancel path (extend injection-edge)
  │
  ├─ Bucket C: mockup-aware + generate-for-mockups
  │  ├─ C-a: resolve_scope for mockup file targets (suite.py:7895 branch)
  │  ├─ C-b: batch compose + approve (generate button, offer-with-options card)
  │  ├─ C-c: mockup-aware stop (RAISES on unregistered, registry extension or HTML tolerance)
  │  ├─ C-d: streaming text cancel (inject-edge cancel mechanism)
  │  ├─ C-e: temporal deixis via event-address-stamp (S2)
  │  ├─ C-f: annotate verb + ingest_comment (twin data collection)
  │  ├─ C-g: governance modes (G1–G4)
  │  └─ C-h: FE show-me lane (Bucket C of Operable Interface, portal-based overlay, next/back/dwell)
  │
  └─ Schema fixes (prerequisite or parallel):
     ├─ T0-WIRE: generate+approve entry seam
     ├─ T0-KEYSTONE: mockup-aware stop locus resolution
     ├─ T0-CARD: bare-UUID → show-through UX
     ├─ T1-EMIT: exactly-once dispatch guarantee (FIX BEFORE Bucket C-a/b dispatch)
     ├─ Grammar: formalize `mockup://` in SCHEMES (or declare exception)
     └─ Grammar: propose `doc://`/`area://` extension (forward, not prerequisite)

PARALLEL UNIFICATIONS (assume during GRS build):
  └─ Merge Walkthrough Organ (vault) + GRS synthesis into ONE criteria
  └─ Mark Operable Interface Group C fulfilled (by GRS FE lane)
  └─ Resolve Remediation Spec T0-WIRE/T0-KEYSTONE/T0-CARD
  └─ Note Project→Product Pipeline's future-consumer path opens (A4)
```

---

## The Biggest Unification Opportunity (Stated Plainly)

**The RHM Walkthrough Organ Criteria (vault) and the guided-review-surface synthesis (repo) are the same design. They should be MERGED into one completion criteria document before loop-prep runs.**

The merge adds:
1. Vault criteria A–G (queue · sequencer · present-anywhere · record · channel-back · voice · governance) as the outer circuit
2. Synthesis Bucket C-a/c (generate-for-mockups · mockup-aware stop) as the mockup-specific extension
3. Operable Interface Group C as fulfilled by the same FE build
4. Remediation Spec items (T0-WIRE / T0-KEYSTONE / T0-CARD) as resolved
5. Project→Product Pipeline's future-consumer note as an `origin: generative` track that opens once A4 lands

**That merged document would be loop-prep's completion criteria — the one artefact that makes this "THE unifying human-interaction organ" rather than "a review surface."**

---

## Forward-Design Points (Not Blockers)

- **`doc://` / `area://` grammar extension** — address system reaching its own build. Enables RHM walking vault notes as tour stops. Forward design point, not prerequisite.
- **Mockup-stop unregistered tolerance** — either extend registry-per-mockup or allow HTML-injected narration. Design choice, resolved by Bucket C-c implementation.
- **Part grain for streaming** — sentence / beat / paragraph? Mode-dependent? CC registry's first-cast decision.
- **R (reserved slots) for concurrent cognition** — R=4 proposed; trade snappier turns (larger R) vs richer cognition (smaller R).

---

## Evidence Grounding

Coverage conducted territory-by-territory (no query substitution):
- **Repo `build-prep/`:** claude-design/ + coherence/ + concurrent-cognition/ + guided-review-surface/
- **Vault `build-prep/`:** 96+ documents including design triads, deep scans, context foundation, project briefs, operational specs
- **Codebase:** contracts/ + store/ + fabric/ + runtime/ + canvas/ (full-directory walks, function-body traces)

Evidence marks:
- **Observed(file:line)** = read directly in documents/code
- **Inferred** = pattern-matched from architectural intent
- **Unification-opportunity** = explicitly names where this build subsumes designed work

---

**Sweep completed 2026-06-08.** Findings integrate across six coverage documents (design-corpus.md, substrate.md, runtime.md, canvas.md, cognition.md, voice.md) into this summary. Each area's complete evidence trail is in its respective file.
