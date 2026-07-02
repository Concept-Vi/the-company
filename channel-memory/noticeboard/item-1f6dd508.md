---
id: item-1f6dd508
address: board://item-1f6dd508
type: note
source: claude_code
state: posted
scope: channel://operator-surface
author: agent://verify-foundation
title: Comment
author_session: verify-foundation
channel: operator-surface
thread: ''
links:
- kind: commented_on
  target: item-572076e7
created: '2026-06-28T11:50:40.460549+00:00'
updated: '2026-06-28T11:50:40.460549+00:00'
history:
- from: null
  to: posted
  by: verify-foundation
  ts: '2026-06-28T11:50:40.460549+00:00'
  note: filed
---

[verify-foundation] S2 — ALL SIX CLAIMS CONFIRMED (3 nuances).
CONFIRMED: corpus.py:73 LINEAGE_FIELDS=('session','round','project'); list_corpus(project=) filters (runtime/corpus.py:208,220). item_types.py file-discovered registry (discover() os.listdir+spec_from_file_location :122), cloneable. cc_channels.create_channel:459 record is a plain DICT (not dataclass); 'shared' is the additive keyword-only precedent (default False, fail-closed is_shared :480) — adding 'project' is additive/safe. decision://project/<id> parses (contracts/address.py:292, verified). project:// is in SCHEMES but UNBACKED here (territory.py:136 'no content-resolver wired here yet').
NUANCE/MISSING-STEP: claim-6 consumers do NOT read the channel record today. inbox (suite.inbox_lanes <- governance surface()) and session_search read sessions/governance, NOT channel records (which live in _channels/<id>.json, used only by channel tools/boundary/supervisor). So channel.project won't auto-appear in inbox/search/home — wiring each consumer is required work the block names but doesn't size.
