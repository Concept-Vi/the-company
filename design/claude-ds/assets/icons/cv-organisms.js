/* cv-organisms.js — the FURNITURE: 28 pure SVG scene-generators (mesh, hubNetwork, cascade,
 * iconStrip, consequencesBox, phaseStrip, constellation, boardGroups, …), deterministic (seeded RNG),
 * tokens-only colour, zero framework coupling. Exported as window.DNA.org (kept — counterpart pages and
 * these pages share the call shape; claude-ds consumers may alias window.CV_ORGANISMS = DNA.org).
 *
 * ported-from: counterpart/design@20a5ac8 surface/runtime/organisms.js (2026-07-03, glyphic W1 —
 * port-by-COPY, the source repo is ④'s live room and is never edited from here). ONE change class:
 * counterpart palette var names re-pointed to claude-ds tokens (the map below). The generators close
 * the provision law's furniture gap: DiagramSolver/ContainmentTree lay out; these render populated
 * content INTO slots ("organisms fill layout slots; they own no page decisions").
 *
 * TOKEN MAP (counterpart -> claude-ds): gold->accent-gold · gold-pop->accent-gold-hover ·
 * goldwash->accent-gold-50 · ochre->accent-gold-deep · bronze->accent-bronze · bronze-line->accent-bronze-2 ·
 * charcoal->ink · body->ink-2 · secondary->ink-3 · faint->fg-muted · page->paper · warm/cool/nested->paper-2 ·
 * line->border-default · reject->status-error · warmpole-1..4->gold-soft/gold-50/tan/bronze-soft ·
 * dna-shadow-lift-1/2->elev-1/2. */
// canon: faces.organisms
/* ============================================================
   surface/runtime/organisms.js — THE FURNITURE. Live generators for the organism
   layer (dna/organisms.json) + the drafted icon set (dna/icons.json).
   Every function returns an SVG/HTML STRING coloured with the page's
   own CSS vars (--gold/--bronze-line/...), so organisms live-drive
   with the tokens like everything else.

   DNA.org.icon(name, size)            one drafted icon
   DNA.org.iconStrip(names, opts)      icons on a dashed rail (+descend)
   DNA.org.mesh(w, h, opts)            the ambient network (seeded, deterministic)
   DNA.org.hubNetwork(opts)            typed hub + spokes (gather in|out)
   DNA.org.consequencesBox(title, stats, opts)   controlled density panel
   DNA.org.cascade(stages, opts)       the time spine
   DNA.org.detailStrip(entries)        tiny-entry texture run
   ============================================================ */
(function (global) {
  "use strict";

  /* ---- the drafted icon set — 24-grid, stroke 1.5, open line, small radius ---- */
/* DNA:ICONS START (generated from dna/icons.json — rebuild: node engine/build/surface.mjs) */
  const ICON = { grid: 24, stroke: 1.5, caps: "round", joins: "round" };
  const P = {
    house: '<path d="M4 11 L12 4 L20 11"/><path d="M6.5 10.5 V19.5 H17.5 V10.5"/><path d="M10 19.5 V14.5 H14 V19.5"/>',
    ledger: '<rect x="5" y="3.5" width="14" height="17" rx="1.8"/><path d="M8.5 8 H15.5 M8.5 12 H15.5 M8.5 16 H13"/>',
    plan: '<rect x="4" y="4" width="16" height="16" rx="1.8"/><path d="M4 13 H11 V20 M11 13 V8 H20 M14.5 4 V8"/>',
    chat: '<path d="M4.5 5.5 H19.5 V15.5 H10.5 L6.5 19 V15.5 H4.5 Z"/><path d="M8.5 9 H15.5 M8.5 12 H13"/>',
    calendar: '<rect x="4" y="5.5" width="16" height="14.5" rx="1.8"/><path d="M4 10 H20 M8.5 3.5 V7 M15.5 3.5 V7"/><path d="M8 14 H10 M14 14 H16 M8 17 H10"/>',
    crane: '<path d="M6 20 H18 M12 20 V5 M12 5 L20 8 M12 5 L5 8 M20 8 V11.5"/><circle cx="20" cy="13.5" r="1.6"/>',
    scale: '<path d="M12 4 V7 M5 7 H19"/><path d="M7.5 7 L5 13 H10 L7.5 7 M16.5 7 L14 13 H19 L16.5 7"/><path d="M9 20 H15 M12 7 V20"/>',
    compass: '<circle cx="12" cy="5.5" r="1.8"/><path d="M10.8 7 L6 20 M13.2 7 L18 20 M8.2 14.5 Q12 12.5 15.8 14.5"/>',
    chart: '<path d="M4.5 4.5 V19.5 H19.5"/><path d="M8 15.5 V11.5 M12 15.5 V8 M16 15.5 V10"/>',
    plug: '<rect x="9" y="10" width="6" height="6" rx="1.2"/><path d="M10.8 10 V6.5 M13.2 10 V6.5 M12 16 V19.5"/>',
  };
  /* DNA:ICONS END */
  function icon(name, size, color) {
    size = size || 24;
    return `<svg width="${size}" height="${size}" viewBox="0 0 ${ICON.grid} ${ICON.grid}" fill="none" stroke="${color || "var(--accent-bronze-2)"}" stroke-width="${ICON.stroke}" stroke-linecap="${ICON.caps}" stroke-linejoin="${ICON.joins}">${P[name] || P.ledger}</svg>`;
  }

  /* ---- icon strip — the toolbox on its dashed rail; optional descend-to-plug ---- */
  function iconStrip(names, o) {
    o = o || {};
    const n = names.length, iw = o.iconSize || 26, gap = o.gap || 36;
    const W = n * iw + (n - 1) * gap, railY = iw + 12;
    let s = names.map((nm, i) => `<g transform="translate(${i * (iw + gap)},0)">${icon(nm, iw)}</g>`).join("");
    s += `<line x1="0" y1="${railY}" x2="${W}" y2="${railY}" stroke="var(--accent-bronze-2)" stroke-width="1.2" stroke-dasharray="5 5" opacity=".75"/>`;
    s += names.map((_, i) => `<line x1="${i * (iw + gap) + iw / 2}" y1="${iw + 3}" x2="${i * (iw + gap) + iw / 2}" y2="${railY}" stroke="var(--accent-bronze-2)" stroke-width="1" opacity=".5"/>`).join("");
    let H = railY + 6;
    if (o.descend) {
      const cx = W / 2; H = railY + 56;
      s += `<path d="M${cx} ${railY} V${railY + 30}" stroke="var(--accent-bronze-2)" stroke-width="1.4" stroke-dasharray="5 5"/>
            <rect x="${cx - 9}" y="${railY + 32}" width="18" height="18" rx="2.5" fill="var(--accent-gold)"/>`;
    }
    return `<svg width="${W}" height="${H}" viewBox="0 -2 ${W} ${H + 2}" style="overflow:visible">${s}</svg>`;
  }

  /* ---- seeded PRNG (deterministic renders — same seed, same weather) ---- */
  function mulberry32(a) { return function () { a |= 0; a = (a + 0x6D2B79F5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

  /* ---- the mesh — ambient person-network, gold heart fading bronze; the weather ---- */
  function mesh(W, H, o) {
    o = o || {};
    const n = o.nodes || 34, rnd = mulberry32(o.seed || 7);
    const hx = (o.heart && o.heart[0]) || W * 0.5, hy = (o.heart && o.heart[1]) || H * 0.45;
    const maxD = Math.hypot(Math.max(hx, W - hx), Math.max(hy, H - hy));
    const pts = [];
    for (let i = 0; i < n; i++) pts.push([rnd() * W, rnd() * H, 4 + rnd() * 9]);
    const tone = (x, y) => { const t = Math.min(1, Math.hypot(x - hx, y - hy) / maxD);
      return t < 0.3 ? "var(--accent-gold)" : t < 0.62 ? "var(--accent-gold-deep)" : "var(--accent-bronze)"; };
    let links = "";
    for (let i = 0; i < n; i++) { // each node links to its 2 nearest forward neighbours
      const cand = pts.map((p, j) => [Math.hypot(p[0] - pts[i][0], p[1] - pts[i][1]), j]).filter(c => c[1] !== i).sort((a, b) => a[0] - b[0]).slice(0, 2);
      for (const [, j] of cand) links += `<line x1="${pts[i][0].toFixed(1)}" y1="${pts[i][1].toFixed(1)}" x2="${pts[j][0].toFixed(1)}" y2="${pts[j][1].toFixed(1)}"/>`;
    }
    const nodes = pts.map(([x, y, r]) => {
      const c = tone(x, y);
      return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r.toFixed(1)}" fill="none" stroke="${c}" stroke-width="1.2"/>
              <circle cx="${x.toFixed(1)}" cy="${(y - r * 0.28).toFixed(1)}" r="${(r * 0.3).toFixed(1)}" fill="none" stroke="${c}" stroke-width="1"/>`;
    }).join("");
    return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" style="display:block" opacity="${o.opacity || 0.5}">
      <g stroke="var(--accent-bronze-2)" stroke-width="0.8" opacity=".45">${links}</g>${nodes}</svg>`;
  }

  /* ---- hub network — typed hub, spokes with direction; gold at arrival ---- */
  function hubNetwork(o) {
    o = o || {};
    const W = o.w || 520, H = o.h || 360, cx = W / 2, cy = H / 2;
    // nodes: strings OR {label, score}. (score → size/opacity when o.weighted.)
    const nodes = (o.nodes || ["C", "D", "K", "B", "S", "F"]).map((n) => (typeof n === "string" ? { label: n } : (n || {})));
    const R = o.radius || Math.min(W, H) / 2 - 46;
    const dirOut = (o.direction || "out") === "out";
    const rnd = mulberry32(o.seed || 1337);                 // deterministic jitter for o.organic
    const fillHub = o.hubFill ? "var(--accent-gold)" : (o.hub === "octagon" ? "var(--paper-2)" : "var(--paper-2)");
    const hubStroke = o.hub === "octagon" ? "var(--accent-gold)" : "var(--accent-gold-deep)";
    const hub = o.hub === "none" ? "" : o.hub === "octagon"
      ? `<polygon points="${[...Array(8)].map((_, i) => { const a = Math.PI / 8 + i * Math.PI / 4; return `${(cx + 34 * Math.cos(a)).toFixed(1)},${(cy + 34 * Math.sin(a)).toFixed(1)}`; }).join(" ")}" fill="${fillHub}" stroke="${hubStroke}" stroke-width="2.4"/>`
      : `<polygon points="${[...Array(6)].map((_, i) => { const a = Math.PI / 6 + i * Math.PI / 3; return `${(cx + 34 * Math.cos(a)).toFixed(1)},${(cy + 34 * Math.sin(a)).toFixed(1)}`; }).join(" ")}" fill="${fillHub}" stroke="${hubStroke}" stroke-width="2.2"/>`;
    let spokes = "", circles = "";
    // node sizing RULE: every circle FITS its label with uniform padding (consistent boundaries) →
    // text always fits. Prominence (score) shows as PROXIMITY-to-hub + opacity + stroke, NOT circle size
    // (so a long low-score label never overflows a small circle). One font size for all (predictable fit).
    const FS = 12, PAD = 11;
    nodes.forEach((nd, i) => {
      const sc = (nd.score == null) ? 1 : Math.max(0, Math.min(1, nd.score));
      const label = String(nd.label || "");
      const textW = label.length * FS * 0.56;                          // ~ Plus Jakarta avg glyph advance
      const nodeR = Math.max(19, textW / 2 + PAD);                     // radius fits the label + uniform pad
      const base = -Math.PI / 2 + (i * 2 * Math.PI) / nodes.length;
      const a = base + (o.organic ? (rnd() - 0.5) * 0.5 : 0);          // jitter angle → organic, not textbook
      const rr = (o.organic ? R * (0.86 + rnd() * 0.22) : R) * (o.weighted ? (1 - 0.17 * sc) : 1); // higher score → closer to hub
      const x = cx + rr * Math.cos(a), y = cy + rr * Math.sin(a);
      const op = o.weighted ? (0.64 + 0.36 * sc) : 1;
      const sw = o.weighted ? (1.4 + 1.0 * sc) : 1.8;                  // closer relations read heavier
      const sx = cx + 44 * Math.cos(a), sy = cy + 44 * Math.sin(a);
      const ex = x - (nodeR + 5) * Math.cos(a), ey = y - (nodeR + 5) * Math.sin(a);
      const [fx, fy, tx, ty] = dirOut ? [sx, sy, ex, ey] : [ex, ey, sx, sy];
      const ang = Math.atan2(ty - fy, tx - fx);
      spokes += `<line x1="${fx.toFixed(1)}" y1="${fy.toFixed(1)}" x2="${tx.toFixed(1)}" y2="${ty.toFixed(1)}" stroke="var(--accent-bronze-2)" stroke-width="1.5" stroke-dasharray="6 6" opacity="${op.toFixed(2)}"/>
        <polygon points="${tx.toFixed(1)},${ty.toFixed(1)} ${(tx - 9 * Math.cos(ang - 0.42)).toFixed(1)},${(ty - 9 * Math.sin(ang - 0.42)).toFixed(1)} ${(tx - 9 * Math.cos(ang + 0.42)).toFixed(1)},${(ty - 9 * Math.sin(ang + 0.42)).toFixed(1)}" fill="var(--accent-gold)" opacity="${op.toFixed(2)}"/>`;
      circles += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${nodeR.toFixed(1)}" fill="var(--paper)" stroke="var(--accent-bronze)" stroke-width="${sw.toFixed(1)}" opacity="${op.toFixed(2)}"/>
        <text x="${x.toFixed(1)}" y="${(y + 4).toFixed(1)}" text-anchor="middle" font-family="Plus Jakarta Sans" font-size="${FS}" font-weight="700" fill="var(--accent-bronze)">${label}</text>`;
    });
    // hub identity: a glyph (the unit's kind/essence) in the focal hub, OR a text label.
    const hubInner = o.hubGlyph
      ? `<text x="${cx}" y="${(cy + 7).toFixed(1)}" text-anchor="middle" font-family="'IBM Plex Mono',monospace" font-size="20" font-weight="700" fill="${o.hubFill ? "var(--ink)" : "var(--accent-gold-deep)"}">${o.hubGlyph}</text>`
      : (o.hubLabel ? `<text x="${cx}" y="${(cy + 6).toFixed(1)}" text-anchor="middle" font-family="Plus Jakarta Sans" font-size="19" font-weight="700" fill="${o.hub === "octagon" ? "var(--accent-gold)" : "var(--accent-gold-deep)"}">${o.hubLabel}</text>` : "");
    return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" style="overflow:visible">${spokes}${hub}${hubInner}${circles}</svg>`;
  }

  /* ---- consequences box — controlled density: several small figures, one calm panel ---- */
  function consequencesBox(title, stats, o) {
    o = o || {};
    const rows = stats.map(([n, l], i) => `<div style="display:flex;align-items:baseline;gap:10px;padding:5px 0">
        <span style="font-weight:700;font-size:${o.figSize || 21}px;letter-spacing:-.01em;color:${i === 0 && o.star ? "var(--accent-gold)" : "var(--accent-gold-deep)"};white-space:nowrap">${n}</span>
        <span style="font-size:12.5px;color:var(--ink-3);line-height:1.4">${l}</span></div>`).join("");
    return `<div style="background:var(--paper-2);border:1px solid var(--border-default);border-radius:12px;padding:18px 22px 14px">
      <div style="font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--accent-bronze);font-weight:700;margin-bottom:6px">${title}</div>${rows}</div>`;
  }

  /* ---- cascade — the time spine with stage boxes + dashed elbows ---- */
  function cascade(stages, o) {
    o = o || {};
    const W = o.w || 470, rowH = o.rowH || 74, H = stages.length * rowH + 16;
    const spineX = 46;
    let s = `<line x1="${spineX}" y1="6" x2="${spineX}" y2="${H - 10}" stroke="var(--accent-bronze-2)" stroke-width="1.6"/>`;
    stages.forEach(([label, name], i) => {
      const y = 18 + i * rowH, bx = spineX + 44 + (i % 2) * 56;
      s += `<circle cx="${spineX}" cy="${y + 17}" r="3.4" fill="var(--accent-gold-deep)"/>
        <text x="${spineX - 12}" y="${y + 21}" text-anchor="end" font-family="IBM Plex Mono" font-size="11" fill="var(--fg-muted)">${label}</text>
        <path d="M${spineX} ${y + 17} H${bx - 12}" stroke="var(--accent-bronze-2)" stroke-width="1.4" stroke-dasharray="5 5"/>
        <polygon points="${bx - 4},${y + 17} ${bx - 13},${y + 12} ${bx - 13},${y + 22}" fill="var(--accent-gold)"/>
        <rect x="${bx}" y="${y}" width="168" height="36" rx="8" fill="var(--paper)" stroke="var(--border-default)"/>
        <text x="${bx + 84}" y="${y + 23}" text-anchor="middle" font-family="Plus Jakarta Sans" font-size="13" font-weight="600" fill="var(--ink-2)">${name}</text>`;
      if (i < stages.length - 1) s += `<path d="M${bx + 84} ${y + 36} V${y + rowH + 2}" stroke="var(--border-default)" stroke-width="1.2"/>`;
    });
    return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" style="overflow:visible">${s}</svg>`;
  }

  /* ---- detail strip — many tiny entries as texture ---- */
  function detailStrip(entries) {
    return `<div style="font-family:'IBM Plex Mono',monospace;font-size:10px;letter-spacing:.06em;color:var(--fg-muted);line-height:2;word-spacing:6px">${entries.join(" · ")}</div>`;
  }

  /* ---- the phase strip — chevron segments, ONE active; the document wearing
     a map of itself (organisms.json phase_strip; corpus-direct HARVEST-3) ---- */
  function phaseStrip(labels, activeIndex, o) {
    o = o || {};
    const n = labels.length, segW = o.segWidth || 150, h = o.height || 36, notch = 14, gap = 6;
    const W = n * segW + (n - 1) * gap;
    const seg = (i) => {
      const x = i * (segW + gap), active = i === activeIndex;
      // chevron: flat left with notch cut, arrow right (direction-as-shape, forward)
      const pts = `${x},0 ${x + segW - notch},0 ${x + segW},${h / 2} ${x + segW - notch},${h} ${x},${h} ${x + notch},${h / 2}`;
      return `<polygon points="${pts}" fill="${active ? "var(--accent-gold-50)" : "none"}"
        stroke="${active ? "var(--accent-gold)" : "var(--border-default)"}" stroke-width="${active ? 1.6 : 1.1}"/>
        <text x="${x + segW / 2 + 2}" y="${h / 2}" text-anchor="middle" dominant-baseline="central"
        font-family="'Plus Jakarta Sans',sans-serif" font-size="${o.fontSize || 13.5}"
        font-weight="${active ? 700 : 600}" fill="${active ? "var(--ink)" : "var(--fg-muted)"}">${labels[i]}</text>`;
    };
    return `<svg width="${W}" height="${h}" viewBox="0 0 ${W} ${h}" style="overflow:visible">${labels.map((_, i) => seg(i)).join("")}</svg>`;
  }

  /* ---- the testimonial — gold quotemarks + quote + bold attribution
     (organisms.json testimonial; corpus-direct) ---- */
  function testimonial(quote, attribution, o) {
    o = o || {};
    const framed = o.framed !== false;
    return `<div style="${framed ? "border:1.5px solid var(--accent-gold);border-radius:10px;" : ""}padding:${framed ? "16px 22px" : "4px 0"};position:relative">
      <span style="color:var(--accent-gold);font-size:26px;font-weight:700;line-height:0;vertical-align:-8px;margin-right:6px">“</span><span style="font-style:italic;color:var(--ink-2);font-size:${o.fontSize || 13.5}px">${quote}</span><span style="color:var(--accent-gold);font-size:26px;font-weight:700;line-height:0;vertical-align:-8px;margin-left:4px">”</span>
      <div style="text-align:right;font-weight:700;color:var(--ink);font-size:${(o.fontSize || 13.5) - 1}px;margin-top:7px">${attribution}</div></div>`;
  }

  /* ---- the check matrix — gold check = brand-affirmation, muted-red cross =
     negation; self row on goldwash (invariant gold-affirmation) ---- */
  function checkMatrix(cols, rows, o) {
    o = o || {};
    const sc = (typeof o.selfCol === "number") ? o.selfCol : -1; // highlighted column index
    const check = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--accent-gold)" stroke-width="3.2" stroke-linecap="round"><path d="M4 13 L9.5 18.5 L20 6"/></svg>`;
    const cross = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="var(--status-error)" stroke-width="2.6" stroke-linecap="round"><path d="M5 5 L19 19 M19 5 L5 19"/></svg>`;
    const colHi = (j) => j === sc ? "background:var(--accent-gold-50);" : "";
    const head = `<tr><th style="text-align:left;padding:7px 10px;font-size:11px;color:var(--ink-3)"></th>${cols.map((c, j) => `<th style="padding:9px 8px;font-size:11px;font-weight:${j === sc ? 700 : 600};color:${j === sc ? "var(--ink)" : "var(--ink-3)"};${colHi(j)}${j === sc ? "border-top:1.5px solid var(--accent-gold);border-left:1.5px solid var(--accent-gold);border-right:1.5px solid var(--accent-gold);border-radius:8px 8px 0 0" : ""}">${c}</th>`).join("")}</tr>`;
    const body = rows.map((r, ri) => {
      const self = !!r.self, last = ri === rows.length - 1;
      return `<tr style="${self ? "background:var(--accent-gold-50);outline:1.5px solid var(--accent-gold);outline-offset:-1px" : ""}">
        <td style="text-align:left;padding:9px 10px;font-size:12px;font-weight:${self ? 700 : 600};color:var(--ink)">${r.label}</td>
        ${r.cells.map((v, j) => `<td style="text-align:center;padding:8px 6px;${colHi(j)}${j === sc ? "border-left:1.5px solid var(--accent-gold);border-right:1.5px solid var(--accent-gold);" + (last ? "border-bottom:1.5px solid var(--accent-gold);border-radius:0 0 8px 8px" : "") : ""}">${v ? check : cross}</td>`).join("")}</tr>`;
    }).join("");
    return `<table style="border-collapse:collapse;width:100%">${head}${body}</table>`;
  }

  /* ---- data-viz that samples the axis ramp — for the dashboard archetype
     (application.json dashboard; charts use DNA.ordinal; corpus-direct) ---- */
  function donut(segments, o) {
    o = o || {};
    const R = o.r || 54, sw = o.stroke || 18, C = 2 * Math.PI * R, cx = R + sw, cy = R + sw;
    const total = segments.reduce((a, s) => a + s.v, 0) || 1;
    let off = 0;
    const ring = segments.map((s, i) => {
      const frac = s.v / total, len = frac * C;
      const col = s.color || `var(--ordinal-${i})`;
      const seg = `<circle cx="${cx}" cy="${cy}" r="${R}" fill="none" stroke="${col}" stroke-width="${sw}"
        stroke-dasharray="${len.toFixed(2)} ${(C - len).toFixed(2)}" stroke-dashoffset="${(-off).toFixed(2)}"
        transform="rotate(-90 ${cx} ${cy})"/>`;
      off += len; return seg;
    }).join("");
    const W = 2 * (R + sw);
    const center = o.center ? `<text x="${cx}" y="${cy}" text-anchor="middle" dominant-baseline="central"
      font-family="'Plus Jakarta Sans'" font-weight="700" font-size="${o.centerSize || 22}" fill="var(--accent-gold)">${o.center}</text>` : "";
    return `<svg width="${W}" height="${W}" viewBox="0 0 ${W} ${W}">${ring}${center}</svg>`;
  }
  function bars(values, o) {
    o = o || {};
    const n = values.length, bw = o.barWidth || 16, gap = o.gap || 12, H = o.height || 90;
    const max = Math.max(...values) || 1, W = n * bw + (n - 1) * gap;
    const b = values.map((v, i) => {
      const h = (v / max) * H, x = i * (bw + gap), col = o.ordinal ? ordinalVar(i, n) : "var(--accent-gold)";
      return `<rect x="${x}" y="${H - h}" width="${bw}" height="${h.toFixed(1)}" rx="2" fill="${col}"/>`;
    }).join("");
    return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${b}</svg>`;
  }
  function ordinalVar(i, n) {
    // sample the axis ramp by position: gold (near/first) -> bronze (far/last)
    if (typeof DNA !== "undefined" && DNA.ordinal) { try { return DNA.ordinal(i, n); } catch (e) {} }
    const stops = ["var(--accent-gold)", "var(--accent-gold-deep)", "var(--accent-bronze)", "var(--accent-bronze-2)"];
    return stops[Math.min(i, stops.length - 1)];
  }

  /* ---- the GRAPH — the substrate projected geometrically (DNA.org.graph). Built OUT FROM
     hubNetwork's radial primitives (deterministic angle placement, label-fit, token colour,
     spokes) but for the whole ADDRESSED repo: a clustered radial graph with type-icons +
     progressive disclosure — OVERVIEW of folder-clusters (root V at centre) → DRILL into one
     folder's files. PURE: (data, opts) -> SVG string; the instrument (DNA.renderGraph/bindGraph,
     surface/viewers/graph/graph-view.js) holds view-state + pan/zoom/filter/tap. Node STATE-SOCKETS
     (idle/spine/selected/dim/root) reuse composition's state→colour mechanism with the graph's
     OWN vocabulary; one colour themes circle-stroke + type-icon together. Type-icons arrive via
     o.iconSVG (injected — DNA.iconSVG from the icon PACK), so this stays self-contained. ---- */
  function graph(data, o) {
    o = o || {}; data = data || {};
    const vw = o.vw || 390, vh = o.vh || 720, cx = vw / 2, cy = vh / 2;
    const iconSVG = o.iconSVG || function () { return ""; };
    const typeHue = o.typeHue || function () { return "var(--accent-bronze)"; };  // type → colour, resolved from dna/tokens.json type_hues (injected like iconSVG)
    // THE PROJECTION (Tim): the addressed CONTAINMENT TREE laid on the screen. SIBLINGS spread along the
    // screen's LONGEST axis (a level = one line); DEPTH marches along the SHORTER axis. wide screen → a level
    // is a HORIZONTAL row, depth goes DOWN · tall screen → a level is a VERTICAL column, depth goes RIGHT.
    // Open a folder = the next level appears + the camera MOVES into it (no teleport). Position MEANS structure.
    const path = Array.isArray(o.path) ? o.path : [];        // the ACTIVE folder chain ([] = root only)
    const sibHoriz = o.sibHoriz != null ? o.sibHoriz : (vw >= vh);  // wide screen → siblings spread horizontally
    const tree = o.tree || data._tree || { childrenOf: {} };
    const kidsOf = (addr) => (tree.childrenOf && tree.childrenOf[addr]) || [];
    const q = (o.filter || "").trim().toLowerCase();
    const hl = o.highlightType || "";                // legend tap: a TYPE to highlight
    const sel = o.selected || "";                    // the selected node id
    const PAGE = "var(--paper)", LINE = "var(--accent-bronze-2)", TXT = "var(--accent-bronze)", GOLD = "var(--accent-gold)";
    const COLLAR = "var(--accent-bronze)";                  // folders OWN brown — their stable collar (Tim)
    const esc = (s) => String(s == null ? "" : s).replace(/[&<>"]/g,
      (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
    // middle-truncate, KEEPING the extension — files that differ only after char ~15 stay distinct
    const trim = (s) => { s = String(s || ""); if (s.length <= 18) return s;
      const dot = s.lastIndexOf("."), ext = dot > 0 && dot > s.length - 8 ? s.slice(dot) : "";
      return s.slice(0, 15 - ext.length) + "…" + ext; };
    const FS = 11, R = 18, mx = 52;
    const SIB = sibHoriz ? 108 : 64;                 // gap between SIBLINGS (wider when horizontal — labels side-by-side)
    const DEP = sibHoriz ? 152 : 190;                // gap between DEPTH levels (the shorter axis)
    const depthC = (ci) => mx + ci * DEP + R;        // a level's position along the depth axis

    // FOLDER ORBIT (Tim): instead of a count NUMBER, dots circle the icon — one per item inside, COLOURED by
    // that item's type, grouped by type in a common order, clockwise. More dots than a ring holds → they STACK
    // into outer LAYERS at consistent dot-spacing, each layer OFFSET to sit at the midpoints between the dots
    // below it (off-centred). (Direct children — the folder's immediate contents.)
    function folderDots(kids) {
      if (!kids || !kids.length) return { svg: "", rings: 0 };
      const sorted = kids.slice()
        .sort((a, b) => (a.isDir === b.isDir ? String(a.type || "").localeCompare(String(b.type || "")) : a.isDir ? -1 : 1));
      const cols = sorted.map((k) => (k.isDir ? COLLAR : typeHue(k.type)));   // dir dots = brown; file dots = type colour
      const dirCount = sorted.filter((k) => k.isDir).length;
      const dotR = 2.2, ring0 = R + 6.5, ringGap = 6.4, arc = 7.4;
      let s = "", placed = 0, ring = 0, cap0 = 0;
      while (placed < cols.length && ring < 6) {
        const rr = ring0 + ring * ringGap, cap = Math.max(6, Math.floor((2 * Math.PI * rr) / arc)), step = (2 * Math.PI) / cap;
        if (ring === 0) cap0 = cap;
        const stagger = ring % 2 ? step / 2 : 0;             // off-centred layer = midpoint between the dots below
        for (let k = 0; k < cap && placed < cols.length; k++, placed++) {
          const ang = -Math.PI / 2 + stagger + k * step;     // clockwise from the top
          s += `<circle cx="${(rr * Math.cos(ang)).toFixed(1)}" cy="${(rr * Math.sin(ang)).toFixed(1)}" r="${dotR}" fill="${cols[placed]}"/>`;
        }
        ring++;
      }
      // DIVIDER (Tim): a small radial tick where the folder(dir)-dots END and the file-dots begin — so the
      // brown sub-folder dots read as separate from the type-coloured file dots.
      let div = "";
      if (dirCount > 0 && dirCount < cols.length && cap0) {
        const a = -Math.PI / 2 + (dirCount - 0.5) * ((2 * Math.PI) / cap0);   // midway between last dir + first file
        const r0 = R + 3, r1 = ring0 + (ring - 1) * ringGap + 4;
        s += `<line x1="${(r0 * Math.cos(a)).toFixed(1)}" y1="${(r0 * Math.sin(a)).toFixed(1)}" x2="${(r1 * Math.cos(a)).toFixed(1)}" y2="${(r1 * Math.sin(a)).toFixed(1)}" stroke="${LINE}" stroke-width="1" opacity=".7"/>`;
      }
      return { svg: `<g class="gr-orbit" style="pointer-events:none">${s}</g>`, rings: ring };
    }

    // a node = ONE group transform, LOCAL-coord children → FLIP-ready + zoom-composable. Opacity rides the
    // ICON (p.op); the LABEL rides p.labelOp (kept readable for small folders); the disc-stroke/RING stays
    // CONSTANT so a near-empty folder is still present + findable (Tim: "the ring would stay").
    function node(x, y, r, label, iconName, p) {
      p = p || {};
      const col = p.color || TXT, op = p.op == null ? 1 : p.op, lop = p.labelOp == null ? op : p.labelOp, fill = p.fill || PAGE;
      const isz = r * 1.1, ly = r + 14 + (p.orbitRings || 0) * 6.4;   // push the label clear of any orbit layers
      const selr = p.selected ? `<circle cx="0" cy="0" r="${(r + 6).toFixed(1)}" fill="none" stroke="${GOLD}" stroke-width="2.2" class="gr-selring"/>` : "";
      const orbit = p.orbit || "";                    // folders: the type-coloured dots circling the icon (count + composition)
      const ic = iconName ? `<g transform="translate(${(-isz / 2).toFixed(1)},${(-isz / 2).toFixed(1)})" opacity="${op}" style="pointer-events:none">${iconSVG(iconName, { size: isz, color: col })}</g>` : "";
      const tx = label ? `<text x="0" y="${ly.toFixed(1)}" text-anchor="middle" font-family="Plus Jakarta Sans" font-size="${FS}" font-weight="${p.bold ? 700 : 600}" fill="${col}" opacity="${lop}" style="pointer-events:none">${esc(label)}</text>` : "";
      return `<g class="gr-node" data-id="${esc(p.id || "")}" data-kind="${esc(p.kind || "")}" data-type="${esc(p.dtype || "")}" transform="translate(${x.toFixed(1)},${y.toFixed(1)})" style="cursor:pointer">` +
        `${selr}${orbit}<circle class="gr-disc" cx="0" cy="0" r="${r.toFixed(1)}" fill="${fill}" stroke="${col}" stroke-width="${p.sw || 1.8}"/>${ic}${tx}</g>`;
    }
    // a trace: gently bowed, colour = the SOURCE node's TYPE (e.stroke), arrow = direction (ALWAYS on — muted
    // head; GOLD head on focus), .gr-flow animates the dash = "in motion" (CSS, reduced-motion-safe).
    function curve(x1, y1, x2, y2, op, e) {
      e = e || {};
      const m0 = (x1 + x2) / 2, m1 = (y1 + y2) / 2, qx = m0 + (cx - m0) * 0.12, qy = m1 + (cy - m1) * 0.12;
      const stroke = e.gold ? GOLD : (e.stroke || LINE);
      let s = `<path class="gr-trace${e.flow ? " gr-flow" : ""}" d="M${x1.toFixed(1)} ${y1.toFixed(1)} Q${qx.toFixed(1)} ${qy.toFixed(1)} ${x2.toFixed(1)} ${y2.toFixed(1)}" fill="none" stroke="${stroke}" stroke-width="${e.gold ? 1.8 : 1.1}" opacity="${op.toFixed(2)}"/>`;
      const t = 0.86, mt = 1 - t;                     // arrowhead near the target on the quadratic — who-depends-on-whom, always shown
      const px = mt * mt * x1 + 2 * mt * t * qx + t * t * x2, py = mt * mt * y1 + 2 * mt * t * qy + t * t * y2;
      const ang = Math.atan2(2 * mt * (qy - y1) + 2 * t * (y2 - qy), 2 * mt * (qx - x1) + 2 * t * (x2 - qx));
      const ah = e.gold ? 8 : 5.5;
      s += `<polygon points="${px.toFixed(1)},${py.toFixed(1)} ${(px - ah * Math.cos(ang - 0.42)).toFixed(1)},${(py - ah * Math.sin(ang - 0.42)).toFixed(1)} ${(px - ah * Math.cos(ang + 0.42)).toFixed(1)},${(py - ah * Math.sin(ang + 0.42)).toFixed(1)}" fill="${stroke}" opacity="${op.toFixed(2)}"/>`;
      return s;
    }

    // ---- build the columns: column ci shows the children of (ci===0 ? root : path[ci-1]); the active
    // item in column ci is path[ci] (highlighted, its children form column ci+1). The structure's own
    // order (address-alpha, dirs before files) places siblings along the short axis. ----
    const pos = {}, cols = [];
    let parentSib = null;                              // the active parent's sibling-coordinate in the prior column
    for (let ci = 0; ci <= path.length; ci++) {
      const parent = ci === 0 ? "." : path[ci - 1];
      const raw = kidsOf(parent);
      const items = (q ? raw.filter((n) => n.id.toLowerCase().includes(q) || String(n.label).toLowerCase().includes(q)) : raw)
        .slice().sort((a, b) => (a.isDir === b.isDir ? String(a.id).localeCompare(String(b.id)) : a.isDir ? -1 : 1));
      const n = items.length, d = depthC(ci);
      // EXPAND UNDER THE PARENT (Tim) — the containment CASCADE: a child level CENTRES under its parent's
      // sibling-coordinate, never from the page margin. Column 0 (root) lays from the margin.
      const sibAt = (j) => (ci === 0 || parentSib == null) ? (mx + (j + 0.5) * SIB) : (parentSib + (j - (n - 1) / 2) * SIB);
      items.forEach((it, j) => { const s = sibAt(j); pos[ci + "|" + it.id] = sibHoriz ? [s, d] : [d, s]; });
      const ai = items.findIndex((it) => it.id === path[ci]);
      parentSib = ai >= 0 ? sibAt(ai) : parentSib;     // the active child's coord seeds the next level's centre
      cols.push({ ci, items, active: path[ci] || null, count: n });
    }
    // export the resolved geometry so graph-view's camera reads it (kills the "MUST mirror" duplication)
    if (o.out) { o.out.pos = pos; o.out.SIB = SIB; o.out.DEP = DEP; o.out.mx = mx; o.out.R = R; o.out.sibHoriz = sibHoriz; }
    const maxItems = Math.max(1, ...cols.map((c) => c.count));
    const sibExtent = mx + maxItems * SIB + mx, depExtent = mx + (path.length + 1) * DEP + R + mx;
    const CW = Math.max(vw, sibHoriz ? sibExtent : depExtent);
    const CH = Math.max(vh, sibHoriz ? depExtent : sibExtent);

    let body = "", links = "";
    cols.forEach((col) => {
      // containment connector: the ACTIVE folder OPENS into the next level (gold stub along the DEPTH axis)
      if (col.active != null && col.ci < path.length) {
        const a = pos[col.ci + "|" + col.active], next = cols[col.ci + 1];
        if (a && next && next.count) {
          const nd = depthC(col.ci + 1);
          const edge = sibHoriz ? [a[0], a[1] + R] : [a[0] + R, a[1]];      // out along the depth axis
          const turn = sibHoriz ? [a[0], nd - R - 6] : [nd - R - 6, a[1]];
          links += `<path class="gr-conn" d="M${edge[0].toFixed(1)} ${edge[1].toFixed(1)} L${turn[0].toFixed(1)} ${turn[1].toFixed(1)}" fill="none" stroke="${GOLD}" stroke-width="1.6" opacity=".5" stroke-linecap="round"/>`;
        }
      }
      col.items.forEach((n) => {
        const [x, y] = pos[col.ci + "|" + n.id];
        const isActive = n.id === col.active;
        const qMatch = !q || n.id.toLowerCase().includes(q) || String(n.label).toLowerCase().includes(q);
        const tMatch = !hl || n.type === hl;
        const match = qMatch && tMatch, dimming = q || hl;
        // FOLDER = brown COLLAR (its stable identity) + orbiting type-dots (count + composition); FILE = type→colour, no collar/dots
        const orb = n.isDir ? folderDots(kidsOf(n.id)) : null;
        const base = n.isDir ? COLLAR : typeHue(n.type);
        body += node(x, y, R, trim(n.label), n.icon,
          { id: n.id, kind: n.isDir ? "dir" : "file", dtype: n.type,
            color: dimming ? (match ? base : LINE) : base,
            op: dimming && !match ? 0.3 : 1, labelOp: dimming && !match ? 0.3 : 1,
            orbit: orb && !(dimming && !match) ? orb.svg : "", orbitRings: orb ? orb.rings : 0,
            sw: n.isDir ? (isActive ? 3.4 : 3) : (isActive ? 2.4 : 1.7),     // folder collar is thick (brown); file ring thin
            bold: isActive || n.spine, selected: isActive || n.id === sel });
      });
    });

    return `<svg class="gr-svg" width="${CW}" height="${CH}" viewBox="0 0 ${CW} ${CH}" style="display:block;overflow:visible">` +
      `<g class="gr-edges">${links}</g><g class="gr-nodes">${body}</g></svg>`;
  }

  /* ---- the CONNECTOR — the movement joint between two frames (deck s5's dashed plug, lifted from var-15's
     .socket/.dash/.prongs/.plugbody into a reusable token-coloured SVG). A bronze SOCKET ring (left) — a
     dashed transport line — a GOLD PLUG body with two prongs (right). For the duo device (merge-sa: the plug
     IS the authorization toggle — gold = the act). (data-less) (role, opts) -> SVG string. ---- */
  function connector(role, o) {
    o = o || {};
    const W = o.w || 96, H = o.h || 56, cy = H / 2;
    const GOLD = "var(--accent-gold)", LINE = "var(--accent-bronze-2)", PAGE = "var(--paper)", OCHRE = "var(--accent-gold-deep)", BRONZE = "var(--accent-bronze)";
    // radial gold→bronze GLOW behind the octagon core + a directional bronze→gold connector gradient (C1 compare:
    // gradient/glow material — the focal node carries a layered glow, the connector reads current→authorized by warmth)
    const gid = "cx-" + String(role || "c").replace(/[^a-z0-9]/gi, "");
    const defs = `<defs><radialGradient id="g${gid}"><stop offset="0%" stop-color="${GOLD}" stop-opacity=".5"/><stop offset="55%" stop-color="${OCHRE}" stop-opacity=".2"/><stop offset="100%" stop-color="${BRONZE}" stop-opacity="0"/></radialGradient>` +
      `<linearGradient id="l${gid}" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="${BRONZE}"/><stop offset="100%" stop-color="${GOLD}"/></linearGradient></defs>`;
    // socket ring (left) with two contact dots
    const sx = 16;
    const socket = `<circle cx="${sx}" cy="${cy}" r="11" fill="${PAGE}" stroke="${LINE}" stroke-width="2"/>` +
      `<circle cx="${sx}" cy="${cy - 4}" r="2.2" fill="${LINE}"/><circle cx="${sx}" cy="${cy + 4}" r="2.2" fill="${LINE}"/>`;
    // dashed transport line
    const dash = `<line x1="${sx + 13}" y1="${cy}" x2="${W - 42}" y2="${cy}" stroke="url(#l${gid})" stroke-width="2" stroke-dasharray="5 5"/>`;
    // prongs reaching from the plug toward the socket
    const px = W - 30;
    const prongs = `<line x1="${px - 10}" y1="${cy - 5}" x2="${px}" y2="${cy - 5}" stroke="${GOLD}" stroke-width="3" stroke-linecap="round"/>` +
      `<line x1="${px - 10}" y1="${cy + 5}" x2="${px}" y2="${cy + 5}" stroke="${GOLD}" stroke-width="3" stroke-linecap="round"/>`;
    // the authorize CORE — rendered as the OCTAGON (Tim Decision-2: octagon = the core mark; verified geometry:
    // a gold OUTLINE on cream, NOT gold-fill). The key/plug being authorized IS the core. Carries the bolt glyph.
    const ox = px, oy = cy - 16;
    const oct = `${ox + 8},${oy} ${ox + 18},${oy} ${ox + 26},${oy + 9} ${ox + 26},${oy + 23} ${ox + 18},${oy + 32} ${ox + 8},${oy + 32} ${ox},${oy + 23} ${ox},${oy + 9}`;
    const plug = `<polygon points="${oct}" fill="${PAGE}" stroke="${GOLD}" stroke-width="2.2"/>` +
      `<path d="M${px + 14} ${cy - 9} L${px + 9} ${cy + 1} H${px + 14} L${px + 11} ${cy + 9} L${px + 18} ${cy - 2} H${px + 13} Z" fill="${GOLD}"/>`;
    const lab = String(role || "connector").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
    const glow = `<circle cx="${ox + 13}" cy="${cy}" r="23" fill="url(#g${gid})"/>`;
    return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" style="overflow:visible" role="img" aria-label="${lab}">${defs}${socket}${dash}${prongs}${glow}${plug}</svg>`;
  }

  /* ---- TAXONOMY EMERGENCE — provisional/ghost kinds (left, dashed, low-opacity = a prior guess) GIVE WAY to
     the real kinds (right, filled = emerged from an open coverage pass), with dashed transition arrows L→R.
     The one net-new device for form-taxonomy: "discover the real kinds from open coverage." Follows the
     hubNetwork/graph authoring conventions — pure (data, opts) -> SVG string, token-coloured.
     data: { provisional:[labels], real:[labels] } ---- */
  function taxonomyEmergence(data, o) {
    o = o || {}; data = data || {};
    const esc = (s) => String(s == null ? "" : s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
    const W = o.w || 340, H = o.h || 200;
    const prov = data.provisional || [], real = data.real || [];
    const GOLD = "var(--accent-gold)", LINE = "var(--accent-bronze-2)", PAGE = "var(--paper)", BRONZE = "var(--accent-bronze)", FAINT = "var(--fg-muted)";
    const colW = 118, gap = W - colW * 2, leftX = colW / 2, rightX = colW + gap + colW / 2;
    const pillH = 28, padY = 16;
    const rowsN = Math.max(prov.length, real.length, 1);
    const stepP = (H - padY * 2) / Math.max(prov.length, 1);
    const stepR = (H - padY * 2) / Math.max(real.length, 1);
    const yOf = (i, step) => padY + step * (i + 0.5);
    // left header (ghost) + right header (emerged)
    let s = `<text x="${leftX}" y="11" text-anchor="middle" font-family="'IBM Plex Mono',monospace" font-size="9.5" letter-spacing=".08em" fill="${FAINT}">PRIOR GUESS</text>` +
      `<text x="${rightX}" y="11" text-anchor="middle" font-family="'IBM Plex Mono',monospace" font-size="9.5" letter-spacing=".08em" fill="${BRONZE}">REAL KINDS</text>`;
    // ghost provisional pills (dashed, low-opacity)
    prov.forEach((lab, i) => {
      const y = yOf(i, stepP);
      s += `<rect x="${leftX - colW / 2 + 6}" y="${(y - pillH / 2).toFixed(1)}" width="${colW - 12}" height="${pillH}" rx="${pillH / 2}" fill="none" stroke="${LINE}" stroke-width="1.3" stroke-dasharray="4 4" opacity=".7"/>` +
        `<text x="${leftX}" y="${(y + 3.5).toFixed(1)}" text-anchor="middle" font-family="Plus Jakarta Sans" font-size="11.5" fill="${FAINT}" opacity=".85">${esc(lab)}</text>`;
    });
    // a coverage-pass arrow bundle from each ghost toward the emergence column (dashed, gold heads)
    prov.forEach((_, i) => {
      const y = yOf(i, stepP), ty = yOf(Math.min(i, real.length - 1), stepR);
      const x1 = leftX + colW / 2 - 4, x2 = rightX - colW / 2 + 2;
      s += `<path d="M${x1} ${y.toFixed(1)} C${(x1 + 26)} ${y.toFixed(1)}, ${(x2 - 26)} ${ty.toFixed(1)}, ${x2} ${ty.toFixed(1)}" fill="none" stroke="${LINE}" stroke-width="1.1" stroke-dasharray="5 5" opacity=".6"/>`;
    });
    // real emerged pills (filled page + bronze border, the first carrying gold = the proposed true set)
    real.forEach((lab, i) => {
      const y = yOf(i, stepR);
      s += `<rect x="${rightX - colW / 2 + 6}" y="${(y - pillH / 2).toFixed(1)}" width="${colW - 12}" height="${pillH}" rx="${pillH / 2}" fill="${PAGE}" stroke="${GOLD}" stroke-width="2" filter="none"/>` +
        `<text x="${rightX}" y="${(y + 3.5).toFixed(1)}" text-anchor="middle" font-family="Plus Jakarta Sans" font-size="11" font-weight="700" fill="${BRONZE}">${esc(lab)}</text>`;
    });
    return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" style="overflow:visible">${s}</svg>`;
  }

  // ════════════════════════════════════════════════════════════════════════════════════════════════════
  // THE ARTEFACT FAMILY (generator-grammar #2) — synthetic ConceptV "material density" from tokens, content-
  // agnostic, REUSABLE (NOT bespoke). PROPOSED CONTRACT (co-scoped with composition): org.<name>(o) -> an
  // SVG/HTML string; o carries {mode?:'synthetic'|'real', real?, w?, h?, label?, ...organism-specific};
  // colours are ONLY tokens (var(--…)); the result scales (max-width:100%); always an aria-label. Default
  // mode = synthetic (carries density with NO real asset); real assets ride the same containers (sourcePanelVisual).
  // designLibraryObject = the first reference organism (generalised from the keystone's library grid).
  // ════════════════════════════════════════════════════════════════════════════════════════════════════
  function designLibraryObject(o) {
    o = o || {};
    const cols = o.cols || 3, rows = o.rows || 2, tw = o.tile || 30, th = o.tileH || 22, gap = o.gap || 7;
    const hl = (o.highlight == null) ? -1 : o.highlight;   // index of the highlighted ("new") design, or -1
    const W = cols * tw + (cols - 1) * gap, H = rows * th + (rows - 1) * gap;
    const LINE = "var(--accent-bronze-2)", GOLD = "var(--accent-gold)", GW = "var(--accent-gold-50)", GP = "var(--accent-gold-hover)";
    const uid = "dl" + (designLibraryObject._n = (designLibraryObject._n || 0) + 1), tileG = "tg" + uid, covG = "cv" + uid;
    const defs = `<defs>` +
      `<linearGradient id="${tileG}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--paper)"/><stop offset="100%" stop-color="var(--paper-2)"/></linearGradient>` +
      `<linearGradient id="${covG}" x1="0" y1="0" x2="0.6" y2="1"><stop offset="0%" stop-color="var(--accent-gold-50)"/><stop offset="100%" stop-color="var(--accent-bronze-soft)"/></linearGradient>` +
      `</defs>`;
    // each tile = a material mini design-thumbnail: a warm tonal COVER band (varied by k) + caption lines below
    const covH = th * 0.5;
    const hint = (x, y, k) => {
      const cx = x + tw / 2, cv = `<rect x="${x + 3}" y="${y + 3}" width="${tw - 6}" height="${covH.toFixed(1)}" rx="1.5"`;
      let cover;
      if (k % 4 === 0) cover = `${cv} fill="url(#${covG})" opacity=".5"/><circle cx="${cx}" cy="${(y + 3 + covH * 0.5).toFixed(1)}" r="${(covH * 0.3).toFixed(1)}" fill="var(--paper)" opacity=".7"/>`;
      else if (k % 4 === 1) cover = `${cv} fill="url(#${covG})" opacity=".34"/>`;
      else if (k % 4 === 2) cover = `${cv} fill="var(--paper-2)"/><path d="M${x + 5} ${(y + 3 + covH - 2).toFixed(1)} L${(x + tw * 0.42).toFixed(1)} ${(y + 5).toFixed(1)} L${(x + tw * 0.6).toFixed(1)} ${(y + 3 + covH * 0.6).toFixed(1)} L${x + tw - 5} ${(y + 5).toFixed(1)}" fill="none" stroke="${LINE}" stroke-width="1" opacity=".5"/>`;
      else cover = `${cv} fill="url(#${covG})" opacity=".28"/><rect x="${x + 5}" y="${(y + 5).toFixed(1)}" width="${(tw * 0.38).toFixed(1)}" height="${(covH * 0.5).toFixed(1)}" fill="var(--paper)" opacity=".6"/>`;
      const ly = y + 4 + covH + 3;
      return cover + `<line x1="${x + 4}" y1="${ly.toFixed(1)}" x2="${x + tw - 5}" y2="${ly.toFixed(1)}" stroke="${LINE}" stroke-width="1" opacity=".5"/><line x1="${x + 4}" y1="${(ly + 3).toFixed(1)}" x2="${(x + tw * 0.6).toFixed(1)}" y2="${(ly + 3).toFixed(1)}" stroke="${LINE}" stroke-width="1" opacity=".3"/>`;
    };
    // REAL design covers (data-URIs) = the material/photographic substance (source-faithful — capital-raise p-05's
    // "Virtual Tours We've Delivered" grid is exactly this). When present, each tile is a real <image>; the synthetic
    // cover-hint is the abstract FALLBACK (the floor), not the finish.
    const covers = Array.isArray(o.covers) ? o.covers.filter(Boolean) : null;
    let tiles = "", clips = "", k = 0;
    for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
      const x = c * (tw + gap), y = r * (th + gap), isHl = (k === hl);
      if (covers && covers.length) {                                    // ── REAL cover (photographic material) ──
        const cid = `${tileG}c${k}`;
        clips += `<clipPath id="${cid}"><rect x="${x}" y="${y}" width="${tw}" height="${th}" rx="3.5"/></clipPath>`;
        tiles += `<rect x="${(x + 1.7).toFixed(1)}" y="${(y + 2.6).toFixed(1)}" width="${tw}" height="${th}" rx="3.5" fill="${LINE}" opacity=".24"/>` +   // soft cast shadow → depth
          `<image href="${covers[k % covers.length]}" x="${x}" y="${y}" width="${tw}" height="${th}" preserveAspectRatio="xMidYMid slice" clip-path="url(#${cid})"/>` +
          `<rect x="${x}" y="${y}" width="${tw}" height="${th}" rx="3.5" fill="none" stroke="${isHl ? GOLD : LINE}" stroke-width="${isHl ? 1.8 : 1}"/>` +   // frame
          `<line x1="${x + 2}" y1="${(y + 1.4).toFixed(1)}" x2="${x + tw - 2}" y2="${(y + 1.4).toFixed(1)}" stroke="var(--paper)" stroke-width="1" opacity=".35"/>` +   // top light
          (isHl ? `<rect x="${x}" y="${y}" width="${tw}" height="${th}" rx="3.5" fill="${GW}" opacity=".25"/><circle cx="${(x + tw - 6).toFixed(1)}" cy="${(y + 6).toFixed(1)}" r="6" fill="${GP}"/><text x="${(x + tw - 6).toFixed(1)}" y="${(y + 9.5).toFixed(1)}" text-anchor="middle" font-size="9" font-weight="700" fill="var(--paper)">+</text>` : "");
      } else {                                                          // ── synthetic cover (abstract fallback) ──
        tiles += `<rect x="${x}" y="${y}" width="${tw}" height="${th}" rx="3.5" fill="${isHl ? GW : `url(#${tileG})`}" stroke="${isHl ? GOLD : LINE}" stroke-width="${isHl ? 1.4 : 1}"/>` +
          `<line x1="${x + 2}" y1="${y + 1.5}" x2="${x + tw - 2}" y2="${y + 1.5}" stroke="var(--paper)" stroke-width="1" opacity=".55"/>` +
          (isHl ? `<text x="${x + tw / 2}" y="${y + th / 2 + 5}" text-anchor="middle" font-size="13" font-weight="700" fill="${GP}">+</text>` : hint(x, y, k));
      }
      k++;
    }
    const lab = String(o.label || "design library").replace(/[&<>"]/g, "");   // self-contained (esc is not in this scope)
    return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" style="max-width:100%;height:auto" role="img" aria-label="${lab}">${defs}${clips}${tiles}</svg>`;
  }

  // fileStack — a stack of offset document pages (files / drafts / documents). Front page carries content lines +
  // ONE gold dog-ear (the single focal). Synthetic material density; n / size are content-driven.
  function fileStack(o) {
    o = o || {};
    const n = Math.max(1, o.n || 3), pw = o.w || 46, ph = o.h || 58, dx = o.dx || 6, dy = o.dy || 5;
    const W = pw + (n - 1) * dx + 4, H = ph + (n - 1) * dy + 4;
    const LINE = "var(--accent-bronze-2)", GP = "var(--accent-gold-hover)";
    const uid = "fs" + (fileStack._n = (fileStack._n || 0) + 1), pageG = "p" + uid, covG = "c" + uid;
    let s = `<defs>` +
      `<linearGradient id="${pageG}" x1="0" y1="0" x2="0.4" y2="1"><stop offset="0%" stop-color="var(--paper)"/><stop offset="100%" stop-color="var(--paper-2)"/></linearGradient>` +
      `<linearGradient id="${covG}" x1="0" y1="0" x2="0.7" y2="1"><stop offset="0%" stop-color="var(--accent-gold-50)"/><stop offset="100%" stop-color="var(--accent-bronze-soft)"/></linearGradient>` +
      `</defs>`;
    for (let i = n - 1; i >= 0; i--) {                              // back-to-front so the front page sits on top
      const x = 2 + i * dx, y = 2 + (n - 1 - i) * dy, front = (i === 0);
      s += `<rect x="${x + 2}" y="${y + 2.5}" width="${pw}" height="${ph}" rx="4" fill="${LINE}" opacity=".12"/>`;   // soft cast
      s += `<rect x="${x}" y="${y}" width="${pw}" height="${ph}" rx="4" fill="url(#${pageG})" stroke="${LINE}" stroke-width="1"/>`;
      s += `<line x1="${x + 1}" y1="${y + 1.5}" x2="${x + pw - 1}" y2="${y + 1.5}" stroke="var(--paper)" stroke-width="1" opacity=".55"/>`;   // top light
      if (front) {
        s += `<rect x="${x + 5}" y="${y + 6}" width="${pw - 10}" height="${(ph * 0.24).toFixed(1)}" rx="2" fill="url(#${covG})" opacity=".5"/>`;   // warm header band
        const ly0 = y + ph * 0.24 + 13;
        for (let l = 0; l < 3; l++) s += `<line x1="${x + 6}" y1="${(ly0 + l * 9).toFixed(1)}" x2="${x + pw - 6 - (l === 2 ? 11 : 0)}" y2="${(ly0 + l * 9).toFixed(1)}" stroke="${LINE}" stroke-width="1" opacity="${l === 0 ? '.5' : '.3'}"/>`;
        s += `<path d="M${x + pw - 13} ${y} L${x + pw} ${y} L${x + pw} ${y + 13} Z" fill="${GP}" opacity=".9"/>`;   // single gold dog-ear (focal)
      }
    }
    const lab = String(o.label || "file stack").replace(/[&<>"]/g, "");
    return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" style="max-width:100%;height:auto" role="img" aria-label="${lab}">${s}</svg>`;
  }

  // planThumbnail — a framed architectural / blueprint plan (the source's floor-plan DNA): faint blueprint grid +
  // room walls + a door arc + ONE gold focal marker (the spot). The "credible artefact" stand-in.
  function planThumbnail(o) {
    o = o || {};
    const W = o.w || 104, H = o.h || 70, p = 5, t = Math.max(2, Math.round(Math.min(W, H) * 0.03));
    const INK = "var(--accent-bronze-2)", GRID = "var(--border-default)", GP = "var(--accent-gold-hover)", SEC = "var(--ink-3)";
    const paper = "ppr" + (planThumbnail._n = (planThumbnail._n || 0) + 1);
    const ix = p + 2, iy = p + 2, iw = W - 2 * (p + 2), ih = H - 2 * (p + 2);
    const wall = (x, y, w, h) => `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${w.toFixed(1)}" height="${h.toFixed(1)}" fill="${INK}"/>`;   // poché (filled) walls = real-plan convention
    const partX = ix + iw * 0.6, doorGap = ih * 0.32, doorTop = iy + ih * 0.14;
    let s = `<defs><linearGradient id="${paper}" x1="0" y1="0" x2="0.3" y2="1"><stop offset="0%" stop-color="var(--paper)"/><stop offset="100%" stop-color="var(--paper-2)"/></linearGradient></defs>` +
      `<rect x="1" y="1" width="${W - 2}" height="${H - 2}" rx="3" fill="url(#${paper})" stroke="${INK}" stroke-width="1"/>`;
    for (let gx = p + 6; gx < W - p; gx += 9) s += `<line x1="${gx}" y1="${p}" x2="${gx}" y2="${H - p}" stroke="${GRID}" stroke-width="1" opacity=".32"/>`;
    for (let gy = p + 6; gy < H - p; gy += 9) s += `<line x1="${p}" y1="${gy}" x2="${W - p}" y2="${gy}" stroke="${GRID}" stroke-width="1" opacity=".32"/>`;
    s += `<rect x="${(ix + t).toFixed(1)}" y="${(iy + t).toFixed(1)}" width="${(iw - 2 * t).toFixed(1)}" height="${(ih - 2 * t).toFixed(1)}" fill="var(--accent-gold-50)" opacity=".55"/>`;   // room wash
    s += wall(ix, iy, iw, t) + wall(ix, iy + ih - t, iw, t) + wall(ix, iy, t, ih) + wall(ix + iw - t, iy, t, ih);   // outer poché
    s += wall(partX, iy, t, doorTop - iy) + wall(partX, doorTop + doorGap, t, iy + ih - (doorTop + doorGap));   // partition + door gap
    s += `<path d="M${(partX + t).toFixed(1)} ${(doorTop + doorGap).toFixed(1)} a${doorGap.toFixed(1)} ${doorGap.toFixed(1)} 0 0 1 ${doorGap.toFixed(1)} ${(-doorGap).toFixed(1)}" fill="none" stroke="${INK}" stroke-width="1" opacity=".6"/>`;   // door swing
    const dy = H - p - 1.5;   // dimension line + ticks
    s += `<line x1="${ix}" y1="${dy}" x2="${ix + iw}" y2="${dy}" stroke="${SEC}" stroke-width="1" opacity=".7"/><line x1="${ix}" y1="${dy - 2}" x2="${ix}" y2="${dy + 2}" stroke="${SEC}" stroke-width="1"/><line x1="${ix + iw}" y1="${dy - 2}" x2="${ix + iw}" y2="${dy + 2}" stroke="${SEC}" stroke-width="1"/>`;
    s += `<rect x="${(ix + iw - 21).toFixed(1)}" y="${(iy + ih - 12).toFixed(1)}" width="19" height="10" fill="var(--paper)" stroke="${INK}" stroke-width="0.8"/><line x1="${(ix + iw - 21).toFixed(1)}" y1="${(iy + ih - 7).toFixed(1)}" x2="${(ix + iw - 2).toFixed(1)}" y2="${(iy + ih - 7).toFixed(1)}" stroke="${INK}" stroke-width="0.6" opacity=".6"/>`;   // title block
    s += `<circle cx="${(ix + iw * 0.3).toFixed(1)}" cy="${(iy + ih * 0.6).toFixed(1)}" r="3" fill="${GP}"/>`;   // single gold focal
    const lab = String(o.label || "plan").replace(/[&<>"]/g, "");
    return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" style="max-width:100%;height:auto" role="img" aria-label="${lab}">${s}</svg>`;
  }

  // projectTileGrid — a grid of project CARDS (cover region + label bar): the dashboard / gallery density.
  // Distinct from designLibraryObject (abstract design tiles); these are project covers. highlight = gold card.
  function projectTileGrid(o) {
    o = o || {};
    const cols = o.cols || 3, rows = o.rows || 2, cw = o.tile || 40, ch = o.tileH || 34, gap = o.gap || 8, bar = 9;
    const hl = (o.highlight == null) ? -1 : o.highlight;
    const W = cols * cw + (cols - 1) * gap, H = rows * (ch + bar) + (rows - 1) * gap;
    const LINE = "var(--accent-bronze-2)", GOLD = "var(--accent-gold)", GW = "var(--accent-gold-50)", GP = "var(--accent-gold-hover)";
    const uid = "pg" + (projectTileGrid._n = (projectTileGrid._n || 0) + 1), cardG = "k" + uid, covG = "v" + uid;
    let s = `<defs>` +
      `<linearGradient id="${cardG}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--paper)"/><stop offset="100%" stop-color="var(--paper-2)"/></linearGradient>` +
      `<linearGradient id="${covG}" x1="0" y1="0" x2="0.6" y2="1"><stop offset="0%" stop-color="var(--accent-gold-50)"/><stop offset="100%" stop-color="var(--accent-bronze-soft)"/></linearGradient>` +
      `</defs>`;
    let k = 0;
    for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {
      const x = c * (cw + gap), y = r * (ch + bar + gap), isHl = (k === hl), op = (0.3 + (k % 3) * 0.1).toFixed(2);
      s += `<rect x="${x}" y="${y}" width="${cw}" height="${ch + bar}" rx="4" fill="url(#${cardG})" stroke="${isHl ? GOLD : LINE}" stroke-width="${isHl ? 1.4 : 1}"/>`;
      s += `<line x1="${x + 2}" y1="${y + 1.5}" x2="${x + cw - 2}" y2="${y + 1.5}" stroke="var(--paper)" stroke-width="1" opacity=".5"/>`;   // top light
      s += `<rect x="${x + 3}" y="${y + 3}" width="${cw - 6}" height="${ch - 6}" rx="2.5" fill="${isHl ? GW : `url(#${covG})`}" opacity="${isHl ? '1' : op}"/>`;   // warm cover
      s += `<path d="M${x + 7} ${y + ch - 7} L${(x + cw * 0.4).toFixed(1)} ${y + 11} L${(x + cw * 0.6).toFixed(1)} ${y + ch - 13} L${(x + cw * 0.78).toFixed(1)} ${y + 9} L${x + cw - 7} ${y + ch - 7} Z" fill="none" stroke="${LINE}" stroke-width="1" opacity=".35"/>`;
      s += `<line x1="${x + 4}" y1="${(y + ch + bar * 0.5).toFixed(1)}" x2="${(x + cw * (isHl ? 0.5 : 0.7)).toFixed(1)}" y2="${(y + ch + bar * 0.5).toFixed(1)}" stroke="${isHl ? GP : LINE}" stroke-width="1.4" opacity="${isHl ? '.9' : '.5'}"/>`;
      k++;
    }
    const lab = String(o.label || "projects").replace(/[&<>"]/g, "");
    return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" style="max-width:100%;height:auto" role="img" aria-label="${lab}">${s}</svg>`;
  }

  // versionStack — version history rows on a lineage spine; the current (top) row gold-marked. The "iteration" artefact.
  function versionStack(o) {
    o = o || {};
    const n = Math.max(1, o.n || 3), rw = o.w || 130, rh = o.rowH || 24, gap = o.gap || 8, sx = 14;
    const cur = (o.current == null) ? 0 : o.current;
    const W = rw + sx, H = n * rh + (n - 1) * gap;
    const PAGE = "var(--paper)", LINE = "var(--accent-bronze-2)", GOLD = "var(--accent-gold)", GW = "var(--accent-gold-50)", GP = "var(--accent-gold-hover)";
    const uid = "vs" + (versionStack._n = (versionStack._n || 0) + 1), rowG = "r" + uid, covG = "c" + uid, chip = rh - 8;
    let s = `<defs>` +
      `<linearGradient id="${rowG}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--paper)"/><stop offset="100%" stop-color="var(--paper-2)"/></linearGradient>` +
      `<linearGradient id="${covG}" x1="0" y1="0" x2="0.7" y2="1"><stop offset="0%" stop-color="var(--accent-gold-50)"/><stop offset="100%" stop-color="var(--accent-bronze-soft)"/></linearGradient>` +
      `</defs>`;
    s += `<line x1="${(sx * 0.4).toFixed(1)}" y1="${rh / 2}" x2="${(sx * 0.4).toFixed(1)}" y2="${H - rh / 2}" stroke="${LINE}" stroke-width="1.4" opacity=".4"/>`;   // lineage spine
    for (let i = 0; i < n; i++) {
      const y = i * (rh + gap), isCur = (i === cur);
      if (isCur) s += `<circle cx="${(sx * 0.4).toFixed(1)}" cy="${y + rh / 2}" r="7" fill="${GP}" opacity=".18"/>`;   // current-node glow
      s += `<circle cx="${(sx * 0.4).toFixed(1)}" cy="${y + rh / 2}" r="${isCur ? 4.5 : 3}" fill="${isCur ? GP : PAGE}" stroke="${isCur ? GP : LINE}" stroke-width="1.3"/>`;
      s += `<rect x="${sx}" y="${y}" width="${rw - sx}" height="${rh}" rx="4" fill="${isCur ? GW : `url(#${rowG})`}" stroke="${isCur ? GOLD : LINE}" stroke-width="${isCur ? 1.3 : 1}"/>`;
      s += `<line x1="${sx + 1}" y1="${y + 1.5}" x2="${rw - 2}" y2="${y + 1.5}" stroke="var(--paper)" stroke-width="1" opacity=".5"/>`;   // top light edge
      s += `<rect x="${sx + 5}" y="${(y + 4).toFixed(1)}" width="${chip}" height="${chip}" rx="2" fill="url(#${covG})" opacity="${isCur ? '.7' : '.45'}"/>`;   // version thumbnail chip
      const tx = sx + 5 + chip + 6;
      s += `<line x1="${tx}" y1="${(y + rh * 0.4).toFixed(1)}" x2="${(tx + (rw - tx) * 0.6).toFixed(1)}" y2="${(y + rh * 0.4).toFixed(1)}" stroke="${LINE}" stroke-width="1.4" opacity=".6"/>`;
      s += `<line x1="${tx}" y1="${(y + rh * 0.66).toFixed(1)}" x2="${(tx + (rw - tx) * 0.4).toFixed(1)}" y2="${(y + rh * 0.66).toFixed(1)}" stroke="${LINE}" stroke-width="1" opacity=".32"/>`;
    }
    const lab = String(o.label || "versions").replace(/[&<>"]/g, "");
    return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" style="max-width:100%;height:auto" role="img" aria-label="${lab}">${s}</svg>`;
  }

  // sourcePanelVisual — the HYBRID seam made concrete: a framed panel that holds a REAL asset (o.real = url) OR a
  // synthetic horizon placeholder. SAME container either way → real assets ride the synthetic containers (contract).
  // A gold corner dot marks "real asset present"; absent = synthetic.
  function sourcePanelVisual(o) {
    o = o || {};
    const W = o.w || 130, H = o.h || 84, p = 5, iw = W - 2 * p, ih = H - 2 * p;
    const FR = "var(--accent-bronze-2)", BG = "var(--paper-2)", LINE = "var(--accent-bronze-2)", GP = "var(--accent-gold-hover)";
    const uid = "sp" + (sourcePanelVisual._n = (sourcePanelVisual._n || 0) + 1);
    let inner;
    if (o.real) {
      const src = String(o.real).replace(/["<>]/g, "");
      inner = `<clipPath id="${uid}"><rect x="${p}" y="${p}" width="${iw}" height="${ih}" rx="3"/></clipPath>` +
        `<image href="${src}" x="${p}" y="${p}" width="${iw}" height="${ih}" preserveAspectRatio="xMidYMid slice" clip-path="url(#${uid})"/>`;
    } else {
      // RICH synthetic SPACE (not line-art): a golden-hour modern-architecture render from the warm_pole ramp —
      // sky/ground gradients, sun glow, a flat-roof house silhouette with warm-lit windows, reflection + vignette
      // for depth. The DNA's "render stand-in for warm-pole imagery", pushed toward indistinguishable-from-real.
      const sky = "sky" + uid, gnd = "gnd" + uid, sun = "sun" + uid, vig = "vig" + uid;
      const hz = p + ih * 0.62, mx = p + iw * 0.16, mw = iw * 0.5, mh = ih * 0.26, mtop = hz - mh;
      inner = `<defs>` +
        `<linearGradient id="${sky}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--accent-gold-soft)"/><stop offset="58%" stop-color="var(--accent-gold-50)"/><stop offset="100%" stop-color="var(--accent-tan)"/></linearGradient>` +
        `<linearGradient id="${gnd}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--accent-tan)"/><stop offset="100%" stop-color="var(--accent-bronze-soft)"/></linearGradient>` +
        `<radialGradient id="${sun}"><stop offset="0%" stop-color="var(--accent-gold-soft)" stop-opacity=".95"/><stop offset="55%" stop-color="var(--accent-gold-50)" stop-opacity=".35"/><stop offset="100%" stop-color="var(--accent-gold-50)" stop-opacity="0"/></radialGradient>` +
        `<radialGradient id="${vig}" cx="50%" cy="40%" r="78%"><stop offset="60%" stop-color="var(--ink)" stop-opacity="0"/><stop offset="100%" stop-color="var(--ink)" stop-opacity=".18"/></radialGradient>` +
        `</defs>` +
        `<rect x="${p}" y="${p}" width="${iw}" height="${ih}" rx="3" fill="url(#${sky})"/>` +
        `<circle cx="${(p + iw * 0.7).toFixed(1)}" cy="${(p + ih * 0.32).toFixed(1)}" r="${(ih * 0.42).toFixed(1)}" fill="url(#${sun})"/>` +
        `<rect x="${p}" y="${hz.toFixed(1)}" width="${iw}" height="${(ih + p - hz).toFixed(1)}" fill="url(#${gnd})"/>` +
        `<g fill="var(--accent-bronze-2)" fill-opacity=".82">` +
          `<rect x="${mx.toFixed(1)}" y="${mtop.toFixed(1)}" width="${mw.toFixed(1)}" height="${mh.toFixed(1)}"/>` +
          `<rect x="${(mx - iw * 0.04).toFixed(1)}" y="${(mtop - ih * 0.03).toFixed(1)}" width="${(mw + iw * 0.12).toFixed(1)}" height="${(ih * 0.035).toFixed(1)}"/>` +
        `</g>` +
        `<g fill="var(--accent-gold-soft)" fill-opacity=".92">` +
          `<rect x="${(mx + mw * 0.12).toFixed(1)}" y="${(mtop + mh * 0.28).toFixed(1)}" width="${(mw * 0.16).toFixed(1)}" height="${(mh * 0.5).toFixed(1)}"/>` +
          `<rect x="${(mx + mw * 0.4).toFixed(1)}" y="${(mtop + mh * 0.28).toFixed(1)}" width="${(mw * 0.42).toFixed(1)}" height="${(mh * 0.5).toFixed(1)}"/>` +
        `</g>` +
        `<rect x="${mx.toFixed(1)}" y="${hz.toFixed(1)}" width="${mw.toFixed(1)}" height="${(ih * 0.06).toFixed(1)}" fill="var(--accent-bronze-2)" fill-opacity=".2"/>` +
        `<rect x="${p}" y="${p}" width="${iw}" height="${ih}" rx="3" fill="url(#${vig})"/>`;
    }
    const frame = `<rect x="1" y="1" width="${W - 2}" height="${H - 2}" rx="4" fill="var(--paper)" stroke="${FR}" stroke-width="1.2"/>`;
    const mark = o.real ? `<circle cx="${W - 9}" cy="9" r="3" fill="${GP}"/>` : "";
    const lab = String(o.label || (o.real ? "source image" : "image placeholder")).replace(/[&<>"]/g, "");
    return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" style="max-width:100%;height:auto" role="img" aria-label="${lab}">${frame}${inner}${mark}</svg>`;
  }

  // evidenceBand — a horizontal strip of evidence/stat chips (figure + label) with faint dividers. The credibility
  // band. Figures = MUTED gold (the figure role, Tim decision-1); labels = secondary; dividers = line.
  function evidenceBand(o) {
    o = o || {};
    const stats = (o.stats && o.stats.length) ? o.stats : [{ value: "3.2k", label: "tours" }, { value: "48", label: "projects" }, { value: "92%", label: "approved" }];
    const cw = o.chip || 78, h = o.h || 46, n = stats.length, W = n * cw;
    const GOLD = "var(--accent-gold)", SEC = "var(--ink-3)", LINE = "var(--border-default)";
    let s = "";
    stats.forEach((st, i) => {
      const cx = i * cw + cw / 2;
      s += `<text x="${cx}" y="${(h * 0.46).toFixed(1)}" text-anchor="middle" font-family="Plus Jakarta Sans,sans-serif" font-size="20" font-weight="700" fill="${GOLD}">${String(st.value).replace(/[<>&]/g, "")}</text>`;
      s += `<text x="${cx}" y="${(h * 0.78).toFixed(1)}" text-anchor="middle" font-family="Plus Jakarta Sans,sans-serif" font-size="10" font-weight="600" letter-spacing=".5" fill="${SEC}">${String(st.label).replace(/[<>&]/g, "").toUpperCase()}</text>`;
      if (i > 0) s += `<line x1="${i * cw}" y1="${(h * 0.22).toFixed(1)}" x2="${i * cw}" y2="${(h * 0.78).toFixed(1)}" stroke="${LINE}" stroke-width="1"/>`;
    });
    const lab = String(o.label || "evidence").replace(/[&<>"]/g, "");
    return `<svg width="${W}" height="${h}" viewBox="0 0 ${W} ${h}" style="max-width:100%;height:auto" role="img" aria-label="${lab}">${s}</svg>`;
  }

  // interfaceFragment — a mini product-UI chrome (title bar + sidebar rail + content panels + ONE gold primary
  // button). The "piece of the app" stand-in for app-register surfaces. Selected nav = edge+tint (not a bright focal).
  function interfaceFragment(o) {
    o = o || {};
    const W = o.w || 140, H = o.h || 92, bar = 15, rail = 28;
    const LINE = "var(--accent-bronze-2)", FAINT = "var(--border-default)", GP = "var(--accent-gold-hover)", GOLD = "var(--accent-gold)", GW = "var(--accent-gold-50)";
    const uid = "if" + (interfaceFragment._n = (interfaceFragment._n || 0) + 1), barG = "b" + uid, sideG = "s" + uid, covG = "c" + uid;
    let s = `<defs>` +
      `<linearGradient id="${barG}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--paper)"/><stop offset="100%" stop-color="var(--paper-2)"/></linearGradient>` +
      `<linearGradient id="${sideG}" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="var(--paper-2)"/><stop offset="100%" stop-color="var(--paper)"/></linearGradient>` +
      `<linearGradient id="${covG}" x1="0" y1="0" x2="0.6" y2="1"><stop offset="0%" stop-color="var(--accent-gold-50)"/><stop offset="100%" stop-color="var(--accent-bronze-soft)"/></linearGradient>` +
      `</defs>`;
    s += `<rect x="1" y="1" width="${W - 2}" height="${H - 2}" rx="6" fill="var(--paper)" stroke="${LINE}" stroke-width="1.1"/>`;
    s += `<path d="M1 7 a6 6 0 0 1 6 -6 h${W - 14} a6 6 0 0 1 6 6 v${bar - 7} h${-(W - 2)} Z" fill="url(#${barG})"/>`;
    s += `<line x1="1" y1="${bar}" x2="${W - 1}" y2="${bar}" stroke="${LINE}" stroke-width="0.8" opacity=".7"/>`;
    s += `<circle cx="9" cy="${(bar / 2).toFixed(1)}" r="2" fill="${FAINT}"/><circle cx="16" cy="${(bar / 2).toFixed(1)}" r="2" fill="${FAINT}"/><circle cx="23" cy="${(bar / 2).toFixed(1)}" r="2" fill="${FAINT}"/>`;
    s += `<rect x="${(W * 0.44).toFixed(1)}" y="${(bar * 0.26).toFixed(1)}" width="${(W * 0.4).toFixed(1)}" height="${(bar * 0.48).toFixed(1)}" rx="${(bar * 0.24).toFixed(1)}" fill="var(--paper)" stroke="${FAINT}" stroke-width="0.8"/>`;   // search pill
    s += `<rect x="1" y="${bar}" width="${rail}" height="${H - bar - 1}" fill="url(#${sideG})"/><line x1="${rail + 1}" y1="${bar}" x2="${rail + 1}" y2="${H - 1}" stroke="${LINE}" stroke-width="0.8" opacity=".45"/>`;
    for (let i = 0; i < 4; i++) {
      const ry = bar + 12 + i * 15, active = (i === 1);
      if (active) s += `<rect x="3" y="${(ry - 5.5).toFixed(1)}" width="${rail - 5}" height="13" rx="3" fill="${GW}" stroke="${GOLD}" stroke-width="0.9"/>`;
      s += `<rect x="8" y="${(ry - 2.5).toFixed(1)}" width="5" height="5" rx="1.3" fill="${active ? GOLD : FAINT}"/>`;
      s += `<line x1="16" y1="${ry}" x2="${rail - 4}" y2="${ry}" stroke="${active ? GOLD : FAINT}" stroke-width="1.5" opacity="${active ? '.9' : '.5'}"/>`;
    }
    const cx0 = rail + 8, cw = W - cx0 - 10;
    s += `<line x1="${cx0}" y1="${bar + 9}" x2="${(cx0 + cw * 0.5).toFixed(1)}" y2="${bar + 9}" stroke="${LINE}" stroke-width="2" opacity=".6"/>`;   // content header
    const cardW = (cw - 8) / 2, cardY = bar + 16, cardH = H - bar - 16 - 21;
    for (let c = 0; c < 2; c++) {
      const x = cx0 + c * (cardW + 8);
      s += `<rect x="${x.toFixed(1)}" y="${cardY}" width="${cardW.toFixed(1)}" height="${cardH}" rx="3" fill="var(--paper)" stroke="${FAINT}" stroke-width="0.8"/>`;
      s += `<rect x="${(x + 2).toFixed(1)}" y="${cardY + 2}" width="${(cardW - 4).toFixed(1)}" height="${(cardH * 0.55).toFixed(1)}" rx="2" fill="url(#${covG})" opacity="${c === 0 ? '.5' : '.34'}"/>`;
      s += `<line x1="${(x + 3).toFixed(1)}" y1="${(cardY + cardH * 0.55 + 5).toFixed(1)}" x2="${(x + cardW - 4).toFixed(1)}" y2="${(cardY + cardH * 0.55 + 5).toFixed(1)}" stroke="${LINE}" stroke-width="1" opacity=".5"/>`;
    }
    s += `<rect x="${W - 44}" y="${H - 15}" width="36" height="10" rx="3" fill="${GP}"/>`;   // single gold focal (primary action)
    const lab = String(o.label || "interface").replace(/[&<>"]/g, "");
    return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" style="max-width:100%;height:auto" role="img" aria-label="${lab}">${s}</svg>`;
  }

  // artifactFlow — input artefact → process → output, left→right with arrows. Output node is the gold accent.
  function artifactFlow(o) {
    o = o || {};
    const nodes = (o.nodes && o.nodes.length) ? o.nodes : ["in", "proc", "out"];
    const nw = o.nodeW || 38, nh = o.nodeH || 34, gap = o.gap || 24, n = nodes.length;
    const W = n * nw + (n - 1) * gap, H = nh;
    const PAGE = "var(--paper)", LINE = "var(--accent-bronze-2)", GP = "var(--accent-gold-hover)", GOLD = "var(--accent-gold)", GW = "var(--accent-gold-50)";
    let s = "";
    for (let i = 0; i < n; i++) {
      const x = i * (nw + gap), last = (i === n - 1), gx = x + nw / 2, gy = nh / 2;
      s += `<rect x="${x}" y="0" width="${nw}" height="${nh}" rx="4" fill="${last ? GW : PAGE}" stroke="${last ? GOLD : LINE}" stroke-width="${last ? 1.4 : 1}"/>`;
      if (i === 0) s += `<line x1="${x + 8}" y1="${gy - 6}" x2="${x + nw - 8}" y2="${gy - 6}" stroke="${LINE}" stroke-width="1" opacity=".55"/><line x1="${x + 8}" y1="${gy}" x2="${x + nw - 8}" y2="${gy}" stroke="${LINE}" stroke-width="1" opacity=".4"/><line x1="${x + 8}" y1="${gy + 6}" x2="${x + nw - 12}" y2="${gy + 6}" stroke="${LINE}" stroke-width="1" opacity=".4"/>`;
      else if (last) s += `<path d="M${gx - 5} ${gy + 1} l3 3 l6 -7" fill="none" stroke="${GP}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>`;
      else s += `<circle cx="${gx}" cy="${gy}" r="7" fill="none" stroke="${LINE}" stroke-width="1.3"/><circle cx="${gx}" cy="${gy}" r="2" fill="${LINE}"/>`;
      if (!last) { const ax2 = x + nw + gap; s += `<line x1="${x + nw + 3}" y1="${gy}" x2="${ax2 - 5}" y2="${gy}" stroke="${LINE}" stroke-width="1.3"/><path d="M${ax2 - 7} ${gy - 3} L${ax2 - 3} ${gy} L${ax2 - 7} ${gy + 3}" fill="none" stroke="${LINE}" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>`; }
    }
    const lab = String(o.label || "flow").replace(/[&<>"]/g, "");
    return `<svg width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" style="max-width:100%;height:auto" role="img" aria-label="${lab}">${s}</svg>`;
  }

  // artifactCluster — composes the family into ONE loose "desk" material-density hero (synthetic-rich, or with a
  // REAL asset via o.real). HTML container; children are the token SVGs, lifted (elevation ladder) + lightly
  // scattered for depth. ONE gold focal total (the real-asset dot OR the library highlight, never both).
  function artifactCluster(o) {
    o = o || {};
    const W = o.w || 300, H = o.h || 200, dense = !!o.dense;
    const L1 = "var(--elev-1)", L2 = "var(--elev-2)";
    const back = sourcePanelVisual({ w: Math.round(W * 0.5), h: Math.round(H * 0.48), real: o.real, label: o.real ? "source" : "" });
    const plan = planThumbnail({ w: Math.round(W * 0.38), h: Math.round(H * 0.32) });
    const files = fileStack({ n: 4, w: Math.round(W * 0.15), h: Math.round(H * 0.30) });
    const lib = designLibraryObject({ cols: 3, rows: 2, highlight: o.real ? -1 : 5, tile: Math.round(W * 0.07), tileH: Math.round(H * 0.065) });
    const ui = interfaceFragment({ w: Math.round(W * 0.42), h: Math.round(H * 0.36) });
    const grid = projectTileGrid({ cols: 3, rows: 2, tile: Math.round(W * 0.09), tileH: Math.round(H * 0.07) });
    const pc = (x, y, rot, sh, z, el) => `<div style="position:absolute;left:${x}%;top:${y}%;transform:rotate(${rot}deg);box-shadow:${sh};border-radius:6px;z-index:${z};background:var(--paper);padding:3px">${el}</div>`;
    // dense = the "fragmentation" pile (the source's Current-Practice panel) · sparse = a clean material-density hero
    const inner = dense
      ? pc(1, 2, -4, L1, 1, ui) + pc(34, 0, 2, L1, 2, back) + pc(2, 40, -2, L2, 5, files) +
        pc(19, 45, 3, L2, 4, plan) + pc(60, 36, 4, L1, 3, lib) + pc(52, 63, -2, L2, 6, grid)
      : pc(2, 6, -3, L1, 1, back) + pc(40, 30, 2.5, L2, 3, plan) + pc(4, 50, -1.5, L2, 4, files) + pc(58, 4, 3.5, L1, 2, lib);
    const lab = String(o.label || "artefacts").replace(/[&<>"]/g, "");
    return `<div role="img" aria-label="${lab}" style="position:relative;width:${W}px;height:${H}px;max-width:100%">${inner}</div>`;
  }

  // boardGroups — the board-view render: grouped sections (one card per group), each = a header (group name +
  // gold count) + item rows (label + channel + state). HTML; tokens-only; material (page card, nested header,
  // lift). Consumes DNA.faceRecord.boardRecord(rows).groups. v1 of board-view's shape slot.
  function boardGroups(o) {
    o = o || {};
    const groups = o.groups || [], W = o.w || 720;
    const esc = (s) => String(s == null ? "" : s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
    const stateCol = (s) => /(living|active|live|open|pending)/i.test(s) ? "var(--accent-gold)" : "var(--ink-3)";
    const sections = groups.map((g) => {
      const rows = (g.items || []).map((it) =>
        `<div style="display:flex;align-items:center;gap:8px;padding:7px 11px;border-top:1px solid var(--border-default)">` +
          `<span style="flex:1;min-width:0;font-size:13px;color:var(--ink-2);line-height:1.3;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">${esc(it.label)}</span>` +
          (it.channel ? `<span style="font-family:'IBM Plex Mono',monospace;font-size:10px;color:var(--ink-3)">${esc(it.channel)}</span>` : "") +
          (it.state ? `<span style="font-size:10px;font-weight:600;color:${stateCol(it.state)};text-transform:uppercase;letter-spacing:.4px">${esc(it.state)}</span>` : "") +
        `</div>`).join("");
      return `<div style="background:var(--paper);border:1px solid var(--border-default);border-radius:12px;overflow:hidden;box-shadow:var(--elev-1)">` +
        `<div style="display:flex;align-items:center;gap:8px;padding:9px 12px;background:var(--paper-2)">` +
          `<span style="flex:1;font-size:13px;font-weight:700;color:var(--ink);text-transform:capitalize">${esc(g.group)}</span>` +
          `<span style="font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:600;color:var(--accent-gold)">${g.count}</span>` +
        `</div>${rows}</div>`;
    }).join("");
    return `<div role="img" aria-label="board" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;align-items:start;width:100%;max-width:${W}px;margin:0 auto">${sections}</div>`;
  }

  // constellation — the transcript-viz render: a STAR-FIELD over a query. RAW mode = session star-nodes (brighter =
  // more relevant → toward centre + glow; bigger = matched denser; colour = live-state). GROUNDED mode = theme-stars
  // (gold) with claim-satellites orbiting (the "what the corpus says" 2-level). Honest degrade (lexical fallback →
  // dimmed + flagged, never a fabricated-confident map). Consumes DNA.faceRecord.transcriptRecord. Tokens-only.
  function constellation(data, o) {
    o = o || {}; data = data || {};
    const W = o.w || 600, H = o.h || 400, cx = W / 2, cy = H / 2;
    const esc = (s) => String(s == null ? "" : s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
    const clip = (s, n) => { s = String(s || ""); return s.length > n ? s.slice(0, n - 1) + "…" : s; };
    const rnd = mulberry32(o.seed || 7);
    const statusCol = (s) => /(supervised-live|live|active)/i.test(s || "") ? "var(--accent-gold-hover)" : /closed/i.test(s || "") ? "var(--accent-bronze)" : "var(--accent-gold-deep)";
    const star = (x, y, r, glow, col, lab) =>
      `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${(r + glow * 4).toFixed(1)}" fill="${col}" opacity="${(0.08 + glow * 0.16).toFixed(2)}"/>` +
      `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r.toFixed(1)}" fill="${col}" opacity="${(0.5 + glow * 0.45).toFixed(2)}"/>` +
      (lab ? `<text x="${x.toFixed(1)}" y="${(y - r - 4).toFixed(1)}" text-anchor="middle" font-family="Plus Jakarta Sans,sans-serif" font-size="10" fill="var(--ink-2)">${esc(clip(lab, 22))}</text>` : "");
    let body = "";
    if (data.mode === "grounded" && (data.clusters || []).length) {
      const themes = data.clusters, n = themes.length, R = Math.min(W, H) * 0.3;
      themes.forEach((t, i) => {
        const a = -Math.PI / 2 + i * 2 * Math.PI / n, tx = cx + (n > 1 ? R : 0) * Math.cos(a), ty = cy + (n > 1 ? R : 0) * Math.sin(a);
        const claims = (t.claims || []).slice(0, 8);
        claims.forEach((c, j) => {
          const ca = j * 2 * Math.PI / Math.max(1, claims.length), cr = 34 + (j % 2) * 12;
          const sx = tx + cr * Math.cos(ca), sy = ty + cr * Math.sin(ca);
          body += `<line x1="${tx.toFixed(1)}" y1="${ty.toFixed(1)}" x2="${sx.toFixed(1)}" y2="${sy.toFixed(1)}" stroke="var(--accent-bronze-2)" stroke-width="0.8" opacity=".3"/>`;
          body += star(sx, sy, 3, 0.3, "var(--accent-gold-deep)", "");
        });
        body += star(tx, ty, 7, 0.85, "var(--accent-gold)", t.label);
      });
    } else {
      // phyllotaxis (golden-angle) spread: brightest → centre, dimmest → edge, sqrt(rank) for even AREA fill →
      // a galaxy, not a central clump; bounded within maxR (margin from the edges); label only the brightest few.
      const nodes = (data.nodes || []).slice(0, 40).slice().sort((p, q) => (q.brightness || 0) - (p.brightness || 0));
      const maxR = Math.min(W, H) * 0.4, GA = 2.399963, N = nodes.length;
      nodes.forEach((nd, i) => {
        const b = Math.max(0, Math.min(1, nd.brightness || 0.5));
        const rank = N > 1 ? i / (N - 1) : 0;
        const ang = i * GA, rad = Math.sqrt(rank) * maxR;
        const x = cx + rad * Math.cos(ang), y = cy + rad * Math.sin(ang);
        const r = 2.5 + Math.min(6, (nd.weight || 1) * 0.8);
        body += star(x, y, r, b, statusCol(nd.status), i < 5 ? nd.label : "");
      });
    }
    const dim = data.degraded
      ? `<rect x="0" y="0" width="${W}" height="${H}" fill="var(--ink)" opacity=".05"/><text x="12" y="${H - 12}" font-family="'IBM Plex Mono',monospace" font-size="10" fill="var(--ink-3)">degraded — lexical fallback (semantic search down)</text>`
      : "";
    const lab = String(o.label || data.query || "constellation").replace(/[&<>"]/g, "");
    // display:block + width:100% + height:auto (via viewBox) = the reliable responsive-SVG sizing; max-width caps
    // it at W so it doesn't over-blow; overflow:hidden clips any edge glow to the field. (Was max-width-only +
    // height:auto → collapsed to 0×0 → content overflowed/scattered; by-use caught it.)
    return `<svg viewBox="0 0 ${W} ${H}" preserveAspectRatio="xMidYMid meet" style="display:block;width:100%;height:auto;max-width:${W}px;margin:0 auto;overflow:hidden" role="img" aria-label="${lab}"><rect width="${W}" height="${H}" fill="var(--paper-2)"/>${body}${dim}</svg>`;
  }

  // navRail — the SURFACE NAVIGATION: a rail of icon+label tiles, one per operator face (decisions · the V ·
  // channels · board · transcript · …), the active one gold-marked. Operator-law: HUMAN labels (always shown —
  // the icon is a decorator that degrades to "" if absent), navigable-not-a-menu-wall (a visual tile rail). The
  // HOST (projection) wires each tile's data-nav → setView(<id>). Horizontal by default; o.vertical = a side rail.
  function navRail(o) {
    o = o || {};
    const items = o.items || [], active = o.active || "";
    const esc = (s) => String(s == null ? "" : s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
    const iconSVG = (global.DNA && global.DNA.iconSVG) ? global.DNA.iconSVG : function () { return ""; };
    const tiles = items.map((it) => {
      const isA = (it.id === active) || !!it.active;
      const ic = it.icon ? iconSVG(it.icon, { size: 18 }) : "";
      return `<button class="dna-nav-tile${isA ? " active" : ""}" type="button" data-nav="${esc(it.id)}" aria-current="${isA ? "page" : "false"}" title="${esc(it.label)}">` +
        (ic ? `<span class="dna-nav-ico">${ic}</span>` : "") +
        `<span class="dna-nav-lab">${esc(it.label)}</span>` +
      `</button>`;
    }).join("");
    return `<nav class="dna-nav${o.vertical ? " v" : ""}" role="navigation" aria-label="${esc(o.label || "surfaces")}">${tiles}</nav>`;
  }

  global.DNA = global.DNA || {};
  global.DNA.org = { icon, iconStrip, mesh, hubNetwork, graph, consequencesBox, cascade, detailStrip, phaseStrip, testimonial, checkMatrix, donut, bars, ordinalVar, connector, taxonomyEmergence, designLibraryObject, fileStack, planThumbnail, projectTileGrid, versionStack, sourcePanelVisual, evidenceBand, interfaceFragment, artifactFlow, artifactCluster, boardGroups, constellation, navRail, _icons: Object.keys(P) };
})(window);
