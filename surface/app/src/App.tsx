import { useEffect, useState, useCallback } from 'react'
import { fetchProjection, type Projection, type ProjPoint, ApiError } from './lib/api'
import { installAddressCapture, subscribeLocus, getLocus, clearNotice } from './lib/address'
import type { MotionFeel } from './tokens/motion'
import { Desktop } from './layouts/Desktop'
import { Portrait } from './layouts/Portrait'
import { Landscape } from './layouts/Landscape'

export type FormFactor = 'desktop' | 'portrait' | 'landscape'

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
  notice: string | null
  dismissNotice: () => void
}

export function App() {
  const ff = useFormFactor()
  const [proj, setProj] = useState<Projection | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [binding, setBinding] = useState('raw')
  const [selected, setSelected] = useState<ProjPoint | null>(null)
  const [feel, setFeel] = useState<MotionFeel>('spring')
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
    fetchProjection({ binding, limit: 600 })
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
  }, [binding])

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
    notice,
    dismissNotice,
  }

  if (ff === 'portrait') return <Portrait s={state} />
  if (ff === 'landscape') return <Landscape s={state} />
  return <Desktop s={state} />
}
