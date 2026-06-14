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
