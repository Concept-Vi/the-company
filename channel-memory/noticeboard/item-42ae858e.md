---
id: item-42ae858e
address: board://item-42ae858e
type: block
source: claude_code
state: current
title: S12 · The face — serve from tokens now, document for the DNA merge
author_session: lead
channel: operator-surface
thread: ''
links:
- kind: part_of
  target: board://item-ed91000e
created: '2026-06-28T11:35:00.315186+00:00'
updated: '2026-06-28T13:05:39.861091+00:00'
history:
- from: null
  to: current
  by: lead
  ts: '2026-06-28T11:35:00.315186+00:00'
  note: filed
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T12:56:17.775440+00:00'
  note: v2 MERGE rewrite (in place)
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T13:03:19.419497+00:00'
  note: restore v1 content dropped in v2 rewrite
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T13:05:39.861091+00:00'
  note: fold corroboration corrections (3 unbiased agents)
---

S12 · The face — MERGE into the bridge's served tokens
DECISION (Tim): serve the face from compiled tokens (kill hardcoding); document the seam for the DNA merge.
v2: RIDE design/_system/tokens.json via emit.py (the warm-gold spine, served as CSS vars like the bridge serves /studio); replace the surface's stale hardcoded palette. WRITE DOCS at the token-serve seam.
COMPANY-IMPROVEMENT #4 (verified): tokens.json has NO light/dark/density axes; the claude-ds ISLAND has them (tokens/theme.css:16-21 data-theme light/dim/dark/contrast; tokens/density.css:33-39 data-density). FIX = build those axes INTO tokens.json/emit.py (islands-join-mainland), reconciling default polarity (claude-ds light-default vs mainland warm-dark). A phone-vs-desktop surface NEEDS the axes.
RESTORED(v1): THREE token layers — tokens.json (mature, served) · claude-ds (the axes island) · the Visual-DNA VAULT (a design SOURCE CORPUS, NOT a token generator — don't wire the surface to it; it's material a human/agent distills tokens FROM). Also: ALIAS the surface's var names to token roles during the merge so existing var() refs resolve.
CORRECTED: '/studio' is a 302 REDIRECT to one mockup file (bridge.py:1428-1437), NOT a generic static mount — there is no static-serve precedent, so serving surface/app/dist (or canvas/app) FROM the bridge is NET-NEW. #4 polarity: theme.css has NO light default (only dim/dark/contrast, all dark-family) → the merge is ADDITIVE, not a light-vs-dark polarity clash; the earlier 'reconcile polarity' framing was wrong.
