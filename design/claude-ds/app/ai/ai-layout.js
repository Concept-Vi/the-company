// app/ai/ai-layout.js
// ============================================================================
// THE WALL FOUNDRY — layout.compose in CV_AI. The graph wall (NODES + THREADS,
// the relational grammar the skin demo and graph solver share) becomes a
// RESOLUTION: a brief goes in, a validated relational spec comes out, and the
// SAME solver/build path renders it. The model proposes STRUCTURE ONLY —
// hub/orbit/col/fx,fy relations, never pixels; geometry stays the solver's.
//
// SINGLE SOURCE: levels from CV_BLOCK, glyph ids from CV_ICONS, occupant
// grammar validated by CV_LAYOUT_GRAMMAR (this file — the one home, used by
// the capability AND any caller). Provider is parametric: 'claude' default,
// params.provider:'local-swarm' routes to the user's 4B concurrent swarm.
//
// Load after ai-registry.js + block-type.js (+ cv-icons for glyph checking).
// ============================================================================
(function () {
  'use strict';
  var AI = window.CV_AI;
  if (!AI) { console.error('ai-layout.js: CV_AI must load first'); return; }

  // SINGLE SOURCE (m0521): text roles come from the TYPE REGISTRY (text-type.js
  // owns the list) — a hardcoded copy here drifted when 'src' was registered.
  function TEXT_ROLES() { var R = window.CV_REGISTRY; return (R && R.text && R.text.roles) || ['micro', 'label', 'title', 'desc', 'body', 'src']; }
  var CHART_KINDS = ['bars', 'donut', 'gantt'];
  var STATES = ['selected', 'stacked', 'potential'];

  // ---- THE GRAMMAR (one home; capability + demo self-test both use it) -----
  function validate(spec) {
    var problems = [];
    if (!spec || !Array.isArray(spec.nodes) || !spec.nodes.length || !Array.isArray(spec.threads)) {
      return ['spec must be { nodes: [≥1 node], threads: [...] }'];
    }
    var hubs = spec.nodes.filter(function (n) { return n.hub === true; }).length;
    if (hubs !== 1) problems.push('exactly one hub required (got ' + hubs + ')');
    var B = window.CV_BLOCK;
    var levels = B ? B.levels().map(function (l) { return l.id; }) : null;
    var names = {};
    spec.nodes.forEach(function (n, i) {
      var p = 'nodes[' + i + ']';
      if (!n.name || !/^[a-z0-9-]+$/.test(n.name)) problems.push(p + ': name must be kebab-case');
      if (names[n.name]) problems.push(p + ': duplicate name "' + n.name + '"');
      names[n.name] = true;
      if (levels && n.level && levels.indexOf(n.level) < 0) problems.push(p + ': unknown level "' + n.level + '"');
      var placed = (n.hub === true) || (n.orbit != null) || (n.col != null) || (n.fx != null && n.fy != null);
      if (!placed) problems.push(p + ': needs a RELATION (hub | orbit | col | fx+fy) — never pixels');
      if (n.fx != null && (n.fx < 0 || n.fx > 1 || n.fy < 0 || n.fy > 1)) problems.push(p + ': fx/fy must be 0..1');
      if (n.col != null && (n.col !== Math.floor(n.col) || n.col < 0 || n.col > 4)) problems.push(p + ': col must be int 0..4');
      if (n.state != null && STATES.indexOf(n.state) < 0) problems.push(p + ': unknown state "' + n.state + '"');
      if (n.glyph != null && window.CV_ICONS && window.CV_ICONS.resolve && !window.CV_ICONS.resolve(n.glyph)) problems.push(p + ': unknown glyph "' + n.glyph + '"');
      (n.body || []).forEach(function (o, j) {
        var q = p + '.body[' + j + ']';
        if (!o || !o.occupant) { problems.push(q + ': occupant required'); return; }
        if (o.occupant === 'text' && TEXT_ROLES().indexOf(o.role) < 0) problems.push(q + ': bad text role');
        if (o.occupant === 'chart' && CHART_KINDS.indexOf(o.kind) < 0) problems.push(q + ': bad chart kind');
      });
    });
    spec.nodes.forEach(function (n, i) {
      if (n.orbit != null && !names[n.orbit]) problems.push('nodes[' + i + ']: orbit target "' + n.orbit + '" not a node');
    });
    spec.threads.forEach(function (t, i) {
      if (!Array.isArray(t) || !names[t[0]] || !names[t[1]]) problems.push('threads[' + i + ']: must be [fromName, toName] of real nodes');
    });
    return problems;
  }

  function buildPrompt(a) {
    var p = a.params || {};
    var B = window.CV_BLOCK;
    if (!B) throw new Error('layout.compose: CV_BLOCK not loaded');
    var levels = B.levels().map(function (l) { return l.id; }).join('|');
    var glyphs = (window.CV_ICONS && window.CV_ICONS.data) ? Object.keys(window.CV_ICONS.data).slice(0, 40).join(', ') : 'chat, link, image';
    return [
      'Compose a ConceptV WALL — a graph of blocks around the Vi hub — as JSON { "nodes": [...], "threads": [...] }.',
      'Placement is RELATIONAL ONLY (the solver computes geometry): each node has exactly one of',
      '  "hub": true (the single Vi centre) · "orbit": "<hub name>" (satellite) · "col": <0..4> (workflow column) · "fx"+"fy" (0..1 furniture).',
      'Node: { "name":"kebab-id", "level":"<' + levels + '>", "w":<8..20 stage-%>, "state":"selected|stacked|potential" (optional),',
      '  "glyph":"<icon id>" (satellites), "body":[ occupants ] }',
      'Occupants: {"occupant":"text","role":"micro|label|title|desc|body","value":"..."} ·',
      '  {"occupant":"chart","kind":"bars|donut|gantt","data":[..],"caption":"..."} ·',
      '  {"occupant":"render3d","geometry":"knot"} · {"occupant":"plus"}',
      'Glyph ids include: ' + glyphs + '.',
      'threads: [["fromName","toName"], ...] — the flow lines; every name must exist.',
      'RULES: exactly one hub; 2–4 columns each led by a level:"region" label node (material none) then 1–3 level:"card" nodes;',
      'cards carry a chart or render3d occupant FIRST, then label + desc text; copy is tight (2–4 words).',
      'Return ONLY the JSON object.',
      '\nBrief: ' + (p.brief || a.brief || ''),
    ].join('\n');
  }

  AI.register({
    id: 'layout.compose', name: 'Compose wall layout', layer: 'capability',
    family: 'layout', surfaces: ['skin-wall', 'canvas'],
    description: 'Generate a relational graph-wall spec (NODES+THREADS) from a brief — structure from the model, geometry from the solver, validated against the live grammar.',
    provider: 'claude', behaviours: ['voice.conceptv'],
    params: { brief: 'string', provider: 'optional provider id (e.g. local-swarm)' },
    run: function (a) {
      var prompt = buildPrompt(a);
      var providerId = (a.params && a.params.provider) || 'claude';
      var exec = providerId === 'claude'
        ? AI.complete(prompt)
        : AI.resolveProvider(providerId).complete(prompt); // loud-fail if the swarm isn't connected
      return Promise.resolve(exec).then(function (raw) {
        var txt = String(raw).replace(/^```(json)?/m, '').replace(/```\s*$/m, '').trim();
        var spec = JSON.parse(txt.slice(txt.indexOf('{'), txt.lastIndexOf('}') + 1));
        var problems = validate(spec);
        if (problems.length) throw new Error('layout.compose: invalid spec —\n' + problems.join('\n'));
        return spec;
      });
    },
  });

  // the grammar's one exported home (demo self-test + any future composer UI)
  window.CV_LAYOUT_GRAMMAR = { validate: validate, buildPrompt: buildPrompt };
})();
