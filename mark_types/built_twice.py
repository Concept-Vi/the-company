"""mark_types/built_twice.py — drift mark-type: built_twice (COMPOSITION ② drift-radar).

The disposition ② drift-radar writes when judge_drift confirms a near-cluster is GENUINELY duplicated —
the SAME logic/vocabulary implemented in 2+ places (a unification target one source should hold). The
value carries {with, shared, source} (the other place(s), what's shared, which should be the single source);
direction `surface` (it SURFACES a unification target for review — render-not-judge, the operator/lead
decides the one-source). The floor: ② JUDGES + marks, it never auto-fixes. See runtime/mark_types.py +
mark_types/AGENTS.md. Its `id` MUST equal the file stem (`built_twice`).
"""

MARK_TYPE = {
    "id": "built_twice",
    "value_shape": "claim",
    "direction": "surface",
    "desc": "the same logic/vocabulary built in 2+ places — a unification target surfaced for review (② drift-radar)",
}
