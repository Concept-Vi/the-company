// canvases/workshop/AIEngine.jsx — Workshop generation engine + UI primitives
//
// Centralises everything Vi can DO inside Workshop:
//   - Generate candidate diffs (block insert, block alternate, page insert,
//     doc-wide transforms, widget/wizard step alternates, …)
//   - Apply diffs to docs (pure functions)
//   - Render candidate galleries + diff cards + suggestion lists
//   - A "chat bridge" any chat rail can use to act on the current doc
//
// All builders (deck/brochure/widget/wizard + future) talk to one engine.
//
// Diff schema (every diff is an immutable plain object):
//   { kind: 'block.insert',  pageIdx, atIdx, section }
//   { kind: 'block.replace', pageIdx, secIdx, section }
//   { kind: 'block.update',  pageIdx, secIdx, dataPatch }
//   { kind: 'block.remove',  pageIdx, secIdx }
//   { kind: 'page.insert',   atIdx, page }
//   { kind: 'page.update',   pageIdx, patch }
//   { kind: 'doc.update',    patch }
//   { kind: 'widget.update', patch }                 // top-level widget fields
//   { kind: 'widget.data',   dataPatch }             // data.* fields
//   { kind: 'wizard.step.insert', atIdx, step }
//   { kind: 'wizard.step.update', stepIdx, patch }
//   { kind: 'wizard.step.remove', stepIdx }
//   { kind: 'batch', diffs: [...] }
//
// Candidate schema:
//   { id, label, summary?, diff }
//
// Target schema (what generation operates on):
//   { kind: 'insert.block', pageIdx, atIdx, hint?, neighborhood }
//   { kind: 'alternate.block', pageIdx, secIdx, section }
//   { kind: 'insert.page', atIdx, neighborhood }
//   { kind: 'doc.transform', instruction }
//   { kind: 'widget.alternate', doc }
//   { kind: 'widget.kpis.regen', doc, count? }
//   { kind: 'wizard.step.insert', atIdx }
//   { kind: 'wizard.step.alternate', stepIdx }

const { useState: useState_ai, useEffect: useEffect_ai, useMemo: useMemo_ai, useRef: useRef_ai } = React;

// ============================================================
// Diff system — pure transforms
// ============================================================

function clone(o) { return o == null ? o : JSON.parse(JSON.stringify(o)); }

function applyDiff(doc, diff) {
  if (!diff || !doc) return doc;
  if (diff.kind === 'batch') {
    return (diff.diffs || []).reduce((d, sub) => applyDiff(d, sub), doc);
  }
  const next = clone(doc);
  switch (diff.kind) {
    case 'block.insert': {
      const p = next.pages[diff.pageIdx];
      if (!p) break;
      const sec = ensureSection(diff.section);
      const at = Math.max(0, Math.min(diff.atIdx, (p.sections || []).length));
      p.sections = [...(p.sections || [])];
      p.sections.splice(at, 0, sec);
      break;
    }
    case 'block.replace': {
      const p = next.pages[diff.pageIdx];
      if (!p || !p.sections?.[diff.secIdx]) break;
      const id = p.sections[diff.secIdx].id;
      p.sections[diff.secIdx] = ensureSection({ ...diff.section, id });
      break;
    }
    case 'block.update': {
      const p = next.pages[diff.pageIdx];
      if (!p || !p.sections?.[diff.secIdx]) break;
      const cur = p.sections[diff.secIdx];
      p.sections[diff.secIdx] = { ...cur, data: { ...cur.data, ...(diff.dataPatch || {}) } };
      break;
    }
    case 'block.remove': {
      const p = next.pages[diff.pageIdx];
      if (!p) break;
      p.sections = (p.sections || []).filter((_, i) => i !== diff.secIdx);
      break;
    }
    case 'page.insert': {
      const at = Math.max(0, Math.min(diff.atIdx, next.pages.length));
      const newPage = { id: 'p-' + Date.now() + '-' + Math.random().toString(36).slice(2, 6), title: diff.page?.title || 'New page', kind: diff.page?.kind || 'content', sections: [], ...diff.page };
      newPage.sections = (newPage.sections || []).map(ensureSection);
      next.pages.splice(at, 0, newPage);
      break;
    }
    case 'page.update': {
      const p = next.pages[diff.pageIdx];
      if (!p) break;
      Object.assign(p, diff.patch || {});
      break;
    }
    case 'doc.update': {
      Object.assign(next, diff.patch || {});
      break;
    }
    case 'widget.update': {
      Object.assign(next, diff.patch || {});
      break;
    }
    case 'widget.data': {
      next.data = { ...(next.data || {}), ...(diff.dataPatch || {}) };
      break;
    }
    case 'wizard.step.insert': {
      const at = Math.max(0, Math.min(diff.atIdx, (next.steps || []).length));
      const step = { id: 'wz-' + Date.now() + '-' + Math.random().toString(36).slice(2, 5), ...(diff.step || {}) };
      next.steps = [...(next.steps || [])];
      next.steps.splice(at, 0, step);
      break;
    }
    case 'wizard.step.update': {
      if (!next.steps?.[diff.stepIdx]) break;
      next.steps[diff.stepIdx] = { ...next.steps[diff.stepIdx], ...(diff.patch || {}) };
      break;
    }
    case 'wizard.step.remove': {
      next.steps = (next.steps || []).filter((_, i) => i !== diff.stepIdx);
      break;
    }
    default:
      console.warn('[AIEngine] unknown diff', diff.kind);
  }
  return next;
}

function ensureSection(sec) {
  if (!sec || !sec.kind) return sec;
  const def = window.WS_BLOCKS?.[sec.kind];
  return {
    id: sec.id || ('sec-' + Date.now() + '-' + Math.random().toString(36).slice(2, 6)),
    kind: sec.kind,
    data: { ...(def?.defaults || {}), ...(sec.data || {}) },
    locked: sec.locked || false,
  };
}

function describeDiff(diff, doc) {
  if (!diff) return '';
  if (diff.kind === 'batch') {
    if (!diff.diffs?.length) return 'No changes';
    return `${diff.diffs.length} change${diff.diffs.length === 1 ? '' : 's'} (${diff.diffs.map(d => describeDiff(d, doc)).slice(0, 3).join('; ')}${diff.diffs.length > 3 ? ', …' : ''})`;
  }
  switch (diff.kind) {
    case 'block.insert':  return `Insert a ${labelForBlock(diff.section?.kind)} block`;
    case 'block.replace': return `Replace block ${diff.secIdx + 1} with a ${labelForBlock(diff.section?.kind)}`;
    case 'block.update':  return `Update block ${diff.secIdx + 1}: ${Object.keys(diff.dataPatch || {}).join(', ')}`;
    case 'block.remove':  return `Remove block ${diff.secIdx + 1}`;
    case 'page.insert':   return `Add page "${diff.page?.title || ''}" at ${diff.atIdx + 1}`;
    case 'page.update':   return `Update page ${diff.pageIdx + 1}: ${Object.keys(diff.patch || {}).join(', ')}`;
    case 'doc.update':    return `Update doc: ${Object.keys(diff.patch || {}).join(', ')}`;
    case 'widget.update': return `Update widget: ${Object.keys(diff.patch || {}).join(', ')}`;
    case 'widget.data':   return `Update widget data: ${Object.keys(diff.dataPatch || {}).join(', ')}`;
    case 'wizard.step.insert': return `Insert step "${diff.step?.title || ''}" at ${diff.atIdx + 1}`;
    case 'wizard.step.update': return `Update step ${diff.stepIdx + 1}: ${Object.keys(diff.patch || {}).join(', ')}`;
    case 'wizard.step.remove': return `Remove step ${diff.stepIdx + 1}`;
  }
  return diff.kind;
}

function labelForBlock(kind) {
  return window.WS_BLOCKS?.[kind]?.label || kind;
}

// ============================================================
// Generation
// ============================================================

// Voice is single-sourced from the AI registry's behaviour entry (CV_AI is the
// one catalogue; this string no longer lives in two places). Loud if missing.
const BRAND_VOICE = (() => {
  if (!window.CV_AI) throw new Error('[AIEngine] CV_AI registry not loaded — load app/ai/ai-registry.js + ai-seed.js before AIEngine');
  const v = window.CV_AI.get('voice.conceptv');
  if (!v) throw new Error('[AIEngine] voice.conceptv behaviour not registered (app/ai/ai-seed.js)');
  return typeof v.text === 'function' ? v.text({}) : v.text;
})();

// One completion helper: route through a resolved CV_AI provider when one is
// supplied (the unified path); otherwise the default Claude endpoint. `cache`
// preserves the 60s prompt cache for idempotent calls (theme/field/suggest).
async function aiComplete(prompt, provider, cache) {
  // Every completion routes through a CV_AI-resolved provider — there is no raw
  // endpoint path. Loud if the registry or the provider's runtime is absent.
  const p = provider || (window.CV_AI ? window.CV_AI.resolveProvider('claude') : null);
  if (!p) throw new Error('[AIEngine] no provider available — CV_AI registry not loaded (app/ai/ai-registry.js)');
  if (cache) {
    const hit = PROMPT_CACHE.get(prompt);
    if (hit !== null) return hit;
    const out = await p.complete(prompt);
    PROMPT_CACHE.set(prompt, out);
    return out;
  }
  return p.complete(prompt);
}

function parseJsonLoose(reply) {
  if (typeof reply !== 'string') return null;
  try { return JSON.parse(reply); } catch {}
  const m = reply.match(/\{[\s\S]*\}/);
  if (m) { try { return JSON.parse(m[0]); } catch {} }
  return null;
}

const AVAILABLE_BLOCK_KINDS = () => Object.keys(window.WS_BLOCKS || {}).filter(k => k !== 'divider');

function blockShapeDoc() {
  // Compact description of every block's expected data shape — enough for Vi
  return AVAILABLE_BLOCK_KINDS().map(k => {
    const def = window.WS_BLOCKS[k];
    const keys = Object.keys(def.defaults || {});
    return `  - ${k}: ${def.label} — fields: ${keys.join(', ') || '(no data)'}`;
  }).join('\n');
}

function pageContextSummary(doc, pageIdx) {
  if (!doc?.pages?.length) return 'Empty doc.';
  const around = (i) => {
    const p = doc.pages[i];
    if (!p) return null;
    return `[page ${i + 1} · ${p.title || p.kind}] ` + (p.sections || []).map(s => `${s.kind}(${JSON.stringify(s.data).slice(0, 80)})`).join(' | ');
  };
  const lines = [];
  for (let i = Math.max(0, pageIdx - 1); i <= Math.min(doc.pages.length - 1, pageIdx + 1); i++) {
    const ln = around(i);
    if (ln) lines.push((i === pageIdx ? '▶ ' : '  ') + ln);
  }
  return lines.join('\n');
}

async function generateCandidates({ doc, target, count = 3, brief = '' } = {}) {
  if (!doc || !target) return [];
  // Unified dispatch: every generative move is a registered CV_AI capability,
  // resolved + run through the one engine (provider + context + behaviours).
  // No per-target switch lives here anymore — the catalogue IS the dispatch.
  if (!window.CV_AI) throw new Error('[AIEngine] CV_AI registry not loaded');
  if (!window.CV_AI.get(target.kind)) {
    throw new Error('[AIEngine] no CV_AI capability for target "' + target.kind + '" — register it in the AI capability catalogue');
  }
  return await window.CV_AI.execute(target.kind, { doc, target, params: { count }, brief, surface: doc.type });
}

function rid() { return Math.random().toString(36).slice(2, 10); }

// ---- Block insert ----
async function viInsertBlock(doc, target, count, brief, provider) {
  const docType = doc.type;
  const ctx = pageContextSummary(doc, target.pageIdx);
  const prompt = `You are Vi, choosing what block to insert into a ConceptV ${docType === 'deck' ? 'slide deck' : 'brochure'}.

${BRAND_VOICE}

Document title: "${doc.title}"
${ctx ? 'Context (nearby pages):\n' + ctx : ''}
Inserting at position ${target.atIdx + 1} of page ${target.pageIdx + 1}.
${brief ? `User hint: "${brief}"` : ''}

Available block kinds:
${blockShapeDoc()}

Propose ${count} alternative blocks that would fit best here. Be DIFFERENT from each other — different kinds where it makes sense. Tailor the data to the surrounding context.

Respond ONLY as JSON (no prose):
{"candidates":[{"label":"3-5 word summary","kind":"<block kind>","data":{...}}, ...]}`;
  const reply = await aiComplete(prompt, typeof provider !== "undefined" ? provider : null);
  const parsed = parseJsonLoose(reply);
  if (!parsed?.candidates) return [];
  return parsed.candidates.slice(0, count).map(c => {
    if (!c.kind || !window.WS_BLOCKS[c.kind]) return null;
    const section = ensureSection({ kind: c.kind, data: c.data || {} });
    return {
      id: rid(),
      label: c.label || labelForBlock(c.kind),
      summary: `${labelForBlock(c.kind)} block`,
      diff: { kind: 'block.insert', pageIdx: target.pageIdx, atIdx: target.atIdx, section },
    };
  }).filter(Boolean);
}

// ---- Block alternate (replace existing block with a variation) ----
async function viAlternateBlock(doc, target, count, brief, provider) {
  const page = doc.pages[target.pageIdx];
  const sec = page?.sections?.[target.secIdx];
  if (!sec) return [];
  const def = window.WS_BLOCKS[sec.kind];
  const otherSections = (page.sections || []).filter((_, i) => i !== target.secIdx);
  const ctxOther = otherSections.map(s => `${s.kind}: ${JSON.stringify(s.data).slice(0, 100)}`).join('\n');

  const prompt = `You are Vi, generating ${count} alternative versions of a ${def.label} block in a ConceptV ${doc.type}.

${BRAND_VOICE}

Document title: "${doc.title}"
Same page also contains:
${ctxOther || '(no other blocks on this page)'}

Current block (kind: ${sec.kind}):
${JSON.stringify(sec.data, null, 2)}

${brief ? `User hint: "${brief}"` : ''}

Generate ${count} DIFFERENT alternatives. Different angles, different copy, but the same JSON shape as the current block. Each should be cohesive — not just minor word swaps. Keep field names identical to the current block.

Respond ONLY as JSON (no prose):
{"candidates":[{"label":"3-5 word summary","data":{...}}, ...]}`;
  const reply = await aiComplete(prompt, typeof provider !== "undefined" ? provider : null);
  const parsed = parseJsonLoose(reply);
  if (!parsed?.candidates) return [];
  return parsed.candidates.slice(0, count).map(c => ({
    id: rid(),
    label: c.label || 'Alternative',
    summary: `Update ${def.label}`,
    diff: { kind: 'block.replace', pageIdx: target.pageIdx, secIdx: target.secIdx, section: { ...sec, data: { ...sec.data, ...c.data } } },
  }));
}

// ---- Page insert ----
async function viInsertPage(doc, target, count, brief, provider) {
  const ctxBefore = doc.pages.slice(Math.max(0, target.atIdx - 2), target.atIdx).map((p, i) => `[${i + 1}] ${p.title} (${(p.sections || []).map(s => s.kind).join(', ')})`).join('\n');
  const ctxAfter = doc.pages.slice(target.atIdx, target.atIdx + 2).map((p, i) => `[next] ${p.title} (${(p.sections || []).map(s => s.kind).join(', ')})`).join('\n');

  const prompt = `You are Vi, proposing ${count} alternative new pages to add to a ConceptV ${doc.type}.

${BRAND_VOICE}

Document title: "${doc.title}"
Pages before this slot:
${ctxBefore || '(none)'}
Pages after this slot:
${ctxAfter || '(none)'}

${brief ? `User hint: "${brief}"` : ''}

Available block kinds:
${blockShapeDoc()}

Each candidate is a full page with title, kind, and 2-4 sections. Be diverse — try different angles (a CTA page, a stat page, a comparison, a quote, a process flow, a contact card …).

Respond ONLY as JSON (no prose):
{"candidates":[{"label":"page title (3-5 words)","kind":"title|content|cover","sections":[{"kind":"...","data":{...}}, ...]}, ...]}`;
  const reply = await aiComplete(prompt, typeof provider !== "undefined" ? provider : null);
  const parsed = parseJsonLoose(reply);
  if (!parsed?.candidates) return [];
  return parsed.candidates.slice(0, count).map(c => ({
    id: rid(),
    label: c.label || 'New page',
    summary: `${(c.sections || []).length} blocks · ${c.kind || 'content'}`,
    diff: {
      kind: 'page.insert',
      atIdx: target.atIdx,
      page: {
        title: c.label || 'New page',
        kind: c.kind || 'content',
        sections: (c.sections || []).filter(s => s.kind && window.WS_BLOCKS[s.kind]).map(s => ensureSection({ kind: s.kind, data: s.data || {} })),
      },
    },
  }));
}

// ---- Doc transform (whole-doc instruction) ----
async function viDocTransform(doc, target, count, brief, provider) {
  const instruction = target.instruction || brief;
  if (!instruction) return [];
  const flat = (doc.pages || []).slice(0, 12).flatMap((p, pi) =>
    (p.sections || []).map((s, si) => ({ pageIdx: pi, secIdx: si, kind: s.kind, data: s.data }))
  );
  const prompt = `You are Vi, applying a whole-document transform to a ConceptV ${doc.type}.

${BRAND_VOICE}

Document title: "${doc.title}"

User instruction: "${instruction}"

Blocks in the document (top 12):
${flat.map(f => `[p${f.pageIdx + 1}.s${f.secIdx + 1}] ${f.kind}: ${JSON.stringify(f.data).slice(0, 120)}`).join('\n')}

Propose ${count} alternative transforms that satisfy the instruction. Each transform is a list of block updates. Don't change more than 6 blocks per candidate. Keep IDs and kinds; only change data fields. Be different from each other — different intensities or angles.

Respond ONLY as JSON (no prose):
{"candidates":[{"label":"3-5 word summary","updates":[{"pageIdx":0,"secIdx":0,"dataPatch":{...}}, ...]}, ...]}`;
  const reply = await aiComplete(prompt, typeof provider !== "undefined" ? provider : null);
  const parsed = parseJsonLoose(reply);
  if (!parsed?.candidates) return [];
  return parsed.candidates.slice(0, count).map(c => ({
    id: rid(),
    label: c.label || 'Transform',
    summary: `${(c.updates || []).length} blocks affected`,
    diff: {
      kind: 'batch',
      diffs: (c.updates || []).slice(0, 12).map(u => ({
        kind: 'block.update',
        pageIdx: u.pageIdx, secIdx: u.secIdx,
        dataPatch: u.dataPatch || {},
      })),
    },
  }));
}

// ---- Theme generate (offers 3 alternative theme presets) ----
async function viThemeGenerate(doc, target, count, brief, provider) {
  const knownThemes = ['editorial', 'showroom', 'documentation', 'narrative', 'data'];
  const prompt = `You are Vi, proposing ${count} alternative visual themes for a ConceptV ${doc.type}.

${BRAND_VOICE}

Document title: "${doc.title}"
Current theme: ${doc.theme || 'editorial'}
${brief ? `User hint: "${brief}"` : ''}

ConceptV's known themes are: ${knownThemes.join(', ')}. Each new candidate proposes EITHER a known theme name from this list (if it fits) or a custom theme description. Pair every theme with a one-line rationale.

Respond ONLY as JSON: {"candidates":[{"label":"3-5 word name","theme":"<known theme key OR custom name>","rationale":"why this fits"}]}`;
  const reply = await aiComplete(prompt, typeof provider !== "undefined" ? provider : null, true);
  const parsed = parseJsonLoose(reply);
  if (!parsed?.candidates) return [];
  return parsed.candidates.slice(0, count).map(c => ({
    id: rid(),
    label: c.label || c.theme,
    summary: c.rationale || '',
    diff: { kind: 'doc.update', patch: { theme: c.theme || 'editorial' } },
  }));
}

// ---- Layout generate (Vi proposes a full page layout for an empty slot) ----
async function viLayoutGenerate(doc, target, count, brief, provider) {
  const ctx = pageContextSummary(doc, target.pageIdx ?? 0);
  const prompt = `You are Vi, proposing ${count} layout candidates for a page in a ConceptV ${doc.type}.

${BRAND_VOICE}

Document title: "${doc.title}"
Page index: ${target.pageIdx ?? 0}
Surrounding context:
${ctx}

${brief ? `User hint: "${brief}"` : ''}

Available block kinds (use 2-5 per layout):
${blockShapeDoc()}

Each candidate is a full layout = ordered list of blocks with their data filled in (tailored to the doc title and context). Each candidate should take a DIFFERENT structural approach.

Respond ONLY as JSON: {"candidates":[{"label":"3-5 word layout name","sections":[{"kind":"...","data":{...}}, ...]}]}`;
  const reply = await aiComplete(prompt, typeof provider !== "undefined" ? provider : null);
  const parsed = parseJsonLoose(reply);
  if (!parsed?.candidates) return [];
  return parsed.candidates.slice(0, count).map(c => {
    const sections = (c.sections || [])
      .filter(s => s.kind && window.WS_BLOCKS?.[s.kind])
      .map(s => ensureSection({ kind: s.kind, data: s.data || {} }));
    if (!sections.length) return null;
    return {
      id: rid(),
      label: c.label || 'Layout',
      summary: `${sections.length} blocks`,
      diff: {
        kind: 'batch',
        diffs: [
          // Replace the page's sections wholesale: a series of inserts at idx 0+
          { kind: 'page.update', pageIdx: target.pageIdx, patch: { sections: [] } },
          ...sections.map((sec, i) => ({ kind: 'block.insert', pageIdx: target.pageIdx, atIdx: i, section: sec })),
        ],
      },
    };
  }).filter(Boolean);
}

// ---- Widget alternate (full-data variation) ----
async function viWidgetAlternate(doc, target, count, brief, provider) {
  const prompt = `You are Vi, generating ${count} alternative versions of a ConceptV widget.

${BRAND_VOICE}

Current widget: kind=${doc.widgetKind}, system=${doc.system}
Current data:
${JSON.stringify(doc.data, null, 2)}

${brief ? `User hint: "${brief}"` : ''}

Generate ${count} DIFFERENT data alternatives, keeping the same widget kind and system. Vary the angle, the metric focus, the property/hub being represented. Same fields, different content.

Respond ONLY as JSON (no prose):
{"candidates":[{"label":"3-5 word summary","data":{title:"",eyebrow:"",kpis:[],rows:[],media:{},chart:{},cta:{}}}, ...]}`;
  const reply = await aiComplete(prompt, typeof provider !== "undefined" ? provider : null);
  const parsed = parseJsonLoose(reply);
  if (!parsed?.candidates) return [];
  return parsed.candidates.slice(0, count).map(c => ({
    id: rid(),
    label: c.label || 'Alternative',
    summary: 'Replace widget content',
    diff: { kind: 'widget.data', dataPatch: c.data || {} },
  }));
}

// ---- Widget KPIs regen ----
async function viWidgetKPIsRegen(doc, target, count, brief, provider) {
  const want = target.count || (doc.data?.kpis?.length || 3);
  const prompt = `You are Vi, generating ${count} alternative KPI sets for a ConceptV widget.

${BRAND_VOICE}

Widget title: "${doc.data?.title}"
Existing KPIs: ${JSON.stringify(doc.data?.kpis || [])}
${brief ? `User hint: "${brief}"` : ''}

Produce ${count} sets, each ${want} KPIs. Each set picks a different angle (occupancy vs revenue vs engagement vs operational vs forward-looking). Keep KPI shape: {label, value, delta, deltaKind}.

Respond ONLY as JSON: {"candidates":[{"label":"3-5 word angle","kpis":[...]}]}`;
  const reply = await aiComplete(prompt, typeof provider !== "undefined" ? provider : null);
  const parsed = parseJsonLoose(reply);
  if (!parsed?.candidates) return [];
  return parsed.candidates.slice(0, count).map(c => ({
    id: rid(),
    label: c.label || 'KPI set',
    summary: `${(c.kpis || []).length} KPIs`,
    diff: { kind: 'widget.data', dataPatch: { kpis: (c.kpis || []).slice(0, 4) } },
  }));
}

// ---- Wizard step insert ----
async function viWizardStepInsert(doc, target, count, brief, provider) {
  const ctx = (doc.steps || []).map((s, i) => `[${i + 1}] ${s.kind} · ${s.title} — ${s.body || ''}`).join('\n');
  const prompt = `You are Vi, proposing ${count} alternative new steps to add to a ConceptV ${doc.wizardKind} wizard.

${BRAND_VOICE}

Existing steps:
${ctx || '(none)'}

Inserting at position ${target.atIdx + 1}.
${brief ? `User hint: "${brief}"` : ''}

Each candidate is a single step. Step kinds: capture | form | choice | review | celebrate.

Respond ONLY as JSON:
{"candidates":[{"label":"3-5 word summary","step":{"kind":"...","title":"...","body":"...","fields":[],"options":[]}}, ...]}`;
  const reply = await aiComplete(prompt, typeof provider !== "undefined" ? provider : null);
  const parsed = parseJsonLoose(reply);
  if (!parsed?.candidates) return [];
  return parsed.candidates.slice(0, count).map(c => ({
    id: rid(),
    label: c.label || 'New step',
    summary: c.step?.kind || 'form',
    diff: { kind: 'wizard.step.insert', atIdx: target.atIdx, step: c.step || {} },
  }));
}

// ---- Wizard step alternate ----
async function viWizardStepAlternate(doc, target, count, brief, provider) {
  const step = doc.steps?.[target.stepIdx];
  if (!step) return [];
  const prompt = `You are Vi, generating ${count} alternative versions of a wizard step.

${BRAND_VOICE}

Wizard kind: ${doc.wizardKind}. Other steps:
${(doc.steps || []).filter((_, i) => i !== target.stepIdx).map((s, i) => `[${i}] ${s.title}`).join(', ')}

Current step:
${JSON.stringify(step, null, 2)}

${brief ? `User hint: "${brief}"` : ''}

Generate ${count} DIFFERENT alternatives. Same kind unless the user hint says otherwise.

Respond ONLY as JSON:
{"candidates":[{"label":"3-5 word summary","patch":{"title":"","body":"","fields":[],"options":[]}}, ...]}`;
  const reply = await aiComplete(prompt, typeof provider !== "undefined" ? provider : null);
  const parsed = parseJsonLoose(reply);
  if (!parsed?.candidates) return [];
  return parsed.candidates.slice(0, count).map(c => ({
    id: rid(),
    label: c.label || 'Alternative',
    summary: `Step ${target.stepIdx + 1}`,
    diff: { kind: 'wizard.step.update', stepIdx: target.stepIdx, patch: c.patch || {} },
  }));
}

// ---- Field alternate ----
async function viFieldAlternate(doc, target, count, brief, provider) {
  const { current, context, blockKind, fieldName, angle } = target;
  const angleHint = {
    shorter:  'Make each alternative SHORTER than the current — half the word count where possible.',
    formal:   'Make each alternative MORE FORMAL — drop colloquialism, prefer precise verbs.',
    specific: 'Make each alternative MORE SPECIFIC — concrete numbers, named examples, proper nouns where natural.',
    different:'Each alternative should take a DIFFERENT angle from the current value (and from each other).',
  }[angle] || 'Each alternative should be a distinct angle, similar length and structure to the current.';
  const prompt = `You are Vi, regenerating one field in a ConceptV ${doc.type} document.

${BRAND_VOICE}

Document title: "${doc.title}"
Block type: ${blockKind || '?'}, field: ${fieldName || '?'}
Current value: ${JSON.stringify(current)}
${context ? `Surrounding context: ${context}` : ''}
${brief ? `User hint: "${brief}"` : ''}

${angleHint}

Generate ${count} alternative values for this field. Match the original's tone, length (unless asked to change it), and structure (if it's a sentence, keep it a sentence; if it's a number string like "94%", keep that format).

Respond ONLY as JSON:
{"candidates":[{"label":"angle","value":<same JSON type as current>}, ...]}`;
  const reply = await aiComplete(prompt, typeof provider !== "undefined" ? provider : null, true);
  const parsed = parseJsonLoose(reply);
  if (!parsed?.candidates) return [];
  return parsed.candidates.slice(0, count).map(c => ({
    id: rid(),
    label: c.label || 'Alternative',
    summary: typeof c.value === 'string' ? c.value.slice(0, 60) : JSON.stringify(c.value).slice(0, 60),
    value: c.value,
    diff: null,
  }));
}

// ============================================================
// Intent classifier — for chat-rail edit mode
// ============================================================

async function classifyIntent({ doc, message }) {
  if (!doc || !message) return { kind: 'question' };
  const prompt = `You are Vi, deciding whether a user message in ConceptV Studio is asking a QUESTION or requesting an EDIT to the current document.

Current document type: ${doc.type}
Document title: "${doc.title}"
${doc.pages ? `Pages: ${doc.pages.length}` : ''}
${doc.steps ? `Steps: ${doc.steps.length}` : ''}

User message: "${message}"

Reply ONLY as JSON, no prose: {"kind":"edit"|"question","reason":"short justification"}

Edit examples: "change the headline to X", "add a CTA slide", "make page 2 more urgent", "shorten everything", "make this widget about Tower West".
Question examples: "what should come next?", "is this any good?", "audit this for me", "what fonts are these?".`;
  // Loud: a classifier failure must surface, not silently downgrade to 'question'.
  const reply = await aiComplete(prompt, typeof provider !== "undefined" ? provider : null);
  const parsed = parseJsonLoose(reply);
  if (parsed?.kind === 'edit') return { kind: 'edit', reason: parsed.reason };
  return { kind: 'question' };
}

async function generateEdit({ doc, message }) {
  // Builds a single batch diff that satisfies the user message.
  const flat = doc.type === 'deck' || doc.type === 'brochure'
    ? (doc.pages || []).slice(0, 12).flatMap((p, pi) =>
        (p.sections || []).map((s, si) => ({ pageIdx: pi, secIdx: si, kind: s.kind, data: s.data })))
    : [];
  const prompt = `You are Vi, generating an EDIT diff for a ConceptV ${doc.type} document.

${BRAND_VOICE}

Document title: "${doc.title}"
${doc.type === 'deck' || doc.type === 'brochure' ? `
Existing blocks (top 12):
${flat.map(f => `[p${f.pageIdx + 1}.s${f.secIdx + 1}] ${f.kind}: ${JSON.stringify(f.data).slice(0, 120)}`).join('\n')}` : ''}
${doc.type === 'widget' ? `Widget data: ${JSON.stringify(doc.data).slice(0, 400)}` : ''}
${doc.type === 'wizard' ? `Steps: ${(doc.steps || []).map((s, i) => `[${i + 1}] ${s.kind} · ${s.title}`).join('; ')}` : ''}

User request: "${message}"

Generate the edits as JSON. Available op kinds:
- block.update {pageIdx, secIdx, dataPatch}
- block.replace {pageIdx, secIdx, section:{kind, data}}
- block.remove {pageIdx, secIdx}
- block.insert {pageIdx, atIdx, section:{kind, data}}
- page.insert {atIdx, page:{title, kind, sections}}
- doc.update {patch:{title}}
- widget.data {dataPatch}
- wizard.step.insert {atIdx, step}
- wizard.step.update {stepIdx, patch}
- wizard.step.remove {stepIdx}

Respond ONLY as JSON:
{"summary":"plain-English description of what you're doing","ops":[{"kind":"...","..."},...]}`;
  // Loud: surface generation/parse failures rather than returning a null no-op.
  const reply = await aiComplete(prompt, typeof provider !== "undefined" ? provider : null);
  const parsed = parseJsonLoose(reply);
  if (!parsed?.ops?.length) return null;
  return {
    summary: parsed.summary || 'Edit',
    diff: { kind: 'batch', diffs: parsed.ops.filter(op => op.kind) },
  };
}

// ============================================================
// Smart templates — Vi-extracted variables + materialization
// ============================================================

function stripVolatile(doc) {
  // Remove IDs, timestamps so substitution is stable across runs
  const next = clone(doc);
  delete next.id; delete next.createdAt;
  (next.pages || []).forEach(p => {
    delete p.id;
    (p.sections || []).forEach(s => { delete s.id; });
  });
  (next.steps || []).forEach(s => { delete s.id; });
  return next;
}

async function extractTemplate(doc) {
  const slim = stripVolatile(doc);
  // Cap large docs — Vi only needs to see strings
  const docJson = JSON.stringify(slim).slice(0, 12000);
  const prompt = `You are converting a ConceptV ${doc.type} into a parameterised template.

${BRAND_VOICE}

Input document JSON:
${docJson}

Identify 3-7 high-level VARIABLES — values that would change between runs of this template. Good variables: proper nouns (property names, person names), specific big numbers or money figures, audience labels, dates, top-level product/feature names, primary URLs. Skip structural strings (button labels like "Continue", field labels like "Bedrooms", recurring brand terms like "ConceptV", "Vi", "Virtual Hub", "Property Wizard").

For each variable, give it a kebab-case key, a human label, a default value (the current value), and a kind ('text' | 'number' | 'url' | 'audience').

Then return the SAME document JSON with every variable occurrence replaced by a placeholder of the form {{key}}. Preserve all structural strings exactly — only replace the actual variable values.

Respond ONLY as JSON, no prose:
{
  "variables": [{"key":"property_name","label":"Property name","default":"Tower East","kind":"text"}, ...],
  "doc": <the document with {{key}} placeholders>
}`;
  const reply = await aiComplete(prompt, typeof provider !== "undefined" ? provider : null);
  const parsed = parseJsonLoose(reply);
  if (!parsed?.doc) throw new Error('Vi returned no parsable template');
  return {
    variables: Array.isArray(parsed.variables) ? parsed.variables : [],
    doc: parsed.doc,
  };
}

function materializeTemplate(template, values) {
  if (!template?.doc) return null;
  // Stringify, replace placeholders, parse back.
  let json = JSON.stringify(template.doc);
  // Replace each variable
  for (const v of (template.variables || [])) {
    const re = new RegExp('\\{\\{' + escapeRegex(v.key) + '\\}\\}', 'g');
    json = json.replace(re, String(values[v.key] ?? v.default ?? '').replace(/"/g, '\\"'));
  }
  // Any leftover placeholders -> empty string
  json = json.replace(/\{\{(\w+)\}\}/g, '');
  let next;
  try { next = JSON.parse(json); } catch { return null; }
  // Re-stamp IDs
  next.id = 'doc-' + Date.now();
  next.createdAt = Date.now();
  (next.pages || []).forEach((p, i) => {
    p.id = 'p-' + Date.now() + '-' + i;
    (p.sections || []).forEach((s, j) => { s.id = 'sec-' + Date.now() + '-' + i + '-' + j; });
  });
  (next.steps || []).forEach((s, i) => { s.id = 'wz-' + Date.now() + '-' + i; });
  return next;
}

function escapeRegex(s) { return String(s).replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

function computeSuggestions(doc, ctx) {
  if (!doc) return [];
  const out = [];
  const { currentPage = 0 } = ctx || {};

  if (doc.type === 'deck' || doc.type === 'brochure') {
    const page = doc.pages?.[currentPage];
    const total = doc.pages?.length || 0;

    if (page && (!page.sections || page.sections.length === 0)) {
      out.push({ id: 'fill-page', label: 'Fill this empty page with Vi', target: { kind: 'insert.block', pageIdx: currentPage, atIdx: 0 }, intent: 'fill' });
    }
    if (page?.sections?.length === 1) {
      out.push({ id: 'add-supporting-block', label: 'Add a supporting block to this page', target: { kind: 'insert.block', pageIdx: currentPage, atIdx: page.sections.length } });
    }
    const hasCta = doc.pages?.some(p => (p.sections || []).some(s => s.kind === 'button' || s.kind === 'callout' || s.data?.cta));
    if (!hasCta && total >= 2) {
      out.push({ id: 'add-cta', label: 'Add a call-to-action page at the end', target: { kind: 'insert.page', atIdx: total } });
    }
    const hasStats = doc.pages?.some(p => (p.sections || []).some(s => s.kind === 'stats' || s.kind === 'metricRow' || s.kind === 'statPills' || s.kind === 'statTable'));
    if (!hasStats && total >= 1) {
      out.push({ id: 'add-stats', label: 'Add a stats / proof page', target: { kind: 'insert.page', atIdx: Math.min(total, 2) } });
    }
    if (total >= 3) {
      out.push({ id: 'shorten', label: 'Shorten every block', target: { kind: 'doc.transform', instruction: 'Shorten every block — half the word count where possible, keep the meaning' } });
      out.push({ id: 'urgency', label: 'Make this more urgent', target: { kind: 'doc.transform', instruction: 'Make this more urgent — sharper verbs, present tense, specific numbers' } });
    }
    if (doc.pages?.length >= 1) {
      out.push({ id: 'audit', label: 'Audit voice & tone', intent: 'audit', target: { kind: 'doc.transform', instruction: 'Audit every block for ConceptV voice: sentence case, second person, no exclamation marks, no emoji. Flag any issues.' } });
    }
  }

  if (doc.type === 'widget') {
    out.push({ id: 'kpis-regen', label: 'Regenerate the KPI set', target: { kind: 'widget.kpis.regen', count: doc.data?.kpis?.length || 3 } });
    out.push({ id: 'widget-alt', label: '3 alternative angles for this widget', target: { kind: 'widget.alternate' } });
  }

  if (doc.type === 'wizard') {
    out.push({ id: 'add-step', label: 'Add a step before review', target: { kind: 'wizard.step.insert', atIdx: Math.max(0, (doc.steps?.length || 1) - 1) } });
    if ((doc.steps || []).length >= 1) {
      out.push({ id: 'shorten-wiz', label: 'Tighten wording across every step', target: { kind: 'doc.transform', instruction: 'Tighten the body copy across every step — concise and clear' } });
    }
  }

  return out;
}

// ============================================================
// Bridge — global hook so other surfaces can interact with a live doc
// ============================================================

const BRIDGE = {
  doc: null,
  saveDoc: null,
  currentPage: 0,
  selectedIdx: null,
  setActive(doc, saveDoc, ctx) {
    BRIDGE.doc = doc;
    BRIDGE.saveDoc = saveDoc;
    BRIDGE.currentPage = ctx?.currentPage || 0;
    BRIDGE.selectedIdx = ctx?.selectedIdx ?? null;
    // Record "what screen Vi is on" in the AI registry, so every capability's
    // context resolves from the live surface without being passed it by hand.
    if (window.CV_AI) window.CV_AI.setActiveSurface(doc?.type || null, doc, { currentPage: BRIDGE.currentPage, selectedIdx: BRIDGE.selectedIdx });
    BRIDGE.notify();
  },
  clear() {
    BRIDGE.doc = null; BRIDGE.saveDoc = null;
    BRIDGE.currentPage = 0; BRIDGE.selectedIdx = null;
    BRIDGE.notify();
  },
  apply(diff) {
    if (!BRIDGE.doc || !BRIDGE.saveDoc) return false;
    const next = applyDiff(BRIDGE.doc, diff);
    BRIDGE.saveDoc(next);
    return true;
  },
  listeners: new Set(),
  subscribe(fn) { BRIDGE.listeners.add(fn); return () => BRIDGE.listeners.delete(fn); },
  notify() { BRIDGE.listeners.forEach(fn => fn()); },
  getActive() { return BRIDGE.doc; },
};

function useBridgeDoc() {
  const [, force] = useState_ai(0);
  useEffect_ai(() => BRIDGE.subscribe(() => force(x => x + 1)), []);
  return BRIDGE.doc;
}

// ============================================================
// Candidate Gallery UI
// ============================================================

function WSCandidateGallery({ open, title, busy, candidates, doc, onPick, onClose, onRefine, count = 3 }) {
  const [hint, setHint] = useState_ai('');
  const [focused, setFocused] = useState_ai(0);
  const [hovered, setHovered] = useState_ai(null);
  const containerRef = useRef_ai(null);

  // Keyboard nav while gallery open
  useEffect_ai(() => {
    if (!open) return;
    function onKey(e) {
      if (e.target?.tagName === 'INPUT' || e.target?.tagName === 'TEXTAREA') return;
      const list = candidates || [];
      if (e.key === 'Escape') { e.preventDefault(); onClose?.(); }
      else if (e.key === 'ArrowRight' || e.key === 'ArrowDown') { e.preventDefault(); setFocused(f => Math.min((list.length || 1) - 1, f + 1)); }
      else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') { e.preventDefault(); setFocused(f => Math.max(0, f - 1)); }
      else if (e.key === 'Enter') { e.preventDefault(); const c = list[focused]; if (c) onPick?.(c); }
      else if (/^[1-9]$/.test(e.key)) {
        const i = parseInt(e.key, 10) - 1;
        if (list[i]) { e.preventDefault(); onPick?.(list[i]); }
      }
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, candidates, focused, onPick, onClose]);

  useEffect_ai(() => { if (open) setFocused(0); }, [open, title]);

  if (!open) return null;
  const list = candidates || [];
  // Show placeholder cards while streaming
  const placeholders = busy ? Math.max(0, count - list.length) : 0;

  return (
    <div className="ws-cand-overlay" onClick={onClose}>
      <div className="ws-cand-panel" onClick={e => e.stopPropagation()} ref={containerRef}>
        <div className="ws-cand-head">
          <ViShape size={18}/>
          <span className="title">{title || 'Pick a candidate'}</span>
          {list.length > 0 && (
            <span className="ws-cand-keyhint">
              <kbd>1</kbd>–<kbd>{list.length}</kbd> pick · <kbd>←</kbd><kbd>→</kbd> nav · <kbd>↵</kbd> apply · <kbd>esc</kbd> close
            </span>
          )}
          <button className="ws-cand-close" onClick={onClose} title="Close (esc)">✕</button>
        </div>

        {(list.length > 0 || placeholders > 0) && (
          <div className="ws-cand-grid">
            {list.map((c, i) => (
              <button
                key={c.id}
                className={`ws-cand-card ${i === focused ? 'focused' : ''} ${i === hovered ? 'hovered' : ''}`}
                onClick={() => onPick(c)}
                onMouseEnter={() => setHovered(i)}
                onMouseLeave={() => setHovered(null)}
                onFocus={() => setFocused(i)}>
                <div className="ws-cand-card-num">{i + 1}</div>
                <div className="ws-cand-card-preview">
                  <WSCandidatePreview doc={doc} candidate={c}/>
                </div>
                <div className="ws-cand-card-meta">
                  <strong>{c.label}</strong>
                  {c.summary && <span>{c.summary}</span>}
                  <span className="diff-desc">{describeDiff(c.diff, doc)}</span>
                </div>
              </button>
            ))}
            {Array.from({ length: placeholders }).map((_, i) => (
              <div key={'ph-' + i} className="ws-cand-card placeholder">
                <div className="ws-cand-card-num"><ViShape size={11} animated/></div>
                <div className="ws-cand-card-preview">
                  <div className="ws-cand-skeleton">
                    <div/><div/><div/><div/>
                  </div>
                </div>
                <div className="ws-cand-card-meta">
                  <strong className="dim">Generating…</strong>
                  <span className="dim">Vi is composing this option</span>
                </div>
              </div>
            ))}
          </div>
        )}

        {!busy && list.length === 0 && (
          <div className="ws-cand-empty">
            <ViShape size={18}/>
            <p>No candidates returned. Try a hint to steer Vi.</p>
          </div>
        )}

        {onRefine && (
          <div className="ws-cand-refine">
            <input
              placeholder='Steer Vi — e.g. "more stat-focused", "use Tower West", "shorter"'
              value={hint}
              onChange={e => setHint(e.target.value)}
              onKeyDown={e => {
                if (e.key === 'Enter' && hint.trim()) {
                  e.preventDefault();
                  onRefine(hint.trim());
                  setHint('');
                }
              }}/>
            <button className="dsa-btn dsa-btn--outline dsa-btn--sm" onClick={() => { onRefine(hint.trim() || 'different angle'); setHint(''); }} disabled={busy}>
              {busy ? <><ViShape size={11} animated/> generating</> : 'Regenerate'}
            </button>
            <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => { onRefine('more options'); setHint(''); }} disabled={busy} title="Get 3 more without losing these">
              + 3 more
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function WSCandidatePreview({ doc, candidate }) {
  if (!candidate || !doc) return null;
  const diff = candidate.diff;
  if (!diff) {
    return <div className="ws-cand-preview-field">{typeof candidate.value === 'string' ? candidate.value : JSON.stringify(candidate.value)}</div>;
  }
  try {
    const previewDoc = applyDiff(doc, diff);
    if (diff.kind === 'block.insert' || diff.kind === 'block.replace') {
      const pi = diff.pageIdx;
      const si = diff.kind === 'block.insert' ? diff.atIdx : diff.secIdx;
      const sec = previewDoc.pages[pi]?.sections[si];
      if (sec) return <RenderedBlockPreview section={sec} scale={0.48}/>;
    }
    if (diff.kind === 'block.update') {
      const sec = previewDoc.pages[diff.pageIdx]?.sections[diff.secIdx];
      if (sec) return <RenderedBlockPreview section={sec} scale={0.48}/>;
    }
    if (diff.kind === 'page.insert') {
      const page = previewDoc.pages[diff.atIdx];
      return <RenderedPagePreview page={page}/>;
    }
    if (diff.kind === 'batch') {
      // Show real before/after for the first 3 affected blocks
      const affected = (diff.diffs || []).filter(d => /block\./.test(d.kind)).slice(0, 2);
      if (!affected.length) {
        return <div className="ws-cand-preview-batch">
          {(diff.diffs || []).slice(0, 4).map((d, i) => (
            <div key={i} className="line">{describeDiff(d, doc)}</div>
          ))}
          {diff.diffs?.length > 4 && <div className="line dim">+ {diff.diffs.length - 4} more</div>}
        </div>;
      }
      return <div className="ws-cand-batch-stack">
        {affected.map((d, i) => {
          let sec;
          if (d.kind === 'block.update') sec = previewDoc.pages[d.pageIdx]?.sections[d.secIdx];
          else if (d.kind === 'block.replace') sec = previewDoc.pages[d.pageIdx]?.sections[d.secIdx];
          if (!sec) return <div key={i} className="line">{describeDiff(d, doc)}</div>;
          return <RenderedBlockPreview key={i} section={sec} scale={0.4} maxHeight={70}/>;
        })}
        {diff.diffs.length > 2 && <div className="line dim">+ {diff.diffs.length - 2} more changes</div>}
      </div>;
    }
    if (diff.kind === 'widget.data') {
      return <MiniWidgetPreview data={{ ...doc.data, ...diff.dataPatch }} widgetKind={doc.widgetKind} system={doc.system}/>;
    }
    if (diff.kind === 'wizard.step.insert' || diff.kind === 'wizard.step.update') {
      const step = diff.step || { ...doc.steps[diff.stepIdx], ...(diff.patch || {}) };
      return <MiniStepPreview step={step}/>;
    }
  } catch {}
  return <div className="ws-cand-preview-field">{describeDiff(diff, doc)}</div>;
}

function MiniBlockPreview({ section }) {
  const def = window.WS_BLOCKS?.[section.kind];
  if (!def) return <div className="ws-cand-preview-field">{section.kind}</div>;
  return (
    <div className="ws-cand-mini-block">
      <div className="kind-tag">{def.label}</div>
      <div className="content">
        {section.kind === 'headline' && <div className="big">{section.data?.text}</div>}
        {section.kind === 'hero' && (<><div className="eyebrow">{section.data?.eyebrow}</div><div className="big">{section.data?.headline}</div><div className="body">{section.data?.body}</div></>)}
        {section.kind === 'body' && <div className="body">{section.data?.text}</div>}
        {section.kind === 'quote' && <div className="quote">"{section.data?.text}"<div className="who">{section.data?.who}</div></div>}
        {section.kind === 'stats' && <div className="mini-stats">{(section.data?.items || []).slice(0, 3).map((it, i) => <div key={i}><span className="v">{it.v}</span><span className="l">{it.l}</span></div>)}</div>}
        {section.kind === 'callout' && (<><div className="callout-lbl">{section.data?.label}</div><div className="body">{section.data?.text}</div></>)}
        {section.kind === 'bullets' && (
          <ul className="mini-bullets">{(section.data?.items || []).slice(0, 4).map((it, i) => <li key={i}>{typeof it === 'string' ? it : ''}</li>)}</ul>
        )}
        {(section.kind === 'metricRow' || section.kind === 'statPills') && (
          <div className="mini-stats">{(section.data?.items || []).slice(0, 4).map((it, i) => <div key={i}><span className="v">{it.v}</span><span className="l">{it.l}</span></div>)}</div>
        )}
        {!['headline','hero','body','quote','stats','callout','bullets','metricRow','statPills'].includes(section.kind) && (
          <div className="generic-content">{JSON.stringify(section.data).slice(0, 140)}…</div>
        )}
      </div>
    </div>
  );
}

function MiniPagePreview({ page }) {
  return (
    <div className="ws-cand-mini-page">
      <div className="page-title">{page.title}</div>
      <div className="page-blocks">
        {(page.sections || []).slice(0, 4).map((s, i) => (
          <div key={i} className="stub">{window.WS_BLOCKS?.[s.kind]?.label || s.kind}</div>
        ))}
      </div>
    </div>
  );
}

function MiniWidgetPreview({ data, widgetKind, system }) {
  return (
    <div className="ws-cand-mini-widget">
      {data?.eyebrow && <div className="eyebrow">{data.eyebrow}</div>}
      <div className="title">{data?.title}</div>
      {(data?.kpis || []).slice(0, 3).map((k, i) => (
        <div key={i} className="kpi"><span className="v">{k.value}</span><span className="l">{k.label}</span></div>
      ))}
    </div>
  );
}

function MiniStepPreview({ step }) {
  return (
    <div className="ws-cand-mini-step">
      <div className="kind-tag">{step.kind}</div>
      <div className="title">{step.title}</div>
      {step.body && <div className="body">{step.body}</div>}
      {(step.fields || []).slice(0, 3).map((f, i) => (
        <div key={i} className="field">{f.label} <span className="kind">({f.kind})</span></div>
      ))}
      {(step.options || []).slice(0, 3).map((o, i) => (
        <div key={i} className="option">○ {o}</div>
      ))}
    </div>
  );
}

// ============================================================
// Diff Card (for chat-rail-driven edits)
// ============================================================

function WSDiffCard({ proposal, doc, onApply, onDiscard }) {
  const [expanded, setExpanded] = useState_ai(false);
  if (!proposal) return null;
  const diffs = proposal.diff?.diffs || [proposal.diff];
  const visibleDiffs = expanded ? diffs : diffs.slice(0, 3);
  const previewDoc = doc ? applyDiff(doc, proposal.diff) : null;

  return (
    <div className="ws-diff-card">
      <div className="ws-diff-summary">
        <ViShape size={12}/>
        <span>{proposal.summary}</span>
      </div>
      <div className="ws-diff-list">
        {visibleDiffs.map((d, i) => (
          <WSDiffLine key={i} diff={d} doc={doc} previewDoc={previewDoc}/>
        ))}
        {diffs.length > visibleDiffs.length && (
          <button className="ws-diff-more" onClick={() => setExpanded(e => !e)}>
            {expanded ? '↑ collapse' : `+ ${diffs.length - 3} more change${diffs.length - 3 === 1 ? '' : 's'}`}
          </button>
        )}
      </div>
      <div className="ws-diff-actions">
        <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={onDiscard}>Discard</button>
        <button className="dsa-btn dsa-btn--primary dsa-btn--sm" onClick={onApply}>Apply</button>
      </div>
    </div>
  );
}

function WSDiffLine({ diff, doc, previewDoc }) {
  if (!diff) return null;
  // For block.update / block.replace — render before / after side by side
  if (diff.kind === 'block.update' || diff.kind === 'block.replace') {
    const before = doc?.pages?.[diff.pageIdx]?.sections?.[diff.secIdx];
    const after = previewDoc?.pages?.[diff.pageIdx]?.sections?.[diff.secIdx];
    if (before && after) {
      return (
        <div className="ws-diff-line ws-diff-ba">
          <div className="ba-tag">{describeDiff(diff, doc)}</div>
          <div className="ba-grid">
            <div className="ba-side">
              <div className="ba-label">before</div>
              <RenderedBlockPreview section={before} scale={0.36} maxHeight={70}/>
            </div>
            <div className="ba-arrow">→</div>
            <div className="ba-side">
              <div className="ba-label">after</div>
              <RenderedBlockPreview section={after} scale={0.36} maxHeight={70}/>
            </div>
          </div>
        </div>
      );
    }
  }
  if (diff.kind === 'block.insert') {
    const after = previewDoc?.pages?.[diff.pageIdx]?.sections?.[diff.atIdx];
    if (after) {
      return (
        <div className="ws-diff-line ws-diff-insert">
          <div className="ba-tag">{describeDiff(diff, doc)}</div>
          <RenderedBlockPreview section={after} scale={0.4} maxHeight={80}/>
        </div>
      );
    }
  }
  if (diff.kind === 'page.insert') {
    const page = previewDoc?.pages?.[diff.atIdx];
    if (page) {
      return (
        <div className="ws-diff-line ws-diff-insert">
          <div className="ba-tag">{describeDiff(diff, doc)}</div>
          <RenderedPagePreview page={page} scale={0.24}/>
        </div>
      );
    }
  }
  // Default — text description
  return <div className="ws-diff-line">— {describeDiff(diff, doc)}</div>;
}

// ============================================================
// Transform menu
// ============================================================

// Whole-doc transforms — a PROJECTION of the CV_AI skill registry (layer:skill,
// family:transform), not a hand-kept list. Registering a transform skill in the
// AI catalogue makes it appear here automatically — the interface and the AI
// read one source, so they are synchronised by construction.
function docTransforms() {
  if (!window.CV_AI) return [];
  return window.CV_AI.query({ layer: 'skill', family: 'transform' }).map(s => {
    const out = { id: s.id.replace(/^skill\./, ''), label: s.name, sub: s.description, skillId: s.id };
    if (s.target && s.target.kind && s.target.kind !== 'doc.transform') out.target = { kind: s.target.kind };
    else out.instruction = s.instruction;
    return out;
  });
}
const DOC_TRANSFORMS = docTransforms();

function WSTransformMenu({ open, onClose, doc, onPickTransform }) {
  if (!open) return null;
  const transforms = docTransforms();   // live projection of the CV_AI skill registry
  return (
    <div className="ws-transform-menu" onClick={e => e.stopPropagation()}>
      <div className="ws-transform-head">Whole-doc transforms</div>
      {transforms.map(t => (
        <button key={t.id} className="ws-transform-item" onClick={() => onPickTransform(t)}>
          <strong>{t.label}</strong>
          {t.sub && <span className="ws-transform-sub">{t.sub}</span>}
        </button>
      ))}
    </div>
  );
}

// ============================================================
// CV_AI capability registration — THE TOOL SET. Each generative move is a
// registered, parametric capability (id == target.kind, so dispatch is the
// catalogue). run() owns build→complete→parse here because it needs the
// composer's prompt helpers (blockShapeDoc, pageContextSummary, ensureSection)
// — exactly as CV_REGISTRY built-ins carry their render(). Provider + context
// + behaviours are resolved by CV_AI.execute and handed in.
// ============================================================
(function registerCapabilities() {
  if (!window.CV_AI) throw new Error('[AIEngine] CV_AI registry not loaded — cannot register capabilities');
  const V = ['voice.conceptv'];
  const CAPS = [
    { id: 'insert.block',        name: 'Insert block',        family: 'deck',    surfaces: ['deck', 'brochure'], icon: 'plus-square',  run: a => viInsertBlock(a.doc, a.target, a.params.count || 3, a.brief, a.provider) },
    { id: 'alternate.block',     name: 'Alternate block',     family: 'deck',    surfaces: ['deck', 'brochure'], icon: 'shuffle',      run: a => viAlternateBlock(a.doc, a.target, a.params.count || 3, a.brief, a.provider) },
    { id: 'insert.page',         name: 'Insert page',         family: 'deck',    surfaces: ['deck', 'brochure'], icon: 'file-plus',    run: a => viInsertPage(a.doc, a.target, a.params.count || 3, a.brief, a.provider) },
    { id: 'doc.transform',       name: 'Whole-doc transform', family: 'deck',    surfaces: ['deck', 'brochure', 'wizard'], icon: 'wand', run: a => viDocTransform(a.doc, a.target, a.params.count || 3, a.brief, a.provider) },
    { id: 'theme.generate',      name: 'Generate theme',      family: 'deck',    surfaces: ['deck', 'brochure'], icon: 'palette',      run: a => viThemeGenerate(a.doc, a.target, a.params.count || 3, a.brief, a.provider) },
    { id: 'layout.generate',     name: 'Generate layout',     family: 'deck',    surfaces: ['deck', 'brochure'], icon: 'layout',       run: a => viLayoutGenerate(a.doc, a.target, a.params.count || 3, a.brief, a.provider) },
    { id: 'widget.alternate',    name: 'Alternate widget',    family: 'widget',  surfaces: ['widget'],           icon: 'activity',     run: a => viWidgetAlternate(a.doc, a.target, a.params.count || 3, a.brief, a.provider) },
    { id: 'widget.kpis.regen',   name: 'Regenerate KPIs',     family: 'widget',  surfaces: ['widget'],           icon: 'bar-chart',    run: a => viWidgetKPIsRegen(a.doc, a.target, a.params.count || 3, a.brief, a.provider) },
    { id: 'wizard.step.insert',  name: 'Insert step',         family: 'wizard',  surfaces: ['wizard'],           icon: 'plus-circle',  run: a => viWizardStepInsert(a.doc, a.target, a.params.count || 3, a.brief, a.provider) },
    { id: 'wizard.step.alternate', name: 'Alternate step',    family: 'wizard',  surfaces: ['wizard'],           icon: 'shuffle',      run: a => viWizardStepAlternate(a.doc, a.target, a.params.count || 3, a.brief, a.provider) },
    // field.alternate also composes the parametric `angle` behaviour (the field
    // toolbar's shorter/formal/specific resolve through it).
    { id: 'field.alternate',     name: 'Alternate field',     family: 'field',   surfaces: ['*'], behaviours: ['voice.conceptv', 'angle'], icon: 'type', run: a => viFieldAlternate(a.doc, a.target, a.params.count || 3, a.brief, a.provider) },
  ];
  for (const c of CAPS) {
    window.CV_AI.register({
      id: c.id, name: c.name, layer: 'capability', family: c.family,
      surfaces: c.surfaces, behaviours: c.behaviours || V, provider: 'claude',
      params: { count: 3 }, icon: c.icon, provenance: 'built-in', run: c.run,
      description: c.name + ' — a Vi generative move on the ' + c.family + ' surface.',
    }, { silent: true });
  }
})();

// ============================================================
// Public exports
// ============================================================

window.WS_AI = {
  applyDiff,
  describeDiff,
  ensureSection,
  generateCandidates,
  generateCandidatesStream,
  classifyIntent,
  generateEdit,
  computeSuggestions,
  viSuggest,
  extractTemplate,
  materializeTemplate,
  invertDiff,
  bridge: BRIDGE,
  useBridgeDoc,
  get cache() { return PROMPT_CACHE; },
};

// ============================================================
// Prompt cache — same prompt within 60s reuses result
// ============================================================

const PROMPT_CACHE = {
  store: new Map(), // hash -> { value, at }
  ttl: 60_000,
  hash(s) {
    let h = 0; const str = String(s);
    for (let i = 0; i < str.length; i++) {
      h = ((h << 5) - h + str.charCodeAt(i)) | 0;
    }
    return String(h);
  },
  get(prompt) {
    const k = PROMPT_CACHE.hash(prompt);
    const e = PROMPT_CACHE.store.get(k);
    if (!e) return null;
    if (Date.now() - e.at > PROMPT_CACHE.ttl) { PROMPT_CACHE.store.delete(k); return null; }
    return e.value;
  },
  set(prompt, value) {
    const k = PROMPT_CACHE.hash(prompt);
    PROMPT_CACHE.store.set(k, { value, at: Date.now() });
    // bound to 200 entries
    if (PROMPT_CACHE.store.size > 200) {
      const oldest = [...PROMPT_CACHE.store.keys()][0];
      PROMPT_CACHE.store.delete(oldest);
    }
  },
  clear() { PROMPT_CACHE.store.clear(); },
};

async function cachedComplete(prompt, opts) {
  const cached = PROMPT_CACHE.get(prompt);
  if (cached !== null) return cached;
  if (!window.CV_AI) throw new Error('[AIEngine] CV_AI registry not loaded — cannot complete');
  const provider = window.CV_AI.resolveProvider('claude');
  const out = await provider.complete(prompt, opts ? { messages: [{ role: 'user', content: prompt }] } : undefined);
  PROMPT_CACHE.set(prompt, out);
  return out;
}

// ============================================================
// Diff inverse — every diff produces an inverse, so the engine can
// undo/redo independent of React state
// ============================================================

function invertDiff(diff, doc) {
  if (!diff || !doc) return null;
  if (diff.kind === 'batch') {
    // To reverse a batch, reverse each diff against the state right before
    // it was applied. Walk forward to capture intermediate docs, then invert.
    const inverses = [];
    let d = doc;
    for (const sub of (diff.diffs || [])) {
      const inv = invertDiff(sub, d);
      d = applyDiff(d, sub);
      if (inv) inverses.unshift(inv);
    }
    return { kind: 'batch', diffs: inverses };
  }
  switch (diff.kind) {
    case 'block.insert': {
      // Reverse: remove at the inserted index
      return { kind: 'block.remove', pageIdx: diff.pageIdx, secIdx: diff.atIdx };
    }
    case 'block.remove': {
      const sec = doc.pages?.[diff.pageIdx]?.sections?.[diff.secIdx];
      if (!sec) return null;
      return { kind: 'block.insert', pageIdx: diff.pageIdx, atIdx: diff.secIdx, section: clone(sec) };
    }
    case 'block.replace': {
      const cur = doc.pages?.[diff.pageIdx]?.sections?.[diff.secIdx];
      if (!cur) return null;
      return { kind: 'block.replace', pageIdx: diff.pageIdx, secIdx: diff.secIdx, section: clone(cur) };
    }
    case 'block.update': {
      const cur = doc.pages?.[diff.pageIdx]?.sections?.[diff.secIdx];
      if (!cur) return null;
      // Capture the prior values of all keys touched
      const restore = {};
      for (const k of Object.keys(diff.dataPatch || {})) restore[k] = clone(cur.data?.[k]);
      return { kind: 'block.update', pageIdx: diff.pageIdx, secIdx: diff.secIdx, dataPatch: restore };
    }
    case 'page.insert': {
      return { kind: 'page.remove', pageIdx: diff.atIdx };
    }
    case 'page.remove': {
      const p = doc.pages?.[diff.pageIdx];
      if (!p) return null;
      return { kind: 'page.insert', atIdx: diff.pageIdx, page: clone(p) };
    }
    case 'page.update': {
      const p = doc.pages?.[diff.pageIdx];
      if (!p) return null;
      const restore = {};
      for (const k of Object.keys(diff.patch || {})) restore[k] = clone(p[k]);
      return { kind: 'page.update', pageIdx: diff.pageIdx, patch: restore };
    }
    case 'doc.update': {
      const restore = {};
      for (const k of Object.keys(diff.patch || {})) restore[k] = clone(doc[k]);
      return { kind: 'doc.update', patch: restore };
    }
    case 'widget.update': {
      const restore = {};
      for (const k of Object.keys(diff.patch || {})) restore[k] = clone(doc[k]);
      return { kind: 'widget.update', patch: restore };
    }
    case 'widget.data': {
      const restore = {};
      for (const k of Object.keys(diff.dataPatch || {})) restore[k] = clone(doc.data?.[k]);
      return { kind: 'widget.data', dataPatch: restore };
    }
    case 'wizard.step.insert': {
      return { kind: 'wizard.step.remove', stepIdx: diff.atIdx };
    }
    case 'wizard.step.remove': {
      const s = doc.steps?.[diff.stepIdx];
      if (!s) return null;
      return { kind: 'wizard.step.insert', atIdx: diff.stepIdx, step: clone(s) };
    }
    case 'wizard.step.update': {
      const s = doc.steps?.[diff.stepIdx];
      if (!s) return null;
      const restore = {};
      for (const k of Object.keys(diff.patch || {})) restore[k] = clone(s[k]);
      return { kind: 'wizard.step.update', stepIdx: diff.stepIdx, patch: restore };
    }
  }
  return null;
}

// ============================================================
// Streaming candidates — fires N independent Vi calls in parallel
// and emits each as it lands. Falls back to the one-shot version.
// ============================================================

async function generateCandidatesStream({ doc, target, count = 3, brief = '', onCandidate, onDone, onError }) {
  if (!doc || !target) { onDone?.(); return; }

  // For some target kinds, a single multi-output prompt makes more sense
  // (e.g. KPI sets that need to differ from each other). For block-level
  // operations, parallel single-shot calls give faster perceived performance.
  const PARALLEL_TARGETS = new Set([
    'insert.block', 'alternate.block', 'insert.page',
    'wizard.step.insert', 'wizard.step.alternate', 'field.alternate',
  ]);

  if (PARALLEL_TARGETS.has(target.kind)) {
    const promises = [];
    for (let i = 0; i < count; i++) {
      const seed = ['practical', 'bold', 'minimal', 'specific'][i] || 'distinct';
      promises.push(generateOneCandidate({ doc, target, brief: brief || '', seed, slotIndex: i })
        .then(c => { if (c) onCandidate?.(c); return c; })
        .catch(e => { onError?.(e); return null; }));
    }
    const results = await Promise.allSettled(promises);
    const out = results.map(r => r.status === 'fulfilled' ? r.value : null).filter(Boolean);
    onDone?.(out);
    return out;
  }

  // Fallback — single batched call
  try {
    const out = await generateCandidates({ doc, target, count, brief });
    for (const c of out) onCandidate?.(c);
    onDone?.(out);
    return out;
  } catch (e) {
    onError?.(e);
    onDone?.([]);
    return [];
  }
}

// Generate ONE candidate for a single target slot, with a seed angle so
// parallel calls return distinct outputs.
async function generateOneCandidate({ doc, target, brief, seed, slotIndex }) {
  // Reuse the existing per-target prompt path but ask for 1 with a flavor seed
  const seededTarget = { ...target };
  const seededBrief = (brief ? brief + ' · ' : '') + `angle: ${seed}, slot ${slotIndex + 1}`;
  const list = await generateCandidates({ doc, target: seededTarget, count: 1, brief: seededBrief });
  return list && list[0] ? list[0] : null;
}

// ============================================================
// Vi-driven dismissible suggestion engine
// ============================================================

const DISMISS_KEY = 'cvstudio:dismissedSuggestions';

function getDismissed() {
  try { return new Set(JSON.parse(localStorage.getItem(DISMISS_KEY) || '[]')); }
  catch { return new Set(); }
}
function dismiss(id) {
  const set = getDismissed(); set.add(id);
  try { localStorage.setItem(DISMISS_KEY, JSON.stringify([...set])); } catch {}
}
function undismiss(id) {
  const set = getDismissed(); set.delete(id);
  try { localStorage.setItem(DISMISS_KEY, JSON.stringify([...set])); } catch {}
}

async function viSuggest({ doc, ctx, count = 4 }) {
  // Combine heuristic suggestions with Vi-generated ones
  const heuristic = computeSuggestions(doc, ctx);
  const dismissed = getDismissed();
  // Filter heuristic
  const visible = heuristic.filter(s => !dismissed.has(s.id));
  // For widget/wizard or simple cases, heuristics are enough
  if (!doc || !doc.pages || doc.pages.length === 0) return visible;
  const pageSummary = (doc.pages || []).slice(0, 8).map((p, i) =>
      `[${i + 1}] ${p.title || p.kind} — ${(p.sections || []).map(s => s.kind).join(', ')}`
    ).join('\n');
    const prompt = `You are Vi, proposing the next ${count} concrete actions a user could take to improve a ConceptV ${doc.type}.

${BRAND_VOICE}

Document title: "${doc.title}"
Current page: ${(ctx?.currentPage ?? 0) + 1} of ${doc.pages.length}
Pages overview:
${pageSummary}

Each suggestion is short (3-7 words), actionable, and corresponds to ONE of these target kinds:
- {"kind":"insert.block","pageIdx":N,"atIdx":M} — propose inserting a block
- {"kind":"alternate.block","pageIdx":N,"secIdx":M} — propose alternates for a specific block
- {"kind":"insert.page","atIdx":N} — propose adding a page at a position
- {"kind":"doc.transform","instruction":"..."} — propose a whole-doc transform

Return ONLY JSON, no prose: {"suggestions":[{"id":"unique-id","label":"3-7 word action","target":{...}}, ...]}`;
  // Loud: a Vi suggestion failure surfaces rather than silently collapsing to
  // heuristics only. If Vi simply returns nothing parsable, heuristics stand.
  const reply = await aiComplete(prompt, typeof provider !== "undefined" ? provider : null, true);
  const parsed = parseJsonLoose(reply);
  if (parsed?.suggestions?.length) {
    const viList = parsed.suggestions
      .filter(s => s.id && !dismissed.has(s.id))
      .slice(0, count)
      .map(s => ({ ...s, source: 'vi' }));
    // Interleave Vi suggestions with heuristic ones; Vi first
    return [...viList, ...visible].slice(0, count + 2);
  }
  return visible;
}

// ============================================================
// Real rendered preview — uses actual block renderers
// ============================================================

function RenderedBlockPreview({ section, scale = 0.5, maxHeight = 140 }) {
  if (!section || !window.WS_BLOCKS) return null;
  const def = window.WS_BLOCKS[section.kind];
  if (!def) return <div className="ws-rendered-fallback">{section.kind}</div>;
  // Render with a no-op setter so contentEditable still appears but doesn't mutate
  const noop = () => {};
  return (
    <div className="ws-rendered-preview" style={{ maxHeight, overflow: 'hidden', position: 'relative' }}>
      <div className="ws-rendered-inner" style={{ transform: `scale(${scale})`, transformOrigin: 'top left', width: `${100 / scale}%`, pointerEvents: 'none' }}>
        {def.render(section.data || def.defaults, noop)}
      </div>
    </div>
  );
}

function RenderedPagePreview({ page, scale = 0.32 }) {
  if (!page) return null;
  return (
    <div className="ws-rendered-page" style={{ maxHeight: 180, overflow: 'hidden', position: 'relative' }}>
      <div style={{ transform: `scale(${scale})`, transformOrigin: 'top left', width: `${100 / scale}%`, pointerEvents: 'none' }}>
        <div style={{font:'700 italic 12px/1 var(--font-display)',color:'var(--accent-bronze)',marginBottom:10}}>{page.title}</div>
        {(page.sections || []).slice(0, 6).map((s, i) => {
          const def = window.WS_BLOCKS?.[s.kind];
          if (!def) return null;
          return <div key={i} style={{marginBottom: 12}}>{def.render(s.data || def.defaults, () => {})}</div>;
        })}
      </div>
    </div>
  );
}

window.WSRenderedBlockPreview = RenderedBlockPreview;
window.WSRenderedPagePreview = RenderedPagePreview;
window.WS_AI.viSuggest = viSuggest;
window.WS_AI.dismissSuggestion = dismiss;
window.WS_AI.undismissSuggestion = undismiss;
window.WS_AI.getDismissed = getDismissed;

// ============================================================
// Workshop docs store — global subscribable copy of all docs,
// so cross-doc embeds (widget-in-deck, wizard-in-deck) update live
// when the source doc is edited.
// ============================================================

const DOCS_STORE = {
  docs: [],
  listeners: new Set(),
  set(docs) {
    DOCS_STORE.docs = docs || [];
    DOCS_STORE.notify();
  },
  notify() { DOCS_STORE.listeners.forEach(fn => fn(DOCS_STORE.docs)); },
  subscribe(fn) { DOCS_STORE.listeners.add(fn); return () => DOCS_STORE.listeners.delete(fn); },
  get(id) { return DOCS_STORE.docs.find(d => d.id === id); },
  byType(t) { return DOCS_STORE.docs.filter(d => d.type === t); },
};

function useWSDocs() {
  const [docs, setDocs] = useState_ai(DOCS_STORE.docs);
  useEffect_ai(() => DOCS_STORE.subscribe(setDocs), []);
  return docs;
}

window.WS_DOCS = DOCS_STORE;
window.useWSDocs = useWSDocs;

// ============================================================
// Workspace variables — a global key/value pool any doc can reference
// via {{key}} placeholders. Updating a value updates every doc that
// references it, instantly.
// ============================================================

const VARS_STORE = {
  vars: [], // [{key, label, value, kind, color?}]
  listeners: new Set(),
  set(vars) { VARS_STORE.vars = vars || []; VARS_STORE.notify(); },
  setOne(key, patch) {
    const idx = VARS_STORE.vars.findIndex(v => v.key === key);
    if (idx >= 0) VARS_STORE.vars[idx] = { ...VARS_STORE.vars[idx], ...patch };
    else VARS_STORE.vars.push({ key, label: key, value: '', kind: 'text', ...patch });
    VARS_STORE.notify();
  },
  remove(key) {
    VARS_STORE.vars = VARS_STORE.vars.filter(v => v.key !== key);
    VARS_STORE.notify();
  },
  notify() {
    VARS_STORE.listeners.forEach(fn => fn(VARS_STORE.vars));
    // Also persist via the App-provided callback if available
    if (VARS_STORE._save) VARS_STORE._save(VARS_STORE.vars);
  },
  subscribe(fn) { VARS_STORE.listeners.add(fn); return () => VARS_STORE.listeners.delete(fn); },
  values() {
    const out = {};
    VARS_STORE.vars.forEach(v => { out[v.key] = v.value; });
    return out;
  },
  bindSave(fn) { VARS_STORE._save = fn; },
};

function substituteVars(text, vars) {
  if (typeof text !== 'string' || !text.includes('{{')) return text;
  const map = vars && vars.length ? vars.reduce((m, v) => (m[v.key] = v.value, m), {}) : VARS_STORE.values();
  return text.replace(/\{\{(\w+)\}\}/g, (_, key) => map[key] != null ? String(map[key]) : `{{${key}}}`);
}

function useWSVars() {
  const [vars, setVars] = useState_ai(VARS_STORE.vars);
  useEffect_ai(() => VARS_STORE.subscribe(setVars), []);
  return vars;
}

window.WS_VARS = VARS_STORE;
window.useWSVars = useWSVars;
window.substituteVars = substituteVars;

// Count how many times each variable key is referenced across all docs.
function countVarReferences() {
  const docs = (window.WS_DOCS?.docs) || [];
  const blob = JSON.stringify(docs);
  const counts = {};
  for (const v of VARS_STORE.vars) {
    const re = new RegExp('\\{\\{' + escapeRegex(v.key) + '\\}\\}', 'g');
    const m = blob.match(re);
    counts[v.key] = m ? m.length : 0;
  }
  // Also count which docs each is in (not just total occurrences)
  const docCounts = {};
  for (const v of VARS_STORE.vars) {
    docCounts[v.key] = (docs || []).filter(d => JSON.stringify(d).includes('{{' + v.key + '}}')).length;
  }
  return { counts, docCounts };
}
window.WS_VARS.countReferences = countVarReferences;

// Vi-audit: scan all docs, find values worth promoting to workspace variables.
async function auditWorkspaceVariables() {
  const docs = (window.WS_DOCS?.docs) || [];
  if (!docs.length) return { variables: [] };
  // Build a compact corpus: every string value across all docs, with source path
  const corpus = [];
  function walk(node, path) {
    if (typeof node === 'string' && node.trim() && !/^\{\{\w+\}\}$/.test(node)) {
      corpus.push({ path, value: node });
    } else if (Array.isArray(node)) {
      node.forEach((v, i) => walk(v, path + '[' + i + ']'));
    } else if (node && typeof node === 'object') {
      for (const k of Object.keys(node)) {
        if (k === 'id' || k === 'createdAt') continue;
        walk(node[k], path + '.' + k);
      }
    }
  }
  docs.forEach(d => walk(d, d.title || d.id));
  // Cap to first ~150 strings, sorted by length descending (real content first)
  const sample = corpus.slice().sort((a, b) => b.value.length - a.value.length).slice(0, 150);
  const existingKeys = VARS_STORE.vars.map(v => v.key).join(', ');
  const prompt = `You are Vi, scanning a ConceptV workspace to find values worth promoting to workspace variables.

${BRAND_VOICE}

Existing variables (don't duplicate): ${existingKeys || '(none)'}

A subset of strings from across the workspace (path → value):
${sample.map(c => `- ${c.path.slice(0, 60)} → ${c.value.slice(0, 80)}`).join('\n')}

Find 3-8 RECURRING or HIGH-VALUE strings that appear multiple times OR are clearly the kind of thing a user would want to swap globally (proper nouns, audience labels, urls, prices, percentages, primary product names). Skip structural strings, UI copy, button labels.

Respond ONLY as JSON: {"variables":[{"key":"kebab_case_key","label":"Human Label","value":"the current most common value","kind":"text|number|url|color","rationale":"one-line why"}]}`;
  // Loud: an audit failure surfaces rather than silently returning no variables.
  const reply = await aiComplete(prompt, typeof provider !== "undefined" ? provider : null, true);
  const parsed = parseJsonLoose(reply);
  return { variables: Array.isArray(parsed?.variables) ? parsed.variables : [] };
}
window.WS_VARS.audit = auditWorkspaceVariables;
window.WSCandidateGallery = WSCandidateGallery;
window.WSDiffCard = WSDiffCard;
window.WSTransformMenu = WSTransformMenu;
window.DOC_TRANSFORMS = DOC_TRANSFORMS;

// ============================================================
// Per-field regen — global tethered toolbar
// ============================================================
// Any input/contentEditable can opt-in by calling:
//   window.WS_FIELD.activate({ rect, value, onApply, blockKind, fieldName, blockData })
//   window.WS_FIELD.deactivate()
// On click, the toolbar invokes WS_FIELD.regenHandler(info) — Workshop wires
// this up to open its candidate gallery.

const FIELD = {
  active: null,
  regenHandler: null,
  listeners: new Set(),
  activate(info) { FIELD.active = info; FIELD.notify(); },
  deactivate() { FIELD.active = null; FIELD.notify(); },
  setRegenHandler(fn) { FIELD.regenHandler = fn; },
  subscribe(fn) { FIELD.listeners.add(fn); return () => FIELD.listeners.delete(fn); },
  notify() { FIELD.listeners.forEach(fn => fn(FIELD.active)); },
};
window.WS_FIELD = FIELD;

function WSFieldToolbar() {
  const [active, setActive] = useState_ai(FIELD.active);
  const [rect, setRect] = useState_ai(null);
  useEffect_ai(() => FIELD.subscribe(setActive), []);

  // Re-measure rect of the active element on scroll / resize, and follow it
  useEffect_ai(() => {
    if (!active?.el) {
      setRect(active?.rect || null);
      return;
    }
    function measure() {
      try { setRect(active.el.getBoundingClientRect()); }
      catch { setRect(active.rect || null); }
    }
    measure();
    const opts = { passive: true, capture: true };
    window.addEventListener('scroll', measure, opts);
    window.addEventListener('resize', measure);
    const ro = new ResizeObserver(measure);
    try { ro.observe(active.el); } catch {}
    const id = setInterval(measure, 400); // catch transform/layout shifts
    return () => {
      window.removeEventListener('scroll', measure, opts);
      window.removeEventListener('resize', measure);
      try { ro.disconnect(); } catch {}
      clearInterval(id);
    };
  }, [active?.el]);

  if (!active || !rect) return null;

  function fire(angle, e) {
    e?.preventDefault(); e?.stopPropagation();
    if (FIELD.regenHandler) FIELD.regenHandler({ ...active, angle });
    FIELD.deactivate();
  }

  function promoteToVar(e) {
    e?.preventDefault(); e?.stopPropagation();
    const cur = (active.value || '').toString();
    const suggested = cur.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '').slice(0, 30) || 'var';
    const key = prompt('Variable key (will become {{' + suggested + '}}):', suggested);
    if (!key) { FIELD.deactivate(); return; }
    const cleanKey = key.toLowerCase().replace(/[^a-z0-9_]+/g, '_').replace(/^_|_$/g, '');
    if (!cleanKey) { FIELD.deactivate(); return; }
    window.WS_VARS?.setOne(cleanKey, {
      key: cleanKey,
      label: cleanKey.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      value: cur,
      kind: 'text',
    });
    // Replace the field with the placeholder
    active.onApply?.('{{' + cleanKey + '}}');
    FIELD.deactivate();
    window.dsaToast?.(`Promoted to variable: {{${cleanKey}}}`);
  }

  // Position above the field; fall back below if too close to viewport top
  const top = rect.top > 60 ? rect.top - 36 : rect.bottom + 8;
  const left = Math.max(8, Math.min(window.innerWidth - 360, rect.left));

  return (
    <div
      className="ws-field-tools"
      style={{ position: 'fixed', top, left, zIndex: 80 }}
      onMouseDown={e => e.preventDefault()}>
      <button onMouseDown={(e) => fire('different', e)} title="3 alternative versions">
        <ViShape size={11}/> alternates
      </button>
      <span className="ws-field-divider"/>
      <button className="ws-field-mini" onMouseDown={(e) => fire('shorter', e)} title="Shorter version">shorter</button>
      <button className="ws-field-mini" onMouseDown={(e) => fire('formal', e)} title="More formal">formal</button>
      <button className="ws-field-mini" onMouseDown={(e) => fire('specific', e)} title="More specific / concrete">specific</button>
      <span className="ws-field-divider"/>
      <button className="ws-field-mini" onMouseDown={promoteToVar} title="Promote to workspace variable — reuse this value across every doc">→ var</button>
    </div>
  );
}

// Bind plain input/textarea to the field toolbar — for builders that don't
// use the contentEditable Edit component.
function bindFieldRegen(el, getValue, onApply, meta) {
  if (!el) return () => {};
  function onFocus() {
    const rect = el.getBoundingClientRect();
    window.WS_FIELD?.activate({ rect, el, value: getValue(), onApply, ...(meta || {}) });
  }
  function onBlur() {
    setTimeout(() => {
      const ae = document.activeElement;
      if (!ae?.closest?.('.ws-field-tools')) window.WS_FIELD?.deactivate();
    }, 150);
  }
  el.addEventListener('focus', onFocus);
  el.addEventListener('blur', onBlur);
  return () => {
    el.removeEventListener('focus', onFocus);
    el.removeEventListener('blur', onBlur);
  };
}

window.WSFieldToolbar = WSFieldToolbar;
window.WS_FIELD.bindFieldRegen = bindFieldRegen;
