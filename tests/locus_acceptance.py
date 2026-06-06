"""tests/locus_acceptance.py — R1 · backend current-locus (the persisted `ui://` locus).

WHAT R1 IS (seams-rhm.md Seam 4): today there is NO backend locus — the operator's locus
exists ONLY FE-side, shipped per-request as `focus.selected` (canvas-node + now, after I1, a
`ui://` address), and NOTHING is remembered between calls ("there is no stored current-locus
anywhere in suite/store"). R1 adds a backend-HELD current `ui://` locus:

  1. the backend HOLDS the operator's current `ui://` locus (net-new — none today);
  2. it is SET when the operator indicates — i.e. when a turn's `focus.selected` carries a
     `ui://` address (I1's widened vocabulary), the most-recent indicated `ui://` is remembered;
  3. the RHM can READ it via a getter (`current_locus()`), exposed so it FEEDS R2's resolution
     later (R2 is NOT built here — the locus is held + settable + readable, not yet consumed).

PERSISTENCE DECISION (deliberate, per the guide): IN-MEMORY attribute on the long-lived Suite
instance (`self._current_locus`), NOT store-backed. Justification — single live operator; R2
reads it LIVE off the same Suite in the same process; the FE re-ships `focus` every request so
the locus re-establishes instantly after any restart (restart-survival buys nothing); store-
backing would be a schema/contract addition with no consumer. So in-memory is the minimal correct
R1.

SET-POINT (reuse, never duplicate): the locus is set INSIDE `_chat_context`, at I1's exact
`startswith("ui://")` extraction (the spec's named set-point, old suite.py:855). This reuses I1's
vocabulary + I1's `_describe_ui_address` S0 grammar gate (a malformed `ui://` RAISES before we
ever store — we never remember an unvalidated locus, fail-loud consistent with I1), and lets us
prove R1 WITHOUT a live completion model (`_chat_context` is deterministic; `chat()` hits fabric).

CLOBBER SEMANTICS (chosen + asserted): a turn carrying a NEW `ui://` focus UPDATES the locus
(last-wins). A turn carrying ONLY a canvas node-id (no `ui://`) DOES NOT clobber the remembered
`ui://` locus — because `indicated` is empty, the write is guarded by `if indicated:` and is
skipped, leaving the prior locus intact. On a MULTI-`ui://` select, last-wins (`indicated[-1]`).

This test drives `_chat_context(...)` directly (the same no-model seam I1's
focus_ui_address_acceptance.py uses), since that IS the set-point.
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


# REAL registered element addresses (corpus addresses.json → S1 UI_REGISTRY rows). Two distinct
# registered controls so we can prove the locus UPDATES from one to the other.
ADDR_A = "ui://toolbar/run"
ADDR_B = "ui://chrome/inbox"
# A well-formed but UNREGISTERED ui:// address (conforms to grammar, no registry row) — proves the
# locus is set even when the description is "(unregistered)" (the address is still a valid locus).
ADDR_UNREG = "ui://toolbar/nonexistent-element-xyz"

store_dir = tempfile.mkdtemp(prefix="locus-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)
    g = "locus"
    suite.create_node(g, "constant", config={"value": "hello"}, node_id="c")
    suite.create_node(g, "uppercase", node_id="u")
    suite.connect(g, "c", "value", "u", "text")

    # precondition: the two locus addresses are genuinely in the live registry (registry-is-truth;
    # never a fabricated handle).
    handles = {row[0] for row in suite.UI_REGISTRY} | {
        ("ui://canvas/*" if row[1] == "canvas" else f"ui://{row[1]}/{row[0]}") for row in suite.UI_REGISTRY}
    check("precondition: ADDR_A is genuinely registered", ADDR_A in handles)
    check("precondition: ADDR_B is genuinely registered", ADDR_B in handles)

    # --- the getter exists and starts EMPTY (no locus until the operator indicates) ---
    check("getter current_locus() exists", hasattr(suite, "current_locus") and callable(suite.current_locus))
    check("locus is None before any indicate", suite.current_locus() is None)

    # --- (1) a chat turn whose focus.selected carries a ui:// address SETS the backend locus ---
    suite._chat_context(g, focus={"selected": [ADDR_A]})
    check("(1) after a ui:// focus turn, the getter returns that address", suite.current_locus() == ADDR_A)

    # --- (2a) a SUBSEQUENT turn with a NEW ui:// focus UPDATES the locus (last-wins) ---
    suite._chat_context(g, focus={"selected": [ADDR_B]})
    check("(2a) a new ui:// focus updates the locus", suite.current_locus() == ADDR_B)

    # --- (2b) a turn with ONLY a canvas node-id (no ui://) does NOT clobber the remembered ui:// locus ---
    suite._chat_context(g, focus={"selected": ["u"]})
    check("(2b) a node-id-only focus does NOT clobber the ui:// locus (remains ADDR_B)",
          suite.current_locus() == ADDR_B)

    # --- (2c) a turn with NO focus also does NOT clobber the locus ---
    suite._chat_context(g, focus=None)
    check("(2c) a no-focus turn does NOT clobber the locus (remains ADDR_B)",
          suite.current_locus() == ADDR_B)

    # --- multi-ui:// select → last-wins (indicated[-1]) ---
    suite._chat_context(g, focus={"selected": [ADDR_A, ADDR_B]})
    check("multi ui:// select → last-wins (locus is ADDR_B)", suite.current_locus() == ADDR_B)
    suite._chat_context(g, focus={"selected": [ADDR_B, ADDR_A]})
    check("multi ui:// select → last-wins (locus is ADDR_A)", suite.current_locus() == ADDR_A)

    # --- a MIXED focus (node-id + ui://) still sets the ui:// as locus (the node-id is co-presence only) ---
    suite._chat_context(g, focus={"selected": ["u", ADDR_B]})
    check("mixed focus (node-id + ui://) sets the ui:// as the locus", suite.current_locus() == ADDR_B)

    # --- an UNREGISTERED-but-well-formed ui:// is still a valid locus (it is the operator's locus
    #     even if undescribable); a MALFORMED ui:// would RAISE in I1's S0 grammar gate before we
    #     ever store, so the locus is never an unvalidated string. ---
    suite._chat_context(g, focus={"selected": [ADDR_UNREG]})
    check("an unregistered (well-formed) ui:// is still set as the locus", suite.current_locus() == ADDR_UNREG)

    # --- PRESERVE: the per-request co-presence path still works (a node-id focus still injects the
    #     co-presence block) — R1 PERSISTS a locus ALONGSIDE the per-request path, never replacing it. ---
    ctx_n = suite._chat_context(g, focus={"selected": ["u"]})
    check("PRESERVE: a node-id focus STILL injects the co-presence block",
          "OPERATOR'S CURRENT FOCUS" in ctx_n)
    check("PRESERVE: the focused node's id + type appear in the co-presence block",
          "u" in ctx_n and "uppercase" in ctx_n)
    ctx_a = suite._chat_context(g, focus={"selected": [ADDR_A]})
    check("PRESERVE: a ui:// focus STILL injects the INDICATING block (per-request path intact)",
          "INDICATING" in ctx_a.upper() and ADDR_A in ctx_a)

    print(f"\nALL {PASS} CHECKS PASS — backend holds + sets + reads a current ui:// locus, "
          f"node-id/no-focus turns don't clobber it, and the per-request focus path is preserved.")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
