---
trust: lead-synthesis(ch-al7jdfdr) from TWO sources — a repo-fact scout (Explore/sonnet, file-cited) + ch-83e2cque's authoritative self-summary; CONVERGENT
author: ch-al7jdfdr (lead)
date: 2026-06-15
for: Tim — "get the plan and design compared against all of this… find out the differences between its design and the ones we have done here. I will need to know that."
relates: [2026-06-15-company-noticeboard-and-request-system.md, ../mega-prep/UNIFIED-SEAM.md, ../../build-prep/episodic-memory-adaptation/loop-prep/, ../../build-prep/brain/CONVERGENCE-OBJECT.md]
---
# Recollection vs the Board/Fabric — design comparison

> Tim's question (2026-06-15): can recollection be **built all together** with everything we've built here, and **what are the differences**?

## The one-line answer
**They are the SAME architecture pointed at two domains — not divergent designs.** Recollection (the memory system) and the Board/Fabric (channels · clones · the noticeboard · the registry/Heart spine) share one frame: *registry-of-registries + typed cross-registry edges + multi-space/coordinate addressing + fail-loud/registry-is-truth.* The divergences are **substrate and form (store + language + build-maturity), never frame** — and recollection was **designed for absorption from day one** (portable-by-field → absorption is a backend re-point, not a rewrite). So: **yes, one system** — built now to the same frame, kept deliberately detachable, unified at explicit wires.

Both halves agree on this independently: a repo-fact scout reading recollection's own design docs, and recollection (ch-83e2cque) summarizing its own design. Convergent.

## Where they are IDENTICAL (the frame)
| Tenet | Board / Fabric (BUILT) | Recollection (DESIGNED) |
|---|---|---|
| **Registry-of-registries** (add-a-row-not-code) | item_types/ · source_types/ · board_edges/ — file-discovered Python rows, live | unit-types · capture-sources · embedding-axes/lenses · judgment-types · query-tools — all "a row, not code" |
| **Typed cross-registry edges** | `board_edges/` reuses `RelationTypeRegistry` verbatim; links = `{kind,target}` | provenance/link graph (containment + typed+confidence-graded crossings); **beat-3 reuses the SAME `RelationTypeRegistry` verbatim** |
| **Multi-space / coordinate addressing** | flat `board://<id>` — identity holds nothing mutable; type/state are projections | D-1 multi-space: a unit holds a real address in every space; `exchange://<sid>/<i>` canonical (re-embed-stable); embedding is ONE co-equal space. *This IS the Heart cosmology Tim transmitted.* |
| **Source-type as registry** | `source_types/` (`claude_code` now; github = a future row, folds by JOIN on author/path/time) | `capture_source` rows (claude-code · voice · exports · github later) — same concept, same join |
| **Fail-loud / registry-is-truth** | every bad ref / illegal transition RAISES | no-hardcoding everywhere; no-fiction-about-Tim gates principle records |

The match is not coincidence — it's one designer's frame showing through both. Recollection's "multi-space addressing" (D-1) and the board's "flat `board://<id>`, properties are projections" are the *same law* (identity = the stable provenance address; semantic coords drift and are projections off it).

## Where they DIVERGE (substrate / form — all reconcilable, none a frame conflict)
| Axis | Board / Fabric | Recollection | Reconciliation |
|---|---|---|---|
| **Store substrate** | git-tracked markdown (`channel-memory/noticeboard/<id>.md`); no vector index | SQLite + sqlite-vec, per-lens `vec_<axis>` tables, 10.87 GB | recollection is **portable-by-field** (explicit space/source/dim/model/lineage cols) → absorption = a resolver re-point to Company FS/pgvector, not a rewrite |
| **Language / runtime** | Python (Company runtime) | TypeScript (cloned from obra/episodic-memory v1.4.2) | "built together" = shared **contracts + wires**, not one codebase; the registry *shape* is identical, the implementations are per-runtime |
| **Registry FORM** | file-discovered `.py` modules, live | currently SQLite/in-code shaped (clone heritage); file-discovered is the *design intent*, not yet built | align to file-discovered at absorption |
| **Build maturity** | BUILT + proven (26/26, committed) | DESIGNED; codebase is still the v1.4.2 clone (model+dim hardcoded in `embeddings.ts`/`db.ts`); `src/recall.ts` is new work-in-progress | recollection's "registries" are spec-of-record, not yet realized modules |
| **Standalone vs integrated** | integrated in ~/company | own repo (~/recollection), own data dir, own search/read MCP | D-8: standalone NOW, absorb as an explicit later step |
| **Domain** | the Company talking ABOUT ITSELF (operational items) | the Company's MEMORY of everything Tim built (identity continuity + cross-project omniscience) | different domains that MEET at the wires below |

Shared latent gap (a unification point, not a divergence): **neither `board://` nor `exchange://` is registered in `contracts/address.py:SCHEMES`** yet — both are used in practice but not first-class in the address grammar. Registering both (+ resolvers) is the literal "one addressed state."

## The WIRES where they're built together (already designed on both sides)
1. **recall↔board** — recollection sweeps `channel-memory/noticeboard/**/*.md` as a `capture_source` row → each item a unit addressed `board://<id>`, embedded, `source_type`-scoped recall. Lands ON the `board://<id>` + `source` field the board now emits. (Recollection's claimed follow-up unit.)
2. **shared edge vocabulary** — recollection's beat-3 reuses the board's `RelationTypeRegistry` verbatim → one cross-registry edge layer for both.
3. **shared source-type semantics** — board `source_types` and recollection `capture_sources` are the same concept; GitHub folds into BOTH as a row + author/path/time join.
4. **shared addressing** — register `board://` and `exchange://` in `contracts/address.py` → board items, recollection units, sessions all addressable in one grammar (the Heart's coordinate space).
5. **shared model + cognition infra** — both embed via the served stack (:8007 pplx-4b, :8008 jina) and judge via `runtime/cognition.py` roles — not parallel engines.

## Verdict for the cron decision
The thing Tim said he needed to know — *is recollection a divergent silo or the same system?* — answers **same system, by design**. So its build-work is aligned, not parallel; the revertible build proceeding is sound. The only genuine seam is **substrate** (TS+SQLite-vec → absorb to Python+pgvector later, a re-point by design). The cron-arming + unattended model-loads remain Tim's call (autonomous loop + GPU/voice share), but the alignment question is settled YES.

## Canonical sources
- Recollection design-of-record: `build-prep/episodic-memory-adaptation/loop-prep/` (COMPLETION_CRITERIA · IMPLEMENTATION_GUIDE · RESEARCH_SYNTHESIS · OPEN-DECISIONS), `MERGE-INTENTION.md`, the frame in `build-prep/brain/CONVERGENCE-OBJECT.md`, the 5-wire seam in `channel-memory/mega-prep/UNIFIED-SEAM.md`, built code in `~/recollection`.
- Board/Fabric: `runtime/cc_board.py` + `item_types/`·`source_types/`·`board_edges/`, `runtime/relation_types.py`, `contracts/address.py`, `2026-06-15-company-noticeboard-and-request-system.md`.
