"""llm — the first AI process node-type (S6/C2). See nodes/AGENTS.md.

Calls a model through the guarded fabric (non-empty/JSON-repair/validate/fail-loud).
The model is a swappable config slot (D2; default = the ollama-cloud brain). Memoised
like any node, so an identical prompt+config reuses the cached call (don't re-hit the model).
"""
from fabric import config as fcfg   # module-level: CONFIG defaults need DEFAULT_BRAIN/DEFAULT_BASE_URL at load (fabric/config.py imports only os — no cycle)

VERSION = "1"
PORTS_IN = {"prompt": "Text"}
PORTS_OUT = {"text": "Text"}

# Editable fields the inspector renders — verbatim → config_schema (registry.py:62).
# Single source of this node's defaults; mirrors what run() falls back to below.
CONFIG = {
    "model":       {"type": "enum",   "label": "Model",         "default": fcfg.DEFAULT_BRAIN, "options_from": "chat_models"},
    "base_url":    {"type": "string", "label": "Endpoint",      "default": fcfg.DEFAULT_BASE_URL},
    "system":      {"type": "text",   "label": "System prompt", "default": ""},
    "temperature": {"type": "number", "label": "Temperature",   "default": None, "min": 0, "max": 2, "step": 0.1},
    "max_tokens":  {"type": "number", "label": "Max tokens",    "default": None, "min": 1},
    "top_p":       {"type": "number", "label": "Top-p",         "default": None, "min": 0, "max": 1, "step": 0.05},
    "retries":     {"type": "number", "label": "Retries",       "default": 3,    "min": 0, "max": 10},
}


def run(inputs: dict, config: dict):
    from fabric import client, transport
    model = config.get("model", fcfg.DEFAULT_BRAIN)
    base_url = config.get("base_url", fcfg.DEFAULT_BASE_URL)
    system = config.get("system")
    messages = ([{"role": "system", "content": system}] if system else []) + \
               [{"role": "user", "content": str(inputs.get("prompt", ""))}]
    t = transport.openai_transport(base_url=base_url)
    passthru = {k: config[k] for k in ("temperature", "max_tokens", "top_p") if k in config}
    return client.complete(t, messages, model=model,
                           retries=config.get("retries", 3), **passthru)
