---
type: contract-entry
resource: remote
summary: Reaching the Company from another device — the REAL path is the operator's phone over Tailscale (tailnet HTTPS via `tailscale serve` to the bridge + canvas, installed as a full-screen PWA); native Claude Code Remote Control + Deep Links are the Anthropic-hosted alternative, contracted as the native surface with the company-vs-native distinction named.
schemes: []
status: building
relates-to: ["[[fabric-config]]", "[[voice]]", "[[session]]", "[[events]]"]
---

# Resource: remote
## Identity
**Remote access is keyed by the TRANSPORT VANTAGE a consumer reaches the Company from — localhost
vs tailnet — not by a device record; there is no `remote://` scheme.** Atlas class CC-15 covers
two distinct things, and the corpus keeps them apart: (1) the COMPANY's own remote path — the
bridge + canvas served over Tailscale HTTPS to Tim's iPhone PWA, which is DONE and working
(`project-mobile-access-tailscale`, verified on-device); (2) NATIVE Claude Code Remote Control
(`--remote-control`, claude.ai/code + the Claude mobile app) and Deep Links (`claude://`), an
Anthropic-hosted relay that is a SEPARATE, un-bridged capability (source `remote-control.md`,
`deep-links.md`, `glossary.md#remote-control`, vault `claude-code-atlas`). The two never blur: the
Company path keeps everything on-machine over the tailnet; native Remote Control routes through the
Anthropic API. This resource contracts both, each op marking which.

## Representation
**The Company remote surface is the set of bridge/canvas endpoints reachable from a given vantage,
governed by the bind config + the `tailscale serve` mapping; the native surface is a Remote Control
session record (a relay registration with a session URL + QR).** Two shapes, two grains.
### (1) Company tailnet vantage (REAL)
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/remote.tailnet-vantage",
  "type": "object",
  "properties": {
    "tailnet_host": { "type": "string", "description": "the MagicDNS name — workstation001.tail777bc2.ts.net (verified)" },
    "served": { "type": "array", "items": { "type": "string" },
                "description": "what tailscale serve maps over HTTPS: the canvas (vite :5173) and the bridge API (:8770)" },
    "https": { "type": "boolean", "description": "Tailscale-issued cert — true (the toggle Tim enabled); REQUIRED for the iOS browser mic (getUserMedia secure-context)" },
    "pwa": { "type": "boolean", "description": "installed full-screen (apple-mobile-web-app-capable + gold Vi icon) — true" } } }
```
### (2) Native Remote Control session (Anthropic-hosted — NOT a company face)
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/remote.native-control-session",
  "type": "object",
  "description": "the native --remote-control session as documented; the company does NOT run this — contracted so a UI knows the alternative",
  "properties": {
    "name": { "type": "string", "description": "title order: --name/--remote-control/--rename > history > auto (myhost-graceful-unicorn)" },
    "session_url": { "type": "string", "description": "claude.ai/code/session_<id> — opens the session in the browser/app" },
    "connection": { "enum": ["outbound-only"], "description": "the local session makes OUTBOUND HTTPS only, never opens an inbound port; registers + polls the Anthropic API" } } }
```
| field | type | volatile? | changed-by | address? → resource | reality (2026-06-12) |
|---|---|---|---|---|---|
| tailnet_host | string | no | operator (tailscale) | — | workstation001.tail777bc2.ts.net — LIVE, verified on iPhone (`project-mobile-access-tailscale`) |
| served | array | no | `tailscale serve` config | — | canvas :5173 + bridge :8770 over tailnet HTTPS; `tailscale` service row in ops/services.json (group reach, system-unit, kept enabled at boot) |
| https | bool | no | Tailscale admin DNS | — | true — cert enabled; the secure-context the browser mic needs ([[voice#Caller]]) |
| native session_url | string | yes | the native relay | — | N/A in company — native Remote Control is NOT wired (no --remote-control in company code; verified grep) |

## State model
**State model: stateless (a vantage/availability description).** The Company tailnet surface has no
session lifecycle of its own — it is the bind+serve configuration through which the bridge's own
resources (sessions, voice, events) are reached. A NATIVE Remote Control session DOES have a
lifecycle (active → reconnect-on-drop → times-out after ~10min offline → process-exit ends it), but
that lifecycle lives in the Anthropic-hosted relay, not in any company state machine.

## Caller
**Over the tailnet the caller is the operator's own device on the private tailnet (anonymous-local
from the bridge's view — tailscaled reaches 127.0.0.1:8770/:5173 directly, no inbound port opens on
the host); there is no public exposure and no auth layer, the tailnet membership IS the boundary.**
This is the recorded mobile-access decision (the B3-class exposure ruling): the bridge binds
localhost, and `tailscale serve` is the ONLY widening — a deliberate, recorded step, not an open
port. Native Remote Control's caller model is different (claude.ai account, multiple short-lived
scoped credentials through the Anthropic API) and is documented for contrast, not operated here.

## Operations

## op: remote.get
**`remote.get` is the reach read: from this vantage, what of the Company is reachable and how —
the tailnet host, what `tailscale serve` exposes, whether HTTPS+PWA are in place — so a consumer
(or a UI rendering a "connect from your phone" affordance) knows the real path rather than guessing.**
```contract:op
op: remote.get
resource: remote
kind: get
status: building
direction: outbound
atlas: [CC-15.1, CC-15.3]
tasks:
  - phrase: "how do I reach the company from my phone"
  - phrase: "what's the tailnet address for the surface"
  - phrase: "is the bridge served over https for mobile"
  - alias: "mobile access"
  - alias: "tailscale path"
  - alias: "connect from another device"
bindings:
  - { kind: http, method: GET, path: /api/now, transport: bridge-http, exposure: "exposure.json#bridge-http", note: "the bridge's liveness read — reached over the tailnet HTTPS origin proves the remote path works (the health the PWA hits). The serve MAPPING is config (tailscale serve), not a bridge route; this op reads reachability, and the mapping is named in Representation" }
  - { kind: cli, command: "company status   (the `tailscale` reach row + `bridge`/`canvas` core rows show what's up to serve)", transport: cli-local, exposure: "exposure.json#cli-local", note: "tailscale = system-unit kept enabled at boot (ops/services.json reach group)" }
liveness: snapshot
live-twin: "[[fabric-config]] (bind config + service up-state); the tailscale serve mapping is operator config, changed by a recorded decision"
emits: []
verification:
  reachability: {state: probe-verified, run: "project-mobile-access-tailscale: bridge+canvas served at https://workstation001.tail777bc2.ts.net/, PWA installed, verified on Tim's iPhone (latency ~1-5ms direct); survives reboot via company.target", date: 2026-06-12, note: "the on-device PATH is proven; the harness has not re-captured it from the corpus-only vantage"}
```
The Company's mobile story is the tailnet PWA, NOT native Remote Control: the phone reaches the
SAME local bridge/canvas the desktop does, over a private tailnet HTTPS origin. That HTTPS origin
is load-bearing beyond convenience — it is the secure context the iOS browser mic requires, so it
is what makes browser voice-in work on the phone ([[voice#Caller]]). A native iOS app would only
be needed for eyes-off/locked-screen voice (a later, separate step).
```contract:example
captured: synthetic            # status=building — the path is on-device-proven; this read is illustrative until harness-captured (V11)
binding: http
request: |
  GET /api/now HTTP/1.1
  Host: workstation001.tail777bc2.ts.net
response: |
  HTTP/1.1 200 OK
  {"ok": true, "served_over": "tailnet-https", "reachable": true}
```
Adjacent: [[remote#op: remote.act]] (the native Remote Control alternative), [[voice#op: voice.watch]]
(why the HTTPS origin matters), [[fabric-config#op: fabric-config.get]] (the bind/exposure posture).

## op: remote.act
**`remote.act` is the PLANNED bridge to NATIVE Claude Code Remote Control / Deep Links — start a
`--remote-control` session, open a `claude://` deep link — the Anthropic-hosted relay the company
does NOT run today, contracted so a UI knows the native alternative exists and is reached outside
the fabric, with the un-bridged boundary named.**
```contract:op
op: remote.act
resource: remote
kind: act
status: planned
direction: outbound
atlas: [CC-15.2, CC-15.4]
tasks:
  - phrase: "make this session controllable from my phone via the claude app"
    params: {act: remote-control}
  - phrase: "open a claude code session from a web link"
    params: {act: deep-link}
  - alias: "remote control a session"
  - alias: "continue a session on claude.ai/code"
  - alias: "claude:// deep link"
bindings:
  - { kind: tui, command: "claude --remote-control [name]  /  /remote-control  /  /mobile (QR)", transport: tui-interactive, exposure: "n/a — interactive", status: planned, note: "NATIVE: the local session registers with the Anthropic API and polls; claude.ai/code + the Claude mobile app connect. The COMPANY does not wire this (no --remote-control anywhere in ~/company; verified grep). Research preview; off-by-default on Team/Enterprise" }
  - { kind: sdk, command: "claude:// deep link (passes prompt/model/workspace) — routes web→desktop", transport: agent-sdk, exposure: "n/a — Agent SDK in-process", status: planned, note: "NATIVE Deep Links (deep-links.md). The company has no deep-link handler; web→Company is the tailnet URL, not claude://" }
liveness: none
emits: []
consequences:
  - when: "native remote-control started (planned — outside the fabric)"
    expect: []
    bound: "n/a — not a company endpoint"
    evidence: "no company-visible outcome; the native session shows in claude.ai/code with a green status dot. The company path is [[remote#op: remote.get]] (tailnet), a different mechanism — named so a UI does not conflate them"
correlate: [session]
verification:
  remote-control: {state: unverified, note: "no company bridge to native Remote Control — planned; the company's mobile path is the tailnet PWA, deliberately not the Anthropic relay"}
  deep-link:      {state: unverified, note: "no claude:// handler in the company — planned"}
```
### Description (purpose-free)
Two native capabilities the company does NOT bridge, contracted so a UI knows the alternative.
(1) Remote Control: `claude --remote-control [name]` (or `/remote-control`) makes a LOCAL session
controllable from claude.ai/code or the Claude mobile app — the local process keeps running and
makes outbound-only HTTPS, the relay routes messages, and the conversation stays in sync across
terminal/browser/phone; some pickers (`/plugin`, `/resume`) stay local-only while text commands
(`/compact`, `/clear`, `/context`, `/usage`, and as of v2.1.166 `/mcp`) work from mobile/web
(source `remote-control.md`). (2) Deep Links: the `claude://` URL scheme passes an initial
prompt/model/workspace to launch a session (web→desktop). The COMPANY'S remote story is
deliberately different — the tailnet PWA ([[remote#op: remote.get]]) keeps everything on-machine —
so these natives are `planned`, un-bridged, named-as-the-boundary, never claimed live.
### Errors
```contract:error
code: remote.native-not-bridged | http: 501 | retryable: false
when: any call asking the company to start native Remote Control or handle a claude:// deep link
teach: "The company does not bridge native Remote Control / Deep Links — its mobile path is the tailnet PWA ([[remote#op: remote.get]]). To use native Remote Control, run `claude --remote-control` directly (Anthropic-hosted relay, claude.ai/code + mobile app), outside the fabric."
```
```contract:example
captured: synthetic            # status=planned → synthetic legal AND loud; no company remote-control bridge exists (V11)
binding: tui
request: |
  (native, outside the fabric)
  $ claude --remote-control couch-session
response: |
  /remote-control is active. Code in CLI or at https://claude.ai/code/session_01EbtMVdffBYsfZuEFKNAf6v
  (the company offers NO equivalent endpoint — reach the Company via the tailnet PWA instead)
```
Adjacent: [[remote#op: remote.get]] (the REAL company path), [[session#op: session.list]] (the
fabric sessions a tailnet consumer drives), [[voice#op: voice.watch]] (voice over the tailnet origin).

## Errors
**Resource-level error vocabulary: `remote.native-not-bridged` (the honest 501 for any request to
operate native Remote Control / Deep Links through the company).** It teaches the real recovery —
use the tailnet PWA for the company, or run native `claude --remote-control` directly outside the
fabric. No error implies the company runs the Anthropic relay; the company-vs-native boundary is
stated, not blurred.

## Links
**No address-typed fields: the tailnet surface references a MagicDNS host + bound ports (config,
not a corpus scheme); a native Remote Control session carries a claude.ai/code URL (an
Anthropic-hosted URL, not a fabric address); `claude://` is a native deep-link scheme, not a
company address.** None resolve to a corpus entry — by design, since the native surface is
un-bridged and the company path is reachability config, not addressable records.
