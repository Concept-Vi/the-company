// F0 · the app context — exposes the single controller (the carved Hud state + handlers) to the region
// components without prop-drilling. Created inside Hud (which has useEditor); consumed by the toolbar,
// palette, inspector, inbox, grow, op-panels, activity, rhm-chat, walkthrough, workshop region components.
import { createContext, useContext } from 'react'
import type { AppController } from './useAppController'

export const AppContext = createContext<AppController | null>(null)

export function useApp(): AppController {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error('useApp must be used within AppContext.Provider (the Hud shell)')
  return ctx
}
