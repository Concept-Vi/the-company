// app/registry/types-seed.js
// Seed the Registry with built-in Types that mirror existing surfaces.
// Every WIDGET_KIND, WIDGET_SYSTEM, WIZARD_KIND, STEP_KIND, and BLOCK
// becomes a first-class Type so consumers can read from one source of truth.
//
// New user/Vi-authored Types that extend these will live alongside in the
// same query — `query({ layer:'system', family:'widget' })` returns the
// built-in kpi/media/hybrid *and* any user-added systems.

(function () {
  const R = window.CV_REGISTRY;
  if (!R) { console.error('[seed] CV_REGISTRY missing'); return; }

  const now = Date.now();
  const builtIn = (t) => ({ provenance: 'built-in', createdAt: now, updatedAt: now, ...t });

  // =========================================================================
  // Layer: TOKEN — design primitives. Stubs that point to existing canvases.
  // =========================================================================
  const tokens = [
    { id: 'token.color.gold',    name: 'Gold accent',  layer: 'token', family: 'color', icon: 'color-swatches', description: 'The brand\'s single loud colour. Used for primary actions, active borders, link emphasis.', defaults: { hex: '#E0C010' }, axis: 'color', axisValue: 'gold', tags: ['color', 'accent'] },
    { id: 'token.color.bronze',  name: 'Bronze',       layer: 'token', family: 'color', icon: 'color-swatches', description: 'Line-drawn illustrations and screen titles.', defaults: { hex: '#988058' }, axis: 'color', axisValue: 'bronze', tags: ['color'] },
    { id: 'token.color.ink',     name: 'Ink',          layer: 'token', family: 'color', icon: 'color-swatches', description: 'Near-black with a warm undertone.', defaults: { hex: '#1F1A12' }, axis: 'color', axisValue: 'ink', tags: ['color'] },
    { id: 'token.color.canvas',  name: 'Canvas',       layer: 'token', family: 'color', icon: 'color-swatches', description: 'Slightly-warm ivory page background.', defaults: { hex: '#FBF7EC' }, axis: 'color', axisValue: 'paper', tags: ['color'] },
    { id: 'token.type.display',  name: 'Display',      layer: 'token', family: 'type',  icon: 'document', description: 'Sora 700, tight tracking.', defaults: { family: 'Sora', weight: 700 }, tags: ['type'] },
    { id: 'token.type.body',     name: 'Body',         layer: 'token', family: 'type',  icon: 'document', description: 'DM Sans 400/500.', defaults: { family: 'DM Sans', weight: 400 }, tags: ['type'] },
    { id: 'token.type.mono',     name: 'Mono',         layer: 'token', family: 'type',  icon: 'document', description: 'JetBrains Mono for URLs/IDs/code.', defaults: { family: 'JetBrains Mono', weight: 500 }, tags: ['type'] },
    { id: 'token.shape.circle',  name: 'Circle',       layer: 'token', family: 'shape', icon: 'browser-house', description: 'User Portal shape.', defaults: { sides: 0 }, axis: 'form', axisValue: 'circle', tags: ['shape', 'entity'] },
    { id: 'token.shape.hexagon', name: 'Hexagon',      layer: 'token', family: 'shape', icon: 'atom', description: 'Property Wizard shape.', defaults: { sides: 6 }, axis: 'form', axisValue: 'hex', tags: ['shape', 'entity'] },
    { id: 'token.shape.octagon', name: 'Octagon',      layer: 'token', family: 'shape', icon: 'check-square', description: 'Virtual Hub shape.', defaults: { sides: 8 }, axis: 'form', axisValue: 'octagon', tags: ['shape', 'entity'] },
    { id: 'token.shape.diamond', name: 'Diamond',      layer: 'token', family: 'shape', icon: 'atom', description: 'Vi (AI framework) shape.', defaults: { sides: 4 }, axis: 'form', axisValue: 'diamond', tags: ['shape', 'entity'] },
  ];

  // =========================================================================
  // Layer: ATOM — single visual units (icons + status dots)
  // The full icon library is already in CV_ICONS — here we register a parent
  // Type that the icon library is a child of, and a few representative atoms.
  // =========================================================================
  const atoms = [
    { id: 'atom.icon',           name: 'Icon',         layer: 'atom', family: 'icon',   icon: 'star',  description: 'Any glyph from the CV icon library. 24×24, 1.5 px stroke, currentColor.', defaults: { name: 'star' }, tags: ['icon'] },
    { id: 'atom.status-dot',     name: 'Status dot',   layer: 'atom', family: 'status', icon: 'check-square', description: '8 px filled circle. Status: ok, warn, error, info.', defaults: { status: 'ok' }, tags: ['status'] },
    { id: 'atom.stamp',          name: 'Stamp',        layer: 'atom', family: 'mark',   icon: 'tag',   description: 'A small monospace label inside a soft-gold pill.', defaults: { text: 'STAMP' }, tags: ['mark'] },
    { id: 'atom.shape-glyph',    name: 'Shape glyph',  layer: 'atom', family: 'shape',  icon: 'atom',  description: 'Inline SVG of an entity shape — circle/hexagon/octagon/diamond.', defaults: { shape: 'circle' }, tags: ['shape', 'entity'] },
  ];

  // =========================================================================
  // Layer: BLOCK — composable content units
  // Mirror every WS_BLOCK as a Type so the slide library is the same registry.
  // The runtime field points to the renderer that lives in Blocks.jsx.
  // =========================================================================
  const blockSeeds = {
    hero:       { name: 'Hero',         family: 'block', icon: 'image',            desc: 'Full-bleed headline + supporting body + CTA + image.',                tags: ['block', 'lead'] },
    headline:   { name: 'Headline',     family: 'block', icon: 'edit',             desc: 'Optional eyebrow + a single H1.',                                     tags: ['block', 'text'] },
    body:       { name: 'Body text',    family: 'block', icon: 'document',         desc: 'A paragraph of supporting copy.',                                     tags: ['block', 'text'] },
    quote:      { name: 'Quote',        family: 'block', icon: 'chat',             desc: 'Pull-quote with attribution.',                                        tags: ['block', 'text'] },
    icons:      { name: 'Tag row',      family: 'block', icon: 'star',             desc: 'A horizontal row of icon + label tags.',                              tags: ['block', 'icon'] },
    stats:      { name: 'Stat grid',    family: 'block', icon: 'pie-chart',        desc: 'A grid of big-number + label tiles.',                                 tags: ['block', 'data'] },
    palette:    { name: 'Palette strip',family: 'block', icon: 'color-swatches',   desc: 'A horizontal strip of colour swatches with hex labels.',              tags: ['block', 'color'] },
    button:     { name: 'Button',       family: 'block', icon: 'tag',              desc: 'A single primary button.',                                            tags: ['block', 'cta'] },
    callout:    { name: 'Callout',      family: 'block', icon: 'lightbulb',        desc: 'A labelled note — eyebrow + paragraph in a tinted panel.',            tags: ['block', 'note'] },
    image:      { name: 'Image slot',   family: 'block', icon: 'image-stack',      desc: 'A placeholder rectangle with a caption.',                             tags: ['block', 'media'] },
    divider:    { name: 'Divider',      family: 'block', icon: 'minus',            desc: 'A dashed gold horizontal rule.',                                      tags: ['block'] },
  };

  // We don't register a `render` function here — the WS_BLOCKS renderer is
  // looked up by the consumer at draw-time. Registry just records the schema.
  const blocks = Object.entries(blockSeeds).map(([id, b]) => ({
    id: 'block.' + id,
    name: b.name,
    layer: 'block',
    family: b.family,
    icon: b.icon,
    description: b.desc,
    tags: b.tags,
    runtime: { kind: 'ws-block', key: id },
    // Defaults are pulled from WS_BLOCKS[id].defaults at lookup time
    defaults: {},
  }));

  // =========================================================================
  // Layer: SYSTEM — composition rules over blocks
  // Widget systems (kpi/media/hybrid). User can author new systems.
  // =========================================================================
  const systems = [
    {
      id: 'system.widget.kpi',
      name: 'KPI system',
      layer: 'system', family: 'widget',
      icon: 'pie-chart',
      description: 'Stat tiles. Headline numbers + deltas, optional sparkline.',
      tags: ['widget', 'data'],
      slots: {
        kpis:  { label: 'KPIs',  accepts: { layers: ['block'], tags: ['data'] }, multiple: true,  default: 3 },
        chart: { label: 'Chart', accepts: { layers: ['block'], tags: ['data'] }, optional: true },
      },
      defaults: { kpis: [], chart: null },
      runtime: { kind: 'widget-system', key: 'kpi' },
    },
    {
      id: 'system.widget.media',
      name: 'Media system',
      layer: 'system', family: 'widget',
      icon: 'image-stack',
      description: 'Imagery-led. Hero shot + caption + optional headline KPI + CTA.',
      tags: ['widget', 'media'],
      slots: {
        media: { label: 'Media', accepts: { layers: ['block'], tags: ['media'] } },
        lead:  { label: 'Lead KPI', accepts: { layers: ['block'], tags: ['data'] }, optional: true },
      },
      defaults: { media: { label: 'Hero render' }, kpis: [] },
      runtime: { kind: 'widget-system', key: 'media' },
    },
    {
      id: 'system.widget.hybrid',
      name: 'Hybrid system',
      layer: 'system', family: 'widget',
      icon: 'browser',
      description: 'Mixed — one media, two KPIs, a row table.',
      tags: ['widget', 'data', 'media'],
      slots: {
        kpis:  { label: 'KPIs',  accepts: { layers: ['block'], tags: ['data'] }, multiple: true, default: 2 },
        rows:  { label: 'Rows',  accepts: { layers: ['block'], tags: ['data'] }, multiple: true, default: 4 },
        media: { label: 'Media', accepts: { layers: ['block'], tags: ['media'] }, optional: true },
      },
      defaults: { kpis: [], rows: [], media: null },
      runtime: { kind: 'widget-system', key: 'hybrid' },
    },
  ];

  // =========================================================================
  // Layer: SURFACE — framed containers with context
  // Widget kinds (dashboard/hub/embed) + wizard step kinds + slide layouts.
  // =========================================================================
  const surfaces = [
    // Widget surfaces (kinds)
    {
      id: 'surface.widget.dashboard',
      name: 'Dashboard tile',
      layer: 'surface', family: 'widget',
      icon: 'browser', description: 'Drops into the platform dashboard grid (320×220).',
      tags: ['widget', 'dashboard'],
      defaults: { width: 320, height: 220 },
      slots: { body: { label: 'System', accepts: { layers: ['system'], families: ['widget'] } } },
      runtime: { kind: 'widget-kind', key: 'dashboard' },
    },
    {
      id: 'surface.widget.hub',
      name: 'Virtual Hub widget',
      layer: 'surface', family: 'widget',
      icon: 'check-square', description: 'Panel on conceptv.io/<hub> (480×320).',
      tags: ['widget', 'hub'],
      defaults: { width: 480, height: 320 },
      slots: { body: { label: 'System', accepts: { layers: ['system'], families: ['widget'] } } },
      runtime: { kind: 'widget-kind', key: 'hub' },
    },
    {
      id: 'surface.widget.embed',
      name: 'Embeddable',
      layer: 'surface', family: 'widget',
      icon: 'link', description: 'Partner site drop-in. Self-contained, co-brandable (380×260).',
      tags: ['widget', 'embed'],
      defaults: { width: 380, height: 260 },
      slots: { body: { label: 'System', accepts: { layers: ['system'], families: ['widget'] } } },
      runtime: { kind: 'widget-kind', key: 'embed' },
    },

    // Wizard step kinds — each is a small surface Type.
    {
      id: 'surface.wizard-step.capture',
      name: 'Capture step',
      layer: 'surface', family: 'wizard-step',
      icon: 'cloud-upload', description: 'Drop files, paste a link, or import. Use early for input.',
      tags: ['wizard', 'step', 'capture'],
      defaults: { title: 'Capture', body: '', fields: [], kind: 'capture' },
      slots: { fields: { label: 'Fallback fields', accepts: { layers: ['block'], tags: ['form'] }, multiple: true, optional: true } },
      runtime: { kind: 'wizard-step-kind', key: 'capture' },
    },
    {
      id: 'surface.wizard-step.form',
      name: 'Form step',
      layer: 'surface', family: 'wizard-step',
      icon: 'edit', description: 'Structured fields — text, number, choice, file.',
      tags: ['wizard', 'step', 'form'],
      defaults: { title: 'Form', body: '', fields: [{ label: 'Field', kind: 'text' }], kind: 'form' },
      runtime: { kind: 'wizard-step-kind', key: 'form' },
    },
    {
      id: 'surface.wizard-step.choice',
      name: 'Choice step',
      layer: 'surface', family: 'wizard-step',
      icon: 'check-square', description: 'Single-select between options. Can branch.',
      tags: ['wizard', 'step', 'choice', 'branching'],
      defaults: { title: 'Choice', body: '', options: ['Option A', 'Option B'], kind: 'choice' },
      runtime: { kind: 'wizard-step-kind', key: 'choice' },
    },
    {
      id: 'surface.wizard-step.review',
      name: 'Review step',
      layer: 'surface', family: 'wizard-step',
      icon: 'eye', description: 'Summary of captured state before submit.',
      tags: ['wizard', 'step', 'review'],
      defaults: { title: 'Review', body: 'Last look. Anything still off?', fields: [], kind: 'review' },
      runtime: { kind: 'wizard-step-kind', key: 'review' },
    },
    {
      id: 'surface.wizard-step.celebrate',
      name: 'Celebrate step',
      layer: 'surface', family: 'wizard-step',
      icon: 'star', description: 'Success / done state.',
      tags: ['wizard', 'step', 'celebrate'],
      defaults: { title: 'Done', body: 'You finished the flow.', fields: [], kind: 'celebrate' },
      runtime: { kind: 'wizard-step-kind', key: 'celebrate' },
    },

    // Slide layouts — surface-layer Types. The canonical generative archetypes
    // are SINGLE-SOURCED from core/archetype-catalog.js (window.CV_ARCHETYPE_CATALOG)
    // and registered in the bulk call below. These three are the app's named
    // slide *kinds*, kept as ALIASES (via `extends`) onto the canonical
    // archetypes — so existing references resolve and title/content map cleanly
    // (UNIFICATION.md W2). Reconciliation via the registry's own inheritance,
    // not a parallel definition.
    {
      id: 'surface.deck-slide.title',
      name: 'Title slide',
      layer: 'surface', family: 'deck-slide',
      icon: 'document', description: 'Large headline + eyebrow + optional CTA.',
      tags: ['deck', 'slide', 'title'],
      extends: 'surface.deck-slide.cover',
      defaults: { kind: 'title' },
      runtime: { kind: 'slide-layout', key: 'title' },
    },
    {
      id: 'surface.deck-slide.content',
      name: 'Content slide',
      layer: 'surface', family: 'deck-slide',
      icon: 'browser', description: 'Mixed-block content slide — the workhorse.',
      tags: ['deck', 'slide', 'content'],
      extends: 'surface.deck-slide.statement',
      defaults: { kind: 'content' },
      runtime: { kind: 'slide-layout', key: 'content' },
    },
    {
      id: 'surface.deck-slide.section',
      name: 'Section divider',
      layer: 'surface', family: 'deck-slide',
      icon: 'minus', description: 'Bronze chapter break with title.',
      tags: ['deck', 'slide', 'section'],
      defaults: { kind: 'section' },
      runtime: { kind: 'slide-layout', key: 'section' },
    },
  ];

  // =========================================================================
  // Layer: DOC — top-level document Types
  // =========================================================================
  // sample slides for doc previews, single-sourced from the archetype catalogue
  // (UNIFICATION W3) so doc.deck/doc.brochure render through the engine too.
  const archSample = (key) => {
    const t = (window.CV_ARCHETYPE_CATALOG || []).find(x => x.runtime && x.runtime.key === key);
    return { archetype: key, content: (t && t.defaults) || {} };
  };
  const deckSampleSlides = ['cover', 'split', 'metric-band', 'closing'].map(archSample);
  const brochureSampleSlides = ['statement', 'metric-band', 'closing'].map(archSample);
  const docs = [
    {
      id: 'doc.deck',
      name: 'Slide deck',
      layer: 'doc', family: 'deck',
      icon: 'browser', description: 'Pitch, sales, all-hands. 16:9 slides composed of blocks.',
      tags: ['doc', 'deck', 'slides'],
      slots: { slides: { label: 'Slides', accepts: { layers: ['surface'], families: ['deck-slide'] }, multiple: true } },
      defaults: { type: 'deck', theme: 'editorial', pages: [], slides: deckSampleSlides },
      runtime: { kind: 'doc-type', key: 'deck' },
    },
    {
      id: 'doc.brochure',
      name: 'One-page brochure',
      layer: 'doc', family: 'brochure',
      icon: 'document', description: 'A4 portrait, one page. Sales collateral, property sheets.',
      tags: ['doc', 'brochure', 'print'],
      slots: { sections: { label: 'Sections', accepts: { layers: ['block'] }, multiple: true } },
      defaults: { type: 'brochure', theme: 'editorial', pages: [], slides: brochureSampleSlides },
      runtime: { kind: 'doc-type', key: 'brochure' },
    },
    {
      id: 'doc.widget',
      name: 'Widget',
      layer: 'doc', family: 'widget',
      icon: 'check-square', description: 'Dashboard tile, hub panel, or partner embed. Composed of a kind × system.',
      tags: ['doc', 'widget'],
      slots: {
        surface: { label: 'Surface',   accepts: { layers: ['surface'], families: ['widget'] } },
        system:  { label: 'System',    accepts: { layers: ['system'],  families: ['widget'] } },
      },
      defaults: { type: 'widget', widgetKind: 'dashboard', system: 'kpi', mode: 'mock', data: {} },
      runtime: { kind: 'doc-type', key: 'widget' },
    },
    {
      id: 'doc.wizard',
      name: 'Wizard',
      layer: 'doc', family: 'wizard',
      icon: 'atom', description: 'Multi-step flow — Property Wizard, onboarding, generic.',
      tags: ['doc', 'wizard', 'flow'],
      slots: { steps: { label: 'Steps', accepts: { layers: ['surface'], families: ['wizard-step'] }, multiple: true } },
      defaults: { type: 'wizard', wizardKind: 'generic', layout: 'sidebar', mode: 'mock', steps: [] },
      runtime: { kind: 'doc-type', key: 'wizard' },
    },
  ];

  // Wizard sub-doc Types (kinds) — extend doc.wizard
  const wizardKinds = [
    {
      id: 'doc.wizard.property',
      name: 'Property Wizard',
      layer: 'doc', family: 'wizard',
      icon: 'atom', description: 'Canonical hexagon flow — capture → enrich → publish → linked hubs.',
      extends: 'doc.wizard', tags: ['wizard', 'property', 'hexagon'],
      defaults: { wizardKind: 'property' },
      runtime: { kind: 'wizard-kind', key: 'property' },
    },
    {
      id: 'doc.wizard.onboarding',
      name: 'Onboarding',
      layer: 'doc', family: 'wizard',
      icon: 'star', description: 'Sign up → workspace → invite team.',
      extends: 'doc.wizard', tags: ['wizard', 'onboarding', 'circle'],
      defaults: { wizardKind: 'onboarding' },
      runtime: { kind: 'wizard-kind', key: 'onboarding' },
    },
    {
      id: 'doc.wizard.generic',
      name: 'Generic flow',
      layer: 'doc', family: 'wizard',
      icon: 'atom', description: 'Custom steps, fields, choices.',
      extends: 'doc.wizard', tags: ['wizard', 'generic', 'diamond'],
      defaults: { wizardKind: 'generic' },
      runtime: { kind: 'wizard-kind', key: 'generic' },
    },
  ];

  // =========================================================================
  // Bulk register. The canonical deck-slide archetypes are single-sourced from
  // core/archetype-catalog.js (window.CV_ARCHETYPE_CATALOG) — the SAME catalogue
  // the DS bundle's RenderType reads — so the archetype list is not duplicated
  // across the app and the core (UNIFICATION.md W2).
  // =========================================================================
  const archetypeTypes = (typeof window !== 'undefined' && window.CV_ARCHETYPE_CATALOG);
  if (!archetypeTypes) throw new Error('[seed] archetype catalogue missing — core/archetype-catalog.js must load before types-seed.js (UNIFICATION W2)');
  R.registerMany(
    [...tokens, ...atoms, ...blocks, ...systems, ...surfaces, ...archetypeTypes, ...docs, ...wizardKinds].map(builtIn),
    { silent: true }
  );

  // Re-resolve defaults for block Types from WS_BLOCKS once it's loaded.
  // (WS_BLOCKS lives in Blocks.jsx and loads via Babel after this seed.)
  function hydrateBlockDefaults() {
    if (!window.WS_BLOCKS) return false;
    const add = [];
    for (const [k, def] of Object.entries(window.WS_BLOCKS)) {
      // cross-doc embeds are widget/wizard references, not composable slide
      // blocks — keep them out of the block catalogue (they render on WidgetRender).
      if (k === 'embedWidget' || k === 'embedWizard') continue;
      const id = 'block.' + k;
      const cur = R.get(id);
      if (cur) {
        if (!Object.keys(cur.defaults || {}).length && def.defaults) cur.defaults = { ...def.defaults };
      } else {
        // register EVERY WS_BLOCK as a block Type (UNIFICATION W3) — one block
        // catalogue, so composites (comparison/orgDiagram/funnel/…) are reachable
        // registry Types and render through the engine via BlockThumb.
        add.push(builtIn({
          id, name: def.label || k, layer: 'block', family: 'block',
          icon: def.icon || 'files-stack', description: '', tags: ['block'],
          runtime: { kind: 'ws-block', key: k }, defaults: { ...(def.defaults || {}) },
        }));
      }
    }
    if (add.length) R.registerMany(add, { silent: true });
    return true;
  }
  if (!hydrateBlockDefaults()) {
    // try again in a few hundred ms — Blocks.jsx is loaded via type="text/babel"
    const t = setInterval(() => { if (hydrateBlockDefaults()) clearInterval(t); }, 200);
    setTimeout(() => clearInterval(t), 5000);
  }

  // CV_HOST:types
  // ^ Vi-authored Types (via ds.propose, kind:"type") are inserted ABOVE this line.

  // Expose seed-counts so the Registry canvas can show "12 built-in" cleanly
  window.CV_REGISTRY_SEED = {
    counts: {
      token: tokens.length,
      atom: atoms.length,
      block: blocks.length,
      system: systems.length,
      surface: surfaces.length,
      doc: docs.length + wizardKinds.length,
    },
  };
})();
