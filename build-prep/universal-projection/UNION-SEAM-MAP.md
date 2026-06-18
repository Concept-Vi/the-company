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
| `decision:rendered` | DNA's decision-card (post-reorg) | GalleryMount · *(should: fork HOOK 1)* | ⏳ staged — GalleryMount listens; DNA emits when her card lands |
| `gallery:write-error` | fork-brain-core (write fail) | RightHand (V's Note) | 🟡 partial — a TAKE/card-write failure has no on-CARD display (the V's Note is the wrong surface + the card overlay covers the surface chrome) → DNA's card lane |
| `projection:rendered` | — | — | ⚪ dead (unused name; harmless) |

## Unwelded / partial seams → routed to their owners (the union work)

1. **`gallery:rerender` had no listener** → WELDED this pass (host re-renders the mounted face; replaceable by
   DNA's finer in-place refresh later). Was: every write (annotation, take) succeeded but never visually
   refreshed.
2. **`decision:rendered` → fork's in-card Ask (HOOK 1)** — HOOK 1 listens only for `gallery:rendered`, so a
   decision card gets no interactive "Ask about this" (only its pre-filled explanation slot), and the V is
   covered by the overlay. Routed to fork (extend HOOK 1 to decision:rendered) — thread g-1781731457.
3. **`gallery:write-error` on a card** — a take/annotation write failure must surface ON the card (the surface
   chrome Notice + the V are both covered by the card overlay z-60). DNA's card lane (the card shows its own
   write-fail state). Flag to DNA.
4. **canonicalization at the take write-point** — `territory_write` marks at the LITERAL element_id; the
   binder claims server-side canonicalization. Happy path safe (DNA stamps canonical); latent silent-miss for
   a non-canonical address. Routed to fork (territory.py) — thread g-1781731457.

## The pattern (for continuity)

The welds that held were the ones built to **fail loud** (the sync shouted when the reorg split files) and the
gaps that were caught were caught by **verify-by-use** (driving the actual meeting point, not trusting "the
code looks right"). The union stays whole over time only if every new seam (a) fails loud on mismatch and (b)
is driven at its meeting point. A silent seam is a future drift. Continuity = no silent seams.
