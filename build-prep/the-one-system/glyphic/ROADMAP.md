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

## PHASE REMAINING — the rest of the LIVE-INSTRUMENT groups (design against the vite surface A0 establishes)
- **The interactive canvas/renderer decision** (reactflow vs extend the tldraw/glyphGraphView pattern) — now a real
  choice on the vite surface, under the one-IR law (a projection of the CVGraph, render nodes via CV_GLYPHIC).
- **Incremental-stable placer** (freeze-x/y — C's pinning is the seed; the spatial-theorem placement modes).
- **Data-binding + storage** (typed-glyphic deep-linked persistence; the domain schema; Supabase Realtime; `project://`).
- **G8 self-describing** (guides + pages per glyphic thing; the authoring panel) — the dual AI+human surface.
- **Zones** · the read-out wording live-tuning · reverse-parser + multi-target polish · the 3 gate-detectors (no-staleness).

## Standing rules (every step)
Verify by USE (headless harness + chrome + the live services) · loud-fail (unknown→throw; guard the READ-4/6 silent-
fails: `satisfied`, `ok:false`-in-200, prompt-cap from live `max_model_len`, embed-fails-loud) · deep-link/resolve-
from-source · one-IR (no fifth strand/registry) · sync diff-first to canonical · advisor at the two gates · preserve
what each change keeps (enumerate it).
