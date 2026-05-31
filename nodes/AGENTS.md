# nodes/ — module constitution

**Is:** the node library — every node-type, in three kinds: **process** (survey, extract, embed, judge, gate…), **content/asset** (document, code, file, image, source, portal), **presentation** (note, annotation, callout, title). Each is one C2 declaration.
**Guarantees:** a node-type is **one self-contained C2 definition** (`ports · config_schema · output_schema · render_set · inspector_schema`). On drop-in it **self-registers**, becomes queryable in the type-graph, and appears in the palette via `/object_info` — **with no change to runtime, UI, or tools.** AI nodes reuse `fabric/` guards. Content nodes hold a content **address**, never inline bytes.
**Where new things go:** a new node-type = a new folder `nodes/<name>/` with its definition (+ a tiny constitution noting what it produces).
**To extend:** declare the C2 contract, drop it in. That's the whole "self-extending" path. Subgraph-as-node (HDA): a saved canvas's promoted ports/config become a new type here.
**Seam:** implements C2; AI behaviour via `fabric/`; rendered generically by `canvas/` from `/object_info`.
**Never:** edit `runtime/` or `canvas/` to add a type · write per-type frontend code · inline large content into a node.
