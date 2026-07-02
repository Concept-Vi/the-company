---
id: item-bd30758f
address: board://item-bd30758f
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: A2 · Your graph idea — nodes, observations, typed edges — is the system's own
  unbuilt design
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-389c8489
created: '2026-06-23T17:13:52.366575+00:00'
updated: '2026-06-23T17:13:52.366575+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-23T17:13:52.366575+00:00'
  note: filed
---

# Your graph idea — nodes, observations, typed edges — is the system's own unbuilt design

You said: *"it sounds like it is a node with 'observations', and the fields and types of relations… those sound like typed edges… the registries are simultaneously what they already are, as well as capable of being a graph at the same time."*

Here is what the agents found, and it lands almost word-for-word on real things:

- **Node = address.** There are 19 kinds of address, all resolved through **one** resolver. An address names a thing — a file, a decision, an image, a session. That's your node.

- **Observation = "mark."** The system already has a concept it literally treats as observations stamped onto an addressed thing — they're called *marks*. There's a registry of **observation-types** (likelihood, contradiction, fingerprint, and so on). Marks are **append-only** and **"mark-is-truth"**: the thing itself never gets edited; instead, observations accumulate on it, and its current state is *composed* by folding the observations in order. **You used the word "observations" — the system uses the same word for the same thing, and it already works this way.**

- **Typed edge = "relation."** There's a registry of relationship-types, each with a direction and an inverse (this→that, and the reverse). The board already links things across all those address-types with typed edges (`authored_by`, `references`, `commented_on`, `reply_to`, …), and there's a function that **follows a thing's typed links outward and resolves whatever they point at** — that's traversal, and it already exists in a first form.

- **The registries-are-also-a-graph** — your exact phrase — is real: the facts the dragnet's index stores are literally three-part statements (*this-file → declares → a-role*), which is the subject–relationship–object shape of a graph. The raw material of a graph is already lying there as facts.

**The one honest refinement** (correcting myself — I said flatly last time "it *is* a graph"): the *facts* are all there in graph-shape, and a *first* traversal exists — but the system does **not yet treat the whole thing as one walkable web.** And here's the striking part the agents surfaced: **the system has explicitly written down that it wants to** — there's a tracked, named, *not-yet-built* design for exactly this ("a unified relation graph… generalize discovery into one query language… not yet built, tracked as a design idea"). **You just described, from your own head, the thing the architecture already knows is its next layer and hasn't built.** Your intuition converged with the system's own roadmap. That's not a coincidence to gloss over — it means the graph isn't speculative; it's the agreed-upon direction, waiting to be assembled from parts that mostly exist.

So the dragnet cards becoming *observations on file-nodes, linked by typed edges* isn't a new architecture — it's **populating the graph the system already wants, using the mark/edge/node machinery that already runs.**
