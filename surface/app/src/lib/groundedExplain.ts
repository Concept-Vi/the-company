// THE GROUNDED WALK-THROUGH — projection's half of the L1 wire (lead g-1782040329 → g-1782042879, build-complete).
//   fork's POST /api/decision/explain (route ✓, returns {what_this_is, why_it_matters, grounding_note}) → DNA's
//   renderGallery resolve-override seam (84dd35d ✓) → THIS host injection → DNA's .dc-explain GROUNDED-EXPLAIN region
//   (archetype.js:238-260, eb85afb ✓ — a voice card BELOW the panels in the binary + n-panel branches) SHOWS it.
//
// WHY THIS EXISTS (the session's substrate-ahead-of-wiring catch): the explanation had no render home — the composed
// card dropped the slot + decisionSlide's telling got no resolve. DNA's eb85afb built the inline .dc-explain region;
// this feeds it. The by-sight closure-test caught each empty middle before it reached Tim.
//
// SHAPE (matches DNA's region exactly, archetype.js:251-255): return the structured OBJECT — what_this_is → main
// text, why_it_matters → the "Why this matters —" line, grounding_note → the ground-note. DNA also accepts a bare
// string (degrades to prose) and degrades to its stub on '' — so '' is the clean fail value.
//
// GATED ON: all 4 pieces built (fork route ✓ + DNA seam ✓ + this injection ✓ + DNA region ✓) + grounding complete
// across the queue (backfill + theorem rebake, lead-verified). ON = GalleryMount supplies the resolve override → the
// region streams the grounded explanation in. (Theorem-fork un-gated: the rebake grounds cube/dimension in Tim's
// real math, lead-verified at source.) The by-sight verifies it SHOWS before this is called closed.
export const GROUNDED_EXPLAIN_ENABLED = true

// the structured grounded explanation — the shape DNA's .dc-explain region maps (archetype.js:251-255).
export type ExplainPayload = { what_this_is?: string; why_it_matters?: string; grounding_note?: string }

// POST /api/decision/explain {id} → the structured grounded explanation for DNA's .dc-explain region. Returns the
// {what_this_is, why_it_matters, grounding_note} OBJECT (so the full voice-card renders: text + why-line + note), or
// '' (DEGRADE-CLEAN → DNA's region falls back to its stub, never a fabricated value). The route is slow for
// theorem-fork (~18s deep grounded run); returning a Promise makes DNA render the "…" placeholder then stream in.
export async function fetchGroundedExplain(decisionId: string): Promise<ExplainPayload | string> {
  try {
    const r = await fetch('/api/decision/explain', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ id: decisionId }),
    })
    if (!r.ok) return '' // route 400/500 (e.g. mid-bounce) → fall back to the stub, no contradiction
    const d = await r.json()
    if (!d || d.ok === false) return ''
    const e = (d.explanation || {}) as Record<string, unknown>
    const what = typeof e.what_this_is === 'string' ? e.what_this_is.trim() : ''
    if (!what) return '' // no grounded content → degrade to DNA's stub (never an empty grounded card)
    const payload: ExplainPayload = { what_this_is: what }
    if (typeof e.why_it_matters === 'string' && e.why_it_matters.trim()) payload.why_it_matters = e.why_it_matters.trim()
    if (typeof e.grounding_note === 'string' && e.grounding_note.trim()) payload.grounding_note = e.grounding_note.trim()
    return payload
  } catch {
    return '' // network / route down → the stub fallback, never a fabricated explanation
  }
}

// The resolve-override GalleryMount passes into DNA.renderGallery. The archetype calls it with each `resolve:<key>`
// slot source; ONLY explanation_source is grounded here (every other key → undefined → DNA's own resolution stays in
// charge — narrow, single-purpose). Returns undefined entirely while gated off (GalleryMount then supplies no
// override → DNA's stub). id = leaf of decision://<frame>/<id>.
export function makeGroundedResolve(
  addr: string,
): ((name: string) => Promise<ExplainPayload | string> | undefined) | undefined {
  if (!GROUNDED_EXPLAIN_ENABLED) return undefined
  const id = (addr.split('/').pop() || '').trim()
  if (!id) return undefined
  return (name: string) => (name === 'explanation_source' ? fetchGroundedExplain(id) : undefined)
}
