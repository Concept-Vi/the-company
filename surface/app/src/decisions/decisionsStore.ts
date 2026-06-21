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
  subtype?: string // the decision's kind (authorize/trade-off/theorem-fork) — the transition fallback keys on it
  owner?: string // the REGISTRY-TRUE side: 'tim' | 'fabric' — whose call this is (composition's field; the filter keys on it)
}

// ★ THE TIM-FACING FILTER — REGISTRY-TRUE: the decision declares its OWN side via `owner` ('tim' | 'fabric'),
// resolved server-side from its subtype (decision_subtypes[subtype].owner) and exposed on /api/decisions. The
// operator stack is owner==='tim' — HIS decisions, not the fabric's settles / legacy rows. A NEW subtype declares
// its own side, so this filter NEVER needs editing again — no hardcoded subtype-set. (The transition fallback was
// removed once owner went live on the feed, bounce g-1782026782 — verified by use: owner=='tim' ×14, the 'fabric'
// and legacy/untyped rows correctly excluded.)
function isTimFacing(d: Record<string, unknown>): boolean {
  return String(d.owner ?? '') === 'tim'
}

// `error` = a COLD-LOAD failure (nothing to show — fail loud). `refreshError` = a REFRESH failed but we still hold
// a valid last-good list (e.g. a transient 500 during a routine bridge bounce) → keep the list, flag subtly, never
// contradict the cards with a "couldn't load" banner. The two are mutually exclusive by construction (see the catch).
type DState = { pending: StackItem[]; loading: boolean; error: string | null; refreshError: boolean; open: boolean }

let state: DState = { pending: [], loading: false, error: null, refreshError: false, open: false }
const subs = new Set<() => void>()
let started = false
let loadSeq = 0 // monotonic load token — a stale list/enrichment never clobbers a newer load

function set(patch: Partial<DState>) {
  state = { ...state, ...patch }
  subs.forEach((f) => f())
}

export async function loadDecisions() {
  const seq = ++loadSeq
  set({ loading: true, error: null, refreshError: false })
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
      // pending AND Tim-facing — his queue holds HIS decisions (owner=='tim'), not the fabric's settles / legacy rows.
      .filter((d) => String(d.state ?? 'pending') === 'pending' && isTimFacing(d))
      .map((d) => {
        const id = String(d.id)
        const prev = known.get(id)
        return {
          id,
          address: String(d.address),
          type: 'decision-sequence' as const, // the only landed type; A4 will declare the rest on the record
          name: String(d.name ?? ''),
          state: d.state as string | undefined,
          subtype: d.subtype as string | undefined,
          owner: d.owner as string | undefined, // registry-true side, carried for legibility (registry-is-truth)
          recommended_label: d.recommended_label as string | undefined,
          meaning: prev?.meaning, // carried forward (undefined on a genuine first-load) → enrich() fills it
          reversibility: prev?.reversibility,
        }
      })
    if (seq !== loadSeq) return // a newer load superseded this one
    set({ pending, loading: false })
    enrich(pending) // fire-and-forget: patch real meaning + reversibility as each record resolves
  } catch {
    if (seq !== loadSeq) return
    // A failed refresh must NOT contradict good data already on screen. Cold-load failure (nothing to show yet) →
    // the hard error (fail loud, with retry). Refresh failure WITH items present (e.g. a transient 500 while the
    // bridge bounces — routine) → keep the last-good queue + a SUBTLE honest flag; never paint "couldn't load" over
    // valid cards. (Found by use: a routine bounce 500'd /api/decisions mid-refresh → the red banner sat over the 14.)
    if (state.pending.length === 0) set({ error: 'Couldn’t load what needs you just now.', loading: false })
    else set({ refreshError: true, loading: false })
  }
}

// ENRICH each item from its OWN registry record (/api/territory) — the real question + reversibility — so the stack
// is a legible preview. Soft-degrade per item: a record that won't load just stays a name + suggestion (never blocks
// the row, never a fake value). NO load-token abort here: a meaning patch is keyed BY ID and merged into whatever is
// CURRENTLY in state.pending (an id that's no longer shown is a harmless no-op) — so it is safe to apply regardless of
// which load fetched it. (Found by use: with the old hard seq-abort, opening the list WHILE the mount-load's enrich
// was still in flight discarded that enrichment — the open's reload bumped loadSeq — so meaning FLICKERED in a beat
// later instead of showing immediately. Merge-by-id makes the in-flight enrichment still land on the rows on screen.)
async function enrich(items: StackItem[]) {
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
