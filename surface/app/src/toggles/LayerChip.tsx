import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { fetchLayers } from '../lib/api'
import { transition } from '../tokens/motion'
import { stamp } from '../lib/address'
import { useChipMenu } from './useChipMenu'

// THE EMBEDDER-LAYER picker (Tim's multi-layer model, 2026-06-15: "multiple embeddings over the same data").
// Every lens is layer-aware; this chooses WHICH embedding you look through. REGISTRY-TRUE: it reads
// /api/layers (the engine's self-description of which embedder layers each space carries) — never a hardcoded
// layer set, so a new embedder layer becomes a menu row with ZERO surface edit (loadable, no single use).
// 'default' = the base (BGE) layer (emb=null); a named layer (e.g. 'pplx') reads that embedder.
// Deceptively simple: resting = the current layer; the options live in the menu, on demand. Hidden when there
// is only one layer (no choice to make).
const DEFAULT = 'default'

export function LayerChip({ emb, setEmb }: { emb: string | null; setEmb: (e: string | null) => void }) {
  const { open, toggle, close, wrapRef, menuClass } = useChipMenu()
  const [layers, setLayers] = useState<string[]>([])
  useEffect(() => {
    let alive = true
    fetchLayers()
      .then((m) => {
        if (!alive) return
        const u = new Set<string>()
        for (const ls of Object.values(m)) for (const l of ls) u.add(l)
        setLayers([...u].sort()) // the union across spaces — the embedder choices (e.g. default · pplx)
      })
      .catch(() => {}) // a missing layers endpoint just hides the chip — never breaks the surface
    return () => {
      alive = false
    }
  }, [])
  if (layers.length <= 1) return null // no layer choice to make — stay invisible (text-minimal)
  const current = emb || DEFAULT
  return (
    <div className="lenschip layerchip" ref={wrapRef} {...stamp('ui://controls/layer')}>
      <button
        className="lenschip-btn"
        {...stamp('ui://controls/layer/current')}
        onClick={toggle}
        aria-expanded={open}
        title="the embedder layer — which embedding you look through"
      >
        <span className="lenschip-label display">◫ {current}</span>
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
              {layers.map((l) => (
                <li key={l}>
                  <button
                    {...stamp(`ui://controls/layer/${encodeURIComponent(l)}`)}
                    className={`lenschip-item ${current === l ? 'lenschip-item--on' : ''}`}
                    onClick={() => {
                      setEmb(l === DEFAULT ? null : l)
                      close()
                    }}
                  >
                    {l}
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
