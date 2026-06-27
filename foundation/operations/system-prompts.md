---
type: operations
title: System prompts — territory map
date_started: 2026-05-28
tags: [foundation, operations, prompts, modes]
---

# System prompts

> [[_operations-index|← Operations hub]]

This file claims the territory rather than answering it. Plenty about system prompts isn't decided on this substrate yet — what they do, where they belong, how they relate to chat templates, how they relate to modes, how the Company will use them as it grows. This file holds the map so future agents have a place to add findings without inventing new files.

## What a system prompt is

A message with `role: "system"` placed at (or near) the top of the messages list in an OpenAI-compat chat request. The model treats it as a higher-priority context than the user's messages — typically used to establish persona, capabilities, constraints, output format.

```
[
  {"role": "system", "content": "You are a careful financial analyst. Never invent numbers."},
  {"role": "user", "content": "Summarise this Q3 report."}
]
```

System prompts are **content**, not structure. They're text that the model reads in a privileged position. By contrast, the chat template (see [[chat-template-patch]]) is structural — the jinja that decides how messages get rendered into the model's input token stream.

The two interact: the chat template decides where the system message gets placed and how it's wrapped; the system prompt's content is what fills that slot.

## Where a system prompt can be set on this substrate

| Where | Lifetime | Who controls |
|---|---|---|
| Per-request | One request | Any client calling the API |
| Open WebUI per-conversation | Until conversation cleared | The user in that conversation |
| Open WebUI per-model preset (Workspace → Models) | Until preset edited | Open WebUI admin (Tim) |
| Open WebUI per-prompt template (Workspace → Prompts) | Reusable, applied on selection | Open WebUI admin (Tim) |
| Ollama Modelfile `SYSTEM` directive | Per-model, baked in at registration | Whoever registers the Ollama model |
| vLLM server default | Server can inject via chat-template logic | Server config (`--chat-template`) |
| In the chat template directly | Per-model, structural | Whoever edits the template |

The right level depends on what the prompt does — task-specific framing belongs per-request; persona belongs at preset level; entity-wide voice belongs at server-default or template level.

## What system prompts are usually used for

(Examples; not exhaustive.)

- **Persona / role**: "You are X kind of agent."
- **Tone / register**: "Respond formally / casually / technically."
- **Output format**: "Always respond in JSON. Never include preamble."
- **Capability advertisement**: "You have access to tools: [list]. Use them when needed."
- **Constraint statement**: "Never invent facts. If unsure, say you don't know."
- **Context anchoring**: "The current date is X. The user is in Y timezone."
- **Task framing**: "You are helping the user accomplish Z; ask clarifying questions as needed."
- **Safety / refusal posture**: standard alignment-style instructions.

In practice these layer — most production system prompts include several of the above.

## What's relevant for the Company

This is where this file is most provisional. The Company hasn't decided how it uses system prompts. Surfacing the dimensions:

- **Entity-voice layer**: when the Company speaks as itself (vs a model instance speaking as Claude / Qwen / etc.), the system prompt is where the Company-voice is established. Tied to the **one-entity** principle in [[../TIM]] Layer 4. A canonical Company-voice system prompt that gets applied across all surfaces would make the Company sound like the Company regardless of which model is generating.
- **Modes layer** (Tim raised the modes idea 2026-05-27 — see [[../exchanges/08-modes]]): a "mode" might partly be implemented as a system-prompt swap. Open-future-mode, Skim-mode, Spiral-review-mode each have different output expectations; a per-mode system prompt could activate them.
- **Department layer**: as the Company grows departments, each department has its own framing (engineering vs operations vs research) — system prompts might capture this.
- **Task-specific layer**: per-task framing on top of persona/mode/department.
- **Tim-context awareness**: when an agent is talking *to Tim* vs *acting on Tim's behalf*, the system prompt frames it. "You are speaking with Tim directly; he prefers X" vs "You are working on Tim's behalf; surface decisions only when blocked."

The layered model (entity-voice → mode → department → task → request-specific) is one organising frame. Other frames possible. None of this is locked in.

## Connections to other operations topics

- [[chat-template-patch]] — system prompts and templates are different things; the template decides where the system prompt slots in
- [[open-webui]] — the Workspace → Prompts and Workspace → Models features are the substrate's current per-prompt and per-preset surfaces
- [[ollama]] — `SYSTEM` directive in Modelfiles bakes a default into Ollama-registered models
- [[runtimes]] — vLLM's `--chat-template` flag is where server-default prompts would live if implemented

## Connections to model files

- [[../models/qwen3_5-4b-awq]] — the current deployed chat; any Company-side system-prompt design lands here first
- Different model families respond differently to the same system prompt; system-prompt portability across models is not free

## Open at this topic

(Things known to be unknown.)

- The Company's canonical voice system prompt (does not exist yet)
- The relationship between system prompts and Tim's "modes" concept (not designed)
- The layered model (entity / mode / department / task / request) is one framing; alternatives not explored
- System-prompt versioning — when the entity-voice prompt evolves, what tracks the changes
- Per-model adaptation — the same intent rendered as system prompts that work well across Qwen / Nemotron / Gemma / cloud models
- Tool-availability advertisement — typically belongs in the system prompt; the substrate doesn't have a canonical tool-list yet to advertise
- Multimodal system prompts — can a system prompt include image content (for visual persona examples, layout templates, etc.)? Open
- How a future Commander's-bridge interface handles system prompts (the user shouldn't have to think about them, but they need to be applied)
- Long system prompts and context budget — production system prompts often exceed 500 tokens; this competes with user/assistant content for the context window
- The interaction with prefix caching — system prompts are good candidates for prefix-cache hits if they're stable across requests

## Connects to

- [[_operations-index]] — hub
- [[chat-template-patch]] — structural counterpart to system-prompt content
- [[open-webui]] — current surfaces for setting prompts
- [[../TIM]] — entity-voice and modes principles
