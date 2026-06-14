---
trust: fabric-derived
author: ch-al7jdfdr (lead, session bda8ce28)
date: 2026-06-14
verified: lead-lane companion to UNIFIED-SEAM.md — the CHANNEL half of the one spec; grounded in Tim-direct corrections (2026-06-14) + lead-lane-inputs.md
relates: [UNIFIED-SEAM.md, APPROVAL-STANDARD.md, ../design/lead-lane-inputs.md]
---
# CHANNEL-LAYER SEAM — the fabric's live-session layer (lead lane), companion to UNIFIED-SEAM

UNIFIED-SEAM covers the MEMORY system (capture→embed→gather→judge→recall + outer layers). This covers
the CHANNEL LAYER — live-session messaging, grouping, membership — the other half of the fabric, and
the ONE place the two halves wire together (the 5th wire: channel-scoped recall).

## 1. The channel model (lead-owned) `[tim-direct corrections 2026-06-14]`
- A **channel** = a named, managed group: member-set + attached context (§3) + coordinator. REUSES the
  Company's existing channels/gatherings concept; not a fork.
- **Membership is a registry**: cc_channel gains create · list · add-member · remove-member · archive.
  A session or supervised clone can be in several channels at once. (Tim: "multiple channels, create/
  managed, members added and removed.")
- **A member is reached by its transport** (the unified transport, Tim-approved "notify-each"): the
  member row carries `transport: channel|supervised`; push dispatches per-member (HTTP to a live
  channel session's port, or supervisor /inject to a clone). One broadcast fans across mixed members;
  replies aggregate by channel thread. Pulling a clone into a channel emits a Notice to Tim.
- **Join = the launch flag, no wrapper** (Tim corrected): `claude --mcp-config channels/channel.mcp.json
  --dangerously-load-development-channels server:company-channel`. The CLI capability is already in the
  registry; nothing wraps it.
- **Profile via a SessionStart HOOK** (Tim): on start a session writes a PROFILE (handle, cwd, model,
  self-description) to the registry, so listing members shows rich profiles, not the thin announce.
  Hook = identity/profile; flag = transport. (Tim applies the global hook — the boundary edit.)

## 2. State today vs to-build
- TODAY (built + proven): cc_channel list/send/broadcast/mail over ad-hoc handle lists; per-session
  announce/reply; the supervisor /channel-reply+/channel-send; presence auto-prune; 17/17 router test.
- TO BUILD (under the confirmed standard, reversible): the channel REGISTRY (named channels, create/
  add/remove/archive); the unified per-member transport (push|supervised — my cc_channels half +
  fork's clone-registration half, Tim-approved); the profile SessionStart hook; the attachments
  manifest (§3); channel-scoped recall (§4, the 5th wire).

## 3. Channel attachment (Tim's "sessions + docs attached to a channel as loadable context")
A channel row carries an **attachments manifest**: `{sessions:[session://…], docs:[path…],
recall_scope:{…}}`. On add-member, the member is handed the manifest as context (the channel's
rule/context-set). Reuses the channel push (inject a context-load message on join).

## 4. ★ THE 5TH WIRE — channel-scoped recall (where the channel layer wires to the memory system)
`cc_channel op=recall {channel, query}` runs the MEMORY system's recall spine (the fork's
capture→embed→gather→judge→recall, the recall-fork's OUTER) **scoped to the channel's attached sessions**
— using D-1 multi-space addressing's scope axes (project·session·segment) as the filter. So the channel
layer CONSUMES the memory system's recall, scoped by channel membership/attachments. This is Tim's
"link recall + semantics to channels." Clean wire: channel layer (lead) → recall API (fork/recollection)
with a scope selector. The recall stack (served :8007/:8008, wire-3) is shared.

## 5. Ownership
- LEAD owns: the channel layer (registry, management, unified transport, attachment, profile-hook),
  and serves the embed :8007 / rerank :8008 stack the memory system uses.
- recollection/fork own: the recall spine + outer memory layers the channel-scoped recall calls into.
- Wire at §4 (channel-scoped recall) + the served-stack contract (UNIFIED-SEAM wire-3).

## 6. Correction to UNIFIED-SEAM (for the recall-fork to apply — its doc)
UNIFIED-SEAM lines 5 + 48 + §5/§8 say "self-approval is HELD (HELD-self-approval.md)". That is now
STALE: Tim confirmed the standard DIRECTLY to the lead — see APPROVAL-STANDARD.md (Option A + the
high-bar transcript condition). HELD-self-approval.md was git-mv'd to APPROVAL-STANDARD.md. Update the
seam's references: self-approval of git-revertible+cross-reviewed consequential actions via high-bar
recorded intent is GREEN; only the truly-irreversible class pings Tim.
