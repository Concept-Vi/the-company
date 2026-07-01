// components/KitPreviews.jsx — mini thumbnails of each UI kit that respond to live token edits
//
// Used inside the Colors canvas (below "Live preview"). Each thumbnail is a stripped-down
// vector of a real surface from one of the UI kits — Platform sidebar/toolbar, Virtual Hub
// menu, Vi workspace. They render from CSS custom properties, so any token edit cascades.

function KitPreviews({ tokens }) {
  // If a tokens map is provided, wrap in a div with inline CSS variable overrides
  // so this thumb renders that palette regardless of the current document state.
  // Useful for compare mode (current vs snapshot).
  const overrides = {};
  if (tokens) {
    for (const [name, hex] of Object.entries(tokens)) {
      if (!hex) continue;
      overrides[`--${name}`] = hex;
      if (name === 'gold') overrides['--accent-gold'] = hex;
      if (name === 'gold-hover') overrides['--accent-gold-hover'] = hex;
      if (name === 'gold-soft') overrides['--accent-gold-soft'] = hex;
      if (name === 'gold-50') overrides['--accent-gold-50'] = hex;
      if (name === 'bronze') overrides['--accent-bronze'] = hex;
      if (name === 'canvas') overrides['--bg-canvas'] = hex;
      if (name === 'surface') overrides['--bg-surface'] = hex;
      if (name === 'dark') overrides['--bg-dark'] = hex;
      if (name === 'muted') overrides['--bg-muted'] = hex;
      if (name === 'sunken') overrides['--bg-sunken'] = hex;
      if (name === 'fg-primary') overrides['--fg-primary'] = hex;
      if (name === 'fg-secondary') overrides['--fg-secondary'] = hex;
      if (name === 'fg-muted') overrides['--fg-muted'] = hex;
    }
  }
  return (
    <div style={{display:'grid',gridTemplateColumns:'repeat(3, 1fr)',gap:14, ...overrides}}>
      <PlatformThumb/>
      <HubThumb/>
      <ViThumb/>
    </div>
  );
}

function ThumbFrame({ label, children, bg, link }) {
  return (
    <div style={{
      borderRadius:'var(--r-md)',overflow:'hidden',
      border:'1px solid var(--border-faint)',
      display:'flex',flexDirection:'column',
      background: bg || 'var(--bg-surface)',
    }}>
      <div style={{
        padding:'8px 12px',display:'flex',alignItems:'center',gap:6,
        font:'600 10px/1 var(--font-body)',color:'var(--fg-muted)',letterSpacing:'0.08em',textTransform:'uppercase',
        borderBottom:'1px solid var(--border-faint)',
        background:'var(--bg-surface)',
      }}>
        {label}
        <span style={{marginLeft:'auto',font:'500 10px/1 var(--font-body)',letterSpacing:0,textTransform:'none',color:'var(--fg-muted)'}}>{link}</span>
      </div>
      <div style={{flex:1,padding:14,minHeight:130}}>{children}</div>
    </div>
  );
}

// --- Platform dashboard surface (sidebar + toolbar) ---
function PlatformThumb() {
  return (
    <ThumbFrame label="Platform" link="dashboard">
      <div style={{display:'grid',gridTemplateColumns:'70px 1fr',gap:8,height:'100%'}}>
        <div style={{display:'flex',flexDirection:'column',gap:4}}>
          {['Projects','Gallery','Brand Kit','Calendar'].map((label, i) => (
            <div key={label} style={{
              padding:'4px 6px',
              borderRadius:4,
              font:'500 9px/1.2 var(--font-body)',color:'var(--fg-primary)',
              ...(i===1 ? { background:'var(--bg-surface)', border:'1px dashed var(--accent-gold)', boxShadow:'var(--shadow-xs)' } : { border:'1px solid transparent' }),
            }}>{label}</div>
          ))}
        </div>
        <div>
          <div style={{font:'700 16px/1 var(--font-display)',color:'var(--accent-bronze)',letterSpacing:'-0.02em',marginBottom:8}}>Gallery</div>
          <div style={{display:'flex',gap:4,marginBottom:8}}>
            <PreviewBtn primary>Create</PreviewBtn>
            <PreviewBtn>Filter</PreviewBtn>
          </div>
          <div style={{display:'grid',gridTemplateColumns:'repeat(4,1fr)',gap:3}}>
            {Array.from({length:8}).map((_,i)=>(
              <div key={i} style={{aspectRatio:'1',background:'var(--bg-sunken)',borderRadius:2}}/>
            ))}
          </div>
        </div>
      </div>
    </ThumbFrame>
  );
}

// --- Virtual Hub viewer surface (dark overlay + menu) ---
function HubThumb() {
  return (
    <ThumbFrame label="Virtual Hub" link="viewer">
      <div style={{
        position:'relative',height:'100%',minHeight:130,
        background:'linear-gradient(165deg, #4A3E2E 0%, #6B5A3F 25%, #C9A86E 55%, #E4CC9E 75%, #8B7251 100%)',
        borderRadius:'var(--r-sm)',overflow:'hidden',
      }}>
        {/* Top-left bug */}
        <div style={{
          position:'absolute',top:8,left:8,
          background:'rgba(31,26,18,.7)',backdropFilter:'blur(8px)',
          padding:'5px 8px',borderRadius:6,
          font:'700 11px/1 var(--font-display)',color:'var(--fg-inverse)',letterSpacing:'-0.02em',
        }}>Concept<span style={{color:'var(--accent-gold)'}}>V</span></div>
        {/* Right info panel */}
        <div style={{
          position:'absolute',top:8,right:8,bottom:8,width:80,
          background:'var(--bg-surface)',borderRadius:6,padding:8,
          display:'flex',flexDirection:'column',gap:4,
        }}>
          <div style={{font:'700 9px/1.1 var(--font-display)',color:'var(--accent-bronze)',textAlign:'center'}}>Apt A</div>
          <div style={{height:1,background:'var(--border-faint)'}}/>
          <div style={{display:'flex',justifyContent:'space-around',color:'var(--accent-bronze)',font:'500 8px/1 var(--font-body)'}}>
            <span>2bd</span><span>2ba</span>
          </div>
          <div style={{height:1,background:'var(--border-faint)'}}/>
          <div style={{background:'var(--bg-muted)',height:6,borderRadius:2}}/>
          <div style={{background:'var(--bg-muted)',height:6,borderRadius:2,width:'70%'}}/>
          <div style={{marginTop:'auto',padding:'4px 6px',background:'var(--accent-gold)',color:'var(--fg-primary)',font:'600 9px/1 var(--font-body)',borderRadius:3,textAlign:'center'}}>Enquire</div>
        </div>
        {/* Bottom MENU */}
        <div style={{
          position:'absolute',bottom:8,left:'50%',transform:'translateX(-50%)',
          background:'rgba(31,26,18,.92)',color:'var(--fg-inverse)',
          padding:'5px 12px',borderRadius:4,
          font:'700 9px/1 var(--font-body)',letterSpacing:'0.12em',
        }}>MENU</div>
      </div>
    </ThumbFrame>
  );
}

// --- Vi workspace surface (chat + tasks + brochure) ---
function ViThumb() {
  return (
    <ThumbFrame label="Vi workspace" link="3-pane">
      <div style={{display:'grid',gridTemplateColumns:'1fr 1fr 1fr',gap:4,height:'100%'}}>
        {/* Chat */}
        <div style={{display:'flex',flexDirection:'column',gap:3}}>
          <div style={{font:'700 8px/1 var(--font-display)',color:'var(--accent-bronze)'}}>Chat</div>
          <ViBubble/>
          <ViBubble user/>
          <ViBubble/>
        </div>
        {/* Tasks */}
        <div style={{display:'flex',flexDirection:'column',gap:3}}>
          <div style={{font:'700 8px/1 var(--font-display)',color:'var(--accent-bronze)'}}>Tasks</div>
          <TaskMini done/>
          <TaskMini active/>
          <TaskMini/>
        </div>
        {/* Output */}
        <div style={{display:'flex',flexDirection:'column',gap:3}}>
          <div style={{font:'700 8px/1 var(--font-display)',color:'var(--accent-bronze)'}}>Output</div>
          <div style={{
            background:'linear-gradient(165deg, #4A3E2E 0%, #C9A86E 70%, #8B7251 100%)',
            height:24,borderRadius:2,
          }}/>
          <div style={{display:'flex',gap:2}}>
            {[1,2,3,4].map(i => <div key={i} style={{flex:1,height:14,background:'var(--accent-gold-faint)',border:'1px solid var(--accent-gold)',borderRadius:2}}/>)}
          </div>
          <div style={{background:'var(--bg-muted)',height:5,borderRadius:1}}/>
          <div style={{background:'var(--bg-muted)',height:5,borderRadius:1,width:'80%'}}/>
        </div>
      </div>
    </ThumbFrame>
  );
}

function PreviewBtn({ primary, children }) {
  return (
    <span style={{
      font:'600 9px/1 var(--font-body)',padding:'5px 8px',borderRadius:4,
      ...(primary ? { background:'var(--accent-gold)', color:'var(--fg-primary)', border:'1px solid var(--accent-gold)' }
                  : { background:'transparent', color:'var(--fg-primary)', border:'1px solid var(--accent-gold)' })
    }}>{children}</span>
  );
}

function ViBubble({ user }) {
  return (
    <div style={{display:'flex',gap:3,alignItems:'flex-start'}}>
      <span style={{
        width:10,height:10,flex:'none',
        ...(user ? { background:'var(--bg-muted)', borderRadius:'50%' }
                 : { background:'var(--bg-surface)', transform:'rotate(45deg)', border:'1.5px solid var(--accent-gold)' })
      }}/>
      <div style={{flex:1,display:'flex',flexDirection:'column',gap:2}}>
        <div style={{background:'var(--bg-muted)',height:4,borderRadius:1}}/>
        <div style={{background:'var(--bg-muted)',height:4,borderRadius:1,width:'70%'}}/>
      </div>
    </div>
  );
}

function TaskMini({ active, done }) {
  return (
    <div style={{
      display:'flex',alignItems:'center',gap:4,
      padding:'4px 6px',borderRadius:3,
      background: active ? 'var(--accent-gold-faint)' : 'var(--bg-surface)',
      border: '1px solid ' + (active ? 'var(--accent-gold)' : 'var(--border-default)'),
      opacity: !active && !done ? 0.55 : 1,
    }}>
      <span style={{
        width:5,height:5,borderRadius:'50%',
        background: done ? 'var(--status-success)' : active ? 'var(--accent-gold)' : 'var(--fg-muted)',
      }}/>
      <div style={{flex:1,background:'var(--bg-muted)',height:3,borderRadius:1}}/>
    </div>
  );
}

window.KitPreviews = KitPreviews;
