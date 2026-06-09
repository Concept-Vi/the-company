"""skills/map_reduce_composition.py — AK3 composition SKILL (Cognition Engine · per-workflow recipe).

map-vs-reduce composition as a reader-composable recipe: WHEN to run_items (1 role × N units, the MAP)
vs run_reduce (the cross-unit JOIN: role|rule|cluster), and HOW to chain them (the run_items `addresses`
output feeds the run_reduce `addresses` input). Audience: an agent/operator-facing composition playbook
(same registry format as skill://summarize). FLOOR: both tools are DRIVERS that emit no
resolve/approve/dispatch — this skill describes composing them only.
"""

SKILL = {
    "id": "map_reduce_composition",
    "label": "map-vs-reduce composition",
    "description": "Recipe: when to run_items (1 role × N units = the MAP) vs run_reduce (cross-unit JOIN: role|rule|cluster), and how to chain them — run_items' `addresses` output feeds run_reduce's `addresses` input.",
    "content": (
        "MAP vs REDUCE — the two composition primitives of the cognition engine, and how to CHAIN them.\n"
        "A single tool-description tells you what each does; THIS recipe tells you which to reach for and\n"
        "how their output→input wiring connects them.\n"
        "\n"
        "THE MAP — run_items(role, items, max_tokens=, temperature=):\n"
        "  1 role × N units. Fans ONE role over N input UNITS in parallel. Each unit is a LITERAL value\n"
        "  OR an ADDRESS (run://… cas://… — resolved via resolve_address). Use it when you want the SAME\n"
        "  operation applied independently to MANY units (describe each, extract from each, classify each).\n"
        "  RETURNS {role, turn_id, n_units, addresses:[run://<turn>/<role>/<i>], resolved, finish_order,\n"
        "           skipped, wall_s}.\n"
        "  KEY OUTPUT: `addresses` — one per OK unit, in unit order. THIS is the handoff to the reduce.\n"
        "  (capture(...) is the MAP variant that ALSO persists durable corpus RECORDS with required\n"
        "   lineage; use capture when the per-unit output must be a reusable queryable record, run_items\n"
        "   when it is an intermediate you feed straight onward — see skill://corpus_pipeline.)\n"
        "\n"
        "THE REDUCE — run_reduce(addresses, mode, role=, reduce_rule=, cluster_threshold=, max_tokens=):\n"
        "  A cross-unit JOIN: collapses a SET of map-output addresses into ONE output. Use it when you\n"
        "  need to combine ACROSS units (synthesize, deduplicate, group, aggregate). THREE modes:\n"
        "    • mode='role'    → SYNTHESIZE join (the model runs, inside the reduce-role). Pass\n"
        "                       role=<a reduce-role id, e.g. reduce_synth from cognition_info().roles>.\n"
        "                       Use for 'write one finding across all these units'.\n"
        "    • mode='rule'    → DETERMINISTIC join, NO model. Pass reduce_rule=<a NAMED built-in>. The\n"
        "                       names come from reduce_rule_names() (currently count·concat·first) — an\n"
        "                       unknown name FAILS LOUD (never a fabricated rule; a callable can't cross\n"
        "                       the MCP boundary, so you select by name). Use for a pure aggregate.\n"
        "    • mode='cluster' → EMBED-CLUSTER join, 'which of these are the same' (needs the embedder\n"
        "                       resident; cluster_threshold default 0.85). Use to DISCOVER groupings.\n"
        "  RETURNS {turn_id, mode, joined, inputs, skipped, wall_s, detail}.\n"
        "\n"
        "HOW TO CHAIN THEM (the load-bearing wiring — this is the whole point):\n"
        "  step 1 (MAP):    m = run_items(role=<a per-unit role>, items=[<N units>])\n"
        "  step 2 (REDUCE): run_reduce(addresses=m['addresses'], mode=<role|rule|cluster>, ...)\n"
        "  → feed the MAP's `addresses` list DIRECTLY as the REDUCE's `addresses`. That list is the\n"
        "    output→input seam. (Filter out m['skipped'] units' slots if a poison unit produced no\n"
        "    address; the addresses list already contains only the OK outputs in order.)\n"
        "\n"
        "COMMON CHAINS:\n"
        "  • MAP then CLUSTER then SYNTHESIZE: run_items(describe) → run_reduce(cluster) →\n"
        "    run_reduce(role) — discover groupings, then write one finding per group. (The corpus\n"
        "    pipeline's LAYER 3 — see skill://corpus_pipeline.)\n"
        "  • MAP then RULE: run_items(extract) → run_reduce(mode='rule', reduce_rule='concat') — gather\n"
        "    every per-unit extraction into one list with no model cost.\n"
        "  • MAP then MAP (no reduce): feed run_items' `addresses` as the NEXT run_items' `items` to apply\n"
        "    a second per-unit role (extract → project) before any join.\n"
        "\n"
        "DECISION RULE: per-unit + independent → MAP (run_items / capture). Across units + one combined\n"
        "output → REDUCE (run_reduce). Need both → MAP then REDUCE, wiring `addresses` → `addresses`.\n"
        "ORIENT from cognition_info().roles for the role ids and reduce_rule_names() for the rule names —\n"
        "never invent an id (registry-is-truth, rule 8)."
    ),
}
