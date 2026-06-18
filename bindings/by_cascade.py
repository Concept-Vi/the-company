# THE CONNECTIONS IN THE REGISTRIES via CASCADE PRECEDENCE (Group 10 — "cascade precedes", a directional-edge
# source Tim named explicitly). sectors = the operator ROLES (+ op verbs) that the saved cascades reference;
# the DIRECTIONAL precedence edges (step i → step i+1 within each cascade — precedence has a direction, so it
# types; symmetric never does) are surfaced as directed chords. Cycles across cascades render AS cycles
# (nonsequential is valid — no forced acyclicity). order_by='edge' arranges the wheel by those edges where
# they sequence. Registry-is-truth: save a cascade (save_cascade) and its steps appear as sectors + precedence
# edges with NO code edit. radius_from='time' is a placeholder axis (this view is about the EDGES, not the
# radius) — centre/radius stay variable like every binding. Empty/edge-sparse honestly when few cascades exist.
BINDING = {
    "id": "by_cascade",
    "label": "Flow — the steps, in the order they run",
    # human meaning (registry-true, declared-first; TENTATIVE draft — Tim/DNA ratify; never machine names)
    "meta": {
        "name": "Flow",
        "is": "The Company's steps, connected in the order they run.",
        "fills": "Each slice is a step; the connections show which step runs before which — the chain of work.",
        "why": "To see the order things happen in — what leads to what.",
    },
    "angle_from": "cascade-flow",
    "radius_from": "time",
    "order_by": "edge",
    "whole_set": True,
}

# HUMAN MEANING for the SECTORS of this lens — the STEPS (the system's roles + op-verbs that saved flows
# reference). Same legibility-type as kinds/raw.py + nodes/_meta.py + bindings/grouped.py + bindings/by_lens.py
# — {id: {name, is}} — kept HERE beside the binding that renders them (bindings/ has no runtime-module collision;
# the projections/_meta.py attempt taught that lesson). projection.py reads this for the "cascade-flow" sector
# domain (was unmapped → humanize-only, no meaning). Each entry is GROUNDED in that role's own ROLE["description"]
# in roles/<id>.py (the op-verbs in the reduce/retrieve op semantics), TRANSLATED to operator language — never
# the chain jargon (RG6 / COMPOSITIONS / MAP-REDUCE / criteria-group). whole_set → no "—" remainder. A step
# present in a saved flow but absent here falls back to a humanized id; composition's set-diff flags it.
# TENTATIVE draft — Tim/DNA ratify (field-set journey-gated, OQ1–4).
CASCADE_FLOW_META = {
    "focus":                {"name": "Read the intent",      "is": "Reads what was said and works out what's being asked, and which steps to run."},
    "eval_classify":        {"name": "Classify a line",      "is": "Labels a short piece of text as a question, a statement, or a command."},
    "decompose_seed":       {"name": "Split an idea into parts", "is": "Takes one big idea and splits it into the smaller parts needed to work on it."},
    "expand_criterion":     {"name": "Spell out a requirement", "is": "Turns one rough part into a full, detailed requirement — what it must do and how it should look."},
    "ground_criterion":     {"name": "Check it actually exists","is": "Checks whether the thing a requirement depends on really exists yet — it won't make one up."},
    "triad_synth":          {"name": "Assemble the plan",     "is": "Pulls the checked requirements together into a complete build plan."},
    "develop_option":       {"name": "Develop an option",     "is": "Works out one full approach to a choice, from one angle."},
    "score_options":        {"name": "Score the options",     "is": "Ranks the approaches that were explored and recommends one — you still decide."},
    "verify_lens":          {"name": "Verify a change",       "is": "Judges a change from one angle — is it correct, does it hold up — before it's accepted."},
    "confirm_registration": {"name": "Confirm a new record",  "is": "Checks a proposed new record honestly matches the real thing — nothing made up — before it's accepted."},
    "repo_digest":          {"name": "Digest a file",         "is": "Sums up, in a sentence, what a piece of the system's code is and does."},
    "reduce_synth":         {"name": "Merge into a summary",  "is": "Joins many separate notes into one short summary."},
    "op:retrieve":          {"name": "Find related",          "is": "Searches the memory and brings back the things closest in meaning."},
    "op:reduce":            {"name": "Combine results",       "is": "Merges many separate results into one combined result (without summarizing them down)."},
}
