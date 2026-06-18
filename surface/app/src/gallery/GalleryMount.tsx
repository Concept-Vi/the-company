import { useEffect, useRef, useCallback } from 'react'

// THE DOM-MOUNT SEAM (front-interface FIRST SLICE — the lead/DNA/fork converged ask, 2026-06-16).
//
// projection drives the wheel (SpaceChip → common_knowledge → click a unit → `projection:select`); DNA's
// render module (window.DNA, hosted from index.html — see scripts/sync-gallery.mjs) turns that drilled
// address into the gallery FACE. This component is the HOST: it gives DNA's vanilla render a STABLE
// container React never reconciles, and binds the drill ONCE. The contract the fabric agreed:
//   • the container is a plain <div id="gallery-mount"> with NO React children → React leaves its subtree
//     alone, so DNA's innerHTML + fork's brain-anchor + wildcard's annotation-strip keep STABLE refs across
//     React re-renders (the whole reason hosting here beats DNA's standalone :8090).
//   • DNA.renderGallery fetches /api/cognition/corpus?address= — RELATIVE, so SAME-ORIGIN here (the surface
//     proxies /api → :8770), which fixes the CORS block DNA hit standalone.
//   • DNA emits `gallery:rendered {element, address, source, record}` AFTER it mounts → we open the face,
//     and fork/wildcard bind to THAT element post-render (the no-DOM-race order the lead set).
//
// COHERENCE (FORM): selecting a point also drives the Disclosure inspector (projection's own panel). The
// gallery FACE is the DRILL-IN — a deliberate modal over the wheel (scrim focus), NOT a second always-on
// panel. Open on render, dismiss returns to the wheel + inspector. One drilled-unit surface at a time.
//
// StrictMode: DNA's script is a CLASSIC tag (ready pre-React), and bindProjectionDrill is called behind a
// module-level guard so dev's double-effect-invoke can't double-bind the projection:select listener.

declare global {
  interface Window {
    DNA?: {
      bindProjectionDrill?: (opts: { container: HTMLElement; source?: string | null }) => void
      renderGallery?: (address: string, opts?: { container?: HTMLElement; source?: string | null }) => Promise<HTMLElement>
    }
  }
}

let bound = false // module-level guard — bind the drill exactly once across StrictMode double-invokes

// Controlled by App (App owns `galleryOpen` so the layouts can suppress the redundant Disclosure when the
// face is up). open = is the face showing; onOpenChange = report open/close (render lands, deselect, dismiss).
export function GalleryMount({ open, onOpenChange }: { open: boolean; onOpenChange: (open: boolean) => void }) {
  const containerRef = useRef<HTMLDivElement>(null)
  const titleRef = useRef<HTMLDivElement>(null)
  // DECISION-SLIDE lifecycle decouple: a decision walk is a SEQUENCE hosted in ONE container (DNA's
  // contract, thread g-1781731457 Q3) — NOT tied to a wheel point. So while a decision slide is up, a
  // wheel-DESELECT (projection:select → null) must NOT close the face (that would kill the walk mid-
  // decision). This flag is set by `decision:rendered` and cleared by any real close (dismiss/Esc) or by a
  // normal corpus drill (gallery:rendered) — the two modes stay mutually exclusive.
  const decisionModeRef = useRef(false)

  const dismiss = useCallback(() => { decisionModeRef.current = false; onOpenChange(false) }, [onOpenChange])

  // a focused modal: when the FACE is open, recede the competing chrome (header/side-text/scrubber). A scrim
  // alone can't — dark chrome text stays legible over a dark scrim, and the header sits in the same top band as
  // the card (design-critic: "9:41" collided with the global header). Hiding the chrome = the single surface.
  useEffect(() => {
    document.body.classList.toggle('gallery-modal-open', open)
    return () => document.body.classList.remove('gallery-modal-open')
  }, [open])

  // bind the drill ONCE (guarded). DNA hosts the listener; we hand it our stable container.
  useEffect(() => {
    if (bound) return
    const container = containerRef.current
    if (!container) return
    if (!window.DNA?.bindProjectionDrill) {
      // FAIL LOUD (no silent no-op): the gallery face can't host without DNA's module loaded.
      console.error('[GalleryMount] window.DNA.bindProjectionDrill missing — gallery face NOT bound. ' +
        'Check index.html loads /gallery/unit-view.js (scripts/sync-gallery.mjs ran?).')
      return
    }
    window.DNA.bindProjectionDrill({ container })
    bound = true
  }, [])

  // the face opens when DNA's render lands; a deselect (projection:select → null) or Esc closes it.
  useEffect(() => {
    const setTitle = (addr: string, fallback: string) => {
      if (titleRef.current) titleRef.current.setAttribute('aria-label', addr ? (addr.replace(/\/+$/, '').split('/').pop() || addr) : fallback)
    }
    const onRendered = (e: Event) => {
      const d = (e as CustomEvent).detail || {}
      decisionModeRef.current = false // a normal corpus drill exits any decision walk (modes mutually exclusive)
      setTitle(d.address || '', 'drilled unit')
      onOpenChange(true)
    }
    // DNA fires `decision:rendered` per decision-SLIDE (g-1781731457 Q3 — projection's chosen key, a sibling to
    // gallery:rendered with the same payload shape). Advancing the walk re-renders the SAME hosted container
    // (content swaps per decision); we open + HOLD open. Mark decision-mode so a wheel-deselect can't kill the walk.
    const onDecisionRendered = (e: Event) => {
      const d = (e as CustomEvent).detail || {}
      decisionModeRef.current = true
      setTitle(d.address || '', 'decision')
      onOpenChange(true)
    }
    const onSelect = (e: Event) => {
      const d = (e as CustomEvent).detail
      if (decisionModeRef.current) return // a decision walk isn't tied to wheel selection — ignore deselect while it's up
      if (!d || !d.address) onOpenChange(false) // deselect / address-less point closes the (corpus) face
    }
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') { decisionModeRef.current = false; onOpenChange(false) } }
    window.addEventListener('gallery:rendered', onRendered)
    window.addEventListener('decision:rendered', onDecisionRendered)
    window.addEventListener('projection:select', onSelect)
    window.addEventListener('keydown', onKey)
    return () => {
      window.removeEventListener('gallery:rendered', onRendered)
      window.removeEventListener('decision:rendered', onDecisionRendered)
      window.removeEventListener('projection:select', onSelect)
      window.removeEventListener('keydown', onKey)
    }
  }, [onOpenChange])

  // The overlay is ALWAYS rendered (visibility toggled by class) — never React-unmounted — so the inner
  // #gallery-mount stays in the DOM and DNA's captured container ref + the rendered element stay valid.
  return (
    <div className={`gallery-overlay ${open ? 'gallery-overlay--open' : ''}`} aria-hidden={!open}>
      <div className="gallery-scrim" onClick={dismiss} />
      {/* the dismiss is a MODAL-level control (overlay child, not card child) — viewport top-right, clear of
          the centred card on desktop and of DNA's in-card sbar glyphs */}
      <button className="gallery-dismiss" onClick={dismiss} aria-label="close">✕</button>
      <div className="gallery-frame" role="dialog" aria-label="drilled unit" ref={titleRef}>
        {/* DNA owns this subtree's innerHTML — React renders the div once and never reconciles its children */}
        <div id="gallery-mount" ref={containerRef} className="gallery-mount" />
      </div>
    </div>
  )
}
