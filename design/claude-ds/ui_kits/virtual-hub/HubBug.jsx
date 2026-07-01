// HubBug.jsx — top-left brand + hub switcher
function HubBug({ hubs, activeHub, onSwitch }) {
  return (
    <div className="vh-bug">
      <div className="vh-bug-logo">
        <img src="../../assets/logos/conceptv-v-yellow.png" alt="ConceptV"/>
      </div>
      <div className="vh-hubsw">
        <span>STAGE</span>
        <div className="tabs">
          {hubs.map(h => (
            <button
              key={h.id}
              className={`tab ${h.id === activeHub ? 'active' : ''}`}
              onClick={() => onSwitch(h.id)}>{h.label}</button>
          ))}
        </div>
      </div>
    </div>
  );
}
window.HubBug = HubBug;
