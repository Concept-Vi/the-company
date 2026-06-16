# FINDS — DNA (ch-ovxwz8k8)

*Per-member append-only finds file (no concurrent-edit races on the shared DISCOVERY_LOG). DNA owns this file; the lead reads across all finds/*.md to synthesize convergences into DISCOVERY_LOG + EMERGING_SHAPE. Finds not conclusions; honest verification-state; nothing final ([[feedback-confident-not-correct]] generative form). Format per find: what · where(path) · verbatim-if-quotable · verification-state · what-shape-it-points-at.*

---

## ROOMS — a built spatial-navigation shell (= F7's "running shell in counterpart/design")
- **WHERE:** `counterpart/design` — `ui/rooms/shell.js` (DNA.rooms) + `rooms.css` (#roombar).
- **WHAT:** four rooms — Gallery · Bench · Map · Almanac (+ Atlas overlay) — as OVERLAYS over ONE canvas (gallery = room 1, never moves; others slide over it). Slide DIRECTION derives from where-you-came-from; spatial_persistence; rooms are registry citizens `{id, order, icon, mount/enter/leave}`; deep-linkable `#room=<id>`.
- **VERIFICATION-STATE:** verified-by-use (running; desktop + mobile).
- **VERBATIM (shell.js):** "Rooms are PLACES (spatial_persistence): overlays slide over the gallery on one canvas; the slide DIRECTION comes from where you came from (arrival_relative_to_path: a transition is a property of the EDGE). The gallery is room 1 and never moves."
- **WHAT SHAPE IT POINTS AT (loosely):** "one addressed canvas; move between places by camera-direction; transition = a property of the EDGE; each place is a projection." = the SAME spatial-navigation shape as projection's "open onto a SPACE not a screen" (F5) + the graph-of-minds drill-in/out (F11) + address-navigation — reached from the ROOMS end. Convergence on the spatial-navigation shape, now 4+ sources. ★ Note "transition = a property of the EDGE" ≈ the connection-tuple (CAND-13) — the edge carries the transition.

## THE ENGINE UNDER THE ROOMS (the "18 registries")
- **WHERE:** `dna/` (roles · types/edges · dials · grammar · tokens · layouts · application · invariants) + `ui/surface.js` (the resolver + splitPane/pinchZoom/control/story).
- **VERIFICATION-STATE:** built (running shell); per-registry verification TBD.
- **SHAPE:** the resolver + registries under the rooms = composition's resolver+registry shape, reached from DNA's end. The rooms are projections; surface.js is the resolver; dna/ is the typed substrate.

## (earlier finds — see DISCOVERY_LOG F10/F12: presentation-as-data layouts.json · 73 reference screens · organisms.js · the identity/voice resolution layer + DNA's 4 axes · the gallery viewer · the parked polarity/inversion theory · surface-vs-projection types · content↔identity split)
