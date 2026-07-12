// axes/ordinal/ordinal-axis.js — the ORDINAL axis (the FIELD face): position-in-a-telling → a
// stop on the warm-metal ramp. "The palette is a number line — index in, axis position out;
// brightness maps to attention" (counterpart's ordinal-colour law, ported as a first-class
// CV_AXES axis, glyphic W2). A FIELD is orientation without reading: you don't read it, you
// orient by it — terrain, not label.
//
// THE MONOTONIC LAW (build-enforced in counterpart; registration-enforced here, loud): the ramp
// must DARKEN monotonically — luminance order is the strongest ordinal cue human vision has; a
// stop breaking lightness order silently kills series-perception. Each stop declares its
// approximate perceptual lightness (meta.L, 0..1, from the sampled palette); registration
// THROWS if the declared Ls ever stop decreasing. Values point at TOKENS (never hex).
//
// ordinal(i, n): the i-th of n gets its ramp stop by even division (few items step the whole
// ramp; many items chunk — past ~7 the CHUNKING law applies upstream, this axis just resolves).
(function () {
  'use strict';
  const AX = (typeof window !== 'undefined') && window.CV_AXES;
  if (!AX) { console.error('ordinal-axis: CV_AXES must load before this (axis-core.js)'); return; }

  const STOPS = [
    { id: 'o1', label: 'first — nearest, warmest', token: 'accent-gold',     meta: { L: 0.82 } },
    { id: 'o2', label: 'early',                    token: 'accent-gold-deep',meta: { L: 0.62 } },
    { id: 'o3', label: 'late',                     token: 'accent-bronze',   meta: { L: 0.58 } },
    { id: 'o4', label: 'last — farthest, coolest', token: 'accent-bronze-2', meta: { L: 0.46 } },
  ];
  // the monotonic-lightness gate — loud, at registration, never silently reordered
  for (let i = 1; i < STOPS.length; i++) {
    if (!(STOPS[i].meta.L < STOPS[i - 1].meta.L))
      throw new Error('[ordinal-axis] ramp must darken monotonically: ' + STOPS[i - 1].id +
        ' (L=' + STOPS[i - 1].meta.L + ') → ' + STOPS[i].id + ' (L=' + STOPS[i].meta.L + ') breaks series-perception');
  }

  AX.register({
    id: 'ordinal', label: 'Ordinal (the telling-order field)',
    groups: [ { id: 'ramp', label: 'The warm-metal ramp' } ],
    values: STOPS.map(s => ({ id: s.id, label: s.label, group: 'ramp', token: s.token, meta: s.meta })),
    default: 'o1',
  });

  // index i of n → the stop id (even division across the ramp; deterministic)
  window.CV_ORDINAL = {
    stopFor: function (i, n) {
      if (!Number.isInteger(i) || i < 0 || !Number.isInteger(n) || n < 1 || i >= n)
        throw new Error('[CV_ORDINAL] stopFor(i, n): need 0 <= i < n');
      const k = n === 1 ? 0 : Math.min(STOPS.length - 1, Math.floor(i * STOPS.length / n));
      return STOPS[k].id;
    },
    tokenFor: function (i, n) {
      const id = this.stopFor(i, n);
      return STOPS.find(s => s.id === id).token;
    },
    stops: STOPS.slice(),
  };
})();
