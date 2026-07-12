# COMPANY FRONTEND — MECHANISMS INVENTORY (read 2026-07-13; for the claude-ds replacement)

Scope read: `surface/app/` (the Vite/React thin-client PWA), `runtime/bridge.py` (the HTTP face, 3861 lines),
`contracts/address.py` (527 lines, the address grammar), `contracts/ui_info.py` (450 lines, the `ui://` layer),
plus `canvas/` (a SECOND, separate frontend bridge.py also serves — flagged below, not in the original brief).

---

## 0. IMPORTANT — there are TWO frontends bridge.py serves, not one

The brief named `surface/app/` (the Vite/React PWA) as "the existing thin-client PWA." That is real and is the
richer of the two. But `runtime/bridge.py`'s `do_GET` serves a DIFFERENT app at the bare root:

- `GET /` and `/index.html` → `canvas/index.html` (`runtime/bridge.py:1487-1490`, `CANVAS = .../canvas/index.html`
  at `runtime/bridge.py:26`). `canvas/` is documented (`canvas/AGENTS.md:12-19`) as "the frontend — the surface
  Tim operates (tldraw + React + Tauri)" with **one generic `ai-node` shape** driven by `/object_info`, NOT
  `surface/app`. `canvas/app/` is its own separate Vite/React project (`canvas/app/package.json`,
  `canvas/app/src/`), distinct from `surface/app/`.
- `surface/app/` (the PWA this report otherwise covers) is NOT one of bridge.py's static-served paths at all —
  it is a separate Vite dev-server/build that proxies `/api` calls to the bridge on `:8770` (per
  `surface/app/src/lib/api.ts:1` — "THIN, FAIL-LOUD CLIENT over the bridge (:8770 via the /api proxy)"). It has
  its own `dist/` (`surface/app/dist/index.html`, `surface/app/vite.config.ts`) and is presumably served by
  whatever hosts that build (not visible in bridge.py).
- `/studio` (`runtime/bridge.py:1492-1501`) 302-redirects to `/mockups/STUDIO.html`, a THIRD static surface (the
  Mockup Studio — a design-review gallery of static HTML mockups under `design/mockups/`, `runtime/bridge.py:150-152,
  1520-1559`), with its own click-capture injection for `?studio=1` (element-deixis, `runtime/bridge.py:1523-1552`).
- `/design-system.css` (`runtime/bridge.py:1502-1507`) serves a generated stylesheet consumed by the mockups.

**Consequence for the replacement:** confirm with Tim/lead which of these three is actually in daily use before
assuming `surface/app/` is the one to replace — bridge.py's own root route serves `canvas/`, not it.

---

## 1. The API surface

`runtime/bridge.py` keeps a single declared route table, `BRIDGE_ROUTES` (`runtime/bridge.py:44-148`), which a
test (`tests/bridge_routes_acceptance.py`, per the comment at `runtime/bridge.py:39-42`) greps against the actual
`path ==` / `self.path ==` dispatch literals so the table can't drift from what's dispatched. `Suite.capabilities()`
projects the `/api/*` subset of this table as `api_verbs` (`runtime/bridge.py:35-38`).

### Non-API served paths (excluded from `api_verbs`, in the table per `runtime/bridge.py:45-47`)
| Path | Purpose |
|---|---|
| `/`, `/index.html` | serves `canvas/index.html` (`runtime/bridge.py:1487-1490`) |
| `/studio` | 302 → `/mockups/STUDIO.html` (`:1492-1501`) |
| `/design-system.css` | generated mockup stylesheet (`:1502-1507`) |
| `/mockups/*.html` | static mockup gallery, path-safe basename resolve (`:1520-1559`, `_safe_mockup_path` `:155-166`) |
| `/api/image/<id>` | prefix route — image bytes by id via `cc_images.image_bytes` (`:1508-1519`) |

### GET routes (consumed today mainly by `surface/app` via `surface/app/src/lib/api.ts`)
Grouped by what `surface/app` actually calls (verified against `api.ts`/stores) vs. the rest of the declared surface.

**Consumed by `surface/app` today:**
| Path | Bridge line | Purpose | Consumer |
|---|---|---|---|
| `/api/projection` | `bridge.py:1806` | THE UNIVERSAL PROJECTION — θ=kind/r=time-from-now/depth=nesting rendering of the corpus, resolved from a `binding` (lens) | `api.ts:135-139 fetchProjection`, `App.tsx:406-449` |
| `/api/context` | `:1965` | R2 scored context bundle at an address | `api.ts:141-143 fetchContext` |
| `/api/territory` | `:1928` | scheme-agnostic SOURCE resolver — the comprehended record + provenance behind an address (`territory_for`) | `api.ts:146-148 fetchTerritory`, `App.tsx:310` (Source verb), `decisionsStore.ts:124` (enrich) |
| `/api/layers` | `:1768` | multi-layer embedder self-description `{space:[layer,…]}` | `api.ts:152-154`, `App.tsx` SpaceChip/LayerChip, `toolsStore.ts:99` (enumSources) |
| `/api/layer-dims` | `:1770` | per-layer full vector dim (MRL ladder source) | `api.ts:159-161` |
| `/api/stream` | own handler, `:1485`/`:2203` | SSE event tail — see §3 | `App.tsx:454-508` (live pulse + corpus-start scrubber floor) |
| `/api/territory/label` | `:1911`(≈ label variant) | human aim-label for a `ui://` address (operator-law: never raw address) | `RightHand.tsx:193,298` |
| `/api/decisions` | `:1580` | the decisions INBOX feed (pending operator decisions) | `decisionsStore.ts:71` |
| `/api/channels` | `:1635` | live fabric roster (channel registry) | `channelStore.ts:50`, `RightHand.tsx:148` (post picker) |
| `/api/board` | `:1663` | Noticeboard items as data | `boardStore.ts:47` |
| `/api/sessions` | `:1641` | agent-session fleet list | `sessionDrillStore.ts:64` |
| `/api/session-recall` | `:1706` | per-session lens (`catch_up`/`open_loops`/`directives`/…) | `sessionDrillStore.ts:89-101` |
| `/api/transcript-search` | `:1684` | whole-corpus semantic/lexical search over transcripts | `transcriptStore.ts:71` |
| `/api/tools` | `:2173` | interactive MCP tool list (name/schema/posture/form_meta) | `toolsStore.ts:233` |
| `/api/resolve` | POST, `:2868` | device-coordinate → CSS allocation resolver (rules AST) | `resolveAllocation.ts:65` |
| `/api/operator-session` | `:1796` | mints the per-session operator token | `operatorSession.ts:53` |
| `/api/decision/update/accept` | POST, `:2716` | operator applies an RHM-proposed card refinement | `App.tsx:386` |
| `/api/territory/write` | POST, `:3598` | route-back write at a `ui://` sub-address (decision take, comment) | `App.tsx:366` (fallback), `RightHand.tsx` via `forkVBrain.direct` |

**Declared but not observed called from the read files above** (still real routes per the table — many are FACE-1/
FACE-4/voice/cognition-authoring surfaces not wired into `surface/app`'s read files): `/api/mockup-feedback(+/status)`,
`/api/corpus`, `/api/graph(s)`, `/api/object_info`, `/api/cognition_info`, `/api/type_info`, `/api/types`,
`/api/models`, `/api/chat-models`, `/api/fit`, `/api/surfaced`, `/api/events`, `/api/now`, `/api/chat`,
`/api/conversations(+/conversation)`, `/api/rhm-config`, `/api/inbox`, `/api/last-change`, `/api/self-change-log`,
`/api/panels`, `/api/capabilities(+/introspection)`, `/api/ui_info`, `/api/scope`, `/api/pages`, `/api/address-help`,
`/api/may`, `/api/access-of`, `/api/keeper`, `/api/up-translate`, `/api/self-changes-at`, `/api/annotations`,
`/api/presentation-pref`, `/api/chats`, `/api/address-history`, `/api/stale-at`, `/api/ref-versions`,
`/api/review/current(+/status)`, `/api/journey/replay`, `/api/journeys`, `/api/voice`, `/api/personas`,
`/api/trial/sessions(+/transcript)`, `/api/cognition/*` (models_for_role/inputs/field_types/list_runs/find_runs/
find_relations/corpus/neighbours), `/api/roles`, `/api/run-stats`, `/api/knobs`, `/api/voice/engine-knobs(+/paths)`,
`/api/timeline`, `/api/cascades`, `/api/flows`, `/api/routines`, `/api/channel-history`, `/api/session-describe`,
`/api/stack-item-types`, `/api/supervisor/sessions(+/health)`, `/api/registry/proposals`.

Full table: `runtime/bridge.py:48-73` (GET), `:74-129` (POST), plus the drift-caught additions at `:130-148`
(`/api/channels`, `/api/sessions`, `/api/timeline`, `/api/board`, `/api/cascades`, `/api/flows`, `/api/routines`,
`/api/transcript-search`, `/api/session-recall`, `/api/channel-history`, `/api/session-describe`,
`/api/stack-item-types`, `/api/brain/ask`, `/api/run-in-channel/propose`, `/api/decision/explain`,
`/api/decision/decided-signals`, `/api/operator-session`, `/api/channel/post`, `/api/decision/update(+/accept)`,
`/api/decision/propose(+/proposals)`, `/api/chat/stream`, `/api/voice/stream`, `/api/voice/turn`,
`/api/registry/proposals(+/approve)`).

### POST routes (dispatched, `do_POST` at `runtime/bridge.py:2617`)
Notable consequential ones actually ridden by `surface/app`:
- `/api/resolve` (`:2868`) — pure computation, host allocation resolver.
- `/api/territory/write` (`:3598`) — the one write-back door for comments/annotations/decision-takes at a
  `ui://` sub-address (route-back, `App.tsx:361-366`).
- `/api/decision/update/accept` (`:2716`) — L5 accept of an RHM-proposed update; gated by the `X-Operator-Session`
  token (`operatorSession.ts:1-33` explains the gate).
- `/api/tools/invoke` (`:3619`) — the generic tool-invoke door (GAP 3), fail-closed operator gate
  (`runtime/bridge.py:82-84`, `:675-750` denylist + posture gate). **Not yet called from `surface/app`** — the
  ToolsPanel's Run action is an explicit pending seam (`ToolsPanel.tsx:9-15`).
- `/api/brain/ask` (`:2625`) — the RHM/V's supervisor-brain source-router; consumed via `forkVBrain` (an
  externally-injected `window.forkVBrain`/`window.forkBrainCore` global — NOT in `surface/app/src`; it's loaded
  from elsewhere, e.g. `public/gallery/fork-*.js`, see §5).
- `/api/say` (`:3097`) — server-side voice (TTS) for the RHM.
- `/api/stt`, `/api/tts`, `/api/voice/*` (`:2889-3411` range) — the voice pipeline (STT partial, TTS, finished-
  thought judge, engine switch, client log).

Full POST dispatch chain: `runtime/bridge.py:2617-3861` (do_POST body), route comments inline at each `elif
self.path ==` (grep list captured during this read — 60+ POST routes total).

---

## 2. The address system

### The grammar (`contracts/address.py`)
`SCHEMES` (`contracts/address.py:162`): `run, cas, blob, vec, ui, code, skill, context, guide, session, cap,
board, clone, mind, exchange, file, project, vi-vision, decision, image, extraction, path, mesh, channel, agent,
operator`. Each scheme is documented inline with its resolver location and whether it's RESOLVED (has a live
dispatch branch in `runtime/cognition.py:resolve_address`) or register-but-defer (label only, widens the legal
set, no resolver yet — same pattern as `ui://`/`code://`).

Key resolved schemes and their canonical parse functions (all in `contracts/address.py`, "declared once, beside
`parse_session_address`" per the file's own convention at `:220-230`):
- `session://<sid>[/step/<tool_use_id>]` — `parse_session_address` (`:234-252`)
- `run://<turn>/<member>[/<index>]` — composition-step gate target, `parse_composition_step_address` (`:274-292`)
- `clone://<source-sid>/<cut>` — `parse_clone_address` (`:314-327`)
- `decision://<frame>/<id>` (frame = `global|project/<id>|user/<id>|session/<id>`, bare = global) —
  `parse_decision_address` + canonicalizer `decision_address` (`:337-375`) — the decision-surface's identity;
  state (pending/decided) is NOT an authored field, it's COMPOSED from the latest `decision_take` mark on the
  canonical address (`:151-153`).
- `project://<project-key>[/<scope-path>[/<resource-key>]]` — `parse_project_address` (`:387-403`), RESOLVED
  2026-07-02 against Postgres schema `container` (`:112-129`).
- `cap://<platform>[@version]/<kind>/<name>` (legacy bare `cap://<kind>/<name>` aliases to platform
  `claude-code`) — `parse_cap_address`/`cap_address` (`:417-459`).
- `image://<channel>/<path...>` — hierarchical, channel-rooted, `parse_image_address`/`image_address`
  (`:500-527`); a general `@v<n>` version-suffix axis applies across ALL addressed content (`split_version`,
  `:478-492`).

`ui://` and `code://` are explicitly *label* schemes the store itself does not resolve (`:20-36`) — `ui://` is
resolved by the UI-component registry (`contracts.ui_info`), `code://` by `Suite.resolve_scope` reading corpus
join data (`design/_system/{addresses.json, code-symbols.json}`).

### The `ui://` layer (`contracts/ui_info.py`)
Grammar: `ui://<kind>/<ref>[/<sub>][/@state]`, `ADDRESS_KINDS = ("chrome", "field", "canvas", "panel", "ext")`
(`contracts/ui_info.py:167`). Parsed by `parse_ui_address` (`:198-223`), fail-loud on a non-`ui://` string or one
with no segments (`:207-216`). `UnionAddressRecord` (`:266+`) is the per-component registry row; `build_ui_info`
(`:92-124`) asserts one source per address (no two entries claim the same `ui://`).

### How `surface/app` stamps + resolves addresses (`surface/app/src/lib/address.ts`)
- Every addressable DOM element carries `data-ui-ref="<full ui:// string>"`, applied via `stamp(addr)`
  (`address.ts:29-31`), paired with a Motion `layoutId` (not shown in this file, per its own comment at `:3`).
- `parseUiAddress` (`:10-22`) mirrors `contracts/ui_info.py:parse_ui_address` client-side.
- ONE sink for all navigation: `resolveUiTarget(addr, {transient?})` (`:64-82`) — validates, sets the module-level
  `_locus` pub/sub store (`:34-48`), adds a `.ui-indicated`/`.ui-spotlight` CSS class, scrolls into view. Malformed
  addresses fail loud into a `Notice` (`:67-69`), never silently swallowed.
- Click capture: `installAddressCapture()` (`:95-110`) is a single capture-phase `document.addEventListener('click',
  …, true)` that finds the nearest `[data-ui-ref]` ancestor and routes it through `resolveUiTarget`.
- The `ui:point` bridge: `installPointerBridge()` (`:126-133`) listens for `window.dispatchEvent(new
  CustomEvent('ui:point', {detail:{address}}))` — this is how the RHM/brain ("V") SPOTLIGHTS an element it is
  discussing, reusing the same `resolveUiTarget` sink but marked `transient: true` (releases the highlight fully,
  vs. a click's persistent `.ui-indicated`). The brain-side emit is external (fork's `forkVBrain`/`forkBrainCore`,
  not in this tree — see §5).
- The pointable-targets catalog (`surface/app/src/lib/pointables.ts`): `window.surfacePointables()` (`:43-68`)
  exposes a curated list of `{token, address, label}` for controls actually present in the DOM (`:25-36`), PLUS
  auto-discovered elements carrying both `data-ui-ref` + `data-point-label` (`:57-65`) — the mechanism any new
  surface uses to become spotlightable without a catalog edit. Tokens are opaque; the brain never receives a raw
  `ui://` address (operator-law, `pointables.ts:1-16`).
- `/api/territory/label?address=` resolves a `ui://` (or any) address to a human label for display (never the
  raw address/code, `RightHand.tsx:193-213,298-313`).
- Read-side address resolution for content (not chrome) rides `/api/territory` → `Territory` type
  (`api.ts:96-111`) → `readTerritoryContent`/`territoryRefCount`/`territoryNotes` in `SourcePanel.tsx:35-74`,
  which extract ONLY human-legible prose (never a raw dict/code/address — operator-law, `SourcePanel.tsx:29-34`).

---

## 3. The stream (SSE contract)

Single endpoint: `GET /api/stream` (`runtime/bridge.py:1485` dispatch, handler `_stream` at `:2203-2237`).

- **Transport**: tails the SHARED `events.jsonl` file (not an in-memory queue) so it captures events from BOTH
  the MCP face and the bridge face (`:2203-2206`). Polling loop, `time.sleep(0.4)` between checks (`:2233`).
- **Event shape**: `id: <seq>\ndata: <json event>\n\n` (`:2229-2230`), where the JSON event is whatever
  `SUITE.events_since(cursor)` yields — includes at minimum `seq`, `ts`, `channel` (used for filtering).
- **Cursor / reconnect**: `?since=<seq>` query param, or falls back to the `Last-Event-ID` header for a gapless
  browser auto-reconnect (`:2210-2211`); default `-1` = from the start (`:2215-2217`).
- **Filter**: `?channel=<name>` — server-side filter, only events stamped with that channel flow through
  (`:2217-2221`); an unstamped event is honestly excluded, never guessed into a channel.
- **Heartbeat**: `: keepalive\n\n` every ~15s so idle proxies don't drop the socket (`:2231-2233`).
- **Client consumption** (`surface/app/src/App.tsx:454-508`): two separate `EventSource`s —
  1. The live tail: `new EventSource('/api/stream?since=' + lastSeqRef.current)` (`:460`), debounced 2.5s
     (`:474-480`) into a `pulse` state bump that triggers a full projection re-fetch (App does NOT apply
     incremental patches — every new event just triggers a re-`fetchProjection`). Paused while scrubbing the
     past (`at` set) or `live=false` (`:455`).
  2. A one-shot `since=-1` stream (`:492-507`) purely to read the FIRST event's `ts` (the scrubber's earliest-
     event floor), closed immediately after the first message.
- Browser `EventSource` auto-reconnects gaplessly via `Last-Event-ID`; `es.onerror` is a no-op by design
  (`App.tsx:483`).

---

## 4. The views today

Per view: name · what it shows · which mechanisms it rides · presentation verdict.

| View / component | What it shows | Mechanisms ridden | Verdict |
|---|---|---|---|
| **The instrument** (`Desktop.tsx`/`Portrait.tsx`/`Landscape.tsx` + `wheel/*`) | THE UNIVERSAL PROJECTION — a polar/grid plot of the corpus, lens-switchable (kinds/semantic/separator/nucleation/…), time-scrubbable, live-streaming | `/api/projection`, `/api/stream`, the address spine (`data-ui-ref` on chrome), Motion (`feel`) | **keep-pattern** — this is the one genuinely bespoke, load-bearing visualization (the "universal projection" equation); not a generic CRUD list. Chrome (chips/legend/scrubber) around it is plain custom CSS/React — test-grade, replaceable. |
| **Disclosure** (`wheel/Disclosure.tsx`, referenced `Desktop.tsx:57`) | the selected point's inspector panel | `selected` point data off the projection | not read in full; referenced only — flag as unread if needed |
| **Gallery face** (`gallery/GalleryMount.tsx`) | the "drill-in" modal for a picked unit OR a decision card — hosts an **externally-authored DOM subtree** DNA renders via `window.DNA.renderGallery`/`bindProjectionDrill` (a classic `<script>` tag loaded pre-React, `GalleryMount.tsx:23-24`) | `/api/cognition/corpus?address=` (via DNA's own fetch, same-origin), `projection:select`/`gallery:rendered`/`decision:rendered`/`gallery:rerender`/`decision:open` events, `/api/decision/explain` (grounded resolve) | **mechanism to preserve; presentation is DNA's, not this repo's** — the React component is a thin, stable-DOM HOST (contract: never React-reconciles the inner div) around a system the claude-ds design system is presumably already the replacement engine for. The event contract (`gallery:rendered`, `decision:rendered`, `gallery:rerender`, `decision:open`, `decision:ready`) is the mechanism to keep. |
| **The V / RightHand-Man** (`rhm/RightHand.tsx`) | a draggable fan-menu overlay with 6 verbs (Go to / See the record / Ask / Note / Drive[soon] / Make[soon]), a brain chat panel, a channel-post composer, a note composer, first-contact greeting + 3-question guided tour | `stamp()`/address spine, `gallery:verb` dispatch (consumed in `App.tsx:270-404`), `/api/territory/label`, `/api/territory/write` (via `forkVBrain.direct`), `projection:select`/`projection:aim` events, an EXTERNAL `window.forkVBrain` object (not in this tree) | **mixed** — the VERB CONTRACT (`gallery:verb{verb,aim_address,payload}`), the aim-follows-selection wiring, and the honest "addressless activity event" degrade are load-bearing mechanism. The fan-menu / draggable-handle / greeting-bubble UI chrome is bespoke custom CSS, clearly labeled test-grade/AI-draft copy throughout (`RightHand.tsx:16-24` "TENTATIVE, for Tim/composition to ratify"). |
| **Source panel** (`source/SourcePanel.tsx`) | the fuller record + provenance + operator's own notes behind a point, resolved via `/api/territory` | `fetchTerritory`, `readTerritoryContent`/`territoryRefCount`/`territoryNotes` extraction (operator-law: prose only) | **keep the extraction logic** (the human-text-only unwrapping of a `Territory` record is a real, non-trivial mechanism); presentation is plain custom CSS, test-grade. |
| **Decisions bar + inbox** (`decisions/DecisionsBar.tsx`, `DecisionsInbox.tsx`) | "N decisions waiting" CTA + a work-queue list; tapping opens a card via the SAME `decision:open` → GalleryMount host | `/api/decisions`, `gallery:rerender` reload-on-write, `decision:open` dispatch, owner-filter (`owner==='tim'`) | **mechanism keep** — the owner-filter + one-open-path + reload-on-write pattern is real; the list/row rendering is plain custom CSS, test-grade, explicitly AI-draft copy. |
| **Channel view / Board view / Transcript view** (`channels/ChannelView.tsx`, `board/BoardView.tsx`, `transcript/TranscriptView.tsx`) | the fabric as a hub-spoke graph / the noticeboard as grouped sections / the whole transcript corpus as a searched constellation | `/api/channels`, `/api/board`, `/api/transcript-search`; each explicitly says (in its own header comment) it renders via **DNA's archetype engine** (`DNA.faceRecord.*` → `DNA.org.*` → `DNA.renderArchetype`) — "NO bespoke graph/list (from-DNA law)" | **mechanism keep (store + open/close/Esc + DNA archetype contract); presentation is ALREADY meant to be DNA's**, i.e. these three are the closest existing analogue to what claude-ds is meant to formalize. Host framing (full-width-centered for graphs vs. scrollable-list for board) is a real, cited constraint (`ChannelView.tsx:6-9`, `BoardView.tsx:6-9`) to preserve. |
| **Session drill** (`sessions/SessionDrill.tsx`) | list of Claude Code sessions → drill into one → DNA's session-card + 3 recall lenses | `/api/sessions`, `/api/session-recall`, DNA's `sessionRecord`/`renderArchetype` drop-in | same verdict as above — DNA-rendered card, host provides list/filter/drill chrome (test-grade). |
| **Tools bar + panel** (`tools/ToolsBar.tsx`, `ToolsPanel.tsx`, `schemaForm.tsx`) | pilot palette: pick a tool → human description → op-conditional form → Run (Run/result explicitly NOT wired yet) | `/api/tools`, `form_meta` consumption adapter (`toolsStore.ts:196-226`), enum-source resolution against live registries (e.g. `/api/layers`) | **mechanism keep (the schema→friendly-form translation + op-conditional field logic is substantial and reusable)**; the panel chrome + entry pill are explicitly scaffold-grade (`ToolsBar.tsx:6` "Placement is scaffold-grade"), AI-draft copy throughout. |
| **Surface nav** (`nav/SurfaceNav.tsx`) | a rail linking all the sibling-overlay surfaces (map/decisions/fabric/board/sessions/history) | dispatches the `*:open` window events each store listens for; degrades to plain fallback buttons if `DNA.org.navRail` isn't loaded (`SurfaceNav.tsx:41-55`) | **keep the routing table + degrade-clean pattern**; visual rendering is already deferred to DNA when present. |
| **Verify-mode banner** | a persistent "your takes are not being saved" banner | `isVerifyMode()` (URL `?verify` param) gating decision-take/update-accept persistence | **mechanism keep** — a real safety rail (`verifyMode.ts:1-32` documents two prior ghost-write incidents this fixed); trivial one-line render, no presentation debt either way. |
| **`canvas/` app** | a SECOND frontend (tldraw + React + Tauri), generic `ai-node` rendering off `/object_info` | not read in depth this pass — flagged in §0 | **unclear** — needs its own read before any replacement decision; bridge.py serves it at `/`, not `surface/app`. |

---

## 5. What any replacement UI MUST preserve (the mechanism contract)

- [ ] **The address spine**: every interactive element stamped `data-ui-ref="<ui://…>"`; ONE capture-phase click
      listener routes through ONE sink (`resolveUiTarget`); malformed addresses fail loud into a Notice, never
      silently swallowed. (`address.ts:29-82,95-110`)
- [ ] **The `ui:point` spotlight bridge**: a `CustomEvent('ui:point', {detail:{address}})` on `window` drives the
      SAME sink as a click, but `transient: true` (releases fully vs. persists) — this is how an external "brain"
      (RHM/V) points at UI without ever holding a parseable address itself. (`address.ts:126-133`, `pointables.ts`)
- [ ] **The pointables catalog**: `window.surfacePointables()` — curated + auto-discovered
      (`data-ui-ref`+`data-point-label`) targets, opaque tokens only reaching the brain. (`pointables.ts:43-68`)
- [ ] **The `gallery:verb` envelope**: `{verb, aim_address, payload}` — the ONE dispatch contract for
      navigate/open-source/drive/generate/annotate(decision-take)/accept-update, consumed centrally in `App.tsx`.
      (`App.tsx:270-404`)
- [ ] **The gallery-face host contract**: a stable, never-React-reconciled container DOM node; `gallery:rendered`/
      `decision:rendered`/`gallery:rerender`/`decision:ready`/`decision:open` events; the "from inbox → close
      returns to inbox" queue-working behavior. (`GalleryMount.tsx:41-232`)
- [ ] **The projection fetch/re-fetch cycle**: lens (`binding`) + space + embedder-layer + MRL-resolution +
      quantization + centre + poles + time(`at`) + rung, all composed into one `/api/projection` query; SSE
      `/api/stream` only PULSES a re-fetch, never patches incrementally. (`App.tsx:406-508`)
- [ ] **The operator-session token**: minted once via `/api/operator-session`, attached via a single
      `window.fetch` wrapper to same-origin `/api/*` calls; invisible to the operator; gates only consequential
      writes server-side. (`operatorSession.ts:34-98`)
- [ ] **Verify-mode**: `?verify` param suppresses decision-take/update-accept PERSISTENCE while still rendering
      the full drive, with a loud persistent banner + per-action Notice. (`verifyMode.ts`, `App.tsx:356-396`)
- [ ] **Operator-law text extraction**: server responses are read for HUMAN PROSE ONLY — `Territory`/decision
      records are unwrapped (`readTerritoryContent`, `territoryNotes`) to strip raw dicts/addresses/code before
      display; every address shown to the operator goes through `/api/territory/label`, never the raw string.
      (`SourcePanel.tsx:29-74`, `RightHand.tsx:193-213,298-313`)
- [ ] **The one-store, subscribe-pattern data layer**: every FACE-1 breadth surface (board/channels/sessions/
      transcript/decisions/tools) is a tiny module-level `{state, subs:Set<fn>}` store with `load*`/`open*`/
      `close*`/`use*` — fail-loud on cold-load error, soft-degrade on refresh error, monotonic `loadSeq` guards
      against stale responses clobbering fresher ones. Deliberately repeated 6×, not abstracted — flagged in the
      source itself as the "ONE subscribe-store pattern" convention. (`decisionsStore.ts`, `boardStore.ts`,
      `channelStore.ts`, `sessionDrillStore.ts`, `transcriptStore.ts`, `toolsStore.ts`)
- [ ] **DNA render-engine seam**: channel/board/transcript/session views explicitly hand rendering to an
      externally-loaded `window.DNA` (`faceRecord.*` adapters → `org.*` organisms → `renderArchetype`) — this is
      the EXISTING analogue of what claude-ds presumably formalizes; the host/adapter split (data store here,
      render there) is the pattern to continue, not discard.
- [ ] **External brain globals**: `window.forkVBrain`, `window.forkBrainCore`, `window.DNA` are all loaded from
      OUTSIDE `surface/app/src` (likely `public/gallery/*.js`, per the file list seen at
      `surface/app/public/gallery/{unit-view,fork-v-brain,surface,fork-gallery-brain-hooks,organisms,
      fork-brain-core,wildcard-gallery-binder,face-adapters,decision-render,archetype}.js` and
      `dna-tokens.css`) — NOT verified read in this pass; any replacement must locate and account for these
      scripts' contracts (`bindProjectionDrill`, `renderGallery`, `attach()`, `postToChannel`, `writeDirections`,
      `groundedAsk`) before assuming they can be dropped.
- [ ] **Fail-loud discipline, universally**: no silent empty states; every store distinguishes cold-load failure
      (blocking error + retry) from refresh failure (keep last-good data, subtle flag); every address parse
      raises on malformed input rather than guessing.

---

## 6. What is presentation-only (safe to discard)

- All hand-authored CSS files: `surface.css`, `board.css`, `channels.css`, `transcript.css`, `sessions.css`,
  `nav.css`, `source.css`, `paper.css` (the "Fresh Paper tokens" design system this repo currently uses) — every
  view's own header comment repeatedly flags its visual layer as "AI-draft," "scaffold-grade," or explicitly
  marked "for Tim's steer" (e.g. `RightHand.tsx:16-24`, `ToolsBar.tsx:6`, `DecisionsBar.tsx:6`,
  `DecisionsInbox.tsx:12-13`).
- The draggable-fan-menu mechanics of the V handle (drag/pointer-capture math, fan-layout trigonometry,
  `RightHand.tsx:345-550`) — the VERB SET + aim-following + gallery:verb dispatch is mechanism; the physical fan
  widget is presentation.
- The 3-layout device-classification chrome (`Desktop.tsx`/`Portrait.tsx`/`Landscape.tsx` + `layouts/shared.tsx`
  `WheelOrState`) beyond the actual `SurfaceState` composition and lens/view-mode branching, which is mechanism
  (which component renders per `binding.radius_from` / `view` is a real routing decision, `shared.tsx:27-70`).
- All literal button/pill/bar markup and copy strings throughout (`DecisionsBar`, `ToolsBar`, `SurfaceNav`
  fallback buttons, `RightHand` greeting bubble text, `SourcePanel` labels) — explicitly called out as AI-supplied
  draft copy pending Tim's ratification in numerous places.
- The Mockup Studio (`/studio`, `/mockups/*.html`, `design-system.css`) is a separate, already-static design-
  review tool — not part of the live operator surface's mechanism at all.

---

## Gaps / not fully verified in this pass

- `canvas/` (the tldraw+Tauri app bridge.py actually serves at `/`) was NOT read beyond its constitution file —
  needs its own pass before any final replacement decision, since it may be the ACTUAL daily-driver, not
  `surface/app`.
- `wheel/Disclosure.tsx`, `wheel/Wheel.tsx`, `wheel/Separator.tsx`, `wheel/Nucleation.tsx`, `wheel/Grid.tsx`,
  `wheel/Tether.tsx`, all `toggles/*.tsx` chips, `tools/schemaForm.tsx`, `Portrait.tsx`/`Landscape.tsx` were
  referenced (imports, call sites) but not opened line-by-line — the verdicts above for the instrument's own
  chrome are inferred from the layout files' usage, not from reading those files directly.
- The `public/gallery/*.js` scripts (DNA/fork's actual render + brain code `surface/app` loads at runtime) were
  NOT read — every "DNA renders this" / "forkVBrain does X" claim above is grounded in the `surface/app/src`
  callers' comments and event contracts, not in the implementations themselves.
- The full POST route list (`runtime/bridge.py:2617-3861`) was enumerated by grep, not read function-by-function;
  only the routes `surface/app` actually calls were traced into their handler bodies.
