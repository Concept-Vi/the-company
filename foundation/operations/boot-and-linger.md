---
type: operations
title: Boot, linger, and WSL lifecycle
date_started: 2026-05-27
tags: [foundation, operations, boot, wsl]
---

# Boot, linger, and WSL lifecycle

> [[_operations-index|← Operations hub]]

## The two lifecycle layers

1. **User session lifecycle**: the lifetime of a Tim-WSL-terminal-session. User systemd services live and die with this.
2. **WSL distro lifecycle**: the lifetime of the WSL Linux distro inside Windows. The distro can shut down when no terminals are open (Windows tears it down to save resources).

The substrate's user-level services ([[systemd-services]]) — `vllm-chat`, `vllm-embed`, `vllm-jina-v4` — depend on **user session lifecycle** by default. They auto-start when the user logs in (because they're `enabled`). They stop when the user's session ends.

The system-level Ollama service depends on the **WSL distro lifecycle**. It runs as long as the distro is up. Same for `docker` (Open WebUI container) — system-managed.

## The linger setting

```
sudo loginctl enable-linger tim
```

Enabling linger tells systemd "even when this user has no active session, keep their user systemd instance running." Effect: the user-level services survive after Tim closes all terminals.

Linger does **not** prevent WSL itself from shutting down — Windows can still tear down the distro if it judges idle. But on most modern Windows + WSL2 configurations the distro stays running while any process is active inside it, so enabling linger effectively keeps the substrate's services up.

**Current state as of 2026-05-27**: linger is **not** enabled. Verify:

```
loginctl show-user tim | grep Linger
```

If `Linger=no`, services die when the last terminal closes.

## Decision: enable linger?

Tradeoffs:

**Enable linger** (services stay up):

- Substrate is always reachable; client tools (Open WebUI, future Company-side agents) can connect any time
- Predictable: the endpoints on ports 8000–8002 are either up or not, not "up if you've opened a terminal recently"
- Resource cost: the substrate keeps GPU + RAM allocations live whenever the distro is running

**Don't enable linger** (services lifecycle with sessions):

- Lower idle resource use
- Substrate goes down between work sessions; reboots automatically when next terminal opens
- Cold-start cost paid more often (~150–180s per service)

For a substrate built to be **the Company's serving layer**, linger-enabled is the matching configuration — the Company expects its services to be there whenever any agent in any session needs them. The cost of cold-starting on every session boundary contradicts the "always available" property.

Recommendation: enable linger. Tim's call.

## Restart-on-failure behaviour

Even without linger, the `Restart=on-failure` directive in each service unit means that within a session, a crashed service auto-restarts after 10s. See [[systemd-services]]. This is independent of linger; it just defines what happens if the process exits unexpectedly.

## WSL-specific boot quirks

- **No traditional init.** WSL2 uses systemd if `[boot] systemd=true` is set in `/etc/wsl.conf`. Verified set on this machine; both system and user systemd work.
- **Networking is host-shared by default.** Services on `localhost` from inside WSL are reachable from Windows-side localhost too (via WSL's port forwarding). Open WebUI's host-network mode + the vLLM services on 0.0.0.0 means everything is reachable from either side.
- **GPU passthrough is per-process, not per-distro.** Each process opens its own CUDA context; the `nvidia-smi` shared library lives at `/usr/lib/wsl/lib/`. No WSL-level GPU configuration to maintain.
- **WSL memory ballooning.** Windows can reclaim RAM from WSL under host pressure. Aggressive reclaim has historically OOM-killed engines. No `wsl.conf` memory cap currently set; relying on Windows defaults.

## Restoring the substrate after a WSL reboot

Without linger:
1. Open a WSL terminal (any one)
2. systemd user services auto-start (because `enabled`)
3. Wait ~150–180s for cold start
4. Services healthy

With linger:
1. WSL distro boots (typically on first terminal open after Windows boot)
2. systemd user instance starts; user services auto-start
3. Same cold-start delay
4. Services stay up after terminal closes

## Manual full-substrate startup (after a stop)

```
sudo systemctl start ollama          # if it was stopped (system-level)
docker start open-webui              # if container was stopped
vllm-stack start                     # user-level chat + embed
systemctl --user start vllm-jina-v4  # optional
```

## Open at this topic

- Linger decision (above)
- WSL memory cap (`wsl.conf` settings) — currently default; could be tuned to prevent host-side memory pressure from triggering OOM kills
- Backup / disaster recovery for the substrate state (HF cache, Ollama registry, venvs, foundation knowledge) — no current strategy
- Whether to consolidate to a single substrate-target unit that starts everything in dependency order
- The `loginctl enable-linger tim` command currently requires sudo — needs to be invoked manually by Tim; not automatable from inside the user session

## Connects to

- [[_operations-index]] — hub
- [[systemd-services]] — what linger affects
- [[runtimes]] — what's at stake when services are or aren't up
- Source: `/etc/wsl.conf`, `~/.config/systemd/user/`
