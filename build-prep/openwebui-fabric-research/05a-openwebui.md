# 05a — Open WebUI: Self-Hosted Chat-UI Platform Research

> Part of the chat-UI platform evaluation for the Company fabric front-end. Companion files: `05b-lobechat.md`, `05c-librechat.md`, `05d-comparison.md`. Shared rubric: `_SHARED-RUBRIC.md`.
>
> **Grounding:** all load-bearing claims fetched live (June 2026) from `github.com/open-webui/open-webui` (README, LICENSE), `docs.openwebui.com`, and `github.com/open-webui/mcpo`. License + MCP claims spot-checked by the lead against the primary source (LICENSE file + the MCP docs page) — both confirmed verbatim.

## Summary

Open WebUI is the most-starred (143k+) and most-shipped (163 release tags) self-hosted AI chat platform, built on **SvelteKit (frontend) + Python/FastAPI (backend)**. It has the richest in-process plugin model of the three candidates (Tools, Pipe/Filter/Action Functions), **native MCP** (Streamable-HTTP, since v0.6.31), and — uniquely — a documented **WebSocket event-push channel** (`__event_emitter__`) plus a REST event-callback endpoint that lets tools push content into a live chat. The decisive caveat: the event push is **scoped to a user-initiated chat/message context** — fully unsolicited server-push into an arbitrary custom panel still needs a Pipe Function or a SvelteKit fork. And the **LICENSE carries a branding-protection clause** (Clause 4) that blocks white-labeling above 50 users without an enterprise license.

---

## 1. Architecture
- **Frontend:** SvelteKit / TypeScript (Node 22.10+), Vite build, static assets served by the backend. Dev server `:5173`.
- **Backend:** Python / FastAPI, fully async, Python 3.11/3.12. Dev server `:8080`, auto-generated API docs at `/docs`.
- **Data store:** SQLite default; PostgreSQL for HA. Vector DBs: ChromaDB + PGVector (maintained), Qdrant/Milvus/Elasticsearch (community).
- **Transport:** REST + **WebSocket** for the event/streaming layer; SSE streams LLM responses. The `__event_emitter__` helper pipes events over WebSocket to the connected client.
- **Scaling:** Redis sessions, multi-worker/multi-node, Kubernetes/Helm, S3/GCS/Azure blob, OpenTelemetry.
- Source: `docs.openwebui.com/getting-started/advanced-topics/development`, `docs.openwebui.com/features`

## 2. Extensibility
Five named extension points (all in-process Python except the external server types):

| Type | Runs | Does |
|---|---|---|
| **Tool** | backend in-proc | Python fn the LLM can call; has `__event_emitter__` |
| **Pipe Function** | backend in-proc | Appears as a selectable model; handles the full completion |
| **Filter Function** | backend in-proc | `inlet`/`outlet`/`stream` hooks on every message; inject/transform |
| **Action Function** | backend in-proc | Per-message buttons running custom Python on click |
| **OpenAPI / MCP server** | external HTTP | Tool endpoints; gets chat/message IDs via headers for event callbacks |

- **Event system (the critical primitive):** in-process plugins `await __event_emitter__({...})` → WebSocket-pushed to the browser live. Event types include `chat:message:delta`/`message` (append), `replace`, `files`, `chat:title`, `chat:tags`, `citation`, `notification`, `status`. **External** tools can do the same via REST: `POST /api/v1/chats/{chat_id}/messages/{message_id}/event`, using the `X-Open-WebUI-Chat-Id` / `X-Open-WebUI-Message-Id` headers forwarded on the outbound call (`ENABLE_FORWARD_USER_INFO_HEADERS=True`). Source: `docs.openwebui.com/features/extensibility/plugin/development/events`
- **Channels:** persistent shared spaces with `@model` tagging, threads, reactions, access control — a real-time multi-participant surface with models as participants. Source: `docs.openwebui.com/features`
- **Pipelines** (separate worker container, OpenAI-compatible): officially **deprecated** in favour of in-process Functions. Do not build new work on it.

## 3. Model + Backend Support
Ollama (first-class), arbitrary **OpenAI-compatible base URL** (Admin → Connections, no fork), Anthropic/Vertex/vLLM via Pipe Functions, image gen (DALL-E/Gemini/ComfyUI), 9 vector DBs for RAG. Pointing it at the fabric's OpenAI-compatible API = configuration only.

## 4. Multi-user / Auth
Full RBAC (roles, groups, per-resource/per-model/per-channel permissions), SSO/OIDC/SAML/LDAP/AD, SCIM 2.0 provisioning, MFA, API keys. MCP-server registration is admin-only; OpenAPI tool access delegable per user/group. Source: `docs.openwebui.com/enterprise/security`

## 5. Mobile / PWA
- SvelteKit → responsive by construction. Voice/audio features (STT/TTS, "hands-free voice & video calls").
- A **desktop app** (`github.com/open-webui/desktop`) runs it natively without Docker.
- **No native iOS/Android app** confirmed in docs; mobile browser is the primary mobile story. Large real deployments (JGU Mainz, 30k+ users) imply mobile-browser works.
- **PWA installability not explicitly confirmed** in the live docs fetched — *unverified* (likely, given SvelteKit, but not stated).

## 6. Theming / Branding
CSS theming (colors/fonts) is allowed and unrestricted. **Name/logo/identity removal is restricted by Clause 4 of the LICENSE** (see §8): permitted only at ≤50 users in any rolling 30-day window, or with written permission, or with an enterprise license. The Enterprise page confirms: free use = original branding intact; white-label = enterprise license required.

## 7. Fork / Extend Difficulty
- **Clean path = in-process plugins**: server-side Python, well-documented API (`__event_emitter__`, `__event_call__`, valves, inlet/outlet/stream), no build step, one-click import. This is the idiomatic, low-friction extension route.
- **Deep frontend changes** (new top-level panels not tied to the chat message lifecycle) require modifying the SvelteKit/TypeScript frontend with a build pipeline — competent but non-trivial.
- Monorepo (`/backend/` + frontend), two-terminal dev. **Contribution friction:** discussion-first policy, PRs to `dev`, CLA required — divergent forks will face maintenance/sync burden. Source: `docs.openwebui.com/getting-started/advanced-topics/development`

## 8. License (HIGHEST-stakes — verified by lead against primary source)
**BSD-3-Clause structure + a material additional Clause 4** (added April 19 2025, v0.6.6+). The three standard BSD clauses are present verbatim; Clause 4 adds branding protection:

> *"...licensees are strictly prohibited from altering, removing, obscuring, or replacing any 'Open WebUI' branding... except: (i) deployments where the total number of end users... does not exceed fifty (50) within any rolling thirty (30) day period; (ii) ...prior written permission...; or (iii) ...a duly executed enterprise license..."* (full text in LICENSE)

- Practical: ≤50 users → full rebrand OK, no enterprise license. >50 users → cannot remove/alter branding without permission or a paid enterprise license.
- A fork from **v0.6.5** (last fully-permissive version) carries no branding restriction.
- `mcpo` (the MCP-to-OpenAPI proxy) is separately **MIT**.

## 9. Maturity / Community
143k+ stars, 20.5k+ forks, 163 tags, last main commit June 1 2026. Backed by Open WebUI Inc. (A16z OSS-AI grant, Mozilla Builders, GitHub Accelerator). Enterprise users incl. Samsung Semiconductor, Astellas, JGU Mainz (35k+). Founder-led (tjbck), tight governance (discussion-first + CLA). Active Discord. Source: `github.com/open-webui/open-webui`

## 10. MCP Support (HIGHEST-stakes — verified by lead against primary source)
**Native, production-supported, Streamable-HTTP only, since v0.6.31.** Configured Admin → External Tools, admin-only. *No native stdio/SSE* (browser/multi-tenant constraint) — for those, use **mcpo** (MIT) to expose any MCP server as an OpenAPI endpoint. Auth: None / Bearer / OAuth 2.1 (dynamic + static, with Dynamic Client Registration). Header templating `{{USER_ID}}`/`{{CHAT_ID}}`/etc. Docs explicitly recommend OpenAPI over MCP for enterprise (SSO/audit). External MCP/OpenAPI tools can push events back via the REST event endpoint. Source: `docs.openwebui.com/features/extensibility/mcp`

---

## The 4 Use-Case Priorities

### (a) Extensibility / inbound-message surfacing — **THE DISCRIMINATOR: Partial (strongest of the three)**
Open WebUI has a **genuine, documented WebSocket event-push system**. An in-process Pipe/Filter Function — or an external system via `POST .../event` with forwarded chat/message IDs — can push `chat:message:delta`, `notification`, content, files, etc. into the **currently-open chat** in real time, no SvelteKit fork. **Constraint:** the push path is **scoped to a user-initiated message context** (user sends → tool gets chat/message IDs → tool pushes back to *that* conversation). A fully unsolicited fabric push into an arbitrary custom panel, with no user turn, is **not a first-class primitive**. Channels is the closest native "shared surface" but is still a user-driven conversation, not a fabric-owned display. Custom sidebar/workspace panels require a frontend fork. → The best push foundation available, but request-scoped, not fabric-owned.

### (b) External call-out to fabric HTTP/MCP — **Strong (non-discriminating)**
Point at any OpenAI-compatible base URL or any MCP Streamable-HTTP server, zero code. Header templating gives the fabric per-request routing context.

### (c) Mobile — **Partial**
Responsive SvelteKit + voice features + desktop app. No confirmed native mobile app; PWA installability unverified from live docs. Mobile browser is the path.

### (d) Code-extension cleanliness — **Strong (in-process) / Partial (deep frontend)**
In-process Python plugin model is the cleanest extension surface of any candidate (no build, hot, documented). Deep frontend panels need SvelteKit skill + build, and the discussion-first/CLA governance adds fork-sync friction.

---

## Bottom line for the fabric use-case
**Biggest strength:** the `__event_emitter__` / REST event-callback system is the most sophisticated chat-level **push** mechanism among self-hosted chat UIs — combined with native MCP/OpenAPI call-out and the Channels surface, it has the most fabric-ready primitive set, *especially* if the fabric pattern is "supervisor replies to a user turn with live-streamed structured output."
**Biggest gap:** (1) the **branding clause** is a hard white-label gate above 50 users (enterprise license or fork from v0.6.5); (2) truly **unsolicited** server-push into arbitrary panels — content with no user turn — still needs a Pipe Function or a SvelteKit fork. The push is real and powerful but **request-scoped, not fabric-owned**.
