// THE SEED IS THE LAYOUT GRID (MANDATE §3/L3 · RESEARCH-SYNTHESIS §D)
// The constants below are LAW (replicated from runtime/projection.py), not parameters. The whole
// wheel — and the spacing that surrounds it — is measured on them, so "nothing is out of proportion"
// is structural, not policed. Polar (theta, r) come straight from /api/projection; we only place them.

export const TAU = Math.PI * 2

// The normalized radius band the engine emits points within ([0.06,1.0]); nucleation pile rides >1.
export const R_MIN = 0.06
export const R_MAX = 1.0

// Fraction of the wheel-region half-extent the r=1.0 ring occupies (leaves a margin band for blooms/labels).
export const WHEEL_FRAC = 0.46

export type Vec2 = { x: number; y: number }

// Centre + radius of the wheel given a region box. In a TALL frame (mobile portrait) the wheel is
// width-constrained — bias it to own more of the width so it dominates the frame (design-critic fix #5),
// instead of floating small with generous side margins. Wide/square frames keep the balanced fraction.
export function wheelGeom(width: number, height: number): { cx: number; cy: number; R: number } {
  const cx = width / 2
  const cy = height / 2
  const tall = height > width * 1.25
  const R = tall ? Math.min(width * 0.48, height * 0.4) : Math.min(width, height) * WHEEL_FRAC
  return { cx, cy, R }
}

// Place a projection point (polar) onto the wheel. theta is already in radians, even-divided by the lock.
// We rotate -90deg so theta=0 reads at the top (north), the natural "12 o'clock start" for a dial.
export function placePolar(theta: number, r: number, cx: number, cy: number, R: number): Vec2 {
  const a = theta - Math.PI / 2
  return { x: cx + r * R * Math.cos(a), y: cy + r * R * Math.sin(a) }
}

// The m/2 concentric ring radii (in px) for a wheel of radius R.
export function ringRadii(rings: number, R: number): number[] {
  const out: number[] = []
  for (let k = 1; k <= rings; k++) out.push((k / rings) * R)
  return out
}

// Angle-hue: sector i -> a muted hue. Colour IS geometry (the one colour inheritance worth keeping).
// sat/lit read from CSS so the pigment taste toggle (S4.2) re-tints live.
export function sectorHue(i: number, n: number): string {
  const sat = cssVar('--pig-sat', '22%')
  const lit = cssVar('--pig-lit', '58%')
  return `hsl(${Math.round((360 * i) / Math.max(n, 1))} ${sat} ${lit})`
}

function cssVar(name: string, fallback: string): string {
  if (typeof window === 'undefined') return fallback
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  return v || fallback
}

// THE CONNECTIONS (Group 10): a directed chord between two sector mid-angles, arced through the interior.
// Direction is read by a source dot (at `from`) + an arrowhead (at `to`); a bidir edge (a real cycle) gets
// arrowheads at BOTH ends — cycles rendered AS cycles, never flattened. Registry-true (the engine supplies
// the edges as sector INDICES); nothing here invents an edge.
export function sectorMidAngle(from: number, to: number): number {
  return (from + to) / 2
}

export function chordPath(
  aMid: number, bMid: number, cx: number, cy: number, rEndPx: number, pull = 0.5,
): { d: string; from: Vec2; to: Vec2; ctrl: Vec2 } {
  const a0 = aMid - Math.PI / 2
  const a1 = bMid - Math.PI / 2
  const from = { x: cx + rEndPx * Math.cos(a0), y: cy + rEndPx * Math.sin(a0) }
  const to = { x: cx + rEndPx * Math.cos(a1), y: cy + rEndPx * Math.sin(a1) }
  const mx = (from.x + to.x) / 2, my = (from.y + to.y) / 2
  const ctrl = { x: mx + (cx - mx) * pull, y: my + (cy - my) * pull } // pulled toward centre = a calm arc
  return { d: `M ${from.x} ${from.y} Q ${ctrl.x} ${ctrl.y} ${to.x} ${to.y}`, from, to, ctrl }
}

// A small arrowhead triangle at `tip`, oriented along the direction coming FROM `tail`.
export function arrowHead(tip: Vec2, tail: Vec2, size = 5): string {
  const ang = Math.atan2(tip.y - tail.y, tip.x - tail.x)
  const a1 = ang + Math.PI - 0.45, a2 = ang + Math.PI + 0.45
  const p1 = { x: tip.x + size * Math.cos(a1), y: tip.y + size * Math.sin(a1) }
  const p2 = { x: tip.x + size * Math.cos(a2), y: tip.y + size * Math.sin(a2) }
  return `M ${tip.x} ${tip.y} L ${p1.x} ${p1.y} L ${p2.x} ${p2.y} Z`
}

// ── THE SQUARE / STRUCTURE HALF (seed §1–3) ──────────────────────────────────────────────────────
// The box is the inscribed-circle square: half-side = R (so the inscribed circle touches the edge
// midpoints, exactly the seed construction). A point's dyadic cell (i,j) in an m×m grid sits at the
// cell centre; multiple points per cell get a stable sub-cell offset (deterministic — no Math.random).
function hash01(n: number): number {
  const x = Math.sin(n * 12.9898 + 1.7) * 43758.5453
  return x - Math.floor(x)
}

export function gridCellCenter(
  i: number, j: number, m: number, cx: number, cy: number, R: number, jitterSeed = 0,
): Vec2 {
  const cell = (2 * R) / Math.max(m, 1)
  const jx = (hash01(jitterSeed) - 0.5) * cell * 0.6
  const jy = (hash01(jitterSeed * 2 + 11) - 0.5) * cell * 0.6
  return { x: cx - R + (i + 0.5) * cell + jx, y: cy - R + (j + 0.5) * cell + jy }
}

// The dyadic nesting divisions to draw, coarsest→finest, with an opacity weight (coarser = stronger):
// for m = 2^d, draw at 2, 4, …, m divisions. A parent boundary CONTAINS its children (MSB-first).
export function dyadicLevels(m: number): { divisions: number; weight: number }[] {
  const out: { divisions: number; weight: number }[] = []
  let div = 2
  const levels: number[] = []
  while (div <= m) { levels.push(div); div *= 2 }
  levels.forEach((d, k) => {
    // coarsest (k=0) strongest; fade toward the finest
    out.push({ divisions: d, weight: 0.16 - k * (0.12 / Math.max(levels.length - 1, 1)) })
  })
  return out
}

// SVG arc path for a sector wedge from inner radius 0 to R, spanning [from,to] radians.
export function wedgePath(from: number, to: number, cx: number, cy: number, R: number): string {
  const a0 = from - Math.PI / 2
  const a1 = to - Math.PI / 2
  const x0 = cx + R * Math.cos(a0), y0 = cy + R * Math.sin(a0)
  const x1 = cx + R * Math.cos(a1), y1 = cy + R * Math.sin(a1)
  const large = to - from > Math.PI ? 1 : 0
  return `M ${cx} ${cy} L ${x0} ${y0} A ${R} ${R} 0 ${large} 1 ${x1} ${y1} Z`
}
