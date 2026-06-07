---
type: constitution
module: runtime
aliases: ["runtime — constitution"]
tags: [company, constitution, runtime]
governs: [S1, C5, C6, S7]
relates-to: ["[[Company Map]]", "[[contracts — constitution]]", "[[fabric — constitution]]", "[[store — constitution]]", "[[nodes — constitution]]", "[[mcp_face — constitution]]"]
status: living
---

# runtime/ — module constitution

**Is:** the heart — the reactive scheduler (watch the store; a node fires the instant its input **addresses** resolve), the memo gate (skip nodes whose output-address already exists), the compile step (workflow→execution, C5), and context-variable resolution for the right-hand-man (C6). This is Invariant II made real (S1).
**Guarantees:** a node runs **only** when its inputs resolve · a cached node is **never** re-run and a cached model node **never** re-hits the GPU — **except** a node that declares `VOLATILE=True`, which the gate re-runs every pass *by design* (it reads mutable truth — the repo, a corpus index, a model-of-someone, a clock — whose inputs don't change but whose output must; this is the gate's defined exception, not a bypass) · pause/retry/branch are addressing operations (stop dispatch / clear an address / new `@branch`) · model dispatch passes a **VRAM semaphore** so the 16 GB card can't OOM · never blocks waiting on Tim.
**Where new things go:** a new context-variable → `context_variables/`. Scheduler logic stays **generic over node-type**.
**To extend:** register a `ContextVariable` (C6); never special-case a node-type inside the scheduler.
**Seam:** uses [[store — constitution]] (C1/C4), operates on C3 records, runs `compile` (C5), resolves context (C6), calls [[fabric — constitution]]. The **decision→implementation wire** (`implement.py` + `dispatch_decision`) reaches OUT through this seam too — it launches Claude Code headlessly (`runtime/implement.py`) and feeds the result back onto the surfaced item, never around the substrate.
**Never:** bake a node-type into the scheduler · bypass the memo gate *ad hoc* (the **only** sanctioned re-run is a node's own `VOLATILE=True` flag — honoured generically by the gate, never special-cased per type) · re-hit the GPU on a cached result · introduce a second "graph" notion (no workflow-engine; durability comes from the addressed store).

## What's in here

The reactive engine room. The **scheduler** watches the store and fires a node the instant
its input **addresses** resolve — no run order, only readiness. The **memo gate** guards the
GPU and the clock: a node whose output-address already exists is skipped, *unless* it
declares `VOLATILE=True`, in which case the gate re-runs it every pass by design. **Compile**
turns a workflow into an execution (C5); **context-variable resolution** feeds the
right-hand-man (C6). And `suite.py` holds **the Suite — the brain**: the engine verbs, the
RHM, the self-modification path, and **the decision→implementation wire** — the one object
[[mcp_face — constitution]] and the bridge both speak to.

**The decision→implementation wire** (`implement.py` + `dispatch_decision`/`surface_build_intent`,
Group W) closes the circuit *recorded decision → governed dispatch to Claude Code → verify → result
back → status=`implemented` **AND surfaced for review*** (AI-operated is NOT review-free), with no
human re-prompt in the middle. It **reuses** existing seams, never a
parallel system: the `derived_from` three-part bind (the dispatch is authorized by the operator's
approve, read from the substrate — `_verify_resolve_bind`, factored from `commit_criterion`); the
append-only event log for **exactly-once** (a `decision.dispatch` event keyed on the resolve `seq`
refuses a second launch — the CHECK→CLAIM section is held under a per-seq in-process lock so a true
thread race over the one Suite can't double-launch, and the durable event is the cross-process/restart
guarantee) and for visibility (`decision.dispatch`/`implemented`/`verify`/`surfaced_for_review`); POLICY POSTURE for the
auto-vs-surface routing; and the **separate `status` lane** (`implemented`) so a build closes WITHOUT
code ever writing the operator `resolved` field. A **declared** consequence class set at surface time
gates auto-vs-surface *before* dispatch on its **posture**: ONLY an `AUTO`-posture class auto-dispatches
(`decision_build` is the one such class — the operator's declared-scope approve IS its authorization).
`AUTO` means auto-**DISPATCH** on the approve (no second gate *before* building) — it does **NOT** mean
auto-**CLOSE** without review;
ANY `CONFIRM`/`SURFACE`/`LOCKED` declared class surfaces for the operator instead (a CONFIRM class like
`destructive`, absent from the LOCKED set, can no longer slip through). The close is `guard("code_build")`-ed
(CONFIRM) on the verification verdict so an unverified close RAISES; a post-build scope-diff (git ground
truth; an EMPTY declared scope is DENY-ALL, never allow-all; paths normalized so `..` can't fool the
guard) surfaces a wandering build back instead of closing it. **AI-operated is NOT review-free (root
AGENTS.md rule 9):** the SAME guarded close that writes `implemented` ALSO surfaces a review item — a
`decision.surfaced_for_review` event + a `build_result_review` inbox item (the existing `surface_review`,
no parallel review system) carrying the result summary + the changed-files diff + `derived_from`, so the
operator sees it in the RHM organ. `implemented` means "done AND surfaced for review", never a silent
terminal; reversible/AUTO builds are non-blocking (the change is made + git-reversible) but ALWAYS
surfaced. The review item is **not** a build-intent (inert to the dispatcher) — approving it reviews, it
never triggers a rebuild. Surfacing the review is part of the ONE dispatch (the `decision.dispatch` claim
is the exactly-once key), never a second dispatch. The build instruction (`build_instruction`) carries
the STANDARDS the work must meet (the product UI/UX bar for any operator-facing surface; the
self-description updated as part of the change; a separate review pass + the operator will review) — it
is **not** asked to self-review (self-review is the weakest kind, and a headless `claude -p` can't drive
a browser); reviewing is a separate stage. *Dispatch* is kept **off the MCP face** (not in `RHM_VERBS`) —
the RHM proposes/surfaces, it never dispatches a build of its own authority. The **production entry seam**
(T0-WIRE) is `POST /api/build-intent` on the OPERATOR face (`bridge.py` → `surface_build_intent`): it only
SURFACES a build-intent (`resolved=None`) for the operator to approve via `/api/resolve` (operator-only);
the WIRE-LOOP then dispatches it. Surfacing-only on the operator face is consistent with "the RHM
proposes/surfaces, never dispatches" — only `dispatch_decision` stays off-face. The exactly-once
`decision.dispatch` claim is written via `_emit_durable` (FAIL LOUD — T1-EMIT), distinct from the lenient
telemetry `_emit`, so a swallowed claim can never silently allow a double-launch. The live capability list
lives in [[Company Map]] — traverse there rather than re-listing it here (the rule in [[Vault Conventions]]).

**The conversational → self-build bridge** (`request_change`, an `RHM_VERBS` whitelist verb) is the
chat entry to the wire. The dispatcher only acts on `intent=="build"` items (`is_build_intent`), which
were minted ONLY by the wire-DOOR (`/api/build-intent` → `surface_build_intent`, `/api/intent-at` →
`surface_intent_at`); the RHM's `build` composes canvas nodes and `propose`/`panel`/`extend` author
NET-NEW components via `/api/apply`, so conversing could not drive an edit-existing-code build.
`request_change` routes a conversational change-request into the EXISTING `surface_intent_at` producer
(REUSED — no parallel intent path), minting an `intent=="build"` item that surfaces for approval through
the SAME inbox/build-intent card + operator-only `/api/resolve` approve. **Nothing builds until the
operator approves** — the approve→dispatch trigger (`resolve_surfaced` + `drive_dispatchable`) is
operator-only, off the MCP face, and UNCHANGED; the wire still only dispatches when armed
(`COMPANY_WIRE_PERMISSION`). Address resolution (`resolve_change_target`, reusing `UI_REGISTRY` +
`parse_ui_address` + `_describe_ui_address`): an explicit RESOLVABLE target (a registered `ui://` or an
unambiguous named element, via a custom confident-single-match-else-ASK matcher) WINS over the held
locus (`current_locus()` is session-held, not this-turn — a stale click must never override a target the
operator named this turn); else the indicated locus; else it ASKS which element — never a guessed scope
(rule 8 — a wrong scope is a wrong build). Proven by `tests/conversational_build_acceptance.py`.

## Relates to

- **Called by** [[canvas — constitution]] — through the bridge (C8) — and by
  [[mcp_face — constitution]], which shares the **one Suite** rather than holding its own.
- **Uses** [[fabric — constitution]] (every model call passes through its guards) and
  [[store — constitution]] (it reads and writes by **address**, never by handle); and it
  **runs** [[nodes — constitution]] — the scheduler dispatches a node-type the moment its
  inputs resolve.
- **Governed by** [[contracts — constitution]] — C5 (compile: workflow→execution) and C6
  (context-variable resolution) are the contracts this folder makes real.

## Read next
[[Company Map]] (the live registry + the whole picture) · [[nodes — constitution]] (what the scheduler runs) · [[Concepts and Principles]] (the addressing/memo ideas this depends on).
