# SKINS — one block grammar, many resolved worlds

> Companion to `analysis/BLOCKS.md`. Source of truth for the SKIN layer: what the six
> reference images (uploads/, May 2026 — the Vi "First Contact" boards + Harborview
> project-trace boards) contain, decomposed onto the system's axes, and how a skin is
> registered so the SAME blocks/tokens resolve to the full glass skin **or** the full
> stone skin. The images are the quality bar — directly comparable.

## 1. What the reference images ARE (decomposition)

The blocks are the SAME blocks (panels · cards · wells · pills · labels — the ladder
holds). What changes is a coordinated set of bindings — **that set is the skin**:

| What the eye sees | Axis / mechanism it maps to |
|---|---|
| Warm champagne **plaster wall** ground: fine tooth/noise, soft mottling, gentle top-light, occasional organic (foliage) shadow, floor seam at the bottom | the GROUND part: skin ground layers (`--skin-ground-*`) = base wash (color axis, warm neutral) + procedural noise texture (texture axis, new `plaster` value) + light gradient (the ambient field, calmed) |
| **Matte porcelain blocks** laid ON the wall: opaque warm-white, slightly lighter than ground, large radii, hairline light top edge | the MATERIAL axis: new `porcelain` value; fills mix from `--glass-ground` (tint mechanism intact) toward warm white |
| **Two-part soft shadows**: tight contact shadow + wide warm ambient falloff — never black, always warm | the DEPTH axis realised per-skin: `--shadow-contact` + `--shadow-ambient` roles (skin re-binds what `--mat-shadow` means) |
| **Debossed wells** inside cards (thumbnails, charts, list rows) | the ladder: `well` rung → `material--inset`; porcelain's inset = inner top shadow + light bottom lip |
| **Selected** card: warm gold rim + soft outer glow + gold check badge | a block STATE (`selected`) — the gold voice; one per view |
| **Ghost / future** blocks: dashed hairline outline, no fill, muted text ("Future explorations", suggested actions) | a block STATE (`potential`) — the outline vocabulary's "potential" made a block state |
| **Card stacks** (decks of offset sheets behind the front card) | depth/stack treatment: `is-stacked` (pseudo-element sheets; physical depth) |
| **Fine luminous gold threads** joining blocks; junction dots; tiny light particles; dashed segments for unresolved paths; arrowheads on process flows | the GRAPH side: blocks as NODES, cv-edges relations as THREADS; per-skin edge roles (`--edge-thread`, `--edge-glow`, `--edge-dot`) |
| **Label nodes**: small caps text + leading dot sitting directly on the wall (no card) | a `label` node = block with material `none` + micro text occupant + connector dot |
| Gold **Vi hub** (the ring-mark, glowing) at the graph's root | the Vi voice: `tint: vi` + `selected` glow on the hub node |
| Layout is **relational**, not stacked: hub → clusters → cards, flows left→right | the two-solver doctrine: same substrate, GRAPH solver arranges; containment still rules INSIDE each block |

**The invariants that do NOT change between skins:** the block grammar (parts/slots/
sockets/ladder/keyline/contain/flow), the tokens' meaning, the gold-is-the-voice rule,
type roles + budgets, the tint whisper mechanism, coordinates.

## 2. The mechanism — how one spec resolves to either skin

1. **`data-skin="<id>"`** on the stage/page scope. The skin re-binds ROLE variables
   only — never a consumer rule: ground layers, the default block material, shadow
   character, edge/thread roles, state glow language.
2. **Material `skin`** (new axis value, the DEFAULT): "the skin's own surface."
   `[data-material="skin"]` is bound per skin scope — glass roles under the glass skin,
   porcelain roles under stone. An explicit material (velum, parchment…) still forces.
3. **Block states** (`state` slot: `none · selected · potential · stacked`) emit
   `is-*` classes; each skin defines what selection-glow and ghost look like through
   the same role vars.
4. **Threads**: edge roles per skin; the demo's thread painter draws node-to-node
   beziers from resolved DOM positions (bridging toward DiagramSolver/cv-edges).

Homes: mechanism + stone skin = `tokens/skins.css`; the registry of skins =
`axes/skin/skin-axis.js` (add a skin = one scope + one axis value); living spec =
`system/skin-system.html`.

## 4. THE GAP ATTACK — current generation vs board 1 (line by line)

| # | Misalignment (current → reference) | Root cause / fix home |
|---|---|---|
| G1 | **Gold reads LEMON** (saturated brand yellow on threads, dots, Vi, check) → boards use **antique gold**, bronze-leaning, low sat | Skins must re-bind the ACCENT usage, not just surfaces: stone gold = ramp's antique end (`--stone-gold` in skins.css) |
| G2 | Threads too thick, loops too loopy, sparks too crisp → hair-thin, gentle arcs, soft particle glows | thread engine params per skin (width, curvature, particle softness) |
| G3 | Selected glow is a box-shadow rim only → boards pool **light on the wall** under/around glowing nodes | `.is-selected::after` halo light-pool (skin role) |
| G4 | Hub is a flat disc → boards show a **torus**: bevelled ring, inner face, glow pool behind, gold V mark (not serif text) | `.node-hub` bevel (inset shadows) + halo; the real V mark asset |
| G5 | Hub has no **satellites** → boards orbit icon pills (waveform, mic, doc, image) linked by threads | new node kind: icon pill (CV_ICONS + porcelain circle) |
| G6 | No **breadcrumb label-chain** ("Product design · Selected") off the hub | label-chain node (two-line label + dot on thread) |
| G7 | Cards: type too large, no corner **"+" affordances**, no photo/render media | smaller node type scale; the actions socket projected as a corner + ; imagery slots (tokens/imagery.css / image-slot) |
| G8 | Direction cards are text-only → boards are **media+text rows** (3-D render left) | card arrange variant `media-row` + imagery slot |
| G9 | Prototype column: title inside the stack card; missing two small square sub-thumbnails | stack layout variant + thumb-pair sub-cluster |
| G10 | Ghost column: no column label, dashed route runs through the ghosts | labeled potential-cluster block; route AROUND nodes (routing engine) |
| G11 | Cluster labels are mono ALL-CAPS → boards use quiet sentence-case, warm gold-grey | label voice = `label` role tinted toward the skin gold, not `micro` |
| G12 | No top chrome (Vi wordmark lockup left, "My Vi" pill right); composer missing the left "T" pill | chrome nodes in the spec (they are blocks too) |
| G13 | Canvas cramped (760px band) → boards are airy 16:10 with generous margins | stage aspect 16:10, node scale rhythm |
| G14 | Missing clusters: Open questions, Evidence | content — add to the spec (same card node) |
| G15 | Layout is declared %, boards read as computed columns/orbits | DiagramSolver layout (the named big rung) |

## 5. What EXACT recreation requires (the capability inventory)
1. **Gold discipline as a skin binding** (G1) — every accent consumer reads skin-scoped gold roles.
2. **Thread engine v2** (G2, G10): per-skin width/curvature/particle params; routing that avoids nodes;
   dashed *routes* vs dashed *states* distinguished; unify with cv-edges verbs / DiagramSolver edges.
3. **Node vocabulary completion** (G5–G9, G12): icon-pill, label-chain, media-row card, stack-with-caption,
   labeled ghost column, wordmark lockup, account pill, T-composer — all registered block variants, not demo HTML.
4. **Light as a first-class layer** (G3, G4): halo pools (ground-painted radial light) with per-skin roles.
5. **Imagery pipeline** (G7–G9): image slots in wells + the warm duotone treatment (tokens/imagery.css).
6. **Solver layout** (G15): hub-orbit + column flow computed from relations.
7. **Board-scale type rhythm** (G7, G11, G13): node title/caption sizes as tokens, sentence-case label voice.
8. **The Harborview vocabulary** (boards 3–6): breadcrumb rail, gantt/donut/histogram/iso-diagram wells
   (dataviz tokens), file-stack cards, marching-ant selection, dashed decision routes.



## 7. ASSET & 3D/LIGHTING BRIEF (for Claude Code — approved architecture)

**The doctrine constraint:** assets become AXIS VALUES; one token flip must re-resolve the world.
The page DOM stays CSS/SVG-resolved — no page-wide 3D framework (it would break direct editing,
streaming paint, and print/PPTX export). 3D enters only as scoped, registered solvers.

### 7a. Texture files wanted (deliver to `assets/textures/`)
Deliver each as a RANGE across both worlds so a skin flip resolves to a real value on
each side — not a single one-off. Tileable, ~2048², WebP, FLAT lighting (no baked
vignette/shadow — those are separate overlay layers).

| File | Spec | Becomes |
|---|---|---|
| `plaster-diffuse.webp` | seamless warm champagne plaster | texture-axis `plaster` → stone skin `--skin-ground` |
| `plaster-cool.webp` | greige/cool plaster variant | texture-axis `plaster-cool` (proves ground is a range) |
| `ink-depth.webp` | dark near-black atmospheric ground, low-contrast | texture-axis `ink-depth` → glass world ground |
| `linen.webp` / `concrete.webp` | optional extra points on the texture axis | more axis values (visible generativity) |
| `foliage-shadow.png` | soft leaf-shadow, black-on-TRANSPARENT, heavy feather, ~2048w | skin light-layer, composited `multiply` (works over any ground) |
| `light-pool.png` | soft radial window-light bloom, white-on-TRANSPARENT | skin light-layer, composited `screen` |
| `floor-strip.webp` | optional wall-meets-floor strip, tileable-x, ~2048×400 | stone skin floor-seam layer |
| *(r3f route only)* `plaster-normal.webp`, `plaster-roughness.webp` | same tile as diffuse | 3D ground material maps |

### 7a-bis. Card renders (deliver to `assets/renders/`)
Transparent-background PNG, consistent 3/4 lighting from top-left (lit by the same
room). A MAP, and ideally MATCHED PAIRS (warm/stone-lit + cool/glass-lit) so the
imagery axis swaps with the skin:
- 3–4 product/object renders (the direction-card forms)
- 2 material-sample blobs (Material-exploration ghost card)

### 7a-ter. The PROMPTS are the real deliverable
The single most valuable hand-off is the TEXT prompt fragments used to generate the
plaster and the renders (even rough). A file is one resolution; the prompt is the
generator. These fold into the `imagery.render` capability (§7b) so the SYSTEM
regenerates skin-matched art from the same tokens — no perpetual manual file
collection. Capture them in `assets/renders/PROMPTS.md`.


### 7b. In-card renders (the product objects / iso structures)
**Now:** GENERATED imagery through the AI registry — a capability (`imagery.render`) on the existing
`openai-image` provider whose prompt is COMPUTED from the skin's tokens (gold role, shadow warmth,
ground colour → lighting words), filling `image-slot` wells. Skin flip → regenerate → the same card
holds a glass-world or stone-world render.
**Later (optional, on approval):** react-three-fibre as a scoped `render3d` KIND solver in CV_NODE —
`{occupant:'render3d', model:'x.glb'}` mounts a small per-well canvas whose lights/env/materials are
computed from the same skin tokens. Never page-wide.

### 7c. What stays CSS forever
Block surface lighting (porcelain bevels, dual warm shadows, rim glows, pooled light, debossed wells)
— computed from skin roles, resolution-pure, printable, direct-editable.

## 6. Status vs the bar

The CSS stone skin reaches: plaster tooth (SVG turbulence noise), porcelain two-shadow plaster tooth (SVG turbulence noise), porcelain two-shadow
blocks, debossed wells, rim-glow selection, dashed ghosts, stacks, glowing threads with
junction dots. Not yet at image grade: photographic foliage shadows, the 3-D floor
seam, particle sparkle along threads, and full DiagramSolver-computed graph layout
(demo uses declared node positions + painted threads). These are the named next rungs.
