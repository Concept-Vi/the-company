---
id: item-95d4dcd3
address: board://item-95d4dcd3
type: block
source: claude_code
state: current
title: B2 · Your assumption was right — channels keep member-registries — richer than
  you thought
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-389c8489
created: '2026-06-23T06:30:09.635371+00:00'
updated: '2026-06-23T06:30:09.635371+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-23T06:30:09.635371+00:00'
  note: filed
---

# Your assumption was right — channels do keep member-registries — and it's richer than you thought

You said *"I believe channels have member registries, if they don't they need them."* They do. And the real one is more capable than you assumed:

- A channel's members aren't just a list of names — each member carries a **participation posture**: **"awake"** (a full participant) or **"listening"** (receive-only, hears but doesn't act). So membership already has a *role-of-presence* built in.
- A member's **live status is never stored** — the system works it out fresh each time by composing three things: what the member *declared* (awake/listening), whether the member is actually *alive* right now, and a live *probe* of whether they're busy or idle. This is the **exact same "never store it, always compose it" pattern** you saw in decisions (mark-is-truth) — applied to "is this member here right now." It refuses to keep a stale "alive" flag that would rot.
- There's a **coordinator** role and a **"conducted" mode** — where *one* session works the others, and the coordinator receives the full picture (who's in the room, their live states, the message). **This is your lead, already built as a concept.** Your structure — "members are AI agents, run by a lead, and the lead is who I talk to" — is *already a first-class mode the channel system supports.* The conductor-works-the-members shape exists.

So when you build member-gated access and member-feeding of dragnets, you're not inventing the member-registry — **you're attaching to one that already tracks posture, liveness, and a lead/coordinator role.**
