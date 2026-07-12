"""mcp_face/remote_safe_manifest.py — the DECLARED public safe-tier manifest (FL1, B4's second front).

THE LAW THIS ENCODES (lead-approved with the declared-manifest condition, board://item-c15c9ffe):
the set of tools visible to the PUBLIC authenticated non-operator tier (remote.py :8772, posture=="safe")
is a DELIBERATE DECLARATION, not an emergent side-effect of whoever last tagged a tool. The acceptance
test (tests/remote_safe_subset_acceptance.py) enumerates the LIVE registry — the same registry
remote._tools_for_tier reads — and fails loud on ANY divergence, in BOTH directions:
  • a tool tagged safe but absent here  = an ACCIDENTAL PUBLIC EXPOSURE (the exact silent-boundary-
    rewrite hazard the 6-lens review flagged: a rename/merge/new door widening the public surface
    with nobody deciding it);
  • a tool listed here but not tagged   = an ACCIDENTAL REMOVAL of client visibility (or manifest rot).
Either way the fix is a DELIBERATE act: change the tool's posture AND this manifest in one reviewed
commit. Editing this file IS the decision record.

SEEDED 2026-07-13 from the live registry (behavior-preserving — this declares what IS, it does not
re-decide it). Entries flagged for an explicit lead/Tim review on the B4 thread: `operator` (exposes
the system's working-with-Tim rules to the client tier) and `corpus` (repo-derived content) — both are
read-only and currently tagged safe; whether they SHOULD be client-visible is a policy call, recorded
there, not silently changed here.
"""

# Every tool the PUBLIC client tier may see. Sorted; one per line so diffs read as decisions.
REMOTE_SAFE_MANIFEST = frozenset({
    "capabilities",
    "capability",
    "channels",
    "cognition_info",
    "cognition_inputs",
    "corpus",
    "directory",
    "field_types",
    "list_by_type",
    "list_cascades",
    "list_graphs",
    "list_skills_contexts",
    "mailbox",
    "marks",
    "models_for_role",
    "object_info",
    "operator",
    "principal",
    "reduce_rule_names",
    "sessions",
    "type_info",
})
