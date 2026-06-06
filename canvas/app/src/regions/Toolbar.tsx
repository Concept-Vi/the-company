// F0 (carved from App.tsx:1331–1371) · the toolbar region. data-ui-ref="toolbar" preserved.
// U1 PRESERVE: the RUN button is `onClick={() => doRun()}` (arrow-wrapped) + the retry is too — NEVER
// `onClick={doRun}` (that passes React's MouseEvent as `force` and re-introduces the canvas-RUN latch).
import { MODES } from '../api'
import { useApp } from '../AppContext'

export function Toolbar() {
  const {
    now, running, chatBusy, runElapsed, runError, modeDesc, layerView, notice,
    doRun, changeMode, wireSelected, portalSelected, deleteSelected, cycleLayers, fitGraph, reload, setRunError, startGuide,
  } = useApp()
  return (
    <div className="hud toolbar" data-ui-ref="toolbar">
      <span className="title">the&nbsp;<em>company</em></span>
      {now && (
        <span className={'presence ' + (now.mode === 'off' ? 'off' : running || chatBusy ? 'busy' : now.surfaced_pending ? 'warn' : 'ok')}>
          <span className="pdot" />{running ? `running… ${runElapsed}s` : chatBusy ? 'thinking…' : now.presence}
        </span>
      )}
      {/* U4: a legible, recoverable run-error surface — shows the failure + a retry, right where RUN is.
         Clears on the next successful run (doRun sets runError=null at entry). */}
      {runError && !running && (
        <span className="run-err" title={runError}>
          ✕ run failed
          <button className="b sm" style={{ marginLeft: 6 }} onClick={() => doRun()} title="retry the run">↻ retry</button>
          <button className="b ghost sm" style={{ marginLeft: 4 }} onClick={() => setRunError(null)} title="dismiss">✕</button>
        </span>
      )}
      {now && (
        // U11: the dropdown's title shows the CURRENT mode's description; each option carries its own.
        <select className="mode-sel" data-ui-ref="ui://toolbar/presence" value={now.mode || 'listening'} onChange={e => changeMode(e.target.value)}
          title={'presence dial · ' + (now.mode || 'listening') + ' — ' + (modeDesc[now.mode || 'listening'] || '')}>
          {MODES.map(m => <option key={m} value={m} title={modeDesc[m] || ''}>{m}</option>)}
        </select>
      )}
      {/* U11: an always-visible one-line description of the active mode. */}
      {now && <span className="mode-desc" title={modeDesc[now.mode || 'listening'] || ''}>{modeDesc[now.mode || 'listening'] || ''}</span>}
      {/* U1 (load-bearing fix): wrap in an arrow so React's MouseEvent is NOT passed as `force`.
         Passing the event made `force.join(', ')` (doRun) throw a synchronous TypeError BEFORE the try{,
         so `finally{ setRunning(false) }` never ran and api.run() never fired → button latched until
         reload. `() => doRun()` → force is undefined → the normal-run branch POSTs /api/run. */}
      <button className="b" data-ui-ref="ui://toolbar/run" onClick={() => doRun()} disabled={running}>{running ? 'running…' : '▶ run'}</button>
      <button className="b ghost" data-ui-ref="ui://toolbar/wire" onClick={wireSelected}>＋ wire</button>
      <button className="b ghost" data-ui-ref="ui://toolbar/portal" onClick={portalSelected}>⊕ portal</button>
      <button className="b ghost" data-ui-ref="ui://toolbar/delete" onClick={deleteSelected}>🗑 delete</button>
      <button className="b ghost" data-ui-ref="ui://toolbar/layers" onClick={cycleLayers}>◐ layers: {['all', 'origin', 'system'][layerView]}</button>
      {/* U6: fit the graph with padding for the fixed panels so nothing tucks under the chrome */}
      <button className="b ghost" data-ui-ref="ui://toolbar/fit" onClick={fitGraph} title="zoom to fit — padded so no node hides under the panels">⊡ fit</button>
      <button className="b ghost" data-ui-ref="ui://toolbar/reload" onClick={reload}>reload</button>
      {/* C1: the operator entry to the SYSTEM-INITIATED guided sequence ("show me how" tour). Steps through
         the interface's addressed elements, narrating each from its corpus how-to + spotlighting it.
         NOTE: deliberately carries NO ui:// data-ui-ref — ui://toolbar/guide is not yet a registered corpus
         address (design/_system/addresses.json is owned by the corpus lane, file-disjoint), and the orphan
         check (ui_registry_acceptance) forbids an unregistered data-ui-ref. Flagged as a grown gap: register
         ui://toolbar/guide in the corpus so the guide control itself becomes an addressable/guidable element. */}
      <button className="b ghost" onClick={() => startGuide()} title="show me how — a guided tour of the interface, spotlighting each part with its how-to">? guide</button>
      {/* C2: the BOOTSTRAP entry — the FIRST thing show-me teaches is HOW TO REQUEST A CHANGE AND APPROVE IT
         FROM INSIDE (point → ask → surface → approve), wiring the operator into self-modifying the Company.
         Same C1 guided-sequence machinery, the 'request-a-change' topic: it spotlights the real wire-door +
         inbox + approve elements (indicating an element first so the door MOUNTS) and narrates the flow.
         The wire-blue tint ties it to the wire's signature colour (the door + the inbox build lane). Same
         NO-data-ui-ref note as ? guide (ui://toolbar/teach not yet a corpus address — flagged grown gap). */}
      <button className="b ghost kit-tone-wire" onClick={() => startGuide('request-a-change')}
        title="teach me to self-modify — a guided walk of requesting a change and approving it from inside the interface (point → ask → surface → approve)">⚙ teach me to self-modify</button>
      {notice && <span className="notice">{notice}</span>}
    </div>
  )
}
