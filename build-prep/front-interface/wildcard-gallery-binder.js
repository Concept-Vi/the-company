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

  // ── Route-OUT: hand one direction-item to fork's address-write (NOT vi-visual's submit) ──
  // fork listens for gallery:direction → territory_for-write(item.element_id, item) → re-render.
  function emitDirection(item) {
    window.dispatchEvent(new CustomEvent('gallery:direction', { detail: item }));
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
  window.addEventListener('gallery:rendered', (e) => {
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
    // Anchorable = content elements (mirrors vi-visual's walker target set, minus infra).
    const sel = 'p,h1,h2,h3,h4,h5,h6,li,blockquote,table,pre,figure,[data-anchorable]';
    let i = 0;
    root.querySelectorAll(sel).forEach(el => {
      if (el.closest && el.closest('.annotation-strip,.comment-picker')) return;
      makeAnnotatable(el, base + '#' + (el.id || ('el-' + (i++))));
    });
  });

  // Expose for DNA to call directly if she prefers explicit binding over the event.
  window.galleryBinder = { makeAnnotatable, emitDirection };
})();
