// core/morph.js
// ============================================================================
// THE MORPH LAW — "nothing teleports." The FLIP helper that tokens/motion.css
// promised ("A helper component will wrap this") but was never built.
//
// One home for every layout transition in the system. A caller describes the
// MUTATION (change data-skin, expand a card, re-solve the graph); this measures
// First rects, runs the mutation, measures Last rects, inverts each moved
// element with a transform, and plays it to zero over the motion tokens. State
// changes become MOTION by construction — the "animated realism machine" the
// doctrine calls for (DESIGN-LANGUAGE §24).
//
//   CV_MORPH.flip(root, mutate, opts?)
//     root    — the element whose descendants may move
//     mutate  — () => void, performs the DOM/attr change (may be async-safe:
//               if it returns a value it's awaited)
//     opts.select   — selector for participants (default '[data-morph-id]')
//     opts.idAttr   — attribute holding a stable identity (default 'data-morph-id')
//     opts.stagger  — 'world' (delay ∝ distance from the wall centre — the
//                     coordinated-sand ripple) | 'none' (default 'world')
//     opts.settle   — extra material "sand" settle (scale 0.996→1) (default true)
//
// Identity: only elements present with the SAME id before AND after are FLIPped
// (they move). New ids get the enter ramp; departed ids get exit. Nothing jumps.
// ============================================================================
(function () {
  'use strict';

  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  function px(v) { return (typeof v === 'number' ? v : parseFloat(v)) || 0; }

  function readToken(name, fallback) {
    var v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    return v || fallback;
  }

  function rectMap(root, sel, idAttr) {
    var map = {};
    Array.prototype.forEach.call(root.querySelectorAll(sel), function (el) {
      var id = el.getAttribute(idAttr);
      if (id) map[id] = el.getBoundingClientRect();
    });
    return map;
  }

  function flip(root, mutate, opts) {
    opts = opts || {};
    var sel = opts.select || '[data-morph-id]';
    var idAttr = opts.idAttr || 'data-morph-id';
    var stagger = opts.stagger || 'world';
    var settle = opts.settle !== false;

    var dur = px(readToken('--dur-move', '280ms'));
    var durEnter = px(readToken('--dur-enter', '360ms'));
    var ease = readToken('--ease-emphasized', 'cubic-bezier(0.2,0,0,1)');

    if (reduce || !dur) { var r = mutate(); return Promise.resolve(r); }

    var first = rectMap(root, sel, idAttr);
    var rootRect = root.getBoundingClientRect();
    var cx = rootRect.left + rootRect.width / 2;
    var cy = rootRect.top + rootRect.height / 2;
    var maxDist = Math.hypot(rootRect.width, rootRect.height) / 2 || 1;

    return Promise.resolve(mutate()).then(function () {
      var last = rectMap(root, sel, idAttr);
      window.__cvMorphLast = { first: Object.keys(first).length, last: Object.keys(last).length, applied: 0, moved: 0 };

      Array.prototype.forEach.call(root.querySelectorAll(sel), function (el) {
        var id = el.getAttribute(idAttr);
        var f = first[id], l = last[id];
        if (!l) return;

        // per-element delay ∝ distance from the wall centre — the ripple that
        // makes a skin change read as coordinated sand, not a flat cut.
        var delay = 0;
        if (stagger === 'world') {
          var d = Math.hypot((l.left + l.width / 2) - cx, (l.top + l.height / 2) - cy);
          delay = Math.round((d / maxDist) * (dur * 0.35));
        }

        if (!f) {
          // ENTER — new block: ramp in from the settle scale.
          el.style.transition = 'none';
          el.style.transformOrigin = '50% 50%';
          el.style.opacity = '0';
          el.style.transform = 'scale(0.985)';
          requestAnimationFrame(function () {
            el.style.transition = 'transform ' + durEnter + 'ms ' + ease + ' ' + delay + 'ms, opacity ' + durEnter + 'ms ' + ease + ' ' + delay + 'ms';
            el.style.opacity = '1';
            el.style.transform = '';
          });
          clear(el, durEnter + delay);
          return;
        }

        // INVERT — moved/resized block.
        var dx = f.left - l.left;
        var dy = f.top - l.top;
        var sx = f.width / (l.width || 1);
        var sy = f.height / (l.height || 1);
        var moved = Math.abs(dx) > 0.5 || Math.abs(dy) > 0.5 || Math.abs(sx - 1) > 0.005 || Math.abs(sy - 1) > 0.005;
        var s0 = settle ? 0.996 : 1;

        el.style.transition = 'none';
        el.style.transformOrigin = '0 0';
        el.style.transform = moved
          ? 'translate(' + dx + 'px,' + dy + 'px) scale(' + (sx * s0) + ',' + (sy * s0) + ')'
          : (settle ? 'scale(' + s0 + ')' : '');
        window.__cvMorphLast.applied++; if (moved) window.__cvMorphLast.moved++;

        requestAnimationFrame(function () {
          el.style.transition = 'transform ' + dur + 'ms ' + ease + ' ' + delay + 'ms';
          el.style.transform = '';
        });
        clear(el, dur + delay);
      });
    });

    function clear(el, ms) {
      setTimeout(function () {
        el.style.transition = '';
        el.style.transform = '';
        el.style.transformOrigin = '';
        el.style.opacity = '';
      }, ms + 40);
    }
  }

  // ── CROSSFADE ──────────────────────────────────────────────────────────
  // Material tokens can't tween (CSS url() backgrounds are discrete). The
  // honest dissolve: freeze a SNAPSHOT of the current skin (a clone tagged
  // with the OLD skin scope), apply the change underneath, and fade the
  // snapshot out over the page duration. Combined with flip()'s settle
  // ripple, a skin swap reads as coordinated sand, not a hard cut.
  //   root       — the skin-scoped element (carries data-skin)
  //   oldSkin    — the data-skin value BEFORE the change
  //   apply      — () => void, performs the skin change (+ rebuild)
  function crossfadeSkin(root, oldSkin, apply) {
    var durPage = px(readToken('--dur-page', '480ms'));
    if (reduce || !durPage || !oldSkin) { apply(); return; }

    var host = root.parentNode;
    var rect = root.getBoundingClientRect();
    var hostRect = host.getBoundingClientRect();
    var ghost = root.cloneNode(true);
    // the clone paints the OLD world; strip live ids so nothing double-binds.
    // SCENE-LIVE grounds: the GL canvas clones BLANK and data-scene-live would
    // strip every card surface from the snapshot — remove both so the ghost
    // falls back to the old skin's full CSS painting.
    ghost.setAttribute('data-skin', oldSkin);
    ghost.removeAttribute('data-scene-live');
    Array.prototype.forEach.call(ghost.querySelectorAll('[data-scene-canvas]'), function (c) { c.remove(); });
    ghost.removeAttribute('id');
    Array.prototype.forEach.call(ghost.querySelectorAll('[id]'), function (n) { n.removeAttribute('id'); });
    ghost.style.position = 'absolute';
    ghost.style.left = (rect.left - hostRect.left) + 'px';
    ghost.style.top = (rect.top - hostRect.top) + 'px';
    ghost.style.width = rect.width + 'px';
    ghost.style.height = rect.height + 'px';
    ghost.style.margin = '0';
    ghost.style.pointerEvents = 'none';
    ghost.style.zIndex = '9999';
    ghost.setAttribute('aria-hidden', 'true');
    ghost.setAttribute('data-skin-ghost', '');
    if (getComputedStyle(host).position === 'static') host.style.position = 'relative';
    host.appendChild(ghost);

    apply();

    var anim = ghost.animate(
      [{ opacity: 1 }, { opacity: 0 }],
      { duration: durPage, easing: readToken('--ease-emphasized', 'ease'), fill: 'forwards' }
    );
    var removed = false;
    function removeGhost() { if (removed) return; removed = true; if (ghost.parentNode) ghost.parentNode.removeChild(ghost); }
    anim.onfinish = removeGhost;
    // GUARANTEED removal: if the animation clock stalls (hidden iframe,
    // throttled tab) onfinish may never fire — the ghost must still leave.
    setTimeout(removeGhost, durPage + 400);
  }

  // ── EXPAND — a block morphs into the SCREEN rung ─────────────────────────
  // Universal: any block with a stable identity expands to fill its stage
  // (the page is itself a block — expanding is just moving UP the ladder),
  // through the SAME flip law. Toggle: call again (or Esc) to collapse.
  //   CV_MORPH.expand(el, opts?) → true (expanded) | false (collapsed)
  //   opts.stage  — the stage element (default: closest .skin-ground)
  //   opts.pad    — screen inset (default: the control rung --glyph-d)
  //   opts.camera — false to skip the coupled camera move (default on:
  //                 expanding = the camera stepping toward the wall)
  function expand(el, opts) {
    opts = opts || {};
    var stage = opts.stage || el.closest('.skin-ground') || el.parentElement;
    var isOpen = el.classList.contains('is-expanded');
    var pad = opts.pad != null ? opts.pad
      : (px(getComputedStyle(el).getPropertyValue('--glyph-d')) || 44);
    var cam = opts.camera !== false && window.CV_WORLD_CAMERA && window.CV_WORLD_CAMERA.to;

    if (!isOpen) {
      el.__cvPrior = { left: el.style.left, top: el.style.top, width: el.style.width,
        height: el.style.height, translate: el.style.translate, zIndex: el.style.zIndex };
      var sb = stage.getBoundingClientRect();
      flip(stage, function () {
        el.classList.add('is-expanded');
        stage.classList.add('has-expanded');
        el.style.left = pad + 'px'; el.style.top = pad + 'px';
        el.style.width = (sb.width - pad * 2) + 'px';
        el.style.height = (sb.height - pad * 2) + 'px';
        el.style.translate = '0 0'; el.style.zIndex = '30';
      }, { stagger: 'none', settle: false });
      if (cam) window.CV_WORLD_CAMERA.to(stage, { zoom: opts.cameraZoom || 1.05 });
      bindCollapse();
    } else {
      var p = el.__cvPrior || {};
      flip(stage, function () {
        el.classList.remove('is-expanded');
        stage.classList.remove('has-expanded');
        el.style.left = p.left || ''; el.style.top = p.top || '';
        el.style.width = p.width || ''; el.style.height = p.height || '';
        el.style.translate = p.translate || ''; el.style.zIndex = p.zIndex || '';
      }, { stagger: 'none', settle: false });
      if (cam) window.CV_WORLD_CAMERA.to(stage, { zoom: 1 });
    }
    return !isOpen;
  }

  var escBound = false;
  function bindCollapse() {
    if (escBound) return; escBound = true;
    document.addEventListener('keydown', function (e) {
      if (e.key !== 'Escape') return;
      var open = document.querySelector('.is-expanded');
      if (open) expand(open);
    });
  }

  window.CV_MORPH = { flip: flip, crossfadeSkin: crossfadeSkin, expand: expand };
})();
