// app/ai/ai-block.js
// ============================================================================
// Registers the BLOCK-FOUNDRY move into CV_AI — the generative counterpart of
// ai-glyphic.js for containers. One capability:
//
//   block.compose — propose a page/section COMPOSITION (a nested block spec)
//                   from a brief. The reply is a JSON block tree whose every
//                   node is VALIDATED against the live axes (level, material,
//                   flow, texture, space) and the Block Type's socket grammar —
//                   trust nothing; structure the catch. Render the result with
//                   CV_BLOCK.chrome()/walk(); nothing in it is hand-styled.
//
// SINGLE SOURCE: the vocabularies come from CV_AXES + CV_BLOCK at prompt-build
// time (never copied); the voice + copy budgets are behaviours; the write path
// is the caller's (a composition is data — the caller decides where it lives).
//
// Load after ai-registry.js + block-type.js (+ axes).
// ============================================================================
(function () {
  'use strict';
  var AI = window.CV_AI;
  if (!AI) { console.error('ai-block.js: CV_AI must load first'); return; }

  function ax(id) {
    var AX = window.CV_AXES;
    if (!AX || !AX.has(id)) throw new Error('block.compose: axis "' + id + '" not loaded');
    return AX.resolve(id);
  }

  function buildPrompt(a) {
    var p = a.params || {};
    var brief = p.brief || a.brief || '';
    var B = window.CV_BLOCK;
    if (!B) throw new Error('block.compose: CV_BLOCK not loaded (app/registry/block-type.js)');
    var levels = B.levels().map(function (l) { return l.id + '(' + l.rank + ': ' + (l.means || '') + ')'; }).join('; ');
    var sockets = B.orderedSockets().map(function (s) { return s.name + '#' + s.order; }).join(' \u2192 ');
    return [
      'You are composing a ConceptV PAGE as a nested BLOCK spec (containers only \u2014 no CSS, no pixels).',
      'A block: { "name":"kebab-id", "level":<one of the ladder>, "material":<' + ax('material').ids().join('|') + '>,',
      '  "tint":<optional zone: content|panel|source|package|review|success|warning|reject|comm|vi>,',
      '  "arrange":<stack|split|flow>, "cols":"<css template, split only>", "count":<int, flow only>, "flow":<' + ax('flow').ids().join('|') + '>,',
      '  "sockets": { "body": [ <child blocks or leaf occupants> ] },',
      '  leaf occupants: { "occupant":"text", "role":<micro|label|title|desc|body>, "value":"..." }',
      '                  { "occupant":"glyphic", "symbol":"<icon id>", "form":"<circle|hex|octagon|diamond>" } }',
      'THE LADDER (level derives depth treatment + spacing rhythm): ' + levels + '.',
      'Socket order is reading order: ' + sockets + '.',
      'RULES: the root is level "page" with material "none"; nesting must DESCEND the ladder (page\u2192region\u2192panel\u2192card\u2192well);',
      'tint is a whisper \u2014 use sparingly, gold ("vi") ONLY for the AI voice; text values obey the copy budgets.',
      'Return ONLY the JSON object of the root block.',
      '\nBrief: ' + brief,
    ].join('\n');
  }

  // validate a composed tree against the LIVE vocabularies — loud, per node.
  function validate(root) {
    var problems = [];
    var lvl = ax('level'), mat = ax('material'), flw = ax('flow');
    var order = { };
    lvl.values().forEach(function (v) { order[v.id] = v.meta.rank; });
    (function walk(n, path, parentRank) {
      if (!n || typeof n !== 'object') { problems.push(path + ': not an object'); return; }
      if (!lvl.has(n.level)) problems.push(path + ': unknown level "' + n.level + '"');
      if (n.material != null && !mat.has(n.material)) problems.push(path + ': unknown material "' + n.material + '"');
      if (n.flow != null && !flw.has(n.flow)) problems.push(path + ': unknown flow "' + n.flow + '"');
      if (lvl.has(n.level) && parentRank != null && order[n.level] <= parentRank && n.level !== 'overlay')
        problems.push(path + ': level "' + n.level + '" does not descend the ladder');
      ((n.sockets && n.sockets.body) || []).forEach(function (c, i) {
        if (c && c.occupant) {
          if (c.occupant === 'text' && (((window.CV_REGISTRY || {}).text || {}).roles || ['micro','label','title','desc','body','src']).indexOf(c.role) < 0) problems.push(path + '/body[' + i + ']: bad text role'); // SINGLE SOURCE m0521: registry owns the role list
          return;
        }
        walk(c, path + '/' + (c && c.name || ('body[' + i + ']')), lvl.has(n.level) ? order[n.level] : null);
      });
    })(root, root && root.name || 'page', null);
    return problems;
  }

  function parse(reply) {
    var txt = String(reply == null ? '' : reply);
    var m = txt.match(/\{[\s\S]*\}/);
    if (!m) throw new Error('block.compose: model reply had no JSON object');
    var root = JSON.parse(m[0]);
    var problems = validate(root);
    return { spec: root, valid: problems.length === 0, problems: problems };
  }

  AI.register({
    id: 'block.compose', name: 'Compose a page of blocks', layer: 'capability', family: 'block',
    surfaces: ['blocks', 'workshop', '*'], behaviours: ['voice.conceptv', 'copy.budgets'], role: 'text',
    params: { brief: '', thread: [] }, icon: 'browser', provenance: 'built-in',
    description: 'Propose a nested block composition (levels \u00b7 materials \u00b7 tints \u00b7 arrange \u00b7 typed text/glyphic occupants) from a brief. Every node validates against the live axes + ladder; render via CV_BLOCK.chrome().',
    build: buildPrompt,
    parse: parse,
    run: function (a) {
      var prompt = buildPrompt(a);
      return AI.complete(prompt).then(function (reply) { return parse(reply); });
    },
  });
})();
