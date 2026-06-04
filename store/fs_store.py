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
        for d in ("objects", "refs", "meta", "memo", "graphs", "surfaced", "locks"):
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
        # DURABLE (T-FSYNC): _atomic_write_fsync fsyncs the tmp's bytes BEFORE the rename + fsyncs the
        # parent dir AFTER, so this hot output write survives a crash (every node fire writes its ref here).
        path = self.root / "refs" / self._safe(logical)
        _atomic_write_fsync(path, cas)

    def head(self, logical: str) -> str | None:
        p = self.root / "refs" / self._safe(logical)
        return p.read_text() if p.exists() else None

    # --- provenance + lineage ---
    def write_provenance(self, prov: Provenance) -> None:
        (self.root / "meta" / (self._safe(prov.address) + ".json")).write_text(
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
        (self.root / "memo" / self._safe(sig)).write_text(cas)

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
        import os as _os
        import threading as _t
        (self.root / "sessions").mkdir(parents=True, exist_ok=True)
        path = self.root / "sessions" / (self._safe(session["id"]) + ".json")
        tmp = path.with_name(f"{path.name}.{_os.getpid()}.{_t.get_ident()}.tmp")
        tmp.write_text(_j.dumps(session, indent=2))
        tmp.replace(path)

    def load_session(self, sid: str) -> dict | None:
        import json as _j
        p = self.root / "sessions" / (self._safe(sid) + ".json")
        return _j.loads(p.read_text()) if p.exists() else None

    def list_sessions(self) -> list[str]:
        d = self.root / "sessions"
        return sorted(p.stem for p in d.glob("*.json")) if d.exists() else []

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
        import os as _os
        import threading as _t
        # ATOMIC (T1-RACE): tmp + os.replace (same-filesystem rename is atomic) so a reader sees the
        # whole old file or the whole new one — never a half-written one against a concurrent read. The
        # naked write_text here (the prior code) could tear the file. Unique tmp PER WRITE (pid+thread)
        # so two concurrent writers never share a tmp name (each file stays whole). Held under the
        # surfaced lock so the WRITE is also serialized against other writers; callers that need the
        # READ serialized too hold surfaced_lock() across their whole get→mutate→save (RLock = no
        # self-deadlock when this re-acquires).
        path = self.root / "surfaced" / (self._safe(decision["id"]) + ".json")
        with self._surfaced_lock:
            tmp = path.with_name(f"{path.name}.{_os.getpid()}.{_t.get_ident()}.tmp")
            tmp.write_text(_j.dumps(decision, indent=2))
            tmp.replace(path)

    def list_surfaced(self) -> list[dict]:
        import json as _j
        return [_j.loads(p.read_text())
                for p in sorted((self.root / "surfaced").glob("*.json"))]

    def get_surfaced(self, sid: str) -> dict | None:
        import json as _j
        p = self.root / "surfaced" / (self._safe(sid) + ".json")
        return _j.loads(p.read_text()) if p.exists() else None
