---
id: item-2ecd462a
address: board://item-2ecd462a
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P12 · 6 · Where it bites regardless of option — the cross-cutting traps
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-80c37615
created: '2026-06-24T05:12:10.404782+00:00'
updated: '2026-06-24T05:12:10.404782+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:10.404782+00:00'
  note: filed
---

## 6 · Where it bites regardless of option — the cross-cutting traps

- **Obsidian Sync is an adversarial second writer, not a free feature.** The files are already git-tracked
  (the no-versioning law lives on git). Obsidian Sync is a *separate* sync system with its *own*
  conflict resolution that knows nothing about `board://` identity, typed edges, or mark-fold. Two sync
  layers over one tree race. The clean stance: **git is the canonical sync; Obsidian Sync only ever runs
  over a *derived/projection* vault (A/C), never over the canonical dir.** This is another argument
  against D and for keeping a projection plane.

- **The typed-edge → wikilink projection is lossy by design — keep it one-way.** `links: [{kind,
    target}]` carries a *kind* (`attached_to`, `commented_on`, `reply_to`, `references`…) and resolves
  cross-scheme (`decision://`, `code://`, `image://`). A `[[wikilink]]` is untyped and file-path-scoped.
  You can *emit* `[[…]]` from edges for the graph view (optionally annotate the kind in link text), but
  you can never recover the kind+scheme from a wikilink — so a read-back would *downgrade* a typed
  cross-registry edge to an untyped path link. This is the §1 law, made concrete.

- **Cross-scheme targets have no file to link to.** Many edges point at `decision://global/visual-fidelity`,
  `code://suite/x`, `image://chan/p-05` — addresses with *no markdown file in the vault*. Obsidian's
  graph can only link node-to-node within the vault. So the projection must decide: emit stub notes for
  non-board targets (so the graph is whole) or only project board↔board edges (so the graph is partial
  but honest). Either way, the resolver — not Obsidian — remains the only thing that can actually
  *follow* a cross-scheme edge.

- **The "document" is logical, not foldered.** A board document is an `order: [block-addr,…]` list with
  blocks linked `part_of`; storage is flat id-keyed. Obsidian's native model is folders + files. The
  projection can render a document as an embedded/transcluded note (`![[block-id]]` in order) — a nice
  lens — but the *sequence truth* stays in `order`, never in folder position.

---
