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
back → terminal status*, with no human re-prompt in the middle. It **reuses** existing seams, never a
parallel system: the `derived_from` three-part bind (the dispatch is authorized by the operator's
approve, read from the substrate — `_verify_resolve_bind`, factored from `commit_criterion`); the
append-only event log for **exactly-once** (a `decision.dispatch` event keyed on the resolve `seq`
refuses a second launch — the CHECK→CLAIM section is held under a per-seq in-process lock so a true
thread race over the one Suite can't double-launch, and the durable event is the cross-process/restart
guarantee) and for visibility (`decision.dispatch`/`implemented`/`verify`); POLICY POSTURE for the
auto-vs-surface routing; and the **separate `status` lane** (`implemented`) so a build closes WITHOUT
code ever writing the operator `resolved` field. A **declared** consequence class set at surface time
gates auto-vs-surface *before* dispatch on its **posture**: ONLY an `AUTO`-posture class auto-dispatches
(`decision_build` is the one such class — the operator's declared-scope approve IS its authorization);
ANY `CONFIRM`/`SURFACE`/`LOCKED` declared class surfaces for the operator instead (a CONFIRM class like
`destructive`, absent from the LOCKED set, can no longer slip through). The close is `guard("code_build")`-ed
(CONFIRM) on the verification verdict so an unverified close RAISES; a post-build scope-diff (git ground
truth; an EMPTY declared scope is DENY-ALL, never allow-all; paths normalized so `..` can't fool the
guard) surfaces a wandering build back instead of closing it. It is kept **off the MCP face** (not in `RHM_VERBS`) — the RHM
proposes/surfaces, it never dispatches a build of its own authority. The unattended trigger (the watcher
/ loop that *calls* `dispatch_decision` from a resolve event) is the WIRE-LOOP seam, built separately. The live capability list lives in [[Company Map]] — traverse there
rather than re-listing it here (the rule in [[Vault Conventions]]).

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
