import { useState } from 'react'
import type { SurfaceState, ViewMode } from '../App'
import type { Projection } from '../lib/api'
import { stamp } from '../lib/address'

// the operator can HIDE the explanation (Tim 2026-06-17: "I should be able to hide them if wanted"). The TITLE
// stays (so they always know which view they're on); the explanation lines collapse. Preference persists.
const COLLAPSE_KEY = 'instrument.legend.collapsed'

// A calm, always-present ORIENTATION (Tim 2026-06-14: "just looking at it I don't know what it is or what it
// chose"). Says, for the active lens: what it is, what the ANGLE/sectors mean, what the RADIUS means, and the
// centre. Text-minimal but never cryptic — derived from the binding (registry-true), not hardcoded per lens.
function angleMeaning(af: string): string {
  if (af === 'kind') return 'the kind of each event'
  if (af === 'kind-group' || af === 'grouped') return 'grouped activity'
  if (!af) return 'one division'
  return `${af.replace(/_/g, ' ')} (one sector each)`
}

function describe(proj: Projection, view: ViewMode, centred: string | null): { title: string; lines: string[] } {
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
        'corners · the residue → grow the box (a new axis)',
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
    if (!centred) {
      return {
        title: b.label,
        lines: ['radius · meaning-distance from the centre', 'pick a point → ⊙ centre here to begin'],
      }
    }
    // centred → the SIGNED strain field shows. Decode BOTH the endpoint glyphs (filed vs meant) and the
    // direction, and cue the two populations so "two directions of tension" is immediate, not inferred.
    let out = 0
    let inn = 0
    for (const p of proj.points) {
      if (p.strain == null || p.r_struct == null || p.scale_size) continue
      if (p.r > p.r_struct) out++
      else inn++
    }
    return {
      title: b.label,
      lines: [
        `radius · meaning-distance from ${centred}`,
        'lines · strain (open tick = filed · dot = meant)',
        `warm = meaning farther (out ${out}) · cool = nearer (in ${inn})`,
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
  const [collapsed, setCollapsed] = useState<boolean>(() => {
    try {
      return localStorage.getItem(COLLAPSE_KEY) === '1'
    } catch {
      return false
    }
  })
  if (!s.proj) return null

  // Compute the orientation ONCE: DECLARED human meaning (registry-true — the binding's `meta`, lead with
  // WHAT-IT-IS then what-fills-it + why; Tim 2026-06-17: the operator must know what they're looking at), else
  // the computed mechanical lines for lenses not yet seeded. The meaning lives in the REGISTRY, never here.
  const meta = s.proj.binding.meta
  let title: string
  let lines: string[]
  if (meta && meta.is) {
    title = meta.name || s.proj.binding.label
    lines = [meta.is, meta.fills, meta.why].filter(Boolean) as string[]
  } else {
    const d = describe(s.proj, s.view, s.centre?.label ?? null)
    // In Both, name the coincidence spine (seed §3): the diamonds on the axes are where the SQUARE (grid) and
    // the CIRCLE (rings) meet — lens-neutral, and only for lenses whose wheel actually draws it.
    const rf = s.proj.binding.radius_from
    const wheelLens = rf !== 'separator' && rf !== 'nucleation'
    title = d.title
    lines =
      s.view === 'both' && wheelLens
        ? [...d.lines, '◆ on the axes · where grid & circle meet — the ratified spine']
        : d.lines
  }

  const toggle = () =>
    setCollapsed((c) => {
      const next = !c
      try {
        localStorage.setItem(COLLAPSE_KEY, next ? '1' : '0')
      } catch {
        /* storage blocked — the choice still holds for the session */
      }
      return next
    })

  return (
    <div className="legend" data-collapsed={collapsed} {...stamp('ui://instrument/legend')}>
      <div className="legend-head">
        <div className="legend-title display">{title}</div>
        <button
          type="button"
          className="legend-toggle"
          onClick={toggle}
          aria-expanded={!collapsed}
          aria-label={collapsed ? 'Show the explanation' : 'Hide the explanation'}
          title={collapsed ? 'Show the explanation' : 'Hide the explanation'}
        >
          {collapsed ? '⌄' : '⌃'}
        </button>
      </div>
      {!collapsed && (
        <ul className="legend-lines">
          {lines.map((l, i) => (
            <li key={i}>{l}</li>
          ))}
        </ul>
      )}
    </div>
  )
}
