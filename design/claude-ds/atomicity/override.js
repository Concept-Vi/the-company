// atomicity/override.js
// ============================================================================
// CV_OVERRIDE — the layer that makes live changes actually STICK.
//
// Mutating a React-managed node's inline style is wiped on the next render (the
// "screen shivers, nothing changes" bug). Instead we stamp the node with a
// stable attribute (data-cv-ov="N") and write a real CSS rule, keyed by that
// attribute, into a dedicated stylesheet with !important. That:
//   • survives React re-renders (the attribute persists; the rule lives in the
//     global sheet, not on the node),
//   • wins specificity battles (its own sheet + !important),
//   • works on ANY element anywhere on screen, not just ones we render,
//   • is fully reversible and inspectable (clear/list/diff).
//
// This is the single mechanism every live edit flows through — restyle from Vi,
// the inspector, Explore — so "change every part of whatever I click" is real.
// ============================================================================
(function () {
  'use strict';
  let sheet, seq = 0;
  const RULES = new Map();   // ovId -> { el, styles:{prop:val}, selectorText }

  function ensureSheet() {
    if (sheet) return sheet;
    const el = document.createElement('style');
    el.id = 'cv-override-sheet';
    document.head.appendChild(el);
    sheet = el.sheet;
    return sheet;
  }
  function idOf(el) {
    let id = el.getAttribute('data-cv-ov');
    if (!id) { id = 'ov' + (++seq); el.setAttribute('data-cv-ov', id); }
    return id;
  }
  function camelToKebab(p) { return p.replace(/[A-Z]/g, m => '-' + m.toLowerCase()); }
  function tok(v) {
    if (v == null || v === '') return null;
    v = String(v).trim();
    if (v.startsWith('--')) return 'var(' + v + ')';
    return v;
  }
  // accept either a CSS-prop map or a Vi "recipe" (bg/fg/radius/…)
  function toStyleMap(input) {
    const r = input || {}, out = {};
    const direct = ['color', 'background', 'backgroundColor', 'borderRadius', 'boxShadow', 'border', 'fontWeight', 'fontFamily', 'fontSize', 'padding', 'margin', 'letterSpacing', 'lineHeight', 'textAlign', 'gap', 'width', 'height', 'opacity', 'borderColor', 'borderWidth'];
    for (const k of direct) if (r[k] != null) out[camelToKebab(k)] = tok(r[k]);
    if (r.bg != null) out['background'] = tok(r.bg);
    if (r.fg != null) out['color'] = tok(r.fg);
    if (r.radius != null) out['border-radius'] = tok(r.radius);
    if (r.shadow != null) out['box-shadow'] = r.shadow === 'none' ? 'none' : tok(r.shadow);
    if (r.border != null) out['border'] = (r.borderWidth || '1px') + ' solid ' + tok(r.border);
    if (r.weight != null) out['font-weight'] = String(r.weight);
    if (r.font != null) out['font-family'] = tok(r.font);
    if (r.tracking != null) out['letter-spacing'] = r.tracking;
    for (const k in out) if (out[k] == null) delete out[k];
    return out;
  }

  function apply(el, input) {
    if (!el || !el.setAttribute) return null;
    ensureSheet();
    const id = idOf(el);
    const incoming = toStyleMap(input);
    const rec = RULES.get(id) || { el, styles: {}, index: -1 };
    Object.assign(rec.styles, incoming);            // merge → cumulative edits
    const decl = Object.entries(rec.styles).map(([p, v]) => `${p}:${v} !important`).join(';');
    const selector = `[data-cv-ov="${id}"]`;
    // rewrite the rule for this id
    if (rec.index >= 0 && sheet.cssRules[rec.index]) sheet.deleteRule(rec.index);
    rec.index = sheet.insertRule(`${selector}{${decl}}`, sheet.cssRules.length);
    rec.el = el; rec.selectorText = selector;
    RULES.set(id, rec);
    reindex();
    return { id, styles: { ...rec.styles } };
  }
  function reindex() { // indices shift after delete/insert; rebuild map→index
    const order = [...RULES.values()];
    for (let i = 0; i < sheet.cssRules.length; i++) {
      const sel = sheet.cssRules[i].selectorText;
      const rec = order.find(r => r.selectorText === sel);
      if (rec) rec.index = i;
    }
  }
  function clear(el) {
    const id = el && el.getAttribute && el.getAttribute('data-cv-ov');
    if (!id || !RULES.has(id)) return;
    const rec = RULES.get(id);
    if (rec.index >= 0 && sheet.cssRules[rec.index]) sheet.deleteRule(rec.index);
    RULES.delete(id); el.removeAttribute('data-cv-ov'); reindex();
  }
  function clearAll() { for (const rec of [...RULES.values()]) clear(rec.el); }
  function get(el) { const id = el && el.getAttribute && el.getAttribute('data-cv-ov'); return id && RULES.has(id) ? { ...RULES.get(id).styles } : null; }
  function list() { return [...RULES.entries()].map(([id, r]) => ({ id, styles: { ...r.styles }, connected: r.el.isConnected })); }

  // a plain-language + computed diff of what an element looks like now (for Vi)
  function snapshotStyles(el) {
    if (!el) return null;
    const cs = getComputedStyle(el);
    const keys = ['color', 'backgroundColor', 'fontFamily', 'fontSize', 'fontWeight', 'lineHeight', 'letterSpacing', 'borderRadius', 'boxShadow', 'padding', 'margin', 'borderWidth', 'borderColor', 'textAlign', 'display', 'width', 'height'];
    const o = {}; for (const k of keys) o[k] = cs[k];
    return o;
  }
  function diff(before, after) {
    const out = {}; if (!before || !after) return out;
    for (const k in after) if (before[k] !== after[k]) out[k] = { from: before[k], to: after[k] };
    return out;
  }

  window.CV_OVERRIDE = { apply, clear, clearAll, get, list, snapshotStyles, diff, toStyleMap };
  console.info('[CV_OVERRIDE] live override layer ready');
})();
