---
id: item-544edc38
address: board://item-544edc38
type: request
source: claude_code
state: done
scope: global
author: session://ch-8djrpmsl
title: 'Heart H1.2: reverse/query traversal on the board (edges-INTO a target + unified
  relations surface)'
author_session: ch-8djrpmsl
channel: ''
thread: ''
links:
- kind: authored_by
  target: session://ch-8djrpmsl
created: '2026-06-15T05:04:09.675114+00:00'
updated: '2026-06-15T05:08:19.917722+00:00'
history:
- from: null
  to: open
  by: ch-8djrpmsl
  ts: '2026-06-15T05:04:09.675114+00:00'
  note: filed
- from: open
  to: picked-up
  by: ch-8djrpmsl
  ts: '2026-06-15T05:04:31.371485+00:00'
  note: Fork self-assigns (lead-assigned via channel, exclusive cc_board.py access
    for H1.2).
- from: picked-up
  to: building
  by: ch-8djrpmsl
  ts: '2026-06-15T05:04:40.614935+00:00'
  note: Building reverse_traverse + relations in cc_board.py, mirroring traverse's
    fail-loud + resolve_address hydration. Falsify-first on real genesis items.
- from: building
  to: done
  by: ch-8djrpmsl
  ts: '2026-06-15T05:08:19.917722+00:00'
  note: Built + committed 70e0e8a. reverse_traverse + relations (in/out/both), structural-by-default
    + optional hydrate; 12/12 incl. proof-by-use on the REAL board (found+hydrated
    the item-15aaf9da→item-e523b30d promoted_from chain). Falsify-first caught relations(out)
    eager-resolve → fixed to structural. traverse (H1.1) untouched.
---

Builds ON H1.1 (commit 68c7eda: resolve_address one-resolver + cc_board.traverse forward-edges). H1.2 = the inverse + query side, in cc_board.py (fork exclusive access, lead won't touch concurrently): (1) reverse_traverse(target_addr, kind=None) → all board items carrying a link {kind, target==target_addr}, matched on the OPAQUE target string (no resolution for the match — projection-over-rows like manifest()); (2) a unified relations(addr, direction in/out/both, kind) surface — edges-into + edges-out-of as one small query (the seed find_relations generalizes; reuse the edge registry + resolve_address for hydration, NOT a parallel engine). Proof-by-use on real genesis items (shared authored_by + the promoted_from chain); fail-loud on unregistered kind; results hydratable via resolve_address. clone-cacc9e8b's ranked next-after-H1.1. Pure C/foundation (Tim's turn-back).
