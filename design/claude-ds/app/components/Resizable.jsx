// components/Resizable.jsx — horizontal split with draggable gutter(s).
//
// Usage:
//   <Resizable
//     storageKey="ai-studio-cols"
//     cols={[
//       { id: 'left',  size: 240, min: 180, max: 340 },
//       { id: 'main',  size: 'flex' },
//       { id: 'right', size: 300, min: 240, max: 480 },
//     ]}>
//     <LeftRail/>
//     <MainStage/>
//     <RightRail/>
//   </Resizable>
//
// Sizes for non-flex cols are persisted to localStorage so the user's
// layout survives reloads. Exactly one column should be 'flex'.

const { useState: useState_rz, useEffect: useEffect_rz, useRef: useRef_rz } = React;

function Resizable({ cols, children, storageKey, className }) {
  const flexIdx = cols.findIndex(c => c.size === 'flex');
  const initial = cols.map(c => c.size === 'flex' ? null : c.size);

  const [sizes, setSizes] = useState_rz(() => {
    if (!storageKey) return initial;
    try {
      const raw = localStorage.getItem('cvstudio:resizable:' + storageKey);
      if (!raw) return initial;
      const parsed = JSON.parse(raw);
      return cols.map((c, i) => c.size === 'flex' ? null : (parsed[i] || c.size));
    } catch { return initial; }
  });

  useEffect_rz(() => {
    if (!storageKey) return;
    try { localStorage.setItem('cvstudio:resizable:' + storageKey, JSON.stringify(sizes)); } catch {}
  }, [sizes, storageKey]);

  const [drag, setDrag] = useState_rz(null);
  const containerRef = useRef_rz(null);

  useEffect_rz(() => {
    if (!drag) return;
    function onMove(e) {
      const dx = e.clientX - drag.startX;
      const col = cols[drag.idx];
      // Dragging the gutter affects the column on its LEFT.
      // If that column is the flex one, the gutter resizes the column on
      // the RIGHT instead (with inverted dx).
      let nextIdx = drag.idx;
      let delta = dx;
      if (cols[nextIdx].size === 'flex') {
        nextIdx = drag.idx + 1;
        delta = -dx;
      }
      const c = cols[nextIdx];
      let next = (drag.startSizes[nextIdx] || 240) + delta;
      const min = c.min ?? 120;
      const max = c.max ?? 560;
      if (next < min) next = min;
      if (next > max) next = max;
      setSizes(prev => prev.map((s, i) => i === nextIdx ? next : s));
    }
    function onUp() { setDrag(null); }
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
    return () => {
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup', onUp);
    };
  }, [drag, cols]);

  function startDrag(i, e) {
    e.preventDefault();
    setDrag({ idx: i, startX: e.clientX, startSizes: [...sizes] });
  }

  const childArray = React.Children.toArray(children);
  return (
    <div ref={containerRef} className={`cv-resizable ${className || ''}`} style={{ display: 'flex', alignItems: 'stretch', width: '100%', height: '100%' }}>
      {childArray.map((child, i) => {
        const size = sizes[i];
        const style = size == null
          ? { flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column' }
          : { flex: '0 0 auto', width: `${size}px`, display: 'flex', flexDirection: 'column' };
        const elements = [
          <div key={`col-${i}`} className="cv-resizable-col" style={style}>
            {child}
          </div>
        ];
        if (i < childArray.length - 1) {
          elements.push(
            <div
              key={`gutter-${i}`}
              className={`cv-gutter ${drag?.idx === i ? 'dragging' : ''}`}
              onMouseDown={e => startDrag(i, e)}
              role="separator"
              aria-orientation="vertical"
            />
          );
        }
        return elements;
      })}
    </div>
  );
}

window.Resizable = Resizable;
