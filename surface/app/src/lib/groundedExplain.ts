// THE GROUNDED WALK-THROUGH — projection's half of the L1 three-party wire (lead g-1782040329).
//   fork's POST /api/decision/explain (the route — built ✓, returns the grounded {what_this_is, why_it_matters,
//   grounding_note}) → DNA's renderGallery resolve-override seam (renderGallery passes the host's opts.resolve
//   through to the `explanation_source` slot) → THIS (the host resolve-injection) → the decision-card's `explain`
//   slot (slot_map: explain → resolve:explanation_source) SHOWS the grounded explanation.
//
// WHY THIS EXISTS (the middle was empty — the session's substrate-ahead-of-wiring catch): the card's explain slot
// has ALWAYS been fed by DNA's leg.why STUB (unit-view.js:145: `name==='explanation_source' ? (leg.why || raw)`),
// never the grounded route — route ✓ + slot ✓ looked wired, the connector wasn't built. This is that connector.
//
// GATED — held OFF pending DNA's RENDER side (by-sight finding at the flip): all 3 backend/seam pieces are built
// (fork route ✓ + DNA resolve-override seam 84dd35d ✓ + this injection ✓) AND grounding is complete across the queue
// (backfill + theorem rebake). BUT flipping ON + verifying by-sight showed the grounded explanation DOES NOT RENDER:
// the composed decision card DROPS the explanation slot (archetype.js:178 `if composed && role==='explanation'`), and
// the visible explanation is the SLIDE-TELLING (DNA.decisionSlide, unit-view.js:165) which is called WITHOUT the
// resolve override — so my fetch fires but lands in a dropped slot. The show-gap is DNA's render (route the grounded
// resolve to decisionSlide's telling, OR render the explain slot in the composed card). Held OFF until then (no
// pointless fetches, no false-live). FLIP true + re-verify the show the instant DNA's render renders it.
export const GROUNDED_EXPLAIN_ENABLED = false

// POST /api/decision/explain {id} → the grounded explanation composed for the card's explain (prose voice-card) slot.
// Returns the composed walk-through string, or '' (DEGRADE-CLEAN → the slot falls back to DNA's resolution, never a
// fabricated value). theorem-fork is slow (~18s, the deep grounded run); returning a Promise makes DNA's archetype
// render the "…" placeholder (archetype.js:422 — async → placeholder, caller streams in) and fill it on resolve.
export async function fetchGroundedExplain(decisionId: string): Promise<string> {
  try {
    const r = await fetch('/api/decision/explain', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ id: decisionId }),
    })
    if (!r.ok) return '' // route 400/500 (e.g. mid-bounce) → fall back, no contradiction
    const d = await r.json()
    if (!d || d.ok === false) return ''
    const e = (d.explanation || {}) as Record<string, unknown>
    // the explain slot renders ONE prose voice-card → compose the grounded what + why. The grounding_note/provenance
    // rides DNA's separate grounding_provenance meta-slot (fork's contract), not this prose body. Degrade per-field.
    const what = typeof e.what_this_is === 'string' ? e.what_this_is.trim() : ''
    const why = typeof e.why_it_matters === 'string' ? e.why_it_matters.trim() : ''
    return [what, why].filter(Boolean).join('\n\n')
  } catch {
    return '' // network / route down → the stub fallback, never a fabricated explanation
  }
}

// The resolve-override GalleryMount passes into DNA.renderGallery once DNA opens the seam. Returns a resolver the
// archetype calls with each `resolve:<key>` slot source; ONLY explanation_source is grounded here (every other key →
// undefined → DNA's own resolution/stub stays in charge — narrow, single-purpose). Returns undefined entirely while
// gated off, so GalleryMount supplies no override at all (DNA keeps its current behavior). id = leaf of decision://.
export function makeGroundedResolve(addr: string): ((name: string) => Promise<string> | undefined) | undefined {
  if (!GROUNDED_EXPLAIN_ENABLED) return undefined
  const id = (addr.split('/').pop() || '').trim()
  if (!id) return undefined
  return (name: string) => (name === 'explanation_source' ? fetchGroundedExplain(id) : undefined)
}
