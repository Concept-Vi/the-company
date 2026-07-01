// canvases/workshop/Section.jsx — wraps every block with controls
// Selection, drag-reorder, refine, variations, lock, delete.

const { useState: useState_s } = React;

function Section({ idx, section, total, isSelected, onSelect, onChange, onRemove, onMove, onLock, onRefine, onVary, variations, activeVariation, onPickVariation, refining }) {
  const def = window.WS_BLOCKS[section.kind];
  if (!def) return null;
  const locked = section.locked;
  return (
    <div
      className={`ws-section ${isSelected ? 'selected' : ''} ${locked ? 'locked' : ''}`}
      data-section-id={section.id}
      data-block-kind={section.kind}
      onClick={onSelect}
      style={{padding: section.kind === 'divider' ? '4px 0' : '20px 24px'}}
    >
      <div className="ws-section-toolbar">
        <span className="badge">{def.label}</span>
        <span className="div"/>
        <button onClick={(e) => { e.stopPropagation(); onMove(idx, -1); }} disabled={idx === 0} title="Move up">↑</button>
        <button onClick={(e) => { e.stopPropagation(); onMove(idx, +1); }} disabled={idx === total - 1} title="Move down">↓</button>
        <span className="div"/>
        <button onClick={(e) => { e.stopPropagation(); onLock(); }} title={locked ? 'Unlock' : 'Lock (Vi won\'t change)'}>{locked ? '🔒' : '🔓'}</button>
        <RefinePop mode="chip" placeholder={`Refine this ${def.label.toLowerCase()}…`} disabled={refining} onRefine={onRefine}/>
        <button onClick={(e) => { e.stopPropagation(); onVary(); }} disabled={refining} title="Generate 3 variations of this block">⤧</button>
        <button onClick={(e) => { e.stopPropagation(); if (confirm(`Remove ${def.label}?`)) onRemove(); }} title="Remove">×</button>
      </div>
      {def.render(section.data, (newData) => onChange({ ...section, data: newData }))}
      {isSelected && variations && variations.length > 0 && (
        <div className="ws-variations" onClick={e => e.stopPropagation()}>
          <span className="label">Variations</span>
          <div className="chips">
            <button className={`chip ${activeVariation == null ? 'active' : ''}`} onClick={() => onPickVariation(null)}>Original</button>
            {variations.map((v, i) => (
              <button key={i} className={`chip ${activeVariation === i ? 'active' : ''}`} onClick={() => onPickVariation(i)}>v{i + 1}</button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
window.WSSection = Section;

// Inserter divider — small "+ add block" between sections + drop target for the Library
function AddDivider({ onAdd, onInsertSection, onInsertVi, atIdx }) {
  const [open, setOpen] = useState_s(false);
  const [dragOver, setDragOver] = useState_s(false);
  const blocks = Object.entries(window.WS_BLOCKS);

  function tryHandlePayload(e) {
    const raw = e.dataTransfer.getData('application/x-cv-library');
    if (!raw) return false;
    e.preventDefault();
    e.stopPropagation();
    try {
      const payload = JSON.parse(raw);
      const resolved = window.WS_resolveLibraryPayload?.(payload);
      if (resolved?.kind === 'section' && onInsertSection) {
        onInsertSection(resolved.section);
        return true;
      }
    } catch {}
    return false;
  }

  return (
    <div
      className={`ws-add-divider ${dragOver ? 'drop-active' : ''}`}
      onClick={(e) => { e.stopPropagation(); setOpen(o => !o); }}
      onDragOver={(e) => {
        if (e.dataTransfer.types.includes('application/x-cv-library')) {
          e.preventDefault();
          e.dataTransfer.dropEffect = 'copy';
          setDragOver(true);
        }
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => { setDragOver(false); tryHandlePayload(e); }}
    >
      <span className="line"/>
      <span className="lbl">{dragOver ? 'Drop here' : '+ add block'}</span>
      <span className="line"/>
      {onInsertVi && (
        <button
          className="vi-action"
          onClick={(e) => { e.stopPropagation(); onInsertVi(); }}
          title="Vi: 3 block options here">
          <ViShape size={11}/> + Vi
        </button>
      )}
      {open && (
        <div style={{
          position:'absolute', background:'var(--bg-surface)', border:'1.5px solid var(--accent-gold)',
          borderRadius:'var(--r-md)', padding:8, boxShadow:'var(--shadow-pop)',
          display:'grid', gridTemplateColumns:'repeat(4, 1fr)', gap:4, zIndex:20,
          marginTop:36,
        }} onClick={e => e.stopPropagation()}>
          {blocks.map(([key, def]) => (
            <button key={key} className="ws-block-btn"
              style={{padding:'10px 8px',minWidth:80}}
              onClick={() => { onAdd(key); setOpen(false); }}>
              <CvIcon name={def.icon} size={18} tone="bronze"/>
              {def.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
window.WSAddDivider = AddDivider;
