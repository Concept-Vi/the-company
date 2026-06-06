"""tests/inbox_target_acceptance.py — L8 · inbox-target click-to-thing (§21.7#9, gain #9).

A surfaced inbox item carries its `ui://` target so clicking it can navigate + spotlight the
thing in context. Surfaced items are OPEN dicts (consumers read via `.get()` — seams-engine
Seam 2 CONFIRMED), so the target lands inside `payload` (the lower-risk open bag) with ZERO
reader changes. The FE composes the preserved `resolveUiTarget` keystone to navigate.

The target is derived by the EXISTING keystone `Suite._registry_ui_target` (node → ui://canvas/
<node>, node-less → ui://chrome/inbox) — registry-valid by construction, no fabrication — and put
DIRECTLY into the payload literal at surface time (governance.py / Inbox.surface UNCHANGED; the
target is payload content, not a rec-level field). present_current already stamps the same value
transiently at present-time (suite.py:2662-2664); L8 PERSISTS it so the item is clickable directly
in the inbox, not only inside a walkthrough.

What this proves (backend half — the click→navigate is the FE reusing resolveUiTarget):
  1. _registry_ui_target derives a navigable ui://canvas/<node> for a node-bound item, and that
     target sits inside `payload`, retrievable via `.get`.
  2. existing consumers (inbox_lanes / the surfaced-item readers) still work UNCHANGED with the
     added field — they `.get` and ignore it (PRESERVE, seams-engine Seam 2).
  3. an item with NO target surfaces fine (no error) and reads exactly as before.
  4. the stored target is one of the forms resolveUiTarget actually accepts (ui://… ; NOT run://,
     which would fail driveCanvas). The grammar discriminator guards against a "test passes but the
     click navigates nowhere" green-paint.
  5. surface_output (the `result` item about a node) PERSISTS ui://canvas/<node-id> in its payload —
     the demonstrative, non-circular, resolvable target: click → camera flies to the node it's about.
  6. node-less items are left targetless (no circular inbox→inbox link); they render as today.
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


def accepted_by_resolver(t: str) -> bool:
    """Mirror the resolveUiTarget grammar (useAppController.ts:733-804): a target navigates iff
    it is a ui:// address (region-only OR region/element, validated against the registry FE-side)
    OR ui://canvas/<node-id> (camera). A bare node-id also works but we never store those here.
    A run:// string is NOT accepted (it would hit driveCanvas and fail loud). This is the
    discriminator that catches a stored-but-unnavigable target."""
    return isinstance(t, str) and t.startswith("ui://")


store_dir = tempfile.mkdtemp(prefix="inbox-target-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    # --- 1: a surfaced item carries an additive ui:// target inside payload (retrievable via .get) ---
    # The target is derived by the EXISTING keystone _registry_ui_target (node → ui://canvas/<node>,
    # node-less → ui://chrome/inbox) — registry-valid by construction, no fabrication. It lands inside
    # `payload` (the open bag consumers already `.get` — seams-engine Seam 2), put there directly as a
    # fresh payload-literal key (no Inbox.surface change, governance.py untouched).
    target = suite._registry_ui_target({"node": "c"})
    check("the keystone derives a navigable ui://canvas/<node> for a node-bound item",
          target == "ui://canvas/c")
    sid = suite.inbox.surface("review", {"name": "x", "title": "t", "ui_target": target},
                              default="reject", resolved=None)
    d = suite.inbox.get(sid)
    check("ui:// target lands inside payload (the open bag)", d["payload"].get("ui_target") == target)
    check("stored target is a form resolveUiTarget accepts (navigable, not run://)",
          accepted_by_resolver(d["payload"].get("ui_target")))

    # --- 2: existing consumers still work UNCHANGED with the added field (preserve via .get) ---
    lanes = suite.inbox_lanes()
    esc_ids = {x["id"] for x in lanes["live_escalations"]}
    check("inbox_lanes still classifies the item (consumer reads via .get, ignores the field)",
          sid in esc_ids)
    check("the surfaced-item readers (action/payload/resolved) are intact",
          d["action"] == "review" and d.get("resolved") is None and d["payload"]["name"] == "x")

    # --- 3: an item with NO target surfaces fine (no error), reads exactly as before ---
    sid2 = suite.inbox.surface("code_build", {"name": "b", "code": "y"}, default="reject", resolved=None)
    d2 = suite.inbox.get(sid2)
    check("an item with no target surfaces fine — no ui_target key, no error",
          "ui_target" not in d2["payload"] and d2["payload"]["code"] == "y")
    lanes2 = suite.inbox_lanes()
    check("the no-target item is a live escalation (behaves as today)",
          sid2 in {x["id"] for x in lanes2["live_escalations"]})

    # --- 4: a node-less item gets NO forced target (no circular inbox→inbox link) ---
    # surface_output is the demonstrative case; node-less items (build_result_review, ideas) are left
    # targetless so the FE renders no useless link — they behave exactly as today.
    sid3 = suite.inbox.surface("code_build", {"name": "node-less"}, default="reject", resolved=None)
    check("a node-less item carries no ui_target (renders as today — no circular link)",
          "ui_target" not in suite.inbox.get(sid3)["payload"])

    # --- 5: surface_output attaches the demonstrative ui://canvas/<node-id> (resolvable, non-circular) ---
    # build a tiny runnable graph: a constant node has an output the instant it runs.
    gid = "l8-target-graph"
    nid = suite.create_node(gid, "constant", config={"value": "hello"}, node_id="c")
    suite.run(gid)
    ro = suite.surface_output(gid, nid)               # returns the surfaced-decision shape
    rsid = ro["surfaced"] if isinstance(ro, dict) and "surfaced" in ro else (
        ro["id"] if isinstance(ro, dict) and "id" in ro else ro)
    rd = suite.inbox.get(rsid)
    tgt = rd["payload"].get("ui_target")
    check("surface_output attaches ui://canvas/<node-id> (camera to the node it's about)",
          tgt == f"ui://canvas/{nid}")
    check("the result-item target is resolver-accepted (navigable)", accepted_by_resolver(tgt))

    # --- 7: the I4 surfaced_for_approval item carries its CLICKED ui:// address as the target ---
    # The GUIDE's named second case: "if the item already has an address/locus, use it." A click on a
    # CONFIRM/LOCKED-tier address SURFACES for see-and-approve (act → did=='surfaced_for_approval'); that
    # item concerns the very element awaiting approval, so it carries that ui:// address as ui_target →
    # click the inbox item → resolveUiTarget drives the view back to the gated element. (Inject a tiered
    # row into the INSTANCE registry, mirroring click_tier_acceptance — never edit addresses.json here.)
    tiered_addr = "ui://source/raw-corpus"
    suite.UI_REGISTRY = list(suite.UI_REGISTRY) + [
        (tiered_addr, "chrome", "Raw corpus", {"dom_handle": tiered_addr},
         {"pointable": True}, {"region": "source", "tier": "source_data"})
    ]
    res = suite.act("run", gid, address=tiered_addr)     # SAME run verb, a CONFIRM/LOCKED-tier ADDRESS
    check("a CONFIRM-tier click surfaced for approval (did=='surfaced_for_approval')",
          res["action"]["did"] == "surfaced_for_approval")
    i4 = suite.inbox.get(res["action"]["surfaced"])
    check("the surfaced_for_approval item carries the CLICKED ui:// address as its target",
          i4["payload"].get("ui_target") == tiered_addr)
    check("the I4 target is resolver-accepted (navigable — drives view to the gated element)",
          accepted_by_resolver(i4["payload"].get("ui_target")))
    # and a click whose locus is NOT a ui:// form carries NO target (guard; behaves as today)
    nonui_addr = "run://some/elsewhere"
    suite.UI_REGISTRY = list(suite.UI_REGISTRY) + [
        (nonui_addr, "chrome", "Elsewhere", {"dom_handle": nonui_addr},
         {"pointable": True}, {"region": "x", "tier": "source_data"})
    ]
    res2 = suite.act("run", gid, address=nonui_addr)
    i4b = suite.inbox.get(res2["action"]["surfaced"])
    check("a non-ui:// gated locus carries no ui_target (guard — no driveCanvas fail, behaves as today)",
          "ui_target" not in i4b["payload"])

    print(f"\nALL {PASS} CHECKS PASS — surfaced items carry a navigable ui:// target in payload; "
          f"consumers preserved (read via .get); no-target items behave as today; "
          f"surface_output points at the node it's about (resolveUiTarget-accepted form)")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
