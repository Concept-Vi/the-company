# Operator Surface — BUILD STATE (resume-here after restart)

> Survives WSL restart (files on ext4 persist; only processes die). Read this + COMPLETION_CRITERIA.md to pick up the loop exactly.

## Where the loop is (2026-06-29)
- **Loop-prep: COMPLETE** — the three docs in this dir (RESEARCH_SYNTHESIS · IMPLEMENTATION_GUIDE · COMPLETION_CRITERIA). Committed.
- **Foundation beat F3: DONE + verified + committed** (790739b) — board frontmatter is open (new typed fields persist); acceptance: `tests/board_open_fields_acceptance.py` (7/7).
- **NEXT in priority order** (Phase 1 foundation, autonomous): **F1** (channel on events → `/api/stream` channel-scoping), **F4** (light/dark/density token axes into design/_system/tokens.json+emit.py), **F5** (single-writer event invariant). Then **F2** (unify channel registries — only AFTER the live-injection transport migrates). Then Phase 2 shell (B2/B3/B1/B4), Phase 3 projects/self (P1/P2), then the core loop.
- **The full itemised plan + status**: COMPLETION_CRITERIA.md (truth-table, two-faced). The board mirror: `operator-surface` channel — v2 plan `item-ed91000e` (S0–S15), connection map `item-5c0698ed`, parts-harvest `item-3865097a`.

## Parallel work (convergence — another session is on the same centre)
- HEAD is `d03fb44 identity fusion: one principal registry (agent/viewer) + grant store` — a DIFFERENT session is building company-improvements (the principal/grant/auth work, related to B4 + S6b). My F3 is safely in history below it. **On resume: re-read recent git log + the board before driving F1/F4 — another session may have advanced or touched the same files.** Don't clobber; fuse.

## What SURVIVES the restart (no action needed)
- All git history incl. F3 (790739b) + the loop docs. The ~180 uncommitted working-tree files (mine + parallel) — files on disk, survive (just uncommitted). The board store (`channel-memory/noticeboard/` + `.data/store/`). All memory (`~/.claude/.../memory/`). The orienteering ledger, the recollection move, the build-prep docs.

## What DIES (ephemeral; relaunch only if wanted — none hold unsaved state)
- `:8421` — the upward-engine map viewer (`python3 -m http.server`, scratchpad). Harmless; relaunch only to re-view that artifact.
- `:8783` / `:8791` — `ops/surface_server.py` (the standalone prototype) + its tailscale serve. **This is the island being RETIRED in v2** — do NOT bother relaunching it; the build replaces it.
- `:8782` — another python (not mine).

## Post-restart, before continuing the loop
1. Confirm the **bridge is up** (`:8770` — the one warm Suite the loop rides). The company services may be systemd auto-start or need `company up`. The loop's bridge-riding features need it warm.
2. Re-read git log + the `operator-surface` board (parallel session may have advanced).
3. Resume at the NEXT item above (F1), per COMPLETION_CRITERIA priority order. Foundation = autonomous; the face/taste + the rule-engine-dispatch edit = walk through Tim.
