// ChatPanel.jsx — Vi conversation surface
const { useEffect: useEffect_c, useRef: useRef_c } = React;

function EntityIcon({ kind }) {
  const map = {
    brandkit:  '🎨',
    master:    '📋',
    gallery:   '📷',
    analytics: '📊',
    files:     '📁',
    pricing:   '💰',
    contact:   '👤',
  };
  return <span style={{fontSize:13}}>{map[kind] || '📄'}</span>;
}

function ReadCard({ entity, kind, done }) {
  return (
    <div className={`vi-read-card ${done ? 'done' : ''}`}>
      <span className="icn">{done ? '✓' : <EntityIcon kind={kind}/>}</span>
      <span className="grow">{done ? 'Read' : 'Reading'} <span className="ent">{entity}</span></span>
      {!done && <ViMark size={18} animated showGlyph={false}/>}
    </div>
  );
}

function MissingPrompt({ label, question, placeholder, value, onChange, onSubmit, submitted }) {
  return (
    <div className="vi-prompt">
      <span className="label">Missing · {label}</span>
      <span className="q">{question}</span>
      {submitted ? (
        <div style={{font:'500 13px/1 var(--font-body)',color:'var(--accent-gold)',display:'flex',alignItems:'center',gap:8}}>
          <span style={{color:'var(--status-success)'}}>✓</span> {value}
        </div>
      ) : (
        <>
          <input className="vi-prompt-input" placeholder={placeholder} value={value} onChange={e=>onChange(e.target.value)} onKeyDown={e=>e.key==='Enter' && onSubmit?.()}/>
          <button className="btn" onClick={onSubmit} style={{alignSelf:'flex-end',background:'var(--accent-gold)',color:'var(--fg-primary)',border:'none',borderRadius:'var(--r-sm)',padding:'7px 14px',font:'700 12px/1 var(--font-body)',cursor:'pointer'}}>Send</button>
        </>
      )}
    </div>
  );
}

function ApproveCard({ text, sub, onApprove }) {
  return (
    <div className="vi-approve">
      <div className="text">{text}<small>{sub}</small></div>
      <button onClick={onApprove}>Approve</button>
    </div>
  );
}

function Message({ from, time, children }) {
  if (from === 'user') {
    return (
      <div className="vi-msg">
        <div className="vi-msg-avatar user">
          <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 12 a4 4 0 1 0 0-8 a4 4 0 0 0 0 8 Z M4 22 a8 8 0 0 1 16 0 Z"/></svg>
        </div>
        <div className="vi-msg-body">
          <div className="vi-msg-name">You <span className="meta">{time}</span></div>
          <div className="vi-msg-text">{children}</div>
        </div>
      </div>
    );
  }
  return (
    <div className="vi-msg">
      <div className="vi-msg-avatar"><ViMark size={32} animated={from==='vi-live'} /></div>
      <div className="vi-msg-body">
        <div className="vi-msg-name">V<span className="i">i</span> <span className="meta">{time}</span></div>
        {children}
      </div>
    </div>
  );
}

function ChatPanel({ children, onSend, value, setValue, disabled }) {
  const ref = useRef_c(null);
  useEffect_c(() => { if (ref.current) ref.current.scrollTop = ref.current.scrollHeight; }, [children]);
  return (
    <div className="vi-chat">
      <div className="vi-msgs" ref={ref}>{children}</div>
      <div className="vi-composer">
        <div className="vi-composer-input">
          <input
            placeholder={disabled ? 'Vi is working…' : 'Reply to Vi, or ask for changes'}
            value={value} onChange={e=>setValue(e.target.value)}
            onKeyDown={e=>e.key==='Enter' && !e.shiftKey && (e.preventDefault(), onSend())}
            disabled={disabled}
          />
        </div>
        <div className="vi-composer-actions">
          <span className="vi-composer-hint">Shift + Enter for new line · Vi reads your connected entities</span>
          <button className="btn" onClick={onSend} disabled={disabled}>Send →</button>
        </div>
      </div>
    </div>
  );
}

window.ChatPanel = ChatPanel;
window.Message = Message;
window.ReadCard = ReadCard;
window.MissingPrompt = MissingPrompt;
window.ApproveCard = ApproveCard;
