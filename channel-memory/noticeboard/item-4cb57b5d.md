---
id: item-4cb57b5d
address: board://item-4cb57b5d
type: request
source: claude_code
state: open
title: 'Make board registries first-class: wire into suite.py _CORPUS_REGISTRIES +
  create_* + cognition_info'
author_session: ch-al7jdfdr
channel: ''
thread: ''
links:
- kind: authored_by
  target: session://ch-al7jdfdr
created: '2026-06-15T04:35:48.663666+00:00'
updated: '2026-06-15T04:35:48.663666+00:00'
history:
- from: null
  to: open
  by: ch-al7jdfdr
  ts: '2026-06-15T04:35:48.663666+00:00'
  note: filed
---

item_types/ and source_types/ are file-discovered + fail-loud (add-a-row-no-code already works), but board-LOCAL — not yet authorable via the create() MCP tool nor visible in cognition_info. DEFERRED from the B build (advisor: highest-risk/lowest-value to edit the cognition engine's central suite.py in a 27-RED, multi-session-churning tree for a convenience). Do it as its own unit, alone, fast-while-suite.py-is-clean, path-scoped commit: add self.item_type_registry/source_type_registry wiring (~suite.py:328), rows in _CORPUS_REGISTRIES (~352), create_item_type/create_source_type wrappers → _write_registry_file, and pass them to build_cognition_info (~5945). Then a row authored via create() + shown in cognition_info = first-class proven. board_edges intentionally NOT included (it reuses relation_type, which is already in the table).
