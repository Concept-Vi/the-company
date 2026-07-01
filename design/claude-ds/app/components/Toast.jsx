// Toast.jsx — simple global notifier (single shared instance)
const { useEffect: useEffect_t, useState: useState_t } = React;

window._toastListeners = window._toastListeners || [];
window.dsaToast = (msg) => window._toastListeners.forEach(fn => fn(msg));

function Toast() {
  const [msg, setMsg] = useState_t(null);
  useEffect_t(() => {
    const sub = (m) => {
      setMsg(m);
      setTimeout(() => setMsg(null), 2200);
    };
    window._toastListeners.push(sub);
    return () => { window._toastListeners = window._toastListeners.filter(f => f !== sub); };
  }, []);
  return (
    <div className={`dsa-toast ${msg ? 'show' : ''}`}>
      <ViShape size={14}/>
      <span>{msg}</span>
    </div>
  );
}
window.Toast = Toast;
