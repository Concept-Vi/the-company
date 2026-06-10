# Context Forager — Research Synthesis

**Round 1 (2026-06-10 overnight): a 4-lane parallel workflow (facets · retrieval · canvas · handoff),
108 tool-uses over the real code/data. FULL raw findings with file:line evidence:
`build-prep/brain/forager-research-raw.md` (canonical detail; this doc is the load-bearing digest).
Vision source: `build-prep/brain/CONTEXT-FORAGER-RIFF.md` (Tim's verbatim).**

## The ground truth that shapes everything

**Corpus reality:** 2,067 deduped records (history=1,420 mined exchanges · repo=644 file digests).
Index rows carry: seq · ts(capture) · address · source_address · record_kind · projection ·
lineage{session, round, project}. `find_corpus` filters by project/kind/projection/source_address;
`query_corpus(text, space=, k=)` does semantic ranking (BGE-M3, honest-empty when embedder down);
`find_relations` does cross-space inversion (needs both spaces vectored). All three are MCP-exposed
(`corpus` tool ops query/list/find/read; detail='detailed' inlines content). **No aggregate/count op**
— facet counts are client-side over op='list' (2k rows is fine) or a new op later.

## Facet reality (Tim's five, honestly)

| Facet | Today | Path to real |
|---|---|---|
| time period | ✗ capture-ts useless (all 2 days); ts_source on only 173/1420, content-only | CHEAP DETERMINISTIC BACKFILL: re-walk transcripts → re-stamp ts_source (latest-seq-wins); g23_mine one-liner DONE (this round) stops the gap |
| topic | ✗ topics space declared, 0 records | interim: pattern_tag clusters (.build/g13/clusters.json) facet the history half NOW; real: a capture run projection='topics' (machinery exists, space auto-appears) |
| project | field exists, degenerate (2079/2080 = 'company') | derivation for exchange:// records from transcript cwd/content; session lineage (g23-mine, exocortex-core…) names CAMPAIGNS not projects |
| principle | ✗ principles space declared, 0 records | a capture run projection='principles'; find_relations then lights up (it fail-louds today by design) |
| language/vocab | ✗ not yet captured | the coined-vocab projection design exists; later round |
| (free) kind/projection/session/source-prefix | ✓ indexed today | v1 chips |

## Canvas reality (lane: canvas)

ONE custom shape exists (NodeShapeUtil, App.tsx:364 registration): TLBaseShape + T.* props
validators + Rectangle2d + HTMLContainer with zoom>0.5 semantic zoom — the direct template.
**Circle2d is exported by tldraw 3.15.6** (true circular hit-area). Programmatic create follows
loadGraph's update/create/prune with createShapeId + the 'n-' prefix; **a forager loader needs its
OWN id prefix ('f-') + type filter so the graph loader's PRUNE never eats forager circles (and vice
versa)** — the coexistence rule. Selection: editor.getSelectedShapes / store listeners are available.
persistenceKey discipline: bump on any shape-props change (company-canvas-v3 today).

## Handoff reality (lane: handoff)

`run_turn(context_block=...)` is an opaque string prefixed onto EVERY turn (ui_claude_session.py:80) —
a selection-set is purely a bridge-side block-builder change. `--resume` carries history, so
**blocks compound across turns**: the set-block must be CURRENT-STATE (replace, not append semantics
in wording) and bounded (~the address_help precedent: per-item caps + a total cap; research suggests
listing {address, kind, head-content} per selected node, full content only for small sets).

## What this means (the one-paragraph design)

v1 is ASSEMBLY: a search box (query_corpus per space) → hits as ForagerCircle shapes ('f-' prefix,
Circle2d, semantic zoom: label → River detail) with lineage/semantic edges → whittle by delete,
grow by more searches → tldraw multi-select → "give to builder" composes a bounded selection-set
context block → /api/claude/turn (S1's seam, already live). Facet chips v1: space · kind ·
session · pattern-tag-cluster; time chip arrives with the backfill flow; topics/principles chips
arrive with their capture runs (each is a flow row, not new machinery).
