import { useEffect, useState } from 'react'

// THE TRANSCRIPT-VIZ STORE — the data layer for FACE-1 breadth surface: the WHOLE transcript corpus (35,904 chunks
// over 1,051 sessions) searched BY MEANING and shown as a CONSTELLATION (recollection's backend, the search-and-see
// face). Mirrors channelStore/decisionsStore (the ONE subscribe-store pattern) with ONE difference: it is
// QUERY-DRIVEN — opening the surface shows a search prompt, and a query loads the result set. So this store holds
// the FULL /api/transcript-search response (not just rows): DNA.faceRecord.transcriptRecord reads api.q, api.mode_used
// AND api.semantic.available off the whole envelope, so the host passes the whole thing through. The RENDER is DNA's
// (transcriptRecord adapter → constellation organism → renderArchetype 'transcript-viz'), mounted by the host.
//
// ★ DATA SHAPE (grounded, NOT guessed — verified LIVE via curl against the running bridge :8770):
//   {ok:true, q, mode_requested, mode_used:'semantic'|'lexical', semantic:{available,why}, index:{chunks,files,…},
//    chunks_matched, sessions_found, results:[{session_address:"session://<id>", title|name, hits_in_session, score,
//    state, snippet, point, primary_verb, commands}], note}. mode_used='semantic' when the embedder is up (real
//    cosine scores ~0.4) → the constellation glow gradient is real; 'lexical' → DNA marks the field degraded.
//   The adapter's RAW mode maps results→session star-nodes (weight=hits, brightness=score, color=state). honest
//   degrade: an empty `results` is an honest no-match (chunks_matched=0), shown as a quiet line, never a blank panel.

export type TranscriptResult = {
  session_address: string
  title: string | null
  name: string | null
  hits_in_session: number
  score: number
  state: string | null
  snippet: string
}

// the full search envelope — the adapter consumes the whole thing (q + mode_used + semantic + results)
export type TranscriptResponse = Record<string, unknown> & {
  ok?: boolean
  q?: string
  mode_used?: string
  semantic?: { available?: boolean; why?: string }
  chunks_matched?: number
  sessions_found?: number
  results?: TranscriptResult[]
}

type TState = {
  query: string // the input's current text (controlled)
  raw: TranscriptResponse | null // the last SEARCH's full response (null = no search yet)
  loading: boolean
  error: string | null
  open: boolean
}

let state: TState = { query: '', raw: null, loading: false, error: null, open: false }
const subs = new Set<() => void>()
let loadSeq = 0

function set(patch: Partial<TState>) {
  state = { ...state, ...patch }
  subs.forEach((f) => f())
}

// keep the input text in the store so the controlled <input> survives re-renders without local state races
export function setTranscriptQuery(query: string) {
  set({ query })
}

// THE SEARCH — recollection's /api/transcript-search?q= (semantic→lexical degrade, honest). k=24 < the constellation's
// 40-node cap → a full-but-bounded star field. Holds the WHOLE response (the adapter reads the envelope, not just rows).
// Fail-loud on error (honest message + retry, never a silent empty graph). seq-guards stale responses (last wins).
export async function searchTranscript(q: string) {
  const query = (q ?? '').trim()
  if (!query) return // empty query is a no-op (the prompt stays); never fires a bare ?q=
  const seq = ++loadSeq
  set({ loading: true, error: null })
  try {
    const r = await fetch(`/api/transcript-search?q=${encodeURIComponent(query)}&k=24`)
    if (!r.ok) throw new Error(`HTTP ${r.status}`)
    const d: TranscriptResponse = await r.json()
    if (seq !== loadSeq) return
    if (d.ok === false) throw new Error('search not ok')
    set({ raw: d, loading: false })
  } catch {
    if (seq !== loadSeq) return
    set({ error: 'Couldn’t search the corpus just now.', loading: false })
  }
}

export function openTranscript() {
  set({ open: true }) // query-driven: opening shows the search prompt; nothing loads until a query
}
export function closeTranscript() {
  set({ open: false })
}

export function useTranscript(): TState {
  const [, force] = useState(0)
  useEffect(() => {
    const cb = () => force((n) => n + 1)
    subs.add(cb)
    return () => {
      subs.delete(cb)
    }
  }, [])
  return state
}
