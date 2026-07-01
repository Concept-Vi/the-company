// app/ai/host-serializer.js
// ============================================================================
// Serializers + host capabilities.
//
// Two jobs, both single-source:
//   1. SERIALIZERS — one per change kind. Each knows the ONE file a change of
//      that kind lives in, and renders the change payload as EXACT source text
//      ready to drop into that file. This is what lets Vi *author real diffs*
//      rather than describe vague suggestions: it produces the literal
//      `CV_AI.register({...})` / token line / @dsCard file a human would write.
//   2. HOST CAPABILITIES — repo.read / repo.list / repo.write / ds.propose /
//      ds.commit registered into CV_AI, so "what Vi can do" includes touching
//      the repository, routed through the same CV_AI.execute() path as every
//      other move. They run on the 'host-fs' provider, which CV_HOST binds.
//
// Loud, never silent: a missing serializer throws; a write with no connected
// runtime throws (or stages, explicitly). No format knowledge is duplicated —
// each serializer is the single home for "how an X is written to source."
// ============================================================================

(function () {
  'use strict';
  const HOST = window.CV_HOST;
  const AI = window.CV_AI;
  if (!HOST) throw new Error('[host-serializer] CV_HOST not loaded — load app/ai/host-runtime.js first');
  if (!AI) throw new Error('[host-serializer] CV_AI not loaded — load app/ai/ai-registry.js first');

  // ---------------------------------------------------------------------------
  // JS value → readable source. Handles functions (via toString, so Vi can
  // author a capability with a real run()/build()), nested objects, arrays.
  // ---------------------------------------------------------------------------
  function js(val, indent) {
    indent = indent || '  ';
    if (val === null) return 'null';
    if (typeof val === 'function') return reindent(val.toString(), indent);
    if (typeof val === 'string') {
      // a function smuggled through JSON as "ƒ…" (CV_HOST.safeClone) → revive
      if (val[0] === 'ƒ') return reindent(val.slice(1), indent);
      return JSON.stringify(val);
    }
    if (typeof val === 'number' || typeof val === 'boolean') return String(val);
    if (Array.isArray(val)) {
      if (!val.length) return '[]';
      const simple = val.every(v => typeof v === 'string' || typeof v === 'number' || typeof v === 'boolean');
      if (simple) return '[' + val.map(v => js(v, indent)).join(', ') + ']';
      return '[\n' + val.map(v => indent + '  ' + js(v, indent + '  ')).join(',\n') + '\n' + indent + ']';
    }
    if (typeof val === 'object') {
      const keys = Object.keys(val).filter(k => val[k] !== undefined);
      if (!keys.length) return '{}';
      return '{\n' + keys.map(k => indent + '  ' + keyName(k) + ': ' + js(val[k], indent + '  ')).join(',\n') + '\n' + indent + '}';
    }
    return JSON.stringify(val);
  }
  function keyName(k) { return /^[A-Za-z_$][\w$]*$/.test(k) ? k : JSON.stringify(k); }
  function reindent(src, indent) {
    const lines = src.replace(/\r/g, '').split('\n');
    if (lines.length === 1) return src;
    // re-base the function body indentation under the current indent
    const body = lines.slice(1);
    const min = Math.min(...body.filter(l => l.trim()).map(l => l.match(/^\s*/)[0].length));
    return lines[0] + '\n' + body.map(l => l.trim() ? indent + l.slice(min) : '').join('\n');
  }

  // ---------------------------------------------------------------------------
  // SERIALIZERS — each is the single home for one change kind's source format.
  // The `anchor` is a sentinel comment new entries insert before, so additions
  // accrete in a predictable spot. (host-runtime appends at EOF if absent.)
  // ---------------------------------------------------------------------------

  // A CV_AI registry entry (capability / behaviour / skill / provider / context).
  // Lives in ai-seed.js — the data home for built-ins.
  HOST.registerSerializer({
    kind: 'ai.entry',
    target: 'app/ai/ai-seed.js',
    strategy: 'append-block',
    anchor: '// CV_HOST:ai-entries',
    describe: 'A CV_AI registry entry (provider/behaviour/skill/capability/context). Registered into the one AI catalogue; appears in every surface that projects it.',
    render: (p) => 'AI.register(' + js(p) + ', { silent: true });',
  });

  // A type/component/atom/archetype registered into CV_REGISTRY.
  HOST.registerSerializer({
    kind: 'type',
    target: 'app/registry/types-seed.js',
    strategy: 'append-block',
    anchor: '// CV_HOST:types',
    describe: 'A Type (token/atom/block/system/surface/doc/template) registered into CV_REGISTRY. Renders through the one engine under the axis-dials.',
    render: (p) => 'CV_REGISTRY.register(' + js(p) + ');',
  });

  // A design token — a new L0 primitive or L1 role. Lives in colors_and_type.css.
  HOST.registerSerializer({
    kind: 'css.token',
    target: (p) => p.file || 'colors_and_type.css',
    strategy: 'css-token',
    anchor: ':root',
    describe: 'A design token (CSS custom property). Added at its lowest layer; every consumer that var()s it updates by construction.',
    render: (p) => `--${slug(p.name)}: ${p.value};` + (p.role ? `   /* ${p.role} */` : ''),
  });

  // A Design System tab card — a tagged .html specimen. New file.
  HOST.registerSerializer({
    kind: 'card',
    target: (p) => `preview/${slug(p.name)}.html`,
    strategy: 'new-file',
    describe: 'A Design System tab card — a tagged HTML specimen. Appears in the tab under its group, grouped automatically.',
    render: (p) => [
      `<!-- @dsCard group="${p.group || 'Brand'}" name="${p.name}" subtitle="${p.subtitle || ''}" viewport="${p.viewport || '700x280'}" -->`,
      '<!DOCTYPE html>', '<html><head><meta charset="utf-8">',
      '<link rel="stylesheet" href="_card.css">', '</head><body>',
      p.body || '<div class="card-pad"><!-- specimen --></div>',
      '</body></html>', '',
    ].join('\n'),
  });

  // A raw file write — escape hatch for anything not yet typed. New file.
  HOST.registerSerializer({
    kind: 'file',
    target: (p) => p.path,
    strategy: 'new-file',
    describe: 'A whole-file write (escape hatch). Prefer a typed kind so the change lives in its proper home.',
    render: (p) => p.contents,
  });

  function slug(s) { return String(s || '').toLowerCase().replace(/[^a-z0-9-]+/g, '-').replace(/^-|-$/g, ''); }

  // ---------------------------------------------------------------------------
  // PROVIDER — the host filesystem provider CV_AI capabilities run on. Bound by
  // CV_HOST.resolveProviderRuntime (loud if no writer when a write is attempted).
  // ---------------------------------------------------------------------------
  AI.register({
    id: 'host-fs', name: 'Host filesystem', layer: 'provider', family: 'host',
    description: 'The environment’s file surface — sandbox review by default, real disk when a browser/native runtime is connected. Resolved by CV_HOST.',
    runtime: { kind: 'host-fs' }, modality: ['fs'], caps: { read: true, write: true },
    icon: 'files-stack', provenance: 'built-in', tags: ['host', 'fs'],
  }, { silent: true });

  // Additional MODEL providers — declared so the catalogue knows other models
  // CAN be used; they resolve to live runtimes only when the exported app
  // connects a native/MCP host. In the sandbox, resolving them throws loudly
  // (pointing the user at the built-in claude provider).
  AI.register({
    id: 'native-model', name: 'Local / other model', layer: 'provider', family: 'text',
    description: 'A model endpoint exposed by your local shell or MCP host (Ollama, an OpenAI-compatible server, another Anthropic key). Activates when the exported app detects window.CV_HOST_NATIVE.complete().',
    runtime: { kind: 'native-model' }, modality: ['text'], caps: { stream: false, json: true },
    icon: 'sparkles', provenance: 'built-in', tags: ['text', 'export-only'],
  }, { silent: true });
  AI.register({
    id: 'mcp-tools', name: 'MCP tools', layer: 'provider', family: 'host',
    description: 'Tool calls routed through a connected MCP host (filesystem, git, search, your own servers). Activates on export with an MCP bridge.',
    runtime: { kind: 'mcp-model' }, modality: ['tool'], caps: {},
    icon: 'network', provenance: 'built-in', tags: ['tools', 'export-only'],
  }, { silent: true });

  // ---------------------------------------------------------------------------
  // CAPABILITIES — "what Vi can do" now includes touching the repo. Routed
  // through CV_AI.execute() like every other move, so they appear in the
  // catalogue, the inspector, and any surface that projects capabilities.
  // ---------------------------------------------------------------------------
  AI.register({
    id: 'repo.read', name: 'Read a file', layer: 'capability', family: 'repo',
    description: 'Read a file from the connected directory (loud if no reader).',
    surfaces: ['*'], provider: 'host-fs', params: { path: '' }, icon: 'document', provenance: 'built-in',
    run: (a) => a.provider.read(a.params.path),
  }, { silent: true });
  AI.register({
    id: 'repo.list', name: 'List a directory', layer: 'capability', family: 'repo',
    description: 'List entries of a directory (loud if no reader).',
    surfaces: ['*'], provider: 'host-fs', params: { path: '' }, icon: 'files-stack', provenance: 'built-in',
    run: (a) => a.provider.list(a.params.path),
  }, { silent: true });

  // The keystone: propose a single-sourced change. Vi calls this with a change
  // descriptor; it serializes to real source and stages it (review-first), or
  // writes it when a writer is connected + auto-apply is on. ALWAYS explicit.
  AI.register({
    id: 'ds.propose', name: 'Propose a change', layer: 'capability', family: 'repo',
    description: 'Serialize a registry mutation (a new token, capability, type, or card) into exact source for its one home file, and commit it through CV_HOST — staged for review in the sandbox, written to disk when connected.',
    surfaces: ['*'], provider: 'host-fs',
    params: { kind: '', title: '', rationale: '', payload: null }, icon: 'wand', provenance: 'built-in',
    run: (a) => a.provider.commit({
      kind: a.params.kind, title: a.params.title, rationale: a.params.rationale,
      payload: a.params.payload, provenance: 'vi',
    }),
  }, { silent: true });

  // Apply an already-staged change (the panel's Apply button uses this path too).
  AI.register({
    id: 'ds.apply', name: 'Apply a staged change', layer: 'capability', family: 'repo',
    description: 'Write a previously staged change to disk via the connected writer. Loud if no writer is connected.',
    surfaces: ['*'], provider: 'host-fs', params: { id: '' }, icon: 'check-square', provenance: 'built-in',
    run: (a) => window.CV_HOST.changes.apply(a.params.id),
  }, { silent: true });

  console.info('[host-serializer] serializers + host capabilities registered');
})();
