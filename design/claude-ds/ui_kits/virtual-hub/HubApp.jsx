// App.jsx — Virtual Hub viewer root
const { useState: useState_vh } = React;

const HUBS = [
  { id: 'entry',     label: 'Entry',         title: 'Lobby — Tower East'      },
  { id: 'apt-a',     label: 'Apartment A',   title: 'Apartment A — Level 12'  },
  { id: 'apt-b',     label: 'Apartment B',   title: 'Apartment B — Level 12'  },
  { id: 'rooftop',   label: 'Rooftop',       title: 'Rooftop Garden'          },
];

function HubApp() {
  const [active, setActive] = useState_vh('apt-a');
  const [menuOpen, setMenuOpen] = useState_vh(false);
  const [panel, setPanel] = useState_vh('info'); // null | info | share | floorplan
  const [capture, setCapture] = useState_vh(null); // {x,y} or null

  const hub = HUBS.find(h => h.id === active);

  function selectPanel(id) {
    setPanel(id);
    if (id === 'floorplan' || id === 'info' || id === 'share') setMenuOpen(false);
  }

  function handleStageClick(e) {
    // Only drop a comment if we click on the photo background — not on any UI overlay
    if (e.target.classList?.contains('vh-stage') || e.target.classList?.contains('vh-vignette')) {
      const rect = e.currentTarget.getBoundingClientRect();
      setCapture({ x: e.clientX - rect.left, y: e.clientY - rect.top });
      setMenuOpen(false);
    }
  }

  return (
    <div className="vh-stage" onClick={handleStageClick}>
      <div className="vh-vignette"/>

      <HubBug hubs={HUBS} activeHub={active} onSwitch={(id)=>{ setActive(id); setCapture(null); }}/>

      <MenuButton open={menuOpen} onClick={() => setMenuOpen(o => !o)}/>
      {menuOpen && (
        <QuickMenu
          active={panel}
          onSelect={selectPanel}
          onClose={() => setMenuOpen(false)}/>
      )}

      {panel === 'info' && !menuOpen && <InfoPanel hub={hub} onClose={() => setPanel(null)}/>}
      {panel === 'share' && !menuOpen && <SharePanel hub={hub} onClose={() => setPanel(null)}/>}

      {panel === 'floorplan' && (
        <FloorplanOverlay
          activeHub={active === 'apt-a' ? 'living' : active}
          onPick={(id) => { setPanel('info'); }}
          onClose={() => setPanel(null)}/>
      )}

      {capture && (
        <CaptureComment x={capture.x} y={capture.y} onClose={() => setCapture(null)}/>
      )}

      {/* Onboarding hint - shown when nothing is open */}
      {!menuOpen && !panel && !capture && (
        <div style={{
          position: 'absolute', bottom: 96, left: '50%', transform: 'translateX(-50%)',
          background: 'rgba(31,26,18,.7)', backdropFilter: 'blur(8px)',
          color: 'rgba(251,247,236,.7)', font: '500 12px/1 var(--font-body)',
          padding: '10px 18px', borderRadius: 999, letterSpacing: '0.04em',
          pointerEvents: 'none',
        }}>
          Click MENU to open the hub controls · or click anywhere on the photo to leave a capture comment
        </div>
      )}
    </div>
  );
}

const _mountApp = document.getElementById('app');
if (_mountApp) ReactDOM.createRoot(_mountApp).render(<HubApp/>);
