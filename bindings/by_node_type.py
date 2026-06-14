# THE CONNECTIONS IN THE REGISTRIES (Group 10) — the node registry rendered as its directional typed edges.
# sectors = every node type (whole_set: the registry's STRUCTURE, not only the rows present in event data);
# the directional TYPE-FLOW edges (A's output type feeds B's input type, asymmetric — Tim: "the only edges
# that get typed are the directional ones") are surfaced as directed chords; cycles among them render AS
# cycles (nonsequential is valid). order_by='edge' arranges the wheel by those edges where they sequence.
# Registry-is-truth: drop a node type into nodes/ and it appears as a sector + its edges, no code edit here.
# radius_from='time' is a placeholder axis (the connections view is about the EDGES, not the radius) — the
# centre/radius stay variable like every binding.
BINDING = {
    "id": "by_node_type",
    "label": "Connections — the node registry by its directional type-flow",
    "angle_from": "node-types",
    "radius_from": "time",
    "order_by": "edge",
    "whole_set": True,
}
