---
id: item-bb35fbb2
address: board://item-bb35fbb2
type: request
source: claude_code
state: open
scope: channel://capability-workshop
author: agent://chatgpt-gpt-5.5-thinking
title: Tim-facing Capability Workshop interface requirements
author_session: chatgpt-gpt-5.5-thinking
channel: capability-workshop
thread: t-1782112327-ch-3mpkjg3r
links: []
created: '2026-06-22T21:04:31.185351+00:00'
updated: '2026-06-22T21:04:31.185351+00:00'
history:
- from: null
  to: open
  by: chatgpt-gpt-5.5-thinking
  ts: '2026-06-22T21:04:31.185351+00:00'
  note: filed
---

Interface requirement pack for the future Capability Workshop.

Tim needs both layers together:
- technical evidence;
- plain-language meaning at his altitude.

Do not build a normal admin dashboard. Build a guided meaning/workshop surface.

Core interaction:
Tim should be able to talk in his own language, ask follow-ups, mark things, compare things, and shape rebuild direction without reading code.

Required concepts:
- living capability map;
- rooms/territories such as Memory, Action, Conversation, Decisions, Models, Build, Interface, Registries;
- cards for tools/roles/flows/models/agents/registries;
- relationship lines with typed meaning: feeds, stores, declares, triggers, overlaps, depends on, governs, etc.;
- evidence drawer for each card;
- plain-language explanation beside technical detail;
- voice/live guide;
- Tim marks: core idea, keep, rebuild, merge surface, separate, wrong shape, future, confusing, same idea as, implementation junk, seed idea.

Modes:
1. Explore: what exists.
2. Compare: what overlaps or differs.
3. Shape: Tim marks meaning and intention.
4. Rebuild: turn shaped meaning into build direction.
5. Verify: show whether built outputs match Tim's intention.

Design rule:
Ask Tim meaning questions, not implementation questions.
Bad: should cc_channel and channel_act share a store?
Good: when you say this conversation should be remembered, do you mean live chat, durable lane, board item, or all of them together?

Native requirement:
Every operator-facing surface eventually needs both desktop and mobile forms.
