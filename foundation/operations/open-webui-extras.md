---
type: operations
title: Open WebUI — extras catalog (providers, tools, integrations)
date_started: 2026-05-28
tags: [foundation, operations, webui, extras, catalog]
---

# Open WebUI extras catalog

> [[_operations-index|← Operations hub]] · runtime overview in [[open-webui]] · version 0.9.5 baseline

Comprehensive enumeration of what Open WebUI 0.9.5 can have plugged into it. Most rows aren't currently enabled on this substrate — this file is the menu, not the live config. Live state lives in `docker inspect open-webui` and the Admin Settings UI.

Status legend in tables: ✓ = enabled today · ◇ = available, not enabled · key = needs API key Tim hasn't provided yet · local = needs no external account

## 1. Web search providers

Open WebUI sets one provider at a time as the active web search backend. Switching is via Admin Settings → Web Search or via `WEB_SEARCH_ENGINE` env var.

| Provider | Status | Cost | Notes |
|---|---|---|---|
| DuckDuckGo | ◇ local | free | No key, HTML scraping. Lowest setup, weakest quality. |
| SearXNG (self-hosted) | ◇ local | free | Best free option; needs a SearXNG container alongside (5-min setup). |
| Tavily | ◇ key | free tier + paid | **AI-first search** — designed for LLM consumption. Tim has key. |
| Brave | ◇ key | free tier + paid | Independent index. Tim has key. Open WebUI supports per-request token budget (Brave LLM Context, added 0.9.3). |
| Google PSE | ◇ key | free 100 q/day + paid | Google Programmable Search Engine. Tim has Google Workspace; needs a PSE engine ID + Custom Search JSON API key. |
| Perplexity | ◇ key | paid | Returns Perplexity-style result with citations. Tim has key. |
| Jina | ◇ key | free tier + paid | Web reader API + search. Returns clean markdown. |
| Exa | ◇ key | free tier + paid | Semantic-search-as-a-service for the web; good for research. |
| Serper | ◇ key | free tier + paid | Cheap general Google scraping. |
| SearchAPI | ◇ key | paid | Google + Bing + Baidu + others through one API. |
| Serply | ◇ key | paid | Same shape as Serper. |
| Serpstack | ◇ key | free tier + paid | Same shape. |
| Bing (Web Search API) | ◇ key | paid | Microsoft official. |
| Kagi | ◇ key | paid (Kagi subscription) | Premium search; needs Kagi account. |
| Mojeek | ◇ key | free tier + paid | Independent UK index. |
| Bocha | ◇ key | paid | Chinese market. |
| Sougou | ◇ key | paid | Chinese market. |
| YaCy (self-hosted) | ◇ local | free | P2P distributed search. Niche; high setup cost. |
| External (custom URL) | ◇ — | depends | Point Open WebUI at any HTTP search endpoint following its expected schema. |

Recommendation: enable **DuckDuckGo + Tavily + Brave + Perplexity + Firecrawl-as-loader** initially; switch active provider per-conversation as the chat needs.

## 2. Web content loading / scraping (paired with search; also used for "paste URL" in chat)

The "loader" is what fetches a URL once a search returns a link, or when a user pastes a URL into chat. Configurable via `WEB_LOADER_ENGINE`.

| Loader | Status | Notes |
|---|---|---|
| `requests` (default) | ◇ local | Simple HTTP fetch + readability extraction. Works on static sites; misses JS-heavy content. |
| `playwright` | ◇ local | Headless Chromium. Renders JS. Needs Playwright dependencies — adds container weight. |
| `firecrawl` | ◇ key | **High-quality structured extraction** for any site, JS-rendered. Tim has key. v2 API supported (0.9.2+). |
| `tavily` | ◇ key | Uses Tavily's extraction. Pairs with Tavily search. |

## 3. Document processing (for file uploads → RAG)

When a user uploads a PDF / DOCX / etc., this engine extracts text. Configurable via `CONTENT_EXTRACTION_ENGINE`.

| Engine | Status | Local/Cloud | Notes |
|---|---|---|---|
| Built-in (default) | ✓ local | local | pdfminer, python-docx, markdown, plain text. Solid for clean text PDFs. |
| Apache Tika | ◇ local | local (container) | Standard enterprise extractor; better for mixed formats; needs a Tika server alongside. |
| Docling | ◇ local | local | IBM's modern doc extractor; excellent for tables / complex layouts. |
| PaddleOCR-VL | ◇ — | local API | OCR-grade extraction (added 0.9.2); handles scanned PDFs and screenshots well. |
| Mistral OCR | ◇ key | cloud | Mistral's OCR service. |
| Azure Document Intelligence | ◇ key | cloud | Microsoft's structured-extraction service. |
| External (custom URL) | ◇ — | — | Point at any HTTP extraction endpoint. |

## 4. Image generation

For "create an image" capability inside chat. Configurable via Admin Settings → Images.

| Backend | Status | Local/Cloud | Notes |
|---|---|---|---|
| OpenAI DALL-E / gpt-image | ◇ key | cloud | OpenAI API. Tim has key. |
| Google Imagen / Gemini Image | ◇ key | cloud | Tim has Google access; needs the right API enabled. |
| AUTOMATIC1111 | ◇ — | local | The classic Stable Diffusion WebUI; needs separate install + VRAM. Not on substrate currently. |
| ComfyUI | ◇ — | local | Node-graph SD; same VRAM cost. |
| Replicate | ◇ key | cloud | Hosted SD / Flux / etc. via Replicate API. |
| Gemini / Imagen | ◇ key | cloud | Same Google API ecosystem. |
| ComfyUI workflow JSON imports | ◇ — | local | Custom pipelines. |

Recommendation: **OpenAI image API first** (Tim has key, zero local infrastructure, immediate). Local SD would conflict with current substrate VRAM budget.

## 5. Speech-to-text (STT)

For voice input in chat. Configurable via Admin Settings → Audio.

| Provider | Status | Local/Cloud | Notes |
|---|---|---|---|
| Whisper (local) | ✓ configured | local | `WHISPER_MODEL=base` is set on the container. Already pre-loaded. UI toggle may still need flipping. |
| OpenAI Whisper API | ◇ key | cloud | Cloud version; faster, more accurate, costs per minute. |
| Web Speech API (browser) | ◇ local | browser | Browser-native STT. Free, works without server. Quality varies by browser. |
| Azure Speech | ◇ key | cloud | Microsoft enterprise STT. |
| Deepgram | ◇ key | cloud | High-quality streaming STT. |

## 6. Text-to-speech (TTS)

For voice output. Configurable via Admin Settings → Audio.

| Provider | Status | Local/Cloud | Notes |
|---|---|---|---|
| Web Speech API (browser) | ◇ local | browser | Free, native browser voices. Robotic-sounding. |
| OpenAI TTS | ◇ key | cloud | Good voices, low latency. Tim has OpenAI key. |
| ElevenLabs | ◇ key | cloud | **Best-in-class voice quality**. Voice cloning available. Paid. |
| Mistral TTS | ◇ key | cloud | Added 0.9.0. |
| Azure TTS | ◇ key | cloud | Enterprise. |
| Transformers (local) | ◇ — | local | Run HuggingFace TTS models locally. VRAM cost; quality varies. |

## 7. Code execution

For "the model writes code → executes → uses result." Configurable via Admin Settings → Code Interpreter.

| Backend | Status | Notes |
|---|---|---|
| Pyodide (browser) | ◇ local | Default. Python sandbox in browser. Supports file uploads via `/mnt/uploads/` (0.9.0+). No pip; restricted libraries. |
| Jupyter | ◇ — | Point at any Jupyter server; gives real Python with any installed packages. Could run a Jupyter container locally. |

## 8. Built-in vector DB for RAG

Open WebUI has its own RAG engine that needs a vector store. Currently this is implicit; configurable via `VECTOR_DB`.

| Store | Status | Notes |
|---|---|---|
| ChromaDB (default) | ✓ local | Built into the container. Adequate for personal use. |
| Qdrant | ◇ local | **Already running on this machine** (port 6333). Faster, better-featured. |
| pgvector | ◇ local | **Already running on this machine** (the langconnect-postgres container). |
| Milvus | ◇ — | Self-hosted. Heavy. |
| Weaviate | ◇ — | Self-hosted. |
| Pinecone | ◇ key | Cloud. |
| Elasticsearch / OpenSearch | ◇ — | Self-hosted. |

Recommendation: switch from ChromaDB to **Qdrant** since it's already live on this machine. Better quality, no extra infrastructure.

## 9. Model providers (LLM connections)

Plug additional models in beyond the local substrate. Each appears in the chat-model dropdown.

| Provider | Status | Notes |
|---|---|---|
| Local vLLM (8000) | ✓ | Qwen3.5-4B-AWQ |
| Local vLLM embed (8001) | ✓ | BGE-M3 |
| Local Ollama (11434) | ✓ | GGUF MoEs + cloud routes (DeepSeek, Kimi, GLM, Gemini, Qwen-397B etc.) |
| OpenAI direct | ◇ key | All OpenAI models — GPT-5, o-series. Tim has key. |
| Anthropic direct | ◇ key | Claude models. Needs Anthropic key. |
| Google Gemini direct | ◇ key | Gemini models via Google AI Studio API. Tim has Google access. |
| Mistral direct | ◇ key | Mistral La Plateforme models. |
| Azure OpenAI | ◇ key | Microsoft-hosted OpenAI. 0.9.0+ supports `/openai/v1` format. |
| Groq | ◇ key | Fast-inference cloud. Llama / Mixtral / etc. |
| Together AI | ◇ key | Cloud-hosted open models. |
| OpenRouter | ◇ key | **One key, many models** — Anthropic / OpenAI / Google / Mistral / Llama / etc. via single endpoint. Good for "I want everything" with single billing. |
| LiteLLM proxy | ◇ — | A self-hosted proxy in front of all of the above; consolidates. |

## 10. Tools / Functions / Filters / Skills (Workspace plugins)

These are Python code that extends what models can do. All Open WebUI versions support; 0.9.x improved discovery and management.

| Type | What it does | Example use |
|---|---|---|
| **Tools** | Python functions the model can call (function calling) | `read_foundation_file(path)`, `query_qdrant(query)`, `restart_service(name)` |
| **Filter functions** | Modify request before sending to model OR modify response before showing user | Strip PII, add disclaimers, redact secrets |
| **Action functions** | UI buttons in chat that trigger custom logic | "Send to my Obsidian", "Save as note", "Run on substrate" |
| **Pipe functions** | Full pipeline replacement — model selection / routing / transformation | Route to cloud Ollama for reasoning, local for chat |
| **Skills** (new 0.9.x) | Reusable named capabilities persisted in chats | Pre-built workflows triggered with @skill |
| **Pipelines** | Separate Python service (advanced) for full pipeline customisation | Production-grade routing, monitoring, rate limiting |

Community sources:
- **openwebui.com/tools** — community-published tools, one-click import (Tools)
- **openwebui.com/functions** — community functions
- **openwebui.com/prompts** — community prompts

## 11. MCP servers

Open WebUI 0.9.0+ supports Model Context Protocol servers as a tool source. Major improvement over earlier custom-Python-tool approach.

| Aspect | State |
|---|---|
| MCP support | ◇ available, none connected yet |
| OAuth-authenticated MCPs | ◇ 0.9.3+ supports `MCP_OAUTH_SERVER_URL` |
| Streaming with MCP tool calls | ◇ 0.9.5+ supports in channel streaming |
| Existing MCP infrastructure on this machine | Multiple MCP processes already running (mcpdoc, agent_frameworks, others) — see [[../system/architecture]] for the broader picture |

This is the architecturally interesting path Tim and I discussed — wiring existing MCP servers into Open WebUI exposes their tools in chat without writing new adapters.

## 12. Calendar / Automations / Task management (new in 0.9.x)

| Feature | State | Notes |
|---|---|---|
| Calendar workspace | ◇ | Events, reminders, recurring schedules. Probably overkill currently. |
| Scheduled automations | ◇ | **Recurring chat tasks.** "Every morning summarise X." Configurable via `AUTOMATION_MAX_COUNT` / `AUTOMATION_MIN_INTERVAL`. |
| Task management tool | ◇ | Track multi-step work in conversations natively. Adds @task / @todo style management. |
| Reminders | ◇ | In-app toasts, browser notifications, optional webhooks. |

## 13. OAuth / SSO (multi-user identity)

Configure Open WebUI to accept logins from external identity providers. Not relevant for single-user-localhost setup; relevant if access is ever extended.

| Provider | Notes |
|---|---|
| Generic OIDC | Any OpenID Connect provider |
| Google | Including Google Workspace |
| Microsoft | Azure AD / Entra ID |
| GitHub | |
| Discord | |
| LDAP | Enterprise directory |
| Reverse-proxy headers | For nginx / caddy / cloudflare auth |
| Custom HTTP headers | For bespoke setups |

## 14. Knowledge / Memory

Built-in features for personalisation and persistent context.

| Feature | What it does |
|---|---|
| Knowledge collections | Upload docs → embedded → attachable to chat via @collection. Foundation could go here. |
| Memory (per-user persistent context) | Long-term facts the model remembers across conversations |
| Saved prompts | Reusable system prompts (Workspace → Prompts) |
| Folder system prompts | Apply a system prompt to a whole folder of chats (0.9.2+) |
| Nested folders | Organisation (0.9.0+) |

## 15. UI / branding

| Feature | Status | Notes |
|---|---|---|
| Custom CSS | ◇ | Override styling via Admin Settings |
| Splash images | ◇ | Boot screen |
| Banners | ◇ | Admin-controlled announcements |
| Themes | ✓ | Light / dark + system; per-user |
| Custom branding (paid) | ◇ | Enterprise feature; full white-label |

## 16. Multi-user / channels (advanced)

| Feature | Notes |
|---|---|
| User accounts + roles | Admin / user / pending |
| User groups + per-group permissions | |
| Channels (multi-user threaded chats) | Multiple humans + agents in one conversation thread. Could become the Crew-chat-with-Tim surface. |
| Shared chats | Per-chat sharing controls (0.9.5 permission fixes) |

---

## What Tim has API keys for (provided in 2026-05-28 conversation, awaiting handover)

- ✓ **Tavily** (web search, AI-optimised)
- ✓ **Firecrawl** (high-quality web scraping)
- ✓ **Brave** (independent search index)
- ✓ **Perplexity** (search with citations)
- ✓ **OpenAI** (models + DALL-E + Whisper + TTS)
- ✓ **Google Workspace** (Tim can generate Google PSE + Gemini API + others as needed — needs clarification on which product specifically)
- ✓ "a bunch of others too" (open — Tim to identify)

## What to enable in the first wave (immediate value, no waiting)

Tier 1 — flip on, no waiting on keys, ~1 minute each:

- DuckDuckGo web search (free fallback / can stay disabled if better is enabled)
- Pyodide code execution
- Built-in URL fetching (default loader)
- Whisper STT (already configured, just expose UI toggle)
- Browser TTS (no server changes)

Tier 2 — needs Tim's keys, enable as keys arrive:

- Tavily search
- Brave search
- Perplexity search
- Firecrawl as web loader
- OpenAI direct (chat + DALL-E + TTS + Whisper API)
- Google PSE (if Tim generates the engine ID)
- Gemini direct (if Tim enables the Generative Language API)
- Mistral TTS (if Tim wants a Mistral key)

Tier 3 — switch vector DB:

- Move from ChromaDB to Qdrant (already running on machine, port 6333). Cleaner state, faster, more featured.

Tier 4 — comes after: MCP connections to the existing MCP infrastructure. Bigger architectural conversation Tim flagged for later.

## Open at this catalog

(Provisional; surface gaps as they're noticed.)

- Anthropic direct (Claude) not enumerated above — Tim didn't list as a key he has; clarification needed (likely yes via Claude Code, but separate API key situation)
- OpenRouter not in Tim's list but would consolidate many models behind one key; flag for consideration
- Local image generation (AUTOMATIC1111 / ComfyUI) deliberately not pursued — VRAM conflict with substrate
- Pipelines (the separate Python service) skipped in detail — advanced; relevant when custom routing becomes needed
- The bigger MCP architectural conversation belongs in [[../system/architecture]] when it happens, not here
- Conduit iOS client ($3.99 App Store) and Open WebUI Desktop v0.0.20 for Windows are downloaded/identified but their setup with the WSL backend isn't documented yet (needs a dedicated topic file when Tim actually installs)
- Per-user vs per-conversation provider settings — most providers can be set globally OR per-model-preset; the right granularity isn't decided
- Cost monitoring across enabled providers — if many cloud providers get keys, total spend visibility becomes a real concern

## Connects to

- [[_operations-index]] — hub
- [[open-webui]] — runtime overview
- [[runtimes]] — broader runtime context
- [[system-prompts]] — territory map for chat-level customisation
- [[../models/_models-index]] — the substrate-side model story
