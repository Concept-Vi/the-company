"""checks/prose_clean.py — the operator-prose leakage floor as a declared check (G3·S3a).
Wraps design/_system/prose_check.check_prose (the deterministic voice judgment — moved off the model
after two failed prompt calibrations; this row makes it cascade-referenceable)."""
import sys

CHECK = {
    "id": "prose_clean",
    "label": "Operator-prose leakage floor",
    "description": ("Deterministically checks a dossier's two operator-facing prose fields for code "
                    "leakage (file paths, markup, selectors, address schemes, feature-id shapes, code "
                    "identifiers). Domain vocabulary is never flagged — structural code shapes only."),
}


def check(value, **params):
    sys.path.insert(0, "/home/tim/company/design/_system")
    from prose_check import check_prose
    out = check_prose(value)
    return {"passed": bool(out.get("passed")),
            "reasons": [f"{h['kind']}: {h['match']}" for h in out.get("hits", [])]}
