// canvases/Voice.jsx — voice rules + vocab + AI rewriter + tone variants
const { useState: useState_v } = React;

const VOICE_RULES = [
  { id: 'r1', title: 'Sentence case for everything',
    desc: 'Including button labels and screen titles. "Brand Kit" not "BRAND KIT" or "brand kit".',
    bad: 'CLICK HERE TO GET STARTED', good: 'Click here to get started' },
  { id: 'r2', title: 'Second person, never first-person plural',
    desc: 'Talk to the reader directly. "You can…" not "We let you…".',
    bad: 'We give users the ability to upload logos.', good: 'You can upload your logos here.' },
  { id: 'r3', title: 'Imperative for actions',
    desc: 'Buttons are verbs. Select, Filter, Upload, Publish — not "Selection" or "The Filter".',
    bad: 'Confirmation', good: 'Confirm' },
  { id: 'r4', title: 'No exclamation marks',
    desc: 'The brand is calm and precise. Excitement is shown through clarity, not punctuation.',
    bad: "You're all set! Your hub is live!", good: "You're all set — your hub is live." },
  { id: 'r5', title: 'No emoji in body copy',
    desc: 'Emoji belong in sidebar nav only. Never in product copy, prose, or button text.',
    bad: '🚀 Get started in seconds', good: 'Get started in seconds' },
  { id: 'r6', title: 'Inline previews of consequences',
    desc: 'Helper text shows what will happen with the variable parts emphasised, like the URL preview pattern.',
    bad: 'Your hub URL will be generated automatically.', good: 'URL preview: conceptv.io/panotours/acme/tower-east' },
  { id: 'r7', title: 'Sparing inline gold accent',
    desc: 'Use the gold emphasis only for dynamic URL fragments, active labels, or link text — never arbitrary emphasis.',
    bad: 'You can <span style="color:#E0C010;font-weight:600">upload</span> images here.', good: 'Drop images at <span style="color:#E0C010;font-weight:600">conceptv.io/upload</span>' },
];

const VOCAB = [
  { term: 'Virtual Hub', meaning: 'The branded panotour surface a viewer experiences in their browser.' },
  { term: 'Hub', meaning: 'A single interactive space within a Virtual Hub (e.g. Entry, Apartment A).' },
  { term: 'Linked Hubs', meaning: 'Per-stage variations of a project that viewers can switch between.' },
  { term: 'Landing Page', meaning: 'The buyer-facing marketing surface that fronts a Virtual Hub.' },
  { term: 'Capture', meaning: 'An annotated screenshot left as a comment inside a Hub.' },
  { term: 'Vi', meaning: 'The AI framework powering User Portal, Property Wizard, and Virtual Hubs.' },
  { term: 'Property Wizard', meaning: 'The configuration engine that takes uploaded design files and assembles a Hub.' },
];

const TONE_CONTEXTS = [
  { id: 'success',    label: 'Success',    example: 'Hub published. Visitors can reach it from your link.' },
  { id: 'error',      label: 'Error',      example: "We couldn't upload that file — check the format and try again." },
  { id: 'onboarding', label: 'Onboarding', example: 'Start by uploading your Brand Kit. Vi will reuse it across every project.' },
  { id: 'empty',      label: 'Empty state', example: 'No projects yet. Create one to see it here.' },
  { id: 'cta',        label: 'Marketing CTA', example: 'Turn an architectural render into a buyer-ready hub in an hour.' },
];

function Voice({ savedRewrites, addSavedRewrite, removeSavedRewrite }) {
  const [paste, setPaste] = useState_v('');
  const [rewritten, setRewritten] = useState_v(null);
  const [rewriteIssues, setRewriteIssues] = useState_v([]);
  const [rewriting, setRewriting] = useState_v(false);

  const [toneCtx, setToneCtx] = useState_v('error');
  const [toneBrief, setToneBrief] = useState_v('Tell the user their file upload failed because it was over 50MB');
  const [toneResults, setToneResults] = useState_v([]);
  const [toneGenerating, setToneGenerating] = useState_v(false);

  const [auditingRule, setAuditingRule] = useState_v(null);
  const [ruleAudits, setRuleAudits] = useState_v({});

  async function rewrite() {
    const text = paste.trim();
    if (!text) return;
    setRewriting(true);
    setRewritten(null);
    setRewriteIssues([]);
    try {
      const rules = VOICE_RULES.map(r => `- ${r.title}: ${r.desc}`).join('\n');
      const prompt = `You are auditing copy against the ConceptV voice. The rules:
${rules}

The user submitted:
"""
${text}
"""

Rewrite the text so it follows EVERY rule. Then list which rules the original violated.

Respond as compact JSON only (no prose, no markdown fences):
{"rewritten": "the rewritten text", "violations": [{"rule":"r1","note":"short reason"}, ...]}

Available rule IDs: r1, r2, r3, r4, r5, r6, r7. Use the short ID exactly.`;
      const reply = await window.CV_AI.complete(prompt);
      let parsed = null;
      try { parsed = JSON.parse(reply); }
      catch {
        const m = String(reply).match(/\{[\s\S]*\}/);
        if (m) { try { parsed = JSON.parse(m[0]); } catch {} }
      }
      if (parsed && parsed.rewritten) {
        setRewritten(parsed.rewritten);
        setRewriteIssues(Array.isArray(parsed.violations) ? parsed.violations : []);
      } else {
        setRewritten(String(reply || '').trim());
      }
    } catch {
      window.dsaToast?.('Rewrite failed. Try again.');
    } finally {
      setRewriting(false);
    }
  }

  async function generateTone() {
    const brief = toneBrief.trim();
    if (!brief) return;
    setToneGenerating(true);
    setToneResults([]);
    try {
      const ctxObj = TONE_CONTEXTS.find(t => t.id === toneCtx);
      const prompt = `Write 3 distinct variants of a "${ctxObj.label}" message for ConceptV.

The brief: ${brief}

Rules: sentence case, second person, no exclamation marks, no emoji, no marketing fluff. Calm, precise, slightly warm. Vary the length and approach across the three — one short and direct, one with a "what to do next" line, one slightly warmer.

Respond as compact JSON only (no prose, no markdown fences):
{"variants": ["...", "...", "..."]}`;
      const reply = await window.CV_AI.complete(prompt);
      let parsed = null;
      try { parsed = JSON.parse(reply); }
      catch {
        const m = String(reply).match(/\{[\s\S]*\}/);
        if (m) { try { parsed = JSON.parse(m[0]); } catch {} }
      }
      if (parsed && Array.isArray(parsed.variants)) {
        setToneResults(parsed.variants.slice(0, 5));
      }
    } catch {
      window.dsaToast?.('Generation failed. Try again.');
    } finally {
      setToneGenerating(false);
    }
  }

  function copy(text) {
    navigator.clipboard?.writeText(text);
    window.dsaToast?.('Copied');
  }

  async function auditRule(rule) {
    setAuditingRule(rule.id);
    try {
      const prompt = `You are auditing the rest of the ConceptV system for compliance with one voice rule.

Rule: ${rule.title}
Explanation: ${rule.desc}

Imagine the typical product UI strings that appear in a SaaS dashboard like ConceptV's (buttons, helper text, empty states, status messages, error toasts, onboarding hints). Generate 3 concrete examples of strings that VIOLATE this rule and would likely appear somewhere in the codebase. For each, provide the corrected version.

Respond as compact JSON only, no prose:
{"findings":[{"location":"<short context hint, e.g. Upload button, Empty calendar, Error toast>","violation":"<the bad string>","fix":"<the good string>"}, ...]}`;
      const reply = await window.CV_AI.complete(prompt);
      let parsed = null;
      try { parsed = JSON.parse(reply); }
      catch {
        const m = String(reply).match(/\{[\s\S]*\}/);
        if (m) { try { parsed = JSON.parse(m[0]); } catch {} }
      }
      if (parsed && Array.isArray(parsed.findings)) {
        setRuleAudits(prev => ({ ...prev, [rule.id]: parsed.findings.slice(0, 6) }));
        window.dsaToast?.(`Found ${parsed.findings.length} likely violations of "${rule.title}"`);
      } else {
        window.dsaToast?.('Audit returned no findings');
      }
    } catch {
      window.dsaToast?.('Audit failed — try again');
    } finally {
      setAuditingRule(null);
    }
  }

  function saveCurrentRewrite() {
    if (!rewritten || !paste.trim()) return;
    const entry = {
      id: 'rw-' + Date.now(),
      original: paste.trim(),
      rewritten,
      violations: rewriteIssues,
      savedAt: new Date().toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'}),
    };
    addSavedRewrite?.(entry);
    window.dsaToast?.('Rewrite saved to library');
  }

  return (
    <>
      <CanvasHeader
        title="Voice & tone"
        sub={`${VOICE_RULES.length} rules · ${VOCAB.length} vocabulary anchors · rewrite anything in brand voice`}
      />
      <div className="dsa-canvas-body">

        {/* Rewriter — the headline feature */}
        <div className="dsa-section">
          <div className="dsa-section-head">
            <h3 className="dsa-section-title">Rewrite anything in brand voice</h3>
            <span className="dsa-section-meta">Paste copy → Vi rewrites and flags which rules the original broke</span>
          </div>
          <div style={{display:'grid',gridTemplateColumns:'1fr 1fr',gap:14}}>
            <div className="dsa-card">
              <div style={{font:'600 11px/1 var(--font-body)',color:'var(--fg-muted)',letterSpacing:'0.08em',textTransform:'uppercase',marginBottom:10}}>Your copy</div>
              <textarea
                style={{
                  border:'1.5px solid var(--accent-gold)', borderRadius:'var(--r-md)',
                  padding:'12px 14px', background:'var(--bg-canvas)', outline:'none',
                  font:'400 14px/1.55 var(--font-body)', color:'var(--fg-primary)',
                  resize:'vertical', minHeight:120, fontFamily:'var(--font-body)',
                }}
                rows="6" placeholder="Paste any block of copy and let Vi rewrite it…"
                value={paste} onChange={e => setPaste(e.target.value)}
              />
              <div style={{display:'flex',gap:8,marginTop:10}}>
                <button className="dsa-btn dsa-btn--ai" onClick={rewrite} disabled={rewriting || !paste.trim()}>
                  <ViShape size={14}/> {rewriting ? 'Rewriting…' : 'Rewrite in brand voice'}
                </button>
                <button className="dsa-btn dsa-btn--ghost" onClick={() => { setPaste(''); setRewritten(null); setRewriteIssues([]); }}>Clear</button>
              </div>
            </div>
            <div className="dsa-card" style={{background: rewritten ? 'var(--accent-gold-50)' : 'var(--bg-surface)'}}>
              <div style={{display:'flex',alignItems:'center',gap:8,marginBottom:10}}>
                <span style={{font:'600 11px/1 var(--font-body)',color:'var(--fg-muted)',letterSpacing:'0.08em',textTransform:'uppercase'}}>Brand voice</span>
                {rewritten && (
                  <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" style={{marginLeft:'auto'}} onClick={() => copy(rewritten)}>Copy</button>
                )}
              </div>
              {rewriting ? (
                <div style={{font:'500 13px/1 var(--font-body)',color:'var(--accent-bronze)',display:'flex',alignItems:'center',gap:8}}>
                  <ViShape size={16} animated/> Vi is auditing and rewriting…
                </div>
              ) : rewritten ? (
                <>
                  <div style={{font:'400 14px/1.55 var(--font-body)',color:'var(--fg-primary)',whiteSpace:'pre-wrap'}}>{rewritten}</div>
                  <div style={{display:'flex',gap:6,marginTop:10}}>
                    <button className="dsa-btn dsa-btn--outline dsa-btn--sm" onClick={saveCurrentRewrite}>Save to library</button>
                    <RefinePop
                      mode="chip"
                      placeholder="Make it shorter, warmer, more direct…"
                      onRefine={async msg => {
                        if (!rewritten) return;
                        setRewriting(true);
                        try {
                          const rules = VOICE_RULES.map(r => `- ${r.title}: ${r.desc}`).join('\n');
                          const prompt = `Revise this on-brand copy further. Brand rules:\n${rules}\n\nCurrent: "${rewritten}"\nUser wants: "${msg}"\n\nReturn JSON only: {"rewritten":"..."}`;
                          const reply = await window.CV_AI.complete(prompt);
                          let parsed = null;
                          try { parsed = JSON.parse(reply); }
                          catch { const m = String(reply).match(/\{[\s\S]*\}/); if (m) { try { parsed = JSON.parse(m[0]); } catch {} } }
                          if (parsed?.rewritten) setRewritten(parsed.rewritten);
                          else window.dsaToast?.('No usable revision — kept the previous');
                        } catch { window.dsaToast?.('Revision failed'); }
                        finally { setRewriting(false); }
                      }}
                    />
                  </div>
                  {rewriteIssues.length > 0 && (
                    <div style={{marginTop:14,paddingTop:12,borderTop:'1px solid rgba(31,26,18,.08)'}}>
                      <div style={{font:'600 11px/1 var(--font-body)',color:'var(--fg-muted)',letterSpacing:'0.06em',textTransform:'uppercase',marginBottom:8}}>Rules the original broke · {rewriteIssues.length}</div>
                      <div style={{display:'flex',flexDirection:'column',gap:6}}>
                        {rewriteIssues.map((v, i) => {
                          const rule = VOICE_RULES.find(r => r.id === v.rule);
                          return (
                            <div key={i} style={{font:'500 12px/1.4 var(--font-body)',color:'var(--fg-primary)'}}>
                              <b style={{color:'var(--status-error)'}}>×</b> {rule?.title || v.rule}
                              {v.note && <span style={{color:'var(--fg-secondary)'}}> — {v.note}</span>}
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div style={{font:'400 13px/1.55 var(--font-body)',color:'var(--fg-muted)'}}>The rewritten version will appear here, with a list of which voice rules the original broke.</div>
              )}
            </div>
          </div>
        </div>

        {/* Tone variants generator */}
        <div className="dsa-section">
          <div className="dsa-section-head">
            <h3 className="dsa-section-title">Generate tone variants for a context</h3>
            <span className="dsa-section-meta">Pick a context, describe what you need to say, get three on-brand variants</span>
          </div>
          <div className="dsa-panel">
            <div style={{display:'flex',gap:6,flexWrap:'wrap',marginBottom:14}}>
              {TONE_CONTEXTS.map(t => (
                <button key={t.id}
                  style={{
                    background: toneCtx === t.id ? 'var(--accent-gold)' : 'transparent',
                    color: toneCtx === t.id ? 'var(--fg-primary)' : 'var(--fg-secondary)',
                    border: '1px solid ' + (toneCtx === t.id ? 'var(--accent-gold)' : 'var(--border-default)'),
                    borderRadius: 999, padding: '6px 14px',
                    font: '500 12px/1 var(--font-body)', cursor: 'pointer',
                  }}
                  onClick={() => setToneCtx(t.id)}>{t.label}</button>
              ))}
            </div>
            <textarea
              style={{
                width:'100%', border:'1.5px solid var(--accent-gold)', borderRadius:'var(--r-md)',
                padding:'10px 12px', background:'var(--bg-canvas)', outline:'none',
                font:'400 13px/1.55 var(--font-body)', color:'var(--fg-primary)',
                resize:'vertical', minHeight:60, fontFamily:'var(--font-body)',
                boxSizing:'border-box',
              }}
              rows="2"
              placeholder="Brief: what does the message need to say?"
              value={toneBrief} onChange={e => setToneBrief(e.target.value)}
            />
            <div style={{display:'flex',alignItems:'center',gap:10,marginTop:10}}>
              <button className="dsa-btn dsa-btn--ai" onClick={generateTone} disabled={toneGenerating || !toneBrief.trim()}>
                <ViShape size={14}/> {toneGenerating ? 'Generating…' : 'Generate 3 variants'}
              </button>
              <span style={{font:'400 11px/1.4 var(--font-body)',color:'var(--fg-muted)'}}>
                Example for {TONE_CONTEXTS.find(t=>t.id===toneCtx)?.label}: <i>"{TONE_CONTEXTS.find(t=>t.id===toneCtx)?.example}"</i>
              </span>
            </div>
            {toneResults.length > 0 && (
              <div style={{display:'grid',gridTemplateColumns:'repeat(3, 1fr)',gap:10,marginTop:14}}>
                {toneResults.map((v, i) => (
                  <div key={i} style={{
                    background:'var(--bg-surface)', borderRadius:'var(--r-md)',
                    padding:'14px 14px 12px', position:'relative',
                    border:'1.5px solid var(--accent-gold)',
                  }}>
                    <div style={{font:'600 10px/1 var(--font-body)',color:'var(--accent-bronze)',letterSpacing:'0.08em',textTransform:'uppercase',marginBottom:8}}>Variant {i+1}</div>
                    <div style={{font:'400 13px/1.55 var(--font-body)',color:'var(--fg-primary)',marginBottom:8}}>{v}</div>
                    <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => copy(v)}>Copy</button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* The rules themselves */}
        <div style={{display:'none'}}>
          <div style={{display:'grid',gridTemplateColumns:'1fr',gap:8}}>
            {VOICE_RULES.map(r => (
              <div key={r.id} className="dsa-card">
                <div style={{display:'grid',gridTemplateColumns:'1fr auto auto',gap:14,alignItems:'start'}}>
                  <div>
                    <h4 style={{font:'700 14px/1.2 var(--font-display)',color:'var(--fg-primary)',margin:'0 0 4px'}}>{r.title}</h4>
                    <p style={{font:'400 13px/1.55 var(--font-body)',color:'var(--fg-secondary)',margin:0}}>{r.desc}</p>
                  </div>
                  <div style={{
                    background:'var(--status-error-bg)', borderRadius:'var(--r-sm)',
                    padding:'8px 12px', minWidth: 220, maxWidth: 280,
                    font:'400 12px/1.45 var(--font-body)', color:'var(--fg-primary)',
                  }}>
                    <div style={{font:'700 10px/1 var(--font-body)',color:'var(--status-error)',letterSpacing:'0.08em',textTransform:'uppercase',marginBottom:4}}>Avoid</div>
                    <span dangerouslySetInnerHTML={{__html: r.bad}}/>
                  </div>
                  <div style={{
                    background:'var(--status-success-bg)', borderRadius:'var(--r-sm)',
                    padding:'8px 12px', minWidth: 220, maxWidth: 280,
                    font:'400 12px/1.45 var(--font-body)', color:'var(--fg-primary)',
                  }}>
                    <div style={{font:'700 10px/1 var(--font-body)',color:'var(--status-success)',letterSpacing:'0.08em',textTransform:'uppercase',marginBottom:4}}>Use</div>
                    <span dangerouslySetInnerHTML={{__html: r.good}}/>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Voice rules — with per-rule audit */}
        <div className="dsa-section">
          <div className="dsa-section-head">
            <h3 className="dsa-section-title">Voice rules · {VOICE_RULES.length}</h3>
            <span className="dsa-section-meta">Click <b>Audit</b> on any rule to find probable violations across your system</span>
          </div>
          <div style={{display:'grid',gridTemplateColumns:'1fr',gap:8}}>
            {VOICE_RULES.map(r => {
              const findings = ruleAudits[r.id];
              const isBusy = auditingRule === r.id;
              return (
                <div key={r.id} className="dsa-card">
                  <div style={{display:'grid',gridTemplateColumns:'1fr auto auto',gap:14,alignItems:'start'}}>
                    <div>
                      <div style={{display:'flex',alignItems:'baseline',gap:8,marginBottom:4}}>
                        <h4 style={{font:'700 14px/1.2 var(--font-display)',color:'var(--fg-primary)',margin:0}}>{r.title}</h4>
                        {findings && <span style={{font:'600 10px/1 var(--font-body)',color:'var(--status-error)',background:'var(--status-error-bg)',padding:'3px 6px',borderRadius:3,letterSpacing:'0.04em',textTransform:'uppercase'}}>{findings.length} found</span>}
                        <button
                          className="dsa-btn dsa-btn--ai dsa-btn--sm"
                          style={{marginLeft:'auto'}}
                          onClick={() => auditRule(r)}
                          disabled={isBusy}
                        >
                          <ViShape size={11} animated={isBusy}/> {isBusy ? 'Auditing…' : findings ? 'Re-audit' : 'Audit system'}
                        </button>
                      </div>
                      <p style={{font:'400 13px/1.55 var(--font-body)',color:'var(--fg-secondary)',margin:0}}>{r.desc}</p>
                    </div>
                    <div style={{
                      background:'var(--status-error-bg)', borderRadius:'var(--r-sm)',
                      padding:'8px 12px', minWidth: 220, maxWidth: 280,
                      font:'400 12px/1.45 var(--font-body)', color:'var(--fg-primary)',
                    }}>
                      <div style={{font:'700 10px/1 var(--font-body)',color:'var(--status-error)',letterSpacing:'0.08em',textTransform:'uppercase',marginBottom:4}}>Avoid</div>
                      <span dangerouslySetInnerHTML={{__html: r.bad}}/>
                    </div>
                    <div style={{
                      background:'var(--status-success-bg)', borderRadius:'var(--r-sm)',
                      padding:'8px 12px', minWidth: 220, maxWidth: 280,
                      font:'400 12px/1.45 var(--font-body)', color:'var(--fg-primary)',
                    }}>
                      <div style={{font:'700 10px/1 var(--font-body)',color:'var(--status-success)',letterSpacing:'0.08em',textTransform:'uppercase',marginBottom:4}}>Use</div>
                      <span dangerouslySetInnerHTML={{__html: r.good}}/>
                    </div>
                  </div>
                  {findings && findings.length > 0 && (
                    <div style={{marginTop:14,paddingTop:14,borderTop:'1px solid var(--border-faint)'}}>
                      <div style={{font:'600 10px/1 var(--font-body)',color:'var(--fg-muted)',letterSpacing:'0.08em',textTransform:'uppercase',marginBottom:10}}>Likely violations in your system</div>
                      <div style={{display:'flex',flexDirection:'column',gap:8}}>
                        {findings.map((f, i) => (
                          <div key={i} style={{display:'grid',gridTemplateColumns:'140px 1fr 1fr',gap:10,alignItems:'start'}}>
                            <span style={{font:'500 11px/1.4 var(--font-mono)',color:'var(--accent-bronze)'}}>{f.location}</span>
                            <span style={{font:'400 12px/1.4 var(--font-body)',color:'var(--fg-primary)',background:'var(--status-error-bg)',padding:'6px 8px',borderRadius:'var(--r-sm)'}}>×&nbsp; {f.violation}</span>
                            <span style={{font:'400 12px/1.4 var(--font-body)',color:'var(--fg-primary)',background:'var(--status-success-bg)',padding:'6px 8px',borderRadius:'var(--r-sm)',display:'flex',alignItems:'flex-start',gap:6}}>
                              <span>✓&nbsp;</span><span style={{flex:1}}>{f.fix}</span>
                              <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" style={{padding:'2px 6px',marginLeft:'auto'}} onClick={() => copy(f.fix)}>copy</button>
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Saved rewrites library */}
        {savedRewrites && savedRewrites.length > 0 && (
          <div className="dsa-section">
            <div className="dsa-section-head">
              <h3 className="dsa-section-title">Saved rewrites · {savedRewrites.length}</h3>
              <span className="dsa-section-meta">Your reusable on-brand copy. Click any line to copy.</span>
            </div>
            <div style={{display:'flex',flexDirection:'column',gap:8}}>
              {savedRewrites.map(rw => (
                <div key={rw.id} className="dsa-card" style={{padding:14}}>
                  <div style={{display:'grid',gridTemplateColumns:'1fr 1fr auto',gap:12,alignItems:'flex-start'}}>
                    <div>
                      <div style={{font:'600 10px/1 var(--font-body)',color:'var(--fg-muted)',letterSpacing:'0.08em',textTransform:'uppercase',marginBottom:6}}>Before · {rw.savedAt}</div>
                      <div style={{font:'400 12px/1.5 var(--font-body)',color:'var(--fg-muted)',whiteSpace:'pre-wrap'}}>{rw.original}</div>
                    </div>
                    <div onClick={() => copy(rw.rewritten)} style={{cursor:'pointer'}}>
                      <div style={{font:'600 10px/1 var(--font-body)',color:'var(--accent-bronze)',letterSpacing:'0.08em',textTransform:'uppercase',marginBottom:6}}>On-brand</div>
                      <div style={{font:'400 13px/1.5 var(--font-body)',color:'var(--fg-primary)',whiteSpace:'pre-wrap'}}>{rw.rewritten}</div>
                    </div>
                    <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => removeSavedRewrite?.(rw.id)}>×</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Vocabulary */}
        <div className="dsa-section">
          <div className="dsa-section-head">
            <h3 className="dsa-section-title">Vocabulary anchors · {VOCAB.length}</h3>
            <span className="dsa-section-meta">Terms the brand owns — use them consistently</span>
          </div>
          <div style={{display:'grid',gridTemplateColumns:'repeat(2, 1fr)',gap:8}}>
            {VOCAB.map(v => (
              <div key={v.term} className="dsa-card">
                <div style={{font:'700 14px/1.2 var(--font-display)',color:'var(--accent-bronze)',marginBottom:4}}>{v.term}</div>
                <div style={{font:'400 12px/1.5 var(--font-body)',color:'var(--fg-secondary)'}}>{v.meaning}</div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </>
  );
}

window.Voice = Voice;
