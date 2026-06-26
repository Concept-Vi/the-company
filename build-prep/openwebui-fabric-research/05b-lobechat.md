# 05b — LobeChat / LobeHub: Self-Hosted Chat-UI Platform Research

> Part of the chat-UI platform evaluation for the Company fabric front-end. Companion files: `05a-openwebui.md`, `05c-librechat.md`, `05d-comparison.md`. Shared rubric: `_SHARED-RUBRIC.md`.
>
> **Grounding:** all load-bearing claims fetched live (June 2026) from `github.com/lobehub/lobehub` (formerly `lobe-chat`; README, releases, LICENSE) and `lobehub.com/docs`. License claim spot-checked by the lead against the primary source (LICENSE file) — confirmed: LobeHub Community License (Apache-2.0-based) requires a **commercial license to develop and distribute a derivative work**.

## Summary

LobeChat has rebranded to **LobeHub** and grown from a chat app into a multi-platform agent harness (web + Electron desktop + **native iOS/Android apps**), built on **Next.js 16 / React 19 + tRPC + Zustand + Drizzle ORM/PostgreSQL**. It is a first-class **native MCP client** (stdio + HTTP, OAuth2), has the best **mobile** story (real native apps), and strong auth (Better Auth, broad SSO). The decisive caveats for the fabric: (1) **no server-initiated push** — it is request/response at the UI layer, no event bus, no custom-panel API; and (2) the **license requires a paid commercial license for any derivative work** — and adding panels / push hooks *is* a derivative work. So the fabric front-end fit is the weakest of the three on the dimension that matters most.

---

## 1. Architecture
- **Frontend:** Next.js 16 + React 19 (hybrid App Router + React Router DOM SPA). Ant Design + `@lobehub/ui`. State: **Zustand**. Data: SWR. API: **tRPC** (end-to-end typed). Styling: **antd-style (CSS-in-JS)**.
- **Backend:** Next.js API routes + tRPC routers. **Drizzle ORM + PostgreSQL 14+**. Redis optional. S3-compatible object storage.
- **Desktop:** Electron (macOS/Windows/Linux installers).
- **Transport:** chat stream = **SSE**. Docker Compose self-host has "WebSocket support" (per deploy-comparison table) but **no documented general-purpose server→client push bus** beyond SSE response streaming.
- Source: `lobehub.com/docs/development/start`, `lobehub.com/docs/self-hosting/start`

## 2. Extensibility
- **MCP (shipped, v2.x):** native MCP client — STDIO + HTTP/HTTPS transports; auth none/Bearer/OAuth2/custom-headers; Tools/Resources/Prompts; one-click desktop install + JSON config for self-host; 10,000+ marketplace tools. "Skills" is the per-agent tools tab. Source: `lobehub.com/docs/usage/community/mcp-market`
- **Legacy plugin gateway** (`chat-plugins-gateway`, 2023): superseded by MCP; `PLUGINS_INDEX_URL` still configurable.
- **Agent Groups:** parallel / sequential / debate topologies; June-2026 commits show active "supervisor reply when it parents to any council member" + "user-interaction tool for inbox agent" multi-agent work.
- **Custom UI / panels:** **no documented extension point.** `src/tools/` has built-in in-chat renderers (artifacts/inspectors) but registering external custom renderers requires forking the Next.js source.
- **MCP resource subscriptions:** an agent can be *notified* when MCP resource data changes — agent-driven, not fabric→UI panel push.

## 3. Model + Backend Support
70+ providers (OpenAI, Anthropic, Gemini, DeepSeek, Llama, Qwen, Mistral, Bedrock, Azure, Perplexity, Ollama…). Custom OpenAI-compatible base URLs supported. `SYSTEM_AGENT` uses `provider/model` (e.g. `ollama/deepseek-v3`). Per-agent default model. Source: `lobehub.com/docs/self-hosting/environment-variables/basic`

## 4. Multi-user / Auth
**Better Auth** (replaced Clerk): email/password, magic links, verification. Broad SSO: Google, GitHub, Microsoft, Apple, Cognito, Auth0, Authelia, Authentik, Casdoor, Cloudflare ZT, Keycloak, Logto, Okta, ZITADEL, generic OIDC, Feishu, WeChat. Redis for multi-instance sessions. **No documented RBAC** beyond email-domain allow-lists (`AUTH_ALLOWED_EMAILS`); workspace concept for teams. Source: `lobehub.com/docs/self-hosting/auth`

## 5. Mobile / PWA — **best of the three**
**Native iOS (App Store 6471212236) and Android (Google Play + APK)** apps, plus macOS/Windows desktop and web. Cross-device account sync. **But:** native mobile apps point at the **cloud** (`app.lobehub.com`) — no documented way to point them at a **self-hosted** server. Self-hosted mobile = responsive **browser** only. Source: `lobehub.com/docs/usage/getting-started/get-lobehub`

## 6. Theming / Branding
- Logo override via `NEXT_PUBLIC_BRAND_LOGO` env var (no code).
- Brand name + other constants live in `src/const/branding.ts` → **editing requires code + rebuild**, and a Jan-2026 maintainer response (issue #11880) states **"modifying branding code is restricted to commercial license holders; for commercial use, contact the LobeHub team."**
- Theme via antd-style CSS-in-JS — no flat-CSS theming API; visual changes are source-level.

## 7. Fork / Extend Difficulty
Modern TS stack but **higher friction than a plain React app**: hybrid **App Router + React Router** is unusual; tRPC means API changes regenerate typed clients; CSS-in-JS makes theming code-level; very large codebase shipping **multiple times/day** (real merge-conflict risk on a fork). Adding a genuinely new UI area needs Zustand slices + new route/layout files + core layout edits. **And** the commercial-derivative-license restriction makes any substantial fork a legal as well as technical undertaking. Source: `lobehub.com/docs/development/start`

## 8. License (HIGHEST-stakes — verified by lead against primary source)
**LobeHub Community License** (Apache-2.0 + additional conditions):
> *"a. LobeChat may be utilized commercially... **without modifying the source code.** b. a commercial license must be obtained from the producer **if you want to develop and distribute a derivative work based on LobeChat.**"* Producer may "adjust the open-source agreement to be more strict or relaxed as deemed necessary." Contact: hello@lobehub.com.

**Implication:** run-as-is commercially = OK. **Any** derivative (fork, added panels, server-push hooks, branding changes beyond the logo env var) = **commercial license required**. Directly hits the fabric use-case, which *requires* derivative work. Source: `raw.githubusercontent.com/lobehub/lobe-chat/main/LICENSE`

## 9. Maturity / Community
79k stars, 15.5k forks. Latest stable v2.2.8 (June 22 2026); canary releases multiple times/day. Backed by **LobeHub LLC** (commercial, monetises a cloud SaaS), full-time core team (arvinxx). LLC holds all license rights + the explicit "may tighten the license" clause. Active Discord/Discussions. Source: `github.com/lobehub/lobehub/releases`

## 10. MCP Support
**Native MCP client, fully shipped (v2.x).** Discovers/manages MCP servers, routes agent requests, handles auth/permissions. Transports: **STDIO + HTTP/HTTPS**; OAuth2 + Bearer. 10,000+ marketplace tools; one-click desktop install / JSON config self-host. Resource-subscription notifications exist (agent-side). Source: `lobehub.com/docs/usage/community/mcp-market`

---

## The 4 Use-Case Priorities

### (a) Extensibility / inbound-message surfacing — **THE DISCRIMINATOR: Weak**
Request/response at the UI layer. **No documented server-initiated push bus, no custom-panel slot, no event-injection API, no widget/iframe concept.** MCP resource-subscriptions notify an *agent* (→ next user turn), not the UI panel autonomously. Genuine fabric→UI push requires **forking the Next.js source** (new Zustand slices, components, WS/SSE handling, route/layout) — *and* that fork needs a **commercial license**. Concretely: `src/tools/` renders in-chat tools but exposes no external-renderer registration; MCP is outbound (agent→tool), not inbound (service→panel).

### (b) External call-out to fabric HTTP/MCP — **Strong (non-discriminating)**
Native custom OpenAI-compatible base URL + MCP HTTP — configuration, not code.

### (c) Mobile — **Strong (cloud) / Partial (self-hosted)**
Real native iOS/Android apps for the cloud; self-hosted mobile is browser-only.

### (d) Code-extension cleanliness — **Partial**
Modern, well-typed, well-organised — but hybrid router + CSS-in-JS + multiple-ships-per-day + the commercial-derivative restriction make UI forking the highest-friction of the three. MCP-tool extension is clean; UI extension is not.

---

## Bottom line for the fabric use-case
**Biggest strength:** the most polished, best-resourced product of the three — native MCP, true native mobile apps, strong SSO, commercial-team velocity; the outbound call-out path is trivially satisfied.
**Biggest gap:** it **cannot** be a fabric front-end for server-initiated push without a significant fork — and that fork immediately hits the **commercial-derivative-license** wall (paid license from LobeHub LLC). For "the fabric pushes channel/member content into custom panels," LobeHub is a polished chat box that must be polled or deeply forked; **neither path is clean**, and the discriminating requirement is a hard architectural + legal gap that configuration cannot bridge.
