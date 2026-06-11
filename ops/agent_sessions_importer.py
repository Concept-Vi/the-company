#!/usr/bin/env python3
"""agent_sessions_importer — backfill the agent-session REGISTRY from the Claude Code catalog.

Session Fabric F1.2 (guide §B): every main session under ``~/.claude/projects/<project>/
<session-uuid>.jsonl`` (~1,059 measured 2026-06-11) becomes ONE durable registry record at
``<store>/agent_sessions/<session-uuid>.json`` (``FsStore.save_agent_session`` — the
save_journey whole-record-atomic pattern), so the registry fold (``Suite.list_agent_sessions``)
and the ``session://<id>`` resolver cover the whole historical catalog, not just sessions the
supervisor sees live. Sidechains (``agent-*.jsonl``) and nested ``subagents/`` files are NOT
sessions — they are skipped (the transcript exporter rolls them up; different organ).

READ-ONLY ON THE CATALOG (hard law): this process opens Tim's jsonl files for reading ONLY —
it never writes, moves, renames, touches, or locks anything under ``~/.claude``. All output
goes to the company store.

NO EVENTS (single-writer law, criteria audit C6): backfilled history lands as whole-record
files (durable identity) ONLY. The importer never emits ``agent_sessions.*`` events — the
session SUPERVISOR is the single fabric-event writer, and a 1,000-event synthetic backfill
on events.jsonl (the hottest shared file) would be both a law violation and a pollution.
Imported records carry ``state="closed"`` (historical sessions have no live process; WAKE
re-spawns via ``--resume``). A record whose state is NOT closed is NEVER overwritten here —
that record is the live supervisor's, not history's.

THE TITLE FALLBACK CHAIN (criteria F1.2, EXACT — measured ~3-7% ai-title coverage, ~100% via
fallbacks; audit B2):
    1. ``ai-title``      — the CC-generated title. These lines are NOT headers: they sit
                           scattered body-to-tail, so extraction is LAST-OCCURRENCE-WINS
                           (the guide's tail-scan ruling — implemented here as overwrite-on-
                           encounter inside the one streaming pass the envelope needs anyway,
                           which yields the identical last-occurrence result).
    2. ``last-prompt``   — the final user prompt line CC records (same last-occurrence rule).
    3. first REAL user turn, truncated — the first ``user`` line that is not meta/noise
                           (system-reminders, Caveat:, command echoes, interrupt markers,
                           task notifications, the summarizer synthetic prompt).
    4. untitled+envelope — a title CONSTRUCTED from the envelope (project · start date ·
                           turn count), so coverage is 100% and the contract entry never
                           promises a fictional field.

Each record (OPEN, schema-additive): {id, name:None, cwd, state:"closed", started,
last_activity, title, title_source, git_branch, cc_version, project, jsonl_path, jsonl_bytes,
jsonl_mtime, turns, imported_at, schema_ver:1}. Re-runs are idempotent: an unchanged source
(same bytes+mtime) is skipped unless ``--force``.

Fail loud: per-file errors are collected and PRINTED, and the process exits non-zero if any
file failed or nothing was imported. Bad json lines inside a file are tolerated-and-counted
(a 4,500-file historical corpus contains torn tails), reported in the stats — never silent.

Run:  /home/tim/company/.venv/bin/python ops/agent_sessions_importer.py [--force] [--limit N]
          [--projects-dir DIR] [--store-dir DIR]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# User-turn texts that are NOT a real prompt (synthesis Round 1b rule 5 + the summarizer rule 7)
# — never usable as a title.
NOISE_PREFIXES = (
    "<system-reminder", "Caveat:", "<command-name", "<command-message",
    "<local-command-stdout", "[Request interrupted", "<task-notification",
    "Context: This summary will be shown",
)
TITLE_MAX = 100
TITLE_SOURCES = ("ai-title", "last-prompt", "first-user-turn", "untitled-envelope")


def _first_text(message: dict | None) -> str | None:
    """A message's first TEXT content — plain-string content or the first text block."""
    if not isinstance(message, dict):
        return None
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text" and isinstance(block.get("text"), str):
                return block["text"]
    return None


def _squash(text: str, limit: int = TITLE_MAX) -> str:
    """One line, whitespace-collapsed, hard-capped (titles are catalog labels, not transcripts)."""
    one = " ".join(text.split())
    return one if len(one) <= limit else one[: limit - 1].rstrip() + "…"


def scan_session_file(path: str) -> dict:
    """ONE streaming read-only pass over a main-session jsonl → everything the record needs.

    The guide's tail-scan ruling is about SEMANTICS (last-occurrence-wins for ai-title /
    last-prompt) — and the envelope (first/last timestamps, turn count) needs head+body
    anyway, so one forward pass collecting both is the cheapest total read: overwriting
    ai_title/last_prompt on every encounter IS last-occurrence-wins. Streams line-by-line
    (never json.load of the file — the catalog holds a 238 MB outlier). Never accumulates
    bodies. Bad lines are counted, not fatal."""
    first_ts = last_ts = None
    cwd = git_branch = version = None
    ai_title = last_prompt = first_user_text = None
    summarizer = False
    turns = 0
    bad_lines = 0
    with open(path, "r", encoding="utf-8", errors="replace") as f:   # READ-ONLY — the one open mode this file uses
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                bad_lines += 1
                continue
            if not isinstance(rec, dict):
                bad_lines += 1
                continue
            ts = rec.get("timestamp")
            if isinstance(ts, str) and ts:
                if first_ts is None:
                    first_ts = ts
                last_ts = ts
            kind = rec.get("type")
            if kind == "ai-title":
                t = rec.get("aiTitle")
                if isinstance(t, str) and t.strip():
                    ai_title = t.strip()                  # overwrite = last-occurrence-wins (tail-scan semantics)
            elif kind == "last-prompt":
                t = rec.get("lastPrompt")
                if isinstance(t, str) and t.strip():
                    last_prompt = t.strip()
            elif kind in ("user", "assistant"):
                turns += 1
                if cwd is None and isinstance(rec.get("cwd"), str) and rec.get("cwd"):
                    cwd = rec["cwd"]
                if git_branch is None and isinstance(rec.get("gitBranch"), str) and rec.get("gitBranch"):
                    git_branch = rec["gitBranch"]
                if version is None and isinstance(rec.get("version"), str) and rec.get("version"):
                    version = rec["version"]
                if kind == "user" and first_user_text is None and not rec.get("isMeta"):
                    text = _first_text(rec.get("message"))
                    if isinstance(text, str):
                        stripped = text.strip()
                        if stripped.startswith("Context: This summary will be shown"):
                            # CC's INTERNAL summarizer one-shot (synthesis Round 1b rule 7) — measured
                            # 2026-06-11: ~77% of the main-file catalog is these, a reality no audit
                            # surfaced. Marked additively so the face/list lanes can filter machine
                            # sessions from Tim's fleet view (gap-pressure drop, F10.1 ledger).
                            summarizer = True
                        if stripped and not any(stripped.startswith(p) for p in NOISE_PREFIXES):
                            first_user_text = stripped
    return {"first_ts": first_ts, "last_ts": last_ts, "cwd": cwd, "git_branch": git_branch,
            "version": version, "ai_title": ai_title, "last_prompt": last_prompt,
            "first_user_text": first_user_text, "summarizer": summarizer,
            "turns": turns, "bad_lines": bad_lines}


def build_record(sid: str, project: str, path: str, scan: dict) -> dict:
    """The scan → ONE registry record, applying the EXACT title fallback chain (F1.2)."""
    st = os.stat(path)
    if scan["ai_title"]:
        title, source = _squash(scan["ai_title"]), "ai-title"
    elif scan["last_prompt"]:
        title, source = _squash(scan["last_prompt"]), "last-prompt"
    elif scan["first_user_text"]:
        title, source = _squash(scan["first_user_text"]), "first-user-turn"
    else:
        started_day = (scan["first_ts"] or "")[:10] or "undated"
        title = f"Untitled — {project} · {started_day} · {scan['turns']} turns"
        source = "untitled-envelope"
    mtime_iso = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat()
    return {
        "id": sid,
        "name": None,                                   # a human launch label — the launcher's field, never the importer's
        "cwd": scan["cwd"],
        "state": "closed",                              # historical: no live process; WAKE re-spawns via --resume
        "started": scan["first_ts"],
        "last_activity": scan["last_ts"] or mtime_iso,  # honest fallback: the file's own mtime
        "title": title,
        "title_source": source,
        "git_branch": scan["git_branch"],
        "cc_version": scan["version"],
        "project": project,
        "jsonl_path": path,
        "jsonl_bytes": st.st_size,
        "jsonl_mtime": st.st_mtime,
        "summarizer": scan["summarizer"],               # CC-internal summary one-shot (machine session, filterable)
        "turns": scan["turns"],
        "bad_lines": scan["bad_lines"],
        "imported_at": datetime.now(timezone.utc).isoformat(),
        "schema_ver": 1,
    }


def run_import(projects_dir: str, store, force: bool = False, limit: int | None = None) -> dict:
    """Backfill the registry. Returns the stats dict (the caller prints/asserts it).

    Skip rules (each counted, never silent):
      · unchanged source (same jsonl bytes+mtime as the existing record) unless --force;
      · a record whose state != closed (the live supervisor's record — never stomped);
      · a duplicate session uuid across project dirs (kept: the later last_activity).
    A file that cannot be read at all lands in file_errors → non-zero exit in main()."""
    stats = {"project_dirs": 0, "main_files": 0, "written": 0, "skipped_unchanged": 0,
             "skipped_live": 0, "duplicates": 0, "bad_lines": 0, "summarizer_sessions": 0,
             "file_errors": [], "titles": {s: 0 for s in TITLE_SOURCES}}
    written_activity: dict[str, str] = {}              # id → last_activity written THIS run (duplicate resolution)
    project_dirs = sorted(d for d in (os.path.join(projects_dir, n) for n in os.listdir(projects_dir))
                          if os.path.isdir(d))
    stats["project_dirs"] = len(project_dirs)
    done = 0
    for pdir in project_dirs:
        project = os.path.basename(pdir)
        for fname in sorted(os.listdir(pdir)):
            if not fname.endswith(".jsonl") or fname.startswith("agent-"):
                continue                                # sidechains are not sessions
            if limit is not None and done >= limit:
                break
            path = os.path.join(pdir, fname)
            sid = fname[: -len(".jsonl")]
            stats["main_files"] += 1
            done += 1
            try:
                st = os.stat(path)
                if sid in written_activity:             # the same uuid in TWO project dirs
                    stats["duplicates"] += 1
                existing = store.load_agent_session(sid)
                if existing is not None and sid not in written_activity:
                    if existing.get("state") not in (None, "closed"):
                        stats["skipped_live"] += 1      # the supervisor's live record — not history's to stomp
                        continue
                    if (not force and existing.get("jsonl_mtime") == st.st_mtime
                            and existing.get("jsonl_bytes") == st.st_size):
                        stats["skipped_unchanged"] += 1
                        continue
                scan = scan_session_file(path)
                rec = build_record(sid, project, path, scan)
                if sid in written_activity and (rec["last_activity"] or "") <= written_activity[sid]:
                    continue                            # the copy already written is the later one — keep it
                store.save_agent_session(rec)
                written_activity[sid] = rec["last_activity"] or ""
                stats["written"] += 1
                stats["bad_lines"] += scan["bad_lines"]
                stats["titles"][rec["title_source"]] += 1
                if rec["summarizer"]:
                    stats["summarizer_sessions"] += 1
            except Exception as exc:                    # noqa: BLE001 — collected + reported + non-zero exit
                stats["file_errors"].append(f"{path}: {type(exc).__name__}: {exc}")
        if limit is not None and done >= limit:
            break
    return stats


def print_stats(stats: dict) -> None:
    """The coverage report the F1.2 unit-verify bar requires — loud, percentages included."""
    w = stats["written"]
    print(f"agent_sessions importer — {stats['project_dirs']} project dirs · "
          f"{stats['main_files']} main-session jsonl scanned (READ-ONLY)")
    print(f"  records written: {w} · skipped unchanged: {stats['skipped_unchanged']} · "
          f"skipped live(non-closed record): {stats['skipped_live']} · cross-dir duplicates: {stats['duplicates']}")
    if w:
        parts = []
        for source in TITLE_SOURCES:
            n = stats["titles"][source]
            parts.append(f"{source} {n} ({100.0 * n / w:.1f}%)")
        print(f"  title coverage: {' · '.join(parts)} → 100.0% titled (chain is total by construction)")
        print(f"  summarizer one-shots (CC-internal, marked summarizer:true): {stats['summarizer_sessions']} "
              f"({100.0 * stats['summarizer_sessions'] / w:.1f}%) — machine sessions, filterable in the registry")
    print(f"  bad json lines tolerated: {stats['bad_lines']}")
    if stats["file_errors"]:
        print(f"  FILE ERRORS ({len(stats['file_errors'])}) — FAIL LOUD:")
        for err in stats["file_errors"]:
            print(f"    {err}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Backfill the agent-session registry from ~/.claude/projects (read-only).")
    ap.add_argument("--projects-dir", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--store-dir", default=None, help="company store root (default: fabric.config.STORE_DIR)")
    ap.add_argument("--force", action="store_true", help="re-import even when the source jsonl is unchanged")
    ap.add_argument("--limit", type=int, default=None, help="stop after N main files (probe runs)")
    args = ap.parse_args(argv)
    if not os.path.isdir(args.projects_dir):
        print(f"agent_sessions importer: projects dir {args.projects_dir!r} does not exist — nothing to import. "
              f"Fail loud.", file=sys.stderr)
        return 1
    from fabric import config as fcfg
    from store.fs_store import FsStore
    store = FsStore(args.store_dir or fcfg.STORE_DIR)
    stats = run_import(args.projects_dir, store, force=args.force, limit=args.limit)
    print_stats(stats)
    if stats["file_errors"]:
        return 2
    if stats["written"] == 0 and stats["skipped_unchanged"] == 0:
        print("agent_sessions importer: NOTHING imported and nothing previously imported — that is a "
              "failure, not a quiet success.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
