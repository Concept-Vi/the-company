---
id: item-7de2f4df
address: board://item-7de2f4df
type: request
source: claude_code
state: done
scope: global
author: session://ch-8djrpmsl
title: clone:// fleet-addressing + reflection-persistence (clones become first-class
  addressed rows)
author_session: ch-8djrpmsl
channel: ''
thread: ''
links:
- kind: authored_by
  target: session://ch-8djrpmsl
created: '2026-06-15T06:43:58.927803+00:00'
updated: '2026-06-15T06:48:36.543003+00:00'
history:
- from: null
  to: open
  by: ch-8djrpmsl
  ts: '2026-06-15T06:43:58.927803+00:00'
  note: filed
- from: open
  to: picked-up
  by: ch-8djrpmsl
  ts: '2026-06-15T06:44:15.922033+00:00'
  note: ''
- from: picked-up
  to: building
  by: ch-8djrpmsl
  ts: '2026-06-15T06:44:16.092763+00:00'
  note: clone:// + reflection-persistence, falsify-first
- from: building
  to: done
  by: ch-8djrpmsl
  ts: '2026-06-15T06:48:36.543003+00:00'
  note: Built+committed 0bdeac3. clone://<source_sid>/<at> addressing + reflection-persistence
    bug-fix (falsify-first 7/7) + get_by_address consumer + op=resolve. 19/19 regression.
    Reflections now durable+addressed; the silent-loss is fixed.
---

Consensus reached (g-1781505586). Tim's A+B unification: clones join the one addressed state. THREE pieces (my cc_clone lane, file-disjoint): (1) BUG-FIX falsify-first: onboard_clone returns the reflection but never PERSISTS it (.data/clones/<h>.json has no reflection field) → the distributed-memory payload is silently lost. Write the reflection onto the clone record. (2) clone:// addressing: clone://<source_sid>/<at> (provenance-stable; at = the cut grammar compact:N|uuid:<uuid>|ts:<iso>, verified address-safe verbatim — no slugify needed). The address = join key over the two handle-files (.data/clones provenance + .data/channels membership), one addressed row, not a 3rd registry. (3) consumer-paired: get_by_address(clone://) → clone+reflection (point-lookup, first consumer); recollection ingests reflection as a unit (semantic fleet-recall, co-built). Cut-token convention → parse_clone_address to lead (contracts.address). clone:// ≠ mind:// (fleet/provenance axis).
