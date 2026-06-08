---
status: scout-read-only
date: 2026-06-08
worktree: /home/tim/company-studio-extract
branch: studio-extract
---

# Scout Report: studio-extract Worktree

## What studio-extract IS

**Abandoned parallel studio build** — a detached lineage of the studio work (the design-review Review.tsx surface + StudioKit.tsx components + bridge mockup serving) that is **6 commits ahead** of the lead's operable-interface-build scaffold, diverged from main before the concurrent-cognition merge landed.

The worktree shows:
- Same Review.tsx, StudioKit.tsx, Composer, Rail, Stage, RhmPanel structure as operable-interface-build (identical code, byte-for-byte through first 80 lines each)
- Same vite.config.ts proxy expansion (adds /mockups + /design-system.css routes)
- Same bridge.py serving (mockup gallery corpus, feedback JSONL path-safe serving)
- **6 unique commits ahead** — all studio-focused (revert of a route drop, route cleanup, proxy wiring, studio scaffold, feedback route, mockup rendering)
- Entire concurrent-cognition merge incorporated
- 60+ build-prep docs committed (Completion Criteria, Implementation Guide, Research Synthesis, broader/, explore/, decisions, handoff notes)

## Lineage vs Lead's Scaffold (operable-interface-build)

| Metric | Result |
|--------|--------|
| **operable-interface-build → studio-extract** | studio-extract is 6 commits AHEAD (those studio commits) |
| **studio-extract → operable-interface-build** | operable-interface-build has 3 commits studio-extract lacks (redownloaded from git, different SHAs) — they are **different commits with identical messages** |
| **vs main** | studio-extract: 6 ahead, main: 1 ahead (the mode-dial unify) — **DIVERGED** |
| **Code diff (main..studio-extract)** | Only docs + design mockups + minimal surface wiring (vite proxy, bridge routes); **zero unique code** beyond operable-interface-build |
| **Collision risk** | None — all studio code is already in operable-interface-build |

## The Critical Finding

**The studio-extract branch is NOT a superset.** It's a parallel fork that diverged BEFORE the mode-dial unify landed on main. Its studio commits (cb471aa through 314221d) would need to be cherry-picked or re-applied if kept; they don't linearly rebase onto current main because main has evolved past their base.

operable-interface-build has **semantically identical studio implementation** (same Review surface, same StudioKit primitives, same seam contracts), so the studio code is not lost — it just exists under the lead's branch.

## What studio-extract Adds (Unique)

- **Build-prep documentation bundle** — 60+ files of design decisions, research synthesis, broader context, exploration notes, Phase-1 plan. These are VALUABLE for future reference but exist in `/build-prep/` and are better kept in the vault (canonical source per README.md).
- **Revert commits** — a back-and-forth on the `/api/mockup-feedback/status` flip route (commit 7cf145c dropped it, 314221d reverted the drop). This is noise; the decision on whether to keep or drop the route should be settled once on main.

## Recommendation: DISCARD

**studio-extract should be discarded** — keep operable-interface-build as the studio lineage. Here's why:

1. **Zero unique code** — the studio surface (Review, StudioKit, bridge.py proxy routes) is already in operable-interface-build, identical, verified-by-use
2. **Stale branch** — diverged before the mode-dial unify; cherry-picking its 6 commits introduces noise and re-decision (the revert shows uncertain closure)
3. **Docs belong in vault** — the build-prep docs are valuable but should live in the canonical vault (`/mnt/c/Users/Workstation001/Documents/Claude/Projects/counterpart/the Company/build-prep/`), not as committed code
4. **Merge risk** — attempting to fold studio-extract into operable-interface-build or main would require careful cherry-picking, adding friction for zero new capability
5. **operable-interface-build is the operative lineage** — it's the one Tim signalled for merge (SESSION-OPERABLE-INTERFACE.md documents it, merge plan live); studio-extract is artifact of an earlier exploratory pass

**Keep operable-interface-build; delete studio-extract.** The studio work is complete and in the right place.
