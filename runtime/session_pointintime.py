"""runtime/session_pointintime.py — POINT-IN-TIME session launch (Session Fabric R3.3/R3.4).

THE CAPABILITY (the spec's "central, hard one"): view any past Claude Code session's life as a
navigable COMPACTION TIMELINE (R3.3), and LAUNCH/MESSAGE a session AT a chosen point — the woken
context reflecting *that* point, not the tip (R3.4). Claude Code has no native resume-at-a-point
(`--resume` restores the tip — Atlas sessions.md); this module builds the documented-buildable
path: the transcript is an append-only parentUuid DAG whose `compact_boundary` events carry their
`preservedMessages`, so the file's state at any historical moment IS a line-prefix of today's file.

THE MECHANISM (research lane 1 §G, "JSONL truncation + new-session seed", grounded in the Atlas):
  · Atlas agent-sdk/session-storage.md: "`forkSession` reads the source entries, rewrites every
    `sessionId` field and remaps message UUIDs, then appends the transformed entries under a new
    key. An adapter-level copy … would produce a transcript that still references the old session
    ID, so the SDK does not use one."  ← the NATIVE fork transform.
  · This module applies EXACTLY that transform to a PREFIX of the source transcript: cut at point
    T, rewrite sessionId everywhere, remap every event uuid (deterministic uuid5), stamp
    `forkedFrom` provenance — and write the result as a NEW session file beside the source.
    The materialized file is then resumable by the completely NATIVE `claude --resume <new-id>`
    (the supervisor's existing WAKE path) — no wrapper around anything a session does natively;
    the genuinely-new layer is only the AT-POINT materialization that Claude Code lacks.
  · WHY a full prefix (not a compact-headed partial chain): the transcript is append-only, so the
    prefix ending at T is byte-for-byte the file as it existed at moment T — a state that was
    actually resumable then. This sidesteps lane 1's open empirical question about `load()`
    accepting a partial compact-headed chain; the remaining empirical question is only whether
    resume accepts the sessionId/uuid-rewritten prefix (the native-fork transform applied to a
    prefix) — settled by the lead's live probe, NEVER asserted here.

THE LAWS THIS MODULE CARRIES:
  · READ-ONLY ON THE CATALOG (the importer's hard law, inherited): the source transcript under
    `~/.claude` is opened for READING only. Materialization writes exactly ONE NEW file per call
    (tmp + atomic rename, same directory so `--resume` finds it under the same encoded-cwd
    project dir) and REFUSES to overwrite an existing path. Nothing existing is ever modified,
    moved, truncated, or locked. `materialize_at_point` re-stats the source before and after and
    FAILS LOUD if it changed under us.
  · REGISTRY-SHAPED (spec R11 frame — everything feeds the future heart): the timeline is a
    durable RECORD (`agent_sessions/timeline/<sid>.json`, cache keyed on source bytes+mtime); a
    materialized session is a REGISTRY RECORD (`agent_sessions/<new-sid>.json`, schema-additive
    provenance fields `materialized_from` / `materialized_at_point` / `materialized_cut_uuid`)
    — both project through the existing folds, never a parallel store.
  · FAIL LOUD, TEACHING (rule 4): every refusal names what exists and how to ask correctly.
  · NO SPAWNING here: this module never launches a process. The SUPERVISOR consumes wake/consult
    intents carrying `at=` and calls materialize_at_point, then spawns through its own existing
    `--resume` path (single-actor law preserved).

POINT GRAMMAR (the `at=` mini-language — one string, mailbox-portable):
  "compact:N"   — the state EXACTLY as compaction #N left it (1-based): the boundary event, its
                  summary head (isCompactSummary), and the full re-appended preserved run.
                  (Measured on the real 41-boundary session: boundary #3's preserved run =
                  1,476 events incl. attachments, re-appended with parents rebased onto the
                  summary — the post-compact segment is self-contained in file order.)
  "uuid:<uuid>" — cut at that event's line (any event; user/assistant tips are the proven shape).
  "ts:<iso>"    — cut at the last user/assistant event at-or-before that timestamp.

Verified WITHOUT spawning claude (the lane's hard limit): structural validity of the materialized
file (every line parses · tip is T · chain walks to a root · zero stale sessionId/uuid full-field
values outside the deliberate `forkedFrom` provenance) + source-untouched proof + the supervisor
at-launch flow against the stub binary. The live "context is that-point's" probe = the lead's.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
import uuid as uuidlib
from datetime import datetime, timezone

SCHEMA_VER = 1
# Deterministic remap namespace: uuid5(NS, f"{new_sid}:{old_uuid}") — re-materializing with the
# same new_sid reproduces the identical file (verifiable, idempotent-by-content).
_REMAP_NS = uuidlib.uuid5(uuidlib.NAMESPACE_URL, "company://session-pointintime/remap")
_UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")

POINT_KINDS = ("compact", "uuid", "ts")


class PointError(ValueError):
    """A teaching refusal about a point spec or its resolution — never a bare stack trace."""


# ───────────────────────────── point grammar ─────────────────────────────

def parse_point(at: str) -> dict:
    """'compact:3' | 'uuid:<uuid>' | 'ts:<iso8601>' → {kind, …}. Teaching-loud on anything else."""
    if not isinstance(at, str) or not at.strip():
        raise PointError(
            "point is empty — pass at='compact:N' (the state as compaction #N left it; the "
            "timeline lists N), at='uuid:<event-uuid>' (cut at that event), or "
            "at='ts:<iso-timestamp>' (cut at the last message at-or-before that moment).")
    s = at.strip()
    kind, sep, val = s.partition(":")
    if not sep or kind not in POINT_KINDS:
        raise PointError(
            f"unparseable point {at!r} — the grammar is one of: 'compact:N' · 'uuid:<uuid>' · "
            f"'ts:<iso-timestamp>'. sessions(op='timeline', session=…) shows a session's points.")
    val = val.strip()
    if kind == "compact":
        try:
            n = int(val)
        except ValueError:
            raise PointError(f"'compact:{val}' — N must be an integer ≥ 1 (1-based boundary number; "
                             f"the timeline shows how many exist).")
        if n < 1:
            raise PointError(f"'compact:{n}' — boundary numbers are 1-based (compact:1 is the first).")
        return {"kind": "compact", "n": n, "at": s}
    if kind == "uuid":
        if not _UUID_RE.match(val):
            raise PointError(f"'uuid:{val}' — not a uuid. Pass an event uuid from the transcript "
                             f"(the timeline's resume_cut_uuid values are launchable points).")
        return {"kind": "uuid", "uuid": val.lower(), "at": s}
    # ts
    try:
        ts = datetime.fromisoformat(val.replace("Z", "+00:00"))
    except ValueError:
        raise PointError(f"'ts:{val}' — not ISO-8601 (e.g. ts:2026-05-26T11:02:42Z).")
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return {"kind": "ts", "ts": ts.isoformat(), "at": s}


# ───────────────────────────── streaming scan ─────────────────────────────

def _iter_jsonl(path: str):
    """Yield (line_no, obj | None) for every line — bad json yields None (tolerated-and-counted
    by callers: a 4,500-file historical corpus contains torn tails; importer precedent)."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh):
            line = line.strip()
            if not line:
                yield i, None
                continue
            try:
                yield i, json.loads(line)
            except ValueError:
                yield i, None


def build_timeline(jsonl_path: str) -> dict:
    """R3.3 — ONE streaming pass over the transcript → the navigable compaction timeline.

    Per boundary: {n, line, uuid, ts, trigger, pre_tokens, post_tokens, messages_summarized,
    preserved_count, resume_cut_line, resume_cut_uuid, point} where resume_cut_* marks the END of
    the boundary's post-compact head — the exact line "the session as compaction #N left it"
    truncates at (the launchable point). Segments between boundaries carry turn counts + time
    spans so the operator sees WHERE along the session's life each point sits.

    MEASURED REALITY (the real 41-boundary-line session, 2026-06-12 inspection — the indexer is
    built against these observed shapes, not the docs' idealization):
      · The summary head (`isCompactSummary`, parent = the boundary uuid) ALWAYS follows the
        boundary; it always extends the cut.
      · Some CC eras RE-APPEND the preserved window after the summary (boundary at line 0/2095:
        1,476-event runs, original uuids + timestamps kept); later eras re-append only a short
        tail or nothing (boundary 9add968e: 4 events; eee33789: none) — the preserved list mostly
        REFERENCES pre-boundary lines. The cut tracker handles both: it extends while lines are
        verifiably the boundary's payload and closes at the first genuinely-new turn.
      · A compaction's re-appended window can CONTAIN A COPY of an earlier compact_boundary event
        (same uuid — line 2096 is a byte-copy of line 0, riding inside boundary 4b4b756a's
        preserved run). Such copies are PAYLOAD, not new compactions: deduped by uuid +
        in-active-preserved-set, never a timeline entry of their own."""
    if not os.path.exists(jsonl_path):
        raise PointError(f"transcript not found: {jsonl_path} — the registry record's jsonl_path "
                         f"is stale, or the session lives under another project dir.")
    st = os.stat(jsonl_path)
    boundaries: list[dict] = []
    segments: list[dict] = []
    seg = {"n": 0, "from_line": 0, "user_msgs": 0, "assistant_msgs": 0,
           "first_ts": None, "last_ts": None}
    active: dict | None = None        # the open boundary's post-compact-head tracker
    seen_boundary_uuids: set[str] = set()
    started = ended = None
    events_total = bad_lines = lines_total = 0
    user_total = assistant_total = 0

    def _close_segment(end_line: int):
        seg["to_line"] = end_line
        segments.append(dict(seg))

    for i, ev in _iter_jsonl(jsonl_path):
        lines_total = i + 1
        if ev is None:
            bad_lines += 1
            continue
        events_total += 1
        ts = ev.get("timestamp")
        if isinstance(ts, str):
            started = started or ts
            ended = ts
            seg["first_ts"] = seg["first_ts"] or ts
            seg["last_ts"] = ts
        et = ev.get("type")
        u = ev.get("uuid")
        if et == "user" and isinstance(ev.get("message"), dict):
            user_total += 1
            seg["user_msgs"] += 1
        elif et == "assistant" and isinstance(ev.get("message"), dict):
            assistant_total += 1
            seg["assistant_msgs"] += 1
        is_boundary = et == "system" and ev.get("subtype") == "compact_boundary"
        is_payload_copy = is_boundary and isinstance(u, str) and (
            u in seen_boundary_uuids
            or (active is not None and u in active["preserved"]))
        if active is not None and isinstance(u, str):
            if ev.get("isCompactSummary") is True and ev.get("parentUuid") == active["b"]["uuid"]:
                # the summary head ALWAYS extends the cut (measured: not always in the preserved list)
                active["b"]["resume_cut_line"] = i
                active["b"]["resume_cut_uuid"] = u
            elif u in active["preserved"]:
                active["b"]["resume_cut_line"] = i
                active["b"]["resume_cut_uuid"] = u
            elif (et in ("user", "assistant") and ev.get("isCompactSummary") is not True
                  and not is_payload_copy):
                active = None          # the first genuinely-new turn closes the post-compact head
        if is_boundary and not is_payload_copy:
            cm = ev.get("compactMetadata") or {}
            pm = cm.get("preservedMessages") or {}
            preserved = set(x for x in (pm.get("uuids") or []) if isinstance(x, str))
            anchor = pm.get("anchorUuid")
            if isinstance(anchor, str):
                preserved.add(anchor)
            if isinstance(u, str):
                seen_boundary_uuids.add(u)
            b = {"n": len(boundaries) + 1, "line": i, "uuid": u, "ts": ts,
                 "trigger": cm.get("trigger"), "pre_tokens": cm.get("preTokens"),
                 "post_tokens": cm.get("postTokens"),
                 "messages_summarized": cm.get("messagesSummarized"),
                 "preserved_count": len(preserved),
                 # fallback: a boundary with no post-compact head cuts at the boundary line itself
                 "resume_cut_line": i, "resume_cut_uuid": u,
                 "point": f"compact:{len(boundaries) + 1}"}
            boundaries.append(b)
            active = {"b": b, "preserved": preserved}
            _close_segment(i)
            seg = {"n": len(boundaries), "from_line": i, "user_msgs": 0, "assistant_msgs": 0,
                   "first_ts": ts, "last_ts": ts}
    _close_segment(lines_total)

    return {"schema_ver": SCHEMA_VER, "jsonl_path": os.path.abspath(jsonl_path),
            "source_bytes": st.st_size, "source_mtime": st.st_mtime,
            "built_at": datetime.now(timezone.utc).isoformat(),
            "lines_total": lines_total, "events_total": events_total, "bad_lines": bad_lines,
            "started": started, "ended": ended,
            "user_msgs": user_total, "assistant_msgs": assistant_total,
            "boundaries": boundaries, "segments": segments}


def resolve_cut(jsonl_path: str, point: dict, timeline: dict | None = None) -> dict:
    """A parsed point → {cut_line, cut_uuid, cut_ts} on this transcript. Teaching-loud misses."""
    tl = timeline or build_timeline(jsonl_path)
    if point["kind"] == "compact":
        n = point["n"]
        bs = tl["boundaries"]
        if n > len(bs):
            raise PointError(
                f"compact:{n} — this session has {len(bs)} compaction boundar"
                f"{'y' if len(bs) == 1 else 'ies'} (1..{len(bs)}). "
                f"sessions(op='timeline') shows them with timestamps.")
        b = bs[n - 1]
        return {"cut_line": b["resume_cut_line"], "cut_uuid": b["resume_cut_uuid"],
                "cut_ts": b["ts"], "boundary": b}
    if point["kind"] == "uuid":
        want = point["uuid"]
        for i, ev in _iter_jsonl(jsonl_path):
            if ev is not None and isinstance(ev.get("uuid"), str) and ev["uuid"].lower() == want:
                return {"cut_line": i, "cut_uuid": ev["uuid"], "cut_ts": ev.get("timestamp"),
                        "event_type": ev.get("type")}
        raise PointError(f"uuid:{want} — no event with that uuid in {os.path.basename(jsonl_path)}. "
                         f"The timeline's resume_cut_uuid values are known-good points.")
    # ts — the LAST user/assistant message event at-or-before the moment
    want = datetime.fromisoformat(point["ts"])
    best = None
    for i, ev in _iter_jsonl(jsonl_path):
        if ev is None or ev.get("type") not in ("user", "assistant"):
            continue
        ts = ev.get("timestamp")
        if not (isinstance(ts, str) and isinstance(ev.get("uuid"), str)):
            continue
        try:
            evt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except ValueError:
            continue
        if evt.tzinfo is None:
            evt = evt.replace(tzinfo=timezone.utc)
        if evt <= want:
            best = {"cut_line": i, "cut_uuid": ev["uuid"], "cut_ts": ts,
                    "event_type": ev.get("type")}
    if best is None:
        raise PointError(f"ts:{point['ts']} — no user/assistant message at or before that moment "
                         f"(session starts {tl.get('started')}).")
    return best


# ───────────────────────────── materialization ─────────────────────────────

def _remap_value(obj, mapping: dict):
    """Walk a decoded event; replace any string field whose ENTIRE value is in `mapping` (the
    native-fork transform: every sessionId field rewritten + message uuids remapped — full-field
    matches only, so a uuid quoted inside conversation PROSE is never mutated; fidelity holds)."""
    if isinstance(obj, dict):
        return {k: _remap_value(v, mapping) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_remap_value(v, mapping) for v in obj]
    if isinstance(obj, str):
        return mapping.get(obj, obj)
    return obj


def materialize_at_point(jsonl_path: str, at: str, *, dest_dir: str | None = None,
                         new_sid: str | None = None, source_sid: str | None = None) -> dict:
    """R3.4 — write the point-in-time session file: the source transcript's PREFIX at point T,
    carried through the native-fork transform (sessionId rewrite + uuid remap + forkedFrom
    provenance), as ONE NEW file the stock `claude --resume <new-sid>` can launch.

    Returns the materialization report (new_sid, new_path, cut, counts, source-untouched proof).
    Raises PointError (teaching) on any refusal. NEVER touches the source; NEVER overwrites."""
    point = parse_point(at)
    if not os.path.exists(jsonl_path):
        raise PointError(f"transcript not found: {jsonl_path}")
    src_stat_before = os.stat(jsonl_path)
    src_sid = source_sid or os.path.splitext(os.path.basename(jsonl_path))[0]
    if not _UUID_RE.match(src_sid):
        # a non-uuid filename (test fixtures) — fall back to the first event's sessionId
        for _, ev in _iter_jsonl(jsonl_path):
            if ev is not None and isinstance(ev.get("sessionId"), str):
                src_sid = ev["sessionId"]
                break
    nsid = new_sid or str(uuidlib.uuid4())
    cut = resolve_cut(jsonl_path, point)
    cut_line = cut["cut_line"]

    # pass 1 — collect every event uuid in the prefix → the deterministic remap
    mapping: dict[str, str] = {src_sid: nsid}
    for i, ev in _iter_jsonl(jsonl_path):
        if i > cut_line:
            break
        if ev is not None and isinstance(ev.get("uuid"), str):
            mapping[ev["uuid"]] = str(uuidlib.uuid5(_REMAP_NS, f"{nsid}:{ev['uuid']}"))

    out_dir = dest_dir or os.path.dirname(os.path.abspath(jsonl_path))
    os.makedirs(out_dir, exist_ok=True)
    new_path = os.path.join(out_dir, f"{nsid}.jsonl")
    if os.path.exists(new_path):
        raise PointError(f"refusing to overwrite {new_path} — a materialized session file already "
                         f"exists there. Pass a fresh new_sid (or none, for a random one).")

    fork_stamp = {"sessionId": src_sid, "messageUuid": cut["cut_uuid"]}
    lines_written = bad_kept = 0
    fd, tmp_path = tempfile.mkstemp(prefix=f".{nsid}.", suffix=".jsonl.tmp", dir=out_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out, \
                open(jsonl_path, "r", encoding="utf-8", errors="replace") as src:
            for i, raw in enumerate(src):
                if i > cut_line:
                    break
                s = raw.strip()
                if not s:
                    continue
                try:
                    ev = json.loads(s)
                except ValueError:
                    bad_kept += 1          # a torn line inside the prefix — kept verbatim, counted loud
                    out.write(raw if raw.endswith("\n") else raw + "\n")
                    lines_written += 1
                    continue
                ev = _remap_value(ev, mapping)
                if isinstance(ev, dict) and ev.get("type"):
                    ev["forkedFrom"] = dict(fork_stamp)   # provenance: the native fork's stamp shape
                out.write(json.dumps(ev, ensure_ascii=False, separators=(",", ":")) + "\n")
                lines_written += 1
        os.replace(tmp_path, new_path)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

    src_stat_after = os.stat(jsonl_path)
    source_untouched = (src_stat_before.st_size == src_stat_after.st_size
                        and src_stat_before.st_mtime_ns == src_stat_after.st_mtime_ns)
    if not source_untouched:
        raise PointError(
            f"SOURCE CHANGED DURING MATERIALIZATION: {jsonl_path} moved "
            f"{src_stat_before.st_size}→{src_stat_after.st_size} bytes. The materialized prefix "
            f"({new_path}) may straddle a torn write — re-run when the session is quiet. "
            f"(A LIVE session's file grows; point-in-time launch of a live session is racy by "
            f"nature — the file was NOT corrupted, only our copy's cut is suspect.)")

    return {"schema_ver": SCHEMA_VER, "at": point["at"], "point": point,
            "source_sid": src_sid, "source_path": os.path.abspath(jsonl_path),
            "new_sid": nsid, "new_path": new_path,
            "cut_line": cut_line, "cut_uuid": cut["cut_uuid"],
            "cut_uuid_new": mapping.get(cut["cut_uuid"]), "cut_ts": cut.get("cut_ts"),
            "lines_written": lines_written, "uuids_remapped": len(mapping) - 1,
            "bad_lines_kept": bad_kept,
            "source_untouched": source_untouched,
            "source_bytes": src_stat_before.st_size,
            "materialized_at": datetime.now(timezone.utc).isoformat()}


def verify_materialized(report: dict) -> dict:
    """The structural proof (everything provable WITHOUT spawning claude): every line parses ·
    the tip is the remapped cut event · the parentUuid chain walks from the tip to an in-file
    root · NO full-field value anywhere still equals the source sid or an old prefix uuid,
    EXCEPT the deliberate forkedFrom provenance. Returns {ok, checks:{…}, problems:[…]}."""
    new_path, src_sid = report["new_path"], report["source_sid"]
    cut_uuid_old, cut_uuid_new = report["cut_uuid"], report["cut_uuid_new"]
    problems: list[str] = []
    occurrences: dict[str, list[int]] = {}     # uuid → line_nos (re-appends DUPLICATE uuids)
    by_line: dict[int, tuple[str, str | None]] = {}   # line → (uuid, parentUuid)
    last_event_uuid = None
    last_event_line = -1
    n_lines = 0
    old_prefix_uuids: set[str] = set()
    # rebuild the old-uuid set deterministically from the new file's own uuids is impossible —
    # instead re-scan the SOURCE prefix (read-only) for the stale-value sweep.
    for i, ev in _iter_jsonl(report["source_path"]):
        if i > report["cut_line"]:
            break
        if ev is not None and isinstance(ev.get("uuid"), str):
            old_prefix_uuids.add(ev["uuid"])

    def _stale_sweep(obj, path="") -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                if path == "" and k == "forkedFrom":
                    continue                      # the deliberate provenance exception
                _stale_sweep(v, f"{path}.{k}" if path else k)
        elif isinstance(obj, list):
            for j, v in enumerate(obj):
                _stale_sweep(v, f"{path}[{j}]")
        elif isinstance(obj, str):
            if obj == src_sid:
                problems.append(f"stale source sessionId at {path}")
            elif obj in old_prefix_uuids:
                problems.append(f"stale pre-remap uuid {obj[:8]}… at {path}")

    for i, ev in _iter_jsonl(new_path):
        n_lines = i + 1
        if ev is None:
            continue                              # bad_lines_kept are declared in the report
        _stale_sweep(ev)
        u = ev.get("uuid")
        if isinstance(u, str):
            occurrences.setdefault(u, []).append(i)
            by_line[i] = (u, ev.get("parentUuid"))
            last_event_uuid, last_event_line = u, i
    checks = {
        "line_count_matches": n_lines == report["lines_written"],
        "tip_is_cut_event": last_event_uuid == cut_uuid_new,
        "no_stale_identifiers": not problems,
    }
    # chain walk: tip → root, APPEND-ORDER resolution — a parent uuid resolves to its LATEST
    # occurrence BEFORE the child's line (re-appended preserved runs DUPLICATE uuids with rebased
    # parents, so a same-line-set uuid→parent map is a graph with cycles; the historical, line-
    # ordered reading is a strictly-decreasing walk — guaranteed termination, mirrors how the
    # append-only file actually accreted).
    hops, cur_line = 0, last_event_line
    while cur_line >= 0:
        u, parent = by_line[cur_line]
        if parent is None:
            cur_line = -1                         # an explicit root — done
            break
        prev = [ln for ln in occurrences.get(parent, []) if ln < cur_line]
        if not prev:
            problems.append(f"chain breaks at line {cur_line} ({u[:8]}…) — parent "
                            f"{str(parent)[:8]}… has no earlier occurrence in the file")
            break
        cur_line = prev[-1]
        hops += 1
    checks["chain_walks_to_root"] = cur_line == -1
    checks["chain_hops"] = hops
    ok = all(v for k, v in checks.items() if isinstance(v, bool))
    return {"ok": ok, "checks": checks, "problems": problems[:20],
            "problems_total": len(problems), "tip_uuid": last_event_uuid,
            "cut_uuid_old": cut_uuid_old}


def materialized_registry_record(report: dict, source_record: dict | None = None,
                                 *, registered_by: str = "") -> dict:
    """The registry record for a materialized session (schema-additive on the importer's shape —
    registry-is-truth; the provenance fields are how the future heart sees point-launches)."""
    src = source_record or {}
    new_path = report["new_path"]
    st = os.stat(new_path)
    title_src = src.get("title") or report["source_sid"][:8]
    return {"id": report["new_sid"], "name": None, "cwd": src.get("cwd"),
            "state": "closed",                    # wake-able; never live until the supervisor spawns it
            "started": src.get("started"), "last_activity": report.get("cut_ts"),
            "title": f"@{report['at']} · {title_src}"[:140],
            "title_source": "materialized",
            "project": src.get("project"), "jsonl_path": new_path,
            "jsonl_bytes": st.st_size, "jsonl_mtime": st.st_mtime,
            "materialized_from": report["source_sid"],
            "materialized_at_point": report["at"],
            "materialized_cut_uuid": report["cut_uuid"],
            "materialized_by": registered_by or None,
            "imported_at": report["materialized_at"], "schema_ver": SCHEMA_VER}
