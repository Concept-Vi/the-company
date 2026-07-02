// atomicity/ingest.js
// ============================================================================
// CV_SOURCE — the Ingestion registry. Upload source material; the system reads
// it deeply, recognises WHAT it is and the CONTEXT it carries, mines it for the
// design DNA buried inside (palette, type feel, voice, structure, values,
// motifs), and brings each finding FORWARD as a single-sourced proposal you can
// review and stage through CV_HOST. Same shape as the other registries.
//
//   dna-signal = f(source, recognizers, analyzers)
//
//   • recognizers — detect a source's TYPE + CONTEXT (heuristic first, model
//     refines). brand-guide · voice-sample · palette/image · deck · stylesheet ·
//     notes · web-capture · data. Register more with registerRecognizer.
//   • analyzers — pull DEPTH for a dimension from a recognised source, each
//     finding carrying its evidence + an optional CV_HOST proposal. Register
//     more with registerAnalyzer.
//   • sources — the persisted corpus the system learns from.
//
// The deep read is the model (via CV_AI.complete) with a structured prompt that
// knows the system's vocabulary, so findings map to real change kinds
// (css.token, ai.entry voice behaviour, type/archetype). Image palette is
// extracted locally with canvas. Loud where it must be; per-source failures are
// surfaced, not swallowed.
// ============================================================================

(function () {
  'use strict';
  const AI = window.CV_AI;
  if (!AI) throw new Error('[CV_SOURCE] CV_AI must load first');
  const LS = 'atomicity:sources';
  const RECOGNIZERS = new Map(), ANALYZERS = new Map();
  const listeners = new Set();
  let SOURCES = load();

  function on(fn) { listeners.add(fn); return () => listeners.delete(fn); }
  function emit() { save(); for (const fn of listeners) { try { fn(); } catch (e) { console.error('[CV_SOURCE]', e); } } }
  function load() { try { return JSON.parse(localStorage.getItem(LS) || '[]'); } catch { return []; } }
  function save() { try { localStorage.setItem(LS, JSON.stringify(SOURCES.map(s => ({ ...s, text: (s.text || '').slice(0, 24000), dataUrl: s.kind === 'image' ? '' : undefined })))); } catch {} }
  function uid() { return 's_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 5); }

  // ---- corpus -------------------------------------------------------------
  function addSource(s) {
    const entry = { id: uid(), name: s.name || 'Untitled', mime: s.mime || 'text/plain', kind: s.kind || 'text', text: s.text || '', dataUrl: s.dataUrl || '', type: null, context: null, findings: [], status: 'new', addedAt: Date.now() };
    SOURCES = [entry, ...SOURCES]; emit(); return entry;
  }
  function get(id) { return SOURCES.find(s => s.id === id) || null; }
  function remove(id) { SOURCES = SOURCES.filter(s => s.id !== id); emit(); }
  function list() { return SOURCES.slice(); }
  function update(id, patch) { SOURCES = SOURCES.map(s => s.id === id ? { ...s, ...patch } : s); emit(); }

  // ---- recognisers (type + context) --------------------------------------
  function registerRecognizer(r) { if (!r || !r.id || typeof r.detect !== 'function') throw new Error('[CV_SOURCE] recognizer needs {id, detect}'); RECOGNIZERS.set(r.id, r); return r; }
  registerRecognizer({ id: 'by-shape', detect(s) {
    const n = (s.name || '').toLowerCase(), t = (s.text || '');
    if (s.kind === 'image') return { type: 'palette-image', context: 'A visual — palette and mood will be read from its pixels.', confidence: 0.9 };
    if (/\.(css|scss)$/.test(n) || /:root|--[a-z-]+:/.test(t)) return { type: 'stylesheet', context: 'Existing styles / tokens.', confidence: 0.8 };
    if (/brand|guideline|identity/.test(n)) return { type: 'brand-guide', context: 'A brand or identity document.', confidence: 0.7 };
    if (/voice|tone|copy|messaging/.test(n)) return { type: 'voice-sample', context: 'Writing whose voice we can learn.', confidence: 0.6 };
    if (/deck|pitch|slides|presentation/.test(n)) return { type: 'deck', context: 'A narrative deck — structure and arc.', confidence: 0.7 };
    if (/\.(json|csv|tsv)$/.test(n)) return { type: 'data', context: 'Structured data.', confidence: 0.6 };
    return { type: 'notes', context: 'Free material to read for intent.', confidence: 0.3 };
  } });

  function recognizeLocal(s) {
    let best = { type: 'notes', context: 'Free material.', confidence: 0 };
    for (const r of RECOGNIZERS.values()) { try { const g = r.detect(s); if (g && g.confidence > best.confidence) best = g; } catch {} }
    return best;
  }

  // ---- analyzers (depth) --------------------------------------------------
  function registerAnalyzer(a) { if (!a || !a.id || typeof a.run !== 'function') throw new Error('[CV_SOURCE] analyzer needs {id, run}'); ANALYZERS.set(a.id, a); return a; }

  // image → palette, extracted from pixels (no model needed)
  registerAnalyzer({ id: 'palette', dimensions: ['color'], types: ['palette-image'],
    async run(s) {
      if (!s.dataUrl) return [];
      const cols = await extractPalette(s.dataUrl);
      return cols.map((hex, i) => ({
        id: 'f_' + i, dimension: 'color', title: 'Palette colour ' + (i + 1),
        detail: 'A dominant colour read from the image.', evidence: hex, confidence: 0.8,
        proposal: { kind: 'css.token', title: 'Add colour ' + hex, payload: { name: 'ingested-' + i + 1, value: hex, role: 'from uploaded image' } },
      }));
    } });

  // image → vision read when a vision runtime is connected (export); the
  // analyzer asks for layout/type/voice/palette as findings. Palette analyzer
  // above always runs as the sandbox-safe floor.
  registerAnalyzer({ id: 'vision-read', dimensions: ['color', 'type', 'structure', 'voice', 'motif'], types: ['palette-image'],
    async run(s) {
      if (!s.dataUrl) return [];
      const provider = AI.resolveProvider ? safeResolve('vision') : null;
      if (!provider) return [];   // sandbox: no vision runtime — palette analyzer covers colour
      const prompt = 'Read this image as design source for the ConceptV system. Report layout/structure, type personality, any voice in visible copy, palette mood and recurring motifs. Few high-signal findings, each with evidence. JSON only: {"findings":[{"dimension","title","detail","evidence","confidence","proposal":{"kind":"css.token|ai.entry","title","payload"}}]}';
      let raw; try { raw = await AI.execute('vision.read', { surface: 'ingest', params: { image: s.dataUrl, prompt } }); }
      catch (e) { return []; }    // not available → silent floor (palette already ran)
      const json = salvage(typeof raw === 'string' ? raw : JSON.stringify(raw));
      return ((json && json.findings) || []).map((f, i) => ({ id: 'iv_' + i, dimension: f.dimension || 'structure', title: f.title || 'Finding', detail: f.detail || '', evidence: f.evidence || '', confidence: f.confidence != null ? f.confidence : 0.6, proposal: f.proposal && f.proposal.kind ? f.proposal : null }));
    } });

  function safeResolve(id) { try { return AI.resolveProvider(id); } catch { return null; } }

  // text → deep model read across design dimensions, with proposals
  registerAnalyzer({ id: 'deep-read', dimensions: ['color', 'type', 'voice', 'structure', 'value', 'motif'], types: ['*'],
    async run(s) {
      if (!s.text || s.text.length < 12) return [];
      const prompt = DEEP_PROMPT(s);
      let raw; try { raw = await AI.complete({ messages: [{ role: 'user', content: prompt }], max_tokens: 1800 }); } catch (e) { try { raw = await AI.complete(prompt); } catch (e2) { throw new Error('Deep read failed: ' + e2.message); } }
      window.__lastDeepRaw = raw;
      const json = salvage(raw);
      if (json && (json.type || json.context)) update(s.id, { type: json.type || s.type, context: json.context || s.context });
      const fs = (json && json.findings) || [];
      return fs.map((f, i) => ({
        id: 'd_' + i, dimension: f.dimension || 'value', title: f.title || 'Finding',
        detail: f.detail || '', evidence: f.evidence || '', confidence: f.confidence != null ? f.confidence : 0.6,
        proposal: f.proposal && f.proposal.kind ? f.proposal : null,
      }));
    } });

  // ---- the deep prompt — knows the system's vocabulary --------------------
  function DEEP_PROMPT(s) {
    return `You are Vi, analysing uploaded source material to improve a design system's DNA. The system speaks in five home-registries: design TOKENS (colour/type/space/depth — css.token), VOICE behaviours (ai.entry, layer "behaviour"), TYPES/archetypes (content→layout specs), and capabilities. Brand today: warm paper + gold + bronze, Sora/DM Sans, sentence-case voice.

Read the material below DEEPLY. First recognise what it IS and the context it carries. Then mine it for the design DNA inside — not surface description, but the meaningful signals worth bringing into the system: a palette or colour mood, type personality, the VOICE (tone, rhythm, forbidden moves), structural/narrative patterns, brand values, recurring motifs. Prefer few high-signal findings over many shallow ones. For each, cite the EVIDENCE (a short quote or detail from the source) and, where it should change the system, attach a concrete proposal.

SOURCE — name: "${s.name}", detected type: ${s.type || 'unknown'}
"""
${(s.text || '').slice(0, 12000)}
"""

Reply as JSON only:
{"type":"<refined type>","context":"<one sentence on what this is and why it matters>","findings":[
  {"dimension":"color|type|voice|structure|value|motif","title":"<short>","detail":"<what you found, plainly>","evidence":"<quote/detail from source>","confidence":0-1,
   "proposal":{"kind":"css.token|ai.entry","title":"<label>","rationale":"<why>","payload":{...}} }
]}
For each finding keep detail and evidence under ~22 words. Return AT MOST 6 of the highest-signal findings. Plain JSON, no markdown fence, nothing outside it.`;
  }

  // ---- orchestration ------------------------------------------------------
  async function recognize(id) {
    const s = get(id); if (!s) throw new Error('[CV_SOURCE] no source ' + id);
    const local = recognizeLocal(s);
    update(id, { type: local.type, context: local.context });
    return local;
  }
  async function analyze(id) {
    const s = get(id); if (!s) throw new Error('[CV_SOURCE] no source ' + id);
    if (!s.type) await recognize(id);
    const cur = get(id);
    update(id, { status: 'analyzing' });
    const findings = []; const errors = [];
    for (const a of ANALYZERS.values()) {
      const types = a.types || ['*'];
      if (!(types.includes('*') || types.includes(cur.type))) continue;
      try { const fs = await a.run(cur); for (const f of fs) findings.push({ ...f, analyzer: a.id }); }
      catch (e) { errors.push({ analyzer: a.id, error: e.message }); }
    }
    // model may also refine type/context via the deep-read result note — keep local type
    update(id, { findings, status: 'analyzed', errors, analyzedAt: Date.now() });
    return { type: cur.type, context: cur.context, findings, errors };
  }
  function bringForward(sourceId, findingId) {
    const s = get(sourceId); if (!s) return null;
    const f = (s.findings || []).find(x => x.id === findingId);
    if (!f || !f.proposal) throw new Error('[CV_SOURCE] finding has no proposal');
    return window.CV_HOST.commit({ ...f.proposal, rationale: (f.proposal.rationale || f.detail) + ' — from source "' + s.name + '".', provenance: 'vi' });
  }
  async function bringAll(sourceId) {
    const s = get(sourceId); if (!s) return [];
    const out = []; for (const f of (s.findings || [])) if (f.proposal) out.push(bringForward(sourceId, f.id)); return out;
  }

  // ---- canvas palette -----------------------------------------------------
  function extractPalette(dataUrl) {
    return new Promise((res) => {
      const img = new Image();
      img.onload = () => {
        const W = 64, H = Math.max(1, Math.round(W * img.height / img.width));
        const c = document.createElement('canvas'); c.width = W; c.height = H;
        const ctx = c.getContext('2d'); ctx.drawImage(img, 0, 0, W, H);
        let data; try { data = ctx.getImageData(0, 0, W, H).data; } catch { return res([]); }
        const buckets = {};
        for (let i = 0; i < data.length; i += 4) {
          const a = data[i + 3]; if (a < 128) continue;
          const r = data[i] >> 4, g = data[i + 1] >> 4, b = data[i + 2] >> 4;
          const k = r + ',' + g + ',' + b; (buckets[k] = buckets[k] || { n: 0, r: 0, g: 0, b: 0 });
          buckets[k].n++; buckets[k].r += data[i]; buckets[k].g += data[i + 1]; buckets[k].b += data[i + 2];
        }
        const top = Object.values(buckets).sort((a, b) => b.n - a.n).slice(0, 6);
        res(top.map(o => '#' + [o.r, o.g, o.b].map(v => Math.round(v / o.n).toString(16).padStart(2, '0')).join('')));
      };
      img.onerror = () => res([]);
      img.src = dataUrl;
    });
  }

  function salvage(raw) {
    let body = String(raw || '');
    const fence = body.match(/```(?:json)?\s*([\s\S]*?)(?:```|$)/); if (fence) body = fence[1];
    try { const j = JSON.parse(body); if (j && j.findings) return j; } catch {}
    const type = (body.match(/"type"\s*:\s*"([^"]+)"/) || [])[1];
    const context = (body.match(/"context"\s*:\s*"([^"]+)"/) || [])[1];
    const findings = [];
    const fi = body.indexOf('"findings"');
    if (fi >= 0) {
      const arr = body.slice(body.indexOf('[', fi));
      let depth = 0, start = -1, inStr = false, esc = false;
      for (let k = 0; k < arr.length; k++) {
        const ch = arr[k];
        if (inStr) { if (esc) esc = false; else if (ch === '\\') esc = true; else if (ch === '"') inStr = false; continue; }
        if (ch === '"') inStr = true;
        else if (ch === '{') { if (depth === 0) start = k; depth++; }
        else if (ch === '}') { depth--; if (depth === 0 && start >= 0) { try { findings.push(JSON.parse(arr.slice(start, k + 1))); } catch {} start = -1; } }
      }
    }
    return { type, context, findings };
  }
  function parseJson(text) {
    const m = String(text || '').match(/```(?:json)?\s*([\s\S]*?)```/);
    let body = m ? m[1] : text;
    const i = body.indexOf('{'); if (i > 0) body = body.slice(i);
    try { return JSON.parse(body); } catch { try { return JSON.parse(body.slice(0, body.lastIndexOf('}') + 1)); } catch { return null; } }
  }

  // ---- CV_AI capabilities (in the one catalogue) --------------------------
  AI.register({ id: 'source.recognize', name: 'Recognise source', layer: 'capability', family: 'ingest', description: 'Detect an uploaded source’s type and context.', surfaces: ['ingest'], role: 'text', icon: 'search', provenance: 'built-in', run: a => recognize(a.params.id) }, { silent: true });
  AI.register({ id: 'source.analyze', name: 'Analyse source deeply', layer: 'capability', family: 'ingest', description: 'Mine an uploaded source for design DNA across colour, type, voice, structure, values and motifs.', surfaces: ['ingest'], role: 'text', behaviours: ['voice.conceptv'], icon: 'sparkles', provenance: 'built-in', run: a => analyze(a.params.id) }, { silent: true });
  AI.register({ id: 'source.synthesize', name: 'Bring findings forward', layer: 'capability', family: 'ingest', description: 'Stage a finding’s proposal into the system through CV_HOST.', surfaces: ['ingest'], provider: 'host-fs', icon: 'wand', provenance: 'built-in', run: a => bringForward(a.params.source, a.params.finding) }, { silent: true });
  AI.register({ id: 'vision.read', name: 'Read an image', layer: 'capability', family: 'ingest', description: 'Understand an image (screenshot/moodboard) via the vision provider. Throws in the sandbox where no vision runtime is connected — callers fall back to local palette extraction.', surfaces: ['ingest'], provider: 'vision', behaviours: ['voice.conceptv'], icon: 'eye', provenance: 'built-in', run: async a => { const p = AI.resolveProvider('vision'); if (!p || !p.runtime || !p.runtime.complete) throw new Error('No vision runtime connected (export AtomiCity with a vision model to read images deeply).'); return p.runtime.complete({ image: a.params.image, prompt: a.params.prompt }); } }, { silent: true });

  function describe() {
    return {
      sources: SOURCES.length,
      recognizers: [...RECOGNIZERS.keys()],
      analyzers: [...ANALYZERS.values()].map(a => ({ id: a.id, dimensions: a.dimensions, types: a.types })),
    };
  }

  window.CV_SOURCE = {
    RECOGNIZERS, ANALYZERS, registerRecognizer, registerAnalyzer,
    addSource, get, remove, list, update,
    recognize, analyze, bringForward, bringAll, extractPalette,
    describe, on, subscribe: on,
  };
  console.info('[CV_SOURCE] ingestion registry ready');
})();
