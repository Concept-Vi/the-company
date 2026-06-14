import { motion, AnimatePresence } from 'framer-motion'
import type { Projection, ProjPoint } from '../lib/api'
import type { MotionFeel } from '../tokens/motion'
import { transition } from '../tokens/motion'
import { gridCellCenter, dyadicLevels, sectorHue } from '../lib/seed'
import { stamp } from '../lib/address'
import { useSize } from './useSize'
import { pointAddress } from './Wheel'

// THE SQUARE / STRUCTURE HALF of the seed (§1–3): the dyadic nested grid + the two axes + the concentric
// circles, over one box centred on the origin. A point sits at its ADDRESS's dyadic cell (i,j at its own
// depth d) — structure, not meaning. The axes are the coincidence spine (where square ∧ circle agree =
// the ratified/addressable); the corner circle (r=√2·R, bulging outside the box) is the FORBIDDEN zone.
// Same data, the other coordinate system — the dual the equation demands.

export function Grid({
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
  const cx = (width || 1) / 2
  const cy = (height || 1) / 2
  const R = Math.min(width || 1, height || 1) * 0.33 // leaves room for the forbidden corner-circle (√2·R)
  const m = Math.max(proj.grid, 1)
  const rings = Math.max(proj.rings, 1)
  const sectorIndex = new Map(proj.sectors.map((s, i) => [s.id, i]))
  const n = Math.max(proj.n, 1)
  const SQRT2 = Math.SQRT2

  const levels = dyadicLevels(m)
  const ringR = (k: number) => (k / rings) * R

  // a point's screen position from its dyadic cell, CLAMPED inside the box: data lives inside the
  // addressable structure; the margin/corners stay empty = the forbidden zone (legible per the equation).
  const place = (p: ProjPoint) => {
    const md = 1 << (p.cell?.d || 0)
    const pos = gridCellCenter(p.cell?.i ?? 0, p.cell?.j ?? 0, md, cx, cy, R, p.seq)
    const pad = 4
    return {
      x: Math.max(cx - R + pad, Math.min(cx + R - pad, pos.x)),
      y: Math.max(cy - R + pad, Math.min(cy + R - pad, pos.y)),
    }
  }

  return (
    <div ref={ref} className="wheel-region" {...stamp('ui://instrument/grid')}>
      {ready && (
        <svg viewBox={`0 0 ${width} ${height}`} className="wheel-svg" role="img" aria-label="structure grid">
          {/* the FORBIDDEN corner-circle (circumscribed, through the corners, bulging outside the box) —
             load-bearing geometry, so it reads as a deliberate boundary, not background noise */}
          <circle cx={cx} cy={cy} r={R * SQRT2} fill="none" stroke="var(--pig-strain)"
            strokeOpacity={0.42} strokeWidth={1.2} strokeDasharray="4 5" />

          {/* the dyadic nested grid lines (coarsest strongest → finest faintest; parent contains children) */}
          {levels.map(({ divisions, weight }) =>
            Array.from({ length: divisions - 1 }, (_, k) => {
              const t = (k + 1) / divisions
              const x = cx - R + t * 2 * R
              const y = cy - R + t * 2 * R
              return (
                <g key={`lvl-${divisions}-${k}`}>
                  <line x1={x} y1={cy - R} x2={x} y2={cy + R} stroke="var(--ink-faint)" strokeOpacity={weight} strokeWidth={1} />
                  <line x1={cx - R} y1={y} x2={cx + R} y2={y} stroke="var(--ink-faint)" strokeOpacity={weight} strokeWidth={1} />
                </g>
              )
            }),
          )}

          {/* the box (square outline) */}
          <rect x={cx - R} y={cy - R} width={2 * R} height={2 * R} fill="none" stroke="var(--hairline)" strokeWidth={1} />

          {/* the m/2 concentric inscribed circles (the circle half, shown alongside so the dual is visible) */}
          {Array.from({ length: rings }, (_, k) => (
            <circle key={`c-${k}`} cx={cx} cy={cy} r={ringR(k + 1)} fill="none"
              stroke="var(--hairline)" strokeWidth={1} />
          ))}

          {/* the two axes through the centre — the coincidence spine (emphasised) */}
          <line x1={cx} y1={cy - R} x2={cx} y2={cy + R} stroke="var(--ink-faint)" strokeOpacity={0.55} strokeWidth={1} />
          <line x1={cx - R} y1={cy} x2={cx + R} y2={cy} stroke="var(--ink-faint)" strokeOpacity={0.55} strokeWidth={1} />

          {/* coincidence points: where the axes meet each circle (square ∧ circle agree = ratified spine) */}
          {Array.from({ length: rings }, (_, k) => {
            const r = ringR(k + 1)
            return (
              <g key={`coin-${k}`}>
                <circle cx={cx - r} cy={cy} r={1.6} fill="var(--ink-faint)" />
                <circle cx={cx + r} cy={cy} r={1.6} fill="var(--ink-faint)" />
                <circle cx={cx} cy={cy - r} r={1.6} fill="var(--ink-faint)" />
                <circle cx={cx} cy={cy + r} r={1.6} fill="var(--ink-faint)" />
              </g>
            )
          })}

          {/* the centre — the origin */}
          <circle cx={cx} cy={cy} r={3} fill="var(--ink-dim)" />

          {/* points at their dyadic cells — decorative animated layer (pointer-events off) */}
          <AnimatePresence>
            {proj.points.map((p) => {
              const pos = place(p)
              const i = sectorIndex.get(p.sector) ?? 0
              const isSel = p.seq === selectedSeq
              const addr = pointAddress(p)
              return (
                <motion.circle
                  key={`pt-${p.seq}`}
                  {...stamp(addr)}
                  layoutId={`pt-${p.seq}`}
                  className="wheel-dot"
                  fill={sectorHue(i, n)}
                  fillOpacity={0.52}
                  stroke={isSel ? 'var(--ink-primary)' : 'transparent'}
                  strokeWidth={isSel ? 1.5 : 0}
                  style={{ pointerEvents: 'none' }}
                  initial={{ cx: pos.x, cy: pos.y, r: 0, opacity: 0 }}
                  animate={{ cx: pos.x, cy: pos.y, r: isSel ? 5.5 : 2.4, opacity: 1 }}
                  exit={{ r: 0, opacity: 0 }}
                  transition={transition('move', feel)}
                />
              )
            })}
          </AnimatePresence>

          {/* HIT layer — touch-friendly */}
          {proj.points.map((p) => {
            const pos = place(p)
            const addr = pointAddress(p)
            return (
              <circle
                key={`hit-${p.seq}`}
                {...stamp(addr)}
                className="wheel-hit"
                cx={pos.x}
                cy={pos.y}
                r={15}
                fill="transparent"
                style={{ pointerEvents: 'all', cursor: 'pointer' }}
                onClick={(e) => {
                  e.stopPropagation()
                  onPick(p)
                }}
              />
            )
          })}
        </svg>
      )}
    </div>
  )
}
