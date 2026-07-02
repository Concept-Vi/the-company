---
id: item-7ad77ae2
address: board://item-7ad77ae2
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: A4 · The dragnet engine — your questions answered definitively, plus what the
  agents added
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-389c8489
created: '2026-06-23T17:13:52.421611+00:00'
updated: '2026-06-23T17:13:52.421611+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-23T17:13:52.421611+00:00'
  note: filed
---

# The dragnet engine — your questions answered definitively, plus what the agents added

**The gating (confirmed, exactly):** a rule, not a model. Parse the file mechanically → if it's real code with functions inside → deep read; otherwise → one-liner. Your design files are "assets," so the rule *structurally* never deep-reads them. Confirmed by the engine's own code and by the agent independently.

**What the agents added that you should know (thinking for you):**

- **There are actually *two* dragnet engines, not one.** One reads code (the one we've been discussing). The other reads *transcripts and documents* — and **it already has a "design" reading stage** built into it, for pulling design-meaning out of content. So "a design lens / purpose-specific reading" is **not from scratch** — there's already precedent for a dragnet having a special stage for a specific purpose. The pattern you want exists in a sibling; it just isn't in the code engine or generalized.

- **The depths and budgets *are* adjustable** — there are knobs for how deep, how many words, what to include, date ranges, which folders. What's *not* adjustable is the gating *rule itself* (the "only code gets deep" decision is frozen). So "configurable dragnets" is partly there (the knobs) and partly not (the frozen rule about what deserves depth). Your point 4 is really: *make the frozen rule a chooseable lens.*

- **The law you set earlier is in the code:** "a dragnet is the entire thing except what's explicitly excluded," with every exclusion recorded with a reason. That's baked in. Your law stuck.

- **Binary things already have an address scheme** (`blob://` for images/audio) — so when vision comes, the *storage and addressing* for what it sees is already there; what's missing is the *seeing reader*, not the place to put what it sees.
