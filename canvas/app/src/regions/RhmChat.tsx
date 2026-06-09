// F0 (carved from App.tsx:1598–1633) · the right-hand-man chat region. data-ui-ref="chat" preserved.
// PRESERVE-LIST: voice push-to-talk (the mic → recordToggle). The gold/working grading is carved verbatim.
//
// L4-GEAR-RETIRE (unify-wave2, Tim's builder's-call — state.json TIM_DECISIONS_2026-06-07 #4: "retire the old
// scattered settings gear, keep the consolidated Settings"). The RhmChat `.rhm-cfg` ⚙ config panel
// (ui://chat/config) is RETIRED — it duplicated config that now lives ONE place in the A3 consolidated Settings
// (opened from the Toolbar ⚙ settings): the model picker (chatModelsX/chooseModel → A3 Brain), persona switch
// (switchPersona → A3 Brain), the voice load-status badge (personaVoiceStatus), the voice INPUT mode
// (setVoiceInputMode → A3 Voice), and the voice ON/OFF toggle (setVoiceEnabled — A3 VoiceSection's
// `voice_enabled` SELECT is the SINGLE source now, rule 3: voice on/off no longer lives twice). All of those
// are gone from here; the A3 Settings is their single home. The chat header no longer carries the ⚙ gear.
//
// KEPT chat-LOCAL (no A3 equivalent — genuinely a chat concern):
//   · conversation threads (S2: + new / reopen) — `.rhm-threads`, the new-conversation control reads the SAME
//     thread state (newConversation/openConversation/threads/threadId); a backend fix made +new start FRESH.
//   · the record / debrief memory loop (V3) — pulled OUT of the retired gear into a small standalone chat
//     control (`.rhm-mem`); it has no A3 section, so it stays here per the lane brief.
//   · minimize (ui://chat/minimize) — collapse to the header so the canvas shows behind (independent of the
//     gear; kept).
import { useState } from 'react'
import { useApp } from '../AppContext'
import { ProposeAffordance } from './ProposeAffordance'

export function RhmChat({ studio = false }: { studio?: boolean } = {}) {
  // `studio` (Tim 2026-06-09): in the design-REVIEW surface the operator is a non-developer reviewing a
  // mockup — so canvas-oriented dev affordances (the model name, the twin record/debrief controls) are
  // noise that read as "development stuff." This prop hides them in the studio ONLY; the canvas mount
  // (default studio=false) is byte-unchanged. The real chat organ, threads, locus + input are kept in both.
  const { cfg, chat, chatBusy, chatMsg, recording, indicated, recordingSession, threads, threadId, setChatMsg, sendChat, recordToggle, micPressed, toggleRecordConversation, startDebriefSession, newConversation, openConversation, indicate } = useApp()
  // minimize — collapse the chat to just its header so the canvas is visible behind it (esp. on mobile,
  // where the panel otherwise fills the screen). A plain in-component toggle; the body is hidden via the
  // `.rhm.min` CSS, the header (with the restore button) stays.
  const [min, setMin] = useState(false)
  return (
    <div className={'hud rhm' + (min ? ' min' : '')} data-ui-ref="chat">
      <div className="rhm-head">
        right-hand-man {!studio && <span className="muted">· {cfg.model || 'default model'}</span>}
        <span className="rhm-min" data-ui-ref="ui://chat/minimize" title={min ? 'expand the chat' : 'minimize — see the canvas'} onClick={() => setMin(m => !m)}>{min ? '▢' : '▁'}</span>
      </div>
      {/* S2 — conversation threads: start fresh + reopen a previous one. Lives in the RHM (Tim, chat-local). */}
      <div className="rhm-threads">
        <button className="b ghost" data-ui-ref="ui://chat/new-conversation" title="start a fresh conversation" onClick={newConversation}>+ new</button>
        <select data-ui-ref="ui://chat/threads" value={threadId || ''} title="reopen a previous conversation"
          onChange={e => e.target.value && openConversation(e.target.value)}>
          <option value="">{threads.length ? 'reopen a conversation…' : '(no past conversations)'}</option>
          {threads.map((t: any) => <option key={t.id} value={t.id}>{t.title || t.id}</option>)}
        </select>
      </div>
      {/* V3 — the memory loop: record this conversation as a trial session, then debrief over the recorded
          sessions (reuses the walkthrough organ). Chat-LOCAL: no A3 equivalent, so it stays here (lifted OUT
          of the retired .rhm-cfg gear into this small standalone control). */}
      {!studio && (
      <div className="rhm-mem">
        <button className={'b ghost' + (recordingSession ? ' rec' : '')} data-ui-ref="ui://chat/record"
          title="record this conversation as a session (so it can be debriefed + feeds the twin)"
          onClick={toggleRecordConversation}>{recordingSession ? '■ stop recording' : '● record'}</button>
        <button className="b ghost" data-ui-ref="ui://chat/debrief"
          title="walk back through the recorded sessions (debrief)"
          onClick={startDebriefSession}>debrief</button>
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
        <input placeholder="ask me to change anything you see" data-ui-ref="ui://chat/input" value={chatMsg}
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
