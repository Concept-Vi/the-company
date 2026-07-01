// atomicity/kit.jsx
// ============================================================================
// AcKit — the AtomiCity component kit. A small set of sophisticated, composable
// primitives that the rest of the app instances. The guiding rule: SHOW meaning
// by visual implication, never by raw technical text. A person with no system
// or domain knowledge should understand everything by looking.
//
//   Specimen     — renders the VISUAL TRUTH of a design value (a colour you see,
//                  a roundness you see, a depth you see) at a tangible scale.
//                  Multi-layered + versatile: the rail, the inspector, and the
//                  gallery all instance it. No numbers, no token names.
//   StateDot     — an animated SVG that shows an item's state (idle → selected →
//                  active → edited) by morphing, not by a label.
//   Tile         — the surface primitive: elevation, hover lift, selected ring.
//   Sheet        — a closable panel (the thing the user couldn't dismiss).
//   HumanControl — a layperson editor that adapts to the value's nature and
//                  shows the change by implication (drag a corner, lift a card).
//   Field        — a labelled wrapper with a plain-language hint.
// ============================================================================
const { useState: useState_k, useEffect: useEffect_k, useRef: useRef_k } = React;

// ---- Specimen: the visual truth of a value --------------------------------
function Specimen({ kind, name, size = 'md' }) {
  const S = { sm: 26, md: 40, lg: 64, xl: 96 }[size] || 40;
  const v = `var(${name})`;
  if (kind === 'color') {
    return <span className="k-spec" style={{ width: S, height: S, borderRadius: 'var(--r-md)', background: v, boxShadow: 'var(--elev-inset)', border: '1px solid color-mix(in srgb, var(--ink) 8%, transparent)' }}/>;
  }
  if (kind === 'radius') {
    return <span className="k-spec" style={{ width: S * 1.3, height: S, background: 'var(--paper-3)', border: '2px solid var(--accent-bronze)', borderRadius: v }}/>;
  }
  if (kind === 'spacing') {
    return (
      <span className="k-spec" style={{ width: S * 1.3, height: S, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: v, background: 'var(--paper-2)', borderRadius: 'var(--r-sm)', padding: '0 6px', overflow: 'hidden' }}>
        <i style={{ width: 8, height: S * 0.5, background: 'var(--accent-bronze)', borderRadius: 1, display: 'block' }}/>
        <i style={{ width: 8, height: S * 0.5, background: 'var(--accent-bronze)', borderRadius: 1, display: 'block' }}/>
      </span>
    );
  }
  if (kind === 'shadow') {
    return <span className="k-spec" style={{ width: S * 1.3, height: S, display: 'grid', placeItems: 'center', background: 'var(--paper-2)', borderRadius: 'var(--r-sm)' }}>
      <i style={{ width: S * 0.8, height: S * 0.6, background: 'var(--bg-surface)', borderRadius: 'var(--r-sm)', boxShadow: v, display: 'block' }}/>
    </span>;
  }
  if (kind === 'font') {
    return <span className="k-spec ghost" style={{ width: S * 1.3, height: S, display: 'grid', placeItems: 'center', font: `700 ${S * 0.5}px ${v}`, color: 'var(--accent-bronze)' }}>Ag</span>;
  }
  return <span className="k-spec ghost" style={{ width: S, height: S, display: 'grid', placeItems: 'center' }}><i style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--accent-bronze)' }}/></span>;
}

// ---- StateDot: animated SVG state ------------------------------------------
function StateDot({ state }) {
  // idle | selected | active | edited — morphs between a ring, a filled diamond,
  // a drawn check, and a pulsing dot. State shown by shape + motion, not text.
  return (
    <span className={`k-state k-state--${state || 'idle'}`} aria-hidden="true">
      <svg viewBox="0 0 24 24" width="18" height="18">
        <circle className="k-ring" cx="12" cy="12" r="8" fill="none" stroke="currentColor" strokeWidth="1.6"/>
        <polygon className="k-gem" points="12,5 19,12 12,19 5,12" fill="currentColor"/>
        <path className="k-check" d="M7 12.5 L10.5 16 L17 8.5" fill="none" stroke="var(--bg-dark)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    </span>
  );
}

// ---- Tile: the surface primitive -------------------------------------------
function Tile({ selected, onClick, className = '', children, style }) {
  return (
    <button type="button" className={`k-tile ${selected ? 'on' : ''} ${className}`} onClick={onClick} style={style}>
      {children}
    </button>
  );
}

// ---- Sheet: a closable panel -----------------------------------------------
function Sheet({ open, onClose, children, side = 'bottom' }) {
  useEffect_k(() => {
    if (!open) return;
    const onKey = e => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, onClose]);
  return (
    <div className={`k-sheet k-sheet--${side} ${open ? 'open' : ''}`} role="dialog">
      <button className="k-sheet-x" onClick={onClose} aria-label="Close">
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><path d="M6 6 L18 18 M18 6 L6 18"/></svg>
      </button>
      {children}
    </div>
  );
}

// ---- Field: labelled, plain-language wrapper -------------------------------
function Field({ label, hint, children }) {
  return (
    <div className="k-field">
      <div className="k-field-label">{label}</div>
      {children}
      {hint && <div className="k-field-hint">{hint}</div>}
    </div>
  );
}

// ---- HumanControl: layperson editor, change shown by implication -----------
function HumanControl({ kind, name, value, onChange }) {
  // color → a big tappable swatch that opens the picker (the swatch IS the value)
  if (kind === 'color') {
    const hex = /^#([0-9a-f]{3,8})$/i.test(value.trim());
    return (
      <label className="k-ctl-color">
        <span className="k-ctl-swatch" style={{ background: `var(${name})` }}>
          <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="#fff" strokeWidth="1.6" style={{ filter: 'drop-shadow(0 1px 2px rgba(0,0,0,.5))' }}><path d="M4 20 L4 15 L15 4 L20 9 L9 20 Z"/><path d="M13 6 L18 11"/></svg>
        </span>
        {hex && <input type="color" value={normHexK(value)} onChange={e => onChange(e.target.value)}/>}
        <span className="k-ctl-color-cap">Tap to change</span>
      </label>
    );
  }
  // radius / spacing → a tactile track; the live specimen above shows the result
  if (kind === 'radius' || kind === 'spacing') {
    const px = parseInt(value, 10);
    const editable = !isNaN(px) && /px\s*$/.test(value.trim());
    if (editable) {
      const max = kind === 'radius' ? 40 : 64;
      return (
        <div className="k-ctl-range">
          <span className="k-ctl-end">{kind === 'radius' ? 'Sharp' : 'Tight'}</span>
          <input type="range" min="0" max={max} value={px} onChange={e => onChange(e.target.value + 'px')}/>
          <span className="k-ctl-end">{kind === 'radius' ? 'Round' : 'Roomy'}</span>
        </div>
      );
    }
  }
  // depth → a lift slider (the specimen shows the float)
  if (kind === 'shadow') {
    return <div className="k-ctl-note">Adjust this in the live preview — it controls how far surfaces lift off the page.</div>;
  }
  if (kind === 'font') {
    return <div className="k-ctl-note">The product's typeface. Set in your brand kit.</div>;
  }
  // fallback: a plain text field, but framed gently (advanced)
  return <input className="k-ctl-text" value={value} onChange={e => onChange(e.target.value)} spellCheck={false}/>;
}

function normHexK(v) { v = v.trim(); if (/^#[0-9a-f]{3}$/i.test(v)) return '#' + v.slice(1).split('').map(c => c + c).join(''); if (/^#[0-9a-f]{8}$/i.test(v)) return v.slice(0, 7); return /^#[0-9a-f]{6}$/i.test(v) ? v : '#000000'; }

// OptionRow — evenly-sized quick-reply buttons (the dynamic "what next" pattern).
// Equal-width grid, centered single-line labels; used wherever the agent offers
// contextual moves. One component, one look, everywhere.
function OptionRow({ options, onPick }) {
  if (!options || !options.length) return null;
  return (
    <div className="k-optionrow">
      {options.map((o, i) => (
        <button key={i} type="button" className={`k-option ${o.primary ? 'primary' : ''}`} onClick={() => onPick(o, i)} title={o.say || o.label}>
          {o.icon && <CvIcon name={o.icon} size={12} tone={o.primary ? 'ink' : 'bronze'}/>}
          <span>{o.label}</span>
        </button>
      ))}
    </div>
  );
}

window.AcKit = { Specimen, StateDot, Tile, Sheet, Field, HumanControl, OptionRow };
Object.assign(window, { Specimen, StateDot, AcTile: Tile, AcSheet: Sheet, AcField: Field, HumanControl, OptionRow });
