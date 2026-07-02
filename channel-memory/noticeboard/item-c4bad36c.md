---
id: item-c4bad36c
address: board://item-c4bad36c
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P6 · 4. The substrate-mcp — the address-graph MCP (most architecturally relev
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-861627e3
created: '2026-06-24T05:12:10.667314+00:00'
updated: '2026-06-24T05:12:10.667314+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:10.667314+00:00'
  note: filed
---

## 4. The substrate-mcp — the address-graph MCP (most architecturally relevant)

Source: `/home/tim/repos/obsidian-overlord/` (the `substrate-mcp` is a *submodule/dir* there). Launchers installed at `~/.local/bin/substrate-mcp`, `substrate-mcp-status`, `substrate-mcp-scan`. Exposed as the **`substrate-mcp__*` MCP toolset** (90+ tools: `search_semantic`, `get_by_address`, `traverse_links`, `get_neighborhood`, `get_vault_schema`, `cluster_by_embedding`, `add_vault`, `reindex`, etc.).

Per its own `ARCHITECTURE.md`, substrate-mcp turns a markdown vault into **three coupled stores**:
1. **address-graph** (SQLite) — every file/dir at a `filesystem://<vault>/<rel>` address, with parent_id, frontmatter, sha256.
2. **autopoietic type-graph** (SQLite) — types *discovered from frontmatter* (`type:`, `layer:`, `body/`).
3. **semantic face** (Chroma) — local Ollama embeddings (`nomic-embed-text`).
Kept fresh by a **filesystem watcher** (watchdog). Resumable scans, sha256 skip.

**Why this matters for "host not master":** substrate-mcp is *already* the pattern of "a custom address+type+semantic graph projected OVER a folder of markdown, treating the markdown as canonical truth and everything else as a projection." That is structurally the SAME shape as the company runtime's `board://` resolver over `channel-memory/noticeboard/*.md`. There are now **two address-graph engines** over markdown in Tim's world (company runtime + substrate-mcp) — a duplication/convergence question, not a missing piece.

**The crux mismatch is partly already solved here:** substrate-mcp parses **wikilinks out** AND frontmatter into a typed graph. It reconciles "markdown for Obsidian" with "address-graph for agents" — exactly the typed-address-edges-vs-`[[wikilinks]]` tension flagged in the question. Worth studying its parser before re-deriving a bridge.

---
