---
type: terrain-entry
name: counterpart
register: descriptive
aliases: ["counterpart", "Design DNA Pack", "DNA", "design"]
path: /home/tim/repos/counterpart
relation: connected
kind: work
status: unconfirmed
created: 2026-06-13
last_active: 2026-06-22
size: 920M
coverage: { files_read: 6, files_total: 1582, last_read: 2026-06-26 }
git_remote: none (working dir); inner design/ is git, master +93 vs origin/main
connection_evidence: ONLY thing in ~/repos referencing ~/company — 4 doc/comment path-pointers to /home/tim/company/runtime/{ui_claude_session,territory}.py + build-prep DECISION-CARD-HOST-CONTRACT.md (verbatim below)
depends-on: ["[[company]]"]
relates-to: ["[[vi-visual-bridge]]"]
secrets: false
move_intent: none
tags: ["#dna", "#fabric"]
---

# counterpart

## What it is
A design/spec workspace for the Company's **identity layer** — the "Design DNA Pack". The real project lives one level down at `/home/tim/repos/counterpart/design/`; the working-dir root holds only `design/` and one backup tarball.

Self-description (`/home/tim/repos/counterpart/design/PROJECT.md` §0, verbatim):
> "A **compositional assembly system** — a *language* — that lets a **parametric, type-based engine** plus **integrated AI workflows** generate interfaces, content, and copy in the company's **identity**."

`design/CLAUDE.md` frames the repo itself as "an addressed, typed, queryable substrate" with its own address-registry / wayfinder / graph. The orienteering claim (design/spec workspace for the operator surface / decision-card host / RHM voice / DNA) is accurate: DNA tokens→registries→templates→dials are the spine, and the operator-surface / decision-card / RHM-voice pieces appear as the consuming surfaces (refs below).

## How it works
Not a runnable service — a design substrate of docs + a surface renderer (`design/surface/runtime/unit-view.js`) + token/registry material. `design/` is git-tracked (branch `master`, **+93 commits ahead of origin/main**; recent commits are `DNA-REPO-FACTS:` entries).

## What it connects to
**counterpart is the ONLY thing in `~/repos` that references `/home/tim/company`.** All four refs are documentation/comment path-pointers (NOT `import` statements) — prose pointers to live Company files the design work reads from or must plug into. **2 distinct runtime files + 1 build-prep contract (cited twice):**

1. `/home/tim/repos/counterpart/design/surface/runtime/unit-view.js:105` — host contract the decision-card renderer must satisfy:
   > `// /home/tim/company/build-prep/the-one-application/DECISION-CARD-HOST-CONTRACT.md`
2. `/home/tim/repos/counterpart/design/docs/command/VOICE-STANDARD-SPEC.md:24` — RHM voice corpus source:
   > `**PANEL_BRIEFING** — /home/tim/company/runtime/ui_claude_session.py (the RHM's live system voice-instruction; the current spoken-prose rules).`
3. `/home/tim/repos/counterpart/design/docs/command/VOICE-STANDARD-SPEC.md:25` — RHM prose-framing source:
   > `**territory_prose framing** — /home/tim/company/runtime/territory.py (the "What this is / The decision / The options are" scaffold the RHM speaks from).`
4. `/home/tim/repos/counterpart/design/docs/command/DECISION-SEQUENCE-SURFACE-DESIGN.md:119` — build-prep host contract again:
   > `/home/tim/company/build-prep/the-one-application/DECISION-CARD-HOST-CONTRACT.md (projection, 7 numbered items, ...)`

Refs #2/#3 cite the two runtime files as the "as-is corpus to EXTRACT his spoken voice from" for the RHM voice spec. Refs #1/#4 cite the build-prep contract the design's decision-card renderer must plug into (`unit-view.js` notes the bespoke renderer was RETIRED 2026-06-19 in favor of the generic archetype). Relation = **connected** (aimed-at + shared-corpus), not external.

## When / where
- **Path:** `/home/tim/repos/counterpart`
- **created:** ~2026-06-13 (project era; backup tarball dated 2026-06-13). Oldest file mtime `2024-12-20` is an ingested source deck (`Company Info, Products & Strategy.pdf`), not project creation.
- **last_active:** 2026-06-22 (`design/docs/command/DNA-REPO-FACTS.md`; last commit 2026-06-22 21:44).
- **size:** 920M (413M tarball + ~341M git-ignored reference/source assets).
- **files_total:** 1,582 (working tree, excl node_modules + .git); 5,565 incl .git; **files_read:** 6.

## Notes / evidence
- **Git nuance:** the `counterpart/` working dir is NOT a git repo (`git status` → fatal), but the inner `design/` IS (master, +93 vs origin/main). Record both.
- **Backup tarball:** `/home/tim/repos/counterpart/design-backup-2026-06-13.tar.gz` = 432,905,637 bytes → 413M on disk (the "433M" figure is decimal-MB).
- Verified: PROJECT.md, CLAUDE.md, and the cited line-context of all 4 company refs (unit-view.js, VOICE-STANDARD-SPEC.md, DECISION-SEQUENCE-SURFACE-DESIGN.md). All four claimed company targets confirmed verbatim.
