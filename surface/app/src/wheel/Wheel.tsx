import { useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import type { Projection, ProjPoint } from '../lib/api'
import type { MotionFeel } from '../tokens/motion'
import { transition } from '../tokens/motion'
import { wheelGeom, placePolar, ringRadii, sectorHue, wedgePath } from '../lib/seed'
import { stamp } from '../lib/address'

// The canonical address for a point: its real address, else a minted dynamic canvas address (never fabricated
// as a real ui:// region — ui://canvas/<id> is the sanctioned mint-on-read scheme, RESEARCH-SYNTHESIS §A).
export function pointAddress(p: ProjPoint): string {
  return p.address && p.address.startsWith('ui://') ? p.address : `ui://canvas/seq-${p.seq}`
}

function useSize<T extends HTMLElement>() {
  const ref = useRef<T | null>(null)
  const [size, setSize] = useState({ width: 0, height: 0 })
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const ro = new ResizeObserver((entries) => {
      const r = entries[0].contentRect
      setSize({ width: r.width, height: r.height })
    })
    ro.observe(el)
    setSize({ width: el.clientWidth, height: el.clientHeight })
    return () => ro.disconnect()
  }, [])
  return { ref, ...size }
}

export function Wheel({
  proj,
  feel,
  selectedSeq,
  onPick,
}: {
  proj: Projection
  feel: MotionFeel
  selectedSeq?: number
  onPick: (p: ProjPoint) => void
}) {
  const { ref, width, height } = useSize<HTMLDivElement>()
  const ready = width > 8 && height > 8
  const { cx, cy, R } = wheelGeom(width || 1, height || 1)
  const sectorIndex = new Map(proj.sectors.map((s, i) => [s.id, i]))
  const n = Math.max(proj.n, 1)

  return (
    <div ref={ref} className="wheel-region" {...stamp('ui://instrument/wheel')}>
      {ready && (
        <svg viewBox={`0 0 ${width} ${height}`} className="wheel-svg" role="img" aria-label="instrument">
          {/* concentric rings — the m/2 rings (seed §1), hairline */}
          {ringRadii(proj.rings, R).map((rad, k) => (
            <circle key={`ring-${k}`} cx={cx} cy={cy} r={rad}
              fill="none" stroke="var(--hairline)" strokeWidth={1} />
          ))}

          {/* sector wedges — soft angle-hue fill + hairline edges (colour IS geometry) */}
          {proj.sectors.map((s, i) => (
            <path
              key={`sec-${s.id}-${i}`}
              {...stamp(`ui://instrument/sector/${encodeURIComponent(s.id)}`)}
              d={wedgePath(s.from, s.to, cx, cy, R)}
              fill={sectorHue(i, n)}
              fillOpacity={0.13}
              stroke="var(--hairline)"
              strokeWidth={1}
            />
          ))}

          {/* the centre — a small soft mark (the origin / "now") */}
          <circle cx={cx} cy={cy} r={3.5} fill="var(--ink-faint)" />

          {/* the point cloud — real data placed by (theta, r); each addressed + animated (no teleport) */}
          <AnimatePresence>
            {proj.points.map((p) => {
              const pos = placePolar(p.theta, p.r, cx, cy, R)
              const i = sectorIndex.get(p.sector) ?? 0
              const isSel = p.seq === selectedSeq
              const addr = pointAddress(p)
              const baseR = p.r > 1 ? 2.0 : 2.4 // piled-out points slightly smaller
              return (
                <motion.circle
                  key={addr}
                  {...stamp(addr)}
                  layoutId={addr}
                  fill={sectorHue(i, n)}
                  fillOpacity={p.r_unknown ? 0.32 : 0.58}
                  stroke={isSel ? 'var(--ink-primary)' : 'transparent'}
                  strokeWidth={isSel ? 1.5 : 0}
                  style={{ cursor: 'pointer' }}
                  initial={{ cx: pos.x, cy: pos.y, r: 0, opacity: 0 }}
                  animate={{ cx: pos.x, cy: pos.y, r: isSel ? 5.5 : baseR, opacity: 1 }}
                  exit={{ r: 0, opacity: 0 }}
                  transition={transition('move', feel)}
                  onClick={(e) => {
                    e.stopPropagation() // the capture listener already indicated; we own the disclosure
                    onPick(p)
                  }}
                />
              )
            })}
          </AnimatePresence>
        </svg>
      )}
    </div>
  )
}
