# AREA — RIGOR / SKEPTIC (the make-or-break read on BRAINWAVE-ONE-MATH.md)

> Read in full: BRAINWAVE-ONE-MATH.md · feedback-glyphic-course-corrections.md · census/AREA-canvas-engines.md
> (§C1/§C2/§E) · core/cv-address.js, cv-arc.js (full, 92+54 lines) · tokens/texture.css ·
> system/system-map.html (SIZERS/COLORERS/childValues/squarify, :396-486) · analysis/LANGUAGE.md ·
> READING-LEDGER.md (the octagon-oracle finding) · system/glyphgraph-generator.html (selection/session) ·
> DiagramSolver.jsx (growth animator, :365-401) · analysis/FINDINGS-LOG.md Slices 77-78 · GUIDE.md
> ("THE CORRECTED LAWS"). Evidence marked Observed (file:line) / Inferred / Verified per the standing rule.
> Standing posture: default-to-wrong, but every attack below is checked against the actual code before
> being kept — three of eight surfaces the wave listed did NOT land as stated; that's recorded honestly.

---

## §A · ATTACKS THAT LAND

### A1 · Uniformity — not hypothetical, ALREADY MEASURED AND FAILED in this corpus
**The break:** x/n and 2π/n give equal divisions. Real content is unequal. This is not a prediction —
it already happened and is logged as a fixed bug.

**Evidence (Observed, FINDINGS-LOG.md:207-222, Slice 78):** the System Map's first sunburst gave "every
file... an equal thin arc (angle = importance ≈ uniform), so size was invisible and folders blurred."
The fix explicitly replaced uniform 2π/n with a **weighted** angular share: "angular share = childValues
(same weight rule as every layout)" (FINDINGS-LOG.md:235). `childValues()` (system-map.html:434-442) is
a real, running weighted-partition function: each child's span = `budget * (metricLeaf(f) / msum)` — a
budget divided by a **metric**, not by count. The squarified treemap (`squarify`, :458-476) consumes
these weighted values directly; area, not count, drives the split.

**Verdict: LANDS, hard.** The brainwave's own citation of the System Map's sunburst as "the circle
half's nearest existing kin" (BRAINWAVE §1) is the same sunburst whose uniform-angle FIRST VERSION was
rejected by Tim for exactly the failure this attack predicts. The one-math as stated (x/n, 2π/n) is the
REJECTED first draft of the System Map's own history, not its resolved state. `cv-address.span(k,n,parent)`
(cv-address.js:25-30) is uniform-only — it takes no weight argument. `cv-shapes.js:33`'s existing
`i*2*Math.PI/n` ring-icon placement is likewise uniform-only (verified by reading the function: no
weight/metric parameter exists anywhere in its signature).

**What design change survives it:** `span(k, n, parent)` must become `span(k, weights, parent)` where
`weights` is a per-child metric array (defaulting to `[1,1,...,1]` for the uniform case, which still
correctly generalizes today's callers) — i.e. `childValues`'s budget-split IS the general form and
uniform is the trivial special case, not the other way round. This is a small, backward-compatible
change to the algebra's signature, not a new mechanism — but it must ship in the FIRST version, not be
retrofitted after the "it just resolves" claim is made to Tim's eye, because the System Map proves the
gap is visible immediately (files/folders/nodes of different sizes are the NORMAL case, not an edge case).

### A2 · Address stability vs derivation — the file that's supposed to BE the law contradicts itself
**The break:** "an address is derived, never stored" (identity rides the address) vs "inserting a
sibling changes every sibling's identity" — tested against the actual algebra, not a hypothetical.

**Evidence (Observed, cv-address.js — the SAME file, two adjacent comment blocks):**
- Header line 5-7 states the relative law: *"addresses are DERIVED from counts, never assigned (insert
  a sibling and every address re-derives — an address is a view, never a stored fact that can stale)."*
- Header line 15-17, four lines later, states the OPPOSITE: *"a node's slot = its span in its frame,
  FROZEN at insertion (stable-slot); a drag writes an authored override; growth never re-ranks placed
  nodes."*
- `slotFor(index, capacity)` (cv-address.js:83-88) implements the SECOND law: it returns a frozen
  `span(index+1, cap)` where `cap` only ever doubles, and existing indices' spans by construction never
  change when `cap` grows — but the value depends on `capacity`'s **history** (how many doublings have
  happened), not on the CURRENT total count. Two graphs with identical final structure but different
  insertion/deletion histories get DIFFERENT frozen spans for the same logical position — directly
  violating the "derived-never-stored... two layouts of the same structure from scratch are identical"
  law the census's own rewritten test-suite proposes to assert (census/AREA-canvas-engines.md:398-400,
  §E point 5).

Census/AREA-canvas-engines.md already caught this independently and named it precisely: "the law split
inside this one file... span/encode/decode/lca/zones = the relative algebra A3 needs; slotFor = the
freeze primitive of the era A3 overturns" (§B(d) and §C1, canvas-engines.md:139-144). The brainwave
(§7-8) builds "identity = addressability" and "groups = registered addresses" directly ON TOP of this
file without resolving which half of it is the law.

**So: does inserting a sibling change every sibling's identity?** Tested against BOTH halves:
- Under the RELATIVE half (`span`/`encode`/`decode`): YES, unconditionally. Child k of n becomes child
  k of n+1 → its `start`/`width` (its address) changes for every sibling to the right of the insertion
  point. If identity IS the address (brainwave §7, verbatim), then EVERY node whose numeric position
  shifted has a NEW identity after every insert. This breaks any persisted reference (a Supabase row
  keyed by address, a binding, a named group member) unless the persisted key is NOT the raw address.
- Under the FROZEN half (`slotFor`): NO — that's precisely why it was built (stable references across
  growth). But it can't be reconciled with "derived, never stored" — it IS a stored fact (the frozen
  span), by the file's own words.

**What's actually stable (tested, not assumed):** the brainwave's answer ("addresses come with their
ancestry so always works" — BRAINWAVE §0/§5) is a real mechanism but it does NOT resolve this: ancestry
(the PATH prefix, e.g. "row 2's third member") is stable ONLY if the counts along that path don't
change either. A sibling insert changes the LEAF's `k` (unstable) but leaves the PARENT path unchanged
(stable) — so what's actually invariant across a same-level insert is the **lineage above the mutated
frame**, never the mutated frame's own members' addresses. This is a real, useful, narrower claim than
"the address IS identity" — it is "the ANCESTRY above the LCA is identity; the address BELOW the LCA is
a resolved position, re-derived every time, and must NOT be used as a storage key."

**What design change would survive it:** identity must be a REGISTERED id (a UUID/registry row per §8's
own "a registered identity in the system") that RESOLVES TO a current address via a lookup, never the
address serving as the id directly. This is not a new idea — it's exactly how the Company's own
`resolve_address` spine already treats every other citizen (types, tokens, capabilities are IDs first,
addresses/positions second — BRAINWAVE §7 says "the deep join to the Company's one-resolver spine" but
doesn't notice that spine's resolver pattern is precisely "id → resolves-to-current-state", the inverse
of "address IS identity"). Concretely: a fill-cell's Supabase row is keyed by a minted id; the id's
CURRENT address is looked up by re-running `decode`/`span` against the live structure at read time. The
brainwave's "addresses come with their ancestry so always works" (§0) becomes true ONLY once ancestry is
resolved through a stable id, not through the raw numeric path.

### A3 · Groups over non-contiguous selections — the LCA over-applies, proven by running the function
**The break:** does "any filter, any selection, one operation" via LCA-certainty hold for a
non-contiguous pick? Tested against `lca`/`lcaAll` directly (cv-address.js:56-69), not assumed.

**Evidence (Observed, traced by hand through the actual algorithm):** `lca(pathA, pathB)` walks the two
paths comparing `[k,n]` pairs position-by-position and stops at the FIRST disagreement. For a filter
selecting cells 2, 5, and 9 of a 12-cell row, each cell's path is `[[2,12]]`, `[[5,12]]`, `[[9,12]]` —
single-level paths under the same parent. `lca([[2,12]], [[5,12]])`: compares `[2,12]` vs `[5,12]` at
index 0 → `2 !== 5` → breaks immediately → returns `[]` (empty path = the ROOT). `lcaAll` folds this
over all three → still `[]`. **The LCA of a non-contiguous same-level selection is the frame that
contains ALL 12 cells, including the 9 non-selected ones** — exactly the over-application the wave
prompt predicted, and it is not an edge case: it is the GENERIC case for any filter/comparison view that
isn't a contiguous run (which is most of what "comparisons, views, orders" (BRAINWAVE §5) actually mean
— e.g. "all cells in error state" is almost never a contiguous range).

**What this means concretely:** "the boundary that must HOLD through a change" (cv-address.js's own
description of LCA) is a real and correct answer to "what is the SAFE re-partition boundary if these
members' positions change" — but it is a DIFFERENT question from "what is the target of a group
operation." Painting cells 2/5/9 gold needs no LCA at all (it's a trivial map over three explicit ids —
the LCA is irrelevant and misleadingly implies a scope larger than the operation touches). MOVING
2/5/9 together as one block needs MORE than the LCA gives: the LCA only tells you re-partitioning is
safe up to the root, not how to carve a new sub-frame for the group. The brainwave's own §8 already
supplies the actual fix ("a selection can be MINTED as an addressed identity") — but its prose frames
minting as a NICE-TO-HAVE ("can be… ") sitting alongside "the cascades and certainty of common ancestor
make it automatic," when the evidence says minting is NOT optional decoration on top of automatic LCA
certainty — it is the ONLY mechanism that makes non-contiguous group operations coherent at all. The
LCA is necessary (for safety) but not sufficient (for scope); §8 conflates the two.

**What design change survives it:** every group/filter/selection operation must go through TWO steps,
not one — (1) mint a group address (a new frame that is NOT a subset of the existing partition, since
non-contiguous members can't share a native sub-frame) with its own registry row, THEN (2) any
structural (move/reform) operation on the group re-partitions relative to the MINTED frame, while any
attribute operation (colour/token) is a plain map over the group's member ids and never touches LCA at
all. Two different operations, not one — the brainwave's "one operation" framing (§8) needs to name
which of the two it means per case.

### A4 · Split/merge/reform — no existing machinery can tween one key into two
**The break:** is there existing animation machinery that can express a SPLIT (one key becoming two)?
Tested directly against the one animator the corpus has.

**Evidence (Observed, DiagramSolver.jsx:365-382):** the "growth animator" the brainwave cites as the
"discipline... already proven in the corpus" for movement (§6, "the growth animator (stable keys +
token transitions)") is, concretely: `h("div", { key: nd.id, ... })` — ONE React key per ONE graph node,
with CSS `transition` on `left`/`top` (DiagramSolver.jsx:486, `transition: "left var(--dur-move,280ms)..."`).
The comment at :375-378 states its own scope precisely: "React keys keep placed nodes' elements alive,
so a style change GLIDES, and a new key ENTERS." That is the WHOLE vocabulary: (a) same key, new
position → glide; (b) new key, no prior element → enter (fade/pop in, presumably via `tokens/diagram.css`
transitions not read here but implied). There is NO third case for "key A's element becomes keys B and C
simultaneously" — React's reconciliation is fundamentally 1:1 per key; a split is TWO new keys entering
while the old key's element is removed, which under this machinery renders as "one thing vanishes, two
unrelated things appear" — the exact opposite of "reforming," with no tween connecting them.

**Verdict: LANDS.** This is not a performance question or a taste question — it's a structural gap in
the reconciliation model being relied on. BRAINWAVE §6's "two moving and splitting, reforming into
something else" is asserted as an axis the frame/content decomposition merely EXPOSES, but exposing the
axis (having an address diff that says "1 became 2") does not supply the RENDERING that makes it read as
continuous motion — that is a distinct, unbuilt animation primitive (a FLIP-style shared-element
transition where one outgoing element's bounding box is the shared start-state for two incoming
elements' start states, cross-faded/morphed). No trace of this exists in the codebase (verified by
reading the whole growth-animator block and the corpus's other keyed-list renderers found in this
census — ContainmentTree's motion/entrance wave (census:94, "motion/entrance wave 59-65") is also
single-node entrance, not many-from-one).

**What design change would survive it:** treat split/merge as its own registered animation PRIMITIVE
(a third case beside glide/enter — call it "spawn-from"), keyed not by node id but by a PARENT id that
both new keys reference during the transition (`data-spawn-from="oldId"`), so CSS/JS can position the
new elements' initial frame at the old element's last known rect and animate outward — genuinely new
machinery, not a byproduct of the address algebra existing. This should be scoped and estimated
explicitly before R3/the fill-track claims split/merge as "already covered."

### A5 · The fill-address read-out risks recreating the EXACT violation Tim banned
**The break:** can the language speak fill-level addresses without becoming the "octagon oracle"
Tim explicitly killed? Tested against the actual violation record, not a hypothetical.

**Evidence (Observed, READING-LEDGER.md:135-148, quoting cv-meaning.js:663-691):** the read-out
engine ALREADY committed this exact mistake once — `REFERENT_KIND = {octagon:'gateway', hex:'system',
...}` was a "MODULE-PRIVATE CONST — hardcoded, unreachable by the author API," which is precisely what
Tim's course-correction #2 calls a "fixed shape-table... AI invention, not canon" (feedback-glyphic-
course-corrections.md:19-21, "the octagon decision was a false decision"). The fix on record is: "the
form FIELDS are in the profile; the referent WORDS are not... the conforming fix... the form fields
carry their referent-words as FIELD DATA... referent() reads them from the active profile" (READING-
LEDGER.md:144-147).

**Applying the same test to the wave prompt's own example** — "cell 7 of 12, featured" — this is a
RAW-ORDINAL RECITATION (index + count), structurally identical in KIND to a fixed lookup table: it
names the coordinate instead of resolving it to a feeling/sense. It is not yet even at the octagon-
oracle's level (which at least resolved to a WORD, 'gateway') — "cell 7 of 12" resolves to nothing;
it's the address printed as English, exactly the "facet-recitation... the octagon oracle... the BROKEN
test" READING-LEDGER.md:81 names as the failure mode to avoid, applied one layer down (facet → fill
position). **This attack LANDS against the naive reading of the brainwave, and the wave prompt's own
example phrase is itself the failure case**, not a working example.

**What survives it, and how:** cv-arc.js already has the right shape for this — `plan()` assigns each
beat a ROLE (open/argue/show/prove, from `narrative_roles`, cv-arc.js:36-38) and the role, not the
raw index, is what the read-out should speak ("the third beat, in the ARGUE role" reads as "arguing its
case," never "beat 3 of 7"). The same move applies to fill-cells: a cell's read-out must resolve through
a FIELD (ordinal-position → phrase, e.g. `first/among/last`, or role-relative like `featured/supporting`)
via `CV_MEANING.field`, never print `k`/`n` directly. This is buildable (the machinery — fields,
combinatorial resolution — already exists per LANGUAGE.md) but it is a REQUIREMENT, not a given: the
fill-track (BRAINWAVE §11, "the language read-out gains fill-level nouns") must be built against
`CV_MEANING.field`, and any implementation that lets `k`/`n` reach a sentence unresolved should be
treated as a REGRESSION into the exact violation the ledger already fixed once.

---

## §B · ATTACKS THAT FAIL (checked hard — the idea's genuine strengths)

### B1 · "The circle half and square half can't compose in one glyphic" — FAILS at the address-algebra level
Tested directly: `encode(path)` (cv-address.js:33-38) and `decode(start, radices)` (:41-52) operate on
an abstract `[[k,n],...]` PATH — they never reference pixels, angles, or any specific coordinate system.
A path like `[[3,12],[2,5]]` ("sector 3 of 12, then cell 2 of 5 within it") is perfectly well-formed
whether level 1 projects to an ANGLE and level 2 projects to a SQUARE GRID, or the reverse, or both
levels are the same geometry. **The mixed-radix address is coordinate-system-agnostic by construction**
— nothing in the algebra assumes linear vs angular. This is a genuine strength: the "one math" claim
survives the mixed-geometry test at the ADDRESS layer.

**What does NOT survive (the honest remainder, for §D):** the PROJECTION layer — the function that
turns a path into actual pixel/angle coordinates per level — has no registered mechanism for "which
geometry family applies at which depth," and there is ZERO evidence anywhere in the corpus of a ring
nested inside a square cell or a square grid nested inside an angular sector (verified: no such
composition exists in cv-shapes.js, DiagramSolver.jsx, or system-map.html's sunburst — the sunburst
mixes rings-by-depth with SPOKES, which is two radial encodings, not a square+circle nesting). So: the
MATH composes (attack fails); the RENDERING REGISTRY for mixed geometries is undesigned (a real, open
requirement, not a break in the one-math claim itself).

### B2 · "Order/sequence/time falling out of the address math is unfounded" — FAILS, cv-arc.js is real and runs
Checked whether "the equations give reading order" is wishful: `cv-arc.js`'s `plan()` is a working,
deterministic, previously-verified-7/7 function (census/AREA-canvas-engines.md:146-153) that already
turns a beat count into an ordered sequence with role/archetype/dial assignment. It is idle (zero
production consumers, verified by grep — canvas-engines.md:273-276) but it is NOT vaporware; the
ordering mechanism the brainwave depends on for §3 already exists and already passed its proof harness.
The attack that "order is asserted, not demonstrated" fails — it's demonstrated, just unwired.

### B3 · "Zone washes as ratio-precedent is fake, it's actually hardcoded" — PARTIALLY fails, worth a nuance
Checked containers.css's zone wash, cited by the brainwave (§2) as "already property-from-address-depth.
Same law, coarser grain": `--zone-depth · 2.1%` (census:166-167, containers.css:77-92 per that census
entry). The DEPTH itself (which level of nesting a zone sits at) IS address-derived — that part of the
citation is correct, the attack fails there. But the multiplier, `2.1%`, is a literal hand-tuned
constant, not derived from any count or ratio — so "everything is ratios, none of it hardcoded" (BRAINWAVE
§4, verbatim) overclaims when applied to THIS example specifically: the address gives the EXPONENT
(depth), but the visual STEP SIZE per unit of depth is still an authored magnitude, exactly the kind of
number the resolution-first law would otherwise flag as hardcoding. This is a survivable, minor
correction (perceptual step-sizes are legitimately tunable constants — a text sizing scale or a colour
ramp needs SOME base unit) but the brainwave's rhetoric should say "positions/counts/order are pure
ratios; per-unit visual magnitudes remain authored tokens" rather than claiming totality.

---

## §C · THE SHARPENED DESIGN (the anchor, corrected)

1. **Partition is `span(k, weights, parent)`, not `span(k, n, parent)`.** Uniform is `weights =
   Array(n).fill(1)`; weighted (content-proportional, matching `childValues`) is the general case. Ship
   weighted from day one — the System Map's own history (Slice 78) proves uniform is the version that
   gets rejected on first sight of real content.
2. **Identity is a minted id that RESOLVES to a current address; the address is never itself the stored
   key.** Ancestry (the path prefix ABOVE the last structural change) is what's actually stable across
   inserts — not the leaf address itself. Persisted references (Supabase rows, bindings, named groups)
   key on the id and re-resolve the path on every read.
3. **Group operations split into two kinds, not one:** attribute ops (colour/token/state) are a plain
   map over explicit member ids — no LCA involved, no boundary implied. Structural ops (move/reform as
   one block) require MINTING a new frame for the group (§8's own mechanism) — the LCA over a
   non-contiguous selection is not that frame; it degenerates to the root and over-scopes.
4. **Split/merge/reform needs a THIRD animation primitive** beyond glide (same key, new position) and
   enter (new key, no predecessor): a spawn-from/collapse-into transition keyed by parent-id references,
   genuinely new machinery to design and build, not a free consequence of having an address diff.
5. **Fill-level read-out speaks through fields (ordinal role, relative position-phrase), never raw
   k-of-n.** The wave prompt's own example phrasing ("cell 7 of 12, featured") is the failure case to
   avoid, not a target to hit — cv-arc's role-based beat naming is the working precedent to extend.
6. **The address algebra composes across geometries (proven); the projection registry that would decide
   "ring vs grid at this depth" does not exist yet (open, must be designed, not assumed free).**
7. **`slotFor`'s frozen/history-dependent allocation must be retired or clearly quarantined** as a
   DIFFERENT, incompatible law from the rest of cv-address — the file cannot keep asserting both without
   naming which callers get which (census/AREA-canvas-engines.md's F1 proposal already says this; this
   wave independently re-derives the same conclusion from the identity-stability angle, which strengthens
   it).

---

## §D · WHAT MUST BE TRUE OF TIM'S EQUATIONS (requirements for the math-session output)

For the one-math to survive the attacks above, the equations arriving from Tim's separate session must:

1. **Accept a weight/metric argument, not just a count `n`.** A partition function that only takes `n`
   reproduces the Slice-78 failure the moment real (unequal) content meets it. This applies to BOTH the
   square family (x/n → weighted-x) and the circle family (2π/n → weighted-2π) symmetrically — if the
   circle equations Tim built separately are uniform-only (2π/n as stated verbatim in the brainwave §0),
   they inherit the same defect the square half already showed in production, and need the same fix
   before they're treated as "already given" (BRAINWAVE §1 currently treats the circle equations as
   complete/reserved — §10 — without this check).
2. **Be legible as a PATH, not just a final coordinate** — i.e. expose the intermediate `(k,n)` (or
   `(k,weights)`) at every level, not just the resolved angle/position, so `lca`/ancestry/mixed-radix
   decode can operate on them. If the equations only emit a final θ or x, the identity/ancestry/LCA
   machinery in §A2/§A3 has nothing to attach to.
3. **Declare, per level, which geometry family it belongs to** (linear-span vs angular-span vs some
   future family) as DATA the projection layer reads — not baked into the numeric output — so the
   composition gap in §B1 can be closed by a registry rather than a special-cased renderer per
   combination.
4. **Supply (or explicitly decline to supply) a rotation-as-parameter-of-division vs rotation-as-post-
   transform answer** (BRAINWAVE §10 already flags this as reserved) — this determines whether a
   rotated division is the SAME address re-projected or a DIFFERENT address, which matters for A2's
   identity-stability question (a rotating fill must not silently be read as "every cell got a new
   identity" each frame).
5. **Be tested against a NON-uniform, NON-contiguous worked example before the socket closes** — e.g.
   "12 cells, sizes [3,1,4,1,5,9,2,6,...], select {2,5,9}, then insert one more, then rotate 15°" — run
   through span/encode/decode/lca by hand or in the verifier, not asserted resolved. Every attack in
   §A was found by doing exactly this against the EXISTING square-half code; the circle-half equations
   deserve the same falsify-first treatment before the socket (§10) is declared filled.

---

**Bottom line:** the algebra genuinely composes across geometries and already has a working (if unwired)
order-resolver — real strengths, not hand-waves. But three claims in the brainwave's own supporting
citations undercut it: the System Map's sunburst history proves uniform partition already failed in
production: children need a `weights` argument from day one; the address file's own header asserts two
incompatible identity laws (derived-never-stored vs frozen-at-insertion) and the brainwave inherits both
without picking one, which breaks "any persisted reference to an address" the moment a sibling is
inserted; and the LCA-certainty claim for groups mathematically degenerates to the whole parent frame for
any non-contiguous selection, so "one operation, automatic" is true for colour/token maps but false for
structural moves unless a group address is minted first — which §8 already proposes but frames as
optional rather than required.
