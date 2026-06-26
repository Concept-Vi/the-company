# THE FULL-ACCESS CONNECTOR — status + runbook
*Tim's directive (2026-06-21): full-access remote connector — "they get all", "get it all done so I can use it and connect it", full authority. This doc is the durable runbook (survives compaction).*

## What it is
A remote MCP connector that lets cloud apps (ChatGPT · Codex · Claude) reach the company's **66 local tools** as **Tim** (his authenticated-remote self), with everyone else locked to 23 safe reads. The relational shape: **Identity (Supabase) → Reach (Tailscale Funnel) → Tools (local remote.py)**.

## Architecture (Arch 1 — remote.py direct; advisor-confirmed clean reuse)
```
ChatGPT/Codex/Claude → OAuth login → SUPABASE Auth (issues signed JWT, sub==Tim)
   → app calls the connector URL with the JWT
   → TAILSCALE FUNNEL (public doorway :10000 → 127.0.0.1:8772)
   → remote.py (validates JWT via Supabase JWKS; sub==Tim → FULL; else → 23 safe)
   → the 66 company tools (run locally)
```
- **Supabase is the OAuth server** (it has `/oauth/clients/register` → supports Dynamic Client Registration, so any MCP client self-registers). remote.py only VALIDATES + serves discovery.
- **remote.py** (`mcp_face/remote.py`) is the minimal-surface tool front (only `/mcp` + discovery; NOT the bridge's 50 routes) — that's why it's the safe Funnel target, not the bridge.

## What's BUILT + VERIFIED (committed 4859a40)
The operator-full path on `remote.py`:
- `sub == OPERATOR_USER_ID` (Tim, `ebe5f9c7-4d66-4717-835f-afc96088facb`) → `SCOPE_OPERATOR_FULL` → all 66 tools (incl. the 10 dangerous MCP verbs: cc_clone/cc_gate/channel_act/connect/mark/node/run_graph/self_change_log/session_post/set_config). Mandatory audit kept.
- Identity overrides the connector-scope gate inside JWT validation (else Tim's token 401s first — advisor catch).
- DEV_TOKEN bypass HARD-DISABLED when `REMOTE_PUBLIC=1` (else a static secret is a JWT-bypass on the public endpoint — advisor catch).
- OAuth discovery advertises the real public resource URL + Supabase AS.

**Adversarial verification (127.0.0.1, default-to-wrong — ALL PASS):**
| Case | Result |
|---|---|
| no token / forged / wrong-sig | 401 |
| dev-token on public instance | 401 (bypass disabled) |
| valid non-Tim token | LIMITED (23 safe; dangerous REFUSED) |
| valid Tim token | FULL (66; cc_clone/node/run_graph dispatch) |

(The real-token-mint proof was blocked by the safety classifier as credential-leakage — fair; the live proof is Tim's actual app-connect.)

## How to RUN remote.py (the production instance)
```bash
SUPABASE_JWKS_URL="https://gctunhsuwpaxeatwlmuv.supabase.co/auth/v1/.well-known/jwks.json" \
SUPABASE_JWT_AUDIENCE="authenticated" \
OPERATOR_USER_ID="ebe5f9c7-4d66-4717-835f-afc96088facb" \
REMOTE_PUBLIC="1" \
PUBLIC_RESOURCE_URL="https://workstation001.tail777bc2.ts.net:10000" \
PUBLIC_AS_URL="https://gctunhsuwpaxeatwlmuv.supabase.co/auth/v1" \
.venv/bin/python mcp_face/remote.py 8772
```
Currently running (nohup, localhost-verified). **TODO (durability):** make it a `company`-managed service so it survives reboot (today it's a nohup process).

## Funnel
- Configured: `tailscale funnel --bg --yes --https=10000 8772` (public :10000 → local :8772). Status: `AllowFunnel:true`, listening.
- Tim ENABLED Funnel on the tailnet (the one admin-console step only he could do).
- Cert provisioned (`tailscale cert workstation001.tail777bc2.ts.net`). The Funnel/`tailscale serve` uses Tailscale's OWN internal cert store — no code reads a cert file. The manual `tailscale cert` EXPORT (the `.crt`/`.key` pair) lives OUT OF THE REPO at `~/.config/company/certs/` (key chmod 600), NOT in the repo root — do not run `tailscale cert` from `/home/tim/company` (it drops the secret key into the working tree; it's gitignored, but it belongs out-of-tree).
- ⚠️ **OPEN: external routing not yet live** — TLS handshake hangs at Tailscale's funnel edge (`43.245.48.235:10000`). Likely propagation (funnel just enabled) or a `:10000` quirk. **Next step if still down: move the funnel to `:443`** (the standard port; currently held by the company-UI serve — would need a path-mount or port reshuffle).

## The connector URL (to hand Tim once external routing is live)
**`https://workstation001.tail777bc2.ts.net:10000/mcp`** — paste into ChatGPT / Codex / Claude as a custom MCP connector; sign in as the Supabase account → full access. Tim controls per-app tool visibility in each app.

## What's LEFT
1. Funnel external routing (propagation re-check / `:443` fallback) — lead.
2. Make remote.py a managed service (durability) — lead.
3. Tim's app-connect = the live one-app proof — Tim.
