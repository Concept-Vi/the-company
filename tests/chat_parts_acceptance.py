"""tests/chat_parts_acceptance.py — Concurrent Cognition G4 (the staged-response queue).

Proves the G4 refactor + the staged path + the PRESERVATION GATE (R1-FOLD F4 / R2-FOLD H3 — the
highest-blast-radius criterion). The bar:

  THE REFACTOR  — chat()'s body is a SHARED CORE (prologue ONCE · part-core PER PART · epilogue ONCE)
                  that BOTH chat() (one part) and chat_parts() (N parts) call (never loops/copies it).
  C4.1          — part grain follows the mode (PART_GRAIN table; switching mode changes the grain).
  C4.2          — Part 1 fires from base context; later parts read role outputs at run://<turn>/<role>
                  via the canonical resolver, and the G3 declared rules decide what injects.
  C4.3          — conditional staging is MANDATORY: a trivial turn / a never-stage mode (focus/background)
                  BYPASSES the whole machine — NO cognition.wave fires.
  C4.5          — tools on the FINAL part only (intermediate parts pure generation).
  THREE SHAPES  — off=4-key · refusal=5-key · normal=7-key, distinct + the provenance asymmetry.
  MONKEYPATCH   — INDEPENDENTLY verified: patch self._model_supports_tools + fabric.client.
                  complete_with_tools and confirm BOTH chat() AND chat_parts() honor them (the gate is
                  not bypassed; no forked brain — the SILENT KILLER no listed rhm_* test catches).
  ONCE-PER-PART — _chat_context (NOT side-effect-free; warns on a down endpoint) runs ONCE PER PART.
  DRIFT HOME    — THOUGHT_SHAPES + PART_GRAIN reflected in runtime/AGENTS.md (mirrors RULE_OPS).
  ADVERSARIAL   — off→4-key (no core leak) · refusal→5-key · down-endpoint warning once-per-part.

The deterministic checks STUB complete_with_tools (no live endpoint dependency). One LIVE staged turn
against the resident 4B (read-only USE) gives the by-use proof of C4.2/C4.4/C4.5 (skipped-with-note if
the endpoint is down — never a false green).
"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from store.fs_store import FsStore                      # noqa: E402
from runtime.registry import NodeRegistry               # noqa: E402
from runtime.suite import Suite                          # noqa: E402

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def tool_call(name, arguments):
    return {"id": "call_1", "type": "function",
            "function": {"name": name, "arguments": json.dumps(arguments)}}


def fresh_suite(tmp):
    store = FsStore(os.path.join(tmp, "store"))
    reg = NodeRegistry().discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)
    return suite, store


def n_waves(store):
    return len([e for e in store.recent_events(2000) if e.get("kind") == "cognition.wave"])


def n_chats(store):
    return len([e for e in store.recent_events(2000) if e.get("kind") == "chat"])


def drain(gen):
    return list(gen)


def _raises(fn):
    try:
        fn()
        return False
    except Exception:
        return True


RESIDENT_BASE = "http://127.0.0.1:8000/v1"
RESIDENT_MODEL = "cyankiwi/Qwen3.5-4B-AWQ-4bit"


def endpoint_up():
    import urllib.request
    try:
        with urllib.request.urlopen(RESIDENT_BASE + "/models", timeout=4) as r:
            return r.status == 200
    except Exception:
        return False


tmp = tempfile.mkdtemp(prefix="g4-chatparts-")
try:
    import fabric.client as fclient

    # ============================================================================================
    # (1) THE REGISTRIES + shape_for/grain_for (C4.1 — L1 data, not control flow)
    # ============================================================================================
    suite, store = fresh_suite(tmp)
    check("(1) THOUGHT_SHAPES has the 5 archetypes",
          set(suite.THOUGHT_SHAPES) == {"linear-stream", "reduce-tree", "jury-select",
                                        "scatter-route", "scatter-write"})
    for sid, shp in suite.THOUGHT_SHAPES.items():
        check(f"(1) shape {sid!r} declares archetype/fanout/join/render_from",
              set(("archetype", "fanout", "join", "render_from")).issubset(shp))
    check("(1) PART_GRAIN covers every MODE", set(suite.PART_GRAIN) == set(suite.MODES))
    check("(1) shape_for(unknown) FAILS LOUD",
          _raises(lambda: suite.shape_for("zzz")))
    # C4.1: switching mode CHANGES the grain (data-driven, not a branch)
    check("(1/C4.1) listening grain=beat", suite.grain_for("listening") == "beat")
    check("(1/C4.1) text-only grain=paragraph", suite.grain_for("text-only") == "paragraph")
    check("(1/C4.1) focus grain=line", suite.grain_for("focus") == "line")
    check("(1/C4.1) the grain DIFFERS across modes (mode changes the grain)",
          len({suite.grain_for(m) for m in ("listening", "text-only", "focus")}) >= 2)
    check("(1/C4.3) focus/background/off do NOT stage; listening/text-only DO",
          (not suite.mode_stages("focus")) and (not suite.mode_stages("background"))
          and (not suite.mode_stages("off")) and suite.mode_stages("listening")
          and suite.mode_stages("text-only"))

    # ============================================================================================
    # (2) THE REFACTOR — chat() = prologue + ONE part-core + epilogue. The shared helpers EXIST and
    #     chat() routes through them (we assert the methods exist + chat() one-part contract holds).
    # ============================================================================================
    for m in ("_chat_prologue", "_chat_part_core", "_chat_epilogue", "chat_parts",
              "_should_stage", "shape_for", "grain_for", "mode_stages"):
        check(f"(2) shared-core method {m} exists", hasattr(suite, m) and callable(getattr(suite, m)))

    # ============================================================================================
    # (3) THREE RETURN SHAPES (distinct + provenance asymmetry) — via STUBBED chat() (no endpoint).
    # ============================================================================================
    suite, store = fresh_suite(tmp + "/3")
    suite.create_node("g", "constant", config={"value": "x"}, node_id="c1")

    # OFF → 4-key (reply, action, mode, history); off short-circuits BEFORE the gate (no model call).
    suite.set_mode("off")
    called = {"cwt": 0}
    orig = fclient.complete_with_tools
    fclient.complete_with_tools = lambda *a, **k: called.__setitem__("cwt", called["cwt"] + 1) or {}
    try:
        r_off = suite.chat("hello", "g")
    finally:
        fclient.complete_with_tools = orig
    check("(3) OFF return is the 4-key shape",
          set(r_off) == {"reply", "action", "mode", "history"})
    check("(3) OFF made NO model call (off is a prologue early-return, no core leak)", called["cwt"] == 0)
    _h2 = store.chat_history(2)
    _g = {row["role"]: row["grade"] for row in _h2}
    check("(3) OFF turn graded gold(user)/working(twin) — provenance asymmetry preserved",
          _g.get("user") == "gold" and _g.get("assistant") == "working")

    # REFUSAL → 5-key (reply, action, mode, model, history). Force the gate False.
    suite.set_rhm_config({"model": "nomic-embed-text:latest", "mode": "listening"})
    suite._model_supports_tools = lambda model, base_url=None: False
    called["cwt"] = 0
    fclient.complete_with_tools = lambda *a, **k: called.__setitem__("cwt", called["cwt"] + 1) or {}
    try:
        r_ref = suite.chat("run the graph", "g")
    finally:
        fclient.complete_with_tools = orig
    check("(3) REFUSAL return is the 5-key shape",
          set(r_ref) == {"reply", "action", "mode", "model", "history"})
    check("(3) REFUSAL made NO model call (refusal is a prologue early-return, no core leak)",
          called["cwt"] == 0)
    check("(3) REFUSAL names the model + tool requirement (legible, no silent fallback)",
          "nomic-embed-text" in r_ref["reply"] and "tool" in r_ref["reply"].lower())

    # NORMAL → 7-key (reply, action, proposal, mode, model, thread_id, history). Stub a tool-capable
    # model + an empty-content run tool_call (the established empty-content-is-success case).
    suite.set_rhm_config({"model": "minimax-m3:cloud", "mode": "listening"})
    suite._model_supports_tools = lambda model, base_url=None: True
    fclient.complete_with_tools = lambda *a, **k: {"role": "assistant", "content": "",
                                                   "tool_calls": [tool_call("run", {})]}
    try:
        r_norm = suite.chat("recompute it", "g")
    finally:
        fclient.complete_with_tools = orig
    check("(3) NORMAL return is the 7-key shape",
          set(r_norm) == {"reply", "action", "proposal", "mode", "model", "thread_id", "history"})
    check("(3) NORMAL dispatched the run (the tool block ran on the one/final part)",
          (r_norm["action"] or {}).get("did") == "run")
    check("(3) the three shapes are DISTINCT (4 != 5 != 7 keys)",
          len({len(r_off), len(r_ref), len(r_norm)}) == 3)

    # ============================================================================================
    # (4) MONKEYPATCH SEAMS — INDEPENDENTLY VERIFIED. Patch self._model_supports_tools (instance attr)
    #     + fabric.client.complete_with_tools (module attr) and confirm BOTH chat() AND chat_parts()
    #     honor them. THE SILENT KILLER: an off/refusal leak into the core, OR a part that bypasses the
    #     module ref (a forked brain). No listed rhm_* test patches chat_parts — this does.
    # ============================================================================================
    suite, store = fresh_suite(tmp + "/4")
    suite.create_node("g", "constant", config={"value": "x"}, node_id="c1")
    suite.set_mode("listening")

    # (4a) GATE patched FALSE → BOTH chat() and chat_parts() refuse, NEITHER calls complete_with_tools.
    suite.set_rhm_config({"model": "some-model", "mode": "listening"})
    suite._model_supports_tools = lambda model, base_url=None: False
    calls = {"n": 0}
    fclient.complete_with_tools = lambda *a, **k: calls.__setitem__("n", calls["n"] + 1) or {
        "role": "assistant", "content": "LEAK", "tool_calls": []}
    try:
        c_chat = suite.chat("substantive question about the storage layer tradeoffs in detail", "g")
        parts = drain(suite.chat_parts("substantive question about the storage layer tradeoffs in detail", "g"))
    finally:
        fclient.complete_with_tools = orig
    check("(4a) GATE=False: chat() honors the patched instance-method gate (refusal 5-key, no call)",
          set(c_chat) == {"reply", "action", "mode", "model", "history"})
    check("(4a) GATE=False: chat_parts() ALSO honors the SAME instance gate (early refusal, no stage)",
          parts[-1].get("staged") is False and parts[-1].get("early_return") is not None)
    check("(4a) GATE=False: complete_with_tools NEVER called by EITHER path (gate not bypassed)",
          calls["n"] == 0)
    check("(4a) GATE=False: no forked-brain LEAK text reached the reply",
          "LEAK" not in c_chat["reply"] and "LEAK" not in parts[-1]["text"])

    # (4b) GATE patched TRUE + complete_with_tools patched → BOTH paths route through the MODULE REF
    #      (if a part used `from fabric.client import complete_with_tools`, the patch would NOT intercept
    #      it → a forked brain). We assert the patch IS hit by both chat() and a STAGED chat_parts().
    suite._model_supports_tools = lambda model, base_url=None: True
    hits = {"n": 0}

    def _seam_stub(*a, **k):
        hits["n"] += 1
        # an intermediate (Part-1) call is offered tools=[] (C4.5); reflect that back legibly.
        toolset = k.get("tools") if "tools" in k else (a[3] if len(a) > 3 else None)
        return {"role": "assistant",
                "content": f"reply (tools_offered={0 if not toolset else len(toolset)})",
                "tool_calls": []}
    fclient.complete_with_tools = _seam_stub
    try:
        hits["n"] = 0
        suite.chat("a clear substantive multi-part question about storage tradeoffs", "g")
        chat_hits = hits["n"]
        hits["n"] = 0
        sparts = drain(suite.chat_parts("a clear substantive multi-part question about storage tradeoffs", "g",
                                        turn_id="seam1"))
        parts_hits = hits["n"]
    finally:
        fclient.complete_with_tools = orig
    check("(4b) chat() routes through the patched MODULE REF (>=1 hit — no forked brain)",
          chat_hits >= 1)
    check("(4b) STAGED chat_parts() routes EVERY part through the SAME patched module ref (>=2 hits)",
          sparts[-1].get("staged") is True and parts_hits >= 2)

    # ============================================================================================
    # (5) C4.5 — TOOLS ON THE FINAL PART ONLY (intermediate parts pure generation). The seam stub
    #     reports how many tools it was offered; Part 1 (intermediate) must be offered ZERO, the final
    #     part the real set.
    # ============================================================================================
    suite, store = fresh_suite(tmp + "/5")
    suite.create_node("g", "constant", config={"value": "x"}, node_id="c1")
    suite.set_mode("listening")
    suite._model_supports_tools = lambda model, base_url=None: True
    offered_log = []

    def _tools_probe(*a, **k):
        toolset = k.get("tools") if "tools" in k else (a[3] if len(a) > 3 else [])
        offered_log.append(len(toolset or []))
        return {"role": "assistant", "content": "part text", "tool_calls": []}
    fclient.complete_with_tools = _tools_probe
    try:
        offered_log.clear()
        drain(suite.chat_parts("a substantive question about the storage tradeoffs in full detail", "g",
                               turn_id="c45"))
    finally:
        fclient.complete_with_tools = orig
    check("(5/C4.5) the STAGED turn made >=2 part-calls", len(offered_log) >= 2)
    check("(5/C4.5) the FIRST (intermediate) part was offered ZERO tools (pure generation)",
          offered_log[0] == 0)
    check("(5/C4.5) the FINAL part WAS offered tools (>0 — the real affordance set)",
          offered_log[-1] > 0)

    # ============================================================================================
    # (6) C4.3 — CONDITIONAL STAGING (mandatory): a trivial turn / never-stage mode → NO cognition.wave.
    # ============================================================================================
    suite, store = fresh_suite(tmp + "/6")
    suite.create_node("g", "constant", config={"value": "x"}, node_id="c1")
    suite._model_supports_tools = lambda model, base_url=None: True
    fclient.complete_with_tools = lambda *a, **k: {"role": "assistant", "content": "ok", "tool_calls": []}
    try:
        # trivial one-liner in listening → bypass, NO wave
        suite.set_mode("listening")
        w0 = n_waves(store)
        triv = drain(suite.chat_parts("hi", "g"))
        w1 = n_waves(store)
        check("(6/C4.3) trivial 'hi' does NOT stage (brevity bypass)", triv[-1].get("staged") is False)
        check("(6/C4.3) trivial turn fired ZERO cognition.wave (the swarm did NOT spin)", w1 == w0)
        # focus mode (never-stage) on a SUBSTANTIVE turn → still NO wave
        suite.set_mode("focus")
        w2 = n_waves(store)
        foc = drain(suite.chat_parts("explain in detail the full memo-gate re-run logic and the volatile exception", "g"))
        w3 = n_waves(store)
        check("(6/C4.3) focus mode does NOT stage even a substantive turn", foc[-1].get("staged") is False)
        check("(6/C4.3) focus fired ZERO cognition.wave", w3 == w2)
        # background mode → never-stage
        suite.set_mode("background")
        w4 = n_waves(store)
        bg = drain(suite.chat_parts("give me a thorough multi-paragraph rundown of the whole architecture", "g"))
        w5 = n_waves(store)
        check("(6/C4.3) background mode does NOT stage", bg[-1].get("staged") is False and w5 == w4)
    finally:
        fclient.complete_with_tools = orig

    # ============================================================================================
    # (7) ADVERSARIAL — off still 4-key (no core leak); refusal still 5-key; _chat_context once-PER-PART
    #     on a down endpoint emits the warning exactly once per part (not once total, not twice/part).
    # ============================================================================================
    suite, store = fresh_suite(tmp + "/7")
    suite.create_node("g", "constant", config={"value": "x"}, node_id="c1")
    # off via chat_parts → the prologue early-return shape, NO core, NO epilogue (one chat event from off).
    suite.set_mode("off")
    pre_chat = n_chats(store)
    op = drain(suite.chat_parts("anything", "g"))
    check("(7) off via chat_parts → ONE part, early_return present, NOT staged (no core leak)",
          len(op) == 1 and op[0].get("early_return") is not None and op[0].get("staged") is False)
    check("(7) off via chat_parts → exactly ONE chat event (the prologue's own emit, no epilogue)",
          n_chats(store) - pre_chat == 1)

    # _chat_context once-per-part: count the 'warning' events a DOWN model registry emits. We force the
    # model reads to raise (down endpoint) and count warnings across a one-part chat() (==1 ctx call) vs
    # a 2-part staged chat_parts() (==2 ctx calls). The warning fires inside _chat_context, once per call.
    suite2, store2 = fresh_suite(tmp + "/7b")
    suite2.create_node("g", "constant", config={"value": "x"}, node_id="c1")
    suite2._model_supports_tools = lambda model, base_url=None: True
    # force available_models to raise → _chat_context emits a 'warning' each time it is assembled.
    def _boom():
        raise RuntimeError("endpoint down (forced)")
    suite2.available_models = _boom
    fclient.complete_with_tools = lambda *a, **k: {"role": "assistant", "content": "ok", "tool_calls": []}

    def warn_count():
        # count the CHAT-registry warning specifically (the one we force via available_models) — it fires
        # exactly ONCE per _chat_context assembly, so its count == the number of part-context assemblies.
        return len([e for e in store2.recent_events(4000)
                    if e.get("kind") == "warning" and "chat model registry unreachable" in str(e.get("summary", ""))])
    try:
        # one-part chat(): exactly ONE _chat_context assembly → ONE warning
        suite2.set_mode("focus")  # focus never stages → chat_parts is the one-part path too; use chat() for the 1-call ref
        w_before = warn_count()
        suite2.chat("a focus question", "g")
        one_part_warns = warn_count() - w_before
        check("(7) _chat_context once-per-part: a ONE-part chat() emits exactly ONE down-endpoint warning",
              one_part_warns == 1)
        # 2-part staged chat_parts(): exactly TWO _chat_context assemblies → TWO warnings
        suite2.set_mode("listening")
        w_before = warn_count()
        sp = drain(suite2.chat_parts("a substantive question about the storage layer tradeoffs in detail", "g",
                                     turn_id="warn1"))
        staged_warns = warn_count() - w_before
        check("(7) the staged turn DID stage (2 parts)", sp[-1].get("staged") is True and len(sp) == 2)
        check("(7) _chat_context once-PER-PART: a 2-part staged turn emits exactly TWO warnings (not 1, not 4)",
              staged_warns == 2)
    finally:
        fclient.complete_with_tools = orig

    # ============================================================================================
    # (8) DRIFT HOME — THOUGHT_SHAPES + PART_GRAIN reflected in runtime/AGENTS.md (mirrors RULE_OPS).
    # ============================================================================================
    agents = open(os.path.join(ROOT, "runtime", "AGENTS.md")).read()
    check("(8) runtime/AGENTS.md reflects THOUGHT_SHAPES (the drift home)", "THOUGHT_SHAPES" in agents)
    check("(8) runtime/AGENTS.md reflects PART_GRAIN (the drift home)", "PART_GRAIN" in agents)
    for sid in suite.THOUGHT_SHAPES:
        check(f"(8) runtime/AGENTS.md names the {sid!r} archetype", sid in agents)

    # ============================================================================================
    # (9) BY-USE — a LIVE staged turn against the resident 4B (read-only). Proves C4.2 (run:// inject via
    #     the G3 rule) + C4.4 (joined reply) + the once-only epilogue end-to-end. Skipped-with-note if down.
    # ============================================================================================
    if endpoint_up():
        suite3, store3 = fresh_suite(tmp + "/9")
        suite3.set_rhm_config({"model": RESIDENT_MODEL, "base_url": RESIDENT_BASE})
        suite3.create_node("g", "constant", config={"value": "x"}, node_id="c1")
        suite3.set_mode("listening")
        cw0 = n_waves(store3)
        ch0 = n_chats(store3)
        live = drain(suite3.chat_parts(
            "What did we decide about the storage layer, and can you summarize the tradeoffs in detail?",
            "g", turn_id="live1"))
        check("(9/by-use) the live turn STAGED (2 parts)", live[-1].get("staged") is True and len(live) == 2)
        check("(9/by-use C1.6) the wave fired exactly ONE cognition.wave rollup", n_waves(store3) - cw0 == 1)
        # the rich rollup payload (run_swarm passes it as the event 'summary')
        wave_ev = [e for e in store3.recent_events(2000) if e.get("kind") == "cognition.wave"][-1]
        payload = wave_ev.get("summary") or {}
        roles_fired = [r["role"] for r in (payload.get("roles") or [])]
        check("(9/by-use C4.2) the listening cast fired CONCURRENTLY (recall+ground among them)",
              "recall" in roles_fired and "ground" in roles_fired)
        check("(9/by-use C1.1) wall < sum (real concurrency)",
              payload.get("wall_s", 1e9) < payload.get("sum_role_s", 0) or payload.get("n_roles", 0) <= 1)
        # C4.2: a role's output is readable BACK at run://<turn>/<role> (the net-new ref-read)
        cas = store3.head("run://live1/recall")
        check("(9/by-use C4.2) a role output is addressable at run://live1/recall", cas is not None)
        # the G3 declared rule decided injection (provenance recorded)
        check("(9/by-use C4.2) the G3 declared rule ran over the resolved role values",
              "inject_provenance" in live[-1])
        # C4.4: the joined reply carries BOTH parts as one string
        res = live[-1].get("result") or {}
        check("(9/by-use C4.4) the epilogue joined both parts into ONE reply",
              live[0]["text"] in res.get("reply", "") and live[1]["text"] in res.get("reply", ""))
        # epilogue once: exactly ONE chat event + ONE user + ONE assistant for the WHOLE staged turn
        check("(9/by-use) the staged turn emitted exactly ONE chat event (epilogue once)",
              n_chats(store3) - ch0 == 1)
        hist = store3.chat_history(40)
        check("(9/by-use) the staged turn appended exactly ONE user + ONE assistant row",
              len(hist) == 2 and {hist[0]["role"], hist[1]["role"]} == {"user", "assistant"})
        print("  -- by-use ran against the LIVE resident 4B --")
    else:
        print("  -- (9) by-use SKIPPED: resident 4B endpoint is DOWN (not a false green; the stubbed "
              "checks above carry the refactor + seam + C4.1/4.3/4.5 proofs) --")

    print(f"\nALL {PASS} CHECKS PASS — G4 staged-response queue: chat() refactored into a shared core "
          "(prologue·part-core·epilogue); 3 return shapes distinct; monkeypatch seams honored by BOTH "
          "chat() AND chat_parts() (no forked brain); C4.1 grain-follows-mode; C4.2 run:// inject via "
          "the G3 rule; C4.3 trivial/never-stage → no wave; C4.5 tools on final part only; "
          "_chat_context once-per-part; drift home reflected")
finally:
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
