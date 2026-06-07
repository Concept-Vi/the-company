// S3/S5 — the dedicated SETTINGS window. A modal (full-screen on mobile, the design-system surface) that
// consolidates the MAIN configurations of whatever's loaded: brain (model · temperature · max-tokens ·
// context window), voice input (ear · listening style · speak on/off), voice output (persona · engine ·
// voice · the engine's own knobs). Quick presets still live in the RHM; this is the config bench. Reflects-
// never-owns: reads cfg + the catalogs, POSTs changes via the controller handlers, reads back. data-ui-ref.
import { useState } from 'react'
import { useApp } from '../AppContext'
import { PanelErrorBoundary } from '../components/PanelErrorBoundary'

export function Settings() {
  const { settingsOpen, setSettingsOpen, cfg, chatModelsX, personas, engineKnobs, voiceInfo, fitReport,
          chooseModel, switchPersona, setBrainKnob, setModelCtx, applyRhm, setVoiceInputMode, setVoiceEnabled, startVoiceService } = useApp()
  const [ctx, setCtx] = useState<string>('')
  if (!settingsOpen) return null
  const bk = cfg.brain_knobs || {}
  const localRow = chatModelsX.find((r: any) => r.service && r.model === cfg.model && r.base_url === cfg.base_url)
  const curEngine = cfg.tts_engine || (personas.find((p: any) => p.id === cfg.persona) || {}).engine || ''
  const engineRows = (engineKnobs && engineKnobs[curEngine]) || []
  const reg = voiceInfo && voiceInfo.stt_registry
  const ears: string[] = Array.isArray(reg) ? reg.map((e: any) => e.id || e.provider || e) : (reg ? Object.keys(reg) : [])
  const modelIdx = chatModelsX.findIndex((r: any) => r.model === cfg.model && (r.base_url === cfg.base_url || !r.base_url))
  return (
    <PanelErrorBoundary>
      <div className="settings" data-ui-ref="ui://settings">
        <div className="settings-head">settings
          <span className="close" data-ui-ref="ui://settings/close" title="close" onClick={() => setSettingsOpen(false)}>✕</span>
        </div>
        <div className="settings-body">
          {fitReport && fitReport.items && fitReport.items.length > 0 && (() => {
            // S6 — the fit-surface: does THIS selection (brain + voice) fit the 16GB card? A bar Tim reads by
            // shape (each piece's share + the ceiling line) + the honest live verdict (measured free), and
            // when it won't fit, WHY + what to unload. The live answer is fits_now (measured); fits_card is
            // the capacity ceiling. Lead with the live one — it's what actually loads right now.
            const f = fitReport, ceil = f.ceiling_mb || 16376
            const ok = f.fits_now, pct = (mb: number) => Math.min(100, (mb / ceil) * 100)
            const totalPct = Math.min(100, (f.need_mb / ceil) * 100)
            const gb = (mb: number) => (mb / 1024).toFixed(1)
            return (
              <section className={'settings-sec settings-fit ' + (ok ? 'fit-ok' : 'fit-over')}>
                <h4>resource fit · {ok ? '✓ fits the card' : '✕ won’t fit together'}</h4>
                <div className="fit-bar" title={`${gb(f.need_mb)} GB needed of ${gb(ceil)} GB card`}>
                  {f.items.filter((i: any) => i.gpu).map((i: any, n: number) => (
                    <span key={i.key} className={'fit-seg fit-seg-' + (n % 4)} style={{ width: pct(i.mb) + '%' }}
                          title={`${i.key} · ${gb(i.mb)} GB`}>{pct(i.mb) > 12 ? i.key.replace(/^(tts|chat)-/, '') : ''}</span>
                  ))}
                  <span className="fit-free" style={{ width: Math.max(0, 100 - totalPct) + '%' }} />
                </div>
                <div className="fit-line">
                  {f.items.filter((i: any) => i.gpu).map((i: any) => `${i.key} ${gb(i.mb)} GB`).join('  +  ')}
                  {'  =  '}<b>{gb(f.need_mb)} GB</b> of {gb(ceil)} GB card
                </div>
                {!ok && (
                  <div className="fit-why">
                    won’t fit right now — needs {gb(f.need_now_mb)} GB, {gb(f.free_mb)} GB free.
                    {f.evict && f.evict.length ? ` Unload to make room: ${f.evict.join(', ')}.` : ' Pick a lighter voice or a smaller brain context.'}
                  </div>
                )}
                {ok && !f.fits_card && (
                  <div className="fit-why">loads now, but the two together exceed the card’s ceiling — close to the edge.</div>
                )}
              </section>
            )
          })()}
          <section className="settings-sec">
            <h4>brain</h4>
            <label>model</label>
            <select value={String(modelIdx)} onChange={e => { const i = Number(e.target.value); if (chatModelsX[i]) chooseModel(chatModelsX[i]) }}>
              <option value="-1">{cfg.model || 'default model'} (current)</option>
              {chatModelsX.map((r: any, i: number) => <option key={i} value={String(i)}>{r.model}{r.service ? (r.up ? ' · local' : ' · local ⏻') : ''}</option>)}
            </select>
            <label>temperature</label>
            <input type="number" step="0.1" min="0" max="2" defaultValue={bk.temperature ?? 0.7} onBlur={e => setBrainKnob('temperature', e.target.value)} />
            <label>max output tokens</label>
            <input type="number" min="1" defaultValue={bk.max_tokens ?? 1024} onBlur={e => setBrainKnob('max_tokens', e.target.value)} />
            {localRow && (
              <>
                <label>context window — restarts {localRow.service}</label>
                <div className="settings-ctx">
                  <input type="number" min="1024" step="1024" placeholder="e.g. 32768" value={ctx} onChange={e => setCtx(e.target.value)} />
                  <button className="b" onClick={() => { const v = Number(ctx); if (v) setModelCtx(localRow.service, v) }}>set &amp; restart</button>
                </div>
              </>
            )}
          </section>
          <section className="settings-sec">
            <h4>voice — input</h4>
            <label>ear (speech-to-text)</label>
            <select value={cfg.stt || ''} onChange={e => applyRhm({ stt: e.target.value })}>
              {ears.length ? ears.map(id => <option key={id} value={id}>{id}</option>) : <option value={cfg.stt || ''}>{cfg.stt || '(default)'}</option>}
            </select>
            {(() => {
              // Ear status + START affordance (Tim 2026-06-07: a down ear had no way to start from the UI).
              const earStat = voiceInfo && voiceInfo.stt && cfg.stt ? voiceInfo.stt[cfg.stt] : undefined
              const earReg = (voiceInfo && voiceInfo.stt_registry && cfg.stt) ? voiceInfo.stt_registry[cfg.stt] : null
              if (earStat === undefined) return null
              if (earStat) return <div className="ear-status ok">● {cfg.stt} online</div>
              const svc = earReg && earReg.service
              return (
                <div className="ear-status down">
                  ✕ {cfg.stt} offline — {earReg && earReg.detail ? earReg.detail : 'not running'}
                  {svc && <button className="b sm" style={{ marginLeft: 8 }} onClick={() => startVoiceService(svc, cfg.stt)}>▶ start</button>}
                </div>
              )
            })()}
            <label>listening style</label>
            <select value={cfg.voice_input_mode || 'push_to_talk'} onChange={e => setVoiceInputMode(e.target.value)}>
              <option value="push_to_talk">🎙 push-to-talk</option>
              <option value="auto_listen">👂 auto-listen (hands-free)</option>
            </select>
            <label className="settings-toggle"><input type="checkbox" checked={(cfg.voice_enabled || 'on') === 'on'} onChange={e => setVoiceEnabled(e.target.checked)} /> speak replies aloud</label>
          </section>
          <section className="settings-sec">
            <h4>voice — output</h4>
            <label>persona</label>
            <select value={cfg.persona || ''} onChange={e => switchPersona(e.target.value)}>
              <option value="">(choose a persona)</option>
              {personas.map((p: any) => <option key={p.id} value={p.id}>{p.name} · {p.engine}</option>)}
            </select>
            <label>engine override</label>
            <select value={cfg.tts_engine || ''} onChange={e => applyRhm({ tts_engine: e.target.value })}>
              <option value="">(persona default{curEngine ? ': ' + curEngine : ''})</option>
              {Object.keys(engineKnobs || {}).map(eng => <option key={eng} value={eng}>{eng}</option>)}
            </select>
            <label>voice override</label>
            <input type="text" defaultValue={cfg.tts_voice || ''} placeholder="blank = the persona's voice (clip / description / named)" onBlur={e => applyRhm({ tts_voice: e.target.value })} />
            {engineRows.length > 0 && (
              <div className="settings-knobs">
                <div className="muted">{curEngine} knobs</div>
                {engineRows.map((k: any) => (
                  <div key={k.key} className="settings-knob"><span className="kk">{k.key}</span><span className="muted">{k.scope === 'serve' ? 'serve · ' : 'live · '}{k.note}</span></div>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>
    </PanelErrorBoundary>
  )
}
