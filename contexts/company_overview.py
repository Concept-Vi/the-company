"""contexts/company_overview.py — the SEED context (Concurrent Cognition C 3b · demonstrative member).

A CONTEXT is a declared, reusable unit of context — a context blob a role reads as its INPUT
(distinct from a skill, which is instructions). This is the registry's first member: real + usable,
so `context://company_overview` resolves to actual content a role can take as its input.

Drop a 2nd `contexts/<id>.py` to add another context — it self-registers + becomes `context://<id>`
(the file-discovered, registry-is-truth path). Its `id` MUST equal the file stem (`company_overview`).
"""

CONTEXT = {
    "id": "company_overview",
    "label": "Company overview",
    "description": "Reusable context blob: what the Company is, in one paragraph, for a role that needs the frame.",
    "content": (
        "The Company is an identity-coupled AI system that the Commander (Tim) directs through a crew "
        "of agents — a multiplier on the Commander's output, not a generic AI framework. It is built "
        "recursively: the system understands and grows its own codebase. Everything is addressed and "
        "registry-driven (registry-is-truth) — node-types, roles, modes, skills, and contexts are all "
        "file-discovered declarations, never literals in code. Cognition is layered: a main stream fed "
        "by a cast of rule-routed model roles, each resolving its input from an address."
    ),
}
