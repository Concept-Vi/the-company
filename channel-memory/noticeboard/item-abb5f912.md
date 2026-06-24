---
id: item-abb5f912
address: board://item-abb5f912
type: block
source: claude_code
state: current
title: P6 · 4. "Membership gates delivery, not access" + three channel systems = the
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-eb5d71e7
created: '2026-06-24T01:32:20.722935+00:00'
updated: '2026-06-24T01:32:20.722935+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:20.722935+00:00'
  note: filed
---

### 4. "Membership gates delivery, not access" + three channel systems = the access model is a new subsystem, sequenced wrong

B3/B4 are the most honest part of the design map, and they quietly describe a large build:

- **Three separate channel stores** that "mirror each other's shapes" but are authoritative for nothing in common. The brief's own B5 says converging them is "likely a prerequisite." Translation: **before "post to a channel and members act" is even well-defined, you must pick/merge channel systems** — a refactor that touches live messaging, the work-group coordinator, and the external-boundary DB simultaneously. That is not a side quest.
- **Data-access-by-membership does not exist** (B4, verified-as-stated by the brief itself). The reassuring spin — "your open default is already the current reality, you just build the restrict mechanism" — hides that *the restrict mechanism is a permission system that doesn't exist*, and that the moment external clients (ChatGPT, system 3, "closed by default") are in scope, "everything is open" is a **security problem, not a convenience.** Tim's envelopes can contain code locations, file paths, and screenshots of his unreleased system. "Open by default" across a boundary system is how that leaks.

**The trap:** the brief lets you build the phone UI on top of channels/membership *as if access were solved*. It isn't, and the convergence it depends on is the kind of cross-cutting refactor that strands work (and Tim's memory note says ~/company has no branches and no merge orchestration — so a half-done channel convergence stalls the whole repo).
