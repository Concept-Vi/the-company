"""checks/dossier_refcheck.py — the registry-dossier no-fiction floor as a declared check (G3·S3a).
Wraps the PROVEN design/_system/refcheck.check_dossier (reuse-don't-parallel — the one implementation;
this row makes it cascade-referenceable by name)."""
import sys

CHECK = {
    "id": "dossier_refcheck",
    "label": "Registry-dossier no-fiction floor",
    "description": ("Deterministically verifies a proposed registry dossier's closed-world claims: "
                    "capabilities ⊆ the canonical vocabulary, maps_to_feature ∈ the real inventory (or "
                    "'proposed'), code refs resolve. The gate that caught every invented feature id."),
}


def check(value, **params):
    sys.path.insert(0, "/home/tim/company/design/_system")
    import refcheck
    out = refcheck.check_dossier(value, **params)
    return {"passed": bool(out.get("passed")), "reasons": list(out.get("reasons", []))}
