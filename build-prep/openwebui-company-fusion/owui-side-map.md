---
type: map
title: OpenWebUI Architecture & Customization Surface — Donor/Host Side of the Company Fusion
subject: open-webui 0.9.6 (installed at /home/tim/openwebui-venv/lib/python3.11/site-packages/open_webui)
version_installed: 0.9.6  (PyPI METADATA → Version: 0.9.6; CHANGELOG [0.9.6] - 2026-06-01)
provenance: STOCK UPSTREAM open-webui/open-webui — NOT a private fork (verified via bundled CHANGELOG.md issue/PR cites)
posture: nothing here is "complete" or "the intended design" — this maps what IS in the installed code + live docs, flags fragile/version-specific bits, and distinguishes supported-extension from fork-only
created: 2026-06-28
evidence_basis: installed Python source (file:line, Observed) + live docs.openwebui.com (URLs). Frontend is a compiled SvelteKit bundle (no .svelte source in venv) — UI claims are Inferred from backend wiring + docs, flagged as such.
---

# OpenWebUI 0.9.6 — Donor-Side Architecture Map

> **Reading note (for the fusion).** OpenWebUI's value is NOT one monolith — it is a set of separable, mostly-clean subsystems bolted to a compiled chat frontend. The strong parts (extension model, channels, RAG factory, identity stack, OpenAI-compat API) are backend-resident and harvestable. The weak parts are (a) the compiled frontend you cannot edit without a fork, (b) a half-finished JSON→relational normalization, and (c) the legacy Pipelines server that upstream itself now deprecates. The LICENSE caps branded reuse at 50 users. Details + evidence below.

---

## 0. PROVENANCE — resolved before the harvest list

Two of the sub-investigations independently suspected this was a private fork (because of `automations`, `calendar`, `terminals`, `skills`, `notes`, `access_grants`, normalized `chat_message`, `@model`-in-channels). **That suspicion is wrong.** The bundled `CHANGELOG.md` attributes every one of these to upstream `open-webui/open-webui` with real issue/PR/commit numbers:

- `[0.9.6] - 2026-06-01` — channel streaming + full chat pipeline in channels (line 150), per-chat skills toggle (#25036/#25037), channel access control (#24725), terminal/calendar/notes fixes.
- `[0.9.0] - 2026-04-20` — scheduled chat **automations** (#23303), official Desktop app (#8262), the 0.9.0 plugin-migration breaking changes.

**Conclusion: this is stock upstream 0.9.6.** Every harvest candidate below is therefore tagged `[upstream]` — none is fork-private. (The agents simply didn't know how far upstream had advanced.) This matters: crediting OpenWebUI for these is correct, and they are reproducible from the public repo.

---

## 1. THE EXTENSION MODEL — the single highest-value fusion surface

There are **three** in-process extension surfaces (Functions, Tools, and a now-legacy Pipelines server). All in-process plugins share one loader.

### 1.0 The shared loader — `utils/plugin.py` (NO sandbox)
Plugin source is a **Python string stored in a DB column and `exec`'d in the host process**. There is no isolation.

- `load_function_module_by_id()` `utils/plugin.py:250` — reads `content` from the `function` DB row (`:255`), runs `replace_imports()` (`:185-199`, rewrites legacy `from utils`→`from open_webui.utils` **and mutates the stored DB content**), writes a `NamedTemporaryFile`, then **`exec(content, module.__dict__)`** (`:277`). Dispatches by top-level class name: `Pipe`→pipe, `Filter`→filter, `Action`→action (`:282-287`); none → raises `'No Function class found'` (`:289`).
- On any load error the function is **auto-deactivated** in the DB (`is_active=False`, `:295`) — silent flip.
- `load_tool_module_by_id()` `:204` — same, requires class `Tools` (`:238`).
- **Imports unrestricted.** A plugin runs *as the server*: full DB, filesystem, network, env, other-model reach. Treat any installed Function/Tool as trust-equivalent to a server fork.
- **`pip` at load** — frontmatter `requirements:` triggers `subprocess pip install` (`:410`), gated by `ENABLE_PIP_INSTALL_FRONTMATTER_REQUIREMENTS` + `OFFLINE_MODE`; tool requirements only for admin-owned tools (`:441`).
- **Live re-exec**: default `load_from_db=True` (`:343`) re-reads+re-`exec`s on every inlet/outlet call (edits apply live); BUT `stream` reads from cache (`utils/filter.py:75`) — an edited `stream()` won't apply until cache refresh. Real behavioral asymmetry.
- DB schema — `models/functions.py:18-33` (`Function`: `id, user_id, name, type(pipe|filter|action), content, meta, valves, is_active, is_global, ...`); `models/tools.py:20-32` (`Tool`, + `specs` JSON + `access_grants`).
- Live doc: <https://docs.openwebui.com/features/extensibility/plugin> ("Tools, Functions, Pipes, Filters, and Pipelines execute arbitrary Python code on your server. This is by design.")

### 1.1 Valves / UserValves (config pattern, all surfaces)
- **`Valves`** — nested Pydantic model, admin-configured, stored in `Function.valves` JSON, hydrated per-run (`functions.py:55-66`, `filter.py:86-88`, `actions.py:65-67`). A Filter's `Valves.priority:int` controls ordering (`filter.py:26-28,59`).
- **`UserValves`** — per-user, stored in `user.settings['functions']['valves'][fn_id]` (`models/functions.py:345-384`), injected as `__user__['valves']` only when the handler names `__user__`.
- Dynamic dropdown options resolvable at schema-fetch via `resolve_valves_schema_options()` (`utils/plugin.py:25-146`), surfaced at `GET /id/{id}/valves/spec` (`routers/functions.py:404-419`).
- **Injected params are signature-sniffed** (`inspect.signature`, e.g. `functions.py:194`) — a plugin opts into each `__dunder__` by naming it; a typo silently drops it. The dunder set is version-specific to 0.9.6.

### 1.2 Pipe / Manifold — `type='pipe'`, driver `functions.py` → **custom models**
- Class `Pipe` with `pipe(self, body, ...)` (`functions.py:286-293`).
- **Manifold**: module also defines `pipes` (list / sync / async callable) → exposes **multiple sub-models** (`:84-121`), sub-id `f'{pipe.id}.{sub_id}'`. This is the **dynamic, runtime-computed model-list** injection point (e.g. a function that queries a provider and returns N models).
- **THIS is how custom models enter the model picker**: `get_function_models()` (`:71-144`) turns every active pipe into `{'id','name','object':'model','owned_by':'openai','pipe':{...}}`.
- Return types: `str`, sync gen/iter, `AsyncGenerator` (→ SSE `StreamingResponse`), `StreamingResponse`, `dict`, pydantic `BaseModel` (`:289-341`) — **full streaming**.
- Injected to `pipe()` (`:252-266`): `__event_emitter__ __event_call__ __chat_id__ __session_id__ __message_id__ __task__ __task_body__ __files__ __user__ __metadata__ __oauth_token__ __request__ __tools__`.
- Doc: <https://docs.openwebui.com/features/extensibility/plugin/functions/pipe> ("Pipe Function: Create Custom Agents/Models").

### 1.3 Filter — `type='filter'`, driver `utils/filter.py` → **pre/post/stream hooks**
- Class `Filter` with up to three methods:
  - `inlet(self, body, ...)` — **pre-request hook**, mutates outgoing payload (`middleware.py:2539`).
  - `outlet(self, body, ...)` — **post-response hook** (`middleware.py:3274/3361/3375`).
  - `stream(self, event, ...)` — **per-chunk hook** (note: first arg is `event`, `filter.py:95-96`; `middleware.py:3972,5232,5244`).
- Generic dispatch `process_filter_functions()` (`filter.py:66-134`); ordering `get_sorted_filter_ids()` (`:21-61`) = global filters (`is_global`) + per-model `meta.filterIds`, sorted by `Valves.priority`.
- **Toggle chips**: a Filter with truthy `toggle` attr (`filter.py:42`) becomes a user-toggleable switch in the chat bar (persisted `routers/functions.py:216,333`).
- `self.file_handler=True` → inlet strips uploaded files (filter owns file handling) (`filter.py:82-83,128-132`).
- Doc: <https://docs.openwebui.com/features/extensibility/plugin/functions/filter>.

### 1.4 Action — `type='action'`, driver `utils/actions.py` → **custom message buttons**
- Class `Action` with `action(self, body, ...)` (`chat_action()` `actions.py:19-133`). **This is the custom message-action-button mechanism** — each active action renders a button under a message; click invokes `action()`. Sub-actions via dotted id (`:20-23`).
- Injected (`:78-84`): `__model__ __id__ __event_emitter__ __event_call__ __request__` (+`__user__`/valves).
- Can mutate the message, and **emit rich UI** — returning HTMLResponse/tuple pushes an `embeds` event to the client (`:109-128`); via `__event_call__` open confirm/input prompts.
- Doc: <https://docs.openwebui.com/features/extensibility/plugin/functions/action>; rich UI: <https://docs.openwebui.com/features/extensibility/plugin/development/rich-ui>; events: <https://docs.openwebui.com/features/extensibility/plugin/development/events>; reserved args: <https://docs.openwebui.com/features/extensibility/plugin/development/reserved-args>.

### 1.5 Tools — model-callable functions — `utils/tools.py`, `routers/tools.py` (931 lines)
- Class `Tools`; each public method (`get_functions_from_tool()` `:786-795`) → one callable tool. Specs auto-generated from **type hints + reST docstring** (`convert_function_to_pydantic_model()` `:707-746`, via langchain `convert_to_openai_function`), stored in `Tool.specs`.
- Dunders **partially-applied and stripped from the LLM-visible signature** (`get_async_tool_function_and_apply_extra_params()` `:168-204`); `__`-prefixed args removed from the JSON spec (`:279-281`).
- **Native vs default function-calling**: same `callable` either way — native hands specs to the model API; default prompts the model and parses. `self.citation=True` → source citations; `self.file_handler` flag like filters.
- Attach via model `meta.toolIds`; access-checked via `AccessGrants` (`:234-250`).
- **External tool servers in the SAME interface**: OpenAPI (`server:` prefix), **MCP**, and `terminal:` servers resolved into one `tools_dict` (`:321-427`, `execute_tool_server()` `:1377`, `oauth_2.1` auth). 
- **Built-in tools** `get_builtin_tools()` `:430-649` — web_search, image gen/edit, code interpreter, memory, knowledge query, notes, **channels**, calendar, automations, tasks — each gated by global-config AND model-capability AND user-permission.
- Docs: <https://docs.openwebui.com/features/extensibility/plugin/tools> · <https://docs.openwebui.com/features/extensibility/plugin/tools/development> · MCP/OpenAPI: <https://docs.openwebui.com/features/extensibility/plugin/tools/openapi-servers/open-webui>.

### 1.6 Pipelines — the separate server — **OFFICIALLY LEGACY/DEPRECATED**
- Not `exec`'d in-process — a **standalone OpenAI-compatible HTTP server** registered as an OpenAI connection (`routers/pipelines.py`). Detected when a connection's model list carries a `pipelines` key (`:191-206`).
- Filter pipelines called over HTTP per request: `POST {url}/{filter_id}/filter/inlet` / `/filter/outlet`, body `{user, body}` (`:85-92,149-156`), wired at `middleware.py:2531/3361` (runs BEFORE in-process Function filters). They do **not** receive `__event_emitter__`/`__request__`/DB.
- Admin upload `/upload` forwards a `.py` to the external server (`:209-260`).
- **Can do what Functions can't**: out-of-process / different-host / heavy-dep / GPU / runtime-isolated, independently restartable.
- **BUT upstream now deprecates them**: <https://docs.openwebui.com/features/extensibility/pipelines> — "Pipelines are legacy and are no longer recommended. They predate the in-process Functions (Pipes, Filters, Actions) and Tools system, which now covers the same use cases." Also <https://docs.openwebui.com/features/extensibility/pipelines/pipes> and `/pipelines/filters`. → **For the fusion: do NOT harvest Pipelines; the in-process Functions model superseded it.**

### Capability → mechanism (direct answer)
| Capability | Mechanism | Evidence |
|---|---|---|
| Custom models in picker | **Pipe/Manifold Function** (or external OpenAI/Pipeline servers) | `functions.py:71-144,84-121` |
| Custom message buttons | **Action Function** | `utils/actions.py:19-133` |
| Pre-request hook | **Filter `inlet`** | `filter.py` via `middleware.py:2539` |
| Post-response hook | **Filter `outlet`** | `middleware.py:3274/3361/3375` |
| Per-chunk stream hook | **Filter `stream`** | `filter.py:95`; `middleware.py:3972,5232,5244` |
| Model tool-calling | **Tools** (in-proc / OpenAPI / MCP / terminal / built-in) | `utils/tools.py:221,430` |
| Toggle chips in chat bar | Filter with `toggle=True` | `filter.py:42` |

---

## 2. CHANNELS — a real Slack-style schema + AI-as-participant (the most novel surface)  [upstream]

7 tables (`models/channels.py`, `models/messages.py`) — not a thin chat wrapper.

- **`channel`** (`channels.py:40-65`): `id, user_id, type(None/''=standard|group|dm :45), name(lowercased :352), description, is_private, data, meta, created/updated/updated_by, archived_at/by, deleted_at/by`. Access NOT a column — in separate `access_grants` (`:83,260`).
- **`channel_member`** (`:97-124`): `role(manager), status(joined/left), is_active, is_channel_muted, is_channel_pinned, invited_at/by, joined_at, left_at, last_read_at` (drives unread).
- **`channel_file`** (`:157-170`): channel↔message↔file link, unique(channel_id,file_id).
- **`channel_webhook`** (`:186-200`): `name, profile_image_url, token (secrets.token_urlsafe(32) :938), last_used_at` — inbound bot identity.
- **`message`** (`messages.py:39-59`): `reply_to_id` (quote), **`parent_id`** (thread root — threads are **one-level flat**), `is_pinned/pinned_at/pinned_by`, content, data/meta. Webhook authors carry `meta.webhook.id`, role `'webhook'`.
- **`message_reaction`** (`messages.py:20-26`): emoji `name`, uniqueness per (message,user,name) in code (`:454-456`), aggregated `{name,users[],count}` (`:483-501`).

### Endpoints (`routers/channels.py`, under `/api/v1/channels`)
All gated by `check_channels_access` (ENABLE_CHANNELS + per-user `features.channels`, `:126-141`). List/create/DM-get-or-create, members add/remove (owner/admin), messages post/get/pinned/thread/update, reactions add/remove, delete, webhooks CRUD (manager/admin), and **`POST /webhooks/{webhook_id}/{token}` (`:1767`) — PUBLIC, unauthenticated** inbound ingress, body `{"content":"..."}`.

### AI-in-channel (the differentiator)  [upstream — CHANGELOG line 150]
`model_response_handler` (`:854-1018`): parses `@model` mentions (`<@M:id|label>` via `utils/channels.py:4-31`), builds thread history into a system prompt, and calls the **full chat-completion pipeline** (`CHAT_COMPLETION_HANDLER`, `:1013`) with `chat_id=channel:{id}` — **native+default function calling, built-in tools, user/MCP tools, filters, RAG knowledge injection**, identical to standard chat. Streams back via `_make_channel_emitter` (`:829-891`, throttled 0.15s) re-routing `chat:completion` token events into channel `message:update` emissions. Runs in a fire-and-forget BackgroundTask (`:1120`).

### Socket.IO (`socket/main.py`) — single inbound event name `channel_events`; room `channel:{id}`
- Inbound (`:471-503`): `typing` (re-broadcast, never persisted) and `last_read_at` (`:503`).
- Outbound to room `{channel_id, message_id, data:{type,data}, user, channel}`: `message` (`:1060` / webhook `:1832`), `message:reply` (`:1071,1602`), `message:update` (edits + **streaming AI tokens** `:1378`), `message:reaction:add/remove` (`:1440,1508`), `message:delete` (`:1579`), `channel:created` to `user:{id}` rooms on DM create.

### Value over plain chats
Real-time multi-user shared timeline · one-level threads · reactions · pins · per-member unread/mute/pin · members+roles · 3 access models (standard-ACL / private-group / DM) · **inbound webhooks with bot identity** · **multiple AI models as first-class streaming participants with full tools/RAG**.

### Fragile / beta flags (honest)
- Docs mark Channels **Beta** with a security warning (public channels visible to all instance users). <https://docs.openwebui.com/features/channels>
- Threads single-level only (no nesting). Typing ephemeral, no server timeout cleanup. **Public webhook endpoint fully unauthenticated** (token-in-URL, no HMAC/signature/visible rate-limit — URL *is* the password). AI response in a BackgroundTask with bare `except: log.exception` (`:1015,1112`) — failures swallowed (only generic "Error:" emitter path `:886-889`). Message delete is hard-delete (no soft-delete) though channel rows have `deleted_at`. Fixed 0.15s throttle, no backpressure config.
- UI: not in venv (compiled). Inferred Slack-like (sidebar list, threads pane, reaction picker, pinned view, unread badges) from router link-building (`:842-847`) + docs.

---

## 3. VOICE  [upstream]

Backend = `routers/audio.py`. The voice-CALL loop (mic capture, turn-taking, sentence-by-sentence playback) lives in the **compiled frontend** — backend is a stateless TTS↔STT pair the client loops.

- **TTS** `POST /speech` (`:579`) — SHA256-caches to `cache/audio/speech/{hash}.mp3` (`:597-606`); gated `chat.tts`. Engines (`_TTS_ENGINES :570`): `openai` (product-grade, merges `TTS_OPENAI_PARAMS`, auto-transcodes to MP3 `:417`), `elevenlabs` (**hardcoded** stability/similarity 0.5 `:444` — weak), `azure` (SSML), `transformers` (local SpeechT5, **hardcoded speaker idx 6799** `:506` — niche/weak), `mistral`. Edge-TTS/Kokoro/Chatterbox/openedai-speech all ride the `openai` engine via base-URL shim (not separate code).
- **`AUDIO_TTS_SPLIT_ON`** (default `'punctuation'`, `config.py:2447`) — the **streaming-TTS knob**: frontend splits the streaming LLM response on punctuation and fires `/speech` per chunk so audio starts before the message finishes. This + caching is the good UX.
- **STT** `POST /transcriptions` (`:1149`), gated `chat.stt`, MIME+ext allowlist + path-traversal defense. Engines (`:872`): local faster-whisper (`''`; `WHISPER_VAD_FILTER` default **False** = silence-trim only, not turn-taking VAD), `openai`, `deepgram`, `azure` (**only engine with diarization/maxSpeakers** `:801`), `mistral`. Preprocessing (`:1031`) converts→compresses→splits ≤20MB→transcribes chunks **concurrently** (`asyncio.as_completed :1064`). `web` engine = browser Web Speech API, never hits backend.
- **UX verdict**: streaming sentence-split TTS = product-grade; real conversational VAD/turn-taking + call/video mode = frontend-only (not in this package); backend VAD only whisper silence-trim, off by default.
- Docs: <https://docs.openwebui.com/features/chat-conversations/audio/speech-to-text/stt-config/> · <https://docs.openwebui.com/category/text-to-speech/>

---

## 4. MODELS / CONNECTIONS  [upstream]

- **Multi OpenAI-compat connections** (`routers/openai.py`): parallel arrays `OPENAI_API_BASE_URLS[]`, `OPENAI_API_KEYS[]`, `OPENAI_API_CONFIGS{}` (keyed by `str(idx)`, legacy by URL — **brittle dual-keying** threaded everywhere `:392,1118,...`). Per-connection: `enable, model_ids(allowlist, skips /models autodetect :404), connection_type, prefix_id(namespacing→groq.llama3 :448), tags, provider`. Queried **concurrently** (`asyncio.gather :422`). Anthropic first-class (`utils/anthropic`, `is_anthropic_url :41`). `/responses` endpoint + catch-all proxy `/{path:path} :1505`. Per-user cached (`@cached :488`).
- **Ollama** (`routers/ollama.py`): separate `OLLAMA_BASE_URLS[]`, normalized into the same dict shape (`utils/models.py:31-46`, `owned_by='ollama'`, `loaded` flag).
- **Dynamic model lists** via manifold pipes (§1.2). **Broken manifold silently yields no models** (exceptions→empty list `functions.py:98` — violates no-silent-failure).
- **Merged list** `utils/models.py`: `get_all_base_models :54` = function + openai + ollama (order matters); `get_all_models :72` overlays Arena models, workspace Models (override vs preset), attaches actions/filters (priority-sorted, batched prewarm), applies `DEFAULT_MODEL_METADATA`.
- **Model entity / presets** (`models/models.py:75`): `base_model_id` (None=override / set=preset), `params(ModelParams: temp/top_p/system-prompt)`, `meta(profile_image, description, capabilities, actionIds/filterIds/tags/knowledge/tools)`. Access via `AccessGrants` with **chained-base enforcement** (`has_base_model_access :406` — a preset can't bypass a restricted base). `BYPASS_MODEL_ACCESS_CONTROL` escape hatch.
- Docs: connect-a-provider/openai-compatible · <https://docs.openwebui.com/features/workspace/models> · <https://docs.openwebui.com/features/chat-conversations/chat-features/chat-params>

---

## 5. KNOWLEDGE / RAG — product-grade, wide  [upstream]

- **Data** (`models/knowledge.py`): `Knowledge` table (`:43`, the "collection"; file membership held in `meta` JSON — **no join table**, inconsistent with newer relational pattern), `KnowledgeDirectory` (`:58`, nested folders inside a KB), access via `access_grants` (`:89`).
- **Vector DBs (14)** (`retrieval/vector/type.py` + `factory.py`): chroma, qdrant (+multitenancy), milvus (+multitenancy), pgvector, pinecone, elasticsearch, opensearch, oracle23ai, s3vector, weaviate, opengauss, valkey, mariadb-vector — selected by `VECTOR_DB` env; singleton `VECTOR_DB_CLIENT` (`factory.py:96`) + async variant.
- **Embeddings** (`retrieval/utils.py:918-1062`): ollama, openai, azure_openai, + local SentenceTransformers fallback.
- **Loaders** (`retrieval/loaders/main.py:228`): external, tika, datalab_marker, docling, Azure DI, mineru, mistral, paddleocr_vl + LangChain per-extension; dedicated youtube/external_web/tavily loaders. Wide, product-grade.
- **Retrieval pipeline**: `query_doc/collection` (`:275,535`), **hybrid BM25+vector** (`query_*_with_hybrid_search :341,613`, `HYBRID_BM25_WEIGHT`), reranking (`get_reranking_function :1063` — external / ColBERT / CrossEncoder), `merge_and_sort_query_results :475`, `get_sources_from_items :1152` (citation assembly), `filter_accessible_collections :1086`.
- **How it reaches chat** (`utils/middleware.py`): model `meta.knowledge` (`:2486`) → non-native injects a `knowledge_search` action (`:2493`) vs **native function-calling = agentic retrieval** (`query_knowledge_files`/`view_knowledge_file` built-in tools `:220,308`); folder-scoped via `metadata['folder_knowledge']`; `#`-invocation per query.
- APIs: `/api/v1/knowledge` (create/reindex/search/files/dirs/sync), `/api/v1/retrieval` (embedding/config/process file|text|youtube|web/query).
- Docs: <https://docs.openwebui.com/features/workspace/knowledge> · <https://docs.openwebui.com/features/chat-conversations/rag/document-extraction>

---

## 6. CONVERSATIONS — core solid; **dual-store is the fragile seam**  [upstream]

- **TWO coexisting message stores** (`models/chats.py`, `models/chat_messages.py`):
  - Legacy `Chat` table (`:41`) — `chat` JSON blob with `history.messages{}` + `history.currentId`. **Branching lives here**: each message has `parentId`+`childrenIds`, `currentId`=active leaf, siblings=branches; regen/edit/branch are new DAG nodes (`:495,611-618`; `routers/chats.py:111,146,224,284`). **This is the authoritative branching representation today.**
  - New normalized `ChatMessage` (`chat_message`, `:79`): `id, chat_id, user_id, role, parent_id, content, output, model_id, files, sources, embeds, done, status_history, error, usage`, indexed `(chat_id,parent_id)`. Dual-write/migration glue (`:540-560`). **Forward path, but mid-migration — read the JSON `history` as truth for now.**
  - `ChatFile` (`:96`) = chat↔file↔message attachment provenance.
- Chat fields: `share_id, archived, pinned, meta, folder_id, tags, summary, last_read_at, tasks`. Folders/tags/shared-chats are separate models.
- APIs `/api/v1/chats`: list/search/pinned/archived/shared, new/import, per-chat get/post, `/{id}/messages/{mid}` + `/event` (normalized write), pin/clone/archive/share/folder/tags, `branchPointMessageId` in clone (`:1211,1282`), stats/export.
- Docs: <https://docs.openwebui.com/features/chat-conversations/data-controls/import-export>

---

## 7. IDENTITY — enterprise-complete  [upstream]

- **Users** (`models/users.py`): `role` default `'pending'` (roles = pending/user/admin), `email, username, oauth, scim`, + presence/status/bio. `ApiKey` table (`:136`) = first-class rows (`key, expires_at, last_used_at`).
- **Groups** (`models/groups.py`): `Group(permissions JSON)` + relational `GroupMember` join (`:73`).
- **Access control** (`utils/access_control/__init__.py`): `has_permission :70`, `has_access :106`, `check_model_access :300`. **`AccessGrant` table** (`models/access_grants.py:20`): `(resource_type ∈ knowledge|model|prompt|tool|note|channel|file, resource_id, principal_type ∈ user|group|*, principal_id, permission ∈ read|write)`. `migrate_access_control :171` converts legacy JSON `access_control` → grant rows; **same dual-model duplication as chats** (JSON field ⟷ grant table coexist; grant table = forward truth).
- **Auth methods** (`utils/auth.py`, `routers/auths.py`): password (bcrypt), JWT (with denylist `invalidate_token`), API key (`sk-`, `ENABLE_API_KEYS_ENDPOINT_RESTRICTIONS` allowlist `:425`), OAuth/OIDC (`utils/oauth.py`, RP-initiated logout `:825`), LDAP (`:315`, ldap3+TLS), trusted-header SSO (`WEBUI_AUTH_TRUSTED_EMAIL_HEADER :358`), **SCIM 2.0** (`routers/scim.py` — full Users+Groups CRUD/PATCH, bearer-gated). Guards `get_verified_user :452`, `get_admin_user :461`.

---

## 8. FRONTEND CUSTOMIZATION — runtime vs fork-only  [upstream]

Frontend is a **prebuilt SvelteKit bundle** at `open_webui/frontend/` (`_app/`, `index.html`, no `.svelte` source; no build toolchain in venv).

**Runtime-customizable (no rebuild):**
- **Custom CSS** — `index.html` hardcodes `<link href="static/custom.css">` (exists, 0 bytes); `/static` mounted `main.py:2978`. Drop CSS in → loads everywhere. `STATIC_DIR` env-overridable (`env.py:240`).
- **Custom JS** — `<script src="static/loader.js">` (exists, 0 bytes), same mount → arbitrary runtime JS.
- **WEBUI_NAME** (`config.py:34` → `/api/config` `main.py:2402`), **banners** (`WEBUI_BANNERS` + live `GET/POST /api/v1/configs/banners` `routers/configs.py:658-670`), **logo/favicon/splash** (overwrite `static/` files or `CUSTOM_NAME`/`WEBUI_FAVICON_URL`), **login/signup toggles** (`ENABLE_SIGNUP`, `ENABLE_LOGIN_FORM`).
- **Functions/Tools/Models/Pipelines** = DB rows via admin UI = primary sanctioned runtime extension surface.

**Fork-only (rebuild required):** page layout, the chat UI itself, components, nav/sidebar, new pages/routes — all compiled Svelte. `SPAStaticFiles` (`main.py:599-611`) only does 404→index fallback, no templating. **So `custom.css`+`loader.js` is the ONLY runtime door into the rendered UI** — deep reskinning possible (restyle/hide/rearrange via CSS+DOM-JS), but true layout/routing changes are fork-only.

**LICENSE — the decisive fusion constraint.** NOT plain BSD-3 — it is the **"Open WebUI License"** (BSD-3 + anti-branding clause 4). Verbatim: rebranding ("Open WebUI" name/logo) is **prohibited** EXCEPT (i) ≤50 end-users in any rolling 30-day window, (ii) prior written permission, or (iii) enterprise license. Code stays modifiable/redistributable (BSD-3 core); only **removing branding at >50 users** is the breach. → A branded public-product fusion that strips OpenWebUI branding at scale requires a paid enterprise license. This cap, not any technical limit, gates a branded fusion.

---

## 9. API SURFACE (programmatic)  — `main.py:1413-1456`

- OpenAI-compat: `/openai/chat/completions` (external clients), `/ollama` proxy. Canonical user path `/api/chat/completions` runs the heavy middleware chain (`utils/middleware.py`) where RAG/tool/knowledge injection happens.
- All `/api/v1/*`: pipelines, tasks, images, audio, retrieval, configs, auths, users, channels, chats, notes, models, knowledge, prompts, tools, skills, memories, folders, groups, files, functions, evaluations, analytics, utils, terminals, automations, calendars; `scim/v2` (conditional). `/ws` Socket.IO (`:1410`).
- Auth: Bearer = JWT session token OR `sk-` API key, both via `get_current_user` (`auth.py:291-318`); keys globally-disable-able + endpoint-restrict-able.

---

## 10. HONEST STRONG-vs-WEAK (for the fusion — "surface, don't decide")

**Genuinely strong / product-grade — worth building INTO a company system:**
1. **Extension model (Functions: Pipe/Filter/Action + Tools)** — clean typed seams: custom models, pre/post/stream hooks, message buttons, model-callable tools (incl. MCP/OpenAPI). The single most reusable design.
2. **Channels + AI-as-participant** — multi-human + multi-model shared real-time timeline streaming through the FULL chat pipeline. The most novel thing here; flag as Beta.
3. **RAG factory** — 14 vector DBs, wide loader matrix, hybrid+rerank, native-function-calling agentic retrieval.
4. **Identity stack** — SCIM/OAuth/LDAP/trusted-header + relational AccessGrant with chained-base enforcement. Enterprise-grade.
5. **OpenAI-compat multi-connection + manifold dynamic model injection** — prefix/filter/tags, concurrent fan-out, presets/overrides.
6. **Streaming sentence-split TTS + caching** — the good voice UX primitive.
7. **Branching chat DAG** (parentId/childrenIds/currentId) — clean conversation model.

**Weak / duplicative-of-a-richer-substrate — likely NOT worth harvesting (the company substrate is richer):**
1. **Pipelines server** — upstream itself deprecates it; superseded by in-process Functions. Skip.
2. **Half-finished JSON→relational normalization** (chat_message ⟷ chat-JSON; access_grant ⟷ access_control JSON; knowledge-files-in-meta vs join tables) — three parallel mid-migration seams; a company substrate with one resolution model should not inherit the duplication.
3. **The compiled frontend** — fork-only, license-capped, and the company's resolution-first/compositional surface is the richer substrate. Harvest backend subsystems, not the UI.
4. **`transformers` local TTS + hardcoded ElevenLabs settings** — niche/weak engine paths.
5. **No-sandbox plugin `exec` + `pip`-at-load** — powerful but a trust/supply-chain liability to inherit as-is; the *interface shapes* are worth more than the loader.

**Cross-cutting fragility flags:** no-silent-failure violations (broken manifold→empty list; swallowed channel-AI errors); signature-sniffed dunder contract (version-specific, typo-fragile); `replace_imports` mutating stored DB content; brittle index/URL dual-keying of connections; unauthenticated public channel webhook.
