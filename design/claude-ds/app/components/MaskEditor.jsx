// components/MaskEditor.jsx — canvas brush mask editor.
//
// Edits a mask layer on top of a source image. The mask is exported as a PNG
// with alpha channel where transparent pixels indicate the area to be edited
// (per OpenAI's spec for images/edits with gpt-image-2).
//
// Controls:
//   - Brush / Eraser
//   - Brush size
//   - Invert mask
//   - Clear
// Output:
//   onChange(blob) is fired whenever the mask is committed (debounced).

const { useEffect: useEffect_me, useRef: useRef_me, useState: useState_me } = React;

function MaskEditor({ src, height = 380, onChange }) {
  const imgRef = useRef_me(null);
  const maskRef = useRef_me(null);
  const composedRef = useRef_me(null);
  const [tool, setTool]      = useState_me('brush');
  const [size, setSize]      = useState_me(40);
  const [drawing, setDrawing] = useState_me(false);
  const [hasMask, setHasMask] = useState_me(false);
  const [dim, setDim] = useState_me({ w: 0, h: 0 });
  const lastPos = useRef_me(null);

  useEffect_me(() => {
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      const ratio = img.naturalWidth / img.naturalHeight;
      const w = Math.round(height * ratio);
      setDim({ w, h: height });
      requestAnimationFrame(() => {
        const m = maskRef.current; if (!m) return;
        m.width = img.naturalWidth; m.height = img.naturalHeight;
        const c = composedRef.current; if (!c) return;
        c.width  = img.naturalWidth; c.height = img.naturalHeight;
        const ctx = c.getContext('2d');
        ctx.drawImage(img, 0, 0);
        repaintComposed();
      });
      imgRef.current = img;
    };
    img.src = src;
  }, [src, height]);

  function repaintComposed() {
    const img = imgRef.current; const mask = maskRef.current; const c = composedRef.current;
    if (!img || !mask || !c) return;
    const ctx = c.getContext('2d');
    ctx.clearRect(0, 0, c.width, c.height);
    ctx.drawImage(img, 0, 0);
    ctx.save();
    ctx.globalAlpha = 0.45;
    ctx.fillStyle = '#E0C010';
    // Draw a tint anywhere mask says "edit here" (mask alpha = 0)
    const mCtx = mask.getContext('2d');
    const mData = mCtx.getImageData(0, 0, mask.width, mask.height);
    const tintCanvas = document.createElement('canvas');
    tintCanvas.width = mask.width; tintCanvas.height = mask.height;
    const tCtx = tintCanvas.getContext('2d');
    const tData = tCtx.createImageData(mask.width, mask.height);
    let hits = 0;
    for (let i = 0; i < mData.data.length; i += 4) {
      const a = mData.data[i + 3];
      if (a < 128) {
        tData.data[i] = 224; tData.data[i+1] = 192; tData.data[i+2] = 16; tData.data[i+3] = 180;
        hits++;
      }
    }
    tCtx.putImageData(tData, 0, 0);
    ctx.drawImage(tintCanvas, 0, 0);
    ctx.restore();
    setHasMask(hits > 0);
    if (onChange) {
      // Output: full image-size canvas, RGB = source, alpha = mask alpha
      const out = document.createElement('canvas');
      out.width = mask.width; out.height = mask.height;
      const oCtx = out.getContext('2d');
      oCtx.drawImage(img, 0, 0);
      const baseData = oCtx.getImageData(0, 0, out.width, out.height);
      for (let i = 0; i < baseData.data.length; i += 4) {
        // Mask alpha < 128 = "edit here" => transparent in output
        baseData.data[i + 3] = mData.data[i + 3] < 128 ? 0 : 255;
      }
      oCtx.putImageData(baseData, 0, 0);
      out.toBlob(blob => onChange(blob), 'image/png');
    }
  }

  function onPointer(e, isDown) {
    if (!maskRef.current) return;
    const rect = composedRef.current.getBoundingClientRect();
    const xs = maskRef.current.width / rect.width;
    const ys = maskRef.current.height / rect.height;
    const cx = (e.clientX - rect.left) * xs;
    const cy = (e.clientY - rect.top)  * ys;
    const ctx = maskRef.current.getContext('2d');
    ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.lineWidth = size * xs;
    if (tool === 'brush') {
      ctx.globalCompositeOperation = 'destination-out';
      ctx.strokeStyle = 'rgba(0,0,0,1)';
    } else {
      ctx.globalCompositeOperation = 'source-over';
      ctx.strokeStyle = 'rgba(0,0,0,1)';
    }
    if (isDown || !lastPos.current) {
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(cx + 0.01, cy);
      ctx.stroke();
    } else {
      ctx.beginPath();
      ctx.moveTo(lastPos.current.x, lastPos.current.y);
      ctx.lineTo(cx, cy);
      ctx.stroke();
    }
    lastPos.current = { x: cx, y: cy };
    repaintComposed();
  }

  function invert() {
    const m = maskRef.current; if (!m) return;
    const ctx = m.getContext('2d');
    const data = ctx.getImageData(0, 0, m.width, m.height);
    // First make sure mask is fully opaque to start (if untouched)
    let anyAlpha = false;
    for (let i = 0; i < data.data.length; i += 4) {
      if (data.data[i + 3] !== 255) { anyAlpha = true; break; }
    }
    if (!anyAlpha) {
      // Untouched: make whole thing transparent so "invert" feels meaningful
      ctx.clearRect(0, 0, m.width, m.height);
    } else {
      // Invert alpha
      for (let i = 0; i < data.data.length; i += 4) {
        data.data[i + 3] = 255 - data.data[i + 3];
      }
      ctx.putImageData(data, 0, 0);
    }
    repaintComposed();
  }
  function clear() {
    const m = maskRef.current; if (!m) return;
    const ctx = m.getContext('2d');
    ctx.clearRect(0, 0, m.width, m.height);
    // Fill fully opaque (default state — no edits)
    ctx.globalCompositeOperation = 'source-over';
    ctx.fillStyle = 'rgba(0,0,0,1)';
    ctx.fillRect(0, 0, m.width, m.height);
    repaintComposed();
  }

  // On first paint, initialize mask to fully opaque so brush "erases" alpha.
  useEffect_me(() => {
    if (!maskRef.current) return;
    const m = maskRef.current;
    const ctx = m.getContext('2d');
    ctx.fillStyle = 'rgba(0,0,0,1)';
    ctx.fillRect(0, 0, m.width, m.height);
    repaintComposed();
  }, [dim.w, dim.h]);

  return (
    <div className="cv-mask-host">
      <div className="cv-mask-toolbar">
        <div className="cv-mask-tools">
          <button className={tool === 'brush' ? 'active' : ''} onClick={() => setTool('brush')}>
            <CvIcon name="edit" size={12} tone={tool === 'brush' ? 'ink' : 'bronze'}/> Brush
          </button>
          <button className={tool === 'eraser' ? 'active' : ''} onClick={() => setTool('eraser')}>
            <CvIcon name="no-symbol" size={12} tone={tool === 'eraser' ? 'ink' : 'bronze'}/> Eraser
          </button>
        </div>
        <label className="cv-mask-size">
          <span>Brush</span>
          <input type="range" min={6} max={140} value={size} onChange={e => setSize(Number(e.target.value))}/>
          <span className="val">{size}px</span>
        </label>
        <div className="cv-mask-actions">
          <button onClick={invert}>Invert</button>
          <button onClick={clear}>Reset</button>
        </div>
      </div>
      <div className="cv-mask-stage" style={{ height }}>
        <canvas
          ref={composedRef}
          className="cv-mask-canvas"
          style={{ width: dim.w, height: dim.h, cursor: tool === 'brush' ? 'crosshair' : 'cell' }}
          onPointerDown={e => { setDrawing(true); lastPos.current = null; onPointer(e, true); }}
          onPointerMove={e => drawing && onPointer(e, false)}
          onPointerUp={() => { setDrawing(false); lastPos.current = null; }}
          onPointerLeave={() => { setDrawing(false); lastPos.current = null; }}
        />
        <canvas ref={maskRef} style={{ display: 'none' }}/>
      </div>
      <div className="cv-mask-help">
        <span>Brush the area you want changed. The <b>gold tint</b> shows what will be edited.</span>
        {hasMask
          ? <span className="status ok"><span className="dot"/> Mask ready</span>
          : <span className="status warn"><span className="dot"/> No mask yet</span>}
      </div>
    </div>
  );
}

window.MaskEditor = MaskEditor;
