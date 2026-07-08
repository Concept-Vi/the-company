---
type: research · inventory
register: descriptive
area: tokens · axes layer (design/claude-ds)
date: 2026-07-09
---

# §A · TOKEN & AXES INVENTORY — Complete Account

## The token architecture (L0 → L1 → L2)

**L0 (primitives, single-sourced):**
- colors_and_type.css (lines 10–140): Surfaces, inks, brand accents, status, borders, shadows, radii, spacing scale
- **The --ramp-1..4 sequence** (lines 72–79): Gold → Bronze-warm → Bronze-2 → implicit bronze-soft. Ordered, calibrated from deck samples (analysis/DIAGRAMS.md). **Observed**: Monotonic lightness—each stop is strictly darker than the previous (L: 0.82→0.62→0.58→0.46), though not yet checked against WCAG contrast pairs.

**L1 (role tokens, derived):**
- Zones (--zone-content, --zone-panel, --zone-source, --zone-reject, --zone-*-ink, --zone-*-wash) — **Inferred** via diagram.css line 54 and colour-mixing patterns in theme.css. These are computed from (L0 brand + --zone-ground) mixed at variable intensity. Not explicitly listed in read files; must be generated or live in containers.css (unread).
- Communication roles (--comm-*, --comm-line) — referenced in diagram.css line 56, derived from --accent-communication.

**L2 (component tokens):**
- All the helpers (--control-h, --row-h, --dgm-node-*, --state-*, --focus-ring, etc.) — these reference L0/L1.

### Scope of tokens (by file):

| File | Tokens | Role | Ratio/Absolute | Status |
|---|---|---|---|---|
| colors_and_type.css | Surfaces, inks, brand (--accent-*), status (--status-*), borders, shadows, radii, spacing (--s-*) | L0 primitives | Mix (px for discrete; colours inherit theme) | ✓ Complete |
| depth.css | --elev-0..5 (shadow ramp), --glow-active, --elev-inset, --grain-*, --hairline*, --blur-* | Shadow + grain algebra | Computed colours; px for blur | ✓ Complete |
| motion.css | --dur-* (90ms–480ms), --ease-* (cubic-bezier), --move-* (8px–120%), --stagger-* | Animation tokens | **MIXED**: durations rational; distances absolute px except --move-off (120%, proportional off-frame) | ⚠ Partial |
| layout.css | --z-* (0–9999 scale), --scrim-fill | Z-index + overlay | Numeric (unitless) ✓; scrim colour relative to --ink ✓ | ✓ Complete |
| surfaces.css | --bp-* (480px–1440px breakpoints), --frame-*-ar, --frame-*-w, --frame-*-h, --grid-* (12%, 7.5%, 76%, 46%), --touch-min, --mobile-* (44px, 56px, 52px), --gutter-* | Surface architecture | **DERIVED**: frame height = frame-width / aspect-ratio ✓; grids as % ✓; chrome as discrete px ✓ | ✓ Exemplary |
| sizing.css | --scale-ratio (1.25), --scale-base (16px), --fs-* (clamp min/pref/max), --lh-*, --space-fluid-*, --measure*, --size-xs..hero (16px–96px ramp) | Type scale + element sizing | **FLUIDITY LAW**: every size is clamp() or viewport-relative ✓ (except --size-* ramp, which are discrete px — **Inferred** intentional, as they are the VALUE-UNITS of the size axis) | ✓ Excellent |
| states.css | --skeleton-*, --focus-ring*, --state-hover/press/selected, --disabled-opacity | Interaction states | Colours relative; opacity numeric ✓ | ✓ Complete |
| theme.css | --zone-ground, --zone-ground-soft, --zone-intensity, --gold-intensity, --ink, --ink-2..5, --border-*, --shadow-c, --grain-opacity | Theme multipliers | All derived via color-mix() against --zone-ground; swaps the ground ✓ | ✓ Complete |
| density.css | --density (0.8/1/1.25), --d-1..12 (computed as px × --density), --control-h, --row-h | Layout breathing room | **RATIO-BASED**: all spacing scales with --density multiplier ✓ | ✓ Complete |
| texture.css | --hatch-angle (45deg), --hatch-gap (6px), --hatch-weight (0.6px), --hatch-color, --blueprint-color, --blueprint-grid-size (24px), --blueprint-grid-opacity | Pattern fills | **ABSOLUTE**: px for gap/weight/grid-size ⚠ | ⚠ Static patterns, not computed addresses |
| diagram.css | --dgm-stroke-*, --dgm-node-*, --dgm-connector-*, --dgm-arrow-size (8px), --dgm-corner-radius (12px), --dgm-edge-* (flow/dependency/reference/rejected colours) | Diagram vocabulary | Mostly relative (reuse radius tokens, zone inks); sizes discrete px | ✓ Complete |
| canvas.css | *(unread)* | *(unread)* | — | — |
| focus.css | *(unread)* | *(unread)* | — | — |
| controls.css | *(unread, component layer)* | *(unread)* | — | — |
| icons.css, dataviz.css, imagery.css, provenance.css, export.css | *(unread, component / surface-specific layers)* | — | — | — |

---

## AXES INVENTORY — How value spaces are declared

Each axis follows the **CV_AXES** shape (axis-core.js): { id, label, groups?[], values[], default } + register/resolve/query verbs.

| Axis ID | Groups | Values | How value resolves | Zero | Status |
|---|---|---|---|---|---|
| **color** | brand, semantic, ink, communication, neutral | gold, gold-deep, gold-soft, bronze, bronze-2, tan, success, warning, error, info, pending, ink, ink-2, muted, soft, sage, sage-soft, paper, surface + aliases (amber→warning) | → token (var(--...)) | — | ✓ Complete |
| **size** | inline, standard, feature | xs, sm, md, lg, xl, hero | → token (--size-*) + meta.px (16–96px) | — | ✓ Complete |
| **form** | none, polygon, round | none, triangle, square, diamond, pentagon, hex, heptagon, septagon, octagon, circle | → CV_SHAPES.geom (resolve=null, consumers render) | 'none' | ✓ Complete |
| **depth** | flat, raised, system | flat, d1–d6, normal | → token (--elev-*) + meta (dy, blur, opacity) | 'flat' | ✓ Complete |
| **motion** | static, ambient, attention, interactive, process | none, breathe, float, pulse, glow, bob, tilt, spin | → CSS class (mo-*) from motion.css | 'none' | ✓ Complete |
| **ordinal** | ramp | o1, o2, o3, o4 | → token (--accent-gold, --accent-gold-deep, --accent-bronze, --accent-bronze-2) + meta.L (lightness) | — | ⚠ **CONFLICT**: uses different tokens than --ramp-1..4 |
| **space** | inner, between, layout | s0–s24 (0–96px, 8px rhythm) | → token (--s-*) + meta.px | 's0' | ✓ Complete |
| **texture** | none, line, field | none, hatch, lines, vert, cross, grid, dense, dots | → *(no payload defined; CV_SHAPES.markSVG must render)* | 'none' | ⚠ **DRIFT**: 8 values registered but only hatch + blueprint implemented in tokens/texture.css |
| **fill** | none, surface, colour | none, paper, wash, tint | → meta.ramp recipes, not tokens | 'none' | ✓ Complete (ramp metadata, not literal tokens) |
| **symbol** | *(live from CV_ICONS taxonomy)* | *(all icons in CV_ICONS.data)* | → SVG body via resolve(I.get(id)) | — | ✓ Live, rebuilds on foundry add |

**Observed**: The axes share identical registration/query/resolve shape (homomorphic with CV_REGISTRY and CV_AI). Axes are TYPED VALUE SPACES, not layers over tokens — the tokens ARE the values.

---

## §B · JOINS TO THE ONE-MATH

### The ramp as ordered address run

**Current state:**
- --ramp-1..4 live in colors_and_type.css (lines 72–79), calibrated, ordered, monotonic lightness.
- ordinal-axis.js hardcodes o1–o4 to DIFFERENT tokens (--accent-gold, --accent-gold-deep, --accent-bronze, --accent-bronze-2).
- Both are sequences over the same conceptual space (gold→bronze scale) but point to different sources.

**The brainwave join:**
The ordinal axis should resolve position-i-of-n → the stop at that ramp position. The ramp tokens are the ADDRESS RUNS. Under one-math, `ordinal(i, n)` means "get the address (and its colour) of the i-th of n equally-spaced addresses along the ramp."

**Action**: Unify ordinal-axis.js to reference --ramp-* tokens (or declare what the ordinal STOPS really are so --ramp-* mirrors them exactly).

---

### Texture: from static patterns to computed addressed grids

**Current state** (tokens/texture.css, lines 14–70):
```css
--hatch-angle: 45deg;
--hatch-gap: 6px;     /* ABSOLUTE */
--blueprint-grid-size: 24px;  /* ABSOLUTE */
.hatch-band { background-image: repeating-linear-gradient(…); }
.blueprint::before { background-image: linear-gradient(…) grid pattern; }
```
Texture is **decorator CSS**, not address-generating.

The texture-axis registers 8 texture types (none, hatch, lines, vert, cross, grid, dense, dots), but only hatch + blueprint have implementations.

**The brainwave join:**
Replace static repeating-linear-gradient with COMPUTED GRIDS:
- Square division (x/n): partition the fill width into n cells; each cell is a block address `block(i, n)`.
- Circle division (2π/n): partition the ring into n sectors; each sector is an address `sector(i, n)`.
- Each cell/sector is then a TOKEN ATTACHMENT POINT (the fill can have per-cell colour, opacity, pattern via addressing).

**Where the math lives:**
- The partition functions: `span(k, n, parent)` in cv-address.js (ALREADY EXIST; zero consumers).
- Reading order: derived from partition (e.g., row-major for square, angular for circle).
- The texture-axis values (hatch, grid, dots, etc.) become ADDRESS PATTERNS, not static fills.

**Action**: 
1. Implement the square-partition grid generator (use span/n math, not hardcoded gap).
2. Implement the circle-partition sector generator (Tim's 2π/n equations when they arrive).
3. Each generated cell/sector gains an address and can carry a colour token.
4. Generalize texture.css pattern definitions from static to parameterised.

---

### Tokens at addresses: the glyphic fill cell model

**Current state:**
Glyphic marks (ring + fill) have a colour. The fill is monochrome or a gradient ramp (fill-axis.js).

**Under one-math:**
If the fill is a computed grid (x/n cells or 2π/n sectors), each cell is addressable. A data binding can then say: "cell (i, n) → resolve its colour from the data," making the fill a **live, addressed surface** where every cell is a distinct identity.

This is the G8b binding pipeline (BRAINWAVE §2): the binding already resolves per-address; texture makes the addresses.

**Where this connects:**
- cv-address.js: `span(k, n, parent)` → a cell's address, including ancestry.
- G8b resolveBindings: per-address resolution (already works; just needs finer grain).
- Tokens: per-address colour token attachment (new).

**Action**: Wire the computed-texture cell addresses into the data-binding system so a portfolio glyphic can colour each cell by its resolved state.

---

### Reading order from partition math

**Current state (BRAINWAVE §3):**
"The equations give reading order for sequence and time coordinate."

**Current axis support:**
ordinal-axis.js has a `stopFor(i, n)` function that maps position-i-of-n to a ramp stop. This is a ONE-DIRECTION map (i,n → stop id).

The inverse (what is the reading order of a set of addresses?) is not yet a formal axis or function.

**Under one-math:**
The partition function naturally yields a reading order:
- For x/n grid: row-major, left-to-right, top-to-bottom.
- For 2π/n sectors: angular, clockwise, starting at angle 0.
- This order is DERIVED from the math, not assigned.

**Where this lives:**
cv-arc.js (ported, verified, zero consumers) is the "arc resolver" that "plans a telling's beats over a sequence." It is waiting for the time coordinate that reading order provides.

**Action**: Expose a reading-order function (part of the texture/partition algebra) so cv-arc.js can wire it as the time axis for sequencing.

---

### Zones as containment-derived wash levels

**Current state:**
Zones (--zone-content, --zone-panel, --zone-source, --zone-reject) are referenced throughout but not explicitly defined in the read files. They are INFERRED to be derived from (L0 brand + --zone-ground) mixed at --zone-intensity.

**Under one-math (BRAINWAVE §3):**
Spacetime relations (contains ↔ contained-by, before ↔ after) are DERIVABLE from address math, not stored. Zones already implement this: a zone's depth (content → panel → nested) is a WASH LEVEL, derived from zone nesting depth (how deep in the containment tree).

**Where this is partially true:**
containers.css (unread) likely computes zones from a containment tree. The fill grid's per-cell zone (if a cell is inside a mark that is inside a canvas) can derive its wash level from the nesting depth.

**Action**: Verify zone derivation in containers.css; confirm it's derivable from address ancestry.

---

### Ratios all the way: absolutes hiding in the system

**Current state (BRAINWAVE §4):**
The system is **mostly** ratio-based:
- Type: clamp() ✓
- Spacing: --s-* (8px rhythm) ✓ or --d-* (--density multiplied) ✓
- Grids: % ✓
- Frames: derived from aspect ratio ✓

**Absolutes that remain:**
- motion.css: --move-xs (8px), --move-sm (16px), --move-md (32px), --move-lg (64px) — these are discrete distances, not fractions of container. **Inferred**: intentional (for "snap to grid" motion), but worth questioning if they should be relative to mark size or container.
- texture.css: --hatch-gap (6px), --blueprint-grid-size (24px) — these are decorative and may be intentional, but they are not derived from the fill width (x/n would derive them).
- diagram.css: --dgm-arrow-size (8px), --dgm-corner-radius (12px) — discrete structural measures.
- surfaces.css: chrome heights (--mobile-statusbar 44px, --touch-min 44px) — universal constants, not derived.

**The law violation:**
texture.css uses absolute px for grid spacing instead of deriving it from the fill width. Under the brainwave, --hatch-gap should be implicit (computed from fill-width / n + line-weight).

**Action**: Flag motion distances and texture gaps as candidates for proportional derivation; verify intent before changing.

---

## §C · DISCONNECTED & UNUSED

### Texture axis / implementation mismatch

**Observed:** texture-axis.js registers 8 values (none, hatch, lines, vert, cross, grid, dense, dots); tokens/texture.css implements only 2 (hatch, blueprint).

**Impact:** The texture axis overpromises. Consumers trying to use 'lines' or 'grid' will find no rendering path.

**Status:** DRIFT — axis and implementation out of sync.

**Action:** Either (a) implement the remaining 6 patterns in CSS, or (b) trim the axis to match the implementations (hatch, blueprint only).

---

### Zone tokens: implicit derivation, no registry

**Observed:** Zone roles (--zone-content, --zone-panel, --zone-source, --zone-reject, --zone-*-ink, --zone-*-wash) are used throughout diagram.css and referenced in theme.css but never explicitly declared in the read files.

**Inferred:** They are likely computed in containers.css (unread) or generated by a script.

**Impact:** Can't verify zone derivation or authoring path without reading containers.css.

**Status:** UNCONFIRMED — need to read containers.css to locate zone token generation.

**Action:** Read /home/tim/company/design/claude-ds/core/containers.css; verify zone derivation is resolution-first (computed from [L0 brand + --zone-ground] at layers).

---

### Ordinal axis vs. ramp tokens

**Observed:** 
- --ramp-1 through --ramp-4 are the canonical warm-metal ramp (colours_and_type.css lines 72–79).
- ordinal-axis.js o1–o4 reference different tokens (--accent-gold, --accent-gold-deep, --accent-bronze, --accent-bronze-2).

**Inferred:** The ramp tokens were defined first; ordinal was added later and chose its own token homes instead of pointing at --ramp-*.

**Impact:** Two homes for the same concept (ordinal ramp). A change to one won't propagate to the other.

**Status:** DRIFT — violates the "one home" law.

**Action:** Unify: either (a) make ordinal-axis.js point at --ramp-* tokens, or (b) make --ramp-* point at the tokens ordinal uses (and rename for clarity).

---

### Unread files (component layer)

- canvas.css (referenced in styles.css line 15)
- focus.css (referenced in styles.css line 11)
- controls.css, icons.css, dataviz.css, imagery.css, provenance.css, export.css (component and surface-specific layers)

These are likely downstream consumers, not core token sources, but should be scanned for hardcoded literals that should be tokens.

**Action:** Quick scan for "--" pattern misses and hardcoded px/colours in these files.

---

## §D · LAW CANDIDATES

### The Resolution-First Law (existing, reinforced)

**Observed:** Every token has ONE home (colors_and_type.css, tokens/*.css, axes/*/). Consumers reference via var(--token) or axis resolve.

**Violation:** ordinal-axis and --ramp-* are two homes for the ordinal ramp.

**Statement:** *Every concept (colour, size, timing, pattern) has exactly one canonical definition. Everything else references that definition. A second home is drift.*

**Enforcement:** At registration, check for duplicate token homes or parallel value sets. Aliases (amber→warning) are OK if the alias points at the true home.

---

### The Monotonic Law (existing, exemplary)

**Observed:** ordinal-axis.js lines 27–30 enforce lightness ordering at registration:
```javascript
if (!(STOPS[i].meta.L < STOPS[i - 1].meta.L))
  throw new Error('[ordinal-axis] ramp must darken monotonically');
```

**Statement:** *Ordinal sequences must darken monotonically. Lightness order is the strongest perceptual cue for series-ordering; breaking it is a category error. Check at registration, fail loud.*

**Application candidates:**
- Other ramps (elevation depth blur values should follow a similar perceptual gradient).
- Size sequences (should progress monotonically in a perceptually even way).

---

### The Fluidity Law (existing, exemplary)

**Observed:** sizing.css (lines 15–40) uses clamp() for every type size and fluid spacing. No breakpoint-specific hardcoding.

**Statement:** *Responsive values flow smoothly across all viewports via clamp(min, pref, max). Never hardcode a type size at a breakpoint; let the function handle the transition.*

**Application candidates:**
- Motion distances (--move-* could be clamp() based on mark size or container width).
- Texture gaps (--hatch-gap could be clamp() based on fill width and desired cell count).

---

### The Field vs. Role Law (emerging)

**Observed:** 
- **Fields** (ordinal, symbol): ORIENTATION without reading. You don't read "o2 = second"; you see the colour and orient by its position in the sequence. Meaning is not in the field; it IS the field.
- **Roles** (colour, motion, fill): semantic bindings. "gold = decision," "pulse = attention." Meaning is separate (lives in CV_MEANING, which is loadable).

**Statement:** *Some axes are FIELDS (intrinsic, not contextual). Mark them in axis metadata (meta.field = true or similar). Fields have one immutable meaning; roles are contextual and loadable.*

**Implications:**
- Field axes can't be recoloured by theme or meaning profile (symbol is always a symbol, ordinal ramp order is always darkening).
- Role axes can be re-assigned meaning (colour 'gold' means 'decision' in one context, 'positive' in another).

---

### The Address Derivation Law (new, from brainwave)

**Statement:** *An address is an identity derived from partition math, not assigned by content or naming. An address carries its ancestry (lineage), so cascades and zones resolve automatically from the address structure.*

**Implications:**
- Texture cells are addresses (result of x/n or 2π/n partition), not decoration.
- Identity (addressed cell) precedes meaning (colour token attached to it).
- Reading order is derived from address sequence, not authored.

---

### The Grid-Type Law (emerging from surfaces.css)

**Observed:** surfaces.css lines 31–47 define frame dimensions as TYPE systems:
```css
--frame-desktop-ar: calc(1440 / 900);  /* ratio, the TYPE */
--frame-desktop-w:  1440px;             /* base dimension */
--frame-desktop-h:  calc(w / ar);       /* DERIVED */
```

**Statement:** *Dimensions that follow a rule should declare the rule (aspect ratio, scale factor), not the result. The result is derived. Adding a new surface = declare ar + base w; height computes.*

**Application candidates:**
- Type scales (declare scale-ratio; sizes derive).
- Spacing scales (declare rhythm; steps derive).
- Texture grids (declare fill-width and cell-count; gap derives).

---

## §E · SCOPE ADDITIONS FOR ONE-MATH BUILD

### 1. Computed-texture implementation

**Status:** NOT STARTED

**Scope:**
- Replace tokens/texture.css static patterns with parameterised grid generators.
- Implement `generateSquareGrid(fillWidth, n, strokeParams)` → SVG grid of n cells.
- Implement `generateCircleGrid(radius, n, angleParams)` → SVG sectors of n angular divisions.
- Each cell/sector is generated with a stable address id (e.g., `cell-3-of-12`).
- Register texture values in the axis to point at generator functions (resolve = generator(…)).

**Dependencies:** Tim's circle equations (2π/n) from his separate math session.

**Touches:** tokens/texture.css, axes/texture/texture-axis.js, CV_SHAPES.markSVG (the compositor).

---

### 2. Token-at-address binding

**Status:** PROPOSED

**Scope:**
- Each generated texture cell should be able to carry a per-cell colour token (via address).
- Extend G8b resolveBindings to resolve per-cell bindings.
- A glyphic's fill-binding can declare: "cell (i, n) → colour from field `status` of data item i" or similar.
- The compositor renders the cell with the resolved colour.

**Dependencies:** Computed-texture cells with stable addresses.

**Touches:** cv-address.js (address → data), G8b binding engine, CV_SHAPES.markSVG.

---

### 3. Ramp unification

**Status:** PARTIALLY DONE

**Scope:**
- Make ordinal-axis.js reference --ramp-* tokens (not --accent-gold, etc.).
- Or: rename --ramp-* to clearly match ordinal-axis stop names (--ordinal-1, --ordinal-2, etc.) and update ordinal-axis.js.
- Verify --ramp-* and ordinal STOPS are truly the same sequence and order.
- Ensure the ramp is the ONE HOME for warm-metal ordered sequences.

**Dependencies:** None; purely a unification task.

**Touches:** colors_and_type.css (--ramp-*), axes/ordinal/ordinal-axis.js.

---

### 4. Reading-order formalization

**Status:** DESIGNED (BRAINWAVE §3); NOT WIRED

**Scope:**
- Expose a function: `readingOrder(addresses, partitionType)` → ordered array of address ids (row-major for square, angular for circle).
- Wire this into cv-arc.js (the arc resolver waiting for time coordinate).
- Make it available as a resolved axis value or a CV_ global function.

**Dependencies:** Computed-texture partition logic (square and circle).

**Touches:** cv-address.js (extend or create cv-reading-order.js), cv-arc.js (wire reading order as time), axes/ordinal/ordinal-axis.js (or new axis if reading order is its own axis).

---

### 5. Texture axis alignment

**Status:** DRIFT SIGNAL

**Scope:**
- Either implement the 6 missing texture patterns (lines, vert, cross, grid, dense, dots) in tokens/texture.css, OR
- Trim texture-axis.js to match the 2 implemented patterns (hatch, blueprint).
- Decision: depends on whether the 6 patterns are in-scope or over-promise.

**Action:** Ask Tim whether all 8 texture types are needed or just the 2 currently used. If 8: implement them. If 2: trim axis.

**Touches:** tokens/texture.css, axes/texture/texture-axis.js.

---

### 6. Zone derivation explicit

**Status:** UNCONFIRMED

**Scope:**
- Read containers.css to locate zone token generation.
- Verify zones are derived from (L0 brand + --zone-ground) at containment depth.
- Document the derivation path: how is --zone-content computed? What makes --zone-panel different?
- Ensure the path is resolution-first (no hardcoded zone RGB values; all mixed from primitives).

**Touches:** core/containers.css, colors_and_type.css (zone derivation rules).

---

### 7. Motion distances as proportional

**Status:** CANDIDATE (verify intent)

**Scope:**
- --move-* (currently 8px, 16px, 32px, 64px, 120% off-screen) are absolute or proportional off-screen.
- Question: should --move-sm be "1/4 of container width" or a fixed 16px? Should it scale with mark size?
- Decision point: Tim's original intent. If motion is tied to mark size (a glyphic that moves should move proportionally to its own size), make them relative. If they are universal motion quanta (all motion steps are these 4 distances), keep absolute.
- **Current code suggests intent:** --move-off is already proportional (120%); others are absolute. Mixed strategy.

**Action:** Clarify with Tim; if proportional is the intent, use clamp() or relative units. If absolute, document the rational.

---

### 8. Texture gaps as proportional

**Status:** CANDIDATE (verify intent)

**Scope:**
- --hatch-gap (6px) and --blueprint-grid-size (24px) are absolute.
- Under one-math, these should be DERIVED from fill width and desired cell count (x/n, 2π/n).
- A fill that is 120px wide and has 4 cells should have ~30px per cell (not a hardcoded 6px gap).
- Question: are the current absolute sizes intentional (aesthetic tuning), or should they be derived?

**Action:** When implementing computed-texture (scope item 1), decide whether texture parameters are user-tunable (knobs on the axis) or derived from mathematics. If derived, remove from tokens/texture.css.

---

### 9. CV_ORDINAL.stopFor(i, n) usage

**Status:** DESIGNED (exists); NEEDS INTEGRATION

**Scope:**
- ordinal-axis.js exports CV_ORDINAL.stopFor(i, n) and CV_ORDINAL.tokenFor(i, n).
- These are used wherever an ordered sequence needs a colour: diagram rings, metric ramps, steppers.
- Verify these functions are actively used; if not, they're drift.
- Under one-math, ensure this is the entry point for "get the colour of position i in an n-element sequence."

**Action:** Grep for CV_ORDINAL usage across the codebase. If unused, mark for removal. If used, ensure it's the canonical entry point.

---

## SUMMARY: Biggest joins, biggest finds, path

**BIGGEST JOIN**: Texture is the entry point. Currently static CSS patterns (hatch, blueprint); under one-math, texture becomes **COMPUTED ADDRESSED GRIDS** (x/n cells, 2π/n sectors), each cell an addressable identity carrying its own token. This is where partition algebra meets the visual surface.

**BIGGEST FIND**: The system is **almost ratio-all-the-way**, but texture.css and motion.css have absolute px that should be either (a) derived from mathematics (texture gap = fill-width / n), or (b) intentional quanta (motion step = universal 16px). The confusion is unresolved.

**PATH**: 
1. Read containers.css to confirm zone derivation.
2. Implement computed-texture generators (square x/n + circle 2π/n from Tim's equations).
3. Unify ordinal-axis to point at --ramp-* tokens.
4. Wire reading-order function into cv-arc.js.
5. Trim or implement texture axis to match implementations.
6. Resolve intent: texture gaps and motion distances as derived or intentional.

**Files to explore next**: core/containers.css, app/registry.js, cv-glyphic.js (compositor), cv-address.js (verify zero consumers).

---

**Written by**: One-Math Wave Reader (tokens/axes territory)  
**Timestamp**: 2026-07-09  
**Confidence**: Observed facts + explicit code paths verified; Inferred from pattern-matching and naming; Unread: containers.css, canvas.css, focus.css, component layers.
