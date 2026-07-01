// usePersisted.js — small localStorage state hook
// Survives refresh; namespaced so we can clear/export everything at once.

(function() {
  const NS = 'cvstudio:';
  const all = () => Object.keys(localStorage).filter(k => k.startsWith(NS));

  window.usePersisted = function(key, initial) {
    const fullKey = NS + key;
    const [val, setVal] = React.useState(() => {
      try {
        const raw = localStorage.getItem(fullKey);
        if (raw == null) return typeof initial === 'function' ? initial() : initial;
        return JSON.parse(raw);
      } catch {
        return typeof initial === 'function' ? initial() : initial;
      }
    });
    React.useEffect(() => {
      try { localStorage.setItem(fullKey, JSON.stringify(val)); } catch {}
    }, [fullKey, val]);
    return [val, setVal];
  };

  window.cvStudioStorage = {
    getAll() {
      const out = {};
      for (const k of all()) {
        const short = k.slice(NS.length);
        try { out[short] = JSON.parse(localStorage.getItem(k)); } catch { out[short] = null; }
      }
      return out;
    },
    clear() {
      for (const k of all()) localStorage.removeItem(k);
    },
  };
})();
