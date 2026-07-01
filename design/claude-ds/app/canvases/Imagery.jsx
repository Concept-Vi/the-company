// canvases/Imagery.jsx — the imagery subsystem of ConceptV Studio.
// Four lanes share one canvas: System library, Project imagery, 360° Hubs, AI Studio.
//
// Every action routes through window.cvImageStore (persistence) and
// window.cvOpenAI (generation). The same imagery can be promoted across
// scopes — adopt an AI generation into System, drop a System image into a
// Project, send a Project image into 360° editing, etc.

const { useState: useState_im, useEffect: useEffect_im, useMemo: useMemo_im, useRef: useRef_im } = React;

const TABS = [
  { id: 'system',   label: 'System library',  icon: 'image-stack', sub: 'Brand-wide imagery — referenced by every output you publish.' },
  { id: 'projects', label: 'Projects',        icon: 'folder',      sub: 'Photos, renders, captures, and drone shots for each property.' },
  { id: 'hubs',     label: '360° Hubs',       icon: 'vr-headset',  sub: 'Equirectangular panoramas powering Virtual Hubs.' },
  { id: 'ai',       label: 'AI Studio',       icon: 'atom',        sub: 'Generate, edit, and refine imagery with Vi via OpenAI.' },
];

const SYSTEM_TAGS = ['Brand hero', 'Interior render', 'Exterior render', 'Drone', 'Detail', 'Texture', 'Mood reference', 'Stakeholders'];
const PROJECT_TAGS = ['Hero', 'Floorplan', 'Render', 'Capture', 'Drone', 'Detail'];

function Imagery({ onNav }) {
  const [tab, setTab]             = useState_im('system');
  const [, force]                 = useState_im(0);
  const [editing, setEditing]     = useState_im(null); // {scope, pid, image}
  const [openAIReady, setOpenAIReady] = useState_im(window.cvOpenAI.isConfigured());

  // Subscribe to store + settings changes
  useEffect_im(() => window.cvImageStore.subscribe(() => force(t => t + 1)), []);
  useEffect_im(() => window.cvOpenAI.subscribe(() => setOpenAIReady(window.cvOpenAI.isConfigured())), []);

  const counts = window.cvImageStore.counts();

  function openEditor(scope, pid, image) {
    setEditing({ scope, pid, image });
  }
  function closeEditor() { setEditing(null); }
  function saveEdit(newSrc) {
    if (!editing) return;
    window.cvImageStore.update(editing.scope, editing.pid, editing.image.id, { src: newSrc });
    setEditing(null);
    window.dsaToast?.('Image saved');
  }

  return (
    <>
      <CanvasHeader
        title="Imagery"
        sub="The full image subsystem — system-wide brand library, per-project assets, 360° hubs, and the AI Studio where Vi generates new material."
        actions={
          <>
            <span className={`cv-im-pill ${openAIReady ? 'ok' : 'warn'}`}>
              <span className="dot"/>{openAIReady ? `Vi · ${window.cvOpenAI.getSettings().imageModel}` : 'Vi · disconnected'}
            </span>
            <button className="dsa-btn dsa-btn--outline" onClick={() => onNav?.('settings')}>
              <CvIcon name="gear" size={12} tone="bronze"/> {openAIReady ? 'Settings' : 'Connect OpenAI'}
            </button>
          </>
        }
      />
      <div className="dsa-canvas-body cv-im-body">
        {/* Tabs */}
        <div className="cv-im-tabs">
          {TABS.map(t => {
            const c = t.id === 'system' ? counts.system : t.id === 'projects' ? counts.projects : t.id === 'hubs' ? counts.hubs : counts.ai;
            return (
              <button key={t.id} className={`cv-im-tab ${tab === t.id ? 'active' : ''}`} onClick={() => setTab(t.id)}>
                <CvIcon name={t.icon} size={14} tone={tab === t.id ? 'gold' : 'bronze'}/>
                <span className="lbl">{t.label}</span>
                <span className="ct">{c}</span>
              </button>
            );
          })}
        </div>
        <p className="cv-im-tab-sub">{TABS.find(t => t.id === tab)?.sub}</p>

        {tab === 'system'   && <SystemLane openEditor={openEditor}/>}
        {tab === 'projects' && <ProjectsLane openEditor={openEditor}/>}
        {tab === 'hubs'     && <HubsLane/>}
        {tab === 'ai'       && <AIStudio onNav={onNav} openEditor={openEditor}/>}
      </div>

      {editing && (
        <ImageEditor
          image={editing.image}
          onClose={closeEditor}
          onSave={saveEdit}
        />
      )}
    </>
  );
}

/* =====================================================================
   SYSTEM LIBRARY
   ===================================================================== */
function SystemLane({ openEditor }) {
  const [filter, setFilter] = useState_im(null);
  const [over, setOver] = useState_im(false);
  const fileRef = useRef_im(null);
  const list = window.cvImageStore.list('system');

  const filtered = filter ? list.filter(im => (im.tags || []).includes(filter)) : list;

  async function onFiles(files) {
    for (const f of files) {
      try { await window.cvImageStore.addFromFile('system', null, f, { tags: ['Brand hero'] }); }
      catch { window.dsaToast?.(`Could not import ${f.name}`); }
    }
    window.dsaToast?.(`Added ${files.length} image${files.length === 1 ? '' : 's'} to system library`);
  }

  async function seedStarter() {
    const starter = [
      { src: '../assets/illustrations/staged_delivery.png',  name: 'Staged delivery diagram',  tags: ['Mood reference'] },
      { src: '../assets/illustrations/platform_overview.png', name: 'Platform overview',        tags: ['Stakeholders'] },
      { src: '../assets/illustrations/vi_ai_framework.jpg',   name: 'Vi framework layers',      tags: ['Stakeholders'] },
      { src: '../assets/illustrations/sales_flywheel.png',    name: 'Sales flywheel',           tags: ['Mood reference'] },
      { src: '../assets/illustrations/stats_panels.png',      name: 'Stats panel reference',    tags: ['Mood reference'] },
      { src: '../assets/illustrations/stakeholders_network.jpg', name: 'Stakeholder network',   tags: ['Stakeholders'] },
    ];
    for (const item of starter) {
      try { await window.cvImageStore.addFromSrc('system', null, item.src, { name: item.name, tags: item.tags, source: 'starter' }); }
      catch {}
    }
    window.dsaToast?.(`Seeded ${starter.length} brand references`);
  }

  return (
    <>
      <div className="cv-im-toolbar">
        <div className="cv-im-tagbar">
          <button className={!filter ? 'active' : ''} onClick={() => setFilter(null)}>All</button>
          {SYSTEM_TAGS.map(t => (
            <button key={t} className={filter === t ? 'active' : ''} onClick={() => setFilter(t)}>{t}</button>
          ))}
        </div>
        <button className="dsa-btn dsa-btn--outline" onClick={seedStarter} title="Import a starter set of brand references">
          <CvIcon name="cloud-download" size={12} tone="bronze"/> Seed starter set
        </button>
        <button className="dsa-btn dsa-btn--primary" onClick={() => fileRef.current?.click()}>
          <CvIcon name="plus" size={12} tone="ink"/> Upload imagery
        </button>
        <input ref={fileRef} type="file" accept="image/*" multiple style={{ display: 'none' }}
          onChange={e => onFiles([...e.target.files])}/>
      </div>

      <div className={`dsa-drop cv-im-drop ${over ? 'over' : ''}`}
        onDragOver={e => { e.preventDefault(); setOver(true); }}
        onDragLeave={() => setOver(false)}
        onDrop={e => {
          e.preventDefault(); setOver(false);
          onFiles([...e.dataTransfer.files].filter(f => f.type.startsWith('image/')));
        }}
        onClick={() => fileRef.current?.click()}>
        <div className="plus"><CvIcon name="cloud-upload" size={22} tone="ink"/></div>
        <div className="label">Drop imagery into the system library</div>
        <div className="hint">JPEG, PNG, or WebP. Vi will tag each upload by mood + lighting and propose where in the brand it fits.</div>
      </div>

      {list.length > 0 && (
        <div className="cv-im-grid">
          {filtered.map(im => (
            <ImageCard key={im.id} image={im} scope="system"
              onEdit={() => openEditor('system', null, im)}
              onRemove={() => { window.cvImageStore.remove('system', null, im.id); window.dsaToast?.('Removed'); }}
            />
          ))}
        </div>
      )}
    </>
  );
}

/* =====================================================================
   PROJECTS
   ===================================================================== */
function ProjectsLane({ openEditor }) {
  const projects = window.cvImageStore.listProjects();
  const [pid, setPid] = useState_im(projects[0]?.id);
  const [over, setOver] = useState_im(false);
  const fileRef = useRef_im(null);

  const list = pid ? window.cvImageStore.list('projects', pid) : [];

  async function onFiles(files) {
    for (const f of files) {
      try { await window.cvImageStore.addFromFile('projects', pid, f); }
      catch { window.dsaToast?.(`Could not import ${f.name}`); }
    }
    window.dsaToast?.(`Added ${files.length} to ${projects.find(p => p.id === pid)?.name}`);
  }

  async function newProject() {
    const name = prompt('Project name');
    if (!name) return;
    const client = prompt('Client / developer (optional)') || '';
    const p = window.cvImageStore.addProject({ name, client });
    setPid(p.id);
  }

  return (
    <div className="cv-im-projects">
      <aside className="cv-im-proj-rail">
        <div className="cv-im-proj-head">
          <h4>Projects</h4>
          <button className="cv-im-proj-add" title="New project" onClick={newProject}>+</button>
        </div>
        {projects.map(p => (
          <button key={p.id} className={`cv-im-proj ${pid === p.id ? 'active' : ''}`} onClick={() => setPid(p.id)}>
            <span className="cv-im-proj-shape"><Octagon/></span>
            <div className="cv-im-proj-meta">
              <span className="cv-im-proj-name">{p.name}</span>
              <span className="cv-im-proj-client">{p.client || '—'}</span>
            </div>
            <span className="cv-im-proj-count">{window.cvImageStore.list('projects', p.id).length}</span>
          </button>
        ))}
      </aside>

      <div className="cv-im-proj-main">
        {pid && (
          <>
            <div className="cv-im-toolbar">
              <div className="cv-im-tagbar">
                <button className="active">All</button>
                {PROJECT_TAGS.map(t => <button key={t}>{t}</button>)}
              </div>
              <button className="dsa-btn dsa-btn--primary" onClick={() => fileRef.current?.click()}>
                <CvIcon name="plus" size={12} tone="ink"/> Upload to project
              </button>
              <input ref={fileRef} type="file" accept="image/*" multiple style={{ display: 'none' }}
                onChange={e => onFiles([...e.target.files])}/>
            </div>

            <div className={`dsa-drop cv-im-drop ${over ? 'over' : ''}`}
              onDragOver={e => { e.preventDefault(); setOver(true); }}
              onDragLeave={() => setOver(false)}
              onDrop={e => { e.preventDefault(); setOver(false); onFiles([...e.dataTransfer.files].filter(f => f.type.startsWith('image/'))); }}
              onClick={() => fileRef.current?.click()}>
              <div className="plus"><CvIcon name="cloud-upload" size={22} tone="ink"/></div>
              <div className="label">Drop imagery for <b>{projects.find(p => p.id === pid)?.name}</b></div>
              <div className="hint">Project imagery is scoped — Vi will only show it in this project's hubs, landing pages, and brochures.</div>
            </div>

            {list.length > 0 && (
              <div className="cv-im-grid">
                {list.map(im => (
                  <ImageCard key={im.id} image={im} scope="projects"
                    onEdit={() => openEditor('projects', pid, im)}
                    onRemove={() => window.cvImageStore.remove('projects', pid, im.id)}
                    onPromote={() => {
                      window.cvImageStore.addFromSrc('system', null, im.src, { name: im.name, tags: ['Brand hero'], source: 'promoted' });
                      window.dsaToast?.('Promoted to system library');
                    }}
                  />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

/* =====================================================================
   360° HUBS
   ===================================================================== */
function HubsLane() {
  const projects = window.cvImageStore.listProjects();
  const [pid, setPid] = useState_im(projects[0]?.id);
  const [active, setActive] = useState_im(null);
  const [, force] = useState_im(0);
  const fileRef = useRef_im(null);

  const panos = pid ? window.cvImageStore.list('hubs', pid) : [];
  const current = panos.find(p => p.id === active) || panos[0];

  async function onFiles(files) {
    for (const f of files) {
      try { await window.cvImageStore.addFromFile('hubs', pid, f, { name: f.name.replace(/\.[^.]+$/, '') }); }
      catch { window.dsaToast?.(`Could not import ${f.name}`); }
    }
    window.dsaToast?.(`Added ${files.length} pano${files.length === 1 ? '' : 's'}`);
  }

  function addHotspot(pos) {
    if (!current) return;
    const label = prompt('Hotspot label (e.g. "Kitchen", "To Balcony")');
    if (!label) return;
    const next = [...(current.hotspots || []), { id: 'h_' + Math.random().toString(36).slice(2,8), lon: pos.lon, lat: pos.lat, label }];
    window.cvImageStore.update('hubs', pid, current.id, { hotspots: next });
    force(t => t + 1);
  }
  function removeHotspot(id) {
    if (!current) return;
    const next = (current.hotspots || []).filter(h => h.id !== id);
    window.cvImageStore.update('hubs', pid, current.id, { hotspots: next });
    force(t => t + 1);
  }
  function rename() {
    const name = prompt('Pano name', current?.name);
    if (!name || !current) return;
    window.cvImageStore.update('hubs', pid, current.id, { name });
  }

  return (
    <div className="cv-im-hubs">
      <aside className="cv-im-proj-rail">
        <div className="cv-im-proj-head"><h4>Projects</h4></div>
        {projects.map(p => (
          <button key={p.id} className={`cv-im-proj ${pid === p.id ? 'active' : ''}`} onClick={() => { setPid(p.id); setActive(null); }}>
            <span className="cv-im-proj-shape"><Octagon/></span>
            <div className="cv-im-proj-meta">
              <span className="cv-im-proj-name">{p.name}</span>
              <span className="cv-im-proj-client">{window.cvImageStore.list('hubs', p.id).length} pano{window.cvImageStore.list('hubs', p.id).length === 1 ? '' : 's'}</span>
            </div>
          </button>
        ))}
      </aside>

      <div className="cv-im-hubs-main">
        <div className="cv-im-toolbar">
          <div className="cv-im-pano-strip">
            {panos.map(p => (
              <button key={p.id} className={`cv-im-pano-thumb ${current?.id === p.id ? 'active' : ''}`} onClick={() => setActive(p.id)}>
                <img src={p.src} alt=""/>
                <span className="lbl">{p.name}</span>
              </button>
            ))}
            <button className="cv-im-pano-add" onClick={() => fileRef.current?.click()}>
              <CvIcon name="plus" size={14} tone="bronze"/>
              <span>Add pano</span>
            </button>
            <input ref={fileRef} type="file" accept="image/*" multiple style={{ display: 'none' }}
              onChange={e => onFiles([...e.target.files])}/>
          </div>
        </div>

        {current ? (
          <>
            <div className="cv-im-pano-card">
              <div className="cv-im-pano-card-head">
                <div>
                  <h3>{current.name}</h3>
                  <span className="meta">Equirectangular · {current.w}×{current.h} · {(current.hotspots || []).length} hotspot{(current.hotspots || []).length === 1 ? '' : 's'}</span>
                </div>
                <div className="cv-im-pano-actions">
                  <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={rename}><CvIcon name="edit" size={11} tone="bronze"/> Rename</button>
                  <button className="dsa-btn dsa-btn--outline dsa-btn--sm"
                    onClick={() => { window.cvImageStore.remove('hubs', pid, current.id); setActive(null); }}>
                    Delete
                  </button>
                </div>
              </div>
              <Pano360
                src={current.src}
                hotspots={current.hotspots || []}
                editable={true}
                onAddHotspot={addHotspot}
                onRemoveHotspot={removeHotspot}
                height={460}
              />
              <div className="cv-im-pano-hotspot-list">
                <h5>Hotspots</h5>
                {(current.hotspots || []).length === 0 && <span className="cv-im-empty-line">No hotspots yet — double-click on the pano to add one.</span>}
                {(current.hotspots || []).map(h => (
                  <div key={h.id} className="cv-im-hotspot-row">
                    <span className="pin"/>
                    <span className="lbl">{h.label}</span>
                    <span className="coords">lon {h.lon.toFixed(1)}°, lat {h.lat.toFixed(1)}°</span>
                    <button onClick={() => removeHotspot(h.id)}>Remove</button>
                  </div>
                ))}
              </div>
            </div>
            <div className="cv-im-pano-url">
              <span className="cv-eyebrow">Hub URL preview</span>
              <code>https://conceptv.io/panotours/<span style={{color:'var(--accent-gold)'}}>yourcompany</span>/<span style={{color:'var(--accent-gold)'}}>{projects.find(p => p.id === pid)?.id}</span>/<span style={{color:'var(--accent-gold)'}}>{current.id}</span></code>
            </div>
          </>
        ) : panos.length === 0 ? (
          <EmptyStateImagery scope="hub"/>
        ) : (
          <div className="cv-im-empty-line" style={{ padding: 24 }}>Select a pano above to view.</div>
        )}
      </div>
    </div>
  );
}

/* =====================================================================
   AI STUDIO — implemented in canvases/AIStudio.jsx and registered as
   window.AIStudio. It is referenced as <AIStudio/> below.
   ===================================================================== */


/* =====================================================================
   Shared bits
   ===================================================================== */
function ImageCard({ image, scope, onEdit, onRemove, onPromote }) {
  return (
    <div className="cv-im-card">
      <div className="cv-im-card-thumb">
        <img src={image.src} alt=""/>
        <div className="cv-im-card-overlay">
          <button title="Edit" onClick={onEdit}><CvIcon name="edit" size={13} tone="ink"/></button>
          {onPromote && <button title="Promote to system" onClick={onPromote}><CvIcon name="cloud-upload" size={13} tone="ink"/></button>}
          <button title="Remove" onClick={onRemove}><CvIcon name="close" size={13} tone="ink"/></button>
        </div>
      </div>
      <div className="cv-im-card-meta">
        <div className="cv-im-card-name">{image.name}</div>
        <div className="cv-im-card-tags">
          {(image.tags || []).slice(0, 3).map(t => <span key={t} className="cv-im-tag">{t}</span>)}
          {image.source === 'ai' && <span className="cv-im-tag cv-im-tag--ai"><ViShape size={9}/> AI</span>}
        </div>
        <div className="cv-im-card-dims">{image.w}×{image.h}</div>
      </div>
    </div>
  );
}

function EmptyStateImagery({ scope }) {
  const msg = {
    system:  ['Your system library is empty.',  'Drop brand photography or generate hero imagery with Vi. Every output in the studio will pull from here.'],
    project: ['No imagery for this project yet.', 'Upload renders, captures, drone shots, and plans. Vi will recommend which to use across hubs and brochures.'],
    hub:     ['No 360° panos yet.',              'Upload an equirectangular JPEG (2:1 aspect, ideally 4096+ wide). Drag to look around, double-click to tag hotspots.'],
  }[scope] || ['Empty', 'Add imagery to get started.'];
  return (
    <div className="cv-im-empty">
      <div className="cv-im-empty-shape"><Diamond/></div>
      <h4>{msg[0]}</h4>
      <p>{msg[1]}</p>
    </div>
  );
}

function Octagon() {
  return (
    <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="var(--accent-bronze)" strokeWidth="1.5" strokeLinejoin="round">
      <path d="M9 2 H15 L22 9 V15 L15 22 H9 L2 15 V9 Z"/>
    </svg>
  );
}
function Diamond() {
  return (
    <svg viewBox="0 0 40 40" width="44" height="44" fill="none" stroke="var(--accent-bronze)" strokeWidth="1.5">
      <path d="M20 4 L36 20 L20 36 L4 20 Z"/>
      <path d="M12 12 L28 28 M28 12 L12 28" strokeDasharray="2 3" opacity="0.5"/>
    </svg>
  );
}

window.Imagery = Imagery;
