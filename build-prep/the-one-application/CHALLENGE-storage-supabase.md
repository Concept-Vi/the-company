Both correctness traps locked in. Writing the final deliverable now.

---

# STORAGE ARCHITECT — Verdict on Moving the Union to Postgres/Supabase

## Verdict: **GO — with shape.** Local Postgres + pgvector as the union store; cloud Supabase as a *later* sync/realtime/mobile layer, not the migration target.

The union map is right that the structural substrate and the semantic corpus should live in **one store, queryable together**. Postgres+pgvector is the correct substrate to deliver that. But three things must be true or the recommendation is wrong:

1. **Local-first deployment, not cloud.** Today every `head()`, `get_vector()`, `load_agent_session()` is a cheap local ext4 read ("reads disk every call, no cache" — `fs_store.py:980`). Pointing those at *cloud* Postgres turns the hot path into network round-trips — a regression, not an upgrade, on a stack that is local-first by constitution (ext4, never `/mnt/c`, RTX-4080-local AI). **Run Postgres locally** (same WSL box, or a sibling container). Cloud Supabase becomes a later *replication/realtime/mobile* tier, addressed identically because the address never changes.

2. **The registries DO NOT move.** The union is over the **addressed graph + its embeddings** (the FsStore data), NOT the type vocabulary. Registry rows stay code-as-data `.py` files versioned by Git ("Git is the migration system" — store/AGENTS.md). `_CORPUS_REGISTRIES` becomes an *enumerable index over them*, not a relocation into SQL. Migrating SCHEMES / relation_types / item_types into tables would discard Git as the registry's migration+review+rollback system for no gain. **Tables hold: objects, refs, meta/provenance, events, vectors, sessions, marks, findings, annotations, dispositions, pins, memo, graphs, chat. Git holds: every `<registry>/*.py` row.**

3. **The seam is the first deliverable — before any backend exists.**

---

## The seam gap is the load-bearing fact (verified)

| Surface | Methods | Evidence |
|---|---|---|
| `contracts/resolver.py` Protocol | **10** | `put_content, get_content, exists, set_ref, head, write_provenance, provenance, lineage, memo_get, memo_set` |
| `FsStore` concrete class | **79** | `grep -cE "def " store/fs_store.py` |
| **Methods the codebase actually calls on `self.store`** | **61** | grepped across `runtime/ nodes/ contracts/` |
| `Suite.__init__` typing | `store: FsStore` | `suite.py:267` — typed to the **concrete class**, not `Resolver` |

**A Supabase backend that implements only the Protocol would be immediately broken** — it covers 10 of the 61 methods (16%) the system calls. This is the real cost, and it's reversible/green-on-fs work that pays off regardless of backend:

- **Step 1a:** Widen `Resolver` Protocol from 10 → the real 61-method call surface (the grep output is the exact list: `append_event`, `events_since`, `put_vector`, `index_corpus`, `layer_dims`, `load_agent_session`, `append_mark`, `disposition_for`, `pin_state_for`, …).
- **Step 1b:** Re-type `Suite.store: FsStore` → `Suite.store: Resolver`. Stays green on fs (FsStore satisfies the wider Protocol by construction). This is the change that makes a second backend *possible*.
- **Step 1c — absorb the two bypass namespaces** (correctness, not polish — they'd be silently stranded otherwise):
  - `cascades.json` via `_ActionRegistry(store.root / "cascades.json")` — `suite.py:394` reaches into the store *root* directly, bypassing FsStore.
  - `agent_sessions/channels.jsonl` via `session_channels.py` — writes a leaf beside `mail.jsonl` outside the method surface.
  Both must become Protocol methods (or explicit tables) before migration, or they survive only on the filesystem.

---

## The vector picture — verified, and simpler than the map implied

Read from real files, not the map:
- **Active `vectors/` is MIXED-DIM and that is BY DESIGN.** 2560-dim (`pplx-embed-context-v1-4b`, `emb=pplx`) AND 1024-dim (`bge-m3`, the default `emb` layer) coexist live (sampled 200 files: 106×2560, 94×1024). The `space_address()` docstring (`fs_store.py:919`) makes this explicit: "the SAME (item, space) can hold MULTIPLE embeddings… a BGE-M3 layer AND a pplx layer side by side at DISTINCT keys." This is Tim's multi-layer model, not corruption.
- **Separate concern:** `vectors.bge-backup-20260615/` (66M, also 1024-dim) is a *different population* with "no API path." That dir is an archival decision (re-ingest as a named `emb` layer, or archive out of the store root) — it is NOT the same thing as the live bge layer. Don't conflate them; dropping "all 1024-dim as the backup" would strand half the live index.

**The vector schema is therefore trivial — one table mirroring `put_vector`'s record verbatim:**

```sql
CREATE TABLE vectors (
  address      text PRIMARY KEY,   -- the _safe(address) key today → real PK
  source       text NOT NULL,      -- bare item it embeds
  space        text,               -- NULL = default space
  emb          text,               -- NULL = default layer (bge); 'pplx' etc.
  dim          int  NOT NULL,
  model        text NOT NULL,
  content_hash text NOT NULL,
  vector       float4[],           -- plain array; NOT indexed
  ts           timestamptz
);
CREATE INDEX ON vectors (space, emb);   -- the filter, not the vector
```

**Do NOT build an HNSW/IVFFlat index, do NOT reach for `halfvec`, do NOT split per-dim.** At ~9k vectors total, `WHERE space=X AND emb=Y` then **exact cosine scan** is sub-10ms. Mixed dims coexist fine *because you never compare across them* (the `(space, emb)` filter already isolates each layer — exactly what `index_corpus(space, emb)` does today). The 2000-dim `vector`-type / halfvec / ANN-index questions only arise at ~100× this corpus; defer them entirely. This is why the store is "Supabase-portable by construction" — the record is already field-shaped for `WHERE`.

---

## The one query that makes it a UNION, not a bridge (= the acceptance test)

The union is real only if a query needs structural + semantic **in one statement**. Here it is:

> *"Board items of type `request`, that have a `responds_to` edge to project P, modified since T, ranked by cosine similarity to query-vector Q."*

- **Today (the bridge):** full-scan `events.jsonl` (4MB, 6,449 lines) for board items → read each item's edges from `board_edges` → read each candidate's vector file from `vectors/` → compute cosine in Python → sort. Four stores, three languages of access, all in app code.
- **In one Postgres store (the union):** one statement —
  ```sql
  SELECT i.address, 1 - (v.vector <=> :q) AS score
  FROM board_items i
  JOIN edges e   ON e.source = i.address AND e.kind = 'responds_to' AND e.target = :project
  JOIN vectors v ON v.source = i.address AND v.space = 'history' AND v.emb = 'pplx'
  WHERE i.type = 'request' AND i.modified_at >= :t
  ORDER BY score DESC;
  ```
This query is the **go-argument and the acceptance test simultaneously**. If the migration can serve it, the union is real. If you can't write it, the union is hollow. (`<=>` works on the plain array via exact scan; no ANN index needed at this scale.)

---

## Migration shape (ordered, reversible at each step)

| Phase | Move | Risk if skipped |
|---|---|---|
| **1. Seam** | Protocol 10→61; `Suite.store: Resolver`; absorb cascades.json + channels.jsonl | Backend covers 16% of calls → broken on day one |
| **2. Local PG stand-up** | Postgres + pgvector on the WSL box (or sibling container) | Cloud-first = hot-path latency regression |
| **3. Shape-B JSONL → tables** | `events`, `chat`, `annotations`, `findings`, `marks`, `dispositions`, `pins`, `mail` → rows with `WHERE field=X`. (`events.jsonl` full-scan at 6,449 lines is the I/O argument.) | Full-file-scan stays the read pattern |
| **4. Shape-A dirs → upsert tables** | `objects` (CAS), `refs`, `ref_history`, `meta`, `memo`, `graphs`, `sessions`, `agent_sessions` keyed by id | — |
| **5. Vectors → the `vectors` table above** | Record migrates verbatim; `(space,emb)` filter + exact scan | — |
| **6. Concurrency swap** | `flock`/`tmp+rename` → Postgres advisory locks + ACID. The `append_event` RLock (`fs_store.py:134`, monotonic-unique seq) → a sequence/SERIAL | Lost-update on the seq invariant the SSE cursor depends on |
| **7. CAS blobs** | `objects/` (90M) → a `content` table or Supabase Storage; keep blake2b key as PK | — |
| **8. BGE-backup decision** | Re-ingest 66M as a named `emb` layer, or archive out of store root | Stranded 2,793-vector population |

Every phase keeps fs as the fallback (dual-write or feature-flagged backend) until verified.

---

## Which Supabase extensions actually help

- **pgvector — YES, core.** It's the whole reason this is a union and not a bridge: the embeddings live in the same store as the structural rows, joinable in one statement. (At current scale, the `vector` *type* and ANN indexes are optional; plain `float4[]` + exact scan suffices. Adopt pgvector's `vector`/`halfvec` + HNSW only when the corpus grows.)
- **Realtime (`postgres_changes`) — YES, strongest concrete pro.** `events_since(seq)` (verified monotonic-unique by the RLock at `fs_store.py:134`) maps **directly** onto a logical-replication change feed. This turns the fabric / board / coherence surfaces from **poll** into **push** — `CognitionView`/`CoherenceView` "reflecting-never-owns over the same SSE" becomes a native subscription. This is the upgrade that the filesystem genuinely can't give.
- **RLS — CONDITIONAL, probably premature.** One entity, single operator → no row-tenancy need *today*. RLS earns its place **only if the mobile PWA hits Postgres directly** (PostgREST). Until then it's overhead. Flag it, don't bank it.
- **Supabase Storage — optional**, for the 90M CAS blob population if you'd rather not hold bytes in a `content` table.
- **PostgREST / Auth — later**, tied to the mobile-direct decision, not the union itself.

---

## Real risks / costs (concrete)

1. **The 51-method seam gap is the true cost.** "Implements the Resolver Protocol" undersells it 6×. Budget Phase 1 as the real work; the backend itself is mechanical once the seam is honest.
2. **Hot-path latency if deployed to cloud.** The single most likely way to make this a regression. Local PG mandatory; cloud is replication.
3. **Two bypass namespaces** (cascades.json, channels.jsonl) silently stranded if not absorbed first — a correctness item, not polish.
4. **Concurrency-model swap is delicate.** The `append_event` seq is monotonic-unique *and load-bearing* (the SSE cursor `id:<seq>` and the wire's `derived_from` bind both assume it). Postgres SERIAL/sequence preserves this, but the swap must be verified by use, not assumed.
5. **Dual-write window.** Until a phase is verified, fs + PG must agree — adds transient complexity. Mitigated by phasing (each shape migrates independently, fs stays the fallback).
6. **No new scheme needed, no `coherence://`, no `channel://`-forced-in** — the union rides existing addresses. (Separately: `channel`/`cluster` absent from SCHEMES is a real gap, but it's an address-grammar fix, not a storage one — don't bundle it here.)

---

## The one sentence

**GO:** put the addressed graph and its embeddings in **one local Postgres+pgvector store** so the structural-and-semantic JOIN above runs as one statement (the union), keep every registry row in Git (the type vocabulary doesn't move), make the migration *possible* by first widening the Resolver seam from 10→61 methods and absorbing the two bypass namespaces, and treat cloud Supabase + Realtime + RLS as a later mobile/push tier — not the migration target — addressed identically because the address never changes.

**Key file anchors:** `contracts/resolver.py` (10-method seam to widen), `store/fs_store.py:267`→`suite.py:267` (`store: FsStore` to re-type to `Resolver`), `store/fs_store.py:919` (`space_address` — the `(space,emb)` multi-layer key that becomes the `vectors` table filter), `store/fs_store.py:516` (`append_event` monotonic seq → Realtime feed), `suite.py:394` + `runtime/session_channels.py` (the two bypass namespaces to absorb first).