import { useEffect, useState, useCallback, useRef } from 'react'
import { fetchProjection, type Projection, type ProjPoint, ApiError } from './lib/api'
import { installAddressCapture, subscribeLocus, getLocus, clearNotice } from './lib/address'
import type { MotionFeel } from './tokens/motion'
import { Desktop } from './layouts/Desktop'
import { Portrait } from './layouts/Portrait'
import { Landscape } from './layouts/Landscape'

export type FormFactor = 'desktop' | 'portrait' | 'landscape'
// The seed's two coordinate systems over one space, three ways: BOTH = the circle inscribed in the square
// (the heart of the equation — present together from the start); CIRCLE = isolate meaning; SQUARE = isolate
// structure. (Tim 2026-06-14: "the circle is inscribed in the square… but I like being able to isolate them.")
export type ViewMode = 'both' | 'circle' | 'square'

// Discrete layout switch (L5) — NOT arithmetic scaling of one layout.
function classify(w: number, h: number): FormFactor {
  if (w >= 1024 && w > h) return 'desktop'
  if (h > w) return 'portrait'
  return 'landscape'
}

function useFormFactor(): FormFactor {
  const [ff, setFf] = useState<FormFactor>(() =>
    classify(window.innerWidth, window.innerHeight),
  )
  useEffect(() => {
    const on = () => setFf(classify(window.innerWidth, window.innerHeight))
    window.addEventListener('resize', on)
    window.addEventListener('orientationchange', on)
    return () => {
      window.removeEventListener('resize', on)
      window.removeEventListener('orientationchange', on)
    }
  }, [])
  return ff
}

// The shared surface state every layout module composes (one wheel, one disclosure, one set of controls).
export type SurfaceState = {
  proj: Projection | null
  error: string | null
  loading: boolean
  binding: string
  setBinding: (id: string) => void
  emb: string | null
  setEmb: (e: string | null) => void
  space: string | null
  setSpace: (s: string | null) => void
  dim: number | null
  setDim: (d: number | null) => void
  quant: string | null
  setQuant: (q: string | null) => void
  selected: ProjPoint | null
  setSelected: (p: ProjPoint | null) => void
  drillAddress: string | null   // the selected unit's contracts.address (the drill-in handoff target); null = nothing drilled
  feel: MotionFeel
  setFeel: (f: MotionFeel) => void
  view: ViewMode
  setView: (v: ViewMode) => void
  nuc: NucParams
  setNuc: (patch: Partial<NucParams>) => void
  centre: Centre | null
  setCentre: (c: Centre | null) => void
  focusCentre: (p: ProjPoint) => void
  poles: { a: Centre | null; b: Centre | null }
  setPole: (which: 'a' | 'b', p: ProjPoint) => void
  clearPoles: () => void
  live: boolean
  setLive: (v: boolean) => void
  at: string | null
  setAt: (t: string | null) => void
  corpusStart: string | null
  now: string | null
  rung: number | null
  setRung: (r: number | null) => void
  notice: string | null
  dismissNotice: () => void
}

// THE RELATIVE CENTRE (the seed §8): attention IS origin-selection. Look at a node → it becomes the centre →
// the whole space re-projects relative to it (radii/relevance recomputed around it; in the circle, this is the
// meaning-distance from it + the strain it reveals). null = the root origin (now / the default whole-frame).
export type Centre = { ref: string; label: string }

// Drivable type-gravity (nucleation) params — which item store is typed against which registry-of-types, at
// which rung. Default to a POPULATING same-space combo so points visibly cluster INSIDE their types (Tim's
// "points close around the types"); the pickers expose the cross-instance combo (the non-circular proof) too.
export type NucParams = { types_space: string; space: string; rung: number }

export function App() {
  const ff = useFormFactor()
  const [proj, setProj] = useState<Projection | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [binding, setBinding] = useState('raw')
  // THE EMBEDDER LAYER (the multi-layer model): null = the default (BGE) layer; a named layer (e.g. 'pplx')
  // reads that embedder's vectors — every lens is layer-aware (registry-true, driven by /api/layers).
  const [emb, setEmb] = useState<string | null>(null)
  // THE SPACE (which embedded item-store the lens ranges over): null = follow the binding's default space; an
  // explicit space (e.g. 'common_knowledge', 'repo') OVERRIDES it. The Instrument is the universal projection —
  // it points at ANY space, not just each binding's default. Driven by the SpaceChip (registry-true, /api/layers).
  const [space, setSpaceState] = useState<string | null>(null)
  // THE MRL RESOLUTION (the meaning-zoom axis): null = full dim; an N truncates every read vector to its first
  // N dims before the cosine — a continuous coarse↔fine zoom, orthogonal to the scale rung. Registry-true: the
  // picker's ladder is derived from the active layer's full dim (/api/layer-dims), never hardcoded.
  const [dim, setDim] = useState<number | null>(null)
  // THE REPRESENTATION axis (binary quantization): null = full float (cosine); 'binary' = sign-bit per dim, read
  // through the same cosine as a Hamming similarity (cos(sign a, sign b)=1−2·Hamming/d) — a coarse, 32×-compact
  // view. Orthogonal to emb (layer) + dim (MRL); composes with both. Registry-true; compute-on-read (pure).
  const [quant, setQuant] = useState<string | null>(null)
  const [selected, setSelected] = useState<ProjPoint | null>(null)
  const [feel, setFeel] = useState<MotionFeel>('spring')
  const [view, setView] = useState<ViewMode>('both')
  const [nuc, setNucState] = useState<NucParams>({ types_space: 'topics', space: 'topics', rung: 8 })
  const setNuc = useCallback((patch: Partial<NucParams>) => setNucState((p) => ({ ...p, ...patch })), [])
  const [centre, setCentre] = useState<Centre | null>(null)
  // THE TWO GRAVITIES are VARIABLES (G9): the operator picks ANY two items as the poles; the separator
  // re-projects everything between them. ref = the item's embeddable source; label = its leaf.
  const [poles, setPoles] = useState<{ a: Centre | null; b: Centre | null }>({ a: null, b: null })
  const setPole = useCallback((which: 'a' | 'b', p: ProjPoint) => {
    const ref = p.source || p.address || `ui://canvas/seq-${p.seq}`
    const label = ref.replace(/\/+$/, '').split('/').pop() || 'pole'
    setPoles((prev) => ({ ...prev, [which]: { ref, label } }))
  }, [])
  const clearPoles = useCallback(() => setPoles({ a: null, b: null }), [])
  // changing the SPACE re-frames the whole instrument: the centre/selection/poles were addresses in the OLD
  // space (their vectors don't exist in the new one → a semantic centre would fail loud). Clear them so the
  // operator re-anchors cleanly in the new space (fail-honest + no stale cross-space references).
  const setSpace = useCallback((sp: string | null) => {
    setSpaceState(sp)
    setCentre(null)
    setSelected(null)
    setPoles({ a: null, b: null })
  }, [])
  const [live, setLive] = useState(true)
  const [pulse, setPulse] = useState(0) // a live-stream tick → re-fetch (the present moves)
  const lastSeqRef = useRef(0)
  // G3 — the time scrubber: at = a past instant the temporal centre is moved to (null = the live now).
  const [at, setAt] = useState<string | null>(null)
  const [corpusStart, setCorpusStart] = useState<string | null>(null) // earliest event ts (the scrubber floor)
  // G11 — the scale-pyramid rung for the semantic lens: null = units, else a coarse rung (themes)
  const [rung, setRung] = useState<number | null>(null)
  const focusCentre = useCallback((p: ProjPoint) => {
    // re-centre on the item: its embeddable source (so meaning re-forms around the ITEM, not its run:// record),
    // else its address. label = the last path segment (text-minimal).
    const ref = p.source || p.address || `ui://canvas/seq-${p.seq}`
    const label = ref.replace(/\/+$/, '').split('/').pop() || 'centre'
    setCentre({ ref, label })
  }, [])
  const [notice, setNotice] = useState<string | null>(null)

  useEffect(() => {
    installAddressCapture()
    const unsub = subscribeLocus((l) => setNotice(l.notice))
    setNotice(getLocus().notice)
    return unsub
  }, [])

  // THE DRILL-IN HANDOFF (front-interface FIRST_SLICE, seam 3): selecting a wheel-point IS "drill into this
  // addressed unit." The points are canvas-drawn (not ui:// DOM elements), so the ui:// locus doesn't carry
  // them — instead we EMIT the selected unit's address on a transport-neutral window event. TWO addresses ride
  // it, with DISTINCT jobs (verified against runtime.cognition.resolve_address, 2026-06-16):
  //   • `address` = the CONTENT-RESOLVABLE address DNA's renderGallery(address) resolves THROUGH resolve_address
  //     to get the unit's content. That is the run:// RECORD (e.g. run://corpus/recollection/…/common_knowledge
  //     → {output.digest, projection, source_address}). It MUST be a scheme resolve_address reads today
  //     (run://·cas://·skill://·context://·session://·cap://·board://) — so we put selected.address (the run://
  //     record) FIRST. NB: the unit's `source` (code://·vi-vision://) is NOT content-resolvable yet → it would
  //     fail loud in renderGallery; that is why source-first was a seam bug (the resolvable addr was misfiled).
  //   • `source` = the unit's CANONICAL source address (code://·board://) — fork's loadable-brain target +
  //     wildcard's route-back = mutation-AT-address write (territory_for). Kept separate, never the render addr.
  // Consumers hook `projection:select`; same-page can read `drillAddress` off the state. We meet at the address
  // (the FIRST_SLICE contract); the look is DNA's, the brain is fork's — projection hands off WHICH addressed
  // unit was pointed at + which field resolves vs which field is the write-back target. null on deselect.
  useEffect(() => {
    const resolveAddr = selected ? (selected.address || selected.source || null) : null  // run:// record first → resolve_address-readable
    window.dispatchEvent(new CustomEvent('projection:select', {
      detail: resolveAddr ? { address: resolveAddr, source: selected?.source ?? null, record: selected?.address ?? null,
                              seq: selected?.seq, kind: selected?.kind, space: proj?.binding?.space ?? null } : null,
    }))
  }, [selected, proj])

  useEffect(() => {
    let alive = true
    setLoading(true)
    setError(null)
    // the type-gravity lens is driven by the nuc params (which store, which type-registry, which rung);
    // other lenses take the plain window. registry-true — the surface never invents, only drives.
    const params: Record<string, string | number | undefined> =
      binding === 'by_nucleation'
        ? { binding, limit: 400, types_space: nuc.types_space, space: nuc.space, rung: nuc.rung }
        : { binding, limit: 600, ...(space ? { space } : {}) }   // SpaceChip override (null = the binding's default space)
    // the relative centre re-projects every lens around the attended node (radius = distance FROM it)
    if (centre) params.center = centre.ref
    // the two gravities (G9): operator-picked poles drive the separator (else the binding's default poles)
    if (binding === 'by_separator' && poles.a && poles.b) {
      params.pole_a = poles.a.ref
      params.pole_b = poles.b.ref
    }
    // the time scrubber (G3): move the temporal centre into the past (project only ts≤at)
    if (at) params.at = at
    // the scale rung (G11): the semantic lens shows theme centroids at a coarse rung (else units)
    if (binding === 'semantic' && rung) params.rung = rung
    // the embedder LAYER (the multi-layer model): read every lens through the chosen embedding (null = default/BGE)
    if (emb) params.emb = emb
    // the MRL RESOLUTION: truncate the read vectors to this many dims before the cosine (null = full dim)
    if (dim) params.dim = dim
    // the REPRESENTATION: binary = sign-bit/Hamming over the read vectors (null = full float cosine)
    if (quant) params.quant = quant
    fetchProjection(params)
      .then((p) => {
        if (!alive) return
        setProj(p)
        // track the newest event seq so the live stream tails from here (only NEW events pulse a refresh)
        for (const pt of p.points) if (typeof pt.seq === 'number' && pt.seq > lastSeqRef.current) lastSeqRef.current = pt.seq
        setLoading(false)
      })
      .catch((e: unknown) => {
        if (!alive) return
        setError(e instanceof ApiError ? e.message : String(e))
        setLoading(false)
      })
    return () => {
      alive = false
    }
  }, [binding, nuc, centre, poles, at, rung, emb, dim, quant, space, pulse])

  // THE LIVE SPINE (the seed §4 / mandate L9 — live, not a viewer): tail /api/stream from the newest seq we
  // know; when NEW events arrive, pulse a (throttled) re-fetch so the present visibly moves — new points bloom
  // in (no teleport). Freeze pauses the stream. EventSource auto-reconnects gaplessly (Last-Event-ID).
  useEffect(() => {
    if (!live || at) return // scrubbing into the past pauses the live present (don't yank back to now)
    let es: EventSource | null = null
    let pending = 0
    let timer: number | null = null
    try {
      es = new EventSource(`/api/stream?since=${lastSeqRef.current}`)
    } catch {
      return
    }
    es.onmessage = (e) => {
      let seq = -1
      try {
        seq = JSON.parse(e.data).seq
      } catch {
        return
      }
      if (typeof seq !== 'number' || seq <= lastSeqRef.current) return
      pending++
      if (timer == null) {
        timer = window.setTimeout(() => {
          timer = null
          if (pending > 0) {
            pending = 0
            setPulse((p) => p + 1) // throttled → re-fetch the projection
          }
        }, 2500)
      }
    }
    es.onerror = () => {} // browser auto-reconnects with Last-Event-ID (gapless)
    return () => {
      es?.close()
      if (timer != null) clearTimeout(timer)
    }
  }, [live, at])

  // the scrubber floor: read the earliest event's ts once (a one-shot stream from seq 0, closed immediately)
  useEffect(() => {
    let es: EventSource | null = null
    try {
      es = new EventSource('/api/stream?since=-1')
    } catch {
      return
    }
    es.onmessage = (e) => {
      try {
        const ts = JSON.parse(e.data).ts
        if (ts) setCorpusStart(ts)
      } catch {
        /* ignore */
      }
      es?.close()
    }
    return () => es?.close()
  }, [])

  const dismissNotice = useCallback(() => {
    clearNotice()
    setNotice(null)
  }, [])

  const state: SurfaceState = {
    proj,
    error,
    loading,
    binding,
    setBinding,
    emb,
    setEmb,
    space,
    setSpace,
    dim,
    setDim,
    quant,
    setQuant,
    selected,
    setSelected,
    drillAddress: selected ? (selected.address || selected.source || null) : null,   // resolvable run:// record first (matches the projection:select `address` field)
    feel,
    setFeel,
    view,
    setView,
    nuc,
    setNuc,
    centre,
    setCentre,
    focusCentre,
    poles,
    setPole,
    clearPoles,
    live,
    setLive,
    at,
    setAt,
    corpusStart,
    now: proj?.now ?? null,
    rung,
    setRung,
    notice,
    dismissNotice,
  }

  if (ff === 'portrait') return <Portrait s={state} />
  if (ff === 'landscape') return <Landscape s={state} />
  return <Desktop s={state} />
}
