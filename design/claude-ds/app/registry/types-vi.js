// app/registry/types-vi.js
// Vi helpers — propose Type schemas from a brief, suggest slots, suggest
// defaults, and promote existing instances into reusable Types.

(function () {
  const R = window.CV_REGISTRY;
  if (!R) return;

  const LAYERS_DOC = `
Layers (atomic composition, low → high):
- token:    design primitive (colour/type/spacing/shape)
- atom:     single visual unit (icon, status dot, stamp)
- block:    composable content unit (KPI tile, sparkline, hero, callout)
- system:   composition rule over blocks (kpi-set, media-led, hybrid)
- surface:  framed container with context (dashboard tile, hub panel, wizard step, slide layout)
- doc:      top-level document Type (deck, brochure, widget, wizard)
- template: doc bound with extracted variables`;

  function parseJsonLoose(reply) {
    if (typeof reply !== 'string') return null;
    try { return JSON.parse(reply); } catch {}
    const m = reply.match(/\{[\s\S]*\}/);
    if (m) { try { return JSON.parse(m[0]); } catch {} }
    return null;
  }

  function kebab(s) {
    return String(s || '').toLowerCase().trim()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '') || 'type-' + Math.random().toString(36).slice(2, 6);
  }

  function uniqueId(layer, family, name) {
    let id = layer + '.' + (family ? family + '.' : '') + kebab(name);
    if (!R.get(id)) return id;
    let n = 2;
    while (R.get(id + '-' + n)) n++;
    return id + '-' + n;
  }

  // ===========================================================================
  // proposeType — given a brief and an optional parent, returns a draft Type.
  // ===========================================================================
  async function proposeType({ brief, parentId = null, layerHint = null, familyHint = null }) {
    const parent = parentId ? R.resolve(parentId) : null;
    const parentDoc = parent
      ? `\nThe new Type EXTENDS this parent:
- id: ${parent.id}
- name: ${parent.name}
- layer: ${parent.layer}
- family: ${parent.family}
- description: ${parent.description}
- slots: ${JSON.stringify(parent.slots || {})}
- defaults: ${JSON.stringify(parent.defaults || {}).slice(0, 400)}
- tags: ${(parent.tags || []).join(', ')}

Inherit everything; only override what needs to change.`
      : '';

    // Compact catalogue of registered Types Vi can REFER to in slot.accepts
    const cat = R.all().filter(t => !t.id.startsWith('template.')).slice(0, 80);
    const catDoc = cat.map(t => `- ${t.id} (${t.layer}/${t.family}): ${t.name}`).join('\n');

    const prompt = `You are Vi, designing a new Type in ConceptV Studio's universal Type Registry.
${LAYERS_DOC}

Brand voice: sentence case, second-person, no exclamation marks, no emoji. Concrete names. ConceptV vocabulary: User Portal, Property Wizard, Virtual Hub, Capture, Vi.

User brief: "${brief}"

${layerHint ? `LAYER (locked): ${layerHint}` : 'Pick the layer that fits.'}
${familyHint ? `FAMILY (locked): ${familyHint}` : 'Pick a sensible family (e.g. widget, wizard-step, block, system).'}
${parentDoc}

Existing Types you may reference in slot.accepts (use layers + families filters):
${catDoc}

Return ONLY JSON — no prose, no markdown fences:
{
  "name": "Title-Case display name (2-5 words)",
  "layer": "<one of layers>",
  "family": "<lowercase family>",
  "description": "one-sentence summary in brand voice",
  "tags": ["3-6 lowercase tags"],
  "extends": ${parentId ? `"${parentId}"` : 'null'},
  "slots": {
    "slotName": {
      "label": "Display label",
      "accepts": { "layers": ["block"], "families": ["widget"], "tags": ["data"] },
      "multiple": true | false,
      "optional": true | false,
      "default": <count if multiple, default value otherwise, optional>
    }
  },
  "defaults": {
    "// any default data the consumer of this Type expects": "..."
  },
  "variables": [
    {"key":"snake_case","label":"Human label","default":"current value","kind":"text|number|url|choice","options":["only for choice"]}
  ],
  "icon": "<icon name from CV icon library — pick something representative>"
}

Notes:
- Slots define WHAT can be embedded in this Type. Most layer:'system' Types have one or two slots accepting layer:'block'.
- Variables are values that change between runs (Templates pull from this list). Only include 2-5 meaningful ones.
- Choose a family that already exists when possible (widget, wizard-step, block, system, deck-slide, brochure-section). Invent a new family only if none fit.`;

    const reply = await window.CV_AI.execute('type.propose', { params: { prompt }, surface: 'registry' });
    const parsed = parseJsonLoose(reply);
    if (!parsed?.name || !parsed?.layer) throw new Error('Vi returned no parsable Type');

    const layer = layerHint || parsed.layer;
    const family = familyHint || parsed.family || 'general';
    return {
      id: uniqueId(layer, family, parsed.name),
      name: parsed.name,
      layer,
      family,
      description: parsed.description || '',
      tags: Array.isArray(parsed.tags) ? parsed.tags : [],
      extends: parsed.extends || parentId || null,
      slots: parsed.slots && typeof parsed.slots === 'object' ? parsed.slots : {},
      defaults: parsed.defaults && typeof parsed.defaults === 'object' ? parsed.defaults : {},
      variables: Array.isArray(parsed.variables) ? parsed.variables : [],
      icon: parsed.icon || 'check-square',
      provenance: 'vi',
    };
  }

  // ===========================================================================
  // promoteInstance — turn an existing doc/widget/wizard instance into a Type.
  // The Type extracts variables; the original instance becomes the canonical
  // sample data, stored in defaults.
  // ===========================================================================
  async function promoteInstance({ instance, intoLayer = 'doc', intoFamily = null }) {
    const family = intoFamily || instance.type || 'general';
    const slim = JSON.parse(JSON.stringify(instance));
    delete slim.id; delete slim.createdAt;

    const prompt = `You are Vi, promoting an existing ConceptV ${family} instance into a reusable TYPE in the registry.
${LAYERS_DOC}

Instance JSON:
${JSON.stringify(slim).slice(0, 6000)}

Convert this into a Type at LAYER="${intoLayer}", FAMILY="${family}".
- Pick a short Type name (2-5 words) that captures the pattern, not the specific instance.
- Write a one-sentence description.
- Identify 2-5 VARIABLES — values that would change between runs (proper nouns, big numbers, audience labels, dates, URLs). Skip structural strings and recurring brand terms (ConceptV, Vi, Virtual Hub).
- Suggest 3-6 tags.

Return ONLY JSON:
{
  "name": "...",
  "description": "...",
  "tags": ["..."],
  "icon": "icon name",
  "variables": [{"key":"property_name","label":"Property name","default":"Tower East","kind":"text"}]
}`;

    const reply = await window.CV_AI.execute('type.materialize', { params: { prompt }, surface: 'registry' });
    const parsed = parseJsonLoose(reply) || {};
    return {
      id: uniqueId(intoLayer, family, parsed.name || (instance.title || 'New type')),
      name: parsed.name || instance.title || 'New type',
      layer: intoLayer,
      family,
      description: parsed.description || '',
      tags: Array.isArray(parsed.tags) ? parsed.tags : [family],
      icon: parsed.icon || 'check-square',
      provenance: 'vi',
      defaults: slim,
      variables: Array.isArray(parsed.variables) ? parsed.variables : [],
    };
  }

  // ===========================================================================
  // suggestSlots — given an existing Type, propose additional useful slots.
  // ===========================================================================
  async function suggestSlots(typeId) {
    const t = R.resolve(typeId);
    if (!t) return [];
    const prompt = `You are Vi, suggesting additional SLOTS for a ConceptV Type.
${LAYERS_DOC}

Current Type:
- name: ${t.name}
- layer: ${t.layer}
- family: ${t.family}
- description: ${t.description}
- existing slots: ${JSON.stringify(t.slots || {})}

Suggest 2-4 NEW slots that would make this Type more useful. Each slot is named, has a label, and accepts a filtered subset of registered Types (by layer + family + tags).

Return ONLY JSON:
{"slots":[{"name":"camelCase","label":"...","accepts":{"layers":[],"families":[],"tags":[]},"multiple":bool,"optional":bool,"rationale":"why this slot helps"}]}`;
    try {
      const reply = await window.CV_AI.execute('type.suggest-slots', { params: { prompt }, surface: 'registry' });
      const parsed = parseJsonLoose(reply);
      return Array.isArray(parsed?.slots) ? parsed.slots : [];
    } catch { return []; }
  }

  window.CV_TYPES_VI = { proposeType, promoteInstance, suggestSlots };
})();
