"""tests/focus_ui_address_acceptance.py — I1 · click-to-indicate (the `focus` vocabulary widening).

WHAT I1 IS (seams-rhm.md Seam 4): today the `focus` param is FE-ephemeral, per-request, and
**canvas-node-only** — `_chat_context` keeps only ids that are canvas graph nodes (`s in by`).
There is NO backend locus and `focus` does not accept `ui://` addresses. I1 WIDENS the EXISTING
`focus` plug-in point so a clicked addressed element ships its `ui://` address as the locus, and
the RHM reply reflects the indicated thing — WITHOUT replacing the canvas-node co-presence path.

This test proves the widening at the `_chat_context` seam (no model call — `_chat_context` builds
the grounding string deterministically, unlike `chat()` which hits the fabric). Three cases:

  (a) a REGISTERED ui:// address in focus.selected → the indicated element's human description is
      injected into the context (resolved via the S1 UI registry / UI_REGISTRY).
  (b) an UNREGISTERED ui:// address in focus.selected → injected AS the address with an
      "(unregistered)" marker (HARD CONSTRAINT: fail-loud, never silently dropped — AGENTS.md rule 4).
  (c) a canvas NODE-ID in focus.selected → the "OPERATOR'S CURRENT FOCUS (co-presence)" block STILL
      injects exactly as before (the PRESERVE check — the node-id path is widened additively, not
      replaced).

The focus object is constructed as the EXACT structure the FE ships (`api.chat(m, {selected})` →
`{selected: [...]}`), so this is the only proof of the FE→backend wire (the browser FORM proof is
the loop's; no services are up here).
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


# A REAL registered element address (corpus addresses.json → S1 UI_REGISTRY row). ui://toolbar/run
# is the RUN control — present in the live registry, so it resolves to a human title.
REGISTERED_ADDR = "ui://toolbar/run"
# A well-formed but UNREGISTERED address (conforms to the ui:// grammar, no registry row).
UNREGISTERED_ADDR = "ui://toolbar/nonexistent-element-xyz"

store_dir = tempfile.mkdtemp(prefix="focus-ui-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)
    g = "focus-ui"
    suite.create_node(g, "constant", config={"value": "hello"}, node_id="c")
    suite.create_node(g, "uppercase", node_id="u")
    suite.connect(g, "c", "value", "u", "text")

    # sanity: REGISTERED_ADDR really IS in the live registry (registry-is-truth; this test is only
    # meaningful if the address it asserts on is genuinely registered — never a fabricated handle).
    handles = {row[0] for row in suite.UI_REGISTRY} | {
        ("ui://canvas/*" if row[1] == "canvas" else f"ui://{row[1]}/{row[0]}") for row in suite.UI_REGISTRY}
    check("REGISTERED_ADDR is genuinely in the live UI registry (precondition)",
          REGISTERED_ADDR in handles)

    # the resolved description the registry produces for REGISTERED_ADDR (the SAME resolver the
    # context uses) — proven below to actually land in the context (the FE→backend wire's payload).
    resolved_desc = suite._describe_ui_address(REGISTERED_ADDR)
    check("REGISTERED_ADDR resolves to a description RICHER than the bare address (registry-sourced)",
          resolved_desc != REGISTERED_ADDR and "unregistered" not in resolved_desc.lower())

    # --- (a) a REGISTERED ui:// address is RESOLVED + injected as the indicated element ---
    ctx = suite._chat_context(g, focus={"selected": [REGISTERED_ADDR]})
    check("(a) the indicated ui:// address string appears in the context",
          REGISTERED_ADDR in ctx)
    check("(a) the indicated element's RESOLVED registry description is injected into the context",
          resolved_desc in ctx)
    check("(a) an INDICATING block is present (distinct from co-presence)",
          "INDICATING" in ctx.upper())

    # --- (b) an UNREGISTERED ui:// address is injected AS the address + marked unregistered (FAIL LOUD) ---
    ctx_u = suite._chat_context(g, focus={"selected": [UNREGISTERED_ADDR]})
    check("(b) the unregistered address is NOT silently dropped — it appears in the context",
          UNREGISTERED_ADDR in ctx_u)
    check("(b) the unregistered address is MARKED '(unregistered)' (fail-loud, rule 4)",
          "unregistered" in ctx_u.lower())

    # --- (c) the PRESERVE check: a canvas NODE-ID still injects the co-presence block UNCHANGED ---
    ctx_n = suite._chat_context(g, focus={"selected": ["u"]})
    check("(c) PRESERVE: a node-id focus STILL injects the co-presence block",
          "OPERATOR'S CURRENT FOCUS" in ctx_n)
    check("(c) PRESERVE: the focused node's id + type appear in the co-presence block",
          "u" in ctx_n and "uppercase" in ctx_n)

    # --- belt-and-suspenders: a MIXED focus (a node-id AND a ui:// address) injects BOTH blocks ---
    ctx_m = suite._chat_context(g, focus={"selected": ["u", REGISTERED_ADDR]})
    check("MIXED: co-presence block present for the node-id",
          "OPERATOR'S CURRENT FOCUS" in ctx_m)
    check("MIXED: indicating block present for the ui:// address",
          "INDICATING" in ctx_m.upper() and REGISTERED_ADDR in ctx_m)

    # --- no-regression: NO focus → neither block (the original empty-focus behaviour) ---
    ctx0 = suite._chat_context(g, focus=None)
    check("no focus → no co-presence block", "OPERATOR'S CURRENT FOCUS" not in ctx0)
    check("no focus → no indicating block", "INDICATING" not in ctx0.upper())

    print(f"\nALL {PASS} CHECKS PASS — focus accepts ui:// addresses (resolved + fail-loud) "
          f"AND the canvas-node co-presence path is preserved.")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
