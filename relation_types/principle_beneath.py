"""relation_types/principle_beneath.py — SEED relation-type: principle-beneath (DIRECTED).

A directed edge: unit A expresses a PRINCIPLE that lies BENEATH unit B (A→B, the principle under the
instance). Computed over the `principles` space (the meaning-level corroboration space) — the
inversion-finder reads `near=principles`. Directed (the principle/instance ends differ). See
runtime/relation_types.py + relation_types/AGENTS.md. Its `id` MUST equal the file stem
(`principle_beneath`); the hyphenated edge name lives in `label`.
"""

RELATION_TYPE = {
    "id": "principle_beneath",
    "label": "principle-beneath",
    "directed": True,
    "near": "principles",
    "desc": "A expresses the principle beneath B (the principle under the instance; directed A→B)",
}
