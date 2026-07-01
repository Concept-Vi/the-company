// atomicity/Home.jsx
// ============================================================================
// Home — the orientation the app was missing. Says what AtomiCity is in one
// line, shows your brand alive, and leads to the few things you actually do.
// No jargon, no registries — just doors. Composed from AcKit + the brand tokens.
// ============================================================================
const { useReducer: useReducer_hm } = React;

const DOORS = [
  { id: 'sec/foundations', icon: 'color-swatches', title: 'Your brand', desc: 'The colours, type and feel of everything. See it, and tune it live.', kind: 'palette' },
  { id: 'sec/explore', icon: 'shuffle', title: 'Explore looks', desc: 'Generate fresh style directions, steer by taste, and make the ones you love real.', kind: 'explore' },
  { id: 'sec/ingest', icon: 'cloud-upload', title: 'Bring in inspiration', desc: 'Drop a brand doc, some copy, or an image — Vi reads it for ideas worth keeping.', kind: 'ingest' },
];
const PALETTE = ['--paper', '--paper-2', '--accent-tan', '--accent-bronze', '--accent-gold', '--ink'];

function AcHome() {
  const [, force] = useReducer_hm(x => x + 1, 0);
  const nav = (id) => window.ATOMICITY && window.ATOMICITY.openNode(id);
  const ask = (t) => window.ATOMICITY && window.ATOMICITY.askVi(t);

  return (
    <div className="hm">
      <header className="hm-hero">
        <div className="hm-hero-mark"><ViShape size={40}/></div>
        <h1>Welcome to Atomi<b>City</b></h1>
        <p>Your living design system. See your brand, shape it with V<span className="i">i</span>, and bring in anything that inspires it — every change flows through the whole product at once.</p>
      </header>

      <div className="hm-doors stagger">
        {DOORS.map((d, i) => (
          <button key={d.id} className="hm-door enter-up" style={{ '--i': i }} onClick={() => nav(d.id)}>
            <span className="hm-door-ic"><CvIcon name={d.icon} size={20} tone="gold" circle/></span>
            <span className="hm-door-title">{d.title}</span>
            <span className="hm-door-desc">{d.desc}</span>
            <span className="hm-door-go">Open <CvIcon name="play" size={11} tone="bronze"/></span>
          </button>
        ))}
        <button className="hm-door hm-door--vi enter-up" style={{ '--i': 3 }} onClick={() => ask('Give me a quick tour — what can I do here?')}>
          <span className="hm-door-ic"><ViShape size={22}/></span>
          <span className="hm-door-title">Ask V<span className="i">i</span></span>
          <span className="hm-door-desc">She knows the whole system. Ask anything, or just say what you’re trying to do.</span>
          <span className="hm-door-go">Start talking <CvIcon name="play" size={11} tone="bronze"/></span>
        </button>
      </div>

      <section className="hm-snapshot">
        <div className="hm-snap-cap">Your brand right now</div>
        <div className="hm-snap-grid">
          <button className="hm-palette" onClick={() => nav('sec/foundations')} title="Open your brand">
            {PALETTE.map(t => <span key={t} className="hm-sw" style={{ background: `var(${t})` }}/>)}
            <span className="hm-palette-cap">Paper · Tan · Bronze · Gold · Ink</span>
          </button>
          <div className="hm-type">
            <div className="hm-type-display">Sora</div>
            <div className="hm-type-body">DM Sans — the everyday reading voice across every surface.</div>
          </div>
          <div className="hm-mini-card">
            <div className="hm-mini-eyebrow">Property Wizard</div>
            <div className="hm-mini-title">14 Eclipse Boulevard</div>
            <div className="hm-mini-price">$1.84m</div>
            <button className="hm-mini-btn">Book inspection</button>
          </div>
        </div>
        <p className="hm-snap-foot">This is your brand applied to a real product surface. Change a colour or the roundness in <button className="hm-link" onClick={() => nav('sec/foundations')}>Your brand</button> and watch it — and the whole app — shift.</p>
      </section>
    </div>
  );
}

window.AcHome = AcHome;
