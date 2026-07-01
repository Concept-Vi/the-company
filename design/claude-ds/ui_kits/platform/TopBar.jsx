// TopBar.jsx — bell + avatar pinned top-right of content column
function TopBar({ notifications = 7 }) {
  return (
    <div className="cv-topbar">
      <span className="cv-bell" role="button" aria-label="Notifications">
        <svg viewBox="0 0 24 24"><path d="M6 17 V11 a6 6 0 0 1 12 0 v6 l1.5 2 H4.5 Z"/><path d="M9.5 19.5 a2.5 2.5 0 0 0 5 0"/></svg>
        {notifications > 0 && <span className="cv-bell-badge">{notifications}</span>}
      </span>
      <span className="cv-avatar">
        <svg viewBox="0 0 24 24"><path d="M12 12 a4 4 0 1 0 0-8 a4 4 0 0 0 0 8 Z M4 22 a8 8 0 0 1 16 0 Z"/></svg>
      </span>
    </div>
  );
}
window.TopBar = TopBar;
