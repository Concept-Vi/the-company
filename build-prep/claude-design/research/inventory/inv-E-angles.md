# Inventory E — Four Angles Census

Fast coverage pass across build-prep (in-repo), vault design docs, branch deltas, and the interface worktree. Maps WHERE things live and what each angle adds/changes.

---

## Angle 1: /home/tim/company/build-prep/ (in-repo)

**Scope:** Only concurrent-cognition/ is present (no root-level build-prep docs).

| What | Appears to be | PRIORITY | Note |
|------|---------------|----------|------|
| 01-role-registry.md | Roles as registered entities — slot-able, queryable | no | Reference for role lifecycle |
| 02-graph-substrate-reuse.md | Reusing canvas graph model for cognition state | no | Architectural choice doc |
| 03-concurrency-and-injection.md | How concurrent roles fire and inject results | YES | Core mechanism for staged cognition |
| 04-staged-response-queue.md | Queue model for the output stream | no | Substrate detail |
| 05-voice-stream-coupling.md | How TTS/voice integrates with part emission | YES | Voice/cognition binding |
| 06-rendering.md | Display of concurrent cognition states | no | Frontend concern |
| Concurrent Cognition — Completion Criteria.md | All 13 criteria (verified-by-use/needs-tim split) | YES | **PRIORITY** — full build closure marker |
| Concurrent Cognition — Implementation Guide.md | Phase-by-phase build stages | YES | **PRIORITY** — build roadmap |
| Concurrent Cognition — Research Synthesis.md | Exploration findings folded into design | no | Reference synthesis |
| DECISIONS.md | Design decisions made during the build | YES | **PRIORITY** — decision record |
| COMPOSABLE-CONCURRENCY-SURFACE.md | Tim's sequencer/timeline vision + RHM reuse + 5 seams | YES | **PRIORITY** — the unifying surface design |
| AUTHORING-FE-HANDOFF.md | Frontend contract for role authoring | YES | Build boundary doc |
| 00-LANDSCAPE.md | Exploration scope + alternatives | no | Context setting |
| review/R1-*.md (5 docs) | Consistency, seams unification, flow trace, adversarial, reference verification | no | Review artifacts |
| review/R2-*.md (4 docs) | Completeness, rule determinism, chat refactor, resource math | no | Review artifacts |
| explore/E*.md (5 docs) | Application designs, cognition UX, alternatives, mode activation | no | Exploration artifacts |
| broader/B*.md (5 docs) | External architectures, node mechanisms, broader applications, model registry, SDD coordination | no | Landscape research |

**Summary:** Concurrent-cognition is FULLY BUILT and DOCUMENTED — 13 completion criteria verified by use. This is Tim's staged-cognition vision, ready to be integrated.

---

## Angle 2: THE VAULT build-prep

### Path A: Counterpart vault (`/mnt/c/Users/Workstation001/Documents/Claude/Projects/counterpart/the Company/build-prep/`)

252 markdown files total. Core design triads + architecture + context sequence:

| What | Appears to be | PRIORITY | Note |
|------|---------------|----------|------|
| **DESIGN TRIADS (3×3 docs each)** | — | — | — |
| Interactive Addressed Surface — {Completion, Implementation, Research} | Addresses as navigation/launch primitives; operator approval + reach gates | YES | **PRIORITY** — defines the primary surface |
| Decision-to-Implementation Wire + Product Surface — {Completion, Implementation, Research} | Decision→autonomous implement→verify loop + surface integration | YES | **PRIORITY** — autonomous agent wire |
| Operable Composition Surface — {Completion, Implementation, Research} | Node config + model registry + build/run/rerun chains + live SSE | YES | **PRIORITY** — the runtime surface |
| **SINGLE DOCS** | — | — | — |
| Operable Interface — Completion Criteria.md | Latest iteration; needs-tim marker on aesthetic | YES | Current state |
| Self-Modifying Interface — Direction, Operator Profile & Loop Extensions.md | The feedback loop extension (worktree builds this) | YES | Interface feedback arch |
| Surfaced Findings — design corpus to build.md | 19,361-file scan findings + 770 design-doc extraction | no | Corpus reference |
| **CONTEXT SEQUENCE (context-00 through context-16)** | — | — | — |
| context-01 to context-16.md | Vi the vision → Tim the origin → Company architecture → Five invariants → Interface/RHM → Foundation laws → Cognitive fabric → Current state → AppData test → Organs → Genetic kernel → Open threads → THE SURFACE → Recall/Identity → Game-engine view → Failure modes | no | Full architectural narrative |
| context-99-glossary.md | Terminology + definitions | no | Reference |
| **DECISIONS & CONTRACTS** | — | — | — |
| Decisions and Options.md | Decision log with options explored | no | Decision record |
| Codebase-Upgrade & Multi-Graph Grounding — D3 Brief.md | D3 decision (one substrate, per-type views) | YES | Resolved design decision |
| contracts/ (C6, C7, D3, D9, D13) | Context-variable interface, MCP tool surface, design decisions | no | Contract specs |
| **OTHER CORE** | — | — | — |
| Company Build Hub.md | The hub + Decisions surface in counterpart vault + canvas interface | YES | Build coordination doc |
| Coherence Gate — Spec.md | Operator-facing coherence enforcement | no | Safety mechanism |
| Collective Cognition — the context-resolution spine.md | RHM's context/variable resolution layer | YES | Core RHM architecture |
| Autonomous Implementation Engine — Field Notes.md | The self-build wire's empirical findings | no | Implementation reference |

**Summary:** Vault build-prep is the CANONICAL DESIGN CORPUS. 252 files spanning context, decisions, three major surface triads, and contracts. The three-triad-per-phase pattern is load-bearing.

### Path B: Canonical vault (`/mnt/c/Users/Workstation001/Documents/Obsidian Builder/notes/architecture/`)

~50 architecture docs covering patterns, designs, and implementation landmarks.

| What | Appears to be | PRIORITY | Note |
|------|---------------|----------|------|
| **(Blueprint) AI-Driven Build System & Open Gaps** | The overall build philosophy + gap inventory | no | Landscape |
| **(Design) Decision Sequence Engine** | How decisions flow to implementation | YES | Core workflow |
| **(Design) Dispatch Triangle** | Vault ↔ Claude Code delivery circuit | YES | Handoff mechanism |
| **(Design) Sequences as Universal Substrate** | How one user commands a vast system via sequences | YES | **PRIORITY** — foundational pattern |
| **(Design) Sequences in Practice** | Inbox, awareness, skills, visualization | YES | Operational form |
| **(Design) Wizard Interaction Pattern** | Conversational step-by-step proposal/refinement | no | UI pattern |
| **(Design) Type-Template Synchronization** | Registry-driven form generation | no | Schema pattern |
| **(Design) System Registry Architecture** | Master registry design | YES | Core data structure |
| **(Note) System Architecture Overview** | High-level coherence view | YES | Map of maps |
| **(Note) Fractal Composition Across All Layers** | Recursive pattern reuse | YES | **PRIORITY** — Tim's founding pattern |
| **(Note) Principles to Implementation Map** | How abstract principles become code | YES | Translation layer |

**Summary:** Canonical vault architecture docs are HIGHLY CONNECTED to the Company surface designs. The "Sequences" pattern is repeated across multiple docs — this is THE foundational primitive.

---

## Angle 3: THE BRANCH DELTAS (from /home/tim/company/)

### concurrent-cognition

**Status:** BUILT. Merged from night-build, 20 commits since merge.

**Files changed:** 4 files (cleanup mode) — STATE.md, ops/cli/app.py, runtime/suite.py, tests/suite_health_acceptance.py
- **Deletions:** 146 lines (test/dead code removal)
- **Net:** Minimal churn — branch is STABLE

**Key commits (last 5):**
- 49debc4: gap-hunt fix — cross-session seam
- fbbcda0: conv_reach wire — build-intent blast_radius
- 76fc0c2: merge main into concurrent-cognition
- 3b6b6b3: self-build audit-ledger unification
- 4ac289e: **Composable Concurrency Surface** — the net-new core (sequencer/timeline + allocator + 3 research threads folded)

**Appears to be:** Concurrent cognition fully implemented + proven by use + integrated with decision-wire. Modest cleanup phase.

**PRIORITY:** Deep-read the Composable Concurrency Surface + auth backend + voice coupling commits if building on this.

---

### interactive-surface-build

**Status:** ACTIVE. Has NOT been merged to main.

**Files changed:** 217 files (~3,500 insertions, ~31,500 deletions = massive refactor).

**Major areas affected:**
- Runtime: bridge (476 lines rewrite), suite (2138 line rewrite, net reduction = consolidation)
- Voice: lifecycle (262 line rewrite), engines refactored, STT scaffold
- Runtime/roles/rules: DELETED (moved to another pattern)
- Tests: 30+ test files deleted (coverage migrated)
- Design: mockups + studio + redesign pass

**Key commits (last 5):**
- ac5b98a: merge main (night-build) into interactive-surface-build
- caaf812: voice/orpheus graphs-default + 4096 ctx
- ecc6dc0: ops: the company CLI (one console pattern)
- 3c85c44: X16 FORM variants (ripple treatments for Tim's pick)
- 3c3c2b2: X12 vector index — semantic ranking live

**Commits 3-30 are X-numbered (X1→X17):** Staged delivery of surface features:
- **X10–X17:** Code dependency graph (structural edges) → semantic ranking → operator reach approval → form surface
- **X7–X9:** Composition, blast radius (structural neighbors), degrade-with-warning
- **X1–X6:** Earlier stage

**Appears to be:** The OVERNIGHT-BUILT interface redesign + the Operable Composition Surface building in parallel. Form aesthetic deferred to redesign pass. NEEDS MERGE + WALKTHROUGH.

**PRIORITY:** YES. This is the active overnight build (2026-06-05+). Read the X-numbered commits in order (they ARE the staged delivery). **CRITICAL: The form/aesthetic is held on Tim's A/B/C decision — not in the code yet.**

---

### night-build

**Status:** Basis for concurrent-cognition + interactive-surface-build merges.

**Files changed:** 331 files (~2,400 insertions, ~67,000 deletions = major consolidation).

**Key commits (last 5):**
- a47f030: retire dead RHM text-parser (chat→native tool-calling)
- 6b43bb3: voice AGENTS.md + GPU-ear registry
- 97811a5: STT fix (explicit .to(DEVICE))
- 34f3018: suite-fix (mode-discipline, cross-process lock)
- 3604ab1: **RHM native tool-calling + mode×context affordance** + D9/D13

**Appears to be:** Consolidation commit bringing together voice remediation, RHM rewrite (to native tool-calling), and ops redesign. Serves as the base for other branches.

**PRIORITY:** NO (base case; integrated into other branches). Reference for mode-discipline + STT GPU changes.

---

### overnight-20260605

**Status:** STALE. Historical checkpoint.

**Key commits:** Same as night-build first 10 commits (historical duplicate).

**PRIORITY:** NO (superseded by night-build).

---

### operable-interface-build

**Status:** STALE/MERGED. Last commit is a "handoff" doc.

**PRIORITY:** NO. This work moved to interactive-surface-build (night-build merged in, unifying the two).

---

## Angle 4: THE WORKTREE (/home/tim/company-interface)

**Worktree branch:** operable-interface-build

**Files changed:** 107 files (~4,450 insertions, ~15,280 deletions = net consolidation).

**Major areas:**
- Runtime: suite (massive simplification), bridge rewrite, governance refinement
- API: route additions (studio feedback, voice status)
- Design: mockups + studio review portal
- Voice: auto-listen + barge-in + speakable layer
- Corpus: chat-gear addresses folded into A3 Settings

**Key commits (last 10):**
- 9890437: wire the feedback route + studio same-origin
- 6fa57b9: **the redesign mockups + the mockup studio** (the review portal)
- 5a1f417: **the gold-primary living-instrument sweep across the real app**
- 067db56: voice auto-listen + barge-in (V-B)
- e2b95bb: corpus retire, fold into A3 Settings
- e366a6d: **a speakable layer** (V-C, V-D)
- 7d418d5: unify point-vs-click coherence
- 8f8a423: merge main into operable-interface-build (9 conflicts resolved)

**Appears to be:** The SURFACE REDESIGN in progress. Gold-primary aesthetic applied, studio (design review portal) wired, voice layer refined, settings unified.

**PRIORITY:** YES. This is where the VISUAL redesign lives. The "mockups" commit is the design corpus entry point. Form/aesthetic choices visible here.

---

## ANGLE MAP (WHERE THINGS LIVE)

### The Triads Pattern

Three **loop-prep triads** exist in the codebase:

1. **Concurrent Cognition** (in-repo build-prep/) — BUILT ✅
   - Completion Criteria, Implementation Guide, Research Synthesis
   - Concurrent-cognition branch merged; integrated into night-build
   - 13 criteria verified by use + 5 needs-tim items

2. **Interactive Addressed Surface** (vault build-prep/) — DESIGNED ✅
   - Completion Criteria, Implementation Guide, Research Synthesis
   - Addresses as navigation/launch primitives
   - Ready to implement (contract: authoring-FE-handoff exists)

3. **Operable Composition Surface** (vault build-prep/) — IN-BUILD 🔨
   - Completion Criteria, Implementation Guide, Research Synthesis
   - Runtime surface: node config, model registry, build/run/rerun, live SSE
   - The X1–X17 staged delivery happening on interactive-surface-build branch

### The Surfaces Hierarchy

```
Tim's Interface (Commander's Bridge)
 ├─ Altitude Layer (F1) — Feedback + learning + form aesthetic
 │  └─ worktree: operable-interface-build (redesign mockups live here)
 │
 ├─ Operable Composition Surface (C-level API)
 │  └─ interactive-surface-build (X-numbered staged build, needs merge)
 │
 ├─ Interactive Addressed Surface (Navigation/Launch)
 │  └─ vault design (ready to implement, contract exists)
 │
 └─ Collective Cognition (RHM Context-Resolution Spine)
    └─ concurrent-cognition branch (BUILT, integrated)
```

### The Code Locations

| Component | Primary Location | Status | Note |
|-----------|-----------------|--------|------|
| **Concurrent Cognition Design** | /home/tim/company/build-prep/concurrent-cognition/ | ✅ BUILT | Merged; stable |
| **Concurrency Surface Spec** | build-prep/concurrent-cognition/COMPOSABLE-CONCURRENCY-SURFACE.md | ✅ | Unifying doc |
| **Operable Composition Build** | /home/tim/company (interactive-surface-build branch) | 🔨 IN-BUILD | X1–X17 staged; needs merge |
| **Interactive Surface Design** | /mnt/c/Users/Workstation001/.../build-prep/Interactive Addressed Surface — {3 docs} | ✅ DESIGNED | Contract exists |
| **Redesign + Studio** | /home/tim/company-interface (operable-interface-build worktree) | 🔨 IN-PROGRESS | Mockups + form wired |
| **Full Context** | /mnt/c/Users/Workstation001/.../build-prep/context-* (16 docs) | ✅ | Canonical narrative |
| **Company Build Hub** | /mnt/c/Users/Workstation001/.../build-prep/Company Build Hub.md | ✅ | Coordination hub |
| **Sequences Pattern** | /mnt/c/Users/Workstation001/Documents/Obsidian Builder/notes/architecture/ (Design) Sequences as Universal Substrate | ✅ | **FOUNDATIONAL** |

---

## TOP PRIORITY DEEP-READS

1. **Composable Concurrency Surface** (`/home/tim/company/build-prep/concurrent-cognition/COMPOSABLE-CONCURRENCY-SURFACE.md`)
   - What: Tim's sequencer/timeline vision + RHM reuse + 5 integration seams
   - Why: Unifies cognition + composition + voice coupling
   - Length: Should be ~2–5 KB (design doc density)

2. **Interactive Addressed Surface — Completion Criteria** (`vault build-prep/Interactive Addressed Surface — Completion Criteria.md`)
   - What: Full spec of the addresses + navigation model
   - Why: Primary surface; ready to implement
   - Status: Contract exists (see AUTHORING-FE-HANDOFF.md in vault)

3. **Operable Composition Surface — Implementation Guide** (`vault build-prep/Operable Composition Surface — Implementation Guide.md`)
   - What: Phased build steps for the runtime surface
   - Why: Maps X1–X17 onto architectural pieces
   - Status: Actively being built on interactive-surface-build

4. **X-Numbered Commit Series** (interactive-surface-build, commits akin to "X16: operator-approves-the-reach" through "X1: ...?")
   - What: Staged delivery of Operable Composition Surface
   - Why: Each commit is a feature + proof-of-function
   - Count: ~17 commits (read titles in order to trace dependencies)

5. **Redesign Mockups Commit** (worktree operable-interface-build, commit 6fa57b9)
   - What: The visual redesign corpus + studio review portal
   - Why: Where aesthetic decisions and form live
   - Note: Studio wireframed; form choices held on Tim's A/B/C decision

6. **Vault Architecture: (Design) Sequences as Universal Substrate** (`canonical vault/notes/architecture/`)
   - What: How one user commands a vast system via sequences
   - Why: The FOUNDATIONAL PATTERN — repeated everywhere
   - Link: Connects to Operable Composition Surface + Decision-to-Implementation Wire

---

## ANGLE SURPRISES / UNEXPECTED SCALE

- **Vault build-prep is MASSIVE:** 252 files. The "context-00 through context-16" narrative alone is a full architectural opus. Equivalent to a PhD thesis in scope.

- **Interactive-surface-build has 17 staged features (X1–X17):** Each is tested, proven, addressable. This is not typical feature branching; it's a DELIVERY SEQUENCE. Merging it requires walking through in order.

- **Three active triads simultaneously:** Concurrent cognition (done), Interactive Addressed Surface (designed), Operable Composition (in-build). They are NOT sequential; they compose. The pattern is **fractal.**

- **The worktree redesign is NOT in interactive-surface-build:** It's a separate worktree evolution. Merging the branch doesn't capture the visual redesign; the worktree is the truth for form/aesthetic.

- **Branch naming is confusing:** operable-interface-build (worktree, stale) ≠ interactive-surface-build (in-repo branch, ACTIVE). The live work migrated; the old worktree branch is historical.

---

## NEXT STEPS (FOR TIM)

**If you want to understand the big picture:**
- Start: vault's context-01 through context-05 (Vi vision → Company → Five invariants → Interface/RHM)
- Then: Composable Concurrency Surface + Sequences as Universal Substrate (the two unifying patterns)
- Then: Walk the three triad designs in order

**If you want to merge interactive-surface-build:**
- Read the X-numbered commits (they are the staged spec)
- Walk the X12 (vector index) + X14 (blast_radius) + X16 (operator approval) chain
- Confirm form/aesthetic choice with the worktree redesign mockups

**If you want to finalize the interface:**
- Worktree redesign is the truth (gold-primary, mockups wired, studio operational)
- Decide on form aesthetic (A/B/C choice Tim is holding)
- Then walkthroughs + merge both interactive-surface-build AND the worktree

