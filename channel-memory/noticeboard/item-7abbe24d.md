---
id: item-7abbe24d
address: board://item-7abbe24d
type: block
source: claude_code
state: current
title: P10 · --- the editable location (Tim's "reduce the agent's effort") ---
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-e42d651f
created: '2026-06-24T01:32:19.966129+00:00'
updated: '2026-06-24T01:32:19.966129+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:19.966129+00:00'
  note: filed
---

# --- the editable location (Tim's "reduce the agent's effort") ---
edit_target:                                     # WHERE to change it — direct, not a search
  content_mode:  board://<node-id>  | file://<abs-path>#L<a>-<b>
  ui_mode:       ui://<kind>/<ref>  →  code://<stem>/<symbol>   # the REAL join: Suite.resolve_scope
                                                  #   reads design/_system/{addresses,code-symbols}.json
  dependencies:  [code://…]                       # from the code-archaeology cards (imports/declares)
