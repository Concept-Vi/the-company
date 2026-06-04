// F0 (carved from App.tsx:1598–1633) · the right-hand-man chat region. data-ui-ref="chat" preserved.
// PRESERVE-LIST: voice push-to-talk (the mic → recordToggle). The gold/working grading + the model/persona
// gear are carved verbatim. (F7 will swap the free-text model input for a registry <select>; F0 keeps it.)
import { useApp } from '../AppContext'

export function RhmChat() {
  const { cfg, cfgOpen, chat, chatBusy, chatMsg, recording, setCfg, setCfgOpen, setChatMsg, applyCfg, sendChat, recordToggle } = useApp()
  return (
    <div className="hud rhm" data-ui-ref="chat">
      <div className="rhm-head">
        right-hand-man <span className="muted">· {cfg.model || 'default model'}</span>
        <span className="cfg-gear" title="configure model + persona" onClick={() => setCfgOpen(o => !o)}>⚙</span>
      </div>
      {cfgOpen && (
        <div className="rhm-cfg">
          <input placeholder="model (e.g. deepseek-v4-flash:cloud)" value={cfg.model || ''}
            onChange={e => setCfg({ ...cfg, model: e.target.value })} />
          <input placeholder="persona / voice (optional)" value={cfg.persona || ''}
            onChange={e => setCfg({ ...cfg, persona: e.target.value })} />
          <button className="b" onClick={applyCfg}>apply config</button>
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
        <input placeholder="ask the company about itself…" value={chatMsg}
          onChange={e => setChatMsg(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter') sendChat() }} />
        <button className={'b ghost mic' + (recording ? ' rec' : '')} onClick={recordToggle}
          title="push-to-talk (voice in; speaks back in listening mode)">{recording ? '■' : '🎙'}</button>
        <button className="b" onClick={() => sendChat()} disabled={chatBusy}>{chatBusy ? '…' : '→'}</button>
      </div>
    </div>
  )
}
