import { useEffect, useState } from 'react'

// THE DECISIONS STORE — one source of truth for "what decisions is the Company waiting on?", shared by the entry
// (DecisionsBar, in each layout) and the list modal (DecisionsInbox, an App-root sibling). A tiny subscribe store
// so both render from ONE fetch + ONE open-state (no double-fetch, no drift between the count and the list).
// registry-is-truth: the data is /api/decisions (fork's pending-decisions registry); we render what it declares and
// branch on nothing. Fail-loud on error (an honest message + retry, never a silent empty).
//
// WHY A SEPARATE STORE (not the existing one): the surface's only other module-level store is `locus`
// (lib/address.ts — `{ address, notice }`), the address-capture + global-notice instrumentation layer. Decisions
// are a different concern (a fetched registry of pending decisions + the list's open-state), so they don't belong
// folded into locus; this mirrors locus's SAME subscribe-store shape rather than inventing a new pattern.

export type PendingDecision = { id: string; address: string; name: string; state?: string; recommended_label?: string }

type DState = { pending: PendingDecision[]; loading: boolean; error: string | null; open: boolean }

let state: DState = { pending: [], loading: false, error: null, open: false }
const subs = new Set<() => void>()
let started = false

function set(patch: Partial<DState>) {
  state = { ...state, ...patch }
  subs.forEach((f) => f())
}

export async function loadDecisions() {
  set({ loading: true, error: null })
  try {
    const r = await fetch('/api/decisions')
    if (!r.ok) throw new Error(`HTTP ${r.status}`)
    const data = await r.json()
    const list: PendingDecision[] = Array.isArray(data) ? data : data.decisions || data.items || []
    // keep only the ones still WAITING on the operator (a decided one drops off)
    set({ pending: list.filter((d) => (d.state || 'pending') === 'pending'), loading: false })
  } catch {
    set({ error: 'Couldn’t load the decisions just now.', loading: false })
  }
}

export function openDecisionsList() {
  set({ open: true })
  loadDecisions() // refresh at the moment of looking
}
export function closeDecisionsList() {
  set({ open: false })
}

// subscribe a component to the store; on first mount, kick the initial load and wire a refresh on any decision write
// (gallery:rerender fires on a take → a decided card leaves the pending list).
export function useDecisions(): DState {
  const [, force] = useState(0)
  useEffect(() => {
    const cb = () => force((n) => n + 1)
    subs.add(cb)
    if (!started) {
      started = true
      loadDecisions()
    }
    const refresh = () => loadDecisions()
    window.addEventListener('gallery:rerender', refresh)
    return () => {
      subs.delete(cb)
      window.removeEventListener('gallery:rerender', refresh)
    }
  }, [])
  return state
}
