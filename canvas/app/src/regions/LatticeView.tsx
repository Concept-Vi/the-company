// LatticeView — THE UNIVERSAL PROJECTION rendered (Tim Geldard's equation).
// The stores as exactly-the-same-points, for free: θ = kind (the sector registry — types are
// angular divisions; n rows re-divide the whole circle), r = time from NOW (the centre), depth =
// nesting, phases = the timestamp's cycles. No layout engine — positions arrive computed; this
// component only draws. Color IS angle (the color wheel is the circle): each sector's hue is its
// midpoint angle — a new registry row re-colors the screen by geometry, never by hand.
import { useCallback, useEffect, useRef, useState } from 'react'

type ProjPoint = {
  seq: number; kind: string; sector: string; theta: number; r: number; depth: number
  address: string; summary: string; ts: string; phases: { day: number; week: number }
}
type Projection = {
  now: string; n: number; rings: number; count: number
  sectors: { id: string; label: string; meaning: string; from: number; to: number }[]
  points: ProjPoint[]
}

const token = (name: string, fall: string) =>
  (typeof window !== 'undefined'
    ? getComputedStyle(document.documentElement).getPropertyValue(name).trim()
    : '') || fall

export default function LatticeView({ onHandoff }: { onHandoff?: () => void }) {
  const wrapRef = useRef<HTMLDivElement | null>(null)
  const cvsRef = useRef<HTMLCanvasElement | null>(null)
  const [proj, setProj] = useState<Projection | null>(null)
  const [picked, setPicked] = useState<ProjPoint | null>(null)
  const [sel, setSel] = useState<ProjPoint[]>([])   // the accumulating working set (forager: sculpt → hand to builder)
  const [zoom, setZoom] = useState(1)        // radial magnification — inner rings (recent) expand
  const [err, setErr] = useState('')
  const inSel = (p: ProjPoint) => sel.some(s => s.seq === p.seq)

  useEffect(() => {
    fetch('/api/projection')
      .then(r => { if (!r.ok) throw new Error(`projection ${r.status}`); return r.json() })
      .then(setProj)
      .catch(e => setErr(String(e?.message || e)))
  }, [])

  const draw = useCallback(() => {
    const cvs = cvsRef.current, wrap = wrapRef.current
    if (!cvs || !wrap || !proj) return
    const dpr = window.devicePixelRatio || 1
    const w = wrap.clientWidth, h = wrap.clientHeight
    cvs.width = w * dpr; cvs.height = h * dpr
    cvs.style.width = `${w}px`; cvs.style.height = `${h}px`
    const g = cvs.getContext('2d')!
    g.setTransform(dpr, 0, 0, dpr, 0, 0)
    g.clearRect(0, 0, w, h)

    const cx = w / 2, cy = h / 2
    const R = Math.min(w, h) / 2 - 34
    const ink = token('--ink', '#c9d1d9'), line = token('--line', '#30363d')
    const accent = token('--accent', '#d4a017')

    // The rings — the inscribed circles (time shells around NOW).
    g.strokeStyle = line; g.lineWidth = 1; g.globalAlpha = 0.55
    for (let i = 1; i <= proj.rings; i++) {
      g.beginPath(); g.arc(cx, cy, (R * i) / proj.rings, 0, Math.PI * 2); g.stroke()
    }
    // The sector boundaries + labels (the angular type divisions — the registry drawn).
    g.globalAlpha = 0.5
    for (const s of proj.sectors) {
      g.beginPath(); g.moveTo(cx, cy)
      g.lineTo(cx + Math.sin(s.from) * R, cy - Math.cos(s.from) * R); g.stroke()
    }
    g.globalAlpha = 0.9; g.fillStyle = ink
    g.font = '11px ui-monospace, monospace'; g.textAlign = 'center'
    const inside = w < 520            // phone face: labels tuck inside the rim (no edge clipping)
    for (const s of proj.sectors) {
      const mid = (s.from + s.to) / 2, lr = inside ? R - 14 : R + 16
      g.fillText(s.label, cx + Math.sin(mid) * lr, cy - Math.cos(mid) * lr + 4)
    }
    // The points — exactly the same points, drawn where they already are.
    const selSeqs = new Set(sel.map(s => s.seq))
    for (const p of proj.points) {
      const rr = Math.pow(p.r, 1 / zoom) * R
      const x = cx + Math.sin(p.theta) * rr, y = cy - Math.cos(p.theta) * rr
      const hue = (p.theta * 180) / Math.PI            // color IS angle
      const chosen = selSeqs.has(p.seq)
      g.globalAlpha = p === picked ? 1 : 0.75
      g.fillStyle = p === picked ? accent : `hsl(${hue}deg 55% 58%)`
      g.beginPath(); g.arc(x, y, p === picked ? 5 : 2.1, 0, Math.PI * 2); g.fill()
      if (chosen) {  // the working set rings — what will ride into the builder
        g.globalAlpha = 0.95; g.strokeStyle = accent; g.lineWidth = 1.5
        g.beginPath(); g.arc(x, y, 6, 0, Math.PI * 2); g.stroke()
      }
    }
    // NOW — the centre, the one shared point of time.
    g.globalAlpha = 1; g.fillStyle = accent
    g.beginPath(); g.arc(cx, cy, 4, 0, Math.PI * 2); g.fill()
    g.strokeStyle = accent; g.globalAlpha = 0.4
    g.beginPath(); g.arc(cx, cy, 9, 0, Math.PI * 2); g.stroke()
    g.globalAlpha = 1
  }, [proj, picked, zoom, sel])

  useEffect(() => { draw() }, [draw])
  useEffect(() => {
    const ro = new ResizeObserver(draw)
    if (wrapRef.current) ro.observe(wrapRef.current)
    return () => ro.disconnect()
  }, [draw])

  const pick = (ev: { clientX: number; clientY: number }) => {
    const wrap = wrapRef.current
    if (!wrap || !proj) return
    const rect = wrap.getBoundingClientRect()
    const px = ev.clientX - rect.left, py = ev.clientY - rect.top
    const w = rect.width, h = rect.height
    const cx = w / 2, cy = h / 2, R = Math.min(w, h) / 2 - 34
    let best: ProjPoint | null = null, bd = 14 * 14
    for (const p of proj.points) {
      const rr = Math.pow(p.r, 1 / zoom) * R
      const x = cx + Math.sin(p.theta) * rr, y = cy - Math.cos(p.theta) * rr
      const d = (x - px) * (x - px) + (y - py) * (y - py)
      if (d < bd) { bd = d; best = p }
    }
    setPicked(best)
  }

  const phaseWord = (d: number) => {
    const hrs = Math.round(d * 24)
    return hrs < 6 ? 'night' : hrs < 12 ? 'morning' : hrs < 18 ? 'afternoon' : 'evening'
  }

  const toggleSel = (p: ProjPoint) =>
    setSel(s => s.some(q => q.seq === p.seq) ? s.filter(q => q.seq !== p.seq) : [...s, p])

  // hand the working set to the BUILDER (the forager seam — same 'builder-context' contract the
  // mobile tray uses; replace-semantics; onHandoff makes the panel visible: canvas view + builder tab).
  const handToBuilder = () => {
    if (!sel.length) return
    const block = `[Operator's lattice selection — ${sel.length} point${sel.length === 1 ? '' : 's'} — CURRENT context]\n` +
      sel.map(p => `- (${p.sector}) ${p.address || p.kind}${p.summary ? ` — ${p.summary}` : ''}`).join('\n')
    window.dispatchEvent(new CustomEvent('builder-context', { detail: { block } }))
    onHandoff?.()
  }

  if (err) return <div className="lattice-err">projection unreachable — {err}</div>
  return (
    <div className="lattice-wrap" ref={wrapRef} onPointerDown={pick}>
      <canvas ref={cvsRef} />
      <div className="lattice-foot">
        <span>{proj ? `${proj.count} points · ${proj.n} sectors · centre = now` : 'projecting…'}</span>
        <label className="lattice-zoom">
          recent⊙<input type="range" min={0.5} max={3.2} step={0.1} value={zoom}
            onChange={e => setZoom(Number(e.target.value))}
            onPointerDown={e => e.stopPropagation()} />
        </label>
      </div>
      {picked && (
        <div className="lattice-card" onPointerDown={e => e.stopPropagation()}>
          <div className="lc-head">
            <span className="lc-sector">{picked.sector}</span>
            <span className="lc-kind">{picked.kind}</span>
            <button className="lc-x" onClick={() => setPicked(null)}>✕</button>
          </div>
          {picked.summary && <div className="lc-sum">{picked.summary}</div>}
          {picked.address && <div className="lc-addr">{picked.address}</div>}
          <div className="lc-meta">
            {picked.ts?.slice(0, 16).replace('T', ' · ')} · {phaseWord(picked.phases.day)} ·
            depth {picked.depth}
          </div>
          <button className="lc-pick" onClick={() => toggleSel(picked)}>
            {inSel(picked) ? '− remove from set' : '＋ add to set'}
          </button>
        </div>
      )}
      {sel.length > 0 && (
        <div className="lattice-set" onPointerDown={e => e.stopPropagation()}>
          <span className="ls-n">⊙ {sel.length} selected</span>
          <button className="ls-go" onClick={handToBuilder}>⚒ hand to builder</button>
          <button className="ls-clear" onClick={() => setSel([])}>clear</button>
        </div>
      )}
    </div>
  )
}
