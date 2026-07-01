// components/CommandPalette.jsx — Cmd+K cross-canvas search overlay
const { useState: useState_cp, useEffect: useEffect_cp, useRef: useRef_cp, useMemo: useMemo_cp } = React;

function CommandPalette({ open, onClose, nav, openExport, copyText }) {
  const [q, setQ] = useState_cp('');
  const [sel, setSel] = useState_cp(0);
  const inputRef = useRef_cp(null);

  // Build a unified searchable index from everything the system knows about
  const items = useMemo_cp(() => {
    if (!open) return [];
    const out = [];

    // Canvases
    const canvases = [
      ['overview', 'Overview',    'dashboard'],
      ['build',    'Build',       'atom'],
      ['inbox',    'Inbox',       'files-stack'],
      ['colors',   'Colors',      'color-swatches'],
      ['icons',    'Icons',       'star'],
      ['type',     'Type',        'document'],
      ['logos',    'Logos & marks','tag'],
      ['imagery',  'Imagery',     'image-stack'],
      ['patterns', 'Motion & space','adjustments'],
      ['components','Components', 'check-square'],
      ['templates','Templates',   'browser'],
      ['voice',    'Voice & tone','chat-double'],
    ];
    canvases.forEach(([id, label, icon]) => {
      out.push({
        kind: 'Canvas', label, icon, hint: 'Open canvas',
        action: () => { nav(id); onClose(); },
      });
    });

    // Actions
    out.push({ kind: 'Action', label: 'Export to disk', icon: 'cloud-download', hint: 'CSS + JS patches', action: () => { openExport(); onClose(); } });
    out.push({ kind: 'Action', label: 'Build something new', icon: 'atom', hint: 'Hand Vi a brief', action: () => { nav('build'); onClose(); } });
    out.push({ kind: 'Action', label: 'Drop into Inbox', icon: 'files-stack', hint: 'Triage uploads', action: () => { nav('inbox'); onClose(); } });

    // Icons — every glyph in the library
    Object.keys(window.CV_ICONS?.data || {}).forEach(name => {
      out.push({
        kind: 'Icon',
        label: name,
        iconRender: name,
        hint: 'Copy name',
        action: () => { copyText(name); onClose(); },
      });
    });

    // Colors — key base + edited
    const baseColors = [
      ['gold', '#E0C010'], ['bronze', '#988058'], ['canvas', '#FBF7EC'],
      ['dark', '#1F1A12'], ['success', '#5A8A4A'], ['error', '#C24A3C'],
      ['info', '#4A78B8'], ['pending', '#E5C547'],
    ];
    baseColors.forEach(([name, hex]) => {
      out.push({
        kind: 'Color', label: name, hint: hex.toUpperCase(),
        colorSwatch: hex,
        action: () => { copyText(hex); onClose(); },
      });
    });

    // Voice rules
    [
      'Sentence case for everything',
      'Second person, never first-person plural',
      'Imperative for actions',
      'No exclamation marks',
      'No emoji in body copy',
      'Inline previews of consequences',
      'Sparing inline gold accent',
    ].forEach(label => {
      out.push({ kind: 'Voice rule', label, icon: 'chat-double', hint: 'Open Voice canvas', action: () => { nav('voice'); onClose(); } });
    });

    return out;
  }, [open]);

  const filtered = useMemo_cp(() => {
    if (!q.trim()) return items.slice(0, 40);
    const lc = q.toLowerCase();
    return items
      .map(it => {
        const text = (it.label + ' ' + (it.kind || '') + ' ' + (it.hint || '')).toLowerCase();
        if (!text.includes(lc)) return null;
        const labelLc = it.label.toLowerCase();
        let score = 0;
        if (labelLc === lc) score = 100;
        else if (labelLc.startsWith(lc)) score = 80;
        else if (labelLc.includes(lc)) score = 50;
        else score = 20;
        return { it, score };
      })
      .filter(Boolean)
      .sort((a, b) => b.score - a.score)
      .slice(0, 40)
      .map(r => r.it);
  }, [q, items]);

  useEffect_cp(() => {
    if (!open) return;
    setQ(''); setSel(0);
    setTimeout(() => inputRef.current?.focus(), 30);
    function onKey(e) {
      if (e.key === 'Escape')        { e.preventDefault(); onClose(); }
      else if (e.key === 'ArrowDown'){ e.preventDefault(); setSel(s => Math.min(s+1, filtered.length-1)); }
      else if (e.key === 'ArrowUp')  { e.preventDefault(); setSel(s => Math.max(s-1, 0)); }
      else if (e.key === 'Enter')    { e.preventDefault(); filtered[sel]?.action(); }
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, filtered, sel]);

  useEffect_cp(() => { setSel(0); }, [q]);

  if (!open) return null;

  return (
    <div style={{
      position:'fixed',inset:0,background:'rgba(31,26,18,.35)',backdropFilter:'blur(6px)',
      zIndex:300,display:'flex',alignItems:'flex-start',justifyContent:'center',paddingTop:'12vh',
    }} onClick={onClose}>
      <div onClick={e => e.stopPropagation()} style={{
        background:'var(--bg-surface)',borderRadius:'var(--r-xl)',width:'min(640px, 92vw)',
        boxShadow:'var(--shadow-modal)',overflow:'hidden',display:'flex',flexDirection:'column',maxHeight:'72vh',
      }}>
        <div style={{display:'flex',alignItems:'center',gap:10,padding:'14px 18px',borderBottom:'1px solid var(--border-faint)'}}>
          <CvIcon name="search" size={16} tone="muted"/>
          <input
            ref={inputRef}
            value={q} onChange={e => setQ(e.target.value)}
            placeholder="Search canvases, icons, colors, voice rules, actions…"
            style={{flex:1,border:'none',outline:'none',font:'400 15px/1.2 var(--font-body)',color:'var(--fg-primary)',background:'transparent'}}
          />
          <span style={{font:'500 11px/1 var(--font-mono)',color:'var(--fg-muted)',padding:'4px 8px',background:'var(--bg-muted)',borderRadius:4}}>esc</span>
        </div>
        <div style={{flex:1,overflowY:'auto',padding:'6px 8px'}}>
          {filtered.length === 0 && (
            <div style={{padding:'30px 20px',textAlign:'center',color:'var(--fg-muted)',font:'400 13px/1.55 var(--font-body)'}}>
              No matches for "<b>{q}</b>"
            </div>
          )}
          {filtered.map((it, i) => {
            const active = i === sel;
            return (
              <div key={i}
                onMouseEnter={() => setSel(i)}
                onClick={() => it.action()}
                style={{
                  display:'flex',alignItems:'center',gap:12,
                  padding:'9px 12px',borderRadius:'var(--r-sm)',cursor:'pointer',
                  background: active ? 'var(--accent-gold-soft)' : 'transparent',
                }}>
                <span style={{width:24,height:24,display:'flex',alignItems:'center',justifyContent:'center',color:'var(--accent-bronze)',flex:'none'}}>
                  {it.iconRender
                    ? <CvIcon name={it.iconRender} size={18} tone={active ? 'gold' : 'bronze'}/>
                    : it.colorSwatch
                      ? <span style={{width:18,height:18,borderRadius:4,background:it.colorSwatch,border:'1px solid var(--border-faint)'}}/>
                      : <CvIcon name={it.icon || 'tag'} size={16} tone={active ? 'gold' : 'bronze'}/>
                  }
                </span>
                <span style={{flex:1,minWidth:0,font:'500 13px/1.2 var(--font-body)',color:'var(--fg-primary)',whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'}}>
                  {it.label}
                  {it.hint && <span style={{color:'var(--fg-muted)',font:'400 11px/1 var(--font-body)',marginLeft:8}}>{it.hint}</span>}
                </span>
                <span style={{font:'500 10px/1 var(--font-body)',color:'var(--fg-muted)',letterSpacing:'0.06em',textTransform:'uppercase'}}>{it.kind}</span>
                {active && <span style={{font:'500 11px/1 var(--font-mono)',color:'var(--fg-muted)'}}>↵</span>}
              </div>
            );
          })}
        </div>
        <div style={{padding:'10px 18px',borderTop:'1px solid var(--border-faint)',display:'flex',gap:14,font:'400 11px/1 var(--font-body)',color:'var(--fg-muted)'}}>
          <span><b style={{color:'var(--fg-secondary)'}}>↑↓</b> navigate</span>
          <span><b style={{color:'var(--fg-secondary)'}}>↵</b> open</span>
          <span><b style={{color:'var(--fg-secondary)'}}>esc</b> close</span>
          <span style={{marginLeft:'auto'}}>{filtered.length} of {items.length}</span>
        </div>
      </div>
    </div>
  );
}

window.CommandPalette = CommandPalette;
