// ⚠️ STATUS (2026-06-22, lead g-1782084952): LOAD-BEARING for the L5 update-accept (scoped-#1b-transparent). Tim
// greenlit "the assistant can update what's on screen" (propose-then-accept); the accept route
// (POST /api/decision/update/accept) VALIDATES this token server-side (401 without) — so this interceptor, which
// attaches X-Operator-Session to every consequential same-origin /api request, IS what makes the operator's accept
// authorize. It's transparent (Tim never sees an auth step) → light-UX + runaway-safety at once (a background agent's
// auto-accept is what the token blocks). SCOPE: load-bearing for the update-accept ONLY; full decide-gating
// (A: OPERATOR_TOKEN_ENFORCE) stays HELD/free per Tim's posting-ungate — decision_take still runs token-free. (Was
// "dormant" 71246d1 when A was the only consumer + held; the L5-accept consumer flipped it load-bearing.)
//
// THE OPERATOR-SESSION TOKEN — projection's frontend half of the #1b secure foundation (lead g-1782051943).
// The secure shape under the supervised-post (Tim's "posting shouldn't be gated" — ungated, the secure way) + the
// L5 accept-floor + real decision_take gating: the surface AUTO-MINTS a per-session operator token on load and
// ATTACHES it to its /api requests as the `X-Operator-Session` header. fork's server-side floor VALIDATES it on
// CONSEQUENTIAL ops (decision_take / supervised-post / accept) and runs READS free. (bridge.py: the header slot is
// accepted+threaded at :3157; enforcement is "a one-line flip when GET /api/operator-session mints" :3173.)
//
// ★ SECURITY (the binding design, lead-locked): the surface NEVER asserts "I am supervised / I am Tim". It only
// carries the token fork MINTED for it. The supervised-vs-autonomous privilege is decided SERVER-SIDE from session
// context fork owns (session_supervisor: live-operator-origin vs spawned/background) — NEVER from anything this
// client sends. A client-asserted `supervised:true` would be spoofable (a background agent sends the same flag →
// posts freely → collapses the gate); this token, minted by the server for THIS surface load, is not. We hold the
// token; we never claim the privilege.
//
// ★ INVISIBLE TO TIM (minimize-gating-on-Tim HOLDS): the mint + attach are transparent — Tim never sees an auth
// step. The token gates SPOOFERS / background agents, never Tim's live use. His decide on the 15/15 cards keeps
// working (the surface carries the token; fork validates it).
//
// ★ SAFE TO LAND BEFORE ENFORCEMENT (the sequencing guard, step 2 of the lead's order): while GET
// /api/operator-session 404s (fork's mint endpoint pending) → no token is held → the interceptor adds nothing →
// ZERO behavior change. The instant fork ships the mint endpoint, the surface mints + attaches automatically; THEN
// fork flips enforcement (step 3) against a surface that already carries the token — so Tim's live decide never
// 401s. This file IS the prerequisite that makes the enforcement-flip non-breaking.

let token: string | null = null
let installed = false

// is this a same-origin /api request the token should ride? (relative `/api/…`, or absolute to our own origin).
// NEVER attach to cross-origin — defensive: the operator token must not leak off this surface.
function isOwnApi(url: string): boolean {
  if (url.startsWith('/api/')) return true
  try {
    const u = new URL(url, window.location.href)
    return u.origin === window.location.origin && u.pathname.startsWith('/api/')
  } catch {
    return false
  }
}

// MINT — GET /api/operator-session → the per-session token. Degrade clean: 404 (endpoint pending) / any error →
// token stays null → the interceptor attaches nothing → no break (enforcement is off until the mint is live).
export async function mintOperatorSession(): Promise<void> {
  try {
    const r = await fetch('/api/operator-session', { method: 'GET' })
    if (!r.ok) return // 404 while fork's mint endpoint is pending → no token, degrade clean
    const d = await r.json()
    const t = d && (d.token || d.operator_session || d.session)
    if (typeof t === 'string' && t) token = t
  } catch {
    /* offline / route down → no token; reads still work, consequential ops gate until a real mint */
  }
}

export function getOperatorToken(): string | null {
  return token
}

// INSTALL — wrap window.fetch ONCE so EVERY same-origin /api request the surface makes carries the token when held.
// A single interceptor (not per-call wiring) is the SAFER design: it can't miss a consequential call, and a missed
// call would 401 the instant enforcement flips. Reads carry it harmlessly (fork ignores it on non-consequential).
// Preserves the caller's headers/init exactly; only adds the one header. EventSource (the SSE /api/stream) is a
// separate API the interceptor doesn't touch — it's a read, runs free, fine.
export function installOperatorSessionFetch(): void {
  if (installed) return
  installed = true
  const orig = window.fetch.bind(window)
  window.fetch = (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    try {
      const url = typeof input === 'string' ? input : input instanceof URL ? input.href : (input as Request).url
      if (token && url && isOwnApi(url)) {
        const headers = new Headers(init?.headers || (input instanceof Request ? input.headers : undefined))
        if (!headers.has('X-Operator-Session')) headers.set('X-Operator-Session', token)
        // string/URL input → carry the merged headers on init; Request input → rebuild with merged headers.
        if (typeof input === 'string' || input instanceof URL) return orig(input, { ...init, headers })
        return orig(new Request(input as Request, { headers }), init)
      }
    } catch {
      /* never let the interceptor break a request — fall through to the original fetch */
    }
    return orig(input as RequestInfo, init)
  }
}

// the one call App init makes: install the interceptor, then mint (fire-and-forget — the interceptor picks the
// token up as soon as the mint resolves; requests before then simply carry no token, which is fine pre-enforcement).
export function installOperatorSession(): void {
  installOperatorSessionFetch()
  void mintOperatorSession()
}
