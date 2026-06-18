import { useEffect, useRef, useCallback, useState } from 'react'

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
  // the address of the CURRENTLY-mounted face — so a write's re-render (gallery:rerender) can refresh THIS face.
  const currentAddrRef = useRef<string>('')
  // CARRY the decision's `subtype` + `render_kind` (composition's locked subtype contract, g-1781731457; lead-ruled
  // the host's one contract-time change). The host stays VARIANT-AGNOSTIC — it never SELECTS a variant (that's DNA's
  // render, from the subtype); it only CARRIES these so its own re-emit of decision:rendered (on the rerender
  // refresh) preserves the contract shape instead of dropping fields, and advertises them on the frame for any
  // consumer. render_kind is the lifecycle lever ('slide' = single, handled now; 'sequence' = a future host
  // walk-driver, built only when a real sequence instance renders — lead's steer, not speculatively).
  const currentSubtypeRef = useRef<string>('')
  const currentRenderKindRef = useRef<string>('slide')
  // a deep-link (?decide=) shows an honest LOADING state while the decision resolves (it can be slow — the
  // recall-grounding), then the card (cleared by onDecisionRendered), or a fail-LOUD error if it never arrives —
  // never a silent blank (no-silent-failures).
  const [dlState, setDlState] = useState<'' | 'loading'>('')

  const dismiss = useCallback(() => { decisionModeRef.current = false; setDlState(''); onOpenChange(false) }, [onOpenChange])

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
      currentAddrRef.current = d.address || ''
      currentSubtypeRef.current = ''; currentRenderKindRef.current = 'slide' // a corpus face carries no decision subtype
      titleRef.current?.removeAttribute('data-decision-subtype')
      titleRef.current?.removeAttribute('data-render-kind')
      setTitle(d.address || '', 'drilled unit')
      onOpenChange(true)
    }
    // UNION-SEAM WELD (2026-06-18 seam audit): fork-brain-core fires `gallery:rerender {element_id}` after a
    // route-back WRITE (an annotation, or a decision TAKE) so the affected face refreshes with the new mark —
    // but NOTHING listened, so a write never visually refreshed (the seam was unwelded). The HOST owns the mount
    // lifecycle → re-mounting is the host's job. On a rerender whose element_id belongs to the CURRENTLY-mounted
    // face (element_id is the bare address or `<addr>#elem`), re-render it: a decision face re-fires
    // decision:rendered (DNA re-renders the now-decided card); a corpus face re-invokes window.DNA.renderGallery
    // (re-fetch → show the new annotation). Degrade-clean (no DNA.renderGallery / no match → no-op; never throws).
    // Replaceable: DNA may later refresh IN PLACE (finer than a full re-mount) — this is the baseline weld.
    const onRerender = (e: Event) => {
      const d = (e as CustomEvent).detail || {}
      const base = String(d.element_id || '').split('#')[0]
      const cur = currentAddrRef.current
      if (!cur || !base || base !== cur) return // not the mounted face → not ours to refresh
      if (decisionModeRef.current) {
        // re-render the decided card — PRESERVE the contract shape (subtype/render_kind) so the host's re-emit
        // doesn't drop fields a consumer (or DNA's variant-select) reads off the event.
        window.dispatchEvent(new CustomEvent('decision:rendered', { detail: { address: cur, subtype: currentSubtypeRef.current || undefined, render_kind: currentRenderKindRef.current } }))
      } else {
        try { window.DNA?.renderGallery?.(cur, { container: containerRef.current as HTMLElement }) } catch { /* best-effort refresh */ }
      }
    }
    // DNA fires `decision:rendered` per decision-SLIDE (g-1781731457 Q3 — projection's chosen key, a sibling to
    // gallery:rendered with the same payload shape). Advancing the walk re-renders the SAME hosted container
    // (content swaps per decision); we open + HOLD open. Mark decision-mode so a wheel-deselect can't kill the walk.
    const onDecisionRendered = (e: Event) => {
      const d = (e as CustomEvent).detail as { address?: string; subtype?: string; render_kind?: string } || {}
      decisionModeRef.current = true
      setDlState('') // a card rendered → clear any deep-link loading/error state
      currentAddrRef.current = d.address || ''
      currentSubtypeRef.current = String(d.subtype || '')                 // carry it (DNA SELECTS the variant from it; host only carries)
      currentRenderKindRef.current = String(d.render_kind || 'slide')     // the lifecycle lever; 'slide' handled now
      if (titleRef.current) { // advertise on the frame for any consumer (inspectable carry)
        if (currentSubtypeRef.current) titleRef.current.setAttribute('data-decision-subtype', currentSubtypeRef.current)
        else titleRef.current.removeAttribute('data-decision-subtype')
        titleRef.current.setAttribute('data-render-kind', currentRenderKindRef.current)
      }
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
    window.addEventListener('gallery:rerender', onRerender)
    window.addEventListener('projection:select', onSelect)
    window.addEventListener('keydown', onKey)
    return () => {
      window.removeEventListener('gallery:rendered', onRendered)
      window.removeEventListener('decision:rendered', onDecisionRendered)
      window.removeEventListener('gallery:rerender', onRerender)
      window.removeEventListener('projection:select', onSelect)
      window.removeEventListener('keydown', onKey)
    }
  }, [onOpenChange])

  // OPEN A DECISION INTO THE HOST — the ONE opener, shared by the URL deep-link AND the in-surface inbox.
  // Renders the decision address into the host container with an honest LOADING state (the resolve can be slow —
  // the recall-grounding — so show "opening…", never a blank). Polls every 250ms over a generous ~20s window:
  // re-attempts the render only if the previous one REJECTED (inFlight cleared on .catch; on success it stays
  // in-flight while the slow resolve completes, and the card render clears the loading via onDecisionRendered).
  // `<id>` → decision://global/<id>; a full address (with ://) is accepted as-is. Honest no-op if DNA isn't loaded.
  const openDecision = useCallback((rawId: string) => {
    const id = (rawId || '').trim()
    if (!id) return () => {}
    const addr = id.includes('://') ? id : `decision://global/${id}`
    setDlState('loading')
    onOpenChange(true)
    let cancelled = false
    let inFlight = false
    let tries = 0
    const tick = () => {
      if (cancelled) return
      const container = containerRef.current
      // rendered → stop polling (onDecisionRendered already cleared dlState). Key off the SEMANTIC marker the
      // card carries — `data-decision-address` — NOT a cosmetic class: since the one-engine collapse (renderDecision
      // RETIRED 2026-06-19) the card draws through DNA.renderArchetype, whose root is `.ar-card`, not `.decision-card`.
      // The data-attribute is engine-agnostic (set whichever renderer draws it), so the host stays variant-agnostic.
      if (container?.querySelector('[data-decision-address], .decision-card')) return
      if (!inFlight && container && window.DNA?.renderGallery) {
        inFlight = true
        window.DNA.renderGallery(addr, { container }).catch(() => { inFlight = false /* rejected → allow a retry */ })
      }
      if (tries++ < 80) setTimeout(tick, 250)
      // after the window we stop RE-attempting, but the in-flight render (slow resolve) still resolves later +
      // clears the loading state via onDecisionRendered. The honest "Opening…" stays until the card arrives.
    }
    tick()
    return () => { cancelled = true }
  }, [onOpenChange])

  // DEEP-LINK (trigger 1) — open a specific decision card straight from the URL (`?decide=<id>`). The direct
  // "open this" link for Tim on his phone (the lead hands him the link → he lands on the card → decides in-surface).
  useEffect(() => {
    let id = ''
    try { id = new URLSearchParams(window.location.search).get('decide') || '' } catch { /* blocked search params */ }
    if (!id) return
    return openDecision(id)
  }, [openDecision])

  // THE INBOX (trigger 2) — the in-surface "decisions waiting" list dispatches `decision:open {id|address}` when the
  // operator taps a row; this renders that decision through the SAME opener (one path, no parallel render logic).
  useEffect(() => {
    const onOpen = (e: Event) => {
      const d = (e as CustomEvent).detail || {}
      openDecision(d.address || d.id || '')
    }
    window.addEventListener('decision:open', onOpen)
    return () => window.removeEventListener('decision:open', onOpen)
  }, [openDecision])

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
        {/* deep-link loading — an honest "opening…" while the decision resolves (it can be slow), never a silent
            blank. React sibling of the (empty) mount; cleared when the card renders (onDecisionRendered). */}
        {dlState === 'loading' && (
          <div className="gallery-deeplink-error" role="status">
            <p>Opening this decision…</p>
          </div>
        )}
      </div>
    </div>
  )
}
