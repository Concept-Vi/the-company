/* core/cv-address.js — THE ADDRESS ALGEBRA (spans · nested fractions · LCA) — window.CV_ADDRESS.
 *
 * The spatial theorem as code: children PARTITION a parent's [0,1); a unit is a SPAN, not a point
 * (child k of n owns [(k-1)/n, k/n) — the point 2/3 is the SEAM where child 3 begins); addresses
 * are DERIVED from counts, never assigned (insert a sibling and every address re-derives — an
 * address is a view, never a stored fact that can stale); a path collapses to ONE mixed-radix
 * number and decodes back when the radices are known (zone 3-of-5 in slide 2-of-3 → 7/15).
 *
 * ported-from: counterpart/design@212ba23 engine/prove/resolve.mjs (the zones()/span arithmetic,
 * proven 11/11 against measured pixels) + dna/address.json (the laws), 2026-07-03, glyphic W1 —
 * port-by-COPY; generalized from deck-geometry to ANY frame nesting + given the LCA (the motion
 * face's anchor law: the boundary that must HOLD through a change is the lowest common ancestor
 * of the changers' addresses — derived, never chosen). Zero DOM/framework coupling; loud-fail.
 *
 * The glyphgraph placement law rides on this: a node's slot = its span in its frame, FROZEN at
 * insertion (stable-slot); a drag writes an authored override; growth never re-ranks placed nodes.
 * Proof harness: _demo/verify_address.js (node-runnable).
 */
(function (global) {
  'use strict';
  function fail(msg) { throw new Error('[CV_ADDRESS] ' + msg); }

  // ---- spans: child k (1-based) of n partitions the parent span --------------------------------
  // parent = {start, width} in [0,1); returns the child's span. Derived, never assigned.
  function span(k, n, parent) {
    if (!Number.isInteger(k) || !Number.isInteger(n) || k < 1 || n < 1 || k > n)
      fail('span: need integers 1 <= k <= n, got k=' + k + ' n=' + n);
    var p = parent || { start: 0, width: 1 };
    return { start: p.start + ((k - 1) / n) * p.width, width: p.width / n };
  }

  // ---- a PATH is [[k1,n1],[k2,n2],...] from the root down; encodes to one number ---------------
  function encode(path) {
    if (!Array.isArray(path) || !path.length) fail('encode: path must be a non-empty [[k,n],...]');
    var s = { start: 0, width: 1 };
    for (var i = 0; i < path.length; i++) s = span(path[i][0], path[i][1], s);
    return s;   // {start, width} — start IS the mixed-radix address; width = the extent (1/∏n)
  }

  // ---- decode: given the start value + the radices [n1,n2,...], recover the path ---------------
  function decode(start, radices) {
    if (typeof start !== 'number' || start < 0 || start >= 1) fail('decode: start must be in [0,1)');
    var path = [], x = start, EPS = 1e-9;
    for (var i = 0; i < radices.length; i++) {
      var n = radices[i];
      var k = Math.floor(x * n + EPS) + 1;             // which child span x falls in (1-based)
      if (k > n) k = n;
      path.push([k, n]);
      x = x * n - (k - 1);                              // re-base into the child's [0,1)
    }
    return path;
  }

  // ---- LCA: the deepest shared prefix of two paths — THE ANCHOR LAW ----------------------------
  // (motion face: diff two views by address; the LCA of the changers is the ring that must hold.)
  function lca(pathA, pathB) {
    if (!Array.isArray(pathA) || !Array.isArray(pathB)) fail('lca: two paths required');
    var out = [];
    for (var i = 0; i < Math.min(pathA.length, pathB.length); i++) {
      if (pathA[i][0] === pathB[i][0] && pathA[i][1] === pathB[i][1]) out.push(pathA[i]);
      else break;
    }
    return out;   // [] = only the root holds
  }
  // the LCA over MANY paths (a whole change-set → the one boundary that anchors the transition)
  function lcaAll(paths) {
    if (!Array.isArray(paths) || !paths.length) fail('lcaAll: at least one path');
    return paths.reduce(function (acc, p) { return lca(acc, p); });
  }

  // ---- zones: a named proportion archetype resolved onto a concrete axis length ----------------
  // parts = fractions summing ~1 (e.g. [0.14, 0.72, 0.10]); axisPx = the frame's real size.
  // (counterpart's zones(), generalized to take parts directly — archetype registries supply them.)
  function zones(parts, axisPx) {
    if (!Array.isArray(parts) || !parts.length) fail('zones: parts[] of fractions required');
    if (typeof axisPx !== 'number' || axisPx <= 0) fail('zones: axisPx must be > 0');
    return parts.map(function (p) { return Math.round(p * axisPx); });
  }

  // ---- stable slots: the k-th INSERTION into a frame gets a frozen span ------------------------
  // Capacity grows by doubling when full (existing slots NEVER move — growth is absorbed by
  // halving the pitch for NEW nodes only when the row saturates; the honest left-anchor rule).
  function slotFor(index, capacity) {
    if (!Number.isInteger(index) || index < 0) fail('slotFor: index >= 0 required');
    var cap = capacity || 8;
    while (index >= cap) cap *= 2;
    return { span: span(index + 1, cap), capacity: cap };
  }

  global.CV_ADDRESS = { span: span, encode: encode, decode: decode, lca: lca, lcaAll: lcaAll,
                        zones: zones, slotFor: slotFor };
})(typeof window !== 'undefined' ? window : globalThis);
