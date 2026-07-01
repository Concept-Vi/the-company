// components/ImageEditor.jsx — modal canvas-based image editor.
// Used by every imagery surface (System, Projects, AI Studio). Crop, adjust,
// filter, rotate, and route to OpenAI for AI edits / variations.
//
// Renders into the page as a full-screen sheet. Caller passes the image record
// and an onSave callback that receives the final image data URL.

const { useState: useState_ed, useEffect: useEffect_ed, useRef: useRef_ed, useMemo: useMemo_ed } = React;

const FILTERS = [
  { id: 'none',    label: 'Original',     css: '' },
  { id: 'warm',    label: 'Warm paper',   css: 'sepia(0.18) saturate(1.08) contrast(1.04) brightness(1.02)' },
  { id: 'cool',    label: 'Cool dawn',    css: 'hue-rotate(-8deg) saturate(0.95) contrast(1.06)' },
  { id: 'bronze',  label: 'Bronze line',  css: 'sepia(0.55) saturate(0.7) contrast(1.1) brightness(0.97)' },
  { id: 'gold',    label: 'Gold-cast',    css: 'sepia(0.3) saturate(1.4) hue-rotate(-10deg)' },
  { id: 'mono',    label: 'Mono ink',     css: 'grayscale(1) contrast(1.08)' },
  { id: 'fade',    label: 'Soft fade',    css: 'contrast(0.92) saturate(0.85) brightness(1.04)' },
];

function ImageEditor({ image, onSave, onClose }) {
  const [mode, setMode]       = useState_ed('adjust'); // adjust | crop | ai
  const [bright, setBright]   = useState_ed(100);
  const [contrast, setCont]   = useState_ed(100);
  const [satur, setSat]       = useState_ed(100);
  const [hue, setHue]         = useState_ed(0);
  const [rotate, setRot]      = useState_ed(0);
  const [flipH, setFlipH]     = useState_ed(false);
  const [flipV, setFlipV]     = useState_ed(false);
  const [filter, setFilter]   = useState_ed('none');
  const [crop, setCrop]       = useState_ed({ x: 0, y: 0, w: 1, h: 1 }); // 0..1
  const [drag, setDrag]       = useState_ed(null);

  // AI tab state
  const [aiPrompt, setAiPrompt] = useState_ed('');
  const [aiBusy, setAiBusy]     = useState_ed(false);
  const [aiResults, setAiResults] = useState_ed([]);

  const imgRef = useRef_ed(null);
  const stageRef = useRef_ed(null);

  const filterCss = useMemo_ed(() => {
    const f = FILTERS.find(f => f.id === filter)?.css || '';
    return `${f} brightness(${bright}%) contrast(${contrast}%) saturate(${satur}%) hue-rotate(${hue}deg)`;
  }, [filter, bright, contrast, satur, hue]);

  const transform = `rotate(${rotate}deg) scaleX(${flipH ? -1 : 1}) scaleY(${flipV ? -1 : 1})`;

  function resetAdjust() {
    setBright(100); setCont(100); setSat(100); setHue(0); setFilter('none');
    setRot(0); setFlipH(false); setFlipV(false);
  }

  // Apply current pipeline to the source image and return a data URL
  async function bake() {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => {
        const sw = img.naturalWidth, sh = img.naturalHeight;
        const cw = sw * crop.w, ch = sh * crop.h;
        const sx = sw * crop.x, sy = sh * crop.y;

        // Rotation-aware target canvas
        const rot = rotate % 360;
        const rad = (rot * Math.PI) / 180;
        const isQ = rot % 180 !== 0;
        const tw = Math.round(isQ ? ch : cw);
        const th = Math.round(isQ ? cw : ch);

        const canvas = document.createElement('canvas');
        canvas.width = tw; canvas.height = th;
        const ctx = canvas.getContext('2d');
        ctx.save();
        ctx.translate(tw / 2, th / 2);
        ctx.rotate(rad);
        ctx.scale(flipH ? -1 : 1, flipV ? -1 : 1);
        ctx.filter = filterCss;
        ctx.drawImage(img, sx, sy, cw, ch, -cw / 2, -ch / 2, cw, ch);
        ctx.restore();
        resolve(canvas.toDataURL('image/jpeg', 0.92));
      };
      img.onerror = reject;
      img.src = image.src;
    });
  }

  async function save() {
    try {
      const out = await bake();
      onSave?.(out);
    } catch { window.dsaToast?.('Could not bake image.'); }
  }

  // Crop overlay handling (drag corners on the displayed image)
  function onCropDown(e, corner) {
    if (mode !== 'crop') return;
    const rect = stageRef.current.getBoundingClientRect();
    setDrag({ corner, rect, startX: e.clientX, startY: e.clientY, startCrop: { ...crop } });
  }
  useEffect_ed(() => {
    if (!drag) return;
    function onMove(e) {
      const { rect, startX, startY, startCrop, corner } = drag;
      const dx = (e.clientX - startX) / rect.width;
      const dy = (e.clientY - startY) / rect.height;
      const c = { ...startCrop };
      if (corner === 'tl') {
        c.x = clamp(startCrop.x + dx, 0, startCrop.x + startCrop.w - 0.05);
        c.y = clamp(startCrop.y + dy, 0, startCrop.y + startCrop.h - 0.05);
        c.w = startCrop.w - (c.x - startCrop.x);
        c.h = startCrop.h - (c.y - startCrop.y);
      } else if (corner === 'tr') {
        const nw = clamp(startCrop.w + dx, 0.05, 1 - startCrop.x);
        c.y = clamp(startCrop.y + dy, 0, startCrop.y + startCrop.h - 0.05);
        c.w = nw;
        c.h = startCrop.h - (c.y - startCrop.y);
      } else if (corner === 'bl') {
        c.x = clamp(startCrop.x + dx, 0, startCrop.x + startCrop.w - 0.05);
        c.w = startCrop.w - (c.x - startCrop.x);
        c.h = clamp(startCrop.h + dy, 0.05, 1 - startCrop.y);
      } else if (corner === 'br') {
        c.w = clamp(startCrop.w + dx, 0.05, 1 - startCrop.x);
        c.h = clamp(startCrop.h + dy, 0.05, 1 - startCrop.y);
      } else if (corner === 'move') {
        c.x = clamp(startCrop.x + dx, 0, 1 - startCrop.w);
        c.y = clamp(startCrop.y + dy, 0, 1 - startCrop.h);
      }
      setCrop(c);
    }
    function onUp() { setDrag(null); }
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
    return () => { window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp); };
  }, [drag]);

  function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

  function aspectCrop(ratio) {
    // Centred crop with given aspect ratio in image coordinates
    if (!imgRef.current) return;
    const sw = imgRef.current.naturalWidth, sh = imgRef.current.naturalHeight;
    const imgAspect = sw / sh;
    let cw, ch;
    if (ratio > imgAspect) { cw = 1; ch = imgAspect / ratio; }
    else { ch = 1; cw = ratio / imgAspect; }
    setCrop({ x: (1 - cw) / 2, y: (1 - ch) / 2, w: cw, h: ch });
  }

  async function runAiEdit() {
    if (!window.cvOpenAI.isConfigured()) {
      window.dsaToast?.('Add an OpenAI API key in Settings first.');
      return;
    }
    setAiBusy(true); setAiResults([]);
    try {
      const baked = await bake();
      const res = await fetch(baked);
      const blob = await res.blob();
      const out = await window.CV_AI.resolveProvider('openai-image').editImage({ prompt: aiPrompt, imageBlob: blob });
      setAiResults(out);
    } catch (e) {
      window.dsaToast?.(e.message || 'AI edit failed.');
    } finally {
      setAiBusy(false);
    }
  }

  return (
    <div className="cv-ed-backdrop" onClick={onClose}>
      <div className="cv-ed-shell" onClick={e => e.stopPropagation()}>
        <header className="cv-ed-head">
          <div className="cv-ed-title">
            <span className="dot"/>
            <h3>Edit · <span className="name">{image.name || 'Image'}</span></h3>
          </div>
          <div className="cv-ed-modes">
            {['adjust','crop','ai'].map(m => (
              <button key={m} className={mode === m ? 'active' : ''} onClick={() => setMode(m)}>
                {m === 'adjust' && <CvIcon name="adjustments" size={12} tone="bronze"/>}
                {m === 'crop'   && <CvIcon name="image" size={12} tone="bronze"/>}
                {m === 'ai'     && <ViShape size={12}/>}
                {m === 'adjust' ? 'Adjust' : m === 'crop' ? 'Crop & rotate' : 'AI edit'}
              </button>
            ))}
          </div>
          <button className="cv-ed-close" onClick={onClose}>✕</button>
        </header>

        <div className="cv-ed-body">
          <div className="cv-ed-stage" ref={stageRef}>
            <div className="cv-ed-image-wrap">
              <img
                ref={imgRef}
                src={image.src}
                alt=""
                onLoad={() => { /* could set initial crop */ }}
                style={{ filter: filterCss, transform, transition: 'filter 120ms linear' }}
              />
              {mode === 'crop' && (
                <div className="cv-ed-crop-overlay">
                  <div className="cv-ed-crop-mask"
                    style={{
                      clipPath: `polygon(
                        0 0, 100% 0, 100% 100%, 0 100%, 0 0,
                        ${crop.x * 100}% ${crop.y * 100}%,
                        ${crop.x * 100}% ${(crop.y + crop.h) * 100}%,
                        ${(crop.x + crop.w) * 100}% ${(crop.y + crop.h) * 100}%,
                        ${(crop.x + crop.w) * 100}% ${crop.y * 100}%,
                        ${crop.x * 100}% ${crop.y * 100}%)`,
                    }}/>
                  <div className="cv-ed-crop-box"
                    onMouseDown={e => onCropDown(e, 'move')}
                    style={{
                      left: `${crop.x * 100}%`, top: `${crop.y * 100}%`,
                      width: `${crop.w * 100}%`, height: `${crop.h * 100}%`,
                    }}>
                    {['tl','tr','bl','br'].map(c => (
                      <span key={c} className={`handle ${c}`} onMouseDown={e => { e.stopPropagation(); onCropDown(e, c); }}/>
                    ))}
                    <div className="cv-ed-grid">
                      <span/><span/><span/><span/>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          <aside className="cv-ed-side">
            {mode === 'adjust' && (
              <div className="cv-ed-panel">
                <h4>Tone</h4>
                <Slider label="Brightness" value={bright} onChange={setBright} min={50} max={150} unit="%" reset={() => setBright(100)}/>
                <Slider label="Contrast"   value={contrast} onChange={setCont} min={50} max={150} unit="%" reset={() => setCont(100)}/>
                <Slider label="Saturation" value={satur} onChange={setSat} min={0} max={200} unit="%" reset={() => setSat(100)}/>
                <Slider label="Hue"        value={hue} onChange={setHue} min={-180} max={180} unit="°" reset={() => setHue(0)}/>

                <h4>Filter</h4>
                <div className="cv-ed-filter-grid">
                  {FILTERS.map(f => (
                    <button key={f.id} className={filter === f.id ? 'active' : ''} onClick={() => setFilter(f.id)}>
                      <span className="thumb" style={{ filter: `${f.css}`, backgroundImage: `url(${image.src})` }}/>
                      <span className="lbl">{f.label}</span>
                    </button>
                  ))}
                </div>

                <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={resetAdjust}>
                  <CvIcon name="refresh" size={11} tone="bronze"/> Reset adjustments
                </button>
              </div>
            )}

            {mode === 'crop' && (
              <div className="cv-ed-panel">
                <h4>Aspect ratio</h4>
                <div className="cv-ed-ratios">
                  <button onClick={() => setCrop({ x:0, y:0, w:1, h:1 })}>Free</button>
                  <button onClick={() => aspectCrop(1)}>1:1</button>
                  <button onClick={() => aspectCrop(3/2)}>3:2</button>
                  <button onClick={() => aspectCrop(16/9)}>16:9</button>
                  <button onClick={() => aspectCrop(4/5)}>4:5</button>
                  <button onClick={() => aspectCrop(2/1)}>2:1 · 360</button>
                </div>
                <h4>Rotate</h4>
                <div className="cv-ed-rotate-row">
                  <button onClick={() => setRot(r => (r - 90 + 360) % 360)}>↺ 90°</button>
                  <button onClick={() => setRot(r => (r + 90) % 360)}>↻ 90°</button>
                  <button onClick={() => setFlipH(f => !f)} className={flipH ? 'on' : ''}>Flip H</button>
                  <button onClick={() => setFlipV(f => !f)} className={flipV ? 'on' : ''}>Flip V</button>
                </div>
                <Slider label="Fine angle" value={rotate} onChange={setRot} min={-180} max={180} unit="°" reset={() => setRot(0)}/>
              </div>
            )}

            {mode === 'ai' && (
              <div className="cv-ed-panel">
                <h4><ViShape size={14}/> AI edit</h4>
                <p className="hint">
                  Vi sends the current image to OpenAI with your prompt and returns edited variants.
                  {!window.cvOpenAI.isConfigured() && <> <a href="#settings" onClick={(e) => { e.preventDefault(); window.cvNav?.('settings'); onClose?.(); }}>Connect a key in Settings →</a></>}
                </p>
                <textarea
                  className="cv-ed-textarea"
                  rows="4"
                  placeholder='e.g. "Make the lighting warmer and more cinematic" or "Replace the sky with sunset"'
                  value={aiPrompt}
                  onChange={e => setAiPrompt(e.target.value)}
                />
                <div className="cv-ed-ai-actions">
                  <button className="dsa-btn dsa-btn--ai" disabled={aiBusy || !aiPrompt.trim() || !window.cvOpenAI.isConfigured()} onClick={runAiEdit}>
                    <ViShape size={12}/> {aiBusy ? 'Editing…' : 'Edit with Vi'}
                  </button>
                </div>
                {aiResults.length > 0 && (
                  <div className="cv-ed-ai-results">
                    {aiResults.map((r, i) => (
                      <div key={i} className="cv-ed-ai-result" onClick={() => onSave?.(r.src)}>
                        <img src={r.src} alt=""/>
                        <span className="lbl">Click to adopt</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </aside>
        </div>

        <footer className="cv-ed-foot">
          <span className="cv-ed-meta">
            {image.w}×{image.h} · <code>{filter}</code>
            {mode === 'crop' && <> · crop {(crop.w * 100).toFixed(0)}% × {(crop.h * 100).toFixed(0)}%</>}
          </span>
          <div className="cv-ed-actions">
            <button className="dsa-btn dsa-btn--outline" onClick={onClose}>Cancel</button>
            <button className="dsa-btn dsa-btn--primary" onClick={save}>
              <CvIcon name="check" size={12} tone="ink"/> Save changes
            </button>
          </div>
        </footer>
      </div>
    </div>
  );
}

function Slider({ label, value, onChange, min, max, unit, reset }) {
  return (
    <label className="cv-ed-slider">
      <div className="row">
        <span className="lbl">{label}</span>
        <span className="val">{value}{unit}</span>
        <button onClick={reset} title="Reset">↺</button>
      </div>
      <input type="range" min={min} max={max} value={value} onChange={e => onChange(Number(e.target.value))}/>
    </label>
  );
}

window.ImageEditor = ImageEditor;
