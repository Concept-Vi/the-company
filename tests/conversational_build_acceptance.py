"""tests/conversational_build_acceptance.py — the CONVERSATIONAL → SELF-BUILD bridge.

Proves the new `request_change` RHM verb routes a conversational change-request into the EXISTING
`surface_intent_at` producer, so it mints an intent=="build" item that surfaces for approval through
the SAME inbox/build-intent card + /api/resolve approve the wire-DOOR uses — closing the gap where the
claude -p self-build wire was reachable ONLY via the wire-door, never via chat.

What this proves (deterministic, model-free where possible — a temp store, no claude -p, no wire arming):
  (i)   request_change with a change description + a RESOLVABLE/INDICATED address calls surface_intent_at
        and produces an item with payload.intent=="build" that is_build_intent() returns True for (so it
        WILL reach the wire when armed+approved).
  (ii)  the same item surfaces for approval EXACTLY like a wire-door intent (same inbox, resolved=None,
        action="review", decision.intent event) — byte-comparable to /api/build-intent's surface_build_intent.
  (iii) an UNRESOLVABLE target does NOT mint a build-intent — it ASKS / fails loud (no fiction, no guessed
        scope). The inbox count does not grow.
  (iv)  the verb is OFFERED in the build-ish modes + derives its native tool correctly from the VerbSpec
        (RHM_VERBS / _DESC / _CLASS / the tools array / available_verbs all project from the one spec).
  (v)   regression: the existing wire path + propose/panel/extend + is_build_intent are unchanged.

Address resolution (the one design point) is exercised across all three tiers:
  (a) INDICATED LOCUS — the operator pointed at an element (current_locus set) → used.
  (b) NAMED ELEMENT  — a ui:// address OR a recognizable name resolved against the registry.
  (c) ASK            — neither → asks, mints nothing.

Run: .venv/bin/python tests/conversational_build_acceptance.py
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def fresh_suite():
    # TEMP store (COMPANY_STORE unset = the LIVE store — use a tmp dir, per the build rules).
    store = FsStore(os.path.join(tempfile.mkdtemp(prefix="convo-wire-"), "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    return Suite(store, reg, nodes_dir=NODES)


def pick_registered_element(suite):
    """A registered, grammar-valid ui:// element address that resolve_change_target accepts. Prefer a
    real element row from the corpus (so resolve_scope can derive a non-empty scope); fall back to a
    region served-form. Returns the address."""
    info = suite.build_ui_info()
    # the full-string element keys (ui://inbox/build-review …) — these are the S1 element rows.
    for key in info:
        if isinstance(key, str) and key.startswith("ui://"):
            return key
    # fallback: a region served-form (ui://chrome/inbox)
    return "ui://chrome/inbox"


def latest_open_inbox_ids(suite):
    return [d["id"] for d in suite.inbox.list() if d.get("resolved") is None]


# ──────────────────────────────────────────────────────────────────────────────────────────────
# (iv) the verb derives correctly from the ONE VerbSpec (single-source) — projection + offer
# ──────────────────────────────────────────────────────────────────────────────────────────────
def test_spec_derivation():
    s = fresh_suite()
    check("verb in RHM_VERBS (the whitelist tuple, derived from the spec)",
          "request_change" in Suite.RHM_VERBS)
    check("verb in RHM_VERB_DESC (gloss derived from the spec)",
          "request_change" in Suite.RHM_VERB_DESC and Suite.RHM_VERB_DESC["request_change"])
    check("verb in RHM_VERB_CLASS (governance class derived from the spec)",
          Suite.RHM_VERB_CLASS.get("request_change") == "register_type")
    check("verb has a native-tool param schema (change required)",
          "change" in Suite._VERB_PARAMS["request_change"]["properties"]
          and Suite._VERB_PARAMS["request_change"]["required"] == ["change"])

    # OFFERED in the build-ish modes (listening/text-only/decide-for-me), NOT in observe/off modes.
    ctx = {"graph_nonempty": True, "inbox_pending": False, "node_selected": False}
    for m in ("listening", "text-only", "decide-for-me"):
        check(f"offered in build-ish mode {m!r}", "request_change" in s.available_verbs(m, ctx))
    for m in ("walkthrough", "watch-and-react", "off"):
        check(f"NOT offered in non-buildish mode {m!r}", "request_change" not in s.available_verbs(m, ctx))

    # native tool derives from the spec (name + schema present in the tools array)
    tools = s._rhm_tools("text-only", ctx)
    rc = next((t for t in tools if t["function"]["name"] == "request_change"), None)
    check("native tool 'request_change' built from the spec", rc is not None)
    check("native tool carries the spec gloss + required change param",
          rc["function"]["description"] == Suite.RHM_VERB_DESC["request_change"]
          and rc["function"]["parameters"]["required"] == ["change"])

    # _json_obj_to_action normalises the tool-call object → the dispatcher dict (shape-recognition)
    a = Suite._json_obj_to_action(
        {"name": "request_change", "arguments": '{"change":"make the run button confirm","target":"ui://toolbar/run"}'},
        "request_change")
    check("_json_obj_to_action maps request_change shape → action dict",
          a == {"verb": "request_change", "change": "make the run button confirm", "target": "ui://toolbar/run"})


# ──────────────────────────────────────────────────────────────────────────────────────────────
# (i)+(ii) a resolvable/indicated address → an intent=="build" item that surfaces like the wire-door
# ──────────────────────────────────────────────────────────────────────────────────────────────
def test_named_address_mints_build_intent():
    s = fresh_suite()
    addr = pick_registered_element(s)
    before = len(latest_open_inbox_ids(s))
    out = s._dispatch_rhm_action(
        {"verb": "request_change", "change": "make this confirm before recomputing", "target": addr},
        graph_id="g")
    check("request_change dispatched (did=request_change)", out.get("did") == "request_change")
    check("it surfaced an item id", bool(out.get("surfaced")))
    sid = out["surfaced"]

    # the surfaced item carries payload.intent=="build" → is_build_intent True (WILL reach the wire)
    rec = next(d for d in s.inbox.list() if d["id"] == sid)
    check("surfaced item payload.intent == 'build'", (rec.get("payload") or {}).get("intent") == "build")
    check("is_build_intent(rec) is True (reaches the claude -p wire when armed+approved)",
          Suite.is_build_intent(rec) is True)

    # (ii) surfaces EXACTLY like a wire-door intent: same inbox, resolved=None, action='review'
    check("resolved is None (a live escalation until the operator resolves)", rec.get("resolved") is None)
    check("action == 'review' (walks the same review lifecycle as the wire-door)", rec.get("action") == "review")
    check("inbox grew by exactly one open item", len(latest_open_inbox_ids(s)) == before + 1)
    # a decision.intent event was emitted (the wire-door's surface_build_intent emits the same)
    evs = [e for e in s.store.events_since(-1) if e.get("kind") == "decision.intent" and e.get("surfaced") == sid]
    check("decision.intent event emitted for the surfaced build-intent", len(evs) == 1)
    check("the event marks intent=build (the discriminator)", evs[0].get("intent") == "build")


def test_indicated_locus_used():
    """(a) INDICATED LOCUS — the operator pointed at an element this turn (current_locus set); the verb
    uses it even when the model supplies NO target."""
    s = fresh_suite()
    addr = pick_registered_element(s)
    # simulate the operator pointing at the element this turn: chat() sets _current_locus via
    # _chat_context from the widened focus.selected. We set it directly (the held backend locus).
    s._current_locus = addr
    out = s._dispatch_rhm_action(
        {"verb": "request_change", "change": "this is too cramped, fix it", "target": None},
        graph_id="g")
    check("request_change with NO target uses the indicated locus", out.get("did") == "request_change")
    check("the minted build-intent is scoped to the INDICATED address", out.get("address") == addr)
    check("source == 'indicated' (the pointed element was the truth)", out.get("source") == "indicated")
    rec = next(d for d in s.inbox.list() if d["id"] == out["surfaced"])
    check("indicated-locus item is a real build-intent", Suite.is_build_intent(rec) is True)


def test_explicit_target_beats_stale_locus():
    """PRECEDENCE (the correctness-critical case the advisor caught): `current_locus()` is the
    most-recent indication ACROSS THE SESSION (set if-indicated, never cleared), so it is NOT reliably
    'this turn'. A STALE earlier click must NEVER silently override a target the operator named THIS
    turn — that would scope the build to the WRONG element (the exact wrong-scope failure rule 8 forbids).
    An explicit, RESOLVABLE target therefore WINS over the held locus."""
    s = fresh_suite()
    s._current_locus = "ui://chrome/activity"            # a stale click from an earlier turn
    res = s.resolve_change_target("the run button", indicated=s.current_locus())
    check("an explicit resolvable target WINS over a stale session locus",
          res["source"] == "named" and res["address"] == "ui://toolbar/run")
    out = s._dispatch_rhm_action(
        {"verb": "request_change", "change": "make the run button confirm before recomputing",
         "target": "the run button"}, graph_id="g")
    check("the minted build-intent is scoped to the NAMED target, not the stale locus",
          out.get("did") == "request_change" and out.get("address") == "ui://toolbar/run")
    # the locus is still used when NO explicit target is given (the 'pointed and didn't restate' case)
    res2 = s.resolve_change_target(None, indicated="ui://toolbar/run")
    check("with no target, the indicated locus is still used", res2["source"] == "indicated"
          and res2["address"] == "ui://toolbar/run")
    # an UNRESOLVABLE named target does NOT beat a usable locus (the locus is preferred over a bad name)
    res3 = s.resolve_change_target("the flux capacitor", indicated="ui://toolbar/run")
    check("a usable locus is preferred over an UNRESOLVABLE named target",
          res3["source"] == "indicated" and res3["address"] == "ui://toolbar/run")


def test_named_element_by_name():
    """(b) NAMED ELEMENT — a recognizable name resolves against the registry to a ui:// address.
    Uses Tim's canonical example: 'the run button' → ui://toolbar/run (an UNAMBIGUOUS single match).
    Note an ambiguous name (e.g. 'the inbox' = the region + many sub-elements) correctly ASKS — proven
    in test_unresolvable_target_asks_not_mints — never guesses (rule 8)."""
    s = fresh_suite()
    res = s.resolve_change_target("the run button", indicated=None)
    check("named element 'the run button' resolves to ui://toolbar/run (Tim's example)",
          res["source"] == "named" and res["address"] == "ui://toolbar/run")
    out = s._dispatch_rhm_action(
        {"verb": "request_change", "change": "make the run button confirm before recomputing",
         "target": "the run button"}, graph_id="g")
    check("named-element request_change mints a build-intent at the resolved address",
          out.get("did") == "request_change" and out.get("address") == "ui://toolbar/run")
    rec = next(d for d in s.inbox.list() if d["id"] == out["surfaced"])
    check("named-element item is a real build-intent (reaches the wire)", Suite.is_build_intent(rec) is True)

    # AMBIGUITY → ASK (never pick one): 'the inbox' spans the region + many sub-elements.
    amb = s.resolve_change_target("the inbox", indicated=None)
    check("an AMBIGUOUS name asks (>1 candidate), never guesses",
          amb["source"] == "ask" and len(amb["candidates"]) > 1)


# ──────────────────────────────────────────────────────────────────────────────────────────────
# (iii) an UNRESOLVABLE target does NOT mint a build-intent — it ASKS (no fiction, no guessed scope)
# ──────────────────────────────────────────────────────────────────────────────────────────────
def test_unresolvable_target_asks_not_mints():
    s = fresh_suite()
    before = len(latest_open_inbox_ids(s))

    # no target, no indicated locus → ASK
    out = s._dispatch_rhm_action(
        {"verb": "request_change", "change": "change something", "target": None}, graph_id="g")
    check("no target + no indicated locus → did=ask_target (asks, no mint)", out.get("did") == "ask_target")
    check("ask carries a fail-loud prompt (no fiction)", bool(out.get("ask")))
    check("NO inbox item minted on an ask", len(latest_open_inbox_ids(s)) == before)

    # an unrecognizable name → ASK
    out2 = s._dispatch_rhm_action(
        {"verb": "request_change", "change": "fix it", "target": "the flux capacitor widget"}, graph_id="g")
    check("unrecognizable element name → did=ask_target (no guess)", out2.get("did") == "ask_target")
    check("STILL no inbox item minted (no guessed scope)", len(latest_open_inbox_ids(s)) == before)

    # a well-formed-but-UNREGISTERED ui:// → ASK (not silently accepted as a DENY-ALL build-intent)
    res = s.resolve_change_target("ui://nowhere/nothing", indicated=None)
    check("unregistered ui:// target → ASK (not accepted)", res["source"] == "ask" and res["address"] is None)

    # an empty change description → refused (fail loud), nothing minted
    out3 = s._dispatch_rhm_action(
        {"verb": "request_change", "change": "", "target": "ui://chrome/inbox"}, graph_id="g")
    check("empty change description → refused, no mint", out3.get("did") == "none")
    check("STILL no inbox item minted on a refused empty change", len(latest_open_inbox_ids(s)) == before)


# ──────────────────────────────────────────────────────────────────────────────────────────────
# (v) regression: the wire-door + propose/panel/extend + is_build_intent are unchanged
# ──────────────────────────────────────────────────────────────────────────────────────────────
def test_wire_door_unchanged():
    s = fresh_suite()
    # the wire-DOOR producer (surface_build_intent, what /api/build-intent calls) still mints a build-intent
    out = s.surface_build_intent("door build", scope=["runtime/suite.py"], consequence_class="decision_build")
    rec = next(d for d in s.inbox.list() if d["id"] == out["id"])
    check("wire-door surface_build_intent still mints intent=build", Suite.is_build_intent(rec) is True)
    check("wire-door item resolved=None (operator approves via /api/resolve)", rec.get("resolved") is None)

    # is_build_intent semantics unchanged: a NON-build review item is NOT a build-intent
    rid = s.inbox.surface("review", {"summary": "a plain review"}, default="reject", resolved=None)
    nonrec = next(d for d in s.inbox.list() if d["id"] == rid)
    check("a plain review item is NOT a build-intent (is_build_intent unchanged)",
          Suite.is_build_intent(nonrec) is False)

    # the same address-derived path (surface_intent_at — the wire-door's /api/intent-at) still works
    addr = pick_registered_element(s)
    out2 = s.surface_intent_at(addr, "intent-at door change", source="operator")
    rec2 = next(d for d in s.inbox.list() if d["id"] == out2["id"])
    check("wire-door surface_intent_at still mints intent=build", Suite.is_build_intent(rec2) is True)


def test_reaches_wire_trigger_built_not_armed():
    """EXECUTION-reachability (not just is_build_intent equivalence): approve a request_change item via
    the operator-only resolve_surfaced under the DEFAULT (inert) wire — prove it ROUTES through the SAME
    resolve→dispatch trigger a wire-door intent does, and stays SAFE-BY-DEFAULT (launch NEVER called, 🔒
    built-not-armed). The wire is NOT armed (COMPANY_WIRE_PERMISSION unset) and NO real claude -p fires
    (launch is faked + asserted uncalled). This converts 'WILL reach the wire' into 'reaches the SAME
    trigger path, gated only by arming'."""
    from runtime import implement as impl
    os.environ.pop("COMPANY_WIRE_PERMISSION", None)            # DEFAULT 'plan' (inert)
    s = fresh_suite()
    calls = []
    orig_launch = impl.launch
    impl.launch = lambda *a, **k: calls.append((a, k)) or {"finished": True, "success": True,
                                                           "exit_code": 0, "summary": "x", "changed_files": []}
    try:
        # mint via the conversational verb (the bridge), then operator-approve (operator-only).
        out = s._dispatch_rhm_action(
            {"verb": "request_change", "change": "tighten this", "target": "ui://toolbar/run"}, graph_id="g")
        sid = out["surfaced"]
        rec = next(d for d in s.inbox.list() if d["id"] == sid)
        check("the request_change item is a dispatchable build-intent (is_build_intent True)",
              Suite.is_build_intent(rec) is True)
        check("wire is NOT armed by default (built-not-armed)", impl.wire_armed() is False)
        verdict = s.resolve_surfaced(sid, "approve", reason="authorize this build")
        check("operator approve recorded (operator-only resolve unchanged)", verdict["resolved"] is True)
        # SAFE-BY-DEFAULT: the trigger did NOT dispatch (launch never called) — same as a wire-door intent.
        check("implement.launch was NEVER called (no self-modify; 🔒 holds)", len(calls) == 0)
        check("NO decision.dispatch event under the default posture (loop did not close)",
              not any(e.get("kind") == "decision.dispatch" for e in s.store.events_since(-1)))
        check("the request_change item did NOT reach status=implemented under default",
              s.inbox.get(sid)["status"] != "implemented")
    finally:
        impl.launch = orig_launch
        os.environ.pop("COMPANY_WIRE_PERMISSION", None)


def test_propose_panel_extend_unchanged():
    """propose/panel/extend (Channel A — NET-NEW components via /api/apply) are NOT build-intents and are
    NOT touched by the new verb. They surface drafts; they never reach the claude -p wire."""
    s = fresh_suite()
    # propose drafts a node-type → surfaces; the surfaced item is NOT a build-intent (intent!='build')
    p = s._dispatch_rhm_action(
        {"verb": "propose", "name": "doubler", "spec": "a node that doubles its numeric input"}, graph_id="g")
    check("propose still surfaces a draft (did=propose or ask)", p.get("did") in ("propose", "ask"))
    if p.get("surfaced"):
        prec = next(d for d in s.inbox.list() if d["id"] == p["surfaced"])
        check("a propose draft is NOT a build-intent (Channel A unchanged)",
              Suite.is_build_intent(prec) is False)
    # the refuse-tail still enforces the whitelist — a non-RHM verb is refused
    r = s._dispatch_rhm_action({"verb": "apply", "name": "x"}, graph_id="g")
    check("a forbidden verb (apply) is still refused (E6 no-bypass)", r.get("did") == "none" and "refused" in r)


if __name__ == "__main__":
    test_spec_derivation()
    test_named_address_mints_build_intent()
    test_indicated_locus_used()
    test_explicit_target_beats_stale_locus()
    test_named_element_by_name()
    test_unresolvable_target_asks_not_mints()
    test_wire_door_unchanged()
    test_reaches_wire_trigger_built_not_armed()
    test_propose_panel_extend_unchanged()
    print(f"\nconversational_build_acceptance: {PASS} checks passed")
