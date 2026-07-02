"""cascades/queue_routing.py — A's queue_routing cascade (priority 90), target=pgmq.

CLOUD-ONLY: the target system (pgmq) lives on the cloud/read side, NOT in ④'s scope. Declared here so the
fan-out is HONEST about the hole (generate_all returns skipped:reason) rather than silently omitting it —
the run-all-report-holes loop A never had. Regenerated on the cloud side; ④ derives only the in-scope faces.
No live handler (never invoked — generate_all short-circuits on cloud_only)."""

CASCADE = {
    "id": "queue_routing",
    "target": "pgmq",
    "priority": 90,
    "cloud_only": True,
    "desc": "per-type queue routing (cloud pgmq)",
}


def handle(type_row: dict, ctx: dict) -> dict:  # never called (cloud_only short-circuits) — fail loud if it is
    raise NotImplementedError("queue_routing is cloud_only — its target pgmq is not present in ④; nothing to derive here.")
