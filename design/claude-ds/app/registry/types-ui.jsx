// app/registry/types-ui.jsx
// Shared visual primitives for the Type Registry — a small set of
// components every consumer surface uses so the system feels coherent.

const { useState: useState_tu, useMemo: useMemo_tu } = React;

const LAYER_RANK = { token: 0, atom: 1, block: 2, system: 3, surface: 4, doc: 5, template: 6 };

// Tiny coloured pip + layer name. Used everywhere a Type appears in the UI.
function TypeLayerBadge({ layer, size = 'sm' }) {
  const info = window.CV_REGISTRY?.LAYER_INFO?.[layer];
  if (!info) return null;
  const px = size === 'lg' ? 7 : size === 'md' ? 6 : 5;
  return (
    <span className={`cv-type-layer cv-type-layer-${size}`} title={info.desc}>
      <span className="pip" style={{ width: px, height: px, background: info.swatch }}/>
      <span className="lbl">{info.label}</span>
    </span>
  );
}

// Provenance badge — built-in / user / vi / imported
function TypeProvBadge({ p }) {
  const map = {
    'built-in': { label: 'Built-in', tone: 'bronze' },
    'user':     { label: 'Yours',    tone: 'gold' },
    'vi':       { label: 'Vi',       tone: 'ink' },
    'imported': { label: 'Imported', tone: 'bronze' },
  };
  const m = map[p] || map['built-in'];
  return <span className={`cv-type-prov cv-type-prov-${p}`} title={`Provenance: ${m.label}`}>{m.label}</span>;
}

// One-line chip for inline reference. Click → onPick.
function TypeChip({ type, onPick, active }) {
  if (!type) return null;
  return (
    <button className={`cv-type-chip ${active ? 'active' : ''}`} onClick={onPick}>
      <CvIcon name={type.icon || 'check-square'} size={12} tone="bronze"/>
      <span className="name">{type.name}</span>
      <TypeLayerBadge layer={type.layer} size="sm"/>
    </button>
  );
}

// Full card for grid display. Composable: pass `slot` to filter accepted Types.
function TypeCard({ type, onOpen, onUse, dense, lineage, thumbWidth }) {
  if (!type) return null;
  const R = window.CV_REGISTRY;
  const slotCount = Object.keys(type.slots || {}).length;
  const childCount = R?.children?.(type.id)?.length || 0;
  const varCount = (type.variables || []).length;
  const tw = thumbWidth || (dense ? 200 : 280);
  return (
    <div className={`cv-type-card ${dense ? 'dense' : ''} cv-prov-${type.provenance || 'built-in'}`} onClick={onOpen}>
      <div className="thumb-wrap">
        {window.TypeThumb
          ? <TypeThumb type={type} width={tw} height={Math.round(tw * 0.6)} dense={dense}/>
          : <div style={{height: tw * 0.6, background:'var(--bg-muted)'}}/>}
        <div className="thumb-overlay">
          <TypeLayerBadge layer={type.layer} size="sm"/>
          <TypeProvBadge p={type.provenance}/>
        </div>
      </div>
      <div className="head">
        <span className="icon">
          <CvIcon name={type.icon || 'check-square'} size={dense ? 14 : 16} tone="bronze"/>
        </span>
        <div className="meta">
          <div className="name">{type.name}</div>
          <div className="row">
            {type.family && <span className="fam">{type.family}</span>}
            {lineage && type.extends && <span className="lineage-inline">extends <code>{type.extends.split('.').pop()}</code></span>}
          </div>
        </div>
      </div>
      {!dense && type.description && <p className="desc">{type.description}</p>}
      {!dense && (type.tags?.length || slotCount || childCount || varCount) ? (
        <div className="foot">
          {slotCount > 0 && <span className="stat" title={`${slotCount} slots`}>◇ {slotCount}</span>}
          {childCount > 0 && <span className="stat" title={`${childCount} children extend this`}>↳ {childCount}</span>}
          {varCount > 0 && <span className="stat" title={`${varCount} variables`}>𝓋 {varCount}</span>}
          {(type.tags || []).slice(0, 3).map(t => <span key={t} className="tag">{t}</span>)}
        </div>
      ) : null}
      {onUse && (
        <button className="use" onClick={(e) => { e.stopPropagation(); onUse(type); }}>Use →</button>
      )}
    </div>
  );
}

// Lineage strip — root → child → child → self
function TypeLineageStrip({ id, onPick }) {
  const R = window.CV_REGISTRY;
  const chain = useMemo_tu(() => R ? R.lineage(id) : [], [id]);
  if (!chain.length) return null;
  return (
    <div className="cv-type-lineage">
      {[...chain].reverse().map((t, i) => (
        <React.Fragment key={t.id}>
          {i > 0 && <span className="sep">›</span>}
          <button className="link" onClick={() => onPick?.(t.id)}>
            <TypeLayerBadge layer={t.layer} size="sm"/>
            <span>{t.name}</span>
          </button>
        </React.Fragment>
      ))}
    </div>
  );
}

// Slot definition strip — show what a slot accepts.
function SlotAcceptsHint({ slot }) {
  const acc = slot?.accepts || {};
  const parts = [];
  if (acc.layers?.length)   parts.push(acc.layers.join(' | '));
  if (acc.families?.length) parts.push('family: ' + acc.families.join(' | '));
  if (acc.tags?.length)     parts.push('tag: ' + acc.tags.join(' | '));
  if (!parts.length) return <span className="cv-slot-hint">any Type</span>;
  return <span className="cv-slot-hint">{parts.join(' · ')}</span>;
}

// Render a Type's slots as boxes with their accept hints — for builder
// inspection and embedding UI.
function TypeSlotList({ type, value, onChange, browseSlot }) {
  const slots = type?.slots || {};
  const keys = Object.keys(slots);
  if (!keys.length) {
    return <div className="cv-slot-empty">This Type has no slots. Add one to make it composable.</div>;
  }
  return (
    <div className="cv-slot-list">
      {keys.map(k => {
        const s = slots[k];
        const cur = value?.[k];
        return (
          <div key={k} className="cv-slot">
            <div className="head">
              <strong>{s.label || k}</strong>
              <span className="slot-name"><code>{k}</code></span>
              {s.multiple && <span className="m-pill">multiple</span>}
              {s.optional && <span className="m-pill">optional</span>}
            </div>
            <SlotAcceptsHint slot={s}/>
            <div className="filled">
              {s.multiple
                ? <>
                    {(cur || []).map((id, i) => <FilledSlotChip key={i} typeId={id}/>)}
                    {(!cur || cur.length === 0) && <em className="empty">No items yet</em>}
                  </>
                : (cur ? <FilledSlotChip typeId={cur}/> : <em className="empty">Empty</em>)}
            </div>
            {browseSlot && <button className="browse" onClick={() => browseSlot(k, s)}>Browse Types →</button>}
          </div>
        );
      })}
    </div>
  );
}

function FilledSlotChip({ typeId }) {
  const R = window.CV_REGISTRY;
  const t = R?.get(typeId);
  if (!t) return <span className="cv-slot-fill missing"><code>{typeId}</code></span>;
  return <TypeChip type={t}/>;
}

// Search input + segmented layer filter. Returns query params via onChange.
function TypeFilterBar({ filter, onChange, layers = window.CV_REGISTRY?.LAYERS || [] }) {
  return (
    <div className="cv-type-filter">
      <div className="search">
        <CvIcon name="search" size={13} tone="muted"/>
        <input
          placeholder="Search Types — name, description, tag…"
          value={filter.search || ''}
          onChange={e => onChange({ ...filter, search: e.target.value })}/>
        {filter.search && <button onClick={() => onChange({ ...filter, search: '' })}>×</button>}
      </div>
      <div className="layer-pills">
        <button className={!filter.layer ? 'active' : ''} onClick={() => onChange({ ...filter, layer: null })}>All layers</button>
        {layers.map(l => (
          <button key={l}
            className={filter.layer === l ? 'active' : ''}
            onClick={() => onChange({ ...filter, layer: l })}>
            <span className="pip" style={{ background: window.CV_REGISTRY?.LAYER_INFO?.[l]?.swatch }}/>
            {window.CV_REGISTRY?.LAYER_INFO?.[l]?.label || l}
          </button>
        ))}
      </div>
    </div>
  );
}

// Compact type-tree — used in Registry sidebar + builder browser.
function TypeTree({ filter, selected, onSelect }) {
  const R = window.CV_REGISTRY;
  const types = useMemo_tu(() => R ? R.query(filter || {}) : [], [filter, R?.all().length]);
  const byLayer = useMemo_tu(() => {
    const m = {};
    for (const t of types) (m[t.layer] = m[t.layer] || []).push(t);
    return m;
  }, [types]);

  // Build parent->children map within each layer for nested display
  return (
    <div className="cv-type-tree">
      {(R?.LAYERS || []).map(layer => {
        const list = byLayer[layer];
        if (!list?.length) return null;
        // Group: roots (no extends within filter set) → then extending children
        const ids = new Set(list.map(t => t.id));
        const roots = list.filter(t => !t.extends || !ids.has(t.extends));
        return (
          <div key={layer} className="layer-group">
            <h6><TypeLayerBadge layer={layer} size="md"/> <span className="count">{list.length}</span></h6>
            <ul>
              {roots.map(r => <TypeTreeNode key={r.id} t={r} all={list} selected={selected} onSelect={onSelect}/>)}
            </ul>
          </div>
        );
      })}
      {!types.length && <div className="cv-type-tree-empty">No Types match.</div>}
    </div>
  );
}

function TypeTreeNode({ t, all, selected, onSelect }) {
  const kids = useMemo_tu(() => all.filter(x => x.extends === t.id), [all, t.id]);
  return (
    <li className={selected === t.id ? 'sel' : ''}>
      <button onClick={() => onSelect?.(t.id)}>
        <CvIcon name={t.icon || 'check-square'} size={12} tone="bronze"/>
        <span className="nm">{t.name}</span>
        <TypeProvBadge p={t.provenance}/>
      </button>
      {kids.length > 0 && (
        <ul>
          {kids.map(k => <TypeTreeNode key={k.id} t={k} all={all} selected={selected} onSelect={onSelect}/>)}
        </ul>
      )}
    </li>
  );
}

Object.assign(window, {
  TypeLayerBadge, TypeProvBadge, TypeChip, TypeCard,
  TypeLineageStrip, SlotAcceptsHint, TypeSlotList,
  TypeFilterBar, TypeTree, TypeTreeNode,
});
