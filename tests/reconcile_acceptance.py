"""tests/reconcile_acceptance.py — the (kind,address) reconcile (C3) + the burn-down rollup (C5).

The finding MODEL, built on the store (C1/C2). Two read-time folds, no model, no engine:
  · C3 reconcile — generalizes reachability's documented/new/stale into a universal (kind,address) upsert:
    given THIS run's findings vs the PRIOR set → known / new / resolved. A finding closes (resolved) when the
    detector no longer emits it (the gap got fixed). The disposition rides the known set forward.
  · C5 burn-down rollup — a read-time fold over the finding store ⨝ the disposition overlay → open vs
    accepted vs closed, by kind/disposition. The burn-down-toward-zero = open-finish findings (to_wire/
    to_build_ui/undispositioned); accepted (by-design/backend_only/voice_owned) is NOT open; the rollup is
    the run_stats-style read-time model (no maintained graph — own/reflect).

Verified by use against the real store primitives.
"""
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime import coherence_detect as cd

PASS = 0
def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")

# ── C3 · the reconcile, as a PURE fold over two finding lists (mirrors reachability documented/new/stale) ─
prior = [{"kind": "unwired-route", "address": "code://b/x"}, {"kind": "unwired-route", "address": "code://b/y"}]
current = [{"kind": "unwired-route", "address": "code://b/y"}, {"kind": "unwired-route", "address": "code://b/z"}]
rec = cd.reconcile(current, prior)
check("known = current ∩ prior  (the gap still stands)", rec["known"] == [("unwired-route", "code://b/y")])
check("new = current − prior  (a fresh disconnection)", rec["new"] == [("unwired-route", "code://b/z")])
check("resolved = prior − current  (the gap closed — detector no longer emits it)",
      rec["resolved"] == [("unwired-route", "code://b/x")])
check("net_change = |new| − |resolved|  (burn-down direction)", rec["net_change"] == 0)

# empty prior (first run): everything is new, nothing resolved
rec0 = cd.reconcile(current, [])
check("first run: all new, none known/resolved", len(rec0["new"]) == 2 and not rec0["known"] and not rec0["resolved"])

# ── C5 · the burn-down rollup over the real store ⨝ the disposition overlay ──────────────────────────
root = os.path.join(tempfile.mkdtemp(prefix="rollup-"), "store")
store = FsStore(root)
# three findings; dispose two, leave one open
store.append_finding({"kind": "unwired-route", "address": "code://b/knobs", "state": "built-no-caller", "source": "structural", "owner": "interface"})
store.append_finding({"kind": "unwired-route", "address": "code://b/voice", "state": "built-no-caller", "source": "structural", "owner": "voice"})
store.append_finding({"kind": "half-migration", "address": "code://b/status", "state": "candidate", "source": "semantic", "owner": "interface"})
store.append_disposition("unwired-route", "code://b/voice", "voice_owned", reason="voice session's", by="coherence")
store.append_disposition("half-migration", "code://b/status", "by-design", reason="backend lifecycle intentional", by="tim")
# knobs left undispositioned → OPEN

roll = cd.burn_down(store)
check("rollup dedups to 3 distinct findings", roll["total"] == 3)
check("OPEN = the undispositioned one (knobs) — the burn-down target", roll["open"] == 1)
check("ACCEPTED = the two dispositioned-accepted (voice_owned + by-design)", roll["accepted"] == 2)
check("by_kind counts both kinds", roll["by_kind"].get("unwired-route") == 2 and roll["by_kind"].get("half-migration") == 1)
check("by_disposition tracks the overlay", roll["by_disposition"].get("voice_owned") == 1 and roll["by_disposition"].get("by-design") == 1 and roll["by_disposition"].get("(open)") == 1)

# re-detection doesn't double-count (own/reflect: dedup by (kind,address) on read)
store.append_finding({"kind": "unwired-route", "address": "code://b/knobs", "state": "built-no-caller", "source": "structural", "owner": "interface"})
roll2 = cd.burn_down(store)
check("re-detection does NOT inflate the model (still 3 distinct, 1 open)", roll2["total"] == 3 and roll2["open"] == 1)

print(f"\nALL {PASS} CHECKS PASS — C3 reconcile (known/new/resolved + net_change) + C5 burn-down rollup "
      f"(open vs accepted, dedup-on-read). The finding model: a read-time fold, no maintained graph.")
