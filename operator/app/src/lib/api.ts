// HARVESTED from surface/app/src/lib/api.ts (the scout-verified clean quarry — K1):
// the THIN, FAIL-LOUD CLIENT over the bridge (:8770 via the /api proxy in dev; same-origin
// relative /api when served BY the bridge at /app — the SAME-ORIGIN law, K0). The getJSON
// core + ApiError are kept VERBATIM (their fail-loud discipline is the point); the fetch
// helpers are re-typed for THIS app's endpoints (greeting), not the projection surface's.

// ---- the verbatim fail-loud core (surface/app/src/lib/api.ts:113-133) --------------------
async function getJSON<T>(url: string): Promise<T> {
  let res: Response
  try {
    res = await fetch(url, { headers: { Accept: 'application/json' } })
  } catch (e) {
    // Network/proxy failure — surface it, never swallow (no-silent-failures).
    throw new ApiError(`network error reaching ${url}: ${(e as Error).message}`)
  }
  const text = await res.text()
  if (!res.ok) {
    // The bridge fails LOUD with a message — carry it to the surface as a Notice.
    throw new ApiError(`${res.status} from ${url}: ${text.slice(0, 300)}`)
  }
  try {
    return JSON.parse(text) as T
  } catch {
    throw new ApiError(`bad JSON from ${url}: ${text.slice(0, 200)}`)
  }
}

export class ApiError extends Error {}

// ---- this app's endpoints ----------------------------------------------------------------

// GET /api/greeting — S2 "caught-up-in-one-glance" (runtime/suite.py greeting()):
// what was BUILT since last contact (git-ground-truth headlines), what WAITS on the
// operator's gate, the NOW signal, and any returned memories. Types mirror that return
// shape (kept loose where the suite composes freely — we read what's present, fail loud
// on transport error, never invent fields).
export type Greeting = {
  since: string | null
  built: string[]
  built_total: number
  waiting_on_you: Array<{ id: string | null; title: string }>
  waiting_total: number
  now: {
    mode?: string
    presence?: string
    dials?: Record<string, string>
    surfaced_pending?: number
    last_operator_contact?: string | null
    [k: string]: unknown
  }
  returned_memories: Array<{
    memory?: string
    condition?: string
    fired_because?: string
    what_returns?: string
  }>
}

export function fetchGreeting(since?: string): Promise<Greeting> {
  const qs = since ? `?since=${encodeURIComponent(since)}` : ''
  return getJSON<Greeting>(`/api/greeting${qs}`)
}

// GET /api/now — the now-signal (runtime/suite.py now_signal): mode, dials, and the LAST EVENT
// (seq + kind + ts). The Arrival pulse reads last_event.seq once so its SSE tail starts at the
// live edge (streaming ?since=-1 would replay the whole corpus — tens of thousands of events).
export type NowSignal = {
  mode?: string
  presence?: string
  dials?: Record<string, string>
  surfaced_pending?: number
  last_event?: { seq: number; ts?: string; kind?: string; [k: string]: unknown }
  [k: string]: unknown
}

export function fetchNow(): Promise<NowSignal> {
  return getJSON<NowSignal>('/api/now')
}

// The R2 scored context bundle (GET /api/context) — harvested with address.ts, whose
// contextAt() rides it (surface/app/src/lib/api.ts:83-90,141-143 verbatim).
export type ContextBundle = {
  address: string
  items?: Array<{ kind?: string; text?: string; summary?: string; ts?: unknown; score?: number }>
  more?: number
  error?: string
  [k: string]: unknown
}

export function fetchContext(address: string): Promise<ContextBundle> {
  return getJSON<ContextBundle>(`/api/context?address=${encodeURIComponent(address)}`)
}
