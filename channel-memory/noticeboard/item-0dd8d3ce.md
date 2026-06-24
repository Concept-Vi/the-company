---
id: item-0dd8d3ce
address: board://item-0dd8d3ce
type: block
source: claude_code
state: current
title: OB4 · The decisive check + what to reuse
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-156ec226
created: '2026-06-24T05:12:11.435740+00:00'
updated: '2026-06-24T05:12:11.435740+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:11.435740+00:00'
  note: filed
---

# The decisive check (run before building) + what already exists

THE ONE CHECK THAT GATES EVERYTHING TWO-WAY: does Obsidian (Properties UI / sync / plugins) PRESERVE our nested `links:` / `history:` YAML arrays and our closed key order on a round-trip? If it mangles them, two-way is OFF — period — and any future write-back must route through OUR serializer (e.g. an inbox→file_item ingestion path), never Obsidian touching the canonical files.

REUSE (this is largely COMPLETING an existing direction, not greenfield):
- `~/company` ALREADY self-declares as a vault (docs/vault-conventions.md: dual code+vault face, wikilink relations, MAP.md home, a Coherence/freshness gate).
- A `Status Board.base` already exists over type:issue notes.
- `substrate-mcp` (the obsidian-overlord) ALREADY reconciles typed-graph + markdown + wikilinks — possibly the convergence point for our two address-graph engines.
- The canonical "Obsidian Builder" vault ships 17 plugins (Bases, Dataview, Kanban, local-rest-api, git, advanced-uri) + your own vi-chat / realclaudian plugins.
- Gaps: `~/company/.obsidian/` doesn't exist yet; two address-graph engines need converging; typed-address edges aren't native wikilinks.
