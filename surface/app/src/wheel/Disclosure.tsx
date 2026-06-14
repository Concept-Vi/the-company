import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import type { ProjPoint, ContextBundle } from '../lib/api'
import type { MotionFeel } from '../tokens/motion'
import { transition } from '../tokens/motion'
import { contextAt } from '../lib/address'
import { pointAddress } from './Wheel'

type Variant = 'panel' | 'sheet' | 'rail'

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
}: {
  point: ProjPoint | null
  feel: MotionFeel
  variant: Variant
  onDismiss: () => void
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

          {/* a few visual facts, not a text wall: which sector, fit/lean/strain when present */}
          <div className="disc-chips">
            <span className="chip">{point.sector}</span>
            {point.born && <span className="chip chip--born">born</span>}
            {typeof point.lean === 'number' && (
              <span className="chip">{point.pole === 'b' ? 'lean B' : point.pole === 'a' ? 'lean A' : 'balanced'}</span>
            )}
            {typeof point.strain === 'number' && <span className="chip chip--strain">strain</span>}
          </div>

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
            <code className="disc-addr">{addr}</code>
          </footer>
        </motion.aside>
      )}
    </AnimatePresence>
  )
}
