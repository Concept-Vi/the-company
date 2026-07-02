"""cascades/theme_specs.py — A's theme_specs cascade (priority 30), target=component_theme_specs.

CLOUD-ONLY: the target system (component_theme_specs) lives on the cloud/read side, NOT in ④'s scope. Declared here so the
fan-out is HONEST about the hole (generate_all returns skipped:reason) rather than silently omitting it —
the run-all-report-holes loop A never had. Regenerated on the cloud side; ④ derives only the in-scope faces.
No live handler (never invoked — generate_all short-circuits on cloud_only)."""

CASCADE = {
    "id": "theme_specs",
    "target": "component_theme_specs",
    "priority": 30,
    "cloud_only": True,
    "desc": "theme tokens for the type's card component (cloud component_registry)",
}


def handle(type_row: dict, ctx: dict) -> dict:  # never called (cloud_only short-circuits) — fail loud if it is
    raise NotImplementedError("theme_specs is cloud_only — its target component_theme_specs is not present in ④; nothing to derive here.")
