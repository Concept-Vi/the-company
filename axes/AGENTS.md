# axes/ — the coordinate-AXIS registry (the resolver's axes-are-registries)

The file-discovered vocabulary of the resolver's COORDINATE dimensions (resolve(invariant, coordinate) → surface).
Each `<id>.py` declares a module-level `AXIS` dict — one orthogonal dimension. ★ ADD AN AXIS = DROP A FILE
(zero engine code; the coordinate-space self-extends — Tim's "axes ARE registries"/recursive registry-is-truth).

- **Mechanism:** `runtime/axis_registry.py` (mirrors stack_item_types/item_types/mark_types — the ONE file-discovered
  registry mechanism, own row shape).
- **Row shape:** `id` (==filename) · `namespace` (the coordinate key) · `fields`? {sub_field: continuous|discrete}
  (the resolve mechanism per sub-field — continuous=DERIVE via a relationship-AST · discrete=registry-SELECT) ·
  `value_source`? ('live' · a ref · 'pending') · `desc`?.
- **The resolver is list-AGNOSTIC** (runtime/resolver.py resolves against whatever coordinate it's handed) — this
  registry is the coordinate's VOCABULARY, not a switch the resolver branches on.
- **★ THE AXIS SET HERE IS THE SURFACE PROJECTION** (device/viewer/mode/type/resolution/state/register, seeded).
  The FORMAL ROOT axes (the four-root lock · the 3/1 · time-as-meta · state/scale/frame-one-family) are Tim+fork's
  vault work, Tim-adjudicated. These rows are DATA (swappable); the mechanism survives any root-set. DON'T assert
  this list as final. perspective · intent · posture are a-row-away (seed when they get real resolve-usage).
- **Consumers (co-scope):** the resolver + projection's coordinate-computation + the host read `as_records()` for
  the available axes. The floor: reading an axis is a READ.
