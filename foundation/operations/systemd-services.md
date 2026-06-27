---
type: operations
title: systemd services — vllm-chat, vllm-embed, vllm-jina-v4
date_started: 2026-05-27
tags: [foundation, operations, systemd]
---

# systemd services

> [[_operations-index|← Operations hub]]

## State

Three user-level systemd services (one per local vLLM serving daemon):

| Unit | File | Serves | Port |
|---|---|---|---|
| `vllm-chat.service` | `~/.config/systemd/user/vllm-chat.service` | [[../models/qwen3_5-4b-awq]] | 8000 |
| `vllm-embed.service` | `~/.config/systemd/user/vllm-embed.service` | [[../models/bge-m3]] | 8001 |
| `vllm-jina-v4.service` | `~/.config/systemd/user/vllm-jina-v4.service` | [[../models/jina-embeddings-v4]] | 8002 |

All three are **user-level** services managed under `systemctl --user`. The Ollama service (`ollama.service`) is **system-level**, not user-level — see [[ollama]] for its lifecycle.

## Unit pattern

```ini
[Unit]
Description=...
After=default.target

[Service]
Type=simple
ExecStart=/home/tim/vllm-tests/<launcher>.sh
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
TimeoutStartSec=300

[Install]
WantedBy=default.target
```

The launchers (`serve.sh`, `serve_embed.sh`, `serve_jina_v4.sh`) in `~/vllm-tests/` activate the appropriate venv, set CUDA env vars, and exec the serving binary. Service units delegate to launchers so launch logic can be edited without `systemctl daemon-reload`.

Key fields:

- `Restart=on-failure` — services restart automatically if they crash. Not `Restart=always` because clean exits (manual `systemctl stop`) should stay stopped.
- `RestartSec=10` — wait 10s between restart attempts (prevents tight crashloop).
- `TimeoutStartSec=300` — five minutes for cold start (covers torch.compile + CUDAGraphs warmup, ~150–180s for a fresh model).

## Service lifecycle

| Command | Effect |
|---|---|
| `systemctl --user start <service>` | Start the service |
| `systemctl --user stop <service>` | Stop the service |
| `systemctl --user restart <service>` | Stop + start |
| `systemctl --user status <service>` | Status + recent log lines |
| `systemctl --user enable <service>` | Start automatically at user login |
| `systemctl --user disable <service>` | Don't start automatically |
| `journalctl --user -u <service>` | Full log history |
| `journalctl --user -u <service> -f` | Follow live logs |

All three services are **enabled** for auto-start at user session. They survive normal logout/login of the WSL user session.

## Boot survival — the linger requirement

Default behaviour: systemd user services run **only while the user has an active session**. If Tim closes all WSL terminals and Windows tears down the WSL distro, the user systemd instance shuts down and the services with it.

To keep services running across full WSL teardowns:

```
sudo loginctl enable-linger tim
```

This is **not currently done** as of 2026-05-27. Verify with:

```
loginctl show-user tim | grep Linger
```

If `Linger=no`, services die when no terminal is open. If `Linger=yes`, they persist.

The decision to enable linger is Tim's — it has implications for whether the WSL distro idles to a stopped state vs stays running consuming resources.

## Service unit details (current state)

### vllm-chat.service

```
[Unit]
Description=vLLM Chat Server (Qwen3.5-4B-AWQ) on port 8000
After=default.target

[Service]
Type=simple
ExecStart=/home/tim/vllm-tests/serve.sh
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
TimeoutStartSec=300

[Install]
WantedBy=default.target
```

`serve.sh` exports CUDA env vars (see [[cuda-toolchain]]), activates `~/vllm-env/`, and execs `vllm serve cyankiwi/Qwen3.5-4B-AWQ-4bit ...` with the production flags including `--chat-template ~/vllm-tests/chat_template_nothink.jinja` (see [[chat-template-patch]]).

### vllm-embed.service

Same shape. ExecStart is `serve_embed.sh`. Launches BGE-M3 via `vllm serve BAAI/bge-m3 --runner pooling --gpu-memory-utilization 0.30 ...`.

### vllm-jina-v4.service

Same shape. ExecStart is `serve_jina_v4.sh`. Activates `~/jina-v4-env/` (not vllm-env) and runs `python ~/vllm-tests/serve_jina_v4.py`.

## Common operations

```bash
# Start everything
systemctl --user start vllm-embed vllm-chat vllm-jina-v4

# Stop everything
systemctl --user stop vllm-chat vllm-embed vllm-jina-v4

# Status of all three at once
systemctl --user is-active vllm-chat vllm-embed vllm-jina-v4

# Restart chat after a config change (e.g. new --max-model-len)
systemctl --user restart vllm-chat

# Follow chat logs during a slow startup
journalctl --user -u vllm-chat -f
```

The [[vllm-stack-cli]] wraps the most common operations into a single command surface.

## Failure modes and recovery

| Symptom | Likely cause | Fix |
|---|---|---|
| Service shows `Active: activating (auto-restart)` repeatedly | Crash loop. See `journalctl --user -u <service> -n 100` | Read the actual error; typically [[cuda-toolchain]] drift or OOM |
| "Free memory on device cuda:0 less than desired" | Another process holds GPU memory | Check `nvidia-smi`; often Chrome/X server; lower `--gpu-memory-utilization` if persistent |
| OOM kill during long-running operation | RAM pressure (downloads + services) | Pause downloads; restart service |
| Tool calling 400 Bad Request | Service launched without `--enable-auto-tool-choice --tool-call-parser qwen3_xml` | Update `serve.sh`; restart service |
| Open WebUI shows the model but inference times out | Service is up but model not loaded yet (during torch.compile / CUDAGraphs warmup) | Wait 60–180s for cold start; check logs |

## Open at this topic

- Whether to add a fourth service for [[../models/nemotron-3-nano-30b-a3b-awq]] (it would conflict with the chat default on VRAM — would be a swap-only service, started manually)
- Linger enablement decision (above)
- Logging volume — journals can grow; no rotation policy configured
- Service-level metrics — none collected; would require a separate observability layer
- Whether to register a `vllm-stack.target` to manage all three as one unit
- Restart ordering — currently no inter-service dependencies; could matter if one service relies on another being up

## Connects to

- [[_operations-index]] — hub
- [[runtimes]] — what each service runs
- [[vllm-stack-cli]] — command wrapper around these services
- [[cuda-toolchain]] — what failure looks like when toolchain drifts
- [[boot-and-linger]] — survival across reboots
- Source: `~/.config/systemd/user/vllm-*.service`, `~/vllm-tests/serve*.sh`
