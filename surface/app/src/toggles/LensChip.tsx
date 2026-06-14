import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import type { Projection } from '../lib/api'
import { transition } from '../tokens/motion'
import { stamp } from '../lib/address'

// The lens + glance, MERGED into ONE chip (text-minimal, L2/L6). Resting = a short name (derived from the
// registry label, never hardcoded) + the live count. The full lens labels live in the menu, on demand.
// A new binding file => a new menu row with zero edit (registry-true, L12).
function shortLabel(label: string): string {
  const head = label.split(/[—–-]/)[0].trim()
  return head || label
}

export function LensChip({
  proj,
  current,
  onPick,
}: {
  proj: Projection
  current: string
  onPick: (id: string) => void
}) {
  const [open, setOpen] = useState(false)
  return (
    <div className="lenschip" {...stamp('ui://controls/lens')}>
      <button
        className="lenschip-btn"
        {...stamp('ui://controls/lens/current')}
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
      >
        <span className="lenschip-label display">{shortLabel(proj.binding.label)}</span>
        <span className="lenschip-count">{proj.count}</span>
        <span className="lenschip-caret" aria-hidden>{open ? '▾' : '▸'}</span>
      </button>
      <AnimatePresence>
        {open && (
          <>
            <div className="lenschip-scrim" onClick={() => setOpen(false)} />
            <motion.ul
              className="lenschip-menu"
              initial={{ opacity: 0, y: -6, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -6, scale: 0.98 }}
              transition={transition('enter')}
            >
              {proj.bindings.map((b) => (
                <li key={b.id}>
                  <button
                    {...stamp(`ui://controls/lens/${encodeURIComponent(b.id)}`)}
                    className={`lenschip-item ${current === b.id ? 'lenschip-item--on' : ''}`}
                    onClick={() => {
                      onPick(b.id)
                      setOpen(false)
                    }}
                  >
                    {b.label}
                  </button>
                </li>
              ))}
            </motion.ul>
          </>
        )}
      </AnimatePresence>
    </div>
  )
}
