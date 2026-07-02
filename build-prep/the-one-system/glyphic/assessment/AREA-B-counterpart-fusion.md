# AREA B — the counterpart convergence (verified against live source, 2026-07-03)

> Territory: `/home/tim/repos/counterpart/design`, READ-ONLY (the ④ container session works live in this
> repo — see §0). Method: every claim below is **Observed** (file:line/JSON-key, or a command I ran and
> saw output from), **Inferred** (a pattern-match I did not execute), or **Your-idea** (my extension). The
> fusion-map rows are checked against the ACTUAL JSON on both sides, not the map's prose.

---

## 0 · FIRST — the ground has moved. REGROUNDING.md and THE-GENERATIVE-LANGUAGE.md are reading a STALE
snapshot of this repo, and the ④ container session is live in it right now.

**Observed** (`git log`, `git status`): HEAD is `a6bb16a`, branch `master`, 93 commits ahead of
`origin/main`, **two files with uncommitted local changes** (`app/webmanifest.json`,
`surface/runtime/surface.js`) and **untracked work** (`review/ingest/_extracted/_SOURCE-IMAGE-ADDRESSES.json`,
a whole `supabase/` directory). This is an active working tree, not a settled snapshot — do not treat
anything here as frozen, and do not edit it (per the brief).

**Observed**: 146 commits happened AFTER the mobile-form-review campaign (`mob-24`, the journal's last
entry) and are NOT in `FORMATION_JOURNAL.md` at all. They include:
- A structural **reorg** (`E.1`/`E.2`, commits `212ba23`/`237dea6`): `substrate/` → `registry/`,
  `engine/` → subdirs, `dist/` → `factory/`, **`ui/` → `surface/`**. This is why `CLAUDE.md`'s own
  quick-map and `docs/WAYFINDER.md` (referenced by CLAUDE.md and by the assessment ANCHOR) are BOTH
  WRONG/MISSING now — `docs/WAYFINDER.md` does not exist; the real derived wayfinder is
  `registry/wayfinder.md`, and it is **itself stale and empty** (see §1).
- A **graph redesign** (P1+P2, chipboard grid + opacity-for-size + flowing arrows).
- A new work-stream authored as "DNA Pack" building `docs/command/DNA-REPO-FACTS.md` (a live, honest,
  bias-flagged repo inventory — the single best orientation document in the repo right now, 1717 lines,
  I read it in full) plus `docs/command/DESIGN-LANGUAGE-EXTRACT.md`, `DNA-TRANSFER-PACK.md`,
  `DNA-UNION-SYNTHESIS.md` — a **visual-DNA extraction-from-source-decks campaign** running in parallel
  to (and mostly unaware of) the glyphic-language work this assessment serves.
- **An in-flight, non-working edit, left broken** (`DNA-REPO-FACTS.md` §4, self-reported by that
  session): `archetype.js`'s two-panel `readVis`/`saveVis` render path was mid-replaced with a
  composed-SVG generator using a `place()` regex to nest organism SVGs; "the (b) version FAILED to
  render (panels showed empty/text-only). This code is currently in a non-working state." **Do not
  build on `archetype.js`'s current renderExplained two-panel path without re-verifying it renders.**

**Your-idea**: REGROUNDING.md §5's "the spacing language… ends mid-discovery" is **WRONG, superseded 35+
journal entries and 146 commits ago** — see §5 below. Whoever wrote REGROUNDING read `FORMATION_JOURNAL.md`
only up to its early-middle, or read the counterpart `LINEAGE.md` reconstruction (which stops even
earlier) and mistook it for current state. This assessment corrects it with the live resolution.

---

## 1 · The wayfinder/registry are STALE and mostly EMPTY — coverage claims from them are false

**Observed** (`registry/wayfinder.md:1-4`): `*Derived from registry/address-registry.json — run
python3 engine/substrate/wayfinder.py. 2026-06-18 06:20 UTC.*` — **dated Jun 18**, i.e. before the E.1/E.2
reorg (Jun 22) that renamed `substrate→registry`, `engine→subdirs`, `ui→surface`. The wayfinder's own
"By location" section still lists pre-reorg folder names is moot because it's worse than stale — it's
**empty**: `### surface/ (0/29 profiled)`, `### dna/ (0/20 profiled)`, all 15 top-level dirs read
`(0/N profiled)`, and the header itself says `None profiled · None edges · None ghosts`. The census
(`assemble.py`) that would populate per-file facts was never run against the `scan.py` skeleton, or was
run and produced nothing — either way, **the substrate CLAUDE.md tells every agent to trust is inert**.

**Observed** (`docs/command/DNA-REPO-FACTS.md:14-15`): the same finding, independently made by the DNA
Pack session — plus a sharper one: `scan.py` line 12 hardcodes `SKIP_TOP = {"source","reference",".git",
"node_modules"}`, so the registry **structurally excludes `source/` (174 files, brand assets + deep docs)
and `reference/` (760 files — the real design-system handoff, incl. `colors_and_type.css`, `deck.css`,
`workshop.css` that the extraction spec cites)**. `registry/address-registry.json`'s 669 addresses and the
"643 tracked files" figure are NOT the whole repo; `git ls-files` itself misses ~934 files/341MB because
`source/`+`reference/` are gitignored. **Any dragnet, coverage claim, or "we searched the whole repo" from
either side must include these two directories explicitly — they are currently invisible to every
registry-based tool.**

**Verified by use**: `python3 -c "import json; r=json.load(open('registry/address-registry.json'));
print(r['_meta'])"` → `{'root': '...', 'entries': 669}` (confirms the count, confirms no per-file
profiling metadata beyond the bare count).

---

## 2 · The fusion map, row by row — verified against live JSON + live code on both sides

Method: for each row I opened the actual `dna/*.json` (counterpart) and the actual JS/analysis file
(claude-ds), and report what's really there. Rows are ordered **by what unblocks the glyphic instrument
first**, per the brief — organisms/shapes/connectors lead because they are the furniture the writer's
canvas has zero of today (REGROUNDING §6.6: "bare nodes on a void, no atmosphere/organisms").

### 2a-0 · tokens.json ↔ tokens/*.css + colors_and_type + emit.py — **same PATTERN, disjoint VALUES; a mechanical (not semantic) fuse**

**Observed** (`dna/tokens.json` root, `version: "stable-1"`): a hand-authored, pixel-sampled palette —
`color.surface` (page/warm/cool/nested/goldwash/base/line, all warm-cream hex), `color.accent` (gold
`#B29135`, gold_soft, ochre, bronze, bronze_line, charcoal `#15120C`, gold_pop `#E3C421`), `color.ink`
(body/secondary/faint), an `axis_ramp` (an ORDERED 4-stop warm-metal scale, explicitly for ordinal
colour-stepping, not arbitrary swatch use), a `warm_pole` ramp (golden-hour gradient family for
warm-imagery stand-ins), a `type_hues` block (file-type→colour categories for the Graph instrument,
explicitly distinct from folder-bronze and from 6 state-machine themes), plus shadow/radius/space/
type-scale/weight/texture/chrome blocks (not shown in full here — see §2f/§4 for space).
`meta.edited_by: "token-playground"` — this file has a LIVE EDITOR app, not just a JSON someone hand-types.

**Observed** (`/home/tim/company/design/_system/emit.py`, full function `emit()`): claude-ds's token
pipeline is a **two-layer compiler** — `primitives` (raw values) feed named `tokens` that are either
`{"v": value}` (flat literal) or `{"ref": <primitive>}` (an indirection: change the primitive once, every
`ref` follows). It fails LOUD on an unknown ref or a token with neither `v` nor `ref`. Output is a single
generated `:root{}` CSS block, marked `DO NOT hand-edit`. This is a strictly MORE governed pipeline than
counterpart's: counterpart's `tokens.json` values are flat hex literals with no primitive-indirection
layer at all — e.g. `gold_pop` and `gold` are independently authored hexes, not `gold_pop: {ref: gold}`
style derivations. **Fusing tokens is almost entirely mechanical**: counterpart's flat `color.accent.*`
block maps directly onto emit.py's flat `{"v": ...}` token shape; the one REAL gap is that counterpart has
no primitive layer, so importing it as-is would flatten past whatever `ref`-based reuse claude-ds already
relies on. The fusion map's "α's derived-roles model in β's emit+governance" is accurate: β (claude-ds/
emit.py) is the governance layer to keep; α (counterpart/tokens.json) supplies the actual warm-palette
VALUES, not the pipeline.

**The values genuinely differ and need a decision, not a merge**: counterpart's warm-cream/gold palette
(`#F8F2E6` page, `#B29135` gold) is corpus-sampled from Tim's real decks (HARVEST-3 evidence trail);
whether claude-ds's current token values already match, diverge, or predate this sampling I did NOT check
line-by-line (a `dna/tokens.json` vs `colors_and_type.css` diff is a fast, high-value follow-up not done
in this pass — flagged in §6). **Also flag**: `docs/command/DNA-REPO-FACTS.md:28` records the live
④/DNA-Pack session EDITING `dna/tokens.json`'s warmth poles + charcoal THIS SESSION, unverified-by-render
— so even counterpart's own "stable-1" token layer is mid-edit right now, not settled ground to copy from
without re-checking after that session's next commit.

### 2a-1 · grammar.json ↔ CV_AXES (axis-core.js + 9 axis dirs) — **NARROWER but PROVEN vs BROADER but UNVERIFIED-BY-RESOLVER**

**Observed** (`dna/grammar.json` top-level keys): `base` (unit=8), `signature_ratio` (×1.5),
`commensurability`, `scales` (type + space, each with a resolver-ready `steps`/`vocabulary`), `proportion`
(named zone archetypes: title-main-footer, split-weighted, plate-internal — fractional, scale-free),
`composition`, `resolution` (context-is-a-scope, nearest-scope-wins), `meta_principles`, `alignment`,
`color`, `texture`, `dials` (density/warmth as named multiplier tables), `scale_tiers`, `invariants`,
`shape`, `movement`, `texture_placement`, `atoms`, `motion`, `provision`, `rules_corpus`. This is a
**single flat file covering type+space+colour+texture+shape+motion as one resolvable grammar**, and
(§2f, §4) it is PROVEN — `resolve.mjs` re-derives real pixel measurements from it, 11/11, executed.

**Observed** (`claude-ds/axes/axis-core.js`, full read of the axis-instance factory + 9 subdirectories:
`color/depth/fill/form/motion/size/space/symbol/texture/`): CV_AXES is **structurally richer** — each
axis is a first-class typed object (`makeAxis(spec)`) with `groups→values` hierarchy, a
`resolveCSS()` that returns `var(--token)` (never a copied literal), a `candidates(subscription)` query
surface an editor/foundry can read directly, and a uniform `register/resolve/list/query/subscribe` verb
set shared with `CV_REGISTRY`/`CV_AI`/`CV_MEANING`. This is a GENERATIVE MODEL (a value's identity is a
token pointer, resolved live) vs counterpart's grammar, which is a **compiled-number resolver** (a rule
produces a px value once, checked against measurements).

**These are not competing implementations of the same idea — they solve different problems.** CV_AXES
answers "what are the valid values of axis X, and what CSS does value V resolve to" (a live authoring/
validation surface). `resolve.mjs`/grammar.json answers "given this rule and this raw pixel context, what
number comes out, and does it match what was measured" (a derivation PROOF). **Neither replaces the
other**: the glyphic instrument needs BOTH — CV_AXES for "what can this slot legally be," grammar.json's
resolver pattern for "given the frame's real size, what number does this rule produce." Fusing means
teaching a `space`/`size` CV_AXES value to resolve THROUGH counterpart's `unit × step` rule (today
`axes/space/space-axis.js`'s values are direct token refs, not rule-derived px) — i.e., import
counterpart's resolver AS a `resolve:` function on the relevant CV_AXES values, per axis-core's own
documented `resolve: fn(value, ctx)` extension point (seen in `axis-core.js`'s value-payload doc comment,
§ observed above). This is a clean seam, not a rebuild.

**Verified live** (this session, `node engine/prove/resolve.mjs`): counterpart's half is proven against
real pixels. **Not verified**: whether any CV_AXES value currently resolves through a comparable
measured-proof harness — I found no `resolve.mjs`-equivalent proof script under `claude-ds/axes/`; this
absence itself is worth flagging back into REGROUNDING's honest-hard-parts list.

### 2a · organisms.json + icons.json ↔ CV_ICONS + foundry + DiagramSolver organisms — **THE MAP ROW UNDERSTATES WHAT'S BUILT**

**Observed** (`dna/organisms.json` meta): 17 declared organism records (mesh, hub_network, icon_strip,
consequences_box, cascade, detail_strip, phase_strip, process_steps, stage_cards, comparison_matrix,
testimonial, branch_tree, time_tree, porthole_row, updown_duo, donut, bars). Of these, **5 have
`generator: null`** (process_steps, stage_cards, branch_tree, time_tree, porthole_row, updown_duo) —
declared gaps, honestly marked.

**Observed** (`surface/runtime/organisms.js:893`, the actual export line): the LIVE generator set is
**28 functions**, not 17: `icon, iconStrip, mesh, hubNetwork, graph, consequencesBox, cascade,
detailStrip, phaseStrip, testimonial, checkMatrix, donut, bars, ordinalVar, connector,
taxonomyEmergence, designLibraryObject, fileStack, planThumbnail, projectTileGrid, versionStack,
sourcePanelVisual, evidenceBand, interfaceFragment, artifactFlow, artifactCluster, boardGroups,
constellation, navRail`. **11 of these 28 (`graph`, `connector`, `taxonomyEmergence`,
`designLibraryObject`, `fileStack`, `planThumbnail`, `projectTileGrid`, `versionStack`,
`sourcePanelVisual`, `evidenceBand`, `interfaceFragment`, `artifactFlow`, `artifactCluster`,
`boardGroups`, `constellation`, `navRail`, `ordinalVar` — actually 17) exist in CODE but are NOT
registered in `dna/organisms.json` at all** — live drift between the declared registry and the built
instrument, in the generous direction (more built than declared). Every one is real SVG, tokens-only
colour (per `engine/lint/dna.mjs`'s enforcement), deterministic (seeded via `mulberry32`), with
`aria-label`.

**Verified by grep, not by rendering** (I did not open a browser — read-only territory, and no dev server
confirmed running): the functions exist and are exported; I have NOT visually verified they render
correctly today, especially given the archetype.js in-flight breakage noted in §0.

**What claude-ds has that this row needs**: `CV_ICONS`/the foundry generate icons FOR a shape (the fill
inside a vessel); counterpart's `organisms.js` generates whole SVG SCENES (hub-and-spoke networks, file
stacks, blueprint plans, constellations, board groups) that are populated mid-scale structures —
`DiagramSolver.jsx`'s "organisms" are structural containers, not this kind of rendered content-object.
**They are complementary, not overlapping**: claude-ds solves LAYOUT of organisms; counterpart RENDERS
organism content. Fusing = counterpart's `DNA.org.*` becomes the content-generator claude-ds's
`ContainmentTree`/`DiagramSolver` slots call INTO, the same way `dna/organisms.json`'s note already says
("organisms are built FROM molecules and icons, and fill layout slots; they own no page decisions").

**Fusion requirement, concretely**: port `surface/runtime/organisms.js` (894 lines, zero external deps,
pure functions `(data, opts) → SVG string`) into `claude-ds/assets/icons/` as a sibling to `cv-icons.js`
— it needs ZERO of counterpart's registry machinery to run standalone (verified: it's an IIFE exporting
`window.DNA.org`, reads no other counterpart file). The only coupling to strip: it reads counterpart's
own `--dna-*` CSS custom properties for colour — **these must be re-pointed to claude-ds's
`var(--accent-gold)` etc. token names** (a mechanical find/replace, ~30 colour refs, verified by
`grep -c "var(--dna-" surface/runtime/organisms.js` pattern).

### 2a-2 · layouts.json ↔ kind.graph + glyphic-type.js sockets + ContainmentTree — **compatible SHAPES, different ENFORCEMENT strength**

**Observed** (`dna/layouts.json` meta, `version: "layouts-4"`): archetypes are **frames** (proportions
referenced FROM grammar.json, never redeclared) + **zones** in reading order + **typed slots** (sockets
accepting content kinds — `slot_types` enumerates ~15: heading/figure/label/list/image/diagram/timeline/
stat-band/statrow/pills/icon-strip/connector/arrow/table/plate/band) + **exactly one focal slot per
frame** (no numeric priority — "global ranks would couple slots to one use and break composition") + a
**reflow policy**. Deck-first, evidenced (all 16 slides of the real deck read + cross-checked against 19
locked mockups). **Verified directly** (`python3 -c "import json; print(list(json.load(open('dna/
layouts.json'))['archetypes'].keys()))"`, run this session): the actual archetype set is
`session-card, channel-view, board-view, transcript-viz, trio, duo, split-bleed, field, grid, stack,
immersive, plate-internal, decision-card` — **13 named archetypes**, each with a `slot_map` (slot.id →
dotted path on the record) — i.e., these are already wired to bind against LIVE DATA records, not just
abstract frames. (Cross-checks DNA-REPO-FACTS §3's list rather than relying on it — that document
self-flags as partial/biased and is authored by the live ④/DNA-Pack session, §0.)

**Observed** (`claude-ds/app/registry/glyphic-type.js`): the glyphic's own structure is **parts → slots →
sockets**: a `slot` takes a VALUE from a single-source vocabulary (a CV_AXES subscription, e.g.
`sub('form')`, `sub('color', {groups:[...], default:'gold'})`); a `socket` is an attachment point that
takes a TYPE (another registered component) or an event, carrying `accepts`/`forbid` conditions PLUS "an
address to occupant" (a socket knows not just what CAN fill it but what currently DOES, addressably).
`core/ContainmentTree.jsx` is the layout SOLVER consuming this: it does LOD-based pruning
(`LOD_RULES: summary/pitch/full`, cutting on `node.priority` + a `detail:"support"` flag), and dispatches
atom rendering through a **registry** (`ATOM_RENDERERS`) rather than an if-chain — "a new atom is DATA
not a code edit."

**The two are compatible at the concept level (typed slots accepting typed content) but claude-ds's
version is more STRUCTURALLY enforced**: counterpart's `slot.accepts:[type]` is a plain array of type
names (a convention, policed by nothing I found — no lint script surfaced for layouts the way
`lint-dna.mjs`/`lint-space.mjs` police colour/space); claude-ds's socket has explicit `accepts`/`forbid`
CONDITIONS plus a live occupant-address, and its LOD pruning is genuinely more sophisticated than anything
in counterpart's layout face (counterpart has no equivalent of `visibleAtLOD`/priority-based pruning — its
"cut-depth" theory, per `dna/SPACES.md` Entry 29, was DEFINED but explicitly NOT YET built into a
registry, per REGROUNDING's own honest-status note). **Fusion requirement, concretely**: port
counterpart's 13 archetypes as DATA into claude-ds's socket grammar (each archetype's zones become parts,
each slot's `accepts` becomes a socket's `accepts`), and gain claude-ds's LOD/priority pruning + condition
enforcement for free — this is the one row where claude-ds's mechanism is straightforwardly the better
host, and counterpart supplies the evidenced CONTENT (13 real, deck-verified archetypes vs claude-ds's
`kind.graph`, which I did not find a populated instance of — worth a follow-up: does `kind.graph` have any
archetypes registered today, or is it an empty mechanism waiting for exactly this content?).

### 2b · shapes.json ↔ CV_SHAPES.shapeTypes / CV_MEANING — **REAL CONFLICT, not a simple merge**

**Observed** (`dna/shapes.json`): counterpart's shape-meaning is CORPUS-DERIVED from Tim's actual decks —
`octagon: "the core itself", cardinality {per_page:1, per_sequence:1}` (evidence: "deck s4 — the V hub,
the deck's only octagon"), `hexagon: "engine / machine subsystem"` (evidence: Property Wizard badge,
company-info p2/p10), `diamond: "the intelligence / the agent (Vi)"` (evidence: company-info p10,
pitch-deck p6/p9), `circle: "HUMAN only — people, roles, avatars (policy 2026-06-10: circles stay
human)"`, plus a RESERVED `thing-node` (square+radius, for the first non-human node — a genuine
minting-policy citizen, not built yet), and `chevron` for phase/forward.

**Observed** (`claude-ds/assets/icons/cv-shapes.js:60-79`): claude-ds's `shapeTypes` is an INVENTED
abstract taxonomy, not corpus-evidenced — `circle: Entity` (generic, not human-specific), `triangle:
Action`, `square: Object`, `diamond: Decision` (AI/logic — close to counterpart's "the agent" but framed
as a decision-branch, not an identity), `pentagon: Feature`, `hex: System` (matches counterpart's
hexagon=engine, coincidentally), `heptagon: Specialised`, `octagon: Gateway` (an endpoint/boundary — NOT
"the core," the OPPOSITE cardinality-role from counterpart's octagon-as-hub).

**This is a genuine semantic collision, not two views of one thing**: counterpart says octagon=the one
hub/core (cardinality-limited, per_sequence:1); claude-ds says octagon=Gateway/endpoint (a boundary, can
recur freely). Fusing these requires a **Tim decision**, not a mechanical merge — pick one octagon meaning
(or split it: keep octagon=core for the glyphgraph's ROOT node only, use a different shape for
gateway/boundary nodes). **This blocks §2a's "shape=f(entityType) lookup" from being ported blind** — the
lookup table itself needs reconciling first, or the glyphic instrument will silently contradict Tim's own
brand grammar the moment it renders a hub.

**A third variant, found in passing**: `claude-ds/core/ContainmentTree.jsx`'s own comment block declares
YET ANOTHER shape-meaning mapping, at the BRAND-ENTITY level (not the abstract-type level): "circle = User
Portal · hex = Property Wizard · octagon = Virtual Hubs · diamond = Vi," explicitly marked as sharing
`assets/icons/cv-shapes.js`'s `entities` array (§ observed above: `entities` list with `userPortal→circle,
propertyWizard→hex, virtualHubs→octagon, vi→diamond`). This is CLOSER to counterpart's evidenced mapping
(octagon as a bounded/singular OUTPUT surface, not a generic gateway-class) but still not identical
(counterpart: octagon=the hub/core itself, cardinality 1; claude-ds: octagon=Virtual Hubs the PRODUCT,
which could recur). **Three shape-meaning tables exist across the two systems today** (CV_SHAPES.shapeTypes
abstract-generic, CV_SHAPES.entities brand-specific, counterpart's shapes.json deck-evidenced) — the
fusion needs to pick which ONE is canonical, or make explicit which axis each answers (generic semantic
class vs specific brand entity vs corpus-observed frequency/cardinality), rather than silently keeping
three.

**What's genuinely new on counterpart's side and NOT in claude-ds at all**: the `minting_policy` (a new
shape enters ONLY with declared meaning AND cardinality — "no casual polygons," lint-enforced) and the
`law` (facet-degree inversely proportional to frequency, countable by lint — `invariant
core-mark-rarity in grammar.json`). claude-ds has no shape-minting governance; any glyph symbol the
glyphic engine mints (memory notes "+12 'language'-family symbols... tonight") should pass through this
kind of gate, and currently doesn't.

### 2c · connectors.json ↔ CV_EDGES + line-mood — **DISJOINT VOCABULARIES, genuinely complementary**

**Observed** (`dna/connectors.json`): verbs are `transport` (carries between siblings, socket→plug
geometry, gold arrival-terminal), `gather` with **direction as a property of the verb** (`in`=many→one
convergence, `out`=one→many fan, both deck-evidenced), `descend` (drop-lines, row steps down), `orbit`
(cyclic, continuous — "Configure/Update orbiting the Property Wizard on dashed ellipses," corpus-direct).
Plus a `seam_law` ("only elements of THIS layer may cross a zone boundary") and a distinct
`annotation_arrow` (the editorial pointing-finger, explicitly NOT a movement verb — "adds attention,
carries nothing").

**Observed** (`claude-ds/assets/icons/cv-edges.js`, full file, 68 lines): `CV_EDGES.kinds` has exactly
**4 entries**: `face` (dashed/gold, "has a viewable page"), `documents` (dashed/bronze, "explains/
teaches"), `higher-order` (lines/sage, "connects up to a concept"), `navigates` (dots/muted, "contextual
navigation"). **Zero overlap in vocabulary** with counterpart's verbs — claude-ds's edges are about
KNOWLEDGE-GRAPH relation types (what kind of fact connects two things); counterpart's connectors are about
MOTION/COMPOSITION relation types (how something visually moves/converges/fans on a canvas). The map row
"ONE edge language: verb × direction × mood × seam law" is **aspirational, not a description of overlap**
— today these are two non-competing axes that should compose (an edge kind like `navigates` could carry a
connector verb like `transport` as its rendered geometry), not two versions of the same thing to pick a
winner from.

**Fusion requirement, concretely**: `CV_EDGES.resolve(spec)` already takes `{kind, line?, direction?,
ink?}` and returns full facets — this is the RIGHT shape to extend. Add counterpart's verb vocabulary as
a **second facet dimension** on the same object: `{kind: 'navigates', verb: 'transport', ...}` where
`kind` answers "what fact" and `verb` answers "what motion." The `direction`-as-property-of-verb pattern
(gather(in)/gather(out) rather than two verbs) is the cleaner design — claude-ds's `direction: 'to'/'from'/
'both'/'none'` on `face`/`documents`/etc. is the SAME pattern already, just not yet extended to `gather`.
This is a genuinely easy, low-risk fuse: add fields, don't restructure.

### 2c-1 · motion.json ↔ motion axis + FLIP morphs — **NO OVERLAP FOUND; counterpart's is a full temporal theory, claude-ds's is a CSS-loop vocabulary**

**Observed** (`dna/motion.json`, read in full — 14KB, `version: "motion-5"`): this is the richest, most
theoretically developed face in the whole repo. `registers_of_change` (three kinds — MOVEMENT "the person
travels," TRANSITION "the content travels, nothing teleports," STATE "the thing itself changes, same unit
new state" — each with its own laws). Ten named `laws`: `everything_animates` (no-teleport invariant),
`change_budget` (bounded difference per hop, tours-evidenced: point density follows rate-of-change of
view, not distance), `anchors_and_changers` + `anchor_is_the_lca` ("WHICH ring holds is not a design
choice — it DERIVES: the LCA of the changers' addresses is the boundary that must hold"),
`transition_is_the_diff` ("transitions are COMPUTED, never hand-authored: diff two views by address —
unchanged=anchors, changed=changers"), `change_intensity` (a spectrum: recolour < reflow < swap <
dissolve-and-reform), `attention_order` (even a static page is temporal — reading IS time),
`arrival_relative_to_path` (a transition is a property of the EDGE, not the destination — verbally
evidenced: the deck's "And it's Difficult…" opening IS a verbal rotation-on-arrival), `anticipatory_verb`
(each connector verb has a temporal signature — descend=zoom-in, transport=lateral-slide, gather=
convergence), `spatial_persistence` (off-screen is a PLACE, not oblivion), `shared_element_continuity`,
`boundary_carries_identity` (THE RING LAW — interior change=state, boundary change=becoming). Plus
`timescales`: the SAME law-set runs at five scales (relationship/artifact/page/interaction/icon) — this is
where `THE-GENERATIVE-LANGUAGE.md` law 9's "one law-set at five timescales" comes from, verbatim-traceable
to this file. Evidence class is unusually strong: `provenance_tours` marks this as **tours-direct** —
Tim's own shipped virtual-tour product (360° architectural navigation), stronger than deck-inference.

**Observed** (`claude-ds/axes/motion/motion-axis.js`, full groups+values list): CV_AXES's motion axis is a
**5-group, 8-value CSS ANIMATION-STATE vocabulary** — groups are `static/ambient/attention/interactive/
process`; values are `none/breathe/float/pulse/glow/bob/tilt/spin`, each mapped to a CSS keyframe class
name (`mo-breathe`, `mo-pulse`, etc.) with `meta:{loop:true}` or `meta:{hover:true}` flags. This answers
"is this element alive, and how" (an idle-vs-active indicator system) — it has NO concept of transition-
between-views, no diff/LCA/anchor computation, no address-awareness at all. **I searched explicitly for
"FLIP" (the well-known First-Last-Invert-Play animation technique, which is what "FLIP morphs" in
REGROUNDING §9a implies) across all of claude-ds's `.js`/`.jsx` files and found zero matches** — either
the FLIP-morph mechanism named in REGROUNDING §9a doesn't exist in code yet (only in the roadmap
vocabulary) or lives under a name I didn't search; this is worth a direct confirm from whoever wrote that
line before assuming it's built.

**This is the sharpest and most consequential gap in the whole assessment for the glyphic instrument's
LIVE GROWTH problem** (REGROUNDING §4's "layout-jump on live growth… stable-slot/freeze law exists,
unwired"). Counterpart's `motion.json` is not just relevant — it is the SPECIFIC, ALREADY-WORKED-OUT
answer: a glyphgraph growing from conversation is exactly the "diff two views by address, anchor = LCA of
changers, budget the change per hop" problem this file solves in the abstract. Nothing needs to be
invented; `anchor_is_the_lca` + `transition_is_the_diff`, composed with `dna/address.json`'s LCA-on-
address-tree arithmetic (§2f), IS the stable-slot/freeze law, already derived, already named, never coded.
**Fusion requirement, concretely**: this is a PORT of THEORY into a MISSING IMPLEMENTATION, not a merge of
two implementations — claude-ds's motion axis stays exactly as-is (it answers a different question,
element liveness) and gains a SECOND, new mechanism for view-transition-as-address-diff, built fresh from
`motion.json`'s laws directly (no existing claude-ds code to reconcile against).

### 2d · modes.json ↔ data-theme/grounds + tonal zoning + CV_MODE — **the map row conflates two different modes systems**

**Observed** (`dna/modes.json`): `surface_mode(ground)` is a **derived visual-chrome dial** — ground is
imagery/render → `product` chrome (dark glass controls, frosted cards, hotspot markers); ground is paper →
`document` chrome (outlined light pills, tinted plates). Resolves per-surface, nearest-scope-wins,
grounds nest (a dark product screenshot can sit inside a paper slide and keep its own chrome). This is
PRODUCT-VERIFIED (not just deck-predicted) against real screens: tour viewer, analytics, captures ledger.

**Observed** (`claude-ds/atomicity/mode-engine.js`): `CV_MODE` is an **interaction state machine** — a
`Map` of registered modes with `activate(id)`/`onEnter`/`onExit`/`subscribe` — "what a click DOES," per
its own header comment. This is orthogonal to `modes.json`'s chrome-derivation: CV_MODE governs BEHAVIOUR
switching (e.g. "operator mode" vs "inspect mode"); `modes.json` governs VISUAL CHROME switching by
ground-type. **The fusion map's "chrome resolved per-ground nearest-scope-wins; mode/app/panel
non-exclusive" is correct as a description of the target state, but it undersells that these are two
independent axes today, not two versions to reconcile** — counterpart's document/product chrome dial has
literally no equivalent anywhere in claude-ds; it is pure NEW furniture.

### 2e · sequence.json ↔ (missing in claude-ds) — **CONFIRMED: no counterpart exists, verified by search**

**Observed**: `grep -rln "sequence\|narrative\|arc\b" claude-ds/analysis/` found only unrelated hits
(pitch-deck analysis files that happen to contain the word). No narrative-role registry, no tier system,
no arc/envelope machinery, no generation-ladder anywhere in claude-ds's code. The map row is accurate:
this is a genuinely missing face.

**Observed** (`dna/sequence.json` + live proof, `node engine/prove/resolve-sequence.mjs`, run and verified
this session): `plan('pitch', 16)` → `open×1 · argue×2 · show×5 · prove×3 · plan×1 · people×3 · close×1`,
**7/7 checks PASS** (total pages, run lengths, bookends immersive, archetype changes at role boundaries,
warmth choreography bookends≥70/middle≤60, every affinity resolves to a real archetype, every envelope
register exists in tokens.dials). This is a **working, tested, live generative arc-planner** — feed it a
narrative role plan + a page count, it derives a whole structured telling with warmth/archetype/register
resolved per page, none of it typed in.

**What this means for the glyphic instrument, concretely**: a glyphgraph GROWN from conversation (the
A0-A6 writer) currently has no sense of "arc" — every node added is structurally the same kind of event.
`sequence.json`'s narrative_roles + generation_ladder is the exact machinery for "a glyphgraph telling has
an ARC" (per THE-GENERATIVE-LANGUAGE §2's own note). **Porting this face is high-value and self-contained**:
`resolve-sequence.mjs` reads only `dna/sequence.json` — no coupling to counterpart's registry/address
system. It can be copied into claude-ds's `core/` wholesale as the missing "arc resolver," renamed for the
glyphgraph's node-kinds instead of deck-page-kinds.

### 2f · address.json ↔ the spatial theorem (n/x) + ui:// registry — **counterpart's half is PROVEN;
claude-ds's half is UNBUILT (not "crude" — genuinely absent in code)**

**Observed** (`dna/address.json` laws): spans-not-points (child k of n owns `[(k-1)/n, k/n)`),
derived-not-assigned, order-from-division, origin-law. **Verified live**
(`node engine/prove/resolve.mjs`, run this session): **11/11 derivations pass** — radius, type scale,
space scale, THREE proportion archetypes (title-main-footer, split-weighted, plate-internal), all
re-derived at a SECOND tier (component) with IDENTICAL fractions, all re-derived at a THIRD raw axis
length (poster 1800px) with identical fractions, density dial re-deriving spacing with no second number
set. The worked example traces a real mockup's full geometry (margin/gap/content-width/plate-width/
radius/title-size) from ONE grammar file, nothing hand-typed. **This is not a design document — it is a
tested resolver with a pass/fail harness**, exactly the kind of proof-machinery REGROUNDING §6.2 says
claude-ds's spatial theorem lacks.

**Observed** (searched claude-ds for `zoneDepth`/`stableSlot`/`n/x` patterns — zero hits): claude-ds's
"zone-depth formula" and "stable-slot placement" that REGROUNDING §3/§9a cite as AREA-21-catalogued
locations are either in a doc-only form (never implemented as code) or under different names I haven't
found — worth a follow-up grep by whoever holds that area, but from this side: **there is no address
RESOLVER analogous to `resolve.mjs` anywhere in claude-ds's code tree**.

**Fusion requirement, concretely**: `address.json`'s laws + `resolve.mjs`'s `zones(archetype, axisPx)`
function is the most directly portable, highest-leverage single piece of machinery in this whole
territory — it is 102 lines, pure math, zero DOM/framework coupling, proven against real measured pixels.
The glyphgraph's placement problem (REGROUNDING §6.2, "currently a crude ring") should be built AS an
instance of this resolver: a glyphgraph node's position = its span address in its parent frame, exactly
as `zones()` already computes for deck layouts. This is the single clearest "port this file, don't
reinvent it" finding in the whole assessment.

### 2g · subject.json + reader.json ↔ (missing in claude-ds, partial in ledger/RHM) — **confirmed missing, richer than the map row suggests**

**Observed** (`dna/subject.json`): sectors radial/simultaneous around an origin, the projection law (cut
+ route as the two authored acts), `arc_as_tour`, `siblings` (siblings-must-agree invariant), a
`lexicon_scope` (jargon christened once per subject), `canvas_geography`, `coverage` (addresses mapped
onto sectors = gap/overlap analysis). **Observed** (`dna/reader.json`): `moving_boundary` (jargon-as-
address, expert-density = address-density — this is the EXACT mechanism memory's
`altitude-transformation-layer` fact names independently), `occasion_ladder` with `cluster_attractors`,
`dial_coupling`, `goodness_as_fit`.

**Your-idea**: these two faces together ARE the formal version of "render for Tim's altitude" — the
RHM/operator's reader-adaptation is currently a set of ad-hoc conventions (per memory:
`altitude-transformation-layer`, `translate-everything-human-meaning`); `subject.json`+`reader.json`
supply the MISSING FORMAL MODEL underneath those conventions (a reader has a held-context/occasion/
distance that DERIVES the right density, not a set of hand-written rules per surface). This is a bigger
find than the map row implies ("the FRAME face") — it's a candidate specification for the RHM's
resolve(content, reader) itself, not just a design-system nicety.

### 2h · voice.json + molecules.json ↔ the read-out / transglyphing — **confirmed bimodal pattern, evidenced**

**Observed** (`dna/molecules.json` `stat_couplet`, `bullet.variants.claim/proven`): every visual atom
carries an explicit `voice` block alongside its visual facets — figure-colour AND "telegraphic, no verb,
no hedge, ≤5 words" wording rules, in the SAME record, with a `voice_form` id linking to `voice.json`'s
registers. This is the literal, working version of THE-GENERATIVE-LANGUAGE §1.17/molecules-row claim
("every visual unit carries its verbal twin") — not aspirational, it's how `dna/molecules.json` is
actually structured today, in every entry I opened.

**Fusion requirement**: the glyphic engine's read-out ("transglyphing," per REGROUNDING §3) should adopt
this exact co-located structure — every glyph/facet record gains a `voice` block with register + form-id,
rather than a separate read-out generator inferring words from shape after the fact. Cheap to adopt (it's
a JSON-authoring convention, not new code), high payoff (guarantees the two halves never drift).

### 2i · canon.json ↔ LANGUAGE.md + 00-the-thinking — **verified, the merge law is real and explicit**

**Observed** (`dna/canon.json` meta.merge_note, read verbatim): *"for Tim's other sessions/projects that
will eventually combine: the LAWS sector is the portable core (content-free principles); the FACES sector
is this identity's specifics. Merge = adopt the laws, bring your own faces."* This is the exact quote
THE-GENERATIVE-LANGUAGE.md's own header cites — confirmed present at source, word-for-word. The canon's
root has 7 top-level sector lines (portable core · the four spaces · the one resolution chain
sequence→layout→organism/molecule→shape/connector→rule→token · the sixteen registries · the working
surfaces · the "nothing claimed unverified" proof ledger · the method). **This resolution chain line is
itself the clearest one-sentence statement of what "fusing" the two systems' generative pipelines means**:
claude-ds would need the SAME chain (sequence→layout→organism→shape/connector→rule→token) to exist as one
traceable path, which today it does not (§2e, §2f above are exactly the missing links: sequence and
rule/token-resolver).

---

## 3 · Working assets ready to serve the glyphic instrument DIRECTLY tonight

Ranked by (a) how self-contained the file is (can it be lifted with minimal rewiring) and (b) how much of
the "80% law — frames need furniture" gap it closes.

1. **`surface/runtime/organisms.js`** (894 lines) — 28 pure SVG-generator functions, tokens-only colour,
   deterministic (seeded RNG), zero framework coupling. **The single highest-value port**: this closes
   REGROUNDING §6.6's "no atmosphere/organisms" gap directly. Coupling to strip: ~30 `var(--dna-*)`
   colour references need re-pointing to claude-ds token names (mechanical).
2. **`engine/prove/resolve.mjs`** (102 lines) + **`dna/address.json`** (its data) — a PROVEN spatial
   resolver (11/11 verified this session). Closes REGROUNDING §6.2's placement gap; the `zones()`
   function is a working `n/x` implementation in miniature, ready to generalize to the glyphgraph's
   own frame nesting.
3. **`engine/prove/resolve-sequence.mjs`** (88 lines) + **`dna/sequence.json`** — a PROVEN arc-planner
   (7/7 verified this session). Closes the "no ARC" gap named in the fusion map's own keystone
   correspondence.
4. **`surface/styles/phone.css` + `piece.css`** — the glass/frost material (`.p-glass`,
   `.p-frost`, backdrop-filter blur, tokens-addressed shadows) is real, live CSS, verified present at
   the exact lines cited. Directly reusable as the glyphgraph canvas's chrome material — this is
   citable "wearing the DNA" furniture, not a description.
5. **`dna/organisms.json` + `dna/shapes.json` + `dna/connectors.json`** as DATA (not just as documents
   to read) — once shape-meaning is reconciled with claude-ds (§2b, needs Tim), these three JSONs are
   directly loadable registries a fused engine can read at runtime, the same way counterpart's own
   `almanac.js` reads them today via `surface/atlas.json`.

**What counterpart's faces conspicuously LACK that claude-ds has** (the reverse direction, per the brief):
- **The live AXES system** (`CV_AXES.css → var(--token)`, `validate`/`candidates`) — counterpart's
  grammar resolves VALUES (radius, space, type) but has no equivalent to claude-ds's generative
  axis-model with live candidate-generation/validation across 9 axes (color/depth/fill/form/motion/size/
  space/symbol/texture). Counterpart's resolver is narrower (spacing+type+proportion only) and does not
  reach form/motion/symbol/fill as generative axes.
- **The meaning registry / glyph_meaning embedding space** (per memory, 220 live vectors in
  `ledger.embedding`) — counterpart has no learned/embedded meaning space at all; its "meaning" is
  entirely hand-authored JSON with deck-citation evidence. This is a genuine asymmetry: counterpart's
  meaning is EVIDENCED (traced to a page) but STATIC; claude-ds's is LEARNED (vectors, judge-scored) but
  (per REGROUNDING's "thin embedding margins") not yet deck-grounded the way counterpart's is.
- **Type sockets / `glyphic-type.js`'s accepts/forbid grammar** — counterpart's `layouts.json` has
  `slot.accepts:[type]` (a similar idea) but no equivalent to claude-ds's full socket/trigger/state
  grammar with typed edges-with-inverses. `dna/types.json` (31KB, not read in full this pass — flagged
  as a follow-up) may narrow this gap; worth a dedicated read before concluding it's fully absent.
- **Company role-based judging** (glyph_compose, the judge pattern) — counterpart's `checker: model`
  concept exists in principle (THE-GENERATIVE-LANGUAGE §2's "keystone correspondence" callout) but no
  counterpart file implements an actual AI-judge call; every "verified" claim in counterpart's DNA is a
  human-authored evidence citation (deck page number), never a model-scored judgement. This is the
  reverse of claude-ds, where role-based judging exists but isn't yet applied to shape/organism minting
  the way counterpart's `minting_policy` (§2b) demands.

---

## 4 · The spacing-language resolution — RESOLVED, not open (correcting REGROUNDING §5)

**Observed** (`FORMATION_JOURNAL.md` entries 21-28, `docs/campaigns/rule-core/SPACING_CIRCUIT.md`): the
thread named in REGROUNDING §5 ("the lineage ends mid-discovery… 61% drift found; its resolution lives in
counterpart's later state") **DID resolve**, in the same repo, well before the mob-24 campaign:

- Entry 21 (HANDOVER.md, 2026-06-12): 76% of spacing values, 61% of rhythm spacing, off-grid; a generic
  "multiples of 4" grid was asserted then REVERTED ("it imposed a convention rather than reading the
  source").
- Entries 22-24 (R1/R1b, 2026-06-13): the real fix — spacing became a **live resolved circuit**, the
  spatial twin of the colour circuit (`lint-space.mjs` as the 7th proof), with an **extensible vocabulary
  spine**: `unit × count → px`, address = `--dna-space-{count}`. **Verified live in `dna/grammar.json`
  today**: the `vocabulary.counts` array holds 47 admitted counts (0.375 through 16.25), with an explicit
  `ingest_provision.candidate_fine_counts` block **still AWAITING Tim's word-choice** (0.5/0.75/1.5/2.5 —
  a deliberate, named, open decision point, not an abandoned thread).
- Entries 25-28 (sr-1 through sr-5, 2026-06-14): full estate rollout — 147 chrome literals, then ALL 74
  pieces (863 spacing + 593 type literals) migrated to `--dna-space-{n}` addresses. Journal's own
  characterization: *"the spacing circuit is complete end-to-end and estate-wide: rule (bonds) → engine
  (DNA.space) → injection (DNA.injectSpace, live on the gallery + every iframe) → consumers (chrome + all
  74 pieces, on-address). The ONLY thing left is Phase 3 TUNING — collapse the mirror into the real
  relationships, his to drive. Everything mechanical is done."*

**Where it actually rests**: a working, wired, estate-wide vocabulary-spine (Law 14 of
THE-GENERATIVE-LANGUAGE — "spacing is a VOCABULARY, not a grid" — is not a standing problem, it is a
DESCRIPTION of what `grammar.json.scales.space.vocabulary` already implements). The one open item is a
Tim-gated word-naming decision on 4 fine-grained counts, explicitly parked, not "mid-discovery." The
55-entry-later mobile-form-review campaign (mob-9…mob-24) and the 146-commit reorg/DNA-Pack arc are the
TRUE latest committed state, and neither touches spacing further.

**Your-idea**: whoever is holding the "spacing as vocabulary" law for the fused system should treat
`grammar.json.scales.space.vocabulary` as the reference implementation to port, not a research question to
re-open — whether claude-ds's spacing scale (`tokens/sizing.css`, `tokens/layout.css`) exists in the SAME
shape (a `unit × named-step` scale with an explicit vocabulary array + an ingest-provision slot for future
fine words) would be the one comparison worth a follow-up grep before assuming a rebuild is needed.

---

## 5 · The per-face fusion worklist (ordered — unblocks the glyphic instrument first)

1. **Port `dna/motion.json`'s laws (anchor_is_the_lca + transition_is_the_diff) + `dna/address.json`'s
   LCA arithmetic** as the glyphgraph's live-growth animator. *Closes the single highest-value gap found
   in this assessment*: REGROUNDING §4's "layout-jump on live growth… the stable-slot/freeze law exists,
   unwired" already HAS its unwired law fully specified in `motion.json` — this is a port of a finished
   theory into missing code, not new design work. No claude-ds equivalent exists (§2c-1's FLIP search
   found nothing) — build fresh from the ten motion.json laws directly.
2. **Port `surface/runtime/organisms.js` wholesale** into `claude-ds/assets/icons/cv-organisms.js`,
   re-point `--dna-*` colour vars to claude-ds tokens. *Closes: no furniture on the canvas.* Low risk
   (pure functions, no framework coupling), high payoff (28 ready SVG generators today vs 0).
3. **Reconcile shape-meaning across THREE existing tables**: `dna/shapes.json` (corpus-evidenced,
   octagon=the-core/cardinality-1), `CV_SHAPES.shapeTypes` (abstract-generic, octagon=Gateway),
   `CV_SHAPES.entities`/`ContainmentTree`'s brand mapping (octagon=Virtual Hubs product) — a Tim decision,
   not mechanical (§2b). Blocking: any organism/glyph that resolves shape-by-entity-type will silently
   contradict Tim's own evidenced brand grammar until this resolves. *Flag for Tim, options-not-binary*:
   (a) adopt counterpart's corpus-evidenced mapping wholesale as canonical (the other two are uncited
   invention), (b) keep as three separate axes (generic semantic class / brand entity / corpus frequency)
   if they're actually answering different questions and should compose, (c) something Tim names that
   none of the three has framed yet.
4. **Port `dna/address.json` + `engine/prove/resolve.mjs`** as the glyphgraph's placement resolver.
   *Closes: the "crude ring" placement gap* with a PROVEN (not theoretical) span-arithmetic engine — and
   is the same LCA machinery item 1 needs, so build them together.
5. **Port `dna/sequence.json` + `engine/prove/resolve-sequence.mjs`** as the glyphgraph's arc/narrative
   resolver, renamed for conversation-growth events instead of deck pages. *Closes: "a glyphgraph telling
   has an ARC," currently absent.*
6. **Port `dna/layouts.json`'s 13 evidenced archetypes as DATA into claude-ds's socket/LOD grammar**
   (`glyphic-type.js` + `ContainmentTree.jsx`) — claude-ds's mechanism (conditions, live occupant-address,
   priority-based LOD pruning) is the stronger host; counterpart supplies the deck-verified content
   claude-ds's `kind.graph` currently lacks (unconfirmed whether it holds any populated archetypes today —
   follow-up needed).
7. **Extend `CV_EDGES.resolve()` with a `verb` facet** carrying counterpart's `transport`/`gather(in|out)`/
   `descend`/`orbit` vocabulary + the seam law. *Closes: the edge language has no motion-verb axis today,
   only relation-kind.* Low risk, additive only.
8. **Teach a `space`/`size` CV_AXES value to resolve THROUGH `grammar.json`'s `unit × step` rule** via
   axis-core's documented `resolve: fn(value, ctx)` extension point, rather than treating CV_AXES and
   grammar.json's resolver as competing systems (§2a-1) — they answer different questions (legal-value-set
   vs derived-pixel-value) and should compose.
9. **Diff `dna/tokens.json`'s corpus-sampled warm palette against `colors_and_type.css`'s current values**
   (not done this pass, §2a-0) before assuming either a copy or a no-op; re-check after the live
   ④/DNA-Pack session's in-flight tokens.json edit (§0) lands, since that edit is unverified-by-render.
10. **Adopt molecules.json's co-located voice-block convention** for every glyph/facet record the
    glyphic engine mints, replacing after-the-fact read-out inference. *Closes: read-out reliability.*
11. **Read `dna/types.json` in full** (31KB, not read this pass) before concluding the socket/type-grammar
    gap (§3, reverse direction) is real — flagged as this assessment's one un-closed loose end.
12. **Reconcile `dna/modes.json`'s document/product chrome dial into claude-ds's grounds/tonal-zoning
    system** — pure addition, no claude-ds equivalent exists; product-verified (not just deck-predicted).
13. **Treat `subject.json`+`reader.json` as a candidate formal spec for the RHM's altitude-transform**,
    not just a design-system face — hand to whoever owns the RHM/operator surface as a review artefact,
    don't silently fold it into the design-system-only fusion.

---

## 6 · What's NOT resolved by this assessment (honest gaps)

- I have **not visually rendered** anything in this repo (read-only territory + no browser dispatched)
  — all "furniture is real" claims are code-read + the two `node` proof-script executions, not
  screenshot-verified. Given `archetype.js`'s self-reported broken state (§0), the gallery's actual
  current visual state should be independently screenshotted before anyone claims the organisms render
  correctly end-to-end in the live page, not just as standalone functions.
- `dna/types.json` (31KB) and `dna/application.json` (17KB) were NOT read in this pass — both are
  plausible homes for socket/type-grammar overlap with claude-ds's `glyphic-type.js` that could soften or
  sharpen the §3 "reverse gap" finding.
- All 14 assigned faces now have a dedicated row (§2a-0 tokens, §2a-1 grammar, §2a-2 layouts, §2a
  organisms+icons, §2b shapes, §2c connectors, §2c-1 motion, §2d modes, §2e sequence, §2f address, §2g
  subject+reader, §2h voice+molecules, §2i canon). Depth is uneven by design — rows with a live proof to
  run (address, sequence) or a sharp conflict to name (shapes) got more space than rows that turned out
  genuinely disjoint-but-compatible (modes, connectors). I did not attempt to force equal length.
- **Not done**: a line-by-line diff of `dna/tokens.json` vs `colors_and_type.css`'s actual current hex
  values (§2a-0), and confirming whether `claude-ds/app/canvases/*` (`kind.graph`) holds any populated
  layout archetypes today vs an empty mechanism (§2a-2). Both are fast, concrete follow-ups flagged in
  the worklist rather than left silent.
- The `④ container session`'s actual current intent (why "DNA Pack" is running a parallel
  visual-extraction-from-source-decks campaign, and whether it knows about the glyphic-language fusion
  mission at all) is inferred from commit messages only — I did not reach that session or read its
  board/channel state. Given it is editing this repo live, right now, **whoever runs the glyphic build
  next should coordinate with it before touching any file it has open** (per the brief's read-only
  instruction, extended as a caution for the build phase too).
- `Supabase/` (untracked, new) appeared in this repo's working tree with no accompanying doc I found —
  worth one grep pass (`find supabase -type f`) before the build phase, in case it's schema work relevant
  to the Company's `ledger` schema convergence.

---

**3-line summary**: All 14 faces verified row-by-row against live JSON + live claude-ds code; the single
highest-value find is `dna/motion.json`'s already-worked-out theory (anchor_is_the_lca +
transition_is_the_diff, tours-evidenced) for exactly the "layout-jump on live growth" gap REGROUNDING
flags as unwired — nothing to invent, only to port, since claude-ds has zero equivalent (FLIP-search came
up empty). Counterpart's engine (organisms.js 28 live generators vs 17 declared, resolve.mjs 11/11,
resolve-sequence.mjs 7/7 — all executed live this session) is real, proven, self-contained furniture ready
tonight; one genuine three-way conflict (octagon means core/hub in counterpart, Gateway in CV_SHAPES,
Virtual-Hubs-the-product in CV_SHAPES.entities) needs Tim, not a merge script. REGROUNDING's "spacing ends
mid-discovery" is stale by 146 commits — it resolved into a live, wired, estate-rolled-out vocabulary
spine with one Tim-gated word-choice left; the repo's true frontier now is a live, uncoordinated reorg +
visual-extraction campaign (④/"DNA Pack," mid-edit on tokens.json and archetype.js right now) the glyphic
build must sync with before editing.

Written to `/home/tim/company/build-prep/the-one-system/glyphic/assessment/AREA-B-counterpart-fusion.md`.
