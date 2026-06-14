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
  // SEPARATOR (Group 9): the two raw pulls + the signed lean toward pole B vs pole A (sign = which gravity,
  // |lean| = how strongly). `pole` is 'a' | 'b' | '—' (neutral). The FORM renders sign as the LEFT/RIGHT basin.
  pull_a?: number; pull_b?: number; lean?: number; pole?: 'a' | 'b' | '—'
  r_struct?: number       // STRAIN (Group 7): where it's FILED (structural radius); r is where it MEANS to be
  strain?: number         // |r_struct - r| — the structure↔meaning divergence (SEED §111); 0 = coherent
  // SCALE (Group 11): a coarse-rung point is a cluster CENTROID (a theme) — it carries how many units it
  // aggregates (scale_size / scale_members), a real member that NAMES it (scale_exemplar), and the finer
  // clusters that fold into it (scale_children). Absent on unit-rung points.
  scale_size?: number; scale_members?: number; scale_exemplar?: string; scale_children?: string[]
  // NUCLEATION (the 20/80 water-law): the typed-fit of this item against the registry of types. `inside` =
  // it fits a registered type (sits in the square); else it piled OUTSIDE. `fit` = its best cosine; `assigned`
  // = the nearest type; `pile_cluster` = the candidate ZONE it nucleates into; `born` = that candidate is a
  // new type; `tail` = an un-clustered pile item (hovers just outside the type it almost-fit).
  inside?: boolean; fit?: number; assigned?: string; pile_cluster?: number; born?: boolean; tail?: boolean
}
type Projection = {
  now: string; n: number; rings: number; count: number; grid?: number
  // radius_from: 'time' (age) | 'address' (tree-distance) | 'semantic' (Group 6 — meaning-distance).
  // needs_center: the semantic lens is selected but no centre chosen yet → items laid out by time, awaiting one.
  binding?: { id: string; label: string; radius_from?: string; radius_normalized?: boolean; space?: string; needs_center?: boolean
    // SEPARATOR (Group 9): the two poles resolved for this field (label + ref), echoed back so the FORM names them.
    poles?: { a: { label?: string; ref?: string }; b: { label?: string; ref?: string } } }
  bindings?: { id: string; label: string }[]
  sectors: { id: string; label: string; from: number; to: number }[]
  points: ProjPoint[]
  // SEPARATOR (Group 9) — THE FIFTH GATE rides in: whether the two-gravity field actually SEPARATES (on raw
  // cosines) + the BALANCE (how the corpus distributes between the poles). Present only in separator mode.
  separation?: {
    separates: boolean; n: number; pole_distinctness: number; distinctness_floor: number
    spread_a: number; spread_b: number; spread_floor: number; rank_corr: number
    balance: { lean_a: number; lean_b: number; neutral: number; minority_frac: number }
  }
  // THE CONNECTIONS (Group 10): the directional typed edges between sectors, as directed sector-index pairs
  // (from→to). `bidir` = a real mutual pair (a cycle, rendered as a cycle, not flattened). Drawn as directed
  // chords; absent on bindings with no edges.
  edges?: { from: number; to: number; bidir?: boolean }[]
  // SCALE LADDER (Group 11): present when the binding's space has a built pyramid. `rung` is the resolved
  // level ('unit' | a coarse k); `rungs` the available coarse cluster-counts (e.g. [8, 32]); n_units the base.
  scale?: { space: string; rung: number | string; rungs: number[]; n_units: number }
  // NUCLEATION (the 20/80 water-law): the type-birth report. membership (inside vs piled), the candidate new
  // types (margin-strength + the permutation-null verdict + born/forming), dissolution candidates, the bounded
  // pile + surfaced tail, and the dial (the 20/80 birth threshold). Present only in nucleation mode.
  nucleation?: {
    n_items: number; n_types: number; membership: { inside: number; pile: number }
    pile_total: number; pile_clustered: number; pile_tail: number
    dial: number; birth_mass: number; median_type_size: number
    born_count: number; distinct_count: number
    candidates: { size: number; margin: number; null_p95: number; distinct: boolean; born: boolean
      birth_mass: number; exemplar: string; members: string[] }[]
    dissolution_candidates: { type: string; size: number; note: string }[]
    type_labels: string[]; type_sizes: number[]
    zones: { id: string; exemplar: string; born: boolean; distinct: boolean; size: number }[]
    types_space?: string
    // registry-true picker options resolved by the bridge (no FE hardcode — new stores/pyramids appear here)
    available?: { item_spaces: string[]; types_spaces: string[]; rungs: number[] }
  }
}

export default function LatticeView({ onHandoff }: { onHandoff?: () => void }) {
  const wrapRef = useRef<HTMLDivElement | null>(null)
  const cvsRef = useRef<HTMLCanvasElement | null>(null)
  const [proj, setProj] = useState<Projection | null>(null)
  const [picked, setPicked] = useState<ProjPoint | null>(null)
  const [pickedSector, setPickedSector] = useState<number | null>(null)  // G10 connections: the driven row (its in/out edges light up)
  const [sel, setSel] = useState<ProjPoint[]>([])   // the accumulating working set (forager: sculpt → hand to builder)
  const [zoom, setZoom] = useState(1)        // radial magnification — inner rings (recent) expand
  const [rung, setRung] = useState<number | null>(null)  // G11 SCALE: null/unit = items; a coarse k = themes
  const [frame, setFrame] = useState<'now' | 'day' | 'week'>('now')  // S4: scale/phase selects the frame
  const [showStrain, setShowStrain] = useState(false)  // G7: overlay the structure↔meaning tension lines
  const [bind, setBind] = useState<string>('')   // the LENS (binding id); '' = the data-driven default
  const [err, setErr] = useState('')
  const [retry, setRetry] = useState(0)          // a retry NONCE — bump it to re-fire the fetch effect with the
                                                  // SAME params (the error view's ↻ retry; recovers a transient
                                                  // failure without a page reload — the G4 robustness dead-end fix)
  const [live, setLive] = useState(true)     // the centre is NOW — and now MOVES (the involuntary axis)
  const [at, setAt] = useState<number | null>(null)          // S/G3 time scrubber — epoch secs (null = live NOW)
  const [center, setCenter] = useState<string | null>(null)  // S/G3 spatial re-centre — an address (null = temporal NOW)
  // SEPARATOR (Group 9): the two driven poles (null = the binding's declared default poles). Picking a point as
  // a pole re-drives the field; the OTHER pole is always kept (the bridge fails loud on a one-pole field).
  const [poleA, setPoleA] = useState<string | null>(null)
  const [poleB, setPoleB] = useState<string | null>(null)
  // NUCLEATION (the 20/80 water-law): the two VARIABLE axes the operator drives — the registry of types
  // (typesSpace) and the content store typed against it (itemSpace) — plus the 20/80 BIRTH dial (null = the
  // binding's defaults). Driving any of them re-reads where new types want to be born; the law is universal,
  // so every embedded store can be a registry OR the content (cross-instance keeps the misfit non-circular).
  const [typesSpace, setTypesSpace] = useState<string | null>(null)
  const [itemSpace, setItemSpace] = useState<string | null>(null)
  const [dial, setDial] = useState<number | null>(null)
  const nowAnchorRef = useRef(Date.now() / 1000)             // the live "now" epoch — the scrub-math anchor
  const spanRef = useRef(86400)                              // seconds the scrubber spans (the visible age range)
  const posRef = useRef<Map<number, { x: number; y: number }>>(new Map())   // last drawn point positions (identity)
  const animRef = useRef<{ from: Map<number, { x: number; y: number }>; t0: number } | null>(null)
  // G11 CROSSFADE: a rung change swaps the WHOLE point-set (themes↔units, no shared seqs), so the position
  // tween can't carry identity across it. To make it read as a CONTINUOUS scale move (not a hard mode-switch),
  // the OUTGOING rung's points fade OUT (departRef) at their last positions while the incoming fade IN. The
  // last drawn frame is held so the departure has something to render. (advisor: crossfade the rung boundary.)
  const lastFrameRef = useRef<{ points: ProjPoint[]; pos: Map<number, { x: number; y: number }> } | null>(null)
  const departRef = useRef<{ points: ProjPoint[]; pos: Map<number, { x: number; y: number }>; t0: number } | null>(null)
  const prevRungRef = useRef<number | string | undefined>(undefined)
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
  // SEPARATOR (Group 9 — the two-gravity field): radius = |lean| (neutral at centre, strong lean at the rim),
  // and the SIGN is the LEFT/RIGHT BASIN (pole A fans left, pole B fans right) — the two gravities as two
  // spatial basins, not two colours (sign must be load-bearing geometry, not decoration). Within each basin the
  // kind-angle spreads the items so they don't stack. The two gravity hues reinforce the split.
  const isSeparator = proj?.binding?.radius_from === 'separator'
  // NUCLEATION (the 20/80 water-law — type-birth): the registry's types are sectors INSIDE the box (what
  // fits); what does NOT fit piles up OUTSIDE the box, and a distinct coherent pile is a CANDIDATE NEW TYPE
  // forming in its own outer zone. radius p.r < 1 = inside the square, p.r > 1 = piled outside it.
  const isNucleation = proj?.binding?.radius_from === 'nucleation'
  const SEP_HUE_A = 212, SEP_HUE_B = 28                       // cool A (left) / warm B (right) — colour IS pole
  const sepColA = `hsl(${SEP_HUE_A}deg 55% 60%)`, sepColB = `hsl(${SEP_HUE_B}deg 62% 56%)`
  const SEP_SPREAD = Math.PI * 0.6                             // each basin fans ~108° around its pole axis
  // basin angle: pole B → right (axis +π/2), pole A → left (axis 3π/2), neutral → top (0). within-basin angle
  // from the kind-theta so items fan out. MUST be used identically by draw() AND pick() (else clicks miss).
  const sepTheta = (p: ProjPoint) => {
    const base = p.pole === 'b' ? Math.PI / 2 : p.pole === 'a' ? (3 * Math.PI) / 2 : 0
    if (p.pole !== 'a' && p.pole !== 'b') return base          // neutral sits on the top axis, near the centre
    return base + ((p.theta / (Math.PI * 2)) - 0.5) * SEP_SPREAD
  }
  // a pole's display name: a friendly binding label is kept; an address (a driven pole) shows its tail segments
  // so the readout never paints a full vec://… address (or, worse, a stale default label for a driven pole).
  const poleLabel = (s?: string) => !s ? 'pole' : !s.includes('://') ? s : s.split('/').filter(Boolean).slice(-2).join('/')
  // NUCLEATION geometry (used IDENTICALLY by draw() and pick() — else clicks land wrong): the registry box is
  // inscribed at R_BOX_FRAC·R; an item that FITS sits inside it (r<1 → r·R_BOX); a piled item sits OUTSIDE it
  // (r>1 → pushed past the box, amplified so the candidate blooms read clear of the box edge). Returns a FRACTION
  // of R (the caller multiplies by R). A short tail segment of an address for the candidate-zone labels.
  // the box is inscribed at R_BOX_FRAC·R (corner at ×1.41 → 0.71·R); a FIT sits inside it (r·R_BOX), a PILE
  // sits CLEARLY OUTSIDE it — beyond the box corner — so "piles up outside the square" is literally true (not
  // in the corner triangles, which would read as inside). Pile band [0.74, 0.90]·R; the candidate blooms/labels
  // live further out at the rim (drawn in draw()). Returns a FRACTION of R.
  const R_BOX_FRAC = 0.5
  const nucRadius = (p: ProjPoint) => p.inside
    ? p.r * R_BOX_FRAC
    : Math.min(0.74 + Math.max(p.r - 1, 0) * 0.9, 0.90)
  const shortName = (s?: string) => !s ? '' : (s.split('/').filter(Boolean).slice(-1)[0] || s).replace(/\.(py|tsx?|md|json)$/, '')
  // SCALE LADDER (Group 11): the rungs fine→coarse = [units, …coarse k descending]. finerRung steps one
  // level IN (coarse k → finer k → units) — the zoom-INTO-a-theme gesture. Distinct from the radial ⌕ zoom
  // (magnify the band) — this changes which RUNG resolves (themes vs units), the advisor's collision avoided.
  const scaleRungs = proj?.scale ? [...proj.scale.rungs].sort((a, b) => b - a) : []   // coarse→fine: [32, 8]→[32,8]
  const ladderCoarseToFine: (number | null)[] = proj?.scale ? [...[...proj.scale.rungs].sort((a, b) => a - b), null] : [null]
  const finerRung = (k: number | null) => {
    const i = ladderCoarseToFine.indexOf(k)
    return i >= 0 && i < ladderCoarseToFine.length - 1 ? ladderCoarseToFine[i + 1] : null
  }
  // S4 — frame-relativity (Tim: "the axes are variables too — scale and state/phase select the
  // frame"). 'now' = radius is age-from-NOW (the default arrow of time). 'day'/'week' = radius is
  // the timestamp's CYCLE coordinate, so the daily/weekly rhythm becomes visible: everything that
  // happened "at 9am" lands on one ring regardless of which day — the cycles, made geometry.
  const radial = (p: ProjPoint) =>
    (isSemantic || isSeparator || isNucleation || frame === 'now') ? Math.pow(p.r, 1 / zoom) : frame === 'day' ? p.phases.day : p.phases.week

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
    if (rung != null) params.set('rung', String(rung))  // G11 SCALE: resolve over the rung's THEMES, not units
    if (poleA) params.set('pole_a', poleA)              // G9 SEPARATOR: drive the two gravities (null = the
    if (poleB) params.set('pole_b', poleB)              // binding's declared default poles)
    if (typesSpace) params.set('types_space', typesSpace)  // NUCLEATION: drive the registry of types …
    if (itemSpace) params.set('space', itemSpace)          // … and the content store typed against it.
    // the 20/80 BIRTH dial is NOT sent — it only gates born (= distinct AND size ≥ birth_mass) and the server
    // already returns size/distinct/pile_clustered, so born is recomputed CLIENT-SIDE → the dial is INSTANT
    // (no compute-heavy refetch per tick; the critic's ~5s dial lag fix). Registry/store/rung still refetch.
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
  }, [live, bind, at, center, rung, poleA, poleB, typesSpace, itemSpace, retry])  // dial omitted — client-side, instant

  // SCALE (Group 11): if the active projection has no pyramid (a non-semantic lens, or a space with no
  // built rungs), drop any held rung so the ladder + state stay honest (the bridge ignores a stray rung,
  // but the UI shouldn't claim a coarse level that isn't rendered).
  useEffect(() => { if (proj && !proj.scale && rung != null) setRung(null) }, [proj, rung])
  // G10 connections: clear the driven row when the active projection has no edges (left the connections view)
  useEffect(() => { if (proj && !(proj.edges && proj.edges.length) && pickedSector != null) setPickedSector(null) }, [proj, pickedSector])
  // G9 separator: drop the driven poles when the active lens is NOT a separator (so they don't leak into another
  // lens — the next time the separator lens opens it starts from its declared default poles).
  useEffect(() => { if (proj && !isSeparator && (poleA || poleB)) { setPoleA(null); setPoleB(null) } }, [proj, isSeparator, poleA, poleB])
  // leaving the nucleation lens clears its driven axes (so a stale types_space/dial can't ride into another lens)
  useEffect(() => { if (proj && !isNucleation && (typesSpace || itemSpace || dial != null)) { setTypesSpace(null); setItemSpace(null); setDial(null) } }, [proj, isNucleation, typesSpace, itemSpace, dial])

  // G11 CROSSFADE: when the resolved RUNG changes (the point-set swaps wholesale), snapshot the just-drawn
  // frame as the DEPARTING set so draw() can fade it out while the new rung fades in (continuous scale move).
  useEffect(() => {
    const rg = proj?.scale?.rung
    if (proj && prevRungRef.current !== undefined && rg !== prevRungRef.current && lastFrameRef.current) {
      departRef.current = { points: lastFrameRef.current.points, pos: lastFrameRef.current.pos, t0: performance.now() }
    }
    prevRungRef.current = rg
  }, [proj])

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

    // NUCLEATION (the 20/80 water-law) — a self-contained face: the registry of types is the SQUARE; what fits
    // sits INSIDE it, what does not piles up OUTSIDE, and a distinct coherent pile blooms into a CANDIDATE NEW
    // TYPE in its own outer zone (geometrically faithful to Tim: "won't fit inside the square → pile up
    // outside"). Drawn instead of the time/semantic/separator wheel — the radius crosses the box boundary here.
    if (isNucleation && proj.nucleation) {
      const nu = proj.nucleation
      const Rb = R * R_BOX_FRAC
      const sectors = proj.sectors
      const nTypes = nu.type_labels.length
      type NucZone = (typeof nu.zones)[number]
      const zoneById = new Map<string, NucZone>(nu.zones.map(z => [z.id, z]))
      // CLIENT-SIDE born (the dial is instant — no refetch): a zone is BORN when distinct AND its mass passes
      // the 20/80 birth threshold = dial × the examined pile. Recolours the blooms the moment the dial moves.
      const dialV = dial ?? nu.dial
      const birthMass = Math.max(3, Math.round(dialV * Math.max(nu.pile_clustered, 1)))
      const born = (z: NucZone) => z.distinct && z.size >= birthMass
      // 1) THE REGISTRY BOX (the square) — the container of the registered types; the inscribed circle marks the
      //    membership boundary (inside = within a type's reach). The brightest structural line (warm grey --tx-3).
      g.strokeStyle = dim; g.globalAlpha = 0.85; g.lineWidth = 1.5; g.strokeRect(cx - Rb, cy - Rb, 2 * Rb, 2 * Rb)
      g.strokeStyle = line; g.globalAlpha = 0.4; g.lineWidth = 1
      g.beginPath(); g.arc(cx, cy, Rb, 0, Math.PI * 2); g.stroke()
      // 2) TYPE SECTORS inside the box — faint spokes + labels at the box edge (the registered types, thinned by
      //    member-share if many). The ✦ candidate zones are drawn as blooms OUTSIDE the box (step 4).
      g.font = '10px ui-monospace, monospace'; g.textAlign = 'center'
      const typeShare = new Map<string, number>()
      for (const p of proj.points) if (p.inside) typeShare.set(p.sector, (typeShare.get(p.sector) || 0) + 1)
      const labelledTypes = new Set([...typeShare.entries()].sort((a, b) => b[1] - a[1])
        .slice(0, nTypes <= 10 ? nTypes : 8).map(e => e[0]))
      for (let i = 0; i < nTypes && i < sectors.length; i++) {
        const s = sectors[i], mid = (s.from + s.to) / 2
        g.strokeStyle = line; g.globalAlpha = 0.22
        g.beginPath(); g.moveTo(cx, cy); g.lineTo(cx + Math.sin(s.from) * Rb, cy - Math.cos(s.from) * Rb); g.stroke()
        if (labelledTypes.has(s.id)) {
          const lr = Rb - 12, lx = cx + Math.sin(mid) * lr, ly = cy - Math.cos(mid) * lr + 3
          const t = shortName(s.label), tw = g.measureText(t).width
          g.globalAlpha = 0.78; g.fillStyle = bg; g.fillRect(lx - tw / 2 - 2, ly - 9, tw + 4, 12)
          g.globalAlpha = 0.85; g.fillStyle = dim; g.fillText(t, lx, ly)
        }
      }
      // 3) THE POINTS — inside (fits) within the box, coloured by the angle-hue (the deliberate colour-IS-geometry
      //    exception, consistent with every other lens); piled OUTSIDE — the tail hugs the box (dim), candidate
      //    members bloom further out coloured by STATE (born = accent gold, forming = ink, absorbed = dim). The
      //    picked point reads gold + larger. Identity stored in posRef so pick() finds the same point.
      const selSeqsN = new Set(sel.map(s => s.seq))
      const posN = new Map<number, { x: number; y: number }>()
      for (const p of proj.points) {
        const rr = nucRadius(p) * R
        const x = cx + Math.sin(p.theta) * rr, y = cy - Math.cos(p.theta) * rr
        posN.set(p.seq, { x, y })
        let col = dim, alpha = 0.32, rad = 1.8
        if (p === picked) { col = accent; alpha = 1; rad = 4 }
        else if (p.inside) { col = `hsl(${(p.theta * 180) / Math.PI}deg 55% 58%)`; alpha = 0.82; rad = 2.0 }
        else if (p.pile_cluster != null) {
          const z = zoneById.get(p.sector)
          if (z && born(z)) { col = accent; alpha = 0.92; rad = 2.6 }
          else if (z?.distinct) { col = ink; alpha = 0.72; rad = 2.2 }
          else { col = dim; alpha = 0.5; rad = 2.0 }
        }                                                    // else: tail (un-clustered pile) — dim, hugging box
        g.globalAlpha = alpha; g.fillStyle = col
        g.beginPath(); g.arc(x, y, rad, 0, Math.PI * 2); g.fill()
        if (selSeqsN.has(p.seq)) {
          g.globalAlpha = 0.95; g.strokeStyle = accent; g.lineWidth = 1.5
          g.beginPath(); g.arc(x, y, rad + 3, 0, Math.PI * 2); g.stroke()
        }
      }
      posRef.current = posN
      // 4) CANDIDATE ZONES (the new types forming outside) — a ✦ marker + exemplar at each zone's outer angle, an
      //    arc bracket marking its angular region beyond the box; BORN reads bright "✦", forming reads ink,
      //    absorbed reads faint. The 20/80 made visible: a region that filled past the dial is a NEW TYPE.
      g.font = '10px ui-monospace, monospace'
      for (const z of nu.zones) {
        const si = sectors.findIndex(s => s.id === z.id); if (si < 0) continue
        const s = sectors[si], mid = (s.from + s.to) / 2
        const zborn = born(z)
        const col = zborn ? accent : z.distinct ? ink : dim
        g.globalAlpha = zborn ? 0.55 : z.distinct ? 0.3 : 0.16; g.strokeStyle = col; g.lineWidth = zborn ? 2.2 : 1
        g.beginPath(); g.arc(cx, cy, R * 0.95, s.from - Math.PI / 2, s.to - Math.PI / 2); g.stroke()  // the bloom's arc, at the rim (clear of the pile band)
        const lr = R * 0.99, lx = cx + Math.sin(mid) * lr, ly = cy - Math.cos(mid) * lr + 3
        const cap = (str: string) => str.length > 15 ? str.slice(0, 14) + '…' : str
        const tag = (zborn ? '✦ ' : '') + cap(shortName(z.exemplar))
        const align: CanvasTextAlign = Math.sin(mid) >= -0.05 ? 'left' : 'right'
        g.textAlign = align
        const tw = g.measureText(tag).width
        // EDGE-AWARE CLAMP (critic fix): keep the whole label box within [pad, w-pad] so a left-rim candidate
        // name never runs off a narrow viewport (the mobile 390px clip — the born type's name must stay readable).
        const pad = 5
        let px = lx, left = align === 'left' ? px : px - tw
        if (left < pad) { px += pad - left; left = pad }
        if (left + tw > w - pad) { px -= (left + tw) - (w - pad); left = w - pad - tw }
        g.globalAlpha = 0.8; g.fillStyle = bg
        g.fillRect(left - 3, ly - 9, tw + 6, 13)
        g.globalAlpha = zborn ? 1 : z.distinct ? 0.8 : 0.5; g.fillStyle = col; g.fillText(tag, px, ly)
      }
      // 5) the centre — a neutral registry origin (NOT the breathing NOW; nucleation has no temporal centre) +
      //    a quiet radial legend so the reading is unambiguous (in = fits, out = piles into a new type).
      g.globalAlpha = 0.5; g.fillStyle = dim; g.beginPath(); g.arc(cx, cy, 3, 0, Math.PI * 2); g.fill()
      g.globalAlpha = 0.55; g.fillStyle = dim; g.font = '9px ui-monospace, monospace'; g.textAlign = 'left'
      g.fillText('inside = fits a type · outside = piles → new type', cx - Rb, cy - R + 12)
      g.globalAlpha = 1
      return
    }

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
    const axisLabels: [number, string][] = (proj.edges && proj.edges.length)
      ? []                                             // CONNECTIONS: radius is a placeholder — no radial axis label (it would mislead + collide with the rim labels)
      : isSeparator
      ? [[1, 'stronger lean →']]                       // SEPARATOR: radius = |lean| (centre = neutral, rim = strong)
      : isSemantic
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
    // THE CONNECTIONS (Group 10 — "the connections in the registries"): the directional typed edges drawn as
    // directed CHORDS between sectors. Each chord bows toward the centre (a chord-diagram arc, readable — not
    // a straight overlap) with an arrowhead at its TARGET (direction); a bidir edge (a real mutual cycle) gets
    // a head at BOTH ends (rendered AS a cycle, never flattened). DRIVE-TO-EXPLORE: pick a sector → its OUT
    // edges light gold, its IN edges light ink, the rest fade — you walk the registry by its real relations.
    const conn = proj.edges || []
    if (conn.length) {
      const secMid = (i: number) => { const s = proj.sectors[i]; return (s.from + s.to) / 2 }
      const ptAt = (ang: number, rho: number) => ({ x: cx + Math.sin(ang) * rho, y: cy - Math.cos(ang) * rho })
      const rim = R * 0.9
      const head = (tipx: number, tipy: number, fromx: number, fromy: number, sz: number) => {
        const a = Math.atan2(tipy - fromy, tipx - fromx)
        g.beginPath(); g.moveTo(tipx, tipy)
        g.lineTo(tipx - sz * Math.cos(a - 0.42), tipy - sz * Math.sin(a - 0.42))
        g.lineTo(tipx - sz * Math.cos(a + 0.42), tipy - sz * Math.sin(a + 0.42))
        g.closePath(); g.fill()
      }
      g.lineCap = 'round'
      for (const e of conn) {
        if (e.from >= proj.sectors.length || e.to >= proj.sectors.length) continue
        const a = ptAt(secMid(e.from), rim), b = ptAt(secMid(e.to), rim)
        const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2
        const ctrl = { x: cx + (mx - cx) * 0.26, y: cy + (my - cy) * 0.26 }   // bow toward centre
        const incident = pickedSector != null && (e.from === pickedSector || e.to === pickedSector)
        const isOut = pickedSector != null && e.from === pickedSector
        let alpha: number, lw: number, col: string
        if (pickedSector == null) { alpha = 0.15; lw = 1; col = dim }
        else if (incident) { alpha = 0.92; lw = 1.7; col = isOut ? accent : ink }
        else { alpha = 0.05; lw = 1; col = dim }
        g.globalAlpha = alpha; g.strokeStyle = col; g.lineWidth = lw
        g.beginPath(); g.moveTo(a.x, a.y); g.quadraticCurveTo(ctrl.x, ctrl.y, b.x, b.y); g.stroke()
        if (pickedSector == null || incident) {
          const sz = incident ? 7 : 4.5
          g.fillStyle = col; g.globalAlpha = Math.min(alpha + 0.1, 1)
          head(b.x, b.y, ctrl.x, ctrl.y, sz)               // arrowhead at the target (direction)
          if (e.bidir) head(a.x, a.y, ctrl.x, ctrl.y, sz)  // a real cycle → a head at the source too
        }
      }
      g.globalAlpha = 1; g.lineWidth = 1
      // the PICKED sector's wedge, lit faintly so the driven row reads (the connections fan from here)
      if (pickedSector != null && pickedSector < proj.sectors.length) {
        const s = proj.sectors[pickedSector]
        g.globalAlpha = 0.1; g.fillStyle = accent
        g.beginPath(); g.moveTo(cx, cy)
        g.arc(cx, cy, R, s.from - Math.PI / 2, s.to - Math.PI / 2); g.closePath(); g.fill()
        g.globalAlpha = 1
      }
    }
    // SEPARATOR (Group 9): the two GRAVITY BASINS — a faint vertical NEUTRAL DIVIDE through the centre, and the
    // two poles marked + NAMED at the left rim (A) and right rim (B). The basins fan the points left vs right, so
    // the SEPARATION is spatial (two regions you can SEE), not two interleaved colours. Drawn instead of the
    // kind-wedges (the angle here is the sign-basin, not the kind-sector, so kind boundaries would mislead).
    if (isSeparator) {
      const pls = proj.binding?.poles
      g.strokeStyle = dim; g.globalAlpha = 0.32; g.lineWidth = 1; g.setLineDash([4, 5])
      g.beginPath(); g.moveTo(cx, cy - R); g.lineTo(cx, cy + R); g.stroke(); g.setLineDash([])
      g.font = '11px ui-monospace, monospace'
      // a SHORT rim tag (first segment, capped) — the FULL pole name lives in the card. ANCHORED at the rim
      // (left tag left-aligned just inside the left rim, right tag right-aligned just inside the right rim) so a
      // long name can never be pulled toward the centre and collide over the cluster (the 390px critic FAIL).
      const rimTag = (s: string) => { const seg = (s.split(/\s*\/\s*/)[0] || s).trim(); return seg.length > 14 ? seg.slice(0, 13) + '…' : seg }
      const poleMark = (col: string, side: -1 | 1, label: string) => {
        const mx = cx + side * R
        g.fillStyle = col; g.strokeStyle = col
        g.globalAlpha = 0.9; g.beginPath(); g.arc(mx, cy, 5, 0, Math.PI * 2); g.fill()
        g.globalAlpha = 0.3; g.lineWidth = 1; g.beginPath(); g.arc(mx, cy, 10, 0, Math.PI * 2); g.stroke()
        g.textAlign = side < 0 ? 'left' : 'right'
        const words = rimTag(label), tw = g.measureText(words).width
        const tx = mx - side * 12, ty = cy - 16                       // 12px inside the rim, reading inward
        const px0 = (side < 0 ? tx : tx - tw) - 3
        g.globalAlpha = 0.82; g.fillStyle = bg; g.fillRect(px0, ty - 10, tw + 6, 14)
        g.globalAlpha = 1; g.fillStyle = col; g.fillText(words, tx, ty)
      }
      poleMark(sepColA, -1, poleLabel(pls?.a?.label) || 'pole A')
      poleMark(sepColB, 1, poleLabel(pls?.b?.label) || 'pole B')
      g.globalAlpha = 1
    }
    // The sector boundaries + labels (the angular type divisions — the registry drawn). Skipped in separator
    // mode (the angle is the sign-basin there, not the kind-wedge).
    if (!isSeparator) {
    g.globalAlpha = 0.5
    for (const s of proj.sectors) {
      g.beginPath(); g.moveTo(cx, cy)
      g.lineTo(cx + Math.sin(s.from) * R, cy - Math.cos(s.from) * R); g.stroke()
    }
    g.font = '11px ui-monospace, monospace'; g.textAlign = 'center'
    const inside = w < 520            // phone face: labels tuck inside the rim (no edge clipping)
    // Label-thinning: the data-driven default can resolve many sectors (e.g. 50 raw kinds). Painting
    // every label would betray the default for legibility — so label only the MAJOR sectors (by
    // point-share), the rest read by colour/position. In CONNECTIONS mode every row is named (you must
    // read which node connects to which), so the whole registry is labelled.
    const perSector = new Map<string, number>()
    for (const p of proj.points) perSector.set(p.sector, (perSector.get(p.sector) || 0) + 1)
    const labelled = conn.length
      ? new Set(proj.sectors.map(s => s.id))
      : new Set([...perSector.entries()].sort((a, b) => b[1] - a[1])
          .slice(0, proj.sectors.length <= 12 ? proj.sectors.length : 10).map(e => e[0]))
    for (let si = 0; si < proj.sectors.length; si++) {
      const s = proj.sectors[si]
      if (!labelled.has(s.id)) continue
      const mid = (s.from + s.to) / 2
      // CONNECTIONS labels EVERY row, so near-vertical neighbours collide on a narrow face — stagger adjacent
      // labels by radius (parity) so they never share a baseline (the wordcount/codebase overprint fix).
      const stagger = conn.length ? (si % 2 === 0 ? 0 : (inside ? -13 : 15)) : 0
      const lr = (inside ? R - 14 : R + 16) + stagger
      const lx = cx + Math.sin(mid) * lr, ly = cy - Math.cos(mid) * lr + 4
      const tw = g.measureText(s.label).width
      g.globalAlpha = 0.82; g.fillStyle = bg   // backing plate so labels read over dense arcs
      g.fillRect(lx - tw / 2 - 3, ly - 10, tw + 6, 14)
      // the picked row's label reads gold; its direct connections stay ink; the rest dim in connections mode
      g.globalAlpha = 1
      g.fillStyle = (conn.length && pickedSector === si) ? accent
        : (conn.length && pickedSector != null) ? dim : ink
      g.fillText(s.label, lx, ly)
    }
    }   // end !isSeparator (sector boundaries + labels)
    // The points — exactly the same points, drawn where they already are. On a re-centre / reframe they
    // ANIMATE from their previous positions to the new ones: a point keeps its seq and SLIDES to its new
    // place rather than teleporting — identity survives the transform (the centre freed, made visible).
    // STRAIN overlay (Group 7, SEED §111): for each point a RADIAL tension segment from where it's FILED
    // (r_struct) to where it MEANS to be (r), at the point's angle — "the line between where a thing is
    // filed and where it means to be." alpha ∝ strain, so coherent points (segment≈0) vanish and only real
    // divergence reads as visible tension. Drawn UNDER the points. Semantic mode + the toggle only.
    if (isSemantic && showStrain) {
      g.strokeStyle = accent; g.lineCap = 'round'
      for (const p of proj.points) {
        if (p.strain == null || p.r_struct == null || p.strain < 0.02) continue
        const rm = Math.pow(p.r, 1 / zoom) * R, rs = Math.pow(p.r_struct, 1 / zoom) * R
        const sn = Math.sin(p.theta), cs = Math.cos(p.theta)
        g.globalAlpha = 0.12 + 0.6 * Math.min(p.strain, 1)      // faint→strong with the gap
        g.lineWidth = 0.6 + 1.4 * Math.min(p.strain, 1)
        g.beginPath(); g.moveTo(cx + sn * rs, cy - cs * rs); g.lineTo(cx + sn * rm, cy - cs * rm); g.stroke()
      }
      g.globalAlpha = 1; g.lineWidth = 1
    }
    const selSeqs = new Set(sel.map(s => s.seq))
    const anim = animRef.current
    const prog = anim ? Math.min((performance.now() - anim.t0) / 480, 1) : 1
    const ease = 1 - Math.pow(1 - prog, 3)             // easeOutCubic
    const nextPos = new Map<number, { x: number; y: number }>()
    // SCALE (Group 11): a coarse rung's points are THEMES (cluster centroids). A theme's dot is SIZED by how
    // many units it aggregates (area ∝ members → bigger theme reads bigger) so going coarse visibly fuses the
    // field; the biggest themes get a label (their exemplar — a real unit that names the theme), thinned by
    // size so a 32-theme rung stays legible. dotR(p): a theme scales with √members; a unit stays the fixed 2.1.
    const isThemeFrame = proj.points.some(p => p.scale_size != null)
    const dotR = (p: ProjPoint) => p.scale_size != null ? 3 + Math.sqrt(p.scale_size) * 1.15 : 2.1
    // G11 CROSSFADE: the OUTGOING rung's points fade out at their last positions (under the incoming set), so
    // a rung step reads as one continuous scale move rather than a blank-then-snap. Cleared when the fade ends.
    const dep = departRef.current
    if (dep) {
      const dprog = Math.min((performance.now() - dep.t0) / 480, 1)
      if (dprog >= 1) { departRef.current = null }
      else {
        const dease = 1 - Math.pow(1 - dprog, 3)
        for (const p of dep.points) {
          const pos = dep.pos.get(p.seq); if (!pos) continue
          const hue = (p.theta * 180) / Math.PI
          const drad = p.scale_size != null ? 3 + Math.sqrt(p.scale_size) * 1.15 : 2.1
          g.globalAlpha = (1 - dease) * 0.5
          g.fillStyle = p.r_unknown ? dim : `hsl(${hue}deg 55% 58%)`
          g.beginPath(); g.arc(pos.x, pos.y, drad, 0, Math.PI * 2); g.fill()
        }
        g.globalAlpha = 1
      }
    }
    const themeLabelled = isThemeFrame
      ? new Set([...proj.points].sort((a, b) => (b.scale_size || 0) - (a.scale_size || 0))
          .slice(0, proj.points.length <= 10 ? proj.points.length : 8).map(p => p.seq))
      : new Set<number>()
    const themeLabels: { x: number; y: number; rad: number; t: string; a: number; isCentre: boolean }[] = []
    for (const p of proj.points) {
      const rr = radial(p) * R
      const pth = isSeparator ? sepTheta(p) : p.theta   // SEPARATOR: angle is the sign-basin (MUST match pick())
      const tx = cx + Math.sin(pth) * rr, ty = cy - Math.cos(pth) * rr
      nextPos.set(p.seq, { x: tx, y: ty })
      let x = tx, y = ty, fade = 1
      if (anim) {
        const from = anim.from.get(p.seq)
        if (from) { x = from.x + (tx - from.x) * ease; y = from.y + (ty - from.y) * ease }
        else fade = ease                               // a point not present before fades in at its place
      }
      // colour IS the angle-hue (the deliberate non-token colour) — EXCEPT in separator mode, where colour IS
      // the POLE (the two gravity hues), reinforcing the left/right basin so the sign reads doubly.
      const sepCol = p.pole === 'b' ? sepColB : p.pole === 'a' ? sepColA : dim
      const hue = (p.theta * 180) / Math.PI
      const baseCol = isSeparator ? sepCol : `hsl(${hue}deg 55% 58%)`
      const chosen = selSeqs.has(p.seq)
      const rad = p === picked ? dotR(p) + 2.4 : dotR(p)
      // a semantic point with NO vector sits at the rim, FAINT + warm-grey (meaning-distance unknown —
      // honestly shown, never silently dropped or faked as 'far').
      g.globalAlpha = (p === picked ? 1 : p.r_unknown ? 0.3 : 0.75) * fade
      g.fillStyle = p === picked ? accent : p.r_unknown ? dim : baseCol
      g.beginPath(); g.arc(x, y, rad, 0, Math.PI * 2); g.fill()
      // a theme reads as a soft disc (a region, not a point): a faint halo ring at its scaled radius
      if (p.scale_size != null && p !== picked) {
        g.globalAlpha = 0.28 * fade; g.strokeStyle = `hsl(${hue}deg 55% 58%)`; g.lineWidth = 1
        g.beginPath(); g.arc(x, y, rad + 2.5, 0, Math.PI * 2); g.stroke()
      }
      if (themeLabelled.has(p.seq) && p.scale_exemplar) {
        const t = String(p.scale_exemplar).split('/').filter(Boolean).slice(-1)[0] || ''
        // carry the disc geometry so the label pass can place collision-free; the CENTRED theme (r=0) sits on
        // the NOW marker, so its label is skipped (the centre is already marked + named in the card).
        themeLabels.push({ x, y, rad, t, a: fade, isCentre: p.r === 0 })
      }
      if (chosen) {  // the working set rings — what will ride into the builder
        g.globalAlpha = 0.95 * fade; g.strokeStyle = accent; g.lineWidth = 1.5
        g.beginPath(); g.arc(x, y, rad + 3.5, 0, Math.PI * 2); g.stroke()
      }
    }
    // theme labels last (over the dots), COLLISION-RESOLVED so none is ever overprinted by a disc, another
    // label, or the centre marker (the critic's focal-centre defect). Biggest themes get first pick of space;
    // each tries above→below→right→left of its disc; a label with no clear slot is DROPPED (declutter — fewer
    // legible labels beat an illegible pile). The NOW centre marker box is reserved up front.
    if (themeLabels.length) {
      g.font = '10px ui-monospace, monospace'; g.textAlign = 'center'
      const placed: { x0: number; y0: number; x1: number; y1: number }[] = [{ x0: cx - 16, y0: cy - 16, x1: cx + 16, y1: cy + 16 }]
      const hits = (b: { x0: number; y0: number; x1: number; y1: number }) =>
        placed.some(q => !(b.x1 < q.x0 || b.x0 > q.x1 || b.y1 < q.y0 || b.y0 > q.y1))
      for (const L of [...themeLabels].sort((a, b) => b.rad - a.rad)) {
        if (L.isCentre) continue                       // the centred theme is the marked centre — no label pile-up
        const tw = g.measureText(L.t).width, hw = tw / 2 + 3
        const cands: [number, number][] = [
          [L.x, L.y - L.rad - 9], [L.x, L.y + L.rad + 13],     // above / below the disc
          [L.x + L.rad + hw + 2, L.y + 1], [L.x - L.rad - hw - 2, L.y + 1]]   // right / left
        let box: { x0: number; y0: number; x1: number; y1: number } | null = null
        let px = 0, py = 0
        for (const [qx, qy] of cands) {
          const b = { x0: qx - hw, y0: qy - 10, x1: qx + hw, y1: qy + 4 }
          if (!hits(b)) { box = b; px = qx; py = qy; break }
        }
        if (!box) continue                             // no clear slot → drop it (declutter, never overprint)
        placed.push(box)
        g.globalAlpha = 0.8 * L.a; g.fillStyle = bg; g.fillRect(box.x0, box.y0, box.x1 - box.x0, box.y1 - box.y0)
        g.globalAlpha = L.a; g.fillStyle = ink; g.fillText(L.t, px, py + 1)
      }
    }
    posRef.current = nextPos
    lastFrameRef.current = { points: proj.points, pos: nextPos }   // held for the next rung crossfade (departRef)
    if (isSeparator) {
      // SEPARATOR: the centre is NEUTRAL (least-leaning), NOT the advancing present — so it must NOT breathe like
      // NOW (that would lie). A quiet dim ring marks the zero-lean origin between the two gravities.
      g.globalAlpha = 0.5; g.fillStyle = dim
      g.beginPath(); g.arc(cx, cy, 3, 0, Math.PI * 2); g.fill()
      g.strokeStyle = dim; g.globalAlpha = 0.3; g.lineWidth = 1
      g.beginPath(); g.arc(cx, cy, 8, 0, Math.PI * 2); g.stroke()
    } else {
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
    }
    g.globalAlpha = 1
  }, [proj, picked, pickedSector, zoom, sel, frame, live, at, showStrain, dial])

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
      const animLive = !!animRef.current && performance.now() - animRef.current.t0 < 480
      // keep ticking while EITHER the position tween OR the rung crossfade (departRef, set when the fetch
      // returns the new rung — later than this effect fires) is still running; departRef self-clears in draw().
      if (animLive || departRef.current) raf = requestAnimationFrame(tick)
      else { animRef.current = null; drawRef.current() }
    }
    raf = requestAnimationFrame(tick)
    return () => { cancelAnimationFrame(raf); animRef.current = null }
  }, [frame, center, rung])   // G11: a rung change crossfades — the new rung's points fade in (continuous scale move)

  const pick = (ev: { clientX: number; clientY: number }) => {
    const wrap = wrapRef.current
    if (!wrap || !proj) return
    const rect = wrap.getBoundingClientRect()
    const px = ev.clientX - rect.left, py = ev.clientY - rect.top
    const w = rect.width, h = rect.height
    const cx = w / 2, cy = h / 2, R = Math.min(w, h) / 2 - 34
    // CONNECTIONS MODE (Group 10): pick a SECTOR (a registry row) by the click's angle → drive its in/out
    // edges. A click near the centre clears the selection (back to the whole web). Points are sparse here;
    // the rows + their connections are what you drive.
    if (proj.edges && proj.edges.length) {
      if (Math.hypot(px - cx, py - cy) < R * 0.12) { setPickedSector(null); return }
      let th = Math.atan2(px - cx, cy - py); if (th < 0) th += Math.PI * 2
      const si = proj.sectors.findIndex(s => s.from <= th && th < s.to)
      setPickedSector(si >= 0 ? si : null)
      return
    }
    let best: ProjPoint | null = null, bd = 14 * 14
    for (const p of proj.points) {
      // NUCLEATION uses its own radius (box-fraction; piled items push outside the box) — MUST match draw().
      const rr = (isNucleation ? nucRadius(p) : radial(p)) * R
      const pth = isSeparator ? sepTheta(p) : p.theta   // MUST match draw()'s basin angle or clicks land wrong
      const x = cx + Math.sin(pth) * rr, y = cy - Math.cos(pth) * rr
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

  // G10 CONNECTIONS — drive-to-explore: the picked row + its OUT (feeds →) / IN (← fed-by) rows, read off
  // the real directional typed edges. connMode = a binding that surfaced edges (e.g. the node registry).
  const connMode = !!(proj?.edges && proj.edges.length)
  const sName = (i: number) => proj?.sectors[i]?.label || `#${i}`
  const pickedRow = (connMode && pickedSector != null && proj) ? {
    name: sName(pickedSector),
    out: proj.edges!.filter(e => e.from === pickedSector).map(e => sName(e.to)),
    inn: proj.edges!.filter(e => e.to === pickedSector).map(e => sName(e.from)),
  } : null

  // G9 SEPARATOR readout — the fifth gate + the BALANCE, made visible (the advisor's mandate: separates:True
  // can still be lopsided, so Tim must SEE the skew). The diverging bar widths are the share leaning each way.
  const sep = isSeparator ? proj?.separation : null
  const sepPoles = proj?.binding?.poles
  const balTot = sep ? Math.max(sep.balance.lean_a + sep.balance.lean_b, 1) : 1
  const balAPct = sep ? Math.round((sep.balance.lean_a / balTot) * 100) : 0

  // NUCLEATION readout — the type-birth report made visible: membership (fits/pile), the candidate new types
  // (born vs forming vs absorbed, with margin-strength + the null verdict), dissolution candidates, and the
  // dial (the 20/80 birth threshold). The candidates are ordered born → forming → absorbed, biggest first.
  const nu = isNucleation ? proj?.nucleation : null
  const nuDial = nu ? (dial ?? nu.dial) : 0.2
  // CLIENT-SIDE born (the dial is instant): born = distinct AND mass past the 20/80 birth threshold = dial ×
  // the examined pile (pile_clustered). Recomputed here + in draw() so a dial tick re-renders with no refetch.
  const nuBirthMass = nu ? Math.max(3, Math.round(nuDial * Math.max(nu.pile_clustered, 1))) : 0
  const nuBorn = (size: number, distinct: boolean) => !!distinct && size >= nuBirthMass
  const nuBornCount = nu ? nu.candidates.filter(c => nuBorn(c.size, c.distinct)).length : 0
  const nuCands = nu ? [...nu.candidates].sort((a, b) =>
    (Number(nuBorn(b.size, b.distinct)) - Number(nuBorn(a.size, a.distinct)))
    || (Number(b.distinct) - Number(a.distinct)) || (b.size - a.size)) : []
  const nuAvail = nu?.available

  // ROBUSTNESS (G4 carry-forward): the error view must NOT be a dead-end. The poll was retired for SSE (which
  // only subscribes after a successful fetch), so a failed pull has no auto-recovery — give it an in-view ↻ retry
  // (re-fires the SAME params via the retry nonce) AND an escape to the default lens (when a bad binding/pole is
  // the cause), so the operator never has to reload the whole app to recover.
  if (err) return (
    <div className="lattice-err">
      <EmptyState>projection unreachable — {err}</EmptyState>
      <div className="lattice-err-actions">
        <button className="le-retry" onClick={() => setRetry(n => n + 1)}>↻ retry</button>
        {(bind || center || poleA || poleB || at != null) && (
          <button className="le-reset"
            onClick={() => { setBind(''); setCenter(null); setPoleA(null); setPoleB(null); setAt(null); setLive(true); setRetry(n => n + 1) }}>
            ← default lens
          </button>
        )}
      </div>
    </div>
  )
  return (
    <div className="lattice-wrap" ref={wrapRef} onPointerDown={pick}>
      <canvas ref={cvsRef} />
      {semanticPending && (
        <div className="lattice-hint" onPointerDown={e => e.stopPropagation()}>
          ◎ semantic lens{proj?.binding?.space ? ` · ${proj.binding.space}` : ''} — pick a centre: tap a point,
          then <b>◎ meaning-field from here</b> to rank everything by meaning-distance
        </div>
      )}
      {connMode && pickedSector == null && (
        <div className="lattice-hint" onPointerDown={e => e.stopPropagation()}>
          ◈ the connections in the registry — each chord is a <b>directional typed edge</b> (arrow = direction).
          Tap a node to light its edges (<b>gold = feeds →</b>, <b>ink = ← fed-by</b>); tap the centre to clear.
        </div>
      )}
      {sep && (
        <div className="lattice-card lc-sep" onPointerDown={e => e.stopPropagation()}>
          <div className="lc-sep-poles">
            <span className="lc-pole lc-pole-a" style={{ color: sepColA }}>◀ {poleLabel(sepPoles?.a?.label) || 'pole A'}</span>
            <span className="lc-pole lc-pole-b" style={{ color: sepColB }}>{poleLabel(sepPoles?.b?.label) || 'pole B'} ▶</span>
          </div>
          {/* the BALANCE — a diverging bar, so a lopsided field SHOUTS even when separates:True */}
          <div className="lc-balance" title={`${sep.balance.lean_a} lean A · ${sep.balance.lean_b} lean B · ${sep.balance.neutral} neutral`}>
            <span className="lc-bal-seg" style={{ width: `${balAPct}%`, background: sepColA }} />
            <span className="lc-bal-seg" style={{ width: `${100 - balAPct}%`, background: sepColB }} />
          </div>
          <div className="lc-sep-meta">
            <span className={'lc-sep-verdict' + (sep.separates ? ' on' : '')}>
              {sep.separates ? '⚖ separates' : '⚠ does not separate'}
            </span>
            {' '}· {sep.balance.lean_a}/{sep.balance.lean_b} · distinct {sep.pole_distinctness.toFixed(2)} · ρ {sep.rank_corr.toFixed(2)}
            {!sep.separates && sep.balance.minority_frac === 0 && <span className="lc-sep-why"> — one pole attracts nobody</span>}
          </div>
          <div className="lc-meta lc-sep-foot">
            <span>tap a point → set it as a pole (drive the two gravities)</span>
            {(poleA || poleB) && (
              // a driven field → offer the way BACK to the binding's default poles (the reset path the drive
              // loop was missing; clearing the overrides re-fetches with the binding's declared poles).
              <button className="lc-sep-reset" onClick={() => { setPoleA(null); setPoleB(null) }}
                title="return to this lens's default two poles">↺ default poles</button>
            )}
          </div>
        </div>
      )}
      {nu && (
        <div className="lattice-card lc-nuc" onPointerDown={e => e.stopPropagation()}>
          <div className="lc-nuc-head">
            <span className="lc-nuc-title">✦ type-nucleation</span>
            <span className="lc-nuc-route" title="the registry of types ← typed against → the content store">
              {shortName(nu.types_space)} ◷ {shortName(proj?.binding?.space)}
            </span>
          </div>
          {/* membership: the fits/pile split — the empty-square (0 fit) cross-store case reads honestly here */}
          <div className="lc-nuc-mem" title="items that FIT a registered type (inside the square) vs those that pile OUTSIDE">
            <b>{nu.membership.inside}</b> fit · <b>{nu.pile_total}</b> piled outside
            {nu.pile_tail > 0 && <span className="lc-nuc-tail"> ({nu.pile_clustered} clustered, {nu.pile_tail} tail)</span>}
          </div>
          {/* the candidate new types — born (past the 20/80 + distinct) vs forming (distinct, not yet massed) */}
          <div className="lc-nuc-cands">
            {nuCands.length === 0 && <span className="lc-nuc-none">— no candidate new types in the pile</span>}
            {nuCands.slice(0, 5).map((c, i) => {
              const born = nuBorn(c.size, c.distinct)
              return (
              <div key={i} className={'lc-nuc-cand' + (born ? ' born' : c.distinct ? ' forming' : ' absorbed')}
                title={`margin ${c.margin} vs null ${c.null_p95} — ${c.distinct ? 'beats the permutation null (distinct)' : 'within noise (absorbed)'}`}>
                <span className="lc-nuc-state">{born ? '✦ new' : c.distinct ? '◦ forming' : '· pile'}</span>
                <span className="lc-nuc-ex">{shortName(c.exemplar)}</span>
                <span className="lc-nuc-num">{c.size} · m{c.margin.toFixed(2)}</span>
              </div>
            )})}
          </div>
          <div className="lc-nuc-verdict">
            <b>{nuBornCount}</b> born · {nu.distinct_count} distinct · birth ≥ {nuBirthMass} (dial {Math.round(nuDial * 100)}%)
          </div>
          {nu.dissolution_candidates.length > 0 && (
            <div className="lc-nuc-diss" title="registered types whose membership thinned — a dissolution CANDIDATE, context-dependent (a sparse type may be rare, not wrong); never auto-applied">
              ⓥ thinning: {nu.dissolution_candidates.map(d => `${shortName(d.type)} (${d.size})`).join(', ')}
            </div>
          )}
        </div>
      )}
      {pickedRow && (
        <div className="lattice-card lc-conn" onPointerDown={e => e.stopPropagation()}>
          <div className="lc-head">
            <Badge tone="sig">{pickedRow.name}</Badge>
            <button className="lc-x" onClick={() => setPickedSector(null)}>✕</button>
          </div>
          <div className="lc-conn-row"><span className="lc-conn-k lc-conn-out">feeds →</span>
            {pickedRow.out.length ? pickedRow.out.join(', ') : <span className="lc-conn-none">— nothing</span>}</div>
          <div className="lc-conn-row"><span className="lc-conn-k">← fed-by</span>
            {pickedRow.inn.length ? pickedRow.inn.join(', ') : <span className="lc-conn-none">— nothing</span>}</div>
          <div className="lc-meta">{pickedRow.out.length} out · {pickedRow.inn.length} in — directional typed edges</div>
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
            <button className="lf-centred" onClick={() => { setCenter(null); setPicked(null); setRung(null); if (isSemantic) setBind('') }}
              onPointerDown={e => e.stopPropagation()} title={`centred on ${center} — tap to release back to NOW`}>
              {isSemantic ? '◎' : '⊙'} {centreSeg} ✕
            </button>
          )}
          {' '}{proj ? `${proj.count} pts · ${proj.n} sectors · ${timeLabel}` : 'projecting…'}
        </span>
        <div className="lattice-frames" onPointerDown={e => e.stopPropagation()}>
          {proj?.scale && (
            // THE SCALE AXIS (Group 11): step the resolution — units (the finest, every embedded item) ↔
            // coarser THEME rungs (cluster centroids). A separate control from the radial ⌕ zoom: ⌕ magnifies
            // the band, ⊟ changes which RUNG resolves. Fine→coarse, left→right.
            <span className="lf-rungs" title="SCALE — resolve over individual items (fine) or themes (coarse)">
              <span className="lf-ic">⊟</span>
              <button className={'lf-rung' + (rung == null ? ' on' : '')} onClick={() => setRung(null)}
                title={`the finest rung — every embedded item (${proj.scale.n_units})`}>units</button>
              {scaleRungs.map(k => (
                <button key={k} className={'lf-rung' + (rung === k ? ' on' : '')} onClick={() => setRung(k)}
                  title={`${k} theme centroids — a coarser meaning-field (fewer, larger regions)`}>{k}</button>
              ))}
            </span>
          )}
          {isNucleation ? (
            // NUCLEATION active: drive the two VARIABLE axes — the registry of types + the content store typed
            // against it — and the 20/80 BIRTH dial. registry-true pickers (the bridge lists what's embedded /
            // has a pyramid); the radial controls don't apply (radius = fit/pile, fixed). The universal law.
            <span className="lf-nuc" title="type-nucleation: type the store against the registry; misfits pile out → new types">
              {nuAvail && nuAvail.types_spaces.length > 0 && (
                <select className="lf-nuc-sel" title="the REGISTRY of types (a store with a built pyramid)"
                  value={proj?.binding?.types_space || ''} onChange={e => { setPicked(null); setTypesSpace(e.target.value) }}>
                  {nuAvail.types_spaces.map(s => <option key={s} value={s}>types: {shortName(s)}</option>)}
                </select>
              )}
              {nuAvail && nuAvail.item_spaces.length > 0 && (
                <select className="lf-nuc-sel" title="the CONTENT store typed against the registry"
                  value={proj?.binding?.space || ''} onChange={e => { setPicked(null); setItemSpace(e.target.value) }}>
                  {nuAvail.item_spaces.map(s => <option key={s} value={s}>items: {shortName(s)}</option>)}
                </select>
              )}
              {nuAvail && nuAvail.rungs.length > 0 && (
                <span className="lf-rungs" title="the registry's granularity — how many types (a coarser/finer registry)">
                  <span className="lf-ic">⊟</span>
                  {nuAvail.rungs.map(k => (
                    <button key={k} className={'lf-rung' + ((proj?.binding?.rung ?? 8) === k ? ' on' : '')}
                      onClick={() => { setPicked(null); setRung(k) }} title={`${k} registered types`}>{k}</button>
                  ))}
                </span>
              )}
              <label className="lf-slider lf-nuc-dial" title="the 20/80 BIRTH threshold — how much a pile must fill to be born a new type (Tim's water-law dial)">
                <span className="lf-ic">✦</span>
                <input type="range" className="lf-zoom" min={0.05} max={0.6} step={0.05} value={nuDial}
                  onChange={e => { setPicked(null); setDial(Number(e.target.value)) }} onPointerDown={e => e.stopPropagation()} />
                <span className="lf-nuc-dialv">{Math.round(nuDial * 100)}%</span>
              </label>
              {(typesSpace || itemSpace || dial != null) && (
                <button className="lc-sep-reset" onClick={() => { setTypesSpace(null); setItemSpace(null); setDial(null); setRung(null) }}
                  title="return to this lens's default registry / store / dial">↺ default</button>
              )}
            </span>
          ) : isSeparator ? (
            // SEPARATOR active: radius is |lean| (not time), angle is the sign-basin — the temporal controls
            // don't apply. A legible note states the reading; zoom still expands the near (low-lean) band.
            <span className="lf-semnote" title="radius = how strongly each item leans; left basin = pole A, right basin = pole B">
              ⚖ lean between two poles{proj?.binding?.radius_normalized ? ' · normalized' : ''}
            </span>
          ) : isSemantic ? (
            // THE CIRCLE active: radius is meaning-distance (not time) — the temporal controls don't apply;
            // a legible note states the reading + its honest normalization. Zoom still expands the near band.
            // ⊿ strain toggles the Group-7 tension overlay (structure↔meaning divergence lines).
            <>
              <span className="lf-semnote" title="radius = cosine meaning-distance from the centre item, in this lens's space">
                ◎ meaning-distance{proj?.binding?.radius_normalized ? ' · normalized' : ''}
              </span>
              <button className={'lf-btn' + (showStrain ? ' on' : '')} onClick={() => setShowStrain(s => !s)}
                title="overlay STRAIN: a radial line from where each item is FILED (structure) to where it MEANS to be (meaning) — the gap is the tension (SEED §111)">
                ⊿ strain
              </button>
            </>
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
          {(isSemantic || isSeparator || frame === 'now') && (
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
          {picked.strain != null && picked.r_struct != null && (
            // STRAIN (Group 7): where it's filed (structure) ↔ where it means to be (meaning), and the gap.
            <div className="lc-meta lc-strain">⊿ strain {picked.strain.toFixed(2)} · filed {picked.r_struct.toFixed(2)} ↔ means {picked.r.toFixed(2)}</div>
          )}
          {isSeparator && picked.lean != null && (
            // SEPARATOR (Group 9): this item's two raw pulls + its signed lean — which gravity, how strongly.
            <div className="lc-meta lc-strain">
              ⚖ leans {picked.pole === 'b' ? '▶ B' : picked.pole === 'a' ? 'A ◀' : 'neutral'} · pull A {picked.pull_a?.toFixed(3)} · pull B {picked.pull_b?.toFixed(3)} · lean {picked.lean.toFixed(3)}
            </div>
          )}
          {picked.scale_size != null && (
            // SCALE (Group 11): a THEME — a coarse cluster of units. Show how many it aggregates, the finer
            // clusters that fold in, and the exemplar (a real unit that names it).
            <div className="lc-meta lc-theme">◇ theme · {picked.scale_size} items{picked.scale_children?.length ? ` · ${picked.scale_children.length} finer` : ''} · ~{String(picked.scale_exemplar || '').split('/').filter(Boolean).slice(-1)[0]}</div>
          )}
          <button className="lc-pick" onClick={() => toggleSel(picked)}>
            {inSel(picked) ? '− remove from set' : '＋ add to set'}
          </button>
          {isSeparator && picked.source ? (
            // THE POLE PICKER (Group 9): make this item a gravity. Each button REPLACES one pole and KEEPS the
            // other (the field always has two poles — the bridge fails loud on one), so tapping drives the field.
            <div className="lc-pole-pick">
              <button className="lc-center lc-pole-set-a" style={{ borderColor: sepColA, color: sepColA }}
                onClick={() => { setPoleA(picked.source!); setPicked(null) }}
                title="make this item the LEFT gravity (pole A) — re-drives the field, keeps pole B">
                ◀ set pole A
              </button>
              <button className="lc-center lc-pole-set-b" style={{ borderColor: sepColB, color: sepColB }}
                onClick={() => { setPoleB(picked.source!); setPicked(null) }}
                title="make this item the RIGHT gravity (pole B) — re-drives the field, keeps pole A">
                set pole B ▶
              </button>
            </div>
          ) : picked.scale_size != null ? (
            // a THEME: ⊕ zoom INTO it (step to the finer rung, centred on its exemplar — a real unit with a
            // vector, so the centre resolves at every rung); ◎ rank this rung's themes by distance from it.
            <>
              {finerRung(rung) !== rung && (
                <button className="lc-center lc-zoomin"
                  onClick={() => { if (picked.scale_exemplar) setCenter(picked.scale_exemplar); setRung(finerRung(rung)); setPicked(null) }}
                  title={`zoom INTO this theme — resolve at the finer rung (${finerRung(rung) == null ? 'units' : finerRung(rung) + ' themes'}), centred here`}>
                  ⊕ zoom into theme
                </button>
              )}
              {picked.source && (
                <button className="lc-center lc-meaning"
                  onClick={() => { setBind('semantic'); setCenter(picked.source!); setPicked(null) }}
                  title="rank this rung's themes by MEANING-distance from this theme">
                  ◎ meaning-field from this theme
                </button>
              )}
            </>
          ) : (
            <>
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
            </>
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
