---
type: operations
title: Chat template patch — Qwen3.5 no-think
date_started: 2026-05-27
tags: [foundation, operations, chat-template, qwen]
---

# Chat template patch — Qwen3.5 no-think

> [[_operations-index|← Operations hub]]

## State

The vLLM chat server for [[../models/qwen3_5-4b-awq]] loads its chat template from `~/vllm-tests/chat_template_nothink.jinja`. This is a copy of the model's bundled template with one block inverted so reasoning mode (`<think>`) is **off by default** instead of **on by default**.

## Why this exists

Qwen3.5 chat-tuned models ship with `<think>` mode as the default. Out-of-box behaviour:

- Every assistant turn opens with a `<think>` block before producing the final answer
- The think block consumes output tokens before any user-visible content appears
- Tool calling breaks because the assistant emits reasoning about tool calls in the content stream rather than emitting a `<tool_call>` properly
- TTFT is dominated by think tokens, defeating the latency profile we benchmark

The template's logic before patching:

```jinja
{%- if enable_thinking is defined and enable_thinking is false %}
    {{- '<think>\n\n</think>\n\n' }}   {# empty think block; effectively disables #}
{%- else %}
    {{- '<think>\n' }}                  {# default case: open think; model fills it #}
{%- endif %}
```

Patched (in `~/vllm-tests/chat_template_nothink.jinja`):

```jinja
{%- if enable_thinking is defined and enable_thinking is true %}
    {{- '<think>\n' }}                  {# explicit opt-in to thinking #}
{%- else %}
    {{- '<think>\n\n</think>\n\n' }}   {# default: empty think; thinking disabled #}
{%- endif %}
```

Logical inversion of the condition. Default flips. Opt-in still works for callers that want reasoning mode.

## How it loads

`~/vllm-tests/serve.sh` passes the patched template via `--chat-template`:

```
vllm serve cyankiwi/Qwen3.5-4B-AWQ-4bit \
  ...
  --chat-template ~/vllm-tests/chat_template_nothink.jinja \
  ...
```

The vLLM server picks up the file and overrides the model's bundled template at request-rendering time.

## Why a file, not an edit-in-place

The model's template inside `~/.cache/huggingface/hub/.../chat_template.jinja` is a **symlink** to a blob in the HF cache. Direct edits are refused by the editor tooling (correctly — modifying blobs would corrupt the cache). Copy-and-override via the `--chat-template` flag is the clean path.

## Caller behaviour

| Caller pattern | Effect |
|---|---|
| Default request (no `chat_template_kwargs`) | No thinking. Direct answer. |
| `chat_template_kwargs: {"enable_thinking": true}` | Explicit opt-in to thinking. Model emits `<think>…</think>` then answer. |
| `chat_template_kwargs: {"enable_thinking": false}` | Same as default (explicit no-think). |

Open WebUI and other generic OpenAI clients don't need to set anything — they get the patched default automatically.

## Family coverage

The patch is **Qwen3.5-specific** in implementation. The same logical inversion would apply to [[../models/qwen3_5-0_8b]] and any future Qwen3.5 / Qwen3.6 chat variant that uses the same template structure — but each new model's template needs to be patched separately (each model ships its own copy).

Verified family-compatible templates (same structure, same inversion possible):
- [[../models/qwen3_5-4b-awq]] — patched, deployed
- [[../models/qwen3_5-0_8b]] — verified same template structure 2026-05-26

Other Qwen variants ([[../models/qwen3_5-2b]], the Qwen3.6 GGUF series via Ollama) have not been verified for template structure.

Non-Qwen models ([[../models/nemotron-3-nano-30b-a3b-awq]], [[../models/gemma-4-26b-a4b-gguf-q3-k-m]]) have different template structures and would need their own template-handling decisions — Nemotron may not have a reasoning mode at all; Gemma 4 has its own conventions.

## Open at this topic

- A second patched template for [[../models/qwen3_5-0_8b]] if it gets deployed (template same; the file would be a copy)
- Whether the inversion approach (override at server) vs the chat-template-kwargs approach (per-request) becomes burden as more models join the substrate — could justify a single chat-template-handling layer
- Nemotron's reasoning-mode behaviour (if any) when that model is brought online
- Gemma 4's template conventions for the GGUF variant; how Ollama handles its template directives
- Whether `enable_thinking: true` produces useful reasoning vs hallucinated reasoning — not characterised

## Connects to

- [[_operations-index]] — hub
- [[../models/qwen3_5-4b-awq]] — depends on this patch
- [[runtimes]] — vLLM `--chat-template` flag
- Source: `~/vllm-tests/chat_template_nothink.jinja` (the patched template)
