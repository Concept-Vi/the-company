// canvases/workshop/Library.jsx — left-side asset library panel
// Replaces the icon-only rail. Searchable tabs for Blocks / Layouts / Icons /
// Components / Imagery. Every tile is click-to-insert AND drag-to-drop onto
// the section list (drop targets live on .ws-add-divider).
//
// Drag payload format (JSON, set on dataTransfer with the custom type
// 'application/x-cv-library'):
//   { kind:'block', block:'<id>', data?:{} }
//   { kind:'layout', layout:'<id>' }
//   { kind:'icon', icon:'<name>' }      -> creates a one-item icons block
//   { kind:'component', component:'<id>' } -> creates a callout block
//   { kind:'image', label:'<text>' }    -> creates an image block

const { useState: useState_lib, useMemo: useMemo_lib } = React;

const LIB_TABS = [
  { id: 'blocks',     label: 'Blocks',     icon: 'files-stack' },
  { id: 'layouts',    label: 'Layouts',    icon: 'browser' },
  { id: 'icons',      label: 'Icons',      icon: 'star' },
  { id: 'components', label: 'Components', icon: 'check-square' },
  { id: 'imagery',    label: 'Imagery',    icon: 'image-stack' },
];

// ---- imagery: small placeholder catalogue (real renders would come from
// the project's media library — this is a faithful set of named slots).
const LIB_IMAGERY = [
  { id: 'render-aerial',   label: 'Aerial render',          tone: 'sky'   },
  { id: 'render-interior', label: 'Interior render',        tone: 'sand'  },
  { id: 'render-kitchen',  label: 'Kitchen detail',         tone: 'stone' },
  { id: 'site-plan',       label: 'Site plan',              tone: 'paper' },
  { id: 'floor-plan',      label: 'Floor plan',             tone: 'paper' },
  { id: 'screenshot-hub',  label: 'Virtual Hub screen',     tone: 'ink'   },
  { id: 'photo-team',      label: 'Team photo',             tone: 'sand'  },
  { id: 'photo-event',     label: 'Event photo',            tone: 'ink'   },
  { id: 'chart-line',      label: 'Line chart',             tone: 'paper' },
  { id: 'chart-bar',       label: 'Bar chart',              tone: 'paper' },
];

function Library({ docType, onInsertBlock, onApplyLayout, onClose }) {
  const [tab, setTab] = useState_lib('blocks');
  const [q, setQ] = useState_lib('');

  const items = useMemo_lib(() => {
    const query = q.trim().toLowerCase();
    if (tab === 'blocks') {
      return Object.entries(window.WS_BLOCKS || {})
        .filter(([k, def]) => k !== 'divider')
        .map(([k, def]) => ({ key: k, label: def.label, icon: def.icon, payload: { kind: 'block', block: k } }))
        .filter(it => !query || it.label.toLowerCase().includes(query) || it.key.includes(query));
    }
    if (tab === 'layouts') {
      const list = window.WS_layoutsForType ? window.WS_layoutsForType(docType || 'deck') : [];
      return list.map(([k, L]) => ({
        key: k, label: L.name, sub: L.desc, icon: L.icon,
        payload: { kind: 'layout', layout: k },
      })).filter(it => !query || it.label.toLowerCase().includes(query) || (it.sub || '').toLowerCase().includes(query));
    }
    if (tab === 'icons') {
      const names = Object.keys(window.CV_ICONS?.data || {});
      return names.map(n => ({
        key: n, label: n, icon: n,
        payload: { kind: 'icon', icon: n },
      })).filter(it => !query || it.key.includes(query));
    }
    if (tab === 'components') {
      const groups = window.COMPONENT_GROUPS || {};
      const flat = [];
      for (const [gName, list] of Object.entries(groups)) {
        for (const c of list) flat.push({
          key: c.id, label: c.name, group: gName, sub: c.desc, icon: 'check-square',
          payload: { kind: 'component', component: c.id, label: c.name, group: gName },
        });
      }
      return flat.filter(it => !query || it.label.toLowerCase().includes(query) || (it.sub || '').toLowerCase().includes(query) || it.group.toLowerCase().includes(query));
    }
    if (tab === 'imagery') {
      return LIB_IMAGERY.map(im => ({
        key: im.id, label: im.label, icon: 'image-stack', tone: im.tone,
        payload: { kind: 'image', label: im.label, tone: im.tone },
      })).filter(it => !query || it.label.toLowerCase().includes(query));
    }
    return [];
  }, [tab, q, docType]);

  function startDrag(e, payload) {
    e.dataTransfer.setData('application/x-cv-library', JSON.stringify(payload));
    e.dataTransfer.effectAllowed = 'copy';
    // Set a small drag image — use the source tile itself
    try {
      const img = e.currentTarget.cloneNode(true);
      img.style.position = 'absolute'; img.style.top = '-1000px'; img.style.left = '0';
      img.style.width = e.currentTarget.offsetWidth + 'px';
      document.body.appendChild(img);
      e.dataTransfer.setDragImage(img, 10, 10);
      setTimeout(() => img.remove(), 0);
    } catch {}
  }

  function clickInsert(payload) {
    if (payload.kind === 'layout') onApplyLayout?.(payload.layout);
    else onInsertBlock?.(payload);
  }

  return (
    <aside className="ws-library" onClick={e => e.stopPropagation()}>
      <header className="ws-library-head">
        <h5>Library</h5>
        {onClose && (
          <button className="ws-library-close" onClick={onClose} title="Collapse library">‹</button>
        )}
      </header>

      <div className="ws-library-tabs" role="tablist">
        {LIB_TABS.map(t => (
          <button
            key={t.id} role="tab" aria-selected={tab === t.id}
            className={`ws-library-tab ${tab === t.id ? 'active' : ''}`}
            onClick={() => { setTab(t.id); setQ(''); }}
            title={t.label}>
            <CvIcon name={t.icon} size={14} tone={tab === t.id ? 'gold' : 'bronze'}/>
            <span>{t.label}</span>
          </button>
        ))}
      </div>

      <div className="ws-library-search">
        <CvIcon name="search" size={13} tone="muted"/>
        <input
          placeholder={`Search ${LIB_TABS.find(x => x.id === tab)?.label.toLowerCase()}…`}
          value={q} onChange={e => setQ(e.target.value)}/>
        {q && <button className="ws-library-clear" onClick={() => setQ('')} title="Clear">×</button>}
      </div>

      <div className="ws-library-hint">
        Click to add to slide · drag onto the canvas to drop in place.
      </div>

      <div className={`ws-library-grid ws-library-grid--${tab}`}>
        {items.length === 0 && (
          <div className="ws-library-empty">No matches for "{q}".</div>
        )}
        {tab === 'icons'
          ? items.map(it => (
              <button key={it.key}
                className="ws-library-icon-tile"
                draggable
                onDragStart={e => startDrag(e, it.payload)}
                onClick={() => clickInsert(it.payload)}
                title={`Insert icon: ${it.label}`}>
                <CvIcon name={it.icon} size={20} tone="bronze"/>
                <span className="lbl">{it.label}</span>
              </button>
            ))
          : tab === 'imagery'
          ? items.map(it => (
              <button key={it.key}
                className={`ws-library-img-tile tone-${it.tone || 'paper'}`}
                draggable
                onDragStart={e => startDrag(e, it.payload)}
                onClick={() => clickInsert(it.payload)}
                title={`Insert image slot: ${it.label}`}>
                <div className="preview" aria-hidden="true">
                  <CvIcon name="image-stack" size={18} tone="bronze"/>
                </div>
                <span className="lbl">{it.label}</span>
              </button>
            ))
          : items.map(it => (
              <button key={it.key}
                className="ws-library-tile"
                draggable
                onDragStart={e => startDrag(e, it.payload)}
                onClick={() => clickInsert(it.payload)}
                title={it.sub || it.label}>
                <span className="ic"><CvIcon name={it.icon} size={16} tone="bronze"/></span>
                <div className="meta">
                  <div className="name">{it.label}</div>
                  {it.group && <div className="group">{it.group}</div>}
                  {it.sub && !it.group && <div className="sub">{it.sub}</div>}
                </div>
                <span className="grip" aria-hidden="true">⋮⋮</span>
              </button>
            ))}
      </div>
    </aside>
  );
}

// ============================================================
// Resolver — given a drag payload, produce a section object
// (or signal "apply layout" with the chosen layout id).
// ============================================================
window.WS_resolveLibraryPayload = function(payload) {
  if (!payload || typeof payload !== 'object') return null;
  if (payload.kind === 'block') {
    const def = window.WS_BLOCKS[payload.block];
    if (!def) return null;
    return { kind: 'section', section: { kind: payload.block, data: { ...def.defaults, ...(payload.data || {}) } } };
  }
  if (payload.kind === 'layout') {
    return { kind: 'layout', layout: payload.layout };
  }
  if (payload.kind === 'icon') {
    const def = window.WS_BLOCKS.icons;
    return { kind: 'section', section: { kind: 'icons', data: { items: [{ icon: payload.icon, label: titleCase(payload.icon) }] } } };
  }
  if (payload.kind === 'component') {
    return { kind: 'section', section: { kind: 'callout', data: { label: payload.group || 'Component', text: `${payload.label} — drop content here.` } } };
  }
  if (payload.kind === 'image') {
    return { kind: 'section', section: { kind: 'image', data: { label: payload.label || 'Image placeholder' } } };
  }
  return null;
};

function titleCase(s) {
  return String(s || '').replace(/[-_]/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

window.Library = Library;
