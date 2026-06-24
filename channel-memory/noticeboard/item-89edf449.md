---
id: item-89edf449
address: board://item-89edf449
type: block
source: claude_code
state: current
title: P7 · Option B — Two-way, RUNTIME-as-reconciler (the strong candidate)
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-80c37615
created: '2026-06-24T05:12:10.265895+00:00'
updated: '2026-06-24T05:12:10.265895+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:10.265895+00:00'
  note: filed
---

### Option B — Two-way, RUNTIME-as-reconciler (the strong candidate)
Obsidian *may* write, but its writes are treated as **events, not truth.** A watcher
(`watchdog`/inotify on the vault, or a `cc_obsidian_ingest` op) sees an Obsidian-authored change,
**validates it, and re-canonicalizes it through the board runtime** (`comment` / `reply` / `edit_item` /
`transition`) — which re-renders the canonical YAML with *our* serializer and appends `history`. Obsidian
never writes the canonical record directly; it writes a *proposal* our runtime folds in.

The decisive insight — and the reason mark-is-truth was built — is that **the two kinds of write behave
completely differently under two writers:**

- **Append-only writes (the common case): ZERO conflict.** An annotation, comment, reply, or mark is a
  *new addressed item linked back by a typed edge* — it never touches the target file. Two writers
  appending different observations to the same node simply produce two new items; state composes by
  folding the thread (`thread()` / mark-fold). There is *nothing to conflict on.* This is most of what
  Tim does from the phone: he annotates. So the dominant write path is conflict-free for free.
- **In-place writes (`edit_item` title/body/order, `transition` state): need a rule.** Here both writers
  mutate one record. The reconciler applies **last-writer-wins with our runtime as the authority that
  stamps it** — Obsidian's edit becomes an `edit_item(..., note="via obsidian")` that appends a `history`
  entry, so even a "conflict" is recorded, not lost (no-versioning law preserved: same file, appended
  history). True simultaneous edits are rare and detectable via `updated` timestamps + content hash.

- **Truth:** intact — the runtime is the only thing that *mints* a canonical record; Obsidian only
  *suggests*.
- **Gain:** the full Obsidian feature set INCLUDING iOS write-back, because an iOS edit becomes an ingest
  event.
- **Where it bites:** the watcher must NOT let Obsidian's serializer be the canonical write (see §4 — it
  re-renders through our serializer instead); and it must distinguish "Obsidian touched the body" from
  "Obsidian reordered the YAML keys" so it doesn't generate phantom edits. The ingest path is real code
  to build and is the lynchpin of correctness.
