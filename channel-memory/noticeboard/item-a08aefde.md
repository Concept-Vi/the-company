---
id: item-a08aefde
address: board://item-a08aefde
type: block
source: claude_code
state: current
title: P10 · 8. Quiet platform/ops realities the brief never costs
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-eb5d71e7
created: '2026-06-24T01:32:20.896939+00:00'
updated: '2026-06-24T01:32:20.896939+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:20.896939+00:00'
  note: filed
---

### 8. Quiet platform/ops realities the brief never costs

- **It's Tailscale-only HTTPS to a workstation (CTX1).** Offline tolerance + optimistic UI + the draft queue surviving a dropped tunnel (BD-F "phone, flaky network") means real local persistence (IndexedDB) and a sync/reconcile layer — another subsystem, and one that interacts badly with mark-is-truth (what happens to a locally-queued draft when the board moved underneath it on reconnect?).
- **"Invitations / codes" to spin up Claude Code members (BD-E)** = session-spawn / clone with identity. Tim's own memory rules (`autonomous-spawn-lead-only`) say sub-agents must NOT fire `claude -p` autonomously. So "Tim's phone mints a code that spawns an acting agent" runs straight into a standing safety rule. Unresolved.
- **The connector-client identity gap (BD-E):** an external client "currently has no session." Routing replies *back to Tim's phone overlay* from an arbitrary member assumes a return path that the three-channel split (B4) hasn't settled.

---
