// atomicity/atlas-model.js
// ============================================================================
// THE ATLAS MODEL — the single projection of the entire system into a tree.
//
// AtomiCity has no hand-written navigation. This file DERIVES the whole
// hierarchical map from the four single sources of truth:
//   • _ds_manifest.json   — components, cards, templates, tokens, themes, fonts
//   • window.CV_REGISTRY   — Types (token→atom→block→system→surface→doc→template)
//   • window.CV_AI         — providers · behaviours · skills · capabilities · context
//   • window.CV_HOST        — runtimes · serializers · staged changes
//
// Because the tree is a projection, it cannot drift from the system: add a
// token, a capability, a card, a Type — it appears here on next build(), no
// edit to AtomiCity. This is the "knows everything in the system without being
// told" backbone — both the browser AND Vi read this one model.
//
// A node: { id, label, kind, icon, count?, badge?, children?, leaf, data }
//   kind drives how the detail pane renders it (token/component/card/template/
//   capability/type/runtime/group/section). data carries the raw record.
// ============================================================================

(function () {
  'use strict';

  let MANIFEST = null;
  let TREE = null;
  const INDEX = new Map();           // id -> node
  const listeners = new Set();

  function on(fn) { listeners.add(fn); return () => listeners.delete(fn); }
  function emit() { for (const fn of listeners) { try { fn(TREE); } catch (e) { console.error('[ATLAS]', e); } } }

  // --- manifest ------------------------------------------------------------
  async function loadManifest() {
    const res = await fetch('../_ds_manifest.json', { cache: 'no-store' });
    if (!res.ok) throw new Error('[ATLAS] could not load _ds_manifest.json (' + res.status + '). AtomiCity must run inside the design-system project.');
    MANIFEST = await res.json();
    return MANIFEST;
  }

  // --- token grouping ------------------------------------------------------
  const TOKEN_KIND_META = {
    color:   { label: 'Color',   icon: 'color-swatches' },
    spacing: { label: 'Spacing', icon: 'ruler' },
    shadow:  { label: 'Depth / shadow', icon: 'layers' },
    radius:  { label: 'Radius',  icon: 'square' },
    font:    { label: 'Type',    icon: 'type' },
    other:   { label: 'Other',   icon: 'sliders' },
  };

  function tokenNodes() {
    const byKind = {};
    for (const t of (MANIFEST.tokens || [])) (byKind[t.kind] = byKind[t.kind] || []).push(t);
    const order = ['color', 'spacing', 'shadow', 'radius', 'font', 'other'];
    return order.filter(k => byKind[k]).map(k => {
      const meta = TOKEN_KIND_META[k] || { label: k, icon: 'sliders' };
      // sub-group by file so the 477 tokens read as their real homes
      const byFile = {};
      for (const t of byKind[k]) (byFile[t.definedIn] = byFile[t.definedIn] || []).push(t);
      const fileKeys = Object.keys(byFile).sort();
      const children = fileKeys.length > 1
        ? fileKeys.map(f => node({
            id: 'tok/' + k + '/' + f, label: f.split('/').pop().replace('.css', ''),
            kind: 'token-file', icon: 'document', count: byFile[f].length,
            data: { file: f, kind: k },
            children: byFile[f].map(tokenLeaf),
          }))
        : byKind[k].map(tokenLeaf);
      return node({ id: 'tok/' + k, label: meta.label, kind: 'token-group', icon: meta.icon, count: byKind[k].length, children });
    });
  }
  function tokenLeaf(t) {
    return node({ id: 'token/' + t.name, label: t.name, kind: 'token', icon: 'droplet', leaf: true, data: t });
  }

  // --- catalogue (cards) ---------------------------------------------------
  function cardNodes() {
    const groups = {};
    for (const c of (MANIFEST.cards || [])) (groups[c.group || 'Other'] = groups[c.group || 'Other'] || []).push(c);
    // a deliberate reading order; unknown groups append alphabetically
    const PREF = ['AI', 'Brand', 'Colors', 'Type', 'Spacing', 'Components', 'UI Kit — Platform', 'UI Kit — Vi', 'UI Kit — Virtual Hub'];
    const keys = Object.keys(groups).sort((a, b) => {
      const ia = PREF.indexOf(a), ib = PREF.indexOf(b);
      if (ia !== -1 || ib !== -1) return (ia === -1 ? 99 : ia) - (ib === -1 ? 99 : ib);
      return a.localeCompare(b);
    });
    // two-level "UI Kit — X" convention nests under a synthetic parent
    const kitKeys = keys.filter(k => /^UI Kit\b/.test(k));
    const flat = keys.filter(k => !/^UI Kit\b/.test(k));
    const out = flat.map(g => groupNode(g, groups[g]));
    if (kitKeys.length) {
      out.push(node({
        id: 'cards/uikit', label: 'UI Kits', kind: 'section', icon: 'grid',
        count: kitKeys.reduce((n, k) => n + groups[k].length, 0),
        children: kitKeys.map(k => groupNode(k, groups[k], k.replace(/^UI Kit —?\s*/, ''))),
      }));
    }
    return out;
  }
  function groupNode(group, cards, labelOverride) {
    return node({
      id: 'cards/' + group, label: labelOverride || group, kind: 'group', icon: 'folder',
      count: cards.length, data: { group },
      children: cards.map(c => node({
        id: 'card/' + c.path, label: c.name, kind: 'card', icon: 'browser', leaf: true,
        badge: c.viewport, data: c,
      })),
    });
  }

  // --- components (compiled bundle) ----------------------------------------
  function componentNodes() {
    return (MANIFEST.components || []).map(c => node({
      id: 'component/' + c.name, label: c.name, kind: 'component', icon: 'component', leaf: true, data: c,
    }));
  }

  // --- templates -----------------------------------------------------------
  function templateNodes() {
    return (MANIFEST.templates || []).map(t => node({
      id: 'template/' + (t.folder || t.name), label: t.name, kind: 'template', icon: 'file-plus', leaf: true, data: t,
    }));
  }

  // --- registries (the system reading itself) ------------------------------
  function registryNodes() {
    const out = [];

    // CV_REGISTRY — Types by layer
    if (window.CV_REGISTRY) {
      const types = window.CV_REGISTRY.all();
      const byLayer = {};
      for (const t of types) (byLayer[t.layer || 'type'] = byLayer[t.layer || 'type'] || []).push(t);
      out.push(node({
        id: 'reg/types', label: 'Types', kind: 'section', icon: 'box', count: types.length,
        data: { registry: 'CV_REGISTRY', doc: 'The type system — token→atom→block→system→surface→doc→template. Single-inheritance, slots, variables. Rendered by the one engine.' },
        children: Object.keys(byLayer).sort().map(l => node({
          id: 'reg/types/' + l, label: l, kind: 'group', icon: 'box', count: byLayer[l].length,
          children: byLayer[l].map(t => node({ id: 'type/' + t.id, label: t.name || t.id, kind: 'type', icon: 'box', leaf: true, data: t })),
        })),
      }));
    }

    // CV_AI — the AI catalogue by layer
    if (window.CV_AI) {
      const LAYERS = ['provider', 'behaviour', 'skill', 'capability', 'context'];
      const layerIcon = { provider: 'server', behaviour: 'feather', skill: 'wand', capability: 'sparkles', context: 'crosshair' };
      out.push(node({
        id: 'reg/ai', label: 'AI (CV_AI)', kind: 'section', icon: 'sparkles',
        count: window.CV_AI.query({}).length,
        data: { registry: 'CV_AI', doc: 'Everything Vi can do — one catalogue of providers, behaviours, skills, capabilities, and context resolvers. The interface is a projection of it.' },
        children: LAYERS.map(layer => {
          const items = window.CV_AI.query({ layer });
          // capabilities sub-group by family (there are many)
          let kids;
          if (layer === 'capability') {
            const byFam = {};
            for (const c of items) (byFam[c.family || 'misc'] = byFam[c.family || 'misc'] || []).push(c);
            kids = Object.keys(byFam).sort().map(f => node({
              id: 'reg/ai/cap/' + f, label: f, kind: 'group', icon: 'sparkles', count: byFam[f].length,
              children: byFam[f].map(aiLeaf),
            }));
          } else {
            kids = items.map(aiLeaf);
          }
          return node({ id: 'reg/ai/' + layer, label: layer + 's', kind: 'group', icon: layerIcon[layer] || 'sparkles', count: items.length, children: kids });
        }),
      }));
    }

    // CV_HOST — the Bridge
    if (window.CV_HOST) {
      const d = window.CV_HOST.describe();
      out.push(node({
        id: 'reg/host', label: 'Bridge (CV_HOST)', kind: 'section', icon: 'cloud-upload',
        badge: d.modeLabel,
        data: { registry: 'CV_HOST', describe: d, doc: 'Where Vi reaches the repo. Pluggable runtimes resolved by capability; a serializer turns a registry mutation into exact source; every change is staged for review before it touches disk.' },
        children: [
          node({ id: 'reg/host/runtimes', label: 'Runtimes', kind: 'group', icon: 'server', count: d.runtimes.length,
            children: d.runtimes.map(r => node({ id: 'runtime/' + r.id, label: r.label, kind: 'runtime', icon: r.available ? 'check-circle' : 'circle', leaf: true, badge: r.available ? 'active' : null, data: r })) }),
          node({ id: 'reg/host/serializers', label: 'Serializers', kind: 'group', icon: 'wand', count: d.serializers.length,
            children: d.serializers.map(s => node({ id: 'serializer/' + s.kind, label: s.kind, kind: 'serializer', icon: 'document', leaf: true, badge: s.strategy, data: s })) }),
          node({ id: 'reg/host/changes', label: 'Proposed changes', kind: 'group', icon: 'edit', count: d.changes.total, badge: d.changes.staged ? d.changes.staged + ' staged' : null,
            children: window.CV_HOST.changes.list().map(c => node({ id: 'change/' + c.id, label: c.title, kind: 'change', icon: 'edit', leaf: true, badge: c.status, data: c })) }),
        ],
      }));
    }

    // CV_SCAN — the autonomous scanner
    if (window.CV_SCAN) {
      const d = window.CV_SCAN.describe();
      const st = window.CV_SCAN.stats();
      out.push(node({
        id: 'reg/scan', label: 'Scanner (CV_SCAN)', kind: 'section', icon: 'search',
        badge: st.tokensTracked ? st.tokensTracked + ' tracked' : 'idle',
        data: { registry: 'CV_SCAN', describe: d, doc: 'The autonomous scanner. Registered sources × extractors, run continuously, build live indexes of where every token is used, where the tags live, and the open work — staying fresh without intervention.' },
        children: [
          node({ id: 'reg/scan/sources', label: 'Sources', kind: 'group', icon: 'files-stack', count: d.sources.length,
            children: d.sources.map(s => node({ id: 'scansrc/' + s.id, label: s.id, kind: 'scan-source', icon: 'document', leaf: true, badge: s.enabled ? null : 'off', data: s })) }),
          node({ id: 'reg/scan/extractors', label: 'Extractors', kind: 'group', icon: 'filter', count: d.extractors.length,
            children: d.extractors.map(e => node({ id: 'scanext/' + e.id, label: e.id, kind: 'scan-extractor', icon: 'filter', leaf: true, badge: e.keys + '', data: e })) }),
        ],
      }));
    }

    return out;
  }
  function aiLeaf(e) {
    return node({ id: 'ai/' + e.id, label: e.name || e.id, kind: 'ai-entry', icon: e.icon || 'sparkles', leaf: true, badge: e.provenance, data: e });
  }

  // --- assemble ------------------------------------------------------------
  function build() {
    if (!MANIFEST) throw new Error('[ATLAS] build() before loadManifest()');
    const sections = [
      node({ id: 'sec/home', label: 'Home', kind: 'section', icon: 'house', leaf: true,
        data: { doc: 'Where to start — what AtomiCity is and the few things you can do.' } }),
      node({ id: 'sec/foundations', label: 'Your brand', kind: 'section', icon: 'color-swatches',
        data: { doc: 'The colours, type, roundness and depth of everything. See it and tune it — changes flow through the whole product live.' },
        children: [
          ...tokenNodes(),
          themesNode(),
          fontsNode(),
        ] }),
      node({ id: 'sec/explore', label: 'Explore', kind: 'section', icon: 'shuffle', leaf: true,
        data: { doc: 'Restyle an element into many directions at once, steer by taste, then make the keeper a real component.' } }),
      node({ id: 'sec/voice', label: 'Voice', kind: 'section', icon: 'chat', leaf: true,
        data: { doc: 'Write copy for real product moments in the house voice — pick the one that sounds right and keep it as an example.' } }),
      node({ id: 'sec/ingest', label: 'Inspiration', kind: 'section', icon: 'cloud-upload', leaf: true,
        data: { doc: 'Upload source material — brand docs, copy, images, notes. Vi recognises what it is, reads it deeply, and brings the ideas forward.' } }),
      node({ id: 'sec/underhood', label: 'Under the hood', kind: 'section', icon: 'network',
        data: { doc: 'The machinery — for the technically curious. Components, examples, templates and the registries the whole system is built from.' },
        children: [
          node({ id: 'sec/components', label: 'Components', kind: 'group', icon: 'component', count: (MANIFEST.components || []).length,
            data: { doc: 'The compiled React components on window.' + MANIFEST.namespace + '. Live, the same code consumers receive.' },
            children: componentNodes() }),
          node({ id: 'sec/catalogue', label: 'Examples', kind: 'group', icon: 'grid', count: (MANIFEST.cards || []).length,
            data: { doc: 'Specimen cards — each a tagged HTML file, grouped automatically.' },
            children: cardNodes() }),
          node({ id: 'sec/templates', label: 'Templates', kind: 'group', icon: 'file-plus', count: (MANIFEST.templates || []).length,
            data: { doc: 'Starting artifacts a consuming project copies — each composes components + tokens.' },
            children: templateNodes() }),
          node({ id: 'sec/system', label: 'Registries', kind: 'group', icon: 'network',
            data: { doc: 'The registries reading themselves — the engine. Change a thing here and every projection, including this map, updates.' },
            children: registryNodes() }),
        ] }),
    ];
    TREE = node({ id: 'root', label: 'AtomiCity', kind: 'root', icon: 'atom', children: sections });
    reindex();
    emit();
    return TREE;
  }
  function themesNode() {
    return node({ id: 'foundations/themes', label: 'Axes & themes', kind: 'group', icon: 'sliders', count: (MANIFEST.themes || []).length,
      data: { doc: 'The dials — surface, density, theme, palette — applied as data-* + CSS vars and threaded through the engine.' },
      children: (MANIFEST.themes || []).map(t => node({ id: 'theme/' + t.selector, label: t.label, kind: 'theme', icon: 'sliders', leaf: true, data: t })) });
  }
  function fontsNode() {
    return node({ id: 'foundations/fonts', label: 'Fonts', kind: 'group', icon: 'type', count: (MANIFEST.brandFonts || []).length,
      children: (MANIFEST.brandFonts || []).map(f => node({ id: 'font/' + f.family, label: f.family, kind: 'font', icon: 'type', leaf: true, badge: (f.tokens || [])[0], data: f })) });
  }

  // --- node + index --------------------------------------------------------
  function node(n) { return { count: undefined, badge: null, leaf: false, children: null, data: null, ...n }; }
  function reindex() {
    INDEX.clear();
    (function walk(n) { INDEX.set(n.id, n); (n.children || []).forEach(walk); })(TREE);
  }
  function find(id) { return INDEX.get(id) || null; }
  function pathTo(id) {
    const out = [];
    (function walk(n, trail) {
      if (n.id === id) { out.push(...trail, n); return true; }
      for (const c of (n.children || [])) if (walk(c, [...trail, n])) return true;
      return false;
    })(TREE, []);
    return out;
  }
  function search(q) {
    q = (q || '').trim().toLowerCase();
    if (!q) return [];
    const hits = [];
    for (const n of INDEX.values()) {
      if (n.id === 'root') continue;
      const hay = (n.label + ' ' + n.kind + ' ' + (n.data && (n.data.subtitle || n.data.description || n.data.value || '') || '')).toLowerCase();
      if (hay.includes(q)) hits.push(n);
    }
    // leaves first, then by label length (closer match)
    return hits.sort((a, b) => (b.leaf - a.leaf) || (a.label.length - b.label.length)).slice(0, 40);
  }

  // a compact, machine-readable census — used by Vi to "know everything"
  function census() {
    const m = MANIFEST || {};
    const tokKinds = {};
    for (const t of (m.tokens || [])) tokKinds[t.kind] = (tokKinds[t.kind] || 0) + 1;
    return {
      namespace: m.namespace,
      tokens: (m.tokens || []).length, tokenKinds: tokKinds,
      components: (m.components || []).map(c => c.name),
      cardGroups: groupCounts(m.cards, 'group'),
      cards: (m.cards || []).length,
      templates: (m.templates || []).map(t => t.name),
      themes: (m.themes || []).map(t => t.label),
      fonts: (m.brandFonts || []).map(f => f.family),
      ai: window.CV_AI ? {
        providers: window.CV_AI.query({ layer: 'provider' }).map(x => x.id),
        behaviours: window.CV_AI.query({ layer: 'behaviour' }).map(x => x.id),
        skills: window.CV_AI.query({ layer: 'skill' }).map(x => x.id),
        capabilities: window.CV_AI.query({ layer: 'capability' }).map(x => x.id),
        contexts: window.CV_AI.query({ layer: 'context' }).map(x => x.id),
      } : null,
      types: window.CV_REGISTRY ? window.CV_REGISTRY.all().length : 0,
      host: window.CV_HOST ? window.CV_HOST.describe().modeLabel : null,
    };
  }
  function groupCounts(arr, key) {
    const o = {}; for (const x of (arr || [])) o[x[key] || 'Other'] = (o[x[key] || 'Other'] || 0) + 1; return o;
  }

  window.ATLAS = {
    async init() { await loadManifest(); return build(); },
    rebuild: build, get tree() { return TREE; }, get manifest() { return MANIFEST; },
    find, pathTo, search, census, on,
    // live registries re-trigger a rebuild so the Atlas never drifts. NOTE: we
    // deliberately do NOT subscribe to CV_AI here — its notify() also fires on
    // setActiveSurface (every navigation), which would loop rebuild↔navigate.
    // New AI entries (learning/proposals) arrive via a CV_HOST change, which
    // rebuilds and re-reads CV_AI fresh.
    _wire() {
      window.CV_REGISTRY && window.CV_REGISTRY.subscribe && window.CV_REGISTRY.subscribe(() => MANIFEST && build());
      window.CV_HOST && window.CV_HOST.subscribe(() => MANIFEST && build());
    },
  };
})();
