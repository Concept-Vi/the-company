// app/ai/ai-studio.js
// ============================================================================
// Studio wiring for CV_AI — registers, the registry-way, the pieces the Studio
// needs so "talk to it" and "click it" are one loop. NOTHING here is a parallel
// system: it's entries in the existing CV_AI (providers / context / capability).
//
//   · voice provider     — two-way voice as just-another-provider. resolveProvider
//     already delegates unknown runtime kinds to CV_HOST, so your OWN local or
//     remote providers (a local model, a different voice engine) register the
//     same way and bind through CV_HOST. The provider registry already exists;
//     this seeds the voice one + documents the local-provider path.
//   · context.studio     — projects the Studio's live state (selection · node ·
//     hover · clicks · screen) into Vi's operating context via the ONE projection
//     (CV_PROJECT.toContext). Same context the UI + CV_VARS + CV_ACTIONS resolve.
//   · studio.command     — turns a natural-language / transcribed-voice instruction
//     into ONE action call chosen from the live tool schema (CV_PROJECT.toToolSchema);
//     the app then CV_ACTIONS.invoke()s it. The chat/voice → action loop, on rails.
//
// Load after ai-registry.js (+ project.js for the context/command to resolve).
// ============================================================================
(function () {
  'use strict';
  var AI = window.CV_AI;
  if (!AI) { console.error('ai-studio.js: CV_AI must load first'); return; }

  // ---- providers: voice + the local-provider pattern ----------------------
  AI.register({
    id: 'voice.openai', name: 'OpenAI realtime voice', layer: 'provider',
    runtime: { kind: 'openai-voice' }, modality: ['voice', 'stream'],
    description: 'Two-way voice (speech-in / speech-out). Bound by CV_HOST — connect a key/runtime ' +
      'locally and it becomes available; resolveProvider delegates this runtime kind to CV_HOST. ' +
      'Swap to any other voice engine by registering a provider with the runtime kind your CV_HOST claims.',
    caps: { stream: true }, icon: 'mic', provenance: 'built-in',
  }, { silent: true });

  AI.register({
    id: 'provider.local', name: 'Local model (your machine)', layer: 'provider',
    runtime: { kind: 'local' }, modality: ['text', 'stream'],
    description: 'Pattern for a provider you run locally / connect into your system. Register one with ' +
      'runtime.kind that your CV_HOST.resolveProviderRuntime claims; capabilities can then name it as ' +
      'their `provider`. Loud (throws) until CV_HOST binds it — never a silent fallback.',
    icon: 'desktop', provenance: 'built-in',
  }, { silent: true });

  // ---- context: project the Studio's live state into Vi's context ----------
  AI.register({
    id: 'context.studio', name: 'Studio context', layer: 'context', surfaces: ['studio'],
    description: 'Projects the Studio\u2019s live state (selection, the node on screen, hover, recent ' +
      'clicks) into Vi\u2019s operating context via the one projection (CV_PROJECT.toContext) — so what ' +
      'you see and select is what Vi knows, through the same variable mechanism the UI uses.',
    resolveCtx: function (doc, base) {
      var P = window.CV_PROJECT;
      var st = (base && base.studio) || (window.CV_STUDIO && window.CV_STUDIO.state) || {};
      return P ? P.toContext(st) : {};
    },
    icon: 'browser', provenance: 'built-in',
  }, { silent: true });

  // ---- capability: instruction → one action call (chat/voice → action loop) -
  AI.register({
    id: 'studio.command', name: 'Interpret a Studio command', layer: 'capability', family: 'studio',
    surfaces: ['studio', '*'], behaviours: ['voice.conceptv'], provider: 'claude',
    params: { instruction: '' }, icon: 'wand', provenance: 'built-in',
    description: 'Turn a natural-language (or transcribed-voice) instruction into a single action call ' +
      'against the current selection — chosen from the LIVE tool schema (CV_PROJECT.toToolSchema). The ' +
      'app then CV_ACTIONS.invoke()s the result. This is how talking and clicking become one action layer.',
    build: function (doc, target, ctx, params) {
      var P = window.CV_PROJECT;
      var sel = (ctx && ctx.node) || target || null;
      var tools = (P && sel) ? P.toToolSchema(sel.spec || sel) : [];
      return [
        'You operate a design Studio by choosing ONE tool call.',
        'Available tools (JSON function schema): ' + JSON.stringify(tools),
        'Current selection: ' + JSON.stringify(sel),
        'Choose the single best tool + arguments for the user\u2019s instruction.',
        'Reply ONLY as JSON: {"action":"<tool name>","args":{ ... }}.',
        'Instruction: ' + (params.instruction || params.brief || ''),
      ].join('\n');
    },
    parse: function (reply) {
      var m = String(reply == null ? '' : reply).match(/\{[\s\S]*\}/);
      if (!m) throw new Error('studio.command: no JSON object in model reply');
      return [JSON.parse(m[0])];
    },
  }, { silent: true });
})();
