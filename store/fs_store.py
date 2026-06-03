"""FilesystemResolver — the addressed store (C1/C4). Implements contracts.resolver.Resolver.

Stdlib + pydantic. Content-addressed immutable objects, mutable refs, typed provenance,
lineage walk, and the memo index. See store/AGENTS.md (never mutate cas://; ext4 only).
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any

from contracts.address import Provenance


class FsStore:
    def __init__(self, root):
        self.root = Path(root)
        for d in ("objects", "refs", "meta", "memo", "graphs", "surfaced"):
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

    def graph_lock(self, gid: str):
        """One re-entrant lock per graph id, created on demand (threadsafe). The Suite's whole-graph
        load→mutate→save_graph mutations (create_node/connect/delete_node/set_config/set_position) hold
        this around the WHOLE read-modify-write so two concurrent mutations on the same graph can't both
        load version V and last-writer-wins (lost update). Re-entrant so a mutation that nests another
        locked call on the same graph does not self-deadlock."""
        import threading as _t
        with self._graph_locks_guard:
            lk = self._graph_locks.get(gid)
            if lk is None:
                lk = _t.RLock()
                self._graph_locks[gid] = lk
            return lk

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
        (self.root / "refs" / self._safe(logical)).write_text(cas)

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
        import os as _os
        import threading as _t
        path = self.root / "graphs" / (self._safe(graph.id) + ".json")
        # Unique tmp PER WRITE (pid+thread): two concurrent same-graph writers (two /api/move, or a
        # move racing an MCP-face create_node/connect on the threading server) must not share one tmp
        # name — a fixed name lets their write_texts interleave into invalid JSON that os.replace then
        # makes the LIVE file (durable corruption). Unique tmp + atomic replace = last-writer-wins, each
        # file always whole. (Traded import-minimalism for write-concurrency correctness.)
        tmp = path.with_name(f"{path.name}.{_os.getpid()}.{_t.get_ident()}.tmp")
        tmp.write_text(graph.model_dump_json(indent=2))
        tmp.replace(path)

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
            with path.open("a", encoding="utf-8") as f:
                f.write(_j.dumps(rec) + "\n")
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
