// F0 (carved from App.tsx:19–155) · the api client + the pure registry/format helpers.
// Pure extraction — no behavior change. F5 adds `r.ok` handling on top of these; F0 keeps them verbatim.
import { getMODEL_OPTIONS } from './registryStore'

// ---------------------------------------------------------------- api (proxied to the bridge)
const J = { 'Content-Type': 'application/json' }

// F5 · the error path. IS (fe-map §5, traced): a backend 400 (e.g. the literal first thing an operator
// hits — model unreachable → bridge.py:371 `_send(400, {"error":…})`) was read with a bare `r => r.json()`
// (no `r.ok`). `fetch` only REJECTS on a network failure; an HTTP-400 with body `{error:"…"}` RESOLVES to
// that object. So `api.chat` resolved to `{error}`, `sendChat` did `setChat({error}.history)` =
// `setChat(undefined)`, and RhmChat's `chat.length` threw at render → with the shell unwrapped, white-screen.
//
// THE FIX — normalize, don't throw. `jr` (json-or-error) checks `r.ok`; on a non-2xx it RETURNS a normalized
// `{error}` (parsing the body's `{error}`, falling back to "<status> <statusText>" for a non-JSON 500). This
// is deliberately a RETURNED error, not a throw: the existing callers (connect/set/surfaceOutput/connect…)
// already branch on `if (r.error) setNotice(...)` on a RESOLVED object — making `jr` throw would turn those
// into uncaught rejections in event handlers (new white-screens). Returning `{error}` instead makes EVERY
// caller more robust for free, and the named call-site guards (sendChat) surface it as a visible state.
// `tts` is intentionally NOT routed through `jr` — it returns a Blob, not JSON.
async function jr(r: Response): Promise<any> {
  if (r.ok) return r.json()
  // try to read the backend's structured `{error}` body; fall back to the HTTP status for a non-JSON body.
  let body: any = null
  try { body = await r.json() } catch { /* non-JSON error body (e.g. a proxy 502 HTML page) */ }
  const msg = (body && body.error) ? body.error : `${r.status} ${r.statusText || 'request failed'}`
  return { error: msg }
}

export const api = {
  graph: () => fetch('/api/graph').then(jr),
  types: () => fetch('/api/types').then(jr),
  // D4: run optionally FORCES a set of node ids past the memo gate (bypass cache). No body = normal run.
  run: (force?: string[]) =>
    fetch('/api/run', { method: 'POST', headers: J, body: JSON.stringify(force ? { force } : {}) }).then(jr),
  // A2: write a node's config (merge-not-replace, backend set_config). Returns fresh graph state.
  set: (node: string, config: any) =>
    fetch('/api/set', { method: 'POST', headers: J, body: JSON.stringify({ node, config }) }).then(jr),
  // B2: live model registry for a kind (chat|embed) — the source of truth, never a hardcoded list.
  models: (kind: string) => fetch('/api/models?kind=' + encodeURIComponent(kind)).then(jr),
  // C5: write a node's position back (sibling of config) after a drag — debounced, backend is truth.
  move: (node: string, x: number, y: number) =>
    fetch('/api/move', { method: 'POST', headers: J, body: JSON.stringify({ node, x, y }) }).then(jr),
  propose: (name: string, spec: string) =>
    fetch('/api/propose', { method: 'POST', headers: J, body: JSON.stringify({ name, spec }) }).then(jr),
  resolve: (id: string, choice: string, reason = '') =>
    fetch('/api/resolve', { method: 'POST', headers: J, body: JSON.stringify({ id, choice, reason }) }).then(jr),
  // X16: the operator authorizes HOW FAR a build's edit propagates — approve named blast-radius
  // members to WIDEN the build's editable scope to their files. DEFAULT is the pointed address only
  // (no call → no expansion). Operator-only (off the MCP face); a member not in the surfaced radius
  // is refused by the backend (consent-time gate).
  approveReach: (id: string, members: string[], reason = '') =>
    fetch('/api/approve-reach', { method: 'POST', headers: J, body: JSON.stringify({ id, members, reason }) }).then(jr),
  apply: (id: string) =>
    fetch('/api/apply', { method: 'POST', headers: J, body: JSON.stringify({ id }) }).then(jr),
  objectInfo: () => fetch('/api/object_info').then(jr),
  // registry-is-truth: WHAT EXISTS (node-types, models, modes, mode_directives, verbs, panels). The
  // presence-mode descriptions are read from capabilities().mode_directives — one backend source, no
  // parallel hardcoded copy on the surface.
  capabilities: () => fetch('/api/capabilities').then(jr),
  addNode: (type: string, config: any = {}) =>
    fetch('/api/node', { method: 'POST', headers: J, body: JSON.stringify({ type, config }) }).then(jr),
  connect: (e: any) =>
    fetch('/api/connect', { method: 'POST', headers: J, body: JSON.stringify(e) }).then(jr),
  del: (node: string) =>
    fetch('/api/delete-node', { method: 'POST', headers: J, body: JSON.stringify({ node }) }).then(jr),
  now: () => fetch('/api/now').then(jr),
  events: () => fetch('/api/events').then(jr),
  chat: (message: string, focus?: any) =>
    fetch('/api/chat', { method: 'POST', headers: J, body: JSON.stringify({ message, focus }) }).then(jr),
  // I3/I2: the click-emission seam — a DETERMINISTIC operator click ships a STRUCTURED {verb, address,
  // args} that drives _dispatch_rhm_action directly (the 7-verb whitelist + no-self-apply ride along
  // INSIDE the dispatcher). This is the path an APPROVED propose-affordance card fires (I3 = click #2,
  // the consent gate) — the action runs ONLY on approve. Returns the same {reply, action} shape /api/chat
  // returns, so the post-approve reaction reuses the existing r.action.did handling.
  act: (verb: string, address?: string, args?: any) =>
    fetch('/api/act', { method: 'POST', headers: J, body: JSON.stringify({ verb, address, args }) }).then(jr),
  chatHistory: () => fetch('/api/chat').then(jr),
  setMode: (mode: string) =>
    fetch('/api/mode', { method: 'POST', headers: J, body: JSON.stringify({ mode }) }).then(jr),
  rhmConfig: () => fetch('/api/rhm-config').then(jr),
  setRhmConfig: (updates: any) =>
    fetch('/api/rhm-config', { method: 'POST', headers: J, body: JSON.stringify(updates) }).then(jr),
  inbox: () => fetch('/api/inbox').then(jr),
  coa: (id: string) => fetch('/api/coa', { method: 'POST', headers: J, body: JSON.stringify({ id }) }).then(jr),
  // F2: route a node's RESULT to the decision surface — backend reads the output from live state
  // (client sends only the node id; canvas reflects-never-owns), surfaces it on the EXISTING inbox path.
  surfaceOutput: (node: string) =>
    fetch('/api/surface-output', { method: 'POST', headers: J, body: JSON.stringify({ node }) }).then(jr),
  react: () => fetch('/api/react', { method: 'POST' }).then(jr),
  lastChange: () => fetch('/api/last-change').then(jr),
  revert: (sha: string) => fetch('/api/revert', { method: 'POST', headers: J, body: JSON.stringify({ sha }) }).then(jr),
  panels: () => fetch('/api/panels').then(jr),
  voice: () => fetch('/api/voice').then(jr),
  stt: (blob: Blob) => fetch('/api/stt', { method: 'POST', headers: { 'Content-Type': 'application/octet-stream' }, body: blob }).then(jr),
  tts: (text: string) => fetch('/api/tts', { method: 'POST', headers: J, body: JSON.stringify({ text }) }).then(r => r.blob()),
  // C1: the UI-component registry (sibling of object_info) — the source of truth for what's addressable.
  uiInfo: () => fetch('/api/ui_info').then(jr),
  // L3 · addressed history (§21.7#1): everything that happened AT a ui:// address. The address-keyed READ
  // over the event tail — the addressed analogue of decision_view. Returns { address, trajectory[] }
  // chronological; a non-ui:// / malformed address → backend 400 (fail-loud, normalized to {error} by jr).
  addressHistory: (address: string) =>
    fetch('/api/address-history?address=' + encodeURIComponent(address)).then(jr),
  // L5 · self-change locating (§21.7#5): "what did the system change HERE?" — the self-change audit log
  // FILTERED by the S3 address→code scope join. Returns { address, scope[], stale, note, changes[] }
  // (each change carries matched_files = the subset that touched this element). A stale corpus is surfaced
  // via `stale`/`note` (regenerate the corpus), NEVER a silent empty that reads "nothing changed here".
  // Revert from here reuses the EXISTING operator-only api.revert(sha) — no new revert path. Malformed
  // address → backend 400 (fail-loud, normalized to {error} by jr).
  selfChangesAt: (address: string) =>
    fetch('/api/self-changes-at?address=' + encodeURIComponent(address)).then(jr),
  // L10 · "stale at this address" (§21.7#10): is the cached result AT this NODE's run:// address out of
  // date vs its CURRENT inputs? A COSTED DERIVATION, not a served field — the surface CALLS this only when
  // it wants the verdict (the backend recompiles + resolves input-hashes + recomputes the _memo_sig +
  // memo_get-compares against the stored output; seams-engine Seam 8a). READ-ONLY: it does NOT mutate the
  // memo gate (no memo_set/set_ref/run). Returns { address, graph, node, stale, unknown, reason, volatile,
  // … }: stale=true/false ONLY when a real comparison was made; otherwise stale=null + unknown=true + a
  // reason (rule 4 — an unevaluable node is never a silent 'fresh'). The key is a run://<graph>/<node>
  // node-instance address (NOT ui:// — `cached` is served per run:// node). A malformed / non-run address →
  // backend 400 (fail-loud, normalized to {error} by jr).
  staleAt: (address: string) =>
    fetch('/api/stale-at?address=' + encodeURIComponent(address)).then(jr),
  // L6 · versions at an address (§21.7#6): the TEMPORAL trail of values an addressed output has held — every
  // set_ref to this run:// address as a {cas, ts, is_current, preview}, NEWEST-FIRST (GET /api/ref-versions
  // → Suite.ref_versions → store.ref_history, the index appended on each set_ref). The CURRENT value is the
  // live portal window; this is the PRIOR-versions half, each fetchable by its surviving cas (put_content is
  // write-once). Returns { address, current, count, versions[] }. The key is a run://<graph>/<node> OUTPUT
  // address (NOT ui:// — versions accrue where set_ref wrote; a PORTAL never writes, so the FE passes the
  // address its config.ref POINTS AT). A malformed / non-run address → backend 400 (fail-loud, normalized to
  // {error} by jr); an address with no history → versions:[] (honest empty, never a silent wrong value).
  refVersions: (address: string) =>
    fetch('/api/ref-versions?address=' + encodeURIComponent(address)).then(jr),
  // B: the walkthrough/review session lifecycle. start makes its OWN session-graph (not graph-scoped);
  // current = the node at the cursor + its coa framing + its ui:// target; next opens the gate + advances.
  reviewStart: (item_ids: string[], mode = 'walkthrough') =>
    fetch('/api/review/start', { method: 'POST', headers: J, body: JSON.stringify({ item_ids, mode }) }).then(jr),
  reviewCurrent: (session: string) =>
    fetch('/api/review/current?session=' + encodeURIComponent(session)).then(jr),
  reviewNext: (session: string) =>
    fetch('/api/review/next', { method: 'POST', headers: J, body: JSON.stringify({ session }) }).then(jr),
  reviewStatus: (session: string) =>
    fetch('/api/review/status?session=' + encodeURIComponent(session)).then(jr),
  // D: the per-step verdict — operator-only. Session+position tag the verdict to its walk step (additive;
  // legacy id+choice+reason callers unchanged). Reflects-never-owns: the verdict goes THROUGH the gate.
  resolveStep: (id: string, choice: string, reason: string, session: string, position: number) =>
    fetch('/api/resolve', { method: 'POST', headers: J, body: JSON.stringify({ id, choice, reason, session, position }) }).then(jr),
  // L9 · reverse journey-recording (§21.7#2-reverse). The REVERSE of the forward resolveUiTarget: capture
  // an ordered ui:// click-path as a DISTINCT journey-record (not a review session), then replay it by
  // stepping the view through the recorded addresses via the PRESERVED resolveUiTarget. start opens the
  // record; step appends one S0-validated address (a malformed/finalized-journey → backend 400); stop
  // finalizes; replay returns { journey, addresses[] } the FE walks one resolveUiTarget at a time.
  journeyStart: () => fetch('/api/journey/start', { method: 'POST', headers: J, body: '{}' }).then(jr),
  journeyStep: (journey: string, address: string) =>
    fetch('/api/journey/step', { method: 'POST', headers: J, body: JSON.stringify({ journey, address }) }).then(jr),
  journeyStop: (journey: string) =>
    fetch('/api/journey/stop', { method: 'POST', headers: J, body: JSON.stringify({ journey }) }).then(jr),
  journeyReplay: (journey: string) =>
    fetch('/api/journey/replay?journey=' + encodeURIComponent(journey)).then(jr),
  journeys: () => fetch('/api/journeys').then(jr),
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
