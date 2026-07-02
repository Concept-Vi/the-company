---
id: item-36fde950
address: board://item-36fde950
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P11 · 5 · The options on the three axes (side by side, not converged)
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-80c37615
created: '2026-06-24T05:12:10.377615+00:00'
updated: '2026-06-24T05:12:10.377615+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:10.377615+00:00'
  note: filed
---

## 5 · The options on the three axes (side by side, not converged)

| | A · Read-only lens | B · Runtime-reconciler | C · Parallel + inbox | D · Vault = canonical dir |
|---|---|---|---|---|
| **Identity law intact?** | ✅ fully (no writes) | ✅ runtime mints all truth | ✅ planes separated | ⚠️ only if filename stays `<id>.md` AND YAML survives |
| **Two-writer conflict?** | none (one writer) | append=zero conflict; in-place=LWW+history | none on projection; intake is additive | raw file race; sync vs git; key-order churn |
| **iOS write-back?** | ❌ (fails stated goal) | ✅ full (edit + annotate) | ✅ for new annotations (the common case) | ✅ but on the riskiest substrate |
| **Code to build** | projector + view-gen | projector + validating ingest watcher | projector + inbox replay | almost none (and that's the trap) |
| **Reversibility** | trivial (delete vault) | high (truth never left runtime) | high | low (Obsidian now in the truth path) |

Read across, not down: **A** is the safe floor that sacrifices input; **B** is the most capable and the
truest to mark-is-truth, at the cost of a real ingest path; **C** is B's conflict-free physical subset and
is arguably the most *aligned* with mark-is-truth (you annotate, you don't overwrite); **D** is a shortcut
that quietly trades mastership for convenience and must clear the §4 check first.

---
