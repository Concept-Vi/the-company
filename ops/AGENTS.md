---
type: constitution
module: ops
aliases: ["ops — constitution"]
tags: [company, constitution, ops, command-center]
governs: []
relates-to: ["[[Company Map]]", "[[runtime — constitution]]"]
status: living
---

# ops/ — AGENTS.md (constitution)

**What it is.** The Company's **operational control** — how the *running system* is seen and operated. Because there are no human developers and no human reads or writes these files, the operating layer must be **one self-describing place an AI can read cold and run**, not config scattered across `~/.config`, ad-hoc `start.sh` scripts, and tribal memory. This folder is that place.

**What it guarantees.**
- **One console to see + operate the runtime.** `ops/company` (symlinked onto `PATH` as `company`) shows every service grouped, its live state (▶ running · ◐ active-no-port-yet · ✖ failed · · stopped), and **drift** (e.g. "RUNNING (unmanaged)" when something is up by hand instead of under its unit). It starts/stops/restarts any service, group, or `all`. See `STARTUP.md` for the command table.
- **One self-describing registry of truth.** `ops/services.json` declares every service (group · title · port · how-managed · health · autostart). The AI reads this to know the whole machine. **Adding a service = adding one entry here.**
- **systemd is the muscle; this is the map + the console.** Reliable execution, `Restart=on-failure`, and start-at-boot (user **linger** is on) live in systemd units (`ops/systemd/` holds the canonical copies). The console *drives* systemd; it never replaces it. The substrate must always be able to bring the console's own services up — including the bridge/canvas the console reports on.
- **Honest over complete.** It declares everything reasonably knowable, accepting some entries (dormant model ports/units) may be imperfect — *visible-and-operable-but-slightly-wrong beats invisible scatter.* A wrong detail is a one-line fix in the registry, never a hunt.
- **Fail loud / no hiding.** Status shows reality (incl. drift and failures), never a flattering fiction. Control actions report ✓/✗ with the error.

**This is the FIRST *instantiation* of one general console — more TYPES, not more tools (open-future).**
Do **not** build duplicate command centers. The right shape (Tim, "one substrate, per-type view-modes" — D3) is **one** console/registry mechanism **instantiated per type**: services are one type-view; **models/VRAM** (which model is live, swap what's in VRAM — the operable face of "it's all resource management"), **cognitive-layers**, **the RHM/modes**, **data/memory**, **jobs/cron** are *other view-modes of the same mechanism*, not separate apps. The service console is the first type this general thing renders; over time the type-views surface together on the canvas (the commander's bridge). Treat this folder as the seed of one generalising console, never as one of many parallel tools.

**Where new things go / how to extend.**
- **Add a service to the command center** → edit `ops/services.json`: add an entry `{ "key": { group, title, port?, manage: {type: "user-unit"|"system-unit"|"manual", unit?}, health?, autostart? } }`. If it needs a *new* systemd unit, add the unit to `ops/systemd/`, then install it (`cp ops/systemd/<x> ~/.config/systemd/user/ && systemctl --user daemon-reload && systemctl --user enable <x>`); to pull it into the core boot set, `WantedBy=company.target` (new units) or `systemctl --user add-wants company.target <unit>` (existing). Then `company status` to confirm it appears. System services (sudo to control) are status-only from the console.
- **Add a new TYPE-view to the console** (NOT a new tool) → generalize the registry + console over the new type (its entries declare their own kind), reusing the same see/operate mechanism over the real substrate. Document it here; (eventually) it becomes another view-mode on the canvas. Same mechanism, more types — never a parallel command center.

**Its seam.** The console reads `services.json` and shells out to `systemctl`/`journalctl`/socket-checks — it owns no state of its own; the registry + systemd are the truth. Anything wanting to know "what runs here" reads `services.json`; anything wanting to operate it calls `company` (or systemd directly).

**What would violate it.** A service started in a way the registry doesn't know about (invisible scatter — the exact anti-pattern this replaces). A console that hides failures or drift. Hand-maintained duplicate truth (two places that both claim what runs). A "command center" that only an informed human could operate — it must be plain enough for a fresh AI session.

## Status of the type-views (open-future, growing)
- **services** — the first type-view (live since 2026-06-04).
- **models/VRAM (the resource manager)** — instantiated 2026-06-06 as the SAME console's
  GPU view: `company gpu`/`models`/`swap`, VRAM cost in `status`, and a hard budget gate on
  `company up` (refuses an over-capacity start, always shows what's holding the card; `--force`
  overrides). Lives in `cli/gpu.py`, not a separate tool. Next growth = telemetry → scheduling
  (see `cli/UPDATING.md`). [[project-native-model-layer]]
  - **Config-block sizing is the ONE source (2026-06-07).** A GPU service's `config.gpu_util` ×
    `vram_ceiling_mb` IS its budget (`gpu.budget_vram`) AND what it launches with. Voice engines that
    aren't `serve_model.sh`-launched (e.g. `tts-orpheus` — own unit + `orpheus.py`) now carry a `config`
    block too; `orpheus.py` reads `config.gpu_util/max_model_len/model` (env is fallback) so the fit-gate
    and the launch never drift. **Size by measurement, never arbitrarily** (Tim): a model carries a
    measured `config._profile` `{fixed_mb, kv_kb_per_token}`, so `/api/model/config` auto-sizes `gpu_util`
    from a new `max_model_len` (and `max_model_len_ceiling` records the model's real capacity, reachable solo).
  - **The fit-surface (`gpu.fit_report` → `/api/fit`).** "Tell me if my selection won't fit" (Tim):
    given selected GPU service keys (brain + voice), returns each budget, the sum vs the card ceiling,
    measured free, and fit/no-fit + what to unload — config-derived, so it tracks a resize. The settings
    window renders it as a bar. Measured on the 16GB card: the 4b (hybrid, KV ~31.7KB/tok) does 256K
    **solo** and co-resides with light voices at 64K, but **Orpheus (~8.5GB) + 64K brain is over by
    ~0.6GB** — a switch-on-demand pair (the gate refuses, never OOMs).
- **model-TYPE capabilities (the capability registry — `cli/capabilities.py`, G8/C8.1–C8.4, 2026-06-08).**
  The THIRD keying (B4): intrinsic capability **by model-id** (tool-calling · json_schema · thinking ·
  context-ceiling · concurrency-knee · speed), each with explicit provenance `declared|probed|measured|served`
  (live/served wins). It owns ONLY model-intrinsic facts — it NEVER stores gpu_util/vram (rule 3); for those
  it **JOINs to `gpu.py`** (`service_key_for(model_id)` matches `config.model`, then `budget_vram`/residency —
  REUSED, never duplicated). Queries: `capabilities_for(model_id)` (the row + the JOIN), `role_can_bind(requires,
  model_id)` / `suitable_models(requires)` (the `requires ⊆ provides` binding query — the `provides` TAG set
  matches `suite.py`'s `capability_providers()` exactly: chat·json·tools·fast·no-think), `placement_for(track)` +
  `swarm_survives_cloud_brain()` (C8.3 cloud-decoupling policy as DATA), `is_resident`/`require_resident` (C8.4
  fail-loud, loud `OFFER_LOAD` on a miss, NEVER auto-loads). **Self-description / DRIFT HOME (C9.4):** this section
  + the `cli/capabilities.py` module docstring are the registry's self-description home; the drift assertion is
  `tests/model_capabilities_acceptance.py`. It COMPLEMENTS `suite.py`'s `MODEL_KNOBS` (per-request knobs, also by
  model-id) — knobs = "dials a request turns"; capabilities = "what the model can do." The DOWNSTREAM consumer is
  `suite.py:capability_providers()` (C2.5), which the lead wires to read this catalog (the one suite-side wire).
- **cognitive-layers · RHM/modes · data/memory · jobs/cron** — not yet instantiated; same mechanism when they are.

## Files
- `company` — launcher (stdlib-only; runs the `cli/` package; `company help`).
- `cli/` — the console package, one job per module:
  - `app.py` (dispatch + the `up` resource gate) · `registry.py` (reads services.json) ·
    `systemd.py` (start/stop/status/logs) · `gpu.py` (**the resource manager**) ·
    `models.py` (inventory + swap) · `capabilities.py` (**the model-TYPE capability registry**, by model-id; JOINs to gpu.py) · `bench.py` · `render.py` (status/health views).
  - `README.md` — use guide.   `UPDATING.md` — how to extend the CLI + the registry schema.
- `services.json` — the registry (the source of truth; now also carries `vram_mb`, `serve`, `vram_ceiling_mb`).
- `STARTUP.md` — the command table + boot behaviour + open items.
- `systemd/` — canonical unit + target files (the muscle).
