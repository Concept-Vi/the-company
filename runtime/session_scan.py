"""runtime/session_scan.py — the programmatic session SCAN (vision §1.6: "build this process into
the tools").  ONE streaming pass over a Claude Code transcript → projectable DATA:

  • rows  (ndjson)  — one row PER EVENT, the schema in channel-memory/schema/session-store-grammar.md §6.
  • summary (json)  — totals, attribution split, model + system-subtype distributions, the boundary
                      timeline (reused from session_pointintime.build_timeline so counts are CONSISTENT),
                      the forkedFrom inherited/own partition, the biggest messages, the largest
                      time-gaps (Tim's away/sleep signal), and the dense-message profile.

DATA, not prose (COMMIT-GRAMMAR §4) — so the Company UI PROJECTS it (the Heart) rather than re-builds it.
Read-only: never writes to or mutates the source transcript.

Boundary/attribution detection is STRUCTURAL, never text (the vault's core law): a compaction is a
`system`/`compact_boundary` event or an `isCompactSummary==true` head — NOT a "continued from…" string
(which is a false positive inside tool-result content).  forkedFrom is the real per-event provenance
field, not an inference.

CLI:  python3 -m runtime.session_scan <transcript.jsonl> [--out-dir DIR] [--rows/--no-rows]
API:  scan_session(path) -> {"summary":{…}, "rows":[…]} ;  write_scan(path, out_dir) -> {paths…}
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

from runtime.session_pointintime import build_timeline, _iter_jsonl   # reuse — one source of truth

SCAN_VER = "scan-1"

PROJECTS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "projects")


class AmbiguousSelfError(RuntimeError):
    """resolve_own_session cannot safely identify SELF (ambiguous + no COMPANY_SESSION_ID) — raised
    TEACHING-loud rather than silently mis-identify self (the self-serve-memory safety keystone)."""


def _encode_cwd(cwd: str) -> str:
    """Encode a cwd to its project-dir name: '/' and '.' → '-' (verified against the live store)."""
    return cwd.replace("/", "-").replace(".", "-")


SELF_MARKER_DIR = os.path.join(os.environ.get("RECOLLECTION_CONFIG_DIR") or os.path.expanduser("~/company/.recollection"), "self")


def _claude_ancestor_pid(pid: int | None = None) -> int | None:
    """Walk /proc from `pid` (default: this process) to the `claude` SESSION process — the SESSION-UNIQUE
    disambiguator (#69). Each live session IS one claude process; the company MCP server + the SessionStart
    hook are both its children, so both resolve to the SAME claude PID → a shared, cwd-independent key
    (cwd alone COLLIDES — 3 sessions share /home/tim). Robust match: comm=='claude' OR the cmdline names
    the claude binary OR comm is a version-string (claude sets comm to its version, e.g. '2.1.175').
    Returns None on no-claude-ancestor (an ORPHANED session whose claude exited → degrade to the
    ambiguous-raise, NEVER a wrong self). Best-effort: any /proc error → None (Linux-only; degrade-clean)."""
    import re
    pid = pid or os.getpid()
    try:
        for _ in range(40):                                    # bounded walk (no infinite loop on a cycle)
            if not pid or pid <= 1:
                return None
            with open(f"/proc/{pid}/stat") as f:
                parts = f.read().split()
            comm = parts[1].strip("()"); ppid = int(parts[3])
            try:                                               # argv0 BASENAME — the executable, not a loose
                argv0 = open(f"/proc/{pid}/cmdline").read().split("\0")[0]   # substring (a /claude path
            except OSError:                                    # ANYWHERE in argv would mis-match → mis-id self,
                argv0 = ""                                     # the silent-corruption hazard the gate guards)
            if comm == "claude" or os.path.basename(argv0) == "claude" \
               or re.match(r"^\d+\.\d+\.\d+$", comm):          # claude sometimes sets comm to its version
                return pid
            pid = ppid
    except (OSError, ValueError, IndexError):
        return None
    return None


def _self_marker(proj: str) -> dict | None:
    """#69 — the SessionStart-hook self-marker read: resolve THIS session via its claude-ancestor PID.
    The hook (a child of claude) writes ~/company/.recollection/self/<claude-pid>.json = {session_id, ...}; the
    resolver (also a child of the same claude) walks to that PID + reads it. Returns the marker dict IF
    its session_id has a transcript in `proj` (the cwd cross-check — belt+braces against a stale/wrong-cwd
    marker), else None (degrade-clean — falls through to the newest-mtime/ambiguous path)."""
    cp = _claude_ancestor_pid()
    if cp is None:
        return None

    def _locate(sid):
        """The sid's transcript, found ANYWHERE under PROJECTS_DIR — not only in the passed `proj`. The
        marker/registration is keyed by the session-unique, compaction-stable claude_pid, so the sid is
        already a trustworthy self-id; requiring it in the PASSED proj was an over-tight check that broke
        a disoriented session resolving from a cwd ≠ its launch cwd (the live bug, 2026-06-18). Validating
        the transcript EXISTS (anywhere) still rejects a stale/recycled-pid marker, and returns the REAL
        project_dir so the caller gets the right path regardless of its cwd. Returns (path, project_dir)
        or (None, None)."""
        if not sid:
            return None, None
        direct = os.path.join(proj, f"{sid}.jsonl")            # fast path: the common (correct-cwd) case
        if os.path.exists(direct):
            return direct, proj
        import glob as _g
        for p in _g.glob(os.path.join(PROJECTS_DIR, "*", f"{sid}.jsonl")):
            return p, os.path.dirname(p)
        return None, None

    # 1) THE FABRIC REGISTRATION (the ONE store — fold-home): the .mjs announce wrote claude_pid; the
    #    SessionStart hook populated session_id. Scan .data/channels/*.json for THIS claude_pid. This is
    #    the home; the marker (below) is the proven fallback kept until this path is verified (caution #2).
    try:
        regdir = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".data", "channels")
        for fn in os.listdir(regdir):
            if not fn.endswith(".json") or fn.startswith("_"):
                continue
            try:
                r = json.load(open(os.path.join(regdir, fn)))
            except (OSError, ValueError):
                continue
            if r.get("claude_pid") == cp:
                _p, _pd = _locate(r.get("session_id"))
                if _p:
                    return {"session_id": r["session_id"], "how": "fabric-registration (#69 claude_pid)",
                            "path": _p, "project_dir": _pd}
    except OSError:
        pass

    # 2) THE MARKER (the proven fallback — kept until the registration path is verified)
    try:
        m = json.load(open(os.path.join(SELF_MARKER_DIR, f"{cp}.json")))
    except (OSError, ValueError):
        return None
    _p, _pd = _locate(m.get("session_id"))
    if _p:
        return {"session_id": m["session_id"], "how": "claude-pid marker", "path": _p, "project_dir": _pd}
    return None


def resolve_own_session(cwd: str | None = None, session_id: str | None = None,
                        *, allow_ambiguous: bool = False) -> dict:
    """Let ANY session find ITS OWN transcript UNAMBIGUOUSLY (the self-serve-memory keystone — Tim:
    "other sessions can scan their own sessions and spawn previous versions"). Resolution order:
      1. explicit session_id (most reliable)
      2. env COMPANY_SESSION_ID — THE unambiguous self-id (a launcher/SessionStart-hook injects it; the
         injection is the launch-infra seam, the resolver is the safe consumer)
      3. the NEWEST .jsonl in the cwd's project dir — ONLY when there is exactly one (truly unambiguous).

    ★ FAIL-LOUD ON AMBIGUITY (the safety keystone): if there's no explicit/env sid AND the project dir
    holds MULTIPLE .jsonl, this RAISES rather than silently returning a newest-mtime GUESS — because for
    self-serve memory, mis-identifying "self" means recalling/cloning the WRONG session as yourself
    (corrupting). The teaching error names COMPANY_SESSION_ID as the fix. `allow_ambiguous=True` opts back
    into the best-guess (newest-mtime) for callers who genuinely accept the risk — never the default.
    Returns {path, session_id, project_dir, cwd, how, ambiguous}; raises on no-dir/no-jsonl/ambiguous."""
    cwd = cwd or os.getcwd()
    proj = os.path.join(PROJECTS_DIR, _encode_cwd(os.path.abspath(cwd)))
    sid = session_id or os.environ.get("COMPANY_SESSION_ID")
    if sid:
        path = os.path.join(proj, f"{sid}.jsonl")
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"resolve_own_session: session_id {sid!r} given but no transcript at {path} — wrong cwd "
                f"(this session's project dir encodes from its cwd) or wrong sid.")
        return {"path": path, "session_id": sid, "project_dir": proj, "cwd": cwd,
                "how": "explicit" if session_id else "env COMPANY_SESSION_ID", "ambiguous": False}
    # 2.5 — #69 SELF-MARKER: the SessionStart hook wrote this session's id keyed by its claude-ancestor
    # PID (session-unique, cwd-independent). The unambiguous self-id for a top-level session with no
    # COMPANY_SESSION_ID env — disambiguates MULTIPLE same-cwd sessions (the cwd-key collision). Degrade-
    # clean: no marker / orphaned session → fall through to the newest-mtime/ambiguous-raise below.
    _m = _self_marker(proj)
    if _m:
        # use the marker's REAL location (it may differ from the passed-cwd proj — a disoriented session
        # resolving from a different cwd still gets its right transcript; claude_pid is the true self-id).
        _pd = _m.get("project_dir", proj)
        return {"path": _m.get("path", os.path.join(_pd, f"{_m['session_id']}.jsonl")),
                "session_id": _m["session_id"], "project_dir": _pd,
                "cwd": cwd, "how": _m.get("how", "claude-pid self-marker (#69)"), "ambiguous": False}
    if not os.path.isdir(proj):
        raise FileNotFoundError(
            f"resolve_own_session: no project dir {proj} for cwd {cwd} — a session's transcript lives "
            f"under ~/.claude/projects/<encoded-cwd>/. Pass session_id, or check the cwd.")
    jsonls = [f for f in os.listdir(proj) if f.endswith(".jsonl")]
    if not jsonls:
        raise FileNotFoundError(f"resolve_own_session: no .jsonl transcripts in {proj}.")
    ranked = sorted(jsonls, key=lambda f: os.stat(os.path.join(proj, f)).st_mtime_ns, reverse=True)
    newest = ranked[0]
    if len(jsonls) > 1 and not allow_ambiguous:
        # ★ AMBIGUOUS + no unambiguous self-id → FAIL LOUD (no silent self-misidentification)
        raise AmbiguousSelfError(
            f"resolve_own_session: {len(jsonls)} transcripts in {proj} and no COMPANY_SESSION_ID/explicit "
            f"sid — cannot safely identify SELF (newest-mtime would GUESS {os.path.splitext(newest)[0]!r}, "
            f"which could be another live session → recalling/cloning the WRONG self). FIX: inject "
            f"COMPANY_SESSION_ID=<this session's id> at launch (the unambiguous self-id), or pass "
            f"session_id=, or allow_ambiguous=True to accept the newest-mtime guess. Fail loud, never "
            f"silently mis-identify self.")
    return {"path": os.path.join(proj, newest), "session_id": os.path.splitext(newest)[0],
            "project_dir": proj, "cwd": cwd,
            "how": "newest-mtime (sole transcript)" if len(jsonls) == 1 else "newest-mtime (AMBIGUOUS guess — allow_ambiguous)",
            "ambiguous": len(jsonls) > 1}


# ───────────────────────── helpers (all structural) ─────────────────────────

def _content_text_len(msg: dict) -> int:
    """Byte-length of the rendered message content (string OR the concatenated text/parts of a list)."""
    if not isinstance(msg, dict):
        return 0
    c = msg.get("content")
    if isinstance(c, str):
        return len(c.encode("utf-8", "replace"))
    if isinstance(c, list):
        total = 0
        for part in c:
            if isinstance(part, dict):
                # text part, tool_use input, or tool_result content — count whatever carries text
                for k in ("text", "content", "input"):
                    v = part.get(k)
                    if isinstance(v, str):
                        total += len(v.encode("utf-8", "replace"))
                    elif v is not None:
                        total += len(json.dumps(v, ensure_ascii=False).encode("utf-8", "replace"))
            elif isinstance(part, str):
                total += len(part.encode("utf-8", "replace"))
        return total
    return 0


def _attribution(ev: dict) -> str:
    """WHO produced this event — structural, never guessed from content.
       assistant·<synthetic> → 'synthetic'; assistant → 'assistant'; user+toolUseResult → 'tool';
       user whose content opens with a <channel wrapper → 'channel'; other user → 'user' (the human);
       system → 'system'; else → the type."""
    et = ev.get("type")
    msg = ev.get("message") if isinstance(ev.get("message"), dict) else {}
    if et == "assistant":
        return "synthetic" if msg.get("model") == "<synthetic>" else "assistant"
    if et == "user":
        if ev.get("isCompactSummary") is True:
            return "compaction"          # a system-generated summary head, NOT a human turn
        if ev.get("toolUseResult") is not None:
            return "tool"
        c = msg.get("content")
        head = c if isinstance(c, str) else (c[0].get("text", "") if isinstance(c, list) and c and isinstance(c[0], dict) else "")
        head = head.lstrip() if isinstance(head, str) else ""
        if head.startswith("<channel "):
            return "channel"
        # injected user-events (NOT human turns): skill activations, slash-commands, background
        # task-notifications, and any isMeta meta-injection. STRUCTURAL filter — content text lies
        # (these are type:user with no toolUseResult), so we discriminate on isMeta + known prefixes.
        if ev.get("isMeta") is True or head.startswith((
                "<task-notification", "<command", "<local-command",
                "Base directory for this skill", "<persisted-output", "<user-prompt-submit")):
            return "inject"
        return "user"                    # a genuine human-typed turn (Tim)
    if et == "system":
        return "system"
    return et or "unknown"


def _usage_tokens(msg: dict) -> dict:
    u = msg.get("usage") if isinstance(msg, dict) else None
    if not isinstance(u, dict):
        return {"in": 0, "out": 0, "cache_read": 0, "cache_creation": 0}
    return {"in": u.get("input_tokens") or 0, "out": u.get("output_tokens") or 0,
            "cache_read": u.get("cache_read_input_tokens") or 0,
            "cache_creation": u.get("cache_creation_input_tokens") or 0}


def _iso_to_epoch(ts) -> float | None:
    if not isinstance(ts, str):
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


# ───────────────────────────── the scan ─────────────────────────────

def scan_session(jsonl_path: str) -> dict:
    """ONE pass → {summary, rows}.  Reuses build_timeline for the boundary/segment timeline so the
    scan and the clone-at-point machinery agree on what a boundary IS."""
    if not os.path.exists(jsonl_path):
        raise FileNotFoundError(f"transcript not found: {jsonl_path}")
    st = os.stat(jsonl_path)
    timeline = build_timeline(jsonl_path)
    boundary_lines = {b["line"]: b for b in timeline["boundaries"]}

    rows: list[dict] = []
    by_type: dict[str, int] = {}
    by_attr: dict[str, int] = {}
    by_model: dict[str, int] = {}
    by_subtype: dict[str, int] = {}
    tokens_by_model: dict[str, dict] = {}
    tot = {"in": 0, "out": 0, "cache_read": 0, "cache_creation": 0}
    ff_inherited = ff_own = 0
    ff_parents: dict[str, int] = {}
    user_bytes: list[tuple] = []        # (bytes, line, ts) for human turns — the dense-message profile
    asst_bytes: list[tuple] = []
    gaps: list[tuple] = []              # (gap_sec, line, ts)
    prev_epoch = None
    first_ts = last_ts = None

    for i, ev in _iter_jsonl(jsonl_path):
        if ev is None or not isinstance(ev, dict) or not ev.get("type"):
            continue
        et = ev.get("type")
        msg = ev.get("message") if isinstance(ev.get("message"), dict) else {}
        ts = ev.get("timestamp")
        attr = _attribution(ev)
        toks = _usage_tokens(msg)
        cbytes = _content_text_len(msg)
        model = msg.get("model")
        subtype = ev.get("subtype")
        ff = ev.get("forkedFrom") if isinstance(ev.get("forkedFrom"), dict) else None
        is_boundary = (et == "system" and subtype == "compact_boundary") or ev.get("isCompactSummary") is True

        ep = _iso_to_epoch(ts)
        gap = (ep - prev_epoch) if (ep is not None and prev_epoch is not None) else None
        if ep is not None:
            prev_epoch = ep
            first_ts = first_ts or ts
            last_ts = ts

        # tallies
        by_type[et] = by_type.get(et, 0) + 1
        by_attr[attr] = by_attr.get(attr, 0) + 1
        if et == "system" and subtype:
            by_subtype[subtype] = by_subtype.get(subtype, 0) + 1
        if et == "assistant":
            m = model or "none"
            by_model[m] = by_model.get(m, 0) + 1
            tm = tokens_by_model.setdefault(m, {"in": 0, "out": 0})
            tm["in"] += toks["in"]; tm["out"] += toks["out"]
            for k in tot:
                tot[k] += toks[k]
            if cbytes:
                asst_bytes.append((cbytes, i, ts))
        if attr == "user" and cbytes:
            user_bytes.append((cbytes, i, ts))
        if ff:
            ff_inherited += 1
            ps = ff.get("sessionId") or "?"
            ff_parents[ps] = ff_parents.get(ps, 0) + 1
        elif et in ("user", "assistant"):
            ff_own += 1
        if gap is not None and gap > 0:
            gaps.append((round(gap, 1), i, ts))

        rows.append({
            "line": i, "uuid": ev.get("uuid"), "parent": ev.get("parentUuid"), "ts": ts,
            "type": et, "role": msg.get("role"), "attr": attr, "model": model,
            "in_tok": toks["in"], "out_tok": toks["out"],
            "cache_read_tok": toks["cache_read"], "cache_creation_tok": toks["cache_creation"],
            "bytes": cbytes, "is_tool_result": ev.get("toolUseResult") is not None,
            "is_boundary": is_boundary, "boundary_point": boundary_lines.get(i, {}).get("point"),
            "subtype": subtype if et == "system" else None,
            "forked_from": ff.get("sessionId") if ff else None,
        })

    user_bytes.sort(reverse=True); asst_bytes.sort(reverse=True); gaps.sort(reverse=True)
    n_user = by_attr.get("user", 0)
    summary = {
        "scan_ver": SCAN_VER, "source_path": os.path.abspath(jsonl_path),
        "source_bytes": st.st_size, "scanned_at": datetime.now(timezone.utc).isoformat(),
        "events_total": len(rows), "first_ts": first_ts, "last_ts": last_ts,
        "duration_sec": (_iso_to_epoch(last_ts) or 0) - (_iso_to_epoch(first_ts) or 0) if first_ts and last_ts else None,
        "by_type": dict(sorted(by_type.items(), key=lambda x: -x[1])),
        "by_attribution": dict(sorted(by_attr.items(), key=lambda x: -x[1])),
        "by_model": dict(sorted(by_model.items(), key=lambda x: -x[1])),
        "system_subtypes": dict(sorted(by_subtype.items(), key=lambda x: -x[1])),
        "tokens_total": tot, "tokens_by_model": tokens_by_model,
        "boundaries": timeline["boundaries"], "segments": timeline["segments"],
        "fork_provenance": {"inherited_events": ff_inherited, "own_events": ff_own,
                            "parents": ff_parents, "is_fork": ff_inherited > 0,
                            "is_root": ff_inherited == 0},
        "dense_profile": {
            "human_turns": n_user,
            "human_bytes_total": sum(b for b, _, _ in user_bytes),
            "human_bytes_mean": round(sum(b for b, _, _ in user_bytes) / n_user, 1) if n_user else 0,
            "biggest_human_msgs": [{"bytes": b, "line": l, "ts": t} for b, l, t in user_bytes[:10]],
            "biggest_assistant_msgs": [{"bytes": b, "line": l, "ts": t} for b, l, t in asst_bytes[:10]],
            "assistant_bytes_mean": round(sum(b for b, _, _ in asst_bytes) / len(asst_bytes), 1) if asst_bytes else 0,
        },
        "largest_gaps_sec": [{"gap_sec": g, "line": l, "ts": t} for g, l, t in gaps[:12]],
    }
    return {"summary": summary, "rows": rows}


def write_scan(jsonl_path: str, out_dir: str, *, write_rows: bool = True) -> dict:
    """Run the scan and persist: <stem>.summary.json (+ <stem>.rows.ndjson). Returns the paths."""
    res = scan_session(jsonl_path)
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(jsonl_path))[0]
    spath = os.path.join(out_dir, f"{stem}.summary.json")
    with open(spath, "w", encoding="utf-8") as f:
        json.dump(res["summary"], f, ensure_ascii=False, indent=2)
    out = {"summary_path": spath, "events": res["summary"]["events_total"]}
    if write_rows:
        rpath = os.path.join(out_dir, f"{stem}.rows.ndjson")
        with open(rpath, "w", encoding="utf-8") as f:
            for r in res["rows"]:
                f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
        out["rows_path"] = rpath
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    path = sys.argv[1]
    out_dir = "."
    write_rows = True
    a = sys.argv[2:]
    if "--out-dir" in a:
        out_dir = a[a.index("--out-dir") + 1]
    if "--no-rows" in a:
        write_rows = False
    rep = write_scan(path, out_dir, write_rows=write_rows)
    print(json.dumps(rep, indent=2))
