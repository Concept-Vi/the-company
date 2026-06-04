---
type: constitution
module: nodes
aliases: ["nodes — constitution"]
tags: [company, constitution, nodes, node-library]
governs: [C2]
relates-to: ["[[Company Map]]", "[[runtime — constitution]]", "[[fabric — constitution]]", "[[store — constitution]]", "[[canvas — constitution]]", "[[contracts — constitution]]"]
status: living
---

# nodes/ — module constitution

**Is:** the node library — every node-type, in three kinds: **process** (survey, extract, embed, judge, gate…), **content/asset** (document, code, file, image, source, portal), **presentation** (note, annotation, callout, title). Each is one C2 declaration.
**Guarantees:** a node-type is **one self-contained C2 definition** (`ports · config_schema · output_schema · render_set · inspector_schema`). On drop-in it **self-registers**, becomes queryable in the type-graph, and appears in the palette via `/object_info` — **with no change to runtime, UI, or tools.** AI nodes reuse `fabric/` guards. Content nodes hold a content **address**, never inline bytes.
**Live-state nodes declare `VOLATILE=True`:** a node that reads **mutable truth** whose inputs don't change every run (the repo on disk → `codebase`; a model of someone → `model_of_tim`; a clock; a corpus index) MUST set module-level `VOLATILE=True`, or the memo gate will serve a frozen first result forever. A pure transform of its inputs (`uppercase`, `join`, `wordcount`) must **not** set it. Test: *can the same input ever need to produce a fresh output?* Yes → `VOLATILE`.
**Where new things go:** a new node-type = a new folder `nodes/<name>/` with its definition (+ a tiny constitution noting what it produces).
**To extend:** declare the C2 contract, drop it in. That's the whole "self-extending" path. Subgraph-as-node (HDA): a saved canvas's promoted ports/config become a new type here.
**Seam:** implements C2; AI behaviour via `fabric/`; rendered generically by `canvas/` from `/object_info`.
**Never:** edit `runtime/` or `canvas/` to add a type · write per-type frontend code · inline large content into a node · ship a node that reads mutable truth without `VOLATILE=True` (it will silently go stale).

## What's in here

The node-type modules (`nodes/*.py`), each one C2-self-registering. The **live, complete
list is the single source of truth** — the auto-maintained REGISTRY block in
[[Company Map]] (do not duplicate it here; that's the rule in [[Vault Conventions]]). By
kind, with the ones worth knowing:

- **process** — pure transforms (`uppercase`, `titlecase`, `wordcount`, `join`) and the AI
  workhorses (`llm`, `ask`, `pair`).
- **content** — `constant`; `codebase` (reads the whole repo — **`VOLATILE`**); `portal`
  (a reference into another graph/address).
- **live-state / special** — `model_of_tim` (the explicit model-of-Tim the RHM reasons
  from — **`VOLATILE`**); `rhm_mode` (the presence dial — a *mode is a node*; also carries
  the voice-trial **`voice_enabled`** on/off toggle, read by `Suite.voice_enabled()`).

## Relates to

- **Called by** [[runtime — constitution]] — the scheduler runs a node when its input
  addresses resolve; and by [[canvas — constitution]], which renders every node generically
  from `/object_info`.
- **Uses** [[fabric — constitution]] (AI nodes call models through its guards) and
  [[store — constitution]] (content nodes hold addresses, never bytes).
- **Governed by** [[contracts — constitution]] — the C2 node contract is the shape every
  node here obeys.

## Read next
[[Company Map]] (the live registry + the whole picture) · [[runtime — constitution]] (what runs these) · [[Vault Conventions]] (why this note is shaped this way).
