# OpenWebUI Customization & Extension — Research for Fabric Integration

**Scope of this report:** what OpenWebUI lets you customize out-of-the-box, and every code-level extension mechanism — ranked by fit for wiring OpenWebUI to an **external custom multi-agent fabric** (call an external HTTP/MCP API + surface inbound messages + add a custom members/channels panel).

**Grounding (evidence basis):**
- **LOCAL INSTALL** — `open-webui` **v0.8.12** (pip), source at `/home/tim/openwebui-venv/lib/python3.11/site-packages/open_webui/`. Every claim below about routers, the channels webhook, and the plugin loader is verified by reading **this** source directly.
- `/home/tim/vi-openwebui/` is a prior deploy attempt — `Dockerfile` + `fly.toml` + theme PNGs + PWA manifest (not a source tree). **⚠ Version divergence:** that Dockerfile is `FROM ghcr.io/open-webui/open-webui:main` — **unpinned, tracks `:main` (latest)**, which is NOT the v0.8.12 I verified against. So the verified source and the likely deploy target can differ. This matters specifically for the inbound channel webhook (the load-bearing finding), which is undocumented and therefore could differ across versions. **Recommendation: pin the deploy image to a known-good version and smoke-test the inbound webhook on that exact image before building on it.**
- **LIVE DOCS** — docs.openwebui.com (current docs track ~v0.9.x). **Drift note:** docs describe a *newer* version than the installed one, so a few doc-described features (native MCP "External Tools", the knowledge-sync tool) may differ in v0.8.12. Conversely, the **inbound channel webhook is present and complete in installed v0.8.12 code but NOT documented** (see §1, "Verify before relying"). Cross-check by use on the *exact* image you deploy.

---

## TL;DR — the decision

The three requirements have **three different best-fit mechanisms**; a single flat ranking would mislead. The headline is that OpenWebUI already ships a **Discord-style real-time Channels substrate** (`routers/channels.py` + `socket/main.py` + a `src/lib/components/channel/` UI), and it solves the two hardest requirements — **inbound push** and the **members/channels panel** — *natively, without a fork*:

| Requirement | Best-fit mechanism | Fork needed? |
|---|---|---|
| **Outbound** — fabric receives a user's message, runs agents, streams a reply | **Pipe Function** (fabric registered as a "model"), OR point OpenWebUI at the fabric as a **custom OpenAI-compatible endpoint** (zero plugin code) | No |
| **Inbound** — fabric pushes a message into the UI *unprompted* | **Channel inbound webhook** — `POST /api/v1/channels/webhooks/{id}/{token}` (public, no user auth, custom name/avatar), pushed live over socket.io | No |
| **Members/channels panel** | **Native Channels UI** (use as-is), OR light frontend additions to it for fabric-specific affordances | No (for as-is) / Frontend fork (for custom affordances) |

**Recommended architecture:** make a **fabric channel** the home surface. The fabric is a channel member (and a `@`-mentionable model via a Pipe). The user talks in the channel; fabric agents push their messages in via the inbound webhook with per-agent names/avatars. This rides OpenWebUI's existing real-time messaging instead of fighting the request/response chat model — and matches the fabric's own "members/channels" mental model.

---

## PART A — Default (no-code) customization

All configured via Admin Panel or environment variables; no Python required.

| Area | What you can change | Where |
|---|---|---|
| **Models** | Add OpenAI-compatible & Ollama connections, per-model system prompt, params, capabilities, visibility, default model | Admin → Settings → Connections / Models; `OPENAI_API_BASE_URLS`, `OLLAMA_BASE_URLS` |
| **System prompts / presets** | Global system prompt; reusable **Prompt presets** (slash-command snippets) in the Workspace | Admin → Settings → Interface; Workspace → Prompts |
| **Banners** | Info/warning banners shown to all users | Admin → Settings → Interface (`WEBUI_BANNERS`) |
| **Branding / theme** | Name, favicon, login background, light/dark, accent color via CSS vars (the `vi-*.png` theme assets in `/home/tim/vi-openwebui/` are this) | `WEBUI_NAME`, custom CSS, `src/app.css` vars |
| **Workspace** | Models, Knowledge bases, Prompts, Tools, Functions surfaces for end-users | Workspace tab |
| **RAG / Knowledge** | Vector DB choice, chunking, hybrid search, embedding model | Admin → Settings → Documents |
| **Permissions / Auth** | RBAC, groups, OAuth/OIDC/LDAP, SCIM, per-feature user permissions (incl. `features.channels`) | Admin → Settings → Users |
| **Feature flags** | Toggle Channels (Beta), Notes, Evaluations, Image gen, Code interpreter, etc. | Admin → Settings → General |
| **~200+ env vars** | Almost everything above is also env-driven for headless config | `config.py` / `env.py` |

These are sufficient for *appearance, models, and access* but cannot wire in external logic, inbound push, or new panels. For that, use Part B.

---

## PART B — Extension mechanisms (the important part)

OpenWebUI is a **SvelteKit frontend + FastAPI/Python backend**. There are five extension layers, in increasing order of power and effort. Below, each is rated against our three requirements.

### B0. Custom OpenAI-compatible endpoint (NO plugin code) — outbound
The lowest-friction outbound option. If the fabric exposes an OpenAI-compatible `/chat/completions` (streaming SSE), register it under Admin → Connections as an "OpenAI API" base URL. The fabric then **appears as a model** in the picker with **zero plugin code**. (`main.py` line 1488 mounts `openai.router`; pipes/connections/pipelines all surface as models — line ~1559.)
- ✅ Best for: simplest possible outbound wiring if the fabric can speak OpenAI's wire format.
- ❌ No inbound, no panel, no per-agent identity, no logic injection beyond what the fabric returns.

### B1. TOOLS — model-callable Python functions (`routers/tools.py`, `utils/tools.py`)
A `Tools` class whose methods are exposed to the model as function-calling tools; docstrings + type hints become the JSON schema. Admin-managed; `Valves`/`UserValves` give config UI. Can call external HTTP (`httpx.AsyncClient`) or MCP servers.
```python
class Tools:
    class Valves(BaseModel):
        fabric_url: str = Field("http://fabric.local")
    async def ask_fabric(self, query: str) -> str:
        """Route a query to the multi-agent fabric. :param query: the question"""
        async with httpx.AsyncClient() as c:
            r = await c.post(f"{self.valves.fabric_url}/ask", json={"q": query})
        return r.text
```
- ✅ Best for: letting the *currently-selected model* delegate sub-tasks to the fabric mid-conversation.
- ❌ Pull-only (model decides when to call); no inbound; no panel. The fabric is a *subordinate tool*, not the conversational surface.

### B2. FUNCTIONS — in-app Python plugins (`functions.py`, `routers/functions.py`, `utils/plugin.py`)
Three subtypes, loaded by `load_function_module_by_id()` (`utils/plugin.py:248`), which detects a top-level `Pipe`, `Filter`, or `Action` class (line 281 returns `module.Pipe(), 'pipe', ...`). Admin pastes/uploads Python in the UI; runs **in-process** in the main server.

- **PIPE** — *registers AS A MODEL*. Implement `pipe(self, body, ...)` (and optionally `pipes()` to expose multiple "models" = a manifold). Returns a string, an OpenAI dict, or an **async generator to stream**. **This is the primary in-app outbound integration point** — a Pipe can stream directly from the fabric's HTTP/MCP API via `httpx.AsyncClient.stream()`, and the fabric becomes a selectable AND `@`-mentionable model.
  ```python
  class Pipe:
      class Valves(BaseModel):
          fabric_url: str = Field("http://fabric.local")
      async def pipe(self, body: dict, __event_emitter__=None):
          async with httpx.AsyncClient(timeout=None) as c:
              async with c.stream("POST", f"{self.valves.fabric_url}/chat",
                                   json=body) as r:
                  async for line in r.aiter_lines():
                      yield line   # OpenAI SSE chunks
  ```
- **FILTER** — `inlet` (before model), `outlet` (after), `stream` (per-chunk) hooks, priority-ordered. For moderation, logging, injecting fabric context into the prompt, observability. Middleware only — modifies data, adds no UI.
- **ACTION** — adds a **button under a message**. On click, runs server logic and can use `__event_call__` for `confirmation`/`input` dialogs and `__event_emitter__` for `status`/`notification`/embedded HTML. **Crucially: Actions can ONLY add message-toolbar buttons — they cannot add a sidebar panel or a top-level page.**

**Event system (`__event_emitter__` / `__event_call__`):** Functions can emit `status`, `notification`, `chat:message:delta`, `chat:message`, `confirmation`, `input`, `embeds` (HTML iframe), `chat:title`, etc. — BUT these are scoped to *the active chat turn that invoked the function*. **They are not a general "push into the UI from outside" mechanism** — a Function only runs in response to a user sending a message. That distinction is the whole reason inbound needs the channel webhook (§B-inbound), not a Function.

### B3. PIPELINES — separate OpenAI-compatible middleware server (`routers/pipelines.py` mounts the client; the server is a SEPARATE repo)
`open-webui/pipelines` is **not** part of the pip package — it's a standalone service (default `:9099`, Docker `ghcr.io/open-webui/pipelines:main`) that OpenWebUI talks to as just another "OpenAI API" connection. Same `Pipe`/`Filter` model as Functions, plus `on_startup`/`on_shutdown`, but runs **out-of-process** so it can carry **arbitrary heavy Python deps** (LangChain/LangGraph, vector libs) and **long-running logic** without blocking the main server. The repo's `examples/integrations/` includes **LangGraph, N8N, Dify, Flowise** adapters — i.e. it is *purpose-built* for fronting an external multi-agent system.
- ✅ Best for: a robust, isolated **outbound adapter** to the fabric — especially if the adapter is heavy/long-running or needs deps you don't want in the main image. Functionally a Pipe, but deployment-isolated.
- ❌ Still outbound/pull-only; no inbound push; no panel.

### B4. CODE FORK — modify the SvelteKit + FastAPI source
Full source only in the github repo `open-webui/open-webui` (the pip `frontend/` dir is built assets, not editable source). Layout: frontend in `src/` (`routes/`, `lib/components/`, `lib/apis/`, `lib/stores/`), backend in `backend/open_webui/`.
- **Add a backend route:** drop `routers/fabric.py`, then `app.include_router(fabric.router, prefix='/api/v1/fabric')` in `main.py` (the exact pattern used for all 25+ routers, e.g. `main.py:1504` for channels).
- **Push real-time inbound:** `socket/main.py` exposes `sio` plus helpers `emit_to_users()`, `enter_room_for_users()`, `get_user_ids_from_room()` (lines 283/299/268). Emit pattern: `await sio.emit('events:channel', data, to=f'channel:{id}')`.
- **Add a frontend panel/page:** new route `src/routes/(app)/fabric/+page.svelte`, component under `src/lib/components/fabric/`, API client in `src/lib/apis/fabric/`, a sidebar entry in `src/lib/components/layout/Sidebar.svelte`, and a socket listener `$socket.on('events:fabric', ...)`.
- **Dev/build:** frontend `npm run dev` (:5173), backend `sh backend/dev.sh` (:8080); build bundles `build/` into the backend static dir. Fork from `dev`, add `upstream` remote, rebase periodically.
- ✅ Best for: deep custom panels and anything the plugin layers structurally cannot do.
- ❌ Highest effort + ongoing rebase/maintenance burden against a fast-moving upstream. **Only fork for what the native Channels substrate + plugins genuinely cannot cover.**

---

## The linchpin: the native CHANNELS substrate solves inbound + panel without a fork

This is the most decision-relevant finding, verified line-by-line in `routers/channels.py`, `models/channels.py`, and `socket/main.py` (installed v0.8.12).

**What Channels is:** a Discord/Slack-style real-time messaging feature (types: standard / group / dm). Admin-created (Beta; enabled via Admin → General "Channels (Beta)"; gated by `ENABLE_CHANNELS` and the `features.channels` user permission — `channels.py:138-147`). It has its own frontend (`src/lib/components/channel/` — `Channel.svelte`, `Messages.svelte`, `MessageInput.svelte`, `Thread.svelte`, `PinnedMessagesModal.svelte`, **`WebhooksModal.svelte`**), a members list, threads, reactions, and pinned messages — **this IS the "members/channels panel."**

**Real-time push:** every message insert emits live to all connected channel clients:
`await sio.emit('events:channel', event_data, to=f'channel:{channel.id}')` (`channels.py:1055`). The frontend `Channel.svelte` listens on `events:channel` and renders new/updated/deleted messages instantly. No polling.

**Models as channel participants:** `@`-mentioning a model in a channel triggers `model_response_handler` (`channels.py:845-1013`), which builds thread history into a system prompt and runs a full `generate_chat_completion`, posting the reply back as a threaded message. **Because a Pipe registers as a model, the fabric can be a first-class `@`-mentionable member of a channel.**

**★ Inbound push — the hard requirement — is solved by a built-in PUBLIC webhook:**
`POST /api/v1/channels/webhooks/{webhook_id}/{token}` (`channels.py:1751`) — docstring: *"Public endpoint to post messages via webhook. No authentication required."* It:
1. Validates the per-webhook secret `token` (generated as `secrets.token_urlsafe(32)` at creation — `models/channels.py:914`; looked up by `get_webhook_by_id_and_token`).
2. Inserts the message with a **custom webhook identity** (name + `profile_image_url`) carried in `meta.webhook` — so each fabric agent can post under its own name/avatar (`channels.py:1774-1790`, model fields at `models/channels.py:185-212`).
3. Emits it live over socket.io to every connected channel client (`channels.py:1816`).

So an **external fabric agent posts a message into the live UI** with just an HTTP POST to a per-channel webhook URL holding a secret token — **no fork, no user session, no auth handshake.** Webhooks are created per-channel by a channel manager via `POST /api/v1/channels/{id}/webhooks/create` (or the `WebhooksModal` UI). This is the inbound + identity mechanism.

> **⚠ Asymmetry — the webhook path does NOT auto-summon models.** Compare the two message paths in the same file: the *user* path `post_new_message` (`channels.py:1088`) schedules a `background_handler` → `model_response_handler`, so a user message that `@`-mentions a model auto-triggers a reply. The *public webhook* path `post_webhook_message` (`channels.py:1751`) does **NOT** — it inserts + emits only. **A fabric-posted (webhook) message that `@`-mentions an OpenWebUI model will NOT chain into a model response.** For the recommended loop this is fine and arguably desirable: the fabric generates its own content and pushes it via webhook, while the *user→fabric* direction goes through `@`-mention→Pipe (which DOES auto-summon). But the team must design the loop knowing the webhook direction is push-only and will not fire OWUI's model pipeline — otherwise a loop expecting it to chain will silently not fire.

> **Verify before relying:** this inbound channel webhook is **present and complete in installed v0.8.12 code** but is **NOT in the live docs** (docs.openwebui.com/features/channels does not mention inbound webhooks). It is real but ahead of / undocumented in the public docs — and the deploy image (`:main`) may differ from v0.8.12. Confirm by use on the **exact image you deploy**: create a channel + webhook, `curl` a message to `POST /api/v1/channels/webhooks/{id}/{token}`, confirm it renders live with the custom name/avatar. Treat as a code-verified capability pending a live smoke-test, not a documented contract.

---

## REST API (for any external-to-OpenWebUI calls)

Auth: **API key / Bearer token** (per-user, inherits that user's permissions) or JWT; an `x-api-key` header is supported behind a proxy. Key endpoints: `POST /api/chat/completions` (OpenAI-compatible; the channels code uses the internal `generate_chat_completion`), `/api/models`, `/api/v1/files/`, `/api/v1/knowledge/...`, `/api/v1/retrieval/...`, and the full `/api/v1/channels/...` surface above (create channel, post message, list members, manage webhooks). Outbound user webhooks exist for notifications (`WEBHOOK_URL` / per-user `notifications.webhook_url`, used in `send_notification`, `channels.py:818`); there is no general inbound webhook *other than the channel webhook* documented.

---

## Final ranking by fit for the fabric-integration use-case

1. **Native Channels + inbound webhook (no fork)** — uniquely satisfies inbound push AND the members/channels panel, the two hardest requirements, with the fabric's own "members/channels" mental model. The recommended spine. Verify the undocumented inbound webhook by use on v0.8.12.
2. **Pipe Function (fabric-as-a-model)** — the clean outbound path; makes the fabric a selectable AND `@`-mentionable channel participant. Pairs with #1.
3. **Pipelines (separate server)** — same as #2 but out-of-process; choose over #2 when the adapter is heavy/long-running or needs isolated deps (LangGraph-style). Outbound only.
4. **Custom OpenAI-compatible endpoint (no code)** — lowest-friction outbound if the fabric speaks OpenAI's wire format; no inbound/panel/identity.
5. **Tools / Filters** — supporting roles: Tools let a model delegate to the fabric; Filters inject context / observe / moderate. Neither carries the conversation or pushes inbound.
6. **Code fork (SvelteKit + FastAPI)** — only for custom panels/affordances the native Channels UI can't express; highest effort + rebase burden. Reserve for genuine gaps after #1–#3.
