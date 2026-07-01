// atomicity/shot.js
// ============================================================================
// CV_SHOT — visual capture + memory. Lets AtomiCity (and Vi) SEE: snapshot the
// selected element (default) or the whole page (optional), keep a capped, FIFO,
// configurable history of those images, and produce before→after pairs so a
// change can be visually diffed.
//
//   • snapshot(el)        → dataURL of just that element + everything inside it
//   • snapshotPage()      → dataURL of the whole page
//   • remember(img, meta) → push into history (capped at `limit`, FIFO)
//   • history()/clear()   → the rolling image memory the chat shows + (on export)
//                            a vision provider receives
//   • limit is adjustable by the user AND the AI (setLimit); 5–10 typical.
//
// Capture uses html2canvas (pinned CDN, loaded lazily). If unavailable it fails
// soft — returns null — and callers fall back to the computed-style diff (text).
// ============================================================================
(function () {
  'use strict';
  const LIB = 'https://unpkg.com/@zumer/snapdom@1.9.11/dist/snapdom.min.js';
  let loading = null;
  const state = { limit: 8, images: [] };       // images: [{id,url,meta,at}]
  const listeners = new Set();
  function on(fn) { listeners.add(fn); return () => listeners.delete(fn); }
  function emit() { for (const fn of listeners) { try { fn(); } catch {} } }

  function ensureLib() {
    if (window.snapdom) return Promise.resolve(window.snapdom);
    if (loading) return loading;
    loading = new Promise((res) => {
      const s = document.createElement('script'); s.src = LIB;
      s.onload = () => res(window.snapdom); s.onerror = () => res(null);
      document.head.appendChild(s);
    });
    return loading;
  }

  async function capture(el) {
    if (!el) return null;
    const lib = await ensureLib(); if (!lib) return null;
    try {
      // snapdom understands modern CSS color (oklch / color-mix), unlike html2canvas
      const canvas = await lib.toCanvas(el, { scale: Math.min(2, window.devicePixelRatio || 1), backgroundColor: null });
      return canvas.toDataURL('image/png');
    } catch (e) { console.warn('[CV_SHOT] capture failed', e); return null; }
  }
  async function snapshot(el) { return capture(el); }
  async function snapshotPage() { return capture(document.querySelector('#atomicity-root') || document.body); }

  function remember(url, meta) {
    if (!url) return null;
    const img = { id: 's' + Date.now().toString(36) + Math.random().toString(36).slice(2, 4), url, meta: meta || {}, at: Date.now() };
    state.images.push(img);
    while (state.images.length > state.limit) state.images.shift();   // FIFO drop
    emit();
    return img;
  }
  function history() { return state.images.slice(); }
  function clear() { state.images = []; emit(); }
  function getLimit() { return state.limit; }
  function setLimit(n) { n = Math.max(1, Math.min(40, parseInt(n, 10) || 8)); state.limit = n; while (state.images.length > n) state.images.shift(); emit(); return n; }

  // a before→after pair around an action: capture, run, capture, remember both.
  async function aroundChange(el, label, run) {
    const before = await snapshot(el);
    let result; try { result = await run(); } catch (e) { result = { error: e.message }; }
    // allow the DOM/paint to settle before the after-shot
    await new Promise(r => requestAnimationFrame(() => setTimeout(r, 60)));
    const after = await snapshot(el);
    const pair = { before, after, label, at: Date.now() };
    if (after) remember(after, { label, kind: 'after' });
    return { pair, result };
  }

  window.CV_SHOT = { snapshot, snapshotPage, capture, remember, history, clear, getLimit, setLimit, aroundChange, on, subscribe: on, state };
  // register config + capability into CV_AI so the AI can adjust its own memory
  if (window.CV_AI) {
    try {
      window.CV_AI.register({
        id: 'shot.setLimit', name: 'Set image memory size', layer: 'capability', family: 'vision',
        description: 'Adjust how many recent screenshots stay in context (FIFO). The AI can tune its own visual memory.',
        surfaces: ['atomicity'], provider: 'host-fs', icon: 'eye', provenance: 'built-in',
        run: a => ({ limit: setLimit(a.params && a.params.n) }),
      }, { silent: true });
      window.CV_AI.register({
        id: 'vision.diff', name: 'See the before/after', layer: 'capability', family: 'vision',
        description: 'Compare a before and after screenshot of a change with the vision provider, so Vi can judge the result and decide whether to continue. Throws in the sandbox (no vision runtime) — callers skip silently and rely on the computed-style diff.',
        surfaces: ['atomicity'], provider: 'vision', behaviours: ['voice.conceptv'], icon: 'eye', provenance: 'built-in',
        async run(a) {
          const p = window.CV_AI.resolveProvider('vision');
          if (!p || !p.runtime || !p.runtime.complete) throw new Error('No vision runtime (export with a vision model to let Vi see changes).');
          return p.runtime.complete({ images: [a.params.before, a.params.after], prompt: 'These are before/after screenshots of a UI change the user asked for. In one short sentence, say whether it achieved the intent ("' + (a.params.intent || 'the requested change') + '") and, if not, what to adjust.' });
        },
      }, { silent: true });
    } catch {}
  }
  console.info('[CV_SHOT] visual capture ready — limit', state.limit);
})();
