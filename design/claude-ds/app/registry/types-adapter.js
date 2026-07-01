// app/registry/types-adapter.js
// Bridge between the legacy global constants (WIDGET_KINDS, WIDGET_SYSTEMS,
// WIZARD_KINDS, STEP_KINDS, WS_BLOCKS) and the new universal Type Registry.
//
// Goal: any USER/VI-authored Type at the corresponding layer/family appears
// in the legacy picker automatically. Existing code keeps working unchanged.
//
// Direction: registry → legacy (the registry is the source of truth; legacy
// arrays are mirrors maintained by this adapter).

(function () {
  const R = window.CV_REGISTRY;
  if (!R) { console.warn('[adapter] CV_REGISTRY missing'); return; }

  // -------------------------------------------------------------------------
  // Helpers — convert a registry Type into the shape each legacy consumer
  // expects.
  // -------------------------------------------------------------------------
  function toWidgetKind(t) {
    const d = t.defaults || {};
    return {
      id: t.runtime?.key || idTail(t.id),
      typeId: t.id,
      label: t.name,
      desc: t.description || '',
      size: { w: d.width || 320, h: d.height || 220 },
      provenance: t.provenance,
      icon: t.icon,
    };
  }
  function toWidgetSystem(t) {
    return {
      id: t.runtime?.key || idTail(t.id),
      typeId: t.id,
      label: t.name,
      desc: t.description || '',
      provenance: t.provenance,
      icon: t.icon,
      slots: t.slots,
    };
  }
  function toWizardKind(t) {
    const d = t.defaults || {};
    // Walk to parent for shape/steps defaults if not set
    return {
      id: d.wizardKind || idTail(t.id),
      typeId: t.id,
      label: t.name,
      desc: t.description || '',
      shape: t.tags?.includes('hexagon') ? 'hexagon'
           : t.tags?.includes('circle')   ? 'circle'
           : t.tags?.includes('octagon')  ? 'octagon'
           : 'diamond',
      provenance: t.provenance,
      steps: d.steps || null,
    };
  }
  function toStepKind(t) {
    return {
      id: t.defaults?.kind || idTail(t.id),
      typeId: t.id,
      label: t.name,
      desc: t.description || '',
      provenance: t.provenance,
    };
  }

  function idTail(id) { return id.split('.').pop(); }

  // -------------------------------------------------------------------------
  // Rebuild legacy arrays from registry — preserves any extra entries that
  // already lived there (like sample step defaults stored as steps:[...])
  // -------------------------------------------------------------------------
  function rebuild() {
    // ===== Widget kinds (surface.widget) =====
    const builtInKinds = (window.__LEGACY_WIDGET_KINDS || window.WIDGET_KINDS || []);
    if (!window.__LEGACY_WIDGET_KINDS) window.__LEGACY_WIDGET_KINDS = [...builtInKinds];

    const regKinds = R.query({ layer: 'surface', family: 'widget' });
    // Merge: legacy entries kept by id; registry entries override metadata,
    // and any user/vi-only registry types append.
    const seen = new Set();
    const merged = [];
    for (const t of regKinds) {
      const wk = toWidgetKind(t);
      merged.push(wk);
      seen.add(wk.id);
    }
    for (const lk of window.__LEGACY_WIDGET_KINDS) {
      if (!seen.has(lk.id)) merged.push({ ...lk, provenance: 'built-in' });
    }
    window.WIDGET_KINDS = merged;

    // ===== Widget systems (system.widget) =====
    if (!window.__LEGACY_WIDGET_SYSTEMS) window.__LEGACY_WIDGET_SYSTEMS = [...(window.WIDGET_SYSTEMS || [])];
    const regSystems = R.query({ layer: 'system', family: 'widget' });
    const seenS = new Set();
    const mergedS = [];
    for (const t of regSystems) {
      const ws = toWidgetSystem(t);
      mergedS.push(ws);
      seenS.add(ws.id);
    }
    for (const ls of window.__LEGACY_WIDGET_SYSTEMS) {
      if (!seenS.has(ls.id)) mergedS.push({ ...ls, provenance: 'built-in' });
    }
    window.WIDGET_SYSTEMS = mergedS;

    // ===== Wizard kinds (doc.wizard children) =====
    if (!window.__LEGACY_WIZARD_KINDS) window.__LEGACY_WIZARD_KINDS = [...(window.WIZARD_KINDS || [])];
    const regWizKinds = R.query({ layer: 'doc', family: 'wizard' }).filter(t => t.id !== 'doc.wizard');
    const seenW = new Set();
    const mergedW = [];
    for (const t of regWizKinds) {
      const wk = toWizardKind(t);
      // Hydrate steps from legacy if registry doesn't carry them
      if (!wk.steps) {
        const legacy = window.__LEGACY_WIZARD_KINDS.find(x => x.id === wk.id);
        if (legacy) { wk.steps = legacy.steps; wk.shape = wk.shape || legacy.shape; }
      }
      mergedW.push(wk);
      seenW.add(wk.id);
    }
    for (const lw of window.__LEGACY_WIZARD_KINDS) {
      if (!seenW.has(lw.id)) mergedW.push({ ...lw, provenance: 'built-in' });
    }
    window.WIZARD_KINDS = mergedW;

    // ===== Wizard step kinds (surface.wizard-step) =====
    if (!window.__LEGACY_STEP_KINDS) window.__LEGACY_STEP_KINDS = [...(window.STEP_KINDS || [])];
    const regSteps = R.query({ layer: 'surface', family: 'wizard-step' });
    const seenSt = new Set();
    const mergedSt = [];
    for (const t of regSteps) {
      const sk = toStepKind(t);
      mergedSt.push(sk);
      seenSt.add(sk.id);
    }
    for (const ls of window.__LEGACY_STEP_KINDS) {
      if (!seenSt.has(ls.id)) mergedSt.push({ ...ls, provenance: 'built-in' });
    }
    window.STEP_KINDS = mergedSt;

    // ===== Blocks — same idea =====
    // We don't replace WS_BLOCKS (renderers live there) but we MARK each block
    // with its registered Type id so consumers can show the link.
    if (window.WS_BLOCKS) {
      for (const [k, def] of Object.entries(window.WS_BLOCKS)) {
        def._typeId = 'block.' + k;
      }
    }

    // Notify any UI that watches the legacy arrays
    window.dispatchEvent(new CustomEvent('cv-registry-rebuild'));
  }

  // Run once now, then on every registry change.
  // Also defer one tick so other scripts that populate the legacy arrays
  // (WidgetBuilder.jsx, WizardBuilder.jsx) have time to run.
  let scheduled = false;
  function schedule() {
    if (scheduled) return;
    scheduled = true;
    requestAnimationFrame(() => { scheduled = false; rebuild(); });
  }
  // Try a few times during boot — Babel-loaded files trickle in
  let attempts = 0;
  const boot = setInterval(() => {
    attempts++;
    if (window.WIDGET_KINDS || window.WIZARD_KINDS || attempts > 20) {
      rebuild();
      if (attempts > 20) clearInterval(boot);
    }
    if (window.WIDGET_KINDS && window.WIZARD_KINDS) clearInterval(boot);
  }, 120);

  R.subscribe(schedule);

  // -------------------------------------------------------------------------
  // Save-as-Type helpers — called from inside builders.
  // -------------------------------------------------------------------------
  window.CV_TYPES_SAVE = {
    /** Promote a widget INSTANCE into a Surface/System pair or a Doc Type. */
    async fromWidget(doc, intoLayer = 'doc') {
      return await window.CV_TYPES_VI.promoteInstance({
        instance: doc, intoLayer, intoFamily: 'widget',
      });
    },
    /** Promote a wizard INSTANCE into a Doc Type (wizard kind). */
    async fromWizard(doc) {
      return await window.CV_TYPES_VI.promoteInstance({
        instance: doc, intoLayer: 'doc', intoFamily: 'wizard',
      });
    },
    /** Promote a wizard STEP into a Surface Type (step kind). */
    async fromWizardStep(step) {
      return await window.CV_TYPES_VI.promoteInstance({
        instance: { type: 'wizard-step', ...step },
        intoLayer: 'surface', intoFamily: 'wizard-step',
      });
    },
    /** Promote a block INSTANCE into a Block Type. */
    async fromBlock(section) {
      return await window.CV_TYPES_VI.promoteInstance({
        instance: { type: 'block', ...section },
        intoLayer: 'block', intoFamily: 'block',
      });
    },
  };

  // -------------------------------------------------------------------------
  // Used by App.jsx to show a small global "Save as Type" modal.
  // -------------------------------------------------------------------------
  const saveListeners = new Set();
  window.CV_TYPES_PROMPT = {
    /** Open the Save-as-Type modal with a pre-filled draft (Type object). */
    open(draft) {
      for (const fn of saveListeners) try { fn(draft); } catch {}
    },
    subscribe(fn) { saveListeners.add(fn); return () => saveListeners.delete(fn); },
  };
})();
