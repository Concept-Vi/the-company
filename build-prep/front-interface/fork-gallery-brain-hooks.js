/*
 * fork-gallery-brain-hooks.js — the loadable-brain + route-back hooks for the gallery face (PER-UNIT mount).
 *
 * Owner: fork (ch-8djrpmsl). Self-wiring module projection includes in surface/app (the same-origin host),
 * alongside wildcard-gallery-binder.js. DNA owns the LOOK (re-skin the classes below); fork owns the WIRE.
 *
 * REUSE-DON'T-PARALLEL (2026-06-17): the brain-turn engine (the /api/claude/turn NDJSON stream + per-address
 * session continuity + the /api/territory/write route-back) now lives ONCE in fork-brain-core.js
 * (window.forkBrainCore). This file is the PER-UNIT mount (bind a brain to a rendered gallery unit, keyed by
 * its source address); fork-v-brain.js is the EVERY-PAGE mount (the V/RHM, keyed by the live aim). Both share
 * the same core — there is exactly one brain-turn implementation. LOAD ORDER: fork-brain-core.js FIRST.
 *
 * THE TWO HOOKS:
 *   HOOK 1 — gallery:rendered → bind the loadable brain to the rendered unit, keyed by detail.source
 *     (= code:// per projection's contract; resolved by territory_for's corpus-record leg server-side).
 *   HOOK 2 — gallery:direction → group by element_id → route-back the write (→ suite.mark at the sub-address).
 *
 * VERIFICATION-STATE: contracts confirmed ({init|text|tool|done|error}, gallery:rendered {element,address,
 * source,record}, gallery:direction item). On-surface use-verification is projection's per THE BAR. No green-paint.
 *
 * DEPENDS: fork-brain-core.js (window.forkBrainCore). POST /api/claude/turn (bridge._claude_stream).
 *   POST /api/territory/write (→ runtime.territory.territory_write; bridge route is a PROPOSED diff).
 */
(function () {
  function core() {
    const c = window.forkBrainCore;
    if (!c) throw new Error('fork-gallery-brain-hooks: forkBrainCore not loaded (load fork-brain-core.js first)');
    return c;
  }

  // ── HOOK 1: bind the loadable brain to a rendered unit, keyed by its source address ──
  // Adds an "ask Claude Code about this" affordance; the conversation context = territory_for(source)
  // (the bridge resolves it). DNA re-skins .brain-ask / .brain-panel / .brain-reply.
  function bindBrain(rootEl, sourceAddr) {
    if (!rootEl || rootEl.nodeType !== 1 || rootEl.dataset.brainBound) return;  // real ELEMENT only (document has no .dataset)
    rootEl.dataset.brainBound = '1';

    const ask = document.createElement('button');
    ask.className = 'brain-ask';                  // DNA RE-SKINS
    // OPERATOR-LAW: human meaning only — never the tool name ("Claude Code") nor the raw address (sourceAddr
    // is code://… — it rides server-side as the brain's context handle, never shown to the operator).
    ask.textContent = 'Ask about this';
    ask.title = 'Ask the right-hand-man about this';
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
        if (q) core().talk(panel.querySelector('.brain-reply'), sourceAddr, q);   // the ONE brain-turn engine
      };
      panel.querySelector('.brain-send').addEventListener('click', send);
    });
  }

  // ── SELF-WIRE HOOK 1: bind after DNA signals rendered (race-safe). detail.source = code:// (projection's
  // contract) = the brain's context handle. Bind at the unit root (detail.element); NEVER fall back to document. ──
  window.addEventListener('gallery:rendered', (e) => {
    const d = e.detail || {};
    const source = d.source || d.address;          // source preferred (canonical code://); address is the run:// record
    const root = d.element || d.root;
    if (source && root && root.nodeType === 1) bindBrain(root, source);
    if (Array.isArray(d.elements)) {
      d.elements.forEach(({ el, address }) => bindBrain(el, address || source));
    }
  });

  // ── SELF-WIRE HOOK 1b: DECISION cards (decision-surface, 2026-06-18 — projection's whole-screen verify
  // caught that HOOK 1 fired only on gallery:rendered, so a decision card got the pre-filled explanation but
  // NO interactive follow-up, and the V handle is COVERED by the card overlay). REUSE-DON'T-PARALLEL: bind the
  // SAME in-card Ask on DNA's `decision:rendered`, keyed by the decision's CANONICAL address — talk(decisionAddr)
  // resolves the decision's territory (meaning/options/state, verified operator-grade) so a follow-up is
  // grounded ON the decision: the RHM "walks through it WITH" the operator (Tim's frame), beyond the one-shot
  // explanation. Mirrors the gallery:rendered contract (detail.element + the address); the address is the BARE
  // canonical decision://global/<id> (the decision IDENTITY — same handle the take targets, NOT a #elem). Harmless
  // before DNA's card lands (the event simply doesn't fire yet); READY the instant it emits. NEVER fall back to document.
  window.addEventListener('decision:rendered', (e) => {
    const d = e.detail || {};
    const addr = d.address || d.decision || d.source;   // the decision's canonical address (decision://global/<id>)
    const root = d.element || d.root;
    if (addr && root && root.nodeType === 1) bindBrain(root, addr);
  });

  // ── HOOK 2: route-back write. gallery:direction → batch per microtask → forkBrainCore.writeDirections
  // (groups by element_id, POSTs /api/territory/write, emits gallery:rerender / gallery:write-error). ──
  let _pending = [];
  function flush() { const items = _pending; _pending = []; core().writeDirections(items); }
  window.addEventListener('gallery:direction', (e) => {
    if (!e.detail || !e.detail.element_id) return;
    _pending.push(e.detail);
    if (_pending.length === 1) Promise.resolve().then(flush);
  });

  // ── HOOK 2b: the decision-card TAKE rides the UNIFIED gallery:verb envelope (galleryBinder.decide →
  // emitVerb('annotate', canonical, {is_decision_take, value, mark_type})), NOT gallery:direction — so it had
  // NO consumer (the take was emitted but never written → a decided decision read pending forever; found in
  // DNA's cutover regression round, 2026-06-18). Consume the take HERE → the decision_take write. Maps the verb
  // envelope → territory_write's item shape: element_id = the CANONICAL decision address (aim_address — decide()
  // already validated it's decision://<frame>/<id>, fork's single-source form), type='decision_take' (territory_
  // write reads `type` as the mark_type), value = the chosen option label. ONLY the take (is_decision_take) is
  // taken here — the annotate verbs (comment/reaction/favour) still dual-emit gallery:direction above, so they
  // are NOT double-written. (When the binder drops the gallery:direction back-compat, migrate those here too.)
  window.addEventListener('gallery:verb', (e) => {
    const d = e.detail || {};
    if (!d.payload || !d.payload.is_decision_take || !d.aim_address) return;   // take-only; annotate stays on gallery:direction
    const item = { element_id: d.aim_address, type: 'decision_take', value: d.payload.value };
    if (d.payload.by != null) item.by = d.payload.by;
    _pending.push(item);
    if (_pending.length === 1) Promise.resolve().then(flush);
  });

  window.forkBrainHooks = { bindBrain };          // expose for explicit binding if projection prefers
})();
