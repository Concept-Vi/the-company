import { AnimatePresence, motion } from 'framer-motion'
import type { Projection } from '../lib/api'
import { transition } from '../tokens/motion'
import { stamp } from '../lib/address'
import { useChipMenu } from './useChipMenu'

// THE REPRESENTATION picker — binary quantization (Tim's "the maths, parametric, no single use"). 'binary' maps
// each read dim to its sign (±1); fed through the SAME cosine that becomes a Hamming similarity
// (cos(sign a, sign b) = 1 − 2·Hamming/d) — a coarse, 32×-compact view of meaning, orthogonal to the layer
// (◫ emb) and resolution (◎ dim) axes and composable with both. Compute-on-read (pure; no stored variant),
// registry-true. Only meaningful on the vector lenses (a `space` in the binding) — hidden on structural ones.
// Verified faithful: NN@10 binary-vs-full 0.81 (pplx 2560d) / 0.70 (BGE 1024d). 'full' = the float cosine.
const OPTS = [
  { id: 'full', label: 'full · float' },
  { id: 'binary', label: 'binary · Hamming' },
]

export function QuantChip({ proj, quant, setQuant }:
  { proj: Projection | null; quant: string | null; setQuant: (q: string | null) => void }) {
  const { open, toggle, close, wrapRef, menuClass } = useChipMenu()
  if (!proj?.binding?.space) return null // no vector lens → no representation choice to make (stay invisible)
  const current = quant === 'binary' ? 'binary' : 'full'
  return (
    <div className="lenschip quantchip" ref={wrapRef} {...stamp('ui://controls/representation')}>
      <button
        className="lenschip-btn"
        {...stamp('ui://controls/representation/current')}
        onClick={toggle}
        aria-expanded={open}
        title="the representation — full float (cosine) or binary sign-bits (Hamming, a coarse 32×-compact view)"
      >
        <span className="lenschip-label display">▦ {current}</span>
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
              {OPTS.map((o) => (
                <li key={o.id}>
                  <button
                    {...stamp(`ui://controls/representation/${o.id}`)}
                    className={`lenschip-item ${current === o.id ? 'lenschip-item--on' : ''}`}
                    onClick={() => {
                      setQuant(o.id === 'binary' ? 'binary' : null)
                      close()
                    }}
                  >
                    {o.label}
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
