import { useEffect, useState } from 'react'

// THE CHANNEL-VIEW STORE — the data layer for FACE-1 breadth surface #1: the live fabric as a GRAPH (channels as
// nodes, weighted by posts, warmth by recency; edges = members→session-spokes · coordinator · promoted_to lineage).
// Mirrors sessionDrillStore/decisionsStore (the ONE subscribe-store pattern). Unlike the session-drill (a list →
// drill), channel-view is ONE graph of the WHOLE fabric — so this store just loads /api/channels and holds the raw
// rows; the RENDER is DNA's (channelGraph adapter → hubNetwork organism → renderArchetype 'channel-view'), mounted
// by the host. registry-is-truth: we hold what /api/channels declares and branch on nothing it doesn't. Fail-loud
// on the load (honest message + retry, never a silent empty).
//
// ★ DATA SHAPE (grounded, NOT guessed — verified live via /api/channels):
//   {ok, channels:[{id, kind, name, purpose, mode, coordinator, status, members:{<uuid>:{participation,added}},
//    origin, created, last_activity, posts, seq, promoted_to}]}. DNA's channelGraph(rawChannels) maps this →
//   {identity:{title,address}, nodes:[{label,score,warmth}], edges:[{from,to,kind}], hub}. NOTE: channelGraph's
//   edges loop expects `members` as an ARRAY but /api/channels serves an OBJECT — the host normalizes at the call
//   site (ChannelView) until DNA's adapter handles the object shape (flagged to DNA, code-grounded).

export type ChannelRow = {
  id: string
  kind: string
  name: string
  posts: number
  coordinator: string | null
  promoted_to: string | null
  last_activity: string | null
  members: Record<string, unknown> // {<uuid>:{participation,added}} — normalized to ids at the render call site
}

type CState = {
  channels: ChannelRow[]
  loading: boolean
  error: string | null
  open: boolean
}

let state: CState = { channels: [], loading: false, error: null, open: false }
const subs = new Set<() => void>()
let loadSeq = 0

function set(patch: Partial<CState>) {
  state = { ...state, ...patch }
  subs.forEach((f) => f())
}

// THE FABRIC — fork's live /api/channels. Fail-loud on error (honest message + retry, never a silent empty graph).
export async function loadChannels() {
  const seq = ++loadSeq
  set({ loading: true, error: null })
  try {
    const r = await fetch('/api/channels')
    if (!r.ok) throw new Error(`HTTP ${r.status}`)
    const d = await r.json()
    const raw: Array<Record<string, unknown>> = Array.isArray(d) ? d : d.channels || d.items || []
    const channels: ChannelRow[] = raw.map((c) => ({
      id: String(c.id ?? ''),
      kind: String(c.kind ?? ''),
      name: String(c.name ?? c.id ?? ''),
      posts: Number(c.posts ?? 0),
      coordinator: (c.coordinator as string) ?? null,
      promoted_to: (c.promoted_to as string) ?? null,
      last_activity: (c.last_activity as string) ?? null,
      members: (c.members && typeof c.members === 'object' ? (c.members as Record<string, unknown>) : {}),
    }))
    if (seq !== loadSeq) return
    set({ channels, loading: false })
  } catch {
    if (seq !== loadSeq) return
    set({ error: 'Couldn’t load the fabric just now.', loading: false })
  }
}

export function openChannels() {
  set({ open: true })
  loadChannels() // refresh at the moment of looking
}
export function closeChannels() {
  set({ open: false })
}

let started = false
function ensureStarted() {
  if (started) return
  started = true
}

export function useChannels(): CState {
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
