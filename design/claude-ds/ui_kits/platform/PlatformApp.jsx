// App.jsx — root app with screen routing
const { useState: useState_app } = React;

const STUB_NOTES = {
  projects:   'Project list — grid of project cards each linking through to their Virtual Hubs and Landing Pages.',
  dashboard:  'Dashboard Updates — feed of recent comments, captures, and approvals across all projects.',
  landing:    'Landing Pages — list of landing pages, each opening the Landing Page editor (see Page Layout panel pattern).',
  files:      'Files — generic file browser with folders, sort, filter, and upload.',
  templates:  'Templates — gallery of pre-built page templates the user can clone.',
  pricing:    'Pricing & Ordering — billing screen with plan tiers and per-hub usage breakdown.',
};

function PlatformApp() {
  const [active, setActive] = useState_app('gallery');

  let screen;
  if (active === 'gallery')       screen = <Gallery/>;
  else if (active === 'calendar') screen = <CalendarScreen/>;
  else if (active === 'brandkit') screen = <BrandKit/>;
  else if (active === 'hubsettings') screen = <HubSettings/>;
  else screen = <Stub title={titleFor(active)} note={STUB_NOTES[active]}/>;

  return (
    <div className="cv-shell">
      <PlatformSidebar active={active} onSelect={setActive}/>
      <main className="cv-main">
        <TopBar notifications={7}/>
        {screen}
        <Chats count={21}/>
      </main>
    </div>
  );
}

function titleFor(id) {
  return {
    projects: 'Projects', dashboard: 'Dashboard Updates', landing: 'Landing Pages',
    files: 'Files', templates: 'Templates', pricing: 'Pricing & Ordering',
  }[id] || id;
}

window.PlatformApp = PlatformApp;
const _mountApp = document.getElementById('app');
if (_mountApp) ReactDOM.createRoot(_mountApp).render(<PlatformApp/>);
