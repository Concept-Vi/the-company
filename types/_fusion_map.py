"""types/_fusion_map.py — the DISPOSITION RECORD for the 7 hollow cloud types (④ L3 · C3.4).

`_`-prefixed → NOT discovered as a TYPE (the FUSE 3 are NEVER silently imported as type files — rule 8: ask,
don't fabricate). This module RECORDS, traceable to evidence, what happened to each hollow type. Served
through Suite.type_info() so the disposition is surfaced to Tim, never buried. Source of the verdicts:
build-prep/the-one-system/organ-studies/HOLLOW-TYPES.md (dead-stuff-carries-intention applied).

  RECONSTRUCT 4 → types/{task,milestone,observation,blocker}.py (de-facto schemas + declared lifecycles).
  FUSE 3        → recorded below (mapping to where the concept ALREADY lives — NOT re-imported hollow).
  GHOST +2      → types/{research,diagnostic}.py (registered, routing harvested — hand-made-powers-generator).
"""

# The FUSE dispositions — each maps to where the concept was ALREADY real (zero-post = redundant-at-birth).
FUSIONS = {
    "decision": {
        "disposition": "FUSE",
        "into": "the engine DECISION organ",
        "targets": ["decisions/", "mark_types/decision_take.py", "mark_types/decision_update.py",
                    "mark_types/decision_update_accept.py", "mark_types/decision_retract.py",
                    "decision_subtypes/"],
        "state_mapping": {"proposed": "decision_take", "decided": "decision_update/accept", "reversed": "decision_retract"},
        "evidence": "0 board posts — the real concept lived in intents/approvals/design_decisions, not here. "
                    "The declared proposed/decided/reversed triple maps 1:1 onto the existing decision marks.",
        "source": "HOLLOW-TYPES.md",
    },
    "design_proposal": {
        "disposition": "FUSE",
        "into": "the `proposal` type (as a subtype/tag)",
        "targets": ["types/proposal.py", "verdict_panels/", "design/"],
        "state_mapping": {"draft": "draft", "review": "review", "approved": "approved", "rejected": "rejected"},
        "evidence": "0 posts (early probe). The non-hollow `proposal` type declares the IDENTICAL four states "
                    "(draft/review/approved/rejected); a second bespoke type would duplicate it.",
        "source": "HOLLOW-TYPES.md",
    },
    "project_space": {
        "disposition": "FUSE",
        "into": "the ④ CONTAINER itself (container.projects + law-11 state)",
        "targets": ["migrations/0013_container.sql", "container.projects"],
        "state_mapping": {"active": "container.projects state", "paused": "container.projects state",
                          "archived": "container.projects state"},
        "evidence": "0 posts. The reflexive move — the container as an item of the type system it contains — "
                    "is FULFILLED by ④ itself (the whole campaign IS this type). Fold active/paused/archived "
                    "into container.projects state (law 11).",
        "source": "HOLLOW-TYPES.md",
    },
}

# The overlap check HOLLOW-TYPES.md flagged for observation, RESOLVED (recorded, not left wobbly).
OBSERVATION_VERDICT = {
    "verdict": "RECONSTRUCT",
    "checked": ["item_types/note.py", "item_types/signal.py"],
    "finding": "note.py is the EVERGREEN ANNOTATION (states posted/archived) — it covers the annotation "
               "surface but NOT observation's new→validated VALIDATION GATE. signal.py is an ACT-SIGNAL "
               "(raised/consumed/superseded) — a different concept entirely. NEITHER models raw-noticing-"
               "kept-separate-from-accepted-knowledge.",
    "discriminator": "61 observation posts (heaviest hollow type) vs 0 for every FUSE type — categorically "
                     "the RECONSTRUCT side (the FUSE set were redundant-at-birth). Observation is the "
                     "validation-lifecycle type; note stays the evergreen annotation. They differ by "
                     "LIFECYCLE (law 11), not by fields.",
    "recorded_overlap": "observation and note both concern 'noticing'; kept distinct by lifecycle.",
    "source": "HOLLOW-TYPES.md",
}

# The full per-type disposition ledger (all 7 hollow + 2 ghost), for type_info() surfacing.
HOLLOW_DISPOSITIONS = {
    "task": {"disposition": "RECONSTRUCT", "posts": 31, "file": "types/task.py"},
    "milestone": {"disposition": "RECONSTRUCT", "posts": 58, "file": "types/milestone.py"},
    "observation": {"disposition": "RECONSTRUCT", "posts": 61, "file": "types/observation.py",
                    "note": "note.py/signal.py overlap checked → RECONSTRUCT (see OBSERVATION_VERDICT)"},
    "blocker": {"disposition": "RECONSTRUCT", "posts": 7, "file": "types/blocker.py"},
    "decision": {"disposition": "FUSE", "posts": 0, "into": FUSIONS["decision"]["into"]},
    "design_proposal": {"disposition": "FUSE", "posts": 0, "into": FUSIONS["design_proposal"]["into"]},
    "project_space": {"disposition": "FUSE", "posts": 0, "into": FUSIONS["project_space"]["into"]},
    "research": {"disposition": "GHOST-REGISTERED", "posts": 2, "file": "types/research.py"},
    "diagnostic": {"disposition": "GHOST-REGISTERED", "posts": 1, "file": "types/diagnostic.py"},
}
