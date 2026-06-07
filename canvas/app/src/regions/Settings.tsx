// S3/S5 — the dedicated SETTINGS window. A modal (full-screen on mobile, the design-system surface) that
// consolidates the MAIN configurations of whatever's loaded: brain (model · temperature · max-tokens ·
// context window), voice input (ear · listening style · speak on/off), voice output (persona · engine ·
// voice · the engine's own knobs). Quick presets still live in the RHM; this is the config bench. Reflects-
// never-owns: reads cfg + the catalogs, POSTs changes via the controller handlers, reads back. data-ui-ref.
import { useState } from 'react'
import { useApp } from '../AppContext'
import { PanelErrorBoundary } from '../components/PanelErrorBoundary'

export function Settings() {
  const { settingsOpen, setSettingsOpen, cfg, chatModelsX, personas, engineKnobs, voiceInfo,
          chooseModel, switchPersona, setBrainKnob, setModelCtx, applyRhm, setVoiceInputMode, setVoiceEnabled } = useApp()
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
