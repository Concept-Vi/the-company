// core/render3d.js
// ============================================================================
// THE RENDER3D WELL SOLVER — window.CV_RENDER3D — a SCOPED 3D imagery well.
// Never page-wide: each mount owns one small canvas inside one block well.
//
//   CV_RENDER3D.mount(el, opts?) → dispose()
//
// The scene is COMPUTED FROM THE SKIN'S TOKENS at mount time (the doctrine:
// lights/env are resolutions of the same single sources, not hand-set):
//   key light colour   ← the well's resolved --edge-dot (the skin's accent)
//   ambient colour     ← the resolved --zone-ground (the world's ground)
//   light/dark balance ← ground luminance (light worlds: bright key, soft fill;
//                        dark worlds: dim ambient, crisp rim)
//   surface maps       ← assets/textures/maps/ (plaster normal+roughness from
//                        the user's round-2 pack); opts.maps overrides.
// Re-skinning re-mounts (the page's skin dial rebuilds wells), so the SAME
// well resolves to a different lit world per skin — one mechanic, N worlds.
//
// three.js is lazy-loaded ONCE from CDN on first mount; loud-fail if absent.
// r3f is deliberately not used here: it requires a bundler; this project is
// raw-browser. The solver contract (scoped, token-computed) is what matters.
// ============================================================================
(function () {
  'use strict';

  // three.js dropped UMD builds after r160 — the modern, latest-compatible
  // path is ESM via dynamic import(), which works from a plain classic script
  // with no bundler. One cached import for all wells.
  var THREE_URL = 'https://unpkg.com/three@0.178.0/build/three.module.js';
  var threeReady = null;

  function loadThree() {
    if (threeReady) return threeReady;
    threeReady = import(THREE_URL).then(function (mod) {
      var T = mod.default || mod;
      if (!T || !T.Scene) throw new Error('render3d: three module loaded but has no Scene export');
      return T;
    }).catch(function (e) { threeReady = null; throw new Error('render3d: failed to import three.js ESM from ' + THREE_URL + ' — ' + e.message); });
    return threeReady;
  }

  // resolve a CSS custom property to an sRGB rgb() string THREE can parse.
  // getComputedStyle now serializes colors in their SPECIFIED space (oklch
  // stays oklch — THREE.Color can't read it), so the probe value is pushed
  // through a 1×1 canvas: canvas parses every CSS color space and its pixels
  // read back as sRGB. Loud-fail on an unparseable token (CLAUDE.md §3).
  var _colorCanvas = null;
  function resolveColor(el, varName, fallback) {
    var probe = document.createElement('span');
    probe.style.color = 'var(' + varName + ', ' + (fallback || '#888') + ')';
    el.appendChild(probe);
    var c = getComputedStyle(probe).color;
    probe.remove();
    if (!_colorCanvas) { _colorCanvas = document.createElement('canvas'); _colorCanvas.width = _colorCanvas.height = 1; }
    var ctx = _colorCanvas.getContext('2d', { willReadFrequently: true });
    ctx.fillStyle = '#000'; ctx.fillStyle = c; // second set only sticks if parseable
    if (c && ctx.fillStyle === '#000000' && !/^(#000|black|rgb\(0, 0, 0\))/.test(c.trim())) {
      throw new Error('render3d: token ' + varName + ' resolved to unparseable color "' + c + '"');
    }
    ctx.clearRect(0, 0, 1, 1); ctx.fillRect(0, 0, 1, 1);
    var d = ctx.getImageData(0, 0, 1, 1).data;
    return 'rgb(' + d[0] + ', ' + d[1] + ', ' + d[2] + ')';
  }
  function luminance(rgbStr) {
    var m = rgbStr.match(/[\d.]+/g) || [128, 128, 128];
    return (0.2126 * m[0] + 0.7152 * m[1] + 0.0722 * m[2]) / 255;
  }

  // token url() resolver — shared with CV_SCENE (one home for map-address reads)
  function tokenURL(el, prop) {
    var v = getComputedStyle(el).getPropertyValue(prop).trim();
    var m = v.match(/url\(["']?([^"')]+)["']?\)/);
    return m ? m[1] : null;
  }

  function mount(el, opts) {
    opts = opts || {};
    var disposed = false, cleanup = null;
    loadThree().then(function (T) {
      if (disposed) return;
      var w = el.clientWidth || 160, h = el.clientHeight || 90;
      var renderer = new T.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setSize(w, h);
      renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
      el.appendChild(renderer.domElement);
      renderer.domElement.style.cssText = 'position:relative;z-index:1;display:block;width:100%;height:100%';

      // ---- token-computed lighting rig ----------------------------------
      var accent = resolveColor(el, '--edge-dot', '#c9a34a');
      var ground = resolveColor(el, '--zone-ground', '#202226');
      var lightWorld = luminance(ground) > 0.5;

      var scene = new T.Scene();
      var cam = new T.PerspectiveCamera(32, w / h, 0.1, 50);
      cam.position.set(1.6, 1.2, 3.2); cam.lookAt(0, 0, 0);

      scene.add(new T.AmbientLight(new T.Color(ground), lightWorld ? 1.1 : 0.5));
      var key = new T.DirectionalLight(0xffffff, lightWorld ? 1.4 : 0.9);
      key.position.set(-2, 3, 2); // top-left, the system's one light direction
      scene.add(key);
      var rim = new T.DirectionalLight(new T.Color(accent), lightWorld ? 0.5 : 1.1);
      rim.position.set(2.4, 0.6, -1.8);
      scene.add(rim);

      // ---- surface maps resolved from the SKIN's map-address tokens --------
      // (--skin-map-normal/--skin-map-roughness in tokens/skins.css — the ONE
      // home shared with the CSS depth ladder). opts.maps still overrides.
      var loader = new T.TextureLoader();
      var normalURL = opts.maps ? (opts.mapBase || '../assets/textures/maps/') + opts.maps + '-normal.png' : (tokenURL(el, '--map-face-normal') || tokenURL(el, '--skin-map-normal'));
      var roughURL  = opts.maps ? (opts.mapBase || '../assets/textures/maps/') + opts.maps + '-roughness.png' : (tokenURL(el, '--map-face-rough') || tokenURL(el, '--skin-map-roughness'));
      var diffURL   = tokenURL(el, '--map-face-diffuse'); // pack-004 unlit albedo — the object is MADE OF the skin's face material
      var mat = new T.MeshStandardMaterial({
        color: lightWorld ? 0xe8e0d2 : 0x3a3f4a,
        roughness: 0.85, metalness: lightWorld ? 0.0 : 0.25,
      });
      if (normalURL) loader.load(normalURL, function (t) { if (!disposed) { mat.normalMap = t; mat.normalScale = new T.Vector2(0.7, 0.7); mat.needsUpdate = true; render(); } });
      if (roughURL) loader.load(roughURL, function (t) { if (!disposed) { mat.roughnessMap = t; mat.needsUpdate = true; render(); } });
      if (diffURL) loader.load(diffURL, function (t) { if (!disposed) { t.colorSpace = T.SRGBColorSpace; mat.map = t; mat.needsUpdate = true; render(); } });

      var geo = opts.geometry === 'knot' ? new T.TorusKnotGeometry(0.62, 0.22, 120, 20)
              : new T.IcosahedronGeometry(0.95, 1);
      var mesh = new T.Mesh(geo, mat);
      mesh.rotation.set(0.4, 0.6, 0);
      scene.add(mesh);

      function render() { if (!disposed) renderer.render(scene, cam); }

      // gentle idle turn unless reduced-motion
      var raf = null;
      if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
        (function tick() { if (disposed) return; mesh.rotation.y += 0.004; render(); raf = requestAnimationFrame(tick); })();
      } else render();

      cleanup = function () {
        if (raf) cancelAnimationFrame(raf);
        geo.dispose(); mat.dispose(); renderer.dispose();
        renderer.domElement.remove();
      };
    }).catch(function (e) { console.error('[render3d] ' + e.message); throw e; });

    return function dispose() { disposed = true; if (cleanup) cleanup(); };
  }

  window.CV_RENDER3D = { mount: mount,
    // the shared token→scene environment home — CV_SCENE (core/render-scene.js)
    // resolves through THESE, never re-implements them.
    env: { loadThree: loadThree, resolveColor: resolveColor, luminance: luminance, tokenURL: tokenURL } };
})();
