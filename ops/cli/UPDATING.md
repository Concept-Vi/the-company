# Updating `company` (maintenance guide)

For a future AI session changing this CLI. Read `../AGENTS.md` first — it's the
constitution. The non-negotiables: **one console, more *types* not more tools**;
**stdlib-only Python** (no pip deps); **the registry is the only source of truth**
(the console owns no state); **fail loud, never hide drift or failure**.

## Architecture (one job per module)
```
../company        launcher: puts cli/ on sys.path, calls app.main()
app.py            arg dispatch + the `up` resource-manager gate. The only place
                  that knows the command grammar.
registry.py       load services.json; resolve(target)→keys; vram_of; serve_script; ceiling
systemd.py        port_open, verdict, control(start/stop/restart), journal — all systemctl/journald
gpu.py            THE RESOURCE MANAGER: read_gpu (nvidia-smi), running_gpu_services,
                  check_fit (budget decision), format_state (the "what's holding the card" block)
models.py         inventory (HF cache + ollama); swap (rewrite serve-script MODEL default)
bench.py          run a ~/vllm-tests bench via the vLLM venv
render.py         status() + health() views
README.md         use guide   ·   UPDATING.md   this file
```
Seam: everything that asks "what runs here" reads `services.json`; everything that
operates it goes through `systemd.py`. Keep that boundary — don't scatter `subprocess`
calls across modules.

## Add a service to the console
Edit `../services.json` — add one entry under `"services"`:
```json
"my-svc": {
  "group": "models",                 // core|brain|voice|models|reach
  "title": "Human-readable name",
  "port": 8009,                       // optional; used for live-state + health
  "manage": {"type": "user-unit", "unit": "my-svc.service"},  // or system-unit / manual(+"run")
  "health": "/v1/models",            // optional
  "serve": "~/vllm-tests/serve_x.sh",// optional; enables `swap` (script must use MODEL="${1:-...}")
  "vram_mb": 4000,                    // optional; GPU cost for the resource manager
  "autostart": false                 // true ONLY means "started by bare `company up`" (the surface)
}
```
New systemd unit? Put the canonical copy in `../systemd/`, then
`cp ../systemd/my-svc.service ~/.config/systemd/user/ && systemctl --user daemon-reload`.
**Do NOT `enable` it** — boot-autostart is off by design; control via `company up`.
Then `company status` to confirm it appears.

## Make `swap` work for a model service
Its `serve` script must set the model via `MODEL="${1:-default/id}"` and pass `"$MODEL"`
to `vllm serve`. `models.py` rewrites that one line. If a script sets the model another
way, `swap` refuses cleanly (script untouched) — normalize the script to the pattern.

## Add a command
In `app.py`, add a branch in `main()`, implement the logic in the module that owns the
concern (GPU→gpu.py, models→models.py, a new view→render.py), and document it in
`README.md`'s table + the `app.py` docstring (which IS `company help`). Keep `app.py`
thin — dispatch + the resource gate only.

## The resource manager (VRAM budget + scheduling + telemetry)
- **Budget.** Ceiling = `vram_ceiling_mb` in `services.json`; per-service cost = `vram_mb`
  (or `load.vram_mb` for voice). The decision is `gpu.check_fit` (measured nvidia-smi free
  vs `gpu.budget_vram` need), enforced in `app._act`.
- **Detect-running = `systemd.is_active` (per-unit), NOT port.** Model services share ports
  (chat-* :8000, embedders :8004); a port check marks every sibling "running" and bypasses
  the gate. `gpu._is_running` handles this (manual services fall back to their unique port).
- **Scheduling.** `--evict` (`gpu.plan_eviction`) stops running GPU holders, models→brain→
  voice / largest-first, only as many as needed, then starts. Default stays refuse.
- **Telemetry (BUILT).** `telemetry.py` records every `--wait` load (real load seconds +
  measured resident VRAM) to `telemetry.jsonl`. `gpu.budget_vram` then prefers the measured
  value over the registry estimate, so the gate self-corrects. `company telemetry` shows the
  rollup and flags estimates that are off.
- **Next growth:** auto-`--wait`-record on every model start; persist run-records to the
  introspective-data substrate (vault) for cross-session rollups; smarter scheduling (warm-pin,
  predict-load, evict-by-recency). Add as functions here + (eventually) a canvas view-mode —
  never a separate tool (constitution: one console, more types).

## Verify before claiming done
`company` is operational truth — test every command against the real machine, not by
reading the code. At minimum: `status`, `gpu`, `health`, `models`, a `swap` dry-check
(regex matches the serve script), `up`/`down` on a real service, and a deliberate
over-budget `up` to confirm it REFUSES. Fix forward; never leave it half-working.
