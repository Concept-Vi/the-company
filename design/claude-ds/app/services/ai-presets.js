// services/ai-presets.js — store for AI Studio presets & pipelines.
//
// Two collections:
//   • presets   — named, reusable parameter blobs ("Warm interior render",
//                 "Bronze line illustration", "Drone exterior"). Each preset
//                 captures the full GenerateOptions: prompt, model, size,
//                 quality, format, compression, background, moderation, n.
//   • pipelines — ordered sequences of steps that operate on an image to
//                 produce an enriched output. Each step has a kind:
//                   - generate: kicks off with a prompt
//                   - edit:     edits the previous step's image with a prompt
//                   - mask:     masked edit using a stored mask region
//                   - filter:   pipes through the local ImageEditor adjustment
//
// Both live in localStorage and are observable. UI subscribes and rerenders.

(function () {
  const NS = 'cvstudio:cvAIPresets:v1';

  // Seeds — give users immediately useful presets out of the box.
  const SEED = {
    presets: [
      {
        id: 'p_warm_interior',
        name: 'Warm interior render',
        icon: 'browser-house',
        body: 'Photoreal interior render of a modern Australian living room. Warm afternoon light through sheer curtains, timber floors, stone bench. Soft palette of cream, gold and ink. 35mm cinematic.',
        model: 'gpt-image-2', size: '1536x1024', quality: 'high', output_format: 'png', background: 'auto', moderation: 'auto', n: 1,
      },
      {
        id: 'p_drone_exterior',
        name: 'Drone exterior — golden hour',
        icon: 'drone',
        body: 'Drone view of a contemporary residential development at golden hour. Glass façade, native landscaping, warm sandstone and brushed gold detailing.',
        model: 'gpt-image-2', size: '2048x1152', quality: 'high', output_format: 'jpeg', output_compression: 92, background: 'auto', moderation: 'auto', n: 1,
      },
      {
        id: 'p_bronze_line',
        name: 'Bronze line illustration',
        icon: 'blueprint',
        body: 'Single-stroke bronze line illustration of an architectural section drawing. Warm ivory paper background. 1.5 px stroke, rounded caps, no fills.',
        model: 'gpt-image-2', size: '1024x1024', quality: 'medium', output_format: 'png', background: 'opaque', moderation: 'auto', n: 1,
      },
      {
        id: 'p_stone_texture',
        name: 'Macro stone texture',
        icon: 'image',
        body: 'Macro photograph of warm beige Australian sandstone with subtle gold veining. Soft directional sunlight. High-resolution texture.',
        model: 'gpt-image-2', size: '2048x2048', quality: 'high', output_format: 'jpeg', output_compression: 88, background: 'auto', moderation: 'auto', n: 1,
      },
      {
        id: 'p_stakeholder_portrait',
        name: 'Stakeholder portrait',
        icon: 'person',
        body: 'Editorial portrait of an Australian developer in a sunlit display suite. Warm tones, natural light, shallow depth of field.',
        model: 'gpt-image-2', size: '1024x1536', quality: 'high', output_format: 'png', background: 'auto', moderation: 'auto', n: 1,
      },
      {
        id: 'p_moodboard',
        name: 'Moodboard tile',
        icon: 'image-stack',
        body: 'Editorial moodboard tile: weathered limestone, brushed gold detailing, soft directional sun, cinematic 35mm grain. Subtle film texture.',
        model: 'gpt-image-2', size: '1024x1024', quality: 'medium', output_format: 'jpeg', output_compression: 90, background: 'auto', moderation: 'auto', n: 4,
      },
    ],
    pipelines: [
      {
        id: 'pl_hero_pack',
        name: 'Hero + close-up pack',
        desc: 'Generates a hero render and a close-up detail edit, then promotes both to the system library.',
        steps: [
          { kind: 'generate', presetId: 'p_warm_interior', label: 'Hero render' },
          { kind: 'edit',     prompt: 'Reframe as a close-up detail of the timber and stone, shallow depth of field.', label: 'Detail' },
          { kind: 'adopt',    to: 'system', tags: ['Brand hero'], label: 'Adopt both into system' },
        ],
      },
      {
        id: 'pl_listing_kit',
        name: 'Project listing kit',
        desc: 'Hero, drone exterior, and 4 moodboard tiles — all tagged to the active project.',
        steps: [
          { kind: 'generate', presetId: 'p_warm_interior',    label: 'Interior hero' },
          { kind: 'generate', presetId: 'p_drone_exterior',   label: 'Drone exterior' },
          { kind: 'generate', presetId: 'p_moodboard',        label: 'Moodboard ×4' },
          { kind: 'adopt',    to: 'project',                  label: 'Adopt all into project' },
        ],
      },
    ],
  };

  function load() {
    try {
      const raw = localStorage.getItem(NS);
      if (!raw) return JSON.parse(JSON.stringify(SEED));
      const parsed = JSON.parse(raw);
      return {
        presets:   parsed.presets   || SEED.presets,
        pipelines: parsed.pipelines || SEED.pipelines,
      };
    } catch { return JSON.parse(JSON.stringify(SEED)); }
  }
  function persist(data) {
    try { localStorage.setItem(NS, JSON.stringify(data)); } catch {}
    listeners.forEach(fn => { try { fn(data); } catch {} });
  }

  let data = load();
  const listeners = new Set();
  function uid(p) { return p + '_' + Math.random().toString(36).slice(2, 9); }

  const api = {
    snapshot() { return JSON.parse(JSON.stringify(data)); },
    subscribe(fn) { listeners.add(fn); return () => listeners.delete(fn); },

    listPresets()   { return [...data.presets]; },
    listPipelines() { return [...data.pipelines]; },

    addPreset(p) {
      const rec = { id: uid('p'), createdAt: Date.now(), ...p };
      data.presets = [rec, ...data.presets];
      persist(data); return rec;
    },
    updatePreset(id, patch) {
      data.presets = data.presets.map(p => p.id === id ? { ...p, ...patch } : p);
      persist(data);
    },
    removePreset(id) {
      data.presets = data.presets.filter(p => p.id !== id);
      persist(data);
    },

    addPipeline(p) {
      const rec = { id: uid('pl'), createdAt: Date.now(), ...p };
      data.pipelines = [rec, ...data.pipelines];
      persist(data); return rec;
    },
    updatePipeline(id, patch) {
      data.pipelines = data.pipelines.map(p => p.id === id ? { ...p, ...patch } : p);
      persist(data);
    },
    removePipeline(id) {
      data.pipelines = data.pipelines.filter(p => p.id !== id);
      persist(data);
    },

    findPreset(id) { return data.presets.find(p => p.id === id); },

    // Resolve a preset to a GenerateOptions object suitable for cvOpenAI.generateImage
    materialize(preset) {
      if (!preset) return null;
      return {
        prompt: preset.body,
        model: preset.model,
        size: preset.size,
        quality: preset.quality,
        output_format: preset.output_format,
        output_compression: preset.output_compression,
        background: preset.background,
        moderation: preset.moderation,
        n: preset.n,
      };
    },
  };

  window.cvAIPresets = api;
})();
