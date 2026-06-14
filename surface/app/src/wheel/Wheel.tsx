import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import type { Projection, ProjPoint } from '../lib/api'
import type { MotionFeel } from '../tokens/motion'
import { transition } from '../tokens/motion'
import { wheelGeom, placePolar, ringRadii, sectorHue, wedgePath, chordPath, arrowHead, sectorMidAngle, dyadicLevels } from '../lib/seed'
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
  showGrid = false,
}: {
  proj: Projection
  feel: MotionFeel
  selectedSeq?: number
  onPick: (p: ProjPoint) => void
  showGrid?: boolean
}) {
  const { ref, width, height } = useSize<HTMLDivElement>()
  const ready = width > 8 && height > 8
  const { cx, cy, R } = wheelGeom(width || 1, height || 1)
  const sectorIndex = new Map(proj.sectors.map((s, i) => [s.id, i]))
  const n = Math.max(proj.n, 1)

  // GROUP 10 drive-to-explore: tap a sector → its OUT edges glow, IN edges ink, the rest fade. Pure read.
  const [selSector, setSelSector] = useState<number | null>(null)
  useEffect(() => {
    setSelSector(null)
  }, [proj.binding.id]) // clear when the lens changes
  const hasEdges = proj.edges.length > 0

  return (
    <div ref={ref} className="wheel-region" {...stamp('ui://instrument/wheel')}>
      {ready && (
        <svg viewBox={`0 0 ${width} ${height}`} className="wheel-svg" role="img" aria-label="instrument">
          {/* THE SQUARE / STRUCTURE half, present together with the circle (the seed §1/§5: the circle is
             INSCRIBED IN the square — square is the outer frame, half-side R, the circle touches its edge
             midpoints; the corners (r·√2) are the forbidden zone). Shown in BOTH view; hidden when the circle
             is isolated. Faint dyadic nested grid + box + the two axes (the coincidence spine), under the circle. */}
          {showGrid && (() => {
            const box = R // outer square: half-side = inscribed-circle radius
            const SQRT2 = Math.SQRT2
            return (
              <g className="wheel-grid">
                {/* the forbidden corner-circle (through the square's corners, bulging past the inscribed circle) —
                   load-bearing in the inscribe story ("the circle that does NOT fit"), so it reads deliberately */}
                <circle cx={cx} cy={cy} r={R * SQRT2} fill="none" stroke="var(--pig-strain)" strokeOpacity={0.36}
                  strokeWidth={1.2} strokeDasharray="4 5" />
                <rect x={cx - box} y={cy - box} width={2 * box} height={2 * box} fill="none"
                  stroke="var(--hairline)" strokeWidth={1} strokeOpacity={0.7} />
                {dyadicLevels(proj.grid || 8).map(({ divisions, weight }) =>
                  Array.from({ length: divisions - 1 }, (_, k) => {
                    const t = (k + 1) / divisions
                    const gx = cx - box + t * 2 * box
                    const gy = cy - box + t * 2 * box
                    return (
                      <g key={`g-${divisions}-${k}`}>
                        <line x1={gx} y1={cy - box} x2={gx} y2={cy + box} stroke="var(--ink-faint)" strokeOpacity={weight * 0.34} strokeWidth={1} />
                        <line x1={cx - box} y1={gy} x2={cx + box} y2={gy} stroke="var(--ink-faint)" strokeOpacity={weight * 0.34} strokeWidth={1} />
                      </g>
                    )
                  }),
                )}
                <line x1={cx} y1={cy - box} x2={cx} y2={cy + box} stroke="var(--ink-faint)" strokeOpacity={0.32} strokeWidth={1} />
                <line x1={cx - box} y1={cy} x2={cx + box} y2={cy} stroke="var(--ink-faint)" strokeOpacity={0.32} strokeWidth={1} />
              </g>
            )
          })()}

          {/* concentric rings — the m/2 rings (seed §1), hairline */}
          {ringRadii(proj.rings, R).map((rad, k) => (
            <circle key={`ring-${k}`} cx={cx} cy={cy} r={rad}
              fill="none" stroke="var(--hairline)" strokeWidth={1} />
          ))}

          {/* sector wedges — soft angle-hue fill + hairline edges (colour IS geometry). A single sector
             (n≤1, e.g. one semantic space) has NO meaningful angular division — skip the degenerate
             full-circle wedge and show clean rings + points instead. */}
          {n > 1 &&
            proj.sectors.map((s, i) => {
              const sel = selSector === i
              const dim = selSector != null && !sel
              return (
                <path
                  key={`sec-${s.id}-${i}`}
                  {...stamp(`ui://instrument/sector/${encodeURIComponent(s.id)}`)}
                  className="wheel-sector"
                  d={wedgePath(s.from, s.to, cx, cy, R)}
                  fill={sectorHue(i, n)}
                  fillOpacity={sel ? 0.3 : dim ? 0.05 : 0.13}
                  stroke="var(--hairline)"
                  strokeWidth={1}
                  style={hasEdges ? { cursor: 'pointer' } : undefined}
                  onClick={hasEdges ? (e) => { e.stopPropagation(); setSelSector(sel ? null : i) } : undefined}
                />
              )
            })}

          {/* THE CONNECTIONS (Group 10) — the REAL directional typed edges as directed chords. Registry-true
             (the engine supplies edges as sector indices). Source dot at `from`, arrowhead at `to`; a bidir
             edge (a genuine cycle) gets arrowheads at BOTH ends — cycles rendered AS cycles. Calm/paper opacity. */}
          {proj.edges.length > 0 &&
            proj.edges.map((e) => {
              const sf = proj.sectors[e.from]
              const st = proj.sectors[e.to]
              if (!sf || !st) return null
              const ch = chordPath(sectorMidAngle(sf.from, sf.to), sectorMidAngle(st.from, st.to), cx, cy, R * 0.84)
              // directional emphasis: OUT (from the tapped sector) glows; IN (to it) inks; the rest fade
              const role = selSector == null ? 'base' : e.from === selSector ? 'out' : e.to === selSector ? 'in' : 'faded'
              const stroke = role === 'out' ? 'var(--pig-leanB)' : role === 'in' ? 'var(--ink-primary)' : 'var(--ink-dim)'
              const op = role === 'faded' ? 0.05 : role === 'out' || role === 'in' ? 0.75 : e.bidir ? 0.32 : 0.2
              const sw = role === 'out' || role === 'in' ? 1.7 : e.bidir ? 1.4 : 1
              return (
                <motion.g
                  key={`edge-${e.from}-${e.to}`}
                  {...stamp(`ui://instrument/edge/${e.from}-${e.to}`)}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={transition('enter', feel)}
                >
                  {(() => {
                    const head = role === 'out' || role === 'in' ? 8 : 6 // arrowheads carry direction — readable
                    return (
                      <>
                        <path d={ch.d} fill="none" stroke={stroke} strokeOpacity={op} strokeWidth={sw} />
                        <circle cx={ch.from.x} cy={ch.from.y} r={2} fill={stroke} fillOpacity={Math.min(op + 0.1, 0.8)} />
                        <path d={arrowHead(ch.to, ch.ctrl, head)} fill={stroke} fillOpacity={Math.min(op + 0.15, 0.9)} />
                        {e.bidir && <path d={arrowHead(ch.from, ch.ctrl, head)} fill={stroke} fillOpacity={Math.min(op + 0.15, 0.9)} />}
                      </>
                    )
                  })()}
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

      {/* GROUP 10 readout — name the tapped sector + its directional degree; 0-in/0-out is a FINDING
         (a pure source feeds but is unfed; a pure sink is fed but feeds nothing), not an empty state */}
      {hasEdges && selSector != null && (() => {
        const out = proj.edges.filter((e) => e.from === selSector).length
        const inc = proj.edges.filter((e) => e.to === selSector).length
        const finding = out > 0 && inc === 0 ? 'pure source' : inc > 0 && out === 0 ? 'pure sink' : null
        return (
          <div className="conn-readout" {...stamp('ui://instrument/connections')}>
            <span className="conn-name">{(proj.sectors[selSector]?.id || '').split('/').pop()}</span>
            <span className="conn-out">{out} out</span>
            <span className="conn-in">{inc} in</span>
            {finding && <span className="conn-finding">{finding}</span>}
          </div>
        )
      })()}
    </div>
  )
}
