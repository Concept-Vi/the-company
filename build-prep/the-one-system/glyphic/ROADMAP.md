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
  → it renders, reads BOTH directions, parses.
- **R2 · Referent words → profile data (A1).** REFERENT_KIND/OP + the determiner ladder move into the
  active profile as field data; referent() and parse() read them there. VERIFY: setField changes read-out
  AND parse live, no code edit.
- **R3 · Placement redo (A3) — the relative laws.** cv-address spans BECOME the position system (address
  = relative span/angle in parent; mutation re-partitions ONE parent span; inside re-resolves bounded+
  angled+animated, outside holds; SAME op for order-changes). Replaces the absolute-freeze DiagramSolver
  edit. verify_g11 REWRITTEN to assert the laws (currently 19/21 broken); the left-vs-centred taste call
  goes to Tim's eye in the live render.
- **R4 · Meaning-shape repairs (A4).** 12 minted symbols → meaning FIELDS via the author API; ordinal
  axis → contextual resolution + the corpus-sampled `--ramp-*` tokens (SYSTEM-GAPS' pre-existing intent);
  gradient interpretation un-baked (one contextually-loaded meaning, field-shaped).
- **R5 · The block system read.** The block/resolution system lives on the UPSTREAM claude.ai/design
  remote — pull/read it (DesignSync) BEFORE G8/zones so those build on it, not beside it.

## PHASE REMAINING — the rest of the LIVE-INSTRUMENT groups (design against the vite surface A0 establishes)
> Reconciled 2026-07-03: G9 parse, G10 targets, G8b binding engine, G2.4, G5 routing are BUILT+verified
> (SYNTHESIS Round 7) — struck from this list. What genuinely remains:
- **The interactive canvas/renderer decision** (reactflow vs extend the tldraw/glyphGraphView pattern) — now a real
  choice on the vite surface, under the one-IR law (a projection of the CVGraph, render nodes via CV_GLYPHIC).
- **Data-binding persistence** (G8b.4: typed-glyphic deep-linked storage; the domain schema; Supabase
  Realtime; `project://`; the ledger.assertion ASK at board://item-be541559) — the binding ENGINE is done.
- **G8 self-describing** (guides + pages per glyphic thing; the USER authoring panel — the AI face exists)
  — on the upstream block system per R5.
- **Zones** · G9 subordination/conditional parse gaps (they throw naming themselves) · a `code` READGRAPH
  target when needed · the 3 gate-detectors (no-staleness) · the G5 FORM taste flags (mixed routing,
  arrowhead angle) + the writer FORM pass to Tim's eye.
- **The wording live-tune** rides EVERY phase (A5: correctability-by-use, never a checkpoint).

## Standing rules (every step)
Verify by USE (headless harness + chrome + the live services) · loud-fail (unknown→throw; guard the READ-4/6 silent-
fails: `satisfied`, `ok:false`-in-200, prompt-cap from live `max_model_len`, embed-fails-loud) · deep-link/resolve-
from-source · one-IR (no fifth strand/registry) · sync diff-first to canonical · advisor at the two gates · preserve
what each change keeps (enumerate it).
