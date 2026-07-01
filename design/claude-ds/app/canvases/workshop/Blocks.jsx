// canvases/workshop/Blocks.jsx — block renderers
// Every block knows how to render itself given its data; inline-editable text uses contentEditable.

const { useRef: useRef_b } = React;

// Editable text — debounced commits on blur. On focus also activates the
// global per-field Vi regen toolbar so the user can click ⤧ to swap the field
// for a Vi-generated alternative.
function Edit({ value, onChange, className, style, tag = 'span', placeholder, field }) {
  const ref = useRef_b(null);
  const Tag = tag;
  // Subscribe to workspace vars so {{key}} substitutions live-update
  const wsVars = (typeof window !== 'undefined' && window.useWSVars) ? window.useWSVars() : [];
  function activate() {
    const el = ref.current;
    if (!el || !window.WS_FIELD) return;
    const rect = el.getBoundingClientRect();
    const sectionEl = el.closest('[data-section-id]');
    const blockKind = sectionEl?.getAttribute('data-block-kind');
    const sectionId = sectionEl?.getAttribute('data-section-id');
    window.WS_FIELD.activate({
      rect,
      value,
      blockKind,
      sectionId,
      fieldName: field || guessFieldName(el),
      onApply: (next) => onChange(next),
    });
  }
  return (
    <Tag
      ref={ref}
      className={`ws-editable ${className || ''}`}
      style={style}
      contentEditable
      suppressContentEditableWarning
      data-ws-field={field || ''}
      onFocus={activate}
      onMouseUp={activate}
      onKeyUp={activate}
      onBlur={(e) => {
        const next = e.currentTarget.textContent;
        if (next !== value) onChange(next);
        // delay deactivate so toolbar clicks land first
        setTimeout(() => {
          // only deactivate if focus left to something other than the toolbar
          const ae = document.activeElement;
          if (!ae?.closest?.('.ws-field-tools')) window.WS_FIELD?.deactivate();
        }, 150);
      }}
      dangerouslySetInnerHTML={{ __html: (window.substituteVars ? window.substituteVars(value, wsVars) : value) || placeholder || '' }}
    />
  );
}

function guessFieldName(el) {
  // Inspect the className for hints like ws-blk-headline, ws-blk-eyebrow, etc.
  const cl = el.className || '';
  const m = cl.match(/ws-blk-([a-z-]+)/i);
  return m ? m[1] : '';
}

// ============================================================
// Block library — keys match data.kind values
// ============================================================
window.WS_BLOCKS = {
  hero: {
    label: 'Hero',
    icon: 'image',
    defaults: { eyebrow: 'Eyebrow', headline: 'Lead with a strong statement', body: 'Short supporting paragraph that builds on the headline.', cta: 'Learn more' },
    render: (data, set) => (
      <div className="ws-blk-hero">
        <div className="ws-blk-hero-text">
          <div className="ws-blk-eyebrow"><Edit value={data.eyebrow} onChange={v => set({...data, eyebrow: v})}/></div>
          <h1><Edit value={data.headline} onChange={v => set({...data, headline: v})}/></h1>
          <p><Edit value={data.body} onChange={v => set({...data, body: v})}/></p>
          {data.cta && (
            <button className="ws-blk-button">
              <Edit value={data.cta} onChange={v => set({...data, cta: v})}/>
              <span>→</span>
            </button>
          )}
        </div>
        <div className="ws-blk-hero-img">{data.imageLabel || 'Hero image'}</div>
      </div>
    ),
  },
  headline: {
    label: 'Headline',
    icon: 'edit',
    defaults: { eyebrow: '', text: 'The mathematics of operation.' },
    render: (data, set) => (
      <div>
        {data.eyebrow && <div className="ws-blk-eyebrow"><Edit value={data.eyebrow} onChange={v => set({...data, eyebrow: v})}/></div>}
        <h1 className="ws-blk-headline"><Edit value={data.text} onChange={v => set({...data, text: v})}/></h1>
      </div>
    ),
  },
  body: {
    label: 'Body text',
    icon: 'document',
    defaults: { text: 'Body text goes here. Click to edit. ConceptV builds tools for stakeholder-rich projects.' },
    render: (data, set) => (
      <p className="ws-blk-body"><Edit value={data.text} onChange={v => set({...data, text: v})}/></p>
    ),
  },
  quote: {
    label: 'Quote',
    icon: 'chat',
    defaults: { text: 'Universal Mechanics turned a six-month process into a six-week one.', who: 'Project Director, multi-stakeholder build' },
    render: (data, set) => (
      <blockquote className="ws-blk-quote">
        "<Edit value={data.text} onChange={v => set({...data, text: v})}/>"
        <span className="who"><Edit value={data.who} onChange={v => set({...data, who: v})}/></span>
      </blockquote>
    ),
  },
  icons: {
    label: 'Tag row',
    icon: 'star',
    defaults: { items: [{icon:'house',label:'Properties'},{icon:'people',label:'Stakeholders'},{icon:'network',label:'Engine'},{icon:'browser',label:'Outputs'}] },
    render: (data, set) => (
      <div className="ws-blk-icons">
        {(data.items || []).map((it, i) => (
          <div className="tag" key={i}>
            <span className="ic">
              {window.CV_ICONS?.data[it.icon] ? (
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" dangerouslySetInnerHTML={{__html: window.CV_ICONS.data[it.icon]}}/>
              ) : '?'}
            </span>
            <span className="lbl"><Edit value={it.label} onChange={v => {
              const next = [...data.items]; next[i] = {...it, label: v};
              set({...data, items: next});
            }}/></span>
          </div>
        ))}
      </div>
    ),
  },
  stats: {
    label: 'Stat grid',
    icon: 'pie-chart',
    defaults: { items: [{v:'10×',l:'Faster turnaround'},{v:'80%',l:'Less revision'},{v:'5+',l:'Stakeholder types'},{v:'24/7',l:'Real-time updates'}] },
    render: (data, set) => (
      <div className="ws-blk-stats">
        {(data.items || []).map((it, i) => (
          <div className="ws-blk-stat" key={i}>
            <div className="v"><Edit value={it.v} onChange={v => { const n = [...data.items]; n[i] = {...it,v}; set({...data, items: n}); }}/></div>
            <div className="l"><Edit value={it.l} onChange={v => { const n = [...data.items]; n[i] = {...it,l:v}; set({...data, items: n}); }}/></div>
          </div>
        ))}
      </div>
    ),
  },
  palette: {
    label: 'Palette strip',
    icon: 'color-swatches',
    defaults: { colors: [{n:'gold',h:'#E0C010'},{n:'bronze',h:'#988058'},{n:'ink',h:'#1F1A12'},{n:'canvas',h:'#FBF7EC'}] },
    render: (data) => (
      <div className="ws-blk-palette">
        {(data.colors || []).map((c, i) => (
          <div className="sw" key={i} style={{background:c.h}}>
            <span className="h" style={{color: isLight(c.h) ? '#1F1A12' : '#FBF7EC'}}>{c.h}</span>
          </div>
        ))}
      </div>
    ),
  },
  button: {
    label: 'Button',
    icon: 'tag',
    defaults: { text: 'Get started' },
    render: (data, set) => (
      <div><button className="ws-blk-button"><Edit value={data.text} onChange={v => set({...data, text: v})}/></button></div>
    ),
  },
  callout: {
    label: 'Callout',
    icon: 'lightbulb',
    defaults: { label: 'Why now', text: 'Universal Mechanics shipped this year as a stable engine — your projects can build on it.' },
    render: (data, set) => (
      <div className="ws-blk-callout">
        <span className="lbl"><Edit value={data.label} onChange={v => set({...data, label: v})}/></span>
        <Edit value={data.text} onChange={v => set({...data, text: v})}/>
      </div>
    ),
  },
  image: {
    label: 'Image slot',
    icon: 'image-stack',
    defaults: { label: 'Image placeholder' },
    render: (data, set) => (
      <div className="ws-blk-image"><Edit value={data.label} onChange={v => set({...data, label: v})}/></div>
    ),
  },
  divider: {
    label: 'Divider',
    icon: 'minus',
    defaults: {},
    render: () => <div className="ws-blk-divider"/>,
  },
  process: {
    label: 'Process flow',
    icon: 'path-flow',
    defaults: { steps: [
      { stage: 'Stage 1', title: 'Placeholders', body: 'Basic visual quality.' },
      { stage: 'Stage 2', title: 'Some elements defined', body: 'Improved visual quality.' },
      { stage: 'Stage 3', title: 'Final output', body: 'High level of detail.' },
    ] },
    render: (data, set) => (
      <div className="ws-blk-process">
        {(data.steps || []).map((st, i) => (
          <React.Fragment key={i}>
            <div className="ws-blk-process-step">
              <div className="stage">
                <Edit value={st.stage} onChange={v => { const n = [...data.steps]; n[i] = {...st, stage: v}; set({...data, steps: n}); }}/>
              </div>
              <div className="title">
                <Edit value={st.title} onChange={v => { const n = [...data.steps]; n[i] = {...st, title: v}; set({...data, steps: n}); }}/>
              </div>
              <div className="body">
                <Edit value={st.body} onChange={v => { const n = [...data.steps]; n[i] = {...st, body: v}; set({...data, steps: n}); }}/>
              </div>
            </div>
            {i < (data.steps || []).length - 1 && (
              <div className="ws-blk-process-arrow" aria-hidden="true">
                <svg viewBox="0 0 40 12" preserveAspectRatio="none">
                  <line x1="0" y1="6" x2="30" y2="6" stroke="currentColor" strokeWidth="1.5" strokeDasharray="3 3"/>
                  <polygon points="28,1 38,6 28,11" fill="currentColor"/>
                </svg>
              </div>
            )}
          </React.Fragment>
        ))}
      </div>
    ),
  },
  imageGrid: {
    label: 'Image grid',
    icon: 'image-stack',
    defaults: { items: [
      { label: 'Aerial' }, { label: 'Interior' }, { label: 'Detail' },
    ] },
    render: (data, set) => (
      <div className="ws-blk-imagegrid">
        {(data.items || []).map((it, i) => (
          <div className="cell" key={i}>
            <div className="ph"><Edit value={it.label} onChange={v => { const n = [...data.items]; n[i] = {...it, label: v}; set({...data, items: n}); }}/></div>
          </div>
        ))}
      </div>
    ),
  },
  featureCards: {
    label: 'Feature cards',
    icon: 'pie-chart',
    defaults: { items: [
      { title: 'Top drivers',  stat: '70%', body: 'Achieving greater accuracy and trustworthiness.' },
      { title: 'Top barriers', stat: '67%', body: 'High cost of software and licenses.' },
      { title: 'Why fail',     stat: '36%', body: 'Poor fit with current practices.' },
    ] },
    render: (data, set) => (
      <div className="ws-blk-features">
        {(data.items || []).map((it, i) => (
          <div className="ws-blk-feature" key={i}>
            <h4 className="title"><Edit value={it.title} onChange={v => { const n = [...data.items]; n[i] = {...it, title: v}; set({...data, items: n}); }}/></h4>
            <div className="stat"><Edit value={it.stat} onChange={v => { const n = [...data.items]; n[i] = {...it, stat: v}; set({...data, items: n}); }}/></div>
            <p className="body"><Edit value={it.body} onChange={v => { const n = [...data.items]; n[i] = {...it, body: v}; set({...data, items: n}); }}/></p>
          </div>
        ))}
      </div>
    ),
  },
  funnel: {
    label: 'Funnel',
    icon: 'path-flow',
    defaults: { steps: [
      { top: 'Research',  label: 'Networks',    bot: 'Referrals',   shape: 'card' },
      { top: 'Architects', label: 'Developers', bot: 'Designers',   shape: 'card' },
      { top: '',           label: 'Virtual Hubs', bot: '',          shape: 'hex'  },
      { top: 'Onsellers',  label: 'Repeat sales', bot: 'Subscribers', shape: 'card' },
      { top: '',           label: 'Organic awareness', bot: '',     shape: 'circle' },
    ], cycle: '3 to 6 months' },
    render: (data, set) => (
      <div className="ws-blk-funnel">
        <div className="ws-blk-funnel-row">
          {(data.steps || []).map((st, i) => (
            <React.Fragment key={i}>
              <div className={`ws-blk-funnel-step shape-${st.shape || 'card'}`}>
                {st.top && (
                  <div className="feeder feeder-top">
                    <span className="chev">⌃⌃</span>
                    <Edit value={st.top} onChange={v => { const n = [...data.steps]; n[i] = {...st, top: v}; set({...data, steps: n}); }}/>
                  </div>
                )}
                <div className="core">
                  <Edit value={st.label} onChange={v => { const n = [...data.steps]; n[i] = {...st, label: v}; set({...data, steps: n}); }}/>
                </div>
                {st.bot && (
                  <div className="feeder feeder-bot">
                    <Edit value={st.bot} onChange={v => { const n = [...data.steps]; n[i] = {...st, bot: v}; set({...data, steps: n}); }}/>
                    <span className="chev">⌄⌄</span>
                  </div>
                )}
              </div>
              {i < (data.steps || []).length - 1 && (
                <div className="ws-blk-funnel-arrow" aria-hidden="true">
                  <svg viewBox="0 0 40 14" preserveAspectRatio="none">
                    <line x1="0" y1="7" x2="30" y2="7" stroke="currentColor" strokeWidth="1.8"/>
                    <polygon points="28,2 38,7 28,12" fill="currentColor"/>
                  </svg>
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
        {data.cycle && (
          <div className="ws-blk-funnel-cycle">
            <span className="cycle-arrow" aria-hidden="true">↻</span>
            <Edit value={data.cycle} onChange={v => set({...data, cycle: v})}/>
          </div>
        )}
      </div>
    ),
  },
  tagCluster: {
    label: 'Tag cluster',
    icon: 'network',
    defaults: {
      hub: 'Project master info',
      hubIcon: 'database',
      branches: [
        { side: 'left', items: [
          { icon: 'tag',     label: 'Brand Kit' },
          { icon: 'document', label: 'Files' },
        ] },
        { side: 'right', items: [
          { icon: 'link',  label: 'Hub Link' },
          { icon: 'image', label: 'Gallery Assets' },
          { icon: 'edit',  label: 'Project Description' },
        ] },
      ],
    },
    render: (data, set) => (
      <div className="ws-blk-cluster">
        <div className="branch-col left">
          {(data.branches?.[0]?.items || []).map((it, i) => (
            <div className="cluster-tag" key={i}>
              <span className="ic">
                {window.CV_ICONS?.data[it.icon] ? (
                  <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" dangerouslySetInnerHTML={{__html: window.CV_ICONS.data[it.icon]}}/>
                ) : '·'}
              </span>
              <Edit value={it.label} onChange={v => {
                const next = [...(data.branches?.[0]?.items || [])]; next[i] = {...it, label: v};
                const branches = [...(data.branches || [])]; branches[0] = {...(branches[0] || {}), items: next};
                set({...data, branches});
              }}/>
            </div>
          ))}
        </div>
        <div className="hub">
          <span className="ic">
            {window.CV_ICONS?.data[data.hubIcon] ? (
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" dangerouslySetInnerHTML={{__html: window.CV_ICONS.data[data.hubIcon]}}/>
            ) : null}
          </span>
          <Edit value={data.hub} onChange={v => set({...data, hub: v})}/>
        </div>
        <div className="branch-col right">
          {(data.branches?.[1]?.items || []).map((it, i) => (
            <div className="cluster-tag" key={i}>
              <span className="ic">
                {window.CV_ICONS?.data[it.icon] ? (
                  <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" dangerouslySetInnerHTML={{__html: window.CV_ICONS.data[it.icon]}}/>
                ) : '·'}
              </span>
              <Edit value={it.label} onChange={v => {
                const next = [...(data.branches?.[1]?.items || [])]; next[i] = {...it, label: v};
                const branches = [...(data.branches || [])]; branches[1] = {...(branches[1] || {}), items: next};
                set({...data, branches});
              }}/>
            </div>
          ))}
        </div>
      </div>
    ),
  },
  pullquote: {
    label: 'Pull quote',
    icon: 'chat-double',
    defaults: {
      lead: 'Universal Mechanics turned a six-month process into a six-week one.',
      who: 'Project Director · multi-stakeholder build',
    },
    render: (data, set) => (
      <div className="ws-blk-pullquote">
        <span className="mark" aria-hidden="true">"</span>
        <div className="lead"><Edit value={data.lead} onChange={v => set({...data, lead: v})}/></div>
        <div className="who"><Edit value={data.who} onChange={v => set({...data, who: v})}/></div>
      </div>
    ),
  },
  metricRow: {
    label: 'Metric row',
    icon: 'pie-chart',
    defaults: { items: [
      { v: '5+',  l: 'stakeholder types' },
      { v: '10×', l: 'faster sign-off' },
      { v: '80%', l: 'less rework' },
      { v: '24/7', l: 'real-time updates' },
    ] },
    render: (data, set) => (
      <div className="ws-blk-metric-row">
        {(data.items || []).map((it, i) => (
          <div className="m" key={i}>
            <div className="v"><Edit value={it.v} onChange={v => { const n = [...data.items]; n[i] = {...it, v}; set({...data, items: n}); }}/></div>
            <div className="l"><Edit value={it.l} onChange={v => { const n = [...data.items]; n[i] = {...it, l: v}; set({...data, items: n}); }}/></div>
          </div>
        ))}
      </div>
    ),
  },
  bullets: {
    label: 'Bullet list',
    icon: 'check',
    defaults: { items: [
      'Numerous stakeholders',
      'Information quality affects collaboration',
      'Persistent friction',
    ] },
    render: (data, set) => (
      <ul className="ws-blk-bullets">
        {(data.items || []).map((it, i) => (
          <li key={i}>
            <span className="marker" aria-hidden="true">▶</span>
            <Edit value={it} onChange={v => { const n = [...data.items]; n[i] = v; set({...data, items: n}); }}/>
          </li>
        ))}
      </ul>
    ),
  },
  iconStrip: {
    label: 'Icon strip',
    icon: 'star',
    defaults: { items: ['house','document','chat','files-stack','calendar','crane','dollar-circle','pie-chart'], arrow: true },
    render: (data, set) => (
      <div className="ws-blk-iconstrip">
        {data.arrow !== false && <span className="lead" aria-hidden="true">→</span>}
        {(data.items || []).map((name, i) => (
          <span className="ic" key={i}>
            {window.CV_ICONS?.data[name] ? (
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" dangerouslySetInnerHTML={{__html: window.CV_ICONS.data[name]}}/>
            ) : '?'}
          </span>
        ))}
      </div>
    ),
  },
  labeledCard: {
    label: 'Highlight card',
    icon: 'info-circle',
    defaults: {
      title: 'Consequences',
      lines: [
        { stat: '$430B+/year', body: 'in rework and' },
        { stat: '$1.4T',        body: 'in non-optimal labour' },
        { stat: '30%',          body: 'of global construction waste' },
        { stat: '9.4 hrs/wk',   body: 'wasted time for mid to high level professionals' },
      ],
    },
    render: (data, set) => (
      <div className="ws-blk-labeledcard">
        <h4 className="title">
          <Edit value={data.title} onChange={v => set({...data, title: v})}/>
        </h4>
        <div className="rows">
          {(data.lines || []).map((ln, i) => (
            <div className="row" key={i}>
              <span className="stat">
                <Edit value={ln.stat} onChange={v => { const n = [...data.lines]; n[i] = {...ln, stat: v}; set({...data, lines: n}); }}/>
              </span>
              <span className="body">
                <Edit value={ln.body} onChange={v => { const n = [...data.lines]; n[i] = {...ln, body: v}; set({...data, lines: n}); }}/>
              </span>
            </div>
          ))}
        </div>
      </div>
    ),
  },
  comparison: {
    label: 'Comparison',
    icon: 'swap',
    defaults: {
      left:  { title: '3D Environment',  caption: 'Versatile interfaces · info and collaboration tools', label: '3D mock' },
      right: { title: '2D Environment',  caption: '"Control panel" · project management tools',         label: '2D mock' },
    },
    render: (data, set) => (
      <div className="ws-blk-comparison">
        {['left','right'].map(side => (
          <div className={`col col-${side}`} key={side}>
            <h4 className="ct">
              <Edit value={data[side]?.title} onChange={v => set({...data, [side]: {...(data[side] || {}), title: v}})}/>
            </h4>
            <div className="ph"><Edit value={data[side]?.label} onChange={v => set({...data, [side]: {...(data[side] || {}), label: v}})}/></div>
            <p className="cap"><Edit value={data[side]?.caption} onChange={v => set({...data, [side]: {...(data[side] || {}), caption: v}})}/></p>
          </div>
        ))}
      </div>
    ),
  },
  hexBadge: {
    label: 'Hex badge',
    icon: 'tag',
    defaults: {
      items: [
        { label: 'Property\nWizard', version: 'v9.0' },
        { label: 'Vi',               version: 'v3.0' },
      ],
    },
    render: (data, set) => (
      <div className="ws-blk-hexbadges">
        {(data.items || []).map((it, i) => (
          <div className="hexbadge" key={i}>
            <div className="shell">
              <svg viewBox="0 0 100 86" preserveAspectRatio="xMidYMid meet" aria-hidden="true">
                <polygon points="25,2 75,2 98,43 75,84 25,84 2,43" fill="var(--bg-surface)" stroke="var(--accent-gold)" strokeWidth="2"/>
              </svg>
              <span className="ic" aria-hidden="true">
                <svg viewBox="0 0 32 32" width="20" height="20">
                  <path d="M8 11 L16 22 L24 11" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </span>
              <div className="lbl">
                <Edit value={it.label} onChange={v => { const n = [...data.items]; n[i] = {...it, label: v}; set({...data, items: n}); }}/>
              </div>
            </div>
            {it.version && (
              <div className="ver">
                <Edit value={it.version} onChange={v => { const n = [...data.items]; n[i] = {...it, version: v}; set({...data, items: n}); }}/>
              </div>
            )}
          </div>
        ))}
      </div>
    ),
  },
  chipRow: {
    label: 'Capability chips',
    icon: 'tag',
    defaults: {
      lead: 'browser-house',
      items: ['Agnostic', 'Accessible', 'Intuitive', 'Seamless', 'Universal'],
    },
    render: (data, set) => (
      <div className="ws-blk-chiprow">
        <div className="lead">
          <span className="seal">
            {window.CV_ICONS?.data[data.lead] ? (
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" dangerouslySetInnerHTML={{__html: window.CV_ICONS.data[data.lead]}}/>
            ) : null}
          </span>
          <span className="arr" aria-hidden="true">▶</span>
        </div>
        <div className="chips">
          {(data.items || []).map((it, i) => (
            <span className="chip" key={i}>
              <Edit value={it} onChange={v => { const n = [...data.items]; n[i] = v; set({...data, items: n}); }}/>
            </span>
          ))}
        </div>
      </div>
    ),
  },
  statPills: {
    label: 'Stat pills',
    icon: 'pie-chart',
    defaults: {
      items: [
        { v: '6 Years',  l: 'Research & Development' },
        { v: '$1.5M+',   l: 'Spent on IP' },
      ],
    },
    render: (data, set) => (
      <div className="ws-blk-statpills">
        {(data.items || []).map((it, i) => (
          <div className="pill" key={i}>
            <span className="v">
              <Edit value={it.v} onChange={v => { const n = [...data.items]; n[i] = {...it, v}; set({...data, items: n}); }}/>
            </span>
            <span className="l">
              <Edit value={it.l} onChange={v => { const n = [...data.items]; n[i] = {...it, l: v}; set({...data, items: n}); }}/>
            </span>
          </div>
        ))}
      </div>
    ),
  },
  statTable: {
    label: 'Stat table',
    icon: 'pie-chart',
    defaults: {
      title: 'Capped Cash Out Option in 12 months',
      hero: { v: '$500M', l: 'Target valuation at exit event' },
      rows: [
        { v: '91x',     l: 'Multiple from investing this round' },
        { v: '5 Years', l: 'Exit event goal' },
        { v: '$6.5M',   l: 'Buy-back valuation in 12 months' },
        { v: '18.2%',   l: 'ROI on optional buy-back' },
        { v: '2 Years', l: 'Intended Series A raise' },
        { v: '$50M',    l: 'Target valuation at Series A' },
        { v: '$5M',     l: 'Planned Series A raise amount' },
      ],
    },
    render: (data, set) => (
      <div className="ws-blk-stattable">
        {data.title && (
          <h4 className="title">
            <Edit value={data.title} onChange={v => set({...data, title: v})}/>
          </h4>
        )}
        {data.hero && (
          <div className="hero">
            <span className="pill">
              <Edit value={data.hero.v} onChange={v => set({...data, hero: {...data.hero, v}})}/>
            </span>
            <span className="hero-l">
              <Edit value={data.hero.l} onChange={v => set({...data, hero: {...data.hero, l: v}})}/>
            </span>
          </div>
        )}
        <div className="rows">
          {(data.rows || []).map((r, i) => (
            <div className="row" key={i}>
              <span className="v">
                <Edit value={r.v} onChange={v => { const n = [...data.rows]; n[i] = {...r, v}; set({...data, rows: n}); }}/>
              </span>
              <span className="l">
                <Edit value={r.l} onChange={v => { const n = [...data.rows]; n[i] = {...r, l: v}; set({...data, rows: n}); }}/>
              </span>
            </div>
          ))}
        </div>
      </div>
    ),
  },
  checklist: {
    label: 'Checklist',
    icon: 'check-square',
    defaults: {
      title: 'Milestones',
      items: [
        'Functioning Vi prototype',
        'Market demand',
        '$350k in credits from Google, AWS and Oracle',
        'Key industry support',
        'Industry investment and $400k annual contract',
      ],
    },
    render: (data, set) => (
      <div className="ws-blk-checklist">
        {data.title && (
          <h4 className="title">
            <Edit value={data.title} onChange={v => set({...data, title: v})}/>
          </h4>
        )}
        <ul>
          {(data.items || []).map((it, i) => (
            <li key={i}>
              <span className="tick" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="3" width="18" height="18" rx="3" fill="var(--accent-gold)" stroke="var(--accent-gold)"/>
                  <path d="M7 12 L10.5 15.5 L17 8" stroke="var(--fg-primary)"/>
                </svg>
              </span>
              <Edit value={it} onChange={v => { const n = [...data.items]; n[i] = v; set({...data, items: n}); }}/>
            </li>
          ))}
        </ul>
      </div>
    ),
  },
  logoStrip: {
    label: 'Logo strip',
    icon: 'tag',
    defaults: {
      title: 'Development Partners and Incubator Programs',
      logos: ['NVIDIA · Inception', 'NVIDIA · Omniverse', 'AWS Activate', 'Google Cloud', 'Oracle for Startups'],
    },
    render: (data, set) => (
      <div className="ws-blk-logostrip">
        {data.title && (
          <h4 className="title">
            <Edit value={data.title} onChange={v => set({...data, title: v})}/>
          </h4>
        )}
        <div className="logos">
          {(data.logos || []).map((it, i) => (
            <div className="logo" key={i}>
              <Edit value={it} onChange={v => { const n = [...data.logos]; n[i] = v; set({...data, logos: n}); }}/>
            </div>
          ))}
        </div>
      </div>
    ),
  },
  bio: {
    label: 'Bio card',
    icon: 'people',
    defaults: {
      name: 'Grant Plummer',
      role: 'Director at Gap Development Sales',
      avatarInitials: 'GP',
      stats: [
        { v: '25+',  l: 'Years of experience' },
        { v: '120+', l: 'Developments in sales portfolio' },
        { v: '$3B+', l: 'Sales in residential property' },
      ],
    },
    render: (data, set) => (
      <div className="ws-blk-bio">
        <div className="who">
          <div className="avatar">
            <Edit value={data.avatarInitials} onChange={v => set({...data, avatarInitials: v})}/>
          </div>
          <div className="meta">
            <div className="name">
              <Edit value={data.name} onChange={v => set({...data, name: v})}/>
            </div>
            <div className="role">
              <Edit value={data.role} onChange={v => set({...data, role: v})}/>
            </div>
          </div>
        </div>
        <div className="stats">
          {(data.stats || []).map((s, i) => (
            <div className="row" key={i}>
              <span className="v">
                <Edit value={s.v} onChange={v => { const n = [...data.stats]; n[i] = {...s, v}; set({...data, stats: n}); }}/>
              </span>
              <span className="l">
                <Edit value={s.l} onChange={v => { const n = [...data.stats]; n[i] = {...s, l: v}; set({...data, stats: n}); }}/>
              </span>
            </div>
          ))}
        </div>
      </div>
    ),
  },
  pillars: {
    label: 'Pillars',
    icon: 'tag',
    defaults: {
      subtitle: 'The Pillars of Our Go-to-Market Strategy',
      items: [
        'Key Industry Figures',
        'Market Partnerships',
        'Organic Recognition',
        'Customer Base',
      ],
    },
    render: (data, set) => (
      <div className="ws-blk-pillars">
        {data.subtitle && (
          <h4 className="subtitle">
            <Edit value={data.subtitle} onChange={v => set({...data, subtitle: v})}/>
          </h4>
        )}
        <div className="row">
          {(data.items || []).map((it, i) => (
            <div className="pillar" key={i}>
              <Edit value={it} onChange={v => { const n = [...data.items]; n[i] = v; set({...data, items: n}); }}/>
            </div>
          ))}
        </div>
      </div>
    ),
  },
  photoBio: {
    label: 'Person card',
    icon: 'people',
    defaults: {
      items: [
        {
          initials: 'TS',
          name: 'Tamara Smith — Key Industry Figure',
          desc: 'National Manager of Partnerships and Strategic Engagement at the AIA',
        },
        {
          initials: 'GP',
          name: 'Grant Plummer — Upcoming Chief Sales Officer',
          desc: 'Director at Gap Development Sales and investor at ConceptV',
        },
      ],
    },
    render: (data, set) => (
      <div className="ws-blk-photobio">
        {(data.items || []).map((p, i) => (
          <div className="person" key={i}>
            <div className="avatar">
              <Edit value={p.initials} onChange={v => { const n = [...data.items]; n[i] = {...p, initials: v}; set({...data, items: n}); }}/>
            </div>
            <div className="meta">
              <div className="name">
                <Edit value={p.name} onChange={v => { const n = [...data.items]; n[i] = {...p, name: v}; set({...data, items: n}); }}/>
              </div>
              <div className="desc">
                <Edit value={p.desc} onChange={v => { const n = [...data.items]; n[i] = {...p, desc: v}; set({...data, items: n}); }}/>
              </div>
            </div>
          </div>
        ))}
      </div>
    ),
  },
  orgDiagram: {
    label: 'Org diagram',
    icon: 'network',
    defaults: {
      caption: 'The AI Framework powering our systems',
      hub: { label: 'Vi', shape: 'diamond' },
      nodes: [
        {
          label: 'User\nPortal', shape: 'circle',
          left:  [{ icon: 'dollar-circle', label: 'Order and contract' }],
          right: [{ icon: 'gear',          label: 'Manage updates' }],
          below: [{ icon: 'cloud',         label: 'Upload design files' }, { icon: 'gear', label: 'Configure Hubs' }],
        },
        {
          label: 'Property\nWizard', shape: 'hex',
          below: [{ icon: 'database',      label: 'Central database' }, { icon: 'network', label: 'Decision tree logic' }],
        },
        {
          label: 'Virtual\nHubs', shape: 'octagon',
          left:  [{ icon: 'people',        label: 'User-specific functions' }],
          right: [{ icon: 'info-circle',   label: 'Centralised information' }],
          below: [{ icon: 'chat',          label: 'Communication tools' }, { icon: 'edit', label: 'Annotation dashboard' }],
        },
      ],
    },
    render: (data, set) => (
      <div className="ws-blk-orgdiagram">
        {data.caption && (
          <div className="caption">
            <Edit value={data.caption} onChange={v => set({...data, caption: v})}/>
          </div>
        )}
        <div className="hub">
          <div className={`node-shell shape-${data.hub?.shape || 'diamond'} hub-node`}>
            <span className="lbl"><Edit value={data.hub?.label} onChange={v => set({...data, hub: {...data.hub, label: v}})}/></span>
          </div>
          <div className="hub-arrow" aria-hidden="true">
            <svg viewBox="0 0 8 24"><line x1="4" y1="0" x2="4" y2="18" stroke="currentColor" strokeWidth="1.5" strokeDasharray="3 3"/><polygon points="0,18 8,18 4,24" fill="currentColor"/></svg>
          </div>
        </div>
        <div className="branches">
          {(data.nodes || []).map((n, i) => (
            <div className="branch" key={i}>
              <div className="row top">
                <div className="side-col left">
                  {(n.left || []).map((it, j) => (
                    <div className="satellite" key={j}>
                      <span className="ic">
                        {window.CV_ICONS?.data[it.icon] ? <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" dangerouslySetInnerHTML={{__html: window.CV_ICONS.data[it.icon]}}/> : null}
                      </span>
                      <span className="lbl">
                        <Edit value={it.label} onChange={v => { const nn = [...data.nodes]; nn[i] = {...n, left: n.left.map((x, k) => k === j ? {...x, label: v} : x)}; set({...data, nodes: nn}); }}/>
                      </span>
                    </div>
                  ))}
                </div>
                <div className={`node-shell shape-${n.shape || 'circle'}`}>
                  <span className="lbl">
                    <Edit value={n.label} onChange={v => { const nn = [...data.nodes]; nn[i] = {...n, label: v}; set({...data, nodes: nn}); }}/>
                  </span>
                </div>
                <div className="side-col right">
                  {(n.right || []).map((it, j) => (
                    <div className="satellite" key={j}>
                      <span className="ic">
                        {window.CV_ICONS?.data[it.icon] ? <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" dangerouslySetInnerHTML={{__html: window.CV_ICONS.data[it.icon]}}/> : null}
                      </span>
                      <span className="lbl">
                        <Edit value={it.label} onChange={v => { const nn = [...data.nodes]; nn[i] = {...n, right: n.right.map((x, k) => k === j ? {...x, label: v} : x)}; set({...data, nodes: nn}); }}/>
                      </span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="below">
                {(n.below || []).map((it, j) => (
                  <div className="satellite below-sat" key={j}>
                    <span className="ic">
                      {window.CV_ICONS?.data[it.icon] ? <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" dangerouslySetInnerHTML={{__html: window.CV_ICONS.data[it.icon]}}/> : null}
                    </span>
                    <span className="lbl">
                      <Edit value={it.label} onChange={v => { const nn = [...data.nodes]; nn[i] = {...n, below: n.below.map((x, k) => k === j ? {...x, label: v} : x)}; set({...data, nodes: nn}); }}/>
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    ),
  },
  contactCard: {
    label: 'Contact card',
    icon: 'email',
    defaults: {
      brand: 'ConceptV',
      lines: [
        { label: 'Phone',     value: '0421 849 615' },
        { label: 'Email',     value: 't.geldard@conceptv.com.au' },
        { label: 'Website',   value: 'www.conceptv.com.au' },
        { label: 'Head Office', value: 'Level 1, 235 Boundary Street\nWest End, QLD 4101' },
      ],
    },
    render: (data, set) => (
      <div className="ws-blk-contactcard">
        <div className="brand">
          <Edit value={data.brand} onChange={v => set({...data, brand: v})}/>
        </div>
        <div className="lines">
          {(data.lines || []).map((ln, i) => (
            <div className="line" key={i}>
              <div className="label">
                <Edit value={ln.label} onChange={v => { const n = [...data.lines]; n[i] = {...ln, label: v}; set({...data, lines: n}); }}/>
              </div>
              <div className="value">
                <Edit value={ln.value} onChange={v => { const n = [...data.lines]; n[i] = {...ln, value: v}; set({...data, lines: n}); }}/>
              </div>
            </div>
          ))}
        </div>
      </div>
    ),
  },
  timeline: {
    label: 'Timeline',
    icon: 'calendar',
    defaults: {
      unit: 'Months',
      ticks: ['6', '12', '18', '24'],
      milestones: [
        { tick: 0, side: 'right', label: 'Marketing & Sales' },
        { tick: 1, side: 'right', label: 'Architecture & Design' },
        { tick: 1, side: 'right', label: 'Property Developers',  offset: 1 },
        { tick: 2, side: 'right', label: 'Commercial Fitouts' },
        { tick: 2, side: 'left',  label: 'Brands & Suppliers' },
        { tick: 2, side: 'right', label: 'Marketplace',          offset: 1 },
        { tick: 3, side: 'right', label: 'Volume Builders' },
        { tick: 3, side: 'right', label: 'Construction Suite',   offset: 1 },
        { tick: 3, side: 'left',  label: 'Kit Homes' },
      ],
    },
    render: (data, set) => {
      const total = (data.ticks || []).length;
      return (
        <div className="ws-blk-timeline">
          <div className="axis">
            <div className="axis-label">
              <Edit value={data.unit} onChange={v => set({...data, unit: v})}/>
            </div>
            <div className="track">
              {(data.ticks || []).map((t, i) => (
                <div className="tick" key={i}>
                  <span className="dot"/>
                  <span className="num">
                    <Edit value={t} onChange={v => { const n = [...data.ticks]; n[i] = v; set({...data, ticks: n}); }}/>
                  </span>
                </div>
              ))}
            </div>
          </div>
          <div className="lane">
            {(data.milestones || []).map((m, i) => {
              const top = ((m.tick + (m.offset || 0) * 0.45) / Math.max(1, total - 0.6)) * 100;
              return (
                <div
                  className={`milestone side-${m.side}`}
                  key={i}
                  style={{top: `${Math.min(98, top)}%`}}
                >
                  <span className="chip">
                    <Edit value={m.label} onChange={v => { const n = [...data.milestones]; n[i] = {...m, label: v}; set({...data, milestones: n}); }}/>
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      );
    },
  },

  // ============================================================
  // Cross-doc embed blocks — reference other Workshop docs
  // ============================================================
  embedWidget: {
    label: 'Widget (embed)',
    icon: 'check-square',
    defaults: { docId: '', cap: 'No widget selected' },
    render: (data, set) => <EmbedWidget data={data} set={set}/>,
  },
  embedWizard: {
    label: 'Wizard (preview)',
    icon: 'atom',
    defaults: { docId: '', cap: 'No wizard selected' },
    render: (data, set) => <EmbedWizard data={data} set={set}/>,
  },
};

function isLight(hex) {
  if (!hex || hex[0] !== '#') return false;
  const h = hex.length === 4 ? hex.slice(1).split('').map(c => c+c).join('') : hex.slice(1);
  const r = parseInt(h.slice(0,2),16), g = parseInt(h.slice(2,4),16), b = parseInt(h.slice(4,6),16);
  return (r*0.299 + g*0.587 + b*0.114) > 175;
}
window.isLight = isLight;

// ============================================================
// Reactive cross-doc embed components — subscribe to WS_DOCS so
// edits to the source widget/wizard appear here without a refresh.
// ============================================================
function EmbedWidget({ data, set }) {
  const docs = (window.useWSDocs ? window.useWSDocs() : null) || [];
  const widgets = docs.filter ? docs.filter(d => d.type === 'widget') : [];
  const target = widgets.find(d => d.id === data.docId);
  return (
    <div className="ws-blk-embed">
      {!target ? (
        <div className="ws-blk-embed-empty">
          <div className="lbl">Pick a Workshop widget to embed</div>
          {widgets.length === 0 && <div className="hint">No widgets in this workspace yet — build one first.</div>}
          {widgets.length > 0 && (
            <div className="picker">
              {widgets.map(w => (
                <button key={w.id} onClick={() => set({ ...data, docId: w.id })}>
                  <div className="picker-thumb">
                    {window.WidgetRender && (
                      <div style={{transform:'scale(0.32)',transformOrigin:'top left',pointerEvents:'none'}}>
                        <window.WidgetRender doc={w} hovered={false}/>
                      </div>
                    )}
                  </div>
                  <span className="w-title">{w.title}</span>
                  <span className="w-kind">{w.widgetKind} · {w.system}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="ws-blk-embed-render">
          {window.WidgetRender ? <window.WidgetRender doc={target} hovered={false}/> : <div className="hint">Widget renderer not loaded</div>}
          <div className="ws-blk-embed-meta">
            <span className="ws-blk-embed-live">● live</span>
            Embedded: <b>{target.title}</b> · {target.widgetKind} / {target.system}
            <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => set({ ...data, docId: '' })}>Change</button>
          </div>
        </div>
      )}
    </div>
  );
}

function EmbedWizard({ data, set }) {
  const docs = (window.useWSDocs ? window.useWSDocs() : null) || [];
  const wizards = docs.filter ? docs.filter(d => d.type === 'wizard') : [];
  const target = wizards.find(d => d.id === data.docId);
  return (
    <div className="ws-blk-embed">
      {!target ? (
        <div className="ws-blk-embed-empty">
          <div className="lbl">Pick a Workshop wizard to preview</div>
          {wizards.length === 0 && <div className="hint">No wizards in this workspace yet — build one first.</div>}
          {wizards.length > 0 && (
            <div className="picker">
              {wizards.map(w => (
                <button key={w.id} onClick={() => set({ ...data, docId: w.id })}>
                  <span className="w-title">{w.title}</span>
                  <span className="w-kind">{w.wizardKind} · {w.steps?.length || 0} steps</span>
                </button>
              ))}
            </div>
          )}
        </div>
      ) : (
        <div className="ws-blk-embed-wiz">
          <div className="head">
            <span className="ws-blk-embed-live">● live</span>
            <span className="title">{target.title}</span>
            <span className="kind">{target.wizardKind} · {target.steps?.length || 0} steps</span>
            <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => set({ ...data, docId: '' })}>Change</button>
          </div>
          <ol className="steps">
            {(target.steps || []).slice(0, 6).map((st, i) => (
              <li key={st.id}>
                <span className="num">{i + 1}</span>
                <span className="title">{st.title}</span>
                <span className="kind">{st.kind}</span>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}

// ============================================================
// Canonical core-render mapping (UNIFICATION.md W3) — SOURCE OF TRUTH is
// core/RenderType.jsx `blockToNode`, which expresses EVERY content block in
// the core vocabulary (atoms/clusters/zones) or routes it to the graph solver.
// This map is the human-readable index of that: atom-role · or 'diagram' for
// graph-routed composites · or 'widget-engine' for cross-doc embeds (which
// stay on WidgetRender, a different legitimate engine). `_atomRole` is set for
// the simple cases consumers may want to read.
// ============================================================
window.WS_BLOCK_CORE = {
  headline: 'headline', body: 'text', quote: 'note', pullquote: 'note', bigQuote: 'note',
  callout: 'callout', button: 'chip', bullets: 'bullet', checklist: 'bullet', icons: 'chip',
  chipRow: 'chip', iconStrip: 'chip', palette: 'chip', pillars: 'chip', logoStrip: 'chip',
  stats: 'metric', statPills: 'metric', metricRow: 'hero-number', featureCards: 'zone+hero-number',
  labeledCard: 'zone+bullet', statTable: 'zone+metric', bio: 'split+badge', photoBio: 'badge',
  contactCard: 'zone+bullet', hexBadge: 'badge', comparison: 'split+zone', hero: 'split',
  image: 'image', imageGrid: 'image', showcase: 'image',
  process: 'diagram', funnel: 'diagram', timeline: 'diagram', tagCluster: 'diagram', orgDiagram: 'diagram',
  embedWidget: 'widget-engine', embedWizard: 'widget-engine', divider: null,
};
window.WS_BLOCK_ATOM = window.WS_BLOCK_CORE; // back-compat alias
if (window.WS_BLOCKS) {
  Object.entries(window.WS_BLOCKS).forEach(([k, b]) => {
    if (k in window.WS_BLOCK_CORE) b._atomRole = window.WS_BLOCK_CORE[k]; // core treatment
  });
}
