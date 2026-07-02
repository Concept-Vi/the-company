"""tests/circuit_compose_acceptance.py — C5.2: intent lifecycle = MARKS ONLY; state = a fold over marks
+ THE CLOCK (④ L5-CIRCUIT stage 2 — the zombie-killer).

THE BAR (COMPLETION-CRITERIA §L5 C5.2): claim(lease) / heartbeat / suspend / terminal as mark_types/ rows;
runtime/circuit.compose_state derives pending/running/suspended/lapsed/terminal — **a test intent with an
expired lease composes to LAPSED with NO reaper process running**. Derived, never stamped.

The EXHAUSTIVE state matrix, every mark combination × clock position:
  pending · running-fresh-lease · running-extended-by-heartbeat · lapsed-expired-no-terminal ·
  terminal-each-outcome (succeeded/failed/cancelled) · suspend (parked; before/after claim; resume) ·
  terminal-after-lapse · reclaim-after-lapse · terminal-wins-over-live-lease · zero-length lease (the
  pour's "liveness never proven") — plus the writers' fail-loud grammar (claim-on-terminal, claim-over-
  live-lease, heartbeat-without-running, double-terminal, unknown outcome, malformed lease) and the
  no-reaper proof (composing twice writes NOTHING — the state is READ, not maintained).

By USE: a temp-root FsStore (per-root ns isolation on container.mark — stage 1's law), real marks through
the ONE API (append_mark), the clock passed explicitly so every position is reproducible.
"""
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("COMPANY_TEST_RUN", "1")   # tag-at-source: never pollute the operator's lanes

from store.fs_store import FsStore                                            # noqa: E402
from runtime.circuit import (compose_state, compose_from_store, claim_intent, heartbeat,    # noqa: E402
                             suspend_intent, terminate, CircuitError, TERMINAL_OUTCOMES)
from runtime.mark_types import MarkTypeRegistry                               # noqa: E402

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def raises(label, fn, needle=""):
    try:
        fn()
    except CircuitError as e:
        check(label + f" [{str(e)[:60]}…]" if needle else label, needle in str(e))
        return
    raise AssertionError(f"FAIL (did not raise): {label}")


store = FsStore(os.path.join(tempfile.mkdtemp(prefix="circuit-"), "store"))
T0 = datetime(2026, 7, 2, 12, 0, 0, tzinfo=timezone.utc)


def iso(dt):
    return dt.isoformat()


# ── 0 · the VOCABULARY is files (mark_types rows discovered, drift-home covered by its own suite) ────
reg = MarkTypeRegistry().discover([os.path.join(ROOT, "mark_types")])
for mid in ("intent_claim", "intent_heartbeat", "intent_suspend", "intent_terminal"):
    check(f"vocabulary=files: mark_types/{mid}.py is a discovered registry row", mid in reg)

# ── 1 · PENDING: no claim → pending (a created-but-unclaimed intent) ─────────────────────────────────
t_pend = "intent://global/acc-pending"
s = compose_from_store(store, t_pend, now=T0)
check("no marks at all → PENDING (never an error; the unclaimed intent)", s["state"] == "pending")
s = compose_state(t_pend, [{"mark_type": "comment", "value": "noise", "ts": iso(T0)}], now=T0)
check("non-lifecycle marks are ignored → still PENDING (additive thread)", s["state"] == "pending")

# ── 2 · RUNNING, fresh lease: claim with now <= lease_until ─────────────────────────────────────────
t_run = "intent://global/acc-running"
claim_intent(store, t_run, by="agent://executor-1", session="session://s1/step/t1",
             lease_until=iso(T0 + timedelta(minutes=5)), now=T0)
s = compose_from_store(store, t_run, now=T0 + timedelta(minutes=1))
check("claim + now <= lease_until → RUNNING", s["state"] == "running")
check("running view carries the claim (by/session) — the live handle is legible",
      s["claim"]["by"] == "agent://executor-1" and s["claim"]["session"] == "session://s1/step/t1")

# ── 3 · RUNNING extended by heartbeat: the lease FOLD ────────────────────────────────────────────────
heartbeat(store, t_run, lease_until=iso(T0 + timedelta(minutes=20)), now=T0 + timedelta(minutes=2))
s = compose_from_store(store, t_run, now=T0 + timedelta(minutes=10))
check("heartbeat EXTENDS the lease: at claim-lease+5m the intent is still RUNNING",
      s["state"] == "running")
check("effective lease is the heartbeat's (max fold), not the claim's",
      s["lease_until"] == iso(T0 + timedelta(minutes=20)))
s = compose_from_store(store, t_run, now=T0 + timedelta(minutes=21))
check("past the EXTENDED lease with no terminal → LAPSED (the clock in the fold)", s["state"] == "lapsed")

# ── 4 · LAPSED: expired lease, no terminal — THE C5.2 BAR, and NO REAPER ────────────────────────────
t_lap = "intent://global/acc-lapsed"
claim_intent(store, t_lap, by="agent://executor-2", session="run://turn9/member2",
             lease_until=iso(T0 + timedelta(seconds=30)), now=T0)
before = len(store.marks_for(t_lap))
s1 = compose_from_store(store, t_lap, now=T0 + timedelta(minutes=5))
s2 = compose_from_store(store, t_lap, now=T0 + timedelta(days=30))
check("THE BAR: expired lease + no terminal → LAPSED (derived)", s1["state"] == "lapsed")
check("…and 30 days later STILL lapsed with ZERO writes in between — no reaper process exists "
      "(compose is a READ; the mark thread is unchanged)",
      s2["state"] == "lapsed" and len(store.marks_for(t_lap)) == before)
s0 = compose_from_store(store, t_lap, now=T0 + timedelta(seconds=10))
check("the SAME thread composes RUNNING at an earlier clock (state is a function of (marks, now))",
      s0["state"] == "running")

# zero-length lease — the pour's honest synthesis ("liveness never proven")
t_zero = "intent://global/acc-zero-lease"
claim_intent(store, t_zero, by="agent://cloud-executor", session="run://historical",
             lease_until=iso(T0), now=T0, ts=iso(T0))
check("ZERO-LENGTH lease (lease_until == claim ts) composes to LAPSED one tick later — the 73 stuck-"
      "running land exactly this way",
      compose_from_store(store, t_zero, now=T0 + timedelta(seconds=1))["state"] == "lapsed")

# ── 5 · TERMINAL, each outcome — and terminal WINS over everything ──────────────────────────────────
for oc in TERMINAL_OUTCOMES:
    t = f"intent://global/acc-terminal-{oc}"
    claim_intent(store, t, by="agent://x", session="session://s/step/1",
                 lease_until=iso(T0 + timedelta(minutes=5)), now=T0)
    terminate(store, t, outcome=oc, result={"why": f"acc {oc}"}, now=T0 + timedelta(minutes=1))
    s = compose_from_store(store, t, now=T0 + timedelta(minutes=2))
    check(f"terminal({oc}) → TERMINAL with the outcome carried", s["state"] == "terminal" and s["outcome"] == oc)

t_win = "intent://global/acc-terminal-wins"
claim_intent(store, t_win, by="agent://x", session="session://s/step/1",
             lease_until=iso(T0 + timedelta(hours=9)), now=T0)
terminate(store, t_win, outcome="succeeded", now=T0 + timedelta(minutes=1))
check("terminal WINS over a still-live lease (no zombie 'running' after the end)",
      compose_from_store(store, t_win, now=T0 + timedelta(minutes=2))["state"] == "terminal")

# ── 6 · SUSPEND: parked (before any claim = the wizard pour; after a claim; resumed by re-claim) ────
t_wiz = "intent://global/acc-suspend-wizard"
suspend_intent(store, t_wiz, at_step="step-2", awaiting="operator input (wizard)", now=T0)
s = compose_from_store(store, t_wiz, now=T0 + timedelta(days=99))
check("suspend with NO claim (the historical wizard rows) → SUSPENDED, and NEVER lapses while parked",
      s["state"] == "suspended" and s["suspended"]["awaiting"] == "operator input (wizard)")

t_park = "intent://global/acc-suspend-parked"
claim_intent(store, t_park, by="agent://x", session="session://s/step/1",
             lease_until=iso(T0 + timedelta(minutes=1)), now=T0)
suspend_intent(store, t_park, at_step=3, awaiting="an external event", now=T0 + timedelta(seconds=30))
check("suspend NEWER than the claim → SUSPENDED (even long past the old lease — parked ≠ lapsed)",
      compose_from_store(store, t_park, now=T0 + timedelta(hours=5))["state"] == "suspended")
claim_intent(store, t_park, by="agent://y", session="session://s2/step/1",
             lease_until=iso(T0 + timedelta(hours=6)), now=T0 + timedelta(hours=5, minutes=1))
check("a LATER claim RESUMES a suspended intent → RUNNING (suspended stays re-claimable)",
      compose_from_store(store, t_park, now=T0 + timedelta(hours=5, minutes=2))["state"] == "running")

# ── 7 · TERMINAL-AFTER-LAPSE: a lapsed intent can still be honestly ENDED ───────────────────────────
t_tal = "intent://global/acc-terminal-after-lapse"
claim_intent(store, t_tal, by="agent://x", session="session://s/step/1",
             lease_until=iso(T0 + timedelta(seconds=5)), now=T0)
check("…lapsed first", compose_from_store(store, t_tal, now=T0 + timedelta(minutes=1))["state"] == "lapsed")
terminate(store, t_tal, outcome="cancelled", result={"why": "operator swept the zombie"},
          now=T0 + timedelta(minutes=2))
check("terminal AFTER lapse → TERMINAL (the end out-folds the expiry)",
      compose_from_store(store, t_tal, now=T0 + timedelta(minutes=3))["state"] == "terminal")

# ── 8 · RECLAIM-AFTER-LAPSE: lapsed is re-claimable — that IS the recovery path ─────────────────────
t_rec = "intent://global/acc-reclaim"
claim_intent(store, t_rec, by="agent://dead-executor", session="session://old/step/1",
             lease_until=iso(T0 + timedelta(seconds=5)), now=T0)
check("…lapsed", compose_from_store(store, t_rec, now=T0 + timedelta(minutes=1))["state"] == "lapsed")
claim_intent(store, t_rec, by="agent://fresh-executor", session="session://new/step/1",
             lease_seconds=600, now=T0 + timedelta(minutes=2))
s = compose_from_store(store, t_rec, now=T0 + timedelta(minutes=3))
check("re-claim after lapse → RUNNING under the NEW claim (by = the fresh executor)",
      s["state"] == "running" and s["claim"]["by"] == "agent://fresh-executor")

# ── 9 · the writers' GRAMMAR — fail-loud, with breadcrumbs ──────────────────────────────────────────
raises("claim on a TERMINAL intent REFUSES (ends end once; REWIND = fork + fresh claim)",
       lambda: claim_intent(store, t_win, by="agent://z", session="session://s/step/2",
                            lease_seconds=60, now=T0 + timedelta(minutes=9)), "TERMINAL")
raises("claim OVER a live lease REFUSES (a second live claim would double-execute)",
       lambda: claim_intent(store, t_rec, by="agent://z", session="session://s/step/2",
                            lease_seconds=60, now=T0 + timedelta(minutes=4)), "RUNNING")
raises("heartbeat with NO claim REFUSES (nothing to extend)",
       lambda: heartbeat(store, "intent://global/acc-nothing",
                         lease_until=iso(T0 + timedelta(minutes=9)), now=T0), "pending".upper())
raises("heartbeat on a LAPSED intent REFUSES (re-claim, never silently resurrect)",
       lambda: heartbeat(store, t_lap, lease_until=iso(T0 + timedelta(days=99)),
                         now=T0 + timedelta(minutes=10)), "LAPSED")
raises("DOUBLE terminal REFUSES (a second terminal would rewrite history)",
       lambda: terminate(store, t_win, outcome="failed", now=T0 + timedelta(minutes=9)), "ALREADY terminal")
raises("unknown outcome REFUSES (closed vocabulary)",
       lambda: terminate(store, t_pend, outcome="exploded", now=T0), "unknown outcome")
raises("claim without ANY lease REFUSES (the lease is the whole zombie-killer)",
       lambda: claim_intent(store, t_pend, by="a", session="s", now=T0), "exactly ONE")
raises("claim with BOTH lease forms REFUSES",
       lambda: claim_intent(store, t_pend, by="a", session="s", lease_until=iso(T0),
                            lease_seconds=5, now=T0), "exactly ONE")
raises("claim with empty `by` REFUSES (unattributed liveness is nobody's assertion)",
       lambda: claim_intent(store, t_pend, by="", session="s", lease_seconds=5, now=T0), "`by`")
raises("claim with empty `session` REFUSES (no live handle → can't be found alive or dead)",
       lambda: claim_intent(store, t_pend, by="a", session=" ", lease_seconds=5, now=T0), "`session`")
raises("a non-intent:// target REFUSES (the lifecycle grammar lives on intent addresses)",
       lambda: claim_intent(store, "board://item-1", by="a", session="s", lease_seconds=5, now=T0),
       "intent://")
raises("suspend with empty `awaiting` REFUSES (a suspend nobody can read is a parked zombie)",
       lambda: suspend_intent(store, t_pend, at_step=1, awaiting="", now=T0), "awaiting")
raises("suspend on a TERMINAL intent REFUSES (nothing left to park)",
       lambda: suspend_intent(store, t_win, at_step=1, awaiting="x", now=T0 + timedelta(minutes=9)),
       "TERMINAL")
raises("a malformed lease_until in the fold FAILS LOUD (an unreadable lease would compose a silent lie)",
       lambda: compose_state("intent://global/x",
                             [{"mark_type": "intent_claim", "ts": iso(T0), "by": "a", "session": "s",
                               "lease_until": "not-a-time"}], now=T0), "not ISO-parseable")

# pending is untouched by all those refusals — refusal means NO write
check("every refusal wrote NOTHING (fail-loud is refuse-before-write)",
      compose_from_store(store, t_pend, now=T0)["state"] == "pending"
      and len([m for m in store.marks_for(t_pend) if m.get("mark_type") in
               ("intent_claim", "intent_heartbeat", "intent_suspend", "intent_terminal")]) == 0)

print(f"\nPASS ({PASS} checks) — C5.2: state composes from marks + the clock; an expired lease IS lapsed; "
      "no reaper process exists (compose is a pure read).")
