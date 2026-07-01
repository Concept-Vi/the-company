// RefinePop.jsx — shared per-item refine UI used across canvases.
// Identical visual language to the dots in Build, so the interaction feels
// the same everywhere: hover any tile, click ↻, type a change, hit refine.

const { useState: useState_rp } = React;

window.RefinePop = function RefinePop({ onRefine, disabled, placeholder, mode = 'dot' }) {
  const [open, setOpen] = useState_rp(false);
  const [val, setVal] = useState_rp('');
  const [busy, setBusy] = useState_rp(false);
  async function go() {
    if (!val.trim() || busy) return;
    setBusy(true);
    try { await onRefine(val.trim()); }
    finally { setBusy(false); setVal(''); setOpen(false); }
  }
  const trigger = mode === 'dot' ? (
    <button
      onClick={(e) => { e.stopPropagation(); setOpen(o => !o); }}
      disabled={disabled || busy}
      title="Refine this one"
      style={{
        position:'absolute',top:4,right:4,
        width:18,height:18,borderRadius:'50%',
        background:'var(--accent-gold)',border:'none',
        cursor: disabled || busy ? 'not-allowed' : 'pointer',
        color:'var(--fg-primary)',font:'700 11px/1 var(--font-body)',
        display:'flex',alignItems:'center',justifyContent:'center',
        opacity: disabled || busy ? 0.4 : 0.85, padding:0, zIndex:2,
      }}>{busy ? '…' : '↻'}</button>
  ) : (
    <button
      onClick={(e) => { e.stopPropagation(); setOpen(o => !o); }}
      disabled={disabled || busy}
      style={{
        background:'transparent', border:'1px solid var(--accent-gold)',
        color:'var(--fg-primary)', borderRadius:999, padding:'4px 10px',
        font:'500 11px/1 var(--font-body)',
        cursor: disabled || busy ? 'not-allowed' : 'pointer',
        display:'inline-flex',alignItems:'center',gap:4,
        opacity: disabled || busy ? 0.5 : 1,
      }}>
      <ViShape size={11}/> {busy ? 'Refining…' : 'Refine'}
    </button>
  );
  return (
    <span style={{position:'relative',display:'inline-flex'}}>
      {trigger}
      {open && (
        <div style={{
          position:'absolute', top:'calc(100% + 6px)', right:0, zIndex:50,
          background:'var(--bg-surface)', border:'1.5px solid var(--accent-gold)',
          borderRadius:'var(--r-md)', padding:10, boxShadow:'var(--shadow-pop)',
          width:260, textAlign:'left',
        }} onClick={e => e.stopPropagation()}>
          <textarea
            autoFocus value={val} onChange={e => setVal(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); go(); } if (e.key === 'Escape') setOpen(false); }}
            placeholder={placeholder} rows="2"
            disabled={busy}
            style={{
              width:'100%', border:'1px solid var(--border-default)', borderRadius:'var(--r-sm)',
              padding:'7px 9px', outline:'none', resize:'none',
              font:'400 12px/1.4 var(--font-body)', color:'var(--fg-primary)',
              background:'var(--bg-canvas)', fontFamily:'var(--font-body)', boxSizing:'border-box',
            }}
          />
          <div style={{display:'flex',gap:6,marginTop:8,justifyContent:'flex-end'}}>
            <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => setOpen(false)}>Cancel</button>
            <button className="dsa-btn dsa-btn--ai dsa-btn--sm" onClick={go} disabled={!val.trim() || busy}>
              <ViShape size={11}/> {busy ? 'Working' : 'Refine'}
            </button>
          </div>
        </div>
      )}
    </span>
  );
};
