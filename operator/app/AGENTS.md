---
type: constitution
register: prescriptive
module: operator/app
aliases: ["operator app — constitution"]
tags: [company, operator, app, frontend, claude-ds, constitution]
governs: []
depends-on: ["[[runtime — constitution]]"]
relates-to: ["[[operator — constitution]]", "[[tests — constitution]]"]
status: building
---

# operator/app — the operator console (K1 home)

**What this is.** The operator app shell — vite + React 18.3.1 + TypeScript (the exact tooling of
`surface/app`, the proven quarry), served BY the bridge at `http://127.0.0.1:8770/app` (B1). B1+B2 landed
the chrome (DS AppShell — nav rail on desktop, tab bar on phone), the theme/density dials, and the first
thin view (Arrival). I1 (`board://item-67e34f0c`) landed the second: **Inbox** — the registry-driven
NEEDS-ME INBOX, folding `inbox_sources/*` (decisions · surfaced · obligations · board_requests) through
`GET /api/needs-me` (`runtime/needs_me.py`) into one card stack Tim acts on directly. I2 (2026-07-13)
landed the **live tail**: Inbox now tails `GET /api/stream` (the SAME EventSource + Last-Event-ID pattern
Arrival's pulse uses) and debounce-refetches needs-me (~2s) whenever a real event lands on the bus —
never a `setInterval`. Chat · Channels still honestly render the DS `.state-block` "not built yet" —
they land specimen-first in K3 order.

## The K0 contract this app obeys (non-negotiable)

- **ONE stylesheet chain.** `index.html` links exactly `/ds/styles.css` — the claude-ds 26-file cascade,
  served from the ONE DS home (`design/claude-ds`). ZERO raw hex/px/rgb anywhere in `src/`
  (`tests/operator_app_shell_acceptance.py` gates all three: literals, the bridge mount, the one-link law).
- **DS components through the sanctioned door.** `src/ds.ts` boots the DS: sets `window.React/ReactDOM`
  (our pinned 18.3.1 — one React instance), loads `/ds/_ds_bundle.js` (the U3 external-consumer
  mechanism), then imports `/ds/index.js` (the U4 door: `getDS()` / `getRegistry()`, loud-fail).
  Components come from `ds()` — NEVER a deep/source import of `design/claude-ds/components/*.jsx`.
  This was a documented tension (the bundle was compiled before `AppShell`/`List`/`ListRow`/`ToastHost`
  existed) — **closed 2026-07-13**: the DS bundle was recompiled (verified: `_ds_bundle.js`'s
  `@ds-bundle` header lists all four, plus `Checkbox`/`Radio`/`Menu`/`Table`/`Search`/`Skeleton`/`Sheet`),
  `App.tsx`/`views/Arrival.tsx`/`views/Inbox.tsx` were switched to pull them from `ds()`, and the
  vite `fs.allow` reach into `design/claude-ds` (only needed for the old source imports) was removed.
  `src/ds.ts`'s `DSNamespace` type carries the four as typed keys now.
- **SAME-ORIGIN law.** All data access is relative `/api/*` (the bridge's thick contract). No hardcoded
  hosts anywhere. Persistence for anything durable is the COMPANY via `/api` — never localStorage-only.
- **The address spine.** `src/lib/address.ts` (harvested verbatim from `surface/app`) — `data-ui-ref`
  stamps, ONE navigation sink (`resolveUiTarget`), the `ui:point` pointer bridge, fail-loud on malformed
  `ui://` addresses. `src/lib/api.ts` carries the harvested fail-loud `getJSON` core (`ApiError`).
  **The `ui://operator/…` address scheme (I2, 2026-07-13)** — every meaningful element carries a
  `data-ui-ref` via `stamp()`, one flat vocabulary under `ui://operator/`:
  - `ui://operator/nav/<view>` — the nav rail item / tab-bar button for each `NAV` entry (`arrival`,
    `inbox`, `chat`, `channels`). Stamped in `App.tsx` by querying the real DOM the compiled `AppShell`
    produces (`.cv-appshell__rail .cv-rail-item`, `.cv-appshell__tabbar .cv-tab`) once at mount and
    matching by array order — `AppShell` (the bundle component) has no per-item address prop to pass
    through, so this is a documented post-render stamp, not a prop. Safe because `NAV` is static and
    every button is React-keyed by `it.id` (never recreated).
  - `ui://operator/inbox/card/<id>` — each Inbox card (`views/Inbox.tsx`), `<id>` == the card's own
    `card.id` from `GET /api/needs-me` (unique per source's `INBOX_SOURCE.fetch()`).
  - `ui://operator/arrival/<section>` — each greeting-digest `Card` in `views/Arrival.tsx`: `pulse`,
    `built`, `waiting`, `now`, `memories`.
  - `ui://operator/dials/<axis>` — the theme/density `Segmented` controls in `App.tsx`'s header:
    `theme`, `density` (one address per control, not per option — `Segmented` only spreads `...rest`
    onto its OUTER wrapper, so a stamp addresses the whole dial, matching "the dials" as the unit).
  New addressable things extend this same flat vocabulary (`ui://operator/<area>/<id>`) — never a
  parallel addressing scheme.
- **The operator-session token (#1b), the header convention (I1).** `src/main.tsx` calls
  `mintOperatorSession()` (`src/lib/api.ts`) alongside `bootDS()` on app boot — ONE `GET
  /api/operator-session` mint per process, held module-level (never re-minted per request). **Every POST
  this app makes carries `X-Operator-Session: <token>`** (`postJSON`/`actOnCard` in `src/lib/api.ts`) —
  server-side enforcement is flag-gated off today (`enforced` in the mint response), so the header is
  currently ignored, but it is sent unconditionally so nothing needs revisiting when enforcement flips on.
  A failed mint warns loudly to the console and leaves POSTs token-less; it never blocks first paint or
  bricks the app (enforcement being off makes that safe).

## Known contract tensions (honest, dated 2026-07-13)

1. **`inbox_sources/obligations.py` and `inbox_sources/board_requests.py`'s "Comment" verb does NOT
   resolve the underlying obligation/request** (I1, honest limitation, dated 2026-07-13). The only WRITE
   door the operator surface exposes onto a board item is `/api/board/comment` (files a real,
   thread-visible `commented_on` comment as `operator://tim`); genuinely clearing a pending obligation
   needs a `reply_to`-edged reply (`cc_board.reply_to_mention`), which is agent/session-only — not a
   bridge door. So the card's button is labelled **"Comment"**, never "Resolve"/"Reply", and the card
   will keep resurfacing after it's clicked (correctly — the obligation is still open). See
   `inbox_sources/obligations.py`'s docstring.
2. **Bundle-internal load-order warts.** Loading `_ds_bundle.js` standalone logs ~11 console errors
   ("CV_AI must load first", "CV_REGISTRY must load first") from early bundle files; the registries DO
   all mount by end of load (verified in-browser: CV_REGISTRY/CV_AI/CV_ICONS/CV_AXES all present,
   `__errors.length === 5`). U9-class DS issue (console.error-and-continue), not this app's — but if a
   future view finds a Type missing from `CV_REGISTRY`, look there first.
3. **Vite dev vs build base asymmetry.** Vite DEV prepends `base` (`/app/`) to root-absolute URLs in
   `index.html` (the stylesheet becomes `/app/ds/styles.css`); `vite build` leaves them unchanged.
   `vite.config.ts` carries a dev-only `/app/ds` → `/ds` proxy rewrite compensating. Verified by use —
   don't "simplify" it away.
4. **AppShell has no per-nav-item address prop.** The compiled `AppShell` renders the rail/tab-bar
   buttons itself from the `nav` array — there is nowhere to pass a `data-ui-ref` per item. `App.tsx`
   stamps them onto the real DOM post-render instead (see the address-scheme note above). If a future
   DS bundle recompile adds an `addr`/`ref` field to nav items, prefer that and delete the DOM-query
   stamp — it is a documented workaround, not the target shape.
5. **The needs-me event-kind vocabulary doesn't match the bus 1:1.** `board.item.filed` and
   `board.item.transitioned` are real `kind` values (verified against
   `tests/board_bus_events_acceptance.py`), but a decided decision does NOT land as `kind:
   "decision.decided"` — it lands as `kind: "op.run"` with `op: "decision.decided"`
   (`runtime/suite.py:emit_run_record`, read at `runtime/bridge.py:1673`). Inbox's live tail
   (`views/Inbox.tsx`) therefore debounce-refetches on **any** stream event rather than filtering by
   kind — honest given the mismatch, and still not polling (nothing fires without a real event).

**Resolved (kept for the paper trail):** *Bundle-stale chrome* — `AppShell`/`List`/`ListRow`/`ToastHost`
(U6, landed 2026-07-13) were compiled into `_ds_bundle.js` on 2026-07-13; `App.tsx`, `views/Arrival.tsx`,
and `views/Inbox.tsx` now pull them from `ds()` (see the K0-contract bullet above) — no more deep
imports of `design/claude-ds/components/*.jsx` anywhere in `src/`.

## How to build / run / verify

- **Dev:** `cd operator/app && npm install && npm run dev` → `http://127.0.0.1:5175/app/`.
  Needs the bridge up on :8770 (it serves `/api` AND `/ds/*`): `systemctl --user status company-bridge`.
- **Build for the bridge:** `npm run build` → `dist/` (gitignored, like the sibling apps). The bridge
  serves it at `http://127.0.0.1:8770/app`; if `dist/` is missing the bridge answers a teaching 503.
- **Verify:** `./.venv/bin/python tests/operator_app_shell_acceptance.py` (static teeth) +
  `./.venv/bin/python tests/bridge_routes_acceptance.py` (the mount is declared==dispatched) +
  `./.venv/bin/python tests/needs_me_acceptance.py` (I1: `inbox_sources/` discovery + the fail-soft fold +
  the card-shape contract) + open the app and LOOK (screenshots under `_shots/`, light + dark + phone
  width). For the Inbox live tail (I2): open chrome-devtools' Network panel on `/app`, confirm ONE
  pending `/api/stream` (EventSource, `Content-Type: text/event-stream`, never resolving) and ZERO
  repeated `/api/needs-me` requests on a timer — a refetch should only appear after a real bus event
  (e.g. `mcp__company__board_act` filing/transitioning an item) lands and the ~2s debounce fires.

## Where new things go

- **A new view** → `src/views/<Name>.tsx`, registered in `App.tsx`'s `NAV`; K3 order, specimen-first
  (Tim reacts to the specimen BEFORE wiring). DS components only; data via `src/lib/api.ts` typed fetchers.
- **A new endpoint fetcher** → `src/lib/api.ts` (typed, riding the harvested fail-loud core).
- **A new "needs me" feed** (I1) → drop `inbox_sources/<id>.py` at the repo root declaring
  `INBOX_SOURCE = {id, label, fetch, card_shape, verbs}` + its own zero-arg `fetch()` adapter (mirrors
  `item_types/<id>.py` — file-discovered, id == filename, fail-loud). ZERO change to `runtime/needs_me.py`
  or `Inbox.tsx` — the fold is generic over the registry. See `runtime/inbox_source_registry.py`'s
  docstring for the schema, and `inbox_sources/decisions.py` for a worked example (including the trap:
  never name the loader module `inbox_sources.py` — it would shadow the data directory of the same name).
- **Never**: a second stylesheet, an inline hex/px, a component hand-rolled where a DS one exists, a
  fetch bypassing `/api` relative paths, a POST that skips `X-Operator-Session`.

## Security posture

Local-only (the bridge binds 127.0.0.1). Do NOT expose `/app` on the tailnet — B4 leg (a) transport
auth is not green (the comment at the bridge mount says the same).
