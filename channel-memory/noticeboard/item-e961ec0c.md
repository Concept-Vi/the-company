---
id: item-e961ec0c
address: board://item-e961ec0c
type: block
source: claude_code
state: current
title: P14 · Ranking by value-for-effort (the honest spread, not a convergence)
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-3480c157
created: '2026-06-24T05:12:10.003043+00:00'
updated: '2026-06-24T05:12:10.003043+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:10.003043+00:00'
  note: filed
---

## Ranking by value-for-effort (the honest spread, not a convergence)

| Rank | Feature | Plug-in | Read/Write | Value to Tim (phone, non-dev) | Effort / gate |
|---|---|---|---|---|---|
| 1 | **Instant search** | Clean | Read | High — find anything, instantly, offline | ~Zero (needs title pass for legible results) |
| 2 | **Bases (.base)** | Clean (fields) / blind (edges) | Read | High — tappable filtered/grouped card views, no code, native mobile | Low — already in vault; needs files reachable + title pass |
| 3 | **iOS app + Sync** | Clean (reading) | Read (+Sync writes) | **Highest** — the whole "from my phone" intent | **High gate** — WSL files aren't synced; needs Windows-side mirror + conflict story |
| 4 | **Dataview** | Clean (fields) | Read | Medium — power queries, but desktop + query language | Low-med (plugin); Bases supersedes for Tim |
| 5 | **Graph / backlinks** | **Partial, lossy** | Read (needs dual-write to show anything) | Tempting but **misleading** — loses edge `kind`, omits cross-address targets | Med + frame-risk; our own graph is the right home |
| 6 | **Properties UI** | Partial (flat only) | **Write** | Low — display scalars; can't safely edit nested edges | Frame-risk (two-writer) |
| 7 | **Canvas / Templates / most plugins** | None | mixed | ~None for machine-generated flat items | Skip |

---
