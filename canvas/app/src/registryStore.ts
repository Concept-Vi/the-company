// F0 · the shape-reachable registry store.
//
// WHY THIS EXISTS (fe-map §0; App.tsx:100–102 pre-carve): the node SHAPE is rendered INSIDE tldraw
// (NodeShapeUtil.component) and cannot reach Hud-local React state — so the read-truth the shape needs
// to draw (ports/schema from OINFO, the connect hook, the live drag gesture, the force-rerun hook, the
// model options, the ui_info registry) lived at MODULE SCOPE as 6 mutable globals. F0 replaces those 6
// raw globals with ONE external store, read via React 18's built-in `useSyncExternalStore` — which IS
// reachable from the shape (a component below <Tldraw> that can't consume a Hud-level React context).
//
// reflects-never-owns (canvas/AGENTS.md): every field here is READ TRUTH from the backend (OINFO,
// MODEL_OPTIONS, UI_INFO) or a hook the controller installs (CONNECT, FORCE_RUN) or transient gesture
// state (DRAG_CONN). The store mirrors the backend; the backend is authoritative — the store NEVER
// becomes a second source of truth for graph state (that stays editor + the backend).
//
// Dependency-free on purpose: no zustand/redux (the worktree runs on a SYMLINKED node_modules pinned to
// the live commit — adding a dep would break that guarantee). The globals were already a hand-rolled
// external store; this just gives them a subscribe/snapshot so React can read them reactively.

// F3: one served node-state, as it rides in capabilities().node_states (suite.py NODE_STATES + S5's render).
// `render.token` is a corpus design-token NAME (e.g. '--fail') — the by-sight colour signal, the ONE source
// for status colour. `render.shape` ('dot'|'ring') distinguishes compute vs reference nodes (border-radius).
// `render.icon` is provisional (S5: no corpus icon registry yet) — kept for forward-compat, not depended on.
export type NodeStateRender = { token: string; icon?: string; shape?: string }
export type NodeStateDef = {
  id: string; label: string; means?: string; applies_to?: string[]; derived_when?: string
  render?: NodeStateRender
}

export type RegistryState = {
  // type -> { ports:{inputs,outputs}, config_schema, kind } — the C1 object_info registry (drives ports + the generic inspector form).
  OINFO: Record<string, any>
  // 'chat_models' | 'embed_models' -> live model id list (the B2 model registry; never a hardcoded list).
  MODEL_OPTIONS: Record<string, string[]>
  // the UI-component registry (/api/ui_info) — the source of what's addressable; the resolver validates ui:// targets against it.
  UI_INFO: Record<string, any>
  // F3: stateId -> NodeStateDef, indexed from capabilities().node_states. The shape + inspector read label +
  // render FROM HERE (registry-is-truth, rule 3): register a state engine-side → it paints everywhere, no FE edit.
  NODE_STATES: Record<string, NodeStateDef>
}

// C1: a drag from an output nub to an input nub COMMITS through this hook (the controller installs it). The
// shape only detects the gesture + endpoints; the CONNECTION round-trips /api/connect (backend type-checks,
// backend owns the edge) — the canvas reflects it, never owns it. Kept as a plain module ref (a function
// handle, not render state) — the shape calls it imperatively on pointer-up.
export let CONNECT: (from_node: string, from_port: string, to_node: string, to_port: string) => void = () => {}
export function setConnect(fn: typeof CONNECT) { CONNECT = fn }

// the live drag-to-connect gesture, module-scope so the source-nub pointerdown and any target-nub
// pointerup share it across shape instances (transient gesture state — never a backend truth).
export let DRAG_CONN: { from_node: string; from_port: string } | null = null
export function setDragConn(v: typeof DRAG_CONN) { DRAG_CONN = v }

// D4: a per-node force-rerun affordance on the card bypasses the memo gate for just that node (the
// controller installs it).
export let FORCE_RUN: (node_id: string) => void = () => {}
export function setForceRun(fn: typeof FORCE_RUN) { FORCE_RUN = fn }

let state: RegistryState = { OINFO: {}, MODEL_OPTIONS: {}, UI_INFO: {}, NODE_STATES: {} }
const listeners = new Set<() => void>()

function emit() { for (const l of listeners) l() }

export const registryStore = {
  subscribe(cb: () => void) { listeners.add(cb); return () => { listeners.delete(cb) } },
  getSnapshot(): RegistryState { return state },
  // partial update — replaces the changed fields, keeps the snapshot identity stable when nothing changed.
  set(patch: Partial<RegistryState>) {
    state = { ...state, ...patch }
    emit()
  },
}

// Imperative reads for non-React call sites (loadGraph/Edges run outside the render cycle and read the
// registry directly — exactly as they read the raw globals before the carve). These return the LIVE
// snapshot fields, so they stay in sync with the store.
export function getOINFO(): Record<string, any> { return state.OINFO }
export function getMODEL_OPTIONS(): Record<string, string[]> { return state.MODEL_OPTIONS }
export function getUI_INFO(): Record<string, any> { return state.UI_INFO }
// F3: imperative read for the node shape (renders inside tldraw, outside React context). Returns the live
// node_states index — the shape reads label + render.token/shape from it to paint status by sight.
export function getNODE_STATES(): Record<string, NodeStateDef> { return state.NODE_STATES }
