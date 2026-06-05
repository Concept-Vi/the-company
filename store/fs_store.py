"""FilesystemResolver — the addressed store (C1/C4). Implements contracts.resolver.Resolver.

Stdlib + pydantic. Content-addressed immutable objects, mutable refs, typed provenance,
lineage walk, and the memo index. See store/AGENTS.md (never mutate cas://; ext4 only).
"""
from __future__ import annotations
import hashlib
import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from contracts.address import Provenance


class FsStore:
    def __init__(self, root):
        self.root = Path(root)
        for d in ("objects", "refs", "ref_history", "meta", "memo", "graphs", "surfaced", "locks"):
            (self.root / d).mkdir(parents=True, exist_ok=True)
        # --- store-level concurrency locks (T1-SEQ / T1-RACE) ---
        # The bridge is a ThreadingHTTPServer over ONE Suite, so read-modify-write paths in the store
        # are run UNSERIALIZED across threads → lost updates + colliding sequence numbers. The locks
        # live HERE (in the store) — not in the Suite — because BOTH the Suite (resolve_surfaced,
        # build_result writes) AND governance.Inbox (set_status, resolve) mutate surfaced items; a lock
        # held only by the Suite would not serialize governance's writes against the Suite's. The store
        # is the one object every writer reaches, so serializing here is the only place that covers all
        # callers. Re-entrant locks so a method that calls another locked store method can't self-deadlock.
        import threading as _t
        self._event_lock = _t.RLock()       # T1-SEQ: append_event seq = read-last → +1 → append (atomic)
        self._surfaced_lock = _t.RLock()     # T1-RACE: surfaced read-modify-write across both faces
        self._graph_locks_guard = _t.Lock()  # guards the per-graph lock map below
        self._graph_locks: dict = {}         # T1-RACE: one lock per graph id (load→mutate→save serialized)
        # --- S4: cross-PROCESS advisory file locks (fcntl) ---
        # The threading locks above serialize threads WITHIN ONE process. The bridge and the MCP face are
        # TWO separate processes on ONE STORE_DIR (bridge.py + mcp_face/server.py both Suite(FsStore(
        # STORE_DIR))), and threading.RLock CANNOT cross that boundary (seams-engine Seam 8b, CONFIRMED).
        # So an OS-level advisory lock (fcntl.flock) is ADDED ON TOP — one lock FILE per resource (per
        # graph id; one for the dispatch claim), never a single global lock (a global one would serialize
        # the whole night + invite the deadlock the spec warns about). LOCK ORDER (documented, applied
        # identically everywhere): the in-process threading RLock is the OUTER lock; the fcntl OS lock is
        # the INNER lock, taken ONLY at the OUTERMOST in-process acquire (depth-counted below) and released
        # on the outermost exit. A nested same-resource acquire reuses the already-held OS lock — it does
        # NOT re-flock (fcntl flock on a 2nd fresh fd for a lock THIS process already holds would BLOCK on
        # itself = self-deadlock; depth-counting sidesteps it). Because the threading RLock guarantees only
        # ONE thread of THIS process is ever inside the critical section, the single shared fd + depth count
        # is race-free. fcntl is POSIX-only (the deploy target is WSL/Linux ext4 — store/AGENTS.md).
        self._os_lock_guard = _t.Lock()      # guards the os-lock fd/depth maps below
        self._os_lock_fds: dict = {}         # resource-key → open fd holding flock(LOCK_EX) while depth>0
        self._os_lock_depth: dict = {}       # resource-key → re-entrant depth (this process/thread)

    def graph_lock(self, gid: str):
        """One re-entrant lock per graph id, created on demand (threadsafe). The Suite's whole-graph
        load→mutate→save_graph mutations (create_node/connect/delete_node/set_config/set_position) hold
        this around the WHOLE read-modify-write so two concurrent mutations on the same graph can't both
        load version V and last-writer-wins (lost update). Re-entrant so a mutation that nests another
        locked call on the same graph does not self-deadlock.

        S4: returns a COMPOUND context manager — the in-process RLock (thread mutual-exclusion) wrapping
        the per-resource fcntl OS lock (cross-PROCESS mutual-exclusion). LOCK ORDER: RLock outer, fcntl
        inner. Existing callers `with self.store.graph_lock(gid):` get cross-process safety for free —
        no call-site change (S4 PRESERVES the existing in-process guarantee, adds the cross-process one)."""
        import threading as _t
        with self._graph_locks_guard:
            lk = self._graph_locks.get(gid)
            if lk is None:
                lk = _t.RLock()
                self._graph_locks[gid] = lk
        return self._compound_lock(lk, f"graph__{self._safe(gid)}")

    def dispatch_lock(self, key):
        """S4 — cross-process advisory lock for the wire's exactly-once dispatch CHECK→CLAIM (keyed on
        the resolve seq). The Suite already holds a per-seq THREADING lock around the check→emit critical
        section (suite.py _dispatch_lock); this is the OS-level companion so two FACES (bridge + MCP, or a
        face + the wire) can't both clear the exactly-once check and double-launch `claude -p`. The durable
        decision.dispatch event remains the cross-RESTART guarantee; this fcntl lock adds the CONCURRENT
        (two-faces-at-once) guarantee the durable event alone does not cover. The Suite wraps its existing
        per-seq RLock as the OUTER lock; pass that RLock here so the compound lock keeps the same RLock-outer
        / fcntl-inner order as graph_lock (one consistent order = no deadlock)."""
        return self._os_lock_cm(f"dispatch__{self._safe(str(key))}")

    @contextmanager
    def _compound_lock(self, rlock, resource_key: str):
        """RLock (outer, thread mutual-exclusion + re-entrancy) → fcntl OS lock (inner, cross-process).
        The OS lock is taken only at the OUTERMOST RLock acquire (the depth-count in _os_lock_cm does that)
        — a nested same-thread acquire reuses the held RLock and the held OS lock. This is THE documented
        lock order, applied identically at every graph mutation site."""
        with rlock:
            with self._os_lock_cm(resource_key):
                yield

    @contextmanager
    def _os_lock_cm(self, resource_key: str):
        """Acquire/release a per-resource fcntl advisory file lock, RE-ENTRANT within this process via a
        depth count. Only the OUTERMOST acquire opens the fd + flock(LOCK_EX) (a blocking exclusive lock);
        inner acquires just bump the depth and reuse the held fd. The outermost release flock(LOCK_UN) +
        closes the fd. Guarded by a threading.Lock so the fd/depth maps are mutated atomically. POSIX-only
        (fcntl); the deploy target is Linux/WSL ext4. The lock FILE is its own file under locks/ — never
        the data file (so an flock on the lock file never interferes with the atomic tmp+replace writes)."""
        import fcntl
        # ENTER — outermost opens + flocks; inner bumps depth. The flock() (which BLOCKS) is taken OUTSIDE
        # the guard so a real cross-process wait does not freeze every other resource's lock bookkeeping.
        need_acquire = False
        with self._os_lock_guard:
            depth = self._os_lock_depth.get(resource_key, 0)
            if depth == 0:
                lf = self.root / "locks" / (resource_key + ".lock")
                fd = os.open(str(lf), os.O_CREAT | os.O_RDWR, 0o644)
                self._os_lock_fds[resource_key] = fd
                need_acquire = True
            self._os_lock_depth[resource_key] = depth + 1
        if need_acquire:
            try:
                fcntl.flock(self._os_lock_fds[resource_key], fcntl.LOCK_EX)
            except BaseException:
                # the blocking flock failed/was interrupted — undo the bookkeeping + close the fd so we
                # NEVER leave a phantom-held lock (the deadlock the spec warns about). Fail loud.
                with self._os_lock_guard:
                    fd = self._os_lock_fds.pop(resource_key, None)
                    self._os_lock_depth[resource_key] = self._os_lock_depth.get(resource_key, 1) - 1
                    if self._os_lock_depth.get(resource_key, 0) <= 0:
                        self._os_lock_depth.pop(resource_key, None)
                if fd is not None:
                    os.close(fd)
                raise
        try:
            yield
        finally:
            # EXIT — outermost releases + closes; inner just decrements. Always runs (finally) so a raising
            # critical section NEVER strands the OS lock held (cross-process deadlock prevention).
            with self._os_lock_guard:
                depth = self._os_lock_depth.get(resource_key, 1) - 1
                if depth <= 0:
                    self._os_lock_depth.pop(resource_key, None)
                    fd = self._os_lock_fds.pop(resource_key, None)
                else:
                    self._os_lock_depth[resource_key] = depth
                    fd = None
            if fd is not None:
                try:
                    fcntl.flock(fd, fcntl.LOCK_UN)
                finally:
                    os.close(fd)

    @staticmethod
    def _fsync_atomic_write(path: Path, data: str) -> None:
        """S4 — a crash-durable atomic write: write to a unique tmp, fsync the tmp's BYTES to disk, then
        os.replace (atomic same-fs rename) into place. Without the fsync, os.replace makes a possibly-
        still-in-page-cache tmp the live file → a crash can leave a zero/short file as the "committed"
        version (Reality Map §1 "no crash-durable resume"). With it, the bytes are on disk BEFORE the
        rename names them the truth. Unique tmp per write (pid+thread) so concurrent writers never share a
        tmp name (last-writer-wins, each file whole). Mirrors the existing tmp+os.replace pattern, adding
        the durability barrier. (Directory-entry durability after the rename is best-effort; the data-loss
        case this kills is a torn/empty file masquerading as committed.)"""
        import threading as _t
        tmp = path.with_name(f"{path.name}.{os.getpid()}.{_t.get_ident()}.tmp")
        fd = os.open(str(tmp), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
        try:
            os.write(fd, data.encode("utf-8"))
            os.fsync(fd)                      # the durability barrier — bytes on disk before the rename
        finally:
            os.close(fd)
        os.replace(str(tmp), str(path))       # atomic: a reader sees the whole old file or the whole new

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
        # Unique tmp PER WRITE (pid+thread): two concurrent same-graph writers (two /api/move, or a
        # move racing an MCP-face create_node/connect on the threading server) must not share one tmp
        # name — a fixed name lets their write_texts interleave into invalid JSON that os.replace then
        # makes the LIVE file (durable corruption). Unique tmp + atomic replace = last-writer-wins, each
        # file always whole. S4: also fsync the tmp before the rename (crash-durable — the in-process
        # graph_lock + the cross-process fcntl graph lock serialize the WRITE; the fsync makes it durable).
        path = self.root / "graphs" / (self._safe(graph.id) + ".json")
        self._fsync_atomic_write(path, graph.model_dump_json(indent=2))

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
            # S4: fsync the appended line to disk before returning. The durable decision.dispatch claim
            # (the wire's exactly-once guarantee) is written through here via _emit_durable — if it were
            # only in the page cache, a crash after the caller acted on a "success" return could lose the
            # claim and allow a double-launch on restart. fsync the fd so the claim is on disk before the
            # caller proceeds. (Append-only log: the fsync is on the appended bytes, no rename needed.)
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
