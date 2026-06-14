// THIN, FAIL-LOUD CLIENT over the bridge (:8770 via the /api proxy).
// The surface is THIN over a thick contract (RESEARCH-SYNTHESIS §B). Types mirror the VERIFIED
// projection contract (runtime/projection.py:819-893) — build the renderer against THIS shape.

export type ProjPoint = {
  seq: number
  kind: string
  sector: string
  theta: number // radians
  r: number // [0.06,1.0]; pile >1 in nucleation
  depth: number
  cell: { i: number; j: number; d: number }
  address: string
  summary: string
  ts: unknown
  phases: { day: number; week: number }
  source?: string
  r_struct?: number
  strain?: number
  pull_a?: number
  pull_b?: number
  lean?: number
  pole?: 'a' | 'b' | '—'
  fit?: number
  assigned?: string
  inside?: boolean
  pile_cluster?: number
  tail?: boolean
  born?: boolean
  r_unknown?: boolean
}

export type Sector = { id: string; label: string; from: number; to: number }
export type Edge = { from: number; to: number; bidir?: boolean }
export type BindingRef = { id: string; label: string }

export type Projection = {
  center: string
  now: string
  n: number
  binding: {
    id: string
    label: string
    angle_from: string
    radius_from: string
    order_by: string
    radius_normalized?: boolean
    space?: string
    poles?: { a: unknown; b: unknown }
    types_space?: string
  }
  bindings: BindingRef[]
  sectors: Sector[]
  edges: Edge[]
  separation?: unknown
  nucleation?: unknown
  rings: number
  grid: number
  lock: string
  points: ProjPoint[]
  count: number
}

// The R2 scored context bundle (GET /api/context). Kept loose — we read what's present, fail loud on error.
export type ContextBundle = {
  address: string
  items?: Array<{ kind?: string; text?: string; summary?: string; ts?: unknown; score?: number }>
  more?: number
  error?: string
  [k: string]: unknown
}

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

export function fetchProjection(params: Record<string, string | number | undefined>): Promise<Projection> {
  const qs = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) if (v !== undefined && v !== '') qs.set(k, String(v))
  return getJSON<Projection>(`/api/projection?${qs.toString()}`)
}

export function fetchContext(address: string): Promise<ContextBundle> {
  return getJSON<ContextBundle>(`/api/context?address=${encodeURIComponent(address)}`)
}
