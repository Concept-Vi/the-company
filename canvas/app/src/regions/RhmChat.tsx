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

export function RhmChat() {
  const { cfg, cfgOpen, chat, chatBusy, chatMsg, recording, setCfg, setCfgOpen, setChatMsg, applyCfg, sendChat, recordToggle } = useApp()
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
          <select data-ui-ref="ui://chat/model-field" value={curModel}
            onChange={e => setCfg({ ...cfg, model: e.target.value })}>
            {/* empty is a VALID state — "default model" (cfg.model || 'default model' in the head). */}
            <option value="">default model</option>
            {/* surface a saved-but-unregistered value rather than silently dropping it (fail-loud, mirrors NodeConfigForm). */}
            {curModel !== '' && !chatModels.includes(curModel) && <option value={curModel}>{curModel} (current)</option>}
            {chatModels.length === 0 && <option value="" disabled>(no registered chat models)</option>}
            {chatModels.map(m => <option key={m} value={m}>{m}</option>)}
          </select>
          <input placeholder="persona / voice (optional)" value={cfg.persona || ''}
            onChange={e => setCfg({ ...cfg, persona: e.target.value })} />
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
      <div className="rhm-input">
        <input placeholder="ask the company about itself…" data-ui-ref="ui://chat/input" value={chatMsg}
          onChange={e => setChatMsg(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') sendChat() }} />
        <button className={'b ghost mic' + (recording ? ' rec' : '')} data-ui-ref="ui://chat/mic" onClick={recordToggle}
          title="push-to-talk (voice in; speaks back in listening mode)">{recording ? '■' : '🎙'}</button>
        <button className="b" data-ui-ref="ui://chat/send" onClick={() => sendChat()} disabled={chatBusy}>{chatBusy ? '…' : '→'}</button>
      </div>
    </div>
  )
}
