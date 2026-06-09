# The Workflow Layer — Architecture (how one orchestration substrate accounts for all twelve compositions + the tool-expansion)

> **What this is.** The governing design for the self-improvement phase's *orchestration*. The twelve compositions (`COMPOSITIONS.md`) are the WORK; this is HOW the Workflow tool builds + runs them coherently, as one substrate, not twelve ad-hoc scripts. Written 2026-06-09 at Tim's direction ("the workflow must account for all the examples + the tool-expansion").
>
> **The problem it solves (Tim's, verbatim frame):** *"Unification is a big problem I have with AI — there's no humans involved."* No human holds the whole code picture, so AI fragments: builds a second parser, a parallel registry, a duplicate path, because it never saw the first. **So unification is the FIRST law here, not a cleanup pass.**

---

## LAW 0 — UNIFICATION (the governing discipline; the answer to "no humans involved")
Every workflow, every agent, every composition obeys this BEFORE it builds anything:
1. **Get the full relevant code picture first.** Before creating X, find what already does X-ish. The deterministic floor (grep/read) always; the semantic floor (the repo exocortex ①, once live) for "what relates to this that I'd never grep." A build agent that hasn't looked is not allowed to create.
2. **Take anything found into scope.** Stranded/incomplete/duplicate/adjacent work the picture surfaces is ADOPTED + completed/unified, never dismissed or routed-around (the standing `feedback-incomplete-work-in-scope` law, generalized from "a dead worker's diff" to "the whole codebase"). Found a second thing that should be one thing → unifying them is now in scope.
3. **Reuse-not-parallel is enforced, not requested.** "Mirror screen_reader / extend parse.py / no second registry-parser-runner" is in every brief's LAWS, and the CONFIRM/verify steps check for it (a new file that duplicates an existing capability is a finding, not a pass).
4. **The standing unification organs:** ① repo-exocortex (the full-code semantic picture) + ② drift-radar (built-twice / doc-vs-code contradiction) are not just "compositions to build later" — they ARE the machine that keeps the picture whole as the codebase grows. They run early and recur. **This is the deepest answer to the no-humans problem: the system holds the picture the humans can't.**

---

## THE TWO LAYERS (don't conflate — the tool-expansion lives between them)
- **BUILD orchestration = the Workflow tool** (`/workflows`): deterministic JS, spawns agents (parallel/pipeline), one run, background. It *writes* roles/modules/seams. (The V-A registry-generation workflow is this.)
- **RUN artifacts = the engine cascades** (`save_cascade`/`run_cascade` on the company MCP): the chains the build produces, fired on the engine.
- **THE GAP between them = the tool-expansion.** Building a composition often reveals a missing engine seam (below). Those seams are themselves build-work — so a workflow that "accounts for all the examples" must build the shared seams, not assume them.

## THE FACULTY SKELETON (why twelve compositions are ONE parameterized shape)
```
extract(deterministic) → ground → MAP(run_items) → REDUCE(run_reduce: role|rule|cluster)
                       → CONFIRM(jury + deterministic refcheck) → PROPOSE(operator floor) → [approve] → ACT
```
Every composition is this skeleton with different **role-fills** `{extract-source · ground-role · map-role · reduce-mode · confirm-spec · act-target}`:
- **V-A register-a-surface** = mockups · screen_reader · register_element · cluster-dedup · refcheck+jury · write-back-to-addresses.json
- **② drift-radar** = repo-corpus · — · — · cluster+compare · judge_drift · mark
- **③ transcript-miner** = jsonl · session-header · mine_exchange · cluster · judge_mining · draft-feedback
- **⑦ spec-compiler** = seed+corpus · few-shot · expand/ground_criterion · role-synth · jury-vs-seed · draft-triad
- **⑫ engine-improves-engine** = needs-tim+flags · — · scout_fix · lane-plan-synth · jury · propose-lane-cut
So **"the workflow accounts for all the examples" = the skeleton is parameterized once; each composition is a role-fill.** The V-A workflow is the hand-specialized first instance AND the template for the generalized faculty-workflow (the B build).

## THE GPU-AWARE RUN LAW (from Tim's resource correction — there is no steady state)
`ensure_resident` handles allocation **async, with swap latency** — the agent requests its model (`run_role(..., ensure=True)` / `company up <svc> --wait`); the system loads it, evicting if authorized. Consequence for orchestration:
> **Build-parallelism is FREE; run-parallelism SERIALIZES on the one 16 GB card.**
- Writing roles/modules is file-disjoint, no GPU → **fan it as wide as the work allows.**
- Steps that FIRE models (MAP on the 4B, EMBED on bge-m3, a stronger-model CONFIRM) **contend on one card** → `ensure_resident` serializes them by swapping. Fanning N model-runs in parallel ≠ N×; it's a swap storm.
- **So:** fan the code-build wide → then run the model-firing steps in a **GPU-aware sequence** (group by model so the card swaps once per group, not per call), or accept swap latency, or mark needs-tim. A workflow's verify-by-use steps that fire the engine must check `company gpu` first, `ensure`/`up` the model they need, gated-evict, never stomp a co-resident session.

## THE SELF-ADVANCING FRONT-END (⑫ — first-use friction is the input, not a failure)
Running a composition by-use surfaces the real seam-gaps. Those gaps are the ⑫ backlog: ⑫ reads the surfaced needs-tim/flags (from `.build/.../WALKTHROUGH.md` + lane-report `flag` fields + ②/⑤ findings) → scouts each against the code → drafts the next workflow's lane-cut. **The loop's new front-end: the engine reads its own gaps and drafts how to close them; I review + dispatch.** So the order is always: crank an instance → harvest gaps → expand from evidence (not prediction).

## THE SEAM BACKLOG (the tool-expansion the compositions revealed — build these as their own workflow pieces)
1. **Cascade multi-variable prompt substitution** — today a decl threads ONE `inputs` value + fixed per-step roles; richer per-step `${var}` interpolation is unbuilt.
2. **The `retrieve`/`similarity` cascade ops** — no engine primitive yet (retrieve runs inline + feeds `inputs`).
3. **Role-scoped capability gating** — B5 projects op/thinking/tools against the BRAIN, not a role's bound model.
4. **`suite.py:capability_providers()` live-bind** — still resident-4b-only (CATALOG widened the DATA; the live-read is the other half).
5. **Embedder-resident handling under contention** — `ensure_resident` path proven on a stub; unproven by-use under real swap (the V-A RG10 cluster-reduce is the first test).
6. **The generalized faculty-runner** — the parameterized skeleton itself (the B build; lifts V-A's 6 pieces into role-fills).
*(Each is buildable; ⑫ orders them by leverage × file-disjointness once V-A's run says which bite first.)*

---

## THE WORKFLOW SET + SEQUENCING (what runs when)
- **Run 1 — V-A registry-generation (NOW):** the ready, safe, git-revertible instance. Builds RG1/RG3/RG6/RG7/RG8/RG9 parallel → gate+commit. Sharpened [C] briefs (register_element richer-schema + two-layer confirm). **Its by-use proof RG10 (run the cascade → a dead element resolves after Tim approves) is the first real test of: the cascade runner's 5-step run:// wiring + the embedder swap-under-contention.** Whatever it hits = the first ⑫ input.
- **Run 2 — the generalized faculty + the bitten seams (NEXT, evidence-informed):** lift V-A's 6 pieces into the parameterized faculty-workflow + build whichever seams Run-1 proved necessary. This is where ② drift-radar / ③ transcript-miner / ⑦ spec-compiler become *the same workflow, different role-fills*.
- **Run 3+ — ① repo-exocortex (the unification organ) + the rest:** the full-code semantic picture (needs the embedder window — also closes the standing needs-tim). Once ① is live, LAW 0's semantic floor turns on, and ⑫ runs continuously as the front-end.

## STATUS
- v1 (2026-06-09): the architecture above. Governs `COMPOSITIONS.md` (the work) + the V-A workflow (instance 1).
- **LAW 0 (unification) is the through-line:** every run gets the full relevant picture first + takes found-work into scope. The standing organs (①/②) make the picture self-maintaining — the system holds what no human can.
