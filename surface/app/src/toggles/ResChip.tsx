import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { fetchLayerDims, type Projection } from '../lib/api'
import { transition } from '../tokens/motion'
import { stamp } from '../lib/address'

// THE RESOLUTION picker — the MRL meaning-zoom (Tim's "uses the maths, parametric, nothing static"). ?dim=<N>
// truncates every read vector to its first N dims before the cosine: a continuous coarse↔fine MEANING zoom,
// ORTHOGONAL to the scale rung (the 2-D scale — rung × dim). REGISTRY-TRUE: the ladder is DERIVED from the
// active layer's full vector dim (/api/layer-dims) — powers of two below it — never a hardcoded dim set; a new
// embedder layer with a different dim just yields a different ladder, ZERO surface edit. Only meaningful on the
// vector lenses (a `space` in the binding); hidden on the structural lenses (raw/connections/day-cycle) and
// whenever there's no finer step to pick (deceptively simple — appears only where it does something).
const FULL = 'full'

export function ResChip({ proj, dim, setDim, emb }:
  { proj: Projection | null; dim: number | null; setDim: (d: number | null) => void; emb: string | null }) {
  const [open, setOpen] = useState(false)
  const [dims, setDims] = useState<Record<string, Record<string, number>>>({})
  useEffect(() => {
    let alive = true
    fetchLayerDims()
      .then((m) => { if (alive) setDims(m) })
      .catch(() => {}) // a missing endpoint just hides the chip — never breaks the surface
    return () => { alive = false }
  }, [])
  const space = proj?.binding?.space
  const full = space ? dims[space]?.[emb || 'default'] : undefined
  // the MRL ladder: powers of two STRICTLY below the full dim, down to 64 — the maths, clamped to the layer.
  const ladder: number[] = []
  if (full) for (let n = 2048; n >= 64; n = n / 2) if (n < full) ladder.push(n)
  const options = [FULL, ...ladder.map(String)]
  if (!full || options.length <= 1) return null // no vector lens / no finer step → stay invisible
  const current = dim ? String(dim) : FULL
  return (
    <div className="lenschip reschip" {...stamp('ui://controls/resolution')}>
      <button
        className="lenschip-btn"
        {...stamp('ui://controls/resolution/current')}
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        title="the resolution — how many vector dims the meaning is read at (the MRL zoom)"
      >
        <span className="lenschip-label display">◎ {current === FULL ? 'full' : `${current}d`}</span>
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
              {options.map((o) => (
                <li key={o}>
                  <button
                    {...stamp(`ui://controls/resolution/${o}`)}
                    className={`lenschip-item ${current === o ? 'lenschip-item--on' : ''}`}
                    onClick={() => {
                      setDim(o === FULL ? null : Number(o))
                      setOpen(false)
                    }}
                  >
                    {o === FULL ? `full · ${full}d` : `${o}d`}
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
