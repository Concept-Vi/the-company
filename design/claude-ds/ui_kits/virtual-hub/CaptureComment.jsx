// CaptureComment.jsx — the comment-capture popup from the source mockup
const { useState: useState_cc } = React;

function CaptureComment({ x, y, onClose }) {
  const [status, setStatus] = useState_cc('pending');
  const STATUSES = {
    pending: { color: '#E5C547', label: 'Pending' },
    approved: { color: '#5A8A4A', label: 'Approved' },
    resolved: { color: '#4A78B8', label: 'Resolved' },
    rejected: { color: '#C24A3C', label: 'Rejected' },
  };
  const cur = STATUSES[status];
  // Position the popup near the click, clamped inside viewport
  const left = Math.min(Math.max(x - 160, 16), window.innerWidth - 336);
  const top  = Math.min(Math.max(y - 20, 16), window.innerHeight - 540);
  return (
    <>
      <div className="vh-tap-marker" style={{left: x, top: y}}/>
      <div className="vh-capture" style={{left, top}}>
        <div className="vh-capture-head">
          <button className="vh-capture-close" onClick={onClose}>✕</button>
          <span className="vh-capture-meta">Created by Sam Lin on 19/05/26</span>
          <span style={{width:22}}/>
        </div>
        <div className="vh-capture-image">
          <div className="expand">⤢</div>
        </div>

        <div className="vh-comments-head">
          <span>Comments</span>
          <button className="more">⌃</button>
        </div>
        <div className="vh-comments-list">
          <div className="vh-comment-row">
            <div className="avatar" style={{background:'#E8D7C2'}}/>
            <div className="bar" style={{background:'var(--accent-gold-50)'}}/>
          </div>
          <div className="vh-comment-row">
            <div className="avatar" style={{background:'#D8D5CB'}}/>
            <div className="bar"/>
          </div>
        </div>

        <div className="vh-attachments">
          <div className="vh-attachment">
            <svg width="22" height="22" viewBox="0 0 22 22" fill="none" stroke="currentColor" strokeWidth="1.5"><rect x="3" y="4" width="16" height="14" rx="1"/><circle cx="8" cy="9" r="1.5"/><path d="M3 15 L8 11 L13 15 L17 13 L19 15"/></svg>
          </div>
          <div className="vh-attachment pdf">
            <svg width="22" height="22" viewBox="0 0 22 22" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M5 2 H13 L17 6 V20 H5 Z"/><path d="M13 2 V6 H17"/><text x="6.5" y="15" font-size="5" font-weight="700" fill="currentColor" stroke="none">PDF</text></svg>
          </div>
        </div>

        <div className="vh-msg-input">
          <input placeholder="Message"/>
          <div className="vh-msg-toolbar">
            <button>B</button>
            <button><i>I</i></button>
            <button style={{textDecoration:'line-through'}}>S</button>
            <button>&lt;/&gt;</button>
            <button>≡</button>
            <button>Aa</button>
            <button>@</button>
            <button>☺</button>
            <button>📎</button>
            <span style={{flex:1}}/>
            <button>···</button>
          </div>
        </div>

        <div>
          <div className="vh-status">
            <span className="vh-status-label">Status</span>
            <button className="vh-status-pill" onClick={() => {
              const keys = Object.keys(STATUSES);
              const i = keys.indexOf(status);
              setStatus(keys[(i+1) % keys.length]);
            }}>
              <span className="dot" style={{background: cur.color}}/>
              {cur.label}
              <span style={{marginLeft:6,color:'var(--fg-muted)'}}>▾</span>
            </button>
          </div>
        </div>

        <div className="vh-capture-pager">
          <button className="arrow">‹</button>
          <span className="label">More Captures</span>
          <button className="arrow">›</button>
        </div>
      </div>
    </>
  );
}
window.CaptureComment = CaptureComment;
