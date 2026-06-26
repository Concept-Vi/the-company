# Live-Local Round-Trip Verify — the lead's by-use acceptance gate (#77 step c)

*The gate before the flip. Every line is verified BY USE on the LOCAL stack — a real call, a watched result — not by reading code. "No error" is not a pass; the PURPOSE must be observed. Authored by lead (ch-al7jdfdr) 2026-06-18 against the live contracts; execute the moment fork's start()+publish-hook AND builder's Edge Function dispatch are both testable.*

## What this proves
Claude Design is a real two-way peer in the SHARED channels on the SAME data, scoped by two gates (posture + RLS), with zero box exposure and zero leak of internal channels — the thing Tim actually asked for. The RLS pieces were each proven in ISOLATION (boundary 0005, design_client 0006). This gate proves the INTEGRATED round-trip through the real transport (websocket-client Realtime) + the Edge Function.

## Preconditions (confirm before running)
- [ ] Local Supabase up (API/Auth :15421, DB :15432); all 5 tables in `supabase_realtime`.
- [ ] Boundary principal env loaded (`.boundary.env`, role=company_boundary); design_client (CD) credential available (role=design_client, client_id=claude-design).
- [ ] Seed `design` shared channel exists (shared=true) + granted in the claude-design client row's `channels`.
- [ ] A CONTROL internal-only channel exists (shared=false) — the leak test.
- [ ] fork's boundary Realtime sub (start()) connected with the principal JWT in phx_join (else RLS streams nothing — silent-empty).

## The round-trip (by use)
**A · BOX→SHARED publish.** A company session posts to `design` → boundary writes to Supabase channel_posts (sender_kind='session') → 201. ☐ row present in Supabase.

**B · SHARED→BOX inject (sessions see each other).** Boundary's Realtime sub receives the INSERT → injects into the OTHER `design` member-sessions, NOT the poster (skip-origin). ☐ a second company session actually receives it; ☐ the poster is NOT re-delivered (no echo, no double-deliver).

**C · CD→SHARED (Claude Design participates).** Drive the Edge Function as CD (design_client JWT forwarded) posting to `design` → 201 (sender_kind='client', from_session='claude-design') → boundary's sub receives → injects into the company member-sessions. ☐ a Claude-Design post reaches the live company sessions.

**D · SHARED→CD read (same data).** As CD, read `design` history via the Edge Function dispatch → sees BOTH the company posts and its own. ☐ CD reads the same data everyone else has.

## The security bar (the "private + secure" half — each BY USE)
**E · Private stays dark.** ☐ the internal-only channel (shared=false) is NEVER published to Supabase (no rows for it); ☐ as CD, read/post to the internal channel → 403; ☐ as CD, read/post to a shared-but-NOT-granted channel → 403.

**F · No impersonation / no service_role bypass (THE crux of the public surface).** ☐ as CD, post with a forged from_session → 403 (RLS ties from_session=client_id) — confirmed through the EDGE FUNCTION path, not just direct REST. ★ THREAT this proves dead: service_role bypasses RLS, so if the Edge Function used it for CD's channel/collab WRITES, a forged from_session would SUCCEED (silent impersonation, the worst failure of a public connector). A 403 here proves the Edge Function forwards the CD user's JWT for writes (RLS gate-2 live) and reserves service_role for ONLY audit-insert + client-registry-read. ☐ corroborate by inspection: the Edge Function's service_role client is called on NO CD-write path (grep the dispatch — service_role touches connector_audit + the clients lookup only).

**G · Fail-closed tools.** ☐ as CD, attempt a non-design/dangerous tool (clone-spawn/dispatch/self-modify/approve) via the Edge Function → refused at gate-1 posture. ☐ a tool with no explicit remote-posture → refused (deny-by-default).

**H · Mandatory audit.** ☐ every CD call (read AND write) writes a connector_audit row; ☐ an induced audit-write failure makes the call FAIL LOUD (no un-audited call succeeds).

**I · Internal lifeline intact.** ☐ the existing session↔session internal fabric still delivers byte-identical (the additive shared path did not disturb the live coordination layer) — re-checked after, on a throwaway channel.

## Pass condition
ALL boxes observed by use. Any red = not done; fix + re-run the whole gate (not just the failed line — integration regressions hide). Only on a fully-green gate do I proceed to THE FLIP (prod migrations 0001–0006 + prod principals + Edge Function deploy + the same gate re-run live on vspokes.com with a real OAuth token).

## Pre-flip hardening (before the public door — found by lead's EF security read 2026-06-18; NOT local-verify blockers)
- **A · Audit ordering (audit-BEFORE-execute).** ✅ RESOLVED (2026-06-18). The EF now writes a PENDING audit row BEFORE dispatch (fail-loud → dispatch skipped if the insert throws), then auditOutcome() PATCHes the row to OK/DISPATCH-ERROR after. Verified by use in gate H: inducing an audit-insert failure (revoke service_role INSERT on connector_audit) on a WRITE → the EF returns "AUDIT PENDING FAILED — call refused (mandatory-audit, no write performed)" AND the channel_posts count is unchanged (5→5) → the write did NOT persist. The earlier "audits AFTER dispatch" framing is STALE — the code is audit-BEFORE.
- **B · Audience binding.** AUDIENCE defaults to the generic "authenticated" (every Supabase user JWT carries it), not the MCP-resource audience the design intends (§5). Mitigated for the first flip by the scope gate (must carry company:design:read|write) + the active-client-policy gate — a random authed user without those → 401. But a resource-bound audience is the defense-in-depth against cross-resource token replay. ACCEPTABLE for the first flip given the scope+policy gates; HARDEN as a fast-follow via a Supabase custom-access-token hook that stamps aud=<MCP resource>, then set AUDIENCE to match. Decide explicitly at the flip — don't let the default ride silently.

## Note on FORM
This gate is a backend round-trip — FORM (the navigable/legible face) attaches to the eventual Claude-Design-in-channel EXPERIENCE: the connector UX (Anthropic's side) + how shared-channel posts render for Tim. That FORM bar is assessed when the participation is live + visible, not in this backend gate. Flagged so it is not skipped later.
