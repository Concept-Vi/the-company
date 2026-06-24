---
id: item-26baf124
address: board://item-26baf124
type: block
source: claude_code
state: current
title: P6 · Option A — Read-only lens (derived projection, Obsidian never writes)
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-80c37615
created: '2026-06-24T05:12:10.238866+00:00'
updated: '2026-06-24T05:12:10.238866+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:10.238866+00:00'
  note: filed
---

### Option A — Read-only lens (derived projection, Obsidian never writes)
The vault is a **regenerated mirror**. Our runtime owns `channel-memory/noticeboard/` as today; a
projector renders a *separate* vault dir (`vaults/company-lens/`) on each board change: one `<id>.md` per
item (or a human-titled file with the id in frontmatter), with `[[…]]` companions emitted from the typed
edges, plus `.base` files for the saved views. Obsidian opens that vault **read-only** (or we simply never
honor its writes). Graph view, backlinks, search, Dataview, Canvas all work on the projection.

- **Truth:** untouched. Zero conflict by construction — there is only one writer.
- **Gain:** every Obsidian read-feature, for free, with no risk.
- **The cost it pays (state it plainly):** it **fails a stated goal.** Tim wants the iOS app + sync as a
  *way in* — annotating from the phone *through Obsidian*. A read-only lens cannot accept a single
  keystroke of input. This is the conservative baseline, not the answer — but it's the correct *floor*:
  if everything else proves too sharp, this still delivers most of the "for free" value.
