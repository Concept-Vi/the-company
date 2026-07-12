// core/layout-fit.js
// ============================================================================
// THE RATIO-FIT LAW — content arrangement is COMPUTED from ratios, never from
// a flat per-axis rule.
//
// The failure this replaces: "fit the height, take the whole row" — a media
// asset reduced into a letterboxed strip with dead space around it. The law:
//
//   1. Every media occupant carries its ASPECT RATIO as a field (--asset-ar),
//      measured from the asset itself at load — never assumed.
//   2. The media's box IS its ratio (aspect-ratio: var(--asset-ar)), so a
//      letterbox (dead padding inside the well) is geometrically impossible.
//   3. The ARRANGEMENT is solved by comparing the ratios of everything that
//      must render in the container: portrait/square media (ar < BESIDE_AR)
//      sits BESIDE the text stack — media takes the golden minor column
//      (imagery has more visual weight: the eye goes there first, so it gets
//      the larger share of height); wide media (ar ≥ BESIDE_AR) spans the
//      full content width and the texts stack under it.
//   4. Padding derives from the control rung (--glyph-d × PAD_RATIO), the
//      same rung every other gap resolves from — even by construction.
//
// Registry-shaped: this file owns BOTH the solver and its CSS (injected once)
// so there is exactly one home for the law. Consumers call:
//   CV_LAYOUT_FIT.stampMedia(el, url?)  — measure + stamp --asset-ar
//   CV_LAYOUT_FIT.arrange(cardEl)       — solve + apply the arrangement
// ============================================================================
(function () {
  'use strict';
  var BESIDE_AR = 1.45;   // below this the media reads as a figure, not a band
  var MEDIA_COL = '42%';  // the golden minor column for beside-mode media
  var PAD_RATIO = 0.27;   // content gap = rung × this (same rung as keylines)

  var css = [
    '/* injected by core/layout-fit.js — THE ratio-fit law, one home */',
    '.cv-fit > .render-well, .cv-fit > .chart-well { height: auto; aspect-ratio: var(--asset-ar); }',
    '.cv-fit-beside { --fit-media-col: ' + MEDIA_COL + '; display: grid; grid-template-columns: minmax(0, var(--fit-media-col)) minmax(0, 1fr);',
    '  column-gap: calc(var(--glyph-d) * ' + PAD_RATIO + '); align-items: center; align-content: center; }',
    '.cv-fit-beside > .render-well, .cv-fit-beside > .chart-well, .cv-fit-beside > .thumb, .cv-fit-beside > .well3d {',
    '  grid-column: 1; grid-row: 1 / span 9; }',
    '.cv-fit-beside > [class*="t-"] { grid-column: 2; }'
  ].join('\n');
  var tag = document.createElement('style');
  tag.setAttribute('data-owner', 'cv-layout-fit');
  tag.textContent = css;
  document.head.appendChild(tag);

  function solve(spec) {
    var ar = spec.media && spec.media.aspect;
    if (!ar || !isFinite(ar)) return { mode: 'stack' };
    return (ar < BESIDE_AR && spec.texts > 0) ? { mode: 'beside' } : { mode: 'stack' };
  }

  // measure the asset's true ratio and stamp it as a FIELD on the element.
  // onDone fires after the stamp so the host can re-solve layout/threads.
  function stampMedia(el, url, onDone) {
    if (!url) { if (onDone) onDone(); return; }
    var img = new Image();
    img.onload = function () {
      el.style.setProperty('--asset-ar', (img.naturalWidth / img.naturalHeight).toFixed(3));
      if (onDone) onDone();
    };
    img.onerror = function () { if (onDone) onDone(); };
    img.src = url;
  }

  function arrange(cardEl) {
    var media = cardEl.querySelector('.render-well, .chart-well, .thumb, .well3d');
    if (!media) return;
    cardEl.classList.add('cv-fit');
    var ar = parseFloat(getComputedStyle(media).getPropertyValue('--asset-ar'));
    var texts = cardEl.querySelectorAll('[class*="t-"]').length;
    cardEl.classList.toggle('cv-fit-beside', solve({ media: { aspect: ar }, texts: texts }).mode === 'beside');
  }

  window.CV_LAYOUT_FIT = { solve: solve, stampMedia: stampMedia, arrange: arrange,
    BESIDE_AR: BESIDE_AR, PAD_RATIO: PAD_RATIO };
})();
