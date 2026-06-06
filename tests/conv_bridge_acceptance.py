"""tests/conv_bridge_acceptance.py — X6 (Convergence) · the ui://↔run:// bridge.

WHAT X6 IS (Convergence Completion Criteria X6 + Research Synthesis Round 4):
R2 (the live address-keyed context accumulator) lives ENTIRELY in the `ui://` tree. `_r2_ancestors`
returns `[]` for any non-`ui://` locus (suite.py:1136), so the run://-keyed strata — **version-history
(L6 `ref_versions`)** and node-instance **addressed events** — can NEVER inherit into the context. The
coordinate system is split in two: ui:// memory resolves; run:// memory is structurally excluded.

X6 BRIDGES the split. The operator's live locus is ALWAYS a `ui://` address (`current_locus()` holds a
ui:// only; `_chat_context` sets it from the indicated ui:// element). A canvas node carries TWO
addresses for the SAME thing: `ui://canvas/<node>` (the UI target — `_registry_ui_target`) and
`run://<graph>/<node>` (where the scheduler's `set_ref` writes its output versions L6, and where its
node-instance events are addressed — suite.py:515/539/549). So the bridge is approach (b): at a
`ui://canvas/<node>` locus, map to the node's `run://<graph>/<node>` counterpart and ALSO gather its
run://-keyed strata (the L6 version-history via `ref_versions`, the node events via the SAME
`_r2_events_at` reader) — so at the locus BOTH schemes' memory resolves into one bounded window.

WHY (b) NOT (a): no production caller ever passes a `run://` locus — `current_locus()` is ui:// only,
and `ingest_comment`/`annotate` RAISE on run://. A "make `_r2_ancestors` walk a run:// locus" widening
would be dead code (nothing reaches it with run://). The bridge MUST fire from the ui:// locus and
resolve its run:// counterpart. The graph_id is NOT held on the Suite (every verb takes it as a param,
node-ids are NOT globally unique — `llm-1` recurs across graphs); the production caller `_chat_context`
HOLDS graph_id as ground truth, so it is THREADED (optional, default None) into the gather. No
enumeration, no fabrication: if graph_id is None or the node is not in that graph, the run:// step is
skipped (the ui:// path is byte-for-byte unchanged).

CROSS-SCHEME PROXIMITY: a `run://` address shares no prefix with the `ui://` locus under
`address_tree_distance` → it would score maximally-FAR and lose the budget cap (present-but-inert). But
the run:// strata ARE the SAME node as the ui:// locus — so each bridged item's SCORING `address` is set
to the ui:// locus (proximity 0, scoring reused UNCHANGED), while its `text` labels it [version]/[run
event]. This is the honest cross-scheme distance: same node, distance 0.

PRESERVE (HARD CONSTRAINTS — verified here):
  - the ui:// ancestors walk + the ui:// gather (annotations/chats/events) is byte-for-byte unchanged
    for a ui:// locus with no graph_id (addr_context_acceptance 34/34 re-proven separately).
  - the decay + R2_BUDGET cap + X8 dedup apply to the bridged run:// items too (one window, bounded).
  - REUSE the existing retrievals — `ref_versions` (L6) + `_r2_events_at` — NO new store.
  - fail-loud: a malformed/unresolvable run:// address → skip with a note, never a crash of the gather.

RED-FIRST: today (before X6) the run://-keyed version-history is ABSENT from the gather at a
`ui://canvas/<node>` locus — the scheme short-circuit excludes it. This test asserts it PRESENT after.

COMPANY_TEST_RUN is set for inbox-hygiene parity with the sibling suites.
"""
import os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ["COMPANY_TEST_RUN"] = "1"

from datetime import datetime, timezone
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


store_dir = tempfile.mkdtemp(prefix="conv-bridge-test-")
try:
    root = os.path.join(store_dir, "store")
    store = FsStore(root)
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    GID = "bridgegraph"
    NODE = "u"                                   # single-output node → set_ref writes the BARE run addr
    UI_LOCUS = f"ui://canvas/{NODE}"             # the ui:// locus the operator is AT (the canvas node)
    RUN_ADDR = f"run://{GID}/{NODE}"             # its run:// counterpart (where versions + events accrue)

    # a constant -> uppercase pipeline; running it fires set_ref at run://<g>/<node> → an L6 version trail.
    suite.create_node(GID, "constant", config={"value": "alpha"}, node_id="c")
    suite.create_node(GID, "uppercase", node_id=NODE)
    suite.connect(GID, "c", "value", NODE, "text")
    suite.run(GID)                               # version 1: "ALPHA" written at run://bridgegraph/u
    # change the upstream + re-run → a SECOND version accrues (the temporal trail is real, not a stub)
    suite.set_config(GID, "c", {"value": "beta"})
    suite.run(GID)                               # version 2: "BETA"

    # SANITY (the substrate this bridge reaches actually has content) — L6 trail exists at the run addr.
    rv = suite.ref_versions(RUN_ADDR)
    check("SANITY: ref_versions(run addr) has a multi-entry L6 trail (the run://-keyed memory exists)",
          rv["count"] >= 2)
    version_previews = " ".join((v.get("preview") or "") for v in rv["versions"])
    check("SANITY: the L6 trail carries the prior version content (ALPHA/BETA)",
          "ALPHA" in version_previews and "BETA" in version_previews)

    # ============================================================================================
    # PART 1 — THE BRIDGE (RED today): at a ui://canvas/<node> locus, the run://-keyed L6 versions
    #           + node events resolve INTO the gather. graph_id is THREADED (the caller holds it).
    # ============================================================================================
    bridged = suite._r2_gather(UI_LOCUS, graph_id=GID)
    btext = "\n".join(it.get("text", "") for it in bridged)
    check("BRIDGE: the run://-keyed L6 version-history resolves at the ui:// canvas-node locus",
          "ALPHA" in btext or "BETA" in btext)
    check("BRIDGE: a bridged version item is LABELLED (legible as version-history, not a bare blob)",
          any("version" in (it.get("text", "") or "").lower() for it in bridged))
    # the node-instance addressed events (create/run echoes at run://<g>/<node>) also reach the gather.
    check("BRIDGE: the node-instance addressed events resolve at the ui:// canvas-node locus",
          any(it.get("kind") == "event" for it in bridged))

    # CROSS-SCHEME PROXIMITY: a bridged run:// item must score as proximity-0 (same node as the locus),
    # NOT maximally far — else it always loses the cap and the bridge is present-but-inert.
    now = datetime.now(timezone.utc)
    bridged_items = [it for it in bridged
                     if "version" in (it.get("text", "") or "").lower() or it.get("kind") == "event"]
    check("PROXIMITY: at least one bridged run:// item is gathered", len(bridged_items) >= 1)
    a_ui_only = {"text": "x", "address": UI_LOCUS, "ts": datetime.now(timezone.utc).isoformat(),
                 "kind": "annotation"}
    for bi in bridged_items:
        check(f"PROXIMITY: bridged item ({bi.get('kind')}) scores at locus-distance 0 (same node, not far)",
              suite.address_tree_distance(UI_LOCUS, bi.get("address", "")) == 0)

    # ============================================================================================
    # PART 2 — PRESERVE the ui:// path byte-for-byte (no graph_id → exactly the old gather)
    # ============================================================================================
    suite.annotate(UI_LOCUS, "UI-ANNOTATION attached at the canvas-node ui:// address")
    ui_only = suite._r2_gather(UI_LOCUS)         # NO graph_id → the run:// step must NOT fire
    ui_text = "\n".join(it.get("text", "") for it in ui_only)
    check("PRESERVE: with NO graph_id the ui:// gather still resolves the ui:// annotation",
          "UI-ANNOTATION" in ui_text)
    check("PRESERVE: with NO graph_id the run://-keyed versions do NOT appear (ui:// path unchanged)",
          "ALPHA" not in ui_text and "BETA" not in ui_text)
    # the bridged gather is a SUPERSET — it still carries the ui:// annotation alongside the run:// strata.
    bridged2 = suite._r2_gather(UI_LOCUS, graph_id=GID)
    b2text = "\n".join(it.get("text", "") for it in bridged2)
    check("PRESERVE: the bridged gather is ADDITIVE (ui:// annotation still present alongside run://)",
          "UI-ANNOTATION" in b2text and ("ALPHA" in b2text or "BETA" in b2text))

    # NODE-MEMBERSHIP GUARD (rule 4 — no silent wrong value): a locus naming a node that does NOT exist
    # in graph_id must NOT pull some other graph's same-id node history. (node-ids are not graph-unique.)
    ghost = suite._r2_gather("ui://canvas/does-not-exist", graph_id=GID)
    gtext = "\n".join(it.get("text", "") for it in ghost)
    check("GUARD: a canvas-node not in graph_id pulls NO run:// strata (no silent wrong-node history)",
          "ALPHA" not in gtext and "BETA" not in gtext)

    # ============================================================================================
    # PART 3 — END-TO-END through the production chat path (graph_id threaded the WHOLE way)
    # ============================================================================================
    # set the locus by indicating the canvas-node ui:// address, then resolve context AT it.
    suite._chat_context(GID, focus={"selected": [UI_LOCUS]})
    check("E2E: the ui:// canvas-node locus is set after indicating", suite.current_locus() == UI_LOCUS)
    ctx = suite._chat_context(GID, focus={"selected": [UI_LOCUS]})
    R2_HEAD = "CONTEXT RESOLVED AT YOUR LOCUS"
    check("E2E: the R2 block is present at the canvas-node locus", R2_HEAD in ctx)
    r2_block = ctx[ctx.index(R2_HEAD):]
    check("E2E: the run://-keyed version-history resolves INTO the chat-path R2 block (the bridge fires "
          "end-to-end)", "ALPHA" in r2_block or "BETA" in r2_block)
    # PRESERVE: the other _chat_context blocks survive unchanged.
    check("E2E-PRESERVE: presence-modes block still present", "presence modes:" in ctx)
    check("E2E-PRESERVE: RHM verbs block still present", "RHM verbs you can perform:" in ctx)
    check("E2E-PRESERVE: the I1 INDICATING block still present", "INDICATING" in ctx.upper())

    # ============================================================================================
    # PART 4 — BOUNDED + DEDUP across both schemes (the window stays bounded; one cap, both schemes)
    # ============================================================================================
    capped = suite._r2_score_and_cap(bridged2, UI_LOCUS, now)
    capped_text = "\n".join(it.get("text", "") for it in capped)
    check("BOUNDED: the bridged+capped slice is ≤ R2_BUDGET chars (one bounded window, both schemes)",
          len(capped_text) <= suite.R2_BUDGET)
    # dedup identity is preserved across schemes — no item appears more than once by (kind,address,text).
    ids = [(it.get("kind"), it.get("address"), it.get("text")) for it in bridged2]
    check("DEDUP: every gathered item is unique by (kind,address,text) across both schemes",
          len(ids) == len(set(ids)))

    # ============================================================================================
    # PART 5 — FAIL-LOUD: a malformed/unresolvable run:// address → skip with a note, never crash
    # ============================================================================================
    # Force ref_versions to RAISE (it raises on a non-run:// / malformed address by contract). The bridge
    # CONSTRUCTS the run:// address from the locus+graph; if that resolution is unhappy the gather must
    # SKIP the run:// strata (warn), never crash the per-turn slice (rule 4 — fail-loud-LEGIBLE).
    orig_ref_versions = suite.ref_versions
    def _boom(addr, limit=25):
        raise ValueError(f"forced malformed/unresolvable: {addr}")
    suite.ref_versions = _boom
    try:
        safe = suite._r2_gather(UI_LOCUS, graph_id=GID)     # must NOT raise
        check("FAIL-LOUD: a raising ref_versions does NOT crash the gather (returns a result)",
              isinstance(safe, list))
        # the ui:// strata still resolve (the run:// failure is isolated, never poisons the whole gather).
        safe_text = "\n".join(it.get("text", "") for it in safe)
        check("FAIL-LOUD: the ui:// strata STILL resolve when the run:// step fails (isolated, not all-or-nothing)",
              "UI-ANNOTATION" in safe_text)
    finally:
        suite.ref_versions = orig_ref_versions

    # ============================================================================================
    # PART 6 — COEXISTENCE under realistic load: a run-BURST must NOT starve the operator's ui:// memory
    # ============================================================================================
    # The cross-scheme proximity fix (run:// items at distance 0) makes them maximally COMPETITIVE in the
    # cap — a freshly-run node's many full-preview versions would, by recency, EVICT the operator's
    # comments at the same locus ("BOTH schemes resolve" → "run:// evicts ui://"). R2_RUN_VERSIONS bounds
    # the run:// contribution so both coexist. Discriminating test: a comment made BEFORE a burst of large
    # runs must still survive the bounded window.
    bs = FsStore(os.path.join(store_dir, "burst"))
    suiteB = Suite(bs, reg, nodes_dir=NODES)
    BG, BN = "burstgraph", "u"
    BUI = f"ui://canvas/{BN}"
    suiteB.create_node(BG, "constant", config={"value": "seed"}, node_id="c")
    suiteB.create_node(BG, "uppercase", node_id=BN)
    suiteB.connect(BG, "c", "value", BN, "text")
    # the operator's comment lands FIRST (older than the burst that follows)
    suiteB.annotate(BUI, "OPERATOR-COMMENT-BURST made before a flood of node runs")
    # a BURST of large-output runs (each output ≥150 chars → full-160-char previews, the LLM/content case)
    for i in range(30):
        suiteB.set_config(BG, "c", {"value": f"v{i:02d}-" + ("y" * 160)})
        suiteB.run(BG)
    bb = suiteB._r2_gather(BUI, graph_id=BG)
    bcap = suiteB._r2_score_and_cap(bb, BUI, datetime.now(timezone.utc))
    bctext = "\n".join(it.get("text", "") for it in bcap)
    n_versions_in_cap = sum(1 for it in bcap if it.get("kind") == "version")
    check("COEXIST: the run:// version contribution is BOUNDED (≤ R2_RUN_VERSIONS) so it can't flood",
          n_versions_in_cap <= suiteB.R2_RUN_VERSIONS)
    check("COEXIST: the operator's ui:// comment SURVIVES a 30-run burst at the same locus (not evicted)",
          "OPERATOR-COMMENT-BURST" in bctext)
    check("COEXIST: the bridged versions ALSO survive alongside the comment (both schemes present)",
          n_versions_in_cap >= 1)
    check("COEXIST: R2_RUN_VERSIONS is a named config constant (D2/X17-configurable, not a bare literal)",
          hasattr(suiteB, "R2_RUN_VERSIONS"))

    print(f"\nPASS — {PASS} checks (X6 · the ui://↔run:// bridge)")
finally:
    import shutil
    shutil.rmtree(store_dir, ignore_errors=True)
