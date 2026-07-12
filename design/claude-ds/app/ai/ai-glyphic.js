// app/ai/ai-glyphic.js
// ============================================================================
// Registers the AI GLYPHIC-FOUNDRY moves into CV_AI — the registry-way wiring
// of "the AI system built into the icon system". Two capabilities:
//
//   glyphic.generate  — propose N candidate SYMBOL records from a brief
//                        (multi-step conversation = repeated calls with the
//                        running thread as context; the surface renders the
//                        candidates live and feeds picks/feedback back in).
//   glyphic.save      — commit a chosen candidate into CV_ICONS (+ taxonomy),
//                        schema-validated, provenance 'vi'. Instantly live.
//
// SINGLE SOURCE: the record SHAPE is CV_GLYPHIC.schema; the write path is
// CV_ICONS.add; the voice is the 'voice.conceptv' behaviour. This file owns
// only the prompt + parse, co-located as the capability declares.
//
// Load after ai-registry.js (and cv-icons/cv-glyphics for the save path).
// ============================================================================
(function () {
  'use strict';
  var AI = window.CV_AI;
  if (!AI) { console.error('ai-glyphic.js: CV_AI must load first'); return; }

  // Build the generation prompt. Threads prior turns + the live taxonomy so Vi
  // proposes ON-system symbols (24px line glyphs) with tags/domain/kind filled.
  function buildPrompt(a) {
    var p = a.params || {};
    var brief = p.brief || a.brief || '';
    var n = p.count || 4;
    var tax = (window.CV_ICONS && window.CV_ICONS.taxonomy) || { domains: {}, kinds: {} };
    var domains = Object.keys(tax.domains || {}).join(', ');
    var kinds = Object.keys(tax.kinds || {}).join(', ');
    var thread = (p.thread || []).map(function (t) { return (t.role || 'user') + ': ' + t.text; }).join('\n');
    return [
      'You are drawing ConceptV line-symbols for the Glyphic system.',
      'STYLE: a single 24×24 SVG body (paths/circles only, NO <svg> wrapper), fill="none",',
      'stroke=currentColor, stroke-width 1.5, round caps/joins. Clean, geometric, 2px margin.',
      'Return ONLY a JSON array of ' + n + ' candidates, each:',
      '{ "id":"kebab-case", "name":"Title Case", "description":"one line",',
      '  "svg":"<path .../>", "facets":{ "domain":<one of: ' + domains + '>,',
      '  "kind":<one of: ' + kinds + '>, "tags":["..."] } }',
      thread ? ('\nConversation so far:\n' + thread) : '',
      '\nBrief: ' + brief,
    ].join('\n');
  }

  function parseCandidates(reply) {
    var txt = String(reply == null ? '' : reply);
    var m = txt.match(/\[[\s\S]*\]/);
    if (!m) throw new Error('glyphic.generate: model reply had no JSON array');
    var arr = JSON.parse(m[0]);
    var GL = window.CV_GLYPHIC;
    return arr.map(function (rec) {
      var problems = GL && GL.validateSymbol ? GL.validateSymbol(rec) : [];
      return { record: rec, valid: problems.length === 0, problems: problems };
    });
  }

  AI.register({
    id: 'glyphic.generate', name: 'Generate glyphic symbols', layer: 'capability', family: 'icon',
    surfaces: ['icons', 'glyphics', '*'], behaviours: ['voice.conceptv'], role: 'text',  /* A1: role-indirection (was provider:'claude') — resolves text→claude now, →Company when A flips the binding */
    params: { brief: '', count: 4, thread: [] }, icon: 'plus', provenance: 'built-in',
    description: 'Propose candidate symbol records (24px line glyphs + tags/domain/kind) from a brief; multi-step by threading prior turns. Candidates validate against CV_GLYPHIC.schema; save with glyphic.save.',
    run: function (a) {
      // A6 sweep: when the bound text provider can fire ROLES (the Company), use the
      // glyph_symbol_candidates ROLE — its output_schema enforces valid records mechanically
      // (the prompt-built JSON-array path breaks on JSON-in-text escaping; proven in A4).
      // A non-role runtime (e.g. the claude sandbox) keeps the original build→complete→parse path.
      var rt = AI.resolveProvider(AI.providerForRole('text'));
      if (typeof rt.runRole === 'function') {
        var p0 = a.params || {};
        var brief0 = p0.brief || a.brief || '';
        var thread0 = (p0.thread || []).map(function (t) { return (t.role || 'user') + ': ' + t.text; }).join('\n');
        var utter = (thread0 ? ('Earlier turns:\n' + thread0 + '\n\n') : '') + 'Brief: ' + brief0;
        return Promise.resolve(rt.runRole('glyph_symbol_candidates', utter, { max_tokens: 2048 })).then(function (j) {
          var GLr = window.CV_GLYPHIC;
          return ((j.output && j.output.candidates) || []).map(function (c) {
            var rec = { id: c.id, name: c.name, description: c.description, svg: c.svg,
                        facets: { domain: c.domain || 'feature', kind: c.kind || 'object', tags: c.tags || [] } };
            var problems = GLr && GLr.validateSymbol ? GLr.validateSymbol(rec) : [];
            return { record: rec, valid: problems.length === 0, problems: problems };
          });
        });
      }
      var prompt = buildPrompt(a);
      var complete = AI.complete ? AI.complete.bind(AI) : (a.provider && a.provider.complete);
      if (!complete) throw new Error('glyphic.generate: no completion provider (CV_AI.complete / provider.complete)');
      return Promise.resolve(complete(prompt)).then(parseCandidates);
    },
  }, { silent: true });

  AI.register({
    id: 'glyphic.save', name: 'Save glyphic symbol', layer: 'capability', family: 'icon',
    surfaces: ['icons', 'glyphics', '*'], behaviours: [], provider: null,
    params: { record: null }, icon: 'check-square', provenance: 'built-in',
    description: 'Commit a chosen symbol candidate into the icon library (CV_ICONS.add) + taxonomy, schema-validated, provenance vi. Instantly available to the explorer, CV_GLYPHIC and the registry.',
    run: function (a) {
      var rec = (a.params || {}).record;
      if (!window.CV_ICONS || !window.CV_ICONS.add) throw new Error('glyphic.save: CV_ICONS.add unavailable');
      var id = window.CV_ICONS.add(Object.assign({ provenance: 'vi' }, rec));
      return { saved: id };
    },
  }, { silent: true });
})();
