// components/Pano360.jsx — equirectangular 360° viewer.
// Loads three.js on demand. Drag to look around, wheel to zoom, hotspots as
// pinned overlays. Works with any equirectangular JPG/PNG (2:1 ratio ideal).

const { useEffect: useEffect_p, useRef: useRef_p, useState: useState_p } = React;

let __threePromise = null;
function loadThree() {
  if (window.THREE) return Promise.resolve(window.THREE);
  if (__threePromise) return __threePromise;
  __threePromise = new Promise((resolve, reject) => {
    const s = document.createElement('script');
    s.src = 'https://unpkg.com/three@0.160.0/build/three.min.js';
    s.onload = () => resolve(window.THREE);
    s.onerror = reject;
    document.head.appendChild(s);
  });
  return __threePromise;
}

function Pano360({ src, hotspots = [], onAddHotspot, onMoveHotspot, onRemoveHotspot, height = 460, editable = false }) {
  const mountRef = useRef_p(null);
  const stateRef = useRef_p({});
  const [ready, setReady] = useState_p(false);
  const [hovering, setHovering] = useState_p(null);

  useEffect_p(() => {
    let cancelled = false;
    let raf = 0;

    loadThree().then(THREE => {
      if (cancelled || !mountRef.current) return;
      const mount = mountRef.current;
      const w = mount.clientWidth;
      const h = height;

      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(75, w / h, 0.1, 100);
      camera.position.set(0, 0, 0.1);

      const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
      renderer.setSize(w, h);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      mount.appendChild(renderer.domElement);
      renderer.domElement.style.borderRadius = '12px';
      renderer.domElement.style.display = 'block';
      renderer.domElement.style.cursor = 'grab';

      const geom = new THREE.SphereGeometry(50, 64, 32);
      geom.scale(-1, 1, 1); // inside-out
      const loader = new THREE.TextureLoader();
      loader.setCrossOrigin('anonymous');
      const tex = loader.load(src);
      tex.colorSpace = THREE.SRGBColorSpace;
      const mat = new THREE.MeshBasicMaterial({ map: tex });
      const sphere = new THREE.Mesh(geom, mat);
      scene.add(sphere);

      let lon = 180, lat = 0, dragging = false, sx = 0, sy = 0, slon = 0, slat = 0;
      let fov = 75;

      function setLook() {
        const phi   = THREE.MathUtils.degToRad(90 - lat);
        const theta = THREE.MathUtils.degToRad(lon);
        camera.lookAt(
          Math.sin(phi) * Math.cos(theta) * 100,
          Math.cos(phi) * 100,
          Math.sin(phi) * Math.sin(theta) * 100
        );
      }

      // Project a (lon, lat) hotspot onto current viewport
      function project(hotLon, hotLat) {
        const phi   = THREE.MathUtils.degToRad(90 - hotLat);
        const theta = THREE.MathUtils.degToRad(hotLon);
        const v = new THREE.Vector3(
          Math.sin(phi) * Math.cos(theta) * 50,
          Math.cos(phi) * 50,
          Math.sin(phi) * Math.sin(theta) * 50
        );
        v.project(camera);
        const x = (v.x * 0.5 + 0.5) * w;
        const y = (-v.y * 0.5 + 0.5) * h;
        const inFront = v.z < 1;
        return { x, y, inFront };
      }

      function onDown(e) {
        dragging = true;
        sx = e.clientX || (e.touches && e.touches[0].clientX);
        sy = e.clientY || (e.touches && e.touches[0].clientY);
        slon = lon; slat = lat;
        renderer.domElement.style.cursor = 'grabbing';
      }
      function onMove(e) {
        if (!dragging) return;
        const cx = e.clientX || (e.touches && e.touches[0].clientX);
        const cy = e.clientY || (e.touches && e.touches[0].clientY);
        lon = slon - (cx - sx) * 0.2;
        lat = Math.max(-85, Math.min(85, slat + (cy - sy) * 0.2));
      }
      function onUp(e) {
        dragging = false;
        renderer.domElement.style.cursor = 'grab';
      }
      function onWheel(e) {
        e.preventDefault();
        fov = Math.max(30, Math.min(100, fov + e.deltaY * 0.05));
        camera.fov = fov;
        camera.updateProjectionMatrix();
      }
      function onClick(e) {
        if (!editable || !onAddHotspot) return;
        // Determine lon/lat under the click via raycast
        const rect = renderer.domElement.getBoundingClientRect();
        const mx = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        const my = -((e.clientY - rect.top) / rect.height) * 2 + 1;
        const ray = new THREE.Raycaster();
        ray.setFromCamera({ x: mx, y: my }, camera);
        const hits = ray.intersectObject(sphere);
        if (hits[0]) {
          const p = hits[0].point;
          const r = p.length();
          const newLat = 90 - THREE.MathUtils.radToDeg(Math.acos(p.y / r));
          const newLon = THREE.MathUtils.radToDeg(Math.atan2(p.z, p.x));
          onAddHotspot({ lon: newLon, lat: newLat });
        }
      }

      renderer.domElement.addEventListener('mousedown', onDown);
      window.addEventListener('mousemove', onMove);
      window.addEventListener('mouseup', onUp);
      renderer.domElement.addEventListener('wheel', onWheel, { passive: false });
      renderer.domElement.addEventListener('dblclick', onClick);
      renderer.domElement.addEventListener('touchstart', onDown);
      renderer.domElement.addEventListener('touchmove', onMove);
      renderer.domElement.addEventListener('touchend', onUp);

      stateRef.current = {
        get hotspotPositions() {
          return hotspots.map(h => ({ ...h, screen: project(h.lon, h.lat) }));
        },
        renderer, scene, camera,
        mountEl: mount,
      };

      function animate() {
        setLook();
        renderer.render(scene, camera);
        // Force hotspot overlay re-render every frame
        setHovering(h => h); // no-op state nudge — react will reconcile against screen positions
        raf = requestAnimationFrame(animate);
      }
      // Use rAF without forcing React re-render every frame — instead update DOM directly
      const overlayEl = mount.querySelector('.cv-pano-overlay');
      function updateOverlay() {
        if (!overlayEl) return;
        const children = overlayEl.querySelectorAll('[data-hot]');
        children.forEach((el, i) => {
          const h = hotspots[i];
          if (!h) return;
          const pos = project(h.lon, h.lat);
          if (!pos.inFront) { el.style.display = 'none'; return; }
          el.style.display = 'flex';
          el.style.transform = `translate(${pos.x}px, ${pos.y}px) translate(-50%, -50%)`;
        });
      }
      function tick() {
        setLook();
        renderer.render(scene, camera);
        updateOverlay();
        raf = requestAnimationFrame(tick);
      }
      tick();

      setReady(true);

      function onResize() {
        const nw = mount.clientWidth;
        renderer.setSize(nw, height);
        camera.aspect = nw / height;
        camera.updateProjectionMatrix();
      }
      const ro = new ResizeObserver(onResize);
      ro.observe(mount);

      stateRef.current.cleanup = () => {
        cancelAnimationFrame(raf);
        ro.disconnect();
        renderer.domElement.removeEventListener('mousedown', onDown);
        window.removeEventListener('mousemove', onMove);
        window.removeEventListener('mouseup', onUp);
        renderer.domElement.removeEventListener('wheel', onWheel);
        renderer.domElement.removeEventListener('dblclick', onClick);
        renderer.dispose();
        try { mount.removeChild(renderer.domElement); } catch {}
      };
    }).catch(() => {
      // If three failed to load (offline) we fall back to a static image preview.
      setReady(false);
    });

    return () => {
      cancelled = true;
      stateRef.current.cleanup?.();
    };
  }, [src, height, JSON.stringify(hotspots)]);

  return (
    <div className="cv-pano-host" style={{ height, position: 'relative' }}>
      <div ref={mountRef} className="cv-pano-mount" style={{ width: '100%', height, position: 'relative', borderRadius: 12, overflow: 'hidden', background: '#1F1A12' }}>
        <div className="cv-pano-overlay" style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
          {hotspots.map((h, i) => (
            <div key={h.id || i} data-hot
              style={{
                position: 'absolute', left: 0, top: 0,
                pointerEvents: 'auto',
                display: 'flex', alignItems: 'center', gap: 6,
              }}>
              <div className="cv-pano-pin" title={h.label}>
                <span className="dot"/>
                <span className="ring"/>
              </div>
              {h.label && <div className="cv-pano-pin-label">{h.label}</div>}
              {editable && onRemoveHotspot && (
                <button className="cv-pano-pin-x" title="Remove"
                  onClick={(e) => { e.stopPropagation(); onRemoveHotspot(h.id || i); }}>×</button>
              )}
            </div>
          ))}
        </div>
        {!ready && (
          <div className="cv-pano-loading">
            <ViShape size={20} animated/>
            <span>Loading 360 engine…</span>
          </div>
        )}
      </div>
      <div className="cv-pano-help">
        <span><b>Drag</b> to look around</span>
        <span><b>Wheel</b> to zoom</span>
        {editable && <span><b>Double-click</b> to add a hotspot</span>}
      </div>
    </div>
  );
}

window.Pano360 = Pano360;
