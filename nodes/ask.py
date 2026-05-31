"""ask — answer a QUESTION grounded in provided CONTEXT (e.g. the codebase). (first-purpose)

A process node: two inputs (question, context) -> a grounded answer via the guarded fabric.
This is the 'talk over the linked codebase' half of the first purpose. See nodes/AGENTS.md.
"""
VERSION = "1"
KIND = "process"
PORTS_IN = {"question": "Text", "context": "Text"}
PORTS_OUT = {"answer": "Text"}

_SYSTEM = ("You are answering questions about THIS codebase. Use ONLY the provided code/docs. "
           "Cite the file paths you rely on. Be concise and specific.")


def run(inputs: dict, config: dict):
    from fabric import client, transport, config as fcfg
    question = str(inputs.get("question", ""))
    context = str(inputs.get("context", ""))
    model = config.get("model", fcfg.DEFAULT_BRAIN)
    system = config.get("system", _SYSTEM)
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"QUESTION:\n{question}\n\nCODEBASE:\n{context}"},
    ]
    t = transport.openai_transport(base_url=config.get("base_url", fcfg.DEFAULT_BASE_URL))
    return client.complete(t, messages, model=model, retries=config.get("retries", 3))
