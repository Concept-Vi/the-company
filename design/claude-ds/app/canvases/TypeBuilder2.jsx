// app/canvases/TypeBuilder2.jsx
// Sub-components for TypeBuilder.jsx — split out to keep files manageable.

const { useState: useState_tb2, useEffect: useEffect_tb2, useMemo: useMemo_tb2 } = React;

// ===========================================================================
// Left rail — searchable Type browser (filter to compatible siblings)
// ===========================================================================
function BuilderLibrary({ draft, browseFilter, setBrowseFilter, patch }) {
  const R = window.CV_REGISTRY;
  const [tick, setTick] = useState_tb2(0);
  useEffect_tb2(() => R?.subscribe(() => setTick(t => t + 1)), []);

  const types = useMemo_tb2(() => R?.query(browseFilter) || [], [browseFilter, tick]);
  return (
    <>
      <TypeFilterBar filter={browseFilter} onChange={setBrowseFilter}/>
      <TypeTree filter={browseFilter} selected={draft?.id}
        onSelect={(id) => {
          // Selecting a sibling = "extend this one" prompt
          if (id === draft.id) return;
          if (confirm(`Switch to editing "${R.get(id)?.name}"? Unsaved changes will be lost.`)) {
            // we use location-state via a custom event so parent reloads draft
            window.dispatchEvent(new CustomEvent('tb-open', { detail: { id } }));
          }
        }}/>
      <div style={{marginTop:14, paddingTop:12, borderTop:'1px dashed var(--border-faint)'}}>
        <button className="dsa-btn dsa-btn--outline dsa-btn--sm" style={{width:'100%'}}
          onClick={() => window.dispatchEvent(new CustomEvent('tb-open', { detail: { id: null } }))}>
          + New blank Type
        </button>
      </div>
    </>
  );
}

// ===========================================================================
// Center — live preview of the Type
// ===========================================================================
function BuilderPreview({ draft, big, mode, brief, setBrief, viPropose, busy }) {
  const R = window.CV_REGISTRY;
  const resolved = useMemo_tb2(() => {
    // Resolve with virtual ancestor lookup since draft.id may not be saved yet
    const base = draft.extends ? R?.resolve(draft.extends) : null;
    return base ? {
      ...base, ...draft,
      slots: { ...(base.slots || {}), ...(draft.slots || {}) },
      defaults: { ...(base.defaults || {}), ...(draft.defaults || {}) },
      variables: mergeVars(base.variables, draft.variables),
      tags: [...new Set([...(base.tags || []), ...(draft.tags || [])])],
    } : { ...draft };
  }, [draft]);

  return (
    <div className={`tb-preview ${big ? 'big' : ''}`}>
      {mode === 'vi' && (
        <div className="tb-vi-shell">
          <div className="tb-vi-head">
            <ViShape size={20} animated={busy}/>
            <div>
              <h3>Vi-led Type authoring</h3>
              <p>Describe the Type. Vi will propose schema, slots, defaults, variables, and an icon. You can edit afterwards in any mode.</p>
            </div>
          </div>
          <textarea rows="3" placeholder="e.g. A funnel-style widget showing top-of-funnel volume, conversion %, and value at each stage"
            value={brief} onChange={e => setBrief(e.target.value)} disabled={busy}/>
          <div className="tb-vi-cta">
            <button className="dsa-btn dsa-btn--ai" onClick={viPropose} disabled={busy || !brief.trim()}>
              <ViShape size={12} animated={busy}/> {busy ? 'Vi is drafting…' : 'Draft schema with Vi →'}
            </button>
            <span className="dim">Vi will fill the inspector. Nothing is saved until you press Save.</span>
          </div>
          <hr/>
          <p style={{font:'400 11px/1.6 var(--font-body)',color:'var(--fg-muted)',margin:0}}>
            Tip — Vi works best with concrete examples. Mention the kind of data, who looks at it,
            and any blocks it should embed.
          </p>
        </div>
      )}

      {mode !== 'vi' && (
        <>
          <div className="tb-preview-head">
            <div className="ic"><CvIcon name={draft.icon || 'check-square'} size={22} tone="bronze"/></div>
            <div className="meta">
              <h2>{draft.name || <em className="dim">Unnamed Type</em>}</h2>
              <div className="row">
                <TypeLayerBadge layer={draft.layer} size="md"/>
                <span className="fam">{draft.family || 'general'}</span>
                <TypeProvBadge p={draft.provenance}/>
              </div>
            </div>
          </div>
          {draft.extends && (
            <div className="tb-preview-lineage">
              <span className="dim">extends</span>
              <TypeLineageStrip id={draft.extends}/>
            </div>
          )}
          <p className="tb-preview-desc">{draft.description || <em className="dim">No description yet.</em>}</p>

          {/* Live thumbnail at canvas scale — the same renderer everywhere */}
          <section className="tb-preview-section">
            <h4>Visual preview</h4>
            <div className="tb-preview-thumb-wrap">
              {window.TypeThumb && <TypeThumb type={resolved} width={520} height={320}/>}
            </div>
          </section>

          <section className="tb-preview-section">
            <h4>Slots ({Object.keys(resolved.slots || {}).length})</h4>
            <TypeSlotList type={resolved} value={null}/>
          </section>

          <section className="tb-preview-section">
            <h4>Defaults</h4>
            <pre className="tb-preview-json">{JSON.stringify(resolved.defaults || {}, null, 2) || '{}'}</pre>
          </section>

          {(resolved.variables || []).length > 0 && (
            <section className="tb-preview-section">
              <h4>Variables ({resolved.variables.length})</h4>
              <ul className="tb-var-list">
                {resolved.variables.map(v => (
                  <li key={v.key}>
                    <strong>{v.label || v.key}</strong>
                    <code>{`{{${v.key}}}`}</code>
                    <span className="dim">{v.kind}</span>
                    <span className="def">= {String(v.default ?? '')}</span>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </>
      )}
    </div>
  );
}

// Render a representative archetype — what the Type *looks like* in context.
function RenderArchetype({ draft, resolved }) {
  const layer = draft.layer;
  if (layer === 'token') {
    const swatch = resolved.defaults?.hex || resolved.defaults?.family || '';
    return (
      <section className="tb-archetype">
        {resolved.defaults?.hex ? (
          <div style={{height:80, borderRadius:'var(--r-md)', background: resolved.defaults.hex, border:'1px solid var(--border-faint)'}}/>
        ) : (
          <div style={{padding:'14px 18px', background:'var(--bg-surface)', border:'1px solid var(--border-faint)', borderRadius:'var(--r-md)', font:`600 22px/1.2 "${swatch || 'serif'}"`}}>The mathematics of operation.</div>
        )}
      </section>
    );
  }
  if (layer === 'atom') {
    return (
      <section className="tb-archetype">
        <div className="tb-atom-preview">
          <CvIcon name={resolved.defaults?.name || resolved.icon || 'star'} size={28} tone="bronze"/>
        </div>
      </section>
    );
  }
  if (layer === 'block') {
    const key = resolved.runtime?.key || draft.runtime?.key;
    const def = key && window.WS_BLOCKS?.[key];
    if (def?.render) {
      const data = { ...def.defaults, ...(resolved.defaults || {}) };
      return (
        <section className="tb-archetype">
          <div className="tb-block-preview">{def.render(data, () => {})}</div>
        </section>
      );
    }
    return <SchemaPreview defaults={resolved.defaults || {}}/>;
  }
  if (layer === 'system') {
    return (
      <section className="tb-archetype">
        <div className="tb-sys-preview">
          {Object.keys(resolved.slots || {}).map(k => (
            <div key={k} className="slot-tile">
              <span className="lbl">{resolved.slots[k].label || k}</span>
              <span className="dim">{(resolved.slots[k].accepts?.layers || []).join(' / ') || 'any'}</span>
            </div>
          ))}
        </div>
      </section>
    );
  }
  if (layer === 'surface') {
    return (
      <section className="tb-archetype">
        <div className="tb-surface-preview">
          <div className="chrome">
            <span className="dot"/><span className="dot"/><span className="dot"/>
            <span className="title">{resolved.name}</span>
          </div>
          <div className="body">
            {Object.keys(resolved.slots || {}).map(k => (
              <div key={k} className="slot">{resolved.slots[k].label || k}</div>
            ))}
            {!Object.keys(resolved.slots || {}).length && <span className="dim">Add a slot to compose this surface.</span>}
          </div>
        </div>
      </section>
    );
  }
  if (layer === 'doc') {
    return (
      <section className="tb-archetype">
        <div className="tb-doc-preview">
          <strong>{resolved.name}</strong>
          <span className="dim">composes</span>
          {Object.keys(resolved.slots || {}).map(k => (
            <div key={k} className="composes">{resolved.slots[k].label || k} ({(resolved.slots[k].accepts?.layers || ['any']).join('/')})</div>
          ))}
        </div>
      </section>
    );
  }
  return null;
}

function SchemaPreview({ defaults }) {
  const keys = Object.keys(defaults || {});
  return (
    <section className="tb-archetype">
      {keys.length ? keys.map(k => (
        <div key={k} className="tb-schema-row">
          <span className="k">{k}</span>
          <span className="v">{stringifyField(defaults[k])}</span>
        </div>
      )) : <em className="dim">No default schema yet. Vi can propose one in the Vi tab.</em>}
    </section>
  );
}

function stringifyField(v) {
  if (v == null) return '—';
  if (typeof v === 'string') return v;
  if (typeof v === 'number' || typeof v === 'boolean') return String(v);
  return JSON.stringify(v).slice(0, 100);
}

function mergeVars(a = [], b = []) {
  const m = new Map();
  for (const v of a || []) m.set(v.key, v);
  for (const v of b || []) m.set(v.key, { ...m.get(v.key), ...v });
  return [...m.values()];
}

// ===========================================================================
// Right rail — inspector (mode-driven: visual / form / json)
// ===========================================================================
function BuilderInspector({ draft, patch, mode, patchSlot, removeSlot, addSlot, patchVariable, removeVariable, addVariable, parentCandidates, viSuggestSlots, busy, setSlotBrowser, embedded }) {
  if (mode === 'json') {
    return <JsonEditor draft={draft} patch={patch}/>;
  }
  return (
    <div className={`tb-inspector ${embedded ? 'embedded' : ''}`}>
      <h5>Basics</h5>
      <BasicsForm draft={draft} patch={patch}/>

      <h5>Lineage</h5>
      <LineageForm draft={draft} patch={patch} parentCandidates={parentCandidates}/>

      <h5>Slots
        <button className="vi-aux" onClick={viSuggestSlots} disabled={busy} title="Vi: suggest more slots">
          <ViShape size={10}/> suggest
        </button>
        <button className="aux" onClick={addSlot} title="Add slot">+</button>
      </h5>
      <SlotsEditor draft={draft} patchSlot={patchSlot} removeSlot={removeSlot} setSlotBrowser={setSlotBrowser}/>

      <h5>Default data
        <button className="aux" onClick={() => patch({ defaults: {} })} title="Clear defaults">clear</button>
      </h5>
      <DefaultsEditor draft={draft} patch={patch}/>

      <h5>Variables
        <button className="aux" onClick={addVariable} title="Add variable">+</button>
      </h5>
      <VariablesEditor draft={draft} patchVariable={patchVariable} removeVariable={removeVariable}/>

      <h5>Tags</h5>
      <TagsField draft={draft} patch={patch}/>
    </div>
  );
}

// ===========================================================================
// Field editors
// ===========================================================================
function BasicsForm({ draft, patch }) {
  const R = window.CV_REGISTRY;
  return (
    <div className="tb-form">
      <label><span>Name</span>
        <input value={draft.name || ''} onChange={e => patch({ name: e.target.value })} placeholder="Tower performance widget"/>
      </label>
      <label><span>Stable id</span>
        <input value={draft.id || ''} onChange={e => patch({ id: e.target.value })} className="mono" placeholder="surface.widget.tower-performance"/>
      </label>
      <label><span>Description</span>
        <textarea rows="2" value={draft.description || ''} onChange={e => patch({ description: e.target.value })} placeholder="One sentence — what is this Type for?"/>
      </label>
      <div className="tb-row">
        <label><span>Layer</span>
          <select value={draft.layer || 'block'} onChange={e => patch({ layer: e.target.value })}>
            {R.LAYERS.map(l => <option key={l} value={l}>{R.LAYER_INFO[l].label}</option>)}
          </select>
        </label>
        <label><span>Family</span>
          <input value={draft.family || ''} onChange={e => patch({ family: e.target.value })} className="mono"/>
        </label>
      </div>
      <label><span>Icon</span>
        <input value={draft.icon || ''} onChange={e => patch({ icon: e.target.value })} className="mono" placeholder="check-square"/>
      </label>
    </div>
  );
}

function LineageForm({ draft, patch, parentCandidates }) {
  return (
    <div className="tb-form">
      <label><span>Extends</span>
        <select value={draft.extends || ''} onChange={e => patch({ extends: e.target.value || null })}>
          <option value="">— No parent (root) —</option>
          {parentCandidates.map(t => <option key={t.id} value={t.id}>{t.name}  ·  {t.id}</option>)}
        </select>
      </label>
      {draft.extends && (
        <p className="tb-form-hint">Inherits slots, defaults, and variables from parent. You can override any of them below.</p>
      )}
    </div>
  );
}

function ViForm({ draft, brief, setBrief, viPropose, busy }) {
  return (
    <div className="tb-form">
      <label><span>Describe the Type</span>
        <textarea rows="4" placeholder="e.g. A funnel-style widget showing top-of-funnel volume, conversion %, and value at each stage" value={brief} onChange={e => setBrief(e.target.value)}/>
      </label>
      <button className="dsa-btn dsa-btn--ai" onClick={viPropose} disabled={busy || !brief.trim()}>
        <ViShape size={12} animated={busy}/> {busy ? 'Drafting…' : 'Draft with Vi'}
      </button>
    </div>
  );
}

function SlotsEditor({ draft, patchSlot, removeSlot, setSlotBrowser }) {
  const slots = draft.slots || {};
  const keys = Object.keys(slots);
  return (
    <div className="tb-slots">
      {keys.length === 0 && <p className="tb-form-hint">No slots yet. Slots define what other Types can be embedded inside this one.</p>}
      {keys.map(k => {
        const s = slots[k];
        return (
          <div key={k} className="tb-slot-card">
            <div className="head">
              <input className="key-in" value={k} readOnly title="Rename: remove and re-add"/>
              <button className="rm" onClick={() => removeSlot(k)}>×</button>
            </div>
            <label><span>Label</span><input value={s.label || ''} onChange={e => patchSlot(k, { label: e.target.value })}/></label>
            <div className="tb-row">
              <label><input type="checkbox" checked={!!s.multiple} onChange={e => patchSlot(k, { multiple: e.target.checked })}/> Multiple</label>
              <label><input type="checkbox" checked={!!s.optional} onChange={e => patchSlot(k, { optional: e.target.checked })}/> Optional</label>
            </div>
            <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => setSlotBrowser?.({ name: k, slot: s })}>
              Edit accepts → <span className="dim"><SlotAcceptsHint slot={s}/></span>
            </button>
          </div>
        );
      })}
    </div>
  );
}

function DefaultsEditor({ draft, patch }) {
  const [raw, setRaw] = useState_tb2(JSON.stringify(draft.defaults || {}, null, 2));
  const [err, setErr] = useState_tb2(null);
  useEffect_tb2(() => { setRaw(JSON.stringify(draft.defaults || {}, null, 2)); }, [draft.id]);
  function commit() {
    try {
      const v = JSON.parse(raw || '{}');
      patch({ defaults: v });
      setErr(null);
    } catch (e) { setErr(e.message); }
  }
  return (
    <div className="tb-defaults">
      <textarea
        className="mono" rows="6"
        value={raw} onChange={e => setRaw(e.target.value)}
        onBlur={commit} spellCheck={false}/>
      {err && <p className="tb-err">Parse error: {err}</p>}
    </div>
  );
}

function VariablesEditor({ draft, patchVariable, removeVariable }) {
  const vars = draft.variables || [];
  return (
    <div className="tb-vars">
      {vars.length === 0 && <p className="tb-form-hint">Variables become Template parameters. List the 2-5 things that change per run.</p>}
      {vars.map((v, i) => (
        <div key={i} className="tb-var-row">
          <input placeholder="key" className="mono" value={v.key || ''} onChange={e => patchVariable(i, { key: e.target.value })}/>
          <input placeholder="label" value={v.label || ''} onChange={e => patchVariable(i, { label: e.target.value })}/>
          <input placeholder="default" value={v.default || ''} onChange={e => patchVariable(i, { default: e.target.value })}/>
          <select value={v.kind || 'text'} onChange={e => patchVariable(i, { kind: e.target.value })}>
            <option value="text">text</option><option value="number">number</option><option value="url">url</option><option value="choice">choice</option>
          </select>
          <button className="rm" onClick={() => removeVariable(i)}>×</button>
        </div>
      ))}
    </div>
  );
}

function TagsField({ draft, patch }) {
  const [raw, setRaw] = useState_tb2((draft.tags || []).join(', '));
  useEffect_tb2(() => { setRaw((draft.tags || []).join(', ')); }, [draft.id]);
  function commit() {
    const list = raw.split(',').map(s => s.trim()).filter(Boolean);
    patch({ tags: [...new Set(list)] });
  }
  return (
    <input className="tb-tags-in mono" value={raw} onChange={e => setRaw(e.target.value)} onBlur={commit} placeholder="comma, separated, tags"/>
  );
}

function JsonEditor({ draft, patch }) {
  const [raw, setRaw] = useState_tb2(JSON.stringify(draft, null, 2));
  const [err, setErr] = useState_tb2(null);
  useEffect_tb2(() => { setRaw(JSON.stringify(draft, null, 2)); }, [draft.id]);
  function commit() {
    try {
      const next = JSON.parse(raw);
      patch(next);
      setErr(null);
    } catch (e) { setErr(e.message); }
  }
  return (
    <div className="tb-json-edit">
      <textarea className="mono" rows="40" value={raw} onChange={e => setRaw(e.target.value)} onBlur={commit} spellCheck={false}/>
      {err && <p className="tb-err">Parse error: {err}</p>}
    </div>
  );
}

function ReviewPanel({ draft }) {
  return (
    <div className="tb-review">
      <h3>{draft.name}</h3>
      <p className="dim">{draft.description}</p>
      <pre className="mono">{JSON.stringify(draft, null, 2)}</pre>
    </div>
  );
}

// ===========================================================================
// Modal — pick what a slot accepts
// ===========================================================================
function SlotBrowserModal({ slot, onClose, onApply }) {
  const R = window.CV_REGISTRY;
  const [acc, setAcc] = useState_tb2({
    layers: slot?.accepts?.layers || [],
    families: slot?.accepts?.families || [],
    tags: slot?.accepts?.tags || [],
  });
  const [familyInput, setFamilyInput] = useState_tb2((acc.families || []).join(', '));
  const [tagInput, setTagInput] = useState_tb2((acc.tags || []).join(', '));

  const preview = useMemo_tb2(() => R?.candidatesForSlot({ accepts: acc }) || [], [acc]);

  function toggleLayer(l) {
    setAcc(a => ({ ...a, layers: a.layers.includes(l) ? a.layers.filter(x => x !== l) : [...a.layers, l] }));
  }
  function commitFamilies() {
    setAcc(a => ({ ...a, families: familyInput.split(',').map(s => s.trim()).filter(Boolean) }));
  }
  function commitTags() {
    setAcc(a => ({ ...a, tags: tagInput.split(',').map(s => s.trim()).filter(Boolean) }));
  }

  return (
    <div className="tb-modal" onClick={onClose}>
      <div className="tb-modal-inner" onClick={e => e.stopPropagation()}>
        <header>
          <h3>What can this slot accept?</h3>
          <button onClick={onClose}>×</button>
        </header>
        <div className="tb-modal-body">
          <div className="tb-modal-form">
            <h5>Layers (any of)</h5>
            <div className="layer-pills">
              {R.LAYERS.map(l => (
                <button key={l} className={acc.layers.includes(l) ? 'on' : ''} onClick={() => toggleLayer(l)}>
                  <span className="pip" style={{background:R.LAYER_INFO[l].swatch}}/> {R.LAYER_INFO[l].label}
                </button>
              ))}
            </div>
            <h5>Families (any of) <span className="dim">comma-separated</span></h5>
            <input className="mono" value={familyInput} onChange={e => setFamilyInput(e.target.value)} onBlur={commitFamilies} placeholder="widget, deck-slide"/>
            <h5>Tags (any of) <span className="dim">comma-separated</span></h5>
            <input className="mono" value={tagInput} onChange={e => setTagInput(e.target.value)} onBlur={commitTags} placeholder="data, media"/>
          </div>
          <div className="tb-modal-preview">
            <h5>Matching Types · {preview.length}</h5>
            <div className="tb-modal-list">
              {preview.length === 0 && <em className="dim">Nothing matches. Loosen the filter.</em>}
              {preview.slice(0, 30).map(t => <TypeChip key={t.id} type={t}/>)}
              {preview.length > 30 && <span className="dim">+ {preview.length - 30} more</span>}
            </div>
          </div>
        </div>
        <footer>
          <button className="dsa-btn dsa-btn--ghost" onClick={onClose}>Cancel</button>
          <button className="dsa-btn dsa-btn--primary" onClick={() => onApply({ accepts: acc })}>Save accepts</button>
        </footer>
      </div>
    </div>
  );
}

Object.assign(window, {
  BuilderLibrary, BuilderPreview, BuilderInspector, RenderArchetype, SchemaPreview,
  BasicsForm, LineageForm, ViForm, SlotsEditor, DefaultsEditor, VariablesEditor,
  TagsField, JsonEditor, ReviewPanel, SlotBrowserModal,
});
