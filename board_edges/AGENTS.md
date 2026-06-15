---
type: constitution
module: board_edges
aliases: ["board_edges — constitution"]
tags: [company, constitution, board-edges, relation-types, board, noticeboard, registry]
governs: [board-edge-vocabulary]
relates-to: ["[[Company Map]]", "[[item_types]]", "[[source_types]]", "[[relation_types]]"]
status: living
---
# board_edges/ — module constitution

**Is:** the file-discovered EDGE-KIND registry for Company NOTICEBOARD items (runtime/cc_board.py) — the typed cross-registry links a board item carries (`links: [{kind, target}]`). A row is a RELATION-TYPE (same row shape as relation_types/), declared `RELATION_TYPE = {...}`. Discovered by REUSING `runtime/relation_types.py:RelationTypeRegistry` VERBATIM — ONE registry mechanism, a SEPARATE vocabulary dir (exactly as roles/ · projections/ · mark_types/ are separate dirs on the one mechanism). A board item's link `kind` is a REFERENCE into this registry, validated fail-loud.

**Why a SEPARATE dir from relation_types/ (decision, 2026-06-15 — lead + fork + advisor):** the board's edges are STRUCTURAL/PROVENANCE edges (item→session/channel/source/board), distinct from relation_types/'s CORPUS-SEMANTIC edges (fragment-of/sibling) that `find_relations`' inversion-finder reads with near/far. "One grammar" is satisfied by one MECHANISM (the RelationTypeRegistry class), NOT one dir. Keeping board edges here avoids coupling structural edges into the cognition-engine corpus vocabulary, and bets nothing on every future relation_types/ consumer staying parametric. UNIFY DELIBERATELY into relation_types/ only when the Heart's cross-registry resolution/traversal engine lands and a consumer genuinely traverses one unified relation graph — tracked as a board `idea` item, not dropped.

**Guarantees (row schema — identical to relation_types/; `board_edges/<id>.py` declares `RELATION_TYPE`):** required `id` (== filename) + `directed` (bool). Optional `inverse`/`near`/`far`/`label`/`desc`. A malformed entry RAISES at discovery. Validated by `runtime/relation_types.py:_build_relation_type`.

**The edge-kinds (the live set — the drift home):**
- **`authored_by`** (label authored-by) — DIRECTED · item → `session://<id>`. The item was authored by this session (cross-registry provenance — the first exercise of the relation registry across registries).
- **`attached_to`** (label attached-to) — DIRECTED · item → channel/Space. The item is attached to a channel.
- **`sourced_from`** (label sourced-from) — DIRECTED · item → source-type row. The item's origin source.
- **`promoted_from`** (label promoted-from) — DIRECTED · inverse `promoted_to` · item → `board://<id>`. This item was promoted from another (e.g. a request promoted-from an idea).

**Where new things go:** a new edge-kind = a new file `board_edges/<id>.py` declaring `RELATION_TYPE`. Update THIS file's live-set.

**To extend:** drop the `<id>.py` row; `cc_board.reset_registries()` re-discovers it (proven by tests/cc_board_acceptance.py: a new `blocks` edge-kind goes live by row-add, no code).

**Seam:** discovered by `runtime/cc_board.py:_edges_reg()` (a `RelationTypeRegistry` instance over THIS dir); consumed by `file_item` (validates each link's `kind` fail-loud).

**Never:** inline the edge set as an enum; fork a SECOND registry mechanism (this REUSES RelationTypeRegistry — only the dir is its own); silently accept an unregistered edge-kind.

## Relates to
[[relation_types]] (the mechanism this reuses + the eventual unification target) · [[item_types]] · [[source_types]] · [[the-heart]]

## Agent-authored entries (auto-reflected)
<!-- created live by the create face; one line per entry — keeps the
     drift-home acceptance green; refine the prose by integration. -->
