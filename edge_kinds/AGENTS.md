---
type: constitution
register: prescriptive
module: edge_kinds
aliases: ["edge_kinds — constitution", "the edge-kind grammar"]
tags: [company, constitution, edge-kinds, graph, path, registry, container, ledger]
governs: [edge-kind-vocabulary]
relates-to: ["[[Company Map]]", "[[board_edges]]", "[[relation_types]]", "[[THE-CONTAINER]]"]
status: living
---
# edge_kinds/ — module constitution

**Is:** the file-discovered EDGE-KIND registry — the ONE edge grammar for the whole edge store (④ THE CONTAINER · L4, GRAPH-PATH §3.1). Each `edge_kinds/<id>.py` declares a module-level `EDGE_KIND` dict (a registry ROW). The files AUTHOR; the DB table `ledger.edge_kind` is the DERIVED read side (law 3: vocabulary=files, data=DB). Every kind that lives in — or lands into — `ledger.edge` / `ledger.assertion` (the unified `ledger.edge_unified`) is governed here: `calls`, `imports`, `contains`, the semantic band, the cloud-landed cartography, and the ledger session's authored-provenance kinds (`generated-by`, `authored_by`).

**Why a purpose-built registry (not `relation_types.RelationTypeRegistry` verbatim):** the `EDGE_KIND` row is a SUPERSET of `RELATION_TYPE` — it adds `face` (the JOB: containment|knowledge|lineage), `endpoints`, `behavior`, `needs_review`. `RelationTypeRegistry` fail-louds on those extra fields (its field set is closed). So `runtime/edge_kinds.py` REUSES the same file-discovery PATTERN in a separate dir with a richer shape — exactly the `board_edges/` precedent (one grammar via one mechanism-shape; a separate dir per vocabulary). Unify into one mechanism when a consumer traverses one unified relation graph.

**Guarantees (row schema — `EDGE_KIND = {...}`):** required `id` (== filename; ONE spelling per concept — kills part_of/part-of drift), `directed` (bool; symmetric kinds declare `False`), `face` (containment|knowledge|lineage). Optional `inverse` (the DECLARED equal-and-opposite NAME — **composed at read, NEVER stored**, law 4), `endpoints` (valid schemes), `behavior` ('dispatch' as a declaration, not a hidden trigger), `label`, `description`, `near`/`far`, `needs_review`. A malformed row RAISES at discovery (`runtime/edge_kinds.py:_validate_row`).

**The two laws this dir carries:**
- **Reverses are declared, composed at read, never stored** (law 4). `imports` declares `inverse: imported_by`; a query for `imported_by` is composed off the stored `imports` rows (`runtime/edge_kinds.py:compose_inverse`). NO `imported_by` row is ever written. A stronger equal-and-opposite than data-level duplication — it cannot drift.
- **Containment is derived, never stored** — a `contains`/`belongs_to`/`part_of` edge (face=containment) is derived from the address hierarchy; the cloud's 319 stored `belongs_to` rows were DROPPED on landing (excluded-with-reason).

**ABSORB-never-reject:** a new kind = author a file + re-assemble. Registration ABSORBS (the seed pulls from the UNION of every source); it is NEVER a rejection gate. The write-time validation (`ledger.validate_edge_kind` / `runtime.edge_kinds.validate_kinds`) FAILS LOUD on an unregistered kind — naming this dir + the absorb path — but the remedy is always "add the row", never "drop the edge". There is deliberately NO hard FK on `ledger.edge` / `ledger.assertion` (a reject gate on the tables the ledger session writes live) — the gate is on the loader's write path.

**Where new things go:** a new edge-kind = a new file `edge_kinds/<id>.py` declaring `EDGE_KIND`. To regenerate from live data: `python ops/seed_edge_kinds.py` (writes files from the ledger.edge + cvi_mine union). Then `python -m runtime.edge_kinds assemble` (folds files → `ledger.edge_kind`; upserts + prunes stale — registry-is-truth).

**Seam:**
- discovered + assembled by `runtime/edge_kinds.py` (`discover` / `assemble` / `validate_kinds` / `compose_inverse` / `inverse_map`).
- the DB read side `ledger.edge_kind` (migration `0018_graph_path.sql`) + the callable validation seam `ledger.edge_kind_exists(text)` (non-blocking — the ledger session's `edge_unified` retro-validation joins on it) and `ledger.validate_edge_kind(text)` (fail-loud).
- consumed by `ops/ledger_build.py:load_run` (write-gate), `ops/migrate_edges_from_cvi.py` (landing classifier), `runtime/paths.py` (path-step `via_kind` validation), `ops/graph_projection.py` (face → edges[]).

**Never:** store a reverse row (compose it); store a containment edge the address already encodes (derive it); inline the kind set as an enum; invent a kind not seen in a source (author it, re-assemble); reject an edge for an unregistered kind (absorb it); a `ledger.edge_kind` row with no source file (a ghost — the assembler prunes it).

## Relates to
[[board_edges]] (the file-per-row precedent this parallels) · [[relation_types]] (the mechanism-shape reused; the eventual unification target) · [[THE-CONTAINER]] (④ · L4) · GRAPH-PATH.md (the organ study — the authority)

## Agent-authored entries (auto-reflected)
<!-- one line per hand-authored kind beyond the generated union; keep the drift-home honest. -->
- **`follows`** (lineage) — the path-step threading relation (ledger.path_step via_kind; ordinal>0).
- **`navigated_to`** (knowledge) — a navigation step (GRAPH-PATH §3.3 navigation paths).
