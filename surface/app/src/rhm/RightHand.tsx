import { type PointerEvent as RPE, useCallback, useEffect, useRef, useState } from 'react'
import { stamp } from '../lib/address'
import vIcon from './v-icon.svg'

// THE RIGHT-HAND-MAN (the 'V') — the RHM's persistent identity, on EVERY page (App mounts it once, a sibling to
// the layout + the gallery). Tim 2026-06-17: a draggable overlay in the bottom-right that fans its options out
// around the corner angle, in thumb reach, never taking over the screen; movable so you can read under it. AND
// the LOADABLE BRAIN: tapping "Ask" opens a panel where the operator TALKS to the right-hand-man (real Claude
// Code) about whatever the V is aimed at.
//
// SWAP SEAM (composition's V-corner-handle contract): the real V organism later renders into THIS container — we
// MEET AT THE DATA (no cross-repo code import). BRAIN SEAM (fork): forkVBrain.attach({panelEl, getAimAddress,
// getAimLabel}) — the V host (here) owns the AIM; fork owns the turn/stream/write at that aim. We meet at the aim.

// The six verbs the right-hand-man collects from the surface (composition's contract). `id` is the CONTRACT verb;
// `label` is operator-facing DRAFT copy — TENTATIVE, for Tim/DNA to ratify. 'ask' opens the brain panel (WIRED);
// the rest emit `rhm:verb` for their own integration phase (navigate/annotate/drive/open-source/generate).
const VERBS = [
  { id: 'navigate', label: 'Go to' },
  { id: 'ask', label: 'Ask' },
  { id: 'annotate', label: 'Note' },
  { id: 'drive', label: 'Drive' },
  { id: 'open-source', label: 'Source' },
  { id: 'generate', label: 'Make' },
] as const

// the V's default aim when the operator hasn't pointed it at anything — the surface itself (territory_label
// degrades this to a human noun; the brain composes whatever context it can). Never shown raw to the operator.
const SURFACE_AIM = 'ui://instrument/surface'

type Pos = { x: number; y: number } | null
type Drag = { id: number; ox: number; oy: number; sx: number; sy: number; moved: boolean }
type Brain = { ask: (p?: string) => unknown; direct: (i: unknown) => unknown; aimChanged: () => void; destroy: () => void }

const POS_KEY = 'rhm.handle.pos'

export function RightHand() {
  const [open, setOpen] = useState(false) // the verb fan
  const [panelOpen, setPanelOpen] = useState(false) // the brain (Ask) panel
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
  const panelRef = useRef<HTMLDivElement>(null)
  const brainRef = useRef<Brain | null>(null)
  const aimRef = useRef<string>(SURFACE_AIM) // the CURRENT aim address (read live by the brain)
  const labelRef = useRef<string>('this part of the surface') // the HUMAN aim label (never the raw address)

  // ── MOUNT THE BRAIN (fork's forkVBrain) into the panel, once ────────────────────────────────────────
  // The V host owns the aim (getAimAddress/getAimLabel); fork owns the turn/stream/write. Fail-soft if the
  // brain module isn't loaded (the panel still renders; talk just no-ops) — never crash the surface.
  useEffect(() => {
    const fv = (window as unknown as { forkVBrain?: { attach: (c: unknown) => Brain } }).forkVBrain
    if (!fv || !panelRef.current) return
    try {
      brainRef.current = fv.attach({
        panelEl: panelRef.current,
        getAimAddress: () => aimRef.current,
        getAimLabel: () => labelRef.current,
        placeholder: 'Ask about what you’re looking at…',
      })
    } catch {
      brainRef.current = null
    }
    return () => {
      try {
        brainRef.current?.destroy()
      } catch {
        /* already gone */
      }
      brainRef.current = null
    }
  }, [])

  // ── FOLLOW THE OPERATOR'S AIM ───────────────────────────────────────────────────────────────────────
  // selecting a wheel-point (projection:select) re-aims the V's brain at that addressed unit; fetch its HUMAN
  // label (operator-law: the panel shows MEANING, never the address) + refresh. Default = the surface itself.
  useEffect(() => {
    const onSelect = (e: Event) => {
      const d = (e as CustomEvent).detail as { address?: string; source?: string } | null
      aimRef.current = d?.address || d?.source || SURFACE_AIM
      fetch(`/api/territory/label?address=${encodeURIComponent(aimRef.current)}`)
        .then((r) => (r.ok ? r.json() : null))
        .then((j: { label?: string } | null) => {
          if (j?.label) {
            labelRef.current = j.label
            try {
              brainRef.current?.aimChanged()
            } catch {
              /* not mounted */
            }
          }
        })
        .catch(() => {
          /* label is best-effort; the brain still talks at the aim */
        })
    }
    window.addEventListener('projection:select', onSelect)
    return () => window.removeEventListener('projection:select', onSelect)
  }, [])

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
    if (id === 'ask') {
      // the WIRED verb: open the brain panel — talk to the right-hand-man about the current aim
      setOpen(false)
      setPanelOpen(true)
      return
    }
    // the other verbs are SEAMS: the integration phase (with fork) wires each to its backend
    window.dispatchEvent(new CustomEvent('rhm:verb', { detail: { verb: id } }))
    setOpen(false)
  }, [])

  // close the fan / panel on Escape or an outside press
  useEffect(() => {
    if (!open && !panelOpen) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setOpen(false)
        setPanelOpen(false)
      }
    }
    const onDown = (e: PointerEvent) => {
      const t = e.target as Node
      const inHandle = !!elRef.current?.contains(t)
      const inPanel = !!panelRef.current?.contains(t)
      if (!inHandle && !inPanel) {
        setOpen(false)
        setPanelOpen(false)
      }
    }
    window.addEventListener('keydown', onKey)
    window.addEventListener('pointerdown', onDown, true)
    return () => {
      window.removeEventListener('keydown', onKey)
      window.removeEventListener('pointerdown', onDown, true)
    }
  }, [open, panelOpen])

  const style = pos ? { left: `${pos.x}px`, top: `${pos.y}px`, right: 'auto', bottom: 'auto' } : undefined

  return (
    <>
      {/* a soft paper scrim so the open fan / brain panel reads as an overlay ABOVE the surface (legible over
          the chart), without a heavy modal takeover; a press anywhere on it closes them */}
      {(open || panelOpen) && (
        <div
          className="vhandle-scrim"
          onClick={() => {
            setOpen(false)
            setPanelOpen(false)
          }}
        />
      )}

      {/* THE BRAIN PANEL — fork's forkVBrain renders `.v-brain` inside here; always in the DOM (so attach has a
          target), shown when panelOpen. The operator talks to the right-hand-man about the current aim. */}
      <div ref={panelRef} className="v-brain-panel" data-open={panelOpen} {...stamp('ui://rhm/brain')}>
        <button className="v-brain-close" type="button" aria-label="Close" onClick={() => setPanelOpen(false)}>
          ×
        </button>
      </div>

      <div ref={elRef} className="vhandle" data-open={open} style={style} {...stamp('ui://rhm/handle')}>
        {open && (
          <div className="vhandle-fan" role="menu" aria-label="Right-hand-man actions">
            {VERBS.map((v, i) => {
              // a thumb arc rising from the bottom-right corner: EVEN vertical spacing (no overlap), leaning
              // LEFT as it climbs (the "around the angle" curve). Pills RIGHT-edge anchored (translate(-100%,…)).
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
