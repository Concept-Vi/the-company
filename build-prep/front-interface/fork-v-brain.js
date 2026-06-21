/*
 * fork-v-brain.js — the V / RIGHT-HAND-MAN brain module: ONE persistent loadable brain on EVERY page,
 * whose context is the CURRENT AIM ADDRESS. The every-page generalization of hook-1.
 *
 * Owner: fork (ch-8djrpmsl). Mounted by projection's V-overlay HOST (the draggable bottom-right V).
 * The V host owns the SHELL + the current AIM (page/surface address by default; an element's address when
 * Tim aims the V at it — the bidirectional-address law: Tim points the V at an address, the brain loads AT
 * that address). This module owns the BRAIN: given the host's live aim, it binds + talks + routes-back,
 * reusing forkBrainCore (the ONE brain-turn engine — no second streamer). The brain is REAL Claude Code
 * (PANEL, via /api/claude/turn). FOCUS-vs-PANEL by SCALE (D2) is a registry/handoff seam, not hardcoded here.
 *
 * OPERATOR LAW: the operator NEVER sees code/files/machine names. This module shows only a HUMAN aim label
 * (supplied by the host via getAimLabel) — never the raw address. The address rides server-side
 * (territory_prose(aim) composes the brain's context); the operator reacts to MEANING.
 *
 * MOUNT API (the seam — projection's host calls this):
 *   forkVBrain.attach({
 *     panelEl,        // REQUIRED — the V's expanded panel DOM (the brain renders here; DNA re-skins .v-brain-*)
 *     getAimAddress,  // REQUIRED — () => string : the CURRENT aim address (read at send-time, so it always
 *                     //            talks about whatever the V is pointed at right now)
 *     getAimLabel,    // optional — () => string : a HUMAN label for the aim ("the Heart map", "this control");
 *                     //            NEVER the raw address. Falls back to a generic "this".
 *     placeholder,    // optional — input placeholder text
 *   }) → { ask(prompt), groundedAsk(prompt), direct(item), aimChanged(), destroy() }
 *
 * TWO brain paths (single-source — both live HERE, both SELF-RENDER into .v-brain-reply, no parallel caller):
 *   • ask(prompt)        → STREAMING turn via forkBrainCore /api/claude/turn (the real-Claude-Code path).
 *   • groundedAsk(prompt)→ BLOCKING grounded answer via /api/brain/ask (the role-resolved mind: kimi, ~5s).
 *                          SELF-RENDERS (placeholder → answer) AND returns {ok,source,answer}. The V's send
 *                          button + Enter fire groundedAsk (the grounded mind is the default ask).
 *
 * VERIFICATION-STATE: shape-correct + logic-traced; reuses the verified core. On-surface use-verification
 * (mount in the V, drive on the phone at 390px first) is projection's per THE BAR. No green-paint.
 */
(function () {
  function attach(cfg) {
    cfg = cfg || {};
    const panelEl = cfg.panelEl;
    const getAimAddress = cfg.getAimAddress;
    if (!panelEl || panelEl.nodeType !== 1) throw new Error('forkVBrain.attach: panelEl must be a real element');
    if (typeof getAimAddress !== 'function') throw new Error('forkVBrain.attach: getAimAddress must be a function');
    const getAimLabel = (typeof cfg.getAimLabel === 'function') ? cfg.getAimLabel : null;
    const core = window.forkBrainCore;
    if (!core) throw new Error('forkVBrain.attach: forkBrainCore not loaded (load fork-brain-core.js first)');

    // Build the brain UI inside the V's panel (DNA re-skins these classes). Idempotent: reuse if already built.
    let root = panelEl.querySelector(':scope > .v-brain');
    if (!root) {
      root = document.createElement('div');
      root.className = 'v-brain';                 // DNA RE-SKINS
      root.innerHTML =
        '<div class="v-brain-aim" aria-live="polite"></div>' +       // human aim label ("Ask about: …")
        '<div class="v-brain-reply" aria-live="polite"></div>' +      // the streamed reply
        '<textarea class="v-brain-input" rows="2"></textarea>' +
        '<button class="v-brain-send" type="button">ask</button>';
      panelEl.appendChild(root);
    }
    const aimEl = root.querySelector('.v-brain-aim');
    const replyEl = root.querySelector('.v-brain-reply');
    const inputEl = root.querySelector('.v-brain-input');
    const sendEl = root.querySelector('.v-brain-send');
    inputEl.placeholder = cfg.placeholder || 'Ask about what you’re looking at…';

    function aimLabel() {
      try { return (getAimLabel && getAimLabel()) || 'this'; } catch (e) { return 'this'; }
    }
    // Show MEANING, never the address. Refreshed on aim change so the operator sees what the brain is on.
    function aimChanged() { aimEl.textContent = 'Ask about: ' + aimLabel(); }
    aimChanged();

    // ask: talk at the CURRENT aim (read live, so re-aim between turns just works). Per-aim session
    // continuity is automatic (core.sessions[aimAddress] — each aim its own conversation thread).
    function ask(prompt) {
      const q = (prompt != null ? prompt : inputEl.value).trim();
      if (!q) return Promise.resolve(null);
      let addr;
      try { addr = getAimAddress(); } catch (e) { addr = null; }
      if (!addr) { replyEl.textContent = '(nothing aimed yet)'; return Promise.resolve(null); }
      inputEl.value = '';
      return core.talk(replyEl, addr, q);
    }

    // groundedAsk: the BLOCKING grounded-mind answer (L2) — POST /api/brain/ask, the {ok,source,answer}
    // shape (the ROLE-RESOLVED brain: kimi via the local ollama host, ~5s). DISTINCT from ask()'s STREAMING
    // /api/claude/turn turn. SELF-RENDERS into forkVBrain's OWN .v-brain-reply slot (the panel DOM is THIS
    // module's — mirror ask; the render belongs HERE, single-source). A "thinking…" placeholder covers the
    // ~5s, then the grounded answer (or a clear note — NEVER a blank middle, the by-sight bar). ALSO returns
    // the parsed response (so a caller can chain). The aim is OPTIONAL — the mind answers general Qs too.
    function groundedAsk(prompt) {
      const q = (prompt != null ? prompt : inputEl.value).trim();
      if (!q) return Promise.resolve(null);
      let addr;
      try { addr = getAimAddress(); } catch (e) { addr = null; }
      inputEl.value = '';
      const body = { question: q };
      if (addr) body.aim = addr;                          // grounds at the current aim when one is set (brain_router routes it)
      replyEl.textContent = '…';                          // SELF-RENDER: the "thinking…" placeholder (covers the blocking ~5s)
      return fetch('/api/brain/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
        .then((r) => r.json())
        .then((d) => {
          replyEl.textContent = (d && d.answer) ? core.stripMd(String(d.answer))   // strip raw **/#/` (operator-law) — SAME fn as talk()
            : (d && d.error) ? '(the brain could not answer just now)'
            : '(no answer)';                              // never a blank middle — a clear note on empty/fail
          return d;
        })
        .catch((e) => {                                   // fail-soft (the floor): a clear note + the error shape
          replyEl.textContent = '(could not reach the brain)';
          return { ok: false, source: 'error', answer: null, error: String(e) };
        });
    }

    // direct: route a direction (comment/reaction/favour) back at the CURRENT aim → suite.mark → re-render.
    function direct(item) {
      let addr;
      try { addr = getAimAddress(); } catch (e) { addr = null; }
      if (!addr || !item) return Promise.resolve(null);
      return core.writeDirections([Object.assign({ element_id: addr, annotation_type: 'direction' }, item)]);
    }

    // The V's primary "ask" affordance fires the GROUNDED MIND (groundedAsk → kimi), not the generic
    // streaming turn — so Tim asking the V gets the grounded answer (the L2 intent). ask() stays exported
    // for a future streaming/agent entry (the real-Claude-Code path), but the default button is grounded.
    sendEl.addEventListener('click', () => groundedAsk());
    inputEl.addEventListener('keydown', (e) => {            // Enter sends; Shift+Enter newlines
      if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); groundedAsk(); }
    });

    function destroy() { if (root && root.parentNode) root.parentNode.removeChild(root); }

    return { ask, groundedAsk, direct, aimChanged, destroy };
  }

  window.forkVBrain = { attach };
})();
