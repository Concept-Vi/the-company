# PROD FLIP RUNBOOK — Claude Design connector goes public (staged, one-confirm-to-execute)
*Staged by lead 2026-06-18 while Tim was away. ★ PRECONDITION: Tim's EXPLICIT, PRESENT "do the flip" — NOT a vague "go." Opening the public door is irreversible + outward-facing; it needs Tim at a keyboard (for his 3 dashboard steps) and watching. The local A–I gate is fully green by use (build-prep/claude-design/LIVE-LOCAL-VERIFY.md) — this is the deploy of the proven thing, not new work.*

## The split: AUTOMATIC (me + builder) vs TIM's DASHBOARD (his project / domain / OAuth secret)

### On Tim's "do the flip", LEAD executes (Supabase MCP on gctunhsuwpaxeatwlmuv):
1. **Apply migrations 0001–0006 to prod** via `mcp__supabase__apply_migration` (one per file; SQL proven on local). Files: build-prep/claude-design/supabase/supabase/migrations/{0001_connector_audit · 0002_clients · 0003_channels · 0004_collab_data · 0005_boundary_rls_seed · 0006_design_client_rls}.sql. (0002 seeds the claude-design client row; 0005 seeds the 'design' shared channel + grants it to claude-design + the authenticated INSERT/UPDATE grants; 0006 the design_client RLS.)
2. **Mint the prod boundary principal** — an authenticated user with `app_metadata.role='company_boundary'` (admin MCP `auth_create_user` then `auth_update_user` to set app_metadata, or create with app_metadata). Hand fork the cred OUT-OF-CHANNEL (COMPANY_CHANNEL_SA_EMAIL/_SA_PASSWORD/_ANON_KEY/_SUPABASE_URL for the prod boundary process — canonical names per supabase_principal.py). 0005's `is_company_boundary()` keys off the claim, so the RLS is byte-identical local↔prod.

### BUILDER executes (its Supabase MCP, code-only, no secrets):
3. **Deploy the edge function** to prod via `mcp__supabase__deploy_edge_function`, `verify_jwt=false` (the EF IS the auth gate — jose jwtVerify vs JWKS; Supabase's function-JWT would double-gate). Supabase auto-injects SUPABASE_URL/SERVICE_ROLE_KEY/ANON_KEY; JWKS_URL derived; AUDIENCE defaults "authenticated". Safe pre-public: auth-gate + zero-pre-auth-leak hold regardless of tables; authed calls error (not leak) until tables exist.

### TIM's DASHBOARD steps (3 — the door can't open without them):
4. **Enable the OAuth server** — Authentication → OAuth Server → Enable.
5. **Create the OAuth client** — Authentication → OAuth Apps → Add client: Name `Vi`, Redirect URI `https://claude.ai/api/mcp/auth_callback`, type Confidential → yields **Client ID + Secret**. ★ ALSO: the CD OAuth-flow user must carry `app_metadata.role='design_client'` + `app_metadata.client_id='claude-design'` (+ scope `company:design:write`) so the 0006 RLS gates it like local — set on the OAuth user's app_metadata OR via a custom-access-token hook (the AUDIENCE fast-follow can stamp both; builder confirms the exact mechanism — see OPEN).
6. **Custom domain** `vspokes.com` → route the project → MCP URL = `https://vspokes.com/functions/v1/claude-design-gateway/mcp`.

### LEAD — the gate before the door is usable:
7. **Live re-verify on the prod public endpoint** — the full A–I, real OAuth token + RLS (the same gates as LIVE-LOCAL-VERIFY, on vspokes.com): zero-pre-auth-leak · channels-scope · post-lands · CD↔company round-trip · non-granted 403 · no-impersonation · fail-closed tools · audit-before-dispatch. Only on green is the door "open."

### HANDOFF CARD → Tim (the connector-dialog inputs):
8. `{ Name: "Vi", Remote MCP server URL: https://vspokes.com/functions/v1/claude-design-gateway/mcp, OAuth Client ID: <from step 5>, OAuth Client Secret: <from step 5> }` → paste into Claude's Add-custom-connector dialog.

## OPEN (resolve before/at the flip — non-blocking to staging)
- ★ **design_client OAuth-claims mechanism** (builder confirming): how the real CD's OAuth-flow JWT gets `role=design_client` + `client_id=claude-design` + scope. Likely a **custom-access-token hook** (also the home for the AUDIENCE resource-binding fast-follow — stamp `aud=<MCP resource>` + set AUDIENCE to match, closing cross-resource replay). If the hook lands, it does both (claims + audience) in one place.
- The OAuth-client step (5) can be Tim-in-dashboard OR lead-via-API if Tim provisions the prod service_role key out-of-channel.

## Why staged, not fired
Tim said "go, get whatever you can going" while away on a bike ride. A live PUBLIC prod deploy is high-severity + irreversible + outward-facing — it needs his specific, present confirm and his eyes (and his 3 dashboard steps). So everything is staged here; on his explicit "do the flip" at a keyboard, steps 1–3 + 7–8 run in minutes and he does 4–6. Nothing touched prod while he was away.
