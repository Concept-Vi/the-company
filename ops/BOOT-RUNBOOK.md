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

# 3 — (optional) arm the scheduled jobs:
company up jobs                   # transcript exporter + sessions reindex timers

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
2. **Phone surface — needs a Tim decision.** `tailscale serve` currently proxies `/ → :8090` (gallery) and
   `:8443 → :5174` (review surface), both from the separate `counterpart` repo, which does NOT auto-start. So
   after reboot the phone URLs are DOWN until `counterpart/design/engine/serve.sh` is run (gated via
   `routines/launch-surfaces.py`). **Q for Tim:** is the phone path the counterpart surfaces (then add that
   serve.sh to the sequence) or the company canvas (then `tailscale serve` needs re-pointing to :5173)?
3. **No one-command fleet relaunch.** Bring-back is `claude` (lead) → lead re-spawns members; there is no
   "restore the whole prior fleet with context" command — it's per-member `--resume <id>`, ids looked up. Flag
   if continuity of specific prior members matters tonight.
4. **Minor cleanups (non-blocking):** `company-embed-pplx.service` `[Install]` is `WantedBy=default.target`
   (inconsistent with siblings — inert while disabled) · a dangling `openclaw-node.service` symlink in
   `default.target.wants/` · the interim transcript chroma index corrupted today
   (`~/.cache/company/substrate-claude-sessions/chroma.corrupt-backup-20260620`) — throwaway, the reindex job
   rebuilds it.

*Key files: `ops/cli/app.py` · `ops/services.json` · `ops/STARTUP.md` · `runtime/session_supervisor.py` ·
`channels/claude-fabric.sh` · `channels/channel.mcp.json` · `~/.bashrc:246` · `~/.config/systemd/user/`.*
