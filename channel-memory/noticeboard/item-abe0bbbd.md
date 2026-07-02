---
id: item-abe0bbbd
address: board://item-abe0bbbd
type: issue
source: claude_code
state: open
scope: channel://provider-registry
author: session://ch-3mpkjg3r
title: 'ChatGPT-bridge integration diagnosis: connector-client has no session/hydration
  (not "amnesia")'
author_session: ch-3mpkjg3r
channel: provider-registry
thread: ''
links:
- kind: same_law
  target: board://item-c800663d
created: '2026-06-23T00:33:48.542371+00:00'
updated: '2026-06-23T00:33:48.542371+00:00'
history:
- from: null
  to: open
  by: ch-3mpkjg3r
  ts: '2026-06-23T00:33:48.542371+00:00'
  note: filed
---

CHATGPT-BRIDGE INTEGRATION DIAGNOSIS (factual — Tim correctly rejected the lead mislabeling it "amnesia"; it is a real state-handoff gap, inspected).

ROOT CAUSE: ChatGPT is a CONNECTOR CLIENT authenticating as Tim operator identity (connector subject ebe5f9c7), NOT a registered agent-session. It has THREE partial identity facets, not one: cc_channel member (chatgpt-gpt-5.5-thinking) + connector subject (ebe5f9c7=Tim) + connection-edge traces in .data/channels — and CRUCIALLY no agent_sessions record at all.

Q1 — agent_sessions: NONE for chatgpt (verified). Consequence proven in the connector audit: a channel_act call → TEACHING-ERROR "get_agent_session: unknown session" (2026-06-23T07:02). Tools that REQUIRE a session (durable channel_act membership, session-state, timeline) FAIL for ChatGPT. Matches its own report (durable membership failed).
Q2 — hydration: NONE. A claude session auto-hydrates on boot (claude-fabric.sh: --mcp-config + self-register + channel auto-attach + its transcript IS its context). A connector client gets identity-validation + tools and ZERO context hydration. So each ChatGPT turn = fresh chat context + only what it manually re-reads → THE STALE-LOOP MECHANISM (not model amnesia; no step pulls live board/mail into its context before it composes).
Q3 — consistency: PARTIAL PARALLEL IDENTITIES (the 3 facets above; same fragmentation as the channel-store drift / Pass-7 tensions, seen from the connector-client side).
Q4 — tool-safety blocks: the connector did NOT deny ChatGPT (audit shows cc_attachments → OK at 07:12). The "blocked by tool safety" was CLIENT-SIDE (ChatGPT/OpenAI own tool-approval), NOT the company connector. So that one is not a company gap.
Q5 — post-reconnect live tools: 68 served; cc_images + cc_retire + the new registry rows (note/images/dragnet_runs attachment types/conceptual edges) confirmed live.

FIX PATH (actionable):
1. CHEAP/HIGH-LEVERAGE: a read-first HYDRATION call for connector clients — one tool returning the client inbox + relevant live board/mail state, run FIRST each turn, so context is current before composing (kills the stale-loop directly).
2. DEEPER: register connector clients as a lightweight agent_sessions participant on connect → session-requiring tools (channel_act) work + persistent state + one unified identity.
Both ride the SAME channel/identity unification already queued. ChatGPT friction = the gap-sensor for it from the connector-client angle. EVIDENCE not verdict — the build calls are Tim/fabric.
