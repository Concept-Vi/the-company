// app/canvases/Architecture.jsx
// Architecture canvas — an explanation of how the Universal Type Registry
// works. Diagrams, layer overview, composition examples, lineage examples,
// and how each existing surface consumes the registry.

const { useState: useState_arch, useMemo: useMemo_arch, useEffect: useEffect_arch } = React;

function Architecture({ onNav, onOpenBuilder }) {
  const R = window.CV_REGISTRY;
  const [tick, setTick] = useState_arch(0);
  useEffect_arch(() => R?.subscribe(() => setTick(t => t + 1)), []);
  const counts = useMemo_arch(() => {
    const m = {};
    for (const t of (R?.all() || [])) m[t.layer] = (m[t.layer] || 0) + 1;
    return m;
  }, [tick]);

  return (
    <>
      <CanvasHeader
        title="Architecture"
        sub="How the universal Type Registry stitches every surface together — one composition substrate for the whole product."
        actions={<>
          <button className="dsa-btn dsa-btn--outline" onClick={() => onNav?.('registry')}>Open Registry →</button>
          <button className="dsa-btn dsa-btn--ai" onClick={() => onOpenBuilder?.()}><ViShape size={12}/> + New Type</button>
        </>}
      />
      <div className="dsa-canvas-body cv-arch-body">

        <SectionIntro/>

        <Section title="The seven layers" sub="Atomic composition — every Type lives at exactly one layer. Lower layers compose into higher ones; higher Types EMBED lower ones via slots.">
          <LayerLadder counts={counts} onLayerClick={() => onNav?.('registry')}/>
        </Section>

        <Section title="Composition by slots" sub="A Type declares named slots; each slot lists the layers, families, and tags it accepts. The registry validates fills automatically.">
          <SlotExample/>
        </Section>

        <Section title="Inheritance — extends, never duplicates" sub="A Type extends one parent and inherits its slots, defaults, and variables. Overrides cascade leaf → root.">
          <LineageExample/>
        </Section>

        <Section title="Types vs Templates" sub="A Type is the schema. A Template is a runnable instance with variables extracted. Same registry, different layer.">
          <TypesVsTemplates onNav={onNav}/>
        </Section>

        <Section title="What consumes the registry" sub="Every surface in the app reads from one source. Add a Type once and it shows up in every consumer.">
          <ConsumersMatrix onNav={onNav}/>
        </Section>

        <Section title="Where new Types come from" sub="Four entry points, one registry. All four produce the same kind of node.">
          <EntryPoints onOpenBuilder={onOpenBuilder} onNav={onNav}/>
        </Section>

        <Section title="Cross-system embedding" sub="A widget Type can appear as a slide block. A wizard step can render a widget. Same protocol, no special cases.">
          <CrossEmbedDiagram/>
        </Section>

      </div>
    </>
  );
}

// ===========================================================================
// Intro panel
// ===========================================================================
function SectionIntro() {
  return (
    <div className="cv-arch-intro">
      <div className="cv-arch-intro-head">
        <ViShape size={26}/>
        <h2>One registry. Every composable thing.</h2>
      </div>
      <p>ConceptV Studio used to ship hard-coded widget kinds, wizard kinds, and slide blocks — three parallel systems with their own pickers. The new universal architecture turns every one of those into a single shape: a <strong>Type</strong> at a specific <strong>layer</strong>. Types extend Types. Types embed Types. Vi can create them in-place from any context.</p>
      <p>That means a custom widget System the user invents in the Workshop today is the same kind of node as a Wizard kind the team ships next week — both live in the registry, both can be queried, embedded, extended, and saved as Templates.</p>
    </div>
  );
}

// ===========================================================================
// Section wrapper
// ===========================================================================
function Section({ title, sub, children }) {
  return (
    <section className="cv-arch-section">
      <header>
        <h3>{title}</h3>
        {sub && <p>{sub}</p>}
      </header>
      {children}
    </section>
  );
}

// ===========================================================================
// Layer ladder — vertical bar with counts + example thumb
// ===========================================================================
function LayerLadder({ counts, onLayerClick }) {
  const R = window.CV_REGISTRY;
  return (
    <div className="cv-arch-ladder">
      {[...(R?.LAYERS || [])].reverse().map(l => {
        const info = R.LAYER_INFO[l];
        const example = R.query({ layer: l })[0];
        return (
          <button key={l} className="cv-arch-rung" onClick={onLayerClick}>
            <div className="rank">L{info.rank}</div>
            <div className="bar" style={{ background: info.swatch }}/>
            <div className="meta">
              <div className="name">{info.label}</div>
              <div className="desc">{info.desc}</div>
            </div>
            <div className="example">
              {example && window.TypeThumb && <TypeThumb type={example} width={150} height={94} dense/>}
            </div>
            <div className="count">{counts[l] || 0}</div>
          </button>
        );
      })}
    </div>
  );
}

// ===========================================================================
// Slot example — visualize a System with slots, schema, and a live preview
// ===========================================================================
function SlotExample() {
  const R = window.CV_REGISTRY;
  const t = R?.get('system.widget.hybrid');
  if (!t) return null;
  return (
    <div className="cv-arch-slot-ex">
      <div className="schema">
        <div className="schema-head">
          <span className="bracket">{`{`}</span>
          <code className="key">"id"</code>: <code className="str">"{t.id}"</code>,
        </div>
        <div className="schema-row">
          <code className="key">"slots"</code>: <span className="bracket">{`{`}</span>
        </div>
        {Object.entries(t.slots).map(([k, s]) => (
          <div key={k} className="schema-slot">
            <code className="key">"{k}"</code>: <span className="bracket">{`{`}</span>
              <code className="key">"accepts"</code>: <span className="hint">{describeAccepts(s.accepts)}</span>
              {s.multiple && <span className="badge">multiple</span>}
              {s.optional && <span className="badge">optional</span>}
            <span className="bracket">{`},`}</span>
          </div>
        ))}
        <div className="schema-row">
          <span className="bracket">{`}`}</span>
        </div>
        <div className="schema-row">
          <span className="bracket">{`}`}</span>
        </div>
      </div>
      <div className="visual">
        <div className="visual-head">
          <strong>{t.name}</strong>
          <TypeLayerBadge layer={t.layer} size="md"/>
          <span style={{marginLeft:'auto',font:'400 11px/1.4 var(--font-body)',color:'var(--fg-muted)'}}>rendered with sample data →</span>
        </div>
        {window.TypeThumb && <TypeThumb type={t} width={360} height={220}/>}
        <div className="visual-slots">
          {Object.entries(t.slots).map(([k, s]) => (
            <div key={k} className={`vslot ${s.multiple ? 'multi' : ''} ${s.optional ? 'opt' : ''}`}>
              <span className="lbl">{s.label || k}</span>
              <span className="hint">{describeAccepts(s.accepts)}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function describeAccepts(acc = {}) {
  const parts = [];
  if (acc.layers?.length)   parts.push(acc.layers.join('|'));
  if (acc.families?.length) parts.push('family:' + acc.families.join('|'));
  if (acc.tags?.length)     parts.push('tag:' + acc.tags.join('|'));
  return parts.join(' · ') || 'any';
}

// ===========================================================================
// Lineage example — wizard kinds extending doc.wizard
// ===========================================================================
function LineageExample() {
  const R = window.CV_REGISTRY;
  const root = R?.get('doc.wizard');
  const kids = R?.descendants('doc.wizard') || [];
  if (!root) return null;
  return (
    <div className="cv-arch-lineage">
      <div className="root">
        <TypeCard type={root}/>
      </div>
      <div className="connector"/>
      <div className="children">
        {kids.map(k => (
          <div key={k.id} className="child">
            <TypeCard type={k} lineage/>
          </div>
        ))}
      </div>
      <p className="caption">
        Each child wizard kind <strong>inherits</strong> the steps slot, the {`{ type, layout, mode }`} defaults,
        and the brand voice. It only overrides the <code>wizardKind</code> field and its tags. New custom flows
        plug in the same way.
      </p>
    </div>
  );
}

// ===========================================================================
// Types vs Templates
// ===========================================================================
function TypesVsTemplates({ onNav }) {
  const R = window.CV_REGISTRY;
  const docType = R?.get('doc.widget');
  return (
    <div className="cv-arch-types-templates">
      <div className="col">
        <h4><TypeLayerBadge layer="doc" size="lg"/> Type</h4>
        <p>A schema — slots, defaults, variables. <em>Doesn't</em> hold instance data.</p>
        {docType && window.TypeThumb && (
          <div className="tt-preview">
            <TypeThumb type={docType} width={300} height={180}/>
            <span className="tt-label">{docType.name}</span>
          </div>
        )}
      </div>
      <div className="arrow">+ variables →</div>
      <div className="col">
        <h4><TypeLayerBadge layer="template" size="lg"/> Template</h4>
        <p>An instance frozen with extracted parameters — runnable to produce a fresh doc.</p>
        {docType && window.TypeThumb && (
          <div className="tt-preview">
            <div style={{position:'relative'}}>
              <TypeThumb type={docType} width={300} height={180}/>
              <span className="vars-badge" style={{position:'absolute',top:8,right:8,background:'var(--accent-gold)',color:'var(--fg-primary)',padding:'4px 8px',borderRadius:999,font:'700 10px/1 var(--font-mono)',boxShadow:'0 1px 3px rgba(0,0,0,0.15)'}}>𝓋 3 variables</span>
            </div>
            <span className="tt-label">Tower East · capture template</span>
          </div>
        )}
      </div>
      <div className="footer">
        <button className="dsa-btn dsa-btn--outline" onClick={() => onNav?.('templates')}>Open Templates →</button>
      </div>
    </div>
  );
}

// ===========================================================================
// Consumers — what reads from the registry
// ===========================================================================
function ConsumersMatrix({ onNav }) {
  const rows = [
    { name: 'Workshop landing',      reads: 'doc-layer Types (all families)',          consumes: 'docs', cta: 'workshop' },
    { name: 'Widget Builder',        reads: 'surface · family=widget + system · family=widget', consumes: 'kinds, systems', cta: 'workshop' },
    { name: 'Wizard Builder',        reads: 'doc.wizard children + surface · family=wizard-step', consumes: 'kinds, step kinds', cta: 'workshop' },
    { name: 'Slide library',         reads: 'block-layer Types',                       consumes: 'blocks', cta: 'workshop' },
    { name: 'Templates canvas',      reads: 'template-layer Types',                    consumes: 'templates', cta: 'templates' },
    { name: 'Build canvas',          reads: 'doc-layer Types + new type-builder',       consumes: 'all', cta: 'build' },
    { name: 'Vi chat',               reads: 'every Type in scope for context',         consumes: 'all', cta: null },
  ];
  return (
    <table className="cv-arch-consumers">
      <thead><tr><th>Surface</th><th>Reads from registry</th><th>Consumes</th><th/></tr></thead>
      <tbody>
        {rows.map(r => (
          <tr key={r.name}>
            <td><strong>{r.name}</strong></td>
            <td className="mono">{r.reads}</td>
            <td>{r.consumes}</td>
            <td>{r.cta && <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => onNav?.(r.cta)}>Open →</button>}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// ===========================================================================
// Entry points — four ways Types get created
// ===========================================================================
function EntryPoints({ onOpenBuilder, onNav }) {
  const items = [
    { tag: 'In-context', title: 'From an instance', desc: 'Press "Save as Type" inside any builder — Vi extracts variables and registers the schema.', cta: () => onNav?.('workshop') },
    { tag: 'In-context', title: 'From a brief',     desc: 'Inside Workshop or Build, describe what you want and choose "make this a new Type" — Vi proposes the schema.', cta: () => onOpenBuilder?.() },
    { tag: 'Standalone', title: 'In the Builder',   desc: 'Open the Type Builder, pick a layer + parent, author slots and defaults from scratch.', cta: () => onOpenBuilder?.() },
    { tag: 'Plan-level', title: 'In Build',         desc: 'Vi can include a "create Type" subtask in a multi-stage plan — the new Type registers as it runs.', cta: () => onNav?.('build') },
  ];
  return (
    <div className="cv-arch-entry-grid">
      {items.map((e, i) => (
        <div key={i} className="cv-arch-entry">
          <span className="tag">{e.tag}</span>
          <h4>{e.title}</h4>
          <p>{e.desc}</p>
          <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={e.cta}>Open →</button>
        </div>
      ))}
    </div>
  );
}

// ===========================================================================
// Cross-embedding diagram — real type thumbs, not text cards
// ===========================================================================
function CrossEmbedDiagram() {
  const R = window.CV_REGISTRY;
  const steps = [
    { type: R?.get('doc.deck'), slotLbl: 'slot: slides[ surface ]' },
    { type: R?.get('surface.deck-slide.content'), slotLbl: 'slot: sections[ block ]' },
    { type: R?.get('block.callout'), slotLbl: 'or any block — including a widget embed', highlight: true },
    { type: R?.get('doc.widget'), slotLbl: 'a full widget doc, embedded' },
  ];
  return (
    <div className="cv-arch-xembed">
      <div className="row">
        {steps.map((s, i) => s.type ? (
          <React.Fragment key={i}>
            <div className={`xembed-card ${s.highlight ? 'highlight' : ''}`}>
              <div className="thumb">
                {window.TypeThumb && <TypeThumb type={s.type} width={180} height={112}/>}
              </div>
              <div className="meta">
                <strong>{s.type.name}</strong>
                <TypeLayerBadge layer={s.type.layer} size="sm"/>
                <em>{s.slotLbl}</em>
              </div>
            </div>
            {i < steps.length - 1 && <div className="xembed-arrow">embeds<br/>↓</div>}
          </React.Fragment>
        ) : null)}
      </div>
      <p className="caption">
        Any Type can be embedded in any slot that accepts its layer/family/tags. Cycles are prevented by the
        registry. Cross-family embedding — widget inside slide, wizard step inside brochure — works the same way.
      </p>
    </div>
  );
}

window.Architecture = Architecture;
