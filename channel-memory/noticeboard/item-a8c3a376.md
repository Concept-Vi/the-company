---
id: item-a8c3a376
address: board://item-a8c3a376
type: block
source: claude_code
state: current
title: S6 · Routing as a typed registry (the throwaway 'lead' fully redone)
author_session: lead
channel: operator-surface
thread: ''
links:
- kind: part_of
  target: board://item-ed91000e
created: '2026-06-28T11:35:00.205760+00:00'
updated: '2026-06-28T13:05:39.774395+00:00'
history:
- from: null
  to: current
  by: lead
  ts: '2026-06-28T11:35:00.205760+00:00'
  note: filed
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T12:56:17.667014+00:00'
  note: v2 MERGE rewrite (in place)
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T13:03:19.355091+00:00'
  note: restore v1 content dropped in v2 rewrite
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T13:05:39.774395+00:00'
  note: fold corroboration corrections (3 unbiased agents)
---

S6 · Routing — REWRITE (v1 named a nonexistent fn)
DECISION (Tim): the 'lead' dotfile was a throwaway test stub — totally redo; routing is TYPED; target = ANY member in ANY channel, MORE THAN ONE at once.
v2 REALITY: TWO un-unified modules — cc_channels.py (file-registry, port-POST transport; send=ONE recipient :380; find :152; live_sessions :94; group channel_members :459 but NO send path reads it) vs session_channels.py (event-folded; post_to_channel :468 FANS TO MANY natively = Tim's 'more than one'). THE BRIDGE USES session_channels ONLY (bridge.py:1573,1682,2701); imports cc_channels nowhere. (v1's cc_channels.resolve_and_send DOES NOT EXIST — drop it.)
v2 RIDE: /api/channel/post (bridge.py:2695 → post_to_channel) for fan/any-channel; /api/channels (1569) the roster; /api/channel-history (1674). The typed route registry rides session_channels.
COMPANY-IMPROVEMENT #2 (verified): two recipient namespaces (cc_channels port-POST members vs session:// session_channels members) are UN-UNIFIED → Tim's any-member-any-channel needs ONE roster + ONE fan router; unify on session_channels; cc_channels.is_shared = Supabase publish-boundary only (cc_channels.py:480-486).
RESTORED(v1) — THE ROUTE-KIND VOCABULARY (the feature, not just the transport): the typed route registry's KINDS = `session`(a named member) · `coordinator`(the channel's coordinator slot) · `broadcast`(all members of a channel) · `cascade`/`dragnet`(route the message INTO a computation — safe) · `queue`(drop for whoever's-next to claim, via the mail leaf) · `spawn`(S6b) — and the fan-to-many kinds ride session_channels.post_to_channel. PER-CHANNEL DEFAULT route replaces the dotfile stub. COLLAPSE: 'lead/coordinator/named-session' (three different things today) become ONE inspectable route registry. Routing is typed (shares the registry grain with mark_types).
CORRECTED: cc_channels.channel_members is :557 (459 = create_channel). #2 ORDERING HAZARD: 12 modules import cc_channels (cc_retire/channel_boundary/cc_attachments/session_supervisor/surface_server…) — NOT a thin demote; and session_supervisor.py:1640 uses cc_channels.send for the LIVE no-polling injection Tim said STAYS (post_to_channel only fans MAIL intents + relies on the supervisor to inject — it is NOT a direct port-push). So #2 CANNOT go foundational/first — demote cc_channels only AFTER the live-injection transport has migrated.
