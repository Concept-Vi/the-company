"""tests/event_seq_acceptance.py — F5: event-seq uniqueness, cross-process, gated on the LIVE log.

HISTORY: the seq was atomic only within one process; the flock trade-off was deliberately surfaced-not-
paid. On 2026-06-29 the detector found 1,151 duplicated seqs in the live log — the cross-process risk
was REAL (multiple faces/sessions write). Resolution: append_event now wraps the read-last→+1→append in
the store's cross-process graph_lock (the same primitive the mailbox pays). Historical dups remain as
archaeology; this suite gates that NO NEW dup lands after the cutover, and PROVES cross-process
uniqueness by hammering from concurrent subprocesses.
"""
import json, os, subprocess, sys, tempfile, threading

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore

# BASELINE gate (strict): 1,151 dups existed when the flock landed (2026-07-13 — accrued over weeks of
# multi-process writing on pre-flock code). ANY dup beyond the baseline = a STILL-RUNNING pre-flock
# writer (an old bridge / another session's MCP face) — the failure is the teaching signal: restart it.
DUP_BASELINE = 1151

PASS = 0
def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")

# 1 — THE LIVE LOG: no NEW duplicated seq post-cutover (the standing detector)
live = os.path.join(ROOT, ".data", "store", "events.jsonl")
if os.path.exists(live):
    seen, dups, bad, total = set(), 0, 0, 0
    with open(live, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                e = json.loads(ln)
            except ValueError:
                bad += 1
                continue
            total += 1
            s_ = e.get("seq")
            if s_ in seen:
                dups += 1
            seen.add(s_)
    check(f"live log parses (events={total}, bad lines={bad})", bad == 0)
    check(f"NO NEW duplicated seq beyond the baseline (dups={dups}, baseline={DUP_BASELINE} — "
          f"a rise means a PRE-FLOCK writer is still running: restart it)", dups <= DUP_BASELINE)
else:
    check("live log absent — invariant vacuously holds", True)

# 2 — in-process: 8 threads x 25 appends -> 200 unique gapless seqs
tmp_dir = os.path.join(tempfile.mkdtemp(prefix="seq-"), "store")
tmp = FsStore(tmp_dir)
def hammer():
    for _ in range(25):
        tmp.append_event({"kind": "t.probe", "summary": "x"})
threads = [threading.Thread(target=hammer) for _ in range(8)]
[t.start() for t in threads]; [t.join() for t in threads]
got = sorted(e["seq"] for e in tmp.events_since(-1))
check("in-process concurrent appends: UNIQUE seqs", len(got) == len(set(got)) == 200)
check("...and GAPLESS (0..199)", got == list(range(200)))

# 3 — CROSS-PROCESS: 4 subprocesses x 30 appends concurrently -> 320 total, all unique (THE fix's proof)
code = (
    "import sys; sys.path.insert(0, %r); from store.fs_store import FsStore; "
    "s = FsStore(%r); [s.append_event({'kind': 'xp.probe', 'summary': 'x'}) for _ in range(30)]"
) % (ROOT, tmp_dir)
procs = [subprocess.Popen([sys.executable, "-c", code]) for _ in range(4)]
[p.wait() for p in procs]
check("all subprocess writers exited clean", all(p.returncode == 0 for p in procs))
allseq = [e["seq"] for e in tmp.events_since(-1)]
check(f"CROSS-PROCESS appends yield UNIQUE seqs (n={len(allseq)})",
      len(allseq) == len(set(allseq)) == 320)
check("...and strictly increasing in file order", all(b > a for a, b in zip(allseq, allseq[1:])))

print(f"\nALL {PASS} CHECKS PASS — event seq unique ACROSS PROCESSES (flock paid with evidence); live log gated (F5)")
