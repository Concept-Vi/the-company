---
id: item-d02d74aa
address: board://item-d02d74aa
type: block
source: claude_code
state: current
title: P8 · 6. The agent/skill layer already built around vaults
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-861627e3
created: '2026-06-24T05:12:10.721998+00:00'
updated: '2026-06-24T05:12:10.721998+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:10.721998+00:00'
  note: filed
---

## 6. The agent/skill layer already built around vaults

- **`obsidian-vault-agent` plugin** (`~/.claude/plugins/cache/obsidian-vault-agent/.../1.0.0/`): ships 4 sub-agents (`vault-editor`, `vault-researcher`, `vault-synthesizer`, `vault-writer`), 13+ skills (`init`, `process`, `recall`, `deep-research`, `synthesize`, `vault-graph`, `paper-discover`, `youtube`, `lecture`, `course`, `slide-maker`), and **hooks**: `validate-frontmatter.sh`, `protect-obsidian.sh`, `protect-templates.sh`, `on-compact.sh`. The `init` skill *creates an agent-ready Zettelkasten vault with CLAUDE.md + MCP config + hooks* — reusable scaffolding for instantiating `~/company/.obsidian/`.
- **The `obsidian:*` skills** (built-in): `json-canvas`, `obsidian-bases`, `obsidian-cli`, `obsidian-markdown`, `defuddle` — first-class authoring of `.base`, `.canvas`, wikilinks, callouts, frontmatter.
- **Obsidian Builder's own `CLAUDE.md` + `_system/` registry** (in vi-vault-design lineage): a *self-describing* vault where `_system/types.md`, `processes.md`, `principles.md`, `status.md`, `registry-protocol.md`, `typed-fences.md`, `codegraph-protocol.md` ARE the operating system. Notably it already invented a **Typed Fence Substrate** (`<format>:<kind>` fenced blocks: `json`/`ndjson`/`yaml`/`events`) for persisting structured data IN markdown — directly relevant to "typed edges in a markdown host."

---
