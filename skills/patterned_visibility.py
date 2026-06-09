"""skills/patterned_visibility.py — AK3 composition SKILL (Cognition Engine · per-workflow recipe).

The patterned-visibility loop as a reader-composable recipe: run → look/compare → mark patterns →
reveals the next step → repeat. The "mark" step is encoded HONESTLY — there is NO write-mark MCP tool
today (writing marks is a later STORE pass; `findings_for` only READS). So "mark a pattern" = encode it
as a NEW LENS via create_projection, which drives the next capture round (that IS "reveals next step →
repeat"). Audience: an agent/operator-facing composition playbook (same registry format as
skill://summarize). FLOOR: describes composing READ / RUN / declarative-create tools only — never
emits resolve/approve/dispatch.
"""

SKILL = {
    "id": "patterned_visibility",
    "label": "The patterned-visibility loop",
    "description": "Recipe: run → look/compare (list_corpus·find_corpus·find_relations·findings_for) → mark the pattern (create_projection encodes it as a lens) → that reveals the next step → repeat. Discovery is not pre-scripted; each look reveals what to do next.",
    "content": (
        "THE PATTERNED-VISIBILITY LOOP — discovery is NOT a pre-scripted plan; it is a loop where each\n"
        "LOOK reveals the next step. RUN something, LOOK at / COMPARE the output, MARK the pattern you\n"
        "see, and that mark reveals the next run. Repeat until the patterns stop revealing new steps.\n"
        "\n"
        "THE LOOP (drive these REAL tools; the loop, not any single tool, is the recipe):\n"
        "\n"
        "1 · RUN — produce something to look at:\n"
        "   capture(role, units, project, session, round, projection=<lens>) for a fresh describe pass,\n"
        "   OR run_items(role, items) for a MAP over addressed units,\n"
        "   OR run_reduce(addresses, mode='cluster') to group 'which are the same'.\n"
        "   (See skill://corpus_pipeline for the full pipeline these sit in.)\n"
        "\n"
        "2 · LOOK / COMPARE — read the output back and put pieces side by side (all READ-only):\n"
        "   • list_corpus(project=P) — every record the capture produced (newest-first).\n"
        "   • find_corpus(project=P, projection=<lens>, kind=, source_address=) — filter to one axis to\n"
        "     compare just those records (e.g. every principles-lens record in a project).\n"
        "   • read_corpus_record(address) / inspect_address(address) — read ONE record/output verbatim.\n"
        "   • find_runs(role=, op=, run_op=) — discover PAST runs + their run:// addresses to compare\n"
        "     across passes (the run index).\n"
        "   • find_relations(item, near_space, far_space) — the INVERSION look: items NEAR in one space\n"
        "     but FAR in another (see skill://inversion_query) — surfaces a pattern you could not see by\n"
        "     reading records one at a time.\n"
        "   • findings_for(address) — read the MARKS already left on an address (the detection thread so\n"
        "     far; positive-only, see-WHY). An unmarked address returns an HONEST empty list.\n"
        "\n"
        "3 · MARK THE PATTERN — encode what you saw so it persists + drives the next run:\n"
        "   IMPORTANT: there is NO write-mark MCP tool today. Writing a `mark` is a later STORE pass;\n"
        "   findings_for only READS marks. So you MARK a pattern by ENCODING it as a new LENS:\n"
        "     create_projection(spec={id, level, produced_by:'model'|'code', embeds:bool, field?, enum?,\n"
        "                             desc:<render-NOT-judge instruction>, stage?})\n"
        "   → the lens applies LIVE everywhere with no code change (capture-schema, the vector spaces\n"
        "     find_relations ranges over if embeds=true, and cognition_info().projections/.spaces). The\n"
        "     desc DESCRIBES what a unit claims; it does NOT judge truth (that is a later reduce). This is\n"
        "     the durable record of 'I noticed this pattern is worth describing across the corpus.'\n"
        "\n"
        "4 · THAT REVEALS THE NEXT STEP — re-run with the new lens:\n"
        "   capture(role, units, project, session, round=<R+1>, projection=<the lens you just created>)\n"
        "   → a new round of records under the new lens. If the lens embeds, the engine capture+embed\n"
        "     pass populates its vector space, so find_relations can now range over it (step 2 next loop).\n"
        "   GO BACK TO 2 — look at the new output, compare to the prior round, mark the next pattern.\n"
        "\n"
        "WHY A LOOP, NOT A LIST: you cannot script which lens matters before you have LOOKED. The corpus\n"
        "is a lossy echo; the gold is the MEANING, surfaced by comparing. Each pass's `round` increments\n"
        "so the lineage shows the detection thread. Stop when a look reveals no new pattern worth\n"
        "encoding. INVERSION USE: the same looking tools find what is MISSING / generic — run a known\n"
        "fingerprint as the `near` item in find_relations and read the gaps (see skill://inversion_query)."
    ),
}
