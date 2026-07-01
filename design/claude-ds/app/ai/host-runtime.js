// app/ai/host-runtime.js
// ============================================================================
// CV_HOST — the Environment / Host registry.
//
// The system already has four single-source registries (tokens, types, the
// engine, AI). CV_HOST is the layer that answers a different question: "what
// can Vi actually DO to the world it is running in — read files, write files,
// run the compiler, call a tool — and which of those are available HERE?"
//
// It is built in the SAME shape as CV_AI: a registry of pluggable, resolvable
// entries (here: runtimes), a uniform op surface routed to the best available
// runtime, and loud failure when something a caller needs is absent. The
// running UI is a projection of this registry (the Bridge panel + the AI card
// read CV_HOST.describe()), never a parallel hand-written status pile.
//
// THE ONE IDEA, applied to the environment:
//   capability-available = f(environment, runtime)
// A file write is not bespoke code per surface. It is: resolve the best writer
// runtime for the current environment, route the op to it. Add a new way to
// reach the disk (a Tauri shell, an MCP file tool, a cloud workspace) = register
// a runtime, not edit every caller.
//
// === Runtimes (low → high capability) ======================================
//   review   The sandbox FLOOR. No disk. Stages every change into a reviewable
//            queue (persisted to localStorage) for a human / the agent to
//            commit. ALWAYS available — so the system is never dead, only
//            degraded, and degraded EXPLICITLY (the panel says "sandbox").
//   fsapi    Browser File System Access API. Real read/write to a directory the
//            user grants with a gesture. Works when this app is opened as a
//            top-level page (i.e. exported + run locally), not inside the
//            sandboxed editor iframe.
//   native   A local shell (Node/Electron/Tauri) or MCP host that injects
//            window.CV_HOST_NATIVE — full read/write/list + exec (run the
//            compiler) + tool calls. The richest mode; lights up on export.
//
// Loud, never silent: ops that need a writer throw with a message naming what
// is missing and how to activate it. The ONLY graceful path is the explicit,
// visible fall-through to `review` staging — which is a labelled mode, not a
// swallowed error.
// ============================================================================

(function () {
  'use strict';

  // ---- persistence keys (browser-local; the disk is the real source) -------
  const LS_CHANGES = 'cv:host:changes';
  const LS_HANDOFF = 'cv:host:handoff-mode';   // 'review' | 'stash' | 'download'
  const LS_AUTOAPPLY = 'cv:host:auto-apply';   // '1' when connected-writer auto-commit is on
  const LS_STASH = 'cv:host:agent-stash';      // serialized changes the exported-agent loop reads

  const listeners = new Set();
  function subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); }
  function notify() { for (const fn of listeners) { try { fn(); } catch (e) { console.error('[CV_HOST] listener', e); } } }

  // ==========================================================================
  // RUNTIMES — the pluggable ways to reach the world. Each declares what it can
  // do (caps), whether it is available right now, and how to activate it.
  // ==========================================================================
  const RUNTIMES = new Map();
  // KIND REGISTRY (A1 seam) — provider runtime-KINDS resolve via a registry instead of a
  // hardcoded if-ladder. registerKind(kind, fn) adds a resolver; resolveProviderRuntime checks
  // this FIRST, then falls through to the built-in kinds below (ADDITIVE — nothing removed yet;
  // the built-ins migrate INTO registered kinds in a later step, once this is proven).
  const KINDS = new Map();
  function registerKind(kind, fn) {
    if (!kind || typeof fn !== 'function') throw new Error('[CV_HOST] registerKind requires (kind, resolverFn)');
    KINDS.set(kind, fn); notify(); return kind;
  }
  function registerRuntime(r) {
    if (!r || !r.id) throw new Error('[CV_HOST] runtime missing id');
    RUNTIMES.set(r.id, r);
    notify();
    return r;
  }

  // The review floor — always present, no disk, stages for review.
  registerRuntime({
    id: 'review', label: 'Sandbox review', rank: 0,
    description: 'No disk access. Every change is serialized to real source and staged for a human or the agent to commit. The safe floor — always available.',
    caps: { read: false, write: false, list: false, exec: false, tools: false },
    available: () => true,
    activate: null, // nothing to activate; it is the floor
  });

  // Browser File System Access API — real disk, granted per-directory.
  let FSAPI_DIR = null; // FileSystemDirectoryHandle once the user connects
  const fsapiSupported = typeof window !== 'undefined' && typeof window.showDirectoryPicker === 'function';
  registerRuntime({
    id: 'fsapi', label: 'Browser file access', rank: 1,
    description: 'Reads & writes a directory you grant with the browser File System Access API. Available when this app runs as a top-level page (exported & opened locally), not inside the editor sandbox.',
    caps: { read: true, write: true, list: true, exec: false, tools: false },
    available: () => fsapiSupported && !!FSAPI_DIR,
    supported: () => fsapiSupported,
    async activate() {
      if (!fsapiSupported) throw new Error('[CV_HOST] File System Access API not supported in this browser. Open the exported app in a Chromium-based browser, or use a native shell.');
      FSAPI_DIR = await window.showDirectoryPicker({ mode: 'readwrite', id: 'conceptv-ds' });
      const perm = await FSAPI_DIR.requestPermission({ mode: 'readwrite' });
      if (perm !== 'granted') { FSAPI_DIR = null; throw new Error('[CV_HOST] read/write permission was not granted for the chosen directory.'); }
      await idbPut('fsapi-dir', FSAPI_DIR);
      notify();
      return FSAPI_DIR.name;
    },
    async disconnect() { FSAPI_DIR = null; await idbDel('fsapi-dir'); notify(); },
    // fs ops --------------------------------------------------------------
    async read(path) { return fsapiRead(FSAPI_DIR, path); },
    async list(dir) { return fsapiList(FSAPI_DIR, dir); },
    async write(path, contents) { return fsapiWrite(FSAPI_DIR, path, contents); },
  });

  // Native shell / MCP host — injected by the export environment.
  registerRuntime({
    id: 'native', label: 'Native / MCP host', rank: 2,
    description: 'A local shell (Node/Electron/Tauri) or MCP host that injects window.CV_HOST_NATIVE — full read/write/list, exec (run the compiler), and tool calls. The richest mode; activates automatically when the exported app detects the bridge.',
    caps: { read: true, write: true, list: true, exec: true, tools: true },
    available: () => !!(typeof window !== 'undefined' && window.CV_HOST_NATIVE),
    activate: null, // auto-detected; the host injects itself
    async read(path) { return reqNative('read', { path }); },
    async list(dir) { return reqNative('list', { path: dir }); },
    async write(path, contents) { return reqNative('write', { path, contents }); },
    async exec(cmd, args) { return reqNative('exec', { cmd, args }); },
    async tool(name, input) { return reqNative('tool', { name, input }); },
  });

  function reqNative(op, payload) {
    const n = window.CV_HOST_NATIVE;
    if (!n || typeof n[op] !== 'function') {
      throw new Error('[CV_HOST] native host present but does not implement "' + op + '". Implement window.CV_HOST_NATIVE.' + op + '() in your local shell.');
    }
    return n[op](payload.path ?? payload.cmd ?? payload.name, payload.contents ?? payload.args ?? payload.input);
  }

  // ==========================================================================
  // RUNTIME RESOLUTION — pick the best runtime that can do what's asked.
  // ==========================================================================
  function ranked() { return [...RUNTIMES.values()].sort((a, b) => b.rank - a.rank); }
  function best(cap) { return ranked().find(r => r.available() && r.caps[cap]) || null; }
  function reader() { return best('read'); }
  function writer() { return best('write'); }
  function canWrite() { return !!writer(); }

  function writerOrThrow() {
    const w = writer();
    if (w) return w;
    const how = ranked().filter(r => r.caps.write).map(r => `• ${r.label}: ${r.description}`).join('\n');
    throw new Error('[CV_HOST] no writable runtime is connected — running in sandbox review mode. To write to disk, activate one:\n' + how + '\nUntil then, changes stay staged for the agent / a human to commit.');
  }

  // ---- uniform op surface (routes to the best runtime; loud if impossible) --
  async function read(path) { const r = reader(); if (!r) throw new Error('[CV_HOST] no runtime can read files here (sandbox). Connect a file runtime.'); return r.read(path); }
  async function list(dir) { const r = best('list'); if (!r) throw new Error('[CV_HOST] no runtime can list files here (sandbox). Connect a file runtime.'); return r.list(dir); }
  async function write(path, contents) { return writerOrThrow().write(path, contents); }
  function capabilities() {
    const caps = { read: false, write: false, list: false, exec: false, tools: false };
    for (const r of RUNTIMES.values()) if (r.available()) for (const k in caps) caps[k] = caps[k] || !!r.caps[k];
    return caps;
  }

  // ==========================================================================
  // CV_AI BRIDGE — let CV_AI.resolveProvider delegate host/model runtime kinds
  // here, so the AI catalogue can name providers we own (a native model
  // endpoint, an MCP tool) without CV_AI knowing how the host reaches them.
  // Loud: returns a bound runtime or throws naming how to activate it.
  // ==========================================================================
  function resolveProviderRuntime(p) {
    const kind = p && p.runtime && p.runtime.kind;
    // A1 seam: a registered kind resolver wins FIRST (additive — the built-in kinds below are unchanged).
    if (KINDS.has(kind)) return KINDS.get(kind)(p);
    // host filesystem provider — used by repo.* capabilities
    if (kind === 'host-fs') {
      return { ...p, read, list, write, capabilities, async commit(change) { return commit(change); } };
    }
    // a model endpoint the native/MCP host exposes (other providers / local models)
    if (kind === 'native-model' || kind === 'mcp-model') {
      const n = (typeof window !== 'undefined') && window.CV_HOST_NATIVE;
      if (!n || typeof n.complete !== 'function') {
        throw new Error('[CV_HOST] provider "' + p.id + '" (' + kind + ') needs a native/MCP host that implements window.CV_HOST_NATIVE.complete(). It activates when you export this app and run it with the local bridge. (In the sandbox, use the built-in "claude" provider.)');
      }
      return { ...p, async complete(prompt, opts) { return n.complete(p.runtime.model || p.id, prompt, opts); } };
    }
    return null; // not ours — let CV_AI throw its own unknown-kind error
  }

  // ==========================================================================
  // HANDOFF SETTINGS — how a committed change is handed off when there is no
  // connected writer (sandbox). Persisted. NEVER auto-downloads by default.
  // ==========================================================================
  const HANDOFF_MODES = {
    review:   { label: 'Review in panel', desc: 'Stage the change in the Bridge panel for you to review, copy, and apply. Nothing leaves the page.' },
    stash:    { label: 'Stash for agent',  desc: 'Also write the serialized change to localStorage so Claude (the agent) can read it back next turn and commit it to disk for you.' },
    download: { label: 'Download file',    desc: 'Also download the patch file. Off by default — opt in here.' },
  };
  function handoffMode() { try { return localStorage.getItem(LS_HANDOFF) || 'review'; } catch { return 'review'; } }
  function setHandoffMode(m) { if (!HANDOFF_MODES[m]) throw new Error('[CV_HOST] unknown handoff mode "' + m + '"'); try { localStorage.setItem(LS_HANDOFF, m); } catch {} notify(); }
  function autoApply() { try { return localStorage.getItem(LS_AUTOAPPLY) === '1'; } catch { return false; } }
  function setAutoApply(on) { try { localStorage.setItem(LS_AUTOAPPLY, on ? '1' : '0'); } catch {} notify(); }

  // ==========================================================================
  // SERIALIZERS — turn a registry mutation into EXACT source text for the one
  // file it belongs in. Registered by host-serializer.js (kept separate so the
  // file-format knowledge lives next to nothing else). Single source: one
  // serializer per change kind; the change kind names its home file + strategy.
  // ==========================================================================
  const SERIALIZERS = new Map();
  function registerSerializer(s) {
    if (!s || !s.kind) throw new Error('[CV_HOST] serializer missing kind');
    if (typeof s.render !== 'function') throw new Error('[CV_HOST] serializer "' + s.kind + '" missing render()');
    SERIALIZERS.set(s.kind, s);
    return s;
  }
  function serialize(change) {
    if (!change || !change.kind) throw new Error('[CV_HOST] change missing kind');
    const s = SERIALIZERS.get(change.kind);
    if (!s) throw new Error('[CV_HOST] no serializer for kind "' + change.kind + '" (registered: ' + [...SERIALIZERS.keys()].join(', ') + ')');
    const source = s.render(change.payload, change);
    return {
      kind: change.kind,
      file: typeof s.target === 'function' ? s.target(change.payload, change) : s.target,
      strategy: s.strategy || 'append-block',
      anchor: typeof s.anchor === 'function' ? s.anchor(change.payload, change) : (s.anchor || null),
      describe: s.describe || '',
      source,
    };
  }

  // ==========================================================================
  // CHANGES — the proposed-change store. Every commit lands here (reviewable),
  // persisted to localStorage. Statuses: staged → applied | rejected.
  // ==========================================================================
  function loadChanges() { try { return JSON.parse(localStorage.getItem(LS_CHANGES) || '[]'); } catch { return []; } }
  function saveChanges(arr) { try { localStorage.setItem(LS_CHANGES, JSON.stringify(arr)); } catch {} notify(); }
  let CHANGES = loadChanges();

  const changes = {
    list() { return CHANGES.slice(); },
    pending() { return CHANGES.filter(c => c.status === 'staged'); },
    get(id) { return CHANGES.find(c => c.id === id) || null; },
    propose(change) {
      const id = change.id || ('chg_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6));
      const serialized = change.serialized || serialize(change);
      const entry = {
        id, kind: change.kind, title: change.title || change.kind,
        rationale: change.rationale || '', provenance: change.provenance || 'vi',
        payload: safeClone(change.payload), serialized,
        status: 'staged', createdAt: Date.now(),
      };
      CHANGES = [entry, ...CHANGES];
      saveChanges(CHANGES);
      return entry;
    },
    async apply(id) {
      const c = changes.get(id);
      if (!c) throw new Error('[CV_HOST] no staged change "' + id + '"');
      await applySerialized(c.serialized);
      c.status = 'applied'; c.appliedAt = Date.now();
      CHANGES = CHANGES.map(x => x.id === id ? c : x);
      saveChanges(CHANGES);
      return c;
    },
    reject(id) { const c = changes.get(id); if (c) { c.status = 'rejected'; CHANGES = CHANGES.map(x => x.id === id ? c : x); saveChanges(CHANGES); } },
    remove(id) { CHANGES = CHANGES.filter(c => c.id !== id); saveChanges(CHANGES); },
    clear() { CHANGES = []; saveChanges(CHANGES); },
    subscribe,
  };

  function safeClone(v) { try { return JSON.parse(JSON.stringify(v, fnReplacer)); } catch { return v; } }
  function fnReplacer(_k, val) { return typeof val === 'function' ? ('ƒ' + val.toString()) : val; }

  // ==========================================================================
  // APPLY — write a serialized change to disk via the connected writer, using
  // its strategy. Loud if no writer. This is the real edit; commit() only
  // stages (review-first by design).
  // ==========================================================================
  async function applySerialized(s) {
    const w = writerOrThrow();
    if (s.strategy === 'new-file') {
      await w.write(s.file, s.source);
      return { file: s.file, wrote: 'new' };
    }
    if (s.strategy === 'css-token') {
      const cur = await read(s.file);
      const next = insertInSelector(cur, s.anchor || ':root', s.source);
      await w.write(s.file, next);
      return { file: s.file, wrote: 'css-token' };
    }
    // default: append-block — insert before an anchor sentinel, else at EOF
    const cur = await read(s.file);
    let next;
    if (s.anchor && cur.includes(s.anchor)) next = cur.replace(s.anchor, s.source + '\n\n  ' + s.anchor);
    else next = cur.replace(/\s*$/, '\n\n' + s.source + '\n');
    await w.write(s.file, next);
    return { file: s.file, wrote: 'append' };
  }

  function insertInSelector(css, selector, line) {
    const re = new RegExp('(' + selector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\s*\\{)');
    if (re.test(css)) return css.replace(re, '$1\n  ' + line);
    return css.replace(/\s*$/, '\n\n' + selector + ' {\n  ' + line + '\n}\n');
  }

  // ==========================================================================
  // commit — THE call Vi makes. Serialize the change, stage it (always — review
  // first), then per environment + settings: if a writer is connected AND
  // auto-apply is on, write it now; else hand off per the handoff-mode setting.
  // Returns a clear, explicit status. Never silently degrades.
  // ==========================================================================
  async function commit(change) {
    const entry = changes.propose(change);
    const mode = handoffMode();
    let result = { id: entry.id, status: 'staged', file: entry.serialized.file, mode };

    if (canWrite() && autoApply()) {
      await changes.apply(entry.id);
      result.status = 'applied';
      result.writer = writer().id;
      return result;
    }
    if (mode === 'stash') { stash(entry); result.stashed = true; }
    if (mode === 'download') { download(entry); result.downloaded = true; }
    return result;
  }

  // ---- handoff side-effects -------------------------------------------------
  function stash(entry) {
    let arr; try { arr = JSON.parse(localStorage.getItem(LS_STASH) || '[]'); } catch { arr = []; }
    arr.unshift({ id: entry.id, file: entry.serialized.file, strategy: entry.serialized.strategy, anchor: entry.serialized.anchor, source: entry.serialized.source, title: entry.title, at: Date.now() });
    try { localStorage.setItem(LS_STASH, JSON.stringify(arr)); } catch {}
  }
  function readStash() { try { return JSON.parse(localStorage.getItem(LS_STASH) || '[]'); } catch { return []; } }
  function clearStash() { try { localStorage.removeItem(LS_STASH); } catch {} }
  function download(entry) {
    const blob = new Blob([entry.serialized.source], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = entry.serialized.file.split('/').pop() + '.patch.txt';
    a.click(); URL.revokeObjectURL(url);
  }

  // ==========================================================================
  // describe — the SELF-DOCUMENTING projection. The Bridge panel and the AI
  // card render this; it is the single source of "what this environment is and
  // what Vi can do in it." No status string is hand-written elsewhere.
  // ==========================================================================
  function describe() {
    const caps = capabilities();
    const w = writer();
    return {
      mode: w ? w.id : 'review',
      modeLabel: w ? w.label : 'Sandbox review',
      capabilities: caps,
      canWrite: !!w,
      runtimes: ranked().map(r => ({
        id: r.id, label: r.label, rank: r.rank, description: r.description,
        caps: r.caps, available: r.available(),
        supported: r.supported ? r.supported() : true,
        canActivate: !!r.activate,
      })),
      serializers: [...SERIALIZERS.values()].map(s => ({ kind: s.kind, target: typeof s.target === 'function' ? '(computed)' : s.target, strategy: s.strategy || 'append-block', describe: s.describe || '' })),
      handoff: { mode: handoffMode(), modes: HANDOFF_MODES, autoApply: autoApply() },
      changes: { staged: changes.pending().length, total: CHANGES.length },
      stash: readStash().length,
    };
  }

  // ==========================================================================
  // tiny IndexedDB helper — persist the granted directory handle across reloads
  // ==========================================================================
  function idb() {
    return new Promise((res, rej) => {
      const r = indexedDB.open('cv-host', 1);
      r.onupgradeneeded = () => r.result.createObjectStore('kv');
      r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error);
    });
  }
  async function idbPut(k, v) { try { const db = await idb(); await new Promise((res, rej) => { const t = db.transaction('kv', 'readwrite'); t.objectStore('kv').put(v, k); t.oncomplete = res; t.onerror = () => rej(t.error); }); } catch {} }
  async function idbGet(k) { try { const db = await idb(); return await new Promise((res) => { const t = db.transaction('kv', 'readonly'); const rq = t.objectStore('kv').get(k); rq.onsuccess = () => res(rq.result); rq.onerror = () => res(null); }); } catch { return null; } }
  async function idbDel(k) { try { const db = await idb(); await new Promise((res) => { const t = db.transaction('kv', 'readwrite'); t.objectStore('kv').delete(k); t.oncomplete = res; t.onerror = res; }); } catch {} }

  // try to restore a previously-granted fsapi directory (needs a gesture to
  // re-verify on some browsers; we keep the handle and surface "reconnect")
  (async () => {
    if (!fsapiSupported) return;
    const h = await idbGet('fsapi-dir');
    if (h && typeof h.queryPermission === 'function') {
      const p = await h.queryPermission({ mode: 'readwrite' });
      if (p === 'granted') { FSAPI_DIR = h; notify(); }
      else { window.__cvFsapiPending = h; } // Bridge panel offers "reconnect"
    }
  })();

  // ---- fsapi path helpers ---------------------------------------------------
  async function dirFor(root, path, create) {
    const parts = path.split('/').filter(Boolean);
    const fileName = parts.pop();
    let dir = root;
    for (const part of parts) dir = await dir.getDirectoryHandle(part, { create: !!create });
    return { dir, fileName };
  }
  async function fsapiRead(root, path) {
    if (!root) throw new Error('[CV_HOST] no directory connected');
    const { dir, fileName } = await dirFor(root, path, false);
    const fh = await dir.getFileHandle(fileName);
    return (await fh.getFile()).text();
  }
  async function fsapiWrite(root, path, contents) {
    if (!root) throw new Error('[CV_HOST] no directory connected');
    const { dir, fileName } = await dirFor(root, path, true);
    const fh = await dir.getFileHandle(fileName, { create: true });
    const ws = await fh.createWritable();
    await ws.write(contents); await ws.close();
    return { file: path };
  }
  async function fsapiList(root, path) {
    if (!root) throw new Error('[CV_HOST] no directory connected');
    let dir = root;
    for (const part of (path || '').split('/').filter(Boolean)) dir = await dir.getDirectoryHandle(part);
    const out = [];
    for await (const [name, handle] of dir.entries()) out.push({ name, kind: handle.kind });
    return out;
  }
  async function reconnectFsapi() {
    const h = window.__cvFsapiPending;
    if (!h) throw new Error('[CV_HOST] nothing to reconnect');
    const p = await h.requestPermission({ mode: 'readwrite' });
    if (p !== 'granted') throw new Error('[CV_HOST] permission denied');
    FSAPI_DIR = h; delete window.__cvFsapiPending; notify(); return h.name;
  }

  // ==========================================================================
  window.CV_HOST = {
    // runtimes
    runtimes: RUNTIMES, registerRuntime, registerKind, ranked, best, reader, writer, canWrite, reconnectFsapi,
    // ops
    read, list, write, capabilities,
    // CV_AI bridge
    resolveProviderRuntime,
    // serializers
    registerSerializer, serialize, _serializers: SERIALIZERS,
    // changes
    changes, applySerialized,
    // the one call
    commit,
    // settings
    handoffMode, setHandoffMode, HANDOFF_MODES, autoApply, setAutoApply,
    // agent stash loop
    readStash, clearStash,
    // self-documentation + reactivity
    describe, subscribe, notify,
  };

  console.info('[CV_HOST] environment ready —', describe().modeLabel);
})();
