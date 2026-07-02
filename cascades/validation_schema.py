"""cascades/validation_schema.py — A's validation_schema cascade (priority 80), target=component_registry.

CLOUD-ONLY: the target system (component_registry) lives on the cloud/read side, NOT in ④'s scope. Declared here so the
fan-out is HONEST about the hole (generate_all returns skipped:reason) rather than silently omitting it —
the run-all-report-holes loop A never had. Regenerated on the cloud side; ④ derives only the in-scope faces.
No live handler (never invoked — generate_all short-circuits on cloud_only)."""

CASCADE = {
    "id": "validation_schema",
    "target": "component_registry",
    "priority": 80,
    "cloud_only": True,
    "desc": "the type's data_schema wired into the cloud component validator",
}


def handle(type_row: dict, ctx: dict) -> dict:  # never called (cloud_only short-circuits) — fail loud if it is
    raise NotImplementedError("validation_schema is cloud_only — its target component_registry is not present in ④; nothing to derive here.")
