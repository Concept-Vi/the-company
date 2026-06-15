import { useEffect, useRef } from 'react'

// THE SELECTION TETHER (design-critic, all lenses) — when a point is selected its detail card appears at the
// edge of the field (panel / sheet / rail), and the eye loses which dot it belongs to. A calm ink curve links
// the selected dot to its card so the relation is SEEN, not inferred. Renderer-agnostic: every lens marks its
// selected dot with `data-tether-point` and the disclosure marks itself `data-tether-card`; this fixed overlay
// measures both in client coords and draws between them. Pure presentation — pointer-events off, never blocks
// a click; zero React re-renders per frame (a rAF loop writes the path/opacity through refs, so following the
// card's enter-animation + live re-projections + scroll/resize is free).
export function Tether({ selectedSeq }: { selectedSeq?: number }) {
  const svgRef = useRef<SVGSVGElement>(null)
  const pathRef = useRef<SVGPathElement>(null)
  const ringRef = useRef<SVGCircleElement>(null)

  useEffect(() => {
    const svg = svgRef.current
    if (selectedSeq == null) {
      if (svg) svg.style.opacity = '0'
      return
    }
    let raf = 0
    const tick = () => {
      const svgEl = svgRef.current
      const path = pathRef.current
      const ring = ringRef.current
      const ptEl = document.querySelector('[data-tether-point]')
      const cardEl = document.querySelector('[data-tether-card]')
      if (svgEl && path && ptEl && cardEl) {
        const pr = ptEl.getBoundingClientRect()
        const cr = cardEl.getBoundingClientRect()
        const px = pr.left + pr.width / 2
        const py = pr.top + pr.height / 2
        // the card anchor = the point on the card's border nearest the dot (closest edge/corner)
        const ax = Math.max(cr.left, Math.min(px, cr.right))
        const ay = Math.max(cr.top, Math.min(py, cr.bottom))
        const dx = ax - px
        const dy = ay - py
        const len = Math.hypot(dx, dy) || 1
        // start at the dot's EDGE (≈ its selected radius), not its centre — the line meets the dot, not its core
        const ux = dx / len
        const uy = dy / len
        const sx = px + ux * 7
        const sy = py + uy * 7
        // BOW THE ARC AWAY FROM THE WHEEL HUB. A straight chord runs through the centre and reads as just
        // another radial spoke — the link dissolves at the convergence (design-critic FAIL). So push the
        // control point RADIALLY OUTWARD from the wheel centre: the tether arcs through open paper, never along
        // the spoke geometry. Fallback (no wheel found): perpendicular to the chord, so it still curves.
        const mx = (sx + ax) / 2
        const my = (sy + ay) / 2
        let bx = -uy
        let by = ux
        const wheelEl = document.querySelector('.wheel-region')
        if (wheelEl) {
          const wr = wheelEl.getBoundingClientRect()
          const awx = mx - (wr.left + wr.width / 2)
          const awy = my - (wr.top + wr.height / 2)
          const al = Math.hypot(awx, awy)
          if (al > 24) { bx = awx / al; by = awy / al }
        }
        const bow = Math.min(len * 0.22, 130)
        const cxb = mx + bx * bow
        const cyb = my + by * bow
        path.setAttribute('d', `M ${sx.toFixed(1)} ${sy.toFixed(1)} Q ${cxb.toFixed(1)} ${cyb.toFixed(1)} ${ax.toFixed(1)} ${ay.toFixed(1)}`)
        if (ring) {
          ring.setAttribute('cx', ax.toFixed(1))
          ring.setAttribute('cy', ay.toFixed(1))
        }
        // only show once the dot is far enough from the card to be a real link (avoids a stub on a tiny gap)
        svgEl.style.opacity = len > 18 ? '1' : '0'
      } else if (svgEl) {
        svgEl.style.opacity = '0'
      }
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => {
      cancelAnimationFrame(raf)
      const s = svgRef.current
      if (s) s.style.opacity = '0'
    }
  }, [selectedSeq])

  return (
    <svg ref={svgRef} className="tether-overlay" aria-hidden>
      <path ref={pathRef} className="tether-line" fill="none" />
      <circle ref={ringRef} className="tether-node" r={2.4} />
    </svg>
  )
}
