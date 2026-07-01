// canvases/Components.jsx — gallery of UI patterns with live state previews + Vi generation
const { useState: useState_cm } = React;

const STATES = ['default', 'hover', 'active', 'disabled'];

// ============================================================
// Built-in component specs (mirror the patterns from the UI kits)
// ============================================================
const COMPONENT_GROUPS = {
  Buttons: [
    { id: 'btn-primary', name: 'Primary', desc: 'Gold filled — reserve for the one "earn attention" action per surface.' },
    { id: 'btn-outline', name: 'Outline', desc: '1.5 px gold border. The default toolbar button.' },
    { id: 'btn-dashed',  name: 'Dashed',  desc: 'Empty / placeholder action. Same as the sidebar "favourites" slot.' },
    { id: 'btn-ghost',   name: 'Ghost',   desc: 'No chrome until hover. Use for tertiary actions in dense UI.' },
    { id: 'btn-dark',    name: 'Dark',    desc: 'Ink fill, cream text. Used for MENU pill in the Virtual Hub viewer.' },
    { id: 'btn-ai',      name: 'AI / Vi', desc: 'Dark with the Vi diamond glyph. Used for any AI-triggered action.' },
  ],
  Inputs: [
    { id: 'in-text',  name: 'Text input', desc: 'Gold border by default. Brand pattern: input reads as "ready" pre-focus.' },
    { id: 'in-search', name: 'Search',    desc: 'Same border, search icon inset. Used in every toolbar.' },
    { id: 'in-textarea', name: 'Textarea', desc: 'Multi-line, identical border treatment.' },
    { id: 'check', name: 'Checkbox', desc: 'Gold fill with ink tick when on; soft gold when off. No third state.' },
  ],
  Cards: [
    { id: 'card-surface', name: 'Surface card', desc: 'White fill, no border, soft warm shadow, 12 px radius. The default content card.' },
    { id: 'card-media',   name: 'Media tile',   desc: 'Sunken fill, no border, 4 px radius. For image/video placeholders.' },
    { id: 'card-drop',    name: 'Dropzone',     desc: 'Dashed gold border + sunken interior. For upload affordances.' },
  ],
  Chips: [
    { id: 'chip-status', name: 'Status pill',  desc: 'Coloured dot + label + soft-fill background.' },
    { id: 'chip-task',   name: 'Task chip',    desc: 'Calendar variant — same shape with a 7 px dot.' },
    { id: 'badge',       name: 'Notification badge', desc: 'Red circular numeric badge on the bell icon — no "+9".' },
  ],
  Panels: [
    { id: 'panel-section', name: 'Soft-gold section panel', desc: 'The brand\'s signature grouped-settings container.' },
    { id: 'panel-dark',    name: 'Dark overlay',           desc: 'rgba(31,26,18,.92) + 12 px backdrop blur. For in-hub menus.' },
  ],
};

function Components({ generated, addGenerated }) {
  const [genOpen, setGenOpen] = useState_cm(false);
  const [genPrompt, setGenPrompt] = useState_cm('A "compact primary" button — same gold fill but at h=32 px with 12 px horizontal padding');
  const [generating, setGenerating] = useState_cm(false);
  const [proposal, setProposal] = useState_cm(null);
  const [selectedGroup, setSelectedGroup] = useState_cm(null);

  const total = Object.values(COMPONENT_GROUPS).reduce((n, g) => n + g.length, 0) + generated.length;

  async function generate() {
    const ask = genPrompt.trim();
    if (!ask) return;
    setGenerating(true);
    setProposal(null);
    try {
      const prompt = `You are extending ConceptV's component system. The brand uses CSS variables: --accent-gold (#E0C010), --accent-gold-soft, --accent-gold-50, --accent-bronze (#988058), --fg-primary, --fg-secondary, --bg-surface, --bg-canvas, --bg-muted, --border-default, --r-md (8px), --r-lg (12px). Existing button base style: 1.5px border, 9px 14px padding, var(--r-md) radius, 600/12px DM Sans font.

The user wants: ${ask}

Generate ONE component variant. Return its spec as JSON:
{
  "name": "<short kebab-case name>",
  "group": "<one of: Buttons | Inputs | Cards | Chips | Panels>",
  "desc": "<one-line description>",
  "html": "<inline-styled HTML for the default state, ideally a single tag>",
  "states": {
    "hover": "<modified inline-styled HTML for hover state (only show what visually changes)>",
    "disabled": "<modified inline-styled HTML for disabled state>"
  }
}

Use ONLY inline styles with CSS vars or hex colours from the palette above. Keep markup short (no nested wrappers unless needed). Default state must be visually distinct from existing variants.

Respond as compact JSON only, no prose, no markdown fences.`;
      const reply = await window.CV_AI.complete(prompt);
      let parsed = null;
      try { parsed = JSON.parse(reply); }
      catch {
        const m = String(reply).match(/\{[\s\S]*\}/);
        if (m) { try { parsed = JSON.parse(m[0]); } catch {} }
      }
      if (parsed && parsed.name && parsed.html) {
        setProposal(parsed);
      } else {
        window.dsaToast?.('Vi returned something I could not parse. Try rephrasing.');
      }
    } catch {
      window.dsaToast?.('Generation failed. Try again.');
    } finally {
      setGenerating(false);
    }
  }

  function adopt() {
    if (!proposal) return;
    addGenerated({ ...proposal, id: 'gen-' + Date.now() });
    window.dsaToast?.(`Adopted "${proposal.name}" into Components`);
    setProposal(null);
    setGenOpen(false);
  }

  const groups = Object.keys(COMPONENT_GROUPS);
  const filteredGroups = selectedGroup ? [selectedGroup] : groups;

  return (
    <>
      <CanvasHeader
        title="Components"
        sub={`${total} patterns · live previews across default / hover / active / disabled states`}
        actions={<button className="dsa-btn dsa-btn--ai" onClick={() => setGenOpen(o => !o)}>
          <ViShape size={14}/> Generate variant
        </button>}
      />
      <div className="dsa-canvas-body">

        {genOpen && (
          <div className="dsa-gen-panel">
            <div className="dsa-gen-head">
              <ViShape size={18}/>
              <span className="dsa-gen-title">Generate a new component variant</span>
              <button className="dsa-gen-close" onClick={() => { setGenOpen(false); setProposal(null); }}>✕</button>
            </div>
            <textarea
              className="dsa-gen-input" rows="2"
              placeholder='Describe the variant. e.g. "A destructive button — red border, red text, becomes filled red on hover"'
              value={genPrompt} onChange={e => setGenPrompt(e.target.value)}
            />
            <div className="dsa-gen-actions">
              <span className="dsa-gen-hint">Vi will return inline-styled HTML using your token system, plus hover and disabled states.</span>
              <button className="dsa-btn dsa-btn--primary" onClick={generate} disabled={generating || !genPrompt.trim()}>
                {generating ? 'Generating…' : 'Generate'}
              </button>
            </div>
            {generating && (
              <div className="dsa-gen-loading">
                <ViShape size={14} animated/> Vi is composing a component in your style…
              </div>
            )}
            {proposal && !generating && (
              <div style={{marginTop:14}}>
                <div style={{display:'flex',alignItems:'baseline',gap:10,marginBottom:10}}>
                  <span style={{font:'700 14px/1 var(--font-display)',color:'var(--fg-primary)'}}>{proposal.name}</span>
                  <span style={{font:'500 10px/1 var(--font-body)',color:'var(--accent-bronze)',letterSpacing:'0.08em',textTransform:'uppercase'}}>{proposal.group}</span>
                </div>
                <p style={{font:'400 12px/1.5 var(--font-body)',color:'var(--fg-secondary)',margin:'0 0 12px'}}>{proposal.desc}</p>
                <ComponentStates html={proposal.html} states={proposal.states} highlight/>
                <div style={{display:'flex',gap:8,justifyContent:'flex-end',marginTop:12}}>
                  <button className="dsa-btn dsa-btn--ghost" onClick={() => setProposal(null)}>Discard</button>
                  <button className="dsa-btn dsa-btn--primary" onClick={adopt}>Adopt into Components</button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Group filter pills */}
        <div className="dsa-cat-bar">
          <button className={!selectedGroup ? 'active' : ''} onClick={() => setSelectedGroup(null)}>All</button>
          {groups.map(g => (
            <button key={g} className={selectedGroup === g ? 'active' : ''} onClick={() => setSelectedGroup(g)}>
              {g} · {COMPONENT_GROUPS[g].length}
            </button>
          ))}
          {generated.length > 0 && (
            <button className={selectedGroup === 'Generated' ? 'active' : ''} onClick={() => setSelectedGroup('Generated')}>
              ◆ Generated · {generated.length}
            </button>
          )}
        </div>

        {/* The galleries */}
        {selectedGroup === 'Generated' ? (
          <div className="dsa-section">
            <div className="dsa-section-head">
              <h3 className="dsa-section-title">Generated this session · {generated.length}</h3>
            </div>
            <div style={{display:'grid',gridTemplateColumns:'1fr',gap:14}}>
              {generated.map(c => <ComponentCard key={c.id} c={c} generated/>)}
            </div>
          </div>
        ) : (
          filteredGroups.map(group => (
            <div className="dsa-section" key={group}>
              <div className="dsa-section-head">
                <h3 className="dsa-section-title">{group}</h3>
                <span className="dsa-section-meta">{COMPONENT_GROUPS[group].length} variants</span>
              </div>
              <div style={{display:'grid',gridTemplateColumns:'1fr',gap:14}}>
                {COMPONENT_GROUPS[group].map(c => <ComponentCard key={c.id} c={c}/>)}
              </div>
            </div>
          ))
        )}

      </div>
    </>
  );
}

// ============================================================
// Component card — renders the same component in every state
// ============================================================
function ComponentCard({ c, generated }) {
  return (
    <div className="dsa-card" style={{padding:18}}>
      <div style={{display:'flex',alignItems:'baseline',gap:10,marginBottom:6}}>
        <h4 style={{font:'700 14px/1 var(--font-display)',color:'var(--fg-primary)',margin:0,letterSpacing:'-0.01em'}}>{c.name}</h4>
        {generated && <span style={{font:'700 9px/1 var(--font-body)',color:'var(--accent-gold)',letterSpacing:'0.06em',textTransform:'uppercase',background:'var(--accent-gold-soft)',padding:'3px 6px',borderRadius:3}}>generated</span>}
        <span style={{font:'500 10px/1 var(--font-mono)',color:'var(--fg-muted)',marginLeft:'auto'}}>{c.id}</span>
      </div>
      <p style={{font:'400 12px/1.5 var(--font-body)',color:'var(--fg-secondary)',margin:'0 0 14px',maxWidth:680}}>{c.desc}</p>
      {generated
        ? <ComponentStates html={c.html} states={c.states}/>
        : <BuiltinStates id={c.id}/>
      }
    </div>
  );
}

// State grid for AI-generated components (HTML strings)
function ComponentStates({ html, states, highlight }) {
  return (
    <div style={{
      display:'grid',gridTemplateColumns:'repeat(auto-fit, minmax(160px, 1fr))',gap:0,
      background:'var(--bg-canvas)',borderRadius:'var(--r-md)',overflow:'hidden',
      border: highlight ? '1.5px solid var(--accent-gold)' : '1px solid var(--border-faint)',
    }}>
      <StateCell label="default" html={html}/>
      <StateCell label="hover" html={states?.hover || html}/>
      <StateCell label="disabled" html={states?.disabled || html} opacity={0.45}/>
    </div>
  );
}

function StateCell({ label, html, opacity }) {
  return (
    <div style={{
      padding:'18px 14px',display:'flex',flexDirection:'column',alignItems:'center',gap:10,
      borderRight:'1px solid var(--border-faint)',
      minHeight:96,justifyContent:'center',
      opacity: opacity ?? 1,
    }}>
      <div dangerouslySetInnerHTML={{__html: html || ''}}/>
      <div style={{font:'600 9px/1 var(--font-body)',color:'var(--fg-muted)',letterSpacing:'0.08em',textTransform:'uppercase'}}>{label}</div>
    </div>
  );
}

// ============================================================
// Built-in component renderers — show real React-styled previews
// ============================================================
function BuiltinStates({ id }) {
  const variants = {
    'btn-primary':   ['default', 'hover', 'disabled'],
    'btn-outline':   ['default', 'hover', 'disabled'],
    'btn-dashed':    ['default', 'hover'],
    'btn-ghost':     ['default', 'hover'],
    'btn-dark':      ['default', 'hover'],
    'btn-ai':        ['default', 'hover'],
    'in-text':       ['default', 'focus', 'disabled'],
    'in-search':     ['default', 'focus'],
    'in-textarea':   ['default', 'focus'],
    'check':         ['off', 'on'],
    'card-surface':  ['default'],
    'card-media':    ['image', 'video'],
    'card-drop':     ['default', 'hover'],
    'chip-status':   ['pending', 'success', 'error'],
    'chip-task':     ['yellow', 'green', 'blue'],
    'badge':         ['default', 'count'],
    'panel-section': ['default'],
    'panel-dark':    ['default'],
  };
  const states = variants[id] || ['default'];
  return (
    <div style={{
      display:'grid',gridTemplateColumns:`repeat(${states.length}, 1fr)`,
      background:'var(--bg-canvas)',borderRadius:'var(--r-md)',overflow:'hidden',
      border:'1px solid var(--border-faint)',
    }}>
      {states.map(state => (
        <div key={state} style={{
          padding:'24px 16px',display:'flex',flexDirection:'column',alignItems:'center',gap:12,
          borderRight:'1px solid var(--border-faint)',minHeight:120,justifyContent:'center',
        }}>
          <Renderer id={id} state={state}/>
          <div style={{font:'600 9px/1 var(--font-body)',color:'var(--fg-muted)',letterSpacing:'0.08em',textTransform:'uppercase'}}>{state}</div>
        </div>
      ))}
    </div>
  );
}

function Renderer({ id, state }) {
  // Buttons
  if (id === 'btn-primary') {
    const isHover = state === 'hover';
    return <button disabled={state==='disabled'} style={{
      background: isHover ? 'var(--accent-gold-hover)' : 'var(--accent-gold)',
      color:'var(--fg-primary)',border:'1.5px solid var(--accent-gold)',
      padding:'9px 16px',borderRadius:'var(--r-md)',font:'600 12px/1 var(--font-body)',
      cursor: state==='disabled' ? 'not-allowed' : 'pointer',
      opacity: state==='disabled' ? 0.45 : 1,
    }}>Publish</button>;
  }
  if (id === 'btn-outline') {
    return <button disabled={state==='disabled'} style={{
      background: state==='hover' ? 'var(--accent-gold-soft)' : 'transparent',
      color:'var(--fg-primary)',border:'1.5px solid var(--accent-gold)',
      padding:'9px 16px',borderRadius:'var(--r-md)',font:'600 12px/1 var(--font-body)',
      cursor:'pointer',opacity: state==='disabled' ? 0.45 : 1,
    }}>Filter</button>;
  }
  if (id === 'btn-dashed') {
    return <button style={{
      background: state==='hover' ? 'var(--accent-gold-50)' : 'transparent',
      color: state==='hover' ? 'var(--fg-primary)' : 'var(--fg-secondary)',
      border:'1.5px dashed var(--accent-gold-dashed)',
      padding:'9px 16px',borderRadius:'var(--r-md)',font:'600 12px/1 var(--font-body)',cursor:'pointer',
    }}>Add Style Switch</button>;
  }
  if (id === 'btn-ghost') {
    return <button style={{
      background: state==='hover' ? 'var(--bg-muted)' : 'transparent',
      color:'var(--fg-primary)',border:'1.5px solid transparent',
      padding:'9px 16px',borderRadius:'var(--r-md)',font:'600 12px/1 var(--font-body)',cursor:'pointer',
    }}>Manage</button>;
  }
  if (id === 'btn-dark') {
    return <button style={{
      background: state==='hover' ? 'var(--bg-dark-2)' : 'var(--bg-dark)',
      color:'var(--fg-inverse)',border:'none',
      padding:'10px 18px',borderRadius:'var(--r-md)',
      font:'700 11px/1 var(--font-body)',letterSpacing:'0.12em',cursor:'pointer',
    }}>MENU</button>;
  }
  if (id === 'btn-ai') {
    return <button style={{
      background: state==='hover' ? 'var(--bg-dark-2)' : 'var(--bg-dark)',
      color:'var(--fg-inverse)',border:'none',
      padding:'9px 14px',borderRadius:'var(--r-md)',
      font:'600 12px/1 var(--font-body)',cursor:'pointer',
      display:'inline-flex',alignItems:'center',gap:7,
    }}><ViShape size={14}/> Generate</button>;
  }
  // Inputs
  if (id === 'in-text') {
    const focus = state==='focus';
    return <input
      placeholder="Hub name"
      defaultValue="Tower East"
      disabled={state==='disabled'}
      style={{
        border:'1.5px solid var(--accent-gold)',
        boxShadow: focus ? '0 0 0 3px var(--accent-gold-soft)' : 'none',
        padding:'10px 12px',borderRadius:'var(--r-md)',
        background:'var(--bg-surface)',outline:'none',
        font:'400 13px/1 var(--font-body)',color:'var(--fg-primary)',
        width:160,opacity: state==='disabled' ? 0.5 : 1,
      }}/>;
  }
  if (id === 'in-search') {
    const focus = state==='focus';
    return (
      <div style={{
        display:'flex',alignItems:'center',gap:8,
        padding:'10px 12px',borderRadius:'var(--r-md)',
        border:'1.5px solid var(--accent-gold)',
        boxShadow: focus ? '0 0 0 3px var(--accent-gold-soft)' : 'none',
        background:'var(--bg-surface)',width:200,
      }}>
        <CvIcon name="search" size={14} tone="muted"/>
        <input style={{flex:1,border:'none',outline:'none',font:'400 13px/1 var(--font-body)',background:'transparent'}} placeholder="Search"/>
      </div>
    );
  }
  if (id === 'in-textarea') {
    return <textarea
      placeholder="Description"
      defaultValue="Light-filled corner apartment with…"
      rows="3"
      style={{
        border:'1.5px solid var(--accent-gold)',
        boxShadow: state==='focus' ? '0 0 0 3px var(--accent-gold-soft)' : 'none',
        padding:'10px 12px',borderRadius:'var(--r-md)',
        background:'var(--bg-surface)',outline:'none',resize:'none',
        font:'400 12px/1.5 var(--font-body)',color:'var(--fg-primary)',
        width:200,
        fontFamily:'var(--font-body)',
      }}/>;
  }
  if (id === 'check') {
    const on = state === 'on';
    return (
      <span style={{display:'inline-flex',alignItems:'center',gap:10,cursor:'pointer'}}>
        <span style={{
          width:18,height:18,borderRadius:4,flex:'none',position:'relative',
          background: on ? 'var(--accent-gold)' : 'var(--accent-gold-soft)',
        }}>
          {on && <span style={{position:'absolute',left:5,top:1.5,width:5,height:10,borderRight:'2px solid var(--fg-primary)',borderBottom:'2px solid var(--fg-primary)',transform:'rotate(45deg)'}}/>}
        </span>
        <span style={{font:'500 13px/1 var(--font-body)',color:'var(--fg-primary)'}}>Information Panel</span>
      </span>
    );
  }
  // Cards
  if (id === 'card-surface') {
    return (
      <div style={{background:'var(--bg-surface)',borderRadius:'var(--r-lg)',boxShadow:'var(--shadow-card)',padding:16,width:200}}>
        <div style={{font:'600 10px/1 var(--font-body)',color:'var(--fg-muted)',letterSpacing:'0.08em',textTransform:'uppercase',marginBottom:8}}>Card</div>
        <div style={{height:60,background:'linear-gradient(135deg,#E8E2CC,#D0C098)',borderRadius:4,marginBottom:8}}/>
        <div style={{font:'500 12px/1 var(--font-body)',color:'var(--fg-secondary)'}}>Tower East — North</div>
      </div>
    );
  }
  if (id === 'card-media') {
    if (state === 'video') {
      return (
        <div style={{background:'var(--bg-sunken)',borderRadius:4,width:160,aspectRatio:'16/10',display:'flex',alignItems:'center',justifyContent:'center'}}>
          <div style={{width:36,height:36,borderRadius:'50%',background:'rgba(31,26,18,.08)',display:'flex',alignItems:'center',justifyContent:'center',color:'var(--accent-bronze)'}}>▶</div>
        </div>
      );
    }
    return <div style={{background:'var(--bg-sunken)',borderRadius:4,width:160,aspectRatio:'16/10'}}/>;
  }
  if (id === 'card-drop') {
    return (
      <div style={{
        background: state === 'hover' ? 'var(--accent-gold-50)' : 'var(--bg-sunken)',
        border:'2px dashed var(--border-dashed)',borderRadius:'var(--r-md)',
        width:160,aspectRatio:'16/10',
        display:'flex',alignItems:'center',justifyContent:'center',cursor:'pointer',
      }}>
        <div style={{width:36,height:36,borderRadius:'50%',background:'var(--accent-gold)',display:'flex',alignItems:'center',justifyContent:'center',font:'400 22px/1 var(--font-body)',color:'var(--fg-primary)'}}>+</div>
      </div>
    );
  }
  // Chips
  if (id === 'chip-status') {
    const m = {
      pending: { bg:'var(--bg-canvas)', dot:'#E5C547', label:'Pending' },
      success: { bg:'var(--bg-canvas)', dot:'#5A8A4A', label:'Approved' },
      error:   { bg:'var(--bg-canvas)', dot:'#C24A3C', label:'Rejected' },
    }[state];
    return (
      <span style={{display:'inline-flex',alignItems:'center',gap:8,padding:'6px 10px',borderRadius:'var(--r-sm)',background:m.bg,font:'500 12px/1 var(--font-body)',color:'var(--fg-primary)',border:'1px solid var(--border-default)'}}>
        <span style={{width:8,height:8,borderRadius:'50%',background:m.dot,display:'inline-block'}}/>
        {m.label}
      </span>
    );
  }
  if (id === 'chip-task') {
    const m = {
      yellow: { bg:'#FBF1C0', dot:'#E5C547' },
      green:  { bg:'#E6EFDB', dot:'#5A8A4A' },
      blue:   { bg:'#DCE7F3', dot:'#4A78B8' },
    }[state];
    return (
      <span style={{display:'inline-flex',alignItems:'center',gap:7,padding:'5px 9px',borderRadius:'var(--r-xs)',background:m.bg,font:'500 11px/1 var(--font-body)',color:'var(--fg-primary)'}}>
        <span style={{width:7,height:7,borderRadius:'50%',background:m.dot,display:'inline-block'}}/>
        Site survey
      </span>
    );
  }
  if (id === 'badge') {
    return (
      <span style={{position:'relative',display:'inline-flex'}}>
        <CvIcon name="bell" size={26} tone="ink"/>
        <span style={{
          position:'absolute',top:-4,right:-6,minWidth:18,height:18,padding:'0 5px',
          borderRadius:999,background:'#F04325',color:'white',
          font:'700 10px/18px var(--font-body)',textAlign:'center',
        }}>{state === 'count' ? '12' : '3'}</span>
      </span>
    );
  }
  // Panels
  if (id === 'panel-section') {
    return (
      <div style={{background:'var(--accent-gold-50)',borderRadius:'var(--r-lg)',padding:'16px 18px',width:240}}>
        <div style={{font:'600 11px/1 var(--font-body)',color:'var(--fg-primary)',marginBottom:8}}>Menu Options</div>
        <div style={{display:'flex',alignItems:'center',gap:10,marginBottom:6}}>
          <span style={{width:16,height:16,borderRadius:4,background:'var(--accent-gold)',position:'relative'}}>
            <span style={{position:'absolute',left:5,top:1.5,width:4,height:8,borderRight:'2px solid var(--fg-primary)',borderBottom:'2px solid var(--fg-primary)',transform:'rotate(45deg)'}}/>
          </span>
          <span style={{font:'500 12px/1 var(--font-body)',color:'var(--fg-primary)'}}>Information Panel</span>
        </div>
        <div style={{display:'flex',alignItems:'center',gap:10}}>
          <span style={{width:16,height:16,borderRadius:4,background:'var(--accent-gold-soft)'}}/>
          <span style={{font:'500 12px/1 var(--font-body)',color:'var(--fg-primary)'}}>Floorplan</span>
        </div>
      </div>
    );
  }
  if (id === 'panel-dark') {
    return (
      <div style={{background:'rgba(31,26,18,.92)',backdropFilter:'blur(8px)',borderRadius:'var(--r-md)',padding:10,display:'flex',flexDirection:'column',gap:2,width:180,color:'var(--fg-inverse)'}}>
        <div style={{padding:'8px 12px',borderRadius:'var(--r-sm)',display:'flex',alignItems:'center',gap:10,font:'500 12px/1 var(--font-body)',background:'rgba(251,247,236,.08)'}}>
          <CvIcon name="info-circle" size={14} tone="cream"/> Info
        </div>
        <div style={{padding:'8px 12px',borderRadius:'var(--r-sm)',display:'flex',alignItems:'center',gap:10,font:'500 12px/1 var(--font-body)',color:'var(--fg-inverse)'}}>
          <CvIcon name="floorplan" size={14} tone="cream"/> Floorplan
        </div>
      </div>
    );
  }
  return null;
}

window.Components = Components;
window.COMPONENT_GROUPS = COMPONENT_GROUPS;
