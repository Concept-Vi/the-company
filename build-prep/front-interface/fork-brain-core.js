/*
 * fork-brain-core.js — THE ONE brain-turn engine (reuse-don't-parallel).
 *
 * Owner: fork (ch-8djrpmsl). The single implementation of: the /api/claude/turn NDJSON stream,
 * per-ADDRESS session continuity, and the /api/territory/write route-back. Shared by BOTH:
 *   • fork-gallery-brain-hooks.js — binds a brain to ONE rendered gallery unit (per-unit).
 *   • fork-v-brain.js            — the V/RHM brain present on EVERY page (context = the CURRENT AIM ADDRESS).
 * There is exactly ONE brain-turn parser/streamer; the two mounts differ only in WHERE the address comes
 * from (a fixed unit source vs the V's live aim). The brain is REAL Claude Code (bridge._claude_stream →
 * run_turn): capable, NOT the weak 4B engine.
 *
 * VERIFICATION-STATE: shape-correct extraction of the verified hook-1 turn logic (same NDJSON contract
 * {init|text|tool|done|error}, same _sessions continuity, same direction-batch route-back). On-surface
 * use-verification (mount + 390px phone drive) is projection's per THE BAR — not claimed here. No green-paint.
 *
 * DEPENDS: POST /api/claude/turn (exists — bridge._claude_stream; the territory_prose composer diff makes its
 * context scheme-agnostic at ANY aim address). POST /api/territory/write (→ runtime.territory.territory_write;
 * the bridge route is a PROPOSED diff, projection's file).
 */
(function () {
  const CLAUDE_TURN = '/api/claude/turn';        // bridge._claude_stream (NDJSON stream)
  const TERRITORY_WRITE = '/api/territory/write'; // → runtime.territory.territory_write (route-back)
  const _sessions = {};                           // address → claude session_id (continue the convo per address)

  // ── THE BRAIN TURN: POST /api/claude/turn, stream the NDJSON reply ──────────────────────────────
  // address = ANY address (a unit source, OR the V's current aim — page/surface default, element on aim).
  // Renders accumulated text into replyEl.textContent by default; pass opts.onText(acc) to render your own
  // way (the V may want a richer panel). opts.onTool / opts.onDone / opts.onError are optional hooks.
  // Strip markdown SYNTAX at the display layer — the RHM is a SPOKEN voice (plain prose), and the reply slot
  // renders textContent (plain), so any leaked markdown shows as literal asterisks ("**What's happening**"),
  // which reads as broken/unfinished (projection's stranger flag, 2026-06-18). PANEL_BRIEFING also asks the
  // brain for no-markdown (the voice); THIS is the reliable safety net so the display is clean prose regardless
  // of what the model emits. Strips **/__ bold, *italic*, `code`, ```fences```, # headers, and -/*/1. bullet
  // MARKERS — keeps the text + newlines. Applied to EVERY emit (default replyEl AND a custom opts.onText).
  function _stripMd(t) {
    return String(t == null ? '' : t)
      .replace(/```([\s\S]*?)```/g, '$1').replace(/`([^`]+)`/g, '$1')
      .replace(/\*\*([\s\S]+?)\*\*/g, '$1').replace(/__([\s\S]+?)__/g, '$1')
      .replace(/\*([^*\n]+?)\*/g, '$1')
      .replace(/(^|\n)[ \t]{0,3}#{1,6}[ \t]+/g, '$1')
      .replace(/(^|\n)[ \t]*[-*+•][ \t]+/g, '$1').replace(/(^|\n)[ \t]*\d+\.[ \t]+/g, '$1');
  }
  async function talk(replyEl, address, prompt, opts) {
    opts = opts || {};
    const _emit = opts.onText || (replyEl ? (t) => { replyEl.textContent = t; } : function () {});
    const setText = (t) => _emit(_stripMd(t));
    let acc = '';
    // reassuring WAIT state (was a bare '…' — a cold stranger wondered if it broke). The text reads as a voice
    // ("Looking…"); _loading toggles a .brain-loading class so projection can style a subtle animated ellipsis.
    const _loading = (on) => { try { if (replyEl && !opts.onText) replyEl.classList.toggle('brain-loading', !!on); } catch (e) {} };
    _loading(true);
    setText('Looking…');
    try {
      // POINTABLES (the spotlight emit, surface-sourced): read the LIVE catalog at send-time so the brain
      // only gets tokens for things currently on screen. Send {token,label} ONLY (NO address — operator-law:
      // addresses stay client-side); keep a local token→address map to dispatch ui:point when the brain calls
      // the point verb. Absent (a per-unit mount, or a host without the fn) → no pointables, brain just speaks.
      let _ptMap = {}; let _pointables = [];
      try {
        const cat = (typeof window.surfacePointables === 'function') ? (window.surfacePointables() || []) : [];
        cat.forEach((c) => {
          if (c && c.token && c.address) { _ptMap[c.token] = c.address; if (c.label) _pointables.push({ token: c.token, label: c.label }); }
        });
      } catch (e) { _ptMap = {}; _pointables = []; }
      const body = { prompt, address };
      if (_pointables.length) body.pointables = _pointables;
      if (_sessions[address]) body.session_id = _sessions[address];   // continue the per-address conversation
      const resp = await fetch(CLAUDE_TURN, {
        method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body),
      });
      const reader = resp.body.getReader();
      const dec = new TextDecoder();
      let buf = '';
      let prevKind = null;   // last event kind — to soft-break between DISTINCT text runs (not mid-stream deltas)
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
          else if (ev.type === 'text' && ev.text) {
            _loading(false);                          // first token arrived — the wait is over
            // soft paragraph break between DISTINCT text runs (e.g. narration → tool-use → answer) so they
            // don't concatenate ("…not guessed.You're looking at…"). Consecutive text deltas (prevKind===
            // 'text') stay joined — never break mid-stream/mid-sentence. (projection's cosmetic, 2026-06-17.)
            if (acc && prevKind && prevKind !== 'text') acc += '\n\n';
            acc += ev.text; setText(acc); prevKind = 'text';
          }
          else if (ev.type === 'tool') { prevKind = 'tool'; if (opts.onTool) opts.onTool(ev); }
          else if (ev.type === 'point' && ev.token) {
            // the brain pointed at an on-screen thing: map its OPAQUE token → ui:// (LOCAL catalog — addresses
            // never came from the server) → dispatch ui:point → projection's ONE sink spotlights it. Unknown/
            // stale token → clean no-op (the sink also no-ops a non-ui://). Never breaks the text stream.
            const _addr = _ptMap[ev.token];
            if (_addr) { try { window.dispatchEvent(new CustomEvent('ui:point', { detail: { address: _addr } })); } catch (e) {} }
          }
          else if (ev.type === 'done') { _loading(false); if (ev.result && !acc) setText(ev.result); if (opts.onDone) opts.onDone(ev); }
          else if (ev.type === 'error') { _loading(false); setText('brain error: ' + ev.error); if (opts.onError) opts.onError(ev); }
        }
      }
      if (!acc) {                                  // never leave the placeholder hanging
        _loading(false);
        const cur = replyEl ? replyEl.textContent : null;
        if (cur === 'Looking…' || opts.onText) setText('(no reply)');
      }
      return acc;
    } catch (err) {
      _loading(false);
      const msg = 'brain unreachable: ' + ((err && err.message) || err);   // fail-loud to the surface
      setText(msg);
      if (opts.onError) opts.onError({ error: msg });
      return null;
    }
  }

  // ── THE ROUTE-BACK: batch directions by element_id, POST /api/territory/write, emit gallery:rerender ──
  // items: [{element_id, type, annotation_type, text?|reaction?|score?, ...}]. Groups per element so a burst
  // on one element writes together. Fail-loud: a write failure emits gallery:write-error (never silent).
  // VERIFICATION GUARD (mirror App.tsx / lib/verifyMode — the standing rule, projection's broadcast): an
  // automated/agent verification DRIVE of the REAL surface must NOT persist. projection's guard covers the
  // decision TAKE (App onVerb); THIS covers MY write path — the seam they flagged: the generic annotations
  // (comment/reaction/favour) ride gallery:direction → HOOK 2 → here, AND the V's direct() → here. So
  // writeDirections is the ONE chokepoint. When ?verify is on the URL, SUPPRESS the POST + announce LOUDLY
  // (no-silent: a console warn + a per-element gallery:write-suppressed event; the App banner already shows).
  // SAME detection as isVerifyMode (URL has 'verify'). Default (no param) = real writes, always — Tim's
  // canonical URL is param-free. Detection is wrapped so it can NEVER break a real write (fall through on error).
  function _verifyMode() {
    try {
      return typeof window !== 'undefined' && !!window.location &&
        new URLSearchParams(window.location.search).has('verify');
    } catch (e) { return false; }
  }
  function writeDirections(items) {
    if (_verifyMode()) {
      try { console.warn('[fork-brain-core] verification mode (?verify) — route-back write SUPPRESSED, nothing persisted'); } catch (e) {}
      (items || []).forEach((it) => {
        const eid = it && it.element_id;
        if (eid) window.dispatchEvent(new CustomEvent('gallery:write-suppressed',
          { detail: { element_id: eid, reason: 'verification mode (?verify) — not saved' } }));
      });
      return Promise.resolve((items || []).map((it) => ({ ok: false, suppressed: true,
        element_id: it && it.element_id, reason: 'verification mode — not saved' })));
    }
    const byElem = {};
    (items || []).forEach((it) => {
      const eid = it && it.element_id;
      if (!eid) return;
      (byElem[eid] = byElem[eid] || []).push(it);
    });
    return Promise.all(Object.entries(byElem).map(([element_id, group]) =>
      fetch(TERRITORY_WRITE, {
        method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ element_id, items: group }),
      }).then(async (r) => {
        // FAIL-LOUD with the REASON (no-silent-failures): read the body ONCE; on a non-2xx, surface the
        // server's reason (territory_write fail-louds a bad item → 400 {error}) via gallery:write-error and
        // do NOT emit rerender (the old code fired rerender even on 4xx — a false success signal). On 2xx,
        // return the territory_write body unchanged (so the success-path consumer is byte-compatible) +
        // emit rerender. The returned entry is always inspectable: success = the body {ok:true,…}; failure
        // = {ok:false, status, error} — so the composer can show WHY (projection's ask).
        let body = '';
        try { body = await r.text(); } catch (e) { body = ''; }
        let parsed = null;
        try { parsed = body ? JSON.parse(body) : null; } catch (e) { parsed = null; }
        if (!r.ok) {
          const reason = (parsed && (parsed.error || parsed.detail)) || body || ('HTTP ' + r.status);
          window.dispatchEvent(new CustomEvent('gallery:write-error',
            { detail: { element_id, status: r.status, error: reason } }));
          return { ok: false, status: r.status, error: reason };
        }
        window.dispatchEvent(new CustomEvent('gallery:rerender', { detail: { element_id } }));
        return parsed;   // the territory_write body ({ok:true, written, marks}) — unchanged for the consumer
      }).catch((err) => {
        const reason = (err && err.message) || String(err);   // network/transport failure — also loud + with a reason
        window.dispatchEvent(new CustomEvent('gallery:write-error', { detail: { element_id, error: reason } }));
        return { ok: false, error: reason };
      })
    ));
  }

  window.forkBrainCore = { talk, writeDirections, sessions: _sessions, CLAUDE_TURN, TERRITORY_WRITE };
})();
