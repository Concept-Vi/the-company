"""tests/commit_queue_acceptance.py — the concurrent-append/commit QUEUE acceptance (fork, 2026-06-20).

Proves, by use, that the queue FIXES the live race it was built for: concurrent committers under
commit-to-main/no-branches no longer clobber each other (projection's 2774b19 swept DNA's append). The
single FIFO drainer serializes every commit; concurrent ENQUEUE loses nothing.

  CQ1  enqueue validation — bad kind / append-without-file-or-content / commit-without-paths-or-message FAIL LOUD.
  CQ2  ★ THE RACE — N concurrent enqueues of appends to the SAME file → one drain → ALL N land in the file AND
       N commits exist (none swept, none lost). The literal scenario the queue exists for.
  CQ3  FIFO — items apply in enqueue order (the commit log + the file content match the order).
  CQ4  FAIL-LOUD — a commit item with a nonexistent path → deadletter + gap Notice written, cursor advances
       (queue doesn't wedge), NEVER a silent drop.
  CQ5  large append_content (>4KB) — spilled to a payload, applied correctly (the queue line stays atomic).
  CQ6  crash-safe RESUME — drain(max_items=1) then drain() resumes from the cursor (no reprocess, no loss).
"""
import os
import sys
import json
import shutil
import tempfile
import threading
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from ops import commit_queue as cq
from ops.commit_queue import enqueue, drain, CommitQueueError, _paths

PASS = 0
ok = True


def check(label, cond):
    global PASS, ok
    if cond:
        PASS += 1
        print(f"  ok  {label}")
    else:
        ok = False
        print(f"  FAIL  {label}")


def _git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)


def _new_repo():
    """A throwaway git repo + an isolated store dir (so the test never touches the real .data/store)."""
    d = tempfile.mkdtemp(prefix="cq-repo-")
    store = tempfile.mkdtemp(prefix="cq-store-")
    _git(d, "init", "-q")
    _git(d, "config", "user.email", "test@example.com")
    _git(d, "config", "user.name", "cq-test")
    # an initial commit so HEAD exists
    open(os.path.join(d, ".seed"), "w").close()
    _git(d, "add", "-A")
    _git(d, "commit", "-q", "-m", "seed")
    return d, store


def _commit_count(repo):
    r = _git(repo, "rev-list", "--count", "HEAD")
    return int(r.stdout.strip())


# ── CQ1 — enqueue validation ────────────────────────────────────────────────────────────────────────
print("\n[CQ1] enqueue validation (fail-loud)")
_d, _s = _new_repo()
for bad, why in (
    ({"kind": "frobnicate"}, "unknown kind"),
    ({"kind": "append", "append_content": "x"}, "append without file"),
    ({"kind": "append", "file": "a.md"}, "append without content"),
    ({"kind": "commit", "message": "m"}, "commit without paths"),
    ({"kind": "commit", "paths": ["a.md"]}, "commit without message"),
):
    raised = False
    try:
        enqueue(bad, store_dir=_s)
    except CommitQueueError:
        raised = True
    check(f"CQ1 {why} RAISES (fail-loud)", raised)

# ── CQ2 — THE RACE: concurrent enqueue of appends to ONE file, none lost ───────────────────────────────
print("\n[CQ2] ★ the race — N concurrent appends to the SAME file, all survive one drain")
d, s = _new_repo()
N = 24
board = "channel-memory/board.md"
errors = []


def _worker(i):
    try:
        enqueue({"kind": "append", "file": board, "append_content": f"entry-{i:03d}\n",
                 "message": f"append entry-{i:03d}", "by": f"session-{i}"}, store_dir=s)
    except Exception as e:  # noqa
        errors.append(repr(e))


threads = [threading.Thread(target=_worker, args=(i,)) for i in range(N)]
for t in threads:
    t.start()
for t in threads:
    t.join()
check("CQ2 all concurrent enqueues succeeded (no enqueue error)", not errors)
before = _commit_count(d)
res = drain(repo=d, store_dir=s)
check("CQ2 drain applied all N items", len(res["applied"]) == N and not res["failed"])
content = open(os.path.join(d, board), encoding="utf-8").read()
present = sum(1 for i in range(N) if f"entry-{i:03d}" in content)
check(f"CQ2 ALL {N} appends present in the file (none swept/lost)", present == N)
check("CQ2 exactly N commits added (one serialized commit per item)", _commit_count(d) - before == N)
# the deep proof: a clean tree (nothing left uncommitted — no swept-but-uncommitted change)
check("CQ2 working tree CLEAN after drain (no stranded uncommitted change)",
      not _git(d, "status", "--porcelain").stdout.strip())

# ── CQ3 — FIFO order ─────────────────────────────────────────────────────────────────────────────────
print("\n[CQ3] FIFO — items apply in enqueue order")
d, s = _new_repo()
for i in range(6):
    enqueue({"kind": "append", "file": "f.md", "append_content": f"L{i}\n", "message": f"msg L{i}"}, store_dir=s)
drain(repo=d, store_dir=s)
lines = [ln for ln in open(os.path.join(d, "f.md"), encoding="utf-8").read().splitlines() if ln]
check("CQ3 file content is in enqueue order", lines == [f"L{i}" for i in range(6)])
log = _git(d, "log", "--format=%s", "-n", "6").stdout.split("\n")
check("CQ3 commit log is in enqueue order (newest first → reversed matches)",
      [x for x in reversed([l for l in log if l])] == [f"msg L{i}" for i in range(6)])

# ── CQ4 — FAIL-LOUD on a bad item (nonexistent path) → deadletter + gap, no wedge, no silent drop ──────
print("\n[CQ4] fail-loud — a commit with a nonexistent path is deadlettered + Noticed, not silently dropped")
d, s = _new_repo()
enqueue({"kind": "commit", "paths": ["does-not-exist.md"], "message": "should fail"}, store_dir=s)
enqueue({"kind": "append", "file": "good.md", "append_content": "ok\n", "message": "good after bad"}, store_dir=s)
res = drain(repo=d, store_dir=s)
p = _paths(s)
check("CQ4 the bad item FAILED (not silently applied)", len(res["failed"]) == 1)
check("CQ4 the deadletter file records it (loud preservation)",
      os.path.exists(p["deadletter"]) and "should fail" in open(p["deadletter"]).read())
check("CQ4 a gap Notice was written (surfaced, never silent)",
      os.path.exists(p["gaps"]) and "commit_queue_failure" in open(p["gaps"]).read())
check("CQ4 the queue did NOT wedge — the GOOD item after it still applied",
      len(res["applied"]) == 1 and os.path.exists(os.path.join(d, "good.md")))

# ── CQ5 — large append_content spilled to a payload ───────────────────────────────────────────────────
print("\n[CQ5] large content (>4KB) — spilled to a payload, applied correctly")
d, s = _new_repo()
big = "x" * 9000 + "\nEND-MARKER\n"
rec = enqueue({"kind": "append", "file": "big.md", "append_content": big, "message": "big append"}, store_dir=s)
# the queue LINE stays small (the atomicity guarantee) — content lives in the payload
qline = open(_paths(s)["queue"], encoding="utf-8").readline()
check("CQ5 the queue line stays small (<3.5KB) — content spilled, line atomic", len(qline) < 3500)
check("CQ5 the payload file holds the big content", os.path.exists(os.path.join(_paths(s)["payloads"], rec["id"] + ".txt")))
drain(repo=d, store_dir=s)
check("CQ5 the big content landed in the target file", "END-MARKER" in open(os.path.join(d, "big.md")).read())

# ── CQ6 — crash-safe resume (cursor) ──────────────────────────────────────────────────────────────────
print("\n[CQ6] crash-safe resume — drain(max_items=1) then drain() finishes, no reprocess")
d, s = _new_repo()
for i in range(4):
    enqueue({"kind": "append", "file": "r.md", "append_content": f"r{i}\n", "message": f"r{i}"}, store_dir=s)
r1 = drain(repo=d, store_dir=s, max_items=1)
check("CQ6 first drain applied exactly 1 (cursor advanced)", len(r1["applied"]) == 1 and r1["cursor"] == 1)
r2 = drain(repo=d, store_dir=s)
check("CQ6 resume applied the remaining 3 (no reprocess, no loss)",
      len(r2["applied"]) == 3 and r2["remaining"] == 0)
check("CQ6 final file has all 4 entries exactly once",
      open(os.path.join(d, "r.md")).read() == "".join(f"r{i}\n" for i in range(4)))
check("CQ6 exactly 4 commits (each item committed once)", _commit_count(d) - 1 == 4)

print(f"\n{'ALL PASS' if ok else 'FAILURES PRESENT'} — {PASS} checks — the commit-queue: validation, "
      "the concurrent-append race (none lost), FIFO, fail-loud-no-silent-drop, large-content spill, crash-safe resume.")
sys.exit(0 if ok else 1)
