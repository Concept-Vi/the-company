// App.jsx — ConceptV Studio root
const { useState: useState_app, useEffect: useEffect_app } = React;

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
      if (i >= 0) { const next = [...prev]; next[i] = d; return next; }
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
      if (val == null) root.style.removeProperty(`--${name}`);
      else root.style.setProperty(`--${name}`, val);
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
    window.cvNav = (target) => setActive(target);
    return () => { delete window.cvNav; };
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

  const recentActivity = [
    ...generatedIcons.slice(-2).reverse().map(g => ({ text: <><b>Adopted "{g.name}"</b> into icons.</>, by: 'via Vi', time: 'recent', icon: 'star', color: 'gold' })),
    ...Object.entries(colorEdits).slice(-1).map(([n, hex]) => ({ text: <><b>Edited token {n}</b> → {hex}.</>, by: 'by you', time: 'recent', icon: 'color-swatches', color: 'gold' })),
    ...savedTemplates.slice(-1).map(t => ({ text: <><b>Saved template "{t.name}"</b>.</>, by: 'by you', time: 'recent', icon: 'browser', color: 'gold' })),
    { text: <><b>Brand Kit</b> updated — added 2 logos.</>, by: 'by you', time: '14m', icon: 'tag' },
    { text: <><b>Voice rule</b>: "No exclamation marks" added.</>, by: 'by you', time: '3h', icon: 'chat-double' },
  ].slice(0, 6);

  const counts = {
    iconCount: Object.keys(window.CV_ICONS?.data || {}).length,
    colorCount: 20 + extraColors.length,
    componentCount: 14 + generatedComponents.length,
    inboxCount: inboxItems.length,
    inboxNew: inboxItems.some(i => !i.appliedCat),
    typeCount: 3,
    logoCount: 4,
    imageryCount: window.cvImageStore?.counts?.()?.total || 0,
    patternCount: 13 + 7 + 6 + 5, // spacing + radii + shadows + motion = 31
    templateCount: 3 + savedTemplates.length,
    typeCountTotal: window.CV_REGISTRY?.all().length || 0,
    voiceCount: 7,
    gaps: 3,
    aiReady: window.cvOpenAI?.isConfigured() ? 1 : 0,
    healthScore: Math.min(100, 86 + Math.min(generatedIcons.length, 6) + extraColors.length + Object.keys(colorEdits).length),
  };

  function addGeneratedIcon(g) {
    setGeneratedIcons(prev => prev.some(x => x.name === g.name) ? prev : [...prev, g]);
  }
  function updateGeneratedIcon(name, body) {
    setGeneratedIcons(prev => prev.map(g => g.name === name ? { ...g, body } : g));
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
  function addExtraColors(list) { setExtraColors(prev => [...prev, ...list]); }
  function setColorEdit(name, hex) { setColorEdits(prev => ({ ...prev, [name]: hex })); }
  function setPatternEdit(name, val) {
    setPatternEdits(prev => {
      const next = { ...prev };
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
  if (active === 'overview')      canvas = <Overview counts={counts} onNav={setActive} recentActivity={recentActivity} onExport={() => setExportOpen(true)} onReset={resetSession}/>;
  else if (active === 'inbox')    canvas = <Inbox items={inboxItems} setItems={setInboxItems} onApplied={onInboxApplied}/>;
  else if (active === 'icons')    canvas = <Icons generated={generatedIcons} addGenerated={addGeneratedIcon} updateGenerated={updateGeneratedIcon} removeGenerated={removeGeneratedIcon}/>;
  else if (active === 'colors')   canvas = <Colors extras={extraColors} addExtras={addExtraColors} colorEdits={colorEdits} setColorEdit={setColorEdit} snapshot={paletteSnapshot} setSnapshot={setPaletteSnapshot} lockedTokens={lockedTokens} toggleLock={toggleLock}/>;
  else if (active === 'voice')    canvas = <Voice savedRewrites={savedRewrites} addSavedRewrite={addSavedRewrite} removeSavedRewrite={removeSavedRewrite}/>;
  else if (active === 'build')    canvas = <Build initialBrief={pendingBrief} onAdoptIcons={addGeneratedIcons} onAdoptColors={addExtraColors} onSaveAsTemplate={saveTemplate} onNav={setActive} onOpenInWorkshop={runWorkshopTemplate}/>;
  else if (active === 'templates')canvas = <Templates savedTemplates={savedTemplates} removeTemplate={removeTemplate} onRunBrief={runTemplateBrief} onRunWorkshopTemplate={runWorkshopTemplate} onOpenRegistry={() => setActive('registry')}/>;
  else if (active === 'registry') canvas = <Registry onOpenBuilder={(id) => { setTbTypeId(id || null); setActive('type-builder'); }}/>;
  else if (active === 'architecture') canvas = <Architecture onNav={setActive} onOpenBuilder={(id) => { setTbTypeId(id || null); setActive('type-builder'); }}/>;
  else if (active === 'type-builder') canvas = <TypeBuilder initialTypeId={tbTypeId} onClose={() => setActive('registry')} onSaved={() => { setActive('registry'); }}/>;
  else if (active === 'components') canvas = <Components generated={generatedComponents} addGenerated={(c) => setGeneratedComponents(prev => [...prev, c])}/>;
  else if (active === 'workshop') canvas = <Workshop docs={workshopDocs} saveDoc={saveWorkshopDoc} removeDoc={removeWorkshopDoc} saveTemplate={saveTemplate} pendingDocId={pendingWorkshopDoc}/>;
  else if (active === 'patterns') canvas = <Patterns edits={patternEdits} setEdit={setPatternEdit} snapshot={patternSnapshot} setSnapshot={setPatternSnapshot} locked={lockedPatterns} toggleLock={togglePatternLock}/>;
  else if (active === 'imagery')  canvas = <Imagery onNav={setActive}/>;
  else if (active === 'bridge')   canvas = <Bridge/>;
  else if (active === 'settings') canvas = <Settings/>;
  else canvas = <StubCanvas id={active}/>;

  return (
    <div className={`dsa-shell ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      {!sidebarCollapsed && (
        <Sidebar
          active={active}
          onSelect={setActive}
          counts={counts}
          onOpenSearch={() => setPaletteOpen(true)}
          onCollapse={() => setSidebarCollapsed(true)}/>
      )}
      {sidebarCollapsed && (
        <button
          type="button"
          className="dsa-drawer-reopen"
          onClick={() => setSidebarCollapsed(false)}
          title="Show sidebar"
          aria-label="Show sidebar">
          <CvIcon name="sidebar-close" size={16} tone="bronze"/>
        </button>
      )}
      <main className="dsa-main">{canvas}</main>
      {active !== 'registry' && <ChatRail scope={active}/>}
      <Toast/>
      <ExportPatch
        open={exportOpen} onClose={() => setExportOpen(false)}
        generatedIcons={generatedIcons} extraColors={extraColors} colorEdits={colorEdits}
        patternEdits={patternEdits}
      />
      <CommandPalette
        open={paletteOpen}
        onClose={() => setPaletteOpen(false)}
        nav={setActive}
        openExport={() => setExportOpen(true)}
        copyText={copyText}
      />
      <SaveAsTypeModal/>
    </div>
  );
}

const _mountApp = document.getElementById('app');
if (_mountApp) ReactDOM.createRoot(_mountApp).render(<App/>);
