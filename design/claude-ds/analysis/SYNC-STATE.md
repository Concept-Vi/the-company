# SYNC-STATE — repo ↔ cloud "ConceptV Design System" (projectId c8f43c46-ed08-42df-9a4e-3a23e4697262)

_Last reconciled: 2026-07-12, session 1fbd0fe1 (counterpart/design lead). Method: full byte-level
diff of the repo working tree against a complete DesignSync text-file mirror
(`/home/tim/company/.build-container/phase-b-served/ds-cloud-mirror/`, `_COVERAGE.tsv` = audit),
then reconciled against the LIVE `list_files` inventory (~1,050 paths incl. binaries)._

## The finding
The repo and the cloud project are ONE system that diverged — NOT two systems.
337 shared text paths, 331 byte-identical at reconcile time. The cloud was ahead by the
block/skin/studio wave; the repo was ahead by the glyphic-language/W-wave (its git history).

## What is now SYNCED (text level — complete except _qa remainder below)
- **cloud→repo**: 76 files landed, commit `c1e3206` (tokens/{skins,material,device}.css · 8 axes ·
  core/ 7 engines · app/registry 10 · app/ai 4 · system/ 9 (studio, block-system, skin-system,
  inspector, …) · specimens/glass-gallery 15 · components/ 7 · assets brand/materials-manifest/
  renders-prompts/roles-json · analysis 5 · _ingest/ICON-AUDIT.md).
- **repo→cloud**: 28 files pushed via DesignSync plan `plan_c8f43c46ed0842df_63e44c59417a`,
  round-trip verified on cv-edges.js: the 19 `_demo/` verify/gen scripts + glyphic-board.html +
  README, `assets/icons/{ConceptVIcon.jsx,icon-paths.js}`, `face-index.js`, and the 6 diverged
  files resolved REPO-WINS (analysis/FINDINGS-LOG.md, app/ai/{ai-glyphic-language,ai-registry}.js,
  app/registry/relationships-seed.js, assets/icons/{cv-edges,cv-meaning}.js — the repo had
  deliberately evolved past the cloud copies, e.g. cv-edges' `means:` strings were consciously
  dissolved into CV_MEANING per R1b; nothing cloud-side needed merging back).
- **_qa probes**: glyph-only, zone-probe, frame-probe, test .html pulled cloud→repo.

## What REMAINS UNSYNCED (cloud-only, absent from the repo)
1. **~14 `_qa/*-test.html` harness pages** (text, pullable via DesignSync any time):
   archetype-test, bridge-test, core-test, cr-test, cv-node-test, decorators-test, glyphic-test,
   mark-compare, meta-test, perpart-test, popover-test, studio-test, vi-glyph-test, views-test.
2. **~600+ binaries** the repo has never had: `_qa/` screenshots (~330) · `_ingest/` source
   images (~250) · `uploads/` (~100) · `inspo/` · `screenshots/` · `assets/{textures, materials/*,
   renders/*.png, roles/*, icons/svg (~150 SVGs — these are text but numerous), illustrations,
   logos, maps, reference, _staging, brand-marks}` · template/root `.thumbnail`s.
   **Hard constraint**: DesignSync `get_file` caps at 256 KiB and routes content through model
   context — unusable for bulk binary transfer. Binary sync needs another channel (export from
   the Claude Design app, or an upload-side bridge). Until then, repo pages referencing
   `../assets/renders/*.png`, textures, etc. will not render locally.
3. `atomicity/.gitkeep` (repo-only, trivial, not pushed).

## Consequence for the mapping/integration work
The ADDRESS MAP of the system can proceed now — all structure-bearing text is synced both sides.
The binary assets are addressed leaves; record their addresses from the live list_files inventory
without transferring bytes. The visual-quality pass on repo-served pages needs the consumed
assets (renders/textures/roles/svg icons) landed locally first.

## UPDATE 2026-07-12 (same session, later): binary recovery pass
**550 binaries recovered locally, zero cloud transfer** (commit 9f5067f):
- `_ingest/` 158 — sources matched from counterpart `review/ingest/` + `source/dump/assets/icons/`
- `assets/` +246 (icons incl. jpg boards, illustrations, logos, reference) + `inspo/` 22 + `uploads/` 10
  + `_qa/` 120 — all from the ConceptV-handoff export at
  `counterpart/design/reference/ConceptV Design System-handoff/conceptv-design-system/project/`
  (an older cloud export; files land at their original project relpaths).

**Remaining cloud-only (needs a cloud channel):**
- assets/textures (~40) · assets/materials/* PBR maps (30) · assets/renders/*.png (10) ·
  assets/roles (~30) · assets/maps (5) · assets/icons/svg (~150, text) · assets/_staging (17) ·
  assets/brand-marks (6)
- newer _qa screenshots (~250 incl. _qa/shots) · screenshots/ (~60) · newer uploads/ (~90,
  the pasted-*/ChatGPT images) · _ingest cloud-extracted (60: image12-62.png, Frame*.svg, p-1b) ·
  ~14 _qa/*-test.html harnesses · 2 .thumbnail
- CHANNELS: (a) a project export/download from the claude.ai Design app if it exists — gets
  everything at once; (b) a dedicated DesignSync transfer session pulling base64 one-at-a-time —
  works only ≤256 KiB/file (2048² PBR maps and renders likely exceed it); (c) the `claude_design`
  MCP (https://api.anthropic.com/v1/design/mcp) registered in user config — its tools load in a
  NEW session after OAuth; unknown whether it adds bulk transfer beyond DesignSync's methods.
- Handoff-recovered files predate the live project state; a `list_files` re-check should verify
  none were since deleted/renamed cloud-side (strays would show as repo-only).

## FINAL 2026-07-12: SYNC COMPLETE (commit 2902cec)
Tim exported the project from the claude.ai Design app (ConceptV Design System-handoff zip,
1,496 files / 351MB). Landed wholesale; 189 divergences resolved by three-way against the
Jul-10 mirror baseline (84 cloud-advanced + 105 cloud-owned taken; 0 repo-ahead; 0 conflicts;
the 6 Jul-10 repo-wins pushes round-tripped back byte-identical — push confirmed).
VERIFIED: 1,496/1,496 export files present + hash-identical in the repo.
Repo-only extras: .gitignore, atomicity/.gitkeep, this record (also pushed to cloud).
**The repo and the cloud project are now ONE, byte-level.** Future divergence prevention =
the fabric-integration mapping (two-engines plan agreed with Tim: counterpart substrate
machinery over claude-ds as project root × the DS's own registries as the symbol level).
