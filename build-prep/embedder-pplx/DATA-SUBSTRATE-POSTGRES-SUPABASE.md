# The Data Substrate — flat-JSON (provisional) → Postgres / Supabase / pgvector

*Stretched out from Tim's 2026-06-15 think-aloud: "Everything in the database can be rewritten, that was just the
first thing that got written, the database hasn't had any attention. I am thinking Postgres, Supabase so later it
can be moved to cloud. I am sure Supabase can be run locally. The database is probably very flat right now."
Living doc. I supply the technical shape; Tim set the direction.*

---

## 1. Where it is now (provisional, by Tim's own account)
The store is **flat files** under `.data/store/`:
- `vectors/<key>.json` — one JSON file per embedded item (`vec__<addr>#space=<space>.json`), holding a single
  vector. **One item → one vector per space.** No layers, no provenance, no history.
- `events.jsonl` — the append-only event stream (corpus.record, etc.).
- `cas/` — content-addressed blobs (the actual text behind records).
The engine reaches this through a **store object injected into the Suite** (`Suite(FsStore(STORE_DIR), …)`) — so
the backend is already swappable IF the interface is honored. This flat store was "the first thing written" — it
works, but it cannot express the multi-layer model (INSTRUMENT-DUAL-INTERFACE-AND-LAYERS.md §3) and won't scale.

## 2. Why move (what the flat store can't do)
- **Layers** — item → MANY readings (embedder × frame × resolution × provenance × lifecycle). Flat one-file-per-
  vector can't hold a stack with override-history; relational rows can.
- **Query** — "all layers of X", "items whose context-reading differs most from isolated", "the latest ratified
  layer per item", vector-ANN + relational filters in one query. pgvector + SQL does this; a directory of JSON
  files does not.
- **Scale** — tens of thousands of events × multiple layers each; binary-quantized full-corpus views (capabilities
  doc §D). HNSW indexes, not a filesystem scan.
- **Cloud + realtime** — Tim wants local→cloud portability and (later) the realtime channel. Supabase gives both:
  the SAME Postgres schema local (Docker) and cloud, plus realtime subscriptions.

## 3. Target — Postgres + pgvector, via Supabase (local now, cloud later)
- **Supabase local** = `supabase start` (Docker): Postgres + pgvector + realtime + auth + storage, identical to
  cloud. Build against local; `supabase link` + push to cloud when ready. Same schema, same client — Tim's
  "later it can be moved to cloud" is then a config flip, not a rewrite.
- **pgvector** for the embeddings (HNSW index per dim/precision variant).
- **Supabase Storage** can replace the `cas/` blob store (or keep cas on disk; the text doesn't need pg).
- **Supabase Realtime** → the live spine (G4 SSE) at scale: subscribe to the events/layers tables → the surface
  updates live without polling. Connects [[project-company-vi-supabase-future]] (the realtime channel) and
  [[project-vichat-supabase-history]] (history in Supabase). NOTE security: [[project-key-rotation-pending]] —
  use fresh keys; never hardcode (the no-hardcoding law).

## 4. Schema sketch (the multi-layer model, relational)
*Illustrative — to refine with Tim. The shape, not the final DDL.*

```
addresses        -- the THINGS (items, units, registry rows) — the spine
  address text primary key        -- run://… code://… ui://… (the canonical address)
  kind, parent_address, created_at, meta jsonb

spaces           -- named projections / lenses (registry-discovered today)
  id text primary key, level, produced_by, embeds bool, meta jsonb

layers           -- THE READINGS (the new core) — one item read under one frame
  id uuid primary key
  address text references addresses
  space  text references spaces
  embedder text                   -- pplx-context-4b · code-embed · … (the loadout)
  reading_mode text               -- isolated | in-context
  context_frame text null         -- the parent/grouping address, if in-context
  dim int, quantization text      -- 2560 | 1024(MRL) ; fp | int8 | binary
  params jsonb                     -- rung, dial, anything that shaped the read
  vector   vector(2560)           -- pgvector (full dim; MRL-truncate at query)
  vector_bin bit(2560) null       -- optional binary variant for scale views
  provenance jsonb                 -- who (Tim|agent id), when, why, run/intent
  lifecycle text                   -- provisional | ratified  (the GATE)
  supersedes uuid null             -- override-history (points at the layer it replaced)
  created_at timestamptz
  -- indexes: HNSW on vector; btree on (address, space, embedder, reading_mode); partial on lifecycle='ratified'

events           -- the corpus.record / telemetry stream (append-only, today's events.jsonl)
  seq bigserial, ts, kind, address, projection, payload jsonb
```
- **One item → many layers** (the whole point). "Current" reading = latest non-superseded ratified layer in a
  slot `(address, space, embedder, reading_mode, context_frame)`; **override** = insert with `supersedes`;
  **store** = insert as a sibling; **promote** = lifecycle provisional→ratified; **stack** = they all coexist.
- **MRL** = store full 2560 once; truncate-at-query for coarser dim (one vector, many resolutions — capabilities
  §C). **Binary** = the optional `vector_bin` for full-corpus scale views (§D).
- **Provenance + lifecycle** = the introspective-data-building byproduct ([[project-introspective-data-building]])
  AND the GATE lifecycle (sample→ratified, the keystone) — both fall out of the layer row.

## 5. Migration path (behind the store interface — swappable, revertible)
1. **Pin the store interface** — enumerate what the Suite/bridge call on the store (`get_vector`, `put_vector`,
   `space_address`, `get_content`, `events`, scale-pyramid reads, …). This is the contract a backend must meet.
2. **Implement `PgStore`** (same interface, Postgres/pgvector backend). The engine (bridge/Suite) is injected
   with it — no engine rewrite if the interface holds. Keep `FsStore` working (fallback / revert).
3. **Stand up Supabase local** (Docker) + the schema (§4). Start with the *current* one-vector-per-item shape
   mapped to a single `layers` row each, so nothing breaks; the multi-layer features turn on incrementally.
4. **Backfill** — import the flat-JSON vectors + events into pg (a one-off). Verify parity (counts, a sample of
   cosines match) before switching the engine's store to PgStore.
5. **Swap + verify** — point the Suite at PgStore; re-run the acceptance suite + the instrument lenses (curl +
   both viewports). Revert = point back at FsStore (git + config).
6. **Then** the multi-layer features (override/store/stack/promote), the realtime spine, binary-scale views — each
   its own beat on the new substrate.
- **This pairs with the embedder migration** (leverage §4): re-embedding the corpus on pplx is the natural moment
  to also write it into the new substrate (do the model-switch and the store-switch together — embed once, land in pg).

## 6. Honest scope + the standard
This is a real redesign, not a tweak — but it's de-risked by the injected-store seam (swap a backend, don't
rewrite the engine) and by keeping FsStore as the revert. It is also a *foundation* enabling the whole vision
(layers, scale, cloud, realtime). Held to the same standards: registry-is-truth (spaces/registries stay
file/registry-discovered — pg holds the DATA, not the schema-of-types), no-silent-fallback (a pg outage fails
loud, never a silent empty), and the dual interface (the layer operations exposed on both faces).

## 7. Open questions for Tim
- **Now vs incremental** — stand up Supabase-local + PgStore as the next foundation beat, or keep flat-JSON until
  the embedder migration forces the issue and do both together? (I lean: do them together — embed once into pg.)
- **cas/storage** — keep content blobs on disk (cas/) or move to Supabase Storage?
- **realtime now or later** — wire Supabase realtime into the live spine as part of this, or keep the current SSE
  until cloud?
- **Layer slot identity** — the `(address, space, embedder, reading_mode, context_frame)` slot key (above) — does
  that match how Tim thinks about "override vs store"? (Drives the schema.)
