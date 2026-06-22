/*
 * wildcard-gallery-binder.js — the portable interaction binder for the gallery face.
 *
 * Owner: wildcard (ch-piffgfxv). Segment: the Circuit + interaction layer.
 * Extracted (verified, not copied-blind) from vi-visual-bridge server.py get_html():
 *   makeAnnotatable (~10942), createComment/createReaction/createFavour (~10891),
 *   collectAnnotationsForSubmit (~11685), taxonomies.json (the vocab source of truth).
 *
 * WHAT THIS IS: a self-wiring module DNA includes in the gallery. It listens for
 * `gallery:rendered`, makes the rendered elements direction-targets keyed by ADDRESS,
 * and emits each piece of direction as `gallery:direction` for fork's address-write.
 * It does NOT render (DNA owns the look) and does NOT write state (fork owns territory_for).
 * It is the MIDDLE of the circuit: rendered-surface -> direction-at-address -> route-out.
 *
 * DISCIPLINE: this is a CONTRACT/REFERENCE for the gallery build, not a drop-in claim of
 * working — verification-state: Observed-shape-correct (item shapes match vi-visual code);
 * NOT yet use-verified on the gallery DOM. DNA re-skins .annotation-strip to the gallery
 * look; fork consumes gallery:direction. Meet at the address.
 */

(function () {
  // ── The interaction vocabulary (from contracts/taxonomies.json — source of truth) ──
  const REACTIONS = ['good', 'wrong', 'explain', 'remember_this', 'do_this'];
  const CONTENT_COMMENT_TYPES = ['note', 'direction', 'correction', 'question', 'praise', 'discuss'];
  // (meta types framing/clarity/relevance/tone exist; first slice uses content types)

  let _seq = 0;
  function annId() { _seq += 1; return 'ann-' + _seq + '-' + (window.__galleryAnnSalt = (window.__galleryAnnSalt || 0) + 1); }

  // ── Canonical item factories (shapes verified against server.py createComment/Reaction/Favour) ──
  // Every item self-identifies its element_id (= the element's ADDRESS#sub). fork groups by element_id.
  function comment(addr, type, text)   { return { id: annId(), type: 'comment',  annotation_type: type, text, element_id: addr }; }
  function reaction(addr, r)           { return { id: annId(), type: 'reaction', reaction: r,            element_id: addr }; }
  function favour(addr, score)         { return { id: annId(), type: 'favour',   score,                  element_id: addr }; }

  // ── Route-OUT: emit the UNIFIED `gallery:verb` envelope (composition's verb contract, t-1781697011) ──
  // One verb-discriminated event; the dispatcher routes by `verb` to the owning lane.
  // ANNOTATE (mark_type comment|reaction|favour) is our lane; MAKE→generate is the gated keystone.
  // detail = { verb, aim_address, payload }. verb ∈ navigate|ask|annotate|drive|open-source|generate.
  function emitVerb(verb, aim_address, payload) {
    window.dispatchEvent(new CustomEvent('gallery:verb', { detail: { verb, aim_address, payload: payload || {} } }));
  }
  // ANNOTATE route-out: an item {type:comment|reaction|favour, ...} → gallery:verb{verb:'annotate'}.
  function emitDirection(item) {
    const mark_type = item.type;                                  // comment | reaction | favour
    const payload = { mark_type };
    if (item.text != null) payload.text = item.text;
    if (item.annotation_type != null) payload.comment_type = item.annotation_type;
    if (item.reaction != null) payload.reaction = item.reaction;
    if (item.score != null) payload.score = item.score;
    emitVerb('annotate', item.element_id, payload);
    // TRANSITION ALIAS (no-break): also re-emit the legacy shape so any consumer still on
    // gallery:direction keeps working. Drop this line once all dispatch is on gallery:verb.
    window.dispatchEvent(new CustomEvent('gallery:direction', { detail: item }));
  }

  // ── DECIDE: the TAKE on a decision-card (fork's contract, t-1781745356) ──
  // Tim picks an option on a decision element → the decision_take mark write-back.
  // EXACT fields (a mismatch = a decided decision silently reads pending):
  //   mark_type = "decision_take" (underscore — exact); value = chosen option LABEL (= decided_value);
  //   target = the CANONICAL decision address.
  // ★ CANONICALIZATION IS SERVER-SIDE (fork's decision_address(parse_decision_address(addr)), Python).
  //   We do NOT reimplement it in JS (a parallel canonicalizer drifts → the exact "decided reads
  //   pending" failure the contract warns of). We emit the decision address we hold + a flag; the
  //   take-writer canonicalizes ONCE at the write-point. is_decision_take lets the dispatcher route
  //   to territory_write({type:'decision_take', value, element_id: decision_address(addr)}).
  // CANONICAL-SHAPE GUARD (validation, NOT canonicalization — projection verified by-use that
  // territory_write marks at the LITERAL element_id; a bare address silently misses → decided reads
  // pending). We do NOT transform the address (that's fork's single-source decision_address); we
  // VALIDATE its shape as a precondition and FAIL LOUD on a non-canonical one — turning a silent miss
  // into a visible refusal. A shape-check may live in two places; a transform may not.
  // Canonical = decision://<frame>/<id>, frame ∈ {global, project/<id>, user/<id>, session/<id>}.
  function _isCanonicalDecisionAddr(addr) {
    if (typeof addr !== 'string' || !addr.startsWith('decision://')) return false;
    const parts = addr.slice('decision://'.length).split('/');
    if (parts[0] === 'global')            return parts.length === 2 && !!parts[1];   // global/<id>
    if (['project','user','session'].includes(parts[0]))
                                          return parts.length === 3 && !!parts[2];   // scope/<sid>/<id>
    return false;  // bare decision://<id> or malformed → NOT canonical (the silent-miss shape)
  }
  function decide(decisionAddress, optionLabel, by) {
    if (!_isCanonicalDecisionAddr(decisionAddress)) {
      // Fail LOUD, do NOT emit — a non-canonical take would silently miss the resolver.
      const msg = '[gallery-binder] decide() refused: non-canonical decision address ' +
        JSON.stringify(decisionAddress) + ' — expected decision://<frame>/<id> (frame global|project/<id>' +
        '|user/<id>|session/<id>). DNA stamps data-decision canonical; pass THAT. Not canonicalizing in JS ' +
        '(fork owns decision_address); this guard turns a silent-miss into a visible refusal.';
      if (typeof console !== 'undefined') console.error(msg);
      throw new Error(msg);
    }
    const payload = { mark_type: 'decision_take', value: optionLabel, is_decision_take: true };
    if (by != null) payload.by = by;
    emitVerb('annotate', decisionAddress, payload);  // annotate-lane; mark_type discriminates the take
  }

  // ── BIND one rendered element as a direction-target keyed by its address ──
  // address = the element's sub-address (e.g. common_knowledge://unit#elem). DNA supplies it
  // on the element as data-address (or we derive from the unit address + an index).
  function makeAnnotatable(el, address) {
    if (!el || el.dataset.viBound) return;       // idempotent — never double-bind
    el.dataset.viBound = '1';
    el.classList.add('annotatable');
    el.setAttribute('data-element-id', address);

    const strip = document.createElement('div');
    strip.className = 'annotation-strip';        // DNA RE-SKINS this class to the gallery look
    strip.innerHTML =
      '<button class="annotation-icon comment-btn" title="Comment">' + ICONS.comment + '</button>' +
      '<button class="annotation-icon favour-btn"  title="Favour">'  + ICONS.favour  + '</button>' +
      '<span class="reaction-row">' +
        REACTIONS.map(r => '<button class="reaction-stamp-btn" data-reaction="' + r + '" title="' + r + '">' + (ICONS[r] || r) + '</button>').join('') +
      '</span>';
    el.appendChild(strip);

    strip.querySelector('.comment-btn').addEventListener('click', e => {
      e.stopPropagation();
      openCommentPicker(el, address);            // one panel, pick a type (Tim's correction)
    });
    strip.querySelector('.favour-btn').addEventListener('click', e => {
      e.stopPropagation();
      const s = promptFavour();                   // gallery-styled; placeholder prompt here
      if (s != null) emitDirection(favour(address, s));
    });
    strip.querySelectorAll('.reaction-stamp-btn').forEach(btn => {
      btn.addEventListener('click', e => {
        e.stopPropagation();
        emitDirection(reaction(address, btn.dataset.reaction));
        markPlaced(el, btn.dataset.reaction);     // visual stamp; DNA styles .placed-stamp
      });
    });
  }

  // ── The comment picker: ONE panel, pick a type (NOT a row of per-type buttons) ──
  function openCommentPicker(el, address) {
    // DNA styles .comment-picker; this is the mechanism. Renders the 6 content types as chips.
    const existing = el.querySelector('.comment-picker');
    if (existing) { existing.remove(); return; }
    const panel = document.createElement('div');
    panel.className = 'comment-picker';
    panel.innerHTML =
      CONTENT_COMMENT_TYPES.map(t => '<button class="ctype" data-t="' + t + '">' + t + '</button>').join('') +
      '<textarea class="comment-text" placeholder="direction…"></textarea>' +
      '<button class="comment-send">send</button>';
    let chosen = 'direction';
    panel.querySelectorAll('.ctype').forEach(b => b.addEventListener('click', () => {
      chosen = b.dataset.t;
      panel.querySelectorAll('.ctype').forEach(x => x.classList.remove('sel'));
      b.classList.add('sel');
    }));
    panel.querySelector('.comment-send').addEventListener('click', () => {
      const text = panel.querySelector('.comment-text').value.trim();
      if (text) emitDirection(comment(address, chosen, text));
      panel.remove();
    });
    el.appendChild(panel);
  }

  function markPlaced(el, r) {
    const s = document.createElement('span');
    s.className = 'placed-stamp ' + r;            // DNA styles
    s.textContent = ICONS[r] ? '' : r;
    s.innerHTML = ICONS[r] || r;
    el.appendChild(s);
  }

  function promptFavour() { const v = window.prompt('Favour score (number):'); return v == null ? null : Number(v); }

  // Minimal inline icons (DNA replaces with the gallery icon set).
  const ICONS = { comment: '💬', favour: '★', good: '✓', wrong: '✕', explain: '?', remember_this: '☆', do_this: '→' };

  // ── SELF-WIRE: bind after projection signals the unit is rendered (race-safe order) ──
  // ACTUAL emit (projection, confirmed g-1781595596): gallery:rendered { element, address, source, record }
  //   - detail.element: the mounted container (#gallery-mount), stable across React re-renders → WALK ROOT
  //   - detail.address: the unit's base address (we derive elem sub-addresses under it)
  //   - detail.source / detail.record: passed through unused here (fork keys the brain off source)
  // Back-compat fallbacks kept: detail.elements [{el,address}] (explicit) or detail.root.
  // BOUND TO BOTH gallery:rendered (corpus drill, unit-view.js) AND decision:rendered
  // (GalleryMount.tsx:137 — decision cards fire THIS, not gallery:rendered). Same payload shape
  // {element|root, address, anchorableSelector?}. Without the decision:rendered binding, ANNOTATE
  // (comment/reaction/favour) never bound on a decision card — decide() fired (direct onclick wire)
  // but the annotate walk didn't (listening for the wrong event). One handler, both events.
  function _onRendered(e) {
    const d = e.detail || {};
    // 1) Explicit element list (if a producer assigns sub-addresses itself).
    if (Array.isArray(d.elements)) {
      d.elements.forEach(({ el, address }) => makeAnnotatable(el, address));
      return;
    }
    // 2) projection's real shape: detail.element is the mount container to walk.
    //    (detail.root kept as an alias for the same role.)
    const root = d.element || d.root;
    if (!root || typeof root.querySelectorAll !== 'function') return;  // fail-quiet, no stray binds
    const base = d.address || 'gallery://unit';
    // ANCHORABLE SELECTOR — the DNA↔wildcard contract. Priority:
    //   (1) detail.anchorableSelector — DNA DECLARES her anchorable selector in the emit
    //       (rot-proof: she owns her markup + restyles freely; we never hardcode her classes).
    //   (2) [data-anchorable] — DNA tags content blocks with the attr (drop-in, durable).
    //   (3) semantic-HTML fallback (works for markdown-rendered surfaces like vi-visual).
    // DNA's v3 renders non-semantic divs (.p-frost etc.), so (3) alone binds 0 — by-use confirmed
    // (proj g-1781605581) — exactly the real-DOM unknown flagged at authoring (journal Entry 43).
    const SEMANTIC = 'p,h1,h2,h3,h4,h5,h6,li,blockquote,table,pre,figure';
    const sel = d.anchorableSelector || ('[data-anchorable],' + SEMANTIC);
    let i = 0;
    let bound = 0;
    root.querySelectorAll(sel).forEach(el => {
      if (el.closest && el.closest('.annotation-strip,.comment-picker')) return;
      makeAnnotatable(el, base + '#' + (el.id || ('el-' + (i++))));
      bound++;
    });
    // Fail-LOUD on zero binds (a silent 0 is the bug projection caught — surface it, don't hide it).
    if (bound === 0 && typeof console !== 'undefined') {
      console.warn('[gallery-binder] 0 anchorable elements under', base,
        '— DNA: pass detail.anchorableSelector OR tag content [data-anchorable]. Selector tried:', sel);
    }
  }
  window.addEventListener('gallery:rendered', _onRendered);
  window.addEventListener('decision:rendered', _onRendered);  // decision cards fire this (GalleryMount:137)

  // Expose for DNA to call directly if she prefers explicit binding over the event.
  window.galleryBinder = { makeAnnotatable, emitDirection, emitVerb, decide };
})();
