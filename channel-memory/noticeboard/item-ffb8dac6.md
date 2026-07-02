---
id: item-ffb8dac6
address: board://item-ffb8dac6
type: idea
source: claude_code
state: captured
scope: global
author: session://ch-al7jdfdr
title: Unify the board edge vocabulary into relation_types/ when the Heart resolution
  engine lands
author_session: ch-al7jdfdr
channel: ''
thread: ''
links:
- kind: authored_by
  target: session://ch-al7jdfdr
created: '2026-06-15T04:35:54.626770+00:00'
updated: '2026-06-15T04:35:54.626770+00:00'
history:
- from: null
  to: captured
  by: ch-al7jdfdr
  ts: '2026-06-15T04:35:54.626770+00:00'
  note: filed
---

board_edges/ reuses the RelationTypeRegistry MECHANISM but is a SEPARATE vocabulary dir from the cognition corpus relation_types/ (decision 2026-06-15: one mechanism, separate dirs — like roles/projections/mark_types). The fork argued for folding board edges into relation_types/ as one relation vocabulary (Heart one-grammar for relations); the advisor + lead kept them separate because find_relations is safe only as long as every consumer stays parametric, and structural edges (item→session) differ from corpus-semantic edges (fragment-of). UNIFY DELIBERATELY: when the Heart's cross-registry resolution/traversal engine actually lands and a consumer genuinely traverses ONE unified relation graph (board + corpus + recollection's beat-3 edges), fold board_edges/ rows into relation_types/ + update relation_types/AGENTS.md (the drift-home acceptance asserts every row reflected). Until then, separate is lower-risk.
