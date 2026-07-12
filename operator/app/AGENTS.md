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
`surface/app`, the proven quarry), served BY the bridge at `http://127.0.0.1:8770/app` (B1). This is
beat B1+B2 of the operator-app program (`board://item-67e34f0c`): the chrome (DS AppShell — nav rail on
desktop, tab bar on phone), the theme/density dials, and ONE thin first view (Arrival). The other nav
items (Inbox · Chat · Channels) honestly render the DS `.state-block` "not built yet" — they land
specimen-first in K3 order.

## The K0 contract this app obeys (non-negotiable)

- **ONE stylesheet chain.** `index.html` links exactly `/ds/styles.css` — the claude-ds 26-file cascade,
  served from the ONE DS home (`design/claude-ds`). ZERO raw hex/px/rgb anywhere in `src/`
  (`tests/operator_app_shell_acceptance.py` gates all three: literals, the bridge mount, the one-link law).
- **DS components through the sanctioned door.** `src/ds.ts` boots the DS: sets `window.React/ReactDOM`
  (our pinned 18.3.1 — one React instance), loads `/ds/_ds_bundle.js` (the U3 external-consumer
  mechanism), then imports `/ds/index.js` (the U4 door: `getDS()` / `getRegistry()`, loud-fail).
  Components come from `ds()` — never deep imports… with one documented tension (below).
- **SAME-ORIGIN law.** All data access is relative `/api/*` (the bridge's thick contract). No hardcoded
  hosts anywhere. Persistence for anything durable is the COMPANY via `/api` — never localStorage-only.
- **The address spine.** `src/lib/address.ts` (harvested verbatim from `surface/app`) — `data-ui-ref`
  stamps, ONE navigation sink (`resolveUiTarget`), the `ui:point` pointer bridge, fail-loud on malformed
  `ui://` addresses. `src/lib/api.ts` carries the harvested fail-loud `getJSON` core (`ApiError`).

## Known contract tensions (honest, dated 2026-07-13)

1. **Bundle-stale chrome (the ONE deep import).** `AppShell` and `List` (U6 components, landed
   2026-07-13) are NOT yet compiled into `_ds_bundle.js` (its `@ds-bundle` header lists 20 components;
   grep confirms zero AppShell/List bodies). Until the DS's compiler regenerates the bundle, `App.tsx`
   and `views/Arrival.tsx` import those two AS SOURCE from the one DS home (vite `fs.allow` reaches it;
   the react plugin compiles the JSX). Their CSS already rides the one `/ds/styles.css` chain
   (`tokens/controls.css`). **When the bundle is recompiled: switch these two imports to `ds()` and
   delete this note.**
2. **Bundle-internal load-order warts.** Loading `_ds_bundle.js` standalone logs ~11 console errors
   ("CV_AI must load first", "CV_REGISTRY must load first") from early bundle files; the registries DO
   all mount by end of load (verified in-browser: CV_REGISTRY/CV_AI/CV_ICONS/CV_AXES all present,
   `__errors.length === 5`). U9-class DS issue (console.error-and-continue), not this app's — but if a
   future view finds a Type missing from `CV_REGISTRY`, look there first.
3. **Vite dev vs build base asymmetry.** Vite DEV prepends `base` (`/app/`) to root-absolute URLs in
   `index.html` (the stylesheet becomes `/app/ds/styles.css`); `vite build` leaves them unchanged.
   `vite.config.ts` carries a dev-only `/app/ds` → `/ds` proxy rewrite compensating. Verified by use —
   don't "simplify" it away.

## How to build / run / verify

- **Dev:** `cd operator/app && npm install && npm run dev` → `http://127.0.0.1:5175/app/`.
  Needs the bridge up on :8770 (it serves `/api` AND `/ds/*`): `systemctl --user status company-bridge`.
- **Build for the bridge:** `npm run build` → `dist/` (gitignored, like the sibling apps). The bridge
  serves it at `http://127.0.0.1:8770/app`; if `dist/` is missing the bridge answers a teaching 503.
- **Verify:** `./.venv/bin/python tests/operator_app_shell_acceptance.py` (static teeth) +
  `./.venv/bin/python tests/bridge_routes_acceptance.py` (the mount is declared==dispatched) + open the
  app and LOOK (screenshots under `_shots/`, light + dark + phone width).

## Where new things go

- **A new view** → `src/views/<Name>.tsx`, registered in `App.tsx`'s `NAV`; K3 order, specimen-first
  (Tim reacts to the specimen BEFORE wiring). DS components only; data via `src/lib/api.ts` typed fetchers.
- **A new endpoint fetcher** → `src/lib/api.ts` (typed, riding the harvested fail-loud core).
- **Never**: a second stylesheet, an inline hex/px, a component hand-rolled where a DS one exists, a
  fetch bypassing `/api` relative paths.

## Security posture

Local-only (the bridge binds 127.0.0.1). Do NOT expose `/app` on the tailnet — B4 leg (a) transport
auth is not green (the comment at the bridge mount says the same).
