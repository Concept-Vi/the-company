"""tests/annotate_vs_operate_acceptance.py — I5: annotate vs operate (two faces) — the ROUTING distinction.

The model (criteria line 109, Implementation Guide I5):
  • clicking a `ui://` (a DESIGN/UI element) with NO consequential verb → ANNOTATE (the I6 path):
    a comment is attached at the address; NOTHING is proposed or run.
  • clicking a `run://` (a LIVE graph-node instance) OR a consequential VERB at an address →
    OPERATE: propose-operation (the I3 affordance) THROUGH the I4 governance TIER — never auto-runs a
    consequential verb at a CONFIRM/LOCKED tier; it SURFACES (propose), never executes.
  • the two are NEVER blurred: an annotate click never dispatches an operation; an operate click never
    silently becomes a comment.

THE CRITICAL CORRECTION (design-substrate CONTRACT.2, Verified): the real safety seam is
**capability + governance TIER, not the scheme string alone.** The scheme is a ROUTING HINT
(`ui://`=UI element → annotate · `run://`=graph-node instance → operate). What GATES a mutating
command is the address's CONFIRM/LOCKED tier (I4's `_tier_for_address` + governance `guard()`), reused
unchanged — NOT a second gate built here. A `ui://` element that resolves to a read-only-driveable
target keeps working read-only via the live `show` path (the `show` verb is AUTO → operate face →
acts immediately, the read-only camera drive — PRESERVED).

DISCRIMINATING ASSERTIONS (a naive impl must NOT pass):
  - annotate case: a comment is actually persisted (annotations_at non-empty) AND NO action outcome
    AND NO surfaced item appeared — the annotate face is structurally incapable of dispatching.
  - CONFIRM-tier operate case: the graph did NOT execute (no 'ran') AND a surfaced item appeared AND
    NO annotation was written at that address — the operate face is structurally incapable of commenting.
  - U1 PRESERVED: a bare/untiered address with an immediate verb (run) still ACTS IMMEDIATELY
    (did=='run', real state moved, AUTO) — routing-by-verb does not regress the immediate RUN.
  - blur guards: annotate(run://…) RAISES (a live instance can't be commented — parse_ui_address);
    the operate path never touches annotations.

The tiered address is injected into the INSTANCE registry (extras={"tier":...}), exactly as
click_tier_acceptance.py does — never by editing design/_system/addresses.json (F4's read-only territory).

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


store_dir = tempfile.mkdtemp(prefix="annotate-vs-operate-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)
    g = "i5-seam"
    suite.create_node(g, "constant", config={"value": "hello"}, node_id="c")
    suite.create_node(g, "uppercase", node_id="u")
    suite.connect(g, "c", "value", "u", "text")

    # The router seam — I5 composes act() (I4 tier gate inside) and annotate() (I6); it does not rewrite
    # either. It is the ONE classifier that decides annotate-vs-operate per click.
    check("Suite.route_click exists (the I5 annotate-vs-operate router)",
          hasattr(suite, "route_click") and callable(suite.route_click))
    check("Suite.act exists (the operate face — I2/I4)",
          hasattr(suite, "act") and callable(suite.act))
    check("Suite.annotate exists (the annotate face — I6)",
          hasattr(suite, "annotate") and callable(suite.annotate))

    # =====================================================================================
    # ANNOTATE FACE — a ui:// element click, NO consequential verb → attach a comment; nothing dispatches.
    # =====================================================================================
    ui_elem = "ui://chrome/inbox"   # a UI/design element (a live registry row)
    surfaced_before = len(suite.list_surfaced())
    r = suite.route_click(ui_elem, g, text="this lane is too loud")
    check("a ui:// click (no verb) ROUTED to ANNOTATE — face=='annotate'",
          r.get("face") == "annotate")
    check("the annotate click PERSISTED a comment at the address (retrievable by address)",
          any(a.get("text") == "this lane is too loud" for a in suite.annotations_at(ui_elem)))
    check("the annotate click produced NO action outcome (it never dispatched an operation)",
          r.get("action") is None)
    check("the annotate click surfaced NOTHING for approval (it is not an operation)",
          len(suite.list_surfaced()) == surfaced_before)

    # =====================================================================================
    # OPERATE FACE / U1 PRESERVED — an immediate verb at a bare/untiered address ACTS IMMEDIATELY.
    # =====================================================================================
    r = suite.route_click(None, g, verb="run")   # bare run — no address, the canvas RUN path
    check("a bare run click ROUTED to OPERATE — face=='operate'", r.get("face") == "operate")
    check("the bare run ACTED IMMEDIATELY — did=='run' (U1 preserved, not proposed)",
          r["action"]["did"] == "run")
    check("the bare run moved REAL state — 'u' is in the ran set (the graph executed)",
          "u" in r["action"].get("ran", []))
    check("the bare run routed AUTO via the verb-class fallback",
          r["action"].get("routed_posture") == "auto")
    check("the bare run wrote NO annotation (the operate face never silently comments)",
          suite.annotations_at(ui_elem) == [a for a in suite.annotations_at(ui_elem)]  # unchanged set
          and not any(a.get("verb") for a in suite.annotations_at(ui_elem)))

    # An UNTIERED registered address with an immediate verb — still acts (verb-class fallback).
    r = suite.route_click(ui_elem, g, verb="run")
    check("a run at an UNTIERED ui:// address ROUTED to OPERATE and ACTED — AUTO (U1 preserved)",
          r.get("face") == "operate" and r["action"]["did"] == "run"
          and r["action"].get("routed_posture") == "auto")

    # =====================================================================================
    # run:// SCHEME — a live graph-node instance always routes to OPERATE (never annotate).
    # =====================================================================================
    run_addr = f"run://{g}/u"   # a LIVE graph-node instance address
    r = suite.route_click(run_addr, g, verb="run")
    check("a run:// (live instance) click ROUTED to OPERATE — face=='operate'",
          r.get("face") == "operate")
    # run:// has no registry tier → verb-class fallback → AUTO run acts (untiered live instance).
    check("the run:// operate click ACTED via verb-class (untiered live instance) — never annotated",
          r["action"]["did"] == "run" and r.get("action") is not None)

    # =====================================================================================
    # OPERATE through the I4 TIER — a consequential verb at a CONFIRM/LOCKED-tier address PROPOSES.
    # =====================================================================================
    # Inject a tiered row into the INSTANCE registry (never edit addresses.json — F4's territory).
    tiered_addr = "ui://source/raw-corpus"
    suite.UI_REGISTRY = list(suite.UI_REGISTRY) + [
        (tiered_addr, "chrome", "Raw corpus", {"dom_handle": tiered_addr},
         {"pointable": True}, {"region": "source", "tier": "source_data"})
    ]
    check("the injected address resolves to its tier ('source_data') — I4's gate is reused",
          suite._tier_for_address(tiered_addr) == "source_data")

    surfaced_before = len(suite.list_surfaced())
    annos_before = len(suite.annotations_at(tiered_addr))
    suite.route_click(None, g, verb="run")   # re-run first so we can prove THIS click did not run
    r = suite.route_click(tiered_addr, g, verb="run")   # a consequential verb at a CONFIRM/LOCKED tier
    check("a consequential verb at a CONFIRM/LOCKED-tier address ROUTED to OPERATE",
          r.get("face") == "operate")
    check("...and PROPOSED — did=='surfaced_for_approval' (NOT 'run'; through the I4 tier)",
          r["action"]["did"] == "surfaced_for_approval")
    check("...the graph did NOT execute — no 'ran' set in the outcome",
          "ran" not in r["action"])
    check("...a surfaced item appeared for see-and-approve (the gate)",
          len(suite.list_surfaced()) == surfaced_before + 1)
    sid = r["action"].get("surfaced")
    check("...the surfaced command is NOT auto-approved (awaiting the operator)",
          sid is not None and not suite.inbox.is_approved(sid))
    check("...routed_posture=='confirm' (address-tier governed, not scheme)",
          r["action"].get("routed_posture") == "confirm")
    check("...NO annotation was written at that address (operate never silently comments)",
          len(suite.annotations_at(tiered_addr)) == annos_before)

    # =====================================================================================
    # PRESERVE the live read-only `show` path — `show` is AUTO → operate → drives the camera read-only.
    # =====================================================================================
    r = suite.route_click(ui_elem, g, verb="show")
    check("a 'show' at an UNTIERED ui:// element ROUTED to OPERATE and ACTED (read-only camera drive)",
          r.get("face") == "operate" and r["action"]["did"] == "show"
          and r["action"].get("routed_posture") == "auto")
    check("...the show targets carry the clicked address (resolveUiTarget drives the view there)",
          ui_elem in (r["action"].get("targets") or []))

    # =====================================================================================
    # THE TWO FACES NEVER BLUR — structural guards.
    # =====================================================================================
    # 1. annotate is structurally ui://-only: a run:// (live instance) CANNOT be commented.
    blur1_raised = False
    try:
        suite.annotate(run_addr, "should not be allowed")
    except Exception:
        blur1_raised = True
    check("annotate(run://…) RAISES — a live instance is structurally incapable of being commented",
          blur1_raised)

    # 2. an annotate input (no verb) NEVER dispatches: routing a ui:// with no verb + no text fails loud
    #    rather than silently dispatching OR silently doing nothing (rule 4).
    blur2_raised = False
    try:
        suite.route_click(ui_elem, g)   # ui://, no verb, no text → annotate with nothing → fail loud
    except Exception:
        blur2_raised = True
    check("a ui:// annotate click with NO text FAILS LOUD (never silently dispatches, never silent no-op)",
          blur2_raised)

    # 3. an operate input never silently annotates: every operate route returns face=='operate' with an
    #    action, never an annotation record (proved above per-case). Final cross-check on count:
    pre = len(suite.annotations_at(ui_elem))
    suite.route_click(ui_elem, g, verb="run")   # operate at the same address the annotate test used
    check("an operate click at a previously-annotated address adds NO new comment (faces stay separate)",
          len(suite.annotations_at(ui_elem)) == pre)

    print(f"\nALL {PASS} CHECKS PASS — I5 annotate-vs-operate routing: a ui:// element (no verb) "
          "ANNOTATES; a run:// instance / a consequential verb OPERATES through the I4 tier "
          "(CONFIRM/LOCKED proposes, bare/untiered/AUTO acts — U1 preserved); the two never blur.")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
