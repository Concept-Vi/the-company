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
models.py         inventory (HF cache + ollama); swap (config.model or legacy script)
bench.py          run a ~/vllm-tests bench via the vLLM venv
render.py         status() + health() views
serveconfig.py    emits vLLM args from a service's `config` block
../serve_model.sh the ONE registry-driven vLLM launcher: `serve_model.sh <service-key>`
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

> **Canonicalization (2026-06-06):** every *installed* user-unit is now copied into
> `ops/systemd/` (company-*, vllm-chat/2b/08b/embed/jina-v4/jina-v5/nemotron/qwen3emb,
> voicemode-whisper, github-runner, llama-swap, litellm-proxy, openclaw-gateway). When you
> add or change a unit, keep its `ops/systemd/` copy in sync (the repo must be able to rebuild
> the machine — self-hosting principle). See STARTUP.md → "Rebuild from the repo".
> **Still outside the repo (deeper coupling, flagged):** (1) the 5 voice trial engines
> (`company-voice-*`) have NO unit installed yet — install one, then add its unit here;
> (2) legacy script-based model services still source `~/vllm-tests/serve_*.sh` (not in repo)
> — migrating them to a `config` block + `serve_model.sh` makes them fully repo-described.

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

## Config-driven models (the generic launcher)
A model service can carry a `config` block instead of a `serve` script string:
```json
"config": {
  "model": "Qwen/Qwen3.5-0.8B", "port": 8006, "gpu_util": 0.30,
  "max_model_len": 4096, "max_num_seqs": 32,
  "flags": ["--enable-prefix-caching", "--tool-call-parser", "qwen3_xml", "--trust-remote-code"],
  "env": {"VLLM_USE_FLASHINFER_SAMPLER": "0"}
}
```
`env` (optional) is per-service env vars — `serve_model.sh` exports them before `vllm serve`
(faithful to what each old serve script set; each script's env differed, so it's per-service,
not hardcoded in the launcher). `serveconfig.py <key> --env` emits them; `serveconfig.py <key>`
emits the args. **All vLLM models are migrated to this** (2026-06-06); the old `serve_*.sh` in
`~/vllm-tests` are superseded (kept as reference, not the launch path).
**Exception — `embed-jina-v4`:** NOT config-driven. vLLM lacks jina-v4 support, so it runs a
custom FastAPI server (`serve_jina_v4.py`, raw transformers) in the `jina-v4-env` venv via
`serve_jina_v4.sh`. It keeps a `serve` string and is the one legitimately script-based model.
Voice services are similar (custom python servers) but carry a `load` block and are managed by
`voice/lifecycle.py` — a different launch path; do not force either onto `serve_model.sh`.
Its unit's ExecStart is just `~/company/ops/serve_model.sh <service-key>`. That launcher
asks `serveconfig.py` to turn the config block into vLLM args and execs `vllm serve`. So:
- **Tuning is data:** `company config <svc> <key> <value>` edits the block + saves; `company
  restart <svc>` applies it. No script editing. `swap` sets `config.model`.
- **The budget reads `gpu_util`:** `budget_vram` returns `gpu_util × ceiling` (the slice vLLM
  reserves) — authoritative, immune to stale telemetry. Lower `gpu_util` → more co-residency.
- **Floor gotcha:** `gpu_util` must hold weights + activations + KV cache. Too low → vLLM
  `ValueError: No available memory for the cache blocks`. (0.20 starved the 0.8B; 0.30 works.)
- **Migrate a legacy script service:** give it a `config` block, point its unit at
  `serve_model.sh <key>`, `daemon-reload`. Goal state: all models config-driven, scripts gone.
- **Add a NEW value field?** add it to the block and teach `serveconfig.py` to emit its flag.

## Combos (run-together sets)
`combos` in `services.json` maps a name → `{services: [...], note}`. `company up @<name>`
resolves to those services and goes through the normal resource gate (so a combo that
doesn't fit is refused/evictable like any start). Add a combo = one entry. Keep combos that
are meant to co-reside within the 16 GB budget (sum their `gpu_util × ceiling`).

**Variants (a base loadout + trial configurations).** Instead of `services`, a combo may declare
`{"extends": "<base-combo>", "swap": {"old-svc": "new-svc"}, "add": [...], "remove": [...], "note": …}`.
It inherits the base's resolved service list and applies the overrides. `registry.combos()` resolves
it for both `company combos` and `up @<variant>`, and fails loud on a missing base, a `swap` source not
in the base, an unknown service, or an `extends` cycle. Use this to trial one slot (e.g. the ear) across
configurations of the same loadout — shipped: `interaction` (base) + `interaction-parakeet` (swaps the ear).

## Verify before claiming done
`company` is operational truth — test every command against the real machine, not by
reading the code. At minimum: `status`, `gpu`, `health`, `models`, a `swap` dry-check
(regex matches the serve script), `up`/`down` on a real service, and a deliberate
over-budget `up` to confirm it REFUSES. Fix forward; never leave it half-working.
