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
  // X7: the pin override — pin/unpin an attached context item at a ui:// ADDRESS so it HOLDS in the
  // bounded R2 window (the dead `pinned` term's SET path; `_r2_score` reads it, nothing set it before).
  // OPERATOR-ONLY, OFF the MCP face (POST /api/pin, beside /api/annotate). `target_ts` is the item's
  // handle (its `ts`); the backend (Suite.pin) S0-validates the address (→ 400) AND fails loud if
  // (address, target_ts) names no real attached item — never a silent no-op. Default pinned=true.
  pin: (address: string, target_ts: string, pinned = true) =>
    fetch('/api/pin', { method: 'POST', headers: J, body: JSON.stringify({ address, target_ts, pinned }) }).then(jr),
  apply: (id: string) =>
    fetch('/api/apply', { method: 'POST', headers: J, body: JSON.stringify({ id }) }).then(jr),
  // G-4 · THE WIRE'S OPERATOR DOOR (the self-build mint seam). Two entry shapes, both MINT-ONLY:
  // they surface a build-intent with resolved=None for the operator to approve — they NEVER dispatch
  // (dispatch is dispatch_decision, off this face + posture-gated + safe-by-default `plan`). The door
  // is INERT-by-default: minting a build-intent is composing a PLAN, not self-modifying live.
  //
  //   intentAt — the RECOGNITION-BY-SIGHT path (the door the operator actually uses): from a POINTED
  //   `ui://` element, mint a build-intent whose SCOPE is DERIVED from the address (S3 resolve_scope)
  //   and whose X16 BLAST-RADIUS is computed at consent time (surface_intent_at, bridge.py:626). So the
  //   minted item carries `payload.blast_radius` → BlastRadiusReach renders the ripple + reach-approval.
  //   An orphan/CSS address → empty scope = DENY-ALL (honest, never fabricated). Backend fail-loud on a
  //   missing address/text → 400 (normalized to {error} by jr).
  intentAt: (address: string, text: string, consequence_class = 'decision_build', why = '') =>
    fetch('/api/intent-at', { method: 'POST', headers: J, body: JSON.stringify({ address, text, consequence_class, why }) }).then(jr),
  //   buildIntent — the SCOPE-DECLARED path (the wire's raw production entry seam, bridge.py:607): the
  //   operator declares the spec + the paths the build may touch directly (no address). It carries NO
  //   blast_radius (no address to compute a radius from) — so it surfaces with the declared scope only.
  //   Provided additively for completeness; the door prefers intentAt (address-grounded, carries the reach).
  //   Empty/omitted scope = DENY-ALL. Backend fail-loud on a missing spec → 400 (normalized by jr).
  buildIntent: (spec: string, scope?: string[], consequence_class = 'decision_build', why = '') =>
    fetch('/api/build-intent', { method: 'POST', headers: J, body: JSON.stringify({ spec, scope, consequence_class, why }) }).then(jr),
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
  // B1 · TEXT-streaming chat — the incremental sibling of `chat` above (which stays untouched). POSTs to
  // /api/chat/stream and reads the ndjson body line-by-line (the SAME reader pattern as voiceStream): each
  // {type:part} → onPart(text, idx) (the reply appears progressively); the terminal {type:done} carries the
  // CANONICAL turn-end state (reply/proposal/action/thread_id/history — a true superset of /api/chat) →
  // onDone(done). A {type:error} event THROWS (so the caller's catch surfaces the real text, not a generic
  // "could not reach the brain" — fail loud, no silent swallow).
  chatStream: async (message: string, focus: any,
                     onPart: (text: string, idx: number) => void,
                     onDone: (done: any) => void) => {
    const res = await fetch('/api/chat/stream', { method: 'POST', headers: J, body: JSON.stringify({ message, focus }) })
    if (!res.ok || !res.body) {
      const t = await res.text().catch(() => '')
      throw new Error('chat stream failed (' + res.status + '): ' + t.slice(0, 200))
    }
    const reader = res.body.getReader(); const dec = new TextDecoder(); let buf = ''
    for (;;) {
      const { done, value } = await reader.read(); if (done) break
      buf += dec.decode(value, { stream: true })
      const lines = buf.split('\n'); buf = lines.pop() || ''
      for (const ln of lines) {
        const s = ln.trim(); if (!s) continue
        let ev: any; try { ev = JSON.parse(s) } catch { continue }
        if (ev.type === 'part') onPart(ev.text, ev.idx)
        else if (ev.type === 'done') onDone(ev)
        else if (ev.type === 'error') throw new Error(ev.error)   // fail loud — the caller's catch surfaces this
      }
    }
  },
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
  // B3 · the configurable interactive-inbox (§6B QUEUE mode): defer a LIVE RHM offer into the inbox as a
  // REAL queued item (the whole proposal shape is persisted so it can be revived), and read it back to
  // RE-OPEN the interactive conversation. Nothing dispatches on defer — the offer's verb runs only on a
  // later approve through /api/act (the B1/B2 consent invariant: nothing-runs-until-approved).
  deferOffer: (proposal: any, note = '') =>
    fetch('/api/defer-offer', { method: 'POST', headers: J, body: JSON.stringify({ proposal, note }) }).then(jr),
  reviveOffer: (id: string) =>
    fetch('/api/revive-offer', { method: 'POST', headers: J, body: JSON.stringify({ id }) }).then(jr),
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
  // Option A — switch between the personas: list them, read which voice engines are resident, and SWITCH
  // (sets the active persona + auto-loads its voice, evicting the previous one — see /api/voice/switch).
  personas: () => fetch('/api/personas').then(jr),
  voiceServices: () => fetch('/api/voice/services').then(jr),
  voiceSwitch: (persona: string) => fetch('/api/voice/switch', { method: 'POST', headers: J, body: JSON.stringify({ persona }) }).then(jr),
  // V2.2 — the streaming voice circuit: POST the recorded utterance, get back an ndjson stream
  // (transcript → reply → per-sentence {wav_b64} chunks → done) in the persona's voice. Returns the raw
  // Response so the caller reads `.body` (NOT jr — it's a stream, not one JSON object).
  voiceStream: (blob: Blob, persona: string, trialSession?: string) =>
    fetch('/api/voice/stream?persona=' + encodeURIComponent(persona)
          + (trialSession ? '&trial_session=' + encodeURIComponent(trialSession) : ''),
          { method: 'POST', headers: { 'Content-Type': 'application/octet-stream' }, body: blob }),
  // V3 — the memory loop: list recorded trial sessions, and start a debrief over them (reuses the
  // walkthrough organ — start_debrief surfaces each session's REAL transcript through the same walk).
  // S2 — conversation threads: start fresh, list previous, reopen one.
  // S1 — the chat-model picker list (ollama/cloud + local vLLM, each with base_url+service+up) + load-on-demand.
  chatModelsDetailed: () => fetch('/api/chat-models').then(jr),
  // S6 (Tim 2026-06-07): "tell me if my selection won't fit." Given the selected GPU service keys
  // (brain + voice), returns each one's VRAM budget, the sum vs the 16GB card ceiling, measured free,
  // and fit/no-fit + what to unload. Config-derived → tracks a resize (brain @256K vs @64K).
  fit: (services: string[]) => fetch('/api/fit?services=' + encodeURIComponent(services.join(','))).then(jr),
  modelLoad: (service: string) => fetch('/api/model/load', { method: 'POST', headers: J, body: JSON.stringify({ service }) }).then(jr),
  // voice trace (Tim 2026-06-07): the browser reports its half of the live voice loop (VAD pause,
  // recording, judge-call, turn-fire, playback, errors) into the ONE event log so the WHOLE process is
  // investigable. Fire-and-forget — a trace write must NEVER break a turn; swallow any failure.
  voiceLog: (event: string, data: any = {}) =>
    fetch('/api/voice/log', { method: 'POST', headers: J, body: JSON.stringify({ event, ...data }) }).catch(() => {}),
  // S5 — set a serve-time model config (e.g. context window) + restart; + the per-TTS-engine knob catalog.
  modelConfig: (service: string, key: string, value: any) => fetch('/api/model/config', { method: 'POST', headers: J, body: JSON.stringify({ service, key, value }) }).then(jr),
  voiceEngineKnobs: () => fetch('/api/voice/engine-knobs').then(jr),
  newConversation: (title?: string) => fetch('/api/conversation/new', { method: 'POST', headers: J, body: JSON.stringify({ title: title || '' }) }).then(jr),
  listConversations: () => fetch('/api/conversations').then(jr),
  loadConversation: (threadId: string) => fetch('/api/conversation?thread_id=' + encodeURIComponent(threadId)).then(jr),
  trialSessions: () => fetch('/api/trial/sessions').then(jr),
  startDebrief: (sessionIds: string[], hostPersona?: string) =>
    fetch('/api/debrief/start', { method: 'POST', headers: J, body: JSON.stringify({ session_ids: sessionIds, host_persona: hostPersona }) }).then(jr),
  // V1.1 — the finished-thought judge: given the utterance-so-far (after a silence pause), is it a complete
  // thought (fire the turn) or is the operator mid-ramble (keep listening)? The "not a dumb silence timer"
  // lever. Returns {finished, verdict, ...}. Fail-loud upstream (a judge error → caller surfaces + can fall
  // back to push-to-talk, never a silent degrade).
  finishedThought: (text: string) =>
    fetch('/api/voice/finished-thought', { method: 'POST', headers: J, body: JSON.stringify({ text }) }).then(jr),
  // C1: the UI-component registry (sibling of object_info) — the source of truth for what's addressable.
  uiInfo: () => fetch('/api/ui_info').then(jr),
  // L-fe · the cognition projection (the SIBLING of object_info, built by L-fe-be): the registry-generated
  // truth the live cognition VIEW renders FROM — roles{id,label,can_fire,is_jury,draws,mode_scope,trigger,
  // render_hint,rules} · rules · edge_kinds · thought_shapes · activation_contexts · casts{mode:[role_id]} ·
  // node_states (the status render-tokens, sibling of capabilities().node_states) · event_kinds (the
  // cognition.* emit-contract). Registry-driven (rule 8): a new role/rule appears here with NO FE code, so
  // the River draws its tributaries + the dots paint their status FROM this — never a hardcoded role list.
  cognitionInfo: () => fetch('/api/cognition_info').then(jr),
  // S7-FE · the FORAGER's search door — semantic corpus query + per-hit record heads (the bridge's
  // /api/corpus-query, S7: Suite.query_corpus + find_corpus enrichment server-side). The honest-empty
  // contract rides through untouched: embedder down → {hits:[], note:'embed endpoint unreachable …'}
  // (the note is RENDERED by ForagerBar, never swallowed); a non-2xx is normalized to {error} by jr (loud).
  corpusQuery: (text: string, space: string | null, k = 16) =>
    fetch('/api/corpus-query?text=' + encodeURIComponent(text) +
      (space ? '&space=' + encodeURIComponent(space) : '') + '&k=' + k).then(jr),
  // STUDIO (G4) · the review-corpus index — every reviewable mockup file actually on disk + its curated
  // meta {file,title,platform,group,address}. The studio gallery binds THIS (registry-is-truth: the disk
  // listing is the source), never a hardcoded FE list, so a new mockup appears the moment its file lands.
  // The per-item `address` is the reviewed-surface ui:// the mockup depicts (the gallery Card carries it as
  // data-ui-ref so selecting a card indicates that locus — the chat/help/annotate seams bind to it).
  // Returns { items:[…] }; a thrown/non-ok response → {error} (jr), surfaced fail-loud by the caller.
  corpus: () => fetch('/api/corpus').then(jr),
  // I6 · the comment THREAD at a ui:// address (the read-back half of annotate). The studio's "comment at
  // an element" posts via /api/annotate (annotateLocus) into the SHARED address-keyed annotation store and
  // reads it back HERE — NOT the bespoke /api/mockup-feedback jsonl (retired for the in-app surface). The
  // backend S0-validates the address (→ 400, fail-loud, normalized to {error} by jr). Returns the thread
  // (oldest-first) keyed by the address; disk-backed (survives reload) — this proves the persist-to-shared-store.
  annotations: (address: string) =>
    fetch('/api/annotations?address=' + encodeURIComponent(address)).then(jr),
  // GENERATE FOLLOW-ON · the studio "generate" step. POSTs ONE reviewed mockup to the committed
  // generate-for-mockups ENGINE (bridge /api/mockup-generate → runtime/generate_mockup). mode defaults
  // to 'plan' — SAFE/read-only: the engine's claude -p run PROPOSES the edit (returns a summary/diff) and
  // changes NOTHING (changed_files == []). Returns the proposed result; a backend 400 (missing mockup / no
  // actionable feedback / engine raise) is normalized to {error} by jr (fail-loud, never a silent no-op).
  mockupGenerate: (mockup: string, mode: 'plan' | 'apply' = 'plan') =>
    fetch('/api/mockup-generate', { method: 'POST', headers: J, body: JSON.stringify({ mockup, mode }) }).then(jr),
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
  // D2 · the COMPOSED address-help bundle (the operator-facing help/altitude surface). EXPOSES the
  // existing D1 composer Suite.address_help (committed 89f60d9 — NOT a parallel FE composer): the JOIN of
  // the three legs at one ui:// address — what_this_is (the represents/feature label) · how_to_use (the
  // corpus 'howto' stratum) · how_to_change (resolve_scope → blast_radius/X16 reach) — plus `legs_present`
  // the AddressHelp panel reads to DEGRADE cleanly per leg (G-53: many elements author no howto yet).
  // Returns { address, what_this_is, how_to_use, how_to_change:{scope,blast_radius,note}, legs_present }.
  // A malformed address → backend 400 (S0 grammar gate, fail-loud, normalized to {error} by jr); a
  // well-formed-but-unregistered address returns a clean partial bundle (never a crash). NOTE: this method
  // is OUTSIDE the voice block (G-8) — it is an address-keyed read sibling of selfChangesAt/addressHistory.
  addressHelp: (address: string) =>
    fetch('/api/address-help?address=' + encodeURIComponent(address)).then(jr),
  // F1 ALTITUDE · THE PRESENTATION-PREFERENCE LEARNING LOOP (the visible half — committed backend e1700b4).
  // These wire the in-system "shape how it presents to me, it remembers" channel. NOTE: OUTSIDE the voice
  // block (G-8) — they are address-keyed read/write siblings of addressHelp/annotate, not voice methods.
  //
  //   presentationPref — READ the ACTIVE learned pref at a ui:// address (GET /api/presentation-pref). The
  //   latest-wins structured pref {kind, arg?} or null (a clean absence — the surface renders no marker).
  //   The backend S0-validates the address (→ 400) AND re-validates a stored junk pref (→ 400, fail-loud,
  //   never a silent degrade-to-default). address_help/up_translate ALREADY consult+attach this; this read
  //   is the standalone seam (e.g. to confirm a pref persisted across reload).
  presentationPref: (address: string) =>
    fetch('/api/presentation-pref?address=' + encodeURIComponent(address)).then(jr),
  //   setPresentationPref — CAPTURE "how Tim wants <this> presented" at a ui:// address (POST). It IS the
  //   annotate-branch of the addressed-feedback channel WITH a presentation intent (rides the same
  //   annotations.jsonl leaf, an additive structured marker — NO parallel store, rule 3). The `pref` is
  //   {kind:'terser'|'more'|'lead_with'|'shape', arg?}: terser/more are bare; lead_with/shape REQUIRE a
  //   non-empty arg. `text` is the human phrasing the operator gave (kept for the thread). Persists keyed
  //   by address; the next address-help/up_translate render REFLECTS it (the adapt step consults it);
  //   survives reload (the leaf reads disk every call). Fail-loud (rule 4): a missing address / a malformed
  //   pref → backend 400 (normalized to {error} by jr) — no silent ignore. OPERATOR-only (off the MCP face).
  //   The voice/typing INPUT that produces "show me this differently" rides the existing chat path
  //   (/api/chat, untouched per G-8); this is the recorder the affordance (or a parsed intent) calls.
  setPresentationPref: (address: string, pref: { kind: string; arg?: string }, text?: string) =>
    fetch('/api/presentation-pref', { method: 'POST', headers: J, body: JSON.stringify({ address, pref, text }) }).then(jr),
  // F1 ALTITUDE · THE GENERALIZED UP-TRANSLATE REACH (committed backend foundation 5f3592b). The reusable
  // "present-this-at-Tim's-altitude" resolver (Suite.up_translate) → an artifact's altitude envelope
  // { lead, mechanism, legs_present, grounded, degraded }. `kind` ∈ address|decision (the two first-class
  // string-keyed kinds on the GET face; finding/event take a caller-held dict the G2/future surfaces POST).
  // NOTE this lane (f1-fe-surface): the ADDRESS surface (AddressHelp) consumes `addressHelp` DIRECTLY (not
  // this envelope) BY DESIGN — address_help keeps the THREE legs (what_this_is · how_to_use · how_to_change)
  // distinct so the panel renders all 5 degrade states, where up_translate's `lead` FLATTENS the front legs
  // into one prose string (which would regress D2's distinct howto-block + the STATE-2 'no how-to authored'
  // cue). This client is the named generalized reach for the OTHER kinds (decision → coa, + future
  // finding/event consumers); it is provided for completeness + correctness, not wired into a FE render here
  // (see the lane report's identified_gaps). A malformed address / unknown kind / missing ref → backend 400.
  upTranslate: (kind: string, ref: string) =>
    fetch('/api/up-translate?kind=' + encodeURIComponent(kind) + '&ref=' + encodeURIComponent(ref)).then(jr),
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
  // C4 (FE show-me lane): the mode-selection → ORGAN-start seam. POST /api/walkthrough/start binds the
  // cosmetic presence-dial 'walkthrough' MODE to the REAL walkthrough organ — set_mode('walkthrough')
  // AND start_session over the pending review items, in ONE composed call. Optional item_ids pre-selects
  // a set; absent → it walks every pending unresolved inbox item. Returns the SAME shape start_session
  // returns (so the FE feeds it straight into the existing walk machinery via setSession) PLUS
  // { organ_started, mode, reason? }: organ_started:true → a populated walk (carries `session`);
  // organ_started:false → nothing pending (carries `reason` — fail-loud, the surface says so, never silent).
  // ASYNC by contract: a populated walk compiles a review-session graph that invokes a model, so this can
  // be slow / hang if no model is up (GAPS G-41) — the FE awaits with a spinner, never blocks the UI thread.
  walkthroughStart: (item_ids?: string[]) =>
    fetch('/api/walkthrough/start', { method: 'POST', headers: J, body: JSON.stringify(item_ids ? { item_ids } : {}) }).then(jr),
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
  // ── COGNITION ENGINE · the HUMAN face (G2 + C7.4) — reflects-never-owns ───────────────────────────────
  // Every method below READS or DRIVES an EXISTING /api/cognition/* route the bridge already serves (the
  // SAME Suite methods the MCP agent face calls — one composition surface, both faces project from the same
  // registries, AGENTS rule 3/8). The FE INVENTS nothing: selects/specs project from these registry reads.
  //
  // THE FLOOR (AGENTS rule 9 + the cognition criteria A1/A4, verified in bridge.py:1695/1741):
  //   • run_role/run_items/run_reduce are COMPUTATION — they produce run:// outputs + op.run telemetry,
  //     NEVER a resolve/approve/dispatch. The FE calls them DIRECTLY (not a floor act).
  //   • create_role/create_skill/create_context are DECLARATIVE-DIRECT (#58, A1 ✅) — they apply LIVE with NO
  //     approval step. The FE posts them direct. (Over-gating create with a fake approval step would VIOLATE
  //     A1; conversely node-type/code create stays GATED — propose_* + /api/apply — and is NOT exposed here.)
  //   • role EDIT/DELETE + rule ATTACH/DETACH SURFACE for approval (bridge role/edit · role/delete ·
  //     rule/attach) — NOT exposed in this authoring lane (it does direct-create only); they remain the RHM's.

  // AUTHORING SELECTS (registry-is-truth) — the option lists the create-role form projects from, so adding a
  // model/input/field-type makes it settable in the form with zero FE edit (rule 8).
  cogModelsForRole: (requires = '') =>
    fetch('/api/cognition/models_for_role?requires=' + encodeURIComponent(requires)).then(jr),
  cogInputs: () => fetch('/api/cognition/inputs').then(jr),     // the addresses a role can read (skill://context://run://cas://…)
  cogFieldTypes: () => fetch('/api/cognition/field_types').then(jr), // the closed output-schema field-type grammar

  // RUN DISCOVERY (G2 "see runs") — the run-index projection (the SAME read the MCP list_runs/find_runs serve).
  // Returns { runs:[{address,op,run_op,turn_id,role,duration_ms,seq,ts}], total_records }. A fabricated op
  // fails loud (→ {error} via jr). `find` filters by role; `list` is the unfiltered tail.
  cogListRuns: (limit = 50) =>
    fetch('/api/cognition/list_runs?limit=' + limit).then(jr),
  cogFindRuns: (opts: { role?: string; op?: string; run_op?: string; limit?: number } = {}) => {
    const p = new URLSearchParams()
    if (opts.role) p.set('role', opts.role)
    if (opts.op) p.set('op', opts.op)
    if (opts.run_op) p.set('run_op', opts.run_op)
    p.set('limit', String(opts.limit ?? 50))
    return fetch('/api/cognition/find_runs?' + p.toString()).then(jr)
  },

  // RUN A ROLE (G2 "do" — fire ONE role over an utterance → its run:// output). COMPUTATION, NOT a floor act
  // (bridge.py:1701). Returns the engine result incl. the run:// address + output. `ensure` requests the
  // gated #50 model-load (a down model otherwise fails loud — no silent fallback).
  cogRunRole: (body: { role: string; utterance?: string; model?: string; inputs?: string[]; max_tokens?: number; temperature?: number; ensure?: boolean }) =>
    fetch('/api/cognition/run_role', { method: 'POST', headers: J, body: JSON.stringify(body) }).then(jr),

  // DIRECT CREATE (C7.4 + A1) — author a role/skill/context, applied LIVE, NO approval (declarative-direct,
  // #58). The correctness gate BITES backend-side: a malformed spec → AuthoringError → 400 → {error} (jr),
  // fail-loud, never written. The build-dispatch floor is untouched (this writes a roles/ file; it never
  // launches claude -p). `spec` is the full role/skill/context shape projected from the authoring selects.
  cogCreateRole: (spec: any) =>
    fetch('/api/cognition/create_role', { method: 'POST', headers: J, body: JSON.stringify({ spec }) }).then(jr),
  cogCreateSkill: (spec: any) =>
    fetch('/api/cognition/create_skill', { method: 'POST', headers: J, body: JSON.stringify({ spec }) }).then(jr),
  cogCreateContext: (spec: any) =>
    fetch('/api/cognition/create_context', { method: 'POST', headers: J, body: JSON.stringify({ spec }) }).then(jr),
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
