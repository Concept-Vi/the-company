// app/ai/ai-capabilities-canvas.js
// ============================================================================
// CV_AI canvas capability catalogue — every per-canvas generative move
// registered as a first-class capability, so the catalogue describes the FULL
// generative surface of the app (not just the composer's 11 + image's 2).
//
// Each entry is data: queryable, inheritable, projectable in the registry
// inspector, and executable through CV_AI.execute(). To keep each canvas's
// bespoke prompt single-sourced (it stays where its domain helpers live), these
// capabilities share a generic `run` that completes a prompt handed in via
// params — so registering the move does NOT duplicate the prompt text. A canvas
// invokes its move with:
//     CV_AI.execute('<id>', { params: { prompt }, surface: '<surface>' })
// which resolves the provider, composes the voice behaviour, records the move,
// and returns the raw reply for the canvas's existing parse.
//
// This completes "the interface is a projection into both, synchronised" for
// every screen: each surface's moves are in the one catalogue the inspector and
// the AI both read.
// ============================================================================

(function () {
  const AI = window.CV_AI;
  if (!AI) throw new Error('[ai-capabilities-canvas] CV_AI not loaded — load app/ai/ai-registry.js first');

  // Generic text run — completes the prompt the canvas hands in (string or
  // {messages}); returns the raw reply. The canvas keeps its own parse.
  const runText = (a) => a.provider.complete(a.params && (a.params.prompt != null ? a.params.prompt : a.params));
  // Generic image runs — delegate to the resolved image provider.
  const runImgGen = (a) => a.provider.generateImage(a.params || {});
  const runImgEdit = (a) => a.provider.editImage(a.params || {});

  // [id, name, family, surfaces[], icon, provider?, run?]
  const TEXT = [
    // Colors canvas
    ['color.palette.generate', 'Generate palette',     'color',     ['colors'],   'palette'],
    ['color.recolor',          'Recolor swatch',       'color',     ['colors'],   'droplet'],
    // Icons canvas
    ['icon.generate',          'Generate icon set',    'icon',      ['icons'],    'grid'],
    ['icon.edit',              'Edit icon',            'icon',      ['icons'],    'edit'],
    ['icon.single',            'Generate one icon',    'icon',      ['icons'],    'plus'],
    // Voice canvas (composes VOICE_RULES inside its own prompt; voice behaviour additive)
    ['voice.rewrite',          'Rewrite in voice',     'voice',     ['voice'],    'feather'],
    ['voice.variants',         'Copy variants',        'voice',     ['voice'],    'copy'],
    ['voice.audit',            'Audit copy',           'voice',     ['voice'],    'search'],
    // Patterns canvas
    ['pattern.generate',       'Generate pattern set', 'pattern',   ['patterns'], 'layers'],
    ['pattern.shadow',         'Generate shadow',      'pattern',   ['patterns'], 'box'],
    // Components canvas
    ['component.generate',     'Generate component',   'component', ['components'],'component'],
    // Build orchestrator
    ['build.plan',             'Plan build',           'build',     ['build'],    'list'],
    ['build.triage',           'Triage edit',          'build',     ['build'],    'filter'],
    ['build.copy',             'Write copy',           'build',     ['build'],    'feather'],
    ['build.icons',            'Build icons',          'build',     ['build'],    'grid'],
    ['build.colors',          'Build colors',         'build',     ['build'],    'palette'],
    ['build.template',         'Extract template',     'build',     ['build'],    'bookmark'],
    // Workshop composer (doc-level, beyond the 11 block-level capabilities)
    ['deck.generate',          'Generate deck',        'deck',      ['deck','brochure'], 'file-plus'],
    ['block.refine',           'Refine block data',    'deck',      ['deck','brochure'], 'edit'],
    ['block.variations',       'Block variations',     'deck',      ['deck','brochure'], 'shuffle'],
    ['slide.compose',          'Compose slide',        'deck',      ['deck','brochure'], 'layout'],
    // Widget / Wizard drafting (whole-doc draft from a brief)
    ['widget.draft',           'Draft widget',         'widget',    ['widget'],   'activity'],
    ['wizard.draft',           'Draft wizard',         'wizard',    ['wizard'],   'list'],
    // Type registry Vi (the type system's own generator)
    ['type.propose',           'Propose Type',         'type',      ['registry'], 'plus-square'],
    ['type.materialize',       'Materialize Type',     'type',      ['registry'], 'box'],
    ['type.suggest-slots',     'Suggest slots',        'type',      ['registry'], 'grid'],
    // Inbox classifier
    ['inbox.classify',         'Classify item',        'inbox',     ['inbox'],    'filter'],
    // Chat rail (free-form Vi conversation)
    ['chat.respond',           'Chat response',        'chat',      ['*'],        'chat'],
  ];

  const IMAGE = [
    ['image.studio.generate',  'Studio generate',      'image',     ['imagery'],  'image',  runImgGen],
    ['image.studio.edit',      'Studio edit',          'image',     ['imagery'],  'edit',   runImgEdit],
  ];

  for (const [id, name, family, surfaces, icon] of TEXT) {
    AI.register({
      id, name, layer: 'capability', family, surfaces,
      behaviours: ['voice.conceptv'], provider: 'claude', params: {}, icon,
      provenance: 'built-in', run: runText,
      description: name + ' — a Vi generative move on the ' + family + ' surface (catalogued; prompt single-sourced in its canvas).',
    }, { silent: true });
  }
  for (const [id, name, family, surfaces, icon, run] of IMAGE) {
    AI.register({
      id, name, layer: 'capability', family, surfaces,
      behaviours: [], provider: 'openai-image', params: {}, icon,
      provenance: 'built-in', run,
      description: name + ' — a Vi image move via the openai-image provider.',
    }, { silent: true });
  }

  // deck.titlechain — the narrative title-chain move (DESIGN-LANGUAGE §16, from
  // capital-raise): emit a deck's slide titles as ONE running sentence, each a
  // clause continuing the prior via a leading connective, so the argument reads
  // from the title rail alone. The RULE is single-sourced in this run; the house
  // voice is composed by the registry (not re-inlined).
  AI.register({
    id: 'deck.titlechain', name: 'Chain deck titles', layer: 'capability', family: 'deck',
    surfaces: ['deck', 'brochure'], behaviours: ['voice.conceptv'], provider: 'claude',
    params: {}, icon: 'link', provenance: 'built-in',
    description: 'Write a deck’s slide titles as one running sentence — each a clause continuing the previous via a leading connective (But/To/With/That/Which/By/And) — so the argument reads from the title rail alone (DESIGN-LANGUAGE §16).',
    run: (a) => {
      const p = a.params || {};
      const outline = p.slides || p.outline || a.brief || '';
      const n = p.count || (Array.isArray(outline) ? outline.length : 8);
      return a.provider.complete(
        'Write a deck’s slide TITLES as ONE running sentence. Each title is a clause that CONTINUES the previous one, beginning with a leading connective (But / To / With / That / Which / By / And / Because / So). Read top to bottom, the titles must parse as a single argument following the arc: problem → thesis → mechanism → proof → moat → ask. Return exactly ' + n + ' titles, one per line, sentence case, no numbering, no quotes. Outline / topic:\n' + (typeof outline === 'string' ? outline : JSON.stringify(outline))
      );
    },
  }, { silent: true });

  window.CV_AI._canvasCapsSeeded = true;
})();
