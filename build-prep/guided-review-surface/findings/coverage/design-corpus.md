# Coverage Round — `area://design-corpus`

> **What this is.** A full-coverage sweep of the DESIGNED corpus in two zones:
> `area://design-corpus` = `build-prep/` (repo) + vault build-prep
> (`/mnt/c/Users/Workstation001/Documents/Claude/Projects/counterpart/the Company/build-prep/`).
> Coverage was by territory (ls + skim + section-read), NOT by query.
> The four relation kinds tracked: **USE** (faculties the guided-review-surface composes) ·
> **TOUCH** (shared designs, contracts, hot surfaces) · **UNIFY/IMPROVE** (the big one — what this
> build could subsume or be the first instance of) · **RELATE** (same shape recurring).
> Evidence marks: **Observed(doc/section)** = read directly in design files ·
> **Inferred** = derived from the design's stated intent · **Unification-opportunity** = explicitly
> calling out where the guided-review-surface IS the same organ as what's designed elsewhere.

---

## 0 · The corpus in one picture

Two zones, fully enumerated:

**Repo build-prep (`/home/tim/company/build-prep/`):**
- `claude-design/` — APPLICATION-STRUCTURE-PACK.md, AUTHORING-UI-BRIEF.md, BACKEND-SEAM-PACK.md,
  CONVERGENCE-WALKTHROUGH.md + research/
- `coherence/` — ANCHOR.md + corpus-chain + semantic-layer docs + findings/
- `concurrent-cognition/` — full triad (Criteria, Guide, Research Synthesis) + LANDSCAPE, DECISIONS,
  COMPOSABLE-CONCURRENCY-SURFACE, AUTHORING-FE-HANDOFF + broader/ + review/
- `guided-review-surface/` — this build's own docs

**Vault build-prep (60+ top-level files + subdirs):**
The designed corpus holds five complete loop-prep triads (Operable Composition Surface · RHM Walkthrough
Organ · Interactive Addressed Surface · Concurrent Cognition · Operable Interface), three deep-scan
ground-truth files (RHM Deep Scan parts 1–3), a ~17-surface APPLICATION-STRUCTURE-PACK (repo), the
voice + decision-wire triads, the context-00–16 foundation files, the Project→Product Pipeline
Blueprint, and the Unification+FORM Master Remediation Spec.

**The finding that shapes the whole sweep:**
The APPLICATION-STRUCTURE-PACK.md §§3–4 names the **Sequences Primitive** (`resolve → present/work →
persist → next/trigger`) as the one relational loop the Company runs at every scale. The guided-review-
surface is, per the synthesis, the **human-facing face that composes the Sequences primitive**. Every
designed surface and organ in the corpus is ALSO an instance of or consumer of that same primitive. This
means the guided-review-surface does not relate to other designs the way a UI panel relates to a data
model — it IS the mechanic the whole Company runs on, pointed at human-review as its first consumer.

Observed(APPLICATION-STRUCTURE-PACK.md:504-541 + context-04-the-five-invariants.md §II).

---

## 1 · USE — Faculties the guided-review-surface composes

These are designed capabilities that the surface literally calls, renders through, or depends on to
function. Each is a seam the build must wire.

### 1.1 The RHM Walkthrough Organ (vault: RHM Walkthrough Organ — triad)

**Relation: USE (the engine core).**
The guided-review-surface's walkthrough engine IS the RHM Walkthrough Organ. The organ's triad
(Criteria/Guide/Research Synthesis, vault) specifies the full `SURFACE → PRESENT → RESPOND → ACT`
circuit. Every Bucket A/B item in the synthesis maps to a grounded piece of the organ:

- `present_current` / `start_guide` (Walkthrough Criteria B1–B5) — the sequencer the surface drives.
  Observed(RHM-Walkthrough-Research-Synthesis §2 + suite.py:6198-6337 per synthesis §2).
- The `coa()` / `resolve_surfaced()` / inbox lifecycle (Criteria D1–D5) — the record+decide circuit.
  Observed(RHM-Walkthrough-Research-Synthesis §1 `coa`:789, `resolve_surfaced`:1153).
- Voice first / STT → RHM → TTS (Criteria F1–F4) — already built on the voice circuit.
  Observed(RHM-Walkthrough-Research-Synthesis §2 voice endpoints; synthesis BUCKET A voice row).
- `guard()` / `POLICY` / `walkthrough` mode (Criteria G1–G4) — the governance layer the surface must
  wire.

**What it means for the build:** the guided-review-surface does NOT need to invent a walkthrough engine
— it is landing INTO a designed, partially-built organ. Bucket A ready pieces in the synthesis align
directly with Criteria A (queue), B (sequencer), C (present anywhere), D (record), E (channel back).
The net-new build from the synthesis (Bucket C) is the MOCKUP layer the organ spec does not yet address
— the organ was designed for live `ui://` nodes; the guided-review-surface extends it to `mockup://`.

**Unification-opportunity:** the "this guided-review surface" and the "RHM Walkthrough Organ" ARE the
same organ. The vault triad is the most detailed existing design for it. The build should treat the
Walkthrough Criteria as a PARENT spec and extend it (not ignore it or duplicate it). The synthesis's
Bucket C items (generate-for-mockups, mockup-aware stop, batch compose, FE show-me lane) are the
extensions that make the organ real for the mockup-review use case — which is its founding mission.

Observed(RHM-Walkthrough-Research-Synthesis §"The general human-interaction primitive" + synthesis
§0 "designed-general, built-partial").

---

### 1.2 The Interactive Addressed Surface (vault: Interactive Addressed Surface — triad)

**Relation: USE (the substrate floor).**
The synthesis §1 explicitly calls the Interactive Addressed Surface the "substrate floor" — "every
element addressable + annotatable + context-resolving." The guided-review-surface rides on top of it.

Key faculties it provides that the build uses:
- `ui://` address grammar + `UI_REGISTRY` (IAS S0–S1) — the addressing scheme for every element the
  surface walks to.
  Observed(Interactive Addressed Surface — Completion Criteria GROUP 1 SPINE S0-S5).
- Event-address-stamp keystone (IAS S2) — stamping `ui://` on every event = the locus-trail substrate
  for temporal deixis (synthesis Bucket C-e).
  Observed(IAS Research Synthesis §R1 SEAM 1 fs_store.py:185-213).
- `ui://→code://` resolver (IAS S3 / synthesis S3) — maps locus to scope for generate-for-mockups.
  Observed(IAS Research Synthesis §R1 SEAM 5).
- Click-INDICATES-and-CONSENTS interaction model (IAS I1–I6) — the consent model the guided-review-
  surface inherits. IAS decided: click = indicate + consent; RHM proposes; governance + see-approve.
  Observed(IAS Completion Criteria INTERACTION group heading decision note).
- R2 context auto-resolution (IAS R1–R2) — the `_chat_context` grounding at each locus.
  Observed(synthesis §2 BUCKET A R2 row: suite.py:3036-3086).
- Cross-process safety (IAS S4) — the concurrency risk the surface must not worsen.
  Observed(IAS Research Synthesis §R1 SEAM 8b).

**What it means for the build:** The IAS build (in a worktree, not merged per memory context) is a
PREREQUISITE or a PARALLEL build to the guided-review-surface. If the IAS criteria are not met (S0–S5,
F0–F9, I1–I6, R1–R2, L1–L7), the guided-review-surface has no stable substrate to walk on. The build
sequence in the synthesis (step 1 text-streaming, step 2 walkthrough↔chat, step 3 FE show-me lane)
maps to IAS phases 0→1→2→3.

**Unification-opportunity:** The guided-review-surface is the FIRST CONSUMER of the IAS — the build
that proves the IAS is real by using it. Building the guided-review-surface without building (or
assuming) the IAS is the path that built a studio that couldn't walk its own mockups. The synthesis
already names this (§0 "comprehension path was not active").

Observed(synthesis §1 "Interactive Addressed Surface is the substrate floor").

---

### 1.3 The Operable Composition Surface (vault: Operable Composition Surface — triad)

**Relation: USE (the act-half).**
The Operable Composition Surface (OCS) is the "configure-nodes-and-run" engine — what gets built and
run when the Commander approves a change from the guided-review-surface.

Key intersections:
- The wire's `dispatch_decision` → `implement.py` → `claude -p` → git path (OCS F2–F3: "route a result
  to the decision surface" + "choose an action from an output") is the ACT half of the guided-review
  circuit. Observed(OCS Completion Criteria GROUP 5 § F2-F3; synthesis BUCKET A "singular wire" row).
- Config-write (OCS A3) and multi-graph (OCS C4) are capabilities the surface would invoke when
  approving a generated change. Observed(OCS Criteria A3, C4; Research Synthesis "reshaping finding").
- The SSE stream (OCS D5 / IAS L2) that shows live build progress is what the surface displays after
  the Commander clicks generate+approve.

**What it means for the build:** The OCS is the downward path from the guided-review-surface's approve
action. It does not need to be rebuilt for this build, but its `drive_dispatchable` / `dispatch_decision`
seam is the dispatch entry point for generate-for-mockups (synthesis Bucket C-a). The MOCKUP-specific
scope resolver (Bucket C-a) needs to produce an OCS-compatible dispatch target — a `claude -p` scoped
to a `.html` file instead of `code://`.

---

### 1.4 Concurrent Cognition (repo build-prep/concurrent-cognition/)

**Relation: USE (the perception layer — how the RHM "sees" each locus).**
The synthesis §1 states: "Collective Cognition is HOW the RHM perceives each locus (looking = address →
auto-resolve)." The Concurrent Cognition build (G0 spike complete + G1 engine proven per Criteria
C0.1–C0.5, C1.1–C1.6) is the architecture that makes the RHM's per-locus comprehension work.

Key intersections:
- The `_chat_context` / `_resolve_context_at` grounding at a locus (R2 in synthesis) is the
  context-assembly half of Concurrent Cognition's cascade.
  Observed(CC Research Synthesis: "The address→resolve→inject SHAPE exists, but injection is NET-NEW").
- The injection edge (CC C1.3) — roles writing to `run://<turn>/<role>` and injecting into the next
  part — is the mechanism that makes "here's what I know about this address" land in the RHM's reply at
  each walkthrough stop.
  Observed(CC Criteria C1.3 injection edge + run:// addressing).
- Rule-based routing (CC L2 / G3) is the deterministic-gate principle the guided-review-surface inherits
  for its consent model. The CC build proved: routes are RULES over resolved values, never confidence.
  Observed(CC Criteria C3.1 "determinism ENFORCED not asserted").
- The staged-part queue (CC G4) is the architecture behind text streaming (synthesis Bucket B "streaming
  text chat") — `chat_parts()` is the CC streaming generator already used in voice.
  Observed(synthesis BUCKET B "streaming text chat" row: chat_parts suite.py:5264-5312).

**What it means for the build:** CC is not just a consumer of the guided-review-surface — it is running
INSIDE the surface's comprehension loop. Each walkthrough stop triggers the CC cascade to build the
per-locus explanation. The CC build (which is proven at G0+G1 level) is the engine behind the
"verified comprehension" result in synthesis §0.

**Unification-opportunity:** The CC `_run_swarm` + injection edge is the architecture the synthesis's
Bucket C-d (live text streaming cancel path) extends. When the surface streams an explanation at a stop,
the CC part-queue IS the streaming substrate. The build should wire to CC's streaming primitives, not
add a parallel text-stream mechanism.

Observed(CC Research Synthesis "reuse-near-wholesale" + "net-new: parallel wave executor").

---

### 1.5 Voice stack (repo build-prep/concurrent-cognition/05-voice-stream-coupling.md + vault voice-research/)

**Relation: USE (the preferred input channel).**
The synthesis names voice-in as "one of the most ready legs" (BUCKET A). The voice research synthesis
(vault: Voice — Realtime Right-Hand-Man — Research Synthesis) confirms the full pipeline: Kokoro TTS
(running) + whisper.cpp STT (built, local default) + VAD/barge-in loop (built in bridge.py:780-793).

The one gap: voice focus passthrough — `/api/voice/stream` calls `chat_parts` with no `focus` arg.
Observed(synthesis BUCKET B "Voice focus passthrough": bridge.py:848 + chat_parts accepts focus).

**What it means for the build:** step 2 in the synthesis sequence (walkthrough↔chat + voice focus
passthrough) is a single-seam fix (one arg) that activates the most-ready input channel.

---

### 1.6 Decision→Implementation Wire (vault: Decision-to-Implementation Wire + Product Surface — triad)

**Relation: USE (the ACT station — governing dispatch from the surface).**
The wire is "built end-to-end, singular" per synthesis BUCKET A. The Decision→Wire Research Synthesis
confirms: `surface_build_intent` → `dispatch_decision` → `implement.py launch` → `claude -p` → git →
`revert_self_change` is the path. T0-WIRE (in the Remediation Spec) confirms the entry seam is
test-only today — that is the synthesis Bucket B "Batch DISPATCH leg."

Key facts from the wire design:
- The dispatch is airtight exactly-once per seam (Remediation Spec T1-EMIT warning notwithstanding).
- The MOCKUP-specific dispatch (Bucket C-a) needs a new `resolve_scope` branch that returns a file
  path scope (`design/mockups/<file>.html`) instead of an empty scope — the wire machinery reuses
  unchanged.
  Observed(synthesis BUCKET C item a: suite.py:7895 empty-scope DENY-ALL).
- `approve_reach` (synthesis D1) is already built at bridge.py:1499 — the Tim-decision is whether to
  surface it or keep it invisible.

**What it means for the build:** the guided-review-surface's "generate → approve → dispatch" path is a
re-entry into the wire via a new action class (mockup-edit) and a new `resolve_scope` branch. No new
wire architecture.

---

## 2 · TOUCH — Shared designs the surface modifies or is modified by

These are designs that the guided-review-surface build would change, or that would change behavior
for the surface if built.

### 2.1 The ~17-surface map (APPLICATION-STRUCTURE-PACK.md §4 + GUIDED-REVIEW-SURFACE.md)

**Relation: TOUCH (the surface IS one of the 17).**
The APPLICATION-STRUCTURE-PACK §4 lists 17 designed surfaces with status. The guided-review-surface
spans three of them:
- **§2.7 Walkthrough** (`B3-walkthrough-desktop`) — "BUILT-forward-drive; net-new: sequencer/pacing,
  element-level show, reverse journey." This IS the guided-review-surface's FE show-me lane (Bucket C-h).
  Observed(APPLICATION-STRUCTURE-PACK.md:575).
- **§2.1 Mockup Studio** (`STUDIO.html`) — "BUILT-standalone; end-state = in-app rebuild." The guided-
  review-surface is that in-app rebuild. The studio is described as "superseded" by the in-app surface.
  Observed(APPLICATION-STRUCTURE-PACK.md:569).
- **§2.11 Build review** (`C3-build-review-desktop`) — "DESIGNED (front-door BUILT; trigger unarmed)."
  The generate+approve batch (Bucket C-b) is the trigger arm for this surface.
  Observed(APPLICATION-STRUCTURE-PACK.md:579).

**What it means for the build:** the build lands simultaneously into three designed surfaces that share
a room (the studio + the walkthrough engine + the build review). The synthesis's "treat as TWO loops
sharing one room" matches the 17-surface map exactly. Building the guided-review-surface IS building
these three surfaces into one integrated experience.

**Touch also (from the 17-surface map):**
- **§2.10 Inbox** (`C1-inbox-desktop`) — the SURFACE station. Build review items land here first.
  Observed(APPLICATION-STRUCTURE-PACK.md:578).
- **§2.2 IA / Commander's bridge** (`IA-desktop.html`) — the parent surface that contains the studio
  as a child page. The studio is a child of the IA; the IA-mobile mockup (73KB) is the one that
  survives at 19% under the 14KB cap (synthesis §0 D2).
  Observed(APPLICATION-STRUCTURE-PACK.md:570).
- **§2.8 Presence dial** — mode = `walkthrough` IS the guided-review-surface's activation. The dial
  design (Criteria G1–G4 in the Walkthrough Organ) must connect mode-select to tour-start.
  Observed(APPLICATION-STRUCTURE-PACK.md:576 + synthesis BUCKET C-h note on deferred FE).

---

### 2.2 The Operable Interface build (vault: Operable Interface — Completion Criteria)

**Relation: TOUCH (FORM law + the FE show-me lane).**
The Operable Interface criteria (active overnight build, per memory context) share hot files and
principles with the guided-review-surface:
- Group C (Show-me / guided-operation) C1–C4 in the Operable Interface IS the FE show-me lane
  (synthesis Bucket C-h). C1 says "a show-me/guided mode binds the existing spine (the `show` verb
  camera + spotlight + the walkthrough organ + TTS) into system-INITIATED step-sequences."
  Observed(Operable Interface Criteria Group C C1-C4).
- Group B (RHM consent surfaces) B1–B3 = the offer-with-options card = the batch-compose surface
  (synthesis Bucket C-b's "generate" UX).
  Observed(Operable Interface Criteria Group B B1-B3).
- The FORM laws (recognition-by-sight, one design language, responsive everywhere) from the Operable
  Interface bind every surface in the same codebase — including the guided-review-surface.
  Observed(Operable Interface Criteria §Laws 1-4).

**What it means for the build:** the Operable Interface build and the guided-review-surface build share
the FE show-me lane. Either they merge (one build, one branch) or they must be explicitly coordinated
on `main` (per the no-branches-in-company rule). The synthesis says the studio is the first consumer
of a general organ — which aligns with the Operable Interface's design mandate.

**Unification-opportunity:** Group C of the Operable Interface criteria IS the guided-review-surface's
FE lane. The build could fulfill both documents with one set of FE changes. Named explicitly below in
§3.

---

### 2.3 The Unification + FORM Remediation Spec (vault)

**Relation: TOUCH (the existing unresolved T0/T1 findings that the guided-review-surface surfaces touch).**
The Remediation Spec documents four Tier-0 showstoppers in the current codebase:
- **T0-WIRE**: the decision wire has no production entry seam. The guided-review-surface's
  generate+approve batch (Bucket C-b) IS the production entry seam. Building Bucket C-b directly
  resolves T0-WIRE.
  Observed(Remediation Spec §3 T0-WIRE).
- **T0-KEYSTONE**: the walkthrough view-drive silently no-ops (raw.ui_target never set). The guided-
  review-surface's tour stop (Bucket C-c) is the fix path — the mockup-aware stop needs to resolve
  the locus carrier correctly.
  Observed(Remediation Spec §3 T0-KEYSTONE; synthesis BUCKET C-c "RAISES on an unregistered address").
- **T0-CARD**: a completed build's review surfaces as a bare UUID. The synthesis Bucket C-b's
  "generate" button + "show through" UX is the designed replacement for the broken build-result card.
  Observed(Remediation Spec §3 T0-CARD).
- **T1-EMIT**: silent-swallow in the exactly-once dispatch guarantee. The guided-review-surface's
  dispatch path (Bucket C-a/b) runs through this code path — the build must resolve T1-EMIT before
  generate-for-mockups is safe.
  Observed(Remediation Spec §3 T1-EMIT).

**What it means for the build:** building the guided-review-surface also resolves the corpus's three
most critical showstoppers (T0-WIRE, T0-KEYSTONE, T0-CARD). The build sequence in synthesis §5 must
include T1-EMIT as a prerequisite of steps 4–6 (no safe dispatch until T1-EMIT is fixed).

---

### 2.4 The design system / mockup corpus (vault design/ + register.json + addresses.json)

**Relation: TOUCH (the corpus is what gets walked + generated-for).**
The mockup corpus (`design/mockups/`) contains 23 mockups, 18 of which carry `data-ui-ref` attributes.
The guided-review-surface walks these files. The `register.json` + `addresses.json` are the registry
that decides whether a stop is registered (and thus whether `present_current` can narrate it or raises).

Key facts:
- Unregistered mockup addresses → `present_current` RAISES (synthesis Bucket C-c). The mockup-aware
  stop requires either: (a) lightweight per-mockup registration, or (b) engine tolerance for
  unregistered stops narrating from injected HTML.
  Observed(synthesis §2 BUCKET C item c + suite.py:6218-6220).
- The `design/blueprint/` + `_system/code-symbols.json` + `_system/addresses.json` are the corpus-side
  of the `ui://→code://` join that generate-for-mockups needs (synthesis S3).
  Observed(IAS Research Synthesis §R1 SEAM 5: the join is corpus-side only).
- The FORM gate (`_system/check.py` + `design-lint`) binds ALL new FE surfaces.
  Observed(IAS Criteria §AUTO-GATES #3 DESIGN-LINT).
- `Surfaced Findings — design corpus to build.md` (vault) documents F3: a backlog of unregistered
  addresses (`ui://twin`, `ui://activity/replay`, `ui://workshop/self-changes`, etc.). The guided-
  review-surface adds mockup addresses to this backlog as it registers each stop.

---

## 3 · UNIFY/IMPROVE — The big one: where this build is THE unifying human-interaction organ

This section is the core finding of the design-corpus sweep. The synthesis states: "the surface was
always designed-general — it is THE one human-interaction organ for the whole Company." The corpus
confirms this three independent ways. Enumerated below are every designed thing the guided-review-
surface could subsume, generalize, or be the first instance of.

### 3.1 THE PRIMARY UNIFICATION: This surface IS the RHM Walkthrough Organ (Unification-opportunity)

**Evidence (Observed, three vault docs + one repo doc):**
1. APPLICATION-STRUCTURE-PACK.md §4 surface 2.7 "Walkthrough" status: "BUILT-forward-drive; net-new:
   sequencer/pacing, element-level show, reverse journey (L9)." The guided-review-surface's Bucket C
   items (C-h: FE show-me lane, C-c: mockup-aware stop) ARE these net-new items.
2. RHM-Walkthrough-Organ-Research-Synthesis "The general human-interaction primitive": "Build-review is
   its first consumer; the project→product pipeline's stages are future consumers. So it is built
   GENERAL, not as build-review's UI."
3. RHM-Walkthrough-Organ-Completion-Criteria §"What this is": "This is its human-in-the-loop made
   operable." The criteria form is: [A queue][B sequencer][C present anywhere][D record][E channel back]
   [F voice][G governance] — the SAME shape as the synthesis's circuit.
4. APPLICATION-STRUCTURE-PACK.md §3 Sequences Primitive: explicitly maps the walkthrough organ as
   "the full circuit made operable for the human — the sequencer turns the inbox pile into a walk."

**Implication:** the guided-review-surface build is not "another surface adjacent to the Walkthrough
Organ" — it IS the walkthrough organ, now grounded in what the wave found about the actual code. The
vault Walkthrough Criteria should be treated as a PARENT doc, and the synthesis's Bucket A/B/C items
map directly onto Criteria A/B/C/D/E/F. The delta between the two:
- The synthesis adds mockup-specificity (Bucket C-a/c) not in the vault design.
- The vault adds governance modes (G1–G4) and idea-capture polarity (A2) not in the synthesis.
- BOTH must be satisfied for the organ to be done.

**What it means for the build:** loop-prep completion criteria should FOLD the Walkthrough Organ
Criteria (vault) and the synthesis (repo) into ONE criteria doc. Building to either alone is
undershooting. Fold direction: synthesis §2 Bucket A/B/C as the grounded-code items; vault Criteria
A–G as the designed-intent items. The merge reveals the complete build.

---

### 3.2 SECOND UNIFICATION: The Operable Interface Group C is THIS build's FE lane

**Evidence (Observed, Operable Interface — Completion Criteria Group C):**
- C1 "Guided-operation mode" — "a show-me/guided mode binds the existing spine (the `show` verb camera
  + spotlight + the walkthrough organ + TTS) into 'show me how' — system-INITIATED step-sequences."
  This is synthesis Bucket C-h (FE show-me lane: "guided overlay + next/back/dwell + dial-select →
  start_walkthrough trigger").
- C2 "Teach-to-request-change" — "the first thing show-me teaches is how to request a change and
  approve it from inside." This is the guided-review-surface's "generate → approve" demo path.
- C3 "`show` resolves element-level addresses" — this is synthesis BUCKET B "walkthrough ↔ chat
  composition" prerequisite (the tour can only spotlight registered elements; C3 adds element-level).
- C4 "Resolve the walkthrough naming trap" — selecting guided mode actually starts the organ. This is
  synthesis BUCKET C-h + G2 (the mode dial connecting to the tour engine).

**Implication:** the Operable Interface build and the guided-review-surface build both need the same
FE lane. Unless they are coordinated into one build, they will produce two diverging implementations of
the same component. The path-of-least-resistance (the Company law) is to build it once, here, and
cross-reference from the Operable Interface criteria as fulfilled.

**Unification-opportunity:** the guided-review-surface FE lane (synthesis step 3 + Bucket C-h) IS the
Operable Interface Group C. Build once, satisfy both.

---

### 3.3 THIRD UNIFICATION: The Mockup Studio (§2.1) is replaced by this build

**Evidence (Observed, APPLICATION-STRUCTURE-PACK.md:569 + synthesis §3):**
- §2.1 status: "BUILT-standalone (worktree, superseded); end-state = in-app rebuild."
- The synthesis §3 confirms: "The studio (§2.1) = a CHILD page of the IA app (the rebuild target)."
- The CONVERGENCE-WALKTHROUGH.md (repo build-prep/claude-design/) verified the studio 6/6 at both
  widths — it is the best evidence of what the guided-review-surface should feel like on the live app.

**Implication:** the guided-review-surface build subsumes the standalone studio. The studio verified
by CONVERGENCE-WALKTHROUGH is the reference prototype; the guided-review-surface is the production
version inside the IA app. Any FORM benchmark for the surface should use the CONVERGENCE-WALKTHROUGH
as the "feels like this" reference.

---

### 3.4 FOURTH UNIFICATION: The project→product pipeline's human-interaction stages

**Evidence (Observed, Project-to-Product Pipeline Blueprint §B/stages + APPLICATION-STRUCTURE-PACK §4
surface 2.11):**
The Project→Product Pipeline Blueprint (vault) describes a pipeline where every stage that produces a
result needing Tim review routes through the inbox → walkthrough → approve → act circuit. Specifically:
- `diagnose` + `scenarios` + `gap-discovery` outputs → Tim reviews through the walkthrough organ.
  Observed(Blueprint §B5–B8: each stage "surfaces for Tim review").
- The build-loop `needs-Tim` items (currently landing in `.build/state.json` + `WALKTHROUGH.md`) are
  the same circuit.
  Observed(RHM-Walkthrough-Research-Synthesis §4 "The build-loop ↔ Tim channel: today Claude Code is
  the entire human-in-the-loop channel").

**Implication:** the guided-review-surface, once built, is the FIRST instantiation of the human-in-
the-loop channel that today runs through Claude Code terminal output. Every future pipeline stage
(diagnose, scenarios, gap routing, verification) uses the same organ. The build pays off immediately
on the current build-review use case AND unlocks every downstream use.

**Unification-opportunity:** the synthesis's "build-review is its first consumer; the project→product
pipeline's stages are future consumers" is literally designed into the Walkthrough Organ Criteria A4
("Build-loop items flow IN — the operable-surface 'needs-Tim' items surface here as `review` items,
not a markdown file"). This criterion is one of the currently-open `☐` items in the Walkthrough Criteria.
Building the guided-review-surface closes A4 and opens the pipeline's future human-review stages.

---

### 3.5 FIFTH UNIFICATION: The FORM unification (IAS corpus-import + Operable Interface design law)

**Evidence (Observed, IAS Criteria C0, F0–F9 + Operable Interface Laws 1–4):**
Both the IAS build and the Operable Interface build require:
- Corpus design-system imported into the repo (IAS C0: `design-system.css` + `tokens.json` + `check.py`).
- FE restructured from the 1660-line monolith (IAS F0).
- Every surface built from corpus tokens (IAS F1 / Operable Interface Law 1).
- Recognition-by-sight rendering, not text-wall (Operable Interface Law 4 / H4).

The guided-review-surface's FE lane (synthesis Bucket C-h) lands in `Review.tsx` + `StudioKit.tsx`
(the studio room). These files are IN the `canvas/app/src/` tree — subject to the same FORM gate.

**Implication:** the guided-review-surface cannot be built without the IAS corpus-import (C0/F0) as a
prerequisite, or the FORM gate will fail. The synthesis's build sequence step 3 (FE show-me lane)
implicitly depends on IAS Phase 0. This is a hard dependency, not a preference.

---

## 4 · RELATE — Same shape, recurring

These are designs in the corpus that share the Sequences primitive shape but are not direct unification
targets — they are the proof that the primitive is real and recurring.

### 4.1 Concurrent Cognition as the same loop at model scale

**Relation: RELATE (the same `resolve → work → persist → trigger` at the AI layer).**
CC Research Synthesis §2 "Round 2 — broader picture" B3 explicitly maps: "the single most productive
reuse: the reactive scheduler fires roles the same way it fires nodes; role = node; cast = graph."
APPLICATION-STRUCTURE-PACK §3 Sequences Primitive names CC as one of the three recurring instances:
"The collective cognition — the context cascade runs the same `resolve → work → persist → trigger`."

**What it means:** the guided-review-surface's per-stop comprehension (looking = address → auto-resolve)
is the CC cascade running at the human-visible surface. The CC build (G0–G1 proven) is not "separate
from" the guided-review-surface — it is the engine that the surface's narration runs on. The wave's
"verified comprehension" result (§0) was the CC cascade producing a non-developer explanation of the
inbox mockup. Building the FE show-me lane means wiring the CC cascade's output to the tour stop.

---

### 4.2 The Decision→Wire as the ACT station at every scale

**Relation: RELATE (the same governed-dispatch at every actuation point).**
The Decision→Wire Research Synthesis documents the `surface_build_intent → dispatch_decision →
implement.py → claude -p → git → revert` path. APPLICATION-STRUCTURE-PACK §3 maps this as the
"RESPOND/ACT stations" of the Sequences Primitive. The wire is not specific to the guided-review-
surface — it fires on every approved change anywhere in the system.

**What it means:** the `generate-for-mockups` dispatch (Bucket C-a) is a new ENTRY POINT into the wire
(a new `resolve_scope` branch), not a new wire. The wire's governance (T1-EMIT fix + T1-RACE fix)
must be solid before any surface uses it.

---

### 4.3 The Coherence substrate (repo build-prep/coherence/)

**Relation: RELATE (the addressable detection layer that the surface renders to Tim's level).**
The coherence/ directory (ANCHOR, COHERENCE-SUBSTRATE, CORPUS-CHAIN, SEMANTIC-LAYER) designs the
system's self-coherence detection — drift-check, symbol validation, refcheck. These feed the
guided-review-surface's "design corpus to build" path: when a mockup's `data-ui-ref` drifts from the
registered address, the coherence detector catches it; the surface's tour stop for that mockup will
then surface the drift to Tim.

APPLICATION-STRUCTURE-PACK CONVERGENCE-WALKTHROUGH confirms the coherence tools already run in the
studio's check loop. The guided-review-surface is the interface through which drift becomes visible and
actionable.

**Relate note:** the coherence sweep (AREA-3 in the guided-review-surface findings) likely has more
detail on the specific touchpoints. This area (design-corpus) flags the architectural relationship:
coherence detection → surface renders → Tim acts → generate dispatches. One circuit.

---

### 4.4 The twin / model-of-Tim (vault §2.9 in 17-surface map + RHM-Walkthrough Criteria D4)

**Relation: RELATE (the learning signal the surface generates).**
The Walkthrough Organ Criteria D4 says "a 'needs-change' WHY becomes directly a new criterion/edit,
not only twin-training." The 17-surface map §2.9 (twin) notes it is "BUILT-cold-start (corpus-pending)."
Every comment the Commander makes during a guided walk (via `annotate` / `ingest_comment`) is located
gold for the twin — `L4` in the IAS criteria.

**What it means:** the guided-review-surface is not only the human-interaction organ — it is the
PRIMARY DATA COLLECTION surface for the twin. Every session builds the model-of-Tim. The
`ingest_comment` path (already built, suite.py:3995) routes through the guided-review-surface's
annotate verb (synthesis Bucket C-f).

---

### 4.5 The idea-capture organ (vault Walkthrough Criteria A2)

**Relation: RELATE (the generative twin of the review queue).**
The Walkthrough Criteria A2 says the inbox has `origin: responsive` (system-awaiting-Tim) vs
`origin: generative` (Tim's ideas). The generative direction feeds in FROM the guided-review-surface
— when Tim says "let's add this" during a walkthrough, that becomes an `origin: generative` item.
The `ideas/Idea-capture as an interface organ.md` (vault) designs the receiving end.

**What it means:** the guided-review-surface is not a one-way read surface. It generates new work.
The RESPOND station's "WHY → new criterion" path (Walkthrough Criteria D4 + E3) flows from the
walkthrough into the generative inbox lane.

---

## 5 · The doc-grammar extension finding (from BUILD-ADDRESS-MAP.md)

**Relation: TOUCH/RELATE (the address system reaching its own build).**
BUILD-ADDRESS-MAP.md §Dogfood note: "the live address grammar (`contracts/address.py` SCHEMES =
run·cas·blob·vec·ui·code) has no scheme for DOCS or DIRECTORY-AREAS. Giving the build's own artefacts
+ the directory addresses is a proposed grammar extension (`doc://`, `area://`) — captured here as the
working coordinate system AND flagged as a candidate unification."

The design corpus sweep confirms: the 17-surface map, the loop-prep triads, the context files —
none of these have addressable `doc://` handles in the live system. This means the guided-review-
surface cannot walk its OWN build documents as stops on a tour (it can walk live `ui://` elements and
mockup HTML; it cannot walk a vault note as a first-class locus).

**Unification-opportunity (INFERRED):** extending the grammar to `doc://` (Obsidian-format markdown
files) and `area://` (directory regions) would make the guided-review-surface able to walk the VAULT —
the Company's own knowledge base — as a tour sequence. The RHM could then walk Tim through the design
documents AS IT WALKS HIM through the built surfaces. The two loops (design-review + live-app-review)
would become one.

This is a forward design point, not a prerequisite. The synthesis's current scope is `ui://` and
`mockup://` — the `doc://` extension is additive. But it is the right direction if the surface is
"THE one human-interaction organ."

---

## 6 · Summary table — all findings by relation kind

| Document / Design Area | Relation Kind | Key Fact | What it means for the build |
|---|---|---|---|
| RHM Walkthrough Organ — triad (vault) | USE + UNIFY | IS the same organ; criteria A–G are the parent design | Fold Walkthrough Criteria into this build's completion criteria |
| Interactive Addressed Surface — triad (vault) | USE + UNIFY | Substrate floor; S0–S5, F0–F9, I–R, L are prerequisites | IAS Phase 0 must precede or run alongside GRS FE lane |
| Operable Composition Surface — triad (vault) | USE | ACT half (dispatch, wire, git) | Mockup-scope dispatch = new `resolve_scope` branch; no new wire |
| Concurrent Cognition — triad (repo) | USE | Perception layer; CC cascade IS the per-stop comprehension | Wire CC `chat_parts` streaming to each tour stop; don't duplicate |
| Voice stack (voice-research/ + vault Voice-RHM) | USE | Most-ready input channel; one seam missing (focus passthrough) | Step 2 of synthesis sequence: one arg addition |
| Decision→Wire triad (vault) | USE | ACT station entry; T0-WIRE resolves when generate+approve lands | Bucket C-b IS T0-WIRE resolution |
| APPLICATION-STRUCTURE-PACK §3–4 (repo) | TOUCH | Sequences Primitive + ~17-surface map; surface is §2.7+2.1+2.11 | Build must satisfy these three surface specs simultaneously |
| Operable Interface Criteria Group C (vault) | TOUCH + UNIFY | Group C IS the FE show-me lane (synthesis Bucket C-h) | Build once; satisfy both docs |
| Unification+FORM Remediation Spec (vault) | TOUCH | T0-WIRE/T0-KEYSTONE/T0-CARD resolved by this build; T1-EMIT prerequisite | Fold T1-EMIT fix as step 0 of the build sequence |
| Design corpus / mockup corpus (vault design/) | TOUCH | 23 mockups; 18 have `data-ui-ref`; most stops unregistered | Mockup-aware stop + registration is Bucket C-a/c |
| Concurrent Cognition (same primitive at AI scale) | RELATE | Same `resolve→work→persist→trigger` at model layer | CC output = tour narration substrate; no duplication |
| Project→Product Pipeline (vault) | RELATE + UNIFY | Every stage's human-review uses this organ | Building GRS opens all future pipeline review stages |
| Coherence substrate (repo build-prep/coherence/) | RELATE | Drift detection feeds the surface's mockup-walk check loop | Surface renders drift catches to Tim during tour |
| Twin / model-of-Tim (vault §2.9) | RELATE | Located gold from every annotate = twin training | `ingest_comment` on every annotate IS twin data collection |
| Idea-capture / generative inbox (vault) | RELATE | Generative WHY→criterion path feeds from the surface | RESPOND station D4/E3 flows to generative inbox lane |
| `doc://` / `area://` grammar extension (BUILD-ADDRESS-MAP) | TOUCH | Address system cannot walk vault docs as first-class loci | Forward direction: extend grammar; not a prerequisite |

---

## 7 · The biggest unification opportunity (stated plainly)

**The guided-review-surface is not a review UI. It is the one human-interaction organ of the Company,
and every designed surface, organ, and pipeline stage in this corpus is a future consumer of it or a
proof that the Sequences Primitive is real.**

The single biggest unification the design-corpus sweep reveals:

> **The RHM Walkthrough Organ criteria (vault) and the guided-review-surface synthesis (repo) are
> the same design expressed twice from different vantage points. They should be MERGED into one
> completion criteria document before loop-prep runs. Building to either alone is incomplete. Building
> to both is the full organ.**

The merge would:
1. Add vault criteria A–G (queue · sequencer · present-anywhere · record · channel-back · voice ·
   governance) as the outer circuit to the synthesis's grounded build map.
2. Add synthesis Bucket C-a/c (generate-for-mockups · mockup-aware stop) as the mockup-specific
   extension not in the vault design.
3. Flag Operable Interface Group C as fulfilled by the same FE build.
4. Note T0-WIRE / T0-KEYSTONE / T0-CARD as resolved by this build (resolving Remediation Spec items).
5. Add the Project→Product Pipeline's future-consumer note as an `origin: generative` track that
   opens once A4 (build-loop items flow IN) is satisfied.

That merged document would be loop-prep's completion criteria — the one artefact that makes this a
"the build is THE unifying human-interaction organ" build rather than "a review surface."

---

*Sweep completed 2026-06-08. Evidence marks: Observed (doc read directly) / Inferred (pattern-derived,
not execution-verified) / Unification-opportunity (explicitly calls out where this build subsumes a
designed thing). Findings APPEND to the guided-review-surface criteria per Tim's grow-scope law.*
