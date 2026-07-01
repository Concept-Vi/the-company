// atomicity/ViConsole.jsx
// ============================================================================
// Vi — the omnipresent agent. An always-present launcher that opens into a
// console. Vi knows the whole system (VI_BRAIN.systemPrompt), interprets intent,
// acts on the interface (the action chips run real ATOMICITY.act verbs), stages
// real repo changes (proposals), solicits feedback fluidly, and LEARNS — folding
// preferences back into CV_AI so it improves. Modes: Chat · Teach · Memory.
// ============================================================================
const { useState: useState_vc, useEffect: useEffect_vc, useRef: useRef_vc } = React;

function ViConsole({ open, onOpen, onClose, ctx, onAct, onOpenNode, pendingAsk, picked, onClearPick, onStartPick }) {
  const [messages, setMessages] = useState_vc([
    { from: 'vi', text: `Hi — I'm V<span class="i">i</span>. I can see your whole system and act on it with you. Ask me anything, or tell me what you're trying to do — I'll figure out the how.` },
  ]);
  const [input, setInput] = useState_vc('');
  const [thinking, setThinking] = useState_vc(false);
  const [mode, setMode] = useState_vc('chat'); // chat | teach | memory
  const [mem, setMem] = useState_vc(window.VI_BRAIN.memory());
  const [nudge, setNudge] = useState_vc(null);
  const [shotN, setShotN] = useState_vc(() => (window.CV_SHOT ? { n: window.CV_SHOT.history().length, limit: window.CV_SHOT.getLimit() } : { n: 0, limit: 8 }));
  const feedRef = useRef_vc(null);

  useEffect_vc(() => window.CV_SHOT && window.CV_SHOT.subscribe(() => setShotN({ n: window.CV_SHOT.history().length, limit: window.CV_SHOT.getLimit() })), []);

  useEffect_vc(() => { if (feedRef.current) feedRef.current.scrollTop = feedRef.current.scrollHeight; }, [messages, thinking]);

  // programmatic asks from detail-pane chips / command bar
  useEffect_vc(() => { if (pendingAsk && pendingAsk.nonce) { setMode('chat'); send(pendingAsk.text); } }, [pendingAsk && pendingAsk.nonce]);

  const sugg = window.VI_BRAIN.suggestions(ctx);

  async function send(textArg) {
    const text = (textArg ?? input).trim();
    if (!text || thinking) return;
    setInput('');
    setMessages(m => [...m, { from: 'user', text: esc(text) }]);
    setNudge(null);

    if (mode === 'teach') {
      setThinking(true);
      try {
        const { entry, proposal } = await window.VI_BRAIN.learn(text, ctx);
        setMem(window.VI_BRAIN.memory());
        setMessages(m => [...m, { from: 'vi',
          text: `Learned: <b>${esc(entry.label)}</b> — "${esc(entry.instruction)}". I'll apply this from now on${entry.surface ? ' on this surface' : ''}.`,
          proposals: proposal ? [{ ...proposal, title: 'Learned: ' + entry.label }] : [] }]);
      } catch (e) {
        setMessages(m => [...m, { from: 'vi', text: 'I could not capture that just now — try rephrasing the preference.' }]);
      }
      setThinking(false); setMode('chat');
      return;
    }

    setThinking(true);
    try {
      const history = messages.slice(-6);
      const res = await window.VI_BRAIN.interpret(text, { ...ctx, picked }, history);
      const msgId = 'm' + Date.now().toString(36);
      setMessages(m => [...m, { id: msgId, from: 'vi', text: fmt(res.say), actions: res.actions, proposals: res.proposals, followup: res.followup, options: res.options }]);
      // auto-run navigational actions; restyle goes through the visual-diff path
      let restyle = null;
      for (const a of (res.actions || [])) {
        if (a.type === 'restyle' && a.style) { restyle = a; continue; }
        if (a.type === 'open' && a.node) onOpenNode(a.node);
        if (a.type === 'search' || a.type === 'expand' || a.type === 'highlight' || a.type === 'connect' || a.type === 'ingest' || a.type === 'explore') onAct(a);
      }
      // whole-page shot on request
      const wantsPage = (res.actions || []).some(a => a.type === 'pageshot');
      if (wantsPage) {
        const purl = await window.CV_SHOT.snapshotPage().catch(() => null);
        if (purl) { window.CV_SHOT.remember(purl, { label: 'page' }); setMessages(m => m.map(x => x.id === msgId ? { ...x, pair: { after: purl } } : x)); }
      }
      if (restyle && picked && picked._el && picked._el.isConnected) {
        const el = picked._el;
        const before = await window.CV_SHOT.snapshot(el).catch(() => null);
        const sBefore = window.CV_OVERRIDE.snapshotStyles(el);
        window.CV_OVERRIDE.apply(el, restyle.style);
        await new Promise(r => requestAnimationFrame(() => setTimeout(r, 80)));
        const after = await window.CV_SHOT.snapshot(el).catch(() => null);
        const sAfter = window.CV_OVERRIDE.snapshotStyles(el);
        if (after) window.CV_SHOT.remember(after, { label: picked.role });
        const sdiff = window.CV_OVERRIDE.diff(sBefore, sAfter);
        setMessages(m => m.map(x => x.id === msgId ? { ...x, pair: { before, after }, sdiff } : x));
        // on export, let Vi actually SEE the change and react (sandbox: skipped)
        if (before && after) {
          window.CV_AI.execute('vision.diff', { surface: 'atomicity', params: { before, after, intent: text } })
            .then(say => { if (say) setMessages(m => m.map(x => x.id === msgId ? { ...x, followup: typeof say === 'string' ? say : (say && say[0]) } : x)); })
            .catch(() => {});
        }
      } else if (restyle) {
        window.dsaToast?.('Select an element first (Inspect mode), then ask me to change it.');
      }
      if (res.actions && res.actions.length) setNudge(window.VI_BRAIN.feedbackNudge(res.actions[0]));
      else if (res.proposals && res.proposals.length) setNudge(window.VI_BRAIN.feedbackNudge({ type: 'propose' }));
    } catch (e) {
      setMessages(m => [...m, { from: 'vi', text: 'I had trouble reaching the model. Try again, or rephrase.' }]);
    }
    setThinking(false);
  }

  function runAction(a) {
    if (a.type === 'open' && a.node) return onOpenNode(a.node);
    onAct(a);
  }

  return (
    <>
      {!open && (
        <button className="ac-vi-fab" onClick={onOpen}>
          <ViShape size={22}/>
          <span>Ask V<span style={{color:'var(--accent-gold)'}}>i</span></span>
        </button>
      )}
      <aside className={`ac-vi-panel ${open ? 'open' : ''}`}>
        <div className="ac-vi-head">
          <ViShape size={22}/>
          <h3>V<span className="i">i</span></h3>
          <span className="ctx">{ctx && ctx.node ? ctx.node.label : 'home'}</span>
          <button className="ac-vi-x" onClick={onClose}>✕</button>
        </div>

        {mode === 'memory' ? (
          <div className="ac-vi-feed">
            <p className="ac-ddoc" style={{ margin: 0 }}>What I've learned you prefer. Each is a live behaviour in the AI registry and a staged change for permanence.</p>
            <div className="ac-mem">
              {mem.length === 0 && <div className="ac-empty">Nothing yet. Switch to <b>Teach</b> and tell me a preference.</div>}
              {mem.map(e => (
                <div className="ac-mem-item" key={e.id}>
                  <CvIcon name="sparkles" size={14} tone="gold"/>
                  <div className="it"><span className="lb">{e.label}</span><br/>{e.instruction}{e.surface ? <em> · {e.surface}</em> : ''}</div>
                  <button className="x" title="Forget" onClick={() => { window.VI_BRAIN.forget(e.id); setMem(window.VI_BRAIN.memory()); }}>✕</button>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="ac-vi-feed" ref={feedRef}>
            {messages.map((m, i) => (
              <div className={`ac-msg ${m.from === 'user' ? 'is-user' : 'is-vi'}`} key={i}>
                <div className={`av ${m.from === 'user' ? 'user' : ''}`}>
                  {m.from === 'user' ? <CvIcon name="user" size={14} tone="bronze"/> : <ViShape size={24}/>}
                </div>
                <div className="bd">
                  <div className="nm">{m.from === 'user' ? 'You' : 'Vi'}</div>
                  <div className="tx" dangerouslySetInnerHTML={{ __html: m.text }}
                    onClick={e => { const n = e.target?.dataset?.node; if (n) onOpenNode(n); }}/>
                  {(m.actions && m.actions.length > 0) && (
                    <div className="ac-acts">
                      {m.actions.filter(a => a.type !== 'note').map((a, j) => (
                        <button key={j} className="ac-act" onClick={() => runAction(a)}>
                          <CvIcon name={actIcon(a.type)} size={11} tone="bronze"/>{actLabel(a)}
                        </button>
                      ))}
                      {m.actions.filter(a => a.type === 'note').map((a, j) => <span key={'n'+j} className="ac-followup">{a.text}</span>)}
                    </div>
                  )}
                  {(m.proposals && m.proposals.length > 0) && (
                    <div className="ac-acts">
                      {m.proposals.map((p, j) => (
                        <button key={j} className="ac-act proposal" onClick={() => onOpenNode('change/' + p.id)}>
                          <CvIcon name="edit" size={11} tone="gold"/>
                          {p.status === 'applied' ? 'Wrote ' : 'Staged '} {p.title} →
                        </button>
                      ))}
                    </div>
                  )}
                  {(m.pair && (m.pair.before || m.pair.after)) && (
                    <div className="ac-vdiff">
                      {m.pair.before && <figure><img src={m.pair.before} alt="before"/><figcaption>before</figcaption></figure>}
                      <span className="ac-vdiff-arrow">→</span>
                      {m.pair.after && <figure><img src={m.pair.after} alt="after"/><figcaption>after</figcaption></figure>}
                    </div>
                  )}
                  {m.followup && <div className="ac-followup">{m.followup}</div>}
                  {(m.options && m.options.length > 0) && (
                    React.createElement(window.AcKit.OptionRow, { options: m.options, onPick: (o) => send(o.say) })
                  )}
                </div>
              </div>
            ))}
            {thinking && (
              <div className="ac-msg"><div className="av"><ViShape size={24} animated/></div>
                <div className="bd"><div className="nm">Vi</div><div className="tx" style={{ color: 'var(--fg-secondary)' }}>thinking…</div></div></div>
            )}
            {nudge && !thinking && <div className="ac-followup" style={{ marginLeft: 35 }}>{nudge}</div>}
            {messages.length === 1 && !thinking && (
              <div className="ac-vi-sugg">
                {sugg.map(s => <button key={s} className="ac-sugg-pill" onClick={() => send(s)}>{s}</button>)}
              </div>
            )}
          </div>
        )}

        <div className="ac-vi-composer">
          {picked && (
            <div className="ac-vi-picked">
              {picked.shot
                ? <img className="ac-vi-picked-shot" src={picked.shot} alt="selection"/>
                : <span className="ac-vi-picked-sw" style={{ background: picked.styles && picked.styles.background }}/>}
              <span className="ac-vi-picked-tx"><b>{picked.role}</b>{picked.text ? ' · ' + picked.text.slice(0, 28) : ''}</span>
              <button className="ac-vi-picked-x" onClick={onClearPick} title="Clear selection">✕</button>
            </div>
          )}
          {picked && mode === 'chat' && (
            <div className="ac-vi-pickacts">
              <button onClick={() => send('Explain this element — what is it and how is it styled?')}>Explain this</button>
              <button onClick={() => send('Give me 3 fresh style directions for this element, then restyle it to the best one.')}>Restyle this</button>
              <button onClick={() => send('Turn this into a reusable component in the system.')}>Make a component</button>
              <button onClick={() => send('Show me the whole page.')}>See full page</button>
            </div>
          )}
          <div className="ac-vi-modes">
            <button className={`ac-vi-mode ${mode === 'chat' ? 'on' : ''}`} onClick={() => setMode('chat')}>Chat</button>
            <button className={`ac-vi-mode ${mode === 'teach' ? 'on' : ''}`} onClick={() => setMode('teach')}>Teach</button>
            <button className={`ac-vi-mode ${mode === 'memory' ? 'on' : ''}`} onClick={() => { setMode('memory'); setMem(window.VI_BRAIN.memory()); }}>Memory ({mem.length})</button>
            <span className="ac-vi-shotmem" title="How many recent screenshots Vi keeps in view (FIFO). Adjustable by you and by Vi.">
              <CvIcon name="eye" size={11} tone="bronze"/>
              <button onClick={() => window.CV_SHOT.setLimit(shotN.limit - 1)} disabled={shotN.limit <= 1}>−</button>
              <b>{shotN.n}/{shotN.limit}</b>
              <button onClick={() => window.CV_SHOT.setLimit(shotN.limit + 1)} disabled={shotN.limit >= 40}>+</button>
            </span>
          </div>
          {mode !== 'memory' && (
            <>
              <div className="ac-vi-input">
                <textarea rows="1" value={input}
                  placeholder={mode === 'teach' ? 'Tell me a preference — e.g. "always show me the source when you propose a change"' : (picked ? `Ask about the selected ${picked.role}, or tell me what to do with it…` : (ctx && ctx.node ? `Ask about ${ctx.node.label}, or tell me what you want…` : 'Ask Vi anything, or describe what you want to do…'))}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); } }}
                  disabled={thinking}/>
                <button className="ac-vi-send" onClick={() => send()} disabled={thinking || !input.trim()}>→</button>
              </div>
              <div className="ac-vi-hint">{mode === 'teach' ? 'I\'ll distil it, apply it live, and stage it for permanence' : 'Enter to send · I can open, search, propose changes, and act with you'}</div>
            </>
          )}
        </div>
      </aside>
    </>
  );
}

function actIcon(t) { return ({ open: 'arrow-right', search: 'search', expand: 'plus', run: 'sparkles', propose: 'edit', connect: 'cloud-upload', highlight: 'crosshair' })[t] || 'dot'; }
function actLabel(a) {
  if (a.type === 'open') return 'Open ' + lastSeg(a.node);
  if (a.type === 'search') return 'Search "' + a.q + '"';
  if (a.type === 'expand') return 'Expand ' + lastSeg(a.node);
  if (a.type === 'run') return 'Run ' + a.capability;
  if (a.type === 'connect') return 'Connect a file runtime';
  if (a.type === 'highlight') return 'Show ' + lastSeg(a.node);
  return a.type;
}
function lastSeg(id) { return String(id || '').split('/').pop(); }
function fmt(t) {
  return String(t || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<b>$1</b>').replace(/`([^`]+)`/g, '<code>$1</code>').replace(/\n/g, '<br>');
}
function esc(s) { return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

window.ViConsole = ViConsole;
