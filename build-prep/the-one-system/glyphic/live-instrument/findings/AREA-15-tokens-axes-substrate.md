# AREA-15 — Tokens · Axes · Substrate (WAVE-3 coverage + UNIFICATION into the Company)

> WAVE-3 coverage+unification agent. Territory: the ~18 `tokens/*.css`, `colors_and_type.css`,
> `styles.css`, `tonal-zoning.css`, `axes/` (axis-core + per-axis modules), and crucially **how
> this UNIFIES INTO the Company** (`~/company/design/_system/tokens.json` → `emit.py`).
>
> **Lens (Tim, overriding):** nothing is final/canonical/done — written as growing, not "built."
> DUPLICATIONS are expected + valuable: for every system, catalogue its UNIQUE QUALITIES and name
> FUSION candidates. The job is **fuse-best-of-all into one place**, never pick a winner.
> Deep-link / single-source / no-staleness is the governing law.
>
> **Coverage honesty / dependency on AREA-12:** AREA-12 (wave-2) already mapped, *inside claude-ds*,
> the `axis-core.js` verbs, the L0→L1→L2 colour chain, the render spine (RenderType/ContainmentTree/
> DiagramSolver), and the **three-colour-map staleness** (color-axis ↔ `CV_GLYPHIC.COLOR_TOKENS` ↔
> CV_MEANING seeds) + the `CV_MEANING.encodings` hex violation. **I lean on AREA-12 for those and do
> not re-derive them.** My additive budget is spent on: (i) the ~18 individual token files AREA-12
> explicitly skipped (its §F), (ii) the **cross-system** picture — two co-located token systems — and
> (iii) sub-questions **(c) duplicates + unique qualities** and **(d) unification into the Company**.
>
> Marking: **Observed (file:line)** = read directly · **Inferred** = pattern-judgment ·
> **External-prior-art** · **My-idea** = proposal for the build.

---

## TL;DR (3 lines — the headline WAVE-3 correction)

1. **There are TWO token systems in the same `~/company/design/` tree, and they are NOT symmetric —
   they are single-source by DIFFERENT MECHANISMS.** `claude-ds/` (this folder) has the **richer
   MODEL** (L0→L1→L2 `color-mix`-derived roles, a `data-*` knob layer, theme remap, and the typed
   `CV_AXES` JS layer on top) but its token CSS is **hand-authored — no JSON source, no emit, no
   `_system/`** (Observed — verified: no generator, no GENERATED header). The parent
   `design/_system/tokens.json → emit.py → design-system.css` has a **flatter model** (`primitives`
   + `{v}`/`{ref}`) but real **machine single-source generation** (change the look from one JSON).
2. **So the fusion writes itself (it is not "pick a winner"):** express claude-ds's layered + axis
   MODEL *through* an emit-style pipeline, INTO the Company centre — which already carries Tim's
   **dated palette decision** (`GOLD-PRIMARY WARM THEME (Tim, 2026-06-07, final)` — warm-charcoal
   dark, gold `#e6ab5c`, no green). "Never pick a winner" governs the *mechanism*; on the *palette*
   there is a Tim signal, and my loaded rule **Islands Join Mainland** resolves it cleanly: the
   island (claude-ds) contributes its model INTO the mainland (the Company), which holds the palette.
3. **For the live glyphgraph layer specifically:** the resolution spine the live RESOLVE stage must
   ride is `CV_AXES.css(axis,value) → var(--token)` + `CV_AXES.validate/candidates` (the loud-fail
   gate on LLM-proposed facet values) — and there is **already a pan/zoom/incremental canvas scaffold
   in `tokens/canvas.css`** (the `.spatial-*` plane, the "programmatic moves glide" transition) that
   the reactflow-vs-build-fresh question must reckon with as a third option, not assume away.

---

## A · COVERAGE — the ~18 token files (what each is + its value-units), the part AREA-12 skipped

`styles.css` is a pure import manifest (Observed, styles.css:36-55) — the ordered single entry point;
later files reference earlier tokens, so order is load-bearing. The files, grouped by what they single-source:

### A.1 The value-unit ramps (these ARE the axes' value-units)
- **`colors_and_type.css`** — the L0/L1 hub (AREA-12 §B). Also the **spacing scale `--s-0..--s-24`**
  (the "ONLY scale", strict 8px rhythm, :140-155), the **radii `--r-*`** (:129-135), the **type
  family/tracking/duration primitives** (:162-178), the **shadow set** (:118-126), and the
  **layout primitives `--layout-*`** (:182-188). This is the single home for the literals.
- **`tokens/sizing.css`** — the **FLUID type scale** `--fs-caption..--fs-display` as `clamp()`
  (:24-33) derived from an explicit `--scale-ratio:1.25` + `--scale-base:16px` RULE (:22-23);
  the matched line-heights `--lh-*` (:36-39); fluid spacing `--space-fluid-*` (:43-46); `--measure*`
  (:49-51); and **the element/mark SIZE ramp `--size-xs..--size-hero`** (:57-64) — *which are the
  value-units of the SIZE AXIS* (Observed cross-ref: size-axis.js maps `xs→size-xs`, meta.px). Plus
  overflow-safe utilities (`.truncate`, `.min0`, `.pill-group`, `.auto-grid`). **For the live layer:
  a Glyphic's render size resolves `CV_AXES.resolve('size').resolve(id).meta.px` → an honest number,
  and the CSS chrome `var(--size-*)` → one home.** (Observed.)
- **`tokens/icons.css`** — the **inline `--icon-xs..--icon-xl`** sub-scale (sizing a glyph WITHIN
  chrome), distinct from `--size-*` (a whole mark). One home for "icon-in-chrome size". (Observed.)
- **`tokens/depth.css`** — the **elevation ramp `--elev-0..--elev-5`** (ambient+key, warm-tinted via
  `--shadow-c`, :22-44) = the value-units of the DEPTH AXIS (depth-axis.js carries `meta{dy,blur}`);
  `--glow-active` (the one gold decision-glow, :47); grain (`--grain-opacity/-scale`, the SVG-noise
  `.grain`). **For the live layer:** the polygon-accurate Glyphic shadow geometry lives in CV_GLYPHIC,
  but the SCALE single-sources here — a node's elevation must `var(--elev-*)`, never a literal box-shadow.
- **`tokens/motion.css`** (NOT read in full this pass — AREA-12 noted motion-axis uses a CSS class
  `mo-*` in `axes/motion/motion.css`, a *separate* file from `tokens/motion.css`) — the durations
  `--dur-*` / eases the canvas + states + focus files all reference (`--dur-move`, `--ease-emphasized`,
  `--dur-quick`). Inferred from the consumers; flag for a deeper read.

### A.2 The KNOB layer — `data-*` attributes that re-tune whole ramps from one place (Observed)
This is claude-ds's distinctive MODEL move and the strongest single-source mechanism it has:
- **`tokens/density.css`** — one knob `--density` (:13) scales density-aware spacing `--d-1..--d-12`
  (`calc(Npx * var(--density))`, :16-23) + control heights; `[data-density="compact|comfortable|
  spacious"]` flips it (:33-35). New components reach for `--d-*` so one attribute re-tunes layout.
- **`tokens/theme.css`** — `data-theme="dim|dark|contrast"` and the orthogonal `data-ground="clean|
  warm"` (:108-110) flip ONLY `--zone-ground` + the ink ramp + `--zone-intensity`; **the 28 zone
  roles recompute themselves** because every wash is `color-mix(... var(--zone-ground))`. "A knob,
  never a redraw" (:101). This is the verified propagation AREA-12 §B.2 proved.
- **`tonal-zoning.css` + colors_and_type.css:329-446** — the zone PIGMENTS (`--pig-*`) + the
  `--zone-intensity` / `--gold-intensity` / `--spatial-opacity` global knobs (:332-336), and the
  `.zone-palette-cooler/.zone-palette-warmer` recolour-by-overriding-pigments variants (:449-457).
  **Re-tune the whole colour language by moving one knob; re-colour by overriding ~9 pigments.**
- **`tokens/canvas.css`** — `--cv-x/--cv-y/--cv-scale` pan/zoom transform knobs (:24-26),
  `--cv-grid`, `--cv-ghost-opacity`. **See §E — this is a live-canvas scaffold, directly relevant.**
- **`tokens/focus.css`** — `--recede-*` / `--focus-lift` / `--focus-scale` (:24-29) drive a
  "bring-forward, soften-the-rest" attention mechanism (`.focus-scope.is-focusing > *:not([data-focus])`).

### A.3 The semantic / vocabulary files (consume the roles, invent nothing — Observed)
- **`tokens/diagram.css`** — the diagram VOCABULARY: stroke weights `--dgm-stroke-*`, node tokens
  `--dgm-node-*`, connector + arrowhead, and the **edge-kind colour map** `--dgm-edge-{flow,
  dependency,reference,rejected,communication}` (:69-73) — *each is `var(--accent-gold)` / a zone-ink
  / `--comm-line`, never a literal*. The `.dgm-edge--*` stroke presets. **This is the static/CSS
  precedent for the live meaning-edge** (the reactflow edge should resolve the same way).
- **`tokens/dataviz.css`** — chart palette `--viz-key`(gold) + `--viz-1..6` (zone inks, :13-19);
  primitives `.viz-stat/.viz-bar/.viz-gauge/.viz-spark`. Gold reserved for the key series only.
- **`tokens/provenance.css`** — authorship marking `--author-{vi,human,suggested}` + `data-author`
  edge treatment + `.by-*` badges + `.vi-authored` wash. **Directly relevant to the live layer's
  two-way authoring** (Tim's voice vs the AI both author the same surface — provenance is the
  human/Vi/suggested distinction already tokenised).
- **`tokens/states.css`** — `--skeleton-*` (the shimmer that "resolves, never pops"), `--focus-ring`
  (gold), `--state-{hover,press,selected}`, `.skeleton`/`.state-block`/`.interactive`. **The skeleton
  path is the staged-reveal the live layer wants** (a node renders as skeleton while extraction
  resolves its facets — AREA-12 §C.3 said the same of ContainmentTree's `loading` swap; here is the
  CSS half).
- **`tokens/layout.css`** — Every-Layout primitives (`.stack/.cluster/.sidebar/.center/.cover/.reel/
  .frame-ratio/.grid-fit/.switcher`) + the **z-index scale `--z-base..--z-max`** (:21-30) — the only
  legal stacking order (a live canvas's overlays/popovers must use these).
- **`tokens/surfaces.css`** (not read in full — AREA-12 covered via the import manifest) — breakpoints,
  canonical frames, container-query convention. `tokens/imagery.css`, `tokens/export.css`,
  `tokens/texture.css`, `tokens/controls.css` (the L2 component layer — AREA-12 §B.1) — consume the
  roles; not on the live-graph critical path. (Coverage honesty: read by manifest + role-refs, not
  line-by-line — flagged, lower relevance to the live layer.)

**Coverage note:** I did NOT re-read every utility line of surfaces/imagery/export/texture/controls;
AREA-12 + the import manifest + the consumer refs cover their role. The files above in §A.1/A.2/A.3
were read directly (Observed) except `tokens/motion.css` (Inferred via consumers) and the four just named.

---

## B · THE AXIS SYSTEM CV_AXES — how a facet value resolves (extends AREA-12 §A with the wiring proof)

AREA-12 §A mapped `axis-core.js` (the `makeAxis` verbs + `resolveCSS` + `candidates`/`validate`) and
the ten axes' payload kinds. **I add the WIRING PROOF and the per-axis resolution detail the live
RESOLVE stage needs**, and I confirm the axes are LIVE, not orphaned scaffolding:

### B.1 The axes are wired and load in dependency order (Observed — `app/index.html`)
`app/index.html:136-151` loads, in order: `axis-core.js` → `cv-icons.js` → `cv-shapes.js` →
`color/space/size/motion/texture/depth/fill/form/symbol`-axis → `cv-meaning.js` → `cv-glyphics.js`.
The comment (:133-134) states *why*: "form/symbol axes need their value sources (shapes/icons) loaded
first." **So `CV_AXES` is a real, populated registry on the live app surface** — the live layer
resolves through an existing object, not a planned one. Also loaded by `system/axis-system.html`,
`system/glyphic-system.html`, `system/glyphic-foundry.html`, `app/registry/glyphic-type.js` (Observed
grep). This is the resolution spine to ride.

### B.2 How each facet value resolves to a `var(--token)` (Observed — the data-binding must use THIS, not hex)
| Axis | resolveCSS payload | The single source it lands on |
|---|---|---|
| **color** (`color-axis.js`) | `token` → `var(--accent-gold)` etc. | `colors_and_type.css` L0/L1. Groups brand/semantic/ink/communication/neutral; aliases `amber→status-warning, clay→status-error, blue→status-info` (:61-63). default `bronze`. |
| **size** (`size-axis.js`) | `token` `--size-*` + **`meta.px`** | `tokens/sizing.css:57-64`. Computational consumers read `meta.px`; CSS reads `var(--size-*)`. default `md`. |
| **space** (`space-axis.js`) | `token` `--s-*` | `colors_and_type.css:140-155` (the 8px scale). |
| **depth** (`depth-axis.js`) | `token` `--elev-*` + `meta{dy,blur,opacity}` | `tokens/depth.css:22-44`. The geometry scale single-sources; CV_GLYPHIC owns the polygon-accurate shadow. |
| **motion** (`motion-axis.js`) | **`css`** (a class name, e.g. `mo-breathe`) | `axes/motion/motion.css` — token-free *by design* (the animation lives in CSS, the axis names the class). |
| **fill** (`fill-axis.js`) | **`meta.ramp`** recipe (none/paper/wash/tint) | the actual gradients live in `CV_GLYPHIC.FILL_RAMPS`; the axis is vocabulary only (Observed fill-axis.js:5-10). |
| **form** (`form-axis.js`) | **`resolve→null`** + `meta{sides,shape}` | references `CV_SHAPES.geom` by id; the n-gon progression `none(0)→3..8→circle(∞)`; render via `CV_SHAPES.markSVG`. default `circle`. **It tolerantly filters to shapes that exist in `CV_SHAPES.geom` (:31-33) — a new shape lights up the axis with no edit.** |
| **texture** (`texture-axis.js`) | enum ids | realised by `CV_SHAPES.markSVG` / `tokens/texture.css`. |
| **symbol** (`symbol-axis.js`) | **`resolve→CV_ICONS.get(id)`** (live svg) | the live-rebuild axis — see B.3. |

**The live RESOLVE answer (a):** a facet value resolves through `CV_AXES.css(axisId, valueId, ctx)`
(axis-core.js:149) → for colour/size/space/depth a `var(--token)` whose literal lives once in the CSS;
for motion a class name; for form/fill/texture/symbol a payload the SHAPE/ICON/GLYPHIC engines realise.
**The data-binding must hand the LLM the axis's `candidates(sub)` as the closed enum and feed the
chosen value id back through `CV_AXES.css` — never emit a hex.** (My-idea, grounded; same as AREA-12 §D.)

### B.3 The no-staleness pattern already in the axes — the GENERATE-ON-MISS precedent (Observed)
`symbol-axis.js:25-42` — `rebuild()` walks `CV_ICONS.data` live and registers every icon (incl.
AI-foundry-added ones) as a symbol value whose payload is `I.get(id)` resolved live; exposed as
`symbol.rebuild` so **the foundry calls it after `CV_ICONS.add`**. Groups derive from
`CV_ICONS.facets[id].domain`. **This is the exact discipline the live GENERATE-ON-MISS stage copies:
draw a new icon mid-conversation → `CV_ICONS.add` → `symbol.rebuild()` → it is immediately a valid
axis value the composer can resolve.** No hardcoded symbol list, no copy. (Observed — and AREA-12 §A.4
named this; I confirm the mechanism reads `CV_ICONS.data` live, not a snapshot.)

### B.4 axis-core is itself a registry-of-registries with the SAME verbs (Observed)
`axis-core.js:135-161` — `CV_AXES.{make,register,resolve,tryResolve,has,list,all,css,candidates,
validate}` mirrors `CV_REGISTRY`/`CV_AI`/`CV_MEANING` (the comment, :19-22). **This sameness is the
fusion lever:** whatever resolver the Company adopts can speak the same five verbs, so the axis layer
ports without a new mechanism.

---

## C · THE TWO TOKEN SYSTEMS — duplicates + UNIQUE QUALITIES (sub-question c, the WAVE-3 core)

Both live under `~/company/design/`. They are **parallel homes for "the look"** — a duplication the
governing law would normally call drift, but here it is two *generations* of the same idea built by
different agents at different times. Catalogue, don't pick.

### C.1 System α — `claude-ds/` (this folder): the RICH MODEL, hand-authored CSS
- **Source of the literal:** the CSS files themselves (`colors_and_type.css` + `tokens/*.css`).
  **Observed (load-bearing, verified this pass):** there is **no `_system/` in claude-ds**, no
  `emit.py`/build script writing the token CSS, and **no `GENERATED` / `DO NOT hand-edit` header** on
  any token file. `grep -rl colors_and_type --include=*.py` finds only `_demo/gen_colors_face.py`
  (which renders a *demo face*, not the tokens). **⇒ claude-ds tokens are hand-authored. Single-source
  is enforced by CSS-cascade discipline (`var()` everywhere, no second hex), not by a machine.**
- **UNIQUE QUALITIES (what fusion must NOT lose):**
  1. **L0→L1→L2 derivation via `color-mix`** — roles are *computed* from primitives toward
     `--zone-ground` (28 zone roles, `--vi-*`, `--comm-*`). A theme/palette swap reflows everything
     (theme.css). The parent's `{ref}` only *aliases* a primitive — it cannot `color-mix`-derive.
  2. **The `data-*` KNOB layer** — `--density`, `--zone-intensity`, `--gold-intensity`,
     `data-theme`, `data-ground`, `--cv-scale` — runtime re-tuning from one attribute. The parent
     has no knob layer (it has `root_extra.font-size` only).
  3. **The typed `CV_AXES` layer** — facet→value→token resolution with `candidates`/`validate`
     (the loud-fail vocabulary gate). The parent has tokens but **no axis/validation layer**.
  4. **Theme remap + accessibility** (dim/dark/contrast) and **orthogonal ground** (clean/warm).
- **WEAKNESS (the real single-source gap):** to change the look you edit across ~18 CSS files by
  hand; nothing emits/validates them; a recurring literal can only be caught by an external linter
  (the parent's `check.py` is *in the parent*, not here). **No machine registry for its own tokens.**

### C.2 System β — `design/_system/tokens.json → emit.py → design-system.css`: the GENERATION pipeline
- **Source of the literal:** `_system/tokens.json` (Observed, 94 lines) — `primitives:{gold:#e6ab5c}`
  + `groups[].tokens` each `{v:value}` (flat) or `{ref:primitive}` (resolves; `emit.py` raises
  `KeyError` on an unknown ref — fail-loud, emit.py:~24). `emit.py` compiles → `design-system.css`
  (Observed header: "GENERATED … DO NOT hand-edit"). Every mockup links the generated CSS.
- **UNIQUE QUALITIES (what fusion must KEEP):**
  1. **Real machine single-source + generation** — change `primitives.gold` once, re-run `emit.py`,
     every consumer follows. Extend-by-registration (add a token = add a JSON entry).
  2. **It is governed by the parent's whole `_system/` machinery** — `check.py` (hardcoded→token
     finder + design-lint that GATES a build by exiting non-zero on off-token literals in app source),
     `refcheck.py`/`symbols.py`/`codeedges.py` (the `code://` drift + dependency graph),
     `mechanisms.json` (the extend-by-registration check registry). claude-ds has **none** of this.
  3. **It carries Tim's DATED palette decision** (see C.3) and embedded design-direction notes
     (the type system, the two-vivid-one-muted status split) right in the JSON `note` fields.
- **WEAKNESS:** the MODEL is flat — no `color-mix` derivation, no knob layer, no axis/validation
  layer, a single theme baked in (warm-charcoal dark). It is *less expressive* than α.

### C.3 The values genuinely DIVERGE — and there is a Tim signal on the palette (Observed)
- claude-ds: `--accent-gold:#E0C010`, **paper-first LIGHT** theme (`--paper:#FCFAF2`), green is a
  live communication voice (`--accent-communication:#7CA85B`). (colors_and_type.css:16,45,91.)
- Company: `gold:#e6ab5c`, **WARM-CHARCOAL DARK** (`bg:#0c0a08`), and the JSON note states:
  *"GOLD-PRIMARY WARM THEME (Tim, 2026-06-07, final): gold is THE primary colour + theme, NO
  green/mint/teal anywhere."* (tokens.json `_palette_note`.)
- **This is NOT a winner-pick on mechanism** (Tim's "never pick a winner" + the task's "fuse-best-of-
  all" govern the MECHANISM). But on PALETTE there is a dated, explicit Tim decision in the centre.
  My loaded rule **Islands Join Mainland** (and the task's "UNIFY INTO the Company") resolves it as
  both/and: claude-ds (island) contributes its *model/mechanism* INTO the centre; the centre's
  *palette* (Tim's dated call) holds. The claude-ds light/green palette becomes a *theme variant
  expressible in the unified model*, not the default. (My-idea, grounded in the rule + the dated note.)

### C.4 A SECOND parallel pair — two data→visual binding registries (only-mine, AREA-12 didn't see β's)
- **α:** `CV_MEANING.encodings` (cv-meaning.js:210-216) — surface-keyed profiles binding one data
  facet → one visual channel (discrete or scale). **AREA-12 §B.3 already flagged its hex violation**
  (the `system-map` profile binds facet→bare hex `#E0C010` instead of a token id — a second home for
  the literal). *I reference, do not re-derive, that finding.*
- **β:** the parent tokens.json **"node-type visual language"** group — `kind-process→{ref:gold}`,
  `kind-content:#b89a6e`, `kind-present:#e6ab5c`, `kind-model:#c0a0c8` (+ `*-bg` variants). This is
  ALSO a facet(node-kind)→appearance binding, living as tokens. (Observed, tokens.json.)
- **The parallel (mine to name):** α binds facet→channel as a *runtime registry* (rich: scale
  interpolation, per-surface profiles) but drifted into hex in one profile; β binds node-kind→colour
  as *static tokens* (machine-emitted, single-source) but only the discrete node-kind case. **Fusion
  candidate:** the live binding grammar = α's encoding-registry SHAPE (facet→channel, discrete+scale,
  per-surface) keyed to TOKEN/axis-value ids (never hex), emitted/validated by β's machinery so a
  drift like `system-map`'s hex is caught by `check.py` at build, not at paint. (My-idea.)

---

## D · UNIFICATION — how these flow INTO the Company (sub-question d, the WAVE-3 deliverable)

**The governing law's prize is: the live layer must resolve from ONE source so growth never stales.
Today there are two token sources + (counting the running app) a third. Unification = collapse to one
home, keeping α's model + β's generation.** The concrete shape, marked as proposals:

### D.1 The fusion mechanism (the HOW, not a vague "merge") — My-idea, grounded
1. **Lift claude-ds's MODEL into the JSON source.** Extend `tokens.json` (or a successor) to express
   (a) **primitives**, (b) **derived roles** with a `mix:{toward, pct}` recipe (so `emit.py` emits the
   `color-mix(... var(--zone-ground))` chains α has — the one expressive thing β lacks), and (c) a
   **knobs** section emitting the `data-*` / `--density` / `--zone-intensity` scaffolding. `emit.py`
   grows two new emitters; the JSON stays the single home. (My-idea.)
2. **The CV_AXES layer becomes the typed VIEW over that one token source.** Each axis value's `token`
   already names a token id (color-axis.js); point those ids at the unified token set. `CV_AXES`
   keeps its `candidates`/`validate` verbs — they are the loud-fail vocabulary gate the live RESOLVE
   stage needs and β has nothing equivalent. (My-idea, grounded in B.4.)
3. **Retire the three-colour-map drift (AREA-12 §A/§D) as part of the lift, not after.** `CV_GLYPHIC.
   COLOR_TOKENS` becomes a thin read of the color axis; the CV_MEANING colour seeds reference axis
   value ids. Otherwise the live layer adds a fourth home. (Reference AREA-12; I concur.)
4. **The far end is the running app (`canvas/app/src`).** tokens.json's own notes say it *promoted
   literals from* `canvas/app/src/app.css` into the registry (the type system note). So the real
   end-state is: one token source → emits the CSS the *running app* AND the mockup corpus AND the
   live glyphgraph all link. (Observed in tokens.json notes; the running app is outside my territory —
   flagged as the unification's far end, non-blocking.)

### D.2 Where deep-link / single-source is HONOURED vs where a copy/hardcode HIDES (Observed)
**Honoured (the good precedents to extend):**
- claude-ds CSS: `var(--token)` everywhere; roles `color-mix` from primitives; the theme/density/zone
  knobs re-tune from one attribute. No second hex in consumers (spot-checked controls/diagram/dataviz/
  provenance — all `var()` or zone-ink, never literal).
- `CV_AXES.resolveCSS` → `var(--token)` (the value points at its single source, never copies).
- `symbol.rebuild()` — the live-readback no-staleness pattern (B.3).
- β's `{ref}` + `emit.py`'s fail-loud `KeyError` on unknown ref.

**Where a copy/hardcode HIDES (the drift to fix in the fusion):**
- **Two token sources for one look** (α hand-CSS vs β JSON) — the macro duplication. Until collapsed,
  "change the look" means two edits, and they have already diverged (C.3).
- **The three colour maps** (AREA-12 §A) — "gold→accent-gold" in color-axis + COLOR_TOKENS + CV_MEANING.
- **`CV_MEANING.encodings` system-map profile binds facet→bare hex** (AREA-12 §B.3) — a second home.
- **A few literal fallbacks in `tokens/diagram.css`/`dataviz.css`** (`var(--zone-panel-ink, #6b6357)`)
  — these are CSS `var()` *fallbacks* (a defensible degrade), NOT a second home; AREA-12 §B.3 makes
  the same distinction. Don't "fix" them into drift. (Observed; Inferred-benign.)

### D.3 Honest correction to the live-instrument synthesis (the both/and)
The synthesis frames the live canvas as "build fresh + reactflow." **There is a third option this
area surfaces:** `tokens/canvas.css` is a **closed-form pan/zoom/incremental canvas scaffold already
present** — `.spatial-canvas` viewport, `.spatial-world` plane transformed by `--cv-x/--cv-y/
--cv-scale`, absolutely-placed `.spatial-node` (which *reuses the diagram node tokens*), an edge SVG
layer, ghosting/memory-shelf for rejected nodes, and crucially **`transition: transform var(--dur-move)
var(--ease-emphasized)` with `.dragging { transition:none }`** — i.e. "programmatic moves glide,
live drag is 1:1" is ALREADY wired (canvas.css:50-58). Combined with AREA-12 §C.4 (the glyphgraph
node+edge render already exists in `glyphGraphView`), the **render + the canvas plane + the "nothing
teleports" motion** all exist in-system, token-resolved, no external lib (CSP-clean). So the reactflow
decision is genuinely a both/and: reactflow's interaction affordances (selection, handles, minimap)
vs the in-system scaffold's token-purity + zero-bundle + CSP-cleanliness. **The fusion question for
the canvas is: does reactflow's node renderer call `CV_GLYPHIC.render` + resolve edges through
`CV_AXES`/`--dgm-edge-*` (staying single-source), or does it fork a second style home?** The
`.spatial-*` scaffold proves the single-source path is buildable without a lib. (Observed + My-idea.)

---

## E · THE FOUR SUB-QUESTIONS — explicit answers (for the synthesizer)

- **(a) The TOKEN graph — how a value resolves to `var(--token)`, what data-binding must use:**
  L0 primitive (hex, one home) → L1 role (`color-mix`/`var()`) → L2 component token (`var()`). A facet
  value resolves via `CV_AXES.css(axis,value) → var(--token)` (color/size/space/depth) or a class /
  shape-payload (motion/form/fill/symbol/texture). **The data-binding must bind facet → a token id or
  axis value id and resolve at paint through `CV_AXES`/`var()` — NEVER a hex.** (§A, §B.2, §D.2.)
- **(b) The AXIS system CV_AXES — how facet values resolve through it:** §B. Live, wired in
  `app/index.html` in dependency order; `candidates`/`validate` are the loud-fail vocabulary gate;
  `symbol.rebuild()` is the generate-on-miss no-staleness pattern.
- **(c) Duplicate/parallel token-or-axis approaches + unique qualities:** §C. **Two token systems**
  (α rich-model hand-CSS · β flat-model JSON+emit) — single-source by *different mechanisms*; values
  diverged (light/gold vs warm-dark/gold; green vs no-green) with a dated Tim palette signal in β.
  **Two data→visual binding registries** (α `CV_MEANING.encodings` · β node-type tokens). Unique
  qualities catalogued per side — fuse, don't pick.
- **(d) How these flow INTO the Company (unification):** §D. Lift α's MODEL (derived roles + knobs +
  the typed CV_AXES view) INTO β's GENERATION pipeline + machinery, keeping β's dated palette as the
  centre; collapse the three colour maps + the encodings-hex as part of the lift; the far end is the
  one token source emitting the CSS the running app + mockups + live glyphgraph all link.

---

## F · Files read (coverage honesty)
**Fully read (Observed):** `styles.css` · `colors_and_type.css` · `tonal-zoning.css` (head + role
refs) · `tokens/{sizing,density,theme,states,layout,depth,canvas,diagram,dataviz,provenance,focus}.css`
· `tokens/icons.css` (head) · `axes/axis-core.js` · `axes/{color,size,form,symbol,fill}/*-axis.js` ·
`app/index.html` (load order) · `_system/tokens.json` (parent) · `_system/emit.py` (parent) ·
`design-system.css` (parent, head) · `conventions.md` (parent, token section). **Verified by grep:**
no `_system/`/emit/GENERATED-header in claude-ds (the hand-authored finding). **Leaned on AREA-12
(not re-derived):** axis-core verbs detail, L0→L1→L2 chain, render spine, three-colour-map, the
`CV_MEANING.encodings` hex violation. **Not read line-by-line (lower live-layer relevance, flagged):**
`tokens/{surfaces,imagery,export,texture,controls,motion}.css` (covered by manifest + consumer refs;
`tokens/motion.css` durations Inferred via consumers) · `axes/{space,motion,texture,depth}/*-axis.js`
(payload kinds taken from AREA-12 §A.3) · the parent `_system/check.py`/`refcheck.py`/etc. internals
(named from the parent CLAUDE.md, not opened). The running app (`canvas/app/src`) is outside territory.

---

### 3-line summary
1. **TWO co-located token systems**, single-source by *different mechanisms*: claude-ds = the **richer
   MODEL** (L0→L1→L2 `color-mix` roles + `data-*` knobs + the typed `CV_AXES` validation layer) but
   **hand-authored CSS with no emit/registry** (verified: no `_system/`, no GENERATED header); the
   parent `_system/tokens.json→emit.py` = the **flatter MODEL with real machine generation** + the
   `check.py`/`code://` governance, and it carries Tim's **dated warm-charcoal gold-primary palette**.
2. **Unification (the HOW, not winner-pick):** lift claude-ds's model (derived roles + knobs + the
   axis view with `candidates`/`validate`) INTO the parent's emit pipeline + machinery, keeping the
   centre's dated palette (Islands-Join-Mainland); collapse the three colour maps + the
   `CV_MEANING.encodings` hex as part of the lift; far end = one source emitting the CSS the running
   app + mockups + live glyphgraph all link. A second parallel pair (two facet→visual binding
   registries) fuses the same way. The live RESOLVE must ride `CV_AXES.css→var(--token)`, never hex,
   and `tokens/canvas.css` already provides a CSP-clean pan/zoom/glide scaffold the reactflow decision
   must reckon with.
3. **Path:** `/home/tim/company/design/claude-ds/analysis/glyphic-language/live-instrument/findings/AREA-15-tokens-axes-substrate.md`
