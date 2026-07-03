# READING LEDGER — the complete first-hand read (started 2026-07-03, after Tim's correction)

> Purpose: the durable record of the full read-through Tim mandated ("complete knowledge before
> acting"). Every entry = a file actually read/run first-hand this pass, with what it changed in my
> picture. This corrects the false claims in assessment/SYNTHESIS.md where noted. Grows until the
> census is covered. Census: 280+ files listed 2026-07-03 (claude-ds full tree).

## Ground truth from RUNNING all 13 verifiers (2026-07-03)
- verify_g0 — PASS: dictionary-as-data round-trips (17.8K JSON incl runtime-authored 'contradicts');
  author API loud-fails proven. G0 fully real.
- verify_language — PASS: read-out composes; **the line facet ALREADY holds right-angled/curved/free
  with phrases ('routes to')** — edges are folded into the meaning system. My claim that edge facets
  weren't wired was partly stale.
- verify_g2 — **35/35 PASS**: size + lineColor ARE meaning-faceted (size has a meaning-type).
  → my claim "G2.3 size-as-comparison not built" was WRONG.
- verify_g2_4 — 22/22: conditionals + negation solid; absent-negate reads plain (honest).
- verify_g3 — **25/25**: relationship Types LIVE in CV_REGISTRY; validator REUSES accepts+CV_COND;
  meaning single-sourced. → my claim G3.2 was in doubt: WRONG, it's done.
- verify_g8b — **32/32 PASS**: data-bound glyphics BUILT — same relation spec + different data =
  different sentence; source unmutated. → my claim "G8b entirely not done" was WRONG.
- verify_g9 — 9/9: the reverse parser with HONEST STARTER GAPS (subordination + conditional throw
  naming themselves "STARTER GAP" — never a wrong parse).
- verify_g10 — **30/30 PASS**: multi-target transglyphing BUILT (a 'triples' target works; unbuilt
  'code' target throws honestly). → my claim "G10 not done" was WRONG.
- verify_readgraph — referent voice proven; the kind-vs-instance SOFT CELL (square+house→"this home",
  circle+house→"the home"); FLAGGED IN THE FILE: verb-ish relations (navigates/becomes) need
  MOOD-FOLDING — a known open item I didn't know.
- verify_g11 — **19/21: MY W2 EDIT BROKE THE VERIFIED CONTRACT.** The 2 failures are boundary
  assertions my changes moved without re-verification: (a) deep-chain compression boundary (my fixed
  116 row-pitch removed the documented ≥6-rank compression); (b) honest-overflow (my brick-wrap keeps
  slots in-frame where the contract asserted off-edge overflow). Behaviour arguably changed for the
  better in isolation, but VERIFIED WORK WAS OVERWRITTEN UNVERIFIED — and the whole placement is to be
  redone under the relative laws anyway (Tim: absolute rule on a relative system).
- verify_address (mine, 13/13) + verify_arc (mine, 7/7) — pass; their DISPOSITION rides the redo.

## app/registry/relationships-seed.js — READ IN FULL (the file I told Tim about without reading)
- Seeds `relationship.<kind>` Types into CV_REGISTRY, **reconciling LIVE at seed time** against the
  two real homes: CV_EDGES.ids() + CV_MEANING.valuesFor('edge'). No meanings re-authored — mirrored
  (REUSE upheld). Source/target sockets accept ['glyphic','atom','block'].
- CONSEQUENCE I didn't know: **my 5 seeded operators auto-became relationship Types** (the union reads
  the meaning profile live). My cv-edges `verbs` table did NOT flow in (verbs ≠ kinds; .ids() returns
  kinds only) — the verbs are fully inert, nowhere consumed.
- `?` and `!` documented as ILLOCUTIONARY (mood on a clause, not binary relations) — correctly not
  seeded. G1.1's "? !" criterion needs re-reading in this light: they belong as MOOD/force markers,
  not edge Types.
- **The gap vs Tim's law:** no `directed`/`inverse` fields on the Types. The Company's relation_types
  records carry {id, directed, inverse, near, far}. G6.2 = align these (the equal-and-opposite law is
  already encoded Company-side; the design-side Types must carry/mirror it).
- 'documents' (June-flagged as invented) flows into the Types via the CV_EDGES union — cleaning the
  HOME cleans the Types; don't patch the seed.

## The census surprises (files whose existence alone corrected me)
- _demo/ holds verifiers for G2, G2.4, G3, G8b, G9, G10, readGraph, glyph — the build went FAR past
  where my assessment claimed. The assessment (AREA docs + my SYNTHESIS) UNDERSTATES the language
  build badly; treat its "not done" claims as unreliable until re-verified here.
- system/glyphic-system.html (73.5K) — unread; likely the full system page.
- analysis/FINDINGS-LOG.md (215K, newest-first) — the running build memory; unread by me.
- analysis/{PROGRESS, SYSTEM-GAPS, HANDOFF, GUIDE, README, DESIGN-LANGUAGE} — unread by me.
- app/registry/{types-seed(22K), types-core(16K), conditions, kinds-type, glyphic-type} — partially
  read only.
- assets/icons/cv-meaning.js is 78K — I have read fragments only.

## STILL TO READ (the queue, in order)
1. assets/icons/glyphgraph.js (the validator) — next.
2. build-prep/the-one-system/glyphic/{GUIDE.md, ROADMAP.md} (the remaining plan docs).
3. cv-meaning.js FULL (chunked). 4. cv-glyphics.js, cv-shapes.js, cv-edges.js full.
5. analysis/FINDINGS-LOG.md (newest slices first), PROGRESS.md, SYSTEM-GAPS.md, HANDOFF.md,
   DESIGN-LANGUAGE.md, GUIDE.md, README.md.
6. app/registry/{glyphic-type, kinds-type, conditions, types-core, types-seed} full.
7. core/{DiagramSolver full, RenderType, ContainmentTree, archetype-catalog}. 8. system pages
   (glyphic-system, language, system-map+build-system-map). 9. app/ai/* full. 10. the rest of the census.

## assets/icons/glyphgraph.js — READ IN FULL
validateGlyphgraph exactly as G3.3 specifies: (1) structure (typed edge, endpoints resolve, unique ids),
(2) kind → relationship.<kind> Type, (3) domain/range via CV_REGISTRY.accepts on source/target sockets
(node classification DERIVED, default ['glyphic']), (4) edge-instance conditions via CV_COND (distinct
from socket conditions). Collect-then-throw naming every violation; lazy registry resolution
(load-order-proof); checkGlyphgraph = the non-throwing editor face.

## build-prep glyphic/GUIDE.md — READ IN FULL (the how)
North-stars: meaning-is-a-field · sentence-is-a-projection (octagon oracle = the BROKEN test, not a
gate) · single glyph = NOUN PHRASE never a sentence · form ⟂ fill (form=what-kind, fill=mode-of-
reference; never let form do definiteness) · don't invent meanings · one mechanism (variable resolution
— meaning/value/identity same shape) · TWO READ-OUTS NEVER CONFLATED (describe=facet inspector,
transglyph=the language) · live dual-authoring IS the point. G4's exact readGraph sequence (focus →
referent [determiner from fill-mode, kind from form, thing from gloss] → clause per edge [mood from
line, verb from relation] → coordination/subordination/conditional → assemble). "DO offer 2–3 candidate
readings where the field is ambiguous." G1: operators act as edges OR OPERATOR-NODES. Held-for-later
(v1): reverse parser, force-directed, multi-target — ALL SINCE BUILT (G9/G10 verifiers prove it).

## build-prep glyphic/ROADMAP.md — READ IN FULL (the sequencing)
DONE list confirms: engine incl reverse parser + multi-target + data-binding + glyphgraph render;
generator B+C; A designed. PHASE REMAINING (the real open list): canvas/renderer decision ·
incremental-stable placer ("C's pinning is the seed; THE SPATIAL-THEOREM PLACEMENT MODES" — plural,
relative!) · data-binding/storage persistence (project://, Supabase Realtime, domain schema) · G8
self-describing (guides+pages+authoring panel) · zones · read-out live-tuning · reverse+multi-target
polish · the 3 gate-detectors.

## analysis/PROGRESS.md — READ (the corpus tracker)
12/12 source folders analysed (the design-DNA analysis of Tim's real decks — zoning ladder, gold ramp,
LOD axis, register). Build sessions: token recalibration → generative core → archetype/template layer →
UNIFICATION W1-W2 (RenderType bridge + archetype-catalog single source; W3-W5 welds documented open).

## analysis/FINDINGS-LOG.md — TOP SLICES READ (82→79; newest-first log, 215K total)
- Slice 82 (G10): READGRAPH_TARGETS = realiser-factory registry (extend-by-registration); english
  realiser byte-identical to prior; triples realiser structural (never calls referent — English cannot
  leak); absent target→english, present-unknown→throws; 'code' target = registered-when-built. 30/0.
- Slice 81 (G2.4): negation single-homed in the dictionary (.negates flag, NEVER string-match);
  relationVerb folds negation; conditionPhrase reuses CV_COND.normalize; the not-operator suppresses its
  relation word (no double-not). PLUS the G8b resolveSet bug fixed en route (resolve-into-scope law).
- Slice 80 (G5): edgeSVG gained POSITIONED mode (one renderer two framings) + routing facet
  (straight/right-angled/curved/free); glyphGraphView renders FULL glyphics; EDGE LABELS OFF BY DEFAULT
  (title = 2-node readGraph clause — the pattern I later "invented" for the-whole-thing was established
  HERE); labels-mode chip = the relation's MEANING never the raw id. FLAGGED for Tim (still open):
  mixed routing taste; curved-edge arrowhead angle; SENTENCE-COVERAGE (the dropped file-clause — my W2
  per-edge-join change sits exactly on this flagged live-tuning surface, arguably legitimate).
- Slice 79 (G3): relationships-seed (9 Types, union reconciled live) + glyphgraph.js validator, 25/25.
STILL TO READ: slices 78 and below (G8b, G9, generator, foundry eras); cv-meaning.js full; SYSTEM-GAPS;
HANDOFF; DESIGN-LANGUAGE; registry files full; core files full; system pages.

## cv-meaning.js — READ (full structure + all major sections; 1271 lines)
- **readGraph (892-959):** target dispatch (absent→english, unknown→loud) · focus = explicit, else a
  source-never-a-target, else first · ONE traversal for every target (walk w/ visited+depth guards,
  lone-conditional FRONT-HOIST, coordination via T.coordinate, subordination via walkAsObject) — only
  the REALISER differs. READGRAPH_TARGETS = extend-by-registration realiser factories; triples NEVER
  calls referent (English cannot leak or the meaning-is-the-graph proof is fake).
- **G8b bindings (961-1008):** a binding IS an encoding set ({bind, map, kind, fallback, stops,
  domain}); resolveBindings is PURE (fresh spec per resolve = the liveness); the appearance domain is
  FACET-VALUES (not hex) — which is exactly what keeps the meaning field intact so the read-out lives
  (bound → 'warning' → amber AND "caution"). ONE resolver (encodings.resolveSet), no parallel binder.
- **G9 parse (1044-1268):** a deterministic INVERSION of the forward grammar reading the SAME single
  sources AT PARSE TIME (gloss inverse, edge feelings, mood phrases — all from the active profile;
  authored words parse for free = G0.5 in both directions). LOSSY-FORWARD documented: the contract is
  the TEXT round-trip, canonical inverses chosen per lossy case. Starter gaps throw NAMING THEMSELVES.
- **★ THE FINDING THAT LANDS ON TIM'S CORRECTION (lines 663-691):**
  `REFERENT_KIND = { octagon:'gateway', hex:'system', pentagon:'feature', heptagon:'special type' }`
  and `REFERENT_OP = { triangle:'action on', diamond:'use of' }` and the DETERMINER LADDER
  ('a possible'/'the'/'this'/'a') are **MODULE-PRIVATE CONSTS — hardcoded, unreachable by the author
  API.** This violates the engine's OWN G0.1 law ("the seed is profile data, not fixed literals the
  author API can't reach"). When Tim says "an octagon does not mean gateway, an AI just wrote that
  there once" — the word 'gateway' is literally a const at cv-meaning.js:664 that live authoring cannot
  correct. The form FIELDS are in the profile; the referent WORDS are not. parse() explicitly documents
  depending on these consts being module-private (its stated reason for living in the same IIFE).
  → The conforming fix (the system's own shape, cf. line fields carrying `phrase`): the form fields
  carry their referent-words as FIELD DATA (e.g. a kindWord/opWord attribute set via setField), the
  determiner ladder becomes fill/outline field data, referent() + parse() read them from the active
  profile. Then "octagon ≠ gateway" is a live authoring correction, not a code edit — exactly the
  architecture Tim mandated.
- **relationVerb/isNegated/conditionPhrase (709-778):** negation single-homed (.negates, never
  string-match); conditionPhrase reuses CV_COND.normalize; relation word survives explicit negate,
  suppressed when the kind IS the negator.

## cv-edges.js — READ IN FULL
Header documents its design intent: "the RELATIONAL sibling of CV_SHAPES.shapeTypes... the ONE home for
edge kinds + their facets"; an edge is faceted like a node (line=material/mood-ish, direction, ink);
geometry in CV_SHAPES.edgeSVG; a CONVERGENCE note: sockets=structure, edge-kinds=the relation's type+look,
"they compose; this is not a second relation model". CONTENT: 4 kinds — 'face' encodes the PAGE-FACE
relation ("this thing has a viewable PAGE — the page is the visible face/projection of the source", i.e.
the design-faces-era concept, not arbitrary), 'documents' (guide-for — June-flagged invented), 'higher-
order', 'navigates'. resolve() SOFT-DEFAULTS kind→'face' when absent (weaker than loud). My W1 verbs
table sits here, inert. DISPOSITION (for the plan update, Tim-visible): under the equal-and-opposite law
edge kinds must become directional verbs w/ declared inverses (align with relation_types' shape);
current kinds re-expressed (face→ has-face/face-of pair?) or retired; the verbs table re-homed or dropped.

## glyphic-type.js — READ IN FULL
The reference universal component: parts (ring/symbol/fill — each a registered Type) + parent glyphic
Type. **valueSlots are AXIS SUBSCRIPTIONS** (sub(axisId,{groups,default}) — default resolved LIVE from
CV_AXES, vocabulary never copied; editors read CV_AXES.candidates(subscription)). Whole-unit slots:
size/motion/depth/value (value = allocated state driving colour via the active meaning profile).
Sockets carry address-to-occupant. Conditions as strings ("texture requires fill != none"; "symbol
meaning is intrinsic (never profile-governed)"). THE pattern for any "no hand-enumerated lists" work.

## kinds-type.js — READ IN FULL
kind.graph: nodes socket accepts [glyphic,atom,block]; edges socket accepts [relationship]; runtime
{kind:'engine', key:'DiagramSolver'}; layout valueSlot enum [force,tree,radial,flow,grid] (declared but
solver implements its own set — a small declaration/implementation drift). panel.composition-menu = the
candidatesForSocket demonstration (a socket accepting a classification shows the matching library with
zero bespoke wiring). kind.slide-system points at core/Slide.

---

## BUILD LOG — PHASE RECONCILE (from the updated plans, 2026-07-03)

### R1 · THE EDGE LAW — BUILT + VERIFIED (commit 28e1a94d)
- Meaning fields: every edge kind declares `directed`; every directed one declares `inverse`
  (verb-pair, declared once). navigates + mirrors + equals/not/and = symmetric (directed:false).
  `documents` gained its missing meaning field (was UNREADABLE — field('edge','documents') threw).
- readGraph: focus tells INCOMING edges via T.clauseInverse — english swaps words, triples keep
  `(kind src focus)` canonical (proof the inverse lives in the realiser, not the graph). Default
  focus = pure source → all existing reads byte-identical (regression green).
- parse: inverse feelings join REL with swap:true → the inverse saying stores the canonical edge.
- Types: {directed, inverse} mirrored via metaFor; **types-core normalize was silently DROPPING
  relationKind/operatorSymbol/negates too** (the dropped-field trap) — now carried.
- cv-edges: verbs table REMOVED (disposition: drift, nothing consumed it — not re-homed);
  resolve() loud (no kind → throw; unknown kind → throw; meaning-only kinds accepted via the union).
- verify_edgelaw.js 15/15 (falsify-first: 2/15 pre-build). All other harnesses green; g11 19/21
  unchanged (pre-existing W2 breakage = R3).
- FLAGS for live-tune (A5): 'part of' is a HOMONYM (higher-order + part-of share the feeling —
  parse picks one); "is becomes"-style mood+feeling seams; all inverse wordings are starter.
- describeRelation (the 2-node inspector read) does not yet realise inverses — readGraph is the
  language home; noted, in scope when the inspector read is next touched.

### R2 · REFERENT WORDS → PROFILE DATA — BUILT + VERIFIED (commit follows R1)
- REFERENT_KIND/OP consts + determiner ladder deleted; words now FIELD DATA (form.kindWord/
  opWord; fill/outline.determiner). referent() + parse() read the SAME fields — authoring a
  word moves both directions live (proven: octagon 'gateway'→'portal' changes read-out AND
  parse; the old word throws loud, no ghost vocabulary; a new determiner parses for free).
- field() DROPPED-FIELD CLASS dissolved (design-for-the-class): raw record spread first —
  any authored extra reaches every reader; no more whitelist-normalizer silent drops.
- Stricter (deliberate): a present-unknown OUTLINE value now throws in referent (was
  unvalidated for non-dashed values) — the trichotomy law now uniform across facets.
- verify_referent_data 12/12 (falsify-first 3/12 pre-build). All 14 harnesses green.

### CORRECTION (2026-07-03, from the census team's first verified handoffs)
- **My queue note was WRONG**: FINDINGS-LOG has NO slices for the stable-slot/G8b/G9/generator builds —
  the log jumps Slice 79 → 78 (language-era → System Map); "stable-slot"/"pinning"/"g11" = zero hits
  (verified by full-range read + grep). ADVISOR-AUDIT §6.1 inherited the same false premise. The actual
  placement-rationale record: verify_g11.js itself, SYNTHESIS Round 6, REGROUNDING.md, + two drift-era
  W-loop files (AREA-21-spatial-proportion-zones, AREA-D-canvas-spatial — only record, unreliable).
  THE GAP IS ITSELF A FINDING: those builds never wrote their slices (discipline breach to book).
- **Early handoff headlines from the completed history-deep read** (file landing as census/AREA-history-deep.md):
  --ramp-1..4 tokens ALREADY EXIST (colors_and_type.css:76-79; A4's hexes are ramp-2..4 — point, don't
  re-mint) · A4 internal collision: symbols are Tim's intrinsic exception (valuesFor('symbol') throws) —
  meaning-fields for the 12 symbols belong on CV_ICONS records, not the profile · octagon='Gateway'
  provenance = cv-shapes.js:79 shapeTypes (a pre-R2 fixed-meaning home CV_MEANING still seeds from) ·
  the three-way icon fork (icon-paths.js + ConceptVIcon.jsx beside CV_ICONS) flagged Slice 34, STILL OPEN ·
  glyphic-foundry.html silently falls back to demo candidates on model failure (loud-fail violation) ·
  AXES.md:71-100 already states Tim's relative placement laws — A3's ORIGINAL-PLAN grounding.

---

## THE CENSUS — COMPLETE (2026-07-03, nine-reader team; evidence = census/AREA-*.md)
Coverage: the glyphic-core corpus is now read ≈ in full, first-hand — engine homes (cv-glyphics/cv-shapes/
cv-icons/cv-organisms/icon-paths/cv-vi-glyph full), core/ (all 17 files, DiagramSolver every line),
app/registry 13/13, app/ai 7/7, the system pages (glyphic-system/language/the-whole-thing/system-map/
glyphgraph-generator full), the canon docs (README/DESIGN-LANGUAGE/HANDOFF/SYSTEM-GAPS/AXES/UNIFICATION/
INTEGRATION/LANGUAGE + the analysis remainder classified), the charter docs (THE-GENERATIVE-LANGUAGE/
REGROUNDING), FINDINGS-LOG WHOLE (all 65 slices). Synthesis = SYNTHESIS.md Round 8; criteria = CRITERIA
A6 (the unification slate); sequencing = ROADMAP R1b/R3-rewritten/R4-corrected/R6; the Tim queue =
TIM-DECISIONS.md. Cross-read corrections recorded in Round 8.4 (incl. one census report's own false
claim — registry-spine's "CV_HOST doesn't exist" — caught and corrected: host-runtime.js:429, 8 consumers).
Lockstep debt CLOSED: DESIGN-LANGUAGE §19/§20 + README read-out bullet applied; HANDOFF "since Slice 3"
addendum + SYSTEM-GAPS triage header applied. Remaining known-unread: none in the glyphic-core census
scope; the upstream block system (R5) is the next NEW territory.
