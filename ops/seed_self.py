#!/usr/bin/env python3
"""ops/seed_self.py — a LIVE session pre-seeds its OWN self-id so it survives compaction (#69/#65).

THE GAP (2026-06-18): resolve_own_session(self) self-heal only works for sessions started AFTER the
SessionStart marker-hook deploy (51a0cf4). Pre-deploy long-running sessions (their hook config is
snapshotted at launch) never wrote a marker → after a compaction they CANNOT auto-self-recall
(verified: resolve_own_session(self) raised AmbiguousSelfError for recollection, a compacted pre-hook
session, until it self-seeded). The /proc backfill-from-outside is UNSAFE (the current post-compaction
sid is internal to the process — cmdline --resume is the STALE launch anchor; start-time collides;
content is entangled across coordinating sessions → mis-id corruption, the exact thing #69 guards).

THE RELIABLE FIX (run from INSIDE the session — the only place that knows its own sid for certain):
  • SELF-ID by NONCE: pass --phrase "<a string ONLY this session has emitted this run>"; this script
    greps ~/.claude/projects/*/*.jsonl for it → the SOLE containing transcript is THIS session (zero
    inference; immune to cwd-collision + mtime-race). OR pass --sid <id> if you already know it.
  • SEED: write ~/.recollection/self/<claude-ancestor-pid>.json (the marker resolve_own_session reads by
    claude_pid). claude_pid is STABLE across compaction, so the marker keeps resolving. Own-dir write
    only — NO shared-registration mutation (safe). With --fold-registration <handle>, also folds
    {claude_pid, session_id} into THIS session's OWN fabric registration (additive; preserves fields).

USAGE (inside the session, BEFORE it compacts):
  # two-step nonce (most reliable): first emit a nonce in a turn, then:
  python ops/seed_self.py --phrase "MY-UNIQUE-NONCE-abc123"
  # or if you know your sid:
  python ops/seed_self.py --sid 970bc7c0-... [--fold-registration ch-xxxx]

After seeding, resolve_own_session() resolves THIS session by its claude_pid across the compaction.
"""
from __future__ import annotations
import argparse, glob, json, os, sys, time

PROJECTS_DIR = os.path.expanduser("~/.claude/projects")
MARKER_DIR = os.path.expanduser("~/.recollection/self")


def _claude_ancestor_pid() -> int | None:
    """Walk /proc from THIS process up to the `claude` ancestor — the session-unique, cwd-independent,
    compaction-stable key. Mirrors runtime/session_scan._claude_ancestor_pid (comm=='claude')."""
    pid = os.getpid()
    for _ in range(40):
        try:
            with open(f"/proc/{pid}/status") as f:
                ppid = None
                for line in f:
                    if line.startswith("PPid:"):
                        ppid = int(line.split()[1]); break
            comm = open(f"/proc/{pid}/comm").read().strip()
        except (OSError, ValueError):
            return None
        if comm == "claude":
            return pid
        if not ppid or ppid <= 1:
            return None
        pid = ppid
    return None


def _find_sid_by_phrase(phrase: str) -> tuple[str | None, list[str]]:
    """The SOLE transcript containing `phrase` is SELF (the session emitted it this run). Returns
    (sid, all_matches) — sid is set only when EXACTLY ONE transcript matches (unambiguous)."""
    matches = []
    for f in glob.glob(os.path.join(PROJECTS_DIR, "*", "*.jsonl")):
        if "/agent-" in f:
            continue
        try:
            with open(f, "r", errors="ignore") as fh:
                if phrase in fh.read():
                    matches.append(f)
        except OSError:
            continue
    if len(matches) == 1:
        return os.path.splitext(os.path.basename(matches[0]))[0], matches
    return None, matches


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--phrase", help="a string ONLY this session has emitted this run (nonce self-id)")
    ap.add_argument("--sid", help="this session's id, if already known")
    ap.add_argument("--fold-registration", metavar="HANDLE",
                    help="also fold {claude_pid, session_id} into this session's OWN fabric registration")
    a = ap.parse_args()

    pid = _claude_ancestor_pid()
    if not pid:
        print("seed_self: could not find the claude ancestor pid (run me INSIDE the session).", file=sys.stderr)
        return 2

    sid = a.sid
    transcript = None
    if not sid:
        if not a.phrase:
            print("seed_self: pass --sid OR --phrase (a unique string this session emitted).", file=sys.stderr)
            return 2
        sid, matches = _find_sid_by_phrase(a.phrase)
        if not sid:
            print(f"seed_self: phrase matched {len(matches)} transcripts (need exactly 1 for an "
                  f"unambiguous self-id). Use a more unique phrase. Matches: "
                  f"{[os.path.basename(m) for m in matches[:5]]}", file=sys.stderr)
            return 3
        transcript = matches[0]
    if not transcript:
        hits = glob.glob(os.path.join(PROJECTS_DIR, "*", f"{sid}.jsonl"))
        transcript = hits[0] if hits else None

    os.makedirs(MARKER_DIR, exist_ok=True)
    marker = {"session_id": sid, "transcript_path": transcript,
              "cwd": os.path.dirname(transcript).replace(PROJECTS_DIR + "/", "").replace("-", "/") if transcript else None,
              "ts": time.time(), "claude_pid": pid, "seeded_by": "ops/seed_self.py"}
    mp = os.path.join(MARKER_DIR, f"{pid}.json")
    with open(mp, "w") as f:
        json.dump(marker, f)
    out = {"seeded_marker": mp, "claude_pid": pid, "session_id": sid, "transcript": transcript}

    if a.fold_registration:
        reg_p = f"/home/tim/company/.data/channels/{a.fold_registration}.json"
        try:
            r = json.load(open(reg_p))
            r["claude_pid"] = pid
            r["session_id"] = sid
            with open(reg_p, "w") as f:
                json.dump(r, f, indent=2)
            out["folded_registration"] = reg_p
        except Exception as e:  # noqa: BLE001
            out["fold_error"] = f"{type(e).__name__}: {e}"

    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
