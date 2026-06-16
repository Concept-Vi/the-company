import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { fetchLayers, type Projection } from '../lib/api'
import { transition } from '../tokens/motion'
import { stamp } from '../lib/address'
import { useChipMenu } from './useChipMenu'

// THE SPACE picker — WHICH item-store the lens ranges over (repo · history · principles · worldview · topics ·
// operators · common_knowledge · …). The Instrument is the UNIVERSAL projection: it must be able to point at ANY
// embedded space, not just each binding's default. The backend already accepts `space` (bridge.build_projection:
// space = q.space or binding.space) — this chip is the missing operator control for that axis (the one drivable
// axis that lacked a chip). REGISTRY-TRUE: the space list is read from /api/layers (the engine's self-description
// of every embedded space) — never hardcoded, so a newly-embedded space (e.g. common_knowledge the moment
// recollection publishes it) becomes a menu row with ZERO surface edit (loadable, no single use, nothing static).
// space=null means "follow the binding's default"; picking a space OVERRIDES it. Hidden for by_nucleation (which
// drives its space through the richer nuc pickers, not this single axis).
export function SpaceChip({ proj, space, setSpace }: { proj: Projection | null; space: string | null; setSpace: (s: string | null) => void }) {
  const { open, toggle, close, wrapRef, menuClass } = useChipMenu()
  const [spaces, setSpaces] = useState<string[]>([])
  useEffect(() => {
    let alive = true
    fetchLayers()
      .then((m) => {
        if (!alive) return
        setSpaces(Object.keys(m).sort()) // the embedded spaces — every space the multi-layer model carries
      })
      .catch(() => {}) // a missing layers endpoint just hides the chip — never breaks the surface
    return () => {
      alive = false
    }
  }, [])
  if (proj?.binding?.id === 'by_nucleation') return null // nucleation drives its space via the nuc pickers
  // REGISTRY-TRUE visibility: only show when the active lens actually RANGES OVER a space (it self-reports
  // `binding.space`). raw / time-of-day / grouped are activity/registry lenses with no corpus space — the
  // backend ignores `space` for them (binding.space=null), so showing the chip there would be a misleading
  // claim. The binding's own self-report drives the chip's existence — never a hardcoded which-lenses list.
  const bindingSpace = proj?.binding?.space
  if (!bindingSpace) return null
  if (spaces.length <= 1) return null // no space choice to make — stay invisible (text-minimal)
  // resting = the effective space: an explicit override, else the binding's actual default (what you're looking at)
  const current = space || bindingSpace
  return (
    <div className="lenschip spacechip" ref={wrapRef} {...stamp('ui://controls/space')}>
      <button
        className="lenschip-btn"
        {...stamp('ui://controls/space/current')}
        onClick={toggle}
        aria-expanded={open}
        title="the space — which embedded item-store the lens ranges over"
      >
        <span className="lenschip-label display">⬡ {current}</span>
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
              {spaces.map((sp) => (
                <li key={sp}>
                  <button
                    {...stamp(`ui://controls/space/${encodeURIComponent(sp)}`)}
                    className={`lenschip-item ${current === sp ? 'lenschip-item--on' : ''}`}
                    onClick={() => {
                      setSpace(sp)
                      close()
                    }}
                  >
                    {sp}
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
