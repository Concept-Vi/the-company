// atomicity/AtomiCity.jsx
// ============================================================================
// AtomiCity root — welds the Atlas browser and Vi into one app. Owns navigation
// state, implements the ATOMICITY.act() verb protocol Vi drives the interface
// through, pushes the active node into CV_AI context, and hosts the command bar.
// ============================================================================
const { useState: useState_ac, useEffect: useEffect_ac, useMemo: useMemo_ac, useCallback: useCallback_ac, useReducer: useReducer_acm } = React;

function AtomiCity() {
  const [tree, setTree] = useState_ac(window.ATLAS.tree);
  const [selId, setSelId] = useState_ac('sec/home');
  const [expanded, setExpanded] = useState_ac(() => new Set(['root']));
  const [hlId, setHlId] = useState_ac(null);
  const [viOpen, setViOpen] = useState_ac(false);
  const [ask, setAsk] = useState_ac({ text: '', nonce: 0 });
  const [cmdOpen, setCmdOpen] = useState_ac(false);
  const [cmdSeed, setCmdSeed] = useState_ac('');
  const [picked, setPicked] = useState_ac(null);   // {descriptor, _el} from CV_PICK

  const pickElement = useCallback_ac((d, el) => {
    setPicked({ ...d, _el: el, shot: null });
    setViOpen(true);
    if (window.CV_SHOT) window.CV_SHOT.snapshot(el).then(url => { if (url) setPicked(p => (p && p._el === el) ? { ...p, shot: url } : p); }).catch(() => {});
  }, []);
  const startPick = useCallback_ac(() => { window.CV_PICK.start(pickElement); }, [pickElement]);
  const clearPick = useCallback_ac(() => setPicked(null), []);

  // keep the tree live as registries change (projection never drifts)
  useEffect_ac(() => window.ATLAS.on(t => setTree({ ...t })), []);

  const node = useMemo_ac(() => window.ATLAS.find(selId), [selId, tree]);
  const ctx = useMemo_ac(() => ({ node, surface: 'atomicity' }), [node]);

  // push active surface + node into CV_AI so context.atomicity resolves
  useEffect_ac(() => { window.CV_AI.setActiveSurface('atomicity', { type: 'atomicity', title: node ? node.label : 'AtomiCity' }, { node }); }, [selId]);

  const expandAncestors = useCallback_ac((id) => {
    const path = window.ATLAS.pathTo(id);
    setExpanded(prev => { const next = new Set(prev); for (const p of path.slice(0, -1)) next.add(p.id); return next; });
  }, []);

  const openNode = useCallback_ac((id) => {
    if (!window.ATLAS.find(id)) return;
    const go = () => { setSelId(id); expandAncestors(id); const det = document.querySelector('.ac-detail'); if (det) det.scrollTop = 0; };
    // "nothing teleports" — cross-fade the detail pane via the View Transitions API
    if (document.startViewTransition && id !== selId) {
      document.startViewTransition(() => ReactDOM.flushSync(go));
    } else { go(); }
  }, [expandAncestors, selId]);

  const toggle = useCallback_ac((id) => setExpanded(prev => { const n = new Set(prev); n.has(id) ? n.delete(id) : n.add(id); return n; }), []);

  const askVi = useCallback_ac((text) => { setViOpen(true); setAsk({ text, nonce: Date.now() }); }, []);

  // THE ACTION PROTOCOL — Vi drives the interface through these verbs.
  const act = useCallback_ac(async (a) => {
    if (!a || !a.type) return;
    if (a.type === 'open' && a.node) return openNode(a.node);
    if (a.type === 'expand' && a.node) { expandAncestors(a.node); setExpanded(prev => new Set(prev).add(a.node)); return; }
    if (a.type === 'highlight' && a.node) { openNode(a.node); setHlId(a.node); setTimeout(() => setHlId(null), 1400); return; }
    if (a.type === 'search') { setCmdSeed(a.q || ''); setCmdOpen(true); return; }
    if (a.type === 'connect') {
      try { const name = await window.CV_HOST.runtimes.get('fsapi').activate(); window.dsaToast?.('Connected to ' + name + ' — Vi can write to disk'); window.ATLAS.rebuild(); }
      catch (e) { window.dsaToast?.(e.message); }
      return;
    }
    if (a.type === 'ingest') {
      openNode('sec/ingest');
      if (a.text && window.CV_SOURCE) { const s = window.CV_SOURCE.addSource({ name: a.name || 'From Vi · ' + new Date().toLocaleTimeString(), kind: 'text', text: a.text }); await window.CV_SOURCE.recognize(s.id); window.CV_SOURCE.analyze(s.id); }
      return;
    }
    if (a.type === 'explore') { openNode('sec/explore'); return; }
    if (a.type === 'restyle' && a.style) {
      // apply via the override layer so the change STICKS (survives re-render)
      setPicked(p => {
        if (p && p._el && p._el.isConnected) { try { window.CV_OVERRIDE.apply(p._el, a.style); } catch (e) {} }
        return p;
      });
      return;
    }
    if (a.type === 'run' && a.capability) {
      try { await window.CV_AI.execute(a.capability, { surface: 'atomicity', params: a.params || {} }); window.dsaToast?.('Ran ' + a.capability); }
      catch (e) { window.dsaToast?.(e.message); }
    }
  }, [openNode, expandAncestors]);

  // expose for cross-component + console use (incl. mode-engine levers)
  useEffect_ac(() => { window.ATOMICITY = { act, openNode, askVi, startPick, setVi: setViOpen, setPicked, pickElement }; return () => { delete window.ATOMICITY; }; }, [act, openNode, askVi, startPick, pickElement]);

  // Cmd+K / Cmd+E
  useEffect_ac(() => {
    function onKey(e) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') { e.preventDefault(); setCmdSeed(''); setCmdOpen(o => !o); }
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'e') { e.preventDefault(); const m = window.CV_MODE.active(); window.CV_MODE.activate(m && m.id === 'inspect' ? 'operator' : 'inspect'); }
      if (e.key === 'Escape') { setCmdOpen(false); }
    }
    window.addEventListener('keydown', onKey); return () => window.removeEventListener('keydown', onKey);
  }, [startPick]);

  const host = window.CV_HOST.describe();

  return (
    <div id="atomicity-root" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div className="ac-top">
        <div className="ac-brand"><span className="mark"><CvIcon name="atom" size={22} tone="gold"/></span><span className="word">Atomi<b>City</b></span></div>
        <span className="sub">{host.namespace || ''}</span>
        <div className="grow"/>
        <ModeSwitch/>
        <button className="ac-searchbtn" onClick={() => { setCmdSeed(''); setCmdOpen(true); }}>
          <CvIcon name="search" size={13} tone="muted"/> Search <kbd>⌘K</kbd>
        </button>
        <span className={`ac-env-pill ${host.canWrite ? 'live' : ''}`} title={host.modeLabel}
          onClick={() => openNode('reg/host')} style={{ cursor: 'pointer' }}>{host.modeLabel}</span>
      </div>

      <div className="ac-body">
        <AcTree tree={tree} selId={selId} expanded={expanded} onToggle={toggle} onSelect={openNode} hlId={hlId}/>
        <AcDetail node={node} onSelect={openNode} onAsk={askVi}/>
      </div>

      <ViConsole open={viOpen} onOpen={() => setViOpen(true)} onClose={() => setViOpen(false)}
        ctx={ctx} onAct={act} onOpenNode={openNode} pendingAsk={ask}
        picked={picked} onClearPick={clearPick} onStartPick={startPick}/>

      {cmdOpen && <AcCommandBar seed={cmdSeed} onClose={() => setCmdOpen(false)} onOpen={openNode} onAsk={askVi} ctx={ctx}/>}
      <Toast/>
    </div>
  );
}

/* ---------------------------- COMMAND BAR ---------------------------- */
function AcCommandBar({ seed, onClose, onOpen, onAsk, ctx }) {
  const [q, setQ] = useState_ac(seed || '');
  const [cur, setCur] = useState_ac(0);
  const results = useMemo_ac(() => window.ATLAS.search(q), [q]);
  const quick = useMemo_ac(() => window.VI_BRAIN.quickCommands(ctx), [ctx]);
  const filteredQuick = useMemo_ac(() => q ? quick.filter(c => c.label.toLowerCase().includes(q.toLowerCase())) : quick, [q, quick]);
  const rows = useMemo_ac(() => [
    ...filteredQuick.map(c => ({ type: 'ask', label: c.label, run: c.run })),
    ...results.map(n => ({ type: 'node', label: n.label, kind: n.kind, id: n.id })),
  ], [filteredQuick, results]);

  useEffect_ac(() => { setCur(0); }, [q]);
  function choose(r) {
    if (!r) return;
    if (r.type === 'ask') { onAsk(r.run); onClose(); }
    else { onOpen(r.id); onClose(); }
  }
  return (
    <div className="ac-cmd-back" onClick={onClose}>
      <div className="ac-cmd" onClick={e => e.stopPropagation()}>
        <input autoFocus value={q} placeholder="Search tokens, components, cards, capabilities… or ask Vi"
          onChange={e => setQ(e.target.value)}
          onKeyDown={e => {
            if (e.key === 'ArrowDown') { e.preventDefault(); setCur(c => Math.min(c + 1, rows.length - 1)); }
            else if (e.key === 'ArrowUp') { e.preventDefault(); setCur(c => Math.max(c - 1, 0)); }
            else if (e.key === 'Enter') { e.preventDefault(); choose(rows[cur]); }
          }}/>
        <div className="ac-cmd-list">
          {filteredQuick.length > 0 && <div className="ac-cmd-sec">Ask Vi</div>}
          {rows.map((r, i) => r.type === 'ask' && (
            <div key={'a'+i} className={`ac-cmd-row ${cur === i ? 'cur' : ''}`} onMouseEnter={() => setCur(i)} onClick={() => choose(r)}>
              <ViShape size={15}/> {r.label}
            </div>
          ))}
          {results.length > 0 && <div className="ac-cmd-sec">In the system</div>}
          {rows.map((r, i) => r.type === 'node' && (
            <div key={'n'+i} className={`ac-cmd-row ${cur === i ? 'cur' : ''}`} onMouseEnter={() => setCur(i)} onClick={() => choose(r)}>
              <CvIcon name="dot" size={12} tone="bronze"/> {r.label} <span className="meta">{r.kind}</span>
            </div>
          ))}
          {rows.length === 0 && <div className="ac-empty">Nothing matches "{q}". Press Enter on an Ask Vi row to send it as a question.</div>}
        </div>
      </div>
    </div>
  );
}

// the mode switcher — a projection of CV_MODE, like every other UI surface
function ModeSwitch() {
  const [, force] = useReducer_acm(x => x + 1, 0);
  useEffect_ac(() => window.CV_MODE.subscribe(force), []);
  const modes = window.CV_MODE.all();
  const active = window.CV_MODE.active();
  return (
    <div className="ac-modes" role="tablist" title="Mode — changes what clicking does (⌘E)">
      {modes.map(m => (
        <button key={m.id} className={`ac-mode ${active && active.id === m.id ? 'on' : ''}`}
          onClick={() => window.CV_MODE.activate(m.id)} title={m.hint}>
          <CvIcon name={m.icon} size={13} tone={active && active.id === m.id ? 'gold' : 'muted'}/>
          {m.label}
        </button>
      ))}
    </div>
  );
}

// normalize a Vi style recipe → inline style props applied to the real node
function normalizeStyle(s) {  const tok = v => (v == null || v === '') ? undefined : (String(v).trim().startsWith('--') ? 'var(' + String(v).trim() + ')' : String(v));
  const out = {};
  if (s.bg != null) out.background = tok(s.bg);
  if (s.fg != null) out.color = tok(s.fg);
  if (s.radius != null) out.borderRadius = tok(s.radius);
  if (s.shadow != null) out.boxShadow = s.shadow === 'none' ? 'none' : tok(s.shadow);
  if (s.border != null) out.border = (s.borderWidth || '1px') + ' solid ' + tok(s.border);
  if (s.weight != null) out.fontWeight = s.weight;
  if (s.font != null) out.fontFamily = tok(s.font);
  if (s.padding != null) out.padding = s.padding;
  if (s.tracking != null) out.letterSpacing = s.tracking;
  if (s.color) out.color = tok(s.color);
  return out;
}

window.AtomiCity = AtomiCity;