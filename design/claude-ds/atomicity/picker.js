// atomicity/picker.js
// ============================================================================
// CV_PICK — select ANY real element anywhere on screen, capture it as structured
// context, hand it to Vi. A document-wide inspect mode: hover spotlights the
// element under the cursor with a label; click captures a descriptor (role, tag,
// text, size, the live computed styles) + a live reference to the node, so Vi
// can talk about it and build from it — and restyles can be applied to the real
// element in place. Esc cancels. The app's own chrome is excluded from picking.
// ============================================================================
(function () {
  'use strict';
  let active = false, box, label, cb = null, lastEl = null;

  function ui() {
    if (box) return;
    box = document.createElement('div');
    box.id = 'cv-pick-box';
    box.style.cssText = 'position:fixed;z-index:2147483646;pointer-events:none;border:2px solid var(--accent-gold,#E0C010);border-radius:5px;box-shadow:0 0 0 9999px rgba(31,26,18,.20);transition:left .07s ease,top .07s ease,width .07s ease,height .07s ease;display:none';
    label = document.createElement('div');
    label.id = 'cv-pick-label';
    label.style.cssText = 'position:fixed;z-index:2147483647;pointer-events:none;font:600 11px/1 var(--font-mono,ui-monospace,monospace);background:#1F1A12;color:#E0C010;padding:4px 9px;border-radius:6px;display:none;white-space:nowrap;box-shadow:0 4px 14px rgba(0,0,0,.3)';
    document.body.appendChild(box); document.body.appendChild(label);
  }
  function excluded(el) { return !el || (el.closest && el.closest('#cv-pick-box,#cv-pick-label,.ac-vi-panel,.ac-vi-fab,.ac-cmd-back,.ac-top,.dsa-toast')); }
  function clsOf(el) { const c = el.className; return (c && c.baseVal !== undefined ? c.baseVal : String(c || '')); }
  function roleOf(el) {
    const t = el.tagName.toLowerCase(), c = clsOf(el);
    if (t === 'button' || /\bbtn\b|button/.test(c)) return 'button';
    if (/^h[1-6]$/.test(t) || /title|heading|addr|headline/.test(c)) return 'heading';
    if (/\bcard\b|tile|panel/.test(c)) return 'card';
    if (t === 'img' || /photo|image|thumb/.test(c)) return 'image';
    if (/badge|pill|\btag\b|chip/.test(c)) return 'badge';
    if (/price|stat|\bnum\b|count|metric/.test(c)) return 'value';
    if (t === 'a') return 'link';
    if (t === 'input' || t === 'textarea' || /field|input/.test(c)) return 'field';
    if (t === 'svg' || t === 'path' || /icon/.test(c)) return 'icon';
    if (/nav|rail|sidebar|menu/.test(c)) return 'navigation';
    return 'element';
  }
  function move(e) {
    const el = document.elementFromPoint(e.clientX, e.clientY);
    if (excluded(el)) { box.style.display = 'none'; label.style.display = 'none'; lastEl = null; return; }
    lastEl = el; const r = el.getBoundingClientRect();
    box.style.display = 'block'; box.style.left = r.left + 'px'; box.style.top = r.top + 'px'; box.style.width = r.width + 'px'; box.style.height = r.height + 'px';
    label.style.display = 'block'; label.textContent = roleOf(el) + ' · ' + el.tagName.toLowerCase();
    label.style.left = r.left + 'px'; label.style.top = Math.max(2, r.top - 24) + 'px';
  }
  function onClick(e) {
    if (excluded(lastEl)) return;
    e.preventDefault(); e.stopPropagation();
    const el = lastEl, d = describe(el); stop(); cb && cb(d, el);
  }
  function onKey(e) { if (e.key === 'Escape') stop(); }

  function start(onPick) {
    ui(); active = true; cb = onPick; document.body.style.cursor = 'crosshair';
    document.addEventListener('mousemove', move, true);
    document.addEventListener('click', onClick, true);
    document.addEventListener('keydown', onKey, true);
  }
  function stop() {
    active = false; document.body.style.cursor = '';
    if (box) box.style.display = 'none'; if (label) label.style.display = 'none';
    document.removeEventListener('mousemove', move, true);
    document.removeEventListener('click', onClick, true);
    document.removeEventListener('keydown', onKey, true);
  }
  function describe(el) {
    const cs = getComputedStyle(el), r = el.getBoundingClientRect();
    const kids = Array.from(el.children).slice(0, 8).map(c => roleOf(c) + ':' + c.tagName.toLowerCase());
    return {
      role: roleOf(el), tag: el.tagName.toLowerCase(), id: el.id || null,
      classes: clsOf(el).split(/\s+/).filter(Boolean).slice(0, 6),
      text: (el.childElementCount === 0 ? (el.textContent || '') : (el.getAttribute('aria-label') || firstText(el))).trim().replace(/\s+/g, ' ').slice(0, 120),
      size: { w: Math.round(r.width), h: Math.round(r.height) },
      layout: { display: cs.display, flexDirection: cs.flexDirection !== 'row' ? cs.flexDirection : undefined, gap: cs.gap !== 'normal' && cs.gap !== '0px' ? cs.gap : undefined, gridTemplateColumns: cs.gridTemplateColumns !== 'none' ? cs.gridTemplateColumns.slice(0, 40) : undefined, position: cs.position !== 'static' ? cs.position : undefined },
      box: { padding: cs.padding, margin: cs.margin !== '0px' ? cs.margin : undefined, borderWidth: cs.borderWidth !== '0px' ? cs.borderWidth : undefined },
      children: kids.length ? kids : undefined,
      styles: {
        color: cs.color, background: cs.backgroundColor,
        font: cs.fontFamily.split(',')[0].replace(/["']/g, ''),
        fontSize: cs.fontSize, weight: cs.fontWeight,
        radius: cs.borderRadius, shadow: cs.boxShadow !== 'none' ? cs.boxShadow.slice(0, 60) : 'none',
        padding: cs.padding, border: cs.borderWidth !== '0px' ? cs.border.slice(0, 50) : 'none',
      },
    };
  }
  function firstText(el) { for (const n of el.childNodes) if (n.nodeType === 3 && n.textContent.trim()) return n.textContent; return el.textContent || ''; }

  window.CV_PICK = { start, stop, describe, roleOf, isActive: () => active };
})();
