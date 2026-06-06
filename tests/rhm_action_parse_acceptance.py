"""tests/rhm_action_parse_acceptance.py — RHM NATIVE TOOL-CALLING dispatch + affordances.

The RHM now ACTS through NATIVE tool-calling, not a hand-typed `ACTION:` line. The fleet chat
models all support native tools (ollama /api/show → capabilities contains "tools"); only an
embedder like nomic-embed-text does not. So:

  • a model's `tool_calls` (OpenAI shape {function:{name, arguments}}) maps — via the SAME
    `_json_obj_to_action` the chat loop uses — to the dispatcher's action dict;
  • the ONE whitelist still lives in `_dispatch_rhm_action` (RHM_VERBS), so a forbidden verb
    emitted as a tool_call is REFUSED end-to-end (E6 — proven parse→dispatch, node not deleted);
  • an empty-content tool_call still yields a NON-BLANK reply (the confirmation fold) — critical
    because a native-tool-call model often emits NO prose, only the call;
  • the RHM model is CAPABILITY-GATED FIRST: a non-tool model (nomic-embed-text) is refused
    FAIL-LOUD — a legible turn, NO model call, NO fallback (rule 4);
  • the AFFORDANCE SET (which verbs are OFFERED) is correct per mode×context (mode-primary,
    context-refines), and narrowing the OFFER never weakens the gate.

THE INVARIANT THAT MUST HOLD (E6, AGENTS.md rule 9): the affordance layer narrows what is
OFFERED; the dispatcher's whitelist is the real gate. A forbidden verb is refused regardless.
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


def tool_call(name, arguments):
    """Build an OpenAI-shape tool_call. `arguments` is a JSON STRING (as the API returns it)."""
    import json
    return {"id": "call_1", "type": "function",
            "function": {"name": name, "arguments": json.dumps(arguments)}}


store_dir = tempfile.mkdtemp(prefix="rhm-tool-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    # ============================================================================================
    # (a) a native tool_call → the correct action dict (via _json_obj_to_action — the SAME path the
    #     chat loop feeds each tool_call through). Args are a JSON string, as the API returns them.
    # ============================================================================================
    BUILD_STEPS = [{"as": "a", "type": "constant", "config": {"value": "x"}},
                   {"as": "u", "type": "uppercase"},
                   {"wire": "a.value -> u.text"}]
    act_build = suite._json_obj_to_action(
        {"name": "build", "arguments": __import__("json").dumps({"steps": BUILD_STEPS})}, "build")
    check("(a) build tool_call → action dict with the 3 steps",
          act_build["verb"] == "build" and isinstance(act_build["steps"], list) and len(act_build["steps"]) == 3)

    act_consult = suite._json_obj_to_action(
        {"name": "consult", "arguments": __import__("json").dumps({"query": "how does the memo gate work"})}, "consult")
    check("(a) consult tool_call → action dict carrying the query",
          act_consult["verb"] == "consult" and "memo gate" in act_consult["query"])

    act_show = suite._json_obj_to_action(
        {"name": "show", "arguments": __import__("json").dumps({"targets": ["answer", "u"]})}, "show")
    check("(a) show tool_call → action dict carrying the targets list",
          act_show["verb"] == "show" and act_show["targets"] == ["answer", "u"])

    # ============================================================================================
    # (b) THE WHITELIST HOLDS — a forbidden `delete` tool_call is mapped to an action by the shape
    #     mapper, but REFUSED by the dispatcher end-to-end (did==none); the node is NOT deleted.
    # ============================================================================================
    g = "tool-sec"
    suite.create_node(g, "constant", config={"value": "x"}, node_id="c")
    act_del = suite._json_obj_to_action(
        {"name": "delete", "arguments": __import__("json").dumps({"node": "c"})}, "delete")
    r_del = suite._dispatch_rhm_action(act_del, g)
    check("(b) forbidden 'delete' tool_call is REFUSED end-to-end (whitelist in dispatcher, did==none)",
          r_del["did"] == "none")
    check("(b) the node was NOT deleted by the refused delete", any(n.id == "c" for n in suite._load(g).nodes))

    # and an allowed verb from a tool_call DISPATCHES (it actually acts) — the whole point.
    suite.create_node(g, "uppercase", node_id="u"); suite.connect(g, "c", "value", "u", "text")
    r_run = suite._dispatch_rhm_action(suite._json_obj_to_action({"name": "run", "arguments": "{}"}, "run"), g)
    check("(b) an allowed verb (run) from a tool_call DISPATCHES (it acts)", r_run["did"] == "run")

    # ============================================================================================
    # (c) AFFORDANCE-SET correctness per mode×context (mode-primary, context-refines). All from the
    #     ONE registry; the rendered verb list + the tools array both read available_verbs().
    # ============================================================================================
    full_ctx = {"graph_nonempty": True, "inbox_pending": False, "node_selected": False}
    empty_ctx = {"graph_nonempty": False, "inbox_pending": False, "node_selected": False}

    # listening: all 7 verbs offered (graph non-empty so run is in)
    av_listen = suite.available_verbs("listening", full_ctx)
    check("(c) listening (non-empty graph) offers ALL 7 verbs", set(av_listen) == set(suite.RHM_VERBS))

    # listening with an EMPTY graph: run is predicate-gated OUT (no point recomputing nothing)
    av_listen_empty = suite.available_verbs("listening", empty_ctx)
    check("(c) listening (EMPTY graph) drops `run` (predicate context-refines)",
          "run" not in av_listen_empty and "build" in av_listen_empty)

    # watch-and-react: an OBSERVE mode — show + consult ONLY. NO build cluster (it doesn't compose) AND
    # NO run (it observes/comments, it does NOT recompute the graph — spec said show+consult only).
    av_watch = suite.available_verbs("watch-and-react", full_ctx)
    check("(c) watch-and-react offers ONLY show+consult (no build cluster, NO run — observe mode)",
          set(av_watch) == {"consult", "show"})

    # walkthrough: a GUIDE mode — show + consult ONLY (same rationale: it guides/consults, doesn't recompute).
    av_walk = suite.available_verbs("walkthrough", full_ctx)
    check("(c) walkthrough offers ONLY show+consult (guide mode — NO run)",
          set(av_walk) == {"consult", "show"})

    # focus: minimal — run + show only (no consult, no build cluster)
    av_focus = suite.available_verbs("focus", full_ctx)
    check("(c) focus offers only run + show (minimal)", set(av_focus) == {"run", "show"})

    # background: same minimal as focus (run + show)
    av_bg = suite.available_verbs("background", full_ctx)
    check("(c) background offers only run + show", set(av_bg) == {"run", "show"})

    # text-only MIRRORS listening (the action set is identical; only the style differs by directive)
    check("(c) text-only mirrors listening's action set",
          set(suite.available_verbs("text-only", full_ctx)) == set(av_listen))

    # decide-for-me: the full set (it acts on what posture permits)
    av_dfm = suite.available_verbs("decide-for-me", full_ctx)
    check("(c) decide-for-me offers all 7 verbs (non-empty graph)", set(av_dfm) == set(suite.RHM_VERBS))

    # off: NO verbs offered (the RHM is disabled)
    check("(c) off offers NO verbs", suite.available_verbs("off", full_ctx) == [])

    # the tools array is built FROM available_verbs — one tool per offered verb, named for the verb,
    # carrying the single-source description. Two channels agree by construction.
    tools = suite._rhm_tools("watch-and-react", full_ctx)
    tool_names = {t["function"]["name"] for t in tools}
    check("(c) _rhm_tools names exactly the available verbs + the `suggest` offer-affordance (single-source w/ available_verbs)",
          tool_names == set(av_watch) | {"suggest"})
    check("(c) each VERB tool carries its single-source description (RHM_VERB_DESC); `suggest` is the meta-offer tool",
          all(t["function"]["description"] == suite.RHM_VERB_DESC[t["function"]["name"]]
              for t in tools if t["function"]["name"] != "suggest"))
    check("(c) off → _rhm_tools is empty (no tools offered)", suite._rhm_tools("off", full_ctx) == [])

    # the single-source derivation: RHM_VERBS / RHM_VERB_DESC / RHM_VERB_CLASS all come from one spec
    check("(c) RHM_VERBS derives from the spec, exact registry-order tuple (7 governed verbs + 3 config-as-tools)",
          suite.RHM_VERBS == ("run", "propose", "build", "consult", "show", "panel", "extend",
                              "configure", "load_voice", "unload_voice"))
    check("(c) RHM_VERB_DESC / RHM_VERB_CLASS keys == the spec keys (no drift)",
          set(suite.RHM_VERB_DESC) == set(suite.RHM_VERB_SPECS) == set(suite.RHM_VERB_CLASS))

    # ============================================================================================
    # (d) CAPABILITY-GATE FAIL-LOUD: a non-tool model (nomic-embed-text) is refused BEFORE any model
    #     call — a legible turn, NO model call, NO fallback. We force the gate to report False (as it
    #     would for an embedder) and assert chat() refuses without ever calling complete_with_tools.
    # ============================================================================================
    from runtime import suite as suite_mod
    import fabric.client as fclient

    # select the embedder as the RHM brain, and force the capability gate to report it non-tool-capable
    suite.set_rhm_config({"model": "nomic-embed-text:latest", "mode": "listening"})
    suite._model_supports_tools = lambda model, base_url=None: False   # the gate says: not tool-capable

    called = {"with_tools": 0}
    _orig = fclient.complete_with_tools
    fclient.complete_with_tools = lambda *a, **k: called.__setitem__("with_tools", called["with_tools"] + 1) or {}
    try:
        r_gate = suite.chat("please run the graph", g)
    finally:
        fclient.complete_with_tools = _orig
    check("(d) non-tool model → chat refuses (no action taken)", r_gate["action"] is None)
    check("(d) refusal is LEGIBLE (names the model / tool requirement, no silent fallback)",
          "nomic-embed-text" in r_gate["reply"] and "tool" in r_gate["reply"].lower())
    check("(d) NO model call was made (complete_with_tools never invoked)", called["with_tools"] == 0)
    # the refusal turn is still logged (continuity), and reports the mode
    check("(d) the refused turn is still logged", store.chat_history(1)[0]["text"].lower().find("can't act") >= 0
          or "select a tool" in store.chat_history(1)[0]["text"].lower())

    # ============================================================================================
    # (e) EMPTY-CONTENT + tool_call → a NON-BLANK reply (the confirmation fold). A native-tool-call
    #     model often emits NO prose, only the call. We stub the transport to return {content:"",
    #     tool_calls:[run]} and a tool-capable gate, and assert the reply is the run confirmation.
    # ============================================================================================
    suite.set_rhm_config({"model": "minimax-m3:cloud", "mode": "listening"})
    suite._model_supports_tools = lambda model, base_url=None: True    # tool-capable now

    # stub complete_with_tools: empty content + a single `run` tool_call (the empty-content-is-success case)
    def _stub_run(*a, **k):
        return {"role": "assistant", "content": "", "tool_calls": [tool_call("run", {})]}
    fclient.complete_with_tools = _stub_run
    try:
        r_empty = suite.chat("recompute it", g)
    finally:
        fclient.complete_with_tools = _orig
    check("(e) empty-content + run tool_call → an action WAS dispatched", r_empty["action"] is not None)
    check("(e) the dispatched action is a run", (r_empty["action"] or {}).get("did") == "run")
    check("(e) the reply is NON-BLANK despite empty content (confirmation fold)",
          bool(r_empty["reply"].strip()) and "ran" in r_empty["reply"].lower())

    # and a forbidden tool_call THROUGH chat() (not just the dispatcher) is refused end-to-end with a
    # legible 'couldn't do that' confirmation — the whitelist holds even via the native-call path.
    def _stub_delete(*a, **k):
        return {"role": "assistant", "content": "", "tool_calls": [tool_call("delete", {"node": "c"})]}
    fclient.complete_with_tools = _stub_delete
    try:
        r_fdel = suite.chat("delete node c", g)
    finally:
        fclient.complete_with_tools = _orig
    check("(e) forbidden 'delete' via chat() native call is REFUSED (did==none)",
          (r_fdel["action"] or {}).get("did") == "none")
    check("(e) node c STILL exists after the refused delete through chat()", any(n.id == "c" for n in suite._load(g).nodes))
    check("(e) the refusal is surfaced in the reply (no silent no-op)", bool(r_fdel["reply"].strip()))

    # ============================================================================================
    # (f) MODE-DISCIPLINE AT DISPATCH (defense-in-depth ATOP the whitelist). A WHITELISTED verb that is
    #     NOT OFFERED in the current mode (e.g. `build` in watch-and-react) must NOT execute. The
    #     affordance set is a REAL gate at dispatch — a forged/confused tool_call for a not-in-mode verb
    #     is refused (did=="none") and NO node is created. The whitelist (E6) still refuses non-RHM_VERBS;
    #     this adds the mode layer. We drive it through the FULL chat() path (the surface the model uses).
    # ============================================================================================
    gm = "mode-discipline"
    suite.create_node(gm, "constant", config={"value": "x"}, node_id="k")   # non-empty graph (so `run` would be ctx-OK)
    suite.set_rhm_config({"model": "minimax-m3:cloud", "mode": "watch-and-react"})
    suite._model_supports_tools = lambda model, base_url=None: True

    # build is a whitelisted RHM verb but NOT offered in watch-and-react → must be refused at dispatch.
    BUILD_FORGED = [{"as": "n", "type": "constant", "config": {"value": "forged"}}]
    nodes_before = len(suite._load(gm).nodes)
    def _stub_build(*a, **k):
        return {"role": "assistant", "content": "", "tool_calls": [tool_call("build", {"steps": BUILD_FORGED})]}
    fclient.complete_with_tools = _stub_build
    try:
        r_modebuild = suite.chat("build me a node", gm)
    finally:
        fclient.complete_with_tools = _orig
    check("(f) forged `build` in watch-and-react via chat() is REFUSED at dispatch (did==none)",
          (r_modebuild["action"] or {}).get("did") == "none")
    check("(f) the refusal names the mode-discipline reason (legible)",
          "watch-and-react" in str((r_modebuild["action"] or {}).get("refused", "")) and
          "build" in str((r_modebuild["action"] or {}).get("refused", "")))
    check("(f) NO node was created by the refused not-in-mode build (graph unchanged)",
          len(suite._load(gm).nodes) == nodes_before)
    check("(f) the refusal is folded into the reply (no silent no-op)", bool(r_modebuild["reply"].strip()))

    # CONTRAST: a verb that IS offered in this mode (show) still DISPATCHES normally — the gate narrows,
    # it does not break offered verbs. `show k` targets the live node → did=="show".
    def _stub_show(*a, **k):
        return {"role": "assistant", "content": "", "tool_calls": [tool_call("show", {"targets": ["k"]})]}
    fclient.complete_with_tools = _stub_show
    try:
        r_modeshow = suite.chat("show me node k", gm)
    finally:
        fclient.complete_with_tools = _orig
    check("(f) an OFFERED verb (show) in watch-and-react still DISPATCHES normally",
          (r_modeshow["action"] or {}).get("did") == "show")

    # E6 STILL HOLDS through the mode-gate: a catastrophic forged `delete` in watch-and-react is refused
    # (it is neither offered in mode NOR whitelisted) and node k survives.
    def _stub_del2(*a, **k):
        return {"role": "assistant", "content": "", "tool_calls": [tool_call("delete", {"node": "k"})]}
    fclient.complete_with_tools = _stub_del2
    try:
        r_modedel = suite.chat("delete node k", gm)
    finally:
        fclient.complete_with_tools = _orig
    check("(f) E6: forged `delete` in watch-and-react STILL refused (did==none)",
          (r_modedel["action"] or {}).get("did") == "none")
    check("(f) E6: node k survives the forged delete", any(n.id == "k" for n in suite._load(gm).nodes))

    print(f"\nALL {PASS} CHECKS PASS — RHM acts via NATIVE tool-calling; whitelist holds end-to-end; "
          "capability-gate fails loud; affordances correct per mode; empty-content tool_call → non-blank reply; "
          "mode-discipline enforced at dispatch")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
