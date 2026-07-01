// canvases/workshop/WidgetBuilder.jsx
// A self-contained editor for ConceptV widgets — KPI, media, and hybrid systems
// across Dashboard tile / Virtual Hub / Embeddable contexts.

const { useState: useState_wb, useEffect: useEffect_wb, useMemo: useMemo_wb } = React;

// ============================================================
// Defaults & schemas
// ============================================================

const WIDGET_KINDS = [
  { id: 'dashboard', label: 'Dashboard tile',    desc: 'Drops into the platform dashboard grid (320×220).', size: { w: 320, h: 220 } },
  { id: 'hub',       label: 'Virtual Hub widget', desc: 'Panel on conceptv.io/<hub> public surface (480×320).', size: { w: 480, h: 320 } },
  { id: 'embed',     label: 'Embeddable',         desc: 'Partner site drop-in. Self-contained, co-brandable (380×260).', size: { w: 380, h: 260 } },
];

const WIDGET_SYSTEMS = [
  { id: 'kpi',    label: 'KPIs',   desc: 'Stat tiles. Headline numbers + deltas.' },
  { id: 'media',  label: 'Media',  desc: 'Imagery-led. Hero shot + caption + CTA.' },
  { id: 'hybrid', label: 'Hybrid', desc: 'Mixed — one media, two KPIs, a row table.' },
];

const MOCK_FEEDS = {
  occupancy: [{ label: 'Occupancy',     value: '94%',  delta: '+3.2pt', deltaKind: 'up' }],
  hubs:      [{ label: 'Linked hubs',   value: '128',  delta: '+12',    deltaKind: 'up' }],
  signups:   [{ label: 'Sign-ups · 7d', value: '42',   delta: '-4',     deltaKind: 'down' }],
  capture:   [{ label: 'Captures',      value: '276',  delta: '+18',    deltaKind: 'up' }],
  revenue:   [{ label: 'Revenue · MTD', value: '$48k', delta: '+11.4%', deltaKind: 'up' }],
};

const SPARK_DATA = {
  rising:  [12,14,13,18,22,19,25,28,26,32,30,36,40],
  falling: [40,38,42,36,33,29,31,28,24,26,22,20,18],
  steady:  [22,24,23,25,22,26,24,27,26,28,27,29,28],
  spiky:   [10,32,14,28,12,30,15,28,22,12,28,16,30],
};

function blankWidget(kind, system) {
  const k = kind || 'dashboard';
  const s = system || 'kpi';
  const base = {
    eyebrow: 'Tower East',
    title:   widgetTitleFor(s),
    kpis:    [...MOCK_FEEDS.occupancy, ...MOCK_FEEDS.hubs, ...MOCK_FEEDS.capture],
    rows: [
      { label: '2 bed', value: '14 of 22',  status: 'ok' },
      { label: '1 bed', value: '8 of 14',  status: 'ok' },
      { label: 'Studio', value: '3 of 6',  status: 'warn' },
    ],
    media: { kind: 'placeholder', label: 'Tower East · hero render', tone: 'gold' },
    chart: { kind: 'spark', points: SPARK_DATA.rising, label: 'Captures · 13w' },
    cta:   { label: 'Open hub', href: 'conceptv.io/tower-east' },
  };
  return {
    widgetKind: k,
    system: s,
    mode: 'mock',
    mocked: true,
    coBrand: false,
    data: base,
  };
}

function widgetTitleFor(system) {
  return system === 'kpi' ? 'Performance' : system === 'media' ? 'Tower East' : 'Tower East · live';
}

// ============================================================
// Vi draft & helpers
// ============================================================

async function viDraftWidget(brief, kind, system) {
  const auto = (v) => !v || v === 'auto';
  const k = auto(kind) ? null : kind;
  const s = auto(system) ? null : system;

  const kindDoc = WIDGET_KINDS.map(x => `  - "${x.id}" — ${x.label}: ${x.desc}`).join('\n');
  const sysDoc  = WIDGET_SYSTEMS.map(x => `  - "${x.id}" — ${x.label}: ${x.desc}`).join('\n');

  const prompt = `You are Vi, drafting a ConceptV widget inside Workshop. ConceptV is an Australian property/innovation-tech platform. ${window.CV_AI.get('voice.conceptv').text}

User's brief: "${brief}"

Decide what to build:

WIDGET KIND ${k ? `(LOCKED to "${k}")` : '(pick the best fit for the brief)'}:
${kindDoc}

SYSTEM ${s ? `(LOCKED to "${s}")` : '(pick the best fit for the brief)'}:
${sysDoc}

Then draft the data. Return ONLY JSON, no prose:
{
  "widgetKind": "dashboard|hub|embed",
  "system": "kpi|media|hybrid",
  "title": "short widget title (3-5 words, tailored to brief)",
  "eyebrow": "short tag above title (2-3 words, optional, can be empty)",
  "kpis": [{"label":"...","value":"94%","delta":"+3.2pt","deltaKind":"up|down|flat"}],
  "rows": [{"label":"...","value":"...","status":"ok|warn|info"}],
  "media": {"kind":"placeholder","label":"what should be shown here","tone":"gold|bronze|ivory"},
  "chart": {"kind":"spark","trend":"rising|falling|steady|spiky","label":"short 2-4 word axis label"},
  "cta": {"label":"button label","href":"conceptv.io/<slug>"}
}

Sizing guidance by system:
- kpi: 3 KPIs, rows can be empty, media optional
- media: 1 strong media.label, KPIs limited to 0-1
- hybrid: 2 KPIs, 1 media caption, 3-4 rows

Tailor everything to the brief. Use specific property names, real numbers, real-sounding metrics.`;

  const reply = await window.CV_AI.complete(prompt);
  let parsed = null;
  try { parsed = JSON.parse(reply); }
  catch {
    const m = String(reply).match(/\{[\s\S]*\}/);
    if (m) { try { parsed = JSON.parse(m[0]); } catch {} }
  }
  if (!parsed) throw new Error('Vi returned no parsable widget');
  const trend = parsed?.chart?.trend || 'rising';
  const resolvedKind   = k || (WIDGET_KINDS.some(x => x.id === parsed.widgetKind) ? parsed.widgetKind : 'dashboard');
  const resolvedSystem = s || (WIDGET_SYSTEMS.some(x => x.id === parsed.system)   ? parsed.system     : 'hybrid');
  return {
    widgetKind: resolvedKind, system: resolvedSystem, mode: 'mock', mocked: true, coBrand: false,
    data: {
      title:   parsed.title  || 'Performance',
      eyebrow: parsed.eyebrow || '',
      kpis:    Array.isArray(parsed.kpis) ? parsed.kpis.slice(0, 4) : [],
      rows:    Array.isArray(parsed.rows) ? parsed.rows.slice(0, 6) : [],
      media:   parsed.media || { kind: 'placeholder', label: '', tone: 'gold' },
      chart:   { kind: 'spark', points: SPARK_DATA[trend] || SPARK_DATA.rising, label: parsed?.chart?.label || 'Trend' },
      cta:     parsed.cta || { label: 'Open hub', href: 'conceptv.io/' },
    },
  };
}

// ============================================================
// Widget renderer — pure presentational
// ============================================================

function WidgetRender({ doc, scale = 1, hovered, loading = false, motion = false }) {
  const { widgetKind, system, data, coBrand } = doc;
  // authorship is legible (DESIGN-LANGUAGE §11): a Vi-drafted mock carries Vi's
  // mark; once a human edits it, it reads as yours. Same provenance vocabulary
  // (.by-*) the engine zones use — no parallel chrome.
  const author = doc.author || (doc.mocked ? 'vi' : 'human');
  const kindDef = WIDGET_KINDS.find(k => k.id === widgetKind) || WIDGET_KINDS[0];
  const { w, h } = kindDef.size;
  const accent = coBrand ? '#2A78C6' : 'var(--accent-gold)';
  const accentSoft = coBrand ? '#DEEAF7' : 'var(--accent-gold-soft)';

  return (
    <div className="ws-widget-frame" style={{
      width: w, height: h, position: 'relative',
      transform: scale !== 1 ? `scale(${scale})` : undefined,
      transformOrigin: 'top left',
    }}>
      <div className="ws-widget-card" style={{
        background: 'var(--bg-surface)',
        borderRadius: 'var(--r-lg)',
        boxShadow: hovered ? 'var(--shadow-pop)' : 'var(--shadow-card)',
        padding: widgetKind === 'embed' ? 18 : 20,
        height: '100%',
        display: 'flex', flexDirection: 'column', gap: 12,
        border: '1px solid var(--border-faint)',
        position: 'relative', overflow: 'hidden',
        transition: 'box-shadow var(--dur-base) var(--ease-out), transform var(--dur-base) var(--ease-out)',
        transform: hovered ? 'translateY(-1px)' : 'translateY(0)',
      }}>
        {/* Header */}
        <div style={{display:'flex',alignItems:'flex-start',gap:10}}>
          <div style={{flex:1,minWidth:0}}>
            {data.eyebrow && <div style={{font:'600 9px/1 var(--font-body)',color:'var(--accent-bronze)',letterSpacing:'0.1em',textTransform:'uppercase',marginBottom:4}}>{data.eyebrow}</div>}
            <div style={{font:'700 16px/1.1 var(--font-display)',color:'var(--fg-primary)',letterSpacing:'-0.01em'}}>{data.title}</div>
          </div>
          {coBrand && (
            <div style={{
              padding:'3px 8px', borderRadius: 'var(--r-pill)',
              background: accentSoft, color: accent,
              font:'700 9px/1 var(--font-body)', letterSpacing:'0.06em', textTransform:'uppercase',
            }}>Partner</div>
          )}
          {!coBrand && (
            <span className={`by by-${author}`} style={{flex:'none',marginTop:1}}>{author === 'vi' ? 'Vi' : 'You'}</span>
          )}
        </div>

        {/* Body — rendered THROUGH THE ONE ENGINE (UNIFICATION W7): the same
            chart / metric / bullet atoms + tokens as every other surface, no
            parallel widget parts. Loud if the engine isn't loaded. */}
        <div style={{flex:1,minHeight:0,display:'flex',flexDirection:'column',gap:10}} data-density="compact">
          {(() => {
            const CT = window.__cvContainmentTree, DS = window.__cvDiagramSolver, T2N = window.__cvTypeToNode;
            if (!CT || !T2N) throw new Error('[WidgetRender] core engine not loaded — unification requires window.__cvContainmentTree');
            const node = T2N({ layer:'system', family:'widget', runtime:{ kind:'widget-system', key:system } }, { ...doc, __bodyOnly:true }, {}).node;
            return React.createElement(CT, { node, lod:'full', surface:'web', density:'compact', DiagramSolver: DS, loading, motion });
          })()}
        </div>

        {/* CTA */}
        {data.cta?.label && (widgetKind !== 'dashboard' || system === 'media') && (
          <div style={{display:'flex',alignItems:'center',gap:8,paddingTop:8,borderTop:'1px dashed var(--accent-gold-soft)'}}>
            <span style={{font:'500 10px/1 var(--font-mono)',color:'var(--fg-muted)',flex:1,minWidth:0,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{data.cta.href}</span>
            <button style={{
              background: accent, color: 'var(--fg-primary)', border: 'none',
              padding: '7px 12px', borderRadius: 'var(--r-md)',
              font: '600 11px/1 var(--font-body)', cursor: 'pointer', flex: 'none',
            }}>{data.cta.label} →</button>
          </div>
        )}
      </div>
    </div>
  );
}


// ============================================================
// Editor
// ============================================================

function WidgetBuilder({ doc, saveDoc, closeDoc, onSaveTemplate }) {
  const WSCandidateGallery = window.WSCandidateGallery;
  const [livePreview, setLivePreview] = useState_wb(true);
  const [showExport, setShowExport] = useState_wb(false);
  const [vary, setVary] = useState_wb(false);
  const [galleryState, setGalleryState] = useState_wb(null);

  if (!doc) return <div>Widget doc missing</div>;
  const { widgetKind, system, mode, data, mocked, coBrand } = doc;

  function update(patch) { saveDoc({ ...doc, ...patch }); }
  function updateData(patch) { saveDoc({ ...doc, data: { ...doc.data, ...patch } }); }
  function setKind(id) { update({ widgetKind: id }); }
  function setSystem(id) { update({ system: id }); }

  async function runGallery({ target, title, onPickOverride }) {
    setGalleryState({ title, busy: true, candidates: [], onPickOverride, target });
    try {
      const cands = await window.WS_AI.generateCandidates({ doc, target, count: 3 });
      setGalleryState(s => s ? { ...s, busy: false, candidates: cands } : s);
    } catch {
      setGalleryState(null);
      window.dsaToast?.('Vi could not generate options');
    }
  }
  async function refineGallery(hint) {
    if (!galleryState) return;
    setGalleryState(s => ({ ...s, busy: true }));
    try {
      const cands = await window.WS_AI.generateCandidates({ doc, target: galleryState.target, count: 3, brief: hint });
      setGalleryState(s => s ? { ...s, busy: false, candidates: cands } : s);
    } catch { setGalleryState(s => s ? { ...s, busy: false } : s); }
  }
  function pickCandidate(cand) {
    if (galleryState?.onPickOverride) galleryState.onPickOverride(cand);
    else if (cand.diff) saveDoc(window.WS_AI.applyDiff(doc, cand.diff));
    setGalleryState(null);
    window.dsaToast?.('Applied');
  }

  return (
    <>
      <CanvasHeader
        title={doc.title}
        sub={`Widget · ${WIDGET_KINDS.find(k => k.id === widgetKind)?.label} · ${WIDGET_SYSTEMS.find(s => s.id === system)?.label}`}
        actions={<>
          <button className="dsa-btn dsa-btn--ghost" onClick={closeDoc}>← All docs</button>
          <div className="ws-mode-seg">
            <button className={mode === 'mock' ? 'active' : ''} onClick={() => update({ mode: 'mock' })} title="Visual mock — static, drag-drop">Mock</button>
            <button className={mode === 'proto' ? 'active' : ''} onClick={() => update({ mode: 'proto' })} title="Functional prototype — interactive, real state">Prototype</button>
          </div>
          <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => setVary(v => !v)}>{vary ? 'Hide variations' : 'Variations'}</button>
          <button className="dsa-btn dsa-btn--outline dsa-btn--sm" onClick={async () => {
            window.dsaToast?.('Vi is extracting a Type…');
            try {
              const draft = await window.CV_TYPES_SAVE.fromWidget(doc);
              window.CV_TYPES_PROMPT.open(draft);
            } catch { window.dsaToast?.('Could not promote'); }
          }} title="Promote this widget into a reusable Type in the Registry">
            <ViShape size={10}/> + Save as Type
          </button>
          <button className="dsa-btn dsa-btn--outline" onClick={() => onSaveTemplate?.(doc)} title="Save as a re-runnable template">+ Save as template</button>
          <span style={{position:'relative'}} onClick={e => e.stopPropagation()}>
            <button className="dsa-btn dsa-btn--primary" onClick={() => setShowExport(s => !s)}>Export ↗</button>
            {showExport && <WidgetExportMenu doc={doc} onClose={() => setShowExport(false)}/>}
          </span>
        </>}
      />
      <div className="dsa-canvas-body">
        <div className="ws-doc-head">
          <input className="ws-doc-title" value={doc.title} onChange={e => update({ title: e.target.value })}/>
          <span className="ws-doc-meta">Auto-saved · {new Date(doc.createdAt).toLocaleDateString()}</span>
        </div>

        {/* Top: kind + system pickers + data toggle */}
        <div className="ws-wb-bar">
          <div className="ws-wb-group">
            <div className="ws-wb-label">Widget kind</div>
            <div className="ws-wb-pills">
              {(window.WIDGET_KINDS || WIDGET_KINDS).map(k => (
                <button key={k.id} className={`ws-wb-pill ${widgetKind === k.id ? 'active' : ''}`}
                  onClick={() => setKind(k.id)}>
                  {k.label}
                  <span className="size">{k.size.w}×{k.size.h}</span>
                  {k.provenance && k.provenance !== 'built-in' && <span className="cv-type-prov cv-type-prov-user" style={{marginLeft:6,padding:'1px 4px',fontSize:8}}>{k.provenance}</span>}
                </button>
              ))}
            </div>
          </div>
          <div className="ws-wb-group">
            <div className="ws-wb-label">System</div>
            <div className="ws-wb-pills">
              {(window.WIDGET_SYSTEMS || WIDGET_SYSTEMS).map(s => (
                <button key={s.id} className={`ws-wb-pill ${system === s.id ? 'active' : ''}`}
                  onClick={() => setSystem(s.id)} title={s.desc}>
                  {s.label}
                  {s.provenance && s.provenance !== 'built-in' && <span className="cv-type-prov cv-type-prov-user" style={{marginLeft:6,padding:'1px 4px',fontSize:8}}>{s.provenance}</span>}
                </button>
              ))}
            </div>
          </div>
          <div className="ws-wb-group">
            <div className="ws-wb-label">Mocked data</div>
            <div className="ws-wb-pills">
              <button className={`ws-wb-pill ${mocked ? 'active' : ''}`} onClick={() => update({ mocked: !mocked })}>
                {mocked ? '● Live mocked feed' : '○ Static values'}
              </button>
              <button className={`ws-wb-pill ${coBrand ? 'active' : ''}`} onClick={() => update({ coBrand: !coBrand })}>
                {coBrand ? '● Co-brand skin' : '○ ConceptV skin'}
              </button>
            </div>
          </div>
        </div>

        <div className="ws-wb-workspace">
          {/* Left: data editor */}
          <aside className="ws-wb-side">
            <WidgetDataPanel doc={doc} update={update} updateData={updateData} runGallery={runGallery}/>
          </aside>

          {/* Center: preview */}
          <main className="ws-wb-stage">
            <WidgetStage doc={doc} mocked={mocked} mode={mode}/>
          </main>

          {/* Right: variations */}
          {vary && (
            <aside className="ws-wb-vary">
              <WidgetVariationsPanel doc={doc} onPick={(patch) => update(patch)}/>
            </aside>
          )}
        </div>
      </div>
      <WSCandidateGallery
        open={!!galleryState}
        title={galleryState?.title}
        busy={galleryState?.busy}
        candidates={galleryState?.candidates}
        doc={doc}
        onPick={pickCandidate}
        onClose={() => setGalleryState(null)}
        onRefine={refineGallery}
      />
    </>
  );
}

// ============================================================
// Stage — renders widget inside platform/hub/embed contexts
// ============================================================

function WidgetStage({ doc, mocked, mode }) {
  const [tick, setTick] = useState_wb(0);
  const [hovered, setHovered] = useState_wb(false);
  // resolve, never pop (states.css §10): when the mocked feed switches on, the tile
  // shows skeletons for one beat, then the real data resolves in with motion.
  const [resolving, setResolving] = useState_wb(false);
  useEffect_wb(() => {
    if (!mocked) { setResolving(false); return; }
    setResolving(true);
    const t = setTimeout(() => setResolving(false), 620);
    return () => clearTimeout(t);
  }, [mocked]);

  // Mocked data feed: subtly rotates KPIs / spark on a timer when mocked === true
  useEffect_wb(() => {
    if (!mocked) return;
    const t = setInterval(() => setTick(x => x + 1), 2200);
    return () => clearInterval(t);
  }, [mocked]);

  const liveDoc = useMemo_wb(() => {
    if (!mocked) return doc;
    // Rotate KPIs and spark to suggest live data
    const seed = tick;
    const trends = ['rising', 'steady', 'spiky', 'rising', 'falling'];
    const trend = trends[seed % trends.length];
    const points = SPARK_DATA[trend] || SPARK_DATA.rising;
    // Nudge KPIs deterministically
    const nudgedKpis = (doc.data.kpis || []).map((k, i) => {
      const m = String(k.value).match(/(-?\d+(\.\d+)?)/);
      if (!m) return k;
      const num = parseFloat(m[0]);
      const drift = ((seed + i) % 6) - 2; // -2..3
      const newVal = String(k.value).replace(m[0], String((num + drift * (k.label?.toLowerCase().includes('rev') ? 0.5 : 1)).toFixed(num % 1 === 0 ? 0 : 1)));
      return { ...k, value: newVal };
    });
    return { ...doc, data: { ...doc.data, kpis: nudgedKpis, chart: { ...doc.data.chart, points } } };
  }, [doc, tick, mocked]);

  return (
    <>
      <WidgetContextFrame kind={doc.widgetKind}>
        <div
          className={`ws-widget-slot ${mode === 'proto' ? 'proto' : ''}`}
          onMouseEnter={() => mode === 'proto' && setHovered(true)}
          onMouseLeave={() => mode === 'proto' && setHovered(false)}
        >
          <WidgetRender doc={liveDoc} hovered={hovered} loading={resolving} motion={mode === 'proto'}/>
          {mocked && !resolving && <div className="ws-live-pill"><span/> live</div>}
        </div>
      </WidgetContextFrame>
      <div style={{textAlign:'center',marginTop:14,font:'500 11px/1.4 var(--font-body)',color:'var(--fg-muted)'}}>
        {mode === 'proto'
          ? <>Hovering, mocked data, and CTA states are interactive. Click <b>Mock</b> for a still frame.</>
          : <>Static visual mock. Switch to <b>Prototype</b> to enable hover / live data / clickable CTA.</>}
      </div>
    </>
  );
}

function WidgetContextFrame({ kind, children }) {
  if (kind === 'dashboard') {
    return (
      <div className="ws-ctx ws-ctx--dash">
        <div className="ws-ctx-chrome">
          <div className="ws-ctx-side">
            <div className="ws-ctx-logo"><div className="diamond"/></div>
            {['Overview','Hubs','Captures','Brand kit','Settings'].map((l, i) => (
              <div key={l} className={`ws-ctx-nav ${i === 0 ? 'active' : ''}`}>{l}</div>
            ))}
          </div>
          <div className="ws-ctx-body">
            <div className="ws-ctx-top">
              <div className="ws-ctx-crumb">Workspace / Dashboard</div>
              <div className="ws-ctx-search"/>
              <div className="ws-ctx-avatar"/>
            </div>
            <div className="ws-ctx-grid">
              <div className="ws-ctx-tile mute"/>
              <div className="ws-ctx-tile mute"/>
              <div className="ws-ctx-target">{children}</div>
              <div className="ws-ctx-tile mute"/>
              <div className="ws-ctx-tile mute"/>
            </div>
          </div>
        </div>
        <div className="ws-ctx-tag">Dashboard context · platform UI kit</div>
      </div>
    );
  }
  if (kind === 'hub') {
    return (
      <div className="ws-ctx ws-ctx--hub">
        <div className="ws-ctx-chrome">
          <div className="ws-ctx-hub-top">
            <span className="brand"><span className="diamond"/> ConceptV</span>
            <span className="url">conceptv.io/tower-east</span>
          </div>
          <div className="ws-ctx-hub-body">
            <div className="ws-ctx-hub-hero"/>
            <div className="ws-ctx-target">{children}</div>
            <div className="ws-ctx-hub-tiles">
              <div className="ws-ctx-tile mute"/>
              <div className="ws-ctx-tile mute"/>
              <div className="ws-ctx-tile mute"/>
            </div>
          </div>
        </div>
        <div className="ws-ctx-tag">Virtual Hub context · conceptv.io/&lt;hub&gt;</div>
      </div>
    );
  }
  // embed
  return (
    <div className="ws-ctx ws-ctx--embed">
      <div className="ws-ctx-chrome">
        <div className="ws-ctx-embed-host">
          <div className="ws-ctx-embed-line w70"/>
          <div className="ws-ctx-embed-line w50"/>
          <div className="ws-ctx-target floating">{children}</div>
          <div className="ws-ctx-embed-line w80"/>
          <div className="ws-ctx-embed-line w60"/>
          <div className="ws-ctx-embed-line w90"/>
        </div>
      </div>
      <div className="ws-ctx-tag">Embedded on partner site</div>
    </div>
  );
}

// ============================================================
// Data panel
// ============================================================

function WidgetDataPanel({ doc, update, updateData, runGallery }) {
  const { data, system } = doc;
  const ViBtn = ({ onClick, title }) => (
    <button onClick={onClick} title={title}
      style={{
        marginLeft:'auto', padding:'3px 7px', borderRadius:999,
        background:'var(--bg-dark)', color:'var(--fg-inverse)',
        border:'none', cursor:'pointer',
        font:'600 9px/1 var(--font-body)', letterSpacing:'0.04em',
        display:'inline-flex', alignItems:'center', gap:4,
      }}>
      <ViShape size={10}/> alts
    </button>
  );
  return (
    <div className="ws-wb-side-inner">
      <div style={{display:'flex',alignItems:'center',gap:8}}>
        <h5 style={{margin:0,padding:0,borderBottom:'none'}}>Content</h5>
        {runGallery && (
          <ViBtn
            title="Vi: 3 alternative widget content sets"
            onClick={() => runGallery({ target: { kind: 'widget.alternate' }, title: '3 alternative angles for this widget' })}
          />
        )}
      </div>
      <div style={{height:1,background:'var(--accent-gold-soft)',marginTop:6,marginBottom:10}}/>
      <Labeled label="Eyebrow"><input value={data.eyebrow || ''} onChange={e => updateData({ eyebrow: e.target.value })}/></Labeled>
      <Labeled label="Title"><input value={data.title || ''} onChange={e => updateData({ title: e.target.value })}/></Labeled>

      {(system === 'kpi' || system === 'hybrid') && (
        <>
          <div style={{display:'flex',alignItems:'center',gap:8,marginTop:16,paddingBottom:6,borderBottom:'1px dashed var(--accent-gold-soft)'}}>
            <h5 style={{margin:0,padding:0,borderBottom:'none'}}>KPIs</h5>
            {runGallery && (
              <ViBtn
                title="Vi: 3 alternative KPI sets"
                onClick={() => runGallery({ target: { kind: 'widget.kpis.regen', count: doc.data?.kpis?.length || 3 }, title: '3 KPI sets for this widget' })}
              />
            )}
          </div>
          {(data.kpis || []).map((k, i) => (
            <div key={i} className="ws-wb-row">
              <input placeholder="Label" value={k.label || ''} onChange={e => updateKpi(i, { label: e.target.value })}/>
              <input placeholder="Value" value={k.value || ''} onChange={e => updateKpi(i, { value: e.target.value })}/>
              <input placeholder="Δ" style={{width:60}} value={k.delta || ''} onChange={e => updateKpi(i, { delta: e.target.value })}/>
              <select value={k.deltaKind || 'up'} onChange={e => updateKpi(i, { deltaKind: e.target.value })}>
                <option value="up">↑</option><option value="down">↓</option><option value="flat">·</option>
              </select>
              <button onClick={() => removeKpi(i)} title="Remove">✕</button>
            </div>
          ))}
          <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => addKpi()}>+ KPI</button>
          <h5>Sparkline</h5>
          <div className="ws-wb-row">
            <select value={inferTrend(data.chart?.points)} onChange={e => updateData({ chart: { ...data.chart, points: SPARK_DATA[e.target.value] } })}>
              {Object.keys(SPARK_DATA).map(k => <option key={k} value={k}>{k}</option>)}
            </select>
            <input placeholder="Axis label" value={data.chart?.label || ''} onChange={e => updateData({ chart: { ...data.chart, label: e.target.value } })}/>
          </div>
        </>
      )}

      {(system === 'media' || system === 'hybrid') && (
        <>
          <h5>Media</h5>
          <Labeled label="Caption"><input value={data.media?.label || ''} onChange={e => updateData({ media: { ...data.media, label: e.target.value } })}/></Labeled>
        </>
      )}

      {system === 'hybrid' && (
        <>
          <h5>Rows</h5>
          {(data.rows || []).map((r, i) => (
            <div key={i} className="ws-wb-row">
              <input placeholder="Label" value={r.label || ''} onChange={e => updateRow(i, { label: e.target.value })}/>
              <input placeholder="Value" value={r.value || ''} onChange={e => updateRow(i, { value: e.target.value })}/>
              <select value={r.status || 'ok'} onChange={e => updateRow(i, { status: e.target.value })}>
                <option value="ok">ok</option><option value="warn">warn</option><option value="info">info</option>
              </select>
              <button onClick={() => removeRow(i)} title="Remove">✕</button>
            </div>
          ))}
          <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => addRow()}>+ Row</button>
        </>
      )}

      <h5>Call to action</h5>
      <Labeled label="Label"><input value={data.cta?.label || ''} onChange={e => updateData({ cta: { ...data.cta, label: e.target.value } })}/></Labeled>
      <Labeled label="URL"><input value={data.cta?.href || ''} onChange={e => updateData({ cta: { ...data.cta, href: e.target.value } })}/></Labeled>

      <h5>Vi</h5>
      <ViRefineBox doc={doc} update={update}/>
    </div>
  );

  function updateKpi(i, p) { updateData({ kpis: data.kpis.map((k, j) => i === j ? { ...k, ...p } : k) }); }
  function removeKpi(i)    { updateData({ kpis: data.kpis.filter((_, j) => j !== i) }); }
  function addKpi()        { updateData({ kpis: [...(data.kpis||[]), { label: 'New', value: '0', delta: '+0', deltaKind: 'flat' }] }); }
  function updateRow(i, p) { updateData({ rows: data.rows.map((k, j) => i === j ? { ...k, ...p } : k) }); }
  function removeRow(i)    { updateData({ rows: data.rows.filter((_, j) => j !== i) }); }
  function addRow()        { updateData({ rows: [...(data.rows||[]), { label: 'Item', value: '0', status: 'ok' }] }); }
}

function inferTrend(points) {
  if (!points) return 'rising';
  const json = JSON.stringify(points);
  for (const k of Object.keys(SPARK_DATA)) {
    if (JSON.stringify(SPARK_DATA[k]) === json) return k;
  }
  return 'rising';
}

function Labeled({ label, children }) {
  return (
    <label className="ws-wb-field">
      <span>{label}</span>
      {children}
    </label>
  );
}

function ViRefineBox({ doc, update }) {
  const [msg, setMsg] = useState_wb('');
  const [busy, setBusy] = useState_wb(false);
  async function go() {
    if (!msg.trim() || busy) return;
    setBusy(true);
    try {
      const draft = await viDraftWidget(msg.trim(), doc.widgetKind, doc.system);
      // Keep title & cta if user has customized, merge data
      update({
        data: { ...draft.data, title: doc.data.title === widgetTitleFor(doc.system) ? draft.data.title : doc.data.title },
      });
      window.dsaToast?.('Vi refined this widget');
      setMsg('');
    } catch {
      window.dsaToast?.('Vi could not refine — try again');
    } finally { setBusy(false); }
  }
  return (
    <div className="ws-wb-vi">
      <ViShape size={14}/>
      <textarea rows="2" placeholder='Ask Vi: "make it more urgent", "show capture velocity", "tower west variant"' value={msg} onChange={e => setMsg(e.target.value)}/>
      <button className="dsa-btn dsa-btn--ai dsa-btn--sm" onClick={go} disabled={busy || !msg.trim()}>{busy ? '…' : 'Refine'}</button>
    </div>
  );
}

// ============================================================
// Variations panel — 3 system swatches side-by-side
// ============================================================

function WidgetVariationsPanel({ doc, onPick }) {
  return (
    <div className="ws-wb-vary-inner">
      <h5>Variations</h5>
      <p className="dim">Swap the system for this widget. KPIs sit calm; media commands attention; hybrid does both.</p>
      <div className="ws-wb-vary-list">
        {WIDGET_SYSTEMS.map(s => {
          const proxy = { ...doc, system: s.id };
          return (
            <button key={s.id}
              className={`ws-wb-vary-card ${doc.system === s.id ? 'active' : ''}`}
              onClick={() => onPick({ system: s.id })}>
              <div className="thumb">
                <div className="thumb-inner" style={{ transform: 'scale(0.42)', transformOrigin: 'top left' }}>
                  <WidgetRender doc={proxy} hovered={false}/>
                </div>
              </div>
              <div className="meta">
                <strong>{s.label}</strong>
                <span>{s.desc}</span>
              </div>
            </button>
          );
        })}
      </div>
      <h5>Try a different kind</h5>
      <div className="ws-wb-vary-list">
        {WIDGET_KINDS.map(k => (
          <button key={k.id}
            className={`ws-wb-vary-card kind ${doc.widgetKind === k.id ? 'active' : ''}`}
            onClick={() => onPick({ widgetKind: k.id })}>
            <span>{k.label}</span>
            <span className="dim">{k.size.w}×{k.size.h}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

// ============================================================
// Export menu
// ============================================================

function WidgetExportMenu({ doc, onClose }) {
  const [view, setView] = useState_wb(null);
  const code = useMemo_wb(() => widgetToJSX(doc), [doc]);

  function downloadJSX() {
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `${slugify(doc.title)}.jsx`; a.click();
    URL.revokeObjectURL(url);
    onClose?.();
  }
  async function downloadPNG() {
    const node = document.querySelector('.ws-widget-frame');
    if (!node) { window.dsaToast?.('Could not find widget'); return; }
    try {
      const rect = node.getBoundingClientRect();
      const canvas = document.createElement('canvas');
      canvas.width = rect.width * 2; canvas.height = rect.height * 2;
      const ctx = canvas.getContext('2d');
      const html = new XMLSerializer().serializeToString(htmlToInline(node));
      const data = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="${rect.width}" height="${rect.height}"><foreignObject width="100%" height="100%">${html}</foreignObject></svg>`)}`;
      const img = new Image();
      img.onload = () => {
        ctx.scale(2, 2); ctx.drawImage(img, 0, 0);
        canvas.toBlob(b => {
          const u = URL.createObjectURL(b);
          const a = document.createElement('a'); a.href = u; a.download = `${slugify(doc.title)}.png`; a.click();
          URL.revokeObjectURL(u);
        });
      };
      img.onerror = () => window.dsaToast?.('PNG export needs cross-origin permissions — try Print to PDF instead');
      img.src = data;
      onClose?.();
    } catch { window.dsaToast?.('Export failed'); }
  }
  function printPDF() {
    window.print();
    onClose?.();
  }

  return (
    <div className="ws-export-menu" onClick={e => e.stopPropagation()}>
      <button onClick={() => setView(view === 'jsx' ? null : 'jsx')}>📄 React / JSX</button>
      <button onClick={downloadJSX}>⬇ Download .jsx</button>
      <button onClick={downloadPNG}>🖼 PNG (widget only)</button>
      <button onClick={printPDF}>🖨 Print → PDF</button>
      {view === 'jsx' && (
        <pre className="ws-export-code">{code}</pre>
      )}
    </div>
  );
}

function htmlToInline(node) {
  // Minimal — return a clone; svg foreignObject path may not work cross-browser,
  // but the user has the JSX + Print path as alternatives.
  return node.cloneNode(true);
}

function widgetToJSX(doc) {
  const { widgetKind, system, data, coBrand } = doc;
  return `// ${doc.title} — ConceptV ${widgetKind} widget (${system})
// Generated from ConceptV Studio · Workshop · Widget Builder
import React from 'react';

export default function ${pascalCase(doc.title)}() {
  const data = ${JSON.stringify(data, null, 2)};
  return (
    <div style={{
      width: ${WIDGET_KINDS.find(k => k.id === widgetKind).size.w},
      height: ${WIDGET_KINDS.find(k => k.id === widgetKind).size.h},
      background: 'var(--bg-surface)',
      borderRadius: 'var(--r-lg)',
      boxShadow: 'var(--shadow-card)',
      padding: 20, display: 'flex', flexDirection: 'column', gap: 12,
      border: '1px solid var(--border-faint)',
      fontFamily: 'var(--font-body)', color: 'var(--fg-primary)',
    }}>
      {data.eyebrow && (
        <div style={{font:'600 9px/1 var(--font-body)',color:'var(--accent-bronze)',letterSpacing:'0.1em',textTransform:'uppercase'}}>
          {data.eyebrow}
        </div>
      )}
      <div style={{font:'700 16px/1.1 var(--font-display)',letterSpacing:'-0.01em'}}>
        {data.title}
      </div>
      ${system === 'kpi' || system === 'hybrid' ? `<div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit, minmax(80px, 1fr))',gap:10}}>
        {(data.kpis || []).map((k, i) => (
          <div key={i} style={{padding:'10px 12px',background:'var(--bg-canvas)',borderRadius:'var(--r-md)',border:'1px solid var(--border-faint)'}}>
            <div style={{font:'700 20px/1 var(--font-display)'}}>{k.value}</div>
            <div style={{font:'500 10px/1.3 var(--font-body)',color:'var(--fg-muted)',textTransform:'uppercase',letterSpacing:'0.06em'}}>{k.label}</div>
          </div>
        ))}
      </div>` : ''}
      ${data.cta?.label ? `<div style={{display:'flex',alignItems:'center',gap:8,paddingTop:8,borderTop:'1px dashed var(--accent-gold-soft)'}}>
        <span style={{font:'500 10px/1 var(--font-mono)',color:'var(--fg-muted)',flex:1}}>{data.cta.href}</span>
        <a href={'https://' + data.cta.href} style={{background:'var(--accent-gold)',color:'var(--fg-primary)',padding:'7px 12px',borderRadius:'var(--r-md)',font:'600 11px/1 var(--font-body)',textDecoration:'none'}}>{data.cta.label} →</a>
      </div>` : ''}
    </div>
  );
}
`;
}

function pascalCase(s) {
  return String(s).replace(/[^a-z0-9]+/gi, ' ').trim().split(/\s+/).map(w => w[0]?.toUpperCase() + w.slice(1).toLowerCase()).join('') || 'Widget';
}
function slugify(s) {
  return String(s).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'widget';
}

// ============================================================
// Exports
// ============================================================

window.WidgetBuilder = WidgetBuilder;
window.WidgetRender = WidgetRender;
window.WIDGET_KINDS = WIDGET_KINDS;
window.WIDGET_SYSTEMS = WIDGET_SYSTEMS;
window.viDraftWidget = viDraftWidget;
window.blankWidget = blankWidget;
