"""tests/rhm_grounding_acceptance.py — the RHM is grounded in the WHOLE interface.

Tim: the RHM must be aware of "everything it needs to be aware of in the whole interface" — all
from the LIVE registry/state, never fabricated. The old `_chat_context` carried the graph, nodes,
node-types, recent activity, and focus — but OMITTED the models (chat + embed), the modes, the RHM
verbs it can itself perform, the inbox count, the panels and the graphs. So the RHM correctly
refused to invent (good) but said "I can't see the models" — because they were genuinely absent.

This proves the enriched context CARRIES those live values (so the system prompt's "answer only
from this state" now lets it answer ABOUT them), while staying within the system-prompt budget.
The model endpoints are stubbed (headless: the fabric/embed endpoints may be down) so we assert
the REAL values the registry returns appear — not that a network call succeeds.
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


store_dir = tempfile.mkdtemp(prefix="rhm-ground-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    # stub the model reads so the test asserts the REAL registry values (not network availability).
    # available_models = chat; models_at("embed") = embed (its endpoint is normally down headless).
    suite._models_cache = ["minimax-m3:cloud", "deepseek-v4-pro:cloud"]   # chat (available_models reads this)
    suite.models_at = lambda kind="chat", base_url=None: (
        ["nomic-embed-text:latest", "BAAI/bge-m3"] if kind == "embed" else suite.available_models())

    g = "ground"
    suite.create_node(g, "constant", config={"value": "x"}, node_id="c")
    suite.create_node(g, "uppercase", node_id="u")

    # surface two inbox items so the inbox COUNT is non-trivial (the RHM must be able to answer
    # "what's awaiting"). surface_review lands a live escalation (resolved is None).
    suite.surface_review({"title": "first review item", "kind": "idea"}, origin="generative")
    suite.surface_review({"title": "second review item", "kind": "idea"}, origin="generative")

    ctx = suite._chat_context(g)

    # --- the WHOLE-interface grounding fields (the fix) ---
    check("context includes the CHAT models", "minimax-m3:cloud" in ctx and "deepseek-v4-pro:cloud" in ctx)
    check("context includes the EMBED models", "nomic-embed-text:latest" in ctx and "bge-m3" in ctx.lower())
    check("context includes the presence MODES", "listening" in ctx and "decide-for-me" in ctx)
    check("context includes the current mode", "current" in ctx.lower() and suite.get_mode() in ctx)
    check("context includes the RHM VERBS it can perform (its own capabilities)",
          all(v in ctx for v in ("run", "propose", "build", "consult", "show", "panel", "extend")))
    check("context includes a one-line gloss of what a verb does (not just the name)",
          "recompute" in ctx.lower() or "compose" in ctx.lower())
    check("context includes the INBOX count (so it can answer 'what's awaiting')",
          "2" in ctx and ("await" in ctx.lower() or "inbox" in ctx.lower() or "escalation" in ctx.lower()))
    check("context includes WHAT's awaiting (the item titles, not just the count)",
          "first review item" in ctx and "second review item" in ctx)
    check("context includes the GRAPHS (it's a multigraph)", g in ctx)

    # --- the existing guarantees still hold (regression) ---
    check("still names the graph + node-types", g in ctx and "uppercase" in ctx)
    check("still does NOT dump the codebase source", "AGENTS.md" not in ctx)

    # --- stays within the system-prompt budget (Tim 2026-06-22: "4000 is never enough context — 16k min
    # really — do not trim when there are other options"). The OLD 4000 forced trimming legitimate ground
    # truth; the budget is 16k (the brain runs on a big-context model — kimi 256K — for the rich context, not
    # starved to the resident 4B). Still GUARDS against the raw-dump bloat class (the 512-ui://-address dump
    # that hit ~19.6k is capped to the named chrome regions). ---
    check(f"stays within the system-prompt budget (len={len(ctx)} < 16000)", len(ctx) < 16000)

    # --- FAIL-LOUD-LEGIBLE degradation: if the embed endpoint is DOWN, context renders a legible
    #     marker (NOT a silent omission and NOT a crash — rule 4). Simulate by making models_at raise.
    def _raise(*a, **k):
        raise RuntimeError("embed endpoint unreachable")
    suite.models_at = _raise
    ctx2 = suite._chat_context(g)
    check("embed endpoint down → context still builds (no crash) with a legible degraded marker",
          "unreachable" in ctx2.lower() or "unavailable" in ctx2.lower())
    check("chat models still present even when embed is down", "minimax-m3:cloud" in ctx2)

    print(f"\nALL {PASS} CHECKS PASS — the RHM is grounded in the whole interface, from the live registry")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
