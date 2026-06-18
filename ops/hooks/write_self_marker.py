#!/usr/bin/env python3
"""ops/hooks/write_self_marker.py — #69 self-serve-memory: write THIS session's self-marker.

Called by the SessionStart hook (cc_registry_freshness_check.sh), failure-isolated. Reads the hook's
stdin JSON (Claude Code passes {session_id, transcript_path, cwd, hook_event_name, ...}) and writes
~/.recollection/self/<claude-pid>.json = {session_id, transcript_path, cwd, ts}, keyed by the
CLAUDE-ANCESTOR PID (session-unique, cwd-independent — the cwd alone collides across co-located
sessions). resolve_own_session (runtime/session_scan.py) reads this by walking to its own claude
ancestor → the unambiguous self-id for a top-level session with no COMPANY_SESSION_ID env.

NEVER raises out: the SessionStart hook runs fabric-wide on every session start, so a failure here must
never break anyone's session — any error → silent exit 0. NO env mutation, NO ~/.claude.json edit
(dodges the self-mod auto-deny); a marker FILE is the whole mechanism."""
import sys, os, json, time


def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        data = json.loads(raw)
        sid = data.get("session_id")
        if not sid:
            return 0
        # the claude-ancestor PID — the session-unique key (reuse the ONE walk in session_scan)
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
        try:
            from runtime.session_scan import _claude_ancestor_pid, SELF_MARKER_DIR
            cp = _claude_ancestor_pid()
        except Exception:
            cp, SELF_MARKER_DIR = None, os.path.join(os.path.expanduser("~"), ".recollection", "self")
        if cp is None:
            return 0                                   # no claude ancestor (orphan / odd launch) → no marker
        os.makedirs(SELF_MARKER_DIR, exist_ok=True)
        marker = {"session_id": sid, "transcript_path": data.get("transcript_path"),
                  "cwd": data.get("cwd") or os.getcwd(), "ts": time.time(), "claude_pid": cp}
        tmp = os.path.join(SELF_MARKER_DIR, f".{cp}.tmp")
        final = os.path.join(SELF_MARKER_DIR, f"{cp}.json")
        with open(tmp, "w") as f:
            json.dump(marker, f)
        os.replace(tmp, final)                         # atomic
        return 0
    except Exception:
        return 0                                       # NEVER break the hook — silent on any failure


if __name__ == "__main__":
    sys.exit(main())
