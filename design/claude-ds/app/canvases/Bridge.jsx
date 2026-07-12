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
const { useState: useState_br, useEffect: useEffect_br, useReducer: useReducer_br } = React;

function useHost() {
  const [, force] = useReducer_br(x => x + 1, 0);
  useEffect_br(() => window.CV_HOST.subscribe(force), []);
  return window.CV_HOST;
}

const CAP_LABEL = { read: 'read files', write: 'write files', list: 'list dirs', exec: 'run compiler', tools: 'call tools' };

function Bridge() {
  const HOST = useHost();
  const d = HOST.describe();
  const [busy, setBusy] = useState_br(null);

  async function activate(id) {
    setBusy(id);
    try {
      if (id === '__reconnect') await HOST.reconnectFsapi();
      else await HOST.runtimes.get(id).activate();
      window.dsaToast?.('Connected — disk access on');
    } catch (e) { window.dsaToast?.(e.message); }
    setBusy(null);
  }

  return (
    <div className="dsa-canvas-scroll" style={{ padding: '28px 32px 64px', maxWidth: 1080, margin: '0 auto' }}>
      <header style={{ marginBottom: 22 }}>
        <h1 style={{ font: '700 30px/1.05 var(--font-display)', color: 'var(--accent-bronze)', margin: '0 0 6px', letterSpacing: '-0.02em' }}>Bridge</h1>
        <p style={{ font: '400 14px/1.6 var(--font-body)', color: 'var(--fg-secondary)', margin: 0, maxWidth: 660 }}>
          Where Vi reaches the repository. In the sandbox, changes are serialized to real source and staged for review. Connect a file runtime — here in the browser, or via a local shell when you export — and Vi writes them to disk directly.
        </p>
      </header>

      {/* ENVIRONMENT --------------------------------------------------------*/}
      <EnvCard d={d} />

      {/* RUNTIMES -----------------------------------------------------------*/}
      <Section title="Runtimes" sub="Ways to reach the world. The best available one handles each operation; sandbox review is the floor.">
        <div style={{ display: 'grid', gap: 10 }}>
          {d.runtimes.map(r => (
            <div key={r.id} style={{
              display: 'flex', alignItems: 'flex-start', gap: 14, padding: '14px 16px',
              border: '1px solid var(--border-soft)', borderRadius: 'var(--r-lg)',
              background: r.available ? 'var(--accent-gold-50)' : 'var(--bg-surface)',
              opacity: r.supported ? 1 : 0.55,
            }}>
              <Dot on={r.available} />
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
                  <strong style={{ font: '600 14px var(--font-body)', color: 'var(--fg-primary)' }}>{r.label}</strong>
                  <span style={{ font: '500 11px var(--font-mono)', color: 'var(--fg-muted)' }}>
                    {Object.keys(r.caps).filter(k => r.caps[k]).map(k => CAP_LABEL[k]).join(' · ') || 'staging only'}
                  </span>
                  {r.available && <span style={{ marginLeft: 'auto', font: '600 11px var(--font-mono)', color: 'var(--status-success)' }}>ACTIVE</span>}
                </div>
                <p style={{ font: '400 12.5px/1.55 var(--font-body)', color: 'var(--fg-secondary)', margin: '4px 0 0' }}>{r.description}</p>
                {r.canActivate && !r.available && (
                  <button className="dsa-btn dsa-btn--outline dsa-btn--sm" style={{ marginTop: 8 }}
                    disabled={!r.supported || busy === r.id} onClick={() => activate(r.id)}>
                    {busy === r.id ? 'Connecting…' : (r.supported ? 'Connect…' : 'Not supported here')}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
        {window.__cvFsapiPending && !d.capabilities.write && (
          <button className="dsa-btn dsa-btn--solid dsa-btn--sm" style={{ marginTop: 10 }} onClick={() => activate('__reconnect')}>
            Reconnect last folder
          </button>
        )}
      </Section>

      {/* HANDOFF SETTING ----------------------------------------------------*/}
      <Section title="When there's no disk access" sub="How a committed change is handed off in the sandbox. It is always staged below; these add to that.">
        <div style={{ display: 'grid', gap: 8 }}>
          {Object.entries(d.handoff.modes).map(([k, m]) => (
            <label key={k} style={{ display: 'flex', gap: 10, padding: '11px 14px', border: '1px solid var(--border-soft)', borderRadius: 'var(--r-md)', cursor: 'pointer', background: d.handoff.mode === k ? 'var(--accent-gold-50)' : 'transparent' }}>
              <input type="radio" name="handoff" checked={d.handoff.mode === k} onChange={() => HOST.setHandoffMode(k)} style={{ marginTop: 3 }} />
              <div>
                <strong style={{ font: '600 13px var(--font-body)', color: 'var(--fg-primary)' }}>{m.label}</strong>
                <p style={{ font: '400 12px/1.5 var(--font-body)', color: 'var(--fg-secondary)', margin: '2px 0 0' }}>{m.desc}</p>
              </div>
            </label>
          ))}
        </div>
        <label style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 12, font: '400 13px var(--font-body)', color: 'var(--fg-secondary)' }}>
          <input type="checkbox" checked={d.handoff.autoApply} onChange={e => HOST.setAutoApply(e.target.checked)} />
          Auto-apply to disk when a writer is connected (skip staging). Off by default.
        </label>
      </Section>

      {/* CHANGES ------------------------------------------------------------*/}
      <Changes HOST={HOST} d={d} />

      {/* STASH (agent loop) -------------------------------------------------*/}
      {d.stash > 0 && (
        <Section title={`Agent stash (${d.stash})`} sub="Serialized changes waiting for Claude to read back and commit on the next turn. Copy this if you're driving the loop manually.">
          <div style={{ display: 'flex', gap: 8 }}>
            <button className="dsa-btn dsa-btn--outline dsa-btn--sm" onClick={() => { navigator.clipboard?.writeText(JSON.stringify(HOST.readStash(), null, 2)); window.dsaToast?.('Stash copied'); }}>Copy stash JSON</button>
            <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => { HOST.clearStash(); HOST.notify(); }}>Clear stash</button>
          </div>
        </Section>
      )}

      {/* WHAT VI CAN DO (projection of CV_AI repo capabilities) -------------*/}
      <Section title="What Vi can do here" sub="Repo capabilities in the AI catalogue, routed through the same execute() path as every other Vi move.">
        <div style={{ display: 'grid', gap: 6 }}>
          {window.CV_AI.query({ family: 'repo' }).map(c => (
            <div key={c.id} style={{ display: 'flex', gap: 10, font: '400 12.5px/1.5 var(--font-body)', color: 'var(--fg-secondary)' }}>
              <code style={{ font: '600 12px var(--font-mono)', color: 'var(--accent-bronze)', minWidth: 110 }}>{c.id}</code>
              <span>{c.description}</span>
            </div>
          ))}
        </div>
        <p style={{ font: '400 12px/1.55 var(--font-body)', color: 'var(--fg-muted)', margin: '14px 0 0' }}>
          Serializers (one home per change kind): {d.serializers.map(s => s.kind).join(' · ')}.
        </p>
      </Section>
    </div>
  );
}

function EnvCard({ d }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 18, padding: '18px 22px', borderRadius: 'var(--r-xl)', background: 'var(--bg-dark)', color: 'var(--fg-inverse)', marginBottom: 6 }}>
      <div>
        <div style={{ font: '500 11px var(--font-mono)', opacity: 0.6, letterSpacing: '0.08em' }}>ENVIRONMENT</div>
        <div style={{ font: '700 22px var(--font-display)', letterSpacing: '-0.01em' }}>{d.modeLabel}</div>
      </div>
      <div style={{ display: 'flex', gap: 7, marginLeft: 'auto', flexWrap: 'wrap', justifyContent: 'flex-end' }}>
        {Object.entries(d.capabilities).map(([k, on]) => (
          <span key={k} style={{
            font: '600 11px var(--font-mono)', padding: '4px 9px', borderRadius: 999,
            background: on ? 'var(--accent-gold)' : 'rgba(255,255,255,.08)',
            color: on ? 'var(--bg-dark)' : 'rgba(255,255,255,.5)',
          }}>{CAP_LABEL[k]}</span>
        ))}
      </div>
    </div>
  );
}

function Changes({ HOST, d }) {
  const list = HOST.changes.list();
  const staged = list.filter(c => c.status === 'staged');
  return (
    <Section title={`Proposed changes${staged.length ? ` (${staged.length} staged)` : ''}`} sub="Each is real source for its one home file. Apply writes it to disk (needs a connected writer); Copy hands you the snippet.">
      {!list.length && (
        <div className="dsa-stub" style={{ padding: 28, textAlign: 'center', border: '1px dashed var(--border-soft)', borderRadius: 'var(--r-lg)' }}>
          <p style={{ font: '400 13px var(--font-body)', color: 'var(--fg-muted)', margin: 0 }}>No changes yet. When Vi proposes one (or you call <code style={{ font: '600 12px var(--font-mono)', color: 'var(--accent-bronze)' }}>ds.propose</code>), it appears here as reviewable source.</p>
        </div>
      )}
      <div style={{ display: 'grid', gap: 12 }}>
        {list.map(c => <ChangeRow key={c.id} c={c} HOST={HOST} canWrite={d.canWrite} />)}
      </div>
    </Section>
  );
}

function ChangeRow({ c, HOST, canWrite }) {
  const [open, setOpen] = useState_br(false);
  const [busy, setBusy] = useState_br(false);
  const statusColor = { staged: 'var(--accent-bronze)', applied: 'var(--status-success)', rejected: 'var(--fg-muted)' }[c.status];
  async function apply() {
    setBusy(true);
    try { await HOST.changes.apply(c.id); window.dsaToast?.('Written to ' + c.serialized.file); }
    catch (e) { window.dsaToast?.(e.message); }
    setBusy(false);
  }
  return (
    <div style={{ border: '1px solid var(--border-soft)', borderRadius: 'var(--r-lg)', overflow: 'hidden', opacity: c.status === 'rejected' ? 0.5 : 1 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 16px', background: 'var(--bg-surface)' }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 8 }}>
            <strong style={{ font: '600 14px var(--font-body)', color: 'var(--fg-primary)' }}>{c.title}</strong>
            <span style={{ font: '600 10px var(--font-mono)', color: statusColor, textTransform: 'uppercase', letterSpacing: '0.06em' }}>{c.status}</span>
            <span style={{ font: '500 11px var(--font-mono)', color: c.provenance === 'vi' ? 'var(--accent-gold-deep)' : 'var(--fg-muted)' }}>{c.provenance}</span>
          </div>
          <div style={{ font: '500 11.5px var(--font-mono)', color: 'var(--fg-muted)', marginTop: 2 }}>→ {c.serialized.file} <span style={{ opacity: 0.6 }}>· {c.serialized.strategy}</span></div>
          {c.rationale && <p style={{ font: '400 12px/1.5 var(--font-body)', color: 'var(--fg-secondary)', margin: '4px 0 0' }}>{c.rationale}</p>}
        </div>
        <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => setOpen(o => !o)}>{open ? 'Hide' : 'Source'}</button>
        <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => { navigator.clipboard?.writeText(c.serialized.source); window.dsaToast?.('Copied'); }}>Copy</button>
        {c.status === 'staged' && <button className="dsa-btn dsa-btn--solid dsa-btn--sm" disabled={!canWrite || busy} title={canWrite ? '' : 'Connect a writer first'} onClick={apply}>{busy ? 'Writing…' : 'Apply'}</button>}
        {c.status === 'staged' && <button className="dsa-btn dsa-btn--ghost dsa-btn--sm" onClick={() => HOST.changes.reject(c.id)}>✕</button>}
      </div>
      {open && (
        <pre style={{ margin: 0, padding: '14px 16px', background: 'var(--bg-dark)', color: 'var(--fg-inverse)', font: '400 11.5px/1.55 var(--font-mono)', whiteSpace: 'pre', overflow: 'auto', maxHeight: '40vh' }}>{c.serialized.source}</pre>
      )}
    </div>
  );
}

function Section({ title, sub, children }) {
  return (
    <section style={{ marginTop: 28 }}>
      <h2 style={{ font: '600 16px var(--font-display)', color: 'var(--fg-primary)', margin: '0 0 3px' }}>{title}</h2>
      {sub && <p style={{ font: '400 12.5px/1.55 var(--font-body)', color: 'var(--fg-muted)', margin: '0 0 12px', maxWidth: 640 }}>{sub}</p>}
      {children}
    </section>
  );
}

function Dot({ on }) {
  return <span style={{ width: 9, height: 9, borderRadius: 999, marginTop: 5, flex: 'none', background: on ? 'var(--status-success)' : 'var(--border-strong)' }} />;
}

window.Bridge = Bridge;
