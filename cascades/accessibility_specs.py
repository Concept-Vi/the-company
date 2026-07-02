"""cascades/accessibility_specs.py — A's accessibility_specs cascade (priority 40), target=component_accessibility_specs.

CLOUD-ONLY: the target system (component_accessibility_specs) lives on the cloud/read side, NOT in ④'s scope. Declared here so the
fan-out is HONEST about the hole (generate_all returns skipped:reason) rather than silently omitting it —
the run-all-report-holes loop A never had. Regenerated on the cloud side; ④ derives only the in-scope faces.
No live handler (never invoked — generate_all short-circuits on cloud_only)."""

CASCADE = {
    "id": "accessibility_specs",
    "target": "component_accessibility_specs",
    "priority": 40,
    "cloud_only": True,
    "desc": "a11y specs for the type's card component (cloud)",
}


def handle(type_row: dict, ctx: dict) -> dict:  # never called (cloud_only short-circuits) — fail loud if it is
    raise NotImplementedError("accessibility_specs is cloud_only — its target component_accessibility_specs is not present in ④; nothing to derive here.")
