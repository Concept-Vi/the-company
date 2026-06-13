# Read 2 — The Company Store (store-of-record readiness for the merge)

**Scope of this read.** Answer one question with code-grounded evidence: *can the Company's store
(`/home/tim/company/store/` + the layers around it) be the single store-of-record for the planned
merge — a RAW CONVERSATION BEDROCK (75,374 raw exchanges from episodic-memory) AND the GENERATED
CONTENT layer (every projection/record/mark, all derived from transcripts) — or does the storage
layer need a rebuild/extension?*

**The lens (Tim's intentional architecture), restated.** There is a clean split:
- **THE CONVERSATION STORE** — raw transcripts, the *only* primary source. (Episodic-memory's
  10.87 GB SQLite holds these today; see `reads/` siblings + INVENTORY.md.)
- **ALL GENERATED CONTENT** — every record/document in every system, all *derived* from transcripts,
  none hand-authored, currently DORMANT/unused/incomplete production material.

This read evaluates whether the Company store is the right physical home for **both**.

**Evidence classification** is marked inline: **Observed** (read directly in code/on-disk, no
execution), **Inferred** (pattern-matched, not verified), **Verified** (confirmed by running).
Files cited with absolute paths + line anchors.

---

## 0. TL;DR (read this, then the evidence)

- **Physical backend:** **plain filesystem on ext4** — one directory per namespace under a single
  store root, JSON files (content-addressed objects + mutable ref pointers) plus append-only
  `*.jsonl` logs. **Not** SQLite, **not** sqlite-vec, **not** Chroma. The live root is
  `/home/tim/company/.data/store/`. **Observed.**
- **Vector store:** **also the filesystem** — `store/.data/store/vectors/`, **one JSON file per
  (item, space)**, each holding the raw embedding as a Python list. Model **BAAI/bge-m3**, **dim
  1024**, space-keyed via the C1 address grammar. **2,186 vectors live right now. Observed.**
- **D1 verdict (can it be the single store-of-record for the merge): NO — not the filesystem
  backend as it stands. The *architecture* (the address grammar + the Resolver Protocol seam) is
  ready and explicitly designed for this; the *current filesystem implementation* is not, by its
  own authors' stated design.** It would need the long-promised **Supabase/Postgres + pgvector
  backend** (the `*_resolver.py` the constitution names but which **does not exist yet**) before it
  can hold 75k raw exchanges + 75k× N-space vectors + millions of provenance/relation edges. The
  filesystem is correct as the *generated-content* store at today's scale (thousands of records);
  it is structurally wrong as the *raw-bedrock* store at 75k+ exchanges. **Observed + Inferred.**

---

## 1. The physical store backend

### 1.1 What it is — `FilesystemResolver` (`FsStore`)

**Observed.** `/home/tim/company/store/fs_store.py` is the *only* concrete backend. Its docstring
(lines 1–13) names it: *"FilesystemResolver — the addressed store (C1/C4)."* It implements
`contracts.resolver.Resolver` (the C4 Protocol, `/home/tim/company/contracts/resolver.py`).

The constitution (`/home/tim/company/store/AGENTS.md:13`) states the design intent verbatim:
> "the addressed store + the resolver — turns an address into bytes and back. Implements C1
> (grammar/provenance) + C4 (Resolver Protocol). **Filesystem-first; Supabase later.**"

And (`store/AGENTS.md:15–16`):
> "**Where new things go:** a new backend = a new `*_resolver.py` implementing the Protocol.
> **To extend:** implement `Resolver` (read/write/head/exists/provenance); select by config; provide
> a one-time backfill. The graph never changes — that's the whole point of the indirection."

So the filesystem backend is **explicitly Phase 1**, with a swap-the-backend-behind-the-address
plan baked in. **The Supabase backend is named, designed-for, and NOT yet built.** **Observed** —
I grepped `store/` and `runtime/` for any `supabase`/`pgvector`/`psycopg`/`*_resolver.py` and found
only `contracts/resolver.py` (the Protocol itself) and unrelated library files in the venvs. There
is exactly one resolver in the system, and it is the filesystem one.

### 1.2 On-disk layout (Observed, live)

Root: `/home/tim/company/.data/store/`. `FsStore.__init__` (`fs_store.py:120–123`) creates one
directory per namespace:

```
.data/store/
  objects/       immutable content-addressed blobs (cas://)        — 8,672 files live
  refs/          mutable logical→cas pointers (run:// "head")       — 7,886 files live
  ref_history/   per-ref append-only (ts,cas) version trail (L6)
  meta/          provenance records, one .json per address          —    87 files live
  memo/          the memoization gate (signature→cas)
  graphs/        canvas/graph registry, one .json per graph         —    73 files live
  surfaced/      the non-blocking decision inbox (S7/D4)            —    90 files live
  locks/         one fcntl lock FILE per resource (cross-process)
  vectors/       the persisted vector index, one .json per (item,space) — 2,186 files live
  sessions/      review-session state (created lazily)
  journeys/      recorded ui:// click-paths (created lazily)
  chat_threads/  conversation-thread metadata (created lazily)
  + root-level append-only logs:
      events.jsonl       the durable trajectory + the corpus index  — 5,062 lines / 1.9 MB live
      chat.jsonl         RHM chat turns (source/grade tagged)        —   210 lines / 136 KB live
      marks.jsonl        the marks layer (Group M)                   —   8.5 KB live
      annotations.jsonl  ui:// comments (I6)                         —   2.6 KB live
      findings.jsonl     coherence findings (C1)
      dispositions.jsonl finding dispositions (C2, last-wins overlay)
      pins.jsonl         pin-state overlay (X7)
```

Total live `.data/` is **169 MB. Observed.** (This is the GENERATED layer at its current,
early scale — a few thousand records. Nothing near the bedrock's 10.87 GB / 75k exchanges.)

### 1.3 Durability + concurrency (Observed — relevant to "ready as store-of-record")

These are *real* engineering, already done, and they are the part of the filesystem backend most
worth preserving conceptually:

- **Immutability of `cas://`** (`fs_store.py:184–198`, `put_content`): content is blake2b-hashed
  (`_hash`, line 176–177, `cas://b2:<hex>`, digest_size=16 → 128-bit), written write-once, never
  mutated. "An update is a new object + a moved pointer" (`AGENTS.md:13`). **Observed.**
- **Atomic + crash-durable writes** (`_atomic_write_fsync`, lines 101–116): write to a unique tmp
  (pid+thread), `fsync` the bytes, `os.replace` (atomic same-fs rename), `fsync` the parent dir.
  Used by every hot pointer write (`set_ref`, `save_graph`, `save_surfaced`, `save_session`,
  `put_vector`, `write_provenance`, `memo_set`). **Observed.**
- **Cross-process locking** (`_CrossProcessLock`, lines 27–82; `graph_lock`/`dispatch_lock`,
  144–173): a re-entrant lock composed of a thread `RLock` (outer) + an `fcntl.flock` on a per-key
  lockfile under `locks/` (inner, taken only at the outermost acquire via a per-thread depth
  counter). Serializes graph load→mutate→save and the wire's exactly-once dispatch CHECK→CLAIM
  across BOTH threads and processes. **Observed.**
- **One stated non-cross-process gap:** `append_event` seq-assignment (`fs_store.py:445–467`) is
  atomic *within one process* (`_event_lock`) but the code comment itself (lines 438–444) says it is
  **NOT cross-process** — two processes can both read seq=N and append N+1 → a duplicated seq. The
  authors deliberately surfaced this rather than wrap the hottest write path in fcntl. **Observed.**
  *This matters for the merge:* the corpus index rides `events.jsonl` seqs (see §5).

**These durability/concurrency guarantees are filesystem-backend properties expressed entirely
behind the resolver seam** (`fs_store.py:6–12` PORTABILITY docstring): the engine calls
`store.graph_lock(gid)` and never knows whether a thread lock, an OS file-lock, or a Postgres
advisory lock enforces it. **A Supabase backend would re-implement the same methods with
backend-native concurrency/durability and the engine would not change.** **Observed (design
statement) + Inferred (that the swap is actually clean — not executed).**

---

## 2. The addressed-record schema (C1 grammar)

**Observed.** `/home/tim/company/contracts/address.py` declares the grammar (lines 1–45):

```
run://<domain>/<intent>/<node>@<branch>#run=<id>   mutable pointer
cas://<algo>:<hash>                                 immutable content
blob://<algo>:<hash>                                large binary (addressed, not inlined)
vec://<source-address>#emb=<model>                  an embedding of a source
ui://<kind>/<ref>                                   a UI component
code://<file-stem>/<symbol>                         a code symbol
skill://<id>                                        a reusable instruction unit
context://<id>                                      a reusable context unit
SCHEMES = ("run","cas","blob","vec","ui","code","skill","context")
```

- **`run://`** and **`cas://`** are the two the *store* resolves (the rest are labels resolved
  elsewhere — `ui://`/`code://` by the Suite's scope resolver, `skill://`/`context://` by
  `runtime/cognition.py:resolve_address`). **Observed** (`address.py:14–41`).
- **Schema-additive law** (`address.py:12`): "add optional fields + bump `schema_ver`; never break
  an existing one." Every record in the store is an **open dict** — `{ts, **rec}` — so new fields
  ride free. This is repeated across every `append_*` method. **Observed.**
- **`Provenance`** (`address.py:48–56`) is the one typed record: `{address, content_hash, type,
  produced_by, inputs[], agent, created_at, schema_ver}`. `inputs[]` is the lineage edge list (what
  an artefact was made FROM). **Observed.**

**Persistence by address — how each scheme is stored** (`fs_store.py`, all **Observed**):
- `cas://<hash>` → `objects/<safe(addr)>` (write-once file). `_safe` (line 180–181) maps
  `://`→`__`, `:`→`_`, `/`→`_` so an address becomes a flat filename.
- `run://...` (a logical "head") → `refs/<safe(addr)>` holding the current `cas://`. `set_ref`
  (215–243) also appends `(ts, cas)` to `ref_history/<safe>` so every address carries a temporal
  version trail (L6, lines 245–275). The *old* bytes always survive (cas is write-once).
- `Provenance` → `meta/<safe(addr)>.json`. `lineage(address)` (297–309) is a breadth-first,
  de-duped, cycle-safe walk back over `inputs[]` toward source.
- `vec://<source>#space=<proj>` → `vectors/<safe>.json` (see §3).

**Round-trip:** `head(logical)` → cas, `get_content(cas)` → the JSON. The rest of the system holds
*addresses, never content* — the indirection that makes the backend swappable (`AGENTS.md:22–28`).

---

## 3. Vectors / embeddings — where they live

**Observed.** Vectors live on the **same filesystem store**, in `vectors/`, as a *sibling
namespace* of `objects/refs` — **not** a separate vector DB. `store/vector_index.py` is the
*orchestration* (build/query/staleness) on top; `fs_store.put_vector/get_vector/index_corpus`
are the *substrate* (fabric-free — the store never calls a model).

- **One file per (item, space)** (`fs_store.py:841–877`, `put_vector`). The record:
  `{address, vector:[...], content_hash, dim, model, space, source, ts}`. Stored atomically
  (tmp+fsync+replace). **Observed.**
- **Live sample** (Verified by reading one on disk):
  `dim=1024, model="BAAI/bge-m3", space="repo", vector length 1024`. **Verified.**
- **Config** (`fabric/config.py:26–37`): `DEFAULT_EMBED_MODEL=BAAI/bge-m3`,
  `DEFAULT_EMBED_DIM=1024`, `DEFAULT_EMBED_URL=http://localhost:8001/v1` (an OpenAI-shaped local
  embed endpoint). **Observed.**
- **Space-keyed vectors (cognition GROUP L)** (`AGENTS.md:30–45`, `fs_store.py:803–948`): one source
  item is a POINT in MANY projection spaces (principle / topic / repo / worldview / history / …) —
  its principle-embedding and topic-embedding are DIFFERENT 1024-vectors of the SAME item. The
  spaced key rides the C1 grammar: `vec://<source>#space=<proj>` (`space_address`, 829–839). `space`
  and `source` are **explicit record fields** (not just buried in the key string) "so the per-space
  filter is a clean field match a Supabase backend implements as `WHERE space = X`." **Observed.**
- **Ranking is reused, not reimplemented** (`vector_index.py:142–172`, `query_index`): it builds
  `store.index_corpus(space=…)` → `[{id, vector}]` and feeds the existing `nodes/retrieve` cosine
  node. A dim mismatch fails loud there. **Observed.**
- **The embedder is DOWN by default** (`vector_index.py:38–44, 117–132`): when `:8001` is
  unreachable the build writes NO vectors, emits a loud `warning` event, returns `degraded:True`,
  never fabricates a zero-vector. So the index is **honestly partial** when the embed stack isn't
  up. (2,186 vectors exist, so it *has* been run with the stack up.) **Observed.**

**Critical mismatch for the merge (Observed):** the Company embeds at **bge-m3 / 1024-dim**; the
episodic bedrock embeds at **MiniLM/bge-small / 384-dim** (INVENTORY.md:88 — `FLOAT[384]` hardcoded
in `vec_exchanges`). The 75,375 existing episodic vectors are **dimensionally incompatible** with
the Company's retrieval (`retrieve._cosine` fails loud on a dim mismatch — by design). A merge that
wants the bedrock searchable in the Company's spaces must **re-embed all 75k exchanges at 1024-dim**
(or stand up a 384-dim space alongside — the space-keying makes mixed-dim *coexistence* legal, but
not cross-space cosine). This is a real, quantified cost, not a detail.

---

## 4. The projection + relation + mark layers

This is the GENERATED-CONTENT layer's vocabulary — the lenses and edges that turn raw transcript
into described, related, marked corpus. All three are **file-discovered registries** (registry-is-
truth: add-a-row = add-a-FILE, no code edit), mirroring roles/skills/node-types.

### 4.1 Projections (`projections/`, `projections/AGENTS.md`) — the LENSES. **Observed.**

A **projection** is a declared LENS over a corpus unit — "one named way to DESCRIBE a file/unit."
Each `projections/<id>.py` is a `PROJECTION` dict `{id, level, produced_by, embeds, field, …}`.
`embeds:true` → that lens becomes a **vector SPACE** (§3). Live set:
- `what` (no-embed), `topics` (embeds), `repo` (embeds), `principles` (embeds), `worldview`
  (embeds), `claimed_status` (no-embed enum), `lineage` (code-extracted, no-embed), and —
  **directly load-bearing for this merge** —
- **`history`** (`projections/history.py`, agent-authored, embeds:true, level=meaning): its own
  `desc` reads:
  > "the session-history lens (③/⑨ — G23): one mined exchange-extract per unit — decisions,
  > corrections, failures, patterns from the conversation record; embedded so failure-patterns
  > cluster and past context retrieves (**durable cross-session memory on the corpus, NOT
  > episodic-memory**)."

  **This is the merge already declared in the architecture.** The Company *intends* to hold mined
  conversation extracts as a `history`-projection space and explicitly frames it as the
  *replacement* for episodic-memory. The lens exists; what's missing is the bedrock under it and the
  ingest at scale. **Observed.**

A "render-NOT-judge" law (K3, `AGENTS.md:55`) governs lenses: a lens DESCRIBES; judgement is a later
reduce pass. **Observed.**

### 4.2 Relation-types (`relation_types/`, `relation_types/AGENTS.md`) — the GRAPH edges. **Observed.**

A **relation-type** is a declared KIND of typed/directional edge between two corpus units — the
vocabulary `find_relations` (L3) labels its discovered relations with. Live set: `principle_beneath`
(directed), `fragment_of` (directed, has inverse `has_fragment`), `contradicts` (directed),
`sibling` (symmetric), plus agent-authored `depends_on` and `precedes`. Each is one
`RELATION_TYPE` dict `{id, directed, inverse, near, far, label, desc}`. `near`/`far` name the
projection SPACES the inversion-finder set-operates over (e.g. near=`principles`). **Observed.**

**Where do relation EDGES physically persist?** This is a gap to flag. The relation-*types* are a
registry (files). But `find_relations` is documented as a **SEPARATE coordinated wiring pass, NOT
built in this lane** (`relation_types/AGENTS.md:52–53`). **Observed.** A discovered relation is a
*finding the operator reviews* — so it would land in the marks/findings leaf (§4.3), keyed by
`target` (which can be a `claim://`/`span://`). **There is no dedicated edge table.** At the
filesystem scale this is fine; at "millions of provenance edges" it is the single biggest scaling
question (see §6). The store's *provenance* edges (`inputs[]` in `meta/*.json`) are a different,
already-built axis (§2) — but they are per-artefact files, not a queryable edge index.

### 4.3 Mark-types + the marks store (`mark_types/`, `fs_store.py:648–752`) — the FINDING/disposition layer. **Observed.**

A **mark** is what a mark-pass (`run_role`/`run_reduce`) writes about a source item — the coherence
finding store, GENERALIZED along two axes (`AGENTS.md:48–69`):
1. **TARGET** (not just an address): a `claim://` or `span://` sub-region as well as a plain address.
   The store treats `target` as an **opaque string** (does not parse the grammar).
2. **`mark_type`** (an id from the `mark_types/` registry) + payload `{value, confidence,
   source_pass, evidence}`.

Marks ride a **sibling `marks.jsonl` leaf** (`append_mark`/`marks_for`/`marks_by_type`/`all_marks`,
lines 677–752), reusing the append-only / field-match pattern. **Why a sibling and not
`findings.jsonl`:** `all_findings()` feeds `coherence_detect.burn_down`, which counts every finding;
a mark in `findings.jsonl` would inflate the burn-down. **Observed.** Marks **fail loud** if
`target`/`mark_type` is missing (an unfindable mark = a silent black hole, store rule 4, lines
692–699). Live: 8.5 KB of marks. Live mark-types: `gold_likelihood` (score/surface), `ai_fingerprint`
(label/subtract — the inversion: noise to subtract), `contradiction` (span), `built_twice` (claim),
`overlap` (claim). **Observed.**

**The whole generated-content vocabulary is portable-by-FIELD**: `target`, `mark_type`, `space`,
`source`, `address`, `lineage.project` are all explicit record fields, repeatedly justified in the
code comments as "a clean SQL `WHERE … = X` a Supabase backend implements." The authors wrote the
filesystem layer *anticipating* the SQL backend. **Observed.**

### 4.4 Projections (the "history" projection of the store itself)

`projections/` also includes view-builders like `history.py` the *projection registry* lens AND
there is a runtime `history` projection over the store (the `events.jsonl` trajectory). Note the
word "history" is overloaded: (a) the `history` PROJECTION lens (mined exchange extracts, §4.1);
(b) `ref_history` (per-address version trail, §2); (c) the event-log trajectory. Three distinct
axes — do not conflate. **Observed.**

---

## 5. How `kind: capture` records persist (the live record you read)

**Observed.** The writer is `/home/tim/company/runtime/corpus.py:write_record` (lines 122–194) —
"the corpus-record WITH LINEAGE (Cognition Engine D1 · the sequencing GATE)." This is a **thin
module over the store** — it makes NO `fs_store` edit; it uses only `put_content` + `set_ref` +
`append_event`. Per unit (or unit×projection) it writes:

1. **The content** (`record`, lines 165–173): `{source_address, output, kind, model, projection,
   lineage, **extra}` → `store.put_content(record)` → an immutable `cas://`. **Deterministic
   content** (no per-write timestamp in the cas) so a resumed re-write hashes to the SAME cas — a
   true no-op. **Observed.**
2. **The pointer** (line 175): `store.set_ref(address, cas)` where `address` =
   `corpus_address(source_address, project, projection)` = `run://corpus/<project>/<source>[/<proj>]`
   (deterministic — resume-safe). **Observed.**
3. **The index** (lines 178–193): a DISTINCT durable event kind **`corpus.record`** appended to the
   ONE `events.jsonl` (NOT `op.run` — that's a closed engine-run grammar). "The log IS the index —
   no maintained index, no parallel DB." **Observed.**

**The live record I cross-checked on disk** (Verified, from `.data/store/events.jsonl`):
```
seq 2209 · kind "corpus.record" · record_kind "capture" · projection "repo"
address        run://corpus/company/code://contracts/shapes.py/repo
source_address code://contracts/shapes.py
lineage {session: "exocortex-ingest-2", round: "1", project: "company"}
```
This matches the prompt's described shape (kind=capture, projection, source_address, output). The
`history`-projection sibling (the bedrock case) would be: `record_kind:"capture"`,
`projection:"history"`, `source_address` = an exchange address, `output` = the mined extract,
`lineage` = {session, round, project} of the source conversation. **Observed + Inferred (the
history case not yet run at scale).**

**THE LINEAGE GATE (the headline, lines 1–15, 97–119):** the writer **REFUSES** a record missing
`session/round/project` (fail-loud, not optional-with-default). Rationale: corroboration (M3) is
**cross-session** (high recurrence of a principle ACROSS sessions = a corroboration mark), and the
inversion-finder (L2) needs to know which session a record came from. **A record written without
lineage can never be corroborated cross-session.** **Observed.** *This is directly load-bearing for
the merge:* every one of the 75,374 raw exchanges, when ingested as a corpus record, MUST carry
`{session, round, project}` — and episodic-memory *does* archive per-session JSONL per project, so
the lineage is recoverable from the source paths. **Observed (the gate) + Inferred (that episodic's
per-session/per-project archive supplies it cleanly — not executed).**

**Read-back / projection:** `read_record` (197–205) = head→get_content. `list_corpus`/`find_corpus`
(208–242) are a **read-time projection over `events_since(-1)` filtered to `kind=="corpus.record"`**,
dedup-on-read by corpus address (latest seq wins — resume-safe). **No maintained index.** **Observed.**

---

## 6. Capacity / readiness — could this hold 75k+ raw exchanges + millions of edges?

This is the D1 crux. All **Observed** from code unless marked.

### 6.1 The filesystem's scaling shape

**One file per record, flat directories, no sharding.** `objects/`, `refs/`, `vectors/`, `meta/`
are each a single flat directory; the key is `_safe(address)` (no `aa/bb/` fan-out)
(`fs_store.py:187, 226, 875`). Today: 8,672 objects, 7,886 refs, 2,186 vectors. **Observed.**

Project the merge onto this shape:
- 75,374 raw exchanges as corpus records → **~75k `cas://` files in `objects/`** + **~75k `refs/`
  files** + (if the `history` lens embeds) **~75k `vectors/` files** — and, because a unit is a
  point in MANY spaces, potentially **75k × (number of embedding spaces)** vector files. With the
  6 embeddable lenses live (topics/repo/principles/worldview/history + any future), that is
  **on the order of 300k–450k vector JSON files in one flat directory.** **Inferred (arithmetic
  from the per-(item,space) design, not executed).**
- ext4 handles large directories (htree), but **a flat directory of hundreds of thousands of small
  JSON files is the known weak spot**: `index_addresses`/`index_corpus` do `sorted(dir.glob("*.json"))`
  then **read and JSON-parse EVERY file on every call** (`fs_store.py:905–948`). At 300k+ files that
  is a multi-second-to-minutes full-scan per query, all in Python, no index. **Observed (the read
  pattern) + Inferred (the wall-time at scale — not benchmarked).**

### 6.2 The event-log scaling shape (the sharper constraint)

`events.jsonl` is the corpus INDEX. Every read projection — `list_corpus`, `find_corpus`,
`recent_events`, `events_since`, the SSE stream — does `path.read_text().splitlines()` over the
**entire file** (`fs_store.py:469–492`, `corpus.py:217`). **Observed.**

- Today: 5,062 lines / 1.9 MB. Adding 75k `corpus.record` events (one per exchange, more per
  projection) makes `events.jsonl` **75k–450k lines / tens-to-hundreds of MB**, and **every
  `list_corpus` call re-reads and re-parses the whole thing** to fold the corpus projection.
  **Observed (pattern) + Inferred (the cost).** This is the "the log IS the index" decision meeting
  scale — elegant at thousands, a full-table-scan-per-query at hundreds of thousands.
- The **seq-uniqueness gap is not cross-process** (`fs_store.py:438–444`, §1.3). A high-volume,
  multi-process bedrock ingest is exactly the workload that would trip duplicate seqs — and the wire
  binds on `seq`. The authors flagged this as a deliberate shared-semantics decision to surface, not
  silently build. **Observed.**

### 6.3 Provenance / relation edges

`meta/*.json` holds `inputs[]` per artefact (one file per address). `lineage()` walks them at read
time. Relation edges (`find_relations`) are **not built yet** and have **no edge table** — they
would land in `marks.jsonl`/`findings.jsonl` as findings (§4.2). "Millions of provenance edges" as
per-file JSON + whole-file `.jsonl` scans is **structurally the wrong shape**; this is precisely what
a relational/graph backend (Postgres rows, or pgvector + a join table) exists for. **Observed +
Inferred.**

### 6.4 What the authors already built FOR the swap (the good news)

The entire layer is written to make the Supabase swap mechanical, and this is **Observed** in code
comments throughout, not speculation:
- Every record carries its filter keys as **explicit fields** (`space`, `source`, `target`,
  `mark_type`, `lineage.project`, `content_hash`) with comments naming the SQL `WHERE` they map to.
- The **Resolver Protocol** (`contracts/resolver.py`) is the entire swap surface; the durability/
  concurrency are sealed behind it (`fs_store.py:6–12`).
- The constitution names the migration path: "a new backend = a new `*_resolver.py` … select by
  config … provide a one-time backfill" (`AGENTS.md:15–16`).

So the *generated-content schema* (the records, the projection/relation/mark vocabulary, the
lineage gate, the content-addressing) is **ready to be carried into a SQL/pgvector backend
unchanged**. What is NOT ready is the *physical filesystem implementation* as the home for the raw
bedrock at 75k+ scale.

---

## 7. D1 verdict — with evidence

**Question:** can the Company store be the single store-of-record for the merged conversation
bedrock (75,374 raw exchanges) + the generated content layer?

**Verdict: ARCHITECTURE YES / CURRENT BACKEND NO. The merge requires building the long-designed
Supabase/Postgres + pgvector resolver (a `*_resolver.py` that does not exist yet) before the store
can be the store-of-record for the raw bedrock. The filesystem backend stays correct for the
generated layer at today's scale, but is structurally wrong for 75k+ raw exchanges + their multi-
space vectors + relation/provenance edges.** This is an **extension along an already-designed seam,
not a rebuild of the schema** — the address grammar, the record shapes, the projection/relation/mark
registries, and the lineage gate all carry over unchanged.

**Evidence chain:**
1. The store is filesystem-first by explicit design, "Supabase later," with the swap-the-backend
   plan written into the constitution (`store/AGENTS.md:13–16`). **Observed.** The Supabase resolver
   **does not exist** (grep of `store/`+`runtime/` finds only `contracts/resolver.py`). **Observed.**
2. Read paths full-scan flat directories and whole `.jsonl` files (`fs_store.py:469–492, 905–948`;
   `corpus.py:217`). At 75k–450k files / hundreds-of-MB logs this is a full-scan-per-query.
   **Observed (pattern) + Inferred (wall-time).**
3. The event-log seq is not cross-process-unique (`fs_store.py:438–444`) — a hazard for a high-
   volume multi-process bedrock ingest, surfaced by the authors as a pending decision. **Observed.**
4. The bedrock's 384-dim vectors are dim-incompatible with the Company's 1024-dim bge-m3 retrieval
   (INVENTORY.md:88 vs `fabric/config.py:37`); the merge must re-embed 75k exchanges (or run a
   parallel 384-dim space). **Observed.**
5. BUT the schema is portable-by-field and sealed behind the Resolver Protocol — the generated
   layer carries over unchanged; the `history` projection *already declares itself the replacement
   for episodic-memory* (`projections/history.py`). **Observed.**

**The split the merge should make** (aligned to Tim's lens, **Inferred** as the cleanest reading):
- **Raw conversation bedrock (75k exchanges, primary source):** belongs in the **Supabase/pgvector
  backend** (the to-be-built resolver) — a `conversation://` or `exchange://`-addressed namespace,
  rows + a pgvector column, re-embedded at the Company's model/dim. The filesystem cannot be the
  bedrock home at this scale.
- **Generated content layer (corpus records, projections, marks, relations):** *already* lives in
  the Company store correctly; it scales into the same Supabase backend trivially because every
  record is portable-by-field. At today's thousands-scale the filesystem is fine; it rides the same
  swap when the bedrock forces the backend up.

So **one store-of-record, two namespaces, one new backend** — the Company store *becomes* the single
store-of-record **after** the pgvector resolver is built and the bedrock is ingested+re-embedded into
it under the lineage gate.

---

## 8. What's dormant / half-built (flagged, per assume-more-work)

- **The Supabase/pgvector backend itself: NOT BUILT.** Named in the constitution, designed-for in
  every field, zero implementation. This is the gating dependency for D1. **Observed.**
- **`find_relations` (L3, the relation-edge wiring): NOT BUILT** — explicitly "a SEPARATE coordinated
  pass, NOT built in this lane" (`relation_types/AGENTS.md:52–53`). The relation-*types* are
  registered (files exist), but no edges are discovered/persisted/queried yet, and there is no edge
  table. **Observed.**
- **The `history` projection: declared but unpopulated at scale.** The lens file exists
  (`projections/history.py`) and frames itself as the episodic-memory replacement, but there is no
  bedrock under it — the mined-exchange corpus is the merge's deliverable, not yet present.
  **Observed.**
- **The marks/findings layer is live but thin** (8.5 KB marks, small findings) — the GENERATED layer
  is early/dormant production material exactly as the lens frames it. **Observed.**
- **Vector index is honestly partial** — built only when the `:8001` embed stack is up; 2,186
  vectors exist. The `index_staleness` interrogation exists but the LIVE re-population is named as a
  follow-up (`vector_index.py:38–44`). **Observed.**
- **Event-log cross-process seq-uniqueness: a surfaced, undecided gap** (`fs_store.py:438–444`).
  **Observed.**
- **Several record types are created lazily** (`sessions/`, `journeys/`, `chat_threads/` only made on
  first write) — present in code, little/no live data. **Observed.**

---

## 9. The 3 most important facts (for the deliverable callback)

1. **The Company store is a plain ext4 filesystem (content-addressed JSON objects + mutable ref
   pointers + append-only `.jsonl` logs), and its vector store is the SAME filesystem — one JSON
   file per (item, space), bge-m3 / 1024-dim. It is NOT SQLite/sqlite-vec/Chroma, and the
   Supabase/pgvector backend it was designed to swap to DOES NOT EXIST yet** (only the
   FilesystemResolver implements the Protocol).
2. **The architecture is merge-ready; the backend is not. The address grammar, the open-record
   schema, the file-discovered projection/relation/mark registries, and the fail-loud
   session/round/project lineage gate all carry over to a SQL/pgvector backend unchanged
   (every filter key is an explicit field, by design) — but the filesystem implementation
   full-scans flat directories and whole `.jsonl` logs, which is structurally wrong for 75k+ raw
   exchanges (→300k–450k vector files, hundreds-of-MB event log re-parsed per query) and for
   millions of relation/provenance edges (no edge table; `find_relations` unbuilt).**
3. **The `history` projection (`projections/history.py`) already declares itself "durable
   cross-session memory on the corpus, NOT episodic-memory" — the merge is named in the
   architecture as the replacement for episodic-memory. The bedrock's 384-dim vectors are
   dim-incompatible with the Company's 1024-dim retrieval, so the 75,374 exchanges must be
   re-embedded (or run as a parallel 384-dim space) on ingest, each carrying recoverable
   session/round/project lineage from episodic's per-session/per-project archive.**

---

*Read 2 of the episodic-memory-adaptation reads set. Sibling docs: `INVENTORY.md` (the episodic
source, Observed/Verified), `LANDSCAPE.md` (the memory-systems survey), `MERGE-INTENTION.md`,
`UPSTREAM-DOCS.md`. This read is provisional where marked Inferred; the two largest unverified
claims are the wall-time of the filesystem read-paths at 75k+ scale (not benchmarked) and the
cleanness of the Supabase swap (design statement, not executed). Both are worth a verification pass
before the merge backend is committed.*
