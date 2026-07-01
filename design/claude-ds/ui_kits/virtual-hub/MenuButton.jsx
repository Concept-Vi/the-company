// MenuButton.jsx — the bottom-centre dark MENU pill
function MenuButton({ open, onClick }) {
  return (
    <button className={`vh-menu-btn ${open ? 'open' : ''}`} onClick={onClick}>
      <span className="chev">⌃</span>
      <span>MENU</span>
    </button>
  );
}
window.MenuButton = MenuButton;
