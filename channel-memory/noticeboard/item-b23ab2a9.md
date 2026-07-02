---
id: item-b23ab2a9
address: board://item-b23ab2a9
type: block
source: claude_code
state: current
scope: channel://operator-surface
author: agent://lead
title: S4 · Search — make the board + attachments searchable by meaning
author_session: lead
channel: operator-surface
thread: ''
links:
- kind: part_of
  target: board://item-ed91000e
created: '2026-06-28T11:35:00.169553+00:00'
updated: '2026-06-28T13:05:39.757401+00:00'
history:
- from: null
  to: current
  by: lead
  ts: '2026-06-28T11:35:00.169553+00:00'
  note: filed
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T12:56:17.635450+00:00'
  note: v2 MERGE rewrite (in place)
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T13:03:19.322027+00:00'
  note: restore v1 content dropped in v2 rewrite
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T13:05:39.757401+00:00'
  note: fold corroboration corrections (3 unbiased agents)
---

S4 · Search — make the board + attachments searchable (RIDE the engine)
DECISION (Tim): boards searchable now (+ attachment types); allow BOTH scopes — default caller's channel (S3), params for specific/range/all.
v2: RIDE the bridge's existing search doors — /api/transcript-search (bridge.py:1618 → determine recall_determine.py:278), /api/corpus-query (1747 → query_index vector_index.py:143), /api/session-recall (1640). Board content is UNINDEXED today.
BUILD (small): projections/board.py (one row, embeds:True) + ops/embed_board.py sweeping cc_board.list_items() + cc_images enumeration (NOTE: list_images() does NOT exist — enumerate via cc_images) → {source_address=board://|image://, text} → the EXISTING embed_corpus_to_spaces. Attachments: images via alt/caption; other types need a text rep (transcript/OCR) — per-type adapter.
SCOPING FIX (v1 was wrong): per-channel-space != one board row (a projection id must == its file stem, projections.py:38; embed refuses unknown projections). USE one `board` space + a channel METADATA FILTER on the vector record (fs_store put_vector has no channel field today — additive). Default = caller's channel (S3); project-search = fan-out over channels.
RESTORED(v1): TUNABLE — which embedder, which space, and WHAT-gets-indexed are config/rows, not hardcoded (everything-configurable). REUSE also the corpus tool's rerank (jina :8008) + read (open a board:// hit) — not just nearest-neighbour.
CORROBORATED + CAVEAT: /api/transcript-search (bridge.py:1618, ?q required) → determine REUSES the WARM resident Suite (~11s warm vs >60s cold). Riding it depends on the bridge staying warm — a fresh/cold process hits the cold path. (Matrices build LAZILY on first query, bridge.py:461-476 — first-hit latency + concurrent-first-hit race.)
