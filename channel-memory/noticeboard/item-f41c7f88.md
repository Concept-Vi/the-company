---
id: item-f41c7f88
address: board://item-f41c7f88
type: block
source: claude_code
state: current
title: P2 · 1. The three vaults (and which one matters)
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-861627e3
created: '2026-06-24T05:12:10.556001+00:00'
updated: '2026-06-24T05:12:10.556001+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:10.556001+00:00'
  note: filed
---

## 1. The three vaults (and which one matters)

| Vault | Path | What it is | Relevance |
|---|---|---|---|
| **Obsidian Builder** | `/home/tim/vaults/Obsidian Builder/` | The CANONICAL live vault (per memory rule `feedback-canonical-vault-is-obsidian-builder`). 265+ notes, Spaces/, Tags/, Canvas files, `.base` files. | This is where the *plugins + config + conventions* to reuse live. |
| **vi-vault-design** | `/home/tim/vaults/vi-vault-design/` | DEPRECATED design vault (same memory rule). Near-identical file set (it's the ancestor). The `.mcp.json` in Obsidian Builder still points its `obsidian` MCP at **this** path — a stale pointer worth noting. | Reference only; do not build on. |
| **`~/company` (the repo)** | `/home/tim/company/` | **Already self-declared an Obsidian vault** — see below. This is the actual board substrate. | THE target. |

**The canonical-vault memory rule is real and load-bearing:** `Obsidian Builder` is the sole canonical Vi vault; `vi-vault-design` is deprecated. Any "plug Obsidian in" work should treat Obsidian Builder as the conventions/plugin reference and `~/company` as the substrate being hosted.

---
