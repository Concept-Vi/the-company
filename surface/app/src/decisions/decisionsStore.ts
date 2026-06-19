import { useEffect, useState } from 'react'

// THE CHANNEL-STACK STORE — one source of truth for "what has the Company's autonomous work surfaced that only the
// operator can settle?", shared by the entry (DecisionsBar) and the stack modal (DecisionsInbox, an App-root
// sibling). A tiny subscribe store so both render from ONE fetch + ONE open-state (no double-fetch, no drift between
// the count and the list). registry-is-truth: the data is the Company's pending registry; we render what it
// declares and branch on nothing it doesn't. Fail-loud on the list load (an honest message + retry, never a silent
// empty); soft-degrade per item on enrichment (a row whose record won't load still shows its name + suggestion).
//
// A channel-stack ITEM is a TYPE (criteria A4 — `decision-sequence | presentation | explanation | verify-request`,
// the axes-are-registries law: adding a kind is a row, not engine code). TODAY the registry (/api/decisions)
// declares ONLY decision items, so we map each to type:'decision-sequence' — the only landed type — and the render
// dispatches on `type` with ONE real case + a fail-loud default. That single switch IS the seam A4 lands into; we do
// NOT author the wider type-enum here (that's composition's lane) and we do NOT build renderers for kinds no real
// data exercises yet (fork's stack-feed, B1, lands the other item-types).
//
// WHY A SEPARATE STORE (not the existing one): the surface's only other module-level store is `locus`
// (lib/address.ts — `{ address, notice }`), the address-capture + global-notice layer. The stack is a different
// concern (a fetched registry of operator-items + the modal's open-state), so it mirrors locus's SAME subscribe-store
// shape rather than inventing a new pattern.

// the only landed stack item-type. A4 (composition) widens this union; the render's fail-loud default already holds
// the seam, so a new kind shows honestly (never silently) the moment its data arrives.
export type StackItemType = 'decision-sequence'

export type StackItem = {
  id: string
  address: string
  type: StackItemType
  name: string
  state?: string
  recommended_label?: string
  // ENRICHED from the item's own registry record (/api/territory) so the stack reads as a legible at-a-glance
  // preview, not a bare name list. Absent until enrichment resolves (or if a record won't load) → the row degrades
  // soft to name + suggestion. Every shown field is a REAL field off the record (registry-is-truth, no fabrication).
  meaning?: string // identity.meaning — the actual question, in human words
  reversibility?: string // identity.legibility.is — e.g. "Reversible · your latest answer wins"
}

type DState = { pending: StackItem[]; loading: boolean; error: string | null; open: boolean }

let state: DState = { pending: [], loading: false, error: null, open: false }
const subs = new Set<() => void>()
let started = false
let loadSeq = 0 // monotonic load token — a stale list/enrichment never clobbers a newer load

function set(patch: Partial<DState>) {
  state = { ...state, ...patch }
  subs.forEach((f) => f())
}

export async function loadDecisions() {
  const seq = ++loadSeq
  set({ loading: true, error: null })
  try {
    const r = await fetch('/api/decisions')
    if (!r.ok) throw new Error(`HTTP ${r.status}`)
    const data = await r.json()
    const raw: Array<Record<string, unknown>> = Array.isArray(data) ? data : data.decisions || data.items || []
    // CARRY FORWARD already-known enrichment by id: a reload (reopen, or a gallery:rerender) must NOT drop the
    // meaning/reversibility we already have, or every open would paint names-only then GROW as enrich() patches
    // back — a shrink-then-grow layout shift on the live surface. Merging by id means a reopen shows the known
    // enriched rows immediately (no shift); enrich() below still refreshes in case a record changed.
    const known = new Map(state.pending.map((p) => [p.id, p]))
    // keep only the ones still WAITING on the operator (a decided one drops off the stack) + map to the typed item.
    const pending: StackItem[] = raw
      .filter((d) => (String(d.state ?? 'pending')) === 'pending')
      .map((d) => {
        const id = String(d.id)
        const prev = known.get(id)
        return {
          id,
          address: String(d.address),
          type: 'decision-sequence' as const, // the only landed type; A4 will declare the rest on the record
          name: String(d.name ?? ''),
          state: d.state as string | undefined,
          recommended_label: d.recommended_label as string | undefined,
          meaning: prev?.meaning, // carried forward (undefined on a genuine first-load) → enrich() fills it
          reversibility: prev?.reversibility,
        }
      })
    if (seq !== loadSeq) return // a newer load superseded this one
    set({ pending, loading: false })
    enrich(pending, seq) // fire-and-forget: patch real meaning + reversibility as each record resolves
  } catch {
    if (seq !== loadSeq) return
    set({ error: 'Couldn’t load what needs you just now.', loading: false })
  }
}

// ENRICH each item from its OWN registry record (/api/territory) — the real question + reversibility — so the stack
// is a legible preview. Soft-degrade per item: a record that won't load just stays a name + suggestion (never blocks
// the row, never a fake value). Guarded by the load token so a superseded enrichment can't clobber a newer load.
async function enrich(items: StackItem[], seq: number) {
  const results = await Promise.allSettled(
    items.map(async (it) => {
      const r = await fetch(`/api/territory?address=${encodeURIComponent(it.address)}`)
      if (!r.ok) throw new Error(`HTTP ${r.status}`)
      const d = await r.json()
      const idn = (d.identity || {}) as Record<string, unknown>
      const leg = (idn.legibility || {}) as Record<string, unknown>
      return { id: it.id, meaning: idn.meaning as string | undefined, reversibility: leg.is as string | undefined }
    }),
  )
  if (seq !== loadSeq) return // superseded; don't clobber a newer load
  const patch = new Map<string, { meaning?: string; reversibility?: string }>()
  for (const res of results) if (res.status === 'fulfilled') patch.set(res.value.id, res.value)
  if (patch.size === 0) return
  set({
    pending: state.pending.map((it) => {
      const p = patch.get(it.id)
      return p ? { ...it, meaning: p.meaning, reversibility: p.reversibility } : it
    }),
  })
}

export function openDecisionsList() {
  set({ open: true })
  loadDecisions() // refresh at the moment of looking
}
export function closeDecisionsList() {
  set({ open: false })
}

// start the store ONCE (on the first subscriber): kick the initial load + wire the refresh-on-write listener at the
// STORE level — NOT per useDecisions subscriber. (Both DecisionsBar + DecisionsInbox subscribe; a per-subscriber
// gallery:rerender listener fired N reloads per event — verified 2× per rerender. One store-level listener = one
// reload regardless of subscriber count.) The store is app-lifetime, so the listener is never removed (no leak).
function ensureStarted() {
  if (started) return
  started = true
  loadDecisions() // initial load
  // gallery:rerender fires on a decision write (a take → a cleared item leaves the stack); reload the registry.
  window.addEventListener('gallery:rerender', () => loadDecisions())
}

// subscribe a component to the store; the store self-starts on the first subscriber.
export function useDecisions(): DState {
  const [, force] = useState(0)
  useEffect(() => {
    const cb = () => force((n) => n + 1)
    subs.add(cb)
    ensureStarted()
    return () => {
      subs.delete(cb)
    }
  }, [])
  return state
}
