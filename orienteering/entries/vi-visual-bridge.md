---
type: terrain-entry
name: vi-visual-bridge
register: descriptive
aliases: ["vi-visual-bridge", "Vi-Wizard", "vi-visual-frontend"]
path: /home/tim/vi-visual-bridge
relation: connected
kind: work
status: unconfirmed
created: 2026-02-23
last_active: 2026-06-22
size: 1.3G
coverage: { files_read: 6, files_total: 9936, last_read: 2026-06-26 }
git_remote: git@github.com:Concept-Vi/vi-wizard.git
connection_evidence: no code import; fabric-only — FORMATION_JOURNAL Entry 68 (2026-06-22) records the LEAD (ch-3mpkjg3r) re-pointing this lane at the Company front interface/centre via company-channel
aimed-at: ["[[company]]"]
relates-to: ["[[counterpart]]"]
secrets: false
move_intent: none
tags: ["#fabric"]
---

# vi-visual-bridge

## What it is
**"Vi-Wizard"** — a "polymorphic visual interaction system that bridges AI agents and Tim through Chrome" (`/home/tim/vi-visual-bridge/README.md:1`). It is NOT a Chrome extension (no `manifest.json` exists) — it is a bridge server + MCP server + embedded Chrome single-page UI. Three names coexist: folder `vi-visual-bridge`, product **Vi-Wizard**, npm package `vi-visual-frontend` (`package.json:2`, "Frontend bundle for vi-visual-bridge — markdown rendering extension stack").

## How it works
- **MCP server:** `mcp/src/index.ts` (HTTP+SSE, port 7732) — `README.md:27-31`.
- **Bridge server:** `server.py` (HTTP API + embedded Chrome UI in `get_html()`, port 7731).
- Deployed via `./deploy.sh`. Frontend bundle = marked / katex / mermaid / shiki / react.

## What it connects to
**Relation = connected (fabric-only, NOT code).** `grep -rn "home/tim/company"` over `*.js/*.ts/*.json/*.md` (excl node_modules) returned **zero hits** — no code import. The connection is session/coordination-level:

- **FORMATION_JOURNAL Entry 68 — 2026-06-22** (`/home/tim/vi-visual-bridge/FORMATION_JOURNAL.md:3521`):
  > "Entry 68 — 2026-06-22 — Re-mobilized; verified the direction circuit ALREADY composes through DNA's renderArchetype... **Provenance:** fabric (lead ch-3mpkjg3r, t-1782116358): re-mobilizing my lane (direction circuit + gallery binder). Framing (islands-join-mainland): build good parts INTO the centre, drop parallel scaffolding — ONE surface, not a parallel app... Blockers→lead not Tim."
- The "Company front interface" framing was set earlier in **Entry 21 — 2026-06-16** (`:1205`): "he CHANGED THE FRAME: the redesign target is now the Company front interface" + "build via Claude Code + channel, 'no Tim gating.'"
- The **company-channel fabric** is the delivery mechanism (`:781`, Entry 13 — 2026-06-12, primary-source observation of a `company-channel` MCP injecting a fabric message + `reply` tool). The LEAD relays (ch-al7jdfdr Entry 14, ch-3mpkjg3r Entry 68) arrive through this channel.

This is the islands-join-mainland pattern in action: the bridge's good parts get absorbed INTO the Company centre, dropping parallel scaffolding.

## When / where
- **Path:** `/home/tim/vi-visual-bridge`
- **created:** 2026-02-23 (earliest commit `2026-02-23 10:28:07`, "the birth").
- **last_active:** 2026-06-22 — **nuance:** committed *code* froze at `2026-03-29 02:10:16` (last of 73 commits); live agent *session activity* (the uncommitted FORMATION_JOURNAL, Entries 68-71) ran to 2026-06-22. State = dormant (code) with recent session re-mobilization.
- **size:** 1.3G (dominated by node_modules). **files_total:** 9,936 (excl node_modules/.git); **files_read:** 6.

## Notes / evidence
**Name reconciliation — "vi-visual-dev" does NOT map to this folder.** It is a separate, Windows-side repo = the FACTORY layer, distinct from this bridge.
- `ls -d /home/tim/vi-visual-dev` → does not exist (no Linux-home folder by that name).
- `/home/tim/.vi/CLAUDE.md:10`: "**FACTORY = the TYPE BUILDER** — composition / `vi-visual-dev`. Registries + types are made here."
- `/home/tim/.vi/projects/vi-visual-dev.md:3`: Repository = `/mnt/c/00_ConceptV/06_Project_Vi/repos/vi-visual-dev` (Windows C: via WSL), GitHub = `Concept-Vi/vi-vision` (note: `vi-vision`, NOT `vi-wizard`). "Multi-agent coordination infrastructure + visual development overlay."
- This bridge's own journal lists it as a **sibling, not self** (`FORMATION_JOURNAL.md:29`, `:94`): "Siblings: visual-factory (home `/mnt/c/00_ConceptV/06_Project_Vi/repos/vi-visual-dev`...)".

The three Vi layers (per `.vi/CLAUDE.md`) map to three distinct repos:
| Layer | Name in `.vi` | Actual location | GitHub |
|---|---|---|---|
| FACTORY (type builder) | `vi-visual-dev` | `/mnt/c/00_ConceptV/06_Project_Vi/repos/vi-visual-dev` (Windows) | `Concept-Vi/vi-vision` |
| DNA (identity) | `counterpart` | `/home/tim/repos/counterpart` | — |
| this repo (Vi-Wizard / bridge) | `vi-visual-bridge` | `/home/tim/vi-visual-bridge` | `Concept-Vi/vi-wizard` |

Verified: README.md, package.json, `.vi/projects/vi-visual-dev.md`, `.vi/CLAUDE.md`, targeted FORMATION_JOURNAL entries (13, 14, 21, 68-69), 5 grep sweeps.
