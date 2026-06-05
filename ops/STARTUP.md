# Company — Startup (the one place everything starts from)

> **The single command:** `systemctl --user start company.target`
> Everything the Company needs comes up from here, each set to restart-on-failure, and auto-starts at boot (user-linger is enabled). Built 2026-06-04 to replace the scatter of hand-started processes.

## The command center — `company`
One console to **see what's running and start/stop/restart it**. It reads the self-describing registry (`ops/services.json`) and drives systemd underneath. Callable from anywhere (symlinked into `~/.local/bin`).
| Do | Command |
|---|---|
| **See everything + its state** | `company` (or `company status`) |
| Start the core set (autostart) | `company up` |
| Start one / a group / all | `company up bridge` · `company up voice` · `company up all` |
| Stop one / a group | `company down bridge` · `company down models` |
| Restart one | `company restart bridge` |
| Tail a service's logs | `company logs bridge -f` |
| What it can do | `company help` |

`company status` shows each service grouped (core · brain · voice · models · reach), its live state (▶ running · ◐ active-no-port-yet · ✖ failed · · stopped), and **drift** (e.g. "RUNNING (unmanaged)" when something is up by hand instead of under systemd). Add a service = add an entry to `ops/services.json`.

### Underneath: systemd (the muscle — still usable directly)
| Do | Command |
|---|---|
| Start/stop the whole core target | `systemctl --user start\|stop company.target` |
| Dependency tree | `systemctl --user list-dependencies company.target` |
| Direct unit control | `systemctl --user restart company-bridge.service` |

## What starts, and where
| Service | Port | What it is | Unit |
|---|---|---|---|
| canvas | 5173 | the operable surface (vite dev server) | `company-canvas.service` |
| bridge | 8770 | UI face of the Suite — the HTTP API the canvas + phone hit | `company-bridge.service` |
| brain (4B) | 8000 | vLLM `Qwen3.5-4B-AWQ` chat (the model) | `vllm-chat.service` |
| TTS (Kokoro) | 4123 | voice out | `company-tts-kokoro.service` |
| STT (Whisper) | 2022 | voice in | `voicemode-whisper.service` |

Each has `Restart=on-failure` (**proven**: kill the bridge → systemd respawns it, port back in ~5 s).

### Already-reliable SYSTEM services (auto-start, not in the target by design)
- **ollama** (`:11434`) — `ollama.service` (system)
- **tailscaled** + `tailscale serve` (canvas + bridge over tailnet HTTPS to the phone at `https://workstation001.tail777bc2.ts.net/`) — `tailscaled.service` (system)

## Boot behaviour
`loginctl enable-linger tim` is set → the user services start when **WSL** boots, no login needed. (See the open item below about WSL itself starting on Windows boot.)

## ⚠️ Open items (flagged, not silently decided)
- **vLLM config drift — needs a decision (native-model-layer stage).** The 4B that was running by hand used `--gpu-memory-utilization 0.80 --max-model-len 32768` (big context, **no** tool-calling). But `vllm-chat.service` runs `~/vllm-tests/serve.sh`, which uses `--gpu-memory-utilization 0.40 --max-model-len 4096 --enable-auto-tool-choice --tool-call-parser qwen3_xml`. **They differ**, so post-restart the brain comes up with serve.sh's config (smaller context, tool-calling on). The RHM wants *both* tool-calling and adequate context — settle the canonical config in the model-layer work. (For now the hand-started 4B is left running; `vllm-chat.service` is enabled for boot but not started, to avoid disrupting the loaded model.)
- **WSL at Windows boot.** Linger starts the services when *WSL* starts — but WSL only starts when Windows launches it. For the box to be reachable after a Windows reboot with no login, add a Windows Task Scheduler entry that runs `wsl` at logon/startup (Windows-side; separate from this).
- **Other models** (`vllm-embed` BGE-M3, jina, larger models) are deliberately **not** in `company.target` — 16 GB VRAM can't hold them alongside the 4B; they belong to the model-layer / VRAM-swap stage.

## Canonical unit files
The unit files live in `ops/systemd/` (this repo) as the source of truth. To (re)install on a fresh machine:
```
cp ops/systemd/*.service ops/systemd/*.target ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now company.target
loginctl enable-linger $USER   # start at boot without login
```
(`vllm-chat.service` + `voicemode-whisper.service` are existing units pulled into the target via `systemctl --user add-wants company.target <unit>`.)

## Reaching it from Tim's phone (DONE + WORKING — 2026-06-04/05)
The Company is **already usable on Tim's iPhone** — this is the established, expected path, not a plan. If Tim says "my phone" / "Tailscale" / "the mobile access", it's this.
- **Tailnet** `workstation001.tail777bc2.ts.net` (Tailscale **Standard plan**); **HTTPS certificates enabled** in the admin DNS console.
- **`tailscale serve`** exposes the **canvas (:5173)** and **bridge (:8770)** over tailnet HTTPS at `https://workstation001.tail777bc2.ts.net/`. The vite dev server allows the tailnet host via `allowedHosts: ['.tail777bc2.ts.net']` in `canvas/app/vite.config.*` (else 403).
- Installed as a **PWA**: full-screen home-screen app ("Vi", gold icon `vi-classic-gold.png`, theme `#d4af37`, `viewport-fit=cover`). Real HTTPS is required for the iOS browser mic (`getUserMedia` secure-context) → enables in-browser voice.
- Survives reboot via `company.target` (+ linger). Cross-session memory: `project-mobile-access-tailscale`.
