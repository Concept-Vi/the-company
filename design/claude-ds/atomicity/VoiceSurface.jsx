// atomicity/Voice.jsx
// ============================================================================
// Voice — the generative copy surface (migrated from Studio's voice canvas).
// Pick a real product moment, Vi writes options IN the house voice (sourced from
// the voice.conceptv behaviour — never inlined), you pick the one that sounds
// right and can save it back as a voice example. Composed from AcKit.
//
// Registers a `voice.write` capability into CV_AI on load (idempotent) so the
// move lives in the one catalogue like everything else.
// ============================================================================
const { useState: useState_vo, useReducer: useReducer_vo } = React;

// register the capability once (it composes the house voice behaviour)
(function registerVoice() {
  const AI = window.CV_AI; if (!AI || (AI.get && AI.get('voice.write'))) return;
  AI.register({
    id: 'voice.write', name: 'Write in the voice', layer: 'capability', family: 'voice',
    description: 'Write several options of microcopy for a product moment, in the ConceptV house voice.',
    surfaces: ['voice', 'atomicity'], provider: 'claude', behaviours: ['voice.conceptv'], icon: 'chat', provenance: 'built-in',
    async run(a) {
      const m = a.params.moment, brief = a.params.brief || '';
      const prompt = `Write 4 options of ${m.kind} for this product moment: "${m.label}".${brief ? ' Extra direction: ' + brief : ''} ${m.hint} Keep each within ${m.max} characters. Reply as JSON only: {"options":["…","…","…","…"]}`;
      let raw; try { raw = await AI.complete({ messages: [{ role: 'user', content: prompt }], max_tokens: 700 }); } catch (e) { raw = await AI.complete(prompt); }
      const mt = String(raw).match(/\{[\s\S]*\}/); let opts = [];
      try { opts = JSON.parse(mt ? mt[0] : raw).options || []; } catch { opts = String(raw).split('\n').map(s => s.replace(/^[-*\d.\s"]+|"$/g, '').trim()).filter(Boolean).slice(0, 4); }
      return opts;
    },
  }, { silent: true });
})();

const MOMENTS = [
  { id: 'cta', kind: 'a button label', label: 'Primary action on a listing', hint: 'Direct, a verb, no period.', max: 24, sample: 'Book inspection' },
  { id: 'headline', kind: 'a headline', label: 'Hero on the User Portal', hint: 'Confident, concrete, one line.', max: 52, sample: 'Find the home that fits your life.' },
  { id: 'insight', kind: 'a Vi insight line', label: 'Vi’s market note on a listing', hint: 'Calm, specific, a real number, second person.', max: 130, sample: 'Three comparable sales settled above guide this month — buyers are active in Bayside.' },
  { id: 'empty', kind: 'an empty-state line', label: 'No saved properties yet', hint: 'Warm, points to the next step.', max: 90, sample: 'Nothing saved yet — tap the heart on a listing to keep it here.' },
  { id: 'error', kind: 'an error message', label: 'A search returned nothing', hint: 'Plain, never blames the user, offers a way forward.', max: 90, sample: 'No matches in that area — try widening the price or suburb.' },
];

function AcVoice() {
  const AI = window.CV_AI;
  const [moment, setMoment] = useState_vo(MOMENTS[0]);
  const [brief, setBrief] = useState_vo('');
  const [options, setOptions] = useState_vo([]);
  const [chosen, setChosen] = useState_vo(null);
  const [busy, setBusy] = useState_vo(false);

  async function write() {
    setBusy(true); setChosen(null);
    try { const opts = await AI.execute('voice.write', { surface: 'voice', params: { moment, brief } }); setOptions(opts || []); }
    catch (e) { window.dsaToast?.(e.message || 'Could not write'); }
    setBusy(false);
  }
  function save(line) {
    try {
      window.CV_HOST.commit({ kind: 'ai.entry', title: 'Voice example · ' + moment.label,
        rationale: 'A house-voice line for “' + moment.label + '”, kept as a reference example.',
        payload: { id: 'voice.eg.' + moment.id + '.' + Date.now().toString(36), name: moment.label, layer: 'behaviour', family: 'voice', text: 'Example (' + moment.kind + '): "' + line + '"', provenance: 'authored' }, provenance: 'you' });
      window.dsaToast?.('Saved to the voice');
    } catch (e) { window.dsaToast?.(e.message); }
  }

  return (
    <div className="vo">
      <div className="vo-rail">
        <div className="vo-rail-lbl">Product moments</div>
        {MOMENTS.map(m => (
          <button key={m.id} className={`vo-moment ${moment.id === m.id ? 'on' : ''}`} onClick={() => { setMoment(m); setOptions([]); setChosen(null); }}>
            <b>{m.label}</b><i>{m.kind}</i>
          </button>
        ))}
      </div>

      <div className="vo-stage">
        <div className="vo-head">
          <div className="vo-head-tx"><h1>{moment.label}</h1><p>{moment.hint}</p></div>
        </div>
        <div className="ex3-intent-row">
          <input className="ex2-intent" value={brief} onChange={e => setBrief(e.target.value)} placeholder="Any extra direction… (optional)" onKeyDown={e => { if (e.key === 'Enter') write(); }}/>
          <button className="fz2-btn solid" disabled={busy} onClick={write}><CvIcon name="chat" size={13} tone="ink"/> {busy ? 'Writing…' : options.length ? 'Again' : 'Write options'}</button>
        </div>

        {options.length === 0 ? (
          <div className="vo-sample"><span className="vo-sample-lbl">The voice sounds like</span><div className="vo-sample-line">{renderMoment(moment, moment.sample)}</div></div>
        ) : (
          <div className="vo-options">
            {options.map((o, i) => (
              <div key={i} className={`vo-opt ${chosen === o ? 'on' : ''}`} onClick={() => setChosen(o)}>
                <div className="vo-opt-render">{renderMoment(moment, o)}</div>
                <div className="vo-opt-foot"><span>{o.length} chars</span><button className="vo-save" onClick={e => { e.stopPropagation(); save(o); }}><CvIcon name="plus" size={11} tone="bronze"/> Save to voice</button></div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function renderMoment(m, text) {
  if (m.id === 'cta') return <button className="vo-as-btn">{text}</button>;
  if (m.id === 'headline') return <div className="vo-as-headline">{text}</div>;
  if (m.id === 'insight') return <div className="vo-as-insight"><span className="vo-gem"/><span><b>Vi</b> · {text}</span></div>;
  return <div className="vo-as-body">{text}</div>;
}

window.AcVoice = AcVoice;
