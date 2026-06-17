import { type PointerEvent as RPE, useCallback, useEffect, useRef, useState } from 'react'
import { stamp } from '../lib/address'
import vIcon from './v-icon.svg'

// THE RIGHT-HAND-MAN HANDLE (the 'V') — the RHM's persistent identity, on EVERY page (App mounts it once, a
// sibling to the layout + the gallery). Tim 2026-06-17: a draggable overlay in the bottom-right that fans its
// options out around the corner angle, in thumb reach, never taking over the screen; movable so you can read
// under it.
//
// This is the SHELL — the swap-seam container + the verb option-set, conforming to composition's V-corner-handle
// contract (board://item-534ef183 in vi-visual-dev). LATER the real V organism (component.organism.brand-icon —
// 8 sockets + a 6-state machine) renders into THIS SAME container; we MEET AT THE DATA (no cross-repo code
// import). So the seam = { this container + the 6-verb fan }. The icon is composition's company-gold monogram
// (vi-classic-gold.svg, copied in), swapped for the live organism later.

// The six verbs the right-hand-man collects from the surface (composition's contract). `id` is the CONTRACT verb
// (the seam the integration phase wires — a tap emits `rhm:verb` for that next phase). `label` is operator-facing
// DRAFT copy — TENTATIVE, for Tim/DNA to ratify (see OPERATOR-SURFACE-LOOP.md open questions); never machine names.
const VERBS = [
  { id: 'navigate', label: 'Go to' },
  { id: 'ask', label: 'Ask' },
  { id: 'annotate', label: 'Note' },
  { id: 'drive', label: 'Drive' },
  { id: 'open-source', label: 'Source' },
  { id: 'generate', label: 'Make' },
] as const

type Pos = { x: number; y: number } | null // explicit left/top once dragged; null = the default bottom-right anchor
type Drag = { id: number; ox: number; oy: number; sx: number; sy: number; moved: boolean }

const POS_KEY = 'rhm.handle.pos'

export function RightHand() {
  const [open, setOpen] = useState(false)
  const [pos, setPos] = useState<Pos>(() => {
    try {
      const r = localStorage.getItem(POS_KEY)
      return r ? (JSON.parse(r) as Pos) : null
    } catch {
      return null
    }
  })
  const dragRef = useRef<Drag | null>(null)
  const elRef = useRef<HTMLDivElement>(null)

  const onPointerDown = useCallback((e: RPE<HTMLButtonElement>) => {
    const el = elRef.current
    if (!el) return
    const rect = el.getBoundingClientRect()
    dragRef.current = { id: e.pointerId, ox: e.clientX - rect.left, oy: e.clientY - rect.top, sx: e.clientX, sy: e.clientY, moved: false }
    try {
      e.currentTarget.setPointerCapture(e.pointerId)
    } catch {
      /* capture is best-effort — drag still tracks via the window-relative math */
    }
  }, [])

  const onPointerMove = useCallback((e: RPE<HTMLButtonElement>) => {
    const d = dragRef.current
    if (!d || d.id !== e.pointerId) return
    if (!d.moved && Math.hypot(e.clientX - d.sx, e.clientY - d.sy) > 4) d.moved = true
    if (!d.moved) return
    const el = elRef.current
    const size = el ? el.offsetWidth : 56
    const nx = Math.min(Math.max(0, e.clientX - d.ox), window.innerWidth - size)
    const ny = Math.min(Math.max(0, e.clientY - d.oy), window.innerHeight - size)
    setPos({ x: nx, y: ny })
    setOpen(false) // moving closes the fan
  }, [])

  const onPointerUp = useCallback((e: RPE<HTMLButtonElement>) => {
    const d = dragRef.current
    dragRef.current = null
    if (!d) return
    if (d.moved) {
      // persist the new resting place (it is always there → remember where the operator put it)
      setPos((p) => {
        if (p) {
          try {
            localStorage.setItem(POS_KEY, JSON.stringify(p))
          } catch {
            /* storage blocked — position still holds for the session */
          }
        }
        return p
      })
    } else {
      setOpen((o) => !o) // a tap (no drag) toggles the fan
    }
    e.currentTarget.releasePointerCapture?.(e.pointerId)
  }, [])

  const onVerb = useCallback((id: string) => {
    // the SEAM: the integration phase (with fork — the address system + the loadable brain) consumes this.
    window.dispatchEvent(new CustomEvent('rhm:verb', { detail: { verb: id } }))
    setOpen(false)
  }, [])

  // close the fan on Escape or an outside press
  useEffect(() => {
    if (!open) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false)
    }
    const onDown = (e: PointerEvent) => {
      if (elRef.current && !elRef.current.contains(e.target as Node)) setOpen(false)
    }
    window.addEventListener('keydown', onKey)
    window.addEventListener('pointerdown', onDown, true)
    return () => {
      window.removeEventListener('keydown', onKey)
      window.removeEventListener('pointerdown', onDown, true)
    }
  }, [open])

  const style = pos ? { left: `${pos.x}px`, top: `${pos.y}px`, right: 'auto', bottom: 'auto' } : undefined

  return (
    <>
      {/* a soft paper scrim so the open fan reads as an overlay ABOVE the surface (legible over the chart),
          without a heavy modal takeover; a press anywhere on it closes the fan */}
      {open && <div className="vhandle-scrim" onClick={() => setOpen(false)} />}
      <div ref={elRef} className="vhandle" data-open={open} style={style} {...stamp('ui://rhm/handle')}>
      {open && (
        <div className="vhandle-fan" role="menu" aria-label="Right-hand-man actions">
          {VERBS.map((v, i) => {
            // a thumb arc rising from the bottom-right corner: EVEN vertical spacing (guarantees no overlap —
            // a strict even-ANGLE radial crowds at the top pole), leaning LEFT as it climbs (the "around the
            // angle" curve). Pills are RIGHT-edge anchored (translate(-100%,…)) so none crosses the right edge.
            const dy = -(44 + i * 38)
            const dx = -(28 + Math.round(104 * Math.sin((i / (VERBS.length - 1)) * (Math.PI / 2))))
            return (
              <button
                key={v.id}
                className="vhandle-verb"
                role="menuitem"
                data-verb={v.id}
                style={{ transform: `translate(-100%, -50%) translate(${dx}px, ${dy}px)` }}
                onClick={() => onVerb(v.id)}
              >
                {v.label}
              </button>
            )
          })}
        </div>
      )}
      <button
        className="vhandle-icon"
        aria-label="Right-hand-man"
        aria-expanded={open}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={onPointerUp}
      >
        <img src={vIcon} alt="" draggable={false} />
      </button>
      </div>
    </>
  )
}
