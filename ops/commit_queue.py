"""ops/commit_queue.py — the concurrent-append/commit QUEUE (the no-branches/commit-to-main race fix).

THE PROBLEM (validated by a live instance, 2026-06-20): under the repo's commit-to-main / no-branches law,
when several sessions commit concurrently, one session's `git add -A && git commit` sweeps up ANOTHER
session's still-uncommitted working-tree change (the index-lock race) — e.g. projection's commit (2774b19)
swept DNA's concurrent board append. Concurrent committers clobber.

THE FIX (Tim's directive): members ENQUEUE their write instead of committing directly; a SINGLE DRAINER
applies them FIFO under one cross-process lock — one commit at a time — so there is never a concurrent
`git add/commit`. Two shapes:
  • append  {file, append_content[, message]}  — the COMMON case (a board/STATE append) — just queue it.
  • commit  {paths, message}                   — stage specific paths + commit (already-written files).

DESIGN (reuse-don't-parallel — built on store primitives, not a new store):
  • ENQUEUE is LOCK-FREE + cross-process safe: the small queue LINE is a single O_APPEND write (<4KB → never
    torn on POSIX, the same guarantee fs_store.append_* relies on). Large `append_content` is SPILLED to a CAS
    payload file (tmp+rename atomic) and the line carries only its id — so the line stays small regardless of
    content size, and concurrent enqueuers never interleave.
  • DRAIN holds an exclusive `fcntl.flock` (LOCK_EX) on locks/commit_queue.lock — the SAME cross-process lock
    pattern as fs_store's _CrossProcessLock — so only ONE drainer runs at a time. It reads from a persisted
    CURSOR (consumption-offset, the SSE/inbox pattern), applies each item (append→add→commit | add→commit),
    advances the cursor after EACH success (crash-safe: resume, never reprocess).
  • FAIL-LOUD on a git conflict / nothing-to-commit / bad path: the item is moved to the DEADLETTER with its
    error AND a (gap) Notice is written — NEVER a silent drop. The cursor advances past it (the queue never
    wedges); the work is loudly preserved in the deadletter for the operator.

LAWS: commit-to-main only (no branches) · no Co-Authored-By trailer · fail-loud + no-silent-drop · reuse the
store's flock + atomic-append patterns · registry/cursor-is-truth (the queue file + cursor are the record).
"""
from __future__ import annotations

import fcntl
import json
import os
import subprocess
import uuid
from datetime import datetime, timezone

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # ops/ -> repo root
VALID_KINDS = ("append", "commit")


class CommitQueueError(ValueError):
    """A malformed enqueue (fail-loud at enqueue) — never a silently-malformed queue item."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _paths(store_dir: str) -> dict:
    """All queue paths under a store dir (default the repo's .data/store; overridable for tests)."""
    return {
        "queue": os.path.join(store_dir, "commit_queue.jsonl"),
        "cursor": os.path.join(store_dir, "commit_queue.cursor"),
        "lock": os.path.join(store_dir, "locks", "commit_queue.lock"),
        "payloads": os.path.join(store_dir, "commit_queue_payloads"),
        "deadletter": os.path.join(store_dir, "commit_queue.deadletter.jsonl"),
        "gaps": os.path.join(store_dir, "commit_queue.gaps.jsonl"),
    }


def _ensure_dirs(store_dir: str) -> None:
    os.makedirs(os.path.join(store_dir, "locks"), exist_ok=True)
    os.makedirs(os.path.join(store_dir, "commit_queue_payloads"), exist_ok=True)


def enqueue(item: dict, *, store_dir: str | None = None) -> dict:
    """Append ONE write-request to the queue. Lock-free + cross-process safe (the line is a single O_APPEND
    write; large append_content is spilled to a payload file so the line stays small). Fail-loud on a bad
    shape (the drainer must never meet a malformed item). Returns the persisted queue record."""
    store_dir = store_dir or os.path.join(_ROOT, ".data", "store")
    if not isinstance(item, dict):
        raise CommitQueueError(f"enqueue: item must be a dict, got {type(item).__name__}")
    kind = item.get("kind")
    if kind not in VALID_KINDS:
        raise CommitQueueError(f"enqueue: kind must be one of {VALID_KINDS}, got {kind!r} (fail loud).")
    _ensure_dirs(store_dir)
    p = _paths(store_dir)
    rid = item.get("id") or uuid.uuid4().hex
    rec = {"ts": _now(), "id": rid, "kind": kind, "by": item.get("by") or "unknown"}

    if kind == "append":
        f = item.get("file")
        content = item.get("append_content")
        if not f or not isinstance(f, str):
            raise CommitQueueError("enqueue(append): needs a non-empty string `file` (target path). Fail loud.")
        if content is None or not isinstance(content, str):
            raise CommitQueueError("enqueue(append): needs a string `append_content`. Fail loud.")
        # SPILL the content to a CAS payload (tmp+rename atomic) so the queue line stays small + atomic.
        payload_path = os.path.join(p["payloads"], rid + ".txt")
        tmp = payload_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(content)
        os.replace(tmp, payload_path)
        rec.update(file=f, payload_ref=rid, message=item.get("message") or f"queue: append to {f}")
    else:  # commit
        paths = item.get("paths")
        msg = item.get("message")
        if not paths or not isinstance(paths, (list, tuple)) or not all(isinstance(x, str) for x in paths):
            raise CommitQueueError("enqueue(commit): needs a non-empty list[str] `paths`. Fail loud.")
        if not msg or not isinstance(msg, str):
            raise CommitQueueError("enqueue(commit): needs a non-empty string `message`. Fail loud.")
        rec.update(paths=list(paths), message=msg)

    # ONE O_APPEND write of a single <4KB line → never torn across concurrent enqueuers (the fs_store guarantee).
    line = json.dumps(rec)
    if len(line) > 3500:
        raise CommitQueueError("enqueue: queue line too large (>3.5KB) — spill more fields to payloads. Fail loud.")
    with open(p["queue"], "a", encoding="utf-8") as fh:
        fh.write(line + "\n")
    return rec


def _read_cursor(p: dict) -> int:
    try:
        with open(p["cursor"], encoding="utf-8") as fh:
            return int((fh.read() or "0").strip() or "0")
    except (FileNotFoundError, ValueError):
        return 0


def _write_cursor(p: dict, n: int) -> None:
    tmp = p["cursor"] + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(str(n))
    os.replace(tmp, p["cursor"])


def _all_items(p: dict) -> list[dict]:
    if not os.path.exists(p["queue"]):
        return []
    out = []
    with open(p["queue"], encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue   # a torn/garbage line is skipped on read (enqueue guarantees whole lines)
    return out


def _git(repo: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)


def _deadletter(p: dict, rec: dict, error: str) -> None:
    """Loud preservation — the failed item + its error to the deadletter AND a (gap) Notice. Never a silent drop."""
    with open(p["deadletter"], "a", encoding="utf-8") as fh:
        fh.write(json.dumps({**rec, "error": error, "failed_at": _now()}) + "\n")
    with open(p["gaps"], "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": _now(), "kind": "commit_queue_failure", "item": rec.get("id"),
                             "notice": f"commit-queue item {rec.get('id')} FAILED: {error}",
                             "detail": rec}) + "\n")


def _apply_one(rec: dict, repo: str, p: dict) -> tuple[bool, str]:
    """Apply ONE item: append→add→commit | add→commit. Returns (ok, message). FAIL-LOUD: a failure returns
    (False, error) — the caller deadletters + Notices; never a silent success/drop."""
    kind = rec.get("kind")
    if kind == "append":
        target = os.path.join(repo, rec["file"])
        payload_path = os.path.join(p["payloads"], rec["payload_ref"] + ".txt")
        if not os.path.exists(payload_path):
            return False, f"payload {rec['payload_ref']} missing (cannot apply append)"
        with open(payload_path, encoding="utf-8") as fh:
            content = fh.read()
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "a", encoding="utf-8") as fh:   # the APPEND (one writer — the drainer — so safe)
            fh.write(content)
        add = _git(repo, "add", "--", rec["file"])
        if add.returncode != 0:
            return False, f"git add failed: {add.stderr.strip()[:200]}"
        paths_desc = rec["file"]
    else:  # commit
        add = _git(repo, "add", "--", *rec["paths"])
        if add.returncode != 0:
            return False, f"git add failed: {add.stderr.strip()[:200]}"
        paths_desc = ",".join(rec["paths"])

    # nothing-to-commit is a FAIL-LOUD condition (the item expected to commit something) — not silent.
    status = _git(repo, "status", "--porcelain")
    if not status.stdout.strip():
        return False, f"nothing staged to commit for {paths_desc} (item expected a change)"
    commit = _git(repo, "commit", "-m", rec["message"])   # NO Co-Authored-By trailer (repo law)
    if commit.returncode != 0:
        return False, f"git commit failed: {commit.stderr.strip()[:200] or commit.stdout.strip()[:200]}"
    return True, rec["message"]


def drain(repo: str | None = None, *, store_dir: str | None = None, max_items: int | None = None) -> dict:
    """Apply queued items FIFO under one cross-process flock — ONE commit at a time. Crash-safe via the
    persisted cursor (advances after each success). A failed item is deadlettered + Noticed (loud, never
    dropped) and the cursor advances past it (the queue never wedges). Returns a summary."""
    repo = repo or _ROOT
    store_dir = store_dir or os.path.join(_ROOT, ".data", "store")
    _ensure_dirs(store_dir)
    p = _paths(store_dir)

    lock_fd = os.open(p["lock"], os.O_RDWR | os.O_CREAT, 0o644)
    fcntl.flock(lock_fd, fcntl.LOCK_EX)   # blocking exclusive lock ACROSS PROCESSES — only one drainer at a time
    try:
        items = _all_items(p)
        cursor = _read_cursor(p)
        applied, failed = [], []
        i = cursor
        while i < len(items):
            if max_items is not None and len(applied) + len(failed) >= max_items:
                break
            rec = items[i]
            ok, msg = _apply_one(rec, repo, p)
            if ok:
                applied.append({"id": rec.get("id"), "message": msg})
            else:
                _deadletter(p, rec, msg)
                failed.append({"id": rec.get("id"), "error": msg})
            i += 1
            _write_cursor(p, i)   # advance AFTER each item (success or loud-fail) — crash-safe, no reprocess
        return {"ok": True, "applied": applied, "failed": failed,
                "cursor": i, "total": len(items), "remaining": max(0, len(items) - i)}
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2 and sys.argv[1] == "drain":
        print(json.dumps(drain(), indent=2))
    else:
        print("usage: python ops/commit_queue.py drain   (enqueue is the library call commit_queue.enqueue)")
