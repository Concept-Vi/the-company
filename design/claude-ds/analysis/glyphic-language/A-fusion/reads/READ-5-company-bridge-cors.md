---
type: read
register: descriptive
title: "READ-5 — The Company Bridge / HTTP API + the CORS reality"
tags: [a-fusion, bridge, cors, transport, cognition-api, sse]
status: unconfirmed
coverage:
  files_read: [runtime/bridge.py, canvas/app/vite.config.js, orienteering/entries/company-systemd.md, STATE.md, HANDOFF.md, design/claude-ds/app/index.html]
  bridge_py_lines_total: 3725
  bridge_py_read: "grep-guided targeted read (~600 lines): route table 32-140, _send/_body/do_GET 1425-1560, cog_run_role/items/reduce 1320-1400, projection helpers scanned, /api/corpus-query 1775-1798, SSE _stream 2120-2151, _chat_stream 2153-2209, do_POST 2527-2570, cognition POSTs 3330-3413, tail/bind 3720-3725. NOT a full line-by-line sweep — sufficient for a/b/c/d."
  last_read: 2026-07-01
---

# READ-5 — The Company Bridge, and how a browser reaches the Company AI

**Never-modify constraint honoured:** this is a READ-ONLY map of `~/company`. Nothing here proposes editing the bridge. The recommended path (below) deliberately needs NO bridge change — because adding CORS headers would itself modify `~/company`.

---

## THE HEADLINE — the CORS answer, stated plainly

**Two-part answer. The second part is the one that decides the A-fusion transport:**

1. **Can a served page call `:8770` DIRECTLY, cross-origin? → NO.** Definitive from the code (mechanism proven below).
2. **Does that block the fusion? → NO — because same-origin is the established, working pattern, and the bridge ALREADY serves design pages from its own origin.** The A-fusion page reaches the Company AI with ZERO bridge changes by being served *same-origin*.

So the classic fork "add CORS headers vs serve same-origin" resolves **decisively to SAME-ORIGIN** — which is also the only option compatible with never-modifying `~/company`.

There are **two existing zero-CORS doors** the fusion page can walk through, both Observed in code:

- **Door A — behind the vite proxy** (how the live canvas + phone reach it today). `canvas/app/vite.config.js:17-20`: the dev origin `:5173` proxies `/api`, `/mockups`, and `/design-system.css` straight to `http://localhost:8770`. To the browser every call is **same-origin** (`:5173`), so no CORS is ever involved. The phone reaches this via Tailscale → `:5173` (HANDOFF.md:107).
- **Door B — served by the bridge itself.** `do_GET` (bridge.py:1453-1494) already serves `/` and `/index.html` (the canvas HTML `CANVAS`), `/studio` (302 → `/mockups/STUDIO.html`), the whole `/mockups/*.html` corpus, and `/design-system.css`. A page served from one of these paths is on the `:8770` origin itself → same-origin → no CORS.

**Bottom line for A: don't design a cross-origin fetch client. Design the fusion surface to be served same-origin — either through the vite proxy (Door A, matches the live canvas + the Tailscale phone path) or as bridge-served static (Door B).** Both need nothing added to `~/company`.

---

## (b) The CORS mechanism — why direct cross-origin fails, from the code

**Observed facts in `runtime/bridge.py`:**

- The ONLY response-writing helper is `_send` (bridge.py:1428-1434). It sends exactly `Content-Type` + `Content-Length` and `end_headers()`. **No `Access-Control-Allow-Origin`.** Grep across the whole 3725-line file: **`Access-Control` appears 0 times.**
- The SSE handler `_stream` (bridge.py:2132-2136) and the NDJSON streamers (`_chat_stream` 2183-2187, plus 2278/2370) hand-write their headers — `text/event-stream` / `application/x-ndjson`, `Cache-Control`, `Connection`. **None emit any `Access-Control-*` header either.**
- **No `do_OPTIONS` method exists** on the `H` handler (grep: `do_OPTIONS` = 0 hits). `H` subclasses `http.server.BaseHTTPRequestHandler`, which defines no `do_OPTIONS` (Verified: `hasattr(BaseHTTPRequestHandler,'do_OPTIONS') == False`).

**Consequences (the "from the code" mechanism):**

- **Simple cross-origin GET** (e.g. `GET /api/corpus-query?text=…` from another origin): the request is sent and the server responds 200, **but with no `Access-Control-Allow-Origin` the browser blocks the calling JS from reading the response.** Effectively dead.
- **Any preflighted call** — every JSON-body POST (`/api/cognition/run_role`, `/api/cognition/embed`, `/api/cognition/corpus`), and anything sending a custom header like `X-Operator-Session` — triggers a CORS **preflight `OPTIONS`**. With no `do_OPTIONS`, `BaseHTTPRequestHandler` falls through to `send_error(501, "Unsupported method ('OPTIONS')")`. **The preflight gets a 501, so the browser never sends the real POST.** Dead at preflight.
- **Cross-origin `EventSource`** (for `/api/stream`) also fails — it requires `Access-Control-Allow-Origin` and cannot carry custom headers. Dead.

**What it would take to make direct cross-origin work (NOT recommended — modifies `~/company`):** add `Access-Control-Allow-Origin` (echo/allow the served origin) to `_send` AND to each hand-written streaming header block, PLUS add a `do_OPTIONS` that answers preflight 204 with `Allow-Methods`/`Allow-Headers` (incl. `X-Operator-Session`). Multi-site edit to a shared file. Same-origin (Door A/B) avoids all of it.

---

## (a) The EXACT routes a browser calls — request/response shapes

All are same-origin `/api/...` calls (via Door A or B). `Content-Type: application/json` for POST bodies.

### `POST /api/cognition/run_role` — fire ONE role (bridge.py:3351-3357 → `cog_run_role` 1325-1371)
- **Request body:** `{ "role": "<role_id>", "utterance"?: "", "model"?: "", "inputs"?: {…}, "max_tokens"?: 256, "temperature"?: 0.0, "ensure"?: false, "ensure_evict"?: false }`
  - The **operation is the role's own `op`** (dispatched on `role.op`, not a caller arg) — a generate-role → structured output; an embed-role → a vector.
  - An `inputs` value that *starts with a registered scheme* (e.g. `decision://…`) is resolved as an address; otherwise it's a literal (bridge.py:1350).
- **Response 200:** `{ "role", "op", "output", "address": "run://<turn>/<role>", "turn_id" }`. The output is persisted to CAS + a `cognition.run_role` run-record is emitted.

### `POST /api/cognition/embed` — text → vector (bridge.py:3370-3379 → same `cog_run_role`)
- Embed is **not** a standalone method — it's `run_role` over an `op='embed'` role (default role id `"embed"`).
- **Request body:** `{ "text": "<string>" }` (also accepts `"utterance"`), optional `{ "role"?: "embed", "model"?: "", "inputs"?, "ensure"?: false, "ensure_evict"?: false }`.
- **Response 200:** the run_role envelope whose **`output` is `{ vector, dim, model }`**.
- **Error mode the browser MUST handle:** a **down local embedder FAILS LOUD** (error, not empty) unless `ensure: true` requests the gated model load (bridge.py:3374, `#50`). Observed pattern across cognition routes: engine errors surface as an error JSON (`400`/error body), never a silent empty.

### `GET /api/corpus-query?text=…` — semantic corpus search (bridge.py:1775-1798, S7 forager)
- **Query params:** `text` (**required** — absent → `400 {"error":"…needs ?text=…"}`, fail loud), `space`? (embedding space/lens), `k`? (default 16).
- **Response 200:** `{ "query", "space", "note", "hits": [ { "address", "score", "kind", "projection", "session", "ts_source", "head" }, … ] }` (`head` = first ~400 chars of the record content).
- Note the sibling **`POST /api/cognition/corpus`** (bridge.py:3380-3413) is the WRITE half — capture + embed-on-write; the LINEAGE gate requires `session/round/project` or raises → 400.

*(Companions if the fusion needs them: `POST /api/cognition/run_items` (map over N units, bridge.py:3358), `POST /api/cognition/run_reduce` (join, 3363), `POST /api/chat/stream` and `POST /api/brain/ask` (the RHM mind).)*

---

## (c) The SSE / streaming surface — live transcript + graph-delta flow

Three distinct streaming doors, **all same-origin-only** (no CORS, per above), with **two different browser mechanics**:

- **`GET /api/stream` → EventSource** (bridge.py:2120-2151). `Content-Type: text/event-stream`; framed as `id: <seq>\ndata: <json>\n\n`; cursor via `?since=` or the `Last-Event-ID` reconnect header (default `-1` = from start); `~15s` keepalive. **This tails the SHARED `events.jsonl`, so it carries EVERY event from BOTH faces** — the single global event bus.
  - *(Observed:* it is a general bus over all emitted events. *Inferred (not verified — I did not read the graph-mutation `_emit`):* graph-delta and live-transcript events ride this same bus, so the fusion's live graph/transcript flow is a subscription to `/api/stream` filtered by event type. Mark as inferred until the emit sites are read.)*
- **`POST /api/chat/stream` → fetch + ReadableStream** (bridge.py:2153-2209), NOT EventSource. `Content-Type: application/x-ndjson`, `Connection: close`. Newline-delimited JSON: `{type:part,idx,text,final}` per completed part (incremental display) then a terminal `{type:done,reply,proposal,action,thread_id,history,parts}`, or `{type:error,error,step}`. Body: `{message, graph_id?, focus?}`. Detects client-disconnect to cancel a speculative turn.
- **`POST /api/voice/stream` / `/api/voice/turn`** — the voice siblings, same NDJSON `Connection: close` mechanics.

**FE takeaway:** subscribe to `/api/stream` with `EventSource` for the live event/graph/transcript bus; use `fetch` + a stream reader (NOT EventSource) for the per-turn chat/voice NDJSON.

---

## (d) Auth / security posture

- **Bind: local-only.** `ThreadingHTTPServer(("127.0.0.1", port), H)` at bridge.py:3725; default port `8770`. It listens on loopback only — not `0.0.0.0`.
- **No transport auth on `:8770`.** The code itself says so (bridge.py:549-555): *"on localhost, same-user, there is NO hard cryptographic boundary — :8770 has no transport auth (any local process can curl it, verified)."* READS run FREE (no token) — the corpus/query/run paths work immediately.
- **Operator-session token = a SAFETY (runaway-prevention) boundary, not adversary-proof.** `GET /api/operator-session` mints a per-process token (`_mint_operator_token`, bridge.py:569); consequential writes are meant to require it via header `X-Operator-Session` (bridge.py:3503). Enforcement on the write door is **threaded but not yet activated** (`TODO(#1b)`, bridge.py:3515-3529) — reads and the prove-on-one corpus query need no token today. *If the fusion sends `X-Operator-Session`, note that header would itself force a CORS preflight — another reason same-origin is the clean path.*
- **Remote/mobile reach = Tailscale + TLS, terminated in front of vite, not by the bridge.** `orienteering/entries/config-company.md:32` + `company-systemd.md`: TLS certs (CN = Tim's Tailscale host) are read by the TLS-terminating service; the phone reaches `https://workstation001.tail777bc2.ts.net` → vite `:5173` → proxy `/api` → `:8770` (HANDOFF.md:107). So exposure is **Tailnet-scoped**, and the browser's origin on the phone is the vite/Tailscale origin — **still same-origin to `/api`**.
- **Live-state note:** the bridge is a **shared systemd service** (`company-bridge.service`, `:8770`) — currently one of only two active Company units (`company-systemd.md:47`). A restart blinks every session on the canvas — coordinate; but the fusion never needs to restart it (read-only consumer).

---

## What the current design-system app does today (Observed)

**Nothing touches the bridge yet.** `design/claude-ds/app/index.html` fetches only local `../core/*.jsx` and loads React/Babel from the unpkg CDN — no `:8770`, no `/api`. Every `:8770` / `/api` mention inside `design/claude-ds` lives in **prior analysis markdown** (`analysis/glyphic-language/live-instrument/findings/AREA-1…`), which explicitly left the CORS question **open** — this READ closes it. So the A-fusion transport is a green field: choose the same-origin serving path up front and the wiring is trivial.

---

## 3-line summary

1. **CORS answer, plainly: direct cross-origin to `:8770` = NO** (no `Access-Control-Allow-Origin` on any response; no `do_OPTIONS` → preflight `OPTIONS` gets `501` → every POST/custom-header/EventSource call is blocked) — **but this does NOT block the fusion: serve the page SAME-ORIGIN** (Door A: behind vite's `/api`→`:8770` proxy, exactly how the live canvas + Tailscale phone reach it; or Door B: as a bridge-served page like `/mockups/*`), which needs **zero changes to `~/company`**.
2. **The doors the browser calls (same-origin):** `POST /api/cognition/run_role` `{role,utterance,inputs,…}`→`{output,address,turn_id}`; `POST /api/cognition/embed` `{text}`→`output:{vector,dim,model}` (fails loud if embedder down unless `ensure:true`); `GET /api/corpus-query?text=&space=&k=`→`{hits:[{address,score,head,…}]}`. Live flow: `EventSource GET /api/stream` (the shared all-events bus, `id:/data:` framing, `Last-Event-ID` reconnect) for transcript/graph-deltas; `fetch`+ReadableStream on `POST /api/chat/stream` (NDJSON `part`/`done`) for per-turn chat.
3. **Security: loopback-only bind (`127.0.0.1:8770`), no transport auth (reads free), operator-session token is a runaway-prevention safety not an adversary wall and its write-enforcement is TODO; remote reach is Tailscale+TLS terminated in front of vite — so mobile is still same-origin to `/api`.**

Path: `/home/tim/company/design/claude-ds/analysis/glyphic-language/A-fusion/reads/READ-5-company-bridge-cors.md`
