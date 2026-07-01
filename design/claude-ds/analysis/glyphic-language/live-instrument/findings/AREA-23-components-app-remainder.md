# AREA-23 — Components / App / Surface / Icon remainder (coverage agent)

**Lens applied (Tim):** nothing canonical/final; duplications KEPT + catalogued by **unique quality** (fuse-not-pick, never "which wins"); **descriptive** — the "verdict" of design-grade vs scaffolding is rendered through the code's **own self-descriptions** (`@ds-adherence-ignore`, `⚠️ DEPRECATED`, `window.`-exposure), not a bare opinion. Every claim marked **Observed (file:line)** / **Inferred** / **My-idea**.

**Coverage honesty (per repo `coverage:` convention):**
- **Read in full (line-level):** all 10 `components/*.d.ts`; `assets/icons/ConceptVIcon.jsx`, `CvIcon.jsx`, `cv-vi-glyph.js`; `components/Glyphic.jsx` + `app/components/ViShape.jsx` (pulled in to complete the Vi-mark drawer comparison); `app/components/CanvasHeader.jsx`, `ExportPatch.jsx`, `ImageEditor.jsx`, `MaskEditor.jsx`, `Pano360.jsx`; `app/canvases/Icons.jsx`; `app/registry/types-thumb.jsx`; `atomicity/Ingest.jsx`; `tweaks-panel.jsx`; `_demo/glyphic-board.html`.
- **Read to signature/structure level (NOT every line):** `app/canvases/Workshop.jsx` (1905 lines — top + lines 143–502 read; the deck/section internals 503–1905 read at function-signature level via grep). Bounded deliberately: Workshop is a document composer, relevant only as an interaction precedent.
- **Characterized, not line-read:** `assets/icons/icon-paths.js` (155 entries, deprecated), `assets/icons/index.html` (icon-explorer page), `atomicity/atomicity.css` (73KB — grepped for graph/node/edge/canvas/glyph/pin terms; characterized below).
- **Cross-referenced but OTHER agents' territory (not deep-read):** `assets/icons/cv-shapes.js`, `cv-glyphics.js`, `cv-icons.js`, `cv-meaning.js`, `glyphgraph.js`, `cv-edges.js`, `core/DiagramSolver.jsx`.

---

## PART (a) — What each thing is + design-grade-reusable vs disposable (via self-description)

### The 10 component `.d.ts` (the typed design-system component surface)
These are **type-only declaration files** (`export declare function …`) — the public contract of the welded component library; the implementations live in the compiled bundle (`_ds_bundle.js`, per `claude-ds/CLAUDE.md` §5). All are **design-grade**: each prop maps to the brand's token/voice vocabulary, none carry literals.
- **Avatar.d.ts** (Observed 1–11): circular avatar, photo or initials, `gold` variant, `size` number|css-length.
- **Badge.d.ts** (Observed 1–14): status label; `tone` ∈ gold·success·warning·error·comm; `dot`; tone "maps to a system voice or state."
- **Button.d.ts** (Observed 1–23): `variant` ∈ primary·ink·outline·ghost·soft·comm·default — comment ties each to a **source button vocabulary** ("gold decision voice", "sage relationship"); `pill`/`block`/`icon`/`as`/`href`.
- **Card.d.ts** (Observed 1–18): surface card; `variant` soft·surface·outline·gold; `raised`/`interactive`/`pad`; header(title/sub)+footer slots.
- **Input.d.ts** (Observed 1–18): form field; `as` input·textarea·select; `label`/`hint`/`error` wraps it in `.cv-field`; "gold focus ring from the source composer."
- **Modal.d.ts** (Observed 1–11): warm-dim backdrop + raised panel; controlled `open`; closes on backdrop/Escape/close-button.
- **Segmented.d.ts** (Observed 1–10): 2–3 option toggle, "the audience toggle"; active option lifts onto a surface.
- **Stepper.d.ts** (Observed 1–10): linear numbered stepper; steps before `active` show gold ✓.
- **Switch.d.ts** (Observed 1–8): on/off; "track turns gold when checked (gold = active voice)."
- **Tabs.d.ts** (Observed 1–10): dashboard tab bar; active tab gets gold underline.

**Glyphgraph bearing:** these are the **chrome** a live-instrument UI is assembled from (the toolbars, the per-node inspector panels, the audience toggles), not the node-render itself. `Segmented`/`Switch`/`Stepper`/`Tabs` are the facet-control vocabulary a node-editor side-panel would reuse.

### Icon / Vi-mark drawers — see PART (b) (the centerpiece duplication).

### `app/components/CanvasHeader.jsx` (Observed 1–13)
Trivial shared header (`title`/`sub`/`actions` → `.dsa-canvas-header`). **Design-grade reusable**, used by every canvas incl. `Icons.jsx:180`. A live-graph surface would reuse it for its header bar.

### `app/components/ExportPatch.jsx` (Observed 1–137)
Modal that turns in-browser Studio edits (generated icons, palette edits, token edits) into **copy/download code patches** targeting the real DS files (`assets/icons/cv-icons.js` :8, `colors_and_type.css` :31/57). **Design-grade**, but note: it's the **manual** bridge from browser state → source files (clipboard/download), NOT a live write-back. (Inferred: the no-staleness law lives in the real DS scripts; Studio edits are a staging area the human reconciles.)

### `app/components/ImageEditor.jsx` (Observed 1–340) + `MaskEditor.jsx` (Observed 1–210) + `Pano360.jsx` (Observed 1–248)
The **imagery editing suite** — largely orthogonal to glyphgraph, with two exceptions noted in (c):
- **ImageEditor**: full-screen crop/adjust/filter/rotate sheet; AI-edit tab routes through `window.CV_AI.resolveProvider('openai-image').editImage(...)` (Observed 159). The **one** load-bearing line for the live layer: this is the established `CV_AI.resolveProvider(id)` call-site pattern (the provider abstraction the anchor §4 wants to extend).
- **MaskEditor**: canvas brush mask → PNG alpha for OpenAI `images/edits` (Observed 1–13, 89). Self-contained.
- **Pano360**: equirectangular 360 viewer; **loads three.js from `https://unpkg.com/three@0.160.0` at runtime** (Observed 13). This is a **live external-CDN script injection** — directly relevant to the anchor's open worry "reactflow inside the no-script-CSP / bundle." It proves the app currently *does* inject external scripts on demand (so CSP is NOT presently blocking that here); it falls back to a static preview on load failure (Observed 198–201). Hotspot interaction details → (c).

### `app/canvases/Icons.jsx` (Observed 1–338)
The Icons canvas: a categorized icon library (9 hardcoded `ICON_CATEGORIES` :4–14) + **live AI generation** (`generate()` :44 → `CV_AI.complete(prompt)` → parse JSON proposals → `adopt()` :82 writes into `window.CV_ICONS.data` live + `addGenerated`). Also `refineIcon` (:101), `duplicateIcon` (:138), `deleteIcon` (:172). **Design-grade as a surface**, but `ICON_CATEGORIES` is a **hardcoded category map** (Observed 4–14) — a no-staleness pressure point: it's a hand-list parallel to `CV_ICONS.facets`/taxonomy (other agents' territory). Glyphgraph bearing → (c): this is the **generate-on-miss / foundry-adopt-live** precedent.

### `app/registry/types-thumb.jsx` (Observed 1–662)
**Universal thumbnail renderer for any Type** — a layer/family/runtime **dispatcher** (`pickRenderer` :73) that maps every registry layer (token·atom·block·system·surface·doc·template) to a render fn, scaled-to-fit via `ScaledThumb` (:13). **High design-grade** and architecturally important: block/system/surface/deck thumbs render **THROUGH THE ONE ENGINE** (`window.__cvRenderType`, gated on `window.__coreReady` — readiness, not fallback; Observed 216, 263–268, 428–435). Carries `RenderShape` (:614) drawing hex/octagon/diamond/circle as polygons. Glyphgraph bearing → (c): this **per-type render dispatch** + **node-shape geometry** is the single closest in-repo analogue to "a reactflow custom-node that renders per type."

### `atomicity/Ingest.jsx` (Observed 1–173)
AtomiCity's ingest surface: drop/paste source material → `window.CV_SOURCE.recognize/analyze/bringForward` → findings grouped by 6 DNA dimensions (color/type/voice/structure/value/motif, `DIM` :10) → "Bring forward" stages proposals. **Design-grade**; all model work routes through `CV_SOURCE → CV_AI/CV_HOST` (Observed 4–6). Relevant to the live layer as a **proposal-staging interaction** model (extract → propose → human accepts), but on documents not a live graph.

### `tweaks-panel.jsx` (Observed 1–541)
**Self-labeled scaffold:** line 1 `// @ds-adherence-ignore -- omelette starter scaffold (raw elements/hex/px by design)`. A reusable floating **Tweaks shell + form controls** (`useTweaks`, `TweaksPanel`, `TweakSlider/Toggle/Radio/Select/Text/Number/Color/Button`) that owns a `postMessage` host protocol (`__activate_edit_mode`/`__edit_mode_set_keys`, Observed 173–186, 229–238). The defaults reference Claude-brand colors (`#D97757`, Observed 17–22) — i.e. it's the **generic Anthropic "omelette" prototype harness**, NOT the ConceptV design system; raw literals are *by design and self-flagged*. Disposable-as-reference for ConceptV form (per `design/CLAUDE.md` "Company Ui Disposable" spirit), but the **control vocabulary** (segmented/slider/scrub-number/curated-color-chip) is a genuine reusable pattern for a node-facet editor.

### `_demo/glyphic-board.html` (Observed 1–113)
A standalone **PROPOSAL artifact** (self-labeled line 43: "PROPOSAL to react to … hand-drawn to show the concept + meanings; once you pick, they become real Glyphics facets the engine generates"). Hand-inlined hex/SVG (NOT on the DS — it's a decision-surface for Tim). This is **the most glyphgraph-load-bearing file in my whole territory** → (c).

### `assets/icons/index.html` (characterized)
Icon-explorer page (`<title>ConceptV — Icon Library</title>`, `@dsCard group="Brand"`). A searchable click-to-copy browser over the icon set. Opened from `Icons.jsx:184` ("Open explorer ↗"). Utility/gallery surface.

### `atomicity/atomicity.css` (characterized, 73KB)
Self-described header (Observed 1–9): "AtomiCity is built FROM the ConceptV system … Every value is a token … No raw colour/shadow/easing literals — only layout geometry." **Design-grade, fully tokenized** chrome for the AtomiCity surfaces (`.ac-*`, `.ig-*`, `.ex*`, `.fz2-*`, `.k-*`). **No glyphgraph/reactflow machinery:** the grep hits for node/edge/canvas/hotspot are `--vi-edge` (a *border-color token*, not a graph edge), `.ac-tnode` (a type-tile, Observed 121), `.ex3-canvas` + selectable product-card hotspots (a selection demo, Observed 608–621). Confirmed: this CSS does NOT touch node/edge graph render.

---

## PART (b) — The Vi-mark / icon drawers: FIVE members, catalogued by axis (fuse-not-pick)

The task named four ("ConceptVIcon vs CvIcon vs cv-vi-glyph vs Glyphic.jsx"); reading them surfaced a **fifth** (`ViShape.jsx`). They are NOT redundant copies to dedupe — they sit on **different axes**, and the system's own comments tell you which pairs are genuine drift vs deliberate separation.

| Member | File:line | Axis / unique quality | Backing data home | Self-described status |
|---|---|---|---|---|
| **cv-vi-glyph.js** | `assets/icons/cv-vi-glyph.js:4` | **The Vi mark as DATA** — a single auto-traced path (`CV_VI_GLYPH = {viewBox, w, h, path}`, 5 subpaths). Not a renderer; a glyph definition consumed by `cv-shapes.js → CV_SHAPES.markSVG`. | itself (the path) | "The ONE home for the Vi glyph" (Observed 2) |
| **ViShape.jsx** | `app/components/ViShape.jsx:2` | **A SEPARATE, hardcoded Vi diamond** drawn inline (`polygon points="12,2 22,12 12,22 2,12"` + hatch pattern, optional `animated`). Ubiquitous UI chrome (the "Vi is thinking" mark across Workshop/Icons/ImageEditor/Pano360/Ingest). | none — literal SVG in-file | (no flag — live, widely used) |
| **ConceptVIcon.jsx** | `assets/icons/ConceptVIcon.jsx:2` | **Deprecated icon renderer** over the legacy `window.CONCEPTV_ICONS` list; renders a `?name` placeholder on miss; ships `ConceptVBadge` gold-circle. | `icon-paths.js` (CONCEPTV_ICONS) | "⚠️ DEPRECATED — prefer CvIcon … kept only for back-compat" (Observed 2) |
| **CvIcon.jsx** | `assets/icons/CvIcon.jsx:1` | **The LIVE icon renderer** — tone system (`CV_TONES` :26), brand stroke auto-scale (`cvBrandStroke` :46), **entity-node container shapes** circle/hex/octagon/diamond (User-Portal/Property-Wizard/Virtual-Hub/Vi, :34–43), `filled`, and `desaturated` (a **state-strength** channel, :87). Falls back to `cv-shapes.js` points with a byte-identical literal fallback "keep in sync" (:36–43). | `cv-icons.js` (CV_ICONS) + `cv-shapes.js` | "the single live icon home" (per ConceptVIcon.jsx:2) |
| **Glyphic.jsx** | `components/Glyphic.jsx:4` | **Facet-spec SOCKET** — does NOT redraw; assembles `{form,symbol,fill,texture,motion,depth,color,value}` and calls the ONE composer `window.CV_GLYPHIC.compose(spec)`; loud-ish placeholder if unloaded. The only ES-module (`import React`) drawer. | `cv-glyphics.js` (CV_GLYPHIC) | "React socket around the one renderer" (Observed 4) |

**The fuse-not-pick reading, stated by the code itself:**
- `icon-paths.js:2` + `ConceptVIcon.jsx:2` are a **deprecation pair the system flags but KEEPS** for back-compat ("migrate them to CvIcon and delete this"). That's the duplication the codebase itself catalogues-and-retains — your lens made literal.
- **CvIcon vs Glyphic is NOT duplication** — different altitudes: CvIcon renders a *single symbol in a tone/shape*; Glyphic renders a *composed facet-spec* (a full glyphic = form+fill+symbol+texture+motion). Glyphic *contains* the icon-as-symbol; they nest.
- **ViShape vs cv-vi-glyph IS a latent duplication of the Vi mark** (Inferred): `ViShape.jsx:14` hand-draws a Vi diamond as a literal polygon, while `cv-vi-glyph.js` holds the *traced canonical* Vi path consumed by `CV_SHAPES`. Two homes for "the Vi mark" — one a simplified UI-chrome diamond, one the brand-accurate trace. Catalogued (not resolved): unique quality of ViShape = cheap inline animatable chrome; of cv-vi-glyph = brand-fidelity data for the entity-shape renderer. (Verify against `cv-shapes.js` — other agent's territory.)
- The **hex/octagon/diamond polygon geometry appears in THREE places**: `CvIcon.CV_SHAPE_PTS` (:38, 100×100, sourced from CV_SHAPES with literal fallback), `types-thumb RenderShape` (:614, computed trig, sized), and `_demo` inline SVG. CvIcon defers to `cv-shapes.js` (good); `RenderShape` computes its own (a parallel). Catalogued as a node-shape-geometry duplication.

---

## PART (c) — Bearing on a glyphgraph NODE's render / interaction / click-actions / state (the load-bearing section)

This is why the wave exists. Ordered by directness to "talk → live reactflow glyphgraph."

### 1. `components/Glyphic.jsx` — **this IS the custom-node face** (Observed 1–64)
A reactflow custom-node would wrap exactly this: props → facet `spec` → `CV_GLYPHIC.compose(spec, {size})` → `{svg, motionClass}` → injected. It already accepts `value` (Observed 29) — the data-binding hook — and degrades loud if `CV_GLYPHIC` is absent (Observed 33–51, no silent blank). **The live pipeline's RESOLVE→RENDER step terminates here.** A node's facets (form from type, fill/colour from state, symbol from icon-lookup, per anchor §3) are precisely this prop set. No new renderer needed — the live layer drives Glyphic's props from the extract→resolve pipeline.

### 2. `_demo/glyphic-board.html` — **the node+edge STATE GRAMMAR** (Observed 72–111)
Hand-drawn but it specifies the live-graph's **state model** directly:
- **Node FILL = state** (Observed 72–84): solid-fill-no-icon = "*this* thing, present" · outline-only = "*any* of this kind (a type/class)" · dashed-outline = "could be added here (potential/open slot)."
- **EDGE = state** (Observed 86–95): dashed→ = "potential / can-become" · solid→ = "actual, asserted, holds now."
- **Composed reading** (Observed 97–109): two nodes + one edge read three ways by varying fill+edge-style — "meaning = f(source · edge · target)" (Observed 111).
- The closing flag (Observed 111) names the **engine parts still missing** for this to be generated rather than hand-drawn: a solid-fill + icon-optional node, a **ring stroke-style facet** (solid/dashed), and **edges joining the meaning registry** (so line-style+direction mean by profile, like fill already does). This is the precise spec a live-graph node/edge needs — and it maps onto Glyphic's `fill`/`form` and an edge-facet not yet in Glyphic's props (Observed: Glyphic.jsx has no edge concept — edges are `cv-edges.js`, other agent's territory). **Catalogued gap:** the node-state grammar is designed here; the edge-as-meaning facet is the named missing engine part.

### 3. Workshop — **the click-an-element → regenerate-in-place interaction precedent** (Observed 143–264)
Workshop is a *document* composer, not a graph, but its interaction model is the closest precedent for "click a node, get AI options":
- `window.__cvFieldFocus` (Observed 150) + `WS_FIELD.activate(...)` — clicking an editable leaf in engine output pops a **per-field Vi regen toolbar** anchored to its `getBoundingClientRect()` (Observed 152–157).
- `WS_AI.generateCandidatesStream({doc, target, onCandidate, onDone})` (Observed 199) — **streaming** candidate generation into a central gallery; candidates arrive incrementally (Observed 201–205).
- `pickCandidate` applies via **diff** (`WS_AI.applyDiff`/`invertDiff`, Observed 220–223) onto an **undo/redo snapshot stack** (Observed 266–277, 358–371).
- Transforms route as engine `target`s (`{kind:'doc.transform', instruction}` or `{kind:'field.alternate', angle, context}`, Observed 171–262).
For the live graph: a node's click-action = a `target` (e.g. `{kind:'glyphic.alternate'}`), options stream into a gallery, pick applies a diff to the graph store, undo via the same snapshot pattern. **The mutation/diff/undo machinery is already shaped here.** (Inferred: `WS_AI`/`WS_BLOCKS`/`viDraft` live elsewhere — other agents' territory; signature-level read only.)

### 4. `app/canvases/Icons.jsx` — **the generate-on-miss / foundry-adopt-live precedent** (Observed 44–92)
The anchor's GENERATE-ON-MISS step (§3) has a working precedent: `generate()` (:44) builds a tightly-constrained prompt (24×24, 1.5px stroke, no fills — the on-style constraint), `CV_AI.complete()` returns JSON proposals, `adopt()` (:82) **writes into `window.CV_ICONS.data` live and notifies the parent** (and dedupes name collisions :85–87). Plus `refineIcon`/`duplicateIcon` (per-icon AI mutation). This is exactly "noun with no close icon → foundry draws a new on-style icon → use it live," already running for the icon library. **Reuse, don't reinvent**, for the live layer's miss-handler. (Caveat: it uses raw `CV_AI.complete` JSON-parsing, not the structured-output `glyphic.generate` capability the anchor §7 references — a parallel path to reconcile.)

### 5. `app/registry/types-thumb.jsx` — **per-type render dispatch + node geometry** (Observed 73, 614)
`pickRenderer(type)` (:73) is a layer/family/runtime → render-fn dispatcher — the structural analogue of a reactflow `nodeTypes` map keyed by glyphic type. It renders through the ONE engine gated on readiness (`__cvRenderType`/`__coreReady`, not a fallback — Observed 216) — the no-staleness discipline in a render context. `RenderShape` (:614) computes hex/octagon/diamond/circle polygons — node-container geometry (parallel to CvIcon's `CV_SHAPE_PTS` and cv-shapes.js; see (b)). `ScaledThumb` (:13) fits arbitrary-size renders into a node box — useful for nodes that render full engine output at node scale.

### 6. `Pano360.jsx` — **a genuine canvas-node interaction parallel + the CSP signal** (Observed 21, 112–167, 13)
Not imagery-orthogonal in one respect: it's an interactive canvas with **pinned overlays projected onto a 3D surface** and **double-click-to-add a hotspot** (Observed 112–128: raycast click → lon/lat → `onAddHotspot`), overlays re-projected every animation frame by direct DOM transform to avoid per-frame React re-render (Observed 156–167). That last point is a real **performance pattern for many moving pinned elements on a canvas** — directly transferable to keeping glyphic nodes/labels positioned during a live, growing layout (anchor §6 "stable incremental auto-placement"). And `loadThree()` injecting an external CDN script at runtime (Observed 8–18) is **evidence the app currently injects external scripts on demand** — bearing on the anchor's open "reactflow-in-CSP" worry (it suggests the current runtime is not hard-blocking external scripts here; verify the CSP for the live build separately).

### Provider call-site (the one ImageEditor line that matters): `ImageEditor.jsx:159`
`window.CV_AI.resolveProvider('openai-image').editImage(...)` — the established `resolveProvider(id)` usage the anchor §4 wants to extend so providers resolve by role/id to the Company fleet. A live-layer consumer would call `CV_AI` the same way; the abstraction point is `resolveProvider`.

---

## Catalogued duplications/parallels (fuse-not-pick summary)
1. **Vi-mark, two homes:** `ViShape.jsx:14` (inline animatable diamond, UI chrome) vs `cv-vi-glyph.js` (canonical traced path data for CV_SHAPES). Different qualities; both live.
2. **Icon renderers, deprecation pair the system keeps:** `ConceptVIcon.jsx`+`icon-paths.js` (legacy, flagged) vs `CvIcon.jsx`+`cv-icons.js` (live). Self-catalogued.
3. **Node-shape polygon geometry, three homes:** `CvIcon.CV_SHAPE_PTS` (defers to cv-shapes.js, w/ literal fallback) · `types-thumb.RenderShape` (computes its own) · `_demo` (inline). CvIcon is the un-stale one.
4. **Generate-into-the-system, two paths:** `Icons.jsx` raw-`CV_AI.complete`+JSON-parse vs the structured `glyphic.generate` capability (anchor §7, other agent). Parallel; reconcile.
5. **Hardcoded lists as staleness pressure points:** `Icons.jsx:4` `ICON_CATEGORIES` (parallel to CV_ICONS taxonomy) · `Workshop.jsx:6` `DOC_TYPES` (but mitigated by `useExtraDocTypes()` :20 merging registry doc-types — the no-staleness extension pattern done right).
6. **CvIcon vs Glyphic: NOT duplication** — they nest (symbol-in-tone vs composed-facet-spec). The altitude separation to preserve.

---

## 3-line summary
The glyphgraph node's render face already exists as **`components/Glyphic.jsx`** (facet-spec → `CV_GLYPHIC.compose`), and its **node+edge state grammar** (fill = present/type/potential, edge solid/dashed = asserted/potential) is fully specified in **`_demo/glyphic-board.html`** — which also names the missing engine parts (ring-stroke facet, edges joined to the meaning registry). The **click-element→stream-options→apply-diff→undo** interaction (`Workshop.jsx` `__cvFieldFocus`/`WS_FIELD`/`generateCandidatesStream`), the **generate-on-miss→adopt-live foundry** (`Icons.jsx`), the **per-type render dispatch + node geometry** (`types-thumb.jsx` `pickRenderer`/`RenderShape`), and a **canvas pinned-overlay perf pattern + live external-script injection** (`Pano360.jsx`) are all reusable precedents. The Vi-mark exists in **five members across distinct axes** (data/chrome/legacy-renderer/live-renderer/facet-socket) — catalogued fuse-not-pick, with the deprecation pair (`ConceptVIcon`/`icon-paths.js`) being a duplication the system itself flags-but-keeps.

**Path:** `/home/tim/company/design/claude-ds/analysis/glyphic-language/live-instrument/findings/AREA-23-components-app-remainder.md`
