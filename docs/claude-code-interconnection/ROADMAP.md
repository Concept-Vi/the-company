# Roadmap — Claude Code Extended Interconnection

## ✅ Built + proven by use (2026-06-14)
- **Channel injection** into a live interactive session (the hallmark).
- **cc_channels** core: registry, presence (auto-prune dead), find, send, reply-routing, threads, mail.
- **Reply loop** — a reply pushes back into the asker's conversation, no polling.
- **Group broadcast** + reply aggregation under one thread.
- **MCP surface** `cc_channel` (list/send/broadcast/mail) + per-session `announce`/`reply`.
- **`@xsession` loadout** — embed-pplx (2560-dim, verified) + tts-qwen3tts (real 24kHz WAV, verified)
  + whisper STT, ~12.6G/16G.
- **Two-session live collaboration** — a lead + a time-travelled fork of it coordinated over the
  channel to divide and build.

## ✅ Built + proven by use (2026-07-09) — the presence-aware UNIFICATION (branch messaging-unification / PR #2)
The two channel worlds are welded into ONE presence-aware delivery layer. "It shouldn't matter if the
supervisor owns them" — a durable channel post now LIVE-injects a hand-started (unsupervised-live)
member via its own .mjs port, not just supervisor-owned ones.
- **`runtime/identity.py`** — the ONE resolver + read-time presence view. Unifies the three identity
  spaces (ephemeral handle · durable session UUID · substrate agent id) by PROBE, derives the F1.2
  state (supervised-live | unsupervised-live | closed) at read time (no `agent_sessions.*` emit —
  single-writer-safe), and recovers a live handle's durable UUID (reg → transcript_path → /proc
  environ → self-marker → fd). `resolve(target)` accepts uuid | ch-handle | as-id | agent-id | cwd |
  session://X and fails loud on ambiguity; `session://<handle>` now RESOLVES instead of raising.
- **`runtime/router.py`** — the ladder: best LIVE transport (supervisor /inject OR .mjs port push) →
  durable mailbox queue → loud-unreachable. Returns a TRUTHFUL receipt {delivered, queued, transport,
  verb, reason}; never a phantom-OK (inspects push().ok), never a silent drop.
- **`session_channels.post_to_channel`** — routes each member by presence: supervised-live keeps its
  deliver-intent; a port-live member is live-pushed here-and-now; the rest queue. The fan names the
  true transport + delivered per member.
- **`mcp_face/tools/send.py`** — the ONE front door: `send(to, message)` for a session or a channel
  (by name or id). `cc_channel`/`channel_act`/`session_post` keep working (they route through the same
  welded functions).
- **Phantom-OK removed** at `route_reply` and the .mjs `reply`/`announce`/`profile` — they report the
  truth (delivered vs recorded-not-confirmed, persisted vs in-memory).
Tests: `tests/messaging_weld_acceptance.py`, `tests/messaging_send_acceptance.py`.
STILL OPEN: reliable UUID capture for non-`~/company` cwds (a durable post reaches a .mjs session only
if its UUID is recoverable) · fold `channel_boundary` shared-publish into the fan · migrate the
`_channels/*.json` named channels · complete `/channel-send` as the router's HTTP door · the
operator-launched live inject+churn verification.

## 🔧 In progress
- **Clone → channel** (the fork's lane): combine `session_pointintime.materialize_at_point` (R3.4,
  proven) with an interactive channel launch so a session cloned *at a point in time* auto-registers
  into the fabric — immediately DM-able and group-joinable. Open seam: the clone must launch
  **interactive** (channels don't fire under `-p`) — likely a held interactive (pty) launch or an
  operator-attach. Passing the materialized `new_sid` as `COMPANY_SESSION_ID` also closes the
  identity gap (clones show their real session_id in `cc_channel op=list`).
- **Role skills** (the fork's lane): skills for the distinct roles/parts of the system.

## ⏭ Next (designed, not built)
- **Capture each session's claude `session_id` at registration** — join the ~1,098-session catalog
  (dossiers, history, recognise-the-fleet). Today live sessions show a handle + cwd + description but
  empty session_id unless launched with `COMPANY_SESSION_ID`.
- **Auto-join via a SessionStart hook** — so a session joins the fabric without the manual launch
  flag. Tim chose "global" (every session). BLOCKED: editing `~/.claude.json` was auto-denied as a
  self-modification; needs Tim's explicit ok, or use a per-project `.claude/settings.json` hook, or
  keep the per-launch flag.
- **Wire group → the real fabric `channels`/`channel_act`** (named persistent groups + gatherings),
  so broadcast targets a named channel, not an ad-hoc handle list.
- **Voice (partially built):** ✅ the engine rides in `@xsession` (tts-qwen3tts) and ✅ `cc_voice`
  (op=engines|speak) wires the fabric to it — any text → a WAV via the resident engine (verified).
  NEXT: the streaming `text_delta` tap on the supervisor `_reader` so a session's reply *speaks as it
  generates* (low-latency), routed to the sentence-streamed voice circuit, distinct voice per session
  (supervisor already passes `--include-partial-messages` but discards the deltas — that's the seam;
  see `build-prep/Voiced Conversation — Path Investigation.md`). Playback is device-side.
- **Reply aggregation surfaced in the UI / RHM** — the fleet view, the room-of-voices.
- **Sender gating** (allowlist) before any non-local sender path.
- **Semantic session-find** — use embed-pplx over the transcript index so "who knows about X / find
  the session about Y" returns the right session to message or clone (the index build is the throwaway
  transcript-search system; the embedder is now resident in `@xsession`).

## Design laws (Tim, locked 2026-06-14)
- Identity = working directory + a self-announced description.
- Replies route THROUGH the mailbox AND are pushed into the right session (recipient never polls).
- Group = the fabric `channels` concept (members = live sessions).
- The GPU loadout is a registry concern (`@xsession`); swap engines via the registry, not by hand.

## ✅ Built + proven by use (2026-07-13) — the TOOL-SURFACE REDESIGN v2 (branch fabric-surface-redesign)
The ~30 hazard-grown doors reshaped into intent-named doors over the UNCHANGED runtime (invariant: no
runtime signature or supervisor route changed — ~60 programmatic callers untouched; old tools keep
working, no flag-day). Per design v2 (board://item-de33cdf8), corrected by a 6-lens adversarial review:
- **Phase 0 defects fixed**: the session-uuid CAPTURE one-liner (the .mjs now reads CLAUDE_CODE_SESSION_ID
  — the root cause of 85% empty session_id / dead durable-id reachability) · cc_retire un-broken (2/3 ops
  crashed on moved functions) · transport "mail" real (PULL-only, fail-loud push, router queues — no more
  phantom-live members) · cc_gate transitions emit fabric events + the /interrupt result recorded ·
  the router is RECORD-AND-DELIVER (live delivery also writes the durable backstop record — history
  never silently lost) · the address grammar unified (channel:// agent:// operator:// registered; one
  scheme list, identity.py's private copy collapsed).
- **New doors**: `directory` (one faceted who/what-exists: registry+live+CLONES joined — the hidden
  fleet visible; rooms their own shape) · `mailbox` (the fabric inbox: durable mail + churn-spanning
  channel mail + fail-soft federated allocations; distinct from operator inbox()/decisions()) ·
  `principal`/`principal_act` (one identity read: resolve/roster/whoami; describe write; register
  TEACHES the substrate path — access stays its own fail-closed door) · `board`/`board_act` (CQRS split
  + the since-cursor) · `send` grew the GROUP fan (ad-hoc broadcast, per-target receipts, one thread) ·
  `channel_act` grew `retire` + the archive coverage GATE (archiving un-harvested members refuses,
  teaching; force=True explicit).
- **Config**: the 3 bare supervisor-address literals now honor COMPANY_SUPERVISOR_BASE.
- Exposure postures preserved/declared per door (safe reads tagged; writes operator-tier; the board
  split deliberately does NOT widen the public boundary).
Tests: fabric_reads · fabric_principal · fabric_channel_lifecycle · fabric_board_cqrs (+ grown
messaging_send) — 12-suite sweep green. STILL OPEN: the remote-safe-subset acceptance test over
remote.py's gate itself · the agent_register cross-repo fold (needs the session↔role join designed) ·
live operator verification of gate-pause/interrupt.
