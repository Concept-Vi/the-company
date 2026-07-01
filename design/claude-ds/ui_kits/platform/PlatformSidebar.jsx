// Sidebar.jsx — left nav rail
const { useState } = React;

const NAV_ITEMS = [
  { id: 'projects',  glyph: '🗂️', label: 'Projects' },
  { id: 'dashboard', glyph: '⌨️', label: 'Dashboard Updates' },
  { id: 'landing',   glyph: '🌐', label: 'Landing Pages' },
  { id: 'files',     glyph: '📁', label: 'Files' },
  { id: 'gallery',   glyph: '📷', label: 'Gallery' },
  { id: 'brandkit',  glyph: '🎨', label: 'Brand Kit' },
];
const TOOL_ITEMS = [
  { id: 'calendar', glyph: '📅', label: 'Calendar' },
  { id: 'templates', glyph: '📄', label: 'Templates' },
  { id: 'pricing', glyph: '🛒', label: 'Pricing & Ordering' },
  { id: 'hubsettings', glyph: '🧭', label: 'Virtual Hub Settings' },
];

function Section({ title, defaultOpen = true, children }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div>
      <button className="cv-section-title" onClick={() => setOpen(!open)} style={{background:'none',border:'none',width:'100%',cursor:'pointer'}}>
        <span className="cv-section-title-label">{title}</span>
        <span className="chev">{open ? '⌄' : '›'}</span>
      </button>
      {open && <div style={{display:'flex',flexDirection:'column',gap:4}}>{children}</div>}
    </div>
  );
}

function PlatformSidebar({ active, onSelect }) {
  return (
    <aside className="cv-sidebar">
      <div className="cv-brand-bug">
        <img src="../../assets/logos/conceptv-wordmark-black.png" alt="ConceptV" />
      </div>
      <div className="cv-menu-header"><span style={{background:'var(--bg-canvas)',padding:'0 14px',position:'relative',zIndex:1}}>Menu</span></div>

      <div className="cv-nav">
        {NAV_ITEMS.map(it => (
          <button
            key={it.id}
            className={`cv-nav-item ${active === it.id ? 'active' : ''}`}
            onClick={() => onSelect(it.id)}>
            <span className="cv-nav-glyph">{it.glyph}</span>{it.label}
          </button>
        ))}
      </div>

      <Section title="Tools">
        {TOOL_ITEMS.map(it => (
          <button
            key={it.id}
            className={`cv-nav-item ${active === it.id ? 'active' : ''}`}
            onClick={() => onSelect(it.id)}>
            <span className="cv-nav-glyph">{it.glyph}</span>{it.label}
          </button>
        ))}
        <div className="cv-slot" style={{marginTop:8}}>Favourited options appear here</div>
      </Section>

      <Section title="Integrations" defaultOpen={false}>
        <button className="cv-nav-item"><span className="cv-nav-glyph">🔌</span>View All</button>
        <div className="cv-slot">Activated options appear here</div>
        <div className="cv-slot">Activated options appear here</div>
      </Section>

      <Section title="Support" defaultOpen={false}>
        <button className="cv-nav-item"><span className="cv-nav-glyph">💬</span>FAQs</button>
        <button className="cv-nav-item"><span className="cv-nav-glyph">📘</span>Tutorials</button>
      </Section>
    </aside>
  );
}

window.PlatformSidebar = PlatformSidebar;
