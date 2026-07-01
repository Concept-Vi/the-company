// Chats.jsx — floating bottom-right pill
function Chats({ count = 21 }) {
  return (
    <div className="cv-chats" role="button">
      <svg viewBox="0 0 24 24"><path d="M3 6 a3 3 0 0 1 3-3 h9 a3 3 0 0 1 3 3 v6 a3 3 0 0 1 -3 3 H9 L5 19 V15 H6 a3 3 0 0 1 -3 -3 Z"/><path d="M9 18 a3 3 0 0 0 3 3 h6 l3 3 v-3 a3 3 0 0 0 3 -3 v-3" transform="translate(-2 -3)"/></svg>
      <span>Chats</span>
      <span className="count">{count}</span>
    </div>
  );
}
window.Chats = Chats;
