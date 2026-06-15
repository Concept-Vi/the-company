"""pair — a composition-mind: [extractor → judge], the N+1 first unit.
The brain for a turn = this COMPOSITION (not one slot). order-edge extractor→judge (kind=feeds): the
judge consumes the extractor's run:// output. Recompose = edit this row's members/order (ZERO code)."""
MIND = {
    "id": "pair",
    "kind": "composition",
    "members": ["extractor", "judge"],
    "order": [{"from": "extractor", "to": "judge", "kind": "feeds"}],
    "desc": "extractor→judge composition (N+1): the judge feeds on the extractor's output. The first composable mind.",
}
