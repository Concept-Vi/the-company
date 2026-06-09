// A3 (settings consolidated) + E2-FE/GC3 (the mode surface) · THE CONSOLIDATED SETTINGS SURFACE.
//
// WHAT THIS IS: the ONE designed place every config slot lives together — modes, models, personas, the RHM
// config, voice — so the operator configures the Company from a single coherent surface instead of the
// scattered gear-in-the-chat + dial-in-the-toolbar (A3: "consolidated, not scattered"). It is a full-viewport
// modal (the Workshop pattern — position:fixed, outside the grid, covers everything) so it works IDENTICALLY
// on desktop and phone (no competition for the bottom-sheet slots; phone gets a full-screen scroll), and is
// navigable-by-sight (a left rail of sections + kit Surfaces, never a text-wall) — the H2 commander's-bridge
// language, built from the shared kit (SectionHead/LaneHead/Badge/Surface) + var() tokens ONLY.
//
// THE FOLD (MERGE-PLAN §2.7 — main's S3/S5/S6 functional pieces folded INTO the A3 sections, re-skinned to the
// kit/tokens so nothing of main's capability is lost and it all reads as ONE surface):
//   · Brain & persona  ← local-vLLM model rows with LOAD-ON-PICK (chatModelsX + chooseModel) · temperature +
//                         max-tokens (setBrainKnob) · context-window set-and-restart (setModelCtx) ·
//                         the resource-fit bar (fitReport + refreshFit) at the top of the section.
//   · Voice            ← per-engine TTS knobs (engineKnobs) · ear status + START a down ear (voiceInfo +
//                         startVoiceService) · listening style push-to-talk/auto-listen (setVoiceInputMode).
// The voice on/off control is NOT duplicated — A3's VoiceSection already owns it (the voice_enabled SELECT);
// main's "speak replies aloud" checkbox is CONVERGED away (rule 3, one source). Conversation threads (S2) stay
// in RhmChat (a chat concern), NOT folded here. Every transplanted control rides an EXISTING controller handler
// over an EXISTING endpoint (chooseModel→/api/model/load · setBrainKnob/setModelCtx · startVoiceService→
// /api/model/load · setVoiceInputMode→/api/rhm-config) — REUSE, never a new write path.
//
// REUSE, NEVER REBUILD (the lane law): every WRITE rides an EXISTING controller handler over an EXISTING
// endpoint. Every READ is registry-truth off an EXISTING endpoint (/api/rhm-config · /api/personas · /api/roles ·
// /api/voice · /api/voice/paths · /api/capabilities · /api/chat-models · /api/voice/engine-knobs · /api/fit). NO
// new config endpoint, NO parallel config state. The legacy RhmChat gear stays working (forbidden file); this
// surface SUPERSEDES it as the consolidated home — a follow-up (allowed to touch RhmChat) retires the gear.
//
// THE MODE SURFACE (E2-FE/GC3): renders capabilities().mode_registry as a HIERARCHY — each of the ≤8 top-level
// modes with its directive (behaviour) + its per-mode-type context-RESOLUTION declaration (strata/howto_detail/
// budget — the "modes-and-context-resolution-are-ONE-system" made visible) + its sub-types + its consent style.
// The mode is SWITCHABLE here (changeMode). The off/suggest/auto AUTO-DETECT toggle renders its LIVE value and
// is live-settable (GC6/E2-live) through the SAME config path (setCfgSlot → set_rhm_config).
import { useState } from 'react'
import { useApp } from '../AppContext'
import { SectionHead, Badge, Surface, EmptyState } from '../components/kit'
import { getMODEL_OPTIONS } from '../registryStore'

// the section spine — recognition-by-sight: an icon + a name per section, the left rail of the surface.
const SECTIONS: { id: 'brain' | 'modes' | 'voice' | 'roles' | 'composition' | 'cognition'; icon: string; name: string; blurb: string }[] = [
  { id: 'brain', icon: '◈', name: 'Brain & persona', blurb: 'the model that thinks · the voice that speaks · the fit' },
  { id: 'modes', icon: '◐', name: 'Modes', blurb: 'presence + how context resolves under each' },
  { id: 'voice', icon: '🎙', name: 'Voice', blurb: 'the ear, the engine, the path' },
  { id: 'roles', icon: '⚖', name: 'Model roles', blurb: 'the model-function bindings (judge + more)' },
  { id: 'composition', icon: '⚙', name: 'Composition', blurb: 'the context-ranking knobs (read)' },
  // G2/C7.4 · the cognition-engine HUMAN face — author a role (direct, no approval), run a role, see runs.
  { id: 'cognition', icon: '⚒', name: 'Cognition', blurb: 'author a role · run a role · see the runs (the engine, on the surface)' },
]

export function Settings() {
  const {
    settingsOpen, settingsTab, setSettingsTab, setSettingsOpen, settingsBusy, settingsErr,
    cfg, now, personas, modeDesc, fleet, roles, voicePaths, voiceStatus, modeRegistry, autodetect, compositionCfg,
    chatModelsX, engineKnobs, voiceInfo, fitReport,
    switchPersona, changeMode, setCfgSlot,
    chooseModel, setBrainKnob, setModelCtx, setVoiceInputMode, startVoiceService,
    // G2/C7.4 · the cognition-engine HUMAN face state + acts (registry reads + run/create — reflects-never-owns)
    cogRuns, cogFieldTypes, cogModels, cogInputs, cogBusy, cogErr, cogLastResult,
    refreshCogRuns, runCogRole, createCogRole, cognitionInfo,
  } = useApp()
  if (!settingsOpen) return null
  const curMode = now?.mode || cfg?.mode || 'listening'
  // the FULL model registry (B2 — incl :cloud models) the role-binding select offers, exactly as the keeper
  // did. The Brain section uses chatModelsX instead (the detailed rows that carry load-on-pick) — that swap is
  // the §2.7 fold; Roles stays on the full registry so cloud models remain bindable to a role.
  const chatModels: string[] = getMODEL_OPTIONS().chat_models || fleet.chat || []

  return (
    // the full-viewport modal scrim + panel (Workshop pattern). The panel is deliberately NOT given
    // data-ui-ref="ui://settings" — that address is already CARRIED by the Toolbar's ⚙ settings button
    // (Toolbar.tsx, the keeper's chosen carrier per MERGE-PLAN §2.6), and resolveUiTarget resolves by
    // querySelector (first DOM match wins), so a second carrier here would make ui://settings ambiguous
    // while the modal is open. One address, one carrier (the launching button). The close button keeps
    // its own ui://settings/close (sole carrier, §3a).
    <div className="settings-scrim" onClick={() => setSettingsOpen(false)}>
      <div className="settings-panel" onClick={e => e.stopPropagation()} role="dialog" aria-label="Settings">
        {/* the masthead — the surface's title + the close */}
        <div className="settings-masthead">
          <SectionHead tag="the company · control" aside={
            <button className="b ghost sm" data-ui-ref="ui://settings/close" onClick={() => setSettingsOpen(false)} title="close settings">✕ close</button>
          }>Settings</SectionHead>
          {settingsErr && <Surface tone="fail"><span className="set-err">⚠ {settingsErr}</span></Surface>}
        </div>
        <div className="settings-body">
          {/* the SECTION RAIL — navigable by sight (icon + name), one section active. On phone this becomes a
             horizontal scroll strip (CSS). */}
          <nav className="settings-rail">
            {SECTIONS.map(s => (
              <button key={s.id} type="button"
                className={'settings-navitem' + (settingsTab === s.id ? ' on' : '')}
                onClick={() => setSettingsTab(s.id)} title={s.blurb}>
                <span className="settings-navicon">{s.icon}</span>
                <span className="settings-navtext"><span className="settings-navname">{s.name}</span>
                  <span className="settings-navblurb">{s.blurb}</span></span>
              </button>
            ))}
          </nav>
          {/* the active section's content */}
          <div className="settings-content">
            {settingsBusy && <span className="muted set-loading">loading registries…</span>}
            {settingsTab === 'brain' && <BrainSection cfg={cfg} chatModelsX={chatModelsX} personas={personas} fitReport={fitReport} setCfgSlot={setCfgSlot} switchPersona={switchPersona} chooseModel={chooseModel} setBrainKnob={setBrainKnob} setModelCtx={setModelCtx} />}
            {settingsTab === 'modes' && <ModesSection curMode={curMode} modeDesc={modeDesc} modeRegistry={modeRegistry} autodetect={autodetect} changeMode={changeMode} setCfgSlot={setCfgSlot} />}
            {settingsTab === 'voice' && <VoiceSection cfg={cfg} voiceStatus={voiceStatus} voiceInfo={voiceInfo} engineKnobs={engineKnobs} personas={personas} voicePaths={voicePaths} setCfgSlot={setCfgSlot} setVoiceInputMode={setVoiceInputMode} startVoiceService={startVoiceService} />}
            {settingsTab === 'roles' && <RolesSection roles={roles} chatModels={chatModels} cfg={cfg} setCfgSlot={setCfgSlot} />}
            {settingsTab === 'composition' && <CompositionSection compositionCfg={compositionCfg} />}
            {settingsTab === 'cognition' && <CognitionSection cognitionInfo={cognitionInfo} cogRuns={cogRuns} cogFieldTypes={cogFieldTypes} cogModels={cogModels} cogInputs={cogInputs} cogBusy={cogBusy} cogErr={cogErr} cogLastResult={cogLastResult} refreshCogRuns={refreshCogRuns} runCogRole={runCogRole} createCogRole={createCogRole} />}
          </div>
        </div>
      </div>
    </div>
  )
}

// — RESOURCE FIT (S6, folded in §2.7) — "will THIS selection (brain + voice) fit the 16GB card?" A bar Tim
// reads by SHAPE (each GPU piece's share of the ceiling) + the honest live verdict (measured free) + when it
// won't fit, WHY + what to unload. Re-skinned to the kit: a Surface (tone sig=fits / fail=won't) holding a
// segmented bar built from tokens only. The segment WIDTHS are computed values (a live %, not a px/hex literal)
// so they stay inline; the colours are the .fit-seg-n token classes. Lives at the TOP of Brain (a `fit` rail
// tab would need the settingsTab union widened in useAppController.ts — lane C's file — so it rides Brain).
function FitBar({ fitReport }: any) {
  const f = fitReport
  if (!f || !f.items || !f.items.length) return null
  const ceil = f.ceiling_mb || 16376
  const ok = f.fits_now
  const pct = (mb: number) => Math.min(100, (mb / ceil) * 100)
  const totalPct = Math.min(100, (f.need_mb / ceil) * 100)
  const gb = (mb: number) => (mb / 1024).toFixed(1)
  const gpuItems = f.items.filter((i: any) => i.gpu)
  return (
    <>
      <SectionHead tag="resource fit" aside={<Badge tone={ok ? 'sig' : 'fail'}>{ok ? 'fits the card' : 'won’t fit together'}</Badge>}>The card</SectionHead>
      <Surface tone={ok ? 'sig' : 'fail'}>
        <div className="fit-bar" title={gb(f.need_mb) + ' GB needed of ' + gb(ceil) + ' GB card'}>
          {gpuItems.map((i: any, n: number) => (
            <span key={i.key} className={'fit-seg fit-seg-' + (n % 4)} style={{ width: pct(i.mb) + '%' }}
              title={i.key + ' · ' + gb(i.mb) + ' GB'}>{pct(i.mb) > 12 ? i.key.replace(/^(tts|chat)-/, '') : ''}</span>
          ))}
          <span className="fit-free" style={{ width: Math.max(0, 100 - totalPct) + '%' }} />
        </div>
        <div className="fit-line">
          {gpuItems.map((i: any) => i.key + ' ' + gb(i.mb) + ' GB').join('  +  ')}
          {'  =  '}<b>{gb(f.need_mb)} GB</b> of {gb(ceil)} GB card
        </div>
        {!ok && (
          <div className="fit-why">
            won’t fit right now — needs {gb(f.need_now_mb)} GB, {gb(f.free_mb)} GB free.
            {f.evict && f.evict.length ? ' Unload to make room: ' + f.evict.join(', ') + '.' : ' Pick a lighter voice or a smaller brain context.'}
          </div>
        )}
        {ok && !f.fits_card && (
          <div className="fit-why">loads now, but the two together exceed the card’s ceiling — close to the edge.</div>
        )}
      </Surface>
    </>
  )
}

// — BRAIN & PERSONA — the conscious model + its knobs + the switchable cast (+ the fit bar at the top). WRITE:
// chooseModel (model picker + load-on-pick) · setBrainKnob (temperature/max-tokens) · setModelCtx (context
// window, restarts the local service) · setCfgSlot('base_url'|'timeout') · switchPersona.
function BrainSection({ cfg, chatModelsX, personas, fitReport, setCfgSlot, switchPersona, chooseModel, setBrainKnob, setModelCtx }: any) {
  const [ctx, setCtx] = useState<string>('')
  const bk = cfg?.brain_knobs || {}
  // the currently-selected row (so the context-window control only shows for a local vLLM model that has a service)
  const localRow = chatModelsX.find((r: any) => r.service && r.model === cfg?.model && r.base_url === cfg?.base_url)
  const modelIdx = chatModelsX.findIndex((r: any) => r.model === cfg?.model && (r.base_url === cfg?.base_url || !r.base_url))
  return (
    <div className="settings-section" data-ui-ref="ui://settings/brain">
      {/* S6 fit bar (folded) — only renders when a fit picture is available (a GPU brain/voice is selected) */}
      <FitBar fitReport={fitReport} />

      <SectionHead tag="conscious role">The brain</SectionHead>
      <Surface tone="sig">
        {/* MODEL — folded from main's S1: the rows include local vLLM models, and picking one that's down
           LOADS it on demand (chooseModel → /api/model/load), budget-gated + fail-loud. */}
        <label className="set-field">
          <span className="set-label">Model <span className="muted">· the model the RHM thinks with · a local one cold-loads on pick</span></span>
          <select className="set-select" value={String(modelIdx)}
            onChange={e => { const i = Number(e.target.value); if (chatModelsX[i]) chooseModel(chatModelsX[i]) }}>
            <option value="-1">{cfg?.model || 'fabric default'} (current)</option>
            {chatModelsX.map((r: any, i: number) => (
              <option key={i} value={String(i)}>{r.model}{r.service ? (r.up ? ' · local' : ' · local ⏻') : ''}</option>
            ))}
          </select>
        </label>
        <label className="set-field">
          <span className="set-label">Temperature <span className="muted">· sampling spread (0 = deterministic)</span></span>
          <input className="set-input" type="number" step={0.1} min={0} max={2} defaultValue={bk.temperature ?? 0.7}
            onBlur={e => setBrainKnob('temperature', e.target.value)} />
        </label>
        <label className="set-field">
          <span className="set-label">Max output tokens <span className="muted">· cap on a single reply's length</span></span>
          <input className="set-input" type="number" min={1} defaultValue={bk.max_tokens ?? 1024}
            onBlur={e => setBrainKnob('max_tokens', e.target.value)} />
        </label>
        {localRow && (
          <label className="set-field">
            <span className="set-label">Context window <span className="muted">· restarts {localRow.service} to apply</span></span>
            <div className="set-ctx-row">
              <input className="set-input" type="number" min={1024} step={1024} placeholder="e.g. 32768"
                value={ctx} onChange={e => setCtx(e.target.value)} />
              <button className="b sm" onClick={() => { const v = Number(ctx); if (v) setModelCtx(localRow.service, v) }}>set &amp; restart</button>
            </div>
          </label>
        )}
        <label className="set-field">
          <span className="set-label">Endpoint <span className="muted">· the provider base URL</span></span>
          <input className="set-input" type="text" defaultValue={cfg?.base_url || ''} placeholder="http://localhost:11434/v1"
            onBlur={e => { const v = e.target.value.trim(); if (v && v !== cfg?.base_url) setCfgSlot('base_url', v) }} />
        </label>
        <label className="set-field">
          <span className="set-label">Reply timeout <span className="muted">· seconds the interactive RHM call may take</span></span>
          <input className="set-input" type="number" min={1} defaultValue={cfg?.timeout ?? 180}
            onBlur={e => { const v = parseInt(e.target.value, 10); if (v > 0 && v !== cfg?.timeout) setCfgSlot('timeout', v) }} />
        </label>
      </Surface>

      <SectionHead tag="the cast" aside={<Badge tone="dim">{personas.length} personas</Badge>}>Persona</SectionHead>
      {personas.length === 0
        ? <EmptyState>No personas registered — the voice cast loads from voice/personas.py.</EmptyState>
        : <div className="set-persona-grid">
            {personas.map((p: any) => {
              const active = p.id === cfg?.persona
              return (
                <Surface key={p.id} tone={active ? 'sig' : undefined} interactive onClick={() => !active && switchPersona(p.id)}
                  title={active ? 'active persona' : 'switch to ' + p.name + ' (cold-loads their voice)'}>
                  <div className="set-persona-head">
                    <span className="set-persona-name">{p.name}</span>
                    {active && <Badge tone="sig">active</Badge>}
                  </div>
                  <div className="set-persona-meta">{p.shading}</div>
                  <div className="set-persona-engine muted">voice engine · {p.engine}</div>
                </Surface>
              )
            })}
          </div>}
    </div>
  )
}

// — MODES (E2-FE/GC3) — the hierarchical mode type-registry + the auto-detect toggle. The mode is SWITCHABLE
// (changeMode — takes live). Each mode shows directive (behaviour) + resolution (HOW context resolves) +
// sub-types + consent. The off/suggest/auto toggle is LIVE-SETTABLE through the EXISTING config path.
function ModesSection({ curMode, modeDesc, modeRegistry, autodetect, changeMode, setCfgSlot }: any) {
  const modes = modeRegistry ? Object.entries(modeRegistry) : []
  const adValue = autodetect?.value || 'off'
  return (
    <div className="settings-section" data-ui-ref="ui://settings/modes">
      <SectionHead tag="presence" aside={<Badge tone="sig">{curMode}</Badge>}>Modes</SectionHead>
      <p className="set-prose">A mode is presence AND how context resolves under it — one system. Selecting a mode switches it live.</p>

      <Surface tone="sig">
        <div className="set-autodetect-head">
          <span className="set-label">Mode auto-detect</span>
          <Badge tone="sig">{adValue}</Badge>
        </div>
        <div className="set-autodetect-opts">
          {(autodetect?.options || ['off', 'suggest', 'auto']).map((o: string) => (
            <button key={o} type="button"
              className={'set-pill' + (o === adValue ? ' on' : '')}
              onClick={() => o !== adValue && setCfgSlot('MODE_AUTODETECT', o)}
              title={o === adValue ? 'current auto-detect mode' : 'set auto-detect → ' + o}>{o}</button>
          ))}
        </div>
        <div className="muted set-note">off = manual only · suggest = propose a mode · auto = switch automatically.
          Selecting an option sets it live (persists across reload).</div>
      </Surface>

      {modes.length === 0
        ? <EmptyState>Mode registry not loaded — capabilities().mode_registry is the source.</EmptyState>
        : <div className="set-modes-list">
            {modes.map(([id, m]: any) => {
              const active = id === curMode
              const res = m.resolution
              const subs = m.subtypes ? Object.keys(m.subtypes) : []
              return (
                <Surface key={id} tone={active ? 'sig' : 'dim'} interactive onClick={() => !active && changeMode(id)}
                  title={active ? 'current presence' : 'switch to ' + (m.label || id)}>
                  <div className="set-mode-head">
                    <span className="set-mode-name">{m.label || id}</span>
                    <span className="set-mode-tags">
                      {active && <Badge tone="sig">active</Badge>}
                      <Badge tone="dim">consent: {m.consent || 'none'}</Badge>
                    </span>
                  </div>
                  <div className="set-mode-directive">{m.directive || modeDesc[id] || ''}</div>
                  <div className="set-mode-resolution">
                    {res
                      ? <span className="muted">context · detail <b>{res.howto_detail || 'full'}</b>
                          {res.budget != null && <> · budget <b>{res.budget}</b></>}
                          {res.strata != null
                            ? <> · strata <b>{Array.isArray(res.strata) ? res.strata.join(', ') : String(res.strata)}</b></>
                            : <> · strata <b>all</b></>}</span>
                      : <span className="muted">context · admit-all (no resolution override)</span>}
                  </div>
                  {subs.length > 0 && (
                    <div className="set-mode-subs">
                      <span className="muted">sub-types:</span>
                      {subs.map(st => <span key={st} className="set-pill sm">{st}</span>)}
                    </div>
                  )}
                </Surface>
              )
            })}
          </div>}
    </div>
  )
}

// — VOICE — the ear (STT), the engine (TTS) + its per-engine knobs, the listening style, the path. WRITE:
// setCfgSlot('stt'|'tts_engine'|'tts_voice'|'voice_path'|'voice_enabled') · setVoiceInputMode (listening
// style) · startVoiceService (start a down ear). s2s renders UNAVAILABLE (G-19), never as working.
//
// THE FOLD (§2.7): per-engine TTS knobs (engineKnobs — under the selected engine), ear status + START a down
// ear (voiceInfo carries per-ear up/down + the ear's service → startVoiceService), and listening style
// (push-to-talk / auto-listen via setVoiceInputMode) are folded in. The voice on/off control is NOT
// duplicated — A3's voice_enabled SELECT below is the single source (main's checkbox converged away, rule 3).
function VoiceSection({ cfg, voiceStatus, voiceInfo, engineKnobs, personas, voicePaths, setCfgSlot, setVoiceInputMode, startVoiceService }: any) {
  const sttRegistry = voiceStatus?.stt_registry || voiceStatus?.stt || {}
  const sttIds = Object.keys(sttRegistry)
  const engines = Array.isArray(voiceStatus?.engines) ? voiceStatus.engines : []
  const paths = voicePaths?.paths ? Object.values(voicePaths.paths) : []
  // the engine whose per-engine knobs to show: the explicit override, else the active persona's engine.
  const curEngine = cfg?.tts_engine || (personas.find((p: any) => p.id === cfg?.persona) || {}).engine || ''
  const engineRows = (engineKnobs && engineKnobs[curEngine]) || []
  // ear status (folded from main): voiceInfo.stt carries the per-ear up/down bool; stt_registry[id].service is
  // the unit to start a down ear with. Read voiceInfo (not voiceStatus) — it's the one carrying the live status.
  const selStt = cfg?.stt || ''
  const earStat = (voiceInfo && voiceInfo.stt && selStt) ? voiceInfo.stt[selStt] : undefined
  const earReg = (voiceInfo && voiceInfo.stt_registry && selStt) ? voiceInfo.stt_registry[selStt] : null
  const earSvc = earReg && earReg.service
  return (
    <div className="settings-section" data-ui-ref="ui://settings/voice">
      <SectionHead tag="listening" aside={<Badge tone={cfg?.voice_enabled === 'off' ? 'dim' : 'sig'}>{cfg?.voice_enabled === 'off' ? 'voice off' : 'voice on'}</Badge>}>Voice</SectionHead>

      <Surface>
        <label className="set-field">
          <span className="set-label">Voice for this mode</span>
          <select className="set-select" value={cfg?.voice_enabled || 'on'} onChange={e => setCfgSlot('voice_enabled', e.target.value)}>
            <option value="on">on — speaks back in listening</option>
            <option value="off">off — text-only even with engines up</option>
          </select>
        </label>
        {/* listening style (folded §2.7): push-to-talk vs hands-free auto-listen */}
        <label className="set-field">
          <span className="set-label">Listening style <span className="muted">· how the mic opens</span></span>
          <select className="set-select" value={cfg?.voice_input_mode || 'push_to_talk'} onChange={e => setVoiceInputMode(e.target.value)}>
            <option value="push_to_talk">🎙 push-to-talk</option>
            <option value="auto_listen">👂 auto-listen (hands-free)</option>
          </select>
        </label>
        <label className="set-field">
          <span className="set-label">Ear (STT) <span className="muted">· the speech-to-text provider</span></span>
          {sttIds.length === 0
            ? <div className="set-static muted">no STT provider registry (voice may be absent)</div>
            : <select className="set-select" value={selStt} onChange={e => setCfgSlot('stt', e.target.value)}>
                {sttIds.map(id => <option key={id} value={id}>{id}</option>)}
              </select>}
        </label>
        {/* ear status + START a down ear (folded §2.7): only shown once we know the ear's up/down state */}
        {earStat !== undefined && (
          earStat
            ? <div className="set-ear-status on">● {selStt} online</div>
            : <div className="set-ear-status down">
                ✕ {selStt} offline — {earReg && earReg.detail ? earReg.detail : 'not running'}
                {earSvc && <button className="b sm set-ear-start" onClick={() => startVoiceService(earSvc, selStt)}>▶ start</button>}
              </div>
        )}
      </Surface>

      <SectionHead tag="speaking">TTS engines</SectionHead>
      {engines.length === 0
        ? <EmptyState>No TTS engines reporting — start a voice service via the company console.</EmptyState>
        : <div className="set-engines">
            {engines.map((e: any) => {
              const sel = (cfg?.tts_engine || '') === e.engine
              return (
                <Surface key={e.engine} tone={e.up ? (sel ? 'sig' : undefined) : 'dim'} interactive
                  onClick={() => e.up && setCfgSlot('tts_engine', sel ? '' : e.engine)}
                  title={e.up ? (sel ? 'active TTS override — click to clear (use persona default)' : 'use ' + e.engine) : e.engine + ' is not up'}>
                  <div className="set-engine-head">
                    <span className="set-engine-name">{e.engine}</span>
                    {sel ? <Badge tone="sig">selected</Badge> : <Badge tone={e.up ? 'await' : 'dim'}>{e.up ? 'up' : 'down'}</Badge>}
                  </div>
                  <div className="muted set-engine-voices">{(e.voices && e.voices.length) ? e.voices.length + ' voice(s)' : 'no voices reported'}</div>
                </Surface>
              )
            })}
          </div>}
      <Surface>
        <label className="set-field">
          <span className="set-label">Voice argument <span className="muted">· an optional voice/speaker override for the engine</span></span>
          <input className="set-input" type="text" defaultValue={cfg?.tts_voice || ''} placeholder="(persona default)"
            onBlur={e => { const v = e.target.value.trim(); if (v !== (cfg?.tts_voice || '')) setCfgSlot('tts_voice', v) }} />
        </label>
        <div className="muted set-note">An empty engine + empty voice argument use the persona's own engine + voice.</div>
      </Surface>

      {/* per-engine TTS knobs (folded §2.7): the selected engine's own serve/live knob rows */}
      {engineRows.length > 0 && (
        <>
          <SectionHead tag="engine knobs" aside={<Badge tone="dim">{curEngine}</Badge>}>Engine knobs</SectionHead>
          <Surface>
            {engineRows.map((k: any) => (
              <div key={k.key} className="set-knob-row">
                <span className="set-knob-key">{k.key}</span>
                <span className="muted set-knob-note">{k.scope === 'serve' ? 'serve · ' : 'live · '}{k.note}</span>
              </div>
            ))}
          </Surface>
        </>
      )}

      <SectionHead tag="circuit">Voice path</SectionHead>
      {paths.length === 0
        ? <EmptyState>Voice-path registry not loaded.</EmptyState>
        : <div className="set-paths">
            {paths.map((p: any) => {
              const sel = (cfg?.voice_path || 'pipeline') === p.id
              const usable = p.available
              return (
                <Surface key={p.id} tone={sel ? 'sig' : usable ? undefined : 'dim'} interactive={usable}
                  onClick={() => usable && !sel && setCfgSlot('voice_path', p.id)}
                  title={usable ? (sel ? 'active path' : 'switch to ' + p.label) : p.label + ' — unavailable: ' + (p.detail || p.note || '')}>
                  <div className="set-path-head">
                    <span className="set-path-name">{p.label}</span>
                    {sel ? <Badge tone="sig">active</Badge> : usable ? <Badge tone="dim">available</Badge> : <Badge tone="fail">unavailable</Badge>}
                  </div>
                  <div className="muted set-path-note">{p.note}</div>
                  {!usable && p.detail && <div className="set-path-detail muted">⚠ {p.detail}</div>}
                </Surface>
              )
            })}
          </div>}
    </div>
  )
}

// — ROLES — the model-FUNCTION role registry (judge + future). Each role binds a model. WRITE: setCfgSlot
// ('roles', {<id>:{model}}) — the backend deep-merges, so binding one role never wipes a sibling.
function RolesSection({ roles, chatModels, cfg, setCfgSlot }: any) {
  const ids = roles ? Object.keys(roles) : []
  const bindings = cfg?.roles || {}
  return (
    <div className="settings-section" data-ui-ref="ui://settings/roles">
      <SectionHead tag="model functions" aside={<Badge tone="dim">{ids.length} role(s)</Badge>}>Model roles</SectionHead>
      <p className="set-prose">Each role is a model-function the system binds a model to — distinct from the conscious brain.</p>
      {ids.length === 0
        ? <EmptyState>Role registry not loaded — GET /api/roles is the source.</EmptyState>
        : ids.map((id: string) => {
            const r = roles[id]
            const bound = bindings[id]?.model || r.binding?.model || ''
            const unbound = !r.binding || !r.binding.model
            return (
              <Surface key={id} tone={unbound ? 'await' : 'sig'} dataUiRef={'ui://settings/role/' + id}>
                <div className="set-role-head">
                  <span className="set-role-name">{r.label || id}</span>
                  {unbound ? <Badge tone="await">unbound</Badge> : <Badge tone="sig">bound</Badge>}
                </div>
                <div className="set-role-desc muted">{r.description}</div>
                {r.recommended_model && <div className="set-role-rec muted">recommended · {r.recommended_model}</div>}
                <label className="set-field">
                  <span className="set-label">Bind model</span>
                  <select className="set-select" value={bound}
                    onChange={e => setCfgSlot('roles', { [id]: { model: e.target.value } })}>
                    <option value="">— unbound (falls to the brain) —</option>
                    {chatModels.map((m: string) => <option key={m} value={m}>{m}</option>)}
                    {bound && !chatModels.includes(bound) && <option value={bound}>{bound} (current)</option>}
                  </select>
                </label>
              </Surface>
            )
          })}
    </div>
  )
}

// — COMPOSITION — the context-ranking knobs (X17). READ-ONLY (env-tuned; no live setter — surfaced honestly).
function CompositionSection({ compositionCfg }: any) {
  const cc = compositionCfg || {}
  const rows = Object.entries(cc).filter(([k]) => k.startsWith('R2_'))
  return (
    <div className="settings-section" data-ui-ref="ui://settings/composition">
      <SectionHead tag="context ranking">Composition knobs</SectionHead>
      <p className="set-prose muted">The R2 context-ranking weights + budget. Env-tuned at boot (COMPANY_R2_*) — read here, no live setter yet.</p>
      {rows.length === 0
        ? <EmptyState>Composition config not loaded.</EmptyState>
        : <div className="set-knobs">
            {rows.map(([k, v]: any) => (
              <Surface key={k} className="set-knob">
                <span className="set-knob-name">{k.replace('R2_', '').toLowerCase().replace(/_/g, ' ')}</span>
                <span className="set-knob-val">{typeof v === 'number' ? v : String(v)}</span>
              </Surface>
            ))}
          </div>}
    </div>
  )
}

// — COGNITION — the cognition-engine HUMAN face (G2 + C7.4). The operator does, on the surface, what the MCP
// agent does: AUTHOR a role (direct, no approval — C7.4/A1), RUN a role (G2 "do" — fire it, see the run://
// output), and SEE the runs (G2 "see" — the run-index). reflects-never-owns: every select PROJECTS from a
// registry read the controller already loaded (cogModels/cogFieldTypes/cogInputs — registry-is-truth, rule 8:
// a new model/field-type/input appears here with ZERO form edit) and every act calls an EXISTING /api/cognition/*
// route (the SAME Suite methods the MCP face calls — one composition surface, G3).
//
// THE FLOOR (AGENTS rule 9 + criteria A1/A4): create_role is DECLARATIVE-DIRECT — it applies LIVE with NO
// approval step (over-gating it with a fake "surfaced for approval" would VIOLATE A1). run_role is COMPUTATION
// (produces a run:// output + op.run telemetry; NEVER resolve/approve/dispatch). The role EDIT/DELETE +
// rule ATTACH/DETACH paths SURFACE for approval and stay the RHM's — this section does direct-create only, and
// node-type/code create (the GATED tier) is NOT here. So the surface emits no floor act.
//
// FORM: built on the shared kit (SectionHead/Badge/Surface/EmptyState) + the existing .set-* form classes +
// design tokens ONLY (no bespoke hex/px) — graded separately by the design-critic (the implementer cannot
// self-certify FORM, AGENTS rule 9). The output-schema authoring (nested objects / list[dict] — Group B2) is
// NOT built here: this form authors the role's IDENTITY + binding + inputs; the rich schema editor is a deeper
// pass. Flagged so it reads as honest scope, never green-painted.
function CognitionSection({ cognitionInfo, cogRuns, cogFieldTypes, cogModels, cogInputs, cogBusy, cogErr, cogLastResult, refreshCogRuns, runCogRole, createCogRole }: any) {
  // the role registry the run-a-role select offers — projected from the live cognition projection (rule 8: a
  // role authored here, or registered engine-side, appears with zero FE edit). roleMeta carries label/op/trigger.
  const roleMeta: Record<string, any> = cognitionInfo?.roles || {}
  const roleIds = Object.keys(roleMeta)
  // RUN-A-ROLE local form state (kept LOCAL — the controller owns only the data + the acts, not the draft).
  const [runRole, setRunRole] = useState('')
  const [runUtterance, setRunUtterance] = useState('')
  const [runModel, setRunModel] = useState('')
  // CREATE-A-ROLE local form state (the role's identity + op + directive). The op is the real engine op axis
  // (generate|embed) the engine dispatches on. We post ONLY ROLE_FIELDS-contract keys (see doCreate) — an
  // unknown key fails loud, so the form holds back to the proven-safe set; the deeper authoring is flagged.
  const [newId, setNewId] = useState('')
  const [newLabel, setNewLabel] = useState('')
  const [newOp, setNewOp] = useState('generate')
  const [newPrompt, setNewPrompt] = useState('')

  function doCreate() {
    // The spec shape is the ROLE_FIELDS contract (runtime/roles.py:71 + runtime/authoring.py render_role_source) —
    // read from the contract, NOT inferred (rule 8): the accepted keys are id · label · description ·
    // prompt_template · output_fields · op · input_addresses · mode_scope · trigger · rules · model_binding · …
    // An UNKNOWN key FAILS LOUD backend-side (authoring.py:156 — never a silent typo'd field). So we emit ONLY
    // proven keys:
    //   • prompt_template (NOT 'prompt') — the directive; its presence ⇒ the role can FIRE.
    //   • op = generate|embed (a real ROLE_FIELDS key, the engine dispatches on it).
    //   • input_addresses = ['utterance'] — the proven-safe input (the docstring's example). The richer input
    //     wiring (run://<turn>/<role>, context://<var>, vec://…#space=<proj>) the input vocabulary advertises is
    //     a DEEPER pass — those are address TEMPLATES, not directly-postable spec values, so binding them here
    //     would risk a fail-loud 400. Flagged in the form, not green-painted.
    //   • model is NOT a ROLE_FIELDS key (binding is `model_binding`/legacy `default_model`) AND create_role
    //     does NOT strip it from the spec (suite.py:8576) — so passing it would FAIL LOUD. The created role
    //     binds to the swarm default; per-role model binding is the deeper model_binding concern. Omitted here.
    const spec: any = { id: newId.trim(), label: newLabel.trim() || newId.trim(), op: newOp, input_addresses: ['utterance'] }
    if (newPrompt.trim()) spec.prompt_template = newPrompt.trim()
    createCogRole(spec)
  }

  return (
    <div className="settings-section" data-ui-ref="ui://settings/cognition">
      <SectionHead tag="the engine, on the surface"
        aside={<Badge tone="dim">{roleIds.length} role(s)</Badge>}>Cognition</SectionHead>
      <p className="set-prose muted">The same composition the agent does, on your surface — author a role (applied live, no approval), run a role, and see the runs. Every select reads the live registry; nothing here is hardcoded.</p>
      {cogErr && <Surface tone="fail"><span className="set-err">⚠ {cogErr}</span></Surface>}

      {/* ── AUTHOR A ROLE (C7.4) — direct-create, applied LIVE, no approval (A1). ───────────────────────── */}
      <div className="cog-block">
        <SectionHead tag="C7.4 · declarative-direct, no approval">Author a role</SectionHead>
        <label className="set-field">
          <span className="set-label">Role id</span>
          <input className="set-input" value={newId} placeholder="e.g. repo_digest" onChange={e => setNewId(e.target.value)} />
        </label>
        <label className="set-field">
          <span className="set-label">Label</span>
          <input className="set-input" value={newLabel} placeholder="(defaults to the id)" onChange={e => setNewLabel(e.target.value)} />
        </label>
        <label className="set-field">
          <span className="set-label">Op</span>
          {/* the two engine ops the dispatcher routes on (generate|embed); registry-truth would widen this from
             a capability registry — flagged as the deeper B5 pass, not green-painted here. */}
          <select className="set-select" value={newOp} onChange={e => setNewOp(e.target.value)}>
            <option value="generate">generate</option>
            <option value="embed">embed</option>
          </select>
        </label>
        <label className="set-field">
          <span className="set-label">Directive (prompt_template)</span>
          <input className="set-input" value={newPrompt} placeholder="You are … — the role's directive (its presence makes the role fire)" onChange={e => setNewPrompt(e.target.value)} />
        </label>
        {/* HONEST SCOPE (no green-paint): this form authors the role's IDENTITY + op + directive + the proven-safe
           'utterance' input, posting ONLY ROLE_FIELDS keys the contract accepts (an unknown key fails loud). The
           DEEPER pass (not built here): per-role model binding (model_binding), the richer INPUT wiring
           (run://<turn>/<role> · context://<var> · vec://…#space — address templates the input vocabulary
           advertises), and the structured output-schema editor (output_fields → BaseModel; field types: the list
           below). These read from the live registry so they're build-ready, but they are not wired into this form. */}
        {(cogFieldTypes.length > 0 || cogModels.length > 0 || cogInputs.length > 0) && (
          <p className="set-prose muted cog-hint">
            Deeper authoring available from the live registry (not in this form yet):
            {cogModels.length > 0 && <> model binding ({cogModels.length} models),</>}
            {cogInputs.length > 0 && <> input wiring ({cogInputs.length} addresses),</>}
            {cogFieldTypes.length > 0 && <> output-schema field types ({cogFieldTypes.join(' · ')}).</>}
          </p>
        )}
        <div className="cog-actions">
          <button className="b" onClick={doCreate} disabled={cogBusy || !newId.trim()}
            title="create this role — applied LIVE, no approval (declarative-direct); a malformed spec is refused fail-loud, never written">
            {cogBusy ? 'working…' : 'create role (live)'}
          </button>
        </div>
      </div>

      {/* ── RUN A ROLE (G2 "do") — fire ONE role; see its run:// output. COMPUTATION, not a floor act. ──── */}
      <div className="cog-block">
        <SectionHead tag="G2 · computation (no approve/dispatch)">Run a role</SectionHead>
        <label className="set-field">
          <span className="set-label">Role</span>
          <select className="set-select" value={runRole} onChange={e => setRunRole(e.target.value)}>
            <option value="">— pick a role —</option>
            {roleIds.map((id: string) => <option key={id} value={id}>{roleMeta[id]?.label || id}</option>)}
          </select>
        </label>
        <label className="set-field">
          <span className="set-label">Model (optional)</span>
          <select className="set-select" value={runModel} onChange={e => setRunModel(e.target.value)}>
            <option value="">— the role's bound model —</option>
            {cogModels.map((m: string) => <option key={m} value={m}>{m}</option>)}
          </select>
        </label>
        <label className="set-field">
          <span className="set-label">Utterance</span>
          <input className="set-input" value={runUtterance} placeholder="what the role works on" onChange={e => setRunUtterance(e.target.value)} />
        </label>
        <div className="cog-actions">
          <button className="b" onClick={() => runCogRole({ role: runRole, utterance: runUtterance, model: runModel })}
            disabled={cogBusy || !runRole}
            title="fire this role → its run:// output. computation only — it never approves or dispatches anything">
            {cogBusy ? 'running…' : 'run role'}
          </button>
        </div>
        {cogLastResult && (
          // the last act's outcome — the run:// address / created id, read by sight (fail-loud already surfaced via cogErr).
          <Surface tone="sig" className="cog-result">
            <div className="cog-result-head">
              <Badge tone="sig">{cogLastResult.kind === 'create' ? 'created' : 'ran'}</Badge>
              {cogLastResult.address && <span className="cog-result-addr">{cogLastResult.address}</span>}
              {cogLastResult.role_id && <span className="cog-result-addr">role: {cogLastResult.role_id}{cogLastResult.path ? ' → ' + cogLastResult.path : ''}</span>}
            </div>
            {(cogLastResult.output != null) && (
              <div className="cog-result-out muted">{typeof cogLastResult.output === 'string' ? cogLastResult.output.slice(0, 600) : JSON.stringify(cogLastResult.output).slice(0, 600)}</div>
            )}
          </Surface>
        )}
      </div>

      {/* ── SEE THE RUNS (G2 "see") — the run-index tail, a navigable list (each run a card, not a text line). */}
      <div className="cog-block">
        <SectionHead tag="G2 · the run index"
          aside={<button className="b ghost sm" onClick={() => refreshCogRuns()} title="re-probe the run index">↻</button>}>Runs</SectionHead>
        {cogRuns.length === 0
          ? <EmptyState>No runs yet — run a role above (or fire a staged turn). The run-index is the source.</EmptyState>
          : cogRuns.map((r: any, i: number) => (
              // each run is a kit Surface card carrying its run:// address (data-ui-ref so the locus is addressable).
              <Surface key={r.address || r.seq || i} tone="dim" className="cog-run" dataUiRef={r.address}>
                <div className="cog-run-head">
                  <span className="cog-run-role">{r.role || r.run_op || r.op || 'run'}</span>
                  {r.duration_ms != null && <Badge tone="dim">{r.duration_ms}ms</Badge>}
                </div>
                <div className="cog-run-meta muted">
                  {r.address && <span className="cog-run-addr">{r.address}</span>}
                  {r.op && <span> · {r.op}</span>}
                  {r.ts && <span> · {String(r.ts).slice(0, 19)}</span>}
                </div>
              </Surface>
            ))}
      </div>
    </div>
  )
}
