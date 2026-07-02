// atomicity/explore-engine.js
// ============================================================================
// CV_EXPLORE — divergent style exploration that converges into real components.
//
// Pick a restyleable element → Vi generates several distinct style DIRECTIONS at
// once → you like / dislike to steer → iterate (more-like-this, or go bolder /
// unrestricted) until one feels right → promote it: it becomes a registered
// Type in the architecture (staged through CV_HOST → types-seed.js, and live in
// CV_REGISTRY) and updates in place. Generation = f(element, intent, taste).
//
// Recipes are data (a small style spec); the markup lives in Explore.jsx and
// renders each recipe with styleFor(), so variants paint live and on-system.
// ============================================================================

(function () {
  'use strict';
  const AI = window.CV_AI;
  if (!AI) throw new Error('[CV_EXPLORE] CV_AI must load first');

  // restyleable elements — each a real fragment of the product surface
  const ELEMENTS = [
    { id: 'button', label: 'Button', content: 'Book inspection' },
    { id: 'card', label: 'Card', content: 'Eclipse Tower' },
    { id: 'price', label: 'Price tag', content: '$1.84m' },
    { id: 'badge', label: 'Badge', content: '360° tour' },
    { id: 'stat', label: 'Stat', content: '23.8k' },
  ];

  // the on-system palette offered to the model (it may also diverge if asked)
  const TOKENS = {
    colour: ['--accent-gold', '--accent-bronze', '--accent-tan', '--paper', '--paper-2', '--paper-3', '--bg-surface', '--bg-dark', '--ink', '--ink-2', '--accent-gold-soft', '--accent-gold-faint'],
    radius: ['--r-sm', '--r-md', '--r-lg', '--r-xl', '--r-pill'],
    shadow: ['--elev-1', '--elev-2', '--elev-3', '--elev-4', 'var(--elev-inset)', 'none'],
    font: ['--font-display', '--font-body', '--font-mono'],
  };

  function tok(v) { if (v == null || v === '') return undefined; v = String(v).trim(); if (v.startsWith('--')) return 'var(' + v + ')'; return v; }
  function styleFor(r) {
    r = r || {};
    return {
      background: tok(r.bg) || 'var(--bg-surface)',
      color: tok(r.fg) || 'var(--ink)',
      border: r.border ? ((r.borderWidth || '1px') + ' solid ' + tok(r.border)) : '1px solid transparent',
      borderRadius: tok(r.radius) || 'var(--r-md)',
      boxShadow: tok(r.shadow) || 'var(--elev-1)',
      fontWeight: r.weight || 600,
      fontFamily: tok(r.font) || 'var(--font-body)',
      letterSpacing: r.tracking || 'normal',
    };
  }

  function PROMPT({ element, intent, liked, disliked, n }) {
    const el = ELEMENTS.find(e => e.id === element) || ELEMENTS[0];
    const taste = (liked && liked.length) ? '\nLIKED directions (lean toward these): ' + JSON.stringify(liked) : '';
    const avoid = (disliked && disliked.length) ? '\nDISLIKED (avoid): ' + JSON.stringify(disliked) : '';
    return `You are Vi, a brand designer. Produce ${n} VISIBLY DIFFERENT style directions for a "${el.label}" in the ConceptV system (warm paper + gold + bronze, Sora/DM Sans). Make them genuinely distinct — e.g. minimal, bold, soft, architectural, dark, editorial, playful — not minor tweaks.${intent ? '\nIntent from the user: ' + intent : ''}${taste}${avoid}

Prefer these tokens (use the names, or var(--x)); you may also use raw values when a direction calls for it:
colours ${TOKENS.colour.join(', ')}; radius ${TOKENS.radius.join(', ')}; shadow ${TOKENS.shadow.join(', ')}; font ${TOKENS.font.join(', ')}.

Each recipe (keep terse): {"name":"<2-3 word direction>","bg","fg","border","borderWidth","radius","shadow","weight","font","tracking","note":"<≤10 words why>"}. Plain JSON only:
{"variants":[ … ${n} … ]}`;
  }

  function salvageVariants(raw) {
    let body = String(raw || '');
    const fence = body.match(/```(?:json)?\s*([\s\S]*?)(?:```|$)/); if (fence) body = fence[1];
    try { const j = JSON.parse(body); if (j && j.variants) return j.variants; } catch {}
    const out = []; const fi = body.indexOf('"variants"'); if (fi < 0) return out;
    const arr = body.slice(body.indexOf('[', fi));
    let depth = 0, start = -1, inStr = false, esc = false;
    for (let k = 0; k < arr.length; k++) {
      const ch = arr[k];
      if (inStr) { if (esc) esc = false; else if (ch === '\\') esc = true; else if (ch === '"') inStr = false; continue; }
      if (ch === '"') inStr = true;
      else if (ch === '{') { if (depth === 0) start = k; depth++; }
      else if (ch === '}') { depth--; if (depth === 0 && start >= 0) { try { out.push(JSON.parse(arr.slice(start, k + 1))); } catch {} start = -1; } }
    }
    return out;
  }

  async function variations(opts) {
    const n = opts.n || 4;
    const prompt = PROMPT({ element: opts.element, intent: opts.intent, liked: opts.liked, disliked: opts.disliked, n });
    let raw; try { raw = await AI.complete({ messages: [{ role: 'user', content: prompt }], max_tokens: 1600 }); } catch (e) { raw = await AI.complete(prompt); }
    const v = salvageVariants(raw).slice(0, n);
    return v.map((r, i) => ({ ...r, id: 'v_' + Date.now().toString(36) + i }));
  }

  // promote a chosen recipe → a registered atom Type (architecture + live)
  function promote({ element, recipe, name }) {
    const slug = (name || recipe.name || element).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    const id = 'atom.' + element + '.' + slug;
    const payload = {
      id, name: name || recipe.name || (element + ' style'), layer: 'atom', role: element,
      style: styleFor(recipe), recipe: { bg: recipe.bg, fg: recipe.fg, border: recipe.border, radius: recipe.radius, shadow: recipe.shadow, weight: recipe.weight, font: recipe.font },
      provenance: 'explored', note: recipe.note || '',
    };
    let staged = null;
    try { staged = window.CV_HOST.commit({ kind: 'type', title: 'Add ' + payload.name + ' (' + element + ')', rationale: 'Promoted from Explore — a ' + element + ' style direction.', payload, provenance: 'you' }); } catch (e) { window.dsaToast?.(e.message); }
    try { window.CV_REGISTRY && window.CV_REGISTRY.register && window.CV_REGISTRY.register(payload); } catch {}
    remember(payload);
    return { id, staged, payload };
  }

  // ---- persisted gallery of promoted atoms (survives reload) --------------
  const LS_GAL = 'atomicity:explored';
  const galListeners = new Set();
  function gallery() { try { return JSON.parse(localStorage.getItem(LS_GAL) || '[]'); } catch { return []; } }
  function remember(payload) {
    const g = gallery().filter(x => x.id !== payload.id);
    g.unshift({ id: payload.id, name: payload.name, role: payload.role, recipe: payload.recipe, note: payload.note, at: Date.now() });
    try { localStorage.setItem(LS_GAL, JSON.stringify(g.slice(0, 60))); } catch {}
    for (const fn of galListeners) { try { fn(); } catch {} }
  }
  function forget(id) { try { localStorage.setItem(LS_GAL, JSON.stringify(gallery().filter(x => x.id !== id))); } catch {} for (const fn of galListeners) { try { fn(); } catch {} } }
  function onGallery(fn) { galListeners.add(fn); return () => galListeners.delete(fn); }

  // ---- Vi-driven explore: generate, optionally auto-promote the best ------
  async function exploreFor({ element, intent, promoteBest }) {
    const el = (ELEMENTS.find(e => e.id === element) || ELEMENTS[0]).id;
    const v = await variations({ element: el, intent, n: 4 });
    if (promoteBest && v.length) { const r = promote({ element: el, recipe: v[0], name: v[0].name }); return { variants: v, promoted: r }; }
    return { variants: v };
  }

  AI.register({ id: 'explore.variations', name: 'Explore style options', layer: 'capability', family: 'explore',
    description: 'Generate several distinct style directions for an element, steered by likes/dislikes.',
    surfaces: ['explore'], role: 'text', behaviours: ['voice.conceptv'], icon: 'shuffle', provenance: 'built-in',
    run: a => variations(a.params || {}) }, { silent: true });
  AI.register({ id: 'explore.promote', name: 'Promote to component', layer: 'capability', family: 'explore',
    description: 'Turn a chosen style direction into a registered Type in the architecture, staged via CV_HOST.',
    surfaces: ['explore'], provider: 'host-fs', icon: 'plus-square', provenance: 'built-in',
    run: a => promote(a.params || {}) }, { silent: true });
  AI.register({ id: 'explore.run', name: 'Explore an element for me', layer: 'capability', family: 'explore',
    description: 'Generate style directions for an element and (optionally) promote the strongest into the system — Vi-driven, end to end.',
    surfaces: ['explore', 'atomicity'], role: 'text', behaviours: ['voice.conceptv'], icon: 'shuffle', provenance: 'built-in',
    run: a => exploreFor(a.params || {}) }, { silent: true });

  // taste profile — distil the liked set into human words, locally + instantly,
  // so steering feels visible and the next batch can lean in. No model needed.
  function tasteProfile(liked) {
    if (!liked || !liked.length) return { tags: [], summary: 'No direction yet — like a few to steer.' };
    const warm = s => /gold|bronze|tan|warm/.test(String(s || ''));
    const dark = s => /dark|ink/.test(String(s || ''));
    let fills = 0, outlines = 0, warmth = 0, roundSum = 0, depth = 0, darkN = 0;
    const rMap = { '--r-sm': 1, '--r-md': 2, '--r-lg': 3, '--r-xl': 4, '--r-pill': 5 };
    const eMap = { 'none': 0, '--elev-1': 1, '--elev-2': 2, '--elev-3': 3, '--elev-4': 4 };
    for (const r of liked) {
      const bg = String(r.bg || '');
      if (!bg || bg === 'transparent') outlines++; else fills++;
      if (warm(bg) || warm(r.fg) || warm(r.border)) warmth++;
      if (dark(bg)) darkN++;
      roundSum += rMap[r.radius] || 2.5;
      depth += eMap[r.shadow] != null ? eMap[r.shadow] : 1.5;
    }
    const n = liked.length, tags = [];
    if (fills >= outlines && fills) tags.push('solid fills'); else if (outlines) tags.push('outlined');
    if (warmth / n > 0.5) tags.push('warm'); if (darkN / n > 0.4) tags.push('dark');
    const r = roundSum / n; tags.push(r > 3.5 ? 'very rounded' : r > 2.2 ? 'rounded' : 'sharp');
    const d = depth / n; tags.push(d > 2.5 ? 'floating' : d > 1.2 ? 'lifted' : 'flat');
    return { tags, summary: 'Leaning ' + tags.join(' · ') + '.', strength: Math.min(1, n / 4) };
  }

  window.CV_EXPLORE = { ELEMENTS, TOKENS, styleFor, variations, promote, tasteProfile, gallery, remember, forget, onGallery, exploreFor };
  console.info('[CV_EXPLORE] exploration engine ready');
})();
