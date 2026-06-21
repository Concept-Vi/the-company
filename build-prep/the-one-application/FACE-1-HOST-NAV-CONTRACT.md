# FACE-1 HOST-NAV CONTRACT — how a FACE-1 surface plugs into the host
*projection-owned (the host/panels lane). The pattern a FACE-1 surface (channel-view · session-drill + embedded-CLI · transcript-viz · timeline/lanes · board-view · address-view) follows to ASSEMBLE onto the host, so when fork's read-API + DNA's archetypes + the keystone-lock land, the surfaces drop in MECHANICALLY — no host plumbing per surface. Companion to DECISION-CARD-HOST-CONTRACT.md + STACK-ITEM-HOST-CONTRACT.md. The four seams below are BUILT + verified (this session); a FACE-1 surface = recollection's DATA (via fork's read-API) → projection's HOST (these seams) → DNA's RENDER (the archetype).*

> ★ The host holds NO per-surface variant knowledge. A new FACE-1 face = a registered surface that uses these seams + its DNA archetype + its fork data-route. ZERO change to the host shell. (registry-is-truth; the instrument stays empty.)

## SEAM 1 · MOUNT — a sibling overlay, every form factor
A FACE-1 surface mounts as an **App-root sibling overlay** (the proven pattern: `GalleryMount` · `DecisionsInbox` · `ToolsPanel`), NOT inside a layout module. So it overlays cleanly on desktop/portrait/landscape with no per-form-factor branch.
- A tiny subscribe-store holds its `{open, …}` state (mirror `decisionsStore`/`toolsStore` — ONE store, no double-fetch/drift). Open via a dispatched event or a store action.
- The overlay is always in the DOM (visibility toggled), so a render ref / DNA element stays valid.
- Reuse `.gallery-overlay`/modal scaffolding + the device allocation (SEAM 5) — do NOT hand-roll positioning.

## SEAM 2 · EMIT — the one verb bus (`gallery:verb`)
Every operator action dispatches the ONE envelope: `window.dispatchEvent(new CustomEvent('gallery:verb', {detail:{verb, aim_address, payload?}}))`. The App-side listener routes it (navigate/open-source/annotate/drive/generate + the decision-take). 
- A verb with no specific handler shows an **honest Notice** (fail-loud, never a silent no-op) — so a FACE-1 surface can emit a new verb today and it surfaces honestly until its handler lands.
- `aim_address` is the resolvable ui:// of the aimed thing (NEVER shown to the operator). Adding a new verb = a case in the one listener, ZERO surface-side change.

## SEAM 3 · POINT — declare affordances pointable inline (auto-included)
Any element the RHM/brain should be able to spotlight declares its pointability **inline**: `data-ui-ref="ui://…"` (its address) + `data-point-label="<human role>"`. `window.surfacePointables()` AUTO-DISCOVERS it (alongside the curated map-controls) — no catalog edit. (lib/pointables.ts, this session.)
- The token returned to the brain is **OPAQUE** (`auto-N`, per-call) — a ui:// NEVER reaches the brain (operator-law / address-free-brain). fork-brain-core maps token→address from the same list.
- Only DOM-present elements are returned (live reflection) — a surface that closes leaves the catalog automatically.
- The `data-point-label` is operator-facing copy (AI-draft, Tim-steerable).

## SEAM 4 · RESOLVE — any address → HUMAN context (never a raw ui://)
To show "what this is" for any addressed thing (a session, a board item, a channel), the host resolves it via `GET /api/territory?address=<ui://…>` (`territory_for` → identity.meaning + context + relations + the operator's notes) — the same path the see-the-record panel + the decision-card enrich use.
- Operator-law: render the HUMAN meaning; the address is the mechanism, NEVER displayed. `territory_prose` strips ui:// to meaning server-side.
- "Address-system surfaced" (the FACE-1 item) = this resolve-to-human, NOT a raw-address widget.
- Every surface element carries its address via `stamp('ui://…')` (lib/address.ts / the `locus` layer) → addressable + navigable + spotlight-able for free.

## SEAM 5 · DEVICE — allocation resolves from the coordinate (no @media)
The surface's layout allocation resolves from the **device-coordinate** (`body[data-ff]` now; fork's `resolve(invariant, coordinate)` via `/api/resolve` on the bounce — RESOLVER-CONTRACT.md), NOT hand-written breakpoints. A FACE-1 surface authors its allocation as the same MODAL/SHELL slot relationships (continuous derivations + orient selects) and consumes the resolved CSS vars (degrade-clean). One definition → all coordinates.

## THE ASSEMBLY (when the gates clear)
For each FACE-1 surface: fork lands its read-route (data) → DNA lands its archetype (render) → projection mounts it as a sibling overlay (SEAM 1), wires its verbs (SEAM 2), its elements declare pointability (SEAM 3) + carry addresses (stamp), it resolves things via /api/territory (SEAM 4), and its allocation resolves from the device-coordinate (SEAM 5). The host shell is unchanged. The four seams are READY today; the renders wait on the keystone-lock.
