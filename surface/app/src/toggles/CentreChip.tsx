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
          // plain-words affordance (a stranger re-aim test: "I changed the view and can't tell how to get back —
          // only a tiny ×"). The WHOLE chip resets; say so in human terms (tooltip + the visible "show all" tag),
          // and prefix "Centred on" so it reads as a STATE you're in, not just a label.
          title={`Centred on ${centre.label} — tap to show everything again`}
          aria-label={`Centred on ${centre.label}. Tap to show everything again.`}
        >
          <span className="centrechip-glyph" aria-hidden>⊙</span>
          <span className="centrechip-pre">Centred on</span>
          <span className="centrechip-label">{centre.label}</span>
          <span className="centrechip-x">show all ×</span>
        </motion.button>
      )}
    </AnimatePresence>
  )
}
