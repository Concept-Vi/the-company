---
id: item-1fd4cac6
address: board://item-1fd4cac6
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P4 · 2 · The FREE-vs-SHIM ledger (the core deliverable)
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-4baaab55
created: '2026-06-24T05:12:09.330338+00:00'
updated: '2026-06-24T05:12:09.330338+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:09.330338+00:00'
  note: filed
---

## 2 · The FREE-vs-SHIM ledger (the core deliverable)

| Capability | Status on OUR data | Why |
|---|---|---|
| Full-text search | **Free** | Plain markdown bodies. **[Inferred]** |
| Properties panel | **Free** | YAML frontmatter is Obsidian-native; `id/type/state/channel/author_session/title/created/updated` all show as properties. **[Inferred]** |
| Bases / Dataview "board view" (table/cards filtered by `type`, `state`, `channel`) | **Free** | Scalar frontmatter keys are exactly what Bases queries. Vault already ships `.base` files to clone. **[Observed]** (`.base` files exist; vault at `/home/tim/vaults/Obsidian Builder/`) |
| Graph view + backlinks | **NOT free → L2 shim** | Edges are `board://…` strings inside a `links:` **list-of-dicts** YAML key. Obsidian graphs only `[[wikilinks]]`, tags, and wikilink-*properties* — it does not walk a list-of-dicts. **[Observed]** (cc_board.py:159-172; `links` is `[{kind,target}]`) |
| `order` / `part_of` logical document → one readable note | **NOT free → L2, but maps cleanly** | See §4 — transclusion is the natural fit. **[Inferred]** |
| Canvas, plugins, iOS app, sync | **Free** *once a syncable vault exists* | These ride on "it's a vault." The catch is purely *where the folder lives* (§6). **[Inferred]** |
| Editing items back | **L3, dangerous** | Two-writer + YAML-shape fragility (§5). |

**The single load-bearing line:** the only things that need a shim are the **typed-edge graph** and the **assembled-document view**. Everything tabular/textual is free today.

---
