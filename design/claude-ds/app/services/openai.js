// services/openai.js — global OpenAI service used across the whole app.
//
// Single source of truth for the user's API key, model preferences, and every
// image call (generate / edit / variation). Every canvas that wants AI imagery
// goes through window.cvOpenAI so we keep one consistent surface, one place to
// swap models, and one place to handle errors + rate limits.
//
// Vi (ChatRail) consults the same service when a user asks for an image in
// chat — the answer comes back as an image message instead of text.
//
// MODEL DISCOVERY
// Image models ship constantly. Rather than hard-code a static dropdown, we:
//   1. Maintain a STATIC capability registry of well-known image models
//      (sizes, qualities, supports edit/variation/style). This is the ground
//      truth for any model id we recognise.
//   2. Provide listImageModels() which hits /v1/models and filters to image-
//      capable ones — matching either the static registry or known prefixes
//      (gpt-image-*, dall-e-*, imagen-*, etc). Result cached for 24h.
//   3. Provide getModelCapabilities(id) which returns the registered caps OR
//      best-guess defaults inferred from the id family.
//
// Anything UI-side that lists models should call listImageModels(); anything
// asking "what sizes / qualities does this model support?" should call
// getModelCapabilities().

(function () {
  const NS = 'cvstudio:cvOpenAI:';
  const KEY_SETTINGS = NS + 'settings';
  const KEY_MODELS   = NS + 'models';
  const MODEL_TTL_MS = 24 * 60 * 60 * 1000;

  const DEFAULT_SETTINGS = {
    apiKey: '',
    proxyUrl: '',
    imageModel: 'gpt-image-2',
    defaultSize: '1024x1024',
    defaultQuality: 'high',
    defaultStyle: 'natural',
    organization: '',
    enableForVi: true,
    safeMode: true,
  };

  /* ============================================================
     STATIC MODEL CAPABILITY REGISTRY
     Add new models here as OpenAI releases them. Unknown models
     still work — they'll fall back to inferred defaults.
     ============================================================ */
  const MODEL_REGISTRY = {
    'gpt-image-2': {
      family:     'gpt-image',
      label:      'GPT Image 2',
      tagline:    'Best for production. Photoreal, readable text, identity-safe edits.',
      sizes:      ['auto', '1024x1024', '1536x1024', '1024x1536', '2048x2048', '2048x1152', '1152x2048', '3840x2160', '2160x3840'],
      qualities:  ['low', 'medium', 'high', 'auto'],
      outputFormats: ['png', 'jpeg', 'webp'],
      backgrounds: ['auto', 'opaque'],   // transparent NOT supported on gpt-image-2
      moderations: ['auto', 'low'],
      maxRefImages: 16,
      maxPromptChars: 32000,
      supports:   { generate: true, edit: true, variation: false, style: false, n: true, maxN: 10, stream: true, partialImages: 3, customSize: true, mask: true, multiRef: true },
      release:    '2026-04',
      tier:       'flagship',
    },
    'gpt-image-2-2026-04-21': {
      family:     'gpt-image',
      label:      'GPT Image 2 · 2026-04-21 snapshot',
      tagline:    'Pinned snapshot of gpt-image-2 for reproducible production.',
      sizes:      ['auto', '1024x1024', '1536x1024', '1024x1536', '2048x2048', '2048x1152', '1152x2048', '3840x2160', '2160x3840'],
      qualities:  ['low', 'medium', 'high', 'auto'],
      outputFormats: ['png', 'jpeg', 'webp'],
      backgrounds: ['auto', 'opaque'],
      moderations: ['auto', 'low'],
      maxRefImages: 16,
      maxPromptChars: 32000,
      supports:   { generate: true, edit: true, variation: false, style: false, n: true, maxN: 10, stream: true, partialImages: 3, customSize: true, mask: true, multiRef: true },
      release:    '2026-04-21',
      tier:       'flagship',
    },
    'gpt-image-1': {
      family:     'gpt-image',
      label:      'GPT Image 1',
      tagline:    'Previous flagship. Native multimodal generation.',
      sizes:      ['1024x1024', '1536x1024', '1024x1536'],
      qualities:  ['low', 'medium', 'high', 'auto'],
      outputFormats: ['png'],
      backgrounds: ['auto', 'opaque', 'transparent'],
      moderations: ['auto', 'low'],
      maxRefImages: 4,
      maxPromptChars: 32000,
      supports:   { generate: true, edit: true, variation: false, style: false, n: true, maxN: 10, stream: false, partialImages: 0, customSize: false, mask: true, multiRef: true },
      release:    '2025-04',
      tier:       'standard',
    },
    'dall-e-3': {
      family:     'dall-e',
      label:      'DALL·E 3',
      tagline:    'Very prompt-faithful. Vivid / natural style param.',
      sizes:      ['1024x1024', '1792x1024', '1024x1792'],
      qualities:  ['standard', 'hd'],
      outputFormats: ['png'],
      backgrounds: [],
      moderations: [],
      maxRefImages: 0,
      maxPromptChars: 4000,
      supports:   { generate: true, edit: false, variation: false, style: true, n: false, maxN: 1, stream: false, partialImages: 0, customSize: false, mask: false, multiRef: false },
      release:    '2023-10',
      tier:       'standard',
    },
    'dall-e-2': {
      family:     'dall-e',
      label:      'DALL·E 2',
      tagline:    'Fastest. Only model with variations endpoint.',
      sizes:      ['256x256', '512x512', '1024x1024'],
      qualities:  [],
      outputFormats: ['png'],
      backgrounds: [],
      moderations: [],
      maxRefImages: 1,
      maxPromptChars: 1000,
      supports:   { generate: true, edit: true, variation: true, style: false, n: true, maxN: 10, stream: false, partialImages: 0, customSize: false, mask: true, multiRef: false },
      release:    '2022-11',
      tier:       'legacy',
    },
  };

  // Patterns the model-list filter will accept even if a specific id isn't
  // in the static registry. New family names go here so a brand-new model
  // automatically appears in the dropdown.
  const IMAGE_MODEL_PATTERNS = [
    /^gpt-image(-|$)/i,
    /^dall-e(-|$)/i,
    /^imagen(-|$)/i,
    /^omni-image(-|$)/i,   // hypothetical future
    /^image-/i,
  ];

  function isLikelyImageModel(id) {
    if (MODEL_REGISTRY[id]) return true;
    return IMAGE_MODEL_PATTERNS.some(re => re.test(id));
  }

  function inferCapabilities(id) {
    // Pick a known family member as the template, then override the id.
    if (/^gpt-image-2/i.test(id)) {
      return { ...MODEL_REGISTRY['gpt-image-2'], label: id, tagline: 'GPT Image 2 family — capabilities inferred.', tier: 'flagship' };
    }
    if (/^gpt-image-1/i.test(id)) {
      return { ...MODEL_REGISTRY['gpt-image-1'], label: id, tagline: 'GPT Image 1 family — capabilities inferred.', tier: 'standard' };
    }
    if (/^gpt-image/i.test(id)) {
      return { ...MODEL_REGISTRY['gpt-image-2'], label: id, tagline: 'New GPT Image model — capabilities inferred from family.', tier: 'flagship' };
    }
    if (/^dall-e-3/i.test(id))  return { ...MODEL_REGISTRY['dall-e-3'], label: id, tier: 'standard' };
    if (/^dall-e-2/i.test(id))  return { ...MODEL_REGISTRY['dall-e-2'], label: id, tier: 'legacy' };
    if (/^dall-e/i.test(id))    return { ...MODEL_REGISTRY['dall-e-3'], label: id, tagline: 'DALL·E family — capabilities inferred.', tier: 'standard' };
    // Generic image model: conservative defaults.
    return {
      family: id.split('-')[0],
      label: id,
      tagline: 'Image model — capabilities inferred from defaults.',
      sizes: ['1024x1024'],
      qualities: [],
      outputFormats: ['png'],
      backgrounds: [],
      moderations: [],
      maxRefImages: 0,
      maxPromptChars: 4000,
      supports: { generate: true, edit: false, variation: false, style: false, n: true, maxN: 1, stream: false, partialImages: 0, customSize: false, mask: false, multiRef: false },
      tier: 'standard',
    };
  }

  function getModelCapabilities(id) {
    if (MODEL_REGISTRY[id]) return MODEL_REGISTRY[id];
    return inferCapabilities(id);
  }

  function loadSettings() {
    try {
      const raw = localStorage.getItem(KEY_SETTINGS);
      if (!raw) return { ...DEFAULT_SETTINGS };
      return { ...DEFAULT_SETTINGS, ...JSON.parse(raw) };
    } catch {
      return { ...DEFAULT_SETTINGS };
    }
  }
  function saveSettings(next) {
    try { localStorage.setItem(KEY_SETTINGS, JSON.stringify(next)); } catch {}
    listeners.forEach(fn => { try { fn(next); } catch {} });
  }
  function loadCachedModels() {
    try {
      const raw = localStorage.getItem(KEY_MODELS);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      if (typeof parsed?.fetchedAt !== 'number') return null;
      return parsed;
    } catch { return null; }
  }
  function saveCachedModels(payload) {
    try { localStorage.setItem(KEY_MODELS, JSON.stringify(payload)); } catch {}
    modelListeners.forEach(fn => { try { fn(payload); } catch {} });
  }

  let settings = loadSettings();
  const listeners = new Set();
  const modelListeners = new Set();

  function endpoint(path) {
    if (settings.proxyUrl) return settings.proxyUrl.replace(/\/$/, '') + path;
    return 'https://api.openai.com' + path;
  }
  function authHeaders(extra) {
    const h = { Authorization: `Bearer ${settings.apiKey}`, ...(extra || {}) };
    if (settings.organization) h['OpenAI-Organization'] = settings.organization;
    return h;
  }
  function isConfigured() { return Boolean(settings.apiKey && settings.apiKey.startsWith('sk-')); }
  function fail(message, code) { const e = new Error(message); e.code = code || 'cv-openai/unknown'; return e; }

  async function readError(res) {
    let body = '';
    try { body = await res.text(); } catch {}
    try {
      const parsed = JSON.parse(body);
      return parsed?.error?.message || parsed?.message || body;
    } catch { return body || `HTTP ${res.status}`; }
  }

  /* ============================================================
     MODEL LIST — fetch /v1/models, filter to image-capable,
     attach capabilities, cache. Returns the cached payload.
     ============================================================ */
  async function listImageModels(opts) {
    const cached = loadCachedModels();
    const stale = !cached || (Date.now() - cached.fetchedAt) > MODEL_TTL_MS;
    if (cached && !stale && !opts?.force) return cached;

    if (!isConfigured()) {
      // No key — return static registry as a fallback "preview" list.
      const fallback = {
        fetchedAt: Date.now(),
        source: 'static',
        models: Object.entries(MODEL_REGISTRY).map(([id, caps]) => ({ id, ...caps })),
      };
      saveCachedModels(fallback);
      return fallback;
    }

    let res;
    try {
      res = await fetch(endpoint('/v1/models'), { headers: authHeaders() });
    } catch (e) {
      throw fail('Could not reach OpenAI to list models.', 'cv-openai/network');
    }
    if (!res.ok) throw fail(await readError(res), `cv-openai/http-${res.status}`);
    const data = await res.json();
    const all = data.data || [];

    const imageOnly = all
      .map(m => m.id)
      .filter(id => isLikelyImageModel(id))
      .sort((a, b) => {
        // Flagship → standard → legacy, then alphabetical
        const ta = getModelCapabilities(a).tier;
        const tb = getModelCapabilities(b).tier;
        const order = { flagship: 0, standard: 1, legacy: 2 };
        if (order[ta] !== order[tb]) return order[ta] - order[tb];
        return a.localeCompare(b);
      });

    // Make sure registered models always appear, even if /v1/models hid them.
    for (const id of Object.keys(MODEL_REGISTRY)) {
      if (!imageOnly.includes(id)) imageOnly.push(id);
    }

    const models = imageOnly.map(id => ({ id, ...getModelCapabilities(id) }));
    const payload = {
      fetchedAt: Date.now(),
      source: 'api',
      models,
      raw: all.length,
    };
    saveCachedModels(payload);
    return payload;
  }

  /* ============================================================
     SIZE VALIDATION (gpt-image-2 supports arbitrary sizes)
     Rules: multiples of 16, aspect ratio between 1:3 and 3:1,
     max edge 3840, total pixels 655,360 to 8,294,400.
     ============================================================ */
  function validateSize(modelId, sizeStr) {
    if (sizeStr === 'auto') return { ok: true };
    const m = /^(\d+)x(\d+)$/i.exec(sizeStr || '');
    if (!m) return { ok: false, reason: 'Use WIDTHxHEIGHT format.' };
    const w = parseInt(m[1], 10), h = parseInt(m[2], 10);
    const caps = getModelCapabilities(modelId);
    if (caps.supports.customSize) {
      if (w % 16 !== 0 || h % 16 !== 0) return { ok: false, reason: 'Width and height must be multiples of 16.' };
      const ar = w / h;
      if (ar < 1/3 || ar > 3) return { ok: false, reason: 'Aspect ratio must be between 1:3 and 3:1.' };
      if (Math.max(w, h) > 3840) return { ok: false, reason: 'Largest edge can be at most 3840 px.' };
      const px = w * h;
      if (px < 655360)  return { ok: false, reason: 'Below minimum 655,360 total pixels.' };
      if (px > 8294400) return { ok: false, reason: 'Above maximum 8,294,400 total pixels.' };
      const experimental = px > (2560 * 1440);
      return { ok: true, experimental };
    }
    if (!caps.sizes.includes(sizeStr)) {
      return { ok: false, reason: `${sizeStr} is not supported by ${modelId}. Try ${caps.sizes.slice(0,3).join(' / ')}.` };
    }
    return { ok: true };
  }

  /* ============================================================
     PROMPT BUILDER — pulls brand context onto every prompt so
     Vi's image outputs match ConceptV unless the caller suppresses
     this with brandEnrich:false.
     ============================================================ */
  const BRAND_SUFFIX = ` Style: warm-paper-with-gold-ink — ivory canvas (#FBF7EC), warm ink (#1F1A12), saturated gold (#E0C010), bronze illustration accents; natural light, warm tones, no cool greys.`;
  function buildPrompt(text, opts) {
    if (opts?.brandEnrich === false) return text;
    if (text.toLowerCase().includes('conceptv')) return text; // already branded
    return text.trimEnd() + BRAND_SUFFIX;
  }

  function resolveQuality(requested, caps) {
    if (!caps.qualities.length) return undefined;
    if (caps.qualities.includes(requested)) return requested;
    // Translation table for generic tier names.
    const map = { high: 'hd', medium: 'standard', low: 'standard' };
    if (map[requested] && caps.qualities.includes(map[requested])) return map[requested];
    return caps.qualities[0];
  }

  /* ---- Image generation ----
     opts: { prompt, model, n, size, quality, output_format, output_compression,
             background, moderation, stream, partial_images, user,
             brandEnrich, onPartial(b64,index) } */
  async function generateImage(opts) {
    if (!isConfigured()) throw fail('OpenAI API key not set. Open Settings to add one.', 'cv-openai/no-key');
    const promptRaw = String(opts?.prompt || '').trim();
    if (!promptRaw) throw fail('Prompt is empty.', 'cv-openai/bad-input');

    const modelId = opts.model || settings.imageModel;
    const caps    = getModelCapabilities(modelId);
    if (promptRaw.length > caps.maxPromptChars) throw fail(`Prompt is over ${caps.maxPromptChars} chars (you sent ${promptRaw.length}).`, 'cv-openai/bad-input');

    const prompt = buildPrompt(promptRaw, opts);

    let size = opts.size || settings.defaultSize;
    const sizeCheck = validateSize(modelId, size);
    if (!sizeCheck.ok) {
      size = caps.sizes[0] === 'auto' ? '1024x1024' : caps.sizes[0];
    }

    const body = {
      model:  modelId,
      prompt,
      n:      caps.supports.n ? Math.min(opts.n || 1, caps.supports.maxN || 1) : 1,
      size,
    };
    if (caps.supports.style)           body.style = opts.style || settings.defaultStyle || 'natural';
    if (caps.qualities.length)         body.quality = resolveQuality(opts.quality || settings.defaultQuality, caps);
    if (caps.outputFormats?.length && opts.output_format && caps.outputFormats.includes(opts.output_format)) body.output_format = opts.output_format;
    if (opts.output_compression != null && (body.output_format === 'jpeg' || body.output_format === 'webp')) body.output_compression = Math.max(0, Math.min(100, opts.output_compression));
    if (caps.backgrounds?.length && opts.background && caps.backgrounds.includes(opts.background)) body.background = opts.background;
    if (caps.moderations?.length && opts.moderation && caps.moderations.includes(opts.moderation))  body.moderation = opts.moderation;
    if (opts.user) body.user = opts.user;

    const wantStream = !!(opts.stream && caps.supports.stream && opts.onPartial);
    if (wantStream) {
      body.stream = true;
      if (opts.partial_images != null) body.partial_images = Math.max(0, Math.min(caps.supports.partialImages || 3, opts.partial_images));
      return streamImagesRequest('/v1/images/generations', body, opts);
    }

    let res;
    try {
      res = await fetch(endpoint('/v1/images/generations'), {
        method: 'POST',
        headers: authHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify(body),
      });
    } catch (e) {
      throw fail(
        `Could not reach OpenAI${settings.proxyUrl ? ' through your proxy' : ' directly from the browser'}. ` +
        `OpenAI may not allow direct CORS calls — set a proxy URL in Settings.`,
        'cv-openai/network'
      );
    }
    if (!res.ok) throw fail(await readError(res), `cv-openai/http-${res.status}`);
    const data = await res.json();
    return (data.data || []).map(d => normalizeImage(d, prompt, body.size, body.output_format || 'png'));
  }

  /* ---- Image edit / compose / mask ----
     opts: { prompt, model, images?: Blob[]|Blob, imageBlob?, mask?, n, size,
             quality, output_format, output_compression, background, moderation,
             stream, partial_images, brandEnrich, onPartial } */
  async function editImage(opts) {
    if (!isConfigured()) throw fail('OpenAI API key not set. Open Settings to add one.', 'cv-openai/no-key');
    const { prompt: promptRaw, mask } = opts || {};
    if (!opts.images && !opts.imageBlob) throw fail('Source image required.', 'cv-openai/bad-input');
    if (!promptRaw) throw fail('Edit prompt required.', 'cv-openai/bad-input');

    const modelId = opts.model || settings.imageModel;
    const caps    = getModelCapabilities(modelId);
    if (!caps.supports.edit) throw fail(`Model ${modelId} does not support editing.`, 'cv-openai/unsupported');

    const images = Array.isArray(opts.images) ? opts.images : (opts.images ? [opts.images] : [opts.imageBlob]);
    if (images.length > (caps.maxRefImages || 0)) throw fail(`Model supports at most ${caps.maxRefImages} reference images.`, 'cv-openai/bad-input');

    const prompt = buildPrompt(promptRaw, opts);
    const requested = opts.size || settings.defaultSize;
    const sCheck = validateSize(modelId, requested);
    const useSize = sCheck.ok ? requested : (caps.sizes[0] === 'auto' ? '1024x1024' : caps.sizes[0]);

    const form = new FormData();
    form.append('model', modelId);
    form.append('prompt', prompt);
    if (images.length === 1) form.append('image', images[0], 'source.png');
    else for (const blob of images) form.append('image[]', blob, 'source.png');
    if (mask) form.append('mask', mask, 'mask.png');
    form.append('size', useSize);
    if (caps.supports.n)        form.append('n', String(Math.min(opts.n || 1, caps.supports.maxN || 1)));
    if (caps.qualities.length)  form.append('quality', resolveQuality(opts.quality || settings.defaultQuality, caps));
    if (caps.outputFormats?.length && opts.output_format && caps.outputFormats.includes(opts.output_format)) form.append('output_format', opts.output_format);
    if (opts.output_compression != null && (opts.output_format === 'jpeg' || opts.output_format === 'webp')) form.append('output_compression', String(Math.max(0, Math.min(100, opts.output_compression))));
    if (caps.backgrounds?.length && opts.background && caps.backgrounds.includes(opts.background)) form.append('background', opts.background);
    if (caps.moderations?.length && opts.moderation && caps.moderations.includes(opts.moderation))  form.append('moderation', opts.moderation);

    const wantStream = !!(opts.stream && caps.supports.stream && opts.onPartial);
    if (wantStream) {
      form.append('stream', 'true');
      if (opts.partial_images != null) form.append('partial_images', String(Math.max(0, Math.min(caps.supports.partialImages || 3, opts.partial_images))));
      return streamImagesRequestForm('/v1/images/edits', form, opts);
    }

    let res;
    try {
      res = await fetch(endpoint('/v1/images/edits'), { method: 'POST', headers: authHeaders(), body: form });
    } catch (e) { throw fail('Could not reach OpenAI. See Settings for a proxy option.', 'cv-openai/network'); }
    if (!res.ok) throw fail(await readError(res), `cv-openai/http-${res.status}`);
    const data = await res.json();
    return (data.data || []).map(d => normalizeImage(d, prompt, useSize, opts.output_format || 'png'));
  }

  /* ---- Streaming helpers ---- */
  async function streamImagesRequest(path, body, opts) {
    return streamSSE(
      endpoint(path),
      { method: 'POST', headers: authHeaders({ 'Content-Type': 'application/json' }), body: JSON.stringify(body) },
      body, opts
    );
  }
  async function streamImagesRequestForm(path, form, opts) {
    return streamSSE(endpoint(path), { method: 'POST', headers: authHeaders(), body: form }, {}, opts);
  }
  async function streamSSE(url, init, body, opts) {
    let res;
    try { res = await fetch(url, init); }
    catch (e) { throw fail('Could not reach OpenAI to stream.', 'cv-openai/network'); }
    if (!res.ok) throw fail(await readError(res), `cv-openai/http-${res.status}`);
    const reader = res.body.getReader();
    const dec = new TextDecoder();
    let buf = '';
    const completed = [];
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      const blocks = buf.split(/\n\n/);
      buf = blocks.pop();
      for (const block of blocks) {
        const dataLine = block.split('\n').find(l => l.startsWith('data:'));
        if (!dataLine) continue;
        const payload = dataLine.slice(5).trim();
        if (payload === '[DONE]') continue;
        try {
          const evt = JSON.parse(payload);
          if (evt.type && evt.type.includes('partial_image') && evt.b64_json) {
            opts.onPartial?.({ src: `data:image/${evt.output_format || 'png'};base64,${evt.b64_json}`, index: evt.partial_image_index ?? 0 });
          } else if (evt.type && evt.type.includes('completed') && evt.b64_json) {
            completed.push({ src: `data:image/${evt.output_format || 'png'};base64,${evt.b64_json}`, prompt: body.prompt || '', size: body.size || evt.size, type: 'b64', usage: evt.usage });
          } else if (evt.b64_json) {
            completed.push({ src: `data:image/${evt.output_format || 'png'};base64,${evt.b64_json}`, prompt: body.prompt || '', size: body.size || evt.size, type: 'b64' });
          }
        } catch {}
      }
    }
    return completed;
  }

  /* ---- Responses API multi-turn image editing ---- */
  async function responsesImage(opts) {
    if (!isConfigured()) throw fail('OpenAI API key not set.', 'cv-openai/no-key');
    const body = {
      model: opts.responsesModel || 'gpt-5.5',
      input: [],
      tools: [{ type: 'image_generation' }],
    };
    if (opts.previous_response_id) body.previous_response_id = opts.previous_response_id;
    if (opts.action && opts.action !== 'auto') body.tool_choice = { type: 'image_generation' };

    const contentItems = [];
    if (opts.input) contentItems.push({ type: 'input_text', text: opts.input });
    if (Array.isArray(opts.imageDataUrls)) for (const url of opts.imageDataUrls) contentItems.push({ type: 'input_image', image_url: url });
    body.input.push({ role: 'user', content: contentItems });

    const toolParams = {};
    if (opts.size)        toolParams.size = opts.size;
    if (opts.quality)     toolParams.quality = opts.quality;
    if (opts.format)      toolParams.format = opts.format;
    if (opts.background)  toolParams.background = opts.background;
    if (opts.action)      toolParams.action = opts.action;
    if (Object.keys(toolParams).length) body.tools[0] = { type: 'image_generation', ...toolParams };

    let res;
    try {
      res = await fetch(endpoint('/v1/responses'), {
        method: 'POST',
        headers: authHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify(body),
      });
    } catch { throw fail('Could not reach OpenAI for chat-edit.', 'cv-openai/network'); }
    if (!res.ok) throw fail(await readError(res), `cv-openai/http-${res.status}`);
    const data = await res.json();
    const items = data.output || [];
    const images = [];
    let revisedPrompt = '';
    for (const it of items) {
      if (it.type === 'image_generation_call') {
        if (it.result) images.push({ src: `data:image/png;base64,${it.result}`, prompt: opts.input || '', size: opts.size, type: 'b64' });
        if (it.revised_prompt) revisedPrompt = it.revised_prompt;
      }
    }
    return { responseId: data.id, images, revisedPrompt, raw: data };
  }

  /* ---- Variations ---- */
  async function variateImage(opts) {
    if (!isConfigured()) throw fail('OpenAI API key not set.', 'cv-openai/no-key');
    const { imageBlob, n, size, model } = opts || {};
    if (!imageBlob) throw fail('Source image required.', 'cv-openai/bad-input');

    // Variations endpoint historically only supports dall-e-2; honour caps.
    const requested = model || settings.imageModel;
    const caps = getModelCapabilities(requested);
    const finalModel = caps.supports.variation ? requested : 'dall-e-2';

    const form = new FormData();
    form.append('image', imageBlob, 'source.png');
    form.append('model', finalModel);
    form.append('n', String(n || 2));
    form.append('size', size || '1024x1024');

    let res;
    try {
      res = await fetch(endpoint('/v1/images/variations'), { method: 'POST', headers: authHeaders(), body: form });
    } catch (e) { throw fail('Could not reach OpenAI.', 'cv-openai/network'); }
    if (!res.ok) throw fail(await readError(res), `cv-openai/http-${res.status}`);
    const data = await res.json();
    return (data.data || []).map(d => normalizeImage(d, '(variation)', size || '1024x1024'));
  }

  function normalizeImage(d, prompt, size, format) {
    const fmt = format || 'png';
    if (d.url)       return { src: d.url, prompt, size, type: 'url',  format: fmt };
    if (d.b64_json)  return { src: `data:image/${fmt};base64,${d.b64_json}`, prompt, size, type: 'b64', format: fmt };
    return { src: '', prompt, size, type: 'unknown', format: fmt };
  }

  /* ---- Connection test (doesn't burn generation credits) ---- */
  async function testConnection() {
    if (!isConfigured()) throw fail('Add a key first.', 'cv-openai/no-key');
    try {
      const res = await fetch(endpoint('/v1/models'), { headers: authHeaders() });
      if (!res.ok) throw fail(await readError(res), `cv-openai/http-${res.status}`);
      const data = await res.json();
      // Refresh the cached model list at the same time — saves a round trip.
      const all = data.data || [];
      const imageOnly = all.map(m => m.id).filter(id => isLikelyImageModel(id));
      const seen = new Set(imageOnly);
      for (const id of Object.keys(MODEL_REGISTRY)) if (!seen.has(id)) imageOnly.push(id);
      saveCachedModels({
        fetchedAt: Date.now(), source: 'api',
        models: imageOnly.map(id => ({ id, ...getModelCapabilities(id) })),
        raw: all.length,
      });
      return { ok: true, modelCount: all.length, imageModelCount: imageOnly.length };
    } catch (e) {
      if (e.code) throw e;
      throw fail('Network error. Try adding a proxy URL in Settings.', 'cv-openai/network');
    }
  }

  async function urlToBlob(url) { const res = await fetch(url); return await res.blob(); }

  function classifyIntent(message) {
    const text = String(message || '').toLowerCase();
    if (!text) return { kind: 'text' };
    const verbs = /(generate|make|create|render|draw|design|paint|produce|show me|sketch|mock up|mock-up)/;
    const nouns = /(image|photo|picture|render|illustration|moodboard|hero|texture|background|wallpaper|portrait|render of|scene)/;
    const editVerbs = /(edit|retouch|replace|inpaint|change|brighten|add|remove|enhance|recolor|reframe)/;
    if (editVerbs.test(text) && nouns.test(text)) return { kind: 'image-edit' };
    if (verbs.test(text) && nouns.test(text)) return { kind: 'image-generate' };
    return { kind: 'text' };
  }

  // Seed cache from static registry so callers can render a list before fetch.
  if (!loadCachedModels()) {
    saveCachedModels({
      fetchedAt: 0, source: 'static',
      models: Object.entries(MODEL_REGISTRY).map(([id, caps]) => ({ id, ...caps })),
    });
  }

  window.cvOpenAI = {
    DEFAULTS: DEFAULT_SETTINGS,
    REGISTRY: MODEL_REGISTRY,
    getSettings: () => ({ ...settings }),
    updateSettings(patch) {
      settings = { ...settings, ...patch };
      saveSettings(settings);
      return { ...settings };
    },
    subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); },
    subscribeModels(fn) { modelListeners.add(fn); return () => modelListeners.delete(fn); },
    getCachedModels: loadCachedModels,
    listImageModels,
    getModelCapabilities,
    validateSize,
    isConfigured,
    classifyIntent,
    generateImage,
    editImage,
    responsesImage,
    variateImage,
    testConnection,
    urlToBlob,
  };
})();
