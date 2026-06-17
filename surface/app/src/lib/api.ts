// THIN, FAIL-LOUD CLIENT over the bridge (:8770 via the /api proxy).
// The surface is THIN over a thick contract (RESEARCH-SYNTHESIS §B). Types mirror the VERIFIED
// projection contract (runtime/projection.py:819-893) — build the renderer against THIS shape.

export type ProjPoint = {
  seq: number
  kind: string
  // the kind's HUMAN words (registry-true, declared-first → humanized-id fallback) — render THESE, never the
  // machine `kind` (operator-law). Present on every point from the projection contract.
  kind_name?: string
  kind_meaning?: string | null
  sector: string
  // the sector's HUMAN name (registry-true, via the lens's meta-registry) — render THIS in the "in" row, never
  // the machine `sector` id (operator-law). On the Kinds lens it equals kind_name; on other lenses it's the
  // node-type/row human name. Present on every point from the projection contract.
  sector_name?: string
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
  // G11 scale pyramid — present only at a COARSE rung (the point is a theme/cluster centroid, not a unit)
  scale_size?: number
  scale_members?: number
  scale_exemplar?: string
}

export type Sector = { id: string; label: string; meaning?: string | null; from: number; to: number }
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
    emb?: string | null   // the active embedder LAYER (null = default/BGE) — the multi-layer model
    res?: number | null   // the active MRL resolution (null = full dim)
    quant?: string | null // the active representation: 'binary' = sign-bit/Hamming, null = full float
    // the binding's DECLARED human meaning (registry-true) — the Legend renders this instead of mechanical
    // jargon (declared-first; null = fall back to the computed lines). Field-set = composition's legibility seed.
    meta?: { name?: string; is?: string; fills?: string; why?: string } | null
  }
  bindings: BindingRef[]
  sectors: Sector[]
  edges: Edge[]
  separation?: unknown
  nucleation?: unknown
  scale?: { space?: string; rung: number | string; rungs?: number[]; n_units?: number }
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

// The STRUCTURED territory at an address (GET /api/territory) — the scheme-agnostic SOURCE resolver
// (runtime/territory.py territory_for): the comprehended record + provenance BEHIND an addressed thing,
// resolved through the ONE resolver. Kept loose (we read what's present); the surface extracts the
// human-legible parts (operator-law: prose, never a raw dict/code/address) and fails loud on transport error.
export type Territory = {
  address: string
  scheme?: string | null
  identity?: unknown
  identity_kind?: string | null
  corpus_content?: unknown
  corpus_record?: unknown
  relations?: { edges_in?: unknown[]; edges_out?: unknown[]; [k: string]: unknown } | null
  notes?: string[]
  legs_present?: Record<string, boolean>
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

// The V's "Source" verb backing — resolve the comprehended record + provenance behind an addressed point.
export function fetchTerritory(address: string): Promise<Territory> {
  return getJSON<Territory>(`/api/territory?address=${encodeURIComponent(address)}`)
}

// The multi-layer model's self-description: {space: [embedder-layer, …]} — registry-true (the engine scans the
// store, the surface never hardcodes the layer set). The layer picker reads this to offer the available embedders.
export function fetchLayers(): Promise<Record<string, string[]>> {
  return getJSON<Record<string, string[]>>(`/api/layers`)
}

// The per-layer full vector DIMENSION: {space: {embedder: dim}} (e.g. {repo: {default: 1024, pplx: 2560}}).
// The resolution picker reads this to derive the MRL zoom ladder (powers of two ≤ the full dim) — registry-true,
// never a hardcoded dim. Fetched once; the active (space, layer) selects which ladder to offer.
export function fetchLayerDims(): Promise<Record<string, Record<string, number>>> {
  return getJSON<Record<string, Record<string, number>>>(`/api/layer-dims`)
}
