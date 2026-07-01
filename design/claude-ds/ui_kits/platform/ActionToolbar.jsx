// ActionToolbar.jsx — Select / Filter / Sort / Search / Clear / Create / Upload
function I({ d, fill }) {
  return <svg className="ic" viewBox="0 0 14 14">{d.map((p,i) => <path key={i} d={p} fill={fill ? 'currentColor' : 'none'} />)}</svg>;
}

function ToolbarBtn({ icon, label, primary, onClick }) {
  return (
    <button className={`cv-btn ${primary ? 'cv-btn--primary' : 'cv-btn--outline'}`} onClick={onClick}>
      {icon}{label}
    </button>
  );
}

const Icons = {
  select:   <I d={["M2 3 H12 V11 H2 Z","M5 7 L6.5 8.5 L10 5"]} />,
  filter:   <I d={["M2 3 H12 L9 7 V11 L5 12 V7 Z"]} />,
  sort:     <I d={["M4 2 V12 M2 4 L4 2 L6 4","M10 12 V2 M8 10 L10 12 L12 10"]} />,
  clear:    <I d={["M2 2 L12 12 M12 2 L2 12"]} />,
  plus:     <I d={["M7 2 V12 M2 7 H12"]} />,
  upload:   <I d={["M7 9 V2 M4.5 4.5 L7 2 L9.5 4.5","M2 10 V12 H12 V10"]} />,
  search:   <I d={["M9.5 9.5 L12 12"]} />,
};

function ActionToolbar({ showSelect = true, showCreate = true, showUpload = true, search = '', onSearch }) {
  return (
    <div className="cv-toolbar">
      {showSelect && <ToolbarBtn icon={Icons.select} label="Select"/>}
      <ToolbarBtn icon={Icons.filter} label="Filter"/>
      <ToolbarBtn icon={Icons.sort} label="Sort"/>
      <div className="cv-search">
        <svg className="ic" viewBox="0 0 14 14" style={{stroke:'var(--fg-muted)'}}><circle cx="6" cy="6" r="4" fill="none" stroke="currentColor"/><path d="M9.5 9.5 L12 12" stroke="currentColor"/></svg>
        <input value={search} onChange={e => onSearch?.(e.target.value)} placeholder="Search"/>
      </div>
      <ToolbarBtn icon={Icons.clear} label="Clear Filters"/>
      <div className="right">
        {showCreate && <ToolbarBtn icon={Icons.plus} label="Create New"/>}
        {showUpload && <ToolbarBtn icon={Icons.upload} label="Upload"/>}
      </div>
    </div>
  );
}

window.ActionToolbar = ActionToolbar;
