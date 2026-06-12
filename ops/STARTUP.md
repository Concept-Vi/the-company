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

`company status` groups services (core · brain · voice · models · reach · jobs), shows live state
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

### Jobs — scheduled derived-data beats (the `jobs` group)
Timers, not ports. `◐ active` = armed (next fire on schedule); `· stopped` = disarmed.
They are bound to `company.target` (`add-wants`, NOT `enable` — boot-autostart stays off), so
they **rise and fall with the Company**: `company up/down jobs` (or `all`, or each by name) arms/
disarms them, `systemctl --user start/stop company.target` does too, and `company status` shows
them. No invisible orphan timers (Tim's requirement).

The **interim transcript-search circuit** (throwaway — Tim is building the real memory system
elsewhere) is two beats in this group, one feeding the next:

| Beat | Fires | Does |
|---|---|---|
| `agent-sessions-exporter` | `*:00/20` (every 20 min) | Claude session jsonl → `~/corpora/claude-sessions/**/*.md` (filtered, redacted, idempotent). `ops/agent_sessions_exporter.py`. |
| `claude-sessions-reindex` | `*:05/20` (5 min later) | substrate **DELTA** reindex of the `claude-sessions` vault so search stays current. Cheap-by-design: a marker (`~/corpora/claude-sessions/.reindex_marker.json`) gates it — if no transcript changed it exits doing nothing (no model load, no GPU). `ops/claude_sessions_reindex.py`. |

The reindex embeds via the `embed-pplx` service (`company up embed-pplx`) into an **isolated**
substrate state dir (`~/.cache/company/substrate-claude-sessions`, separate from the bge-m3
substrate). Search it: `ops/wire_substrate_claude_sessions.py search "query" [--rerank]` (full
substrate face) or `ops/transcript_search.py search "query"` (numpy fallback). If the embedder is
down when there's work, the reindex **fails loud** (exit non-zero) and leaves the marker stale so
the next fire retries — it never fakes an index.

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
Every installed user-unit lives in `ops/systemd/` (this repo) as the source of truth
(canonicalized 2026-06-06). When you add/change a unit, keep its `ops/systemd/` copy in sync.

## Rebuild from the repo
What the repo fully describes and can restore on a fresh machine:
- the console (`ops/cli/` + `ops/company`), the registry (`ops/services.json`),
- the generic launcher (`ops/serve_model.sh`), and **all installed systemd units** (`ops/systemd/`).

To reinstall the runtime layer:
```bash
cp ops/systemd/*.service ops/systemd/*.timer ops/systemd/*.target ~/.config/systemd/user/
systemctl --user daemon-reload
# Bind the job timers to the Company target (creates company.target.wants/ symlinks;
# does NOT enable boot-autostart — company.target itself stays disabled):
systemctl --user add-wants company.target \
  company-agent-sessions-exporter.timer company-claude-sessions-reindex.timer
systemctl --user daemon-reload
# do NOT `enable` anything else — boot-autostart is off by design; bring up on demand:
company status        # confirm the map (jobs included)
company up            # the surface (canvas + bridge)
company up jobs       # arm the scheduled beats (exporter + reindex)
```
**What the repo does NOT carry (separate restore — flagged honestly):**
- the model-serving venvs (`~/vllm-env`, `~/.voice-venvs/*`) and the model weights
  (HF cache, Ollama store) — large, live outside the repo;
- legacy serve scripts (`~/vllm-tests/serve_*.sh`) that script-based services still source.
  **Config-driven models** (a `config` block + `serve_model.sh`, e.g. chat-2b/chat-08b) need
  none of those scripts — migrating the rest to `config` makes the repo progressively more
  self-sufficient. The 5 voice trial engines (`company-voice-*`) have no unit yet — install,
  then add the unit to `ops/systemd/`.
