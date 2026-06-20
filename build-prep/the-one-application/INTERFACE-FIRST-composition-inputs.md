# THE INTERFACE FIRST — composition's input package for the build team
*Tim-directed 2026-06-18 (in-session). The decision-cards + RHM + archetypes interface is THE FIRST THING — Tim's HOOK into the whole process; all decisions/communications/interactions reach him through it, and all other work is then done WITH him THROUGH it. Built well, good shape, native desktop+phone both orientations, live + interactive. composition's contribution to the inputs the DNA-fork needs to make mockups Tim reacts to.*

## THE GOAL (Tim's words, decompressed)
A BETTER INTERFACE for the channels, completed first:
- decision-cards + the system the DNA-fork is building + the archetypes,
- OPERATIONAL on desktop AND phone, BOTH orientations (native, not responsive-shrink — device is a resolution dimension),
- the RIGHT-HAND-MAN goes through things WITH Tim, LIVE + interactive,
- it is Tim's HOOK: every decision · communication · interaction reaches him through it; he makes changes/updates/comments on what the streams do, through it (improving the system) → needs the Claude-Code-channel + RHM connection wired,
- much is already built (~80% per the as-is survey) — this is ASSEMBLE + a few new TYPES + the LOOK-AND-FEEL loop, not from-scratch.
- START LOCAL is authorized (don't wait on the substrate-home decision); the Supabase move happens later and BECOMES one of the first decisions the interface walks Tim through. The interface's first real job = deciding its own foundation.

## HOW THE FORK USES THIS
The DNA-fork looks at content + works out MOCKUPS to go through with Tim → Tim reacts → that's the look-and-feel → the build team (projection · composition · the fork(s) · DNA) builds v1. composition supplies: the TYPES (what to make), the LAWS (how to make it for Tim), the decision MODEL (what gets decided). The fork supplies the LOOK; Tim supplies the REACTION; DNA renders; projection hosts.

## 1 · THE ARCHETYPE CATALOG (the custom component TYPES — composition's domain)
Tim wants "visual and interactive representations of things — graphs, diagrams, selectors, interactive visual/spatial materials, instruments." In the factory these are ARCHETYPES: a typed thing the keystone renders into a visual/interactive surface, driven by data/sockets, themed by DNA, via the SAME mechanism as the decision-card (the first archetype). Adding a kind = a type row + a render-archetype, ZERO new screen-code. Each below is a render-archetype to define + mock up:

- **decision-card** (BUILT — the first archetype; render_kind=slide). The thing + options + RHM explanation; the take writes back. The subtype variants (binary/trade-off/naming/prioritize) select elements + explanation regime.
- **graph** — a node-graph of addressed things + typed edges (the DNA graph-instrument, in motion). Layout = a DATA definition (radial/cluster/tree — the new node-graph LAYOUT FAMILY in layouts.js); coil/uncoil = choreography-as-data; motion = DNA.motion resolved. Renders connectedness at levels-of-detail.
- **diagram** — a structured relational picture (flow/sequence/hierarchy) — like graph but authored-relation, not resolved-from-substrate. Same layout-as-data + connection-as-data spine.
- **selector** — choose among options/modes/things (the socket-selector model, already generic: any organism's sockets → a pick surface). Drives a value; the mode-selector is one instance.
- **instrument** — a live reading/steering surface (the V is the first: state→colour, dials, the verb-fan). A control surface that READS a value live + STEERS it (drive = re-resolve). Dials, gauges, the mode-as-colour cascade.
- **spatial-material** — interactive visual/spatial substances (the socket-materials: animation/glow/effect/palette carried by any asset; the radial/connection reveals). The "material substance / has weight" register Tim's design language wants.

Each archetype: { typed row · a render-archetype (slot_map / render_kind) · driven by data+sockets · themed by DNA tokens · obeys the legibility + no-dev-look laws }. composition defines the type + the contract; DNA renders; the fork mocks up the look.

## 2 · HOW TO MAKE THINGS FOR TIM (the laws — non-negotiable, on every archetype)
- ★ NEVER looks like a developer wrote it / that a developer would read it. No machine-names, no jargon, no filenames, no raw IDs surfaced. (Tim's supreme constraint.)
- LEGIBILITY (meaning, resolved from the row): every thing carries {name, is, fills?, why?}; the surface LEADS with name (human anchor) + is (what-kind), words before any glyph; touch-visible (phone has no hover — never hide meaning in a tooltip); name resolves per-instance (declared → humanise(leaf) → never the raw leaf).
- NAVIGABLE / SPATIAL, not a text-wall or a list — Tim recognises by sight, not by reading. A visual/spatial surface he can move through.
- NATIVE dual-device, both orientations — desktop AND phone, portrait AND landscape, each a distinct native treatment (a resolution dimension, like theme), not a shrunk desktop.
- DESIGN-SYSTEM-built (DNA tokens), no bespoke values; coherent scale/type/spacing; reads as product, not prototype.
- RESOLUTION-FIRST — everything resolves from typed rows; nothing hardcoded; a new kind = a new row, not new screen-code.

## 3 · WHAT GETS DECIDED (the decision model — BUILT + designed)
- decision/option/decision-card + legibility types: AUTHORED + committed (schemas/vi-vision/v1/, 23524ad). decision:// resolves LIVE in the company centre (fork, 97be816). state composed from a decision_take mark (registry-is-truth; the take IS the artifact).
- SUBTYPE system (designed): a `subtype` on the decision row → a decision_subtypes registry → { card_variant (elements), explanation_policy (the RHM regime) }. One knob → the right card + the right explanation per kind.
- ★ THE KINDS DERIVE, not invented: the subtype vocabulary + each kind's elements fall out of GATHERING Tim's real pending decisions (the union's 5 + DNA's overlaps + the merge + the substrate-home + …). So gathering the real decisions is the prerequisite that ALSO reveals the subtypes — and is the interface's first real CONTENT. (Coordination: who gathers the pending set? lead/recollection — flag.)

## 4 · THE BUILD SHAPE (local-first, assemble-not-build)
- HOST: projection (the instrument + the surface + the lifecycle, variant-agnostic). RENDER: DNA (the archetype variants via lyRender). TYPES+CONTRACT: composition (this catalog + the decision/subtype model + the keystone). SURFACE/MOCKUPS: the DNA-fork. TAKE: wildcard (the write-back). EXPLAIN: fork's RHM.
- LOCAL-FIRST: the keystone renders from the local registry today; build the interface local, Supabase-move-later (as interface content). No substrate-home dependency.
- LOOP: fork mockups → Tim reacts → look-and-feel → build team builds v1. composition feeds the types/laws/decision-model (this doc); reacts to mockups for type-fidelity.

## OPEN / FLAG
- The archetype RENDER-LAYER above the keystone (an `archetype` field + a loud-lookup registry) — designed, not built; it's how render_kind=slide/graph/selector resolve. composition builds it as part of v1.
- Gather Tim's real pending decisions (prerequisite for the subtypes + the first content) — lead/recollection lane.
- Native dual-orientation treatments per archetype — fork mockups + composition's form-factor resolve (the app-shell form-factor work).
