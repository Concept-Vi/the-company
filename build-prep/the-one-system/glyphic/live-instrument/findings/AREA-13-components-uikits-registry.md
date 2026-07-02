# AREA-13 — Components, UI-kits, and Registry depth (wave-2 coverage)

> Wave-2 COVERAGE agent. Territory: `components/` (the React component library + `Glyphic.jsx`),
> the **registry depth** wave-1 only skimmed (`app/registry/*`), and `ui_kits/` (vi · platform ·
> virtual-hub). Goal: tell the live-instrument build what is **design-system-grade reusable** vs
> **disposable**, where the Glyphic socket already lives, and where the registry grammar already
> has (or lacks) the hooks the live layer needs. Evidence marked **Observed (file:line)** /
> **Inferred** / **My-idea**. I correct the brief where it named files that don't exist.

---

## 0 · Brief corrections (what's actually on disk)

The dispatch brief named several files/components that **do not exist**. Correcting up front so the
synthesis isn't built on phantoms:

- **Components that DON'T exist:** `Popover`, `Select`, `Tooltip`, and `controls-live.html` are **not
  in `components/`**. (Observed: `ls components/` — the dir has Avatar, Badge, Button, Card, Glyphic,
  Input, Modal, Segmented, Stepper, Switch, Tabs + their `.d.ts` + `component-library.html`.) A
  *tooltip* and a *select* exist only as **CSS classes** (`.cv-tooltip`, `.cv-select`) shown in
  `component-library.html:160,81` — there is no React component wrapping them. `Input.jsx` renders
  `<select class="cv-select">` when `as="select"` (Observed: `components/Input.jsx:15`), so "Select"
  is a *mode of Input*, not its own component.
- **Registry files that DON'T exist:** `actions`, `events`, `decorators`, `vars`, `views`, `query`,
  `project`, `types-seed` was the only one of several named that's real. The **actual**
  `app/registry/` is: `conditions.js`, `components-type.js`, `glyphic-type.js`, `kinds-type.js`,
  `relationships-seed.js`, `types-adapter.js`, `types-core.js`, `types-hooks.js`, `types-seed.js`,
  `types-thumb.jsx`, `types-ui.jsx`, `types-vi.js`, `SaveAsTypeModal.jsx`. (Observed: `ls`.)
  - **There is no events/actions/decorators file because there is no separate event/action model.**
    The event/action concept lives *inside the type schema* as an **event-socket**: a socket with
    `kind:'event'`, `event:'click'`, `onPick:'open'|'insert'`, and an `address` to the occupant.
    (Observed: `components-type.js:128` modal `trigger` socket; `kinds-type.js:40` `onItemClick`;
    `types-core.js:292` `socketInfo()` reads `kind`/`event`/`address`/`onPick`.) This is a genuine
    synthesis point, not a gap — see §2.4.

---

## 1 · The component library — what exists, and is it instrument-grade?

### 1.1 The pattern: every component is a thin token-class wrapper (Observed)

All 11 non-Glyphic components share **one shape**: a tiny function that maps props → a `cv-*` class
string, renders a plain element, and **carries zero literal style values**. The visual lives entirely
in `tokens/controls.css` (referenced, never copied). Concretely:

- `Button.jsx:14-24` — builds `["cv-btn", "cv-btn--"+variant, …]`, renders `<button>` or `<a>`. No color/size literals. (Observed)
- `Card.jsx:15-29` — `["cv-card", "cv-card--"+variant, raised, interactive, pad]` + optional head/foot. (Observed)
- `Badge.jsx:11-17`, `Avatar.jsx:5-11`, `Switch.jsx:6-12`, `Segmented.jsx:5-17`, `Tabs.jsx:6-18`,
  `Stepper.jsx:6-16`, `Input.jsx:10-28`, `Modal.jsx:6-22` — all the same: class-assembly over `cv-*`,
  data-driven (`items`/`options`/`steps` arrays), controlled via `value`+`onChange`. (Observed)

**Verdict — these ARE design-system-grade and the live instrument SHOULD build on them, not bespoke
chrome.** They theme for free (every value is a token via the `cv-*` classes), they are tiny, and
they are uncontroversial. The instrument's surrounding UI (the composer input, send button, the
transcript rail, approve/confirm affordances, mode toggles) maps almost 1:1:
- composer text field → `Input` (`as="textarea"`)
- send / correct / undo → `Button` (variants give the voice)
- listen-mode ⇄ push-to-talk → `Segmented` (it IS the "landing audience toggle" pattern, `Segmented.jsx:1`)
- live/idle/"Vi is listening" → `Badge` (tones map to states, `Badge.jsx` doc) or the kit's `ViStatusPill`
- the extract→resolve pipeline stages → `Stepper` (done/active/upcoming, `Stepper.jsx:11`)
- a confirm-before-mutate dialog → `Modal` (`Modal.jsx`, controlled `open`, Esc + backdrop close)
- speaker/entity chips → `Avatar` / `Badge`

(Inferred — the mapping is mine, but each component's stated purpose in its header comment supports
it: Segmented = "landing audience toggle", Tabs = "product dashboard tabs", Stepper = "linear
numbered progress".)

### 1.2 Two honest gaps for an instrument surface (Observed absence)

- **No overlay/floating primitive beyond Modal.** No Popover, no Tooltip-as-component, no
  anchored-panel. A live canvas wants a node-context popover ("rename", "change relation", "why this
  glyph?"). That is a **build**, and it should be a new token-class wrapper (`.cv-popover`) + a
  `component.popover` Type, *not* inline-styled in the canvas. (Observed: none exist.)
- **No list/feed/scroller component.** The transcript and the narration log need a scrolling list;
  today every kit hand-rolls it (e.g. `ChatPanel.jsx:82` does `ref.current.scrollTop = scrollHeight`
  inline). (Observed.) Minor, but flag it so it lands as a primitive, not a copy.

### 1.3 `Glyphic.jsx` — the React socket around the one renderer (Observed — the key anchor)

This is the single most important file in my territory for the live instrument.

- `Glyphic.jsx:25-31` assembles a **facet-spec** from props (`form, symbol, fill, texture, motion,
  depth, size, color:{ring,symbol}`, optional `value`) and calls **`window.CV_GLYPHIC.compose(spec,
  {size})`** — it does **NOT redraw**; it asks the single composition source for `{svg, motionClass}`
  and injects the SVG. (Observed: `Glyphic.jsx:53-61`.)
- If `CV_GLYPHIC` isn't loaded it renders a **labelled dashed placeholder**, never a blank
  (Observed: `Glyphic.jsx:33-51`) — graceful but loud-ish, the right pattern.
- The `.d.ts` is a precise contract: form enum, symbol = a `CV_ICONS` id, fill/texture/motion/depth
  enums, `value` = "an allocated value … colours via the active meaning profile". (Observed:
  `Glyphic.d.ts:17-38`.)

**This is exactly the seam the reactflow/tldraw custom-node needs.** A live-canvas node's render body
can BE `<Glyphic … />` (browser-side compose) OR — per wave-1's backend-owns-truth decision — the
server can call the same `CV_GLYPHIC.compose` and the FE node reflects the resolved SVG string. Either
way **the renderer already exists and is single-sourced**; the live layer must not write a second
glyph drawer. (My-idea, but grounded in `Glyphic.jsx:53` + `CV_GLYPHIC.compose` at
`assets/icons/cv-glyphics.js:232`.)

**Two CV_GLYPHIC entry points exist** (Observed: `cv-glyphics.js:232 compose`, `:287 render`,
`:306` an edge/relation render path). `compose(spec)` → `{svg, motionClass}` for a single glyph;
there's also a relation/edge resolver (`:315 EDGES.resolve(rel.edge)`). So **the engine already knows
how to render an edge between two glyphics**, not just a node — directly relevant to the glyphgraph
canvas. (Observed; I did not trace the full edge-render output.)

---

## 2 · Registry DEPTH (the part wave-1 skimmed)

The registry is **deep and genuinely resolution-native** — this is the strongest evidence for the
GOVERNING LAW being already-honoured at the type layer. Five things matter for the live instrument:

### 2.1 `conditions.js` — `CV_COND`, the one condition evaluator (Observed — reusable as-is)

A single shared evaluator that gates whether a slot is enabled / a socket accepts / a declaration
applies. (Observed: `conditions.js:7-20`.) Three input forms all normalise to one eval: structured
`{field,op,value}`, a string DSL (`"texture requires fill != none"`, `"size >= md"`), or a predicate
function. (Observed: `conditions.js:13-19`, ops list `:24-37`, `"A requires B"` sugar `:59-62`.)
Public API: `test / testAll / failures / normalize`. (Observed: `:99-117`.)

**For the live instrument:** when an extracted entity resolves to a glyphic, the rules that govern
*which facets are legal* (`"texture requires fill != none"` is already a real glyphic condition —
Observed `glyphic-type.js:55`) are evaluated by **this** evaluator. The NL→glyphgraph composer should
run candidate specs through `CV_COND.testAll` so it can't produce an illegal glyph. **Reuse, don't
reinvent.** (My-idea; grounded.)

### 2.2 `types-core.js` — `CV_REGISTRY`, the inheritance + acceptance grammar (Observed — the spine)

This is the universal Type registry: layers `token→atom→block→system→surface→doc→template`
(Observed `:45`), single-inheritance via `extends` with `resolve()` flattening root→leaf
(Observed `:194-212`), and **`accepts(slot, type, ctx)`** — the load-bearing function for a live
graph. (Observed `:249-273`.) It supports **classification-based acceptance** (a socket lists the
classifications it admits; a type lists what it's classified as), `forbid`, `layers`/`families`/`tags`
filters, AND **socket-level conditions evaluated through `CV_COND`** (Observed `:253`). `socketInfo()`
exposes the event-socket fields (`kind/event/address/onPick`, Observed `:292-304`).

**For the live instrument:** when the composer wants to know "can this extracted node fill that
socket / can this relation join these two glyphics", the answer is **already computable** —
`candidatesForSocket(socket, ctx)` (Observed `:279`) returns every Type that fits, with no bespoke
wiring. This is the registry-native validation the no-staleness law wants, *already built*. The
glyphgraph validator should call `accepts()` rather than hand-checking. (My-idea; grounded.)

### 2.3 `kinds-type.js` — the glyphgraph KIND is already declared (Observed — corrects the anchor)

The anchor/LIVE-INSTRUMENT treat the graph canvas as a fresh build. **At the type layer it already
exists as a declared kind.** `kind.graph` (Observed `kinds-type.js:46-58`) declares: a `nodes` socket
`accepts:['glyphic','atom','block']`, an `edges` socket `accepts:['relationship']`, a `layout`
value-slot (`force/tree/radial/flow/grid`), and **`runtime:{kind:'engine', key:'DiagramSolver'}`**.
There is also `panel.composition-menu` (`:25-44`) whose `items` socket accepts `['glyphic','atom',
'control']` — the "compositional template menu panel" — and `kind.slide-system` (`:59-72`).

**So the live canvas is not a new kind — it's a new RUNTIME for an existing kind.** Today
`kind.graph.runtime.key === 'DiagramSolver'` (the SVG solver, `core/DiagramSolver.jsx`). The
reactflow/tldraw live surface is a **second runtime for the same declared `kind.graph`** — which is
exactly the resolution-native shape: the *what* (nodes accept glyphics, edges accept relationships)
stays single-sourced; only the *how it's drawn live* is new. (Inferred from the `runtime` field
pattern + `RenderType`'s runtime-key dispatch; see §2.6.)

### 2.4 `relationships-seed.js` — the edges placeholder is FILLED, reconciled from real homes (Observed)

`kind.graph`'s `edges` socket `accepts:['relationship']` was an **unfilled placeholder** (no
relationship Types existed). `relationships-seed.js` fills it: every edge-kind becomes a first-class
Type `relationship.<kind>` with `classification:['relationship']` and `source`/`target` sockets that
accept node classes. (Observed `:99-129`.) Crucially it **does NOT re-author meaning** — it reconciles
the id list live at seed-time from **`CV_EDGES.ids()` ∪ `CV_MEANING` edge.* operator fields**
(Observed `:49-70`), and pulls each relation's `means`/`symbol`/`look` from those existing homes
(Observed `metaFor` `:74-97`). This is the no-staleness law worked correctly: the relation TYPES are
derived, the meaning stays single-sourced.

**For the live instrument — this is the directly-relevant part of the EXTRACT→RESOLVE→edges stage.**
When a small model extracts a relation ("the buyer is interested in the apartment"), the resolver maps
`edge.kind` → `relationship.<kind>` (Observed: the brief in `:28-30` says `validateGlyphgraph` does
exactly this map), and `accepts()` on the source/target sockets rejects an endpoint that isn't a valid
node class (Observed `:120-125`). **An unknown edge kind throws — loud, never silent** (Observed: doc
comment `:23`). The live layer's relation-resolution is therefore *already specced as a registry
lookup*, not a new mechanism.

### 2.5 `types-vi.js` — AI authoring of Types is already a registry move (Observed — the dual-author precedent)

`CV_TYPES_VI.proposeType / promoteInstance / suggestSlots` (Observed `:205`) drive the AI side of
authoring: given a brief, Vi returns a JSON Type spec (validated, `:111`), executed via
**`CV_AI.execute('type.propose', …)`** (Observed `:109`). It feeds Vi a **compact live catalogue** of
registered Types it may reference in `slot.accepts` (Observed `:61-62`) — so AI-authored types compose
with existing ones by construction.

**For the live instrument:** this is the **template** for "the AI authors the living surface." The
NL→glyphgraph composer is the same shape as `proposeType` — an `CV_AI.execute(...)` call returning a
structured spec validated against the registry — just targeting glyphgraph nodes/edges instead of
Types. Wave-1's "RESOLVE composer (G-L4)" should be built in this idiom (one `CV_AI` capability with a
`run`, returning structured output), NOT a bespoke parser. (My-idea; grounded in the `proposeType`
shape.) Note the **dual-author** discipline is already here: `provenance:'vi'` vs `'user'` (Observed
`types-core.js:323-348`, `:129`) — the same surface is authored by both, exactly the two-way authoring
the live vision wants.

### 2.6 `components-type.js` — TOTAL COMPONENT COVERAGE, but the render path is INERT (Observed — a real finding)

`components-type.js` registers every React component as a universal-component Type with
classification, value-slots (enum props inline, axis-backed props pointing at the axis), sockets, and
conditions. (Observed `:33-132`.) Each gets `runtime:{kind:'react-component', global: NS+'.'+Name}`
(Observed `:136`). This is the repo's law made literal: "the interface is a projection of the
registries."

**BUT — verified, not inferred — nothing renders a `react-component` Type from the registry.**
- `grep react-component` across `core/` + `app/` returns **only the registration site**
  (`components-type.js:15,136`) — no consumer. (Observed.)
- `RenderType.jsx`'s `typeToNode` dispatches on **`layer`/`family`**: `surface/deck-slide` →
  archetype builder, `doc` → slide sequence, `system|surface/widget` → widget node, else →
  `blockToNode` (the WS_BLOCKS *atom* vocabulary). (Observed `RenderType.jsx:104-133`.) There is **no
  branch reading `runtime.kind === 'react-component'` or `runtime.global`.** A `component.button` Type
  fed to `RenderType` falls through `keyOf → "button"` to `blockToNode`'s `case "button"` which
  returns an atom `chip` (Observed `RenderType.jsx:48`) — i.e. it renders the *wrong* thing, not the
  React `Button`.
- `Components.jsx` (the Studio's component gallery) does **not** read the registry at all — it has its
  own hand-authored `COMPONENT_GROUPS` literal (Observed `Components.jsx:9-37`); `grep CV_REGISTRY`
  in it is empty (Observed).

**So `components-type.js` is a registry *catalogue* (queryable, gives the composition-menu its
candidates) but is NOT a live render path.** This is the one place in my territory where the
"projection of the registries" claim is **catalogue-only, not render-only-from-one-source** — a
latent staleness seam: edit `Button.jsx` and the `component.button` Type's declared slots don't
update (they're hand-listed at `:39-43`), and *nothing* renders the component *through* the Type.

**Why it matters for the live instrument:** the live canvas wants to drop **controls** (a button, a
switch) onto/around glyphic nodes via the composition-menu (`panel.composition-menu` accepts
`'control'`, Observed `kinds-type.js:37`). The candidate list works; **the render does not**. If the
live surface needs to instantiate a registered component, it must build the missing
`runtime.kind:'react-component'` dispatch (resolve `runtime.global` → the window component → render
with the value-slots as props). This is a **small, in-scope build** that also *closes* the staleness
seam — and it's the same "render-from-data" discipline wave-1 named for glyph nodes, applied to the
control layer. (Observed gap + My-idea fix.)

> **Framing note (not a wave-1 contradiction):** wave-1's "render-from-data / one generic node-type /
> kill the per-type branch" was about the **live glyphgraph nodes** (server-composed glyph). My finding
> is a *different axis* — the **React component library's registry projection** in this repo, tied to
> the repo's own law. They don't conflict; they're parallel instances of the same principle, one
> already-clean (glyphic via `compose`) and one half-wired (components via inert `runtime`).

### 2.7 The rest, briefly (Observed)

- `glyphic-type.js` — registers the Glyphic + its three part-types (ring/symbol/fill) declaring
  **STRUCTURE only**; slot vocabularies are read **live from `CV_GLYPHIC.facets`** via `sub(axisId)`
  subscriptions — "there is no second list of forms/fills/textures here" (Observed `:7-9,29-33`). The
  reference worked example of the slots/sockets/parts grammar. Exposes `R.glyphic.valuesFor(facet)`
  (Observed `:115-118`).
- `types-hooks.js` — reactive React hooks (`useTypes/useType/useResolvedType/useLineage/useChildren`)
  that re-render on any registry change via `R.subscribe` (Observed `:11-44`). The live canvas's React
  store can subscribe the same way — the registry is already a reactive source.
- `types-ui.jsx` — shared registry-UI primitives (`TypeCard/TypeChip/TypeTree/TypeFilterBar/
  TypeSlotList/SlotAcceptsHint`) — these are the **browser/inspector** pieces, reusable for a
  "what can I place here" palette in the live instrument. (Observed `:247-251`.)
- `types-adapter.js` — bridges the registry → legacy global arrays (WIDGET_KINDS etc.); registry is
  source-of-truth, legacy arrays are mirrors (Observed `:7-9`). Not instrument-relevant; flags that
  some consumers still read legacy mirrors.
- `types-seed.js` — seeds tokens/atoms/blocks/systems/surfaces/docs (Observed via grep: `token.color.*`,
  `atom.*`, `block.*`, `system.widget.*`, `surface.wizard-step.*`, `surface.deck-slide.*`, `doc.*`).
  The breadth of real surfaces; confirms the property/wizard/hub/deck domain the instrument narrates.
- `SaveAsTypeModal.jsx` — the review-before-commit step for a Vi-extracted Type draft (Observed). The
  "correct it before it lands" affordance — directly the shape the **voice-correction loop** wants for
  a node ("no, that's wrong — fix").
- `kinds-type.js` `runtime:{kind:'engine', key:'DiagramSolver'}` is the precedent that a kind names its
  rendering engine; `RenderType.jsx:119` dispatches `runtime.key` for deck-slides, so the
  **runtime-key dispatch pattern exists** even though the `react-component` *kind* isn't wired. A live
  graph runtime would register as a new engine key. (Observed.)

---

## 3 · `ui_kits/` — real product UIs or references? (Observed)

**Verdict: they are hand-built, self-mounting DEMO apps — high-fidelity *reference* surfaces, NOT a
reusable component layer for the instrument.** Each is a full `index.html` + self-mounting
`ReactDOM.createRoot` app with its own CSS file and bespoke components. They show *how the product
looks*; they are not imported by anything. (Observed: each has its own `index.html`, `*.css`, and an
`App.jsx`/`*App.jsx` ending in `if (_mountApp) ReactDOM.createRoot(...).render(...)` —
`ViKitApp.jsx:239`, `PlatformApp.jsx:43`.)

- **`ui_kits/vi/`** — **the most instrument-relevant kit.** A three-pane "Vi Workspace": left
  **Conversation** (`ChatPanel.jsx`), centre **Task tree** (the 3-layer agent architecture live),
  right **Output preview**. (Observed `vi/README.md:5-15`, `ViKitApp.jsx:184-235`.)
  - **`ChatPanel.jsx` is the closest existing surface to the live-instrument's conversation pane**:
    a scrolling message list (`vi-msgs`, auto-scroll `:82`), a composer with Enter-to-send /
    Shift+Enter-newline (`:88-94`), a disabled "Vi is working…" state (`:89`), and Vi-side affordances
    — `ReadCard` ("Reading/Read <entity>"), `MissingPrompt` (inline gap-fill question + input),
    `ApproveCard` (approve a result). (Observed `ChatPanel.jsx:17-101`.)
  - **This is a borrowable interaction *pattern*, not borrowable code**: it's `cv-*`-styled but
    self-contained (`vi.css`), uses **emoji** for entity icons (`ChatPanel.jsx:5-14` — a disposable
    shortcut, *not* the glyphic system), and is wired to a scripted step demo (`ViKitApp.jsx:60-93`).
    The live instrument should **rebuild this pane on the real components** (`Input`+`Button`+a new
    list primitive) and replace the emoji with `Glyphic`. (Observed + My-idea.)
  - `ViMark` (the diamond avatar with pulsing-line-fill "thinking" animation) and `ViStatusPill`
    ("Vi is reading…", "Vi found 2 missing fields") are **directly reusable patterns** for the
    instrument's "listening / extracting / composing" live state. (Observed `vi/README.md:19-24`.)
  - The **Task tree** pane (Layer 1 plans / Layer 2 spawns clones / Layer 3 executes) is a literal
    visualisation of Tim's **extraction-vs-judgment** law and the concurrent-extract pipeline —
    a ready-made reference for showing the live extract swarm. (Observed `ViKitApp.jsx:14-41`.)

- **`ui_kits/platform/`** — the creator dashboard (sidebar nav + screens: Gallery/Calendar/BrandKit/
  HubSettings). (Observed `platform/README.md`, `PlatformApp.jsx:13-33`.) Reference for *where the
  instrument lives* in the product, not reusable for the canvas. README lists components
  (Checkbox/Dropzone/MediaTile/SectionPanel) that exist only as kit-local files, **not** in the
  shared `components/` library — confirming kits are siloed demos.

- **`ui_kits/virtual-hub/`** — the buyer-facing immersive panotour viewer (dark overlay UI over a
  full-bleed render). (Observed `virtual-hub/README.md`.) This is the **domain the instrument
  narrates** (a property, its rooms, captures, comments) — useful as *content reference* (what the
  glyphgraph is about), not as instrument chrome.

**Net on kits:** treat all three as **disposable reference** for look/interaction, with **one
exception of value**: the `vi/` kit's *interaction model* (conversation + live task tree + output
preview, with read/missing/approve affordances) is the **closest prior design to the live
instrument's own three-zone shape** (talk · watch-it-build · the graph). Mine it for UX, rebuild on
the real components + Glyphic. (Observed + My-idea.)

---

## 4 · What this means for the live-instrument build (grounded)

**Reuse (already design-system-grade, single-sourced):**
- The **11 token-class components** as the instrument's surrounding chrome (composer, send, mode
  toggle, status, stepper, modal). They theme for free. (§1.1)
- **`Glyphic.jsx` + `CV_GLYPHIC.compose`** as the live-canvas node body — the one glyph renderer
  already exists, incl. an edge/relation render path. **Do not write a second drawer.** (§1.3)
- **`CV_COND`** for legal-facet/legal-edge validation of composed specs. (§2.1)
- **`CV_REGISTRY.accepts / candidatesForSocket`** for "can this node/edge go here" — registry-native
  validation, no bespoke graph rules. (§2.2)
- **`kind.graph` + `relationship.*` Types** — the glyphgraph's node/edge grammar is **already
  declared and filled**; the live canvas is a *new runtime for an existing kind*, not a new kind. (§2.3, §2.4)
- **`CV_TYPES_VI.proposeType` shape** as the template for the NL→glyphgraph composer (one `CV_AI`
  capability, structured output, validated against the registry). (§2.5)
- **`types-hooks` `R.subscribe`** so the canvas React store reacts to registry changes natively. (§2.7)
- The **`vi/` kit interaction model** as the UX reference for the three-zone instrument. (§3)

**Build (genuine gaps, all in-scope, none a new mechanism):**
- A **new live runtime/engine for `kind.graph`** (the reactflow/tldraw surface) registered as a
  runtime key, parallel to `DiagramSolver` — the *how-drawn-live*, the *what* stays single-sourced. (§2.3)
- The missing **`runtime.kind:'react-component'` dispatch** if the canvas instantiates registered
  controls — resolve `runtime.global` → window component → render with value-slots as props. Closes
  a latent staleness seam *and* gives the live layer a render-from-registry control path. (§2.6)
- A **Popover/anchored-panel primitive** (`.cv-popover` token-class + `component.popover` Type) for
  node context actions, and a **list/scroller primitive** for the transcript — built as primitives,
  not inline-styled in the canvas. (§1.2)
- Rebuild the **conversation pane** on `Input`+`Button`+the new list primitive, replacing the kit's
  emoji entity-icons with `Glyphic`. (§3)

**The no-staleness watch (where hardcoding would sneak in, in my territory):**
- The `component.*` Types **hand-list their slots/enums** (`components-type.js:39-43`) — these can
  drift from the actual `.jsx` props. If the live layer leans on these, derive them or accept the
  drift consciously. (§2.6)
- The kits use **emoji and inline styles** freely (e.g. `ChatPanel.jsx:5-14,33-39`) — they're demos,
  but do not copy those literals into the instrument. (§3)

---

## 3-line summary

1. The 11 components are **design-system-grade thin token-class wrappers** the instrument should build
   on; `Glyphic.jsx` is the **React socket around the one `CV_GLYPHIC.compose` renderer** (incl. an
   edge-render path) — the exact seam the live-canvas node needs, never re-drawn.
2. The **registry is deep and resolution-native**: `kind.graph` + filled `relationship.*` Types
   already declare the glyphgraph's node/edge grammar (the live canvas = a *new runtime for an existing
   kind*); `CV_COND` + `CV_REGISTRY.accepts` + the `CV_TYPES_VI.proposeType` shape give the
   composer/validator for free — **BUT `components-type.js` is a catalogue-only projection: verified
   that NO renderer dispatches its `runtime.kind:'react-component'`, a latent staleness seam to close.**
3. The **three `ui_kits/` are disposable demo apps** (self-mounting, siloed CSS, emoji); reuse only the
   **`vi/` kit's interaction model** (conversation · live task-tree · output-preview, with read/
   missing/approve affordances) as the UX reference — the closest prior design to the instrument's
   three-zone shape — then rebuild on the real components + Glyphic.

Path: `/home/tim/company/design/claude-ds/analysis/glyphic-language/live-instrument/findings/AREA-13-components-uikits-registry.md`
