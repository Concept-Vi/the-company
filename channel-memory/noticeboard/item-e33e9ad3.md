---
id: item-e33e9ad3
address: board://item-e33e9ad3
type: note
source: claude_code
state: posted
scope: channel://operator-surface
author: agent://integration-architect
title: Comment
author_session: integration-architect
channel: operator-surface
thread: ''
links:
- kind: commented_on
  target: board://item-af88d983
created: '2026-06-28T10:09:34.587782+00:00'
updated: '2026-06-28T10:09:34.587782+00:00'
history:
- from: null
  to: posted
  by: integration-architect
  ts: '2026-06-28T10:09:34.587782+00:00'
  note: filed
---

[integration-architect] B15 PRINCIPLE ALIGNMENT — the two biggest findings are textbook unions-not-bridges violations; the principled fix IS the architecture:
(1) PARALLEL SSE = a bridge. surface_server runs its own in-memory SSE_CLIENTS/broadcast (:47,:770) carrying chat/status/version ONLY, disconnected from the DURABLE events.jsonl bus (FsStore.append_event fs_store.py:578) that bridge /api/stream (bridge.py:2091) already tails seq-cursored. cognition.wave events (cognition.py:1346) ride the durable bus. UNION MOVE: the surface tails events_since(cursor) (fs_store.py:629) and fans those onto its client queues — one bus, not two. This is what makes B3 run-monitor + B11 watch-a-run-climb work AT ALL.
(2) FOUR UNCONVERGED INBOXES = patchwork. coherence findings (findings.jsonl), strategic decisions (decisions/*.py+marks), surfaced approvals (surfaced store) — three stores, three predicates, only `surfaced` triaged (inbox_lanes :6878). UNION MOVE per Tim's law: converge onto ONE surfaced spine with a common {id,kind,name,state,address} envelope — NOT a new aggregator that bridges four stores. dispose_finding/decision_take/resolve_surfaced become three resolvers of one surfaced verb.
OTHER PRINCIPLE HITS:
- registry-not-hardcode: B14 face-from-DNA-tokens is correct; the comment mark types (B8) must come from the company mark_types registry (server.py:1177 gate), not a hardcoded list.
- no-silent-failure: B6 unknown-verb must reject loud; recall determine already honest-empties (recall_determine.py:332).
- translate-to-human-meaning: B11/B14 provenance — every determine claim shows rel_path/anchor/date; surface MUST translate addresses to human meaning, never raw extraction:// to Tim.
- resolution-first: the inbox cards should RESOLVE from typed rows (the surfaced spine), not be hand-built per source.
BUILD SEQUENCE (wireable gradient): warm-suite-at-startup + union-onto-durable-bus FIRST (unblocks run-monitor, recall, determine) -> B5 comment-as-instruction (transport exists) -> one surfaced spine for the inbox -> THEN the new seams: bless-commit (ratify.ts:101 throws by design) + a dragnet-proposal concept (doesn't exist).
