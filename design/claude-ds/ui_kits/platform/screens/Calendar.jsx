// screens/Calendar.jsx
function TopTask({ color, name }) {
  return (
    <div className="cv-cal-task">
      <div className={`name ${color}`}>{name}</div>
      <div className="due">Due Date: 00/00/00</div>
      <div className="desc">Lorem ipsum dolor sit amet, consectetur adipiscing elit</div>
    </div>
  );
}

function CalChip({ kind, label }) {
  return <span className={`cv-cal-chip ${kind}`}><span className="dot"></span>{label}</span>;
}

function Day({ n, muted, today, children }) {
  return (
    <div>
      <span className={`cv-cal-day ${muted ? 'muted' : ''} ${today ? 'today' : ''}`}>{n}</span>
      {children}
    </div>
  );
}

function CalendarScreen() {
  return (
    <>
      <h1 className="cv-screen-title">Calendar</h1>
      <div className="cv-toolbar">
        <button className="cv-btn cv-btn--outline">Filter</button>
        <button className="cv-btn cv-btn--outline">Sort</button>
        <div className="cv-search">
          <svg className="ic" viewBox="0 0 14 14"><circle cx="6" cy="6" r="4" fill="none" stroke="var(--fg-muted)" strokeWidth="1.5"/><path d="M9.5 9.5 L12 12" stroke="var(--fg-muted)" strokeWidth="1.5"/></svg>
          <input placeholder="Search"/>
        </div>
        <button className="cv-btn cv-btn--outline">Clear Filters</button>
        <div className="right">
          <button className="cv-btn cv-btn--outline" style={{minWidth:160,justifyContent:'space-between'}}>
            <span>📊 Task Type</span><span>▾</span>
          </button>
        </div>
      </div>

      <div className="cv-cal-tasks">
        <div className="cv-cal-tasks-title">
          <span>Top Tasks &amp; Reminders</span>
          <span style={{font:'500 12px/1 var(--font-body)',color:'var(--fg-muted)',cursor:'pointer'}}>Manage</span>
        </div>
        <div className="cv-cal-tasks-row">
          <TopTask color="" name="Task Name"/>
          <TopTask color="purple" name="Task Name"/>
          <TopTask color="" name="Task Name"/>
          <TopTask color="green" name="Task Name"/>
          <TopTask color="green" name="Task Name"/>
          <TopTask color="blue" name="Task Name"/>
          <TopTask color="orange" name="Task Name"/>
          <TopTask color="" name="Task Name"/>
        </div>
      </div>

      <div className="cv-cal-monthnav">
        <button>‹</button>
        <span className="m">June 2026</span>
        <button>›</button>
      </div>

      <div className="cv-cal-grid">
        <div className="cv-cal-headers">
          {['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'].map(d => <div key={d}>{d}</div>)}
        </div>
        <div className="cv-cal-week">
          <Day n={27} muted/><Day n={28} muted/><Day n={29} muted/><Day n={30} muted/><Day n={31} muted/><Day n={1}/><Day n={2}/>
        </div>
        <div className="cv-cal-week">
          <Day n={3}/>
          <Day n={4}><CalChip kind="yellow" label="Task Name"/><CalChip kind="orange" label="Task Name"/></Day>
          <Day n={5}><CalChip kind="purple" label="Task Name"/><CalChip kind="gray" label="Task Name"/></Day>
          <Day n={6}><CalChip kind="green" label="Task Name"/><CalChip kind="yellow" label="Task Name"/></Day>
          <Day n={7}><CalChip kind="blue" label="Task Name"/><CalChip kind="orange" label="Task Name"/><CalChip kind="gray" label="Task Name"/></Day>
          <Day n={8}/><Day n={9}/>
        </div>
        <div className="cv-cal-week">
          <Day n={10}><CalChip kind="green" label="Task Name"/></Day>
          <Day n={11}><CalChip kind="orange" label="Task Name"/></Day>
          <Day n={12}><CalChip kind="yellow" label="Task Name"/><CalChip kind="gray" label="Task Name"/><CalChip kind="orange" label="Task Name"/></Day>
          <Day n={13}><CalChip kind="red" label="Task Name"/></Day>
          <Day n={14}><CalChip kind="gray" label="Task Name"/></Day>
          <Day n={15} today><CalChip kind="gray" label="Task Name"/></Day>
          <Day n={16}/>
        </div>
      </div>
    </>
  );
}

window.CalendarScreen = CalendarScreen;
