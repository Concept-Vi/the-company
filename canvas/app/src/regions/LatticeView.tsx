// LatticeView — THE UNIVERSAL PROJECTION rendered (Tim Geldard's equation).
// The stores as exactly-the-same-points, for free: θ = kind (the sector registry — types are
// angular divisions; n rows re-divide the whole circle), r = time from NOW (the centre), depth =
// nesting, phases = the timestamp's cycles. No layout engine — positions arrive computed; this
// component only draws. Color IS angle (the color wheel is the circle): each sector's hue is its
// midpoint angle — a new registry row re-colors the screen by geometry, never by hand.
import { useCallback, useEffect, useRef, useState } from 'react'
import { Badge, EmptyState } from '../components/kit'

type ProjPoint = {
  seq: number; kind: string; sector: string; theta: number; r: number; depth: number
  cell: { i: number; j: number; d: number }   // the dyadic structural coordinate (the square half)
  address: string; summary: string; ts: string; phases: { day: number; week: number }
  source?: string        // the embeddable key (present on corpus items) — the meaning-field re-centres on it
  r_unknown?: boolean     // a semantic point with no vector → at the rim, flagged (never silent-dropped)
}
type Projection = {
  now: string; n: number; rings: number; count: number; grid?: number
  // radius_from: 'time' (age) | 'address' (tree-distance) | 'semantic' (Group 6 — meaning-distance).
  // needs_center: the semantic lens is selected but no centre chosen yet → items laid out by time, awaiting one.
  binding?: { id: string; label: string; radius_from?: string; radius_normalized?: boolean; space?: string; needs_center?: boolean }
  bindings?: { id: string; label: string }[]
  sectors: { id: string; label: string; from: number; to: number }[]
  points: ProjPoint[]
}

export default function LatticeView({ onHandoff }: { onHandoff?: () => void }) {
  const wrapRef = useRef<HTMLDivElement | null>(null)
  const cvsRef = useRef<HTMLCanvasElement | null>(null)
  const [proj, setProj] = useState<Projection | null>(null)
  const [picked, setPicked] = useState<ProjPoint | null>(null)
  const [sel, setSel] = useState<ProjPoint[]>([])   // the accumulating working set (forager: sculpt → hand to builder)
  const [zoom, setZoom] = useState(1)        // radial magnification — inner rings (recent) expand
  const [frame, setFrame] = useState<'now' | 'day' | 'week'>('now')  // S4: scale/phase selects the frame
  const [bind, setBind] = useState<string>('')   // the LENS (binding id); '' = the data-driven default
  const [err, setErr] = useState('')
  const [live, setLive] = useState(true)     // the centre is NOW — and now MOVES (the involuntary axis)
  const [at, setAt] = useState<number | null>(null)          // S/G3 time scrubber — epoch secs (null = live NOW)
  const [center, setCenter] = useState<string | null>(null)  // S/G3 spatial re-centre — an address (null = temporal NOW)
  const nowAnchorRef = useRef(Date.now() / 1000)             // the live "now" epoch — the scrub-math anchor
  const spanRef = useRef(86400)                              // seconds the scrubber spans (the visible age range)
  const posRef = useRef<Map<number, { x: number; y: number }>>(new Map())   // last drawn point positions (identity)
  const animRef = useRef<{ from: Map<number, { x: number; y: number }>; t0: number } | null>(null)
  const inSel = (p: ProjPoint) => sel.some(s => s.seq === p.seq)
  // relative-time word for the scrubbed centre (NOW → the past), read off the live anchor
  const relTime = (epoch: number) => {
    const s = Math.max(Math.round(nowAnchorRef.current - epoch), 0)
    const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60)
    return h ? `${h}h${m ? ` ${m}m` : ''} ago` : m ? `${m}m ago` : 'moments ago'
  }

  // THE CIRCLE (Group 6): the semantic lens is selected but awaiting a centre → items lie by time, clickable
  // (pick one → meaning-field). isSemantic is the ACTIVE meaning-field (a real centre) — only then is r
  // meaning-distance and the temporal frames don't apply, so radius reads straight off p.r (zoomable).
  const semanticPending = proj?.binding?.needs_center === true
  const isSemantic = proj?.binding?.radius_from === 'semantic' && !semanticPending
  // S4 — frame-relativity (Tim: "the axes are variables too — scale and state/phase select the
  // frame"). 'now' = radius is age-from-NOW (the default arrow of time). 'day'/'week' = radius is
  // the timestamp's CYCLE coordinate, so the daily/weekly rhythm becomes visible: everything that
  // happened "at 9am" lands on one ring regardless of which day — the cycles, made geometry.
  const radial = (p: ProjPoint) =>
    (isSemantic || frame === 'now') ? Math.pow(p.r, 1 / zoom) : frame === 'day' ? p.phases.day : p.phases.week

  // The centre is NOW — so NOW must keep moving. The 15s POLL is retired: the lattice SUBSCRIBES to
  // /api/stream (SSE, the shared events.jsonl tap) and re-projects the instant an event is written, so a
  // new point appears in real time, not up-to-15s late — the projection as an organ, not a photograph.
  // Frozen (live off) OR scrubbed into the past = no live stream (the frame is held). Pure read.
  useEffect(() => {
    let alive = true, es: EventSource | null = null, deb = 0, lastSeq = -1
    const params = new URLSearchParams()
    if (bind) params.set('binding', bind)               // semantic-without-a-centre → the bridge returns the
    if (at != null) params.set('at', String(at))        // space's items by time, flagged needs_center (pick one)
    if (center) params.set('center', center)            // the spatial re-centre (radius = distance-from-address)
    const url = '/api/projection' + (params.toString() ? `?${params.toString()}` : '')
    const apply = (d: Projection, markNew: boolean) => {
      if (!alive) return
      // a re-projection driven by a NEW event: snapshot current positions so the arrivals DRIFT IN (the
      // existing tween fades in any seq not present before), while everything already placed holds still.
      if (markNew && posRef.current.size) animRef.current = { from: new Map(posRef.current), t0: performance.now() }
      setProj(d); setErr('')
      lastSeq = d.points.reduce((m, p) => Math.max(m, p.seq || 0), lastSeq)
    }
    const fetchProj = (markNew: boolean) => fetch(url)
      .then(async r => {
        if (!r.ok) {                                    // surface the bridge's legible message (semantic-no-centre etc.)
          const b = await r.json().catch(() => null)
          throw new Error(b?.hint || b?.error || `projection ${r.status}`)
        }
        return r.json()
      })
      .then(d => apply(d, markNew))
      .catch(e => { if (alive) setErr(String(e?.message || e)) })
    fetchProj(false).then(() => {
      if (!alive || !live || at != null) return         // frozen / scrubbed: no live subscription
      // subscribe from the latest seq we have → only FUTURE events stream (no replay of the whole log).
      es = new EventSource('/api/stream' + (lastSeq >= 0 ? `?since=${lastSeq}` : ''))
      es.onmessage = () => { clearTimeout(deb); deb = window.setTimeout(() => fetchProj(true), 220) }  // coalesce bursts
      // EventSource auto-reconnects on error (gapless via Last-Event-ID) — hold the last frame meanwhile.
    })
    return () => { alive = false; clearTimeout(deb); if (es) es.close() }
  }, [live, bind, at, center])

  // keep the scrub anchor + span fresh while live-at-NOW, so the scrubber spans the real visible age range
  useEffect(() => {
    if (at == null) nowAnchorRef.current = Date.now() / 1000
    if (at == null && proj && proj.points.length) {
      const nowE = Date.parse(proj.now) / 1000
      const oldest = Math.min(...proj.points.map(p => Date.parse(p.ts) / 1000))
      if (isFinite(oldest) && nowE - oldest > 0) spanRef.current = Math.max(nowE - oldest, 3600)
    }
  }, [proj, at])

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
    // Resolve the corpus tokens once per draw (canvas needs string colours, so read the computed
    // palette from design-system.css — never a hardcoded hex). The per-point hsl() angle-hue below
    // is the ONE deliberate non-token colour (colour IS geometry) — preserved on purpose.
    const css = getComputedStyle(document.documentElement)
    const v = (n: string) => css.getPropertyValue(n).trim()
    const ink = v('--tx'), line = v('--line'), accent = v('--acc'), dim = v('--tx-3'), bg = v('--bg')

    // THE SQUARE / STRUCTURE half (the seed §1): the box frames the wheel (the inscribed circle radius R
    // touches its edge midpoints); inside it the DYADIC grid — recursive quadrant lines that fade as they
    // deepen, so the nested structure (an address is a path is a grid coordinate) reads as a scaffold.
    const m = proj.grid || 1
    const levels = Math.max(Math.round(Math.log2(m)), 0)
    // the box frame reads FIRST (the brightest structural line, in the warm grey --tx-3 so it lifts off
    // the near-black); the dyadic grid inside fades BY LEVEL so the coarse subdivisions anchor "where in
    // the structure" and the fine ones recede — the self-similar nesting, kept legible but under the wheel.
    g.strokeStyle = dim
    g.globalAlpha = 0.85; g.lineWidth = 1.5; g.strokeRect(cx - R, cy - R, 2 * R, 2 * R)
    g.lineWidth = 1
    for (let L = 1; L <= levels; L++) {
      const div = 1 << L, step = (2 * R) / div
      g.globalAlpha = Math.max(0.5 - 0.12 * (L - 1), 0.12)   // L1 .50, L2 .38, L3 .26, L4 .14 — coarse brightest
      g.beginPath()
      for (let k = 1; k < div; k++) {
        g.moveTo(cx - R + k * step, cy - R); g.lineTo(cx - R + k * step, cy + R)
        g.moveTo(cx - R, cy - R + k * step); g.lineTo(cx + R, cy - R + k * step)
      }
      g.stroke()
    }
    // navigable structure: the picked point's dyadic CELL lights up in the grid (its structural home —
    // the SQUARE coordinate of the same item the circle shows angularly; the circle/square duality, seen).
    if (picked && picked.cell) {
      const side = (2 * R) / (1 << picked.cell.d)
      const x0 = cx - R + picked.cell.i * side, y0 = cy - R + picked.cell.j * side
      g.globalAlpha = 0.13; g.fillStyle = accent; g.fillRect(x0, y0, side, side)
      g.globalAlpha = 0.7; g.strokeStyle = accent; g.lineWidth = 1.5; g.strokeRect(x0, y0, side, side)
    }
    // The concentric rings — the seed's m/2 inscribed circles (the radial shells); the outermost (R) is
    // the circle inscribed in the box. Count = proj.rings (= m/2), resolved from the address hierarchy.
    g.strokeStyle = line; g.lineWidth = 1
    for (let i = 1; i <= proj.rings; i++) {
      g.globalAlpha = 0.5; g.beginPath(); g.arc(cx, cy, (R * i) / proj.rings, 0, Math.PI * 2); g.stroke()
    }
    // the radial-axis labels at fixed fractions (independent of the ring COUNT): 'now' marks the rim
    // (older outward); a cycle frame marks its clock quarters.
    const axisLabels: [number, string][] = isSemantic
      ? [[1, 'farther in meaning →']]                  // the CIRCLE: radius = meaning-distance from the centre
      : frame === 'now'
      ? [[1, 'older →']]
      : frame === 'day' ? [[0.25, '06h'], [0.5, '12h'], [0.75, '18h'], [1, '24h']]
      : [[0.25, 'Tue'], [0.5, 'Thu'], [0.75, 'Sat'], [1, 'Sun']]
    g.fillStyle = dim; g.font = '9px ui-monospace, monospace'; g.textAlign = 'left'
    for (const [frac, lab] of axisLabels) {
      g.globalAlpha = 0.6; g.fillText(lab, cx + 3, cy - R * frac + 11)
    }
    g.globalAlpha = 1
    // The sector boundaries + labels (the angular type divisions — the registry drawn).
    g.globalAlpha = 0.5
    for (const s of proj.sectors) {
      g.beginPath(); g.moveTo(cx, cy)
      g.lineTo(cx + Math.sin(s.from) * R, cy - Math.cos(s.from) * R); g.stroke()
    }
    g.font = '11px ui-monospace, monospace'; g.textAlign = 'center'
    const inside = w < 520            // phone face: labels tuck inside the rim (no edge clipping)
    // Label-thinning: the data-driven default can resolve many sectors (e.g. 50 raw kinds). Painting
    // every label would betray the default for legibility — so label only the MAJOR sectors (by
    // point-share), the rest read by colour/position. No privileged binding, just honest density.
    const perSector = new Map<string, number>()
    for (const p of proj.points) perSector.set(p.sector, (perSector.get(p.sector) || 0) + 1)
    const labelled = new Set(
      [...perSector.entries()].sort((a, b) => b[1] - a[1])
        .slice(0, proj.sectors.length <= 12 ? proj.sectors.length : 10).map(e => e[0]))
    for (const s of proj.sectors) {
      if (!labelled.has(s.id)) continue
      const mid = (s.from + s.to) / 2, lr = inside ? R - 14 : R + 16
      const lx = cx + Math.sin(mid) * lr, ly = cy - Math.cos(mid) * lr + 4
      const tw = g.measureText(s.label).width
      g.globalAlpha = 0.82; g.fillStyle = bg   // backing plate so labels read over dense arcs
      g.fillRect(lx - tw / 2 - 3, ly - 10, tw + 6, 14)
      g.globalAlpha = 1; g.fillStyle = ink
      g.fillText(s.label, lx, ly)
    }
    // The points — exactly the same points, drawn where they already are. On a re-centre / reframe they
    // ANIMATE from their previous positions to the new ones: a point keeps its seq and SLIDES to its new
    // place rather than teleporting — identity survives the transform (the centre freed, made visible).
    const selSeqs = new Set(sel.map(s => s.seq))
    const anim = animRef.current
    const prog = anim ? Math.min((performance.now() - anim.t0) / 480, 1) : 1
    const ease = 1 - Math.pow(1 - prog, 3)             // easeOutCubic
    const nextPos = new Map<number, { x: number; y: number }>()
    for (const p of proj.points) {
      const rr = radial(p) * R
      const tx = cx + Math.sin(p.theta) * rr, ty = cy - Math.cos(p.theta) * rr
      nextPos.set(p.seq, { x: tx, y: ty })
      let x = tx, y = ty, fade = 1
      if (anim) {
        const from = anim.from.get(p.seq)
        if (from) { x = from.x + (tx - from.x) * ease; y = from.y + (ty - from.y) * ease }
        else fade = ease                               // a point not present before fades in at its place
      }
      const hue = (p.theta * 180) / Math.PI            // color IS angle (the deliberate non-token colour)
      const chosen = selSeqs.has(p.seq)
      // a semantic point with NO vector sits at the rim, FAINT + warm-grey (meaning-distance unknown —
      // honestly shown, never silently dropped or faked as 'far').
      g.globalAlpha = (p === picked ? 1 : p.r_unknown ? 0.3 : 0.75) * fade
      g.fillStyle = p === picked ? accent : p.r_unknown ? dim : `hsl(${hue}deg 55% 58%)`
      g.beginPath(); g.arc(x, y, p === picked ? 5 : 2.1, 0, Math.PI * 2); g.fill()
      if (chosen) {  // the working set rings — what will ride into the builder
        g.globalAlpha = 0.95 * fade; g.strokeStyle = accent; g.lineWidth = 1.5
        g.beginPath(); g.arc(x, y, 6, 0, Math.PI * 2); g.stroke()
      }
    }
    posRef.current = nextPos
    // NOW — the centre, the one shared point of time. When live-at-now it BREATHES on a smooth client
    // clock (performance.now(), continuous) — the advancing present visible at the origin, not a 15s step.
    g.globalAlpha = 1; g.fillStyle = accent
    g.beginPath(); g.arc(cx, cy, 4, 0, Math.PI * 2); g.fill()
    g.strokeStyle = accent
    g.globalAlpha = 0.4; g.beginPath(); g.arc(cx, cy, 9, 0, Math.PI * 2); g.stroke()
    if (live && at == null) {  // the breath of NOW — smooth, on the client clock (a slow ~3s expand/fade)
      const phase = 0.5 + 0.5 * Math.sin(performance.now() / 1000 * 2)   // 0..1
      g.globalAlpha = 0.1 + 0.18 * phase
      g.beginPath(); g.arc(cx, cy, 11 + 6 * phase, 0, Math.PI * 2); g.stroke()
    }
    g.globalAlpha = 1
  }, [proj, picked, zoom, sel, frame, live, at])

  useEffect(() => { draw() }, [draw])
  useEffect(() => {
    const ro = new ResizeObserver(draw)
    if (wrapRef.current) ro.observe(wrapRef.current)
    return () => ro.disconnect()
  }, [draw])

  // re-centring (spatial `center` change) and reframing (now↔day↔week) ANIMATE — kick a short rAF tween
  // that re-draws while the easeOutCubic runs. drawRef keeps the trigger off the live-refresh path (so a
  // routine 15s pull doesn't jitter every point — only a deliberate transform animates).
  const drawRef = useRef(draw)
  useEffect(() => { drawRef.current = draw })

  // the LIVE CLOCK — while live-at-now, a continuous (throttled ~22fps) rAF redraws so NOW breathes
  // smoothly and SSE arrivals drift in. Stops when frozen/scrubbed (the frame goes static). This is the
  // smooth client clock that advances NOW between event-driven re-projections.
  useEffect(() => {
    if (!(live && at == null)) return
    let raf = 0, stop = false, last = 0
    const tick = (t: number) => {
      if (stop) return
      if (t - last >= 45) { drawRef.current(); last = t }
      if (animRef.current && performance.now() - animRef.current.t0 >= 480) animRef.current = null
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => { stop = true; cancelAnimationFrame(raf) }
  }, [live, at])

  // re-centring (spatial `center` change) and reframing (now↔day↔week) ANIMATE — a short easeOutCubic
  // tween. When the live clock is running it draws the tween; when frozen, kick a one-shot rAF here.
  useEffect(() => {
    if (!posRef.current.size) return
    animRef.current = { from: new Map(posRef.current), t0: performance.now() }
    if (live && at == null) return       // the live clock is already redrawing → it animates the tween
    let raf = 0
    const tick = () => {
      drawRef.current()
      if (animRef.current && performance.now() - animRef.current.t0 < 480) raf = requestAnimationFrame(tick)
      else { animRef.current = null; drawRef.current() }
    }
    raf = requestAnimationFrame(tick)
    return () => { cancelAnimationFrame(raf); animRef.current = null }
  }, [frame, center])

  const pick = (ev: { clientX: number; clientY: number }) => {
    const wrap = wrapRef.current
    if (!wrap || !proj) return
    const rect = wrap.getBoundingClientRect()
    const px = ev.clientX - rect.left, py = ev.clientY - rect.top
    const w = rect.width, h = rect.height
    const cx = w / 2, cy = h / 2, R = Math.min(w, h) / 2 - 34
    let best: ProjPoint | null = null, bd = 14 * 14
    for (const p of proj.points) {
      const rr = radial(p) * R
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

  // the time/frame label (the temporal centre) for the foot readout; the spatial centre shows as a chip
  const timeLabel = at != null ? `◷ ${relTime(at)}` : frame === 'now' ? 'now' : `cycle:${frame}`
  const centreSeg = center ? (center.split('/').filter(Boolean).slice(-1)[0] || center) : ''

  if (err) return <div className="lattice-err"><EmptyState>projection unreachable — {err}</EmptyState></div>
  return (
    <div className="lattice-wrap" ref={wrapRef} onPointerDown={pick}>
      <canvas ref={cvsRef} />
      {semanticPending && (
        <div className="lattice-hint" onPointerDown={e => e.stopPropagation()}>
          ◎ semantic lens{proj?.binding?.space ? ` · ${proj.binding.space}` : ''} — pick a centre: tap a point,
          then <b>◎ meaning-field from here</b> to rank everything by meaning-distance
        </div>
      )}
      <div className="lattice-foot">
        <span>
          <button className={'lf-live' + ((live && at == null) ? ' on' : '')}
            onClick={() => { if (at != null) { setAt(null); setLive(true) } else setLive(l => !l) }}
            onPointerDown={e => e.stopPropagation()}
            title={at != null ? 'centre scrubbed into the past — tap to return to NOW'
              : live ? 'now is advancing — tap to freeze the frame' : 'frozen — tap to follow now'}>
            {at != null ? '◷ past' : live ? '● live' : '⏸ frozen'}
          </button>
          {proj?.bindings && proj.bindings.length > 1 && (
            <select className="lf-lens" value={bind} title="the lens — which registry resolves the angle (nothing hardcoded)"
              onChange={e => setBind(e.target.value)} onPointerDown={e => e.stopPropagation()}>
              <option value="">lens: default</option>
              {proj.bindings.map(b => <option key={b.id} value={b.id}>lens: {b.label}</option>)}
            </select>
          )}
          {center && (
            <button className="lf-centred" onClick={() => { setCenter(null); setPicked(null); if (isSemantic) setBind('') }}
              onPointerDown={e => e.stopPropagation()} title={`centred on ${center} — tap to release back to NOW`}>
              {isSemantic ? '◎' : '⊙'} {centreSeg} ✕
            </button>
          )}
          {' '}{proj ? `${proj.count} pts · ${proj.n} sectors · ${timeLabel}` : 'projecting…'}
        </span>
        <div className="lattice-frames" onPointerDown={e => e.stopPropagation()}>
          {isSemantic ? (
            // THE CIRCLE active: radius is meaning-distance (not time) — the temporal controls don't apply;
            // a legible note states the reading + its honest normalization. Zoom still expands the near band.
            <span className="lf-semnote" title="radius = cosine meaning-distance from the centre item, in this lens's space">
              ◎ meaning-distance{proj?.binding?.radius_normalized ? ' · normalized' : ''}
            </span>
          ) : (
            <>
              <label className="lf-slider" title="scrub the centre back in time — NOW → the past (frozen where you let go)">
                <span className="lf-ic">⏱</span>
                <input type="range" className="lf-scrub" min={0} max={Math.round(spanRef.current)}
                  step={Math.max(Math.round(spanRef.current / 240), 1)}
                  value={at != null ? Math.min(Math.round(nowAnchorRef.current - at), Math.round(spanRef.current)) : 0}
                  onChange={e => { const back = Number(e.target.value); setPicked(null); setAt(back <= 0 ? null : Math.round(nowAnchorRef.current - back)) }} />
              </label>
              {(['now', 'day', 'week'] as const).map(fr => (
                <button key={fr} className={'lf-btn' + (frame === fr ? ' on' : '')}
                  onClick={() => setFrame(fr)}
                  title={fr === 'now' ? 'radius = time since now' : `radius = position in the ${fr} cycle`}>
                  {fr === 'now' ? '⊙ now' : fr === 'day' ? '☼ day' : '◷ week'}
                </button>
              ))}
            </>
          )}
          {(isSemantic || frame === 'now') && (
            <label className="lf-slider" title="zoom the inner band">
              <span className="lf-ic">⌕</span>
              <input type="range" className="lf-zoom" min={0.5} max={3.2} step={0.1} value={zoom}
                onChange={e => setZoom(Number(e.target.value))} onPointerDown={e => e.stopPropagation()} />
            </label>
          )}
        </div>
      </div>
      {picked && (
        <div className="lattice-card" onPointerDown={e => e.stopPropagation()}>
          <div className="lc-head">
            <Badge tone="sig">{picked.sector}</Badge>
            <Badge tone="dim">{picked.kind}</Badge>
            <button className="lc-x" onClick={() => setPicked(null)}>✕</button>
          </div>
          {picked.summary && <div className="lc-sum">{picked.summary}</div>}
          {picked.address && <div className="lc-addr">{picked.address}</div>}
          <div className="lc-meta">
            {picked.ts?.slice(0, 16).replace('T', ' · ')} · {phaseWord(picked.phases.day)} ·
            cell {picked.cell.i},{picked.cell.j} · depth {picked.cell.d}
          </div>
          <button className="lc-pick" onClick={() => toggleSel(picked)}>
            {inSel(picked) ? '− remove from set' : '＋ add to set'}
          </button>
          {picked.address && (
            <button className="lc-center" onClick={() => { setCenter(picked.address); setPicked(null) }}
              title="re-centre the projection on this address — radius becomes distance-from-here">
              ⊙ centre on this
            </button>
          )}
          {picked.source && (
            // THE CIRCLE (Group 6): only an EMBEDDED item (one with a vector) can be a meaning-centre —
            // sets the semantic lens + this item's source together, so the field always opens with a centre.
            <button className="lc-center lc-meaning"
              onClick={() => { setBind('semantic'); setCenter(picked.source!); setPicked(null) }}
              title="rank everything by MEANING-distance from this item (the circle / semantic radius)">
              ◎ meaning-field from here
            </button>
          )}
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
