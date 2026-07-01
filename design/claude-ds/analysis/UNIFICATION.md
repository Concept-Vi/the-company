# UNIFICATION — welding the two halves into one system

> **Purpose of this document & of the current work: unification, not new design.** The system
> was built as TWO disconnected halves that are meant to be one (`grep` confirms zero references
> between them). This file is the critical map of the duplication, the canonical decision that
> resolves it, and the staged weld. It is the deliberate structural decision SYNTHESIS-PLAN §3
> flagged as the keystone. Read with `AXES.md` (the model) + `INTEGRATION.md` (the anti-drift
> token contract) + `app/registry/types-core.js` (the existing type model).

## 0. The finding — two engines for one described system
`AXES.md`/`REQUIREMENTS.md` describe **one** thing: *one type system + one rule engine + two
solvers, computing `f(content, axis-position)` over the invariant DNA.* It exists today as two
halves that never met:

| Half | Where | What it is | What it LACKS |
|---|---|---|---|
| **The type system + generator** | `app/registry/*` (`CV_REGISTRY`, `types-seed`, **`types-vi.proposeType`**), `WS_LAYOUTS`, `WS_BLOCKS` | A real 7-layer atomic-composition model (token→atom→block→system→surface→doc→template) with inheritance, slot-embedding, variables, provenance, AND a Vi generator that proposes new on-DNA Types from a brief. This is the "one type system" + the north-star generator, **already built.** | No `f(content, axis)`. `WS_LAYOUTS` are fixed block arrays; render path is app-only JSX (`WS_BLOCKS`). No LOD/surface/density recompute. |
| **The rule engine + two solvers** | `core/*` (`ContainmentTree`, `DiagramSolver`, `Slide`/`Archetypes`, `cv-nodes`) | The `f(content, axis)` computation: a block solver + graph solver over a shared node type, with LOD pruning, depth-keyed zoning, density/surface dials. | Its own private vocabulary (`CVNode`/`Archetypes`) **disconnected from the registry**; knows nothing of Types, slots, inheritance, or the Vi generator. |

**They are the two halves of the same machine.** The type system has no engine; the engine has no
type system. Nothing bridges them. That gap is the whole task.

## 1. The duplication this produced (what to collapse)
Three parallel lists exist for each concept — the symptom of the missing weld:

| Concept | Strand A (app type model) | Strand B (app composer) | Strand C (core engine) | → Canonical |
|---|---|---|---|---|
| **Archetypes / slide layouts** | `surface.deck-slide.{title,content,section}` Types (3 stubs) | `WS_LAYOUTS` (~24 layouts) | `Slide` + `Archetypes` (13 builders) | **ONE** catalogue of `surface.deck-slide.*` Types; the *renderer* is the archetype builder, run by the solvers. |
| **Atoms / blocks** | `atom.*` + `block.*` Types (point at `runtime:ws-block`) | `WS_BLOCKS` (11 JSX renderers) | `ContainmentTree` atom registry (metric/bullet/hero-number/badge/note/qr/chip/image/text) | **ONE** `block.*`/`atom.*` Type set rendered by the core atom registry. |
| **Tokens / shapes** | `token.*` Types (gold/bronze/ink, circle/hex/octagon/diamond) | — | the L0/L1 CSS tokens + solver shape clips | already single-sourced in CSS; the `token.*` Types are pointers — keep, reconcile values. |
| **Docs (deck/brochure…)** | `doc.*` Types + slots | `WS_*` doc state | `PitchDeck.dc.html` template | doc Type = a sequence of surface(archetype) Types, rendered by the engine. |

The containment ladder and the registry layers are the **same hierarchy** stated twice:

```
AXES containment:   Deck → Band → Section → Zone → Cluster → Atom
CV_REGISTRY layers: doc  → surface → system → block → atom   (+ token below, template above)
core CVNode kinds:  band/diagram → section → zone → cluster → atom
```
→ these three columns are ONE ladder. Unify the names/mapping; do not keep three.

## 2. The canonical decision
1. **`CV_REGISTRY`'s schema is THE type system** (it is the richer, already-load-bearing model — it
   drives the app pickers and the Vi generator). The core's `CVNode`/`CVGraph` are the engine's
   **internal IR**, not a second type system.
2. **The core solvers are THE one rule engine.** Everything renders through them under the axis-dials.
   `WS_BLOCKS` JSX becomes legacy/alias; the canonical renderer is the core atom registry.
3. **The bridge is `typeToNode(type, data, axis)`** — resolve a registry Type (`R.resolve`, with its
   slots/defaults/data) into a `CVNode`/`CVGraph` IR, then hand it to the solvers. One function welds
   the type system to the engine. A `RenderType` component is its React entry point.
4. **The catalogue is single-sourced in the bundle** so templates AND the app share it: the core
   exposes its archetypes + atoms **as registry-shaped Type seeds** (`CoreTypes`). The app's
   `types-seed.js` seeds FROM that catalogue instead of declaring stubs — the 13 archetypes BECOME the
   canonical `surface.deck-slide.*` Types; `WS_LAYOUTS` entries map onto them (annotated, then retired).
5. **`Slide` is just the deck-slide case of `RenderType`** — no parallel archetype registry; the
   archetype builders are the *render functions* of the deck-slide Types (exactly as `WS_BLOCKS[k].render`
   is the render of `block.k`).
6. **Token-purity is unchanged** (INTEGRATION.md): the IR carries only token-backed styles, so
   generated output still cannot drift.

Net shape: **`CV_REGISTRY` (types + Vi generation) → `typeToNode` → core solvers (one engine, axis-dials) → DNA-pure output.** The loop closes: `proposeType` already emits Types in this grammar, so a *generated* Type renders through the same engine — the north star, finally wired.

## 3. Staged weld — STATUS
- **W1 — the bridge: ✅ DONE.** `core/RenderType.jsx` (`typeToNode` + `RenderType`) renders any
  CV_REGISTRY Type through the solvers; `Slide` delegates to it (one render path).
- **W2 — single-source the catalogue: ✅ DONE.** `core/archetype-catalog.js` is the one catalogue
  (now also carrying representative `defaults` per archetype); the app seeds from it; `title/content`
  are `extends` aliases; `WS_LAYOUTS.archetype` / `WS_BLOCKS._atomRole` annotated.
- **W4 — one engine in the app: ✅ DONE.** `app/index.html` now loads `../styles.css` (the full
  token + `core/containers` layer — previously the app had only `colors_and_type.css`) and loads the
  core solvers + bridge **as source** via a strip-and-eval bootstrap (the `data-type="module"` path
  is broken in this Babel build — `targets.esmodules` bug). Sets the `window.__cv*` globals the app
  consumes. Verified: app boots clean, engine renders inside the app (gold `#E0C010`, `.cv-band`).
- **W3 — render through the one engine: ✅ DONE for all preview paths (block · slide · doc · widget-system).**
  `BlockThumb`, `SurfaceSlideThumb`, `DocDeckThumb`/`DocBrochureThumb`, and now `SystemWidgetThumb`
  all render their Type through `RenderType` → solvers. `widgetToNode` expresses a widget system
  (kpi/media/hybrid) as a Zone tile (REQUIREMENTS F2: product UI = the same containment tree) —
  KPIs→metrics, rows→bullets, media/chart→image placeholders, cta→chip. The containment engine now
  spans block → slide → deck/brochure → widget.
  - **Boundaries (correct, not fallbacks):** (a) cross-doc **embeds** (`embedWidget`/`embedWizard`)
    stay on `WidgetRender` — they're widget/wizard surfaces, a different legitimate engine, not slide
    content (`blockToNode` throws for them, loud). (b) The Workshop **inline-editing** surface still
    uses the editable `WS_BLOCKS` React blocks (contentEditable); the engine renders read-only
    computed output, so editing-on-engine needs editable atoms — the remaining frontier (W6).
- **W5 — generator loop: ✅ DONE for deck-slide.** A Vi-proposed Type that extends a known
  archetype previews through the engine via `SurfaceSlideThumb` automatically. (Brand-new structural
  archetypes with no builder are the boundary — `proposeType` should `extends` a known one.)
- **LOUD-FAIL:** every fallback removed — `RenderType` throws if the engine/Type is missing,
  `Slide` throws without the bridge, `buildSlide` throws on an unknown archetype, `typeToNode` throws
  without the builders, `CoreTypes`/`types-seed`/`ds-base` throw without the catalogue/bundle. No
  silent placeholder renders. (The one async gate — `SurfaceSlideThumb` waiting on `window.__coreReady`
  — is readiness, not a fallback: it shows a neutral placeholder only until the core finishes loading.)

### Still open (next)
- **W6** — Workshop **inline-editing** through the engine. ✅ **COMPLETE (block content):** the
  block solver's text leaves (text · note · metric value/label · hero-number · bullet title/text ·
  chip · image caption) and the Band/Section/Zone **titles** are now inline-**editable** — when
  `ContainmentTree` is rendered with an `onEdit(path,value)` callback, each text leaf the block solver
  tagged with a data path (`node.edit*`) becomes contentEditable and commits on blur (the app's proven
  uncontrolled pattern). Verified: 4 editable leaves render from a tagged node, no errors. ✅ **Round-trip
  proven & all block-content tagged:** every block-solver `blockToNode` case now carries its data paths
  (`edit`/`editValue`/`editLabel`/`editTitle`/`editText`); `RenderType` threads `onEdit` to the solver;
  editing a `stats` value committed `items.0.v` → data updated (label preserved) → re-render reflected
  it. **Remaining:** the composer's `def.render` swap — render block sections via `RenderType(...onEdit
  writes back via a dotted-path setter)`, keep diagram/embed sections on their renderers, reconnect the
  Vi per-field regen toolbar; then `WS_BLOCKS` editing retires.
- **W7** — the LIVE widget/product-UI render onto the engine. ✅ **DONE:** a real **dataviz atom**
  (`chart` role — sparkline/bar/gauge from `tokens/dataviz.css`) + a `delta` on the metric atom; and
  `WidgetRender` (the live dashboard/hub/embed renderer) now renders its body **through the engine**
  (frame/header/CTA chrome kept; the parallel `Spark`/`Delta`/`KPITile` parts retired). Live widgets,
  registry previews, decks and templates now share the same atoms + tokens. Remaining trim: delete the
  now-dead `Spark`/`Delta`/`KPITile`/`Widget*` sub-components.
- Move the registry ENGINE (`types-core`) into the bundle so templates use the same registry
  singleton as the app (today templates use the `CoreTypes` minimal lookup).

## 4. Critical notes / risks
- **Do not churn what's right** (AUDIT-INDEX 8–10): shape system, icon library, voice, token values.
- **App boot is fragile** (self-mounting `.jsx` poison the bundle — HANDOFF §6.2). W2 wiring must be
  guarded (`if (window.ConceptVDesignSystem_c8f43c?.CoreTypes)`) and additive.
- **Bundle is stale mid-turn** (§6.1) — verify the bridge via the Babel harness; the app-side weld is
  validated by the end-of-turn rebuild + the verifier.
- **The earlier slice-4 mistake**, recorded honestly: `Slide`/`Archetypes` shipped as a *fourth*
  parallel strand instead of welding the existing three. This document + W1–W2 absorb it into the weld
  rather than leaving it parallel (or churning it away).
