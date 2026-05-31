# fabric/ — module constitution

**Is:** the model binding — one endpoint over LiteLLM + llama-swap + adapters, with the reliability guards. The "engine beneath" the runtime calls (S6).
**Guarantees:** **every** model call is guarded — non-empty-content check + JSON-repair-retry + cloud backoff (the `fabric.py` lessons; kimi/glm return empty). VRAM decisions read **live `nvidia-smi`**, never an internal ledger. Structured output validated or **fails loud** (LiteLLM+ollama can silently drop `response_format` — probe `supports_response_schema`). **NO Gemini.**
**Where new things go:** a new model/provider = a **config entry generated from the registry** (not hand-edited); a new capability-type = an adapter (rerank/layout/etc.).
**To extend:** add to the generated LiteLLM/llama-swap config via the registry; or add a capability adapter behind the unified verb.
**Seam:** called by `runtime/`; configured from the type/model registry; the RHM brain is one swappable model slot here (D2).
**Never:** call a model without the guards · hardcode a provider/key · trust a VRAM ledger over the card · use Gemini.
