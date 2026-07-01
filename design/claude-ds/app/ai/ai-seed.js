// app/ai/ai-seed.js
// ============================================================================
// CV_AI built-in seed — the providers, behaviours, skills and context
// resolvers that don't depend on the composer's prompt helpers. The
// capabilities themselves (which DO use those helpers) are registered from
// canvases/workshop/AIEngine.jsx, exactly as CV_REGISTRY built-ins that carry
// a render() function are seeded where that function lives.
//
// This file is DATA. Each entry is parametric and inheritable; adding a model
// provider, a tone behaviour, a one-click skill, or a new screen's context
// resolver is a registration, not a code change.
// ============================================================================

(function () {
  const AI = window.CV_AI;
  if (!AI) throw new Error('[ai-seed] CV_AI not loaded — load app/ai/ai-registry.js first');

  // ==========================================================================
  // PROVIDERS — model endpoints. Resolved to live runtimes by CV_AI.resolveProvider.
  // ==========================================================================
  AI.register({
    id: 'claude', name: 'Claude', layer: 'provider', family: 'text',
    description: 'Anthropic Claude — the text/JSON generation endpoint behind every Vi authoring move.',
    runtime: { kind: 'claude' }, modality: ['text', 'stream'],
    caps: { stream: true, json: true, maxPromptChars: 200000 },
    icon: 'sparkles', provenance: 'built-in', tags: ['text', 'json', 'default'],
  }, { silent: true });

  AI.register({
    id: 'openai-image', name: 'OpenAI Image', layer: 'provider', family: 'image',
    description: 'Image generation/edit via the shared window.cvOpenAI service (model + size + quality resolved there).',
    runtime: { kind: 'openai-image' }, modality: ['image'],
    caps: { stream: false, json: false },
    icon: 'image', provenance: 'built-in', tags: ['image'],
  }, { silent: true });

  AI.register({
    id: 'vision', name: 'Vision', layer: 'provider', family: 'image',
    description: 'Multimodal image understanding — reads screenshots/moodboards for layout, type feel, voice and palette. Resolves to a real vision runtime when AtomiCity is exported with one connected; in the browser sandbox it is unavailable and callers fall back to local pixel analysis.',
    runtime: { kind: 'vision' }, modality: ['image', 'text'],
    caps: { stream: false, json: true, exportOnly: true },
    icon: 'eye', provenance: 'built-in', tags: ['image', 'vision', 'export'],
  }, { silent: true });

  // ==========================================================================
  // BEHAVIOURS — instruction fragments composed INTO a capability's prompt.
  // The ConceptV voice is the spine; the "angle" behaviours are parametric
  // modifiers a capability or skill selects via params.angle.
  // ==========================================================================
  AI.register({
    id: 'voice.conceptv', name: 'ConceptV voice', layer: 'behaviour', family: 'voice',
    description: 'The house voice every Vi output speaks in — sentence case, second person, no exclamation/emoji, concrete numbers, canonical product names.',
    text: 'Brand voice: sentence case, second-person ("you"), no exclamation marks, no emoji. Concrete numbers. ConceptV names: User Portal, Property Wizard, Virtual Hub (a.k.a. Hub or Linked Hub), Capture, Vi.',
    icon: 'feather', provenance: 'built-in', tags: ['voice', 'always-on'],
  }, { silent: true });

  // angle behaviour — one entry, parameterised by params.angle (the field
  // toolbar's shorter/formal/specific/different all resolve through this).
  const ANGLE_TEXT = {
    shorter:  'Make each alternative SHORTER than the current — half the word count where possible.',
    formal:   'Make each alternative MORE FORMAL — drop colloquialism, prefer precise verbs.',
    specific: 'Make each alternative MORE SPECIFIC — concrete numbers, named examples, proper nouns where natural.',
    different:'Each alternative should take a DIFFERENT angle from the current value (and from each other).',
  };
  AI.register({
    id: 'angle', name: 'Regeneration angle', layer: 'behaviour', family: 'angle',
    description: 'Parametric steer applied to field/alternate regeneration — shorter, more formal, more specific, or a fresh angle.',
    text: (params) => ANGLE_TEXT[params && params.angle] || 'Each alternative should be a distinct angle, similar length and structure to the current.',
    params: { angle: 'different' },
    icon: 'shuffle', provenance: 'built-in', tags: ['angle', 'modifier'],
  }, { silent: true });

  // diversity behaviour — used by streaming parallel calls so slots differ.
  AI.register({
    id: 'diversity', name: 'Slot diversity', layer: 'behaviour', family: 'angle',
    description: 'Seeds parallel single-shot generations so the returned candidates are visibly distinct from one another.',
    text: (params) => params && params.seed ? `Take a distinctly ${params.seed} angle; this is option ${(params.slotIndex ?? 0) + 1} and must differ from the others.` : '',
    icon: 'grid', provenance: 'built-in', tags: ['angle', 'modifier'],
  }, { silent: true });

  // ==========================================================================
  // SKILLS — named parametric intents a user invokes. Each binds to a
  // capability + a target/param payload. The composer's whole-doc transform
  // menu and the suggestion engine are PROJECTIONS of these entries.
  // ==========================================================================
  const SKILLS = [
    { id: 'skill.shorten',  name: 'Shorten everything',   sub: 'Half the word count where possible', instruction: 'Shorten every block — half the word count where possible, keep the meaning.' },
    { id: 'skill.lengthen', name: 'Lengthen with detail', sub: 'Add a supporting sentence per block', instruction: 'Add one supporting sentence or specific detail to every long-form block.' },
    { id: 'skill.urgent',   name: 'More urgent tone',     sub: 'Sharper verbs, present tense',        instruction: 'Make the tone more urgent — sharper verbs, present tense, specific numbers.' },
    { id: 'skill.friendly', name: 'Warmer / more human',  sub: 'Second-person, conversational',       instruction: 'Make this warmer — second-person, conversational, no jargon, still no exclamation marks.' },
    { id: 'skill.pro',      name: 'More professional',    sub: 'Precise verbs, concrete metrics',     instruction: 'Make this more professional — precise verbs, concrete metrics, less marketing fluff.' },
    { id: 'skill.audit',    name: 'Audit voice & tone',   sub: 'Enforce ConceptV voice rules',        instruction: 'Audit every block against ConceptV voice rules (sentence case, second person, no exclamation marks, no emoji). Tighten as needed.' },
    { id: 'skill.concrete', name: 'Add concrete numbers', sub: 'Replace vague claims with numbers',   instruction: 'Wherever possible, add a concrete number, percentage, or named example.' },
  ];
  for (const s of SKILLS) {
    AI.register({
      id: s.id, name: s.name, layer: 'skill', family: 'transform',
      description: s.sub,
      instruction: s.instruction,
      // a transform skill drives the doc.transform capability
      target: { capability: 'doc.transform', kind: 'doc.transform' },
      icon: 'wand', provenance: 'built-in', tags: ['transform', 'whole-doc'],
    }, { silent: true });
  }
  // theme skill drives the theme.generate capability (not a doc.transform)
  AI.register({
    id: 'skill.theme', name: 'Switch visual theme', layer: 'skill', family: 'transform',
    description: '3 theme proposals',
    instruction: 'Propose alternative visual themes that fit this document.',
    target: { capability: 'theme.generate', kind: 'theme.generate' },
    icon: 'palette', provenance: 'built-in', tags: ['transform', 'theme'],
  }, { silent: true });

  // ==========================================================================
  // CONTEXT RESOLVERS — project "what screen Vi is on" into the compact context
  // object every capability's prompt is built from. Keyed by surface; the
  // generic resolver is the floor so no surface is ever context-less.
  // ==========================================================================

  // shared helpers (self-contained — the composer's richer versions live in
  // AIEngine, but context resolution must work even before that module loads)
  function pageNeighbourhood(doc, pageIdx) {
    if (!doc || !doc.pages || !doc.pages.length) return 'Empty document.';
    const line = (i) => {
      const p = doc.pages[i]; if (!p) return null;
      return `[page ${i + 1} · ${p.title || p.kind}] ` + (p.sections || []).map(s => `${s.kind}(${JSON.stringify(s.data).slice(0, 70)})`).join(' | ');
    };
    const lines = [];
    for (let i = Math.max(0, pageIdx - 1); i <= Math.min(doc.pages.length - 1, pageIdx + 1); i++) {
      const ln = line(i); if (ln) lines.push((i === pageIdx ? '▶ ' : '  ') + ln);
    }
    return lines.join('\n');
  }

  AI.register({
    id: 'context.generic', name: 'Generic context', layer: 'context', family: 'context',
    description: 'Fallback — title + type. Every surface gets at least this.',
    surfaces: ['generic'],
    resolveCtx: (doc) => ({ title: doc && doc.title, docType: doc && doc.type }),
    provenance: 'built-in', icon: 'crosshair',
  }, { silent: true });

  AI.register({
    id: 'context.pages', name: 'Page-doc context', layer: 'context', family: 'context',
    description: 'Decks & brochures — resolves the neighbourhood around the current page plus document-level facts (page count, has-CTA, has-stats).',
    surfaces: ['deck', 'brochure'],
    resolveCtx: (doc, base) => {
      const pageIdx = (base && base.currentPage) || 0;
      const pages = (doc && doc.pages) || [];
      return {
        title: doc && doc.title, docType: doc && doc.type,
        pageIdx, pageCount: pages.length,
        neighbourhood: pageNeighbourhood(doc, pageIdx),
        hasCta: pages.some(p => (p.sections || []).some(s => s.kind === 'button' || s.kind === 'callout' || (s.data && s.data.cta))),
        hasStats: pages.some(p => (p.sections || []).some(s => ['stats', 'metricRow', 'statPills', 'statTable'].includes(s.kind))),
        currentPageEmpty: pages[pageIdx] && (!pages[pageIdx].sections || pages[pageIdx].sections.length === 0),
      };
    },
    provenance: 'built-in', icon: 'layout',
  }, { silent: true });

  AI.register({
    id: 'context.widget', name: 'Widget context', layer: 'context', family: 'context',
    description: 'Widgets — resolves the widget kind/system and current data shape (kpis, media, chart) Vi is varying.',
    surfaces: ['widget'],
    resolveCtx: (doc) => ({
      title: doc && doc.data && doc.data.title, docType: 'widget',
      widgetKind: doc && doc.widgetKind, system: doc && doc.system,
      kpiCount: doc && doc.data && (doc.data.kpis || []).length,
      hasMedia: !!(doc && doc.data && doc.data.media), hasChart: !!(doc && doc.data && doc.data.chart),
    }),
    provenance: 'built-in', icon: 'activity',
  }, { silent: true });

  AI.register({
    id: 'context.wizard', name: 'Wizard context', layer: 'context', family: 'context',
    description: 'Wizards — resolves the wizard kind and the step sequence Vi is inserting into or rewriting.',
    surfaces: ['wizard'],
    resolveCtx: (doc) => ({
      docType: 'wizard', wizardKind: doc && doc.wizardKind,
      stepCount: doc && (doc.steps || []).length,
      steps: doc && (doc.steps || []).map((s, i) => `[${i + 1}] ${s.kind} · ${s.title}`).join('; '),
    }),
    provenance: 'built-in', icon: 'list',
  }, { silent: true });

  // ==========================================================================
  // IMAGE CAPABILITIES — the image endpoint is in the catalogue too, so "what
  // Vi can do" includes imagery and routes through the same execute() path.
  // run() resolves the openai-image provider (loud) and calls it directly.
  // ==========================================================================
  AI.register({
    id: 'image.generate', name: 'Generate image', layer: 'capability', family: 'image',
    description: 'Generate brand imagery from a prompt via the openai-image provider.',
    surfaces: ['*'], behaviours: [], provider: 'openai-image', params: { count: 1 },
    icon: 'image', provenance: 'built-in',
    run: (a) => a.provider.generateImage({ prompt: a.params.prompt || a.brief, n: a.params.count || 1, brandEnrich: a.params.brandEnrich !== false }),
  }, { silent: true });
  AI.register({
    id: 'image.edit', name: 'Edit image', layer: 'capability', family: 'image',
    description: 'Edit / compose / mask existing imagery via the openai-image provider.',
    surfaces: ['*'], behaviours: [], provider: 'openai-image', params: { count: 1 },
    icon: 'edit', provenance: 'built-in',
    run: (a) => a.provider.editImage({ prompt: a.params.prompt || a.brief, images: a.params.images, mask: a.params.mask, n: a.params.count || 1 }),
  }, { silent: true });

  // CV_HOST:ai-entries
  // ^ Vi-authored CV_AI entries (via ds.propose) are inserted ABOVE this line.

  // mark seed completion so AIEngine can assert its prerequisites loudly
  window.CV_AI._seeded = true;
})();
