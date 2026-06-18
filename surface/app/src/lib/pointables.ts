// THE POINTABLE-TARGETS CATALOG — the surface's self-knowledge of what the RHM/brain can "point at" (the spotlight
// v2's surface-sourced source of truth). WHY surface-sourced: the brain's context is address-free (territory_prose
// strips every ui:// to human meaning — operator-law), and the SERVER carries no per-control labels (verified:
// /api/territory/label for ui://controls/* and ui://instrument/* returns the generic "this part of the surface").
// So the human meaning of the controls lives HERE, on the surface. The spotlight flow (fork's v2): the brain picks a
// TOKEN (an opaque handle, never a ui://) from this catalog by meaning → fork-brain-core maps token→address →
// dispatches `ui:point {address}` → the existing sink (installPointerBridge → resolveUiTarget) spotlights it.
//
// Exposed as window.surfacePointables() so fork-brain-core reads the LIVE set at send-time (only targets currently
// rendered in the DOM are returned — e.g. the scrubber/centre come and go by layout/state). The TOKEN→address map
// is the same list, so fork maps a returned token back to its address with no address ever reaching the brain.
//
// LABELS are AI-SUPPLIED DRAFTS (operator-facing copy) — marked for Tim's steer; only FINAL copy is gated.
// (Sectors ui://instrument/sector/<id> are addressable + pointable too, but DNA currently SUPPRESSES their spotlight
// visual [surface.css:310] and their labels are dynamic per-lens — deferred from v1 until DNA un-suppresses; flagged.)

export type Pointable = { token: string; address: string; label: string }

// the curated affordance catalog — token (opaque handle), the stamped ui:// address, the human role-description.
const CATALOG: Pointable[] = [
  { token: 'wheel', address: 'ui://instrument/wheel', label: 'the live map — every recent thing, shown as dots' },
  { token: 'lens', address: 'ui://controls/lens', label: 'the lens — what the dots are grouped by' },
  { token: 'space', address: 'ui://controls/space', label: 'which set of things is shown' },
  { token: 'layer', address: 'ui://controls/layer', label: 'what signal positions the dots' },
  { token: 'resolution', address: 'ui://controls/resolution', label: 'how finely the dots are grouped' },
  { token: 'representation', address: 'ui://controls/representation', label: 'how the dots are drawn' },
  { token: 'view', address: 'ui://controls/view', label: 'circle vs square — the two coordinate systems' },
  { token: 'centre', address: 'ui://controls/centre', label: 'the centre — what everything is measured from' },
  { token: 'time', address: 'ui://controls/scrubber', label: 'the time scrubber — move to a past moment' },
  { token: 'live', address: 'ui://controls/live', label: 'the live indicator — the present is moving' },
  { token: 'legend', address: 'ui://instrument/legend', label: 'the legend — what the colours and slices mean' },
]

function cssEscape(s: string): string {
  return s.replace(/(["\\])/g, '\\$1')
}

let _installed = false
export function installPointables() {
  if (_installed) return
  _installed = true
  // return ONLY the targets currently in the DOM — the catalog reflects what's actually pointable right now.
  ;(window as unknown as { surfacePointables: () => Pointable[] }).surfacePointables = () =>
    CATALOG.filter((p) => document.querySelector(`[data-ui-ref="${cssEscape(p.address)}"]`))
}
