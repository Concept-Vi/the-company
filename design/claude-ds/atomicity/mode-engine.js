// atomicity/mode-engine.js
// ============================================================================
// CV_MODE — the Modes registry. The interaction layer: what a click DOES, what
// hover shows, what the cursor is, and which behaviours/capabilities are live
// depend on the active MODE. Same shape as the other registries
// (register/resolve/query/activate/subscribe). Modes are data + lifecycle, so
// new ones (annotate, measure, compare…) drop in without touching the shell.
//
//   interaction = f(mode)
//
// A mode: { id, label, icon, hint, cursor, accent?, config{}, onEnter(api),
//           onExit(api), onPick(descriptor, el, api) }
//   • config declares behaviour flags the rest of the app reads
//     (e.g. clicksSelect, navTree, viContext) — single source for "what's on".
//   • onEnter/onExit run real setup/teardown (e.g. start/stop CV_PICK).
//   • the registry drives CV_AI too: entering a mode pushes its behaviours as the
//     active set so Vi's tone/permissions follow the mode.
//
// Two built-ins: OPERATOR (normal — click navigates & edits) and INSPECT (click
// selects any element → Vi context). Loud if you activate an unknown mode.
// ============================================================================
(function () {
  'use strict';
  const MODES = new Map();
  const listeners = new Set();
  let activeId = null;

  function subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); }
  function emit() { for (const fn of listeners) { try { fn(activeId); } catch (e) { console.error('[CV_MODE]', e); } } }

  // the api handed to mode lifecycle hooks — the levers a mode may pull
  const api = {
    pick: (cb) => window.CV_PICK && window.CV_PICK.start(cb),
    stopPick: () => window.CV_PICK && window.CV_PICK.stop(),
    toast: (m) => window.dsaToast && window.dsaToast(m),
    openVi: () => window.ATOMICITY && window.ATOMICITY.setVi && window.ATOMICITY.setVi(true),
    setPicked: (p) => window.ATOMICITY && window.ATOMICITY.setPicked && window.ATOMICITY.setPicked(p),
  };

  function register(mode) {
    if (!mode || !mode.id) throw new Error('[CV_MODE] mode needs an id');
    MODES.set(mode.id, { config: {}, cursor: 'default', icon: 'cursor', ...mode });
    emit(); return mode;
  }
  function get(id) { return MODES.get(id) || null; }
  function all() { return [...MODES.values()]; }
  function query(f) { f = f || {}; return all().filter(m => Object.keys(f).every(k => m[k] === f[k])); }

  function activate(id) {
    const next = MODES.get(id);
    if (!next) throw new Error('[CV_MODE] no mode "' + id + '"');
    if (activeId === id) return next;
    const prev = MODES.get(activeId);
    if (prev && prev.onExit) { try { prev.onExit(api); } catch (e) { console.error('[CV_MODE] onExit', e); } }
    activeId = id;
    // reflect the mode on the document so CSS can respond globally
    document.documentElement.setAttribute('data-mode', id);
    document.body && (document.body.style.cursor = next.cursor || '');
    // push the mode's behaviours as Vi's active set, if any
    if (window.CV_AI && next.behaviours && window.CV_AI.setActiveBehaviours) {
      try { window.CV_AI.setActiveBehaviours(next.behaviours); } catch {}
    }
    if (next.onEnter) { try { next.onEnter(api); } catch (e) { console.error('[CV_MODE] onEnter', e); } }
    emit();
    return next;
  }
  function active() { return MODES.get(activeId) || null; }
  function configOf(key) { const m = active(); return m && m.config ? m.config[key] : undefined; }

  // ---------------- built-in modes ----------------
  register({
    id: 'operator', label: 'Operator', icon: 'cursor', hint: 'Click to navigate and edit — the normal way of working.',
    cursor: 'default', accent: '--accent-bronze',
    config: { clicksSelect: false, navTree: true, viContext: false },
    onEnter(a) { a.stopPick(); },
    onExit() {},
  });

  register({
    id: 'inspect', label: 'Inspect', icon: 'crosshair', hint: 'Click any element on screen to select it and hand it to Vi.',
    cursor: 'crosshair', accent: '--accent-gold',
    config: { clicksSelect: true, navTree: false, viContext: true },
    onEnter(a) {
      // persistent pick: re-arm after each capture so you can keep selecting
      const loop = () => a.pick((d, el) => { (window.ATOMICITY && window.ATOMICITY.pickElement ? window.ATOMICITY.pickElement(d, el) : (a.setPicked({ ...d, _el: el }), a.openVi())); if (active() && active().id === 'inspect') setTimeout(loop, 60); });
      loop();
    },
    onExit(a) { a.stopPick(); },
  });

  function describe() {
    return { active: activeId, modes: all().map(m => ({ id: m.id, label: m.label, config: m.config })) };
  }

  window.CV_MODE = { register, get, all, query, activate, active, configOf, describe, subscribe, MODES };
  // default to operator once the DOM is ready
  if (document.body) activate('operator'); else document.addEventListener('DOMContentLoaded', () => activate('operator'));
  console.info('[CV_MODE] mode registry ready — operator · inspect');
})();
