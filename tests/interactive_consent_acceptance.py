"""tests/interactive_consent_acceptance.py — B2: the ON-SCREEN INTERACTIVE BUILD consent surface.

THE LANE (Operable Interface, Completion Criteria B2 · direction doc §6B.2 mode 3):
A CONSEQUENTIAL verb (build/panel/extend) must come ON-SCREEN, INTERACTIVE — NOT a silent inbox-drop:
the RHM offers MULTIPLE real options to compare + choose + discuss (chat-until-approve), and the chosen
one drives the EXISTING dispatch (the /api/act path) only on the operator's explicit approve. NOTHING runs
until approved. This is built ON the B1 substrate (the native `suggest` tool → a structured `proposal`
carrying options[]/direction → the FE card → approve fires /api/act = Suite.act). B2 widens `suggest` to
carry an `options[]` array of alternatives and an `interactive` marker (derived from the verb class —
registry-truth, never fabricated), and proves the consent invariant end to end.

THE DISCRIMINATOR PROVEN HERE (B2 vs a wider B1):
  • a consequential `suggest` yields a MULTI-OPTION offer marked `interactive` (the comparison surface);
  • each option carries the DISTINGUISHING content (label + summary), not just the verb;
  • offering dispatches NOTHING (the consent gate — the dispatcher is never called by `suggest`);
  • approving exactly ONE chosen option fires Suite.act = the same dispatch path a direct /api/act uses,
    and for build composes the pipeline, for panel/extend surfaces a CONFIRM draft (a SECOND approval) —
    nothing self-applies;
  • fail-loud: a non-whitelisted option is dropped (never a bad card); an all-bad offer yields no card.

No live model: the model's tool_call is synthesized (the plumbing is what B2 owns; multi-option GENERATION
QUALITY is the live-model half — flagged needs-tim, not asserted here). Real Suite + temp FsStore + real nodes.
COMPANY_TEST_RUN tags any surfaced draft test_origin (inbox hygiene, governance.py).
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

store_dir = tempfile.mkdtemp(prefix="interactive-consent-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)
    suite._model_supports_tools = lambda model, base_url=None: True   # native tool-calling path (no live model)
    g = "b2-graph"
    # a non-empty graph in a build-ish mode so build/panel/extend are OFFERED (available_verbs).
    suite.create_node(g, "constant", config={"value": "hi"}, node_id="c")
    suite.set_mode("text-only")   # a build-ish interactive mode (build/panel/extend offered)

    # spy on the dispatcher so we PROVE offering does not execute.
    dispatched = []
    _real_dispatch = suite._dispatch_rhm_action
    def spy_dispatch(action, graph_id):
        dispatched.append(action)
        return _real_dispatch(action, graph_id)
    suite._dispatch_rhm_action = spy_dispatch

    # =====================================================================================
    # 0. the `suggest` tool now advertises the multi-option `options[]` shape for consequential verbs.
    # =====================================================================================
    actx = suite._affordance_context(g, None)
    tools = suite._rhm_tools("text-only", actx)
    sug = next((t["function"] for t in tools if t["function"]["name"] == "suggest"), None)
    check("the RHM is offered the `suggest` tool", sug is not None)
    check("`suggest` advertises an `options[]` parameter (B2 multi-option shape)",
          "options" in sug["parameters"]["properties"])
    opt_item = sug["parameters"]["properties"]["options"].get("items", {}).get("properties", {})
    check("each option declares a `summary` (the distinguishing content the operator chooses by)",
          "summary" in opt_item)
    check("consequential verbs are OFFERED in this mode (build/panel/extend reachable)",
          {"build", "panel", "extend"} <= {t["function"]["name"] for t in tools})

    # =====================================================================================
    # 1. A CONSEQUENTIAL `suggest` with options[] → a MULTI-OPTION INTERACTIVE proposal, no dispatch.
    #    Three panel designs — same verb, DIFFERENT summary (the realistic consequential case).
    # =====================================================================================
    dispatched.clear()
    three_panels = {"options": [
        {"verb": "panel", "label": "Compact knobs", "summary": "model + temperature only, one row",
         "args": {"name": "rhm-quick", "spec": "model, temperature"}},
        {"verb": "panel", "label": "Full lab", "summary": "model, persona, mode, voice, roles — every slot",
         "args": {"name": "rhm-full", "spec": "model, persona, mode, voice, roles"}},
        {"verb": "panel", "label": "Voice-first", "summary": "STT ear + TTS engine + voice toggle, grouped",
         "args": {"name": "rhm-voice", "spec": "stt, tts_engine, voice_enabled"}},
    ]}
    fabric_client.complete_with_tools = lambda *a, **k: {
        "role": "assistant",
        "content": "I can add a settings panel a few ways — which fits?",
        "tool_calls": [tool_call("suggest", three_panels)]}
    r = suite.chat("add a settings panel for the RHM", g)
    prop = r.get("proposal") or {}

    check("the chat response carries a structured `proposal`", isinstance(r.get("proposal"), dict))
    check("the offer is marked INTERACTIVE (consequential verb → the on-screen comparison surface)",
          prop.get("interactive") is True)
    check("the proposal carries MULTIPLE options (the alternatives to compare)",
          isinstance(prop.get("options"), list) and len(prop["options"]) == 3)
    check("each option carries its DISTINGUISHING summary (not just the verb)",
          all(o.get("summary") for o in prop["options"])
          and len({o["summary"] for o in prop["options"]}) == 3)
    check("each option carries a human label", all(o.get("label") for o in prop["options"]))
    check("each option's verb is a REAL whitelisted RHM verb (registry-is-truth)",
          all(o["verb"] in Suite.RHM_VERBS for o in prop["options"]))
    check("the offer carries the direction/steer channel (discuss-to-refine, not yes/no)",
          prop.get("direction") is True)

    # THE CONSENT GATE — offering a consequential build executed NOTHING:
    check("offering did NOT dispatch ANY verb (consent gate: dispatcher never called)", dispatched == [])
    check("offering returned action=None (nothing ran — not even surfaced a draft)", r.get("action") is None)
    check("the prose reply survives alongside the options", (r.get("reply") or "").strip() != "")

    # =====================================================================================
    # 2. SELECT ≠ APPROVE: the FE selects locally (no backend call); only an EXPLICIT approve dispatches.
    #    The backend invariant that GUARANTEES this: there is NO route by which carrying options runs one;
    #    the ONLY thing that dispatches a chosen option is a deliberate Suite.act on it (the approve commit).
    #    (The FE select-then-approve interaction is verified BY USE in chrome — see the report.)
    # =====================================================================================
    dispatched.clear()
    # re-derive the offer (a fresh turn) WITHOUT approving anything → still zero dispatch.
    fabric_client.complete_with_tools = lambda *a, **k: {
        "role": "assistant", "content": "same options", "tool_calls": [tool_call("suggest", three_panels)]}
    r_again = suite.chat("show me again", g)
    check("re-offering (the operator merely looking / steering) dispatches NOTHING", dispatched == [])
    check("the re-offer is still interactive multi-option", (r_again.get("proposal") or {}).get("interactive") is True)

    # =====================================================================================
    # 3. APPROVE the CHOSEN option → Suite.act (what /api/act calls) — for panel, the CONFIRM-class verb
    #    SURFACES a draft for a SECOND operator approval, NEVER self-applies. (propose_panel may also ASK
    #    when the spec needs registry info it doesn't have — PoLR fail-loud; that ALSO surfaces an item and
    #    self-applies nothing. The B2 invariant we assert: a consequential approve surfaces for review and
    #    never self-applies — both `panel` and `ask` honour it. No model is mocked for propose_panel, so we
    #    accept either deterministic outcome.) The chosen one (and ONLY it) drives the dispatch.
    # =====================================================================================
    suite._dispatch_rhm_action = _real_dispatch   # drop the spy for the real run
    chosen = prop["options"][1]                   # the operator picked "Full lab"
    before = {d["id"] for d in suite.inbox.list()}
    approved = suite.act(chosen["verb"], g, address=chosen.get("address"), args=chosen.get("args"))
    did = (approved.get("action") or {}).get("did")
    check("approving the chosen panel option fires act() to a CONFIRM-class outcome (panel-draft or ask — never a self-apply)",
          did in ("panel", "ask"))
    after = suite.inbox.list()
    new_items = [d for d in after if d["id"] not in before]
    check("approving the consequential option SURFACES an item for a SECOND operator approval (never self-applies)",
          len(new_items) == 1 and new_items[0].get("resolved") is None)
    # NB: the EXACT payload (the generated panel JSON) is the model's output — propose_panel invokes a model
    # we deliberately do NOT mock (the lane is real-nodes-no-model), so the surfaced draft's contents are
    # non-deterministic. We assert the model-INDEPENDENT consent invariant only (surfaces / never self-applies).
    # The "the CHOSEN option (and only it) drives the dispatch" proof is the model-free BUILD case below.

    # =====================================================================================
    # 4. A CONSEQUENTIAL `build` offer with options → interactive; approve composes the pipeline (AUTO).
    # =====================================================================================
    suite._dispatch_rhm_action = spy_dispatch
    dispatched.clear()
    build_opts = {"options": [
        {"verb": "build", "label": "Uppercase chain",
         "summary": "constant → uppercase (loud the value)",
         "args": {"steps": [{"as": "u", "type": "uppercase"}]}},
        {"verb": "build", "label": "Word count",
         "summary": "constant → wordcount (measure it)",
         "args": {"steps": [{"as": "w", "type": "wordcount"}]}},
    ]}
    fabric_client.complete_with_tools = lambda *a, **k: {
        "role": "assistant", "content": "two ways to extend it:", "tool_calls": [tool_call("suggest", build_opts)]}
    rb = suite.chat("extend the graph", g)
    pb = rb.get("proposal") or {}
    check("a multi-option BUILD offer is interactive", pb.get("interactive") is True)
    check("the build offer carries both approaches with distinct summaries",
          len(pb.get("options", [])) == 2 and pb["options"][0]["summary"] != pb["options"][1]["summary"])
    check("offering the builds dispatched NOTHING (consent gate)", dispatched == [])

    suite._dispatch_rhm_action = _real_dispatch
    nodes_before = len(suite.state(g)["nodes"])
    ch = pb["options"][0]
    built = suite.act(ch["verb"], g, address=ch.get("address"), args=ch.get("args"))
    check("approving the chosen build composes the pipeline (build did=build, AUTO)",
          built.get("action") and built["action"].get("did") == "build")
    check("the chosen build ACTUALLY added the node (the chosen option drove the dispatch)",
          len(suite.state(g)["nodes"]) == nodes_before + 1)

    # =====================================================================================
    # 5. FAIL-LOUD / registry-truth: a non-whitelisted option is DROPPED; an all-bad offer yields NO card.
    # =====================================================================================
    suite._dispatch_rhm_action = spy_dispatch
    dispatched.clear()
    mixed = {"options": [
        {"verb": "panel", "label": "good", "summary": "a real panel", "args": {"name": "ok", "spec": "x"}},
        {"verb": "delete_node", "label": "evil", "summary": "should never card"},   # not whitelisted
    ]}
    fabric_client.complete_with_tools = lambda *a, **k: {
        "role": "assistant", "content": "", "tool_calls": [tool_call("suggest", mixed)]}
    rm = suite.chat("do a thing", g)
    pm = rm.get("proposal") or {}
    check("a non-whitelisted option is DROPPED from the offer (registry-truth, never a bad card)",
          len(pm.get("options", [])) == 1 and pm["options"][0]["verb"] == "panel")
    check("the dropped offer still dispatched nothing", dispatched == [])

    dispatched.clear()
    allbad = {"options": [{"verb": "delete_node", "label": "x"}, {"verb": "apply_node", "label": "y"}]}
    fabric_client.complete_with_tools = lambda *a, **k: {
        "role": "assistant", "content": "noted.", "tool_calls": [tool_call("suggest", allbad)]}
    ra = suite.chat("another thing", g)
    check("an ALL-non-whitelisted offer yields NO proposal card (fail-loud: no fiction)",
          ra.get("proposal") is None)
    check("and dispatched nothing", dispatched == [])

    # =====================================================================================
    # 6. PRESERVED — B1 (single, non-consequential) offer is UNCHANGED (not marked interactive).
    # =====================================================================================
    dispatched.clear()
    fabric_client.complete_with_tools = lambda *a, **k: {
        "role": "assistant", "content": "want to look?",
        "tool_calls": [tool_call("suggest", {"verb": "show", "address": "ui://chrome/inbox", "label": "Inbox"})]}
    r1 = suite.chat("show inbox", g)
    p1 = r1.get("proposal") or {}
    check("a single non-consequential offer stays B1 (NOT interactive — the light card)",
          p1.get("interactive") is False and len(p1.get("options", [])) == 1)
    check("the B1 offer still carries options[]/direction (the shape the FE maps generically)",
          isinstance(p1.get("options"), list) and p1.get("direction") is True)
    check("the B1 single offer dispatched nothing (consent preserved)", dispatched == [])

finally:
    fabric_client.complete_with_tools = _real_with_tools
    shutil.rmtree(store_dir, ignore_errors=True)

print(f"\nINTERACTIVE-CONSENT (B2) ACCEPTANCE: {PASS} checks passed")
