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

## The rule engine (Concurrent Cognition G3 · `runtime/rules.py` · the L2 core)

A **rule** is the deterministic routing primitive of the collective cognition (L2): a role emits
structured output; **declared rules** decide what happens to it — route/inject/chain/land/surface.
*"That is the main mechanism that all of this application is aimed at."* A rule is a **declared
data-AST interpreted by a RESTRICTED evaluator — NEVER `eval`/`exec`/`compile`** (a dict tree with a
closed op-set, authored AS data, never a parsed string). This generalizes the G0 spike's hand-written
`cognition.injection_rule` into declared data (the spike rule is now the first declared AST, proven
identical). **A model runs ONLY inside a role, NEVER inside a rule** — a rule is a pure decision over
resolved values; the **driver** (cognition.py/suite.py) performs the effect (mirrors `gate.py`: the
node returns `{port:value}`, the scheduler does the `set_ref`).

Determinism is **structural** (R1-FOLD F5 / R2-FOLD H2): the grammar has only boolean/comparison/
arithmetic/field-access/membership over resolved `run://` values + static literals — `now`/`random`/
`call`/IO/wave-completion-order/partial-results **cannot appear** (they are not ops). Field-access is
dict-key traversal on the resolved values only (never `getattr`/dunder reach). The evaluator is handed
ONLY fully-resolved values (the `gate.py` purity discipline) → identical inputs route identically
regardless of role finish-order. **Per-rule readiness** (no global barrier, **never a timeout**): a
rule fires only when every declared input is **settled** (resolved OR provably pruned/failed). A
missing/pruned reference **fails loud OR hits a declared `on_missing`** — never `gate.py`'s implicit
truthy-on-missing. Heavier-than-a-predicate computation → a **role/node (composition)**, not a richer
rule (the rule-vs-role classifier). A **static AST whitelist-walk at commit-time** — wired into role
discovery (`roles._build_role` → `validate_role_rules`, so a malformed rule in a dropped-in `roles/*.py`
fails loud at discovery) AND at `Rule` construction (`Rule.__post_init__` → `validate_ast`, so any built
rule rides import) — rejects anything outside the grammar or past the **renderability nesting-cap**
(`MAX_RULE_DEPTH` — the edge-badge must stay legible, C3.3) — so a new/changed rule rides the **normal
change path** (no special gate, C3.4). A rule + each firing are **addressable, renderable data** (the
live view G7 draws them; reflects-never-owns).

**The two net-new registries (drift homes — C9.4 / R2-FOLD H5; `tests/rules_acceptance.py` asserts both
stay reflected HERE, mirroring `edge_kinds_acceptance` → `contracts/AGENTS.md`):**

- **`RULE_OPS`** — the closed grammar (the only ops a rule AST may use; whitelist by construction):
  - leaves: `field` (dot-path read of a resolved value) · `lit` (a static literal).
  - boolean: `and` · `or` · `not`.
  - comparison: `eq` · `ne` · `lt` · `le` · `gt` · `ge`.
  - arithmetic: `add` · `sub` · `mul`.
  - membership: `in` · `contains`.
- **`DESTINATION_KINDS`** — the five destinations a rule routes to (C3.2 · DECISIONS Batch 3 Q4).
  **CRITICAL LAW:** none of these is — and none may ever be — `resolve`/`approve`/`dispatch`
  (`FORBIDDEN_DESTINATION_VERBS`); a rule **surfaces** for the operator, it can NEVER forge an operator
  approve (the `claude -p`/build-dispatch floor is **lead-only**, C9.2 — held by construction):
  - **`inject`** — inject the routed value into a later reply part (write→`run://` address, read back
    by the C1.3 canonical resolver at part-assembly; the spike's recall-injection is this kind).
  - **`chain`** — chain/trigger a dependent role (the rule names the next role; the driver fires
    `run_role` on it — the model runs in the ROLE, never the rule). The `check` case.
  - **`address`** — land the routed value at a `run://` address for later (a durable write, no reply impact).
  - **`surface`** — surface to the inbox/decisions for the operator — **REUSES `Suite.surface_review`**
    (an `ask` event, `resolved=None`; a live escalation until the operator resolves). Never a `resolve`.
  - **`lane`** — write the routed value to a named **typed lane/channel** (a `cognition.lane` typed
    run-record on the ONE event log — a named stream, NOT a parallel channel subsystem).

`route()` is the only place a decision becomes an effect; the evaluator (`evaluate`) is pure. Add a new
op or destination ⇒ add it to `RULE_OPS`/`DESTINATION_KINDS` **and reflect it here** (the drift home),
or `tests/rules_acceptance.py` fails loud.

## The staged-response queue (Concurrent Cognition G4 · `runtime/suite.py` · the reply as PARTS)

The **staged-response queue** is the LAST piece of the spine: `chat()`'s body is **extracted into a
shared core** that BOTH `chat()` (one part) and `chat_parts()` (N parts) call (R1-FOLD F4 / R2-FOLD H3
— `chat_parts()` can neither LOOP `chat()`, which re-runs the gate + emits N chat events, nor COPY it,
which forks the brain). The shape is **prologue ONCE · part-core PER PART · epilogue ONCE**:

- **`_chat_prologue`** — the `mode=="off"` early-return (4-key) + the fail-loud capability-gate refusal
  (5-key). Both keep their OWN append+emit and do NOT reach the epilogue. The **three return shapes stay
  distinct** (off=4 · refusal=5 · normal=7) with the provenance asymmetry (off/refusal hardcode
  gold/twin; normal uses `_provenance_grade`/`_source`) — **never normalized.** The gate is an
  **instance-method call on `self`** (`self._model_supports_tools`) — the `rhm_*` tests monkeypatch that
  exact seam; break it and the gate goes green on a forked brain (the silent killer).
- **`_chat_part_core`** — one model generation + (on the **final part only**, C4.5) the tool block.
  Calls `client.complete_with_tools` **via the module ref** (`from fabric import client` — never
  `from fabric.client import complete_with_tools`; the second monkeypatch seam). Assembles
  `_chat_context` **ONCE PER PART** (it is NOT side-effect-free — emits a `warning` on a down endpoint;
  per-part is the tested behavior). **ALL parts** route through `complete_with_tools` (intermediate →
  `tools=[]`) so the seam check has teeth on every part. Returns `{text, outcomes, proposals}`; never
  appends history, never emits `chat`.
- **`_chat_epilogue`** — ONCE: `action_field` shaping · the SINGLE user+assistant append · thread bump ·
  the SINGLE `_emit("chat")`. For `chat_parts()` the reply is the JOINED parts.

**The two net-new registries (drift homes — C9.4 / R2-FOLD H5; `tests/chat_parts_acceptance.py` asserts
both stay reflected HERE, mirroring `rules_acceptance` → `RULE_OPS`/`DESTINATION_KINDS`):**

- **`THOUGHT_SHAPES`** — the ~5 archetypes (E1 / E0-EXPLORE-SYNTHESIS), built ONCE. Net-new shape fields
  `archetype` · `fanout` (wave-width policy) · `join` (the barrier-dep role, `None` = no reduce) ·
  `render_from` (which role's output G7 draws the reply from):
  - **`linear-stream`** — a sequence of reply parts, each enriched by the role wave (voice's shape).
  - **`reduce-tree`** — fan-out the cast → a `join` role reduces → one answer.
  - **`jury-select`** — N candidate draws → a deterministic verdict picks the winner (the C2.4 jury).
  - **`scatter-route`** — N classifications routed to their own lanes (no reduce, no reply).
  - **`scatter-write`** — N consolidations written to sinks (background; no reply).
- **`PART_GRAIN`** — the per-MODE config table (C4.1): mode → `{grain (line/beat/paragraph), shape, stage}`.
  `shape_for(mode)`/`grain_for(mode)` read it (fail loud on an unknown mode); `mode_stages(mode)` is the
  C4.3 never-stage flag (**`focus`/`background`/`off` never stage** — a trivial turn or a never-stage mode
  BYPASSES the swarm entirely, NO `cognition.wave` fires). Switching mode changes the grain by reading
  this table — never a per-mode branch.

`chat_parts()` (a generator yielding parts) wires the **G3 declared rules into part-assembly** (the job
the spike deferred, C4.2): Part 1 fires from base context instantly (`is_final=False`, pure generation);
the mode's cast fires CONCURRENTLY via `run_swarm` (G1) writing `run://<turn>/<role>`; the declared rules
(`cognition.INJECTION_RULE` + any AST-shaped role `rules`) read those resolved values back via
`resolve_run_ref` (the canonical resolver — NOT `_chat_context`/`_resolve_context_at`, which read
operator-notebook strata) and decide what injects into the FINAL part (which carries the prior parts for
coherence, C4.4, and runs the tool block, C4.5). Add a new shape/grain ⇒ add it to
`THOUGHT_SHAPES`/`PART_GRAIN` **and reflect it here**, or `tests/chat_parts_acceptance.py` fails loud.

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
