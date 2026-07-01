// canvases/workshop/Polish.jsx
// UX polish layer for Workshop:
//   - Keyboard shortcuts overlay (press "?" to show)
//   - First-run onboarding tour explaining the new Vi capabilities
//   - Error boundary that catches render errors and recovers gracefully

const { useState: useState_p, useEffect: useEffect_p } = React;

// ============================================================
// Keyboard shortcuts overlay
// ============================================================

const SHORTCUTS = [
  { group: 'Navigate', items: [
    { keys: '⌘K',          desc: 'Open Search palette' },
    { keys: '⌘Z',          desc: 'Undo (also for Vi edits)' },
    { keys: '⌘⇧Z',         desc: 'Redo' },
    { keys: '←  →',         desc: 'Previous / next slide' },
    { keys: '?',           desc: 'This help overlay' },
    { keys: 'Esc',         desc: 'Close modal / cancel' },
  ]},
  { group: 'Edit', items: [
    { keys: '⌘D',          desc: 'Duplicate current page (deck)' },
    { keys: 'Click any text', desc: 'Inline edit · Vi alternates appear' },
    { keys: 'shorter / formal / specific', desc: 'Field tone variants' },
  ]},
  { group: 'Vi gallery', items: [
    { keys: '1  2  3',       desc: 'Pick that candidate' },
    { keys: '←  →',          desc: 'Move focus between candidates' },
    { keys: '↵',            desc: 'Apply focused candidate' },
    { keys: 'Esc',          desc: 'Close gallery' },
    { keys: '+ 3 more',      desc: 'Generate 3 more without losing these' },
  ]},
  { group: 'Vi everywhere', items: [
    { keys: '⤧ next to any field',  desc: 'Per-field alternates' },
    { keys: '+ Vi on dividers',     desc: '3 block proposals for that slot' },
    { keys: 'Transform',            desc: 'Whole-doc transforms (Shorten, Urgent, etc.)' },
    { keys: '+ Template',           desc: 'Save with Vi-extracted variables' },
    { keys: 'Chat rail edits',      desc: 'Type "change X to Y" — Vi proposes a diff' },
  ]},
];

function WSShortcutsOverlay() {
  const [open, setOpen] = useState_p(false);
  useEffect_p(() => {
    function onKey(e) {
      if (e.target?.tagName === 'INPUT' || e.target?.tagName === 'TEXTAREA' || e.target?.isContentEditable) return;
      if (e.key === '?' || (e.key === '/' && e.shiftKey)) { e.preventDefault(); setOpen(o => !o); }
      else if (e.key === 'Escape' && open) { e.preventDefault(); setOpen(false); }
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open]);
  if (!open) return null;
  return (
    <div className="ws-shortcuts-overlay" onClick={() => setOpen(false)}>
      <div className="ws-shortcuts-panel" onClick={e => e.stopPropagation()}>
        <div className="ws-shortcuts-head">
          <ViShape size={18}/>
          <span className="title">Keyboard & Vi shortcuts</span>
          <button className="ws-cand-close" onClick={() => setOpen(false)}>✕</button>
        </div>
        <div className="ws-shortcuts-body">
          {SHORTCUTS.map(g => (
            <div key={g.group} className="ws-shortcuts-group">
              <h4>{g.group}</h4>
              <div className="ws-shortcuts-list">
                {g.items.map(it => (
                  <div key={it.keys + it.desc} className="ws-shortcut-row">
                    <kbd>{it.keys}</kbd>
                    <span>{it.desc}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
        <div className="ws-shortcuts-foot">
          <span>Press <kbd>?</kbd> any time to open this.</span>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// First-run onboarding — pops once, explains the AI surfaces.
// ============================================================

const ONBOARD_KEY = 'cvstudio:onboarded:engine-v2';

const ONBOARD_STEPS = [
  {
    title: 'Vi is woven through Workshop now.',
    body: 'Every block, every page, every field, every doc — generation and selection live where you work.',
    cta: 'Show me',
  },
  {
    title: 'Click any text → Vi pill appears.',
    body: 'Get 3 alternatives, or steer with "shorter / formal / specific". Same pattern for headlines, KPIs, step bodies, anything.',
    cta: 'Next',
  },
  {
    title: 'Hover a "+ add block" divider.',
    body: 'A black "+ Vi" pill shows up. Click it → 3 block proposals fit to that slot, with live previews.',
    cta: 'Next',
  },
  {
    title: 'Transform anything wholesale.',
    body: 'The Transform button in the header opens 7 whole-doc moves (Shorten, Urgent, Audit…). Each gives you 3 candidates as a batch diff.',
    cta: 'Next',
  },
  {
    title: 'Chat with Vi → it can EDIT.',
    body: '"Change page 2 headline to X" or "make this more urgent" — Vi returns a diff card. Apply, or discard. Cmd-Z undoes anything.',
    cta: 'Next',
  },
  {
    title: 'Save → reusable templates.',
    body: 'Click "+ Template". Vi extracts the variable parts (property names, audiences, numbers). Re-run from the Templates canvas with different values.',
    cta: 'Got it',
  },
];

function WSOnboarding() {
  const [step, setStep] = useState_p(-1);
  useEffect_p(() => {
    let done = false;
    try { done = !!localStorage.getItem(ONBOARD_KEY); } catch {}
    if (!done) setStep(0);
  }, []);
  function dismiss() {
    try { localStorage.setItem(ONBOARD_KEY, '1'); } catch {}
    setStep(-1);
  }
  function next() {
    if (step >= ONBOARD_STEPS.length - 1) dismiss();
    else setStep(s => s + 1);
  }
  if (step < 0) return null;
  const s = ONBOARD_STEPS[step];
  return (
    <div className="ws-onboard-overlay">
      <div className="ws-onboard-panel">
        <div className="ws-onboard-head">
          <ViShape size={22}/>
          <span className="title">A note from Vi</span>
          <span className="step">{step + 1} / {ONBOARD_STEPS.length}</span>
          <button className="ws-cand-close" onClick={dismiss}>Skip</button>
        </div>
        <div className="ws-onboard-body">
          <h3>{s.title}</h3>
          <p>{s.body}</p>
        </div>
        <div className="ws-onboard-foot">
          <div className="ws-onboard-dots">
            {ONBOARD_STEPS.map((_, i) => (
              <span
                key={i}
                role="button"
                tabIndex={0}
                onClick={() => setStep(i)}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') setStep(i); }}
                className={i === step ? 'active' : i < step ? 'done' : ''}/>
            ))}
          </div>
          <button className="dsa-btn dsa-btn--primary" onClick={next}>{s.cta}</button>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// Error boundary — wraps a subtree and shows a recovery panel
// if a React render error fires
// ============================================================

class WSErrorBoundary extends React.Component {
  constructor(p) { super(p); this.state = { err: null, info: null }; }
  static getDerivedStateFromError(err) { return { err }; }
  componentDidCatch(err, info) {
    this.setState({ err, info });
    try { console.error('[WSErrorBoundary]', err, info); } catch {}
  }
  reset() { this.setState({ err: null, info: null }); }
  render() {
    if (!this.state.err) return this.props.children;
    return (
      <div className="ws-error-boundary">
        <h3>This part of Workshop hit an error.</h3>
        <p>Vi caught the crash so the rest of Studio keeps working. You can try again, or carry on — your work is auto-saved.</p>
        <pre>{this.state.err?.message || String(this.state.err)}</pre>
        <div style={{display:'flex',gap:8,justifyContent:'flex-end'}}>
          <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => location.reload()}>Reload Studio</button>
          <button className="dsa-btn dsa-btn--primary dsa-btn--sm" onClick={() => this.reset()}>Try again</button>
        </div>
      </div>
    );
  }
}

window.WSShortcutsOverlay = WSShortcutsOverlay;
window.WSOnboarding = WSOnboarding;
window.WSErrorBoundary = WSErrorBoundary;
