# AREA: render-homes — full first-hand census

> Territory: `assets/icons/*` (excluding cv-meaning.js, cv-edges.js's meaning fields, glyphgraph.js,
> relationships-seed.js — already audited by others per READING-LEDGER) plus `face-index.js` (one
> directory up, but a direct edge-law consumer so read here). Every file below READ IN FULL.
> Grounded on: feedback-glyphic-course-corrections.md · CRITERIA.md (+ AMENDMENTS A1-A5) · ROADMAP.md ·
> ADVISOR-AUDIT.md §4-§8 · READING-LEDGER.md · GUIDE.md "THE CORRECTED LAWS" · SYNTHESIS.md ROUND 7.

---

## §A · File-by-file account (file:line)

**cv-glyphics.js (24.4K, 400 lines) — READ IN FULL.** `window.CV_GLYPHIC`, the ONE composition home.
- `FACETS` (34-65): the facet contract (form/symbol/fill/color/texture/motion/size/depth/outline), each
  declaring its single source + a `means:` doc-string (UI/help text, NOT an interpreted meaning — never
  consulted by the read-out; confirmed by grep, §B).
- `DEFAULTS`/`COLOR_TOKENS`/`FILL_RAMPS`/`DEPTHS` (69-106): system defaults, all token-refs (`var(--…)`),
  no raw hex except `COLOR_TOKENS`'s documented fallback literals (`#5A8A4A` etc., `var(--x, fallback)`
  form — legitimate degrade-with-value, not a second colour system).
- `schema` (117-141): the AI-foundry record shapes for `symbol` and `glyphic` — single source both
  readers (foundry + validator) use.
- `normalize/validate/valuesOf` (154-207): pure structural helpers, delegate value-spaces to `CV_SHAPES`/
  `CV_ICONS`/`CV_AXES`. No meaning logic.
- `_bind` (166-176): the G8b binding thread-point — delegates entirely to `CV_MEANING.resolveBindings`;
  throws loud if a bound spec arrives with `CV_MEANING` unloaded. No parallel binder (confirmed).
- `meaningOf/colorForValue` (214-236): delegate to `CV_MEANING`; `colorForValue` throws loud on an
  unrecognised value rather than emitting a silent literal (line 235) — a real loud-fail, not decorative.
- `compose` (254-313): **the render composition** — binds → normalizes → resolves ring/symbol colour
  (independently, G2.1) → delegates ALL geometry to `CV_SHAPES.markSVG`. Per-part motion (ring vs symbol)
  threaded as class names resolved via the Motion axis (`motionClassFor`, 240-248), never inline CSS.
- `describe` (327-331): read-out entry point, throws if `CV_MEANING` absent — meaning stays out of this file.
- `composeRelation` (339-384): the relational compositor — binds source/target/edge → `CV_EDGES.resolve`
  for kind→facets → `CV_SHAPES.edgeSVG` for geometry → `CV_MEANING.describeRelation` for the sentence.
  Three explicit "thread-through" comments (361, 375-377) document facets `EDGES.resolve` structurally
  drops (`lineColor`, `negate`, `conditions`) and re-attach them by hand from `edgeSpec` — correct, but a
  fragile seam: any future facet added to edge specs must be manually re-threaded here or it silently
  vanishes before the read-out sees it (not yet a violation — flagging as a designed-fragile point).

**cv-shapes.js (26.8K, 386 lines) — READ IN FULL.** `window.CV_SHAPES`, the ONE geometry home.
- `geom` (48-58): 8 true regular n-gons + circle, generated algorithmically (`ngon()`), never hand-plotted
  polygons except the byte-identical CvIcon.jsx fallback (cross-referenced, in sync).
- `shapeTypes` (64-81): **8 shape→type→meaning entries, each carrying a single hardcoded `meaning:`
  sentence** (e.g. octagon: "An output, endpoint or boundary — buyer-facing surfaces and terminals.").
  This is the SAME shape A4 flags for the 12 language symbols. Disposition (verified, not inferred): this
  table is a **documented fallback only** — `CV_GLYPHIC.meaningOf` (cv-glyphics.js:214-223) uses it ONLY
  `if (!M)` (CV_MEANING not loaded); the live path is `CV_MEANING.meaningOf` via `seedFormBindings()`
  (cv-meaning.js:39-47), which pulls `{value: t.type, meaning: t.meaning}` **by reference** from this same
  table into the profile as real field data (feeling-shaped after `seedFields()`'s `seed('form', …)` calls
  at cv-meaning.js:364-372 override it with FIELD data incl. `kindWord`). So: not drift, but a residual
  single-sentence description sitting in the geometry file — worth a comment update in the R4 pass
  clarifying it is fallback-only and will read stale if `shapeTypes.meaning` and the profile's authored
  `form` fields diverge (no sync check today).
- `entities` (86-92): brand-instance→shape compat layer (userPortal/propertyWizard/virtualHubs/vi/generic).
  Legacy but live (CvIcon.jsx's `shape=` prop resolves through `CV_SHAPES.entity`).
- `markSVG` (203-293): **the ONE renderer.** Cascade: `markDefaults` ◀ type/entity treatment ◀ `opts`.
  Handles ring/symbol/fill/texture/depth/outline/motion, all token-sourced. `outline` facet (216-218):
  dashed = potential, none = open — geometry only, no interpretation of WHAT dashed means (that's
  `CV_MEANING`'s `seed('outline', …)`, cv-meaning.js:382-384). Clean separation confirmed.
- `edgeSVG` (312-381): the edge-geometry sibling. Two modes (BOX for inline `composeRelation`, POSITIONED
  for `DiagramSolver`'s glyphgraph layout) sharing ONE facet→dash/colour/routing resolution — no parallel
  geometry. `routing` facet (321, 345-357): straight/right-angled/curved/free, each meaningful per
  `CV_MEANING` (comment at 301-302 cites the seeded phrases) — geometry renders the shape, meaning lives
  elsewhere; confirmed clean.
- No meaning interpretation leaks found anywhere else in this file (grep-verified, §B).

**cv-edges.js (5.2K, 91 lines, most recently touched 13:16 today) — READ IN FULL.** `window.CV_EDGES`.
- `EDGE_KINDS` (33-42): **4 entries — face/documents/higher-order/navigates — each carrying line/direction/
  ink (look facets, legitimate) PLUS a single hardcoded `means:` sentence.** This is a live, unreconciled
  duplicate of meaning that ALSO now exists as proper field data in `cv-meaning.js:431-437` (seeded by
  R1, verified BUILT+VERIFIED per READING-LEDGER). Two homes describe the same four relations: one
  field-shaped (feeling+senses+directed+inverse, the corrected law's shape) and one sentence-shaped (the
  literal thing Tim's correction #2 named as wrong — "one-sentence definitions on symbols = wrong shape,"
  same principle applies to edges). See §D for full analysis — this is the sharpest concrete finding in
  my territory.
- `resolve()` (59-86): confirmed LOUD per the edge law header comment (55-58: "the 2026-07-03 `verbs`
  motion table... was DRIFT... Removed, not re-homed") — no kind throws (61-62), unknown kind not in
  either home throws (73-75). The union-acceptance path (68-77) correctly defers to `CV_MEANING.valuesFor
  ('edge')` for meaning-only kinds — this IS the law working as designed. The `means:` field at line 84
  (`means: k.means || null`) is the ONLY place a caller could still read the OLD sentence-shaped meaning
  instead of the field; nothing in my grep of composeRelation/describeRelation reads `.means` from the
  resolved facets (composeRelation discards it, cv-glyphics.js:355 destructures `kind/type/line/direction/
  ink` off `ef`, never `.means`) — so `.means` is currently a dead/unread field on the resolved object,
  not an active drift vector, but its presence is exactly the debt ADVISOR-AUDIT §5 flag 1 named ("the
  Tim-visible step... has not happened").

**cv-icons.js (52.9K, 574 lines) — READ IN FULL.** `window.CV_ICONS`.
- `.data` (30-208): ~127 SVG bodies, 24×24 grid, stroke=currentColor. The 12 language-family symbols are
  at 438-449 (verbatim list + text in §C below).
- `.aliases`/`.brand` (215-252): semantic⇄brand name resolution + the brand-feature-set flag list.
- `.taxonomy` (263-287): domain facet (14 domains incl. `language`, added 2026-07-03) + kind facet
  (object/action/state/concept) — the ONE classification source `CV_GLYPHIC`/explorer both read.
- `.facets` (291-449): per-symbol `{domain, kind, tags[]}`, PLUS for the 12 language symbols specifically,
  `{name, description}` ALSO inline in the facets record (438-449) — this is a structurally different
  shape from every other symbol's facet entry (which carries only domain/kind/tags). Not itself a
  violation of the edge/meaning law (symbols are INTRINSIC per cv-meaning.js:9-10, "a symbol's denotation
  ... never here") but IS the exact one-sentence-definition shape A4 names for rework into meaning fields.
- `symbolGloss` cross-check (cv-meaning.js:485-489): each of the 12 carries a ONE-WORD gloss (frame→
  'frame', equation→'law', seed→'beginning', corpus→'memory', operator→'sign', …) — this is BY DESIGN
  (comment at cv-meaning.js:482-484: "a small gloss maps an icon id to its plain word") and is NOT what
  A4 targets; the target is the 438-449 `description:` prose, not the gloss word.
- `.byDomain/.byKind/.search/.resolve/.get/.svg/.markup` (453-518): pure query/render helpers, clean.
- `.add`/`._persist`/`._loadPersisted` (530-573): the AI-foundry write path — validates via
  `CV_GLYPHIC.validateSymbol` when present, writes into `.data`+`.facets` (the SAME single sources every
  reader uses — confirmed no second list created for authored symbols).

**icon-paths.js (32.2K, 235 lines) — structure read + spot-checks (mostly path data, confirmed).**
Self-documents as **DEPRECATED at line 2**: "DO NOT EXTEND. The single home for icons is `cv-icons.js`
... This file... is a legacy parallel list kept only so older consumers don't break; migrate them to
CvIcon and delete this." Populates `window.CONCEPTV_ICONS` (a flat `{set, cat, body}` map, ~90 entries,
scanned start-to-end — no hidden non-icon logic, no meaning fields, pure path strings as the header
promises). Only consumer found: `system/build-system-map.js` (a self-description generator, not a
render path) and its own file. Honest dead weight, not drift — the file names its own disposition
correctly; nothing here contradicts that self-label.

**cv-organisms.js (81.9K, 910 lines) — READ IN FULL, first-hand.** See §B verdict below (the flagged item).

**cv-vi-glyph.js (940B, 5 lines) — READ IN FULL.** `window.CV_VI_GLYPH`, a single traced-path record
(`{viewBox, w, h, path}`) for the ConceptV "Vi" wordmark. Auto-traced from a PNG, consumed by
`cv-shapes.js`'s `viWordmark()` (cv-shapes.js:182-187) for the `vi` brand entity. Clean, single-purpose,
no meaning content, correctly the one home for this one glyph.

**glyph-arc-seed.json (5.97K) — read + consumer-traced (not `.js` — the brief named `.js`, only `.json`
exists; confirmed via `ls`, not a missing file, just a naming mismatch in the brief).** Consumed by
`core/cv-arc.js` (comment reference, cv-arc.js:7) and `_demo/verify_arc.js:6` (`require(...)`, 7/7 passing
per READING-LEDGER). Legitimately wired — not an island.

**face-index.js (one directory up: `/home/tim/company/design/claude-ds/face-index.js`, NOT under
`assets/icons/` — the brief's path was off by one directory; read anyway since it is a direct, live
consumer of the edge law).** Header: "GENERATED: window.CV_FACES from the live page-face bindings."
Loaded by `app/index.html:152`. Confirmed (via `_demo/verify_glyph.js:18-21`) to instantiate real
`{"kind":"face"}` edge records — this is the live surface ADVISOR-AUDIT §4 already traced as a safe
caller (no kind-less edge). Still speaking the OLD kind name post-R1; unaffected functionally (R1 kept
`face` as a valid kind with a declared inverse) but it is one of the concrete "Tim-visible" surfaces named
in §5 flag 1 that nothing has yet routed in front of Tim.

---

## §B · UNIFICATION findings + fold-in designs

**B1 — meaning stays out of geometry (the law holds).** Grep-verified across cv-shapes.js and
cv-glyphics.js: every `meaning`/`means` occurrence is either (a) a doc-string never read by the render
path, (b) a delegation to `CV_MEANING` with a loud-fail guard, or (c) the one documented fallback
(`shapeTypes.meaning`, used only when `CV_MEANING` is absent). No place resolves an interpreted meaning
inline and bakes it into an SVG attribute. The render pipeline is genuinely: **facets → CV_SHAPES/CV_ICONS
(geometry) in parallel with facets → CV_MEANING (meaning)**, joined only at `describe`/`describeRelation`
call sites, never inside `compose`/`markSVG`/`edgeSVG` themselves. This is the one clean structural
finding worth stating plainly: the render-homes territory does NOT violate the "meaning is a field,
geometry is separate" law anywhere in its own code.

**B2 — the edge-kind duplicate (cv-edges.js `EDGE_KINDS.means` vs cv-meaning.js field data) should
fold into ONE home.** Concretely: `cv-edges.js`'s `means:` strings (34-41) should be **deleted**, not
migrated — the facts they carry (declared inverse, feeling, senses) already live correctly in
`cv-meaning.js:431-437` post-R1. `CV_EDGES.resolve()`'s return object (78-85) should stop returning
`means` at all (or, if a look-registry-side gloss is still wanted for the `_demo`/specimen pages, it
should read `CV_MEANING.field('edge', spec.kind).feeling` live rather than hold its own copy — same
pattern `colorForValue` already uses for colour). This closes the exact gap ADVISOR-AUDIT §5 flag 1
described as "unbooked debt": the sentence-shaped description of `face`/`documents` doesn't just risk
drifting from the field-shaped one, it ALREADY HAS a second, never-synced copy sitting live in the
registry callers may still read.

**B3 — the 12 language symbols' `description:` (cv-icons.js:438-449) is the direct R4 target, but the
correct fold-in keeps the taxonomy fact split from the meaning fact.** `domain/kind/tags` (the intrinsic
classification) legitimately stay in `CV_ICONS.facets` — the symbol's SEARCHABLE identity, unrelated to
the meaning-field law (per cv-meaning.js's own architecture decision, symbols are excluded from
`MEANING_FACETS` on purpose). Only `description:` (the one-sentence prose) is the violation shape; it
should retire to depiction-for-search caption (A4's own wording) OR promote into a genuine
`CV_MEANING`-authored field if these 12 concepts are meant to participate in the read-out the way `form`/
`edge` values do (unclear from what exists today — no relation/read-out path currently touches the
`language` domain's symbols; they are pure icon-library entries used for depiction, not yet wired into
transglyphing). Recommend surfacing this ambiguity to Tim rather than silently picking one (see §E).

**B4 — cv-organisms.js should either be wired or removed, not left as a silent island** (full case in
the verdict below, §B-verdict). If any of its 28 generators are wanted, the ones that overlap the
language system's own responsibility (`graph()`'s node/edge renderer, `icon()`'s parallel icon dict)
should NOT be wired as-is — they would create the exact "second relation model" / "second icon home"
CV_EDGES's own header (22-27) explicitly warns against. The organisms that are pure content-furniture
with no overlap (`cascade`, `consequencesBox`, `phaseStrip`, `testimonial`, `donut`, `bars`,
`fileStack`, `planThumbnail`, etc.) are safe to wire into a real page if wanted — they don't touch the
glyphic language at all.

### cv-organisms.js — THE VERDICT
**Observed, not inferred:** zero `<script src=".../cv-organisms.js">` tags exist anywhere in claude-ds
(grep across every `.html`); zero `.js`/`.jsx` file references `CV_ORGANISMS` or `DNA.org` other than
cv-organisms.js's own closing assignment (`global.DNA.org = {...}`, line 909). It defines its OWN global
namespace (`window.DNA`), completely disjoint from `CV_GLYPHIC`/`CV_SHAPES`/`CV_EDGES`/`CV_ICONS`/
`CV_MEANING`/`CV_REGISTRY`/`CV_AI` — the seven registries every other file in the census participates in.
It carries its own icon dictionary (`P`, lines 39-50, 10 entries) parallel to `CV_ICONS.data`; its own
node/edge graph renderer (`graph()`, 274-424) with hand-rolled arrowhead math, colour resolution, and
state-sockets, parallel to `CV_SHAPES.edgeSVG` + `CV_GLYPHIC.composeRelation`; and its own token-name
translation table (the file-header comment's counterpart→claude-ds palette map) — a THIRD token-naming
layer alongside the real `colors_and_type.css` tokens and the `COLOR_TOKENS` map in cv-glyphics.js.

This is a genuine, confirmed **island** — ported by-copy (its own header says so: "ported-from:
counterpart/design@20a5ac8... port-by-COPY... ONE change class: token re-pointing") into a namespace
nothing in the language system reaches into, with internal machinery that duplicates rather than reuses
the one-icon-home / one-edge-geometry-home laws this whole census otherwise confirms are holding. It is
"KEPT AS MACHINERY" per SYNTHESIS.md ROUND 7 (7.2) and CRITERIA A4 ("cv-organisms.js... KEEP as
machinery, re-verify their disposition as A3/the build consumes them") — so its presence is not
unauthorized, but "kept as machinery" has not yet meant "wired to anything," and nothing in the 280+ file
census (per READING-LEDGER) currently imports it. Verdict: **built, unconsumed, and structurally
parallel to homes this system has already unified elsewhere** — the single largest unification gap in
this territory by file size (81.9K of code with zero live callers).

---

## §C · Disconnected/unused (evidence)

1. **cv-organisms.js — entirely unconsumed** (see verdict above). 81.9K, 28 functions, zero callers.
2. **icon-paths.js + ConceptVIcon.jsx — self-labeled deprecated, consumed only by each other + a
   self-description generator** (`system/build-system-map.js`). Not drift (honestly marked), but dead
   weight sitting in the live directory rather than an `_archive/`.
3. **`CV_EDGES` entries' `.means` field** (cv-edges.js:84) — resolved into every `edgeSVG`/`composeRelation`
   call's `ef` object but never read downstream (confirmed: `composeRelation` destructures `kind/type/
   line/direction/ink` off `ef`, cv-glyphics.js:355, never `.means`). Dead data flowing through a live
   path — cheap to remove per §B2.
4. **`kind.graph`'s `layout` valueSlot enum** `[force,tree,radial,flow,grid]` (per READING-LEDGER's
   kinds-type.js note, cross-referenced, not re-verified first-hand here since kinds-type.js is outside
   my territory) is declared separately from what DiagramSolver actually implements — flagged already by
   the other reader; I confirm from this side that `CV_SHAPES`/`CV_GLYPHIC` carry no `layout` concept at
   all, so this drift is entirely on the registry/solver side, not in render-homes.

---

## §D · Corrections to plan/ledger/audit claims

1. **ADVISOR-AUDIT §5 flag 1 ("face/documents were law-conformed, not dispositioned") is CONFIRMED STILL
   OPEN from this side, with one addition the audit didn't have:** the audit traced cv-meaning.js's side
   (the field data) and the live HTML surfaces (face-index.js, the-whole-thing.html) still speaking
   `kind:'face'`. This census adds the concrete second-home evidence: `cv-edges.js`'s `EDGE_KINDS` table
   (33-42) is not just an old naming convention living on in HTML data — it is STILL A LIVE, LOADED,
   RESOLVED registry entry (loaded in `app/index.html`, `system/the-whole-thing.html`,
   `system/glyphgraph-generator.html` via `<script src="cv-edges.js">`) carrying its OWN sentence-shaped
   `means:` for the same four kinds R1 already re-expressed as fields. This is not dormant history; it
   resolves on every `CV_EDGES.resolve()` call today.
2. **A4's "12 minted 'language'-family symbols" claim is verified verbatim** (§C list matches exactly:
   frame, block, equation, window, seed, weave, judge, ring, corpus, room, territory, operator — cv-icons.js
   438-449). No 13th or missing entry.
3. **The READING-LEDGER's "STILL TO READ" queue item "cv-glyphics.js, cv-shapes.js, cv-edges.js full"
   is now CLOSED** by this census — all three read in full, first-hand, findings above.
4. **Minor brief-path correction:** the team-lead's brief named `glyph-arc-seed.js` and implied
   `face-index.js` lives under `assets/icons/`; only `glyph-arc-seed.json` exists (no `.js` sibling), and
   `face-index.js` lives at the claude-ds root, one directory above `assets/icons/`. Both read anyway;
   no content implication, just a path note for whoever maintains the ledger next.
5. **No evidence found that `MEANING_FACETS` excludes `outline`/`line`/`edge`/`direction`/`lineColor`/
   `size` at runtime** — I initially suspected a gap (the array literal at cv-meaning.js:34 omits them)
   but cv-meaning.js:339-341 pushes all six into `MEANING_FACETS` immediately after, before `seedFields()`
   runs. Recording this so no future reader re-derives the same false alarm from the literal alone.

---

## §E · Inputs for R4 (the 12 symbols) and R3 (render side of placement)

**For R4 (12 symbols → meaning fields):**
- The exact rework target is `cv-icons.js:438-449`'s `description:` values, verbatim (quoting for direct
  use): frame — "A way of seeing — rules of projection over data that never changes; every viewer is one,
  and is a node in the space it views." · block — "The atomic composable unit — typed, addressed,
  nestable; every boundary the root of its own cascade." · equation — "A law that computes — a value
  derived from relations, never placed by hand." · window — "The visible half of the world — the
  coordinate space made touchable: see, point, direct." · seed — "The start that carries the whole —
  every telling grows root-first from it, complete at every stage." · weave — "Descent and traverse woven
  — the multiaxial reading; any forward walk through the lattice is a valid telling." · judge — "The one
  that weighs — extraction proposes in parallel, judgment composes the one answer." · ring — "The
  boundary that carries identity through change — interior change is state, boundary change is
  becoming." · corpus — "The remembered whole — everything spoken, kept addressed; the transcripts are
  the root of all data." · room — "A place of work — a session, a bench, a gallery; rooms are places and
  the camera slides between them." · territory — "A subject around its origin — soft-edged sectors
  radial about a centre; the cut and the route make a telling of it." · operator — "A universal sign — a
  relation whose meaning arrives free because everyone already holds it."
- Each already has a one-word gloss in `cv-meaning.js:487-489` (frame/block/law/window/beginning/weave/
  judge/ring/memory/room/territory/sign) that should likely SURVIVE as the gloss (it's the right shape —
  a plain word, not a sentence) while the prose above becomes the FIELD (feeling + senses) IF these
  symbols are meant to enter the read-out grammar. Open question for Tim/R4 (not mine to decide): are
  these 12 meant to be relation-bearing / read-out participants (like `form` values), or are they
  intentionally pure library/depiction symbols whose "meaning" is documentation, not language? Nothing
  in the current render pipeline reads their description at all (confirmed: `describe`/`readGraph`/
  `referent` never touch `CV_ICONS.facets[x].description` for any symbol, language-family or otherwise)
  — so today they are inert prose, which is itself consistent with A4's "demote to depiction-for-search
  caption" instruction. If that's the final call, the fix is small: rename `description` → something
  read as caption-only, keep `name`+`tags`, done. If Tim wants them to speak, that's new read-out wiring,
  not just a field-reshape.
- The `--ramp-*` ordinal axis piece of A4 is outside this territory (SYSTEM-GAPS.md, unread by me,
  outside assets/icons/) — no findings to add there.

**For R3 (render side of placement):**
- `cv-shapes.js`'s `edgeSVG` POSITIONED mode (336-366) is the direct consumer R3 will touch: it takes
  `opts.from`/`opts.to` as literal `{x,y}` coordinates with `gapFrom`/`gapTo` — this is ALREADY relative
  to whatever coordinate space the caller (`DiagramSolver`) hands it; the geometry function itself has NO
  absolute-pixel assumption baked in (it computes unit vectors and shortens from whatever two points it's
  given). This means R3's redo of placement (cv-address spans → relative resolution) should be able to
  feed `edgeSVG` unchanged — the geometry layer is already agnostic to WHERE the coordinates came from.
  The routing shapes (right-angled/curved/free, 345-357) are also coordinate-space-agnostic. **No render-
  homes file needs to change for the A3/R3 placement redo** — the seam is entirely upstream in
  DiagramSolver/cv-address, confirming ADVISOR-AUDIT §6's ranked risk list correctly scoped R3 outside
  this territory.
- One consumer-side note for whoever does R3: `CV_GLYPHIC.composeRelation`'s BOX mode (the inline
  node→edge→node glyphic, cv-glyphics.js:339-384) does NOT take positioned coordinates at all — it always
  self-lays a little inline SVG. If R3's relative-placement work ever wants composeRelation's OUTPUT
  placed relatively (not just DiagramSolver's POSITIONED edges), that is new wiring, not something R3
  gets for free from the edge-geometry work.

---

## §F · Proposed plan-file edits (tentative)

1. **CRITERIA.md A2** — add a concrete line item: "cv-edges.js `EDGE_KINDS[].means` (33-42) still
   duplicates the field-shaped meaning now in cv-meaning.js:431-437 for the same 4 kinds; remove `means`
   from `EDGE_KINDS` + `CV_EDGES.resolve()`'s return, or make it a live read of
   `CV_MEANING.field('edge',id).feeling` — closes the last unbooked half of R1's edge-law migration."
2. **READING-LEDGER.md** — mark `cv-glyphics.js, cv-shapes.js, cv-edges.js full` (queue item 4) DONE,
   with a pointer to this census file for the detail.
3. **ROADMAP.md PHASE RECONCILE** — R1 could gain a sub-bullet: "R1b · cv-edges.js means-field removal
   (the duplicate this census found) — small, mechanical, no meaning change, just the second home
   deleted."
4. **A4** — the census suggests splitting A4's "12 minted symbols → meaning FIELDS" into two possible
   outcomes depending on a Tim call not yet made (participant-in-read-out vs depiction-only); recommend
   the amendment text note this fork explicitly rather than assume the "meaning FIELDS" outcome, since
   nothing today wires these symbols into any read-out path (§E).
5. **A4 (cv-organisms.js line)** — currently reads "KEEP as machinery, re-verify their disposition."
   This census's verdict (zero consumers, structurally parallel to unified homes) suggests the
   amendment should be sharpened to name the actual choice: wire the non-overlapping furniture
   generators into a real page, OR explicitly retire the overlapping ones (icon dict, graph renderer)
   before anything depends on them and calcifies the duplicate.

All five are tentative — proposals for whoever owns plan-file edits to confirm, not applied by me
(read-only on sources per my brief).
