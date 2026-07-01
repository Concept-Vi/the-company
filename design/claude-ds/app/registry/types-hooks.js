// app/registry/types-hooks.js
// React hooks for the universal Type Registry. Reactive — re-renders when
// any Type is registered/updated/removed.

(function () {
  const { useState, useEffect, useMemo, useCallback } = React;
  const R = window.CV_REGISTRY;
  if (!R) { console.error('[hooks] CV_REGISTRY missing'); return; }

  // useTypes(filter) — re-runs query on every registry change
  function useTypes(filter) {
    const [tick, setTick] = useState(0);
    useEffect(() => R.subscribe(() => setTick(t => t + 1)), []);
    return useMemo(() => R.query(filter), [tick, JSON.stringify(filter || null)]);
  }

  // useType(id) — single Type by id
  function useType(id) {
    const [tick, setTick] = useState(0);
    useEffect(() => R.subscribe(() => setTick(t => t + 1)), []);
    return useMemo(() => R.get(id), [tick, id]);
  }

  // useResolvedType(id) — Type flattened with its ancestry
  function useResolvedType(id) {
    const [tick, setTick] = useState(0);
    useEffect(() => R.subscribe(() => setTick(t => t + 1)), []);
    return useMemo(() => R.resolve(id), [tick, id]);
  }

  // useLineage(id) — array of types from self → root
  function useLineage(id) {
    const [tick, setTick] = useState(0);
    useEffect(() => R.subscribe(() => setTick(t => t + 1)), []);
    return useMemo(() => R.lineage(id), [tick, id]);
  }

  // useChildren(id) — Types directly extending this one
  function useChildren(id) {
    const [tick, setTick] = useState(0);
    useEffect(() => R.subscribe(() => setTick(t => t + 1)), []);
    return useMemo(() => R.children(id), [tick, id]);
  }

  // Convenience: register/update wrappers that always notify
  function useRegistryActions() {
    return useMemo(() => ({
      register:   (t) => R.register(t),
      update:     (id, patch) => R.update(id, patch),
      remove:     (id) => R.remove(id),
      candidates: (slot) => R.candidatesForSlot(slot),
      accepts:    (slot, type) => R.accepts(slot, type),
    }), []);
  }

  window.useTypes = useTypes;
  window.useType = useType;
  window.useResolvedType = useResolvedType;
  window.useLineage = useLineage;
  window.useChildren = useChildren;
  window.useRegistryActions = useRegistryActions;
})();
