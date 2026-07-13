// THE DS DOOR (K0 §3) — this app consumes the design system ONLY through the two
// sanctioned mechanisms:
//
//   1. `_ds_bundle.js` (the U3 external-consumer mechanism): loaded as a classic script
//      AFTER window.React/ReactDOM are set (the bundle consumes React as a runtime
//      global — design/claude-ds/package.json's peer note). It mounts
//      window.ConceptVDesignSystem_c8f43c + the registries (CV_REGISTRY, CV_ICONS,
//      CV_AXES, CV_AI, CV_POPOVER, …) — the bundle IS the compiled load order
//      (token CSS chain aside, which index.html links as /ds/styles.css).
//   2. `design/claude-ds/index.js` (the U4 sanctioned import surface): getDS() /
//      getRegistry(), both LOUD-FAIL. Imported at runtime from /ds/index.js so the
//      one home serves it — never a copied file.
//
// Everything here fails LOUD (claude-ds CLAUDE.md §3): a missing bundle, a failed
// door import, or an unmounted registry throws — the app never renders unstyled or
// silently component-less.
import React from 'react'
import ReactDOM from 'react-dom/client'

type DSNamespace = Record<string, unknown> & {
  // the bundle components this app uses (typed loosely — the bundle is untyped JS;
  // the .d.ts files live beside the component sources in the DS home)
  Card: React.ComponentType<Record<string, unknown>>
  Badge: React.ComponentType<Record<string, unknown>>
  Segmented: React.ComponentType<Record<string, unknown>>
  Button: React.ComponentType<Record<string, unknown>>
  // U6 chrome (landed 2026-07-13, now compiled into _ds_bundle.js — the bundle-recompile
  // that closed the former "bundle-stale chrome" tension; see AGENTS.md's contract-tensions
  // note for the history). Consumed through ds() like every other component — never a
  // source import of design/claude-ds/components/*.jsx from this app.
  AppShell: React.ComponentType<Record<string, unknown>>
  List: React.ComponentType<Record<string, unknown>>
  ListRow: React.ComponentType<Record<string, unknown>>
  ToastHost: React.ComponentType<Record<string, unknown>>
}
type DSDoor = {
  getDS: () => DSNamespace
  getRegistry: (id: string) => Record<string, unknown>
  listRegistries: () => Array<{ id: string; loaded: boolean }>
}

let _door: DSDoor | null = null

function loadScript(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    const s = document.createElement('script')
    s.src = src
    s.onload = () => resolve()
    s.onerror = () => reject(new Error(`[operator-app] failed to load ${src} — is the bridge serving /ds/* (runtime/bridge.py)?`))
    document.head.appendChild(s)
  })
}

/** Boot the DS: set the React globals the bundle expects, load the bundle, import the door.
 *  MUST complete before the first render (App components call ds() synchronously). */
export async function bootDS(): Promise<void> {
  // The bundle consumes React as a window global (window.React / window.ReactDOM) — provide
  // OUR pinned 18.3.1 so there is exactly one React instance in the page.
  ;(window as unknown as Record<string, unknown>).React = React
  ;(window as unknown as Record<string, unknown>).ReactDOM = ReactDOM
  await loadScript('/ds/_ds_bundle.js')
  // The sanctioned door, imported from the one DS home at runtime (never bundled/copied).
  // The specifier is a variable so neither vite (build-time) nor tsc (a rooted path never
  // matches an ambient module declaration) tries to resolve it statically.
  const doorUrl = '/ds/index.js'
  _door = (await import(/* @vite-ignore */ doorUrl)) as DSDoor
  // Loud-fail probe: getDS() throws if the bundle namespace didn't mount.
  _door.getDS()
}

/** The bundle namespace (Card, Badge, Segmented, RenderType, …). Throws if bootDS() hasn't run. */
export function ds(): DSNamespace {
  if (!_door) throw new Error('[operator-app] ds() before bootDS() — the DS door is not open yet.')
  return _door.getDS()
}

/** A named registry global (CV_ICONS, CV_AXES, …). Throws on unknown/unmounted (the door's law). */
export function registry(id: string): Record<string, unknown> {
  if (!_door) throw new Error('[operator-app] registry() before bootDS() — the DS door is not open yet.')
  return _door.getRegistry(id)
}
