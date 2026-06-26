# Shared Research Rubric — Self-Hosted LLM Chat-UI Platforms for a Fabric Front-End

You are researching ONE platform as part of a 3-platform evaluation. Every researcher uses THIS rubric so the four reports are apples-to-apples.

## CRITICAL GROUNDING RULE
- Your training cutoff is stale (Jan 2026; it is now June 2026). These platforms ship constantly.
- **Write NOTHING from memory.** Every factual claim must come from a LIVE source fetched this session: official docs, the GitHub repo (README, source files, releases/changelog), or recent reputable articles.
- **Cite the URL** for each load-bearing claim, inline.
- If you cannot verify something from a live source, **say so explicitly** ("could not verify — last known: X").
- Two claims are HIGHEST stakes and must be verified from the primary source (not a blog):
  1. **LICENSE** — read the actual LICENSE file in the repo. Note any branding-protection / commercial clauses (e.g. OpenWebUI added a branding clause in 2025 restricting removal of its branding above a user threshold). State the exact license + any non-standard clauses verbatim-ish.
  2. **MCP support** — fastest-moving feature in this space. Is it native? via plugin/gateway? not at all? Cite the current release/docs that prove it.

## THE USE-CASE (what this front-end must serve)
A self-hosted front-end for a CUSTOM multi-agent "fabric": a supervisor + channels + members that emit content. The front-end is NOT just a chat box — the fabric PUSHES messages into the UI (supervisor/channels/members emitting unsolicited, server-initiated content into custom panels). What matters most, in priority order:
- **(a) Extensibility** — ability to add custom panels + custom tools + **inbound-message surfacing** (server-initiated push of channel/member messages into the UI).
- **(b) External call-out** — ability to call an external HTTP / MCP API (the fabric exposes one).
- **(c) Mobile access** — real phone usability, not just "a PWA exists."
- **(d) Code-extension cleanliness** — how cleanly the actual code can be extended or forked.

## THE 10 STANDARD DIMENSIONS (cover every one)
1. **Architecture** — frontend stack, backend stack, data store, how they communicate (REST/WS/SSE).
2. **Extensibility** — tools/functions/plugins/pipelines/filters/custom-UI mechanisms. Name the actual extension points and how they load.
3. **Model + backend support** — Ollama, OpenAI-compatible endpoints, local models, others. Can it point at an arbitrary OpenAI-compatible base URL?
4. **Multi-user / auth** — accounts, roles/RBAC, SSO/OAuth/LDAP, per-user isolation.
5. **Mobile / PWA** — installable PWA? responsive? native apps? real phone usability.
6. **Theming / branding** — custom themes, white-label, logo/name replacement, CSS overrides. (Tie to license clauses if relevant.)
7. **Fork / extend difficulty** — how hard to extend or fork the CODE. Language, modularity, build system, contribution friction, how invasive a deep change is.
8. **License** — exact license + any non-standard clauses (see HIGHEST stakes above).
9. **Maturity / community** — GitHub stars, contributors, release cadence, governance, backing org, momentum (June 2026 state).
10. **MCP support** — see HIGHEST stakes above.

## THE 4 USE-CASE PRIORITIES (score each EXPLICITLY at the end)
For each of (a)/(b)/(c)/(d), give a 1-line verdict + a STRENGTH rating (Strong / Partial / Weak / None) with evidence.
- **THE DISCRIMINATOR — inbound-message surfacing:** Be concrete. Can the fabric push channel/member messages into the UI? Is there a websocket/SSE hook, a custom-panel injection point, an event bus? Or would server-initiated push require a FORK? These platforms are all built request/response (user sends → assistant replies); server-initiated push of unsolicited content into custom panels is the genuinely hard fit. This is THE thing that separates "themeable chat box" from "fabric front-end." Answer it concretely with code/architecture evidence.
- Note: (b) external OpenAI-compatible call-out is trivial for ALL THREE (point at a base URL) — say so but don't let it inflate the score; it does not discriminate.

## OUTPUT
Return your findings as your final message (markdown). Structure: a 2-3 line summary, then the 10 dimensions, then the 4 priorities scored, then a short "Bottom line for the fabric use-case" paragraph naming the single biggest strength and the single biggest gap. Include URLs inline. Mark anything unverified.
Do NOT write the report file yourself — return the full markdown as your message; the lead writes the file.
