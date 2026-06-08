// THE STUDIO'S INTEGRATION SEAMS — wired vs PENDING (layer ③ of the Application-Structure Pack).
//
// WHY THIS FILE EXISTS: the pack's law is REUSE, never reinvent (the standalone studio's sin). So every
// seam the studio uses is declared here against the REAL backend, split honestly into:
//   · WIRED   — the seam exists on the worktree backend and the studio calls it today (file:line below).
//   · PENDING — the seam is genuinely NET-NEW (no single resolver exists yet). Declared as a typed stub
//               that FAILS LOUD / visibly marks "pending backend bind" — so the architecture is VISIBLE
//               even where the bind doesn't exist, WITHOUT faking it (a fake stub would mislead Claude
//               Design about what's available). Calling a PENDING seam throws a labelled error.
//
// The verified divergence from the lane brief's PENDING list (the brief's SHOULD-BE tags were stale —
// confirmed against code, per the intent-studio finding §5.4): I2 /api/act and the build-intent door
// (surface_intent_at) and R1-on-chat-focus ARE built and reachable. They are WIRED, not pending.

// ── WIRED SEAMS (the studio binds these to the real backend today) ───────────────────────────────────
// Each entry is the contract the studio relies on; the actual call lives in api.ts / useAppController.ts.
export const STUDIO_WIRED = {
  // the gallery corpus — registry-is-truth (the disk listing), NOT a hardcoded FE list. (NET-NEW route this lane.)
  corpus:            { route: 'GET /api/corpus',            via: 'api.corpus()',             backend: 'runtime/bridge.py _corpus_index' },
  // the focus→locus→context-at-address channel: a ui:// in focus.selected sets the R1 backend-held locus.
  chatAtLocus:       { route: 'POST /api/chat',             via: 'sendChat → api.chat(m,{selected:[ui://…]})', backend: 'runtime/suite.py:4471 chat / _chat_context (R1 set)' },
  // attach a comment at a ui:// locus — into the SHARED address-keyed annotation store (NOT the jsonl).
  annotate:          { route: 'POST /api/annotate',         via: 'annotateLocus → fetch /api/annotate',        backend: 'runtime/suite.py:3967 annotate' },
  // read the comment THREAD back at a locus (the persist-to-shared-store proof).
  annotationsAt:     { route: 'GET /api/annotations?address=', via: 'api.annotations(addr)',  backend: 'runtime/suite.py:4030 annotations_at' },
  // what-this-is + what-a-change-touches at a locus (the composed D1 affordance resolver).
  addressHelp:       { route: 'GET /api/address-help?address=', via: 'api.addressHelp(addr)', backend: 'runtime/suite.py:1959 address_help / 6929 resolve_scope' },
  // the altitude transform of a system artifact at the locus.
  upTranslate:       { route: 'GET /api/up-translate',      via: 'api.upTranslate(kind,ref)', backend: 'runtime/suite.py:5100 up_translate' },
  // I2 — the address-keyed command seam the I3 approve card fires on CONSENT (click #2). WIRED (stale brief).
  act:               { route: 'POST /api/act',              via: 'api.act(verb,addr,args) (approveProposal)',  backend: 'runtime/bridge.py:1052 / suite.py _dispatch_rhm_action' },
  // the build-intent door — mint a change-request FROM a locus (resolved=None, plan-mode). WIRED (stale brief);
  // surface_intent_at is built. The L1 ADDRESSED-FEEDBACK→INTENT *single resolver* is the pending leg (below).
  intentAt:          { route: 'POST /api/intent-at',        via: 'mintBuildIntent → api.intentAt(addr,text)',  backend: 'runtime/bridge.py:626 surface_intent_at' },
  // IN-FRAME ELEMENT DEIXIS (BUILT this lane, moved up from PENDING per this file's contract): clicking a
  // sub-element INSIDE the staged mockup indicates ITS ui:// address (not just the whole reviewed surface).
  // NOT an /api route — a postMessage bridge: the bridge injects a sandboxed capture script before </body> on
  // the studio serving path (iframe src '/mockups/<file>?studio=1'), which postMessages the nearest ui://
  // data-ui-ref up to the parent; the Stage (StudioKit.tsx) listens (same-origin + envelope-type + ui:// guards)
  // and calls the EXISTING setReviewMockup(file, addr) locus sink (no parallel store, no iframe remount).
  // Fail-soft: a no-ui://-ref click posts nothing → the locus stays at the whole-mockup address. Proven by-use
  // (click ui://toolbar/run inside the mockup → Stage badge + Composer locus updated; no-ref click → unchanged).
  inFrameDeixis:     { route: 'postMessage {type:studio-deixis,address} (no /api route)', via: 'Stage window message listener → setReviewMockup(file, addr) → indicate(addr)', backend: 'runtime/bridge.py mockup-serving ?studio=1 capture-script injection' },
} as const

// ── PENDING SEAMS (genuinely net-new — declared, NOT faked) ──────────────────────────────────────────
// Shape: a typed descriptor + a throwing call. Importing it makes the seam VISIBLE in the architecture;
// invoking it FAILS LOUD with the pending label (never a silent no-op, never a fake success). When the
// backend bind lands, replace the body with the real api call and move the entry into STUDIO_WIRED.
export type PendingSeam = {
  id: string
  what: string
  why_pending: string
  designed_test: string   // the named acceptance test that will prove it (from the Interactive Addressed Surface criteria)
}

export const STUDIO_PENDING: Record<string, PendingSeam> = {
  // R2 — the addressed-context READ-face. The BACKEND RESOLVER is now BUILT (Suite.context_at composes the
  // EXISTING `_r2_gather` + `_r2_score_and_cap` — the same R2 engine the chat runs — behind GET /api/context;
  // malformed→400, well-formed-but-unattached→honest-empty/DENY-ALL). What remains PENDING is the FE CONSUMER:
  // no studio region calls /api/context yet (the per-leg reads — annotation thread + address-help — serve the
  // panel today). So this stays a declared seam until an addressed-context INSPECTOR region (on AddressHelp /
  // RhmPanel) binds api.context(address). Catalogued as `to_wire` in Suite._ORPHAN_ROUTES for that connect-it
  // backlog. NB the GET /api/context literal here is what keeps the route reachability-WIRED (a real FE
  // declaration referencing it) without a false "calls it today" claim.
  R2_CONTEXT_AT_ADDRESS: {
    id: 'R2',
    what: 'GET /api/context?address= — the address-keyed context bundle (annotations + chats + addressed events at the locus AND its ancestors, scored + budget-capped by the recency·proximity·pin decay)',
    why_pending: 'the BACKEND resolver is BUILT (Suite.context_at / GET /api/context, proven by addr_context_acceptance + by-use curl); the pending leg is the FE CONSUMER — an addressed-context inspector region binding api.context(address). DESIGNED, ☐.',
    designed_test: 'addr_context_acceptance.py',
  },
  // I4 — a click's governance TIER resolved by the address's union-record governance field (not the verb),
  // so a bare run/build stays AUTO but a tiered address escalates. The live face gates by verb, not address.
  I4_ADDRESS_TIER: {
    id: 'I4',
    what: 'address → governance tier — a click\'s consent tier resolved from the address\'s union-record governance field',
    why_pending: 'the live gate is per-verb (guard() + address→tier is not the gating key yet). DESIGNED, ☐.',
    designed_test: 'click_tier_acceptance.py',
  },
  // R1-persistent — a server-side PERSISTENT operator current-locus (set on indicate, survives across calls),
  // beyond the per-payload ui_target stamping + the per-chat focus.selected locus. The studio indicates via
  // focus.selected each turn (which IS the R1-on-chat path); a standing server-held locus is the net-new half.
  R1_PERSISTENT_LOCUS: {
    id: 'R1',
    what: 'backend persistent current-locus — the server holds the operator\'s current ui:// locus across calls (set on indicate), not only per-chat-turn via focus.selected',
    why_pending: 'partially present (ui_target stamping + per-turn focus locus); a standing server-side current-locus is DESIGNED, ☐.',
    designed_test: '(R1 — Interactive Addressed Surface criteria)',
  },
  // L1 — the ADDRESSED-FEEDBACK→BUILD-INTENT single resolver: a comment-at-address auto-becomes a build-intent
  // (spec + scope[] via S3) surfaced for approval AT that address. surface_build_intent/surface_intent_at are
  // built (so the studio's "request a change" door is WIRED), but the AUTO leg — a plain COMMENT promoting
  // itself into an intent — is the net-new bind.
  L1_COMMENT_TO_INTENT: {
    id: 'L1',
    what: 'addressed-comment → build-intent (auto) — a comment-at-address surfaces_build_intent with spec + scope[] derived from the address, for approval at that address',
    why_pending: 'the explicit "request a change" door (intentAt) IS wired; the AUTO promotion of a plain comment into an intent is unbuilt. DESIGNED, ☐.',
    designed_test: '(L1 — Interactive Addressed Surface criteria)',
  },
  // (IN-FRAME DEIXIS — was here — is now BUILT and moved into STUDIO_WIRED above as `inFrameDeixis` (the
  //  bridge ?studio=1 capture-script → postMessage → Stage listener → setReviewMockup locus sink). Per this
  //  file's contract: "when the backend bind lands, move the entry into STUDIO_WIRED.")
}

// Invoking a pending seam FAILS LOUD (rule 4 — never a silent no-op, never a fake success). A region that
// wires a not-yet-built control to one of these gets a labelled throw the operator/dev sees, making the
// missing bind VISIBLE at the point of use rather than silently doing nothing.
export function callPendingSeam(key: keyof typeof STUDIO_PENDING): never {
  const s = STUDIO_PENDING[key]
  throw new Error(
    `[studio · PENDING SEAM ${s.id}] "${s.what}" is not yet bound to the backend — ${s.why_pending} ` +
    `(designed test: ${s.designed_test}). This is a declared net-new seam, not a silent no-op.`
  )
}
