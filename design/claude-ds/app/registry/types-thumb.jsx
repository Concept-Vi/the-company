// app/registry/types-thumb.jsx
// Universal thumbnail renderer for any Type in the registry.
// Layer-aware: each layer + runtime combo knows how to render a representative
// preview, then we scale it to fit. Used in TypeCard everywhere — Registry,
// Workshop landing, Templates, Architecture, TypeBuilder.

const { useMemo: useMemo_th, useRef: useRef_th, useState: useState_th, useEffect: useEffect_th } = React;

// ===========================================================================
// Scaled stage — fits children of any size into a target box.
// Renders at native size offscreen, measures, then scales the visual.
// ===========================================================================
function ScaledThumb({ children, native = { w: 320, h: 220 }, width, height, align = 'center', bg, pad = 0 }) {
  const w = width || 240;
  const h = height || Math.round(w * (native.h / native.w));
  const sx = (w - pad * 2) / native.w;
  const sy = (h - pad * 2) / native.h;
  const scale = Math.min(sx, sy);
  const tx = (w - native.w * scale) / 2;
  const ty = align === 'top' ? pad : (h - native.h * scale) / 2;
  return (
    <div className="cv-thumb-stage" style={{ width: w, height: h, background: bg || 'var(--bg-canvas)' }}>
      <div className="cv-thumb-scaled" style={{
        position: 'absolute',
        width: native.w, height: native.h,
        transformOrigin: '0 0',
        transform: `translate(${tx}px, ${ty}px) scale(${scale})`,
        pointerEvents: 'none',
      }}>{children}</div>
    </div>
  );
}

// ===========================================================================
// TypeThumb — the entry point
// ===========================================================================
function TypeThumb({ type: rawType, width = 240, height, dense = false, contextLabel }) {
  const R = window.CV_REGISTRY;
  const type = useMemo_th(() => {
    if (!rawType) return null;
    if (rawType.lineage) return rawType;
    return R?.resolve(rawType.id) || rawType;
  }, [rawType?.id]);

  if (!type) return <ThumbPlaceholder width={width} height={height}/>;

  const h = height || Math.round(width * 0.66);
  // Layer/family/runtime dispatch
  const renderer = pickRenderer(type);
  if (!renderer) return <ThumbPlaceholder width={width} height={h} label={type.layer}/>;
  return (
    <div className={`cv-thumb cv-thumb-${type.layer} ${dense ? 'dense' : ''}`} style={{ width, height: h }}>
      {renderer({ type, width, height: h, dense, contextLabel })}
      {contextLabel && (
        <div className="cv-thumb-context">{contextLabel}</div>
      )}
    </div>
  );
}

function ThumbPlaceholder({ width, height, label }) {
  return (
    <div className="cv-thumb cv-thumb-placeholder" style={{ width, height: height || Math.round(width * 0.66) }}>
      <CvIcon name="image-stack" size={24} tone="muted"/>
      {label && <span>{label}</span>}
    </div>
  );
}

// ===========================================================================
// Dispatcher — pick the right rendering function for a Type
// ===========================================================================
function pickRenderer(type) {
  const layer = type.layer;
  const family = type.family;
  const runtimeKind = type.runtime?.kind;

  if (layer === 'token') {
    if (family === 'color') return TokenColorThumb;
    if (family === 'type')  return TokenTypeThumb;
    if (family === 'shape') return TokenShapeThumb;
    return TokenGenericThumb;
  }
  if (layer === 'atom') {
    if (family === 'icon')   return AtomIconThumb;
    if (family === 'status') return AtomStatusThumb;
    if (family === 'shape')  return AtomShapeThumb;
    if (family === 'mark')   return AtomStampThumb;
    return AtomIconThumb;
  }
  if (layer === 'block') return BlockThumb;
  if (layer === 'system') {
    if (family === 'widget') return SystemWidgetThumb;
    return SystemGenericThumb;
  }
  if (layer === 'surface') {
    if (family === 'widget')      return SurfaceWidgetThumb;
    if (family === 'wizard-step') return SurfaceWizardStepThumb;
    if (family === 'deck-slide')  return SurfaceSlideThumb;
    return SurfaceGenericThumb;
  }
  if (layer === 'doc') {
    if (family === 'widget')   return DocWidgetThumb;
    if (family === 'wizard')   return DocWizardThumb;
    if (family === 'deck')     return DocDeckThumb;
    if (family === 'brochure') return DocBrochureThumb;
    return DocGenericThumb;
  }
  if (layer === 'template') return TemplateThumb;
  return null;
}

// ===========================================================================
// TOKEN renderers
// ===========================================================================
function TokenColorThumb({ type, width, height }) {
  const hex = type.defaults?.hex || '#E0C010';
  const light = isLightHex(hex);
  return (
    <div className="cv-thumb-token-color" style={{ width, height, background: hex }}>
      <span className="hex" style={{ color: light ? '#1F1A12' : '#FBF7EC' }}>{hex}</span>
      <span className="name" style={{ color: light ? '#1F1A12cc' : '#FBF7ECcc' }}>{type.name}</span>
    </div>
  );
}
function TokenTypeThumb({ type, width, height }) {
  const family = type.defaults?.family || 'sans-serif';
  const weight = type.defaults?.weight || 600;
  return (
    <div className="cv-thumb-token-type" style={{ width, height }}>
      <div className="big" style={{ font: `${weight} ${Math.round(height * 0.6)}px/1 ${family}` }}>Aa</div>
      <div className="meta">
        <strong>{type.name}</strong>
        <span style={{ font: `400 11px/1 ${family}` }}>{family}</span>
      </div>
    </div>
  );
}
function TokenShapeThumb({ type, width, height }) {
  const id = type.id.split('.').pop();
  return (
    <div className="cv-thumb-token-shape" style={{ width, height }}>
      <RenderShape shape={id} size={Math.min(width, height) * 0.6}/>
      <span className="name">{type.name}</span>
    </div>
  );
}
function TokenGenericThumb({ type, width, height }) {
  return (
    <div className="cv-thumb-token-generic" style={{ width, height }}>
      <CvIcon name={type.icon || 'color-swatches'} size={28} tone="bronze"/>
      <span>{type.name}</span>
    </div>
  );
}

// ===========================================================================
// ATOM renderers
// ===========================================================================
function AtomIconThumb({ type, width, height }) {
  const name = type.defaults?.name || type.icon || 'star';
  return (
    <div className="cv-thumb-atom-icon" style={{ width, height }}>
      <div className="ring">
        <CvIcon name={name} size={Math.min(width, height) * 0.45} tone="bronze"/>
      </div>
    </div>
  );
}
function AtomStatusThumb({ type, width, height }) {
  return (
    <div className="cv-thumb-atom-status" style={{ width, height }}>
      <span className="dot ok"/>
      <span className="dot warn"/>
      <span className="dot info"/>
      <span className="dot err"/>
    </div>
  );
}
function AtomShapeThumb({ type, width, height }) {
  const shape = type.defaults?.shape || 'circle';
  return (
    <div className="cv-thumb-atom-shape" style={{ width, height }}>
      <RenderShape shape={shape} size={Math.min(width, height) * 0.55}/>
    </div>
  );
}
function AtomStampThumb({ type, width, height }) {
  return (
    <div className="cv-thumb-atom-stamp" style={{ width, height }}>
      <span className="stamp">{(type.defaults?.text || 'STAMP').toUpperCase()}</span>
    </div>
  );
}

// ===========================================================================
// BLOCK renderer — content blocks render THROUGH THE ONE ENGINE (UNIFICATION
// W3): block Type → RenderType → typeToNode(blockToNode) → solvers. Cross-doc
// embeds (widget/wizard) keep their own engine (WidgetRender). Gated on
// window.__coreReady (readiness, not a fallback).
// ===========================================================================
function BlockThumb({ type, width, height }) {
  const key = type.runtime?.key || type.id.split('.').pop();
  const isEmbed = key === 'embedWidget' || key === 'embedWizard';
  const [ready, setReady] = useState_th(typeof window !== 'undefined' && !!window.__cvRenderType);
  useEffect_th(() => {
    if (ready || isEmbed) return;
    let on = true;
    (window.__coreReady || Promise.resolve()).then(() => { if (on) setReady(!!window.__cvRenderType); });
    return () => { on = false; };
  }, [ready]);
  const def = window.WS_BLOCKS?.[key];
  const data = useMemo_th(() => ({ ...(def?.defaults || {}), ...(type.defaults || {}) }), [key, type.id]);
  const RT = typeof window !== 'undefined' && window.__cvRenderType;

  if (!isEmbed && ready && RT) {
    return (
      <ScaledThumb native={{ w: 760, h: 440 }} width={width} height={height} pad={10} bg="var(--zone-ground)">
        {React.createElement(RT, { type: { id: 'block.' + key, layer: 'block', family: 'block', runtime: { kind: 'core-block', key } }, data, lod: 'full', surface: 'web', density: 'compact' })}
      </ScaledThumb>
    );
  }
  // cross-doc embeds → the widget/wizard engine
  if (!def?.render) return <ThumbPlaceholder width={width} height={height} label={type.name}/>;
  return (
    <ScaledThumb native={{ w: 600, h: 380 }} width={width} height={height} pad={8} bg="var(--bg-surface)">
      <div className="cv-thumb-block-host">
        {def.render(data, () => {})}
      </div>
    </ScaledThumb>
  );
}

// ===========================================================================
// SYSTEM renderers — widget composition rules
// ===========================================================================
const MOCK_WIDGET_DOC = {
  data: {
    eyebrow: 'Tower East',
    title: 'Performance',
    kpis: [
      { label: 'Occupancy', value: '94%', delta: '+3.2pt', deltaKind: 'up' },
      { label: 'Linked hubs', value: '128', delta: '+12', deltaKind: 'up' },
      { label: 'Captures', value: '276', delta: '+18', deltaKind: 'up' },
    ],
    rows: [
      { label: '2 bed', value: '14 of 22', status: 'ok' },
      { label: '1 bed', value: '8 of 14', status: 'ok' },
      { label: 'Studio', value: '3 of 6', status: 'warn' },
    ],
    media: { kind: 'placeholder', label: 'Tower East · hero render', tone: 'gold' },
    chart: { kind: 'spark', points: [12,14,13,18,22,19,25,28,26,32,30,36,40], label: 'Captures · 13w' },
    cta: { label: 'Open hub', href: 'conceptv.io/tower-east' },
  },
  coBrand: false,
};

function SystemWidgetThumb({ type, width, height }) {
  // widget system → a Zone tile rendered THROUGH THE ENGINE (UNIFICATION W3 +
  // REQUIREMENTS F2: product UI = containment tree). Charts/deltas are
  // placeholders pending a dataviz atom (W7). Gated on __coreReady.
  const systemKey = type.runtime?.key || type.id.split('.').pop();
  const [ready, setReady] = useState_th(typeof window !== 'undefined' && !!window.__cvRenderType);
  useEffect_th(() => {
    if (ready) return; let on = true;
    (window.__coreReady || Promise.resolve()).then(() => { if (on) setReady(!!window.__cvRenderType); });
    return () => { on = false; };
  }, [ready]);
  const doc = { ...MOCK_WIDGET_DOC, widgetKind: 'dashboard', system: systemKey };
  const RT = typeof window !== 'undefined' && window.__cvRenderType;
  if (ready && RT) {
    return (
      <ScaledThumb native={{ w: 360, h: 260 }} width={width} height={height} pad={6} bg="var(--zone-ground)">
        {React.createElement(RT, { type: { layer: 'system', family: 'widget', runtime: { kind: 'widget-system', key: systemKey } }, data: doc, lod: 'full', surface: 'web', density: 'compact' })}
      </ScaledThumb>
    );
  }
  const WR = window.WidgetRender;
  if (!WR) return <ThumbPlaceholder width={width} height={height} label={type.name}/>;
  return (
    <ScaledThumb native={{ w: 320, h: 220 }} width={width} height={height} pad={6}>
      <WR doc={doc} hovered={false}/>
    </ScaledThumb>
  );
}
function SystemGenericThumb({ type, width, height }) {
  const slots = Object.entries(type.slots || {});
  return (
    <div className="cv-thumb-system-generic" style={{ width, height }}>
      <strong>{type.name}</strong>
      <div className="slots">
        {slots.length === 0 && <em>No slots</em>}
        {slots.map(([k, s]) => (
          <div key={k} className="slot">
            <span className="lbl">{s.label || k}</span>
            <span className="acc">{(s.accepts?.layers || []).join('·')}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ===========================================================================
// SURFACE renderers
// ===========================================================================
function SurfaceWidgetThumb({ type, width, height }) {
  const widgetKey = type.runtime?.key || type.id.split('.').pop(); // dashboard/hub/embed
  const WR = window.WidgetRender;
  if (!WR) return <ThumbPlaceholder width={width} height={height} label={type.name}/>;
  // Pick a default system for the preview
  const doc = { ...MOCK_WIDGET_DOC, widgetKind: widgetKey, system: 'hybrid' };

  return (
    <div className="cv-thumb-surface-widget" style={{ width, height }}>
      <SurfaceWidgetFrame kind={widgetKey} width={width} height={height} WR={WR} doc={doc}/>
    </div>
  );
}

function SurfaceWidgetFrame({ kind, width, height, WR, doc }) {
  if (kind === 'dashboard') {
    return (
      <div className="ctx-dash">
        <div className="rail">
          <span className="d"/><span className="d"/><span className="d"/><span className="d"/>
        </div>
        <div className="grid">
          <div className="mute"/><div className="mute"/>
          <div className="cell">
            <ScaledThumb native={{ w: 320, h: 220 }} width={Math.round((width-46)/3)} height={Math.round((height-22)/2)} pad={0}>
              <WR doc={doc} hovered={false}/>
            </ScaledThumb>
          </div>
          <div className="mute"/><div className="mute"/><div className="mute"/>
        </div>
      </div>
    );
  }
  if (kind === 'hub') {
    return (
      <div className="ctx-hub">
        <div className="topbar"><span className="brand"/><span className="url"/></div>
        <div className="hero"/>
        <div className="row">
          <ScaledThumb native={{ w: 480, h: 320 }} width={Math.round(width * 0.5)} height={Math.round(height * 0.5)} pad={0}>
            <WR doc={{ ...doc, widgetKind: 'hub' }} hovered={false}/>
          </ScaledThumb>
          <div className="aside"><span/><span/><span/></div>
        </div>
      </div>
    );
  }
  // embed
  return (
    <div className="ctx-embed">
      <div className="lines"><span style={{width:'70%'}}/><span style={{width:'50%'}}/></div>
      <ScaledThumb native={{ w: 380, h: 260 }} width={Math.round(width * 0.8)} height={Math.round(height * 0.55)} pad={0}>
        <WR doc={{ ...doc, widgetKind: 'embed' }} hovered={false}/>
      </ScaledThumb>
      <div className="lines"><span style={{width:'90%'}}/><span style={{width:'60%'}}/></div>
    </div>
  );
}

function SurfaceWizardStepThumb({ type, width, height }) {
  const stepKind = type.defaults?.kind || type.runtime?.key || 'form';
  return (
    <div className="cv-thumb-surface-step" style={{ width, height }}>
      <div className="step-frame">
        <div className="head">
          <span className="eyebrow">Step 2 of 5</span>
          <strong>{type.name}</strong>
        </div>
        <div className="body">
          <StepBodyPreview kind={stepKind}/>
        </div>
        <div className="foot">
          <span className="back">← Back</span>
          <span className="cta">Continue →</span>
        </div>
      </div>
    </div>
  );
}

function StepBodyPreview({ kind }) {
  if (kind === 'capture') return (
    <div className="step-capture">
      <div className="dz">⤓<span>Drop files</span></div>
    </div>
  );
  if (kind === 'choice') return (
    <div className="step-choice">
      <div className="opt picked">●  Option A</div>
      <div className="opt">○  Option B</div>
      <div className="opt">○  Option C</div>
    </div>
  );
  if (kind === 'review') return (
    <div className="step-review">
      <div className="row"><span>Property</span><span>Tower East</span></div>
      <div className="row"><span>Beds</span><span>2</span></div>
      <div className="row"><span>Audience</span><span>Investors</span></div>
    </div>
  );
  if (kind === 'celebrate') return (
    <div className="step-celebrate">
      <div className="big">✓</div>
      <div className="lbl">Done</div>
    </div>
  );
  // form (default)
  return (
    <div className="step-form">
      <div className="field"><span className="lbl">Full name</span><span className="input"/></div>
      <div className="field"><span className="lbl">Email</span><span className="input"/></div>
      <div className="field"><span className="lbl">Role</span><span className="input"/></div>
    </div>
  );
}

// Renders a deck-slide Type THROUGH THE ONE ENGINE (UNIFICATION W3): the same
// RenderType → solvers path the templates use. No hand-drawn mock — the preview
// IS the engine output, so a built-in OR Vi-proposed archetype previews from one
// source of truth. Gated on window.__coreReady (async core load), not a fallback.
function SurfaceSlideThumb({ type, width, height }) {
  const [ready, setReady] = useState_th(typeof window !== 'undefined' && !!window.__cvRenderType);
  useEffect_th(() => {
    if (ready) return;
    let on = true;
    (window.__coreReady || Promise.resolve()).then(() => { if (on) setReady(!!window.__cvRenderType); });
    return () => { on = false; };
  }, [ready]);
  const RT = typeof window !== 'undefined' && window.__cvRenderType;
  if (!ready || !RT) return <ThumbPlaceholder width={width} height={height} label={type.name}/>;
  const data = (type.defaults && Object.keys(type.defaults).length) ? type.defaults : undefined;
  return (
    <ScaledThumb native={{ w: 1280, h: 720 }} width={width} height={height} pad={0} bg="var(--zone-ground)">
      {React.createElement(RT, { type, data, lod: 'pitch', surface: 'slide', density: 'compact' })}
    </ScaledThumb>
  );
}

function SurfaceGenericThumb({ type, width, height }) {
  return (
    <div className="cv-thumb-surface-generic" style={{ width, height }}>
      <div className="chrome">
        <span className="d"/><span className="d"/><span className="d"/>
        <span className="title">{type.name}</span>
      </div>
      <div className="body">
        {Object.keys(type.slots || {}).map(k => <div key={k} className="slot">{type.slots[k].label || k}</div>)}
      </div>
    </div>
  );
}

// ===========================================================================
// DOC renderers
// ===========================================================================
function DocWidgetThumb({ type, width, height }) {
  // doc.widget shows the dashboard chrome with a sample widget inside
  return <SurfaceWidgetThumb type={{ ...type, runtime: { kind: 'widget-kind', key: 'dashboard' } }} width={width} height={height}/>;
}

function DocWizardThumb({ type, width, height }) {
  // Mini wizard: sidebar with numbered steps + a content area
  const shape = type.tags?.includes('hexagon') ? 'hexagon'
              : type.tags?.includes('circle')   ? 'circle'
              : type.tags?.includes('octagon')  ? 'octagon'
              : 'diamond';
  // Resolve steps: explicit defaults > legacy WIZARD_KINDS lookup > fallback
  let steps = type.defaults?.steps;
  if (!Array.isArray(steps) || !steps.length) {
    const key = type.runtime?.key || type.defaults?.wizardKind;
    const legacy = (window.WIZARD_KINDS || []).find(k => k.id === key);
    if (legacy?.steps) steps = legacy.steps;
  }
  if (!Array.isArray(steps) || !steps.length) {
    steps = [
      { title: 'Capture' }, { title: 'Enrich' }, { title: 'Audience' }, { title: 'Review' }, { title: 'Publish' },
    ];
  }
  const shown = steps.slice(0, 5);
  return (
    <div className="cv-thumb-doc-wizard" style={{ width, height }}>
      <div className="rail">
        <div className="brand">
          <RenderShape shape={shape} size={14}/>
          <span>ConceptV</span>
        </div>
        <ol>
          {shown.map((s, i) => (
            <li key={i} className={i === 1 ? 'active' : i === 0 ? 'done' : ''}>
              <span className="dot">{i === 0 ? '' : i + 1}</span>
              <span className="lbl">{s.title || s.label || `Step ${i + 1}`}</span>
            </li>
          ))}
        </ol>
      </div>
      <div className="stage">
        <div className="eyebrow">Step 2 of {shown.length}</div>
        <div className="h"/>
        <div className="line w90"/><div className="line w70"/>
        <div className="field"/><div className="field"/>
        <div className="cta"/>
      </div>
    </div>
  );
}

function DocDeckThumb({ type, width, height }) {
  // The deck preview is its FIRST slide rendered THROUGH THE ENGINE (UNIFICATION
  // W3, doc level) on a stacked-card affordance — sample slides single-sourced
  // from the archetype catalogue (doc.deck defaults). Gated on __coreReady.
  const [ready, setReady] = useState_th(typeof window !== 'undefined' && !!window.__cvRenderType);
  useEffect_th(() => {
    if (ready) return; let on = true;
    (window.__coreReady || Promise.resolve()).then(() => { if (on) setReady(!!window.__cvRenderType); });
    return () => { on = false; };
  }, [ready]);
  const slides = type.defaults?.slides || [];
  const RT = typeof window !== 'undefined' && window.__cvRenderType;
  const hh = height || Math.round(width * 0.66);
  if (ready && RT && slides.length) {
    const first = slides[0];
    return (
      <div className="cv-thumb-doc-deck" style={{ width, height: hh, position: 'relative' }}>
        <div style={{ position: 'absolute', left: 10, top: 10, right: 2, bottom: 2, borderRadius: 6, background: 'var(--zone-ground)', boxShadow: 'var(--elev-1)' }}/>
        <div style={{ position: 'absolute', left: 5, top: 5, right: 5, bottom: 5, borderRadius: 6, background: 'var(--zone-ground)', boxShadow: 'var(--elev-1)' }}/>
        <div style={{ position: 'absolute', left: 0, top: 0, right: 10, bottom: 10, borderRadius: 6, overflow: 'hidden', boxShadow: 'var(--elev-2)', border: '1px solid var(--zone-base-edge)' }}>
          <ScaledThumb native={{ w: 1280, h: 720 }} width={width - 10} height={hh - 10} pad={0} bg="var(--zone-ground)">
            {React.createElement(RT, { type: { layer: 'surface', family: 'deck-slide', runtime: { kind: 'core-archetype', key: first.archetype } }, data: first.content, lod: 'pitch', surface: 'slide', density: 'compact' })}
          </ScaledThumb>
        </div>
      </div>
    );
  }
  return (
    <div className="cv-thumb-doc-deck" style={{ width, height: hh }}>
      {[0, 1, 2, 3].map(i => (
        <div key={i} className="slide" style={{ zIndex: 4 - i, transform: `translate(${i * 6}px, ${i * 5}px)` }}/>
      ))}
    </div>
  );
}

function DocBrochureThumb({ type, width, height }) {
  // brochure preview = its first sample slide through the engine (UNIFICATION W3)
  const [ready, setReady] = useState_th(typeof window !== 'undefined' && !!window.__cvRenderType);
  useEffect_th(() => {
    if (ready) return; let on = true;
    (window.__coreReady || Promise.resolve()).then(() => { if (on) setReady(!!window.__cvRenderType); });
    return () => { on = false; };
  }, [ready]);
  const slides = type.defaults?.slides || [];
  const RT = typeof window !== 'undefined' && window.__cvRenderType;
  const hh = height || Math.round(width * 0.66);
  if (ready && RT && slides.length) {
    const first = slides[0];
    return (
      <div className="cv-thumb-doc-brochure" style={{ width, height: hh }}>
        <ScaledThumb native={{ w: 794, h: 1123 }} width={width} height={hh} pad={6} align="top" bg="var(--zone-ground)">
          {React.createElement(RT, { type: { layer: 'surface', family: 'deck-slide', runtime: { kind: 'core-archetype', key: first.archetype } }, data: first.content, lod: 'pitch', surface: 'print', density: 'compact' })}
        </ScaledThumb>
      </div>
    );
  }
  return (
    <div className="cv-thumb-doc-brochure" style={{ width, height: hh }}>
      <div className="sheet">
        <div className="head"><span className="brand"/><span className="contact"/></div>
        <div className="hero"/>
        <div className="cols">
          <div className="col"><span/><span/><span style={{width:'70%'}}/></div>
          <div className="col"><span/><span style={{width:'80%'}}/><span/></div>
        </div>
        <div className="cta"/>
      </div>
    </div>
  );
}

function DocGenericThumb({ type, width, height }) {
  return (
    <div className="cv-thumb-doc-generic" style={{ width, height }}>
      <div className="card">
        <CvIcon name={type.icon || 'browser'} size={28} tone="bronze"/>
        <strong>{type.name}</strong>
        <span>{type.family} doc</span>
      </div>
    </div>
  );
}

// ===========================================================================
// TEMPLATE renderer — fallback to parent thumb + variable badge
// ===========================================================================
function TemplateThumb({ type, width, height }) {
  const R = window.CV_REGISTRY;
  const parent = type.extends ? R?.get(type.extends) : null;
  return (
    <div className="cv-thumb-template" style={{ width, height }}>
      {parent ? <TypeThumb type={parent} width={width} height={height}/> : <DocGenericThumb type={type} width={width} height={height}/>}
      <span className="vars-badge">𝓋 {(type.variables || []).length}</span>
    </div>
  );
}

// ===========================================================================
// Shape helper
// ===========================================================================
function RenderShape({ shape, size = 28 }) {
  const s = size;
  const stroke = 'var(--accent-gold)';
  const fill = 'var(--accent-gold-soft)';
  if (shape === 'hexagon') {
    const r = s / 2 - 1; const cx = s / 2; const cy = s / 2;
    const pts = [];
    for (let i = 0; i < 6; i++) {
      const a = Math.PI / 6 + i * Math.PI / 3;
      pts.push(`${(cx + r * Math.cos(a)).toFixed(2)},${(cy + r * Math.sin(a)).toFixed(2)}`);
    }
    return <svg width={s} height={s} viewBox={`0 0 ${s} ${s}`}><polygon points={pts.join(' ')} fill={fill} stroke={stroke} strokeWidth="1.5"/></svg>;
  }
  if (shape === 'octagon') {
    const r = s / 2 - 1; const cx = s / 2; const cy = s / 2;
    const pts = [];
    for (let i = 0; i < 8; i++) {
      const a = Math.PI / 8 + i * Math.PI / 4;
      pts.push(`${(cx + r * Math.cos(a)).toFixed(2)},${(cy + r * Math.sin(a)).toFixed(2)}`);
    }
    return <svg width={s} height={s} viewBox={`0 0 ${s} ${s}`}><polygon points={pts.join(' ')} fill={fill} stroke={stroke} strokeWidth="1.5"/></svg>;
  }
  if (shape === 'diamond') {
    return <svg width={s} height={s} viewBox={`0 0 ${s} ${s}`}>
      <polygon points={`${s/2},1 ${s-1},${s/2} ${s/2},${s-1} 1,${s/2}`} fill="none" stroke={stroke} strokeWidth="1.5"/>
      <g stroke={stroke} strokeWidth="0.5" opacity="0.5">
        <line x1={s/2} y1="1" x2={s/2} y2={s-1}/>
        <line x1="1" y1={s/2} x2={s-1} y2={s/2}/>
      </g>
    </svg>;
  }
  // circle
  return <svg width={s} height={s} viewBox={`0 0 ${s} ${s}`}><circle cx={s/2} cy={s/2} r={s/2 - 1} fill={fill} stroke={stroke} strokeWidth="1.5"/></svg>;
}

function isLightHex(h) {
  if (!h?.startsWith('#')) return true;
  const hex = h.length === 4 ? h.replace(/^#(.)(.)(.)/, '#$1$1$2$2$3$3') : h;
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return (r * 299 + g * 587 + b * 114) / 1000 > 150;
}

Object.assign(window, {
  TypeThumb, ScaledThumb, RenderShape, ThumbPlaceholder,
});
