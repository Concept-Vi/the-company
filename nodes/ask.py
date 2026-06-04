"""ask — answer a QUESTION grounded in provided CONTEXT (e.g. the codebase). (first-purpose)

A process node: two inputs (question, context) -> a grounded answer via the guarded fabric.
This is the 'talk over the linked codebase' half of the first purpose. See nodes/AGENTS.md.
"""
from fabric import config as fcfg   # module-level: CONFIG defaults need DEFAULT_BRAIN/DEFAULT_BASE_URL at load (fabric/config.py imports only os — no cycle)

VERSION = "1"
KIND = "process"
PORTS_IN = {"question": "Text", "context": "Text"}
PORTS_OUT = {"answer": "Text"}

_SYSTEM = ("You are answering questions about THIS codebase. Use ONLY the provided code/docs. "
           "Cite the file paths you rely on. Be concise and specific.")

# Editable fields the inspector renders. ask reads ONLY these (no temperature/max_tokens/top_p).
CONFIG = {
    "model":    {"type": "enum",   "label": "Model",         "default": fcfg.DEFAULT_BRAIN, "options_from": "chat_models"},
    "system":   {"type": "text",   "label": "System prompt", "default": _SYSTEM},
    "base_url": {"type": "string", "label": "Endpoint",      "default": fcfg.DEFAULT_BASE_URL},
    "retries":  {"type": "number", "label": "Retries",       "default": 3, "min": 0, "max": 10},
    # Single-call ceiling. Default = cloud timeout (batch node over large context can wait out a queue).
    "timeout":  {"type": "number", "label": "Timeout (s)",   "default": fcfg.DEFAULT_CLOUD_TIMEOUT, "min": 1},
}


def run(inputs: dict, config: dict):
    from fabric import client, transport
    question = str(inputs.get("question", ""))
    context = str(inputs.get("context", ""))
    model = config.get("model", fcfg.DEFAULT_BRAIN)
    system = config.get("system", _SYSTEM)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"QUESTION:\n{question}\n\nCODEBASE:\n{context}"},
    ]
    timeout = config.get("timeout", fcfg.DEFAULT_CLOUD_TIMEOUT)
    t = transport.openai_transport(base_url=config.get("base_url", fcfg.DEFAULT_BASE_URL), timeout=timeout)
    return client.complete(t, messages, model=model, retries=config.get("retries", 3))
