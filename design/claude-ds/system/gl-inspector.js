// system/gl-inspector.js
// ============================================================================
// THE GL INSPECTOR — a dev window for the scene, and a PROJECTION of the
// --gl-* token registry (never a parallel store). Every control reads its
// current value from getComputedStyle(stage) and writes back a --gl-* token
// on the stage; the scene re-resolves. Nothing here holds state the tokens
// don't already own.
//
//   • CAMERA   — tilt X/Y (live, no rebuild), reset. Reveals the relief the
//                dead-on ortho camera hides.
//   • LIGHTING — light-boost, env-intensity, exposure.
//   • MATERIAL — wall-tint, slab-tint, slab-emissive, emissive-intensity.
//   • RELIEF   — thick-unit, thick-zone, side-tint, zone-dim.
//
// Visible ONLY while the stage is in GL mode (data-scene-live). One button in
// the chrome toggles it. Material/light writes debounce a detach+attach
// (materials are resolved at attach); tilt writes go straight to the live
// handle. A "copy tokens" button dumps the current dial values as CSS so a
// good calibration can be pasted into tokens/skins.css — the one home.
// ============================================================================
(function () {
  'use strict';

  // DIAL SPECS — id maps 1:1 to a --gl-* token. kind drives the control.
  var GROUPS = [
    { name: 'Camera', dials: [
      { t: '--gl-tilt-x', label: 'Tilt X', kind: 'range', min: -0.6, max: 0.6, step: 0.01, live: true },
      { t: '--gl-tilt-y', label: 'Tilt Y', kind: 'range', min: -0.6, max: 0.6, step: 0.01, live: true },
    ] },
    { name: 'Lighting', dials: [
      { t: '--gl-light-boost', label: 'Light boost', kind: 'range', min: 0.2, max: 4, step: 0.05 },
      { t: '--gl-env-intensity', label: 'Env intensity', kind: 'range', min: 0, max: 2, step: 0.05 },
      { t: '--gl-exposure', label: 'Exposure', kind: 'range', min: 0.4, max: 2, step: 0.05 },
    ] },
    { name: 'Material', dials: [
      { t: '--gl-wall-tint', label: 'Wall tint', kind: 'color' },
      { t: '--gl-slab-tint', label: 'Slab tint', kind: 'color' },
      { t: '--gl-slab-emissive', label: 'Slab emissive', kind: 'color' },
      { t: '--gl-slab-emissive-intensity', label: 'Emissive amt', kind: 'range', min: 0, max: 4, step: 0.05 },
    ] },
    { name: 'Relief / depth', dials: [
      { t: '--gl-thick-unit', label: 'Card thickness', kind: 'range', min: 0.5, max: 10, step: 0.1 },
      { t: '--gl-thick-zone', label: 'Zone thickness', kind: 'range', min: 0.2, max: 6, step: 0.1 },
      { t: '--gl-zone-dim', label: 'Zone dim', kind: 'range', min: 0.7, max: 1, step: 0.01 },
      { t: '--gl-side-tint', label: 'Side face', kind: 'color' },
    ] },
  ];

  function readVar(stage, t) { return getComputedStyle(stage).getPropertyValue(t).trim(); }

  // hex normaliser: getComputedStyle returns rgb(...) — <input type=color> needs #rrggbb
  function toHex(v) {
    if (!v) return '#cccccc';
    if (v[0] === '#') return v.length === 4 ? '#' + v[1] + v[1] + v[2] + v[2] + v[3] + v[3] : v;
    var m = v.match(/rgba?\(([^)]+)\)/);
    if (!m) return '#cccccc';
    var p = m[1].split(',').map(function (n) { return Math.max(0, Math.min(255, Math.round(parseFloat(n)))); });
    return '#' + p.slice(0, 3).map(function (n) { return ('0' + n.toString(16)).slice(-2); }).join('');
  }

  function build(stage) {
    if (stage.__glInspector) return stage.__glInspector;

    var panel = document.createElement('div');
    panel.setAttribute('data-gl-inspector', '');
    panel.style.cssText = [
      'position:fixed', 'top:64px', 'right:16px', 'width:264px', 'max-height:calc(100vh - 96px)',
      'overflow:auto', 'z-index:9999', 'font:12px/1.4 ui-sans-serif,system-ui,sans-serif',
      'color:#2b2620', 'background:rgba(250,248,243,0.94)', 'backdrop-filter:blur(14px)',
      '-webkit-backdrop-filter:blur(14px)', 'border:1px solid rgba(120,105,80,0.28)',
      'border-radius:14px', 'box-shadow:0 12px 40px rgba(60,50,35,0.22)', 'padding:0',
      'user-select:none', 'display:none',
    ].join(';');

    var head = document.createElement('div');
    head.style.cssText = 'display:flex;align-items:center;justify-content:space-between;padding:11px 13px;cursor:grab;border-bottom:1px solid rgba(120,105,80,0.18)';
    head.innerHTML = '<strong style="font-weight:650;letter-spacing:.02em">GL scene</strong>';
    var close = document.createElement('button');
    close.textContent = '\u2715';
    close.style.cssText = 'border:0;background:none;font-size:13px;cursor:pointer;color:#8a7d64;padding:2px 4px';
    close.onclick = function () { toggle(stage, false); };
    head.appendChild(close);
    panel.appendChild(head);

    var body = document.createElement('div');
    body.style.cssText = 'padding:6px 13px 12px';
    panel.appendChild(body);

    var rebuildTimer = null;
    function rebuild() {
      clearTimeout(rebuildTimer);
      rebuildTimer = setTimeout(function () {
        if (window.CV_SCENE) { window.CV_SCENE.detach(stage); window.CV_SCENE.attach(stage); }
      }, 140);
    }

    var refreshers = [];

    GROUPS.forEach(function (grp) {
      var h = document.createElement('div');
      h.textContent = grp.name;
      h.style.cssText = 'margin:12px 0 5px;font-weight:650;font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;color:#9a8b6e';
      body.appendChild(h);

      grp.dials.forEach(function (d) {
        var row = document.createElement('label');
        row.style.cssText = 'display:grid;grid-template-columns:1fr auto;gap:6px 8px;align-items:center;margin:5px 0';
        var lab = document.createElement('span');
        lab.textContent = d.label;
        lab.style.cssText = 'grid-column:1;color:#4a4236';
        var out = document.createElement('span');
        out.style.cssText = 'grid-column:2;font-variant-numeric:tabular-nums;color:#8a7d64;font-size:11px';

        var input;
        if (d.kind === 'color') {
          input = document.createElement('input');
          input.type = 'color';
          input.style.cssText = 'grid-column:1/3;width:100%;height:26px;border:1px solid rgba(120,105,80,0.3);border-radius:7px;background:none;cursor:pointer;padding:2px';
          input.oninput = function () { stage.style.setProperty(d.t, input.value); rebuild(); };
        } else {
          input = document.createElement('input');
          input.type = 'range'; input.min = d.min; input.max = d.max; input.step = d.step;
          input.style.cssText = 'grid-column:1/3;width:100%';
          input.oninput = function () {
            stage.style.setProperty(d.t, input.value);
            out.textContent = (+input.value).toFixed(d.step < 0.1 ? 2 : (d.step < 1 ? 1 : 0));
            if (d.live && stage.__cvScene && stage.__cvScene.setTilt) {
              var tx = parseFloat(readVar(stage, '--gl-tilt-x')) || 0;
              var ty = parseFloat(readVar(stage, '--gl-tilt-y')) || 0;
              stage.__cvScene.setTilt(tx, ty);
            } else { rebuild(); }
          };
        }

        row.appendChild(lab);
        if (d.kind !== 'color') row.appendChild(out);
        row.appendChild(input);
        body.appendChild(row);

        refreshers.push(function () {
          var v = readVar(stage, d.t);
          if (d.kind === 'color') { input.value = toHex(v); }
          else { input.value = parseFloat(v) || 0; out.textContent = (+input.value).toFixed(d.step < 0.1 ? 2 : (d.step < 1 ? 1 : 0)); }
        });
      });
    });

    // actions
    var actions = document.createElement('div');
    actions.style.cssText = 'display:flex;gap:7px;margin-top:14px';
    var reset = document.createElement('button');
    reset.textContent = 'Reset';
    reset.style.cssText = 'flex:1;padding:7px;border:1px solid rgba(120,105,80,0.3);border-radius:8px;background:rgba(255,255,255,0.5);cursor:pointer;font:inherit;color:#4a4236';
    reset.onclick = function () {
      GROUPS.forEach(function (g) { g.dials.forEach(function (d) { stage.style.removeProperty(d.t); }); });
      if (window.CV_SCENE) { window.CV_SCENE.detach(stage); window.CV_SCENE.attach(stage); }
      setTimeout(refresh, 220);
    };
    var copy = document.createElement('button');
    copy.textContent = 'Copy tokens';
    copy.style.cssText = reset.style.cssText + ';background:#c9a34a;border-color:#b8923a;color:#2b2410;font-weight:600';
    copy.onclick = function () {
      var lines = [];
      GROUPS.forEach(function (g) { g.dials.forEach(function (d) {
        if (d.live) return; // tilt is a viewport control, not a committed skin value
        lines.push('  ' + d.t + ': ' + readVar(stage, d.t) + ';');
      }); });
      var text = lines.join('\n');
      navigator.clipboard && navigator.clipboard.writeText(text);
      copy.textContent = 'Copied \u2713';
      setTimeout(function () { copy.textContent = 'Copy tokens'; }, 1200);
    };
    actions.appendChild(reset); actions.appendChild(copy);
    body.appendChild(actions);

    // drag the panel by its header
    (function () {
      var down = null;
      head.addEventListener('pointerdown', function (e) {
        if (e.target === close) return;
        down = { x: e.clientX, y: e.clientY, top: panel.offsetTop, left: panel.offsetLeft };
        head.style.cursor = 'grabbing'; head.setPointerCapture(e.pointerId);
      });
      head.addEventListener('pointermove', function (e) {
        if (!down) return;
        panel.style.top = (down.top + e.clientY - down.y) + 'px';
        panel.style.left = (down.left + e.clientX - down.x) + 'px';
        panel.style.right = 'auto';
      });
      head.addEventListener('pointerup', function () { down = null; head.style.cursor = 'grab'; });
    })();

    function refresh() { refreshers.forEach(function (f) { f(); }); }

    document.body.appendChild(panel);
    var api = { panel: panel, refresh: refresh };
    stage.__glInspector = api;
    return api;
  }

  function toggle(stage, on) {
    var api = build(stage);
    if (on === undefined) on = api.panel.style.display === 'none';
    api.panel.style.display = on ? 'block' : 'none';
    if (on) api.refresh();
  }

  window.CV_GL_INSPECTOR = { toggle: toggle, build: build };
})();
