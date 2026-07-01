// atomicity/scan-engine.js
// ============================================================================
// CV_SCAN — the Scanner registry. The fifth-shape registry (register/resolve/
// query/subscribe), but for KNOWLEDGE THE SYSTEM HAS ABOUT ITSELF that isn't in
// a hand-authored catalogue: where every token is actually used, where the
// @dsCard/@template tags live, and the open TODOs. You register WHAT to scan
// (sources) and WHAT to look for (extractors); the engine runs them over the
// whole project, builds live indexes, and keeps them fresh on its own — on load,
// on an interval, and when the tab regains focus. No manual rebuild.
//
//   scan-index = f(sources × extractors), continuously
//
// SOURCES resolve a list of {path, text} units:
//   • cssom        — the live document.styleSheets (always current, no fetch)
//   • manifest     — every file the manifest references (cards, components,
//                    globalCssPaths, templates) → auto-grows as the DS grows
//   • extra-styles — curated app/kit stylesheets not in the manifest
//   • host-tree    — when a CV_HOST runtime can list+read (i.e. exported with fs
//                    or MCP), walk the REAL repo tree → full, intervention-free
// EXTRACTORS pull facts: token-usage (var(--x)), dscard, template, todo.
//
// Loud where it must be (no source/extractor at all → throw); per-file fetch
// misses are collected into report(), not swallowed silently — discovery is
// best-effort by nature.
// ============================================================================

(function () {
  'use strict';
  const SOURCES = new Map();
  const EXTRACTORS = new Map();
  const INDEXES = {};            // extractorId -> Map(key -> [{file, text}])
  const CACHE = new Map();       // path -> { hash, text }
  const REPORT = { errors: [], files: 0, lastRun: 0, ms: 0, runs: 0 };
  const listeners = new Set();
  let running = false, timer = null, lastSig = '';

  function subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); }
  function notify() { for (const fn of listeners) { try { fn(); } catch (e) { console.error('[CV_SCAN]', e); } } }
  function hash(s) { let h = 5381; for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0; return h; }

  // -- registration ---------------------------------------------------------
  function registerSource(s) {
    if (!s || !s.id || typeof s.resolve !== 'function') throw new Error('[CV_SCAN] source needs {id, resolve()}');
    SOURCES.set(s.id, { enabled: true, ...s }); notify(); return s;
  }
  function registerExtractor(e) {
    if (!e || !e.id || !(e.re instanceof RegExp)) throw new Error('[CV_SCAN] extractor needs {id, re}');
    EXTRACTORS.set(e.id, { key: m => m[1], ...e }); notify(); return e;
  }

  // -- the run --------------------------------------------------------------
  async function run() {
    if (running) return; running = true;
    const t0 = performance.now();
    REPORT.errors = [];
    const next = {}; for (const id of EXTRACTORS.keys()) next[id] = new Map();
    const seen = new Set();
    let fileCount = 0;

    for (const src of SOURCES.values()) {
      if (!src.enabled) continue;
      let units = [];
      try { units = await src.resolve() || []; }
      catch (e) { REPORT.errors.push({ source: src.id, error: e.message }); continue; }
      for (const u of units) {
        if (!u || u.text == null) continue;
        if (u.path && seen.has(u.path)) continue;     // de-dupe across sources
        if (u.path) seen.add(u.path);
        fileCount++;
        for (const ex of EXTRACTORS.values()) {
          if (ex.accept && !ex.accept(u.path || '')) continue;
          const re = new RegExp(ex.re.source, ex.re.flags.includes('g') ? ex.re.flags : ex.re.flags + 'g');
          let m;
          while ((m = re.exec(u.text))) {
            let key; try { key = ex.key(m); } catch { key = null; }
            if (key == null) continue;
            const arr = next[ex.id].get(key) || []; arr.push({ file: u.path || '(inline)', text: (m[0] || '').slice(0, 120) });
            next[ex.id].set(key, arr);
            if (m.index === re.lastIndex) re.lastIndex++;
          }
        }
      }
    }

    for (const id in next) INDEXES[id] = next[id];
    REPORT.files = fileCount; REPORT.runs++; REPORT.ms = Math.round(performance.now() - t0); REPORT.lastRun = Date.now();
    running = false;
    const sig = Object.entries(INDEXES).map(([k, m]) => k + ':' + m.size).join('|') + '#' + fileCount;
    if (sig !== lastSig) { lastSig = sig; notify(); }
    return INDEXES;
  }

  // -- continuous -----------------------------------------------------------
  function start(intervalMs) {
    stop();
    run();
    timer = setInterval(() => { if (document.visibilityState === 'visible') run(); }, intervalMs || 45000);
    document.addEventListener('visibilitychange', onVis);
  }
  function onVis() { if (document.visibilityState === 'visible' && Date.now() - REPORT.lastRun > 10000) run(); }
  function stop() { if (timer) clearInterval(timer); timer = null; document.removeEventListener('visibilitychange', onVis); }

  // -- fetch helper (cached by content; tolerant) ---------------------------
  async function fetchUnit(path) {
    try {
      const res = await fetch('../' + path, { cache: 'no-store' });
      if (!res.ok) { REPORT.errors.push({ file: path, error: 'HTTP ' + res.status }); return null; }
      const text = await res.text(); const h = hash(text);
      CACHE.set(path, { hash: h, text });
      return { path, text };
    } catch (e) { REPORT.errors.push({ file: path, error: e.message }); return null; }
  }
  async function fetchAll(paths) {
    const out = []; const uniq = [...new Set(paths)].filter(Boolean);
    await Promise.all(uniq.map(async p => { const u = await fetchUnit(p); if (u) out.push(u); }));
    return out;
  }

  // ======================= BUILT-IN SOURCES ===============================
  // live stylesheets — always current, zero fetch
  registerSource({
    id: 'cssom', description: 'The live document.styleSheets — the actual running styles, always current.',
    resolve() {
      const out = [];
      for (const sheet of Array.from(document.styleSheets)) {
        let rules; try { rules = sheet.cssRules; } catch { continue; } if (!rules) continue;
        let text = ''; for (const r of Array.from(rules)) text += r.cssText + '\n';
        out.push({ path: sheet.href ? sheet.href.split('/').slice(-2).join('/') : '(inline styles)', text });
      }
      return out;
    },
  });

  // everything the manifest references — grows automatically with the DS
  registerSource({
    id: 'manifest', description: 'Every file the design-system manifest references — cards, component sources, global CSS, templates. Self-grows as the system grows.',
    async resolve() {
      const m = (window.ATLAS && window.ATLAS.manifest) || {};
      const paths = [
        ...(m.cards || []).map(c => c.path),
        ...(m.components || []).map(c => c.sourcePath),
        ...(m.globalCssPaths || []),
        ...(m.templates || []).map(t => t.entryPath).filter(Boolean),
      ];
      return fetchAll(paths);
    },
  });

  // curated stylesheets the manifest doesn't list (app + kits)
  registerSource({
    id: 'extra-styles', description: 'Curated app/kit stylesheets outside the manifest (the consumer chrome). Extend via CV_SCAN.registerSource.',
    paths: ['app/app.css', 'app/deck.css', 'app/workshop.css', 'app/registry.css', 'app/imagery.css',
            'ui_kits/platform/platform.css', 'ui_kits/vi/vi.css', 'ui_kits/virtual-hub/hub.css',
            'tonal-zoning.css', 'atomicity/atomicity.css'],
    async resolve() { return fetchAll(this.paths); },
  });

  // the REAL repo tree — only when a CV_HOST runtime can list+read (export/MCP)
  registerSource({
    id: 'host-tree', description: 'Walks the real repository via a connected CV_HOST runtime (file access / MCP). Dormant in the sandbox; full coverage once exported.',
    async resolve() {
      const H = window.CV_HOST; if (!H || !H.best || !H.best('list') || !H.best('read')) return [];
      const exts = /\.(css|jsx|tsx|ts|js|html)$/i; const skip = /(^|\/)(node_modules|_archive|_ds_bundle|\.)/;
      const out = []; const seen = new Set();
      async function walk(dir, depth) {
        if (depth > 6) return;
        let entries; try { entries = await H.list(dir); } catch { return; }
        for (const e of entries || []) {
          const p = dir ? dir + '/' + e.name : e.name; if (skip.test(p)) continue;
          if (e.kind === 'directory') await walk(p, depth + 1);
          else if (exts.test(e.name) && !seen.has(p)) { seen.add(p); try { out.push({ path: p, text: await H.read(p) }); } catch {} }
        }
      }
      await walk('', 0);
      return out;
    },
  });

  // ======================= BUILT-IN EXTRACTORS ============================
  registerExtractor({ id: 'token-usage', description: 'Every var(--token) reference — the real usage graph.', re: /var\(\s*(--[a-z0-9-]+)/gi, key: m => m[1] });
  registerExtractor({ id: 'dscard', description: '@dsCard specimen tags.', re: /@dsCard[^\n]*?name="([^"]+)"/g, key: m => m[1] });
  registerExtractor({ id: 'template', description: '@template starter tags.', re: /@template[^\n]*?name="([^"]+)"/g, key: m => m[1] });
  registerExtractor({ id: 'todo', description: 'Open work — TODO / FIXME / HACK / @todo notes.', re: /(?:TODO|FIXME|HACK|@todo)\b[:\s-]*([^\n*]{0,140})/gi, key: () => 'todo' });

  // ======================= QUERIES ========================================
  function index(id) { return INDEXES[id] || new Map(); }
  function usage(tokenName) {
    const hits = index('token-usage').get(tokenName) || [];
    const byFile = {}; for (const h of hits) byFile[h.file] = (byFile[h.file] || 0) + 1;
    const files = Object.entries(byFile).map(([path, count]) => ({ path, count })).sort((a, b) => b.count - a.count);
    return { token: tokenName, total: hits.length, files, selectors: cssomSelectors(tokenName).slice(0, 8) };
  }
  function cssomSelectors(tokenName) {
    const needle = 'var(' + tokenName, out = [];
    for (const sheet of Array.from(document.styleSheets)) {
      let rules; try { rules = sheet.cssRules; } catch { continue; } if (!rules) continue;
      for (const r of Array.from(rules)) { if (r.style && r.cssText.includes(needle) && r.selectorText) out.push(r.selectorText); if (out.length > 12) return out; }
    }
    return out;
  }
  function todos() { return (index('todo').get('todo') || []).map(h => ({ file: h.file, text: h.text })); }
  function tags() { return { dscard: [...index('dscard').keys()], template: [...index('template').keys()] }; }

  function describe() {
    return {
      sources: [...SOURCES.values()].map(s => ({ id: s.id, description: s.description, enabled: s.enabled })),
      extractors: [...EXTRACTORS.values()].map(e => ({ id: e.id, description: e.description, keys: index(e.id).size })),
      report: { ...REPORT, errorCount: REPORT.errors.length },
      continuous: !!timer,
    };
  }
  function stats() { return { files: REPORT.files, lastRun: REPORT.lastRun, runs: REPORT.runs, ms: REPORT.ms, tokensTracked: index('token-usage').size, todos: (index('todo').get('todo') || []).length, errors: REPORT.errors.length }; }

  window.CV_SCAN = {
    registerSource, registerExtractor, SOURCES, EXTRACTORS,
    run, start, stop, get running() { return running; },
    index, indexes: INDEXES, usage, todos, tags,
    report: () => REPORT, stats, describe, subscribe,
  };
  console.info('[CV_SCAN] scanner registry ready — sources:', [...SOURCES.keys()].join(', '));
})();
