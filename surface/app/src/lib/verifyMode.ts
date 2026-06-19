// VERIFICATION MODE — the dry-run guard that lets a verifier (an away-sprint loop fire, a critic agent, me)
// DRIVE the REAL surface — open a decision, click an option, walk a flow — WITHOUT persisting a real
// decision_take. WHY THIS EXISTS (root cause, not a bandaid):
//
//   A take is written source=operator — INDISTINGUISHABLE from Tim's own answer. An automated verification
//   drive of the real surface has now twice written GHOST takes that made a decision Tim never answered read
//   "decided": cluster-identity on 2026-06-18 (retracted 00:31 by fork), then a fresh 7-take burst at
//   2026-06-19 03:20:20–27 AFTER the retract (the signature of an automated drive — most likely a prior fire
//   of this very loop, which runs every ~7 min and does exactly this verification). "Retract again" is a
//   bandaid: the 00:31 retract was undone by the 03:20 burst. The DURABLE fix is to SUPPRESS the persist
//   while verifying — so a verification drive can never contaminate a real decision.
//
// EXPLICIT + DEFAULT-SAFE: ON only when the URL carries ?verify (e.g. ?verify=1). Tim's canonical operator
// URL (https://workstation001.tail777bc2.ts.net:8443/) carries NO param → real writes, ALWAYS. A verifier
// opens the surface with ?verify=1.
//
// LOUD, NEVER SILENT (the no-silent-failure law): a silently-dropped take is the exact failure that law
// guards against. So verification mode shows a PERSISTENT banner ("Verification mode — your takes are NOT
// being saved", rendered in App) AND a per-click Notice naming the suppressed take. The default path is the
// only path that writes; suppression is always announced.
//
// SCOPE: this guards the decision TAKE (the contamination that actually happened). Generic annotations
// (comment/reaction/favour) ride wildcard/fork's separate gallery:direction → HOOK 2 write, not this
// dispatcher — fork can mirror this guard there if verification of annotations becomes a contamination path.
export function isVerifyMode(): boolean {
  try {
    return new URLSearchParams(window.location.search).has('verify')
  } catch {
    return false // SSR / no location — default to the SAFE real-write path is wrong here; no location means
    // no surface to verify, so false (real-write) is correct: this only runs in the browser anyway.
  }
}
