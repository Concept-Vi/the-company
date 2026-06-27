# OpenWebUI ↔ Fabric — Staged Build Plan (B)

**Status:** plan, post-research, post-smoke-test. The platform question is closed (OpenWebUI, no fork) and the
one empirical gate is verified by-use on running **0.9.6** (the channels webhook). Grounded in
`01..08` + `04b` research reports in this dir. **Delivered to Tim distilled through the OpenWebUI channel
(fabric-test) per his direction; this is the agent-register build doc.**

## What's already real (verified, not planned)
- **Foundation — DONE.** OpenWebUI **0.9.6** running (`:8081`), served to the phone via Tailscale
  (`https://workstation001.tail777bc2.ts.net:8444`, tailnet-private HTTPS, PWA). Confirmed by Tim on-device.
- **The push primitive — VERIFIED by-use.** `POST /api/v1/channels/{id}/webhooks/create` (admin) → a per-member
  webhook with identity; `POST /api/v1/channels/webhooks/{id}/{token}` (auth-free, token-only) inserts a message
  that renders live over socket.io with that identity (`meta.webhook`). Smoke-test 200 + message landed + Tim saw it.
- **The brain — EXISTS, half-built.** `brain_router` is a source-router; the `fleet` source already reads the
  supervisor roster/sessions/channel-traffic and proposes (read+propose floor; spawn/inject stay lead-only).
  "Chat with the supervisor" ≡ "ask the RHM a fleet question" is the designed architecture (`SUPERVISOR-AS-BRAIN.md`).

## The architecture Tim specified
Members are **all AI**, message **each other** (the existing fabric mesh); **multiple channels, multiple members
each**; members **self-register**, and **registration is what creates the webhook**. OpenWebUI is the human window
onto that mesh — Tim watches and steps in.

## Stages (all additive; none a fork)

### Stage 1 — THE ROOM (fabric → OpenWebUI, the mesh made visible)
- Map each fabric (session_channels) channel ↔ an OpenWebUI channel (ensure-exists on first use).
- **Member self-registration → webhook creation:** when a fabric member joins a channel, the fabric (holding an
  OWUI admin token) calls `…/webhooks/create` with the member's name+avatar → stores the returned `{webhook_id,
  token}` on the member's channel registration. (N members → N webhooks; identity fixed at creation, per r9.)
- **Forward the mesh:** every fabric channel post (member→member) is mirrored into the OWUI channel via that
  member's webhook (token-post). Implement as the `transport:"webhook"` branch in `cc_channels`/the channel
  router (07-report P2 — additive to the pluggable transport field, NOT a rewrite).
- **Result:** Tim watches the whole AI↔AI conversation live on his phone, each member as itself.

### Stage 2 — THE CONCIERGE (Tim ↔ the RHM, "chat with the supervisor")
- Build the **thin OpenAI-protocol adapter**: `POST /v1/chat/completions` → `brain_router.ask` (map
  messages↔question/aim, stream onto `/api/chat/stream`). This is the ONLY real gap (no OpenAI face exists today).
- Register it in OpenWebUI as a model ("Right Hand") via Admin→Connections (custom OpenAI base URL — zero OWUI code).
- **Result:** Tim selects "Right Hand" and chats the RHM, which already reads the supervisor via the fleet-source.
- *Smallest stage; gives the chat-with-the-supervisor feel immediately.*

### Stage 3 — YOUR VOICE BACK (Tim → fabric, close the loop)
- The reply path (push-only asymmetry, r9-confirmed: webhook-in, Pipe-out). When Tim posts in an OWUI channel,
  route it to the fabric: an OWUI **Pipe/Function** that calls the bridge `POST /api/channel/post {channel, message}`
  (ungated, live) tagged to the mapped fabric channel — OR Tim @-mentions the "Right Hand" model which routes.
- **Result:** Tim is a symmetric participant (sees the mesh + posts into it), not just a watcher. "Be in the room."

### Stage 4 — HYGIENE: one mind everywhere
- Unify RHM model-resolution across the faces (`/brain/ask`→kimi, `/chat`→Suite-pick, `/decision/explain`→`-pro`)
  so the RHM in OpenWebUI = the same role-resolved mind as the V-icon, never path-dependent `-pro`
  (cognition-is-role-resolved; the `-pro` anti-pattern caught earlier this session). Small rider.

## Decisions / cross-cutting
- The fabric needs an **OWUI admin token** to create webhooks (store securely; all local/tailnet).
- **Propose-floor holds:** the phone surface reads + proposes; it cannot fire `/spawn`/`/inject` (lead-only).
- **Pin OWUI to 0.9.6** (the verified version; the old deploy Dockerfile tracked unpinned `:main`).
- **Sequencing (flexible):** Stage 2 is smallest (chat fast); Stage 1 is the bigger payoff (the room). Either first.

## Fallback (not needed unless something regresses)
Fork LibreChat (MIT) for the room — only if OpenWebUI's channels substrate ever fails the use-case. The smoke-test
retired that risk; LibreChat stays documented as the clean fallback, not the plan.
