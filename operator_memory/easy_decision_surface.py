"""operator_memory/easy_decision_surface.py — Tim's decision surface is never an isolated technical artifact (GC15 row)."""
MEMORY = {
    "id": "easy_decision_surface",
    "rule": "Never make Tim's decision surface an isolated technical document. Specs/docs are fine and often wanted — addressed to agents; when TIM's guidance is needed, the ask arrives in conversation at his altitude with examples.",
    "why": "He is not a developer and never reads/reviews the files agents do; his guidance is highest-value when the question reaches him in his own shape.",
    "evidence": [
        {"quote": "you should never ask me to read isolated technical specs, it's basically me saying I am not a developer so if you want me to give guidance or response on something make it easy for me", "source": "2026-06-10, rejecting the 'build-and-show don't spec' framing"},
        {"quote": "You will need to explain the decisions to me, I don't understand what you're asking me about what my responses will do", "source": "2026-06-10, mid-walk"}],
    "scope": {"when": "surfacing anything that needs Tim's input"},
    "status": "confirmed",
    "confirmed": "2026-06-10 in conversation (his rewrite of mined rule 2)",
}
