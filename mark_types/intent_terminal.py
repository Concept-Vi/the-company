"""mark_types/intent_terminal.py — CIRCUIT mark-type: intent_terminal (the walk ENDED — wins over everything).

④ L5-CIRCUIT (organ-studies/CIRCUIT.md §4): the mark that ENDS an intent's lifecycle. Record fields (open
record, beside target/ts):
  • `outcome` — succeeded | failed | cancelled (the closed vocabulary; anything else FAILS LOUD at write —
                runtime/circuit.terminate).
  • `result`  — optional; the outcome payload (result/error detail).
`value` = the outcome label (value_shape `label`). compose_state: a terminal WINS over every other mark and
over the clock — terminal-after-lapse is terminal, terminal-beside-a-live-lease is terminal. A second
terminal on the same target is a grammar violation (fail-loud): ends end once. ABORT = a `cancelled`
terminal (cc_gate's abort, one vocabulary). direction `surface`. id MUST equal the file stem
(`intent_terminal`).
"""

MARK_TYPE = {
    "id": "intent_terminal",
    "value_shape": "label",
    "direction": "surface",
    "desc": "the intent's walk ended — value/outcome = succeeded|failed|cancelled (closed vocab, "
            "fail-loud), result = the outcome payload; wins over every other mark and over the clock; "
            "a second terminal refuses (ends end once)",
}
