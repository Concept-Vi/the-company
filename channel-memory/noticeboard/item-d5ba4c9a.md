---
id: item-d5ba4c9a
address: board://item-d5ba4c9a
type: block
source: claude_code
state: current
title: F7 · The comments→design process needs ~zero new engine
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-228f99c7
created: '2026-06-25T02:18:09.204706+00:00'
updated: '2026-06-25T02:18:09.204706+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-25T02:18:09.204706+00:00'
  note: filed
---

# The comments→design process maps onto existing primitives — ~zero new engine

Stage-by-stage onto what already runs:
- ingest = `run_items(comment_extractor)`
- cluster = `run_reduce(mode=cluster)`
- synthesize = `run_items` / `run_role`
- vet = cascade `check` step
- verify = `run_jury`
- surface = a flow's `surface_review` (pattern: `flows/floor_walk.py`)

The cascade format is already proven (verify-jury / option-panel / spec-compiler in `cascades.json`). **NET-NEW = a ~50-line flow** (`flows/comments_to_design.py`, mirroring `floor_walk.py`) **+ a ~30-line cascade declaration + maybe one deterministic check** — config, not engine.

Invariants to respect: cascade `op` is constrained (the `kind` field selects the primitive); `run_reduce` doesn't self-persist (the runner does — that's what makes a reduce feedable-by-address); `run://` threading is the only spine (fail-loud on missing); flows are propose-only (no resolve/approve/dispatch, no `claude -p`). This is **"bind, don't build a fleet" made concrete and file-located.**
