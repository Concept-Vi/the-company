import { useEffect, useState, useCallback } from 'react'
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
  selected: ProjPoint | null
  setSelected: (p: ProjPoint | null) => void
  feel: MotionFeel
  setFeel: (f: MotionFeel) => void
  view: ViewMode
  setView: (v: ViewMode) => void
  nuc: NucParams
  setNuc: (patch: Partial<NucParams>) => void
  centre: Centre | null
  setCentre: (c: Centre | null) => void
  focusCentre: (p: ProjPoint) => void
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
  const [selected, setSelected] = useState<ProjPoint | null>(null)
  const [feel, setFeel] = useState<MotionFeel>('spring')
  const [view, setView] = useState<ViewMode>('both')
  const [nuc, setNucState] = useState<NucParams>({ types_space: 'topics', space: 'topics', rung: 8 })
  const setNuc = useCallback((patch: Partial<NucParams>) => setNucState((p) => ({ ...p, ...patch })), [])
  const [centre, setCentre] = useState<Centre | null>(null)
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

  useEffect(() => {
    let live = true
    setLoading(true)
    setError(null)
    // the type-gravity lens is driven by the nuc params (which store, which type-registry, which rung);
    // other lenses take the plain window. registry-true — the surface never invents, only drives.
    const params: Record<string, string | number | undefined> =
      binding === 'by_nucleation'
        ? { binding, limit: 400, types_space: nuc.types_space, space: nuc.space, rung: nuc.rung }
        : { binding, limit: 600 }
    // the relative centre re-projects every lens around the attended node (radius = distance FROM it)
    if (centre) params.center = centre.ref
    fetchProjection(params)
      .then((p) => {
        if (!live) return
        setProj(p)
        setLoading(false)
      })
      .catch((e: unknown) => {
        if (!live) return
        setError(e instanceof ApiError ? e.message : String(e))
        setLoading(false)
      })
    return () => {
      live = false
    }
  }, [binding, nuc, centre])

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
    selected,
    setSelected,
    feel,
    setFeel,
    view,
    setView,
    nuc,
    setNuc,
    centre,
    setCentre,
    focusCentre,
    notice,
    dismissNotice,
  }

  if (ff === 'portrait') return <Portrait s={state} />
  if (ff === 'landscape') return <Landscape s={state} />
  return <Desktop s={state} />
}
