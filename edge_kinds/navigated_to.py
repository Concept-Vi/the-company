"""edge_kinds/navigated_to.py — edge kind 'navigated_to' · face=knowledge.

A user/agent NAVIGATION step: stood at one address, navigated to another (GRAPH-PATH §3.3 — navigation
paths land steps at ui:// with via_kind=navigated_to). Inverse 'navigated_from' is COMPOSED AT READ."""
EDGE_KIND = {
    "id": "navigated_to",
    "directed": True,
    "inverse": "navigated_from",
    "face": "knowledge",
    "label": "navigated-to",
    "description": "a navigation step moved from the source address to the target address",
}
