// F0 · the app controller — the carved brain of the former 1070-line Hud() (App.tsx:578–1269).
//
// WHAT THIS IS: a single hook holding ALL the former Hud-local state (the ~37 useState), the refs that
// MUST stay refs (the concurrency/cursor guards), and every editor-bound handler + effect. It is created
// once inside a component that has `useEditor` (Hud, in App.tsx) and exposed via AppContext so the carved
// presentational region components (Toolbar/Palette/Inspector/Inbox/Grow/Activity/RhmChat/Walkthrough/
// Workshop/OpPanels) read it without prop-drilling. This is the "state container" F0 calls for: ONE place,
// not 37 hooks scattered + 6 module globals (the globals moved to registryStore — the shape-reachable half).
//
// PRESERVED VERBATIM (the carve is a mechanical extraction, NOT a rewrite):
//  · reflects-never-owns — loadGraph prune + debounced equality-guarded write-back (the editor.store.listen).
//  · SSE mergeEvents seq-dedup + the openStream per-kind dispatch (gapless resume).
//  · the resolveUiTarget / show attention keystone (the single sink that drives the view to any address).
//  · wtBusyRef synchronous concurrency guards (one click = one request — these STAY refs, pre-render gating).
//  · the U1 fix: doRun(force?) with the always-clearing finally; call sites arrow-wrap (() => doRun()).
//  · voice push-to-talk, demonstrate-first, delete-confirm, semantic zoom, drag-to-wire (in NodeShape).
import { useState, useRef, useEffect } from 'react'
import { Editor, useValue } from 'tldraw'
import { api } from './api'
import { registryStore, setConnect, setForceRun, getUI_INFO } from './registryStore'
import { NodeShape, shapeIdFor, NODE_H, loadGraph, refresh } from './NodeShape'
import { J } from './api'

export function useAppController(editor: Editor) {
  const [edges, setEdges] = useState<{ from: string; from_port?: string; to: string; to_port?: string }[]>([])
  const [running, setRunning] = useState(false)
  // U4: a legible run-error surface. A real api.run()/refresh() rejection sets this; the toolbar shows it
  // with a retry, and it always clears `running` (no dead-end latch). null = no error.
  const [runError, setRunError] = useState<string | null>(null)
  // U2: the most-recent run's STUCK node ids — held here (from the run event/result) and re-applied onto the
  // shapes AFTER each loadGraph (the per-node /api/graph status is only ran|cached|idle and would overwrite).
  const stuckNodes = useRef<Set<string>>(new Set())
  // U3: when a run is in flight, the wall-clock start (ms) so the toolbar can show elapsed during the waits.
  const [runStartedAt, setRunStartedAt] = useState<number | null>(null)
  const [runElapsed, setRunElapsed] = useState(0)
  const [types, setTypes] = useState<string[]>([])
  const [gname, setGname] = useState('')
  const [gspec, setGspec] = useState('')
  const [surf, setSurf] = useState<any>(null)
  const [growMsg, setGrowMsg] = useState('the brain writes it · you approve · it goes live.')
  const [workshop, setWorkshop] = useState<any>(null)
  const [oinfo, setOinfo] = useState<any>({})
  // F8 (fleet surface): the live model fleet, fed from the registry (api.models per kind — the B2 source of
  // truth, never a hardcoded list). Shape: per-kind a string list of model names + a per-kind error string.
  // reflects-never-owns: this is READ truth off /api/models; the canvas never owns the fleet. fail-loud
  // (rule 4): a kind whose registry fetch FAILS carries its error so the panel surfaces it (never a silently
  // empty list). `alive` is NOT a per-model heartbeat (no such field exists in the registry — fabricating one
  // would break rule 8): a model PRESENT in the live registry list IS the live fleet for that kind; an empty
  // list with no error means the registry returned none. `loaded` flips true after the first fetch resolves
  // so the panel can distinguish "still booting" from "registry genuinely empty".
  const [fleet, setFleet] = useState<{ chat: string[]; embed: string[]; chatErr: string; embedErr: string; loaded: boolean }>(
    { chat: [], embed: [], chatErr: '', embedErr: '', loaded: false })
  // F3: the served node_states index (id -> {label, render{token,icon,shape}…}) mirrored into React state so
  // the Inspector (a context-reading region) paints status BY SIGHT from the registry, same as the shape does.
  const [nodeStates, setNodeStates] = useState<Record<string, any>>({})
  // registry-is-truth: per-mode descriptions read from capabilities().mode_directives (backend is the one
  // source). Default {} → every lookup falls back to '' until the snapshot loads (safe, never a stale guess).
  const [modeDesc, setModeDesc] = useState<Record<string, string>>({})
  const [notice, setNotice] = useState('')
  const [gid, setGid] = useState('codebase')
  const [layerView, setLayerView] = useState(0)   // 0 all · 1 origin only · 2 system only
  const [now, setNow] = useState<any>(null)
  const [events, setEvents] = useState<any[]>([])
  const [chat, setChat] = useState<any[]>([])
  const [chatMsg, setChatMsg] = useState('')
  const [chatBusy, setChatBusy] = useState(false)
  // I1 · click-to-indicate: the ui:// address of the element the operator has CLICKED to indicate (the
  // locus their next chat turn is about). null = nothing indicated. This is the WIDENED `focus`
  // vocabulary (seams-rhm Seam 4): a ui:// address rides in the SAME `focus.selected` list as canvas
  // node-ids — the backend `_chat_context` branches on the value (ui:// → INDICATING block; node-id →
  // co-presence block). We mirror the address in React (the chip / shipped focus) AND apply a PERSISTENT
  // `.ui-indicated` class on the DOM element (the visible selection — FORM), distinct from F4's TRANSIENT
  // `.ui-spotlight` ring (which the show-resolver flashes and removes after a timeout).
  const [indicated, setIndicated] = useState<string | null>(null)
  const indicatedRef = useRef<string | null>(null)   // for the capture handler (avoids a stale closure)
  // L9 · reverse journey-recording (§21.7#2-reverse). The REVERSE of the forward resolveUiTarget: an
  // EXPLICIT start/stop recording of the operator's ordered ui:// click-path as a DISTINCT journey-record
  // (NOT the review-session organ — that records item-ids; this records navigation). While `journeyId` is
  // set (recording is ON), every indicated ui:// address is appended as a step (in `indicate`); stopping
  // finalizes the record; replaying steps the view through the recorded addresses via the PRESERVED
  // resolveUiTarget (no second navigation mechanism). DISTINCT names from the voice-PTT `recording`/
  // `recordToggle` so the mic is untouched. The ref is read by the capture path (avoids a stale closure).
  const [journeyId, setJourneyId] = useState<string | null>(null)
  const journeyIdRef = useRef<string | null>(null)
  const [journeyReplaying, setJourneyReplaying] = useState(false)
  // I3 · propose-affordance (the CONSENT gate, click #2): when the RHM PROPOSES an action (emits a
  // structured {verb, address, args} on the chat response WITHOUT executing it), we hold it here as
  // EPHEMERAL state — NOT in the `chat` array (that array is replaced wholesale by r.history on the
  // next turn, which would vanish the card). The RhmChat region renders it as an approvable card; the
  // approve handler fires /api/act (api.act → the I2 dispatch path — REUSE, not a new path), so the
  // action runs ONLY on approve; dismiss just drops it (a reject does nothing). Mirrors the `indicated`
  // chip pattern (separate ephemeral state beside the chat log).
  const [proposal, setProposal] = useState<{ verb: string; address?: string | null; args?: any } | null>(null)
  // L3 · addressed history (§21.7#1): the trajectory of events stamped AT the indicated ui:// address —
  // "everything that happened here". Loaded by fetchHistory whenever the operator indicates an element;
  // rendered NAVIGABLE (grouped by kind) by the History region. null = nothing indicated / no history yet.
  const [history, setHistory] = useState<{ address: string; trajectory: any[] } | null>(null)
  const [historyBusy, setHistoryBusy] = useState(false)
  // L5 · self-change locating (§21.7#5): "what did the SYSTEM change HERE?" — the self-change audit log
  // FILTERED to the indicated ui:// element's code scope (the S3 address→code join). Loaded by
  // fetchSelfChanges whenever the operator indicates an element; rendered by the SelfChanges region with a
  // per-row revert (the EXISTING operator-only api.revert). Carries `stale`/`note` so the surface tells
  // "corpus stale — regenerate" apart from "no changes here" (fail-loud, never a silent empty).
  const [selfChanges, setSelfChanges] =
    useState<{ address: string; scope: string[]; stale: boolean; note: string; changes: any[] } | null>(null)
  const [selfChangesBusy, setSelfChangesBusy] = useState(false)
  // L10 · "stale at this address" (§21.7#10): the freshness verdict for the SELECTED node — is its cached
  // result out of date vs its CURRENT inputs? A COSTED DERIVATION (recompile + input-hash + _memo_sig
  // compare — seams-engine Seam 8a), NOT a free read, so it is fetched ON-DEMAND when a node WITH a stored
  // output is selected (the operator focusing a node is the request, mirroring how History/SelfChanges
  // load on indicate). null = nothing selected / no cached result to compare. The "cached" half is already
  // served (selected.status); L10 adds the derived "stale" half ALONGSIDE it — it does not change `cached`.
  const [freshness, setFreshness] =
    useState<{ address: string; stale: boolean | null; unknown?: boolean; reason?: string; volatile?: boolean } | null>(null)
  const [freshnessBusy, setFreshnessBusy] = useState(false)
  // L6 · live-history / versions at an address (§21.7#6): the TEMPORAL trail of values an addressed output
  // has held over time (GET /api/ref-versions → Suite.ref_versions → store.ref_history, appended on each
  // set_ref). The CURRENT value is the live portal window; this is the OTHER half — prior versions, each
  // fetchable by its surviving cas. Loaded ON-DEMAND when a node with a stored-output address is selected
  // (mirroring how freshness loads on selection). null = nothing selected / no versioned address.
  const [versions, setVersions] =
    useState<{ address: string; current: string | null; count: number;
               versions: { cas: string; ts: string; is_current: boolean; preview: string }[] } | null>(null)
  const [versionsBusy, setVersionsBusy] = useState(false)
  const [cfg, setCfg] = useState<any>({ model: '', persona: '' })
  const [cfgOpen, setCfgOpen] = useState(false)
  const [personas, setPersonas] = useState<any[]>([])   // Option A: the cast you can switch between (id·name·engine)
  const [voiceStatus, setVoiceStatus] = useState<string>('')   // V4.2: '' | 'loading' | 'ready' | 'down' (the persona voice's load state)
  const [recordingSession, setRecordingSession] = useState<string>('')   // V3.1: the active trial_session id when recording the conversation ('' = not recording)
  // U12: the /api/inbox payload is { live_escalations, resolved_for_you, batched, counts }. `batched` is a
  // SUBSET-grouping of live_escalations — NOT a third disjoint lane. We render the two real lanes.
  const [inbox, setInbox] = useState<any>({ live_escalations: [], resolved_for_you: [], batched: {}, counts: { escalations: 0, resolved: 0 } })
  const [showResolved, setShowResolved] = useState(false)   // U12: resolved-for-you collapsed by default
  const [drill, setDrill] = useState(false)
  const [reason, setReason] = useState('')
  const [lastChange, setLastChange] = useState<any>(null)
  const [panels, setPanels] = useState<any[]>([])
  const [recording, setRecording] = useState(false)
  const recorderRef = useRef<MediaRecorder | null>(null)
  // V2.1 — iOS audio unlock. iOS only plays audio that was unlocked by a USER GESTURE; the reply plays
  // ~5s later (post STT+brain), so a fresh `new Audio().play()` is blocked + silently dropped. We keep ONE
  // Web Audio AudioContext, resume() it inside the mic/send gesture (primeAudio), and play every reply
  // (and every streamed chunk, V2.2) through it — scheduled on a cursor so chunks play in order.
  const audioCtxRef = useRef<AudioContext | null>(null)
  const playCursorRef = useRef<number>(0)
  // V1.1 — auto-listen session (hands-free): tap to start, it auto-finalises each utterance on a finished
  // thought and re-listens, tap to stop. Distinct from push-to-talk (recordToggle). The ref holds the live
  // session so the second tap can end it.
  const autoListenRef = useRef<{ stop: boolean; stream: MediaStream | null }>({ stop: false, stream: null })
  // A2/A4: the selected node's live config (from /api/graph), keyed by nodeId — the inspector reads it
  // here, NOT off the tldraw shape props (which carry no config). Refreshed on every graph load.
  const configByNode = useRef<Record<string, any>>({})
  const [configTick, setConfigTick] = useState(0)   // bump to re-render the inspector form after a write
  // C5: per-node debounce timers for drag-end → /api/move (one write per settle, not per pointermove).
  const moveTimers = useRef<Record<string, any>>({})
  const streamSeq = useRef<number>(-1)              // G2: highest seq the client has seen (EventSource cursor)
  // B-frontend: the active review session — null when no walk is running.
  const [session, setSession] = useState<any>(null)
  const sessionRef = useRef<any>(null)              // mirror for the openStream closure
  const [wtReason, setWtReason] = useState('')      // the step's reject/comment WHY (captured into the verdict)
  const [voiceOn, setVoiceOn] = useState(true)      // F3: voice|text toggle — voice-first, falls back to text
  const [wtSpoke, setWtSpoke] = useState('')        // last voice status line for the card
  const spokenFor = useRef<string>('')              // F1: which (session:cursor) we've already spoken
  // CONCURRENCY GUARD: wtBusy DISABLES Next + every respond control while a request is in flight (the
  // visible/UX half). wtBusyRef is the LOAD-BEARING half: a rapid double-click can fire two handlers before
  // React commits the disabled re-render, so we gate on the ref synchronously at entry — one click = one
  // request, guaranteed. Cleared in `finally` so an error re-enables (never a dead end). PRESERVE-LIST item 6.
  const [wtBusy, setWtBusy] = useState(false)
  const wtBusyRef = useRef(false)
  sessionRef.current = session
  // F2 (responsive): the active MOBILE tab. At <699px the grid collapses to one column, the rails+overlays
  // are hidden (they overlap at phone width — fe-map §4), and a bottom tabbar drives which surface shows as a
  // bottom-sheet over the (always-mounted) canvas. 'canvas' = no sheet (board full-bleed). This state is INERT
  // on desktop/tablet (those breakpoints display:none the tabbar+sheets), so it never changes desktop layout.
  // tldraw stays mounted under the sheet at every width — semantic-zoom/drag-to-wire (preserve-list) intact.
  const [mobileTab, setMobileTab] = useState<'canvas' | 'palette' | 'inbox' | 'rhm'>('canvas')

  // Merge events by SEQ into the current list — an event already present (same seq) is never duplicated,
  // regardless of source. Makes `key={e.seq}` inherently unique and kills the "two children with the same
  // key" render-loop. Sorted newest-first; capped at the last 200. PRESERVE-LIST item 4.
  function mergeEvents(setter: typeof setEvents, incoming: any[]) {
    setter(prev => {
      const bySeq = new Map<number, any>()
      for (const e of prev) if (e && e.seq != null) bySeq.set(e.seq, e)
      for (const e of incoming) if (e && e.seq != null) bySeq.set(e.seq, e)
      return Array.from(bySeq.values()).sort((a, b) => b.seq - a.seq).slice(0, 200)
    })
  }
  async function poll() {
    // poll() MERGES events (never replaces) so it can't reintroduce a seq the stream already showed.
    // F7 (fail-loud, rule 4): a poll failure means the surfaces (now/events/inbox/last-change/panels) just
    // went STALE without any signal — the operator can't tell live data from frozen data. Surface a visible
    // notice instead of swallowing. This is self-limiting (the next successful op overwrites `notice`), so a
    // one-off transient blip clears itself rather than accumulating spam — but a persistent bridge-down stays
    // visible because nothing succeeds to clear it.
    try { setNow(await api.now()); mergeEvents(setEvents, await api.events()); setInbox(await api.inbox()); setLastChange(await api.lastChange()); setPanels(await api.panels()) }
    catch (e: any) { setNotice('⚠ refresh failed — surfaces may be stale (' + (e?.message || e) + ')') }
  }
  // F8 (fleet surface): (re)load the live model fleet from the registry, PER KIND so one endpoint being
  // down doesn't blank the other. fail-loud (rule 4): each kind captures its own error string — api.models
  // returns a normalized `{error}` on a non-ok response (api.ts jr), and a thrown network error is caught
  // here; either way the panel renders the error, never a silently empty list. registry-is-truth (rule 8):
  // the rows ARE the registry response; nothing is invented. Returns nothing — it writes the fleet state.
  async function refreshFleet() {
    for (const kind of ['chat', 'embed'] as const) {
      let list: string[] = []
      let err = ''
      try {
        const r = await api.models(kind)
        if (r && r.error) err = String(r.error)                 // normalized backend error (e.g. embed endpoint not configured)
        else if (Array.isArray(r)) list = r                     // the live model-name list for this kind
        else err = 'unexpected registry response'               // neither a list nor an {error} — surface it, never guess
      } catch (e: any) { err = e?.message || String(e) }        // network/transport failure — fail loud
      setFleet(prev => ({ ...prev, [kind]: list, [kind + 'Err']: err, loaded: true }))
    }
  }
  async function openCoa(id: string) {
    setGrowMsg('compiling the decision into a value-choice…')
    const c = await api.coa(id)            // decision-compiler UP
    setSurf({ id: c.id, name: c.raw?.name, code: c.raw?.code, coa: c.framing }); setDrill(false)
  }

  // mirror the latest graph's per-node config into the ref the inspector reads. Only bump the re-render
  // tick when the config actually CHANGED — so an unrelated live event during an edit doesn't re-mount the
  // form and drop an in-progress keystroke.
  function syncConfig(g: any) {
    const m: Record<string, any> = {}
    ;(g.nodes || []).forEach((n: any) => { m[n.id] = n.config || {} })
    const changed = JSON.stringify(m) !== JSON.stringify(configByNode.current)
    configByNode.current = m
    if (changed) setConfigTick(t => t + 1)
  }

  // load once, then go LIVE via the event stream (G2) — no 2.5s polling timer. PRESERVE: this keeps the
  // run-once initializer pattern (useState(()=>…)) + the editor.store.listen drag write-back verbatim.
  useState(() => {
    ;(window as any).__editor = editor   // automation/debug handle
    // C1: install the connect hook — a nub-drag commits the wire through /api/connect (backend owns it).
    setConnect((fn, fp, tn, tp) => { void doConnect(fn, fp, tn, tp) })
    // D4: install the per-node force-rerun hook.
    setForceRun((nid) => { void doRun([nid]) })
    // F7 (fail-loud, rule 4): boot fetches were each `try{…}catch{ /* */ }` — a bridge hiccup mid-boot left
    // the matching panel SILENTLY empty (no Notice, no signal). Now each swallow records WHICH source failed
    // into `bootErrors`; at the end of boot we surface ONE combined visible notice (Toolbar line 50 renders
    // `notice`). `notice` is last-write-wins and the boot happy-path NEVER calls setNotice, so a boot-error
    // notice persists until the operator's first action — and accumulating into one string means two boot
    // failures can't clobber each other into a single misleading line. We still degrade gracefully (the app
    // boots with whatever DID load) — fail-loud, not fail-stop.
    // bootErrors is declared HERE (above the outer try) so the catch below can fold the partial detail into the
    // final notice — a TOTAL bridge-down trips an UNGUARDED await first (objectInfo/loadGraph/types/…), which
    // before this aborted the IIFE as an "Uncaught (in promise)" and the combined notice was NEVER reached
    // (verified: forced dead-backend → shell rendered but blank panels, no notice). The outer catch turns that
    // unreachable-notice failure into a loud one without restructuring the individual awaits.
    const bootErrors: string[] = []
    ;(async () => {
     try {
      // B2: live model lists FIRST (the source of truth) so config_schema dropdowns resolve immediately.
      let modelOptions: Record<string, string[]> = {}
      try { modelOptions = { chat_models: await api.models('chat'), embed_models: await api.models('embed') } }
      catch (e: any) { bootErrors.push('model lists (' + (e?.message || e) + ')') }
      // F8 (fleet surface): populate the live fleet panel from the registry, PER KIND with its own error
      // (refreshFleet surfaces an embed-endpoint-not-configured or a down endpoint visibly, never silently
      // empty). Fire-and-forget (`void`): refreshFleet OWNS its fail-loud path — it catches each kind's error
      // INTO the fleet state, so a failure surfaces IN THE PANEL (the right place for it), independent of the
      // boot-notice path. Not awaited, so a slow/hung model endpoint never stalls the rest of boot.
      void refreshFleet()
      const oi = await api.objectInfo()
      let ui: Record<string, any> = {}
      try { ui = await api.uiInfo() }
      catch (e: any) { bootErrors.push('ui registry (' + (e?.message || e) + ')') }   // registry is the source of truth for ui:// targets — its absence MUST be visible
      registryStore.set({ OINFO: oi, MODEL_OPTIONS: modelOptions, UI_INFO: ui })   // C1: ports/schema/ui reachable by the shape + Edges
      setOinfo(oi)
      // registry-is-truth: pull the per-mode directives from capabilities() (backend MODE_DIRECTIVES is the
      // ONE source) so the presence dropdown shows backend truth, not a parallel hardcoded copy.
      // F3: ALSO index capabilities().node_states (7 states, each carrying label + S5's render{token,icon,shape})
      // into the store so the shape + inspector paint status BY SIGHT from the registry — a new state registered
      // engine-side then paints everywhere with zero FE edits (one-source, rule 3). Array -> {id: def} map.
      try {
        const caps = await api.capabilities(); setModeDesc(caps?.mode_directives || {})
        const ns = Array.isArray(caps?.node_states) ? caps.node_states : []
        const nsIndex: Record<string, any> = {}
        for (const s of ns) if (s && s.id) nsIndex[s.id] = s
        registryStore.set({ NODE_STATES: nsIndex })   // shape-reachable half (NodeShape reads via getNODE_STATES)
        setNodeStates(nsIndex)                         // React half (the Inspector region reads via context)
      } catch (e: any) { bootErrors.push('capabilities/node-states (' + (e?.message || e) + ')') }   // F7: status-by-sight + mode dial silently went blank on a swallow — surface it
      const g = await loadGraph(editor); setEdges(g.edges || []); setGid(g.id); syncConfig(g)
      if ((g.nodes || []).length) setTimeout(fitGraph, 120)   // U6: chrome-aware fit on first load
      setTypes(await api.types())
      // F5: chatHistory now resolves to `{error}` on a non-ok GET — never feed a non-array into `chat`
      // (RhmChat reads `chat.length`/`chat.map`). Defensive guard; the array path is unchanged.
      { const h = await api.chatHistory(); if (Array.isArray(h)) setChat(h) }
      setCfg(await api.rhmConfig())
      api.personas().then(p => setPersonas(Array.isArray(p) ? p : [])).catch(() => {})   // the switchable cast
      const evs = await api.events(); mergeEvents(setEvents, evs)
      streamSeq.current = evs.reduce((m: number, e: any) => Math.max(m, e.seq ?? -1), -1)  // cursor = last seen
      setNow(await api.now()); setInbox(await api.inbox()); setLastChange(await api.lastChange()); setPanels(await api.panels())
      // S7c (same-device resume): a persisted session id rehydrates the walk at the SAME cursor on reload.
      try {
        const sid = localStorage.getItem('company-review-session')
        if (sid) {
          const s = await api.reviewCurrent(sid)
          if (s && !s.error) setSession(s)
          else localStorage.removeItem('company-review-session')   // stale/closed — don't resurface a dead walk (EXPECTED, not an error — stays quiet)
        }
      } catch (e: any) {
        // F7: a stale/closed session resolving to `{error}` is EXPECTED (handled above, stays quiet). This
        // catch only fires on a real FETCH failure (bridge unreachable) — that is NOT expected and must be
        // visible, not a silent no-op that leaves a half-resumed walk.
        bootErrors.push('walk resume (' + (e?.message || e) + ')')
      }
      // F7: the GUARDED-fetch failures (above) accumulated into bootErrors; surface them as ONE visible notice
      // (fail-loud, rule 4). The UNGUARDED-await failures are caught by the outer catch below. Empty list +
      // no throw → boot was clean → stays silent. Set in `finally` so BOTH paths converge to one notice.
     } catch (e: any) {
       // F7: an UNGUARDED boot await rejected (a TOTAL bridge-down hits objectInfo/loadGraph/types/… before
       // the guarded blocks can complete). Without this the IIFE aborted as "Uncaught (in promise)" and the
       // shell rendered with blank panels and NO signal. Now it fails LOUD — fold in any partial detail.
       bootErrors.push('boot halted (' + (e?.message || e) + ')')
     } finally {
       // single convergence point for clean | partial | total-failure boot. Empty list → silent (clean boot).
       if (bootErrors.length) setNotice('⚠ boot incomplete — could not load: ' + bootErrors.join('; ') + ' (the bridge may be down)')
       // openStream in `finally` (NOT in the try): even on a boot failure the live surface must still connect,
       // so when the bridge returns the EventSource reconnect (es.onerror) recovers the surface on the next
       // event — fail-loud, NOT fail-stop (a boot reject must not strand the app dead-until-reload).
       openStream()                                       // G2: replaces setInterval(poll, 2500)
     }
    })()
    // C5: drag-end write-back. The {source:'user'} filter narrows to operator gestures; the LOAD-BEARING
    // loop-breaker is the equality guard below (from.x/y === to.x/y → skip). Debounced per-shape.
    const unlisten = editor.store.listen((entry) => {
      for (const rec of Object.values(entry.changes.updated)) {
        const [from, to]: any = rec as any
        if (!to || to.typeName !== 'shape' || to.type !== 'node') continue
        if (from && from.x === to.x && from.y === to.y) continue   // only POSITION changes write a move
        const nid = (to.props as any).nodeId; if (!nid) continue
        const x = to.x, y = to.y
        clearTimeout(moveTimers.current[nid])
        moveTimers.current[nid] = setTimeout(() => { void api.move(nid, x, y) }, 350)
      }
    }, { source: 'user', scope: 'document' })
    return unlisten
  })

  // G2: the live surface — one EventSource replaces the 2.5s poll. Each event is dispatched BY KIND to the
  // exact refresh the timer used to do blindly. Connect with ?since=<cursor> so we don't replay history.
  function openStream() {
    const since = streamSeq.current
    const es = new EventSource('/api/stream?since=' + since)
    es.onmessage = async (m) => {
      let ev: any; try { ev = JSON.parse(m.data) } catch { return }
      // Always merge the event into the log by SEQ (mergeEvents dedupes), so the log can NEVER hold two
      // children with the same key — even when backlogs overlap (this was the render-loop root cause).
      mergeEvents(setEvents, [ev])
      // The high-water gate gates DISPATCH (not the log): an event we've already acted on must not
      // re-trigger loadGraph/poll on a reconnect replay. Only genuinely-new seqs drive a refresh.
      if (ev.seq != null && ev.seq <= streamSeq.current) return
      if (ev.seq != null) streamSeq.current = ev.seq
      const k = ev.kind
      // structural changes → reload the graph (positions/edges/nodes/status)
      if (k === 'run' || k === 'create' || k === 'connect' || k === 'delete' || k === 'move') {
        // U2: a `run` event carries the scheduler's stuck/ran arrays directly — fold it in BEFORE the
        // repaint so the stuck overlay survives the loadGraph that follows (which only knows ran|cached|idle).
        if (k === 'run') applyStuckFromEvents([ev])
        const g = await loadGraph(editor); setEdges(g.edges || []); syncConfig(g)
        paintStuck()   // U2: re-apply stuck after loadGraph reset statuses to ran|cached|idle
        // F7 (fail-loud, rule 4): a genuinely-NEW event arrived (we're past the high-water gate) but the
        // follow-up refresh fetch failed → the surface is now STALE relative to a live event, with no signal.
        // Surface it. NOTE: this is NOT the SSE reconnect (that's es.onerror below — a transient retry, left
        // untouched). A per-event refresh failure is a real swallow; the reconnect is legitimate tolerate.
        try { setNow(await api.now()) } catch (e: any) { setNotice('⚠ live update missed a refresh (' + (e?.message || e) + ')') }
      } else if (k === 'mode' || k === 'config') {
        try { setNow(await api.now()); setCfg(await api.rhmConfig()) } catch (e: any) { setNotice('⚠ mode/config update missed a refresh (' + (e?.message || e) + ')') }
      } else if (k === 'ask' || k === 'reject' || k === 'resolve' || k === 'apply' || k === 'grow' || k === 'revert' || k.startsWith('decision.')) {
        // WIRE-UI: the decision→implementation wire emits `decision.*` events. NONE carry a companion `ask`,
        // so without this branch a surfaced build-intent / dispatch start / `implemented` close would fall
        // into the final `else` (setNow only) and the inbox/build-intent surface would go STALE.
        // startsWith('decision.') so the NEW `decision.surfaced_for_review` kind is handled the moment the
        // backend lane emits it — author-from-registry. Events already auto-merged at the top of onmessage.
        try { setInbox(await api.inbox()); setNow(await api.now()); setLastChange(await api.lastChange()); setPanels(await api.panels()) } catch (e: any) { setNotice('⚠ inbox/decision update missed a refresh (' + (e?.message || e) + ')') }
      } else if (k === 'chat' || k === 'react') {
        // F5: SSE-driven refresh — guard against a non-array (`{error}`) ever reaching the chat log.
        try { const h = await api.chatHistory(); if (Array.isArray(h)) setChat(h) } catch (e: any) { setNotice('⚠ chat update missed a refresh (' + (e?.message || e) + ')') }
      } else if (k === 'review.advance' || k === 'review.start') {
        // B-frontend: the walk advanced server-side. Refresh the card from present_current IF it's OUR
        // session — reflects-never-owns (the backend session is truth). refreshSession surfaces its own
        // failures via setNotice already (✕ session: …), so no extra wrap needed here.
        if (ev.session && sessionRef.current && ev.session === sessionRef.current.session) {
          await refreshSession(ev.session)
        }
      } else {
        try { setNow(await api.now()) } catch (e: any) { setNotice('⚠ live update missed a refresh (' + (e?.message || e) + ')') }
      }
    }
    // PRESERVE-LIST (transient tolerate, NOT a swallow): EventSource auto-reconnects on a dropped connection;
    // Last-Event-ID gives gapless resume. This is the ONE legitimate tolerate-then-retry — a reconnect is
    // expected operational churn, not a swallowed error, so it stays quiet by design. (F7 distinction.)
    es.onerror = () => { /* EventSource auto-reconnects; Last-Event-ID gives gapless resume */ }
  }

  async function reload() { const g = await loadGraph(editor); setEdges(g.edges || []); syncConfig(g); paintStuck(); await poll(); await maybeReact() }
  // U6: fit the graph but PAD for the chrome so no node tucks under the panels.
  // F2: the pad is READ FROM THE LIVE LAYOUT, not hardcoded panel px. fe-map §4 found these magic numbers
  // (158/330/56/240) DUPLICATED here and in app.css — they desync the moment the responsive grid changes a
  // track. Now we measure the actual rendered rails/toolbar via getBoundingClientRect() (the layout OWNS the
  // geometry; JS reads it — single source). At narrow breakpoints the rails are display:none → their rect
  // width/height is 0 → zero pad automatically, so a phone fit isn't padded for chrome that isn't there.
  function fitGraph() {
    const shapes = editor.getCurrentPageShapes().filter(s => s.type === 'node')
    if (!shapes.length) { editor.zoomToFit({ animation: { duration: 300 } }); return }
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity
    shapes.forEach(s => {
      const b = editor.getShapePageBounds(s.id); if (!b) return
      minX = Math.min(minX, b.minX); minY = Math.min(minY, b.minY)
      maxX = Math.max(maxX, b.maxX); maxY = Math.max(maxY, b.maxY)
    })
    if (!isFinite(minX)) { editor.zoomToFit({ animation: { duration: 300 } }); return }
    const z = editor.getZoomLevel() || 1
    // measure the chrome that actually overlaps the canvas at THIS width (0 when display:none)
    const rectW = (sel: string) => { const e = document.querySelector(sel) as HTMLElement | null; return e ? e.getBoundingClientRect().width : 0 }
    const rectH = (sel: string) => { const e = document.querySelector(sel) as HTMLElement | null; return e ? e.getBoundingClientRect().height : 0 }
    const GAP = 16                                                    // breathing room past the chrome edge
    const padL = (rectW('.as-rail') + GAP) / z                        // left rail (palette) — 0 on mobile
    const padR = (rectW('.as-panel') + GAP) / z                       // right rail (inspector) — 0 on mobile
    const padT = (rectH('.as-top') + GAP) / z                         // toolbar height (wraps → measured, not guessed)
    const padB = (Math.max(rectH('.as-canvas .activity'), rectH('.as-canvas .rhm')) + GAP) / z   // bottom overlays — 0 on mobile
    const bounds = { x: minX - padL, y: minY - padT, w: (maxX - minX) + padL + padR, h: (maxY - minY) + padT + padB }
    editor.zoomToBounds(bounds, { targetZoom: 1, animation: { duration: 300 } })
  }
  async function maybeReact() {   // watch-and-react: backend-gated, comments only in that mode
    // F7 (fail-loud, rule 4): this probe runs after every reload/run. A failure used to vanish silently — if
    // the brain is supposed to be reacting and the call dies, the operator should know it isn't. Self-limiting
    // (the next successful op overwrites `notice`), so a transient blip clears; a persistent failure stays up.
    try { const r = await api.react(); if (r.comment) { const h = await api.chatHistory(); if (Array.isArray(h)) setChat(h) } }
    catch (e: any) { setNotice('⚠ watch-and-react probe failed (' + (e?.message || e) + ')') }
  }
  // U5: a palette add seeds its position into the VISIBLE viewport. Operator-intent placement (the canvas
  // reporting where the operator placed it), NOT an invented layout: the position rides to the backend.
  async function addNode(type: string) {
    setNotice('+ ' + type)
    const vp = editor.getViewportPageBounds()
    const jitter = ((editor.getCurrentPageShapes().filter(s => s.type === 'node').length) % 5) * 26
    const x = Math.round(vp.midX - 120 + jitter)   // 120 = half a node's width (w:240)
    const y = Math.round(vp.midY - NODE_H / 2 + jitter)
    const r = await fetch('/api/node', { method: 'POST', headers: J, body: JSON.stringify({ type, config: {}, position: { x, y } }) }).then(x => x.json())
    await reload()
    const nid = r?.id
    if (nid) {
      const sid = shapeIdFor(nid)
      if (editor.getShape(sid)) {
        editor.select(sid)
        editor.zoomToSelection({ animation: { duration: 350 } })
        setTimeout(() => {
          const el = document.querySelector(`[data-shape-id="${sid}"] .node-card`) as HTMLElement | null
          if (el) { el.classList.add('node-flash'); setTimeout(() => el.classList.remove('node-flash'), 1400) }
        }, 60)
      }
      setNotice(`+ ${type} · ${nid} (added in view)`)
    }
  }
  async function wireSelected() {
    const sel = (editor.getSelectedShapes().filter(s => s.type === 'node') as NodeShape[])
    if (sel.length !== 2) { setNotice('select exactly two nodes to wire (left → right)'); return }
    const [a, b] = [...sel].sort((p, q) => p.x - q.x)
    const outs = Object.keys(oinfo[a.props.nodeType]?.ports?.outputs || {})
    const ins = Object.keys(oinfo[b.props.nodeType]?.ports?.inputs || {})
    if (!outs.length || !ins.length) { setNotice('those node-types have no compatible ports'); return }
    const r = await api.connect({ from_node: a.props.nodeId, from_port: outs[0], to_node: b.props.nodeId, to_port: ins[0] })
    if (r.error) setNotice('✕ ' + r.error)
    else { setNotice(`wired ${a.props.nodeId}.${outs[0]} → ${b.props.nodeId}.${ins[0]}`); await reload() }
  }
  // C1: a drag from an output nub to an input nub. The backend TYPE-CHECKS the wire and OWNS the edge.
  async function doConnect(from_node: string, from_port: string, to_node: string, to_port: string) {
    const r = await api.connect({ from_node, from_port, to_node, to_port })
    if (r?.error) setNotice('✕ ' + r.error)
    else { setNotice(`wired ${from_node}.${from_port} → ${to_node}.${to_port}`); const g = await loadGraph(editor); setEdges(g.edges || []); syncConfig(g) }
  }
  // A2: write one config key on a node → /api/set (merge) → refresh so the inspector shows the merged value.
  async function setNodeConfig(nodeId: string, key: string, value: any) {
    setNotice(`set ${nodeId}.${key}`)
    const g = await api.set(nodeId, { [key]: value })
    if (g?.error) { setNotice('✕ ' + g.error); return }
    setEdges(g.edges || []); syncConfig(g); await refresh(editor, g)
  }
  // F2: route the selected node's OUTPUT to the decision surface (inbox/COA).
  async function surfaceOutput(nodeId: string) {
    setNotice('surfacing output of ' + nodeId + ' → inbox')
    const r = await api.surfaceOutput(nodeId)
    if (r?.error) { setNotice('✕ ' + r.error); return }
    setNotice(`→ inbox · ${r.name} (drill from the inbox to decide)`); await poll()
  }
  // F3: choose "build from this output" — prefill the GROW panel's spec with the node's output and focus it.
  function buildFromOutput(nodeId: string, output: string) {
    setGname('')
    setGspec(output || '')
    setSurf(null)
    setGrowMsg(`build a node from ${nodeId}'s output — name it, refine the spec, then dispatch.`)
    setNotice('build-from-output → grow panel (edit + dispatch)')
  }
  async function deleteSelected() {
    const sel = (editor.getSelectedShapes().filter(s => s.type === 'node') as NodeShape[])
    if (!sel.length) { setNotice('select node(s) to delete'); return }
    // U10: guard the only real destructive path — a single click must not irreversibly delete. Confirm
    // first (names the nodes). PRESERVE-LIST: delete-confirm.
    const names = sel.map(s => s.props.nodeId).join(', ')
    if (!window.confirm(`Delete ${sel.length} node(s)?\n\n${names}\n\nThis removes them from the graph.`)) {
      setNotice('delete cancelled'); return
    }
    for (const s of sel) await api.del(s.props.nodeId)
    setNotice(`deleted ${sel.length} node(s)`); await reload()
  }
  // I1 · click-to-indicate. Make `addr` the indicated locus: paint the PERSISTENT visible selection on
  // its DOM element (single-selection — clear any prior one first) and mirror it in React (the chip +
  // the shipped focus). Passing null/an unresolvable address CLEARS the indication. The class is applied
  // to the element whose data-ui-ref attribute equals the full ui:// address (F4 stamps these); if that
  // element isn't in the DOM right now we still keep the address as the locus (the backend resolves it
  // from the registry), just without a visible ring — surfaced, never a silent no-op.
  function clearIndicatedDom() {
    document.querySelectorAll('.ui-indicated').forEach(el => {
      el.classList.remove('ui-indicated'); el.removeAttribute('data-click-mode')   // I5: drop the prior mode cue too
    })
  }
  // I5 · the annotate-vs-operate ROUTING HINT (the FORM default — needs-tim). Classify which FACE a
  // BARE click (no consequential verb) at `addr` is in. THIS MIRRORS THE CANONICAL BACKEND RULE
  // (Suite.route_click) EXACTLY — single-source, so the visible cue never contradicts what fires:
  //   • `run://` (a LIVE graph-node instance) → 'operate'  (a click proposes/runs an operation).
  //   • `ui://`  (a DESIGN/UI element)         → 'annotate' (a bare click attaches a comment), ALWAYS.
  // The scheme is a ROUTING HINT, not the gate (design-substrate CONTRACT.2): the read-only `show`/
  // camera drive is reached by an EXPLICIT `show` VERB (the RHM / the I3 approve path), NOT by a bare
  // click — so a bare click on a drivenReadOnly element still ANNOTATES (matching route_click). The
  // actual safety gate for a verb-bearing operate click is the BACKEND's address→tier (I4) + guard().
  // Verb-bearing controls (a RUN button) operate via their own onClick regardless of this cue.
  function clickMode(addr: string | null | undefined): 'annotate' | 'operate' | null {
    if (!addr) return null
    if (addr.startsWith('run://')) return 'operate'            // a live instance — always the operate face
    if (!addr.startsWith('ui://')) return null
    return 'annotate'                                          // a ui:// element, no verb → annotate (route_click rule)
  }
  function indicate(addr: string | null) {
    clearIndicatedDom()
    if (!addr) { indicatedRef.current = null; setIndicated(null); setNotice('indication cleared'); return }
    indicatedRef.current = addr; setIndicated(addr)
    const el = document.querySelector('[data-ui-ref="' + addr + '"]') as HTMLElement | null
    const mode = clickMode(addr)
    if (el) { el.classList.add('ui-indicated'); if (mode) el.setAttribute('data-click-mode', mode) }   // I5: paint the mode cue
    const title = getUI_INFO()[addr]?.title
    const modeWord = mode === 'annotate' ? ' — click to comment' : mode === 'operate' ? ' — click to operate' : ''
    setNotice('indicating ' + (title || addr) + ' — your next message is about this' + modeWord)
    // L9 · capture wire: while a journey is RECORDING, this indicated ui:// address is appended as the
    // next step of the ordered path. Only full ui:// addresses reach here (the capture listener already
    // filters), and only on a real indication (addr non-null — the clear/toggle-off path returned above),
    // so an indicate(null) never records a step. The append is S0-validated server-side (fail loud).
    if (journeyIdRef.current) recordJourneyStep(addr)
  }
  // L9 · the step-append, factored so `indicate` stays focused. Fire-and-surface: a backend 400 (malformed
  // address — shouldn't happen since only registered ui:// refs indicate, but fail-loud anyway) surfaces a
  // notice, never a silent swallow (rule 4). Recording continues; one bad step doesn't end the journey.
  async function recordJourneyStep(addr: string) {
    const jid = journeyIdRef.current
    if (!jid) return
    try {
      const r = await api.journeyStep(jid, addr)
      if (r?.error) { setNotice('✕ journey step: ' + r.error); return }
      const n = Array.isArray(r?.steps) ? r.steps.length : '?'
      setNotice('● recording journey — step ' + n + ': ' + (getUI_INFO()[addr]?.title || addr))
    } catch (e: any) { setNotice('✕ could not record journey step: ' + (e?.message || e)) }
  }
  // I5 · the ANNOTATE commit gesture — the click→comment that makes the annotate FUNCTION reachable on
  // the surface (the criteria FUNCTION: "clicking a ui:// attaches a comment"). Fires POST /api/annotate
  // (the I6 endpoint) for the indicated `ui://` locus. Fail-loud (rule 4): no locus / not a ui:// element
  // / empty text → a visible notice, never a silent no-op. api.ts is off-limits here, so the fetch is
  // inline (the same J header the rest of the app uses). The OPERATE face is reached separately (a
  // control's own onClick → /api/act, and the I3 approve→/api/act path) — never blurred with this.
  async function annotateLocus(text: string) {
    const addr = indicatedRef.current
    if (!addr || !addr.startsWith('ui://')) { setNotice('✕ indicate a ui:// element first, then comment'); return }
    const body = (text || '').trim()
    if (!body) { setNotice('✕ a comment needs text (no silent no-op)'); return }
    try {
      const r = await fetch('/api/annotate', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ address: addr, text: body }),
      }).then(x => x.json())
      if (r?.error) { setNotice('✕ ' + r.error); return }       // fail-loud: surface the backend 400, never swallow
      const title = getUI_INFO()[addr]?.title
      setNotice('💬 comment attached to ' + (title || addr))     // the annotate face's "did X" (rule 4)
    } catch (e: any) { setNotice('✕ could not attach comment: ' + (e?.message || e)) }
  }
  // A document-level CAPTURE listener: a click on any element carrying a ui:// data-ui-ref INDICATES it.
  // Capture phase + read the nearest [data-ui-ref] ancestor so a click on an inner glyph still resolves
  // to the addressed container; we DON'T preventDefault/stopPropagation — indicating is additive, the
  // element's own onClick still fires (a RUN button still runs AND becomes the indicated locus). Only
  // FULL ui:// refs indicate (the locus vocabulary); bare-handle legacy refs are skipped.
  // EXCLUSION (advisor): the RHM chat's OWN operating controls (ui://chat/* — input, send, mic, config,
  // model-field, all F4-stamped) are how the operator CONVERSES, not things they point at. Without this
  // the most basic flow self-destructs: click an element to indicate it → click the chat input to type →
  // the input's ui://chat/input would OVERWRITE the locus → every message becomes "about the input/send".
  // So a click anywhere inside the chat region (the .rhm container is bare-keyed "chat") leaves the
  // current indication UNTOUCHED — you point with the rest of the surface, then talk in the chat.
  useEffect(() => {
    function onDocClick(e: MouseEvent) {
      const tgt = e.target as HTMLElement | null
      if (tgt?.closest?.('[data-ui-ref="chat"]')) return    // inside the chat region → conversing, never indicating
      const t = tgt?.closest?.('[data-ui-ref]') as HTMLElement | null
      if (!t) return
      const ref = t.getAttribute('data-ui-ref') || ''
      if (!ref.startsWith('ui://')) return       // only full ui:// addresses are loci (skip bare/run:// carriers)
      if (ref === indicatedRef.current) { indicate(null); return }   // click the indicated thing again → toggle off
      indicate(ref)
    }
    document.addEventListener('click', onDocClick, true)   // capture: see it before the element's own onClick stops it
    return () => document.removeEventListener('click', onDocClick, true)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])
  // L3 · addressed history (§21.7#1). When the operator INDICATES a ui:// element, load "everything that
  // happened here" — the GET /api/address-history trajectory for that locus. Reflects-never-owns: the
  // runtime is authoritative, the surface just reads. Clearing the indication clears the history. A
  // backend 400 (malformed address) is surfaced as a notice + empty trajectory (fail-loud, rule 4 — never
  // a silent swallow). The live SSE feed also re-pokes it (poll bumps a tick) so a NEW addressed event at
  // the indicated locus shows without a re-click — but the cheap, always-correct trigger is `indicated`.
  async function fetchHistory(addr: string | null) {
    if (!addr || !addr.startsWith('ui://')) { setHistory(null); return }   // only ui:// loci carry an addressed view
    setHistoryBusy(true)
    try {
      const r = await api.addressHistory(addr)
      if (r?.error) { setHistory({ address: addr, trajectory: [] }); setNotice('✕ ' + r.error); return }
      setHistory({ address: addr, trajectory: Array.isArray(r?.trajectory) ? r.trajectory : [] })
    } catch (e: any) {
      setHistory({ address: addr, trajectory: [] }); setNotice('✕ could not load history: ' + (e?.message || e))
    } finally { setHistoryBusy(false) }
  }
  // Load the history whenever the indicated locus changes (and re-load when the live event count moves, so
  // a fresh addressed event at THIS locus appears without a re-click — events.length is the cheap poke).
  useEffect(() => { fetchHistory(indicated) /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [indicated, events.length])
  // L5 · self-change locating (§21.7#5). When the operator INDICATES a ui:// element, load "what did the
  // SYSTEM change HERE?" — the self-change audit log filtered by the S3 address→code scope join. Mirrors
  // fetchHistory exactly: reflects-never-owns (the runtime is authoritative; this only reads). A backend
  // 400 (malformed address) is surfaced as a notice (fail-loud, rule 4 — never a silent swallow). STALE
  // TRICHOTOMY is carried through whole (stale/note) so the region renders "corpus stale — regenerate"
  // distinctly from "no self-changes here." Re-poked by events.length so a fresh self-apply at THIS locus
  // appears without a re-click.
  async function fetchSelfChanges(addr: string | null) {
    if (!addr || !addr.startsWith('ui://')) { setSelfChanges(null); return }   // only ui:// loci have a code scope
    setSelfChangesBusy(true)
    try {
      const r = await api.selfChangesAt(addr)
      if (r?.error) {
        setSelfChanges({ address: addr, scope: [], stale: false, note: r.error, changes: [] })
        setNotice('✕ ' + r.error); return
      }
      setSelfChanges({
        address: addr,
        scope: Array.isArray(r?.scope) ? r.scope : [],
        stale: !!r?.stale,
        note: r?.note || '',
        changes: Array.isArray(r?.changes) ? r.changes : [],
      })
    } catch (e: any) {
      setSelfChanges({ address: addr, scope: [], stale: false, note: '', changes: [] })
      setNotice('✕ could not load self-changes: ' + (e?.message || e))
    } finally { setSelfChangesBusy(false) }
  }
  useEffect(() => { fetchSelfChanges(indicated) /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [indicated, events.length])
  // Revert a self-change FROM the indicated element — reuses the EXISTING operator-only api.revert(sha)
  // (the /api/revert gate; no new revert path). After it lands, re-read the located list so the row clears.
  async function revertSelfChangeAt(sha: string) {
    if (!sha) return
    setNotice('rolling back self-change ' + sha.slice(0, 8) + '…')
    const r = await api.revert(sha)
    if (r?.error) { setNotice('✕ revert failed: ' + r.error); return }
    setNotice('↩ reverted ' + sha.slice(0, 8) + ' — undone (git ' + (r.head || '').slice(0, 8) + '). bounded, recoverable.')
    setTypes(await api.types()); await fetchSelfChanges(indicated); setLastChange(await api.lastChange())
  }
  async function sendChat(override?: string) {
    const m = (override ?? chatMsg).trim()
    if (!m || chatBusy) return
    primeAudio()                                               // V2.1: unlock audio in the send gesture (typed-chat voice-out)
    setChatMsg(''); setChatBusy(true)
    setChat(c => [...c, { role: 'user', text: m }])
    // I3 — consent integrity: clear any prior un-acted proposal BEFORE this turn. A card the operator
    // ignored must not linger beside a new answer (approving it later would fire the OLD, now out-of-
    // context, verb-at-address). A fresh proposal (if this turn carries one) is set below from r.proposal.
    setProposal(null)
    try {
      // co-presence: the RHM sees what the operator has selected on the canvas right now (node-ids) AND
      // the ui:// address they've CLICKED to indicate (I1) — BOTH ride in the one `focus.selected` list
      // (the widened vocabulary; the backend branches on each value). The indicated address goes first so
      // the INDICATING block leads when both are present.
      const nodeIds = (editor.getSelectedShapes().filter(s => s.type === 'node') as NodeShape[]).map(s => s.props.nodeId)
      const selected = indicatedRef.current ? [indicatedRef.current, ...nodeIds] : nodeIds
      const r = await api.chat(m, { selected })
      // F5 · the named bug. On a backend 400 (model unreachable — the literal first thing an operator hits)
      // api.chat now resolves to a normalized `{error}` (api.ts jr). BEFORE F5 this did `setChat(r.history)`
      // = `setChat(undefined)` → RhmChat `chat.length` threw at render → white-screen. Now: surface the
      // backend's error text as a VISIBLE assistant message (fail-loud, rule 4 — never a silent swallow) and
      // return WITHOUT touching the chat array. `finally` clears chatBusy. No throw, no undefined setChat.
      if (r.error) { setChat(c => [...c, { role: 'assistant', text: '⚠ ' + r.error }]); return }
      // defensive (advisor): only replace the log with a real array. A future non-ok GET would resolve to
      // `{error}` (no `.history`); never `setChat(undefined)`.
      if (Array.isArray(r.history)) setChat(r.history)
      await poll()
      if (now?.mode === 'listening' && r.reply) speakReply(r.reply).catch(() => { /* TTS hiccup is harmless here */ })   // voice out
      // I3 — the CONSENT gate: if the RHM PROPOSED an action (a structured {verb, address, args} on the
      // response, with action===null because nothing ran), hold it for the operator to APPROVE. The card
      // renders in RhmChat; approveProposal fires /api/act. Nothing executes here (the whole point).
      if (r.proposal) { setProposal(r.proposal); return }
      // the decision-compiler DOWN: an action the RHM TOOK (execute-then-render — PRESERVED) routes its
      // post-hoc reaction through the SAME handler the approve path reuses.
      await applyActionReactions(r.action)
    }
    catch { setChat(c => [...c, { role: 'assistant', text: '(could not reach the brain)' }]) }
    finally { setChatBusy(false) }
  }

  // I3 — the post-dispatch reaction handler, factored out so BOTH the execute-then-render chat path
  // (sendChat, PRESERVED verbatim) AND the propose-affordance APPROVE path (approveProposal → /api/act)
  // drive the SAME reactions. This is what makes "approving runs the verb EXACTLY as it would have"
  // true: the approve path is the I2 dispatch path, and its outcome reaction is this one handler.
  async function applyActionReactions(action: any) {
    if (!action) return
    if (action.did === 'run' || action.did === 'build') { await reload() }
    if (action.did === 'show') {           // attention-direction: move the operator's view (THE KEYSTONE)
      const targets: string[] = action.targets || []
      const canvasIds = targets.filter(t => !t.startsWith('ui://')).map((nid: string) => shapeIdFor(nid)).filter((id: any) => editor.getShape(id))
      if (canvasIds.length) { editor.select(...canvasIds); editor.zoomToSelection({ animation: { duration: 450 } }) }
      targets.forEach(t => { if (t.startsWith('ui://')) resolveUiTarget(t) })   // chrome/panel/canvas-by-address
    }
    if (action.did === 'propose') {
      const all = await fetch('/api/surfaced').then(x => x.json())
      const d = all.find((x: any) => x.id === action.surfaced)
      if (d) setSurf({ id: d.id, name: d.payload.name, code: d.payload.code })   // → operator approves in GROW panel
    }
    if (action.did === 'panel') {            // update the interface through the interface
      const all = await fetch('/api/surfaced').then(x => x.json())
      const d = all.find((x: any) => x.id === action.surfaced)
      if (d) setSurf({ id: d.id, name: d.payload.name, code: JSON.stringify(d.payload.panel, null, 2), isPanel: true })
    }
    if (action.did === 'extend') {           // arbitrary code → build-gated on approve
      const all = await fetch('/api/surfaced').then(x => x.json())
      const d = all.find((x: any) => x.id === action.surfaced)
      if (d) setSurf({ id: d.id, name: d.payload.name, code: d.payload.code, isExt: true })
    }
  }

  // I3 — APPROVE (click #2, the consent commit): fire the proposed verb-at-address through /api/act
  // (the I2 dispatch path — REUSE, never a new path). The action runs ONLY here, on the operator's
  // approve. Then drive the SAME post-dispatch reaction the chat path uses, surface the "did X"
  // confirmation as an assistant message, and clear the card. Fail-loud on a backend error (rule 4).
  async function approveProposal() {
    const p = proposal
    if (!p || chatBusy) return
    setChatBusy(true)
    try {
      const r = await api.act(p.verb, p.address || undefined, p.args)
      if (r.error) { setChat(c => [...c, { role: 'assistant', text: '⚠ ' + r.error }]) }
      else {
        if (r.reply) setChat(c => [...c, { role: 'assistant', text: '✓ ' + r.reply }])
        await applyActionReactions(r.action)
        await poll()
      }
    }
    catch { setChat(c => [...c, { role: 'assistant', text: '(could not reach the brain to act)' }]) }
    finally { setProposal(null); setChatBusy(false) }
  }
  // I3 — REJECT/DISMISS does nothing but drop the card (no backend call; the action never ran).
  function dismissProposal() { setProposal(null) }
  async function changeMode(mm: string) { setNotice('presence → ' + mm); await api.setMode(mm); await poll() }
  async function applyCfg() {
    const c = await api.setRhmConfig({ model: cfg.model, persona: cfg.persona })
    setCfg(c); setCfgOpen(false); setNotice('RHM config → ' + (c.model || 'default')); await poll()
  }
  // Option A — switch between the personas: set the chosen persona AS active and AUTO-LOAD its voice
  // (the backend evicts the previous voice engine to fit the 16 GB card, then cold-loads this one —
  // accepted that a switch may cold-load). We optimistically reflect the new persona, then poll the
  // engine to 'up' so the operator sees when it's ready to speak. Fail-loud on the notice; never a
  // silent no-op. (A persona whose voice won't fit even after eviction — e.g. orpheus beside a big
  // brain — surfaces the budget gate's reason here.)
  async function switchPersona(id: string) {
    if (!id || id === cfg.persona) { setCfg((c: any) => ({ ...c, persona: id })); return }
    setCfg((c: any) => ({ ...c, persona: id }))
    setVoiceStatus('loading')                            // V4.2: badge tracks the cold-load
    setNotice(`switching to ${id} — cold-loading their voice…`)
    try {
      const r = await api.voiceSwitch(id)
      if (r.error) { setVoiceStatus('down'); setNotice('⚠ could not switch to ' + id + ': ' + r.error); return }
      if (r.service) {                                  // an engine that needs loading (not an always-on one)
        const dl = Date.now() + 240000                  // the heavy voices (orpheus) cold-load in minutes
        for (;;) {
          const sv = await api.voiceServices().catch(() => null)
          const st = sv?.services?.[r.service]?.state
          if (st === 'up') break
          if (st === 'down' || Date.now() > dl) { setVoiceStatus('down'); setNotice(`⚠ ${id}'s voice (${r.engine}) didn't come up — open the voice panel`); break }
          await new Promise(res => setTimeout(res, 3000))
        }
      }
      setVoiceStatus('ready')
      setNotice(`${id} is ready — talk (🎙) or type; it speaks back in listening mode`)
      setCfg(await api.rhmConfig())
    } catch (e: any) { setNotice('⚠ switch failed: ' + (e?.message || e)) }
  }
  function cycleLayers() {
    const next = (layerView + 1) % 3
    setLayerView(next)
    const b = document.body.classList
    b.remove('layers-dim', 'layers-dim-authored')
    if (next === 1) { b.add('layers-dim'); setNotice('layers · origin only (system-derived dimmed)') }
    else if (next === 2) { b.add('layers-dim-authored'); setNotice('layers · system-derived only (origin dimmed)') }
    else setNotice('layers · all')
  }
  async function portalSelected() {
    const sel = (editor.getSelectedShapes().filter(s => s.type === 'node') as NodeShape[])
    if (sel.length !== 1) { setNotice('select one node to open a live portal onto it'); return }
    const src = sel[0]
    if (src.props.nodeType === 'portal') { setNotice('that is already a portal'); return }
    const ref = `run://${gid}/${src.props.nodeId}`
    await api.addNode('portal', { ref })
    setNotice(`portal → ${ref} (one artefact, live view)`); await reload()
  }

  // C2/C3 — THE KEYSTONE (frontend half): resolveUiTarget moves the operator's view to ANY addressable UI
  // thing. The SINGLE sink for both attention-direction entry points (the chat `show` action AND the
  // walkthrough card's per-step drive). PRESERVE-LIST item 5. registry-is-truth: a ui:// ref is validated
  // against UI_INFO (from /api/ui_info) — an UNKNOWN ref fails loud with a notice, never a silent no-op.
  function resolveUiTarget(target?: string): boolean {
    if (!target) return false
    if (!target.startsWith('ui://')) return driveCanvas(target)   // form 1: bare node-id → canvas camera
    // RES1 (F8 follow-up): the S0 canonical grammar is ui://<region>/<element>[/<sub>][/@state] where the
    // ELEMENT segment is now OPTIONAL — region-only addresses (ui://models, ui://inbox, ui://chat, …) are
    // valid AND registered in S1 (the 12 region-only corpus rows, served by /api/ui_info, DOM-stamped by
    // F4). The old regex /^ui:\/\/([^/]+)\/(.+)$/ REQUIRED a /<element> after the region, so every
    // region-only address returned "malformed" and could not be DRIVEN via show/walkthrough. We WIDEN the
    // accepted grammar to BOTH forms without rewriting the resolver (PRESERVE-LIST item 5): the existing
    // kind/element path below is unchanged byte-for-byte; we ADD a region-only/full-string branch in
    // front of it that mirrors the backend _describe_ui_address (suite.py) matching — a registry row is
    // matched by EITHER its full-string key (the corpus element + region-only rows, keyed by the whole
    // ui:// address) OR the live region served-form ui://<kind>/<ref> (the bare-keyed chrome regions).
    // GRAMMAR GATE (fail loud, rule 4): ui:// + ≥1 non-empty path segment, optional trailing /@state or
    // @state — structurally identical to contracts/ui_info.py parse_ui_address. A non-conforming string
    // (e.g. "ui://" alone, or no segments) is still rejected as malformed.
    if (!/^ui:\/\/[^/@]+(?:\/[^/@]+)*(?:\/?@[^/@]+)?$/.test(target)) {
      setNotice('✕ malformed ui:// target: ' + target); return false
    }
    const UI_INFO = getUI_INFO()
    // canvas branch — first segment "canvas" drives the camera (PRESERVED). Covers the live served forms
    // ui://canvas/* (whole canvas) and ui://canvas/<node-id>, AND the region-only ui://canvas (→ fit).
    // NOTE (pre-existing, not a RES1 change): ui://canvas/<elem> like ui://canvas/portal-window /
    // ui://canvas/node route to the CAMERA path (driveCanvas), not to their DOM elements — the canvas
    // overlap was always camera-resolved. Left as-is.
    const canvasMm = target.match(/^ui:\/\/canvas(?:\/(.+))?$/)
    if (canvasMm) {
      const ref = canvasMm[1]
      if (ref == null || ref === '*') { editor.zoomToFit({ animation: { duration: 450 } }); setNotice('→ canvas'); return true }
      return driveCanvas(ref)
    }
    // RES1 (F8 follow-up) — REGION-ONLY addresses (single segment, e.g. ui://inbox, ui://models). Two DOM
    // conventions coexist (this is the reconciliation, mirroring backend _describe_ui_address's two match
    // arms — ref==address (full-key) OR served==address (region served-form)):
    //   • the 7 LEGACY chrome regions (inbox/chat/activity/inspector/toolbar/walkthrough/workshop) are
    //     keyed BARE in the registry (UI_INFO["inbox"]) and carry the BARE DOM data-ui-ref="inbox". For
    //     these, route the bare key through the EXISTING kind/element tail below so ui://inbox resolves
    //     BYTE-FOR-BYTE identically to the served ui://chrome/inbox form (same DOM key, title, openable).
    //   • the corpus-only region rows (models/grow/tabbar/twin) have NO bare twin; they are keyed by the
    //     FULL string (UI_INFO["ui://models"]) and the DOM carries data-ui-ref="ui://models". Full-string DOM.
    // SCOPE: bare resolution is SINGLE-SEGMENT ONLY — ui://toolbar/run is NEVER stripped to bare "run".
    const regionMm = target.match(/^ui:\/\/([^/@]+)$/)   // exactly one segment, no element, no @state
    let ref: string
    if (regionMm) {
      const region = regionMm[1]
      if (UI_INFO[region] != null) {
        ref = region                                     // bare row exists → existing kind/element tail (served-form mirror)
      } else if (UI_INFO[target] != null) {
        return spotlightUiRef(target, target, UI_INFO)   // full-string corpus region row → full-string DOM
      } else if (Object.keys(UI_INFO).length) {
        // well-formed but UNREGISTERED — fail loud as "no registered UI target", NOT "malformed" (mirrors
        // backend _describe_ui_address's "(unregistered)" arm: unregistered ≠ malformed grammar).
        setNotice('✕ no registered UI target for ' + target + ' (registry is truth)'); return false
      } else {
        ref = region                                     // registry not loaded yet — defer to the DOM tail
      }
    } else {
      // RES1 multi-segment / full-string branch: a region+element (+sub/@state) address. The DOM carries
      // the WHOLE ui:// string verbatim (F4 stamps full strings for the corpus element rows, e.g.
      // data-ui-ref="ui://toolbar/run", data-ui-ref="ui://inbox/build-review"). If the full address is a
      // registry key, resolve by it directly (the kind/element split below would mis-key it to a bare
      // "run"). Mirrors backend _describe_ui_address's full-key arm.
      if (UI_INFO[target] != null) {
        return spotlightUiRef(target, target, UI_INFO)   // domKey === infoKey === the full address
      }
      // EXISTING kind/element served-form path (PRESERVED byte-for-byte): ui://<kind>/<ref> where kind ∈
      // {chrome,field,panel,ext} and <ref> is the BARE registry key (ui://chrome/inbox → key "inbox",
      // DOM data-ui-ref="inbox"). This is what backend show/_registry_ui_target emits today; unchanged.
      const mm = target.match(/^ui:\/\/([^/]+)\/(.+)$/)
      if (!mm) { setNotice('✕ malformed ui:// target: ' + target); return false }
      ref = mm[2]
    }
    // chrome | field | panel | ext → a DOM target. Validate against the registry (fail loud if unknown).
    if (UI_INFO[ref] == null && Object.keys(UI_INFO).length) {
      setNotice('✕ no registered UI target for ' + ref + ' (registry is truth)'); return false
    }
    // openable (e.g. workshop) must be OPEN before we can scroll to it — honor the capability from the registry.
    if (UI_INFO[ref]?.capabilities?.openable && ref === 'workshop' && !workshop && selectedRef.current) {
      setWorkshop(selectedRef.current)   // open the workshop onto the current selection so the target exists in the DOM
    }
    return spotlightUiRef(ref, ref, UI_INFO)
  }
  // RES1: the shared DOM-spotlight tail of resolveUiTarget — querySelector the data-ui-ref, scroll it into
  // view, ring it (fail loud if it's not mounted right now). Factored out so the existing kind/element path
  // and the new region-only/full-string path drive the SAME spotlight behaviour verbatim (no behaviour
  // drift). `domKey` is the data-ui-ref value to query; `infoKey` is the UI_INFO key for the title.
  function spotlightUiRef(domKey: string, infoKey: string, UI_INFO: Record<string, any>): boolean {
    // defer one frame so a just-opened region is mounted before we query for it (fail loud if still absent).
    setTimeout(() => {
      const el = document.querySelector('[data-ui-ref="' + domKey + '"]') as HTMLElement | null
      if (!el) { setNotice('✕ UI target not in the DOM right now: ' + domKey); return }
      el.scrollIntoView({ block: 'center', behavior: 'smooth' })
      el.classList.add('ui-spotlight')
      setNotice('→ ' + (UI_INFO[infoKey]?.title || infoKey))
      setTimeout(() => el.classList.remove('ui-spotlight'), 2400)   // transient ring — additive, no layout reflow
    }, 30)
    return true
  }
  // the canvas camera path — reused by both ui://canvas/<id> and a bare node-id. A node-id with no shape
  // fails loud (we never point at nothing).
  function driveCanvas(nodeId: string): boolean {
    const id = shapeIdFor(nodeId)
    if (!editor.getShape(id)) { setNotice('✕ no node ' + nodeId + ' on the canvas'); return false }
    editor.select(id); editor.zoomToSelection({ animation: { duration: 450 } })
    setNotice('→ ' + nodeId); return true
  }
  const selectedRef = useRef<NodeShape['props'] | null>(null)

  // B-frontend: start a walk over a set of review item ids (the inbox affordance — the operator-driven
  // entry point for S1). Persists the session id in localStorage (S7c, same-device resume).
  async function startWalk(itemIds: string[]) {
    if (!itemIds.length) { setNotice('no review items to walk'); return }
    if (wtBusyRef.current) return                  // CONCURRENCY GUARD: start framing takes ~20s while session is still null — a 2nd click would start TWO sessions
    wtBusyRef.current = true; setWtBusy(true)
    setNotice('starting walk over ' + itemIds.length + ' item(s)…')
    try {
      const s = await api.reviewStart(itemIds, 'walkthrough')
      if (s?.error) { setNotice('✕ ' + s.error); return }
      try { localStorage.setItem('company-review-session', s.session) } catch { /* */ }
      setSession(s); setWtReason(''); setWtSpoke('')
    } catch (e: any) { setNotice('✕ could not start the walk: ' + (e?.message || e)) }
    finally { wtBusyRef.current = false; setWtBusy(false) }   // re-enable on success OR error
  }
  // refresh the card from the server-authoritative present_current. reflects-never-owns.
  async function refreshSession(sid: string) {
    try {
      const s = await api.reviewCurrent(sid)
      if (s?.error) { setNotice('✕ session: ' + s.error); endWalk(); return }
      setSession(s); setWtReason('')
    } catch { /* bridge transient — the next event re-pulls */ }
  }
  function endWalk() {
    setSession(null); sessionRef.current = null; spokenFor.current = ''
    try { localStorage.removeItem('company-review-session') } catch { /* */ }
  }
  // D-frontend: respond to the current step — operator-only, tagged with the session id + cursor position.
  async function respondStep(choice: string) {
    if (!session?.item) return
    if (wtBusyRef.current) return                  // CONCURRENCY GUARD: a request is already in flight — drop the extra click
    wtBusyRef.current = true; setWtBusy(true)       // ref gates synchronously (pre-render); state disables the controls visibly
    const why = (choice === 'reject' || choice === 'comment') ? wtReason : ''
    setNotice('verdict: ' + choice + ' · ' + session.item)
    try {
      const r = await api.resolveStep(session.item, choice, why, session.session, session.cursor)
      if (r?.error || r?.ok === false) { setNotice('✕ ' + (r.error || 'resolve refused')); return }
      setSession((cur: any) => cur ? { ...cur, _responded: choice } : cur)   // mark the step responded (UI hint)
      await poll()   // refresh the inbox so the resolved item drops out of live_escalations
    } catch (e: any) { setNotice('✕ resolve failed: ' + (e?.message || e)) }
    finally { wtBusyRef.current = false; setWtBusy(false) }   // re-enable on success OR error — never a dead end
  }
  // B-frontend: Next — write the current step's go-gate → the scheduler fires it → the session advances.
  async function nextStep() {
    if (!session?.session) return
    if (wtBusyRef.current) return                  // CONCURRENCY GUARD: framing takes ~20s — a 2nd click would desync the cursor
    wtBusyRef.current = true; setWtBusy(true)
    setNotice('next →')
    try {
      const s = await api.reviewNext(session.session)
      if (s?.error) { setNotice('✕ ' + s.error); return }
      if (s.done) { setSession({ ...session, ...s, done: true, item: null, framing: null }) }
      else { setSession(s); setWtReason('') }
    } catch (e: any) { setNotice('✕ next failed: ' + (e?.message || e)) }
    finally { wtBusyRef.current = false; setWtBusy(false) }   // re-enable on success OR error
  }

  // B+C — the per-step VIEW DRIVE: when the walk lands on a new step, MOVE the view to the thing the item
  // concerns. Deps are the STEP only (not voiceOn) so toggling voice mid-step does NOT re-zoom.
  useEffect(() => {
    if (!session || session.done || !session.item) return
    const tgt = session.raw?.ui_target
    if (tgt) resolveUiTarget(tgt)   // registry-validated; fail-loud if unknown
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session?.session, session?.cursor, session?.item])

  // F — the per-step NARRATION: SPEAK the step's framing, voice-FIRST (gated on the voice|text toggle).
  // Speak ONCE per (session:cursor) step (spokenFor guard); any voice failure falls back to text (F4).
  useEffect(() => {
    if (!session || session.done || !session.item) return
    const stepKey = session.session + ':' + session.cursor
    if (spokenFor.current === stepKey) return
    spokenFor.current = stepKey
    const text = session.framing || (session.raw?.payload?.note) || ('Review item ' + session.item)
    if (voiceOn) {
      setWtSpoke('speaking…')
      speakReply(text)
        .then(() => setWtSpoke('🔊 spoke the framing'))
        .catch(() => setWtSpoke('voice unavailable — read it on screen'))   // F4: never a dead end
    } else setWtSpoke('text mode')
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session?.session, session?.cursor, session?.item, voiceOn])

  // U3: tick an elapsed counter while a run is in flight (not a frozen "running…"). Also toggle a body
  // class so CSS can PULSE the not-yet-resolved node cards.
  useEffect(() => {
    if (runStartedAt == null) { document.body.classList.remove('canvas-running'); return }
    document.body.classList.add('canvas-running')
    const t = setInterval(() => setRunElapsed(Math.floor((Date.now() - runStartedAt) / 1000)), 250)
    return () => { clearInterval(t); document.body.classList.remove('canvas-running') }
  }, [runStartedAt])

  const selected = useValue('sel', () => {
    const s = editor.getOnlySelectedShape()
    return s && s.type === 'node' ? (s as NodeShape).props : null
  }, [editor])

  // U7: selecting a node must surface its inspector even if the operator has scrolled the right rail down.
  useEffect(() => {
    if (!selected) return
    const insp = document.querySelector('[data-ui-ref="inspector"]') as HTMLElement | null
    if (insp) insp.scrollTo ? insp.scrollTo({ top: 0, behavior: 'smooth' }) : (insp.scrollTop = 0)
  }, [selected?.nodeId])
  selectedRef.current = selected

  // L10 · "stale at this address" (§21.7#10). When a node with a STORED output is selected, derive whether
  // its cached result is out of date vs its CURRENT inputs (GET /api/stale-at → Suite.stale_at_address). A
  // COSTED DERIVATION (recompile + input-hash + _memo_sig compare; seams-engine Seam 8a), NOT a served
  // field — so we fetch it ON-DEMAND on selection (the operator focusing the node IS the request), keyed by
  // the node's run:// instance address (NOT ui:// — `cached` is served per run:// node). READ-ONLY: the
  // memo gate is unmutated. Re-poked by events.length so a fresh run/input-change at THIS node re-derives
  // the badge without a re-select. Fail-loud (rule 4): a backend 400 surfaces as unknown+reason, never a
  // silent "fresh"; an unevaluable node (volatile/reference/no-cache) comes back unknown with its reason.
  async function fetchFreshness(addr: string | null, status?: string) {
    // only a node that HOLDS a cached result has a "stale vs inputs" question (cached/ran). idle/stuck/
    // failed/empty have nothing cached to be stale → clear the badge (never a misleading verdict).
    if (!addr || !addr.startsWith('run://') || !(status === 'cached' || status === 'ran')) {
      setFreshness(null); return
    }
    setFreshnessBusy(true)
    try {
      const r = await api.staleAt(addr)
      if (r?.error) { setFreshness({ address: addr, stale: null, unknown: true, reason: r.error }); return }
      setFreshness(r)
    } catch (e: any) {
      setFreshness({ address: addr, stale: null, unknown: true, reason: 'could not derive freshness: ' + (e?.message || e) })
    } finally { setFreshnessBusy(false) }
  }
  // Derive freshness whenever the selected node changes (and re-derive when the live event count moves, so a
  // run or an upstream input-change at THIS node refreshes the badge without a re-select). selected?.address
  // is the run:// instance; selected?.status gates the fetch to nodes that actually hold a cached result.
  useEffect(() => { fetchFreshness(selected?.address || null, selected?.status)
    /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [selected?.address, selected?.status, events.length])

  // L6 · versions at an address (§21.7#6). When a node is selected, load the trail of values its OUTPUT
  // address has held (GET /api/ref-versions → Suite.ref_versions). THE LOAD-BEARING CHOICE: versions accrue
  // where a `set_ref` WROTE. A PORTAL never calls set_ref (RESOLVE='reference', the scheduler skips it), so
  // its OWN address has no history — the address that holds the versions is the one its config.ref POINTS
  // AT (carried in the shape prop as `ref`). A compute node's own run:// `address` IS where its versions
  // accrue. So: portal → its `ref`; any other node → its `address`. Re-poked by events.length so a fresh
  // set_ref at this address (a re-run) surfaces the new version without a re-select. Fail-loud (rule 4):
  // a backend 400 (malformed / non-run address) surfaces as a notice, never a silent empty mistaken for
  // "no versions"; an address never written returns versions:[] honestly.
  function versionedAddress(s: typeof selected): string | null {
    if (!s) return null
    if (s.nodeType === 'portal') return (s.ref && s.ref.startsWith('run://')) ? s.ref : null   // the address it WINDOWS onto
    return (s.address && s.address.startsWith('run://')) ? s.address : null                      // its own output
  }
  async function fetchVersions(addr: string | null) {
    if (!addr) { setVersions(null); return }
    setVersionsBusy(true)
    try {
      const r = await api.refVersions(addr)
      if (r?.error) { setVersions(null); setNotice('⚠ could not load versions: ' + r.error); return }
      setVersions(r)
    } catch (e: any) {
      setVersions(null); setNotice('⚠ could not load versions: ' + (e?.message || e))
    } finally { setVersionsBusy(false) }
  }
  useEffect(() => { fetchVersions(versionedAddress(selected))
    /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [selected?.address, selected?.nodeType, selected?.ref, events.length])

  // D4: run the graph; `force` (a node-id list) bypasses the memo gate for just those nodes. U1: the
  // arrow-wrapped call sites pass `() => doRun()` so React's MouseEvent is NEVER passed as `force`.
  async function doRun(force?: string[]) {
    setRunning(true); setRunError(null)
    setRunStartedAt(Date.now()); setRunElapsed(0)   // U3: start the elapsed clock for the in-flight run
    setGrowMsg(force ? `force re-running ${force.join(', ')} (past the memo cache)…`
                     : 'resolving… presence of data at each address fires the next node')
    try {
      const st = await api.run(force); await refresh(editor, st)
      const ran = (st.nodes || []).filter((n: any) => n.status === 'ran').length
      const cached = (st.nodes || []).filter((n: any) => n.status === 'cached').length
      // U2: the run RESULT (state) carries only ran|cached|idle — the STUCK list lives on the emitted `run`
      // event. Pull the freshest events, read the latest run event's stuck array, then re-apply the paint.
      try { const evs = await api.events(); applyStuckFromEvents(evs) } catch { /* the SSE run event also carries it */ }
      const stuckN = stuckNodes.current.size
      setGrowMsg(`run complete · ${ran} ran · ${cached} cached` + (stuckN ? ` · ${stuckN} stuck` : '') + '.')
      await poll(); await maybeReact()
    }
    catch (e: any) {
      // U4 (fail loud, no dead end): a REAL rejection — network down, or a node that RAISED and failed the
      // whole run. Surface it legibly with a retry; never an uncaught promise rejection, never a silent swallow.
      const msg = e?.message || String(e)
      setRunError(msg); setGrowMsg('✕ run failed — ' + msg); setNotice('✕ run failed: ' + msg)
    }
    finally { setRunning(false); setRunStartedAt(null) }   // ALWAYS clears running — the latch can never persist (U1)
  }
  // U2: read the latest `run` event's stuck/ran arrays and update stuckNodes, then repaint the shapes.
  function applyStuckFromEvents(evs: any[]) {
    const runEv = (evs || []).filter((e: any) => e && e.kind === 'run').sort((a, b) => (b.seq ?? 0) - (a.seq ?? 0))[0]
    if (!runEv) return
    const stuck: string[] = Array.isArray(runEv.stuck) ? runEv.stuck : []
    const ran: string[] = Array.isArray(runEv.ran) ? runEv.ran : []
    const next = new Set(stuck)
    ran.forEach(id => next.delete(id))   // anything that ran this pass is, by definition, no longer stuck
    stuckNodes.current = next
    paintStuck()
  }
  // U2: write the stuck status onto the tldraw shapes (a client-only overlay status; the backend status
  // stays ran|cached|idle — reflects-never-owns). Re-applied after every loadGraph so a refresh can't erase it.
  function paintStuck() {
    editor.getCurrentPageShapes().forEach(s => {
      if (s.type !== 'node') return
      const nid = (s as NodeShape).props.nodeId
      const isStuck = stuckNodes.current.has(nid)
      const cur = (s as NodeShape).props.status
      if (isStuck && cur !== 'stuck') editor.updateShape<NodeShape>({ id: s.id, type: 'node', props: { status: 'stuck' } })
      else if (!isStuck && cur === 'stuck') editor.updateShape<NodeShape>({ id: s.id, type: 'node', props: { status: 'idle' } })
    })
  }
  async function dispatch() {
    if (!gname || !gspec) { setGrowMsg('enter a name + what it should do.'); return }
    setGrowMsg(`dispatching… the brain is writing the ${gname} node…`); setSurf(null)
    const r = await api.propose(gname, gspec)
    if (r.error) { setGrowMsg(''); setSurf({ error: r.error }) } else setSurf(r)
    await poll()
  }
  // V2.1 — prime/unlock audio. MUST be called from a synchronous user-gesture handler (the mic tap, the
  // send click) BEFORE any await, so iOS unlocks the context for the later (post-async) reply playback.
  // Idempotent: resume() is safe to call repeatedly. On a fresh turn it also resets the play cursor.
  function primeAudio() {
    try {
      if (!audioCtxRef.current) {
        const Ctx = (window.AudioContext || (window as any).webkitAudioContext)
        if (Ctx) audioCtxRef.current = new Ctx()
      }
      audioCtxRef.current?.resume?.()
    } catch { /* no Web Audio → speakReply falls back to <audio> below */ }
  }
  // Play one wav (an ArrayBuffer) through the unlocked context, SCHEDULED after anything already queued
  // (so streamed sentence-chunks play in order — V2.2). Fail-loud-ish: if the context is blocked/absent,
  // fall back to a plain <audio> element (works on desktop; on iOS the gesture-primed context is the path).
  async function playWavBuffer(buf: ArrayBuffer) {
    const ctx = audioCtxRef.current
    if (ctx && ctx.state === 'running') {
      const audioBuf = await ctx.decodeAudioData(buf.slice(0))
      const src = ctx.createBufferSource(); src.buffer = audioBuf; src.connect(ctx.destination)
      const now = ctx.currentTime
      const at = Math.max(now, playCursorRef.current || now)
      src.start(at); playCursorRef.current = at + audioBuf.duration
      return
    }
    // fallback (desktop / context not unlocked): a one-shot element
    await new Audio(URL.createObjectURL(new Blob([buf], { type: 'audio/wav' }))).play()
  }
  // voice out — speak text in the configured persona voice (the bridge routes /api/tts to it). Plays through
  // the gesture-unlocked Web Audio context (V2.1) so it actually sounds on iOS. Throws on a hard failure so
  // callers that need a fallback (the walk, F4) can catch and degrade to text. PRESERVE-LIST: push-to-talk.
  async function speakReply(text: string) {
    playCursorRef.current = 0                                   // a whole-reply utterance starts a fresh queue
    const blob = await api.tts(text)
    await playWavBuffer(await blob.arrayBuffer())
  }
  function b64ToArrayBuffer(b64: string): ArrayBuffer {
    const bin = atob(b64 || ''); const bytes = new Uint8Array(bin.length)
    for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i)
    return bytes.buffer
  }
  // V2.2 — a voice turn through the designed STREAMING circuit (/api/voice/stream): post the recorded
  // utterance, consume the ndjson (transcript → reply → per-SENTENCE {wav_b64} chunks → done), append the
  // turns to the chat, and play each sentence in the PERSONA's voice through the gesture-unlocked context
  // (V2.1) AS IT ARRIVES — first audio at ~(STT+brain+one sentence), not after the whole reply. Fail-LOUD
  // on a stream/engine error (never a silent swallow). No persona set → the simple stt→chat path (which
  // still speaks via /api/tts's persona-default). The walk-verdict path stays on plain STT (caller-gated).
  async function runVoiceTurn(blob: Blob) {
    const persona = (cfg?.persona || '').trim()
    if (!persona) {                                            // no persona → simple path (text + tts persona-default)
      setNotice('transcribing…')
      const r = await api.stt(blob)
      if (r.text) { setNotice('you said: ' + r.text); await sendChat(r.text) } else setNotice('(no speech detected)')
      return
    }
    playCursorRef.current = 0
    setNotice('listening…')
    let res: Response
    try { res = await api.voiceStream(blob, persona, recordingSession || undefined) }   // V3.1: record if a session is active
    catch (e: any) { setNotice('⚠ voice circuit unreachable: ' + (e?.message || e)); return }
    if (!res.ok || !res.body) {
      const t = await res.text().catch(() => ''); setNotice('⚠ voice turn failed (' + res.status + '): ' + t.slice(0, 160)); return
    }
    const reader = res.body.getReader(); const dec = new TextDecoder(); let buf = ''
    for (;;) {
      const { done, value } = await reader.read(); if (done) break
      buf += dec.decode(value, { stream: true })
      const lines = buf.split('\n'); buf = lines.pop() || ''
      for (const ln of lines) {
        const s = ln.trim(); if (!s) continue
        let ev: any; try { ev = JSON.parse(s) } catch { continue }
        if (ev.type === 'transcript') { setNotice('you said: ' + ev.text); if (ev.text) setChat(c => [...c, { role: 'user', text: ev.text }]) }
        else if (ev.type === 'reply') { if (ev.text) setChat(c => [...c, { role: 'assistant', text: ev.text }]) }
        else if (ev.type === 'chunk') { try { await playWavBuffer(b64ToArrayBuffer(ev.wav_b64)) } catch { /* keep streaming the rest */ } }
        else if (ev.type === 'error') { setNotice('⚠ ' + ev.error) }                 // fail loud (V2.3)
        else if (ev.type === 'done') { setNotice(''); poll() }
      }
    }
  }
  // voice in — push-to-talk: record → STT → send as a chat turn (which then speaks its reply)
  async function recordToggle() {
    primeAudio()                                               // V2.1: unlock audio in THIS gesture for the later reply
    if (recording) { recorderRef.current?.stop(); return }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const rec = new MediaRecorder(stream)
      const chunks: BlobPart[] = []
      rec.ondataavailable = e => chunks.push(e.data)
      rec.onstop = async () => {
        stream.getTracks().forEach(t => t.stop()); setRecording(false)
        const blob = new Blob(chunks, { type: 'audio/webm' })
        // F2: when a walk is active, the mic routes to the session RESPOND path (transcript-only verdict —
        // no spoken reply). A keyword map turns speech into a verdict; anything else is a comment carrying
        // the transcript as the WHY (never a dead end — F4). This stays on plain STT.
        if (sessionRef.current && !sessionRef.current.done) {
          setNotice('transcribing…')
          try {
            const r = await api.stt(blob)
            if (r.text) {
              setNotice('you said: ' + r.text)
              const t = r.text.toLowerCase()
              const choice = /\bapprove|accept|yes|approved\b/.test(t) ? 'approve'
                : /\breject|decline|no\b/.test(t) ? 'reject'
                : /\bskip|pass|later\b/.test(t) ? 'skip'
                : /\bdecide|you decide|defer to you\b/.test(t) ? 'decide'
                : 'comment'
              if (choice === 'reject' || choice === 'comment') setWtReason(r.text)   // capture the spoken WHY
              setWtSpoke('🎙 heard: "' + r.text + '" → ' + choice)
              await respondStep(choice)
            } else setNotice('(no speech detected)')
          } catch (e: any) { setNotice('STT error — type instead: ' + (e?.message || e)) }   // F4: fall back to text
          return
        }
        // Outside a walk → a CONVERSATION turn through the streaming voice circuit (V2.2): transcript +
        // reply + the persona's voice, sentence-streamed. Fail-loud inside runVoiceTurn.
        try { await runVoiceTurn(blob) } catch (e: any) { setNotice('voice turn error — type instead: ' + (e?.message || e)) }
      }
      recorderRef.current = rec; rec.start(); setRecording(true); setNotice('listening… (click again to stop)')
    } catch { setNotice('mic unavailable — grant microphone permission') }
  }
  // V1.1 — AUTO-LISTEN (hands-free, "reply on a finished thought, not a silence timer"). One continuous
  // recorder; a Web Audio analyser watches RMS for a speech→silence PAUSE; on a pause the utterance-so-far
  // is transcribed + put to the finished-thought JUDGE — if finished, the turn fires (streamed persona
  // voice via runVoiceTurn) and the buffer resets; if not, it keeps listening (don't cut him off). The
  // recorder is PAUSED during the reply so viv's voice isn't captured as new input (echo). Tap again to stop.
  // The real feel (does it wait for a finished thought) is needs-tim — no mic on the server.
  function stopAutoListen() {
    autoListenRef.current.stop = true
    autoListenRef.current.stream?.getTracks().forEach(t => t.stop())
    setRecording(false); setNotice('')
  }
  async function startAutoListen() {
    primeAudio()                                               // unlock audio in this gesture (V2.1)
    let stream: MediaStream
    try { stream = await navigator.mediaDevices.getUserMedia({ audio: true }) }
    catch { setNotice('mic unavailable — grant microphone permission'); return }
    autoListenRef.current = { stop: false, stream }
    setRecording(true); setNotice('listening… (tap to stop)')
    const ctx = audioCtxRef.current || new (window.AudioContext || (window as any).webkitAudioContext)()
    audioCtxRef.current = ctx
    const analyser = ctx.createAnalyser(); analyser.fftSize = 512
    ctx.createMediaStreamSource(stream).connect(analyser)
    const data = new Uint8Array(analyser.fftSize)
    let chunks: BlobPart[] = []
    const rec = new MediaRecorder(stream)
    rec.ondataavailable = e => { if (e.data && e.data.size) chunks.push(e.data) }
    rec.start(250)                                             // periodic chunks so the buffer is fresh on a pause
    const SILENCE_MS = 800, SPEECH_RMS = 0.015
    let spoke = false, lastVoice = performance.now(), busy = false
    const tick = async () => {
      if (autoListenRef.current.stop) { try { rec.state !== 'inactive' && rec.stop() } catch {} ; stream.getTracks().forEach(t => t.stop()); setRecording(false); setNotice(''); return }
      if (!busy && rec.state === 'recording') {
        analyser.getByteTimeDomainData(data)
        let sum = 0; for (let i = 0; i < data.length; i++) { const v = (data[i] - 128) / 128; sum += v * v }
        const rms = Math.sqrt(sum / data.length); const now = performance.now()
        if (rms > SPEECH_RMS) { spoke = true; lastVoice = now }
        if (spoke && (now - lastVoice) > SILENCE_MS && chunks.length) {
          busy = true
          const blob = new Blob(chunks, { type: 'audio/webm' })
          try {
            const r = await api.stt(blob); const text = (r.text || '').trim()
            if (text) {
              const j = await api.finishedThought(text)
              if (j && j.finished) {
                try { rec.pause() } catch {}                   // pause capture so the reply isn't heard as input
                setNotice('you said: ' + text); setRecording(false)
                await runVoiceTurn(blob)                       // streamed persona-voice reply (V2.2)
                chunks = []; spoke = false; lastVoice = performance.now()
                if (!autoListenRef.current.stop) { try { rec.resume() } catch {} ; setRecording(true); setNotice('listening… (tap to stop)') }
              } else { setNotice('… go on'); lastVoice = performance.now() }  // not finished — keep him talking
            }
          } catch (e: any) { setNotice('⚠ ' + (e?.message || e) + ' — tap to use push-to-talk') }  // fail loud → ptt fallback
          busy = false
        }
      }
      setTimeout(tick, 150)
    }
    tick()
  }
  // The mic press routes by the configured input mode (V1.3). Push-to-talk → recordToggle (tap/tap).
  // Auto-listen → start a hands-free session, or stop it if one is live. Both unlock audio in the gesture.
  // V1.3 — switch the voice INPUT mode (push_to_talk ↔ auto_listen); persists via the config slot.
  async function setVoiceInputMode(mode: string) {
    if (autoListenRef.current.stream && !autoListenRef.current.stop) stopAutoListen()   // end a live session on switch
    try { const c = await api.setRhmConfig({ voice_input_mode: mode }); setCfg(c); setNotice('voice input → ' + mode.replace('_', '-')) }
    catch (e: any) { setNotice('⚠ ' + (e?.message || e)) }
  }
  // V3.1 — record this conversation as a TRIAL SESSION (so it can be debriefed + feeds the twin). Start
  // mints a trial_session id (the voice stream then records each turn via trial_record_turn); stop clears
  // it. The id format mirrors the backend's namespaced trial sessions.
  function toggleRecordConversation() {
    if (recordingSession) { setRecordingSession(''); setNotice('recording stopped') }
    else {
      const persona = (cfg?.persona || 'rhm')
      const id = 'trial-' + persona + '-' + Math.floor(Date.now() / 1000)
      setRecordingSession(id); setNotice('● recording this conversation — speak; turns are saved for debrief')
    }
  }
  // V3.2 — debrief: walk back through the recorded session(s) via the EXISTING walkthrough organ
  // (start_debrief surfaces each session's real transcript as review items through the same walk).
  async function startDebriefSession() {
    try {
      const sessions = await api.trialSessions()
      const ids = (Array.isArray(sessions) ? sessions : []).map((s: any) => s.session_id || s.id || s).filter(Boolean)
      if (!ids.length) { setNotice('no recorded sessions yet — record a conversation first'); return }
      const r = await api.startDebrief(ids)
      if (r && r.error) { setNotice('⚠ debrief: ' + r.error); return }
      setNotice('debrief started — review the surfaced sessions in the inbox / walk'); await poll()
    } catch (e: any) { setNotice('⚠ debrief failed: ' + (e?.message || e)) }
  }
  // V4.3 — global voice OUTPUT on/off (the voice_enabled slot), independent of presence mode. off = text
  // replies, no synth. Persists live.
  async function setVoiceEnabled(on: boolean) {
    try { const c = await api.setRhmConfig({ voice_enabled: on ? 'on' : 'off' }); setCfg(c); setNotice('voice output ' + (on ? 'on' : 'off')) }
    catch (e: any) { setNotice('⚠ ' + (e?.message || e)) }
  }
  function micPressed() {
    const mode = (cfg?.voice_input_mode || 'push_to_talk')
    if (mode === 'auto_listen') {
      if (autoListenRef.current.stream && !autoListenRef.current.stop) stopAutoListen()
      else startAutoListen()
    } else {
      recordToggle()
    }
  }
  // L9 · reverse journey-recording — the explicit start/stop control. OFF → start_journey (open a record;
  // subsequent indicated ui:// addresses append as steps via `indicate`). ON → stop_journey (finalize →
  // the record becomes replayable). Distinct from the voice `recordToggle` above (the mic) — this records
  // a NAVIGATION path, not audio. Keeps the ref in sync synchronously (the capture path reads the ref).
  async function toggleJourneyRecording() {
    if (journeyIdRef.current) {
      const jid = journeyIdRef.current
      journeyIdRef.current = null; setJourneyId(null)        // stop capturing immediately (ref first)
      try {
        const r = await api.journeyStop(jid)
        if (r?.error) { setNotice('✕ stop journey: ' + r.error); return }
        const n = Array.isArray(r?.steps) ? r.steps.length : 0
        setNotice('■ journey recorded — ' + n + ' step(s). replayable.')
      } catch (e: any) { setNotice('✕ could not stop journey: ' + (e?.message || e)) }
      return
    }
    try {
      const r = await api.journeyStart()
      if (r?.error) { setNotice('✕ start journey: ' + r.error); return }
      journeyIdRef.current = r.id; setJourneyId(r.id)
      setNotice('● recording journey — click a path of elements, then stop to finalize')
    } catch (e: any) { setNotice('✕ could not start journey: ' + (e?.message || e)) }
  }
  // L9 · the REPLAY — fetch a recorded journey's ordered ui:// addresses and step the view through them
  // via the PRESERVED resolveUiTarget (the reverse of present_current's per-step drive; REUSE, not a
  // second navigation mechanism). A short pause between steps so each spotlight is seen (the resolver's
  // ring is ~2.4s; we pace at ~1.1s so the walkthrough reads as a guided tour). Fail-loud on a backend
  // 400 or an unresolvable step (resolveUiTarget already surfaces its own "not in the DOM" notice).
  async function replayJourney(jid: string) {
    if (!jid || journeyReplaying) return
    setJourneyReplaying(true); setNotice('▶ replaying journey ' + jid + '…')
    try {
      const r = await api.journeyReplay(jid)
      if (r?.error) { setNotice('✕ replay: ' + r.error); return }
      const addresses: string[] = Array.isArray(r?.addresses) ? r.addresses : []
      if (!addresses.length) { setNotice('journey ' + jid + ' has no steps to replay'); return }
      for (let i = 0; i < addresses.length; i++) {
        setNotice('▶ journey step ' + (i + 1) + '/' + addresses.length + ': ' + addresses[i])
        resolveUiTarget(addresses[i])                        // THE PRESERVED FORWARD RESOLVER — drives the view to the address
        await new Promise(res => setTimeout(res, 1100))      // pace so each spotlight is seen (guided tour)
      }
      setNotice('✓ journey ' + jid + ' replayed — ' + addresses.length + ' step(s)')
    } catch (e: any) { setNotice('✕ could not replay journey: ' + (e?.message || e)) }
    finally { setJourneyReplaying(false) }
  }
  function fieldValue(f: any) {
    if (f.target === 'mode') return now?.mode || 'listening'
    if (f.target === 'model') return cfg?.model || ''
    if (f.target === 'persona') return cfg?.persona || ''
    return ''
  }
  async function setField(f: any, v: string) {
    if (f.target === 'mode') await changeMode(v)
    else { const c = await api.setRhmConfig({ [f.target]: v }); setCfg(c); setNotice(f.target + ' → ' + v) }
  }
  async function revertLast() {
    if (!lastChange?.sha) return
    setGrowMsg('rolling back the last self-change…')
    const r = await api.revert(lastChange.sha)
    setTypes(await api.types()); await reload()
    setGrowMsg('↩ reverted — the change is undone (git ' + (r.head || '').slice(0, 8) + '). bounded, recoverable.')
  }
  async function approveApply() {
    await api.resolve(surf.id, 'approve')
    const r = await api.apply(surf.id)
    if (r.error) { setSurf({ ...surf, error: r.error }) }
    else { setSurf(null); setGrowMsg(`✓ approved + applied → ${surf.name} is now a live node-type.`); setTypes(r.types); await poll() }
  }

  return {
    // state values (read by the region components)
    edges, running, runError, runStartedAt, runElapsed, types, gname, gspec, surf, growMsg, workshop,
    oinfo, nodeStates, modeDesc, notice, gid, layerView, now, events, chat, chatMsg, chatBusy, cfg, cfgOpen, inbox,
    showResolved, drill, reason, lastChange, panels, recording, configTick, session, wtReason, voiceOn, personas, voiceStatus, recordingSession,
    wtSpoke, wtBusy, selected, mobileTab, fleet, indicated, proposal, history, historyBusy,
    selfChanges, selfChangesBusy, freshness, freshnessBusy, versions, versionsBusy, journeyId, journeyReplaying,
    // refs the components read for the inspector form
    configByNode,
    // setters the components call directly
    setGname, setGspec, setSurf, setWorkshop, setNotice, setCfg, setCfgOpen, setChatMsg, setShowResolved,
    setDrill, setReason, setWtReason, setVoiceOn, setRunError, setGrowMsg, setMobileTab,
    // handlers
    poll, openCoa, reload, fitGraph, addNode, wireSelected, doConnect, setNodeConfig, surfaceOutput,
    buildFromOutput, deleteSelected, sendChat, changeMode, applyCfg, cycleLayers, portalSelected,
    resolveUiTarget, startWalk, endWalk, respondStep, nextStep, dispatch, recordToggle, micPressed, setVoiceInputMode, setVoiceEnabled, toggleRecordConversation, startDebriefSession, fieldValue,
    setField, revertLast, revertSelfChangeAt, approveApply, doRun, refreshFleet, indicate, clickMode, annotateLocus,
    approveProposal, dismissProposal, toggleJourneyRecording, replayJourney, switchPersona,
  }
}

export type AppController = ReturnType<typeof useAppController>
