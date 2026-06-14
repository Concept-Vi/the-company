import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import type { ProjPoint, ContextBundle, Projection } from '../lib/api'
import type { MotionFeel } from '../tokens/motion'
import { transition } from '../tokens/motion'
import { contextAt } from '../lib/address'
import { pointAddress } from './Wheel'

type Variant = 'panel' | 'sheet' | 'rail'

// WHAT IT CHOSE (Tim 2026-06-14: "I don't know what it is or what it chose"). The legend says what the lens is;
// this narrates, for the SELECTED point, WHY it landed where it did — its division (angle) and what its radius
// means in the active lens — in plain words + the real value. Derived from the binding (registry-true).
type Place = { k: string; v: string; num?: string; tone?: 'born' | 'strain' | 'pile' }
// the readable leaf of a path-like id (code://projections/worldview.py → worldview.py) — no machine-dump
function leaf(s: string): string {
  const t = (s || '').replace(/[/]+$/, '')
  return t.split('/').pop() || t
}
function placement(p: ProjPoint, binding: Projection['binding'] | undefined, centre: string | null): Place[] {
  const out: Place[] = [{ k: 'in', v: leaf(p.sector) }] // the division (its kind/type) it sits in
  const rf = binding?.radius_from
  const num = (x: number | undefined) => (typeof x === 'number' ? x.toFixed(2) : '—')
  // a COARSE theme (cluster centroid) — say WHAT it is: a cluster of N, named by its exemplar (G11)
  if (p.scale_size) {
    out.push({ k: 'theme', v: `cluster of ${p.scale_members ?? p.scale_size}`, num: String(p.scale_size) })
    if (p.scale_exemplar) out.push({ k: 'e.g.', v: leaf(p.scale_exemplar) })
  }
  if (rf === 'semantic') {
    const d = p.r ?? 1
    const w = p.r_unknown ? 'no meaning vector — at the rim' : d < 0.34 ? 'close in meaning' : d < 0.67 ? 'mid-distance' : 'far in meaning'
    out.push({ k: 'meaning', v: centre ? `${w} from ${centre}` : w, num: num(p.r) })
    if (typeof p.strain === 'number')
      out.push({ k: 'tension', v: 'filed vs meant', num: num(p.strain), tone: 'strain' })
  } else if (rf === 'separator') {
    const pole = p.pole === 'b' ? 'pole B' : p.pole === 'a' ? 'pole A' : 'balanced'
    out.push({ k: 'leans', v: pole, num: num(Math.abs(p.lean ?? 0)) })
  } else if (rf === 'nucleation') {
    if (p.inside) out.push({ k: 'fits', v: 'inside', num: num(p.fit) })
    else if (p.tail) out.push({ k: 'corner', v: 'fits no type, forms no new type → needs a new axis', num: num(p.fit), tone: 'pile' })
    else out.push({ k: 'misfit', v: p.born ? 'piled → a new type ✦' : 'fits no type · piled', tone: p.born ? 'born' : 'pile' })
  } else if (rf === 'address') {
    out.push({ k: 'distance', v: `structural from ${centre ?? 'centre'}`, num: num(p.r) })
  } else {
    const d = p.r ?? 0
    const w = d < 0.34 ? 'recent' : d < 0.67 ? 'a while ago' : 'long ago'
    out.push({ k: 'age', v: centre ? `from ${centre}` : w, num: num(p.r) })
  }
  return out
}

// Clean excerpt: never cut mid-word; end on a word boundary with an ellipsis (design-critic fix #1).
function excerpt(s: string, max = 150): string {
  const t = (s || '').replace(/\s+/g, ' ').trim()
  if (t.length <= max) return t
  const cut = t.slice(0, max)
  const sp = cut.lastIndexOf(' ')
  return cut.slice(0, sp > 50 ? sp : max).replace(/[\s,;:.\-—]+$/, '') + '…'
}

// One disclosure component, three hosts. The resting state shows NOTHING (text-minimal, L2/L6) —
// it only mounts when a point is selected; entrance/exit are motion mirrors (no teleport, L3).
export function Disclosure({
  point,
  feel,
  variant,
  onDismiss,
  onFocus,
  onSetPole,
  binding,
  centreLabel,
}: {
  point: ProjPoint | null
  feel: MotionFeel
  variant: Variant
  onDismiss: () => void
  onFocus?: (p: ProjPoint) => void
  onSetPole?: (which: 'a' | 'b', p: ProjPoint) => void
  binding?: Projection['binding']
  centreLabel?: string | null
}) {
  const [bundle, setBundle] = useState<ContextBundle | null>(null)
  const [ctxError, setCtxError] = useState<string | null>(null)
  const addr = point ? pointAddress(point) : null

  useEffect(() => {
    if (!addr) {
      setBundle(null)
      setCtxError(null)
      return
    }
    let live = true
    setBundle(null)
    setCtxError(null)
    contextAt(addr)
      .then((b) => live && setBundle(b))
      .catch((e: unknown) => live && setCtxError(String((e as Error).message || e)))
    return () => {
      live = false
    }
  }, [addr])

  const enter =
    variant === 'sheet'
      ? { initial: { y: 360, opacity: 0 }, animate: { y: 0, opacity: 1 }, exit: { y: 360, opacity: 0 } }
      : variant === 'rail'
        ? { initial: { x: 40, opacity: 0 }, animate: { x: 0, opacity: 1 }, exit: { x: 40, opacity: 0 } }
        : { initial: { opacity: 0, y: 10 }, animate: { opacity: 1, y: 0 }, exit: { opacity: 0, y: 10 } }

  const items = (bundle?.items || []).slice(0, 6)

  return (
    <AnimatePresence>
      {point && addr && (
        <motion.aside
          className={`disclosure disclosure--${variant}`}
          data-ui-ref={addr}
          {...enter}
          transition={transition('enter', feel)}
        >
          {variant === 'sheet' && <div className="sheet-handle" aria-hidden />}
          <header className="disc-head">
            <span className="disc-kind display">{point.kind || point.sector}</span>
            <button className="disc-close" onClick={onDismiss} aria-label="dismiss">×</button>
          </header>

          {point.summary && <p className="disc-summary">{excerpt(point.summary, 160)}</p>}

          {/* WHY IT'S HERE — its division + what its radius means in this lens (plain words + real value) */}
          <dl className="disc-place">
            {placement(point, binding, centreLabel ?? null).map((pl, i) => (
              <div className={`place-row ${pl.tone ? `place-row--${pl.tone}` : ''}`} key={i}>
                <dt className="place-k">{pl.k}</dt>
                <dd className="place-v">
                  {pl.v}
                  {pl.num && <span className="place-num">{pl.num}</span>}
                </dd>
              </div>
            ))}
          </dl>

          <div className="disc-context">
            {ctxError && <p className="notice-inline">context unavailable: {ctxError}</p>}
            {!ctxError && bundle && items.length === 0 && (
              <p className="disc-empty">no context attached yet</p>
            )}
            {items.map((it, k) => (
              <div className="ctx-item" key={k}>
                {it.kind && <span className="ctx-kind">{it.kind}</span>}
                <span className="ctx-text">{excerpt(it.text || it.summary || '', 150)}</span>
              </div>
            ))}
            {bundle?.more ? <p className="disc-empty">+{bundle.more} more beyond the cap</p> : null}
          </div>

          <footer className="disc-foot">
            {/* in the separator lens, any item can become one of the two gravities (G9 — poles are variables) */}
            {onSetPole && binding?.radius_from === 'separator' && (
              <div className="disc-poles">
                <button className="disc-pole" onClick={() => onSetPole('a', point)} title="make this the left gravity">⟸ pole A</button>
                <button className="disc-pole" onClick={() => onSetPole('b', point)} title="make this the right gravity">pole B ⟹</button>
              </div>
            )}
            {onFocus && (
              <button className="disc-focus" onClick={() => onFocus(point)} title="re-centre the space on this">
                ⊙ centre here
              </button>
            )}
            <code className="disc-addr">{addr}</code>
          </footer>
        </motion.aside>
      )}
    </AnimatePresence>
  )
}
