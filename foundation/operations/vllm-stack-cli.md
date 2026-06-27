---
type: operations
title: vllm-stack CLI
date_started: 2026-05-27
tags: [foundation, operations, cli]
---

# vllm-stack CLI

> [[_operations-index|← Operations hub]]

## State

A bash wrapper at `~/vllm-tests/vllm-stack`, symlinked into `~/.local/bin/vllm-stack` (on PATH). Single command surface for routine substrate operations — start/stop/swap/benchmark/inspect.

## Command surface

```
vllm-stack start                          start both chat + embed
vllm-stack stop                           stop both
vllm-stack restart                        restart both
vllm-stack status                         systemd status + GPU + disk
vllm-stack health                         ping all endpoints (chat, embed, jina-v4, ollama, webui)
vllm-stack ports                          port-to-service map

vllm-stack logs chat                      follow chat logs
vllm-stack logs embed                     follow embed logs
vllm-stack logs jina-v4                   follow jina-v4 logs

vllm-stack list-local                     all downloaded models + sizes + Ollama-registered

vllm-stack bench-chat [flags]             ~/vllm-tests/bench.py
vllm-stack bench-embed [flags]            ~/vllm-tests/bench_embed.py
vllm-stack bench-suite [flags]            ~/vllm-tests/bench_suite.py (deep)
vllm-stack bench-long-ctx [flags]         ~/vllm-tests/bench_long_ctx.py (needs 32K server)

vllm-stack swap-chat <hf-id>              stop chat, edit serve.sh, restart
vllm-stack swap-embed <hf-id>             same for embed

vllm-stack jina-v4 start                  start the optional jina-v4 service
vllm-stack jina-v4 stop                   stop jina-v4

vllm-stack enable-boot                    set services to start at login
vllm-stack disable-boot                   unset auto-start
```

Running `vllm-stack` with no args prints this surface.

## What each section does

**Lifecycle** (`start`, `stop`, `restart`): delegates to `systemctl --user`. See [[systemd-services]].

**Status / health / ports**: composite view of `systemctl status`, `nvidia-smi`, `du`, and HTTP pings. Useful as the one-line check before starting other work.

**Logs**: delegates to `journalctl --user -u <service> -f`. See [[systemd-services]].

**list-local**: enumerates both the HF cache (`~/.cache/huggingface/hub/models--*/`) and Ollama (`ollama list`). Useful for "what do I have on disk and what's registered where."

**Benchmarks**: each one activates `~/vllm-env/` and runs the corresponding script in `~/vllm-tests/`. See [[benchmarks]] for what each measures.

**swap-chat / swap-embed**: the chat-default-model swap procedure. Stops the running service, rewrites the `MODEL="..."` line in the relevant launcher, restarts. Cold start ~2–3 minutes per swap. See [[model-swap]] for the constraint/decision discussion.

**jina-v4**: separate sub-command because jina-v4 is optional — not part of the always-on set in the same way chat and embed are. (Currently `vllm-jina-v4.service` is enabled for boot — this CLI knob lets the service be managed without editing systemd directly.)

**Boot**: wrap `systemctl --user enable/disable`. The boot-and-linger discussion is in [[boot-and-linger]].

## Why a CLI

Same reason any operational system has one: a stable surface that names the routine operations, so the routine operations don't need re-derivation each time. Future agents reading this folder know that `vllm-stack swap-chat <hf-id>` is the canonical way to change the deployed chat model — they don't need to learn the underlying sequence of systemctl + sed + restart.

The CLI also embeds **the right defaults** — e.g. running the bench-suite via `vllm-stack bench-suite` doesn't require the caller to remember to activate the venv first.

## Adding a command

The CLI is at `~/vllm-tests/vllm-stack`. Bash, single file. To add a new command:

1. Add a new `case "${1:-}"` branch
2. Document at the top of the file (the usage block is the source of truth for `vllm-stack` with no args)
3. Match the existing pattern: short, single-purpose, no nested logic

Don't grow this into a tool; it's a surface, not an engine.

## Open at this topic

- No `vllm-stack swap-jina-v4` command (jina-v4 is single-tenant on its venv; less swap-likely)
- No `vllm-stack ollama <register|deregister>` command for GGUF lifecycle — could be useful as more GGUF models are added
- No `vllm-stack export-state` to dump current substrate config (services, models, env) into a portable artifact — would help disaster recovery
- No autocomplete for tab-completion of subcommands or HF model IDs

## Connects to

- [[_operations-index]] — hub
- [[systemd-services]] — what the lifecycle commands delegate to
- [[model-swap]] — the swap procedure
- [[benchmarks]] — what the bench-* commands run
- Source: `~/vllm-tests/vllm-stack`, symlinked to `~/.local/bin/vllm-stack`
