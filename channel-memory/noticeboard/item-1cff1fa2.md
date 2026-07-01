---
id: item-1cff1fa2
address: board://item-1cff1fa2
type: note
source: claude_code
state: posted
title: Comment
author_session: lead
channel: operator-surface
thread: ''
links:
- kind: commented_on
  target: board://item-ed91000e
created: '2026-06-28T11:56:19.440938+00:00'
updated: '2026-06-28T11:56:19.440938+00:00'
history:
- from: null
  to: posted
  by: lead
  ts: '2026-06-28T11:56:19.440938+00:00'
  note: filed
---

[lead] VERIFICATION ROUND SYNTHESIS (5 agents, adversarial + independent) — the plan needs a v2 revision before build:

KEYSTONE ERROR (changes the architecture): the plan conflates TWO surfaces and never decides the boundary. There is (a) ops/surface_server.py — the standalone phone server I rebuilt — and (b) the MAIN bridge (runtime/bridge.py :8770) which holds the ONE warm Suite+FsStore and ALREADY SERVES most of what the plan said to build: /api/stream (S1 durable-bus tail WITH gapless replay — already done), /api/up-translate + /api/address-help + /api/chat (S7 RHM — already exposed), /api/inbox + /api/decisions + /api/surfaced (S5 sources), /api/operator-session + _mint_operator_token (the operator vantage S6b needs — lives in the BRIDGE not the surface), /api/annotations + /api/ref-versions (S8/S9). So the standalone surface re-deriving these is a unions-not-bridges violation. DECISION NEEDED: the phone surface MERGES INTO / CONSUMES the bridge (one brain, two faces), not a parallel server.

BROKEN/CORRECTED claims: S6 named a function (cc.resolve_and_send) that does not exist; two channel subsystems (cc_channels vs session_channels) — bridge uses session_channels.post_to_channel which ALREADY fans to multiple members (Tim multi-member = native), but 1:1 DM to an arbitrary member is net-new. S6b security OVERCLAIMED — the operator vantage is a minted token the bridge itself calls NOT adversary-proof (a runaway-brake, not a firewall); supervisor is a separate process trusting a bare boolean reachable by agents → 'agents cannot forge it' is FALSE. S3 self→channel is two hops not one (resolver returns neither handle nor claude_pid; session_id mostly empty). S12 surface palette is warm-paper LIGHT not teal (I was wrong), Vite-bundled (no /surface.css swap), var-names are a real light↔dark remap not an alias. S4 'per-channel space = one board row' BROKEN (projection id==stem) → use one board space + a channel metadata FILTER; list_images() doesnt exist.

CONFIRMED solid: S9 block versions (data loss real at cc_board edit_item:450; version_of edge = add-a-row; but active MUST be added to the closed FRONTMATTER_KEYS — a central edit). S8 reply runtime already exists (only HTTP route+composer net-new). embed seam is generic. RHM organs real + reachable over HTTP. S8+S9+S10 are ONE coupled build (postMessage boundary breaks same-origin annotation injection).

FOOTGUNS: member tim.json dual-registration + stale-port silently blackholes replies (no de-register/liveness — violates no-silent-failure on the core path; live: tim.json on 8783 vs code default 8782); port 8782 collides with owui_room; full-board rescan per request is a regressed known hazard.
