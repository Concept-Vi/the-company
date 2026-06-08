"""skills/summarize.py — the SEED skill (Concurrent Cognition C 3b · the demonstrative member).

A SKILL is a declared, reusable unit of instructions — the instructions text a role reads as its
INPUT. This is the registry's first member (like roles/judge.py was the seed role): real + usable,
so `skill://summarize` resolves to actual instructions a role can take as its primary input.

Drop a 2nd `skills/<id>.py` to add another skill — it self-registers + becomes `skill://<id>`
(the file-discovered, registry-is-truth path). Its `id` MUST equal the file stem (`summarize`).
"""

SKILL = {
    "id": "summarize",
    "label": "Summarize",
    "description": "Reusable instructions: condense the given content to its essentials, no loss of load-bearing detail.",
    "content": (
        "You are summarizing. Read the supplied content and produce a faithful condensation:\n"
        "- Keep every load-bearing fact, decision, and number; drop only redundancy and filler.\n"
        "- Preserve the relationships between the parts, not just a flat list of points.\n"
        "- Do not add information that is not in the source; do not soften or hedge what it states.\n"
        "Return the condensation only — no preamble."
    ),
}
