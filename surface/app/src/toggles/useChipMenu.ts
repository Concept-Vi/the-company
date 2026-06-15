import { useCallback, useRef, useState } from 'react'

// SHARED chip-menu state + POPOVER COLLISION (design-critic S4). The optics chips (lens · layer · resolution)
// drop an absolutely-positioned menu under themselves (left:0). When a chip sits far enough right that a
// ~menuW-wide menu would run off the viewport's right edge — the mobile case where the cluster reaches the
// edge — the menu is anchored to the chip's RIGHT edge instead (the `lenschip-menu--right` modifier), so it
// opens leftward into view rather than clipping. Measured on each OPEN (the chip's position is stable while
// the menu is up). One hook, three call sites — no per-chip duplication, the design-system collision answer.
export function useChipMenu(menuW = 240) {
  const [open, setOpen] = useState(false)
  const [menuClass, setMenuClass] = useState('')
  const wrapRef = useRef<HTMLDivElement>(null)
  const toggle = useCallback(() => {
    setOpen((o) => {
      if (!o && wrapRef.current) {
        const r = wrapRef.current.getBoundingClientRect()
        // flip to right-anchored when a left:0 menu would overflow the right edge (8px breathing margin)
        setMenuClass(r.left + menuW > window.innerWidth - 8 ? 'lenschip-menu--right' : '')
      }
      return !o
    })
  }, [menuW])
  const close = useCallback(() => setOpen(false), [])
  return { open, toggle, close, wrapRef, menuClass }
}
