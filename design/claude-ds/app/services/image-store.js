// services/image-store.js — shared image library across the studio.
//
// One global window.cvImageStore. Every image surface in the system reads and
// writes through this — the Imagery canvas, the Build canvas, the Workshop
// embed blocks, and Vi (when it adopts a generated image).
//
// Storage shape:
//   {
//     system:   Image[]               // brand-wide imagery
//     projects: { [pid]: Image[] }    // per-project assets
//     hubs:     { [pid]: Pano[] }     // per-project 360 captures
//     ai:       Image[]               // recent AI generations (history)
//     projectsList: Project[]         // known projects
//   }
//
// Image: { id, src, name, w?, h?, tags?[], note?, createdAt, source }
// Pano:  { id, src, name, title?, hotspots?[], yaw?, createdAt }
// Project: { id, name, client, hubCount }
//
// Images are stored as data URLs after a downsample pass (≤ 1280 px on the
// long edge for stills, ≤ 2400 px for panos). Quality is lossy JPEG.

(function () {
  const NS = 'cvstudio:cvImageStore:v1';

  const DEFAULT_PROJECTS = [
    { id: 'eclipse-tower',     name: 'Eclipse Tower',     client: 'Northpoint Properties', hubCount: 3 },
    { id: 'bayside-villa',     name: 'Bayside Villa',     client: 'Sienna Developments',   hubCount: 1 },
    { id: 'lumen-apartments',  name: 'Lumen Apartments',  client: 'Atlas Residential',     hubCount: 2 },
  ];

  const DEFAULT_DATA = {
    system: [],
    projects: { 'eclipse-tower': [], 'bayside-villa': [], 'lumen-apartments': [] },
    hubs:     { 'eclipse-tower': [], 'bayside-villa': [], 'lumen-apartments': [] },
    ai:       [],
    projectsList: DEFAULT_PROJECTS,
  };

  function load() {
    try {
      const raw = localStorage.getItem(NS);
      if (!raw) return JSON.parse(JSON.stringify(DEFAULT_DATA));
      const parsed = JSON.parse(raw);
      return {
        ...DEFAULT_DATA,
        ...parsed,
        projects: { ...DEFAULT_DATA.projects, ...(parsed.projects || {}) },
        hubs:     { ...DEFAULT_DATA.hubs,     ...(parsed.hubs     || {}) },
        projectsList: parsed.projectsList || DEFAULT_PROJECTS,
      };
    } catch {
      return JSON.parse(JSON.stringify(DEFAULT_DATA));
    }
  }
  function persist(data) {
    try { localStorage.setItem(NS, JSON.stringify(data)); } catch (e) {
      // localStorage quota — surface a toast.
      window.dsaToast?.('Storage limit reached. Remove some images and try again.');
    }
    listeners.forEach(fn => { try { fn(data); } catch {} });
  }

  let data = load();
  const listeners = new Set();

  function uid() { return 'img_' + Math.random().toString(36).slice(2, 10); }

  // ---- Downsample a File / Blob / src to a JPEG data URL.
  async function downsample(input, opts) {
    const maxEdge   = opts?.maxEdge   || 1280;
    const quality   = opts?.quality   || 0.85;
    const mimeOut   = opts?.mime      || 'image/jpeg';

    const src = typeof input === 'string'
      ? input
      : await new Promise((resolve, reject) => {
          const fr = new FileReader();
          fr.onload = () => resolve(fr.result);
          fr.onerror = reject;
          fr.readAsDataURL(input);
        });

    const img = await new Promise((resolve, reject) => {
      const i = new Image();
      i.onload = () => resolve(i);
      i.onerror = reject;
      i.crossOrigin = 'anonymous';
      i.src = src;
    });

    let { naturalWidth: w, naturalHeight: h } = img;
    const longEdge = Math.max(w, h);
    if (longEdge > maxEdge) {
      const s = maxEdge / longEdge;
      w = Math.round(w * s);
      h = Math.round(h * s);
    }
    const canvas = document.createElement('canvas');
    canvas.width = w; canvas.height = h;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0, w, h);
    return { src: canvas.toDataURL(mimeOut, quality), w, h };
  }

  function emit() { persist(data); }

  // ---- Public API ----
  const api = {
    snapshot() { return JSON.parse(JSON.stringify(data)); },
    subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); },

    // Projects
    listProjects() { return [...data.projectsList]; },
    addProject(p) {
      const proj = { id: p.id || ('proj_' + Math.random().toString(36).slice(2, 8)), name: p.name || 'Untitled', client: p.client || '', hubCount: p.hubCount || 0 };
      data.projectsList = [...data.projectsList, proj];
      data.projects[proj.id] = data.projects[proj.id] || [];
      data.hubs[proj.id]     = data.hubs[proj.id]     || [];
      emit();
      return proj;
    },

    // Collections
    list(scope, pid) {
      if (scope === 'system') return [...(data.system || [])];
      if (scope === 'ai')     return [...(data.ai || [])];
      if (scope === 'projects') return [...(data.projects[pid] || [])];
      if (scope === 'hubs')     return [...(data.hubs[pid] || [])];
      return [];
    },

    async addFromFile(scope, pid, file, meta) {
      const { src, w, h } = await downsample(file, scope === 'hubs' ? { maxEdge: 2400, quality: 0.82 } : {});
      const rec = {
        id: uid(),
        src, w, h,
        name: meta?.name || file.name || 'Untitled',
        tags: meta?.tags || [],
        note: meta?.note || '',
        source: meta?.source || 'upload',
        createdAt: Date.now(),
        ...(scope === 'hubs' ? { yaw: 0, hotspots: [] } : {}),
      };
      this._push(scope, pid, rec);
      return rec;
    },

    async addFromSrc(scope, pid, src, meta) {
      const { src: out, w, h } = await downsample(src, scope === 'hubs' ? { maxEdge: 2400 } : {});
      const rec = {
        id: uid(),
        src: out, w, h,
        name: meta?.name || 'Generated image',
        tags: meta?.tags || [],
        note: meta?.note || '',
        source: meta?.source || 'ai',
        prompt: meta?.prompt,
        createdAt: Date.now(),
        ...(scope === 'hubs' ? { yaw: 0, hotspots: [] } : {}),
      };
      this._push(scope, pid, rec);
      return rec;
    },

    _push(scope, pid, rec) {
      if (scope === 'system')   data.system   = [rec, ...(data.system || [])];
      if (scope === 'ai')       data.ai       = [rec, ...(data.ai || [])].slice(0, 60);
      if (scope === 'projects') data.projects[pid] = [rec, ...(data.projects[pid] || [])];
      if (scope === 'hubs')     data.hubs[pid]     = [rec, ...(data.hubs[pid] || [])];
      emit();
    },

    update(scope, pid, id, patch) {
      const apply = (list) => list.map(im => im.id === id ? { ...im, ...patch } : im);
      if (scope === 'system')   data.system   = apply(data.system);
      if (scope === 'ai')       data.ai       = apply(data.ai);
      if (scope === 'projects') data.projects[pid] = apply(data.projects[pid] || []);
      if (scope === 'hubs')     data.hubs[pid]     = apply(data.hubs[pid] || []);
      emit();
    },

    remove(scope, pid, id) {
      const filt = (list) => list.filter(im => im.id !== id);
      if (scope === 'system')   data.system   = filt(data.system);
      if (scope === 'ai')       data.ai       = filt(data.ai);
      if (scope === 'projects') data.projects[pid] = filt(data.projects[pid] || []);
      if (scope === 'hubs')     data.hubs[pid]     = filt(data.hubs[pid] || []);
      emit();
    },

    counts() {
      const systemCount = data.system.length;
      const projectCount = Object.values(data.projects).reduce((a, b) => a + b.length, 0);
      const hubCount     = Object.values(data.hubs).reduce((a, b) => a + b.length, 0);
      return {
        total:    systemCount + projectCount + hubCount,
        system:   systemCount,
        projects: projectCount,
        hubs:     hubCount,
        ai:       data.ai.length,
      };
    },

    // Approximate footprint of stored data URLs in bytes
    bytes() {
      try {
        const raw = localStorage.getItem(NS) || '';
        return raw.length;
      } catch { return 0; }
    },

    downsample,
  };

  window.cvImageStore = api;
})();
