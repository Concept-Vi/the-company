// app/canvases/Registry.jsx — Workshop Studio Floor
//
// A complete rethink: instead of a typed database browser, the Registry is
// a walk through your Workshop's capabilities. Organised by WHAT YOU CAN
// MAKE, not by abstract layer. Vi is always present. Editing happens
// directly on the thumb — no forms.

const { useState: useState_reg, useEffect: useEffect_reg, useMemo: useMemo_reg, useRef: useRef_reg } = React;

// ===========================================================================
// Workstations — the spine of the page. Each is a question the user
// might genuinely ask about their Workshop.
// ===========================================================================
const WORKSTATIONS = [
  {
    id: 'decks',
    headline: 'Slide decks',
    sub: 'What goes inside your decks?',
    addPrompt: 'A new slide layout or slide block — e.g. "split image with quote", "five-stat comparison"',
    shelves: [
      { label: 'Slide layouts', query: { layer: 'surface', family: 'deck-slide' }, addLayer: 'surface', addFamily: 'deck-slide' },
      { label: 'Slide blocks',  query: { layer: 'block' }, addLayer: 'block', addFamily: 'block' },
    ],
  },
  {
    id: 'brochures',
    headline: 'Brochures',
    sub: 'One-page collateral and property sheets',
    addPrompt: 'A new brochure section — e.g. "agent contact strip", "spec table with images"',
    shelves: [
      { label: 'Sections', query: { layer: 'block' }, addLayer: 'block', addFamily: 'brochure-section' },
    ],
  },
  {
    id: 'widgets',
    headline: 'Widgets',
    sub: 'Dashboard tiles, hub panels, partner embeds',
    addPrompt: 'A new widget kind or system — e.g. "kiosk widget", "funnel system", "leaderboard"',
    shelves: [
      { label: 'Widget kinds',   query: { layer: 'surface', family: 'widget' }, addLayer: 'surface', addFamily: 'widget' },
      { label: 'Widget systems', query: { layer: 'system',  family: 'widget' }, addLayer: 'system',  addFamily: 'widget' },
    ],
  },
  {
    id: 'wizards',
    headline: 'Wizards',
    sub: 'Multi-step flows — capture, configure, publish',
    addPrompt: 'A new wizard kind or step kind — e.g. "feedback wizard", "voice-capture step", "branching menu"',
    shelves: [
      { label: 'Wizard kinds', query: { layer: 'doc',     family: 'wizard' },      onlyExtending: 'doc.wizard', addLayer: 'doc',     addFamily: 'wizard', addParent: 'doc.wizard' },
      { label: 'Step kinds',   query: { layer: 'surface', family: 'wizard-step' }, addLayer: 'surface', addFamily: 'wizard-step' },
    ],
  },
  {
    id: 'shared',
    headline: 'Shared materials',
    sub: 'Atoms and tokens used across every doc type',
    addPrompt: 'A new atom or token — e.g. "status pill", "gradient swatch"',
    collapsedByDefault: true,
    shelves: [
      { label: 'Atoms',  query: { layer: 'atom' },  addLayer: 'atom',  addFamily: 'atom' },
      { label: 'Tokens', query: { layer: 'token' }, addLayer: 'token', addFamily: 'token' },
    ],
  },
];

// ===========================================================================
// Main canvas
// ===========================================================================
function Registry({ onOpenBuilder }) {
  const R = window.CV_REGISTRY;
  const [tick, setTick] = useState_reg(0);
  useEffect_reg(() => R?.subscribe(() => setTick(t => t + 1)), []);

  const [search, setSearch] = useState_reg('');
  const [collapsed, setCollapsed] = useState_reg(() => {
    const init = {};
    for (const ws of WORKSTATIONS) if (ws.collapsedByDefault) init[ws.id] = true;
    return init;
  });
  const [inspected, setInspected] = useState_reg(null); // typeId | null
  const [adder, setAdder] = useState_reg(null);         // { stationId, shelfIdx } | null

  function openInspector(id) { setInspected(id); }
  function closeInspector() { setInspected(null); }

  // Composition counts — show which workstations have user/vi additions
  const userAdditions = useMemo_reg(() => {
    if (!R) return {};
    const m = {};
    for (const ws of WORKSTATIONS) {
      let n = 0;
      for (const sh of ws.shelves) {
        n += R.query(sh.query).filter(t => t.provenance === 'user' || t.provenance === 'vi').length;
      }
      m[ws.id] = n;
    }
    return m;
  }, [tick]);

  return (
    <div className="rs-shell">
      <RegistryFloor
        search={search} setSearch={setSearch}
        collapsed={collapsed} setCollapsed={setCollapsed}
        userAdditions={userAdditions}
        onOpenType={openInspector}
        onAdd={(stationId, shelfIdx) => setAdder({ stationId, shelfIdx })}
        onAdvanced={onOpenBuilder}
        inspected={inspected}
      />

      {inspected && (
        <TypeInspector
          typeId={inspected}
          onClose={closeInspector}
          onPickRelated={(id) => setInspected(id)}
          onAddVariant={(parent) => setAdder({ stationId: null, shelfIdx: null, parent })}
          onAdvanced={onOpenBuilder}
        />
      )}

      <ViStudioRail
        context={inspected ? R?.get(inspected) : null}
        onPickType={openInspector}
      />

      {adder && (
        <QuickAdder
          adder={adder}
          stationDef={adder.stationId ? WORKSTATIONS.find(w => w.id === adder.stationId) : null}
          onClose={() => setAdder(null)}
          onSaved={(t) => { setAdder(null); setInspected(t.id); }}
          onAdvanced={() => { setAdder(null); onOpenBuilder?.(); }}
        />
      )}

      <FloatingAddButton onClick={() => setAdder({})}/>
    </div>
  );
}

// ===========================================================================
// Floor — vertical scroll of workstations
// ===========================================================================
function RegistryFloor({ search, setSearch, collapsed, setCollapsed, userAdditions, onOpenType, onAdd, onAdvanced, inspected }) {
  const R = window.CV_REGISTRY;
  return (
    <div className={`rs-floor ${inspected ? 'with-inspector' : ''}`}>
      <header className="rs-floor-head">
        <div className="rs-floor-title">
          <h1>What can your Workshop make?</h1>
          <p>Pick anything to inspect or edit. Ask Vi to add or change. Each row is a kind of thing your Workshop can produce.</p>
        </div>
        <div className="rs-floor-tools">
          <div className="rs-search">
            <CvIcon name="search" size={14} tone="muted"/>
            <input placeholder="Find a Type by name or description…" value={search} onChange={e => setSearch(e.target.value)}/>
            {search && <button onClick={() => setSearch('')}>×</button>}
          </div>
          <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => onAdvanced?.()} title="Open Type Builder for advanced authoring (slots, JSON, lineage)">
            ⚙ Advanced
          </button>
        </div>
      </header>

      <div className="rs-stations">
        {WORKSTATIONS.map(ws => (
          <Workstation
            key={ws.id} ws={ws}
            collapsed={collapsed[ws.id]}
            setCollapsed={(v) => setCollapsed(c => ({ ...c, [ws.id]: v }))}
            additions={userAdditions[ws.id] || 0}
            search={search}
            onOpenType={onOpenType}
            onAdd={(shelfIdx) => onAdd(ws.id, shelfIdx)}
          />
        ))}
      </div>
    </div>
  );
}

// ===========================================================================
// Workstation — a horizontal group of shelves
// ===========================================================================
function Workstation({ ws, collapsed, setCollapsed, additions, search, onOpenType, onAdd }) {
  return (
    <section className={`rs-station ${collapsed ? 'collapsed' : ''}`}>
      <header className="rs-station-head" onClick={() => setCollapsed(!collapsed)}>
        <div className="rs-station-title">
          <span className="caret">{collapsed ? '▸' : '▾'}</span>
          <h3>{ws.headline}</h3>
          {additions > 0 && <span className="addn">+{additions} custom</span>}
        </div>
        <p className="rs-station-sub">{ws.sub}</p>
      </header>
      {!collapsed && (
        <div className="rs-station-body">
          {ws.shelves.map((sh, i) => (
            <Shelf key={i} shelf={sh} search={search} onOpenType={onOpenType} onAdd={() => onAdd(i)}/>
          ))}
        </div>
      )}
    </section>
  );
}

// ===========================================================================
// Shelf — one horizontal row of TypeThumbs (filterable, scrollable)
// ===========================================================================
function Shelf({ shelf, search, onOpenType, onAdd }) {
  const R = window.CV_REGISTRY;
  const [tick, setTick] = useState_reg(0);
  useEffect_reg(() => R?.subscribe(() => setTick(t => t + 1)), []);

  let types = useMemo_reg(() => R?.query({ ...shelf.query, search }) || [], [shelf, search, tick]);
  if (shelf.onlyExtending) types = types.filter(t => t.extends === shelf.onlyExtending);

  return (
    <div className="rs-shelf">
      <div className="rs-shelf-head">
        <span className="lbl">{shelf.label}</span>
        <span className="count">{types.length}</span>
      </div>
      <div className="rs-shelf-track">
        {types.map(t => (
          <ShelfTile key={t.id} type={t} onOpen={() => onOpenType(t.id)}/>
        ))}
        <button className="rs-shelf-add" onClick={onAdd} title="Add a new one">
          <span className="plus">+</span>
          <span className="lbl">Add</span>
        </button>
      </div>
    </div>
  );
}

// ===========================================================================
// ShelfTile — minimal-text card; thumb is the star.
// Hover reveals quick actions. Name appears as a small overlay on hover only.
// ===========================================================================
function ShelfTile({ type, onOpen }) {
  return (
    <button className={`rs-tile cv-prov-${type.provenance}`} onClick={onOpen}>
      <div className="rs-tile-thumb">
        {window.TypeThumb && <window.TypeThumb type={type} width={220} height={130}/>}
      </div>
      <div className="rs-tile-overlay">
        <div className="rs-tile-meta">
          <strong>{type.name}</strong>
          {type.provenance !== 'built-in' && <span className="prov">{type.provenance}</span>}
        </div>
        <div className="rs-tile-actions">
          <span className="hint">Click to open</span>
        </div>
      </div>
    </button>
  );
}

// ===========================================================================
// Floating + action — opens the quick adder modal anywhere
// ===========================================================================
function FloatingAddButton({ onClick }) {
  return (
    <button className="rs-fab" onClick={onClick} title="Add a new Type">
      <ViShape size={16}/>
      <span>Add</span>
    </button>
  );
}

window.Registry = Registry;
