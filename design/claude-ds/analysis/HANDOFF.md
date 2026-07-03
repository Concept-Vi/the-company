# ⭐ START HERE — Master Handoff

> **SINCE THIS WAS WRITTEN (addendum 2026-07-03):** this briefing is accurate for the token/core era
> (Slices 1-3) but is TWO BUILD ERAS STALE below. Since written: the **Glyphic LANGUAGE ENGINE**
> (G0-G11 — meaning registry/read-out/reverse parser/multi-target/data-binding/the glyphgraph render)
> was built + harness-verified, and **PHASE RECONCILE** (R1 the edge law · R2 referent-words-as-profile-
> data) landed (FINDINGS-LOG Slices 79-84). Do NOT "pick up Slice 4" from §7/§9 — boot from
> `~/company/build-prep/the-one-system/glyphic/REGROUNDING.md` + `CRITERIA.md` (+ its AMENDMENTS) +
> `ROADMAP.md` for the current state; the census record is `…/glyphic/census/AREA-*.md`.


> **You are taking over the build of the ConceptV Design System with no other instruction, no
> user guidance you can rely on, and no developers involved. This document is your complete
> briefing.** Read it fully before touching anything. By the end you should know the mission, the
> mindset, where everything is, what has been done, the conventions to follow, the traps to avoid,
> and exactly what to do next. Everything you need is in this repo — this file is the index to it.

> 🧭 **Read `CLAUDE.md` (project root) first — it is the operating manual** and the shortest path to
> the one idea: *one home per concept; everything references it; change the home → it propagates.*
> The system now has **four single-source registries** — **tokens** (`styles.css`+`tokens/*`),
> **types** (`CV_REGISTRY`), **the engine** (`core/` solvers), and **AI** (`CV_AI`, `app/ai/*`) — all
> the same shape. `analysis/INTEGRATION.md` §6 is the wiring contract for all four. Nothing is
> hand-set or duplicated; if you're copying a value/prompt/shape, you're drifting.

---

## 0. The mission & the mindset (read twice)

**What we are building:** not "a design system" in the ordinary sense (a pile of components + a
colour palette). We are building a **unified generative system** — *one type system, one rule
engine, two layout solvers, computed by a small set of orthogonal axis-dials over a fixed
invariant DNA core.* `design = f(content, axisPosition)`. The same content spec computes a 16:9
slide, a mobile scroll, an A4 one-pager, or an interactive app screen. (The full model is in
`AXES.md`. Internalise it — it is the whole point.)

**The mentality you must hold (the user was emphatic about this):**
- The goal is the **unified generative thing, NOT the fastest possible thing.** Depth on every
  axis. If you find yourself reaching for a quick, flat, hand-written answer, stop — that is the
  failure mode we are explicitly fighting.
- **Vigilance against "technical success."** A thing that compiles, or renders, or passes
  `check_design_system`, is NOT necessarily right. "It works" ≠ "it is the correct expression of
  the DNA." Always ask: is this *computed from the rules*, or did I just hand-set it? Is this
  *deep*, or merely functional?
- **Audit before you touch.** Never sweep-edit. The system is mature and someone's real work —
  understand what exists for the scope you're about to change *before* changing it (see §4).
- **The original system was shallow** — "flat ivory, one gold, no texture, the system feels
  still." That was a faithful but *narrow* read of the source. The real DNA (proven across 12
  source folders) is richer on every axis. We are deepening it without discarding what's genuine.
- **Everything you do will be checked thoroughly.** Document what you did and *why*, and flag
  anything you suspect was missed or is a missed opportunity. Leave the trail.

---

## 1. What ConceptV is (domain, 30 seconds)

ConceptV is an Australian innovation-technology company. Its products turn architectural design
files into **Virtual Hubs** (interactive panotour experiences for property buyers). Three platform
entities + an AI framework, each with a **canonical shape** (used consistently in diagrams):
**User Portal = circle · Property Wizard = hexagon · Virtual Hubs = octagon · Vi (AI) = line-fill
diamond** (wordmark "V" + gold subscript "i"). Pipeline: **Revit → Enscape → ConceptV**. Voice:
calm, professional, sentence-case, second-person, no exclamation/emoji in body. Full brand detail
is in the root **`README.md`** (read its v2 section first, then the v1 body for product-UI facts).

---

## 2. The repository map — where everything is

```
ROOT
├── README.md            Brand bible. v2 section at top = the generative layer (authoritative
│                        when it conflicts with the v1 body). v1 body = product-UI facts (still true).
├── SKILL.md             Agent skill entrypoint (how a consumer invokes this DS).
├── DESIGN-LANGUAGE.md   The cross-cutting design RULES (v2). Token-level "how the system thinks."
│
├── styles.css           ⭐ THE single entry point. @imports colors_and_type.css + every tokens/*.css
│                        + core/containers.css, in dependency order. Consumers link THIS.
├── colors_and_type.css  Source-of-truth L0/L1 tokens: pigments, --ramp-1..4, gold/bronze, ink,
│                        --zone-* registry (mixes toward --zone-ground), type scale, spacing (--s-*),
│                        status set. THE colour/type spine. ~408 lines.
├── tokens/              The token families (all registered, all @import-ed by styles.css):
│   ├── surfaces.css     typed frame ratios (ar + base w → h via calc), ratio-invariant grid % types
│   ├── sizing.css       fluid type/space (clamp), overflow utils
│   ├── depth.css        elevation ramp + grain
│   ├── motion.css       "nothing teleports" motion language (durations, eases, move/morph)
│   ├── diagram.css      diagram vocabulary (node/edge tokens, reuses zones)
│   ├── theme.css        light/dim/dark/contrast — flip --zone-ground, washes recompute
│   ├── density.css      --density knob → --d-1..12 spacing
│   ├── layout.css       Every-Layout primitives (.stack/.cluster/.sidebar/…) + z-index scale
│   ├── states.css       loading/resolve, empty/error, interaction, focus ring
│   ├── focus.css        attention / dim-the-rest
│   ├── icons.css        icon stroke/size/two-tone language
│   ├── dataviz.css      chart palette from zones + viz primitives
│   ├── imagery.css      aspect-ratio, blur-up, art direction
│   ├── canvas.css       spatial canvas scaffold (pan/zoom/edge routing)
│   ├── provenance.css   human / Vi / suggested authorship marking
│   ├── export.css       print/PDF/deck page sizes + lifecycle tags
│   └── texture.css      diagonal hatch + blueprint ghost (low-opacity)
│
├── core/                ⭐ THE GENERATIVE CORE (slice 3 — built & verified). See §5.
│   ├── containers.css   the typed containment ladder (Band→Section→Zone→Cluster→Atom);
│   │                    zone wash COMPUTED from nesting depth (zoning = depth made visible)
│   ├── cv-nodes.d.ts    the SHARED node type both solvers consume (CVNode, CVGraph, CVAxis)
│   ├── ContainmentTree.jsx/.d.ts   the BLOCK solver (flow/stacking + LOD pruning)
│   ├── DiagramSolver.jsx/.d.ts     the GRAPH solver (relational placement, 9 diagram types)
│   └── generative-core.html        @dsCard proving the core computes (Components group)
│
├── analysis/            ⭐ THE BRAIN. The full source-corpus analysis + the model + this handoff.
│                        (detailed in §3 — read AXES.md, then this file's siblings)
│
├── assets/              REAL brand assets (don't regenerate — use these):
│   ├── logos/           real wordmark + V marks (PNG). Gold sampled = #E0C010 (the TRUE logo gold)
│   ├── icons/           99-icon library: cv-icons.js (window.CV_ICONS), CvIcon.jsx, svg/, explorer
│   ├── illustrations/   architecture diagrams, staged delivery, Vi framework, stats panels
│   └── reference/       raw screenshots of the real product UI
│
├── preview/             Design-System-tab cards (~30, "Brand" group) — the existing specimen cards
├── ui_kits/             Three real UI kits (creator dashboard, virtual-hub viewer, Vi workspace).
│   ├── platform/        PlatformApp.jsx + PlatformSidebar.jsx + screens. Self-mounts (DOM-guarded).
│   ├── virtual-hub/     HubApp.jsx + viewer panels. Self-mounts (DOM-guarded).
│   └── vi/              ViKitApp.jsx + chat/task-tree/preview. Self-mounts (DOM-guarded).
├── app/                 The ConceptV Studio app (the design-system manager UI itself).
│                        app/App.jsx self-mounts (DOM-guarded). app/canvases/Workshop.jsx = composer.
│
├── _ingest/             The 12 SOURCE folders (decks, one-pagers, web mockups) — the evidence.
├── _archive-v1/         Snapshot of colors_and_type.css + tonal-zoning.css BEFORE the v2 rebuild.
├── _qa/                 Throwaway test harnesses + probes (e.g. core-test.html, zone-probe.html).
│
├── _ds_bundle.js        ⚠️ COMPILED OUTPUT — never edit by hand. Rebuilt at END OF TURN. (see §6)
├── _ds_manifest.json    ⚠️ COMPILED OUTPUT — never edit by hand.
└── _adherence.oxlintrc.json  ⚠️ COMPILED OUTPUT (the drift lint) — never edit by hand.
```

---

## 3. The analysis layer (`analysis/`) — what each doc is for

This folder is the accumulated understanding. **Read in this order:**

1. **`AXES.md`** — ⭐ THE MODEL. The parametric axes, the containment hierarchy, zoning=depth, the
   block/graph unification, the cross-axis synthesis. *This is the spine of everything.*
2. **`DIAGRAMS.md`** — the diagram generator's type system (10 types, subtypes, content schemas,
   icons as a content type). The graph solver implements this.
3. **`REQUIREMENTS.md`** — the living spec. North-star: rules that compute / generate new on-DNA
   components. Maps capabilities the system must have.
4. **`INTEGRATION.md`** — ⭐ HOW NEW THINGS CONNECT WITHOUT DRIFT. The L0/L1/L2 token-layer graph
   and the anti-drift contract. Read before adding ANY token or component.
5. **`SYNTHESIS-PLAN.md`** — the build order (the slices), each finding → concrete change, ordered
   by readiness (🟢 ready / 🟡 keystone / 🔵 later).
6. **`AUDIT-INDEX.md`** — the whole-system content-TYPE map + the **10 reconciliation tensions**
   (where the source DNA overrides the v1 README — tensions 1–7 are the "depth fixes").
7. **`FINDINGS-LOG.md`** — ⭐ THE RUNNING BUILD MEMORY. Per-slice: what the audit found, what it
   changed, what was done. Newest first. **Append here every slice.**
8. **`SYSTEM-GAPS.md`** — raw findings by confidence (what's confirmed vs dialect vs speculative).
9. **`GUIDE.md`** — how to run a source-folder analysis (the 9-level lens method), if more ingest arrives.
10. **`PROGRESS.md`** — folder-by-folder analysis tracker + the session log (narrative of every pass).
11. **Per-source docs:** `pitch-deck.md` (the deep baseline, 3 passes, §1–21), `deck1-2026.md`
    (the register/LOD comparison, §A–I), `recent-pitches.md` (density⊥ratio stress test),
    `landing-mockups.md` (web surface), `vt-family.md` (print one-pagers + summary LOD),
    `mid-lod.md` (company-info + presentation-15p). `_TEMPLATE.md` = blank lens for a new folder.

**All 12 source folders are analysed** (PROGRESS.md). The model survived every one with zero
contradictions — density stress test, register comparison, web surface, print ratio, mid-LOD. It
is as validated as analysis can make it. Do not re-analyse unless NEW source material arrives;
the next work is *building*, not analysing.

---

## 4. The conventions & protocols you MUST follow

### 4a. The token-layer discipline (the anti-drift contract — from INTEGRATION.md)
Everything references tokens; **nothing hardcodes a value.** Layers:
- **L0 primitives** (`colors_and_type.css`): pigments, `--ramp-*`, `--zone-ground`, raw scales.
  *New colours enter HERE.*
- **L1 semantic roles**: `--zone-*-surface` (mixed toward `--zone-ground`), colour-roles
  (ink/gold/bronze), status set. *Derived from L0 via `color-mix` — never literals.*
- **L2 component tokens** (`tokens/*.css`): `--dgm-*`, `--icon-*`, `--elev-*`, control sizes.
  *Reference L1, never literals.*
- **Consumers** (components, templates, the solvers): reference L0–L2 **only**. No hex, ever.

A value is defined **once, at its lowest layer**; everything above uses `var()`. Recalibrating a
pigment auto-updates every consumer — that's the guarantee. **This is why the generative output
inherits the DNA by construction: it has no literals to drift with.**

### 4b. Colour-role logic (don't break it)
**ink = content · gold = active/attention · bronze = structural voice** (section headers, line
illustrations). The gold is a **ramp** (`--ramp-1..4`: gold→bronze→tan), not one swatch. The TRUE
logo gold is `#E0C010` — **never soften it** (an early plan got this wrong; the softer `#d6bf57`
is the *applied* deck gold = a ramp stop, not a replacement). See FINDINGS-LOG slice-1.

### 4c. Zoning = containment depth (the central insight)
Near-white washes are **not** a semantic colour map. They render *nesting depth* (~2% undertone
per level, mixed toward `--zone-ground` so it's theme-invariant). A Zone is a wash; a Section
groups; the Band is the ground. Any semantic colour is an *optional layer on top*. The block
solver sets `--zone-depth` as it walks the tree (see `core/containers.css`).

### 4d. New axes follow the established knob pattern
A new dial = a `data-*` attribute + CSS vars, exactly like `data-theme` / `data-density` /
`data-surface` already work. No new mechanism. Keep axes **orthogonal** (LOD ≠ surface; a phone
can show high detail). Correlation ≠ coupling — defaults may link axes, the architecture must not.

### 4e. Where to write things (so nothing is lost)
- **Build memory** → append to `analysis/FINDINGS-LOG.md` every slice (audit findings + actions +
  open items). Newest first.
- **Progress** → tick `analysis/PROGRESS.md` (+ session-log line) and the in-tool todo list.
- **New rules/claims the system makes** → `DESIGN-LANGUAGE.md` and the root `README.md` v2 section,
  **in lockstep** (don't let the docs codify a stale read — the v1 README already did that once).
- **Raw findings** → `SYSTEM-GAPS.md`; **model changes** → `AXES.md`.

### 4f. This is a DESIGN-SYSTEM project — author types correctly
- **Components** = a `<Name>.d.ts` + sibling `<Name>.jsx`/`.tsx` (PascalCase) anywhere in the repo.
  The compiler bundles them into `_ds_bundle.js` and exposes capital-letter exports on
  `window.ConceptVDesignSystem_c8f43c`. Read them in card HTML via
  `const { X } = window.ConceptVDesignSystem_c8f43c`. **Do NOT `<script src>` a `.jsx` directly.**
- **Design System tab cards** = an `.html` whose FIRST LINE is
  `<!-- @dsCard group="…" name="…" subtitle="…" viewport="WxH" -->`. Groups seen: Brand, Colors,
  Spacing, Components, UI Kit — *. Every component dir needs one (it's the thumbnail).
- **Templates** (reusable decks/pages a consumer copies) = `templates/<slug>/<Slug>.dc.html` via
  the `dc_write` tool, with `<!-- @template name="…" description="…" -->` as the first line and
  `<helmet><script src="./ds-base.js"></script></helmet>`. **Not yet built** — slice 4/onward.
- **Solver authoring trick:** the two solvers use `const h = React.createElement` (JSX-free) so the
  React binding is unambiguous in the compiled bundle. Keep that pattern for new compiled components,
  OR use real JSX (the compiler transpiles it) — but if you hand-author a card that evals multiple
  `.jsx` in one scope, give each its own `Function` scope (top-level `const h` collides otherwise —
  that's what `_qa/core-test.html` does).

### 4g. Validate every change
Run **`check_design_system`** after every edit. It reports components, cards, tokens, and ISSUES
(unregistered tokens, missing cards, stale readme, raw `.jsx` in cards, duplicate names). Fix what
it flags, re-run until clean. "MANIFEST STALE" is expected mid-turn (it rewrites at end of turn) —
not an error. Pass `verbose:true` to see the full export map when a component compiled but isn't
on the namespace.

---

## 5. The generative core (slice 3) — what exists and how to use it

**Status: built, verified, clean.** This is the architectural keystone; slices 4–5 compose onto it.

- **`core/containers.css`** — the ladder classes: `.cv-band` (artifact ground, carries the 12%
  ratio-invariant margins + locks band aspect per `data-surface`), `.cv-section` (bronze header +
  content, unpainted), `.cv-zone` (the painted panel; wash = `--zone-depth × ~2.1% × intensity`
  mixed toward ground; `data-tone="neutral|review"` swaps pigment; `data-raised` lifts),
  `.cv-cluster` (`data-flow="col|row|grid|split"` layout, unpainted), `.cv-atom` (leaf). Per-level
  collapse via container queries.
- **`core/cv-nodes.d.ts`** — the shared types. `CVNode {kind, role, tone, flow, priority, detail,
  title, text, value, label, bullet, children, graph}`; `CVGraph {type, nodes, edges, axes,
  center, state}`; `CVAxis {lod, surface, density}`. **Both solvers consume this.**
- **`ContainmentTree` (block solver)** — props `{node, lod, surface, density, DiagramSolver}`.
  Walks the tree; **LOD prunes** by `priority` cutoff (summary≤1, pitch≤2, full=all) and drops
  `detail:"support"` at low LOD; sets `--zone-depth` per nesting; renders atoms by `role`
  (metric = gold tabular number+label; bullet = ▸/→/✓ by `bullet`; chip; text). A `kind:"diagram"`
  node hands its `graph` to the DiagramSolver.
- **`DiagramSolver` (graph solver)** — props `{graph, axis}`. Computes positions per `type`:
  hub (radial+center), network (ring), morph (before=ring ↔ after=hub, tweens via motion tokens),
  pipeline/timeline (L→R), quadrant (by node x/y + axis labels), tree (root+children), stack
  (vertical). Renders gold flow arrows / dashed dep+ref edges + shaped nodes (circle/hex/diamond/
  square) with depth-keyed fills. Implements DIAGRAMS.md.
- **`core/generative-core.html`** — the proof card: one spec at 3 LOD levels (scaled artboards) +
  diagrams across types + the live network→hub morph. Use it as the reference for how to mount the
  solvers from a card (`const {ContainmentTree, DiagramSolver} = window.ConceptVDesignSystem_c8f43c`).

**Verified behaviour:** LOD pruning correct (summary = priority-1 section + hero metric only);
hub/pipeline/quadrant compute + render in vocabulary. Verified via `_qa/core-test.html` (Babel
harness) because the bundle is stale mid-turn (§6).

---

## 6. ⚠️ TRAPS & GOTCHAS (things to check — learned the hard way)

1. **`_ds_bundle.js` is STALE mid-turn.** It only rebuilds at END OF TURN. So a component card you
   author this turn loads the *old* bundle and your new component will appear missing / the
   namespace shows only `__errors`. **This is not a bug in your code.** To verify a compiled
   component the same turn: use the **Babel-harness pattern** (`_qa/core-test.html`) — fetch the
   `.jsx`, strip `export`, transpile with Babel, run each in its own `Function` scope. Otherwise,
   end the turn (bundle rebuilds) and let `ready_for_verification`'s verifier check the real card.
2. **Self-mounting `.jsx` poison the shared bundle.** Any file that runs
   `ReactDOM.createRoot(getElementById('app')).render(...)` at module top-level throws when the
   bundle loads on a page without `#app`, aborting eval before later exports attach. The 4 known
   ones (app/App.jsx, PlatformApp, ViKitApp, HubApp) are now DOM-guarded (`if(getElementById('app'))`).
   **If you add or import another self-mounting file, guard it the same way**, or it breaks every
   component card. (There was also a TDZ bug — `WS_AI.cache` is now a getter.)
3. **Custom props under component selectors get flagged as unregistered tokens.** `check_design_system`
   wants `--vars` under `:root` or a `[data-*]` scope. Set per-instance values **inline** (the solver
   does `style={{'--zone-depth': depth}}`) or via a `data-*` attribute, not via a descendant rule
   like `.cv-zone .cv-zone { --zone-depth: 2 }`. Private `--_foo` vars are tolerated.
4. **`@kind` annotations on tokens.** Token comments carry `/* @kind color|spacing|font|other */`.
   Dimensional values (fluid clamps, ratios, durations) are `other`, NOT `font` (marking a clamp as
   `font` made the compiler hunt for a font-family and trip the font-upload prompt). See FINDINGS slice-2.
5. **Bulk file `move` needs project ownership.** It failed mid-build once; the workaround is
   copy-then-delete each file individually (single deletes work). Renames of components = rename the
   FILE (the compiler names components by filename, not the function name).
6. **Most "hardcoded hex" in the app/kits are legitimate literal holders** (the palette source, a
   token definition), not drift. Audit before "fixing" — don't blindly var()-ify. See FINDINGS slice-1b.
7. **`html-to-image` screenshots of cross-origin-stylesheet cards fall back to unstyled** — that's a
   capture artifact, not a real render failure. Verify with `eval_js` (computed styles) when unsure.

---

## 7. What's DONE vs what's NEXT

### Done (this build, all validated)
- **All 12 source folders analysed** → the model (`AXES.md`) + per-folder docs. Zero contradictions.
- **Slice 1** — token recalibration: added `--ramp-1..4` + `--accent-bronze-warm` (logo gold/bronze
  preserved); de-hardcode pass; zone ladder measured & confirmed already-subtle (NOT the flat
  problem — the v1 `#FBF4C8` panels were).
- **Slice 2** — atom tokens, TYPED as rules: frame ratios (`-ar` + base `-w` → `-h` via `calc`, so a
  new surface auto-derives), ratio-invariant grid % types, modular type-scale rule, texture (hatch +
  blueprint), bullet-kinds (▸/→/✓), frame-signature. Status set kept.
- **Slice 3** — the generative core (§5): containment ladder + block & graph solvers on a shared
  node type, wired to LOD/surface/density. Built, verified, clean. README refreshed to v2.

### Next (in priority order — todos 64, 65)
- **Slice 4 (🟡) — the component & template library.** Build ON the core:
  - The **13 slide archetypes** (from the analysis) as composable templates (fixed Section/Zone/
    Group subtrees + content-as-data — proven by the duplicate "Our Entry Markets" slides). Author
    as `templates/<slug>/<Slug>.dc.html` via `dc_write` (see §4f).
  - The **stepper** (ramp-tinted chevron: Design▸Marketing▸Sales▸Construction; ramp position can be
    a per-variant parameter — see vt-family).
  - The remaining **diagram presets** (the DiagramSolver already does the 9 layout types; wire up
    real-content presets + the icon-in-node content type per DIAGRAMS.md).
  - The **comparison/pricing table** (confirmed cross-surface component), stat row, pill-group,
    profile block, QR card, trust strip — the atom→group→zone templates catalogued in AXES.md §capstone.
  - **Discipline:** audit the existing app/ui_kit components FIRST (don't rebuild what `app/components`
    or the kits already have — lift/reconcile). Verify each (harness or end-of-turn). Log to FINDINGS.
- **Slice 5 (🔵) — motion + interactivity → the deck→app bridge.** Motion-placement rules (only hero
  concept + immersive product views animate; analytical slides stay still), the space↔time variant
  (a subtree shown in space OR played over time), then the runtime-mutable tree = the embedded
  product UI (nav→panel→table→row IS the same containment tree, mutable). Needs a product-UI-heavy
  source pass to confirm specifics.

---

## 8. Suspected missed opportunities / things to revisit (flagged for the checker)

Be skeptical of all prior work — including this. Known soft spots worth a fresh eye:
- **The block solver's atom roles are a starter set** (metric/bullet/chip/text). The analysis
  catalogued more atom types (hero-number, number+label variants, badge, geo-locator, device-channel
  strip). Slice 4 should grow `renderAtom` to cover them — or better, make atom rendering itself a
  registry so new atoms are data, not code branches.
- **The containment ladder's collapse rules are minimal** (split→stack at 640px). The full
  "responsive fragility list" (pitch-deck §21) has more per-level rules to encode.
- **The graph solver computes layout but not edge-routing/overlap-avoidance** — fine for small
  diagrams, may need refinement for the dense 49pp-style graphs.
- **`tonal-zoning.css` and the original `Tonal Zoning System.html`** (the very first deliverable)
  predate the v2 token rebuild — check they still reference live tokens, or fold them into the core
  / archive them. There may be other v1 consumers still pointing at deprecated `--accent-gold-50`.
- **No template (`templates/`) exists yet** — the whole point (a consumer copying a starting deck)
  is unproven until slice 4 ships one and it's verified in a consuming context.
- **The `app/` Studio UI itself** has not been re-skinned with the v2 depth (texture, zone washes,
  motion). It's the system's own shopfront — a candidate once the library exists.
- **Verify the solvers in a real consuming `.dc.html` template**, not just a card — that's the true
  end-to-end test (DS bundle → `<x-import component-from-global-scope>` → rendered template).

---

## 9. Your first moves in a fresh session

1. Read this file, then `AXES.md`, then `INTEGRATION.md`, then `FINDINGS-LOG.md` (newest entries).
2. Skim the root `README.md` v2 section + `DESIGN-LANGUAGE.md`.
3. Open `core/generative-core.html` and `_qa/core-test.html` to see the core working.
4. Run `check_design_system` to confirm a clean baseline before you change anything.
5. Pick up **Slice 4** (todo 64). Audit existing components first. Build deep, not fast. Verify each
   piece. Append to FINDINGS-LOG. Tick PROGRESS + todos. Keep the docs in lockstep.

> Remember the mandate: the **unified generative system**, with **vigilance against mere technical
> success**. If something feels flat or hand-written, it's wrong — make it computed, make it deep.
