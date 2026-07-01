// canvases/Workshop.jsx — visual canvas for composing real deliverables
// Doc types: deck + brochure live; website, social, email, video coming soon.

const { useState: useState_w, useEffect: useEffect_w, useMemo: useMemo_w, useRef: useRef_w } = React;

const DOC_TYPES = [
  { id: 'deck',      label: 'Slide deck',      desc: 'Pitch, sales, all-hands. 16:9 slides with structured sections.', icon: 'browser',          active: true },
  { id: 'brochure',  label: 'One-page brochure',desc: 'Sales collateral, property sheets. A4 portrait, one page.',     icon: 'document',         active: true },
  { id: 'widget',    label: 'Widget',           desc: 'Dashboard tile, hub panel, or partner embed. KPI, media, or hybrid systems.', icon: 'check-square',    active: true },
  { id: 'wizard',    label: 'Wizard',           desc: 'Multi-step flow — Property Wizard, onboarding, or generic.', icon: 'atom',          active: true },
  { id: 'website',   label: 'Website',         desc: 'Marketing site, multi-page. Composable hero + sections.',        icon: 'browser-house',    active: false },
  { id: 'social',    label: 'Social tile',     desc: 'LinkedIn / Instagram squares, story formats.',                   icon: 'image',            active: false },
  { id: 'email',     label: 'Email layout',    desc: 'Newsletters, transactional, broadcast.',                         icon: 'email',            active: false },
  { id: 'video',     label: 'Video storyboard',desc: 'Frame-by-frame storyboard with captions.',                       icon: 'video-player',     active: false },
];

// Registry-driven doc Types — anything registered at layer=doc shows up
// alongside the built-in DOC_TYPES. User-/Vi-authored doc Types are
// rendered as a separate "From Registry" group on the picker.
function useExtraDocTypes() {
  const [tick, setTick] = React.useState(0);
  React.useEffect(() => window.CV_REGISTRY?.subscribe(() => setTick(t => t + 1)), []);
  return React.useMemo(() => {
    const R = window.CV_REGISTRY;
    if (!R) return [];
    // Only user/vi-authored doc Types — built-ins are already in the top row
    const all = R.query({ layer: 'doc' });
    return all.filter(t => t.provenance === 'user' || t.provenance === 'vi');
  }, [tick]);
}

function Workshop({ docs, saveDoc, removeDoc, saveTemplate, pendingDocId }) {
  // Hoist window-exposed components to local names for cleaner JSX
  const WSCandidateGallery = window.WSCandidateGallery;
  const WSTransformMenu = window.WSTransformMenu;
  const WSFieldToolbar = window.WSFieldToolbar;
  const WSShortcutsOverlay = window.WSShortcutsOverlay;
  const WSOnboarding = window.WSOnboarding;
  const WSErrorBoundary = window.WSErrorBoundary;

  const [view, setView] = useState_w('list');
  const [docId, setDocId] = useState_w(null);
  const [drafting, setDrafting] = useState_w(false);
  const [draftBrief, setDraftBrief] = useState_w('');
  const [draftType, setDraftType] = useState_w(null);
  const [draftKind, setDraftKind] = useState_w(null);     // widget kind / wizard kind, or 'auto'
  const [draftSystem, setDraftSystem] = useState_w(null); // widget system, or 'auto'
  const [selectedIdx, setSelectedIdx] = useState_w(null);
  const [variations, setVariations] = useState_w({});
  const [activeVariations, setActiveVariations] = useState_w({});
  const [refiningIdx, setRefiningIdx] = useState_w(null);
  const [currentPage, setCurrentPage] = useState_w(0);
  const [exportOpen, setExportOpen] = useState_w(false);
  const [showOutline, setShowOutline] = useState_w(true);
  const [showThemeBar, setShowThemeBar] = useState_w(false);
  const [layoutPickerForPage, setLayoutPickerForPage] = useState_w(null);
  const [aiFillingPage, setAiFillingPage] = useState_w(null);
  const [libraryOpen, setLibraryOpen] = useState_w(true);
  const [slideDropActive, setSlideDropActive] = useState_w(false);
  const undoStack = useRef_w([]);
  const redoStack = useRef_w([]);
  const ignoreNextChange = useRef_w(false);

  // Workshop-wide candidate gallery (any caller can open it)
  const [galleryState, setGalleryState] = useState_w(null); // { title, target, candidates, busy, onPick }
  // Whole-doc transform menu visibility
  const [transformMenuOpen, setTransformMenuOpen] = useState_w(false);
  useEffect_w(() => {
    if (!transformMenuOpen) return;
    function onDoc() { setTransformMenuOpen(false); }
    document.addEventListener('click', onDoc);
    return () => document.removeEventListener('click', onDoc);
  }, [transformMenuOpen]);
  // Whether to show the side suggestions panel
  const [showSuggestions, setShowSuggestions] = useState_w(true);

  const doc = docs.find(d => d.id === docId);

  // Sync the AI bridge — chat rail + cross-doc surfaces can act on this doc
  useEffect_w(() => {
    if (doc && view === 'edit') {
      window.WS_AI?.bridge.setActive(doc, saveDoc, { currentPage, selectedIdx });
    }
    return () => {
      // only clear if we're leaving
    };
  }, [doc, view, currentPage, selectedIdx]);
  useEffect_w(() => () => { window.WS_AI?.bridge.clear(); }, []);

  // If parent passed a pendingDocId (e.g. from running a template), open it
  useEffect_w(() => {
    if (pendingDocId && docs.find(d => d.id === pendingDocId)) {
      setDocId(pendingDocId);
      setView('edit');
      setCurrentPage(0);
    }
  }, [pendingDocId]);

  // Workshop-wide save-as-template flow: Vi extracts variables → modal preview
  const [templatePreview, setTemplatePreview] = useState_w(null);
  // null | { extracting: true } | { variables, doc, name }
  async function saveAsTemplate(d) {
    if (!d) return;
    setTemplatePreview({ extracting: true });
    try {
      const extracted = await window.WS_AI.extractTemplate(d);
      setTemplatePreview({
        extracting: false,
        variables: extracted.variables || [],
        doc: extracted.doc,
        name: d.title + ' (template)',
        sourceType: d.type,
      });
    } catch {
      window.dsaToast?.('Vi could not extract variables — saving as plain copy');
      // Fallback: save without variables
      saveTemplate?.({
        id: 'tpl-' + Date.now(),
        name: d.title + ' (template)',
        kind: 'workshop-doc',
        docType: d.type,
        doc: clone(d),
        variables: [],
        savedAt: new Date().toLocaleDateString(),
      });
      setTemplatePreview(null);
    }
  }
  function confirmSaveTemplate() {
    if (!templatePreview || templatePreview.extracting) return;
    saveTemplate?.({
      id: 'tpl-' + Date.now(),
      name: templatePreview.name,
      kind: 'workshop-doc',
      docType: templatePreview.sourceType,
      doc: templatePreview.doc,
      variables: templatePreview.variables,
      savedAt: new Date().toLocaleDateString(),
    });
    setTemplatePreview(null);
    window.dsaToast?.(`Template saved · ${templatePreview.variables.length} variables · find it in Templates`);
  }
  function clone(o) { return JSON.parse(JSON.stringify(o)); }

  // Register the per-field regen handler — opens the candidate gallery with
  // the focused field's value + context and applies the picked value back
  useEffect_w(() => {
    if (!window.WS_FIELD) return;
    // reconnect the Vi per-field regen toolbar onto the engine's editable leaves
    window.__cvFieldFocus = (info) => {
      const el = info.el; if (!el || !window.WS_FIELD) return;
      window.WS_FIELD.activate({
        rect: el.getBoundingClientRect(), value: info.value,
        blockKind: el.closest('[data-block-kind]')?.getAttribute('data-block-kind'),
        sectionId: el.closest('[data-section-id]')?.getAttribute('data-section-id'),
        fieldName: info.path, onApply: info.apply,
      });
    };
    window.WS_FIELD.setRegenHandler((info) => {
      // Build a small context blob (siblings' values inside the same section)
      let blockData = null;
      try {
        if (info.sectionId && doc?.pages) {
          for (const p of doc.pages) {
            const s = (p.sections || []).find(x => x.id === info.sectionId);
            if (s) { blockData = s.data; break; }
          }
        }
      } catch {}
      const context = blockData ? JSON.stringify(blockData).slice(0, 200) : '';
      const target = {
        kind: 'field.alternate',
        current: info.value,
        blockKind: info.blockKind,
        fieldName: info.fieldName,
        angle: info.angle || 'different',
        context,
      };
      const angleTitle = ({
        shorter: 'Shorter versions',
        formal:  'More formal versions',
        specific:'More specific versions',
        different:'Alternative angles',
      })[info.angle || 'different'];
      runGallery({
        target,
        title: `${angleTitle} for "${(info.value || '').toString().slice(0, 40) || info.fieldName || 'this field'}"`,
        onPickOverride: (cand) => { info.onApply?.(cand.value); },
      });
    });
    return () => { window.WS_FIELD.setRegenHandler(null); window.__cvFieldFocus = null; };
  }, [doc]);

  // Open the central candidate gallery + drive Vi generation (streaming)
  async function runGallery({ target, title, brief, onPickOverride }) {
    const stateId = Date.now() + Math.random();
    setGalleryState({ id: stateId, title, target, busy: true, candidates: [], onPickOverride });
    try {
      await window.WS_AI.generateCandidatesStream({
        doc, target, count: 3, brief: brief || '',
        onCandidate: (c) => {
          setGalleryState(s => s && s.id === stateId
            ? { ...s, candidates: [...(s.candidates || []), c] }
            : s);
        },
        onDone: () => {
          setGalleryState(s => s && s.id === stateId ? { ...s, busy: false } : s);
        },
        onError: () => { /* swallow per-candidate errors */ },
      });
    } catch {
      setGalleryState(s => s && s.id === stateId ? { ...s, busy: false } : s);
      window.dsaToast?.('Vi could not generate options — try again');
    }
  }

  function pickCandidate(cand) {
    if (galleryState?.onPickOverride) {
      galleryState.onPickOverride(cand);
    } else if (cand.diff) {
      const inv = window.WS_AI.invertDiff(cand.diff, doc);
      saveDoc(window.WS_AI.applyDiff(doc, cand.diff));
      // Future: push inv to a Vi-undo stack if we wire it
    }
    setGalleryState(null);
    window.dsaToast?.('Applied · ⌘Z to undo');
  }

  async function refineGallery(hint) {
    if (!galleryState) return;
    const stateId = galleryState.id;
    if (hint === 'more options') {
      // Keep existing, add 3 more
      setGalleryState(s => ({ ...s, busy: true }));
      try {
        await window.WS_AI.generateCandidatesStream({
          doc, target: galleryState.target, count: 3, brief: 'distinctly different from the previous options',
          onCandidate: (c) => setGalleryState(s => s && s.id === stateId
            ? { ...s, candidates: [...(s.candidates || []), c] } : s),
          onDone: () => setGalleryState(s => s && s.id === stateId ? { ...s, busy: false } : s),
        });
      } catch { setGalleryState(s => s && s.id === stateId ? { ...s, busy: false } : s); }
      return;
    }
    setGalleryState({ ...galleryState, candidates: [], busy: true });
    try {
      await window.WS_AI.generateCandidatesStream({
        doc, target: galleryState.target, count: 3, brief: hint,
        onCandidate: (c) => setGalleryState(s => s && s.id === stateId
          ? { ...s, candidates: [...(s.candidates || []), c] } : s),
        onDone: () => setGalleryState(s => s && s.id === stateId ? { ...s, busy: false } : s),
      });
    } catch { setGalleryState(s => s && s.id === stateId ? { ...s, busy: false } : s); }
  }

  function openTransform(t) {
    setTransformMenuOpen(false);
    if (t.target) {
      // Theme/layout-style transforms route through a direct engine target
      runGallery({ target: t.target, title: t.label });
    } else {
      runGallery({ target: { kind: 'doc.transform', instruction: t.instruction }, title: `Pick a transform: ${t.label}` });
    }
  }

  // History snapshot on every doc change
  useEffect_w(() => {
    if (!doc) return;
    if (ignoreNextChange.current) { ignoreNextChange.current = false; return; }
    // Capture a snapshot — keep last 30
    const snap = JSON.stringify(doc);
    const prev = undoStack.current[undoStack.current.length - 1];
    if (prev !== snap) {
      undoStack.current = [...undoStack.current.slice(-29), snap];
      redoStack.current = [];
    }
  }, [doc]);

  // Keyboard: arrows for nav, Cmd+Z undo, Cmd+Shift+Z redo, Cmd+D duplicate
  useEffect_w(() => {
    if (view !== 'edit') return;
    function onKey(e) {
      if (document.activeElement && /INPUT|TEXTAREA/.test(document.activeElement.tagName)) return;
      if (document.activeElement?.isContentEditable) return;
      const mod = e.metaKey || e.ctrlKey;
      if (mod && e.key.toLowerCase() === 'z' && !e.shiftKey) { e.preventDefault(); undo(); }
      else if (mod && (e.key.toLowerCase() === 'z' && e.shiftKey || e.key.toLowerCase() === 'y')) { e.preventDefault(); redo(); }
      else if (mod && e.key.toLowerCase() === 'd' && doc?.type === 'deck') { e.preventDefault(); duplicatePage(currentPage); }
      else if (e.key === 'ArrowRight' && doc?.type === 'deck') {
        if (selectedIdx == null) setCurrentPage(p => Math.min(p + 1, doc.pages.length - 1));
      }
      else if (e.key === 'ArrowLeft' && doc?.type === 'deck') {
        if (selectedIdx == null) setCurrentPage(p => Math.max(p - 1, 0));
      }
      else if (e.key === 'Escape') { setSelectedIdx(null); setLayoutPickerForPage(null); }
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [view, doc, currentPage, selectedIdx]);

  function newDoc(type) {
    setDraftType(type); setDraftBrief('');
    if (type === 'widget')      { setDraftKind('auto'); setDraftSystem('auto'); }
    else if (type === 'wizard') { setDraftKind('auto'); setDraftSystem(null); }
    else                        { setDraftKind(null); setDraftSystem(null); }
  }

  async function startDraft(useAI) {
    const id = 'doc-' + Date.now();
    const type = draftType;
    let pages, extras = {};
    if (useAI && draftBrief.trim()) {
      setDrafting(true);
      try {
        if (type === 'widget') {
          extras = await window.viDraftWidget(draftBrief.trim(), draftKind, draftSystem);
          pages = blankPages(type);
        } else if (type === 'wizard') {
          extras = await window.viDraftWizard(draftBrief.trim(), draftKind);
          pages = blankPages(type);
        } else {
          pages = await viDraft(type, draftBrief.trim());
        }
      }
      catch { window.dsaToast?.('Draft failed — starting blank'); pages = blankPages(type); extras = blankExtras(type); }
      finally { setDrafting(false); }
    } else {
      pages = blankPages(type);
      extras = blankExtras(type, draftKind, draftSystem);
    }
    const newDoc = {
      id, type,
      title: titleFromBrief(draftBrief) || titleForType(type),
      pages,
      theme: 'editorial',
      createdAt: Date.now(),
      ...extras,
    };
    saveDoc(newDoc);
    setDocId(id); setView('edit'); setDraftType(null); setDraftBrief('');
    setCurrentPage(0); setSelectedIdx(null); setVariations({}); setActiveVariations({});
    undoStack.current = []; redoStack.current = [];
  }

  function openDoc(id) {
    setDocId(id); setView('edit'); setCurrentPage(0); setSelectedIdx(null);
    setVariations({}); setActiveVariations({});
    undoStack.current = []; redoStack.current = [];
  }

  function closeDoc() { setView('list'); setDocId(null); setSelectedIdx(null); }

  function updateDoc(updater) {
    if (!doc) return;
    saveDoc(typeof updater === 'function' ? updater(doc) : updater);
  }

  function undo() {
    if (undoStack.current.length < 2) { window.dsaToast?.('Nothing to undo'); return; }
    const current = undoStack.current.pop();
    redoStack.current.push(current);
    const prev = undoStack.current[undoStack.current.length - 1];
    if (prev) { ignoreNextChange.current = true; saveDoc(JSON.parse(prev)); window.dsaToast?.('Undone'); }
  }
  function redo() {
    if (!redoStack.current.length) { window.dsaToast?.('Nothing to redo'); return; }
    const next = redoStack.current.pop();
    undoStack.current.push(next);
    ignoreNextChange.current = true; saveDoc(JSON.parse(next));
    window.dsaToast?.('Redone');
  }

  function updateSection(pageIdx, secIdx, newSec) {
    updateDoc(d => ({ ...d, pages: d.pages.map((p, i) => i === pageIdx ? { ...p, sections: p.sections.map((s, j) => j === secIdx ? newSec : s) } : p) }));
  }

  function removeSection(pageIdx, secIdx) {
    updateDoc(d => ({ ...d, pages: d.pages.map((p, i) => i === pageIdx ? { ...p, sections: p.sections.filter((_, j) => j !== secIdx) } : p) }));
    setSelectedIdx(null);
  }

  function addSection(pageIdx, atIdx, kind) {
    updateDoc(d => ({
      ...d, pages: d.pages.map((p, i) => {
        if (i !== pageIdx) return p;
        const def = window.WS_BLOCKS[kind];
        const newSection = { id: 'sec-' + Date.now(), kind, data: { ...def.defaults } };
        const next = [...p.sections]; next.splice(atIdx, 0, newSection);
        return { ...p, sections: next };
      }),
    }));
  }

  function moveSection(pageIdx, fromIdx, toIdx) {
    updateDoc(d => ({
      ...d, pages: d.pages.map((p, i) => {
        if (i !== pageIdx) return p;
        const next = [...p.sections];
        const [moved] = next.splice(fromIdx, 1);
        next.splice(toIdx, 0, moved);
        return { ...p, sections: next };
      }),
    }));
    setSelectedIdx(toIdx);
  }

  function duplicateSection(pageIdx, secIdx) {
    updateDoc(d => ({
      ...d, pages: d.pages.map((p, i) => {
        if (i !== pageIdx) return p;
        const orig = p.sections[secIdx];
        const dup = { ...orig, id: 'sec-' + Date.now(), data: { ...orig.data } };
        const next = [...p.sections]; next.splice(secIdx + 1, 0, dup);
        return { ...p, sections: next };
      }),
    }));
  }

  function toggleLock(pageIdx, secIdx) {
    updateDoc(d => ({ ...d, pages: d.pages.map((p, i) => i === pageIdx ? { ...p, sections: p.sections.map((s, j) => j === secIdx ? { ...s, locked: !s.locked } : s) } : p) }));
  }

  function addPage(layoutId = 'blank', atIdx) {
    let newPage;
    const idx = atIdx ?? (doc?.pages?.length || 0);
    if (layoutId === 'blank' && atIdx == null) {
      newPage = { id: 'p-' + Date.now(), title: `Slide ${(doc?.pages?.length || 0) + 1}`, kind: 'content', sections: [] };
    } else {
      newPage = window.WS_buildPage(layoutId, idx);
    }
    updateDoc(d => {
      const pages = [...d.pages];
      pages.splice(idx, 0, newPage);
      return { ...d, pages };
    });
    setCurrentPage(idx);
    setSelectedIdx(null);
  }

  function duplicatePage(idx) {
    updateDoc(d => {
      const orig = d.pages[idx];
      if (!orig) return d;
      const dup = {
        ...orig, id: 'p-' + Date.now(),
        sections: orig.sections.map((s, j) => ({ ...s, id: 'sec-' + Date.now() + '-' + j, data: { ...s.data } })),
      };
      const pages = [...d.pages]; pages.splice(idx + 1, 0, dup);
      return { ...d, pages };
    });
    setCurrentPage(idx + 1);
    window.dsaToast?.('Slide duplicated');
  }

  function removePage(idx) {
    if (!doc || doc.pages.length === 1) { window.dsaToast?.('Can\'t remove the last slide'); return; }
    if (!confirm('Remove this slide?')) return;
    updateDoc(d => ({ ...d, pages: d.pages.filter((_, i) => i !== idx) }));
    setCurrentPage(p => Math.max(0, Math.min(p, doc.pages.length - 2)));
  }

  function movePage(fromIdx, toIdx) {
    updateDoc(d => {
      const pages = [...d.pages];
      const [moved] = pages.splice(fromIdx, 1);
      pages.splice(toIdx, 0, moved);
      return { ...d, pages };
    });
    setCurrentPage(toIdx);
  }

  function setPageKind(pageIdx, kind) {
    updateDoc(d => ({ ...d, pages: d.pages.map((p, i) => i === pageIdx ? { ...p, kind, motif: null } : p) }));
  }

  function setPageMotif(pageIdx, motif) {
    updateDoc(d => ({ ...d, pages: d.pages.map((p, i) => i === pageIdx ? { ...p, motif } : p) }));
  }

  function setTheme(theme) {
    updateDoc(d => ({ ...d, theme }));
    window.dsaToast?.(`Theme: ${window.WS_THEMES[theme].name}`);
  }

  function insertSectionAt(pageIdx, atIdx, section) {
    updateDoc(d => ({
      ...d, pages: d.pages.map((p, i) => {
        if (i !== pageIdx) return p;
        const def = window.WS_BLOCKS[section.kind];
        if (!def) return p;
        const newSection = { id: 'sec-' + Date.now(), kind: section.kind, data: { ...def.defaults, ...(section.data || {}) } };
        const next = [...p.sections];
        next.splice(atIdx, 0, newSection);
        return { ...p, sections: next };
      }),
    }));
    setSelectedIdx(atIdx);
  }

  function applyLayout(layoutId) {
    if (!doc) return;
    if (layoutId === 'blank') return;
    const built = window.WS_buildPage(layoutId, currentPage);
    updateDoc(d => ({ ...d, pages: d.pages.map((p, i) => i === currentPage ? { ...p, kind: built.kind, sections: built.sections } : p) }));
    window.dsaToast?.(`Applied layout: ${window.WS_LAYOUTS[layoutId]?.name || layoutId}`);
  }

  function handleLibraryInsert(payload) {
    if (!doc) return;
    const resolved = window.WS_resolveLibraryPayload?.(payload);
    if (!resolved) return;
    if (resolved.kind === 'layout') { applyLayout(resolved.layout); return; }
    const at = (doc.pages[currentPage]?.sections?.length) || 0;
    insertSectionAt(currentPage, at, resolved.section);
  }

  function handleSlideDrop(e) {
    const raw = e.dataTransfer?.getData('application/x-cv-library');
    if (!raw) return;
    e.preventDefault();
    try {
      const payload = JSON.parse(raw);
      handleLibraryInsert(payload);
    } catch {}
    setSlideDropActive(false);
  }

  async function refineSection(pageIdx, secIdx, message) {
    const sec = doc.pages[pageIdx].sections[secIdx];
    setRefiningIdx(secIdx);
    try {
      const prompt = `You are revising one block in a ConceptV ${doc.type === 'deck' ? 'slide deck' : 'brochure'}.

Block type: ${sec.kind}
Current data (JSON): ${JSON.stringify(sec.data)}

User wants: "${message}"

Return revised data — same JSON structure, only change values per the user's request. ${window.CV_AI.get('voice.conceptv').text}

Respond as compact JSON only, no prose, no markdown fences.`;
      const reply = await window.CV_AI.complete(prompt);
      const parsed = parseJsonLoose(reply);
      if (parsed && typeof parsed === 'object') {
        updateSection(pageIdx, secIdx, { ...sec, data: { ...sec.data, ...parsed } });
        window.dsaToast?.(`Refined ${window.WS_BLOCKS[sec.kind].label}`);
      } else { window.dsaToast?.('Vi returned no usable change'); }
    } catch { window.dsaToast?.('Refine failed'); }
    finally { setRefiningIdx(null); }
  }

  async function generateVariations(pageIdx, secIdx) {
    const sec = doc.pages[pageIdx].sections[secIdx];
    setRefiningIdx(secIdx);
    try {
      const prompt = `Generate 3 variations of this ConceptV ${doc.type} block. Same structure, different angles. ${window.CV_AI.get('voice.conceptv').text}

Block type: ${sec.kind}
Original (JSON): ${JSON.stringify(sec.data)}

Respond as compact JSON only: {"variations":[ <obj1>, <obj2>, <obj3> ]}`;
      const reply = await window.CV_AI.complete(prompt);
      const parsed = parseJsonLoose(reply);
      if (parsed && Array.isArray(parsed.variations)) {
        setVariations(prev => ({ ...prev, [sec.id]: parsed.variations.slice(0, 5) }));
        window.dsaToast?.(`${parsed.variations.length} variations`);
      } else { window.dsaToast?.('Vi returned no variations'); }
    } catch { window.dsaToast?.('Variations failed'); }
    finally { setRefiningIdx(null); }
  }

  function pickVariation(pageIdx, secIdx, variIdx) {
    const sec = doc.pages[pageIdx].sections[secIdx];
    if (variIdx == null) { setActiveVariations(prev => ({ ...prev, [sec.id]: null })); return; }
    const vari = variations[sec.id]?.[variIdx];
    if (!vari) return;
    updateSection(pageIdx, secIdx, { ...sec, data: { ...sec.data, ...vari } });
    setActiveVariations(prev => ({ ...prev, [sec.id]: variIdx }));
  }

  async function fillSlideWithVi(pageIdx) {
    setAiFillingPage(pageIdx);
    try {
      const page = doc.pages[pageIdx];
      const context = doc.pages.slice(0, pageIdx).map(p => p.sections.map(s => s.kind + ': ' + JSON.stringify(s.data)).join(' / ')).join('\n');
      const prompt = `You are filling a single slide inside a ConceptV ${doc.type === 'deck' ? 'slide deck' : 'brochure'}.

Document title: "${doc.title}"
${context ? 'Previous slides for context:\n' + context : 'This is the first slide.'}

Current slide kind: ${page.kind || 'content'}.

Compose 2-4 blocks for this slide. ${window.CV_AI.get('voice.conceptv').text}

Available block kinds and data shapes:
- hero: {eyebrow, headline, body, cta, imageLabel}
- headline: {eyebrow?, text}
- body: {text}
- quote: {text, who}
- icons: {items:[{icon,label}]} (icons: house, people, network, browser, file, chat, building-tall, vr-headset, dashboard, dollar-circle, calendar, gear, link, share, lightbulb, star, atom)
- stats: {items:[{v,l}]}
- callout: {label, text}
- button: {text}

Respond as compact JSON only:
{"sections":[{"kind":"...","data":{...}}, ...]}`;
      const reply = await window.CV_AI.complete(prompt);
      const parsed = parseJsonLoose(reply);
      if (parsed && Array.isArray(parsed.sections) && parsed.sections.length) {
        const newSections = parsed.sections.filter(s => s.kind && window.WS_BLOCKS[s.kind]).map((s, j) => ({
          id: 'sec-' + Date.now() + '-' + j,
          kind: s.kind,
          data: { ...window.WS_BLOCKS[s.kind].defaults, ...(s.data || {}) },
        }));
        updateDoc(d => ({ ...d, pages: d.pages.map((p, i) => i === pageIdx ? { ...p, sections: newSections } : p) }));
        window.dsaToast?.(`Filled with ${newSections.length} blocks`);
      } else { window.dsaToast?.('Vi returned no usable blocks'); }
    } catch { window.dsaToast?.('Fill failed'); }
    finally { setAiFillingPage(null); }
  }

  // ---------- Render ----------
  if (view === 'list') {
    return (
      <>
        <CanvasHeader
          title="Workshop"
          sub="Compose real deliverables — slides, brochures, and more. Pick a doc type to start, or open one you've already made."
        />
        <div className="dsa-canvas-body">
          {draftType ? (
            <NewDocPanel type={draftType} brief={draftBrief} setBrief={setDraftBrief}
              kind={draftKind} setKind={setDraftKind}
              system={draftSystem} setSystem={setDraftSystem}
              drafting={drafting} onCancel={() => setDraftType(null)}
              onStartBlank={() => startDraft(false)} onStartAI={() => startDraft(true)}/>
          ) : (
            <>
              <DocTypePicker DOC_TYPES={DOC_TYPES} onPick={newDoc}/>

              {docs.length > 0 && (
                <div className="dsa-section" style={{marginTop:28}}>
                  <div className="dsa-section-head">
                    <h3 className="dsa-section-title">Your docs · {docs.length}</h3>
                  </div>
                  <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fill, minmax(220px, 1fr))',gap:10}}>
                    {[...docs].sort((a, b) => b.createdAt - a.createdAt).map(d => (
                      <div key={d.id} className="dsa-card" style={{cursor:'pointer',padding:14}} onClick={() => openDoc(d.id)}>
                        <div style={{font:'700 9px/1 var(--font-body)',color:'var(--accent-bronze)',letterSpacing:'0.08em',textTransform:'uppercase',marginBottom:8}}>
                          {DOC_TYPES.find(t => t.id === d.type)?.label || d.type}
                        </div>
                        <div style={{font:'700 14px/1.2 var(--font-display)',color:'var(--fg-primary)',marginBottom:4,letterSpacing:'-0.01em'}}>{d.title}</div>
                        <div style={{font:'400 11px/1 var(--font-body)',color:'var(--fg-muted)'}}>{d.pages.length} {d.pages.length === 1 ? 'page' : 'pages'} · {new Date(d.createdAt).toLocaleDateString()}</div>
                        <div style={{marginTop:10,display:'flex',gap:6}}>
                          <button className="dsa-btn dsa-btn--outline dsa-btn--sm" onClick={(e) => { e.stopPropagation(); openDoc(d.id); }}>Open</button>
                          <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={(e) => { e.stopPropagation(); if (confirm('Delete this doc?')) removeDoc(d.id); }}>Delete</button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </>
    );
  }

  // Editing view
  if (!doc) return <CanvasHeader title="Workshop" sub="Doc not found"/>;

  // Widget / Wizard docs use their own self-contained editors
  if (doc.type === 'widget') {
    const WB = window.WidgetBuilder;
    return <>
      <WB doc={doc} saveDoc={saveDoc} closeDoc={closeDoc} onSaveTemplate={saveAsTemplate}/>
      <TemplatePreviewModal preview={templatePreview} onClose={() => setTemplatePreview(null)} onConfirm={confirmSaveTemplate} onChangeName={(n) => setTemplatePreview(p => ({ ...p, name: n }))} onChangeVar={(i, patch) => setTemplatePreview(p => ({ ...p, variables: p.variables.map((v, j) => i === j ? { ...v, ...patch } : v) }))}/>
    </>;
  }
  if (doc.type === 'wizard') {
    const WZ = window.WizardBuilder;
    return <>
      <WZ doc={doc} saveDoc={saveDoc} closeDoc={closeDoc} onSaveTemplate={saveAsTemplate}/>
      <TemplatePreviewModal preview={templatePreview} onClose={() => setTemplatePreview(null)} onConfirm={confirmSaveTemplate} onChangeName={(n) => setTemplatePreview(p => ({ ...p, name: n }))} onChangeVar={(i, patch) => setTemplatePreview(p => ({ ...p, variables: p.variables.map((v, j) => i === j ? { ...v, ...patch } : v) }))}/>
    </>;
  }

  const isDeck = doc.type === 'deck';
  const page = doc.pages[currentPage] || doc.pages[0];
  const motif = window.WS_resolveMotif(doc, page);
  const bleed = window.WS_MOTIFS[motif]?.bleed || 'light';
  const isEmptySlide = page.sections.length === 0;

  return (
    <>
      <CanvasHeader
        title={doc.title}
        sub={`${DOC_TYPES.find(t => t.id === doc.type)?.label} · ${doc.pages.length} ${doc.pages.length === 1 ? 'page' : 'pages'} · ⌘Z undo · ⌘D dup · ←→ nav`}
        actions={<>
          <button className="dsa-btn dsa-btn--ghost" onClick={closeDoc}>← All docs</button>
          <button
            className={`dsa-btn dsa-btn--ghost dsa-btn--sm ${showThemeBar ? 'dsa-btn--outline' : ''}`}
            onClick={() => setShowThemeBar(s => !s)}
            title="Theme & background"
          >Theme · {window.WS_THEMES[doc.theme || 'editorial']?.name || 'Editorial'}</button>
          <button
            className={`dsa-btn dsa-btn--ghost dsa-btn--sm ${page.locked ? 'dsa-btn--outline' : ''}`}
            onClick={() => updateDoc(d => ({ ...d, pages: d.pages.map((p, i) => i === currentPage ? { ...p, locked: !p.locked } : p) }))}
            title={page.locked ? 'Slide locked — click to unlock' : 'Lock slide — Vi and edits will be blocked'}
          >{page.locked ? '🔒 Locked' : '🔓 Lock slide'}</button>
          <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={undo} title="Undo (⌘Z)">↶</button>
          <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={redo} title="Redo (⌘⇧Z)">↷</button>
          <button className="dsa-btn dsa-btn--outline dsa-btn--sm" onClick={() => saveAsTemplate(doc)} title="Save this doc as a reusable template with Vi-extracted variables">+ Template</button>
          <span style={{position:'relative'}} onClick={e => e.stopPropagation()}>
            <button className="dsa-btn dsa-btn--ai dsa-btn--sm" onClick={() => setTransformMenuOpen(o => !o)} title="Whole-doc Vi transforms">
              <ViShape size={12}/> Transform
            </button>
            <WSTransformMenu open={transformMenuOpen} onClose={() => setTransformMenuOpen(false)} doc={doc} onPickTransform={openTransform}/>
          </span>
          <span style={{position:'relative'}} onClick={e => e.stopPropagation()}>
            <button className="dsa-btn dsa-btn--primary" onClick={() => setExportOpen(o => !o)}>Export ↗</button>
            {exportOpen && (() => { const M = window.WSExportMenu; return <M doc={doc} onClose={() => setExportOpen(false)}/>; })()}
          </span>
        </>}
      />
      <div className="dsa-canvas-body">
        <div className="ws-doc-head">
          <input className="ws-doc-title" value={doc.title} onChange={e => updateDoc(d => ({ ...d, title: e.target.value }))}/>
          <span className="ws-doc-meta">Auto-saved · {new Date(doc.createdAt).toLocaleDateString()}</span>
        </div>

        {showThemeBar && (
          <ThemeBar
            theme={doc.theme || 'editorial'}
            onTheme={setTheme}
            currentMotif={motif}
            onPageMotif={m => setPageMotif(currentPage, m)}
            pageKind={page.kind || 'content'}
            onPageKind={k => setPageKind(currentPage, k)}
            onClose={() => setShowThemeBar(false)}
          />
        )}

        <div className={`ws-workspace ${!libraryOpen ? 'no-left' : ''} ${(isDeck && !showOutline) ? 'no-right' : ''}`}>
          {/* Left panel: searchable Library — blocks / layouts / icons / components / imagery */}
          {libraryOpen ? (
            <window.Library
              docType={doc.type}
              onInsertBlock={handleLibraryInsert}
              onApplyLayout={applyLayout}
              onClose={() => setLibraryOpen(false)}
            />
          ) : (
            <button
              className="ws-library-reopen"
              onClick={() => setLibraryOpen(true)}
              title="Open library">
              <CvIcon name="files-stack" size={16} tone="bronze"/>
              <span>Library</span>
            </button>
          )}

          {/* Center: preview */}
          <div
            className={`ws-doc ${slideDropActive ? 'slide-drop-active' : ''}`}
            onClick={() => { setSelectedIdx(null); setLayoutPickerForPage(null); }}
            onDragOver={(e) => {
              if (e.dataTransfer.types.includes('application/x-cv-library')) {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'copy';
                setSlideDropActive(true);
              }
            }}
            onDragLeave={(e) => {
              // only clear if leaving the container, not children
              if (e.currentTarget === e.target) setSlideDropActive(false);
            }}
            onDrop={handleSlideDrop}
          >
            {isDeck ? (
              <SlideFrame doc={doc} page={page} motif={motif} bleed={bleed} slideIndex={currentPage} slideCount={doc.pages.length}>
                {isEmptySlide ? (
                  <LayoutPicker
                    docType="deck"
                    onPick={layoutId => {
                      if (layoutId === 'blank') { setLayoutPickerForPage(null); return; }
                      const built = window.WS_buildPage(layoutId, currentPage);
                      updateDoc(d => ({ ...d, pages: d.pages.map((p, i) => i === currentPage ? { ...p, kind: built.kind, sections: built.sections } : p) }));
                      setLayoutPickerForPage(null);
                    }}
                    onAiFill={() => fillSlideWithVi(currentPage)}
                    aiBusy={aiFillingPage === currentPage}
                    onAiPropose={() => runGallery({ target: { kind: 'layout.generate', pageIdx: currentPage }, title: '3 layout proposals for this page' })}
                  />
                ) : (
                  <SectionList
                    page={page} pageIdx={currentPage}
                    selectedIdx={selectedIdx} setSelectedIdx={setSelectedIdx}
                    refiningIdx={refiningIdx}
                    onUpdate={(i, s) => updateSection(currentPage, i, s)}
                    onRemove={i => removeSection(currentPage, i)}
                    onMove={(from, to) => moveSection(currentPage, from, to)}
                    onLock={i => toggleLock(currentPage, i)}
                    onDuplicate={i => duplicateSection(currentPage, i)}
                    onRefine={(i, msg) => refineSection(currentPage, i, msg)}
                    onVary={i => runGallery({ target: { kind: 'alternate.block', pageIdx: currentPage, secIdx: i }, title: '3 alternates for this block' })}
                    variations={variations}
                    activeVariations={activeVariations}
                    onPickVariation={(i, vi) => pickVariation(currentPage, i, vi)}
                    onAddSection={(at, kind) => addSection(currentPage, at, kind)}
                    onInsertSection={(at, sec) => insertSectionAt(currentPage, at, sec)} onInsertVi={(at) => runGallery({ target: { kind: 'insert.block', pageIdx: currentPage, atIdx: at }, title: 'Pick a block to insert here' })}
                  />
                )}
              </SlideFrame>
            ) : (
              <BrochurePreview page={page}>
                {isEmptySlide ? (
                  <LayoutPicker
                    docType="brochure"
                    onPick={layoutId => {
                      if (layoutId === 'blank') { setLayoutPickerForPage(null); return; }
                      const built = window.WS_buildPage(layoutId, currentPage);
                      updateDoc(d => ({ ...d, pages: d.pages.map((p, i) => i === currentPage ? { ...p, kind: built.kind, sections: built.sections } : p) }));
                      setLayoutPickerForPage(null);
                    }}
                    onAiFill={() => fillSlideWithVi(currentPage)}
                    aiBusy={aiFillingPage === currentPage}
                    onAiPropose={() => runGallery({ target: { kind: 'layout.generate', pageIdx: currentPage }, title: '3 layout proposals for this page' })}
                  />
                ) : (
                  <SectionList
                    page={page} pageIdx={currentPage}
                    selectedIdx={selectedIdx} setSelectedIdx={setSelectedIdx}
                    refiningIdx={refiningIdx}
                    onUpdate={(i, s) => updateSection(currentPage, i, s)}
                    onRemove={i => removeSection(currentPage, i)}
                    onMove={(from, to) => moveSection(currentPage, from, to)}
                    onLock={i => toggleLock(currentPage, i)}
                    onDuplicate={i => duplicateSection(currentPage, i)}
                    onRefine={(i, msg) => refineSection(currentPage, i, msg)}
                    onVary={i => runGallery({ target: { kind: 'alternate.block', pageIdx: currentPage, secIdx: i }, title: '3 alternates for this block' })}
                    variations={variations}
                    activeVariations={activeVariations}
                    onPickVariation={(i, vi) => pickVariation(currentPage, i, vi)}
                    onAddSection={(at, kind) => addSection(currentPage, at, kind)}
                    onInsertSection={(at, sec) => insertSectionAt(currentPage, at, sec)} onInsertVi={(at) => runGallery({ target: { kind: 'insert.block', pageIdx: currentPage, atIdx: at }, title: 'Pick a block to insert here' })}
                  />
                )}
              </BrochurePreview>
            )}

            {isDeck && (
              <SlideStrip
                doc={doc} currentPage={currentPage}
                onPick={i => { setCurrentPage(i); setSelectedIdx(null); }}
                onAdd={() => addPage('blank', doc.pages.length)}
                onMove={movePage}
                onDuplicate={duplicatePage}
                onRemove={removePage}
                resolveMotif={p => window.WS_resolveMotif(doc, p)}
              />
            )}
          </div>

          {/* Right rail: slide outline + Vi suggestions */}
          {isDeck && showOutline && (
            <aside className="ws-outline-panel">
              <h5>Outline · {doc.pages.length}</h5>
              <OutlineList
                doc={doc} currentPage={currentPage}
                onPick={i => { setCurrentPage(i); setSelectedIdx(null); }}
                onMove={movePage}
                onAdd={() => addPage('blank', doc.pages.length)}
              />
              <VariablesRail/>
              <ViSuggestionsRail doc={doc} currentPage={currentPage} selectedIdx={selectedIdx} onRun={runGallery}/>
            </aside>
          )}
          {!isDeck && (
            <aside className="ws-outline-panel">
              <VariablesRail/>
              <ViSuggestionsRail doc={doc} currentPage={currentPage} selectedIdx={selectedIdx} onRun={runGallery}/>
            </aside>
          )}
        </div>
      </div>
      {/* Candidate gallery — opened by section/divider/transform/suggestion */}
      <WSCandidateGallery
        open={!!galleryState}
        title={galleryState?.title}
        busy={galleryState?.busy}
        candidates={galleryState?.candidates}
        doc={doc}
        onPick={pickCandidate}
        onClose={() => setGalleryState(null)}
        onRefine={refineGallery}
      />
      {/* Global per-field Vi regen toolbar */}
      <WSFieldToolbar/>
      {/* Save-as-template preview modal */}
      <TemplatePreviewModal
        preview={templatePreview}
        onClose={() => setTemplatePreview(null)}
        onConfirm={confirmSaveTemplate}
        onChangeName={(n) => setTemplatePreview(p => ({ ...p, name: n }))}
        onChangeVar={(i, patch) => setTemplatePreview(p => ({ ...p, variables: p.variables.map((v, j) => i === j ? { ...v, ...patch } : v) }))}
      />
      {WSShortcutsOverlay ? <WSShortcutsOverlay/> : null}
      {WSOnboarding ? <WSOnboarding/> : null}
    </>
  );
}

// ============================================================
// Sub-components
// ============================================================

function DocTypePicker({ DOC_TYPES, onPick }) {
  const extras = useExtraDocTypes();
  const R = window.CV_REGISTRY;
  return (
    <>
      <div className="dsa-section">
        <div className="dsa-section-head">
          <h3 className="dsa-section-title">Start something new</h3>
          <span className="dsa-section-meta">Click a doc type to open a new draft{extras.length ? ` · ${extras.length} custom Types in your Registry` : ''}</span>
        </div>
        <div className="ws-picker">
          {DOC_TYPES.map(t => {
            const regType = t.active ? R?.get('doc.' + t.id) : null;
            return (
              <div key={t.id} className={`ws-type ${t.active ? '' : 'coming-soon'}`}
                onClick={() => t.active && onPick(t.id)}>
                {!t.active && <span className="ws-type-soon">Coming soon</span>}
                {regType && window.TypeThumb ? (
                  <div className="ws-type-thumb">
                    <window.TypeThumb type={regType} width={280} height={160}/>
                  </div>
                ) : (
                  <div className="ws-type-icon"><CvIcon name={t.icon} size={26} tone="bronze"/></div>
                )}
                <h4 className="ws-type-name">{t.label}</h4>
                <p className="ws-type-desc">{t.desc}</p>
              </div>
            );
          })}
        </div>
      </div>
      {extras.length > 0 && (
        <div className="dsa-section" style={{marginTop:18}}>
          <div className="dsa-section-head">
            <h3 className="dsa-section-title">From your Type Registry · {extras.length}</h3>
            <span className="dsa-section-meta">Custom doc Types you (or Vi) have authored</span>
          </div>
          <div className="ws-picker">
            {extras.map(t => {
              const family = (window.CV_REGISTRY?.resolve(t.id)?.family) || 'deck';
              const fallback = ['widget', 'wizard', 'deck', 'brochure'].includes(family) ? family : 'deck';
              return (
                <div key={t.id} className="ws-type" onClick={() => onPick(fallback, t)}>
                  <span className="ws-type-soon" style={{background:'var(--bg-dark)',color:'var(--fg-inverse)'}}>{t.provenance}</span>
                  <div className="ws-type-thumb">
                    {window.TypeThumb && <window.TypeThumb type={t} width={280} height={160}/>}
                  </div>
                  <h4 className="ws-type-name">{t.name}</h4>
                  <p className="ws-type-desc">{t.description}</p>
                  <div>
                    <window.TypeLayerBadge layer={t.layer} size="sm"/>
                    <span style={{font:'500 9px/1 var(--font-mono)',color:'var(--fg-muted)',letterSpacing:'0.04em'}}>{t.family}</span>
                    {t.extends && <span style={{font:'500 9px/1 var(--font-mono)',color:'var(--fg-muted)',marginLeft:'auto'}}>extends {t.extends.split('.').pop()}</span>}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </>
  );
}

function NewDocPanel({ type, brief, setBrief, kind, setKind, system, setSystem, drafting, onCancel, onStartBlank, onStartAI }) {
  const t = DOC_TYPES.find(x => x.id === type);
  const placeholders = {
    deck:     'e.g. "Investor pitch for ConceptV — 6 slides"',
    brochure: 'e.g. "One-page sell sheet for Virtual Hub"',
    widget:   'e.g. "Show occupancy and capture velocity for Tower East" or "Hub gallery widget for a tower\u2019s public page" or "Embeddable pricing widget for partner sites"',
    wizard:   'e.g. "4-step onboarding for new tenants" or "Capture a new property through to hub publish" or "Generic feedback form, 3 steps"',
  };
  const widgetKinds = (typeof window !== 'undefined' && window.WIDGET_KINDS) || [];
  const widgetSystems = (typeof window !== 'undefined' && window.WIDGET_SYSTEMS) || [];
  const wizardKinds = (typeof window !== 'undefined' && window.WIZARD_KINDS) || [];
  return (
    <div className="dsa-card" style={{padding:24}}>
      <div style={{display:'flex',alignItems:'center',gap:12,marginBottom:14}}>
        <div className="ws-type-icon"><CvIcon name={t.icon} size={26} tone="bronze"/></div>
        <div>
          <h3 style={{font:'700 18px/1.1 var(--font-display)',color:'var(--fg-primary)',margin:0,letterSpacing:'-0.01em'}}>New {t.label.toLowerCase()}</h3>
          <p style={{font:'400 12px/1.5 var(--font-body)',color:'var(--fg-secondary)',margin:'4px 0 0'}}>Describe what you want, or start blank and compose it block by block.</p>
        </div>
        <button className="dsa-btn dsa-btn--ghost" style={{marginLeft:'auto'}} onClick={onCancel}>Cancel</button>
      </div>
      <textarea rows="3"
        placeholder={placeholders[type] || ''}
        value={brief} onChange={e => setBrief(e.target.value)}
        style={{
          width:'100%',border:'1.5px solid var(--accent-gold)',borderRadius:'var(--r-md)',
          padding:'12px 14px',background:'var(--bg-canvas)',outline:'none',
          font:'400 14px/1.55 var(--font-body)',color:'var(--fg-primary)',
          resize:'vertical',minHeight:80,fontFamily:'var(--font-body)',boxSizing:'border-box',
        }} disabled={drafting}/>

      {/* Widget kind + system pickers */}
      {type === 'widget' && (
        <div style={{display:'flex',flexWrap:'wrap',gap:18,marginTop:14}}>
          <DraftPicker label="Widget kind" value={kind} onChange={setKind} options={[
            { id: 'auto', label: 'Vi decides', desc: 'Pick based on your brief' },
            ...widgetKinds.map(k => ({ id: k.id, label: k.label, desc: `${k.size.w}×${k.size.h} · ${k.desc.split('.')[0]}` })),
          ]}/>
          <DraftPicker label="System" value={system} onChange={setSystem} options={[
            { id: 'auto', label: 'Vi decides', desc: 'Pick based on your brief' },
            ...widgetSystems.map(s => ({ id: s.id, label: s.label, desc: s.desc })),
          ]}/>
        </div>
      )}

      {/* Wizard kind picker */}
      {type === 'wizard' && (
        <div style={{display:'flex',flexWrap:'wrap',gap:18,marginTop:14}}>
          <DraftPicker label="Wizard kind" value={kind} onChange={setKind} options={[
            { id: 'auto', label: 'Vi decides', desc: 'Pick based on your brief' },
            ...wizardKinds.map(k => ({ id: k.id, label: k.label, desc: k.desc })),
          ]}/>
        </div>
      )}
      <div style={{display:'flex',gap:8,marginTop:12,alignItems:'center'}}>
        <button className="dsa-btn dsa-btn--ai" onClick={onStartAI} disabled={drafting || !brief.trim()}>
          <ViShape size={14} animated={drafting}/> {drafting ? 'Vi is drafting…' : 'Vi, draft this'}
        </button>
        <button className="dsa-btn dsa-btn--outline" onClick={onStartBlank} disabled={drafting}>Start blank</button>
        <span style={{font:'400 11px/1 var(--font-body)',color:'var(--fg-muted)',marginLeft:'auto'}}>
          {drafting ? 'Composing pages…' : 'You can refine every section after drafting.'}
        </span>
      </div>
    </div>
  );
}

function SlideFrame({ doc, page, motif, bleed, children, slideIndex, slideCount }) {
  const M = window.WSMotifLayer;
  const wrapRef = useRef_w(null);
  const innerRef = useRef_w(null);
  const [scale, setScale] = useState_w(1);
  useEffect_w(() => {
    if (!wrapRef.current) return;
    function fit() {
      const w = wrapRef.current?.offsetWidth || 1280;
      setScale(Math.max(0.2, Math.min(1.4, w / 1280)));
    }
    fit();
    const ro = new ResizeObserver(fit);
    ro.observe(wrapRef.current);
    return () => ro.disconnect();
  }, []);
  return (
    <div ref={wrapRef} className="ws-slide-stage">
      <div
        ref={innerRef}
        className="ws-slide-frame"
        data-bleed={bleed}
        data-kind={page?.kind || 'content'}
        style={{ transform: `scale(${scale})` }}
      >
        <M motif={motif}/>
        <div className="ws-slide-inner">{children}</div>
        {/* Slide chrome — page number + brand mark + hatched bottom edge */}
        <div className="ws-slide-edge" aria-hidden="true">
          <svg viewBox="0 0 1280 12" preserveAspectRatio="none" width="100%" height="100%">
            <defs>
              <pattern id="ws-hatch" x="0" y="0" width="14" height="12" patternUnits="userSpaceOnUse" patternTransform="rotate(0)">
                <line x1="0" y1="14" x2="14" y2="0" stroke="currentColor" strokeWidth="1"/>
              </pattern>
            </defs>
            <rect width="1280" height="12" fill="url(#ws-hatch)"/>
          </svg>
        </div>
        {slideIndex != null && slideCount > 1 && (
          <div className="ws-slide-num" aria-hidden="true">
            {String(slideIndex + 1).padStart(2, '0')}
            <span className="of">/{String(slideCount).padStart(2, '0')}</span>
          </div>
        )}
        <div className="ws-slide-mark" aria-hidden="true">
          <svg viewBox="0 0 32 32" width="34" height="34">
            <circle cx="16" cy="16" r="14" fill="none" stroke="currentColor" strokeWidth="1.5"/>
            <path d="M8 11 L16 22 L24 11" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
      </div>
    </div>
  );
}

function BrochurePreview({ page, children }) {
  return <div className="ws-brochure-frame">{children}</div>;
}

function LayoutPicker({ onPick, onAiFill, aiBusy, docType = 'deck', onAiPropose }) {
  const layouts = window.WS_layoutsForType ? window.WS_layoutsForType(docType) : Object.entries(window.WS_LAYOUTS).filter(([k]) => k !== 'blank');
  return (
    <div className="ws-layout-picker" onClick={e => e.stopPropagation()}>
      <h3 className="ws-layout-picker-title">Pick a layout</h3>
      <p className="ws-layout-picker-sub">…or let Vi compose one for you.</p>
      <div className="ws-layout-grid">
        {layouts.map(([key, L]) => (
          <button key={key} className="ws-layout-tile" onClick={() => onPick(key)}>
            <CvIcon name={L.icon} size={20} tone="bronze"/>
            <div className="name">{L.name}</div>
            <div className="desc">{L.desc}</div>
          </button>
        ))}
      </div>
      <div className="ws-empty-actions">
        {onAiPropose && (
          <button className="dsa-btn dsa-btn--outline" onClick={onAiPropose} disabled={aiBusy} title="Vi proposes 3 alternative custom layouts">
            <ViShape size={14}/> 3 layout proposals
          </button>
        )}
        <button className="ws-vi-cta" onClick={onAiFill} disabled={aiBusy}>
          <ViShape size={14} animated={aiBusy}/> {aiBusy ? 'Vi is composing…' : 'Vi, draft this for me'}
        </button>
        <button className="dsa-btn dsa-btn--ghost" onClick={() => onPick('blank')}>Start blank</button>
      </div>
    </div>
  );
}

function SectionList({ page, pageIdx, selectedIdx, setSelectedIdx, refiningIdx, onUpdate, onRemove, onMove, onLock, onDuplicate, onRefine, onVary, variations, activeVariations, onPickVariation, onAddSection, onInsertSection, onInsertVi }) {
  const dragRef = useRef_w({ from: null });
  return (
    <>
      {page.sections.map((sec, idx) => (
        <React.Fragment key={sec.id}>
          {idx === 0 && <window.WSAddDivider onAdd={kind => onAddSection(0, kind)} onInsertSection={s => onInsertSection?.(0, s)} onInsertVi={onInsertVi ? () => onInsertVi(0) : null} atIdx={0}/>}
          <SectionDraggable
            sec={sec} idx={idx} total={page.sections.length}
            isSelected={selectedIdx === idx} refining={refiningIdx === idx}
            onSelect={(e) => { e?.stopPropagation?.(); setSelectedIdx(idx); }}
            onChange={s => onUpdate(idx, s)}
            onRemove={() => onRemove(idx)}
            onMove={(from, to) => onMove(from, to)}
            onMoveUp={() => idx > 0 && onMove(idx, idx - 1)}
            onMoveDown={() => idx < page.sections.length - 1 && onMove(idx, idx + 1)}
            onLock={() => onLock(idx)}
            onDuplicate={() => onDuplicate(idx)}
            onRefine={msg => onRefine(idx, msg)}
            onVary={() => onVary(idx)}
            variations={variations[sec.id]}
            activeVariation={activeVariations[sec.id]}
            onPickVariation={vi => onPickVariation(idx, vi)}
            dragRef={dragRef}
          />
          <window.WSAddDivider onAdd={kind => onAddSection(idx + 1, kind)} onInsertSection={s => onInsertSection?.(idx + 1, s)} onInsertVi={onInsertVi ? () => onInsertVi(idx + 1) : null} atIdx={idx + 1}/>
        </React.Fragment>
      ))}
    </>
  );
}

// dotted-path immutable setter for engine onEdit → section data writeback (W6)
function wsSetPath(obj, path, val) {
  const ks = String(path).split('.');
  const root = Array.isArray(obj) ? obj.slice() : { ...obj };
  let cur = root;
  for (let i = 0; i < ks.length - 1; i++) {
    const k = ks[i]; const nx = cur[k];
    cur[k] = Array.isArray(nx) ? nx.slice() : { ...(nx || {}) };
    cur = cur[k];
  }
  cur[ks[ks.length - 1]] = val;
  return root;
}
// cross-doc embeds (widget engine) keep their own renderer; EVERYTHING else —
// including diagrams (graph solver, now with editable node labels) — renders +
// edits through the one engine.
const WS_ENGINE_EDIT_SKIP = new Set(['embedWidget', 'embedWizard']);

function SectionDraggable(props) {
  const { sec, idx, total, isSelected, refining, onSelect, onChange, onRemove, onMove, onMoveUp, onMoveDown, onLock, onDuplicate, onRefine, onVary, variations, activeVariation, onPickVariation, dragRef } = props;
  const [dragOver, setDragOver] = useState_w(null); // 'top' | 'bot' | null
  const [isDragging, setIsDragging] = useState_w(false);
  const def = window.WS_BLOCKS[sec.kind];
  if (!def) return null;
  return (
    <div
      className={`ws-section ${isSelected ? 'selected' : ''} ${sec.locked ? 'locked' : ''} ${isDragging ? 'dragging' : ''} ${dragOver === 'top' ? 'drag-over-top' : ''} ${dragOver === 'bot' ? 'drag-over-bot' : ''}`}
      data-section-id={sec.id}
      data-block-kind={sec.kind}
      style={{padding: sec.kind === 'divider' ? '4px 0' : '18px 22px'}}
      onDragStart={(e) => {
        if (!e.target.closest?.('.ws-drag-handle')) { e.preventDefault(); return; }
        dragRef.current.from = idx; setIsDragging(true); e.dataTransfer.effectAllowed = 'move';
      }}
      onDragEnd={() => { dragRef.current.from = null; setIsDragging(false); setDragOver(null); }}
      onDragOver={(e) => {
        // Library drops are handled by AddDivider — ignore them here
        if (e.dataTransfer.types.includes('application/x-cv-library')) return;
        e.preventDefault();
        const rect = e.currentTarget.getBoundingClientRect();
        const mid = rect.top + rect.height / 2;
        setDragOver(e.clientY < mid ? 'top' : 'bot');
      }}
      onDragLeave={() => setDragOver(null)}
      onDrop={(e) => {
        if (e.dataTransfer.types.includes('application/x-cv-library')) return;
        e.preventDefault();
        const from = dragRef.current.from;
        setDragOver(null);
        if (from == null || from === idx) return;
        const insertAt = dragOver === 'top' ? idx : idx + 1;
        const to = insertAt > from ? insertAt - 1 : insertAt;
        onMove(from, to);
      }}
      onClick={onSelect}
    >
      <div className="ws-section-toolbar">
        <span
          className="ws-drag-handle"
          draggable
          title="Drag to reorder"
          aria-label="Drag to reorder"
        >⋮⋮</span>
        <span className="badge">{def.label}</span>
        <span className="div"/>
        <div className="move-group" role="group" aria-label="Move">
          <button onClick={(e) => { e.stopPropagation(); onMoveUp?.(); }} disabled={idx === 0} title="Move up">↑</button>
          <button onClick={(e) => { e.stopPropagation(); onMoveDown?.(); }} disabled={idx === total - 1} title="Move down">↓</button>
        </div>
        <span className="div"/>
        <window.RefinePop mode="chip" disabled={refining} onRefine={onRefine} placeholder={`Refine this ${def.label.toLowerCase()}…`}/>
        <button onClick={(e) => { e.stopPropagation(); onVary(); }} disabled={refining} title="3 variations">⤧ Variations</button>
        <span className="div"/>
        <div className="secondary-group">
          <button onClick={(e) => { e.stopPropagation(); onDuplicate(); }} title="Duplicate">⎘</button>
          <button onClick={(e) => { e.stopPropagation(); onLock(); }} title={sec.locked ? 'Unlock' : 'Lock'}>{sec.locked ? '🔒' : '🔓'}</button>
          <button onClick={(e) => { e.stopPropagation(); if (confirm(`Remove ${def.label}?`)) onRemove(); }} title="Remove">×</button>
        </div>
      </div>
      {WS_ENGINE_EDIT_SKIP.has(sec.kind)
        ? def.render(sec.data, onChange)
        : React.createElement(window.__cvRenderType, {
            type: { layer: 'block', family: 'block', runtime: { kind: 'ws-block', key: sec.kind } },
            data: sec.data, lod: 'full', surface: 'web', density: 'comfortable',
            onEdit: (p, v) => onChange(wsSetPath(sec.data, p, v)),
          })}
      {isSelected && variations && variations.length > 0 && (
        <div className="ws-variations" onClick={e => e.stopPropagation()}>
          <span className="label">Variations</span>
          <div className="chips">
            <button className={`chip ${activeVariation == null ? 'active' : ''}`} onClick={() => onPickVariation(null)}>Original</button>
            {variations.map((v, i) => (
              <button key={i} className={`chip ${activeVariation === i ? 'active' : ''}`} onClick={() => onPickVariation(i)}>v{i + 1}</button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function SlideStrip({ doc, currentPage, onPick, onAdd, onMove, onDuplicate, onRemove, resolveMotif }) {
  const dragRef = useRef_w({ from: null });
  return (
    <div className="ws-slide-strip" onClick={e => e.stopPropagation()}>
      {doc.pages.map((p, i) => {
        const motif = resolveMotif(p);
        const bleed = window.WS_MOTIFS[motif]?.bleed || 'light';
        return (
          <div key={p.id}
            className={`ws-thumb ${i === currentPage ? 'active' : ''}`}
            draggable
            onDragStart={() => { dragRef.current.from = i; }}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => { e.preventDefault(); const from = dragRef.current.from; if (from != null && from !== i) onMove(from, i); }}
            onClick={() => onPick(i)}>
            <span className="ws-thumb-num">{String(i + 1).padStart(2, '0')}</span>
            <div className={`ws-thumb-frame ws-motif ws-motif--${motif}`} data-bleed={bleed}>
              <window.WSMotifLayer motif={motif}/>
              <div className="ws-thumb-body">
                <div className="ws-slide-inner" style={{padding:'40px 48px',width:1280,height:720,boxSizing:'border-box'}}>
                  {p.sections.slice(0, 4).map((sec, j) => {
                    const def = window.WS_BLOCKS[sec.kind]; if (!def) return null;
                    const body = WS_ENGINE_EDIT_SKIP.has(sec.kind)
                      ? def.render(sec.data, () => {})
                      : React.createElement(window.__cvRenderType, { type: { layer: 'block', family: 'block', runtime: { kind: 'ws-block', key: sec.kind } }, data: sec.data, lod: 'full', surface: 'web', density: 'comfortable' });
                    return <React.Fragment key={sec.id || j}>{body}</React.Fragment>;
                  })}
                </div>
              </div>
            </div>
            <div className="ws-thumb-actions">
              <button className="ws-thumb-action" title="Duplicate" onClick={(e) => { e.stopPropagation(); onDuplicate(i); }}>⎘</button>
              <button className="ws-thumb-action danger" title="Remove" onClick={(e) => { e.stopPropagation(); onRemove(i); }}>×</button>
            </div>
          </div>
        );
      })}
      <div className="ws-slide-strip-add" onClick={onAdd}>+</div>
    </div>
  );
}

function OutlineList({ doc, currentPage, onPick, onMove, onAdd }) {
  const dragRef = useRef_w({ from: null });
  return (
    <div style={{display:'flex',flexDirection:'column',gap:2}}>
      {doc.pages.map((p, i) => (
        <div key={p.id}
          className={`ws-outline-row ${i === currentPage ? 'active' : ''}`}
          draggable
          onDragStart={() => { dragRef.current.from = i; }}
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => { e.preventDefault(); const from = dragRef.current.from; if (from != null && from !== i) onMove(from, i); }}
          onClick={() => onPick(i)}>
          <span className="n">{String(i + 1).padStart(2, '0')}</span>
          <div>
            <div style={{font:'500 12px/1.3 var(--font-body)',color:'inherit',whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'}}>
              {p.sections[0]?.data?.text || p.sections[0]?.data?.headline || p.title || `Slide ${i + 1}`}
            </div>
            <div className="kind">{p.kind || 'content'}</div>
          </div>
        </div>
      ))}
      <button className="ws-outline-row" style={{color:'var(--accent-gold)',cursor:'pointer'}} onClick={onAdd}>
        <span className="n">+</span>
        <span>Add slide</span>
      </button>
    </div>
  );
}

function VariablesRail() {
  const vars = (typeof window !== 'undefined' && window.useWSVars) ? window.useWSVars() : [];
  const [adding, setAdding] = useState_w(false);
  const [newKey, setNewKey] = useState_w('');
  const [newValue, setNewValue] = useState_w('');
  const [auditing, setAuditing] = useState_w(false);
  const [auditResult, setAuditResult] = useState_w(null);

  // Reference counts live-recompute when docs or vars change
  const [refs, setRefs] = useState_w({ counts: {}, docCounts: {} });
  useEffect_w(() => {
    const recount = () => setRefs(window.WS_VARS?.countReferences?.() || { counts: {}, docCounts: {} });
    recount();
    const u1 = window.WS_DOCS?.subscribe?.(recount);
    const u2 = window.WS_VARS?.subscribe?.(recount);
    return () => { u1?.(); u2?.(); };
  }, []);

  function addVar() {
    const k = newKey.toLowerCase().replace(/[^a-z0-9_]+/g, '_').replace(/^_|_$/g, '');
    if (!k) return;
    window.WS_VARS?.setOne(k, {
      key: k,
      label: k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      value: newValue,
      kind: 'text',
    });
    setNewKey(''); setNewValue(''); setAdding(false);
  }

  async function audit() {
    setAuditing(true);
    setAuditResult(null);
    try {
      const result = await window.WS_VARS?.audit?.();
      setAuditResult(result);
    } catch { window.dsaToast?.('Vi audit failed — try again'); }
    finally { setAuditing(false); }
  }

  function acceptAudit(v) {
    const k = (v.key || '').toLowerCase().replace(/[^a-z0-9_]+/g, '_').replace(/^_|_$/g, '');
    if (!k) return;
    window.WS_VARS?.setOne(k, {
      key: k,
      label: v.label || k,
      value: v.value || '',
      kind: ['text','number','url','color'].includes(v.kind) ? v.kind : 'text',
    });
    setAuditResult(r => r ? { ...r, variables: r.variables.filter(x => x.key !== v.key) } : r);
    window.dsaToast?.(`Added {{${k}}}`);
  }
  function acceptAll() {
    (auditResult?.variables || []).forEach(acceptAudit);
    setAuditResult(null);
  }

  return (
    <div style={{marginTop:14, paddingTop:12, borderTop:'1px dashed var(--accent-gold-soft)'}}>
      <h5 style={{display:'flex',alignItems:'center',gap:6}}>
        <span style={{color:'var(--accent-gold)'}}>◆</span> Workspace vars
        <span style={{marginLeft:'auto',display:'inline-flex',gap:4}}>
          <button
            onClick={audit}
            disabled={auditing}
            title="Vi scans every doc and proposes variables to extract"
            style={{background:'var(--bg-dark)',color:'var(--fg-inverse)',border:'none',borderRadius:999,cursor:'pointer',font:'600 9px/1 var(--font-body)',padding:'3px 8px',letterSpacing:'0.04em',display:'inline-flex',alignItems:'center',gap:3}}>
            {auditing ? <><ViShape size={10} animated/> scanning</> : <><ViShape size={10}/> find</>}
          </button>
          <button
            onClick={() => setAdding(a => !a)}
            title={adding ? 'Cancel' : 'Add a variable'}
            style={{background:'transparent',border:'1px dashed var(--accent-gold-dashed)',borderRadius:999,cursor:'pointer',color:'var(--accent-bronze)',font:'600 9px/1 var(--font-body)',padding:'3px 8px',letterSpacing:'0.04em'}}>
            {adding ? 'cancel' : '+ add'}
          </button>
        </span>
      </h5>
      <p style={{font:'400 10px/1.4 var(--font-body)',color:'var(--fg-muted)',margin:'4px 0 8px'}}>
        Define once, use as <code style={{font:'500 10px/1 var(--font-mono)',color:'var(--accent-gold)'}}>{'{{key}}'}</code> anywhere — updates everywhere.
      </p>

      {/* Audit results */}
      {auditResult && auditResult.variables?.length > 0 && (
        <div style={{display:'flex',flexDirection:'column',gap:4,padding:'8px',background:'var(--accent-gold-50)',borderRadius:'var(--r-sm)',border:'1px dashed var(--accent-gold)',marginBottom:8}}>
          <div style={{display:'flex',alignItems:'center',gap:6}}>
            <span style={{font:'700 italic 11px/1 var(--font-display)',color:'var(--accent-bronze)'}}>
              Vi found {auditResult.variables.length} candidate{auditResult.variables.length === 1 ? '' : 's'}
            </span>
            <button onClick={acceptAll} className="dsa-btn dsa-btn--primary dsa-btn--sm" style={{marginLeft:'auto'}}>Accept all</button>
            <button onClick={() => setAuditResult(null)} className="dsa-btn dsa-btn--ghost dsa-btn--sm">Dismiss</button>
          </div>
          {auditResult.variables.map((v, i) => (
            <div key={i} style={{display:'flex',alignItems:'center',gap:6,padding:'5px 7px',background:'var(--bg-surface)',borderRadius:'var(--r-sm)',border:'1px solid var(--border-faint)'}}>
              <div style={{flex:1,minWidth:0}}>
                <code style={{font:'600 10px/1 var(--font-mono)',color:'var(--accent-gold)'}}>{`{{${v.key}}}`}</code>
                <div style={{font:'500 11px/1.3 var(--font-body)',color:'var(--fg-primary)',marginTop:2,whiteSpace:'nowrap',overflow:'hidden',textOverflow:'ellipsis'}}>{v.value}</div>
                {v.rationale && <div style={{font:'400 9px/1.3 var(--font-body)',color:'var(--fg-muted)',marginTop:1}}>{v.rationale}</div>}
              </div>
              <button onClick={() => acceptAudit(v)} className="dsa-btn dsa-btn--outline dsa-btn--sm" title="Add this variable">+</button>
            </div>
          ))}
        </div>
      )}
      {auditResult && (!auditResult.variables || auditResult.variables.length === 0) && (
        <div style={{font:'400 11px/1.4 var(--font-body)',color:'var(--fg-muted)',padding:'8px',background:'var(--bg-canvas)',borderRadius:'var(--r-sm)',border:'1px dashed var(--border-faint)',marginBottom:8,display:'flex',gap:8,alignItems:'center'}}>
          Vi didn't find new variables.
          <button onClick={() => setAuditResult(null)} className="dsa-btn dsa-btn--ghost dsa-btn--sm" style={{marginLeft:'auto'}}>OK</button>
        </div>
      )}

      {adding && (
        <div style={{display:'flex',flexDirection:'column',gap:4,padding:'8px',background:'var(--bg-canvas)',borderRadius:'var(--r-sm)',border:'1px dashed var(--accent-gold-soft)',marginBottom:8}}>
          <input
            placeholder="key (e.g. property_name)"
            value={newKey}
            onChange={e => setNewKey(e.target.value)}
            style={{padding:'5px 7px',border:'1px solid var(--border-faint)',borderRadius:'var(--r-sm)',font:'500 11px/1 var(--font-mono)',background:'var(--bg-surface)',outline:'none'}}/>
          <input
            placeholder="value"
            value={newValue}
            onChange={e => setNewValue(e.target.value)}
            onKeyDown={e => { if (e.key === 'Enter') addVar(); }}
            style={{padding:'5px 7px',border:'1px solid var(--border-faint)',borderRadius:'var(--r-sm)',font:'400 11px/1.3 var(--font-body)',background:'var(--bg-surface)',outline:'none'}}/>
          <button className="dsa-btn dsa-btn--primary dsa-btn--sm" onClick={addVar} disabled={!newKey}>Add</button>
        </div>
      )}
      <div style={{display:'flex',flexDirection:'column',gap:4}}>
        {vars.length === 0 && !adding && !auditResult && (
          <div style={{font:'400 11px/1.4 var(--font-body)',color:'var(--fg-muted)',padding:'8px',background:'var(--bg-canvas)',borderRadius:'var(--r-sm)',border:'1px dashed var(--border-faint)'}}>
            None yet — focus any text, click <b>→ var</b> in the Vi toolbar, or hit <b>find</b> to let Vi scan your workspace.
          </div>
        )}
        {vars.map(v => {
          const refCount = refs.counts[v.key] || 0;
          const docCount = refs.docCounts[v.key] || 0;
          const isColor = v.kind === 'color' || (typeof v.value === 'string' && /^#[0-9A-F]{3,8}$/i.test(v.value));
          return (
            <div key={v.key} style={{
              display:'grid', gridTemplateColumns:'1fr 18px', gap:4, alignItems:'center',
              padding:'6px 8px', background:'var(--bg-canvas)',
              border:'1px solid var(--border-faint)', borderRadius:'var(--r-sm)',
            }}>
              <div style={{minWidth:0,display:'flex',flexDirection:'column',gap:3}}>
                <div style={{display:'flex',alignItems:'center',gap:6}}>
                  <code style={{font:'600 10px/1 var(--font-mono)',color:'var(--accent-gold)'}}>{`{{${v.key}}}`}</code>
                  {refCount > 0 ? (
                    <span title={`Referenced ${refCount} time${refCount === 1 ? '' : 's'} across ${docCount} doc${docCount === 1 ? '' : 's'}`}
                      style={{marginLeft:'auto',font:'500 9px/1 var(--font-mono)',color:'var(--status-success)',background:'var(--status-success-bg)',padding:'2px 5px',borderRadius:999}}>
                      live · {docCount}d / {refCount}×
                    </span>
                  ) : (
                    <span title="Not yet referenced — type {{var}} anywhere"
                      style={{marginLeft:'auto',font:'500 9px/1 var(--font-mono)',color:'var(--fg-muted)'}}>
                      unused
                    </span>
                  )}
                </div>
                <div style={{display:'flex',alignItems:'center',gap:4}}>
                  {isColor && (
                    <input
                      type="color"
                      value={v.value || '#888888'}
                      onChange={e => window.WS_VARS?.setOne(v.key, { value: e.target.value, kind: 'color' })}
                      style={{width:24,height:24,border:'1px solid var(--border-faint)',borderRadius:'var(--r-sm)',padding:0,cursor:'pointer',background:v.value || '#888888',flex:'none'}}
                    />
                  )}
                  <input
                    value={v.value || ''}
                    onChange={e => window.WS_VARS?.setOne(v.key, { value: e.target.value })}
                    style={{flex:1,padding:'3px 6px',border:'1px solid var(--border-faint)',borderRadius:'var(--r-sm)',font:'500 11px/1.3 var(--font-body)',background:'var(--bg-surface)',outline:'none',color:'var(--fg-primary)'}}/>
                </div>
              </div>
              <button
                onClick={() => { if (confirm(`Remove variable {{${v.key}}}? References will stay as literal text.`)) window.WS_VARS?.remove(v.key); }}
                title="Remove variable"
                style={{background:'transparent',border:'none',cursor:'pointer',color:'var(--fg-muted)',padding:0,fontSize:11}}>
                ✕
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ViSuggestionsRail({ doc, currentPage, selectedIdx, onRun }) {
  const [sugg, setSugg] = useState_w([]);
  const [busy, setBusy] = useState_w(false);
  const [refreshKey, setRefreshKey] = useState_w(0);

  // Compute heuristic suggestions instantly, then enrich with Vi async
  useEffect_w(() => {
    const heur = window.WS_AI.computeSuggestions(doc, { currentPage, selectedIdx });
    const dismissed = window.WS_AI.getDismissed?.() || new Set();
    setSugg(heur.filter(s => !dismissed.has(s.id)));
    setBusy(true);
    let cancelled = false;
    window.WS_AI.viSuggest({ doc, ctx: { currentPage, selectedIdx }, count: 4 })
      .then(list => { if (!cancelled) setSugg(list); })
      .catch(() => {})
      .finally(() => { if (!cancelled) setBusy(false); });
    return () => { cancelled = true; };
  }, [doc?.id, currentPage, selectedIdx, refreshKey]);

  function dismissSugg(id) {
    window.WS_AI.dismissSuggestion?.(id);
    setSugg(s => s.filter(x => x.id !== id));
  }

  if (!sugg.length && !busy) return null;
  return (
    <div style={{marginTop:14, paddingTop:12, borderTop:'1px dashed var(--accent-gold-soft)'}}>
      <h5 style={{display:'flex',alignItems:'center',gap:6}}>
        <ViShape size={12} animated={busy}/> Vi suggestions
        <button
          onClick={() => setRefreshKey(k => k + 1)}
          title="Regenerate suggestions"
          style={{marginLeft:'auto',background:'transparent',border:'none',cursor:'pointer',color:'var(--fg-muted)',font:'500 11px/1 var(--font-mono)',padding:'2px 4px'}}>
          ↻
        </button>
      </h5>
      <div className="ws-sugg-list">
        {sugg.map(s => (
          <div key={s.id} className="ws-sugg-item-wrap">
            <button className="ws-sugg-item" onClick={() => onRun({ target: s.target, title: s.label })}>
              {s.source === 'vi' && <span className="ws-sugg-vi" title="Vi suggestion">✦</span>}
              <span>{s.label}</span>
            </button>
            <button
              className="ws-sugg-dismiss"
              onClick={(e) => { e.stopPropagation(); dismissSugg(s.id); }}
              title="Dismiss">
              ✕
            </button>
          </div>
        ))}
        {busy && sugg.length < 2 && (
          <div className="ws-sugg-skeleton">
            <div/><div/>
          </div>
        )}
      </div>
    </div>
  );
}

function TemplatePreviewModal({ preview, onClose, onConfirm, onChangeName, onChangeVar }) {
  if (!preview) return null;
  return (
    <div className="ws-cand-overlay" onClick={onClose}>
      <div className="ws-cand-panel" onClick={e => e.stopPropagation()} style={{maxWidth: 640}}>
        <div className="ws-cand-head">
          <ViShape size={18}/>
          <span className="title">Save as template</span>
          <button className="ws-cand-close" onClick={onClose}>✕</button>
        </div>
        {preview.extracting ? (
          <div className="ws-cand-busy">
            <ViShape size={14} animated/>
            <span>Vi is finding variables in your doc…</span>
          </div>
        ) : (
          <div style={{padding:'18px 22px',display:'flex',flexDirection:'column',gap:16}}>
            <label style={{display:'flex',flexDirection:'column',gap:5}}>
              <span style={{font:'600 10px/1 var(--font-body)',color:'var(--accent-bronze)',letterSpacing:'0.1em',textTransform:'uppercase'}}>Template name</span>
              <input
                value={preview.name || ''}
                onChange={e => onChangeName(e.target.value)}
                style={{
                  padding:'9px 12px',border:'1.5px solid var(--accent-gold)',
                  borderRadius:'var(--r-md)',background:'var(--bg-canvas)',outline:'none',
                  font:'500 14px/1 var(--font-body)',color:'var(--fg-primary)',
                }}/>
            </label>
            <div style={{display:'flex',flexDirection:'column',gap:8}}>
              <div style={{font:'600 10px/1 var(--font-body)',color:'var(--accent-bronze)',letterSpacing:'0.1em',textTransform:'uppercase'}}>
                Vi found {preview.variables?.length || 0} variable{preview.variables?.length === 1 ? '' : 's'}
              </div>
              {(preview.variables || []).map((v, i) => (
                <div key={i} style={{
                  display:'grid', gridTemplateColumns:'160px 1fr 90px 28px',
                  gap:8, alignItems:'center',
                  padding:'8px 10px',background:'var(--bg-surface)',
                  border:'1px solid var(--border-faint)',borderRadius:'var(--r-md)',
                }}>
                  <input
                    placeholder="variable key"
                    value={v.label || ''}
                    onChange={e => onChangeVar(i, { label: e.target.value })}
                    style={{padding:'6px 8px',border:'1px solid var(--border-faint)',borderRadius:'var(--r-sm)',font:'500 12px/1 var(--font-body)',background:'var(--bg-canvas)',outline:'none'}}
                  />
                  <input
                    placeholder="default value"
                    value={v.default || ''}
                    onChange={e => onChangeVar(i, { default: e.target.value })}
                    style={{padding:'6px 8px',border:'1px solid var(--border-faint)',borderRadius:'var(--r-sm)',font:'400 12px/1.3 var(--font-body)',background:'var(--bg-canvas)',outline:'none'}}
                  />
                  <select
                    value={v.kind || 'text'}
                    onChange={e => onChangeVar(i, { kind: e.target.value })}
                    style={{padding:'6px 8px',border:'1px solid var(--border-faint)',borderRadius:'var(--r-sm)',font:'500 11px/1 var(--font-body)',background:'var(--bg-canvas)',outline:'none'}}>
                    <option value="text">text</option>
                    <option value="number">number</option>
                    <option value="url">url</option>
                    <option value="audience">audience</option>
                  </select>
                  <div style={{font:'400 10px/1 var(--font-mono)',color:'var(--fg-muted)',textAlign:'right'}}>{`{{${v.key}}}`}</div>
                </div>
              ))}
              {(!preview.variables || !preview.variables.length) && (
                <div style={{font:'400 12px/1.5 var(--font-body)',color:'var(--fg-muted)',padding:'14px',background:'var(--bg-muted)',borderRadius:'var(--r-md)'}}>
                  Vi didn't find any variables — that's OK. You can still save this doc as a static template.
                </div>
              )}
            </div>
            {/* Live preview of the materialized doc with current defaults */}
            {preview.doc && (
              <div style={{display:'flex',flexDirection:'column',gap:8}}>
                <div style={{font:'600 10px/1 var(--font-body)',color:'var(--accent-bronze)',letterSpacing:'0.1em',textTransform:'uppercase'}}>
                  Preview with defaults
                </div>
                <div style={{maxHeight:200,overflow:'auto',background:'var(--bg-canvas)',borderRadius:'var(--r-md)',border:'1px solid var(--border-faint)',padding:12}}>
                  <TemplatePreviewRender preview={preview}/>
                </div>
              </div>
            )}
          </div>
        )}
        <div style={{display:'flex',gap:8,padding:'14px 22px',borderTop:'1px dashed var(--accent-gold-soft)',background:'var(--bg-surface)',justifyContent:'flex-end'}}>
          <button className="dsa-btn dsa-btn--ghost" onClick={onClose}>Cancel</button>
          <button className="dsa-btn dsa-btn--primary" onClick={onConfirm} disabled={preview.extracting}>
            Save template
          </button>
        </div>
      </div>
    </div>
  );
}

function TemplatePreviewRender({ preview }) {
  if (!preview?.doc) return null;
  // Materialize with current values (variable.default since modal doesn't track edits to default beyond the field input)
  const values = {};
  (preview.variables || []).forEach(v => { values[v.key] = v.default || ''; });
  let mat = null;
  try {
    mat = window.WS_AI?.materializeTemplate({ doc: preview.doc, variables: preview.variables || [] }, values);
  } catch {}
  if (!mat) return <div style={{font:'400 11px/1.4 var(--font-mono)',color:'var(--fg-muted)'}}>Could not materialize preview.</div>;
  // Decks/brochures: render pages preview
  if (mat.pages?.length && window.WSRenderedPagePreview) {
    return (
      <div style={{display:'flex',flexDirection:'column',gap:14}}>
        {mat.pages.slice(0, 2).map((p, i) => (
          <div key={i}>
            <div style={{font:'700 italic 11px/1 var(--font-display)',color:'var(--accent-bronze)',marginBottom:6}}>Page {i + 1}</div>
            <window.WSRenderedPagePreview page={p} scale={0.32}/>
          </div>
        ))}
        {mat.pages.length > 2 && (
          <div style={{font:'400 11px/1 var(--font-body)',color:'var(--fg-muted)',textAlign:'center'}}>+ {mat.pages.length - 2} more pages</div>
        )}
      </div>
    );
  }
  // Widget: render via WidgetRender
  if (mat.widgetKind && window.WidgetRender) {
    return <window.WidgetRender doc={mat} hovered={false}/>;
  }
  // Wizard: render step list
  if (mat.steps?.length) {
    return (
      <ol style={{listStyle:'none',padding:0,margin:0,display:'flex',flexDirection:'column',gap:6}}>
        {mat.steps.slice(0, 6).map((s, i) => (
          <li key={i} style={{display:'flex',alignItems:'center',gap:8,font:'500 11px/1.2 var(--font-body)',color:'var(--fg-primary)'}}>
            <span style={{width:18,height:18,borderRadius:'50%',background:'var(--accent-gold)',display:'flex',alignItems:'center',justifyContent:'center',font:'700 9px/1 var(--font-mono)'}}>{i + 1}</span>
            <span style={{flex:1}}>{s.title}</span>
            <span style={{font:'500 9px/1 var(--font-mono)',color:'var(--fg-muted)',letterSpacing:'0.06em',textTransform:'uppercase'}}>{s.kind}</span>
          </li>
        ))}
      </ol>
    );
  }
  return <div style={{font:'400 11px/1.4 var(--font-mono)',color:'var(--fg-muted)'}}>No preview available for this template kind.</div>;
}

function DraftPicker({ label, value, onChange, options }) {
  return (
    <div style={{display:'flex',flexDirection:'column',gap:6,flex:'1 1 240px',minWidth:0}}>
      <div style={{font:'600 9px/1 var(--font-body)',color:'var(--accent-bronze)',letterSpacing:'0.1em',textTransform:'uppercase'}}>{label}</div>
      <div style={{display:'flex',flexWrap:'wrap',gap:6}}>
        {options.map(o => {
          const active = value === o.id || (value == null && o.id === 'auto');
          return (
            <button key={o.id}
              onClick={() => onChange(o.id)}
              title={o.desc}
              style={{
                display:'inline-flex',flexDirection:'column',gap:2,
                padding:'7px 11px', textAlign:'left',
                background: active ? 'var(--accent-gold-soft)' : 'var(--bg-canvas)',
                border: '1.5px solid ' + (active ? 'var(--accent-gold)' : 'var(--border-faint)'),
                borderRadius:'var(--r-md)', cursor:'pointer',
                font:'600 11px/1 var(--font-body)', color:'var(--fg-primary)',
                transition:'all 140ms var(--ease-out)',
              }}>
              {o.label}
              {o.desc && <span style={{font:'400 9px/1.2 var(--font-body)',color:'var(--fg-muted)',textTransform:'none',letterSpacing:0,maxWidth:200}}>{o.desc}</span>}
            </button>
          );
        })}
      </div>
    </div>
  );
}

function ThemeBar({ theme, onTheme, currentMotif, onPageMotif, pageKind, onPageKind, onClose }) {
  return (
    <div className="ws-theme-bar">
      <span className="label">Theme</span>
      {Object.entries(window.WS_THEMES).map(([k, t]) => {
        const sample = Object.values(t.map).slice(0, 3).map(m => window.WS_MOTIFS[m]?.bleed === 'dark' ? '#1F1A12' : window.WS_MOTIFS[m]?.bleed === 'gold' ? '#E0C010' : '#FBF7EC');
        return (
          <button key={k} className={`ws-theme-chip ${theme === k ? 'active' : ''}`} onClick={() => onTheme(k)} title={t.desc}>
            <span className="swatch">{sample.map((c, i) => <span key={i} style={{background:c}}/>)}</span>
            {t.name}
          </button>
        );
      })}
      <span style={{width:1,height:18,background:'var(--border-faint)',margin:'0 6px'}}/>
      <span className="label">This slide</span>
      <select value={pageKind} onChange={e => onPageKind(e.target.value)}
        style={{font:'500 11px/1 var(--font-body)',padding:'5px 8px',borderRadius:'var(--r-sm)',border:'1px solid var(--border-default)',background:'var(--bg-canvas)',color:'var(--fg-primary)'}}>
        {window.WS_KINDS.map(k => <option key={k} value={k}>{k}</option>)}
      </select>
      <select value={currentMotif} onChange={e => onPageMotif(e.target.value)}
        style={{font:'500 11px/1 var(--font-body)',padding:'5px 8px',borderRadius:'var(--r-sm)',border:'1px solid var(--border-default)',background:'var(--bg-canvas)',color:'var(--fg-primary)'}}>
        {Object.entries(window.WS_MOTIFS).map(([k, m]) => <option key={k} value={k}>{m.name}</option>)}
      </select>
      <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" style={{marginLeft:'auto'}} onClick={onClose}>Close</button>
    </div>
  );
}

function BlockMenuButton({ onAdd }) {
  const [open, setOpen] = useState_w(false);
  return (
    <span style={{position:'relative'}}>
      <button className="ws-rail-btn" onClick={() => setOpen(o => !o)} title="Add block">
        <CvIcon name="files-stack" size={18} tone="bronze"/>
        <span className="label">Add block</span>
      </button>
      {open && (
        <div style={{
          position:'absolute', left:'calc(100% + 8px)', top:0, zIndex:60,
          background:'var(--bg-surface)', border:'1.5px solid var(--accent-gold)',
          borderRadius:'var(--r-md)', padding:8, boxShadow:'var(--shadow-pop)',
          display:'grid', gridTemplateColumns:'repeat(2, 1fr)', gap:4, width: 240,
        }} onClick={e => e.stopPropagation()}>
          {Object.entries(window.WS_BLOCKS).map(([key, def]) => (
            <button key={key} className="ws-block-btn"
              onClick={() => { onAdd(key); setOpen(false); }}>
              <CvIcon name={def.icon} size={16} tone="bronze"/>
              {def.label}
            </button>
          ))}
        </div>
      )}
    </span>
  );
}

// ============================================================
// Vi drafting
// ============================================================
async function viDraft(type, brief) {
  const blockKinds = Object.keys(window.WS_BLOCKS).filter(k => k !== 'divider');
  const prompt = `You are Vi, drafting a ConceptV ${type === 'deck' ? 'slide deck' : 'one-page brochure'} from a brief.

Brief: "${brief}"

${window.CV_AI.get('voice.conceptv').text} Concrete and on-brand.

Available block kinds: ${blockKinds.join(', ')}
Block data shapes:
- hero: {eyebrow, headline, body, cta, imageLabel}
- headline: {eyebrow?, text}
- body: {text}
- quote: {text, who}
- icons: {items:[{icon:<name>,label}]} (icon: house, people, network, browser, file, chat, building-tall, vr-headset, dashboard, dollar-circle, calendar, gear, link, share, lightbulb, star, atom)
- stats: {items:[{v,l}]}
- palette: {colors:[{n,h:<hex>}]}
- button: {text}
- callout: {label, text}
- image: {label}

Each slide gets a "kind" — one of: title, section, content, image, quote, stats, closing. Use these to mark slide rhythm.

Compose ${type === 'deck' ? '4-6 slides' : 'one page with 4-6 sections'}.

Respond as compact JSON only:
{"pages":[{"title":"...","kind":"title|section|content|image|quote|stats|closing","sections":[{"kind":"...","data":{...}}, ...]}, ...]}`;
  const reply = await window.CV_AI.execute('deck.generate', { params: { prompt }, surface: doc?.type || 'deck' });
  const parsed = parseJsonLoose(reply);
  if (!parsed || !Array.isArray(parsed.pages) || !parsed.pages.length) throw new Error('Vi returned no usable pages');
  return parsed.pages.map((p, i) => ({
    id: 'p-' + Date.now() + '-' + i,
    title: p.title || `Slide ${i + 1}`,
    kind: window.WS_KINDS.includes(p.kind) ? p.kind : (i === 0 ? 'title' : i === parsed.pages.length - 1 ? 'closing' : 'content'),
    sections: (p.sections || []).filter(s => s && s.kind && window.WS_BLOCKS[s.kind]).map((s, j) => ({
      id: 'sec-' + Date.now() + '-' + i + '-' + j,
      kind: s.kind,
      data: { ...window.WS_BLOCKS[s.kind].defaults, ...(s.data || {}) },
    })),
  }));
}

function blankPages(type) {
  if (type === 'widget' || type === 'wizard') {
    return [{ id: 'p-' + Date.now(), title: type, kind: type, sections: [] }];
  }
  if (type === 'deck') {
    return [{ id: 'p-' + Date.now(), title: 'Slide 1', kind: 'title', sections: [] }];
  }
  return [{ id: 'p-' + Date.now(), title: 'Page 1', kind: 'content', sections: [
    { id: 'sec-' + Date.now() + '-a', kind: 'hero', data: { ...window.WS_BLOCKS.hero.defaults } },
  ]}];
}

function blankExtras(type, kind, system) {
  if (type === 'widget') return window.blankWidget(
    kind && kind !== 'auto' ? kind : 'dashboard',
    system && system !== 'auto' ? system : 'hybrid',
  );
  if (type === 'wizard') return window.blankWizard(
    kind && kind !== 'auto' ? kind : 'property',
  );
  return {};
}

function titleForType(type) {
  if (type === 'widget') return 'Untitled widget';
  if (type === 'wizard') return 'Untitled wizard';
  if (type === 'deck')   return 'Untitled deck';
  return 'Untitled brochure';
}

function titleFromBrief(brief) {
  if (!brief) return null;
  const words = brief.split(/\s+/).slice(0, 6).join(' ');
  return words.length < brief.length ? words + '…' : words;
}

function parseJsonLoose(reply) {
  try { return JSON.parse(reply); } catch {}
  const m = String(reply || '').match(/\{[\s\S]*\}/);
  if (m) { try { return JSON.parse(m[0]); } catch {} }
  return null;
}

window.Workshop = Workshop;
window.WS_viDraft = (typeof viDraft !== 'undefined') ? viDraft : null;
