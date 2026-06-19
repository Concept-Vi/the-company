import { useLayoutEffect, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import type { MotionFeel } from '../tokens/motion'
import { transition } from '../tokens/motion'
import { Taste } from './Taste'
import { stamp } from '../lib/address'

// A single calm affordance (a gear) that holds the taste scaffold ON DEMAND — so the resting surface stays
// near-textless (L2/L6) while Tim can still flip typeface/pigment/motion by tapping. (Design-critic fix #2:
// the toggles must not sit permanently on the product surface.)
export function Settings({ feel, setFeel }: { feel: MotionFeel; setFeel: (f: MotionFeel) => void }) {
  const [open, setOpen] = useState(false)
  const gearRef = useRef<HTMLButtonElement>(null)
  // The panel is VIEWPORT-anchored (position: fixed, hugging the right edge + max-width capped to the viewport),
  // NOT anchored to the gear's right edge — because the gear sits mid-header on a phone, so a gear-right-anchored
  // panel overflowed the LEFT viewport edge (the first taste column clipped off-screen at 390 — fresh-eyes catch).
  // We only MEASURE the gear to drop the panel just below it (top); right/width come from the viewport so it can
  // never clip at any width. Measured (not a hand-written breakpoint) — resolver-spirit: compute from the device.
  const [top, setTop] = useState<number | null>(null)
  useLayoutEffect(() => {
    if (!open) return
    const g = gearRef.current
    if (g) setTop(g.getBoundingClientRect().bottom)
  }, [open])
  return (
    <div className="settings" {...stamp('ui://controls/settings')}>
      <button
        ref={gearRef}
        className="settings-gear"
        {...stamp('ui://controls/settings/open')}
        onClick={() => setOpen((o) => !o)}
        aria-label="taste"
        aria-expanded={open}
      >
        ⚙
      </button>
      <AnimatePresence>
        {open && (
          <>
            <div className="lenschip-scrim" onClick={() => setOpen(false)} />
            <motion.div
              className="settings-panel"
              style={top != null ? { top } : undefined}
              initial={{ opacity: 0, y: -6, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -6, scale: 0.98 }}
              transition={transition('enter')}
            >
              <span className="settings-title">taste</span>
              <Taste feel={feel} setFeel={setFeel} />
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}
