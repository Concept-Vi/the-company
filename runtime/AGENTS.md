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

## The corpus pillar (Cognition Engine K1/D1 · `runtime/projections.py` + `runtime/corpus.py`)

The corpus pillar rides the cognition spine: a capture/map run over a corpus produces durable,
addressed, embeddable, queryable RECORDS (the SINK the scale test was missing). Two NET-NEW modules
land here this pass:

- **`runtime/projections.py`** — the **file-discovered PROJECTION registry** (the lens vocabulary of
  the corpus pillar). A projection is a declared LENS over a unit (`what`/`topics`/`principles`/
  `worldview`/`claimed_status`/`lineage`). It is a registry **like roles/skills** — `os.listdir` →
  import `projections/<id>.py`, each a FILE not a dict (the PART-4.3 file-discovery + create_*-authorable
  BAR; add-a-row = a FILE, no code edit). Mirrors `runtime/roles.py:RoleRegistry` /
  `runtime/skills.py` exactly (the ONE registry mechanism). Drift home: `projections/AGENTS.md`;
  proven by `tests/projections_acceptance.py`. The capture-schema builder reads `model_projections()`,
  the space-keying (Group L) reads `embeddable()`, `cognition_info` reads `as_records()` — all pure
  reads (the floor). **render-NOT-judge** (K3): a lens describes; judgement is a later reduce.
- **`runtime/corpus.py`** — the **corpus-record WITH LINEAGE** (the sequencing GATE). A thin module
  over the store's EXISTING public methods (`put_content`/`set_ref`/`append_event` + read-back) — it
  does **NOT** edit `store/fs_store.py` (the STORE lane owns that). The record carries `session/round/
  project` lineage **FROM THE START**, and `write_record` **REFUSES** a record without it (fail-loud,
  NOT optional-with-default) — because corroboration (M3) is cross-SESSION and the inversion-finder
  (L2) needs the placement, so retrofitting lineage = a full re-capture. The record is indexed on the
  ONE event log via a **DISTINCT `corpus.record` kind** (NOT `op.run` — that is a CLOSED engine-run
  grammar; `list_corpus`/`find_corpus` are a read-projection over it, dedup-on-read for resume-safety).
  The cas content is deterministic (no per-write `ts` in the content) so a resumed write is a true no-op
  overwrite. Three lineage axes kept distinct: corpus lineage (here) ≠ `store.lineage()` (provenance
  walk) ≠ `decision_lineage` (event trajectory). The floor holds: `corpus.record` is telemetry, never a
  resolve/dispatch (enrolled in the `cognition_governance_acceptance` source-invariant scan). Proven by
  `tests/corpus_acceptance.py`.

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
`run://<turn>/<role>/<i>`; it mirrors `run_swarm`'s gate/pool/barrier/rollup (reuse, not forked).
**ROBUSTNESS AT SCALE (F1/F2 — caught by the whole-repo map over raw file text):** a unit is an ADDRESS
only when it **STARTS WITH a registered scheme** (`contracts.address.scheme(unit) is not None`), NOT when
it merely CONTAINS "://" — 16% of repo files mention `run://`/`ui://` MID-TEXT, and the old contains-check
sent every such file to `resolve_address` (which fail-louds on a not-resolvable scheme) and aborted the
map; now those files are LITERALS (the text the role fans over). A templated `run://<turn>/x` still
classifies as an address (it STARTS with `run://`). **The fan is per-unit RESILIENT, not all-or-nothing:**
a unit whose `run_role` RAISES (a PROCESSING failure — e.g. an over-context file → 400) goes to
`ItemsResult.failed` (recorded in the result + the `cognition.items` rollup — fail-loud VISIBILITY, never
silent), kept OUT of `runs`/`resolved` (its address was never `set_ref`'d), and the GOOD units' outputs
STILL return — one poison unit no longer discards the whole batch. The ADDRESS CONTRACT is unchanged: a
RESOLUTION failure (an unresolvable `run://` unit under the default `on_missing="raise"`) is a fatal
misconfiguration and STILL fails the whole fan loud; a declared `on_missing="skip"` records it in
`.skipped` (the two failure points are distinguished by a private `_ResolutionError` marker — resolution
re-raises after the barrier, processing routes to `.failed`). Proven by `tests/run_items_acceptance.py`
(incl. §3's resolution-fail-loud, which locks the address contract). Its
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

**F3 — CHUNK-AND-COMPOSE for over-context units (`run_chunked` · the over-context TIER).** A unit whose
text exceeds the model's context window USED to be a DEAD END (a loud 400 — correct, no silent truncation,
but unprocessable). `run_chunked(role, text, store, *, turn_id, context_window=None, compose_mode="role"|"rule", …)`
is the tier that makes the common over-context case (one big document) processable: a SIZE GATE compares
`len(text)` against a per-chunk char budget DERIVED from the model's context window — `context_window`
defaults to the LIVE registry's `max_model_len` (the SAME `ops/services.json` `config` block
`SlotBudget.from_registry` reads, `model_context_window()`; **NOTHING hardcodes 65536**; injectable for a
SHORT synthetic test window). A unit that **FITS** runs `role` ONCE via `run_role` — **byte-identical** to
today (no chunking, no reduce, no extra event). A unit that is **OVER**-context is SPLIT (`chunk_text` —
deterministic, paragraph/line-boundary preferring, hard-split fallback, the join covers the WHOLE doc),
MAPPED via **`run_items`** (1 role × N chunks — REUSE, no 2nd map), then COMPOSED via **`run_reduce`**
(`mode="role"` synthesize via `roles/reduce_synth.py`, or `mode="rule"` a pure L2 join — REUSE, no 2nd
reduce). **THE LOAD-BEARING FAIL-LOUD (the F3 law — a dropped chunk is LOUD):** the chunks ARE ONE
document, so `run_items`' F2 per-unit resilience (a poison unit → `.failed`, good units still return) is
the OPPOSITE of what F3 needs — composing the survivors would SILENTLY TRUNCATE the document. So after the
map `run_chunked` INSPECTS `.failed` AND `.skipped`; if either is non-empty it RAISES a legible error
(which chunk, of how many, why — F4) and NEVER composes a truncated document (rule 4). Additive + opt-in
(today's callers + `run_role`/`run_items`/`run_reduce` untouched); a DRIVER (the model runs only in the
map-role + the reduce-role; NO resolve/approve/dispatch — the floor holds, it only calls the two
already-floor-clean primitives; it adds NO third emit, so C1.6's per-fan rollup discipline is preserved).
Proven by `tests/chunk_compose_acceptance.py` (over-context → chunked → mapped → composed → ONE output, on
a long synthetic doc + a short injected window/mocked short-context transport; a fitting unit byte-identical
to `run_role`; a seeded chunk-failure FAILS LOUD without a partial compose).

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
A reduce's joined output is not landed at a `run://` address by `run_reduce` itself (its `op.run` row
carries empty `addresses`) — so a STANDALONE reduce is discoverable-as-having-happened but not feedable-by-address.
**The cascade RUNNER (below) closes this for a chained reduce:** it OWNS persist+index for every step, so a
reduce *inside a cascade* IS landed at a step-keyed `run://` address and IS feedable/discoverable.

**E2 — the run index is INCREMENTAL (`Suite._run_index_fold` · `runtime/suite.py`).** `list_runs`/`find_runs`
USED to re-read + re-filter the WHOLE `op.run` log on EVERY call (O(events) — caught at scale). The op.run
log is append-only with monotonic-unique seqs (T1-SEQ), so the projection is cheaply incremental: the Suite
holds the projected rows (`_run_index_rows`, oldest-first) + a high-water seq (`_run_index_hw`); each call
reads ONLY `events_since(high_water)` (the tail delta, read ONCE under `_run_index_lock`), projects the new
ENGINE_RUN_OP events via the SHARED `_project_run_event` (so a cold rebuild + an incremental fold produce
byte-identical rows), and advances the high-water over the WHOLE delta (the last delta event may itself be a
non-engine op.run, so the cursor must move past it). The op.run log STAYS the source of truth (**no parallel
store, no maintained index on disk, NO `fs_store` edit**) — the cache is a pure derived projection a fresh
Suite rebuilds from the log; cross-PROCESS safe (each process reads the disk tail past its OWN high-water,
appends are immutable). `total_records` keeps the pre-E2 EVENT-count semantics (a fan event = N rows but ONE
record). Proven by `tests/run_index_incremental_acceptance.py` (the 2nd call reads only the delta — spied; a
sibling Suite rebuilds from the shared log; cold-scan-equal).

## GROUP J — the cognition↔resolution feedback loop (the system sees its OWN thinking · `runtime/suite.py`)

R2 resolves operator-NOTEBOOK strata at the operator's locus; the swarm's per-turn cognition
(`run://<turn>/<role>`) was a PARALLEL edge that never converged back. **J1 wires the PRIOR COMPLETED turn's
cognition into what the NEXT turn's R2 resolves** — the system's own thinking becomes its context. REUSE, no
second system: `_r2_gather` (a NET-NEW `cognition` stratum) + `resolve_address` (the canonical resolver) + the
swarm's OWN lifecycle events for discovery.

- **`_r2_cognition_strata(now, intent)`** gathers the prior turns' role outputs as R2 items. COMPLETED turns
  are the `cognition.turn.done` events (one per turn, emitted in `chat_parts`'s EPILOGUE, after both parts);
  the per-role `run://` addresses come from each completed turn's **`cognition.role.ran`** events (ok-only —
  each carries `turn_id`/`role`/`ok`/`address`). **CRITICAL — NOT the #54 run-index:** the run-index
  deliberately does NOT cover the per-cast swarm (one `op.run` per cast-role "would flood the index" — see
  the run-index section above), so `find_runs` returns 0 for swarm cognition (VERIFIED BY USE: a live staged
  turn fires 6 roles that resolve at `run://<turn>/<role>` yet `find_runs`→0). `cognition.role.ran` is the
  swarm's per-turn DISCOVERY surface (`resolve_address` stays the RESOLUTION — role.ran is discovery, not a
  parallel resolver). *(The completion-criteria named "via the run-index #54"; the run-index is the wrong
  producer surface for the swarm — same INTENT, correct source. Flagged so the next agent doesn't re-derive.)*
- **THE IN-FLIGHT EXCLUSION (the load-bearing correctness):** `_chat_context` runs DURING the current turn's
  part-core (at BOTH part-1 AND part-2); the current turn's `turn.done` fires LATER (epilogue). Keying
  completed-turns on `turn.done` excludes the in-flight turn by construction — even though its `role.ran`
  events have ALREADY fired by part-2 (so it is the `turn.done` gate, NOT absence-of-events, that excludes it;
  proven by a test that seeds an in-flight turn's role.ran WITHOUT turn.done).
- **THE ANCHOR (resolves with OR WITHOUT a canvas locus):** a SECOND, dedicated R2 call in `_chat_context`
  anchored at the FIXED `Suite.R2_COGNITION_ANCHOR = "ui://cognition/recent"` (parses like the per-turn
  `ui://cognition/<turn>`), so cognition resolves on a plain chat (no selection) — the case J1 exists for. The
  items score AT the anchor (X6 cross-scheme proximity 0 → recency/intent rank them); a spec-driven `framing`
  header labels them "YOUR OWN PRIOR THINKING" (not the locus header). Suppressed in `off` mode.
- **THE OPT-IN GATE (the silent-leak guard):** the cognition stratum is gated by an EXPLICIT POSITIVE
  membership `admit is not None and "cognition" in admit` — **NOT `_ok("cognition")`** (which is True for the
  default admit-all `resolution=None`, and would SILENTLY leak conversation-global cognition into the
  address-attached reads `context_at`/`surface_intent_at` with no test failure). ONLY the dedicated
  cognition-resolution call supplies a spec whose `strata` admits `cognition`; every other R2 caller is
  byte-for-byte unchanged.
- **BOUNDED** (`R2_COGNITION_TURNS` most-recent completed turns; `R2_COGNITION_PER_ROLE` chars/role — mirrors
  `R2_RUN_VERSIONS`/`R2_HOWTO_MAX`) so it can't flood the window; **FAIL-LOUD-LEGIBLE** (a pruned ref is
  WARN+skipped, never crashes the gather). Proven by `tests/cognition_resolution_loop_acceptance.py` + LIVE
  end-to-end against the resident 4B (a real staged turn's 6-role cognition fed the next turn).

**E4 — the run-output DESTINATION (`Suite.route_run_output` · `runtime/suite.py`).** E4 = chain
save/re-run + output-destination. The SAVE + RE-RUN half IS the SAVED CASCADE (`save_cascade`/`run_cascade`,
GROUP N — a declared re-runnable pipeline; `cascade_acceptance`). The remaining bit: route a DIRECT run's
output to a named destination/lane WITHOUT a saved cascade. `route_run_output(run_address, destination, *,
turn_id, params)` READS the output via `resolve_address` (the canonical resolver) and performs the effect via
**`rules.route`** over the SAME `DESTINATION_KINDS` (`address`/`lane`/`surface`/`inject`/`chain`) — NO second
router, NO destination logic re-implemented. **THE FLOOR HOLDS BY CONSTRUCTION:** `rules.route` can only do
the five non-consequential kinds; `FORBIDDEN_DESTINATION_VERBS` (resolve/approve/dispatch) are rejected — a
routed run output can NEVER forge an operator approve or launch a build (`surface` rides `surface_review` → an
`ask`, never a resolve). Fail-loud on an unknown destination + an unresolvable address. Proven by
`tests/route_run_output_acceptance.py`.

**B-fix (P3) — `PROTECTED_ROLES` DERIVED, not a second-copy literal.** It conflated two role classes with
DIFFERENT sources: (a) the SPIKE roles `cognition.py` imports by name (`focus`/`recall`/`ground`) — a second
copy of `cognition.SPIKE_ROLES`, now DERIVED from it in `__init__` (add a spike role there → it protects here,
no edit; a fail-loud assert catches drift); (b) the load-bearing CONFIG roles suite.py's OWN machinery binds
by name (`judge`/`verify_jury`/`voice`/`check`/`connect`) — suite-OWNED dependencies with no other
source-of-truth (no role-file `protected` marker exists, and that file is not the SUITE lane's to add), kept
declared as `_SUITE_OWNED_PROTECTED_ROLES` (the honest single source for "the roles suite.py depends on by
name"). The full `PROTECTED_ROLES` is the union, built in `__init__`. *(The OTHER two B-targets:
`ENGINE_RUN_OPS` is itself the source — the emit sites mirror it — so it's already single-source, not a copy;
`api_verbs` (`capabilities()`) was a second copy of `bridge.py`'s route literals — now DE-HARDCODED: it is
projected from `bridge.BRIDGE_ROUTES` (the single-source route table) via a LAZY import in `Suite._api_verbs`
that sidesteps the circular import, with a drift test keeping `BRIDGE_ROUTES` == the live dispatcher. See "The
substrate WENT LIVE" section below for the full close-out.)*

## The cascade RUNNER (Cognition Engine GROUP N · `runtime/cognition.py` + `runtime/suite.py` + `mcp_face/server.py` · the LARGEST net-new of the corpus pillar)

A **saved cascade** is a declared, named, RE-RUNNABLE pipeline — a frozen recipe (AK4) an agent reuses
without re-deriving. **Two halves, both REUSE-don't-parallel:**

- **DECLARE + SAVE = the EXISTING one door.** A cascade IS an `ActionRegistry` row — the decl
  `{name, steps:[{op, model?, ...}], output_schema?}` VALIDATED + persisted by
  `runtime/coherence_actions.py:build_action` / `ActionRegistry` (**EXISTS — REUSED, never a 2nd validator/
  registry**). `Suite.save_cascade(decl)` is the ONE validation door (registry-is-truth: each step's `model`
  must be a member of the LIVE model registry = chat ∪ embed, else `build_action` FAILS LOUD on a hardcoded
  literal); it persists to `cascade_registry` (an `ActionRegistry` at `<store.root>/cascades.json` — ext4,
  survives reload). `list_cascades`/`get_cascade` discover them.
- **EXECUTE = the net-new RUNNER** (`cognition.run_cascade`). For each step it fires the right ENGINE
  PRIMITIVE — `run_role` (1→1) · `run_items` (MAP 1→N) · `run_reduce` (JOIN N→1) — **riding the existing
  engine, NO 2nd engine.** It THREADS each step's output → the next step's input via the `run://` resolver,
  PERSISTS + op.run-INDEXES each step (so `find_runs` sees every step), and returns the final addressed output.

**THE TWO TRAPS the design handles (the seams an agent updating this MUST preserve):**

- **TRAP 1 — the decl `op` is CONSTRAINED.** `build_action._VALID_OPS` =
  `(generate, embed, similarity, retrieve, detect, reduce)`; a step's `op` CANNOT be a primitive name
  (`run_role`/`run_items`/`run_reduce`), and `coherence_actions.py` is reuse-only (do NOT edit it). So the
  PRIMITIVE rides an ADDITIVE step field the validator copies through verbatim: **`kind` ∈
  `CASCADE_KINDS` = `(role, items, reduce)`** (`_cascade_step_kind`, fail-loud on an unknown kind). Derivation
  when `kind` absent: `op=="reduce"`→reduce · `fan:true`/`items:[…]`→items · else role. **`op` is the
  OPERATION axis; `kind` is the FAN axis** — never collapse them. `similarity`/`retrieve`/`detect` have no
  engine primitive in the trio yet → out-of-lane, **flagged needs-tim/N2** (a step using one fails loud at
  run, never silently skips).
- **TRAP 2 — `run_reduce` does NOT address its joined output** (it returns `ReduceResult.joined`; its
  `op.run` row carries empty `addresses` by design — the caller decides whether to land it). So **THE RUNNER
  OWNS PERSIST + INDEX UNIFORMLY for EVERY step:** it calls the primitives with `emit=None` (suppressing their
  self-`op.run`, which would otherwise DOUBLE-record `run_items`/`run_reduce` and give the reduce an
  addressless row), then persists each step's output to a STEP-KEYED address and emits exactly ONE `op.run`
  per step under the matching `ENGINE_RUN_OP`. This is what makes a chained reduce **feedable-by-address +
  discoverable** — closing the "reduce not addressed" gap for cascades.

**THE SEAM (output→input — the heart):** step 0 reads `run_cascade(inputs)`; step N reads step N-1's output
ADDRESS(es). **Cardinality is explicit per-primitive** (never inferred by magic): `role` consumes ONE value →
ONE address `run://<turn>/<i>-<role>`; `items` consumes a LIST → a LIST `run://<turn>-s<i>/<role>/<j>`;
`reduce` consumes a LIST → ONE address THE RUNNER persists. Step outputs are keyed by **step index**
(`<i>-<role>`), NOT bare `run://<turn>/<role>` — two steps sharing a role would otherwise overwrite (the MCP
`run_role` wrapper uses the bare form; the runner can't, a chain re-uses roles). **`resolve_role` is INJECTED**
(not imported) so the engine stays Suite-free — the Suite passes `self.role_registry` lookup (fail-loud on an
unknown role).

**THE FLOOR (AGENTS.md rule + C9.2):** a cascade step is a role-run — `run://` COMPUTATION. The runner emits
ONLY `op.run` telemetry (per step) — **NEVER resolve/approve/dispatch, launches NO `claude -p`**; a cascade is
computation, never a code-build. (Source-invariant-scanned by `cognition_governance_acceptance`.)

**MCP face:** `save_cascade(decl)` · `list_cascades()` · `run_cascade(name, inputs?)` (rich descriptions,
AK2 bar). **NOT built (deliberate follow-up):** cloud-tier routing per step (N2 — `run_role` pins
`RESIDENT_BASE_URL`; a multi-endpoint router is net-new fabric/ transport, needs-tim); looping / multi-turn /
human-tier steps (the synthesis mentions them — not in the linear-runner scope this pass). Add a kind/op
mapping ⇒ extend `CASCADE_KINDS` + `_cascade_step_kind` **and reflect it here** (the drift home). Proven by
`tests/cascade_acceptance.py` (save→validate→persist→reload + the 2-step live end-to-end against the resident
4B + per-step op.run discovery + fail-loud + the floor).

## The activation contexts (Concurrent Cognition G5 · `runtime/activation.py` + `runtime/suite.py` · the dial generalised)

The **activation contexts** generalise "mode" (the presence dial) from *presence-modes* to the named ways
a cast can fire. Per-turn (the live reply) is the spine of G0–G4; G5 adds the **three NET-NEW non-turn
triggers** as declared data + real entry points (R1-FOLD F7 / R2-FOLD H6 — there was NO activation
substrate: `background` was only a presence-MODE directive, zero `.timer` units). **The always-on CALLER
is now BUILT (`runtime/activation_driver.py` — `ActivationCaller.activation_tick(suite)` fires the DUE
clock-driven drivers [background idle-gate · held-cursor rollup · mode-detect→toggle] + sense ONLY on a
supplied real event; it REUSES the H/I entry points byte-for-byte, never bypasses the idle gate, and is
floor-covered in `COG_SOURCES`). `POST /api/activation/tick` is the live manual/external-drive seam. The
AUTONOMOUS loop (`run_activation_loop`) is OFF BY DEFAULT behind `activation_loop_enabled()`
(`COMPANY_ACTIVATION_LOOP`) — importing the bridge auto-starts nothing (the `wire_armed`/`policy=None`
inert default). ENABLING the always-on cadence live (the flag + the tick interval/triggers) is a
system-behaviour decision → needs-tim; the MECHANISM is proven by USE (a tick fires the cast).**

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

### The activation DRIVERS (Group H · `runtime/activation.py` · the dial GETS DRIVEN)

G5 built the activation-context substrate + the entry points; H builds the **decision layer** that decides
*when* to fire them. **The always-on CALLER** (an idle-loop daemon · an OS event source · a `.timer`)
stays **needs-tim** (no always-on GPU-consuming daemon is stood up — the operator's call). So each driver
is a **tickable** function the caller would invoke on a cadence — **never a thread/`while`/route/timer**.
The net-new is the DECISION/STATE each driver adds OVER the entry point; the entry point is REUSED, never
re-implemented (it still enforces the mode budget + the sacred reserve + routes over the non-consequential
`DESTINATION_KINDS` — the `claude -p` floor holds by construction). Proven by USE (`tests/activation_drivers_acceptance.py`):
a synthetic idle/event/clock tick FIRES the cast and LANDS its output at surface/address/lane (not a no-op).

- **`background_tick`** (H1) — the **idle gate**: fires `fire_activation('background')` ONLY when the mode
  allocates `background` live AND the operator has been quiet ≥ the idle threshold (read from the shared
  signal). A non-fire returns a legible reason (rule 4 — no silent no-op).
- **`sense_tick`** (H2) — the **event intake**: shapes a RAW screen/app/state event → the `sense_event`
  dict (a `summary` the cast reads as its utterance) and dispatches `fire_activation('sense')`. Fail-loud
  on a non-dict raw event (never a fabricated sense event).
- **`RollupDriver`** (H3) — the **held cursor**: `.tick()` consolidates the cognition.wave records since
  the HELD `since` cursor (so a tick never re-consolidates prior waves), advancing the cursor to the log
  head each tick; an empty interval is a legible no-op. `consolidate_rollup` does the math; the driver owns
  only the cursor.
- **`activity_signal`** — the **shared activity reader** (REUSED by H1's idle gate AND I1's detector — one
  reader, two consumers): a deterministic READ of the shared event log → `{idle_seconds, last_activity,
  mode, inbox, recent_kinds}`. Fires/emits nothing.

### The mode AUTO-DETECTOR (Group I · `runtime/activation.py` · the toggle GETS A CANDIDATE)

`Suite.autodetect_mode(candidate)` already honours the off/suggest/auto TOGGLE over a SUPPLIED candidate
(proven by `autodetect_setter_acceptance`); I1 builds the **detector that PRODUCES** one. **Deterministic +
FILE-DISCOVERED-registry-driven** (NOTHING static): the signal→candidate map is the **file-discovered
`mode_detection_rules/` registry** (`runtime/mode_detection_rules.py` → `Suite.mode_detection_rule_registry`),
walked first-match-wins by the declared **`priority`** — no model (non-deterministic + GPU), no inline
if/else ladder, **and no hardcoded list** (the rules USED to be a `MODE_DETECTION_RULES = [...]` literal
with lambda predicates; that was a CODE-edit-to-add + a SECOND predicate mechanism, so it was converted to
a file-discovered registry whose conditions are declared `rules.RULE_OPS` data-ASTs — see
[[mode_detection_rules — constitution]]). The detector FEEDS `autodetect_mode` (never `set_mode` directly —
the toggle owns the posture; a suggestion SURFACES via the existing `mode` event, never a silent switch
outside the declared posture). The periodic CALLER is the same needs-tim seam as H.

- **`detect_mode_candidate`** — a pure READ that walks `suite.mode_detection_rule_registry.ordered()`
  (ascending `priority`) over the `activity_signal` snapshot → `{candidate, why, signal, rule, priority,
  rule_index}` (candidate=None ⇒ no rule matched). A rule whose candidate is not in `suite.MODES` FAILS
  LOUD (rule 8 — validated at DETECT time, since the registry can't see the live mode set at discovery).
  Each rule's `when` is pre-validated at registry discovery (`rules.validate_ast`) + evaluated PURE
  (`rules.evaluate`).
- **`propose_mode`** — runs the detector and, if the candidate DIFFERS from the live mode, feeds it to
  `autodetect_mode` (off no-ops · suggest surfaces · auto switches). A candidate equal to the live mode is
  a no-op.

**The detection-rule REGISTRY (the file-discovered registry — drift home is its OWN constitution
[[mode_detection_rules — constitution]]; `tests/mode_autodetect_acceptance.py` asserts the discovered rules
stay reflected there + the registry named HERE, mirroring `projections_acceptance` → `projections/AGENTS.md`):**

- **`mode_detection_rules/`** (`runtime/mode_detection_rules.py:ModeDetectionRuleRegistry`) — the
  file-discovered signal→candidate rules. Each `mode_detection_rules/<id>.py` declares a module-level
  `MODE_DETECTION_RULE = {id · candidate · why · when · priority}`: `when` is a `rules.RULE_OPS` data-AST
  over the `activity_signal` keys (idle_seconds/last_activity/mode/inbox/recent_kinds), `priority` orders
  first-match-wins (ascending — **NOT** listdir/filename order; detection is order-bearing). Add/tune a
  rule = a **FILE** (add-a-row=a-FILE, no code edit), mirroring `roles/`/`projections/`. The seed rules:
  `background` (priority 10 — long idle), `focus` (20 — active + clear inbox), `listening` (30 — inbox>0).
  A malformed rule FAILS LOUD at discovery; a removed file un-registers on `rediscover`.

**The other net-new drift-home registry (`tests/activation_drivers_acceptance.py` asserts it stays reflected HERE):**

- **`OPERATOR_ACTIVITY_KINDS`** (`runtime/activation.py`) — the event kinds that count as operator
  activity for the idle gate (`chat`/`cognition.turn.done`/operator graph acts); the system's OWN
  background activity (`activation`/`op.run`/mid-wave `cognition.*`) is deliberately EXCLUDED so a
  background tick can't reset its own idle clock. The shared `activity_signal` reader's `inbox` count is
  the inbox-lanes `counts.escalations` (the live-escalation lane — items the operator must work).

Add a driver/detector helper or an `OPERATOR_ACTIVITY_KINDS` member ⇒ reflect it here (or
`tests/activation_drivers_acceptance.py` fails loud); add/tune a detection rule ⇒ a FILE in
`mode_detection_rules/` + reflect it in [[mode_detection_rules — constitution]] (or
`tests/mode_autodetect_acceptance.py` fails loud).

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

## The corpus pillar — SUITE FACE (Cognition Engine GROUP B + GROUP D · `runtime/suite.py` over `runtime/projections.py` + `runtime/corpus.py` + `store/vector_index.py`)

The corpus/discovery pillar rides the cognition spine. Its registries + record + space-keyed index live
in their own modules (`runtime/projections.py` K1/P1 · `runtime/corpus.py` D1 · `store/vector_index.py`
Group L) — the **Suite is the thin FACE** over them (the SUITE lane; the MCP tools + `/api` routes are the
SURFACE/BRIDGE lanes on top). **Reuse-don't-parallel:** every method here delegates to those modules; the
record gate, the dedup-on-read, and the cosine ranking are NOT reimplemented.

- **The SELECTS PROJECT the file-discovered PROJECTION registry (GROUP B — registry-is-truth, no
  hardcoding).** The Suite discovers `projections/` in `__init__` (`self.projection_registry =
  ProjectionRegistry().discover([self.projections_dir])`, mirroring `role_registry`). `cognition_info()`
  AUGMENTS its returned envelope with `projections` (= `projection_registry.as_records()` — the discovered
  lens set verbatim) + `spaces` (= `embeddable()` ids — the Group-L vector spaces); `available_inputs()`
  adds `projections` (the lens ids — the corpus discovery vocabulary) + `projection_spaces` (the
  `vec://<item>#space=<id>` read-addresses a corpus-reading role/rule can wire). **THE BAR (PART 4.3):**
  drop a `projections/<id>.py`, restart the bridge, and the lens appears in BOTH selects with NO code
  change (proven by use against the live `/api/cognition_info` + `/api/cognition/inputs`). **Seam (BAR2):**
  the proper long-term home for the projection serialization is a `projections=` kwarg on
  `contracts/cognition_info.build_cognition_info` (mirroring `roles`/`rules`/`edge_kinds`); until that
  contracts-lane edit lands, `cognition_info()` augments the dict in-lane (still the ONE `as_records()`
  source — never a hand-built list). The other 6 file-discovered registries
  (lifters/mark-types/ai-tics/relation-types/generation-policies/forms) instantiate + project the SAME way
  as they land.
- **The corpus record FACE (GROUP D):** `write_corpus_record(source_address, output, kind, lineage,
  model?, projection?, **extra)` → `corpus.write_record(self.store, ...)` — the LINEAGE GATE bites here
  (session/round/project REQUIRED, fail-loud `CorpusError`; a record without lineage is uncorroboratable
  cross-session). `read_corpus_record(address)` round-trips it back (honest None if never written).
  `list_corpus(project?)` / `find_corpus(project?, kind?, projection?, source_address?)` are the read-time
  PROJECTION over the `corpus.record` event log (dedup-on-read, the run-index sibling — no maintained
  index, no parallel DB).
- **`find_relations(item, near_space, far_space, k?, min_score?)` — THE INVERSION-FINDER (GROUP L2):** the
  cross-space "same principle, different subject" query — items NEAR `item` in `near_space` but NOT near it
  in `far_space` (near∩¬far). The query VECTOR is the item's OWN persisted per-space vector
  (`store.get_vector(store.space_address(item, space))`), so the query side needs **no live embedder** (the
  persisted vectors are enough — matters because :8001 is DOWN); the k-NN reuses
  `vector_index.query_index(space=)` (no cosine reimplemented). **The threshold pivot:** `query_index`
  returns EVERY indexed item ranked (including score≈0), so "in the far ranked list" ≠ "is a far-NEIGHBOUR"
  — a neighbour is `score ≥ min_score` (default 0.5; a per-projection `cluster_threshold` is a
  relation/generation POLICY — registry-projected once those registries land — so it is a tunable PARAM
  here, not a hardcoded global). FAIL LOUD: a missing anchor (item not embedded in a named space) raises;
  an unpopulated space is an honest empty difference (distinct from the missing-anchor raise).

## The SPACE-EMBED wiring (Cognition Engine GROUP L · L1/D2 · `runtime/cognition.py:embed_corpus_to_spaces` · the end-to-end SINK that fed `find_relations`)

`find_relations` reads the item's persisted per-space vector (`store.get_vector(store.space_address(item,
space))`) — but **nothing wrote those per-space vectors**: `run_role(op=embed)` PRODUCED a vector and
RETURNED it (`{vector, dim, model}`), yet the result was never `put_vector`'d into a SPACE, so the corpus's
embedded records never populated a queryable space and `find_relations` had nothing to read end-to-end (its
docstring even said the item "must be embedded in both spaces first (run the capture+embed pass)" — that
pass did not exist). **`embed_corpus_to_spaces(store, records, projections, *, embed_fn?, dim?, model?,
base_url?)` IS that pass** — the thin engine path the corpus capture uses to PERSIST embeddings space-keyed.

- **REUSE-DON'T-PARALLEL (NO 2nd vector path):** it is a pure delegate to STORE's existing space-keyed
  `vector_index.build_index(store, [{address: source_address, text}], space=<projection>)` — which already
  does embed→space-keyed `put_vector`. That path embeds via `client.complete_embeddings` (the EXACT plumbing
  `run_role(op=embed)` uses — the ONE embed path, not paralleled), keys by `store.space_address(item, space)`
  (the SAME key `find_relations` reads — lines up by construction), carries the explicit `space`/`source`
  fields, and gives the content-hash incremental diff + the one-round-trip batch + the degrade-with-warning
  FOR FREE. `embed_corpus_to_spaces` makes NO `put_vector` call itself (build_index owns persist). It groups
  records by projection (one build_index per space), validates each against `projection_registry.embeddable()`
  (registry-is-truth — a record naming a non-embeddable lens RAISES, never silently dropped). **Why a path,
  not inside `run_role(op=embed)`:** like generate's `run_role` returns the validated dict and the CALLER
  persists, embed returns the vector and the CAPTURE PATH persists — `run_role(op=embed)`'s return stays
  `{vector,dim,model}`, untouched.
- **EMBEDDER-DOWN (deliberate):** the batch path uses build_index's **degrade-with-warning** (a LOUD durable
  `warning` event, NO vectors written, `degraded=True`, no crash) — chosen knowingly so a multi-record/
  multi-space capture pass is not aborted whole by a transient :8001 outage; re-embed when up populates the
  space. (The HARD-raise fail-loud lives at the single-embed seam — `run_role(op=embed)`/`complete_embeddings`
  — for a deliberate one-shot embed; this is still fail-loud — never a silent `[]`, never a fabricated vector.)
- **THE FLOOR:** `put_vector` is a store WRITE — `embed_corpus_to_spaces` emits no `op.run`/resolve/approve/
  dispatch, is not on the MCP face, not in `RHM_VERBS`. Proven by `tests/space_embed_acceptance.py` (records
  → embed pass → vectors at `space_address` → `find_relations` near∩¬far end-to-end with per-space-distinct
  geometry teeth + fail-loud + embedder-down degrade + the floor).

**O3 — `finish_reason`/token-count is AVAILABLE at the `run_role` seam (`runtime/cognition.py`).** `run_role`
gained an additive `meta: dict | None = None` out-param: a caller that passes `meta={}` reads the
completion's `finish_reason` (+ `usage`) back via the transport's `_fill_meta` (the ladder path already used
this seam internally). `meta=None` (every current caller) is BYTE-IDENTICAL to before — no meta reaches the
transport, the request body is untouched, and the return is the same `model_dump()` (`run_swarm`/
`dry_run_role`/`run_cascade`/the MCP wrapper depend on that exact shape — `finish_reason` is an OUT-PARAM,
**never folded into the returned dict**). This makes the O3 value AVAILABLE; **PERSISTING it into the
agent-facing `op.run` run-record is the MCP wrapper's emit (`mcp_face/server.py:run_role` — a DIFFERENT
lane), flagged needs-coordination (not edited here).**

**THE FLOOR (C9.2) HOLDS:** every method here is a READ or a `corpus.record` telemetry write — NONE emits
`resolve`/`approve`/`dispatch`, NONE is in `RHM_VERBS` or on the MCP face (the SURFACE/BRIDGE lanes expose
them). Proven by `tests/suite_corpus_relations_acceptance.py` (the selects project the discovered set + the
drop-in bar + the corpus round-trip/gate + the near∩¬far inversion over seeded vectors + the floor); the
modules' own proofs are `tests/projections_acceptance.py` + `tests/corpus_acceptance.py`.

## The authoring backend (Concurrent Cognition C7.4/C7.5 · `runtime/authoring.py` + `runtime/suite.py` · the WRITE-side)

The cognition layer is now **authored from the surface**, not only viewed. The write-side **GENERALIZES
`propose_node`/`apply_node`** (the propose-not-apply governance path) to **roles + rules** — never a parallel
authoring system:

- **`runtime/authoring.py`** — the PURE half: the **ONE fields→source renderer** (`render_role_source`:
  operator field-set → a real `roles/<id>.py` module declaring `class <Name>Out(BaseModel)` + `ROLE = {…}`
  — C7.5's "dynamically define structured outputs"), the **field-type registry** (`FIELD_TYPES`, widened
  by Cognition Engine **B2** beyond flat scalars: the 6 scalars (`str·int·float·bool·list[str]·list[int]`,
  `kind:"scalar"`) PLUS the RICHER kinds `enum` (→ `Literal[...]`), `object` (→ a nested sub-`BaseModel`),
  `list[object]`/`list[dict]` (→ `list[<SubModel>]`), with the per-field MODIFIERS `optional` (→ `T | None`)
  and `default` — rendered by a **recursive renderer** (`_render_output_fields`/`_build_field_line`) that
  emits sub-models BEFORE their owners (define-before-use; no forward refs) and a conditional `Literal`
  import (only when an enum appears, so a flat-scalar role renders **byte-identical** — the additive law).
  Each row carries a `kind` discriminator + the `params` the richer kinds need (`enum→values`,
  `object/list[object]→fields`), surfaced via `field_types()` so the FE/agent learns the per-type shape
  from the registry (registry-is-truth). `output_schema` is ALREADY real Pydantic — B2 widens the AUTHORING
  grammar, NOT Pydantic, NOT a 2nd registry. An unknown type / malformed nested-or-enum spec fails loud —
  rule 8; proven by `tests/richer_types_acceptance.py`), and **THE GATE**
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

## The 6 registries WIRED into their consumers (Cognition Engine WIRING · `runtime/suite.py` + `runtime/cognition.py` + `mcp_face/server.py`)

The 6 file-discovered registries (719f82d — lifters/mark_types/generation_policies/relation_types/ai_tics/
forms) now EXIST **and are CONSUMED** (they were "existence only" before). All three wires REUSE the
existing patterns — NO parallel author path, NO 2nd anything:

- **generation_policies → `run_role` (NOTHING static).** `cognition.run_role` gains an OPT-IN `policy`
  param (default `None` = BYTE-IDENTICAL to before — no penalty, no meta, one call). When set, it reads the
  regime from the file-discovered `generation_policy_registry()` (registry-is-truth, fail-loud on an unknown
  id) and runs its **repetition_penalty LADDER as DATA**: start at `default_rep_penalty`, pass
  `repetition_penalty=<rung>` + read `finish_reason` back via the transport's `meta={}` out-param (O3); on
  `finish_reason=="length"` escalate to `next_rep_penalty`; **EXHAUST the ladder → fail-loud
  `degenerate-loop`** (the regime's own contract, never a silent give-up). The penalty VALUE is the registry
  rung, never a code constant. **NO live caller is flipped onto it** (run_swarm/dry_run_role/run_cascade stay
  `policy=None`) — item 1 asks only that `run_role` CAN read the ladder. **KNOWN/FLAGGED (coordinate-with-
  owner):** `fabric/transport.py` (out of this lane) copies only `temperature/max_tokens/top_p` into the
  request body (transport.py:92/122) — it does NOT yet forward `repetition_penalty`, so the penalty does not
  reach vLLM until that one-line passthrough lands. The ladder LOGIC + registry-sourced value + escalation +
  fail-loud exhaustion are real + proven (`tests/generation_policy_ladder_acceptance.py`); the penalty's
  EFFECT is gated on the transport edit. `diff_against_source` is read off the policy but the output-vs-source
  diff is NOT implemented this pass (flagged not-done, never silently ignored).

- **create_* (declarative-direct authoring — MIRROR create_skill/create_projection).** `Suite.create_mark_type`/
  `create_generation_policy`/`create_relation_type`/`create_ai_tic` author a `<name>/<id>.py` LIVE with NO
  approval, via the SHARED `Suite._write_registry_file` helper over the single-source `_CORPUS_REGISTRIES`
  table (render `<CONST> = {...}` → the registry's OWN `discover()` gate-in-tempdir → atomic write →
  `_commit_or_rollback` → rediscover). It is create_projection's mechanism FACTORED into one helper (the
  proper home that tool's BAR2 seam wished for) — reuse-don't-parallel, no copy-pasted bodies. The MCP tools
  (`create_mark_type`/…) are thin delegators. **SCOPED TO THE 4 PURE-DATA registries:** `lifter` (an `extract`
  CALLABLE) and `form` (a `match` CALLABLE) carry EXECUTABLE CODE in their row — pprint can't serialize a
  function + MCP-JSON can't carry one, so a data-create would always fail-loud at the gate. That is the
  FLOOR's "executable-code create stays GATED" line: lifter/form need a CODE-render+gate authoring contract
  (create_role-style render of a `def`, or the gated propose→apply), net-new + unspecified → **flagged for the
  operator, NOT invented here** (they stay LISTABLE in the selects + GOVERNED by the floor; only data-CREATE
  excludes them). `_write_registry_file` fail-louds defense-in-depth if ever handed a callable field.

- **marks suite-side API + MCP tool.** `Suite.mark(target, mark_type, **fields)`/`marks_for`/`marks_by_type`
  REUSE STORE-2's `append_mark`/`marks_for`/`marks_by_type` (the dumb `marks.jsonl` leaf). A mark targets a
  CLAIM or SPAN, carries a **registered** `mark_type` — the Suite owns the type GATE (fail-loud on an unknown
  type; `store.append_mark` stays dumb by design, its docstring says it won't import the registry). The `mark`/
  `marks_for`/`marks_by_type` MCP tools are thin delegators. Retrievable by BOTH keys (target AND mark_type).

- **The selects advertise the new registries.** `available_inputs()` adds `lifters`/`mark_types`/
  `generation_policies`/`relation_types`/`ai_tics`/`forms` (the discovery/capture vocabulary a corpus-reading
  role/rule/cascade composes with) — projected from the live registries, never a hardcoded list (drop a
  `<name>/<id>.py` → restart → it appears). **NOT touched:** `cognition_info()`'s projection of the 6
  registries (the live-registry VIEW) — that is the **owner's coordinate-with follow-up** (the contract owner
  is actively editing `contracts/cognition_info.py`; an in-lane augment there would collide). The exact shape
  the owner needs: `info["lifters"] = self.lifter_registry.as_records()`, `info["mark_types"] = …`, … mirroring
  the existing `info["projections"]`.

- **floor teeth:** `tests/cognition_governance_acceptance.py` enrolls all 6 new `runtime/<name>.py` in
  COG_SOURCES (the source-invariant scan) + adds all 6 to HOMES (5→11 drift homes). The floor scan is now 38
  checks (was 31); the 6 are floor-clean by construction (reads + DATA writes, never resolve/dispatch).

Proven by `tests/generation_policy_ladder_acceptance.py` (17) + `tests/registry_authoring_marks_acceptance.py`
(55) + the floor (38) + the MCP tool round-trip (live, isolated repo).

## The substrate WENT LIVE — the three call-sites (SUITE-3 WIRING · `runtime/suite.py` + `mcp_face/server.py`)

The corpus substrate was BUILT (the 6 registries' `as_records()`, `embed_corpus_to_spaces`, the `run_role`
`meta` out-param, `route_run_output`) but not all CALLED. SUITE-3 wired the call-sites that make it LIVE —
**reuse-don't-parallel** (call the existing fn, no second path):

- **`cognition_info()` PASSES the 6 registries + projections to `build_cognition_info`.** The contract
  serializer opened the uniform `projections=`/`lifters=`/`mark_types=`/`generation_policies=`/
  `relation_types=`/`ai_tics=`/`forms=` kwargs (each projecting the registry's OWN `as_records()` — rule 3,
  one source); the caller now passes `self.<x>_registry` for each, so `/api/cognition_info` + the MCP
  `cognition_info` tool show them **NON-EMPTY** (they were `[]` because the caller didn't pass them). The
  previous in-lane `info["projections"]`/`info["spaces"]` AUGMENT is now REDUNDANT and removed — the
  `projections=` kwarg produces both (the contract derives `spaces` from `projections.embeddable()`),
  collapsing two mechanisms into ONE.
- **CAPTURE-EMBED ONE-SOURCE — `Suite.capture_corpus` is the ONE capture+embed-on-write seam BOTH faces call.**
  *(Was: only the MCP `capture` tool embedded-on-write; the bridge `/api/cognition/corpus` route ONLY wrote
  the record and NEVER embedded — so capturing via /api SILENTLY did not populate the space, and
  `find_relations` stayed empty over it, a no-silent-failure violation. The FINAL lane closed it.)* The
  write+embed is HOISTED into **`Suite.capture_corpus(records, *, project, session, round, embed_fn=?)`** —
  it writes each lineage-gated `write_corpus_record` FIRST (the **sequencing gate**: session/round/project ride
  IN the record BEFORE the first embed), derives the embed-text via **`Suite._embed_text`** (MOVED here from
  `mcp_face/server.py` so it travels WITH the shared seam — deterministic stringification, so a re-captured
  record is a content-hash no-op), and embeds the embeddable-projection records via
  `cognition.embed_corpus_to_spaces` (the REUSE delegate to `vector_index.build_index(space=)` — NO second
  vector path; its FIRST live caller). **BOTH faces CALL it:** the MCP `capture` tool owns only the FAN
  (`run_items` over units) then hands the per-unit records to `capture_corpus`; the bridge `/api/cognition/corpus`
  POST arm assembles its single-record (or `records:[…]` batch) body into `capture_corpus`. So both populate
  the space IDENTICALLY; neither silently no-ops. **FAIL-LOUD (the WHOLE POINT — registry-is-truth +
  no-silent-fallback):** `capture_corpus` does NOT pre-filter the embeddable check — it lets
  `embed_corpus_to_spaces` OWN it (the embeddable decision is `projection_registry.embeddable()`), so a record
  naming a projection that is NOT an embeddable space RAISES (→ a 400 on the bridge). A record with NO
  projection is legitimately capture-only (`embedded=None`, no error — distinct from "asked for a non-embeddable
  space", which fails loud). A DOWN embedder → `build_index`'s sanctioned LOUD degrade-with-warning
  (`degraded=True`, no vectors, no crash). The result rides back as `embedded` on the return (and on `capture`'s
  return). Proven by `tests/capture_one_source_acceptance.py` (both faces populate identically; the fail-loud;
  the floor) + `tests/suite3_wiring_acceptance.py` §2/§5. **needs-tim:** a LIVE `:8001` embed (the embedder is
  DOWN — the capture→embed→space→`find_relations` code path is proven on a stub).
- **O3 PERSISTED — the MCP `run_role` wrapper rides `finish_reason` onto the `op.run` record.** The wrapper
  passes `meta={}` into `cognition.run_role` (the OUT-PARAM seam — the engine's return shape is UNCHANGED,
  `finish_reason` never folds into it) and threads `finish_reason` (+ `usage` if present) into the
  `emit_run_record` `op.run` index event; `_project_run_event` carries `finish_reason` onto the discovered
  row (present-only — None when absent, never fabricated), so `find_runs` surfaces WHY a run stopped
  (`stop`/`length`/tool-call) — introspective-data-building, the run self-instruments.

**E4 (chain save/re-run + output-destination) is COVERED** by the saved cascade (`save_cascade`/`run_cascade`,
GROUP N — chain SAVE + RE-RUN) + `route_run_output` (the run-output DESTINATION param — route a DIRECT run's
output to address/lane/surface via `rules.route` over `DESTINATION_KINDS`, reuse, no second router) —
verified by use, not rebuilt. **THE FLOOR HOLDS:** every wired call-site is computation/telemetry — `capture`
is a `corpus.record`/`put_vector`/`op.run` write, `cognition_info` is a pure read, `run_role` emits `op.run`
— NONE emits resolve/approve/dispatch, NONE launches `claude -p`. Proven by `tests/suite3_wiring_acceptance.py`
(47) + the floor (`cognition_governance_acceptance` 38) + no-regression (`run_discovery` 22, `mcp_engine` 35,
`cognition_info_registries` 45, `cognition_info` 82, `drift` 5, `route_run_output`, `cascade` 25,
`space_embed` 27). **needs-tim:** a LIVE `:8001` embed (the embedder is DOWN — the capture→embed→space code
path is proven on a stub; a real BGE-M3 capture populating the space is the embedder-up follow-up). **B-fix
CLOSED — `api_verbs` is now DERIVED from `bridge.BRIDGE_ROUTES`** (the FINAL lane): `runtime/bridge.py` now
declares **`BRIDGE_ROUTES`** — a flat tuple, the SINGLE SOURCE of the bridge route table (every `path ==` /
`self.path ==` literal the `do_GET`/`do_POST` dispatcher handles, listed ONCE). `capabilities()['api_verbs']`
projects the `/api/*` subset of it (`Suite._api_verbs` — a projection by the INTRINSIC path-prefix, NOT a
hand-maintained classification, so adding an `/api/` route makes it appear with no second list). The
circular-import constraint (suite.py can't import bridge.py at module load — bridge imports Suite) is handled
by a LAZY import inside `_api_verbs` (both modules are loaded by call-time). The TEETH that make this the
single source rather than a relabeled third copy: **`tests/bridge_routes_acceptance.py`** greps the dispatcher's
own route literals out of `bridge.py` and fail-louds if `BRIDGE_ROUTES` drifts from them BOTH directions
(dispatched-but-unlisted OR listed-but-undispatched) — so a route can't be added/removed without the matching
`BRIDGE_ROUTES` edit. The dispatch `if/elif` chain is UNCHANGED (de-hardcoding the projection, not rewriting
the dispatcher — a high-regression refactor avoided deliberately). The old curated 22-item literal is GONE; the
preamble label softened to "the api routes" since it now includes POST verbs (a fuller true list — POLR working,
not a regression). (`PROTECTED_ROLES` — the other flagged B-fix — was already de-hardcoded: derived from
`cognition.SPIKE_ROLES` ∪ `_SUITE_OWNED_PROTECTED_ROLES`.)

## The cognition-engine HUMAN-FACE routes (Cognition Engine LANE-BRIDGE · `runtime/bridge.py` · G2)

The HUMAN face (the FE/#55) reaches the cognition engine over `/api/cognition/*`, **reflects-never-owns**:
the bridge serves what the operator sees + does, the backend is truth. Every route REUSES the SAME engine
the swarm + the MCP face use — **reuse-don't-parallel, NO second engine**:

- **RUN (computation):** `POST /api/cognition/{run_role,run_items,run_reduce,embed}` fire the ONE engine
  (`runtime.cognition.run_role`/`run_items`/`run_reduce`/`resolve_address`) via the module-level `cog_run_role`/
  `cog_run_items`/`cog_run_reduce` GLUE in `bridge.py`. The OP rides the ROLE (`role.op` — generate|embed),
  never a caller kwarg (engine dispatches on `role.op`; `/api/cognition/embed` fires an embed-op role,
  default `embed`). A run PERSISTS to `run://<turn>/<role>[/<i>]` (turn-id `fe-…`) and emits the ONE
  `op.run` RUN-INDEX record (#54) so an FE-initiated run is DISCOVERABLE by `list_runs`/`find_runs`
  identically to an MCP-initiated one. **THE FLOOR (C9.2):** a run produces a `run://` output + `op.run`
  telemetry — it emits NO resolve/approve/dispatch; the `claude -p` wire stays OFF this seam.
- **READ (the human-face reads):** `GET /api/cognition/{list_runs,find_runs,find_relations}` +
  `GET /api/cognition/corpus` (`?address=` reads ONE record, else the filtered/full corpus projection) —
  thin delegations to `Suite.list_runs`/`find_runs`/`find_relations`/`read_corpus_record`/`find_corpus`/
  `list_corpus` (the SAME methods the MCP tools call). `POST /api/cognition/corpus` is the CAPTURE write
  (`Suite.write_corpus_record` — the lineage gate bites: session/round/project REQUIRED, fail-loud). This is
  `/api/cognition/corpus`, **NOT `/api/corpus`** (that is the mockup-gallery index — a name-collision,
  verified preserved).
- **DIRECT create (declarative-direct, #58 — no approval):** `POST /api/cognition/{create_role,create_skill,
  create_context}` reuse the SAME `Suite.create_*` (render→correctness-gate→write→git-commit→rediscover);
  a malformed spec is REFUSED fail-loud, never written. **node-type / arbitrary-code create stays GATED**
  (operator-only — `propose_*` + `/api/apply`/`/api/resolve`), NOT on these run-routes.

**THE SEAM (BAR2 — surfaced honestly, not silently shipped):** the run_role/items/reduce GLUE (turn-id +
input-address resolution + persist + the `op.run` emit) is **mirrored byte-for-byte** from
`mcp_face/server.py` (same `ENGINE_RUN_OPS` strings, same `addresses=[address]`, same `run_op`) because the
engine deliberately leaves persist+index to the caller, and extracting a shared helper would touch
`suite.py`/`mcp_face` (out of the BRIDGE lane). **The two copies MUST stay identical** — drift on the
op-string / `addresses=` silently breaks #54 discovery for one face. **The long-term home** is one shared
`Suite.run_role/run_items/run_reduce` (or a `runtime/cognition_face.py`) both faces call; until that
suite.py/mcp_face edit lands, the mirror is the reuse. Proven BY USE (the run quartet over the resident 4B,
the run-index discovery of `fe-` runs, the corpus round-trip + lineage-gate, the near∩¬far inversion over
seeded space-vectors, `/api/corpus` gallery still 200, fail-loud on bad-op/missing-anchor/missing-lineage).
**NOT proven (needs-tim):** a successful `/api/cognition/embed` + a `run_reduce(mode='cluster')` (the local
embedder at :8001 is DOWN — both fail loud correctly; a real embed needs the embedder resident, a GPU
window). **NOW UNBLOCKED (the methods landed):** the declarative-direct create_* Suite + MCP methods now
EXIST — `create_projection` (cc9a749) + `create_mark_type`/`create_generation_policy`/`create_relation_type`/
`create_ai_tic` (WIRING, via the shared `Suite._write_registry_file`; `create_lifter`/`create_form` stay
GATED code-authoring — see the WIRING section above). So adding the bridge `POST /api/cognition/create_*`
routes for them is the now-unblocked BRIDGE-lane follow-up (no longer "inventing" — the delegate methods
exist), out of this WIRING lane's edit set (bridge.py).

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
