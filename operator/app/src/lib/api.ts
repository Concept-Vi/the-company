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

// ---- the operator-session token (#1b) ----------------------------------------------------
// GET /api/operator-session mints a per-process token on app boot (runtime/bridge.py
// _mint_operator_token); the app attaches it as X-Operator-Session on every CONSEQUENTIAL POST
// (approve/reject/comment — never on a plain read). Enforcement is flag-gated server-side today
// (`enforced` in the response) — sending it is FREE and future-proof either way: ignored when
// enforcement is off, required once it flips on. Minted ONCE at boot and held module-level (no
// re-mint per request — the surface mints ONE session token, not one per POST).
export type OperatorSession = { ok: boolean; operator_session: string; enforced: boolean; supervised_post: boolean }

let _operatorToken: string | null = null

export async function mintOperatorSession(): Promise<string> {
  const d = await getJSON<OperatorSession>('/api/operator-session')
  _operatorToken = d.operator_session
  return _operatorToken
}

// ---- the fail-loud POST core (mirrors getJSON's discipline — network/HTTP/JSON errors all
// surface as ApiError, never swallowed) -----------------------------------------------------
async function postJSON<T>(url: string, body: Record<string, unknown>): Promise<T> {
  let res: Response
  try {
    res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        ...(_operatorToken ? { 'X-Operator-Session': _operatorToken } : {}),
      },
      body: JSON.stringify(body),
    })
  } catch (e) {
    throw new ApiError(`network error POSTing ${url}: ${(e as Error).message}`)
  }
  const text = await res.text()
  if (!res.ok) {
    throw new ApiError(`${res.status} from ${url}: ${text.slice(0, 300)}`)
  }
  try {
    return JSON.parse(text) as T
  } catch {
    throw new ApiError(`bad JSON from ${url}: ${text.slice(0, 200)}`)
  }
}

// ---- GET /api/needs-me — the I1 NEEDS-ME INBOX (runtime/needs_me.py:needs_me_inbox) --------
// One card list folded from every registered `inbox_sources/*` row. `errors` is the fail-soft
// side-channel: a broken source shows up here LOUD — it never blanks the other sources' cards.
export type InboxVerb = { id: string; label: string; door: string }
export type InboxCard = {
  source: string
  id: string
  address: string
  title: string
  why: string
  verbs: InboxVerb[]
  created: string
}
export type NeedsMe = { cards: InboxCard[]; count: number; sources: string[]; errors: Array<{ source: string; error: string }> }

export function fetchNeedsMe(): Promise<NeedsMe> {
  return getJSON<NeedsMe>('/api/needs-me')
}

// ---- acting on a card's verb ----------------------------------------------------------------
// Doors carry different bodies (they are different bridge endpoints, not one uniform shape —
// registry-is-truth, not a fiction of uniformity): `/api/resolve` needs {id,choice,reason};
// `/api/decision` (a read-view, POST-shaped) needs only {id}; `/api/board/comment` needs
// {target,text} (free text — obligations/board_requests cards post a canned acknowledgement,
// see inbox_sources/obligations.py's honest-limitation note: this does NOT clear the underlying
// obligation, only /api/resolve's approve/reject and a real reply_to do that). Any OTHER door
// falls back to the generic {id, choice: verb.id} shape.
export type VerbResult = { ok: boolean; raw: unknown }

export async function actOnCard(card: InboxCard, verb: InboxVerb): Promise<VerbResult> {
  let raw: unknown
  if (verb.door === '/api/resolve') {
    raw = await postJSON(verb.door, { id: card.id, choice: verb.id, reason: '' })
  } else if (verb.door === '/api/decision') {
    raw = await postJSON(verb.door, { id: card.id })
  } else if (verb.door === '/api/board/comment') {
    raw = await postJSON(verb.door, {
      target: card.address,
      text: `Seen — Tim, via the Needs-Me inbox (“${card.title}”).`,
    })
  } else {
    raw = await postJSON(verb.door, { id: card.id, choice: verb.id })
  }
  return { ok: true, raw }
}
