"""tests/interactive_inbox_acceptance.py — B3 · the configurable interactive-inbox (§6B QUEUE mode).

THE CRITERION (build-prep Operable Interface — Completion Criteria B3):
  "Any offer/build is configurable to defer to the inbox — and the inbox item stays a LIVE conversation
   with the RHM when revisited, not a dead queue."

What this proves BY USE (real Suite + temp FsStore + real nodes, NO model):
  1. defer_offer PERSISTS a live RHM offer (its verb/address/args/options/interactive/direction — the
     revival state) as a REAL inbox item in the SAME surfaced store every other lane uses (registry-is-truth,
     no parallel queue), with resolved=None so it lands in live_escalations.
  2. A FRESH Suite (new process simulation — a new Suite over the SAME store dir) reads it back unchanged.
  3. revive_offer reconstructs the interactive offer — enough to RE-OPEN the ProposeAffordance card
     (options + interactive + direction all intact).
  4. NOTHING is dispatched on defer or revive (the consent gate: the offer's verb runs only on a later
     approve; defer/revive never call act/dispatch). select≠approve, nothing-runs-until-approved PRESERVED.
  5. The ROUND-TRIP closes: resolving the deferred item (the approve path the FE runs after a successful
     act) clears it OUT of live_escalations — no ghost duplicate left behind.
  6. FAIL LOUD: a non-dict proposal, a proposal with neither verb nor options, and reviving a non-deferred
     /missing id all RAISE — never a silent no-op or a wrong-card revive.

COMPANY_TEST_RUN is set so any surfaced item is tagged test_origin (inbox hygiene, governance.py); the
test reads the RAW store (inbox.list / list_surfaced) so the hygiene filter doesn't hide our own items.
"""
import os, sys, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["COMPANY_TEST_RUN"] = "1"

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def fresh_suite(store_root):
    """A NEW Suite over an EXISTING store dir — simulates a process restart reading the persisted queue."""
    store = FsStore(store_root)
    reg = NodeRegistry(); reg.discover([NODES])
    return Suite(store, reg, nodes_dir=NODES), store


store_dir = tempfile.mkdtemp(prefix="interactive-inbox-test-")
try:
    store_root = os.path.join(store_dir, "store")
    suite, store = fresh_suite(store_root)
    g = "b3-graph"
    suite.create_node(g, "constant", config={"value": "hello"}, node_id="c")
    suite.create_node(g, "uppercase", node_id="u")
    suite.connect(g, "c", "value", "u", "text")

    # spy on the RHM dispatcher to PROVE defer/revive never execute the offered verb (the consent gate).
    dispatched = []
    _real_dispatch = suite._dispatch_rhm_action
    def spy_dispatch(action, graph_id):
        dispatched.append(action); return _real_dispatch(action, graph_id)
    suite._dispatch_rhm_action = spy_dispatch

    # the offer the operator parks — a B2-style INTERACTIVE build offer with multiple options + a steer
    # channel. This is exactly the proposal shape ProposeAffordance/approveProposal carry.
    offer = {
        "verb": "build", "address": "ui://canvas/u", "args": {"spec": "a summariser"},
        "interactive": True, "direction": True,
        "options": [
            {"verb": "build", "address": "ui://canvas/u", "args": {"spec": "a summariser"},
             "label": "summariser", "summary": "a node that summarises the input"},
            {"verb": "build", "address": "ui://canvas/u", "args": {"spec": "a classifier"},
             "label": "classifier", "summary": "a node that classifies the input"},
        ],
    }

    # =====================================================================================
    # 1. DEFER persists the offer as a REAL inbox item carrying the revival state.
    # =====================================================================================
    before = len(store.list_surfaced())
    res = suite.defer_offer(offer, note="parked while I think")
    sid = res["id"]
    after = store.list_surfaced()
    check("defer_offer returns the surfaced id of the queued item", isinstance(sid, str) and sid)
    check("defer_offer PERSISTED a new surfaced item (one more than before)", len(after) == before + 1)
    rec = store.get_surfaced(sid)
    check("the persisted item has the DISTINCT action class `deferred_offer` (not review/build)",
          rec and rec.get("action") == "deferred_offer")
    check("the persisted item is a LIVE escalation (resolved=None — it stays until the operator acts)",
          rec.get("resolved") is None)
    pp = (rec.get("payload") or {}).get("proposal") or {}
    check("the persisted proposal carries the verb (revival state)", pp.get("verb") == "build")
    check("the persisted proposal carries the address (revival state)", pp.get("address") == "ui://canvas/u")
    check("the persisted proposal carries the args (revival state)", pp.get("args") == {"spec": "a summariser"})
    check("the persisted proposal carries the interactive marker (B2 surface re-renders)",
          pp.get("interactive") is True)
    check("the persisted proposal carries the direction (steer) channel flag", pp.get("direction") is True)
    check("the persisted proposal carries ALL options[] (the comparison surface revives intact)",
          isinstance(pp.get("options"), list) and len(pp["options"]) == 2
          and pp["options"][1].get("label") == "classifier"
          and pp["options"][1].get("summary") == "a node that classifies the input")
    check("DEFER dispatched NOTHING (the consent gate: the offered verb did not run)", dispatched == [])

    # it lands in the operator's live lane (the inbox_lanes the FE reads). COMPANY_TEST_RUN tags it
    # test_origin so inbox_lanes filters it from the OPERATOR view — assert on the RAW escalation predicate
    # (resolved is None) which is what live_escalations keys on for a real (untagged) operator run.
    raw_live = [d for d in suite.inbox.list() if d.get("resolved") is None and d.get("action") == "deferred_offer"]
    check("the deferred offer is a live escalation in the one inbox store (no parallel queue)",
          any(d["id"] == sid for d in raw_live))

    # =====================================================================================
    # 2. A FRESH Suite (process-restart sim) reads the queued offer back.
    # =====================================================================================
    suite2, store2 = fresh_suite(store_root)
    rec2 = store2.get_surfaced(sid)
    check("a FRESH Suite over the same store reads the persisted deferred offer", rec2 is not None)
    revived = suite2.revive_offer(sid)
    rp = revived.get("proposal") or {}
    check("revive_offer (fresh Suite) reconstructs the verb", rp.get("verb") == "build")
    check("revive_offer reconstructs the interactive marker (re-opens the B2 surface)", rp.get("interactive") is True)
    check("revive_offer reconstructs the direction (steer) channel", rp.get("direction") is True)
    check("revive_offer reconstructs ALL options[] (the live conversation, not a dead card)",
          len(rp.get("options") or []) == 2 and rp["options"][0].get("label") == "summariser")
    check("revive_offer carries the note the operator left", revived.get("note") == "parked while I think")
    check("the revived item is still UNRESOLVED (reviving doesn't act/resolve)", revived.get("resolved") is None)

    # reviving dispatched nothing either (same Suite-level spy on suite2 to be sure).
    d2 = []
    _rd2 = suite2._dispatch_rhm_action
    suite2._dispatch_rhm_action = lambda a, gid: (d2.append(a) or _rd2(a, gid))
    _ = suite2.revive_offer(sid)
    check("REVIVE dispatched NOTHING (re-opening the card runs nothing — approve is the only dispatch)", d2 == [])

    # =====================================================================================
    # 3. ROUND-TRIP: resolving the item (the approve path the FE runs AFTER a successful act) clears it.
    #    (We resolve directly — the same operator-only resolve the FE calls with the threaded _sid. The
    #     act itself is the existing /api/act path proven by propose_affordance_acceptance; here we prove
    #     the QUEUE empties so no ghost lingers.)
    # =====================================================================================
    before_live = [d for d in store2.list_surfaced() if d.get("id") == sid][0]
    check("PRE-approve: the item is still live (resolved=None) — nothing ran from the queue alone",
          before_live.get("resolved") is None)
    suite2.resolve_surfaced(sid, "approve", "approved from the revived offer")
    rec3 = store2.get_surfaced(sid)
    check("POST-approve: the deferred offer is RESOLVED (leaves live_escalations — no ghost duplicate)",
          rec3.get("resolved") == "approve")
    still_live = [d for d in suite2.inbox.list() if d.get("resolved") is None and d.get("action") == "deferred_offer"]
    check("POST-approve: NO deferred_offer remains a live escalation (the queue emptied)", still_live == [])

    # =====================================================================================
    # 4. FAIL LOUD — never a silent no-op, never a wrong-card revive.
    # =====================================================================================
    def raises(fn, exc):
        try:
            fn(); return False
        except exc:
            return True
        except Exception:
            return False

    check("defer_offer(non-dict) RAISES (fail loud)", raises(lambda: suite.defer_offer("nope"), TypeError))
    check("defer_offer with neither verb nor options RAISES (nothing to revive)",
          raises(lambda: suite.defer_offer({"address": "ui://x"}), ValueError))
    check("revive_offer(missing id) RAISES (fail loud)", raises(lambda: suite.revive_offer("s999-nope"), KeyError))

    # reviving a NON-deferred surfaced item (e.g. a review item) must refuse — never a wrong-card revive.
    other = suite.surface_review({"title": "a real review", "kind": "idea"}, origin="generative")["id"]
    check("revive_offer on a NON-deferred-offer item RAISES (no wrong-card revive)",
          raises(lambda: suite.revive_offer(other), ValueError))

    # =====================================================================================
    # 5. a SINGLE-option (B1) offer defers + revives just as well (the surface maps generically).
    # =====================================================================================
    b1 = {"verb": "show", "address": "ui://chrome/inbox", "label": "go to the inbox", "direction": True}
    r_b1 = suite.defer_offer(b1)
    rev_b1 = suite.revive_offer(r_b1["id"])
    check("a B1 single-offer defers + revives (verb intact)", rev_b1["proposal"].get("verb") == "show")
    check("a B1 single-offer revives NOT interactive (stays the B1 click-to-act surface)",
          rev_b1["proposal"].get("interactive") is False)

    print(f"\nALL {PASS} CHECKS PASS — B3 configurable interactive-inbox: a deferred offer is a REAL queued, "
          f"revivable item in the one inbox store; a fresh process reads it; reviving re-opens the live "
          f"interactive offer; NOTHING dispatches until approve; the round-trip empties the queue; fail-loud.")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
