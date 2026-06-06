// F0 (carved from App.tsx:1598–1633) · the right-hand-man chat region. data-ui-ref="chat" preserved.
// PRESERVE-LIST: voice push-to-talk (the mic → recordToggle). The gold/working grading + the model/persona
// gear are carved verbatim.
// F6 (RHM model dropdown): the model field is a REGISTRY <select> fed from the SAME live source the
// node-config model field uses — MODEL_OPTIONS.chat_models (B2 registry, set at boot in useAppController
// from api.models('chat'); node configs reach it via options_from→getMODEL_OPTIONS). The RHM is a chat
// surface, so chat_models is the correct slice. Read reactively via useSyncExternalStore (registryStore's
// documented React read, registryStore.ts:6–8) so the list populates the instant boot lands MODEL_OPTIONS —
// no dependency on render-timing, and no touch to useAppController (F7's file). The control mirrors
// NodeConfigForm's select structure (NodeConfigForm.tsx:23–28): no-silent-drop of a saved-but-unregistered
// value, an empty-registry fallback, plus the RHM-specific empty "default model" state (cfg.model === '' is
// VALID — line "{cfg.model || 'default model'}" — so a leading empty option preserves it). The rhm-config
// write path is UNCHANGED (setCfg → applyCfg) and data-ui-ref="ui://chat/model-field" is preserved (F4).
import { useSyncExternalStore } from 'react'
import { useApp } from '../AppContext'
import { registryStore } from '../registryStore'
import { ProposeAffordance } from './ProposeAffordance'

export function RhmChat() {
  const { cfg, cfgOpen, chat, chatBusy, chatMsg, recording, indicated, personas, voiceStatus, switchPersona, setCfg, setCfgOpen, setChatMsg, applyCfg, sendChat, recordToggle, micPressed, setVoiceInputMode, setVoiceEnabled, indicate } = useApp()
  // the live chat-model registry — same source the node-config model dropdown reads (MODEL_OPTIONS.chat_models).
  const registry = useSyncExternalStore(registryStore.subscribe, registryStore.getSnapshot)
  const chatModels = registry.MODEL_OPTIONS.chat_models || []
  const curModel = cfg.model || ''
  return (
    <div className="hud rhm" data-ui-ref="chat">
      <div className="rhm-head">
        right-hand-man <span className="muted">· {cfg.model || 'default model'}</span>
        <span className="cfg-gear" data-ui-ref="ui://chat/config" title="configure model + persona" onClick={() => setCfgOpen(o => !o)}>⚙</span>
      </div>
      {cfgOpen && (
        <div className="rhm-cfg">
          {/* V4.1 — the consolidated voice & brain settings home: brain model, persona+voice, input mode,
              voice on/off — one place, all live, legible on mobile. */}
          <div className="cfg-head">voice &amp; brain</div>
          <select data-ui-ref="ui://chat/model-field" value={curModel}
            onChange={e => setCfg({ ...cfg, model: e.target.value })}>
            {/* empty is a VALID state — "default model" (cfg.model || 'default model' in the head). */}
            <option value="">default model</option>
            {/* surface a saved-but-unregistered value rather than silently dropping it (fail-loud, mirrors NodeConfigForm). */}
            {curModel !== '' && !chatModels.includes(curModel) && <option value={curModel}>{curModel} (current)</option>}
            {chatModels.length === 0 && <option value="" disabled>(no registered chat models)</option>}
            {chatModels.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
          {/* Option A — switch between the cast: selecting a persona sets it active AND auto-loads its
              voice (evicting the previous one to fit the card; a switch may cold-load). The notice tracks
              progress to 'ready'. */}
          <select data-ui-ref="ui://chat/persona-field" value={cfg.persona || ''}
            title="switch persona — loads that voice (the card holds one at a time, so a switch cold-loads)"
            onChange={e => switchPersona(e.target.value)}>
            <option value="">(choose a persona)</option>
            {personas.map((p: any) => <option key={p.id} value={p.id}>{p.name} · {p.engine}</option>)}
            {cfg.persona && !personas.some((p: any) => p.id === cfg.persona) &&
              <option value={cfg.persona}>{cfg.persona} (current)</option>}
          </select>
          {/* V4.2 — the voice load status: a switch may cold-load the engine; show loading→ready so the
              operator knows when they can talk (not just a transient notice). */}
          {voiceStatus && <span className={'voice-status ' + voiceStatus}
            title={'voice engine: ' + voiceStatus}>
            {voiceStatus === 'loading' ? '⏳ loading voice…' : voiceStatus === 'ready' ? '✓ voice ready' : '⚠ voice down'}
          </span>}
          {/* V1.3 — the voice INPUT mode: two distinct capabilities, switchable. push-to-talk (tap to
              start/stop) or auto-listen (speak; it fires the turn when you finish a thought — the judge,
              not a dumb timer). Persists via the voice_input_mode slot; takes effect on the next mic press. */}
          <select data-ui-ref="ui://chat/input-mode" value={cfg.voice_input_mode || 'push_to_talk'}
            title="how the mic finalises a turn — push-to-talk (tap to stop) or auto-listen (stops when you finish a thought)"
            onChange={e => setVoiceInputMode(e.target.value)}>
            <option value="push_to_talk">🎙 push-to-talk</option>
            <option value="auto_listen">👂 auto-listen (hands-free)</option>
          </select>
          {/* V4.3 — global voice output on/off (the voice_enabled slot), independent of mode. */}
          <label className="cfg-toggle" data-ui-ref="ui://chat/voice-toggle"
            title="speak replies aloud — off = text replies only">
            <input type="checkbox" checked={(cfg.voice_enabled || 'on') === 'on'}
              onChange={e => setVoiceEnabled(e.target.checked)} />
            <span>{(cfg.voice_enabled || 'on') === 'on' ? '🔊 voice on' : '🔇 voice off'}</span>
          </label>
          <button className="b" data-ui-ref="ui://chat/config" onClick={applyCfg}>apply config</button>
        </div>
      )}
      <div className="rhm-log">
        {chat.length === 0 && <div className="muted">ask about the system — it answers from live state, and says so when it can't see something.</div>}
        {chat.map((t, i) => (
          <div key={i} className={'msg ' + t.role}>
            <span className="who">{t.role === 'user'
              ? <>you<span className="grade gold" title="gold — Tim's own words (trains the twin)">◆</span></>
              : <>vi<span className="grade working" title="working-grade — the twin's inference, not ground truth">◇</span></>}
            </span>
            <span className="txt">{t.text}</span>
          </div>
        ))}
        {chatBusy && <div className="msg assistant"><span className="who">vi</span><span className="txt muted">thinking…</span></div>}
      </div>
      {/* I1 · click-to-indicate: when the operator has clicked an addressed element, a chip shows the
          indicated locus (their next message is about it) + a clear (✕). NB: NO data-ui-ref on the chip
          or its ✕ — they are not addressed loci themselves (clicking one must not re-indicate the chip). */}
      {indicated && (
        <div className="rhm-indicating" title="your next message is about this element">
          <span className="ic">⌖</span>
          <span className="ind-addr">{indicated}</span>
          <button className="ind-clear" onClick={() => indicate(null)} title="stop indicating">✕</button>
        </div>
      )}
      {/* I3 · propose-affordance: when the RHM PROPOSES an action, the approvable card renders here —
          the action runs ONLY when the operator approves it (the consent gate, click #2). */}
      <ProposeAffordance />
      <div className="rhm-input">
        <input placeholder="ask the company about itself…" data-ui-ref="ui://chat/input" value={chatMsg}
          onChange={e => setChatMsg(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') sendChat() }} />
        <button className={'b ghost mic' + (recording ? ' rec' : '')} data-ui-ref="ui://chat/mic" onClick={micPressed}
          title={(cfg.voice_input_mode || 'push_to_talk') === 'auto_listen'
            ? (recording ? 'auto-listen on — tap to stop' : 'auto-listen — tap to start hands-free; it replies when you finish a thought')
            : 'push-to-talk — tap to start, tap to stop'}>{recording ? '■' : ((cfg.voice_input_mode || 'push_to_talk') === 'auto_listen' ? '👂' : '🎙')}</button>
        <button className="b" data-ui-ref="ui://chat/send" onClick={() => sendChat()} disabled={chatBusy}>{chatBusy ? '…' : '→'}</button>
      </div>
    </div>
  )
}
