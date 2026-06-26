# 05d — Head-to-Head: Self-Hosted Chat-UI Platforms as a Fabric Front-End

> Synthesis of `05a-openwebui.md`, `05b-lobechat.md`, `05c-librechat.md` against the use-case in `_SHARED-RUBRIC.md`. All inputs grounded in live June-2026 sources; the two highest-stakes claims per platform (LICENSE + MCP) were spot-checked by the lead against primary sources before this synthesis.

## The use-case, restated
A self-hosted front-end for the Company's custom multi-agent **fabric** — a *supervisor + channels + members* that **emit content**. The front-end is **not a chat box** that waits for the user; the fabric **pushes** unsolicited, server-initiated messages into the UI (into custom panels). What matters, in priority order:
- **(a)** Extensibility — custom panels + custom tools + **inbound-message surfacing** (server→UI push).
- **(b)** External call-out — call the fabric's HTTP / MCP API.
- **(c)** Mobile — real phone usability.
- **(d)** Code-extension cleanliness — how cleanly the code can be forked/extended.

## The one finding that frames everything
**None of the three does fabric-owned server-push natively.** All three are architecturally request/response: the user sends → the assistant streams a reply (SSE). "The fabric pushes channel/member messages into a custom panel, with no user turn" is the genuinely hard fit, and it is **a fork in every case**. So this is not "which platform does it" — it's **which platform is cheapest to fork for the push layer, with the least license friction, on the cleanest code.** Everything below serves that question. (Per `feedback-not-a-replacement`: found-in-a-separate-system ≠ the answer — each is a *base to fork*, not a drop-in fabric front-end.)

---

## Comparison table

| Dimension | **Open WebUI** | **LobeChat / LobeHub** | **LibreChat** |
|---|---|---|---|
| **Frontend stack** | SvelteKit / TS | Next.js 16 + React 19 (hybrid router), tRPC, Zustand, antd CSS-in-JS | **React 18 + Vite + Tailwind + Radix** (plain) |
| **Backend stack** | Python / FastAPI (async) | Next.js API + tRPC, Drizzle | **Node / Express 5 (TS)** |
| **Data store** | SQLite → Postgres; 9 vector DBs | PostgreSQL (Drizzle) | MongoDB + Redis |
| **(a) Inbound push — DISCRIMINATOR** | **Partial — best foundation.** WebSocket `__event_emitter__` + REST event-callback push into a chat, **but request-scoped** (needs a user turn or in-proc Pipe; arbitrary panel = fork) | **Weak.** No push bus, no panel API; fabric→UI = **fork + commercial license** | **Weak — but cheapest fork.** SSE = LLM-stream only; push = add SSE/WS route + hook + panel (**~3–5 files**) |
| **(b) External call-out** | Strong (OpenAI base URL / MCP) | Strong (OpenAI base URL / MCP) | **Strong — cleanest** (custom endpoint *and* fabric-as-MCP-server, both zero-code) |
| **(c) Mobile** | Partial (responsive; PWA unverified; desktop app; no native) | **Strong (cloud) / Partial (self-host)** — native iOS/Android, but apps target cloud only | Partial (installable PWA; no native; depth unverified) |
| **(d) Fork/extend cleanliness** | Strong in-proc plugins / Partial deep frontend; discussion-first + CLA friction | Partial — hybrid router + CSS-in-JS + ships-many-times/day + license | **Strong — most tractable** (conventional, no proprietary framework) |
| **Tools/plugins** | 5 in-proc types (Tool/Pipe/Filter/Action) + OpenAPI/MCP | MCP "Skills" + Agent Groups (legacy plugins deprecated) | Agents + Actions (OpenAPI) + MCP + custom endpoints |
| **Model/backend** | Ollama + any OpenAI-compatible + more | 70+ providers + OpenAI-compatible | OpenAI/Azure/Anthropic/Gemini/Bedrock/Ollama + any custom |
| **Auth / multi-user** | RBAC + SSO/OIDC/SAML/LDAP + SCIM + MFA | Better Auth + broad SSO; **no real RBAC** (email allow-list) | **ACL RBAC + OIDC/SAML/LDAP + per-user MCP/OBO** (strongest) |
| **MCP** | Native, **Streamable-HTTP only** (v0.6.31); stdio/SSE via `mcpo` | Native client, **stdio + HTTP**, OAuth2, 10k marketplace | Native, config-driven, **stdio + SSE + streamable-HTTP**, OAuth2 + OBO + deferred tools |
| **License** | **BSD-3 + branding Clause 4** — no rebrand >50 users w/o enterprise license | **LobeHub Community License** — **commercial license required for any derivative work** | **MIT — clean, no clauses** |
| **Maturity** | 143k★, 163 tags, Open WebUI Inc. (founder-led, CLA) | 79k★, ships daily, LobeHub LLC (commercial) | ~39.6k★, daily commits, joining **ClickHouse** |

---

## How each scores on what matters most (the 4 priorities, weighted)

**(a) is the deciding axis. (b) is a tie (non-discriminating). (c) is a near-tie. (d) breaks the tie on (a)** — because (a) is a fork everywhere, so "cheapest, least-encumbered fork" wins.

- **Open WebUI** — the only one with a *real push primitive* today (`__event_emitter__` over WebSocket). If the fabric pattern is **"supervisor replies to a user turn with live-streamed structured output,"** this is the best fit *without* a frontend fork — an in-process Pipe/Filter Function streams fabric output into the chat. But for **truly unsolicited, multi-panel, no-user-turn** push (the literal discriminator), it still needs a SvelteKit fork — and the **branding clause** gates white-label above 50 users.
- **LibreChat** — no push today, but the **cleanest external call-out** (two zero-code paths), **MIT (no clauses)**, the **most tractable fork** (plain React/Express/Mongo, ~3–5 files for a push channel), and the **strongest enterprise auth**. The fork you must do anyway is the least painful and the least legally encumbered here.
- **LobeChat/LobeHub** — best mobile + most polished product, but the **weakest on (a)** (no push, highest-friction UI fork) and the fork **requires a paid commercial license**. The license + fork-friction combination rules it out as a *fork base* for this use-case (excellent as an off-the-shelf chat product, which this is not).

---

## Recommendation

**Primary: fork LibreChat** as the fabric front-end base.

Reasoning, tied to the priorities:
1. **The push layer is a fork no matter what** — so optimise for *fork cleanliness + license freedom*, and LibreChat wins both: conventional React/Express/MongoDB (no proprietary framework, ~3–5 files to add a fabric→browser SSE/WS channel + custom panel), **MIT with zero branding/commercial clauses** (vs. OpenWebUI's >50-user branding gate and LobeHub's commercial-derivative-license wall).
2. **(b) is best here** — the fabric is reachable two zero-code ways (OpenAI-compatible custom endpoint *and* fabric-as-MCP-server), so the user-turn path works on day one while the push fork is built.
3. **(d) strongest** — and **auth strongest** (ACL RBAC + OIDC/SAML/LDAP + per-user MCP/OBO), which a multi-member fabric will want.
4. **(c) acceptable** — installable PWA; mobile is a near-tie and not decisive.

**Strong alternative: Open WebUI — choose it instead if the fabric's surfacing pattern is request-scoped** (supervisor/members respond to a user turn with live-streamed, structured, multi-part output rather than fully autonomous panel push). Its `__event_emitter__` push + Channels + in-process Python plugins would let you deliver a lot **without forking the frontend at all** — a materially smaller build than LibreChat's fork *if* request-scoped streaming covers the need. The cost is the **branding clause** (white-label needs an enterprise license, or fork from v0.6.5) and a heavier lift the day you need true unsolicited multi-panel push.

**Not recommended as a fork base: LobeChat/LobeHub** — the commercial-derivative-license requirement plus the highest UI-fork friction make it the wrong base for a heavily-customised fabric front-end, despite being the best stand-alone product and the best mobile story.

### The honest gap (don't let the recommendation hide it)
Whichever you pick, you are **building the inbound-message-surfacing layer yourself** — none of these ships fabric-owned server-push into custom panels. The real decision is:
- **"Fork LibreChat and build the push channel + panels"** (most control, cleanest base, MIT), **vs.**
- **"Use Open WebUI request-scoped event push and accept its shape"** (least build *if* the pattern fits, but branding-gated and request-scoped).

Pick by **the fabric's actual surfacing pattern**: *autonomous unsolicited panel push* → LibreChat fork. *Live-streamed structured replies to user turns* → Open WebUI, no frontend fork.
