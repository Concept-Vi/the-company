---
type: constitution
register: prescriptive
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

**The item-types (the live set — the drift home; `tests/cc_board_acceptance.py` asserts the core types present + per-type lifecycles distinct):**
- **request** — an ask to add/change the Company/MCP/CLI/a channel. open → picked-up → building → done / declined.
- **issue** — a bug/wrong-behaviour report (supersedes the legacy hand-kept SYSTEM-GAPS.md ledger). open → triaged → fixing → resolved / wontfix.
- **tip** — a discovered better way. posted (evergreen) ⇄ archived.
- **guide** — a how-to / living doc, updated in place. living ⇄ archived.
- **idea** — a seed/thought; may be promoted to a request (via a `promoted_from` edge). captured → discussing → promoted / dropped.
- **signal** — a fabric SIGNAL a lane consumes to ACT (first instance: `decision.decided` — the operator decided an addressed decision; work GATED on it can RESUME with the chosen option). The shared-tree, floor-clean half of the operator-cycle's resume wire ([[cross-session-via-shared-tree]]; the live-MCP channel post stays gated) — posted by `decision_registry.decision_decided_signal`, linked `attached_to` the decision:// address. raised → consumed / superseded.
- **④ L6-BOARD landed types (the cloud notice_board_posts pour, organ-studies/BOARD.md §3):** **observation** (61) · **milestone** (58) · **design** (32) · **task** (31) · **blocker** (7) · **cognitive_guide** (3) · **research** (2) · **diagnostic** (1) — the 8 rows landing the 319 cloud posts losslessly; every one honours the LEGACY lifecycle the cloud actually used: open → resolved / closed (⇄ reopen). (The cloud declared richer per-type states — e.g. task's {todo,in_progress,blocked,done} — but 319/319 live posts used only open/resolved/closed; registry-is-truth over the unenforced declaration.) `issue` additionally gained an ADDITIVE `closed` state (12 cloud issue posts land in it; nothing removed — the existing lifecycle is intact).
- **board_view** — a BOARD-VIEW record (④ L6: "one store, many boards" made first-class). A view is itself an addressed item; PINNING is a typed `pinned` edge FROM the view TO an item, so a pin on one view is absent on another (salience belongs to the view, never the item). active ⇄ archived.

**Where new things go:** a new story-type = a new file `item_types/<id>.py` declaring `ITEM_TYPE`. Update THIS file's live-set when you add one.

**To extend:** drop the `<id>.py` row; `cc_board.reset_registries()` (or a fresh process) re-discovers it. Zero code change — the registry re-reads the directory.

**Seam:** discovered by `runtime/item_types.py:ItemTypeRegistry`; consumed by `runtime/cc_board.py` (file_item validates `type`; transition validates the move against the type's declared lifecycle).

**Never:** inline the type set as an enum in code; hardcode lifecycle transitions in the transition logic (they live ON the row); silently skip a malformed row.

## Relates to
[[source_types]] · [[board_edges]] · [[relation_types]] (the edge-vocabulary mechanism this mirrors) · [[the-heart]] (registry-of-registries)

## Agent-authored entries (auto-reflected)
<!-- created live by the create face; one line per entry — keeps the
     drift-home acceptance green; refine the prose by integration. -->
