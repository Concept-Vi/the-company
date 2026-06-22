import { useEffect, useRef } from 'react'
import { openDecisionsList } from '../decisions/decisionsStore'
import { stamp } from '../lib/address'
import './nav.css'

// THE SURFACE NAV (the cross-cutting "link all faces — navigable between them" criterion). Tim's gap (2026-06-22):
// the breadth surfaces (the fabric / the board / sessions) were BUILT but ORPHAN — opened only by window events
// nothing dispatched, so Tim couldn't reach his own screens. This is the missing LINK. The RENDER is DNA's
// (DNA.org.navRail — icon+label tiles, navigable-not-a-menu-wall, operator-law human labels; 179cea0); the HOST
// (this) positions the rail + wires each tile's data-nav → opening its surface (the contract DNA's navRail declares:
// "the HOST wires each tile's data-nav → setView(<id>)"). Degrade-clean: if DNA.org.navRail isn't loaded, fall back
// to plain labelled buttons so Tim can ALWAYS reach his screens (the unblock must never depend on the render).
//
// Each surface is a sibling-overlay over the instrument (the map = home); opening one shows it, closing returns to
// the map. Decisions mirrors the count-pill's openDecisionsList (one open-path). Transcript (History) is the corpus
// searched by meaning as a constellation — query-driven, opens on `transcript:open`. The map tile returns to the
// instrument (dismiss overlays).

type Surface = { id: string; label: string; icon?: string; open: () => void }

const SURFACES: Surface[] = [
  // the map = home: dismiss any open overlay (each overlay closes on Escape-when-open) → back to the instrument.
  { id: 'map', label: 'The map', icon: 'compass', open: () => window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' })) },
  { id: 'decisions', label: 'Decisions', icon: 'ledger', open: () => openDecisionsList() },
  { id: 'fabric', label: 'The fabric', icon: 'plug', open: () => window.dispatchEvent(new CustomEvent('channels:open')) },
  { id: 'board', label: 'The board', icon: 'plan', open: () => window.dispatchEvent(new CustomEvent('board:open')) },
  { id: 'sessions', label: 'Sessions', icon: 'chat', open: () => window.dispatchEvent(new CustomEvent('sessions:open')) },
  { id: 'transcript', label: 'History', icon: 'history', open: () => window.dispatchEvent(new CustomEvent('transcript:open')) },
]

type DNAGlobal = { org?: { navRail?: (o: unknown) => string } }
const dnaNav = () => (window as unknown as { DNA?: DNAGlobal }).DNA?.org?.navRail

export function SurfaceNav() {
  const ref = useRef<HTMLDivElement>(null)
  const byId = (id: string) => SURFACES.find((s) => s.id === id)?.open

  // render DNA's navRail (its design) into the host + delegate tile taps → open the surface. Degrade-clean: no
  // navRail → React's fallback buttons (below) stay. Re-render once on mount (the surface set is static).
  useEffect(() => {
    const host = ref.current
    const navRail = dnaNav()
    if (!host || !navRail) return // DNA not loaded → the fallback buttons render; nav still works
    try {
      host.innerHTML = navRail({ items: SURFACES.map((s) => ({ id: s.id, label: s.label, icon: s.icon })), vertical: true, label: 'Screens' })
      const onClick = (e: Event) => {
        const t = (e.target as HTMLElement)?.closest('[data-nav]') as HTMLElement | null
        if (!t) return
        byId(t.getAttribute('data-nav') || '')?.()
      }
      host.addEventListener('click', onClick)
      return () => host.removeEventListener('click', onClick)
    } catch {
      /* navRail threw → leave the fallback buttons (degrade-clean) */
    }
  }, [])

  return (
    <div className="surface-nav" aria-label="Screens" {...stamp('ui://nav/surfaces')}>
      {/* DNA's navRail mounts here when loaded; until/unless it does, the fallback buttons below keep the nav working */}
      <div ref={ref} className="surface-nav-dna" />
      <div className="surface-nav-fallback">
        {SURFACES.map((s) => (
          <button key={s.id} className="surface-nav-item" type="button" onClick={s.open} {...stamp(`ui://nav/surface/${s.id}`)}>
            {s.label}
          </button>
        ))}
      </div>
    </div>
  )
}
