import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import type { Projection, ProjPoint } from '../lib/api'
import type { NucParams } from '../App'
import type { MotionFeel } from '../tokens/motion'
import { transition } from '../tokens/motion'
import { placePolar, sectorHue, wedgePath } from '../lib/seed'
import { stamp } from '../lib/address'
import { useSize } from './useSize'
import { pointAddress } from './Wheel'

// TYPE-NUCLEATION — the type system AS the divisions of the circle (Tim 2026-06-14: "the types/divisions of
// the circle, so the data points close around the types"). Each registry type is an angular DIVISION; an item
// is typed against the registry and sits in its best-fit type's sector. Items that FIT cluster INSIDE the
// membership boundary (close around their type); misfits PILE OUTSIDE it (the forbidden zone); a distinct
// pile blooms as a CANDIDATE new type (✦) and is BORN once its mass passes the 20/80 dial. Pure read; the
// dial recomputes born client-side (instant); the space/rung pickers drive the engine (registry-true).

type NucReport = {
  pile_clustered?: number
  born_count?: number
  distinct_count?: number
  pile_total?: number
  n_types?: number
  zones?: { id: string; exemplar?: string; born?: boolean; distinct?: boolean; size?: number }[]
  available?: { item_spaces?: string[]; types_spaces?: string[]; rungs?: number[] }
}

export function Nucleation({
  proj,
  feel,
  selectedSeq,
  onPick,
  nuc,
  setNuc,
}: {
  proj: Projection
  feel: MotionFeel
  selectedSeq?: number
  onPick: (p: ProjPoint) => void
  nuc: NucParams
  setNuc: (patch: Partial<NucParams>) => void
}) {
  const { ref, width, height } = useSize<HTMLDivElement>()
  const ready = width > 8 && height > 8
  const cx = (width || 1) / 2
  const cy = (height || 1) / 2
  const R = Math.min(width || 1, height || 1) * 0.4 // r=1 boundary; pile rides to ~1.2·R outside it
  const report = (proj.nucleation || {}) as NucReport
  const typeSectors = proj.sectors.filter((s) => !s.id.startsWith('✦'))
  const n = Math.max(proj.n, 1)
  const sectorIndex = new Map(proj.sectors.map((s, i) => [s.id, i]))

  // the 20/80 birth DIAL — client-side so blooms toggle born/forming instantly (no refetch)
  const [dial, setDial] = useState(0.2)
  const pileClustered = report.pile_clustered ?? 0
  const birthMass = Math.max(3, Math.round(dial * pileClustered))
  const zones = report.zones || []
  const avail = report.available || {}

  // place each candidate bloom at its pile's TRUE angle (mean θ of the cluster's outside members), so a born
  // type appears where its pile actually is — not an arbitrary even spread. Fallback: even spread.
  const clusterTheta = new Map<number, { sum: number; k: number }>()
  for (const p of proj.points) {
    if (typeof p.pile_cluster === 'number') {
      const e = clusterTheta.get(p.pile_cluster) || { sum: 0, k: 0 }
      e.sum += p.theta ?? 0
      e.k += 1
      clusterTheta.set(p.pile_cluster, e)
    }
  }
  const zoneAngle = (k: number): number => {
    const e = clusterTheta.get(k)
    if (e && e.k > 0) return e.sum / e.k - Math.PI / 2
    return -Math.PI / 2 + (TAU_LOCAL * (k + 0.5)) / Math.max(zones.length, 1)
  }

  return (
    <div ref={ref} className="wheel-region" {...stamp('ui://instrument/nucleation')}>
      {ready && (
        <svg viewBox={`0 0 ${width} ${height}`} className="wheel-svg" role="img" aria-label="type nucleation">
          {/* the type DIVISIONS (registry types as angular sectors, angle-hue) */}
          {typeSectors.map((s, i) => (
            <path key={`t-${s.id}-${i}`} {...stamp(`ui://instrument/type/${encodeURIComponent(s.id)}`)}
              d={wedgePath(s.from, s.to, cx, cy, R)} fill={sectorHue(i, n)} fillOpacity={0.14}
              stroke="var(--hairline)" strokeWidth={1} />
          ))}

          {/* the MEMBERSHIP boundary (inside = fits a type / close around it; outside = the misfit pile) */}
          <circle cx={cx} cy={cy} r={R} fill="none" stroke="var(--ink-dim)" strokeOpacity={0.55} strokeWidth={1.4} />
          {/* the pile horizon (where the forbidden pile rides) */}
          <circle cx={cx} cy={cy} r={R * 1.18} fill="none" stroke="var(--pig-strain)" strokeOpacity={0.4}
            strokeWidth={1} strokeDasharray="3 5" />

          <circle cx={cx} cy={cy} r={3} fill="var(--ink-faint)" />

          {/* points — inside (clustered around their type) vs piled out (forbidden), animated */}
          <AnimatePresence>
            {proj.points.map((p) => {
              const pos = placePolar(p.theta, p.r, cx, cy, R)
              const i = sectorIndex.get(p.sector) ?? 0
              const isSel = p.seq === selectedSeq
              const addr = pointAddress(p)
              const inside = !!p.inside
              return (
                <motion.circle
                  key={addr}
                  {...stamp(addr)}
                  layoutId={addr}
                  className="wheel-dot"
                  fill={inside ? sectorHue(i, n) : 'var(--pig-strain)'}
                  fillOpacity={inside ? 0.6 : 0.46}
                  stroke={isSel ? 'var(--ink-primary)' : 'transparent'}
                  strokeWidth={isSel ? 1.5 : 0}
                  style={{ pointerEvents: 'none' }}
                  initial={{ cx: pos.x, cy: pos.y, r: 0, opacity: 0 }}
                  animate={{ cx: pos.x, cy: pos.y, r: isSel ? 5.5 : inside ? 2.6 : 1.9, opacity: 1 }}
                  exit={{ r: 0, opacity: 0 }}
                  transition={transition('move', feel)}
                />
              )
            })}
          </AnimatePresence>

          {/* candidate new-type BLOOMS at the rim — the climactic event made VISIBLE: a forming pile is a
             dashed ochre ring; a BORN type is a filled green disc with a soft halo + a ✦ spark. Placed at the
             pile's true angle. */}
          {zones.map((z, k) => {
            const born = !!z.distinct && (z.size ?? 0) >= birthMass
            const ang = zoneAngle(k)
            const bx = cx + R * 1.2 * Math.cos(ang)
            const by = cy + R * 1.2 * Math.sin(ang)
            const rad = 6 + Math.min((z.size ?? 0) / 6, 12)
            return (
              <g key={`zone-${z.id}-${k}`} {...stamp(`ui://instrument/candidate/${k}`)}>
                {born && (
                  // soft halo (paper-glow, not neon)
                  <circle cx={bx} cy={by} r={rad + 5} fill="var(--pig-born)" fillOpacity={0.12} />
                )}
                <motion.circle
                  cx={bx} cy={by}
                  initial={{ r: 0, opacity: 0 }}
                  animate={{ r: rad, opacity: 1 }}
                  transition={transition('enter', feel)}
                  fill={born ? 'var(--pig-born)' : 'none'}
                  fillOpacity={born ? 0.55 : 0}
                  stroke={born ? 'var(--pig-born)' : 'var(--pig-pile)'}
                  strokeOpacity={born ? 0.9 : 0.7}
                  strokeWidth={1.6}
                  strokeDasharray={born ? undefined : '3 3'}
                />
                {born && (
                  // the ✦ spark marks a NEW TYPE (distinct from any dial handle)
                  <text x={bx} y={by + 3.5} textAnchor="middle" fontSize={rad}
                    fill="var(--ground-accent)" style={{ pointerEvents: 'none' }}>✦</text>
                )}
              </g>
            )
          })}

          {/* hit layer */}
          {proj.points.map((p) => {
            const pos = placePolar(p.theta, p.r, cx, cy, R)
            const addr = pointAddress(p)
            return (
              <circle key={`hit-${addr}`} {...stamp(addr)} className="wheel-hit" cx={pos.x} cy={pos.y} r={15}
                fill="transparent" style={{ pointerEvents: 'all', cursor: 'pointer' }}
                onClick={(e) => { e.stopPropagation(); onPick(p) }} />
            )
          })}
        </svg>
      )}

      {/* the report (born / forming / pile) — calm, text-minimal */}
      <div className="nuc-report">
        <span className="nuc-born">{zones.filter((z) => z.distinct && (z.size ?? 0) >= birthMass).length} born</span>
        <span className="nuc-sep">·</span>
        <span className="nuc-form">{zones.length} candidates</span>
        <span className="nuc-sep">·</span>
        <span className="nuc-pile">{report.pile_total ?? 0} piled</span>
      </div>

      {/* the drive controls in ONE bottom stack (dial row, then the pickers row) so they never collide
         on a narrow frame */}
      <div className="nuc-controls">
        {/* the 20/80 birth dial — slides the mass a pile needs to be born (instant, client-side) */}
        <div className="nuc-dial" {...stamp('ui://controls/dial')}>
          <span className="nuc-dial-label">birth ◑</span>
          <input className="nuc-dial-range" type="range" name="nuc-dial" min={0} max={1} step={0.05} value={dial}
            onChange={(e) => setDial(Number(e.target.value))} aria-label="birth threshold" />
          <span className="nuc-dial-val">{Math.round(dial * 100)}%</span>
        </div>

        {/* the space / types / rung pickers — drive what is typed against what (registry-true) */}
        <div className="nuc-pickers" {...stamp('ui://controls/nuc')}>
          <Picker name="items" label="items" value={nuc.space} options={avail.item_spaces} onPick={(v) => setNuc({ space: v })} />
          <Picker name="types" label="types" value={nuc.types_space} options={avail.types_spaces} onPick={(v) => setNuc({ types_space: v })} />
          <Picker name="rung" label="rung" value={String(nuc.rung)} options={(avail.rungs || []).map(String)} onPick={(v) => setNuc({ rung: Number(v) })} />
        </div>
      </div>
    </div>
  )
}

const TAU_LOCAL = Math.PI * 2

function Picker({
  name, label, value, options, onPick,
}: {
  name: string; label: string; value: string; options?: string[]; onPick: (v: string) => void
}) {
  if (!options || options.length === 0) return null
  return (
    <label className="nuc-picker">
      <span className="nuc-picker-label">{label}</span>
      <select className="nuc-picker-sel" name={name} value={value} onChange={(e) => onPick(e.target.value)}>
        {options.map((o) => <option key={o} value={o}>{o}</option>)}
      </select>
    </label>
  )
}
