# store/fs_store_file_vectors.retired.py — THE PRE-SUPABASE FILE-BACKED VECTOR NAMESPACE (RETIRED 2026-07-02)
#
# ① of NORTH-STAR (Tim-authorized cutover): the vector namespace moved to Supabase `ledger.embedding`
# (store/pg_vectors.py — pgvector 0.8.2, halfvec multi-dim, HNSW; search runs IN Postgres). Per Tim's
# no-fallback rule these original file-IO implementations are preserved COMMENTED OUT — effectively
# removed, zero influence, but legible + recoverable. They were the methods of FsStore reading/writing
# .data/store/vectors/*.json (one file per vector, mtime-cached, numpy space matrices).
#
# To restore: paste these bodies back over the delegating methods in store/fs_store.py (same names,
# same signatures) and remove the pg_vectors delegation. The .data/store/vectors/ files were left
# intact at cutover (not deleted) — data recovery needs no re-embed for anything already there;
# anything embedded AFTER the cutover exists only in ledger.embedding (migrate back via a reverse of
# ops/migrate_vectors_to_supabase.py).
#

#     def put_vector(self, address: str, vector: list, content_hash: str, *, dim: int, model: str,
#                    space: str | None = None, source: str | None = None, emb: str | None = None) -> dict:
#         """Persist one {address: vector} entry into the vectors/ namespace, ATOMICALLY (crash-durable
#         tmp+fsync+os.replace — the SAME guarantee save_surfaced/save_graph give, so a reader sees the whole
#         old entry or the whole new one, never a torn one). Keyed by _safe(address). Schema-additive open
#         record. The store does NOT validate the vector (no model here) — the dim contract is enforced UP at
#         the embed fabric (complete_embeddings dim= guard) and DOWN at the query cosine (retrieve._cosine);
#         the store just persists the bytes by address.
#
#         SPACE-KEYED (additive — every prior caller is unchanged): when `space`/`source` are given, the entry
#         records WHICH projection space it belongs to (`space`) and WHICH source item it embeds (`source`),
#         as EXPLICIT FIELDS (the portable per-space filter key — see the class-comment above). `address` is
#         still the storage key (the composed `vec://<source>#space=<proj>` for a spaced entry — callers
#         compose it via `space_address`). Omitting both = the default/None space (the unspaced legacy entry,
#         keyed by its bare source address) — byte-for-byte the prior shape PLUS the two additive fields
#         defaulting to None, so old readers (index_corpus/index_addresses with no space filter) see it
#         exactly as today."""
#         import json as _j
#         from datetime import datetime, timezone
#         # FAIL LOUD (rule 4): a SPACED entry MUST name its source item — `source` defaults to `address`, which
#         # for a spaced entry is the composed `vec://…#space=` KEY, not the bare item. Letting that default
#         # through would silently record a wrong round-trip (a per-space query would return the internal key,
#         # not the item). build_index always passes the bare source, so this only bites a direct misuse.
#         if space is not None and source is None:
#             raise ValueError(
#                 f"put_vector: a spaced entry (space={space!r}) must pass `source` (the bare item address it "
#                 f"embeds) — defaulting source to the composed key {address!r} would record a wrong round-trip.")
#         (self.root / "vectors").mkdir(parents=True, exist_ok=True)   # defensive (mirrors save_session) — never assume __init__ ran
#         rec = {"address": address, "vector": list(vector), "content_hash": content_hash,
#                "dim": int(dim), "model": model, "space": space, "emb": emb,
#                # `source` defaults to the bare address for an unspaced entry (it IS its own source) so the
#                # field is always present + truthful — a spaced entry carries the bare item address it embeds.
#                "source": source if source is not None else address,
#                "ts": datetime.now(timezone.utc).isoformat()}
#         path = self.root / "vectors" / (self._safe(address) + ".json")
#         self._fsync_atomic_write(path, _j.dumps(rec))
#         return rec
#
#     def get_vector(self, address: str) -> dict | None:
#         """The persisted vector entry at `address`, or None if never built (an HONEST None — never a
#         crash, never a fabricated zero-vector; rule 4). Reads disk every call (no in-memory cache), so a
#         SECOND store over the same root sees a prior store's vectors (persistence-survives-reload)."""
#         import json as _j
#         p = self.root / "vectors" / (self._safe(address) + ".json")
#         return _j.loads(p.read_text()) if p.exists() else None
#
#     def remove_vector(self, address: str) -> bool:
#         """RETRACT one persisted vector by its storage `address` (the composed `vec://…#space=` key for a
#         spaced entry — compose via `space_address`, the SAME key put_vector stored under). Returns True if a
#         file was removed, False if none existed (honest, never a crash — idempotent retract). The next
#         `_vector_records()` scan drops it from the cache + bumps `_vec_version` automatically (file-vanished
#         eviction is already handled there), so the matrix cache / rankings refresh with NO staleness.
#
#         ★ Closes the harvested architectural gap (2026-06-22): embed was incremental-ADD-only with no way to
#         RETRACT an embedded vector, so a cleaned asset's stale vectors persisted in the live space. This is the
#         non-destructive-to-the-source retract: it removes the INDEX entry only (the source asset/CAS is
#         untouched), so a re-embed rebuilds it. Atomic at the filesystem level (a single os.unlink)."""
#         p = self.root / "vectors" / (self._safe(address) + ".json")
#         try:
#             p.unlink()
#             return True
#         except FileNotFoundError:
#             return False
#
#     def remove_vectors(self, addresses) -> int:
#         """Bulk RETRACT — remove many vectors by storage address. Returns the count actually removed (absent
#         ones are skipped, not errors). One pass; the next `_vector_records()` evicts them all + bumps the
#         version once. Use for cleaning an out-of-scope slice from a space (compose each address via
#         `space_address(source, space, emb)`)."""
#         return sum(1 for a in addresses if self.remove_vector(a))
#
#     # A sentinel for "ALL spaces, no filter" — DISTINCT from space=None ("the DEFAULT/unspaced space only").
#     # The default of the space= kwarg is None (default-space-only), which is exactly the pre-space behaviour
#     # the live callers (consult/R2 query_index, index_staleness) depend on: a spaced entry must NOT leak into
#     # the default corpus, or (a) retrieval is polluted and (b) two projections with different embed-dims make
#     # retrieve._cosine fail-loud the instant they share the corpus. Pass space=ALL_SPACES to enumerate the
#     # whole index regardless of space (used by nothing on the hot path; available for an index-wide audit).
#     ALL_SPACES = object()
#
#     def _vector_records(self) -> list[dict]:
#         """Every persisted vector record, parsed — the ONE read path index_corpus/index_addresses share,
#         with an incremental in-memory cache (X12-FAST, 2026-06-18). The naive path read+parsed all 5862
#         `vectors/*.json` on EVERY call (~1.5s), re-paid per query_index and x8 per recall_for_decision →
#         the >15s decision-surface hang. Here each file is parsed ONCE and revalidated cheaply.
#
#         CORRECTNESS (the cache must never serve a stale ranking — no-silent-failures):
#           - Revalidate EVERY call by a per-file (st_mtime_ns, st_size) signature from a single os.scandir.
#             put_vector writes ATOMICALLY (tmp+fsync+os.replace) → a changed entry gets a new mtime → its
#             signature differs → it is RE-PARSED. A NEW file appears in the scan → parsed. A REMOVED file
#             drops from the scan → evicted. This holds ACROSS PROCESSES (Tim runs many sessions against one
#             store): the signature is read from the filesystem, not an in-process counter, so another
#             session's write is seen on the next call.
#           - Only NEW/CHANGED files are read+parsed — the full ~1.5s parse is paid only on the first call
#             after a (re)start; steady-state is scandir+stat (~10ms for 5862) + parse-of-the-few-changed.
#           - The lock is held ONLY for the refresh (scandir+stat+parse); the returned list is consumed by
#             the cosine/rerank stages OUTSIDE the lock, so a slow/abandoned recall thread never holds it.
#         Returns the list of parsed record dicts (read-only — callers must not mutate them)."""
#         import json as _j
#         d = self.root / "vectors"
#         with self._vec_cache_lock:
#             cache = self._vec_cache
#             if not d.exists():
#                 if cache:
#                     cache.clear()
#                 return []
#             try:
#                 scan = list(os.scandir(d))
#             except OSError:
#                 return []
#             seen = set()
#             out = []
#             changed = False                                  # any new/changed/evicted entry this scan → bump version
#             for entry in scan:
#                 name = entry.name
#                 if not name.endswith(".json"):
#                     continue
#                 seen.add(name)
#                 try:
#                     st = entry.stat()
#                 except OSError:
#                     continue
#                 sig = (st.st_mtime_ns, st.st_size)
#                 cached = cache.get(name)
#                 if cached is not None and cached[0] == sig:
#                     rec = cached[1]                          # UNCHANGED — reuse the parsed record
#                 else:
#                     try:
#                         with open(entry.path, "r", encoding="utf-8") as fh:
#                             rec = _j.loads(fh.read())
#                     except Exception:
#                         cache.pop(name, None)               # torn/unreadable → skip + forget (retry next call)
#                         continue
#                     cache[name] = (sig, rec)               # NEW/CHANGED — parse once, remember
#                     changed = True
#                 out.append(rec)
#             if len(cache) != len(seen):                     # evict entries whose file vanished
#                 for gone in [n for n in cache if n not in seen]:
#                     cache.pop(gone, None)
#                 changed = True
#             if changed:                                      # X12-MATRIX: invalidate the per-space matrix cache
#                 self._vec_version += 1                       # (built lazily, signature-keyed on this version)
#             return out
#
#     def warm_vector_cache(self) -> int:
#         """Populate the X12-FAST in-memory vector cache up front (returns the record count). Called at bridge
#         startup so the FIRST semantic query after a (re)start — e.g. a decision-open, whose memory leg has a
#         3s budget — is already warm; otherwise its cold full-parse (~1.5s) pushes the leg over budget and the
#         decision resolves UNGROUNDED once (verified 2026-06-18: cold first-resolve 3.08s→timeout; after warm
#         1.84s→grounded). Idempotent + cheap when already warm (revalidate-only).
#
#         X12-MATRIX warm (lead 2026-06-21, the SEPARABLE trim): ALSO pre-build the per-(space,emb) cosine
#         matrices for the LARGE named spaces. This is PURE NUMPY (np.asarray over the vectors) — NO chat-4b /
#         cluster-step (that was prewarm_theorem_explains, dropped for the contention-spiral). So it trims the
#         cold-first matrix-rebuild (~30s on the 67k extractions space, measured) WITHOUT re-introducing the
#         bounce-contention = best-of-both. Only spaces above _MATRIX_WARM_MIN (the build/RAM-worth-it ones; the
#         tiny spaces stay lazy — cheap). Best-effort; never blocks startup."""
#         recs = self._vector_records()
#         try:
#             from collections import Counter
#             counts = Counter((rec.get("space"), rec.get("emb")) for rec in recs if rec.get("space") is not None)
#             for (sp, em), n in counts.items():
#                 if n >= _MATRIX_WARM_MIN:
#                     self.space_matrix(sp, em)                 # NUMPY build + cache (no chat-4b) — moves the ~30s off the first-open
#         except Exception:
#             pass                                              # warm is best-effort — never block startup
#         return len(recs)
#
#     def index_addresses(self, space=None) -> list[str]:
#         """Every address currently in the vector index, sorted. Reads the entries (the `address` field is
#         the truth, not the _safe filename) so the canonical address is returned verbatim. Empty index → []
#         (an honest empty — the embedder may have been DOWN at build, the index stays empty/partial honestly).
#
#         SPACE filter (additive — default unchanged): `space=None` (the default) → only DEFAULT/unspaced
#         entries (`rec.space is None`), so the legacy callers + index_staleness see EXACTLY today's address
#         set (no spaced entries leaking in as phantom `extra`s). `space="<proj>"` → only that projection's
#         entries. `space=FsStore.ALL_SPACES` → every entry regardless of space.
#
#         Reads via the cached _vector_records() (X12-FAST) — the SAME per-record filter as before, byte-
#         identical results; only the file-read is cached/incremental now."""
#         out = []
#         for rec in self._vector_records():
#             if space is self.ALL_SPACES or rec.get("space") == space:
#                 out.append(rec["address"])
#         return sorted(out)
#
#     def index_corpus(self, space=None, emb=None, records=None) -> list[dict]:
#         """The index as a corpus list `[{id: <item>, vector: [...]}]` — the EXACT shape nodes/retrieve.run
#         consumes (id + vector), so the QUERY path feeds it straight in with NO reshaping and NO reimplemented
#         cosine. Empty index → [] (query then returns empty + an honest note).
#
#         SPACE filter (additive — default unchanged): `space=None` (the default) → only DEFAULT/unspaced
#         entries, EXACTLY today's corpus (no spaced entry leaks in → no polluted ranking, no cross-dim cosine
#         crash). `space="<proj>"` → only that projection's entries, and each entry's `id` is its `source` (the
#         BARE item address it embeds) — so a per-space query RETURNS THE ITEM (which round-trips through the
#         existing code://-resolution), not the internal vec://#space= key. `space=FsStore.ALL_SPACES` → every
#         entry (id = the verbatim stored address). A legacy entry with no `source` field falls back to its
#         own `address` (it IS its own source).
#
#         Reads via the cached _vector_records() (X12-FAST) — the SAME per-record filter as before, byte-
#         identical results; only the file-read is cached/incremental now.
#
#         `records` (additive, default None — BYTE-IDENTICAL when absent): a PRE-FETCHED _vector_records()
#         SNAPSHOT to filter, instead of fetching it here. THE SCANDIR-ONCE seam (2026-06-21): a MULTI-SPACE
#         caller (recall_for_decision queries 6-7 spaces for ONE decision) would otherwise re-scandir+stat the
#         whole vectors/ dir (~0.29s @ 49,853 files) per space = the bulk of the decision card-resolve memory
#         leg's 3s-budget overrun once the 44k extraction layer grew the store. Fetching the snapshot ONCE and
#         passing it to each per-space call collapses 6-7 scandirs to one. CORRECTNESS: the 6-7 queries of one
#         recall are ONE logical read — a single consistent snapshot is MORE correct than 6 mid-write views; and
#         each recall fetches a FRESH snapshot (no cross-call staleness — unlike a dir-mtime cache, which is
#         UNSAFE on WSL ext4: create/delete don't bump dir mtime, proved by falsify-first 2026-06-21)."""
#         out = []
#         for rec in (records if records is not None else self._vector_records()):
#             if space is self.ALL_SPACES:
#                 out.append({"id": rec["address"], "vector": rec["vector"]})
#             elif rec.get("space") == space and rec.get("emb") == emb:
#                 # within a NAMED space, rank/return by the SOURCE item (not the internal vec://#space= key)
#                 # so the caller gets the item back; the default space (space is None) returns the bare address
#                 # (== source for an unspaced entry) — identical to the pre-space shape.
#                 # emb=None (default) matches the BGE default layer (existing entries: no emb field → None) —
#                 # byte-identical to pre-layer behaviour; emb='<tag>' selects that embedder layer (multi-layer model).
#                 _id = rec.get("source") if space is not None else rec["address"]
#                 out.append({"id": _id if _id is not None else rec["address"], "vector": rec["vector"]})
#         return out
#
#     def space_matrix(self, space, emb):
#         """X12-MATRIX: the per-(space,emb) cosine MATRIX (ids, M:np.ndarray) — query_index's fast-path. Built
#         ONCE from _vector_records using the SAME (space,emb) filter + id logic as index_corpus (→ the SAME
#         ranked ids, so the matmul ranking is IDENTICAL to index_corpus→retrieve), cached keyed on `_vec_version`
#         (bumped on ANY vector change → NO staleness, auto-fresh on a (re)bake). Returns:
#           • (ids, M)  — ids parallel to M's rows; do `(M @ q)/(|rows|·|q|)` for cosine.
#           • ([], None) — the space is empty (honest; caller returns empty).
#           • None       — numpy absent, the DEFAULT/ALL space (not a perf target), or a RAGGED-dim space (a dim
#                          mismatch must hit index_corpus→retrieve's FAIL-LOUD path, never a silent matrix).
#         Only NAMED spaces are matrixed (the perf target = the big named spaces, e.g. the 67k extractions)."""
#         if space is None or space is self.ALL_SPACES:
#             return None
#         try:
#             import numpy as _np
#         except Exception:
#             return None
#         recs = self._vector_records()                        # refresh (+ may bump _vec_version)
#         ver = self._vec_version
#         key = (space, emb)
#         cached = self._space_matrix_cache.get(key)
#         if cached is not None and cached[0] == ver:
#             return (cached[1], cached[2])
#         ids, vecs = [], []
#         for rec in recs:
#             if rec.get("space") == space and rec.get("emb") == emb:
#                 _id = rec.get("source") if rec.get("source") is not None else rec.get("address")
#                 v = rec.get("vector")
#                 if _id is not None and v:
#                     ids.append(_id)
#                     vecs.append(v)
#         if not ids:
#             self._space_matrix_cache[key] = (ver, [], None)
#             return ([], None)
#         dim0 = len(vecs[0])
#         if any(len(v) != dim0 for v in vecs):                # ragged → let index_corpus→retrieve fail loud
#             return None
#         M = _np.asarray(vecs, dtype=_np.float64)
#         self._space_matrix_cache[key] = (ver, ids, M)
#         return (ids, M)
#
#     def layers_by_space(self) -> dict:
#         """Which embedder LAYERS each content/registry space carries: {space: [emb_tag, ...]} (the default/BGE
#         layer shown as 'default'; a named embedder, e.g. 'pplx', as itself). The self-description of the
#         multi-layer model — a picker (the FE) OR an agent (the dual interface) reads this to choose which layer
#         to view. Internal `scale:*` pyramid spaces + the default/unspaced space are excluded (only the lens/
#         registry spaces a layer is chosen FOR).
#
#         X12-FAST (2026-06-22): served from the mtime-gated self-description memo (_layers_self_desc) — a single
#         os.stat of the vectors dir on the hot path; recompute (from the SHARED _vector_records cache) only when
#         a (space,emb) is actually added/removed. Replaces the old private raw glob+read_text full scan that
#         re-read 1.2 GB / ~58,737 files on EVERY call and, fired concurrently by the surface, jammed the bridge
#         under the GIL (the 'no content loads' hang)."""
#         return self._layers_self_desc()["layers"]
#
#     def _layers_self_desc(self) -> dict:
#         """The mtime-gated memo behind layers_by_space() + layer_dims() (they read the SAME vectors, so ONE
#         compute serves both). Hot path = one os.stat of the vectors dir: if its mtime is unchanged since the
#         memo was built, return the memo (no scan). A vectors-dir mtime change (a (space,emb) file added/removed
#         — exactly when the self-description changes) triggers a single recompute over the shared, incrementally
#         cached _vector_records(). Returns {"layers": {space:[emb,…]}, "dims": {space:{emb:dim}}}; scale:* and
#         the default/unspaced space are excluded (only the lens/registry spaces a layer is chosen FOR)."""
#         d = self.root / "vectors"
#         try:
#             sig = d.stat().st_mtime_ns
#         except OSError:
#             return {"layers": {}, "dims": {}}
#         memo = self._layers_memo
#         if memo is not None and self._layers_memo_mtime == sig:   # nothing added/removed → instant
#             return memo
#         with self._layers_lock:
#             if self._layers_memo is not None and self._layers_memo_mtime == sig:  # another thread just built it
#                 return self._layers_memo
#             layers: dict[str, set] = {}
#             dims: dict[str, dict] = {}
#             for rec in self._vector_records():
#                 space = rec.get("space")
#                 if not space or str(space).startswith("scale:"):  # skip default/unspaced + internal pyramid spaces
#                     continue
#                 emb = rec.get("emb") or "default"
#                 layers.setdefault(space, set()).add(emb)
#                 if not dims.get(space, {}).get(emb):              # first record per (space,emb) settles the dim
#                     v = rec.get("vector")
#                     if isinstance(v, list) and v:
#                         dims.setdefault(space, {})[emb] = len(v)
#             built = {
#                 "layers": {sp: sorted(es) for sp, es in sorted(layers.items())},
#                 "dims": {sp: dims[sp] for sp in sorted(dims)},
#             }
#             self._layers_memo = built
#             self._layers_memo_mtime = sig
#             return built
#
#     def layer_dims(self) -> dict:
#         """The vector DIMENSION of every (space, embedder-layer): {space: {emb_tag: full_dim}} (e.g.
#         {'repo': {'default': 1024, 'pplx': 2560}}). The RESOLUTION picker reads this to derive the MRL zoom
#         ladder PER layer (powers of two ≤ the full dim) — registry-true, never a hardcoded dim. All vectors in
#         a layer share a dim (the embedder fixes it), so the FIRST record per (space, emb) settles it. Internal
#         scale:* pyramid spaces + the default/unspaced space are excluded.
#
#         X12-FAST (2026-06-22): served from the same mtime-gated memo as layers_by_space (_layers_self_desc) —
#         ONE compute serves both (they read the same vectors). Replaces the old private full glob+read_text+
#         json-parse scan that re-read 1.2 GB / ~58,737 files per call and, fired concurrently by the surface,
#         jammed the whole bridge under the GIL."""
#         return self._layers_self_desc()["dims"]
