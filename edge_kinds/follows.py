"""edge_kinds/follows.py — edge kind 'follows' · face=lineage.

The path-step threading relation: step N follows step N-1 in an ordered walk (ledger.path_step). The
default `via_kind` for a derived path step (ordinal > 0). Inverse 'preceded_by' is COMPOSED AT READ."""
EDGE_KIND = {
    "id": "follows",
    "directed": True,
    "inverse": "preceded_by",
    "face": "lineage",
    "label": "follows",
    "description": "the source step follows the target step in an ordered path walk (ledger.path_step)",
}
