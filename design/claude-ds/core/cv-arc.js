/* core/cv-arc.js — THE ARC RESOLVER (a telling has an arc) — window.CV_ARC.
 *
 * plan(arcName, n, {roles, arcs}) expands an arc's elastic run-lengths to exactly n beats
 * (start at minimums, grow elastic roles in listed order), assigns each beat an archetype
 * from the role's affinity (cycling within a run; forced change at every role boundary) and
 * dials from the role's envelope. DETERMINISTIC — same inputs, same plan. Roles/arcs are DATA
 * (the seed: assets/icons/glyph-arc-seed.json — deck-evidenced; the glyphgraph authors its own
 * event-kinds over the same machinery in use).
 *
 * ported-from: counterpart/design@212ba23 engine/prove/resolve-sequence.mjs (proven 7/7 —
 * plan('pitch',16) re-derives the source deck's exact structure), 2026-07-03, glyphic W1 —
 * port-by-COPY, generalized: data injected (no fs coupling), loud-fail, browser+node.
 * Proof harness: _demo/verify_arc.js.
 *
 * Why the glyphgraph needs it: a conversation-grown graph currently treats every node as the
 * same kind of event; the arc gives a telling its SHAPE (open → argue → show → prove → …) —
 * warmth choreography + archetype affinity + register per beat, derived never placed.
 */
(function (global) {
  'use strict';
  function fail(msg) { throw new Error('[CV_ARC] ' + msg); }
  var norm = function (a) { return String(a).replace(/\s*\(.*\)$/, ''); };

  function plan(arcName, n, data) {
    if (!data || !data.narrative_roles || !data.arcs) fail('plan: data {narrative_roles, arcs} required');
    var arc = data.arcs[arcName];
    if (!arc) fail('plan: unknown arc "' + arcName + '" (have: ' + Object.keys(data.arcs).join(', ') + ')');
    var runs = arc.runs.map(function (r) { return { role: r.role, count: r.count, len: r.count[0] }; });
    var total = runs.reduce(function (s, r) { return s + r.len; }, 0);
    for (var ri = 0; ri < runs.length; ri++) {                    // grow elastic roles in listed order
      while (runs[ri].len < runs[ri].count[1] && total < n) { runs[ri].len++; total++; }
    }
    if (total !== n) fail('arc "' + arcName + '" cannot reach ' + n + ' beats (got ' + total + ')');

    var beats = [], prevArch = null;
    runs.forEach(function (r) {
      var role = data.narrative_roles[r.role];
      if (!role) fail('plan: run names unknown role "' + r.role + '"');
      var aff = role.archetype_affinity.map(norm);
      for (var i = 0; i < r.len; i++) {
        var arch = aff[i % aff.length];
        if (i === 0 && arch === prevArch && aff.length > 1) arch = aff[1];   // change at the boundary
        var env = role.dial_envelope;
        beats.push({ role: r.role, archetype: arch,
          dials: { warmth: Math.round((env.warmth[0] + env.warmth[1]) / 2),
                   register: env.register[0], density: env.density } });
        prevArch = arch;
      }
    });
    return beats;
  }

  global.CV_ARC = { plan: plan, _norm: norm };
})(typeof window !== 'undefined' ? window : globalThis);
