// THE HOST RESOLVE-CONSUME — the host half of resolve(device-coordinate)→allocation (RESOLVER-CONTRACT.md §3/§7).
// The host COMPUTES its layout allocation from the screen-size COORDINATE by asking fork's resolver primitive
// (/api/resolver — renamed 2026-07-13, was /api/resolve which SHADOWED the operator approval door; POST {invariant, coordinate} → {ok, resolved:{slot:value}}) — NOT @media breakpoints. The
// invariant (the per-slot relationships) is authored HERE to the locked contract; fork's resolve() evaluates it.
//
// DEGRADE-CLEAN (contract §6): /api/resolve is committed-not-live until the lead's batched bounce (the running
// bridge's rules.py is sys.modules-cached stale → it fail-louds my valid AST today). So on ANY failure (400/404/
// error) we set NOTHING and the live `body[data-ff]` CSS (App's device-coordinate root) holds — the surface is
// unchanged. When the bounce lands, resolve() returns real px and the CSS vars below WIN over the data-ff
// fallbacks. So this is bounce-ready + zero-regression now. (Same pattern as the tool-face form_meta consume.)
//
// VERIFIED: the POST contract + response shape read from the live handler (bridge.py:2179-2198). The resolve
// VALUES are verify-on-bounce (can't exercise the live engine while it's stale); the invariant slots were
// co-shaped FROM the live CSS (contract §3) so they track current behavior (the continuous form of body[data-ff]).

// AST builders — fork's rules.py grammar (field/lit/mul/sub/clamp), so the invariant reads like the contract.
const field = (path: string) => ({ op: 'field', path })
const lit = (value: number | string | boolean) => ({ op: 'lit', value })
const mul = (a: unknown, b: unknown) => ({ op: 'mul', args: [a, b] })
const sub = (a: unknown, b: unknown) => ({ op: 'sub', args: [a, b] })
const clamp = (x: unknown, lo: unknown, hi: unknown) => ({ op: 'clamp', args: [x, lo, hi] })
const select = (path: string, cases: Record<string, unknown>, def?: unknown) =>
  def === undefined ? { select: path, cases } : { select: path, cases, default: def }

// THE MODAL ALLOCATION INVARIANT (RESOLVER-CONTRACT.md §3, HOST/MODAL) — px numbers (the host appends the unit).
// pad_top: continuous reclaim-by-height (short landscape → small, tall → up to 16). pad_x/full_width/radius:
// discrete by orient. chrome (top bars) subtracted for the available frame height.
const CHROME_PX = 56
export const MODAL_INVARIANT: Record<string, unknown> = {
  pad_top: clamp(mul(field('device.h'), lit(0.02)), lit(4), lit(16)),
  // ★ select CASES are RAW results — resolve_slot returns cases[key] AS-IS (NOT re-evaluated). A lit() AST here
  //   would be returned as the {op,value} OBJECT, not the number (caught by-use on the bounce → "[object Object]").
  pad_x: select('device.orient', { portrait: 0, landscape: 12 }, 12),
  frame_max_h: sub(field('device.h'), lit(CHROME_PX)),
}

export type Coordinate = { device: { w: number; h: number; orient: 'portrait' | 'landscape' } }

// the live device-coordinate (the ROOT — screen-size; orient derived h>w). Matches App's classify()/body[data-ff].
export function coordinateFromWindow(): Coordinate {
  const w = window.innerWidth
  const h = window.innerHeight
  return { device: { w, h, orient: h > w ? 'portrait' : 'landscape' } }
}

// map a resolved slot name → the CSS custom property the surface.css rules read (with a data-ff fallback in var()).
const SLOT_VAR: Record<string, string> = {
  pad_top: '--res-modal-pad-top',
  pad_x: '--res-modal-pad-x',
  frame_max_h: '--res-modal-frame-max-h',
}
// numeric slots that need a px unit when written to CSS (the resolver returns raw numbers).
const PX_SLOTS = new Set(['pad_top', 'pad_x', 'frame_max_h'])

let _seq = 0 // monotonic guard — a slow resolve from an old coordinate never clobbers a newer one (resize storm).

// Resolve the MODAL allocation for the current coordinate and apply it as CSS vars on :root. DEGRADE-CLEAN: any
// failure leaves the vars UNSET → the body[data-ff] CSS fallbacks hold (no change, no throw). Idempotent; safe to
// call on mount + every resize/orientationchange.
export async function resolveAndApplyModal(): Promise<void> {
  const seq = ++_seq
  const coordinate = coordinateFromWindow()
  let resolved: Record<string, unknown> | null = null
  try {
    const r = await fetch('/api/resolver', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ invariant: MODAL_INVARIANT, coordinate }),
    })
    const data = await r.json().catch(() => null)
    if (r.ok && data && data.ok === true && data.resolved && typeof data.resolved === 'object') {
      resolved = data.resolved as Record<string, unknown>
    }
    // else: committed-not-live / fail-loud teaching-error → degrade-clean (leave vars unset; CSS fallback holds).
  } catch {
    /* network/parse → degrade-clean */
  }
  if (seq !== _seq) return // a newer coordinate superseded this resolve
  const root = document.documentElement.style
  for (const [slot, cssVar] of Object.entries(SLOT_VAR)) {
    const v = resolved ? resolved[slot] : undefined
    // GUARD (fail-safe, found by-use on the bounce): only write a PRIMITIVE. A non-number/string resolved value
    // (e.g. a malformed slot that returned an AST object) must NEVER become "[object Object]" in CSS — that breaks
    // the whole shorthand → 0 (a regression). Skip it → the var()'s data-ff fallback governs (degrade-clean, never
    // regress). Defense-in-depth alongside fixing the slot itself.
    if (v === undefined || v === null || (typeof v !== 'number' && typeof v !== 'string')) {
      root.removeProperty(cssVar)
      continue
    }
    root.setProperty(cssVar, PX_SLOTS.has(slot) && typeof v === 'number' ? `${v}px` : String(v))
  }
}
