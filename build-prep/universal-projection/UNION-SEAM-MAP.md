# UNION-SEAM MAP — the cross-stream event seams (are they welded?)

Tim's direction (2026-06-18): "a big purpose of all of this is union… it sounds like you've come across some
inconsistencies." The inconsistencies the build kept surfacing are all the SAME shape: **seams where two
parts — built by different streams (DNA · fork · wildcard · composition · recollection · projection), at
different times — were supposed to MEET, and the join was *assumed* rather than welded.** And every one was
*silent* (a dropped take, a swallowed import, a stale label) — which is what lets the union drift apart
without anyone noticing. Silence is the enemy of both union and continuity.

This is the deliberate audit (instead of stumbling on seams one fire at a time): walk every cross-stream
EVENT, list its emitters vs listeners, and mark whether the seam is WELDED (both sides meet + fails loud on
mismatch) or UNWELDED (a side missing / a silent drop). Re-run this map whenever an event is added or moved.

## The cross-stream events (surface src/ + synced public/gallery/ hooks)

| event | emitters | listeners | status |
|---|---|---|---|
| `gallery:rendered` | DNA `unit-view.js` | GalleryMount · wildcard-binder · fork-hooks | ✅ welded (1 emit, 3 listen) |
| `gallery:verb` | wildcard-binder · RightHand | App `onVerb` | ✅ welded — incl. the TAKE (`is_decision_take`), wired 41e3738 |
| `gallery:direction` | wildcard-binder | fork-hooks HOOK 2 | ✅ welded (annotation route-back → territory_write) |
| `gallery:rerender` | fork-brain-core (post-write) | **GalleryMount** | ✅ welded THIS PASS (6e4e2c5) — was UNWELDED (no listener → writes never refreshed) |
| `projection:select` | App | GalleryMount · RightHand | ✅ welded |
| `projection:aim` | Wheel | RightHand | ✅ welded |
| `decision:rendered` | DNA's decision-card | GalleryMount · fork HOOK 1b | ✅ welded + VERIFIED — DNA emits on the real card; host opens+holds; fork HOOK 1b binds the in-card Ask. Driven end-to-end both viewports (the flagship prove-on-one) |
| `gallery:write-error` | fork-brain-core (write fail) | DNA's decision-card (on-card banner) | ✅ welded + VERIFIED THIS FIRE — the card listens (`unit-view.js:492`), matches `element_id`===`data-decision-address`, shows the "Couldn't save — try again" banner + disables the options. DROVE it on the real card (390+1440): banner shown, `.write-error` set, options opacity .6 / pointer-events none |
| `projection:rendered` | — | — | ⚪ dead (unused name; harmless) |

## The four flagged seams → ALL WELDED + CLOSED (the union work, done)

Every seam this audit surfaced as "assumed not welded" is now welded by its owner AND driven at its meeting
point (not trusted as "code looks right"). The union of the decision surface is whole.

1. **`gallery:rerender` had no listener** → ✅ WELDED (6e4e2c5; host re-renders the mounted face; replaceable by
   DNA's finer in-place refresh later). Was: every write (annotation, take) succeeded but never visually
   refreshed. Verified: a take flips the card to decided via this refresh.
2. **`decision:rendered` → fork's in-card Ask** → ✅ WELDED — fork added HOOK 1b (`fork-gallery-brain-hooks.js`,
   listens for `decision:rendered`, binds the same in-card Ask keyed to the decision's canonical address).
   Verified: the Ask mounts on the real card (the flagship prove-on-one, both viewports).
3. **`gallery:write-error` on a card** → ✅ WELDED + VERIFIED THIS FIRE — the seam projection structurally
   COULD NOT cover (the card overlay z-60 hides the surface chrome's Notice + the V, so only the card can show
   a save failure). The fork built it INTO the card render: a `.dc-error-banner` + a global `gallery:write-error`
   listener that matches `element_id`===the card's `data-decision-address` and reveals the banner. DROVE it on
   the real merge-sa-authorize card, BOTH viewports: fire `gallery:write-error{element_id: bare canonical}` →
   "Couldn't save — try again" banner shows (red, DNA-token styled), `.write-error` class set, options disabled
   (opacity .6 / pointer-events:none). A failed take is now LOUD, not silent. no-silent-failure satisfied.
4. **canonicalization at the take write-point** → ✅ WELDED — wildcard's `decide()` REFUSES a non-canonical
   address (fail-LOUD guard, TEST9), so a bad/`#elem` stamp SCREAMS at the emit point. Verified the match
   chain end-to-end: the card's `data-decision-address` === the bare canonical (so both the take write AND the
   write-error match key agree). ⚠ HARDENING NOTE (verified-safe, not a bug): `/api/territory` does NOT return
   `identity.address` (it's `None`), so the card's match key comes from the render-time `d.address` fallback,
   NOT from registry-truth. It's CLEAN today (driven: `matchesBareCanonical: true`), but a future render-path
   change that drops the fallback would silently break the write-error match. The robust weld = the resolver
   returns `identity.address` (registry-is-truth) so the card never depends on a render-time fallback. Routed
   to fork as a small hardening (not blocking — verified working).

## Seam class 2 — the surface↔bridge API routes (audited 2026-06-18; ALL WELDED)

Every `/api/*` the surface (src/) + the synced hooks call, verified live against the bridge — a 404 would
be a silent seam (the feature breaks). All respond via their correct method:

| route | method | status |
|---|---|---|
| `/api/projection` · `/api/cognition/corpus` · `/api/cognition/neighbours` · `/api/context` · `/api/layers` · `/api/layer-dims` · `/api/territory` · `/api/territory/label` | GET | ✅ 200 |
| `/api/territory/write` · `/api/claude/turn` | POST | ✅ 200 (drove the take + explain this session) |
| `/api/stream` | GET/SSE (EventSource, App.tsx:368/402) | ✅ 200 (opens the live spine) |

Two false-positive 404s ruled out (recorded so a future audit doesn't re-flag them): **`/api/layer`** — not a
real route; a regex truncation of `/api/layer-dims` (the real call, welded). **POST `/api/stream`** — 404 only
because it's a GET-only SSE route; GET → 200. No silent API seam.

## The pattern (for continuity)

The welds that held were the ones built to **fail loud** (the sync shouted when the reorg split files) and the
gaps that were caught were caught by **verify-by-use** (driving the actual meeting point, not trusting "the
code looks right"). The union stays whole over time only if every new seam (a) fails loud on mismatch and (b)
is driven at its meeting point. A silent seam is a future drift. Continuity = no silent seams.
