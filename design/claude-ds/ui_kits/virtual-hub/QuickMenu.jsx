// QuickMenu.jsx — the dark menu column that pops up
function QmIcon({ d, fill }) {
  return <svg className="ic" viewBox="0 0 16 16">{d.map((p,i) => <path key={i} d={p} fill={fill?'currentColor':'none'}/>)}</svg>;
}
const QM_ICONS = {
  info:      <QmIcon d={["M8 3 v8 M8 13 v.01","M8 1 a7 7 0 1 1 0 14 a7 7 0 0 1 0 -14 Z"]} />,
  floorplan: <QmIcon d={["M2 3 H14 V13 H2 Z","M2 7 H14 M9 7 V13 M6 13 V10"]} />,
  share:     <QmIcon d={["M5 7 L11 4 M5 9 L11 12","M4 8 a1.5 1.5 0 1 1 0 .01 Z M12 4 a1.5 1.5 0 1 1 0 .01 Z M12 12 a1.5 1.5 0 1 1 0 .01 Z"]} />,
  gyro:      <QmIcon d={["M8 2 a6 6 0 1 1 0 12 a6 6 0 0 1 0 -12 Z","M8 5 a3 3 0 1 1 0 6 a3 3 0 0 1 0 -6 Z"]} />,
  close:     <QmIcon d={["M3 3 L13 13 M13 3 L3 13"]} />,
};

function QuickMenu({ active, onSelect, onClose }) {
  return (
    <div className="vh-quickmenu">
      <button className={active==='info' ? 'active' : ''} onClick={()=>onSelect('info')}>{QM_ICONS.info}Info</button>
      <button className={active==='floorplan' ? 'active' : ''} onClick={()=>onSelect('floorplan')}>{QM_ICONS.floorplan}Floorplan</button>
      <button className={active==='share' ? 'active' : ''} onClick={()=>onSelect('share')}>{QM_ICONS.share}Share</button>
      <button className="muted">{QM_ICONS.gyro}Gyro Not Found</button>
      <div className="divider"/>
      <button className="close" onClick={onClose}>{QM_ICONS.close}CLOSE</button>
    </div>
  );
}
window.QuickMenu = QuickMenu;
