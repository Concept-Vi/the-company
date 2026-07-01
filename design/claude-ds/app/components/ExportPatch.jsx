// ExportPatch.jsx — modal that shows what's changed and lets you download patches
const { useState: useState_xp, useMemo: useMemo_xp } = React;

function ExportPatch({ open, onClose, generatedIcons, extraColors, colorEdits, patternEdits }) {
  const iconsJs = useMemo_xp(() => {
    if (!generatedIcons.length) return null;
    const entries = generatedIcons.map(g => `  '${g.name}': \`${g.body}\`,`).join('\n');
    return `// Add these to assets/icons/cv-icons.js inside CV_ICONS.data:\n\nwindow.CV_ICONS.data = Object.assign(window.CV_ICONS.data || {}, {\n${entries}\n});\n`;
  }, [generatedIcons]);

  const colorsCss = useMemo_xp(() => {
    const lines = [];
    if (Object.keys(colorEdits).length) {
      lines.push('/* Edits to base palette tokens */');
      for (const [name, hex] of Object.entries(colorEdits)) {
        const cssName = name.startsWith('--') ? name : `--${slug(name)}`;
        lines.push(`  ${cssName}: ${hex};`);
      }
      lines.push('');
    }
    if (extraColors.length) {
      lines.push('/* New palette groups added in Studio */');
      const groups = {};
      for (const c of extraColors) { groups[c.group] = (groups[c.group] || []).concat(c); }
      for (const [g, cs] of Object.entries(groups)) {
        lines.push(`  /* ${g} */`);
        for (const c of cs) lines.push(`  --${slug(c.name)}: ${c.hex.toUpperCase()};   /* ${c.role} */`);
      }
    }
    if (!lines.length) return null;
    return `/* Append inside :root in colors_and_type.css */\n:root {\n${lines.map(l => l.startsWith('  ')||l==='' ? l : '  ' + l).join('\n')}\n}\n`;
  }, [extraColors, colorEdits]);

  const patternsCss = useMemo_xp(() => {
    const entries = Object.entries(patternEdits || {});
    if (!entries.length) return null;
    const groups = { spacing: [], radii: [], shadows: [], motion: [], other: [] };
    for (const [name, val] of entries) {
      if (val == null) continue;
      const bucket =
        name.startsWith('s-')      ? 'spacing' :
        name.startsWith('r-')      ? 'radii'   :
        name.startsWith('shadow-') ? 'shadows' :
        (name.startsWith('ease-') || name.startsWith('dur-')) ? 'motion' :
        'other';
      groups[bucket].push([name, val]);
    }
    const out = [];
    const labels = { spacing: 'Spacing', radii: 'Radii', shadows: 'Shadows', motion: 'Motion', other: 'Other' };
    for (const k of Object.keys(groups)) {
      if (!groups[k].length) continue;
      out.push(`  /* ${labels[k]} */`);
      for (const [n, v] of groups[k]) out.push(`  --${n}: ${v};`);
      out.push('');
    }
    if (!out.length) return null;
    return `/* Pattern edits — patch inside :root in colors_and_type.css */\n:root {\n${out.join('\n').replace(/\n$/, '')}\n}\n`;
  }, [patternEdits]);

  if (!open) return null;

  const empty = !iconsJs && !colorsCss && !patternsCss;

  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(31,26,18,.4)',
      backdropFilter: 'blur(4px)', zIndex: 200,
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 32,
    }} onClick={onClose}>
      <div style={{
        background: 'var(--bg-canvas)', borderRadius: 'var(--r-xl)',
        width: 'min(720px, 100%)', maxHeight: '88vh', overflow: 'auto',
        boxShadow: 'var(--shadow-modal)',
        padding: '24px 28px 28px',
      }} onClick={e => e.stopPropagation()}>
        <div style={{display:'flex',alignItems:'center',marginBottom:6}}>
          <h2 style={{font:'700 22px/1 var(--font-display)',color:'var(--accent-bronze)',margin:0,letterSpacing:'-0.02em'}}>Export to design system</h2>
          <button onClick={onClose} style={{marginLeft:'auto',background:'none',border:'none',cursor:'pointer',color:'var(--fg-muted)',fontSize:18}}>✕</button>
        </div>
        <p style={{font:'400 13px/1.55 var(--font-body)',color:'var(--fg-secondary)',margin:'0 0 18px',maxWidth:520}}>
          Studio holds your edits in browser state. To make them stick across the actual design system files, drop these patches into the right places.
        </p>

        {empty && (
          <div className="dsa-stub">
            <h3>Nothing to export yet</h3>
            <p>Once you adopt generated icons, generate new palettes, or edit existing tokens, the patches will appear here.</p>
          </div>
        )}

        {iconsJs && <ExportBlock title="Icons → cv-icons.js" file="assets/icons/cv-icons.js" code={iconsJs}/>}
        {colorsCss && <ExportBlock title="Colors → colors_and_type.css" file="colors_and_type.css" code={colorsCss}/>}
        {patternsCss && <ExportBlock title="Motion & space → colors_and_type.css" file="colors_and_type.css" code={patternsCss}/>}
      </div>
    </div>
  );
}

function ExportBlock({ title, file, code }) {
  const [copied, setCopied] = useState_xp(false);
  function copy() {
    navigator.clipboard?.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }
  function download() {
    const ext = file.split('.').pop();
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `studio-patch.${ext === 'js' ? 'js' : 'css'}`;
    a.click();
    URL.revokeObjectURL(url);
  }
  return (
    <div style={{marginBottom: 16}}>
      <div style={{display:'flex',alignItems:'baseline',marginBottom:8}}>
        <h3 style={{font:'700 14px/1 var(--font-display)',color:'var(--fg-primary)',margin:0}}>{title}</h3>
        <span style={{font:'500 11px/1 var(--font-mono)',color:'var(--fg-muted)',marginLeft:8}}>→ {file}</span>
        <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" style={{marginLeft:'auto'}} onClick={copy}>{copied ? '✓ Copied' : 'Copy'}</button>
        <button className="dsa-btn dsa-btn--outline dsa-btn--sm" onClick={download}>Download</button>
      </div>
      <pre style={{
        background:'var(--bg-dark)', color:'var(--fg-inverse)',
        padding:'14px 16px', borderRadius:'var(--r-md)',
        font:'400 11px/1.55 var(--font-mono)',
        whiteSpace:'pre', overflow:'auto', maxHeight:'30vh',
        margin: 0,
      }}>{code}</pre>
    </div>
  );
}

function slug(s) { return String(s).toLowerCase().replace(/[^a-z0-9-]+/g, '-').replace(/^-|-$/g,''); }

window.ExportPatch = ExportPatch;
