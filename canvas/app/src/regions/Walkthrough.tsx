// F0 (carved from App.tsx:1274–1330) · the WALKTHROUGH CARD — the visible review organ. Shown only while a
// session is active. data-ui-ref="walkthrough" preserved. Wrapped in PanelErrorBoundary by the shell so a
// bad item degrades to a contained card. PRESERVE-LIST: wtBusyRef concurrency guards (every respond control
// + Next disabled while a request is in flight — one click = one verdict), voice/text toggle, the per-step
// resolveUiTarget drive (in the controller effect), operator-only verdicts (→ /api/resolve through the gate).
import { useApp } from '../AppContext'

export function Walkthrough() {
  const { session, voiceOn, wtReason, wtBusy, wtSpoke, setVoiceOn, setWtReason, endWalk, resolveUiTarget, respondStep, nextStep } = useApp()
  if (!session) return null
  return (
    <div className="hud walkthrough" data-ui-ref="walkthrough">
      <div className="wt-head">
        <span className="wt-title">walkthrough</span>
        <span className="wt-mode" data-ui-ref="ui://walkthrough/voice">
          <button className={voiceOn ? 'on' : ''} onClick={() => setVoiceOn(true)} title="voice-first: speak each step">🔊 voice</button>
          <button className={!voiceOn ? 'on' : ''} onClick={() => setVoiceOn(false)} title="text only">text</button>
        </span>
        <span className="wt-prog">{session.done ? 'complete' : `${(session.cursor ?? 0) + 1} of ${session.total}`}</span>
        <span className="close" style={{ cursor: 'pointer', color: 'var(--dim)' }} title="leave the walk (the session stays server-side)"
          onClick={endWalk}>✕</span>
      </div>
      {session.done ? (
        <div className="wt-done">✓ walk complete — {session.total} item(s) reviewed. Verdicts are recorded; the
          build loop reads them on its next fire (approved→done · new-ask→a new criterion · rejected→requeued · skipped→still pending).
          <div style={{ marginTop: 10 }}><button className="b ghost" onClick={endWalk}>close</button></div>
        </div>
      ) : (
        <>
          {/* S7b: framing is fail-safe — if the coa LLM errored the backend returns the raw payload; we
             still show SOMETHING (the note / the item id), the walk never blocks. */}
          <div className="wt-frame">{session.framing || (session.raw?.payload?.note) || ('Review item: ' + session.item + ' (no framing returned — raw payload below)')}</div>
          {session.raw?.ui_target && <div className="wt-target">concerns: {session.raw.ui_target}
            <button className="b ghost sm" data-ui-ref="ui://walkthrough/show-again" style={{ marginLeft: 8 }} title="move the view to this thing again"
              onClick={() => resolveUiTarget(session.raw.ui_target)}>↪ show again</button></div>}
          <input className="wt-reason" data-ui-ref="ui://walkthrough/reason" placeholder="why? (captured into the verdict — required for reject/comment)"
            value={wtReason} onChange={e => setWtReason(e.target.value)} />
          {/* CONCURRENCY GUARD: every respond control is disabled while a request is in flight (wtBusy) —
             one click = one verdict; the .wt-busy class dims them so the lock is visible during the ~20s wait. */}
          <div className={'wt-respond' + (wtBusy ? ' wt-busy' : '')} data-ui-ref="ui://walkthrough/verdict">
            <button className="b verdict approve" disabled={wtBusy} onClick={() => respondStep('approve')} title="approve this item">✓ approve</button>
            <button className="b ghost verdict reject" disabled={wtBusy} onClick={() => respondStep('reject')} title="reject (give a reason)">✕ reject</button>
            <button className="b ghost verdict" disabled={wtBusy} onClick={() => respondStep('comment')} title="comment — capture a note, stays pending">✎ comment</button>
            <button className="b ghost verdict" disabled={wtBusy} onClick={() => respondStep('skip')} title="skip — still needs you later">⤼ skip</button>
            <button className="b ghost verdict" disabled={wtBusy} onClick={() => respondStep('decide')} title="let the system decide (deterministic, by consequence)">⚖ decide</button>
          </div>
          <div className="wt-foot">
            {wtBusy
              ? <span className="wt-resolved">⏳ working… (framing can take a moment)</span>
              : session._responded
                ? <span className="wt-resolved">✓ responded: {session._responded}</span>
                : <span className="muted">respond, then advance</span>}
            {/* Next disabled while a /api/review/next (or any respond) request is pending — a 2nd click
               mid-flight would issue a concurrent next that desyncs the backend cursor. */}
            <button className="b" data-ui-ref="ui://walkthrough/next" style={{ marginLeft: 'auto' }} disabled={wtBusy} onClick={nextStep} title="advance to the next step">{wtBusy ? '…' : 'next →'}</button>
            {wtSpoke && <span className="wt-spoke">{wtSpoke}</span>}
          </div>
        </>
      )}
    </div>
  )
}
