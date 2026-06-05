"""tests/addr_history_acceptance.py — L3 · addressed history/audit (§21.7#1).

THE PRINCIPLE (§21.7#1): clicking an element shows everything that happened AT ITS ADDRESS.
The store side is genuinely free — S2 already stamped ~20 emit sites so every event at an
addressable locus carries an additive `address` field (a `ui://` or `run://` ref; see
event_address_acceptance.py). L3 WIDENS the existing audit-view machinery: `decision_view`
already filters `events_since(-1)` on `e.get("surfaced")==sid`; the addressed analogue filters
the SAME tail on `e.get("address")==addr`.

THE SHAPE OF THE WIDEN (advisor + guide PRESERVES): a SIBLING method `address_view(address)`,
mirroring how `session_view` "clones decision_view but filters on `session`" (suite.py). This
leaves `decision_view`'s `sid` path LITERALLY UNTOUCHED — the strongest satisfaction of the
HARD preserve-constraint. The query address is S0-validated (reuse `parse_ui_address`, matching
`annotations_at`/`chats_at`) where it enters; the stored events are NOT re-validated — they are
just compared. A stored `run://` event simply won't equal a `ui://` query, so it is filtered out
correctly: there is nothing to special-case about events carrying `run://`.

SCOPE BOUNDARY (deliberate, NOT an omission): `address_view` accepts `ui://` queries only — the
grammar `parse_ui_address` enforces. This matches the FE: "clicking an element" fires the
indicate flow ONLY for `ui://`-stamped DOM elements (useAppController). `ui://` history is
genuinely rich (chrome/inbox/chat/workshop events + every I6/I7 addressed comment & chat), so
`ui://`-complete IS complete for L3's principle. A `run://` node's history is reached by node
selection, a different mechanism.

WHAT THIS TEST PROVES (RED-first):
  1. address_view(addr) returns EXACTLY the events stamped at `addr`, in chronological order.
  2. ISOLATION: events at a DIFFERENT address are NOT returned (the address IS the key).
  3. PRESERVE: decision_view(sid) still filters on `surfaced==sid` exactly as before — the
     sid path is untouched.
  4. FAIL-LOUD: a malformed / non-ui:// query address RAISES (the S0 grammar gate), never
     silently returns [] (which a caller could read as "no history").
"""
import os, sys, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

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


store_dir = tempfile.mkdtemp(prefix="addrhist-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    # The sibling exists (the widen is a sibling, decision_view untouched).
    check("Suite.address_view exists (the addressed-history sibling of decision_view)",
          hasattr(suite, "address_view") and callable(suite.address_view))

    # --- emit a couple of addressed events AT ONE address via the real annotate path ---
    # annotate(address, text) writes an annotation AND emits an addressed `annotation` event
    # (suite.py: self._emit("annotation", ..., address=address)). Two comments at one locus →
    # two addressed events at that locus, in order.
    A = "ui://inbox/build-review"
    suite.annotate(A, "first comment here")
    suite.annotate(A, "second comment here")

    # a DIFFERENT address — must NOT leak into A's history (the isolation proof).
    B = "ui://workshop/self-changes"
    suite.annotate(B, "an unrelated comment elsewhere")

    view = suite.address_view(A)
    check("address_view returns a dict keyed by the queried address",
          isinstance(view, dict) and view.get("address") == A)
    traj = view.get("trajectory")
    check("address_view returns a trajectory list", isinstance(traj, list))

    # EXACTLY the two events at A come back (no more, no fewer).
    at_a = [e for e in traj if e.get("kind") == "annotation"]
    check("address_view returns EXACTLY the two annotation events emitted at A",
          len(at_a) == 2)
    check("every returned event is stamped at the queried address (the address IS the key)",
          all(e.get("address") == A for e in traj))

    # IN ORDER — chronological by seq (the audit must not scramble the path).
    seqs = [e.get("seq", 0) for e in traj]
    check("the addressed history is in chronological order (oldest-first by seq)",
          seqs == sorted(seqs))
    summaries = [e.get("summary", "") for e in at_a]
    check("the two comments come back in emit order (first before second)",
          "first comment here"[:20] in summaries[0] and "second comment here"[:20] in summaries[1])

    # ISOLATION — B's comment is NOT in A's view, and A's are NOT in B's.
    check("B's event does NOT leak into A's addressed history (isolation)",
          all("unrelated comment elsewhere"[:20] not in e.get("summary", "") for e in traj))
    view_b = suite.address_view(B)
    b_anns = [e for e in view_b["trajectory"] if e.get("kind") == "annotation"]
    check("address_view(B) returns ONLY B's event (isolation, the other direction)",
          len(b_anns) == 1 and "unrelated comment elsewhere"[:20] in b_anns[0].get("summary", ""))

    # --- PRESERVE: decision_view's existing sid path is UNTOUCHED ---
    # Surface an item + resolve it → it accrues `surfaced==sid` events. decision_view(sid) must
    # still reconstruct that trajectory by `surfaced`, exactly as before L3.
    sid = suite.inbox.surface("idea", {"title": "a thought"}, default="reject")
    suite._emit("proposed", "an idea surfaced", surfaced=sid, address="ui://chrome/inbox")
    suite.resolve_surfaced(sid, "approve", reason="go")
    dview = suite.decision_view(sid)
    check("decision_view(sid) still returns a dict with the item + trajectory (sid path preserved)",
          isinstance(dview, dict) and dview.get("id") == sid and isinstance(dview.get("trajectory"), list))
    check("decision_view(sid) STILL filters on surfaced==sid (not on address) — every event is the item's",
          dview["trajectory"] and all(e.get("surfaced") == sid for e in dview["trajectory"]))
    # and the sid trajectory is in order (the preserved behaviour, unchanged).
    dseqs = [e.get("seq", 0) for e in dview["trajectory"]]
    check("decision_view(sid)'s trajectory is in chronological order (unchanged)",
          dseqs == sorted(dseqs))

    # --- FAIL-LOUD: a malformed / non-ui:// query RAISES (the S0 gate), never silent [] ---
    for bad in ["not-an-address", "run://graph/node", "ui://", ""]:
        raised = False
        try:
            suite.address_view(bad)
        except (ValueError, TypeError):
            raised = True
        check(f"address_view({bad!r}) RAISES on a non-ui:// / malformed query (fail-loud S0 gate)", raised)

    print(f"\nALL {PASS} CHECKS PASS — L3 addressed history: address_view filters the event tail by "
          f"`address` (sibling, sid path untouched), exact + isolated + ordered, ui://-validated, fail-loud.")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
