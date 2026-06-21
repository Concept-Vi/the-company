# stack_item_types/ — the channel-STACK item-type registry (FACE-2 / A4)

The file-discovered vocabulary of things the fabric STACKS on a channel for the operator to clear
(the operator-cycle: works → stacks typed items → BLOCKED → Tim clears → resume). Each
`<id>.py` declares a module-level `STACK_ITEM_TYPE` dict — a RENDER/DISPATCH contract, NOT a lifecycle.

- **Mechanism:** `runtime/stack_item_types.py` (the 5th standalone instance of the ONE file-discovered
  registry mechanism — mirrors mark_types/item_types/relation_types/roles/projections; own row shape).
- **NOT the board `item_types/`** — that registry carries a board LIFECYCLE (initial/states/transitions:
  idea/issue/guide/tip/request). THIS carries a render/dispatch contract (row_fields + unsettled_state +
  open_verb). Different shapes → separate registries (reuse the mechanism, not the row).
- **Row shape:** `id` (==filename, required) · `label`? · `desc`? · `row_fields`? {field: source dot-path,
  prefixed by domain — `identity.*` (the /api/territory enrich record) or `feed.*` (the stack-feed row);
  the host reads each from its domain} · `unsettled_state`? (default 'pending'; item leaves the queue when
  state != this) · `open_verb`? {event, payload}. Absent fields degrade soft (host shows `name`); an
  unlanded type fail-louds `--unready`.
- **Add a type = drop a file.** Zero engine code (axes-are-registries). The host (projection,
  STACK-ITEM-HOST-CONTRACT.md) renders any item from the declaration + holds no variant-knowledge.
- **Contract:** build-prep/the-one-application/STACK-ITEM-HOST-CONTRACT.md (the host consume-interface) +
  RESOLVER-CONTRACT.md (the spine). Seeded: decision-sequence (live precedent), presentation, explanation,
  verify-request. The feed (fork's stack-feed) + per-type host renderers (projection) light each end-to-end.
- **The floor:** reading a stack-item-type is a READ — no resolve/dispatch/approve.
