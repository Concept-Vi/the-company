# FRONTEND REPLACEMENT — the claude-ds inventory (the join of the two reader reports + the map)

_2026-07-13 · ds-map. Sources: COMPANY-FRONTEND-MECHANISMS.md (313 lines, file:line-cited) ·
COMPANY-KNOWLEDGE-LAYER.md (120 lines) · registry/{address,symbol}-registry.json + GAPS.md.
Directive (Tim): claude-ds REPLACES the company frontend's presentation; the mechanisms stay._

## 1 · What "the frontend" actually is — THREE surfaces, not one
| Surface | What | Served | Replacement posture |
|---|---|---|---|
| `canvas/` (tldraw+React+Tauri) | one generic ai-node shape over /object_info | bridge ROOT (`/` → canvas/index.html, bridge.py:1487) | needs its own read; tldraw-bound controller — lead's K1 already rules: re-express, never lift |
| `surface/app/` (Vite/React PWA) | the instrument (universal projection) + 10 sibling overlays | its own vite build proxying /api → :8770 | THE main replacement target; richest mechanism set |
| `design/mockups/` Studio | static design-review gallery | bridge `/studio` + /design-system.css | already a review surface; folds into the DS specimen/review flow naturally |
**OPEN QUESTION FOR TIM/LEAD: which is in daily use?** The bridge's own root serves canvas/, but surface/app is the richer, newer client. (mechanisms §0)

## 2 · The already-connected seam nobody had on the board: DNA renders surface/app TODAY
ChannelView / BoardView / TranscriptView / SessionDrill state in their own headers: rendering via
**counterpart DNA's archetype engine** (`DNA.faceRecord.* → DNA.org.* → DNA.renderArchetype`, "NO bespoke
graph/list — from-DNA law"); GalleryMount hosts `window.DNA.renderGallery` in a React-stable DOM island.
**Consequence: the replacement is largely a DNA→claude-ds question, not a build-from-nothing** — and the
two-design-systems doctrine (board://item-62514a68) is not theoretical: the company frontend is the live
consumer of system #3. Whatever direction the doctrine takes, these four views follow it.

## 3 · The mechanism contract (MUST preserve — condensed checklist; full versions in the two reports)
- Address spine: every element `data-ui-ref="ui://…"`; ONE capture-phase click listener → ONE sink
  (resolveUiTarget); malformed = loud Notice. The `ui:point` CustomEvent drives the same sink transiently
  (how the brain spotlights UI); `window.surfacePointables()` catalog, opaque tokens to the brain.
- The `gallery:verb {verb, aim_address, payload}` envelope — the one verb dispatch, consumed centrally.
- SSE contract: /api/stream tails events.jsonl; `?since=`/Last-Event-ID gapless reconnect; `?channel=` filter;
  keepalive; client re-fetches projection on pulse (no incremental patching).
- Operator-law: prose only reaches the operator (territory extraction, /api/territory/label — never raw
  addresses/dicts); verify-mode banner (?verify) gating takes (two prior ghost-write incidents).
- page-face isolation: any address's bound page serves on a SEPARATE origin :8774, no-script CSP,
  content-addressed only — hard security constraint, keep.
- Knowledge layer: door/cards + guides + message verbs are AGENT-facing (SessionStart-injected); the
  OPERATOR-facing help layer is /api/address-help (what-is · how-to-change · how-to-use) + guided-tour +
  walkthrough — mechanism built, **howto content ~unauthored** (suite.py's own "G-53" comment).
- The API surface: ~18 GET routes consumed by surface/app today; 60+ POST routes; full table in mechanisms §1.

## 4 · What claude-ds HAS for this vs what it LACKS (map-grounded)
HAS: the token spine (736 names, 0 hard/family ghosts as of 333ab2d) · 4 skins · 16 axes · block/level/material
grammar · 169 drawn icons + glyphic language · RenderType/Slide render door · CV_AI provider seam (company-http
exists per the lead's K0) · specimen/review flow · the map itself (rerun-able truth).
LACKS (already itemised): U6 operator components (Toast/Sheet/List/Menu/Nav-AppShell…) · 32 ghost icons
(the app's registries already ask for them) · CV_STUDIO/state half + 3 deaf triggers · the two-door reconcile
(U13) · **and now, from this inventory: DS-native equivalents of the archetype renderers DNA provides today**
(faceRecord/org/renderArchetype for channel-graph, board-list, session-card, transcript-constellation) — the
concrete bridge between the doctrine decision and the build.

## 5 · Proposed sequencing (not canon; for the board)
1. Tim/lead answer: which surface is the daily driver (§1) + the token-arrow (item-62514a68).
2. The DS grows the archetype-renderer equivalents (§4) AS REGISTERED TYPES with specimens — the four
   DNA-rendered views then re-point one at a time (mechanism hosts unchanged — they're already thin).
3. The unauthored howto content (§3) gets authored as part of each view's replacement (the help mechanism
   is free; the words are the work).
4. canvas/ gets its own reader pass before anything touches it.
