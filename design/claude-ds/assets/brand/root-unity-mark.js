// assets/brand/root-unity-mark.js
// ============================================================================
// CV_ROOT_UNITY_MARK — the brand mark for ROOT UNITY (window.CV_ROOT_UNITY_MARK).
//
// The name encodes the thesis: every component, token, slot, action — everything —
// is the same ONE unit (Unity), and the whole system is the ROOT of that unit:
// √(unit). The mark draws it literally as the Glyphic anatomy (spec §5d): a
// radical sign whose radicand is the unit cell — a square element, an inscribed
// circle (the ring), and a centre dot (the symbol). √□◯• — the root of the one.
//
// Single source: this is the only place the mark geometry lives; cards + the app
// read svg() from here. Colours default to the design tokens (themeable).
// ============================================================================
(function () {
  'use strict';

  // body-only SVG (no <svg> wrapper) on a 64×64 grid, stroke=currentColor unless
  // overridden. ring/dot/square can be tinted independently.
  function body(o) {
    o = o || {};
    var ink   = o.ink   || 'currentColor';
    var ring  = o.ring  || 'var(--accent-gold)';
    var dot   = o.dot   || 'var(--accent-bronze)';
    var w     = o.weight || 3;
    return [
      // radical: stem + tick, sweeping into the overline across the radicand
      '<path d="M4 38 L11 38 L17 54 L27 12 L60 12" fill="none" stroke="' + ink + '" stroke-width="' + w + '" stroke-linecap="round" stroke-linejoin="round"/>',
      // the unit cell — square element
      '<rect x="33" y="20" width="23" height="23" rx="4" fill="none" stroke="' + ink + '" stroke-width="' + (w - 0.6) + '"/>',
      // inscribed circle — the ring
      '<circle cx="44.5" cy="31.5" r="9.2" fill="none" stroke="' + ring + '" stroke-width="' + (w - 0.4) + '"/>',
      // centre dot — the symbol
      '<circle cx="44.5" cy="31.5" r="2.6" fill="' + dot + '" stroke="none"/>',
    ].join('');
  }

  function svg(o) {
    o = o || {};
    var size = o.size || 64;
    return '<svg viewBox="0 0 64 64" width="' + size + '" height="' + size + '" role="img" aria-label="Root Unity" style="display:block;overflow:visible">' + body(o) + '</svg>';
  }

  window.CV_ROOT_UNITY_MARK = {
    name: 'Root Unity',
    glyph: '\u221A\u25A1\u25EF\u2022',     // √□◯•
    body: body,
    svg: svg,
    meaning: 'The root of the unit: every part is the same one unit; the system is √(unit). ' +
             'The radicand is the Glyphic anatomy — square element, inscribed ring, centre symbol.',
  };
})();
