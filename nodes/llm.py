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
    # Single-call ceiling. Default = cloud timeout (batch node can wait out a slow cloud queue).
    "timeout":     {"type": "number", "label": "Timeout (s)",   "default": fcfg.DEFAULT_CLOUD_TIMEOUT, "min": 1},
    # Per-DRAW cache-key (Concurrent Cognition C1.5 / R1-FOLD F9). A jury/ensemble role fires N
    # draws of the SAME prompt+model; each draw passes a DISTINCT `draw` id so the memo gate
    # (scheduler._memo_sig hashes ex.config wholesale) gives each a DISTINCT signature → they do
    # NOT collapse into one cached generation. This does NOT disable llm memoization app-wide:
    # an ordinary llm node declares NO draw (default None) → its sig is byte-identical run-to-run
    # → it still memoizes (a real app feature, preserved). `draw` is a pure cache-key differentiator
    # — it is NOT forwarded to the model (the variation comes from temperature>0, set by the jury).
    "draw":        {"type": "number", "label": "Draw id",       "default": None, "min": 0},
}


def run(inputs: dict, config: dict):
    from fabric import client, transport
    model = config.get("model", fcfg.DEFAULT_BRAIN)
    base_url = config.get("base_url", fcfg.DEFAULT_BASE_URL)
    system = config.get("system")
    messages = ([{"role": "system", "content": system}] if system else []) + \
               [{"role": "user", "content": str(inputs.get("prompt", ""))}]
    timeout = config.get("timeout", fcfg.DEFAULT_CLOUD_TIMEOUT)
    t = transport.openai_transport(base_url=base_url, timeout=timeout)
    # `draw` (C1.5) is DELIBERATELY NOT in passthru — it is a memo cache-key differentiator only
    # (varies the scheduler sig per jury draw), never a model sampling param. The actual generation
    # variation a jury wants comes from temperature>0; with temp=0 N draws yield identical text.
    passthru = {k: config[k] for k in ("temperature", "max_tokens", "top_p") if k in config}
    return client.complete(t, messages, model=model,
                           retries=config.get("retries", 3), **passthru)
