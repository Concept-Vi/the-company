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

const { useState: useState_as, useEffect: useEffect_as, useMemo: useMemo_as, useRef: useRef_as } = React;

const MODES = [
  { id: 'generate', label: 'Generate',  icon: 'atom',        desc: 'Text → image. Full GPT Image 2 control surface.' },
  { id: 'edit',     label: 'Edit',      icon: 'edit',        desc: 'Send a source image with a change instruction.' },
  { id: 'compose',  label: 'Compose',   icon: 'image-stack', desc: 'Combine up to 16 reference images with roles.' },
  { id: 'mask',     label: 'Mask',      icon: 'browser-pen', desc: 'Brush a region to inpaint. Alpha mask powered.' },
  { id: 'chat',     label: 'Chat',      icon: 'chat-tree',   desc: 'Multi-turn editing via the Responses API.' },
];

const ROLE_OPTIONS = [
  { id: 'base',      label: 'Base',      desc: 'Image to start from.' },
  { id: 'reference', label: 'Reference', desc: 'General context.' },
  { id: 'style',     label: 'Style',     desc: 'Match this look.' },
  { id: 'object',    label: 'Object',    desc: 'Include this object.' },
  { id: 'identity',  label: 'Identity',  desc: 'Match this person.' },
];

function AIStudio({ onNav }) {
  const projects = window.cvImageStore.listProjects();
  const cached   = window.cvOpenAI.getCachedModels?.()?.models || [];
  const [models, setModels] = useState_as(cached);
  const [presets, setPresets] = useState_as(window.cvAIPresets.listPresets());
  const [pipelines, setPipelines] = useState_as(window.cvAIPresets.listPipelines());

  const settings = window.cvOpenAI.getSettings();
  const [mode, setMode]         = useState_as('generate');
  const [modelId, setModelId]   = useState_as(settings.imageModel);
  const caps                    = window.cvOpenAI.getModelCapabilities(modelId);

  const [prompt, setPrompt]     = useState_as(presets[0]?.body || '');
  const [brandEnrich, setBrand] = useState_as(true);

  const [size, setSize]         = useState_as(caps.sizes[1] || caps.sizes[0] || '1024x1024');
  const [customSize, setCustomSize] = useState_as({ w: 1536, h: 1024 });
  const [useCustomSize, setUseCustomSize] = useState_as(false);
  const [quality, setQuality]   = useState_as(caps.qualities[0] || '');
  const [format, setFormat]     = useState_as(caps.outputFormats?.[0] || 'png');
  const [compression, setCompression] = useState_as(90);
  const [background, setBackground]   = useState_as('auto');
  const [moderation, setModeration]   = useState_as('auto');
  const [n, setN]               = useState_as(1);
  const [stream, setStream]     = useState_as(caps.supports.stream);
  const [partialImages, setPartialImages] = useState_as(caps.supports.partialImages || 0);

  const [target, setTarget]     = useState_as({ scope: 'system', pid: projects[0]?.id });
  const [results, setResults]   = useState_as([]);
  const [partials, setPartials] = useState_as([]);
  const [busy, setBusy]         = useState_as(false);
  const [err, setErr]           = useState_as(null);
  const [activePreset, setActivePreset] = useState_as(presets[0]?.id);

  // Edit / compose / mask state
  const [editSourceUrl, setEditSourceUrl] = useState_as(null);
  const [composeImages, setComposeImages] = useState_as([]);
  const [maskSourceUrl, setMaskSourceUrl] = useState_as(null);
  const [maskBlob, setMaskBlob]           = useState_as(null);

  // Chat state
  const [chatTurns, setChatTurns] = useState_as([]);
  const [chatInput, setChatInput] = useState_as('');
  const [chatBusy, setChatBusy]   = useState_as(false);
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
  useEffect_as(() => window.cvAIPresets.subscribe(d => { setPresets(d.presets); setPipelines(d.pipelines); }), []);

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
      brandEnrich,
    };
    if (caps.qualities.length)        opts.quality = quality || caps.qualities[0];
    if (caps.outputFormats?.length)   opts.output_format = format;
    if ((format === 'jpeg' || format === 'webp')) opts.output_compression = compression;
    if (caps.backgrounds?.length)     opts.background = background;
    if (caps.moderations?.length)     opts.moderation = moderation;
    if (caps.supports.stream && stream) {
      opts.stream = true;
      opts.partial_images = partialImages;
    }
    return opts;
  }

  function onPartial({ src, index }) {
    setPartials(prev => { const next = [...prev]; next[index] = src; return next; });
  }

  async function urlToBlob(url) { return await (await fetch(url)).blob(); }

  async function runGenerate() {
    setErr(null); setBusy(true); setResults([]); setPartials([]);
    try {
      const opts = buildOptions();
      if (stream && caps.supports.stream) opts.onPartial = onPartial;
      const out = await window.CV_AI.resolveProvider('openai-image').generateImage(opts);
      setResults(out);
      for (const im of out) {
        try { await window.cvImageStore.addFromSrc('ai', null, im.src, { name: prompt.slice(0, 60), prompt, source: 'ai' }); }
        catch {}
      }
    } catch (e) { setErr(e.message || 'Generation failed.'); }
    finally { setBusy(false); }
  }

  async function runEdit() {
    if (!editSourceUrl) { setErr('Add a source image first.'); return; }
    setErr(null); setBusy(true); setResults([]); setPartials([]);
    try {
      const blob = await urlToBlob(editSourceUrl);
      const opts = { ...buildOptions(), images: [blob] };
      if (stream && caps.supports.stream) opts.onPartial = onPartial;
      const out = await window.CV_AI.resolveProvider('openai-image').editImage(opts);
      setResults(out);
      for (const im of out) try { await window.cvImageStore.addFromSrc('ai', null, im.src, { name: prompt.slice(0, 60), prompt, source: 'ai' }); } catch {}
    } catch (e) { setErr(e.message || 'Edit failed.'); }
    finally { setBusy(false); }
  }

  async function runCompose() {
    if (composeImages.length === 0) { setErr('Add at least one reference image.'); return; }
    if (composeImages.length > (caps.maxRefImages || 0)) { setErr(`Up to ${caps.maxRefImages} reference images.`); return; }
    setErr(null); setBusy(true); setResults([]); setPartials([]);
    try {
      const blobs = await Promise.all(composeImages.map(i => urlToBlob(i.src)));
      const rolesStr = composeImages.map((i, idx) => `Image ${idx + 1}: ${i.role || 'reference'} (${i.name || 'unnamed'})`).join('\n');
      const composedPrompt = `${prompt}\n\nReference images:\n${rolesStr}`;
      const opts = { ...buildOptions(), prompt: composedPrompt, images: blobs };
      if (stream && caps.supports.stream) opts.onPartial = onPartial;
      const out = await window.CV_AI.resolveProvider('openai-image').editImage(opts);
      setResults(out);
      for (const im of out) try { await window.cvImageStore.addFromSrc('ai', null, im.src, { name: prompt.slice(0, 60), prompt: composedPrompt, source: 'ai' }); } catch {}
    } catch (e) { setErr(e.message || 'Compose failed.'); }
    finally { setBusy(false); }
  }

  async function runMask() {
    if (!maskSourceUrl) { setErr('Pick a source image first.'); return; }
    if (!maskBlob)      { setErr('Brush a mask area first.'); return; }
    setErr(null); setBusy(true); setResults([]); setPartials([]);
    try {
      const blob = await urlToBlob(maskSourceUrl);
      const opts = { ...buildOptions(), images: [blob], mask: maskBlob };
      if (stream && caps.supports.stream) opts.onPartial = onPartial;
      const out = await window.CV_AI.resolveProvider('openai-image').editImage(opts);
      setResults(out);
      for (const im of out) try { await window.cvImageStore.addFromSrc('ai', null, im.src, { name: prompt.slice(0, 60), prompt, source: 'ai' }); } catch {}
    } catch (e) { setErr(e.message || 'Mask edit failed.'); }
    finally { setBusy(false); }
  }

  async function sendChat() {
    const text = chatInput.trim();
    if (!text) return;
    setChatTurns(t => [...t, { role: 'user', content: text }]);
    setChatInput(''); setChatBusy(true); setErr(null);
    try {
      const opts = {
        input: text, action: 'auto',
        size: useCustomSize && caps.supports.customSize ? `${customSize.w}x${customSize.h}` : size,
        quality, format, background,
        previous_response_id: chatRespId,
      };
      const out = await window.CV_AI.resolveProvider('openai-image').responsesImage(opts);
      setChatRespId(out.responseId);
      setChatTurns(t => [...t, { role: 'vi', content: out.revisedPrompt || 'Generated', images: out.images, revisedPrompt: out.revisedPrompt }]);
      for (const im of out.images) try { await window.cvImageStore.addFromSrc('ai', null, im.src, { name: text.slice(0, 60), prompt: text, source: 'ai' }); } catch {}
    } catch (e) {
      setErr(e.message || 'Chat-edit failed.');
      setChatTurns(t => [...t, { role: 'vi', content: `⚠ ${e.message || 'Failed'}` }]);
    } finally { setChatBusy(false); }
  }

  async function runPipeline(p) {
    setRunningPipelineId(p.id); setPipelineLog([]); setErr(null);
    let lastImage = null;
    try {
      for (let i = 0; i < p.steps.length; i++) {
        const step = p.steps[i];
        setPipelineLog(l => [...l, { i, label: step.label || step.kind, status: 'running' }]);
        if (step.kind === 'generate') {
          const preset = step.presetId && window.cvAIPresets.findPreset(step.presetId);
          const seed = preset ? window.cvAIPresets.materialize(preset) : { prompt: step.prompt };
          const out = await window.CV_AI.resolveProvider('openai-image').generateImage({ ...seed, brandEnrich: true });
          lastImage = out[0]?.src;
          for (const im of out) try { await window.cvImageStore.addFromSrc('ai', null, im.src, { source: 'ai', name: (seed.prompt || '').slice(0,60), prompt: seed.prompt }); } catch {}
        } else if (step.kind === 'edit' && lastImage) {
          const blob = await urlToBlob(lastImage);
          const out = await window.CV_AI.resolveProvider('openai-image').editImage({ prompt: step.prompt, images: [blob], model: modelId });
          lastImage = out[0]?.src;
          for (const im of out) try { await window.cvImageStore.addFromSrc('ai', null, im.src, { source: 'ai', name: (step.prompt || '').slice(0,60), prompt: step.prompt }); } catch {}
        } else if (step.kind === 'adopt') {
          const aiList = window.cvImageStore.list('ai').slice(0, 6);
          for (const im of aiList) {
            const scope = step.to === 'project' ? 'projects' : 'system';
            await window.cvImageStore.addFromSrc(scope, target.pid, im.src, { name: im.name, prompt: im.prompt, source: 'ai', tags: step.tags || ['AI'] });
          }
        }
        setPipelineLog(l => l.map(x => x.i === i ? { ...x, status: 'ok' } : x));
      }
      window.dsaToast?.(`Pipeline "${p.name}" complete`);
    } catch (e) {
      setErr(`Pipeline failed: ${e.message}`);
      setPipelineLog(l => { const next = [...l]; const idx = next.findIndex(x => x.status === 'running'); if (idx >= 0) next[idx] = { ...next[idx], status: 'fail' }; return next; });
    } finally {
      setRunningPipelineId(null);
    }
  }

  function savePreset() {
    if (!presetName.trim()) return;
    window.cvAIPresets.addPreset({
      name: presetName.trim(), body: prompt, icon: 'star',
      model: modelId,
      size: useCustomSize ? `${customSize.w}x${customSize.h}` : size,
      quality, output_format: format,
      output_compression: (format === 'jpeg' || format === 'webp') ? compression : undefined,
      background, moderation, n,
    });
    setSavePresetOpen(false); setPresetName('');
    window.dsaToast?.(`Saved preset "${presetName.trim()}"`);
  }

  async function adoptResult(im, scopeOverride) {
    const scope = scopeOverride || target.scope;
    const meta = { name: prompt.slice(0, 60), prompt, source: 'ai', tags: ['AI'] };
    if (scope === 'system')        await window.cvImageStore.addFromSrc('system', null, im.src, meta);
    else if (scope === 'projects') await window.cvImageStore.addFromSrc('projects', target.pid, im.src, meta);
    else if (scope === 'hubs')     await window.cvImageStore.addFromSrc('hubs', target.pid, im.src, { name: prompt.slice(0, 40), tags: ['AI'] });
    window.dsaToast?.(`Adopted into ${scope === 'system' ? 'system library' : scope === 'hubs' ? '360° hubs' : projects.find(p => p.id === target.pid)?.name || 'project'}`);
  }
  function adoptAllResults() { for (const r of results) adoptResult(r); }
  function downloadResult(im) {
    const a = document.createElement('a');
    a.href = im.src; a.download = `vi-${Date.now()}.${im.format || 'png'}`;
    a.click();
  }

  async function addComposeFiles(files) {
    const next = [];
    for (const f of files) {
      const reader = await new Promise((resolve, reject) => {
        const fr = new FileReader();
        fr.onload = () => resolve(fr.result); fr.onerror = reject;
        fr.readAsDataURL(f);
      });
      next.push({ src: reader, role: next.length === 0 ? 'base' : 'reference', name: f.name });
    }
    setComposeImages(prev => [...prev, ...next].slice(0, caps.maxRefImages || 16));
  }
  function removeCompose(i) { setComposeImages(prev => prev.filter((_, idx) => idx !== i)); }
  function setComposeRole(i, role) { setComposeImages(prev => prev.map((x, idx) => idx === i ? { ...x, role } : x)); }

  const configured = window.cvOpenAI.isConfigured();
  const sizeValidation = useMemo_as(() => {
    const sz = useCustomSize ? `${customSize.w}x${customSize.h}` : size;
    return window.cvOpenAI.validateSize?.(modelId, sz) || { ok: true };
  }, [size, customSize, useCustomSize, modelId]);

  /* ===== RENDER ===== */
  return (
    <div className="cv-as">
      {!configured && (
        <ConnectBanner onNav={onNav}/>
      )}

      {/* Mode strip — flat tabs */}
      <div className="cv-as-tabs">
        {MODES.map(m => {
          const cap = window.cvOpenAI.getModelCapabilities(modelId).supports;
          const disabled =
            (m.id === 'edit'    && !cap.edit) ||
            (m.id === 'compose' && !cap.multiRef) ||
            (m.id === 'mask'    && !cap.mask);
          return (
            <button key={m.id}
              className={`cv-as-tab ${mode === m.id ? 'active' : ''}`}
              onClick={() => !disabled && setMode(m.id)}
              disabled={disabled}
              title={disabled ? `Not supported by ${modelId}` : m.desc}>
              <CvIcon name={m.icon} size={14} tone={mode === m.id ? 'gold' : 'bronze'}/>
              <span>{m.label}</span>
            </button>
          );
        })}
        <span className="cv-as-tab-desc">{MODES.find(m => m.id === mode)?.desc}</span>
      </div>

      {/* Three-column layout with draggable gutters */}
      <div className="cv-as-shell">
        <Resizable storageKey="ai-studio-cols" cols={[
          { id: 'left',  size: 230, min: 200, max: 320 },
          { id: 'main',  size: 'flex' },
          { id: 'right', size: 340, min: 280, max: 480 },
        ]}>
          {/* LEFT — presets + pipelines */}
          <PresetRail
            presets={presets}
            pipelines={pipelines}
            activePresetId={activePreset}
            onApplyPreset={applyPreset}
            onRemovePreset={id => window.cvAIPresets.removePreset(id)}
            onSaveCurrentAsPreset={() => setSavePresetOpen(true)}
            onRunPipeline={runPipeline}
            runningPipelineId={runningPipelineId}
            pipelineLog={pipelineLog}
            configured={configured}
          />

          {/* CENTER — mode stage */}
          <div className="cv-as-stage cv-stack-loose">
            {mode === 'generate' && (
              <PromptCard prompt={prompt} setPrompt={setPrompt} caps={caps} brandEnrich={brandEnrich} setBrand={setBrand}/>
            )}
            {mode === 'edit' && (
              <>
                <SourcePicker label="Source image" url={editSourceUrl} onChoose={setEditSourceUrl} target={target} setTarget={setTarget}/>
                <PromptCard prompt={prompt} setPrompt={setPrompt} caps={caps} brandEnrich={brandEnrich} setBrand={setBrand}
                  placeholder="What should change? E.g. 'replace the sky with golden hour' or 'add brushed gold trim to the window frames'"/>
              </>
            )}
            {mode === 'compose' && (
              <>
                <ComposeRack items={composeImages} max={caps.maxRefImages}
                  onAddFiles={addComposeFiles} onRemove={removeCompose} onSetRole={setComposeRole}/>
                <PromptCard prompt={prompt} setPrompt={setPrompt} caps={caps} brandEnrich={brandEnrich} setBrand={setBrand}
                  placeholder="Describe the composition. Refer to images by number — 'use image 1 as the room, image 2 as the lighting'"/>
              </>
            )}
            {mode === 'mask' && (
              <>
                <SourcePicker label="Image to mask" url={maskSourceUrl}
                  onChoose={url => { setMaskSourceUrl(url); setMaskBlob(null); }} target={target} setTarget={setTarget}/>
                {maskSourceUrl && <MaskEditor src={maskSourceUrl} onChange={setMaskBlob} height={300}/>}
                <PromptCard prompt={prompt} setPrompt={setPrompt} caps={caps} brandEnrich={brandEnrich} setBrand={setBrand}
                  placeholder='What to paint into the brushed region. E.g. "a sandstone fireplace"'/>
              </>
            )}
            {mode === 'chat' && (
              <ChatLane turns={chatTurns} input={chatInput} setInput={setChatInput} busy={chatBusy}
                onSend={sendChat} onReset={() => { setChatTurns([]); setChatRespId(null); }} configured={configured}/>
            )}

            {err && <div className="cv-as-err">{err}</div>}

            {/* Compact param bar — always visible */}
            {mode !== 'chat' && (
              <ParamBar
                modelId={modelId} models={models} caps={caps}
                size={size} setSize={setSize}
                useCustomSize={useCustomSize} setUseCustomSize={setUseCustomSize}
                customSize={customSize} setCustomSize={setCustomSize}
                sizeValidation={sizeValidation}
                quality={quality} setQuality={setQuality}
                n={n} setN={setN}
                showAdvanced={showAdvanced} setShowAdvanced={setShowAdvanced}
                format={format} setFormat={setFormat}
                compression={compression} setCompression={setCompression}
                background={background} setBackground={setBackground}
                moderation={moderation} setModeration={setModeration}
                stream={stream} setStream={setStream}
                partialImages={partialImages} setPartialImages={setPartialImages}
                setModelId={setModelId}
                target={target} setTarget={setTarget} projects={projects}
                onSavePreset={() => setSavePresetOpen(true)}
              />
            )}

            {/* Run row */}
            {mode !== 'chat' && (
              <div className="cv-as-runbar">
                <button className="cv-as-run-btn" disabled={busy || !configured || !sizeValidation.ok || !prompt.trim()}
                  onClick={() => mode === 'generate' ? runGenerate() : mode === 'edit' ? runEdit() : mode === 'compose' ? runCompose() : runMask()}>
                  <ViShape size={14} animated={busy}/>
                  <span>{busy ? (stream ? 'Streaming…' : 'Generating…') : (mode === 'generate' ? 'Generate' : mode === 'edit' ? 'Apply edit' : mode === 'compose' ? 'Compose' : 'Apply mask')}</span>
                </button>
                <div className="cv-as-runbar-meta">
                  {!sizeValidation.ok && <span className="cv-as-warn">{sizeValidation.reason}</span>}
                  {sizeValidation.ok && sizeValidation.experimental && <span className="cv-as-warn cv-as-warn--mild">Experimental size</span>}
                  <span className="cv-as-cost">
                    <b>{n}</b>× {format.toUpperCase()}{(format === 'jpeg' || format === 'webp') ? ` ${compression}%` : ''} · <code>{modelId}</code>
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* RIGHT — results */}
          <ResultsRail
            results={results} partials={partials} busy={busy} n={n}
            onAdopt={adoptResult} onAdoptAll={adoptAllResults}
            onDownload={downloadResult}
            onEditAgain={src => { setEditSourceUrl(src); setMode('edit'); }}
            history={window.cvImageStore.list('ai').slice(0, 6)}
          />
        </Resizable>
      </div>

      {savePresetOpen && (
        <SavePresetModal
          name={presetName} setName={setPresetName}
          onCancel={() => setSavePresetOpen(false)}
          onSave={savePreset}
        />
      )}
    </div>
  );
}

/* ============================================================
   ConnectBanner
   ============================================================ */
function ConnectBanner({ onNav }) {
  return (
    <div className="cv-as-banner">
      <div className="cv-as-banner-shape"><ViShape size={20}/></div>
      <div className="cv-as-banner-body">
        <h4>AI Studio is in preview mode</h4>
        <p>Connect your OpenAI API key to unlock generation, editing, masks, and chat.</p>
      </div>
      <button className="cv-pill cv-pill--filled" onClick={() => onNav?.('settings')}>
        <CvIcon name="gear" size={12} tone="ink"/> Open Settings
      </button>
    </div>
  );
}

/* ============================================================
   PresetRail
   ============================================================ */
function PresetRail({ presets, pipelines, activePresetId, onApplyPreset, onRemovePreset, onSaveCurrentAsPreset, onRunPipeline, runningPipelineId, pipelineLog, configured }) {
  return (
    <div className="cv-as-rail">
      <div className="cv-panel-head">
        <h4>Presets</h4>
        <span className="meta">{presets.length}</span>
        <div className="right">
          <button className="cv-as-icon-btn" title="Save current as preset" onClick={onSaveCurrentAsPreset}>+</button>
        </div>
      </div>
      <div className="cv-as-preset-list">
        {presets.map(p => (
          <button key={p.id} className={`cv-as-preset ${activePresetId === p.id ? 'active' : ''}`} onClick={() => onApplyPreset(p)}>
            <span className="ico"><CvIcon name={p.icon || 'star'} size={13} tone={activePresetId === p.id ? 'gold' : 'bronze'}/></span>
            <span className="name">{p.name}</span>
            <button className="x" onClick={e => { e.stopPropagation(); onRemovePreset(p.id); }} title="Remove">×</button>
          </button>
        ))}
      </div>

      <div className="cv-panel-head" style={{marginTop:'var(--s-6)'}}>
        <h4>Pipelines</h4>
        <span className="meta">{pipelines.length}</span>
      </div>
      <div className="cv-as-pipeline-list">
        {pipelines.map(p => (
          <div key={p.id} className={`cv-as-pipeline ${runningPipelineId === p.id ? 'running' : ''}`}>
            <div className="head">
              <span className="name">{p.name}</span>
              <button className="cv-as-pipe-run" disabled={!configured || runningPipelineId} onClick={() => onRunPipeline(p)}>
                <ViShape size={10}/> Run
              </button>
            </div>
            <p>{p.desc}</p>
            <ol>
              {p.steps.map((s, i) => {
                const log = pipelineLog.find(l => l.i === i);
                return (
                  <li key={i} className={log?.status || ''}>
                    <span className="badge">{s.kind}</span>
                    <span className="lbl">{s.label || s.prompt || ''}</span>
                    {log?.status === 'running' && <span className="dot"/>}
                    {log?.status === 'ok' && <span className="ok">✓</span>}
                    {log?.status === 'fail' && <span className="bad">✗</span>}
                  </li>
                );
              })}
            </ol>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ============================================================
   PromptCard
   ============================================================ */
function PromptCard({ prompt, setPrompt, caps, brandEnrich, setBrand, placeholder }) {
  const remaining = (caps?.maxPromptChars || 32000) - prompt.length;
  return (
    <div className="cv-as-prompt">
      <div className="cv-panel-head">
        <h4>Prompt</h4>
        <span className="meta">describe what you want</span>
      </div>
      <textarea
        value={prompt} onChange={e => setPrompt(e.target.value)}
        rows={4}
        placeholder={placeholder || 'Describe the image. Vi will respect ConceptV warmth + gold accents.'}
      />
      <div className="cv-as-prompt-meta">
        <label className="cv-as-toggle">
          <input type="checkbox" checked={brandEnrich} onChange={e => setBrand(e.target.checked)}/>
          <span>Brand-enrich the prompt</span>
        </label>
        <span className={`cv-as-count ${remaining < 200 ? 'low' : ''}`}>{remaining.toLocaleString()} chars left</span>
      </div>
    </div>
  );
}

/* ============================================================
   SourcePicker
   ============================================================ */
function SourcePicker({ label, url, onChoose, target, setTarget }) {
  const fileRef = useRef_as(null);
  const [pickerOpen, setPicker] = useState_as(false);
  const projects = window.cvImageStore.listProjects();

  async function onFile(file) {
    const reader = await new Promise((res, rej) => {
      const fr = new FileReader();
      fr.onload = () => res(fr.result); fr.onerror = rej;
      fr.readAsDataURL(file);
    });
    onChoose(reader);
  }

  return (
    <div className="cv-as-source">
      <div className="cv-panel-head">
        <h4>{label}</h4>
        <div className="right">
          <button className="cv-as-icon-btn cv-as-icon-btn--wide" onClick={() => fileRef.current?.click()}>
            <CvIcon name="cloud-upload" size={11} tone="bronze"/> Upload
          </button>
          <button className="cv-as-icon-btn cv-as-icon-btn--wide" onClick={() => setPicker(p => !p)}>
            <CvIcon name="image-stack" size={11} tone="bronze"/> Library
          </button>
          <input ref={fileRef} type="file" accept="image/*" style={{display:'none'}}
            onChange={e => e.target.files[0] && onFile(e.target.files[0])}/>
        </div>
      </div>
      {url ? (
        <div className="cv-as-source-preview">
          <img src={url} alt=""/>
          <button className="cv-as-source-clear" onClick={() => onChoose(null)}>✕</button>
        </div>
      ) : (
        <div className="cv-as-dropzone" onClick={() => fileRef.current?.click()}>
          <CvIcon name="image" size={24} tone="bronze"/>
          <span>Drop or click to upload, or pick from your library.</span>
        </div>
      )}
      {pickerOpen && (
        <LibraryPicker onClose={() => setPicker(false)} onChoose={src => { onChoose(src); setPicker(false); }}
          target={target} setTarget={setTarget} projects={projects}/>
      )}
    </div>
  );
}

function LibraryPicker({ onClose, onChoose, target, setTarget, projects }) {
  const [scope, setScope] = useState_as(target.scope);
  const list = scope === 'system' ? window.cvImageStore.list('system')
    : scope === 'ai' ? window.cvImageStore.list('ai')
    : window.cvImageStore.list('projects', target.pid);
  return (
    <div className="cv-as-picker">
      <div className="cv-as-picker-head">
        <div className="tabs">
          {[['system','System'],['projects','Projects'],['ai','AI history']].map(([id,lbl]) => (
            <button key={id} className={scope === id ? 'active' : ''} onClick={() => setScope(id)}>{lbl}</button>
          ))}
        </div>
        {scope === 'projects' && (
          <select value={target.pid} onChange={e => setTarget({ ...target, pid: e.target.value })}>
            {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>
        )}
        <button className="x" onClick={onClose}>✕</button>
      </div>
      <div className="cv-as-picker-grid">
        {list.length === 0 && <span className="cv-as-empty-line">Nothing here yet.</span>}
        {list.map(im => (
          <button key={im.id} className="cv-as-picker-tile" onClick={() => onChoose(im.src)} title={im.name}>
            <img src={im.src} alt=""/>
            <span>{im.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

/* ============================================================
   ComposeRack
   ============================================================ */
function ComposeRack({ items, max, onAddFiles, onRemove, onSetRole }) {
  const fileRef = useRef_as(null);
  return (
    <div className="cv-as-compose">
      <div className="cv-panel-head">
        <h4>References</h4>
        <span className="meta">{items.length} / {max} max</span>
        <div className="right">
          <button className="cv-as-icon-btn cv-as-icon-btn--wide" onClick={() => fileRef.current?.click()} disabled={items.length >= max}>
            <CvIcon name="plus" size={11} tone="bronze"/> Add
          </button>
          <input ref={fileRef} type="file" accept="image/*" multiple style={{display:'none'}}
            onChange={e => { onAddFiles([...e.target.files]); e.target.value = ''; }}/>
        </div>
      </div>
      {items.length === 0 ? (
        <div className="cv-as-dropzone" onClick={() => fileRef.current?.click()}>
          <CvIcon name="image-stack" size={24} tone="bronze"/>
          <span>Upload up to {max} references — each can play a role.</span>
        </div>
      ) : (
        <div className="cv-as-compose-grid">
          {items.map((it, i) => (
            <div key={i} className="cv-as-compose-tile">
              <span className="num">{i + 1}</span>
              <img src={it.src} alt=""/>
              <button className="x" onClick={() => onRemove(i)}>×</button>
              <div className="role-row">
                {ROLE_OPTIONS.map(r => (
                  <button key={r.id} className={it.role === r.id ? 'active' : ''} title={r.desc}
                    onClick={() => onSetRole(i, r.id)}>{r.label}</button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/* ============================================================
   ParamBar — compact, deck-restrained, collapsible advanced section
   ============================================================ */
function ParamBar({
  modelId, models, caps, setModelId,
  size, setSize, useCustomSize, setUseCustomSize, customSize, setCustomSize, sizeValidation,
  quality, setQuality, format, setFormat, compression, setCompression,
  background, setBackground, moderation, setModeration,
  n, setN, stream, setStream, partialImages, setPartialImages,
  target, setTarget, projects,
  showAdvanced, setShowAdvanced,
  onSavePreset,
}) {
  return (
    <div className="cv-as-params">
      {/* Main row: model + size + n + adopt destination */}
      <div className="cv-as-params-main">
        <div className="cv-as-param">
          <label>Model</label>
          <select value={modelId} onChange={e => setModelId(e.target.value)}>
            {models.length === 0 && <option>{modelId}</option>}
            {models.map(m => <option key={m.id} value={m.id}>{m.id}{m.tier === 'flagship' ? ' ★' : ''}</option>)}
          </select>
        </div>

        <div className="cv-as-param cv-as-param--size">
          <label>Size</label>
          <div className="cv-as-size-pills">
            {caps.sizes.slice(0, 4).map(s => (
              <button key={s} className={(!useCustomSize && size === s) ? 'on' : ''}
                onClick={() => { setUseCustomSize(false); setSize(s); }}>
                {s === 'auto' ? 'Auto' : s.replace('x', '×')}
              </button>
            ))}
            {caps.sizes.length > 4 && (
              <select className="cv-as-size-more" value={useCustomSize ? '__custom' : size}
                onChange={e => {
                  if (e.target.value === '__custom') setUseCustomSize(true);
                  else { setUseCustomSize(false); setSize(e.target.value); }
                }}>
                <option value="" disabled>More…</option>
                {caps.sizes.slice(4).map(s => <option key={s} value={s}>{s.replace('x', ' × ')}</option>)}
                {caps.supports.customSize && <option value="__custom">Custom…</option>}
              </select>
            )}
            {caps.sizes.length <= 4 && caps.supports.customSize && (
              <button className={useCustomSize ? 'on' : ''} onClick={() => setUseCustomSize(true)}>Custom</button>
            )}
          </div>
          {useCustomSize && (
            <div className="cv-as-custom-size">
              <input type="number" min={256} max={3840} step={16} value={customSize.w}
                onChange={e => setCustomSize(c => ({...c, w: Number(e.target.value)}))}/>
              <span>×</span>
              <input type="number" min={256} max={3840} step={16} value={customSize.h}
                onChange={e => setCustomSize(c => ({...c, h: Number(e.target.value)}))}/>
              <span className={`hint ${sizeValidation.ok ? 'ok' : 'fail'}`}>
                {sizeValidation.ok
                  ? `${((customSize.w * customSize.h) / 1e6).toFixed(2)}MP`
                  : sizeValidation.reason}
              </span>
            </div>
          )}
        </div>

        <div className="cv-as-param">
          <label>Variants</label>
          <select value={n} onChange={e => setN(Number(e.target.value))} disabled={!caps.supports.n}>
            {Array.from({ length: caps.supports.n ? (caps.supports.maxN || 1) : 1 }).map((_, i) => (
              <option key={i + 1} value={i + 1}>{i + 1}</option>
            ))}
          </select>
        </div>

        {caps.qualities.length > 0 && (
          <div className="cv-as-param">
            <label>Quality</label>
            <select value={quality} onChange={e => setQuality(e.target.value)}>
              {caps.qualities.map(q => <option key={q} value={q}>{q}</option>)}
            </select>
          </div>
        )}

        <div className="cv-as-param cv-as-param--target">
          <label>Adopt into</label>
          <div className="cv-as-target">
            {['system','projects','hubs'].map(s => (
              <button key={s} className={target.scope === s ? 'on' : ''} onClick={() => setTarget({ ...target, scope: s })}>
                {s === 'system' ? 'System' : s === 'projects' ? 'Project' : 'Hub'}
              </button>
            ))}
            {(target.scope === 'projects' || target.scope === 'hubs') && (
              <select value={target.pid} onChange={e => setTarget({ ...target, pid: e.target.value })}>
                {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
              </select>
            )}
          </div>
        </div>

        <div className="cv-as-params-actions">
          <button className="cv-as-link-btn" onClick={() => setShowAdvanced(v => !v)}>
            {showAdvanced ? 'Hide advanced' : 'Advanced'} {showAdvanced ? '▴' : '▾'}
          </button>
          <button className="cv-as-link-btn" onClick={onSavePreset}>
            <CvIcon name="star" size={11} tone="bronze"/> Save preset
          </button>
        </div>
      </div>

      {showAdvanced && (
        <div className="cv-as-params-advanced">
          {caps.outputFormats?.length > 0 && (
            <div className="cv-as-param">
              <label>Format</label>
              <select value={format} onChange={e => setFormat(e.target.value)}>
                {caps.outputFormats.map(f => <option key={f} value={f}>{f}</option>)}
              </select>
            </div>
          )}
          {(format === 'jpeg' || format === 'webp') && (
            <div className="cv-as-param cv-as-param--slider">
              <label>Compression</label>
              <input type="range" min={0} max={100} value={compression} onChange={e => setCompression(Number(e.target.value))}/>
              <span className="cv-mono cv-muted">{compression}%</span>
            </div>
          )}
          {caps.backgrounds?.length > 0 && (
            <div className="cv-as-param">
              <label>Background</label>
              <select value={background} onChange={e => setBackground(e.target.value)}>
                {caps.backgrounds.map(b => <option key={b} value={b}>{b}</option>)}
              </select>
            </div>
          )}
          {caps.moderations?.length > 0 && (
            <div className="cv-as-param">
              <label>Moderation</label>
              <select value={moderation} onChange={e => setModeration(e.target.value)}>
                {caps.moderations.map(m => <option key={m} value={m}>{m}</option>)}
              </select>
            </div>
          )}
          {caps.supports.stream && (
            <div className="cv-as-param">
              <label>Streaming</label>
              <label className="cv-as-toggle inline">
                <input type="checkbox" checked={stream} onChange={e => setStream(e.target.checked)}/>
                <span>Stream partials</span>
              </label>
            </div>
          )}
          {caps.supports.stream && stream && (
            <div className="cv-as-param cv-as-param--slider">
              <label>Partial frames</label>
              <input type="range" min={0} max={caps.supports.partialImages || 3} value={partialImages}
                onChange={e => setPartialImages(Number(e.target.value))}/>
              <span className="cv-mono cv-muted">{partialImages}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/* ============================================================
   ResultsRail
   ============================================================ */
function ResultsRail({ results, partials, busy, n, onAdopt, onAdoptAll, onDownload, onEditAgain, history }) {
  return (
    <div className="cv-as-rail">
      <div className="cv-panel-head">
        <h4>Results</h4>
        {results.length > 0 && (
          <div className="right">
            <button className="cv-as-link-btn" onClick={onAdoptAll}>Adopt all</button>
          </div>
        )}
      </div>

      {busy && (
        <div className="cv-as-results-grid">
          {Array.from({ length: n }).map((_, i) => (
            <div key={i} className="cv-as-skel">
              {partials[i] ? (
                <img src={partials[i]} alt="" className="partial"/>
              ) : (
                <div className="placeholder">
                  <ViShape size={18} animated/>
                  <span>Variant {i + 1}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {!busy && results.length === 0 && (
        <div className="cv-as-empty">
          <DiamondShape/>
          <p>Run a generation to see results here.</p>
        </div>
      )}

      {!busy && results.length > 0 && (
        <div className="cv-as-results-grid">
          {results.map((r, i) => (
            <div key={i} className="cv-as-result">
              <img src={r.src} alt=""/>
              <div className="actions">
                <button className="primary" onClick={() => onAdopt(r)}>Adopt</button>
                <button onClick={() => onEditAgain(r.src)}>Edit</button>
                <button className="icon" onClick={() => onDownload(r)} title="Download">
                  <CvIcon name="cloud-download" size={11} tone="bronze"/>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="cv-panel-head" style={{marginTop:'var(--s-6)'}}>
        <h4>Recent</h4>
        <span className="meta">{history.length}</span>
      </div>
      <div className="cv-as-history">
        {history.length === 0 && <span className="cv-as-empty-line">No history yet.</span>}
        {history.map(im => (
          <button key={im.id} className="cv-as-history-item" onClick={() => onEditAgain(im.src)} title={im.prompt}>
            <img src={im.src} alt=""/>
            <span>{im.prompt?.slice(0, 60) || im.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

/* ============================================================
   ChatLane
   ============================================================ */
function ChatLane({ turns, input, setInput, busy, onSend, onReset, configured }) {
  const scrollRef = useRef_as(null);
  useEffect_as(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [turns, busy]);
  return (
    <div className="cv-as-chat">
      <div className="cv-panel-head">
        <h4>Multi-turn editing</h4>
        <span className="meta">via Responses API</span>
        {turns.length > 0 && (
          <div className="right">
            <button className="cv-as-link-btn" onClick={onReset}>
              <CvIcon name="refresh" size={11} tone="bronze"/> Reset thread
            </button>
          </div>
        )}
      </div>
      <div className="cv-as-chat-feed" ref={scrollRef}>
        {turns.length === 0 && (
          <div className="cv-as-chat-empty">
            <DiamondShape/>
            <h4>Start a conversation</h4>
            <p>Each message can generate fresh or edit the previous image. Context threads automatically.</p>
          </div>
        )}
        {turns.map((t, i) => (
          <div key={i} className={`cv-as-chat-turn ${t.role}`}>
            <div className="bubble">
              <span className="who">{t.role === 'user' ? 'You' : 'Vi'}</span>
              <span className="text">{t.content}</span>
              {t.revisedPrompt && t.role === 'vi' && (
                <details className="revised">
                  <summary>Revised prompt</summary>
                  <code>{t.revisedPrompt}</code>
                </details>
              )}
              {t.images?.length > 0 && (
                <div className="images">
                  {t.images.map((im, j) => <img key={j} src={im.src} alt=""/>)}
                </div>
              )}
            </div>
          </div>
        ))}
        {busy && (
          <div className="cv-as-chat-turn vi">
            <div className="bubble"><ViShape size={14} animated/> generating…</div>
          </div>
        )}
      </div>
      <div className="cv-as-chat-composer">
        <textarea
          value={input} onChange={e => setInput(e.target.value)}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); onSend(); } }}
          rows={2}
          placeholder={configured ? 'Tell Vi what to make or change…' : 'Connect OpenAI in Settings to chat-edit.'}
          disabled={!configured || busy}
        />
        <button className="cv-as-run-btn cv-as-run-btn--sm" onClick={onSend} disabled={!configured || busy || !input.trim()}>
          <ViShape size={12}/>
        </button>
      </div>
    </div>
  );
}

/* ============================================================
   SavePresetModal
   ============================================================ */
function SavePresetModal({ name, setName, onCancel, onSave }) {
  return (
    <div className="cv-as-modal-back" onClick={onCancel}>
      <div className="cv-as-modal" onClick={e => e.stopPropagation()}>
        <h3>Save current config as preset</h3>
        <p>Captures every parameter you've set — prompt, model, size, quality, format, n, background, moderation.</p>
        <input autoFocus value={name} onChange={e => setName(e.target.value)}
          placeholder='Name this preset, e.g. "Bayside hero — golden hour"'/>
        <div className="cv-as-modal-actions">
          <button className="cv-pill" onClick={onCancel}>Cancel</button>
          <button className="cv-pill cv-pill--filled" disabled={!name.trim()} onClick={onSave}>Save preset</button>
        </div>
      </div>
    </div>
  );
}

function DiamondShape() {
  return (
    <svg viewBox="0 0 40 40" width="48" height="48" fill="none" stroke="var(--accent-bronze)" strokeWidth="1.5">
      <path d="M20 4 L36 20 L20 36 L4 20 Z"/>
      <path d="M12 12 L28 28 M28 12 L12 28" strokeDasharray="2 3" opacity="0.5"/>
    </svg>
  );
}

window.AIStudio = AIStudio;
