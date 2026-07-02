---
id: item-e7c8946c
address: board://item-e7c8946c
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P11 · One-line takeaways for the host-idea
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-861627e3
created: '2026-06-24T05:12:10.803410+00:00'
updated: '2026-06-24T05:12:10.803410+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:10.803410+00:00'
  note: filed
---

## One-line takeaways for the host-idea

- **The convention layer is already written** (`docs/vault-conventions.md`): repo = code + Obsidian vault, dual-face, link-carried relations, declared home note. The host idea *completes* this, it doesn't start it.
- **The board rendering already has a working template** (`Status Board.base` over `type:issue` notes) — point a `.base` at `type:note` board items and the phone/desktop board view appears for free.
- **substrate-mcp is the proof + the parser** for reconciling typed-graph + markdown + semantics; study it before designing the edge bridge.
- **The first concrete, reversible step** is instantiating `~/company/.obsidian/` from the existing Obsidian Builder config + the `obsidian-vault-agent:init` scaffolding — purely additive, our runtime stays master, Obsidian becomes a second lens immediately.
