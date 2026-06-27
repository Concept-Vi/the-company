---
type: terrain-entry
name: dot-vi
register: descriptive
aliases: ["dot-vi"]
path: /home/tim/.vi
relation: external
kind: config
status: unconfirmed
created: 2026-03-02
last_active: 2026-06-17
size: 224K
coverage: { files_read: 3, files_total: 31, last_read: 2026-06-26 }
git_remote: none
purpose: the cross-session frame doc — auto-loaded into every Claude session as active instructions
language: markdown
relates-to: ["[[company]]", "[[company-systemd]]"]
secrets: false
move_intent: none
tags: [fabric]
---

# dot-vi

## What it is
The cross-session frame: a small vault of markdown that is auto-loaded into EVERY Claude Code session as active instructions (the `~/.vi` shared-context directory). It holds Tim's canonical architecture frame and the cross-session channel launch rules.

Evidence (Observed): `CLAUDE.md` (2026-06-17) states "Tim's canonical architecture frame (2026-06-17). Hold this as canonical" and names the four layers — DNA=identity, FACTORY=type builder, GALLERY=content/scenes, and "THE COMPANY (`~/company`) = ADDRESS RESOLUTION + MODELS + everything else — the substrate all layers resolve through." Other files: `IDENTITY.md`, `PROJECTS.md`, `REGISTRY.md`, `TELESCOPE_*.md`, `TIM.md`, plus `rules/` and `build-ideas/`.

## How it works
Static markdown, loaded by the Claude Code harness as a shared-context directory (per the global CLAUDE.md: "any CLAUDE.md or rules/*.md in `~/.vi` become active instructions automatically"). `rules/cross-session-channels.md` (Observed) documents launching fabric sessions via `~/company/channels/` — `claude --mcp-config /home/tim/company/channels/channel.mcp.json … server:company-channel`, with handles registered at `/home/tim/company/.data/channels/<handle>.json`, and names `channels/company_channel.mjs` (the channel MCP server) + `channels/channel.mcp.json`.

## What it connects to
- `[[company]]` — its `CLAUDE.md` names the Company as the substrate layer (DNA/FACTORY/GALLERY all resolve through it); the address spine + model routing are "the COMPANY layer".
- `[[company-systemd]]` (indirectly via the fabric) — `rules/cross-session-channels.md` launches sessions against `~/company/channels/`, the cross-session messaging mesh.

## When / where
Path `/home/tim/.vi`, 224K, 31 files. Files span 2026-03-02 (`README.md`) to 2026-06-17 (`CLAUDE.md`, `rules/`). created 2026-03-02, last_active 2026-06-17.

## Notes / evidence
Read: `CLAUDE.md` in full; `rules/cross-session-channels.md` grepped for the launch wiring; directory listing. NOT read: the `TELESCOPE_*`, `PROJECTS`, `REGISTRY`, `IDENTITY` bodies in full. This is config (frame/instructions), not data — it shapes how sessions orient to the Company.
