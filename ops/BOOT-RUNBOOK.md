# BOOT RUNBOOK — bring the Company back after a full WSL/computer restart

*Assembled 2026-06-20 by fork from an empirically-verified service-map (live `systemctl is-enabled` /
`loginctl` / `tailscale serve status` / actual file reads — NOT from docs; where docs disagreed with live
state, live state wins). Audience: the LEAD (to verify + relay the minimal commands to Tim) and any relaunched
session. Supersedes the stale `ops/WINDOWS-BOOT.md` (see Flag 1). Self-contained: the lead does not exist until
step 4.*

## THE ONE-LINE TRUTH
A reboot loses **zero files** — the git tree, `.data/store` (decisions · marks · events · refs · vectors ·
agent_sessions), the vaults, and `~/.claude` transcripts are all on disk and survive. It loses only **live
processes, VRAM-resident models, and live agent sessions.** By design (Tim 2026-06-06) **almost nothing
Company auto-starts on boot** — Tim brings it back with `company up` (+ a model loadout) and then types `claude`
to launch the lead, from which the fleet is re-spawned. The `mcp__company__*` tools work the instant any
`claude` session starts (they read `.data/store` directly — no running service required).

---

## ★ THE MINIMAL SEQUENCE — what Tim types post-reboot
*(Already up automatically, no action: `ollama` + `tailscaled` [system units] and `memory-guard` [watches
`~/.claude`]. Nothing else Company-side self-starts.)*

```bash
# 1 — the interactive surface (canvas + bridge); also activates the 4 staged commits (they run from the
#     working tree, so a fresh start picks up current disk state automatically):
company up                        # canvas :5173 + bridge :8770   (the only autostart-flagged pair)
company up session-supervisor     # :8771 — needed only if the managed clone-fleet will be used

# 2 — the GPU loadout for the cross-session fabric + a local brain + MEANING-RECALL (the embedders):
company up @xsession-brain        # embed-pplx :8007 + rerank-jina :8008 + chat-4b :8000 + stt-whisper
#   → this is what restores the embed engine (the precondition for the concurrent theorem-mine).
#   alternatives: @wake (phone-PWA brain/ear/voice) · @xsession (fabric+voice, no 4b)

# 2c — ★ THE COGNITION CHAT PATH (concurrent models via the MCP — run_role/run_items/cascades on local+cloud).
#      ADDED 2026-06-20 after a live gap: post-reboot the chat path was DEAD (local chat models not resident +
#      litellm :4100 not started) so the company couldn't run ANY concurrent model. What makes it work:
#      • ollama :11434 AUTO-STARTS at boot (system unit) + serves cloud (':cloud') + ollama-local (':tag') models
#        = the ZERO-VRAM concurrent path. The run_role routing fix (c1e00ba) sends ollama/cloud models there.
#      • ★ the routing fix goes LIVE only after the company MCP SERVER reloads (it caches the old code) — a fresh
#        `claude` session (step 4) reloads it. So: do step 4 to pick up the fix before relying on concurrent models.
#      • OPTIONAL proxy: litellm :4100 — `bash fabric/serve_litellm.sh` (zero-VRAM, the "intended" endpoint; NOT
#        required, ollama-direct works). Consider adding to company-up if the proxy path is preferred.
#      • DEFAULT-model cognition (run_items/cascades with NO model override) uses the local 4b (:8000) → needs
#        step 2 (@xsession-brain loads it) OR a cognition-default-to-cloud change (OPEN — lead/Tim design call).
#      ⟹ concurrent CLOUD models at boot need only: ollama (auto) + a fresh MCP. Default-model cognition also
#        needs the 4b (step 2). This is the "so it doesn't happen again" startup requirement.
#      ★ SECOND-LAYER GAP (found 2026-06-20 verifying the fix; routing now reaches the model — refused→reaches):
#        cloud models return EMPTY content to the role engine's STRUCTURED-OUTPUT request — reasoning models
#        (deepseek-flash) answer only in the reasoning trace; instruct models (kimi) returned empty. So clean
#        structured EXTRACTION (run_role with an output-schema) does NOT yet work on cloud. RELIABLE concurrent
#        extraction therefore needs the LOCAL no-think/json models (chat-2b/4b — a GPU load, step 2) OR a fix to
#        the cloud structured-output handling (the role engine's JSON/response_format request vs ollama-cloud).
#        OPEN — flagged to lead; the routing gap itself is FIXED + verified.

# 3 — (optional) arm the scheduled jobs:
company up jobs                   # transcript exporter + sessions reindex timers

# 3b — TIM'S PHONE SURFACES (the tailscale phone path — NOT company units, do NOT auto-start; see Flag 2).
#      tailscale serve persists across reboot (/ → :8090 gallery, :8443 → :5174 operator surface), so once
#      both servers are up the phone URLs work. Both are needed for the live keystone verify + Tim's phone.
/home/tim/repos/counterpart/design/engine/serve.sh &     # gallery  :8090 (counterpart server/server.py)
( cd /home/tim/company/surface/app && npm run dev & )     # operator surface :5174 (company surface/app vite; predev re-syncs DNA's gallery)

# 4 — launch the LEAD (the `claude` alias auto-attaches the fabric channel):
cd /home/tim/company && claude

# 5 — FROM INSIDE THE LEAD (the lead's job, not Tim's): re-spawn fleet members as needed —
#     company session new --resume <prior-id>     (rehydrate a member WITH its prior context)
#     or the sessions(op='wake'/'consult') MCP tool.

# verify:
company status                    # every service + live state + VRAM budget (16 GB ceiling)
company health                    # port pings
```

**Genuinely minimal:** if Tim only needs the agents (not the web/phone surface or GPU models), **step 4 alone
(`claude`) gives a working lead with full `mcp__company` tools off disk.** Steps 1–3 add the surface, the GPU
models/recall, and the managed fleet.

---

## THE `company` CLI (the one control surface)
`ops/company` shim → `ops/cli/app.py` (dispatcher), on PATH as `~/.local/bin/company`. Reads the
self-describing registry `ops/services.json` and drives `systemctl --user`. Bare `company up` starts only
`autostart:true` services (canvas + bridge). Targets: a service key · a group (`core|brain|voice|models|reach|
jobs`) · an `@combo` · `all`. Other verbs: `down` · `restart` · `logs SVC [-f]` · `gpu` · `health` ·
`up TARGET --evict` (make GPU room; default REFUSES an over-budget start) · `session [list|new|send|stop|fleet]`.

## SERVICES (verified) — name · port · unit/starter · group
- **canvas** :5173 · `company-canvas.service` (vite) · core · *autostart*
- **bridge** :8770 · `company-bridge.service` (`runtime/bridge.py 8770`) · core · *autostart* (drop-in sets
  `COMPANY_WIRE_PERMISSION=acceptEdits`)
- **session-supervisor** :8771 · `company-session-supervisor.service` · core
- chat-4b :8000 · `vllm-chat.service` · brain  ·  embed-pplx :8007 · `company-embed-pplx.service` · models  ·
  rerank-jina :8008 · manual `ops/serve_rerank.sh` (no unit) · models
- voice: tts-kokoro :4123 · stt-whisper :2022 (`voicemode-whisper.service`) · stt-parakeet/canary/granite
  :2031-33 · tts-chatterbox/orpheus/cosyvoice/xtts/qwen3tts :4124-28
- **ollama** :11434 · `ollama.service` (SYSTEM) · **auto-on-boot** · tailscale · `tailscaled.service` (SYSTEM) ·
  **auto-on-boot**
- gallery :8090 + review-surface :5174 — served by the **separate `counterpart` repo**
  (`/home/tim/repos/counterpart/design/engine/serve.sh`), NOT a company unit, NOT auto-start (see Flag 2).

## WHAT AUTO-RESTORES ON BOOT (verified live) — almost nothing
- `ollama.service`, `tailscaled.service` (system units, enabled).
- `memory-guard.service` (user, lingering) — git-autocommits `~/.claude` memory.
- **Everything else is disabled.** `company.target` is disabled AND absent from `default.target.wants/`, so
  linger pulls up nothing Company-side. The job timers are enabled but `WantedBy=company.target` only → inactive
  until `company up jobs`.

## THE FABRIC RELAUNCH (the actual mechanism)
Live agent sessions all die on reboot and do NOT auto-relaunch. Two paths:
1. **The lead / any interactive member — Tim types `claude`.** `~/.bashrc:246` aliases it to
   `channels/claude-fabric.sh`, which execs the real binary with `--mcp-config channels/channel.mcp.json
   --dangerously-load-development-channels server:company-channel`. On load the session self-registers to
   `.data/channels/` and calls `announce`. The `company` MCP is registered globally in `~/.claude.json`
   (→ `mcp_face/server.py`), so `mcp__company__*` is available to every `claude` session automatically.
2. **The managed clone fleet — spawned BY the lead, never auto** (the "lead-only spawn" law). The
   session-supervisor (:8771) is the single subprocess launcher but restores no roster on its own; the lead
   spawns via `company session new --resume <id>` or `sessions(op='wake'/'consult')`. Company-model spawns use
   the ollama launcher (Tim 2026-06-16).
   **Resume rehydrates context:** transcripts at `~/.claude/projects/<encoded-cwd>/<id>.jsonl` survive; `--resume
   <id>` keeps the id + context, `--fork` copies to a new id, no flag = fresh. Prior members CAN return with
   full context IF their ids are looked up (in `.data/channels/*.json` + supervisor events).

## PERSISTS vs LOST
- **Persists (on disk):** git tree (incl. the large uncommitted set — `main` is ahead 1339 of origin; services
  run from the working tree, so the staged commits activate on restart automatically) · `.data/store` (all
  decisions/marks/events/vectors — git-ignored, disk-only) · `.data/channels` · `~/.claude` transcripts · vaults
  · model caches. **No critical in-memory-only state found** (the store is filesystem-backed, append-only).
- **Lost (re-create):** live processes (→ `company up`) · VRAM models (→ the loadout) · live agent sessions +
  in-RAM context (→ `claude` + optional `--resume`) · armed job timers (→ `company up jobs`).

---

## ★ FLAGS / DECISIONS FOR TIM (carried by the lead)
1. **Stale doc:** `ops/WINDOWS-BOOT.md` claims linger auto-pulls the whole stack on boot — FALSE per live state
   (`company.target` disabled + not wanted). `ops/STARTUP.md` is correct. (Cleanup: fix/retire WINDOWS-BOOT.md.)
2. **Phone surface — RESOLVED (2026-06-20, verified by live tailscale mapping).** The phone path IS the
   review surfaces, now in the boot sequence (step 3b): `tailscale serve` (persists across reboot) maps
   `/ → :8090` (the DNA **gallery**, counterpart `server/server.py`, started by `counterpart/design/engine/serve.sh`)
   and `:8443 → :5174` (the **operator surface**, which is the COMPANY repo's `surface/app` vite — NOT
   counterpart; corrects the earlier note). Neither auto-starts, so step 3b brings both up. `routines/launch-surfaces.py`
   is a STATUS-reporter (gated), not an auto-launcher. (Future cleanup: wrap step 3b as `company up surfaces`
   so it's one verb like the rest.)
3. **No one-command fleet relaunch.** Bring-back is `claude` (lead) → lead re-spawns members; there is no
   "restore the whole prior fleet with context" command — it's per-member `--resume <id>`, ids looked up. Flag
   if continuity of specific prior members matters tonight.
4. **Minor cleanups (non-blocking):** `company-embed-pplx.service` `[Install]` is `WantedBy=default.target`
   (inconsistent with siblings — inert while disabled) · a dangling `openclaw-node.service` symlink in
   `default.target.wants/` · the interim transcript chroma index was corrupted
   **+ REBUILT CLEAN today** (35,904 vectors, verified by use — recollection; old corrupt copy →
   `~/.cache/company/substrate-claude-sessions/chroma.corrupt-backup-20260620`). It SURVIVES the reboot on disk →
   recall returns the moment embed-pplx binds (`company up @xsession-brain`), **NO reindex needed** (don't run the
   hours-long reindex — the index is healthy). The real post-reboot recall risk is the embedder LOAD-HANG flap
   (GAP fbfc1d2): a fresh boot should clear the wedge; the recall watchdog is the durable fix.

*Key files: `ops/cli/app.py` · `ops/services.json` · `ops/STARTUP.md` · `runtime/session_supervisor.py` ·
`channels/claude-fabric.sh` · `channels/channel.mcp.json` · `~/.bashrc:246` · `~/.config/systemd/user/`.*
