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
guard) surfaces a wandering build back instead of closing it. **GIT CHECKPOINT (Tim's safety mandate
before arming):** after all gates pass and BEFORE the close marks `implemented`, the wire commits
EXACTLY the build's `changed_delta` paths as a single `[self-build] <sid>: <intent>` commit
(`_self_build_commit` → `_git_self_commit` with the `[self-build]` prefix — reuse, not a parallel git
path; path-scoped `git add <delta>` so a concurrent writer's unstaged dirty files are NEVER swept in),
so every accepted autonomous build is one `git revert <sha>` from undone (the same prefix-agnostic
operator revert path as `[self-apply]`). The sha is recorded (item · `decision.implemented` event · the
review item). A commit failure (or an empty delta) FAILS LOUD — surfaces the build back via a
`decision.verify` terminal event, NEVER `implemented` (a build that can't be checkpointed is not
safe-closed). The `committer` is injectable (threaded through `drive_dispatchable`) so tests never
commit the live repo. These `[self-build]` checkpoints are surfaced alongside the `[self-apply]`
self-mods — AND the operator's own `[checkpoint]` restore points (below) — in the **unified
self-change audit ledger** (`self_change_log`/`last_self_change`, each record **stream-tagged**
`self-apply`|`self-build`|`checkpoint`; `GET /api/self-change-log`), and all undo through the one
prefix-agnostic `revert_self_change` — so every reversible change is visible AND one-click revertible
from one place, not just revertible-by-sha off its review item. The stream set is single-sourced
(`Suite._SELF_CHANGE_STREAMS`): the subject-classifier, the revert-tagger, and the ledger's `--grep`
net all derive from it, so a stream can't be added without the ledger seeing it (fail-loud one-source,
rules 3+4). **AI-operated is NOT review-free (root
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
coherence, C4.4, and runs the tool block, C4.5).

**The engine triad (C-build): `run_swarm` is MAP, `run_reduce` is the cross-unit JOIN, `run_jury` is the
draws-reduce.** `run_swarm` fans N roles × 1 ctx → N `run://` outputs (map). `run_reduce(addresses, store,
*, mode)` (C 2/4) reads those outputs back via the SHARED `_read_back` helper (the same primitive the jury
uses — jury body unchanged) and joins them: `mode="role"` synthesises N→1 via a reduce-ROLE whose input is
the composed outputs (the C 1/4 input-axis); `mode="rule"` is a pure deterministic verdict over them (L2,
no model — mirrors `run_jury`'s `verdict_rule`); `mode="cluster"` embeds (op=embed) + greedy-cosine-groups
(reusing `nodes/retrieve._cosine` / `vector_index.query_index`) — the cross-unit "which of these are the
same" join, the **built-twice-discovery** primitive. `run_reduce` is a DRIVER (the model runs only in a
reduce-role; rule/cluster are pure L2) and emits NO resolve/approve/dispatch (the floor holds). It wires
the previously-declared-but-dead `reduce-tree` THOUGHT_SHAPE live. **`run_items(role, items, store, *,
turn_id, ...)` (C 3/4) is the fourth — the axis-INVERSION: 1 role × N units** (vs `run_swarm`'s N roles ×
1 ctx), fanning ONE role over N input-units (each a literal or an address), output per-unit at
`run://<turn>/<role>/<i>`; it mirrors `run_swarm`'s gate/pool/barrier/rollup (reuse, not forked). Its
companion **`resolve_address(store, addr, *, turn_id)` is the scheme-dispatching resolver** (the
"resolve content from ANY address" seam): materialises `<turn>` templates, then dispatches by `://`
presence — `run://`→`resolve_run_ref`, `cas://`→`get_content` (both REUSE), a bare name→a `BARE_NAME`
sentinel (a ctx-key), and **every other scheme (`skill://`/`context://`/blob/vec/ui/code) RAISES
fail-loud — the extensible seam where those resolvers plug in** (skills/contexts are net-new addressable
registries landing on this seam, C 3b). The `run_role` input is `ctx`-supplied (default `Utterance:`) OR
resolved from `input_addresses` via the address system (C 1/4 seam — a role's input can be a skill / a
context / any upstream output, set by address); `op: generate|embed` selects the operation (embed reuses
`complete_embeddings`, local-resident only). Add a new shape/grain ⇒ add it to
`THOUGHT_SHAPES`/`PART_GRAIN` **and reflect it here**, or `tests/chat_parts_acceptance.py` fails loud.

**The run INDEX — runs are DISCOVERABLE as inputs, not just known-by-address (#54 storage-discovery).**
Run outputs are already durable + addressed (`run_role`/`run_items`/`run_reduce` write `run://<turn>/<role>`
via CAS, immutable, cross-session) and read back by `resolve_address` — but there was **no list/query over
them**, so an agent could only read a run it already KNEW the address of. The keystone of "outputs→inputs"
composability is **discovery**: each engine run now emits ONE cheap `op.run` RUN-INDEX event to the store —
`run_items`/`run_reduce` inside the engine fns (next to their `cognition.items`/`cognition.reduce` rollup,
through the SAME `emit` sink), `run_role` in its MCP wrapper (engine `run_role` has no emit + does not
persist — the CALLER assigns the address — and it's reused INTERNALLY per-cast-role/per-draw, so emitting
there would flood the index; the emit lives colocated with the discoverable persist, exactly ONE per
agent-facing run). The event carries `op` (the closed `Suite.ENGINE_RUN_OPS` = `cognition.run_role`/
`run_items`/`run_reduce`) · `run_op` (generate|embed|role|rule|cluster) · `turn_id` · `role` · the
introspective `duration_ms` (the SHARED `op.run` field — `run_stats` rolls it up for free, this is the
**introspective-data law**: a run self-instruments) · and the per-fan `addresses` list (the C1.6
**one-emit-per-fan** discipline — never one `append_event` per unit). **`Suite.list_runs`/`find_runs`** are
a READ-TIME PROJECTION over that log (`events_since`, the `run_stats` sibling — the op.run log IS the index,
**no maintained index, no new store, NO `fs_store` edit, no parallel DB**), EXPANDING the per-fan addresses
into one discovered ROW PER concrete `run://` address; `find_runs(role=…|op=…|run_op=…)` filters. The MCP
`list_runs`/`find_runs` tools expose the same to agents. **Behaviour-preserving** (a run's output persists
to `run://` exactly as before — the index is purely additive) and **the floor holds** (the `op.run` emit is
telemetry — `append_event(kind='op.run')`, NEVER a resolve/approve/dispatch; `cognition_governance` stays
19/19). Proven by `tests/run_discovery_acceptance.py` (the run index + projection + MCP tools + the full
outputs→inputs-**by-discovery** loop, live against the resident 4B). **NOT built (deliberate follow-up):**
lifecycle — `run://` outputs are **unbounded** (no gc/ttl); discovery is the keystone, gc is a later call.
A reduce's joined output is not landed at a `run://` address today (its `op.run` row carries empty
`addresses`), so a reduce is discoverable-as-having-happened but not yet feedable-by-address.

## The activation contexts (Concurrent Cognition G5 · `runtime/activation.py` + `runtime/suite.py` · the dial generalised)

The **activation contexts** generalise "mode" (the presence dial) from *presence-modes* to the named ways
a cast can fire. Per-turn (the live reply) is the spine of G0–G4; G5 adds the **three NET-NEW non-turn
triggers** as declared data + real entry points (R1-FOLD F7 / R2-FOLD H6 — there was NO activation
substrate: `background` was only a presence-MODE directive, zero `.timer` units). **The always-on DRIVERS
that *call* these entry points (the idle-loop daemon · the OS/bridge event-hook source · the timer
scheduler) are system-lifecycle + GPU-always-on concerns → needs-tim; this build provides the MECHANISM +
entry points, proven by USE (invoking fires the cast).**

**The net-new registry (drift home — C9.4 / R2-FOLD H5; `tests/activation_contexts_acceptance.py` asserts
it stays reflected HERE, mirroring `rules_acceptance` → `RULE_OPS`):**

- **`ACTIVATION_CONTEXTS`** (`runtime/activation.py`) — the named contexts (L1 declared data). Each row
  DECLARES its trigger kind (the needs-tim driver), whether it produces a spoken REPLY, the allowed
  `DESTINATION_KINDS`, and whether it fires a swarm:
  - **`per-turn`** — the live reply; trigger=turn; owned by `chat()`/`chat_parts()` (the G0–G4 spine —
    registered as the BASELINE, NEVER fired by `fire_activation`).
  - **`background`** — an IDLE-LOOP tick fires the mode's cast between turns; **NO reply**; destinations
    surface/address/lane.
  - **`sense`** — an EVENT-HOOK (screen/app/state change) fires the cast given a sense event; NO reply.
  - **`rollup`** — a TIMER tick runs the **introspective-data-building** consolidation of the swarm's OWN
    `run://`-addressed run-records (the `cognition.wave` telemetry) into ONE rollup distribution at a
    `run://rollup/<id>` address (READ-HALF — fires no swarm; GC targets the superseded `run://` CAS refs,
    NEVER the append-only event log).

**Entry points (reuse-don't-parallel):** `Suite.fire_activation(context, …)` → `activation.fire_activation`
fires the cast via `run_swarm` (G1) and routes the outputs via `rules.route` (G3) — so the **`claude -p`
floor holds by construction** (the five `DESTINATION_KINDS` are non-consequential; `surface` goes through
`surface_review` → an `ask`, never a `resolve`). `Suite.consolidate_rollup(…)` → `activation.consolidate_rollup`
reuses `run_stats`' distribution math. NO second scheduler/executor/inbox.

**`ACTIVATION_ALLOCATION`** (`runtime/suite.py`, C5.5) — a MODE allocates which contexts are LIVE, the slot
BUDGET (`reserve_r`/`per_role_ctx`/`main_ctx_tokens` — the `SlotBudget` is COMPUTED from these against the
live registry, never a literal), AND the declared brain CONFIG (the mode→loadout registry, H8/H1:
`swarm-16k` for the swarm-heavy `background` mode, `voice-64k` for voice-depth modes — DECLARED here, NOT
swapped by this build; driving `company up/swap` is the always-on loadout concern, needs-tim).

**THE RESERVE IS SACRED (C5.5):** `reserve_r` is the per-turn live-stream reservation; `fire_activation`
FAILS LOUD if a mode declares it below `FLOOR_RESERVE_R`. A non-turn cast runs under
`swarm_slots = max_num_seqs − reserve_r`, bounded by the SAME process-wide `cognition.global_vram_gate`
the per-turn stream uses → R permits ALWAYS stay free for the live per-turn call (a background swarm can
never starve it). Add a context ⇒ add it to `ACTIVATION_CONTEXTS` **and reflect it here**, or
`tests/activation_contexts_acceptance.py` fails loud.

## The live cognition VIEW backend (Concurrent Cognition L-fe-be · `contracts/cognition_info.py` + `runtime/suite.py` + `runtime/bridge.py` · §F net-new backend)

The live cognition VIEW (`build-prep/concurrent-cognition/06-rendering.md`) is a **generic
reflects-never-owns renderer** of the collective-cognition layer — exactly as the canvas is a generic
renderer of node-types. The backend it renders from is **a SIBLING projection, not new machinery** (06
§B.3): the cognition registries serialize through `build_cognition_info` (the sibling of
`build_object_info`), and the view lights up from per-turn `cognition.*` LIFECYCLE events on the existing
`/api/stream` SSE (mirroring the `decision.*` precedent).

**The projection (`contracts/cognition_info.build_cognition_info` → `Suite.cognition_info()` →
`/api/cognition_info`):** GENERATED FROM the live registries (rule 3, one source) — never hand-written —
and FAILS LOUD on a key/id disagreement (mirrors `object_info.py:79-83`). Serializes the file-discovered
roles + each role's declared rules/render-hint/facet, the declared G3 rules (`as_record`), and the
net-new cognition registries `EDGE_KINDS` · `THOUGHT_SHAPES` · `ACTIVATION_CONTEXTS` · `RULE_OPS` ·
`DESTINATION_KINDS` · the cast-per-mode · the cognition node-state vocabulary. **DYNAMIC + REUSABLE
(Tim's directive):** drop a role file / a rule / an edge-kind → it appears in the projection live, no FE
code (the ComfyUI generic-renderer pattern). `cognition_capabilities()` and `cognition_info()` share the
SAME role serializer (`contracts.cognition_info._serialize_role`) — never two role serializers that can
drift (reuse-don't-parallel).

**The net-new registry (drift home — C9.4 / R2-FOLD H5; `tests/cognition_info_acceptance.py` asserts it
stays reflected HERE, mirroring `rules_acceptance` → `RULE_OPS` and `edge_kinds_acceptance` →
`contracts/AGENTS.md`):**

- **`COGNITION_EVENT_KINDS`** (`contracts/cognition_info.py`) — the per-turn cognition.* LIFECYCLE
  emit-contract the staged-turn path (`Suite.chat_parts`) writes onto the ONE event log (lenient `_emit`
  telemetry — NARRATION/visibility, reflects-never-owns, never a safety claim) and `/api/stream` serves.
  The FE (L-fe) binds to THIS contract, not an invented one (06 §F#3). Each carries a TOP-LEVEL `address`
  (the locus, C7.2): `ui://cognition/<turn>` for the turn frame, `run://<turn>/<role>` for a role
  instance (run:// reuse — NOT a net-new `cog://` scheme; §H default lean). The kinds, EMITTED
  SYNCHRONOUSLY at true causal points (the honest order under concurrency: `turn.start` →
  `role.fire`×N pre-wave → `part`(1) early → `role.ran`×N post-join → `inject` → `part`(2) →
  `turn.done`):
  - **`cognition.turn.start`** `{turn_id, mode, shape, grain, cast[], address}` — the swarm is about
    to fire; the view opens a turn frame.
  - **`cognition.role.fire`** `{turn_id, role, model, address=run://<turn>/<role>}` — a role's model
    call is launched (the dot goes 'firing'). Synchronous + deterministic, one per fireable role.
  - **`cognition.role.ran`** `{turn_id, role, ok, ms, error?, address=run://<turn>/<role>}` — a role
    returned (read off the wave's `RoleRun` records after the barrier).
  - **`cognition.inject`** `{turn_id, rule, source, role(=source alias), into, chars, address=run://<turn>/<source>}` —
    a declared G3 rule injected a role's output into the final reply part (the injection edge SOURCE→brain
    lights up). The `source` role is always identified (recovered from the rule's `value_path` when the
    rule isn't role-attached). `cost` (the edge weight) is DEFERRED until C6 faculty injections exist.
  - **`cognition.part`** `{turn_id, part, final, staged, address=ui://cognition/<turn>}` — a staged
    reply part was emitted (the river fills).
  - **`cognition.turn.done`** `{turn_id, total_ms, n_parts, n_roles, address=ui://cognition/<turn>}` —
    the turn completed; the view closes the frame.

  **PRESERVED:** the per-WAVE `cognition.wave` rollup (`run_swarm`, C1.6) is UNCHANGED — these per-TURN
  lifecycle events are ADDITIVE narration alongside it. **THE FLOOR (C9.2):** no cognition.* kind is —
  and none may ever be — a `resolve`/`approve`/`dispatch`; a cognition.* event NARRATES backend truth,
  it can never forge an operator action. Add an event kind ⇒ add it to `COGNITION_EVENT_KINDS` **and
  reflect it here**, or `tests/cognition_info_acceptance.py` fails loud.

## The authoring backend (Concurrent Cognition C7.4/C7.5 · `runtime/authoring.py` + `runtime/suite.py` · the WRITE-side)

The cognition layer is now **authored from the surface**, not only viewed. The write-side **GENERALIZES
`propose_node`/`apply_node`** (the propose-not-apply governance path) to **roles + rules** — never a parallel
authoring system:

- **`runtime/authoring.py`** — the PURE half: the **ONE fields→source renderer** (`render_role_source`:
  operator field-set → a real `roles/<id>.py` module declaring `class <Name>Out(BaseModel)` + `ROLE = {…}`
  — C7.5's "dynamically define structured outputs"), the **closed field-type registry** (`FIELD_TYPES`:
  str·int·float·bool·list[str]·list[int]; an unknown type fails loud — rule 8), and **THE GATE**
  (`gate_role_source` / `load_role_from_source`): validate a generated module by **discovering it in a temp
  dir OUTSIDE the live tree** (mirrors `Suite._gate_extension`). This is the #1 constraint — a malformed
  `roles/*.py` makes `RoleRegistry.discover` RAISE, which would brick the WHOLE cognition layer; so a bad
  role fails loud at propose/apply and NEVER reaches the live `roles/` dir.
- **`Suite` role write-path** (suite.py, propose-not-apply): `propose_role` (operator field-set OR a
  brain-drafted `brief`; renders + GATES + SURFACES) → operator approves via the existing operator-only
  `resolve_surfaced` → `apply_role` writes the file ONLY on `inbox.is_approved` (authorization READ from the
  inbox, never a caller flag), git-commits (revert-able), re-discovers → the role appears in
  `/api/cognition_info` LIVE. `edit_role` (re-propose) · `delete_role`/`apply_role_delete` (surfaced removal).
  A **`role_build`/`role_delete`** action class (declared CONFIRM in `governance.py POLICY`) routes
  `apply_surfaced` to `apply_role`/`apply_role_delete` — a role is a `roles/` file, NEVER mis-written to
  `nodes/`. **`PROTECTED_ROLES`** (the roles `cognition.py` imports by name — focus·recall·ground·judge·
  verify_jury·voice·check·connect) are REFUSED for edit/delete even on approve (a brick is never an
  acceptable approve outcome — surfaced as needs-tim instead).
- **Rule authoring** (exposes the `runtime/rules.py` primitives — never a second evaluator): `validate_rule`
  (wraps `validate_ast` + the destination check → `{ok, errors, references, destination_ok, renderable,
  when_text, depth}`) · `dry_run_rule` (wraps `Rule.decide` over sample values → the routing decision, no
  effect) · `attach_rule`/`detach_rule` (constrained `edit_role` mutating `ROLE['rules']`, propose-not-apply).
- **Test/preview**: `dry_run_role` (fire ONE role — registered OR a draft field-set — via `cognition.run_role`,
  the SAME fire path the swarm uses) · `preview_turn` (fire `chat_parts` → the parts + the per-turn
  `cognition.*` lifecycle, mode set+restored; never a parallel turn engine).
- **The SELECTs** (every FE dropdown from truth): `models_for_role` (wraps `capabilities.suitable_models` —
  models whose provides ⊇ requires) · `available_inputs` (utterance + roles' run:// addresses + context vars)
  · `field_types` (the closed registry).

**THE FLOOR (C9.2) HOLDS:** no authoring method emits `resolve`/`approve`/`dispatch` — authoring SURFACES,
the OPERATOR approves. None is in `RHM_VERBS` (operator-face only, like `/api/build-intent`; no
self-author-and-approve). Endpoints: `POST /api/cognition/{role/propose,role/edit,role/delete,role/dry_run,
rule/validate,rule/dry_run,rule/attach,rule/detach,preview_turn}` + `GET /api/cognition/{models_for_role,
inputs,field_types}`; apply rides the existing operator-only `/api/apply` (+ `/api/resolve`). Proven by
`tests/authoring_acceptance.py` (the create→approve→live loop, the gate, validate good+bad, the dry-runs,
the selects, delete + protected-refuse, the floor source-invariant). The FE design brief is
`build-prep/concurrent-cognition/AUTHORING-FE-HANDOFF.md`.
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

**The operator checkpoint** (`Suite.checkpoint(paths, label)` → `POST /api/checkpoint`, operator-only)
is the THIRD reversible stream (`[checkpoint]`), beside the two AUTONOMOUS ones (`[self-apply]` self-mod,
`[self-build]` the wire's accepted builds). It lets the operator stamp their OWN reversible restore point
— "checkpoint these files so I can experiment, and revert if it goes wrong" — committed through the SAME
`_git_self_commit`, surfaced in the SAME ledger, undone through the SAME prefix-agnostic
`revert_self_change`: a thin reuse, never a parallel git/ledger/revert path. **Path-scoped on purpose**
(root AGENTS.md rule 10 — Tim runs MULTIPLE sessions on `main`): it commits EXACTLY the named paths
(pathspec), so a concurrent session's unstaged in-flight work is NEVER swept in and a revert can never
destroy it — a whole-tree checkpoint would be a footgun and is **refused**. Three fail-loud guards
(empty/whole-tree path-set · a path escaping the repo root · an empty delta — committing nothing is not a
restore point; rules 4+8). Kept **off the MCP face** + out of `RHM_VERBS`, like `revert_self_change` —
the RHM proposes/surfaces, it never commits of its own authority; minting is an operator act on the
operator face. Proven by `tests/selfmod_audit_acceptance.py`.

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
