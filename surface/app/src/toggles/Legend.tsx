import type { SurfaceState } from '../App'
import type { Projection } from '../lib/api'
import { stamp } from '../lib/address'

// A calm, always-present ORIENTATION (Tim 2026-06-14: "just looking at it I don't know what it is or what it
// chose"). Says, for the active lens: what it is, what the ANGLE/sectors mean, what the RADIUS means, and the
// centre. Text-minimal but never cryptic — derived from the binding (registry-true), not hardcoded per lens.
function angleMeaning(af: string): string {
  if (af === 'kind') return 'the kind of each event'
  if (af === 'kind-group' || af === 'grouped') return 'grouped activity'
  if (!af) return 'one division'
  return `${af.replace(/_/g, ' ')} (one sector each)`
}

function describe(proj: Projection, view: 'circle' | 'square', centred: string | null): { title: string; lines: string[] } {
  const b = proj.binding
  const n = proj.n
  if (view === 'square') {
    return {
      title: 'Structure — the address grid',
      lines: [
        'each point sits in its address cell',
        'grid · recursive dyadic nesting',
        'corners · forbidden (unreachable)',
      ],
    }
  }
  if (b.radius_from === 'nucleation') {
    return {
      title: b.label,
      lines: [
        `${n} sectors · one per type`,
        'inside the ring · fits that type',
        'outside · the misfit pile → new types (✦)',
      ],
    }
  }
  if (b.radius_from === 'separator') {
    return {
      title: b.label,
      lines: ['left / right · the two poles', 'distance from the centre line · how strongly it leans', 'the bar · the balance between them'],
    }
  }
  if (b.radius_from === 'semantic') {
    const sc = proj.scale
    if (sc && sc.rung !== 'unit') {
      // G11 coarse rung — the points are theme centroids (clusters), not units
      return {
        title: b.label,
        lines: [
          `${proj.count} themes · clusters at rung ${sc.rung}`,
          'bigger blob · more items in the theme',
          centred ? `radius · meaning-distance from ${centred}` : 'pick a point → ⊙ centre here',
        ],
      }
    }
    return {
      title: b.label,
      lines: [
        centred ? `radius · meaning-distance from ${centred}` : 'radius · meaning-distance from the centre',
        centred ? 'lines · the strain (filed vs meant)' : 'pick a point → ⊙ centre here to begin',
      ],
    }
  }
  // edges present → connections
  if (proj.edges && proj.edges.length > 0) {
    return {
      title: b.label,
      lines: [`${n} sectors · ${angleMeaning(b.angle_from)}`, 'curves · directional typed edges (the connections)'],
    }
  }
  // time / address default
  return {
    title: b.label,
    lines: [
      `${n} sectors · angle = ${angleMeaning(b.angle_from)}`,
      centred ? `radius · distance from ${centred}` : 'radius · age (centre = now)',
    ],
  }
}

export function Legend({ s }: { s: SurfaceState }) {
  if (!s.proj) return null
  const { title, lines } = describe(s.proj, s.view, s.centre?.label ?? null)
  // In Both, the circle and square are over one space — name the coincidence spine (seed §3): the diamonds on
  // the axes are where structure and meaning AGREE (the ratified / addressable points). Only meaningful in Both.
  const all = s.view === 'both' ? [...lines, '◆ on the axes · where structure & meaning agree'] : lines
  return (
    <div className="legend" {...stamp('ui://instrument/legend')}>
      <div className="legend-title display">{title}</div>
      <ul className="legend-lines">
        {all.map((l, i) => (
          <li key={i}>{l}</li>
        ))}
      </ul>
    </div>
  )
}
