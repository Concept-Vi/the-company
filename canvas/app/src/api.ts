// F0 (carved from App.tsx:19–155) · the api client + the pure registry/format helpers.
// Pure extraction — no behavior change. F5 adds `r.ok` handling on top of these; F0 keeps them verbatim.
import { getMODEL_OPTIONS } from './registryStore'

// ---------------------------------------------------------------- api (proxied to the bridge)
const J = { 'Content-Type': 'application/json' }
export const api = {
  graph: () => fetch('/api/graph').then(r => r.json()),
  types: () => fetch('/api/types').then(r => r.json()),
  // D4: run optionally FORCES a set of node ids past the memo gate (bypass cache). No body = normal run.
  run: (force?: string[]) =>
    fetch('/api/run', { method: 'POST', headers: J, body: JSON.stringify(force ? { force } : {}) }).then(r => r.json()),
  // A2: write a node's config (merge-not-replace, backend set_config). Returns fresh graph state.
  set: (node: string, config: any) =>
    fetch('/api/set', { method: 'POST', headers: J, body: JSON.stringify({ node, config }) }).then(r => r.json()),
  // B2: live model registry for a kind (chat|embed) — the source of truth, never a hardcoded list.
  models: (kind: string) => fetch('/api/models?kind=' + encodeURIComponent(kind)).then(r => r.json()),
  // C5: write a node's position back (sibling of config) after a drag — debounced, backend is truth.
  move: (node: string, x: number, y: number) =>
    fetch('/api/move', { method: 'POST', headers: J, body: JSON.stringify({ node, x, y }) }).then(r => r.json()),
  propose: (name: string, spec: string) =>
    fetch('/api/propose', { method: 'POST', headers: J, body: JSON.stringify({ name, spec }) }).then(r => r.json()),
  resolve: (id: string, choice: string, reason = '') =>
    fetch('/api/resolve', { method: 'POST', headers: J, body: JSON.stringify({ id, choice, reason }) }).then(r => r.json()),
  apply: (id: string) =>
    fetch('/api/apply', { method: 'POST', headers: J, body: JSON.stringify({ id }) }).then(r => r.json()),
  objectInfo: () => fetch('/api/object_info').then(r => r.json()),
  // registry-is-truth: WHAT EXISTS (node-types, models, modes, mode_directives, verbs, panels). The
  // presence-mode descriptions are read from capabilities().mode_directives — one backend source, no
  // parallel hardcoded copy on the surface.
  capabilities: () => fetch('/api/capabilities').then(r => r.json()),
  addNode: (type: string, config: any = {}) =>
    fetch('/api/node', { method: 'POST', headers: J, body: JSON.stringify({ type, config }) }).then(r => r.json()),
  connect: (e: any) =>
    fetch('/api/connect', { method: 'POST', headers: J, body: JSON.stringify(e) }).then(r => r.json()),
  del: (node: string) =>
    fetch('/api/delete-node', { method: 'POST', headers: J, body: JSON.stringify({ node }) }).then(r => r.json()),
  now: () => fetch('/api/now').then(r => r.json()),
  events: () => fetch('/api/events').then(r => r.json()),
  chat: (message: string, focus?: any) =>
    fetch('/api/chat', { method: 'POST', headers: J, body: JSON.stringify({ message, focus }) }).then(r => r.json()),
  chatHistory: () => fetch('/api/chat').then(r => r.json()),
  setMode: (mode: string) =>
    fetch('/api/mode', { method: 'POST', headers: J, body: JSON.stringify({ mode }) }).then(r => r.json()),
  rhmConfig: () => fetch('/api/rhm-config').then(r => r.json()),
  setRhmConfig: (updates: any) =>
    fetch('/api/rhm-config', { method: 'POST', headers: J, body: JSON.stringify(updates) }).then(r => r.json()),
  inbox: () => fetch('/api/inbox').then(r => r.json()),
  coa: (id: string) => fetch('/api/coa', { method: 'POST', headers: J, body: JSON.stringify({ id }) }).then(r => r.json()),
  // F2: route a node's RESULT to the decision surface — backend reads the output from live state
  // (client sends only the node id; canvas reflects-never-owns), surfaces it on the EXISTING inbox path.
  surfaceOutput: (node: string) =>
    fetch('/api/surface-output', { method: 'POST', headers: J, body: JSON.stringify({ node }) }).then(r => r.json()),
  react: () => fetch('/api/react', { method: 'POST' }).then(r => r.json()),
  lastChange: () => fetch('/api/last-change').then(r => r.json()),
  revert: (sha: string) => fetch('/api/revert', { method: 'POST', headers: J, body: JSON.stringify({ sha }) }).then(r => r.json()),
  panels: () => fetch('/api/panels').then(r => r.json()),
  voice: () => fetch('/api/voice').then(r => r.json()),
  stt: (blob: Blob) => fetch('/api/stt', { method: 'POST', headers: { 'Content-Type': 'application/octet-stream' }, body: blob }).then(r => r.json()),
  tts: (text: string) => fetch('/api/tts', { method: 'POST', headers: J, body: JSON.stringify({ text }) }).then(r => r.blob()),
  // C1: the UI-component registry (sibling of object_info) — the source of truth for what's addressable.
  uiInfo: () => fetch('/api/ui_info').then(r => r.json()),
  // B: the walkthrough/review session lifecycle. start makes its OWN session-graph (not graph-scoped);
  // current = the node at the cursor + its coa framing + its ui:// target; next opens the gate + advances.
  reviewStart: (item_ids: string[], mode = 'walkthrough') =>
    fetch('/api/review/start', { method: 'POST', headers: J, body: JSON.stringify({ item_ids, mode }) }).then(r => r.json()),
  reviewCurrent: (session: string) =>
    fetch('/api/review/current?session=' + encodeURIComponent(session)).then(r => r.json()),
  reviewNext: (session: string) =>
    fetch('/api/review/next', { method: 'POST', headers: J, body: JSON.stringify({ session }) }).then(r => r.json()),
  reviewStatus: (session: string) =>
    fetch('/api/review/status?session=' + encodeURIComponent(session)).then(r => r.json()),
  // D: the per-step verdict — operator-only. Session+position tag the verdict to its walk step (additive;
  // legacy id+choice+reason callers unchanged). Reflects-never-owns: the verdict goes THROUGH the gate.
  resolveStep: (id: string, choice: string, reason: string, session: string, position: number) =>
    fetch('/api/resolve', { method: 'POST', headers: J, body: JSON.stringify({ id, choice, reason, session, position }) }).then(r => r.json()),
}
export { J }

export const MODES = ['listening', 'text-only', 'background', 'focus', 'walkthrough', 'watch-and-react', 'decide-for-me', 'off']
// U11: the per-mode descriptions (so a newcomer can tell them apart in the dropdown). registry-is-truth:
// these come from capabilities().mode_directives (backend MODE_DIRECTIVES in runtime/suite.py is the ONE
// source) — read into controller state at boot, NOT a parallel hardcoded copy. A mode missing from the
// snapshot renders an empty string (safe fallback), never a stale guess.

// A2/B2: transform a node-type's config_schema ({key:{type,label,default,options_from?,options?,...}})
// into the flat field-defs the inspector renders. enum -> select; everything else -> input. options come
// from the LIVE registry (options_from) or an inline list — never hardcoded here.
export function resolveOptions(f: any): string[] {
  if (f.options_from) return getMODEL_OPTIONS()[f.options_from] || []
  if (Array.isArray(f.options)) return f.options
  return []
}
export function configSchemaToFields(schema: any): any[] {
  return Object.entries(schema || {}).map(([key, f]: [string, any]) => ({
    key,
    label: f.label || key,
    type: (f.type === 'enum' || f.options_from || Array.isArray(f.options)) ? 'select' : 'input',
    rawType: f.type,                                  // number|string|text|enum — drives value coercion
    options: resolveOptions(f),
    default: f.default,
  }))
}
// Coerce an edited form value back to its declared type before writing (the advisor's number/null trap):
// number fields must send a Number (not "0.7"); an emptied number preserves null rather than NaN.
export function coerceConfigValue(field: any, raw: string): any {
  if (field.rawType === 'number') {
    if (raw === '' || raw == null) return null
    const n = Number(raw)
    return Number.isNaN(n) ? null : n
  }
  return raw
}

export function relTime(iso?: string) {
  if (!iso) return ''
  const d = (Date.now() - new Date(iso).getTime()) / 1000
  if (d < 1) return 'now'
  if (d < 60) return `${Math.floor(d)}s`
  if (d < 3600) return `${Math.floor(d / 60)}m`
  return `${Math.floor(d / 3600)}h`
}

// WIRE-UI: a surfaced item is a BUILD-INTENT iff payload.intent === "build" (the wire's discriminator,
// runtime/suite.py is_build_intent). reflects-never-owns: we read this off the surfaced item the backend
// owns; we invent nothing.
export function isBuildIntent(d: any): boolean {
  return !!d && (d.payload?.intent === 'build')
}
// WIRE-UI: map the backend's REAL status lane (governance.py REVIEW_STATUSES: inbox · presented ·
// responded · resolved · requeue · implemented) to an operator-legible build phase. There is NO
// `dispatched` status — dispatch sets `presented` (suite.py:1344) — so we read `presented` as
// "dispatched · running". Author-from-registry: every label corresponds to a status the backend can emit.
export function buildPhase(d: any): { label: string; cls: string } {
  const st = d.status || 'inbox'
  const r = d.payload?.build_result
  if (st === 'implemented') return { label: 'implemented ✓', cls: 'bi-done' }
  if (st === 'presented') return { label: 'dispatched · running…', cls: 'bi-running' }
  // a re-queued failure/overrun is distinguished by having RUN: a build_result, an overrun, or a
  // requeued_from back-reference. NOT by `why` — every build-intent carries a `why` from
  // surface_build_intent (suite.py:1251), so keying on `why` would mislabel a fresh awaiting intent.
  if (r || d.payload?.overrun || d.payload?.requeued_from) return { label: 'surfaced back — needs you', cls: 'bi-back' }
  return { label: 'awaiting approval', cls: 'bi-inbox' }
}

// WIRE-UI · DEMONSTRATE-FIRST: derive a plain-language "what you can now do" + a canvas-demonstrable
// node-type from the build_result the backend owns (never a diff as the headline).
export function deriveOutcome(d: any, liveTypes: string[]): { line: string; demoType: string | null } {
  const p = d.payload || {}
  const r = p.build_result
  const changed: string[] = (r?.changed_files) || []
  // a new node-type = a freshly-added nodes/<name>.py whose stem is now a LIVE registered type.
  const nodeFile = changed.find((f: string) => /(^|\/)nodes\/[^/]+\.py$/.test(f))
  const nodeType = nodeFile ? (nodeFile.split('/').pop() || '').replace('.py', '') : null
  const demoType = nodeType && liveTypes.includes(nodeType) ? nodeType : null
  if (demoType) return { line: `The “${demoType}” node is ready — place it on the canvas to see it work.`, demoType }
  if (r?.success && r?.summary) return { line: r.summary.split('\n')[0].slice(0, 240), demoType: null }
  if (r?.success) return { line: 'The build completed — review the outcome below.', demoType: null }
  return { line: '', demoType: null }
}
