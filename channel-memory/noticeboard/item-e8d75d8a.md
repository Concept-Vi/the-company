---
id: item-e8d75d8a
address: board://item-e8d75d8a
type: block
source: claude_code
state: current
title: C4 · Net-new + footguns + COMPANY-improvements to fold (the universalising
  lens)
author_session: lead
channel: operator-surface
thread: ''
links:
- kind: part_of
  target: board://item-5c0698ed
created: '2026-06-28T12:23:39.955090+00:00'
updated: '2026-06-28T12:23:39.955090+00:00'
history:
- from: null
  to: current
  by: lead
  ts: '2026-06-28T12:23:39.955090+00:00'
  note: filed
---

GENUINELY NET-NEW (build): outbound device PUSH (wake a closed phone — NO VAPID/web-push/APNS/service-worker anywhere in the repo; SSE only reaches a foregrounded app) · annotate EDIT/DELETE door on the bridge (/api/annotate is create-only) · artefact per-element pinning anchored on ui:// addresses (not client-side CSS paths) · author-identity attribution · tailnet exposure of the bridge.
COMPANY-IMPROVEMENTS TO FOLD INTO SCOPE (per convergence methodology — fix in the centre, not work around):
  1. NO channel field on events/vectors/findings/marks/annotations/surfaced — 'channel' is a read-time fold, so the SSE bus CANNOT be server-side channel-filtered. Fix: stamp a channel field at emit (the mailbox to/from/verb/thread, fs_store.py:1394, is the model). UNIVERSAL — helps all channel-scoped reads, not just the surface.
  2. DUAL channel registry: session_channels (event-folded, bridge uses) vs cc_channels (file-registry, gates Supabase publish via is_shared). Unify on session_channels as canonical; is_shared = publish-boundary flag only.
  3. Process-local event seq (fs_store.py:589-596) can dup across processes — MERGE (single writer) largely dissolves it; otherwise apply the mailbox's cross-process lock.
  4. TOKEN axes: design/_system/tokens.json + emit.py is the single warm-DARK spine with NO light/dark/density axes; design/claude-ds is an unmerged island that HAS data-theme (light/dim/dark/contrast) + data-density. Build those axes INTO tokens.json/emit.py (islands-join-mainland) — a phone-vs-desktop surface NEEDS them.
  5. FRONTMATTER_KEYS closed set — verify (thin in the map); reconcile against registry-driven item/source/edge types, not a hardcoded key list.
FOOTGUNS (surface-local, fix in the merge): tim.json dual-registration; full-board rescan (surface_server.py:225-237 — repoint at /api/board); the os.remove delete bypass.
