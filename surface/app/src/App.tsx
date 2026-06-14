import { useEffect, useState, useCallback } from 'react'
import { fetchProjection, type Projection, type ProjPoint, ApiError } from './lib/api'
import { installAddressCapture, subscribeLocus, getLocus, clearNotice } from './lib/address'
import type { MotionFeel } from './tokens/motion'
import { Desktop } from './layouts/Desktop'
import { Portrait } from './layouts/Portrait'
import { Landscape } from './layouts/Landscape'

export type FormFactor = 'desktop' | 'portrait' | 'landscape'
export type ViewMode = 'circle' | 'square' // the seed's two coordinate systems over one space

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
  notice: string | null
  dismissNotice: () => void
}

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
  const [view, setView] = useState<ViewMode>('circle')
  const [nuc, setNucState] = useState<NucParams>({ types_space: 'topics', space: 'topics', rung: 8 })
  const setNuc = useCallback((patch: Partial<NucParams>) => setNucState((p) => ({ ...p, ...patch })), [])
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
    const params =
      binding === 'by_nucleation'
        ? { binding, limit: 400, types_space: nuc.types_space, space: nuc.space, rung: nuc.rung }
        : { binding, limit: 600 }
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
  }, [binding, nuc])

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
    notice,
    dismissNotice,
  }

  if (ff === 'portrait') return <Portrait s={state} />
  if (ff === 'landscape') return <Landscape s={state} />
  return <Desktop s={state} />
}
