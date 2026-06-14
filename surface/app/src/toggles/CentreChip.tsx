import { AnimatePresence, motion } from 'framer-motion'
import type { Centre } from '../App'
import { transition } from '../tokens/motion'
import { stamp } from '../lib/address'

// Shows the active relative centre (the seed §8) — what the space is currently projected around — and lets
// the operator return to the root origin. Absent when centred on root (null). Calm, text-minimal.
export function CentreChip({ centre, onReset }: { centre: Centre | null; onReset: () => void }) {
  return (
    <AnimatePresence>
      {centre && (
        <motion.button
          className="centrechip"
          {...stamp('ui://controls/centre')}
          onClick={onReset}
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -4 }}
          transition={transition('enter')}
          title="return to the root origin"
        >
          <span className="centrechip-glyph" aria-hidden>⊙</span>
          <span className="centrechip-label">{centre.label}</span>
          <span className="centrechip-x" aria-hidden>×</span>
        </motion.button>
      )}
    </AnimatePresence>
  )
}
