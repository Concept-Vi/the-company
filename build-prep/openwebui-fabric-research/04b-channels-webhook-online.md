# Channels + Inbound Webhook — ONLINE cross-check (companion to 04)

**Task:** Verify ONLINE the load-bearing local-code finding from `04-openwebui-customization.md` — that OpenWebUI ships a Discord/Slack-style **Channels** substrate AND a **public inbound webhook** `POST /api/v1/channels/webhooks/{id}/{token}` (no user auth, per-webhook token) that renders a message LIVE over socket.io. The local install (v0.8.12) is being **upgraded to the latest** right now, so the central question is the **0.8.12 → latest version delta**.

**Verdict up front:** The finding is **CONFIRMED** and survives the upgrade. The latest release is **v0.9.6** (2026-06-01) — not "~0.9.x". The webhook endpoint, the no-auth token model, the socket render path, and the push-only asymmetry are **byte-for-byte the same behavior in v0.9.6 as in v0.8.12**. **One correction to the local finding:** the feature IS documented (on a separate admin docs page), and the per-message payload is `{content}` ONLY — the custom name/avatar is set at webhook-creation time, not passed per-POST.

**Evidence discipline:** source-file-at-a-tag = **Confirmed** (primary). CHANGELOG/PR = **Confirmed** for when-added/what-changed. Docs/forum = as noted. Every claim pinned to a ref.

---

## 1. CONFIRM the feature + endpoint + mechanism — **Confirmed (primary source, v0.9.6 tag)**

Read directly from `open-webui` at tag **v0.9.6** (and re-confirmed identical at `main`):
- Source: `backend/open_webui/routers/channels.py` — https://raw.githubusercontent.com/open-webui/open-webui/v0.9.6/backend/open_webui/routers/channels.py (and `…/main/…` — byte-identical on all webhook symbols at fetch time)
- Source: `backend/open_webui/models/channels.py` — https://raw.githubusercontent.com/open-webui/open-webui/v0.9.6/backend/open_webui/models/channels.py
- Cross-check: `backend/open_webui/routers/channels.py` at v0.8.12 (older) — confirms the public webhook path is behaviorally unchanged 0.8.12 → 0.9.6

**The Channels substrate exists** (types: standard / group / dm; members, threads, reactions, pinned messages; gated by `ENABLE_CHANNELS` + `features.channels` permission, Beta). `check_channels_access` (`channels.py:126`) — *"Dependency to ensure channels are globally enabled."*

**The public inbound webhook exists, unchanged:**
- Route decorator `@router.post('/webhooks/{webhook_id}/{token}')` → `async def post_webhook_message(...)` (`channels.py:1767-1768`).
- Docstring verbatim: **`"Public endpoint to post messages via webhook. No authentication required."`** (`channels.py:1775`).
- Token validation: `webhook = await Channels.get_webhook_by_id_and_token(webhook_id, token, db=db)` → 401 if no match (`channels.py:1779-1784`).
- Token is generated as **`secrets.token_urlsafe(32)`** at creation (`models/channels.py:938`, in `insert_webhook`) — identical to the local finding.
- Message inserted with webhook identity in meta: `MessageForm(content=form_data.content, meta={'webhook': {'id': webhook.id}})` (`channels.py:1791-1796`).
- Live render: `await sio.emit('events:channel', event_data, to=f'channel:{channel.id}')` (`channels.py:1832-1836`). The event carries `user: {id, name, role:'webhook'}` from the stored webhook record (`channels.py:1817-1828`).
- Creation endpoint (manager/admin only): `@router.post('/{id}/webhooks/create')` (`channels.py:1681`); plus list/update/delete webhook routes (`1662/1705/1734`); plus a webhook profile-image route (`1628`). The `WebhooksModal.svelte` UI fronts these.

> **★ Payload correction to the local finding (Confirmed).** The local note says the webhook posts "with a custom sender name+avatar." Precisely: the POST **body** is `class WebhookMessageForm(BaseModel): content: str` — **`content` ONLY** (`channels.py:1763-1765`, identical in v0.8.12 at `1747`). The custom **name + `profile_image_url`** are set once at webhook creation via `class ChannelWebhookForm(BaseModel): name: str; profile_image_url: Optional[str]` (`models/channels.py:247-249`) and stored on the webhook row. **You cannot vary identity per-POST.** Design consequence for the fabric: **each agent that needs its own name/avatar needs its own webhook** (one webhook = one fixed identity). This does not weaken the architecture — it just means N agents → N webhooks per channel.

## 2. VERSION HISTORY + the 0.8.12 → latest delta — **Confirmed (CHANGELOG + source diff)**

Source: `CHANGELOG.md` @ main — https://raw.githubusercontent.com/open-webui/open-webui/main/CHANGELOG.md (version section headers verified by line).

- **Latest release: v0.9.6** (2026-06-01). v0.8.12 was 2026-03-26/27. Release ladder between them: 0.9.0 (2026-04-20) → 0.9.1 → 0.9.2 → 0.9.3 → 0.9.4 → 0.9.5 (2026-05-09) → 0.9.6.
  - `gh api repos/open-webui/open-webui/releases` confirms tags + dates.
- **When the channel webhook was ADDED: v0.7.0 (2026-01-09)** — CHANGELOG: *"🪝 Channel managers can now create webhooks to allow external services to post messages to channels without authentication."* (commit `cd296fcf`). So it predates v0.8.12 by ~2.5 months and is mature, not bleeding-edge.
- **Channels feature itself** is older still (group/DM channel types landed in the 0.8.0 era; the @-mention model path has been iterated across many releases).

**The webhook PUBLIC path is behaviorally identical across 0.8.12 → 0.9.6** (Confirmed by diffing both files):
- v0.8.12 `post_webhook_message` at line **1751**; v0.9.6 at **1767**. Same docstring, same `{content}`-only form, same token lookup, same insert+emit, **same absence of any model-summon** in both. Line numbers drift; behavior does not.

**What DID change between 0.8.12 and 0.9.6 (Confirmed) — none of it breaks the webhook contract:**
- **v0.9.6 — Channel chat access control** ([PR #24725](https://github.com/open-webui/open-webui/pull/24725), title *"fix: gate chat_completion channel: branch on channel access + message scoping"*): a security fix on the **model-mention / chat-completion response path** (verifies caller access, scopes thread messages, prevents cross-channel message overwrite). **Explicitly NOT the public webhook endpoint** — confirmed in the PR and by `model_response_handler` now calling `get_filtered_models(..., user=user)` (`channels.py:855`). Affects the *user→model* direction, not the *fabric→webhook* direction.
- **v0.9.5 — Channel streaming + full pipeline** (CHANGELOG): @-mentioning a model in a channel now streams in real time and supports the full chat-completion pipeline (native/default function calling, built-in tools incl. web search + image gen, user tools, MCP tools, filters, RAG) — same capabilities as standard chat. *Strengthens* the model-as-channel-participant path (relevant to the Pipe `@`-mention direction, #B-outbound in 04).
- **v0.9.x — Webhook avatar URL validation** ([PR #24370](https://github.com/open-webui/open-webui/pull/24370)): channel webhook `profile_image_url` is now validated before saving (`validate_profile_image_url`, `models/channels.py:251-256`). A real **creation-time** delta vs 0.8.12: an invalid/unsafe avatar URL is rejected at webhook-create. Does not affect posting.
- Numerous channel hardening fixes across 0.8.x/0.9.x: message ownership enforcement, pin write-permission, private member-list access, inactive-member access, pinned-webhook-message render robustness. All defensive; none touch the inbound webhook POST contract.

**Upgrade-path note:** a `pip install -U open-webui` lands on the **release** (v0.9.6). The prior deploy attempt's Dockerfile is `FROM ghcr.io/open-webui/open-webui:main` (unpinned, tracks latest). I fetched and verified `channels.py` at BOTH the **v0.9.6 release tag** AND **`main`** — they are byte-identical on every load-bearing symbol (webhook route `1767`, docstring `1775`, `WebhookMessageForm` `1763`, `background_handler`/`model_response_handler`, `get_webhook_by_id_and_token`). So both the release and `:main` carry the same webhook contract at fetch time. Caveat: `:main` moves daily — pin the deploy and smoke-test (see Stability).

## 3. Documented or undocumented? — **Correction: it IS documented (Confirmed)**

The local finding called the inbound webhook "genuinely undocumented." That is **half right and worth correcting:**
- The **feature page** `docs.openwebui.com/features/channels` has **zero** webhook mentions (confirmed by fetch) — it covers @-mentioning, reactions, files, access control, and states *"Channels is currently in Beta."* The local author checked this page, hence the "undocumented" call.
- BUT there is a **dedicated admin docs page**: `docs.openwebui.com/features/administration/webhooks/` (source repo `open-webui/docs`, `docs/features/administration/webhooks.md`). It documents **Channel (incoming) webhooks** explicitly:
  - Endpoint pattern verbatim: **`{WEBUI_API_BASE_URL}/channels/webhooks/{webhook_id}/{token}`** — matches the code exactly.
  - Payload verbatim: **`{ "content": "Your message content here" }`** — **confirms the `{content}`-only body** (independent corroboration of the §1 correction; docs do NOT show name/avatar in the POST).
  - Setup: *"Only channel managers and administrators can create and manage webhooks."* via Edit Channel → Webhooks → Manage → New Webhook (the `WebhooksModal`).
  - Security warnings verbatim: *"Anyone with the webhook URL can post messages to the channel, so treat it securely"* / *"Keep them secure and don't expose them in public repositories or logs"* / *"If a webhook URL is compromised, delete the webhook and create a new one."*
  - It does **NOT** state whether a webhook message triggers a model reply (the asymmetry is undocumented — see §4).
  - URLs: https://docs.openwebui.com/features/administration/webhooks/ · https://github.com/open-webui/docs/blob/main/docs/features/administration/webhooks.md

**Net:** it is a documented, supported capability (docs + CHANGELOG + a per-channel UI to create webhooks), not a hidden internal. Treat it as a stable contract — but still smoke-test on the exact deployed image (§4).

## 4. Stability + gotchas — design around these

- **The push-only asymmetry — Confirmed in source, undocumented anywhere.** The *user* path `post_new_message` (`channels.py:1094`) schedules `background_tasks.add_task(background_handler)` → `model_response_handler` (lines `1120-1129`), so a user message that `@`-mentions a model **auto-summons a reply**. The *public webhook* path `post_webhook_message` (`1767-1838`) does **insert + emit ONLY — no `background_handler`, no `model_response_handler`** (verified by reading the whole function: nothing between insert at 1791 and the `events:channel` emit at 1832 triggers a model). **A webhook-posted message that `@`-mentions an OWUI model will NOT chain into a reply.** Identical in v0.8.12 and v0.9.6. No doc/blog states this — it is a code-only fact. **For the fabric loop this is fine/desirable** (fabric generates its own content and pushes it; the *user→fabric* direction goes via @-mention→Pipe, which DOES auto-summon). But any loop that *expects* the webhook to re-trigger OWUI's model pipeline will **silently not fire**.
- **No rate limiting — Confirmed (absence, route + app entrypoint).** `post_webhook_message` has no rate-limit decorator (no `@limiter`/`slowapi`/throttle in `channels.py`), AND there is no global HTTP rate-limit middleware in `backend/open_webui/main.py` (no `slowapi`/`Limiter`/throttle; the only `limiter` there is `anyio.to_thread.current_default_thread_limiter()` at `main.py:670` — a thread-pool concurrency cap, not a per-request/IP rate limit). The endpoint is **public + unauthenticated by design**; the only gate is the 32-byte `token_urlsafe` secret (strong against brute force) plus `ENABLE_CHANNELS`. Treat the URL as a bearer secret; if exposed, anyone can post unlimited messages. Put your own rate limit / WAF in front if the URL ever leaves the trusted box.
- **Beta + `ENABLE_CHANNELS` gate — Confirmed.** Channels is Beta (admin must enable). The webhook path calls `check_channels_access(request)` (`channels.py:1776`) with **no user** — so it only checks the **global** `ENABLE_CHANNELS` flag. **Gotcha: if an admin turns Channels off globally, the webhook 403s** even with a valid token. Keep `ENABLE_CHANNELS=true` for the deploy.
- **Identity is fixed per-webhook — Confirmed** (see §1 correction). N agent identities → N webhooks. `profile_image_url` validated at create-time in v0.9.x (so use a valid http(s) or `data:image` URL).
- **`:main` drift risk.** I verified `channels.py` at the **v0.9.6 release tag** AND at **`main`** — identical on every load-bearing symbol at fetch time. The prior Dockerfile tracks `:main` (unpinned), which moves daily. **Recommendation (unchanged from 04): pin the deploy image to v0.9.6** (or whatever you upgrade to) and run a one-time smoke test on that exact image: create channel → create webhook → `curl -X POST {base}/api/v1/channels/webhooks/{id}/{token} -H 'Content-Type: application/json' -d '{"content":"hello"}'` → confirm it renders live with the webhook's name/avatar. Code-verified capability; verify-by-use seals it.
- **No removal/deprecation risk seen.** The webhook has shipped since v0.7.0, has its own docs page, its own UI modal, and accumulating hardening (avatar validation, pinned-webhook robustness) — the trend is *investment*, not deprecation.

## 5. Real-world external/bot precedent — **Confirmed it's a known integration pattern**

- OWUI's own docs frame channel webhooks as the **Discord/Slack incoming-webhook analog** for posting external-service messages into a channel (docs.openwebui.com/features/administration/webhooks/).
- Community integration precedent (general OWUI external automation, web search — treat as Inferred for specifics): **n8n** and **Zapier** integrations and custom scripts are commonly used to post into OWUI / drive workflows (e.g. pondhouse-data.com "Integrating n8n with Open WebUI"; n8n community threads; OWUI Discussion [#16428](https://github.com/open-webui/open-webui/discussions/16428) on webhook enhancements/event scoping; Discussion [#8274](https://github.com/open-webui/open-webui/discussions/8274) on appending assistant messages). These confirm the *pattern* (external service → OWUI via webhook) is exercised in the wild; none is a verbatim spec for the channel webhook, so design from the source contract in §1, not these.

---

### Sources
- Code (primary, v0.9.6): `routers/channels.py` https://raw.githubusercontent.com/open-webui/open-webui/v0.9.6/backend/open_webui/routers/channels.py · `models/channels.py` https://raw.githubusercontent.com/open-webui/open-webui/v0.9.6/backend/open_webui/models/channels.py
- CHANGELOG: https://raw.githubusercontent.com/open-webui/open-webui/main/CHANGELOG.md
- PR #24725 (v0.9.6 channel access control): https://github.com/open-webui/open-webui/pull/24725
- PR #24370 (webhook avatar URL validation): https://github.com/open-webui/open-webui/pull/24370
- Docs — channels feature page (no webhook): https://docs.openwebui.com/features/channels
- Docs — webhooks admin page (documents channel webhook): https://docs.openwebui.com/features/administration/webhooks/ · repo: https://github.com/open-webui/docs/blob/main/docs/features/administration/webhooks.md
- Community precedent: https://www.pondhouse-data.com/blog/integrating-n8n-with-open-webui · https://github.com/open-webui/open-webui/discussions/16428 · https://github.com/open-webui/open-webui/discussions/8274
