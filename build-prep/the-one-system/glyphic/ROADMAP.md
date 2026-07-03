# Glyphic — Unified Build Roadmap (the sequencing layer)

> ONE ordered remaining-work list over the existing docs (CRITERIA/GUIDE/SYNTHESIS = the engine plan ·
> LIVE-INSTRUMENT.md = the unification map · A-fusion/A-DESIGN.md = the AI union · UNDERSTANDING/00 = the method).
> This is a roadmap, not a re-derivation — it points. Home = claude-ds; AI home = the Company (decided).
> Governing frame: sequential build, **verify-by-use per step**, loud-fail, deep-link/resolve-from-source,
> one-IR, unions-not-bridges, sync diff-first. **Orchestration (advisor-corrected): A is a sequential refactor
> of one shared registry — NOT a fan-out. Build the spine sequentially with a verify-gate per step; fan out
> agents ONLY for genuinely independent bits (the drop-in role files, the embed-space). Advisor at two gates:
> before the caps→roles migration, and before the first `~/company` write.**

## DONE (this session — built, verified, synced to canonical)
- **The Glyphic language engine** — facets · rulebook+validator · read-out (referent/readGraph) · conditionals/
  negation · data-binding · reverse parser · multi-target · the DiagramSolver glyphgraph render. Harness-green.
- **The generator** — B (meaning-first writer: describe→resolve→draw+read; pickers demoted to "refine") + C
  (collaborative: canvas click/shift-multiselect/rubber-band/drag-move-pinned/dblclick-insert/group-ops +
  `window.CV_GLYPHGRAPH_SESSION` shared-selection substrate). Verified by sight + interaction.
- **The substrate** — 20 findings · the unification map · UNDERSTANDING/00 (method + relational whole + trust-map).
- **A — the AI union — DESIGNED + decisions settled** (Company home · vite-proxy door · charter nod given).
- **Pre-flight (2026-07-02):** bridge :8770 ✓, embed returns a real vector ✓, run_role route live ✓, 37 roles ✓.

## PHASE A — the AI union (sequential, verify-gated; A-DESIGN §8)
- **A0 · WALKING SKELETON (item #1 — de-risk the spine before anything else).** The thinnest vertical: a
  same-origin surface (vite `/api`→:8770 proxy) that (i) fires ONE `run_role` WITH a `json_schema` and gets back
  VALIDATED structured JSON, and (ii) embeds a phrase → a vector. Proves the one load-bearing unknown
  (does `json_schema` forward end-to-end through the transport passthrough — READ-5/6 flagged it). Embed half
  already proven via shell. **If schema-forward fails, the design adjusts here — huge misdirected build saved.**
- **A1 · One-registry + projection seam.** `CV_HOST.registerKind(kind,resolverFn)` + role-indirection →
  `CV_AI` resolves entries from the one home; collapse the ~33 `'claude'` pins to one binding; restore loud-fail.
  **Preserve the 43 capabilities:** migrate ONE end-to-end, confirm the other 42 still resolve, THEN proceed.
  *(advisor gate before the destructive migration.)*
- **A2 · Model-capabilities → roles.** The fusion move: model-using caps become typed roles (own prompt+schema),
  fired via the existing `run_role` — no dumb endpoint, no double-prompt. Pure-fn caps stay browser-run.
  *(the `glyph_*` role files are independent drop-ins → safe to fan out once the pattern proves on one.)*
- **A3 · Embed path + `glyph_meaning` projection space** + populate/embed/reindex (registry/data; `~/company` write → advisor gate).
- **A4 · Meaning-resolution + generate-on-miss** in the writer — embed-nearest + generate-role-on-miss; retire the starter parser.
- **A5 · Extract/compose roles** (`roles/glyph_extract.py` / `glyph_compose.py` + map→reduce) — the real NL→graph.
- **A6 · Collaborative AI** — a capability reads `CV_GLYPHGRAPH_SESSION` (selection+graph) + pushes graph-ops. Two hands, one CVGraph.

## PHASE CONVERGENCE — counterpart/design → claude-ds
Identify `/home/tim/repos/counterpart/design`'s unique parts (dna/ engine/ factory/ pieces/[56] surface/ supabase/)
and FUSE the best into claude-ds; drop the parallel (islands-join-mainland). A scoped read+fuse pass.

## PHASE RECONCILE — the 2026-07-03 correction, FIRST (CRITERIA AMENDMENTS A1-A5; drift → law)
> This phase repairs what the W-loop drift broke and lands Tim's corrections as build. It PRECEDES
> everything below because the pieces below stand on these homes (edges, placement, meaning-shape).
- **R1 · The edge law (A2 + G6.2 in one move).** relationship Types gain `directed`+`inverse` (converging
  the Company's relation_types shape); readGraph realises the inverse from focus (one stored edge, both
  tellings); the cv-edges `verbs` table is dispositioned through the meaning/registration doors WITH
  opposites; the soft kind-default goes loud; the existing kinds (face/documents/higher-order/navigates)
  re-expressed as verb-pairs or surfaced to Tim in the live render. VERIFY: author a verb-pair at runtime
  → it renders, reads BOTH directions, parses. **[R1 core BUILT 2026-07-03, commit 28e1a94d — verify_edgelaw 15/15.]**
- **R1b · The edge law's census tails** (CRITERIA A2 census notes): delete cv-edges' `means:` sentences
  (the second meaning home, resolving live) · enrich glyphic.assist's payload + context.glyphic with
  directed/inverse (vocab.relations = full fields, not bare ids; update roles/glyph_assist.py's kind doc) ·
  name directed/inverse/kindWord/opWord/determiner in glyphic.author/-relation's declared params
  (discoverability = correctability) · describeRelation realises inverses (same law, second read-path) ·
  fold system-map EDGE_TYPES into the one edge home (verbs from meaning fields, colours from the profile —
  its node encoding is already CV_MEANING-sourced; only edges were left hardcoded) · 'documents' default-
  RETIRED pending the Tim door (appears in no Tim material, no live graph).
- **R2 · Referent words → profile data (A1).** REFERENT_KIND/OP + the determiner ladder move into the
  active profile as field data; referent() and parse() read them there. VERIFY: setField changes read-out
  AND parse live, no code edit. **[BUILT 2026-07-03, commit bac3ed16 — verify_referent_data 12/12; the
  seeded words match the recorded LANGUAGE.md canon (census/AREA-tim-canon §C1).]**
- **R3 · Placement redo (A3) — the relative laws.** cv-address spans BECOME the position system (address
  = relative span/angle in parent; mutation re-partitions ONE parent span; inside re-resolves bounded+
  angled+animated, outside holds; SAME op for order-changes). Replaces the absolute-freeze DiagramSolver
  edit. verify_g11 REWRITTEN FIRST (falsify-first) to assert the laws per census/AREA-canvas-engines §E
  (currently 19/21 broken); the left-vs-centred taste call goes to Tim's eye in the live render (centred
  is now LAW-DERIVED under spans — present both, recommend centred).
  **Design of record = census/AREA-canvas-engines §E** (frames tree · LCA boundary · proportional
  re-partition · movement = the existing growth animator on the address diff · authored x/y priority kept).
  Pre-read = SYNTHESIS Round 6 + verify_g11's own header (NOT FINDINGS-LOG — the G11 era never wrote its
  slices; that gap is itself booked). It is wiring PLUS law-design: cv-address's algebra exists unconsumed
  (13/13) but the boundary-cascade/budget/animation parts are real design (don't under-scope as W2 did).
  Preserve the generator's narrow contract (nd.x/nd.y + nd._pos; 5 affordances); single-source its copied
  VB/MARG constants (export the projection); land the R3 seam at the retired place() call-site. Fold-toward:
  the System Map's childValues partition (same law, more tested). En-route sweep: the two silent catches
  loud, the raw hex → token, harness loader kept in step (it source-slices `function layout(graph) {`).
  SCOPE: glyphgraph case first; the pre-language layouts follow as a named tail (TIM-DECISIONS default).
- **R4 · Meaning-shape repairs (A4, census-corrected).** The 12 symbols: description→caption (depiction-
  only default) OR field+wiring if Tim wants them speaking (TIM-DECISIONS — symbols are the intrinsic
  exception, so the profile is NOT their home); ordinal axis → contextual resolution POINTING AT the
  existing `--ramp-1..4` tokens (colors_and_type.css:76-79 — never re-mint); gradient interpretation
  un-baked; cv-shapes shapeTypes `meaning:` sentences marked fallback-only with a sync note (the
  octagon='Gateway' origin home, cv-shapes.js:79).
- **R5 · The block system read.** The block/resolution system lives on the UPSTREAM claude.ai/design
  remote — pull/read it (DesignSync) BEFORE G8/zones so those build on it, not beside it. Check its
  Type/slot/socket grammar against THIS registry's grammar for compatibility before any merge (a second
  structurally-different Type grammar arriving from upstream = the drift class this census exists to prevent).
- **R6 · THE UNIFICATION SLATE** (CRITERIA A6, the census's 10 items): third-solver naming + one-placement-
  law framing · typeToNode routing for address-bearing glyphgraph nodes · EDGE_TYPES fold (rides R1b) ·
  glyphic-foundry boot-check + fold-forward as the G8.3 seed (+ its silent demo-fallback made loud;
  AtomiCity check) · cv-organisms disposition · icon-fork retirement · components-type orphans decision +
  ax()/sub() unification · W6/CV_SCAN reuse for G8.3/G8.4 + the params-discoverability fix first · the
  meaning-author serializer · the small loud-fail closures. Plus the SELF-DESCRIPTION debts: HANDOFF.md
  "since Slice 3" addendum · SYSTEM-GAPS.md closed-items header · FINDINGS-LOG slices for every future
  law-level change (the G11 era's missing slices = the cautionary tale) · one chrome pass over
  language.html / the-whole-thing.html / the generator (page-green, owed since R1/R2; the generator's AI
  pipeline is BUILT both sides — what's missing is exactly this end-to-end verification).

## PHASE REMAINING — the rest of the LIVE-INSTRUMENT groups (design against the vite surface A0 establishes)
> Reconciled 2026-07-03: G9 parse, G10 targets, G8b binding engine, G2.4, G5 routing are BUILT+verified
> (SYNTHESIS Round 7) — struck from this list. PHASE A corrections from the census (AREA-ai-layer): **A1
> role-indirection is DONE in app/ai/** (zero literal 'claude' pins; ROLE_PROVIDERS live) — remaining A1 =
> CV_HOST.registerKind's environment-side migration (built, unexercised); **A2 has proven on TWO
> capabilities** (glyphic.generate, glyphic.assist); **A5 = the one genuinely unfired piece**
> (glyph_extract/glyph_compose exist both sides, no caller — split: BUILT / VERIFY-by-use). What genuinely remains:
- **The interactive canvas/renderer decision** (reactflow vs extend the tldraw/glyphGraphView pattern) — now a real
  choice on the vite surface, under the one-IR law (a projection of the CVGraph, render nodes via CV_GLYPHIC).
- **Data-binding persistence** (G8b.4: typed-glyphic deep-linked storage; the domain schema; Supabase
  Realtime; `project://`; the ledger.assertion ASK at board://item-be541559) — the binding ENGINE is done.
- **G8 self-describing** (guides + pages per glyphic thing; the USER authoring panel — the AI face exists)
  — on the upstream block system per R5.
- **Zones** · G9 subordination/conditional parse gaps (they throw naming themselves) · a `code` READGRAPH
  target when needed · the 3 gate-detectors (no-staleness) · the G5 FORM taste flags (mixed routing,
  arrowhead angle) + the writer FORM pass to Tim's eye.
- **G5 FORM addendum**: relation-TYPE by sight (two dashed edges of different kinds are visually identical
  today — language.html's own honest "Next:" flag; G5.1's ☑ covers mood/state/direction, not type).
- **The charter's under-booked charges** (census/AREA-canon-docs §E, Tim-visible before adoption since they
  widen scope): the provision/product bar ("frames without furniture" — organisms/atmosphere/evidence-
  density/zones on the canvas) as explicit items · two-wayness as a STANDING invariant (checker), not a
  one-off R1 · PHASE CONVERGENCE adopts THE-GENERATIVE-LANGUAGE §2's 16-face fusion map as its worklist
  (the mapping exists; don't flatten to "a scoped pass"; method precedent = the Slice 27→28 fold-in) · the
  missing narrative-arc organ (sequence.json face — cv-arc.js is its unconsumed engine half).
- **The wording live-tune** rides EVERY phase (A5: correctability-by-use, never a checkpoint).
- **TIM-DECISIONS.md** (same folder) = the standing Tim-visible queue (defaults set, nothing gated).

## Standing rules (every step)
Verify by USE (headless harness + chrome + the live services) · loud-fail (unknown→throw; guard the READ-4/6 silent-
fails: `satisfied`, `ok:false`-in-200, prompt-cap from live `max_model_len`, embed-fails-loud) · deep-link/resolve-
from-source · one-IR (no fifth strand/registry) · sync diff-first to canonical · advisor at the two gates · preserve
what each change keeps (enumerate it).
