"""runtime/identity.py — the ONE identity resolver + presence view (read-time, single-writer-safe).

THE ROOT DISEASE this closes: three identity spaces with no join —
  • ephemeral HANDLE  `ch-XXXX`  (churns per launch; keys .data/channels/<handle>.json)
  • durable SESSION UUID         (stable; keys <store>/agent_sessions/<uuid>.json + the fold)
  • substrate AGENT ID           (free text; keys agent_mcp.* in the external admin server)
No code mapped between them, so "who is this and how do I reach them right now" had no answer that
survives a handle churn. THIS module is that answer.

WHAT IT IS: a READ-TIME PROJECTION (never a new store, never a writer). It composes the stores that
already exist and adds the missing join:
  • cc_channels.live_sessions()  — .mjs transport presence (pid-pruned = truth), the HANDLE space.
  • the supervisor /sessions probe (cc_channels._sup_sessions) — the SUPERVISED-live truth (UUID space).
  • principals.resolve_kind      — agent|viewer|ambiguous (identity kind), same regs.
  • session_scan claude_pid + the self-marker — the handle→UUID RECOVERY ladder.
It DERIVES suite's F1.2 state (supervised-live | unsupervised-live | closed) at READ TIME, exactly as
suite.py:923-927 prescribes ("liveness refinement is derived at read time by callers"), and it EMITS
NOTHING — respecting the supervisor SINGLE-WRITER law (session_supervisor.py:14-17: only the supervisor
writes agent_sessions.* events). unsupervised-live becomes real here (a live .mjs session that the
supervisor does NOT own) — the state the vocabulary defined but nothing ever surfaced.

THE PRESENCE ROW (one durable identity, all its reachability):
  {uuid, handle, as_id, agent_id, cwd, description, model, kind,
   state: supervised-live|unsupervised-live|closed,
   transports: ["supervised"] | ["channel"] | [],   # what can reach it THIS INSTANT (by probe)
   reachable: bool, port, pid, claude_pid, forked_from, reg, sources}

Downstream: runtime/router.py picks a transport from `transports`; the unified channel fan + the
send() tool resolve targets here. The 5 missing resolvers of the map (R1 handle→UUID, R2 UUID→handle,
R4 agent-id→*, R5 grammar-fallback) all resolve THROUGH this module.
"""
from __future__ import annotations

import glob
import json
import os
import time as _time

from runtime import cc_channels as cc
from runtime import principals
from runtime import session_scan

# The address schemes a target may arrive dressed in (contracts/address.py grammar). We strip the
# scheme and resolve the bare id — R5: `session://ch-h8xvlf6i` must RESOLVE, not raise (the traced
# broken circuit). clone://<sid>/<at> carries the source sid as its first path segment.
_SCHEMES = ("session://", "agent://", "clone://")


def _strip_scheme(target: str) -> str:
    """Reduce an addressed target to the bare id it names. `session://X`→`X`; `agent://slug`→`slug`;
    `clone://<sid>/<at>`→`<sid>` (the source session). A bare id passes through untouched."""
    t = (target or "").strip()
    for s in _SCHEMES:
        if t.startswith(s):
            rest = t[len(s):]
            return rest.split("/", 1)[0] if s == "clone://" else rest
    return t


# ── R1 handle→UUID recovery ladder ─────────────────────────────────────────────────────────────
# 83% of live .mjs regs carry session_id="" (the SessionStart-hook backfill loses its race). Recover
# the durable UUID for ANY live handle, in descending reliability. Every rung is a pure read.

def _uuid_from_environ(claude_pid) -> str | None:
    """The STRONG rung: the Claude Code CLI stamps its own session uuid into its process environment
    (CLAUDE_CODE_SESSION_ID; COMPANY_SESSION_ID when a launcher pins it). Read /proc/<claude_pid>/environ
    — the CLI's own truth, independent of any reg field or hook. (Absent on pre-2026-07 sessions whose
    CLI predates the var — those fall through to the marker/fd rungs or stay reachable-but-uuid-unknown.)"""
    try:
        cp = int(claude_pid)
    except (TypeError, ValueError):
        return None
    try:
        with open(f"/proc/{cp}/environ", "rb") as f:
            raw = f.read()
    except OSError:
        return None
    for kv in raw.split(b"\0"):
        for key in (b"CLAUDE_CODE_SESSION_ID=", b"COMPANY_SESSION_ID="):
            if kv.startswith(key):
                val = kv[len(key):].decode("utf-8", "replace").strip()
                if val:
                    return val
    return None


def _uuid_from_fd(claude_pid) -> str | None:
    """Weak last rung: IF the claude process happens to hold its transcript .jsonl open, read
    /proc/<claude_pid>/fd/* for the open ~/.claude/projects/*/*.jsonl basename-uuid. (Claude usually
    appends-and-closes, so this rarely fires — kept only as a harmless final attempt.)"""
    try:
        cp = int(claude_pid)
    except (TypeError, ValueError):
        return None
    fddir = f"/proc/{cp}/fd"
    try:
        names = os.listdir(fddir)
    except OSError:
        return None
    proj = session_scan.PROJECTS_DIR
    for n in names:
        try:
            tgt = os.readlink(os.path.join(fddir, n))
        except OSError:
            continue
        if tgt.startswith(proj) and tgt.endswith(".jsonl"):
            base = os.path.basename(tgt)[:-len(".jsonl")]
            if base:
                return base
    return None


# ── the process-start ↔ transcript-first-event match (SAFE deep rung) ────────────────────────────
# A live session's claude process started at a wall-clock time; a FRESH session's transcript first
# event is within seconds of that. Match the ONE transcript in the session's cwd whose first-event ts
# is UNIQUE within a tolerance of the process start → high-confidence, no-guess recovery for regs that
# captured nothing else. (A --resume'd session's transcript predates its process start, so no match
# lands inside the tolerance — correctly rejected, never mis-guessed. Two sessions starting within the
# tolerance in one cwd → AMBIGUOUS → rejected. So a hit is unique + confident.)
_HZ = os.sysconf("SC_CLK_TCK") if hasattr(os, "sysconf") else 100
_BTIME = None
for _ln in (open("/proc/stat") if os.path.exists("/proc/stat") else []):
    if _ln.startswith("btime "):
        try: _BTIME = int(_ln.split()[1])
        except (ValueError, IndexError): pass
        break


def _proc_start_wall(pid) -> "float | None":
    try:
        d = open(f"/proc/{int(pid)}/stat").read()
        fields = d[d.rindex(")") + 2:].split()        # after the (comm) group, field indexing is stable
        return (_BTIME + int(fields[19]) / _HZ) if _BTIME is not None else None
    except (OSError, ValueError, TypeError, IndexError):
        return None


def _transcript_first_ts(path: str) -> "float | None":
    from datetime import datetime
    try:
        with open(path) as f:
            for line in f:
                try: o = json.loads(line)
                except ValueError: continue
                ts = o.get("timestamp")
                if ts:
                    return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except OSError:
        return None
    return None


def _uuid_from_starttime(reg: dict, tolerance: float = 10.0) -> "str | None":
    cp, cwd = reg.get("claude_pid"), reg.get("cwd")
    if not cp or not cwd:
        return None
    ps = _proc_start_wall(cp)
    if ps is None:
        return None
    pdir = os.path.join(session_scan.PROJECTS_DIR, session_scan._encode_cwd(cwd))
    within = []
    for tp in glob.glob(os.path.join(pdir, "*.jsonl")):
        ft = _transcript_first_ts(tp)
        if ft is not None and abs(ft - ps) <= tolerance:
            within.append(os.path.basename(tp)[:-len(".jsonl")])
    return within[0] if len(within) == 1 else None       # unique-within-tolerance ONLY (else no guess)


def recover_uuid(reg: dict, *, deep: bool = False) -> "tuple[str | None, str]":
    """The handle→UUID ladder for one .mjs reg. Returns (uuid_or_None, how). Pure reads, no writes.
    `deep=True` adds the (slower) process-start↔transcript match as a final rung — correctness over
    speed, used when resolving a specific target; the fleet LIST stays fast (deep=False)."""
    sid = (reg.get("session_id") or "").strip()
    if sid:
        return sid, "reg.session_id"
    tp = (reg.get("transcript_path") or "").strip()
    if tp.endswith(".jsonl"):
        base = os.path.basename(tp)[:-len(".jsonl")]
        if base:
            return base, "reg.transcript_path"
    cp = reg.get("claude_pid")
    if cp not in (None, "", -1):
        env = _uuid_from_environ(cp)                # rung 3 (STRONG): the CLI's own CLAUDE_CODE_SESSION_ID
        if env:
            return env, "proc-environ(claude_pid)"
        try:                                        # rung 4: the SessionStart-hook self-marker (by claude_pid)
            m = json.load(open(os.path.join(session_scan.SELF_MARKER_DIR, f"{int(cp)}.json")))
            msid = (m.get("session_id") or "").strip()
            if msid:
                return msid, "self-marker(claude_pid)"
        except (OSError, ValueError, TypeError):
            pass
        u = _uuid_from_fd(cp)                        # rung 5 (weak): a live open transcript, if any
        if u:
            return u, "proc-fd(claude_pid)"
    if deep:                                        # rung 6 (deep): unique process-start↔transcript match
        u = _uuid_from_starttime(reg)
        if u:
            return u, "proc-starttime-match"
    return None, "unrecovered"


def reconcile_registry(chan_dir: str | None = None) -> dict:
    """Self-healing capture: for every live .mjs reg with an empty session_id, DEEP-recover its durable
    UUID and, on a CONFIDENT recovery (any ladder rung — all are ground-truth or unique-match, never a
    guess), BACKFILL it into the reg file. Makes a session durably resolvable by uuid (surviving its
    handle churn) + turns future reads into the fast rung-1 path. Mirrors write_self_marker/seed_self's
    established reg-backfill. Returns {scanned, backfilled:[{handle,uuid,how}], skipped}."""
    d = chan_dir or cc.CHAN_DIR
    out = {"scanned": 0, "backfilled": [], "skipped": 0}
    if not os.path.isdir(d):
        return out
    for fn in os.listdir(d):
        if not fn.endswith(".json") or fn.startswith("_"):
            continue
        p = os.path.join(d, fn)
        reg = cc._read_reg(p)
        if not reg or (reg.get("session_id") or "").strip():
            continue
        out["scanned"] += 1
        uuid, how = recover_uuid(reg, deep=True)
        if not uuid:
            out["skipped"] += 1
            continue
        reg["session_id"] = uuid
        reg["session_id_recovered_by"] = how          # provenance (never silently rewrite identity)
        try:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(reg, f, indent=2)
            out["backfilled"].append({"handle": reg.get("handle"), "uuid": uuid, "how": how})
        except OSError:
            out["skipped"] += 1
    return out


# ── the supervisor-owned (supervised-live) truth, by live probe ──────────────────────────────────
def _supervised_index(base: str | None = None) -> "tuple[bool, dict]":
    """Probe the supervisor /sessions ONCE. Returns (reachable, {uuid|as_id -> record}) for every
    non-closed owned session. reachable=False (supervisor down / mid-restart) is honest — callers must
    not read it as 'nobody is supervised'. A record: {id: as-…, claude_session_id?, state, ...}."""
    base = (base or cc.DEFAULT_SUPERVISOR_BASE).rstrip("/")
    reachable, recs = cc._sup_sessions(base)
    idx: dict = {}
    for r in recs or []:
        if r.get("state") == "closed":
            continue
        as_id = r.get("id")
        uuid = r.get("claude_session_id") or r.get("session_id")
        rec = {"as_id": as_id, "uuid": uuid, "state": r.get("state"), "base": base, "raw": r}
        if uuid:
            idx[uuid] = rec
        if as_id:
            idx.setdefault(as_id, rec)
    return reachable, idx


def _row_from_channel_reg(reg: dict, supervised_idx: dict, deep: bool = False) -> dict:
    """Build a PresenceRow for a live .mjs member. State is DERIVED: if the supervisor ALSO owns this
    session (its recovered uuid is in the supervised index) it is supervised-live; else it is a live-
    but-unowned session = unsupervised-live (the keystone) — reachable via the .mjs `channel` transport."""
    transport = cc._transport_of(reg)                        # "channel" (default) or "supervised"
    uuid, how = recover_uuid(reg, deep=deep)
    kind = principals.resolve_kind(reg).get("kind")
    sup = (uuid and supervised_idx.get(uuid)) or None
    if transport == "supervised" or sup:
        state, transports = "supervised-live", ["supervised"]
    else:
        state, transports = "unsupervised-live", ["channel"]
    return {
        "uuid": uuid, "uuid_how": how,
        "handle": reg.get("handle"),
        "as_id": (sup or {}).get("as_id") or reg.get("supervisor_session"),
        "agent_id": reg.get("agent_id") or (reg.get("profile") or {}).get("agent_id"),
        "cwd": reg.get("cwd"), "description": reg.get("description"), "model": reg.get("model"),
        "kind": kind, "state": state, "transports": transports, "reachable": True,
        "port": reg.get("port"), "pid": reg.get("pid"), "claude_pid": reg.get("claude_pid"),
        "forked_from": reg.get("forked_from"),
        "reg": reg, "sources": ["cc_channels"] + (["supervisor"] if sup else []),
    }


def presence_all(base: str | None = None, deep: bool = False) -> list[dict]:
    """The unified LIVE fleet — every session reachable RIGHT NOW, as PresenceRows, deduped by durable
    uuid (falling back to handle when a uuid can't be recovered). Union of:
      • cc_channels.live_sessions()  — .mjs members (channel + cc_clone-supervised regs), pid-truth.
      • the supervisor /sessions probe — supervised-live sessions that have NO .mjs reg (the /spawn'd
        case, map gap G20): reachable via the supervisor `supervised` transport only.
    Read-only; probes, never assumes; emits nothing."""
    reachable, sup_idx = _supervised_index(base)
    rows: dict = {}                                          # dedup key (uuid|handle) -> row
    seen_uuids: set = set()
    seen_as: set = set()
    for reg in cc.live_sessions():
        row = _row_from_channel_reg(reg, sup_idx, deep=deep)
        key = row["uuid"] or f"handle:{row['handle']}"
        rows[key] = row
        if row["uuid"]:
            seen_uuids.add(row["uuid"])
        if row["as_id"]:
            seen_as.add(row["as_id"])
    # supervised-live sessions the supervisor owns but that have no .mjs reg → add them (reach via /inject)
    for k, rec in sup_idx.items():
        uuid, as_id = rec.get("uuid"), rec.get("as_id")
        if (uuid and uuid in seen_uuids) or (as_id and as_id in seen_as):
            continue
        if k == as_id and uuid:                              # index has this rec under both keys; add once
            continue
        rows[uuid or f"as:{as_id}"] = {
            "uuid": uuid, "uuid_how": "supervisor", "handle": None, "as_id": as_id,
            "agent_id": None, "cwd": (rec.get("raw") or {}).get("cwd"),
            "description": (rec.get("raw") or {}).get("title"), "model": None,
            "kind": principals.KIND_AGENT, "state": "supervised-live", "transports": ["supervised"],
            "reachable": True, "port": None, "pid": None, "claude_pid": None, "forked_from": None,
            "reg": None, "sources": ["supervisor"],
        }
        if uuid:
            seen_uuids.add(uuid)
    return sorted(rows.values(), key=lambda r: (r.get("state") != "supervised-live", r.get("handle") or ""))


class AmbiguousTarget(cc.ChannelError):
    """A target matched more than one live session — fail loud, never message the wrong one (mirrors
    cc_channels.find's contract, one identity notion)."""


def resolve(target: str, *, base: str | None = None, registry=None, deep: bool = True) -> dict | None:
    """Resolve ANY target form to ONE PresenceRow (or None if not live and not durably known).
    target = uuid | ch-handle | as-id | agent-id | cwd | 'session://…' | 'clone://…' | unique substring.
    Fail-loud on AMBIGUOUS (>1 live match). `registry` (optional suite.get_agent_session) lets a not-live
    target still be classified as a known-but-CLOSED session vs an unknown id — a truthful negative."""
    bare = _strip_scheme(target)
    fleet = presence_all(base, deep=deep)

    # 1) exact match on any durable/near-durable key (uuid wins; then handle/as_id/agent_id/cwd)
    def _exact(r):
        return bare in (
            r.get("uuid"), r.get("handle"), r.get("as_id"), r.get("agent_id"), r.get("cwd"))
    exact = [r for r in fleet if _exact(r)]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        raise AmbiguousTarget(
            f"target {target!r} matches {len(exact)} live sessions "
            f"({[(r.get('handle'), r.get('uuid')) for r in exact]}) — address by uuid to disambiguate.")

    # 2) substring on cwd/description (the human-friendly fallback, fail-loud on ambiguity)
    sub = [r for r in fleet if bare and (bare in (r.get("cwd") or "") or bare in (r.get("description") or ""))]
    if len(sub) == 1:
        return sub[0]
    if len(sub) > 1:
        raise AmbiguousTarget(
            f"target {target!r} matched {len(sub)} live sessions by substring — address by uuid/handle.")

    # 3) not live — is it a KNOWN closed session (truthful negative) or unknown?
    if registry is not None:
        try:
            row = registry(bare)
            if row:
                return {"uuid": row.get("id") or bare, "handle": None, "as_id": None, "agent_id": None,
                        "cwd": row.get("cwd"), "description": row.get("title"), "model": None,
                        "kind": principals.KIND_AGENT, "state": "closed", "transports": [],
                        "reachable": False, "port": None, "pid": None, "claude_pid": None,
                        "forked_from": None, "reg": None, "sources": ["agent_sessions"]}
        except Exception:
            pass
    return None


_last_reconcile = [0.0]


def maybe_reconcile(chan_dir: str | None = None, min_interval: float = 180.0) -> None:
    """Throttled, NON-BLOCKING self-heal: at most once per `min_interval`, run reconcile_registry in a
    DAEMON THREAD so the caller NEVER blocks on the transcript scan. It is called from a channel post,
    which on the bridge sits on the request path — running the (multi-second) deep scan synchronously
    there would stall the server (it did: a ~19s post). Backgrounded, the post returns immediately;
    a member not-yet-backfilled simply queues on THIS post and resolves on the next (eventual). Capture
    still heals as the fabric is USED, no separate cron. Returns immediately (None)."""
    now = _time.time()
    if now - _last_reconcile[0] < min_interval:
        return None
    _last_reconcile[0] = now

    def _bg():
        try:
            reconcile_registry(chan_dir)
        except Exception:
            pass
    import threading
    threading.Thread(target=_bg, name="mu-reconcile", daemon=True).start()
    return None


if __name__ == "__main__":                                   # smoke: print the live fleet as JSON
    import sys
    fleet = presence_all()
    slim = [{k: r[k] for k in ("uuid", "handle", "as_id", "cwd", "state", "transports",
                               "reachable", "uuid_how", "kind")} for r in fleet]
    json.dump({"count": len(fleet), "fleet": slim}, sys.stdout, indent=2)
    print()
