---
type: constitution
module: item_types
aliases: ["item_types — constitution"]
tags: [company, constitution, item-types, board, noticeboard, registry]
governs: [board-item-type-vocabulary]
relates-to: ["[[Company Map]]", "[[source_types]]", "[[board_edges]]"]
status: living
---
# item_types/ — module constitution

**Is:** the file-discovered ITEM-TYPE registry for the Company NOTICEBOARD (runtime/cc_board.py). A row = one of Tim's "story things" — a KIND of board record (request · issue · tip · guide · idea) WITH its own lifecycle (the legal state-machine). File-discovered, never a hardcoded enum: a board item's `type` is a REFERENCE into this registry, and its legal `state` moves are a property of its type's row.

**Guarantees (the row schema — `item_types/<id>.py` declares `ITEM_TYPE = {...}`):** required `id` (== filename, fail-loud otherwise), `initial` (∈ states), `states` (non-empty list of str), `transitions` ({from_state: [allowed to_state, …]}; every key + target ∈ states). Optional `label`, `desc`. A malformed entry (bad id / id≠filename / unknown field / initial∉states / transition to/from unknown state) FAILS LOUD at discovery — never a silent skip. Validated by `runtime/item_types.py:_build_item_type`.

**The item-types (the live set — the drift home; `tests/cc_board_acceptance.py` asserts all five present + per-type lifecycles distinct):**
- **request** — an ask to add/change the Company/MCP/CLI/a channel. open → picked-up → building → done / declined.
- **issue** — a bug/wrong-behaviour report (supersedes the legacy hand-kept SYSTEM-GAPS.md ledger). open → triaged → fixing → resolved / wontfix.
- **tip** — a discovered better way. posted (evergreen) ⇄ archived.
- **guide** — a how-to / living doc, updated in place. living ⇄ archived.
- **idea** — a seed/thought; may be promoted to a request (via a `promoted_from` edge). captured → discussing → promoted / dropped.

**Where new things go:** a new story-type = a new file `item_types/<id>.py` declaring `ITEM_TYPE`. Update THIS file's live-set when you add one.

**To extend:** drop the `<id>.py` row; `cc_board.reset_registries()` (or a fresh process) re-discovers it. Zero code change — the registry re-reads the directory.

**Seam:** discovered by `runtime/item_types.py:ItemTypeRegistry`; consumed by `runtime/cc_board.py` (file_item validates `type`; transition validates the move against the type's declared lifecycle).

**Never:** inline the type set as an enum in code; hardcode lifecycle transitions in the transition logic (they live ON the row); silently skip a malformed row.

## Relates to
[[source_types]] · [[board_edges]] · [[relation_types]] (the edge-vocabulary mechanism this mirrors) · [[the-heart]] (registry-of-registries)

## Agent-authored entries (auto-reflected)
<!-- created live by the create face; one line per entry — keeps the
     drift-home acceptance green; refine the prose by integration. -->
