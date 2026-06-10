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
  // B1 · text-streaming default-on. The streaming path is a true superset of /api/chat (the done event
  // carries proposal/action/thread/history) so this can default true with the non-stream path intact as a
  // fallback (flip to false to use the whole-reply-wait /api/chat path).
  const [chatStreaming] = useState(true)
  // REVIEW WORKSPACE — the mockup the operator is reviewing (a filename, e.g. "IA-mobile.html"), or null.
  // Held here (NOT via indicate(), which paints a same-document DOM class + clears on an unresolvable
  // address — a mockup lives in an iframe and mockup:// is not a registry address). When set, sendChat
  // ships `mockup://<file>` in focus.selected so the brain reads the mockup as ground truth and explains
  // it at the operator's altitude. A ref mirrors it for sendChat's non-stale read (like indicatedRef).
  const [reviewMockup, setReviewMockupState] = useState<string | null>(null)
  const reviewMockupRef = useRef<string | null>(null)
  // STUDIO · the reviewed-surface ui:// address of the currently-open mockup (from the corpus index's
  // per-item `address`). Held so the Stage/Composer/RhmPanel can show + bind the locus even when the
  // gallery Card's DOM element isn't the click target (e.g. a programmatic open). The LOAD-BEARING locus
  // binding is still `indicate(address)` (below in setReviewMockup) → it sets indicatedRef, which sendChat/
  // annotateLocus/fetchAddressHelp all read. This is just the mirror the studio regions display.
  const [reviewAddress, setReviewAddress] = useState<string | null>(null)
  // GENERATE FOLLOW-ON · the live state for the studio "generate" step. `generateBusy` gates the button
  // (a plan-mode dispatch is a real round-trip — the engine spawns claude -p), and `generateResult` holds
  // the PROPOSED result the engine returns (its summary + changed_files, which are [] in safe plan mode) so
  // the surface can SHOW what it WOULD change. reflects-never-owns: this is a display mirror of the backend's
  // returned proposal, not authoritative state.
  const [generateBusy, setGenerateBusy] = useState(false)
  const [generateResult, setGenerateResult] = useState<any | null>(null)
  // V-B: the POINTED ELEMENT content (text + bounded html + tag) when the operator clicks an UN-registered
  // mockup element. Shipped in focus.pointed_element so the RHM describes the ACTUAL element from the mockup
  // HTML it already holds — instead of resolving a fake ui:// address (the registry-is-truth fix). null when
  // a registered element / the whole mockup is the locus (those resolve via the registry on their own).
  const pointedElementRef = useRef<{ text: string; tag: string; html: string } | null>(null)
  function setReviewMockup(file: string | null, address?: string | null,
                           pointed?: { text: string; tag: string; html: string } | null) {
    reviewMockupRef.current = file
    setReviewMockupState(file)
    // STUDIO locus binding: opening a mockup INDICATES the surface it depicts (its ui:// address), so the
    // RhmPanel's chat, the address-help, and the Composer's annotate all bind to that locus for free — the
    // focus→locus→context-at-address channel (capability-map §0). null address → clear the indication (the
    // mockup has no mapped surface yet — honest, the chat still grounds on mockup:// content). reflects-
    // never-owns: indicate() is the one locus sink; we don't hold a parallel locus.
    const addr = address ?? null
    setReviewAddress(addr)
    if (addr) indicate(addr); else indicate(null)
    pointedElementRef.current = pointed ?? null   // the specific element (if un-registered) the RHM should read
  }
  // STUDIO (G4) · the gallery corpus, bound from /api/corpus (registry-is-truth — the disk listing, never a
  // hardcoded FE list). Each item {file,title,platform,group,address}. fail-loud: a fetch failure carries
  // its error into `corpusErr` so the Rail surfaces it, never a silently empty gallery. reflects-never-owns.
  const [corpus, setCorpus] = useState<{ file: string; title: string; platform: string; group: string; address: string | null }[]>([])
  const [corpusErr, setCorpusErr] = useState<string>('')
  async function refreshCorpus() {
    try {
      const r = await api.corpus()
      if (r && r.error) { setCorpusErr(String(r.error)); return }
      setCorpus(Array.isArray(r?.items) ? r.items : [])
      setCorpusErr('')
    } catch (e: any) { setCorpusErr(e?.message || String(e)) }
  }
  // STUDIO · the comment THREAD at the indicated locus — the read-back half of annotate, from the SHARED
  // address-keyed annotation store (GET /api/annotations?address=), NOT the bespoke mockup-feedback jsonl
  // (retired for the in-app surface). The Composer posts via annotateLocus (POST /api/annotate) and reads
  // back here, proving the persist-to-shared-store. Keyed on `indicated`; re-poked by events.length so a
  // fresh comment at this locus appears live. null = nothing indicated / no thread yet.
  const [annotations, setAnnotations] = useState<{ address: string; thread: any[] } | null>(null)
  const [annotationsBusy, setAnnotationsBusy] = useState(false)
  async function fetchAnnotations(addr: string | null) {
    if (!addr || !addr.startsWith('ui://')) { setAnnotations(null); return }   // only ui:// loci carry a thread
    setAnnotationsBusy(true)
    try {
      const r = await api.annotations(addr)
      if (r?.error) { setAnnotations({ address: addr, thread: [] }); setNotice('✕ ' + r.error); return }   // fail-loud
      // the store returns the thread as a list (oldest-first); tolerate either a bare list or {thread:[…]}.
      const thread = Array.isArray(r) ? r : (Array.isArray(r?.thread) ? r.thread : (Array.isArray(r?.annotations) ? r.annotations : []))
      setAnnotations({ address: addr, thread })
    } catch (e: any) {
      setAnnotations({ address: addr, thread: [] }); setNotice('✕ could not load comments: ' + (e?.message || e))
    } finally { setAnnotationsBusy(false) }
  }
  // I1 · click-to-indicate: the ui:// address of the element the operator has CLICKED to indicate (the
  // locus their next chat turn is about). null = nothing indicated. This is the WIDENED `focus`
  // vocabulary (seams-rhm Seam 4): a ui:// address rides in the SAME `focus.selected` list as canvas
  // node-ids — the backend `_chat_context` branches on the value (ui:// → INDICATING block; node-id →
  // co-presence block). We mirror the address in React (the chip / shipped focus) AND apply a PERSISTENT
  // `.ui-indicated` class on the DOM element (the visible selection — FORM), distinct from F4's TRANSIENT
  // `.ui-spotlight` ring (which the show-resolver flashes and removes after a timeout).
  const [indicated, setIndicated] = useState<string | null>(null)
  const indicatedRef = useRef<string | null>(null)   // for the capture handler (avoids a stale closure)
  // I1-gate / L4-COHERENCE (Tim 2026-06-07, unify-wave2): click-to-indicate is the DEFAULT (ON), with the
  // `◎ point` toolbar toggle as an explicit OPT-OUT for pure navigation. WHY ON by default: the branch's
  // verified-by-use flows — show-me (C1/C2), address-help (D2), altitude (F1) — ALL assume that clicking a UI
  // element INDICATES it (so the help panel / show-me / shaping target the clicked element). With indicate
  // defaulting OFF (the merge carried main's a89dab1 over-broad gate), a click indicated nothing and those
  // flows silently broke. Main's REAL a89dab1 fix was the MODAL EXCLUSION in onDocClick (don't indicate inside
  // a modal — which fixed the Settings ✕-close + translucency bug); the global default-OFF gate was an
  // over-broad way to get there. So: indicate ON by default (C/D/F work out of the box), the modal-exclusion
  // guards in onDocClick KEPT (main's fix holds — a click inside the A3 Settings / Workshop modal does NOT
  // indicate, the ✕ closes, no translucency), and the toggle still lets the operator switch indicate OFF.
  // BOTH the state (drives the toolbar button visual) and the ref (drives the onDocClick behavior — the gate
  // reads indicateModeRef.current, and the ref is NEVER synced from state, only flipped in toggleIndicateMode)
  // must start true, or the gate would early-return until the toggle was pressed (the silent break, build-clean).
  const [indicateMode, setIndicateMode] = useState(true)
  const indicateModeRef = useRef(true)
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
  // B1 · OFFER-WITH-OPTIONS shape (mirrors the backend suite.py:3313-3317 `proposal`): the top-level
  // {verb,address,args} is the PRIMARY offer; `options[]` are the one-click choices the operator picks
  // among (v1 carries exactly one — the surface maps over it generically so it's ready when the backend
  // emits several); `direction:true` means the offer accepts a steer (the operator types a refinement →
  // it loops back to the RHM to re-offer). Each option carries a `label` (the human one-liner shown on
  // its button). Extended from the binary {verb,address,args} card → the rich consent surface.
  // B2 · an option carries a `summary` (the DISTINGUISHING line the operator reads to choose between
  // alternatives — for build/panel/extend the verb+address are often identical across options, so the
  // summary IS the differentiator the comparison surface renders as the primary content).
  type ProposalOption = { verb: string; address?: string | null; args?: any; label?: string; summary?: string | null }
  // B2 · `interactive` (from the backend, derived from the verb class build/panel/extend — registry-truth):
  // when true the ProposeAffordance region renders the ON-SCREEN COMPARISON surface (select-then-approve +
  // chat-until-approve), NOT B1's click-to-act list. Single-option / non-consequential offers stay B1.
  // B3 · `_sid` — when an offer is REVIVED from the inbox (a deferred_offer surfaced item), the proposal
  // carries the surfaced id so the round-trip closes: on approve/dismiss the revived item is RESOLVED out
  // of `live_escalations` (it doesn't linger as a ghost after it's been acted). A fresh (non-revived) offer
  // has no _sid. Reflects-never-owns: only the operator's approve/dismiss resolves it.
  const [proposal, setProposal] = useState<
    { verb: string; address?: string | null; args?: any; options?: ProposalOption[]; direction?: boolean; interactive?: boolean; _sid?: string } | null
  >(null)
  // D2 · the COMPOSED address-help bundle for the indicated ui:// element — the operator-facing help/altitude
  // surface (REPO-KNOWLEDGE D2). The three legs (what_this_is · how_to_use · how_to_change) of "what can I do
  // here?" joined by the EXISTING D1 composer Suite.address_help (exposed via GET /api/address-help — NOT a
  // parallel FE composer). Loaded by fetchAddressHelp whenever the operator indicates an element (keyed on
  // `indicated` ONLY — the help text is STATIC per address, so unlike History/SelfChanges it does NOT re-poll
  // on events.length). Rendered AT TIM'S ALTITUDE by the AddressHelp region: plain-language what/how-to-use
  // lead; the mechanism (code scope, file paths, blast-radius reach) drills down on demand. `legs_present`
  // drives the per-leg DEGRADE (G-53: many elements author no howto yet → an honest "no how-to authored yet",
  // never a blank). null = nothing indicated / not yet loaded. `addressHelpError` carries a fail-loud message
  // (malformed address → backend 400) so the panel says so, never a silent blank.
  // F1 ALTITUDE: the bundle ALSO carries the LEARNED presentation pref (the adapt step attaches it backend-
  // side — _apply_presentation_pref, committed e1700b4): `presentation_pref` {kind, arg?} = the structured
  // learned shaping at this locus (null when none — the clean default), `presentation_directive` = its human
  // form. The AddressHelp panel renders these as a 'learned: …' marker + a model-free structural adapt
  // (lead_with:change auto-hoists the how-to-change drill-down). These MUST be threaded through (the prior
  // fixed mapping dropped them) or the marker never appears.
  const [addressHelp, setAddressHelp] = useState<{
    address: string; what_this_is: string; how_to_use: string | null;
    how_to_change: { scope: string[]; blast_radius: any; note: string | null };
    legs_present: { what_this_is: boolean; how_to_change: boolean; how_to_use: boolean };
    presentation_pref: { kind: string; arg?: string } | null;
    presentation_directive: string | null;
  } | null>(null)
  // F1: a transient busy flag for the feedback affordance (so the chips disable + show 'shaping…' while the
  // pref POSTs + the bundle re-fetches — the affordance is fail-loud + never double-fires).
  const [prefBusy, setPrefBusy] = useState(false)
  const [addressHelpBusy, setAddressHelpBusy] = useState(false)
  const [addressHelpError, setAddressHelpError] = useState<string | null>(null)
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
  // L4-GEAR-RETIRE: `cfgOpen`/`applyCfg` (the legacy RhmChat .rhm-cfg gear's open-state + apply) are GONE —
  // the gear is retired (its config duplicated A3). The consolidated A3 Settings (settingsOpen below) is the
  // single config home; it writes via setCfgSlot → set_rhm_config. No parallel config surface remains (rule 3).
  const [personas, setPersonas] = useState<any[]>([])   // Option A: the cast you can switch between (id·name·engine)
  // A3/E2-FE · THE CONSOLIDATED SETTINGS SURFACE state. `settingsOpen` raises the one designed Settings region
  // (the full-viewport modal mounted in App.tsx) — the single place modes/models/personas/RHM-config/voice all
  // live together (A3 "consolidated, not scattered"). It is INDEPENDENT of `cfgOpen` (the legacy RhmChat gear,
  // a forbidden-file we leave working): both read the SAME cfg/personas/etc. controller state — single source,
  // no parallel config system (rule 3). The extra read-only registries the Settings surface renders are loaded
  // ON OPEN (loadSettingsData) so a closed surface costs nothing: `roles` (the model-FUNCTION role registry,
  // GET /api/roles) · `voicePaths` (the pipeline/s2s registry, GET /api/voice/paths — s2s renders UNAVAILABLE,
  // never as working, G-19) · `voiceStatus` (per-engine TTS + STT availability, GET /api/voice) · `modeRegistry`
  // (E1 — the hierarchical mode type-registry: ≤8 modes × subtypes × per-mode context-resolution declarations,
  // from capabilities().mode_registry) · `autodetect` (E2 — the off/suggest/auto toggle's LIVE value + options,
  // from capabilities().composition_config; READ-ONLY here — there is no runtime setter, surfaced honestly as
  // env-set, never a silent no-op control). reflects-never-owns: every one is READ truth off the registry.
  const [settingsOpen, setSettingsOpen] = useState(false)
  const settingsOpenRef = useRef(false)   // openStream's closure is stale → the ref lets the SSE branch see live open-state
  settingsOpenRef.current = settingsOpen
  const [settingsTab, setSettingsTab] = useState<'brain' | 'modes' | 'voice' | 'roles' | 'composition' | 'cognition'>('brain')
  const [roles, setRoles] = useState<Record<string, any> | null>(null)
  const [voicePaths, setVoicePaths] = useState<any | null>(null)
  const [voiceStatus, setVoiceStatus] = useState<any | null>(null)
  const [modeRegistry, setModeRegistry] = useState<Record<string, any> | null>(null)
  const [autodetect, setAutodetect] = useState<{ value: string; options: string[] } | null>(null)
  const [compositionCfg, setCompositionCfg] = useState<Record<string, any> | null>(null)
  const [settingsBusy, setSettingsBusy] = useState(false)
  const [settingsErr, setSettingsErr] = useState<string | null>(null)
  // ---- main's voice/settings state, folded in (S1/S2/S3/S5/S6/V3/V4) ----
  // NB: main also declared `voiceStatus` (a string load-state) and `settingsOpen`. The branch already owns
  // both names above: `voiceStatus` is the A3 per-engine availability OBJECT, and `settingsOpen` raises the
  // consolidated A3 modal (the same toggle main's S3 opened). So main's `settingsOpen` dup is dropped
  // (converged to the one above) and main's string load-state is renamed `personaVoiceStatus` (§3e #2).
  const [personaVoiceStatus, setPersonaVoiceStatus] = useState<string>('')   // V4.2 (was voiceStatus): '' | 'loading' | 'ready' | 'down' — the persona voice's load state
  const [recordingSession, setRecordingSession] = useState<string>('')   // V3.1: the active trial_session id when recording the conversation ('' = not recording)
  const [chatModelsX, setChatModelsX] = useState<any[]>([])   // S1: detailed chat-model picker rows (ollama + local vLLM, base_url·service·up)
  const [engineKnobs, setEngineKnobs] = useState<any>({})   // S5: per-TTS-engine knob catalog
  const [voiceInfo, setVoiceInfo] = useState<any>({})   // S5: /api/voice — stt_registry (ears) + engines (TTS up-status)
  const [fitReport, setFitReport] = useState<any>(null)   // S6: "will my selection fit the card?" (brain+voice budgets vs ceiling)
  const [threads, setThreads] = useState<any[]>([])   // S2: previous conversations (reopen list)
  const [threadId, setThreadId] = useState<string | null>(null)   // S2: the current conversation thread ('' / null = global)
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
  // V-B (Tim 2026-06-07) — the BARGE-IN + STREAM-CANCEL handles. Two defects fixed in this lane:
  //  (1) re-arm: auto-listen used ONE MediaRecorder across pause()/resume() and reset `chunks=[]` after
  //      the only chunk carrying the webm/EBML init header — so turn 2+ produced a HEADERLESS continuation
  //      fragment that STT could not decode (proven by the on-phone trace: every autolisten_stt after the
  //      first fire is chars:0/empty:true while vad_pause keeps firing). FIX = a FRESH recorder per listen
  //      cycle (mirrors what makes push-to-talk reliable — recordToggle always news up a recorder).
  //  (2) barge-in: nothing listened during playback + nothing could STOP a reply mid-stream. FIX = the
  //      persistent analyser keeps reading RMS while SPEAKING; sustained speech cancels the reply.
  // `voiceReaderRef` holds the in-flight /api/voice/stream reader so a barge-in can reader.cancel() it —
  // closing the socket, which the bridge's MSG_PEEK client_gone() detects to STOP synth (no bridge change).
  const voiceReaderRef = useRef<ReadableStreamDefaultReader<Uint8Array> | null>(null)
  // `playSourcesRef` tracks every live AudioBufferSourceNode so a barge-in can stop() them (cut the audio
  // already playing/queued). `playEpochRef` is a generation counter: playWavBuffer captures the epoch at
  // schedule time and a barge-in bumps it, so a chunk that arrives AFTER the cut never gets scheduled.
  const playSourcesRef = useRef<AudioBufferSourceNode[]>([])
  const playEpochRef = useRef<number>(0)
  // `bargedRef` flags that the CURRENT turn was interrupted by the operator speaking — runVoiceTurn checks
  // it to stop consuming/playing the cancelled stream, and the auto-listen loop reads it to start the new
  // capture immediately rather than waiting for the (now-cancelled) reply to "finish".
  const bargedRef = useRef<boolean>(false)
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
  // A2 (G-36): 'activity' joins the union so the ambient feed gets a tabbar-driven bottom-sheet (mirrors the
  // 'rhm' reveal). G-57: an interactive offer landing raises 'rhm' (the App.tsx Hud effect calls setMobileTab).
  // This is sheet-layer state only — NOT a voice function; it stays the single source of "which bottom surface
  // is up" so a fresh offer and the operator's tab never both claim the bottom edge.
  const [mobileTab, setMobileTab] = useState<'canvas' | 'palette' | 'inbox' | 'rhm' | 'activity'>('canvas')
  // L-fe · the live cognition VIEW state (C7.1/C7.2/C7.3). reflects-never-owns: this is folded PURELY from
  // the `cognition.*` SSE lifecycle (the L-fe-be emit-contract) — the view NEVER writes cognition state, it
  // only mirrors what the backend emits as a staged turn fires. `cognitionInfo` is the registry projection
  // (/api/cognition_info) the view RENDERS FROM (roles → River tributaries, node_states → status tokens —
  // registry-driven, rule 8). `cognitionTurn` is the LIVE turn being narrated, built event-by-event:
  //   • turn.start  → open a fresh frame {turn_id, mode, shape, grain, cast[], address, roles{}}, every
  //                   cast role seeded LATENT (so a role that never fires reads as a dry gap, E2 §B.2/§C).
  //   • role.fire   → that role → FIRING (its model call is in flight).
  //   • role.ran    → that role → RAN (ok) or FAILED (a loud silted stub, ok:false — fail-loud rule 4).
  //   • inject      → the SOURCE role contributed `chars` into the reply → mark `injected` + sum contribution
  //                   (the worn-channel width, E2 §C — contribution = chars, the budget=attention shape).
  //   • part        → a reply part landed (the river fills as parts arrive); track n_parts.
  //   • turn.done   → the frame closes (total_ms, n_roles); kept as the last turn so the Pulse stays glanceable.
  // The PULSE (Altitude 0, default) reads the turn's shape FROM this (dilation = roles fired + chars injected,
  // a loud notch if any role FAILED, calm when idle). The RIVER (Altitude 1, on click) draws the tributaries.
  const [cognitionInfo, setCognitionInfo] = useState<Record<string, any>>({})
  const [cognitionTurn, setCognitionTurn] = useState<any>(null)
  const cognitionTurnRef = useRef<any>(null)   // the openStream closure folds into this synchronously (no stale closure)
  // G2/C7.4 · the cognition-engine HUMAN-face state (the SETTINGS "cognition" section reads it). reflects-
  // never-owns: every field below is a registry projection or a run-index read off an EXISTING /api/cognition/*
  // route (the SAME Suite methods the MCP face calls) — the FE owns nothing, it mirrors what the backend serves.
  //   • cogRuns        — the run-index tail (G2 "see runs"): {address,op,run_op,turn_id,role,duration_ms,…}.
  //   • cogFieldTypes  — the closed output-schema field-type grammar (the create-role form's type select).
  //   • cogModels      — the chat-capable models a role can bind (the create-role + run-role model select).
  //   • cogInputs      — the addresses a role can read (skill://context://run://cas://…).
  //   • cogBusy/cogErr — fail-loud surface state for the run/create/discover acts (a 400 SAYS so, never silent).
  //   • cogLastResult  — the last run_role/create_* outcome (the section shows the run:// / created id by-sight).
  const [cogRuns, setCogRuns] = useState<any[]>([])
  const [cogFieldTypes, setCogFieldTypes] = useState<string[]>([])
  const [cogModels, setCogModels] = useState<string[]>([])
  const [cogInputs, setCogInputs] = useState<string[]>([])
  const [cogBusy, setCogBusy] = useState(false)
  const [cogErr, setCogErr] = useState<string | null>(null)
  const [cogLastResult, setCogLastResult] = useState<any>(null)

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
  // L-fe · fold ONE cognition.* event into the live turn frame (reflects-never-owns — pure projection of the
  // emit-contract). Returns the NEXT turn object (or the current one unchanged). A role's status is DERIVED
  // from the lifecycle (the contract IS the truth): cast → latent, fire → firing, ran(ok) → ran, ran(!ok) →
  // failed, inject → contributed. A turn.start for a NEW turn_id opens a fresh frame (so the view always
  // narrates the latest turn). An event for an OLDER turn than the live one is ignored (the river fills in
  // event order for the current turn). schema-additive (rule): unknown fields are ignored; a missing field
  // never throws (so BE/FE evolve independently).
  function foldCognition(cur: any, ev: any): any {
    const k = ev.kind, t = ev.turn_id
    if (!t) return cur
    if (k === 'cognition.turn.start') {
      // a fresh frame — seed every fireable cast role LATENT (a role that never fires = a dry gap, E2 §B.2).
      const roles: Record<string, any> = {}
      for (const r of (Array.isArray(ev.cast) ? ev.cast : [])) roles[r] = { role: r, status: 'latent', chars: 0, ms: 0, ok: null, error: '' }
      return { turn_id: t, mode: ev.mode || '', shape: ev.shape || '', grain: ev.grain || '', address: ev.address || ('ui://cognition/' + t), cast: Array.isArray(ev.cast) ? ev.cast : [], roles, parts: 0, injected_chars: 0, n_inject: 0, done: false, total_ms: 0, n_roles: 0, started_ts: ev.ts || '' }
    }
    // every later event must belong to the CURRENT live turn (else it's an out-of-order tail — ignore).
    if (!cur || cur.turn_id !== t) return cur
    const roles = { ...cur.roles }
    const touch = (r: string) => { if (!roles[r]) roles[r] = { role: r, status: 'latent', chars: 0, ms: 0, ok: null, error: '' }; return roles[r] }
    if (k === 'cognition.role.fire') {
      const r = touch(ev.role); roles[ev.role] = { ...r, status: 'firing', model: ev.model || r.model || '' }
      return { ...cur, roles }
    }
    if (k === 'cognition.role.ran') {
      const r = touch(ev.role); const ok = ev.ok !== false
      roles[ev.role] = { ...r, status: ok ? (r.status === 'injected' || r.chars > 0 ? 'injected' : 'ran') : 'failed', ok, ms: ev.ms || 0, error: ev.error || '' }
      return { ...cur, roles }
    }
    if (k === 'cognition.inject') {
      const src = ev.source || ev.role; const r = touch(src)
      const chars = Number(ev.chars) || 0
      // contribution lands on the SOURCE role (the worn channel) — mark injected; keep failed if it failed.
      roles[src] = { ...r, status: r.status === 'failed' ? 'failed' : 'injected', chars: (r.chars || 0) + chars }
      return { ...cur, roles, injected_chars: (cur.injected_chars || 0) + chars, n_inject: (cur.n_inject || 0) + 1 }
    }
    if (k === 'cognition.part') return { ...cur, parts: Math.max(cur.parts || 0, Number(ev.part) || 0) }
    if (k === 'cognition.turn.done') return { ...cur, done: true, total_ms: Number(ev.total_ms) || 0, n_roles: Number(ev.n_roles) || 0, parts: Math.max(cur.parts || 0, Number(ev.n_parts) || 0) }
    return cur
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
      // L-fe: load the cognition projection (the sibling of object_info) so the live cognition VIEW renders
      // FROM the registry (roles → River tributaries, node_states → status tokens; registry-driven, rule 8).
      // Guarded like ui_info — a missing projection MUST be visible (the view shows nothing rather than guess).
      // Mirrored into BOTH the React state (the region reads it) AND the shape-reachable store (so the cognition
      // node-state render-tokens read EXACTLY like NodeShape reads NODE_STATES). Fire-tolerant: a 404 (the route
      // not yet on the bridge) records a boot error, never crashes boot.
      try {
        const ci = await api.cognitionInfo()
        if (ci && !ci.error) { setCognitionInfo(ci); registryStore.set({ COGNITION_INFO: ci }) }
        else bootErrors.push('cognition projection (' + (ci?.error || 'unavailable') + ')')
      } catch (e: any) { bootErrors.push('cognition projection (' + (e?.message || e) + ')') }
      const g = await loadGraph(editor); setEdges(g.edges || []); setGid(g.id); syncConfig(g)
      if ((g.nodes || []).length) setTimeout(fitGraph, 120)   // U6: chrome-aware fit on first load
      setTypes(await api.types())
      // F5: chatHistory now resolves to `{error}` on a non-ok GET — never feed a non-array into `chat`
      // (RhmChat reads `chat.length`/`chat.map`). Defensive guard; the array path is unchanged.
      { const h = await api.chatHistory(); if (Array.isArray(h)) setChat(h) }
      setCfg(await api.rhmConfig())
      api.personas().then(p => setPersonas(Array.isArray(p) ? p : [])).catch(() => {})   // the switchable cast
      api.listConversations().then(t => setThreads(Array.isArray(t) ? t : [])).catch(() => {})   // S2: reopen list
      api.chatModelsDetailed().then(m => setChatModelsX(Array.isArray(m) ? m : [])).catch(() => {})   // S1: picker rows
      api.voiceEngineKnobs().then(k => setEngineKnobs(k && typeof k === 'object' ? k : {})).catch(() => {})   // S5: engine knobs
      api.voice().then(v => setVoiceInfo(v && typeof v === 'object' ? v : {})).catch(() => {})   // S5: ears + engine status
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
        // A3 · keep the open Settings surface LIVE: a mode/config change (from this surface, the toolbar dial,
        // the RhmChat gear, or the RHM's own configure verb) re-loads the read-only registries so the modes/
        // autodetect/roles/voice panels reflect the new truth without a re-open. Inert when settings are closed.
        if (settingsOpenRef.current) void loadSettingsData()
      } else if (k.startsWith('cognition.')) {
        // L-fe · the LIVE COGNITION VIEW branch (C7.2 — live + no poll). This MIRRORS the `decision.*` branch
        // below: a `cognition.*` lifecycle event (the L-fe-be emit-contract) folds into the live turn frame so
        // the Pulse opens / the River fills as a STAGED turn fires (turn.start → role.fire×N → part → role.ran×N
        // → inject → part → turn.done). reflects-never-owns: we ONLY mirror the emitted events; nothing is
        // written back. The fold is synchronous off the ref (no stale closure, no await — these events arrive
        // fast and in-order). `cognition.wave` (the per-WAVE rollup, preserved by L-fe-be) is NOT a per-turn
        // lifecycle kind → foldCognition ignores it (only the 6 contract kinds touch the frame). The event is
        // already merged into the activity log at the top of onmessage (so the feed shows it too).
        const next = foldCognition(cognitionTurnRef.current, ev)
        cognitionTurnRef.current = next
        setCognitionTurn(next)
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
  // I1-gate: enter/leave the deliberate point-to-indicate mode. Leaving clears any live indication (+ its
  // `.ui-indicated` DOM cue) so the surface returns fully to normal clicking.
  function toggleIndicateMode() {
    const next = !indicateModeRef.current
    indicateModeRef.current = next; setIndicateMode(next)
    if (!next) indicate(null)
    setNotice(next ? '◎ point mode ON — tap a UI element to make it your next message’s focus' : 'point mode off')
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
      // STUDIO · close the loop by USE: the comment is in the SHARED annotation store → re-read the thread
      // so the Composer's thread view shows it immediately (the persist-to-shared-store proof). The
      // events.length poke would also refresh it, but the explicit re-read makes the round-trip atomic.
      await fetchAnnotations(addr)
    } catch (e: any) { setNotice('✕ could not attach comment: ' + (e?.message || e)) }
  }
  // GENERATE FOLLOW-ON · the studio "generate" step — wire the committed generate-for-mockups ENGINE to the
  // surface. For the MOCKUP under review (the whole file, NOT the ui:// locus — generate operates on the
  // file, comment/request operate on the locus), POST /api/mockup-generate in PLAN mode (api.mockupGenerate
  // defaults to 'plan' = SAFE/read-only: the engine PROPOSES the edit and changes NOTHING). The RHM then
  // SHOWS what it would change (the returned summary + changed_files==[] proof). MINT/PROPOSE-only — plan
  // mode never applies a change. Fail-loud (rule 4): no mockup open, or a backend 400 (no actionable
  // feedback / engine raise normalized to {error} by jr) → a visible notice, never a silent no-op.
  async function mockupGenerate(mockup: string | null) {
    if (!mockup) { setNotice('✕ open a mockup to review first, then generate'); return }
    setGenerateBusy(true)
    try {
      const r = await api.mockupGenerate(mockup, 'plan')
      if (r?.error) { setGenerateResult(null); setNotice('✕ ' + r.error); return }   // fail-loud: surface the backend 400
      setGenerateResult(r)
      const n = Array.isArray(r.changed_files) ? r.changed_files.length : 0
      setNotice('⚙ generate (plan) proposed an edit for ' + mockup + ' — ' + n + ' file(s) would change (nothing applied)')
    } catch (e: any) { setGenerateResult(null); setNotice('✕ generate failed: ' + (e?.message || e)) }
    finally { setGenerateBusy(false) }
  }
  // G-4 · THE WIRE'S OPERATOR DOOR — mint a build-intent FROM the indicated ui:// element (the missing
  // FE caller for the self-build wire; D1/G-4). The SIBLING of annotateLocus: where annotateLocus attaches
  // a comment, this REQUESTS A CHANGE — it POSTs /api/intent-at, which mints a build-intent whose SCOPE is
  // derived from the pointed address (S3) and whose X16 BLAST-RADIUS is computed at consent time, so the
  // minted item carries the reach the operator then sees + approves (BlastRadiusReach + /api/resolve — the
  // door's "see the reach → approve" half reuses the EXISTING components, never reimplemented). MINT-ONLY:
  // it surfaces the intent with resolved=None; it NEVER dispatches (dispatch is dispatch_decision, off this
  // face, posture-gated, safe-by-default `plan`). Returns the minted item (so the caller can show its reach
  // inline) or null on failure. Fail-loud (rule 4): no locus / not a ui:// element / empty text → a visible
  // notice, never a silent no-op. After a successful mint we poll() so the new build-intent also appears in
  // the Inbox builds lane (the persistent home; the door is the entry, the Inbox is the standing deck).
  async function mintBuildIntent(text: string): Promise<any | null> {
    const addr = indicatedRef.current
    if (!addr || !addr.startsWith('ui://')) { setNotice('✕ point at a ui:// element first, then request the change'); return null }
    const body = (text || '').trim()
    if (!body) { setNotice('✕ a change request needs a description (no silent no-op)'); return null }
    try {
      const r = await api.intentAt(addr, body)
      if (r?.error) { setNotice('✕ ' + r.error); return null }   // fail-loud: surface the backend 400, never swallow
      const title = getUI_INFO()[addr]?.title
      setNotice('⚙ build-intent minted at ' + (title || addr) + ' — review the reach, then approve (plan-mode by default)')
      await poll()                                                // the new intent joins the Inbox builds lane too
      return r
    } catch (e: any) { setNotice('✕ could not mint the build-intent: ' + (e?.message || e)); return null }
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
  // ── MOBILE POINTING (Tim's design, 2026-06-11): LONG-PRESS = point. No toggle. The set
  // ACCUMULATES across taps/tabs (multi-select: long-press elsewhere adds; long-press a selected
  // thing removes it). Regular taps stay completely normal. Desktop's point-mode is untouched.
  const [pointedSet, setPointedSet] = useState<string[]>([])
  const pointedSetRef = useRef<string[]>([])
  const togglePointed = (addr: string) => {
    const cur = pointedSetRef.current
    const next = cur.includes(addr) ? cur.filter(a => a !== addr) : [...cur, addr]
    pointedSetRef.current = next; setPointedSet(next)
    document.querySelectorAll('.ui-pointed').forEach(el => {
      const ref = (el as HTMLElement).dataset?.uiRef
      if (ref && !next.includes(ref)) el.classList.remove('ui-pointed')
    })
    if (!cur.includes(addr)) {
      document.querySelectorAll(`[data-ui-ref="${CSS.escape(addr)}"]`).forEach(el => el.classList.add('ui-pointed'))
      indicate(addr)                                      // last-pointed = the indicated locus (compat)
    }
  }
  const clearPointed = () => {
    pointedSetRef.current = []; setPointedSet([])
    document.querySelectorAll('.ui-pointed').forEach(el => el.classList.remove('ui-pointed'))
    indicate(null)
  }
  useEffect(() => {
    if (window.innerWidth > 699) return                   // the long-press gesture is the PHONE face
    let timer: any = null, sx = 0, sy = 0, target: string | null = null, fired = false
    const HOLD_MS = 480, MOVE_PX = 9
    const down = (e: PointerEvent) => {
      const el = (e.target as HTMLElement)?.closest?.('[data-ui-ref]') as HTMLElement | null
      const ref = el?.dataset?.uiRef
      // only FULL addresses point (ui:// chrome+canvas, run:// instances, exchange:// circles);
      // the chat/builder/tray's own controls never become the subject (the conversing guard).
      if (!ref || !/^(ui|run|exchange):\/\//.test(ref)) return
      if (el.closest('[data-ui-ref="chat"], [data-ui-ref="ui://chat/builder"], .mobile-tray')) return
      sx = e.clientX; sy = e.clientY; target = ref; fired = false
      timer = setTimeout(() => { fired = true; togglePointed(target!) }, HOLD_MS)
    }
    const move = (e: PointerEvent) => {
      if (timer && (Math.abs(e.clientX - sx) > MOVE_PX || Math.abs(e.clientY - sy) > MOVE_PX)) {
        clearTimeout(timer); timer = null                 // a drag is a drag — never a point
      }
    }
    const up = () => { if (timer) { clearTimeout(timer); timer = null } }
    const ctx = (e: Event) => { if (fired) e.preventDefault() }   // iOS long-press menu suppression
    document.addEventListener('pointerdown', down, true)
    document.addEventListener('pointermove', move, true)
    document.addEventListener('pointerup', up, true)
    document.addEventListener('contextmenu', ctx, true)
    return () => {
      document.removeEventListener('pointerdown', down, true)
      document.removeEventListener('pointermove', move, true)
      document.removeEventListener('pointerup', up, true)
      document.removeEventListener('contextmenu', ctx, true)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    function onDocClick(e: MouseEvent) {
      if (!indicateModeRef.current) return                  // I1-gate: indicate only fires in the deliberate mode (Tim) — otherwise clicks are normal
      const tgt = e.target as HTMLElement | null
      if (tgt?.closest?.('[data-ui-ref="chat"]')) return    // inside the chat region → conversing, never indicating
      // G-4 · the WIRE-DOOR exclusion (mirrors the chat guard above, same failure it prevents). The door
      // (ui://canvas/wire-request) is the surface where the operator DESCRIBES a change TO the pointed
      // element — clicking into its textarea must NOT re-indicate the door itself (which would overwrite
      // the operator's pointed target and mint the change AGAINST the door). So a click anywhere inside the
      // wire door leaves the current indication UNTOUCHED — you point with the rest of the surface, then
      // describe the change in the door. (The door reads `indicated`, never becomes it.)
      if (tgt?.closest?.('[data-ui-ref="ui://canvas/wire-request"]')) return
      // S1 · the BUILDER-PANEL exclusion (same class as the chat guard — the second conversation
      // partner gets the same conversing-not-indicating rule). A click into the builder's input/send/
      // build-this must NOT re-indicate ui://chat/builder — that would overwrite the pointed target the
      // conversation (and a minted change) is ABOUT. The panel READS `indicated`, never BECOMES it.
      if (tgt?.closest?.('[data-ui-ref="ui://chat/builder"]')) return
      // F1 · the ADDRESS-HELP panel exclusion (same class as the chat + wire-door guards above). The help
      // panel (ui://inspector/help) is where the operator READS what-this-is + DRILLS the mechanism + SHAPES
      // how it presents (the F1 feedback affordance) — all ABOUT the currently-indicated element. A click
      // inside it (a drill caret, a reach toggle, a 'terser'/'lead with' chip) must NOT re-indicate to the
      // help panel itself — that would overwrite the pointed locus the help is FOR (and the shaping would be
      // recorded against ui://inspector/help instead of the real target). So the help panel READS `indicated`,
      // it never BECOMES it (mirrors the chat-region guard precisely). The panel still carries its data-ui-ref
      // (so show-me/address_help can describe the help surface itself); this only stops a click INSIDE it from
      // hijacking the indication — you point with the rest of the surface, then read/shape in the help panel.
      if (tgt?.closest?.('[data-ui-ref="ui://inspector/help"]')) return
      // STUDIO · the COMPOSER exclusion (same class as the chat + wire-door + help-panel guards above). The
      // studio Composer (ui://studio/composer) is where the operator types a comment/change-request ABOUT
      // the currently-indicated reviewed surface. A click into its textarea/buttons must NOT re-indicate the
      // composer itself — that would overwrite the pointed locus and record the comment against
      // ui://studio/composer instead of the real surface. So the Composer READS `indicated`, never BECOMES
      // it (mirrors the chat-region guard precisely). The same applies to the studio RhmPanel's own help
      // surface (ui://studio/rhm/help) — a drill there is ABOUT the locus, not a new locus.
      if (tgt?.closest?.('[data-ui-ref="ui://studio/composer"], [data-ui-ref="ui://studio/rhm/help"]')) return
      // L4-COHERENCE: the MODAL exclusion (main's REAL a89dab1 fix — keep it; it is what makes indicate-ON
      // safe). A click inside a modal OPERATES it (close/config), it never points AT it. NB the A3 consolidated
      // Settings modal root is `.settings-scrim`/`.settings-panel` (Settings.tsx:71-72) — NOT `.settings` — so
      // the merged `.settings` selector was a NO-OP for A3 (it matched only main's retired bespoke modal). With
      // indicate now defaulting ON, that no-op would resurrect the exact bug a89dab1 fixed (the Settings ✕
      // wouldn't close + a tap painted `.ui-indicated` translucency). So the guard matches the A3 classes
      // explicitly. `.workshop` (Workshop.tsx:18, exact class) is kept. This is the ONLY in-territory lever for
      // the A3 modal (Settings.tsx/App.tsx are out of this lane).
      if (tgt?.closest?.('.settings-scrim, .settings-panel, .workshop')) return    // inside a MODAL → operate it, never indicate
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
  // D2 · the COMPOSED address-help bundle. When the operator INDICATES a ui:// element, load "what can I do
  // here?" — the three legs (what_this_is · how_to_use · how_to_change) joined by the EXISTING D1 composer
  // (GET /api/address-help → Suite.address_help). Reflects-never-owns: the runtime/corpus is authoritative,
  // the surface just reads + composes the help. Keyed on `indicated` ONLY (the help text is STATIC per
  // address — no events.length re-poke, unlike History/SelfChanges). DEGRADE-CLEAN: a well-formed-but-thin
  // address returns a partial bundle (legs_present flags the gaps); the AddressHelp panel renders each leg's
  // absence honestly (G-53). FAIL-LOUD (rule 4): a backend 400 (a malformed address) sets addressHelpError so
  // the panel SAYS the address couldn't be resolved — never a silent blank.
  async function fetchAddressHelp(addr: string | null) {
    setAddressHelpError(null)
    if (!addr || !addr.startsWith('ui://')) { setAddressHelp(null); return }   // only a ui:// locus has help
    setAddressHelpBusy(true)
    try {
      const r = await api.addressHelp(addr)
      if (r?.error) {                                  // backend 400 (malformed/unparseable address) — fail loud
        setAddressHelp(null); setAddressHelpError(r.error); setNotice('✕ ' + r.error); return
      }
      setAddressHelp({
        address: r.address,
        what_this_is: r.what_this_is || addr,
        how_to_use: r.how_to_use ?? null,
        how_to_change: {
          scope: Array.isArray(r?.how_to_change?.scope) ? r.how_to_change.scope : [],
          blast_radius: r?.how_to_change?.blast_radius ?? null,
          note: r?.how_to_change?.note ?? null,
        },
        legs_present: {
          what_this_is: !!r?.legs_present?.what_this_is,
          how_to_change: !!r?.legs_present?.how_to_change,
          how_to_use: !!r?.legs_present?.how_to_use,
        },
        // F1: the learned presentation pref the adapt step attached (null = the clean default — no marker).
        presentation_pref: r?.presentation_pref ?? null,
        presentation_directive: r?.presentation_directive ?? null,
      })
    } catch (e: any) {
      setAddressHelp(null); setAddressHelpError(e?.message || String(e))
      setNotice('✕ could not load address help: ' + (e?.message || e))
    } finally { setAddressHelpBusy(false) }
  }
  // Load the help whenever the indicated locus changes. STATIC per address → no events.length dependency.
  // (NOT static once F1 lands: a learned pref re-shapes the bundle — but the pref is set THROUGH this same
  // surface via setPresentationPrefAt, which re-fetches explicitly, so the effect stays keyed on `indicated`.)
  useEffect(() => { fetchAddressHelp(indicated) /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [indicated])
  // F1 ALTITUDE · THE IN-SYSTEM FEEDBACK CHANNEL (the visible half of the learning loop, committed backend
  // e1700b4). The SIBLING of annotateLocus/mintBuildIntent: where annotateLocus attaches a COMMENT and
  // mintBuildIntent REQUESTS A CHANGE, this RESHAPES HOW THE LOCUS PRESENTS — "show me this terser / more
  // detail / lead with the change". It records the pref via POST /api/presentation-pref (Suite.set_presentation_pref
  // — the recorder, OFF the verb whitelist: a pref is a CONTROL signal, not an action), then RE-FETCHES the
  // address-help bundle so the surface RE-RENDERS adapted (the adapt step consults the pref). The loop closes
  // by USE: set a pref → the bundle reflects it (marker + the lead_with structural hoist) → it persists
  // (the leaf reads disk, survives reload). The voice/typing INPUT ("show me this differently") rides the
  // existing chat path (/api/chat, untouched per G-8); THIS is the deterministic affordance that records it.
  //
  // FAIL-LOUD (rule 4): no locus / not a ui:// element → a visible notice, never a silent no-op. The
  // arg-taking kinds (lead_with/shape) REQUIRE a non-empty arg (the backend re-checks + 400s); the affordance
  // passes the arg, and we guard it here too so the operator gets the message, not a swallowed 400. A backend
  // 400 (malformed pref / address) surfaces via setNotice. `text` is the human phrasing kept for the thread.
  async function setPresentationPrefAt(kind: string, arg?: string, text?: string) {
    const addr = indicatedRef.current
    if (!addr || !addr.startsWith('ui://')) { setNotice('✕ point at a ui:// element first, then shape how it presents'); return }
    const a = (arg || '').trim()
    if ((kind === 'lead_with' || kind === 'shape') && !a) {
      setNotice('✕ "' + kind + '" needs a value (e.g. what to lead with) — no silent no-op'); return
    }
    const pref: { kind: string; arg?: string } = a ? { kind, arg: a } : { kind }
    setPrefBusy(true)
    try {
      const r = await api.setPresentationPref(addr, pref, text)
      if (r?.error) { setNotice('✕ ' + r.error); return }     // fail-loud: surface the backend 400, never swallow
      // CLOSE THE LOOP: the pref is recorded; re-fetch the bundle so the surface re-renders adapted (the
      // useEffect won't re-fire — `indicated` is unchanged — so the re-fetch is explicit here).
      await fetchAddressHelp(addr)
      const title = getUI_INFO()[addr]?.title
      setNotice('✦ learned how to present ' + (title || addr) + ' — it will be shown this way from now on')
    } catch (e: any) { setNotice('✕ could not shape the presentation: ' + (e?.message || e)) }
    finally { setPrefBusy(false) }
  }
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
  // STUDIO · load the comment thread whenever the indicated locus changes (and on a live event at this
  // locus — events.length is the cheap poke, mirroring History/SelfChanges). Read-back of the SHARED store.
  useEffect(() => { fetchAnnotations(indicated) /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [indicated, events.length])
  // STUDIO (G4) · bind the gallery corpus once on mount (registry-is-truth). Fire-and-forget — refreshCorpus
  // OWNS its fail-loud path (it writes corpusErr the Rail surfaces), so a slow/failed corpus fetch never
  // stalls the rest of boot. The Studio surface also re-binds on mount as a belt-and-braces (cheap GET).
  useEffect(() => { void refreshCorpus() /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [])
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
      // REVIEW WORKSPACE: when a mockup is open, ship it as `mockup://<file>` so the brain reads it as
      // ground truth (the backend _chat_context injects the mockup's content into the LIVE-STATE block).
      // It rides FIRST so the "mockup under review" framing leads the focus block (like the indicated addr).
      const reviewPrefix = reviewMockupRef.current ? ['mockup://' + reviewMockupRef.current] : []
      const selected = [...reviewPrefix, ...(indicatedRef.current ? [indicatedRef.current] : []), ...nodeIds]
      // B1 · STREAMING is the DEFAULT path (parts appear incrementally); the non-stream /api/chat is the
      // PRESERVED fallback (behind chatStreaming, default true). The streaming `done` event is a true SUPERSET
      // of /api/chat's return (reply/proposal/action/thread_id/history), so the SAME post-turn handling
      // (handleChatResult) runs for both — no feature is lost on the stream path (no silent regression).
      if (chatStreaming) {
        // hold the live assistant message index so each {type:part} appends to ITS text in place. Push an
        // empty assistant bubble first; parts grow it. On done we OVERWRITE with the canonical joined reply
        // (the parts are display-incremental; the persisted reply is the source of truth — never a re-join).
        let assistantIdx = -1
        let acc = ''
        let captured: any = null                               // the done event — handled AFTER the stream closes (so its
        await api.chatStream(m, { selected, pointed_element: pointedElementRef.current },  // V-B: ship the pointed element (run INSIDE this try's error coverage)
          (text) => {                                          // onPart — the incremental display
            acc = acc ? acc + ' ' + text : text
            setChat(c => {
              if (assistantIdx < 0) { assistantIdx = c.length; return [...c, { role: 'assistant', text: acc }] }
              const nc = c.slice(); nc[assistantIdx] = { role: 'assistant', text: acc }; return nc
            })
          },
          (done) => {                                          // onDone — reconcile the bubble to the CANONICAL reply
            captured = done
            if (done.reply) {                                  // overwrite the incremental bubble with the canonical reply
              setChat(c => {
                if (assistantIdx < 0) return [...c, { role: 'assistant', text: done.reply }]
                const nc = c.slice(); nc[assistantIdx] = { role: 'assistant', text: done.reply }; return nc
              })
            }
          })
        // the done event IS the /api/chat-shaped return → reuse the shared handler (proposal/action/thread/
        // poll/voice-out). AWAITED HERE (not in onDone, which chatStream runs un-awaited inside its read loop)
        // so a post-turn poll()/reaction rejection is caught by THIS try (fail-loud, no unhandled rejection) +
        // chatBusy clears AFTER it settles. applyHistory:false — the parts already rendered; re-setting history
        // would double the turn.
        if (captured) await handleChatResult(captured, { applyHistory: false })
        return
      }
      const r = await api.chat(m, { selected, pointed_element: pointedElementRef.current })  // V-B: ship the pointed element
      // F5 · the named bug. On a backend 400 (model unreachable — the literal first thing an operator hits)
      // api.chat now resolves to a normalized `{error}` (api.ts jr). BEFORE F5 this did `setChat(r.history)`
      // = `setChat(undefined)` → RhmChat `chat.length` threw at render → white-screen. Now: surface the
      // backend's error text as a VISIBLE assistant message (fail-loud, rule 4 — never a silent swallow) and
      // return WITHOUT touching the chat array. `finally` clears chatBusy. No throw, no undefined setChat.
      if (r.error) { setChat(c => [...c, { role: 'assistant', text: '⚠ ' + r.error }]); return }
      // the shared post-turn handler (proposal/action/thread/history/poll/voice-out) — reused by the stream
      // path. AWAITED so a post-turn poll()/reaction rejection stays inside this try (the preserved non-stream
      // path's original behaviour: poll/applyActionReactions were awaited directly in sendChat's try).
      await handleChatResult(r, { applyHistory: true })
    }
    catch (e: any) { setChat(c => [...c, { role: 'assistant', text: '⚠ ' + (e?.message || '(could not reach the brain)') }]) }
    finally { setChatBusy(false) }
  }

  // B1 · the SHARED post-turn handler. /api/chat returns {reply,proposal,action,thread_id,history}; the
  // streaming {type:done} event is a SUPERSET of the SAME shape. Both route here so neither path loses the
  // consent card, the action reactions, the thread sync, or the voice-out. `applyHistory` is false on the
  // stream path (the turn was already rendered incrementally — re-setting history would double it).
  async function handleChatResult(r: any, { applyHistory }: { applyHistory: boolean }) {
    // defensive (F5/advisor): only replace the log with a real array. A non-ok GET resolves to `{error}`
    // (no `.history`); never `setChat(undefined)`.
    if (applyHistory && Array.isArray(r.history)) setChat(r.history)
    if (r.thread_id) { setThreadId(r.thread_id); refreshThreads() }   // S2: keep the thread + its last_msg/title fresh
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
  // B1 — APPROVE / PICK-AN-OPTION (click #2, the consent commit). The offer-with-options surface calls
  // this with the chosen option; called bare it commits the PRIMARY offer (top-level verb/address/args).
  // Either way it fires the chosen verb-at-address through /api/act (the I2 dispatch path — REUSE, never
  // a new path). The action runs ONLY here, on the operator's pick. Then drive the SAME post-dispatch
  // reaction the chat path uses, surface the "did X" confirmation, and clear the card. Fail-loud (rule 4).
  async function approveProposal(opt?: { verb: string; address?: string | null; args?: any }) {
    const p = proposal
    if (!p || chatBusy) return
    // the picked option (an explicit choice) OR the primary offer (a bare approve) — never a guess.
    const chosen = opt ?? { verb: p.verb, address: p.address, args: p.args }
    setChatBusy(true)
    try {
      const r = await api.act(chosen.verb, chosen.address || undefined, chosen.args)
      if (r.error) { setChat(c => [...c, { role: 'assistant', text: '⚠ ' + r.error }]) }
      else {
        if (r.reply) setChat(c => [...c, { role: 'assistant', text: '✓ ' + r.reply }])
        await applyActionReactions(r.action)
        // B3 — round-trip integrity: if this offer was REVIVED from the inbox (_sid), the act has now run,
        // so RESOLVE the queued item out of live_escalations (approve) — else it would linger as a ghost
        // duplicate after the very thing it queued was done. Only AFTER a successful act (never before).
        if (p._sid) { await api.resolve(p._sid, 'approve', 'approved from the revived offer') }
        await poll()   // poll() refreshes the inbox → the resolved deferred-offer leaves live_escalations
      }
    }
    catch { setChat(c => [...c, { role: 'assistant', text: '(could not reach the brain to act)' }]) }
    finally { setProposal(null); setChatBusy(false) }
  }
  // B1 — STEER/REFINE (the direction channel — not binary): the operator types a steer ("smaller scope",
  // "the other node", "a draft first") and it loops BACK to the RHM to refine the offer. Implemented by
  // REUSING sendChat (the voice/co-presence path stays untouched — we do NOT edit sendChat's body) with a
  // composed message that names the standing offer so the RHM refines it rather than answering fresh. The
  // prior offer is NOT in the chat log (suite.py:3365 persists only prose+action), so the steer carries
  // the offer-context inline. sendChat already clears the old card (line 669); a refined offer returns as
  // a NEW r.proposal → that IS the loop. SEAM: the RHM MAY act or answer instead of re-offering depending
  // on mode — the FE cannot force a re-suggest; this presents the steer, the brain decides (flagged gap).
  async function steerProposal(text: string) {
    const p = proposal
    const steer = text.trim()
    if (!p || !steer || chatBusy) return
    const at = p.address ? ` at ${p.address}` : ''
    const composed = `Refine the offer (${p.verb}${at}) — steer: ${steer}`
    await sendChat(composed)   // reuses the preserved chat path; the refined offer returns as a new proposal
  }
  // B3 — DEFER (the configurable QUEUE arm, §6B mode #4): the operator isn't rejecting the offer, just not
  // now — and now it is a REAL queued item, not the old no-op set-aside. Persist the WHOLE offer (its
  // verb/address/args/options/interactive/direction) to the inbox via /api/defer-offer (the EXISTING
  // surfaced/inbox store — registry-is-truth, no parallel queue). It lands in live_escalations (resolved=
  // None), gets its own resume lane in the Inbox, and revisiting RE-OPENS this exact interactive card
  // (reviveOffer below). NOTHING runs: defer dispatches no /api/act — the offer's verb runs only on a later
  // approve (the B1/B2 consent invariant preserved). Fail-loud on a backend error (never a silent drop).
  async function deferProposal() {
    const p = proposal
    if (!p || chatBusy) return
    // already-queued (a revived offer with _sid) → deferring again is a no-op re-shelve: just drop the card.
    if (p._sid) { setNotice('offer set aside — it’s still queued in your inbox (revisit it there)'); setProposal(null); return }
    setChatBusy(true)
    try {
      const r = await api.deferOffer({ verb: p.verb, address: p.address, args: p.args,
        options: p.options, interactive: p.interactive, direction: p.direction })
      if (r?.error) { setNotice('✕ could not queue the offer: ' + r.error); return }   // fail-loud, keep the card
      setNotice('⏸ offer queued to your inbox — revisit it any time to resume the conversation')
      setProposal(null)
      await poll()   // refresh the inbox so the new deferred-offer lane appears immediately
    }
    catch (e: any) { setNotice('✕ could not reach the brain to queue the offer (' + (e?.message || e) + ')') }
    finally { setChatBusy(false) }
  }
  // B1 — SET ASIDE (the lighter, DISTINCT action): drop the live card WITHOUT queuing and without acting —
  // "not now, and I don't need it kept." The honest no-op set-aside (no /api/act, no inbox item). Kept as a
  // separate secondary from the durable QUEUE (defer) above, so the operator chooses queue-it vs forget-it.
  function setAsideProposal() { setNotice('offer set aside — not queued (ask again to revisit)'); setProposal(null) }
  // I3 — REJECT/DISMISS does nothing but drop the card (no backend call; the action never ran). If this is a
  // REVIVED queued offer (_sid), resolving it rejected clears it out of the inbox (round-trip integrity —
  // it doesn't linger after the operator has explicitly rejected it).
  function dismissProposal() {
    const p = proposal
    if (p?._sid) { api.resolve(p._sid, 'reject', 'dismissed from the revived offer').then(() => poll()) }
    setProposal(null)
  }
  // B3 — REVIVE a deferred offer from the inbox: read the persisted proposal back out and RE-OPEN the live
  // interactive card (the ProposeAffordance with its options + steer + approve), carrying _sid so approve/
  // dismiss closes the round-trip. This is the "live conversation when revisited, not a dead queue" half of
  // B3. Reuses the SAME setProposal the chat path uses — the revived card is byte-identical to the original
  // offer (select≠approve, nothing-runs-until-approved are preserved for free). Fail-loud on a backend error.
  async function reviveOffer(sid: string) {
    if (!sid) return
    const r = await api.reviveOffer(sid)
    if (r?.error) { setNotice('✕ could not reopen the offer: ' + r.error); return }
    const stored = r?.proposal
    if (!stored || (!stored.verb && !(stored.options && stored.options.length))) {
      setNotice('✕ the deferred offer carried no revivable proposal'); return   // fail-loud, never a dead card
    }
    setMobileTab('rhm')   // bring the RHM surface forward (on phone the offer renders in the rhm sheet)
    setProposal({ ...stored, _sid: sid })
    setNotice('▷ reopened the deferred offer — discuss, steer, then approve (nothing has run)')
  }
  // C4 (FE show-me lane) — dial-select STARTS the organ. Selecting the guided/walkthrough presence mode
  // must do MORE than the cosmetic set_mode: it must bind the dial to the REAL walkthrough organ. We keep
  // the existing pure set_mode+poll (harmless+keeps the dial honest for every mode) and, ONLY for the
  // walkthrough mode, ALSO call POST /api/walkthrough/start (the backend composer: set_mode + start_session
  // over the pending items). The call is ASYNC with the EXISTING wtBusy spinner — a populated walk compiles
  // a model-invoking session graph and can be slow / model-dependent (GAPS G-41), so we never block the UI
  // thread expecting an instant return. On organ_started:true we feed the result straight into the EXISTING
  // walk machinery via setSession (same shape start_session returns → the per-step zoom effect [~1046] and
  // narration effect drive themselves). On organ_started:false we surface the reason as a CLEAR message
  // (rule 4 — fail loud, never a silent no-op: the dial IS set, but there is nothing to step through).
  async function changeMode(mm: string) {
    setNotice('presence → ' + mm); await api.setMode(mm); await poll()
    if (mm !== 'walkthrough') return
    if (wtBusyRef.current) return                    // a walk start/step is already in flight — drop the extra
    wtBusyRef.current = true; setWtBusy(true)
    setNotice('walkthrough selected — gathering what needs you…')
    try {
      // G-41 — the populated walk compiles a model-invoking review-session graph; with NO model up the
      // server-side start_walkthrough HANGS indefinitely. A bare `await` on that would NEVER resolve, so
      // `finally` would never run and wtBusyRef (the SHARED guard for startWalk/nextStep/respondStep too)
      // would stay TRUE forever — bricking the entire review organ until a reload, with a stuck
      // "gathering…" notice. That is a SILENT FAILURE (rule 4). We BOUND the call: race it against a
      // generous deadline (a LIVE model walk is legitimately slow — minutes for a cold model — so the
      // window is wide; this only catches a true hang, never a slow-but-progressing start). On timeout we
      // surface a LOUD, recoverable degrade and the finally releases the guard (the operator can retry).
      const TIMEOUT_MS = 45000
      const r: any = await Promise.race([
        api.walkthroughStart(),                       // no item_ids → walk every PENDING unresolved inbox item
        new Promise((_, rej) => setTimeout(() => rej(new Error('__wt_timeout__')), TIMEOUT_MS)),
      ])
      if (r?.error) { setNotice('✕ walkthrough: ' + r.error); return }
      if (r.organ_started) {
        try { localStorage.setItem('company-review-session', r.session) } catch { /* */ }
        setSession(r); setWtReason(''); setWtSpoke('')   // → the existing per-step view-drive + narration fire
        setNotice('walkthrough started — stepping you through ' + (r.total != null ? r.total + ' item(s)' : 'what needs you'))
      } else {
        // nothing-pending: the dial IS in guide mode, but there is nothing to walk — say so plainly.
        setNotice('🛈 ' + (r.reason || 'nothing pending to walk through — surface or capture an item first, then re-select walkthrough'))
      }
    } catch (e: any) {
      // The timeout reject (G-41 model-down) gets a SPECIFIC, recoverable message; anything else surfaces raw.
      if (e?.message === '__wt_timeout__') {
        setNotice('✕ no model responded — start a model (the walkthrough organ needs one to compile the walk), then re-select walkthrough')
      } else { setNotice('✕ could not start the walkthrough: ' + (e?.message || e)) }
    }
    finally { wtBusyRef.current = false; setWtBusy(false) }   // re-enable on success OR error OR timeout — the guard is NEVER stuck
  }
  // C1 (FE show-me lane) — start a SYSTEM-INITIATED GUIDED SEQUENCE (the "show me how" tour). Distinct from
  // changeMode/startWalk (which walk pending INBOX items via coa, model-dependent): a guide walks the
  // INTERFACE's own addressed ELEMENTS, narrating each from the corpus how-to (address_help) — MODEL-FREE
  // by construction (the backend present_current guide branch returns before coa). It rides the EXISTING
  // walk machinery: on organ_started we setSession(r) and the SAME per-step view-drive effect [~1104] +
  // narration effect [~1113] + the Walkthrough card drive themselves — because each step's raw.ui_target is
  // now a real element address (G-43), resolveUiTarget SPOTLIGHTS the live element, and session.framing IS
  // the how-to text (so the voice narration effect speaks the how-to for free — we never touch speakReply).
  // POST /api/guide/start is called INLINE (api.ts is the voice session's hot-collision file, G-8 — we do
  // NOT add a method there). BOUNDED-await mirrors changeMode's G-41 fix: although the guide is model-free,
  // a hung/slow bridge must never leave the SHARED wtBusyRef guard stuck (that would brick the review organ
  // too) — we race the start against a deadline and the finally ALWAYS releases. Reachable as an operator
  // entry (the toolbar "?" guide control) AND directly system/RHM-initiated (the route + start_guide()).
  async function startGuide(topic?: string) {
    if (wtBusyRef.current) return                    // a walk/guide start or step is already in flight — drop the extra
    wtBusyRef.current = true; setWtBusy(true)
    setNotice('show me how — starting a guided tour…')
    try {
      // BOUND the start (G-41/G-44 reuse): the guide is model-free, but a hung bridge would otherwise leave
      // wtBusyRef TRUE forever (the SHARED guard for startWalk/nextStep/respondStep too) → a silent brick.
      const r: any = await Promise.race([
        fetch('/api/guide/start', { method: 'POST', headers: J, body: JSON.stringify({ topic: topic || undefined }) }).then(x => x.json()),
        new Promise((_, rej) => setTimeout(() => rej(new Error('__wt_timeout__')), 45000)),
      ])
      if (r?.error) { setNotice('✕ guide: ' + r.error); return }
      if (r.organ_started) {
        try { localStorage.setItem('company-review-session', r.session) } catch { /* */ }
        setSession(r); setWtReason(''); setWtSpoke('')   // → the existing per-step view-drive + narration fire
        setNotice('guided tour started — stepping you through ' + (r.total != null ? r.total + ' part(s)' : 'the interface'))
      } else {
        // FAIL LOUD (rule 4 — no silent no-op): the dial IS in guide register, but nothing to tour. Say so.
        setNotice('🛈 ' + (r.reason || 'no parts of the interface to tour right now'))
      }
    } catch (e: any) {
      if (e?.message === '__wt_timeout__') setNotice('✕ the guide did not start in time — try again')
      else setNotice('✕ could not start the guide: ' + (e?.message || e))
    }
    finally { wtBusyRef.current = false; setWtBusy(false) }   // re-enable on success OR error OR timeout — never stuck
  }
  // L4-GEAR-RETIRE: `applyCfg` (the legacy gear's model+persona apply) is GONE — A3 Settings writes each slot
  // live via setCfgSlot → set_rhm_config (the same backend path), so there is no batched apply gesture anymore.
  // Option A — switch between the personas: set the chosen persona AS active and AUTO-LOAD its voice
  // (the backend evicts the previous voice engine to fit the 16 GB card, then cold-loads this one —
  // accepted that a switch may cold-load). We optimistically reflect the new persona, then poll the
  // engine to 'up' so the operator sees when it's ready to speak. Fail-loud on the notice; never a
  // silent no-op. (A persona whose voice won't fit even after eviction — e.g. orpheus beside a big
  // brain — surfaces the budget gate's reason here.)
  async function switchPersona(id: string) {
    if (!id || id === cfg.persona) { setCfg((c: any) => ({ ...c, persona: id })); return }
    setCfg((c: any) => ({ ...c, persona: id }))
    setPersonaVoiceStatus('loading')                            // V4.2: badge tracks the cold-load
    setNotice(`switching to ${id} — cold-loading their voice…`)
    try {
      const r = await api.voiceSwitch(id)
      if (r.error) { setPersonaVoiceStatus('down'); setNotice('⚠ could not switch to ' + id + ': ' + r.error); return }
      if (r.service) {                                  // an engine that needs loading (not an always-on one)
        const dl = Date.now() + 240000                  // the heavy voices (orpheus) cold-load in minutes
        for (;;) {
          const sv = await api.voiceServices().catch(() => null)
          const st = sv?.services?.[r.service]?.state
          if (st === 'up') break
          if (st === 'down' || Date.now() > dl) { setPersonaVoiceStatus('down'); setNotice(`⚠ ${id}'s voice (${r.engine}) didn't come up — open the voice panel`); break }
          await new Promise(res => setTimeout(res, 3000))
        }
      }
      setPersonaVoiceStatus('ready')
      setNotice(`${id} is ready — talk (🎙) or type; it speaks back in listening mode`)
      setCfg(await api.rhmConfig())
    } catch (e: any) { setNotice('⚠ switch failed: ' + (e?.message || e)) }
  }
  // A3/E2-FE · load the read-only registries the consolidated Settings surface renders. Fire on OPEN (and on
  // a config/mode SSE event while open, so the surface stays live). reflects-never-owns: each is READ truth off
  // an EXISTING endpoint — NO new config endpoint, NO parallel composer (the lane law). fail-loud (rule 4): a
  // fetch that fails sets settingsErr so the surface SAYS so, never a silent blank; partial loads still render
  // (each setter is independent — one down endpoint doesn't blank the others). api.ts is off-limits to this
  // lane, so the two reads without an existing api method (roles, voicePaths, voice) use an inline fetch with
  // the same jr-style normalization the rest of the app uses (matching annotateLocus's inline-fetch precedent).
  async function loadSettingsData() {
    setSettingsBusy(true); setSettingsErr(null)
    const errs: string[] = []
    // capabilities carries the E1 mode_registry + the E2 composition_config (incl MODE_AUTODETECT). One call.
    try {
      const caps = await api.capabilities()
      setModeRegistry(caps?.mode_registry || {})
      const cc = caps?.composition_config || {}
      setCompositionCfg(cc)
      setAutodetect({ value: cc.MODE_AUTODETECT || 'off', options: Array.isArray(cc.MODE_AUTODETECT_OPTIONS) ? cc.MODE_AUTODETECT_OPTIONS : ['off', 'suggest', 'auto'] })
    } catch (e: any) { errs.push('capabilities/modes (' + (e?.message || e) + ')') }
    // roles — the model-FUNCTION role registry (judge + future) the config lab binds. GET /api/roles.
    try { const r = await fetch('/api/roles').then(x => x.json()); if (r?.error) errs.push('roles (' + r.error + ')'); else setRoles(r || {}) }
    catch (e: any) { errs.push('roles (' + (e?.message || e) + ')') }
    // voice paths — the pipeline/s2s registry. GET /api/voice/paths (s2s renders UNAVAILABLE, G-19).
    try { const r = await fetch('/api/voice/paths').then(x => x.json()); if (r?.error) errs.push('voice-paths (' + r.error + ')'); else setVoicePaths(r) }
    catch (e: any) { errs.push('voice-paths (' + (e?.message || e) + ')') }
    // voice status — per-engine TTS up/voices + the STT (ear) registry. api.voice() is the existing READ method.
    try { const r = await api.voice(); if (r?.error) errs.push('voice (' + r.error + ')'); else setVoiceStatus(r) }
    catch (e: any) { errs.push('voice (' + (e?.message || e) + ')') }
    // G2/C7.4 · the cognition-engine registry projections (the create-role form's selects + the run-index).
    // Each is an EXISTING /api/cognition/* read (registry-is-truth, rule 8) — a new model/field-type/input
    // appears in the form with zero FE edit. Independent of the others (one down read doesn't blank the rest).
    try { const r = await api.cogFieldTypes(); if (r?.error) errs.push('cognition field-types (' + r.error + ')'); else setCogFieldTypes(Array.isArray(r) ? r : (r?.types || Object.keys(r || {}))) }
    catch (e: any) { errs.push('cognition field-types (' + (e?.message || e) + ')') }
    try { const r = await api.cogModelsForRole(''); if (r?.error) errs.push('cognition models (' + r.error + ')'); else setCogModels(Array.isArray(r) ? r : (r?.models || [])) }
    catch (e: any) { errs.push('cognition models (' + (e?.message || e) + ')') }
    // available_inputs returns {utterance, roles[], role_addresses[], context_variables[], projections[],
    // projection_spaces[]} — flatten into the readable address vocabulary the input-wiring select offers
    // (registry-is-truth: a new role/context-var/projection appears here with zero FE edit, rule 8).
    try {
      const r = await api.cogInputs()
      if (r?.error) errs.push('cognition inputs (' + r.error + ')')
      else if (Array.isArray(r)) setCogInputs(r)
      else {
        const flat = [
          ...(r?.utterance ? ['utterance'] : []),
          ...(Array.isArray(r?.role_addresses) ? r.role_addresses : []),
          ...(Array.isArray(r?.context_variables) ? r.context_variables.map((c: string) => 'context://' + c) : []),
          ...(Array.isArray(r?.projection_spaces) ? r.projection_spaces : []),
        ]
        setCogInputs(flat)
      }
    }
    catch (e: any) { errs.push('cognition inputs (' + (e?.message || e) + ')') }
    try { const r = await api.cogListRuns(30); if (r?.error) errs.push('cognition runs (' + r.error + ')'); else setCogRuns(Array.isArray(r?.runs) ? r.runs : []) }
    catch (e: any) { errs.push('cognition runs (' + (e?.message || e) + ')') }
    if (errs.length) setSettingsErr('could not load: ' + errs.join('; '))
    setSettingsBusy(false)
  }
  // A3 · open the consolidated Settings surface — raises the modal AND loads its read-only registries. The
  // writable slots (model/persona/mode) already live in cfg/now (loaded at boot + kept live by SSE), so they
  // render instantly; loadSettingsData fills the extras. Closing just lowers the modal (state persists).
  function openSettings(tab?: 'brain' | 'modes' | 'voice' | 'roles' | 'composition') {
    if (tab) setSettingsTab(tab)
    setSettingsOpen(true)
    void loadSettingsData()
  }
  // A3 · write ANY whitelisted rhm-config slot through the EXISTING set_rhm_config path (the 11-slot whitelist:
  // model/base_url/persona/mode/voice_enabled/timeout/stt/roles/tts_engine/tts_voice/voice_path). REUSE — NOT a
  // new endpoint, NOT a new write path: it is the same api.setRhmConfig applyCfg uses, generalised to one slot.
  // The backend fail-loud-validates (unknown slot/engine/path → 400) so an invalid value surfaces, never sets.
  // After the write we mirror the returned fresh config (reflects-never-owns — the backend value is truth) and
  // poll() so the live surface (presence dot, mode line) reflects the change everywhere. The mode slot keeps
  // routing through changeMode (it also drives the walkthrough organ), so this is for the non-mode slots.
  async function setCfgSlot(key: string, value: any) {
    setNotice('set ' + key + ' → ' + value)
    try {
      const c = await api.setRhmConfig({ [key]: value })
      if (c?.error) { setSettingsErr(c.error); setNotice('✕ ' + c.error); return }
      setCfg(c); setNotice(key + ' → ' + value); await poll()
    } catch (e: any) { setSettingsErr(e?.message || String(e)); setNotice('✕ could not set ' + key + ': ' + (e?.message || e)) }
  }
  // G2 · re-probe the run-index (the "see runs" half) without a restart — the SAME read loadSettingsData does.
  async function refreshCogRuns() {
    setCogBusy(true); setCogErr(null)
    try { const r = await api.cogListRuns(30); if (r?.error) setCogErr(r.error); else setCogRuns(Array.isArray(r?.runs) ? r.runs : []) }
    catch (e: any) { setCogErr(e?.message || String(e)) }
    setCogBusy(false)
  }
  // G2 "do" · FIRE a role over an utterance → its run:// output. COMPUTATION, NOT a floor act (the engine
  // produces run:// + op.run telemetry; it never resolves/approves/dispatches — bridge.py:1701). Fail-loud:
  // a backend 400 (down model / unknown role) surfaces on cogErr + a notice, never a silent no-op. On success
  // the result (the run:// address + output) lands on cogLastResult AND the run-index is re-probed so the new
  // run shows in the list (the surface SEES what the act produced — verify-by-the-surface, not by assertion).
  async function runCogRole(body: { role: string; utterance?: string; model?: string }) {
    if (!body.role) { setCogErr('pick a role to run'); return }
    setCogBusy(true); setCogErr(null); setCogLastResult(null)
    setNotice('running role ' + body.role + '…')
    try {
      const r = await api.cogRunRole({ role: body.role, utterance: body.utterance || '', model: body.model || undefined })
      if (r?.error) { setCogErr(r.error); setNotice('✕ run ' + body.role + ': ' + r.error); setCogBusy(false); return }
      setCogLastResult({ kind: 'run', ...r })
      setNotice('ran ' + body.role + (r?.address ? ' → ' + r.address : ''))
      await refreshCogRuns()
    } catch (e: any) { setCogErr(e?.message || String(e)); setNotice('✕ run ' + body.role + ': ' + (e?.message || e)) }
    setCogBusy(false)
  }
  // C7.4 + A1 · DIRECT-CREATE a role (declarative-direct, NO approval — the floor-correct path; the bridge
  // reuses the SAME Suite.create_role the MCP create_role tool calls). The CORRECTNESS gate bites backend-side
  // (a malformed spec → AuthoringError → 400 → cogErr, fail-loud, never written). The build-dispatch floor is
  // untouched (this writes a roles/ file; it never launches claude -p). On success the created role is LIVE
  // (rediscovered) — we reload the cognition projections so the new role appears in the selects (registry-truth).
  async function createCogRole(spec: any) {
    if (!spec?.id) { setCogErr('a role needs an id'); return }
    setCogBusy(true); setCogErr(null); setCogLastResult(null)
    setNotice('creating role ' + spec.id + '…')
    try {
      const r = await api.cogCreateRole(spec)
      if (r?.error) { setCogErr(r.error); setNotice('✕ create ' + spec.id + ': ' + r.error); setCogBusy(false); return }
      setCogLastResult({ kind: 'create', ...r })
      setNotice('created role ' + spec.id + ' (live, no approval)')
      // the new role is live + rediscovered — refresh the cognition registry projection so the River/selects see it.
      try { const ci = await api.cognitionInfo(); if (ci && !ci.error) setCognitionInfo(ci) } catch { /* projection refresh is best-effort; the create already succeeded */ }
      try { const m = await api.cogModelsForRole(''); if (m && !m.error) setCogModels(Array.isArray(m) ? m : (m?.models || [])) } catch { /* best-effort */ }
    } catch (e: any) { setCogErr(e?.message || String(e)); setNotice('✕ create ' + spec.id + ': ' + (e?.message || e)) }
    setCogBusy(false)
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
      // C2 fix — a DOM-STAMPED canvas ELEMENT (not a graph node): the wire-door (data-ui-ref=
      // "ui://canvas/wire-request") + the portal window (ui://canvas/portal-window) are REGISTERED corpus
      // addresses carried as literal data-ui-ref strings on a DOM element, NOT tldraw shapes. Before this,
      // EVERY ui://canvas/<ref> fell to driveCanvas (the camera path) → it looked for a graph NODE named
      // "wire-request" and fail-loud'd ("no node wire-request on the canvas"), so the C2 ask-step spotlight
      // (the request-a-change door — the heart of the bootstrap) never landed. DISCRIMINATOR (cannot drift
      // the node-camera path): a live graph node-id is NEITHER a registered corpus address (UI_INFO[target]
      // is null for runtime node-ids) NOR DOM-stamped with a literal ui://canvas/<id> data-ui-ref (tldraw
      // shapes are camera-driven). So a registered address that is ALSO present in the DOM as that exact
      // data-ui-ref → spotlight it (the DOM element); everything else (every review-walk node drive) falls
      // straight through to driveCanvas, byte-identical. The DOM-present check means a registered-but-
      // unmounted canvas element camera-falls-back rather than spotlight-failing.
      if (UI_INFO[target] != null && document.querySelector('[data-ui-ref="' + target + '"]')) {
        return spotlightUiRef(target, target, UI_INFO)   // DOM-stamped canvas element (e.g. the wire-door)
      }
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
      // G-44 — BOUND the start (mirrors changeMode's G-41 fix): reviewStart compiles a model-invoking
      // review-session graph; with NO model up it HANGS server-side, and a bare await would leave the
      // SHARED wtBusyRef guard TRUE forever (the finally never runs) → bricks the whole review organ until
      // reload (a silent failure, rule 4). Race it against a generous deadline (a live walk is legitimately
      // slow — minutes for a cold model — so the window is wide; this only catches a true hang). On timeout:
      // degrade LOUD + release the guard so the operator can retry.
      const s: any = await Promise.race([
        api.reviewStart(itemIds, 'walkthrough'),
        new Promise((_, rej) => setTimeout(() => rej(new Error('__wt_timeout__')), 45000)),
      ])
      if (s?.error) { setNotice('✕ ' + s.error); return }
      try { localStorage.setItem('company-review-session', s.session) } catch { /* */ }
      setSession(s); setWtReason(''); setWtSpoke('')
    } catch (e: any) {
      if (e?.message === '__wt_timeout__') setNotice('✕ no model responded — start a model (the walk organ needs one to compile), then try again')
      else setNotice('✕ could not start the walk: ' + (e?.message || e))
    }
    finally { wtBusyRef.current = false; setWtBusy(false) }   // re-enable on success OR error OR timeout — never stuck
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
    // C2 — a GUIDED TOUR may have left an element INDICATED (step 0 indicates ui://toolbar/run to MOUNT the
    // wire-door for the ask step). On closing the tour, clear that indication so the canvas returns to a
    // neutral state the operator didn't have to choose (no lingering door / .ui-indicated / contextualized
    // history). Scoped to a GUIDE close (capture the flag BEFORE nulling) so a REVIEW-walk close — which never
    // sets indication — is byte-identical/undisturbed. indicate(null) is the existing clear path (fail-safe).
    const wasGuide = !!(sessionRef.current?.guide || sessionRef.current?.raw?.guide_address)
    setSession(null); sessionRef.current = null; spokenFor.current = ''
    if (wasGuide && indicatedRef.current) indicate(null)
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
  // C2 (teach-to-self-modify tour): a guided step may carry an INDICATE hint (raw.indicate, a ui:// address)
  // — a hard-gated element (the request-a-change wire-door) renders ONLY while a ui:// element is indicated.
  // So we call the EXISTING indicate(addr) FIRST (it sets `indicated` → React re-renders → the door mounts),
  // THEN resolveUiTarget. The spotlight is safe across this re-render because spotlightUiRef DEFERS its DOM
  // query one frame (setTimeout 30ms) — by the time it querySelectors the freshly-mounted door, React has
  // flushed. We supply the hint only; indicate() is the unchanged machinery (registry-validated, fail-loud).
  // No indicate hint (the default tour / review walk) → unchanged behaviour (resolveUiTarget only).
  useEffect(() => {
    if (!session || session.done || !session.item) return
    const hint = session.raw?.indicate as string | undefined
    if (hint && hint.startsWith('ui://') && indicatedRef.current !== hint) {
      indicate(hint)                // MOUNT the hard-gated element (the wire-door) before the spotlight
    }
    const tgt = session.raw?.ui_target
    if (tgt) resolveUiTarget(tgt)   // registry-validated; fail-loud if unknown (defers 30ms → mount lands first)
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
    // V-B: capture the play-epoch at ENTRY. A barge-in bumps playEpochRef + stops live sources; a chunk
    // whose decode finishes AFTER that bump must NOT schedule onto the (now-cut) timeline — so we re-check
    // the epoch after the async decode and drop the buffer if the turn was interrupted while we decoded.
    const epoch = playEpochRef.current
    const ctx = audioCtxRef.current
    if (ctx && ctx.state === 'running') {
      const audioBuf = await ctx.decodeAudioData(buf.slice(0))
      if (epoch !== playEpochRef.current) return                 // barged-in mid-decode — abandon this chunk
      const src = ctx.createBufferSource(); src.buffer = audioBuf; src.connect(ctx.destination)
      const now = ctx.currentTime
      const at = Math.max(now, playCursorRef.current || now)
      src.start(at); playCursorRef.current = at + audioBuf.duration
      // track the live source so a barge-in can stop() it; self-prune on natural end.
      playSourcesRef.current.push(src)
      src.onended = () => { playSourcesRef.current = playSourcesRef.current.filter(s => s !== src) }
      return
    }
    // fallback (desktop / context not unlocked): a one-shot element
    if (epoch !== playEpochRef.current) return                   // barged-in mid-decode — don't start it
    await new Audio(URL.createObjectURL(new Blob([buf], { type: 'audio/wav' }))).play()
  }
  // V-B — CUT all reply audio NOW (barge-in or a hard stop). Bump the epoch so any chunk still decoding is
  // dropped (playWavBuffer re-checks), stop() every live source node, and reset the play cursor so the next
  // turn starts a fresh queue. Fail-soft per-source (a node that already ended throws on stop()).
  function stopPlayback() {
    playEpochRef.current += 1
    for (const s of playSourcesRef.current) { try { s.stop() } catch { /* already ended */ } }
    playSourcesRef.current = []
    playCursorRef.current = 0
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
    // V-B: hold the reader so a barge-in (the auto-listen analyser hearing the operator speak over the
    // reply) can reader.cancel() it — that closes the socket, which the bridge's client_gone()/MSG_PEEK
    // detects and STOPS the per-sentence synth before the next one (no server change). bargedRef starts
    // false for this turn; if it flips, we stop consuming + drop any remaining chunks.
    bargedRef.current = false
    const reader = res.body.getReader(); const dec = new TextDecoder(); let buf = ''
    voiceReaderRef.current = reader
    try {
      for (;;) {
        let chunk: ReadableStreamReadResult<Uint8Array>
        try { chunk = await reader.read() }
        catch { break }                                          // reader.cancel() (barge-in) rejects the pending read — exit cleanly
        const { done, value } = chunk; if (done) break
        if (bargedRef.current) break                             // operator spoke over the reply — stop consuming this turn
        buf += dec.decode(value, { stream: true })
        const lines = buf.split('\n'); buf = lines.pop() || ''
        for (const ln of lines) {
          if (bargedRef.current) break
          const s = ln.trim(); if (!s) continue
          let ev: any; try { ev = JSON.parse(s) } catch { continue }
          if (ev.type === 'transcript') { setNotice('you said: ' + ev.text); if (ev.text) setChat(c => [...c, { role: 'user', text: ev.text }]) }
          else if (ev.type === 'reply') { if (ev.text) setChat(c => [...c, { role: 'assistant', text: ev.text }]) }
          else if (ev.type === 'chunk') { try { await playWavBuffer(b64ToArrayBuffer(ev.wav_b64)) } catch (e: any) { api.voiceLog('play_fail', { idx: ev.idx, error: String(e?.message || e) }) } }   // iOS/audio playback failure — captured, not silent
          else if (ev.type === 'error') { api.voiceLog('stream_error', { error: ev.error, step: ev.step, turn_id: ev.turn_id }); setNotice('⚠ ' + ev.error) }   // fail loud (V2.3) + durable
          else if (ev.type === 'done') { setNotice(''); poll() }
        }
      }
    } finally {
      if (voiceReaderRef.current === reader) voiceReaderRef.current = null   // only clear if still ours
    }
  }
  // V-B — BARGE-IN: the operator started speaking over the reply. Cut the audio (stopPlayback) AND cancel
  // the in-flight reply stream (reader.cancel → socket close → the bridge's client_gone() stops synth).
  // Sets bargedRef so runVoiceTurn's consume loop exits. Idempotent + fail-soft (a reader already done
  // throws on cancel). Returns nothing; the caller starts the fresh capture cycle.
  function bargeIn() {
    bargedRef.current = true
    stopPlayback()
    const r = voiceReaderRef.current
    if (r) { try { r.cancel() } catch { /* already settled */ } ; voiceReaderRef.current = null }
    api.voiceLog('autolisten_bargein', { input_mode: 'auto_listen' })   // durable: the reply was interrupted
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
      api.voiceLog('ptt_start', { input_mode: 'push_to_talk' })   // push-to-talk recording opened
    } catch { api.voiceLog('mic_denied', { mode: 'push_to_talk' }); setNotice('mic unavailable — grant microphone permission') }
  }
  // V1.1 / V-B — AUTO-LISTEN (hands-free, "reply on a finished thought, not a silence timer").
  //
  // SHAPE (V-B rewrite, Tim 2026-06-07 — fixes "works for turn 1 only, no barge-in, then doesn't register"):
  //  · the `stream` + Web Audio `analyser` are PERSISTENT for the whole session (independent of any recorder;
  //    the analyser tap is what watches RMS — it is alive in EVERY phase, including while the reply speaks).
  //  · a FRESH MediaRecorder is created for EACH listen cycle (inside `listenOnce`) and fully stop()'d to
  //    FLUSH a complete webm. ROOT-CAUSE FIX for re-arm: the old code reused ONE recorder across pause()/resume() and reset
  //    `chunks=[]` after the only chunk carrying the webm/EBML header had been consumed — so turn 2+ produced
  //    a HEADERLESS fragment STT could not decode (proven by the phone trace: every post-fire autolisten_stt
  //    was chars:0/empty:true while vad_pause kept firing → the recorder WAS recording, the BLOB was junk).
  //    A fresh recorder per cycle = a fresh header every turn (exactly why push-to-talk, which news up a
  //    recorder per press, always worked). No pause()/resume() to fail, either.
  //  · phases: LISTENING (recorder running, RMS end-of-speech → STT+judge → fire/keep) → SPEAKING (NO recorder;
  //    analyser still tapping → BARGE-IN detect) → back to LISTENING. After a fired turn the loop ALWAYS
  //    re-arms a fresh recorder (the re-arm the old code lost), unless the operator stopped the session.
  //  · BARGE-IN: while SPEAKING, sustained speech (≥ BARGEIN_FRAMES consecutive frames over a RAISED RMS,
  //    to reject speaker-bleed) calls bargeIn() — cut the audio + cancel the reply stream — and immediately
  //    starts a fresh capture cycle. Echo-avoidance is preserved WITHOUT pausing a recorder: no recorder runs
  //    during playback, so viv's own voice is never captured as input; the analyser (not a recorder) is what
  //    listens for the interruption.
  // The real feel (does it wait for a finished thought; barge-in sensitivity; iOS audio) is needs-tim.
  function stopAutoListen() {
    autoListenRef.current.stop = true
    autoListenRef.current.stream?.getTracks().forEach(t => t.stop())
    if (voiceReaderRef.current) bargeIn()                      // cut a reply still speaking; no-op (no spurious log) if idle
    setRecording(false); setNotice('')
  }
  async function startAutoListen() {
    primeAudio()                                               // unlock audio in this gesture (V2.1)
    let stream: MediaStream
    try { stream = await navigator.mediaDevices.getUserMedia({ audio: true }) }
    catch { api.voiceLog('mic_denied', { mode: 'auto_listen' }); setNotice('mic unavailable — grant microphone permission'); return }
    autoListenRef.current = { stop: false, stream }
    api.voiceLog('autolisten_start', { input_mode: 'auto_listen', silence_ms: 800, speech_rms: 0.015 })   // session opened (mic granted)
    setRecording(true); setNotice('listening… (tap to stop)')
    // PERSISTENT analyser tap — alive across LISTENING and SPEAKING (the barge-in detector reads it too).
    const ctx = audioCtxRef.current || new (window.AudioContext || (window as any).webkitAudioContext)()
    audioCtxRef.current = ctx
    const analyser = ctx.createAnalyser(); analyser.fftSize = 512
    ctx.createMediaStreamSource(stream).connect(analyser)
    const data = new Uint8Array(analyser.fftSize)
    const SILENCE_MS = 800, SPEECH_RMS = 0.015
    // barge-in is deliberately LESS sensitive than the listen-VAD (higher RMS + sustained frames) so the
    // speaker's own audio bleeding into the mic doesn't false-trigger a cut. These are FEEL parameters —
    // the exact values are Tim's to tune on-device (flagged needs-tim).
    const BARGEIN_RMS = 0.04, BARGEIN_FRAMES = 4

    // read the current RMS off the persistent analyser (0..~1).
    const readRms = () => {
      analyser.getByteTimeDomainData(data)
      let sum = 0; for (let i = 0; i < data.length; i++) { const v = (data[i] - 128) / 128; sum += v * v }
      return Math.sqrt(sum / data.length)
    }

    // ONE LISTEN CYCLE: a FRESH recorder, watch RMS for an end-of-speech pause, transcribe + judge.
    // Resolves with the captured blob+text when a FINISHED thought fires; loops internally (re-arming a
    // fresh recorder) while not-finished; resolves null if the session was stopped. The fresh-recorder-
    // per-cycle is the re-arm fix.
    // FRESH recorder per TURN (not per pause). One continuously-running recorder accumulates the WHOLE
    // turn's audio (so chunk[0] carries the webm header → every snapshot is decodable). On a not-finished
    // pause we SNAPSHOT the accumulated blob WHILE the recorder keeps running (header present) and KEEP
    // listening — so a multi-segment thought ("show me the inbox" … "and then settings") is heard WHOLE,
    // which is the entire point of the finished-thought judge over a dumb silence timer. We only stop()+
    // discard at the TURN boundary: when a thought FIRES (flush the tail, resolve) — the session loop's
    // next listenOnce() then news up the fresh recorder for the next turn (THAT is the cross-turn re-arm
    // fix; the old bug was reusing one recorder ACROSS turns with a reset buffer → headerless turn-2).
    const listenOnce = (): Promise<{ blob: Blob; text: string } | null> => new Promise((resolve) => {
      const chunks: BlobPart[] = []
      const rec = new MediaRecorder(stream)                    // FRESH recorder for THIS turn ⇒ chunk[0] has the header
      rec.ondataavailable = e => { if (e.data && e.data.size) chunks.push(e.data) }
      rec.start(250)                                           // periodic chunks so a snapshot is fresh on a pause
      let spoke = false, lastVoice = performance.now(), busy = false
      const tick = async () => {
        if (autoListenRef.current.stop) {
          try { rec.state !== 'inactive' && rec.stop() } catch {}
          resolve(null); return
        }
        if (!busy && rec.state === 'recording') {
          const rms = readRms(); const now = performance.now()
          if (rms > SPEECH_RMS) { spoke = true; lastVoice = now }
          if (spoke && (now - lastVoice) > SILENCE_MS && chunks.length) {
            busy = true
            api.voiceLog('vad_pause', { silence_ms: Math.round(now - lastVoice), chunks: chunks.length })
            // SNAPSHOT the accumulated utterance-so-far WITHOUT stopping the recorder. chunks[0] holds the
            // webm header (the recorder has run continuously since the turn began), so the snapshot decodes.
            const blob = new Blob(chunks, { type: 'audio/webm' })
            try {
              const r = await api.stt(blob); const text = (r.text || '').trim()
              api.voiceLog('autolisten_stt', { chars: text.length, empty: !text, text: text.slice(0, 200) })
              if (text) {
                const j = await api.finishedThought(text)
                api.voiceLog('autolisten_judge', { verdict: j && j.verdict, finished: !!(j && j.finished), text: text.slice(0, 200) })
                if (j && j.finished) {
                  // FIRE — stop the recorder to FLUSH the tail into a final complete blob, then resolve.
                  const finalBlob: Blob = await new Promise((res) => {
                    rec.onstop = () => res(new Blob(chunks, { type: 'audio/webm' }))
                    try { rec.stop() } catch { res(new Blob(chunks, { type: 'audio/webm' })) }
                  })
                  api.voiceLog('autolisten_fire', { chars: text.length })
                  resolve({ blob: finalBlob, text }); return   // caller speaks the reply, then re-arms (fresh listenOnce)
                }
              }
              // not finished (or empty) → KEEP the recorder running + KEEP the accumulated chunks; just reset
              // the VAD pause-clock so the next pause re-evaluates the (now longer) accumulated thought. This
              // is what makes a multi-segment thought heard WHOLE — we do NOT discard the pre-pause speech.
              if (autoListenRef.current.stop) { try { rec.state !== 'inactive' && rec.stop() } catch {} ; resolve(null); return }
              setNotice(text ? '… go on' : 'listening… (tap to stop)')
              lastVoice = performance.now(); busy = false
            } catch (e: any) {
              try { rec.state !== 'inactive' && rec.stop() } catch {}
              api.voiceLog('error', { where: 'autolisten', error: String(e?.message || e) })
              setNotice('⚠ ' + (e?.message || e) + ' — tap to use push-to-talk')
              resolve(null); return                            // fail loud → operator falls back to push-to-talk
            }
          }
        }
        setTimeout(tick, 150)
      }
      tick()
    })

    // THE SESSION LOOP: listen → fire → SPEAK (with barge-in watch) → re-arm. Runs until the operator stops.
    ;(async () => {
      while (!autoListenRef.current.stop) {
        const fired = await listenOnce()
        if (!fired || autoListenRef.current.stop) break
        setNotice('you said: ' + fired.text); setRecording(false)
        // SPEAK the reply. No recorder runs now (echo-safe). A concurrent barge-in WATCH ticks the analyser;
        // sustained speech cancels the reply (bargeIn) and unblocks immediately so we re-arm at once.
        let watching = true
        const watchBargeIn = async () => {
          let hot = 0
          while (watching && !autoListenRef.current.stop) {
            if (readRms() > BARGEIN_RMS) { if (++hot >= BARGEIN_FRAMES) { bargeIn(); break } }
            else hot = 0
            await new Promise(r => setTimeout(r, 80))
          }
        }
        const watcher = watchBargeIn()
        try { await runVoiceTurn(fired.blob) }                 // streamed persona-voice reply (V2.2)
        catch (e: any) { api.voiceLog('error', { where: 'autolisten_turn', error: String(e?.message || e) }); setNotice('⚠ ' + (e?.message || e)) }
        watching = false; await watcher                        // stop the barge-in watch before re-listening
        if (autoListenRef.current.stop) break
        setRecording(true); setNotice('listening… (tap to stop)')   // RE-ARM — the loop continues to listenOnce()
      }
      // session ended — make sure the mic is released + state cleared.
      stream.getTracks().forEach(t => t.stop()); setRecording(false); setNotice('')
    })()
  }
  // The mic press routes by the configured input mode (V1.3). Push-to-talk → recordToggle (tap/tap).
  // Auto-listen → start a hands-free session, or stop it if one is live. Both unlock audio in the gesture.
  // V1.3 — switch the voice INPUT mode (push_to_talk ↔ auto_listen); persists via the config slot.
  async function setVoiceInputMode(mode: string) {
    if (autoListenRef.current.stream && !autoListenRef.current.stop) stopAutoListen()   // end a live session on switch
    try { const c = await api.setRhmConfig({ voice_input_mode: mode }); setCfg(c); setNotice('voice input → ' + mode.replace('_', '-')) }
    catch (e: any) { setNotice('⚠ ' + (e?.message || e)) }
  }
  // S3/S5 — settings-window config setters. applyRhm sets any rhm_config slot live (stt/tts_engine/
  // tts_voice/persona/brain_knobs/roles…); setModelCtx reconfigures a model's serve-time context window
  // + restarts it (the explicit "set the context window" ask, budget-gated, fail-loud).
  async function applyRhm(updates: any) {
    try { const c = await api.setRhmConfig(updates); setCfg(c); setNotice('config updated') }
    catch (e: any) { setNotice('⚠ ' + (e?.message || e)) }
  }
  async function setBrainKnob(key: string, value: any) {
    await applyRhm({ brain_knobs: { [key]: value } })
  }
  async function setModelCtx(service: string, value: number) {
    try {
      setNotice('setting context window + restarting ' + service + '…')
      const r = await api.modelConfig(service, 'max_model_len', value)
      if (r && r.error) { setNotice('⚠ ' + r.error); return }
      setNotice(service + ' context → ' + value + (r.restarted ? ' (restarted)' : ' (applies on next start)'))
      api.chatModelsDetailed().then(m => setChatModelsX(Array.isArray(m) ? m : [])).catch(() => {})
    } catch (e: any) { setNotice('⚠ ' + (e?.message || e)) }
  }
  // S6 (Tim 2026-06-07) — "if things don't fit from what I've selected, it would tell me." Compute the
  // GPU service keys for the CURRENT selection (the local brain service + the persona's voice engine
  // service `tts-<engine>`), ask /api/fit, and stash the picture for the settings surface to render. Only
  // GPU-resident services count — a cloud/ollama brain has no `service` and contributes nothing to the card.
  async function refreshFit(over?: { model?: string; base_url?: string; persona?: string; tts_engine?: string }) {
    try {
      const model = over?.model ?? cfg.model, base_url = over?.base_url ?? cfg.base_url
      const persona = over?.persona ?? cfg.persona, ttsEngine = over?.tts_engine ?? cfg.tts_engine
      const keys: string[] = []
      const brainRow = chatModelsX.find((r: any) => r.service && r.model === model && r.base_url === base_url)
      if (brainRow?.service) keys.push(brainRow.service)
      const eng = ttsEngine || (personas.find((p: any) => p.id === persona) || {}).engine
      if (eng) keys.push('tts-' + eng)                       // voice engine service key (tts-orpheus, tts-kokoro, …)
      if (!keys.length) { setFitReport(null); return }
      setFitReport(await api.fit(keys))
    } catch { setFitReport(null) /* non-fatal: the surface just hides the fit line */ }
  }
  // Voice fix (Tim 2026-06-07): START a down ear/voice service FROM the interface (an offline ear had no
  // start affordance — "can't start it through the interface"). Budget-gated + fail-loud via /api/model/load
  // (a CPU ear like whisper.cpp costs no VRAM and just starts; a GPU ear that won't fit refuses loudly).
  async function startVoiceService(service: string, label?: string) {
    try {
      setNotice('starting ' + (label || service) + '…')
      const r = await api.modelLoad(service)
      if (r && r.error) { setNotice('⚠ ' + r.error); return }
      setNotice((label || service) + ' starting — give it a moment')
      setTimeout(() => api.voice().then(v => setVoiceInfo(v && typeof v === 'object' ? v : {})).catch(() => {}), 2800)
    } catch (e: any) { setNotice('⚠ ' + (e?.message || e)) }
  }
  // S1 — choose a chat model: set model + its base_url (so a local vLLM model uses its own endpoint), and
  // LOAD its service on demand if it's a company-managed model that's down (budget-gated, like a voice switch).
  async function chooseModel(row: any) {
    if (!row || !row.model) return
    try {
      const c = await api.setRhmConfig({ model: row.model, base_url: row.base_url })
      setCfg(c); setNotice('brain → ' + row.model)
      if (row.service && !row.up) {                          // a local vLLM model that isn't running → load it
        setNotice('loading ' + row.model + ' — cold start…')
        const r = await api.modelLoad(row.service)
        if (r && r.error) { setNotice('⚠ ' + r.error); return }
        setNotice(row.model + ' starting — give it a moment, then talk')
      }
      api.chatModelsDetailed().then(m => setChatModelsX(Array.isArray(m) ? m : [])).catch(() => {})   // refresh up-status
    } catch (e: any) { setNotice('⚠ ' + (e?.message || e)) }
  }
  // S2 — conversation threads (in the RHM): start fresh / list / reopen.
  async function refreshThreads() { try { const t = await api.listConversations(); setThreads(Array.isArray(t) ? t : []) } catch { /* non-fatal */ } }
  async function newConversation() {
    try { const r = await api.newConversation(); setThreadId(r.thread_id || null); setChat([]); setNotice('fresh conversation'); refreshThreads() }
    catch (e: any) { setNotice('⚠ ' + (e?.message || e)) }
  }
  async function openConversation(tid: string) {
    if (!tid) return
    try { const r = await api.loadConversation(tid); setThreadId(r.id || tid); setChat(Array.isArray(r.history) ? r.history : []); setNotice('reopened: ' + (r.title || tid)); refreshThreads() }
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

  // S6: recompute the fit whenever the settings window is open and the selection (brain model / voice
  // persona / engine override) or the picker rows change — so the surface always reflects the live choice.
  useEffect(() => {
    if (!settingsOpen) return
    refreshFit()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [settingsOpen, cfg.model, cfg.base_url, cfg.persona, cfg.tts_engine, chatModelsX.length])

  return {
    // state values (read by the region components)
    edges, running, runError, runStartedAt, runElapsed, types, gname, gspec, surf, growMsg, workshop,
    oinfo, nodeStates, modeDesc, notice, gid, layerView, now, events, chat, chatMsg, chatBusy, cfg, inbox,
    showResolved, drill, reason, lastChange, panels, recording, configTick, session, wtReason, voiceOn, personas,
    // A3/E2-FE · the consolidated Settings surface state
    settingsOpen, settingsTab, roles, voicePaths, voiceStatus, modeRegistry, autodetect, compositionCfg, settingsBusy, settingsErr,
    // main's voice/settings state (S1/S2/S3/S5/S6/V3/V4) — voiceStatus→personaVoiceStatus; settingsOpen already above
    personaVoiceStatus, recordingSession, threads, threadId, chatModelsX, engineKnobs, voiceInfo, fitReport,
    wtSpoke, wtBusy, selected, mobileTab, fleet, indicated, proposal, history, historyBusy,
    addressHelp, addressHelpBusy, addressHelpError, prefBusy,
    selfChanges, selfChangesBusy, freshness, freshnessBusy, versions, versionsBusy, journeyId, journeyReplaying,
    cognitionInfo, cognitionTurn,   // L-fe: the live cognition VIEW state (projection + the folded live turn)
    // G2/C7.4: the cognition-engine HUMAN face (the Settings 'cognition' section) — registry reads + run/create acts
    cogRuns, cogFieldTypes, cogModels, cogInputs, cogBusy, cogErr, cogLastResult,
    refreshCogRuns, runCogRole, createCogRole,
    // refs the components read for the inspector form
    configByNode,
    // setters the components call directly
    setGname, setGspec, setSurf, setWorkshop, setNotice, setCfg, setChatMsg, setShowResolved,
    setDrill, setReason, setWtReason, setVoiceOn, setRunError, setGrowMsg, setMobileTab,
    setSettingsOpen, setSettingsTab,
    // handlers
    poll, openCoa, reload, fitGraph, addNode, wireSelected, doConnect, setNodeConfig, surfaceOutput,
    buildFromOutput, deleteSelected, sendChat, changeMode, cycleLayers, portalSelected,
    resolveUiTarget, startWalk, startGuide, endWalk, respondStep, nextStep, dispatch, recordToggle, fieldValue,
    setField, revertLast, revertSelfChangeAt, approveApply, doRun, refreshFleet, indicate, clickMode, annotateLocus, mintBuildIntent, setPresentationPrefAt,
    pointedSet, togglePointed, clearPointed,
    approveProposal, dismissProposal, steerProposal, deferProposal, setAsideProposal, reviveOffer, toggleJourneyRecording, replayJourney, switchPersona,
    // A3/E2-FE · the consolidated Settings handlers
    openSettings, loadSettingsData, setCfgSlot,
    // main's voice/settings handlers (S1/S2/S3/S5/S6/V3/V4 + the indicate-mode toggle); setSettingsOpen already returned above
    micPressed, setVoiceInputMode, setVoiceEnabled, toggleRecordConversation, startDebriefSession, newConversation, openConversation, chooseModel, applyRhm, setBrainKnob, setModelCtx, refreshFit, startVoiceService,
    indicateMode, toggleIndicateMode,
    // REVIEW WORKSPACE / STUDIO — the mockup-studio organ folded into the main app (the scaffolded surface)
    reviewMockup, setReviewMockup, reviewAddress,
    corpus, corpusErr, refreshCorpus,
    annotations, annotationsBusy, fetchAnnotations,
    // GENERATE FOLLOW-ON — the studio "generate" step (the committed engine wired to the surface)
    mockupGenerate, generateBusy, generateResult,
  }
}

export type AppController = ReturnType<typeof useAppController>
