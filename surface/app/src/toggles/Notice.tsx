import { AnimatePresence, motion } from 'framer-motion'
import { transition } from '../tokens/motion'

// Fail-loud, calmly: address/data errors surface here (never a silent swallow), animated in/out.
export function Notice({ message, onDismiss }: { message: string | null; onDismiss: () => void }) {
  return (
    <AnimatePresence>
      {message && (
        <motion.div
          className="notice"
          role="status"
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -12 }}
          transition={transition('enter')}
        >
          <span>{message}</span>
          <button className="notice-x" onClick={onDismiss} aria-label="dismiss">×</button>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
