import { useEffect, useState } from 'react'

// THE TOOLS STORE — one source of truth for the TOOL FACE (the pilot palette: click a tool → a human description
// + a friendly op-conditional form → run → a rendered result). Mirrors decisionsStore's subscribe-store shape (the
// ONE store pattern, not a fork) so the entry (ToolsBar) + the panel (ToolsPanel) render from ONE fetch + ONE
// open/selected state. registry-is-truth: the tool list comes from fork's /api/tools (gap 2 — name+schema+posture
// straight off the FastMCP registry); we render what it declares and branch on nothing.
//
// ★ SCAFFOLD STATE (2026-06-19): fork's /api/tools (gap 2) + /api/tools/invoke (gap 3) are NOT landed yet, and
// DNA's tool-card archetype (gap 4, the RESULT render) is mid-build. So this fire builds the FRONT HALF — the shell
// + the op-conditional form engine — verified by use against the PROVE-ON-ONE tool `corpus` (op=query), whose REAL
// schema is seeded below (registry-truth, read from the live corpus tool). When fork's /api/tools lands, loadTools
// fetches the real list and the seed is bypassed (the seam is preserved). The RUN action + the RESULT render are
// explicit pending seams (invoke-endpoint + DNA's archetype) — NOT built here (no guessing an endpoint, no bespoke
// from-DNA result render). See build-prep/the-one-application/TOOL-FACE-BUILD.md (gap 5/6 = projection).

// The descriptor shape: {name, description, inputSchema, posture} is fork's /api/tools contract (gap 2). The
// FORM-METADATA fields (opField/opParams/labels) are projection's gap-5 friendly-form layer — AI-DRAFT, marked for
// Tim's steer (operator-law: human meaning, never machine param names) + a descriptor-enrichment contract flagged
// to fork (so /api/tools or the human-description layer can carry per-tool form-meta; absent → the engine falls
// back to all-params with name-labels, so an un-enriched tool still renders).
export type JSONSchemaProp = {
  type?: string
  enum?: string[]
  default?: unknown
  title?: string
  description?: string
}
export type ToolDescriptor = {
  name: string // the machine id (corpus) — NEVER shown to the operator; used only to call the tool
  title?: string // the HUMAN name shown in the palette (gap 7; AI-draft) — falls back to a humanised name
  description: string // HUMAN meaning (gap 7; AI-draft here)
  inputSchema: { type?: string; properties: Record<string, JSONSchemaProp>; required?: string[] }
  posture?: string // safe|design|consent|hazard|locked — DISPLAY only; the server enforces the gate (never the UI)
  // --- projection's friendly-form layer (AI-draft, Tim-steerable) ---
  opField?: string // the discriminator enum param (e.g. 'op') → rendered first as a friendly selector
  opParams?: Record<string, string[]> // op value → the params it actually uses (the op-conditional form)
  opRequired?: Record<string, string[]> // op value → which of its params are REQUIRED (the op-conditional Run guard)
  opLabels?: Record<string, string> // op value → its HUMAN name on the selector pill (never the raw verb)
  enumLabels?: Record<string, Record<string, string>> // param → (enum value → HUMAN option label)
  // a param whose options come from a LIVE registry endpoint (the agreed form_meta convention, fork+lead): the URL's
  // response (object → its keys, or an array) becomes the param's enum at load → a friendly dropdown, registry-true,
  // no special-casing. e.g. corpus space ← /api/layers. Resolved by resolveEnumSources(); degrade-clean if absent.
  enumSources?: Record<string, string> // param → source URL
  labels?: Record<string, { label: string; help?: string }> // param → human label + help
}

// THE PROVE-ON-ONE SEED — `corpus`, op="query". The inputSchema is corpus's REAL registry schema (read from the
// live tool: op enum + the op-conditional params). The labels + opParams are AI-DRAFT human translations (marked
// for Tim's steer). Transitional: replaced by fork's /api/tools the moment it lands.
const CORPUS_SEED: ToolDescriptor = {
  name: 'corpus',
  title: 'The Company’s memory',
  description:
    'Ask the Company’s memory a question in plain words and get back the things it has stored that mean the most — its notes, past work, and what it has learned about its own code.',
  posture: 'safe',
  opField: 'op',
  inputSchema: {
    type: 'object',
    required: ['op'],
    properties: {
      op: { type: 'string', enum: ['query', 'list', 'find', 'read', 'neighbours'], default: 'query' },
      text: { type: 'string' },
      space: { type: 'string', default: 'history' }, // a preferred default; enum injected from /api/layers (enumSources)
      k: { type: 'integer', default: 8 },
      detail: { type: 'string', enum: ['concise', 'detailed'], default: 'concise' },
      rerank: { type: 'boolean', default: false },
      top_n: { type: 'integer', default: 0 },
      emb: { type: 'string', default: 'pplx' },
      address: { type: 'string' },
      project: { type: 'string' },
      kind: { type: 'string' },
      projection: { type: 'string' },
      source_address: { type: 'string' },
      limit: { type: 'integer', default: 50 },
      min_score: { type: 'number', default: 0 },
    },
  },
  // op → the params that op actually uses (the op-conditional form). The FRIENDLY set: expert knobs with good
  // defaults (emb/reading-lens [a machine name], top_n, min_score) are intentionally NOT surfaced — the operator
  // sees only meaningful inputs (no machine-name leak, no rerank-dependent field dangling). The defaults still ride
  // every call. (Curating the visible set is the friendly-form job; AI-draft, Tim-steerable.)
  opParams: {
    query: ['text', 'space', 'k', 'detail', 'rerank'],
    list: ['project', 'limit'],
    find: ['project', 'kind'],
    read: ['address'],
    neighbours: ['address'],
  },
  // which params each op REQUIRES — the Run guard won't fire an incomplete form (operator-law: never a silent
  // empty run). query needs a question; read/neighbours need the exact thing; list/find run with no required input.
  opRequired: {
    query: ['text'],
    read: ['address'],
    neighbours: ['address'],
  },
  // "Where to look" options come from the LIVE embeddable spaces (registry-true) — the generic enum-source convention
  // (was a special-case; now any param can declare one). The keys of /api/layers become the dropdown options.
  enumSources: { space: '/api/layers' },
  // each op's HUMAN name on the selector (never the raw verb) — so a stranger can tell them apart (query vs find)
  // and "neighbours" isn't opaque. The raw value is still what's sent; only the label is humanised.
  opLabels: {
    query: 'Ask a question',
    list: 'Browse all',
    find: 'Filter to some',
    read: 'Open one',
    neighbours: 'Find related',
  },
  // human labels (AI-draft, Tim-steerable) — operator never sees the raw param name.
  labels: {
    op: { label: 'What to do', help: 'Ask a question, or browse/look up what’s stored.' },
    text: { label: 'Your question', help: 'Ask in plain words — like you’d ask a person.' },
    space: { label: 'Where to look', help: 'Pick which part of the Company’s memory to search.' },
    k: { label: 'How many results', help: 'The number of closest matches to bring back.' },
    detail: { label: 'How much of each', help: '“Concise” = just the gist; “detailed” = the full content.' },
    rerank: { label: 'Sharper ranking', help: 'A slower, more careful re-ordering of the matches.' },
    top_n: { label: 'Keep the best', help: 'After sharper ranking, how many to keep (0 = all).' },
    emb: { label: 'Reading lens', help: 'Which way of reading meaning to use.' },
    address: { label: 'The exact thing', help: 'The name of one specific stored item.' },
    project: { label: 'Which project', help: 'Narrow to one project’s records.' },
    kind: { label: 'Which kind', help: 'Narrow to one kind of thing.' },
    projection: { label: 'Which view', help: 'Narrow to one way the records were captured.' },
    source_address: { label: 'From this source', help: 'Narrow to records made from one source.' },
    limit: { label: 'How many to list', help: 'The most records to bring back.' },
    min_score: { label: 'Minimum closeness', help: 'Only matches at least this close (0 = no floor).' },
  },
  // human names for the "Where to look" spaces (AI-draft, Tim-steerable) — the values are injected at load from
  // the live /api/layers (registry-true), these translate them so the operator never picks a raw space key.
  enumLabels: {
    space: {
      common_knowledge: 'What it’s learned',
      history: 'Past discussions',
      operators: 'Operators',
      principles: 'Principles',
      repo: 'The code',
      topics: 'Topics',
      worldview: 'Worldview',
    },
  },
}

type TState = {
  tools: ToolDescriptor[]
  loading: boolean
  error: string | null
  scaffold: boolean // true = showing the seed because /api/tools isn't live yet (honest, not silent)
  open: boolean
  selected: string | null // the picked tool's name (null = the list)
}

let state: TState = { tools: [], loading: false, error: null, scaffold: false, open: false, selected: null }
const subs = new Set<() => void>()
let started = false

function set(patch: Partial<TState>) {
  state = { ...state, ...patch }
  subs.forEach((f) => f())
}

// Resolve any param that declares an enumSource: fetch the URL → its keys (object) or items (array) become the
// param's enum (a friendly dropdown), preserving a valid preferred default. The GENERIC form of the old corpus-space
// special-case (registry-is-truth, no per-tool code). Degrade-clean: a dead/absent source → the param is left as-is.
async function resolveEnumSources(tool: ToolDescriptor): Promise<ToolDescriptor> {
  if (!tool.enumSources) return tool
  const props: Record<string, JSONSchemaProp> = { ...tool.inputSchema.properties }
  for (const [param, url] of Object.entries(tool.enumSources)) {
    if (!props[param]) continue
    try {
      // TIMEOUT (friction-fix, by-use): a SLOW/hanging enum-source must never block — /api/layers ~1.2s × 5 tools
      // hung the tool LIST on "Looking…" for 6s+. Abort at 1.5s → the param degrades clean to free-text.
      const ctrl = new AbortController()
      const to = setTimeout(() => ctrl.abort(), 1500)
      const r = await fetch(url, { signal: ctrl.signal }).finally(() => clearTimeout(to))
      if (!r.ok) continue
      const data = await r.json()
      const opts = (Array.isArray(data) ? data : Object.keys(data)).filter(Boolean).map(String)
      if (!opts.length) continue
      const pref = props[param].default
      props[param] = { ...props[param], enum: opts, default: pref && opts.includes(String(pref)) ? pref : opts[0] }
    } catch {
      /* source unavailable → leave the param as a free-text input (graceful) */
    }
  }
  return { ...tool, inputSchema: { ...tool.inputSchema, properties: props } }
}

// MAP fork's server-side form_meta onto the surface's ToolDescriptor shape. fork's /api/tools carries the
// descriptor-enrichment as a NESTED, snake_case `form_meta` ({human_name, human_description, op_labels,
// op_params, param_labels, enum_sources}); the surface's friendly-form layer wants it FLAT (title, opLabels,
// opParams, labels, enumSources, opField). This is the CONSUMPTION ADAPTER — deliberately SEPARABLE from the
// form RENDERER (schemaForm may later move onto DNA's archetype engine; the consumption stays). A tool with NO
// form_meta degrades clean: the bare schema (title/name) renders a plain form, never a crash. (Verified live:
// form_meta is populated for `corpus` only; the other 65 are null → fork's content track, see the flag.)
// opField (the op-discriminator FIELD) isn't named in form_meta yet → INFERRED as the enum param whose values
// are exactly the op_labels/op_params keys (works for corpus → `op`); flagged to fork to add an explicit op_field.
function applyFormMeta(d: Record<string, unknown>): ToolDescriptor {
  const sch = (d.inputSchema || d.input_schema || { properties: {} }) as ToolDescriptor['inputSchema']
  const t: ToolDescriptor = {
    name: String(d.name),
    description: String(d.description || ''),
    inputSchema: { ...sch, properties: sch.properties || {} },
    posture: d.posture as string | undefined,
  }
  const fm = d.form_meta as Record<string, any> | null | undefined
  if (!fm || typeof fm !== 'object') return t // un-enriched tool → plain schema form (graceful, never a crash)
  if (fm.human_name) t.title = String(fm.human_name)
  if (fm.human_description) t.description = String(fm.human_description)
  if (fm.op_labels && typeof fm.op_labels === 'object') t.opLabels = fm.op_labels
  if (fm.op_params && typeof fm.op_params === 'object') t.opParams = fm.op_params
  if (fm.op_required && typeof fm.op_required === 'object') t.opRequired = fm.op_required
  if (fm.enum_sources && typeof fm.enum_sources === 'object') t.enumSources = fm.enum_sources
  if (fm.enum_labels && typeof fm.enum_labels === 'object') t.enumLabels = fm.enum_labels
  if (fm.param_labels && typeof fm.param_labels === 'object') {
    t.labels = {}
    for (const [p, label] of Object.entries(fm.param_labels)) t.labels[p] = { label: String(label) }
  }
  const opKeys = new Set([...Object.keys(fm.op_labels || {}), ...Object.keys(fm.op_params || {})])
  if (opKeys.size) {
    const props = t.inputSchema.properties
    t.opField = Object.keys(props).find((p) => {
      const en = props[p]?.enum
      return Array.isArray(en) && en.length > 0 && en.every((v) => opKeys.has(String(v)))
    })
  }
  return t
}

let toolsSeq = 0 // monotonic load token — a stale background enum-resolve never clobbers a newer load
export async function loadTools() {
  const seq = ++toolsSeq
  set({ loading: true, error: null })
  try {
    const r = await fetch('/api/tools')
    if (!r.ok) throw new Error(`HTTP ${r.status}`)
    const data = await r.json()
    const rawList: Array<Record<string, unknown>> = Array.isArray(data) ? data : data.tools || data.items || []
    if (!rawList.length) throw new Error('empty')
    if (seq !== toolsSeq) return
    // ★ RENDER THE LIST IMMEDIATELY from form_meta (applyFormMeta is SYNC — names/labels/op-structure all present).
    // Do NOT block the panel on N enum-source fetches: a slow source (/api/layers ~1.2s) hung "Looking…" for 6s+
    // once 57 tools carried form_meta (regression caught by-use post-bounce). Only the enum DROPDOWN options need
    // the fetch → resolve them in the BACKGROUND (each timeout'd, degrade-clean to free-text) + patch the list.
    const mapped = rawList.map(applyFormMeta)
    set({ tools: mapped, scaffold: false, loading: false })
    Promise.all(mapped.map(resolveEnumSources)).then((enriched) => { if (seq === toolsSeq) set({ tools: enriched }) })
  } catch {
    // /api/tools failed → the prove-on-one SEED (honest: scaffold:true says it's the pilot tool). NOT an error.
    if (seq !== toolsSeq) return
    const seed = await resolveEnumSources(CORPUS_SEED)
    if (seq === toolsSeq) set({ tools: [seed], scaffold: true, loading: false })
  }
}

export function openTools() {
  set({ open: true, selected: null })
  loadTools()
}
export function closeTools() {
  set({ open: false })
}
export function selectTool(name: string | null) {
  set({ selected: name })
}

function ensureStarted() {
  if (started) return
  started = true
  loadTools()
}

export function useTools(): TState {
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
