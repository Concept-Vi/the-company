// Sidebar.jsx — left nav of asset classes
const { useEffect: useEffect_sb } = React;

const NAV_SECTIONS = [
  {
    title: 'Workspace',
    items: [
      { id: 'overview', label: 'Overview',  icon: 'dashboard' },
      { id: '__search', label: 'Search everything', icon: 'search', shortcut: '⌘K', isAction: true },
      { id: 'workshop', label: 'Workshop',  icon: 'browser' },
      { id: 'build',    label: 'Build',     icon: 'atom' },
      { id: 'inbox',    label: 'Inbox',     icon: 'files-stack', countKey: 'inboxCount', newKey: 'inboxNew' },
    ],
  },
  {
    title: 'System',
    items: [
      { id: 'registry',     label: 'Type Registry',  icon: 'network',  countKey: 'typeCountTotal' },
      { id: 'architecture', label: 'Architecture',   icon: 'hierarchy' },
    ],
  },
  {
    title: 'Foundations',
    items: [
      { id: 'colors',   label: 'Colors',    icon: 'color-swatches', countKey: 'colorCount' },
      { id: 'type',     label: 'Type',      icon: 'document', countKey: 'typeCount' },
      { id: 'icons',    label: 'Icons',     icon: 'star',  countKey: 'iconCount' },
      { id: 'logos',    label: 'Logos & marks', icon: 'tag', countKey: 'logoCount' },
      { id: 'imagery',  label: 'Imagery',   icon: 'image-stack', countKey: 'imageryCount' },
      { id: 'patterns', label: 'Motion & space', icon: 'adjustments', countKey: 'patternCount' },
    ],
  },
  {
    title: 'Build with',
    items: [
      { id: 'components', label: 'Components', icon: 'check-square', countKey: 'componentCount' },
      { id: 'templates',  label: 'Templates',  icon: 'browser', countKey: 'templateCount' },
      { id: 'voice',      label: 'Voice & tone', icon: 'chat-double', countKey: 'voiceCount' },
    ],
  },
  {
    title: 'AI & settings',
    items: [
      { id: 'bridge',   label: 'Bridge',   icon: 'cloud-upload' },
      { id: 'settings', label: 'Settings', icon: 'gear', newKey: 'needsAI' },
    ],
  },
];

function Sidebar({ active, onSelect, counts, onOpenSearch, onCollapse }) {
  return (
    <aside className="dsa-side">
      <div className="dsa-brand">
        <img src="../assets/logos/conceptv-wordmark-black.png" alt="ConceptV"/>
        <button
          type="button"
          className="dsa-drawer-close"
          onClick={() => onCollapse?.()}
          title="Hide sidebar"
          aria-label="Hide sidebar">
          <CvIcon name="sidebar-close" size={16} tone="bronze"/>
        </button>
      </div>

      {NAV_SECTIONS.map(sec => (
        <div key={sec.title}>
          <h4>{sec.title}</h4>
          <div className="dsa-nav">
            {sec.items.map(item => (
              <button
                key={item.id}
                className={`dsa-nav-item ${active === item.id ? 'active' : ''}`}
                onClick={() => item.isAction && item.id === '__search' ? onOpenSearch?.() : onSelect(item.id)}>
                <span className="gly">
                  <CvIcon name={item.icon} size={16} tone="bronze"/>
                </span>
                {item.label}
                {item.shortcut && (
                  <span style={{marginLeft:'auto',font:'600 9px/1 var(--font-mono)',color:'var(--fg-muted)',background:'var(--bg-muted)',padding:'3px 5px',borderRadius:3,letterSpacing:'0.06em'}}>{item.shortcut}</span>
                )}
                {item.countKey && counts[item.countKey] != null && (
                  <span className="count">{counts[item.countKey]}</span>
                )}
                {item.newKey && counts[item.newKey] && <span className="new-dot"/>}
              </button>
            ))}
          </div>
        </div>
      ))}

      <div className="spacer"/>

      <div className="dsa-system-status">
        <b>System health</b>
        {counts.healthScore}% coverage · {counts.gaps} gap{counts.gaps === 1 ? '' : 's'} flagged.
      </div>
    </aside>
  );
}
window.Sidebar = Sidebar;
