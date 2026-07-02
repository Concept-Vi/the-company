---
id: item-1c3b121f
address: board://item-1c3b121f
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P8 · 6 · Point-straight vs Mirror — the cross-cutting decision (Axis A)
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-4baaab55
created: '2026-06-24T05:12:09.440813+00:00'
updated: '2026-06-24T05:12:09.440813+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:09.440813+00:00'
  note: filed
---

## 6 · Point-straight vs Mirror — the cross-cutting decision (Axis A)

| | **A1 · Point straight at `channel-memory/noticeboard/`** | **A2 · Mirror into a vault folder** |
|---|---|---|
| Data freshness | Live; zero lag; one copy. | Needs a sync (rsync/symlink/watcher); a second copy to keep honest. |
| `.obsidian/` pollution | **Drops `.obsidian/` into the git-tracked company repo.** Must gitignore it or it churns the repo. **[Observed]** repo is git-tracked. | Vault config lives in the mirror, repo stays clean. |
| Two-writer risk | Maximal — Obsidian sits *on* the canonical files. | Contained — Obsidian writes to the mirror; a one-way sync (store→mirror) makes it structurally read-only. |
| iOS / sync (the whole point — mobile) | A vault buried inside the company git repo is **awkward to reach with Obsidian's iOS app + Obsidian Sync.** Tim's note (memory): the synced vault he actually uses lives Windows-side; WSL paths don't get mobile sync. **[Observed memory]** | A standalone mirror folder is exactly what Obsidian Sync/iCloud expects → mobile lights up cleanly. |
| L2 enrichment safety | Body mutation touches canonical files. | Enrichment happens in the mirror — canonical files never change. |
| Effort | Lowest to *start* (just open the folder). | One sync component; but every later layer is safer. |

**Reading:** A1 is the fastest demo and the truest "one copy of the data." A2 is the safer home for anything beyond L0/L1 and is **the natural fit for the mobile/iOS goal** — which is the entire point of this project. A one-way (store → mirror) sync turns A2 into a structurally-read-only lens, which is the cleanest possible expression of "host not master."

---
