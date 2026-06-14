// THE SINGLE MOTION SYSTEM (MANDATE L3 · RESEARCH-SYNTHESIS §F)
// One module imported everywhere — so motion feels authored, not per-component improvised.
// No-teleport law: every appear/disappear/move/resize tweens; animate transform+opacity only.
import type { Transition } from 'framer-motion'

// Spring presets (iOS-inspired). The S4.3 taste toggle swaps spring <-> eased on the same transitions.
export const SPRING_GENTLE: Transition = { type: 'spring', stiffness: 100, damping: 20, mass: 1 }
export const SPRING_SNAPPY: Transition = { type: 'spring', stiffness: 170, damping: 15, mass: 1 }

// Material-validated eased-out cubic (the crisp alternative).
export const EASE_OUT: [number, number, number, number] = [0.4, 0, 0.2, 1]

// Durations (design tokens, seconds for Motion).
export const DUR = { enter: 0.36, move: 0.42, exit: 0.28, colour: 0.15 } as const

export type MotionFeel = 'spring' | 'eased'

// Resolve the transition for a given role, honouring the taste toggle + reduced-motion.
export function transition(
  role: 'enter' | 'move' | 'exit' | 'colour',
  feel: MotionFeel = 'spring',
): Transition {
  if (typeof window !== 'undefined' &&
      window.matchMedia?.('(prefers-reduced-motion: reduce)').matches) {
    return { duration: 0.001 }
  }
  if (feel === 'spring' && (role === 'enter' || role === 'move')) {
    return role === 'enter' ? SPRING_GENTLE : SPRING_SNAPPY
  }
  return { duration: DUR[role], ease: EASE_OUT }
}

// Shared variants for the disclosure grammar (peek -> open -> dismiss); entrance/exit are mirrors.
export const fadeRise = {
  hidden: { opacity: 0, y: 8 },
  shown: { opacity: 1, y: 0 },
}
