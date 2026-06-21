"""FilesystemResolver — the addressed store (C1/C4). Implements contracts.resolver.Resolver.

Stdlib + pydantic. Content-addressed immutable objects, mutable refs, typed provenance,
lineage walk, and the memo index. See store/AGENTS.md (never mutate cas://; ext4 only).

PORTABILITY (a hard constraint — Tim is Supabase-bound): the concurrency + durability
guarantees below (cross-process locking, fsync) are filesystem-BACKEND properties expressed
ENTIRELY behind the resolver seam. The engine calls `store.graph_lock(gid)` and never knows
whether it is enforced by a thread RLock, an OS file-lock, or a Postgres advisory lock. NO
`fcntl`/lockfile/fsync reference may leak outside this module — a Supabase backend would
implement the SAME methods with backend-native concurrency/durability and the engine would
not change. That is the whole point of the indirection (store/AGENTS.md).
"""
from __future__ import annotations
import fcntl
import hashlib
import json
import os
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from contracts.address import Provenance


class _CrossProcessLock:
    """A RE-ENTRANT lock that serializes a critical section across BOTH threads (in one
    process) AND processes (against the same store on disk).

    Why both: the bridge is a ThreadingHTTPServer over ONE Suite (in-process thread race),
    AND Tim runs MULTIPLE sessions/processes against the SAME store (cross-process race,
    STATE.md). A thread RLock alone covers only the first; an `fcntl.flock` on a per-key
    lockfile covers the second. We compose them.

    Re-entrancy is REQUIRED, not optional: `graph_lock` is documented + used re-entrantly
    (suite.py nests locked calls on the same gid). But `fcntl.flock` is PER-FD and NOT
    re-entrant — a naive flock-on-enter / release-on-exit deadlocks (or, worse, the inner
    `__exit__` releases the OUTER's lock). So we:
      • hold a thread RLock (re-entrant in-process by construction), and
      • take the `flock` ONLY on the OUTERMOST acquire (depth 0→1) and release it ONLY on
        the OUTERMOST exit (depth 1→0), tracked by a per-THREAD depth counter.
    A separate process has its own counter + its own fd, so flock serializes the two
    processes; within a thread, nesting just increments depth (no second flock).
    """

    def __init__(self, lockfile: Path):
        self._lockfile = lockfile
        self._rlock = threading.RLock()          # in-process re-entrancy + nesting
        self._depth: dict[int, int] = {}         # thread-id -> nesting depth (flock held iff depth>0)
        self._fds: dict[int, int] = {}           # thread-id -> the open fd holding the flock
        self._depth_guard = threading.Lock()     # guards the two maps above

    @contextmanager
    def acquire(self):
        tid = threading.get_ident()
        # Serialize THREADS first (re-entrant). This also makes the depth bookkeeping safe:
        # only the holder of the RLock for THIS key touches its own thread's depth entry.
        self._rlock.acquire()
        try:
            with self._depth_guard:
                d = self._depth.get(tid, 0)
                if d == 0:
                    # OUTERMOST acquire for this thread → take the OS file-lock (serializes processes).
                    fd = os.open(self._lockfile, os.O_RDWR | os.O_CREAT, 0o644)
                    fcntl.flock(fd, fcntl.LOCK_EX)   # blocking exclusive lock across processes
                    self._fds[tid] = fd
                self._depth[tid] = d + 1
            yield
        finally:
            with self._depth_guard:
                d = self._depth.get(tid, 0)
                if d <= 1:
                    # OUTERMOST exit → release the OS file-lock + close its fd.
                    fd = self._fds.pop(tid, None)
                    if fd is not None:
                        fcntl.flock(fd, fcntl.LOCK_UN)
                        os.close(fd)
                    self._depth.pop(tid, None)
                else:
                    self._depth[tid] = d - 1
            self._rlock.release()


def _fsync_path(path: Path) -> None:
    """fsync a directory entry so a rename/create within it is durable (the rename can be
    lost on crash if the parent dir is not itself fsync'd). Best-effort on platforms that
    refuse to fsync a directory fd; the file-content fsync is the primary guarantee."""
    try:
        dfd = os.open(str(path), os.O_RDONLY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except (OSError, PermissionError):
        # Some filesystems disallow fsync on a directory fd. The file's own content fsync
        # (done by the caller) is the durability guarantee; the dir fsync hardens the rename.
        pass


def _atomic_write_fsync(path: Path, data: str) -> None:
    """Write `data` to `path` atomically AND durably: write to a unique tmp, fsync the tmp's
    fd (force the BYTES to stable storage), os.replace (atomic same-fs rename), then fsync the
    PARENT DIR (force the rename's directory entry to stable storage). Unique tmp PER WRITE
    (pid+thread) so two concurrent writers on the same target never share a tmp name —
    last-writer-wins, each file always whole. Mirrors the prior tmp+os.replace pattern but
    adds the two fsyncs (T-FSYNC)."""
    tmp = path.with_name(f"{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    try:
        os.write(fd, data.encode())
        os.fsync(fd)                      # bytes → stable storage BEFORE the rename
    finally:
        os.close(fd)
    os.replace(tmp, path)                 # atomic rename (same filesystem)
    _fsync_path(path.parent)              # rename's dir entry → stable storage


class FsStore:
    def __init__(self, root):
        self.root = Path(root)
        for d in ("objects", "refs", "ref_history", "meta", "memo", "graphs", "surfaced", "locks", "vectors"):
            (self.root / d).mkdir(parents=True, exist_ok=True)
        # --- store-level concurrency locks (T1-SEQ / T1-RACE / T-LOCK) ---
        # The bridge is a ThreadingHTTPServer over ONE Suite, so read-modify-write paths in the store
        # are run UNSERIALIZED across threads → lost updates + colliding sequence numbers. AND Tim runs
        # MULTIPLE sessions/PROCESSES against the SAME store (STATE.md) → the thread lock alone does
        # NOTHING across processes. The locks live HERE (in the store) — not in the Suite — because BOTH
        # the Suite (resolve_surfaced, build_result writes) AND governance.Inbox (set_status, resolve)
        # mutate surfaced items; a lock held only by the Suite would not serialize governance's writes
        # against the Suite's. The store is the one object every writer reaches, so serializing here is
        # the only place that covers all callers. Re-entrant so a method that calls another locked store
        # method can't self-deadlock.
        self._event_lock = threading.RLock()       # T1-SEQ: append_event seq = read-last → +1 → append (atomic)
        self._surfaced_lock = threading.RLock()    # T1-RACE: surfaced read-modify-write across both faces
        self._graph_locks_guard = threading.Lock()  # guards the per-graph cross-process lock map below
        self._graph_locks: dict = {}                # T-LOCK: one CROSS-PROCESS lock per graph id
        # X12-FAST: the incremental in-memory vector-index cache (see _vector_records). index_corpus/
        # index_addresses read+parse the WHOLE vectors/ dir on every call (5862 files ≈ 1.5s) — re-paid
        # per query_index, ×8 per recall_for_decision = the >15s decision-surface hang (2026-06-18). The
        # cache parses each file ONCE, revalidates by a cheap per-file (mtime_ns,size) signature on every
        # call (CROSS-PROCESS correct: another session's atomic put_vector → a new mtime/size → re-parsed;
        # a removed file → dropped), and re-reads ONLY changed/new files. _safe-filename -> ((mtime_ns,size), rec).
        self._vec_cache: dict = {}
        self._vec_cache_lock = threading.Lock()    # held ONLY during the refresh (scandir+stat+parse-changed)

    def _safe_lock_name(self, key: str) -> str:
        """A filename-safe lockfile name for an arbitrary key (graph id, claim key). Reuses the
        address-safe encoder so e.g. 'dispatch-claim:7' and 'g/1' both map to valid filenames."""
        return self._safe(key) + ".lock"

    def graph_lock(self, gid: str):
        """A re-entrant CROSS-PROCESS lock per graph id, created on demand (threadsafe). Backed by
        BOTH a thread RLock (in-process re-entrancy + the threading-bridge race) AND an `fcntl.flock`
        on a per-graph lockfile under `<root>/locks/` (the cross-PROCESS guarantee — Tim runs multiple
        sessions). The Suite's whole-graph load→mutate→save_graph mutations (create_node / connect /
        delete_node / set_config / set_position) hold this around the WHOLE read-modify-write so two
        concurrent mutations on the same graph — even in two SEPARATE PROCESSES — can't both load
        version V and last-writer-wins (lost update). Returned object is a context manager
        (`with store.graph_lock(gid): ...`), API unchanged from the prior thread-only RLock — the
        engine is agnostic to the enforcement (PORTABILITY: a Supabase backend would use an advisory
        lock here and the engine would not change). Re-entrant so a mutation that nests another locked
        call on the same graph (or the same claim key) does not self-deadlock.

        Also used (with a distinct key, e.g. `dispatch-claim:<seq>`) to wrap the exactly-once
        dispatch check→claim so two PROCESSES can't both pass the TOCTOU — the same primitive the
        spec mandates for the dispatch-claim, behind the same seam."""
        with self._graph_locks_guard:
            lk = self._graph_locks.get(gid)
            if lk is None:
                lk = _CrossProcessLock(self.root / "locks" / self._safe_lock_name(gid))
                self._graph_locks[gid] = lk
        return lk.acquire()

    def dispatch_lock(self, key):
        """Compat alias for the wire's exactly-once dispatch CHECK→CLAIM → the SAME cross-process
        primitive as graph_lock, keyed by a distinct `dispatch-claim:<key>` lockfile (this is exactly
        main's generalized design — graph_lock's docstring documents this usage). The convergence lineage
        called `store.dispatch_lock(seq)`; this routes it to graph_lock so there is ONE cross-process lock
        mechanism, two call spellings (no duplicate locking)."""
        return self.graph_lock(f"dispatch-claim:{key}")

    @staticmethod
    def _hash(b: bytes) -> str:
        return "cas://b2:" + hashlib.blake2b(b, digest_size=16).hexdigest()

    @staticmethod
    def _safe(addr: str) -> str:
        return addr.replace("://", "__").replace(":", "_").replace("/", "_")

    # --- immutable content (cas://) ---
    def put_content(self, data: Any) -> str:
        b = json.dumps(data, sort_keys=True).encode()
        cas = self._hash(b)
        p = self.root / "objects" / self._safe(cas)
        # CAS object paths are always FILES. If the target exists as a DIRECTORY, the store is corrupt
        # (a stray/colliding path) — `p.write_bytes` would raise IsADirectoryError mid-write and surface
        # as a torn HTTP 400 with no diagnosis. Detect it first and FAIL LOUD with a clean, actionable
        # message (never a half-written write, never a bare OS errno). Write-once otherwise.
        if p.is_dir():
            raise IsADirectoryError(
                f"CAS object path {p} is a directory, not a file — the object store is corrupt at "
                f"this address (a stray/colliding directory). Remove it; CAS objects are write-once files.")
        if not p.exists():                      # write-once; never mutate
            p.write_bytes(b)
        return cas

    def get_content(self, cas: str) -> Any:
        return json.loads((self.root / "objects" / self._safe(cas)).read_bytes())

    def exists(self, cas: str) -> bool:
        return (self.root / "objects" / self._safe(cas)).exists()

    def _fsync_atomic_write(self, path: Path, data: str) -> None:
        """Compat method alias → the module-level `_atomic_write_fsync` (the one verified T-FSYNC
        crash-durable atomic-write primitive). The convergence lineage spelled this `self._fsync_atomic_write`;
        the night-build lineage spelled it `_atomic_write_fsync` (module func). The merge standardises on the
        module func as THE implementation and keeps this thin method so every existing `self.`-call routes to it
        — ONE primitive, both call spellings (no duplicate durability code)."""
        _atomic_write_fsync(path, data)

    # --- mutable pointer (run://) ---
    def set_ref(self, logical: str, cas: str) -> None:
        # ATOMIC (T1-RACE): set_ref is the scheduler's hot-path output write (every node fire writes its
        # ref here). A naked write_text TRUNCATES the target before re-filling it, so during that window a
        # concurrent head() on the threading bridge can read "" — which the scheduler readiness check
        # (`all(store.head(a) for a in ex.inputs.values())`, scheduler.py) treats as UNRESOLVED (the node
        # silently waits a pass) and get_content("") raises. tmp + os.replace (same-filesystem rename is
        # atomic) means a reader sees the WHOLE old cas or the WHOLE new one — never a torn/empty ref.
        # Mirrors save_graph/save_surfaced/save_session exactly. Unique tmp PER WRITE (pid+thread) so two
        # concurrent set_refs on the same logical never share a tmp name (last-writer-wins, each whole).
        # S4: crash-durable (fsync the tmp before the atomic rename) — was tmp.write_text+replace (atomic
        # vs torn reads) but NOT durable: a crash could leave the not-yet-flushed tmp as the live ref.
        path = self.root / "refs" / self._safe(logical)
        self._fsync_atomic_write(path, cas)
        # L6 (§21.7#6) — APPEND (ts, cas) to this address's version-history index AFTER the current-ref
        # write SUCCEEDS. set_ref OVERWRITES the live ref (head() = last write, preserved byte-for-byte
        # above) and the *old* cas bytes already SURVIVE (put_content is write-once, never deletes) — but
        # nothing mapped a ref to its PRIOR cas hashes. This index is that map: it stores only (ts, cas)
        # tuples (hashes + timestamps), NEVER copies of the bytes — a prior version is fetched by its cas
        # through the existing get_content path. DECISION: versioning is ALL refs (every set_ref appends —
        # cheap, ~80 bytes/line); NO write cap (append-only, lock-free `open("a")`, mirroring the
        # append_annotation/append_chat precedent — a write cap would force a read-modify-write that
        # regresses set_ref's atomic hot path); the READ is bounded instead (ref_history(ref, limit=...)).
        # Appended AFTER the atomic write so (a) the overwrite path is untouched and (b) a write that
        # RAISES never records a version that never became current. Consecutive identical cas is a
        # legitimate entry (history records WRITES, not distinct values). One jsonl file per logical ref
        # (keyed by _safe(logical)), so two addresses never collide and one address's trail reads alone.
        # NOTE: lineage() (provenance INPUTS — what an artefact was made FROM) is a DIFFERENT axis and stays
        # untouched; this is the TEMPORAL trail of one address.
        self._append_ref_version(logical, cas)

    def _append_ref_version(self, logical: str, cas: str) -> None:
        """Append one {ts, cas} line to this ref's version-history jsonl (L6). Lock-free append (the same
        durability class as append_annotation/append_chat) — it is a SEPARATE file from the live ref, so it
        never interferes with set_ref's atomic tmp+replace on the ref itself."""
        import json as _j
        from datetime import datetime, timezone
        d = self.root / "ref_history"
        d.mkdir(parents=True, exist_ok=True)   # defensive (mirrors save_session/save_journey) — never assume __init__ ran
        rec = {"ts": datetime.now(timezone.utc).isoformat(), "cas": cas}
        # ONE write() of a single line (< 4KB) — on POSIX a single write of < PIPE_BUF/page is atomic for an
        # O_APPEND file handle, so concurrent appenders never interleave a torn line (verified by the
        # concurrent-storm check in version_history_acceptance.py: N×M writers, every line parses, count exact).
        with (d / self._safe(logical)).open("a", encoding="utf-8") as f:
            f.write(_j.dumps(rec) + "\n")

    def ref_history(self, logical: str, limit: int | None = None) -> list[dict]:
        """L6 — the ordered version trail of one address: every set_ref to `logical` as a {ts, cas} entry,
        OLDEST-FIRST (chronological). `limit` bounds the READ (the last N entries, newest end kept, order
        preserved) — the append side is unbounded, so a bound here never loses an older write, it just
        windows the view. A ref NEVER written returns [] (an HONEST empty, not a crash, not a silent wrong
        value — rule 4). Reads disk every call (no in-memory cache), so a SECOND store over the same root
        sees a prior store's writes (persistence-survives-reload). A prior version's BYTES are fetched by
        its `cas` through get_content (the cas objects survive — put_content is write-once)."""
        import json as _j
        p = self.root / "ref_history" / self._safe(logical)
        if not p.exists():
            return []
        lines = [l for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
        if limit is not None:
            lines = lines[-limit:]
        return [_j.loads(l) for l in lines]

    def head(self, logical: str) -> str | None:
        p = self.root / "refs" / self._safe(logical)
        return p.read_text() if p.exists() else None

    # --- provenance + lineage ---
    def write_provenance(self, prov: Provenance) -> None:
        # ATOMIC (Concurrent Cognition C1.6 / R1-FOLD F8): a naked write_text TRUNCATES then re-fills,
        # so a concurrent reader (provenance()) on the threading bridge can read torn/empty JSON, and a
        # crash mid-write leaves a corrupt meta file. Under a concurrent swarm of role-runs each writing
        # provenance, that race is real. tmp + fsync + os.replace makes every reader see the WHOLE old or
        # WHOLE new record — the SAME guarantee set_ref/save_graph give. (Strictly more durable than the
        # prior write_text; the app's serial node-runs are unaffected except for the added fsync.)
        self._fsync_atomic_write(
            self.root / "meta" / (self._safe(prov.address) + ".json"),
            prov.model_dump_json(indent=2))

    def provenance(self, address: str) -> Provenance | None:
        p = self.root / "meta" / (self._safe(address) + ".json")
        return Provenance.model_validate_json(p.read_text()) if p.exists() else None

    def lineage(self, address: str) -> list[str]:
        """Walk provenance inputs back toward source (breadth-first, de-duped, cycle-safe)."""
        order, seen, queue = [], set(), [address]
        while queue:
            a = queue.pop(0)
            if a in seen:
                continue
            seen.add(a)
            order.append(a)
            prov = self.provenance(a)
            if prov:
                queue.extend(i for i in prov.inputs if i not in seen)
        return order

    # --- memo (the gate) ---
    def memo_get(self, sig: str) -> str | None:
        p = self.root / "memo" / self._safe(sig)
        return p.read_text() if p.exists() else None

    def memo_set(self, sig: str, cas: str) -> None:
        # ATOMIC (Concurrent Cognition C1.6 / R1-FOLD F8): like set_ref, this is a hot-path pointer
        # write read concurrently by memo_get on the threading bridge. A naked write_text truncates
        # then re-fills → a concurrent memo_get can read "" → the memo gate (scheduler) treats "" as a
        # miss and re-fires (a wasted GPU hit), or get_content("") raises. tmp + fsync + os.replace
        # gives the whole-old-or-whole-new guarantee (mirrors set_ref). Crash-durable too.
        self._fsync_atomic_write(self.root / "memo" / self._safe(sig), cas)

    # --- graphs registry (S3): canvases live in the substrate, shared across faces ---
    def save_graph(self, graph) -> None:
        # ATOMIC (C5): /api/move makes this a high-frequency path on the threading server; a naked
        # write_text could tear graphs/<id>.json against the running bridge's reads. tmp + os.replace
        # (same-filesystem rename is atomic) means a reader sees the old file or the new — never a
        # half-written one. Mirrors the apply_* paths' tmp+replace pattern.
        path = self.root / "graphs" / (self._safe(graph.id) + ".json")
        # Unique tmp PER WRITE (pid+thread): two concurrent same-graph writers (two /api/move, or a
        # move racing an MCP-face create_node/connect on the threading server) must not share one tmp
        # name — a fixed name lets their write_texts interleave into invalid JSON that os.replace then
        # makes the LIVE file (durable corruption). Unique tmp + atomic replace = last-writer-wins, each
        # file always whole. (Traded import-minimalism for write-concurrency correctness.)
        # DURABLE (T-FSYNC): _atomic_write_fsync fsyncs the tmp's bytes BEFORE the rename + fsyncs the
        # parent dir AFTER, so the canvas substrate (shared across faces) survives a crash.
        _atomic_write_fsync(path, graph.model_dump_json(indent=2))

    def load_graph(self, gid: str):
        from contracts.node_record import Graph
        p = self.root / "graphs" / (self._safe(gid) + ".json")
        return Graph.model_validate_json(p.read_text()) if p.exists() else None

    # --- review-session state (B): server-authoritative, ATOMIC (clones save_graph, NOT save_surfaced) ---
    def save_session(self, session: dict) -> None:
        """Persist a review-session record (cursor + item ids + mode + graph id) atomically. The walk is
        server-authoritative: Next/respond mutate this on the threading bridge, so a naked write_text could
        tear the file against a concurrent read. tmp + os.replace (same-fs rename is atomic) → a reader sees
        the old file or the new, never a half-written one — the SAME guarantee save_graph gives. (save_surfaced
        now also gives this guarantee — tmp+replace under the surfaced lock, T1-RACE — so this is no longer the
        only atomic surfaced-shaped write.) Unique tmp PER WRITE (pid+thread) so concurrent writers never share
        a tmp name (last-writer-wins, each file whole)."""
        import json as _j
        (self.root / "sessions").mkdir(parents=True, exist_ok=True)
        path = self.root / "sessions" / (self._safe(session["id"]) + ".json")
        self._fsync_atomic_write(path, _j.dumps(session, indent=2))   # S4: crash-durable atomic write

    def load_session(self, sid: str) -> dict | None:
        import json as _j
        p = self.root / "sessions" / (self._safe(sid) + ".json")
        return _j.loads(p.read_text()) if p.exists() else None

    def list_sessions(self) -> list[str]:
        d = self.root / "sessions"
        return sorted(p.stem for p in d.glob("*.json")) if d.exists() else []

    # --- scale-pyramid structure (Group 11): the multi-scale rungs' NESTING/membership sidecar. The coarse
    # CENTROIDS live in the vector substrate (put_vector, space=scale:<space>:k<K>) so query_index resolves
    # them; this sidecar holds the STRUCTURE (per-rung clusters, members, exemplar labels, cross-rung parent
    # links) keyed by the UNIT space it coarsens — one record per space. Clones save_session's atomic dict
    # write (a derived, rebuildable artefact, not the canonical store) — additive, its own scale/ dir, so no
    # vector path or graph path is touched. See runtime/scale.py for the build/resolve that reads it. ---
    def save_scale_pyramid(self, space: str, pyramid: dict, emb: str | None = None) -> None:
        import json as _j
        (self.root / "scale").mkdir(parents=True, exist_ok=True)
        # emb=None → the default-layer pyramid (path unchanged: scale/<space>.json); a named emb keys a
        # SEPARATE per-embedder pyramid (scale/<space>#emb=<emb>.json) so a pplx pyramid never overwrites BGE's.
        key = space if emb is None else f"{space}#emb={emb}"
        path = self.root / "scale" / (self._safe(key) + ".json")
        self._fsync_atomic_write(path, _j.dumps(pyramid, indent=2))   # crash-durable atomic (mirrors save_session)

    def load_scale_pyramid(self, space: str, emb: str | None = None) -> dict | None:
        import json as _j
        key = space if emb is None else f"{space}#emb={emb}"
        p = self.root / "scale" / (self._safe(key) + ".json")
        return _j.loads(p.read_text()) if p.exists() else None

    def list_scale_pyramids(self) -> list[str]:
        d = self.root / "scale"
        return sorted(p.stem for p in d.glob("*.json")) if d.exists() else []

    # --- journey-record state (L9): the REVERSE of the forward resolver — a recorded ordered click-path
    # through ui:// addresses, retrieved-whole-by-id then replayed via the forward resolveUiTarget. This
    # is a DISTINCT object from a review-session (above): a journey records NAVIGATION (an addressed
    # path), a session records a REVIEW (item-ids walked with a cursor). Distinct directory → distinct
    # store, so a journey id and a session id never collide. Mirrors save_session/load_session (the atomic
    # tmp+replace whole-record write) — the truer structural parallel for a retrieved-whole record — while
    # the record itself stays OPEN ({id, ts, steps:[{address, ts, **}], done, **}) per the append_*
    # {ts,**} additive convention (store constitution: schema-additive, never schema-breaking). ---
    def save_journey(self, journey: dict) -> None:
        """Persist a journey-record (id + ordered addressed steps + done) atomically. Same crash-durable
        tmp+replace guarantee as save_session — a reader sees the old file or the new, never a torn one."""
        import json as _j
        (self.root / "journeys").mkdir(parents=True, exist_ok=True)
        path = self.root / "journeys" / (self._safe(journey["id"]) + ".json")
        self._fsync_atomic_write(path, _j.dumps(journey, indent=2))

    def load_journey(self, jid: str) -> dict | None:
        import json as _j
        p = self.root / "journeys" / (self._safe(jid) + ".json")
        return _j.loads(p.read_text()) if p.exists() else None

    def list_journeys(self) -> list[str]:
        d = self.root / "journeys"
        return sorted(p.stem for p in d.glob("*.json")) if d.exists() else []

    # --- agent-session registry records (Session Fabric F1.2): the DURABLE IDENTITY of a Claude Code
    # session in the fabric's registry — {id (the Claude session uuid), name, cwd, title, title_source,
    # state (supervised-live|unsupervised-live|closed), started, last_activity, + envelope (git_branch,
    # project, jsonl_path, jsonl_bytes, turns, …), schema_ver} — an OPEN record per the append_* {ts,**}
    # additive convention. Clones the save_journey/save_session whole-record-atomic pattern for a DISTINCT
    # noun: `agent_sessions/` is a SEPARATE dir from the review-session `sessions/` dir (an agent-session
    # id and a review-session id never collide — the save_journey precedent; Session Fabric naming ruling
    # N2: tool `sessions` · dir `agent_sessions/` · events `agent_sessions.*`, never `fabric/`). The LIVE
    # state trajectory rides `agent_sessions.*` events on events.jsonl (log-IS-the-index, the runs-fold
    # pattern in runtime/suite.py); these records hold what must survive without the log: who the session
    # IS. Writers: the read-only importer (ops/agent_sessions_importer.py, backfilling the historical
    # catalog as state=closed) + the session supervisor (the single agent_sessions.* event writer). ---
    def save_agent_session(self, rec: dict) -> None:
        """Persist one agent-session registry record atomically (crash-durable tmp+replace, the
        save_journey guarantee). STRUCTURAL fail-loud (the append_mark discipline): a record with a
        missing/empty `id` is REFUSED — an unaddressable session is a silent black hole (rule 4),
        and `id` is what `session://<id>` resolves by."""
        import json as _j
        sid = rec.get("id")
        if not isinstance(sid, str) or not sid.strip():
            raise ValueError(
                "save_agent_session: record has no `id` (the Claude session uuid) — refused. An "
                "agent-session record without an id can never be resolved (session://<id>) or listed; "
                "fail loud, never write an unfindable record.")
        (self.root / "agent_sessions").mkdir(parents=True, exist_ok=True)
        path = self.root / "agent_sessions" / (self._safe(sid) + ".json")
        self._fsync_atomic_write(path, _j.dumps(rec, indent=2))

    def load_agent_session(self, sid: str) -> dict | None:
        import json as _j
        p = self.root / "agent_sessions" / (self._safe(sid) + ".json")
        return _j.loads(p.read_text()) if p.exists() else None

    def list_agent_sessions(self) -> list[str]:
        d = self.root / "agent_sessions"
        return sorted(p.stem for p in d.glob("*.json")) if d.exists() else []

    def agent_session_mtimes(self) -> dict[str, float]:
        """{session id → record-file mtime} — the registry fold's cheap change-detection key (the suite
        re-loads ONLY records whose mtime moved, mirroring the run-index's events_since(high_water) delta
        discipline so a 1,000-record backfilled catalog isn't re-read on every list). A non-filesystem
        backend implements the same contract with its own change marker (updated_at)."""
        d = self.root / "agent_sessions"
        if not d.exists():
            return {}
        return {p.stem: p.stat().st_mtime for p in d.glob("*.json")}

    # --- agent-session TIMELINE cache (Session Fabric R3.3): one durable record per session at
    # agent_sessions/timeline/<sid>.json — the compaction-timeline index runtime/session_pointintime
    # builds (registry-shaped, the R11 frame: a RECORD other surfaces project from, never a parallel
    # store). Staleness is the CALLER's contract: the record carries source_bytes+source_mtime and the
    # suite recomputes when the transcript moved. Same whole-record-atomic write as the registry. ---
    def save_agent_session_timeline(self, sid: str, rec: dict) -> None:
        import json as _j
        if not isinstance(sid, str) or not sid.strip():
            raise ValueError("save_agent_session_timeline: empty session id — refused (unfindable record).")
        d = self.root / "agent_sessions" / "timeline"
        d.mkdir(parents=True, exist_ok=True)
        self._fsync_atomic_write(d / (self._safe(sid) + ".json"), _j.dumps(rec, indent=2))

    def load_agent_session_timeline(self, sid: str) -> dict | None:
        import json as _j
        p = self.root / "agent_sessions" / "timeline" / (self._safe(sid) + ".json")
        return _j.loads(p.read_text()) if p.exists() else None

    # --- conversation threads (S2): a thread = a CONVERSATION (new / list / reopen). Metadata mirrors
    # save_session (atomic whole-record). The TURNS stay in the ONE append-only chat.jsonl carrying an
    # additive `thread_id` (the same one-source pattern as the `address` field for chats_for) — no parallel
    # chat store (store constitution). A turn with NO thread_id is the legacy/global stream (back-compat). ---
    def save_chat_thread(self, thread: dict) -> None:
        import json as _j
        (self.root / "chat_threads").mkdir(parents=True, exist_ok=True)
        path = self.root / "chat_threads" / (self._safe(thread["id"]) + ".json")
        self._fsync_atomic_write(path, _j.dumps(thread, indent=2))

    def load_chat_thread(self, tid: str) -> dict | None:
        import json as _j
        p = self.root / "chat_threads" / (self._safe(tid) + ".json")
        return _j.loads(p.read_text()) if p.exists() else None

    def list_chat_threads(self) -> list[str]:
        d = self.root / "chat_threads"
        return sorted(p.stem for p in d.glob("*.json")) if d.exists() else []

    def chats_in_thread(self, thread_id: str, limit: int = 200) -> list[dict]:
        """Every chat turn carrying `thread_id`, oldest-first, last `limit` — the reopened conversation.
        Filters the SAME chat.jsonl by the additive thread_id field (inverse of chats_for's address)."""
        import json as _j
        path = self.root / "chat.jsonl"
        if not path.exists():
            return []
        out = [_j.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        return [r for r in out if r.get("thread_id") == thread_id][-limit:]

    def list_graphs(self) -> list[str]:
        return sorted(p.stem for p in (self.root / "graphs").glob("*.json"))

    # --- event log (I2): append-only captured trajectory, persists across sessions ---
    def append_event(self, event: dict) -> dict:
        import json as _j
        from datetime import datetime, timezone
        path = self.root / "events.jsonl"
        # T1-SEQ — the WHOLE read-last-seq → +1 → append is ONE atomic critical section under the
        # store-level event lock. Unserialized (the prior code), two concurrent emits on the
        # ThreadingHTTPServer both read seq=N and both write N+1 → a DUPLICATED seq. That breaks two
        # invariants: (a) the wire's three-part bind locates its authorizing event by seq==derived_from
        # (a duplicate could bind to the WRONG event); (b) the SSE cursor `id:<seq>` (bridge.py) assumes
        # monotonic-unique. The lock makes seq atomic + monotonic + unique. (RLock so a nested store
        # call cannot self-deadlock.)
        # T1-SEQ: the thread `_event_lock` makes the read-last → +1 → append atomic within ONE process.
        # NOTE (surfaced to Tim — see store.report.json needs_tim): this is NOT cross-process — two
        # PROCESSES can still both read seq=N and append N+1 → a duplicated seq. Closing that would wrap
        # this section in the same cross-process primitive graph_lock uses, but that adds an flock+fsync
        # to EVERY emit (hot path) + a permanent lock-ordering invariant the self-coding brain must know.
        # Whether the event log needs cross-process seq-uniqueness is a deliberate shared-semantics
        # decision (AGENTS.md rule 7 — surface cross-cutting, don't decide unilaterally), so it is
        # surfaced, not silently built into the hottest write path.
        with self._event_lock:
            seq = 0
            if path.exists():
                # last line's seq + 1 (append-only; order is preserved by the file itself)
                with path.open("rb") as f:
                    try:
                        f.seek(-2, 2)
                        while f.read(1) != b"\n":
                            f.seek(-2, 1)
                    except OSError:
                        f.seek(0)
                    last = f.readline().decode().strip()
                if last:
                    seq = _j.loads(last).get("seq", 0) + 1
            rec = {"seq": seq, "ts": datetime.now(timezone.utc).isoformat(), **event}
            # DURABLE (T-FSYNC): append, flush, then os.fsync the fd so the event (incl. the exactly-once
            # dispatch claim + the SSE trajectory) is forced to stable storage before we return — a
            # power-loss after this return must not lose an acknowledged claim/event.
            with path.open("a", encoding="utf-8") as f:
                f.write(_j.dumps(rec) + "\n")
                f.flush()
                os.fsync(f.fileno())
            return rec

    def recent_events(self, limit: int = 50) -> list[dict]:
        import json as _j
        path = self.root / "events.jsonl"
        if not path.exists():
            return []
        lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        return [_j.loads(l) for l in reversed(lines[-limit:])]   # newest-first

    def events_since(self, seq: int) -> list[dict]:
        """Events with seq > given, OLDEST-first — the SSE stream cursor (G). Sibling of
        recent_events (which is newest-first last-N). Tails the shared file, so it captures BOTH
        faces' events (bridge + MCP), not an in-memory queue. A fresh client passes -1 to get all."""
        import json as _j
        path = self.root / "events.jsonl"
        if not path.exists():
            return []
        out = []
        for l in path.read_text(encoding="utf-8").splitlines():
            if not l.strip():
                continue
            rec = _j.loads(l)
            if rec.get("seq", -1) > seq:
                out.append(rec)
        return out

    # --- right-hand-man chat log (I2): append-only, chronological, persists ---
    def append_chat(self, turn: dict) -> dict:
        import json as _j
        from datetime import datetime, timezone
        rec = {"ts": datetime.now(timezone.utc).isoformat(), **turn}
        with (self.root / "chat.jsonl").open("a", encoding="utf-8") as f:
            f.write(_j.dumps(rec) + "\n")
        return rec

    def chat_history(self, limit: int = 40) -> list[dict]:
        import json as _j
        path = self.root / "chat.jsonl"
        if not path.exists():
            return []
        lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        return [_j.loads(l) for l in lines[-limit:]]   # oldest-first (chronological)

    def chats_for(self, address: str) -> list[dict]:
        """I7 — every chat turn ATTACHED to `address`, oldest-first (the `chat://` thread at that
        locus). Filters the SAME append-only `chat.jsonl` (I2/I7's lane) by the additive `address`
        field — the address IS the key. This is the INVERSE of the I6 `annotations_for` leaf: I6
        has its OWN annotations.jsonl, I7 RIDES the open append_chat record (`rec = {"ts", **turn}`)
        with one additive field, so it stays ONE-SOURCE (no parallel chat store — store constitution).
        An ordinary RHM turn (no `address`) is NOT returned; a turn at a DIFFERENT address is NOT
        returned (isolation). Reads disk every call (no in-memory cache), so a SECOND Suite over the
        same store root sees a prior Suite's writes (persistence-survives-reload)."""
        import json as _j
        path = self.root / "chat.jsonl"
        if not path.exists():
            return []
        out = []
        for l in path.read_text(encoding="utf-8").splitlines():
            if not l.strip():
                continue
            rec = _j.loads(l)
            if rec.get("address") == address:
                out.append(rec)
        return out

    # --- addressed annotations (I6): append-only, keyed by `ui://` address, persists ---
    def append_annotation(self, rec: dict) -> dict:
        """Persist an annotation (comment) attached to a `ui://` address — the I6 store leaf.

        OPEN-RECORD, like append_chat: `{ts, **rec}` splat through to a NEW `annotations.jsonl`
        at the store root (its own file — SEPARATE from chat.jsonl, which is I2/I7's lane). The
        store stays dumb: it does NOT validate the address (that S0 gate is the Suite's job, where
        the semantic work lives, mirroring `act`). The `address` field is the retrieval key; `ts`
        rides free from the open shape and feeds R2's recency/decay bound later. Append-only so an
        address accrues a comment THREAD (history), not a last-writer-wins single value."""
        import json as _j
        from datetime import datetime, timezone
        out = {"ts": datetime.now(timezone.utc).isoformat(), **rec}
        with (self.root / "annotations.jsonl").open("a", encoding="utf-8") as f:
            f.write(_j.dumps(out) + "\n")
        return out

    def annotations_for(self, address: str) -> list[dict]:
        """Every annotation attached to `address`, oldest-first (the comment thread at that locus).
        Filters the append-only `annotations.jsonl` by the `address` field — the address IS the key.
        Reads from disk every call (no in-memory cache), so a SECOND Suite over the same store root
        sees a prior Suite's writes (the persistence-survives-reload property I6 must prove)."""
        import json as _j
        path = self.root / "annotations.jsonl"
        if not path.exists():
            return []
        out = []
        for l in path.read_text(encoding="utf-8").splitlines():
            if not l.strip():
                continue
            rec = _j.loads(l)
            if rec.get("address") == address:
                out.append(rec)
        return out

    # --- coherence finding store (C1) + disposition overlay (C2) ---
    # The substrate spine of the Coherence model, built on the SAME own/reflect split the pin overlay uses.
    # DETECTION (a finding) is re-derivable → an append-only, address-keyed open record (mirrors
    # append_annotation): a detector re-run re-appends; the reconcile/rollup dedups by (kind,address) at read
    # time (own/reflect: re-derive freely, the read folds to current). DISPOSITION is a DECISION (not
    # recomputable) → a last-wins overlay keyed by the (kind,address) finding handle (mirrors the pin overlay),
    # NOT a mutation of the append-only finding record, so it SURVIVES a re-detection. A disposition is a
    # micro-ADR. The store stays dumb (turns an address into bytes and back; never calls a model — the
    # detector semantics live in coherence_detect.py / the Suite, mirroring annotations' S0 gate).
    def append_finding(self, rec: dict) -> dict:
        """Persist a coherence finding — `{kind, address, state, evidence, source, ...}` — to an append-only
        `findings.jsonl`. Open-record like append_annotation: `{ts, **rec}`. The `address` is the retrieval
        key; append-only so a re-detection accrues (the reconcile dedups by (kind,address) on read). The store
        does NOT validate the finding (that is the detector's job)."""
        import json as _j
        from datetime import datetime, timezone
        out = {"ts": datetime.now(timezone.utc).isoformat(), **rec}
        with (self.root / "findings.jsonl").open("a", encoding="utf-8") as f:
            f.write(_j.dumps(out) + "\n")
        return out

    def findings_for(self, address: str) -> list[dict]:
        """Every finding at `address`, oldest-first (the detection thread). Filters append-only
        `findings.jsonl` by the `address` field — the address IS the key. Reads disk every call, so a second
        Suite over the same store root sees a prior Suite's findings (persistence-survives-reload)."""
        import json as _j
        path = self.root / "findings.jsonl"
        if not path.exists():
            return []
        out = []
        for l in path.read_text(encoding="utf-8").splitlines():
            if not l.strip():
                continue
            rec = _j.loads(l)
            if rec.get("address") == address:
                out.append(rec)
        return out

    def all_findings(self) -> list[dict]:
        """Every finding record (for the reconcile/burn-down rollup — C3/C5). Append-only, oldest-first."""
        import json as _j
        path = self.root / "findings.jsonl"
        if not path.exists():
            return []
        return [_j.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]

    def append_disposition(self, kind: str, address: str, disposition: str, *, reason: str = "", by: str = "") -> dict:
        """Record a disposition (finish/defer/by-design/…) on the finding handle `(kind, address)`, as an
        APPEND-ONLY control record in `dispositions.jsonl`, resolved LAST-WINS (`disposition_for`). WHY an
        overlay not a field on the finding: the finding store is append-only (a re-detection re-appends), so
        the disposition cannot live on the record (it would be lost/duplicated on re-detect). The overlay is
        keyed by the finding's STABLE handle `(kind, address)`, so the decision persists across re-detections.
        Open-record: `{ts, kind, address, disposition, reason, by}`; append-only so the disposition HISTORY is
        preserved (a later change is a NEW record, last-wins — the micro-ADR trail; never a lost update)."""
        import json as _j
        from datetime import datetime, timezone
        rec = {"ts": datetime.now(timezone.utc).isoformat(), "kind": kind, "address": address,
               "disposition": disposition, "reason": reason, "by": by}
        with (self.root / "dispositions.jsonl").open("a", encoding="utf-8") as f:
            f.write(_j.dumps(rec) + "\n")
        return rec

    def disposition_for(self, kind: str, address: str) -> dict | None:
        """The resolved disposition on `(kind, address)`, LAST-WINS over append-only `dispositions.jsonl`
        (a later record overrides — a changed decision reads as the latest). Reads disk every call
        (persistence-survives-reload). No disposition record → None (the additive default: the finding is
        OPEN/undispositioned)."""
        import json as _j
        path = self.root / "dispositions.jsonl"
        if not path.exists():
            return None
        latest = None
        for l in path.read_text(encoding="utf-8").splitlines():
            if not l.strip():
                continue
            rec = _j.loads(l)
            if rec.get("kind") == kind and rec.get("address") == address:
                latest = rec   # last line wins
        return latest

    # --- marks store (cognition-engine GROUP M) = the finding store, GENERALIZED ---
    # A MARK is what a mark-pass (run_role/run_reduce) writes about a source item. It GENERALIZES the
    # coherence finding record (above) along two axes the finding shape can't carry (Implementation Guide
    # §4.2, which supersedes M1's "same shape" over-claim):
    #   1. TARGET, not just an address. A finding is keyed by `address`; a mark targets a CLAIM or a SPAN
    #      (a sub-region of an item) as well as a plain address. `target` is the retrieval key and is an
    #      OPAQUE STRING here — the store turns it into bytes and back, exactly as append_annotation does NOT
    #      validate its `ui://` address (the S0/C1 grammar gate is the Suite/contract's job, where the
    #      semantic work lives). Illustrative shapes a caller may use: a bare `code://`/`ui://` address, a
    #      `claim://<item>#<n>` claim handle, or a `span://<item>#<start>-<end>` span handle — the store
    #      neither defines nor parses that grammar; it field-matches the whole string.
    #   2. mark_type + the mark payload. A mark carries `mark_type` (a string id FROM the mark-types
    #      registry — built by a SEPARATE lane; this store codes against it as an opaque id, never imports
    #      the registry) plus the run-1 mark payload `{value, confidence, source_pass, evidence}`. The
    #      finding's `{kind, state, source}` can't carry a mark_type-keyed retrieval.
    # WHY a sibling `marks.jsonl` leaf and NOT `findings.jsonl` (this is GENERALIZE, not PARALLEL — the
    # store rule forbids a second STORE/backend/resolver, NOT a second leaf-file on the ONE root; pins/
    # dispositions/annotations/chat already prove many `.jsonl` leaves = one store): `all_findings()` feeds
    # coherence_detect.burn_down (the orphan backlog rollup) which counts EVERY finding record — so a mark
    # written into findings.jsonl would silently inflate the live burn-down by a mark. The sibling leaf
    # leaves the finding read-path BYTE-FOR-BYTE untouched, so old findings still read exactly as before
    # (the preservation guarantee is trivial by construction) and a mark NEVER leaks into the finding/
    # burn-down corpus — the SAME "a spaced entry never leaks into the default corpus" discipline the
    # space-keyed vectors use. The shape REUSES append_finding/findings_for exactly (open-record, append-
    # only, address/key field-match) — this IS the finding store's pattern, generalized to a second target+
    # mark_type dimension.
    # PORTABLE BY FIELD, not string-parse (store constitution, mirroring put_vector's space/source): `target`
    # and `mark_type` are EXPLICIT record fields, so the per-type / per-target filter is a clean field match a
    # Supabase backend implements as `WHERE mark_type = X` / `WHERE target = X` — no address-string parsing.
    def append_mark(self, rec: dict) -> dict:
        """Persist a MARK — `{target, mark_type, value?, confidence?, source_pass?, evidence?, ...}` — to an
        append-only `marks.jsonl` at the store root (its OWN leaf, separate from findings.jsonl). Open-record
        like append_finding/append_annotation: `{ts, **rec}` splat through, so a mark-pass may carry any extra
        fields (run-1's `value/confidence/source_pass/evidence`, or new ones) without a schema edit. `target`
        and `mark_type` are the two retrieval keys (field matches, portable to a SQL `WHERE`). Append-only so
        a target accrues a mark THREAD (re-running a mark-pass re-appends; a reader folds to current — the same
        own/reflect property findings have). The store stays DUMB: it does NOT validate the target grammar
        (the S0/C1 gate is the Suite/contract lane, mirroring append_annotation) and does NOT import the
        mark-types registry (mark_type is an opaque string id from a separate lane). STRUCTURAL fail-loud (like
        put_vector's dim guard — structural, not semantic): `target` and `mark_type` must be present + non-empty
        strings, else the mark has no retrieval key and would be a silent black hole (store rule 4 — fail loud,
        never write an unfindable record)."""
        import json as _j
        from datetime import datetime, timezone
        target = rec.get("target")
        mark_type = rec.get("mark_type")
        if not isinstance(target, str) or not target.strip():
            raise ValueError(f"append_mark: a mark must carry a non-empty string `target` (got {target!r}) — "
                             "it is the retrieval key; an unfindable mark is a silent black hole (fail-loud).")
        if not isinstance(mark_type, str) or not mark_type.strip():
            raise ValueError(f"append_mark: a mark must carry a non-empty string `mark_type` (got {mark_type!r}) "
                             "— it is the second retrieval key (from the mark-types registry); fail-loud.")
        out = {"ts": datetime.now(timezone.utc).isoformat(), **rec}
        with (self.root / "marks.jsonl").open("a", encoding="utf-8") as f:
            f.write(_j.dumps(out) + "\n")
        return out

    def marks_for(self, target: str) -> list[dict]:
        """Every mark on `target`, oldest-first (the mark thread at that claim/span/address). Field-matches
        the append-only `marks.jsonl` by the `target` field — `target` IS the key (a clean SQL `WHERE target=X`
        for a Supabase backend). Reads disk every call (no cache), so a SECOND Suite over the same store root
        sees a prior Suite's marks (persistence-survives-reload). Mirrors findings_for exactly, on the marks
        leaf. An unmarked target → `[]` (the additive default; never an error)."""
        import json as _j
        path = self.root / "marks.jsonl"
        if not path.exists():
            return []
        out = []
        for l in path.read_text(encoding="utf-8").splitlines():
            if not l.strip():
                continue
            rec = _j.loads(l)
            if rec.get("target") == target:
                out.append(rec)
        return out

    def marks_by_type(self, mark_type: str) -> list[dict]:
        """Every mark of `mark_type`, oldest-first (the cross-target view of one mark kind — e.g. every
        `ai-fingerprint` mark, or every `principle-beneath` mark). Field-matches the append-only `marks.jsonl`
        by the `mark_type` field (a clean SQL `WHERE mark_type=X` for a Supabase backend). Reads disk every
        call (persistence-survives-reload). The SECOND retrieval projection over the SAME leaf — the marks
        generalization's second axis (by-type retrieval, which the finding store's address-only key can't do).
        An absent mark_type → `[]` (additive default; never an error)."""
        import json as _j
        path = self.root / "marks.jsonl"
        if not path.exists():
            return []
        out = []
        for l in path.read_text(encoding="utf-8").splitlines():
            if not l.strip():
                continue
            rec = _j.loads(l)
            if rec.get("mark_type") == mark_type:
                out.append(rec)
        return out

    def all_marks(self) -> list[dict]:
        """Every mark record, oldest-first (for a cross-mark rollup / the patterned-visibility render).
        Append-only over the marks leaf — the marks sibling of all_findings (and DISTINCT from it: marks
        NEVER appear in all_findings, so coherence_detect.burn_down's orphan count is unpolluted)."""
        import json as _j
        path = self.root / "marks.jsonl"
        if not path.exists():
            return []
        return [_j.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]

    # --- pin-state overlay (X7 · Convergence): operator's "keep this in view" override ---
    def append_pin(self, address: str, target_ts: str, pinned: bool) -> dict:
        """X7 — record a pin/unpin of an attached item, as an APPEND-ONLY control-state record.

        WHY a separate `pins.jsonl` log instead of a field ON the annotation/chat record (the literal
        guide wording): the annotation/chat stores are APPEND-ONLY immutable logs (store constitution —
        an 'update' is a new object + a moved pointer, never a mutated line). So we cannot edit the
        existing line to set `pinned:True`. Re-APPENDING the record with `pinned:True` ALSO fails: the
        X8 dedup keys on `(address, full text)` and keeps the FIRST occurrence (the unpinned one), so a
        re-append is silently dropped — the pin would be lost. And we MUST NOT write pin-state into
        `chat.jsonl` at all (every chat turn must be `source`-tagged and flows the training pipe — a pin
        control-record would pollute the twin's signal / the echo-guard).

        So pin-state is an ADDITIVE OVERLAY: a tiny append-only `pins.jsonl` keyed by the item's
        `(address, target_ts)` handle, resolved LAST-WINS on read (`pin_state_for`). This is additive
        CONTROL-state on the SAME store (one FsStore, one root) — NOT a parallel CONTEXT system: it adds
        no items to the gather, only flips the existing `pinned` field the gather already reads. The
        `pinned` field still appears ON the record `annotations_at`/`chats_at` return (the overlay is
        applied there), schema-additive: an item with no pin record reads as unpinned.

        Open-record, like append_annotation: `{ts, address, target_ts, pinned}`. Append-only so the pin
        HISTORY is preserved (a later unpin is a NEW record, last-wins on read — never a lost-update)."""
        import json as _j
        from datetime import datetime, timezone
        rec = {"ts": datetime.now(timezone.utc).isoformat(),
               "address": address, "target_ts": target_ts, "pinned": bool(pinned)}
        with (self.root / "pins.jsonl").open("a", encoding="utf-8") as f:
            f.write(_j.dumps(rec) + "\n")
        return rec

    def pin_state_for(self, address: str) -> dict:
        """X7 — the resolved pin-state at `address`: `{target_ts: pinned_bool}`, LAST-WINS over the
        append-only `pins.jsonl` (a later record for the same `(address, target_ts)` overrides — so an
        unpin after a pin reads as unpinned). Reads disk every call (no in-memory cache), so a second
        Suite over the same store root sees a prior Suite's pins (persistence-survives-reload). An
        address with no pin records → `{}` (every item reads as unpinned — the additive default)."""
        import json as _j
        path = self.root / "pins.jsonl"
        if not path.exists():
            return {}
        state: dict = {}
        for l in path.read_text(encoding="utf-8").splitlines():
            if not l.strip():
                continue
            rec = _j.loads(l)
            if rec.get("address") == address:
                state[rec.get("target_ts")] = bool(rec.get("pinned"))   # last line wins
        return state

    # --- persisted vector index (X12 · Convergence): {address: vector} keyed by the SAME address grammar ---
    # A SIBLING namespace of objects/refs/surfaced under the ONE store root (NOT a parallel store, NOT a
    # new DB — store constitution: one substrate, the address never changes). One file per ADDRESS (keyed by
    # _safe(address), the same key transform every other namespace uses), holding the open record
    # {address, vector, content_hash, dim, model, ts}. These are PURE substrate primitives — fabric-free:
    # the store NEVER calls a model (store constitution: store turns an address into bytes and back). The
    # embedding ORCHESTRATION (embed the corpus → degrade-with-warning when :8001 is down) lives in
    # store/vector_index.py, which CALLS these. The content_hash makes a re-build INCREMENTAL — the build
    # path re-embeds an address ONLY when its content_hash changed (compare get_vector(addr)["content_hash"]).
    # SPACE-KEYED VECTORS (cognition-engine GROUP L · L1/L2): a single source item is a POINT in MANY
    # PROJECTION SPACES (principle / topic / vocab / ...) — its principle-embedding and its topic-embedding
    # are DIFFERENT vectors of the SAME item, and a query must be able to rank WITHIN one space (k-NN in
    # principle-space ≠ in topic-space). This is done THROUGH the C1 address grammar, not an address hack:
    # the grammar already declares `vec://<source-address>#emb=<model>` (contracts/address.py); a SPACED
    # vector rides the SAME shape with a `#space=<projection>` fragment — `vec://<source-address>#space=<proj>`.
    # That composed `vec://` string is the per-(item,space) KEY (one file per (item,space) under _safe()),
    # so the same item in two spaces is two entries that never collide; the UNSPACED (default) vector keeps
    # its BARE source address as the key, byte-for-byte as before (back-compat — old single-space vectors
    # still resolve).
    #
    # PORTABILITY (store constitution + C4 Resolver Protocol — Supabase-later implements the SAME): the
    # space + the source are carried as EXPLICIT FIELDS on the open record (`space`, `source`), NOT only
    # buried inside the address string. So the per-space filter is a clean FIELD match (`rec["space"]==X`)
    # that a SQL backend implements as a `WHERE space = X` column — never an opaque `#space=` substring a
    # backend must parse out. Field and address AGREE by construction (the address is composed FROM source
    # + space). An entry with NO `space` field (every pre-cognition-engine entry) IS the default/None space.
    @staticmethod
    def space_address(source: str, space: str | None, emb: str | None = None) -> str:
        """Compose the per-(item,space[,EMBEDDER-LAYER]) KEY through the C1 grammar. space=None+emb=None → the
        BARE source address (the default space/layer — byte-identical to the pre-space key, so old single-space
        vectors are untouched). A named space → `vec://<source>#space=<proj>` (the existing vec:// `#`-fragment
        shape). A named `emb=<tag>` adds the `#emb=<embedder>` fragment (contracts/address.py ALREADY declares
        `vec://<source>#emb=<model>` for exactly this) so the SAME (item, space) can hold MULTIPLE embeddings —
        e.g. a BGE-M3 layer (emb=None, the default) AND a pplx layer (emb='pplx') side by side at DISTINCT keys.
        This is Tim's multi-layer model (2026-06-15: 'multiple different embeddings over the same data') — NON-
        destructive: emb=None preserves every existing key byte-for-byte; a named emb adds a new key, never
        overwrites the default layer."""
        if space is None and emb is None:
            return source
        addr = f"vec://{source}"
        if space is not None:
            addr += f"#space={space}"
        if emb is not None:
            addr += f"#emb={emb}"
        return addr

    def put_vector(self, address: str, vector: list, content_hash: str, *, dim: int, model: str,
                   space: str | None = None, source: str | None = None, emb: str | None = None) -> dict:
        """Persist one {address: vector} entry into the vectors/ namespace, ATOMICALLY (crash-durable
        tmp+fsync+os.replace — the SAME guarantee save_surfaced/save_graph give, so a reader sees the whole
        old entry or the whole new one, never a torn one). Keyed by _safe(address). Schema-additive open
        record. The store does NOT validate the vector (no model here) — the dim contract is enforced UP at
        the embed fabric (complete_embeddings dim= guard) and DOWN at the query cosine (retrieve._cosine);
        the store just persists the bytes by address.

        SPACE-KEYED (additive — every prior caller is unchanged): when `space`/`source` are given, the entry
        records WHICH projection space it belongs to (`space`) and WHICH source item it embeds (`source`),
        as EXPLICIT FIELDS (the portable per-space filter key — see the class-comment above). `address` is
        still the storage key (the composed `vec://<source>#space=<proj>` for a spaced entry — callers
        compose it via `space_address`). Omitting both = the default/None space (the unspaced legacy entry,
        keyed by its bare source address) — byte-for-byte the prior shape PLUS the two additive fields
        defaulting to None, so old readers (index_corpus/index_addresses with no space filter) see it
        exactly as today."""
        import json as _j
        from datetime import datetime, timezone
        # FAIL LOUD (rule 4): a SPACED entry MUST name its source item — `source` defaults to `address`, which
        # for a spaced entry is the composed `vec://…#space=` KEY, not the bare item. Letting that default
        # through would silently record a wrong round-trip (a per-space query would return the internal key,
        # not the item). build_index always passes the bare source, so this only bites a direct misuse.
        if space is not None and source is None:
            raise ValueError(
                f"put_vector: a spaced entry (space={space!r}) must pass `source` (the bare item address it "
                f"embeds) — defaulting source to the composed key {address!r} would record a wrong round-trip.")
        (self.root / "vectors").mkdir(parents=True, exist_ok=True)   # defensive (mirrors save_session) — never assume __init__ ran
        rec = {"address": address, "vector": list(vector), "content_hash": content_hash,
               "dim": int(dim), "model": model, "space": space, "emb": emb,
               # `source` defaults to the bare address for an unspaced entry (it IS its own source) so the
               # field is always present + truthful — a spaced entry carries the bare item address it embeds.
               "source": source if source is not None else address,
               "ts": datetime.now(timezone.utc).isoformat()}
        path = self.root / "vectors" / (self._safe(address) + ".json")
        self._fsync_atomic_write(path, _j.dumps(rec))
        return rec

    def get_vector(self, address: str) -> dict | None:
        """The persisted vector entry at `address`, or None if never built (an HONEST None — never a
        crash, never a fabricated zero-vector; rule 4). Reads disk every call (no in-memory cache), so a
        SECOND store over the same root sees a prior store's vectors (persistence-survives-reload)."""
        import json as _j
        p = self.root / "vectors" / (self._safe(address) + ".json")
        return _j.loads(p.read_text()) if p.exists() else None

    # A sentinel for "ALL spaces, no filter" — DISTINCT from space=None ("the DEFAULT/unspaced space only").
    # The default of the space= kwarg is None (default-space-only), which is exactly the pre-space behaviour
    # the live callers (consult/R2 query_index, index_staleness) depend on: a spaced entry must NOT leak into
    # the default corpus, or (a) retrieval is polluted and (b) two projections with different embed-dims make
    # retrieve._cosine fail-loud the instant they share the corpus. Pass space=ALL_SPACES to enumerate the
    # whole index regardless of space (used by nothing on the hot path; available for an index-wide audit).
    ALL_SPACES = object()

    def _vector_records(self) -> list[dict]:
        """Every persisted vector record, parsed — the ONE read path index_corpus/index_addresses share,
        with an incremental in-memory cache (X12-FAST, 2026-06-18). The naive path read+parsed all 5862
        `vectors/*.json` on EVERY call (~1.5s), re-paid per query_index and x8 per recall_for_decision →
        the >15s decision-surface hang. Here each file is parsed ONCE and revalidated cheaply.

        CORRECTNESS (the cache must never serve a stale ranking — no-silent-failures):
          - Revalidate EVERY call by a per-file (st_mtime_ns, st_size) signature from a single os.scandir.
            put_vector writes ATOMICALLY (tmp+fsync+os.replace) → a changed entry gets a new mtime → its
            signature differs → it is RE-PARSED. A NEW file appears in the scan → parsed. A REMOVED file
            drops from the scan → evicted. This holds ACROSS PROCESSES (Tim runs many sessions against one
            store): the signature is read from the filesystem, not an in-process counter, so another
            session's write is seen on the next call.
          - Only NEW/CHANGED files are read+parsed — the full ~1.5s parse is paid only on the first call
            after a (re)start; steady-state is scandir+stat (~10ms for 5862) + parse-of-the-few-changed.
          - The lock is held ONLY for the refresh (scandir+stat+parse); the returned list is consumed by
            the cosine/rerank stages OUTSIDE the lock, so a slow/abandoned recall thread never holds it.
        Returns the list of parsed record dicts (read-only — callers must not mutate them)."""
        import json as _j
        d = self.root / "vectors"
        with self._vec_cache_lock:
            cache = self._vec_cache
            if not d.exists():
                if cache:
                    cache.clear()
                return []
            try:
                scan = list(os.scandir(d))
            except OSError:
                return []
            seen = set()
            out = []
            for entry in scan:
                name = entry.name
                if not name.endswith(".json"):
                    continue
                seen.add(name)
                try:
                    st = entry.stat()
                except OSError:
                    continue
                sig = (st.st_mtime_ns, st.st_size)
                cached = cache.get(name)
                if cached is not None and cached[0] == sig:
                    rec = cached[1]                          # UNCHANGED — reuse the parsed record
                else:
                    try:
                        with open(entry.path, "r", encoding="utf-8") as fh:
                            rec = _j.loads(fh.read())
                    except Exception:
                        cache.pop(name, None)               # torn/unreadable → skip + forget (retry next call)
                        continue
                    cache[name] = (sig, rec)               # NEW/CHANGED — parse once, remember
                out.append(rec)
            if len(cache) != len(seen):                     # evict entries whose file vanished
                for gone in [n for n in cache if n not in seen]:
                    cache.pop(gone, None)
            return out

    def warm_vector_cache(self) -> int:
        """Populate the X12-FAST in-memory vector cache up front (returns the record count). Called at bridge
        startup so the FIRST semantic query after a (re)start — e.g. a decision-open, whose memory leg has a
        3s budget — is already warm; otherwise its cold full-parse (~1.5s) pushes the leg over budget and the
        decision resolves UNGROUNDED once (verified 2026-06-18: cold first-resolve 3.08s→timeout; after warm
        1.84s→grounded). Idempotent + cheap when already warm (revalidate-only)."""
        return len(self._vector_records())

    def index_addresses(self, space=None) -> list[str]:
        """Every address currently in the vector index, sorted. Reads the entries (the `address` field is
        the truth, not the _safe filename) so the canonical address is returned verbatim. Empty index → []
        (an honest empty — the embedder may have been DOWN at build, the index stays empty/partial honestly).

        SPACE filter (additive — default unchanged): `space=None` (the default) → only DEFAULT/unspaced
        entries (`rec.space is None`), so the legacy callers + index_staleness see EXACTLY today's address
        set (no spaced entries leaking in as phantom `extra`s). `space="<proj>"` → only that projection's
        entries. `space=FsStore.ALL_SPACES` → every entry regardless of space.

        Reads via the cached _vector_records() (X12-FAST) — the SAME per-record filter as before, byte-
        identical results; only the file-read is cached/incremental now."""
        out = []
        for rec in self._vector_records():
            if space is self.ALL_SPACES or rec.get("space") == space:
                out.append(rec["address"])
        return sorted(out)

    def index_corpus(self, space=None, emb=None, records=None) -> list[dict]:
        """The index as a corpus list `[{id: <item>, vector: [...]}]` — the EXACT shape nodes/retrieve.run
        consumes (id + vector), so the QUERY path feeds it straight in with NO reshaping and NO reimplemented
        cosine. Empty index → [] (query then returns empty + an honest note).

        SPACE filter (additive — default unchanged): `space=None` (the default) → only DEFAULT/unspaced
        entries, EXACTLY today's corpus (no spaced entry leaks in → no polluted ranking, no cross-dim cosine
        crash). `space="<proj>"` → only that projection's entries, and each entry's `id` is its `source` (the
        BARE item address it embeds) — so a per-space query RETURNS THE ITEM (which round-trips through the
        existing code://-resolution), not the internal vec://#space= key. `space=FsStore.ALL_SPACES` → every
        entry (id = the verbatim stored address). A legacy entry with no `source` field falls back to its
        own `address` (it IS its own source).

        Reads via the cached _vector_records() (X12-FAST) — the SAME per-record filter as before, byte-
        identical results; only the file-read is cached/incremental now.

        `records` (additive, default None — BYTE-IDENTICAL when absent): a PRE-FETCHED _vector_records()
        SNAPSHOT to filter, instead of fetching it here. THE SCANDIR-ONCE seam (2026-06-21): a MULTI-SPACE
        caller (recall_for_decision queries 6-7 spaces for ONE decision) would otherwise re-scandir+stat the
        whole vectors/ dir (~0.29s @ 49,853 files) per space = the bulk of the decision card-resolve memory
        leg's 3s-budget overrun once the 44k extraction layer grew the store. Fetching the snapshot ONCE and
        passing it to each per-space call collapses 6-7 scandirs to one. CORRECTNESS: the 6-7 queries of one
        recall are ONE logical read — a single consistent snapshot is MORE correct than 6 mid-write views; and
        each recall fetches a FRESH snapshot (no cross-call staleness — unlike a dir-mtime cache, which is
        UNSAFE on WSL ext4: create/delete don't bump dir mtime, proved by falsify-first 2026-06-21)."""
        out = []
        for rec in (records if records is not None else self._vector_records()):
            if space is self.ALL_SPACES:
                out.append({"id": rec["address"], "vector": rec["vector"]})
            elif rec.get("space") == space and rec.get("emb") == emb:
                # within a NAMED space, rank/return by the SOURCE item (not the internal vec://#space= key)
                # so the caller gets the item back; the default space (space is None) returns the bare address
                # (== source for an unspaced entry) — identical to the pre-space shape.
                # emb=None (default) matches the BGE default layer (existing entries: no emb field → None) —
                # byte-identical to pre-layer behaviour; emb='<tag>' selects that embedder layer (multi-layer model).
                _id = rec.get("source") if space is not None else rec["address"]
                out.append({"id": _id if _id is not None else rec["address"], "vector": rec["vector"]})
        return out

    def layers_by_space(self) -> dict:
        """Which embedder LAYERS each content/registry space carries: {space: [emb_tag, ...]} (the default/BGE
        layer shown as 'default'; a named embedder, e.g. 'pplx', as itself). The self-description of the
        multi-layer model — a picker (the FE) OR an agent (the dual interface) reads this to choose which layer
        to view. On-demand scan of the vectors dir (regex over the raw record text — avoids parsing the big
        vector array; NOT in any per-request hot path). Internal `scale:*` pyramid spaces + the default/unspaced
        space are excluded (only the lens/registry spaces a layer is chosen FOR)."""
        import re
        d = self.root / "vectors"
        if not d.exists():
            return {}
        sp_re = re.compile(r'"space":\s*(?:"([^"]*)"|null)')
        emb_re = re.compile(r'"emb":\s*(?:"([^"]*)"|null)')
        out: dict[str, set] = {}
        for p in d.glob("*.json"):
            try:
                txt = p.read_text()
            except Exception:
                continue
            sm = sp_re.search(txt)
            space = sm.group(1) if sm else None
            if not space or space.startswith("scale:"):    # skip default/unspaced + internal pyramid spaces
                continue
            em = emb_re.search(txt)
            out.setdefault(space, set()).add((em.group(1) if (em and em.group(1)) else "default"))
        return {sp: sorted(layers) for sp, layers in sorted(out.items())}

    def layer_dims(self) -> dict:
        """The vector DIMENSION of every (space, embedder-layer): {space: {emb_tag: full_dim}} (e.g.
        {'repo': {'default': 1024, 'pplx': 2560}}). The RESOLUTION picker reads this to derive the MRL zoom
        ladder PER layer (powers of two ≤ the full dim) — registry-true, never a hardcoded dim. All vectors in
        a layer share a dim (the embedder fixes it), so ONE vector per (space, emb) settles it: one pass over
        the vectors dir, regex to group, JSON-parse only the FIRST vector of each group (bounded by the #groups,
        not the #vectors). Same on-demand cost as layers_by_space — NOT a per-request hot path; the FE fetches
        it once. Internal scale:* pyramid spaces + the default/unspaced space are excluded."""
        import re, json as _json
        d = self.root / "vectors"
        if not d.exists():
            return {}
        sp_re = re.compile(r'"space":\s*(?:"([^"]*)"|null)')
        emb_re = re.compile(r'"emb":\s*(?:"([^"]*)"|null)')
        out: dict[str, dict] = {}
        for p in d.glob("*.json"):
            try:
                txt = p.read_text()
            except Exception:
                continue
            sm = sp_re.search(txt)
            space = sm.group(1) if sm else None
            if not space or space.startswith("scale:"):     # skip default/unspaced + internal pyramid spaces
                continue
            em = emb_re.search(txt)
            emb = em.group(1) if (em and em.group(1)) else "default"
            if out.get(space, {}).get(emb):                 # already settled this group's dim — skip the parse
                continue
            try:
                v = _json.loads(txt).get("vector")
                if isinstance(v, list) and v:
                    out.setdefault(space, {})[emb] = len(v)
            except Exception:
                continue
        return {sp: out[sp] for sp in sorted(out)}

    # --- surfaced-decision inbox (S7/D4): non-blocking gates, shared across faces ---
    def surfaced_lock(self):
        """T1-RACE — the store-level lock a CALLER holds around a surfaced read-modify-write
        (get_surfaced → mutate → save_surfaced) so two concurrent RMWs on the same item can't both
        read version V and last-writer-wins (lost update). Lives in the store because BOTH the Suite
        (resolve_surfaced, build_result writes) and governance.Inbox (set_status, resolve) mutate
        surfaced items — a Suite-only lock wouldn't serialize governance's writes. Re-entrant: a caller
        holding it can call save_surfaced (which re-acquires) without self-deadlock."""
        return self._surfaced_lock

    def save_surfaced(self, decision: dict) -> None:
        import json as _j
        # ATOMIC (T1-RACE): tmp + os.replace (same-filesystem rename is atomic) so a reader sees the
        # whole old file or the whole new one — never a half-written one against a concurrent read. The
        # naked write_text here (the prior code) could tear the file. Unique tmp PER WRITE (pid+thread)
        # so two concurrent writers never share a tmp name (each file stays whole). Held under the
        # surfaced lock so the WRITE is also serialized against other writers; callers that need the
        # READ serialized too hold surfaced_lock() across their whole get→mutate→save (RLock = no
        # self-deadlock when this re-acquires). S4: also fsync the tmp before the rename (crash-durable).
        path = self.root / "surfaced" / (self._safe(decision["id"]) + ".json")
        with self._surfaced_lock:
            self._fsync_atomic_write(path, _j.dumps(decision, indent=2))

    def list_surfaced(self) -> list[dict]:
        import json as _j
        return [_j.loads(p.read_text())
                for p in sorted((self.root / "surfaced").glob("*.json"))]

    def get_surfaced(self, sid: str) -> dict | None:
        import json as _j
        p = self.root / "surfaced" / (self._safe(sid) + ".json")
        return _j.loads(p.read_text()) if p.exists() else None

    # --- agent-session MAILBOX (Session Fabric §C: sessions message sessions) -------------------------
    # The fabric's one durable message leaf: `agent_sessions/mail.jsonl` — a SIBLING jsonl leaf on the
    # ONE root (the marks.jsonl precedent: many leaves ≠ a second store), living INSIDE the agent_sessions/
    # dir beside the registry's whole-record files (naming ruling N2 — dir `agent_sessions/`, never
    # `fabric/`, never the review-session `sessions/`). EVERYTHING the MCP face does to the fabric reduces
    # to an append here (the FLOOR split, synthesis §6.3): DELIVER/WAKE/CONSULT are INTENT records the
    # SUPERVISOR service pops and acts on (the face never spawns `claude -p`); queue-class records are
    # pulled by the target session itself at its next turn (sessions(op=inbox)).
    #
    # SHAPE (guide §C): {seq, id, ts, to: "session://<uuid>", from, verb, cas, thread, ...open record}.
    # The BODY rides the cas:// object store (put_content — immutable, dedup'd), NEVER inline — the mail
    # line stays small (<4KB ⇒ one O_APPEND write is never torn, the _append_ref_version argument) and a
    # reader resolves `cas` via get_content. `to`/`from`/`verb`/`thread` are EXPLICIT record fields
    # (portable-by-field: a Supabase backend filters WHERE to_session=X, no string parsing).
    #
    # SEQ UNIQUENESS — THE APPEND-EVENT LANDMINE, CLOSED HERE BY CONSTRUCTION: append_event's seq is
    # NOT cross-process-unique (its own surfaced NOTE above) and the mailbox's writers are exactly the
    # many-process workload (every Claude Code session runs its own MCP-face process over this one
    # store). So the WHOLE read-last-seq → +1 → append rides under graph_lock("agent_sessions:mail")
    # — the cross-process primitive (fcntl, the dispatch-claim precedent) — making mail seqs atomic +
    # monotonic + unique ACROSS PROCESSES. Mail is intent-class (a claim, not narration): the append is
    # flushed + fsync'd before return (the append_event durability class — an acknowledged post must
    # survive a crash; guide §A "write inject intent to mailbox (durable)").
    #
    # CONSUMPTION = PER-CONSUMER CURSOR REFS (synthesis §2.3's cheaper design): NO read-modify-write
    # status field on messages, ever. A durable consumer (the supervisor; any pull session that wants
    # its position to survive) holds a ref `agent-mail-cursor://<consumer>` whose value is the last
    # CONSUMED seq — reads are agent_mail_since(cursor), the advance is set_agent_mail_cursor (under its
    # own per-consumer graph_lock; regression refused — replay is an explicit `since=`, never a silent
    # cursor rollback). The ref rides set_ref/head, so every advance also lands in ref_history — the
    # consumption trail for free (introspective-data). Retention: keep-forever by design (criteria N8).
    def append_agent_mail(self, rec: dict) -> dict:
        """Persist ONE fabric mail record — `{to, from, verb, cas, thread?, ...}` — to the append-only
        `agent_sessions/mail.jsonl`. STRUCTURAL fail-loud (the append_mark discipline): `to` (the target
        session address — the supervisor's and the inbox's retrieval key), `from` (the REPLY path),
        `verb` (the routing decision the consumer honours) and `cas` (the body ref) must each be present
        + non-empty strings, else the record is an unroutable/unanswerable black hole (store rule 4).
        The store stays DUMB on semantics: it does NOT validate the verb vocabulary (the face/router
        gates that against the live state machine) nor the session id's existence (the registry lane's
        gate). Owns `seq`/`id`/`ts` (never caller-overridable); `thread` defaults to the mail id so every
        message is born aggregatable (consult fan replies join on it). Cross-process-unique seq under
        graph_lock; fsync'd before return (intent-class durability)."""
        import json as _j
        from datetime import datetime, timezone
        for field, why in (("to", "the target session — the supervisor's pop filter + the inbox key"),
                           ("from", "the reply path — an unanswerable message is a dead end"),
                           ("verb", "the routing decision (deliver|wake|consult|queue) its consumer honours"),
                           ("cas", "the body ref (put_content the message first; bodies never ride inline)")):
            v = rec.get(field)
            if not isinstance(v, str) or not v.strip():
                raise ValueError(
                    f"append_agent_mail: a mail record must carry a non-empty string `{field}` "
                    f"(got {v!r}) — it is {why}. Fail loud, never write an unroutable record.")
        d = self.root / "agent_sessions"
        d.mkdir(parents=True, exist_ok=True)   # defensive — never assume __init__ or the registry lane ran first
        path = d / "mail.jsonl"
        with self.graph_lock("agent_sessions:mail"):   # CROSS-PROCESS: seq read→+1→append is one critical section
            seq = 0
            if path.exists():
                with path.open("rb") as f:             # tail-read the last line (the append_event pattern)
                    try:
                        f.seek(-2, 2)
                        while f.read(1) != b"\n":
                            f.seek(-2, 1)
                    except OSError:
                        f.seek(0)
                    last = f.readline().decode().strip()
                if last:
                    seq = _j.loads(last).get("seq", -1) + 1
            out = {**rec}
            out["seq"] = seq
            out["id"] = f"mail-{seq}"
            out["ts"] = datetime.now(timezone.utc).isoformat()
            if not (isinstance(out.get("thread"), str) and out["thread"].strip()):
                out["thread"] = out["id"]
            with path.open("a", encoding="utf-8") as f:
                f.write(_j.dumps(out) + "\n")
                f.flush()
                os.fsync(f.fileno())                   # durable: an acknowledged intent survives a crash
            return out

    def agent_mail_since(self, seq: int = -1, *, to: str | None = None, verb: str | None = None,
                         thread: str | None = None, limit: int | None = None) -> list[dict]:
        """Mail records with seq STRICTLY greater than `seq`, OLDEST-first (FIFO — consumption order;
        the events_since semantics: a fresh consumer passes -1 for everything). Field-match filters
        (each a clean SQL WHERE for a Supabase backend): `to` (a session:// address — your inbox),
        `verb` (one routing class, e.g. the supervisor popping intents), `thread` (one conversation,
        e.g. a consult fan's aggregate). `limit` keeps the FIRST N after the cursor (oldest-first, so
        a paginating consumer never skips; the LAST returned record's seq is the next cursor). Reads
        disk every call (persistence-survives-reload; a sibling process's appends are seen on the next
        call). No mail / nothing matching → an HONEST empty list."""
        import json as _j
        path = self.root / "agent_sessions" / "mail.jsonl"
        if not path.exists():
            return []
        out = []
        for l in path.read_text(encoding="utf-8").splitlines():
            if not l.strip():
                continue
            rec = _j.loads(l)
            if rec.get("seq", -1) <= seq:
                continue
            if to is not None and rec.get("to") != to:
                continue
            if verb is not None and rec.get("verb") != verb:
                continue
            if thread is not None and rec.get("thread") != thread:
                continue
            out.append(rec)
            if limit is not None and len(out) >= limit:
                break
        return out

    def agent_mail_cursor(self, consumer: str) -> int:
        """The durable per-consumer consumption cursor: the last mail seq `consumer` has CONSUMED
        (-1 = never consumed — sees everything, the agent_mail_since fresh-consumer default). Read via
        the ref seam (head of `agent-mail-cursor://<consumer>`). A corrupt cursor value FAILS LOUD
        (never a silent reset-to-zero — that would silently replay or skip a consumer's whole box)."""
        if not isinstance(consumer, str) or not consumer.strip():
            raise ValueError(
                "agent_mail_cursor: `consumer` must be a non-empty string — the cursor is PER-CONSUMER "
                "(e.g. 'supervisor', or a session id reading its own inbox durably).")
        raw = self.head(f"agent-mail-cursor://{consumer}")
        if raw is None:
            return -1
        try:
            return int(raw.strip())
        except ValueError:
            raise ValueError(
                f"agent_mail_cursor: the stored cursor for {consumer!r} is corrupt ({raw!r}, not an "
                f"int). Fail loud — a guessed cursor silently replays or skips mail. Inspect "
                f"ref_history('agent-mail-cursor://{consumer}') for the trail; re-set it deliberately "
                f"via set_agent_mail_cursor.") from None

    def set_agent_mail_cursor(self, consumer: str, seq: int) -> dict:
        """ADVANCE `consumer`'s consumption cursor to `seq` (the last seq it has fully consumed).
        Monotonic by contract: a REGRESSION is refused fail-loud (replay is an explicit
        agent_mail_since(since=<older>) read, never a silent cursor rollback that would re-deliver
        intents — a re-popped WAKE is a duplicate spawn). Re-setting the SAME seq is idempotent-OK
        (a consumer may safely re-ack after a crash). The read→compare→set rides under a per-consumer
        graph_lock (cross-process: two processes sharing one consumer identity cannot interleave).
        Each advance lands in ref_history (the consumption trail, free introspective data)."""
        if not isinstance(seq, int) or isinstance(seq, bool):
            raise ValueError(f"set_agent_mail_cursor: seq must be an int (got {seq!r}).")
        with self.graph_lock(f"agent_sessions:cursor:{consumer}"):
            cur = self.agent_mail_cursor(consumer)   # also validates `consumer` + fails loud on corruption
            if seq < cur:
                raise ValueError(
                    f"set_agent_mail_cursor: refusing to move {consumer!r} BACKWARD ({cur} → {seq}) — "
                    f"a silent rollback re-delivers consumed intents (a re-popped wake = a duplicate "
                    f"spawn). To re-read old mail, pass since={seq} to agent_mail_since explicitly; "
                    f"the cursor only advances.")
            self.set_ref(f"agent-mail-cursor://{consumer}", str(seq))
            return {"consumer": consumer, "cursor": seq, "previous": cur}
