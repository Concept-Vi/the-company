# Area 2 — The detector layer, and how detectors become CONTRIBUTORS to one model

> Companion to `ANCHOR.md`. My area: the existing self-description + detector layer
> (`doc_drift`, `refresh_self_description`, the three new gates, the 118 `*_acceptance.py` corpus),
> and the concrete path from *point-detectors that forget* to *contributors that write into one
> unified, persisted, typed, addressed, dispositioned finding-model*.
>
> Evidence marking, per Tim's template:
> **Verified** = I executed it this session (live numbers). **Observed** = read in the code (file:line).
> **Inferred** = pattern-match, labelled as such. **[my idea]** = design proposal, not yet in the code.

---

## 0 · The one-paragraph thesis (read this first)

The unification the anchor wants is **not** net-new architecture. It is **`reachability()`'s
own internal shape, generalized across every detector.** `reachability()` already splits its
findings three ways — `documented` / `new_orphans` / `stale` (suite.py:7080-7082) — which is
*exactly* a per-detector reconcile loop: **known / new / resolved.** And `_ORPHAN_ROUTES`'s tags
(`to_wire` / `to_build_ui` / `voice_owned` / `backend_only`, suite.py:7017-7054) are **the
disposition vocabulary in embryo.** So the whole "turn detectors into contributors" thesis reduces
to one move: *take the documented/new/stale reconcile that reachability does in-line, carry the
disposition on the `known` set, and make every detector do it against one persisted finding-store
instead of recomputing-and-forgetting.* Everything else in this file is grounding that, and being
honest about where it gets hard.

---

## 1 · What the self-description layer ACTUALLY is right now (Observed)

The system already maintains a **factual self-model that regenerates from the registry**. This is
the proof-of-concept the anchor leans on, and it is real:

- **`capabilities()`** (suite.py:683-767) — the single self-model projection. One dict of *what
  exists*: `node_types`, `models`, `modes`, `mode_directives`, `mode_registry`, `rhm_verbs`,
  `node_states`, `panels`, `stt`, `cognition`, `composition_config`, `api_verbs`. The docstring
  calls it "the reflective fold." Every authoring prompt and every registered select reads from it,
  so *the registry is the easy path and nothing is guessed* (the PoLR law).
- **`refresh_self_description()`** (suite.py:823-839) — regenerates the auto-maintained `<!--REGISTRY-->`
  block of `MAP.md` and the `<!--SUITES-->` block of `STATE.md` **from `capabilities()`**. Called on
  every apply/revert (and inside `_make_live_and_refresh`, suite.py:7091-7109, which `rediscover()`s
  then refreshes *before* the drift check so a new capability reads green).
- **`doc_drift()`** (suite.py:855-869) — the inverse: what `capabilities()` has that the maintained
  doc-block does *not* yet reflect. Returns `{map_node_types, map_rhm_verbs, map_modes, map_panels,
  state_missing_suites}` — each a list of *names present in reality but absent from the written
  self-description*. Checked **inside the marker block** (`_doc_block`, suite.py:844-853, lowercased),
  not whole-file, so prose substrings can't false-pass (red-team F3, noted in-code).
- **`drift_acceptance.py`** turns `doc_drift()` into a fail-loud gate: every node-type, verb, mode,
  panel, and suite must be reflected, or the suite fails.

**Verified live this run:** `doc_drift()` returns all-empty
(`{"map_node_types": [], "map_rhm_verbs": [], "map_modes": [], "map_panels": [], "state_missing_suites": []}`)
— the self-description is currently in sync.

**The key observation for this area:** `doc_drift` is *already a contributor-shaped detector.* It
reads two views (`capabilities()` = should-be, the doc-block = is-written), computes a typed
set-difference, and each element of that difference is a finding (`{kind: stale-self-description,
at: MAP.md#REGISTRY, missing: <name>}`). It just emits the difference as a return value that the
test asserts on and throws away. **That throw-away is the entire gap the anchor names.**

---

## 2 · The three gates, by their real emitted shapes (Observed + Verified)

Each gate returns an **ad-hoc dict**. They share a deep structure but speak different field-names —
which is precisely why they can't be queried together today.

### 2.1 `suite_health()` (suite.py:6969-7006) — the all-green gate
```
{ green:    [suite, ...],
  needs_dep:[suite, ...],          # documented live-dep skip (NOT a red)
  red:      [(suite, detail), ...],
  all_green: bool,
  counts:   {green, needs_dep, red, total} }
```
Runs every `*_acceptance` suite **standalone** as a fail-loud subprocess (`_full_suite_runner`,
suite.py:6957-6967), classifying green / needs-live-dep / red. The needs-dep excuse is *registry-bounded*:
only `_LIVE_DEP_SUITES` (suite.py:6944-6949) members, and only when output shows a `_DOWN_SIGNALS`
(suite.py:6953-6955) string — so neither a false alarm nor a masked real red gets through. This is a
**slow** detector (spawns ~115 subprocesses); the docstring designates it pre-merge/pre-deploy/periodic,
not per-build. *(I did not run it live — it's expensive — but the shape is Observed.)*

### 2.2 `reachability()` (suite.py:7056-7089) — the built-but-unwired gate
```
{ wired:       [route, ...],
  documented:  [(route, tag, note), ...],   # catalogued orphans = the BACKLOG
  new_orphans: [route, ...],                # NEW disconnection → gate FAILS
  stale:       [route, ...],                # catalogued but now wired/removed → self-correct
  all_accounted: bool,
  backlog:     {to_build_ui:[...], to_wire:[...], voice_owned:[...], backend_only:[...]},
  counts:      {routes, wired, orphan, new, stale} }
```
Extracts every `"/api/..."` literal from `bridge.py`, checks each for a caller in `canvas/app/src`
or `tests/`, and reconciles against `_ORPHAN_ROUTES`.

**Verified live this run:** `{routes: 112, wired: 80, orphan: 32, new: 0, stale: 0}`; backlog =
`to_build_ui: 12, to_wire: 9, voice_owned: 10, backend_only: 1`. So *right now* 32/112 routes are
orphans, all catalogued, none new, none stale. The gate is green because every orphan is *accounted
for* — which is the disposition idea already working: an orphan is not a defect, it is a finding with
a disposition.

### 2.3 `doc_drift()` — covered in §1.

### 2.4 The shared structure they don't yet share (Inferred)
Every one of the three is: **`compare(should_be, actual) → typed difference, reconciled against a
known-set, classified`.**
- `should_be`/`actual`: `capabilities()` vs doc-block · `bridge.py` routes vs FE/test callers ·
  declared suites vs standalone-pass.
- `known-set`: the catalogue (`_ORPHAN_ROUTES`) for reachability; *implicit/none* for the other two.
- `classification`: documented/new/stale · green/needs-dep/red · present/missing.

They differ only in **field names and whether a known-set exists.** Unify those two and they are one
machine. **This is the convergence the anchor is reaching for, and it is sitting in the code already.**

---

## 3 · The finding-schema → real-primitive mapping (the core of this file)

The anchor's finding object —
`{kind, at, state, owner, disposition, since, evidence}` — does **not** need a new store. Every field
maps onto a primitive that already exists in this codebase. This is the "build-on-not-beside" proof.

| Finding field | Already-existing primitive | Evidence |
|---|---|---|
| **typed** (`kind`) | `NODE_STATES` registry + the **node-type declaration shape** (drop a file with `KIND`, `PORTS_IN`, `CONFIG`, a `run()`) | `nodes/wordcount.py`; `NODE_STATES` referenced suite.py:725; registry `register_module` reads declared constants registry.py:75-90 |
| **addressed** (`at`) | `append_annotation` is **already address-keyed** — *"the address IS the key"* | `store/fs_store.py:534` (`append_annotation`), `:550` (`annotations_for`, filters by `address` field) |
| **persisted** (`since`, durability) | `append_event` (`op.run` run-records) + `annotations.jsonl`, both append-only | `store/fs_store.py:426` (`append_event`), `:534`; `_emit` carries arbitrary `**meta` incl. `address=` (suite.py:497-506) |
| **dispositioned + lifecycle** (`disposition`, `state`, `owner`) | the **Inbox SEPARATE-status-lane** | `runtime/governance.py` — `Inbox.surface` (:95), `REVIEW_STATUSES` (:151), `set_status`/`status` lane (:134-135, :163), `resolve` (:184), `is_approved` (:201) |
| **evidence** | the detector's own output string (reachability's note, suite_health's `detail` tail) | reachability `documented` tuples (suite.py:7080); suite_health `red` `(suite, detail)` (suite.py:7002) |
| **disposition vocabulary** | `_ORPHAN_ROUTES` tags | suite.py:7017-7054 (`to_wire`/`to_build_ui`/`voice_owned`/`backend_only`) |

**So the finding-model is a lens over three existing stores** — addressed annotations (locus), the
event log (history/durability), and the inbox-style status lane (mutable disposition) — projected
through one new typed view. Not a parallel universe. That is exactly the anchor's §4 bet, and it
holds against the real code.

---

## 4 · The one load-bearing design tension — and the code already solved it

**Tension:** a finding needs a **mutable** disposition (`pending → to-wire → resolved`, or
`pending → by-design`). But the event log and `annotations.jsonl` are **append-only immutable logs**
(the store constitution; noted at fs_store.py:572-585: pins live in a *separate* `pins.jsonl` rather
than mutating the annotation record, precisely because the annotation store is append-only).

You cannot mutate a finding's disposition by editing its event. So which way do findings persist?

**The Inbox already answers this exact question (Observed, governance.py).** When the consent gate
needed a *mutable* lifecycle on top of an *immutable* substrate, it did NOT overload the append-only
record. It introduced a **separate `status` lane** advanced under a locked `get → mutate → save`,
explicitly *never touching* the operator-only `resolved` field (governance.py:134-135, comment:
*"a SEPARATE lifecycle field… NEVER overload `resolved`"*; `REVIEW_STATUSES =
("inbox","presented","responded","resolved","requeue","implemented")` at :151; `set_status`
mutates only `status` under the store lock at :163-178).

**[my idea, but grounded]** Findings should persist the *same way the inbox does it*:
- **Detection** is append-only: each detector run emits its raw findings as `op.run`-style events
  (introspective-data-building — `emit_run_record`, suite.py:508-518 — pointed at *integrity* as the
  op). This is the immutable trace: *"at tick T, detector D saw finding F."* Cheap, lenient, never
  breaks the run it records.
- **Disposition** is a mutable lane: the *current* finding-record (keyed by finding-id, see §5) carries
  a `disposition` field advanced under a lock via the inbox's exact `get→mutate→save` discipline. The
  consequential dispositions (auto-finish dispatch) route through the **real consent gate** that
  already exists (`Inbox.surface` with `resolved=None` → operator `resolve` → `is_approved`).

This means: **the burn-down history is the append-only event trace; the live model is the
disposition-lane projection over the current finding-set.** Two existing patterns, composed. The
anchor's §9 question *"the burn-down history IS institutional memory… queryable: when did this
connect, what migration left this, who dispositioned that as by-design and why"* falls straight out
of the append-only trace — `run_stats`-style rollups (suite.py:520-552) over finding-events.

---

## 5 · Identity & dedup — the thing that stops thrash (the anchor's §5 open risk)

A detector re-runs every tick. Without a **stable finding-id**, each run re-emits "the same"
unwired-route as a *new* finding, the model floods, and the burn-down never converges — which is
exactly the thrash the anchor flags as the convergence risk.

**Observed:** `reachability()` already dedups by the **route literal** — it reconciles this-run's
orphans against `_ORPHAN_ROUTES` keyed by the route string (suite.py:7080-7082). So the same orphan
across two runs is the *same* catalogue entry, not two. That is dedup-by-natural-key, working today.

**[my idea]** Generalize it: every finding has a stable key = **`(kind, address)`** (+ a discriminator
where one address can host several findings of a kind). A detector run is an **upsert against that
key**, producing exactly the three-way reconcile reachability already does:
- key seen before, still failing → **known** (carry its disposition forward).
- key new this run → **new** (default disposition `pending`, surface it).
- key in the model but NOT in this run → **resolved** (it connected / was removed — auto-close,
  recording *when* in the trace).

`new_orphans` / `documented` / `stale` → `new` / `known` / `resolved`. **This is reachability's
reconcile, lifted to be the universal detector contract.** Convergence then has a precise definition
(anchor §5): the model converges iff, over a window, |new| − |resolved| ≤ 0 with no `pending`
"finish" findings left — *net burn-down*, computable from the trace, with thrash visible as a finding
that oscillates known↔resolved (a meta-finding the model can raise about itself — the recursive
watch the anchor §9 muses on).

---

## 6 · Declared detectors, not hand-coded gates (more types, not more tools)

The anchor (§9) and my brief ask: *how should detectors be **declared** rather than hand-coded?*
The answer is **the node-type discovery mechanism, reused.**

**Observed — how a node-type is declared today:** drop a `.py` file in `nodes/` declaring module-level
constants and a function. `registry.discover()` (registry.py:55-66) walks the dir, skips `_`-prefixed
files, loads any module with a `run()` attribute, and `register_module` (registry.py:75-90) reads its
declared `KIND`, `PORTS_IN`, `PORTS_OUT`, `CONFIG`, `OUTPUT_SCHEMA`, `VERSION` into a `NodeType`.
`rediscover()` (registry.py:68-73) clears and re-walks so a removed file un-registers. **A capability
is added by declaration + discovery, never by editing a central switch.** `wordcount.py` is the whole
contract: 8 lines, all declaration.

**[my idea] — a detector declared the identical way.** A `detectors/` dir; each file declares:
```python
# detectors/unwired_route.py
KIND        = "unwired-route"          # the finding type (→ NODE_STATES-style registry entry)
READS       = ("code://bridge.py", "code://canvas/app/src", "code://tests")   # what graph it reads
DISPOSITIONS= ("to_wire", "to_build_ui", "voice_owned", "backend_only")        # this kind's vocab
def address(finding): ...               # map a raw finding → its ui://|code://|run:// coordinate
def detect(views) -> list[finding]: ... # the predicate; returns typed findings
```
A `DetectorRegistry.discover(["detectors"])` — byte-for-byte the node pattern — turns "add a new
class of integrity check" into "drop a declared file," not "hand-code another bespoke gate method on
`Suite`." The existing three gates become the first three *migrated* detectors, their reconcile/
classify logic moved into the shared upsert engine (§5), their bespoke logic shrinking to a `detect()`
predicate. `doc_drift` is the cleanest first migration — it's already pure `compare(should_be, actual)`.
**This is "more types, not more tools" applied to coherence itself.**

---

## 7 · Latent detectors — tiered honestly by difficulty (the "but actually" gold)

The anchor lists candidate detectors flat. They are **not** equally feasible. Tiering them is the
honest contribution, and it routes the make-or-break rigor to Area C.

### Tier 1 — cheap, trustworthy now (literal / registry set-difference)
These compare two *declared* views; no call-graph needed; false-positive rate near zero.
- **stale-self-description** — *already built* (`doc_drift`, §1). The template for the tier.
- **new-orphan-route** — *already built* (`reachability`, §2.2).
- **registry-vs-live mismatch** — `capabilities()` (the running registry) vs `registry.discover()`
  over the disk (`nodes/`). A node-type present on disk but not live, or live but file-gone, is a
  clean set-difference. The machinery exists: `rediscover()` already does the disk walk
  (registry.py:68); the live set is `self.registry.types`. *(Inferred feasible; not yet a detector.)*
- **stale-catalogue** — *already built* (reachability's `stale` set, suite.py:7082): a catalogued
  orphan that is now wired/removed self-corrects.
- **suite-not-indexed** — *already built* (`doc_drift.state_missing_suites`).

### Tier 2 — hard; NO literal to grep; needs a real call/import graph
These are the anchor's hard-part #1, and the current gates **admit their own weakness here**:
`reachability`'s docstring (suite.py:7063-7065) says *"Heuristic (literal-string match — a route
called only via a computed path reads as orphan)."* The session-history false positives the anchor §7
cites came from exactly this.
- **capability-with-no-consumer** — a public method/route with no caller. Grep finds *string* callers
  only; a method reached via `getattr`, a dispatch table, or a computed route is a false orphan.
  Needs **AST-level call-graph for Python** + import-resolution for the FE.
- **FE-component-with-no-mount** — a `.tsx` region component (18 in `canvas/app/src/regions/`; 28
  `.tsx` across all of `canvas/app/src/`) that nothing imports/renders. Grep for the component name catches direct JSX use but misses
  lazy/dynamic mounts and registry-driven rendering. Needs an **import graph of the FE.**
- **half-migration** — mechanism X partly replaced by Y (the feedback JSONL→annotation-store case in
  anchor §1, where the *status lifecycle* was the dropped piece). There is no single literal that says
  "this migration is half-done." Detecting it means modelling *both* the old and new mechanism and
  noticing a record-shape that has neither's full lifecycle — likely AST + schema-diff, the hardest
  Tier-2.

**Hand-off:** Tier 2 is where the model's *trustworthiness for an autonomous loop* is won or lost.
Grep does not cover it. This is Area C's make-or-break and I am explicitly NOT claiming the detector
layer can do it cheaply. The honest split: Tier 1 detectors can ship trustworthy on string/registry
compares **today**; Tier 2 is gated on an accurate connection graph.

### Tier 3 — hardest; no clean machine signal at all
- **suite-covers-capability (coverage gaps)** — "does *some* acceptance suite actually exercise
  capability C?" There is no literal binding a suite to a capability (suites are free Python that
  import and assert). Mapping coverage means either (a) a *declared* `COVERS = [...]` constant on each
  suite — i.e. extend the declaration pattern of §6 to suites, which is plausible and cheap to author
  but relies on humans/agents declaring honestly; or (b) genuine coverage instrumentation (tracing
  which capabilities a suite's run touches), which is heavy. **I do not believe this is a spec-able
  detector yet** — say so plainly rather than pretend. The declared-`COVERS` route (a) is the realistic
  first cut and fits the more-types-not-more-tools grain.

---

## 8 · Where the gates are fragile *as detectors* (told straight)

- **String extraction is brittle both ways.** `reachability` regexes `"/api/..."` literals from
  `bridge.py` (suite.py:7068) and string-matches them in FE/tests (suite.py:7079). A route built via
  string-concatenation, or called from a path the glob doesn't read, mis-classifies. The gate already
  excludes the meta-gate files (suite.py:7071-7076) because their *docstrings mention routes as
  examples* — a doc mention falsely "wired" an orphan. That patch is evidence the heuristic is fragile
  enough to need hand-exclusions; an AST approach wouldn't need them.
- **`_ORPHAN_ROUTES` is a hand-kept dict in source.** It IS the embryonic disposition store — but it
  lives as a Python literal edited by hand (suite.py:7017). To become a real disposition lane it must
  move to the persisted, lockable store (§4), or every disposition change is a code commit. That move
  is the single most concrete "turn the gate into a contributor" step.
- **`suite_health` is O(suites) subprocesses.** ~115 spawns. Fine as a periodic standing gate; wrong
  as a per-tick detector. The cadence question (anchor §7.6) is real: detectors must declare their
  cost class. Tier-1 compares are near-free (run every tick); `suite_health` is expensive (run
  pre-merge). **[my idea]** the declared-detector schema (§6) should carry a `COST`/`CADENCE` field so
  the loop schedules cheap detectors hot and expensive ones on a gate — same as `_LIVE_DEP_SUITES`
  declares external deps.
- **The needs-dep excuse is signal-string based** (`_DOWN_SIGNALS`, suite.py:6953). It's well-guarded
  (registry-bounded, only on documented suites) but it is still substring-matching on output — a suite
  whose real bug happens to print "connection refused" could be mis-excused. Low risk, but it is the
  same class of fragility as the route-string matching: *the gates lean on strings where they'd want
  structure.*

---

## 9 · How this composes with the rest of the anchor (connections, not a recap)

- **The cognition live-model convergence (anchor §9) is real and specific.** `emit_run_record`
  (suite.py:508) → `op.run` events → `run_stats` rollups (suite.py:520-552) is *the same emit→trace→
  rollup loop* the cognition stream uses for wave telemetry (cognition.py:502, 531; activation.py
  rollups :250-269). A coherence finding-trace is **another `op` in the same introspective-data-building
  substrate** — `emit_run_record("coherence.detect", ms, kind=..., address=..., found=...)`. The
  cognition view and a coherence view would render the *same kind of thing* (a live, addressed,
  reflects-never-owns rollup), which is why the anchor's "one substrate, two lenses" instinct is sound:
  *how it thinks* and *how whole it is* are both rollups over the one event log.
- **The autonomous loop's worklist (anchor §5)** = `findings where disposition == to_wire|to_build_ui
  and state == pending`, ordered. The loop already exists (`runtime/implement.py` + the reviewer gate —
  *anchor-sourced §8; not read this session*); the finding-model is the *queryable worklist* it lacks. The reviewer-gate's keep/revert verdict
  (suite.py `resolve_verdicts_since`:6591) becomes the signal that re-runs the detectors and resolves
  (or re-opens) the finding.
- **Recursion (anchor §9):** the model can watch the coherence of its own mechanisms — a detector that
  oscillates known↔resolved is a thrash meta-finding (§5); a disposition lane with a growing
  `backend_only`/`by-design` pile that hides real gaps is a "disposition-dumping-ground" meta-finding
  (anchor §7.2). Both are just more declared detectors over the finding-trace.

---

## 10 · The concrete first-cut build order (what I'd actually do — [my idea])

Smallest steps that each leave the system more coherent, every one grounded in an existing primitive:

1. **A persisted finding-store as a lens over existing stores** — finding-events on the append-only
   log (`emit_run_record`, "coherence.detect") + a disposition lane copied from `Inbox.advance_review`
   (governance.py:164). No new storage tech. (Resolves anchor hard-part #3.)
2. **Migrate `_ORPHAN_ROUTES` out of source into that disposition lane** — the most concrete
   gate→contributor conversion; dispositioning a route stops being a code commit.
3. **The universal reconcile engine** — `(kind, address)` upsert → known/new/resolved (§5),
   generalizing reachability's documented/new/stale. Net-burn-down computable.
4. **Declare the three gates as detectors** (§6); `doc_drift` first (cleanest), then `reachability`,
   then `suite_health` (with a declared `CADENCE`).
5. **Add Tier-1 detectors by declaration** — registry-vs-live, suite-not-indexed already partly there.
6. **Gate Tier-2 on Area C's connection graph** — do NOT ship capability-with-no-consumer or
   FE-no-mount on grep; they corrode trust (anchor §7.1). Declare their `kind` and `address` mapper now,
   wire their `detect()` to the AST graph when Area C delivers it.
7. **Render as a lens, not a new app** — a `company coherence` CLI over the finding-store first; the
   full RHM-capable surface (anchor §6) as the cognition-view sibling, reusing `address_help`/
   `up_translate` over a finding.

---

## 11 · Net

The detector layer is not three tests that need promoting to a model — it is **a model that already
exists, fragmented across three return-shapes that forget themselves, sitting on top of every
primitive the unified version needs.** `reachability` already does the reconcile; `_ORPHAN_ROUTES`
already does dispositions; the Inbox already solved mutable-state-on-immutable-substrate; the registry
already does declared-discovery; `emit_run_record` already does the persisted trace. The work is
**naming and composing** what's here — generalize reachability's three-way reconcile, move the
disposition dict into the inbox-pattern lane, and declare detectors like node-types — **not building
beside it.** The single hardest unsolved piece is squarely Area C's: Tier-2 detection needs a real
connection graph, and the current gates honestly admit their string-heuristic can't be trusted there.
Ship Tier-1 trustworthy now; gate Tier-2 on the graph; never let grep findings drive the autonomous
loop, because a false "unwired" is the one failure that erodes the whole instrument.
