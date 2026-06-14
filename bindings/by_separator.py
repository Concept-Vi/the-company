"""The TWO-GRAVITY SEPARATOR lens (Group 9) — a GENERAL variable-two-pole resolution.

radius_from='separator' makes each item's radius its signed LEAN between two poles (pull toward A vs
pull toward B); angle_from still divides the wheel (here by kind), so the separator composes with any
angular division — it changes only the radius. The two poles are VARIABLES, registry-true: declared in
THIS ROW and overridable per request (?pole_a=&pole_b=) so the operator drives which two gravities. The
poles below are two clustering-separated regions of the `topics` lens (real, distinct corpus regions —
NOT a hardcoded oracle); the separation_report in the response is the honest witness that they separate
(if a pyramid rebuild shifts the clusters, `separates` tells the truth rather than silently lying).

Pollution (origin vs the AI-corner) is ONE named instance of this general mechanism, not its purpose —
it sets pole_b to a planted anchor:// vector. That instance is the named deferred application; this lens
is the general two-gravity field."""

BINDING = {
    "id": "by_separator",
    "label": "Two gravities — lean between two poles",
    "angle_from": "kind",            # the angular division composes freely; the separator owns only radius
    "radius_from": "separator",
    "order_by": "count",
    "space": "topics",               # the lens the items + poles live in (cosines are within ONE space)
    # default poles: the TWO MOST-DISTINCT clustering-separated regions of the topics lens (measured
    # 1-cos≈0.19, the widest of the 28 centroid pairs), overridable per request. The discriminator confirms
    # they separate with OPPOSED ordering (Spearman≈−0.18) and clean leaders (worldview/conceptual ← what.py,
    # worldview.py, principles.py | runtime/sessions ← introspection.py, sessions.py, server.py).
    "pole_a": "cluster://topics/k8/6",
    "pole_a_label": "worldview / conceptual region",
    "pole_b": "cluster://topics/k8/4",
    "pole_b_label": "sessions / runtime region",
}
