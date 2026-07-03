# AREA CENSUS — app/registry/ (the Type spine) — read 2026-07-03

> Reader: registry-spine lens, UNIFICATION mandate. All 13 files in `app/registry/` read in FULL
> first-hand this pass (not re-derived from the ledger). Cross-checked against READING-LEDGER.md's
> prior partial reads of types-core/types-seed/conditions/glyphic-type/kinds-type — no contradictions
> found; this report adds the 6 files the ledger never opened (SaveAsTypeModal, components-type,
> types-adapter, types-hooks, types-thumb, types-ui, types-vi — 7 actually) plus consumer-tracing
> the ledger didn't do.

## §A · File-by-file account (file:line)

1. **types-core.js** (17.2K, 389 lines) — THE registry engine. `register/registerMany/update/remove/
   get/all/query/resolve/lineage/children/descendants/accepts/candidatesForSlot/slotEnabled/
   socketInfo/subscribe`. Storage: `BUILTIN`/`USER`/`TEMPLATES` Maps in memory; `USER`+`TEMPLATES`
   persist to `localStorage` (`cv:registry:user-types`, `cv:registry:templates`, lines 56-57).
   `normalize()` (309-367) is the single gate every registered Type passes through — **the dropped-
   field trap lives here**: any field not explicitly listed in normalize's return object is silently
   discarded on every register/update. Post-R1 (2026-07-03, this session's edit at 345-353) it
   explicitly carries `relationKind/operatorSymbol/negates/directed/inverse` with a comment naming
   the trap by class ("a normalize that doesn't carry a field makes the entry silently inert").
   `accepts()` (249-273) is the ONE socket/slot acceptance function — classification-array shorthand,
   `acc.classification/forbid/layers/families/tags`, AND a `slot.conditions` gate that calls
   `window.CV_COND.testAll` (253) — **this is the seam where Types and conditions meet.**
2. **types-seed.js** (22.6K, 402 lines) — registers 11 tokens, 4 atoms, 11 blocks (from
   `blockSeeds`), 3 widget systems, 12 surfaces (3 widget-kind + 5 wizard-step + 3+1 slide layouts),
   4 docs, 3 wizard-kinds, PLUS the entire `window.CV_ARCHETYPE_CATALOG` spread in at line 350 —
   **this is where core/archetype-catalog.js's archetypes become registry Types**, single-sourced
   (throws at line 348 if the catalogue isn't loaded first — loud dependency). `hydrateBlockDefaults()`
   (356-380) back-fills block Type defaults from `window.WS_BLOCKS` once Babel loads it, polling up
   to 5s. Line 387-388: `// CV_HOST:types` marker comment — Vi-authored types insert above this line
   (a textual insertion point, not `CV_HOST` as a real object — see §C).
3. **types-thumb.jsx** (27.8K, 661 lines) — the universal thumbnail dispatcher (`pickRenderer`,
   72-111) — one function per layer×family combo, ~20 renderer functions. Notably: `BlockThumb`,
   `SystemWidgetThumb`, `SurfaceSlideThumb`, `DocDeckThumb`, `DocBrochureThumb` all gate on
   `window.__coreReady`/`window.__cvRenderType` and render THROUGH the one engine (RenderType) rather
   than hand-drawing — the comments at 197-201, 258-261, 423-426, 513-516, 549-550 explicitly cite
   "UNIFICATION Wn" for each — this file is itself a record of a prior unification pass done right.
   `RenderShape` (614-647) hand-draws hexagon/octagon/diamond/circle SVGs locally — a small
   **duplicate** of shape-drawing logic that likely also exists in `assets/icons/cv-shapes.js`
   (unread this pass — flag for cv-shapes reader) — low-risk (pure decorative thumb shapes, 4 lines
   each) but worth a REUSE check.
4. **conditions.js** (5.7K, 122 lines) — `CV_COND`: `test/testAll/failures/normalize`, a string-DSL
   (`"fill != none"`, `"A requires B"` sugar), structured `{field,op,value}`/`{all}`/`{any}`/`{not}`,
   and a predicate escape hatch. Pure, no dependencies (comment line 20 confirms "load after nothing").
   Unknown op → **permissive** (line 95, "unknown op → permissive (loud elsewhere)") — this is the
   ONE place in the registry spine that is NOT loud-fail by default; it defers loudness to a caller
   that never actually checks (see §C for the risk this creates).
5. **glyphic-type.js** (6.1K, 119 lines) — registers the reference universal component: 3 part-Types
   (`glyphic-ring`, `glyphic-symbol`, `glyphic-fill`) + the parent `glyphic` Type. THE canonical
   demonstration of `sub(axisId, extra)` (29-33) — a value-slot that is an axis SUBSCRIPTION, default
   resolved live from `CV_AXES.resolve(axisId).default()`, never copied. `R.glyphic.valuesFor(facet)`
   (117) exposes `CV_GLYPHIC.valuesOf` without duplicating it.
6. **kinds-type.js** (4.7K, 77 lines) — 3 more Types: `panel.composition-menu` (a socket-acceptance
   demo), `kind.graph` (points at `core/DiagramSolver`, edges socket `accepts:['relationship']` —
   THE placeholder relationships-seed.js fills), `kind.slide-system` (points at `core/Slide`). Line
   50: `layout` valueSlot declares enum `[force,tree,radial,flow,grid]` but the ledger already found
   (and I confirm by not finding any registry-side reconciliation) the solver implements its own
   layout set — a **declared-vs-implemented drift**, small, flagged not fixed here.
7. **relationships-seed.js** (8.1K, 146 lines) — read in full above (§ Reading Ledger already covered
   this one in depth: live union of `CV_EDGES.ids()` ∪ `CV_MEANING.valuesFor('edge')`, R1's
   `{directed,inverse}` mirroring at 76-101, sockets accept `['glyphic','atom','block']`). Nothing new
   to add beyond confirming the ledger's account matches the current file exactly (post-R1).
8. **components-type.js** (8.1K, 138 lines) — registers 11 UI-component Types (button/badge/avatar/
   card/input/switch/tabs/segmented/stepper/modal) at `runtime:{kind:'react-component', global: NS+
   '.'+d.name}` where `NS='ConceptVDesignSystem_c8f43c'` (31) — a pointer into the compiled DS bundle.
   Its own header (lines 6-13) states the ambition precisely: "Everything on an interface is a
   templated dynamic component … and they're all in registries" — but see §C: **zero consumers**.
9. **types-adapter.js** (8.8K, 223 lines) — bidirectional-looking but actually ONE-directional bridge:
   registry → legacy globals (`WIDGET_KINDS/WIDGET_SYSTEMS/WIZARD_KINDS/STEP_KINDS`), merging registry
   Types with whatever pre-existed in those legacy arrays (preserves both, registry wins on id
   collision). Runs on a poll-then-subscribe pattern (160-176) because Babel-loaded scripts trickle
   in. Also hosts `window.CV_TYPES_SAVE` (182-209, `fromWidget/fromWizard/fromWizardStep/fromBlock` —
   instance-to-Type promotion entry points) and `window.CV_TYPES_PROMPT` (215-221, the modal-open
   pub/sub `SaveAsTypeModal` subscribes to).
10. **types-hooks.js** (2.2K, 62 lines) — `useTypes/useType/useResolvedType/useLineage/useChildren/
    useRegistryActions` — thin reactive wrappers around `R.subscribe`. No logic of its own; a correct
    thin layer (nothing to flag).
11. **types-vi.js** (8.8K, 206 lines) — AI-authoring surface for Types: `proposeType` (brief→draft
    Type via `CV_AI.execute('type.propose', …)`), `promoteInstance` (an existing doc/widget/wizard
    instance → a Type via `'type.materialize'`), `suggestSlots`. All three route through
    `window.CV_AI.execute` — confirms the Type registry's AI-authoring path is wired to the ONE AI
    registry (`CV_AI`), not a parallel LLM call — consistent with the four-registries law in the
    project CLAUDE.md.
12. **types-ui.jsx** (10.2K, 252 lines) — shared visual primitives: `TypeLayerBadge/TypeProvBadge/
    TypeChip/TypeCard/TypeLineageStrip/SlotAcceptsHint/TypeSlotList/TypeFilterBar/TypeTree/
    TypeTreeNode`. All read live from `window.CV_REGISTRY` — no cached/copied Type data. Clean.
13. **SaveAsTypeModal.jsx** (5.2K, 105 lines) — a review-before-commit modal for `types-vi.js`'s
    AI-proposed drafts; calls `window.CV_REGISTRY.register(draft)` directly (line 31) on Save. This
    is a REAL, reachable write path into the persisted USER map (see §C, localStorage liveness).

## §B · UNIFICATION findings + fold-in designs

**B1 — the Type system and the glyphic language are TWO SEPARATE GRAMMARS that already
INTERLOCK at exactly one seam, and the seam is sound.** The glyphic language (CV_MEANING/CV_EDGES/
readGraph, in `assets/icons/`) owns MEANING (what a thing says). The Type registry (this folder) owns
STRUCTURE (what a thing IS — its slots, sockets, inheritance, acceptance). They interlock via:
  - `glyphic-type.js`'s `sub(axisId)` reads `CV_AXES` (value vocabulary) — never `CV_MEANING`.
  - `relationships-seed.js` reads `CV_MEANING.valuesFor('edge')` + `CV_EDGES.ids()` to MINT structural
    Types from meaning-side vocabulary — the one place the two grammars cross, and it's a clean
    one-way REUSE (mint Types from meaning, never mint meaning from Types).
  - `glyphgraph.js` (assets/icons/, already read per ledger) is the actual consumer that walks BOTH:
    it resolves edge kind → `relationship.<kind>` Type (structure/socket validation) AND separately
    reads `CV_MEANING`/`CV_COND` for meaning/condition validation. Confirmed live at
    `assets/icons/glyphgraph.js:61` (`R.query({family:'relationship'}).filter(rt => rt.relationKind
    === kind || rt.id === kind)`).
  This is NOT drift — it's the correct separation the CLAUDE.md's four-registries table describes
  ("Types" vs the generative engine are separate rows). **No fold-in needed here; this seam is
  already unified correctly.** The risk is elsewhere (§C, §D).

**B2 — the axis-subscription pattern (`sub()`) is used in EXACTLY ONE FILE** (`glyphic-type.js`),
not system-wide. `components-type.js`'s `ax(axis, extra)` (line 25) is a DIFFERENT, thinner helper —
it declares `{axis, ...extra}` directly without resolving a live default via `CV_AXES.resolve(axisId)
.default()`. Only 2 of components-type.js's ~15 value-slots use `ax()` (avatar.size, card.depth); the
other 13 use `en([...])` — hand-enumerated arrays that are the COMPONENT'S OWN prop contract (e.g.
button `variant: en(['primary','ink','outline',...])`), which is legitimate per the file's own header
comment ("enum props list their values inline (the component's own contract)") — these are NOT
axis-vocabulary duplicates (verified: none of `primary/ink/outline/ghost/soft/comm` etc. collide with
an axis id in `axes/`). **UNIFICATION OPPORTUNITY**: `ax()` and `sub()` are the same concept
(axis-subscription) implemented twice, one lighter-weight. Fold `ax()` into `sub()` (or make `ax()`
call `sub()` under the hood) so there is ONE axis-subscription primitive across the whole registry,
not a glyphic-only one and a components-only one that happen to look similar. Low-risk, mechanical.

**B3 — CV_COND is genuinely the one evaluator, confirmed by grep, with one soft spot.** Every
consumer (`types-core.js` accepts/slotEnabled, `cv-meaning.js`'s conditionPhrase per the ledger,
`glyphgraph.js`'s edge-instance conditions) calls into `window.CV_COND` — no parallel condition logic
found anywhere in `app/registry/`, `assets/icons/`, or the demo harnesses. **The one gap**: unknown
operators are "permissive" (conditions.js:95) with a comment deferring loudness to "elsewhere" — I
found no "elsewhere" that actually checks for this and throws. This is a real, small loud-fail gap:
an author who typos an op (`'!==' ` instead of `'!='`) gets a SILENTLY-PASSING condition, not a thrown
error — the opposite of every other loud-fail law in this codebase. **Fold-in**: `CV_COND.test`
should throw on an unrecognized `op` unless a caller explicitly opts into permissive mode; this is a
one-line change (`if (!op) throw new Error(...)` at conditions.js:95) consistent with G2.5's "every
new facet value LOUD-FAILS on an unknown value" law, which this evaluator currently violates.

**B4 — `types-adapter.js` is a real, working, ALREADY-UNIFIED bridge**, not drift: it keeps legacy
globals (`WIDGET_KINDS` etc.) as PROJECTIONS of the registry rather than a second source (registry
wins on id collision, legacy fills gaps). This is the pattern the whole system should use whenever
retiring a legacy array — cite as the template.

## §C · Disconnected/unused Types + files (evidence: zero consumers)

1. **`components-type.js`'s 11 component Types — ORPHANED.** Grepped every `component.button` /
   `component.badge` / `component.card` / `component.modal` id and the general pattern
   `CV_REGISTRY.query` against `family`/`classification: 'control'|'status'|'overlay'` etc. across the
   whole tree: the ONLY reference to any of these ids is `kinds-type.js` (which does not reference
   them either — that grep hit was a false-positive scan boundary, re-checked: `kinds-type.js` has NO
   `component.*` references; the grep matched because both files were in the same search glob). Re-run
   confirms: **no builder, no panel, no candidatesForSocket call, no `system/*.html` page reads any
   `component.*` Type.** They render via `runtime:{kind:'react-component', global: NS+'.'+name}` but
   nothing resolves that runtime pointer anywhere (no dispatcher case for `'react-component'` exists
   in `types-thumb.jsx`'s `pickRenderer` — confirmed by reading pickRenderer in full: it dispatches on
   layer/family only, never checks `runtime.kind === 'react-component'`). **These 11 Types are
   declared, structurally complete, and completely inert** — a real orphan class, exactly the kind of
   "designed ahead of time, nothing in use" case my UNIFICATION lens was sent to find. Disposition
   options: (a) wire `types-thumb.jsx` with a `react-component` thumbnail case that resolves `NS+'.'+
   name` off `window` and renders it live — would make the whole file earn its keep and give the
   Type registry actual UI-component coverage (the stated ambition); (b) if the compiled bundle
   doesn't actually export flat names at `window.ConceptVDesignSystem_c8f43c.Button` etc. (unverified
   — the bundle is compiled output per the project CLAUDE.md's traps section, not opened this pass),
   the runtime pointer itself may be stale and need re-pointing before (a) can work.
2. **`kind.slide-system` and `kind.graph` — read but not exercised beyond one demo page and one
   verify harness.** `system/type-system.html:174` reads `panel.composition-menu` (the ONE genuinely
   demonstrated Type from kinds-type.js); `kind.graph`/`kind.slide-system` have zero consumers outside
   `_demo/verify_g3.js`. Lower-severity than #1 (they're pointers at real, live engines — DiagramSolver
   and Slide both run elsewhere — so the ENGINES aren't orphaned, only their registry-Type wrapper is
   unexercised as a socket-acceptance demo). Disposition: low-priority; these are honest "declared,
   not yet wired into a composition-menu UI" stubs, consistent with kinds-type.js's own header
   ("registers thin Type declarations that POINT at the existing graph/slide engines").
3. **The node-level `address` field (G3.1's flagged gap) — independently reconfirmed.** I read
   `normalize()` in full (types-core.js:309-367): it carries `id/name/layer/family/kind/
   classification/description/extends/slots/sockets/valueSlots/parts/conditions/axis/axisValue/
   relationKind/operatorSymbol/negates/directed/inverse/defaults/variables/tags/provenance/icon/
   render/createdAt/updatedAt/version/forkedFrom/runtime` — 29 fields, NO top-level `address`. The
   only `address` in this file is nested inside `socketInfo()` (line 297, an occupant pointer for a
   SOCKET, not the Type/node itself). CRITERIA G3.1's claim ("the node `address` field is NOT yet
   carried — the G6.2 seam") is confirmed TRUE by this full read, independent of the ledger's prior
   partial read. This is the concrete blocker for G6.1 (a glyphgraph node's `address` resolving via
   `resolve_address`) — until `normalize()` gains an `address` field, no Type can carry a real Company
   address, and G6 stays undone by construction, not by oversight.
4. **`localStorage` persistence — LIVE, not vestigial (correcting a plausible assumption).** Traced
   the full write path: `SaveAsTypeModal.jsx:31` → `window.CV_REGISTRY.register(draft)` →
   `types-core.js:100` `register()` → since `provenance` on an AI-drafted Type defaults to `'user'`
   (types-vi.js never sets `provenance:'built-in'`) → `USER.set()` (105) → `saveUserTypes()` (108) →
   `localStorage.setItem('cv:registry:user-types', …)` (87). `app/index.html` loads the full registry
   chain INCLUDING `TypeBuilder.jsx`/`RegistryInspector.jsx`, and `RegistryInspector.jsx:573` calls
   `window.CV_REGISTRY.register(p.draft)` directly — a second real write path, in the main app
   surface, not a demo page. **Verified (Observed, not Inferred): the persistence path is reachable
   from the shipped app, both files that write to it are loaded by `app/index.html`.** I did not
   execute it in a browser this pass (no chrome-devtools run), so "loads on boot and round-trips a
   real localStorage write" is Observed-by-trace, not Verified-by-execution — flagging the
   distinction per the evidence-classification rule.

## §D · Corrections to plan/ledger/audit claims

1. **READING-LEDGER.md's kinds-type.js account is accurate** — I confirm the `layout` valueSlot
   enum vs. solver-implemented-set drift at kinds-type.js:50 exactly as recorded ("a small
   declaration/implementation drift"). No correction needed.
2. **READING-LEDGER.md's glyphic-type.js account is accurate** — the `sub()` axis-subscription
   pattern, whole-unit slots, sockets, conditions all match my full read exactly.
3. **ADVISOR-AUDIT.md §1's file count "13" for app/registry is correct** (I count 13: SaveAsTypeModal,
   components-type, conditions, glyphic-type, kinds-type, relationships-seed, types-adapter,
   types-core, types-hooks, types-seed, types-thumb, types-ui, types-vi). Byte total in the audit
   (134,880) is close to my own sum (~134.9K) — confirmed, no correction.
4. **NEW finding not in any prior doc**: the ADVISOR-AUDIT and READING-LEDGER both focus on
   types-core/types-seed/conditions/glyphic-type/kinds-type as "the registry" but never mention
   `components-type.js`'s orphan status, `types-adapter.js`'s legacy-bridge design, or the `ax()`
   vs `sub()` duplication. These are new, first-hand findings from this pass, not corrections to
   existing claims — the prior passes genuinely didn't reach these files (consistent with the
   ledger's own "partially read" admission for this directory).
5. **CRITERIA G3.4** ("no second edge registry / no second meaning store created — verified by grep")
   — I extend this: there is also no second TYPE registry (`CV_HOST` does not exist as an object
   anywhere in the codebase; it's referenced only in ROADMAP.md's PHASE A prose as a FUTURE
   `CV_HOST.registerKind` — grepped, zero hits for `window.CV_HOST` or `CV_HOST =`). ROADMAP A1's
   plan to build `CV_HOST.registerKind(kind, resolverFn)` is describing NEW work, not something
   already there — worth flagging so a future reader doesn't assume it exists.

## §E · Inputs for PHASE RECONCILE (R1-R5 — what the Type grammar must respect)

- **R1 (edge law) — ALREADY LANDED here, verified sound.** `types-core.js` normalize() carries
  `{directed, inverse}` (352-353); `relationships-seed.js` mirrors them from `CV_MEANING` (76-101).
  Nothing further needed in this directory for R1.
- **R2 (referent words → profile data)** — no direct touch-point in `app/registry/`; this lives
  entirely in `cv-meaning.js` (outside my territory). No registry-side blocker found.
- **R3 (placement redo, relative laws)** — `kinds-type.js`'s `kind.graph` `layout` valueSlot
  (`enum [force,tree,radial,flow,grid]`, line 50) is DECLARATIVE ONLY and does not encode any
  position/placement logic itself — R3's redo happens in `cv-address.js`/`DiagramSolver.jsx`
  (outside this territory) and will not require a registry-shape change UNLESS the relative-address
  system wants to be expressed as a Type valueSlot (e.g. a `position` axis subscription analogous to
  `sub('form')`) — if so, `glyphic-type.js`'s `sub()` pattern is the ready-made mechanism to extend,
  not a new one to invent.
- **R4 (meaning-shape repairs)** — no direct touch-point in `app/registry/`.
- **R5 (block system read)** — no direct touch-point in `app/registry/`; note for whoever does R5:
  if the upstream block system has its own Type/slot/socket grammar, it should be checked against
  THIS registry's grammar (extends/slots/sockets/valueSlots/conditions) for compatibility BEFORE
  merging, per the unions-not-bridges law — a second, structurally-different Type grammar arriving
  from upstream would be exactly the kind of drift this whole census exists to prevent.
- **The `address` field gap (§C.3) blocks G6.1 directly** — whoever picks up G6 needs
  `types-core.js:normalize()` extended with an `address` field (mirroring the socket-level pattern
  already at line 297) BEFORE a glyphgraph node can resolve through `resolve_address`. This is a
  small, well-scoped, non-destructive addition (add one field to normalize's return object) — safe
  to do independently of R1-R5, no dependency conflicts found.

## §F · PROPOSED PLAN-FILE EDITS (tentative — Tim/lead to confirm before landing)

1. **CRITERIA.md G3.1** — no wording change needed; my independent re-verification agrees with the
   existing note. Could ADD a pointer: "see census/AREA-registry-spine.md §C.3 for the exact
   normalize() field list confirming the gap."
2. **CRITERIA.md — new item under G0 or G3** (tentative id G3.5): *"CV_COND unknown-op handling is
   loud — an unrecognized operator throws rather than silently passing."* Currently conditions.js:95
   is the one soft spot in an otherwise loud-fail system; this is a small, mechanical, low-risk fix
   (one line) that closes a real gap against the standing loud-fail law (ROADMAP's "Standing rules"
   line: "loud-fail (unknown→throw...)").
3. **ROADMAP.md — new PHASE REMAINING bullet** (tentative): *"components-type.js's 11 Types are
   orphaned (zero consumers, no thumb-dispatcher case) — either wire a `react-component` thumbnail
   case + confirm the compiled-bundle global actually resolves, or explicitly disposition as
   scaffolding-not-yet-wired (not drift, not dead — Tim's 'designed ahead of time' pattern, but it
   needs a decision, not silence)."* This is exactly the class of finding the census team was sent
   to surface, not silently fold in — flagging for the lead/Tim rather than unilaterally wiring it,
   since it touches the compiled bundle (a traps-section landmine per this project's own CLAUDE.md).
4. **DESIGN-LANGUAGE.md / README v2** (per ADVISOR-AUDIT §8.1's lockstep directive) — if R1's edge
   law goes into these docs as directed, ALSO add the `ax()`/`sub()` axis-subscription duplication
   (§B2) as a "known small duplication, not yet unified" note, so it doesn't silently re-diverge
   further as components-type.js grows.

---
**Coverage note**: all 13 files in `app/registry/` read in full (100% of directory by file count and
byte weight, ~134.9K). Cross-directory greps (not full reads) touched `assets/icons/cv-meaning.js`,
`assets/icons/glyphgraph.js`, `axes/*`, `system/type-system.html`, `app/index.html`,
`app/canvases/TypeBuilder.jsx`, `app/canvases/RegistryInspector.jsx`, `_demo/verify_g3.js`,
`_demo/verify_g2_4.js` — consumer-tracing only, not first-hand full reads; flagged as such throughout.
