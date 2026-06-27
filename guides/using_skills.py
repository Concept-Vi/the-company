"""guides/using_skills.py — the SEED guide (the demonstrative first member).

A GUIDE is a declared, reusable NARRATIVE how-to — the prose a human/agent reads to LEARN a part of
the system (the second face of "one entry, two faces"; the first face is the dense skill:// a role
reads mid-task). This is the registry's first member (like skills/summarize.py was the seed skill,
roles/judge.py the seed role): real + grounded, so `guide://using_skills` resolves to an actual,
verifiable how-to.

It documents the SKILL registry (target `skill://summarize`, the canonical worked example) — a
non-obvious-use system, the right CARRIER for a guide (the review's [A4]: guides attach to systems/
capabilities, NOT to operational role-inputs themselves). It is grounded in the real files
(`skills/AGENTS.md`, `runtime/skills.py`, and `skill://summarize`'s resolved content) — nothing here
is invented. `source_hash` is the sha256 prefix of `skill://summarize`'s content at authoring time;
if that content changes, the hash differs → this guide is STALE and due a re-author (freshness).

Drop a 2nd `guides/<id>.py` (a `GUIDE` dict) to add another guide — it self-registers + becomes
`guide://<id>` (the file-discovered, registry-is-truth path). Its `id` MUST equal the file stem.
"""

GUIDE = {
    "id": "using_skills",
    "label": "Using skills",
    "description": "How to author and use a skill in the Company — what a skill is, when to add one, how it resolves.",
    "target": "skill://summarize",
    "grounded_from": [
        "skill://summarize",          # the worked example this guide teaches from (resolved + hashed)
        "file://skills/AGENTS.md",    # the skills constitution (the drift home)
        "file://runtime/skills.py",   # the registry implementation (the mechanism)
    ],
    "source_hash": "d2a7fea181874a7c",
    "content": (
        "# Using skills in the Company\n"
        "\n"
        "A **skill** is a reusable unit of *instructions* — the text a ROLE reads as its primary "
        "input mid-task. Skills are a file-discovered registry (registry-is-truth): one "
        "`skills/<id>.py` per skill, self-registering, addressable as `skill://<id>`.\n"
        "\n"
        "## When to reach for one\n"
        "Add a skill when you have an instruction-set a role should read repeatedly — a condensation "
        "brief, an extraction recipe, a multi-step composition playbook. Do NOT reach for a skill for "
        "a one-off prompt; reach for it when the instructions are *reused by address*.\n"
        "\n"
        "## How to add one (the only steps)\n"
        "1. Create `skills/<id>.py` with a module-level `SKILL` dict. Its `id` MUST equal the file "
        "stem, and it MUST declare a non-empty string `content` (the instructions). `label` and "
        "`description` are optional operator-facing fields.\n"
        "2. That's it — it self-registers on discovery; `skill://<id>` now resolves to its `content` "
        "with NO change to the resolver, the cognition driver, or the UI.\n"
        "3. Reflect the new skill in `skills/AGENTS.md` (the drift home) — "
        "`tests/skills_contexts_acceptance.py` fails loud if a discovered skill is not reflected there.\n"
        "\n"
        "## Worked example (the target of this guide)\n"
        "`skill://summarize` resolves to a faithful-condensation brief: keep every load-bearing fact "
        "and relationship, add nothing, return the condensation only. A role with "
        "`input_addresses=[skill://summarize]` reads exactly that as its input.\n"
        "\n"
        "## Gotchas (learned from the schema)\n"
        "- The `SKILL` schema is a STRICT closed set: `{id, content, label, description}`. An unknown "
        "field FAILS LOUD at discovery — you cannot quietly add a field no consumer reads.\n"
        "- `id` must equal the filename, or discovery RAISES.\n"
        "- An unknown `skill://<id>` RAISES — registry-is-truth never fabricates a missing skill.\n"
        "- A skill is the dense INSTRUCTION face. To document a system for a *learner*, write a GUIDE "
        "(`guide://<id>`, this registry) — do not stuff narrative into a skill's `content`.\n"
    ),
}
