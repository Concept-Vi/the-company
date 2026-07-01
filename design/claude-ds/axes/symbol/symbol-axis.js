// axes/symbol/symbol-axis.js
// ============================================================================
// THE SYMBOL AXIS — window.CV_AXES.resolve('symbol')
//
// Typed view over the inner-glyph library (CV_ICONS). SPECIAL among axes: a
// symbol's meaning is INTRINSIC (a house is a house), so unlike colour/texture/
// motion it is NOT governed by the loadable meaning profiles (CV_MEANING). The
// axis groups values by the icon faceted taxonomy (CV_ICONS.facets.domain) and
// stays in sync — it reads the library live, including AI-foundry-added symbols.
//
// Load after axes/axis-core.js AND cv-icons.js.
// ============================================================================
(function () {
  'use strict';
  if (!window.CV_AXES) { console.error('symbol-axis.js: CV_AXIS core must load first'); return; }
  var I = window.CV_ICONS;
  if (!I) { console.error('symbol-axis.js: CV_ICONS must load first'); return; }

  // domains become groups; each icon a value tagged with its domain.
  var domains = {};
  function domainOf(id) { return (I.facets && I.facets[id] && I.facets[id].domain) || 'feature'; }

  var symbol = window.CV_AXES.make({
    id: 'symbol',
    label: 'Symbol',
    description: 'Inner-glyph library (CV_ICONS). Meaning is INTRINSIC — the one axis NOT governed by contextual meaning profiles. Groups = icon taxonomy domains.',
    meta: { intrinsicMeaning: true },
    default: 'person',
  });

  function rebuild() {
    Object.keys(I.data || {}).forEach(function (id) {
      var d = domainOf(id);
      if (!domains[d]) { domains[d] = true; symbol.registerGroup({ id: d, label: d.charAt(0).toUpperCase() + d.slice(1) }); }
      symbol.register({ id: id, label: (I.facets && I.facets[id] && I.facets[id].name) || id, group: d,
        // a symbol's payload is its 24px svg body, resolved live from the library
        resolve: function () { return I.get ? I.get(id) : (I.data ? I.data[id] : null); },
        meta: { intrinsic: true } });
    });
  }
  rebuild();
  symbol.rebuild = rebuild;   // foundry calls this after CV_ICONS.add

  window.CV_AXES.register(symbol);
})();
