// canvases/Settings.jsx — system-wide settings, focused on the OpenAI surface
// Vi uses for all image generation. Adding a key here lights up the AI Studio
// inside Imagery and the image-aware mode in Vi.
const { useState: useState_st, useEffect: useEffect_st } = React;

function Settings() {
  const [s, setS] = useState_st(() => window.cvOpenAI.getSettings());
  const [reveal, setReveal] = useState_st(false);
  const [testing, setTesting] = useState_st(false);
  const [testResult, setTestResult] = useState_st(null);
  const [pendingKey, setPendingKey] = useState_st(s.apiKey);
  const [pendingProxy, setPendingProxy] = useState_st(s.proxyUrl);
  const [pendingOrg, setPendingOrg] = useState_st(s.organization);
  const [modelPayload, setModelPayload] = useState_st(() => window.cvOpenAI.getCachedModels?.() || null);
  const [refreshingModels, setRefreshingModels] = useState_st(false);
  const [modelError, setModelError] = useState_st(null);

  useEffect_st(() => window.cvOpenAI.subscribe(next => setS({ ...next })), []);
  useEffect_st(() => window.cvOpenAI.subscribeModels?.(payload => setModelPayload({ ...payload })), []);

  // Pull model list on first mount if we've never fetched and we are configured.
  useEffect_st(() => {
    const cached = window.cvOpenAI.getCachedModels?.();
    if (cached && cached.source === 'api' && cached.fetchedAt > 0) return;
    if (!window.cvOpenAI.isConfigured()) return;
    refreshModels();
  }, []);

  async function refreshModels() {
    if (!window.cvOpenAI.isConfigured()) {
      setModelError('Add an API key first to fetch the live model list.');
      return;
    }
    setRefreshingModels(true); setModelError(null);
    try {
      const payload = await window.cvOpenAI.listImageModels({ force: true });
      setModelPayload(payload);
      window.dsaToast?.(`Found ${payload.models.length} image models`);
    } catch (e) {
      setModelError(e.message || 'Could not fetch models.');
    } finally {
      setRefreshingModels(false);
    }
  }

  function patch(part) {
    const next = window.cvOpenAI.updateSettings(part);
    setS(next);
  }

  function saveCredentials() {
    patch({ apiKey: pendingKey.trim(), proxyUrl: pendingProxy.trim(), organization: pendingOrg.trim() });
    window.dsaToast?.('Credentials saved');
    setTestResult(null);
  }

  async function runTest() {
    setTesting(true); setTestResult(null);
    try {
      const r = await window.cvOpenAI.testConnection();
      setTestResult({ ok: true, msg: `Connected. ${r.modelCount} models visible · ${r.imageModelCount} image-capable.` });
      // testConnection refreshes the model cache as a side effect
      setModelPayload(window.cvOpenAI.getCachedModels?.());
    } catch (e) {
      setTestResult({ ok: false, msg: e.message || 'Connection failed.' });
    } finally { setTesting(false); }
  }

  const masked = (() => {
    const k = s.apiKey || '';
    if (!k) return '';
    if (reveal) return k;
    if (k.length < 10) return '•'.repeat(k.length);
    return k.slice(0, 6) + '•'.repeat(Math.max(8, k.length - 10)) + k.slice(-4);
  })();

  const storageBytes = window.cvImageStore?.bytes() || 0;
  const storageMB = (storageBytes / (1024 * 1024)).toFixed(2);

  return (
    <>
      <CanvasHeader
        title="Settings"
        sub="Configure the AI services your studio uses. Vi connects to OpenAI for image generation, editing, and variations."
        actions={
          <button className="dsa-btn dsa-btn--outline" onClick={() => window.location.reload()}>
            <CvIcon name="refresh" size={12} tone="bronze"/> Reload
          </button>
        }
      />
      <div className="dsa-canvas-body">

        {/* ====== Connection status banner ====== */}
        <div className={`cv-st-banner ${window.cvOpenAI.isConfigured() ? 'ok' : 'warn'}`}>
          <span className="dot"/>
          <div>
            <b>{window.cvOpenAI.isConfigured() ? 'OpenAI is connected' : 'OpenAI is not connected'}</b>
            <span>
              {window.cvOpenAI.isConfigured()
                ? <>Vi can generate, edit, and refine images on any canvas. Image model: <code>{s.imageModel}</code>.</>
                : <>Add an API key below to unlock image generation across the studio. Until then, Imagery → AI Studio will run in preview mode.</>}
            </span>
          </div>
        </div>

        {/* ====== API credentials ====== */}
        <section className="cv-st-section">
          <header>
            <h3>API credentials</h3>
            <p>Stored locally in your browser. Never sent anywhere except OpenAI (and only when you call it).</p>
          </header>
          <div className="cv-st-grid">
            <label className="cv-st-field">
              <span className="lbl">OpenAI API key</span>
              <div className="cv-st-input-row">
                <input
                  type={reveal ? 'text' : 'password'}
                  className="cv-st-input mono"
                  placeholder="sk-…"
                  value={pendingKey}
                  onChange={e => setPendingKey(e.target.value)}
                  autoComplete="off"
                  spellCheck={false}
                />
                <button type="button" className="cv-st-eye" onClick={() => setReveal(r => !r)} title={reveal ? 'Hide' : 'Reveal'}>
                  <CvIcon name={reveal ? 'eye-off' : 'eye'} size={14} tone="bronze"/>
                </button>
              </div>
              <span className="hint">
                {s.apiKey
                  ? <>Active key: <code>{masked}</code> — get a new one at <a href="https://platform.openai.com/api-keys" target="_blank">platform.openai.com/api-keys</a></>
                  : <>Get a key at <a href="https://platform.openai.com/api-keys" target="_blank">platform.openai.com/api-keys</a></>}
              </span>
            </label>

            <label className="cv-st-field">
              <span className="lbl">Organization ID <em>(optional)</em></span>
              <input
                type="text" className="cv-st-input mono"
                placeholder="org-…"
                value={pendingOrg}
                onChange={e => setPendingOrg(e.target.value)}
              />
              <span className="hint">Required only if your key spans multiple orgs.</span>
            </label>

            <label className="cv-st-field full">
              <span className="lbl">Proxy URL <em>(optional)</em></span>
              <input
                type="text" className="cv-st-input mono"
                placeholder="https://your-proxy.example.com  (leave blank to call OpenAI directly)"
                value={pendingProxy}
                onChange={e => setPendingProxy(e.target.value)}
              />
              <span className="hint">If your network blocks direct browser calls to OpenAI, route through a thin proxy that forwards to <code>api.openai.com</code>.</span>
            </label>
          </div>

          <div className="cv-st-actions">
            <button className="dsa-btn dsa-btn--primary" onClick={saveCredentials}>
              <CvIcon name="check" size={12} tone="ink"/> Save credentials
            </button>
            <button className="dsa-btn dsa-btn--outline" onClick={runTest} disabled={testing || !pendingKey.trim()}>
              {testing ? 'Testing…' : 'Test connection'}
            </button>
            {testResult && (
              <span className={`cv-st-result ${testResult.ok ? 'ok' : 'fail'}`}>
                {testResult.ok ? '✓' : '✗'} {testResult.msg}
              </span>
            )}
          </div>
        </section>

        {/* ====== Image defaults ====== */}
        <section className="cv-st-section">
          <header style={{display:'flex',alignItems:'flex-start',gap:16}}>
            <div style={{flex:1}}>
              <h3>Image models</h3>
              <p>Pulled live from OpenAI. New models appear automatically as they ship.</p>
            </div>
            <div style={{display:'flex',flexDirection:'column',alignItems:'flex-end',gap:6}}>
              <button className="dsa-btn dsa-btn--outline dsa-btn--sm" onClick={refreshModels} disabled={refreshingModels}>
                <CvIcon name="refresh" size={11} tone="bronze"/> {refreshingModels ? 'Refreshing…' : 'Refresh model list'}
              </button>
              <span className="cv-st-models-meta">
                {modelPayload?.source === 'api'
                  ? <>{modelPayload.models.length} image models · pulled {formatRelative(modelPayload.fetchedAt)}</>
                  : modelPayload?.source === 'static'
                    ? <>Showing {modelPayload.models.length} known models · connect a key to pull live</>
                    : 'No models loaded yet'}
              </span>
            </div>
          </header>
          {modelError && <div className="cv-st-result fail" style={{marginBottom:12}}>✗ {modelError}</div>}

          <ModelPicker
            models={modelPayload?.models || []}
            selectedId={s.imageModel}
            onSelect={id => patch({ imageModel: id })}
          />

          <ModelDefaults settings={s} patch={patch} models={modelPayload?.models || []}/>

          <div className="cv-st-toggle-row" style={{marginTop:18, paddingTop:14, borderTop:'1px dashed var(--accent-gold-soft)'}}>
            <label className="cv-st-toggle">
              <input type="checkbox" checked={s.enableForVi} onChange={e => patch({ enableForVi: e.target.checked })}/>
              <span>Let Vi generate images when asked in chat</span>
            </label>
            <label className="cv-st-toggle">
              <input type="checkbox" checked={s.safeMode} onChange={e => patch({ safeMode: e.target.checked })}/>
              <span>Safe mode — block prompts that may violate policy before sending</span>
            </label>
          </div>
        </section>

        {/* ====== Storage ====== */}
        <section className="cv-st-section">
          <header>
            <h3>Local storage</h3>
            <p>All your imagery and studio state lives in this browser. Clearing wipes everything you've adopted.</p>
          </header>
          <div className="cv-st-storage">
            <div className="meter">
              <div className="fill" style={{ width: `${Math.min(100, (storageBytes / (5 * 1024 * 1024)) * 100).toFixed(1)}%` }}/>
            </div>
            <div className="legend">
              <span><b>{storageMB} MB</b> used of ≈ 5 MB browser quota</span>
              <span>{window.cvImageStore?.counts?.()?.total || 0} images stored</span>
            </div>
            <div className="cv-st-actions">
              <button className="dsa-btn dsa-btn--outline" onClick={() => {
                if (confirm('Clear ALL studio state? Inboxes, palette edits, imagery — everything.')) {
                  window.cvStudioStorage?.clear();
                  location.reload();
                }
              }}>Clear all studio state</button>
            </div>
          </div>
        </section>

      </div>
    </>
  );
}

/* ===========================================================
   Live model picker — grouped by tier (flagship / standard /
   legacy), capability badges per card, selectable.
   =========================================================== */
function ModelPicker({ models, selectedId, onSelect }) {
  if (!models?.length) {
    return (
      <div className="cv-st-models-empty">
        <ViShape size={18}/>
        <span>No models loaded yet — add an API key and click <b>Refresh model list</b>.</span>
      </div>
    );
  }

  const tiers = [
    { id: 'flagship', label: 'Flagship', desc: 'Newest and highest fidelity. Use for hero imagery.' },
    { id: 'standard', label: 'Standard', desc: 'Reliable, prompt-faithful workhorses.' },
    { id: 'legacy',   label: 'Legacy',   desc: 'Older models — fastest, lowest cost, narrower features.' },
  ];

  const grouped = {};
  for (const m of models) {
    const t = m.tier || 'standard';
    grouped[t] = grouped[t] || [];
    grouped[t].push(m);
  }

  return (
    <div className="cv-st-models">
      {tiers.map(tier => {
        const list = grouped[tier.id];
        if (!list?.length) return null;
        return (
          <div className="cv-st-model-tier" key={tier.id}>
            <div className="cv-st-model-tier-head">
              <span className={`cv-st-tier-badge tier-${tier.id}`}>{tier.label}</span>
              <span className="cv-st-tier-desc">{tier.desc}</span>
            </div>
            <div className="cv-st-model-grid">
              {list.map(m => (
                <button
                  key={m.id}
                  type="button"
                  className={`cv-st-model-card ${selectedId === m.id ? 'active' : ''}`}
                  onClick={() => onSelect(m.id)}>
                  <div className="cv-st-model-card-head">
                    <div>
                      <span className="cv-st-model-id">{m.id}</span>
                      {m.release && <span className="cv-st-model-release">released {m.release}</span>}
                    </div>
                    <span className="cv-st-model-radio">{selectedId === m.id ? '●' : '○'}</span>
                  </div>
                  <p className="cv-st-model-tag">{m.tagline}</p>
                  <div className="cv-st-model-caps">
                    {m.supports?.generate && <span className="cap" title="Image generation">generate</span>}
                    {m.supports?.edit     && <span className="cap" title="Inpainting / edit">edit</span>}
                    {m.supports?.variation && <span className="cap" title="Variations">variations</span>}
                    {m.supports?.style    && <span className="cap" title="Style param">style</span>}
                    {m.supports?.n && (m.supports?.maxN || 1) > 1 && <span className="cap">n × {m.supports.maxN}</span>}
                  </div>
                  <div className="cv-st-model-meta">
                    <span>{m.sizes?.length || 0} sizes</span>
                    {m.qualities?.length > 0 && <span>· {m.qualities.length} quality tiers</span>}
                  </div>
                </button>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

/* ===========================================================
   Capability-aware defaults — size, quality, style options
   adapt to whatever the selected model actually supports.
   =========================================================== */
function ModelDefaults({ settings, patch, models }) {
  const caps = window.cvOpenAI.getModelCapabilities(settings.imageModel);

  return (
    <div className="cv-st-grid" style={{marginTop:18, paddingTop:14, borderTop:'1px dashed var(--accent-gold-soft)'}}>
      <label className="cv-st-field">
        <span className="lbl">Default size for <code>{settings.imageModel}</code></span>
        <select className="cv-st-input" value={settings.defaultSize}
          onChange={e => patch({ defaultSize: e.target.value })}>
          {(caps.sizes || []).map(s => <option key={s} value={s}>{s.replace('x', ' × ')}</option>)}
          {!(caps.sizes || []).includes(settings.defaultSize) && (
            <option value={settings.defaultSize}>{settings.defaultSize} (not supported)</option>
          )}
        </select>
      </label>

      {caps.qualities?.length > 0 ? (
        <label className="cv-st-field">
          <span className="lbl">Default quality</span>
          <select className="cv-st-input" value={settings.defaultQuality}
            onChange={e => patch({ defaultQuality: e.target.value })}>
            {caps.qualities.map(q => <option key={q} value={q}>{q}</option>)}
          </select>
        </label>
      ) : (
        <label className="cv-st-field">
          <span className="lbl">Default quality</span>
          <span className="cv-st-static-field">Fixed for this model.</span>
        </label>
      )}

      {caps.supports?.style ? (
        <label className="cv-st-field">
          <span className="lbl">Style preference</span>
          <select className="cv-st-input" value={settings.defaultStyle}
            onChange={e => patch({ defaultStyle: e.target.value })}>
            <option value="natural">Natural — photoreal default</option>
            <option value="vivid">Vivid — hyper-stylised</option>
          </select>
        </label>
      ) : (
        <label className="cv-st-field">
          <span className="lbl">Style preference</span>
          <span className="cv-st-static-field">Not configurable for this model.</span>
        </label>
      )}

      <label className="cv-st-field">
        <span className="lbl">Per call: variants (n)</span>
        <span className="cv-st-static-field">
          {caps.supports?.n
            ? <>Up to <b>{caps.supports.maxN}</b> images per call</>
            : <>Single image per call</>}
        </span>
      </label>
    </div>
  );
}

/* ===========================================================
   Pretty time formatter
   =========================================================== */
function formatRelative(ts) {
  if (!ts) return 'never';
  const diff = Date.now() - ts;
  const m = Math.floor(diff / 60000);
  if (m < 1) return 'just now';
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  const d = Math.floor(h / 24);
  return `${d}d ago`;
}

window.Settings = Settings;
