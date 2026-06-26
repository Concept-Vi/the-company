---
id: item-3d92a53f
address: board://item-3d92a53f
type: block
source: claude_code
state: current
title: F1 · The scope (needs, not solutions)
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-91983d4f
created: '2026-06-24T12:12:11.429611+00:00'
updated: '2026-06-24T12:12:11.429611+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T12:12:11.429611+00:00'
  note: filed
---

# The scope — what's needed (framed as needs, the HOW is yours to resolve with Tim)

Everything discussed this session, as NEEDS (not designs):
- The realtime two-way chat (operator ⇄ a member) is WORKING as a first-bit over the channel fabric — build the rest on/around it.
- The full channel + project system: addressing chat to ANY member (not just the lead); resolving "the lead/Vi" to a live session by ROLE (not a pinned handle); delivering replies to the app even when the chat tab is closed; a PROJECT switcher (the app is hard-wired to one channel — it needs to be multi-project: projects ≈ channels, each with its content / people / conversation).
- The interface itself must become a proper COMPOSITION under the company's laws (it is currently a monolith) — and every change Tim requests thereafter must be made properly + self-documented, with no drift. (See the interface-architecture background doc — background only, no plan.)
- Latent capabilities raised: images/files both ways (wired), tappable choices/decisions, remote tool-approval (permission relay), and VOICE (needs a working STT service — all company STT providers are currently offline).
The lead does NOT specify how any of this is built. That is for Tim's architecture + your research.
