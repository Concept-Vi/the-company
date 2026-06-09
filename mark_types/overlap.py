"""mark_types/overlap.py — drift mark-type: overlap (COMPOSITION ② drift-radar).

The disposition ② drift-radar writes when judge_drift finds significant SHARED RESPONSIBILITY between
near units — softer than `built_twice` (not the same logic duplicated, but overlapping concern that COULD
be unified). The value carries {with, shared, source}; direction `surface` (a unification candidate for
review, render-not-judge). The floor: ② judges + marks, never auto-fixes. See runtime/mark_types.py +
mark_types/AGENTS.md. Its `id` MUST equal the file stem (`overlap`).
"""

MARK_TYPE = {
    "id": "overlap",
    "value_shape": "claim",
    "direction": "surface",
    "desc": "significant shared responsibility between near units — a softer unification candidate (② drift-radar)",
}
