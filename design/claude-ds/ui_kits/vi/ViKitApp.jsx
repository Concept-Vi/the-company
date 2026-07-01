// App.jsx — Vi Workspace, brochure-builder demo
const { useState: useState_v } = React;

const NAV = [
  { id: 'workspace', glyph: '◆', label: 'Workspace' },
  { id: 'history',   glyph: '⌛', label: 'History' },
  { id: 'templates', glyph: '📄', label: 'Templates' },
  { id: 'sources',   glyph: '🔗', label: 'Connected sources' },
  { id: 'settings',  glyph: '⚙',  label: 'Vi settings' },
];

// ---------- Step definitions ----------
// Each step is a snapshot of: chat messages, task layers, brochure filled fields, composer hint.
function buildLayers({ layer1, layer2, layer3 }) {
  return [
    {
      desc: 'Plans the task and decides what entities to read.',
      nodes: [
        { name: 'Plan brochure build', meta: 'Strategy locked in 0.4s', state: layer1 },
      ],
    },
    {
      desc: 'Spawns clones that read the connected entities in parallel.',
      nodes: [
        { name: 'Read · Brand Kit',     meta: '4 colours · 2 logos',      state: layer2[0] },
        { name: 'Read · Master Info',   meta: '12 fields · 2 gaps',       state: layer2[1] },
        { name: 'Read · Gallery',       meta: '8 hero images',            state: layer2[2] },
        { name: 'Read · Analytics',     meta: '36 mo. occupancy',         state: layer2[3] },
      ],
    },
    {
      desc: 'Executes the brochure assembly and saves output to file.',
      nodes: [
        { name: 'Hero + palette',    state: layer3[0] },
        { name: 'Stats grid',        state: layer3[1] },
        { name: 'Description copy',  state: layer3[2] },
        { name: 'Finalize & export', state: layer3[3] },
      ],
    },
  ];
}

const TIMESTAMPS = ['09:41', '09:41', '09:42', '09:42', '09:43', '09:43'];

function ViKitApp() {
  const [step, setStep] = useState_v(0);
  const [composer, setComposer] = useState_v('Build a brochure for Tower East from the Marketing template');
  const [priceInput, setPriceInput] = useState_v('');
  const [agentInput, setAgentInput] = useState_v('');
  const [priceSubmitted, setPriceSubmitted] = useState_v(false);
  const [agentSubmitted, setAgentSubmitted] = useState_v(false);

  function reset() {
    setStep(0);
    setComposer('Build a brochure for Tower East from the Marketing template');
    setPriceInput(''); setAgentInput('');
    setPriceSubmitted(false); setAgentSubmitted(false);
  }

  function send() {
    if (step === 0) {
      setStep(1);
      setComposer('');
      // Auto-advance reading state
      setTimeout(() => setStep(2), 1800);
    }
  }

  function submitPrice() {
    if (!priceInput.trim()) return;
    setPriceSubmitted(true);
    setTimeout(() => setStep(3), 600);
  }
  function submitAgent() {
    if (!agentInput.trim()) return;
    setAgentSubmitted(true);
    setTimeout(() => setStep(4), 600);
  }

  // ---------- Derived state ----------
  const layers =
    step === 0 ? buildLayers({ layer1: 'idle', layer2: ['idle','idle','idle','idle'], layer3: ['idle','idle','idle','idle'] }) :
    step === 1 ? buildLayers({ layer1: 'done', layer2: ['active','active','active','active'], layer3: ['idle','idle','idle','idle'] }) :
    step === 2 ? buildLayers({ layer1: 'done', layer2: ['done','done','done','done'], layer3: ['done','done','active','blocked'] }) :
    step === 3 ? buildLayers({ layer1: 'done', layer2: ['done','done','done','done'], layer3: ['done','done','done','active'] }) :
                 buildLayers({ layer1: 'done', layer2: ['done','done','done','done'], layer3: ['done','done','done','done'] });

  const filled =
    step === 0 ? { brand: false, stats: false, description: false, title: false, price: false, agent: false, finalize: false } :
    step === 1 ? { brand: false, stats: false, description: false, title: false, price: false, agent: false, finalize: false } :
    step === 2 ? { brand: true,  stats: true,  description: true,  title: true,  price: false, agent: false, finalize: false } :
    step === 3 ? { brand: true,  stats: true,  description: true,  title: true,  price: priceInput || '$2,450,000', agent: false, finalize: false } :
                 { brand: true,  stats: true,  description: true,  title: true,  price: priceInput, agent: agentInput, finalize: true };

  // ---------- Chat messages ----------
  const messages = [];
  if (step >= 1) {
    messages.push(
      <Message key="u0" from="user" time={TIMESTAMPS[0]}>
        Build a brochure for <b>Tower East</b> from the Marketing template.
      </Message>
    );
  }
  if (step >= 1) {
    messages.push(
      <Message key="v0" from={step === 1 ? 'vi-live' : 'vi'} time={TIMESTAMPS[1]}>
        <div className="vi-msg-text" style={{marginBottom:8}}>
          On it. I'll read the entities connected to Tower East and assemble the brochure.
        </div>
        <ReadCard kind="brandkit"  entity="Brand Kit"   done={step >= 2}/>
        <ReadCard kind="master"    entity="Master Info" done={step >= 2}/>
        <ReadCard kind="gallery"   entity="Gallery"     done={step >= 2}/>
        <ReadCard kind="analytics" entity="Analytics"   done={step >= 2}/>
      </Message>
    );
  }
  if (step >= 2) {
    messages.push(
      <Message key="v1" from={step === 2 ? 'vi-live' : 'vi'} time={TIMESTAMPS[2]}>
        <div className="vi-msg-text">
          Brand, palette, stats, and description are filled.<br/>
          Two gaps from Master Info I need from you: <b>starting price</b> and <b>agent contact</b>.
        </div>
        <MissingPrompt
          label="Master Info"
          question="What's the starting price for the 2-bed apartments?"
          placeholder="e.g. $2,450,000"
          value={priceInput} onChange={setPriceInput} onSubmit={submitPrice}
          submitted={priceSubmitted}
        />
      </Message>
    );
  }
  if (step >= 3) {
    messages.push(
      <Message key="v2" from={step === 3 ? 'vi-live' : 'vi'} time={TIMESTAMPS[3]}>
        <div className="vi-msg-text">Locked in. One more — who should buyers contact?</div>
        <MissingPrompt
          label="Master Info"
          question="Agent name & contact (will appear in the footer)"
          placeholder="e.g. Sam Lin · sam@conceptv.io · +61 …"
          value={agentInput} onChange={setAgentInput} onSubmit={submitAgent}
          submitted={agentSubmitted}
        />
      </Message>
    );
  }
  if (step >= 4) {
    messages.push(
      <Message key="v3" from="vi" time={TIMESTAMPS[4]}>
        <div className="vi-msg-text" style={{marginBottom:8}}>
          Brochure is ready. I've published it back to the project files in three formats and queued the same content into the Tower East Landing Page draft.
        </div>
        <ApproveCard
          text="Tower East — Sky Apartments brochure"
          sub="3 formats · auto-synced to Landing Pages · revision saved"
          onApprove={reset}
        />
      </Message>
    );
  }
  // Step 0: empty chat, prompt user
  if (step === 0) {
    messages.push(
      <Message key="welcome" from="vi" time={TIMESTAMPS[0]}>
        <div className="vi-msg-text">
          Hi — I'm <b>V<span style={{color:'var(--accent-gold)'}}>i</span></b>. Pick a template + project and I'll read your connected entities, ask for anything missing, and consolidate the result.
        </div>
        <div className="vi-msg-text" style={{marginTop:8,color:'var(--fg-secondary)'}}>
          Try: <span className="accent">"Build a brochure for Tower East from the Marketing template"</span>
        </div>
      </Message>
    );
  }

  // ---------- Status pill ----------
  const statusPill =
    step === 1 ? <ViStatusPill live>Vi is reading 4 entities…</ViStatusPill> :
    step === 2 ? <ViStatusPill>Vi found 2 missing fields</ViStatusPill> :
    step === 3 ? <ViStatusPill>Vi is waiting on agent contact</ViStatusPill> :
    step === 4 ? <ViStatusPill>Vi finished · 3 outputs saved</ViStatusPill> :
                 <ViStatusPill>Vi is idle · awaiting prompt</ViStatusPill>;

  return (
    <div className="vi-shell">
      <aside className="vi-side">
        <div className="brand"><img src="../../assets/logos/conceptv-wordmark-black.png" alt="ConceptV"/></div>
        <div>
          <h4>Vi</h4>
          <div className="vi-nav">
            {NAV.map(n => (
              <button key={n.id} className={`vi-nav-item ${n.id==='workspace'?'active':''}`}>
                <span className="glyph" style={n.id==='workspace'?{color:'var(--accent-gold)'}:{}}>{n.glyph}</span>{n.label}
              </button>
            ))}
          </div>
        </div>
        <div style={{marginTop:'auto',padding:'12px 8px',font:'400 11px/1.4 var(--font-body)',color:'var(--fg-muted)'}}>
          <button onClick={reset} className="vi-nav-item" style={{font:'600 12px/1 var(--font-body)',color:'var(--accent-bronze)'}}>↺ Reset demo</button>
        </div>
      </aside>

      <div className="vi-workspace">
        <div className="vi-pane">
          <div className="vi-pane-header">
            <ViMark size={28} animated={step===1}/>
            <h2 className="vi-pane-title">Conversation</h2>
            <span className="vi-pane-sub">Tower East</span>
          </div>
          <ChatPanel
            value={composer} setValue={setComposer}
            onSend={send}
            disabled={step !== 0}
          >
            {messages}
          </ChatPanel>
        </div>

        <div className="vi-pane">
          <div className="vi-pane-header">
            <h2 className="vi-pane-title">Task tree</h2>
            <span className="vi-pane-sub normal" style={{marginLeft:14}}>{statusPill}</span>
          </div>
          <TaskTree layers={layers}/>
        </div>

        <div className="vi-pane">
          <div className="vi-pane-header">
            <h2 className="vi-pane-title">Output</h2>
            <span className="vi-pane-sub">Brochure · live</span>
          </div>
          <OutputPreview filled={filled}/>
        </div>
      </div>
    </div>
  );
}

const _mountApp = document.getElementById('app');
if (_mountApp) ReactDOM.createRoot(_mountApp).render(<ViKitApp/>);
