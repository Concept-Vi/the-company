# System gaps — what the material has that the design system doesn't (yet)

Running log. Each entry: what it is, evidence (folder/page), and the proposed
home in the system. Nothing here is built until confirmed across folders.

---

## ★ CONFIRMED ACROSS 2 FOLDERS (pitch-deck + deck1-2026) — SYNTHESIS-READY
> Identical values in both decks → these are universal, not dialect. Safe to graduate into tokens.
- **Near-white zoning ladder** (recalibrate `--zone-*`): ground `#fefefe`/`#ffffff` · warm-ivory `#fdfcf7` (exact match both decks) · warm-cream `#fcf9f4` · neutral-grey `#f8f8f8` · embossed `#f6f8f7` · hatch-ivory `#fdfcf5`. Semantic = warm-vs-neutral undertone, ~1–3% deltas. Optional hue-coded semantics layered on top, per-app only.
- **Gold→bronze→tan ramp:** primary `#d6bf57` · bright `#dad364` · bronze `#c09d5d` · tan `#b98664`. Soften `--accent-gold` (`#E0C010`→~`#d6bf57`); warm/lighten `--accent-bronze` (→`#c09d5d`). Add ordered ramp.
- **Grid:** 12% side margins · 7.5% title top · 76% content band · split ~46/54 · bottom hatch-rule + V-mark **frame signature**.
- **Colour-role logic:** ink=content · gold=active/decision (never body) · bronze=structural/quiet; contrast-as-hierarchy.
- **Atom set & archetype library** (see pitch-deck.md §5–6) — recur identically; archetypes are *selected per cut* from a shared library.

## ★ NEW from deck1-2026 — the REGISTER / PURPOSE dimension
- **Two cuts of one source:** *terse/presented/motion-ready* vs *verbose/static/leave-behind*. Same DNA, different verbosity + density + length + motion-readiness. → templates need a **register switch** driving the **copy content-model** (headline bullets ↔ sentence bullets) + **`--density`** + **static-dense-visual ↔ motion-slot** swap.
- **Motion / GIF placeholder = first-class slot** (hub diagram, virtual-tour, room views animate). Dense static visuals and motion slots are interchangeable by register. → motion-ready placeholder component (ties to the motion language + the deck→interactive bridge).
- **Density is a per-cut/per-surface setting**, not a fixed deck property → the presented cut is also the most mobile-reflow-friendly.

## ★ DEEP COMPARATIVE FINDINGS (from the diff between the two cuts)
> Principles neither deck shows alone — high-value for how templates/components should be structured.
- **Space↔time complexity trade-off:** a slide has a fixed complexity budget spendable in *space* (dense static) OR *time* (animation). A dense diagram and a "simple frame + GIF" are **register variants of one component**, swappable. Motion and density are one control, not two.
- **Pace-controller determines register:** reader-paced → verbose/self-sufficient; presenter-paced → terse/anchors-only. Self-serve/mobile ⇒ verbose; live pitch ⇒ terse.
- **Level-of-Detail (LOD) is an axis orthogonal to surface size.** Same message at multiple zoom levels (17pp read → 16pp pitch → 1pp summary). Expose **content LOD** as its own template control alongside surface size — *the mechanism for "one source → many outputs".*
- **Invariant skeleton vs flexible muscle:** numbers + diagrams + structure NEVER change between cuts; only prose/length flex. → treat **numbers/diagrams as fixed payload slots**, prose as **LOD-variable** text. Numbers are sacred.
- **Bullet = {claim, support}:** terse keeps claim, drops support. Render depth by LOD.
- **Motion-placement rule:** animate only the hero **concept diagram** + **immersive product/spatial views**; keep analytical slides still.
- **Narrative-priority ranking:** slides are essential vs optional; tag instances → **auto-shorten to a time budget**.
- **Conserved ink-budget:** terse = fewer + larger; verbose = more + smaller; text-area ~constant. Resize survivors, don't just delete.
- **Canonical master = deck1-2026** (2× res, "2026", motion-ready) — sample production values from it.

## ★ CONFIRMED ACROSS 3 FOLDERS (+ recent-pitches, 3:2, high-detail)
- **Ratio-invariance:** zoning ladder (`#faf9f7`≈`#fdfcf7`), gold ramp (`#c4ab43`/`#c49649`), **~12% margins**, frame signature all hold unchanged at **3:2** and high density. → **ratio is just a surface value; density/LOD is independent of it** (resolves the AXES open question).
- **High LOD = more *sections*, not crammed text** — negative-space rule survives; density buys structure.
- **Slides ARE templates (proof):** `recent-pitches` p-25 & p-49 are the same "Our Entry Markets" layout with different data (general vs luxury). → the 13 archetypes should become **parameterised templates** (fixed layout + content as data); variant takes of one template are expected.
- **New atoms:** QR "Virtual Tour" **phygital card** · **`→` flow-bullet** (bullet glyph is semantic: `▶` plain vs `→` leads-to) · **quadrant/positioning map** (axes + plotted node-cards + dashed connectors) · **team/org grid** · **geo locator** (tinted map) · **multi-section-per-slide** (the high-LOD mechanism) · **device-channel showcase strip**.
- New `--frame-*` entry needed for **3:2** (and the ratio set is open-ended — treat ratio as a free surface parameter).

## ★ CONTAINMENT HIERARCHY (structural axis — see AXES.md for the full model)
- Nested-container ladder: **Deck → Slide → Section → Zone/Panel → Group/Cluster → Atom**, each a box with inherited spacing rhythm (panel pad ~2.5–3%, gutter ~2%, marker→text ~3%).
- **Zoning = the hierarchy made visible:** near-white washes mark *container depth* (~1–3% undertone), not semantic categories. This is why zoning is universal+subtle. Semantic hue mapping is an optional layer on top.
- **LOD operates on the tree** (more sections + atom depth = higher LOD); **templates are fixed subtrees** with content as data; **density** scales spacing uniformly across levels.
- → Build implication: model the system as **recursive containers** (each level a component with role + spacing), with the zone-wash as the container's surface treatment keyed to nesting depth.

## ★ THE CONTAINMENT TREE IS THE SPINE OF EVERY AXIS (cross-folder synthesis — see AXES.md)
Re-examining all 4 folders: each parametric axis *operates on the containment tree*:
- **Surface/responsive** = per-container-level collapse (the "fragility list" = container-local collapse rules).
- **Motion** = temporal traversal of the tree; space↔time = "show children in space" vs "play them over time" (same subtree).
- **LOD** = per-node prune/grow; settable locally = **progressive disclosure**.
- **Interactive (deck→app bridge)** = runtime tree mutation; the embedded product UI (nav→panel→table→row) **is the same tree, mutable**. One model for decks and app.
- **Depth/z** = elevation encodes nesting depth + focus (focus = raise container, recede siblings).
- **Theme** = zoning-as-depth is theme-invariant (mechanism survives; ground flips).
- **Invariants** = LOD-locked node *types* (numbers, diagrams), not a separate concept.
- **CAPSTONE:** atoms / components / patterns / the 13 archetypes are all **templates at different tree depths**, and they **compose**. → Build the system as a **library of typed, composable containers** (role + spacing + collapse rule + depth-keyed wash); the dials compute any output.

---

## Seeded from first samples (provisional — confirm during folder analysis)

### Zoning — RECALIBRATE (not keep)
- The real zoning is **near-imperceptible warm-white tonal separation** (~2–6% tint deltas), occasionally a **diagonal hatch texture** rather than flat tint. The current `--zone-*` palette is too saturated and semantically hot-coded. → Recalibrate `--zone-*` to true sampled values; reframe as a *universal subtle surface ladder*, with semantic mapping kept optional/per-app.

### New motifs not in the system
- **Blueprint / architectural line ghost** background layer (very low opacity). → new texture token + utility, sibling to `.grain`.
- **Diagonal hatch** motif — both edge rule (bottom of covers) and texture fill (zone backgrounds). → tokenised hatch (angle/spacing/colour/opacity) + utility.
- **Gold→bronze→brown tonal gradient** used as a *sequence/relationship* ramp (e.g. diagram ring colours). → tokenised ordered ramp distinct from the flat gold accent.
- **Brand-mark-in-headline** — the gold **V** substituted for a letter in display text. → type treatment / component.
- **Triangle / play bullets** in gold, direction points into content. → list/bullet atom.
- **Hairline gold outline callout** (stat box, e.g. "92.67%") — outline, not fill; logo + big number + supporting text. → stat-callout component.
- **Big-number / stat** display treatment. → dataviz/type token (relate to `.viz-stat`).
- **Photo block + dark caption overlay** ("Gain competitive advantage"). → media-caption pattern (extends `tokens/imagery.css`).
- **Interactive hotspot dots** on full-bleed imagery, **MENU pill**, **account icon**, **info markers**. → interactive-affordance atoms (the deck→component bridge).
- **Full-bleed photographic cover** with logo + warm bronze subtitle lockup. → cover layout pattern.

### Structural / responsive
- Real presentation ratios (16:9, 3:2, A4 portrait, tall web) → confirm/extend `--frame-*` set; derive ratio-based reflow rules per layout pattern (level 9).

---

## ✅ CONFIRMED from `pitch-deck` (baseline, 17pp) — real sampled values

> These are evidence-backed and ready to synthesise once a 2nd folder confirms them.
> Sampled hexes are from flat regions; gold ramp from hue-cluster analysis.

### Zoning — RECALIBRATE to this near-white ladder (highest priority)
Replace the saturated `--zone-*` palette with a true ~1–3% undertone ladder:
- ground `#fefefe` · warm-ivory `#fdfcf7` · warm-cream `#fcf9f4` · **neutral-grey `#f8f8f8`** · embossed `#f6f8f7` · hatch-ivory `#fdfcf5`.
- **Semantic signal = warm-vs-neutral undertone**, not hue: in sibling cards the odd-one-out is *neutral grey*, the rest *warm ivory*. Keep any hue-coded semantic mapping strictly **optional/per-app**, layered on top of this universal subtle ladder.

### Brand gold is a RAMP (not one gold)
- bright `#dad364` → **primary `#d6bf57`** → **bronze `#c09d5d`** → **tan `#b98664`** → deep brown.
- Soften `--accent-gold` (`#E0C010` is too acidic) toward `#d6bf57`; warm/lighten `--accent-bronze` (`#988058` → `#c09d5d`). Add the ordered ramp (wire into `tokens/diagram.css` ring colours + a general `--ramp-*`).
- Accent coral/terracotta `#d4907a` (sparing). Title ink near-neutral `#191919`.

### Dataviz palette (multi-hue ONLY in charts)
- gold + navy `#212d5b` + blue `#4c7bc8` + green `#8aae48`/`#35a550` + red `#d4726c` + orange. → reconcile with `tokens/dataviz.css`.

### New motifs to tokenise/build (confirmed present)
- **Diagonal gold hatch** — full-width band behind metrics + thin bottom baseline rule. → hatch token (angle/spacing/colour/opacity) + `.hatch-band` / `.hatch-rule`.
- **Blueprint ghost** — faint architectural linework background (esp. top). → texture token sibling to `.grain`.
- **Bottom "frame signature"** — hatch rule (left ~60%) + circular gold **V mark** bottom-right, on ~every analytical slide. → deck chrome component.
- **Embossed hero-number chip** — raised light box + big gold number. → component.
- **Hairline-outline callout** — outline (not fill) stat box (logo + number + line). → component.
- **Outlined pill w/ ramp border** — pill row whose borders gradate gold→tan. → extends `.pill`.
- **Icon-flow row** — thin line icons on a dashed baseline converging to a node. → component (reuses `tokens/icons.css` + diagram edges).
- **Hex / diamond badge** — brand badges w/ version label. → component.
- **Profile block** — circular photo + bronze name + role + stat triplet. → component.
- **Interactive affordances** — state-coloured hotspot dots (green/amber/red = approved/review/declined), MENU pill, account icon, info markers, embedded 2D panel chrome. → the deck→component bridge atoms.

### Structure
- Outer side margins **≈12%**, title top **≈7.5%**, content band **≈76%**. Split ratio **≈46/54** with bleed-off-edge visual zone + optional hairline divider + crossing arrow.
- 13 layout archetypes catalogued (see `pitch-deck.md` §6) → candidate **templates** later.
- Responsive intents per archetype recorded (§9): split→stack, triptych→1-col, metric-band→2-col on mobile portrait; margins 12%→5–6%; type via clamp.

---

## ✅ DEEP-PASS additions from `pitch-deck` (connection / texture / depth / unnamed)

> Cross-cutting languages — most are likely universals; confirm across folders before building.

### Depth & texture (tokenise as a layered z-stack)
- **Z-order depth stack** (universal): `blueprint ghost → white ground → soft panel (low shadow) → card → frosted-glass overlay → floating UI/hotspot → modal`. → formalise z-scale + elevation roles (extends `tokens/depth.css` + the `--z-*` scale).
- **Frosted glass / glassmorphism** — backdrop-blur panel + hairline light border + soft shadow, used over photography (contact card, action bars). → new component/utility `.glass`.
- **Translucent layered-panel stack** — semi-transparent UI panels with coloured edge strokes receding in z ("user-relevant layers"). → depth/diagram motif.
- **Embossed hero-number chip** — raised/inset light box (inner highlight + soft drop). (already noted; depth detail added.)
- **Shadows run warm + soft + large-blur** — recalibrate `--elev-*` warmer/softer than current defaults; sample exact values when synthesising.
- **Three background textures, opacity-layered:** blueprint ghost (top-weighted), diagonal gold hatch (bands + baseline rule), paper-grain/white. → blueprint token + hatch token + keep `.grain`.

### Connective / narrative systems (relevant to decks AND app)
- **Connector / "2-way" language** — plug icon + dashed bidirectional connectors encoding translation/sync/overlay. → connector vocabulary (extends diagram edges).
- **Italic-bronze connective caption** — the "narration" register that synthesises a slide + seeds the next. → type role.
- **Recurring-diagram-with-changed-state** (chaos network → ordered hub) — author diagrams as reusable with state, not one-offs. → principle + diagram-generator requirement.
- **Frame signature** (bottom hatch rule + V mark + 12% margins + title 7.5%) — the per-page binding. → deck chrome component.
- **Reading-direction arrow** crossing the split divider — reading cue + translation metaphor. → split-layout pattern detail.

### Semantic colour beyond brand (IMPORTANT — likely a real universal)
- **Status traffic-light set:** green = approved · amber = review/pending · red = declined. Distinct from brand gold; lives in the product UI. → semantic status tokens (reconcile with existing zone-success/warning/reject — but these are SATURATED chips here, not near-white washes; the washes and the chips are two different layers).

### Embedded product-UI vocabulary (mine for the APP design system)
- Consistent app chrome across slides: left nav menu · top tab bar · data tables w/ status pills · right comment/detail panel · account icon top-right · "MENU" pill · hotspot markers · "Hide Dashboard". → catalogue as app component candidates when a product-UI-heavy folder is analysed.

### Smaller conventions (hard rules)
- **Number+label pairing:** number gold + tabular-nums; label small grey, right/beneath. Never varies.
- **Gold-underline emphasis** — a third emphasis level (vs bold-ink, vs gold-fill).
- **Shape-coded sub-brands** — hexagon (engine) vs diamond (assistant); shape is semantic.
- **Trust strip** — muted partner-logo row.
- **Everything rounded** (pills full-round, cards ~1% radius, photos rounded) — soft geometry is a rule.
- **Negative space non-negotiable** even at peak density.
- **Photography art-direction spec** — warm coastal-luxury interiors, floor-to-ceiling glass, neutral cream/taupe/timber + sage + rust accents; rounded organic furniture rhyming with UI geometry. → imagery art-direction note (extends `tokens/imagery.css`).
- **Alignment signals slide type** — centred = statement; left = working.

---

## ✅ THIRD-PASS additions from `pitch-deck` (rules *between* elements)

> The finest-grain layer: micro-typography, colour-role logic, latent motion, restraint guardrails. Confirm across folders.

### Type & scale
- **Modular type scale** ≈ 1.25 per step with a ~1.9 display jump (title 4.6%h · section 2.4% · body 1.8% · caption 1.6% · micro 1.2%). → encode as a real scale, not ad-hoc clamps.
- **Balanced 2-line titles** (`text-wrap: balance`, leading ~1.05). Re-balance per width.
- **Hanging-indent bullets** (marker in margin, ~3% gutter, wrapped lines align to text).
- **Number-formatting convention:** gold + tabular-nums; suffixes k/M/B/T, `+`, `/unit`, `x`, `%`; grey label inline or to the right; never split number from label on wrap.
- **Caps reserved** for tiny eyebrow/label only; everything else sentence case. Curly punctuation.

### Colour-role logic (the *when*)
- **ink = content (titles/body), gold = active (numbers/bullets/emphasis/interactive), bronze = structural/quiet (section headers, italic captions, labels).** Gold never used for body.
- **Contrast-as-hierarchy:** connective tissue deliberately low-contrast (italic bronze) to recede; content high-contrast; numbers lead by size not saturation. → guardrail when applying colour.
- **Ramp position = loudness** (gold→bronze→tan = loud→quiet).

### Grid (fine)
- panel padding ≈ 2.5–3% width · inter-panel gutter ≈ 2% · marker→text gutter ≈ 3%.
- **Invisible 4-corner frame:** bottom hatch rule (left→~60%), V mark (bottom-right), account icon (top-right), title (top-left/centre). → the "chrome" of the deck-frame component.

### Latent motion (bridge to motion language)
- **Directional-cue set:** up-chevron (expand), down-triangle (reveal/continue), right-arrow (flow/translate). → small indicator component set.
- **Entrance order = reading order** (title→lede→panels→caption) → default stagger sequence for animated/interactive versions.
- Affordances imply interaction (hotspots, MENU pill, layered panels, dashed connectors) — design these with their motion in mind.

### Restraint guardrails (ANTI-patterns the system refuses — encode in adherence rules)
- No pure black · no hard/dark shadows · no gradients outside photography · no saturated fills outside charts · no heavy rules (hairline only) · **no left-accent-border cards** · no drop-caps · no all-caps body · italic only for bronze captions · underline only for gold emphasis · **no emoji** · icons never ornamental.

### Production / authoring
- **Master-template, single-source discipline** (pixel-consistent chrome across all slides; one icon family/type/palette) → faithful to componentise; the 13 archetypes are the master layouts.
- **Copy content-model** (title=claim · lede=explanation · section-header=1–3 words · caption=italic synthesis · bullet=single claim) → scaffold into templates.

### Responsive fragility (write rules for these first)
6-across metric band · 2×3 gallery · absolute-positioned timeline/network diagrams · bleeding split visual · balanced 2-line titles · inline number+label runs.
