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

**This is the FIRST command center — there will be more (open-future).**
The service command center is the **first instance of a recurring pattern**, not a finished thing. The pattern: *a self-describing registry + a plain console over a reliable substrate, that lets the operator (or the AI) **see and run** one domain of the system.* Other command centers are expected as the Company grows — e.g. **model/VRAM resource control** (which model is live, swap what's in VRAM — the operable face of "it's all resource management"), **the RHM/modes**, **data/memory**, **jobs/cron**. Each is one domain's see-and-operate surface; over time they surface on the canvas (the commander's bridge). Treat this folder as the seed of that layer, written to grow — never as the whole of it.

**Where new things go / how to extend.**
- **Add a service to the command center** → edit `ops/services.json`: add an entry `{ "key": { group, title, port?, manage: {type: "user-unit"|"system-unit"|"manual", unit?}, health?, autostart? } }`. If it needs a *new* systemd unit, add the unit to `ops/systemd/`, then install it (`cp ops/systemd/<x> ~/.config/systemd/user/ && systemctl --user daemon-reload && systemctl --user enable <x>`); to pull it into the core boot set, `WantedBy=company.target` (new units) or `systemctl --user add-wants company.target <unit>` (existing). Then `company status` to confirm it appears. System services (sudo to control) are status-only from the console.
- **Add a *new* command center** → follow the pattern above: a self-describing registry (JSON here or in the owning module) + a plain console that reads the registry and drives the real substrate + the substrate's reliability underneath. Document it in this constitution, add a row to the root `AGENTS.md` "Where things go" table and the `MAP.md` module map, and (eventually) give it a panel on the canvas. One domain per command center; same shape every time so an AI recognises it instantly.

**Its seam.** The console reads `services.json` and shells out to `systemctl`/`journalctl`/socket-checks — it owns no state of its own; the registry + systemd are the truth. Anything wanting to know "what runs here" reads `services.json`; anything wanting to operate it calls `company` (or systemd directly).

**What would violate it.** A service started in a way the registry doesn't know about (invisible scatter — the exact anti-pattern this replaces). A console that hides failures or drift. Hand-maintained duplicate truth (two places that both claim what runs). A "command center" that only an informed human could operate — it must be plain enough for a fresh AI session.

## Files
- `company` — the console (Python, stdlib-only; `company help`).
- `services.json` — the registry (the source of truth).
- `STARTUP.md` — the command table + boot behaviour + open items.
- `systemd/` — canonical unit + target files (the muscle).
