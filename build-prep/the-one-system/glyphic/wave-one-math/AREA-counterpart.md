# AREA: counterpart/design — origin of the address/sequence algebra

Territory: `/home/tim/repos/counterpart/design` (READ-ONLY — another live session's room; nothing
written there). All claims below are Observed (file:line/path) unless marked Inferred. Read in full:
`dna/*.json` (all 20 faces skimmed, 8 read in full — address, sequence, shapes, connectors, molecules,
motion, subject, reader), `engine/prove/resolve.mjs`, `engine/prove/resolve-sequence.mjs`,
`docs/RESOLUTION.md` (head), `dna/canon.json` (laws sector), `docs/LINEAGE.md` (head + structure),
`reference/.../db/schema.sql`, `supabase/.temp/*`. Sampled: `surface/runtime/organisms.js`,
`surface/runtime/{unit-view,archetype,wayfinder-view}.js`, `pieces/decision-card/` listing, repo
`CLAUDE.md`. Not fully read: the other 12 dna/*.json faces, `docs/BACKLOG.md` (63KB),
`docs/command/*` (10 files, largest 237KB), `pieces/` bodies (56 folders, sampled 1 listing only),
`surface/viewers/`, `server/`.

## §A · The account — this repo IS the origin the claude-ds address/sequence faces were ported from

This is not a guess — the shapes match almost verbatim. `dna/address.json` (v"address-2") states the
exact laws the anchor attributes to `core/cv-address.js`:
- `spans_not_points`: "child k of n owns [(k-1)/n, k/n)" — the anchor's `span(k,n,parent)`.
- `derived_not_assigned` + `origin_law`: addresses computed from counts, never assigned; first child
  of any unit starts at 0.
- `arithmetic.path_form`: **addresses may be written as paths (`deck/2of3/3of5`) OR as fractions
  (`7/15 @ depth 2`) — "with the radices known (3, then 5), 7/15 decodes back to (slide 2, zone 3)."**
  This IS ancestry-in-the-address / mixed-radix encode-decode, confirmed present in the origin design
  in prose (`dna/address.json:30`).
- `uses.lca`: "the LOWEST COMMON ANCESTOR of a set of addresses is the smallest scope containing them
  all" — present, matches the anchor's `lca`/`lcaAll` description exactly.
- **No rotation, no circle math anywhere in `address.json`.** The square/interval half only. Matches
  the brainwave's own framing that the circle half awaits Tim's separate-session equations.

`dna/sequence.json` (v"sequence-9", the most-iterated face in the folder) is far more developed than
the brainwave's §3 sketch: `reading_axes.measure` ("a root's story is a conserved whole… children
PARTITION it… fusion is conservation") is word-for-word the brainwave's §3 "order falls out" claim,
written a month earlier (2026-06-10/11 vs the brainwave's 2026-07-03). `reading_axes.walks` (any
forward path is legal, legalized by three story-tree invariants), `.fields` (warmth/ordinal/density as
readable direction, not just axes), and the `generation_ladder` (seed→root→roles→titles→frames→
slots→voice→tokens, explicitly named as "Intent→Proposal→Approval→Execution applied to design") are
all present, named, and evidence-classified (verified / predicted / corpus-confirmed) — this face is
MORE rigorous than the brainwave's treatment of order/sequence.

`dna/motion.json` (v"motion-5") is the strongest single find: it is **already the brainwave's §6
"movement holds different axes," ratified by Tim on 2026-06-11** — three weeks before the brainwave
doc existed:
- `anchors_and_changers.anchor_is_the_lca` (`motion.json:44`): "WHICH ring holds is not a design
  choice — it DERIVES: take all the changers' addresses; the LCA is the boundary that must hold."
- `transition_is_the_diff` (`motion.json:48`): "transitions are COMPUTED, never hand-authored: diff
  two views by address — unchanged = anchors, changed = changers, the transition ANIMATES THE DIFF."
- Plus `change_budget`, `boundary_carries_identity` (the ring law — interior change = state, boundary
  change = becoming), `arrival_relative_to_path`, `anticipatory_verb`, `spatial_persistence`,
  `expert_lane` — a complete, Tim-authored temporal law-set the brainwave's §6 re-derives independently
  and less precisely.

`dna/subject.json` (v"subject-3") is the circle/polygon face — but a DIFFERENT circle than the
brainwave's fill-texture circle. Tim's words recorded there: "the business is the top level… each
domain or face is one of the sectors around the origin, like it makes a polygon around it" — sectors
are RADIAL, SIMULTANEOUS, no inherent order, and the space is **soft-edged** ("subjective, continuous,
bounded BUT NOT WITH SHARP EDGES"). This is explicitly opposed to "artifact space (spans, counts,
addresses) has SHARP edges." Turning one into the other requires an AUTHORED act: **the CUT** (where
soft becomes sharp seams) and **the ROUTE** (the order sectors are visited) — "exactly what the
calculable half cannot derive… choosing where soft territory becomes sharp seams is judgment" (§20-21).

`dna/reader.json` (v"reader-3") supplies the demand-side half missing from the brainwave entirely:
`goodness_as_fit` ("'good' is not a property of an artifact — it is the FIT between the artifact's
coordinates and the occasion's demands") with a `brief_schema` {subject_region, reader, occasion,
purpose}, and `artifact_as_route` / `count_as_distance` (page-count is READER-DISTANCE ÷
change-budget-per-page, not a style choice).

`engine/prove/resolve.mjs` and `resolve-sequence.mjs` are real, runnable, self-proving resolvers —
but **resolve.mjs only implements the GRAMMAR face** (unit×ratio scale/radius/type/zone-proportion
derivation, proven against measured mockups) and **resolve-sequence.mjs only implements `plan(arc,n)`**
(deterministic page-plan generation from `sequence.json`, proof-verified against the source 16-slide
deck: 7/7 checks pass). **Neither implements `address.json`'s own span/LCA/encode/decode algebra.**
Grepped the whole repo (`engine/`, `surface/`, `factory/`) for `function lca|span|encode|decode` and
`lowestCommonAncestor` — zero hits anywhere. **`dna/address.json`'s formal algebra is 100% prose, never
coded, in this repo either** — confirming the anchor's "zero production consumers" finding about
`cv-address.js` is not a one-off: the gap exists independently in the very sibling it was allegedly
ported from.

**But the CIRCLE half (2π/n) is not merely designed — it is SHIPPED, here, inverting the expected
order.** `surface/runtime/organisms.js`'s `graph()` function (the `DNA.org.graph` instrument, backing
the file-substrate map) contains `folderDots()` (`organisms.js:283-309`): for a folder's children,
`cap = max(6, floor(2·π·r / arc))`, `step = 2·π / cap`, `ang = -π/2 + stagger + k·step` — each child
gets a dot at a computed angle, **coloured by its type token**, clockwise from the top, overflowing
into additional concentric rings (each ring offset from the one below) when the count exceeds one
ring's capacity. This is brainwave §1 ("circle divided 2π/n → angular sectors, each sector is an
address") AND §2 ("each division… can have colour tokens") **already built and running** — just
addressing the file-substrate, not slide/subject content. A second independent 2π/n implementation
sits in the same file for the transcript constellation (`organisms.js:838-849`, phyllotaxis/golden-
angle spread). Neither references `dna/address.json` or `dna/subject.json`'s sector-polygon law; both
hand-rolled the angle math fresh.

`dna/canon.json`'s `laws` sector explicitly names `"derivation"`: "No value typed in: every number
derives from unit×ratio×dials×role; every address derives from the counts" — refs BOTH
`dna/address.json` and `engine/prove/resolve.mjs` as if the latter implements the former. It does not
(see above) — **the canon's own cross-reference is aspirational, not verified.**

`docs/RESOLUTION.md` (Tim, 2026-06-14, explicitly marked as superseding an earlier wrong cut) is a
deeper resolution theory than anything the brainwave states: **DERIVE, NEVER PLACE** ("if a value has
to be intentionally written by someone for a specific case, the system failed to derive it — that is a
defect, not a feature" — sharper than resolution-first) and a **CASCADE vs COMPOSE** split: containment
nests (nearest-wins), but the OTHER axes (temporal + two more, "FOUR so far — Tim's stated bound")
**compose by multiplication, none "wins."** The doc's epistemic stance is explicitly binding: "nothing
in the repo is authoritative — including the grammar and these registries… identify the real thing by
work," and "'so far' is load-bearing — never state a set is closed unless Tim has stated the bound."

`docs/LINEAGE.md` (418KB, 1493 lines, "453 entries") is **not** an identity/relation ledger — correcting
the task's framing — it is a densely reconstituted turn-by-turn recovery of the pre-compaction session
that GENERATED `address.json`/`sequence.json`/`motion.json`/`subject.json` in the first place (method:
15 parallel agents read 15 chronological slices of the stripped transcript). It is the **genesis
reasoning** behind every face above: e.g. entry [26] is Tim's "it should widen… the language spans a
range" pivot that produced the dial system; [76-85] is the "depth of subtlety" correction that produced
tonal zoning. Extremely high-value as a "why" source for whoever formalizes the one-math socket.

## §B · Joins to the one-math (circle/2π, ancestry, Supabase)

1. **Ancestry**: CONFIRMED present in the origin design (`address.json`'s path/fraction dual notation,
   decodable given known radices). The brainwave's claim that cv-address's `encode/decode` carries
   ancestry is grounded — it traces to here.
2. **Rotation**: CONFIRMED ABSENT everywhere in this repo (`address.json`, `subject.json`, `grammar.json`
   not fully read but no rotation hits in any grep). Genuinely awaits Tim's separate math session, as
   brainwave §10 assumes.
3. **The circle is not one thing.** This repo has TWO circles that must not be conflated when Tim's
   equations arrive: (a) `subject.json`'s semantic polygon — sectors around a business/territory
   origin, SOFT-edged, requiring an authored CUT to become addressable; (b) `organisms.js`'s literal
   pixel-angle 2π/n partition — SHARP, mechanical, already shipped for the file-substrate. The
   brainwave's §1 fill-texture circle is closer to (b). The brainwave's §10 socket should ask which one
   (or both, related by cut-then-address) Tim's equations target.
4. **Motion is not a new axis to design — it's an existing one to ADOPT.** `motion.json`'s
   `anchor_is_the_lca` / `transition_is_the_diff` predate and outrank the brainwave's §6/§8 treatment;
   they are Tim-ratified law, not agent-derived-from-principle. The one-math build should import this
   face wholesale rather than re-deriving movement axes.
5. **Supabase — NEGATIVE FINDING, corrects the task's framing.** `supabase/` in this repo holds only
   `.temp/linked-project.json`: `{"ref":"gctunhsuwpaxeatwlmuv","name":"Concept-Vi's Project", …}` — a
   CLI link to a live Supabase project, no schema files at all. **No address/identity/symbol backend
   exists here.** A schema DOES exist at
   `reference/Counterpart-handoff/counterpart/project/db/schema.sql` (341 lines) — but it belongs to a
   completely different, unrelated prototype product bundled as read-only reference material:
   "Counterpart Studio," a Vi-led design/build studio app (see its own `CLAUDE.md`) with registries
   `MS_KINDS`/`MS_RESOLVE`/`MS_DECISIONS`/`MS_ARTIFACTS`/`MS_MEMORY`/`MS_PRODUCE`, mirrored 1:1 into
   Postgres tables `kind`/`artifact`/`variable_binding`/`memory`/`preference`/`design_value` with
   pgvector local embeddings and a resolution precedence
   `explicit > preference > memory > ai > default`. **This is a working pattern for "declarative
   type + instance that resolves variables," not an existing address/circle backend** — worth studying
   as a schema-design precedent for the one-math's eventual persistence layer (§11 of the brainwave),
   but it does not pre-empt that work. Flag up-fabric: is `gctunhsuwpaxeatwlmuv` ("Concept-Vi's
   Project") the SAME Supabase project backing Project Vi elsewhere? If so, any future address/identity
   schema should target it rather than mint a new project (unions-not-bridges).

## §C · Disconnected / unfinished

- `dna/address.json`'s span/LCA/encode-decode algebra: spec-only, zero code, in this repo AND its
  claude-ds descendant. Confirmed cross-repo gap, not local.
- **Two addressing systems in ONE repo, never joined, same word "address" for different math:** (1)
  the file-substrate addressing system (`registry/address-registry.json`, `engine/substrate/{scan,
  assemble,wayfinder,graph}.py`, fully live, documented in this repo's own root `CLAUDE.md` as "an
  addressed, typed, queryable substrate") vs (2) the content/span addressing (`dna/address.json`,
  prose-only). Paths in (1) are already exactly the mixed-radix `path_form` (2) describes — these look
  like the SAME primitive at two resolutions, unrecognized as such.
- The 2π/n circle math is now known independently reinvented in at least 3 places (Company's System
  Map sunburst per the anchor, claude-ds's radial layouts per the anchor, and THIS repo's
  `organisms.js` graph/constellation) with zero shared derivation function.
- `reference/Counterpart-handoff/` is a whole separate, more OPERATIONALIZED sibling product (a real
  running React app + Postgres schema) sitting inside this repo as read-only reference, unsynced with
  and unreferenced by the `dna/` design-language — its resolve/kind/decision architecture is more
  mature in some ways (it actually runs) than the DNA face files, yet neither side cites the other.
- `docs/RESOLUTION.md`'s CASCADE-vs-COMPOSE distinction and 4-signed-axis model sits unreferenced by
  `dna/canon.json`'s simpler "derivation" law and entirely absent from the brainwave doc.
- `pieces/decision-card/` contains files named `real-cluster-identity.html`, `real-event-streams.html`,
  `real-file-identity.html`, `real-form-taxonomy.html`, `real-merge-sa-authorize.html`,
  `real-rerank-loadout.html`, `real-substrate-home.html` — these read as live renders of REAL Company/
  dragnet concepts through this DNA system already. Not opened (budget) — flagging as a likely
  additional source of address/identity consumption evidence for a follow-up pass.

## §D · Law candidates

1. **"Derive, never place"** (`docs/RESOLUTION.md §2`) — sharper than resolution-first: a value a
   person had to type for a specific case is a DEFECT, not a feature. A falsifiable per-value litmus
   test. Candidate for verbatim adoption into Tim's canon.
2. **CASCADE vs COMPOSE are not the same mechanism** — containment nests (nearest-scope-wins); every
   other axis (temporal, + 2 more per Tim's 4-axis bound) COMPOSES by multiplying, none "wins." The
   brainwave's §4 ("ratios all multiply") and its repeated invocation of "every boundary is a root of
   its own cascade" may be silently conflating two different resolution mechanisms — worth an explicit
   split before the one-math build encodes it.
3. **"Circle before square" (observed, not yet a law)** — in this repo the circle/angular partition
   shipped and the square/span partition stayed prose, inverting the brainwave's implicit expectation.
   Candidate generalization: derivable math tends to get BUILT at the point some rendering need PULLS
   it through, not at the point it is specified — spec completeness does not predict build order; a
   concrete consuming surface does.
4. **Two circles, not one** — a SHARP geometric circle (pixel angle, 2π/n, mechanically address-
   generating) is a different object from a SOFT semantic circle (subject sectors, requiring an
   authored CUT before it has addresses at all). Conflating them would make the brainwave over-claim
   "everything resolves" where subject.json insists some of it is irreducibly authored.
5. **Epistemic stance as a standing law** (`docs/RESOLUTION.md` preamble): nothing in any DNA/canon
   file — including the brainwave doc itself — is authoritative; "so far" is load-bearing. Applies
   reflexively to this very wave's output.

## §E · Scope additions — what folds INTO the centre

1. Pull `motion.json`'s ratified law-set (anchor_is_the_lca, transition_is_the_diff, change_budget,
   boundary_carries_identity, arrival_relative_to_path, anticipatory_verb, spatial_persistence,
   expert_lane) wholesale into the one-math build as the canonical movement-axis spec — it is more
   precise and already Tim-ratified, not agent-derived-from-principle like the brainwave's §6.
2. Fold `subject.json`'s CUT + ROUTE model in as the explicit boundary between what the address system
   can derive and what must stay authored judgment — a necessary corrective to the brainwave's implicit
   "everything resolves" framing.
3. Adopt `reader.json`'s `goodness_as_fit` / `brief_schema` (subject_region + reader + occasion +
   purpose) as the "purpose-recorded" invariant for anything the one-math system generates.
4. Extract `organisms.js`'s `folderDots()`/`graph()` radial algebra into a shared, named,
   general-purpose circle-partition primitive — it already works and is tested; it should become (or
   inform) the base circle-resolver the address algebra's circle half plugs into, rather than building
   fresh once Tim's equations land.
5. `docs/RESOLUTION.md` in full (only the head was read here) should be read by whoever formalizes the
   brainwave's §10 socket — it is the most rigorous resolution theory found in this wave's territory.
6. `docs/LINEAGE.md` is the genesis reasoning behind address/sequence/motion/subject — mine it for "why"
   before re-deriving justifications from scratch in the one-math build.
7. Flag to the lead/Tim: confirm whether Supabase project `gctunhsuwpaxeatwlmuv` ("Concept-Vi's
   Project") is the same backend as Project Vi's main Supabase — if so, target it for any future
   address/identity/group persistence schema rather than minting a new one.
