"""tests/act_endpoint_acceptance.py — I2: the /api/act emission seam (the emission RELOCATION).

A DETERMINISTIC human click replaces the model's unreliable prose-emission for the interactive
path (§21.4#1). This proves the seam end-to-end at the Suite level (`Suite.act`, the logic the
thin /api/act bridge route wraps — reachability is grepped separately):

  1. A click-shaped {verb, address, args} drives a verb THROUGH to a real result, with NO model
     and NO prose-parse (`_parse_rhm_action` is never touched) — the dispatch-bypass-prose proof.
  2. The 7-verb whitelist rides along for FREE (inside the dispatcher): a non-whitelisted verb is
     REFUSED with no effect, no raise — the no-bypass guarantee is preserved structurally.
  3. No-self-apply is preserved: propose/panel/extend SURFACE a draft for operator approval; they
     never self-apply (no node-type registered, no inbox auto-resolved).
  4. The confirmation is re-folded for EVERY verb (incl. consult's full answer fold) — never a
     silent success (AGENTS.md rule 4).

COMPANY_TEST_RUN is set so any surfaced draft is tagged test_origin (inbox-hygiene, governance.py).
"""
import os, sys, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["COMPANY_TEST_RUN"] = "1"   # tag any surfaced draft as test_origin (inbox hygiene)

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


store_dir = tempfile.mkdtemp(prefix="act-endpoint-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)
    g = "act-seam"
    suite.create_node(g, "constant", config={"value": "hello"}, node_id="c")
    suite.create_node(g, "uppercase", node_id="u")
    suite.connect(g, "c", "value", "u", "text")

    # =====================================================================================
    # 1. THE SEAM: a click-shaped {verb, address, args} → dispatch → result, NO prose.
    # =====================================================================================
    check("Suite.act exists (the operator-face emission seam)", hasattr(suite, "act") and callable(suite.act))

    # --- show: the click's ADDRESS is the locus, mapped to the verb's natural target slot (I1) ---
    res = suite.act("show", g, address="ui://chrome/inbox")
    check("a {verb:show, address:ui://chrome/inbox} click DISPATCHES to a show outcome",
          res["action"]["did"] == "show")
    check("the click's address resolved as the show target",
          "ui://chrome/inbox" in res["action"]["targets"])
    check("the operator sees a 'did X' confirmation (re-folded, not silent)",
          "moved your view" in res["reply"] and "ui://chrome/inbox" in res["reply"])
    check("the response is the same {reply, action} shape /api/chat returns",
          set(("reply", "action")).issubset(res.keys()))

    # --- run: a real verb driven to a real result (the canvas RUN, AUTO) ---
    before_files = set(os.listdir(NODES))
    res = suite.act("run", g)
    check("a {verb:run} click DISPATCHES and recomputes the graph",
          res["action"]["did"] == "run" and "u" in res["action"]["ran"])
    check("run's confirmation is re-folded for the operator", "ran:" in res["reply"])
    check("run routed through governance posture AUTO (verb-class, the chat() re-fold)",
          res["action"].get("routed_posture") == "auto")

    # --- the dispatch-bypass-prose PROOF: a malformed-prose-looking 'verb' is NOT prose-parsed;
    #     it is treated as a structured verb and refused by the dispatcher (no _parse_rhm_action). ---
    pre_hist = len(suite.chat_history(200))
    res = suite.act("ACTION: run", g)   # prose that the OLD path would parse — here it's a literal verb
    check("a prose-looking verb is NOT prose-parsed — refused as an unknown structured verb",
          res["action"]["did"] == "none")
    check("act() writes NO chat history (it is not the prose/chat path — pure structured dispatch)",
          len(suite.chat_history(200)) == pre_hist)

    # =====================================================================================
    # 2. THE WHITELIST RIDES ALONG (inside the dispatcher) — no-bypass preserved.
    # =====================================================================================
    snapshot = set(os.listdir(NODES))
    res = suite.act("apply", g, args={"id": "anything"})
    check("a click for 'apply' is REFUSED (whitelist, not a click-widened authority)",
          res["action"]["did"] == "none")
    check("the refusal does NOT raise — it returns a no-effect outcome (fail-soft, loud reply)",
          "couldn't do that" in res["reply"] or "not permitted" in str(res["action"]))
    check("a refused apply wrote NO node file", set(os.listdir(NODES)) == snapshot)

    res = suite.act("delete", g, address="ui://canvas/c", args={"node": "c"})
    check("a click for 'delete' is REFUSED", res["action"]["did"] == "none")
    check("the node was NOT deleted by a refused delete-click",
          any(n.id == "c" for n in suite._load(g).nodes))

    res = suite.act("write_file", g, args={"path": "/etc/x"})
    check("an arbitrary verb is REFUSED (whitelist, not blacklist)", res["action"]["did"] == "none")

    # =====================================================================================
    # 3. NO-SELF-APPLY: propose SURFACES a draft for operator approval — never self-applies.
    # =====================================================================================
    types_before = set(suite.list_types())
    surfaced_before = len(suite.list_surfaced())
    res = suite.act("propose", g, args={"name": "reverser", "spec": "reverse the input text"})
    check("a 'propose' click SURFACES a draft (did=propose), routed CONFIRM",
          res["action"]["did"] in ("propose", "ask") and res["action"].get("routed_posture") == "confirm")
    check("propose did NOT register a live node-type (no self-apply)",
          set(suite.list_types()) == types_before)
    check("propose surfaced an item for operator approval (the gate, not auto-resolved)",
          len(suite.list_surfaced()) == surfaced_before + 1)
    sid = res["action"].get("surfaced")
    check("the surfaced draft is NOT operator-approved (awaiting see-and-approve)",
          sid is not None and not suite.inbox.is_approved(sid))
    check("propose's confirmation tells the operator it's awaiting approval",
          "awaiting your approval" in res["reply"] or "asking rather than" in res["reply"])

    # =====================================================================================
    # 4. CONSULT fold: a consult click returns its FULL answer (not the silent else-branch).
    # =====================================================================================
    res = suite.act("consult", g, args={"query": "how does the run verb work"})
    check("a 'consult' click DISPATCHES and folds its FULL answer (📖), never silent",
          res["action"]["did"] == "consult" and res["reply"].startswith("📖") and len(res["reply"]) > 3)

    print(f"\nALL {PASS} CHECKS PASS — /api/act seam: click→dispatch (no prose), whitelist + "
          "no-self-apply preserved, confirmation re-folded")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
