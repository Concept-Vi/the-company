// canvases/workshop/Export.jsx — real exporters with motif/bleed support
// - Standalone HTML / PDF use the same buildStandaloneHtml with motif backgrounds
// - PPTX colors each slide based on its motif

const { useState: useState_x } = React;

window.WSExport = function exportDoc(doc, format) {
  if (!doc) return;
  if (format === 'html') return exportHtml(doc);
  if (format === 'pdf')  return exportPdf(doc);
  if (format === 'pptx') return exportPptx(doc);
  throw new Error('Unknown export format: ' + format);
};

function exportHtml(doc) {
  const html = buildStandaloneHtml(doc);
  const blob = new Blob([html], { type: 'text/html' });
  triggerDownload(blob, doc.title.replace(/[^a-z0-9-]+/gi, '-').toLowerCase() + '.html');
}

function exportPdf(doc) {
  const html = buildStandaloneHtml(doc, { print: true });
  const w = window.open('', '_blank');
  if (!w) { window.dsaToast?.('Pop-up blocked — allow pop-ups for export'); return; }
  w.document.open(); w.document.write(html); w.document.close();
  setTimeout(() => { try { w.focus(); w.print(); } catch {} }, 600);
}

// ============================================================
// Motif CSS per id — mirrored from workshop.css but inlined for standalone export
// ============================================================
const MOTIF_CSS = {
  ivory:    'background: var(--canvas);',
  paper:    'background: radial-gradient(circle at 30% 20%, rgba(152,128,88,.04) 0 1px, transparent 1px) 0 0/13px 13px, radial-gradient(circle at 70% 60%, rgba(152,128,88,.04) 0 1px, transparent 1px) 0 0/23px 23px, var(--canvas);',
  blueprint:'background: linear-gradient(rgba(224,192,16,.10) 1px, transparent 1px) 0 0/24px 24px, linear-gradient(90deg, rgba(224,192,16,.10) 1px, transparent 1px) 0 0/24px 24px, var(--canvas);',
  edgeband: 'background: var(--canvas); position: relative; padding-left: 96px !important;',
  watermark:'background: var(--canvas); position: relative;',
  ink:      'background: radial-gradient(ellipse at 80% 0%, rgba(224,192,16,.06), transparent 50%), radial-gradient(ellipse at 0% 100%, rgba(152,128,88,.08), transparent 50%), var(--dark);',
  goldBleed:'background: radial-gradient(ellipse at 80% 100%, rgba(31,26,18,.08), transparent 50%), var(--gold);',
  section:  'background: linear-gradient(135deg, rgba(31,26,18,.15), transparent), var(--bronze);',
};

function motifFor(doc, page) {
  return (window.WS_resolveMotif ? window.WS_resolveMotif(doc, page) : null) || 'ivory';
}
function bleedFor(motif) {
  return window.WS_MOTIFS?.[motif]?.bleed || 'light';
}

function buildStandaloneHtml(doc, opts = {}) {
  const isDeck = doc.type === 'deck';
  const cssVars = `:root { --gold:#E0C010;--gold-hover:#C8AB0E;--gold-soft:#F4E89A;--gold-50:#FBF4C8;--bronze:#988058;--canvas:#FBF7EC;--surface:#fff;--dark:#1F1A12;--fg:#1F1A12;--fg2:#6B5F47;--fg-inv:#FBF7EC;--bd:#E8DFC5; }`;
  const baseCss = `
* { box-sizing: border-box; }
body { margin:0; font-family: 'DM Sans', system-ui, sans-serif; background: var(--canvas); color: var(--fg); -webkit-font-smoothing: antialiased; }
.frame { border-radius: 12px; padding: 48px 60px; margin: 20px auto; max-width: ${isDeck ? '1100px' : '760px'}; position: relative; overflow: hidden; box-shadow: 0 1px 2px rgba(31,26,18,.04), 0 4px 14px rgba(31,26,18,.05); ${isDeck ? 'aspect-ratio: 16/9; display: flex; flex-direction: column; justify-content: center; gap: 16px;' : ''} }
.frame.bleed-dark { color: var(--fg-inv); }
.frame.bleed-dark .eyebrow { color: var(--gold); }
.frame.bleed-dark h1, .frame.bleed-dark p { color: var(--fg-inv); }
.frame.bleed-dark .quote { color: var(--gold); border-left-color: var(--gold); }
.frame.bleed-dark .quote .who { color: rgba(251,247,236,.7); }
.frame.bleed-dark .stat { background: rgba(251,247,236,.08); }
.frame.bleed-dark .stat .v { color: var(--gold); }
.frame.bleed-dark .stat .l { color: rgba(251,247,236,.7); }
.frame.bleed-dark .icons .ring { border-color: var(--gold); color: var(--gold); }
.frame.bleed-dark .icons .lbl { color: rgba(251,247,236,.9); }
.frame.bleed-dark .callout { background: rgba(251,247,236,.06); border-left-color: var(--gold); }
.frame.bleed-gold { color: var(--fg); }
.frame.bleed-gold .eyebrow { color: var(--fg); opacity: 0.85; }
.frame.bleed-gold .quote { border-left-color: var(--fg); color: var(--fg); }
.watermark-mark { position: absolute; right: -40px; bottom: -40px; width: 280px; height: 280px; pointer-events: none; z-index: 0; }
.section-mark { position: absolute; left: 50%; top: 50%; transform: translate(-50%,-50%); width: 360px; height: 360px; pointer-events: none; z-index: 0; }
.frame > *:not(.watermark-mark):not(.section-mark) { position: relative; z-index: 1; }
.eyebrow { font: 600 12px/1 sans-serif; color: var(--bronze); letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 8px; }
h1 { font: 700 44px/1.05 'Sora', sans-serif; letter-spacing: -0.025em; margin: 0 0 10px; }
p { font: 400 16px/1.6 'DM Sans', sans-serif; margin: 0 0 14px; max-width: 64ch; }
.hero { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; align-items: center; min-height: 220px; }
.hero-img { border-radius: 8px; aspect-ratio: 4/3; background: linear-gradient(135deg, var(--gold-soft), #E8E2CC); display: flex; align-items: center; justify-content: center; color: var(--bronze); font: 600 11px/1 sans-serif; letter-spacing: 0.08em; text-transform: uppercase; }
.btn { display: inline-flex; align-items: center; gap: 8px; background: var(--gold); color: var(--fg); border: none; padding: 12px 22px; border-radius: 8px; font: 700 13px/1 sans-serif; cursor: pointer; text-decoration: none; }
.quote { font: 600 22px/1.35 'Sora', sans-serif; color: var(--bronze); border-left: 3px solid var(--gold); padding-left: 18px; margin: 0; } .quote .who { display: block; font: 400 13px/1 sans-serif; color: var(--fg2); margin-top: 8px; }
.icons { display: flex; gap: 16px; flex-wrap: wrap; } .icons .item { display: flex; flex-direction: column; align-items: center; gap: 6px; min-width: 80px; } .icons .ring { width: 48px; height: 48px; border-radius: 50%; border: 1.5px solid var(--gold); display: flex; align-items: center; justify-content: center; color: var(--bronze); } .icons .lbl { font: 500 11px/1.3 sans-serif; text-align: center; }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 12px; } .stat { background: var(--gold-50); border-radius: 8px; padding: 14px 16px; text-align: center; } .stat .v { font: 700 32px/1 'Sora', sans-serif; color: var(--bronze); } .stat .l { font: 500 11px/1.3 sans-serif; color: var(--fg2); margin-top: 4px; }
.palette { display: flex; gap: 8px; } .palette .sw { flex: 1; min-height: 60px; border-radius: 6px; position: relative; } .palette .sw .h { position: absolute; bottom: 4px; left: 6px; font: 500 9px/1 monospace; }
.callout { background: var(--gold-50); border-left: 4px solid var(--gold); border-radius: 8px; padding: 16px 20px; font: 500 14px/1.55 sans-serif; } .callout .lbl { display: block; font: 700 10px/1 sans-serif; color: var(--bronze); letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 6px; }
.img-slot { background: linear-gradient(135deg, #E8E2CC, var(--gold-soft)); border-radius: 8px; min-height: 180px; display: flex; align-items: center; justify-content: center; color: var(--bronze); font: 600 11px/1 sans-serif; letter-spacing: 0.08em; text-transform: uppercase; }
.divider { height: 1px; background: var(--bd); margin: 14px 0; }
.deck-title { padding: 32px 48px 16px; max-width: 1200px; margin: 0 auto; font-family: 'Sora', sans-serif; font-weight: 700; font-size: 28px; letter-spacing: -0.02em; color: var(--bronze); }
.deck-wrap { max-width: 1200px; margin: 0 auto; padding: 0 24px 48px; }
@page { size: ${isDeck ? 'landscape' : 'A4 portrait'}; margin: 0; }
@media print { body { background: white; margin: 0; } .frame { box-shadow: none; margin: 0; ${isDeck ? '' : 'min-height: 100vh;'} page-break-after: always; border-radius: 0; max-width: none; } .deck-title, .deck-wrap { padding: 0; max-width: none; } }
`;
  const watermarkSvg = `<svg class="watermark-mark" viewBox="0 0 100 100"><polygon points="50,8 92,50 50,92 8,50" fill="none" stroke="#E0C010" stroke-width="1.5" opacity="0.16"/><polygon points="50,8 92,50 50,92 8,50" fill="#E0C010" opacity="0.04"/></svg>`;
  const sectionSvg = `<svg class="section-mark" viewBox="0 0 100 100"><polygon points="50,8 92,50 50,92 8,50" fill="none" stroke="#FBF7EC" stroke-width="1" opacity="0.5"/><polygon points="50,8 92,50 50,92 8,50" fill="#FBF7EC" opacity="0.06"/></svg>`;
  const body = doc.pages.map(p => {
    const motif = motifFor(doc, p);
    const bleed = bleedFor(motif);
    const motifCss = MOTIF_CSS[motif] || MOTIF_CSS.ivory;
    const overlay = motif === 'watermark' ? watermarkSvg : motif === 'section' ? sectionSvg : '';
    const sections = p.sections.map(blockToHtml).join('');
    return `<div class="frame bleed-${bleed}" style="${motifCss}">${overlay}${sections}</div>`;
  }).join('\n');
  const fonts = `<link href="https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700&family=DM+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">`;
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>${escapeHtml(doc.title)}</title>${fonts}<style>${cssVars}${baseCss}</style></head><body>${isDeck ? `<div class="deck-title">${escapeHtml(doc.title)}</div><div class="deck-wrap">${body}</div>` : body}</body></html>`;
}

function blockToHtml(sec) {
  const d = sec.data || {};
  switch (sec.kind) {
    case 'hero':
      return `<div class="hero"><div>${d.eyebrow ? `<div class="eyebrow">${escapeHtml(d.eyebrow)}</div>` : ''}<h1>${escapeHtml(d.headline || '')}</h1><p>${escapeHtml(d.body || '')}</p>${d.cta ? `<a class="btn">${escapeHtml(d.cta)} <span>→</span></a>` : ''}</div><div class="hero-img">${escapeHtml(d.imageLabel || 'Hero image')}</div></div>`;
    case 'headline':
      return `${d.eyebrow ? `<div class="eyebrow">${escapeHtml(d.eyebrow)}</div>` : ''}<h1>${escapeHtml(d.text || '')}</h1>`;
    case 'body':
      return `<p>${escapeHtml(d.text || '')}</p>`;
    case 'quote':
      return `<blockquote class="quote">"${escapeHtml(d.text || '')}"<span class="who">${escapeHtml(d.who || '')}</span></blockquote>`;
    case 'icons':
      return `<div class="icons">${(d.items || []).map(it => {
        const icon = window.CV_ICONS?.data?.[it.icon];
        return `<div class="item"><div class="ring">${icon ? `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">${icon}</svg>` : '•'}</div><div class="lbl">${escapeHtml(it.label || '')}</div></div>`;
      }).join('')}</div>`;
    case 'stats':
      return `<div class="stats">${(d.items || []).map(it => `<div class="stat"><div class="v">${escapeHtml(it.v || '')}</div><div class="l">${escapeHtml(it.l || '')}</div></div>`).join('')}</div>`;
    case 'palette':
      return `<div class="palette">${(d.colors || []).map(c => `<div class="sw" style="background:${c.h}"><span class="h" style="color:${window.isLight?.(c.h) ? '#1F1A12' : '#FBF7EC'}">${c.h}</span></div>`).join('')}</div>`;
    case 'button':
      return `<div><a class="btn">${escapeHtml(d.text || 'Button')}</a></div>`;
    case 'callout':
      return `<div class="callout"><span class="lbl">${escapeHtml(d.label || '')}</span>${escapeHtml(d.text || '')}</div>`;
    case 'image':
      return `<div class="img-slot">${escapeHtml(d.label || 'Image')}</div>`;
    case 'divider':
      return `<div class="divider"></div>`;
    default: return '';
  }
}

function escapeHtml(s) {
  return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename;
  document.body.appendChild(a); a.click();
  setTimeout(() => { document.body.removeChild(a); URL.revokeObjectURL(url); }, 100);
}

// ============================================================
// PPTX (deck) — PptxGenJS client-side with motif-aware backgrounds
// ============================================================
async function loadPptx() {
  if (window.PptxGenJS) return window.PptxGenJS;
  await new Promise((res, rej) => {
    const s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/pptxgenjs@3.12.0/dist/pptxgen.bundle.js';
    s.onload = res; s.onerror = rej;
    document.head.appendChild(s);
  });
  return window.PptxGenJS;
}

// Background color per motif (PPTX is limited — solid colors only for backgrounds)
const PPTX_BG = {
  ivory:    'FBF7EC',
  paper:    'FBF7EC',
  blueprint:'FBF7EC',
  edgeband: 'FBF7EC',
  watermark:'FBF7EC',
  ink:      '1F1A12',
  goldBleed:'E0C010',
  section:  '988058',
};

async function exportPptx(doc) {
  if (doc.type !== 'deck') {
    window.dsaToast?.('PPTX export is for slide decks only — use PDF or HTML instead');
    return;
  }
  window.dsaToast?.('Building .pptx — one moment…');
  const PptxGenJS = await loadPptx();
  const pptx = new PptxGenJS();
  pptx.layout = 'LAYOUT_WIDE';
  pptx.title = doc.title;

  const GOLD = 'E0C010', BRONZE = '988058', FG = '1F1A12', FG2 = '6B5F47', GOLD_50 = 'FBF4C8', CREAM = 'FBF7EC';

  doc.pages.forEach((page, pageIdx) => {
    const motif = motifFor(doc, page);
    const bleed = bleedFor(motif);
    const slide = pptx.addSlide();
    slide.background = { color: PPTX_BG[motif] || CREAM };

    // Bleed-aware text colors
    const TXT = bleed === 'dark' ? CREAM : bleed === 'gold' ? FG : FG;
    const TXT2 = bleed === 'dark' ? 'B3A98E' : bleed === 'gold' ? FG : FG2;
    const EYEBROW = bleed === 'dark' ? GOLD : bleed === 'gold' ? FG : BRONZE;
    const ACCENT = bleed === 'dark' ? GOLD : bleed === 'gold' ? FG : BRONZE;
    const STAT_BG = bleed === 'dark' ? '2A2620' : bleed === 'gold' ? 'C8AB0E' : GOLD_50;

    // Edge band motif draws a gold band on the left
    let leftPad = 0.7;
    if (motif === 'edgeband') {
      slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 0.4, h: 7.5, fill: { color: GOLD }, line: { type: 'none' } });
      leftPad = 1.1;
    }
    // Watermark / section overlays (PPTX has no shadow/blur — we just add a subtle V shape)
    if (motif === 'watermark') {
      slide.addShape(pptx.ShapeType.diamond, { x: 9.5, y: 4.5, w: 3.2, h: 3.2, fill: { type: 'none' }, line: { color: GOLD, width: 1, transparency: 84 } });
    }
    if (motif === 'section') {
      slide.addShape(pptx.ShapeType.diamond, { x: 4.2, y: 1.5, w: 4.9, h: 4.9, fill: { type: 'none' }, line: { color: CREAM, width: 1, transparency: 50 } });
    }

    let y = 0.5;
    const slideW = 13.333;
    const usableW = slideW - leftPad - 0.7;

    page.sections.forEach(sec => {
      const d = sec.data || {};
      switch (sec.kind) {
        case 'hero': {
          const halfW = usableW / 2 - 0.15;
          if (d.eyebrow) { slide.addText(d.eyebrow, { x: leftPad, y, w: halfW, h: 0.3, fontFace: 'DM Sans', fontSize: 11, bold: true, color: EYEBROW, charSpacing: 2 }); y += 0.32; }
          slide.addText(d.headline || '', { x: leftPad, y, w: halfW, h: 1.0, fontFace: 'Sora', fontSize: 32, bold: true, color: TXT });
          slide.addText(d.body || '', { x: leftPad, y: y + 1.1, w: halfW, h: 1.2, fontFace: 'DM Sans', fontSize: 13, color: TXT2 });
          if (d.cta) {
            slide.addShape(pptx.ShapeType.roundRect, { x: leftPad, y: y + 2.4, w: 1.6, h: 0.45, fill: { color: GOLD }, line: { type: 'none' }, rectRadius: 0.08 });
            slide.addText(d.cta, { x: leftPad, y: y + 2.4, w: 1.6, h: 0.45, fontFace: 'DM Sans', fontSize: 12, bold: true, color: FG, align: 'center' });
          }
          slide.addShape(pptx.ShapeType.rect, { x: leftPad + halfW + 0.3, y, w: halfW, h: 3.2, fill: { color: 'E8E2CC' }, line: { type: 'none' } });
          slide.addText(d.imageLabel || 'Hero image', { x: leftPad + halfW + 0.3, y, w: halfW, h: 3.2, fontFace: 'DM Sans', fontSize: 11, bold: true, color: BRONZE, align: 'center', valign: 'middle', charSpacing: 2 });
          y += 3.4;
          break;
        }
        case 'headline': {
          if (d.eyebrow) { slide.addText(d.eyebrow, { x: leftPad, y, w: usableW, h: 0.3, fontFace: 'DM Sans', fontSize: 11, bold: true, color: EYEBROW, charSpacing: 2 }); y += 0.32; }
          slide.addText(d.text || '', { x: leftPad, y, w: usableW, h: 1.2, fontFace: 'Sora', fontSize: 40, bold: true, color: TXT });
          y += 1.3;
          break;
        }
        case 'body': {
          slide.addText(d.text || '', { x: leftPad, y, w: usableW, h: 1.2, fontFace: 'DM Sans', fontSize: 14, color: TXT });
          y += 1.3;
          break;
        }
        case 'quote': {
          slide.addShape(pptx.ShapeType.rect, { x: leftPad, y, w: 0.04, h: 1.4, fill: { color: GOLD }, line: { type: 'none' } });
          slide.addText(`"${d.text || ''}"`, { x: leftPad + 0.2, y, w: usableW - 0.2, h: 1.0, fontFace: 'Sora', fontSize: 22, bold: true, color: ACCENT });
          slide.addText(d.who || '', { x: leftPad + 0.2, y: y + 1.0, w: usableW - 0.2, h: 0.3, fontFace: 'DM Sans', fontSize: 12, color: TXT2 });
          y += 1.5;
          break;
        }
        case 'icons': {
          const items = d.items || [];
          const iconW = Math.min(1.4, usableW / Math.max(items.length, 1));
          items.forEach((it, i) => {
            const x = leftPad + i * iconW;
            slide.addShape(pptx.ShapeType.ellipse, { x: x + iconW/2 - 0.3, y, w: 0.6, h: 0.6, fill: { type: 'none' }, line: { color: GOLD, width: 1.5 } });
            slide.addText(it.label || '', { x, y: y + 0.7, w: iconW, h: 0.4, fontFace: 'DM Sans', fontSize: 11, color: TXT, align: 'center' });
          });
          y += 1.3;
          break;
        }
        case 'stats': {
          const items = d.items || [];
          const statW = Math.min(2.4, usableW / Math.max(items.length, 1));
          items.forEach((it, i) => {
            const x = leftPad + i * (statW + 0.1);
            slide.addShape(pptx.ShapeType.roundRect, { x, y, w: statW, h: 1.2, fill: { color: STAT_BG }, line: { type: 'none' }, rectRadius: 0.08 });
            slide.addText(it.v || '', { x, y, w: statW, h: 0.7, fontFace: 'Sora', fontSize: 30, bold: true, color: ACCENT, align: 'center', valign: 'middle' });
            slide.addText(it.l || '', { x, y: y + 0.75, w: statW, h: 0.4, fontFace: 'DM Sans', fontSize: 10, color: TXT2, align: 'center' });
          });
          y += 1.4;
          break;
        }
        case 'palette': {
          const cols = d.colors || [];
          const cw = usableW / Math.max(cols.length, 1);
          cols.forEach((c, i) => {
            const x = leftPad + i * cw;
            slide.addShape(pptx.ShapeType.rect, { x: x + 0.05, y, w: cw - 0.1, h: 0.8, fill: { color: (c.h || '').replace('#','') }, line: { type: 'none' } });
            slide.addText(c.h || '', { x: x + 0.05, y: y + 0.55, w: cw - 0.1, h: 0.3, fontFace: 'Courier', fontSize: 9, color: 'FFFFFF' });
          });
          y += 0.9;
          break;
        }
        case 'callout': {
          slide.addShape(pptx.ShapeType.roundRect, { x: leftPad, y, w: usableW, h: 1.0, fill: { color: STAT_BG }, line: { type: 'none' }, rectRadius: 0.08 });
          slide.addShape(pptx.ShapeType.rect, { x: leftPad, y, w: 0.06, h: 1.0, fill: { color: GOLD }, line: { type: 'none' } });
          if (d.label) slide.addText(d.label, { x: leftPad + 0.2, y: y + 0.1, w: usableW - 0.3, h: 0.25, fontFace: 'DM Sans', fontSize: 9, bold: true, color: EYEBROW, charSpacing: 2 });
          slide.addText(d.text || '', { x: leftPad + 0.2, y: y + 0.35, w: usableW - 0.3, h: 0.6, fontFace: 'DM Sans', fontSize: 13, color: TXT });
          y += 1.15;
          break;
        }
        case 'button': {
          slide.addShape(pptx.ShapeType.roundRect, { x: leftPad, y, w: 1.8, h: 0.5, fill: { color: GOLD }, line: { type: 'none' }, rectRadius: 0.08 });
          slide.addText(d.text || 'Button', { x: leftPad, y, w: 1.8, h: 0.5, fontFace: 'DM Sans', fontSize: 13, bold: true, color: FG, align: 'center', valign: 'middle' });
          y += 0.65;
          break;
        }
        case 'image': {
          slide.addShape(pptx.ShapeType.rect, { x: leftPad, y, w: usableW, h: 1.8, fill: { color: 'E8E2CC' }, line: { type: 'none' } });
          slide.addText(d.label || 'Image', { x: leftPad, y, w: usableW, h: 1.8, fontFace: 'DM Sans', fontSize: 11, bold: true, color: BRONZE, align: 'center', valign: 'middle', charSpacing: 2 });
          y += 1.95;
          break;
        }
        case 'divider': {
          slide.addShape(pptx.ShapeType.line, { x: leftPad, y: y + 0.1, w: usableW, h: 0, line: { color: 'E8DFC5', width: 1 } });
          y += 0.3;
          break;
        }
      }
      y += 0.15;
    });
  });

  const filename = doc.title.replace(/[^a-z0-9-]+/gi, '-').toLowerCase() + '.pptx';
  await pptx.writeFile({ fileName: filename });
  window.dsaToast?.(`Exported "${filename}"`);
}

// ============================================================
// ExportMenu — pops up next to the Export button
// ============================================================
window.WSExportMenu = function ExportMenu({ doc, onClose }) {
  const [busy, setBusy] = useState_x(null);
  async function go(fmt) {
    setBusy(fmt);
    try { await window.WSExport(doc, fmt); }
    catch (err) { window.dsaToast?.('Export failed: ' + (err.message || err)); }
    finally { setBusy(null); onClose(); }
  }
  const isDeck = doc.type === 'deck';
  const opts = [
    { id: 'html', label: 'Standalone HTML', desc: 'Single .html file with motifs baked in.', icon: 'globe' },
    { id: 'pdf',  label: 'Print to PDF',    desc: 'Opens print dialog — choose "Save as PDF".', icon: 'file-pdf' },
    isDeck && { id: 'pptx', label: 'PowerPoint .pptx', desc: 'Editable, with motif backgrounds.', icon: 'file' },
  ].filter(Boolean);
  return (
    <div style={{
      position:'absolute', top: '100%', right: 0, marginTop: 6,
      background:'var(--bg-surface)', border:'1.5px solid var(--accent-gold)',
      borderRadius:'var(--r-md)', padding: 8, boxShadow:'var(--shadow-pop)',
      width: 280, zIndex: 100,
    }} onClick={e => e.stopPropagation()}>
      <div style={{font:'700 10px/1 var(--font-body)',color:'var(--fg-muted)',letterSpacing:'0.08em',textTransform:'uppercase',padding:'6px 8px 8px'}}>Export</div>
      {opts.map(o => (
        <button key={o.id}
          onClick={() => go(o.id)}
          disabled={busy != null}
          style={{
            display:'flex',alignItems:'center',gap:10,
            width:'100%',padding:'10px 10px',borderRadius:'var(--r-sm)',
            background: busy === o.id ? 'var(--accent-gold-50)' : 'transparent',
            border:'none', cursor: busy ? 'wait' : 'pointer', textAlign:'left',
            opacity: busy && busy !== o.id ? 0.4 : 1,
          }}
        >
          <CvIcon name={o.icon} size={18} tone="bronze"/>
          <div style={{flex:1}}>
            <div style={{font:'600 13px/1.2 var(--font-body)',color:'var(--fg-primary)'}}>{o.label}{busy === o.id ? ' …' : ''}</div>
            <div style={{font:'400 11px/1.3 var(--font-body)',color:'var(--fg-muted)',marginTop:2}}>{o.desc}</div>
          </div>
        </button>
      ))}
    </div>
  );
};
