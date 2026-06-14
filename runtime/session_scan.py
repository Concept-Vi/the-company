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
