import { useEffect, useState } from 'react'

// THE BOARD-VIEW STORE — the data layer for FACE-1 breadth surface #2: the fabric Noticeboard as GROUPED sections
// (by type, or state). Mirrors channelStore/sessionDrillStore (the ONE subscribe-store pattern). Like channel-view,
// board-view is ONE view of the WHOLE board — so this store loads /api/board and holds the raw rows; the RENDER is
// DNA's (boardRecord adapter → boardGroups organism → renderArchetype 'board-view'), mounted by the host.
// registry-is-truth: we hold what /api/board declares and branch on nothing it doesn't. Fail-loud (honest message +
// retry, never a silent empty).
//
// ★ DATA SHAPE (grounded, verified live via /api/board): {items:[{id, address, type, source, state, title, channel,
//   thread, links, created, updated, author_session, body, history}], …}. DNA's boardRecord(rows,{groupBy}) maps this
//   → {identity:{title:"The board",address:"board://"}, groups:[{group, count, items:[{label,state,type,channel,
//   updated,address}]}], total}. boardGroups({groups}) renders the grouped sections into the body shape slot.

export type BoardRow = {
  id: string
  address: string
  type: string
  state: string
  title: string
  channel: string | null
  updated: string | null
  created: string | null
}

type BState = {
  rows: BoardRow[]
  loading: boolean
  error: string | null
  open: boolean
}

let state: BState = { rows: [], loading: false, error: null, open: false }
const subs = new Set<() => void>()
let loadSeq = 0

function set(patch: Partial<BState>) {
  state = { ...state, ...patch }
  subs.forEach((f) => f())
}

// THE BOARD — fork's live /api/board. Fail-loud on error (honest message + retry, never a silent empty board).
export async function loadBoard() {
  const seq = ++loadSeq
  set({ loading: true, error: null })
  try {
    const r = await fetch('/api/board')
    if (!r.ok) throw new Error(`HTTP ${r.status}`)
    const d = await r.json()
    const raw: Array<Record<string, unknown>> = Array.isArray(d) ? d : d.items || d.board || []
    const rows: BoardRow[] = raw.map((c) => ({
      id: String(c.id ?? ''),
      address: String(c.address ?? c.id ?? ''),
      type: String(c.type ?? 'other'),
      state: String(c.state ?? ''),
      title: String(c.title ?? c.id ?? '(untitled)'),
      channel: (c.channel as string) ?? null,
      updated: (c.updated as string) ?? null,
      created: (c.created as string) ?? null,
    }))
    if (seq !== loadSeq) return
    set({ rows, loading: false })
  } catch {
    if (seq !== loadSeq) return
    set({ error: 'Couldn’t load the board just now.', loading: false })
  }
}

export function openBoard() {
  set({ open: true })
  loadBoard() // refresh at the moment of looking
}
export function closeBoard() {
  set({ open: false })
}

let started = false
function ensureStarted() {
  if (started) return
  started = true
}

export function useBoard(): BState {
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
