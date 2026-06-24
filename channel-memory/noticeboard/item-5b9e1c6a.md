---
id: item-5b9e1c6a
address: board://item-5b9e1c6a
type: block
source: claude_code
state: current
title: P5 · 3. Plugins already installed (Obsidian Builder loadout)
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-861627e3
created: '2026-06-24T05:12:10.640040+00:00'
updated: '2026-06-24T05:12:10.640040+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:10.640040+00:00'
  note: filed
---

## 3. Plugins already installed (Obsidian Builder loadout)

`/home/tim/vaults/Obsidian Builder/.obsidian/plugins/` — 17 plugins, the directly relevant ones:

| Plugin | What it gives "for free" | Bite / note |
|---|---|---|
| **dataview** | Live queries over frontmatter — the legacy query engine. | Path/tag-based, not address-based. |
| **obsidian-local-rest-api** | **HTTP API into the vault** (port 27124 TLS, key in `.../obsidian-local-rest-api/data.json`). A live write/read path our runtime could call. | API key is plaintext in config; TLS cert self-signed. A real second-writer channel. |
| **advanced-canvas** | Enhanced `.canvas` (the JSON Canvas format). | Tim uses Canvas heavily (20+ `.canvas` files). |
| **obsidian-kanban** | Board/Kanban view over notes — **directly relevant to "board"**. | Kanban stores its own markdown; column = a field. |
| **obsidian-tasks-plugin** | Task/checkbox querying across vault. | |
| **obsidian-advanced-uri** | `obsidian://` deep-links to any note/command — a way for OUR surface to jump INTO Obsidian. | The inbound-link bridge. |
| **omnisearch** | Fuzzy full-text instant search. | |
| **templater-obsidian** | Templated note creation (frontmatter scaffolding). | Matches our id-keyed file creation. |
| **obsidian-git** | Auto-commit/sync the vault via git. | `~/company` is git already → natural fit. |
| **obsidian42-brat** | Beta-plugin loader (how Tim ships his own plugins). | |
| **obsidian-mind-map**, **calendar**, **custom-slides**, **obsidian-icon-folder**, **obsidian-style-settings** | mind-maps, calendar, slides, folder icons, theming. | |
| **vi-chat** (custom) | **Tim's own plugin** v10.1.249 — "Context-aware AI chat sidebar for vault operations." Has its own `src/`, MCP registration, TTS cache, boot-trace. `isDesktopOnly:false` (mobile-capable). | A purpose-built in-vault AI surface Tim authored. Big asset — overlaps with "our front end." |
| **realclaudian / Claudian** (custom) | v2.0.16 — embeds **Claude Code / Codex as collaborators inside the vault**, vault as working dir. `.claudian/sessions/`. `isDesktopOnly:true`. | Means agents already run *inside* the vault context. |

**`.base` files are in active use** — Obsidian Bases (the newer native DB-view engine, successor to Dataview):
- `Dashboard.base` — table/work-queue/by-layer views with **formulas** (`age_days`, `needs_work`, `layer`) grouping by `processing_status`.
- `Spaces/Mobile Parity/02 Status Board.base` — an **issue tracker board**: filters `note.type == "issue"`, severity/triage sort formulas, "Breaking First / By Category / Open Only" views.

That Status Board.base is *almost exactly* the board-as-vault pattern already realized for a different domain (mobile-parity issues). It's a working template for rendering our `board://` items as a Base.

---
