---
id: item-0dd81f2c
address: board://item-0dd81f2c
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: F6 · The graph-unification seam
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-228f99c7
created: '2026-06-25T02:18:09.174581+00:00'
updated: '2026-06-25T02:18:09.174581+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-25T02:18:09.174581+00:00'
  note: filed
---

# The graph-unification seam — many layers, not yet one walkable graph

A "unified relation graph" is tracked-but-unbuilt (design debt `board://item-ffb8dac6`).

**Already converges them:** the ONE resolver (nodes), the ONE edge-registry mechanism (vocab), and `territory.py:territory_for` already COMPOSES `resolve_address` + `cc_board.relations` at ANY address — proof a cross-layer walk works *when edges are present*.

**THE BLOCKER = the edge-SOURCE seam:** `cc_board.reverse_traverse`/`relations` only scan `list_items(board_dir)` — board-authored edges only; the field-index triples, the extraction k-NN, and recollection's `file://`/`project://` edges are invisible to it.

**SMALLEST FIRST STEP (the system's own tracked next move):** wire the field-index edges into `relations()` → an address gains typed edges from 2 sources not 1 → the first genuine cross-layer walk, upgrading `territory_for`'s relations leg. **This is the SAME wire as F5-C — F5 and F6 converge on one identical first step.** (Vocabulary-merge — folding `board_edges/` into `relation_types/` — is the deferred-safe, low-value move; the edge-source seam is the real one.)
