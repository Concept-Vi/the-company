# SYNTHESIS PLAN — from analysis → the design system

> The bridge. Maps **confirmed** findings (see SYSTEM-GAPS.md, AXES.md) to concrete
> changes in the real design system. Ordered by readiness + dependency. Build the
> foundation (recalibrate values) before the structure (containers) before the
> library (templates). Nothing here is built yet — this is the plan.

## Readiness key
- 🟢 **Ready now** — confirmed across ≥3 folders, low risk, no structural decision needed.
- 🟡 **Ready after a structural decision** — needs the container architecture agreed first.
- 🔵 **Confirm with 1–2 more folders** (`vt-*`, `company-info`) before committing.

---

## 1. Token recalibrations — 🟢 ready now (confirmed 3–4 folders)
*Where: `colors_and_type.css` (values only; names stable; deprecate don't rename).*
- **Zone ladder → real near-white values** (replace the over-saturated pigments). Targets sampled identical across decks: ground `#fefefe` · warm-ivory `#fdfcf7` · warm-cream `#fcf9f4` · neutral-grey `#f8f8f8` · embossed `#f6f8f7` · hatch-ivory `#fdfcf5`. Deltas ~1–3%. Keep the `color-mix(... var(--zone-ground))` machinery (theme-invariance proven); just retune pigments/percentages so light-mode output matches these.
- **Gold:** soften `--accent-gold` `#E0C010` → ~`#d6bf57` (the deck's working gold). Keep old as `--accent-gold-legacy` if anything depends on it.
- **Bronze:** warm/lighten `--accent-bronze` `#988058` → ~`#c09d5d`.
- **Add the brand RAMP** (new ordered scale): `--ramp-1 #dad364 · --ramp-2 #d6bf57 · --ramp-3 #c09d5d · --ramp-4 #b98664`. Wire into `tokens/diagram.css` ring colours.
- **Semantic reframing (docs):** zoning = *containment-depth*, not category. Any hue-coded zone meaning is an opt-in app layer. Update the zone specimen card copy.

## 2. New token additions — 🟢 mostly ready
*Where: extend existing `tokens/*.css`.*
- **Hatch** token + `.hatch-band` / `.hatch-rule` (45° gold, band behind metrics + bottom rule). → `tokens/depth.css` or new `tokens/texture.css`.
- **Blueprint ghost** texture utility (faint architectural linework, top-weighted) — sibling to `.grain`.
- **Frame signature** (bottom hatch-rule + V-mark + 12% margins + title 7.5%) → a deck-chrome utility.
- **Two bullet semantics:** `▶` plain vs `→` "leads-to" → extend the bullet atom with a `kind`.
- **Status traffic-light** (green=approved / amber=review / red=declined) — saturated chips, distinct from the near-white washes. → `tokens/states.css` (semantic status set).
- **Frame ratios:** add **3:2** and a **web/scroll** surface to `--frame-*`; treat ratio as a free surface parameter (paged↔scrolling).

## 3. Container architecture — 🟡 the central structural build
*Where: components (`.d.ts` + `.jsx`) — the recursive container library.*
The capstone finding: **Deck → Slide/Band → Section → Zone/Panel → Group/Cluster → Atom**, each a
typed container with **role + spacing rhythm + collapse rule + depth-keyed wash**. Build as a small
set of composable container components (not one-off layouts):
- `Band` (paged-or-stacked; the Slide generalisation) · `Section` (bronze header + content) ·
  `Zone`/`Panel` (wash + radius + padding, depth-keyed) · `Cluster`/`Stack` (already in `tokens/layout.css`) · atoms.
- Each carries: its **collapse rule** (the responsive-fragility list = per-container collapse) and its **zone-wash** keyed to nesting depth.
- This is the single model that serves **decks AND the app** (the app's nav→panel→table→row IS this tree, mutable).

## 4. Template library — 🟡 after §3
*Where: `templates/<slug>/` (DCs) for slide/page/deck level; components for smaller.*
Everything catalogued is a **template at some tree depth**, and they compose:
- Atom/Group/Zone/Section templates → components.
- **Slide templates = the 13 archetypes** → `templates/`.
- **Deck/Page templates** (the narrative arc) → `templates/`.
- Parameterise by data (proven: variant "Our Entry Markets" slides; audience toggle) → **typed slots**, content-as-data, audience-variant param.

## 5. Axis controls — 🟡 wire to existing knobs
- **LOD** (summary→pitch→full) = per-node prune/grow → a content control; also enables **progressive disclosure** (interactive).
- **Register/pace** (presenter↔reader) → drives LOD + density + space/time visual mode together (keep separable).
- **Surface** paged↔scrolling → `Band` renders paged or stacked.
- Reuse existing `--density` + `data-theme` knobs (already built). 

## 6. Motion + space↔time — 🔵 confirm placement, then build
- **Motion-placement rule:** animate only hero concept diagram + immersive product views; analytical stays still.
- **Space↔time variant:** a container can *show children in space* OR *play them over time* — build as one component with a `mode`. Ties to `tokens/motion.css` + the GIF/motion-slot.

## 7. Deck→app bridge — 🔵 later
The embedded product UI (nav, tab bar, tables, status pills, comment panel, hotspots) is the same
containment tree, mutable. Mine a product-UI-heavy folder, then build app components on the same
container library. Interactive = runtime tree mutation (expand/collapse/reveal/raise-LOD).

---

## Suggested first execution slice (when moving from analysis → build)
1. **§1 + §2** token recalibration & additions (🟢, low-risk, immediately improves fidelity).
2. Refresh the **zone specimen card** to the true subtle ladder + document zoning-as-depth.
3. Then pause for a **structural decision on §3** (the container library) — that's the big one and should be deliberate.

*Remaining analysis that would de-risk §4–7: `vt-*` (tight LOD + A4), `company-info`/`presentation-15p` (mid-LOD), a product-UI-heavy source for the app bridge.*

---

## CAPSTONE — the unified build (all 12 folders analysed; corpus complete)
The whole system reduces to **one generative core**, built once, then everything composes on it:

> **One type system + one rule engine + two layout solvers** (block = flow/stacking, graph =
> relational), computed by the **axis-dials** (surface/LOD/register/density/theme) over an
> **invariant DNA core** (numbers, diagrams-as-spec, ramp, zoning-as-depth, colour-role logic).

### Build order (consolidated, dependency-ordered)
1. **🟢 Token recalibration & additions** (§1–§2) — real zone ladder, gold→bronze ramp, hatch/blueprint/frame-signature, two bullet kinds, status set, 3:2+web+A4 frames. *Low-risk; do first.* Refresh the zone specimen card (zoning = depth).
2. **🟡 The generative core** (the keystone decision):
   - **Typed container model** (Band→Section→Zone→Cluster→Atom): role + spacing rhythm + collapse rule + depth-keyed wash.
   - **Block solver** (flow/stacking) + **graph solver** (relational: radial/mesh/pipeline/quadrant/timeline) on the shared node type. Pick solver by content kind; they nest.
   - Wire the **axis-dials** to existing `--density`/`data-theme` + new **LOD** + **surface(paged↔scroll↔print)**.
3. **🟡 Component & template library** — atoms→Zone→Section→Slide(13 archetypes)→Deck, all typed-slot templates with content-as-data + audience/variant params. Includes the **stepper**, **diagram generator** (10 types, `DIAGRAMS.md`), comparison table, stat-card, profile-block, frosted-glass, etc.
4. **🔵 Motion + interactivity** — temporal traversal, state-morph (diagram chaos→order), space↔time mode; then runtime tree-mutation for the **deck→app bridge** (needs a product-UI source).

### Doc index (analysis layer — complete)
`AXES.md` (model: axes + containment + block/graph) · `REQUIREMENTS.md` (north-star + spec) ·
`DIAGRAMS.md` (graph type system) · `SYSTEM-GAPS.md` (raw findings) · `GUIDE.md` (method) ·
`PROGRESS.md` (all 12 folders ✓) · per-folder docs (`pitch-deck`, `deck1-2026`, `recent-pitches`,
`landing-mockups`, `vt-family`, `mid-lod`).
