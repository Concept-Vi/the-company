# BRAINWAVE — ONE MATH: the addressed fill (Tim, 2026-07-03)

> **Register: provisional, growing — a discovery being stretched, not a spec.** Tim's brainwave verbatim
> in §0; each part expanded in §1-§9; the cross-system connections grounded in the census
> (census/AREA-*.md) so nothing here is speculation about what exists — only about what it becomes.
> Tim is deriving the equations in a separate session; this doc is the structure that RECEIVES them
> (the socket is §10). Everything open; his eye corrects live.

## §0 · The brainwave (verbatim, preserved)

"In glyphics, the form/outer layer has fill, and the fill has a texture layer which makes grids and
lines and geometric proportional lines, which could also be rotated, and have colours change. In a
separate session I'm doing all the maths behind this, and the texture and fill made me realise. The
lines/grids/internal geometry is just maths for the square x/n and the circle 2pi/n, which gives block
addresses — it gives the address of the squares, while the equations I have already gives the circles.
With the tokens, each division of the fill/thing is a distinct identity/address, so can have colour
tokens. It also has order, the equations give reading order for sequence and time coordinate. the
texture and fill can be computed to squares and grids, and with everything being ratios none of it is
hardcoded and it just resolves. Comparisons, views, orders — whatever purpose the surface needs to
serve, it's just names attached to addresses, addresses come with their ancestry so always works.
Movement too, if squares are computed grids, blocks, pixels, then movement holds different axes.
Sliding off screen, vs two moving and splitting, reforming into something else — these are additional
axes that give variable frame-content coordinates. So identity, it's just if there's an address for it
or not. So any blocks can be considered and operated as one, just by being a registered identity in
the system. Any group, any filter, any selection, one operation. And so, can coloured or otherwise
interact with any of the other axes, independently and as part of any group, the cascades and
certainty of common ancestor make it automatic, given every node/thing is an address containing its
lineage."

## §1 · The core: texture is address-generating math

The glyphic's anatomy (Tim's own recorded correction, glyphic-system.html §1b): the element is a
perfect square; the ring bounds an inner space (the fill) and an outer space. The brainwave adds the
third depth: **the fill has internal geometry — a texture layer of grids, lines, proportional
divisions — and that geometry is not decoration. It is the address math made visible.**

- A square divided x/n → a grid of cells. Each cell is a **block address**.
- A circle divided 2π/n → angular sectors. Each sector is an address. (Tim's separate-session
  equations already give the circles.)
- Rotation, colour-change on the lines: transforms and tokens applied to *addressed* geometry.

**The algebra for the square half already exists in the folder and is consumed by NOTHING** —
`core/cv-address.js`: `span(k, n, parent)` IS x/n (children partition a parent's [0,1)),
`encode/decode` is the mixed-radix path (ancestry in the address), `lca` is the common-ancestor
certainty, `zones(parts, axisPx)` is already the grid projection. The census proved it has zero
production consumers (census/AREA-canvas-engines §C1). The brainwave is what it was FOR: not a layout
helper — **the one math under texture, placement, blocks, order, movement, and identity.**

The circle half's nearest existing kin: the System Map's sunburst (angle = leaf-count, uniform per
file — FINDINGS-LOG Slice 77-78) and the radial layouts — 2π/n partitions already drawn once, ad hoc.
Tim's equations replace the ad hoc with the law.

## §2 · Every division is an identity — tokens attach to addresses

"Each division of the fill/thing is a distinct identity/address, so can have colour tokens."

A fill stops being one colour. It is an **addressed grid where every cell resolves its own token**.
Connections:
- **The token system** (`styles.css` L0→L1→L2; `tokens/texture.css`'s hatch/blueprint patterns are
  today STATIC pattern fills): texture becomes *computed* — the pattern is generated from n + the
  equations, and each generated cell is a token attachment point. Token-at-address is the new joint
  between the token registry and the address algebra.
- **The ramp** (`--ramp-1..4`, minted Slice 1): an ordered token sequence — exactly what an ordered
  address run consumes (cell k of n → ramp position k/n). The ordinal axis stops naming stops and
  starts *resolving* them.
- **G8b data-binding** (`resolveBindings`, pure, verified 32/32): a binding resolves per-address → a
  glyphic whose fill cells are LIVE data (a portfolio glyphic: each cell a property, coloured by its
  status token; the read-out speaks the truth of each addressed cell). The binding engine needs no
  change — it gains a finer-grained target.
- **Zone washes** (`containers.css`: wash = f(zone-depth)): already property-from-address-depth.
  Same law, coarser grain. The fill grid is the same wash law inside the mark.

## §3 · Order falls out — sequence and the time coordinate

"It also has order, the equations give reading order for sequence and time coordinate."

The division math yields a canonical **reading order** over the cells — which means order/sequence/
time is DERIVED, never assigned. Connections:
- **The ordinal axis** (R4): stops being a hand-set field ("insertion order") and becomes the reading
  order the equations give — resolved relative to the telling's extent, exactly as A4 corrected.
- **cv-arc.js** (ported, verified 7/7, zero consumers — census/AREA-canvas-engines §C2): the arc
  resolver plans a telling's beats over a sequence. It is the *time-shaping* half waiting for the
  time coordinate this math provides. The wire between them is now designed, not just flagged.
- **The two-space split (Tim's same-day correction):** spacetime edges (contains↔contained-by,
  before↔after) vs semantic relations. The brainwave closes it: **the spacetime layer need not be
  STORED as edge records at all — it is DERIVABLE from the address math.** Containment = ancestry in
  the address; before/after = the reading order the equations give. Stored, declared vocabulary
  remains only for SEMANTIC relations (meaning-space fields). Spacetime is computed; semantics is
  authored. (This dissolves most of the "which edge types belong in the family" question: the family
  is the algebra's own relations.)

## §4 · Ratios all the way — nothing hardcoded, it just resolves

"With everything being ratios none of it is hardcoded and it just resolves."

The resolution-first law (registry rows + schemas that RESOLVE into the thing) applied to geometry.
Declare n (and the equation family); derive everything: the grid, the addresses, the order, the token
positions, the projection to pixels. The W2 placement failure ("an absolute rule on a relative
system" — pixel constants) was exactly a violation of this; the System Map's unit-mismatch bug
(FINDINGS-LOG :444 — importance units vs bytes collapsing a folder to 0.24px) is the measured proof
that mixing an absolute currency into a ratio system breaks it. One currency: ratios of the parent.

## §5 · Purpose = names attached to addresses

"Comparisons, views, orders — whatever purpose the surface needs to serve, it's just names attached
to addresses, addresses come with their ancestry so always works."

A view/comparison/order is not a new structure — it is a NAMING over the existing address space. The
ancestry in every address is what makes any naming resolvable without extra wiring. Connections:
- **The System Map's lenses** (SIZERS/COLORERS registries, Slice 69): already names-over-addresses —
  a lens re-colours/re-sizes without moving zones ("zones must not move"). The brainwave generalises
  the lens registry to every surface.
- **The language:** an addressed cell is a NOUN ("addresses are the nouns, edges the verbs" —
  LANGUAGE.md, Tim's dated record). A named view is therefore SPEAKABLE: "the twelve parts of this
  system, three featured, read in order" is a read-out over fill addresses. The read-out grammar
  (readGraph/referent) gains a finer subject without a new mechanism.
- **AXES.md's capstone** ("the containment tree is the spine of every axis") — this is that sentence
  made operational: every axis (colour, order, comparison, view) hangs names on the one spine.

## §6 · Movement holds different axes — variable frame-content coordinates

"Sliding off screen, vs two moving and splitting, reforming into something else — these are
additional axes that give variable frame-content coordinates."

If everything drawn sits on computed grids (squares → blocks → pixels), then movement decomposes into
INDEPENDENT AXES rather than one "animate x,y":
- **frame axis** — the viewport/camera moves over stationary content (slide off screen; the room
  symbol's own gloss: "the camera slides between them"; the operator-surface window work is this axis
  at product scale).
- **content axes** — an address re-partitions: one cell becomes two (split), two merge, a set
  re-forms into a different structure (reform). These are ADDRESS DIFFS, not pixel tweens.
- The discipline is already proven in the corpus: geometry authoritative + instant, animation is a
  FLIP decoration that must never affect correctness (Slice 70); the growth animator (stable keys +
  token transitions) — movement = choreography over the address diff, bounded by the changed
  boundary (LCA), angled, animated. R3's design (census/AREA-canvas-engines §E) is this brainwave's
  first consumer; the brainwave extends it with the split/merge/reform verbs and the separable frame
  coordinate.

## §7 · Identity = addressability

"So identity, it's just if there's an address for it or not."

The existence test for ANY thing in the system: does it have an address. This is the frame law
(node≡frame≡type≡registry≡coordinate) said in one clause, and it is the deep join to the Company's
one-resolver spine (`resolve_address` — everything reachable dispatches). G6.1 (a glyphgraph node's
`address` resolving to a real Company thing) stops being a nice-to-have field: **it is the identity
mechanism itself.**

## §8 · Groups are addresses too — any selection, one operation

"Any blocks can be considered and operated as one, just by being a registered identity… Any group,
any filter, any selection, one operation… the cascades and certainty of common ancestor make it
automatic, given every node/thing is an address containing its lineage."

A group/filter/selection becomes operable-as-one by REGISTERING AN IDENTITY (an address) for it.
Then every axis (colour, state, motion, meaning) applies to it exactly as to an atom — and cascade
conflicts resolve automatically because lineage is IN the address: the LCA gives certainty about
which boundary a cascade owns. Connections:
- **CV_GLYPHGRAPH_SESSION** (the live selection substrate the generator + the collaborative AI
  share): a selection is today transient state; under this law a selection can be MINTED as an
  addressed identity → one operation, speakable, persistable, sharable with the AI as a noun.
- **cv-address.lca/lcaAll**: already implemented and stated in its own header as "the boundary that
  must HOLD through a change — derived, never chosen." The cascade certainty is a one-call primitive.
- **The registry**: "a registered identity in the system" = a registry row — identity-by-registration
  is how every other citizen already works (types, tokens, capabilities). Groups join the same door.

## §9 · The self-similarity (the part the parts add up to)

The glyphic contains a fill; the fill contains an addressed grid; each cell is an identity that can
carry tokens, order, data, meaning — i.e. **each cell is a small glyphic-shaped thing, and the canvas
is a large fill.** The same partition law runs at every scale: canvas → nodes (R3's frames),
block-surface → zones (ContainmentTree), mark → fill cells (the texture layer), and — per the block
symbol's own gloss — "every boundary the root of its own cascade." One math; the scales are just
frames. This is why the placement rebuild, the texture layer, the block system (upstream, R5), the
ordinal axis, and group-operations are ONE build in different clothes.

## §10 · The socket for Tim's equations (what arrives from his math session)

Reserved, explicitly not derived here (his session owns it): the circle equations (2π/n family and
what he's built beyond it) · the reading-order function over mixed square/circle divisions · any
proportional-line families beyond uniform n (golden/harmonic splits?) · rotation as a parameter of
the division (not a post-transform?). The structure above consumes whatever form they arrive in,
because everything downstream needs only: (a) a partition function → addresses, (b) an order
function → the time coordinate. Those are the two plugs.

## §11 · What this changes in the build (fed into the plan files)

- **R3 (placement)** = the FIRST CONSUMER of the one math (already designed on cv-address spans;
  Tim's answer: ALL layouts together, one pass — they are all readings of the same algebra).
- **A NEW TRACK — the addressed fill / texture layer**: CV_SHAPES.markSVG gains a computed-texture
  path (partition the fill → addressed cells → per-cell tokens/bindings/order) replacing static
  pattern fills; the language read-out gains fill-level nouns. Waits only on the equations' arrival
  for the circle half; the square half (cv-address) is ready now.
- **The spacetime/semantic split lands as DERIVED vs DECLARED**: containment + order computed from
  addresses; semantic relations stay authored meaning fields. (Reframes R1b's remaining edge-family
  question.)
- **Groups-as-identities**: mint-an-address-for-a-selection joins the registry; LCA cascade
  certainty; the collaborative AI receives selections as nouns.
- **G6.1 rises in priority**: address = identity = the existence mechanism (not just convergence).
- **The Supabase backend** (with the symbol-record expansion from Tim's same-day answer): addresses,
  identities, groups, symbol multi-field records — one persistence substrate for the address space.


---

# THE WAVE (2026-07-09) — nine areas grounded it; the idea comes back BIGGER and corrected
> Evidence: wave-one-math/AREA-*.md (9 reports: design-machinery · canvases-app · tokens-axes ·
> templates-kits · system-remainder · counterpart · company-spine · math-priors · rigor/skeptic).
> Read whole, together. What follows is the anchor CORRECTED — the sharpened design supersedes the
> corresponding §1-§11 claims where they conflict.

## §12 · The kernel is FIVE primitives, not two (math-priors §B — every formula in the code catalogued)
1. **partition(parent, weights)** — WEIGHTED from day one (uniform = the special case). Proven need:
   the System Map's childValues discovered "the lens changes the ratio, never the currency" under real
   pressure; Tim himself rejected uniform 2π/n on the sunburst (Slice 78). Tim's equations must accept
   a weight argument, or they reproduce that failure on first contact with real content.
2. **project(children, extent, mode: linear|angular, gap?)** — one law dissolving the THREE (four with
   counterpart's organisms) independent hand-written 2π/n sites. Squarify/treemap is EXPLICITLY NOT a
   mode — 2D area-packing is a different algorithm class, a registered sibling (never force-fit).
3. **grow(...)** — the growth contract, DECIDED not inherited: cv-address's own header asserts derived-
   never-stored AND frozen-at-insertion four lines apart (rigor A2). Resolution: freeze the INPUTS of a
   derivation ({index, capacity}), never its OUTPUT; better, retire slotFor per R3's design.
4. **order(items, roles) → beats WITH an explicit t** — today no time COORDINATE exists anywhere
   (cv-arc emits array order only). Also: ONE declared fencepost law (ring divides by n, pipeline by
   n-1, spans into n cells — three conventions, currently mixed silently).
5. **fit(frame, content) → scale** — slide-fit's ratio, promoted to a named primitive (open: partition
   in reverse?).

## §13 · The corrections the skeptic proved (each survives-by-redesign, not by wishing)
- **IDENTITY IS A MINTED ID THAT RESOLVES TO AN ADDRESS — the raw address is never the stored key.**
  Derived addresses CHANGE on sibling insert (k of n → k of n+1); what's stable is the ancestry ABOVE
  the mutated frame. Persisted things (rows, bindings, group members) key on minted ids and re-resolve.
  This is exactly how the Company's resolver already treats every citizen — id first, position second.
- **Group operations are TWO kinds, not one:** attribute ops (colour/state/token) = a plain map over
  member ids, no LCA involved; structural ops (move/reform-as-one) REQUIRE minting a frame — the LCA of
  a non-contiguous selection degenerates to the whole parent (proven by running lcaAll: cells 2,5,9 of
  12 → root). Minting is the mechanism, not decoration.
- **Split/merge/reform needs a THIRD animation primitive** ("spawn-from") beside glide and enter —
  React keys are 1:1; one-becomes-two has no tween today. New machinery, scoped explicitly.
- **Fill-level read-out speaks through MEANING FIELDS, never raw k-of-n** — "cell 7 of 12" is the
  octagon-oracle failure one layer down. cv-arc's role-named beats are the working precedent.
- **Ratios claim, bounded honestly:** positions/counts/order are pure ratios; per-unit visual
  MAGNITUDES (the 2.1% wash step, a gap inset) remain authored tokens — a constant may buy breathing
  room BETWEEN ratio-derived cells, never move which ratio produced the boundary.

## §14 · The relation split is THREE buckets, not two (company-spine §B2)
DERIVED (containment + pure sequence — from the address math) · AUTHORED PROVENANCE (who/what made
this — created/authored-by/sourced-from: facts no address encodes) · SEMANTIC (declared meaning
fields). The Company already ENFORCES bucket 1 as law (edge_kinds/AGENTS.md: "containment is derived,
never stored" — 319 stored belongs_to rows DROPPED on landing) and holds the groups precedent
(mind:// kind=composition: members + typed order edges behind ONE resolvable address — generalize it
scheme-neutral, don't rebuild it).

## §15 · Recovered canon that outranks the anchor (counterpart — Tim-ratified, import wholesale)
- **motion.json's law-set** (anchor_is_the_lca · transition_is_the_diff · change_budget ·
  boundary_carries_identity · arrival_relative_to_path · anticipatory_verb · spatial_persistence ·
  expert_lane) — the movement axes, already Tim's law, more precise than §6.
- **TWO CIRCLES, not one:** the SHARP mechanical circle (2π/n, address-generating) vs the SOFT semantic
  circle (subject sectors needing an authored CUT before addresses exist). The equations socket (§10)
  must say which it feeds. Some things are irreducibly authored — "everything resolves" is bounded.
- **CASCADE vs COMPOSE** (RESOLUTION.md): containment nests (nearest-scope wins); other axes COMPOSE
  (multiply, none wins) — two resolution mechanisms the build must not conflate. And the litmus law:
  **"derive, never place — a value a person had to type for a specific case is a defect."**

## §16 · Where the laws already operate (the anchor's claims, found running)
project:// address DB-GENERATED from the key (identity=addressability in SQL) · containment-derived
law enforced Company-side · navgraph's tree-is-spine/edges-are-web (tested) · the RG1→RG9 chain =
minting identities over selections, end-to-end with Tim's consent gate (the §8 pipeline, built for
ui://) · childValues weighted partition · wash=f(depth) · X11's structural+semantic sibling edges
(degrade-honestly) · slide transitions + Workshop scale-fit = the frame axis live.

## §17 · The disconnection harvest (headline items; full lists in the nine reports' §C/§E)
glyph:// UNREGISTERED on the one resolver (hundreds of real glyph://symbol/* addresses invisible to
resolve_address — small additive join, scoped) · relation_types/ fully built, ZERO consumers, dangling
inverse ("follows") · glyph_assist accepts ANY caller-supplied edge kind (ungoverned third vocabulary
path) · canvas identity = 7 hand-maintained lists, no registry row, Cmd+K provably stale · AIEngine's
whole diff/undo system addresses by ARRAY INDEX (live correctness risk; swapping coordinates for
address paths = the cleanest single migration found) · order = array position EVERYWHERE (ids that
freeze creation-position into strings) · texture-axis promises 8 patterns, CSS implements 2, in
absolute px · ordinal-axis points at the wrong tokens (not --ramp-*) · code-symbols vs code-edges
94 vs 4908 (a documented half-done migration) · element-map stale by 22 addresses; a README claims 25
of 505 · three field-synonyms for one concept (represents/roles/maps_to_feature) · build-system-map
declares verb-pairs, emits only forward halves · fixed shape-tables STILL LIVE in 3 more places (one
TEACHING the octagon table to the AI in a prompt) · 4 unreachable stub canvases with false copy ·
undo computes the invertible diff then throws it away · AtomiCity's divergent boot + icon monkey-patch
· counterpart's OWN two address systems (file-substrate live vs span-spec prose) — same primitive at
two resolutions, unrecognized.

## §18 · Supabase reality (corrects §11's assumption)
NO address/identity backend exists yet anywhere. counterpart/supabase = only a CLI link to project
`gctunhsuwpaxeatwlmuv` ("Concept-Vi's Project" — CONFIRM with Tim whether this is the main Vi backend;
target it if so, never mint a parallel project). The Counterpart-handoff schema (kind/artifact/
variable_binding/memory/preference + pgvector, resolution precedence explicit>preference>memory>ai>
default) is the closest studied precedent for the persistence layer — a pattern to learn from, not a
thing to consume.
