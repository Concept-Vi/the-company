// core/world-camera.js
// ============================================================================
// THE WORLD CAMERA — window.CV_WORLD_CAMERA — the ONE home for the coupled
// camera/content coordinate system. Every `.skin-ground` element is a framed
// view into the texture world: its --world-zoom is DERIVED (never hand-set)
// as elementWidth / FRAME, where FRAME is the 1440px design reference. All
// world-scaled lengths (ground tiles, material grains — anything declared as
// calc(var(--world-zoom) * <native px>) in tokens/skins.css) follow the frame
// exactly like a camera moving toward/away from the wall.
//
//   CV_WORLD_CAMERA.FRAME      — the reference frame width (px)
//   CV_WORLD_CAMERA.observe(el)— couple a late-added ground to the camera
//
// One ResizeObserver for the page; grounds present at load are auto-coupled.
// A page can still override --world-zoom inline for a DELIBERATE zoom (the
// override wins over the observed value only if set on a descendant scope).
// ============================================================================
(function () {
  'use strict';
  var FRAME = 1440;
  var coupled = [];

  // ── WORLD-POSITION MATERIAL STAMP ────────────────────────────────────────
  // THE decorrelation law, graduated from the demo into the camera (one home):
  // every material SURFACE inside a ground samples the ONE texture at its own
  // world offset (--mat-tex-pos, consumed by tokens/material.css longhands).
  // Runs automatically on couple/resize/camera moves; pages with their OWN
  // layout passes call CV_WORLD_CAMERA.stampMaterials(ground) after them.
  function stampMaterials(ground) {
    var gb = ground.getBoundingClientRect();
    var mats = ground.querySelectorAll('.material, [class*="material--"]');
    for (var i = 0; i < mats.length; i++) {
      var r = mats[i].getBoundingClientRect();
      mats[i].style.setProperty('--mat-tex-pos',
        (-(r.left - gb.left)).toFixed(0) + 'px ' + (-(r.top - gb.top)).toFixed(0) + 'px');
    }
  }

  function measure(el) {
    var w = el.clientWidth;
    var f = parseFloat(el.dataset.cvZoomFactor || '1') || 1; // deliberate camera factor × derived base
    if (w > 0) el.style.setProperty('--world-zoom', (w / FRAME * f).toFixed(4));
  }

  // ── DELIBERATE CAMERA MOVES ── CV_WORLD_CAMERA.to(el, {zoom, panX, panY}) ─
  // The camera steps toward/away/across the wall: rAF-tweens a zoom FACTOR
  // (multiplied onto the derived base, so the size-coupling law keeps holding
  // under resize) and the --world-pan-x/y vars every ground consumes as
  // background-position. Fires 'cv:cameramove' when the move lands so pages
  // can re-stamp world offsets. One camera, every move.
  function to(el, target, opts) {
    opts = opts || {};
    var dur = opts.duration != null ? opts.duration : 480;
    var f0 = parseFloat(el.dataset.cvZoomFactor || '1') || 1;
    var f1 = target.zoom != null ? target.zoom : f0;
    var x0 = parseFloat(el.style.getPropertyValue('--world-pan-x')) || 0;
    var y0 = parseFloat(el.style.getPropertyValue('--world-pan-y')) || 0;
    var x1 = target.panX != null ? target.panX : x0;
    var y1 = target.panY != null ? target.panY : y0;
    var t0 = performance.now();
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) dur = 0;
    function ease(t) { return t < 0.5 ? 4*t*t*t : 1 - Math.pow(-2*t + 2, 3) / 2; }
    (function tick(now) {
      var t = dur ? Math.min(1, (now - t0) / dur) : 1;
      var k = ease(t);
      el.dataset.cvZoomFactor = (f0 + (f1 - f0) * k).toFixed(4);
      el.style.setProperty('--world-pan-x', (x0 + (x1 - x0) * k).toFixed(1) + 'px');
      el.style.setProperty('--world-pan-y', (y0 + (y1 - y0) * k).toFixed(1) + 'px');
      measure(el);
      if (t < 1) requestAnimationFrame(tick);
      else { stampMaterials(el); el.dispatchEvent(new CustomEvent('cv:cameramove', { bubbles: true, detail: { zoom: f1, panX: x1, panY: y1 } })); }
    })(t0);
  }

  // ResizeObserver where it fires; some embedded contexts throttle it to
  // never, so every path ALSO measures synchronously and on window resize.
  var ro = typeof ResizeObserver !== 'undefined'
    ? new ResizeObserver(function (entries) { for (var i = 0; i < entries.length; i++) measure(entries[i].target); })
    : null;

  function observe(el) {
    if (coupled.indexOf(el) === -1) coupled.push(el);
    measure(el);                       // immediate — the coupling is never pending
    stampMaterials(el);                // decorrelate whatever is already laid out
    if (ro) ro.observe(el);
  }

  function couple() {
    var grounds = document.querySelectorAll('.skin-ground');
    for (var i = 0; i < grounds.length; i++) observe(grounds[i]);
  }

  window.addEventListener('resize', function () { for (var i = 0; i < coupled.length; i++) { measure(coupled[i]); stampMaterials(coupled[i]); } });

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', couple);
  else couple();

  window.CV_WORLD_CAMERA = { FRAME: FRAME, observe: observe, measure: measure, to: to, stampMaterials: stampMaterials };
})();
