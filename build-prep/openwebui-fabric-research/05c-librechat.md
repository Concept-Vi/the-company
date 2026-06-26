# 05c — LibreChat: Self-Hosted Chat-UI Platform Research

> Part of the chat-UI platform evaluation for the Company fabric front-end. Companion files: `05a-openwebui.md`, `05b-lobechat.md`, `05d-comparison.md`. Shared rubric: `_SHARED-RUBRIC.md`.
>
> **Why this is the third pick:** chosen over AnythingLLM (RAG-app skew), Jan (desktop/Electron-first), and Big-AGI (smaller community) because it is the **most forkable conventional React/Node stack** with active multi-user auth, an agents framework, and strong MCP traction. The live evidence confirms that reasoning.
>
> **Grounding:** all load-bearing claims fetched live (June 2026) from `github.com/danny-avila/LibreChat` (README, LICENSE, package.json files) and `librechat.ai/docs`. License + MCP claims spot-checked by the lead against primary sources. **One correction applied:** the research agent listed `websocket` as a 4th MCP transport; the live MCP docs page lists **three** (stdio, SSE, streamable-HTTP) and does **not** mention websocket — corrected below.

## Summary

LibreChat is an actively maintained (~39.6k stars, daily commits), **MIT-licensed** chat UI on a deliberately **conventional stack: React 18 + Express 5 + MongoDB**, Turborepo monorepo. Its **MCP support is first-class and config-driven** (not plugin-gated) and its **OpenAI-compatible "custom endpoint"** is the cleanest "point at an arbitrary HTTP API" story of the three — so the fabric is reachable two ways (custom endpoint *and* fabric-as-MCP-server) with zero code. The MIT license has **no branding clause**, and ClickHouse is now backing the project. The gap, as with the others: **no native server→browser push** — SSE carries only in-flight LLM token streams; fabric→UI push of unsolicited content requires a **bounded fork** (~3–5 new files), made tractable precisely by the plain stack.

---

## 1. Architecture
- **Frontend:** React 18.2 / TypeScript, Vite, Tailwind CSS, Radix UI + Headless UI + Ariakit, Framer Motion. SPA. **PWA via `vite-plugin-pwa` v1.3.0** (service worker + manifest → installable).
- **Backend:** Node.js, **Express 5.2** / TypeScript. Turborepo monorepo: `api/` + `client/` + `packages/` (the agentic runtime is the separately-versioned `@librechat/agents` package).
- **Database:** **MongoDB** (Mongoose 8) + Redis (sessions/rate-limit).
- **Transport:** REST for CRUD; **SSE** for LLM token streaming **only** — there is **no general-purpose bidirectional server→browser channel**. (LibreChat's backend *can* speak SSE/WS to external MCP servers; that is backend↔MCP, not server↔browser.)
- Source: `client/package.json`, `api/package.json` (raw.githubusercontent.com), `librechat.ai/docs/configuration/librechat_yaml`

## 2. Extensibility
- **Custom Endpoints** (`librechat.yaml` `endpoints.custom[]`): any OpenAI-compatible base URL, per-endpoint key, **custom headers** with `{{LIBRECHAT_USER_*}}` / `{{LIBRECHAT_BODY_CONVERSATIONID}}` placeholders, `addParams`/`dropParams`, icon. First-class config primitive. Source: `librechat.ai/docs/configuration/librechat_yaml/object_structure/custom_endpoint`
- **Agents framework:** no-code builder; Code Interpreter, File Search/Context, MCP tools, **Actions** (tools generated from an OpenAPI spec URL), **Agent Chain** (Mixture-of-Agents), Subagents, Skills (SKILL.md), Artifacts (React/HTML/Mermaid in a side pane). Source: `librechat.ai/docs/features/agents`
- **Agents API (Beta):** programmatic access to LibreChat agents via OpenAI-compatible SDK / Open Responses — enables external orchestration (fabric→LibreChat).
- **Deferred Tools:** MCP tools excluded from initial context, discovered on demand via ToolSearch.
- **Custom panels / UI injection:** **none.** `interface.yaml` toggles visibility of *existing* elements; it does not add new ones. New panels = fork the React client.

## 3. Model + Backend Support
Native: OpenAI, Azure, Anthropic, Gemini, Bedrock, Ollama, and **any OpenAI-compatible custom endpoint**. The fabric is one YAML stanza:
```yaml
endpoints:
  custom:
    - name: 'Fabric'
      apiKey: 'user_provided'        # or static token
      baseURL: 'http://fabric-host:PORT/v1'
      models: { default: ['supervisor', 'channel-alpha'] }
```
`directEndpoint: true` for non-standard paths; per-user identity headers; dynamic model fetch with `fetch: true`. Source: `librechat.ai/docs/configuration/librechat_yaml/object_structure/custom_endpoint`

## 4. Multi-user / Auth — strongest enterprise auth of the three
- Local email/password (registration toggle); social OAuth2 (Google, GitHub, Discord, Facebook, Apple); **OpenID Connect** (Auth0, Cognito, Entra/AD, Keycloak — with token reuse for downstream MCP On-Behalf-Of); **SAML**; **LDAP/AD** (full bind/search/StartTLS).
- **ACL-based RBAC** (migrated to ACL model at v0.8.0-rc3): `USER`/`ADMIN` + custom roles; per-resource `VIEWER/EDITOR/OWNER` on agents, prompts, MCP servers, shared links; admin panel.
- **Per-user MCP isolation** (15-min idle disconnect; `{{LIBRECHAT_USER_ID}}` into MCP headers). Source: `librechat.ai/docs/configuration/authentication/ldap`, `.../access_control`

## 5. Mobile / PWA
**Installable PWA** (`vite-plugin-pwa` confirmed in `client/package.json`), responsive Tailwind UI. **No native mobile app** ("LibreChat is a self-hosted web application, not a native app" — docs). Depth of mobile optimization (offline, push, gestures) **unverified** from live sources. → "Installable PWA" verified; "good phone usability" unverified.

## 6. Theming / Branding
Config (`interface` object): custom welcome (`{{user.name}}`), privacy/TOS URLs + modal, feature toggles, per-endpoint `iconURL`, MCP `iconPath`. **No `logo`/`appName` key** in `librechat.yaml` (the branding docs path 404s); full white-label = fork-and-rebuild the client **or** inject CSS overrides. **No license clause restricts branding** (MIT). Source: `librechat.ai/docs/configuration/librechat_yaml/object_structure/interface`, discussion #3706

## 7. Fork / Extend Difficulty — most tractable of the three
- **Conventional stack** (React 18, *not* a framework like Next.js; Express 5; MongoDB) — any mid-level TS/React dev can navigate it. No proprietary component framework (Radix + Tailwind).
- **Monorepo** `api/`+`client/`+`packages/`; `@librechat/agents` runtime separately versioned. Full TypeScript types in shared packages.
- **Config-first** (endpoints, MCP, interface toggles) shrinks the fork surface for common cases.
- **Server push (the hard part):** add a new SSE/WebSocket route on Express + a React context/hook to subscribe + a custom panel component — **~3–5 new files, no deep core surgery**, but a real fork with ongoing merge cost (daily upstream commits). Source: `github.com/danny-avila/LibreChat`

## 8. License (HIGHEST-stakes — verified by lead against primary source)
**Standard MIT** (Copyright (c) 2026 LibreChat). **No branding-protection clause, no commercial restriction, no attribution-in-UI requirement.** White-label + commercial deployment fully permitted. (Contrast: OpenWebUI's branding clause, LobeHub's commercial-derivative restriction.) Source: `raw.githubusercontent.com/danny-avila/LibreChat/main/LICENSE`

## 9. Maturity / Community
~39.6k stars, 8.1k forks, 4,579 commits, 95 tags, last commit hours before scrape (June 22 2026). Solo founder (danny-avila) + active core contributors; **community-maintained, not a corporate product** — **but now joining ClickHouse** ("to power the open-source Agentic Data Stack") → corporate backing = likely sustained investment + a governance/roadmap influence to watch. Source: `github.com/danny-avila/LibreChat`, `clickhouse.com/blog/librechat-open-source-agentic-data-stack`

## 10. MCP Support (HIGHEST-stakes — verified by lead against primary source)
**Native, config-driven (`librechat.yaml` `mcpServers`), not plugin/gateway.** Transports (per live docs): **`stdio`, `sse`, `streamable-http`** — streamable-HTTP recommended for production; SSE legacy/"not recommended for production." *(The 4th transport "websocket" claimed in raw research is NOT listed on the live MCP docs page — corrected.)* MCP servers appear in the **chat dropdown** *and* the **Agent builder**; **UI-based add** without config edit/restart (for HTTP/SSE); YAML-added servers need a restart. Per-user `customUserVars`, OAuth2 (+ Dynamic Client Registration), On-Behalf-Of token exchange, deferred tools, Smithery.ai marketplace. The fabric can expose itself as a streamable-HTTP MCP server (whitelisted via `mcpSettings.allowedAddresses`). Source: `librechat.ai/docs/features/mcp`, `.../object_structure/mcp_servers`

---

## The 4 Use-Case Priorities

### (a) Extensibility / inbound-message surfacing — **THE DISCRIMINATOR: Weak (but the most tractable fork)**
SSE is **strictly** in-flight LLM token streaming; **no** server-initiated push bus, no event bus, no server↔browser WebSocket, no custom-panel injection API. `interface` toggles existing components only. **Fabric→UI push requires a fork:** new persistent SSE/WS route on Express (fabric triggers) + React subscribe hook + custom panel component — **bounded (~3–5 files), no deep core surgery**, ongoing merge cost. The conventional stack is what makes this the *least painful* fork of the three. (The Agents API Beta enables fabric→LibreChat outbound calls / webhook-style coordination, but that is not inbound server-push.)

### (b) External call-out to fabric HTTP/MCP — **Strong (non-discriminating; cleanest of the three)**
Two zero-code paths: the `custom` OpenAI-compatible endpoint, and fabric-as-MCP-server (streamable-HTTP to an internal address). Per-user identity headers included.

### (c) Mobile — **Partial**
Installable PWA + responsive; no native app; mobile-optimization depth unverified.

### (d) Code-extension cleanliness — **Strong (most tractable of the three)**
React 18 + Express 5 + MongoDB + TS, conventional and well-understood; clean monorepo; separately-versioned agents runtime; config-driven for common cases. Main friction = merge cost vs. daily upstream.

---

## Bottom line for the fabric use-case
**Biggest strength:** the cleanest external-call-out story (custom endpoint *and* fabric-as-MCP-server, both zero-code), **MIT with no branding clause**, conventional React/Express/MongoDB stack that makes the inevitable fork the **most tractable of the three**, plus new ClickHouse backing.
**Biggest gap:** **no native server→browser push** — the fabric cannot push unsolicited channel/member content into the UI without forking the React client to add a real-time channel + custom panel. That fork is **bounded and achievable**, not a configuration option. The "most-forkable conventional stack" rationale is confirmed: if a fork is unavoidable (it is, for every candidate), LibreChat is the one you'd most want to fork.
