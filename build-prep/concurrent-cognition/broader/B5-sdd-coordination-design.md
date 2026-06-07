# B5 — Sub-Agent-Driven Build Coordination (a meta-design, on paper)

*Tim's premise, 2026-06-07: build Concurrent Cognition via **sub-agent-driven development** in the `company-cognition` worktree, combining loop-prep's written triad with sub-agent parallelism. His insight: "if the plan and the sequence and the design is big and it is written, then it's a common reference for parallel sequences of all end-to-end implementations." And the recursion: the build should USE THE SAME node/graph mechanism it is building — the graph IS the plan, sub-agents query it.*

*This file is READ-ONLY research output. It designs HOW the build is coordinated — the methodology. It does NOT design the cognition layer itself (that is the triad's job; see `00-LANDSCAPE.md` + `03-concurrency-and-injection.md` for WHAT gets built). Every file:line claim traces to `~/company` / this worktree as of 2026-06-07 and is carried forward from the six research threads (01–06) + the landscape.*

---

## 0. The shape of the answer (read this first)

There are three load-bearing decisions this doc makes, and they are not the obvious ones:

1. **Slices are cut by FILE-DISJOINTNESS, not by feature-verticals.** The premise's "end-to-end vertical slices each agent takes start→finish" is the *aspiration*; the *constraint* is that nearly every net-new piece in the landscape converges on **one file** — `runtime/suite.py` (role registry, `_run_swarm`, the `chat()` part-loop, `brevity_judge`, the injection gather) — plus `runtime/bridge.py`. Two agents cannot both own `suite.py` in the same loop without colliding (no branches — rule 10 — so no merge to reconcile them). So the honest structure is a **sequential spine** (the suite.py-centric foundation) flanked by a **small number of genuinely disjoint parallel lanes**. The 32-way parallel *cognition* does NOT imply a 32-way parallel *build*; conflating the two is the trap.

2. **The coordination methodology already exists and is proven on THIS codebase — specialize it, don't reinvent it.** Six sibling skills (`company-build`, `wire-build`, `voice-build`, `rhm-build`, `remediation-build`, `interactive-surface-build`) all encode the same loop shape for this exact repo: read criteria → build the next buildable file-disjoint lanes → verify by USE + adversarial → commit per criterion → flag needs-tim, cron-driven. *That* is the answer to "how do sub-agents reference the common plan and report back." This doc produces a **`cognition-build` specialization** of that pattern.

3. **The recursion (build-as-a-graph in the company engine) is an AFTER, not a bootstrap** — because the very first thing being built (parallel dispatch) is the thing the engine currently lacks (`scheduler.py` is strictly serial, `03 §A.3`). A light *visibility* version is available now (the build plan AS a company graph for state, executed by the file-based loop); full *execution* of the build through the engine is the natural second self-build proof, after the mechanism exists.

The rest of the doc expands each of these, maps the slices, and gives the phase/sequence map.

---

## 1. How loop-prep's triad becomes the "big written common reference"

Tim's insight names the core property: **a written plan large enough is a shared coordinate system** — every parallel implementation sequence reads the same document and therefore lands in the same world without talking to each other. This is loop-prep's three-document methodology used as a *coordination substrate*, not just a planning artifact.

### 1.1 The three documents and what each one carries here

The triad lives at `build-prep/concurrent-cognition/` alongside the research threads. Each document plays a coordination role:

| Document | What it IS (loop-prep) | Its coordination role in a sub-agent build |
|---|---|---|
| **Completion Criteria** | the truth-table — verifiable statements about system state, two-faced (FUNCTION + FORM), priority-ordered by dependency | **the shared task surface.** Each criterion is a unit a sub-agent can claim, build, and have verified. The priority order IS the dispatch order. The FORM face is what stops the rendering lane shipping a prototype. |
| **Implementation Guide** | the HOW — principles, sequence-of-operations, do's/don'ts, file-paths-with-roles, pseudocode | **the per-agent briefing.** A sub-agent dispatched to a criterion reads only its guide section + the named files. This is where the file:line evidence from `03` becomes "MODIFY `suite.py` `chat()` at the single-call seam `:3424`, REUSE `resolve_role` `:3172`, KEEP the single-call path." |
| **Research Synthesis** | the WHAT-EXISTS — the evidence base, by exploration round | **the reuse spine + the preserve-list source.** `00-LANDSCAPE.md §2` (reuse table) and `03 §G` (reused-vs-net-new) ALREADY are most of this. It is the document that prevents an agent building a parallel system (loop-prep principle 2 / AGENTS.md rule 2). |

The change-flow direction is fixed (loop-prep): **research → synthesis → guide → criteria**, never reversed. If an agent discovers the codebase contradicts the spec, the spec changes to match reality — not reality to match the spec.

### 1.2 Why "big and written" works as coordination (the mechanism, not the slogan)

The reason a large written plan substitutes for inter-agent messaging:

- **Sub-agents fired in parallel cannot message each other** (Task subagents are fire-and-forget; even teammates are hub-and-spoke, and messages are ephemeral — `orchestrating-swarms` runtime caveats). The only durable shared state is **files**.
- So the plan must carry **everything two agents would otherwise have to negotiate**: the seam each one touches, the address namespace each one writes, the contract between them, what each must preserve. If the plan says "Role Registry rows live in `ROLE_REGISTRY` (`suite.py:929`); the swarm executor reads them via `resolve_role`; the injection gather reads from the `swarm://<turn>/<role>` namespace," then three agents building those three pieces converge on a working seam **without ever talking**.
- This is the same property the repo itself is built on (AGENTS.md: "after those four files you should be able to act correctly without re-deriving anything"). The triad extends the self-description down to *this build*.

**The expansion-ratio matters (Tim's standing preference):** the triad should be written EXPANSIVELY — more content than the conversation produced — because the parallel sub-agent build absorbs volume as a feature, and because an under-specified seam is exactly where two parallel agents drift apart. Brevity here is the failure mode.

---

## 2. Slicing the build — end-to-end where possible, serial where the hot files force it

### 2.1 The collision map (why naive vertical slicing fails)

Cross-referencing the net-new pieces (`00-LANDSCAPE.md §3`, `03 §G`) against the files they touch:

| # | Net-new piece | Primary file(s) | Collides on |
|---|---|---|---|
| 1 | Parallel dispatch (ThreadPoolExecutor) | `runtime/suite.py` (new `_run_swarm`) or `fabric/swarm.py` | suite.py (helper lives on Suite) |
| 2 | Request-concurrency budget (Semaphore(32), R reserved) | `runtime/suite.py` (Suite singleton holds the semaphore) | **suite.py** |
| 3 | `json_schema` in transport | `fabric/transport.py` | **disjoint** ✓ |
| 4 | General Role Registry | `runtime/suite.py` (`ROLE_REGISTRY` `:929`) | **suite.py** |
| 5 | `_run_swarm(roles, budget)` helper | `runtime/suite.py` / `fabric/swarm.py` | suite.py |
| 6 | Staged-response queue (THOUGHT_SHAPES + part-loop + `chat_parts`) | `runtime/suite.py` (`chat()` `:3424`), `runtime/bridge.py` | **suite.py + bridge.py** |
| 7 | `brevity_judge` | `runtime/suite.py` (mirrors `is_finished_thought` `:3253`) | **suite.py** |
| 8 | Injection edge (`swarm://` namespace + gather branch) | `runtime/suite.py` (`_resolve_context_at` `:1943`, `_chat_context` `:1461`) | **suite.py** |
| 9 | `llm` node marked VOLATILE | `nodes/llm.py` | **disjoint** ✓ |
| 10 | Rendering (cognition serializer + `cognition.*` SSE + FE views) | `runtime/suite.py` (serializer) + `runtime/bridge.py` (SSE branch) + `canvas/app/src/*` (FE) | suite.py + bridge.py + **FE disjoint** ✓ |

**Verdict:** pieces 1, 2, 4, 5, 6, 7, 8 and the serializer-half of 10 all land in `suite.py`. They are **one sequential spine**, not seven parallel lanes. Pieces 3, 9, and the **FE-half of 10** (the `canvas/app/src` views — `CognitionView`/`RoleShape`/cognition-`Edges`) are genuinely file-disjoint and can run in parallel with the spine.

This matches what the prior loops learned by doing: `voice-build` flagged "the hot files overlap → mostly sequential." The same physics applies here. The architecture's poetry (32 parallel thoughts) must not inflate the claimed build parallelism.

### 2.2 The actual slice map

```
                    ┌─────────────────────────────────────────────────────┐
                    │ PARALLEL DISJOINT LANES (run alongside the spine)    │
                    │                                                       │
   LANE T  ─────────┤  transport: json_schema response_format (#3)         │
   (fabric/transport.py)  one branch; retry already exists; sheet §5 proves│
                    │  the 4B does strict schemas. No suite.py touch.       │
                    │                                                       │
   LANE V  ─────────┤  nodes/llm.py VOLATILE=True (#9)                      │
   (nodes/llm.py)   │  else identical role draws memo-collapse to one       │
                    │  result (scheduler.py:96). Tiny, isolated.            │
                    │                                                       │
   LANE R  ─────────┤  RENDERING FRONT-END (FE half of #10)                │
   (canvas/app/src) │  CognitionView · RoleShape · cognition-Edges ·        │
                    │  cognition node-state vocabulary in the FE.           │
                    │  Disjoint from core; gated on the cognition.* SSE     │
                    │  CONTRACT (a doc'd event shape), NOT on the backend    │
                    │  impl — so FE can build against the contract early.   │
                    └─────────────────────────────────────────────────────┘

   ════════════════ THE SEQUENTIAL SPINE (suite.py + bridge.py) ════════════════
   one owner at a time; commit per criterion; no two spine agents concurrent

   S0  PROVING SPIKE  ─ generalise judge → 2-role registry → ONE injected
       (gate)           2nd part. Proves dispatch + json_schema + injection
                        + a 2-part staged reply END-TO-END before fan-out.
                        (landscape §6 — recommended-first.)
                          │ depends on LANE T (json_schema) being in
                          ▼
   S1  Slot scheduler  ─ Semaphore(32) on the Suite singleton + the
       (MAKE-OR-BREAK)   reservation (swarm pool max_workers = 32−R).
                         #1+#2+#5. "the make-or-break each agent named"
                         (landscape §4). Everything fans out from here.
                          │
                          ▼
   S2  Role Registry   ─ generalise ROLE_REGISTRY to declarative role rows
                         (#4) + generic run_role. Judge is the seed.
                          │
                          ▼
   S3  Injection edge  ─ swarm:// namespace + gather branch in _r2_gather;
                         resolve at _chat_context :1461 via _resolve_context_at
                         (#8). Option (a) from 03 §E.4.
                          │
                          ▼
   S4  Staged queue    ─ THOUGHT_SHAPES registry + part schema + intra-turn
                         runner + chat_parts(); shape_for(mode) (focus/
                         background → never stage) (#6). The chat() part-loop.
                          │
                          ▼
   S5  brevity_judge   ─ short-response bypass mirroring the judge (#7).
                          │
                          ▼
   S6  cognition.* emit─ the serializer half of #10 + the cognition.* SSE
       contract+backend  branch in bridge.py (mirrors decision.*). This is
                         the BACKEND that LANE R's contract was built against;
                         here they MEET.
```

**What is parallel vs sequential, stated plainly:**
- **Parallel from the start:** Lane T, Lane V, Lane R (FE). Three agents, three disjoint file-sets, fired together.
- **Sequential, one-owner-at-a-time:** S0→S1→S2→S3→S4→S5→S6, all on `suite.py`(+`bridge.py`). These cannot be parallelized against each other because they edit the same file and there is no branch to merge.
- **The one synchronization point:** Lane R (FE, built against the `cognition.*` contract) MEETS S6 (the backend that emits that contract). The contract is written FIRST (in the triad), so both sides build against it independently and converge.
- **Lane R has a SPLIT completion (the rule-9 timing trap):** Lane R can be *built + design-lint'd statically* (on-token, design-system components — `canvas/app/src` is disjoint, no backend needed) in Phase 3. But its **by-USE FORM green is gated on S6/integration** — the design-critic drives a browser and screenshots a *rendered cognition frame*, and there is nothing real to render until S6 emits `cognition.*` events (or until cognition-event fixtures stand in). So Lane R does NOT fully green in Phase 3; its build+lint half lands in Phase 3, its by-use FORM half lands at integration (Phase 4). Premature-greening a rendering surface with no real data is exactly the FORM-is-half-of-done failure rule 9 exists to prevent.

This is the genuine, honest parallelism: **3 disjoint lanes + 1 serial spine**, not 8 parallel verticals.

### 2.3 Where strict ordering is FORCED (and why)

- **S0 (proving spike) before everything else on the spine.** Landscape §6's recommendation. Proving dispatch+schema+injection+part-loop on a 2-role toy *before* fanning out means the make-or-break is de-risked while the blast radius is tiny. A spike that fails redirects the whole design cheaply.
- **S1 (slot scheduler) before S2–S6.** Every later piece *fans out from* the scheduler (landscape §4 names it the make-or-break). You cannot meaningfully build the role registry's value (parallel roles) or the staged queue (swarm-between-parts) without the dispatch+budget mechanism existing.
- **LANE T (json_schema) before S0.** S0's injection proof needs a role to write *validated* structured JSON; that needs the transport's `json_schema` branch (#3). T is tiny and disjoint, so it lands first/fast.
- **S6 (backend emit) gated by S4/S3 producing cognition state to emit** — you can't serialize a swarm's run-state before the swarm runs.

Everything else is dependency-chained but not artificially ordered.

---

## 3. How sub-agents reference the common plan + report back (no self-passing)

This specializes `orchestrating-swarms` + `subagent-orchestration` to the constraints of THIS repo. It is the proven sibling-loop pattern (`company-build` et al.) re-pointed at the cognition triad.

### 3.1 The reference path (how an agent knows what to do)

A dispatched sub-agent reads, in order:
1. **`AGENTS.md` → `MAP.md` → `STATE.md` → the module's `AGENTS.md`** — the repo's standing orientation (the laws, the structure, the current state).
2. **The Completion Criteria** — finds its assigned criterion (or the next buildable one for a swarm-pull worker).
3. **The Implementation Guide section** that criterion references — the HOW + the named files + the preserve-list.
4. **The Research Synthesis** entry — the reuse anchors, so it extends rather than parallels.

The agent's *prompt* carries only: its criterion ID, absolute paths to the triad, its role (implementer / verifier / design-critic), and the one-owner-of-this-file guarantee. Everything else is in the files (`subagent-orchestration`: don't cram context into prompts; shared context lives in files).

### 3.2 Completion conditions (no self-passing — `orchestrating-swarms` principle 2)

- A criterion is **two-faced** (loop-prep / AGENTS.md rule 9): FUNCTION (the behaviour, verified by USE — run it, don't read it) AND FORM (the product face, verified by a design rubric). A line is green only when BOTH are verified.
- **The implementer does NOT grade its own work.** A **separate verifier agent** confirms each criterion against its stated conditions, by execution: for the cognition spine, that means running the relevant acceptance suites + a by-use turn through `chat()`; for the rendering lane, a **design-critic** (browser-driving, screenshots) judging against the rubric, plus a **design-lint** that fails loud on off-token / bespoke-element (AGENTS.md rule 9's three places: criteria, critic, lint).
- **Verification is by USE.** The repo's own bar (STATE.md): "tests ARE the convergence record" + "prove by USE — operate the live system." A new capability ships a new acceptance suite (e.g. `cognition_dispatch_acceptance`, `staged_parts_acceptance`, `injection_edge_acceptance`) that proves it by execution. "No error" is not done.

### 3.3 Gap-surfacing, issue capture, preserve-lists (`orchestrating-swarms` principles 3–5)

- **Surface gaps, don't invent (AGENTS.md rule 8).** When an agent hits ambiguity or a missing design decision (e.g. "which roles in the first cast?", "part grain?"), it STOPS and records a design-delta / surfaces a `NEEDS:` — it does NOT fill the gap silently. The open forks in `00-LANDSCAPE.md §5` and `03 §F` are the *known* gaps; an agent hitting one routes to Tim, never guesses.
- **Issue capture is structured.** Issues reference the triad section they contradict. With `mcp__substrate-mcp__report_issue` / `list_issues` available in this environment, issues can be logged there (durable, queryable) rather than as informal notes. A file-based `issues.md` in the build-prep folder is the no-MCP fallback.
- **Preserve-lists are mandatory (the highest-blast-radius edit here is `chat()`).** S4 restructures `chat()` from a single `complete_with_tools` call (`suite.py:3424`) into a part-loop — this is the change most able to break the live RHM. The preserve-list for S4 MUST pin, and the verifier MUST confirm still-passing:
  - the existing single-call reply path (a turn that doesn't stage still works);
  - `focus` / `background` modes **never stage** (`shape_for(mode)` returns single-shot) — these modes must behave exactly as today;
  - the judge (`is_finished_thought`) unchanged;
  - the decision→implementation wire untouched;
  - native tool-calling still emits operator-facing `tool_calls` (the open fork: tools on the final part only vs all parts — flagged, not guessed).
  - **Regression gate:** the existing `rhm_acceptance.py`, `rhm_action_acceptance.py`, `rhm_action_parse_acceptance.py`, `rhm_grounding_acceptance.py`, `modes_acceptance.py`, `react_acceptance.py` suites must all still pass after S4. They ARE the preserve-list made executable.

### 3.4 No branches, no per-agent worktrees (AGENTS.md rule 10)

This is a hard departure from `orchestrating-swarms`' default (teammates auto-get individual git worktrees). In THIS repo:
- The build runs IN the existing `company-cognition` worktree (already a `git worktree`, not a branch — `.git` is a file pointer). Work commits to **one branch**, per criterion, file-disjoint.
- Sub-agents do NOT spawn their own worktrees/branches (that would strand work nobody knows to merge — the exact headache rule 10 exists to prevent; and orchestrating-swarms warns of worktree-nesting after compaction).
- **File-disjointness is what makes same-branch concurrent commits safe.** Lane T (`transport.py`), Lane V (`nodes/llm.py`), Lane R (`canvas/app/src`) touch non-overlapping files, so concurrent commits to the one branch don't conflict (git serializes). The spine (S0–S6) is one-owner-at-a-time precisely because it is NOT file-disjoint.
- Commit verified-BEFORE-commit (rule 10: never commit broken); update the self-description (MAP/STATE + module AGENTS.md) as part of each change (rule 9 clause).

### 3.5 The loop driver (specialize the proven pattern)

Produce a **`cognition-build` skill** as a sibling of `voice-build`/`wire-build`/`rhm-build`. Its body:
> Read the Completion Criteria + `00-LANDSCAPE.md` + `03`. Find the next buildable criterion (respect the spine ordering S0→S6; fire the disjoint lanes T/V/R alongside). Dispatch an implementer to the criterion with its guide section + preserve-list. On claimed completion, dispatch a separate verifier (by-use + adversarial; design-critic + design-lint for FORM). Mark green only on the verifier's pass. Commit per criterion to the branch under rule 10. Flag needs-tim for the open forks. Cron-driven, crash-safe (state in the criteria file + substrate issues, never in messages).

This is exactly the shape of the six existing build skills — re-pointed, not reinvented (loop-prep principle 2: don't build a parallel system when one exists).

---

## 4. The recursion — could the build be coordinated AS a graph in the node mechanism?

Tim's recursion: the build should USE the same node/graph mechanism it is building; the graph IS the plan; sub-agents query it. There are TWO graph systems to keep distinct, and the bootstrapping order matters.

### 4.1 Two distinct graph systems (don't conflate them)

| System | What it is | Availability here |
|---|---|---|
| **`graph-driven-coordination` (the skill)** | Project Vi **Memory** graphs as a workflow state machine (CURRENT_STATE / DESIRED_STATE / CONSTRAINT, entry points, flags). Sub-agents query the memory graph. | **The `mcp__project-vi-memory__*` tools are NOT present in this environment.** Only `mcp__company__*` (the company's own engine) and `mcp__substrate-mcp__*` are available. So the skill *as written* cannot run here. Its **principle** (the graph is the plan; query state, don't pass tasks) can still be realized on another substrate. |
| **The company engine itself** (`mcp__company__*`: `create_node`, `run_graph`, `propose_node`, `get_state`, `get_events`) | The thing being built — nodes fire when input addresses resolve. | Available. But its scheduler is **strictly serial today** (`scheduler.py:59-61`; `03 §A.3`) — parallel dispatch is the FIRST thing this very build adds. |

### 4.2 The bootstrapping verdict — execution is an AFTER, visibility is available NOW

**Executing the build *through* the company engine (parallel agent dispatch expressed as graph-runs) is blocked by the bootstrap:** the engine cannot dispatch in parallel until *this build* gives it parallel dispatch (S1). You cannot use the mechanism to build the mechanism that doesn't exist yet. So full execution-recursion is the **natural SECOND self-build proof** — run it *after* S1+ exist, as the demonstration that the cognition build can coordinate the next build. That is a powerful milestone and worth naming as the graduation story; it is not the bootstrap.

**A light recursion IS available now — represent the build plan AS a company graph for VISIBILITY/STATE, executed by the file-based loop:**
- A node per slice (S0–S6, Lane T/V/R); edges = dependencies; `get_state` shows progress; `get_events` is the live build telemetry. The company engine becomes the *map of its own construction* (the reflective fold the MAP.md already describes for the codebase).
- This is honest recursion (the system holds its own build plan) without requiring the unbuilt parallel scheduler. The actual dispatch stays the file-based `cognition-build` loop; the graph is the *visible state*, not the *executor*.
- **Issue capture** maps to `substrate-mcp` `report_issue`/`list_issues`; **completion state** maps to the criteria file (durable truth) mirrored into the graph node states.

**Recommendation:** Do NOT block the build on either recursion. Build the cognition layer with the file-based `cognition-build` loop (§3). OPTIONALLY mirror the plan into a company graph for visibility (cheap, honest, no bootstrap dependency). RESERVE the full execution-recursion (build-coordinated-through-the-engine) as the celebrated second self-build proof, run once S1's parallel dispatch is real. This respects the bootstrapping order and keeps the make-or-break (S1) on the critical path rather than behind a chicken-and-egg.

---

## 5. The phase/sequence map (research → triad → spike → parallel slices → integration → verification)

```
PHASE 0 — RESEARCH                                              [DONE / mostly done]
  ✓ Six read-only threads (01–06) + 00-LANDSCAPE.md aggregated.
  ✓ 03 carries the make-or-break detail (slot budget, injection seam, file:lines).
  Parallel: yes (six agents already ran). Sequential after: the triad.
  Gap to close before triad: confirm the open forks that BLOCK the spike
  (part-grain can wait; json_schema decision + injection option (a vs b) cannot).

PHASE 1 — TRIAD (loop-prep)                                     [the common reference]
  Write Completion Criteria · Implementation Guide · Research Synthesis,
  EXPANSIVELY, two-faced criteria, priority-ordered to the spine S0→S6 + lanes.
  Bake in: preserve-lists (esp. chat()), the cognition.* SSE CONTRACT (so FE
  Lane R can build against it), the open forks marked needs-tim.
  Parallel: drafting can fan out by document section; SYNTHESIS leads
  (it's mostly transcribed from §2/§G already). Sequential: criteria last
  (it depends on guide + synthesis). Then PLAN-REVIEW (the plan-review skill:
  send agents to find what the plan missed, build findings back — the prior
  loops all did this before building).

PHASE 2 — PROVING SPIKE (S0)                                    [sequential GATE]
  Generalise judge → 2-role registry → ONE injected 2nd part. End-to-end:
  dispatch + json_schema + injection + 2-part staged reply.
  Depends on: Lane T (json_schema) landed first.
  Parallel: NO — single tiny spike on suite.py. This gate de-risks the whole
  design before any fan-out. If it fails, redirect cheaply.

PHASE 3 — PARALLEL SLICES                                       [3 lanes ∥ + 1 serial spine]
  Disjoint lanes (fire together, distinct file-sets, same branch):
     LANE T  fabric/transport.py     json_schema (#3)        — feeds the spike, lands first
     LANE V  nodes/llm.py            VOLATILE (#9)           — tiny, isolated
     LANE R  canvas/app/src          cognition FE (#10 FE)   — built+lint'd vs the SSE contract
                                       in P3; by-USE FORM green deferred to P4 (needs real
                                       cognition.* data — fixtures or the live S6 backend)
  Sequential spine (one owner at a time, suite.py + bridge.py):
     S1 slot scheduler (MAKE-OR-BREAK) → S2 role registry → S3 injection edge
     → S4 staged queue (the chat() part-loop; preserve-list gated) → S5 brevity_judge
     → S6 cognition.* emit (backend; MEETS Lane R at the contract)
  Each criterion: implementer → separate verifier → commit. needs-tim on forks.

PHASE 4 — INTEGRATION                                          [the lanes MEET the spine]
  The one true synchronization point: S6 (backend emit) ⨝ Lane R (FE views)
  at the cognition.* contract. Run a live turn through chat() that stages parts,
  fires the swarm, injects, and renders the cognition frame live on the canvas.
  Voice: each completed PART is the TTS streaming unit (05) — confirm overlap.
  Parallel: no — this is the convergence; one integrated by-use run.

PHASE 5 — VERIFICATION (prove by USE, not by reading)         [the bar]
  ✓ New acceptance suites pass (cognition_dispatch · staged_parts · injection_edge · brevity).
  ✓ ALL preserve-list regression suites still green (rhm_* · modes · react · wire).
  ✓ Slot budget proven by USE: a swarm wave never starves the next main part
    (the make-or-break, measured — R/swarm-cap is a config slot tuned here).
  ✓ FORM: design-critic passes the cognition surface against the rubric;
    design-lint green (on-token, design-system components).
  ✓ Self-description updated (MAP/STATE/module AGENTS.md) + drift_acceptance green.
  Subjective taste calls (the cognition surface's feel; the live voice overlap)
  → flagged needs-tim, NEVER self-green-painted.

  Open forks surfaced for Tim throughout (never built unasked):
  R/swarm-cap · part-grain · first role cast · residency policy · cloud
  escape-hatch · tools-across-parts · swarm:// GC · address scheme (run:// vs cog://).
  (Full list: 00-LANDSCAPE.md §5 + 03 §F.)
```

### 5.1 Parallel-vs-sequential, summarized

| Phase | Parallel within it | Forced sequential |
|---|---|---|
| 0 Research | the six threads (done) | triad waits on research |
| 1 Triad | draft by document/section | criteria last; plan-review after |
| 2 Spike | none (single gate) | after Lane T; before all fan-out |
| 3 Slices | **3 disjoint lanes ∥** | the **spine S1→S6** is serial (shared suite.py) |
| 4 Integration | none (convergence) | after S6 + Lane R |
| 5 Verification | suites can run in parallel | after integration |

---

## 6. The methodology synthesis (the whole thing in one frame)

```
  THE BIG WRITTEN PLAN (loop-prep triad)            = the shared coordinate system
     Completion Criteria  (the task surface, two-faced, priority-ordered)
     Implementation Guide (per-agent briefing: seams, files, preserve-lists)
     Research Synthesis   (reuse spine; prevents parallel systems)
                    │
                    │ sub-agents READ it (no messaging; files are the only durable state)
                    ▼
  THE LOOP (a cognition-build skill = specialization of the 6 proven sibling loops)
     read criteria → next buildable → implementer (reads its guide section)
       → SEPARATE verifier (by-use + adversarial; design-critic + lint for FORM)
       → green only on verifier pass → commit per criterion to the ONE branch
       → surface forks needs-tim → repeat.   Cron-driven, crash-safe.
                    │
                    ▼
  THE SLICING                3 disjoint lanes ∥  +  1 serial spine (suite.py)
     because the net-new pieces collide on suite.py — file-disjointness, not
     feature-verticals, sets the parallelism. (The 32-way cognition ≠ 32-way build.)
                    │
                    ▼
  THE GATES         spike (S0) before fan-out  ·  scheduler (S1) before all roles
                    ·  preserve chat() (the live RHM)  ·  FORM is half of done
                    │
                    ▼
  THE RECURSION     NOW: optionally mirror the plan as a company graph (visibility)
                    AFTER: once S1 exists, coordinate the NEXT build THROUGH the
                    engine's new parallel dispatch — the second self-build proof.
                    (Not the bootstrap: the engine can't parallel-dispatch until
                    this build gives it that.)
```

### 6.1 The laws this methodology honours (carried from AGENTS.md, made specific)
- **Rule 2 (schema-additive):** every piece is additive; new role rows, a new helper, a new SSE branch — never a schema-break. The triad's synthesis is the reuse spine that keeps it additive.
- **Rule 3 (one source):** ONE injection law (`_resolve_context_at`, option (a) — `03 §E.4`), ONE role registry, ONE semaphore on the Suite singleton. The plan names them so parallel agents don't mint duplicates.
- **Rule 4 (fail loud):** the swarm fails loud per-role; no silent fallback to the cloud brain when the 4B isn't resident; the verifier fails loud, never green-paints.
- **Rule 8 (registry-is-truth):** roles + the `:8000` binding are registered, not invented; agents hitting a gap ASK (`NEEDS:`), the open forks route to Tim.
- **Rule 9 (FORM is half of done):** two-faced criteria + separate design-critic + design-lint for Lane R; backend-only spine pieces still update the surface that exposes them.
- **Rule 10 (no branches):** work IN the existing worktree, commit per criterion to one branch, file-disjoint lanes make concurrent commits safe, no per-agent worktrees, verified-before-commit.

### 6.2 What stays OPEN (this doc closes nothing it shouldn't)
This is the *coordination* design. It deliberately does NOT decide: the role cast, part grain, R/swarm-cap, residency policy, cloud escape-hatch, tools-across-parts, `swarm://` GC, or the address scheme — those are the triad's + Tim's calls (forks in `00-LANDSCAPE.md §5`, `03 §F`). It also does not re-decide the architecture (that's the landscape + threads). It proposes the SHAPE of the build and the order; the contents are filled by the triad and corrected by use.

---

## 7. Provenance
- Skills read in full: `loop-prep`, `graph-driven-coordination`, `graph-subagent-execution`, `subagent-orchestration`, `orchestrating-swarms` (`~/.claude/skills/*/SKILL.md`).
- Build context: `00-LANDSCAPE.md` (architecture, reuse §2, net-new §3, forks §5, path §6); `03-concurrency-and-injection.md` (the make-or-break: slot budget §C.3, injection seam §E, file:lines, reused-vs-net-new §G); `AGENTS.md` (rules 1–10, esp. 8/9/10), `MAP.md`, `STATE.md` (current built state; scheduler strictly serial; `chat()` single-call seam).
- Sibling proven loops cited: `~/.claude/skills/{company-build,wire-build,voice-build,rhm-build,remediation-build,interactive-surface-build}/SKILL.md`.
- Tool-availability check (2026-06-07): `mcp__company__*` + `mcp__substrate-mcp__*` present; `mcp__project-vi-memory__*` ABSENT — hence the §4 two-systems distinction and the file-based loop as the executor.
```
