/*
 * fork-gallery-brain-hooks.js — the loadable-brain + route-back hooks for the gallery face.
 *
 * Owner: fork (ch-8djrpmsl). Segment: the addressed-state + Claude-Code-as-loadable-brain wire.
 * Self-wiring module projection includes in surface/app (the same-origin host), alongside
 * wildcard-gallery-binder.js. DNA owns the LOOK (re-skin the classes below); fork owns the WIRE.
 *
 * THE TWO HOOKS (lead's spec, confirmed contracts):
 *   HOOK 1 — gallery:rendered → bind the loadable brain to the rendered unit/element, keyed by
 *     detail.source (= code:// per projection's contract; resolved by territory_for's corpus-record leg).
 *     "Talk to Claude Code about THIS" → POST /api/claude/turn {prompt, address: source} → stream the reply
 *     in-surface. The brain is the DEFAULT (host Claude via run_turn — capable; NOT the weak 4B engine).
 *   HOOK 2 — gallery:direction (wildcard's binder) → group by element_id → POST the route-back write
 *     (territory_for-write → suite.mark at the sub-address) → signal re-render. Sequenced AFTER hook 1
 *     round-trips (wildcard confirmed the item shapes: {id,type,annotation_type|reaction|score, text?, element_id}).
 *
 * VERIFICATION-STATE: Observed-shape-correct (contracts confirmed: /api/claude/turn NDJSON {init|text|tool|done},
 *   gallery:rendered {address,source,root|elements}, gallery:direction item). NOT yet use-verified on the
 *   surface DOM (awaits projection's mount + the territory_prose bridge diff applied). Meet at the address.
 *
 * DEPENDS: POST /api/claude/turn (exists — bridge._claude_stream; the territory_prose diff makes its context
 *   scheme-agnostic). POST /api/territory/write (PROPOSED to the bridge owner → territory_write).
 */
(function () {
  const CLAUDE_TURN = '/api/claude/turn';        // existing: bridge._claude_stream (NDJSON stream)
  const TERRITORY_WRITE = '/api/territory/write'; // PROPOSED: → runtime.territory.territory_write
  const _sessions = {};                           // address → claude session_id (continue the convo per unit)

  // ── HOOK 1: bind the loadable brain to a rendered unit, keyed by its source address ──
  // Adds an "ask Claude Code about this" affordance; the conversation context = territory_for(source)
  // (the bridge resolves it). DNA re-skins .brain-ask / .brain-panel / .brain-reply.
  function bindBrain(rootEl, sourceAddr) {
    if (!rootEl || rootEl.nodeType !== 1 || rootEl.dataset.brainBound) return;  // real ELEMENT only (document has no .dataset → the old `|| document` fallback crashed here)
    rootEl.dataset.brainBound = '1';

    const ask = document.createElement('button');
    ask.className = 'brain-ask';                  // DNA RE-SKINS
    ask.textContent = 'Ask Claude Code about this';
    ask.title = 'Talk to the loadable brain about ' + sourceAddr;
    rootEl.appendChild(ask);

    ask.addEventListener('click', (e) => {
      e.stopPropagation();
      let panel = rootEl.querySelector(':scope > .brain-panel');
      if (panel) { panel.remove(); return; }      // toggle
      panel = document.createElement('div');
      panel.className = 'brain-panel';            // DNA RE-SKINS
      panel.innerHTML =
        '<div class="brain-reply" aria-live="polite"></div>' +
        '<textarea class="brain-input" placeholder="Ask about this unit…"></textarea>' +
        '<button class="brain-send">send</button>';
      rootEl.appendChild(panel);
      const send = () => {
        const q = panel.querySelector('.brain-input').value.trim();
        if (q) talk(panel.querySelector('.brain-reply'), sourceAddr, q);
      };
      panel.querySelector('.brain-send').addEventListener('click', send);
    });
  }

  // ── The brain turn: POST /api/claude/turn, stream the NDJSON reply into `replyEl` ──
  async function talk(replyEl, address, prompt) {
    replyEl.textContent = '…';
    let acc = '';
    try {
      const body = { prompt, address };
      if (_sessions[address]) body.session_id = _sessions[address];   // continue the per-unit conversation
      const resp = await fetch(CLAUDE_TURN, {
        method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body),
      });
      const reader = resp.body.getReader();
      const dec = new TextDecoder();
      let buf = '';
      for (;;) {
        const { value, done } = await reader.read();
        if (done) break;
        buf += dec.decode(value, { stream: true });
        let nl;
        while ((nl = buf.indexOf('\n')) >= 0) {
          const line = buf.slice(0, nl).trim(); buf = buf.slice(nl + 1);
          if (!line) continue;
          let ev; try { ev = JSON.parse(line); } catch { continue; }
          if (ev.type === 'init' && ev.session_id) _sessions[address] = ev.session_id;
          else if (ev.type === 'text' && ev.text) { acc += ev.text; replyEl.textContent = acc; }
          else if (ev.type === 'tool') { /* optional: show tool activity */ }
          else if (ev.type === 'done') { if (ev.result && !acc) replyEl.textContent = ev.result; }
          else if (ev.type === 'error') { replyEl.textContent = 'brain error: ' + ev.error; }
        }
      }
      if (!acc && replyEl.textContent === '…') replyEl.textContent = '(no reply)';
    } catch (err) {
      replyEl.textContent = 'brain unreachable: ' + (err && err.message || err);   // fail-loud to the surface
    }
  }

  // ── SELF-WIRE HOOK 1: bind after DNA signals rendered (race-safe, same order wildcard's binder uses) ──
  // detail.source = code:// (projection's contract) = the brain's context handle (territory_for resolves it).
  // Bind at the unit root (detail.root); per-element brains are a follow (detail.elements).
  window.addEventListener('gallery:rendered', (e) => {
    const d = e.detail || {};
    const source = d.source || d.address;          // source preferred (canonical code://); address is the run:// record
    // DNA's CONFIRMED emit shape is {element, address, source, record} (g-1781595596) — bind at detail.element,
    // the rendered unit root. d.root kept as a legacy alias. NEVER fall back to `document`: its .dataset is
    // undefined (crashes bindBrain) AND a page-wide "ask" button is wrong. Bind only when root is a real element.
    const root = d.element || d.root;
    if (source && root && root.nodeType === 1) bindBrain(root, source);
    if (Array.isArray(d.elements)) {
      d.elements.forEach(({ el, address }) => bindBrain(el, address || source));
    }
  });

  // ── HOOK 2: route-back write (sequenced after hook 1 round-trips). gallery:direction → group by
  // element_id → POST the write → re-render. Batches per microtask so a burst of directions on one element
  // writes together. ──
  let _pending = [];
  function flushDirections() {
    const items = _pending; _pending = [];
    const byElem = {};
    items.forEach(it => { (byElem[it.element_id] = byElem[it.element_id] || []).push(it); });
    Object.entries(byElem).forEach(([element_id, group]) => {
      fetch(TERRITORY_WRITE, {
        method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ element_id, items: group }),
      }).then(r => r.ok ? r.json() : null)
        .then(() => window.dispatchEvent(new CustomEvent('gallery:rerender', { detail: { element_id } })))
        .catch(err => window.dispatchEvent(new CustomEvent('gallery:write-error',
          { detail: { element_id, error: String(err) } })));   // fail-loud, never silent
    });
  }
  window.addEventListener('gallery:direction', (e) => {
    if (!e.detail || !e.detail.element_id) return;
    _pending.push(e.detail);
    if (_pending.length === 1) Promise.resolve().then(flushDirections);
  });

  window.forkBrainHooks = { bindBrain, talk };   // expose for explicit binding if projection prefers
})();
