# Area 1 — The Addressable Substrate the Coherence Model Would Live On

> Companion to `../ANCHOR.md`. My allocated area: the *ground* a Coherence finding stands on —
> the address system, the registry (declared truth), `capabilities()` as self-model, the typed
> structured-record patterns, and the event log + store. The anchor's question for me:
> **IF findings are typed+addressed records that are "just another lens over the existing
> substrate," what does that concretely look like ON these mechanisms — what's perfectly suited,
> what's missing, what must be added, and where does a finding actually get stored + addressed?**
>
> Evidence is marked **[OBS]** (observed in code, `file:line`), **[INF]** (inferred from the
> code's shape, not executed), **[IDEA]** (my own proposal). I deliberately mined the *almost* —
> where the existing machinery does NOT fit is more load-bearing than where it does.

---

## 0 · The headline (read this first)

The substrate is **more ready than the anchor claims in one dimension and less ready in another**,
and both matter:

- **More ready:** there is a *canonical, contract-level address grammar* with an explicit, named
  extension precedent (`ui://` and `code://` were both added to `SCHEMES` purely additively); an
  **AST-level code-dependency graph already exists** (`design/_system/codeedges.py`, stdlib `ast`,
  precise resolution, bounded reach); and the **disposition lifecycle is already built and battle-
  tested** in the surfaced/inbox system (`status` vocabulary + operator `resolved` + `reason` +
  consent-gate routing). The "typed addressed record with a state and a disposition that persists"
  the anchor wants is **not hypothetical — it ships, today, as a surfaced item.**

- **Less ready:** the address registry is **`ui://`-only (71 entries) and the anchor's node-set is
  far broader** than what is addressable now (suites, migrations, voice engines, mockups have no
  address). The embryonic disposition system (`_ORPHAN_ROUTES`) is a **hardcoded Python dict
  literal, not a persisted addressed record** — right *shape*, wrong *form*. And the single most
  important constraint: **a finding cannot just BE a surfaced item**, because the surfaced inbox is
  deliberately operator-only and *already drowned once* in pollution. That tension is the gold of
  this area and Section 4 is about it.

The one-line answer to "where is a finding stored + addressed": **its detection rides the addressed
event log; its standing dispositioned state rides a surfaced-*like* record in its own lane (NOT the
operator inbox); the burn-down model is a read-time rollup. Three mechanisms, three halves — not one
home.** Section 6 lays this out concretely.

---

## 1 · The address system — the coordinate space, mapped against the code

### What's actually there [OBS]

The canonical grammar is **not** in `addresses.json` (that's a registry *of* `ui://` entries); it
lives at the contract layer in two files:

- **`contracts/address.py:32`** — `SCHEMES = ("run", "cas", "blob", "vec", "ui", "code")`. This is
  the legal scheme set. The module documents each:
  - `run://<domain>/<intent>/<node>@<branch>#run=<id>` — mutable pointer (store-resolved)
  - `cas://<algo>:<hash>` — immutable content (store-resolved)
  - `blob://`, `vec://<source>#emb=<model>` — large binary, embeddings (store-resolved)
  - `ui://<kind>/<ref>` — a UI component (resolved **elsewhere**, not by the store)
  - `code://<file-stem>/<symbol>` — a code symbol (resolved by `Suite.resolve_scope`)
- **`contracts/ui_info.py:186-217`** — `parse_ui_address()` + the `_GRAMMAR_RE`. The grammar is
  **purely structural** (segments + optional `@state`); it does NOT encode kind/region — those are
  *record fields*, not parsed from the string. This is a deliberate design choice and it matters
  enormously for Coherence (see §5): the address string is a dumb locator; meaning lives in records.
- **`runtime/suite.py:7758` `resolve_scope(ui_addr)`** — the `ui://→code://→scope[]` join: takes a
  UI address, reads the corpus join data (`addresses.json` + `code-symbols.json`), and returns the
  code symbols that power it. This is the **already-built bridge from "a thing on screen" to "the
  code behind it"** — exactly the edge a Coherence finding needs to draw.

### How an address is formed / parsed / resolved [OBS]

The three schemes resolve through **three different machineries** — this is a key fact the anchor
glosses:

| scheme | formed by | parsed/validated by | resolved by |
|---|---|---|---|
| `run://` | `contracts/address.py:46 run_address()`, `compile.py:28` | `address.scheme()` | the **store** (`fs_store.head/get_content`) |
| `cas://` | `fs_store.put_content` (`_hash`) | `address.is_cas()` | the **store** (immutable) |
| `ui://`  | hand-authored in `addresses.json` / live `UI_REGISTRY` | `parse_ui_address()` (S0 grammar gate, raises on malformed) | the **frontend resolver** + `_describe_ui_address` — *the store does not resolve it* |
| `code://`| generated by `design/_system/symbols.py` | (corpus-side) | `Suite.resolve_scope` reading corpus join data |

**[INF]** This split is the single most important structural fact for Coherence: `run://`/`cas://`
are *live store coordinates* (resolve to bytes), while `ui://`/`code://` are *labels into side
registries* (resolve to descriptions/symbols, the store refuses them). A finding that anchors to a
`code://` address is anchoring to a **registry entry, not a stored object** — so the finding's *own*
persistence cannot ride the same resolver as its target. (This is why §6 splits storage from
addressing.)

### Addressing COVERAGE — the gap the anchor understates [OBS]

I counted the real registries:

- `design/_system/addresses.json`: **71 addresses, all `ui://`** (no `run://`, `code://`, anything
  else — verified by parsing the file).
- `design/_system/code-symbols.json`: **94 `code://` symbols** (a *separate* registry, keyed
  `code://<file-stem>/<symbol>`, e.g. `code://scheduler/run`, `code://bridge/do_POST`).

The anchor's node list is: "backend routes, public methods/capabilities, front-end surfaces and
components, acceptance suites, registered `ui://` addresses, node-types, migrations, design mockups,
voice engines…" Against the real coverage:

| anchor node-class | addressable today? | how |
|---|---|---|
| front-end surfaces/components | **yes** | `ui://` (71 entries) |
| code symbols / methods | **yes** | `code://` (94 symbols) |
| backend `/api` routes | **partially** | a route literal in `bridge.py`; not a registered address — `reachability()` extracts them by regex |
| node-types | **yes (named)** | registry keys (`capabilities().node_types`), not a `://` address |
| node instances / runs | **yes** | `run://<graph>/<node>` |
| acceptance suites | **no** | a filename in `tests/`; no address |
| migrations | **no** | not modeled at all |
| design mockups | **partially** | a mockup carries a `data-ui-ref` = the *same* `ui://` as its real component (addresses.json `_what`) |
| voice engines | **no** | named in `services.json`, not addressed |

**[IDEA]** So "every element has an address" is *partly aspirational*. For Coherence to model the
whole anchor node-set, the address space must **grow new element-classes**, and the honest options
are: (a) extend the existing schemes' segment-space (`ui://`/`code://` already prove this is just a
registration), or (b) — better, per the project's own law — give suites/migrations/engines a
`code://`-style entry (a suite *is* a file with symbols; a voice engine *is* a config record), so no
new scheme is needed, only new registry rows. This is the "more types, not more tools" answer applied
to *addresses*: don't invent `suite://`, register the suite at `code://tests/<name>`.

---

## 2 · The registry — the "declared truth" half of integrity

### What's there [OBS]

`capabilities()` (`runtime/suite.py:683-767`) is the system's machine-readable self-model — "one
snapshot of WHAT EXISTS … the reflective fold." It projects, **all from the live registry, never
hardcoded:** `node_types`, `models`, `modes` + `mode_directives` + `mode_registry` (hierarchical),
`rhm_verbs`, `node_states` (a state-type registry!), `panels`, `stt`, `cognition` (role/rule
registry), `composition_config`, `api_verbs`.

The crucial pattern, stated in the code itself repeatedly: **"registry-is-truth"** — the surface
*reads* the vocabulary from `capabilities()` rather than hardcoding it (e.g. `node_states` comment,
suite.py:721: "the surface renders the status vocabulary from here instead of hardcoding
idle/ran/cached/stuck/live/empty").

### Why this is half of integrity already [OBS, agreeing with the anchor]

The anchor's claim — "the registry says what *should* be; the live system shows what *is*; coherence
is the comparison" — is **directly supported** by `doc_drift()` (`suite.py:855`) +
`refresh_self_description()` (`suite.py:823`): the MAP/STATE files are *regenerated from the live
registry*, and `doc_drift` fails loud if the written description falls behind. That is *exactly* a
declared-vs-actual comparison, already running. Coherence generalizes the comparison from
"description vs registry" to "every edge vs every registry expectation."

### The extension point for finding-types [IDEA, grounded]

Here is the concrete "more types not more tools" move. `capabilities()` already exposes
`node_states` as a **state-type registry** — a list of `{state, meaning, applies_to}`. The Coherence
model's "kinds of finding" (`unwired-route`, `half-migration`, `stale-symbol`, `uncovered-capability`)
should be **declared the same way: a `finding_types` registry projected by `capabilities()`**, each
entry carrying `{kind, detector, default_disposition, applies_to_scheme, explain_template}`. Then:

- a *new* integrity check is a **registry row + a detector function**, not a new bespoke gate class —
  answering anchor §9's "types of finding is itself a registry the system can grow";
- the RHM and the surface read the finding vocabulary from `capabilities().finding_types`, so they
  render new finding-kinds with zero code change (registry-is-truth);
- `up_translate` (the at-altitude explainer, suite.py:5775) can be made to dispatch on the
  finding-kind's `explain_template`, so explanations stay faithful to the declared type.

This is the single cleanest place the Coherence model attaches to the registry: **finding-kinds are
node-states for the *system itself* rather than for a node instance.**

---

## 3 · The typed structured-record patterns — the storage idiom

The anchor says findings should be "typed in the same way the rest of the app is typed." Here is the
actual idiom in this repo, which is **not** primarily "typed fences" (that's the Vi-Chat plugin's
substrate, a *separate* system per the no-MVP/found-elsewhere memory) — in `~/company` the typed-
record idiom is:

### Pattern A — the open append-only addressed log [OBS]

`fs_store.append_annotation(rec)` / `annotations_for(address)` (`fs_store.py:534-566`):
- writes `{ts, **rec}` to a single `annotations.jsonl`, **keyed by the `address` field — the address
  IS the key**;
- append-only (an address accrues a *thread*, never last-write-wins);
- the store stays "dumb" — it does **not** validate the address; the S0 grammar gate is the Suite's
  job. Storage and meaning are deliberately separated.

This is **the exact shape a finding-record wants** and it is the closest prior art to "a finding is a
living record at an address." `append_chat`/`chats_for` (`fs_store.py:495-531`) and the event log are
the same idiom.

### Pattern B — the mutable-state overlay on an immutable log [OBS] — *the disposition mechanism*

This is the subtle, important one. The store is append-only/immutable by constitution
(`store/AGENTS.md`: "an 'update' is a new object + a moved pointer"). So how do you give an
append-only record a *mutable* state (e.g. a finding moving `open → dispositioned → resolved`)? The
repo already solved this exact problem for pins (`fs_store.py:569-625`):

> `append_pin` writes a tiny separate `pins.jsonl` keyed by `(address, target_ts)`, resolved
> **LAST-WINS on read** (`pin_state_for`). The docstring is explicit about *why*: you can't mutate
> the append-only annotation line, and re-appending is dedup-dropped, so pin-state is an **additive
> overlay** resolved at read time.

**[IDEA]** A finding's **disposition lifecycle is structurally identical to a pin**: the finding is
an immutable detection record (append-only), and its disposition (`to-wire` → `deferred` →
`by-design` → `resolved`) is an **additive overlay** (`coherence_disposition.jsonl`?) resolved
last-wins. This is not a guess about how it *could* work — it is *literally the pattern the repo
already uses for exactly this immutable-log-with-mutable-state problem*. It even has the right honesty
property: the disposition *history* is preserved (who dispositioned it by-design, and when — anchor
§9's institutional-memory want).

### Pattern C — the read-time rollup over events [OBS]

`emit_run_record(op, duration_ms, **conditions)` → `run_stats()` (`suite.py:~520-560`): a typed
run-record is emitted into the **existing** event log (`kind='op.run'`), and the distributions
(n/median/p95) are **DERIVED off the hot path on read**, "NOT a new analytics store." This is the
project's **Introspective Data Building law** in working code — the exact law the anchor says
Coherence is "pointed, for the first time, at integrity itself."

**[IDEA]** The Coherence *model* (the burn-down, the count of open findings by kind/owner) is a
`run_stats`-style **read-time rollup over `kind='coherence.finding'` events** — never a maintained
materialized graph. This kills anchor §7.6's cost worry at the root: you don't *maintain* a live
graph, you *re-derive* the model on read from an append-only event stream, exactly as `run_stats`
already does. Incremental detection appends events; the model is always a fold over them.

---

## 4 · The contradiction the anchor must absorb — *a finding is NOT a surfaced item*

This is the most important thing in this file. I went looking to confirm "a finding is a surfaced
item" and the code refused it. Two pieces of evidence:

1. **`Inbox.resolve()` is deliberately operator-only and kept off the agent face**
   (`governance.py:184-187`): *"OPERATOR-only … Must NOT be reachable by the agent it gates — kept
   off the MCP face; only the UI/operator channel calls this."* The autonomous loop **by design
   cannot self-dispose** a surfaced item. If findings were surfaced items, the loop could detect them
   but never clear them without Tim — defeating the whole "burns down autonomously" promise.

2. **The surfaced inbox already drowned once.** `governance.py:123-133` (the `test_origin` fix): the
   operator inbox *"was ~90% test/adversarial pollution."* Hundreds of auto-detected findings poured
   into the *same* queue would re-create exactly that flood, and bury the genuine consequential
   decisions (the spends, the external publishes) the inbox exists to protect.

So the design answer is **not** "findings are surfaced items." It is: **findings get their own lane
that borrows the surfaced item's *shape* — `status` lifecycle (closed vocabulary, fail-loud,
`set_status` raises on unknown, governance.py:151,163-176) + `resolved`/`reason` (the WHY,
governance.py:184-197) — but is NOT the operator decision inbox.** Concretely [IDEA]:

- A finding lives in a `coherence/` lane (its own surfaced-*like* store dir, or a tagged sub-stream),
  with its own status vocabulary: `("open", "to-wire", "deferred", "by-design", "resolved",
  "regressed")`.
- **Most dispositions are auto/agent-settable** (the loop dispositions a clear `unwired-route` as
  `to-wire` and proceeds) — the *opposite* posture from the operator inbox's `resolve()`. Only the
  *consequential* disposition (marking something **`by-design`** — i.e. permanently accepting a gap)
  **escalates to the operator inbox** through the *existing* consent gate (`governance.POLICY`). That
  is the right division: the machine burns down `to-wire`; Tim alone says `by-design`.
- This also fixes anchor §7.2's "dumping-ground" worry mechanically: `by-design` is the *only*
  disposition that routes through the operator gate, so it can't be set silently to hide a real gap;
  every `by-design` carries Tim's `reason` (governance.py:188) and accretes into documented
  architecture.

**[INF]** This is *more* faithful to the substrate than the anchor's "findings are typed like
surfaced items," because it reuses the *mechanism* (status + resolve + consent gate) while respecting
the *boundary* (agent-disposable vs operator-only) the code already enforces.

---

## 5 · `coherence://` — does the finding need its own scheme? (the anchor's open question, decided)

Anchor §9 asks: "a `coherence://` scheme, or do findings ride existing `code://`/`ui://`?" The code
gives a clean, defensible split — **both, for different things:**

- **The finding's TARGET rides existing schemes.** A finding *about* an unwired route anchors to the
  `code://` symbol (and the `ui://` surface that should consume it). The store side is uniform: every
  `_emit` is address-stamped and `events_since` returns them all regardless of scheme **[OBS]**, so a
  `coherence.finding` event carrying `address=<code://…>` *is* persisted and queryable by that address.
  **BUT — the one "for free" claim that does NOT hold [OBS, corrected]:** the existing
  `/api/address-history` endpoint (bridge.py:401) → `address_view` (suite.py:9482-9486) calls
  `parse_ui_address()` as an S0 gate that **raises on any non-`ui://` string** (the grammar is
  `^ui://`; the docstring at suite.py:9476 is explicit — *"SCOPE: `ui://` queries only"*). So a
  `code://`-targeted finding does **not** surface through `/api/address-history` today; it would 400.
  Two honest consequences: (a) a finding's `ui://` "also" field (the surface that should consume the
  route) *does* appear in that surface's history for free — the operator clicking the relevant surface
  sees it; (b) for the `code://` target to be browsable by-address, `address_view` must be **widened to
  admit `code://`** (a small, on-theme "what's missing" item — the reader's address-equality filter
  already works for any scheme; only the `parse_ui_address` gate blocks it). **[INF]** This is anchor's
  "the same address that names a button names the finding about that button" — *true at the store/event
  layer now, true at the operator-browse layer after a one-method widening.*

- **The finding's OWN identity is a record id, NOT a new scheme.** The surfaced system already mints
  ids like `s<N>-<action_class>` (`governance.py:120`); events already carry a monotonic `seq`
  (`fs_store.py:459`). A finding's identity should be a `finding:<kind>:<target-address>:<seq>`-style
  **stable id in its own lane**, not a `coherence://` address. **[IDEA + grounded]** Reason: the
  `://` schemes in this repo are *resolution contracts* (the store or a named resolver turns them into
  content/symbols). A finding is not a *resolvable location* — it's a *record about* a location. The
  project's law is "more types, not more tools/schemes." Inventing `coherence://` would be a new
  scheme that resolves to… a record in a lane keyed by `code://` anyway. So: **no `coherence://`.**
  The finding is a *typed record whose `target` field is an existing address.* That is strictly truer
  to `contracts/address.py`'s own model (where `ui://`/`code://` are "labels," and the resolvable
  things are `run://`/`cas://`).

This decision is the concrete answer to anchor §7.3 ("build-on-not-beside, how exactly?"): a finding
introduces **no new store, no new scheme, no new resolver** — only (a) a new `kind` on the existing
event log, (b) a new disposition overlay reusing the pin pattern, (c) a new `finding_types` registry
row in `capabilities()`, and (d) a new lane that reuses the surfaced *shape* but its own status
vocabulary. Four registrations, zero parallel machinery.

---

## 6 · WHERE a finding is stored + addressed — the concrete three-halves answer

Pulling §3–§5 together into the deliverable the anchor asked for. A finding has **three lives**, each
on a mechanism that already exists:

```
LIFE 1 — DETECTION (the moment a detector sees a gap)
  → an addressed event:  store.append_event({
        kind:    "coherence.finding",
        finding: "unwired-route",          # the finding-TYPE (from the finding_types registry)
        target:  "code://bridge/api_knobs", # rides an EXISTING scheme; persisted+queryable by address
        also:    "ui://config/knobs",       # the surface that SHOULD consume it — THIS one shows in /api/address-history (§5)
        state:   "built-no-caller",
        evidence:"reachability(): no caller in canvas/app/src or tests/",
        owner:   "interface-stream",
        seq:     <monotonic, from append_event>
     }, address="code://bridge/api_knobs")
  mechanism: fs_store.append_event (suite.py:_emit) — ALREADY address-stamped on every emit
  (event_address_acceptance enforces it). Sibling of emit_run_record. NO NEW STORE.

LIFE 2 — STANDING DISPOSITIONED STATE (does this gap still stand, and what's the call on it)
  → a surfaced-LIKE record in the coherence lane + a last-wins disposition overlay:
        coherence_disposition.jsonl  keyed by (finding-id) → { state, by, reason, ts }
  mechanism: the PIN overlay pattern (fs_store.append_pin/pin_state_for) for the mutable state,
  + the surfaced status-vocabulary + resolve/reason SHAPE (governance.Inbox) — but its OWN lane,
  NOT the operator inbox (§4). by-design escalates through governance.POLICY to the real inbox.

LIFE 3 — THE MODEL / BURN-DOWN (the glanceable whole; what the loop reads as its worklist)
  → a read-time rollup:  fold kind="coherence.finding" events ⨝ disposition overlay
     → { open_by_kind, open_by_owner, burn_down_over_time, net_change }
  mechanism: the run_stats() pattern (suite.py) — derived on read, off the hot path. NO MAINTAINED
  GRAPH. The loop's "done" = this rollup has zero open non-by-design findings.
```

**[INF]** Every cell above names a real method or a real pattern in the repo. Nothing in the storage
+ addressing layer is net-new machinery; it is *configuration of existing mechanisms*. The only
genuinely new code is the **detectors** (Area C) and the **finding_types registry rows** + the
**lane-specific status vocabulary**.

---

## 7 · What's perfectly suited / missing / must-be-added (the scorecard)

**Perfectly suited (use as-is):**
- `contracts/address.py` SCHEMES + the additive-extension precedent — the coordinate space, with a
  proven way to widen it (but §5: we don't even need to widen it).
- `fs_store.append_event` / `events_since` / address-stamped `_emit` — the detection log, *already*
  the addressed, queryable substrate; findings show up in `address-history` for free.
- The pin overlay pattern — the immutable-log-with-mutable-disposition solution, already solved.
- `run_stats` / Introspective-Data-Building — the read-time rollup = the burn-down model.
- `capabilities()` registry-is-truth + `node_states` state-registry — the home for `finding_types`.
- `up_translate`/`address_help`/`resolve_scope` — the RHM can explain a finding at a `code://`/`ui://`
  target with NO new explainer (anchor §6, §7.5).
- The surfaced `status`+`resolved`+`reason`+consent-gate *shape* — the disposition machinery (reuse
  the shape, §4).

**Missing / must be added:**
- A **finding lane** distinct from the operator inbox (§4) — the single most important new piece.
- **Address coverage** for suites, migrations, voice engines, `/api` routes-as-registered-addresses
  (§1) — register them `code://`-style; don't invent schemes.
- **Migrate `_ORPHAN_ROUTES` from a hardcoded dict (`suite.py:7017`) to persisted dispositioned
  records.** Today it's the right *shape* (route → `(tag, note)`, where tag ∈ `to_build_ui|to_wire|
  voice_owned|backend_only` is literally an embryonic disposition) in the *wrong form* (a Python
  literal an agent must edit-in-source to update). Promoting it to records is both a migration *and*
  the **first real test** of the finding lane — and a satisfying recursion: the orphan catalogue
  becomes the first set of Coherence findings.
- A **`finding_types` registry** projected by `capabilities()` (§2) — so new checks are declared rows.
- **Widen `address_view` to admit `code://`** (suite.py:9482-9486 — today `parse_ui_address`-gated to
  `ui://`, §5) so findings targeting code symbols are browsable by their target, not only via their
  `ui://` "also" surface. Small: the address-equality filter is already scheme-agnostic; only the gate
  blocks it.
- The detectors' **accuracy upgrade from string-match to AST** — *Area C's territory*; I note only
  that the AST tool already exists (`codeedges.py` `reach()/reach_report()`, bounded, fail-loud), so a
  finding's `evidence` field can anchor to a *precise* `code-edges.json` reach result instead of
  `reachability()`'s current regex (`suite.py:7068` `re.findall(r'"(/api/...)"')` against concatenated
  FE/test source — which the anchor §7.1 correctly flags as false-positive-prone).

---

## 8 · Extensions the substrate makes cheap (leaving the idea bigger)

- **The recursion is real and the substrate supports it [IDEA].** Anchor §9 asks "could the model
  watch the coherence of the mechanisms that maintain coherence?" Yes, *for free*: the consent gate,
  the build wire, the detectors are all *code symbols* with `code://` addresses and `code-edges.json`
  reach data. A finding can target `code://governance/resolve` as legitimately as `code://bridge/
  api_knobs`. The Coherence model can hold a finding *about its own disposition mechanism* with no new
  machinery — the address space is uniform over the system including itself.

- **Burn-down history IS institutional memory [OBS-supported].** Because detection rides the
  append-only event log (monotonic `seq`, `ts`), the questions anchor §9 wants — "when did this
  connect, what migration left this, who dispositioned that by-design and why" — are **`events_since`
  queries filtered by `kind='coherence.finding'` + the disposition overlay's preserved history.** The
  `reason` field (governance.py:188 — "the trajectory that generalises, not just the endpoint") is
  *already* the place the why is captured. The thing-that-replaces-the-developer-who-remembers is a
  query over a log that already exists. (Per §5: the *event store* holds these keyed by any address;
  only the operator-facing `/api/address-history` browse path is `ui://`-gated and needs a one-method
  widening to browse `code://`-targeted findings — not new machinery.)

- **One substrate, two lenses (Coherence ⨯ Cognition) [INF].** Anchor §9's deepest open question —
  are the Coherence model and the Cognition stream "the same kind of thing"? From the storage layer,
  **yes**: the cognition stream is *also* address-stamped events on the *same* log (`run://` node
  events, the `cognition.*` SSE branch; suite.py:5371 `_emit` with `_cog_addr`). Both are live,
  addressed, reflects-never-owns folds over the *one* event log. They are not two substrates; they are
  **two `kind=` filters over one event stream**, two read-time rollups, two lenses. That is the
  strongest possible version of "build-on-not-beside": Coherence and Cognition *share the event log
  and the address space by construction* — the only difference is the `kind` they fold.

- **`reflects-never-owns` is automatic [OBS].** Because the finding model is a read-time rollup over
  events surfaced via the existing SSE stream (`events_since` → `id:<seq>`, bridge.py), a Coherence
  *surface* (anchor §6) inherits liveness with no state of its own — findings appear/resolve in front
  of Tim as the loop appends `coherence.finding` and disposition events. The cognition view
  (`CognitionView.tsx`) is the existing proof that this render-a-live-fold pattern works.

---

## 9 · The honest fragilities I can see from THIS layer

- **The event log is not cross-process-unique on `seq`** (`fs_store.py:438-444`, surfaced to Tim):
  two *processes* can both append `seq=N`. For *telemetry* findings this is tolerable (a rollup
  tolerates a dup), but if a finding's *identity* keys on `seq`, two sessions detecting concurrently
  could collide. **[IDEA]** Key finding identity on `(kind, target-address, content-hash)` not on
  `seq`, so a duplicate detection *dedups* rather than forks — and the dedup is itself the
  "this gap still stands" signal.

- **`ui://`/`code://` resolve through side registries the store won't touch** (§1) — so a finding
  whose target's *registry entry* is stale (`code-symbols.json` `resolves:false`, a named symbol no
  longer in the file) is anchored to a *dangling address*. That's not a bug — `symbols.py` already
  treats `resolves:false` as a **drift signal**. **[IDEA]** A dangling finding-target is itself a
  finding (`stale-target`), which is the right recursive behavior, but the model must not silently
  drop it (the no-silent-failures law).

- **The disposition overlay's last-wins read is O(scan) on a growing `.jsonl`** (same as
  `pin_state_for`, `annotations_for` — they read the whole file each call, `fs_store.py:554`). Fine at
  71 addresses / dozens of findings; a whole-system graph at scale would want the compaction the store
  already contemplates for refs. Flagged, not solved — and squarely the Supabase-backend seam
  (`store/AGENTS.md`: "Filesystem-first; Supabase later"), which the resolver indirection already
  isolates.

---

## 10 · One-paragraph synthesis for the cross-area read

The addressable substrate is **ready to host a Coherence model without a single new store, scheme, or
resolver** — detection rides the already-address-stamped event log (so findings auto-appear in their
target's address-history), the disposition lifecycle reuses the proven pin-overlay-on-immutable-log
pattern plus the surfaced status/`resolved`/`reason`/consent-gate *shape*, and the burn-down model is
a `run_stats`-style read-time fold (no maintained graph → the cost worry dissolves). The two hard
truths the anchor must absorb: **(1) a finding cannot BE a surfaced item** — the operator inbox is
deliberately operator-only and already-drowned, so findings need their own lane that borrows the
shape but is agent-disposable, with only `by-design` escalating through the consent gate; and **(2)
the address space is `ui://`-only (71) today and far narrower than the anchor's node-set** —
suites/migrations/engines must be *registered* (`code://`-style, not new schemes) before they're
modelable. The cleanest single win: promote the hardcoded `_ORPHAN_ROUTES` dict into the first real
dispositioned finding-records, which is simultaneously the migration, the first test of the lane, and
the recursion the anchor dreams of (the system holding findings about itself).
