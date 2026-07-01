// atomicity/Atlas.jsx
// ============================================================================
// The Atlas browser — a hierarchical, collapsible tree (left) and a live detail
// pane (right). Both render purely from the ATLAS projection model, so they
// can't drift from the system. The detail pane renders each node by its kind and
// always ends with "What Vi can do here" — the agent and the browser are welded.
// ============================================================================
const { useState: useState_at, useEffect: useEffect_at, useMemo: useMemo_at } = React;
const NS = (window.ATLAS && window.ATLAS.manifest && window.ATLAS.manifest.namespace) || null;
// instance the shared kit Tile, keeping the Atlas tile's own className/look
function AcKitTile({ onClick, children }) {
  return React.createElement(window.AcKit.Tile, { onClick, className: 'ac-tile' }, children);
}

/* ---------------------------- TREE ---------------------------- */
function AcTree({ tree, selId, expanded, onToggle, onSelect, hlId }) {
  if (!tree) return null;
  return (
    <nav className="ac-rail">
      <div className="ac-rail-head">System map</div>
      {(tree.children || []).map(n => (
        <AcTreeNode key={n.id} node={n} depth={0} selId={selId} expanded={expanded} onToggle={onToggle} onSelect={onSelect} hlId={hlId}/>
      ))}
    </nav>
  );
}
function AcTreeNode({ node, depth, selId, expanded, onToggle, onSelect, hlId }) {
  const open = expanded.has(node.id);
  // Foundations is ONE page — collapse token kinds/files in the tree so they
  // don't deep-drill into hundreds of leaves; clicking one opens the workbench.
  const hideKids = node.kind === 'token-group' || node.kind === 'token-file';
  const hasKids = node.children && node.children.length > 0 && !hideKids;
  return (
    <div className="ac-tnode">
      <div className={`ac-trow ${selId === node.id ? 'sel' : ''} ${hlId === node.id ? 'hl' : ''}`}
        onClick={() => { onSelect(node.id); if (hasKids && !open) onToggle(node.id); }}>
        <span className={`ac-caret ${open ? 'open' : ''} ${hasKids ? '' : 'leaf'}`}
          onClick={e => { e.stopPropagation(); if (hasKids) onToggle(node.id); }}>
          <CvIcon name="chevron-right" size={12} tone="muted"/>
        </span>
        <CvIcon name={node.icon || 'dot'} size={depth === 0 ? 16 : 14} tone={selId === node.id || depth === 0 ? 'gold' : 'bronze'} circle={depth === 0}/>
        <span className="lbl">{node.label}</span>
        {node.badge && <span className={`badge ${String(node.badge).toLowerCase()}`}>{node.badge}</span>}
        {node.count != null && <span className="cnt">{node.count}</span>}
      </div>
      {hasKids && open && (
        <div className="ac-children">
          {node.children.map(c => (
            <AcTreeNode key={c.id} node={c} depth={depth + 1} selId={selId} expanded={expanded} onToggle={onToggle} onSelect={onSelect} hlId={hlId}/>
          ))}
        </div>
      )}
    </div>
  );
}

/* ---------------------------- DETAIL ---------------------------- */
function AcDetail({ node, onSelect, onAsk }) {
  if (!node) return <div className="ac-empty">Select anything in the map to inspect it.</div>;
  const crumbs = window.ATLAS.pathTo(node.id);
  const sugg = window.VI_BRAIN.suggestions({ node, surface: 'atomicity' });
  const isFdn = node.id === 'sec/foundations' || ['token', 'token-group', 'token-file'].includes(node.kind);
  const eyebrow = isFdn ? 'Design tokens · live' : (crumbs.length > 1 ? crumbs[crumbs.length - 2].label : 'The system');
  const title = isFdn ? 'Foundations' : node.label;
  const kindLabel = isFdn ? 'workbench' : node.kind;
  const heroIcon = isFdn ? 'layers' : (node.icon || 'dot');
  const doc = isFdn
    ? 'Every design value, on one page. Edit any of them and the whole app — and the live preview — updates instantly. Stage a change to write it back to its source file.'
    : (node.data && (node.data.doc || node.data.subtitle || node.data.description));
  const bare = node.id === 'sec/home'; // Home owns the whole canvas
  if (bare) return <div className="ac-detail"><div className="ac-detail-inner">{React.createElement(window.AcHome, {})}</div></div>;
  return (
    <div className="ac-detail">
      <div className="ac-detail-inner">
        <div className="ac-crumbs">
          {crumbs.map((c, i) => (
            <React.Fragment key={c.id}>
              {i > 0 && <span className="sep">›</span>}
              {i === crumbs.length - 1
                ? <span className="cur">{c.label}</span>
                : <button onClick={() => onSelect(c.id)}>{c.label}</button>}
            </React.Fragment>
          ))}
        </div>

        <header className="ac-hero">
          <div className="ac-eyebrow">{eyebrow}</div>
          <div className="ac-dtitle">
            <CvIcon name={heroIcon} size={28} tone="gold" circle/>
            <h1>{title}</h1>
            <span className="kind">{kindLabel}</span>
          </div>
          {doc && <p className="ac-ddoc">{doc}</p>}
        </header>

        <AcBody node={node} onSelect={onSelect}/>

        <div className="ac-vi-actions">
          <h3><ViShape size={15}/> What V<span style={{color:'var(--accent-gold)'}}>i</span> can do here</h3>
          <div className="ac-vi-chips">
            {sugg.map(s => (
              <button key={s} className="ac-chip" onClick={() => onAsk(s)}>
                <CvIcon name="arrow-right" size={11} tone="bronze"/>{s}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function AcBody({ node, onSelect }) {
  const k = node.kind;

  // Foundations → the editable workbench (table of values + live preview)
  if ((node.id === 'sec/foundations' || k === 'token-group' || k === 'token-file' || k === 'token') && window.AcFoundations) {
    return React.createElement(window.AcFoundations, { node });
  }
  // Home → orientation surface
  if (node.id === 'sec/home' && window.AcHome) {
    return React.createElement(window.AcHome, {});
  }
  // Ingest → upload + deep analysis surface
  if (node.id === 'sec/ingest' && window.AcIngest) {
    return React.createElement(window.AcIngest, {});
  }
  // Explore → generate style directions → promote to a component
  if (node.id === 'sec/explore' && window.AcExplore) {
    return React.createElement(window.AcExplore, {});
  }
  // Voice → generative house-voice copy
  if (node.id === 'sec/voice' && window.AcVoice) {
    return React.createElement(window.AcVoice, {});
  }

  // sections/groups → tiles of children
  if (node.children && node.children.length && !node.leaf) {
    return (
      <div className="ac-section-grid-wrap">
        {node.id === 'reg/host' && <EnvCheck/>}
        <div className="ac-section-grid">
        {node.children.map((c, i) => (
          <AcKitTile key={c.id} onClick={() => onSelect(c.id)}>
            <div className="top">
              <CvIcon name={c.icon || 'dot'} size={18} tone="gold" circle/>
              <span className="name">{c.label}</span>
              {c.count != null && <span className="cnt">{c.count}</span>}
            </div>
            {(c.data && (c.data.subtitle || c.data.description || c.data.doc)) &&
              <span className="desc">{(c.data.subtitle || c.data.description || c.data.doc).slice(0, 96)}</span>}
            {c.badge && !(c.data && (c.data.subtitle || c.data.description || c.data.doc)) && <span className="desc"><b>{c.badge}</b></span>}
          </AcKitTile>
        ))}
        </div>
      </div>
    );
  }

  // leaves by kind
  if (k === 'token') return <AcToken t={node.data}/>;
  if (k === 'card') return <AcCard c={node.data}/>;
  if (k === 'component') return <AcComponent c={node.data}/>;
  if (k === 'template') return <AcTemplate t={node.data}/>;
  if (k === 'theme') return <AcKV data={{ selector: node.data.selector, label: node.data.label }} note="A dial applied as a CSS selector. Threaded through the engine so every surface responds."/>;
  if (k === 'font') return <AcKV data={{ family: node.data.family, status: node.data.status, tokens: (node.data.tokens||[]).join(', '), defined: node.data.path }}/>;
  if (k === 'ai-entry') return <AcAiEntry e={node.data}/>;
  if (k === 'type') return <AcType t={node.data}/>;
  if (k === 'runtime') return <AcKV data={{ id: node.data.id, available: String(node.data.available), capabilities: Object.keys(node.data.caps||{}).filter(x=>node.data.caps[x]).join(', ') || 'staging only' }} note={node.data.description}/>;
  if (k === 'serializer') return <AcKV data={{ kind: node.data.kind, target: node.data.target, strategy: node.data.strategy }} note={node.data.describe}/>;
  if (k === 'change') return <AcChange c={node.data}/>;
  return <AcKV data={node.data || {}}/>;
}

/* ---- leaf renderers ---- */
function AcToken({ t }) {
  const isColor = t.kind === 'color';
  return (
    <div>
      {isColor && <div className="ac-swatch-lg" style={{ background: t.value }}/>}
      <dl className="ac-kv" style={{ marginTop: isColor ? 18 : 0 }}>
        <dt>name</dt><dd><code>{t.name}</code></dd>
        <dt>value</dt><dd><span className="ac-token-value">{t.value}</span></dd>
        <dt>kind</dt><dd>{t.kind}</dd>
        <dt>defined in</dt><dd><code>{t.definedIn}</code></dd>
      </dl>
      <p className="ac-note">This is its single home. Anything that needs this value references <code>var({t.name})</code> — change it here and every consumer updates by construction.</p>
    </div>
  );
}
function AcCard({ c }) {
  const [w, h] = String(c.viewport || '700x360').split('x').map(Number);
  return (
    <div className="ac-card">
      <div className="ac-card-head"><CvIcon name="browser" size={13} tone="bronze"/> {c.path} <span style={{ marginLeft: 'auto', font: '600 11px var(--font-mono)', color: 'var(--fg-muted)' }}>{c.viewport}</span></div>
      <iframe className="ac-iframe" src={'../' + c.path} style={{ height: Math.min(h || 360, 560) }} title={c.name}/>
    </div>
  );
}
function AcComponent({ c }) {
  const ns = NS && window[NS];
  const Comp = ns && ns[c.name];
  return (
    <div>
      <dl className="ac-kv">
        <dt>export</dt><dd><code>window.{NS}.{c.name}</code></dd>
        <dt>source</dt><dd><code>{c.sourcePath}</code></dd>
      </dl>
      <p className="ac-ddoc" style={{ marginTop: 14 }}>Compiled into <code>_ds_bundle.js</code> and exposed on the namespace. Load the bundle, then <code>const {'{'} {c.name} {'}'} = window.{NS}</code>.</p>
      {Comp ? <AcMount Comp={Comp} name={c.name}/> :
        <p className="ac-ddoc">Live mount unavailable here (bundle not loaded in this view). Open its specimen card in the Catalogue to see it run.</p>}
    </div>
  );
}
class AcMount extends React.Component {
  constructor(p) { super(p); this.state = { err: null }; }
  componentDidCatch(e) { this.setState({ err: e.message }); }
  render() {
    if (this.state.err) return <p className="ac-ddoc">This component needs props to render standalone ({this.state.err}). It runs in its specimen card and in templates.</p>;
    return (
      <div className="ac-card"><div className="ac-card-head"><ViShape size={13}/> Live mount</div>
        <div style={{ padding: 18, overflow: 'auto', maxHeight: 480 }}>{React.createElement(this.props.Comp)}</div>
      </div>
    );
  }
}
function AcTemplate({ t }) {
  return (
    <div>
      <dl className="ac-kv">
        <dt>entry</dt><dd><code>{t.entryPath}</code></dd>
        <dt>folder</dt><dd><code>{t.folder}</code></dd>
      </dl>
      {t.entryPath && (
        <div className="ac-card" style={{ marginTop: 14 }}>
          <div className="ac-card-head"><CvIcon name="file-plus" size={13} tone="bronze"/> {t.name}
            <a href={'../' + t.entryPath} target="_blank" rel="noreferrer" style={{ marginLeft: 'auto', font: '600 11px var(--font-mono)', color: 'var(--accent-bronze)' }}>open ↗</a></div>
          <iframe className="ac-iframe" src={'../' + t.entryPath} style={{ height: 460 }} title={t.name}/>
        </div>
      )}
    </div>
  );
}
function AcAiEntry({ e }) {
  const lineage = window.CV_AI.lineage ? window.CV_AI.lineage(e.id) : [e];
  return (
    <div>
      <dl className="ac-kv">
        <dt>id</dt><dd><code>{e.id}</code></dd>
        <dt>layer</dt><dd>{e.layer}</dd>
        <dt>family</dt><dd>{e.family}</dd>
        {e.provider && <><dt>provider</dt><dd><code>{e.provider}</code></dd></>}
        {e.behaviours && <><dt>behaviours</dt><dd><code>{(e.behaviours||[]).join(', ')}</code></dd></>}
        {e.surfaces && <><dt>surfaces</dt><dd>{(e.surfaces||[]).join(', ')}</dd></>}
        <dt>provenance</dt><dd>{e.provenance}</dd>
      </dl>
      {lineage.length > 1 && <p className="ac-ddoc" style={{ marginTop: 12 }}>Inherits: {lineage.map(x => x.id).join(' → ')}</p>}
    </div>
  );
}
function AcType({ t }) {
  return (
    <dl className="ac-kv">
      <dt>id</dt><dd><code>{t.id}</code></dd>
      <dt>layer</dt><dd>{t.layer}</dd>
      {t.extends && <><dt>extends</dt><dd><code>{t.extends}</code></dd></>}
      {t.slots && <><dt>slots</dt><dd>{Object.keys(t.slots).join(', ')}</dd></>}
      {t.provenance && <><dt>provenance</dt><dd>{t.provenance}</dd></>}
    </dl>
  );
}
function AcChange({ c }) {
  return (
    <div>
      <dl className="ac-kv">
        <dt>kind</dt><dd><code>{c.kind}</code></dd>
        <dt>→ file</dt><dd><code>{c.serialized.file}</code></dd>
        <dt>strategy</dt><dd>{c.serialized.strategy}</dd>
        <dt>status</dt><dd><b>{c.status}</b></dd>
      </dl>
      {c.rationale && <p className="ac-ddoc" style={{ marginTop: 10 }}>{c.rationale}</p>}
      <pre className="ac-pre" style={{ marginTop: 12 }}>{c.serialized.source}</pre>
    </div>
  );
}
function AcKV({ data, note }) {
  return (
    <div>
      <dl className="ac-kv">
        {Object.entries(data || {}).map(([k, v]) => <React.Fragment key={k}><dt>{k}</dt><dd>{typeof v === 'string' && v.length < 40 ? <code>{v}</code> : String(v)}</dd></React.Fragment>)}
      </dl>
      {note && <p className="ac-ddoc" style={{ marginTop: 12 }}>{note}</p>}
    </div>
  );
}

window.AcTree = AcTree;
window.AcDetail = AcDetail;

// EnvCheck — live "what's autonomous here vs on export" self-check, projected
// from CV_HOST + CV_SCAN. No hand-written status; reads the registries.
function EnvCheck() {
  const h = window.CV_HOST.describe();
  const scanTree = (window.CV_SCAN && window.CV_SCAN.describe().sources.find(s => s.id === 'host-tree')) || null;
  const caps = h.capabilities || {};
  const rows = [
    { k: 'read', label: 'Read project files', on: !!caps.read },
    { k: 'write', label: 'Write changes to disk', on: !!caps.write },
    { k: 'list', label: 'Walk the whole repo', on: !!caps.list },
    { k: 'exec', label: 'Run the compiler', on: !!caps.exec },
    { k: 'scan', label: 'Scan the real source tree', on: !!(caps.list && caps.read) },
  ];
  return (
    <div className="ac-env">
      <div className="ac-env-top">
        <CvIcon name={h.canWrite ? 'check-circle' : 'cloud-upload'} size={18} tone="gold" circle/>
        <div>
          <div className="ac-env-mode">{h.modeLabel}</div>
          <div className="ac-env-sub">{h.canWrite ? 'Vi writes changes straight to your project.' : 'Changes are staged for review. Export AtomiCity and run it with file access (or an MCP host) to let Vi write, scan the real tree, and run the build autonomously.'}</div>
        </div>
      </div>
      <div className="ac-env-grid">
        {rows.map(r => (
          <div key={r.k} className={`ac-env-cap ${r.on ? 'on' : ''}`}>
            <CvIcon name={r.on ? 'check' : 'circle'} size={13} tone={r.on ? 'gold' : 'muted'}/>
            <span>{r.label}</span>
            <em>{r.on ? 'active' : 'on export'}</em>
          </div>
        ))}
      </div>
    </div>
  );
}
window.EnvCheck = EnvCheck;
