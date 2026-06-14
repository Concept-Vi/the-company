import { useState } from 'react'
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
  return (
    <div className="settings" {...stamp('ui://controls/settings')}>
      <button
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
