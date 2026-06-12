---
type: contract-entry
resource: computer-use
summary: Claude Code's reach beyond the editor — WebFetch (fetch+extract a URL, lossy by design) and WebSearch (native session tools), the Claude-in-Chrome browser-automation integration (open tabs, click, type, read console; beta, not WSL), and the API computer-use tool (screenshot+mouse/keyboard, beta header). Native in-session/in-browser capabilities; the company spawns sessions with mcp__company ONLY, so none are granted by default — contracted as the native surface with the gap named.
schemes: []
status: planned
relates-to: ["[[session]]", "[[permission]]", "[[headless-control]]", "[[knowledge-corpus]]"]
---

# Resource: computer-use

> **Refocus (Session Fabric R1.4, 2026-06-13):** the company command-wrapper endpoints this entry once cited (the ③④⑤ MCP tools + `/api/config|dev|auto` bridge arms + the R3 config_writer rail) were REMOVED — they duplicated what a real Claude Code session does natively. The capability is reached by DRIVING A REAL SESSION (the supervisor's spawn/inject + R1-prime profile); this entry remains as the NATIVE data-model declaration a UI renders. Ops whose only real endpoint was the wrapper are back to `planned` — honestly.
## Identity
**Computer/web reach is keyed by the SESSION that wields it (`session://<id>`) — there is no
`computer-use://` scheme.** Atlas class CC-17 spans three distinct native surfaces, kept apart in
the corpus: (1) WEB ACCESS — the `WebFetch`/`WebSearch` session tools
(`tools-reference.md#webfetch-tool-behavior`, `web-fetch-tool.md`, vault
`claude-code-atlas`/`claude-platform-docs`); (2) BROWSER AUTOMATION — the Claude-in-Chrome
extension integration (`chrome.md`, beta, Chrome/Edge only, NOT WSL); (3) COMPUTER USE — the API
computer-use tool (screenshot + mouse/keyboard, `computer-use-tool.md`, beta header
`computer-use-2025-11-24`). HONEST STATUS: all three are `planned` against the company. They are
native session/browser/API capabilities, and crucially the company spawns every session with
`--allowedTools mcp__company` ONLY ([[permission#Representation]]), so even WebFetch/WebSearch are
NOT in a fabric session's grant by default, and the company exposes no endpoint to drive a browser
or computer-use loop. The gap is named per op; the Chrome path is additionally blocked on WSL (the
company's host).

## Representation
**Web/computer reach is three native tool surfaces a session MAY have, each with its own grant +
mechanics — WebFetch (lossy URL→markdown→small-model extraction), WebSearch, the Chrome
browser-automation tool set, and the API computer-use action set — none granted to a fabric session
by default.**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/computer-use.surface",
  "type": "object",
  "description": "the three native reach surfaces (sources tools-reference.md, chrome.md, computer-use-tool.md). The company grants none by default",
  "properties": {
    "web_fetch": { "type": "object", "description": "WebFetch: takes URL+prompt, fetches, converts HTML→markdown, runs the prompt via a small fast model — LOSSY (Claude gets the model's answer, not the raw page). HTTP→HTTPS upgrade, 15min cache, cross-host redirect returns a notice (second call follows). Domain-gated: prompts on first new domain except preapproved doc domains; WebFetch(domain:x) allow/deny/ask rules" },
    "web_search": { "type": "object", "description": "WebSearch: search the web; pairs with WebFetch (search to locate a named page, then fetch). API tool types web_search_20250305 / web_fetch_20250910" },
    "chrome": { "type": "object", "description": "Claude-in-Chrome: opens tabs, clicks/types, reads console/network, fills forms, extracts data; shares your browser login state; pauses for login/CAPTCHA. BETA, Chrome/Edge only, site perms inherited from the extension. NOT supported on WSL" },
    "computer_use": { "type": "object", "description": "API computer-use tool: screenshot capture + mouse(click/drag/scroll) + keyboard(type/keys). BETA header computer-use-2025-11-24 (Opus 4.8/4.7/4.6, Sonnet 4.6, Opus 4.5). Needs OS accessibility perms; may not work headless" } } }
```
| field | type | volatile? | changed-by | address? → resource | reality (2026-06-12) |
|---|---|---|---|---|---|
| web_fetch / web_search | object | no (tool capability) | the session's tool grant | — | NATIVE session tools; NOT in a fabric session's `--allowedTools mcp__company` grant ([[permission]]). Granting them = a planned spawn-permission extension ([[permission#op: permission.act]]) |
| chrome | object | no | the Chrome extension + grant | — | NATIVE; beta, Chrome/Edge only. BLOCKED on WSL (the company host is WSL2) — `chrome.md`: "WSL is also not supported". No company face drives it |
| computer_use | object | no | API beta header + OS perms | — | NATIVE API tool; needs a beta header + OS accessibility perms. No company face; the company's headless spawn does not set the computer-use beta or grant the tool |

## State model
**State model: stateless (per-session/per-call tool capabilities).** Web/computer reach has no
lifecycle of its own — each is a tool the model calls within a turn. A Chrome automation session
has visible browser state (open tabs, login), but that lives in the browser, not in any company
state machine; computer-use is per-action (screenshot → act → screenshot).

## Caller
**Inside a session the caller is the model (these are the model's tools, gated by permission rules);
from outside there is no caller because no company endpoint drives them.** WebFetch/WebSearch are
permission-gated like any tool: in default/acceptEdits the first hit on a new domain prompts (except
preapproved doc domains), and `auto`/`bypassPermissions` skip the prompt — so a fabric session in
the default `plan` posture ([[permission]]) would not even have these in its grant. Chrome site
permissions come from the extension itself; computer-use needs OS-level accessibility grants. The
nearest real seam to surface any of this through the company is the spawn-permission extension
([[permission#op: permission.act]]) plus reading the session stream ([[headless-control]]) — both
`planned`.

## Operations

## op: computer-use.act
**`computer-use.act` is the PLANNED reach bridge: drive WebFetch/WebSearch, a Chrome
browser-automation step, or a computer-use action for a session — the native capabilities the
company does not expose (and that a default fabric session is not even granted), named here so a UI
knows the real boundary and the spawn-permission + host (WSL) constraints.**
```contract:op
op: computer-use.act
resource: computer-use
kind: act
status: planned
direction: outbound
atlas: [CC-17.1, CC-17.2, CC-17.3]
tasks:
  - phrase: "fetch a web page and extract what it says about X"
    params: {act: web-fetch}
  - phrase: "search the web for recent articles on Y"
    params: {act: web-search}
  - phrase: "open the app in a browser and click through the onboarding"
    params: {act: browser}
  - phrase: "screenshot the screen and click the button"
    params: {act: computer}
  - alias: "web access"
  - alias: "browser automation"
  - alias: "control the computer"
  - alias: "take a screenshot and click"
bindings: []
liveness: none
emits: []
consequences:
  - when: "web-fetch / web-search (planned — would run as native session tools)"
    expect: []
    bound: "n/a — not built; natively a fetch is lossy (small-model extraction), 15min-cached, domain-gated"
    evidence: "no company-visible structured outcome; in a granted session the tool result reaches the model and surfaces only in the FOLDED text/tool frames ([[headless-control#op: headless-control.watch]])"
  - when: "browser / computer (planned)"
    expect: []
    bound: "n/a — not built; Chrome is NOT WSL-supported (the company host), computer-use needs OS accessibility perms + a beta header"
    evidence: "no company face; native browser actions run in a visible Chrome window, computer-use as screenshot→act loops — neither is observable through the company"
correlate: [session]
verification:
  web:      {state: unverified, note: "WebFetch/WebSearch native but not in the fabric grant; no company endpoint — planned"}
  browser:  {state: unverified, note: "Chrome integration beta + NOT supported on WSL (the company host); no company face — planned"}
  computer: {state: unverified, note: "API computer-use needs beta header + OS perms; no company face — planned"}
```
### Description (purpose-free)
Three native reach capabilities, contracted as a planned company bridge. (1) WEB ACCESS: WebFetch
takes a URL + an extraction prompt, fetches, converts HTML to markdown, and runs the prompt through
a small fast model — so the result is the model's answer, NOT the raw page (lossy by design; a <!-- lint-ok: "page" = WebFetch's native web-page result, F7 carve-out (CONVENTIONS) -->
"page doesn't mention X" may just mean the prompt didn't ask). HTTP upgrades to HTTPS, large pages <!-- lint-ok: native WebFetch behavior, F7 carve-out -->
truncate, results cache 15 minutes, cross-host redirects return a notice. Domain access is
permission-gated (preapproved doc domains fetch silently; `WebFetch(domain:...)` allow/deny/ask
rules override). WebSearch pairs with it. (2) BROWSER AUTOMATION: the Claude-in-Chrome extension
lets a session open tabs, click, type, read console/network logs, fill forms, and extract data, <!-- lint-ok: native Claude-in-Chrome actions, F7 carve-out -->
sharing the browser's login state and pausing for login/CAPTCHA — beta, Chrome/Edge only, and NOT
supported on WSL. (3) COMPUTER USE: the API tool captures screenshots and drives mouse/keyboard for
GUI automation (beta header, OS accessibility perms). The company exposes none of these and does not
even grant WebFetch/WebSearch to a default fabric session — this op names the gap, the grant path,
and the host (WSL) constraint on Chrome.
### Request (PLANNED shape — the contract the seam should fulfil)
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/computer-use.act.request",
  "type": "object",
  "required": ["session", "act"],
  "properties": {
    "session": { "type": "string", "description": "session://<id> that would wield the tool (must be granted it — see [[permission#op: permission.act]])" },
    "act":     { "enum": ["web-fetch", "web-search", "browser", "computer"] },
    "url":     { "type": "string", "description": "act=web-fetch: the URL (HTTP auto-upgraded to HTTPS)" },
    "prompt":  { "type": "string", "description": "act=web-fetch: the extraction prompt (determines what reaches the model — lossy)" },
    "query":   { "type": "string", "description": "act=web-search: the search query" },
    "browser_action": { "type": "object", "description": "act=browser: open/click/type/read-console (Chrome integration) — Chrome/Edge only, not WSL" },
    "computer_action": { "type": "object", "description": "act=computer: screenshot/click/type/key (API computer-use, beta)" } },
  "additionalProperties": false }
```
### Interaction semantics
Native rules a consumer MUST respect when this op lands (sourced to the docs):
- **WebFetch is lossy and uncacheable-control.** The HTML→markdown→small-model conversion is not
  configurable; for the raw page, use `curl` via Bash. Repeated same-URL fetches return from the <!-- lint-ok: "page" = native web-page result (WebFetch), F7 carve-out -->
  15-minute cache.
- **Domain gating.** Default/acceptEdits prompt on a new domain (except preapproved doc domains);
  `auto`/`bypassPermissions` skip it; explicit `WebFetch(domain:...)` deny/ask/allow rules take
  precedence — and a fabric session's grant (`mcp__company` only) excludes WebFetch entirely.
- **Sandbox network is separate.** A sandboxed process still needs an explicit sandbox network rule
  even for an allowed WebFetch domain.
- **Chrome: WSL not supported.** The company host is WSL2 (`Linux ...-microsoft-standard-WSL2`), so
  the Chrome integration cannot run there — a hard host constraint, not a soft preference.
- **Computer-use: beta + perms.** Requires the beta header and OS accessibility permissions; may not
  work headless.
### Errors
```contract:error
code: computer-use.not-exposed | http: 501 | retryable: false
when: any call against this op today
teach: "Web/browser/computer reach is PLANNED — no company endpoint drives it, and a default fabric session is granted only mcp__company (no WebFetch/WebSearch). To use web access today, grant the tools to a session ([[permission#op: permission.act]], planned) or run a native session with WebFetch/WebSearch allowed. Chrome automation is NOT supported on WSL (this host); computer-use needs an API beta header + OS perms."
```
```contract:error
code: computer-use.not-granted | http: 409 | retryable: false
when: (when built) act=web-fetch/web-search against a session not granted the tool
teach: "The session's permission posture does not include WebFetch/WebSearch (the fabric default is --allowedTools mcp__company, [[permission#Representation]]). Add the tool via the planned spawn grant ([[permission#op: permission.act]] allow:[WebFetch, WebSearch])."
```
```contract:example
captured: synthetic            # status=planned → synthetic legal AND loud; no company computer-use endpoint, Chrome not on WSL (V11)
binding: http
request: |
  POST /api/computer-use HTTP/1.1   (PLANNED — endpoint does not exist)
  {"session":"as-91cf4502","act":"web-fetch","url":"https://example.com/docs","prompt":"what auth methods are supported?"}
response: |
  HTTP/1.1 501 Not Implemented
  {"error":"Web/computer reach is planned; no company endpoint drives it and the fabric grants only mcp__company. Grant WebFetch via the planned permission.act, or run a native session. Chrome automation is not supported on WSL (this host)."}
```
Adjacent: [[permission#op: permission.act]] (the grant a session needs to even hold these tools),
[[headless-control#op: headless-control.watch]] (where a tool result would surface, folded),
[[knowledge-corpus#op: knowledge-corpus.search]] (the docs on WebFetch/Chrome/computer-use).

## Errors
**Resource-level error vocabulary: `computer-use.not-exposed` (the honest 501 — no company face, and
a default fabric session isn't even granted WebFetch/WebSearch) and `computer-use.not-granted` (the
permission-posture refusal a built face would return).** Both teach the live recovery — grant the
tool via the planned spawn permission, run a native session, and respect the hard WSL constraint on
Chrome — and name the gap. No error claims a reach face the company has not built.

## Links
**No address-typed fields: web/computer reach references the `session://` that would wield it
(dereferences to [[session]]) and external URLs/queries (web resources, not corpus addresses).**
Fetched content, search results, screenshots, and browser state are external/transient artifacts,
not fabric records — they never resolve to a corpus entry, by design, since the whole surface is a
planned, ungranted, partly-host-blocked native capability.
