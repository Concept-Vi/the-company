---
type: constitution
module: store
aliases: ["store — constitution"]
tags: [company, constitution, store]
governs: [C1, C4]
relates-to: ["[[Company Map]]", "[[contracts — constitution]]", "[[runtime — constitution]]"]
status: living
---

# store/ — module constitution

**Is:** the addressed store + the resolver — turns an address into bytes and back. Implements C1 (grammar/provenance) + C4 (Resolver Protocol). Filesystem-first; Supabase later.
**Guarantees:** content at `cas://` is **immutable** — never mutated, never lost (an "update" is a new object + a moved pointer). Reads live truth. The store lives on **ext4 (`~/...`), never `/mnt/c`**. Every write records provenance (`inputs[]` → lineage to source). **Cross-process safe (S4):** the bridge + MCP face are two processes on ONE store dir, so the threading locks (in-process only) are **layered with `fcntl` OS advisory locks** — `graph_lock(gid)` and `dispatch_lock(seq)` return a compound CM (threading RLock **outer**, fcntl **inner**, the fcntl taken only at the outermost acquire via a depth-count so a re-entrant call can't self-deadlock). One lock FILE per resource under `locks/` (never a global lock — that would serialize the night). This serializes the graph load→mutate→save and the wire's dispatch CHECK→CLAIM **across the process boundary** (no lost-update, no double-dispatch). Hot writes (`set_ref`/`save_graph`/`save_surfaced`/`save_session`/`append_event`) are **fsync'd** before the atomic rename (crash-durable). The durable `decision.dispatch` event stays the cross-RESTART exactly-once guarantee; fcntl adds the concurrent (two-faces-now) one. (POSIX-only; the deploy target is Linux/WSL ext4.) **Chat turns carry provenance too** — every `append_chat` records `source` (`operator` = Tim, `twin` = the model) and `grade` (`gold`/`working`); the twin's training signal is filtered to operator-gold so the model **never learns from its own output, even laundered back as a role-flipped 'user' turn** (the echo-guard against model-collapse). Any new chat-persist path MUST tag `source`, or the echo-guard silently fails open.
**Where new things go:** a new backend = a new `*_resolver.py` implementing the Protocol.
**To extend:** implement `Resolver` (read/write/head/exists/provenance); select by config; provide a one-time backfill. The graph never changes — that's the whole point of the indirection.
**Seam:** speaks C1 grammar; implements C4; called by [[runtime — constitution]].
**Never:** mutate `cas://` content · put a backend type above the Protocol · store the DB under `/mnt/c` · lose old versions · write a chat turn without a `source` tag (breaks the twin echo-guard).

## What's in here

The **addressed store and its resolver** — the one piece that turns an address into bytes
and back, so the rest of the system holds *addresses*, never content. Everything durable
flows through here: the events the runtime emits, the chat turns (with their provenance
tags), the surfaced results, and the panels' persisted state — each written by address and
read by address through the same Resolver Protocol. The backend behind the address is
swappable (filesystem-first, Supabase later) precisely because the address never changes.
See [[Company Map]] for where the store sits in the whole picture.

**Space-keyed vectors (cognition-engine GROUP L).** A source item is a POINT in MANY PROJECTION SPACES
(principle/topic/vocab/…) — its principle-embedding and its topic-embedding are DIFFERENT vectors of the
SAME item. The store holds all of them THROUGH the C1 grammar (not an address hack): a spaced vector rides
the existing `vec://<source-address>#emb=<model>` shape with a `#space=<projection>` fragment
(`vec://<item>#space=<proj>`, composed by `FsStore.space_address(source, space)`), one file per
(item, space). The default/unspaced vector keeps its BARE source address as the key (back-compat — old
single-space vectors are byte-for-byte untouched). **Portable by FIELD, not by string-parse:** `put_vector`
carries `space` (None | projection) and `source` (the bare item address) as EXPLICIT record fields, so the
per-space filter is a clean field match a Supabase backend implements as `WHERE space = X` — the address
fragment is only the unique key, never the thing a backend must parse. `index_corpus(space=…)` /
`index_addresses(space=…)` / `vector_index.query_index(space=…)` default to `space=None` = the
DEFAULT/unspaced entries ONLY (a spaced entry NEVER leaks into the default corpus — that would pollute
retrieval and crash `retrieve._cosine` when two projections differ in dim); a named space returns the
SOURCE items (round-trips); `FsStore.ALL_SPACES` enumerates everything. `build_index(space=…)` keys its
incremental diff on the SPACED address (the same item in two spaces is independent). All params are optional
kwargs — every prior caller is unchanged. NEXT (a later STORE pass, NOT done here): marks-generalization —
the finding/disposition store extended with a claim/span target + `mark_type` retrieval.

## Relates to

- **Called by** [[runtime — constitution]] — everything that persists, and everything read
  back, goes through the store by address; the runtime never touches a backend directly.
- **Governed by** [[contracts — constitution]] — C1 (the address grammar + provenance) and
  C4 (the Resolver Protocol) are the shapes every backend here obeys.

## Read next
[[Company Map]] (where the store sits in the whole picture) · [[runtime — constitution]] (what reads and writes through it) · [[Concepts and Principles]] (immutability, addressing, provenance).
