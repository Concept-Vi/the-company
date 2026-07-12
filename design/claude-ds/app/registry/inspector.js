// app/registry/inspector.js
// ============================================================================
// CV_INSPECTOR — the ONE inspector. The single home for "project a node → an
// editing surface," rendered for ANY kind from ONE source.
//
// The spec asks for this repeatedly (glyphic-system.html §09/§10/§11): "build
// the socket inspector ONCE over CV_NODE.candidates, so the same panel edits a
// token, a glyphic, a panel, or a slide." Until now every surface hand-rolled
// its own picker (the Studio has a hardcoded glyphic FACETS list and renders
// NO sockets at all — half the grammar was invisible). This module is that one
// inspector: it consumes CV_PROJECT.toInspector(node) and renders the WHOLE
// projection generically —
//
//   · value-slots  — each option previewed by RENDERING THE NODE through
//                     CV_NODE.render with that one slot overridden (the preview
//                     rule is universal — it dogfoods the one mechanic — so there
//                     is zero per-facet branching: a recoloured glyph IS the
//                     colour preview, a re-formed glyph IS the form preview).
//   · sockets      — the previously-invisible half: each socket lists its live
//                     candidates (CV_NODE.candidates via toInspector) as a
//                     pick-library; an event-socket is marked and opens an
//                     address. Picking invokes fill-socket / open.
//   · decorators   — what is ALSO true of the node, as badges (audience-filtered
//                     by the projection already).
//   · actions      — applicable verbs as buttons (handed to the host via onAction).
//
// Every mutation goes through the ONE action layer (CV_ACTIONS.invoke) against a
// live node held by the caller — so clicking here is identical to the AI calling
// the same verb (CV_PROJECT.coherent). No second home for "how to edit a node."
//
// API:  CV_INSPECTOR.mount(el, { typeId?, node, audience?, size?, surface?,
//                                onChange?(node), onAction?(action, ctrl) })
//          → a controller { refresh(), descriptor(), node, set(node) }
//       CV_INSPECTOR.describe(target, opts?)   // the raw toInspector descriptor
//
// Pure + window-assigning. Load AFTER project.js / cv-node.js / actions.js /
// axis-core.js + axes / decorators.js / cv-glyphics.js.
// ============================================================================
(function () {
  'use strict';
  var P   = function () { return window.CV_PROJECT; };
  var N   = function () { return window.CV_NODE; };
  var ACT = function () { return window.CV_ACTIONS; };
  var DEC = function () { return window.CV_DECORATORS; };
  var AX  = function () { return window.CV_AXES; };

  function fail(m) { throw new Error('CV_INSPECTOR: ' + m); }
  // inline icon glyph from the symbol single source (CV_ICONS) — so action
  // buttons carry the same icons the Studio drew, with no second icon map.
  function iconSVG(name) {
    var I = window.CV_ICONS; if (!I || !name || !I.get) return '';
    var body = I.get(name); if (!body) return '';
    return '<svg class="ci-ic" viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">' + body + '</svg>';
  }
  function esc(s) { return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }

  // ---- one-time scoped stylesheet (references tokens; no literals) -----------
  var STYLE_ID = 'cv-inspector-style';
  function ensureStyle() {
    if (typeof document === 'undefined' || document.getElementById(STYLE_ID)) return;
    var css = [
      '.cv-insp{font-family:var(--font-body);color:var(--fg-primary);display:flex;flex-direction:column;gap:14px}',
      '.cv-insp .ci-block{display:flex;flex-direction:column;gap:7px}',
      '.cv-insp .ci-fl{display:flex;align-items:baseline;gap:8px}',
      '.cv-insp .ci-fn{font:600 10px/1 var(--font-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--fg-muted)}',
      '.cv-insp .ci-fv{font:500 11px/1 var(--font-mono);color:var(--accent-gold-deep);margin-left:auto}',
      '.cv-insp .ci-acc{font:500 9px/1.3 var(--font-mono);color:var(--fg-soft)}',
      '.cv-insp .ci-tiles{display:flex;flex-wrap:wrap;gap:6px}',
      '.cv-insp .ci-tiles.scroll{flex-wrap:nowrap;overflow-x:auto;padding-bottom:4px}',
      '.cv-insp .ci-tile{display:flex;flex-direction:column;align-items:center;gap:3px;min-width:40px;padding:6px 5px;border:1px solid var(--border-faint);border-radius:9px;background:var(--paper);cursor:pointer;transition:border-color .12s,box-shadow .12s}',
      '.cv-insp .ci-tile:hover{border-color:color-mix(in srgb,var(--accent-gold) 55%,transparent)}',
      '.cv-insp .ci-tile.on{border-color:var(--accent-gold);box-shadow:0 0 0 1px var(--accent-gold) inset}',
      '.cv-insp .ci-tile .cap{font:500 8.5px/1.1 var(--font-mono);color:var(--fg-muted);max-width:54px;text-align:center;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}',
      '.cv-insp .ci-sw{width:26px;height:26px;border-radius:6px;border:1px solid color-mix(in srgb,var(--fg-primary) 10%,transparent)}',
      '.cv-insp .ci-glyph{display:inline-flex;width:30px;height:30px;align-items:center;justify-content:center}',
      '.cv-insp .ci-sock{border:1px dashed color-mix(in srgb,var(--accent-bronze) 38%,transparent);border-radius:11px;padding:11px 12px;background:color-mix(in srgb,var(--accent-gold) 3%,var(--paper));display:flex;flex-direction:column;gap:8px}',
      '.cv-insp .ci-sock.evt{border-color:color-mix(in srgb,var(--status-warning) 50%,transparent)}',
      '.cv-insp .ci-sockhead{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap}',
      '.cv-insp .ci-sockname{font:700 12px/1 var(--font-display);color:var(--fg-primary)}',
      '.cv-insp .ci-badge{font:600 8px/1 var(--font-mono);letter-spacing:.06em;text-transform:uppercase;padding:3px 6px;border-radius:999px;background:color-mix(in srgb,var(--accent-gold) 13%,transparent);color:var(--accent-gold-deep)}',
      '.cv-insp .ci-badge.evt{background:color-mix(in srgb,var(--status-warning) 16%,transparent);color:color-mix(in srgb,var(--status-warning) 86%,var(--fg-primary))}',
      '.cv-insp .ci-cand{display:flex;align-items:center;gap:7px;padding:5px 9px;border:1px solid var(--border-faint);border-radius:8px;background:var(--paper);cursor:pointer;font:500 11px/1.1 var(--font-body);color:var(--fg-secondary)}',
      '.cv-insp .ci-cand:hover{border-color:color-mix(in srgb,var(--accent-gold) 55%,transparent);color:var(--fg-primary)}',
      '.cv-insp .ci-empty{font:400 11px/1.4 var(--font-body);color:var(--fg-soft);font-style:italic}',
      '.cv-insp .ci-decs,.cv-insp .ci-acts{display:flex;flex-wrap:wrap;gap:6px}',
      '.cv-insp .ci-dec{font:600 9.5px/1 var(--font-mono);padding:5px 9px;border-radius:999px;background:color-mix(in srgb,var(--accent-bronze) 9%,transparent);color:var(--accent-bronze-2);border:1px solid color-mix(in srgb,var(--accent-bronze) 22%,transparent)}',
      '.cv-insp .ci-dec.beh{background:color-mix(in srgb,var(--accent-gold) 12%,transparent);color:var(--accent-gold-deep);border-color:color-mix(in srgb,var(--accent-gold) 32%,transparent)}',
      '.cv-insp .ci-act{display:inline-flex;align-items:center;font:600 11px/1 var(--font-body);padding:7px 12px;border-radius:8px;border:1px solid color-mix(in srgb,var(--accent-bronze) 28%,transparent);background:var(--paper);color:var(--fg-primary);cursor:pointer}',
      '.cv-insp .ci-ic{vertical-align:-2px;margin-right:5px}',
      '.cv-insp .ci-play{font:600 9px/1 var(--font-mono);border:1px solid color-mix(in srgb,var(--accent-gold) 40%,transparent);background:var(--paper);color:var(--accent-gold-deep);border-radius:6px;padding:3px 6px;cursor:pointer}',
      '.cv-insp .ci-play.on{background:var(--accent-gold);color:var(--fg-primary)}',
      '.cv-insp .ci-act.primary{background:var(--accent-gold);border-color:var(--accent-gold);color:var(--fg-primary)}',
      '.cv-insp .ci-divider{display:flex;align-items:center;gap:8px;font:600 9px/1 var(--font-mono);letter-spacing:.12em;text-transform:uppercase;color:var(--fg-soft);margin-top:2px}',
      '.cv-insp .ci-divider::after{content:"";flex:1;height:1px;background:var(--border-faint)}',
    ].join('');
    var st = document.createElement('style'); st.id = STYLE_ID; st.textContent = css;
    document.head.appendChild(st);
  }

  // ---- preview: render the NODE (with one slot overridden) through CV_NODE ----
  // the universal preview rule. Returns inner HTML for a tile. Falls back to ''
  // (caller shows the label) when a kind has no visual solver.
  function previewHTML(node, slotName, optId, size, o2) {
    var n = N(); if (!n) return '';
    o2 = o2 || {};
    var spec = Object.assign({}, node || {});
    if (o2.part) {
      // override a PART's slot (ring/fill/symbol) — preview the whole glyphic with
      // just that part changed, so a per-part option previews truthfully.
      var parts = Object.assign({}, spec.parts || {});
      parts[o2.part] = Object.assign({}, parts[o2.part] || {});
      if (slotName) parts[o2.part][slotName] = optId;
      spec.parts = parts;
    } else if (slotName) {
      spec[slotName] = optId;
    }
    var out;
    try { out = n.render(spec, { opts: { size: size || 30, flat: true } }); }
    catch (e) { return ''; }
    if (out && typeof out === 'object' && out.svg) {
      // motion only animates when previewing is ON (else every tile would wiggle)
      var mc = o2.motionOn ? (out.motionClass || '') : '';
      return '<span class="ci-glyph ' + mc + '">' + out.svg + '</span>';
    }
    if (typeof out === 'string' && /^(var\(|#|rgb|hsl|color-mix)/.test(out.trim())) {
      return '<span class="ci-sw" style="background:' + esc(out) + '"></span>';
    }
    return '';
  }

  // current value of a slot on the live node (generic — flattens a colorset {ring,…})
  function currentId(node, slot) {
    var cur = node ? node[slot.name] : undefined;
    if (cur == null) cur = slot.current;
    if (cur && typeof cur === 'object') cur = cur.ring != null ? cur.ring : cur[Object.keys(cur)[0]];
    return cur;
  }

  function structureTarget(o) {
    // what toInspector reads STRUCTURE from. Order matters:
    //   · an explicit Type id wins;
    //   · an already-lensed/canonical node → pass the OBJECT through (toInspector
    //     lenses-or-passes it; we must NOT hand back its `kind` string, or it gets
    //     mis-resolved as a Type id, e.g. a token node's kind "token");
    //   · an instance referencing its Type by id (a panel) → that id;
    //   · otherwise a raw spec (a glyphic spec) or an id string → pass through.
    if (o.typeId) return o.typeId;
    var node = o.node;
    if (node == null) return null;
    if (typeof node === 'object' && node.kind && node.payload !== undefined) return node;
    if (typeof node === 'object' && node.kindId) return node.kindId;
    return node;
  }

  function describe(target, opts) {
    var p = P(); if (!p) fail('CV_PROJECT not loaded');
    var o = (target && (target.node !== undefined || target.typeId)) ? target : { node: target };
    o = Object.assign({}, o, opts || {});
    return p.toInspector(structureTarget(o), { audience: o.audience || null });
  }

  // ---- mount ---------------------------------------------------------------
  function mount(el, opts) {
    if (!el) fail('mount() needs an element');
    ensureStyle();
    opts = opts || {};
    var node = opts.node || null;
    var size = opts.size || 30;
    var motionPreview = false;
    var caps = opts.captions !== false;   // host may hide per-tile captions to match a label-less skin
    var audience = opts.audience || null;
    var surface = opts.surface || 'inspector';

    function ctx() { return { node: node, audience: audience, surface: surface, state: { node: node } }; }
    // Edits route through a host-supplied invoker when given (so the host's
    // undo/log/ctx stay in the loop — adopting CV_INSPECTOR loses no capability);
    // otherwise straight through the one action layer.
    function doInvoke(verb, args) {
      if (opts.invoke) return opts.invoke(verb, args, ctx());
      return ACT().invoke(verb, args, ctx());
    }
    function descriptor() { return P().toInspector(structureTarget(Object.assign({}, opts, { node: node })), { audience: audience }); }

    function setValue(slotName, optId, part) {
      try { doInvoke('set-value', part ? { slot: slotName, value: optId, part: part } : { slot: slotName, value: optId }); }
      catch (e) { /* loud in console, but keep the UI alive */ console.error(e); }
      refresh(); if (opts.onChange) opts.onChange(node, { slot: slotName, value: optId, part: part });
    }
    // current value of a slot — per-part (via the glyphic's own expandParts, the one
    // source for the flat→part mapping) when `part` is set, else whole-node.
    function curOf(s, part) {
      if (part) {
        try { var ep = window.CV_GLYPHIC && window.CV_GLYPHIC.expandParts && window.CV_GLYPHIC.expandParts(window.CV_GLYPHIC.normalize(node || {})); if (ep && ep[part]) return ep[part][s.name]; } catch (e) {}
      }
      return currentId(node, s);
    }
    function fillSocket(sock, candId) {
      var verb = sock.event ? 'open' : 'fill-socket';
      var args = sock.event ? { address: candId } : { socket: sock.name, occupant: candId };
      try { doInvoke(verb, args); } catch (e) { console.error(e); }
      refresh(); if (opts.onChange) opts.onChange(node, { socket: sock.name, occupant: candId });
    }

    // PICK MODE — render ONLY a single-axis value picker (the behaviours panel's
    // "choose a target value" surface, folded into the one inspector). Each value
    // previewed by overriding that axis on a base node (a recoloured/reformed
    // glyph), falling back to a swatch. opts.pick = { axis, current, label, base, onPick }.
    function renderPick() {
      var pk = opts.pick;
      var ax = AX() && AX().has(pk.axis) ? AX().resolve(pk.axis) : null;
      var vals = ax ? ax.values() : [];
      var base = pk.base || node || {};
      var tiles = vals.map(function (v) {
        var pv = previewHTML(base, pk.axis, v.id, 28, {});
        if (!pv && AX() && AX().css(pk.axis, v.id)) pv = '<span class="ci-sw" style="background:' + esc(AX().css(pk.axis, v.id)) + '"></span>';
        return '<button class="ci-tile' + (v.id === pk.current ? ' on' : '') + '" data-pick="' + esc(v.id) + '" title="' + esc(v.label || v.id) + '">' + (pv || '') + (caps ? '<span class="cap">' + esc(v.label || v.id) + '</span>' : '') + '</button>';
      }).join('');
      el.className = (el.className || '').replace(/\bcv-insp\b/g, '').trim() + ' cv-insp';
      el.innerHTML = '<div class="ci-block"><div class="ci-fl"><span class="ci-fn">' + esc(pk.label || ('choose ' + pk.axis)) + '</span></div><div class="ci-tiles' + (vals.length > 12 ? ' scroll' : '') + '">' + tiles + '</div></div>';
      el.querySelectorAll('.ci-tile[data-pick]').forEach(function (b) { b.onclick = function () { if (pk.onPick) pk.onPick(b.getAttribute('data-pick')); }; });
    }

    function render() {
      if (opts.pick) return renderPick();
      var d = descriptor();
      var html = '';

      // one slot → its block HTML. `part` scopes current value, preview override
      // and the eventual set-value to a part (ring/fill/symbol). Used identically
      // for flat, whole-unit and per-part slots — one renderer, no branching.
      function slotBlock(s, part) {
        if (!(s.options && s.options.length)) return '';
        var cur = curOf(s, part);
        var scroll = s.options.length > 12;
        var isMotion = s.axis === 'motion';
        var isSize = s.axis === 'size';
        var curOpt = s.options.filter(function (o) { return o.id === cur; })[0];
        var tiles = s.options.map(function (o, i) {
          var px = scroll ? 24 : 30;
          if (isSize) px = 16 + Math.min(i, 6) * 4;
          var pv = previewHTML(node, s.name, o.id, px, { motionOn: isMotion && motionPreview, part: part });
          var on = (o.id === cur) ? ' on' : '';
          return '<button class="ci-tile' + on + '" data-slot="' + esc(s.name) + '"' + (part ? ' data-part="' + esc(part) + '"' : '') + ' data-val="' + esc(o.id) + '" title="' + esc(o.label || o.id) + '">' +
            (pv || '') + (caps ? '<span class="cap">' + esc(o.label || o.id) + '</span>' : '') + '</button>';
        }).join('');
        var play = isMotion ? '<button class="ci-play' + (motionPreview ? ' on' : '') + '" data-play="1" title="Preview motion">' + (motionPreview ? '\u275a\u275a' : '\u25b6') + '</button>' : '';
        return '<div class="ci-block"><div class="ci-fl"><span class="ci-fn">' + esc(s.name) + '</span>' + play +
          (s.means ? '<span class="ci-acc">' + esc(s.means) + '</span>' : '') +
          '<span class="ci-fv">' + esc(curOpt ? (curOpt.label || curOpt.id) : (cur == null ? '—' : cur)) + '</span></div>' +
          '<div class="ci-tiles' + (scroll ? ' scroll' : '') + '">' + tiles + '</div></div>';
      }

      // PER-PART view when the node exposes part groups (a glyphic): the whole-unit
      // facets first, then a section per part — each part's colour/texture/motion
      // cleanly separate. Otherwise the flat (collapsed) view (back-compat).
      if (d.partGroups && d.partGroups.length) {
        var wh = (d.wholeSlots || []).map(function (s) { return slotBlock(s, null); }).join('');
        if (wh) html += '<div class="ci-group ci-group-whole">' + wh + '</div>';
        d.partGroups.forEach(function (g) {
          var inner = g.slots.map(function (s) { return slotBlock(s, g.part); }).join('');
          if (inner) html += '<div class="ci-group" data-group-part="' + esc(g.part) + '"><div class="ci-divider">' + esc(g.label) + ' \u00b7 part</div>' + inner + '</div>';
        });
      } else {
        (d.slots || []).forEach(function (s) { html += slotBlock(s, null); });
      }

      // ---- sockets (the previously-invisible half of the grammar) ----
      if (d.sockets && d.sockets.length) {
        html += '<div class="ci-divider">sockets · what plugs in</div>';
        d.sockets.forEach(function (sk) {
          var ev = !!sk.event;
          var cands = (sk.candidates || []);
          var body = cands.length
            ? '<div class="ci-tiles">' + cands.map(function (c) {
                return '<button class="ci-cand" data-sock="' + esc(sk.name) + '" data-cand="' + esc(c.id) + '" title="' + esc(c.id) + '">' + esc(c.label || c.id) + '</button>';
              }).join('') + '</div>'
            : '<div class="ci-empty">no candidates accept here yet</div>';
          html += '<div class="ci-sock' + (ev ? ' evt' : '') + '"><div class="ci-sockhead">' +
            '<span class="ci-sockname">' + esc(sk.name) + '</span>' +
            (ev ? '<span class="ci-badge evt">⚡ ' + esc(sk.event) + '</span>' : '') +
            '<span class="ci-badge">◂ ' + esc([].concat(sk.accepts || []).join(' · ')) + (sk.multiple ? ' ×n' : '') + '</span>' +
            (sk.optional ? '<span class="ci-acc">optional</span>' : '') +
            '</div>' + body + '</div>';
        });
      }

      // ---- decorators ----
      if (d.decorators && d.decorators.length) {
        html += '<div class="ci-divider">what\u2019s also true</div><div class="ci-decs">' +
          d.decorators.map(function (dc) {
            var val = (dc.value === true || Array.isArray(dc.value) || dc.value == null) ? '' : ' ' + esc(dc.value);
            return '<span class="ci-dec' + (dc.behaviour ? ' beh' : '') + '">' + esc(dc.id) + val + '</span>';
          }).join('') + '</div>';
      }

      // ---- actions (verbs that aren't the inline set-value/remove) ----
      var acts = (d.actions || []).filter(function (a) { return ['set-value', 'remove'].indexOf(a.id) < 0; });
      if (acts.length) {
        html += '<div class="ci-divider">do more</div><div class="ci-acts">' +
          acts.map(function (a) {
            return '<button class="ci-act' + (a.actionType === 'generate' ? ' primary' : '') + '" data-action="' + esc(a.id) + '">' + iconSVG(a.icon) + esc(a.verb) + '</button>';
          }).join('') + '</div>';
      }

      if (!html) html = '<div class="ci-empty">This node has nothing to compose \u2014 it is a leaf (the floor of the recursion).</div>';
      el.className = (el.className || '').replace(/\bcv-insp\b/g, '').trim() + ' cv-insp';
      el.innerHTML = html;
      wire();
    }

    function wire() {
      el.querySelectorAll('.ci-tile[data-slot]').forEach(function (t) {
        t.onclick = function () { setValue(t.getAttribute('data-slot'), t.getAttribute('data-val'), t.getAttribute('data-part') || null); };
      });
      var d = null;
      el.querySelectorAll('.ci-cand[data-sock]').forEach(function (c) {
        c.onclick = function () {
          if (!d) d = descriptor();
          var name = c.getAttribute('data-sock');
          var sk = (d.sockets || []).filter(function (s) { return s.name === name; })[0] || { name: name };
          fillSocket(sk, c.getAttribute('data-cand'));
        };
      });
      el.querySelectorAll('.ci-play[data-play]').forEach(function (b) {
        b.onclick = function (e) { e.stopPropagation(); motionPreview = !motionPreview; refresh(); };
      });
      el.querySelectorAll('.ci-act[data-action]').forEach(function (b) {
        b.onclick = function () {
          var id = b.getAttribute('data-action');
          var def = ACT() ? ACT().tryResolve(id) : null;
          if (opts.onAction) opts.onAction(def || { id: id }, controller);
        };
      });
    }

    function refresh() { render(); return controller; }

    var controller = {
      refresh: refresh,
      descriptor: descriptor,
      get node() { return node; },
      set: function (n) { node = n; return refresh(); },
    };
    render();
    return controller;
  }

  window.CV_INSPECTOR = { mount: mount, describe: describe, previewHTML: previewHTML };
})();
