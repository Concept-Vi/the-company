---
type: constitution
register: prescriptive
module: source_types
aliases: ["source_types — constitution"]
tags: [company, constitution, source-types, board, noticeboard, registry, provenance]
governs: [board-source-vocabulary]
relates-to: ["[[Company Map]]", "[[item_types]]", "[[board_edges]]"]
status: living
---
# source_types/ — module constitution

**Is:** the file-discovered SOURCE-TYPE registry for the Company NOTICEBOARD (runtime/cc_board.py). A row = a declared ORIGIN of board records / correlatable history (Claude Code transcripts now; GitHub history and other coding apps later). A board item's `source` is a REFERENCE into this registry. Stamping `source` as a registry-ref NOW means a future source (e.g. `github`) folds in by a JOIN on shared keys (author/path/time), NOT a migration — Tim 2026-06-15: "same author so they correlate… matching the schema of each source, declared in the source-type registry."

**Guarantees (the row schema — `source_types/<id>.py` declares `SOURCE_TYPE = {...}`):** required `id` (== filename, fail-loud). Optional `label`, `join_keys` (list of str — the shared keys this source correlates with others on), `desc`. Unknown field RAISES. Validated by `runtime/source_types.py:_build_source_type`.

**The source-types (the live set — the drift home):**
- **claude_code** — Claude Code session transcripts; the default origin. `join_keys: [author, path, time]` (the seam GitHub folds in on).

**Where new things go:** a new source = a new file `source_types/<id>.py` declaring `SOURCE_TYPE` (e.g. a future `github.py`). Update THIS file's live-set when you add one.

**To extend:** drop the `<id>.py` row; `cc_board.reset_registries()` re-discovers it. Zero code change.

**Seam:** discovered by `runtime/source_types.py:SourceTypeRegistry`; consumed by `runtime/cc_board.py` (file_item validates `source`). The recall↔board wire (recollection) treats the board as a capture-source — same source-type seam, one level up.

**Never:** inline the source set as an enum; silently accept an unregistered source; drop `join_keys` semantics (they are the correlation contract).

## Relates to
[[item_types]] · [[board_edges]] · [[the-heart]] (one source-type vocabulary across the board + recollection's capture-sources)

## Agent-authored entries (auto-reflected)
<!-- created live by the create face; one line per entry — keeps the
     drift-home acceptance green; refine the prose by integration. -->
