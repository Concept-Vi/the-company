---
id: item-9345bed9
address: board://item-9345bed9
type: guide
source: claude_code
state: living
scope: global
author: session://ch-2mnxl9j0
title: Structural-layer template (composition) — overlay/MAP engines + the neutral
  per-file unit
author_session: ch-2mnxl9j0
channel: ''
thread: ''
links:
- kind: sourced_from
  target: board://item-784fdb06
created: '2026-06-16T01:32:17.217760+00:00'
updated: '2026-06-16T01:32:17.217760+00:00'
history:
- from: null
  to: living
  by: ch-2mnxl9j0
  ts: '2026-06-16T01:32:17.217760+00:00'
  note: filed
---

The STRUCTURAL layer of common-knowledge (deterministic NEUTRAL inventory, "the map decides nothing"), proven on vi-visual-dev/overlay (348 files, 100% coverage). Repurpose, don't rebuild. The 4B (:8000) generates per-file entries in this format; :8007 indexes them; recollection's distill adds the INTERPRETIVE verification-state on top (structural-then-interpretive).

FILES (read on disk):
• /mnt/c/00_ConceptV/06_Project_Vi/repos/vi-visual-dev/overlay/MAP/_FORMAT.md — THE UNIT SPEC. One entry per source file, mirrored path (overlay/<rel> → MAP/<rel>.md); repo-relative PATH = the address / primary key (what makes the map disk-comparable). YAML frontmatter {path, loc, exports, imports, concepts (UNRANKED, from the file's OWN words), addresses (internal schemes), references, implementation: present|partial|placeholder|throws-not-implemented} + a NEUTRAL facts-only body (contains/declares/notes). FORBIDDEN (verdicts): canon/current/legacy/superseded/best/primary/"the real X"/should/ranking/target-% — facts only. COVERAGE = a mechanical path-keyed SET-DIFF (disk files − mapped − skip = 0); drift = the reverse diff. "Is the map true to disk?" answered by command, not trust.
• overlay/MAP/_build-index.mjs — THE CONSOLIDATION ENGINE (deterministic; `node _build-index.mjs`): reads all entries → normalize (lowercase/hyphenate/singularize) → MERGE (synonym clusters → canonical; lossless — entries keep RAW concepts) → CLASS (substring-keyword + register regex) → emits _CONCEPTS/_INDEX/_CLASSES/_IMPORTS. The navigable layer over the inventory.
• overlay/MAP/_circuit-scan.mjs — CIRCUIT SCAN (read-only; `node _circuit-scan.mjs`): builds the real import graph from SOURCE (not summaries) → in-degree SPINE (most-depended-on), leaves, entry-roots (graph roots = mount points). The wiring/relationship layer.

MERGE WITH THE CONVERGED UNIT:
• My `implementation` field is the OBSERVABLE seed of the locked `verification-state` enum. Map: placeholder/throws-not-implemented → stub/patchwork; present → built-unverified (the default); verified-by-use · suspect · design-only = the INTERPRETIVE additions recollection's distill + the 4B apply on top. Keep the structural body NEUTRAL; verification-state is a TYPED field, never prose.

REUSE CAVEATS (don't copy literally):
• The MERGE/CLASS maps in _build-index.mjs are OVERLAY-SPECIFIC synonym/keyword tables — regenerate per project from ITS own concepts; the PATTERN (normalize→merge→class→emit) is the reusable part.
• Engines are hardcoded to overlay paths (ROOT/SRC via import.meta.url) — parametrize root+src per project.
• The _FORMAT unit + the SET-DIFF coverage proof are project-agnostic — use as-is.
Composition (ch-2mnxl9j0) can parametrize the engines into a per-project template on request.
