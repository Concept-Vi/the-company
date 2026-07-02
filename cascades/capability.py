"""cascades/capability.py — A's capability cascade (priority 60), target=capabilities.

CLOUD-ONLY: the target system (capabilities) lives on the cloud/read side, NOT in ④'s scope. Declared here so the
fan-out is HONEST about the hole (generate_all returns skipped:reason) rather than silently omitting it —
the run-all-report-holes loop A never had. Regenerated on the cloud side; ④ derives only the in-scope faces.
No live handler (never invoked — generate_all short-circuits on cloud_only)."""

CASCADE = {
    "id": "capability",
    "target": "capabilities",
    "priority": 60,
    "cloud_only": True,
    "desc": "the project.manage_<t>s capability row (cloud capabilities table)",
}


def handle(type_row: dict, ctx: dict) -> dict:  # never called (cloud_only short-circuits) — fail loud if it is
    raise NotImplementedError("capability is cloud_only — its target capabilities is not present in ④; nothing to derive here.")
