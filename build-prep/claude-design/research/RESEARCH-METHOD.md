# Architecture-Visibility Research — the layered method (Tim's steer, 2026-06-08)

> Goal: make the WHOLE application architecture **visible and understandable** so Claude Design (and any
> agent) can design into it and integrate cleanly. Tim's caution: a lot was built, from many angles
> (6 branches + the worktree + the vault) — **don't underestimate the research.** So: layered, by model
> tier, thorough, coverage-guaranteed. This produces the keystone (`APPLICATION-STRUCTURE-PACK.md`) at
> FULL scope — Wave 1 was a 5-agent sampler; this is the complete sweep.

## The layers (cheap → smart → synthesis)

```
LAYER 1 · COVERAGE / INVENTORY   — CHEAP models (Haiku), broad parallel fan-out
   Know WHERE everything is. A complete census of files/folders, classified by a one-line
   "appears to be", with a PRIORITY flag for deep-read and the ANGLE (which branch/worktree/vault).
   NOT comprehension — location. Output: research/inventory/<region>.md.

LAYER 2 · DEEP READ / REPORT     — SMART models (Sonnet/Opus), targeted, keyed off Layer 1
   Understand what's IN the flagged places. Per coherent cluster (module/subsystem/surface):
   what it does, its contracts, components, seams, public surface, state (built/partial/designed),
   how it connects. Coverage guaranteed by Layer 1's map (no guessing where to look).
   Output: research/deep/<cluster>.md.

LAYER 3 · SYNTHESIS              — SMART (Opus)
   Reconcile into the application-structure pack: surface skeletons · component contracts ·
   integration seams · token-slots · conventions+laws — the architecture made visible/understandable.
   Plus a COMPLETENESS CRITIC: what place/angle/claim is missing? → a top-up round if not dry.
```

## Coverage guarantee (so nothing from any angle is missed)
- Layer 1 maps every dir across every angle (the 6 branches + worktree + vault build-prep), not just main.
- Layer 2 must cover every PRIORITY-flagged place from Layer 1.
- Layer 3's completeness critic asks "what angle/place/claim did we not cover?" → loop-until-dry on coverage.

## Layer 1 partition (5 cheap agents — grounded in the real tree)
- **INV-A** runtime/ + store/ + fabric/ + contracts/ + root — the backend core + contracts.
- **INV-B** canvas/ + design/ + panels/ — the FE + the design substrate.
- **INV-C** nodes/ + roles/ + mcp_face/ + voice/ — node-types, cognition roles, the MCP face, voice.
- **INV-D** tests/ + docs/ + ops/ + every AGENTS.md/MAP.md/STATE.md — the self-description + tests + ops.
- **INV-E** THE ANGLES — build-prep/ (repo) + the vault build-prep + the deltas of the 5 non-main
  branches + the company-interface worktree. Where things live across angles.

## Status
Layer 1 launched 2026-06-08 (Haiku ×5). Layer 2 dispatches when the inventory lands + is reviewed.
The studio scaffold (the proving slice) runs in parallel — it proves the pack's USE while this produces
the pack's INPUT at full scope.
