// ============================================================================
// build-system-map.js — the CANONICAL generator for the System Map model.
//
// SINGLE SOURCE of the codebase model. system/system-map.json is its OUTPUT,
// never hand-edited. Re-run this to regenerate the model after disk changes
// (Piece 1b: a future file-watch calls buildSystemMap() on change + re-emits;
// today the agent runs it via run_script, and the canvas re-fetches the JSON).
//
// Environment-agnostic: pass in { ls, readFile } so it runs anywhere those
// exist (the run_script sandbox, a Node watcher, etc.).
//
//   const model = await buildSystemMap({ ls, readFile });
//   await saveFile('system/system-map.json', JSON.stringify(model));
//
// Model shape (version 2):
//   nodes[]   {id,name,path,parent,type:'file'|'folder',ext,role,size,defines[],uses[]}
//   edges[]   {from,to,kind:'contains'|'loads'|'uses:<GLOBAL>', type:'contains'|'loads'|'resolves'}
//             type = the bidirectional-verb edge family (see EDGE_TYPES in system-map.html):
//             contains↔sits-inside, loads↔loaded-by, resolves-from↔resolves-into.
//   globals[] {global,node}            — every window.CV_* and its defining file
//   roleCounts{}, scanned[], generatedAt, version
// ============================================================================

// Compiled / generated / transient artifacts the map must NOT show.
const SKIP = new Set([
  '_ds_bundle.js', '_ds_manifest.json', '_adherence.oxlintrc.json',
  'system-map.json', 'system-map.tmp.json', '_shot.png'
]);
const CODE = new Set(['js','jsx','ts','tsx','mjs','html','css']); // files read for metadata
const isDot = n => n.startsWith('.');

// ---- role classification (the one place a file's system-membership is decided) ----
// NOTE: this mirrors the design-system's own grouping. When a file moves system,
// change it here and the whole map re-colours from one edit.
function classifyRole(p, ext) {
  if (p.startsWith('_archive-v1')) return 'archive';
  if (p.startsWith('_ingest'))     return 'ingest';
  if (p.startsWith('inspo'))       return 'inspo';
  if (p.startsWith('uploads'))     return 'upload';
  if (p.startsWith('screenshots') || p.includes('_qa/shots') || p.includes('_qa/01-imagery')) return 'shot';
  if (p.startsWith('tokens/') && ext === 'css') return 'token';
  if (['colors_and_type.css','styles.css','tonal-zoning.css'].includes(p)) return 'token';
  if (p === 'axes/axis-core.js') return 'axis-core';
  if (p.startsWith('axes/') && /-axis\.js$/.test(p)) return 'axis';
  if (p.startsWith('axes/') && ext === 'css') return 'axis-css';
  if (p.startsWith('axes/') && ext === 'js') return 'axis';
  if (p === 'assets/icons/cv-glyphics.js') return 'glyphic-core';
  if (p === 'assets/icons/cv-glyphic.css') return 'glyphic-css';
  if (p === 'assets/icons/cv-meaning.js') return 'meaning';
  if (['assets/icons/cv-shapes.js','assets/icons/cv-icons.js','assets/icons/cv-vi-glyph.js'].includes(p)) return 'value-source';
  if (p.startsWith('app/registry/') && ext === 'js') return 'registry';
  if (p.startsWith('app/ai/')) return 'ai';
  if (p.startsWith('core/') && ['jsx','ts','js'].includes(ext)) return 'engine';
  if (p.startsWith('components/') && (ext === 'jsx' || ext === 'ts' || p.endsWith('.d.ts'))) return 'component';
  if (p.startsWith('templates/')) return 'template';
  if (p.startsWith('ui_kits/')) return 'ui-kit';
  if (p.startsWith('atomicity/')) return 'atomicity';
  if (p.startsWith('specimens/') && ext === 'html') return 'specimen';
  if ((p.startsWith('preview/') || p.startsWith('system/')) && ext === 'html') return 'card';
  if (p.startsWith('app/')) return 'app';
  if (ext === 'md') return 'doc';
  if (['png','jpg','jpeg','gif','webp','svg'].includes(ext)) return 'other';
  if (ext === 'html') return 'card';
  return 'other';
}

// ---- metadata regexes ----
const DEF_RE = /(?:window|globalThis)\.(CV_[A-Z0-9_]+)\s*=|(?:^|[\n;])\s*(?:var|let|const)\s+(CV_[A-Z0-9_]+)\s*=/g;
const REF_RE = /\bCV_[A-Z0-9_]+\b/g;
const SRC_RE = /(?:src|href)\s*=\s*["']([^"']+)["']/g;
const IMP_RE = /(?:import\s[^'"]*from\s*|import\s*|require\s*\(\s*)["']([^"']+)["']/g;
const CSS_IMP_RE = /@import\s+(?:url\()?["']([^"']+)["']/g;

function normalizePath(base, rel) {
  if (!rel || /^(https?:|data:|#|mailto:)/.test(rel)) return null;
  rel = rel.split('?')[0].split('#')[0];
  const parts = base.includes('/') ? base.slice(0, base.lastIndexOf('/')).split('/') : [];
  rel.split('/').forEach(s => { if (s === '.' || s === '') return; if (s === '..') parts.pop(); else parts.push(s); });
  return parts.join('/');
}

async function buildSystemMap({ ls, readFile, readFileBinary, encoding = null, timeBudgetMs = 24000 } = {}) {
  const nodes = [];
  const addFile = (path, name, parentId) => {
    const dot = name.lastIndexOf('.');
    nodes.push({ id: path, name, path, parent: parentId, type: 'file',
      ext: dot > 0 ? name.slice(dot + 1).toLowerCase() : '', role: 'other', size: null, defines: [], uses: [] });
  };

  // 1. parallel BFS walk (one ls round-trip per directory LEVEL, not per node)
  let level = [{ dir: '', parentId: null, name: null, candidate: false }];
  while (level.length) {
    const res = await Promise.all(level.map(it => ls(it.dir).then(names => ({ it, names })).catch(() => ({ it, names: null }))));
    const next = [];
    for (const { it, names } of res) {
      if (names === null) { if (it.candidate) addFile(it.dir, it.name, it.parentId); continue; } // dotless file
      if (it.candidate) nodes.push({ id: it.dir, name: it.name, path: it.dir, parent: it.parentId, type: 'folder', ext: null, role: 'folder', size: null, defines: [], uses: [] });
      for (const name of names) {
        if (isDot(name) || SKIP.has(name)) continue;
        const path = it.dir ? it.dir + '/' + name : name;
        if (name.lastIndexOf('.') > 0) addFile(path, name, it.dir || null);
        else next.push({ dir: path, parentId: it.dir || null, name, candidate: true });
      }
    }
    level = next;
  }

  // 2. classify
  nodes.forEach(n => { if (n.type === 'file') n.role = classifyRole(n.path, n.ext); });

  // 3. read code files: size + defines/uses, retain raw for the loads pass
  const RAW = {};
  const enc = (typeof TextEncoder !== 'undefined') ? new TextEncoder() : null;
  const codeFiles = nodes.filter(n => n.type === 'file' && CODE.has(n.ext));
  const t0 = Date.now();
  for (let i = 0; i < codeFiles.length; i += 60) {
    if (Date.now() - t0 > timeBudgetMs) break;
    await Promise.all(codeFiles.slice(i, i + 60).map(async n => {
      try {
        const txt = await readFile(n.path); RAW[n.id] = txt;
        n.size = enc ? enc.encode(txt).length : txt.length;
        const defs = new Set(); let m; DEF_RE.lastIndex = 0;
        while ((m = DEF_RE.exec(txt))) defs.add(m[1] || m[2]);
        n.defines = [...defs];
        const uses = new Set(); (txt.match(REF_RE) || []).forEach(g => { if (!defs.has(g)) uses.add(g); });
        n.uses = [...uses];
      } catch (e) { RAW[n.id] = ''; }
    }));
  }

  // 3b. size for the rest of the tree so the "file size" lens covers EVERY file
  //     (docs/data via text length; binaries via byte length). Budget-bounded: a single
  //     30s pass can't byte-size hundreds of images, so leftover images keep size=null
  //     and are filled incrementally (re-run with a fresh budget) — still single-source.
  const TEXT_MORE = new Set(['md','json','svg','txt','csv']);
  const rest = nodes.filter(n => n.type === 'file' && n.size == null);
  for (let i = 0; i < rest.length; i += 60) {
    if (Date.now() - t0 > timeBudgetMs) break;
    await Promise.all(rest.slice(i, i + 60).map(async n => {
      try {
        if (TEXT_MORE.has(n.ext)) { const t = await readFile(n.path); n.size = enc ? enc.encode(t).length : t.length; }
        else if (readFileBinary) { const b = await readFileBinary(n.path); n.size = b.size; }
      } catch (e) { /* leave size null */ }
    }));
  }

  // 4. globals (global -> first defining node)
  const DEFINER = {}, globals = [];
  nodes.forEach(n => (n.defines || []).forEach(g => { if (!DEFINER[g]) { DEFINER[g] = n.id; globals.push({ global: g, node: n.id }); } }));

  // 5. edges: contains + uses:<GLOBAL> + loads
  const edges = [];
  nodes.forEach(n => { if (n.parent) edges.push({ from: n.parent, to: n.id, kind: 'contains', type: 'contains' }); });
  nodes.forEach(n => (n.uses || []).forEach(g => { if (DEFINER[g] && DEFINER[g] !== n.id) edges.push({ from: n.id, to: DEFINER[g], kind: 'uses:' + g, type: 'resolves' }); }));
  const ID = new Set(nodes.map(n => n.id));
  const resolve = p => { if (!p) return null; if (ID.has(p)) return p; for (const ex of ['.js','.jsx','.ts','.css','/index.html','/index.js']) if (ID.has(p + ex)) return p + ex; return null; };
  nodes.forEach(n => {
    const txt = RAW[n.id]; if (!txt) return; let m; const seen = new Set();
    const add = rel => { const t = resolve(normalizePath(n.path, rel)); if (t && t !== n.id && !seen.has(t)) { seen.add(t); edges.push({ from: n.id, to: t, kind: 'loads', type: 'loads' }); } };
    if (n.ext === 'html') { SRC_RE.lastIndex = 0; let mm; while ((mm = SRC_RE.exec(txt))) add(mm[1]); }
    if (['js','jsx','ts','mjs','html'].includes(n.ext)) { IMP_RE.lastIndex = 0; let mm; while ((mm = IMP_RE.exec(txt))) add(mm[1]); }
    if (n.ext === 'css') { CSS_IMP_RE.lastIndex = 0; let mm; while ((mm = CSS_IMP_RE.exec(txt))) add(mm[1]); }
  });

  // 6. counts + model
  const roleCounts = {}; nodes.forEach(n => roleCounts[n.role] = (roleCounts[n.role] || 0) + 1);
  return { nodes, edges, globals, roleCounts, encoding, scanned: codeFiles.map(n => n.id), generatedAt: Date.now(), version: 2 };
}

if (typeof module !== 'undefined') module.exports = { buildSystemMap, classifyRole };
if (typeof window !== 'undefined') window.buildSystemMap = buildSystemMap;
