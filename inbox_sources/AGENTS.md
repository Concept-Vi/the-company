---
type: constitution
register: prescriptive
module: inbox_sources
aliases: ["inbox_sources — constitution"]
tags: [company, constitution, inbox-sources, operator, needs-me, registry]
governs: [needs-me-inbox-source-vocabulary]
relates-to: ["[[Company Map]]", "[[item_types]]", "[[operator app — constitution]]"]
status: living
---
# inbox_sources/ — module constitution

**Is:** the file-discovered INBOX-SOURCE registry for the operator's NEEDS-ME INBOX (I1,
`board://item-67e34f0c`) — `runtime/inbox_source_registry.py:InboxSourceRegistry`, folded by
`runtime/needs_me.py:needs_me_inbox()` into ONE card list `GET /api/needs-me` serves. Mirrors
`item_types/` (the ONE registry mechanism: file-discovered, id == filename, fail-loud, dict-like,
rediscover) — a STANDALONE copy because the row shape is its own (a fetch + a card-shape + a verb list,
not a lifecycle).

**Guarantees (the row schema — `inbox_sources/<id>.py` declares `INBOX_SOURCE = {...}` PLUS its own
zero-arg `fetch()` adapter in the SAME file):** required `id` (== filename, fail-loud otherwise), `label`
(non-empty str), `fetch` (a dotted `"pkg.mod:attr"` reference resolving to a callable — commonly
`"inbox_sources.<id>:fetch"`, the adapter living right there), `card_shape` (the 5 field-name hints:
`id_field · address_field · title_field · why_field · created_field` — the generic fold in
`runtime/needs_me.py` uses these to lift a raw item into the uniform card, so the FETCH is responsible for
making its raw items actually carry those fields), `verbs` (a non-empty list of `{id, label, door}` — the
declared action buttons; `door` may carry `{id}`/`{address}` tokens the fold substitutes per-card). A
malformed entry FAILS LOUD at discovery — never a silent skip. Validated by
`runtime/inbox_source_registry.py:_build_inbox_source`.

**★ TRAP (learned by use, 2026-07-13): never name a module `inbox_sources.py`.** A module of that exact
name ANYWHERE Python can import it (e.g. `runtime/inbox_sources.py`) SHADOWS this directory — Python's
import rule is "a regular module always beats a namespace package, regardless of sys.path order" (PEP
420), and `runtime/` is always on `sys.path` when `bridge.py` runs (its own script directory). The
registry LOADER lives at `runtime/inbox_source_registry.py` specifically to avoid this collision — keep
it there; do not rename it back.

**The inbox-sources (the live set):**
- **decisions** — open decisions (`state == "pending"`) from `runtime.cognition.decision_registry()` /
  `decision_inbox`, the SAME feed `/api/decisions` projects. Verb: `view` → `/api/decision` (a read/drill
  door — `decision_take` itself is a heavier, `/api/territory/write`-gated action that doesn't fit a bare
  verb button in v1).
- **surfaced** — unresolved surfaced intents from `Suite.list_surfaced()` (T3-HYGIENE: `test_origin`
  excluded, mirrors `Suite.inbox_lanes()`). Verbs: `approve`/`reject` → `/api/resolve` (the verb's own id
  IS the `choice` sent).
- **obligations** — Tim's pending typed messages via `cc_board.pending_obligations("tim")`. Verb:
  `comment` → `/api/board/comment` (an HONEST LIMITATION — see the module's docstring: this posts a real,
  visible comment but does NOT clear `_obligation`, which needs a `reply_to`-edged reply the bridge
  doesn't expose).
- **board_requests** — open `request`-type board items (`cc_board.list_items(type="request",
  state="open")`). Verb: `comment` → `/api/board/comment` (same honest limitation — it does not transition
  the item's state).

**Where new things go:** a new "needs me" feed = a new file `inbox_sources/<id>.py` declaring
`INBOX_SOURCE` + its own `fetch()`. Zero code change to `runtime/needs_me.py` or
`operator/app/src/views/Inbox.tsx` — the fold and the card renderer are both generic over the registry.
Update THIS file's live-set when you add one.

**To extend:** drop the `<id>.py` row; `InboxSourceRegistry().discover(...)` (or a fresh process)
re-discovers it.

**Seam:** discovered by `runtime/inbox_source_registry.py:InboxSourceRegistry`; folded by
`runtime/needs_me.py:needs_me_inbox()`; served by `runtime/bridge.py`'s `GET /api/needs-me`; consumed by
`operator/app/src/views/Inbox.tsx` via `operator/app/src/lib/api.ts:fetchNeedsMe`/`actOnCard`.

**Never:** inline the source set as a hardcoded fold in `needs_me.py`; name the loader module
`inbox_sources.py`; let a card's verb label overclaim what its door actually does (see the honest-
limitation notes above); let one broken source blank the rest of the inbox (the fold's per-source
try/except — `errors[]` — is load-bearing, keep it).

## Relates to
[[item_types]] (the mirrored registry mechanism) · [[operator app — constitution]] (the Inbox view + the
`X-Operator-Session` header convention) · [[the-heart]] (registry-of-registries)
