// atomicity/Foundations.jsx
// ============================================================================
// Foundations — the brand's visual language, for a person who knows nothing
// about the system. No token names, no var(), no px, no "files" by default.
// Meaning is shown by implication (a colour you see, a roundness you see, a
// depth you see); names are human ("Gold", "Soft", "Floating"); the detail is
// there only if you open it. Composed entirely from AcKit.
//
// Zones, each with one job:
//   • rail (left)   — choose a facet: Palette · Type · Roundness · Depth · Spacing
//   • gallery (mid) — the choices, as tangible visual specimens
//   • preview (right) — a real product surface; the effect of your choices, live
//   • inspector     — a CLOSABLE sheet: what it is, in plain words, + one control
// ============================================================================
const { useState: useState_fd, useEffect: useEffect_fd, useMemo: useMemo_fd, useReducer: useReducer_fd } = React;
const { Specimen, StateDot, Tile, Sheet, Field, HumanControl } = window.AcKit;

window.__acFoundationEdits = window.__acFoundationEdits || {};
function applyEdit(name, value) { window.__acFoundationEdits[name] = value; document.documentElement.style.setProperty(name, value); }
function clearEdit(name) { delete window.__acFoundationEdits[name]; document.documentElement.style.removeProperty(name); }

// the curated, human-facing language (the machinery stays in the Atlas/Scanner)
const FACETS = [
  { id: 'palette', label: 'Palette', icon: 'color-swatches', kind: 'color', blurb: 'The colours that carry the brand.',
    groups: [
      { label: 'Surfaces', items: [
        { t: '--paper', name: 'Paper', desc: 'The warm off-white the whole product rests on.' },
        { t: '--paper-2', name: 'Soft panel', desc: 'A gentle cream for grouped areas and panels.' },
        { t: '--bg-surface', name: 'Card', desc: 'Clean white for cards that lift off the page.' },
        { t: '--bg-dark', name: 'Night', desc: 'The deep ground for bars and dark surfaces.' },
      ] },
      { label: 'Brand', items: [
        { t: '--accent-gold', name: 'Gold', desc: 'The signature highlight — buttons and the numbers that matter.' },
        { t: '--accent-bronze', name: 'Bronze', desc: 'The quiet companion — fine lines, labels and titles.' },
        { t: '--accent-tan', name: 'Tan', desc: 'A soft sandy neutral for gentle accents.' },
      ] },
      { label: 'Text', items: [
        { t: '--ink', name: 'Ink', desc: 'The main reading colour — a warm near-black.' },
        { t: '--fg-secondary', name: 'Muted text', desc: 'Secondary copy and helper text.' },
      ] },
    ] },
  { id: 'type', label: 'Type', icon: 'type', kind: 'font', blurb: 'How words look across the product.',
    groups: [{ label: 'Typefaces', items: [
      { t: '--font-display', name: 'Display', desc: 'Headlines and big numbers — confident and tight.' },
      { t: '--font-body', name: 'Body', desc: 'The everyday reading text everywhere.' },
      { t: '--font-mono', name: 'Detail', desc: 'Small technical labels and codes.' },
    ] }] },
  { id: 'roundness', label: 'Roundness', icon: 'square', kind: 'radius', blurb: 'How soft the corners feel.',
    groups: [{ label: 'Corners', items: [
      { t: '--r-sm', name: 'Subtle', desc: 'Barely-there softening for small chips.' },
      { t: '--r-md', name: 'Soft', desc: 'The everyday corner for inputs and tiles.' },
      { t: '--r-lg', name: 'Rounded', desc: 'Friendly cards and panels.' },
      { t: '--r-xl', name: 'Generous', desc: 'Large hero surfaces.' },
      { t: '--r-pill', name: 'Pill', desc: 'Fully rounded — buttons and tags.' },
    ] }] },
  { id: 'depth', label: 'Depth', icon: 'layers', kind: 'shadow', blurb: 'How far things lift off the page.',
    groups: [{ label: 'Elevation', items: [
      { t: '--elev-1', name: 'Lifted', desc: 'A whisper of separation from the page.' },
      { t: '--elev-2', name: 'Raised', desc: 'A card you feel you could pick up.' },
      { t: '--elev-3', name: 'Floating', desc: 'Menus and popovers above the content.' },
      { t: '--elev-4', name: 'Overlay', desc: 'Dialogs that sit above everything.' },
      { t: '--elev-5', name: 'Dragged', desc: 'The highest — something held in motion.' },
    ] }] },
  { id: 'spacing', label: 'Spacing', icon: 'ruler', kind: 'spacing', blurb: 'The breathing room between things.',
    groups: [{ label: 'Rhythm', items: [
      { t: '--s-2', name: 'Snug', desc: 'Tight grouping — an icon and its label.' },
      { t: '--s-3', name: 'Cozy', desc: 'Comfortable gaps inside a control.' },
      { t: '--s-4', name: 'Comfortable', desc: 'The default breathing room.' },
      { t: '--s-6', name: 'Roomy', desc: 'Between the sections of a panel.' },
      { t: '--s-8', name: 'Generous', desc: 'Between major blocks of the page.' },
    ] }] },
];
const KIND_TO_FACET = { color: 'palette', font: 'type', radius: 'roundness', shadow: 'depth', spacing: 'spacing' };

function AcFoundations({ node }) {
  const focusFacet = node.kind === 'token' || node.kind === 'token-group' || node.kind === 'token-file'
    ? KIND_TO_FACET[(node.data && node.data.kind) || node.id.split('/')[1]] : null;
  const [facetId, setFacetId] = useState_fd(focusFacet || 'palette');
  const [sel, setSel] = useState_fd(node.kind === 'token' ? (node.data && node.data.name) : null);
  const [, force] = useReducer_fd(x => x + 1, 0);
  useEffect_fd(() => {
    const f = focusFacet || facetId; if (f !== facetId) setFacetId(f);
    if (node.kind === 'token') setSel(node.data && node.data.name);
  }, [node.id]);

  const facet = FACETS.find(f => f.id === facetId) || FACETS[0];
  const allItems = useMemo_fd(() => facet.groups.flatMap(g => g.items), [facetId]);
  const selItem = allItems.find(i => i.t === sel) || null;
  const edited = Object.keys(window.__acFoundationEdits);

  return (
    <div className="fz2">
      <div className="fz2-rail">
        {FACETS.map(f => (
          <button key={f.id} className={`fz2-facet ${facetId === f.id ? 'on' : ''}`} onClick={() => { setFacetId(f.id); setSel(null); }}>
            <span className="fz2-facet-ic"><CvIcon name={f.icon} size={16} tone={facetId === f.id ? 'gold' : 'bronze'}/></span>
            <span className="fz2-facet-tx"><b>{f.label}</b><i>{f.blurb}</i></span>
          </button>
        ))}
        {edited.length > 0 && (
          <button className="fz2-resetall" onClick={() => { edited.forEach(clearEdit); setSel(s => s); force(); }}>
            <StateDot state="edited"/> Undo all changes
          </button>
        )}
      </div>

      <div className="fz2-gallery">
        {facet.groups.map(g => (
          <div key={g.label} className="fz2-group">
            <div className="fz2-group-lbl">{g.label}</div>
            <div className="fz2-tiles">
              {g.items.map(it => {
                const dirty = window.__acFoundationEdits[it.t] != null;
                const on = sel === it.t;
                return (
                  <Tile key={it.t} selected={on} className="fz2-tile" onClick={() => setSel(it.t)}>
                    <Specimen kind={facet.kind} name={it.t} size={facet.kind === 'color' ? 'lg' : 'lg'}/>
                    <span className="fz2-tile-name">{it.name}</span>
                    <span className="fz2-tile-state"><StateDot state={on ? 'selected' : dirty ? 'edited' : 'idle'}/></span>
                  </Tile>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      <div className="fz2-preview">
        <div className="fz2-preview-cap">Your product, live</div>
        <LivePreview/>
      </div>

      <Sheet open={!!selItem} onClose={() => setSel(null)}>
        {selItem && <Inspector facet={facet} item={selItem} onChange={() => force()} />}
      </Sheet>
    </div>
  );
}

function Inspector({ facet, item, onChange }) {
  const [adv, setAdv] = useState_fd(false);
  const [usage, setUsage] = useState_fd(() => window.CV_SCAN ? window.CV_SCAN.usage(item.t) : null);
  useEffect_fd(() => {
    if (!window.CV_SCAN) return;
    const upd = () => setUsage(window.CV_SCAN.usage(item.t));
    upd(); return window.CV_SCAN.subscribe(upd);
  }, [item.t]);

  const tok = (window.ATLAS.manifest.tokens || []).find(t => t.name === item.t) || { value: '', definedIn: '' };
  const live = window.__acFoundationEdits[item.t];
  const value = live != null ? live : tok.value;
  const dirty = live != null;
  const places = usage ? usage.total : 0;

  function set(v) { applyEdit(item.t, v); onChange(); }
  function undo() { clearEdit(item.t); onChange(); }
  function save() {
    try {
      window.CV_HOST.commit({ kind: 'css.token', title: 'Set ' + item.name, rationale: '“' + item.name + '” (' + facet.label + ') set to ' + value + '.', payload: { name: item.t.replace(/^--/, ''), value, role: facet.kind, file: tok.definedIn }, provenance: 'you' });
      window.dsaToast?.('Saved to the brand');
    } catch (e) { window.dsaToast?.(e.message); }
  }

  return (
    <div className="fz2-insp">
      <div className="fz2-insp-hero">
        <Specimen kind={facet.kind} name={item.t} size="xl"/>
        <div className="fz2-insp-id">
          <div className="fz2-insp-name">{item.name}</div>
          <div className="fz2-insp-desc">{item.desc}</div>
        </div>
      </div>

      <Field label={`Adjust ${item.name.toLowerCase()}`} hint={facet.kind === 'color' ? 'The change shows everywhere it’s used, instantly.' : 'Watch the live preview update as you go.'}>
        <HumanControl kind={facet.kind} name={item.t} value={value} onChange={set}/>
      </Field>

      <div className="fz2-insp-places">
        <CvIcon name="globe" size={13} tone="bronze"/>
        {places > 0 ? <span>Used in <b>{places}</b> place{places === 1 ? '' : 's'} across your product.</span> : <span>Part of the core language.</span>}
      </div>

      <div className="fz2-insp-acts">
        {dirty && <button className="fz2-btn ghost" onClick={undo}><StateDot state="edited"/> Undo</button>}
        <button className="fz2-btn solid" onClick={save}>Save to brand</button>
      </div>

      <button className="fz2-adv-toggle" onClick={() => setAdv(a => !a)}>
        <CvIcon name={adv ? 'minus' : 'plus'} size={11} tone="muted"/> {adv ? 'Hide' : 'Show'} technical details
      </button>
      {adv && (
        <div className="fz2-adv">
          <div><span>name</span><code>{item.t}</code></div>
          <div><span>value</span><code>{value}</code></div>
          <div><span>defined in</span><code>{tok.definedIn}</code></div>
          {usage && usage.files.length > 0 && <div><span>in files</span><code>{usage.files.slice(0, 6).map(f => f.path.split('/').pop()).join(', ')}{usage.files.length > 6 ? '…' : ''}</code></div>}
        </div>
      )}
    </div>
  );
}

// the live product surface — reads the same tokens, updates as you edit
function LivePreview() {
  return (
    <div className="fzp">
      <div className="fzp-bar">
        <span className="fzp-brand"><span className="fzp-mark"><CvIcon name="atom" size={14} tone="gold"/></span> User Portal</span>
        <span className="fzp-nav"><i/><i/><i/></span>
        <span className="fzp-vipill"><span className="gem"/> Vi</span>
      </div>
      <div className="fzp-card">
        <div className="fzp-photo"><span className="fzp-360"><CvIcon name="vr-headset" size={12} tone="ink"/> 360° tour</span></div>
        <div className="fzp-body">
          <div className="fzp-eyebrow">Property Wizard · listing</div>
          <div className="fzp-addr">14 Eclipse Boulevard</div>
          <div className="fzp-suburb">Bayside · VIC 3196</div>
          <div className="fzp-price">$1.84<span>m</span> <em>guide</em></div>
          <div className="fzp-stats"><span><b>4</b> bed</span><span><b>2</b> bath</span><span><b>2</b> car</span><span><b>540</b> m²</span></div>
          <div className="fzp-btns"><button className="fzp-btn primary">Book inspection</button><button className="fzp-btn ghost">Save</button></div>
        </div>
      </div>
      <div className="fzp-insight"><span className="gem"/><span><b>Vi</b> · three comparable sales settled above guide this month — buyers are active in Bayside.</span></div>
      <div className="fzp-trio"><div><b>23.8</b><span>k views</span></div><div><b>148</b><span>enquiries</span></div><div><b>12</b><span>inspections</span></div></div>
    </div>
  );
}

window.AcFoundations = AcFoundations;
