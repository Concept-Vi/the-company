"""tests/propose_affordance_acceptance.py — the OFFER-WITH-OPTIONS consent affordance (the "shall I?").

UNIFIED (2026-06-06 main-merge): the convergence shipped this as a parser-era `AFFORD:` TEXT directive
(`_parse_rhm_proposal`); main moved the RHM to NATIVE tool-calling and retired the text-directive trigger.
The capability is PRESERVED and unified: the RHM now OFFERS an action by calling a native `suggest` tool
(instead of emitting `AFFORD:` text) → chat() returns a structured `proposal` WITHOUT dispatching → the FE
renders an approvable card → approving fires /api/act. Same consent guarantee (propose must NOT execute),
modern trigger. The proposal carries an `options[]` + `direction` shape so the RICH layer (multi-option
generation + a steer→refine loop + interactive on-screen builds; see the Self-Modifying-Interface direction
doc §6B) extends it WITHOUT a re-trigger.

THE WHOLE POINT (the consent gate): proposing must NOT execute. Proven by spying on the dispatcher: a
`suggest` tool_call NEVER reaches `_dispatch_rhm_action` (no side-effect), `action` is None, and a
structured `proposal` rides on the response. An ORDINARY verb tool_call still execute-then-renders
(the native dispatch path untouched). Approve → Suite.act (what /api/act calls) — reuse, not a new path.

COMPANY_TEST_RUN is set so any surfaced draft is tagged test_origin (inbox hygiene, governance.py).
"""
import os, sys, json, tempfile, shutil

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


def tool_call(name, args):
    """The OpenAI tool_call shape chat() consumes (arguments is a JSON string)."""
    return {"function": {"name": name, "arguments": json.dumps(args)}}


_real_with_tools = fabric_client.complete_with_tools

store_dir = tempfile.mkdtemp(prefix="propose-affordance-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)
    suite._model_supports_tools = lambda model, base_url=None: True   # native tool-calling path (no live model)
    g = "i3-graph"
    suite.create_node(g, "constant", config={"value": "hello"}, node_id="c")
    suite.create_node(g, "uppercase", node_id="u")
    suite.connect(g, "c", "value", "u", "text")
    suite.set_mode("text-only")   # a normal (non-decide-for-me) interactive mode

    # ---- spy on the dispatcher so we can PROVE offering does not execute ----
    dispatched = []
    _real_dispatch = suite._dispatch_rhm_action
    def spy_dispatch(action, graph_id):
        dispatched.append(action)
        return _real_dispatch(action, graph_id)
    suite._dispatch_rhm_action = spy_dispatch

    # =====================================================================================
    # 0. the `suggest` tool is OFFERED whenever the RHM can act (the unified trigger exists).
    # =====================================================================================
    actx = suite._affordance_context(g, None)
    tool_names = {t["function"]["name"] for t in suite._rhm_tools("text-only", actx)}
    check("the RHM is offered the `suggest` tool (the unified offer-with-options affordance)",
          "suggest" in tool_names)
    check("`suggest` is offered ALONGSIDE the real verbs (not instead of them)",
          "show" in tool_names and "run" in tool_names)

    # =====================================================================================
    # 1+2. THE CONSENT GATE: a `suggest` tool_call emits a structured proposal and does NOT dispatch.
    #      The proposal carries a real whitelisted verb + a real address + the options/direction shape.
    # =====================================================================================
    dispatched.clear()
    fabric_client.complete_with_tools = lambda *a, **k: {
        "role": "assistant",
        "content": "Here's the inbox — want me to take you there?",
        "tool_calls": [tool_call("suggest", {"verb": "show", "address": "ui://chrome/inbox",
                                              "label": "Go to the inbox"})]}
    r = suite.chat("show me the inbox", g)

    check("the chat response carries a structured `proposal`", isinstance(r.get("proposal"), dict))
    prop = r.get("proposal") or {}
    check("the proposal carries the offered verb", prop.get("verb") == "show")
    check("the proposal carries the address", prop.get("address") == "ui://chrome/inbox")
    check("the proposal verb is a REAL whitelisted RHM verb (registry-is-truth)",
          prop.get("verb") in Suite.RHM_VERBS)
    # the rich-layer shape is carried from v1 (so multi-option + steer extends without a re-trigger):
    check("the proposal carries an options[] (rich-layer-ready; v1 = the single offer)",
          isinstance(prop.get("options"), list) and len(prop["options"]) >= 1
          and prop["options"][0].get("verb") == "show")
    check("the proposal carries the direction channel flag (operator may steer, not only yes/no)",
          prop.get("direction") is True)

    from contracts.ui_info import parse_ui_address
    ok_addr = True
    try:
        parse_ui_address(prop.get("address"))
    except Exception:
        ok_addr = False
    check("the proposal address is a grammar-valid ui:// address", ok_addr)

    # THE WHOLE POINT — offering executed NOTHING:
    check("offering did NOT dispatch the verb (consent gate: dispatcher never called)",
          dispatched == [])
    check("offering returned action=None (nothing ran)", r.get("action") is None)
    check("the prose reply survives alongside the proposal",
          (r.get("reply") or "").strip() != "")

    # =====================================================================================
    # 3. PRESERVED: an ordinary verb tool_call STILL execute-then-renders (native path untouched).
    # =====================================================================================
    dispatched.clear()
    fabric_client.complete_with_tools = lambda *a, **k: {
        "role": "assistant", "content": "", "tool_calls": [tool_call("run", {})]}
    r2 = suite.chat("run the graph", g)
    check("an ordinary verb tool_call STILL dispatches (execute-then-render preserved)",
          len(dispatched) == 1 and dispatched[0].get("verb") == "run")
    check("the dispatched turn returns an executed outcome (r.action.did=run)",
          r2.get("action") and r2["action"].get("did") == "run")
    check("a dispatched turn carries NO proposal (act and offer are distinct)",
          r2.get("proposal") is None)

    # =====================================================================================
    # 4. APPROVE → Suite.act (what /api/act calls) runs the verb EXACTLY as a direct act() call.
    #    The reuse proof: the approve path is the act dispatch path, not a new one.
    # =====================================================================================
    suite._dispatch_rhm_action = _real_dispatch   # drop the spy for the real run
    approved = suite.act(prop["verb"], g, address=prop["address"], args=prop.get("args"))
    direct = suite.act("show", g, address="ui://chrome/inbox")
    check("approving the proposal fires act() to the SAME outcome as a direct /api/act call (reuse)",
          approved["action"]["did"] == direct["action"]["did"] == "show"
          and "ui://chrome/inbox" in approved["action"]["targets"])

    # =====================================================================================
    # 5. GOVERNED: a `suggest` for a NON-whitelisted verb yields NO card (the offer is whitelist-gated,
    #    never a silent bad proposal) — the offer is governed by the SAME RHM_VERBS truth as dispatch.
    # =====================================================================================
    suite._dispatch_rhm_action = spy_dispatch   # re-attach the spy
    dispatched.clear()
    fabric_client.complete_with_tools = lambda *a, **k: {
        "role": "assistant", "content": "Sure.",
        "tool_calls": [tool_call("suggest", {"verb": "delete", "address": "ui://chrome/inbox"})]}
    r5 = suite.chat("delete that", g)
    check("a `suggest` for a non-whitelisted verb yields NO proposal (offer is governed, never a bad card)",
          r5.get("proposal") is None)
    check("a non-whitelisted offer still dispatches NOTHING (consent gate + whitelist intact)",
          dispatched == [] and r5.get("action") is None)

    # NOTE — the parser-era `_parse_rhm_proposal` (the retired AFFORD: text directive) remains on the
    # Suite as dead code from the merge; the live trigger is the native `suggest` tool proven above. The
    # RICH layer (multi-option generation, the steer→refine direction loop, interactive on-screen builds
    # for consequential verbs, configurable interactive-inbox) extends the options[]/direction shape —
    # see build-prep "Self-Modifying Interface … §6B. The RHM Consent-Interaction Model".

    print(f"\nALL {PASS} CHECKS PASS — offer-with-options consent affordance (unified into native "
          f"tool-calling): the RHM OFFERS, nothing runs until approve; act and offer stay distinct.")
finally:
    fabric_client.complete_with_tools = _real_with_tools
    shutil.rmtree(store_dir, ignore_errors=True)
