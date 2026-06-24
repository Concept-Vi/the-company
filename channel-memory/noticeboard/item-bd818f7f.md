---
id: item-bd818f7f
address: board://item-bd818f7f
type: block
source: claude_code
state: current
title: P14 · Does "host not master" actually hold — or quietly invert?
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-48cd6801
created: '2026-06-24T05:12:11.229288+00:00'
updated: '2026-06-24T05:12:11.229288+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:11.229288+00:00'
  note: filed
---

## Does "host not master" actually hold — or quietly invert?

**My honest read: it does not hold by default, and it inverts silently, in three creeping ways:**

1. **Write races invert ownership de facto** (§1.1): whoever wrote last wins, and sync writes last
   often. The master loses writes it thinks it made. Ownership inverts not by decision but by timing.
2. **Schema drift makes Obsidian the de-facto formatter** (§1.2): once Obsidian reorders/normalizes
   YAML on every touch, the *canonical on-disk form* is whatever Obsidian last emitted, not what
   `_render` intended. Our `sort_keys=False` stable order is gone; Obsidian's serializer is now the
   shape of truth.
3. **Dialect accretion makes Obsidian load-bearing** (§3.1): bodies fill with Obsidian-only syntax
   until the data can't be faithfully rendered without it.

"Host not master" can **only** hold if enforced in code, not by promise. The minimum enforcement the
grounding doc does NOT yet have:
- A **single-writer discipline**: either the runtime owns the files and Obsidian is mounted **read-only**
  (hard to truly enforce on mobile), OR Obsidian writes to a **separate projection/export** vault that
  is regenerated *from* the master and **never read back** (one-way mirror — the only clean "lens").
- **Version/CAS on writes** (an `updated`/hash check before overwrite) so a stale sync write is
  *rejected loud* instead of clobbering — currently absent.
- **Schema-guard on read**: tolerate/repair Obsidian's reordering and normalize-back on our next
  write, and quarantine (Gap + Notice) any file that fails parse rather than letting fail-loud nuke
  the node from the human's view.

The cleanest honest answer: **the only "host not master" architecture that survives contact is the
one-way projection** — master → generated read-only Obsidian mirror, Obsidian never writes canonical
data. The two-way "Obsidian is a second editor on the live files" version is the one that bites in
every tier above, and it bites hardest in exactly Tim's environment (mobile, sync, phone-driven edits).

---
