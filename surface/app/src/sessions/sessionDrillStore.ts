import { useEffect, useState } from 'react'

// THE SESSION-DRILL STORE — the data layer for the FACE-1 session-drill surface (the supervisor face: the list of
// Claude-Code sessions this machine has run → drill into one → its lenses). Mirrors decisionsStore/toolsStore (the
// ONE subscribe-store pattern, no fork) so the entry + the panel render from ONE fetch + ONE open-state. The RENDER
// is DNA's session-card organism (mounted by the host when it binds — composition's proof-gate); this store only
// fetches + holds the DATA + branches on nothing the data doesn't declare (registry-is-truth). Fail-loud on the
// list load (an honest message + retry, never a silent empty).
//
// ★ DATA SHAPES (grounded, NOT guessed):
//  • THE LIST — fork's `/api/sessions` (LIVE, verified): {sessions:[{id,name,cwd,state,last_activity,title,seq,…}],
//    total}. The session ROWS the surface lists.
//  • THE PER-SESSION LENS — recollection's session_recall ops (data-shape supplied by-use, t-1782022338):
//    catch_up {items:[{line,ts,attr,text}]} · open_loops {open:[{line,ts,attr,kind,likely_resolved,text}]} ·
//    directives {items:[{line,ts,bytes,text}]} · decisions · drift · timeline. ★ The lens ROUTE is NOT exposed yet
//    (no /api/session-recall on the bridge) — recollection flagged "coordinate the route with fork." So loadLens()
//    is a SEAM: it calls the agreed route once fork lands it; until then it degrades clean (honest "not ready"),
//    NOT a guessed URL (critical-comparison: don't build to an assumed route). LENS_ROUTE is the single edit-point.

export type SessionRow = {
  id: string
  name: string
  cwd: string
  state: string // 'closed' | live | …
  last_activity: string | null
  title: string | null
  seq: number
}

// the per-session lens shape (recollection's by-use contract) — what the drilled session-card renders.
export type LensItem = { line?: number; ts?: string; attr?: string; kind?: string; likely_resolved?: boolean; text: string }
export type SessionLens = {
  catch_up?: LensItem[]
  open_loops?: LensItem[]
  directives?: LensItem[]
  loading: boolean
  routeReady: boolean // false until fork's lens route exists → the card shows an honest "lenses coming" state
}

type SState = {
  sessions: SessionRow[]
  total: number
  loading: boolean
  error: string | null
  open: boolean
  selected: string | null // the drilled session id (null = the list)
  lens: SessionLens | null
}

let state: SState = { sessions: [], total: 0, loading: false, error: null, open: false, selected: null, lens: null }
const subs = new Set<() => void>()
let loadSeq = 0

function set(patch: Partial<SState>) {
  state = { ...state, ...patch }
  subs.forEach((f) => f())
}

// THE LIST — fork's live /api/sessions. Newest-active first (the surface's primary order); fail-loud on error.
export async function loadSessions() {
  const seq = ++loadSeq
  set({ loading: true, error: null })
  try {
    const r = await fetch('/api/sessions')
    if (!r.ok) throw new Error(`HTTP ${r.status}`)
    const d = await r.json()
    const raw: Array<Record<string, unknown>> = Array.isArray(d) ? d : d.sessions || d.items || []
    const sessions: SessionRow[] = raw.map((s) => ({
      id: String(s.id ?? ''),
      name: String(s.name ?? ''),
      cwd: String(s.cwd ?? ''),
      state: String(s.state ?? ''),
      last_activity: (s.last_activity as string) ?? null,
      title: (s.title as string) ?? null,
      seq: Number(s.seq ?? 0),
    }))
    if (seq !== loadSeq) return
    set({ sessions, total: Number(d.total ?? sessions.length), loading: false })
  } catch {
    if (seq !== loadSeq) return
    set({ error: 'Couldn’t load the sessions just now.', loading: false })
  }
}

// THE LENS ROUTE — fork's per-session lens route (3c173be, confirmed by the lead, aligned to recollection's
// session_lens spec): /api/session-recall?session=&op=<catch_up|open_loops|directives|decisions|drift|timeline|find>.
// Committed; goes LIVE on the checkpoint bounce → degrade-clean until then (a 404 → that lens stays empty, never a
// fabricated one). The single edit-point is now filled (was the pending seam).
const LENS_ROUTE = (id: string, op: string) => `/api/session-recall?session=${encodeURIComponent(id)}&op=${op}`

export async function loadLens(sessionId: string) {
  set({ lens: { loading: true, routeReady: true } })
  // fetch the 3 core lenses CONCURRENTLY (recollection's shapes: catch_up/directives → {items}, open_loops → {open}).
  // Each degrades clean per-op (route-not-live/404/empty → that lens empty; never blocks, never fabricates). With a
  // short timeout so a slow lens can't hang the card (the tool-face lesson).
  const fetchOp = async (op: string): Promise<LensItem[]> => {
    try {
      const ctrl = new AbortController()
      const to = setTimeout(() => ctrl.abort(), 4000)
      const r = await fetch(LENS_ROUTE(sessionId, op), { signal: ctrl.signal }).finally(() => clearTimeout(to))
      if (!r.ok) return []
      const d = await r.json()
      const arr = d.items || d.open || []
      return Array.isArray(arr) ? (arr as LensItem[]) : []
    } catch {
      return []
    }
  }
  const [catch_up, open_loops, directives] = await Promise.all([fetchOp('catch_up'), fetchOp('open_loops'), fetchOp('directives')])
  if (state.selected !== sessionId) return // a fast re-select superseded this → don't clobber
  set({ lens: { catch_up, open_loops, directives, loading: false, routeReady: true } })
}

export function openSessions() {
  set({ open: true, selected: null })
  loadSessions()
}
export function closeSessions() {
  set({ open: false })
}
export function selectSession(id: string | null) {
  set({ selected: id, lens: null })
  if (id) loadLens(id)
}

let started = false
function ensureStarted() {
  if (started) return
  started = true
  loadSessions()
}

export function useSessions(): SState {
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
