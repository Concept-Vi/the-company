/* @ds-bundle: {"format":3,"namespace":"ConceptVDesignSystem_c8f43c","components":[{"name":"Avatar","sourcePath":"components/Avatar.jsx"},{"name":"Badge","sourcePath":"components/Badge.jsx"},{"name":"Button","sourcePath":"components/Button.jsx"},{"name":"Card","sourcePath":"components/Card.jsx"},{"name":"Glyphic","sourcePath":"components/Glyphic.jsx"},{"name":"Input","sourcePath":"components/Input.jsx"},{"name":"Modal","sourcePath":"components/Modal.jsx"},{"name":"Segmented","sourcePath":"components/Segmented.jsx"},{"name":"Stepper","sourcePath":"components/Stepper.jsx"},{"name":"Switch","sourcePath":"components/Switch.jsx"},{"name":"Tabs","sourcePath":"components/Tabs.jsx"},{"name":"ContainmentTree","sourcePath":"core/ContainmentTree.jsx"},{"name":"DiagramSolver","sourcePath":"core/DiagramSolver.jsx"},{"name":"RenderType","sourcePath":"core/RenderType.jsx"},{"name":"CoreTypes","sourcePath":"core/RenderType.jsx"},{"name":"Slide","sourcePath":"core/Slide.jsx"},{"name":"Archetypes","sourcePath":"core/Slide.jsx"}],"sourceHashes":{"app/App.jsx":"7d4f61231dd6","app/ai/ai-capabilities-canvas.js":"eab19f2efbe2","app/ai/ai-glyphic.js":"454f502955de","app/ai/ai-registry.js":"fab976c3c4e9","app/ai/ai-seed.js":"0d52900d9c74","app/ai/host-runtime.js":"2ea1f22789c2","app/ai/host-serializer.js":"3624b7c2d896","app/canvases/AIStudio.jsx":"59e91e06ede6","app/canvases/Architecture.jsx":"476715ae9f15","app/canvases/Bridge.jsx":"ad27b5e2e51b","app/canvases/Build.jsx":"4ed9e6999cd7","app/canvases/Colors.jsx":"2223049f7a4e","app/canvases/Components.jsx":"5ec59a18e929","app/canvases/Icons.jsx":"9d708456807a","app/canvases/Imagery.jsx":"9252f47f8c91","app/canvases/Inbox.jsx":"2bde75c16d43","app/canvases/Overview.jsx":"a166faab8ea0","app/canvases/Patterns.jsx":"77b6d1c11342","app/canvases/Registry.jsx":"05fa2d45cf64","app/canvases/RegistryInspector.jsx":"98729a371542","app/canvases/Settings.jsx":"989a4bfe4ba2","app/canvases/StubCanvases.jsx":"493682597dae","app/canvases/Templates.jsx":"fc5124dc5e0d","app/canvases/TypeBuilder.jsx":"e9eba42aa601","app/canvases/TypeBuilder2.jsx":"57e78baecb14","app/canvases/Voice.jsx":"653e780a8833","app/canvases/Workshop.jsx":"c1eb9822f2a5","app/canvases/workshop/AIEngine.jsx":"b1f87554ee02","app/canvases/workshop/Blocks.jsx":"7c6327a87584","app/canvases/workshop/Export.jsx":"a862dacdfd69","app/canvases/workshop/Layouts.jsx":"0035eae201b2","app/canvases/workshop/Library.jsx":"12fea63360ad","app/canvases/workshop/Polish.jsx":"8f3ec8036eda","app/canvases/workshop/Section.jsx":"3fc095530924","app/canvases/workshop/WidgetBuilder.jsx":"eafc3a532724","app/canvases/workshop/WizardBuilder.jsx":"105d38657fd8","app/components/CanvasHeader.jsx":"43a6ffe145f8","app/components/ChatRail.jsx":"4acf69cb0ce2","app/components/CommandPalette.jsx":"04cd8707dff8","app/components/ExportPatch.jsx":"2568c63a1dcb","app/components/ImageEditor.jsx":"8dfce267fb77","app/components/KitPreviews.jsx":"0614572698f7","app/components/MaskEditor.jsx":"0cc0ade4f8c6","app/components/Pano360.jsx":"326bd1b39aff","app/components/RefinePop.jsx":"86c1a60173aa","app/components/Resizable.jsx":"1af1e686479e","app/components/Sidebar.jsx":"2b991a403a21","app/components/Toast.jsx":"8fa5f4debec9","app/components/ViShape.jsx":"7ce5d121927a","app/components/usePersisted.js":"c00d18f30e24","app/registry/SaveAsTypeModal.jsx":"a1dc8a171c27","app/registry/components-type.js":"00f717b1a520","app/registry/conditions.js":"cfffbebdf522","app/registry/glyphic-type.js":"eceb6b5e2164","app/registry/kinds-type.js":"6b5f01aeefc3","app/registry/types-adapter.js":"684b87f40cca","app/registry/types-core.js":"8a9024a8ceee","app/registry/types-hooks.js":"5b1fa00eaaba","app/registry/types-seed.js":"84c6eb79f7e1","app/registry/types-thumb.jsx":"e4a74607f7d1","app/registry/types-ui.jsx":"6ea8c2338c43","app/registry/types-vi.js":"04769b31ac0b","app/services/ai-presets.js":"42386f3d1aef","app/services/image-store.js":"bc148d43658e","app/services/openai.js":"d6de45be91cb","assets/icons/ConceptVIcon.jsx":"19aaeda0518c","assets/icons/CvIcon.jsx":"5eac79214445","assets/icons/cv-glyphics.js":"dde9c97221b7","assets/icons/cv-icons.js":"c86a1f3406ef","assets/icons/cv-meaning.js":"bdec1f28cbf3","assets/icons/cv-shapes.js":"1c6ee162a213","assets/icons/cv-vi-glyph.js":"82b41fccbe8f","assets/icons/icon-paths.js":"0f981b21a534","atomicity/Atlas.jsx":"0c35a71042cf","atomicity/AtomiCity.jsx":"4f68c3dee6f8","atomicity/Explore.jsx":"1c4e4a7ae23d","atomicity/Foundations.jsx":"5ee0f5b47f41","atomicity/Home.jsx":"4b1c8e9e2745","atomicity/Ingest.jsx":"a70d8280c96b","atomicity/ViConsole.jsx":"5d049d056052","atomicity/VoiceSurface.jsx":"ccdfff7899f0","atomicity/atlas-model.js":"0a98094b032e","atomicity/explore-engine.js":"8c3e036134f0","atomicity/ingest.js":"6b3e2c5b7a17","atomicity/kit.jsx":"a4718a540cbe","atomicity/mode-engine.js":"e076ac2a3bbf","atomicity/override.js":"2d2ab208a7ef","atomicity/picker.js":"88e2102d340c","atomicity/scan-engine.js":"0336d04027e5","atomicity/shot.js":"9619510f8bd5","atomicity/vi-brain.js":"af8bed5d049e","axes/axis-core.js":"0ecd5d39793b","axes/color/color-axis.js":"3abccaa1b9fd","axes/depth/depth-axis.js":"f34d104b3c8b","axes/fill/fill-axis.js":"cb1a2f7e8911","axes/form/form-axis.js":"049eaa0adb26","axes/motion/motion-axis.js":"5e9657a74643","axes/size/size-axis.js":"87b6e7c0abe6","axes/space/space-axis.js":"d3bc2c781bdc","axes/symbol/symbol-axis.js":"d06b5807c203","axes/texture/texture-axis.js":"083a45234160","components/Avatar.jsx":"a38b44cde8e5","components/Badge.jsx":"3cdd070ca5ff","components/Button.jsx":"d7a24dd3c9ba","components/Card.jsx":"3296390edbe5","components/Glyphic.jsx":"87c6c5cbf2e3","components/Input.jsx":"ad7903b8a238","components/Modal.jsx":"b72ec6c457cb","components/Segmented.jsx":"622f617e8abd","components/Stepper.jsx":"a4fbfd19513c","components/Switch.jsx":"b1e1f0d6eb6e","components/Tabs.jsx":"86845adedf04","core/ContainmentTree.jsx":"eebd11e916d1","core/DiagramSolver.jsx":"50bf342f3a26","core/RenderType.jsx":"a1e421c665bc","core/Slide.jsx":"6357ab078294","core/archetype-catalog.js":"11c8d6e1e752","core/slide-fit.js":"ac7974a00f9b","preview/image-slot.js":"9309434cb09c","system/build-system-map.js":"e36fb4b39f0c","tweaks-panel.jsx":"6591467622ed","ui_kits/platform/ActionToolbar.jsx":"631fbddb47bc","ui_kits/platform/Chats.jsx":"5e17e4777f6d","ui_kits/platform/PlatformApp.jsx":"27838168f0c5","ui_kits/platform/PlatformSidebar.jsx":"e005aeec0535","ui_kits/platform/TopBar.jsx":"e0fcf91e7496","ui_kits/platform/screens/BrandKit.jsx":"c2c42d40ad59","ui_kits/platform/screens/Calendar.jsx":"f5ec612b1250","ui_kits/platform/screens/Gallery.jsx":"e44df1327bc8","ui_kits/platform/screens/HubSettings.jsx":"0bff95d1aa3f","ui_kits/platform/screens/Stub.jsx":"c759c2c94cee","ui_kits/vi/ChatPanel.jsx":"abf8ceb04fcc","ui_kits/vi/OutputPreview.jsx":"e29b7550e83a","ui_kits/vi/TaskTree.jsx":"f8a4f3c48b5c","ui_kits/vi/ViKitApp.jsx":"96c12112e88d","ui_kits/vi/ViMark.jsx":"674be272106e","ui_kits/vi/ViStatusPill.jsx":"7163964718c6","ui_kits/virtual-hub/CaptureComment.jsx":"191e64d165b7","ui_kits/virtual-hub/FloorplanOverlay.jsx":"3a97552eb6dc","ui_kits/virtual-hub/HubApp.jsx":"1a612d556d39","ui_kits/virtual-hub/HubBug.jsx":"d0ebbb7f6f80","ui_kits/virtual-hub/InfoPanel.jsx":"bc98573b1e03","ui_kits/virtual-hub/MenuButton.jsx":"fb80f4cec705","ui_kits/virtual-hub/QuickMenu.jsx":"2bd0aee86d80","ui_kits/virtual-hub/SharePanel.jsx":"560df1a59586"},"inlinedExternals":[],"unexposedExports":[{"name":"typeToNode","sourcePath":"core/RenderType.jsx"}]} */

(() => {

const __ds_ns = (window.ConceptVDesignSystem_c8f43c = window.ConceptVDesignSystem_c8f43c || {});

const __ds_scope = {};

(__ds_ns.__errors = __ds_ns.__errors || []);

// app/App.jsx
try { (() => {
// App.jsx — ConceptV Studio root
const {
  useState: useState_app,
  useEffect: useEffect_app
} = React;
function App() {
  const [active, setActive] = useState_app('overview');
  const [inboxItems, setInboxItems] = window.usePersisted('inbox', []);
  const [generatedIcons, setGeneratedIcons] = window.usePersisted('genIcons', []);
  const [extraColors, setExtraColors] = window.usePersisted('extraColors', []);
  const [colorEdits, setColorEdits] = window.usePersisted('colorEdits', {});
  const [patternEdits, setPatternEdits] = window.usePersisted('patternEdits', {});
  const [patternSnapshot, setPatternSnapshot] = window.usePersisted('patternSnapshot', null);
  const [lockedPatterns, setLockedPatterns] = window.usePersisted('lockedPatterns', []);
  const [savedTemplates, setSavedTemplates] = window.usePersisted('templates', []);
  const [generatedComponents, setGeneratedComponents] = window.usePersisted('genComponents', []);
  const [paletteSnapshot, setPaletteSnapshot] = window.usePersisted('paletteSnapshot', null);
  const [exportOpen, setExportOpen] = useState_app(false);
  const [paletteOpen, setPaletteOpen] = useState_app(false);
  const [lockedTokens, setLockedTokens] = window.usePersisted('lockedTokens', []);
  const [savedRewrites, setSavedRewrites] = window.usePersisted('savedRewrites', []);
  const [workshopDocs, setWorkshopDocs] = window.usePersisted('workshopDocs', []);
  const [workspaceVars, setWorkspaceVars] = window.usePersisted('workspaceVars', []);
  const [sidebarCollapsed, setSidebarCollapsed] = useState_app(false);
  const [pendingBrief, setPendingBrief] = useState_app(null);
  const [pendingWorkshopDoc, setPendingWorkshopDoc] = useState_app(null);
  const [tbTypeId, setTbTypeId] = useState_app(null); // when set, render TypeBuilder canvas

  // Listen for tb-open events from anywhere in the app
  useEffect_app(() => {
    function onOpen(e) {
      setTbTypeId(e.detail?.id ?? null);
      setActive('type-builder');
    }
    window.addEventListener('tb-open', onOpen);
    return () => window.removeEventListener('tb-open', onOpen);
  }, []);

  // Subscribe to registry for sidebar counts
  const [registryTick, setRegistryTick] = useState_app(0);
  useEffect_app(() => window.CV_REGISTRY?.subscribe(() => setRegistryTick(t => t + 1)), []);

  // Re-render when imagery store or OpenAI config changes (sidebar counts, pills).
  useEffect_app(() => window.cvImageStore?.subscribe(() => setRegistryTick(t => t + 1)), []);
  useEffect_app(() => window.cvOpenAI?.subscribe(() => setRegistryTick(t => t + 1)), []);
  function saveWorkshopDoc(d) {
    setWorkshopDocs(prev => {
      const i = prev.findIndex(x => x.id === d.id);
      if (i >= 0) {
        const next = [...prev];
        next[i] = d;
        return next;
      }
      return [d, ...prev];
    });
  }
  function removeWorkshopDoc(id) {
    setWorkshopDocs(prev => prev.filter(d => d.id !== id));
  }
  function toggleLock(name) {
    setLockedTokens(prev => prev.includes(name) ? prev.filter(x => x !== name) : [...prev, name]);
  }
  function addSavedRewrite(entry) {
    setSavedRewrites(prev => [entry, ...prev].slice(0, 50));
  }
  function removeSavedRewrite(id) {
    setSavedRewrites(prev => prev.filter(r => r.id !== id));
  }

  // Rehydrate persisted generated icons into CV_ICONS.data at boot
  useEffect_app(() => {
    if (window.CV_ICONS && generatedIcons.length) {
      for (const g of generatedIcons) {
        if (!window.CV_ICONS.data[g.name]) window.CV_ICONS.data[g.name] = g.body;
      }
    }
  }, []);

  // Apply colorEdits to CSS custom properties on :root
  useEffect_app(() => {
    const root = document.documentElement;
    for (const [name, hex] of Object.entries(colorEdits)) {
      root.style.setProperty(`--${name}`, hex);
    }
  }, [colorEdits]);

  // Apply patternEdits to :root — spacing / radii / shadows / motion all
  // share the same simple --${name}: value protocol.
  useEffect_app(() => {
    const root = document.documentElement;
    for (const [name, val] of Object.entries(patternEdits)) {
      if (val == null) root.style.removeProperty(`--${name}`);else root.style.setProperty(`--${name}`, val);
    }
  }, [patternEdits]);

  // Keep the global WS_DOCS store in sync so embed blocks update reactively
  useEffect_app(() => {
    window.WS_DOCS?.set(workshopDocs);
  }, [workshopDocs]);

  // Keep WS_VARS in sync; also bind save handler so VARS edits persist
  useEffect_app(() => {
    window.WS_VARS?.set(workspaceVars);
  }, [workspaceVars]);
  useEffect_app(() => {
    window.WS_VARS?.bindSave(setWorkspaceVars);
  }, []);

  // Expose a global setActive so cross-canvas widgets (Vi suggestions, editor
  // links, etc.) can route without prop drilling.
  useEffect_app(() => {
    window.cvNav = target => setActive(target);
    return () => {
      delete window.cvNav;
    };
  }, []);

  // Global Cmd+K
  useEffect_app(() => {
    function onKey(e) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setPaletteOpen(true);
      }
    }
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, []);
  const recentActivity = [...generatedIcons.slice(-2).reverse().map(g => ({
    text: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("b", null, "Adopted \"", g.name, "\""), " into icons."),
    by: 'via Vi',
    time: 'recent',
    icon: 'star',
    color: 'gold'
  })), ...Object.entries(colorEdits).slice(-1).map(([n, hex]) => ({
    text: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("b", null, "Edited token ", n), " \u2192 ", hex, "."),
    by: 'by you',
    time: 'recent',
    icon: 'color-swatches',
    color: 'gold'
  })), ...savedTemplates.slice(-1).map(t => ({
    text: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("b", null, "Saved template \"", t.name, "\""), "."),
    by: 'by you',
    time: 'recent',
    icon: 'browser',
    color: 'gold'
  })), {
    text: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("b", null, "Brand Kit"), " updated \u2014 added 2 logos."),
    by: 'by you',
    time: '14m',
    icon: 'tag'
  }, {
    text: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("b", null, "Voice rule"), ": \"No exclamation marks\" added."),
    by: 'by you',
    time: '3h',
    icon: 'chat-double'
  }].slice(0, 6);
  const counts = {
    iconCount: Object.keys(window.CV_ICONS?.data || {}).length,
    colorCount: 20 + extraColors.length,
    componentCount: 14 + generatedComponents.length,
    inboxCount: inboxItems.length,
    inboxNew: inboxItems.some(i => !i.appliedCat),
    typeCount: 3,
    logoCount: 4,
    imageryCount: window.cvImageStore?.counts?.()?.total || 0,
    patternCount: 13 + 7 + 6 + 5,
    // spacing + radii + shadows + motion = 31
    templateCount: 3 + savedTemplates.length,
    typeCountTotal: window.CV_REGISTRY?.all().length || 0,
    voiceCount: 7,
    gaps: 3,
    aiReady: window.cvOpenAI?.isConfigured() ? 1 : 0,
    healthScore: Math.min(100, 86 + Math.min(generatedIcons.length, 6) + extraColors.length + Object.keys(colorEdits).length)
  };
  function addGeneratedIcon(g) {
    setGeneratedIcons(prev => prev.some(x => x.name === g.name) ? prev : [...prev, g]);
  }
  function updateGeneratedIcon(name, body) {
    setGeneratedIcons(prev => prev.map(g => g.name === name ? {
      ...g,
      body
    } : g));
  }
  function removeGeneratedIcon(name) {
    setGeneratedIcons(prev => prev.filter(g => g.name !== name));
  }
  function addGeneratedIcons(list) {
    list.forEach(g => {
      if (window.CV_ICONS && !window.CV_ICONS.data[g.name]) window.CV_ICONS.data[g.name] = g.body;
    });
    setGeneratedIcons(prev => {
      const next = [...prev];
      for (const g of list) if (!next.some(x => x.name === g.name)) next.push(g);
      return next;
    });
  }
  function addExtraColors(list) {
    setExtraColors(prev => [...prev, ...list]);
  }
  function setColorEdit(name, hex) {
    setColorEdits(prev => ({
      ...prev,
      [name]: hex
    }));
  }
  function setPatternEdit(name, val) {
    setPatternEdits(prev => {
      const next = {
        ...prev
      };
      if (val == null) {
        delete next[name];
        // also remove from :root so default cascades back
        document.documentElement.style.removeProperty(`--${name}`);
      } else {
        next[name] = val;
      }
      return next;
    });
  }
  function togglePatternLock(name) {
    setLockedPatterns(prev => prev.includes(name) ? prev.filter(x => x !== name) : [...prev, name]);
  }
  function onInboxApplied(cat) {
    setTimeout(() => {
      if (cat === 'icons') window.dsaToast?.('Open Icons to see it in the library →');
      if (cat === 'colors') window.dsaToast?.('Open Colors to see it in the palette →');
    }, 1500);
  }
  function resetSession() {
    if (!confirm('Clear all session state (adopted icons, palette edits, inbox, templates)?')) return;
    window.cvStudioStorage?.clear();
    location.reload();
  }
  function saveTemplate(t) {
    setSavedTemplates(prev => [t, ...prev]);
  }
  function removeTemplate(id) {
    setSavedTemplates(prev => prev.filter(t => t.id !== id));
  }
  function runTemplateBrief(brief) {
    setPendingBrief(brief);
    setActive('build');
    setTimeout(() => setPendingBrief(null), 100);
  }
  function runWorkshopTemplate(materializedDoc) {
    // Insert the materialized doc into the workshop store and switch surface
    saveWorkshopDoc(materializedDoc);
    setPendingWorkshopDoc(materializedDoc.id);
    setActive('workshop');
    setTimeout(() => setPendingWorkshopDoc(null), 200);
  }
  function copyText(s) {
    navigator.clipboard?.writeText(s);
    window.dsaToast?.(`Copied "${s}"`);
  }
  let canvas;
  if (active === 'overview') canvas = /*#__PURE__*/React.createElement(Overview, {
    counts: counts,
    onNav: setActive,
    recentActivity: recentActivity,
    onExport: () => setExportOpen(true),
    onReset: resetSession
  });else if (active === 'inbox') canvas = /*#__PURE__*/React.createElement(Inbox, {
    items: inboxItems,
    setItems: setInboxItems,
    onApplied: onInboxApplied
  });else if (active === 'icons') canvas = /*#__PURE__*/React.createElement(Icons, {
    generated: generatedIcons,
    addGenerated: addGeneratedIcon,
    updateGenerated: updateGeneratedIcon,
    removeGenerated: removeGeneratedIcon
  });else if (active === 'colors') canvas = /*#__PURE__*/React.createElement(Colors, {
    extras: extraColors,
    addExtras: addExtraColors,
    colorEdits: colorEdits,
    setColorEdit: setColorEdit,
    snapshot: paletteSnapshot,
    setSnapshot: setPaletteSnapshot,
    lockedTokens: lockedTokens,
    toggleLock: toggleLock
  });else if (active === 'voice') canvas = /*#__PURE__*/React.createElement(Voice, {
    savedRewrites: savedRewrites,
    addSavedRewrite: addSavedRewrite,
    removeSavedRewrite: removeSavedRewrite
  });else if (active === 'build') canvas = /*#__PURE__*/React.createElement(Build, {
    initialBrief: pendingBrief,
    onAdoptIcons: addGeneratedIcons,
    onAdoptColors: addExtraColors,
    onSaveAsTemplate: saveTemplate,
    onNav: setActive,
    onOpenInWorkshop: runWorkshopTemplate
  });else if (active === 'templates') canvas = /*#__PURE__*/React.createElement(Templates, {
    savedTemplates: savedTemplates,
    removeTemplate: removeTemplate,
    onRunBrief: runTemplateBrief,
    onRunWorkshopTemplate: runWorkshopTemplate,
    onOpenRegistry: () => setActive('registry')
  });else if (active === 'registry') canvas = /*#__PURE__*/React.createElement(Registry, {
    onOpenBuilder: id => {
      setTbTypeId(id || null);
      setActive('type-builder');
    }
  });else if (active === 'architecture') canvas = /*#__PURE__*/React.createElement(Architecture, {
    onNav: setActive,
    onOpenBuilder: id => {
      setTbTypeId(id || null);
      setActive('type-builder');
    }
  });else if (active === 'type-builder') canvas = /*#__PURE__*/React.createElement(TypeBuilder, {
    initialTypeId: tbTypeId,
    onClose: () => setActive('registry'),
    onSaved: () => {
      setActive('registry');
    }
  });else if (active === 'components') canvas = /*#__PURE__*/React.createElement(Components, {
    generated: generatedComponents,
    addGenerated: c => setGeneratedComponents(prev => [...prev, c])
  });else if (active === 'workshop') canvas = /*#__PURE__*/React.createElement(Workshop, {
    docs: workshopDocs,
    saveDoc: saveWorkshopDoc,
    removeDoc: removeWorkshopDoc,
    saveTemplate: saveTemplate,
    pendingDocId: pendingWorkshopDoc
  });else if (active === 'patterns') canvas = /*#__PURE__*/React.createElement(Patterns, {
    edits: patternEdits,
    setEdit: setPatternEdit,
    snapshot: patternSnapshot,
    setSnapshot: setPatternSnapshot,
    locked: lockedPatterns,
    toggleLock: togglePatternLock
  });else if (active === 'imagery') canvas = /*#__PURE__*/React.createElement(Imagery, {
    onNav: setActive
  });else if (active === 'bridge') canvas = /*#__PURE__*/React.createElement(Bridge, null);else if (active === 'settings') canvas = /*#__PURE__*/React.createElement(Settings, null);else canvas = /*#__PURE__*/React.createElement(StubCanvas, {
    id: active
  });
  return /*#__PURE__*/React.createElement("div", {
    className: `dsa-shell ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`
  }, !sidebarCollapsed && /*#__PURE__*/React.createElement(Sidebar, {
    active: active,
    onSelect: setActive,
    counts: counts,
    onOpenSearch: () => setPaletteOpen(true),
    onCollapse: () => setSidebarCollapsed(true)
  }), sidebarCollapsed && /*#__PURE__*/React.createElement("button", {
    type: "button",
    className: "dsa-drawer-reopen",
    onClick: () => setSidebarCollapsed(false),
    title: "Show sidebar",
    "aria-label": "Show sidebar"
  }, /*#__PURE__*/React.createElement(CvIcon, {
    name: "sidebar-close",
    size: 16,
    tone: "bronze"
  })), /*#__PURE__*/React.createElement("main", {
    className: "dsa-main"
  }, canvas), active !== 'registry' && /*#__PURE__*/React.createElement(ChatRail, {
    scope: active
  }), /*#__PURE__*/React.createElement(Toast, null), /*#__PURE__*/React.createElement(ExportPatch, {
    open: exportOpen,
    onClose: () => setExportOpen(false),
    generatedIcons: generatedIcons,
    extraColors: extraColors,
    colorEdits: colorEdits,
    patternEdits: patternEdits
  }), /*#__PURE__*/React.createElement(CommandPalette, {
    open: paletteOpen,
    onClose: () => setPaletteOpen(false),
    nav: setActive,
    openExport: () => setExportOpen(true),
    copyText: copyText
  }), /*#__PURE__*/React.createElement(SaveAsTypeModal, null));
}
const _mountApp = document.getElementById('app');
if (_mountApp) ReactDOM.createRoot(_mountApp).render(/*#__PURE__*/React.createElement(App, null));
})(); } catch (e) { __ds_ns.__errors.push({ path: "app/App.jsx", error: String((e && e.message) || e) }); }

// app/ai/ai-capabilities-canvas.js
try { (() => {
// app/ai/ai-capabilities-canvas.js
// ============================================================================
// CV_AI canvas capability catalogue — every per-canvas generative move
// registered as a first-class capability, so the catalogue describes the FULL
// generative surface of the app (not just the composer's 11 + image's 2).
//
// Each entry is data: queryable, inheritable, projectable in the registry
// inspector, and executable through CV_AI.execute(). To keep each canvas's
// bespoke prompt single-sourced (it stays where its domain helpers live), these
// capabilities share a generic `run` that completes a prompt handed in via
// params — so registering the move does NOT duplicate the prompt text. A canvas
// invokes its move with:
//     CV_AI.execute('<id>', { params: { prompt }, surface: '<surface>' })
// which resolves the provider, composes the voice behaviour, records the move,
// and returns the raw reply for the canvas's existing parse.
//
// This completes "the interface is a projection into both, synchronised" for
// every screen: each surface's moves are in the one catalogue the inspector and
// the AI both read.
// ============================================================================

(function () {
  const AI = window.CV_AI;
  if (!AI) throw new Error('[ai-capabilities-canvas] CV_AI not loaded — load app/ai/ai-registry.js first');

  // Generic text run — completes the prompt the canvas hands in (string or
  // {messages}); returns the raw reply. The canvas keeps its own parse.
  const runText = a => a.provider.complete(a.params && (a.params.prompt != null ? a.params.prompt : a.params));
  // Generic image runs — delegate to the resolved image provider.
  const runImgGen = a => a.provider.generateImage(a.params || {});
  const runImgEdit = a => a.provider.editImage(a.params || {});

  // [id, name, family, surfaces[], icon, provider?, run?]
  const TEXT = [
  // Colors canvas
  ['color.palette.generate', 'Generate palette', 'color', ['colors'], 'palette'], ['color.recolor', 'Recolor swatch', 'color', ['colors'], 'droplet'],
  // Icons canvas
  ['icon.generate', 'Generate icon set', 'icon', ['icons'], 'grid'], ['icon.edit', 'Edit icon', 'icon', ['icons'], 'edit'], ['icon.single', 'Generate one icon', 'icon', ['icons'], 'plus'],
  // Voice canvas (composes VOICE_RULES inside its own prompt; voice behaviour additive)
  ['voice.rewrite', 'Rewrite in voice', 'voice', ['voice'], 'feather'], ['voice.variants', 'Copy variants', 'voice', ['voice'], 'copy'], ['voice.audit', 'Audit copy', 'voice', ['voice'], 'search'],
  // Patterns canvas
  ['pattern.generate', 'Generate pattern set', 'pattern', ['patterns'], 'layers'], ['pattern.shadow', 'Generate shadow', 'pattern', ['patterns'], 'box'],
  // Components canvas
  ['component.generate', 'Generate component', 'component', ['components'], 'component'],
  // Build orchestrator
  ['build.plan', 'Plan build', 'build', ['build'], 'list'], ['build.triage', 'Triage edit', 'build', ['build'], 'filter'], ['build.copy', 'Write copy', 'build', ['build'], 'feather'], ['build.icons', 'Build icons', 'build', ['build'], 'grid'], ['build.colors', 'Build colors', 'build', ['build'], 'palette'], ['build.template', 'Extract template', 'build', ['build'], 'bookmark'],
  // Workshop composer (doc-level, beyond the 11 block-level capabilities)
  ['deck.generate', 'Generate deck', 'deck', ['deck', 'brochure'], 'file-plus'], ['block.refine', 'Refine block data', 'deck', ['deck', 'brochure'], 'edit'], ['block.variations', 'Block variations', 'deck', ['deck', 'brochure'], 'shuffle'], ['slide.compose', 'Compose slide', 'deck', ['deck', 'brochure'], 'layout'],
  // Widget / Wizard drafting (whole-doc draft from a brief)
  ['widget.draft', 'Draft widget', 'widget', ['widget'], 'activity'], ['wizard.draft', 'Draft wizard', 'wizard', ['wizard'], 'list'],
  // Type registry Vi (the type system's own generator)
  ['type.propose', 'Propose Type', 'type', ['registry'], 'plus-square'], ['type.materialize', 'Materialize Type', 'type', ['registry'], 'box'], ['type.suggest-slots', 'Suggest slots', 'type', ['registry'], 'grid'],
  // Inbox classifier
  ['inbox.classify', 'Classify item', 'inbox', ['inbox'], 'filter'],
  // Chat rail (free-form Vi conversation)
  ['chat.respond', 'Chat response', 'chat', ['*'], 'chat']];
  const IMAGE = [['image.studio.generate', 'Studio generate', 'image', ['imagery'], 'image', runImgGen], ['image.studio.edit', 'Studio edit', 'image', ['imagery'], 'edit', runImgEdit]];
  for (const [id, name, family, surfaces, icon] of TEXT) {
    AI.register({
      id,
      name,
      layer: 'capability',
      family,
      surfaces,
      behaviours: ['voice.conceptv'],
      provider: 'claude',
      params: {},
      icon,
      provenance: 'built-in',
      run: runText,
      description: name + ' — a Vi generative move on the ' + family + ' surface (catalogued; prompt single-sourced in its canvas).'
    }, {
      silent: true
    });
  }
  for (const [id, name, family, surfaces, icon, run] of IMAGE) {
    AI.register({
      id,
      name,
      layer: 'capability',
      family,
      surfaces,
      behaviours: [],
      provider: 'openai-image',
      params: {},
      icon,
      provenance: 'built-in',
      run,
      description: name + ' — a Vi image move via the openai-image provider.'
    }, {
      silent: true
    });
  }

  // deck.titlechain — the narrative title-chain move (DESIGN-LANGUAGE §16, from
  // capital-raise): emit a deck's slide titles as ONE running sentence, each a
  // clause continuing the prior via a leading connective, so the argument reads
  // from the title rail alone. The RULE is single-sourced in this run; the house
  // voice is composed by the registry (not re-inlined).
  AI.register({
    id: 'deck.titlechain',
    name: 'Chain deck titles',
    layer: 'capability',
    family: 'deck',
    surfaces: ['deck', 'brochure'],
    behaviours: ['voice.conceptv'],
    provider: 'claude',
    params: {},
    icon: 'link',
    provenance: 'built-in',
    description: 'Write a deck\u2019s slide titles as one running sentence \u2014 each a clause continuing the previous via a leading connective (But/To/With/That/Which/By/And) \u2014 so the argument reads from the title rail alone (DESIGN-LANGUAGE \u00a716).',
    run: a => {
      const p = a.params || {};
      const outline = p.slides || p.outline || a.brief || '';
      const n = p.count || (Array.isArray(outline) ? outline.length : 8);
      return a.provider.complete('Write a deck\u2019s slide TITLES as ONE running sentence. Each title is a clause that CONTINUES the previous one, beginning with a leading connective (But / To / With / That / Which / By / And / Because / So). Read top to bottom, the titles must parse as a single argument following the arc: problem \u2192 thesis \u2192 mechanism \u2192 proof \u2192 moat \u2192 ask. Return exactly ' + n + ' titles, one per line, sentence case, no numbering, no quotes. Outline / topic:\n' + (typeof outline === 'string' ? outline : JSON.stringify(outline)));
    }
  }, {
    silent: true
  });
  window.CV_AI._canvasCapsSeeded = true;
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "app/ai/ai-capabilities-canvas.js", error: String((e && e.message) || e) }); }

// app/ai/ai-glyphic.js
try { (() => {
// app/ai/ai-glyphic.js
// ============================================================================
// Registers the AI GLYPHIC-FOUNDRY moves into CV_AI — the registry-way wiring
// of "the AI system built into the icon system". Two capabilities:
//
//   glyphic.generate  — propose N candidate SYMBOL records from a brief
//                        (multi-step conversation = repeated calls with the
//                        running thread as context; the surface renders the
//                        candidates live and feeds picks/feedback back in).
//   glyphic.save      — commit a chosen candidate into CV_ICONS (+ taxonomy),
//                        schema-validated, provenance 'vi'. Instantly live.
//
// SINGLE SOURCE: the record SHAPE is CV_GLYPHIC.schema; the write path is
// CV_ICONS.add; the voice is the 'voice.conceptv' behaviour. This file owns
// only the prompt + parse, co-located as the capability declares.
//
// Load after ai-registry.js (and cv-icons/cv-glyphics for the save path).
// ============================================================================
(function () {
  'use strict';

  var AI = window.CV_AI;
  if (!AI) {
    console.error('ai-glyphic.js: CV_AI must load first');
    return;
  }

  // Build the generation prompt. Threads prior turns + the live taxonomy so Vi
  // proposes ON-system symbols (24px line glyphs) with tags/domain/kind filled.
  function buildPrompt(a) {
    var p = a.params || {};
    var brief = p.brief || a.brief || '';
    var n = p.count || 4;
    var tax = window.CV_ICONS && window.CV_ICONS.taxonomy || {
      domains: {},
      kinds: {}
    };
    var domains = Object.keys(tax.domains || {}).join(', ');
    var kinds = Object.keys(tax.kinds || {}).join(', ');
    var thread = (p.thread || []).map(function (t) {
      return (t.role || 'user') + ': ' + t.text;
    }).join('\n');
    return ['You are drawing ConceptV line-symbols for the Glyphic system.', 'STYLE: a single 24×24 SVG body (paths/circles only, NO <svg> wrapper), fill="none",', 'stroke=currentColor, stroke-width 1.5, round caps/joins. Clean, geometric, 2px margin.', 'Return ONLY a JSON array of ' + n + ' candidates, each:', '{ "id":"kebab-case", "name":"Title Case", "description":"one line",', '  "svg":"<path .../>", "facets":{ "domain":<one of: ' + domains + '>,', '  "kind":<one of: ' + kinds + '>, "tags":["..."] } }', thread ? '\nConversation so far:\n' + thread : '', '\nBrief: ' + brief].join('\n');
  }
  function parseCandidates(reply) {
    var txt = String(reply == null ? '' : reply);
    var m = txt.match(/\[[\s\S]*\]/);
    if (!m) throw new Error('glyphic.generate: model reply had no JSON array');
    var arr = JSON.parse(m[0]);
    var GL = window.CV_GLYPHIC;
    return arr.map(function (rec) {
      var problems = GL && GL.validateSymbol ? GL.validateSymbol(rec) : [];
      return {
        record: rec,
        valid: problems.length === 0,
        problems: problems
      };
    });
  }
  AI.register({
    id: 'glyphic.generate',
    name: 'Generate glyphic symbols',
    layer: 'capability',
    family: 'icon',
    surfaces: ['icons', 'glyphics', '*'],
    behaviours: ['voice.conceptv'],
    provider: 'claude',
    params: {
      brief: '',
      count: 4,
      thread: []
    },
    icon: 'plus',
    provenance: 'built-in',
    description: 'Propose candidate symbol records (24px line glyphs + tags/domain/kind) from a brief; multi-step by threading prior turns. Candidates validate against CV_GLYPHIC.schema; save with glyphic.save.',
    run: function (a) {
      var prompt = buildPrompt(a);
      var complete = AI.complete ? AI.complete.bind(AI) : a.provider && a.provider.complete;
      if (!complete) throw new Error('glyphic.generate: no completion provider (CV_AI.complete / provider.complete)');
      return Promise.resolve(complete(prompt)).then(parseCandidates);
    }
  }, {
    silent: true
  });
  AI.register({
    id: 'glyphic.save',
    name: 'Save glyphic symbol',
    layer: 'capability',
    family: 'icon',
    surfaces: ['icons', 'glyphics', '*'],
    behaviours: [],
    provider: null,
    params: {
      record: null
    },
    icon: 'check-square',
    provenance: 'built-in',
    description: 'Commit a chosen symbol candidate into the icon library (CV_ICONS.add) + taxonomy, schema-validated, provenance vi. Instantly available to the explorer, CV_GLYPHIC and the registry.',
    run: function (a) {
      var rec = (a.params || {}).record;
      if (!window.CV_ICONS || !window.CV_ICONS.add) throw new Error('glyphic.save: CV_ICONS.add unavailable');
      var id = window.CV_ICONS.add(Object.assign({
        provenance: 'vi'
      }, rec));
      return {
        saved: id
      };
    }
  }, {
    silent: true
  });
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "app/ai/ai-glyphic.js", error: String((e && e.message) || e) }); }

// app/ai/ai-registry.js
try { (() => {
// app/ai/ai-registry.js
// ============================================================================
// CV_AI — the Universal AI Registry.
//
// The AI layer expressed in the SAME shape as everything else in the unified
// system (cf. app/registry/types-core.js → CV_REGISTRY, core/RenderType.jsx).
// Where CV_REGISTRY answers "what can be composed?", CV_AI answers "what can Vi
// DO, with what, knowing where it is?" — and it does so the same way: a single
// hierarchical registry of parametric, inheritable, resolvable entries, with
// the running interface a *projection* of the registry rather than a parallel
// pile of hand-written functions.
//
// Generative discipline (identical to the rest of the system):
//   ai-output = f(capability, context, params)
// A capability is NOT a bespoke function with an inline prompt. It is a Type:
// it declares which behaviours it composes, which provider it runs on, what
// params (dials) it takes, and how to build its prompt from (resolved context
// + behaviours + params). Add a new AI move = register data, not write code.
//
// === Layers (low → high, atomic composition) ===============================
//   provider   A model endpoint: claude (text/stream), openai-image (image).
//              Capabilities + inference, exactly like the type system's tokens.
//   behaviour  A reusable instruction fragment composed INTO prompts: the
//              ConceptV voice, an "angle" (shorter/formal/specific), a persona.
//   skill      A named parametric intent a user can invoke (the doc transforms:
//              shorten / urgent / audit / …). Binds to a capability + params.
//   capability A tool: one generative operation (insert.block, alternate.block,
//              theme.generate, field.alternate, …). Composes behaviours, picks
//              a provider, resolves context, builds a prompt, parses candidates.
//   context    A resolver keyed by surface: projects "what screen Vi is on"
//              (deck / widget / wizard / brochure + selection) into the compact
//              context object every capability's prompt is built from.
//
// One registry, every surface. The composer, the chat rail, the field toolbar,
// the registry inspector and any future surface all resolve the SAME catalogue
// and the SAME live context — so the AI and the interface are synchronised by
// construction (they read one source), not by hand.
//
// Mirrors CV_REGISTRY's API surface verbatim so the two registries are learnable
// as one: register/registerMany/update/remove/get/all/query/resolve/lineage/
// subscribe, LS-persisted user/vi provenance, built-ins in memory.
// ============================================================================

(function () {
  const LAYERS = ['provider', 'behaviour', 'skill', 'capability', 'context'];
  const LAYER_INFO = {
    provider: {
      label: 'Provider',
      rank: 0,
      swatch: '#E0C010',
      desc: 'Model endpoint — claude (text/stream), openai (image).'
    },
    behaviour: {
      label: 'Behaviour',
      rank: 1,
      swatch: '#B7973C',
      desc: 'Reusable instruction fragment composed into prompts — voice, angle, persona.'
    },
    skill: {
      label: 'Skill',
      rank: 2,
      swatch: '#988058',
      desc: 'Named parametric intent a user invokes — shorten, urgent, audit.'
    },
    capability: {
      label: 'Capability',
      rank: 3,
      swatch: '#7E6539',
      desc: 'A tool — one generative operation. Composes behaviours, picks a provider.'
    },
    context: {
      label: 'Context',
      rank: 4,
      swatch: '#5B4628',
      desc: 'Surface-keyed resolver — projects the current screen into Vi\u2019s operating context.'
    }
  };
  const STORAGE_KEY = 'cv:ai-registry:user-entries';
  const listeners = new Set();
  let suppressNotify = false;

  // Built-ins live in memory (re-seeded each load); user/vi persisted to LS.
  const BUILTIN = new Map();
  const USER = new Map();
  function loadFromStorage() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) for (const t of JSON.parse(raw)) USER.set(t.id, t);
    } catch {}
  }
  function saveUser() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify([...USER.values()]));
    } catch {}
  }

  // ---------------------------------------------------------------------------
  // Registry API — mirrors CV_REGISTRY
  // ---------------------------------------------------------------------------
  function register(entry, opts = {}) {
    const t = normalize(entry);
    if (!t.id) {
      throw new Error('[CV_AI] entry missing id: ' + JSON.stringify(entry).slice(0, 120));
    }
    if (!LAYERS.includes(t.layer)) {
      throw new Error('[CV_AI] entry "' + t.id + '" has unknown layer "' + t.layer + '" (expected one of ' + LAYERS.join('/') + ')');
    }
    if (t.provenance === 'built-in') BUILTIN.set(t.id, t);else USER.set(t.id, t);
    if (!opts.silent) {
      if (t.provenance !== 'built-in') saveUser();
      notify();
    }
    return t;
  }
  function registerMany(entries, opts = {}) {
    suppressNotify = true;
    try {
      for (const t of entries) register(t, {
        silent: true
      });
    } finally {
      suppressNotify = false;
    }
    if (!opts.silent) {
      saveUser();
      notify();
    }
  }
  function update(id, patch, opts = {}) {
    const cur = get(id);
    if (!cur) return null;
    if (cur.provenance === 'built-in') {
      // built-ins fork into user space on edit (same contract as CV_REGISTRY)
      return register({
        ...cur,
        ...patch,
        id: cur.id,
        provenance: 'user',
        forkedFrom: cur.id,
        updatedAt: Date.now(),
        version: (cur.version || 1) + 1
      }, opts);
    }
    return register({
      ...cur,
      ...patch,
      updatedAt: Date.now(),
      version: (cur.version || 1) + 1
    }, opts);
  }
  function remove(id, opts = {}) {
    if (BUILTIN.has(id)) return false;
    const removed = USER.delete(id);
    if (removed && !opts.silent) {
      saveUser();
      notify();
    }
    return removed;
  }
  function get(id) {
    return id ? USER.get(id) || BUILTIN.get(id) || null : null;
  }
  function all() {
    return [...BUILTIN.values(), ...USER.values()];
  }
  function query({
    layer,
    layers,
    family,
    families,
    surface,
    tags,
    provenance,
    extendsId,
    search
  } = {}) {
    let out = all();
    if (layer) out = out.filter(t => t.layer === layer);
    if (layers && layers.length) out = out.filter(t => layers.includes(t.layer));
    if (family) out = out.filter(t => t.family === family);
    if (families && families.length) out = out.filter(t => families.includes(t.family));
    if (surface) out = out.filter(t => !t.surfaces || t.surfaces.includes('*') || t.surfaces.includes(surface));
    if (provenance) out = out.filter(t => t.provenance === provenance);
    if (extendsId) out = out.filter(t => t.extends === extendsId);
    if (tags && tags.length) out = out.filter(t => (t.tags || []).some(x => tags.includes(x)));
    if (search) {
      const q = search.toLowerCase();
      out = out.filter(t => t.id.includes(q) || (t.name || '').toLowerCase().includes(q) || (t.description || '').toLowerCase().includes(q) || (t.tags || []).some(x => x.toLowerCase().includes(q)));
    }
    return out.sort(byLayerThenName);
  }
  function byLayerThenName(a, b) {
    const da = LAYER_INFO[a.layer]?.rank ?? 99,
      db = LAYER_INFO[b.layer]?.rank ?? 99;
    if (da !== db) return da - db;
    return (a.name || '').localeCompare(b.name || '');
  }

  // ---------------------------------------------------------------------------
  // Inheritance — flatten an entry with its ancestors (leaf wins). Lets a
  // capability `extends` a base capability and override params/behaviours, the
  // way a Type extends a Type. Functions (build/parse/resolve) inherit too.
  // ---------------------------------------------------------------------------
  function resolve(id) {
    const chain = lineage(id);
    if (!chain.length) return null;
    const merged = chain.reduceRight((acc, t) => ({
      ...acc,
      ...t,
      params: {
        ...(acc.params || {}),
        ...(t.params || {})
      },
      behaviours: [...new Set([...(acc.behaviours || []), ...(t.behaviours || [])])],
      surfaces: t.surfaces || acc.surfaces,
      tags: [...new Set([...(acc.tags || []), ...(t.tags || [])])]
    }), {});
    merged.lineage = chain.map(t => t.id);
    merged.id = chain[0].id;
    merged.name = chain[0].name;
    merged.provenance = chain[0].provenance;
    return merged;
  }
  function lineage(id) {
    const out = [];
    const seen = new Set();
    let cur = get(id);
    while (cur && !seen.has(cur.id)) {
      seen.add(cur.id);
      out.push(cur);
      cur = cur.extends ? get(cur.extends) : null;
    }
    return out;
  }
  function children(id) {
    return all().filter(t => t.extends === id);
  }

  // ---------------------------------------------------------------------------
  // Normalize — fill defaults, stamp timestamps (mirrors CV_REGISTRY.normalize)
  // ---------------------------------------------------------------------------
  function normalize(t) {
    const now = Date.now();
    return {
      id: t.id,
      name: t.name || t.id,
      layer: t.layer || 'capability',
      family: t.family || t.layer || 'capability',
      description: t.description || '',
      extends: t.extends || null,
      surfaces: t.surfaces || null,
      // which surfaces an entry applies to (null = any)
      behaviours: t.behaviours || [],
      // behaviour ids a capability composes
      provider: t.provider || null,
      // provider id a capability runs on
      params: t.params || {},
      // dials (count, angle, …)
      tags: t.tags || [],
      provenance: t.provenance || 'user',
      icon: t.icon || 'sparkles',
      // functional members (built-ins set these; carried through untouched)
      run: t.run,
      // capability: ({doc,target,ctx,params,provider}) -> candidate[] (owns build→complete→parse)
      build: t.build,
      // capability: (doc, target, ctx, params) -> prompt string
      parse: t.parse,
      // capability: (reply, doc, target, params) -> candidate[]
      resolveCtx: t.resolveCtx,
      // context: (doc, ctx) -> contextObject
      text: t.text,
      // behaviour: instruction fragment (string or fn(params)->string)
      instruction: t.instruction,
      // skill: the intent text
      target: t.target,
      // skill: capability id + target descriptor it invokes
      runtime: t.runtime || null,
      // provider: { kind } — how to reach the live endpoint
      modality: t.modality || null,
      // provider: ['text'] | ['text','stream'] | ['image']
      caps: t.caps || null,
      // provider: { stream, json, maxPromptChars }
      createdAt: t.createdAt || now,
      updatedAt: t.updatedAt || now,
      version: t.version || 1,
      forkedFrom: t.forkedFrom || null
    };
  }

  // ---------------------------------------------------------------------------
  // Provider resolution — bind a provider entry to its LIVE runtime, with
  // inference for unknown ids (mirrors openai.js getModelCapabilities). LOUD:
  // if the runtime an entry names isn't present, throw — no silent fallback.
  // ---------------------------------------------------------------------------
  function resolveProvider(id) {
    const p = get(id);
    if (!p) throw new Error('[CV_AI] provider not found: "' + id + '" (registered providers: ' + query({
      layer: 'provider'
    }).map(x => x.id).join(', ') + ')');
    if (p.layer !== 'provider') throw new Error('[CV_AI] "' + id + '" is a ' + p.layer + ', not a provider');
    const kind = p.runtime && p.runtime.kind;
    if (kind === 'claude') {
      if (typeof window === 'undefined' || !window.claude || typeof window.claude.complete !== 'function') {
        throw new Error('[CV_AI] provider "' + id + '" runtime (window.claude.complete) not available');
      }
      return {
        ...p,
        async complete(prompt, opts) {
          // window.claude.complete accepts a string or {messages}
          return opts && opts.messages ? window.claude.complete(opts) : window.claude.complete(prompt);
        }
      };
    }
    if (kind === 'openai-image') {
      const svc = typeof window !== 'undefined' ? window.cvOpenAI : null;
      if (!svc || typeof svc.generateImage !== 'function' || typeof svc.editImage !== 'function') {
        throw new Error('[CV_AI] provider "' + id + '" runtime (window.cvOpenAI) not available');
      }
      return {
        ...p,
        service: svc,
        generateImage: opts => svc.generateImage(opts),
        editImage: opts => svc.editImage(opts),
        responsesImage: opts => svc.responsesImage(opts),
        getModelCapabilities: modelId => svc.getModelCapabilities(modelId)
      };
    }
    // Any other runtime kind is owned by the Host/Environment layer (CV_HOST):
    // filesystem providers, native/MCP model endpoints. Delegate to it so the
    // AI catalogue can name providers it doesn't itself know how to reach. Loud:
    // CV_HOST returns a bound runtime or throws naming how to activate it.
    if (typeof window !== 'undefined' && window.CV_HOST && typeof window.CV_HOST.resolveProviderRuntime === 'function') {
      const bound = window.CV_HOST.resolveProviderRuntime(p);
      if (bound) return bound;
    }
    throw new Error('[CV_AI] provider "' + id + '" has unknown runtime kind "' + kind + '" (no CV_HOST runtime claimed it)');
  }

  // ---------------------------------------------------------------------------
  // Context resolution — "resolve context from what screen Vi is on." Runs the
  // registered context resolver whose surface matches, producing the compact
  // context object capabilities build prompts from. Falls through a generic
  // resolver so every surface gets SOME context, never nothing.
  // ---------------------------------------------------------------------------
  function resolveContext({
    surface,
    doc,
    ctx
  } = {}) {
    const sfc = surface || doc && doc.type || ACTIVE.surface || 'generic';
    const base = {
      surface: sfc,
      doc,
      ...(ctx || {})
    };
    // most specific surface resolver wins; 'generic' is the floor
    const resolver = query({
      layer: 'context'
    }).find(c => (c.surfaces || []).includes(sfc)) || get('context.generic');
    if (resolver && typeof resolver.resolveCtx === 'function') {
      try {
        return {
          ...base,
          ...resolver.resolveCtx(doc, base)
        };
      } catch (e) {
        throw new Error('[CV_AI] context resolver "' + resolver.id + '" failed: ' + e.message);
      }
    }
    return base;
  }

  // ---------------------------------------------------------------------------
  // Behaviour composition — concatenate the resolved behaviour fragments a
  // capability declares (+ any extra ids), into the prompt preamble.
  // ---------------------------------------------------------------------------
  function composeBehaviours(ids, params) {
    return (ids || []).map(bid => {
      const b = get(bid);
      if (!b) throw new Error('[CV_AI] behaviour not found: "' + bid + '"');
      const txt = typeof b.text === 'function' ? b.text(params || {}) : b.text;
      return txt || '';
    }).filter(Boolean).join('\n\n');
  }

  // ---------------------------------------------------------------------------
  // execute — THE generative path: ai-output = f(capability, context, params).
  // Resolves the capability (+ inheritance), resolves context from the active
  // surface, composes behaviours, builds the prompt, dispatches to the resolved
  // provider, parses candidates. Every failure is loud.
  // ---------------------------------------------------------------------------
  async function execute(capabilityId, {
    doc,
    target,
    ctx,
    params,
    brief,
    surface
  } = {}) {
    const cap = resolve(capabilityId);
    if (!cap) throw new Error('[CV_AI] capability not found: "' + capabilityId + '" (registered: ' + query({
      layer: 'capability'
    }).map(x => x.id).join(', ') + ')');
    // A skill is a named intent bound to a capability + instruction — delegate
    // to its target capability, threading the skill's instruction as the brief.
    if (cap.layer === 'skill') {
      const targetId = cap.target && cap.target.capability;
      if (!targetId) throw new Error('[CV_AI] skill "' + capabilityId + '" has no target capability');
      return execute(targetId, {
        doc,
        target: {
          ...(cap.target || {}),
          ...(target || {})
        },
        ctx,
        params: {
          ...(params || {}),
          instruction: cap.instruction,
          skill: cap.id
        },
        brief: brief || cap.instruction,
        surface
      });
    }
    if (cap.layer !== 'capability') throw new Error('[CV_AI] "' + capabilityId + '" is a ' + cap.layer + ', not a capability');
    const mergedParams = {
      ...(cap.params || {}),
      ...(params || {}),
      brief: brief || params && params.brief || ''
    };
    const resolvedCtx = resolveContext({
      surface: surface || target && target.surface,
      doc,
      ctx: {
        ...ctx,
        target
      }
    });
    const provider = resolveProvider(cap.provider || 'claude');

    // run() path — the capability owns build→complete→parse (it needs the
    // composer's prompt helpers). It still receives the resolved provider,
    // context and composed behaviour preamble, so routing stays unified.
    if (typeof cap.run === 'function') {
      const preamble = composeBehaviours(cap.behaviours, mergedParams);
      return (await cap.run({
        doc,
        target,
        ctx: resolvedCtx,
        params: mergedParams,
        provider,
        preamble,
        brief: mergedParams.brief
      })) || [];
    }

    // build/parse path — pure-data capabilities (no helper dependency).
    if (typeof cap.build !== 'function') throw new Error('[CV_AI] capability "' + capabilityId + '" has neither run() nor build()');
    const preamble = composeBehaviours(cap.behaviours, mergedParams);
    const body = cap.build(doc, target, resolvedCtx, mergedParams);
    if (!body) return [];
    const reply = await provider.complete(preamble ? preamble + '\n\n' + body : body);
    return (typeof cap.parse === 'function' ? cap.parse(reply, doc, target, mergedParams) : reply) || [];
  }

  // ---------------------------------------------------------------------------
  // Active surface — the single place "what screen Vi is on" is recorded, so
  // context auto-resolves everywhere. Surfaces push to this on focus; the
  // chat rail / field toolbar / suggestions read from it.
  // ---------------------------------------------------------------------------
  const ACTIVE = {
    surface: null,
    doc: null,
    ctx: null
  };
  function setActiveSurface(surface, doc, ctx) {
    ACTIVE.surface = surface;
    ACTIVE.doc = doc != null ? doc : ACTIVE.doc;
    ACTIVE.ctx = ctx || ACTIVE.ctx;
    notify();
  }

  // ---------------------------------------------------------------------------
  function subscribe(fn) {
    listeners.add(fn);
    return () => listeners.delete(fn);
  }
  function notify() {
    if (suppressNotify) return;
    for (const fn of listeners) try {
      fn();
    } catch {}
  }

  // ---------------------------------------------------------------------------
  window.CV_AI = {
    LAYERS,
    LAYER_INFO,
    register,
    registerMany,
    update,
    remove,
    get,
    all,
    query,
    resolve,
    lineage,
    children,
    resolveProvider,
    resolveContext,
    composeBehaviours,
    execute,
    // convenience: route a one-off text completion through the resolved claude
    // provider — the single endpoint every surface should call instead of
    // window.claude.complete directly. Loud if the runtime is absent.
    complete(promptOrOpts) {
      return resolveProvider('claude').complete(promptOrOpts);
    },
    get active() {
      return ACTIVE;
    },
    setActiveSurface,
    subscribe,
    _builtin: BUILTIN,
    _user: USER
  };
  loadFromStorage();
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "app/ai/ai-registry.js", error: String((e && e.message) || e) }); }

// app/ai/ai-seed.js
try { (() => {
// app/ai/ai-seed.js
// ============================================================================
// CV_AI built-in seed — the providers, behaviours, skills and context
// resolvers that don't depend on the composer's prompt helpers. The
// capabilities themselves (which DO use those helpers) are registered from
// canvases/workshop/AIEngine.jsx, exactly as CV_REGISTRY built-ins that carry
// a render() function are seeded where that function lives.
//
// This file is DATA. Each entry is parametric and inheritable; adding a model
// provider, a tone behaviour, a one-click skill, or a new screen's context
// resolver is a registration, not a code change.
// ============================================================================

(function () {
  const AI = window.CV_AI;
  if (!AI) throw new Error('[ai-seed] CV_AI not loaded — load app/ai/ai-registry.js first');

  // ==========================================================================
  // PROVIDERS — model endpoints. Resolved to live runtimes by CV_AI.resolveProvider.
  // ==========================================================================
  AI.register({
    id: 'claude',
    name: 'Claude',
    layer: 'provider',
    family: 'text',
    description: 'Anthropic Claude — the text/JSON generation endpoint behind every Vi authoring move.',
    runtime: {
      kind: 'claude'
    },
    modality: ['text', 'stream'],
    caps: {
      stream: true,
      json: true,
      maxPromptChars: 200000
    },
    icon: 'sparkles',
    provenance: 'built-in',
    tags: ['text', 'json', 'default']
  }, {
    silent: true
  });
  AI.register({
    id: 'openai-image',
    name: 'OpenAI Image',
    layer: 'provider',
    family: 'image',
    description: 'Image generation/edit via the shared window.cvOpenAI service (model + size + quality resolved there).',
    runtime: {
      kind: 'openai-image'
    },
    modality: ['image'],
    caps: {
      stream: false,
      json: false
    },
    icon: 'image',
    provenance: 'built-in',
    tags: ['image']
  }, {
    silent: true
  });
  AI.register({
    id: 'vision',
    name: 'Vision',
    layer: 'provider',
    family: 'image',
    description: 'Multimodal image understanding — reads screenshots/moodboards for layout, type feel, voice and palette. Resolves to a real vision runtime when AtomiCity is exported with one connected; in the browser sandbox it is unavailable and callers fall back to local pixel analysis.',
    runtime: {
      kind: 'vision'
    },
    modality: ['image', 'text'],
    caps: {
      stream: false,
      json: true,
      exportOnly: true
    },
    icon: 'eye',
    provenance: 'built-in',
    tags: ['image', 'vision', 'export']
  }, {
    silent: true
  });

  // ==========================================================================
  // BEHAVIOURS — instruction fragments composed INTO a capability's prompt.
  // The ConceptV voice is the spine; the "angle" behaviours are parametric
  // modifiers a capability or skill selects via params.angle.
  // ==========================================================================
  AI.register({
    id: 'voice.conceptv',
    name: 'ConceptV voice',
    layer: 'behaviour',
    family: 'voice',
    description: 'The house voice every Vi output speaks in — sentence case, second person, no exclamation/emoji, concrete numbers, canonical product names.',
    text: 'Brand voice: sentence case, second-person ("you"), no exclamation marks, no emoji. Concrete numbers. ConceptV names: User Portal, Property Wizard, Virtual Hub (a.k.a. Hub or Linked Hub), Capture, Vi.',
    icon: 'feather',
    provenance: 'built-in',
    tags: ['voice', 'always-on']
  }, {
    silent: true
  });

  // angle behaviour — one entry, parameterised by params.angle (the field
  // toolbar's shorter/formal/specific/different all resolve through this).
  const ANGLE_TEXT = {
    shorter: 'Make each alternative SHORTER than the current — half the word count where possible.',
    formal: 'Make each alternative MORE FORMAL — drop colloquialism, prefer precise verbs.',
    specific: 'Make each alternative MORE SPECIFIC — concrete numbers, named examples, proper nouns where natural.',
    different: 'Each alternative should take a DIFFERENT angle from the current value (and from each other).'
  };
  AI.register({
    id: 'angle',
    name: 'Regeneration angle',
    layer: 'behaviour',
    family: 'angle',
    description: 'Parametric steer applied to field/alternate regeneration — shorter, more formal, more specific, or a fresh angle.',
    text: params => ANGLE_TEXT[params && params.angle] || 'Each alternative should be a distinct angle, similar length and structure to the current.',
    params: {
      angle: 'different'
    },
    icon: 'shuffle',
    provenance: 'built-in',
    tags: ['angle', 'modifier']
  }, {
    silent: true
  });

  // diversity behaviour — used by streaming parallel calls so slots differ.
  AI.register({
    id: 'diversity',
    name: 'Slot diversity',
    layer: 'behaviour',
    family: 'angle',
    description: 'Seeds parallel single-shot generations so the returned candidates are visibly distinct from one another.',
    text: params => params && params.seed ? `Take a distinctly ${params.seed} angle; this is option ${(params.slotIndex ?? 0) + 1} and must differ from the others.` : '',
    icon: 'grid',
    provenance: 'built-in',
    tags: ['angle', 'modifier']
  }, {
    silent: true
  });

  // ==========================================================================
  // SKILLS — named parametric intents a user invokes. Each binds to a
  // capability + a target/param payload. The composer's whole-doc transform
  // menu and the suggestion engine are PROJECTIONS of these entries.
  // ==========================================================================
  const SKILLS = [{
    id: 'skill.shorten',
    name: 'Shorten everything',
    sub: 'Half the word count where possible',
    instruction: 'Shorten every block — half the word count where possible, keep the meaning.'
  }, {
    id: 'skill.lengthen',
    name: 'Lengthen with detail',
    sub: 'Add a supporting sentence per block',
    instruction: 'Add one supporting sentence or specific detail to every long-form block.'
  }, {
    id: 'skill.urgent',
    name: 'More urgent tone',
    sub: 'Sharper verbs, present tense',
    instruction: 'Make the tone more urgent — sharper verbs, present tense, specific numbers.'
  }, {
    id: 'skill.friendly',
    name: 'Warmer / more human',
    sub: 'Second-person, conversational',
    instruction: 'Make this warmer — second-person, conversational, no jargon, still no exclamation marks.'
  }, {
    id: 'skill.pro',
    name: 'More professional',
    sub: 'Precise verbs, concrete metrics',
    instruction: 'Make this more professional — precise verbs, concrete metrics, less marketing fluff.'
  }, {
    id: 'skill.audit',
    name: 'Audit voice & tone',
    sub: 'Enforce ConceptV voice rules',
    instruction: 'Audit every block against ConceptV voice rules (sentence case, second person, no exclamation marks, no emoji). Tighten as needed.'
  }, {
    id: 'skill.concrete',
    name: 'Add concrete numbers',
    sub: 'Replace vague claims with numbers',
    instruction: 'Wherever possible, add a concrete number, percentage, or named example.'
  }];
  for (const s of SKILLS) {
    AI.register({
      id: s.id,
      name: s.name,
      layer: 'skill',
      family: 'transform',
      description: s.sub,
      instruction: s.instruction,
      // a transform skill drives the doc.transform capability
      target: {
        capability: 'doc.transform',
        kind: 'doc.transform'
      },
      icon: 'wand',
      provenance: 'built-in',
      tags: ['transform', 'whole-doc']
    }, {
      silent: true
    });
  }
  // theme skill drives the theme.generate capability (not a doc.transform)
  AI.register({
    id: 'skill.theme',
    name: 'Switch visual theme',
    layer: 'skill',
    family: 'transform',
    description: '3 theme proposals',
    instruction: 'Propose alternative visual themes that fit this document.',
    target: {
      capability: 'theme.generate',
      kind: 'theme.generate'
    },
    icon: 'palette',
    provenance: 'built-in',
    tags: ['transform', 'theme']
  }, {
    silent: true
  });

  // ==========================================================================
  // CONTEXT RESOLVERS — project "what screen Vi is on" into the compact context
  // object every capability's prompt is built from. Keyed by surface; the
  // generic resolver is the floor so no surface is ever context-less.
  // ==========================================================================

  // shared helpers (self-contained — the composer's richer versions live in
  // AIEngine, but context resolution must work even before that module loads)
  function pageNeighbourhood(doc, pageIdx) {
    if (!doc || !doc.pages || !doc.pages.length) return 'Empty document.';
    const line = i => {
      const p = doc.pages[i];
      if (!p) return null;
      return `[page ${i + 1} · ${p.title || p.kind}] ` + (p.sections || []).map(s => `${s.kind}(${JSON.stringify(s.data).slice(0, 70)})`).join(' | ');
    };
    const lines = [];
    for (let i = Math.max(0, pageIdx - 1); i <= Math.min(doc.pages.length - 1, pageIdx + 1); i++) {
      const ln = line(i);
      if (ln) lines.push((i === pageIdx ? '▶ ' : '  ') + ln);
    }
    return lines.join('\n');
  }
  AI.register({
    id: 'context.generic',
    name: 'Generic context',
    layer: 'context',
    family: 'context',
    description: 'Fallback — title + type. Every surface gets at least this.',
    surfaces: ['generic'],
    resolveCtx: doc => ({
      title: doc && doc.title,
      docType: doc && doc.type
    }),
    provenance: 'built-in',
    icon: 'crosshair'
  }, {
    silent: true
  });
  AI.register({
    id: 'context.pages',
    name: 'Page-doc context',
    layer: 'context',
    family: 'context',
    description: 'Decks & brochures — resolves the neighbourhood around the current page plus document-level facts (page count, has-CTA, has-stats).',
    surfaces: ['deck', 'brochure'],
    resolveCtx: (doc, base) => {
      const pageIdx = base && base.currentPage || 0;
      const pages = doc && doc.pages || [];
      return {
        title: doc && doc.title,
        docType: doc && doc.type,
        pageIdx,
        pageCount: pages.length,
        neighbourhood: pageNeighbourhood(doc, pageIdx),
        hasCta: pages.some(p => (p.sections || []).some(s => s.kind === 'button' || s.kind === 'callout' || s.data && s.data.cta)),
        hasStats: pages.some(p => (p.sections || []).some(s => ['stats', 'metricRow', 'statPills', 'statTable'].includes(s.kind))),
        currentPageEmpty: pages[pageIdx] && (!pages[pageIdx].sections || pages[pageIdx].sections.length === 0)
      };
    },
    provenance: 'built-in',
    icon: 'layout'
  }, {
    silent: true
  });
  AI.register({
    id: 'context.widget',
    name: 'Widget context',
    layer: 'context',
    family: 'context',
    description: 'Widgets — resolves the widget kind/system and current data shape (kpis, media, chart) Vi is varying.',
    surfaces: ['widget'],
    resolveCtx: doc => ({
      title: doc && doc.data && doc.data.title,
      docType: 'widget',
      widgetKind: doc && doc.widgetKind,
      system: doc && doc.system,
      kpiCount: doc && doc.data && (doc.data.kpis || []).length,
      hasMedia: !!(doc && doc.data && doc.data.media),
      hasChart: !!(doc && doc.data && doc.data.chart)
    }),
    provenance: 'built-in',
    icon: 'activity'
  }, {
    silent: true
  });
  AI.register({
    id: 'context.wizard',
    name: 'Wizard context',
    layer: 'context',
    family: 'context',
    description: 'Wizards — resolves the wizard kind and the step sequence Vi is inserting into or rewriting.',
    surfaces: ['wizard'],
    resolveCtx: doc => ({
      docType: 'wizard',
      wizardKind: doc && doc.wizardKind,
      stepCount: doc && (doc.steps || []).length,
      steps: doc && (doc.steps || []).map((s, i) => `[${i + 1}] ${s.kind} · ${s.title}`).join('; ')
    }),
    provenance: 'built-in',
    icon: 'list'
  }, {
    silent: true
  });

  // ==========================================================================
  // IMAGE CAPABILITIES — the image endpoint is in the catalogue too, so "what
  // Vi can do" includes imagery and routes through the same execute() path.
  // run() resolves the openai-image provider (loud) and calls it directly.
  // ==========================================================================
  AI.register({
    id: 'image.generate',
    name: 'Generate image',
    layer: 'capability',
    family: 'image',
    description: 'Generate brand imagery from a prompt via the openai-image provider.',
    surfaces: ['*'],
    behaviours: [],
    provider: 'openai-image',
    params: {
      count: 1
    },
    icon: 'image',
    provenance: 'built-in',
    run: a => a.provider.generateImage({
      prompt: a.params.prompt || a.brief,
      n: a.params.count || 1,
      brandEnrich: a.params.brandEnrich !== false
    })
  }, {
    silent: true
  });
  AI.register({
    id: 'image.edit',
    name: 'Edit image',
    layer: 'capability',
    family: 'image',
    description: 'Edit / compose / mask existing imagery via the openai-image provider.',
    surfaces: ['*'],
    behaviours: [],
    provider: 'openai-image',
    params: {
      count: 1
    },
    icon: 'edit',
    provenance: 'built-in',
    run: a => a.provider.editImage({
      prompt: a.params.prompt || a.brief,
      images: a.params.images,
      mask: a.params.mask,
      n: a.params.count || 1
    })
  }, {
    silent: true
  });

  // CV_HOST:ai-entries
  // ^ Vi-authored CV_AI entries (via ds.propose) are inserted ABOVE this line.

  // mark seed completion so AIEngine can assert its prerequisites loudly
  window.CV_AI._seeded = true;
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "app/ai/ai-seed.js", error: String((e && e.message) || e) }); }

// app/ai/host-runtime.js
try { (() => {
// app/ai/host-runtime.js
// ============================================================================
// CV_HOST — the Environment / Host registry.
//
// The system already has four single-source registries (tokens, types, the
// engine, AI). CV_HOST is the layer that answers a different question: "what
// can Vi actually DO to the world it is running in — read files, write files,
// run the compiler, call a tool — and which of those are available HERE?"
//
// It is built in the SAME shape as CV_AI: a registry of pluggable, resolvable
// entries (here: runtimes), a uniform op surface routed to the best available
// runtime, and loud failure when something a caller needs is absent. The
// running UI is a projection of this registry (the Bridge panel + the AI card
// read CV_HOST.describe()), never a parallel hand-written status pile.
//
// THE ONE IDEA, applied to the environment:
//   capability-available = f(environment, runtime)
// A file write is not bespoke code per surface. It is: resolve the best writer
// runtime for the current environment, route the op to it. Add a new way to
// reach the disk (a Tauri shell, an MCP file tool, a cloud workspace) = register
// a runtime, not edit every caller.
//
// === Runtimes (low → high capability) ======================================
//   review   The sandbox FLOOR. No disk. Stages every change into a reviewable
//            queue (persisted to localStorage) for a human / the agent to
//            commit. ALWAYS available — so the system is never dead, only
//            degraded, and degraded EXPLICITLY (the panel says "sandbox").
//   fsapi    Browser File System Access API. Real read/write to a directory the
//            user grants with a gesture. Works when this app is opened as a
//            top-level page (i.e. exported + run locally), not inside the
//            sandboxed editor iframe.
//   native   A local shell (Node/Electron/Tauri) or MCP host that injects
//            window.CV_HOST_NATIVE — full read/write/list + exec (run the
//            compiler) + tool calls. The richest mode; lights up on export.
//
// Loud, never silent: ops that need a writer throw with a message naming what
// is missing and how to activate it. The ONLY graceful path is the explicit,
// visible fall-through to `review` staging — which is a labelled mode, not a
// swallowed error.
// ============================================================================

(function () {
  'use strict';

  // ---- persistence keys (browser-local; the disk is the real source) -------
  const LS_CHANGES = 'cv:host:changes';
  const LS_HANDOFF = 'cv:host:handoff-mode'; // 'review' | 'stash' | 'download'
  const LS_AUTOAPPLY = 'cv:host:auto-apply'; // '1' when connected-writer auto-commit is on
  const LS_STASH = 'cv:host:agent-stash'; // serialized changes the exported-agent loop reads

  const listeners = new Set();
  function subscribe(fn) {
    listeners.add(fn);
    return () => listeners.delete(fn);
  }
  function notify() {
    for (const fn of listeners) {
      try {
        fn();
      } catch (e) {
        console.error('[CV_HOST] listener', e);
      }
    }
  }

  // ==========================================================================
  // RUNTIMES — the pluggable ways to reach the world. Each declares what it can
  // do (caps), whether it is available right now, and how to activate it.
  // ==========================================================================
  const RUNTIMES = new Map();
  function registerRuntime(r) {
    if (!r || !r.id) throw new Error('[CV_HOST] runtime missing id');
    RUNTIMES.set(r.id, r);
    notify();
    return r;
  }

  // The review floor — always present, no disk, stages for review.
  registerRuntime({
    id: 'review',
    label: 'Sandbox review',
    rank: 0,
    description: 'No disk access. Every change is serialized to real source and staged for a human or the agent to commit. The safe floor — always available.',
    caps: {
      read: false,
      write: false,
      list: false,
      exec: false,
      tools: false
    },
    available: () => true,
    activate: null // nothing to activate; it is the floor
  });

  // Browser File System Access API — real disk, granted per-directory.
  let FSAPI_DIR = null; // FileSystemDirectoryHandle once the user connects
  const fsapiSupported = typeof window !== 'undefined' && typeof window.showDirectoryPicker === 'function';
  registerRuntime({
    id: 'fsapi',
    label: 'Browser file access',
    rank: 1,
    description: 'Reads & writes a directory you grant with the browser File System Access API. Available when this app runs as a top-level page (exported & opened locally), not inside the editor sandbox.',
    caps: {
      read: true,
      write: true,
      list: true,
      exec: false,
      tools: false
    },
    available: () => fsapiSupported && !!FSAPI_DIR,
    supported: () => fsapiSupported,
    async activate() {
      if (!fsapiSupported) throw new Error('[CV_HOST] File System Access API not supported in this browser. Open the exported app in a Chromium-based browser, or use a native shell.');
      FSAPI_DIR = await window.showDirectoryPicker({
        mode: 'readwrite',
        id: 'conceptv-ds'
      });
      const perm = await FSAPI_DIR.requestPermission({
        mode: 'readwrite'
      });
      if (perm !== 'granted') {
        FSAPI_DIR = null;
        throw new Error('[CV_HOST] read/write permission was not granted for the chosen directory.');
      }
      await idbPut('fsapi-dir', FSAPI_DIR);
      notify();
      return FSAPI_DIR.name;
    },
    async disconnect() {
      FSAPI_DIR = null;
      await idbDel('fsapi-dir');
      notify();
    },
    // fs ops --------------------------------------------------------------
    async read(path) {
      return fsapiRead(FSAPI_DIR, path);
    },
    async list(dir) {
      return fsapiList(FSAPI_DIR, dir);
    },
    async write(path, contents) {
      return fsapiWrite(FSAPI_DIR, path, contents);
    }
  });

  // Native shell / MCP host — injected by the export environment.
  registerRuntime({
    id: 'native',
    label: 'Native / MCP host',
    rank: 2,
    description: 'A local shell (Node/Electron/Tauri) or MCP host that injects window.CV_HOST_NATIVE — full read/write/list, exec (run the compiler), and tool calls. The richest mode; activates automatically when the exported app detects the bridge.',
    caps: {
      read: true,
      write: true,
      list: true,
      exec: true,
      tools: true
    },
    available: () => !!(typeof window !== 'undefined' && window.CV_HOST_NATIVE),
    activate: null,
    // auto-detected; the host injects itself
    async read(path) {
      return reqNative('read', {
        path
      });
    },
    async list(dir) {
      return reqNative('list', {
        path: dir
      });
    },
    async write(path, contents) {
      return reqNative('write', {
        path,
        contents
      });
    },
    async exec(cmd, args) {
      return reqNative('exec', {
        cmd,
        args
      });
    },
    async tool(name, input) {
      return reqNative('tool', {
        name,
        input
      });
    }
  });
  function reqNative(op, payload) {
    const n = window.CV_HOST_NATIVE;
    if (!n || typeof n[op] !== 'function') {
      throw new Error('[CV_HOST] native host present but does not implement "' + op + '". Implement window.CV_HOST_NATIVE.' + op + '() in your local shell.');
    }
    return n[op](payload.path ?? payload.cmd ?? payload.name, payload.contents ?? payload.args ?? payload.input);
  }

  // ==========================================================================
  // RUNTIME RESOLUTION — pick the best runtime that can do what's asked.
  // ==========================================================================
  function ranked() {
    return [...RUNTIMES.values()].sort((a, b) => b.rank - a.rank);
  }
  function best(cap) {
    return ranked().find(r => r.available() && r.caps[cap]) || null;
  }
  function reader() {
    return best('read');
  }
  function writer() {
    return best('write');
  }
  function canWrite() {
    return !!writer();
  }
  function writerOrThrow() {
    const w = writer();
    if (w) return w;
    const how = ranked().filter(r => r.caps.write).map(r => `• ${r.label}: ${r.description}`).join('\n');
    throw new Error('[CV_HOST] no writable runtime is connected — running in sandbox review mode. To write to disk, activate one:\n' + how + '\nUntil then, changes stay staged for the agent / a human to commit.');
  }

  // ---- uniform op surface (routes to the best runtime; loud if impossible) --
  async function read(path) {
    const r = reader();
    if (!r) throw new Error('[CV_HOST] no runtime can read files here (sandbox). Connect a file runtime.');
    return r.read(path);
  }
  async function list(dir) {
    const r = best('list');
    if (!r) throw new Error('[CV_HOST] no runtime can list files here (sandbox). Connect a file runtime.');
    return r.list(dir);
  }
  async function write(path, contents) {
    return writerOrThrow().write(path, contents);
  }
  function capabilities() {
    const caps = {
      read: false,
      write: false,
      list: false,
      exec: false,
      tools: false
    };
    for (const r of RUNTIMES.values()) if (r.available()) for (const k in caps) caps[k] = caps[k] || !!r.caps[k];
    return caps;
  }

  // ==========================================================================
  // CV_AI BRIDGE — let CV_AI.resolveProvider delegate host/model runtime kinds
  // here, so the AI catalogue can name providers we own (a native model
  // endpoint, an MCP tool) without CV_AI knowing how the host reaches them.
  // Loud: returns a bound runtime or throws naming how to activate it.
  // ==========================================================================
  function resolveProviderRuntime(p) {
    const kind = p && p.runtime && p.runtime.kind;
    // host filesystem provider — used by repo.* capabilities
    if (kind === 'host-fs') {
      return {
        ...p,
        read,
        list,
        write,
        capabilities,
        async commit(change) {
          return commit(change);
        }
      };
    }
    // a model endpoint the native/MCP host exposes (other providers / local models)
    if (kind === 'native-model' || kind === 'mcp-model') {
      const n = typeof window !== 'undefined' && window.CV_HOST_NATIVE;
      if (!n || typeof n.complete !== 'function') {
        throw new Error('[CV_HOST] provider "' + p.id + '" (' + kind + ') needs a native/MCP host that implements window.CV_HOST_NATIVE.complete(). It activates when you export this app and run it with the local bridge. (In the sandbox, use the built-in "claude" provider.)');
      }
      return {
        ...p,
        async complete(prompt, opts) {
          return n.complete(p.runtime.model || p.id, prompt, opts);
        }
      };
    }
    return null; // not ours — let CV_AI throw its own unknown-kind error
  }

  // ==========================================================================
  // HANDOFF SETTINGS — how a committed change is handed off when there is no
  // connected writer (sandbox). Persisted. NEVER auto-downloads by default.
  // ==========================================================================
  const HANDOFF_MODES = {
    review: {
      label: 'Review in panel',
      desc: 'Stage the change in the Bridge panel for you to review, copy, and apply. Nothing leaves the page.'
    },
    stash: {
      label: 'Stash for agent',
      desc: 'Also write the serialized change to localStorage so Claude (the agent) can read it back next turn and commit it to disk for you.'
    },
    download: {
      label: 'Download file',
      desc: 'Also download the patch file. Off by default — opt in here.'
    }
  };
  function handoffMode() {
    try {
      return localStorage.getItem(LS_HANDOFF) || 'review';
    } catch {
      return 'review';
    }
  }
  function setHandoffMode(m) {
    if (!HANDOFF_MODES[m]) throw new Error('[CV_HOST] unknown handoff mode "' + m + '"');
    try {
      localStorage.setItem(LS_HANDOFF, m);
    } catch {}
    notify();
  }
  function autoApply() {
    try {
      return localStorage.getItem(LS_AUTOAPPLY) === '1';
    } catch {
      return false;
    }
  }
  function setAutoApply(on) {
    try {
      localStorage.setItem(LS_AUTOAPPLY, on ? '1' : '0');
    } catch {}
    notify();
  }

  // ==========================================================================
  // SERIALIZERS — turn a registry mutation into EXACT source text for the one
  // file it belongs in. Registered by host-serializer.js (kept separate so the
  // file-format knowledge lives next to nothing else). Single source: one
  // serializer per change kind; the change kind names its home file + strategy.
  // ==========================================================================
  const SERIALIZERS = new Map();
  function registerSerializer(s) {
    if (!s || !s.kind) throw new Error('[CV_HOST] serializer missing kind');
    if (typeof s.render !== 'function') throw new Error('[CV_HOST] serializer "' + s.kind + '" missing render()');
    SERIALIZERS.set(s.kind, s);
    return s;
  }
  function serialize(change) {
    if (!change || !change.kind) throw new Error('[CV_HOST] change missing kind');
    const s = SERIALIZERS.get(change.kind);
    if (!s) throw new Error('[CV_HOST] no serializer for kind "' + change.kind + '" (registered: ' + [...SERIALIZERS.keys()].join(', ') + ')');
    const source = s.render(change.payload, change);
    return {
      kind: change.kind,
      file: typeof s.target === 'function' ? s.target(change.payload, change) : s.target,
      strategy: s.strategy || 'append-block',
      anchor: typeof s.anchor === 'function' ? s.anchor(change.payload, change) : s.anchor || null,
      describe: s.describe || '',
      source
    };
  }

  // ==========================================================================
  // CHANGES — the proposed-change store. Every commit lands here (reviewable),
  // persisted to localStorage. Statuses: staged → applied | rejected.
  // ==========================================================================
  function loadChanges() {
    try {
      return JSON.parse(localStorage.getItem(LS_CHANGES) || '[]');
    } catch {
      return [];
    }
  }
  function saveChanges(arr) {
    try {
      localStorage.setItem(LS_CHANGES, JSON.stringify(arr));
    } catch {}
    notify();
  }
  let CHANGES = loadChanges();
  const changes = {
    list() {
      return CHANGES.slice();
    },
    pending() {
      return CHANGES.filter(c => c.status === 'staged');
    },
    get(id) {
      return CHANGES.find(c => c.id === id) || null;
    },
    propose(change) {
      const id = change.id || 'chg_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
      const serialized = change.serialized || serialize(change);
      const entry = {
        id,
        kind: change.kind,
        title: change.title || change.kind,
        rationale: change.rationale || '',
        provenance: change.provenance || 'vi',
        payload: safeClone(change.payload),
        serialized,
        status: 'staged',
        createdAt: Date.now()
      };
      CHANGES = [entry, ...CHANGES];
      saveChanges(CHANGES);
      return entry;
    },
    async apply(id) {
      const c = changes.get(id);
      if (!c) throw new Error('[CV_HOST] no staged change "' + id + '"');
      await applySerialized(c.serialized);
      c.status = 'applied';
      c.appliedAt = Date.now();
      CHANGES = CHANGES.map(x => x.id === id ? c : x);
      saveChanges(CHANGES);
      return c;
    },
    reject(id) {
      const c = changes.get(id);
      if (c) {
        c.status = 'rejected';
        CHANGES = CHANGES.map(x => x.id === id ? c : x);
        saveChanges(CHANGES);
      }
    },
    remove(id) {
      CHANGES = CHANGES.filter(c => c.id !== id);
      saveChanges(CHANGES);
    },
    clear() {
      CHANGES = [];
      saveChanges(CHANGES);
    },
    subscribe
  };
  function safeClone(v) {
    try {
      return JSON.parse(JSON.stringify(v, fnReplacer));
    } catch {
      return v;
    }
  }
  function fnReplacer(_k, val) {
    return typeof val === 'function' ? '\u0192' + val.toString() : val;
  }

  // ==========================================================================
  // APPLY — write a serialized change to disk via the connected writer, using
  // its strategy. Loud if no writer. This is the real edit; commit() only
  // stages (review-first by design).
  // ==========================================================================
  async function applySerialized(s) {
    const w = writerOrThrow();
    if (s.strategy === 'new-file') {
      await w.write(s.file, s.source);
      return {
        file: s.file,
        wrote: 'new'
      };
    }
    if (s.strategy === 'css-token') {
      const cur = await read(s.file);
      const next = insertInSelector(cur, s.anchor || ':root', s.source);
      await w.write(s.file, next);
      return {
        file: s.file,
        wrote: 'css-token'
      };
    }
    // default: append-block — insert before an anchor sentinel, else at EOF
    const cur = await read(s.file);
    let next;
    if (s.anchor && cur.includes(s.anchor)) next = cur.replace(s.anchor, s.source + '\n\n  ' + s.anchor);else next = cur.replace(/\s*$/, '\n\n' + s.source + '\n');
    await w.write(s.file, next);
    return {
      file: s.file,
      wrote: 'append'
    };
  }
  function insertInSelector(css, selector, line) {
    const re = new RegExp('(' + selector.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\s*\\{)');
    if (re.test(css)) return css.replace(re, '$1\n  ' + line);
    return css.replace(/\s*$/, '\n\n' + selector + ' {\n  ' + line + '\n}\n');
  }

  // ==========================================================================
  // commit — THE call Vi makes. Serialize the change, stage it (always — review
  // first), then per environment + settings: if a writer is connected AND
  // auto-apply is on, write it now; else hand off per the handoff-mode setting.
  // Returns a clear, explicit status. Never silently degrades.
  // ==========================================================================
  async function commit(change) {
    const entry = changes.propose(change);
    const mode = handoffMode();
    let result = {
      id: entry.id,
      status: 'staged',
      file: entry.serialized.file,
      mode
    };
    if (canWrite() && autoApply()) {
      await changes.apply(entry.id);
      result.status = 'applied';
      result.writer = writer().id;
      return result;
    }
    if (mode === 'stash') {
      stash(entry);
      result.stashed = true;
    }
    if (mode === 'download') {
      download(entry);
      result.downloaded = true;
    }
    return result;
  }

  // ---- handoff side-effects -------------------------------------------------
  function stash(entry) {
    let arr;
    try {
      arr = JSON.parse(localStorage.getItem(LS_STASH) || '[]');
    } catch {
      arr = [];
    }
    arr.unshift({
      id: entry.id,
      file: entry.serialized.file,
      strategy: entry.serialized.strategy,
      anchor: entry.serialized.anchor,
      source: entry.serialized.source,
      title: entry.title,
      at: Date.now()
    });
    try {
      localStorage.setItem(LS_STASH, JSON.stringify(arr));
    } catch {}
  }
  function readStash() {
    try {
      return JSON.parse(localStorage.getItem(LS_STASH) || '[]');
    } catch {
      return [];
    }
  }
  function clearStash() {
    try {
      localStorage.removeItem(LS_STASH);
    } catch {}
  }
  function download(entry) {
    const blob = new Blob([entry.serialized.source], {
      type: 'text/plain'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = entry.serialized.file.split('/').pop() + '.patch.txt';
    a.click();
    URL.revokeObjectURL(url);
  }

  // ==========================================================================
  // describe — the SELF-DOCUMENTING projection. The Bridge panel and the AI
  // card render this; it is the single source of "what this environment is and
  // what Vi can do in it." No status string is hand-written elsewhere.
  // ==========================================================================
  function describe() {
    const caps = capabilities();
    const w = writer();
    return {
      mode: w ? w.id : 'review',
      modeLabel: w ? w.label : 'Sandbox review',
      capabilities: caps,
      canWrite: !!w,
      runtimes: ranked().map(r => ({
        id: r.id,
        label: r.label,
        rank: r.rank,
        description: r.description,
        caps: r.caps,
        available: r.available(),
        supported: r.supported ? r.supported() : true,
        canActivate: !!r.activate
      })),
      serializers: [...SERIALIZERS.values()].map(s => ({
        kind: s.kind,
        target: typeof s.target === 'function' ? '(computed)' : s.target,
        strategy: s.strategy || 'append-block',
        describe: s.describe || ''
      })),
      handoff: {
        mode: handoffMode(),
        modes: HANDOFF_MODES,
        autoApply: autoApply()
      },
      changes: {
        staged: changes.pending().length,
        total: CHANGES.length
      },
      stash: readStash().length
    };
  }

  // ==========================================================================
  // tiny IndexedDB helper — persist the granted directory handle across reloads
  // ==========================================================================
  function idb() {
    return new Promise((res, rej) => {
      const r = indexedDB.open('cv-host', 1);
      r.onupgradeneeded = () => r.result.createObjectStore('kv');
      r.onsuccess = () => res(r.result);
      r.onerror = () => rej(r.error);
    });
  }
  async function idbPut(k, v) {
    try {
      const db = await idb();
      await new Promise((res, rej) => {
        const t = db.transaction('kv', 'readwrite');
        t.objectStore('kv').put(v, k);
        t.oncomplete = res;
        t.onerror = () => rej(t.error);
      });
    } catch {}
  }
  async function idbGet(k) {
    try {
      const db = await idb();
      return await new Promise(res => {
        const t = db.transaction('kv', 'readonly');
        const rq = t.objectStore('kv').get(k);
        rq.onsuccess = () => res(rq.result);
        rq.onerror = () => res(null);
      });
    } catch {
      return null;
    }
  }
  async function idbDel(k) {
    try {
      const db = await idb();
      await new Promise(res => {
        const t = db.transaction('kv', 'readwrite');
        t.objectStore('kv').delete(k);
        t.oncomplete = res;
        t.onerror = res;
      });
    } catch {}
  }

  // try to restore a previously-granted fsapi directory (needs a gesture to
  // re-verify on some browsers; we keep the handle and surface "reconnect")
  (async () => {
    if (!fsapiSupported) return;
    const h = await idbGet('fsapi-dir');
    if (h && typeof h.queryPermission === 'function') {
      const p = await h.queryPermission({
        mode: 'readwrite'
      });
      if (p === 'granted') {
        FSAPI_DIR = h;
        notify();
      } else {
        window.__cvFsapiPending = h;
      } // Bridge panel offers "reconnect"
    }
  })();

  // ---- fsapi path helpers ---------------------------------------------------
  async function dirFor(root, path, create) {
    const parts = path.split('/').filter(Boolean);
    const fileName = parts.pop();
    let dir = root;
    for (const part of parts) dir = await dir.getDirectoryHandle(part, {
      create: !!create
    });
    return {
      dir,
      fileName
    };
  }
  async function fsapiRead(root, path) {
    if (!root) throw new Error('[CV_HOST] no directory connected');
    const {
      dir,
      fileName
    } = await dirFor(root, path, false);
    const fh = await dir.getFileHandle(fileName);
    return (await fh.getFile()).text();
  }
  async function fsapiWrite(root, path, contents) {
    if (!root) throw new Error('[CV_HOST] no directory connected');
    const {
      dir,
      fileName
    } = await dirFor(root, path, true);
    const fh = await dir.getFileHandle(fileName, {
      create: true
    });
    const ws = await fh.createWritable();
    await ws.write(contents);
    await ws.close();
    return {
      file: path
    };
  }
  async function fsapiList(root, path) {
    if (!root) throw new Error('[CV_HOST] no directory connected');
    let dir = root;
    for (const part of (path || '').split('/').filter(Boolean)) dir = await dir.getDirectoryHandle(part);
    const out = [];
    for await (const [name, handle] of dir.entries()) out.push({
      name,
      kind: handle.kind
    });
    return out;
  }
  async function reconnectFsapi() {
    const h = window.__cvFsapiPending;
    if (!h) throw new Error('[CV_HOST] nothing to reconnect');
    const p = await h.requestPermission({
      mode: 'readwrite'
    });
    if (p !== 'granted') throw new Error('[CV_HOST] permission denied');
    FSAPI_DIR = h;
    delete window.__cvFsapiPending;
    notify();
    return h.name;
  }

  // ==========================================================================
  window.CV_HOST = {
    // runtimes
    runtimes: RUNTIMES,
    registerRuntime,
    ranked,
    best,
    reader,
    writer,
    canWrite,
    reconnectFsapi,
    // ops
    read,
    list,
    write,
    capabilities,
    // CV_AI bridge
    resolveProviderRuntime,
    // serializers
    registerSerializer,
    serialize,
    _serializers: SERIALIZERS,
    // changes
    changes,
    applySerialized,
    // the one call
    commit,
    // settings
    handoffMode,
    setHandoffMode,
    HANDOFF_MODES,
    autoApply,
    setAutoApply,
    // agent stash loop
    readStash,
    clearStash,
    // self-documentation + reactivity
    describe,
    subscribe,
    notify
  };
  console.info('[CV_HOST] environment ready —', describe().modeLabel);
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "app/ai/host-runtime.js", error: String((e && e.message) || e) }); }

// app/ai/host-serializer.js
try { (() => {
// app/ai/host-serializer.js
// ============================================================================
// Serializers + host capabilities.
//
// Two jobs, both single-source:
//   1. SERIALIZERS — one per change kind. Each knows the ONE file a change of
//      that kind lives in, and renders the change payload as EXACT source text
//      ready to drop into that file. This is what lets Vi *author real diffs*
//      rather than describe vague suggestions: it produces the literal
//      `CV_AI.register({...})` / token line / @dsCard file a human would write.
//   2. HOST CAPABILITIES — repo.read / repo.list / repo.write / ds.propose /
//      ds.commit registered into CV_AI, so "what Vi can do" includes touching
//      the repository, routed through the same CV_AI.execute() path as every
//      other move. They run on the 'host-fs' provider, which CV_HOST binds.
//
// Loud, never silent: a missing serializer throws; a write with no connected
// runtime throws (or stages, explicitly). No format knowledge is duplicated —
// each serializer is the single home for "how an X is written to source."
// ============================================================================

(function () {
  'use strict';

  const HOST = window.CV_HOST;
  const AI = window.CV_AI;
  if (!HOST) throw new Error('[host-serializer] CV_HOST not loaded — load app/ai/host-runtime.js first');
  if (!AI) throw new Error('[host-serializer] CV_AI not loaded — load app/ai/ai-registry.js first');

  // ---------------------------------------------------------------------------
  // JS value → readable source. Handles functions (via toString, so Vi can
  // author a capability with a real run()/build()), nested objects, arrays.
  // ---------------------------------------------------------------------------
  function js(val, indent) {
    indent = indent || '  ';
    if (val === null) return 'null';
    if (typeof val === 'function') return reindent(val.toString(), indent);
    if (typeof val === 'string') {
      // a function smuggled through JSON as "ƒ…" (CV_HOST.safeClone) → revive
      if (val[0] === '\u0192') return reindent(val.slice(1), indent);
      return JSON.stringify(val);
    }
    if (typeof val === 'number' || typeof val === 'boolean') return String(val);
    if (Array.isArray(val)) {
      if (!val.length) return '[]';
      const simple = val.every(v => typeof v === 'string' || typeof v === 'number' || typeof v === 'boolean');
      if (simple) return '[' + val.map(v => js(v, indent)).join(', ') + ']';
      return '[\n' + val.map(v => indent + '  ' + js(v, indent + '  ')).join(',\n') + '\n' + indent + ']';
    }
    if (typeof val === 'object') {
      const keys = Object.keys(val).filter(k => val[k] !== undefined);
      if (!keys.length) return '{}';
      return '{\n' + keys.map(k => indent + '  ' + keyName(k) + ': ' + js(val[k], indent + '  ')).join(',\n') + '\n' + indent + '}';
    }
    return JSON.stringify(val);
  }
  function keyName(k) {
    return /^[A-Za-z_$][\w$]*$/.test(k) ? k : JSON.stringify(k);
  }
  function reindent(src, indent) {
    const lines = src.replace(/\r/g, '').split('\n');
    if (lines.length === 1) return src;
    // re-base the function body indentation under the current indent
    const body = lines.slice(1);
    const min = Math.min(...body.filter(l => l.trim()).map(l => l.match(/^\s*/)[0].length));
    return lines[0] + '\n' + body.map(l => l.trim() ? indent + l.slice(min) : '').join('\n');
  }

  // ---------------------------------------------------------------------------
  // SERIALIZERS — each is the single home for one change kind's source format.
  // The `anchor` is a sentinel comment new entries insert before, so additions
  // accrete in a predictable spot. (host-runtime appends at EOF if absent.)
  // ---------------------------------------------------------------------------

  // A CV_AI registry entry (capability / behaviour / skill / provider / context).
  // Lives in ai-seed.js — the data home for built-ins.
  HOST.registerSerializer({
    kind: 'ai.entry',
    target: 'app/ai/ai-seed.js',
    strategy: 'append-block',
    anchor: '// CV_HOST:ai-entries',
    describe: 'A CV_AI registry entry (provider/behaviour/skill/capability/context). Registered into the one AI catalogue; appears in every surface that projects it.',
    render: p => 'AI.register(' + js(p) + ', { silent: true });'
  });

  // A type/component/atom/archetype registered into CV_REGISTRY.
  HOST.registerSerializer({
    kind: 'type',
    target: 'app/registry/types-seed.js',
    strategy: 'append-block',
    anchor: '// CV_HOST:types',
    describe: 'A Type (token/atom/block/system/surface/doc/template) registered into CV_REGISTRY. Renders through the one engine under the axis-dials.',
    render: p => 'CV_REGISTRY.register(' + js(p) + ');'
  });

  // A design token — a new L0 primitive or L1 role. Lives in colors_and_type.css.
  HOST.registerSerializer({
    kind: 'css.token',
    target: p => p.file || 'colors_and_type.css',
    strategy: 'css-token',
    anchor: ':root',
    describe: 'A design token (CSS custom property). Added at its lowest layer; every consumer that var()s it updates by construction.',
    render: p => `--${slug(p.name)}: ${p.value};` + (p.role ? `   /* ${p.role} */` : '')
  });

  // A Design System tab card — a tagged .html specimen. New file.
  HOST.registerSerializer({
    kind: 'card',
    target: p => `preview/${slug(p.name)}.html`,
    strategy: 'new-file',
    describe: 'A Design System tab card — a tagged HTML specimen. Appears in the tab under its group, grouped automatically.',
    render: p => [`<!-- @dsCard group="${p.group || 'Brand'}" name="${p.name}" subtitle="${p.subtitle || ''}" viewport="${p.viewport || '700x280'}" -->`, '<!DOCTYPE html>', '<html><head><meta charset="utf-8">', '<link rel="stylesheet" href="_card.css">', '</head><body>', p.body || '<div class="card-pad"><!-- specimen --></div>', '</body></html>', ''].join('\n')
  });

  // A raw file write — escape hatch for anything not yet typed. New file.
  HOST.registerSerializer({
    kind: 'file',
    target: p => p.path,
    strategy: 'new-file',
    describe: 'A whole-file write (escape hatch). Prefer a typed kind so the change lives in its proper home.',
    render: p => p.contents
  });
  function slug(s) {
    return String(s || '').toLowerCase().replace(/[^a-z0-9-]+/g, '-').replace(/^-|-$/g, '');
  }

  // ---------------------------------------------------------------------------
  // PROVIDER — the host filesystem provider CV_AI capabilities run on. Bound by
  // CV_HOST.resolveProviderRuntime (loud if no writer when a write is attempted).
  // ---------------------------------------------------------------------------
  AI.register({
    id: 'host-fs',
    name: 'Host filesystem',
    layer: 'provider',
    family: 'host',
    description: 'The environment\u2019s file surface — sandbox review by default, real disk when a browser/native runtime is connected. Resolved by CV_HOST.',
    runtime: {
      kind: 'host-fs'
    },
    modality: ['fs'],
    caps: {
      read: true,
      write: true
    },
    icon: 'files-stack',
    provenance: 'built-in',
    tags: ['host', 'fs']
  }, {
    silent: true
  });

  // Additional MODEL providers — declared so the catalogue knows other models
  // CAN be used; they resolve to live runtimes only when the exported app
  // connects a native/MCP host. In the sandbox, resolving them throws loudly
  // (pointing the user at the built-in claude provider).
  AI.register({
    id: 'native-model',
    name: 'Local / other model',
    layer: 'provider',
    family: 'text',
    description: 'A model endpoint exposed by your local shell or MCP host (Ollama, an OpenAI-compatible server, another Anthropic key). Activates when the exported app detects window.CV_HOST_NATIVE.complete().',
    runtime: {
      kind: 'native-model'
    },
    modality: ['text'],
    caps: {
      stream: false,
      json: true
    },
    icon: 'sparkles',
    provenance: 'built-in',
    tags: ['text', 'export-only']
  }, {
    silent: true
  });
  AI.register({
    id: 'mcp-tools',
    name: 'MCP tools',
    layer: 'provider',
    family: 'host',
    description: 'Tool calls routed through a connected MCP host (filesystem, git, search, your own servers). Activates on export with an MCP bridge.',
    runtime: {
      kind: 'mcp-model'
    },
    modality: ['tool'],
    caps: {},
    icon: 'network',
    provenance: 'built-in',
    tags: ['tools', 'export-only']
  }, {
    silent: true
  });

  // ---------------------------------------------------------------------------
  // CAPABILITIES — "what Vi can do" now includes touching the repo. Routed
  // through CV_AI.execute() like every other move, so they appear in the
  // catalogue, the inspector, and any surface that projects capabilities.
  // ---------------------------------------------------------------------------
  AI.register({
    id: 'repo.read',
    name: 'Read a file',
    layer: 'capability',
    family: 'repo',
    description: 'Read a file from the connected directory (loud if no reader).',
    surfaces: ['*'],
    provider: 'host-fs',
    params: {
      path: ''
    },
    icon: 'document',
    provenance: 'built-in',
    run: a => a.provider.read(a.params.path)
  }, {
    silent: true
  });
  AI.register({
    id: 'repo.list',
    name: 'List a directory',
    layer: 'capability',
    family: 'repo',
    description: 'List entries of a directory (loud if no reader).',
    surfaces: ['*'],
    provider: 'host-fs',
    params: {
      path: ''
    },
    icon: 'files-stack',
    provenance: 'built-in',
    run: a => a.provider.list(a.params.path)
  }, {
    silent: true
  });

  // The keystone: propose a single-sourced change. Vi calls this with a change
  // descriptor; it serializes to real source and stages it (review-first), or
  // writes it when a writer is connected + auto-apply is on. ALWAYS explicit.
  AI.register({
    id: 'ds.propose',
    name: 'Propose a change',
    layer: 'capability',
    family: 'repo',
    description: 'Serialize a registry mutation (a new token, capability, type, or card) into exact source for its one home file, and commit it through CV_HOST — staged for review in the sandbox, written to disk when connected.',
    surfaces: ['*'],
    provider: 'host-fs',
    params: {
      kind: '',
      title: '',
      rationale: '',
      payload: null
    },
    icon: 'wand',
    provenance: 'built-in',
    run: a => a.provider.commit({
      kind: a.params.kind,
      title: a.params.title,
      rationale: a.params.rationale,
      payload: a.params.payload,
      provenance: 'vi'
    })
  }, {
    silent: true
  });

  // Apply an already-staged change (the panel's Apply button uses this path too).
  AI.register({
    id: 'ds.apply',
    name: 'Apply a staged change',
    layer: 'capability',
    family: 'repo',
    description: 'Write a previously staged change to disk via the connected writer. Loud if no writer is connected.',
    surfaces: ['*'],
    provider: 'host-fs',
    params: {
      id: ''
    },
    icon: 'check-square',
    provenance: 'built-in',
    run: a => window.CV_HOST.changes.apply(a.params.id)
  }, {
    silent: true
  });
  console.info('[host-serializer] serializers + host capabilities registered');
})();
})(); } catch (e) { __ds_ns.__errors.push({ path: "app/ai/host-serializer.js", error: String((e && e.message) || e) }); }

// app/canvases/AIStudio.jsx
try { (() => {
// canvases/AIStudio.jsx — the full GPT Image 2-powered AI Studio.
//
// Designed against the ConceptV pitch deck: paper canvas, soft-cream
// panels, gold ▶ bullets, dashed-gold rules, big-gold-numbers stats.
//
// Five modes share one chrome:
//   • Generate — text → image
//   • Edit     — source image + instruction
//   • Compose  — up to 16 references with roles
//   • Mask     — brushed inpainting
//   • Chat     — multi-turn Responses API
//
// Layout: three resizable columns — Presets | Stage | Results.
// Each panel is a single soft-cream wash. No nested borders.

const {
  useState: useState_as,
  useEffect: useEffect_as,
  useMemo: useMemo_as,
  useRef: useRef_as
} = React;
const MODES = [{
  id: 'generate',
  label: 'Generate',
  icon: 'atom',
  desc: 'Text → image. Full GPT Image 2 control surface.'
}, {
  id: 'edit',
  label: 'Edit',
  icon: 'edit',
  desc: 'Send a source image with a change instruction.'
}, {
  id: 'compose',
  label: 'Compose',
  icon: 'image-stack',
  desc: 'Combine up to 16 reference images with roles.'
}, {
  id: 'mask',
  label: 'Mask',
  icon: 'browser-pen',
  desc: 'Brush a region to inpaint. Alpha mask powered.'
}, {
  id: 'chat',
  label: 'Chat',
  icon: 'chat-tree',
  desc: 'Multi-turn editing via the Responses API.'
}];
const ROLE_OPTIONS = [{
  id: 'base',
  label: 'Base',
  desc: 'Image to start from.'
}, {
  id: 'reference',
  label: 'Reference',
  desc: 'General context.'
}, {
  id: 'style',
  label: 'Style',
  desc: 'Match this look.'
}, {
  id: 'object',
  label: 'Object',
  desc: 'Include this object.'
}, {
  id: 'identity',
  label: 'Identity',
  desc: 'Match this person.'
}];
function AIStudio({
  onNav
}) {
  const projects = window.cvImageStore.listProjects();
  const cached = window.cvOpenAI.getCachedModels?.()?.models || [];
  const [models, setModels] = useState_as(cached);
  const [presets, setPresets] = useState_as(window.cvAIPresets.listPresets());
  const [pipelines, setPipelines] = useState_as(window.cvAIPresets.listPipelines());
  const settings = window.cvOpenAI.getSettings();
  const [mode, setMode] = useState_as('generate');
  const [modelId, setModelId] = useState_as(settings.imageModel);
  const caps = window.cvOpenAI.getModelCapabilities(modelId);
  const [prompt, setPrompt] = useState_as(presets[0]?.body || '');
  const [brandEnrich, setBrand] = useState_as(true);
  const [size, setSize] = useState_as(caps.sizes[1] || caps.sizes[0] || '1024x1024');
  const [customSize, setCustomSize] = useState_as({
    w: 1536,
    h: 1024
  });
  const [useCustomSize, setUseCustomSize] = useState_as(false);
  const [quality, setQuality] = useState_as(caps.qualities[0] || '');
  const [format, setFormat] = useState_as(caps.outputFormats?.[0] || 'png');
  const [compression, setCompression] = useState_as(90);
  const [background, setBackground] = useState_as('auto');
  const [moderation, setModeration] = useState_as('auto');
  const [n, setN] = useState_as(1);
  const [stream, setStream] = useState_as(caps.supports.stream);
  const [partialImages, setPartialImages] = useState_as(caps.supports.partialImages || 0);
  const [target, setTarget] = useState_as({
    scope: 'system',
    pid: projects[0]?.id
  });
  const [results, setResults] = useState_as([]);
  const [partials, setPartials] = useState_as([]);
  const [busy, setBusy] = useState_as(false);
  const [err, setErr] = useState_as(null);
  const [activePreset, setActivePreset] = useState_as(presets[0]?.id);

  // Edit / compose / mask state
  const [editSourceUrl, setEditSourceUrl] = useState_as(null);
  const [composeImages, setComposeImages] = useState_as([]);
  const [maskSourceUrl, setMaskSourceUrl] = useState_as(null);
  const [maskBlob, setMaskBlob] = useState_as(null);

  // Chat state
  const [chatTurns, setChatTurns] = useState_as([]);
  const [chatInput, setChatInput] = useState_as('');
  const [chatBusy, setChatBusy] = useState_as(false);
  const [chatRespId, setChatRespId] = useState_as(null);

  // Pipeline runner
  const [runningPipelineId, setRunningPipelineId] = useState_as(null);
  const [pipelineLog, setPipelineLog] = useState_as([]);

  // Save preset modal
  const [savePresetOpen, setSavePresetOpen] = useState_as(false);
  const [presetName, setPresetName] = useState_as('');

  // Parameter drawer collapse (advanced controls)
  const [showAdvanced, setShowAdvanced] = useState_as(false);

  // --- Subscriptions
  useEffect_as(() => window.cvOpenAI.subscribeModels?.(p => setModels(p.models || [])), []);
  useEffect_as(() => window.cvAIPresets.subscribe(d => {
    setPresets(d.presets);
    setPipelines(d.pipelines);
  }), []);

  // Coerce options when model changes
  useEffect_as(() => {
    const c = window.cvOpenAI.getModelCapabilities(modelId);
    if (!c.sizes.includes(size)) setSize(c.sizes[0]);
    if (c.qualities.length && !c.qualities.includes(quality)) setQuality(c.qualities[0]);
    if (!c.qualities.length) setQuality('');
    if (c.outputFormats?.length && !c.outputFormats.includes(format)) setFormat(c.outputFormats[0]);
    if (c.backgrounds?.length && !c.backgrounds.includes(background)) setBackground(c.backgrounds[0]);
    if (!c.supports.stream) setStream(false);
    if (!c.supports.customSize) setUseCustomSize(false);
    if (n > (c.supports.maxN || 1)) setN(c.supports.maxN || 1);
  }, [modelId]);

  // --- Helpers
  function applyPreset(p) {
    setActivePreset(p.id);
    setPrompt(p.body);
    if (p.model) setModelId(p.model);
    if (p.size) setSize(p.size);
    if (p.quality) setQuality(p.quality);
    if (p.output_format) setFormat(p.output_format);
    if (p.output_compression != null) setCompression(p.output_compression);
    if (p.background) setBackground(p.background);
    if (p.moderation) setModeration(p.moderation);
    if (p.n) setN(p.n);
  }
  function buildOptions() {
    const opts = {
      prompt,
      model: modelId,
      size: useCustomSize && caps.supports.customSize ? `${customSize.w}x${customSize.h}` : size,
      n,
      brandEnrich
    };
    if (caps.qualities.length) opts.quality = quality || caps.qualities[0];
    if (caps.outputFormats?.length) opts.output_format = format;
    if (format === 'jpeg' || format === 'webp') opts.output_compression = compression;
    if (caps.backgrounds?.length) opts.background = background;
    if (caps.moderations?.length) opts.moderation = moderation;
    if (caps.supports.stream && stream) {
      opts.stream = true;
      opts.partial_images = partialImages;
    }
    return opts;
  }
  function onPartial({
    src,
    index
  }) {
    setPartials(prev => {
      const next = [...prev];
      next[index] = src;
      return next;
    });
  }
  async function urlToBlob(url) {
    return await (await fetch(url)).blob();
  }
  async function runGenerate() {
    setErr(null);
    setBusy(true);
    setResults([]);
    setPartials([]);
    try {
      const opts = buildOptions();
      if (stream && caps.supports.stream) opts.onPartial = onPartial;
      const out = await window.CV_AI.resolveProvider('openai-image').generateImage(opts);
      setResults(out);
      for (const im of out) {
        try {
          await window.cvImageStore.addFromSrc('ai', null, im.src, {
            name: prompt.slice(0, 60),
            prompt,
            source: 'ai'
          });
        } catch {}
      }
    } catch (e) {
      setErr(e.message || 'Generation failed.');
    } finally {
      setBusy(false);
    }
  }
  async function runEdit() {
    if (!editSourceUrl) {
      setErr('Add a source image first.');
      return;
    }
    setErr(null);
    setBusy(true);
    setResults([]);
    setPartials([]);
    try {
      const blob = await urlToBlob(editSourceUrl);
      const opts = {
        ...buildOptions(),
        images: [blob]
      };
      if (stream && caps.supports.stream) opts.onPartial = onPartial;
      const out = await window.CV_AI.resolveProvider('openai-image').editImage(opts);
      setResults(out);
      for (const im of out) try {
        await window.cvImageStore.addFromSrc('ai', null, im.src, {
          name: prompt.slice(0, 60),
          prompt,
          source: 'ai'
        });
      } catch {}
    } catch (e) {
      setErr(e.message || 'Edit failed.');
    } finally {
      setBusy(false);
    }
  }
  async function runCompose() {
    if (composeImages.length === 0) {
      setErr('Add at least one reference image.');
      return;
    }
    if (composeImages.length > (caps.maxRefImages || 0)) {
      setErr(`Up to ${caps.maxRefImages} reference images.`);
      return;
    }
    setErr(null);
    setBusy(true);
    setResults([]);
    setPartials([]);
    try {
      const blobs = await Promise.all(composeImages.map(i => urlToBlob(i.src)));
      const rolesStr = composeImages.map((i, idx) => `Image ${idx + 1}: ${i.role || 'reference'} (${i.name || 'unnamed'})`).join('\n');
      const composedPrompt = `${prompt}\n\nReference images:\n${rolesStr}`;
      const opts = {
        ...buildOptions(),
        prompt: composedPrompt,
        images: blobs
      };
      if (stream && caps.supports.stream) opts.onPartial = onPartial;
      const out = await window.CV_AI.resolveProvider('openai-image').editImage(opts);
      setResults(out);
      for (const im of out) try {
        await window.cvImageStore.addFromSrc('ai', null, im.src, {
          name: prompt.slice(0, 60),
          prompt: composedPrompt,
          source: 'ai'
        });
      } catch {}
    } catch (e) {
      setErr(e.message || 'Compose failed.');
    } finally {
      setBusy(false);
    }
  }
  async function runMask() {
    if (!maskSourceUrl) {
      setErr('Pick a source image first.');
      return;
    }
    if (!maskBlob) {
      setErr('Brush a mask area first.');
      return;
    }
    setErr(null);
    setBusy(true);
    setResults([]);
    setPartials([]);
    try {
      const blob = await urlToBlob(maskSourceUrl);
      const opts = {
        ...buildOptions(),
        images: [blob],
        mask: maskBlob
      };
      if (stream && caps.supports.stream) opts.onPartial = onPartial;
      const out = await window.CV_AI.resolveProvider('openai-image').editImage(opts);
      setResults(out);
      for (const im of out) try {
        await window.cvImageStore.addFromSrc('ai', null, im.src, {
          name: prompt.slice(0, 60),
          prompt,
          source: 'ai'
        });
      } catch {}
    } catch (e) {
      setErr(e.message || 'Mask edit failed.');
    } finally {
      setBusy(false);
    }
  }
  async function sendChat() {
    const text = chatInput.trim();
    if (!text) return;
    setChatTurns(t => [...t, {
      role: 'user',
      content: text
    }]);
    setChatInput('');
    setChatBusy(true);
    setErr(null);
    try {
      const opts = {
        input: text,
        action: 'auto',
        size: useCustomSize && caps.supports.customSize ? `${customSize.w}x${customSize.h}` : size,
        quality,
        format,
        background,
        previous_response_id: chatRespId
      };
      const out = await window.CV_AI.resolveProvider('openai-image').responsesImage(opts);
      setChatRespId(out.responseId);
      setChatTurns(t => [...t, {
        role: 'vi',
        content: out.revisedPrompt || 'Generated',
        images: out.images,
        revisedPrompt: out.revisedPrompt
      }]);
      for (const im of out.images) try {
        await window.cvImageStore.addFromSrc('ai', null, im.src, {
          name: text.slice(0, 60),
          prompt: text,
          source: 'ai'
        });
      } catch {}
    } catch (e) {
      setErr(e.message || 'Chat-edit failed.');
      setChatTurns(t => [...t, {
        role: 'vi',
        content: `⚠ ${e.message || 'Failed'}`
      }]);
    } finally {
      setChatBusy(false);
    }
  }
  async function runPipeline(p) {
    setRunningPipelineId(p.id);
    setPipelineLog([]);
    setErr(null);
    let lastImage = null;
    try {
      for (let i = 0; i < p.steps.length; i++) {
        const step = p.steps[i];
        setPipelineLog(l => [...l, {
          i,
          label: step.label || step.kind,
          status: 'running'
        }]);
        if (step.kind === 'generate') {
          const preset = step.presetId && window.cvAIPresets.findPreset(step.presetId);
          const seed = preset ? window.cvAIPresets.materialize(preset) : {
            prompt: step.prompt
          };
          const out = await window.CV_AI.resolveProvider('openai-image').generateImage({
            ...seed,
            brandEnrich: true
          });
          lastImage = out[0]?.src;
          for (const im of out) try {
            await window.cvImageStore.addFromSrc('ai', null, im.src, {
              source: 'ai',
              name: (seed.prompt || '').slice(0, 60),
              prompt: seed.prompt
            });
          } catch {}
        } else if (step.kind === 'edit' && lastImage) {
          const blob = await urlToBlob(lastImage);
          const out = await window.CV_AI.resolveProvider('openai-image').editImage({
            prompt: step.prompt,
            images: [blob],
            model: modelId
          });
          lastImage = out[0]?.src;
          for (const im of out) try {
            await window.cvImageStore.addFromSrc('ai', null, im.src, {
              source: 'ai',
              name: (step.prompt || '').slice(0, 60),
              prompt: step.prompt
            });
          } catch {}
        } else if (step.kind === 'adopt') {
          const aiList = window.cvImageStore.list('ai').slice(0, 6);
          for (const im of aiList) {
            const scope = step.to === 'project' ? 'projects' : 'system';
            await window.cvImageStore.addFromSrc(scope, target.pid, im.src, {
              name: im.name,
              prompt: im.prompt,
              source: 'ai',
              tags: step.tags || ['AI']
            });
          }
        }
        setPipelineLog(l => l.map(x => x.i === i ? {
          ...x,
          status: 'ok'
        } : x));
      }
      window.dsaToast?.(`Pipeline "${p.name}" complete`);
    } catch (e) {
      setErr(`Pipeline failed: ${e.message}`);
      setPipelineLog(l => {
        const next = [...l];
        const idx = next.findIndex(x => x.status === 'running');
        if (idx >= 0) next[idx] = {
          ...next[idx],
          status: 'fail'
        };
        return next;
      });
    } finally {
      setRunningPipelineId(null);
    }
  }
  function savePreset() {
    if (!presetName.trim()) return;
    window.cvAIPresets.addPreset({
      name: presetName.trim(),
      body: prompt,
      icon: 'star',
      model: modelId,
      size: useCustomSize ? `${customSize.w}x${customSize.h}` : size,
      quality,
      output_format: format,
      output_compression: format === 'jpeg' || format === 'webp' ? compression : undefined,
      background,
      moderation,
      n
    });
    setSavePresetOpen(false);
    setPresetName('');
    window.dsaToast?.(`Saved preset "${presetName.trim()}"`);
  }
  async function adoptResult(im, scopeOverride) {
    const scope = scopeOverride || target.scope;
    const meta = {
      name: prompt.slice(0, 60),
      prompt,
      source: 'ai',
      tags: ['AI']
    };
    if (scope === 'system') await window.cvImageStore.addFromSrc('system', null, im.src, meta);else if (scope === 'projects') await window.cvImageStore.addFromSrc('projects', target.pid, im.src, meta);else if (scope === 'hubs') await window.cvImageStore.addFromSrc('hubs', target.pid, im.src, {
      name: prompt.slice(0, 40),
      tags: ['AI']
    });
    window.dsaToast?.(`Adopted into ${scope === 'system' ? 'system library' : scope === 'hubs' ? '360° hubs' : projects.find(p => p.id === target.pid)?.name || 'project'}`);
  }
  function adoptAllResults() {
    for (const r of results) adoptResult(r);
  }
  function downloadResult(im) {
    const a = document.createElement('a');
    a.href = im.src;
    a.download = `vi-${Date.now()}.${im.format || 'png'}`;
    a.click();
  }
  async function addComposeFiles(files) {
    const next = [];
    for (const f of files) {
      const reader = await new Promise((resolve, reject) => {
        const fr = new FileReader();
        fr.onload = () => resolve(fr.result);
        fr.onerror = reject;
        fr.readAsDataURL(f);
      });
      next.push({
        src: reader,
        role: next.length === 0 ? 'base' : 'reference',
        name: f.name
      });
    }
    setComposeImages(prev => [...prev, ...next].slice(0, caps.maxRefImages || 16));
  }
  function removeCompose(i) {
    setComposeImages(prev => prev.filter((_, idx) => idx !== i));
  }
  function setComposeRole(i, role) {
    setComposeImages(prev => prev.map((x, idx) => idx === i ? {
      ...x,
      role
    } : x));
  }
  const configured = window.cvOpenAI.isConfigured();
  const sizeValidation = useMemo_as(() => {
    const sz = useCustomSize ? `${customSize.w}x${customSize.h}` : size;
    return window.cvOpenAI.validateSize?.(modelId, sz) || {
      ok: true
    };
  }, [size, customSize, useCustomSize, modelId]);

  /* ===== RENDER ===== */
  return /*#__PURE__*/React.createElement("div", {
    className: "cv-as"
  }, !configured && /*#__PURE__*/React.createElement(ConnectBanner, {
    onNav: onNav
  }), /*#__PURE__*/React.createElement("div", {
    className: "cv-as-tabs"
  }, MODES.map(m => {
    const cap = window.cvOpenAI.getModelCapabilities(modelId).supports;
    const disabled = m.id === 'edit' && !cap.edit || m.id === 'compose' && !cap.multiRef || m.id === 'mask' && !cap.mask;
    return /*#__PURE__*/React.createElement("button", {
      key: m.id,
      className: `cv-as-tab ${mode === m.id ? 'active' : ''}`,
      onClick: () => !disabled && setMode(m.id),
      disabled: disabled,
      title: disabled ? `Not supported by ${modelId}` : m.desc
    }, /*#__PURE__*/React.createElement(CvIcon, {
      name: m.icon,
      size: 14,
      tone: mode === m.id ? 'gold' : 'bronze'
    }), /*#__PURE__*/React.createElement("span", null, m.label));
  }), /*#__PURE__*/React.createElement("span", {
    className: "cv-as-tab-desc"
  }, MODES.find(m => m.id === mode)?.desc)), /*#__PURE__*/React.createElement("div", {
    className: "cv-as-shell"
  }, /*#__PURE__*/React.createElement(Resizable, {
    storageKey: "ai-studio-cols",
    cols: [{
      id: 'left',
      size: 230,
      min: 200,
      max: 320
    }, {
      id: 'main',
      size: 'flex'
    }, {
      id: 'right',
      size: 340,
      min: 280,
      max: 480
    }]
  }, /*#__PURE__*/React.createElement(PresetRail, {
    presets: presets,
    pipelines: pipelines,
    activePresetId: activePreset,
    onApplyPreset: applyPreset,
    onRemovePreset: id => window.cvAIPresets.removePreset(id),
    onSaveCurrentAsPreset: () => setSavePresetOpen(true),
    onRunPipeline: runPipeline,
    runningPipelineId: runningPipelineId,
    pipelineLog: pipelineLog,
    configured: configured
  }), /*#__PURE__*/React.createElement("div", {
    className: "cv-as-stage cv-stack-loose"
  }, mode === 'generate' && /*#__PURE__*/React.createElement(PromptCard, {
    prompt: prompt,
    setPrompt: setPrompt,
    caps: caps,
    brandEnrich: brandEnrich,
    setBrand: setBrand
  }), mode === 'edit' && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(SourcePicker, {
    label: "Source image",
    url: editSourceUrl,
    onChoose: setEditSourceUrl,
    target: target,
    setTarget: setTarget
  }), /*#__PURE__*/React.createElement(PromptCard, {
    prompt: prompt,
    setPrompt: setPrompt,
    caps: caps,
    brandEnrich: brandEnrich,
    setBrand: setBrand,
    placeholder: "What should change? E.g. 'replace the sky with golden hour' or 'add brushed gold trim to the window frames'"
  })), mode === 'compose' && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(ComposeRack, {
    items: composeImages,
    max: caps.maxRefImages,
    onAddFiles: addComposeFiles,
    onRemove: removeCompose,
    onSetRole: setComposeRole
  }), /*#__PURE__*/React.createElement(PromptCard, {
    prompt: prompt,
    setPrompt: setPrompt,
    caps: caps,
    brandEnrich: brandEnrich,
    setBrand: setBrand,
    placeholder: "Describe the composition. Refer to images by number \u2014 'use image 1 as the room, image 2 as the lighting'"
  })), mode === 'mask' && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(SourcePicker, {
    label: "Image to mask",
    url: maskSourceUrl,
    onChoose: url => {
      setMaskSourceUrl(url);
      setMaskBlob(null);
    },
    target: target,
    setTarget: setTarget
  }), maskSourceUrl && /*#__PURE__*/React.createElement(MaskEditor, {
    src: maskSourceUrl,
    onChange: setMaskBlob,
    height: 300
  }), /*#__PURE__*/React.createElement(PromptCard, {
    prompt: prompt,
    setPrompt: setPrompt,
    caps: caps,
    brandEnrich: brandEnrich,
    setBrand: setBrand,
    placeholder: "What to paint into the brushed region. E.g. \"a sandstone fireplace\""
  })), mode === 'chat' && /*#__PURE__*/React.createElement(ChatLane, {
    turns: chatTurns,
    input: chatInput,
    setInput: setChatInput,
    busy: chatBusy,
    onSend: sendChat,
    onReset: () => {
      setChatTurns([]);
      setChatRespId(null);
    },
    configured: configured
  }), err && /*#__PURE__*/React.createElement("div", {
    className: "cv-as-err"
  }, err), mode !== 'chat' && /*#__PURE__*/React.createElement(ParamBar, {
    modelId: modelId,
    models: models,
    caps: caps,
    size: size,
    setSize: setSize,
    useCustomSize: useCustomSize,
    setUseCustomSize: setUseCustomSize,
    customSize: customSize,
    setCustomSize: setCustomSize,
    sizeValidation: sizeValidation,
    quality: quality,
    setQuality: setQuality,
    n: n,
    setN: setN,
    showAdvanced: showAdvanced,
    setShowAdvanced: setShowAdvanced,
    format: format,
    setFormat: setFormat,
    compression: compression,
    setCompression: setCompression,
    background: background,
    setBackground: setBackground,
    moderation: moderation,
    setModeration: setModeration,
    stream: stream,
    setStream: setStream,
    partialImages: partialImages,
    setPartialImages: setPartialImages,
    setModelId: setModelId,
    target: target,
    setTarget: setTarget,
    projects: projects,
    onSavePreset: () => setSavePresetOpen(true)
  }), mode !== 'chat' && /*#__PURE__*/React.createElement("div", {
    className: "cv-as-runbar"
  }, /*#__PURE__*/React.createElement("button", {
    className: "cv-as-run-btn",
    disabled: busy || !configured || !sizeValidation.ok || !prompt.trim(),
    onClick: () => mode === 'generate' ? runGenerate() : mode === 'edit' ? runEdit() : mode === 'compose' ? runCompose() : runMask()
  }, /*#__PURE__*/React.createElement(ViShape, {
    size: 14,
    animated: busy
  }), /*#__PURE__*/React.createElement("span", null, busy ? stream ? 'Streaming…' : 'Generating…' : mode === 'generate' ? 'Generate' : mode === 'edit' ? 'Apply edit' : mode === 'compose' ? 'Compose' : 'Apply mask')), /*#__PURE__*/React.createElement("div", {
    className: "cv-as-runbar-meta"
  }, !sizeValidation.ok && /*#__PURE__*/React.createElement("span", {
    className: "cv-as-warn"
  }, sizeValidation.reason), sizeValidation.ok && sizeValidation.experimental && /*#__PURE__*/React.createElement("span", {
    className: "cv-as-warn cv-as-warn--mild"
  }, "Experimental size"), /*#__PURE__*/React.createElement("span", {
    className: "cv-as-cost"
  }, /*#__PURE__*/React.createElement("b", null, n), "\xD7 ", format.toUpperCase(), format === 'jpeg' || format === 'webp' ? ` ${compression}%` : '', " \xB7 ", /*#__PURE__*/React.createElement("code", null, modelId))))), /*#__PURE__*/React.createElement(ResultsRail, {
    results: results,
    partials: partials,
    busy: busy,
    n: n,
    onAdopt: adoptResult,
    onAdoptAll: adoptAllResults,
    onDownload: downloadResult,
    onEditAgain: src => {
      setEditSourceUrl(src);
      setMode('edit');
    },
    history: window.cvImageStore.list('ai').slice(0, 6)
  }))), savePresetOpen && /*#__PURE__*/React.createElement(SavePresetModal, {
    name: presetName,
    setName: setPresetName,
    onCancel: () => setSavePresetOpen(false),
    onSave: savePreset
  }));
}

/* ============================================================
   ConnectBanner
   ============================================================ */
function ConnectBanner({
  onNav
}) {
  return /*#__PURE__*/React.createElement("div", {
    className: "cv-as-banner"
  }, /*#__PURE__*/React.createElement("div", {
    className: "cv-as-banner-shape"
  }, /*#__PURE__*/React.createElement(ViShape, {
    size: 20
  })), /*#__PURE__*/React.createElement("div", {
    className: "cv-as-banner-body"
  }, /*#__PURE__*/React.createElement("h4", null, "AI Studio is in preview mode"), /*#__PURE__*/React.createElement("p", null, "Connect your OpenAI API key to unlock generation, editing, masks, and chat.")), /*#__PURE__*/React.createElement("button", {
    className: "cv-pill cv-pill--filled",
    onClick: () => onNav?.('settings')
  }, /*#__PURE__*/React.createElement(CvIcon, {
    name: "gear",
    size: 12,
    tone: "ink"
  }), " Open Settings"));
}

/* ============================================================
   PresetRail
   ============================================================ */
function PresetRail({
  presets,
  pipelines,
  activePresetId,
  onApplyPreset,
  onRemovePreset,
  onSaveCurrentAsPreset,
  onRunPipeline,
  runningPipelineId,
  pipelineLog,
  configured
}) {
  return /*#__PURE__*/React.createElement("div", {
    className: "cv-as-rail"
  }, /*#__PURE__*/React.createElement("div", {
    className: "cv-panel-head"
  }, /*#__PURE__*/React.createElement("h4", null, "Presets"), /*#__PURE__*/React.createElement("span", {
    className: "meta"
  }, presets.length), /*#__PURE__*/React.createElement("div", {
    className: "right"
  }, /*#__PURE__*/React.createElement("button", {
    className: "cv-as-icon-btn",
    title: "Save current as preset",
    onClick: onSaveCurrentAsPreset
  }, "+"))), /*#__PURE__*/React.createElement("div", {
    className: "cv-as-preset-list"
  }, presets.map(p => /*#__PURE__*/React.createElement("button", {
    key: p.id,
    className: `cv-as-preset ${activePresetId === p.id ? 'active' : ''}`,
    onClick: () => onApplyPreset(p)
  }, /*#__PURE__*/React.createElement("span", {
    className: "ico"
  }, /*#__PURE__*/React.createElement(CvIcon, {
    name: p.icon || 'star',
    size: 13,
    tone: activePresetId === p.id ? 'gold' : 'bronze'
  })), /*#__PURE__*/React.createElement("span", {
    className: "name"
  }, p.name), /*#__PURE__*/React.createElement("button", {
    className: "x",
    onClick: e => {
      e.stopPropagation();
      onRemovePreset(p.id);
    },
    title: "Remove"
  }, "\xD7")))), /*#__PURE__*/React.createElement("div", {
    className: "cv-panel-head",
    style: {
      marginTop: 'var(--s-6)'
    }
  }, /*#__PURE__*/React.createElement("h4", null, "Pipelines"), /*#__PURE__*/React.createElement("span", {
    className: "meta"
  }, pipelines.length)), /*#__PURE__*/React.createElement("div", {
    className: "cv-as-pipeline-list"
  }, pipelines.map(p => /*#__PURE__*/React.createElement("div", {
    key: p.id,
    className: `cv-as-pipeline ${runningPipelineId === p.id ? 'running' : ''}`
  }, /*#__PURE__*/React.createElement("div", {
    className: "head"
  }, /*#__PURE__*/React.createElement("span", {
    className: "name"
  }, p.name), /*#__PURE__*/React.createElement("button", {
    className: "cv-as-pipe-run",
    disabled: !configured || runningPipelineId,
    onClick: () => onRunPipeline(p)
  }, /*#__PURE__*/React.createElement(ViShape, {
    size: 10
  }), " Run")), /*#__PURE__*/React.createElement("p", null, p.desc), /*#__PURE__*/React.createElement("ol", null, p.steps.map((s, i) => {
    const log = pipelineLog.find(l => l.i === i);
    return /*#__PURE__*/React.createElement("li", {
      key: i,
      className: log?.status || ''
    }, /*#__PURE__*/React.createElement("span", {
      className: "badge"
    }, s.kind), /*#__PURE__*/React.createElement("span", {
      className: "lbl"
    }, s.label || s.prompt || ''), log?.status === 'running' && /*#__PURE__*/React.createElement("span", {
      className: "dot"
    }), log?.status === 'ok' && /*#__PURE__*/React.createElement("span", {
      className: "ok"
    }, "\u2713"), log?.status === 'fail' && /*#__PURE__*/React.createElement("span", {
      className: "bad"
    }, "\u2717"));
  }))))));
}

/* ============================================================
   PromptCard
   ============================================================ */
function PromptCard({
  prompt,
  setPrompt,
  caps,
  brandEnrich,
  setBrand,
  placeholder
}) {
  const remaining = (caps?.maxPromptChars || 32000) - prompt.length;
  return /*#__PURE__*/React.createElement("div", {
    className: "cv-as-prompt"
  }, /*#__PURE__*/React.createElement("div", {
    className: "cv-panel-head"
  }, /*#__PURE__*/React.createElement("h4", null, "Prompt"), /*#__PURE__*/React.createElement("span", {
    className: "meta"
  }, "describe what you want")), /*#__PURE__*/React.createElement("textarea", {
    value: prompt,
    onChange: e => setPrompt(e.target.value),
    rows: 4,
    placeholder: placeholder || 'Describe the image. Vi will respect ConceptV warmth + gold accents.'
  }), /*#__PURE__*/React.createElement("div", {
    className: "cv-as-prompt-meta"
  }, /*#__PURE__*/React.createElement("label", {
    className: "cv-as-toggle"
  }, /*#__PURE__*/React.createElement("input", {
    type: "checkbox",
    checked: brandEnrich,
    onChange: e => setBrand(e.target.checked)
  }), /*#__PURE__*/React.createElement("span", null, "Brand-enrich the prompt")), /*#__PURE__*/React.createElement("span", {
    className: `cv-as-count ${remaining < 200 ? 'low' : ''}`
  }, remaining.toLocaleString(), " chars left")));
}

/* ============================================================
   SourcePicker
   ============================================================ */
function SourcePicker({
  label,
  url,
  onChoose,
  target,
  setTarget
}) {
  const fileRef = useRef_as(null);
  const [pickerOpen, setPicker] = useState_as(false);
  const projects = window.cvImageStore.listProjects();
  async function onFile(file) {
    const reader = await new Promise((res, rej) => {
      const fr = new FileReader();
      fr.onload = () => res(fr.result);
      fr.onerror = rej;
      fr.readAsDataURL(file);
    });
    onChoose(reader);
  }
  return /*#__PURE__*/React.createElement("div", {
    className: "cv-as-source"
  }, /*#__PURE__*/React.createElement("div", {
    className: "cv-panel-head"
  }, /*#__PURE__*/React.createElement("h4", null, label), /*#__PURE__*/React.createElement("div", {
    className: "right"
  }, /*#__PURE__*/React.createElement("button", {
    className: "cv-as-icon-btn cv-as-icon-btn--wide",
    onClick: () => fileRef.current?.click()
  }, /*#__PURE__*/React.createElement(CvIcon, {
    name: "cloud-upload",
    size: 11,
    tone: "bronze"
  }), " Upload"), /*#__PURE__*/React.createElement("button", {
    className: "cv-as-icon-btn cv-as-icon-btn--wide",
    onClick: () => setPicker(p => !p)
  }, /*#__PURE__*/React.createElement(CvIcon, {
    name: "image-stack",
    size: 11,
    tone: "bronze"
  }), " Library"), /*#__PURE__*/React.createElement("input", {
    ref: fileRef,
    type: "file",
    accept: "image/*",
    style: {
      display: 'none'
    },
    onChange: e => e.target.files[0] && onFile(e.target.files[0])
  }))), url ? /*#__PURE__*/React.createElement("div", {
    className: "cv-as-source-preview"
  }, /*#__PURE__*/React.createElement("img", {
    src: url,
    alt: ""
  }), /*#__PURE__*/React.createElement("button", {
    className: "cv-as-source-clear",
    onClick: () => onChoose(null)
  }, "\u2715")) : /*#__PURE__*/React.createElement("div", {
    className: "cv-as-dropzone",
    onClick: () => fileRef.current?.click()
  }, /*#__PURE__*/React.createElement(CvIcon, {
    name: "image",
    size: 24,
    tone: "bronze"
  }), /*#__PURE__*/React.createElement("span", null, "Drop or click to upload, or pick from your library.")), pickerOpen && /*#__PURE__*/React.createElement(LibraryPicker, {
    onClose: () => setPicker(false),
    onChoose: src => {
      onChoose(src);
      setPicker(false);
    },
    target: target,
    setTarget: setTarget,
    projects: projects
  }));
}
function LibraryPicker({
  onClose,
  onChoose,
  target,
  setTarget,
  projects
}) {
  const [scope, setScope] = useState_as(target.scope);
  const list = scope === 'system' ? window.cvImageStore.list('system') : scope === 'ai' ? window.cvImageStore.list('ai') : window.cvImageStore.list('projects', target.pid);
  return /*#__PURE__*/React.createElement("div", {
    className: "cv-as-picker"
  }, /*#__PURE__*/React.createElement("div", {
    className: "cv-as-picker-head"
  }, /*#__PURE__*/React.createElement("div", {
    className: "tabs"
  }, [['system', 'System'], ['projects', 'Projects'], ['ai', 'AI history']].map(([id, lbl]) => /*#__PURE__*/React.createElement("button", {
    key: id,
    className: scope === id ? 'active' : '',
    onClick: () => setScope(id)
  }, lbl))), scope === 'projects' && /*#__PURE__*/React.createElement("select", {
    value: target.pid,
    onChange: e => setTarget({
      ...target,
      pid: e.target.value
    })
  }, projects.map(p => /*#__PURE__*/React.createElement("option", {
    key: p.id,
    value: p.id
  }, p.name))), /*#__PURE__*/React.createElement("button", {
    className: "x",
    onClick: onClose
  }, "\u2715")), /*#__PURE__*/React.createElement("div", {
    className: "cv-as-picker-grid"
  }, list.length === 0 && /*#__PURE__*/React.createElement("span", {
    className: "cv-as-empty-line"
  }, "Nothing here yet."), list.map(im => /*#__PURE__*/React.createElement("button", {
    key: im.id,
    className: "cv-as-picker-tile",
    onClick: () => onChoose(im.src),
    title: im.name
  }, /*#__PURE__*/React.createElement("img", {
    src: im.src,
    alt: ""
  }), /*#__PURE__*/React.createElement("span", null, im.name)))));
}

/* ============================================================
   ComposeRack
   ============================================================ */
function ComposeRack({
  items,
  max,
  onAddFiles,
  onRemove,
  onSetRole
}) {
  const fileRef = useRef_as(null);
  return /*#__PURE__*/React.createElement("div", {
    className: "cv-as-compose"
  }, /*#__PURE__*/React.createElement("div", {
    className: "cv-panel-head"
  }, /*#__PURE__*/React.createElement("h4", null, "References"), /*#__PURE__*/React.createElement("span", {
    className: "meta"
  }, items.length, " / ", max, " max"), /*#__PURE__*/React.createElement("div", {
    className: "right"
  }, /*#__PURE__*/React.createElement("button", {
    className: "cv-as-icon-btn cv-as-icon-btn--wide",
    onClick: () => fileRef.current?.click(),
    disabled: items.length >= max
  }, /*#__PURE__*/React.createElement(CvIcon, {
    name: "plus",
    size: 11,
    tone: "bronze"
  }), " Add"), /*#__PURE__*/React.createElement("input", {
    ref: fileRef,
    type: "file",
    accept: "image/*",
    multiple: true,
    style: {
      display: 'none'
    },
    onChange: e => {
      onAddFiles([...e.target.files]);
      e.target.value = '';
    }
  }))), items.length === 0 ? /*#__PURE__*/React.createElement("div", {
    className: "cv-as-dropzone",
    onClick: () => fileRef.current?.click()
  }, /*#__PURE__*/React.createElement(CvIcon, {
    name: "image-stack",
    size: 24,
    tone: "bronze"
  }), /*#__PURE__*/React.createElement("span", null, "Upload up to ", max, " references \u2014 each can play a role.")) : /*#__PURE__*/React.createElement("div", {
    className: "cv-as-compose-grid"
  }, items.map((it, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    className: "cv-as-compose-tile"
  }, /*#__PURE__*/React.createElement("span", {
    className: "num"
  }, i + 1), /*#__PURE__*/React.createElement("img", {
    src: it.src,
    alt: ""
  }), /*#__PURE__*/React.createElement("button", {
    className: "x",
    onClick: () => onRemove(i)
  }, "\xD7"), /*#__PURE__*/React.createElement("div", {
    className: "role-row"
  }, ROLE_OPTIONS.map(r => /*#__PURE__*/React.createElement("button", {
    key: r.id,
    className: it.role === r.id ? 'active' : '',
    title: r.desc,
    onClick: () => onSetRole(i, r.id)
  }, r.label)))))));
}

/* ============================================================
   ParamBar — compact, deck-restrained, collapsible advanced section
   ============================================================ */
function ParamBar({
  modelId,
  models,
  caps,
  setModelId,
  size,
  setSize,
  useCustomSize,
  setUseCustomSize,
  customSize,
  setCustomSize,
  sizeValidation,
  quality,
  setQuality,
  format,
  setFormat,
  compression,
  setCompression,
  background,
  setBackground,
  moderation,
  setModeration,
  n,
  setN,
  stream,
  setStream,
  partialImages,
  setPartialImages,
  target,
  setTarget,
  projects,
  showAdvanced,
  setShowAdvanced,
  onSavePreset
}) {
  return /*#__PURE__*/React.createElement("div", {
    className: "cv-as-params"
  }, /*#__PURE__*/React.createElement("div", {
    className: "cv-as-params-main"
  }, /*#__PURE__*/React.createElement("div", {
    className: "cv-as-param"
  }, /*#__PURE__*/React.createElement("label", null, "Model"), /*#__PURE__*/React.createElement("select", {
    value: modelId,
    onChange: e => setModelId(e.target.value)
  }, models.length === 0 && /*#__PURE__*/React.createElement("option", null, modelId), models.map(m => /*#__PURE__*/React.createElement("option", {
    key: m.id,
    value: m.id
  }, m.id, m.tier === 'flagship' ? ' ★' : '')))), /*#__PURE__*/React.createElement("div", {
    className: "cv-as-param cv-as-param--size"
  }, /*#__PURE__*/React.createElement("label", null, "Size"), /*#__PURE__*/React.createElement("div", {
    className: "cv-as-size-pills"
  }, caps.sizes.slice(0, 4).map(s => /*#__PURE__*/React.createElement("button", {
    key: s,
    className: !useCustomSize && size === s ? 'on' : '',
    onClick: () => {
      setUseCustomSize(false);
      setSize(s);
    }
  }, s === 'auto' ? 'Auto' : s.replace('x', '×'))), caps.sizes.length > 4 && /*#__PURE__*/React.createElement("select", {
    className: "cv-as-size-more",
    value: useCustomSize ? '__custom' : size,
    onChange: e => {
      if (e.target.value === '__custom') setUseCustomSize(true);else {
        setUseCustomSize(false);
        setSize(e.target.value);
      }
    }
  }, /*#__PURE__*/React.createElement("option", {
    value: "",
    disabled: true
  }, "More\u2026"), caps.sizes.slice(4).map(s => /*#__PURE__*/React.createElement("option", {
    key: s,
    value: s
  }, s.replace('x', ' × '))), caps.supports.customSize && /*#__PURE__*/React.createElement("option", {
    value: "__custom"
  }, "Custom\u2026")), caps.sizes.length <= 4 && caps.supports.customSize && /*#__PURE__*/React.createElement("button", {
    className: useCustomSize ? 'on' : '',
    onClick: () => setUseCustomSize(true)
  }, "Custom")), useCustomSize && /*#__PURE__*/React.createElement("div", {
    className: "cv-as-custom-size"
  }, /*#__PURE__*/React.createElement("input", {
    type: "number",
    min: 256,
    max: 3840,
    step: 16,
    value: customSize.w,
    onChange: e => setCustomSize(c => ({
      ...c,
      w: Number(e.target.value)
    }))
  }), /*#__PURE__*/React.createElement("span", null, "\xD7"), /*#__PURE__*/React.createElement("input", {
    type: "number",
    min: 256,
    max: 3840,
    step: 16,
    value: customSize.h,
    onChange: e => setCustomSize(c => ({
      ...c,
      h: Number(e.target.value)
    }))
  }), /*#__PURE__*/React.createElement("span", {
    className: `hint ${sizeValidation.ok ? 'ok' : 'fail'}`
  }, sizeValidation.ok ? `${(customSize.w * customSize.h / 1e6).toFixed(2)}MP` : sizeValidation.reason))), /*#__PURE__*/React.createElement("div", {
    className: "cv-as-param"
  }, /*#__PURE__*/React.createElement("label", null, "Variants"), /*#__PURE__*/React.createElement("select", {
    value: n,
    onChange: e => setN(Number(e.target.value)),
    disabled: !caps.supports.n
  }, Array.from({
    length: caps.supports.n ? caps.supports.maxN || 1 : 1
  }).map((_, i) => /*#__PURE__*/React.createElement("option", {
    key: i + 1,
    value: i + 1
  }, i + 1)))), caps.qualities.length > 0 && /*#__PURE__*/React.createElement("div", {
    className: "cv-as-param"
  }, /*#__PURE__*/React.createElement("label", null, "Quality"), /*#__PURE__*/React.createElement("select", {
    value: quality,
    onChange: e => setQuality(e.target.value)
  }, caps.qualities.map(q => /*#__PURE__*/React.createElement("option", {
    key: q,
    value: q
  }, q)))), /*#__PURE__*/React.createElement("div", {
    className: "cv-as-param cv-as-param--target"
  }, /*#__PURE__*/React.createElement("label", null, "Adopt into"), /*#__PURE__*/React.createElement("div", {
    className: "cv-as-target"
  }, ['system', 'projects', 'hubs'].map(s => /*#__PURE__*/React.createElement("button", {
    key: s,
    className: target.scope === s ? 'on' : '',
    onClick: () => setTarget({
      ...target,
      scope: s
    })
  }, s === 'system' ? 'System' : s === 'projects' ? 'Project' : 'Hub')), (target.scope === 'projects' || target.scope === 'hubs') && /*#__PURE__*/React.createElement("select", {
    value: target.pid,
    onChange: e => setTarget({
      ...target,
      pid: e.target.value
    })
  }, projects.map(p => /*#__PURE__*/React.createElement("option", {
    key: p.id,
    value: p.id
  }, p.name))))), /*#__PURE__*/React.createElement("div", {
    className: "cv-as-params-actions"
  }, /*#__PURE__*/React.createElement("button", {
    className: "cv-as-link-btn",
    onClick: () => setShowAdvanced(v => !v)
  }, showAdvanced ? 'Hide advanced' : 'Advanced', " ", showAdvanced ? '▴' : '▾'), /*#__PURE__*/React.createElement("button", {
    className: "cv-as-link-btn",
    onClick: onSavePreset
  }, /*#__PURE__*/React.createElement(CvIcon, {
    name: "star",
    size: 11,
    tone: "bronze"
  }), " Save preset"))), showAdvanced && /*#__PURE__*/React.createElement("div", {
    className: "cv-as-params-advanced"
  }, caps.outputFormats?.length > 0 && /*#__PURE__*/React.createElement("div", {
    className: "cv-as-param"
  }, /*#__PURE__*/React.createElement("label", null, "Format"), /*#__PURE__*/React.createElement("select", {
    value: format,
    onChange: e => setFormat(e.target.value)
  }, caps.outputFormats.map(f => /*#__PURE__*/React.createElement("option", {
    key: f,
    value: f
  }, f)))), (format === 'jpeg' || format === 'webp') && /*#__PURE__*/React.createElement("div", {
    className: "cv-as-param cv-as-param--slider"
  }, /*#__PURE__*/React.createElement("label", null, "Compression"), /*#__PURE__*/React.createElement("input", {
    type: "range",
    min: 0,
    max: 100,
    value: compression,
    onChange: e => setCompression(Number(e.target.value))
  }), /*#__PURE__*/React.createElement("span", {
    className: "cv-mono cv-muted"
  }, compression, "%")), caps.backgrounds?.length > 0 && /*#__PURE__*/React.createElement("div", {
    className: "cv-as-param"
  }, /*#__PURE__*/React.createElement("label", null, "Background"), /*#__PURE__*/React.createElement("select", {
    value: background,
    onChange: e => setBackground(e.target.value)
  }, caps.backgrounds.map(b => /*#__PURE__*/React.createElement("option", {
    key: b,
    value: b
  }, b)))), caps.moderations?.length > 0 && /*#__PURE__*/React.createElement("div", {
    className: "cv-as-param"
  }, /*#__PURE__*/React.createElement("label", null, "Moderation"), /*#__PURE__*/React.createElement("select", {
    value: moderation,
    onChange: e => setModeration(e.target.value)
  }, caps.moderations.map(m => /*#__PURE__*/React.createElement("option", {
    key: m,
    value: m
  }, m)))), caps.supports.stream && /*#__PURE__*/React.createElement("div", {
    className: "cv-as-param"
  }, /*#__PURE__*/React.createElement("label", null, "Streaming"), /*#__PURE__*/React.createElement("label", {
    className: "cv-as-toggle inline"
  }, /*#__PURE__*/React.createElement("input", {
    type: "checkbox",
    checked: stream,
    onChange: e => setStream(e.target.checked)
  }), /*#__PURE__*/React.createElement("span", null, "Stream partials"))), caps.supports.stream && stream && /*#__PURE__*/React.createElement("div", {
    className: "cv-as-param cv-as-param--slider"
  }, /*#__PURE__*/React.createElement("label", null, "Partial frames"), /*#__PURE__*/React.createElement("input", {
    type: "range",
    min: 0,
    max: caps.supports.partialImages || 3,
    value: partialImages,
    onChange: e => setPartialImages(Number(e.target.value))
  }), /*#__PURE__*/React.createElement("span", {
    className: "cv-mono cv-muted"
  }, partialImages))));
}

/* ============================================================
   ResultsRail
   ============================================================ */
function ResultsRail({
  results,
  partials,
  busy,
  n,
  onAdopt,
  onAdoptAll,
  onDownload,
  onEditAgain,
  history
}) {
  return /*#__PURE__*/React.createElement("div", {
    className: "cv-as-rail"
  }, /*#__PURE__*/React.createElement("div", {
    className: "cv-panel-head"
  }, /*#__PURE__*/React.createElement("h4", null, "Results"), results.length > 0 && /*#__PURE__*/React.createElement("div", {
    className: "right"
  }, /*#__PURE__*/React.createElement("button", {
    className: "cv-as-link-btn",
    onClick: onAdoptAll
  }, "Adopt all"))), busy && /*#__PURE__*/React.createElement("div", {
    className: "cv-as-results-grid"
  }, Array.from({
    length: n
  }).map((_, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    className: "cv-as-skel"
  }, partials[i] ? /*#__PURE__*/React.createElement("img", {
    src: partials[i],
    alt: "",
    className: "partial"
  }) : /*#__PURE__*/React.createElement("div", {
    className: "placeholder"
  }, /*#__PURE__*/React.createElement(ViShape, {
    size: 18,
    animated: true
  }), /*#__PURE__*/React.createElement("span", null, "Variant ", i + 1))))), !busy && results.length === 0 && /*#__PURE__*/React.createElement("div", {
    className: "cv-as-empty"
  }, /*#__PURE__*/React.createElement(DiamondShape, null), /*#__PURE__*/React.createElement("p", null, "Run a generation to see results here.")), !busy && results.length > 0 && /*#__PURE__*/React.createElement("div", {
    className: "cv-as-results-grid"
  }, results.map((r, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    className: "cv-as-result"
  }, /*#__PURE__*/React.createElement("img", {
    src: r.src,
    alt: ""
  }), /*#__PURE__*/React.createElement("div", {
    className: "actions"
  }, /*#__PURE__*/React.createElement("button", {
    className: "primary",
    onClick: () => onAdopt(r)
  }, "Adopt"), /*#__PURE__*/React.createElement("button", {
    onClick: () => onEditAgain(r.src)
  }, "Edit"), /*#__PURE__*/React.createElement("button", {
    className: "icon",
    onClick: () => onDownload(r),
    title: "Download"
  }, /*#__PURE__*/React.createElement(CvIcon, {
    name: "cloud-download",
    size: 11,
    tone: "bronze"
  })))))), /*#__PURE__*/React.createElement("div", {
    className: "cv-panel-head",
    style: {
      marginTop: 'var(--s-6)'
    }
  }, /*#__PURE__*/React.createElement("h4", null, "Recent"), /*#__PURE__*/React.createElement("span", {
    className: "meta"
  }, history.length)), /*#__PURE__*/React.createElement("div", {
    className: "cv-as-history"
  }, history.length === 0 && /*#__PURE__*/React.createElement("span", {
    className: "cv-as-empty-line"
  }, "No history yet."), history.map(im => /*#__PURE__*/React.createElement("button", {
    key: im.id,
    className: "cv-as-history-item",
    onClick: () => onEditAgain(im.src),
    title: im.prompt
  }, /*#__PURE__*/React.createElement("img", {
    src: im.src,
    alt: ""
  }), /*#__PURE__*/React.createElement("span", null, im.prompt?.slice(0, 60) || im.name)))));
}

/* ============================================================
   ChatLane
   ============================================================ */
function ChatLane({
  turns,
  input,
  setInput,
  busy,
  onSend,
  onReset,
  configured
}) {
  const scrollRef = useRef_as(null);
  useEffect_as(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [turns, busy]);
  return /*#__PURE__*/React.createElement("div", {
    className: "cv-as-chat"
  }, /*#__PURE__*/React.createElement("div", {
    className: "cv-panel-head"
  }, /*#__PURE__*/React.createElement("h4", null, "Multi-turn editing"), /*#__PURE__*/React.createElement("span", {
    className: "meta"
  }, "via Responses API"), turns.length > 0 && /*#__PURE__*/React.createElement("div", {
    className: "right"
  }, /*#__PURE__*/React.createElement("button", {
    className: "cv-as-link-btn",
    onClick: onReset
  }, /*#__PURE__*/React.createElement(CvIcon, {
    name: "refresh",
    size: 11,
    tone: "bronze"
  }), " Reset thread"))), /*#__PURE__*/React.createElement("div", {
    className: "cv-as-chat-feed",
    ref: scrollRef
  }, turns.length === 0 && /*#__PURE__*/React.createElement("div", {
    className: "cv-as-chat-empty"
  }, /*#__PURE__*/React.createElement(DiamondShape, null), /*#__PURE__*/React.createElement("h4", null, "Start a conversation"), /*#__PURE__*/React.createElement("p", null, "Each message can generate fresh or edit the previous image. Context threads automatically.")), turns.map((t, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    className: `cv-as-chat-turn ${t.role}`
  }, /*#__PURE__*/React.createElement("div", {
    className: "bubble"
  }, /*#__PURE__*/React.createElement("span", {
    className: "who"
  }, t.role === 'user' ? 'You' : 'Vi'), /*#__PURE__*/React.createElement("span", {
    className: "text"
  }, t.content), t.revisedPrompt && t.role === 'vi' && /*#__PURE__*/React.createElement("details", {
    className: "revised"
  }, /*#__PURE__*/React.createElement("summary", null, "Revised prompt"), /*#__PURE__*/React.createElement("code", null, t.revisedPrompt)), t.images?.length > 0 && /*#__PURE__*/React.createElement("div", {
    className: "images"
  }, t.images.map((im, j) => /*#__PURE__*/React.createElement("img", {
    key: j,
    src: im.src,
    alt: ""
  })))))), busy && /*#__PURE__*/React.createElement("div", {
    className: "cv-as-chat-turn vi"
  }, /*#__PURE__*/React.createElement("div", {
    className: "bubble"
  }, /*#__PURE__*/React.createElement(ViShape, {
    size: 14,
    animated: true
  }), " generating\u2026"))), /*#__PURE__*/React.createElement("div", {
    className: "cv-as-chat-composer"
  }, /*#__PURE__*/React.createElement("textarea", {
    value: input,
    onChange: e => setInput(e.target.value),
    onKeyDown: e => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        onSend();
      }
    },
    rows: 2,
    placeholder: configured ? 'Tell Vi what to make or change…' : 'Connect OpenAI in Settings to chat-edit.',
    disabled: !configured || busy
  }), /*#__PURE__*/React.createElement("button", {
    className: "cv-as-run-btn cv-as-run-btn--sm",
    onClick: onSend,
    disabled: !configured || busy || !input.trim()
  }, /*#__PURE__*/React.createElement(ViShape, {
    size: 12
  }))));
}

/* ============================================================
   SavePresetModal
   ============================================================ */
function SavePresetModal({
  name,
  setName,
  onCancel,
  onSave
}) {
  return /*#__PURE__*/React.createElement("div", {
    className: "cv-as-modal-back",
    onClick: onCancel
  }, /*#__PURE__*/React.createElement("div", {
    className: "cv-as-modal",
    onClick: e => e.stopPropagation()
  }, /*#__PURE__*/React.createElement("h3", null, "Save current config as preset"), /*#__PURE__*/React.createElement("p", null, "Captures every parameter you've set \u2014 prompt, model, size, quality, format, n, background, moderation."), /*#__PURE__*/React.createElement("input", {
    autoFocus: true,
    value: name,
    onChange: e => setName(e.target.value),
    placeholder: "Name this preset, e.g. \"Bayside hero \u2014 golden hour\""
  }), /*#__PURE__*/React.createElement("div", {
    className: "cv-as-modal-actions"
  }, /*#__PURE__*/React.createElement("button", {
    className: "cv-pill",
    onClick: onCancel
  }, "Cancel"), /*#__PURE__*/React.createElement("button", {
    className: "cv-pill cv-pill--filled",
    disabled: !name.trim(),
    onClick: onSave
  }, "Save preset"))));
}
function DiamondShape() {
  return /*#__PURE__*/React.createElement("svg", {
    viewBox: "0 0 40 40",
    width: "48",
    height: "48",
    fill: "none",
    stroke: "var(--accent-bronze)",
    strokeWidth: "1.5"
  }, /*#__PURE__*/React.createElement("path", {
    d: "M20 4 L36 20 L20 36 L4 20 Z"
  }), /*#__PURE__*/React.createElement("path", {
    d: "M12 12 L28 28 M28 12 L12 28",
    strokeDasharray: "2 3",
    opacity: "0.5"
  }));
}
window.AIStudio = AIStudio;
})(); } catch (e) { __ds_ns.__errors.push({ path: "app/canvases/AIStudio.jsx", error: String((e && e.message) || e) }); }

// app/canvases/Architecture.jsx
try { (() => {
// app/canvases/Architecture.jsx
// Architecture canvas — an explanation of how the Universal Type Registry
// works. Diagrams, layer overview, composition examples, lineage examples,
// and how each existing surface consumes the registry.

const {
  useState: useState_arch,
  useMemo: useMemo_arch,
  useEffect: useEffect_arch
} = React;
function Architecture({
  onNav,
  onOpenBuilder
}) {
  const R = window.CV_REGISTRY;
  const [tick, setTick] = useState_arch(0);
  useEffect_arch(() => R?.subscribe(() => setTick(t => t + 1)), []);
  const counts = useMemo_arch(() => {
    const m = {};
    for (const t of R?.all() || []) m[t.layer] = (m[t.layer] || 0) + 1;
    return m;
  }, [tick]);
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(CanvasHeader, {
    title: "Architecture",
    sub: "How the universal Type Registry stitches every surface together \u2014 one composition substrate for the whole product.",
    actions: /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("button", {
      className: "dsa-btn dsa-btn--outline",
      onClick: () => onNav?.('registry')
    }, "Open Registry \u2192"), /*#__PURE__*/React.createElement("button", {
      className: "dsa-btn dsa-btn--ai",
      onClick: () => onOpenBuilder?.()
    }, /*#__PURE__*/React.createElement(ViShape, {
      size: 12
    }), " + New Type"))
  }), /*#__PURE__*/React.createElement("div", {
    className: "dsa-canvas-body cv-arch-body"
  }, /*#__PURE__*/React.createElement(SectionIntro, null), /*#__PURE__*/React.createElement(Section, {
    title: "The seven layers",
    sub: "Atomic composition \u2014 every Type lives at exactly one layer. Lower layers compose into higher ones; higher Types EMBED lower ones via slots."
  }, /*#__PURE__*/React.createElement(LayerLadder, {
    counts: counts,
    onLayerClick: () => onNav?.('registry')
  })), /*#__PURE__*/React.createElement(Section, {
    title: "Composition by slots",
    sub: "A Type declares named slots; each slot lists the layers, families, and tags it accepts. The registry validates fills automatically."
  }, /*#__PURE__*/React.createElement(SlotExample, null)), /*#__PURE__*/React.createElement(Section, {
    title: "Inheritance \u2014 extends, never duplicates",
    sub: "A Type extends one parent and inherits its slots, defaults, and variables. Overrides cascade leaf \u2192 root."
  }, /*#__PURE__*/React.createElement(LineageExample, null)), /*#__PURE__*/React.createElement(Section, {
    title: "Types vs Templates",
    sub: "A Type is the schema. A Template is a runnable instance with variables extracted. Same registry, different layer."
  }, /*#__PURE__*/React.createElement(TypesVsTemplates, {
    onNav: onNav
  })), /*#__PURE__*/React.createElement(Section, {
    title: "What consumes the registry",
    sub: "Every surface in the app reads from one source. Add a Type once and it shows up in every consumer."
  }, /*#__PURE__*/React.createElement(ConsumersMatrix, {
    onNav: onNav
  })), /*#__PURE__*/React.createElement(Section, {
    title: "Where new Types come from",
    sub: "Four entry points, one registry. All four produce the same kind of node."
  }, /*#__PURE__*/React.createElement(EntryPoints, {
    onOpenBuilder: onOpenBuilder,
    onNav: onNav
  })), /*#__PURE__*/React.createElement(Section, {
    title: "Cross-system embedding",
    sub: "A widget Type can appear as a slide block. A wizard step can render a widget. Same protocol, no special cases."
  }, /*#__PURE__*/React.createElement(CrossEmbedDiagram, null))));
}

// ===========================================================================
// Intro panel
// ===========================================================================
function SectionIntro() {
  return /*#__PURE__*/React.createElement("div", {
    className: "cv-arch-intro"
  }, /*#__PURE__*/React.createElement("div", {
    className: "cv-arch-intro-head"
  }, /*#__PURE__*/React.createElement(ViShape, {
    size: 26
  }), /*#__PURE__*/React.createElement("h2", null, "One registry. Every composable thing.")), /*#__PURE__*/React.createElement("p", null, "ConceptV Studio used to ship hard-coded widget kinds, wizard kinds, and slide blocks \u2014 three parallel systems with their own pickers. The new universal architecture turns every one of those into a single shape: a ", /*#__PURE__*/React.createElement("strong", null, "Type"), " at a specific ", /*#__PURE__*/React.createElement("strong", null, "layer"), ". Types extend Types. Types embed Types. Vi can create them in-place from any context."), /*#__PURE__*/React.createElement("p", null, "That means a custom widget System the user invents in the Workshop today is the same kind of node as a Wizard kind the team ships next week \u2014 both live in the registry, both can be queried, embedded, extended, and saved as Templates."));
}

// ===========================================================================
// Section wrapper
// ===========================================================================
function Section({
  title,
  sub,
  children
}) {
  return /*#__PURE__*/React.createElement("section", {
    className: "cv-arch-section"
  }, /*#__PURE__*/React.createElement("header", null, /*#__PURE__*/React.createElement("h3", null, title), sub && /*#__PURE__*/React.createElement("p", null, sub)), children);
}

// ===========================================================================
// Layer ladder — vertical bar with counts + example thumb
// ===========================================================================
function LayerLadder({
  counts,
  onLayerClick
}) {
  const R = window.CV_REGISTRY;
  return /*#__PURE__*/React.createElement("div", {
    className: "cv-arch-ladder"
  }, [...(R?.LAYERS || [])].reverse().map(l => {
    const info = R.LAYER_INFO[l];
    const example = R.query({
      layer: l
    })[0];
    return /*#__PURE__*/React.createElement("button", {
      key: l,
      className: "cv-arch-rung",
      onClick: onLayerClick
    }, /*#__PURE__*/React.createElement("div", {
      className: "rank"
    }, "L", info.rank), /*#__PURE__*/React.createElement("div", {
      className: "bar",
      style: {
        background: info.swatch
      }
    }), /*#__PURE__*/React.createElement("div", {
      className: "meta"
    }, /*#__PURE__*/React.createElement("div", {
      className: "name"
    }, info.label), /*#__PURE__*/React.createElement("div", {
      className: "desc"
    }, info.desc)), /*#__PURE__*/React.createElement("div", {
      className: "example"
    }, example && window.TypeThumb && /*#__PURE__*/React.createElement(TypeThumb, {
      type: example,
      width: 150,
      height: 94,
      dense: true
    })), /*#__PURE__*/React.createElement("div", {
      className: "count"
    }, counts[l] || 0));
  }));
}

// ===========================================================================
// Slot example — visualize a System with slots, schema, and a live preview
// ===========================================================================
function SlotExample() {
  const R = window.CV_REGISTRY;
  const t = R?.get('system.widget.hybrid');
  if (!t) return null;
  return /*#__PURE__*/React.createElement("div", {
    className: "cv-arch-slot-ex"
  }, /*#__PURE__*/React.createElement("div", {
    className: "schema"
  }, /*#__PURE__*/React.createElement("div", {
    className: "schema-head"
  }, /*#__PURE__*/React.createElement("span", {
    className: "bracket"
  }, `{`), /*#__PURE__*/React.createElement("code", {
    className: "key"
  }, "\"id\""), ": ", /*#__PURE__*/React.createElement("code", {
    className: "str"
  }, "\"", t.id, "\""), ","), /*#__PURE__*/React.createElement("div", {
    className: "schema-row"
  }, /*#__PURE__*/React.createElement("code", {
    className: "key"
  }, "\"slots\""), ": ", /*#__PURE__*/React.createElement("span", {
    className: "bracket"
  }, `{`)), Object.entries(t.slots).map(([k, s]) => /*#__PURE__*/React.createElement("div", {
    key: k,
    className: "schema-slot"
  }, /*#__PURE__*/React.createElement("code", {
    className: "key"
  }, "\"", k, "\""), ": ", /*#__PURE__*/React.createElement("span", {
    className: "bracket"
  }, `{`), /*#__PURE__*/React.createElement("code", {
    className: "key"
  }, "\"accepts\""), ": ", /*#__PURE__*/React.createElement("span", {
    className: "hint"
  }, describeAccepts(s.accepts)), s.multiple && /*#__PURE__*/React.createElement("span", {
    className: "badge"
  }, "multiple"), s.optional && /*#__PURE__*/React.createElement("span", {
    className: "badge"
  }, "optional"), /*#__PURE__*/React.createElement("span", {
    className: "bracket"
  }, `},`))), /*#__PURE__*/React.createElement("div", {
    className: "schema-row"
  }, /*#__PURE__*/React.createElement("span", {
    className: "bracket"
  }, `}`)), /*#__PURE__*/React.createElement("div", {
    className: "schema-row"
  }, /*#__PURE__*/React.createElement("span", {
    className: "bracket"
  }, `}`))), /*#__PURE__*/React.createElement("div", {
    className: "visual"
  }, /*#__PURE__*/React.createElement("div", {
    className: "visual-head"
  }, /*#__PURE__*/React.createElement("strong", null, t.name), /*#__PURE__*/React.createElement(TypeLayerBadge, {
    layer: t.layer,
    size: "md"
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      marginLeft: 'auto',
      font: '400 11px/1.4 var(--font-body)',
      color: 'var(--fg-muted)'
    }
  }, "rendered with sample data \u2192")), window.TypeThumb && /*#__PURE__*/React.createElement(TypeThumb, {
    type: t,
    width: 360,
    height: 220
  }), /*#__PURE__*/React.createElement("div", {
    className: "visual-slots"
  }, Object.entries(t.slots).map(([k, s]) => /*#__PURE__*/React.createElement("div", {
    key: k,
    className: `vslot ${s.multiple ? 'multi' : ''} ${s.optional ? 'opt' : ''}`
  }, /*#__PURE__*/React.createElement("span", {
    className: "lbl"
  }, s.label || k), /*#__PURE__*/React.createElement("span", {
    className: "hint"
  }, describeAccepts(s.accepts)))))));
}
function describeAccepts(acc = {}) {
  const parts = [];
  if (acc.layers?.length) parts.push(acc.layers.join('|'));
  if (acc.families?.length) parts.push('family:' + acc.families.join('|'));
  if (acc.tags?.length) parts.push('tag:' + acc.tags.join('|'));
  return parts.join(' · ') || 'any';
}

// ===========================================================================
// Lineage example — wizard kinds extending doc.wizard
// ===========================================================================
function LineageExample() {
  const R = window.CV_REGISTRY;
  const root = R?.get('doc.wizard');
  const kids = R?.descendants('doc.wizard') || [];
  if (!root) return null;
  return /*#__PURE__*/React.createElement("div", {
    className: "cv-arch-lineage"
  }, /*#__PURE__*/React.createElement("div", {
    className: "root"
  }, /*#__PURE__*/React.createElement(TypeCard, {
    type: root
  })), /*#__PURE__*/React.createElement("div", {
    className: "connector"
  }), /*#__PURE__*/React.createElement("div", {
    className: "children"
  }, kids.map(k => /*#__PURE__*/React.createElement("div", {
    key: k.id,
    className: "child"
  }, /*#__PURE__*/React.createElement(TypeCard, {
    type: k,
    lineage: true
  })))), /*#__PURE__*/React.createElement("p", {
    className: "caption"
  }, "Each child wizard kind ", /*#__PURE__*/React.createElement("strong", null, "inherits"), " the steps slot, the ", `{ type, layout, mode }`, " defaults, and the brand voice. It only overrides the ", /*#__PURE__*/React.createElement("code", null, "wizardKind"), " field and its tags. New custom flows plug in the same way."));
}

// ===========================================================================
// Types vs Templates
// ===========================================================================
function TypesVsTemplates({
  onNav
}) {
  const R = window.CV_REGISTRY;
  const docType = R?.get('doc.widget');
  return /*#__PURE__*/React.createElement("div", {
    className: "cv-arch-types-templates"
  }, /*#__PURE__*/React.createElement("div", {
    className: "col"
  }, /*#__PURE__*/React.createElement("h4", null, /*#__PURE__*/React.createElement(TypeLayerBadge, {
    layer: "doc",
    size: "lg"
  }), " Type"), /*#__PURE__*/React.createElement("p", null, "A schema \u2014 slots, defaults, variables. ", /*#__PURE__*/React.createElement("em", null, "Doesn't"), " hold instance data."), docType && window.TypeThumb && /*#__PURE__*/React.createElement("div", {
    className: "tt-preview"
  }, /*#__PURE__*/React.createElement(TypeThumb, {
    type: docType,
    width: 300,
    height: 180
  }), /*#__PURE__*/React.createElement("span", {
    className: "tt-label"
  }, docType.name))), /*#__PURE__*/React.createElement("div", {
    className: "arrow"
  }, "+ variables \u2192"), /*#__PURE__*/React.createElement("div", {
    className: "col"
  }, /*#__PURE__*/React.createElement("h4", null, /*#__PURE__*/React.createElement(TypeLayerBadge, {
    layer: "template",
    size: "lg"
  }), " Template"), /*#__PURE__*/React.createElement("p", null, "An instance frozen with extracted parameters \u2014 runnable to produce a fresh doc."), docType && window.TypeThumb && /*#__PURE__*/React.createElement("div", {
    className: "tt-preview"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      position: 'relative'
    }
  }, /*#__PURE__*/React.createElement(TypeThumb, {
    type: docType,
    width: 300,
    height: 180
  }), /*#__PURE__*/React.createElement("span", {
    className: "vars-badge",
    style: {
      position: 'absolute',
      top: 8,
      right: 8,
      background: 'var(--accent-gold)',
      color: 'var(--fg-primary)',
      padding: '4px 8px',
      borderRadius: 999,
      font: '700 10px/1 var(--font-mono)',
      boxShadow: '0 1px 3px rgba(0,0,0,0.15)'
    }
  }, "\uD835\uDCCB 3 variables")), /*#__PURE__*/React.createElement("span", {
    className: "tt-label"
  }, "Tower East \xB7 capture template"))), /*#__PURE__*/React.createElement("div", {
    className: "footer"
  }, /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--outline",
    onClick: () => onNav?.('templates')
  }, "Open Templates \u2192")));
}

// ===========================================================================
// Consumers — what reads from the registry
// ===========================================================================
function ConsumersMatrix({
  onNav
}) {
  const rows = [{
    name: 'Workshop landing',
    reads: 'doc-layer Types (all families)',
    consumes: 'docs',
    cta: 'workshop'
  }, {
    name: 'Widget Builder',
    reads: 'surface · family=widget + system · family=widget',
    consumes: 'kinds, systems',
    cta: 'workshop'
  }, {
    name: 'Wizard Builder',
    reads: 'doc.wizard children + surface · family=wizard-step',
    consumes: 'kinds, step kinds',
    cta: 'workshop'
  }, {
    name: 'Slide library',
    reads: 'block-layer Types',
    consumes: 'blocks',
    cta: 'workshop'
  }, {
    name: 'Templates canvas',
    reads: 'template-layer Types',
    consumes: 'templates',
    cta: 'templates'
  }, {
    name: 'Build canvas',
    reads: 'doc-layer Types + new type-builder',
    consumes: 'all',
    cta: 'build'
  }, {
    name: 'Vi chat',
    reads: 'every Type in scope for context',
    consumes: 'all',
    cta: null
  }];
  return /*#__PURE__*/React.createElement("table", {
    className: "cv-arch-consumers"
  }, /*#__PURE__*/React.createElement("thead", null, /*#__PURE__*/React.createElement("tr", null, /*#__PURE__*/React.createElement("th", null, "Surface"), /*#__PURE__*/React.createElement("th", null, "Reads from registry"), /*#__PURE__*/React.createElement("th", null, "Consumes"), /*#__PURE__*/React.createElement("th", null))), /*#__PURE__*/React.createElement("tbody", null, rows.map(r => /*#__PURE__*/React.createElement("tr", {
    key: r.name
  }, /*#__PURE__*/React.createElement("td", null, /*#__PURE__*/React.createElement("strong", null, r.name)), /*#__PURE__*/React.createElement("td", {
    className: "mono"
  }, r.reads), /*#__PURE__*/React.createElement("td", null, r.consumes), /*#__PURE__*/React.createElement("td", null, r.cta && /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--ghost dsa-btn--sm",
    onClick: () => onNav?.(r.cta)
  }, "Open \u2192"))))));
}

// ===========================================================================
// Entry points — four ways Types get created
// ===========================================================================
function EntryPoints({
  onOpenBuilder,
  onNav
}) {
  const items = [{
    tag: 'In-context',
    title: 'From an instance',
    desc: 'Press "Save as Type" inside any builder — Vi extracts variables and registers the schema.',
    cta: () => onNav?.('workshop')
  }, {
    tag: 'In-context',
    title: 'From a brief',
    desc: 'Inside Workshop or Build, describe what you want and choose "make this a new Type" — Vi proposes the schema.',
    cta: () => onOpenBuilder?.()
  }, {
    tag: 'Standalone',
    title: 'In the Builder',
    desc: 'Open the Type Builder, pick a layer + parent, author slots and defaults from scratch.',
    cta: () => onOpenBuilder?.()
  }, {
    tag: 'Plan-level',
    title: 'In Build',
    desc: 'Vi can include a "create Type" subtask in a multi-stage plan — the new Type registers as it runs.',
    cta: () => onNav?.('build')
  }];
  return /*#__PURE__*/React.createElement("div", {
    className: "cv-arch-entry-grid"
  }, items.map((e, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    className: "cv-arch-entry"
  }, /*#__PURE__*/React.createElement("span", {
    className: "tag"
  }, e.tag), /*#__PURE__*/React.createElement("h4", null, e.title), /*#__PURE__*/React.createElement("p", null, e.desc), /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--ghost dsa-btn--sm",
    onClick: e.cta
  }, "Open \u2192"))));
}

// ===========================================================================
// Cross-embedding diagram — real type thumbs, not text cards
// ===========================================================================
function CrossEmbedDiagram() {
  const R = window.CV_REGISTRY;
  const steps = [{
    type: R?.get('doc.deck'),
    slotLbl: 'slot: slides[ surface ]'
  }, {
    type: R?.get('surface.deck-slide.content'),
    slotLbl: 'slot: sections[ block ]'
  }, {
    type: R?.get('block.callout'),
    slotLbl: 'or any block — including a widget embed',
    highlight: true
  }, {
    type: R?.get('doc.widget'),
    slotLbl: 'a full widget doc, embedded'
  }];
  return /*#__PURE__*/React.createElement("div", {
    className: "cv-arch-xembed"
  }, /*#__PURE__*/React.createElement("div", {
    className: "row"
  }, steps.map((s, i) => s.type ? /*#__PURE__*/React.createElement(React.Fragment, {
    key: i
  }, /*#__PURE__*/React.createElement("div", {
    className: `xembed-card ${s.highlight ? 'highlight' : ''}`
  }, /*#__PURE__*/React.createElement("div", {
    className: "thumb"
  }, window.TypeThumb && /*#__PURE__*/React.createElement(TypeThumb, {
    type: s.type,
    width: 180,
    height: 112
  })), /*#__PURE__*/React.createElement("div", {
    className: "meta"
  }, /*#__PURE__*/React.createElement("strong", null, s.type.name), /*#__PURE__*/React.createElement(TypeLayerBadge, {
    layer: s.type.layer,
    size: "sm"
  }), /*#__PURE__*/React.createElement("em", null, s.slotLbl))), i < steps.length - 1 && /*#__PURE__*/React.createElement("div", {
    className: "xembed-arrow"
  }, "embeds", /*#__PURE__*/React.createElement("br", null), "\u2193")) : null)), /*#__PURE__*/React.createElement("p", {
    className: "caption"
  }, "Any Type can be embedded in any slot that accepts its layer/family/tags. Cycles are prevented by the registry. Cross-family embedding \u2014 widget inside slide, wizard step inside brochure \u2014 works the same way."));
}
window.Architecture = Architecture;
})(); } catch (e) { __ds_ns.__errors.push({ path: "app/canvases/Architecture.jsx", error: String((e && e.message) || e) }); }

// app/canvases/Bridge.jsx
try { (() => {
// app/canvases/Bridge.jsx
// ============================================================================
// Bridge — the canvas surface for CV_HOST (the Environment / Host layer).
//
// PURE PROJECTION: every value shown here is read from CV_HOST.describe() and
// CV_AI's repo capabilities. There is no hand-written status text — connect a
// runtime or stage a change and this view recomputes. This is the same
// "interface = projection of the registry" contract the rest of Studio honours.
//
// It shows: the current environment + what Vi can do in it, the connectable
// runtimes (sandbox review → browser file access → native/MCP), the handoff
// setting, and the queue of proposed changes (each with its real serialized
// source, copy, and apply-to-disk).
// ============================================================================
const {
  useState: useState_br,
  useEffect: useEffect_br,
  useReducer: useReducer_br
} = React;
function useHost() {
  const [, force] = useReducer_br(x => x + 1, 0);
  useEffect_br(() => window.CV_HOST.subscribe(force), []);
  return window.CV_HOST;
}
const CAP_LABEL = {
  read: 'read files',
  write: 'write files',
  list: 'list dirs',
  exec: 'run compiler',
  tools: 'call tools'
};
function Bridge() {
  const HOST = useHost();
  const d = HOST.describe();
  const [busy, setBusy] = useState_br(null);
  async function activate(id) {
    setBusy(id);
    try {
      if (id === '__reconnect') await HOST.reconnectFsapi();else await HOST.runtimes.get(id).activate();
      window.dsaToast?.('Connected — disk access on');
    } catch (e) {
      window.dsaToast?.(e.message);
    }
    setBusy(null);
  }
  return /*#__PURE__*/React.createElement("div", {
    className: "dsa-canvas-scroll",
    style: {
      padding: '28px 32px 64px',
      maxWidth: 1080,
      margin: '0 auto'
    }
  }, /*#__PURE__*/React.createElement("header", {
    style: {
      marginBottom: 22
    }
  }, /*#__PURE__*/React.createElement("h1", {
    style: {
      font: '700 30px/1.05 var(--font-display)',
      color: 'var(--accent-bronze)',
      margin: '0 0 6px',
      letterSpacing: '-0.02em'
    }
  }, "Bridge"), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 14px/1.6 var(--font-body)',
      color: 'var(--fg-secondary)',
      margin: 0,
      maxWidth: 660
    }
  }, "Where Vi reaches the repository. In the sandbox, changes are serialized to real source and staged for review. Connect a file runtime \u2014 here in the browser, or via a local shell when you export \u2014 and Vi writes them to disk directly.")), /*#__PURE__*/React.createElement(EnvCard, {
    d: d
  }), /*#__PURE__*/React.createElement(Section, {
    title: "Runtimes",
    sub: "Ways to reach the world. The best available one handles each operation; sandbox review is the floor."
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 10
    }
  }, d.runtimes.map(r => /*#__PURE__*/React.createElement("div", {
    key: r.id,
    style: {
      display: 'flex',
      alignItems: 'flex-start',
      gap: 14,
      padding: '14px 16px',
      border: '1px solid var(--border-soft)',
      borderRadius: 'var(--r-lg)',
      background: r.available ? 'var(--accent-gold-50, #FBF4D8)' : 'var(--bg-surface)',
      opacity: r.supported ? 1 : 0.55
    }
  }, /*#__PURE__*/React.createElement(Dot, {
    on: r.available
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("strong", {
    style: {
      font: '600 14px var(--font-body)',
      color: 'var(--fg-primary)'
    }
  }, r.label), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '500 11px var(--font-mono)',
      color: 'var(--fg-muted)'
    }
  }, Object.keys(r.caps).filter(k => r.caps[k]).map(k => CAP_LABEL[k]).join(' · ') || 'staging only'), r.available && /*#__PURE__*/React.createElement("span", {
    style: {
      marginLeft: 'auto',
      font: '600 11px var(--font-mono)',
      color: 'var(--status-success, #2E7D32)'
    }
  }, "ACTIVE")), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 12.5px/1.55 var(--font-body)',
      color: 'var(--fg-secondary)',
      margin: '4px 0 0'
    }
  }, r.description), r.canActivate && !r.available && /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--outline dsa-btn--sm",
    style: {
      marginTop: 8
    },
    disabled: !r.supported || busy === r.id,
    onClick: () => activate(r.id)
  }, busy === r.id ? 'Connecting…' : r.supported ? 'Connect…' : 'Not supported here'))))), window.__cvFsapiPending && !d.capabilities.write && /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--solid dsa-btn--sm",
    style: {
      marginTop: 10
    },
    onClick: () => activate('__reconnect')
  }, "Reconnect last folder")), /*#__PURE__*/React.createElement(Section, {
    title: "When there's no disk access",
    sub: "How a committed change is handed off in the sandbox. It is always staged below; these add to that."
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 8
    }
  }, Object.entries(d.handoff.modes).map(([k, m]) => /*#__PURE__*/React.createElement("label", {
    key: k,
    style: {
      display: 'flex',
      gap: 10,
      padding: '11px 14px',
      border: '1px solid var(--border-soft)',
      borderRadius: 'var(--r-md)',
      cursor: 'pointer',
      background: d.handoff.mode === k ? 'var(--accent-gold-50,#FBF4D8)' : 'transparent'
    }
  }, /*#__PURE__*/React.createElement("input", {
    type: "radio",
    name: "handoff",
    checked: d.handoff.mode === k,
    onChange: () => HOST.setHandoffMode(k),
    style: {
      marginTop: 3
    }
  }), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("strong", {
    style: {
      font: '600 13px var(--font-body)',
      color: 'var(--fg-primary)'
    }
  }, m.label), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 12px/1.5 var(--font-body)',
      color: 'var(--fg-secondary)',
      margin: '2px 0 0'
    }
  }, m.desc))))), /*#__PURE__*/React.createElement("label", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 10,
      marginTop: 12,
      font: '400 13px var(--font-body)',
      color: 'var(--fg-secondary)'
    }
  }, /*#__PURE__*/React.createElement("input", {
    type: "checkbox",
    checked: d.handoff.autoApply,
    onChange: e => HOST.setAutoApply(e.target.checked)
  }), "Auto-apply to disk when a writer is connected (skip staging). Off by default.")), /*#__PURE__*/React.createElement(Changes, {
    HOST: HOST,
    d: d
  }), d.stash > 0 && /*#__PURE__*/React.createElement(Section, {
    title: `Agent stash (${d.stash})`,
    sub: "Serialized changes waiting for Claude to read back and commit on the next turn. Copy this if you're driving the loop manually."
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--outline dsa-btn--sm",
    onClick: () => {
      navigator.clipboard?.writeText(JSON.stringify(HOST.readStash(), null, 2));
      window.dsaToast?.('Stash copied');
    }
  }, "Copy stash JSON"), /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--ghost dsa-btn--sm",
    onClick: () => {
      HOST.clearStash();
      HOST.notify();
    }
  }, "Clear stash"))), /*#__PURE__*/React.createElement(Section, {
    title: "What Vi can do here",
    sub: "Repo capabilities in the AI catalogue, routed through the same execute() path as every other Vi move."
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 6
    }
  }, window.CV_AI.query({
    family: 'repo'
  }).map(c => /*#__PURE__*/React.createElement("div", {
    key: c.id,
    style: {
      display: 'flex',
      gap: 10,
      font: '400 12.5px/1.5 var(--font-body)',
      color: 'var(--fg-secondary)'
    }
  }, /*#__PURE__*/React.createElement("code", {
    style: {
      font: '600 12px var(--font-mono)',
      color: 'var(--accent-bronze)',
      minWidth: 110
    }
  }, c.id), /*#__PURE__*/React.createElement("span", null, c.description)))), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 12px/1.55 var(--font-body)',
      color: 'var(--fg-muted)',
      margin: '14px 0 0'
    }
  }, "Serializers (one home per change kind): ", d.serializers.map(s => s.kind).join(' · '), ".")));
}
function EnvCard({
  d
}) {
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 18,
      padding: '18px 22px',
      borderRadius: 'var(--r-xl)',
      background: 'var(--bg-dark)',
      color: 'var(--fg-inverse)',
      marginBottom: 6
    }
  }, /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      font: '500 11px var(--font-mono)',
      opacity: 0.6,
      letterSpacing: '0.08em'
    }
  }, "ENVIRONMENT"), /*#__PURE__*/React.createElement("div", {
    style: {
      font: '700 22px var(--font-display)',
      letterSpacing: '-0.01em'
    }
  }, d.modeLabel)), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 7,
      marginLeft: 'auto',
      flexWrap: 'wrap',
      justifyContent: 'flex-end'
    }
  }, Object.entries(d.capabilities).map(([k, on]) => /*#__PURE__*/React.createElement("span", {
    key: k,
    style: {
      font: '600 11px var(--font-mono)',
      padding: '4px 9px',
      borderRadius: 999,
      background: on ? 'var(--accent-gold, #E0C010)' : 'rgba(255,255,255,.08)',
      color: on ? 'var(--bg-dark, #1F1A12)' : 'rgba(255,255,255,.5)'
    }
  }, CAP_LABEL[k]))));
}
function Changes({
  HOST,
  d
}) {
  const list = HOST.changes.list();
  const staged = list.filter(c => c.status === 'staged');
  return /*#__PURE__*/React.createElement(Section, {
    title: `Proposed changes${staged.length ? ` (${staged.length} staged)` : ''}`,
    sub: "Each is real source for its one home file. Apply writes it to disk (needs a connected writer); Copy hands you the snippet."
  }, !list.length && /*#__PURE__*/React.createElement("div", {
    className: "dsa-stub",
    style: {
      padding: 28,
      textAlign: 'center',
      border: '1px dashed var(--border-soft)',
      borderRadius: 'var(--r-lg)'
    }
  }, /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 13px var(--font-body)',
      color: 'var(--fg-muted)',
      margin: 0
    }
  }, "No changes yet. When Vi proposes one (or you call ", /*#__PURE__*/React.createElement("code", {
    style: {
      font: '600 12px var(--font-mono)',
      color: 'var(--accent-bronze)'
    }
  }, "ds.propose"), "), it appears here as reviewable source.")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gap: 12
    }
  }, list.map(c => /*#__PURE__*/React.createElement(ChangeRow, {
    key: c.id,
    c: c,
    HOST: HOST,
    canWrite: d.canWrite
  }))));
}
function ChangeRow({
  c,
  HOST,
  canWrite
}) {
  const [open, setOpen] = useState_br(false);
  const [busy, setBusy] = useState_br(false);
  const statusColor = {
    staged: 'var(--accent-bronze)',
    applied: 'var(--status-success,#2E7D32)',
    rejected: 'var(--fg-muted)'
  }[c.status];
  async function apply() {
    setBusy(true);
    try {
      await HOST.changes.apply(c.id);
      window.dsaToast?.('Written to ' + c.serialized.file);
    } catch (e) {
      window.dsaToast?.(e.message);
    }
    setBusy(false);
  }
  return /*#__PURE__*/React.createElement("div", {
    style: {
      border: '1px solid var(--border-soft)',
      borderRadius: 'var(--r-lg)',
      overflow: 'hidden',
      opacity: c.status === 'rejected' ? 0.5 : 1
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 12,
      padding: '12px 16px',
      background: 'var(--bg-surface)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      flex: 1,
      minWidth: 0
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("strong", {
    style: {
      font: '600 14px var(--font-body)',
      color: 'var(--fg-primary)'
    }
  }, c.title), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '600 10px var(--font-mono)',
      color: statusColor,
      textTransform: 'uppercase',
      letterSpacing: '0.06em'
    }
  }, c.status), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '500 11px var(--font-mono)',
      color: c.provenance === 'vi' ? 'var(--accent-gold-deep,#B7973C)' : 'var(--fg-muted)'
    }
  }, c.provenance)), /*#__PURE__*/React.createElement("div", {
    style: {
      font: '500 11.5px var(--font-mono)',
      color: 'var(--fg-muted)',
      marginTop: 2
    }
  }, "\u2192 ", c.serialized.file, " ", /*#__PURE__*/React.createElement("span", {
    style: {
      opacity: 0.6
    }
  }, "\xB7 ", c.serialized.strategy)), c.rationale && /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 12px/1.5 var(--font-body)',
      color: 'var(--fg-secondary)',
      margin: '4px 0 0'
    }
  }, c.rationale)), /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--ghost dsa-btn--sm",
    onClick: () => setOpen(o => !o)
  }, open ? 'Hide' : 'Source'), /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--ghost dsa-btn--sm",
    onClick: () => {
      navigator.clipboard?.writeText(c.serialized.source);
      window.dsaToast?.('Copied');
    }
  }, "Copy"), c.status === 'staged' && /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--solid dsa-btn--sm",
    disabled: !canWrite || busy,
    title: canWrite ? '' : 'Connect a writer first',
    onClick: apply
  }, busy ? 'Writing…' : 'Apply'), c.status === 'staged' && /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--ghost dsa-btn--sm",
    onClick: () => HOST.changes.reject(c.id)
  }, "\u2715")), open && /*#__PURE__*/React.createElement("pre", {
    style: {
      margin: 0,
      padding: '14px 16px',
      background: 'var(--bg-dark)',
      color: 'var(--fg-inverse)',
      font: '400 11.5px/1.55 var(--font-mono)',
      whiteSpace: 'pre',
      overflow: 'auto',
      maxHeight: '40vh'
    }
  }, c.serialized.source));
}
function Section({
  title,
  sub,
  children
}) {
  return /*#__PURE__*/React.createElement("section", {
    style: {
      marginTop: 28
    }
  }, /*#__PURE__*/React.createElement("h2", {
    style: {
      font: '600 16px var(--font-display)',
      color: 'var(--fg-primary)',
      margin: '0 0 3px'
    }
  }, title), sub && /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 12.5px/1.55 var(--font-body)',
      color: 'var(--fg-muted)',
      margin: '0 0 12px',
      maxWidth: 640
    }
  }, sub), children);
}
function Dot({
  on
}) {
  return /*#__PURE__*/React.createElement("span", {
    style: {
      width: 9,
      height: 9,
      borderRadius: 999,
      marginTop: 5,
      flex: 'none',
      background: on ? 'var(--status-success,#2E7D32)' : 'var(--border-strong,#c9bfa8)'
    }
  });
}
window.Bridge = Bridge;
})(); } catch (e) { __ds_ns.__errors.push({ path: "app/canvases/Bridge.jsx", error: String((e && e.message) || e) }); }

// app/canvases/Build.jsx
try { (() => {
// canvases/Build.jsx — cross-canvas Vi planner with 3-layer task tree
const {
  useState: useState_b,
  useEffect: useEffect_b,
  useRef: useRef_b
} = React;

// Template seeds the user can start from
const SEEDS = [{
  id: 'brochure',
  label: 'Property brochure',
  brief: 'A one-page property brochure for a 2-bed apartment with hero render, 4 stat tiles, description, price, and agent contact'
}, {
  id: 'palette',
  label: 'Marketing palette',
  brief: 'A 5-color palette for marketing emails that sits beside my brand gold'
}, {
  id: 'icons',
  label: 'Icons + colors for payments',
  brief: 'A new sub-system for handling payment flows: 6 icons (card, invoice, refund, etc.) and a 4-color status palette'
}, {
  id: 'voice',
  label: 'Voice for error states',
  brief: 'Three error message variants for upload failures, length-limit issues, and login problems'
}, {
  id: 'slide',
  label: 'Title slide',
  brief: 'A pitch-deck title slide composition with logo, headline, subheadline, and date'
}, {
  id: 'widget',
  label: 'Dashboard widget',
  brief: 'A hybrid dashboard widget showing occupancy, linked hubs, capture count, and a 13-week capture sparkline for Tower East'
}, {
  id: 'wizard',
  label: 'Onboarding wizard',
  brief: 'A 4-step onboarding flow — sign up, set up workspace, drop in logo for brand kit, invite teammates'
}];
function Build({
  initialBrief,
  onAdoptIcons,
  onAdoptColors,
  onSaveAsTemplate,
  onNav,
  onOpenInWorkshop
}) {
  const [brief, setBrief] = useState_b(initialBrief || SEEDS[0].brief);
  // stage: 1 = brief, 2 = plan review, 3 = generation, 4 = compose & adopt
  const [stage, setStage] = useState_b(1);
  const [planning, setPlanning] = useState_b(false);
  const [generating, setGenerating] = useState_b(false);
  const [composing, setComposing] = useState_b(false);
  const [plan, setPlan] = useState_b(null);
  const [error, setError] = useState_b(null);
  const [refining, setRefining] = useState_b(false);
  const [refineInput, setRefineInput] = useState_b('');
  const [refinements, setRefinements] = useState_b([]); // history of {message, changedKinds, ts}

  // If a brief gets pushed in from outside (e.g. from Templates), reset to stage 1 with that brief
  useEffect_b(() => {
    if (initialBrief) {
      setBrief(initialBrief);
      setStage(1);
      setPlan(null);
      setError(null);
    }
  }, [initialBrief]);
  const subtasksRef = useRef_b([]);
  subtasksRef.current = plan?.subtasks || [];
  const busy = planning || generating || composing || refining;
  async function generatePlan() {
    if (!brief.trim()) return;
    setPlanning(true);
    setError(null);
    setPlan(null);
    try {
      const planPrompt = `You are Vi, an AI planner inside ConceptV Studio. The user has given you a brief; your job is to decompose it into 2-4 parallel subtasks, each handled by a specialist sub-agent that touches ONE canvas of the design system.

The available sub-agents:
- icons-generator — generates 1-6 new SVG icons (24x24, 1.5px stroke, no fills, brand line style)
- colors-generator — generates a coherent palette of 3-6 named hex colors
- copy-writer — writes 1-3 short on-brand copy variants for a specific context (button/heading/body/error etc.)
- widget-builder — produces a ConceptV widget (dashboard tile / hub panel / partner embed) with title, KPIs, rows, CTA. Use when the brief mentions a dashboard tile, embedded card, hub widget, public-facing live data display.
- wizard-builder — produces a multi-step flow (Property Wizard, onboarding, signup, generic form). Use when the brief describes a step-by-step user flow.
- workshop-deck — produces a Workshop slide deck (multiple slides). Use when the brief mentions a pitch / investor / sales deck / all-hands / multiple slides.
- workshop-brochure — produces a one-page brochure. Use when the brief mentions a sell-sheet, A4 sheet, one-pager, property brochure.
- type-builder — registers a new Type in the universal Type Registry. Use when the user explicitly asks to create a new kind / system / template / archetype, or when the brief implies a reusable pattern (e.g. "we'll keep doing this for many properties"). Outputs the Type schema (name, layer, family, slots, defaults, variables).
- composer — composes a final output (a card preview, a slide preview, an asset listing) using whatever was generated above

Brief: "${brief.trim()}"

Plan the work. Output a JSON object describing:
- strategy: a one-sentence summary of your approach
- subtasks: an array of 2-4 subtasks. Each has:
  - kind: one of "icons-generator" | "colors-generator" | "copy-writer" | "widget-builder" | "wizard-builder" | "workshop-deck" | "workshop-brochure" | "composer"
  - label: a short human-readable task name (3-6 words)
  - brief: the specific brief you'd hand the sub-agent (1-2 sentences)

Always include exactly ONE composer subtask at the end, with a brief describing what the final output should look like (e.g. "Render a brochure card combining the icons + palette + copy" or "Hand off the generated widget for review").

If the brief asks for a Workshop doc (deck, brochure, widget, wizard) DIRECTLY (e.g. "make me an investor deck"), include the matching workshop-* / widget-builder / wizard-builder subtask alongside complementary subtasks (icons / colors / copy) if useful.

Respond as compact JSON only, no prose, no markdown fences.`;
      const planReply = await window.CV_AI.execute('build.plan', {
        params: {
          prompt: planPrompt
        },
        surface: 'build'
      });
      let planObj;
      try {
        planObj = JSON.parse(planReply);
      } catch {
        const m = String(planReply).match(/\{[\s\S]*\}/);
        if (m) {
          try {
            planObj = JSON.parse(m[0]);
          } catch {}
        }
      }
      if (!planObj || !Array.isArray(planObj.subtasks) || !planObj.subtasks.length) {
        throw new Error("Couldn't parse plan");
      }
      const subtasks = planObj.subtasks.map((s, i) => ({
        ...s,
        id: 'st-' + i,
        status: 'idle',
        result: null
      }));
      setPlan({
        strategy: planObj.strategy || '',
        subtasks
      });
      setStage(2);
    } catch (err) {
      setError(String(err.message || err));
    } finally {
      setPlanning(false);
    }
  }
  function updateSubtaskBrief(id, newBrief) {
    setPlan(p => ({
      ...p,
      subtasks: p.subtasks.map(s => s.id === id ? {
        ...s,
        brief: newBrief
      } : s)
    }));
  }
  function updateSubtaskLabel(id, newLabel) {
    setPlan(p => ({
      ...p,
      subtasks: p.subtasks.map(s => s.id === id ? {
        ...s,
        label: newLabel
      } : s)
    }));
  }
  function removeSubtask(id) {
    setPlan(p => ({
      ...p,
      subtasks: p.subtasks.filter(s => s.id !== id)
    }));
  }
  async function runGeneration() {
    if (!plan) return;
    setStage(3);
    setGenerating(true);
    setError(null);
    try {
      const composerIdx = plan.subtasks.findIndex(s => s.kind === 'composer');
      const nonComposers = plan.subtasks.filter((s, i) => i !== composerIdx);

      // mark all non-composers active, clear any prior results
      setPlan(p => ({
        ...p,
        subtasks: p.subtasks.map(s => s.kind !== 'composer' ? {
          ...s,
          status: 'active',
          result: null
        } : {
          ...s,
          status: 'idle',
          result: null
        })
      }));
      const results = await Promise.all(nonComposers.map(async s => {
        try {
          const r = await runSubtask(s, brief);
          setPlan(p => ({
            ...p,
            subtasks: p.subtasks.map(x => x.id === s.id ? {
              ...x,
              status: 'done',
              result: r
            } : x)
          }));
          return {
            id: s.id,
            kind: s.kind,
            label: s.label,
            result: r
          };
        } catch (err) {
          setPlan(p => ({
            ...p,
            subtasks: p.subtasks.map(x => x.id === s.id ? {
              ...x,
              status: 'blocked',
              result: {
                error: String(err.message || err)
              }
            } : x)
          }));
          return {
            id: s.id,
            kind: s.kind,
            label: s.label,
            result: {
              error: true
            }
          };
        }
      }));
      setGenerating(false);
      // auto-advance to compose
      await runCompose(results);
    } catch (err) {
      setError(String(err.message || err));
      setGenerating(false);
    }
  }
  async function runCompose(results) {
    setStage(4);
    setComposing(true);
    try {
      const composer = plan?.subtasks.find(s => s.kind === 'composer');
      if (composer) {
        setPlan(p => ({
          ...p,
          subtasks: p.subtasks.map(x => x.id === composer.id ? {
            ...x,
            status: 'active'
          } : x)
        }));
        try {
          const r = await runComposer(composer, brief, results);
          setPlan(p => ({
            ...p,
            subtasks: p.subtasks.map(x => x.id === composer.id ? {
              ...x,
              status: 'done',
              result: r
            } : x)
          }));
        } catch (err) {
          setPlan(p => ({
            ...p,
            subtasks: p.subtasks.map(x => x.id === composer.id ? {
              ...x,
              status: 'blocked',
              result: {
                error: String(err.message || err)
              }
            } : x)
          }));
        }
      }
    } finally {
      setComposing(false);
    }
  }
  async function recompose() {
    if (!plan) return;
    const parts = plan.subtasks.filter(s => s.kind !== 'composer').map(s => ({
      id: s.id,
      kind: s.kind,
      label: s.label,
      result: s.result
    }));
    await runCompose(parts);
  }
  function reset() {
    setStage(1);
    setPlan(null);
    setError(null);
    setRefinements([]);
    setRefineInput('');
  }
  function backToBrief() {
    if (busy) return;
    setStage(1);
  }
  function backToPlan() {
    if (busy) return;
    setStage(2);
  }
  async function refinePart(scope, message) {
    // scope: { kind: 'icon'|'color'|'copy'|'composed'|'icons-all'|'colors-all'|'copy-all', target?: name/index }
    if (!message || !plan) return;
    setRefining(true);
    try {
      const iconsSub = plan.subtasks.find(s => s.kind === 'icons-generator');
      const colorsSub = plan.subtasks.find(s => s.kind === 'colors-generator');
      const copySub = plan.subtasks.find(s => s.kind === 'copy-writer');
      const composerSub = plan.subtasks.find(s => s.kind === 'composer');
      const markActive = id => setPlan(p => ({
        ...p,
        subtasks: p.subtasks.map(x => x.id === id ? {
          ...x,
          status: 'active'
        } : x)
      }));
      const markDone = (id, result) => setPlan(p => ({
        ...p,
        subtasks: p.subtasks.map(x => x.id === id ? {
          ...x,
          status: 'done',
          result
        } : x)
      }));
      let changedLabel = '';

      // ===== Per-item: single icon =====
      if (scope.kind === 'icon' && iconsSub) {
        markActive(iconsSub.id);
        const existing = iconsSub.result?.icons || [];
        const target = existing.find(i => i.name === scope.target);
        if (!target) throw new Error('Icon not found');
        const prompt = `You are revising one icon in ConceptV's style (24×24, 1.5px stroke, no fills, currentColor).

Original icon: "${target.name}"
Current SVG body: ${target.body}

User wants this change: "${message}"

Return ONLY the new icon body (path/circle/rect markup that goes inside <svg viewBox="0 0 24 24">). No wrapper, no fill or stroke attributes.

Respond as compact JSON only:
{"name": "${target.name}", "body": "<new svg body>"}`;
        const reply = await window.CV_AI.complete(prompt);
        const parsed = parseJsonLoose(reply);
        if (parsed?.body) {
          const newIcons = existing.map(i => i.name === target.name ? {
            ...i,
            body: parsed.body
          } : i);
          markDone(iconsSub.id, {
            ...iconsSub.result,
            icons: newIcons
          });
          changedLabel = `icon "${target.name}"`;
        }
      }
      // ===== Per-item: single color =====
      else if (scope.kind === 'color' && colorsSub) {
        markActive(colorsSub.id);
        const existing = colorsSub.result?.colors || [];
        const target = existing.find(c => c.name === scope.target);
        if (!target) throw new Error('Color not found');
        const prompt = `You are revising one color in ConceptV's warm-ivory palette (gold #E0C010, bronze #988058, no cool greys).

Original: ${target.name} ${target.hex} (${target.role})
User wants: "${message}"

Return ONLY the new color. JSON only:
{"name": "${target.name}", "hex": "#...", "role": "..."}`;
        const reply = await window.CV_AI.complete(prompt);
        const parsed = parseJsonLoose(reply);
        if (parsed?.hex) {
          const newColors = existing.map(c => c.name === target.name ? {
            ...c,
            hex: parsed.hex,
            role: parsed.role || c.role
          } : c);
          markDone(colorsSub.id, {
            ...colorsSub.result,
            colors: newColors
          });
          changedLabel = `color "${target.name}"`;
        }
      }
      // ===== Per-item: single copy variant =====
      else if (scope.kind === 'copy' && copySub) {
        markActive(copySub.id);
        const existing = copySub.result?.variants || [];
        const idx = scope.target;
        const target = existing[idx];
        if (target == null) throw new Error('Variant not found');
        const prompt = `Rewrite this one copy variant in ConceptV's voice (sentence case, second person, no exclamation marks, no emoji).

Original: "${target}"
User wants: "${message}"

Return ONLY the new variant. JSON only:
{"variant": "..."}`;
        const reply = await window.CV_AI.complete(prompt);
        const parsed = parseJsonLoose(reply);
        if (parsed?.variant) {
          const newVariants = existing.map((v, i) => i === idx ? parsed.variant : v);
          markDone(copySub.id, {
            ...copySub.result,
            variants: newVariants
          });
          changedLabel = `copy variant ${idx + 1}`;
        }
      }
      // ===== Section-level: all icons / colors / copy =====
      else if (scope.kind === 'icons-all' && iconsSub) {
        markActive(iconsSub.id);
        try {
          const r = await runIcons(iconsSub.brief + ' — also: ' + message, brief);
          if (r && Array.isArray(r.icons) && r.icons.length) {
            markDone(iconsSub.id, r);
            changedLabel = 'all icons';
          } else {
            // Bad response — restore previous result, don't blank the section
            markDone(iconsSub.id, iconsSub.result);
            window.dsaToast?.('Vi returned no icons — kept the previous set');
          }
        } catch {
          markDone(iconsSub.id, iconsSub.result);
          window.dsaToast?.('Icon refine failed — kept the previous set');
        }
      } else if (scope.kind === 'colors-all' && colorsSub) {
        markActive(colorsSub.id);
        try {
          const r = await runColors(colorsSub.brief + ' — also: ' + message, brief);
          if (r && Array.isArray(r.colors) && r.colors.length) {
            markDone(colorsSub.id, r);
            changedLabel = 'all colors';
          } else {
            markDone(colorsSub.id, colorsSub.result);
            window.dsaToast?.('Vi returned no colors — kept the previous set');
          }
        } catch {
          markDone(colorsSub.id, colorsSub.result);
          window.dsaToast?.('Color refine failed — kept the previous set');
        }
      } else if (scope.kind === 'copy-all' && copySub) {
        markActive(copySub.id);
        try {
          const r = await runCopy(copySub.brief + ' — also: ' + message, brief);
          if (r && Array.isArray(r.variants) && r.variants.length) {
            markDone(copySub.id, r);
            changedLabel = 'all copy';
          } else {
            markDone(copySub.id, copySub.result);
            window.dsaToast?.('Vi returned no copy — kept the previous set');
          }
        } catch {
          markDone(copySub.id, copySub.result);
          window.dsaToast?.('Copy refine failed — kept the previous set');
        }
      }
      // ===== Composed-only: re-run just composer =====
      else if (scope.kind === 'composed' && composerSub) {
        // fall through to composer rerun below
        changedLabel = 'composition';
      }

      // Always re-run composer with up-to-date parts
      if (composerSub) {
        markActive(composerSub.id);
        // Use latest plan state
        const latestPlan = await new Promise(r => setPlan(p => {
          r(p);
          return p;
        }));
        const allParts = latestPlan.subtasks.filter(s => s.kind !== 'composer').map(s => ({
          id: s.id,
          kind: s.kind,
          label: s.label,
          result: s.result
        }));
        try {
          const r = await runComposer(composerSub, brief + ' (revised: ' + message + ')', allParts);
          markDone(composerSub.id, r);
        } catch {}
      }
      setRefinements(prev => [...prev, {
        message,
        summary: `Refined ${changedLabel || 'the output'}`,
        changedKinds: [changedLabel || scope.kind],
        ts: new Date().toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit'
        })
      }]);
      window.dsaToast?.(`Refined ${changedLabel || 'output'}`);
    } catch (err) {
      window.dsaToast?.('Refine failed: ' + (err.message || err));
    } finally {
      setRefining(false);
    }
  }
  async function refine() {
    const message = refineInput.trim();
    if (!message || !plan) return;
    setRefining(true);
    setRefineInput('');
    try {
      // Phase 1: ask Vi which subtasks to re-run, and with what new sub-briefs
      const partsSummary = plan.subtasks.map(s => {
        if (s.kind === 'icons-generator') return `[${s.kind}] ${s.label}\n  icons: ${(s.result?.icons || []).map(i => i.name).join(', ') || '(none)'}`;
        if (s.kind === 'colors-generator') return `[${s.kind}] ${s.label}\n  colors: ${(s.result?.colors || []).map(c => `${c.name} ${c.hex}`).join(', ') || '(none)'}`;
        if (s.kind === 'copy-writer') return `[${s.kind}] ${s.label}\n  variants:\n    ${(s.result?.variants || []).map((v, i) => `${i + 1}. ${v}`).join('\n    ')}`;
        if (s.kind === 'composer') return `[${s.kind}] ${s.label}\n  title: ${s.result?.title || ''}\n  body: ${s.result?.preview?.body || ''}`;
        return `[${s.kind}] ${s.label}`;
      }).join('\n\n');
      const triagePrompt = `You are revising a build. The original brief was: "${brief}"

Current parts:
${partsSummary}

The user wants this change: "${message}"

Decide which subtasks need to be re-run to make this change. For each, write a NEW sub-brief that captures both the original intent and the requested change. Return JSON only:
{
  "subtasks": [{"kind": "icons-generator|colors-generator|copy-writer", "newBrief": "..."}, ...],
  "summary": "<one-line description of what's changing>"
}

Always re-run the composer last (don't include it in subtasks — it's automatic). Only include subtasks that actually need to change. If only the copy needs an edit, only return copy-writer.`;
      const triageReply = await window.CV_AI.execute('build.triage', {
        params: {
          prompt: triagePrompt
        },
        surface: 'build'
      });
      let triage;
      try {
        triage = JSON.parse(triageReply);
      } catch {
        const m = String(triageReply).match(/\{[\s\S]*\}/);
        if (m) {
          try {
            triage = JSON.parse(m[0]);
          } catch {}
        }
      }
      if (!triage || !Array.isArray(triage.subtasks)) {
        throw new Error("Couldn't parse refinement plan");
      }

      // Map triage subtasks to existing plan subtasks by kind, override brief, mark active
      const targetKinds = new Set(triage.subtasks.map(t => t.kind));
      setPlan(p => ({
        ...p,
        subtasks: p.subtasks.map(s => {
          if (s.kind === 'composer') return {
            ...s,
            status: 'idle'
          };
          if (!targetKinds.has(s.kind)) return s;
          const t = triage.subtasks.find(x => x.kind === s.kind);
          return {
            ...s,
            brief: t.newBrief || s.brief,
            status: 'active',
            result: null
          };
        })
      }));

      // Re-run each affected subtask
      const affected = plan.subtasks.filter(s => targetKinds.has(s.kind));
      const newResults = await Promise.all(affected.map(async s => {
        const t = triage.subtasks.find(x => x.kind === s.kind);
        const newBrief = t.newBrief || s.brief;
        try {
          const r = await runSubtask({
            ...s,
            brief: newBrief
          }, brief + ' ' + message);
          setPlan(p => ({
            ...p,
            subtasks: p.subtasks.map(x => x.id === s.id ? {
              ...x,
              status: 'done',
              result: r
            } : x)
          }));
          return {
            id: s.id,
            kind: s.kind,
            label: s.label,
            result: r
          };
        } catch {
          setPlan(p => ({
            ...p,
            subtasks: p.subtasks.map(x => x.id === s.id ? {
              ...x,
              status: 'blocked'
            } : x)
          }));
          return {
            id: s.id,
            kind: s.kind,
            label: s.label,
            result: {
              error: true
            }
          };
        }
      }));

      // Always re-run composer with full context (kept parts + new parts)
      const composer = plan.subtasks.find(s => s.kind === 'composer');
      if (composer) {
        setPlan(p => ({
          ...p,
          subtasks: p.subtasks.map(x => x.id === composer.id ? {
            ...x,
            status: 'active'
          } : x)
        }));
        const allParts = plan.subtasks.filter(s => s.kind !== 'composer').map(s => {
          const updated = newResults.find(r => r.id === s.id);
          return {
            id: s.id,
            kind: s.kind,
            label: s.label,
            result: updated ? updated.result : s.result
          };
        });
        try {
          const r = await runComposer(composer, brief + ' (revised: ' + message + ')', allParts);
          setPlan(p => ({
            ...p,
            subtasks: p.subtasks.map(x => x.id === composer.id ? {
              ...x,
              status: 'done',
              result: r
            } : x)
          }));
        } catch {
          setPlan(p => ({
            ...p,
            subtasks: p.subtasks.map(x => x.id === composer.id ? {
              ...x,
              status: 'blocked'
            } : x)
          }));
        }
      }
      setRefinements(prev => [...prev, {
        message,
        summary: triage.summary || '',
        changedKinds: [...targetKinds],
        ts: new Date().toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit'
        })
      }]);
      window.dsaToast?.(`Applied "${message.slice(0, 30)}${message.length > 30 ? '…' : ''}"`);
    } catch (err) {
      window.dsaToast?.('Refinement failed: ' + (err.message || err));
    } finally {
      setRefining(false);
    }
  }
  const composerDone = plan?.subtasks.find(s => s.kind === 'composer')?.status === 'done';
  return /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(CanvasHeader, {
    title: "Build",
    sub: "Hand Vi a brief. It plans the work, hands subtasks to specialist agents, and assembles the result \u2014 drawing icons, colors, and copy from across your system.",
    actions: stage > 1 && /*#__PURE__*/React.createElement("button", {
      className: "dsa-btn dsa-btn--ghost",
      onClick: reset,
      disabled: busy
    }, "\u21BA Start over")
  }), /*#__PURE__*/React.createElement("div", {
    className: "dsa-canvas-body"
  }, /*#__PURE__*/React.createElement(Stepper, {
    stage: stage,
    planning: planning,
    generating: generating,
    composing: composing,
    composerDone: composerDone,
    onJumpTo: n => {
      if (busy) return;
      if (n < stage) setStage(n);
    }
  }), stage === 1 && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("div", {
    className: "dsa-section"
  }, /*#__PURE__*/React.createElement("div", {
    className: "dsa-section-head"
  }, /*#__PURE__*/React.createElement("h3", {
    className: "dsa-section-title"
  }, "1 \xB7 Write the brief"), /*#__PURE__*/React.createElement("span", {
    className: "dsa-section-meta"
  }, "Or pick a template to seed it")), /*#__PURE__*/React.createElement("div", {
    className: "dsa-card",
    style: {
      padding: 18
    }
  }, /*#__PURE__*/React.createElement("textarea", {
    style: {
      width: '100%',
      border: '1.5px solid var(--accent-gold)',
      borderRadius: 'var(--r-md)',
      padding: '12px 14px',
      background: 'var(--bg-canvas)',
      outline: 'none',
      font: '400 14px/1.55 var(--font-body)',
      color: 'var(--fg-primary)',
      resize: 'vertical',
      minHeight: 80,
      fontFamily: 'var(--font-body)',
      boxSizing: 'border-box'
    },
    rows: "3",
    placeholder: "What do you want to build?",
    value: brief,
    onChange: e => setBrief(e.target.value),
    disabled: planning
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 6,
      flexWrap: 'wrap',
      marginTop: 14
    }
  }, SEEDS.map(s => /*#__PURE__*/React.createElement("button", {
    key: s.id,
    disabled: planning,
    style: {
      background: 'transparent',
      border: '1px solid var(--border-default)',
      borderRadius: 999,
      padding: '6px 14px',
      cursor: planning ? 'not-allowed' : 'pointer',
      font: '500 12px/1 var(--font-body)',
      color: 'var(--fg-secondary)',
      opacity: planning ? 0.5 : 1
    },
    onClick: () => setBrief(s.brief)
  }, s.label))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 8,
      marginTop: 14
    }
  }, /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--ai",
    onClick: generatePlan,
    disabled: !brief.trim() || planning
  }, /*#__PURE__*/React.createElement(ViShape, {
    size: 14,
    animated: planning
  }), " ", planning ? 'Planning…' : 'Generate plan →'), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 11px/1 var(--font-body)',
      color: 'var(--fg-muted)'
    }
  }, "Vi will decompose this brief into specialist subtasks for you to review.")))), /*#__PURE__*/React.createElement("div", {
    className: "dsa-section",
    style: {
      marginTop: 8
    }
  }, /*#__PURE__*/React.createElement("div", {
    className: "dsa-section-head"
  }, /*#__PURE__*/React.createElement("h3", {
    className: "dsa-section-title"
  }, "How Build works")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(4, 1fr)',
      gap: 12
    }
  }, /*#__PURE__*/React.createElement(BuildHowCard, {
    layer: "1",
    title: "Brief",
    desc: "Tell Vi what you want to make. Start from a template or write it yourself."
  }), /*#__PURE__*/React.createElement(BuildHowCard, {
    layer: "2",
    title: "Plan",
    desc: "Vi decomposes the brief into 2-4 specialist subtasks \u2014 one per canvas. You review and tweak before anything runs."
  }), /*#__PURE__*/React.createElement(BuildHowCard, {
    layer: "3",
    title: "Generate",
    desc: "The subtasks run in parallel: icons, colors, copy. Each lights up live as it completes."
  }), /*#__PURE__*/React.createElement(BuildHowCard, {
    layer: "4",
    title: "Compose",
    desc: "A composer agent assembles the parts into a final preview you can refine, adopt, or save as a template."
  })))), stage === 2 && plan && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("div", {
    className: "dsa-section"
  }, /*#__PURE__*/React.createElement("div", {
    className: "dsa-section-head"
  }, /*#__PURE__*/React.createElement("h3", {
    className: "dsa-section-title"
  }, "2 \xB7 Review the plan"), /*#__PURE__*/React.createElement("span", {
    className: "dsa-section-meta"
  }, "Edit any subtask brief, remove what you don't need, or regenerate the plan")), plan.strategy && /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--accent-gold-faint)',
      borderLeft: '3px solid var(--accent-gold)',
      borderRadius: 'var(--r-sm)',
      padding: '10px 14px',
      marginBottom: 14,
      display: 'flex',
      gap: 10,
      alignItems: 'flex-start'
    }
  }, /*#__PURE__*/React.createElement(ViShape, {
    size: 14
  }), /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      font: '700 10px/1 var(--font-body)',
      color: 'var(--accent-bronze)',
      letterSpacing: '0.08em',
      textTransform: 'uppercase',
      marginBottom: 4
    }
  }, "Vi's strategy"), /*#__PURE__*/React.createElement("div", {
    style: {
      font: '400 13px/1.5 var(--font-body)',
      color: 'var(--fg-primary)'
    }
  }, plan.strategy))), /*#__PURE__*/React.createElement(PlanEditor, {
    plan: plan,
    onChangeBrief: updateSubtaskBrief,
    onChangeLabel: updateSubtaskLabel,
    onRemove: removeSubtask
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 8,
      marginTop: 14,
      alignItems: 'center'
    }
  }, /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--ai",
    onClick: runGeneration,
    disabled: busy || !plan.subtasks.length
  }, /*#__PURE__*/React.createElement(ViShape, {
    size: 14
  }), " Approve plan & generate \u2192"), /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--outline",
    onClick: generatePlan,
    disabled: planning
  }, "\u21BB Regenerate plan"), /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--ghost",
    onClick: backToBrief,
    disabled: busy
  }, "\u2190 Edit brief"), /*#__PURE__*/React.createElement("span", {
    style: {
      marginLeft: 'auto',
      font: '400 11px/1 var(--font-body)',
      color: 'var(--fg-muted)'
    }
  }, plan.subtasks.filter(s => s.kind !== 'composer').length, " parallel subtasks \xB7 1 composer")))), stage === 3 && plan && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("div", {
    className: "dsa-section"
  }, /*#__PURE__*/React.createElement("div", {
    className: "dsa-section-head"
  }, /*#__PURE__*/React.createElement("h3", {
    className: "dsa-section-title"
  }, "3 \xB7 ", generating ? 'Vi is generating…' : 'Generation complete'), plan.strategy && /*#__PURE__*/React.createElement("span", {
    className: "dsa-section-meta",
    style: {
      color: 'var(--fg-secondary)',
      font: '400 12px/1.4 var(--font-body)'
    }
  }, plan.strategy)), /*#__PURE__*/React.createElement(TaskList, {
    subtasks: plan.subtasks
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 8,
      marginTop: 14,
      alignItems: 'center'
    }
  }, !generating && /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--ai",
    onClick: async () => {
      const parts = plan.subtasks.filter(s => s.kind !== 'composer').map(s => ({
        id: s.id,
        kind: s.kind,
        label: s.label,
        result: s.result
      }));
      await runCompose(parts);
    },
    disabled: busy
  }, /*#__PURE__*/React.createElement(ViShape, {
    size: 14
  }), " Compose final output \u2192"), !generating && /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--outline",
    onClick: runGeneration,
    disabled: busy
  }, "\u21BB Re-run generation"), !generating && /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--ghost",
    onClick: backToPlan,
    disabled: busy
  }, "\u2190 Edit plan")), /*#__PURE__*/React.createElement(PartsPreview, {
    plan: plan
  }))), stage === 4 && plan && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("div", {
    className: "dsa-section"
  }, /*#__PURE__*/React.createElement("div", {
    className: "dsa-section-head"
  }, /*#__PURE__*/React.createElement("h3", {
    className: "dsa-section-title"
  }, "4 \xB7 ", composing ? 'Vi is composing…' : 'Output'), /*#__PURE__*/React.createElement("span", {
    className: "dsa-section-meta"
  }, "Adopt parts into your system, copy text, or save the whole run as a reusable template"), /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--ghost dsa-btn--sm",
    style: {
      marginLeft: 'auto'
    },
    onClick: backToPlan,
    disabled: busy
  }, "\u2190 Edit plan")), composing && /*#__PURE__*/React.createElement("div", {
    className: "dsa-gen-loading",
    style: {
      margin: '0 0 14px'
    }
  }, /*#__PURE__*/React.createElement(ViShape, {
    size: 16,
    animated: true
  }), " Composing final output from the generated parts\u2026"), /*#__PURE__*/React.createElement(Output, {
    plan: plan,
    brief: brief,
    onAdoptIcons: onAdoptIcons,
    onAdoptColors: onAdoptColors,
    onSaveAsTemplate: onSaveAsTemplate,
    onNav: onNav,
    onOpenInWorkshop: onOpenInWorkshop,
    onRefinePart: refinePart,
    refining: refining
  }), "}/>"), !composing && composerDone && /*#__PURE__*/React.createElement("div", {
    className: "dsa-section"
  }, /*#__PURE__*/React.createElement("div", {
    className: "dsa-section-head"
  }, /*#__PURE__*/React.createElement("h3", {
    className: "dsa-section-title"
  }, "Refine with Vi"), /*#__PURE__*/React.createElement("span", {
    className: "dsa-section-meta"
  }, "Ask for changes \u2014 Vi decides which subtasks to re-run and updates the output in place")), /*#__PURE__*/React.createElement("div", {
    className: "dsa-card",
    style: {
      padding: 18
    }
  }, refinements.length > 0 && /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 8,
      marginBottom: 14
    }
  }, refinements.map((r, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    style: {
      padding: '10px 12px',
      background: 'var(--accent-gold-faint)',
      borderRadius: 'var(--r-sm)',
      borderLeft: '3px solid var(--accent-gold)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 8,
      marginBottom: 4
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: '700 10px/1 var(--font-body)',
      color: 'var(--accent-bronze)',
      letterSpacing: '0.08em',
      textTransform: 'uppercase'
    }
  }, "Revision ", i + 1), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '500 11px/1 var(--font-body)',
      color: 'var(--fg-muted)'
    }
  }, r.ts), /*#__PURE__*/React.createElement("span", {
    style: {
      marginLeft: 'auto',
      font: '500 10px/1 var(--font-body)',
      color: 'var(--fg-muted)'
    }
  }, r.changedKinds.length ? `re-ran ${r.changedKinds.join(', ')}` : '')), /*#__PURE__*/React.createElement("div", {
    style: {
      font: '400 13px/1.4 var(--font-body)',
      color: 'var(--fg-primary)',
      marginBottom: r.summary ? 4 : 0
    }
  }, r.message), r.summary && /*#__PURE__*/React.createElement("div", {
    style: {
      font: '400 11px/1.4 var(--font-body)',
      color: 'var(--fg-secondary)',
      fontStyle: 'italic'
    }
  }, r.summary)))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 8,
      alignItems: 'flex-end'
    }
  }, /*#__PURE__*/React.createElement(ViShape, {
    size: 28,
    animated: refining
  }), /*#__PURE__*/React.createElement("textarea", {
    value: refineInput,
    onChange: e => setRefineInput(e.target.value),
    onKeyDown: e => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        refine();
      }
    },
    placeholder: "Ask for changes. e.g. \"Make the icons more rounded\", \"Use a cooler palette\", \"Shorten the body copy\", \"Add a card icon\"",
    rows: "2",
    disabled: refining,
    style: {
      flex: 1,
      border: '1.5px solid var(--accent-gold)',
      borderRadius: 'var(--r-md)',
      padding: '10px 12px',
      background: 'var(--bg-canvas)',
      outline: 'none',
      font: '400 13px/1.55 var(--font-body)',
      color: 'var(--fg-primary)',
      resize: 'vertical',
      minHeight: 48,
      fontFamily: 'var(--font-body)',
      opacity: refining ? 0.6 : 1
    }
  }), /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--ai",
    onClick: refine,
    disabled: refining || !refineInput.trim()
  }, /*#__PURE__*/React.createElement(ViShape, {
    size: 14
  }), " ", refining ? 'Iterating…' : 'Refine')), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 8,
      marginTop: 10,
      flexWrap: 'wrap'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: '400 11px/1.6 var(--font-body)',
      color: 'var(--fg-muted)'
    }
  }, "Try:"), ['Make the icons rounder', 'Cooler palette', 'Shorten the copy', 'Add a payment icon', 'Use a darker accent'].map(s => /*#__PURE__*/React.createElement("button", {
    key: s,
    disabled: refining,
    onClick: () => setRefineInput(s),
    style: {
      background: 'transparent',
      border: '1px solid var(--border-default)',
      borderRadius: 999,
      padding: '4px 10px',
      cursor: refining ? 'not-allowed' : 'pointer',
      font: '500 11px/1 var(--font-body)',
      color: 'var(--fg-secondary)',
      opacity: refining ? 0.5 : 1
    }
  }, s)))))), error && /*#__PURE__*/React.createElement("div", {
    className: "dsa-stub",
    style: {
      marginTop: 14
    }
  }, /*#__PURE__*/React.createElement("h3", null, "Something went wrong"), /*#__PURE__*/React.createElement("p", null, error), /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--outline",
    onClick: reset
  }, "Start over"))));
}
function Stepper({
  stage,
  planning,
  generating,
  composing,
  composerDone,
  onJumpTo
}) {
  const steps = [{
    n: 1,
    label: 'Brief',
    sub: 'Tell Vi what you want'
  }, {
    n: 2,
    label: 'Plan',
    sub: 'Review the decomposition'
  }, {
    n: 3,
    label: 'Generate',
    sub: 'Run parallel subtasks'
  }, {
    n: 4,
    label: 'Compose',
    sub: 'Assemble & adopt'
  }];
  // Determine running step
  let running = 0;
  if (planning && stage === 1) running = 1;else if (planning) running = 2;else if (generating) running = 3;else if (composing) running = 4;
  return /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'stretch',
      gap: 0,
      marginBottom: 24,
      background: 'var(--bg-surface)',
      border: '1px solid var(--border-default)',
      borderRadius: 'var(--r-md)',
      padding: 6,
      overflow: 'hidden'
    }
  }, steps.map((s, i) => {
    const isActive = s.n === stage;
    const isDone = s.n < stage;
    const isRunning = running === s.n;
    const isClickable = isDone && onJumpTo;
    const color = isActive ? 'var(--accent-gold)' : isDone ? 'var(--status-success)' : 'var(--fg-muted)';
    return /*#__PURE__*/React.createElement(React.Fragment, {
      key: s.n
    }, /*#__PURE__*/React.createElement("button", {
      type: "button",
      onClick: () => isClickable && onJumpTo(s.n),
      disabled: !isClickable,
      style: {
        flex: 1,
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        padding: '10px 14px',
        background: isActive ? 'var(--accent-gold-faint)' : 'transparent',
        border: 'none',
        borderRadius: 'var(--r-sm)',
        cursor: isClickable ? 'pointer' : 'default',
        textAlign: 'left',
        minWidth: 0,
        transition: 'background 150ms var(--ease-out)'
      },
      title: isClickable ? 'Jump back to this step' : ''
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        width: 26,
        height: 26,
        borderRadius: '50%',
        background: isActive ? 'var(--accent-gold)' : isDone ? 'var(--status-success)' : 'transparent',
        border: isActive || isDone ? 'none' : '1.5px solid var(--border-default)',
        color: isActive || isDone ? '#fff' : 'var(--fg-muted)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        font: '700 12px/1 var(--font-body)',
        flex: 'none',
        animation: isRunning ? 'dsa-pulse 1.2s ease-in-out infinite' : 'none'
      }
    }, isDone ? '✓' : s.n), /*#__PURE__*/React.createElement("span", {
      style: {
        minWidth: 0,
        display: 'flex',
        flexDirection: 'column'
      }
    }, /*#__PURE__*/React.createElement("span", {
      style: {
        font: '700 12px/1.1 var(--font-display)',
        color: isActive ? 'var(--accent-bronze)' : isDone ? 'var(--fg-primary)' : 'var(--fg-muted)',
        letterSpacing: '0.02em',
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis'
      }
    }, s.label), /*#__PURE__*/React.createElement("span", {
      style: {
        font: '400 10px/1.3 var(--font-body)',
        color: 'var(--fg-muted)',
        marginTop: 2,
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis'
      }
    }, s.sub))), i < steps.length - 1 && /*#__PURE__*/React.createElement("span", {
      style: {
        alignSelf: 'center',
        flex: 'none',
        width: 18,
        height: 1,
        background: s.n < stage ? 'var(--status-success)' : 'var(--border-default)',
        margin: '0 2px'
      }
    }));
  }));
}
const SUBTASK_META = {
  'icons-generator': {
    tone: '#6E5BBE',
    label: 'Icons generator'
  },
  'colors-generator': {
    tone: '#B3793A',
    label: 'Colors generator'
  },
  'copy-writer': {
    tone: '#3A7F6E',
    label: 'Copy writer'
  },
  'widget-builder': {
    tone: '#1F1A12',
    label: 'Widget builder'
  },
  'wizard-builder': {
    tone: '#988058',
    label: 'Wizard builder'
  },
  'workshop-deck': {
    tone: '#E0C010',
    label: 'Deck builder'
  },
  'workshop-brochure': {
    tone: '#E0C010',
    label: 'Brochure builder'
  },
  'type-builder': {
    tone: '#5B4628',
    label: 'Type builder'
  },
  'composer': {
    tone: 'var(--accent-bronze)',
    label: 'Composer'
  }
};
function PlanEditor({
  plan,
  onChangeBrief,
  onChangeLabel,
  onRemove
}) {
  const others = plan.subtasks.filter(s => s.kind !== 'composer');
  const composer = plan.subtasks.find(s => s.kind === 'composer');
  return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: `repeat(${Math.min(Math.max(others.length, 1), 3)}, 1fr)`,
      gap: 10
    }
  }, others.map(s => /*#__PURE__*/React.createElement(PlanEditorCard, {
    key: s.id,
    sub: s,
    onChangeBrief: onChangeBrief,
    onChangeLabel: onChangeLabel,
    onRemove: onRemove,
    removable: true
  }))), composer && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'center',
      padding: '6px 0'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: 2,
      height: 18,
      background: 'var(--accent-gold)',
      opacity: 0.5,
      display: 'block'
    }
  })), /*#__PURE__*/React.createElement(PlanEditorCard, {
    sub: composer,
    onChangeBrief: onChangeBrief,
    onChangeLabel: onChangeLabel,
    onRemove: onRemove,
    removable: false,
    wide: true
  })));
}
function PlanEditorCard({
  sub,
  onChangeBrief,
  onChangeLabel,
  onRemove,
  removable,
  wide
}) {
  const meta = SUBTASK_META[sub.kind] || {
    tone: 'var(--fg-muted)',
    label: sub.kind
  };
  return /*#__PURE__*/React.createElement("div", {
    style: {
      background: 'var(--bg-surface)',
      border: '1.5px solid var(--border-default)',
      borderRadius: 'var(--r-md)',
      padding: '12px 14px',
      width: wide ? '100%' : 'auto',
      display: 'flex',
      flexDirection: 'column',
      gap: 6
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 6
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: 8,
      height: 8,
      borderRadius: 2,
      background: meta.tone,
      flex: 'none'
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '700 10px/1 var(--font-body)',
      color: meta.tone,
      letterSpacing: '0.06em',
      textTransform: 'uppercase'
    }
  }, meta.label), removable && /*#__PURE__*/React.createElement("button", {
    type: "button",
    onClick: () => onRemove(sub.id),
    title: "Remove this subtask",
    style: {
      marginLeft: 'auto',
      background: 'transparent',
      border: 'none',
      color: 'var(--fg-muted)',
      cursor: 'pointer',
      padding: 2,
      lineHeight: 1,
      font: '500 14px/1 var(--font-body)'
    }
  }, "\xD7")), /*#__PURE__*/React.createElement("input", {
    value: sub.label,
    onChange: e => onChangeLabel(sub.id, e.target.value),
    style: {
      border: 'none',
      background: 'transparent',
      padding: 0,
      outline: 'none',
      font: '600 13px/1.2 var(--font-display)',
      color: 'var(--fg-primary)',
      width: '100%'
    }
  }), /*#__PURE__*/React.createElement("textarea", {
    value: sub.brief,
    onChange: e => onChangeBrief(sub.id, e.target.value),
    rows: wide ? 2 : 3,
    style: {
      border: '1px solid var(--border-default)',
      borderRadius: 'var(--r-sm)',
      background: 'var(--bg-canvas)',
      padding: '8px 10px',
      outline: 'none',
      font: '400 12px/1.45 var(--font-body)',
      color: 'var(--fg-secondary)',
      resize: 'vertical',
      fontFamily: 'var(--font-body)',
      boxSizing: 'border-box',
      width: '100%',
      minHeight: 60
    }
  }));
}
function PartsPreview({
  plan
}) {
  const icons = plan.subtasks.find(s => s.kind === 'icons-generator' && s.result && !s.result.error)?.result;
  const colors = plan.subtasks.find(s => s.kind === 'colors-generator' && s.result && !s.result.error)?.result;
  const copy = plan.subtasks.find(s => s.kind === 'copy-writer' && s.result && !s.result.error)?.result;
  const typeDrafts = plan.subtasks.filter(s => s.kind === 'type-builder' && s.result?.kind === 'type-draft');
  if (!icons && !colors && !copy && !typeDrafts.length) return null;
  return /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: 18,
      padding: 16,
      background: 'var(--bg-surface)',
      border: '1px dashed var(--border-default)',
      borderRadius: 'var(--r-md)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      font: '700 10px/1 var(--font-body)',
      color: 'var(--fg-muted)',
      letterSpacing: '0.08em',
      textTransform: 'uppercase',
      marginBottom: 10
    }
  }, "Generated so far"), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: 16
    }
  }, icons && icons.icons && /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      font: '600 11px/1 var(--font-body)',
      color: 'var(--fg-secondary)',
      marginBottom: 6
    }
  }, "Icons \xB7 ", icons.icons.length), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 6,
      flexWrap: 'wrap'
    }
  }, icons.icons.map((ic, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    title: ic.name,
    style: {
      width: 32,
      height: 32,
      borderRadius: 'var(--r-sm)',
      background: 'var(--bg-canvas)',
      border: '1px solid var(--border-default)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center'
    }
  }, /*#__PURE__*/React.createElement("svg", {
    viewBox: "0 0 24 24",
    width: "20",
    height: "20",
    fill: "none",
    stroke: "var(--accent-bronze)",
    strokeWidth: "1.5",
    strokeLinecap: "round",
    strokeLinejoin: "round",
    dangerouslySetInnerHTML: {
      __html: ic.body
    }
  }))))), colors && colors.colors && /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      font: '600 11px/1 var(--font-body)',
      color: 'var(--fg-secondary)',
      marginBottom: 6
    }
  }, "Colors \xB7 ", colors.colors.length), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      gap: 0,
      borderRadius: 'var(--r-sm)',
      overflow: 'hidden',
      border: '1px solid var(--border-default)'
    }
  }, colors.colors.map((c, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    title: `${c.name} · ${c.hex}`,
    style: {
      flex: 1,
      height: 32,
      background: c.hex
    }
  })))), copy && copy.variants && /*#__PURE__*/React.createElement("div", {
    style: {
      gridColumn: '1 / -1'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      font: '600 11px/1 var(--font-body)',
      color: 'var(--fg-secondary)',
      marginBottom: 6
    }
  }, "Copy \xB7 ", copy.variants.length), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      flexDirection: 'column',
      gap: 4
    }
  }, copy.variants.map((v, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    style: {
      font: '400 12px/1.5 var(--font-body)',
      color: 'var(--fg-primary)',
      padding: '6px 10px',
      background: 'var(--bg-canvas)',
      border: '1px solid var(--border-default)',
      borderRadius: 'var(--r-sm)'
    }
  }, v)))), typeDrafts.length > 0 && /*#__PURE__*/React.createElement("div", {
    style: {
      gridColumn: '1 / -1'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      font: '600 11px/1 var(--font-body)',
      color: 'var(--fg-secondary)',
      marginBottom: 6
    }
  }, "New Types \xB7 ", typeDrafts.length), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
      gap: 8
    }
  }, typeDrafts.map(s => {
    const d = s.result.draft;
    return /*#__PURE__*/React.createElement("div", {
      key: s.id,
      style: {
        padding: 12,
        background: 'var(--bg-canvas)',
        border: '1px dashed var(--accent-gold)',
        borderRadius: 'var(--r-sm)'
      }
    }, /*#__PURE__*/React.createElement("div", {
      style: {
        display: 'flex',
        alignItems: 'center',
        gap: 6,
        marginBottom: 4
      }
    }, window.TypeLayerBadge && /*#__PURE__*/React.createElement(window.TypeLayerBadge, {
      layer: d.layer,
      size: "sm"
    }), /*#__PURE__*/React.createElement("strong", {
      style: {
        font: '700 12px/1.1 var(--font-display)',
        color: 'var(--fg-primary)'
      }
    }, d.name)), /*#__PURE__*/React.createElement("p", {
      style: {
        margin: 0,
        font: '400 11px/1.4 var(--font-body)',
        color: 'var(--fg-secondary)'
      }
    }, d.description), /*#__PURE__*/React.createElement("button", {
      className: "dsa-btn dsa-btn--ai dsa-btn--sm",
      style: {
        marginTop: 8
      },
      onClick: () => {
        window.CV_TYPES_PROMPT.open(d);
      }
    }, /*#__PURE__*/React.createElement(ViShape, {
      size: 10
    }), " Review & register"));
  })))));
}
function BuildHowCard({
  layer,
  title,
  desc
}) {
  return /*#__PURE__*/React.createElement("div", {
    className: "dsa-card"
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 8,
      marginBottom: 6
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      background: 'var(--accent-gold-faint)',
      color: 'var(--accent-bronze)',
      font: '700 10px/1 var(--font-body)',
      letterSpacing: '0.08em',
      textTransform: 'uppercase',
      padding: '4px 8px',
      borderRadius: 'var(--r-sm)'
    }
  }, "Layer ", layer), /*#__PURE__*/React.createElement("h4", {
    style: {
      font: '700 14px/1 var(--font-display)',
      color: 'var(--fg-primary)',
      margin: 0
    }
  }, title)), /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 12px/1.55 var(--font-body)',
      color: 'var(--fg-secondary)',
      margin: 0
    }
  }, desc));
}
function TaskList({
  subtasks
}) {
  // Composer is always last; non-composers display as parallel row
  const composer = subtasks.find(s => s.kind === 'composer');
  const others = subtasks.filter(s => s.kind !== 'composer');
  return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: `repeat(${Math.max(others.length, 1)}, 1fr)`,
      gap: 8,
      marginBottom: composer ? 10 : 0
    }
  }, others.map(s => /*#__PURE__*/React.createElement(TaskNode, {
    key: s.id,
    sub: s
  }))), composer && /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      justifyContent: 'center',
      padding: '2px 0'
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: 2,
      height: 14,
      background: 'var(--accent-gold-dashed)',
      display: 'block'
    }
  })), /*#__PURE__*/React.createElement(TaskNode, {
    sub: composer,
    wide: true
  })));
}
function TaskNode({
  sub,
  wide
}) {
  const stateColor = sub.status === 'active' ? 'var(--accent-gold)' : sub.status === 'done' ? 'var(--status-success)' : sub.status === 'blocked' ? 'var(--status-error)' : 'var(--fg-muted)';
  return /*#__PURE__*/React.createElement("div", {
    style: {
      background: sub.status === 'active' ? 'var(--accent-gold-faint)' : 'var(--bg-surface)',
      borderRadius: 'var(--r-md)',
      border: '1.5px solid ' + (sub.status === 'active' ? 'var(--accent-gold)' : sub.status === 'blocked' ? 'var(--status-error)' : 'var(--border-default)'),
      padding: '12px 14px',
      width: wide ? '100%' : 'auto',
      opacity: sub.status === 'idle' ? 0.55 : 1,
      transition: 'all 200ms var(--ease-out)'
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'center',
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      width: 8,
      height: 8,
      borderRadius: '50%',
      background: stateColor,
      animation: sub.status === 'active' ? 'dsa-pulse 1.2s ease-in-out infinite' : 'none'
    }
  }), /*#__PURE__*/React.createElement("span", {
    style: {
      font: '700 10px/1 var(--font-body)',
      color: 'var(--accent-bronze)',
      letterSpacing: '0.06em',
      textTransform: 'uppercase'
    }
  }, sub.kind)), /*#__PURE__*/React.createElement("div", {
    style: {
      font: '600 13px/1.2 var(--font-display)',
      color: 'var(--fg-primary)',
      marginTop: 6
    }
  }, sub.label), /*#__PURE__*/React.createElement("div", {
    style: {
      font: '400 11px/1.4 var(--font-body)',
      color: 'var(--fg-secondary)',
      marginTop: 4
    }
  }, sub.brief));
}
function Output({
  plan,
  brief,
  onAdoptIcons,
  onAdoptColors,
  onSaveAsTemplate,
  onNav,
  onOpenInWorkshop,
  onRefinePart,
  refining
}) {
  const icons = plan.subtasks.find(s => s.kind === 'icons-generator' && s.result && !s.result.error)?.result;
  const colors = plan.subtasks.find(s => s.kind === 'colors-generator' && s.result && !s.result.error)?.result;
  const copy = plan.subtasks.find(s => s.kind === 'copy-writer' && s.result && !s.result.error)?.result;
  const composed = plan.subtasks.find(s => s.kind === 'composer' && s.result && !s.result.error)?.result;
  // Workshop-doc subtask outputs (widget, wizard, deck, brochure)
  const workshopDocResults = plan.subtasks.filter(s => s.result?.kind === 'workshop-doc' && !s.result.error);
  const [saving, setSaving] = useState_b(false);
  const [saved, setSaved] = useState_b(false);
  async function saveTemplate() {
    setSaving(true);
    try {
      // Ask Vi to extract parameters from the brief
      const prompt = `Given this build brief, identify the 1-3 parameters most worth turning into reusable inputs. Replace each in the brief with {{paramKey}} placeholders.

Brief: "${brief}"

Respond as compact JSON only, no prose:
{"name": "<short template name 2-5 words>", "description": "<one-line description>", "pattern": "<brief with {{params}} substituted>", "params":[{"key":"camelCase","label":"Human label","default":"original value"}]}`;
      const reply = await window.CV_AI.complete(prompt);
      let parsed = null;
      try {
        parsed = JSON.parse(reply);
      } catch {
        const m = String(reply).match(/\{[\s\S]*\}/);
        if (m) {
          try {
            parsed = JSON.parse(m[0]);
          } catch {}
        }
      }
      if (!parsed) {
        // Fallback: no parameters extracted
        parsed = {
          name: (composed?.title || 'Untitled template').slice(0, 40),
          description: composed?.summary || brief.slice(0, 80),
          pattern: brief,
          params: []
        };
      }
      onSaveAsTemplate({
        id: 'tpl-' + Date.now(),
        name: parsed.name,
        description: parsed.description,
        briefPattern: parsed.pattern || brief,
        params: parsed.params || [],
        savedAt: new Date().toLocaleDateString()
      });
      setSaved(true);
      window.dsaToast?.(`Saved "${parsed.name}" to Templates`);
    } catch {
      window.dsaToast?.('Save failed');
    } finally {
      setSaving(false);
    }
  }
  return /*#__PURE__*/React.createElement("div", {
    className: "dsa-card",
    style: {
      padding: 22
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      gap: 12,
      marginBottom: 14
    }
  }, composed?.title && /*#__PURE__*/React.createElement("h3", {
    style: {
      font: '700 22px/1.1 var(--font-display)',
      color: 'var(--accent-bronze)',
      margin: 0,
      letterSpacing: '-0.02em',
      flex: 1
    }
  }, composed.title), /*#__PURE__*/React.createElement("button", {
    className: `dsa-btn ${saved ? 'dsa-btn--outline' : 'dsa-btn--ai'} dsa-btn--sm`,
    onClick: saveTemplate,
    disabled: saving || saved
  }, saved ? '✓ Saved' : saving ? 'Saving…' : /*#__PURE__*/React.createElement(React.Fragment, null, /*#__PURE__*/React.createElement(ViShape, {
    size: 12
  }), " Save as template")), !saved && onNav && /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--primary dsa-btn--sm",
    onClick: async () => {
      await saveTemplate();
      setTimeout(() => onNav('templates'), 200);
    },
    disabled: saving
  }, "Save & open \u2192")), composed?.summary && /*#__PURE__*/React.createElement("p", {
    style: {
      font: '400 13px/1.55 var(--font-body)',
      color: 'var(--fg-secondary)',
      margin: '0 0 16px'
    }
  }, composed.summary), composed?.preview && /*#__PURE__*/React.createElement(ComposedPreview, {
    preview: composed.preview,
    icons: icons?.icons || [],
    colors: colors?.colors || [],
    copy: copy?.variants || []
  }), workshopDocResults.length > 0 && /*#__PURE__*/React.createElement("div", {
    style: {
      marginTop: composed?.preview ? 18 : 0,
      marginBottom: 18
    }
  }, /*#__PURE__*/React.createElement("div", {
    style: {
      font: '600 11px/1 var(--font-body)',
      color: 'var(--fg-muted)',
      letterSpacing: '0.08em',
      textTransform: 'uppercase',
      marginBottom: 10
    }
  }, "Workshop docs \xB7 ", workshopDocResults.length), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
      gap: 10
    }
  }, workshopDocResults.map(s => /*#__PURE__*/React.createElement(WorkshopDocResult, {
    key: s.id,
    subtask: s,
    onOpen: onOpenInWorkshop,
    brief: brief
  })))), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: icons && colors ? '1fr 1fr' : '1fr',
      gap: 14,
      marginTop: composed?.preview ? 18 : 0
    }
  }, icons && icons.icons && /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      marginBottom: 8,
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: '600 11px/1 var(--font-body)',
      color: 'var(--fg-muted)',
      letterSpacing: '0.08em',
      textTransform: 'uppercase'
    }
  }, "Generated icons \xB7 ", icons.icons.length), onRefinePart && /*#__PURE__*/React.createElement(RefineChip, {
    scope: {
      kind: 'icons-all'
    },
    onRefine: onRefinePart,
    disabled: refining,
    label: "Refine all",
    placeholder: "e.g. Make them all rounder"
  }), /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--primary dsa-btn--sm",
    style: {
      marginLeft: 'auto'
    },
    onClick: () => {
      onAdoptIcons(icons.icons);
      window.dsaToast?.(`Adopted ${icons.icons.length} icons`);
    }
  }, "Adopt all")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill, minmax(80px, 1fr))',
      gap: 6
    }
  }, icons.icons.map((ic, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    style: {
      background: 'var(--bg-canvas)',
      borderRadius: 'var(--r-sm)',
      padding: '10px 6px 6px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: 6,
      position: 'relative'
    },
    className: "dsa-part-tile"
  }, /*#__PURE__*/React.createElement("svg", {
    viewBox: "0 0 24 24",
    width: "26",
    height: "26",
    fill: "none",
    stroke: "var(--accent-bronze)",
    strokeWidth: "1.5",
    strokeLinecap: "round",
    strokeLinejoin: "round",
    dangerouslySetInnerHTML: {
      __html: ic.body
    }
  }), /*#__PURE__*/React.createElement("div", {
    style: {
      font: '500 10px/1.2 var(--font-mono)',
      color: 'var(--fg-secondary)',
      textAlign: 'center'
    }
  }, ic.name), onRefinePart && /*#__PURE__*/React.createElement(RefineDot, {
    scope: {
      kind: 'icon',
      target: ic.name
    },
    onRefine: onRefinePart,
    disabled: refining,
    placeholder: `Change "${ic.name}"`
  }))))), colors && colors.colors && /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'flex',
      alignItems: 'baseline',
      marginBottom: 8,
      gap: 8
    }
  }, /*#__PURE__*/React.createElement("span", {
    style: {
      font: '600 11px/1 var(--font-body)',
      color: 'var(--fg-muted)',
      letterSpacing: '0.08em',
      textTransform: 'uppercase'
    }
  }, "Generated colors \xB7 ", colors.colors.length), onRefinePart && /*#__PURE__*/React.createElement(RefineChip, {
    scope: {
      kind: 'colors-all'
    },
    onRefine: onRefinePart,
    disabled: refining,
    label: "Refine all",
    placeholder: "e.g. Cooler / warmer / more saturated"
  }), /*#__PURE__*/React.createElement("button", {
    className: "dsa-btn dsa-btn--primary dsa-btn--sm",
    style: {
      marginLeft: 'auto'
    },
    onClick: () => {
      onAdoptColors(colors.colors.map(c => ({
        ...c,
        group: colors.group || 'Build'
      })));
      window.dsaToast?.(`Adopted ${colors.colors.length} colors`);
    }
  }, "Adopt all")), /*#__PURE__*/React.createElement("div", {
    style: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill, minmax(110px, 1fr))',
      gap: 6
    }
  }, colors.colors.map((c, i) => /*#__PURE__*/React.createElement("div", {
    key: i,
    style: {
      background: 'var(--bg-canva