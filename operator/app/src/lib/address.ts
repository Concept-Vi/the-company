// HARVESTED VERBATIM from surface/app/src/lib/address.ts (the scout-verified clean quarry — K1).
// THE ADDRESS SPINE — every addressable element carries its `ui://` address as data-ui-ref (the
// literal full string, stamped before first render — the corpus convention). All navigation routes
// through ONE sink (resolveUiTarget). Malformed addresses FAIL LOUD (a Notice). The only adaptations:
// the import path (this app's api.ts) and dropping the Motion layoutId note (framer-motion is not a
// dependency here — the DS's motion tokens carry movement).

import { fetchContext, type ContextBundle } from './api'

// ---- grammar (mirror contracts/ui_info.py:parse_ui_address) -------------------------------------
// ui:// + >=1 '/'-delimited segment + optional trailing @state. Fails loud on malformed.
export function parseUiAddress(addr: string): { ok: true; segments: string[]; state?: string } | { ok: false; reason: string } {
  if (typeof addr !== 'string' || !addr.startsWith('ui://')) return { ok: false, reason: 'must start with ui://' }
  let rest = addr.slice('ui://'.length)
  let state: string | undefined
  const at = rest.indexOf('@')
  if (at >= 0) {
    state = rest.slice(at + 1)
    rest = rest.replace(/\/?@.*$/, '')
  }
  const segments = rest.split('/').filter(Boolean)
  if (segments.length === 0) return { ok: false, reason: 'needs at least one path segment' }
  return { ok: true, segments, state }
}

export function isUiAddress(addr: string | null | undefined): addr is string {
  return !!addr && parseUiAddress(addr).ok
}

// Stamp props for an addressable element: data-ui-ref (literal full string).
export function stamp(addr: string): { 'data-ui-ref': string } {
  return { 'data-ui-ref': addr }
}

// ---- the locus store (a tiny pub/sub so React reflects the indicated address) -------------------
export type Locus = { address: string | null; notice: string | null }
let _locus: Locus = { address: null, notice: null }
const _subs = new Set<(l: Locus) => void>()

export function getLocus(): Locus {
  return _locus
}
export function subscribeLocus(fn: (l: Locus) => void): () => void {
  _subs.add(fn)
  return () => _subs.delete(fn)
}
function setLocus(next: Partial<Locus>) {
  _locus = { ..._locus, ...next }
  _subs.forEach((fn) => fn(_locus))
}

// indicate: set the locus + paint the soft highlight. Additive — never blocks normal clicking.
export function indicate(addr: string) {
  document.querySelectorAll('.ui-indicated').forEach((el) => el.classList.remove('ui-indicated'))
  const el = document.querySelector(`[data-ui-ref="${cssEscape(addr)}"]`)
  if (el) el.classList.add('ui-indicated')
  setLocus({ address: addr, notice: null })
}

// THE SINGLE SINK: every address-driven navigation (click / future voice / future gesture) comes here.
// `transient` decouples the V-POINTING path from the CLICK-NAV path: a CLICK is navigation, so
// .ui-indicated PERSISTS; a brain pointing as it speaks is attention-DIRECTION — transient, fully
// releasing with the glow. Two acts, two behaviours.
export function resolveUiTarget(addr: string, opts?: { transient?: boolean }): boolean {
  const parsed = parseUiAddress(addr)
  if (!parsed.ok) {
    // Fail loud — a calm Notice, never a silent swallow (mirrors the backend 400).
    setLocus({ notice: `Unknown address (${parsed.reason}): ${addr}` })
    return false
  }
  indicate(addr)
  const el = document.querySelector(`[data-ui-ref="${cssEscape(addr)}"]`)
  if (el) {
    el.classList.add('ui-spotlight')
    el.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' })
    window.setTimeout(() => {
      el.classList.remove('ui-spotlight')
      if (opts && opts.transient) el.classList.remove('ui-indicated') // pointing releases; click stays
    }, 1200)
  }
  return true
}

export function clearNotice() {
  setLocus({ notice: null })
}

export function contextAt(addr: string): Promise<ContextBundle> {
  return fetchContext(addr)
}

// ---- the capture-phase listener (mirror runtime/bridge.py's deixis gate) ------------------------
// Only full ui:// refs are loci. Additive: no preventDefault / stopPropagation.
let _installed = false
export function installAddressCapture() {
  if (_installed) return
  _installed = true
  document.addEventListener(
    'click',
    (e) => {
      const t = e.target as Element | null
      const node = t?.closest?.('[data-ui-ref]') as Element | null
      if (!node) return
      const a = node.getAttribute('data-ui-ref') || ''
      if (a.indexOf('ui://') !== 0) return
      resolveUiTarget(a)
    },
    true, // capture phase
  )
}

function cssEscape(s: string): string {
  // Minimal escape for attribute-selector quoting (CSS.escape isn't guaranteed in every runtime).
  return s.replace(/(["\\])/g, '\\$1')
}

// ---- the POINTER bridge — the programmatic twin of installAddressCapture (clicks) ----------------
// Anything dispatches `window.dispatchEvent(new CustomEvent('ui:point', { detail: { address: 'ui://…' } }))`
// → it routes to the SAME single sink (resolveUiTarget), fail-loud on a malformed ui:// address. Only
// ui:// loci point (mirrors the click gate); a non-ui:// address is an honest no-op.
let _pointerInstalled = false
export function installPointerBridge() {
  if (_pointerInstalled) return
  _pointerInstalled = true
  window.addEventListener('ui:point', (e) => {
    const addr = String(((e as CustomEvent).detail || {}).address || '')
    if (addr.indexOf('ui://') === 0) resolveUiTarget(addr, { transient: true })
  })
}
