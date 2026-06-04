"""tests/rhm_action_parse_acceptance.py — model-/provider-AGNOSTIC RHM action parsing.

The requirement (Tim): the RHM must ACTUALLY ACT regardless of which model/provider is
selected, and a NEW model must "just work". Real models DON'T emit the canonical
`ACTION: verb args` line — each provider emits its OWN native tool-call shape (Anthropic/XML
`<invoke>`, JSON `{"name":...}`, minimax's `]<]minimax[>[` delimiter, a fenced ```json block).
`_parse_rhm_action` must recognise the intended verb+args in ANY of these shapes and normalise
them to the SAME dispatcher dict — so the same intent expressed in any shape extracts the same
action. And the wrapper tokens must NEVER leak into the shown reply.

THE INVARIANT THAT MUST HOLD ACROSS THE CHANGE (E6, AGENTS.md rule 9): the parser is
shape-recognition ONLY — it does NOT whitelist. The DISPATCHER holds the one whitelist
(RHM_VERBS). So a forbidden verb (delete) extracted by the parser is REFUSED end-to-end by the
dispatcher (did == "none") — proven here parse→dispatch, not just "the parser dropped it".
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


# wrapper tokens that must NEVER reach the operator's shown text
LEAK_TOKENS = ("<invoke", "</invoke>", "<tool_call", "</tool_call>", "]<]", "[>[", "```json", "ACTION:")

store_dir = tempfile.mkdtemp(prefix="rhm-parse-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    # ---------------------------------------------------------------------------------------
    # (a) the canonical ACTION: line (clean prose then the action) — the existing shape, kept.
    # The build pipeline JSON is the SAME for all four "build" shapes below — assert identical.
    # ---------------------------------------------------------------------------------------
    BUILD_JSON = '[{"as":"a","type":"constant","config":{"value":"x"}},{"as":"u","type":"uppercase"},{"wire":"a.value -> u.text"}]'
    shown_a, act_a = suite._parse_rhm_action(f"Sure — I'll wire that up now.\nACTION: build {BUILD_JSON}")
    check("(a) canonical ACTION: build parses",
          act_a and act_a["verb"] == "build" and isinstance(act_a["steps"], list) and len(act_a["steps"]) == 3)
    check("(a) shown reply has the prose, no ACTION token", "wire that up" in shown_a and "ACTION:" not in shown_a)

    # ---------------------------------------------------------------------------------------
    # (b) minimax native: the `]<]minimax[>[` delimiter + a <tool_call><invoke> wrapper.
    #     This is the LITERAL shape observed leaking raw into a live chat.
    # ---------------------------------------------------------------------------------------
    minimax = (f"Here's the pipeline.]<]minimax[>[<tool_call><invoke name=\"build\">{BUILD_JSON}</invoke></tool_call>")
    shown_b, act_b = suite._parse_rhm_action(minimax)
    check("(b) minimax wrapper → build extracted", act_b and act_b["verb"] == "build" and len(act_b["steps"]) == 3)
    check("(b) build steps IDENTICAL to the canonical shape", act_b["steps"] == act_a["steps"])
    check("(b) NO wrapper token leaks into the shown reply",
          not any(tok in shown_b for tok in LEAK_TOKENS))

    # ---------------------------------------------------------------------------------------
    # (c) Anthropic/XML <invoke name="consult"> — args are the query text inside the tag.
    # ---------------------------------------------------------------------------------------
    shown_c, act_c = suite._parse_rhm_action('Let me check the source.\n<invoke name="consult">how does the memo gate work</invoke>')
    check("(c) <invoke name=consult> → consult extracted",
          act_c and act_c["verb"] == "consult" and "memo gate" in act_c["query"])
    check("(c) no wrapper token leaks", not any(tok in shown_c for tok in LEAK_TOKENS))

    # ---------------------------------------------------------------------------------------
    # (d) a fenced ```json {"verb":"show","targets":[...]} action block.
    # ---------------------------------------------------------------------------------------
    fenced = 'I will take you there.\n```json\n{"verb":"show","targets":["answer"]}\n```'
    shown_d, act_d = suite._parse_rhm_action(fenced)
    check("(d) fenced json action → show extracted",
          act_d and act_d["verb"] == "show" and act_d["targets"] == ["answer"])
    check("(d) no fence token leaks into the shown reply", not any(tok in shown_d for tok in LEAK_TOKENS))

    # also a JSON tool-call shape {"name":"consult","arguments":{"query":...}} — provider-agnostic
    shown_e2, act_e2 = suite._parse_rhm_action('Checking.\n{"name":"consult","arguments":{"query":"what are the contracts"}}')
    check("JSON {name,arguments} tool-call → consult extracted",
          act_e2 and act_e2["verb"] == "consult" and "contracts" in act_e2["query"])

    # ---------------------------------------------------------------------------------------
    # (e) NO action: a plain grounded answer → action is None (don't over-trigger).
    #     Includes prose that MENTIONS "ACTION:" mid-sentence (the RHM explains its own mechanism)
    #     — that must NOT be mistaken for a real trailing action.
    # ---------------------------------------------------------------------------------------
    _, act_none = suite._parse_rhm_action("The graph has 2 nodes, both resolved. Nothing to do.")
    check("(e) plain answer → no action", act_none is None)
    _, act_mention = suite._parse_rhm_action(
        "To act, I append an ACTION: line such as ACTION: run — but you didn't ask me to do anything.")
    check("(e) 'ACTION:' described mid-prose (not a trailing directive) → no over-trigger", act_mention is None)
    # a benign standalone JSON object (e.g. the RHM SHOWING an example node config) must NOT be
    # mistaken for a tool-call and silently eaten from the shown reply (no-silent-loss).
    benign = 'Here is an example node config:\n{"name":"uppercase","type":"uppercase"}\nThat is all.'
    shown_benign, act_benign = suite._parse_rhm_action(benign)
    check("(e) benign {name,type} example config → NOT a tool-call (no over-trigger)", act_benign is None)
    check("(e) the benign JSON is NOT stripped from the shown reply (no silent content loss)",
          '"name":"uppercase"' in shown_benign)

    # ---------------------------------------------------------------------------------------
    # (f) THE WHITELIST HOLDS — a forbidden verb is extractable by the parser but REFUSED by the
    #     dispatcher. Proven END-TO-END (parse → dispatch → did == "none"), the no-bypass guarantee.
    # ---------------------------------------------------------------------------------------
    g = "parse-sec"
    suite.create_node(g, "constant", config={"value": "x"}, node_id="c")
    _, act_del = suite._parse_rhm_action('<invoke name="delete">c</invoke>')
    # the parser is allowed to extract it (shape-recognition only) — the DISPATCHER must refuse it.
    r_del = suite._dispatch_rhm_action(act_del, g)
    check("(f) forbidden 'delete' (any shape) is REFUSED end-to-end (whitelist in dispatcher, did==none)",
          r_del["did"] == "none")
    check("(f) the node was NOT deleted", any(n.id == "c" for n in suite._load(g).nodes))

    # and the allowed verbs still dispatch from these shapes — the WHOLE point: it acts.
    suite.create_node(g, "uppercase", node_id="u"); suite.connect(g, "c", "value", "u", "text")
    r_run = suite._dispatch_rhm_action(suite._parse_rhm_action('<invoke name="run"></invoke>')[1], g)
    check("an allowed verb (run) from a native wrapper DISPATCHES (it actually acts)", r_run["did"] == "run")

    print(f"\nALL {PASS} CHECKS PASS — RHM parses verbs from ANY model/provider shape; whitelist holds; no leak")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
