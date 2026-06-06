# `company` — the Company's control surface (use guide)

`company` is the ONE command for operating the whole running system: see and
start/stop services, manage the local models, and read + budget the GPU (the
resource manager). It reads the self-describing registry `../services.json` and
drives systemd underneath. Callable from anywhere (`~/.local/bin/company`).

**Nothing auto-starts at boot** (Tim, 2026-06-06). The machine boots cold; you bring
up exactly what a task needs with `company up` and free it with `company down`. Only
`ollama` and `tailscaled` stay enabled at boot (system services).

## Everyday commands
| Command | Does |
|---|---|
| `company` or `company status` | every service grouped (core·brain·voice·models·reach), live state, ~VRAM cost, GPU budget |
| `company up [TARGET] [--force]` | start. No TARGET = the surface (canvas+bridge). |
| `company down TARGET` | stop |
| `company restart TARGET [--force]` | restart |
| `company logs SERVICE [-f]` | tail a service's journal |
| `company gpu` | measured VRAM used/free + what's holding the card |
| `company health` | quick ✓/✗ port ping of every service |
| `company models` | what's on disk (HF cache for vLLM + Ollama's own store) |
| `company swap SERVICE MODEL_ID` | point a model service at another model + restart |
| `company bench chat\|embed\|suite\|long-ctx [args]` | run a stack benchmark |
| `company telemetry` | learned model load times + measured VRAM vs the registry estimates |
| `company help` | the built-in summary |

`TARGET` = a **service key** (`bridge`, `chat-4b`), a **group** (`core`, `brain`,
`voice`, `models`, `reach`), or **`all`**. Examples:
```
company up                 # bring up the surface
company up brain           # start the 4B chat worker
company up voice           # TTS + STT
company down models        # free all model servers
company swap chat-4b cyankiwi/Qwen3.5-4B-AWQ-4bit
company logs bridge -f
```

## The resource manager (VRAM budget + scheduling)
The card is 16 GB and the models don't all fit at once, so `company up`:
- **always prints what's holding the GPU** (measured used/free + the running model/voice
  services and their ~VRAM) — so any agent knows the state without a second call;
- **REFUSES a start that would exceed capacity** (measured free vs the *learned-or-estimated*
  cost of what you're starting), telling you the shortfall;
- **`--evict`** makes room automatically: stops running GPU services (models→brain→voice,
  largest first) only until the start fits, then starts — the scheduling step beyond refuse;
- **`--force`** overrides a refusal (loudly) — for cases you know offload is acceptable;
- **`--wait`** blocks until the model is actually serving, then records its **real** load
  time + **measured** VRAM to telemetry. Over time the gate budgets against measured
  numbers, not guesses — see `company telemetry`. Detection of "what's running" uses the
  per-unit `systemctl is-active`, never the port (model services share ports).

Examples:
```
company up chat-4b --wait         # start the 4B, wait for it, record its real cost
company up embed-jina-v4 --evict  # auto-free room for jina-v4, then start it
company telemetry                 # see measured load times + VRAM vs the estimates
```

State symbols in `status`: ▶ running · ◐ active-no-port-yet · ✖ failed · · stopped ·
"RUNNING (unmanaged)" = up by hand, not under its unit (drift).

## What's where
- `../company` — launcher (thin; runs this package).
- `app.py` — command dispatch.   `registry.py` — reads `services.json`.
- `systemd.py` — start/stop/status/logs.   `gpu.py` — **the resource manager** (read card, enforce budget, plan evictions).
- `telemetry.py` — records real loads (measured VRAM + load time); feeds the budget.
- `models.py` — inventory + `swap`.   `bench.py` — benchmarks.   `render.py` — `status`/`health` views.
- `../services.json` — the registry (source of truth).   `../AGENTS.md` — the constitution.
- To change/extend the CLI, read **UPDATING.md**.
