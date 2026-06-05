"""tests/propose_affordance_acceptance.py — I3: propose-affordance (the CONSENT gate, click #2).

NET-NEW (seams-rhm Seam 2 REFUTE): today the system is execute-then-render — a verb runs
server-side inside chat() and the FE renders the OUTCOME. There is no "proposed action awaiting
a click" affordance. I3 adds one: the RHM emits a structured {verb, address, args} PROPOSAL
alongside its prose, chat() returns it WITHOUT executing the verb, the FE renders an approvable
card, and APPROVING fires /api/act (the I2 endpoint) — the action runs ONLY on approve.

THE WHOLE POINT (the consent gate): proposing must NOT execute. This test proves it by spying on
the dispatcher: when the model emits the propose-affordance directive, `_dispatch_rhm_action` is
NEVER called (no side-effect), `action` is None, and a structured `proposal` rides on the response.

What this proves end-to-end (Suite level — the bridge route is a thin wrapper, grepped separately):
  1. A chat turn whose model-completion carries the propose-affordance directive emits a structured
     {verb, address} PROPOSAL on the response AND does NOT dispatch (the consent gate).
  2. The proposal carries a REAL whitelisted RHM verb (RHM_VERBS — registry-is-truth) and a REAL
     ui:// address (grammar-valid; registry-is-truth).
  3. PRESERVED: an ordinary ACTION: turn STILL execute-then-renders (the existing path untouched).
  4. Approve → Suite.act (what /api/act calls) runs the verb EXACTLY as a direct act() call does
     (reuse, not a new dispatch path) — same outcome shape.

COMPANY_TEST_RUN is set so any surfaced draft is tagged test_origin (inbox hygiene, governance.py).
"""
import os, sys, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["COMPANY_TEST_RUN"] = "1"

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
import fabric.client as fabric_client

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def stub_completion(text):
    """Replace fabric.client.complete so chat() gets a DETERMINISTIC model output (no live model)."""
    fabric_client.complete = lambda *a, **k: text


_real_complete = fabric_client.complete

store_dir = tempfile.mkdtemp(prefix="propose-affordance-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)
    g = "i3-graph"
    suite.create_node(g, "constant", config={"value": "hello"}, node_id="c")
    suite.create_node(g, "uppercase", node_id="u")
    suite.connect(g, "c", "value", "u", "text")
    suite.set_mode("text-only")   # a normal (non-decide-for-me) mode — the execute-then-render path

    # ---- spy on the dispatcher so we can PROVE proposing does not execute ----
    dispatched = []
    _real_dispatch = suite._dispatch_rhm_action
    def spy_dispatch(action, graph_id):
        dispatched.append(action)
        return _real_dispatch(action, graph_id)
    suite._dispatch_rhm_action = spy_dispatch

    # =====================================================================================
    # 1+2. THE CONSENT GATE: a propose-affordance directive emits a structured proposal and
    #      does NOT dispatch. The proposal carries a real whitelisted verb + a real address.
    # =====================================================================================
    check("Suite has a propose-affordance parser (_parse_rhm_proposal)",
          hasattr(suite, "_parse_rhm_proposal") and callable(suite._parse_rhm_proposal))

    dispatched.clear()
    stub_completion("Here's the inbox — want me to take you there?\nAFFORD: show ui://chrome/inbox")
    r = suite.chat("show me the inbox", g)

    check("the chat response carries a structured `proposal`", isinstance(r.get("proposal"), dict))
    prop = r.get("proposal") or {}
    check("the proposal carries the verb", prop.get("verb") == "show")
    check("the proposal carries the address", prop.get("address") == "ui://chrome/inbox")
    check("the proposal verb is a REAL whitelisted RHM verb (registry-is-truth)",
          prop.get("verb") in Suite.RHM_VERBS)

    from contracts.ui_info import parse_ui_address
    ok_addr = True
    try:
        parse_ui_address(prop.get("address"))
    except Exception:
        ok_addr = False
    check("the proposal address is a grammar-valid ui:// address", ok_addr)

    # THE WHOLE POINT — proposing executed NOTHING:
    check("proposing did NOT dispatch the verb (consent gate: dispatcher never called)",
          dispatched == [])
    check("proposing returned action=None (nothing ran)", r.get("action") is None)
    check("the prose reply survives alongside the proposal (the directive is stripped from prose)",
          "AFFORD:" not in (r.get("reply") or "") and (r.get("reply") or "").strip() != "")

    # =====================================================================================
    # 3. PRESERVED: an ordinary ACTION: turn STILL execute-then-renders (existing path intact).
    # =====================================================================================
    dispatched.clear()
    stub_completion("Recomputing the graph now.\nACTION: run")
    r2 = suite.chat("run the graph", g)
    check("an ordinary ACTION: turn STILL dispatches (execute-then-render preserved)",
          len(dispatched) == 1 and dispatched[0].get("verb") == "run")
    check("the ACTION: turn returns an executed outcome (r.action.did=run)",
          r2.get("action") and r2["action"].get("did") == "run")
    check("an ACTION: turn carries NO proposal (the two paths are distinct)",
          r2.get("proposal") is None)

    # =====================================================================================
    # 4. APPROVE → Suite.act (what /api/act calls) runs the verb EXACTLY as a direct act() call.
    #    This is the reuse proof: the approve path is the I2 dispatch path, not a new one.
    # =====================================================================================
    suite._dispatch_rhm_action = _real_dispatch   # drop the spy for the real run
    approved = suite.act(prop["verb"], g, address=prop["address"], args=prop.get("args"))
    direct = suite.act("show", g, address="ui://chrome/inbox")
    check("approving the proposal fires act() to the SAME outcome as a direct /api/act call (reuse)",
          approved["action"]["did"] == direct["action"]["did"] == "show"
          and "ui://chrome/inbox" in approved["action"]["targets"])

    # =====================================================================================
    # 5. A malformed model-emitted ui:// address DROPS the proposal and KEEPS the prose (consistent
    #    with the verb philosophy: a bad model output never kills the whole turn — it rides through /
    #    fails loud at the click, or here yields no card; the operator still gets the answer).
    # =====================================================================================
    suite._dispatch_rhm_action = spy_dispatch   # re-attach the spy
    dispatched.clear()
    # `ui://` alone is grammatically malformed (no segments) — parse_ui_address RAISES on it. The
    # parser must catch that and DROP the proposal (keep the prose), never let it 400 the turn.
    stub_completion("Sure, here you go.\nAFFORD: show ui://")
    r5 = suite.chat("show me that", g)
    check("a malformed proposed address yields NO proposal (the turn is not killed)",
          r5.get("proposal") is None)
    check("the prose answer survives a malformed proposed address (no 400, no lost turn)",
          (r5.get("reply") or "").strip() != "" and "AFFORD:" not in (r5.get("reply") or ""))
    check("a malformed proposed address still dispatches NOTHING (consent gate intact)",
          dispatched == [] and r5.get("action") is None)

    # NOTE on REJECT/DISMISS: dismissing a card is PURE FRONT-END state (setProposal(null)) with NO
    # backend call — there is nothing server-side to assert. The consent guarantee it rests on is the
    # one proven above: at propose time NOTHING dispatched (#1), so a dropped card leaves the system
    # exactly as it was. (FE dismiss behavior is verified by the loop's browser pass.)

    print(f"\nALL {PASS} CHECKS PASS — I3 propose-affordance: the RHM proposes, the action runs ONLY on approve")
finally:
    fabric_client.complete = _real_complete
    shutil.rmtree(store_dir, ignore_errors=True)
