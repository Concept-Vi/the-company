// atomicity/vi-brain.js
// ============================================================================
// VI_BRAIN — Vi's mind inside AtomiCity.
//
// This is the "version of you" the brief asks for: an agent that KNOWS the whole
// system (because it reads the same registries the Atlas does), INTERPRETS intent
// rather than waiting for exact commands, ACTS on the interface (navigate, open,
// propose real changes), SOLICITS feedback fluidly, and LEARNS — folding what it
// learns back into the one AI registry so it genuinely gets better at operating.
//
// It owns no UI. It exposes:
//   • systemPrompt(ctx)         — composes Vi's knowledge (census + context + learnings)
//   • interpret(message, ctx)    — model turn → { say, actions[], proposal?, followup }
//   • suggestions(ctx)           — proactive, context-aware quick moves
//   • quickCommands(ctx)         — short commands projected for the command bar
//   • learn(feedback, ctx)       — distil feedback → live CV_AI behaviour + CV_HOST proposal
//   • memory() / forget(id)      — the learned-preference store
//
// THE ACTIONS PROTOCOL: Vi may return actions the host (AtomiCity.jsx) executes
// via window.ATOMICITY.act(action). Vi can do on the screen what the user can —
// open any node, search, run a capability, stage a change. The vocabulary lives
// HERE (single source); the host implements each verb.
// ============================================================================

(function () {
  'use strict';
  const AI = window.CV_AI;
  if (!AI) throw new Error('[VI_BRAIN] CV_AI not loaded');

  const LS_MEM = 'atomicity:learnings';

  // ==========================================================================
  // ACTION VOCABULARY — the verbs Vi can perform on the interface. The host
  // implements each; this is the contract both sides read.
  // ==========================================================================
  const ACTIONS = {
    open:      { desc: 'Open a node in the Atlas detail pane.', args: 'node (atlas id)' },
    search:    { desc: 'Run a search across the whole system.', args: 'q' },
    expand:    { desc: 'Expand a section/group in the tree.', args: 'node' },
    run:       { desc: 'Run a CV_AI capability by id.', args: 'capability, params' },
    propose:   { desc: 'Stage a single-sourced repo change via CV_HOST.', args: 'kind, title, rationale, payload' },
    connect:   { desc: 'Prompt the user to connect a file runtime (Bridge).', args: '' },
    highlight: { desc: 'Briefly highlight a node so the user can see it.', args: 'node' },
    ingest:    { desc: 'Open Sources and (if given text) add + deeply analyse it as source material.', args: 'text?' },
    explore:   { desc: 'Open Explore to generate style directions for an element.', args: 'element?' },
    restyle:   { desc: 'Apply a live style to the element the user has SELECTED on screen (the picked element). Use the same recipe keys as a css style.', args: 'style:{bg,fg,radius,shadow,border,borderWidth,weight,font,padding,tracking}' },
    pageshot:  { desc: 'Capture a screenshot of the whole page (use when you need to see the full layout, not just the selected element).', args: '' },
  };

  // ==========================================================================
  // MEMORY — learned preferences. Stored locally; rehydrated into CV_AI at boot
  // so they take effect immediately; proposed to CV_HOST for permanence.
  // ==========================================================================
  function memory() { try { return JSON.parse(localStorage.getItem(LS_MEM) || '[]'); } catch { return []; } }
  function saveMemory(arr) { try { localStorage.setItem(LS_MEM, JSON.stringify(arr)); } catch {} }

  // register one learned behaviour into CV_AI live (immediate effect)
  function registerLearned(entry) {
    AI.register({
      id: entry.id, name: entry.label, layer: 'behaviour', family: 'learned',
      description: 'Learned from feedback: ' + entry.label,
      text: entry.instruction,
      surfaces: entry.surface ? [entry.surface] : undefined,
      provenance: 'vi-learned', icon: 'sparkles',
    }, { silent: true });
  }
  function rehydrate() {
    for (const e of memory()) { try { registerLearned(e); } catch {} }
  }

  // applicable learnings for the current surface (global + surface-matched)
  function applicableLearnings(surface) {
    return memory().filter(e => !e.surface || e.surface === surface);
  }

  // ==========================================================================
  // SYSTEM KNOWLEDGE — the prompt that makes Vi know everything without being
  // told. Census of the live system + the architecture rules + current context
  // + applicable learnings + the action protocol.
  // ==========================================================================
  const ARCHITECTURE = `AtomiCity is the interface to the ConceptV Design System — a unified generative system whose ONE law is: everything is defined once and referenced everywhere (no second home for any value). It has four single-source registries, all the same shape (register/resolve/query):
• Tokens — colour/space/type/depth values in CSS, layered L0 primitives → L1 roles → L2 component tokens. A new colour = a new L0 primitive + an L1 role; consumers reference the role.
• CV_REGISTRY — Types (token→atom→block→system→surface→doc→template), single-inheritance, rendered by one engine under axis-dials (theme/density/surface).
• CV_AI — everything you (Vi) can do: providers, behaviours (the voice is voice.conceptv — never inline a voice string), skills, capabilities (id == the move), context resolvers.
• CV_HOST — the Bridge: how you reach the repo. A serializer turns a registry mutation into the EXACT source for its one home file; every change is staged for review, then written to disk when a runtime is connected.
To change anything: find its one home, edit there, reference elsewhere. To add: register it in the right registry (or propose a token/card/Type/capability via CV_HOST) — never hand-lay a copy.`;

  function systemPrompt(ctx) {
    const c = window.ATLAS ? window.ATLAS.census() : {};
    const node = ctx && ctx.node;
    const learn = applicableLearnings(ctx && ctx.surface);
    const lines = [
      'You are Vi — the resident agent of AtomiCity. You are proactive, concise, and you know this system cold. You speak in sentence case, second person, no exclamation marks, no emoji.',
      '',
      ARCHITECTURE,
      '',
      'LIVE SYSTEM CENSUS (what currently exists — read it, never ask the user for it):',
      JSON.stringify(c),
      '',
      node ? `THE USER IS LOOKING AT: "${node.label}" (${node.kind})${node.data ? ' — ' + JSON.stringify(node.data).slice(0, 240) : ''}.` : 'The user is at the AtomiCity home.',
    ];
    if (ctx && ctx.picked) {
      const p = ctx.picked;
      lines.push('', 'THE USER HAS SELECTED A REAL ELEMENT ON SCREEN (this is the focus). Its current live styles, layout and box model are below — you already know them, so NEVER read pixel values, padding, or class names back to the user.',
        JSON.stringify({ role: p.role, tag: p.tag, text: p.text, styles: p.styles, layout: p.layout, box: p.box, children: p.children }),
        'When they ask to change it: JUST DO IT. Return a `restyle` action (keys: bg, fg, radius, shadow, border, borderWidth, weight, font, padding, margin, gap, lineHeight, textAlign, fontSize, width, height, opacity, letterSpacing; token names like "--accent-gold"/"--s-4" or raw CSS) — it applies to the real element instantly via the override layer and is captured as a before→after image under your reply. Use the layout/box info to choose the right property (e.g. tighten spacing → padding/gap). Keep prose to ONE short, warm line, e.g. "Tightened it up — better?". Do NOT explain what you did, list values, or ask a clinical multi-option question in prose.',
        'Instead put the next moves in `options` (rendered as buttons under your message). Make them DYNAMIC and relevant to what just happened — e.g. for a spacing change: {"label":"A bit more","say":"a little more"}, {"label":"Ease off","say":"slightly less"}, {"label":"Apply to all","say":"apply this to every "+role}, {"label":"Make a variant","say":"make this a reusable density variant"}. "Apply to all" / "Make a variant" should, when clicked, lead you to `propose` a type or token so the whole system can scale; a single change is already applied live (that’s "apply here").');
    }
    if (learn.length) {
      lines.push('', 'WHAT YOU HAVE LEARNED the user prefers (honour these):');
      for (const e of learn) lines.push('• ' + e.instruction);
    }
    lines.push(
      '',
      'HOW TO RESPOND. Reply with a short prose answer (2–4 sentences, **bold** for emphasis, `code` for ids/tokens). Then, if and only if doing something would help, append ONE fenced block:',
      '```atomicity',
      '{ "actions": [ {"type":"open","node":"<atlas id>"} , {"type":"restyle","style":{...}} , {"type":"propose","kind":"css.token|ai.entry|type|card","title":"...","rationale":"...","payload":{...}} ], "options": [ {"label":"≤3 words","say":"the message to send if clicked"} ], "followup": "optional one short line" }',
      '```',
      'Action verbs available: ' + Object.keys(ACTIONS).join(', ') + '.',
      '`options` are quick-reply buttons shown under your message; prefer them over a long prose question. Keep labels ≤3 words, evenly weighted, and contextual to what just happened. Always offer them after acting on a picked element.',
      'Prefer to DO over describe: if the user names a thing, open it; if they imply a change, propose it (a real payload the serializer can write); if they ask "what/how", answer AND offer the next move as a followup.',
      'For propose payloads: css.token = {name,value,role}; ai.entry = a full CV_AI entry {id,name,layer,family,...}; type = a CV_REGISTRY type; card = {name,group,subtitle,body}. Never invent fields the serializer does not read.',
      'Never claim you committed to disk — proposals are staged for review unless a writer is connected. Be honest about that boundary.',
    );
    return lines.join('\n');
  }

  // ==========================================================================
  // INTERPRET — one Vi turn. Returns prose + parsed actions + an optional staged
  // proposal result + a followup. Loud on model failure (no silent empty).
  // ==========================================================================
  async function interpret(message, ctx, history) {
    const sys = systemPrompt(ctx);
    const msgs = [{ role: 'user', content: sys }];
    for (const h of (history || []).slice(-6)) msgs.push({ role: h.role === 'user' ? 'user' : 'assistant', content: stripHtml(h.text) });
    msgs.push({ role: 'user', content: message });

    const raw = await AI.complete({ messages: msgs });
    const { prose, block } = extractBlock(raw);
    const out = { say: prose || raw, actions: [], followup: null, proposals: [], options: [] };
    if (block) {
      try {
        const parsed = JSON.parse(block);
        out.followup = parsed.followup || null;
        out.options = Array.isArray(parsed.options) ? parsed.options.filter(o => o && o.label && o.say).slice(0, 5) : [];
        for (const a of (parsed.actions || [])) {
          if (a && a.type === 'propose') {
            // stage it through CV_HOST immediately so the user sees a real diff
            try {
              const res = await window.CV_HOST.commit({ kind: a.kind, title: a.title, rationale: a.rationale, payload: a.payload, provenance: 'vi' });
              out.proposals.push({ ...res, title: a.title });
            } catch (e) { out.actions.push({ type: 'note', text: 'Could not stage change: ' + e.message }); }
          } else if (a && ACTIONS[a.type]) {
            out.actions.push(a);
          }
        }
      } catch (e) { /* malformed block — prose still stands */ }
    }
    return out;
  }

  // ==========================================================================
  // SUGGESTIONS — proactive, context-aware. Derived from the current node's
  // kind so Vi always has something useful to offer without being asked.
  // ==========================================================================
  function suggestions(ctx) {
    const node = ctx && ctx.node;
    if (!node || node.kind === 'root') return [
      'Give me a tour of the system',
      'What should I work on first?',
      'Add a new accent colour',
      'What can you do here?',
    ];
    const k = node.kind;
    const L = node.label;
    if (k === 'token' || k === 'token-group' || k === 'token-file')
      return [`Add a token next to ${L}`, `What references ${L}?`, 'Suggest a missing token', 'Check this palette for contrast'];
    if (k === 'component')
      return [`How do I use ${L}?`, `What tokens does ${L} read?`, 'Propose a new component', 'Show me its live demo'];
    if (k === 'card' || k === 'group')
      return [`Explain the "${L}" card`, 'Add a card to this group', 'Reorganise this group', 'What\'s missing here?'];
    if (k === 'ai-entry' || k === 'group' && /capabilit|behaviour|skill|provider|context/i.test(L))
      return [`What does ${L} do?`, 'Add a new capability', 'Teach Vi a new behaviour', 'Trace this capability\'s prompt'];
    if (k === 'type')
      return [`What extends ${L}?`, 'Add a Type that extends this', 'Materialise it under a different axis'];
    if (k === 'runtime' || k === 'serializer' || k === 'change')
      return ['Connect a file runtime', 'Stage a sample change', 'Explain how the Bridge writes to disk'];
    if (k === 'template') return [`Open ${L}`, 'Build a new template', 'What components does it use?'];
    return [`Tell me about ${L}`, 'What can I do here?', 'Suggest an improvement'];
  }

  // short, imperative commands for the command bar (always available + contextual)
  function quickCommands(ctx) {
    const base = [
      { label: 'Tour the system', run: 'Give me a 4-step tour of what AtomiCity contains.' },
      { label: 'What should I do next?', run: 'Audit the system and tell me the single highest-value thing to do next.' },
      { label: 'Add an accent colour', run: 'Propose a new accent colour token that fits the palette.' },
      { label: 'Teach Vi something', run: 'I want to teach you a preference.' },
    ];
    const node = ctx && ctx.node;
    if (node && node.kind === 'token') base.unshift({ label: `Find references to ${node.label}`, run: `What in the system references ${node.label}?` });
    if (node && node.kind === 'component') base.unshift({ label: `How to use ${node.label}`, run: `Show me how to use the ${node.label} component, with a snippet.` });
    return base;
  }

  // ==========================================================================
  // LEARN — turn conversational feedback into a durable preference. Distil it
  // with the model into a crisp instruction, register it LIVE into CV_AI (so the
  // next turn already honours it), persist locally, and propose it to CV_HOST so
  // it becomes a real ai-seed.js behaviour on commit. This is "gets better at
  // operating for me" made single-sourced.
  // ==========================================================================
  async function learn(feedback, ctx) {
    const distillPrompt = `The user is teaching Vi a lasting preference about how to work in their design system. Turn their words into ONE crisp, imperative instruction Vi should follow from now on (max 22 words, sentence case, no preamble). Also give a 3-5 word label.\n\nUser said: "${feedback}"\n\nReply as JSON only: {"label":"...","instruction":"...","scope":"global|surface"}`;
    let label, instruction, scope = 'global';
    try {
      const raw = await AI.complete(distillPrompt);
      const j = JSON.parse(extractBlock(raw).block || raw.slice(raw.indexOf('{')));
      label = j.label; instruction = j.instruction; scope = j.scope || 'global';
    } catch {
      label = feedback.slice(0, 32); instruction = feedback.trim();
    }
    const entry = {
      id: 'vi.learned.' + Date.now().toString(36),
      label, instruction,
      surface: scope === 'surface' ? (ctx && ctx.surface) : null,
      createdAt: Date.now(),
    };
    // live effect
    registerLearned(entry);
    // persist locally
    const mem = memory(); mem.unshift(entry); saveMemory(mem);
    // propose for permanence (staged for review / written if connected)
    let proposal = null;
    try {
      proposal = await window.CV_HOST.commit({
        kind: 'ai.entry',
        title: 'Learned: ' + label,
        rationale: 'Vi learned this preference from your feedback: "' + feedback.slice(0, 120) + '"',
        payload: {
          id: entry.id, name: label, layer: 'behaviour', family: 'learned',
          description: 'Learned from feedback: ' + label,
          text: instruction,
          surfaces: entry.surface ? [entry.surface] : undefined,
          provenance: 'vi-learned', icon: 'sparkles',
        },
        provenance: 'vi',
      });
    } catch (e) { /* staging still recorded locally + live */ }
    return { entry, proposal };
  }
  function forget(id) {
    saveMemory(memory().filter(e => e.id !== id));
    try { AI.remove && AI.remove(id); } catch {}
  }

  // a fluid feedback nudge Vi can offer after acting (the "would it have been
  // better if…" move) — phrased from the last action so it feels specific.
  function feedbackNudge(lastAction) {
    if (!lastAction) return null;
    const map = {
      open: 'Did you want the live preview, or its lineage and references?',
      propose: 'Want me to apply this now, refine the value, or hold it for review?',
      search: 'Too many results, or not what you meant? Tell me how to search better for you.',
      run: 'Was that the angle you wanted? I can re-run it differently if you tell me how.',
    };
    return map[lastAction.type] || 'Would a different approach have served you better here?';
  }

  // ==========================================================================
  // Register AtomiCity's own context resolver + capabilities into CV_AI, so the
  // agent surface is in the one catalogue like every other.
  // ==========================================================================
  function registerSelf() {
    if (AI.get && AI.get('context.atomicity')) return;
    AI.register({
      id: 'context.atomicity', name: 'AtomiCity context', layer: 'context', family: 'context',
      description: 'Projects the live system census + the node the user is viewing into Vi’s prompt context.',
      surfaces: ['atomicity'],
      resolveCtx: (doc, base) => ({
        docType: 'atomicity',
        census: window.ATLAS ? window.ATLAS.census() : null,
        viewing: base && base.node ? { id: base.node.id, label: base.node.label, kind: base.node.kind } : null,
      }),
      provenance: 'built-in', icon: 'atom',
    }, { silent: true });

    AI.register({
      id: 'atomicity.interpret', name: 'Interpret intent', layer: 'capability', family: 'atomicity',
      description: 'Vi’s main turn in AtomiCity — interpret what the user means and return prose + interface actions + staged proposals.',
      surfaces: ['atomicity'], behaviours: ['voice.conceptv'], role: 'text', icon: 'atom',
      provenance: 'built-in', params: {},
      run: (a) => interpret(a.params.message, a.params.ctx, a.params.history),
    }, { silent: true });
    AI.register({
      id: 'atomicity.learn', name: 'Learn a preference', layer: 'capability', family: 'atomicity',
      description: 'Distil conversational feedback into a durable behaviour, register it live, and propose it to the repo so Vi improves permanently.',
      surfaces: ['atomicity'], role: 'text', icon: 'sparkles',
      provenance: 'built-in', params: {},
      run: (a) => learn(a.params.feedback, a.params.ctx),
    }, { silent: true });
  }

  // --- helpers -------------------------------------------------------------
  function extractBlock(text) {
    const m = String(text || '').match(/```(?:atomicity|json)?\s*([\s\S]*?)```/);
    if (!m) return { prose: text, block: null };
    const prose = text.slice(0, m.index).trim() + (text.slice(m.index + m[0].length).trim() ? '\n' + text.slice(m.index + m[0].length).trim() : '');
    return { prose: prose.trim(), block: m[1].trim() };
  }
  function stripHtml(s) { return String(s || '').replace(/<[^>]+>/g, ''); }

  window.VI_BRAIN = {
    ACTIONS, systemPrompt, interpret, suggestions, quickCommands,
    learn, memory, forget, rehydrate, feedbackNudge, registerSelf,
  };

  // boot: register self into CV_AI + rehydrate learnings for immediate effect
  registerSelf();
  rehydrate();
})();
