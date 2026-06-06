# Company — Startup & Control (the one place everything starts from)

> **Nothing auto-starts at boot anymore** (Tim's call, 2026-06-06). The Company has many
> models and capabilities that don't all run at once and would fight over 16 GB of VRAM,
> so every service is **on-demand** through the `company` CLI. You bring up exactly what a
> task needs and free it when done. The only things still enabled at boot are the two
> always-on system services: **ollama** and **tailscaled** (the phone path).

## The one command center — `company`
One console to see what's running, start/stop it, manage the local models, and read the GPU.
It reads the self-describing registry (`ops/services.json`) and drives systemd underneath.
Callable from anywhere (symlinked into `~/.local/bin`). The old `vllm-stack` tool is now a
thin shim that forwards here — there is a single brain.

| Do | Command |
|---|---|
| **See everything + state + VRAM budget** | `company` (or `company status`) |
| Start the surface (canvas + bridge) | `company up` |
| Start one / a group / all | `company up chat-4b` · `company up voice` · `company up all` |
| Stop one / a group | `company down chat-4b` · `company down models` |
| Restart one | `company restart bridge` |
| Tail a service's logs | `company logs bridge -f` |
| **Measured GPU VRAM** (used/free of 16 GB) | `company gpu` |
| Quick health ping of every port | `company health` |
| What's on disk (HF cache + Ollama) | `company models` |
| Point a model service at a different model + restart | `company swap chat-4b <model_id>` |
| Run a stack benchmark | `company bench chat\|embed\|suite\|long-ctx [args]` |
| What it can do | `company help` |

`company status` groups services (core · brain · voice · models · reach), shows live state
(▶ running · ◐ active-no-port-yet · ✖ failed · · stopped), each service's **~VRAM cost**, and
a **GPU budget** line. `company up <model>` prints the VRAM it will add against what's already
committed and **warns if the start would exceed 16 GB** (it surfaces the risk; it does not yet
hard-refuse — that resource-manager enforcement is an open decision). Add a service = add an
entry to `ops/services.json` (set `serve` to its serve-script for `swap`, `vram_mb` for budgeting).

### `swap` coverage
Generic over the registry: works for any model service whose `serve` script uses the
`MODEL="${1:-...}"` pattern — verified for `chat-4b`, `embed-bge`, `chat-nemotron`, `chat-2b/08b`.
`embed-jina-v5` and `embed-qwen3` set their model differently, so `swap` will refuse them
cleanly (script left unchanged) until those scripts are normalized.

### Underneath: systemd (the muscle — still usable directly)
| Do | Command |
|---|---|
| Direct unit control | `systemctl --user restart company-bridge.service` |
| A system service (ollama/tailscale) | `sudo systemctl restart ollama.service` |

## Boot behaviour (2026-06-06)
- **No user services auto-start.** `company.target` and all its children, the vLLM units,
  whisper, and the CI runner (`pipeliner`) are **systemd-disabled**. `loginctl` linger may still
  be set, but with nothing enabled, nothing comes up — you start it with `company up`.
- **System services kept at boot:** `ollama.service`, `tailscaled.service`. Disabled at boot:
  `snap.docker.dockerd` (start with `sudo systemctl start snap.docker.dockerd` when you need a
  container), the ubuntu installer junk service.
- **WSL at Windows boot** is still separate (Windows Task Scheduler running `wsl`), if you want
  the box reachable after a Windows reboot with no login.

## Reaching it from Tim's phone (DONE + WORKING — 2026-06-04/05)
The Company is usable on Tim's iPhone — the established, expected path. If Tim says "my phone" /
"Tailscale" / "the mobile access", it's this. Because the surface no longer auto-starts, bring it
up first with **`company up`** (canvas + bridge), then:
- **Tailnet** `workstation001.tail777bc2.ts.net` (Tailscale **Standard plan**); HTTPS certs enabled.
- **`tailscale serve`** exposes canvas (:5173) + bridge (:8770) over tailnet HTTPS at
  `https://workstation001.tail777bc2.ts.net/`. vite allows the tailnet host via
  `allowedHosts: ['.tail777bc2.ts.net']` in `canvas/app/vite.config.*`.
- Installed as a **PWA** ("Vi", gold icon, theme `#d4af37`). Real HTTPS enables the iOS browser mic.
- Cross-session memory: `project-mobile-access-tailscale`.

## Canonical unit files
Unit files live in `ops/systemd/` (this repo) as the source of truth. To (re)install on a fresh
machine, copy them to `~/.config/systemd/user/`, `systemctl --user daemon-reload`. Do **not**
`enable` them — leave boot-autostart off; control everything with `company up`.
