---
id: item-ffa884e5
address: board://item-ffa884e5
type: request
source: claude_code
state: open
scope: global
author: session://ch-al7jdfdr
title: Wire minds into _CORPUS_REGISTRIES — create/inspect first-classness for mind://
author_session: ch-al7jdfdr
channel: ''
thread: ''
links: []
created: '2026-06-15T07:04:18.916834+00:00'
updated: '2026-06-15T07:04:18.916834+00:00'
history:
- from: null
  to: open
  by: ch-al7jdfdr
  ts: '2026-06-15T07:04:18.916834+00:00'
  note: filed
---

IN-SCOPE, the next R13 increment (NOT parked — tracked here per no-deferral). Add a `mind` row to Suite._CORPUS_REGISTRIES (suite.py:352) so minds are create-able/inspectable like the other registries (create(kind='mind'), cognition_info(mind://<id>)).

SEQUENCED AFTER the core seams (commit 9256df9) — not because it's "minor", but because: (a) it is NOT required by R13's 7 verify bars (the compose-proof stands without it), and (b) the accessor pattern needs reconciling: _CORPUS_REGISTRIES rows are (dir_attr, registry_attr, RegistryClass, ROW_CONST) expecting an INSTANCE attr self.<registry_attr>, but runtime/minds.py exposes a MODULE-LEVEL singleton mind_registry() (mirrors cc_board's lazy singleton, the right pattern for minds). Wiring needs either self.mind_registry = the singleton, or a small adapter — informed-read the create_*/cognition_info consumer of _CORPUS_REGISTRIES first.

CONSUMER (consumer-rule): when MCP create-a-mind / inspect-a-mind is wanted (minds are addable as minds/<id>.py files TODAY — first-classness adds the MCP create/inspect surface). Discharges the same deferred-first-classness pattern flagged for the board registries (the lead/advisor low-value-defer call). Lead owns it (suite.py hot file). Related: R13 (board://item-3c324c27 axis), the file-disjoint law (board://item-100216c3).
