import { AnimatePresence, motion } from 'framer-motion'
import type { Projection } from '../lib/api'
import { transition } from '../tokens/motion'
import { stamp } from '../lib/address'
import { useChipMenu } from './useChipMenu'

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
  const { open, toggle, close, wrapRef, menuClass } = useChipMenu()
  return (
    <div className="lenschip" ref={wrapRef} {...stamp('ui://controls/lens')}>
      <button
        className="lenschip-btn"
        {...stamp('ui://controls/lens/current')}
        onClick={toggle}
        aria-expanded={open}
      >
        <span className="lenschip-label display">{shortLabel(proj.binding.label)}</span>
        {/* the live count of things on the map — give the bare number HUMAN meaning (operator-law: a raw "600" reads
            as a mystery to a stranger, fresh-eyes flag). title+aria-label so it's explicable on hover + to a screen
            reader; whether the VISIBLE number wants a unit suffix is DNA's chip-aesthetic call (flagged). */}
        <span className="lenschip-count" title={`${proj.count} things on the map`} aria-label={`${proj.count} things on the map`}>{proj.count}</span>
        <span className="lenschip-caret" aria-hidden>{open ? '▾' : '▸'}</span>
      </button>
      <AnimatePresence>
        {open && (
          <>
            <div className="lenschip-scrim" onClick={close} />
            <motion.ul
              className={`lenschip-menu ${menuClass}`}
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
                      close()
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
