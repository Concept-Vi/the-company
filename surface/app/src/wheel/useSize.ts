import { useEffect, useRef, useState } from 'react'

// Observe a container's content box. Shared by the wheel (polar) and the separator (two-basin) views so
// both lock to the same measured region (proportion by construction).
export function useSize<T extends HTMLElement>() {
  const ref = useRef<T | null>(null)
  const [size, setSize] = useState({ width: 0, height: 0 })
  useEffect(() => {
    const el = ref.current
    if (!el) return
    const ro = new ResizeObserver((entries) => {
      const r = entries[0].contentRect
      setSize({ width: r.width, height: r.height })
    })
    ro.observe(el)
    setSize({ width: el.clientWidth, height: el.clientHeight })
    return () => ro.disconnect()
  }, [])
  return { ref, ...size }
}
