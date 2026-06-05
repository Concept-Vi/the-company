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
  const [cfg, setCfg] = useState<any>({ model: '', persona: '' })
  const [cfgOpen, setCfgOpen] = useState(false)
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
    try { setNow(await api.now()); mergeEvents(setEvents, await api.events()); setInbox(await api.inbox()); setLastChange(await api.lastChange()); setPanels(await api.panels()) } catch { /* bridge transient */ }
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
    ;(async () => {
      // B2: live model lists FIRST (the source of truth) so config_schema dropdowns resolve immediately.
      let modelOptions: Record<string, string[]> = {}
      try { modelOptions = { chat_models: await api.models('chat'), embed_models: await api.models('embed') } } catch { /* */ }
      const oi = await api.objectInfo()
      let ui: Record<string, any> = {}
      try { ui = await api.uiInfo() } catch { /* the registry is the source of truth for ui:// targets */ }
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
      } catch { /* */ }
      const g = await loadGraph(editor); setEdges(g.edges || []); setGid(g.id); syncConfig(g)
      if ((g.nodes || []).length) setTimeout(fitGraph, 120)   // U6: chrome-aware fit on first load
      setTypes(await api.types())
      // F5: chatHistory now resolves to `{error}` on a non-ok GET — never feed a non-array into `chat`
      // (RhmChat reads `chat.length`/`chat.map`). Defensive guard; the array path is unchanged.
      { const h = await api.chatHistory(); if (Array.isArray(h)) setChat(h) }
      setCfg(await api.rhmConfig())
      const evs = await api.events(); mergeEvents(setEvents, evs)
      streamSeq.current = evs.reduce((m: number, e: any) => Math.max(m, e.seq ?? -1), -1)  // cursor = last seen
      setNow(await api.now()); setInbox(await api.inbox()); setLastChange(await api.lastChange()); setPanels(await api.panels())
      // S7c (same-device resume): a persisted session id rehydrates the walk at the SAME cursor on reload.
      try {
        const sid = localStorage.getItem('company-review-session')
        if (sid) {
          const s = await api.reviewCurrent(sid)
          if (s && !s.error) setSession(s)
          else localStorage.removeItem('company-review-session')   // stale/closed — don't resurface a dead walk
        }
      } catch { /* */ }
      openStream()                                        // G2: replaces setInterval(poll, 2500)
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
        try { setNow(await api.now()) } catch { /* */ }
      } else if (k === 'mode' || k === 'config') {
        try { setNow(await api.now()); setCfg(await api.rhmConfig()) } catch { /* */ }
      } else if (k === 'ask' || k === 'reject' || k === 'resolve' || k === 'apply' || k === 'grow' || k === 'revert' || k.startsWith('decision.')) {
        // WIRE-UI: the decision→implementation wire emits `decision.*` events. NONE carry a companion `ask`,
        // so without this branch a surfaced build-intent / dispatch start / `implemented` close would fall
        // into the final `else` (setNow only) and the inbox/build-intent surface would go STALE.
        // startsWith('decision.') so the NEW `decision.surfaced_for_review` kind is handled the moment the
        // backend lane emits it — author-from-registry. Events already auto-merged at the top of onmessage.
        try { setInbox(await api.inbox()); setNow(await api.now()); setLastChange(await api.lastChange()); setPanels(await api.panels()) } catch { /* */ }
      } else if (k === 'chat' || k === 'react') {
        // F5: SSE-driven refresh — guard against a non-array (`{error}`) ever reaching the chat log.
        try { const h = await api.chatHistory(); if (Array.isArray(h)) setChat(h) } catch { /* */ }
      } else if (k === 'review.advance' || k === 'review.start') {
        // B-frontend: the walk advanced server-side. Refresh the card from present_current IF it's OUR
        // session — reflects-never-owns (the backend session is truth).
        if (ev.session && sessionRef.current && ev.session === sessionRef.current.session) {
          await refreshSession(ev.session)
        }
      } else {
        try { setNow(await api.now()) } catch { /* */ }
      }
    }
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
    try { const r = await api.react(); if (r.comment) { const h = await api.chatHistory(); if (Array.isArray(h)) setChat(h) } } catch { /* */ }
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
  async function sendChat(override?: string) {
    const m = (override ?? chatMsg).trim()
    if (!m || chatBusy) return
    setChatMsg(''); setChatBusy(true)
    setChat(c => [...c, { role: 'user', text: m }])
    try {
      // co-presence: the RHM sees what the operator has selected on the canvas right now
      const selected = (editor.getSelectedShapes().filter(s => s.type === 'node') as NodeShape[]).map(s => s.props.nodeId)
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
      // the decision-compiler DOWN: an action the RHM took routes through the gate
      if (r.action?.did === 'run' || r.action?.did === 'build') { await reload() }
      if (r.action?.did === 'show') {           // attention-direction: move the operator's view (THE KEYSTONE)
        const targets: string[] = r.action.targets || []
        const canvasIds = targets.filter(t => !t.startsWith('ui://')).map((nid: string) => shapeIdFor(nid)).filter((id: any) => editor.getShape(id))
        if (canvasIds.length) { editor.select(...canvasIds); editor.zoomToSelection({ animation: { duration: 450 } }) }
        targets.forEach(t => { if (t.startsWith('ui://')) resolveUiTarget(t) })   // chrome/panel/canvas-by-address
      }
      if (r.action?.did === 'propose') {
        const all = await fetch('/api/surfaced').then(x => x.json())
        const d = all.find((x: any) => x.id === r.action.surfaced)
        if (d) setSurf({ id: d.id, name: d.payload.name, code: d.payload.code })   // → operator approves in GROW panel
      }
      if (r.action?.did === 'panel') {            // update the interface through the interface
        const all = await fetch('/api/surfaced').then(x => x.json())
        const d = all.find((x: any) => x.id === r.action.surfaced)
        if (d) setSurf({ id: d.id, name: d.payload.name, code: JSON.stringify(d.payload.panel, null, 2), isPanel: true })
      }
      if (r.action?.did === 'extend') {           // arbitrary code → build-gated on approve
        const all = await fetch('/api/surfaced').then(x => x.json())
        const d = all.find((x: any) => x.id === r.action.surfaced)
        if (d) setSurf({ id: d.id, name: d.payload.name, code: d.payload.code, isExt: true })
      }
    }
    catch { setChat(c => [...c, { role: 'assistant', text: '(could not reach the brain)' }]) }
    finally { setChatBusy(false) }
  }
  async function changeMode(mm: string) { setNotice('presence → ' + mm); await api.setMode(mm); await poll() }
  async function applyCfg() {
    const c = await api.setRhmConfig({ model: cfg.model, persona: cfg.persona })
    setCfg(c); setCfgOpen(false); setNotice('RHM config → ' + (c.model || 'default')); await poll()
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
    const mm = target.match(/^ui:\/\/([^/]+)\/(.+)$/)
    if (!mm) { setNotice('✕ malformed ui:// target: ' + target); return false }
    const kind = mm[1], ref = mm[2]
    if (kind === 'canvas') {
      if (ref === '*') { editor.zoomToFit({ animation: { duration: 450 } }); setNotice('→ canvas'); return true }
      return driveCanvas(ref)
    }
    // chrome | field | panel | ext → a DOM target. Validate against the registry (fail loud if unknown).
    const UI_INFO = getUI_INFO()
    if (UI_INFO[ref] == null && Object.keys(UI_INFO).length) {
      setNotice('✕ no registered UI target for ' + ref + ' (registry is truth)'); return false
    }
    // openable (e.g. workshop) must be OPEN before we can scroll to it — honor the capability from the registry.
    if (UI_INFO[ref]?.capabilities?.openable && ref === 'workshop' && !workshop && selectedRef.current) {
      setWorkshop(selectedRef.current)   // open the workshop onto the current selection so the target exists in the DOM
    }
    // defer one frame so a just-opened region is mounted before we query for it (fail loud if still absent).
    setTimeout(() => {
      const el = document.querySelector('[data-ui-ref="' + ref + '"]') as HTMLElement | null
      if (!el) { setNotice('✕ UI target not in the DOM right now: ' + ref); return }
      el.scrollIntoView({ block: 'center', behavior: 'smooth' })
      el.classList.add('ui-spotlight')
      setNotice('→ ' + (UI_INFO[ref]?.title || ref))
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
  // voice out — speak text (local Kokoro via the bridge). Throws on failure so callers that need a fallback
  // (the walk, F4) can catch and degrade to text. PRESERVE-LIST: voice push-to-talk.
  async function speakReply(text: string) {
    const blob = await api.tts(text)
    await new Audio(URL.createObjectURL(blob)).play()
  }
  // voice in — push-to-talk: record → STT → send as a chat turn (which then speaks its reply)
  async function recordToggle() {
    if (recording) { recorderRef.current?.stop(); return }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const rec = new MediaRecorder(stream)
      const chunks: BlobPart[] = []
      rec.ondataavailable = e => chunks.push(e.data)
      rec.onstop = async () => {
        stream.getTracks().forEach(t => t.stop()); setRecording(false); setNotice('transcribing…')
        try {
          const r = await api.stt(new Blob(chunks, { type: 'audio/webm' }))
          if (r.text) {
            setNotice('you said: ' + r.text)
            // F2: when a walk is active, the mic routes to the session RESPOND path (not sendChat). A simple
            // keyword map turns speech into a verdict; anything else becomes a comment carrying the
            // transcript as the WHY (never a dead end — F4). Outside a walk, it's a normal chat turn.
            if (sessionRef.current && !sessionRef.current.done) {
              const t = r.text.toLowerCase()
              const choice = /\bapprove|accept|yes|approved\b/.test(t) ? 'approve'
                : /\breject|decline|no\b/.test(t) ? 'reject'
                : /\bskip|pass|later\b/.test(t) ? 'skip'
                : /\bdecide|you decide|defer to you\b/.test(t) ? 'decide'
                : 'comment'
              if (choice === 'reject' || choice === 'comment') setWtReason(r.text)   // capture the spoken WHY
              setWtSpoke('🎙 heard: "' + r.text + '" → ' + choice)
              await respondStep(choice)
            } else await sendChat(r.text)
          }
          else setNotice('(no speech detected)')
        } catch (e: any) { setNotice('STT error — type instead: ' + (e?.message || e)) }   // F4: fall back to text
      }
      recorderRef.current = rec; rec.start(); setRecording(true); setNotice('listening… (click again to stop)')
    } catch { setNotice('mic unavailable — grant microphone permission') }
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
    showResolved, drill, reason, lastChange, panels, recording, configTick, session, wtReason, voiceOn,
    wtSpoke, wtBusy, selected, mobileTab,
    // refs the components read for the inspector form
    configByNode,
    // setters the components call directly
    setGname, setGspec, setSurf, setWorkshop, setNotice, setCfg, setCfgOpen, setChatMsg, setShowResolved,
    setDrill, setReason, setWtReason, setVoiceOn, setRunError, setGrowMsg, setMobileTab,
    // handlers
    poll, openCoa, reload, fitGraph, addNode, wireSelected, doConnect, setNodeConfig, surfaceOutput,
    buildFromOutput, deleteSelected, sendChat, changeMode, applyCfg, cycleLayers, portalSelected,
    resolveUiTarget, startWalk, endWalk, respondStep, nextStep, dispatch, recordToggle, fieldValue,
    setField, revertLast, approveApply, doRun,
  }
}

export type AppController = ReturnType<typeof useAppController>
