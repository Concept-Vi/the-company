# Claude Design → Company Connector — Remote MCP Exposure Design

*Draft for channel review. Security-sensitive: no build until Tim + lead approve the exposure boundary.*

## 1. Mission (restated from lead brief)

Make the company MCP **REMOTE** so Claude Design (Anthropic's no-code design tool) can connect as a custom connector, participate in company channels, read design/pipeline state, and submit design intent — while **never** gaining access to operator-only, destructive, or clone-spawning verbs.

Three sub-goals:
1. **Remote MCP gateway** — Streamable HTTP + OAuth 2.1, scoped by posture.
2. **Local Supabase ground** — dev Postgres + Auth + edge functions; proves-local-before-prod.
3. **Claude Design connector** — the inlet of the Face Pipeline (board://item-c0a2d591): seed → design → translate → company.

## 2. Current system (what I found)

| Piece | Location | Role | Relevant fact |
|---|---|---|---|
| **mcp_face** | `mcp_face/server.py` | stdio MCP server exposing ~64 generic verbs over `runtime.suite.Suite` | Process child of `claude`; no auth beyond Unix parent-trust |
| **Bridge** | `runtime/bridge.py:2728` | HTTP `:8770` REST face (`/api/*`) | Separate from MCP; already thread-pooled |
| **Session supervisor** | `runtime/session_supervisor.py` | HTTP `:8771` owns spawn/inject/teardown | 127.0.0.1 ONLY by law |
| **Capability posture** | `introspection/registry.py` + `ops/cli/capabilities.py` | Binary-discovered registry of Claude Code's own capabilities, classified `safe/consent/hazard/locked/unmatched` | Exists for the **platform**, not for company MCP tools |
| **Tool annotations** | `contracts/tools.py` | `readonly/destructive/idempotent` | Wired to SDK hints in `sessions.py` and `channels.py`; older modules pending |
| **MCP config** | `channels/channel.mcp.json` + `ui_claude_session.py:_MCP_CONFIG` | Declares stdio `mcp_face/server.py` to Claude | `--strict-mcp-config` rejects unknown keys |
| **Channel fabric** | `channels/company_channel.mjs` | Cross-session injection server | Already HTTP listener per session; separate concern |

## 3. Target architecture

```
┌─────────────────┐     OAuth 2.1 + PKCE      ┌─────────────────────────────┐
│  Claude Design  │ ─────────────────────────▶│  Remote MCP gateway         │
│  (custom conn.) │     Streamable HTTP       │  (build-prep/claude-design) │
└─────────────────┘                           └──────────────┬──────────────┘
                                                             │
                                                             │ calls same SUITE
                                                             │ as bridge + mcp_face
                                                             ▼
                                               ┌─────────────────────────────┐
                                               │  runtime.suite.Suite          │
                                               │  (one brain, now three faces)   │
                                               └─────────────────────────────┘
```

**Design principle:** reuse the existing `mcp_face/server.py` verbs, but gate the remote face with a **remote-posture whitelist**. Do not fork a second engine. The remote gateway is a transport + auth + scoping layer only.

## 4. Tool posture classification for the remote face

We extend the existing `readonly/destructive/idempotent` annotations with a **remote-posture** dimension.

### 4.0 Two non-negotiable guards

1. **FAIL-CLOSED / deny-by-default.** A tool with **no explicit** `safe` or `design` remote-posture is **NOT** exposed. Allow-list only; a newly added tool can never auto-leak because the default posture is absent/deny.
2. **MANDATORY AUDIT.** Every remote call is logged before execution. Audit-write failure ⇒ the call **FAILS LOUD**. No un-audited call ever succeeds.

### 4.1 Posture table

| Posture | Meaning | Remote policy |
|---|---|---|
| `safe` | Pure read, no side effects, idempotent | ✅ Expose |
| `design` | Needed for the Face Pipeline / Claude Design workflow; reversible/non-destructive | ✅ Expose |
| `consent` | Writes state but not destructive; leaves a trail | ⚠️ Expose only if explicitly enabled for the connector (DEFERRED initially) |
| `hazard` | Destructive or irreversible (`delete`, graph mutation) | ❌ Never expose remotely |
| `locked` | Operator-only (`approve`, `dispatch`, `apply`, `build-intent`) | ❌ Never expose remotely |

### 4.1 Proposed initial whitelist for Claude Design

| Tool module | Tools / ops | Remote posture | Why |
|---|---|---|---|
| `introspection` | `capability` (list/get/search/describe) | `safe` | Read what exists |
| `object_info`, `list_by_type`, `list_graphs` | | `safe` | Generic read |
| `cognition_info` | read-only sections | `safe` | Learn composition registries |
| `corpus` | query/read | `safe` | Ask the codebase |
| `instrument` | projection queries | `safe` | Navigate data |
| `territory` + `territory/label` | read | `safe` | Resolve addresses to human meaning |
| `chat` | `chat` | `safe` | RHM dialogue |
| `operator` | `operator(op='rules')` | `safe` | Read standing operator rules |
| `sessions` | `op=list|inbox|watch|describe|search|timeline` | `safe` | Read session fabric |
| `cc_channel` | `cc_channel.send` (to channels) | `design` | Claude Design participates in channel threads |
| `cc_board` | read ops | `safe` | Read noticeboard |
| `marks` / `annotations` | read ops only | `safe` | Read marks; **writes DEFERRED** until consent/audit gates are proven |
| **NEW** `claude_design` | `ingest_bundle`, `submit_seed`, `walk_decision` | `design` | The Face Pipeline inlet |

### 4.2 Explicitly NOT exposed remotely

| Tool / module | Why excluded |
|---|---|
| `node` (`create/delete/propose/apply`) | Graph mutation + build dispatch |
| `connect`, `set_config` | Direct graph mutation |
| `cc_clone` | Spawns Claude copies |
| `cc_gate` | Native gate/abort/rewind |
| `session_post` with `verb=wake\|consult` | Spawns sessions |
| `resolve_surfaced`, `approve_proposal`, `dispatch` | Operator-only governance floor |
| `checkpoint`, `revert`, `self_change_log` writes | Self-modification |
| `run_graph` | Compute-heavy; defer until rate-limiting exists |

## 5. Authentication model

**Choice: OAuth 2.1 with Supabase Auth as the authorization server.**

Rationale:
- Claude custom connectors require OAuth.
- Supabase Auth already provides JWTs, user management, and local dev.
- One auth stack for company users and Claude Design connector users.

### 5.1 Flow

1. Claude Design discovers the company MCP server via its connector URL.
2. Server returns `401` + `WWW-Authenticate` with protected resource metadata.
3. Client fetches `/.well-known/oauth-protected-resource`, then `/.well-known/oauth-authorization-server` from Supabase Auth.
4. Dynamic Client Registration (DCR) with Supabase Auth (or static client ID for Claude Design).
5. PKCE authorization code flow; user consents to scope `company:design:readwrite`.
6. Supabase issues signed JWT with audience = the company MCP resource.
7. Every MCP request carries `Authorization: Bearer <jwt>`.
8. Gateway validates JWT via Supabase Auth (local or project) and enforces token audience.

### 5.2 Scopes

| Scope | Grants |
|---|---|
| `company:design:read` | Safe read tools only |
| `company:design:write` | Safe + design tools (channel posts, pipeline ingest/seed) |
| `company:operator:*` | **Not issued remotely** — reserved for local/operator face |

**Initial write surface:** channel-post + pipeline ingest/seed only. `annotate`/`mark` writes are **deferred** until the consent/audit gates are proven.

## 6. Transport

**Primary: MCP Streamable HTTP** (`2025-06-18` spec). Single endpoint `POST/GET /mcp`.

- Server must support `Accept: application/json, text/event-stream`.
- Session management via `Mcp-Session-Id` header.
- Validate `Origin` header; bind local dev to `127.0.0.1`.
- HTTPS in production; local dev uses localhost / tailscale only.

**Why not HTTP+SSE legacy?** Claude docs say Streamable HTTP is preferred and legacy is being deprecated. We can support legacy as a fallback if cost is low.

**Hosting options:**
- **Dev:** dedicated `mcp_face/remote.py` service on `:8772` (lead ruling: isolate the internet-facing surface; `:8770` stays internal).
- **Prod:** Supabase Edge Function behind Tim's custom domain, same auth stack.

## 7. Local Supabase plan

1. Install Supabase CLI.
2. `supabase start` in `build-prep/claude-design/supabase/` or project root.
3. Configure:
   - `auth.users` table holds connector users.
   - Edge function `mcp-auth` validates tokens and returns JWKS.
   - Postgres schema `connector_audit` logs every remote tool call (who, what, when, address).
   - **Audit-write failure ⇒ call fails loud** (mandatory-audit guard).
4. Prove-local-before-prod: test client connects to `https://localhost:<supabase-port>` / local tunnel.

## 7.1 Production deployment (Tim-ruling; PUBLIC step gated)

- **Public endpoint:** APPROVED. The hard bar is **"secure and private"**.
- **Form:** Supabase Edge Function behind Tim's **custom domain** (project ref + domain provided by lead on request).
- **Auth stack:** Supabase Auth DIRECTLY as the OAuth 2.1 authorization server (no separate OAuth server).
- **Required hardening:**
  - Zero pre-auth leak: 401 + minimal OAuth metadata only before authentication.
  - OAuth 2.1 + PKCE.
  - Tight scopes (`read` vs `design-write`); operator scope NEVER remote.
  - Rate-limiting.
  - HTTPS only.
  - Fail-closed posture filter.
  - Mandatory audit.

**Sequence:** local build → lead verifies fail-closed + audit + scopes → THEN public deploy to custom domain.

## 8. Build sequence

1. ✅ **Design approval** — approved by lead with two required additions + six answers + Tim's Q5 ruling.
2. **Add remote-posture metadata** to `mcp_face/tools/*.py` modules (or a single `remote_exposure.json` registry).
3. **Build `mcp_face/remote.py`** — FastMCP-over-HTTP gateway on `:8772`, posture filter, JWT validation.
4. **Local Supabase** — auth + mandatory audit.
5. **Security verify** — lead verifies fail-closed REFUSES non-whitelisted/hazard tools, audit fires, scopes hold.
6. **Public deploy** — Supabase Edge Function behind Tim's custom domain (gated on step 5).
7. **Face Pipeline inlet tool** — `claude_design.ingest_bundle` calls existing INGEST → TAG → COMPOSE → VALIDATE → RECONCILE → REGISTER machinery.
8. **Verify by use** — real Claude Design export round-trips through Supabase + company.

## 9. Decisions (rulings received)

| Question | Ruling |
|---|---|
| **Port / process** | Dedicated `mcp_face/remote.py` on `:8772`; `:8770` bridge stays internal |
| **Consent write scope** | channel-post + pipeline ingest/seed only initially; `annotate`/`mark` writes **deferred** |
| **run_graph** | **NOT** exposed (even read-only compute); read-only graph inspection via `get_state`/`get_results` is safe |
| **Production auth** | Supabase Auth **directly** as the OAuth 2.1 authorization server |
| **Public hosting** | APPROVED. Supabase Edge Function behind Tim's custom domain, with the hardening listed in §7.1 |
| **Face Pipeline priority** | gateway + auth + posture-filter FIRST → verify authed connection → THEN `claude_design.ingest_bundle` |

---

*Sources: `mcp_face/server.py`, `runtime/bridge.py`, `runtime/session_supervisor.py`, `introspection/registry.py`, `contracts/tools.py`, `channels/channel.mcp.json`, `channels/company_channel.mjs`, MCP 2025-06-18 Streamable HTTP + Authorization specs, Claude custom connector docs, and oracle reply from clone-c9f6db2d. Rulings from lead via channel thread t-1781749300-ch-9e8zbg8b.*
