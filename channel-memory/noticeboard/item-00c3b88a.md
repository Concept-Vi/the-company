---
id: item-00c3b88a
address: board://item-00c3b88a
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P7 · 5. Access paths into the vault (already wired)
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-861627e3
created: '2026-06-24T05:12:10.695079+00:00'
updated: '2026-06-24T05:12:10.695079+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:10.695079+00:00'
  note: filed
---

## 5. Access paths into the vault (already wired)

Three independent ways IN already exist — reuse, don't rebuild:
1. **MCP (semantic/structural):** `substrate-mcp__*` tools (add the company vault via `add_vault`, then `search_semantic` / `get_by_address` / `traverse_links`). Plus the bare `obsidian` MCP in Obsidian Builder's `.mcp.json` (`@mauricio.wolff/mcp-obsidian`, currently pointed at the deprecated vault).
2. **REST (live read/write into a *running* Obsidian):** `obsidian-local-rest-api` on `https://localhost:27124`, key on disk.
3. **CLI + deep-links:** the `obsidian-cli` (Bash) per memory rule `feedback-obsidian-mcp-preference`, and `obsidian://` URIs via advanced-uri for inbound jumps from our surface.

Memory rule `feedback-obsidian-mcp-preference`: Tim **prefers Obsidian MCP tools** for read/write/search/patch where they fit; the CLI stays capable as fallback.

---
