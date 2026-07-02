---
id: item-5d40fb57
address: board://item-5d40fb57
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: 'P2 · 0. The one verdict that matters: there are TWO annotation runtimes, and '
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-e42d651f
created: '2026-06-24T01:32:19.641778+00:00'
updated: '2026-06-24T01:32:19.641778+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:19.641778+00:00'
  note: filed
---

## 0. The one verdict that matters: there are TWO annotation runtimes, and the brief conflates them

The brief (and design-map A5) says "the mark + comment + edge machinery already runs… an annotation IS a typed observation." That sentence hides a real fork I verified in the code:

- **Board-comment-as-edge** (`runtime/cc_board.py`): `comment()` files a *new board item* and links it `commented_on → target`. `reply()` links `reply_to → comment`. `thread()` folds the reverse-edges into a nested tree. **Verified** — this is what the existing phone artefact uses.
- **Mark-as-composed-state** (`runtime/suite.py:mark/marks_for/marks_by_type` over `store.append_mark`; `runtime/decision_registry.py:compose_state`): an append-only `{target, mark_type, value, confidence, evidence, status}` record; the target's *state is the fold of its mark thread*, the target never mutates. `mark_type` is gated against the file-discovered `mark_types/` registry. **Verified** — this is the "mark-is-truth" runtime, and it is a *different store and a different shape* from board-comments.

**These are not the same machinery.** They are two implementations of "typed observation on an address":
- A board-comment is *itself an addressed node* (`board://`) — repliable, threadable, its own thing.
- A mark is *not addressed* — it's a disposition that composes into the target's state.

**The architectural decision the envelope forces:** is an annotation-envelope a **board item** (so it threads, gets replied to, gets routed — Tim explicitly wants replies and threading) or a **mark** (so the target node's "current understanding" composes from the observation thread — the beautiful pattern A5 sells)?

My answer: **the envelope is a board item** (it must be addressable, repliable, routable, lifecycle-bearing — none of which marks give you), **and** a derived **mark** can be *projected from it* onto the target node when you want the composed-state view (e.g. "what's the live verdict on this paragraph"). Don't pick one; **the board-item is the durable artifact, the mark is a read-projection**. But name it — the brief's "it all already runs as one thing" is *Inferred and partly false*: it's two runtimes, and which one is authoritative for the envelope is undecided.

---
