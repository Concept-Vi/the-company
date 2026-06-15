"""pair — a composition-mind: [extractor → judge], the N+1 first unit.
The brain for a turn = this COMPOSITION (not one slot). The feeds order-edge is EXECUTED by
run_composition (walk the edge): the judge's input is built FROM the extractor's output (`as: "extract"`)
+ the original source (`source_as: "raw_exchange"`) — so the judge consumes the real extract, not the raw
utterance (the flat-fan bug). Recompose = edit this row's members/order/as/source_as (ZERO code)."""
MIND = {
    "id": "pair",
    "kind": "composition",
    "members": ["extractor", "judge"],
    "order": [{"from": "extractor", "to": "judge", "kind": "feeds", "as": "extract"}],
    "source_as": "raw_exchange",
    "desc": "extractor→judge composition (N+1): judge feeds on the extractor's output (as=extract) + source (raw_exchange).",
}
