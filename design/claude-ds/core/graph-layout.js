// core/graph-layout.js
// ============================================================================
// THE GRAPH LAYOUT ENGINE — window.CV_GRAPH_LAYOUT — the ONE home for
// "position computed from relationships." Both the React DiagramSolver
// (core/DiagramSolver.jsx) and the vanilla skin/board painter
// (system/skin-system.html) resolve node positions THROUGH this — there is
// no second positioner. (analysis/SKINS.md §5 · CLAUDE.md: one engine.)
//
//   solve(graph, {w, h, R}) → { [id]: {x, y} }   in a w×h coordinate space
//
// Types (data, not code branches at the call site): hub · morph · network ·
// pipeline · timeline · quadrant · tree · stack · COLUMN. The board layout is
// `column`: a left hub with orbiting satellites, then evenly-spread columns of
// stacked cards, plus fixed furniture (fx/fy in 0..1). Everything is COMPUTED
// from each node's relational fields (col / order / orbit / hub), never a
// hand-placed pixel — flip one field and the graph re-lays-out.
// ============================================================================
(function () {
  'use strict';

  function solve(graph, opts) {
    opts = opts || {};
    var w = opts.w || 320, h = opts.h || 320, R = opts.R || 130;
    var type = graph.type, nodes = graph.nodes || [], center = graph.center;
    var n = nodes.length, cx = w / 2, cy = h / 2, pos = {};

    function ring(items, radius, ox, oy) {
      var c0x = ox == null ? cx : ox, c0y = oy == null ? cy : oy;
      items.forEach(function (nd, i) {
        var a = -Math.PI / 2 + (i * 2 * Math.PI) / items.length;
        pos[nd.id] = { x: c0x + radius * Math.cos(a), y: c0y + radius * Math.sin(a) };
      });
    }

    switch (type) {
      case 'hub': {
        var c = center || nodes[0].id;
        pos[c] = { x: cx, y: cy };
        ring(nodes.filter(function (nd) { return nd.id !== c; }), R);
        break;
      }
      case 'morph': {
        if (graph.state === 'after') { var c2 = center || nodes[0].id; pos[c2] = { x: cx, y: cy }; ring(nodes.filter(function (nd) { return nd.id !== c2; }), R); }
        else ring(nodes, R);
        break;
      }
      case 'network': ring(nodes, R); break;
      case 'pipeline':
        nodes.forEach(function (nd, i) { pos[nd.id] = { x: 40 + (i * (w - 80)) / Math.max(1, n - 1), y: cy }; });
        break;
      case 'timeline':
        nodes.forEach(function (nd, i) { pos[nd.id] = { x: 40 + (i * (w - 80)) / Math.max(1, n - 1), y: cy + 30 }; });
        break;
      case 'quadrant':
        nodes.forEach(function (nd) { pos[nd.id] = { x: 40 + (nd.x != null ? nd.x : 0.5) * (w - 80), y: h - 40 - (nd.y != null ? nd.y : 0.5) * (h - 80) }; });
        break;
      case 'tree': {
        var root = center || nodes[0].id;
        pos[root] = { x: cx, y: 48 };
        var rest = nodes.filter(function (nd) { return nd.id !== root; });
        rest.forEach(function (nd, i) { pos[nd.id] = { x: 40 + (i * (w - 80)) / Math.max(1, rest.length - 1), y: h - 70 }; });
        break;
      }
      case 'stack':
        nodes.forEach(function (nd, i) { pos[nd.id] = { x: cx, y: 50 + (i * (h - 100)) / Math.max(1, n - 1) }; });
        break;

      // ---- COLUMN — the board layout (analysis/SKINS.md) -----------------
      // Relational fields per node:
      //   hub:true            → the graph root (left anchor)
      //   orbit:'<hubId>'     → satellite on an arc left-of its hub
      //   col:<int>           → column index (0..N); cards stack within a column
      //   fx,fy:0..1          → fixed furniture (chrome), fractional of w/h
      case 'column': {
        var pad = graph.pad || {};
        var colStart = (pad.left != null ? pad.left : 0.20) * w;   // x of column 0
        var colEnd   = (pad.right != null ? pad.right : 0.79) * w; // x of last column
        var rowTop   = (pad.top != null ? pad.top : 0.14) * h;
        // rowBot reserves the bottom band for composer/T-pill furniture so
        // evenly-spread cards never collide with it (verifier: composer was
        // covering "Direction 03").
        var rowBot   = (pad.bottom != null ? pad.bottom : 0.70) * h;
        // orbit/aspect: solve runs in a 0..100 square but the stage is wider
        // than tall (16:10). Scaling the orbit's vertical component by the
        // aspect keeps satellites on a TRUE circle in pixels instead of a
        // vertically-squashed ellipse that clustered them onto the hub.
        var aspect = graph.aspect || 1;

        // furniture first (explicit fractional position)
        nodes.forEach(function (nd) { if (nd.fx != null) pos[nd.id] = { x: nd.fx * w, y: (nd.fy != null ? nd.fy : 0.5) * h }; });

        // the hub
        var hub = nodes.filter(function (nd) { return nd.hub; })[0];
        var hx = (graph.hubX != null ? graph.hubX : 0.12) * w;
        var hy = (graph.hubY != null ? graph.hubY : 0.42) * h;
        if (hub) pos[hub.id] = { x: hx, y: hy };

        // satellites on an arc hugging the hub's LEFT side (upper-left → lower-
        // left); angles stay in (0.5π, 1.5π) so a satellite never pokes right
        // into the first column. Radius clears the hub's + satellite's radii.
        var sats = nodes.filter(function (nd) { return nd.orbit; });
        var sr = (graph.orbitR != null ? graph.orbitR : 0.10) * w;
        // TANGENCY LAW (verifier m0541): a declared orbitR is a *preference*;
        // the FLOOR is derived from the actual rendered rungs. If the consumer
        // stamps measured diameters (hubPx / satPx, + stagePx = the px width
        // this w maps to), the radius can never be less than
        // hubR + satR + gap — satellites are tangent to the hub, never on it.
        // Same doctrine as the composer rule: geometry from measurements,
        // never a fraction that silently drifts when a rung token changes.
        if (graph.hubPx && graph.satPx && graph.stagePx) {
          var clearU = ((graph.hubPx + graph.satPx) / 2 + (graph.gapPx != null ? graph.gapPx : 12)) / graph.stagePx * w;
          if (sr < clearU) sr = clearU;
        }
        sats.forEach(function (nd, i) {
          var a = Math.PI * (0.72 + (i * 0.56) / Math.max(1, sats.length - 1)); // lower-left → upper-left
          pos[nd.id] = { x: hx + sr * Math.cos(a), y: hy + sr * aspect * Math.sin(a) };
        });

        // columns of stacked cards/labels — computed from col + array order
        var cols = {};
        nodes.forEach(function (nd) { if (nd.col != null && !nd.hub && !nd.orbit && nd.fx == null) { (cols[nd.col] = cols[nd.col] || []).push(nd); } });
        var colKeys = Object.keys(cols).map(Number).sort(function (a, b) { return a - b; });
        var maxCol = colKeys.length ? colKeys[colKeys.length - 1] : 0;
        colKeys.forEach(function (ci) {
          var x = maxCol === 0 ? colStart : colStart + (ci * (colEnd - colStart)) / maxCol;
          var items = cols[ci];
          var m = items.length;
          items.forEach(function (nd, i) {
            var y = m === 1 ? (rowTop + rowBot) / 2 : rowTop + (i * (rowBot - rowTop)) / (m - 1);
            // a column header (label node) sits just above its first card
            pos[nd.id] = { x: x, y: y };
          });
        });
        break;
      }

      default: ring(nodes, R);
    }
    return pos;
  }

  // ── THE ROUTING LAW — route(p1, p2, obstacles) → an s-curve that flows
  // BETWEEN blocks, never across them. Deterministic: try the straight
  // s-curve first, then bow the control midline perpendicular to the chord
  // in growing steps until no sample lands inside an inflated obstacle;
  // if nothing fully clears, take the least-colliding bow (loud in console).
  // One home — the demo painter, DiagramSolver and any future thread engine
  // all route through THIS.
  function route(p1, p2, obstacles, opts) {
    var margin = (opts && opts.margin) || 10;
    var infl = (obstacles || []).map(function (r) {
      return { l: r.left - margin, r: r.right + margin, t: r.top - margin, b: r.bottom + margin };
    }).filter(function (o) {
      // an obstacle hugging an ENDPOINT makes the route unclearable by
      // construction (the anchor sits on a block edge) — the endpoints' own
      // neighbourhood is legitimate thread space. The corridor extends a little
      // BEYOND the raw box (2.5× margin): a thread anchored on a card edge must
      // emerge alongside that card, and an immediately-adjacent sibling shares
      // that emergence corridor (m0459 graze).
      var ep = margin * 2.5;
      return !(p1.x > o.l - ep && p1.x < o.r + ep && p1.y > o.t - ep && p1.y < o.b + ep) &&
             !(p2.x > o.l - ep && p2.x < o.r + ep && p2.y > o.t - ep && p2.y < o.b + ep);
    });
    function attempt(bow) {
      var dx = p2.x - p1.x, dy = p2.y - p1.y, len = Math.hypot(dx, dy) || 1;
      var nx = -dy / len, ny = dx / len;
      var mx = (p1.x + p2.x) / 2;
      var c1 = { x: mx + nx * bow, y: p1.y + ny * bow };
      var c2 = { x: mx + nx * bow, y: p2.y + ny * bow };
      var n = 0;
      for (var t = 0.08; t < 0.93; t += 0.06) {
        var u = 1 - t;
        var x = u*u*u*p1.x + 3*u*u*t*c1.x + 3*u*t*t*c2.x + t*t*t*p2.x;
        var y = u*u*u*p1.y + 3*u*u*t*c1.y + 3*u*t*t*c2.y + t*t*t*p2.y;
        for (var i = 0; i < infl.length; i++) {
          var o = infl[i];
          if (x > o.l && x < o.r && y > o.t && y < o.b) { n++; break; }
        }
      }
      return { n: n, c1: c1, c2: c2 };
    }
    var best = null;
    // bow magnitude is CAPPED by the chord: a bow larger than ~45% of the
    // chord length reads as a loop/spiral, not a routed thread (m0427). This is
    // the PREFERRED pass — kept tight for aesthetics.
    var chord = Math.hypot(p2.x - p1.x, p2.y - p1.y);
    var cap = Math.max(30, chord * 0.45);
    var bows = [0, 26, -26, 52, -52, 80, -80, 110, -110, 150, -150, 200, -200].filter(function (b) { return Math.abs(b) <= cap; });
    if (!bows.length) bows = [0];
    for (var i = 0; i < bows.length; i++) {
      var h = attempt(bows[i]);
      if (h.n === 0) { best = h; break; }
      if (!best || h.n < best.n) best = h;
    }
    // FALLBACK CORRIDOR (m0459): a short chord boxed in by a wide card stack
    // (e.g. chain→interviews down the col-0 gutter) has NO in-cap bow that
    // clears — the preferred pass exhausts with samples still inside blocks.
    // Rather than draw a scribble THROUGH a card (which the routing law forbids
    // outright), escalate past the cap: a wide detour around the column's outer
    // edge is a legitimate routed thread. Widths keyed to the obstacle span so
    // the corridor is as tight as it can be while still clearing.
    if (best.n > 0) {
      var reach = 0;
      for (var k = 0; k < infl.length; k++) reach = Math.max(reach, infl[k].r - infl[k].l, infl[k].b - infl[k].t);
      var esc = [];
      [0.75, 0.9, 1.05, 1.2, 1.4, 1.7, 2.0, 2.3].forEach(function (f) { var m = Math.max(chord * 0.6, reach * f); esc.push(m); esc.push(-m); });
      for (var j = 0; j < esc.length; j++) {
        var e = attempt(esc[j]);
        if (e.n === 0) { best = e; break; }
        if (e.n < best.n) best = e;
      }
    }
    if (best.n > 0) console.warn('[graph-layout] route ' + JSON.stringify(p1) + '→' + JSON.stringify(p2) + ' could not fully clear (' + best.n + ' samples inside blocks)');
    var c1 = best.c1, c2 = best.c2;
    return {
      c1: c1, c2: c2, clear: best.n === 0,
      d: 'M' + p1.x.toFixed(1) + ' ' + p1.y.toFixed(1) + ' C ' + c1.x.toFixed(1) + ' ' + c1.y.toFixed(1) + ', ' + c2.x.toFixed(1) + ' ' + c2.y.toFixed(1) + ', ' + p2.x.toFixed(1) + ' ' + p2.y.toFixed(1),
      at: function (t) {
        var u = 1 - t;
        return { x: u*u*u*p1.x + 3*u*u*t*c1.x + 3*u*t*t*c2.x + t*t*t*p2.x,
                 y: u*u*u*p1.y + 3*u*u*t*c1.y + 3*u*t*t*c2.y + t*t*t*p2.y };
      }
    };
  }

  window.CV_GRAPH_LAYOUT = { solve: solve, route: route };
})();
