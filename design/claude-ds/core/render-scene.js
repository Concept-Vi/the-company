// core/render-scene.js
// ============================================================================
// THE SCENE LAW — window.CV_SCENE — ULTRA rendering as a resolution.
//
// The wall becomes a REAL WebGL scene: one scoped canvas behind .skin-ground,
// every material block a lit 3D slab (depth rung → z height, skin maps → PBR
// material, world offset → UV phase), the Vi light-pool a real point light,
// shadows genuinely cast. Everything is the SAME single sources resolving:
//
//   gate      ← the skin's --scene-mode token ('gl' | anything else = CSS).
//               ONE token flips a whole world between DOM-CSS and WebGL.
//   camera    ← CV_WORLD_CAMERA: --world-zoom scales the ortho camera,
//               --world-pan-x/y pan it, cv:cameramove re-syncs. One camera.
//   geometry  ← the solved DOM layout (block rects + border-radius + depth
//               rung). The DOM stays the layout truth; GL is a PROJECTION.
//   materials ← the skin's texture/map tokens via CV_RENDER3D.env (the one
//               token→scene home); per-block UV offset = the SAME world-
//               position law as --mat-tex-pos.
//   lights    ← same rules as the well solver: key from top-left (the one
//               light, --key-shadow-x), ambient from the ground, accent rim
//               from the skin's gold; PLUS the hub light-pool (a point light
//               over the wall centre — the reference boards' vignette).
//
// While the scene is live the ground carries data-scene-live: CSS hands the
// block SURFACES (fill/texture/shadow/filter) to GL and keeps content (text,
// glyphics, wells) in the DOM above the canvas. Detach restores CSS fully —
// reversible by construction. Loud-fail on missing prerequisites (CLAUDE §3).
//
//   CV_SCENE.attach(ground)  → scene handle (or null if token says CSS)
//   CV_SCENE.sync(ground)    → re-project after any layout pass
//   CV_SCENE.detach(ground)  → back to pure CSS
// ============================================================================
(function () {
  'use strict';

  function env() {
    var E = window.CV_RENDER3D && window.CV_RENDER3D.env;
    if (!E) throw new Error('render-scene: core/render3d.js must load first (it owns the token→scene env)');
    return E;
  }

  function px(v) { return parseFloat(v) || 0; }

  function attach(ground) {
    var gcs = getComputedStyle(ground);
    var mode = gcs.getPropertyValue('--scene-mode').trim();
    function dial(name, fallback) { var v = gcs.getPropertyValue(name).trim(); return v === '' ? fallback : (isNaN(parseFloat(v)) ? v : parseFloat(v)); }
    if (mode !== 'gl') { detach(ground); return null; }
    // WORLD SIGNATURE: materials/lights/textures are resolved ONCE at attach.
    // If the skin changed since, a plain sync() would keep the STALE world's
    // materials (verifier m0438: stone rendering glass's dark transmission).
    var sig = (ground.getAttribute('data-skin') || ground.closest('[data-skin]')?.getAttribute('data-skin') || '') +
              '|' + getComputedStyle(ground).getPropertyValue('--scene-material').trim();
    if (ground.__cvScene) {
      if (ground.__cvScene.sig === sig) { ground.__cvScene.sync(); return ground.__cvScene; }
      detach(ground); // world changed — rebuild fresh from the new skin's tokens
    }

    var E = env();
    var handle = { live: false, sig: sig, sync: function () {}, dispose: function () {} };
    ground.__cvScene = handle;

    E.loadThree().then(function (T) {
      if (ground.__cvScene !== handle) return; // detached while loading

      var canvas = document.createElement('canvas');
      canvas.setAttribute('data-scene-canvas', '');
      canvas.style.cssText = 'position:absolute;inset:0;z-index:0;pointer-events:none;width:100%;height:100%';
      ground.prepend(canvas);

      var renderer = new T.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
      renderer.toneMappingExposure = dial('--gl-exposure', 1.0); // preserve: pixel readback (probes/QA) must see the last frame, not a cleared buffer
      // COLOR MANAGEMENT (todo 87.1): sRGB output transform, NO photographic
      // tone map — this is an evenly-lit wall, not HDR photography; ACES piled
      // every value into its shoulder and crushed the wall/slab separation to
      // ~3 (m0476 probe). Direct sRGB lets material multipliers express fully.
      renderer.outputColorSpace = T.SRGBColorSpace;
      renderer.toneMapping = T.NoToneMapping;
      renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
      renderer.shadowMap.enabled = true;
      renderer.shadowMap.type = T.PCFSoftShadowMap;

      var scene = new T.Scene();
      handle.__scene = scene; // debuggability: probes can traverse the live graph
      // WORLD READS — resolved BEFORE the env IIFE below runs: it reads
      // lightWorld/matKind, and hoisted-var reads gave every LIGHT world the
      // dark night env (the grey washed wall, m0570) and glass never its rim.
      var groundC = E.resolveColor(ground, '--zone-ground', '#202226');
      var accent = E.resolveColor(ground, '--edge-dot', '#c9a34a');
      var lightWorld = E.luminance(groundC) > 0.5;
      var matKind = gcs.getPropertyValue('--scene-material').trim() || 'standard';
      // ENVIRONMENT: physical materials (transmission/clearcoat) can't sparkle
      // in a void — generate a tiny equirect env from the world's own tokens
      // (ground below, sky above, one bright key streak where the key light
      // sits). One mechanism, every world; glass gets its speculars from this.
      (function () {
        var ec = document.createElement('canvas'); ec.width = 128; ec.height = 64;
        var g = ec.getContext('2d');
        var grad = g.createLinearGradient(0, 0, 0, 64);
        if (lightWorld) { grad.addColorStop(0, '#fff9ee'); grad.addColorStop(0.5, '#e8e2d4'); grad.addColorStop(1, '#b8b2a4'); }
        else { grad.addColorStop(0, '#7d8598'); grad.addColorStop(0.45, '#262b36'); grad.addColorStop(1, '#04050a'); }
        g.fillStyle = grad; g.fillRect(0, 0, 128, 64);
        g.fillStyle = lightWorld ? 'rgba(255,255,255,0.95)' : 'rgba(255,246,225,0.92)';
        g.beginPath(); g.ellipse(34, 10, 16, 6, -0.35, 0, Math.PI * 2); g.fill();
        var envTex = new T.CanvasTexture(ec);
        envTex.mapping = T.EquirectangularReflectionMapping;
        scene.environment = envTex;
        scene.environmentIntensity = dial('--gl-env-intensity', lightWorld ? 0.55 : 1.0);
      })();
      var cam = new T.OrthographicCamera(0, 1, 0, -1, -400, 400);

      // ---- token-computed light rig (same rules as the well solver) -------
      // VALUE-ABOVE-GROUND LAW: ambient must be near-WHITE — tinting it with
      // the ground colour multiplies every slab toward the wall's tan and the
      // whole world goes monochrome mud (the m0427 regression). The wall's
      // colour belongs to the wall TEXTURE, not the light.
      // ALL light intensities scale through the ONE --gl-light-boost dial
      // (skin-scoped, GL-plane-only) — the calibration lever now that exposure
      // is inert by design (no tone map).
      var boost = dial('--gl-light-boost', 1.0);
      scene.add(new T.AmbientLight(0xffffff, boost * (lightWorld ? 1.0 : 0.45))); // NEUTRAL ambient — warmth belongs to the albedo + key, not a global tint (m0476 warm-cast 40)
      var keyX = px(getComputedStyle(ground).getPropertyValue('--key-shadow-x')) || 0.55;
      var key = new T.DirectionalLight(0xfffcf4, boost * (lightWorld ? 1.5 : 0.9));
      key.castShadow = true;
      key.shadow.mapSize.set(2048, 2048);
      key.shadow.radius = 8;
      scene.add(key);
      // THE HUB LIGHT-POOL: the wall's centre (Vi) carries a warm pool — the
      // reference boards' vignette, as a real light instead of a baked overlay.
      var rim = new T.DirectionalLight(new T.Color(accent), boost * (lightWorld ? 0.22 : (matKind === 'glass' ? 1.8 : 0.9)));
      rim.position.set(1.6, 0.8, 2.2);
      scene.add(rim);
      var pool = new T.PointLight(new T.Color(accent), boost * (lightWorld ? 0.32 : 1.0), 0, 2);
      scene.add(pool);

      // ---- materials from the skin's map tokens ---------------------------
      var loader = new T.TextureLoader();
      var texCache = {}; // one decode per URL — slabs get cheap clones (shared image)
      // ALPHA-FLATTEN LAW (sector 1, m0510): a map with transparent texels
      // uploaded to an OPAQUE material renders undefined memory — the checkered
      // blotch. EVERY decoded map is scanned; any alpha < 255 is flattened onto
      // the average opaque colour before upload. One law, every texture.
      function flattenAlpha(img) {
        var c = document.createElement('canvas'); c.width = img.width; c.height = img.height;
        var x = c.getContext('2d'); x.drawImage(img, 0, 0);
        var d; try { d = x.getImageData(0, 0, c.width, c.height).data; } catch (e) { return img; }
        var hasAlpha = false, r = 0, g = 0, b = 0, n = 0;
        for (var i = 3; i < d.length; i += 16) { // stride-4 sample is plenty
          if (d[i] < 250) hasAlpha = true;
          else { r += d[i - 3]; g += d[i - 2]; b += d[i - 1]; n++; }
        }
        if (!hasAlpha) return img;
        var base = document.createElement('canvas'); base.width = c.width; base.height = c.height;
        var bx = base.getContext('2d');
        bx.fillStyle = n ? 'rgb(' + Math.round(r / n) + ',' + Math.round(g / n) + ',' + Math.round(b / n) + ')' : '#808080';
        bx.fillRect(0, 0, base.width, base.height);
        bx.drawImage(img, 0, 0);
        return base;
      }
      function baseTex(url) {
        if (!url) return null;
        if (!texCache[url]) {
          var t = loader.load(url, function (loaded) {
            var flat = flattenAlpha(loaded.image);
            t.image = flat;
            // COLD-CACHE LAW (verifier m0445): clones made before decode carry
            // image:undefined FOREVER unless the base propagates its pixels.
            (t.__clones || []).forEach(function (c) { c.image = flat; c.needsUpdate = true; });
            t.needsUpdate = true;
            render();
          });
          t.wrapS = t.wrapT = T.RepeatWrapping;
          t.colorSpace = T.SRGBColorSpace;
          t.__clones = [];
          texCache[url] = t;
        }
        return texCache[url];
      }
      function tex(url, spanPx) {
        var b = baseTex(url);
        if (!b) return null;
        var t = b.clone(); // shares the decoded image — no reload, no black flash
        t.__span = spanPx;
        if (b.image) { t.needsUpdate = true; } // decoded already — safe now
        else { b.__clones.push(t); }           // not yet — the base delivers on decode
        return t;
      }
      var zoom = px(getComputedStyle(ground).getPropertyValue('--world-zoom')) || 1;
      var spanFace = px(getComputedStyle(ground).getPropertyValue('--span-face')) || 460;
      var spanWall = px(getComputedStyle(ground).getPropertyValue('--span-wall')) || 1250;
      // PBR MAP SLOTS (pack-004): UNLIT albedo + normal + roughness resolved
      // from the skin's --map-* tokens. The old baked-LIT tiles double-lit
      // under real GL lights (the 'bad CGI' mud) — they stay CSS-only.
      var faceURL = E.tokenURL(ground, '--gl-map-face-diffuse'); // GL PLANE ONLY — never falls back into CSS-plane tokens (plane split)
      var faceNormalURL = E.tokenURL(ground, '--gl-map-face-normal');
      var faceRoughURL = E.tokenURL(ground, '--gl-map-face-rough');
      var faceAoURL = E.tokenURL(ground, '--gl-map-face-ao');
      var wallURL = E.tokenURL(ground, '--gl-map-wall-diffuse'); // no CSS-plane fallback
      var normalURL = E.tokenURL(ground, '--gl-map-wall-normal');
      var roughURL = E.tokenURL(ground, '--gl-map-wall-rough');
      var wallAoURL = E.tokenURL(ground, '--gl-map-wall-ao');
      var wallDispURL = E.tokenURL(ground, '--gl-map-wall-displacement');

      var wallMat = new T.MeshStandardMaterial({ roughness: 0.94, metalness: 0, color: new T.Color(dial('--gl-wall-tint', lightWorld ? '#d2cbbb' : '#b9bcc4')) }); // wall multiplier RECEDES ~2 shades under the slabs — separation lives here + the slab emissive floor (m0476 calibration)(value-above-ground law)
      var wallTex = tex(wallURL, spanWall); if (wallTex) wallMat.map = wallTex;
      if (normalURL) { var wn = tex(normalURL, spanWall); wn.colorSpace = T.NoColorSpace; wallMat.normalMap = wn; wallMat.normalScale = new T.Vector2(0.5, 0.5); }
      if (roughURL) { var wr = tex(roughURL, spanWall); wr.colorSpace = T.NoColorSpace; wallMat.roughnessMap = wr; wallMat.roughness = 1; }
      if (wallAoURL) { var wa = tex(wallAoURL, spanWall); wa.colorSpace = T.NoColorSpace; wallMat.aoMap = wa; wallMat.aoMapIntensity = 0.75; }
      if (wallDispURL) { var wd = tex(wallDispURL, spanWall); wd.colorSpace = T.NoColorSpace; wallMat.displacementMap = wd; wallMat.displacementScale = 5; wallMat.displacementBias = -2.5; }

      // SLAB MATERIAL KIND is a token (--scene-material, resolved up top):
      // 'glass' resolves a physical transmission material (the glass world's
      // GL ceiling), default is the lit standard slab. PER-ROLE PIGMENT: the
      // zone→pigment law (tokens/glass.css [data-glass-zone] → --glass-tint-pig
      // → the ONE --pig-* registry) projects into GL — each slab reads its own
      // zone's resolved pigment and settles it into the stone, the same whisper
      // the CSS plane mixes. One source, both planes; no per-block material list.
      function slabMaterial(el) {
        if (matKind === 'glass') return new T.MeshPhysicalMaterial({
          transmission: 0.92, thickness: 9, roughness: 0.12, ior: 1.45,
          clearcoat: 1, clearcoatRoughness: 0.08, specularIntensity: 1.5,
          color: 0xffffff, attenuationColor: new T.Color(accent), attenuationDistance: 140,
        });
        var m = new T.MeshStandardMaterial({ roughness: 0.88, metalness: 0, color: new T.Color(dial('--gl-slab-tint', lightWorld ? '#fffdf8' : '#3a3f4a')),
          emissive: new T.Color(dial('--gl-slab-emissive', lightWorld ? '#40352a' : '#0a0c12')), emissiveIntensity: dial('--gl-slab-emissive-intensity', 1.0) }); // emissive floor lifts slabs clear of the wall (reference separation, m0476) — INTENSITY is skin-dialled (stone 0.4: full strength read as the brown glow, m0570)
        var zoneEl = el && el.closest && el.closest('[data-glass-zone]');
        if (zoneEl) {
          var pig = E.resolveColor(zoneEl, '--glass-tint-pig', '');
          if (pig) m.color.lerp(new T.Color(pig), dial('--gl-pig-amt', 0.16));
        }
        return m;
      }

      // CONTACT AO: one shared radial-alpha texture — a tight dark pool under
      // every slab (the reference boards' grounded look; shadow maps alone
      // read too diffuse at contact).
      var aoTex = (function () {
        var c = document.createElement('canvas'); c.width = c.height = 128;
        var x = c.getContext('2d');
        var g = x.createRadialGradient(64, 64, 8, 64, 64, 64);
        g.addColorStop(0, 'rgba(0,0,0,0.34)'); g.addColorStop(0.6, 'rgba(0,0,0,0.14)'); g.addColorStop(1, 'rgba(0,0,0,0)');
        x.fillStyle = g; x.fillRect(0, 0, 128, 128);
        var t = new T.CanvasTexture(c); return t;
      })();

      // FOLIAGE GOBO: the skin's foliage-shadow texture as a soft multiply
      // plane floating just above the wall — the one overlay token, in GL.
      var foliageURL = E.tokenURL(ground, '--tex-foliage');
      var foliageMat = foliageURL ? new T.MeshBasicMaterial({
        map: tex(foliageURL, spanWall * 2), transparent: true, opacity: 0.05, depthWrite: false,
      }) : null;

      // PIVOT/TILT: the ortho camera looks dead-on (relief invisible from the
      // front). A pivot at the wall centre lets the whole world TILT so slab
      // side-faces + zone relief read as real depth. Tilt is a dial
      // (--gl-tilt-x/y, radians) OR driven live by the inspector via
      // handle.setTilt — same token contract as every other axis.
      var pivot = new T.Group();
      var group = new T.Group();
      pivot.add(group);
      scene.add(pivot);
      var tilt = { x: dial('--gl-tilt-x', 0), y: dial('--gl-tilt-y', 0) };
      var wall = null;

      // rounded-rect slab: extruded shape → real thickness + side faces
      function slab(w, h, r, d) {
        var s = new T.Shape();
        r = Math.min(r, w / 2, h / 2);
        s.moveTo(r, 0); s.lineTo(w - r, 0); s.absarc(w - r, r, r, -Math.PI / 2, 0);
        s.lineTo(w, h - r); s.absarc(w - r, h - r, r, 0, Math.PI / 2);
        s.lineTo(r, h); s.absarc(r, h - r, r, Math.PI / 2, Math.PI);
        s.lineTo(0, r); s.absarc(r, r, r, Math.PI, Math.PI * 1.5);
        return new T.ExtrudeGeometry(s, { depth: d, bevelEnabled: true, bevelThickness: 1.2, bevelSize: 1.2, bevelSegments: 2, curveSegments: 6 });
      }

      function sync() {
        var W = ground.clientWidth, H = ground.clientHeight;
        if (!W || !H) return;
        renderer.setSize(W, H, false);
        var z = px(getComputedStyle(ground).getPropertyValue('--world-zoom')) || zoom;
        var panX = px(getComputedStyle(ground).getPropertyValue('--world-pan-x'));
        var panY = px(getComputedStyle(ground).getPropertyValue('--world-pan-y'));
        cam.left = -panX / z; cam.right = (W - panX) / z;
        cam.top = panY / z; cam.bottom = -(H - panY) / z;
        cam.position.set(0, 0, 300); cam.lookAt(0, 0, 0);
        cam.updateProjectionMatrix();

        // apply the tilt about the wall centre (pivot at centre, group offset back)
        var cx = W / 2, cy = -H / 2;
        pivot.position.set(cx, cy, 0);
        group.position.set(-cx, -cy, 0);
        pivot.rotation.set(tilt.x, tilt.y, 0);
        // TEXT-PINNING: mirror the pivot tilt onto the DOM content layer (CSS
        // rule in tokens/skins.css reads these) — labels ride their slabs'
        // faces. Signs flip: GL is y-up, CSS y-down. Identity at tilt 0.
        ground.style.setProperty('--gl-dom-tilt-x', (-tilt.x * 180 / Math.PI).toFixed(3) + 'deg');
        ground.style.setProperty('--gl-dom-tilt-y', (-tilt.y * 180 / Math.PI).toFixed(3) + 'deg');

        key.position.set(W * 0.5 - keyX * 600, H * 0.4, 340);
        key.target.position.set(W * 0.5, -H * 0.5, 0); scene.add(key.target);
        var ks = Math.max(W, H) * 0.75;
        key.shadow.camera.left = -ks; key.shadow.camera.right = ks;
        key.shadow.camera.top = ks; key.shadow.camera.bottom = -ks;
        key.shadow.camera.updateProjectionMatrix();
        pool.position.set(W * 0.5, -H * 0.42, 220);
        pool.distance = Math.max(W, H) * 1.1;

        // wall plane (receives shadows; grain at the wall span)
        if (wall) { group.remove(wall); wall.geometry.dispose(); }
        // displacement needs vertices to displace — segments only when a map exists
        wall = new T.Mesh(new T.PlaneGeometry(W * 3, H * 3, wallDispURL ? 96 : 1, wallDispURL ? 96 : 1), wallMat);
        if (wallMat.aoMap) wall.geometry.setAttribute('uv2', wall.geometry.attributes.uv); // aoMap samples uv2
        wall.position.set(W / 2, -H / 2, 0);
        wall.receiveShadow = true;
        if (wallMat.map) wallMat.map.repeat.set((W * 3) / (spanWall * z), (H * 3) / (spanWall * z));
        group.add(wall);
        // foliage gobo floats above the wall, below the slabs
        if (foliageMat) {
          var fol = new T.Mesh(new T.PlaneGeometry(W * 1.4, H * 1.4), foliageMat);
          fol.userData.sharedMat = true;
          fol.position.set(W * 0.28, -H * 0.3, 0.8);
          group.add(fol);
        }

        // slabs from the SOLVED DOM — the layout truth projected into GL.
        // EVERY CONTAINMENT RUNG projects (sector 2, m0510): cards AND their
        // nested zones/wells (.material--inset) — the handover strips their CSS
        // surfaces, so GL MUST re-emit each as its own thin slab on the parent
        // face, exactly the containment ladder in relief.
        group.children.slice().forEach(function (c) { if (c !== wall) { group.remove(c); c.geometry.dispose(); if (!c.userData.sharedMat) { (Array.isArray(c.material) ? c.material : [c.material]).forEach(function (mm) { mm.dispose(); }); } } }); // textures + shared materials are cache-owned — never disposed per sync
        var gb = ground.getBoundingClientRect();
        // THICKNESS IS A TOKEN (sector 3): per-rung relief resolved from the skin
        // cascade — 2D layout stays identical, 3D adds only these dials.
        var thickUnit = dial('--gl-thick-unit', 3.2);   // card slab px per depth rung
        var thickZone = dial('--gl-thick-zone', 1.4);   // nested zones size a LITTLE out
        var sideTint = new T.Color(dial('--gl-side-tint', lightWorld ? '#a89e8c' : '#14171e')); // role ladder side-face (120)
        var slabInfo = new Map(); // el → {zTop} so children stack on the parent FACE
        ground.querySelectorAll('.material[data-depth], .material--inset[data-depth]').forEach(function (el) {
          if (el.closest('[data-skin-ghost]')) return;
          var r = el.getBoundingClientRect();
          if (!r.width || !r.height) return;
          var depth = parseInt(el.getAttribute('data-depth'), 10) || 2;
          var parentEl = el.parentElement && el.parentElement.closest('.material[data-depth], .material--inset[data-depth]');
          var parentInfo = parentEl ? slabInfo.get(parentEl) : null;
          // RUNG KIND IS CONTAINMENT, not class (cards also carry material--inset):
          // a rung nested inside another projected rung is a ZONE — thin relief on
          // the parent face; a top-level rung is a CARD — depth-rung thickness.
          var isNested = !!parentInfo;
          var rad = px(getComputedStyle(el).borderRadius) || 10;
          var thick = isNested ? thickZone : depth * thickUnit;
          var x = (r.left - gb.left - panX) / z, y = (r.top - gb.top - panY) / z;
          var w = r.width / z, h = r.height / z;
          var m = slabMaterial(el);
          if (isNested) { // zone tonal rung: a shade toward the wall (ghost 190 on the ladder)
            if (m.color) m.color.multiplyScalar(dial('--gl-zone-dim', 0.94));
          }
          if (matKind !== 'glass' && faceURL) {
            // WORLD-PHASE UVs (pack-004 parity with --mat-tex-pos): ExtrudeGeometry
            // UVs are SHAPE-SPACE WORLD PX (not 0..1) — repeat must be 1/span so
            // one tile spans exactly the declared physical footprint regardless
            // of slab size (repeat=w/span was the 'zoomed differently per card'
            // defect), and offset pins the tile to WORLD position so no two
            // slabs show the same region.
            function phase(map) {
              map.repeat.set(1 / spanFace, 1 / spanFace);
              map.offset.set(((x % spanFace) + spanFace) % spanFace / spanFace, ((-(y + h) % spanFace) + spanFace) % spanFace / spanFace);
              return map;
            }
            m.map = phase(tex(faceURL, spanFace));
            if (faceNormalURL) { var fn = phase(tex(faceNormalURL, spanFace)); fn.colorSpace = T.NoColorSpace; m.normalMap = fn; m.normalScale = new T.Vector2(0.6, 0.6); }
            if (faceRoughURL) { var fr = phase(tex(faceRoughURL, spanFace)); fr.colorSpace = T.NoColorSpace; m.roughnessMap = fr; m.roughness = 1; }
            if (faceAoURL) { var fa = phase(tex(faceAoURL, spanFace)); fa.colorSpace = T.NoColorSpace; m.aoMap = fa; m.aoMapIntensity = 0.35; }
          }
          var g = slab(w, h, rad, thick);
          if (m.aoMap) g.setAttribute('uv2', g.attributes.uv); // aoMap samples uv2
          // SIDE FACES darker than the top face (role ladder side-face rung):
          // ExtrudeGeometry group 0 = caps, group 1 = walls — a second material,
          // not a second mesh.
          var side = m.clone(); side.map = null; side.normalMap = null; side.roughnessMap = null; side.aoMap = null;
          if (side.color) side.color.copy(sideTint);
          var mesh = new T.Mesh(g, [m, side]);
          mesh.castShadow = true; mesh.receiveShadow = true;
          // STACKING LAW: a nested rung sits ON its parent's face, not at a
          // depth-derived float — relief follows containment.
          var zBase = parentInfo ? parentInfo.zTop + 0.4 : 2 + depth * 1.2;
          mesh.position.set(x, -y - h, zBase);
          slabInfo.set(el, { zTop: zBase + thick });
          group.add(mesh);
          // contact AO pool under the slab (scaled to footprint + depth);
          // nested zones skip it — their contact is the parent face, shadow maps carry it
          if (!parentInfo) {
            var pad = 10 + depth * 4;
            var ao = new T.Mesh(new T.PlaneGeometry(w + pad * 2, h + pad * 2), new T.MeshBasicMaterial({ map: aoTex, transparent: true, depthWrite: false, opacity: Math.min(0.9, 0.35 + depth * 0.12) }));
            ao.position.set(x + w / 2 + depth * 1.6 * (keyX), -y - h / 2 - depth * 1.6, zBase - 0.5);
            group.add(ao);
          }
        });
        render();
      }

      function render() { renderer.render(scene, cam); }

      ground.setAttribute('data-scene-live', '');
      var onCam = function () { sync(); };
      ground.addEventListener('cv:cameramove', onCam);
      var ro = new ResizeObserver(function () { sync(); });
      ro.observe(ground);

      handle.live = true;
      handle.sync = sync;
      // INSPECTOR HOOKS (dev): tilt is live (no rebuild — sync only repositions);
      // material/light dials are token writes + detach/attach (the inspector owns
      // that path). Reading current tilt lets the panel init its sliders.
      handle.setTilt = function (x, y) { tilt.x = x; tilt.y = y; sync(); };
      handle.getTilt = function () { return { x: tilt.x, y: tilt.y }; };
      handle.dispose = function () {
        ro.disconnect();
        ground.removeEventListener('cv:cameramove', onCam);
        ground.removeAttribute('data-scene-live');
        ground.style.removeProperty('--gl-dom-tilt-x');
        ground.style.removeProperty('--gl-dom-tilt-y');
        Object.keys(texCache).forEach(function (k) { texCache[k].dispose(); });
        renderer.dispose();
        canvas.remove();
      };
      sync();
    }).catch(function (e) { console.error('[render-scene] ' + e.message); delete ground.__cvScene; throw e; });

    return handle;
  }

  function sync(ground) {
    // MODE-AWARE: sync re-reads the dial, so turning --scene-mode off (or a
    // skin swap to a CSS-plane skin) detaches; turning it on attaches. One entry.
    var mode = getComputedStyle(ground).getPropertyValue('--scene-mode').trim();
    if (mode !== 'gl') { detach(ground); return; }
    attach(ground); // attach is SIG-AWARE (skin + material): same world = cheap sync, changed world = rebuild from the new skin's tokens (m0587: sync() kept stone's world after a swap to glass)
  }

  function detach(ground) {
    if (!ground.__cvScene) return;
    var h = ground.__cvScene;
    delete ground.__cvScene;
    if (h.dispose) h.dispose();
  }

  window.CV_SCENE = { attach: attach, sync: sync, detach: detach };
})();
