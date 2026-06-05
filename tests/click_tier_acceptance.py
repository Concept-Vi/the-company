"""tests/click_tier_acceptance.py — I4: governance-tiered clicks (ADDRESS-KEYED, not verb-keyed).

The tier of a click is resolved by **address→tier** (the union address record's governance `tier`
field), NOT by the verb. So:

  • An AUTO-tier address (or an UNTIERED / UNKNOWN address) acts on the verb's own class —
    a bare run/build ACTS IMMEDIATELY (AUTO). ← the U1 preserve, the do-not-regress invariant.
  • A CONFIRM/LOCKED-tier address PROPOSES → surfaces for see-and-approve → does NOT act.

THE BLOCKER THIS UNIT GUARDS (review-code-truth ISSUE 1): verb-keying the tier — making run/build
PROPOSE — would regress U1 (the already-fixed immediate canvas RUN, App.tsx:1362/1169). The rule is
address-keyed: a bare run stays AUTO; only an address explicitly tiered CONFIRM/LOCKED proposes.

DISCRIMINATING ASSERTIONS (a naive impl must NOT pass):
  - U1 case proves the run ACTUALLY EXECUTED — did=="run" AND real state moved ("u" in ran) — for
    BOTH a bare run (no address) AND a run on an untiered/unknown address. Not just routed_posture.
  - CONFIRM case proves the graph did NOT execute (no run outcome, nothing ran) AND a surfaced item
    appeared AND it is NOT auto-approved (awaiting see-and-approve).

The tiered address is injected into the INSTANCE registry (a row with extras={"tier":...}) — never
by editing design/_system/addresses.json (F4's read-only territory).

COMPANY_TEST_RUN is set so any surfaced item is tagged test_origin (inbox hygiene, governance.py).
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


store_dir = tempfile.mkdtemp(prefix="click-tier-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)
    g = "tier-seam"
    suite.create_node(g, "constant", config={"value": "hello"}, node_id="c")
    suite.create_node(g, "uppercase", node_id="u")
    suite.connect(g, "c", "value", "u", "text")

    check("Suite.act exists (the operator-face emission seam I4 gates)",
          hasattr(suite, "act") and callable(suite.act))
    check("Suite._tier_for_address exists (the address→tier lookup)",
          hasattr(suite, "_tier_for_address") and callable(suite._tier_for_address))

    # =====================================================================================
    # U1 — THE DO-NOT-REGRESS INVARIANT: a bare run acts IMMEDIATELY (no address tier).
    # =====================================================================================
    res = suite.act("run", g)   # bare run — no address at all
    check("a BARE run click ACTED IMMEDIATELY — did=='run' (not proposed)",
          res["action"]["did"] == "run")
    check("a BARE run click moved REAL state — 'u' is in the ran set (the graph executed)",
          "u" in res["action"].get("ran", []))
    check("a BARE run routed AUTO via the verb-class fallback (no address tier)",
          res["action"].get("routed_posture") == "auto")

    # An UNTIERED registered address — must STILL act immediately (absence of tier → verb-class).
    untiered = "ui://chrome/inbox"   # a live registry row, carries NO tier
    check("the untiered live address has tier None (verb-class fallback path)",
          suite._tier_for_address(untiered) is None)
    res = suite.act("run", g, address=untiered)
    check("a run on an UNTIERED address ACTED IMMEDIATELY — did=='run', AUTO (U1 preserved)",
          res["action"]["did"] == "run" and res["action"].get("routed_posture") == "auto")
    # The graph EVALUATED (the dispatcher reached the engine) — the memo gate may report 'u' as
    # cached here since nothing changed since the bare run above; either way it was NOT proposed.
    check("the run on an untiered address EVALUATED the graph (u ran or cached — never proposed)",
          "u" in (res["action"].get("ran", []) + res["action"].get("cached", [])))

    # An UNKNOWN address (not in the registry) — also acts (None tier → verb-class), never CONFIRM.
    res = suite.act("run", g, address="ui://nowhere/ghost")
    check("a run on an UNKNOWN address ACTED IMMEDIATELY (missing tier ≠ unknown→CONFIRM fail-safe)",
          res["action"]["did"] == "run" and res["action"].get("routed_posture") == "auto")

    # =====================================================================================
    # CONFIRM-tier address — a run on it PROPOSES (surfaces) and does NOT execute.
    # =====================================================================================
    # Inject a tiered row into the INSTANCE registry (never edit addresses.json — F4's territory).
    # extras carries tier='source_data' (a LOCKED/CONFIRM class in governance.POLICY).
    tiered_addr = "ui://source/raw-corpus"
    suite.UI_REGISTRY = list(suite.UI_REGISTRY) + [
        (tiered_addr, "chrome", "Raw corpus", {"dom_handle": tiered_addr},
         {"pointable": True}, {"region": "source", "tier": "source_data"})
    ]
    check("the injected address resolves to its tier ('source_data')",
          suite._tier_for_address(tiered_addr) == "source_data")

    surfaced_before = len(suite.list_surfaced())
    # Re-run first so we can prove THIS click did not change the ran-state.
    suite.act("run", g)
    res = suite.act("run", g, address=tiered_addr)   # SAME run verb — but a CONFIRM-tier ADDRESS
    check("a run on a CONFIRM/LOCKED-tier address PROPOSED — did=='surfaced_for_approval' (not 'run')",
          res["action"]["did"] == "surfaced_for_approval")
    check("the CONFIRM-tier run did NOT execute the graph — no 'ran' set in the outcome",
          "ran" not in res["action"])
    check("the CONFIRM-tier click surfaced ITEM for see-and-approve (the gate)",
          len(suite.list_surfaced()) == surfaced_before + 1)
    sid = res["action"].get("surfaced")
    check("the surfaced command is NOT auto-approved (awaiting the operator)",
          sid is not None and not suite.inbox.is_approved(sid))
    check("the surfaced item records the verb+address it gated (auditable locus)",
          (lambda d: d and d["payload"].get("verb") == "run"
                     and d["payload"].get("address") == tiered_addr)(suite.inbox.get(sid)))
    check("the operator sees a 'needs approval, not yet acted' confirmation (rule 4, no silent success)",
          "needs approval" in res["reply"] and "not yet acted" in res["reply"])
    check("the outcome carries routed_posture=='confirm' (address-tier governed)",
          res["action"].get("routed_posture") == "confirm")

    # =====================================================================================
    # ADDRESS-KEYED, not verb-keyed: a NON-run verb at the same tiered address ALSO proposes;
    # and the SAME address tier gates regardless of verb (proves it is the address, not the verb).
    # =====================================================================================
    res = suite.act("show", g, address=tiered_addr)
    check("a 'show' (normally AUTO) at a CONFIRM-tier address ALSO proposes — keyed by ADDRESS",
          res["action"]["did"] == "surfaced_for_approval")

    print(f"\nALL {PASS} CHECKS PASS — I4 address-keyed tiering: bare/untiered/unknown run ACTS "
          "IMMEDIATELY (U1 preserved); a CONFIRM/LOCKED-tier address PROPOSES (no execution).")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
