# AREA · math priors — the math already in the code (wave: ONE-MATH grounding)

> Territory: every place partition/ratio/angle/grid geometry is computed TODAY, at the equation
> level, file:line. Register: provisional — a catalogue to be corrected, not a verdict.
> Evidence tags used throughout: **Observed** (read in the file) · **Inferred** (my interpretation
> of what the code implies) · **Verified** (executed and watched it pass/fail).

## Verified this session

- `node _demo/verify_address.js` → **13/13 pass** (span/encode/decode/lca/zones/slotFor all hold).
- `node _demo/verify_arc.js` → **7/7 pass** (elastic-run plan, deterministic, loud-fail).
- `grep -rl CV_ADDRESS` outside its own file/demo → **one hit**, and it is a *comment*
  (`core/DiagramSolver.jsx:74`, "the address IS the CV_ADDRESS shape") — no code actually calls
  `span/encode/decode/lca/zones/slotFor`. The census's "zero production consumers" claim for
  `cv-address.js` is **still true right now**, not stale.
- `grep -rl CV_ARC` outside its own file/demo → six hits, but every one is `CV_ARCHETYPE_CATALOG` /
  `CV_ARCHETYPE_META` (a substring collision with an unrelated registry). The real `window.CV_ARC`
  (the arc/sequence resolver) has **zero consumers**, confirming the anchor's claim.

Both pieces of "the algebra already exists and nothing uses it" are corroborated, live, today.

---

## §A · The formula catalogue

### A1 · `core/cv-address.js` — the canonical (unconsumed) square-half algebra

| Formula | Class | Evidence |
|---|---|---|
| `span(k,n,parent)`: `start = p.start + (k-1)/n·p.width`, `width = p.width/n` | **(a)** the law itself | cv-address.js:25-30 |
| `encode(path)`: fold `span` over a path → one mixed-radix number | **(a)** | :33-38 |
| `decode(start, radices)`: `k = floor(x·n)+1`, re-base `x = x·n-(k-1)` per level | **(a)** | :41-52 |
| `lca(pathA,pathB)` / `lcaAll`: longest shared address prefix | **(a)** (relational, not geometric, but the anchor's cascade-certainty primitive) | :56-69 |
| `zones(parts, axisPx)`: `round(p·axisPx)` per named fraction | **(a)** ratio→px projection | :74-78 |
| `slotFor(index, capacity)`: `span(index+1, cap)`, `cap` doubles while `index>=cap` | **(a)**, but see the open question below | :83-88 |

**A finding the anchor doesn't have, and it matters for R3:** `slotFor` is a **pure** function — it
takes `capacity` as an explicit argument and holds no internal state. The header comment
("existing slots NEVER move… doubling absorbs growth… the honest left-anchor rule") is an *intent*,
not something the function enforces by itself. Concretely: `slotFor(3)` with default `capacity=8`
gives `span(4,8).start = 3/8 = 0.375`. If capacity later grows to 16 for a *different* index, and
someone re-queries slot 3 as `slotFor(3, 16)`, they get `span(4,16).start = 3/16 = 0.1875` — a
**different number**. The "never moves" guarantee only holds if the **caller** freezes
`{index, capacity}` *together* on the node at insertion and never re-derives capacity for an old
node — i.e. different nodes can legitimately carry *different* denominators forever. This is
workable (older, wider cells; newer, narrower ones sharing the tail of the parent) but it is
**Inferred**, not demonstrated: with zero production consumers, there is no real call site to watch
this invariant hold. Whoever builds R3 needs to decide and document this contract explicitly
(§B and §E return to this).

### A2 · `assets/icons/cv-shapes.js` — the circle-half, independently, twice more than the anchor knew

- `ngon(n, rotDeg, R)` — **line 29-37**: `a = -π/2 + rot + i·2π/n`; vertex `(50+R·cos a, 50+R·sin a)`.
  This is **exactly** `2π/n` (Observed) — the anchor cites the System Map's sunburst as the circle
  half's "nearest existing kin"; this is a **second, independent, closer** site the anchor missed —
  it's already generating true regular-polygon *addresses* (vertex k of n), just for static shape
  outlines, not layout. **(a)**.
- `markBox: { span: 86, … }` on a fixed 100×100 viewBox — every shape's height is 86% of the box,
  width computed to keep the polygon regular. Because the box itself is a normalized (dimensionless,
  scales-to-any-final-size) reference frame, `86` is really `0.86` of the parent — **(a)**, ratio
  already, just spelled in box-units instead of a fraction. (cv-shapes.js:106, 129)
- `roundedFit(ptsStr, r)` + `centroidInradius(verts)` — corner-rounding (quadratic Bézier fillets)
  and area-centroid/inscribed-radius of a convex polygon. **(c) genuinely other** — this is rendering
  fidelity (where does the icon sit inside a rounded hexagon), not address math. No amount of
  partition/order algebra produces this; it's a separate, permanent citizen. (:148-179)
- `edgeSVG`'s curved/free routing: quadratic bow `bow = (routing==='free'?0.34:0.18)·len`, control
  point offset perpendicular to the chord. **(c)** vector/routing geometry, not partition. (:348-354)

### A3 · `core/DiagramSolver.jsx` — the graph solver: SEVEN layout formulas, one already-broken by the anchor's own diagnosis

- `ring(items, radius)` — **line 36-39**: `a = -π/2 + i·2π/n`. This is the **third** independent
  `2π/n` site (after cv-shapes' `ngon` and the System Map's sunburst) — same formula, three separate
  hand-written copies, zero shared code. **(a)**, but a duplication the kernel must dissolve.
- `hub`/`morph` — center fixed at `(cx,cy)`, remaining nodes on `ring()`. **(a)** (rides the above).
- `pipeline`/`timeline` — **line 55, 58**: `x = 40 + i·(VB-80)/(n-1)`. **(b) convertible, but with a
  real mathematical difference from `span()` that must not be glossed over**: `cv-address.span`
  partitions an extent into **n cells** (fencepost: n cells, n-1 internal seams). This formula places
  **n points across n-1 gaps** (fencepost: n points, n-1 intervals). They are not the same partition
  family — converting "point mode" to "span mode" changes where things land, it isn't just a
  relabeling. See §C.
- `tree` — root fixed at top, rest spread with the same `i/(rest.length-1)` point-mode formula.
  **(b)**, same fencepost issue. (:128-134)
- `stack` — `y = 50 + i·(VB-100)/(n-1)`. **(b)**, same issue. (:135-137)
- `quadrant` — `x = 40 + (nd.x??0.5)·(VB-80)`. Authored fraction placed directly — **(a)**, already
  ratio-of-frame, no conversion needed. (:60-61)
- **`glyphgraph` (the W2 placement fix, lines 63-127) — this is the anchor's "first consumer" (R3),
  and it is currently the single worst offender of the anchor's own §4 law, sitting right next to a
  comment that explicitly invokes the algebra it isn't using:**
  - `LAY_SIZE=58`, `LAY_PITCH=58·1.55=89.9` (**a literal, absolute pixel stride, never n-based**),
    `LAY_ROW_PITCH=116`, `LAY_MARGIN=44`, `PER_LINE=3`, `SUB_PITCH=40` — six hand-picked pixel
    constants (:92-95, 117-118) governing a placement scheme (frozen `{row, slot}` addresses,
    brick-wrap sub-lines when a row overflows) that is **structurally the exact same problem
    `cv-address.slotFor` already solves** (stable slot, capacity grows without moving existing
    nodes) — reinvented from scratch, badly, in absolute units, one file away from the real
    primitive, with a comment on line 74 that *names* `CV_ADDRESS` without calling it.
  - The rank computation feeding `row` (longest-path over edges, lines 77-91) is **(c) genuinely
    other** — a topological/graph-distance algorithm, not reducible to any partition formula. It has
    to run *before* any address math can assign a row.
  - The authored override (`nd.x!=null` branch, line 108-109): `x = 30+nd.x·(VB-60)` — **(a)**,
    already ratio-of-frame, consistent with `quadrant`.

### A4 · `core/ContainmentTree.jsx` + `containers.css` — the wash law, exactly as the anchor says, plus its exact constant

- `--_pct: calc(var(--zone-depth) * 2.1%)` (containers.css:77) — wash is **literally** `f(depth)`,
  confirming anchor §2 precisely, down to the constant (2.1%, not the anchor's approximated "~2%").
  **(a)**, already the one-math, in production, today (unlike cv-address). `--zone-depth` itself is
  set by `ContainmentTree.jsx`'s recursive walk (`node.kind==="zone" ? depth+1 : depth`, line 368) —
  so depth is **derived from tree position**, never authored. Strong existing proof of "property
  from address depth."
- `LOD_RULES` (`{summary:{maxPriority:1}, pitch:{maxPriority:2}, full:{maxPriority:99}}`,
  ContainmentTree.jsx:20-24) — a hand-authored threshold table, not partition math. Minor, **(c)**.

### A5 · `system/system-map.html` — treemap, sunburst, and a live worked proof of "one currency"

- **`childValues(pid)` (lines 434-442) is the single best existing proof of the anchor's §4 law in
  the whole corpus, and the anchor doesn't cite it.** The System Map has FIVE incompatible size
  lenses (`SIZERS`: importance/size/links/influence/even — line 414-419), each in a different unit
  (an authored 0-7.5 role score, raw bytes, edge-count, dependent-count, flat 1). Naively swapping
  lenses would make folders and files incomparable (a folder weighted in "importance" next to a file
  weighted in "bytes"). The actual code: **folders always keep their importance-recursive weight
  (`stableFolder`, line 424-426); a folder's loose files share a `budget` fixed in that SAME
  importance currency (`budget = Σ leafW(file)`), and the CURRENT lens only decides each file's
  proportional SLICE of that budget** (`value = budget · metricLeaf(f)/msum`, line 440). The lens
  changes the **ratio**, never the **currency**. This is `childValues` re-deriving, unprompted, the
  exact "ratios all the way, one currency" law Tim states in the brainwave — already built, already
  running, already correct. **(a)**, and a strong law-candidate confirmation (§D).
- `squarify(items,x,y,w,h)` (lines 458-476) — the Bruls et al. squarified treemap: each item's target
  `_a = value/total · (w·h)` **is** ratio-of-parent math **(a)**; but the row-cutting itself (which
  items join a "row," pick horizontal vs vertical cut via a `worst()` aspect-ratio heuristic, greedy
  left-to-right) is **(c) genuinely other** — a 2D rectangle-packing algorithm, not a closed-form
  quotient. See §C — this is the sharpest resistance point found.
- `sunburst` (lines 523-547) — **the actual circle-half weighted generalization of `span()`**:
  `da = span · leaves(k)/tot` per child (line 545), i.e. angle is allocated by proportional weight,
  not uniform `2π/n` — structurally identical to `childValues`'s ratio-of-budget move, just wrapped
  onto an angular axis. **(a)**. One controlled exception: `GAP=0.014` (line 547) is a fixed angular
  inset subtracted symmetrically from each sector for visual breathing room — a real constant, but
  one that never changes *which* ratio produced the sector, only decorates its edges. Flagged as a
  law-candidate pattern in §D, not a violation.
- `districts` / `layers` (lines 549-576) — both re-run `squarify` (same 2D-packing algorithm, so the
  resistance in §C applies twice more) over different regroupings. `layers` additionally computes
  band heights as `sqrt(Σ leafW)` per band (line 568) — a specific **(c)** perceptual-correction
  formula (so that doubling total weight roughly doubles *area*, not linear height) — a real, named,
  reusable rule if the one-math keeps it, but not partition math itself.
- `annular(cx,cy,r0,r1,a0,a1)` (lines 500-506) — the SVG arc-path trig that *renders* a sector once
  `a0,a1` are already known. **(c)**, pure rendering geometry downstream of the ratio math above.

### A6 · `core/cv-arc.js` — the order half, already running, not yet emitting a time coordinate

- The elastic run-length grower (lines 30-32: `while(len<max && total<n) grow`) is **(c) genuinely
  other** — a greedy discrete bin-fill/allocation algorithm (grow elastic roles in listed order until
  the total beat count is hit exactly), not a ratio or angle formula.
- Its OUTPUT — `beats[]`, an ordered array — **is** the anchor's §3 "reading order," but only
  *implicitly*: the order is nothing but array index. **cv-arc.plan() never emits an explicit
  fractional position** (`t = i/n` or similar). Verified 7/7, deterministic, but there is no time
  *coordinate* to hand anywhere yet — just a sequence. This is a real gap, not a nuance (§E).
- Archetype cycling `aff[i % aff.length]` (line 41) — modulo indexing into a repeating pattern.
  **(c)**, partition-adjacent (a mini cyclic partition) but not the same algebra.
- Dial resolution `Math.round((env.warmth[0]+env.warmth[1])/2)` (line 45) — a midpoint average,
  **(c)**, minor, not partition.

### A7 · `core/slide-fit.js` — the frame/content axis, made of one ratio

- `s = Math.min(fw/designW, fh/h)` (line 46) — this **is** anchor §6's "variable frame-content
  coordinates," concretely: scale is the min of two independent axis ratios (frame-extent over
  content-extent), the standard aspect-preserving "fit" computation, with the shorter axis's ratio
  winning and the other axis letterboxed (`used=h·s`, centered via `top=(fh-used)/2`, lines 48-49).
  **(b)/(a) borderline** — it is expressible as ratio math (frame = parent, content = a child extent
  that may *overflow* 1, requiring a `min()` clamp instead of the free partition span/zones assume),
  but it is a **distinct operation** from partition (dividing one extent into several) — it's
  *comparing* two extents to find a common scale. Flagged in §B as a candidate third primitive.

---

## §B · The kernel API — the socket, made precise

The anchor's §10 says the structure needs exactly two plugs: **(a)** a partition function → addresses,
**(b)** an order function → the time coordinate. Having now read every equation, that's *necessary*
but **not sufficient** to actually subsume what's already written — the real gap between "two plugs"
and the code above is that `cv-address.span()`/`zones()` as they exist **only do uniform-n or
pre-computed fractions**; they do not do what `childValues` and `sunburst` *already, independently*
had to invent: **partition an extent by arbitrary per-child WEIGHTS in a foreign unit, normalized
into the parent's currency.** That generalization is the one real addition the kernel must make
before it can claim `childValues`/`sunburst` as consumers instead of parallel reinventions.

Proposed shape (Observed gaps → Inferred primitives; Tim's equations are the authority, this is
scaffolding for where they'd plug in):

1. **`partition(parent, weights) → children[]`** — generalizes `span()` (weights = `n` equal 1s) AND
   `childValues`/`sunburst` (weights = arbitrary positive numbers in ANY unit, normalized internally
   to fractions of `parent`). One function, both existing behaviors are special cases. `parent` is
   `{start,width}` for a linear extent or `{a0,a1}` for an angular one — same shape either way (this
   is why the sunburst and `zones()` are the same law on a different axis).
2. **`project(children[], extentPx, mode) → pixels|angles`** — generalizes `zones()` (mode:'linear')
   to also cover the THREE independently-hand-written `2π/n` sites (cv-shapes `ngon`, DiagramSolver
   `ring`, system-map `sunburst`) under `mode:'angular'`, with an optional fixed `gap` inset (the
   sunburst's `GAP=0.014` pattern, §D). **Explicitly excludes 2D area-packing** — squarify is not a
   mode of this function (see §C); the kernel should say so rather than let a future consumer try to
   force treemap layout through `project()` and get it wrong.
3. **`grow(index, node) → {index, capacity, span}`** — the stable-slot primitive (`slotFor`,
   generalized), with the open contract from §A1 resolved explicitly: **capacity is frozen ON the
   node at first assignment and never recomputed for that node**; `grow()` is only ever called with a
   *new* index to mint a fresh `{index,capacity}` pair, and always reads an existing node's stored
   pair back rather than re-deriving it. This is the one change that lets `DiagramSolver`'s
   `glyphgraph` branch (A3) replace `LAY_PITCH/LAY_ROW_PITCH/PER_LINE/SUB_PITCH` with real calls.
4. **`order(items, roleData) → beats[{…, t}]`** — `cv-arc.plan()`, with one addition: emit an explicit
   `t` (fractional position) per beat, not just array order — and DECLARE once, system-wide, whether
   `t = i/n` or `i/(n-1)` (closes the fencepost inconsistency in §A3/§C, needed before pipeline/
   timeline/tree/stack and the arc's beats can share one time-coordinate law).
5. **`fit(frameExtent, contentExtent) → scale`** (candidate, from A7) — `slide-fit.js`'s
   `min(ratio_x, ratio_y)`, generalized as a named primitive rather than living only inside the paged-
   surface fitter. Open question for Tim's math session: is this truly a 4th primitive, or is it
   `partition()` run in reverse (content as parent, frame as the "child" whose span may legally
   exceed 1, clamped)? Recorded as open, not resolved here.

## §C · What resists the one-math (found, not glossed over)

1. **2D area-packed layout (squarify/treemap) is a different algorithm CLASS, not a mode of
   partition.** `system-map.html:458-476` (and its two reuses in `districts`/`layers`). Partition
   math (linear or angular) is fundamentally 1-dimensional: divide one extent by weight. Packing N
   weighted items into a 2D rectangle while keeping cells visually "squarish" requires the greedy
   `worst()`-heuristic row-cutting (Bruls et al.) — genuinely combinatorial, no closed form. It
   *consumes* ratio math internally (`_a = value/total·area`) but the *shape* of the cut is not
   derivable from any single equation. This should be a **registered sibling algorithm**, explicitly
   NOT folded into `project()`, so nobody breaks it trying to force-fit it later.
2. **Graph-topological rank** (`DiagramSolver.jsx:77-91`, longest-path layering over edges) has to
   run *before* any address math assigns a glyphgraph node's row — it depends on edge structure, not
   a count or a weight. Genuinely other; a precondition to partition, not a form of it.
3. **Rendering-fidelity geometry**: corner rounding + centroid/inradius (`cv-shapes.js:148-179`),
   Bézier bow offsets for curved/free edge routing (`cv-shapes.js:348-354`), and the arc-path trig
   `annular()` (`system-map.html:500-506`). All permanent, all downstream of address math, none of
   them expressible as partition or order.
4. **An internal inconsistency the one-math should force a decision on, not inherit**: `ring()`
   places n points using `n` as the divisor (correct for a closed loop — no fencepost); `pipeline`/
   `timeline`/`tree`/`stack` place n points using `n-1` (open extent, correct fencepost for POINTS);
   `span()`/`zones()` divide into n CELLS (correct fencepost for SPANS/regions). All three are
   legitimate for their own geometry (closed loop vs. open point-sequence vs. cell-partition) but
   **DiagramSolver currently mixes point-mode and never touches the cell-mode primitive at all** —
   this needs a resolution-first declaration (§E), not silent convergence.
5. **The `slotFor` growth contract is underspecified, not resistant, but unresolved** — see §A1.
   Zero production consumers means there is no real usage to observe the "existing slots never move"
   invariant against. This is a genuine open question for the math session, flagged rather than
   assumed.
6. **cv-arc's elastic run-length allocator** (greedy bin-fill to hit an exact beat count) is a
   discrete allocation algorithm, not a ratio — it decides HOW MANY beats a role gets, which is a
   precondition to the (currently-missing) `t=i/n` order coordinate, not a substitute for it.

## §D · Law candidates (surfaced by the math itself, not asserted from the brainwave)

1. **"A lens changes the ratio, never the currency."** `system-map.html`'s `childValues` (A5) is a
   *working, running* instance of anchor §4 solving a real cross-unit problem (bytes vs. links vs.
   authored-importance) — not a hypothetical the brainwave introduces, but a law the codebase already
   independently discovered under pressure. Worth naming and generalizing explicitly, and worth
   pointing at as evidence the kernel's `partition(parent, weights)` generalization (§B.1) is not
   speculative — it's lifting an already-proven pattern out of one file into the shared home.
2. **"Freeze the address's INPUTS at assignment, never its OUTPUT."** `cv-address.slotFor` freezes
   `{index, capacity}`, not a pixel position — the pixel position is *always* re-derived from those
   frozen inputs via `span()`. This refines "derived, never stored" (anchor §4) with its one
   principled exception: growth-stability requires freezing *something*, and the candidate law is
   that the something is the minimal set of inputs to the derivation, never the derived value itself.
3. **"A lens is a projection, never a layout change."** Already true and running: System Map's
   `SIZERS`/`COLORERS` registries resize files without moving zones (anchor §5's "names attached to
   addresses" — this is the working precedent, not a future promise).
4. **"A constant may buy visual breathing room between ratio-derived cells, never inside the ratio
   itself."** The sunburst's `GAP=0.014` (A5) is a hardcoded number that nonetheless doesn't violate
   "ratios all the way" — it's subtracted symmetrically post-hoc, changing presentation, not which
   ratio produced the boundary. Worth naming explicitly so future reviewers don't flag every small
   inset constant as a violation, nor use "it's just a gap" to smuggle in real hardcoding.
5. **"1D partition and 2D packing are different citizens; don't let one grow legs it doesn't have."**
   A candidate governance law straight out of §C.1: the one-math's authority is over cells/sectors/
   points on ONE axis (or an angular one); treemap-style area packing must be registered as its own
   algorithm, not squeezed under the same socket, so a future "just make everything go through
   partition()" impulse doesn't quietly break the treemap.

## §E · Scope additions (concrete, file-addressed, not hypothetical)

- **Generalize `cv-address.span()`/`zones()` to weighted partition** (§B.1) — lift `childValues`'s
  budget/msum ratio-of-ratio logic (system-map.html:434-442) out of that file and into
  `cv-address.js` as a first-class function; it is currently stranded, duplicated in spirit by the
  sunburst's own weighted-angle code (system-map.html:539-547).
- **Rewrite `DiagramSolver.jsx`'s glyphgraph placement (lines 63-127)** to call `cv-address.slotFor`
  + `span` once the growth contract (§A1/§B.3) is resolved, retiring `LAY_PITCH`/`LAY_ROW_PITCH`/
  `PER_LINE`/`SUB_PITCH`/`LAY_MARGIN` — this is the anchor's named "R3, first consumer," and this
  wave found it is not a green-field build: it's a **reconciliation** of an already-written, already-
  half-working, ad-hoc reinvention sitting one file away from the real primitive it needs.
  `feedback-glyphic-course-corrections.md` point 4 ("placement must be RELATIVE, totally redone")
  applies here directly, with a specific file and line range now attached to it.
- **Register squarify/treemap as its own algorithm citizen** (§C.1, §D.5) — explicitly NOT a
  `project()` mode, so the "one math" doesn't get stretched to cover something it structurally can't.
- **Resolve the n vs. n-1 fencepost convention** (§C.4) system-wide before R3 touches `pipeline`/
  `tree`/`stack`/`timeline` — a one-line decision, but it needs to be made once, centrally, not per
  layout.
- **Add an explicit `t` (fractional position) to `cv-arc.plan()`'s beats** (§A6, §B.4) — today order
  is array-index-only; the anchor's "time coordinate" doesn't exist as a number anywhere yet.
- **Decide the `slotFor` growth contract explicitly** (§A1, §C.5) before anything depends on it —
  zero consumers today means this is cheap to decide now and expensive to discover as a bug later.

---

**Files read in full**: `core/cv-address.js`, `assets/icons/cv-shapes.js`, `core/DiagramSolver.jsx`,
`core/ContainmentTree.jsx`, `core/containers.css`, `core/cv-arc.js`, `core/slide-fit.js`,
`system/system-map.html` (lines 400-660, the sizing/colour/layout registries + squarify/sunburst/
districts/layers — the file continues past 660 into interaction/UI code outside this territory's
math scope), `assets/icons/CvIcon.jsx` (confirmed its polygon points are a documented byte-identical
*fallback* of `cv-shapes.js`'s output, not a fourth independent geometry site).
