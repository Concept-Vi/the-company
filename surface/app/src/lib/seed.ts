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

// SVG arc path for a sector wedge from inner radius 0 to R, spanning [from,to] radians.
export function wedgePath(from: number, to: number, cx: number, cy: number, R: number): string {
  const a0 = from - Math.PI / 2
  const a1 = to - Math.PI / 2
  const x0 = cx + R * Math.cos(a0), y0 = cy + R * Math.sin(a0)
  const x1 = cx + R * Math.cos(a1), y1 = cy + R * Math.sin(a1)
  const large = to - from > Math.PI ? 1 : 0
  return `M ${cx} ${cy} L ${x0} ${y0} A ${R} ${R} 0 ${large} 1 ${x1} ${y1} Z`
}
