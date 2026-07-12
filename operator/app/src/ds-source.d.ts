// Type shims for the DS pieces TypeScript cannot resolve on its own:
//
// 1. '/ds/index.js' — the sanctioned door, imported at RUNTIME from the bridge-served
//    DS home (never bundled). A bare URL import has no compile-time module — declare it.
declare module '/ds/index.js' {
  export function getDS(): Record<string, unknown>
  export function getRegistry(id: string): Record<string, unknown>
  export function listRegistries(): Array<{ id: string; loaded: boolean }>
  export const BUNDLE_GLOBAL: string
  export const REGISTRY_GLOBALS: string[]
}
