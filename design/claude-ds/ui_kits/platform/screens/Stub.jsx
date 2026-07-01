// screens/Stub.jsx — placeholder for screens that aren't fully built out
function Stub({ title, note }) {
  return (
    <>
      <h1 className="cv-screen-title">{title}</h1>
      <div style={{
        background: 'var(--bg-muted)',
        borderRadius: 'var(--r-lg)',
        padding: '40px 32px',
        color: 'var(--fg-secondary)',
        font: '400 14px/1.55 var(--font-body)',
        maxWidth: 640,
        textAlign: 'center',
      }}>
        <div style={{font:'600 11px/1 var(--font-body)',color:'var(--accent-bronze)',letterSpacing:'.08em',textTransform:'uppercase',marginBottom:10}}>Not implemented in this kit</div>
        {note || `The ${title} surface follows the same shell + soft-gold-panel patterns as the other screens. Add it by composing the Sidebar + TopBar + sections from this kit.`}
      </div>
    </>
  );
}
window.Stub = Stub;
