---
type: terrain-entry
name: obsidian-overlord
register: descriptive
aliases: ["obsidian-overlord", "substrate-mcp", "vi-substrate"]
path: /home/tim/repos/obsidian-overlord
relation: connected
kind: engine
status: unconfirmed
created: 2026-05-19
last_active: 2026-06-26
size: 9.2G
coverage: { files_read: 4, files_total: 11831, last_read: 2026-06-26 }
git_remote: git@github.com:Concept-Vi/obsidian-overlord.git
connection_evidence: operational/runtime — no code import; shared MCP substrate (substrate-mcp tools live in Company Claude sessions), pointed at the same pplx-embed-context-4b embedding endpoint as the Company
relates-to: ["[[cache-company]]", "[[counterpart]]"]
secrets: false
move_intent: none
tags: ["#mcp", "#embedding", "#memory"]
---

# obsidian-overlord

## What it is
The repo folder is named `obsidian-overlord`, but the package IS **`substrate-mcp`** — a local-only MCP server that indexes markdown vaults into three coupled stores and exposes tools for AI agents to read / search / write / configure against them.

- `/home/tim/repos/obsidian-overlord/pyproject.toml:2` → `name = "substrate-mcp"`
- `pyproject.toml:4` (description): "Substrate-conformant MCP server over an Obsidian-style markdown vault — address-graph, type-graph, semantic face (Chroma + Ollama), filesystem watcher, parametric read/write/config tools."
- `README.md:3-7`: "indexes a markdown vault into three coupled stores (an address-graph, an autopoietic type-graph, and a Chroma semantic face) ... Filesystem watcher keeps everything fresh."

This is the live `substrate-mcp__*` tool surface available inside Company Claude sessions (the same tools appear in this session's deferred-tool list: `mcp__substrate-mcp__search_semantic`, `get_by_address`, `reindex`, etc.).

## How it works
- **MCP server entry point:** `substrate-mcp = "substrate_mcp.server:main"` (`pyproject.toml:19`).
- **CLI entry points:** `substrate-mcp-scan`, `substrate-mcp-status` (`pyproject.toml:20-21`); bash wrapper `/home/tim/repos/obsidian-overlord/substrate-mcp` runs `.venv/bin/python -m substrate_mcp.cli`.
- **Source:** 14 modules under `/home/tim/repos/obsidian-overlord/src/substrate_mcp/` (server, db, parser, scanner, watcher, embeddings, schema_profiler, docs_gen, issues, report, config, cli).
- **48 tools** exposed (8 config, 4 destructive, 1 feedback, 30 read, 3 read-remote, 2 write) per `README.md:85` (README prose still says "24"; the generated count is 48).
- **Stores:** SQLite `.state/substrate.db` (tables: `addresses, chunks, headings, wikilinks, types, type_assignments, vaults, vault_schemas, sessions, session_events, state_history, scan_log, block_ids`) + per-vault Chroma collections under `.state/chroma/`.
- **Embeddings (live, switched off README default):** `/home/tim/repos/obsidian-overlord/.state/config.json:155-157` → `embedding_provider: "openai"`, `embedding_model: "perplexity-ai/pplx-embed-context-v1-4b"`, `ollama_base_url: "http://localhost:8007/v1"`. This is the same pplx-embed-context-4b model recorded in the Company's embedding-model decision.

## What it connects to
**Relation = connected (operational/runtime, NOT code).** `grep -rn "home/tim/company"` across the whole repo (all file types, excluding node_modules/.git/.venv) returned **zero matches** — there is no code import, config entry, or doc reference in either direction, and `/home/tim/company` is not one of its indexed vaults. The wiring is operational: substrate-mcp loads as an MCP server in the same Claude sessions the Company runs in, and it is pointed at the same local pplx-embed-context-4b embedding endpoint (`localhost:8007`) the Company uses.

**Canonical vault:** there is no single canonical vault — **10 vaults are registered** in the `vaults` table (`vi-context-design, _issues, visual-dna, elevenlabs-mcp, visual-design-corpus, ulm-inventory, unification-vault, claude-code-atlas, claude-platform-docs, relative-difference`). The installer default is `relative-difference` → `/mnt/c/Users/Workstation001/Documents/Claude/Projects/Relative difference/universal-mechanics`. Index scale: **9,790 addresses, 116,726 chunks**.

## When / where
- **Path:** `/home/tim/repos/obsidian-overlord`
- **created:** 2026-05-19 (earliest = only commit, `2026-05-19 18:49:03 +1000 "Initial commit"`).
- **last_active:** 2026-06-26 — `.state/substrate.db` (5.4G) mtime is today with a 70MB WAL; config last edited 2026-06-16; CHANGELOG to 2026-06-12. The system is genuinely live.
- **size:** 9.2G (dominated by `.state/`: 5.4G `substrate.db` + `chroma/` with ~40 sub-collections).
- **files_total:** 11,831 (excl node_modules/.git); **files_read:** 4 (`README.md`, `pyproject.toml`, `.state/config.json`, the `substrate-mcp` wrapper) + DB queried + dir listings.

## Notes / evidence
- **Git "last_active" is misleading** — a single initial commit (2026-05-19) and nothing since. All subsequent runtime + content (DB to today, config to 06-16, CHANGELOG to 06-12, issues to 06-10) is **uncommitted drift**. Per honest-status: flag substantial uncommitted runtime+content drift on this repo.
- Verified: `pyproject.toml`, `README.md`, `.state/config.json`, `vaults` table query. Coverage is thin on source modules (read by listing, not line-by-line).
