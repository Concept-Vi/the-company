---
type: hub
title: Operations — Index
folder: operations
date_started: 2026-05-27
tags: [foundation, operations, hub, moc]
---

# Operations — Index

> Folder: `~/company/foundation/operations/`
> All entries here follow [open-future mode]([[../TIM#Layer 3 — Open-future writing mode (2026-05-27)]]) — provisional, dated, examples-not-specs, every closure marked, every gap explicit.

This file is the hub for everything operational about the substrate that serves the [[../models/_models-index|models]]: runtimes, toolchain, services, command surface, deployment patterns, troubleshooting. Each topic has its own file; this hub maps them by purpose.

The split is deliberate: the [[../models/_models-index|models hub]] answers "which model for which need"; this hub answers "how to run, deploy, swap, debug, and operate the substrate."

## How this folder works

- **One file per operational topic.** Filenames are short and purpose-named: `cuda-toolchain.md`, `runtimes.md`, `vllm-stack-cli.md`, etc.
- **Hub-to-topic links** use wikilinks: `[[runtimes]]`.
- **Each topic file holds**: what the topic is, current state (configurations, paths, versions), why decisions were made the way they were (so future agents can reverse-engineer them rather than guess), known-good procedures, known failure modes + recoveries, open questions.

## How to add a new operational topic

A future agent extending this folder works through this sequence:

1. **Identify the topic boundary.** Is this a new top-level concern (a new runtime, a new service tier) or an extension of an existing topic? Prefer extension when the boundary is unclear.
2. **Create** `~/company/foundation/operations/<purpose-name>.md` using the closest existing file as template.
3. **Fill** state, decisions, procedures. Leave open registers where unknowns exist.
4. **Add a row** to the appropriate section of this hub.
5. **Cross-link** to models that depend on this topic and to other operational topics that touch it.
6. **Date** every claim about runtime versions, paths, observed behaviour.

## Topics by purpose

### Runtimes — what serves models

| Topic | Role |
|---|---|
| [[runtimes]] | The three local runtimes (vLLM, Ollama, jina-v4-env) plus Open WebUI; why each exists; what each serves; constraints |
| [[cuda-toolchain]] | The CUDA pinning that makes vLLM + flashinfer work on WSL — the load-bearing fix without which nothing serves |
| [[chat-template-patch]] | The no-think chat template that makes Qwen3.5-4B-AWQ behave as a default chat model rather than a reasoning-mode model |
| [[system-prompts]] | Territory map: where system prompts can be set; how they relate to chat templates, modes, persona, the Company's entity-voice |
| [[ollama]] | Ollama-specific operational notes — model registration, Modelfile pattern, cloud routes |
| [[open-webui]] | The interactive chat UI on port 8080 — what it can and cannot configure, what reaches vLLM vs what's UI-side |
| [[open-webui-extras]] | Catalog of every provider / tool / integration Open WebUI 0.9.5 can have plugged in — search, image gen, voice, code exec, doc processing, MCP, OAuth, model providers, etc. |

### Lifecycle — how services start, stop, swap

| Topic | Role |
|---|---|
| [[systemd-services]] | The systemd user units (`vllm-chat`, `vllm-embed`, `vllm-jina-v4`) — boot, restart-on-failure, logs |
| [[vllm-stack-cli]] | The `vllm-stack` command surface — every routine operation has a one-line invocation |
| [[model-swap]] | The pattern for swapping the chat or embed default to a different model; the VRAM constraints that make swap-vs-co-resident the central trade |
| [[boot-and-linger]] | What happens at WSL reboot; the `loginctl enable-linger` step that decides whether services survive user-session ends |

### Substrate state

| Topic | Role |
|---|---|
| [[vram-budget]] | The 16 GiB VRAM accounting — what fits with what, current co-resident default, swap-only frontiers |
| [[ports]] | Which port runs which service; the canonical map |
| [[paths]] | Where things live on disk — venvs, HF cache, foundation, vllm-tests, ollama cache |

### Diagnostics — when things go wrong

| Topic | Role |
|---|---|
| [[troubleshooting]] | Known failure modes and their fixes — the patterns that took time to discover, written down so they don't have to be re-discovered |

### Benchmarking and validation

| Topic | Role |
|---|---|
| [[benchmarks]] | The benchmark scripts in `~/vllm-tests/` — what each measures, how to run, how to interpret |

## Source archive

Operational knowledge originated in `~/vllm-tests/` during the substrate's initial setup. Those files remain the **primary operational record** (configs that actually run, scripts that actually execute); this folder is the **synthesis** — distilled, indexed, cross-linked, agent-onboardable. The same synthesis/source split used for [[../exchanges/_exchanges-index|exchanges]] applies here.

When operational details change, the primary source (`~/vllm-tests/serve.sh`, `~/.config/systemd/user/*.service`, etc.) is updated first; this folder is updated to reflect.

## Open at this folder

- Topics that exist but are not yet split into their own files (anything operational not in the table above is implicitly open)
- The `troubleshooting` file is a placeholder; failures and fixes accumulate there as they occur and as memory of past fixes is consolidated
- Monitoring / observability — none currently set up beyond `journalctl` and `nvidia-smi`; an explicit topic when this becomes a need
- Security — the substrate is currently localhost-only with no auth; an explicit topic when exposed beyond localhost
- Backup / recovery for the HF cache, the venvs, the Ollama registry, and the foundation knowledge layer itself
- The relationship between this operations layer and any future Company-side ops (when the Company grows beyond the substrate, operational concerns will surface that aren't yet here)

## Connects to

- [[../TIM]] — foundation document
- [[../models/_models-index]] — what these operations serve
- [[../exchanges/_exchanges-index]] — verbatim source for conversations that produced this knowledge
- [[../system/README]] — synthesis layer; principles + architecture
