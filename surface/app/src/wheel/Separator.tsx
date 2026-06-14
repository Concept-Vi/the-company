import { motion, AnimatePresence } from 'framer-motion'
import type { Projection, ProjPoint } from '../lib/api'
import type { MotionFeel } from '../tokens/motion'
import { transition } from '../tokens/motion'
import { TAU } from '../lib/seed'
import { stamp } from '../lib/address'
import { useSize } from './useSize'
import { pointAddress } from './Wheel'

// GROUP 9 — the two-gravity separator FORM. Two BASINS: pole A pulls left, pole B pulls right; a point's
// horizontal distance from the centre line = how strongly it leans (r = |lean|, normalized). The fifth gate
// (separates / doesn't) is the calm headline; the diverging balance bar shows the skew. Real data only —
// poles + lean + the separation report all come from the engine (pure read, registry-true).

type Balance = { lean_a: number; lean_b: number; neutral: number; minority_frac: number }
type Separation = { separates?: boolean; balance?: Balance; pole_distinctness?: number }

function leaf(s: string | undefined): string {
  const t = (s || '').replace(/\/+$/, '')
  return t.split('/').pop() || t
}

export function Separator({
  proj,
  feel,
  selectedSeq,
  onPick,
  polesDriven,
  onClearPoles,
}: {
  proj: Projection
  feel: MotionFeel
  selectedSeq?: number
  onPick: (p: ProjPoint) => void
  polesDriven?: boolean
  onClearPoles?: () => void
}) {
  const { ref, width, height } = useSize<HTMLDivElement>()
  const ready = width > 8 && height > 8
  const cx = (width || 1) / 2
  const cy = (height || 1) / 2
  const halfW = cx * 0.9
  const halfH = cy * 0.86
  const sep = (proj.separation || {}) as Separation
  const bal = sep.balance
  const poleA = proj.binding.poles?.a as { label?: string } | undefined
  const poleB = proj.binding.poles?.b as { label?: string } | undefined

  // each point's basin coordinate
  const place = (p: ProjPoint) => {
    const sign = p.pole === 'b' ? 1 : p.pole === 'a' ? -1 : Math.sign(p.lean ?? 0) || 0
    const x = cx + sign * p.r * halfW
    const y = cy + ((p.theta ?? 0) / TAU - 0.5) * 2 * halfH
    return { x, y, sign }
  }

  // balance bar geometry
  const la = bal?.lean_a ?? 0
  const lb = bal?.lean_b ?? 0
  const tot = Math.max(la + lb, 1)
  const barW = Math.min(width * 0.5, 360)
  const leftW = (la / tot) * barW
  const rightW = (lb / tot) * barW
  const barY = height - 26

  return (
    <div ref={ref} className="wheel-region" {...stamp('ui://instrument/separator')}>
      {ready && (
        <svg viewBox={`0 0 ${width} ${height}`} className="wheel-svg" role="img" aria-label="two-gravity separator">
          {/* the centre balance line */}
          <line x1={cx} y1={cy - halfH} x2={cx} y2={cy + halfH} stroke="var(--hairline)" strokeWidth={1} />
          {/* the two basin centroids (faint anchors) */}
          <circle cx={cx - halfW} cy={cy} r={4} fill="var(--pig-leanA)" fillOpacity={0.5} />
          <circle cx={cx + halfW} cy={cy} r={4} fill="var(--pig-leanB)" fillOpacity={0.5} />

          {/* points — decorative animated layer (pole-coloured), pointer-events off */}
          <AnimatePresence>
            {proj.points.map((p) => {
              const { x, y } = place(p)
              const isSel = p.seq === selectedSeq
              const addr = pointAddress(p)
              const hue = p.pole === 'b' ? 'var(--pig-leanB)' : 'var(--pig-leanA)'
              return (
                <motion.circle
                  key={`pt-${p.seq}`}
                  {...stamp(addr)}
                  layoutId={`pt-${p.seq}`}
                  className="wheel-dot"
                  fill={hue}
                  fillOpacity={0.6}
                  stroke={isSel ? 'var(--ink-primary)' : 'transparent'}
                  strokeWidth={isSel ? 1.5 : 0}
                  style={{ pointerEvents: 'none' }}
                  initial={{ cx: x, cy: y, r: 0, opacity: 0 }}
                  animate={{ cx: x, cy: y, r: isSel ? 5.5 : 2.6, opacity: 1 }}
                  exit={{ r: 0, opacity: 0 }}
                  transition={transition('move', feel)}
                />
              )
            })}
          </AnimatePresence>

          {/* hit layer (touch-friendly) */}
          {proj.points.map((p) => {
            const { x, y } = place(p)
            const addr = pointAddress(p)
            return (
              <circle
                key={`hit-${p.seq}`}
                {...stamp(addr)}
                className="wheel-hit"
                cx={x}
                cy={y}
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

          {/* the diverging balance bar (the skew, seen) */}
          {bal && (
            <g>
              <rect x={cx - leftW} y={barY} width={leftW} height={8} rx={2} fill="var(--pig-leanA)" fillOpacity={0.55} />
              <rect x={cx} y={barY} width={rightW} height={8} rx={2} fill="var(--pig-leanB)" fillOpacity={0.55} />
            </g>
          )}
        </svg>
      )}

      {/* pole labels (real, small) + the fifth-gate verdict — text-minimal overlays. Operator-driven poles
         show as leaves; a reset returns to the binding's default gravities. */}
      <div className="sep-pole sep-pole--a">{polesDriven ? leaf(poleA?.label) : poleA?.label}</div>
      <div className="sep-pole sep-pole--b">{polesDriven ? leaf(poleB?.label) : poleB?.label}</div>
      {polesDriven && onClearPoles && (
        <button className="sep-reset" onClick={onClearPoles} title="back to the default two gravities">↺ default poles</button>
      )}
      {bal && (
        <div className="sep-counts">
          <span className="sep-count sep-count--a">{la}</span>
          <span className="sep-count sep-count--b">{lb}</span>
        </div>
      )}
      <div className={`sep-verdict ${sep.separates ? 'sep-verdict--yes' : 'sep-verdict--no'}`}>
        {sep.separates ? 'separates' : 'does not separate'}
      </div>
    </div>
  )
}
