import { motion, AnimatePresence } from 'framer-motion'
import type { Projection, ProjPoint } from '../lib/api'
import type { MotionFeel } from '../tokens/motion'
import { transition } from '../tokens/motion'
import { wheelGeom, placePolar, ringRadii, sectorHue, wedgePath, chordPath, arrowHead, sectorMidAngle } from '../lib/seed'
import { stamp } from '../lib/address'
import { useSize } from './useSize'

// The canonical address for a point: its real address, else a minted dynamic canvas address (never fabricated
// as a real ui:// region — ui://canvas/<id> is the sanctioned mint-on-read scheme, RESEARCH-SYNTHESIS §A).
export function pointAddress(p: ProjPoint): string {
  return p.address && p.address.startsWith('ui://') ? p.address : `ui://canvas/seq-${p.seq}`
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

          {/* sector wedges — soft angle-hue fill + hairline edges (colour IS geometry). A single sector
             (n≤1, e.g. one semantic space) has NO meaningful angular division — skip the degenerate
             full-circle wedge and show clean rings + points instead. */}
          {n > 1 &&
            proj.sectors.map((s, i) => (
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

          {/* THE CONNECTIONS (Group 10) — the REAL directional typed edges as directed chords. Registry-true
             (the engine supplies edges as sector indices). Source dot at `from`, arrowhead at `to`; a bidir
             edge (a genuine cycle) gets arrowheads at BOTH ends — cycles rendered AS cycles. Calm/paper opacity. */}
          {proj.edges.length > 0 &&
            proj.edges.map((e) => {
              const sf = proj.sectors[e.from]
              const st = proj.sectors[e.to]
              if (!sf || !st) return null
              const ch = chordPath(sectorMidAngle(sf.from, sf.to), sectorMidAngle(st.from, st.to), cx, cy, R * 0.84)
              return (
                <motion.g
                  key={`edge-${e.from}-${e.to}`}
                  {...stamp(`ui://instrument/edge/${e.from}-${e.to}`)}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={transition('enter', feel)}
                >
                  <path d={ch.d} fill="none" stroke="var(--ink-dim)"
                    strokeOpacity={e.bidir ? 0.32 : 0.2} strokeWidth={e.bidir ? 1.4 : 1} />
                  <circle cx={ch.from.x} cy={ch.from.y} r={2} fill="var(--ink-dim)" fillOpacity={0.5} />
                  <path d={arrowHead(ch.to, ch.ctrl)} fill="var(--ink-dim)" fillOpacity={0.55} />
                  {e.bidir && <path d={arrowHead(ch.from, ch.ctrl)} fill="var(--ink-dim)" fillOpacity={0.55} />}
                </motion.g>
              )
            })}

          {/* STRAIN (Group 7, the seed §3) — the radial tension between where a point is FILED (its
             structural/repo-tree radius r_struct) and where it MEANS to be (its semantic radius r), drawn at
             the point's angle. Present only in the semantic lens WITH a centre. Longer + stronger = more
             divergence between structure and meaning = the forbidden tension. The open tick marks the filed
             position; the dot (below) sits at the meaning position. Animates with the re-projection (no teleport). */}
          {proj.points.map((p) => {
            if (p.strain == null || p.r_struct == null) return null
            const a = placePolar(p.theta, p.r_struct, cx, cy, R) // filed
            const b = placePolar(p.theta, p.r, cx, cy, R) // means
            // cap softer so the longest (highest-strain) segments don't read as axis spokes near the hub
            const op = Math.min(0.14 + p.strain * 0.7, 0.52)
            return (
              <g key={`strain-${p.seq}`} {...stamp(pointAddress(p))}>
                <motion.line
                  initial={{ x1: a.x, y1: a.y, x2: b.x, y2: b.y, opacity: 0 }}
                  animate={{ x1: a.x, y1: a.y, x2: b.x, y2: b.y, opacity: 1 }}
                  transition={transition('move', feel)}
                  stroke="var(--pig-strain)"
                  strokeOpacity={op}
                  strokeWidth={1}
                />
                <motion.circle
                  initial={{ cx: a.x, cy: a.y }}
                  animate={{ cx: a.x, cy: a.y }}
                  transition={transition('move', feel)}
                  r={1.6}
                  fill="none"
                  stroke="var(--pig-strain)"
                  strokeOpacity={op * 0.8}
                  strokeWidth={1}
                />
              </g>
            )
          })}

          {/* the centre — a small soft mark (the origin / "now") */}
          <circle cx={cx} cy={cy} r={3.5} fill="var(--ink-faint)" />

          {/* the point cloud — DECORATIVE layer: real data placed by (theta, r); each addressed + animated.
             Entrance r:0->baseR, lens-change tweens cx/cy/r, exit r->0 (no teleport). pointer-events off —
             the hit layer below owns clicks (so tiny dots are still tappable on touch). */}
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
                  className="wheel-dot"
                  fill={sectorHue(i, n)}
                  fillOpacity={p.r_unknown ? 0.32 : 0.58}
                  stroke={isSel ? 'var(--ink-primary)' : 'transparent'}
                  strokeWidth={isSel ? 1.5 : 0}
                  style={{ pointerEvents: 'none' }}
                  initial={{ cx: pos.x, cy: pos.y, r: 0, opacity: 0 }}
                  animate={{ cx: pos.x, cy: pos.y, r: isSel ? 5.5 : baseR, opacity: 1 }}
                  exit={{ r: 0, opacity: 0 }}
                  transition={transition('move', feel)}
                />
              )
            })}
          </AnimatePresence>

          {/* HIT layer — invisible, touch-friendly (r=15 ≈ generous tap target vs the 2.4px dot). Carries the
             address so the capture listener indicates the right point; sits on top so it owns the click. */}
          {proj.points.map((p) => {
            const pos = placePolar(p.theta, p.r, cx, cy, R)
            const addr = pointAddress(p)
            return (
              <circle
                key={`hit-${addr}`}
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
