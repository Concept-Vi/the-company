"""skills/corpus_pipeline.py — AK3 composition SKILL (Cognition Engine · per-workflow recipe).

A composition SKILL encodes the RECIPE for a MULTI-STEP cognition workflow — the ORDER, the
output→input WIRING, and when to use which tier. A single tool-description can describe one tool; it
CANNOT encode multi-step composition. This skill is the 3-layer corpus pipeline as a reader-composable
recipe. Audience note: like all four AK3 skills, this is an agent/operator-facing composition playbook
(same registry row + format as `skill://summarize`); a role CAN read it as input, but its primary use is
as the recipe a reader composes the real MCP tools from.

Every tool named below EXISTS in mcp_face/server.py (verified). The FLOOR holds: this skill only
DESCRIBES composing READ / RUN tools — it never instructs emitting resolve/approve/dispatch and never
launches claude -p (a skill is declarative content).
"""

SKILL = {
    "id": "corpus_pipeline",
    "label": "The 3-layer corpus pipeline",
    "description": "Recipe: capture(describe over N units)→run_items(extract)→run_items(project)→[engine embed pass]→run_reduce(cluster then synthesize)→findings_for. The order + each step's output→next-input wiring.",
    "content": (
        "THE 3-LAYER CORPUS PIPELINE — turn a corpus of N units into discoverable, addressed,\n"
        "queryable knowledge. Drive these REAL MCP tools IN THIS ORDER; each step's OUTPUT is the\n"
        "next step's INPUT (the wiring is the recipe — a single tool-desc cannot carry it).\n"
        "\n"
        "ORIENT FIRST (registry-is-truth — never invent an id; read it):\n"
        "  • cognition_info() → .roles (the describe/extract/reduce role ids you may fire),\n"
        "    .projections (the lens ids), .spaces (the embeddable lens ids find_relations ranges over).\n"
        "  Pass only ids that appear there; a fabricated id is a failure (AGENTS.md rule 8).\n"
        "\n"
        "LAYER 1 — CAPTURE (the describe pass · the SINK at scale):\n"
        "  capture(role=<a describe-role id>, units=[<N units: literal values OR run://·cas:// addresses>],\n"
        "          project=<P>, session=<S>, round=<R>, projection=<lens id, optional>)\n"
        "  → fans ONE role over N units (REUSES run_items, the MAP) and PERSISTS one durable corpus\n"
        "    RECORD per OK unit. project·session·round are REQUIRED (lineage gate — a record missing any\n"
        "    is REFUSED fail-loud; it would be uncorroboratable cross-session + unplaceable by the\n"
        "    inversion-finder).\n"
        "  RETURNS {captured:[{i, source_address, address, cas, seq}], skipped, failed, turn_id, ...}.\n"
        "  WIRING: `captured[*].address` are the record addresses; read one back with\n"
        "    read_corpus_record(address) / inspect_address(address); list/filter the set with\n"
        "    list_corpus(project=P) / find_corpus(project=P, projection=<lens>). `skipped`/`failed`\n"
        "    carry units that produced NO record (per-unit resilience — a poison unit never vanishes).\n"
        "\n"
        "LAYER 1b — EXTRACT, then PROJECT (refine the captured units, still the MAP):\n"
        "  These are two further run_items MAP passes — same engine, different role, fed the prior\n"
        "  layer's addressed outputs:\n"
        "  run_items(role=<an extract-role id>, items=[<the addresses captured above>])\n"
        "    → {addresses:[run://<turn>/<role>/<i>], resolved, skipped, ...}. EXTRACT pulls the\n"
        "      structured field-set out of each unit.\n"
        "  run_items(role=<a project-role id>, items=[<the extract addresses>])\n"
        "    → another {addresses:[...]}. PROJECT re-describes each through a specific LENS (or capture\n"
        "      with projection=<lens> in one move). Pass the PRIOR step's `addresses` straight in as the\n"
        "      next `items` — that list IS the output→input handoff.\n"
        "  (Distinguish capture vs run_items: capture persists durable CORPUS RECORDS with lineage;\n"
        "   run_items writes run:// outputs only. Use capture when the output must be a reusable,\n"
        "   queryable corpus record; run_items for an intermediate MAP whose outputs you feed onward.)\n"
        "\n"
        "LAYER 2 — EMBED (per-projection vectors · NOT an agent tool here):\n"
        "  There is NO standalone `embed` MCP tool. LAYER-2 embedding is performed by the ENGINE/BRIDGE\n"
        "  capture+embed pass over the corpus records of EMBEDDABLE lenses (a projection with embeds=true\n"
        "  becomes a vector SPACE — see cognition_info().spaces). The pass writes one per-space vector per\n"
        "  unit at the space-keyed index, which is exactly what LAYER 3's find_relations reads. The\n"
        "  embedder must be UP when this pass runs (a missing anchor makes find_relations fail loud).\n"
        "  If you need a one-off vector of an arbitrary input from the agent seat, that is a DIFFERENT\n"
        "  thing: run_role(role=<r>, op='embed', ensure=True) (ensure=True asks the gated actuator to\n"
        "  load the embedder if it is down) — it returns {vector, dim, model}, it does NOT populate the\n"
        "  corpus space index.\n"
        "\n"
        "LAYER 3 — REDUCE (the cross-unit JOIN · cluster THEN synthesize):\n"
        "  run_reduce(addresses=[<the LAYER-1/1b run:// or record addresses>], mode='cluster',\n"
        "             cluster_threshold=0.85)\n"
        "    → groups 'which of these are the same' (needs the embedder resident). RETURNS {joined, ...}.\n"
        "  THEN synthesize each cluster (or the whole set):\n"
        "  run_reduce(addresses=[...], mode='role', role=<a reduce-role id, e.g. reduce_synth>)\n"
        "    → one synthesized output across the units (the model runs only inside the reduce-role).\n"
        "  (run_reduce mode='rule', reduce_rule=<a NAMED built-in from reduce_rule_names()>, is the\n"
        "   deterministic no-model join — count/concat/first — when you need a pure L2 aggregate.)\n"
        "  CLUSTER-THEN-SYNTHESIZE is the order: cluster discovers the groupings; the role pass writes the\n"
        "  finding per group. Chaining run_items (MAP) → run_reduce (JOIN) is the map-vs-reduce recipe —\n"
        "  see skill://map_reduce_composition.\n"
        "\n"
        "READ THE RESULT — findings_for(address):\n"
        "  findings_for(<a corpus address>) READS the MARKS / gold-likelihood profile a mark-pass left on\n"
        "  that address (oldest-first, positive-only, see-WHY). An address with no findings returns an\n"
        "  HONEST empty list. NOTE: WRITING marks (`mark`) is a later STORE pass and is NOT a tool today —\n"
        "  findings_for is the READ side only. To ENCODE a pattern you discovered, author a new lens with\n"
        "  create_projection and run another capture round (see skill://patterned_visibility).\n"
        "\n"
        "ONE-LINE FLOW:\n"
        "  cognition_info → capture(describe) → run_items(extract) → run_items(project) →\n"
        "  [engine capture+embed pass over embeddable lenses] → run_reduce(cluster) →\n"
        "  run_reduce(role: synthesize) → findings_for / list_corpus to read it back."
    ),
}
