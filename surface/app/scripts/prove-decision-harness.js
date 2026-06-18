// prove-decision-harness.js — the READY prove-on-one harness (lead-directed, t-1781758984).
//
// Runs the FULL decision loop against a decision address and asserts EVERY leg, so the moment the decision-
// card fork's render lands, the prove-on-one runs SAME-SECOND with a per-leg verdict. Browser-side (the loop
// is host events + DOM). Run it in the live surface via chrome-devtools/console:
//
//   // paste this file's `proveDecision` into the page, then:
//   await proveDecision('decision://global/<id>')                    // SHOW legs (resolve/host/ask) — safe, no take
//   await proveDecision('decision://global/<THROWAWAY-id>', { decide: '<option label>' })  // FULL loop incl. the take
//
// ★ Pass `decide` ONLY on a THROWAWAY decision (it flips real state). For a REAL decision, run without
//   `decide` to verify resolve+host+ask, then let the OPERATOR make the real choice (that IS the prove-on-one).
//
// Two modes, auto-detected: REAL-CARD (the fork's render is already mounted in #gallery-mount → assert it) vs
// SYNTHETIC (no real card yet → drive a stub decision:rendered so host+ask legs are still exercised in test).
//
// Returns { pass, mode, legs:[{leg, ok, detail}] }. ok===null = leg skipped (not counted in pass).

async function proveDecision(addr, opts = {}) {
  const wait = (ms) => new Promise((r) => setTimeout(r, ms))
  const legs = []
  const log = (leg, ok, detail) => legs.push({ leg, ok, detail })
  const done = (mode) => {
    const checked = legs.filter((l) => l.ok !== null)
    return { pass: checked.length > 0 && checked.every((l) => l.ok), mode, legs }
  }

  // LEG 1 — RESOLVE: /api/territory returns a decision.record with the contract shape the card renders from.
  let resolved = null
  try { resolved = await (await fetch('/api/territory?address=' + encodeURIComponent(addr))).json() }
  catch (e) { log('resolve', false, 'fetch failed: ' + e); return done('error') }
  const idy = resolved.identity || {}
  log('resolve', resolved.scheme === 'decision' && idy.id != null && Array.isArray(idy.options) && idy.state != null,
      { scheme: resolved.scheme, state: idy.state, options: (idy.options || []).map((o) => o.label), subtype: idy.subtype || null })

  // LEG 2 — HOST OPEN + the card mounts. REAL-CARD if #gallery-mount already holds a non-stub card for this
  // addr (the fork rendered it); else SYNTHETIC: drive a stub decision:rendered so host+ask are still exercised.
  const mount = document.getElementById('gallery-mount')
  const existing = mount && mount.firstElementChild && !mount.querySelector('[data-harness-stub]')
  const mode = existing ? 'real-card' : 'synthetic'
  let root = existing ? mount.firstElementChild : null
  if (!existing) {
    root = document.createElement('div'); root.setAttribute('data-harness-stub', '1')
    if (mount) { mount.innerHTML = ''; mount.appendChild(root) }
    window.dispatchEvent(new CustomEvent('decision:rendered', { detail: { element: root, address: addr, subtype: idy.subtype || 'binary', render_kind: idy.render_kind || 'slide' } }))
    await wait(700)
  }
  const frame = document.querySelector('.gallery-frame')
  log('host-open', !!document.querySelector('.gallery-overlay--open'),
      { overlayOpen: !!document.querySelector('.gallery-overlay--open'), advertisedSubtype: frame ? frame.getAttribute('data-decision-subtype') : null })

  // LEG 3 — the in-card ASK mounted (fork HOOK 1b binds on decision:rendered.element).
  const ask = (root && (root.querySelector('.brain-ask') || (root.innerText || '').includes('Ask'))) || !!document.querySelector('#gallery-mount .brain-ask')
  log('in-card-ask', !!ask, { found: !!ask })

  // LEG 4 — the TAKE flips state pending→decided (uses the REAL take path; only when opts.decide is given).
  if (opts.decide != null) {
    const before = idy.state
    const binder = window.galleryBinder
    let reRendered = false
    window.addEventListener('decision:rendered', () => { reRendered = true }, { once: true })
    if (binder && binder.decide) binder.decide(addr, opts.decide)
    else window.dispatchEvent(new CustomEvent('gallery:verb', { detail: { verb: 'annotate', aim_address: addr, payload: { mark_type: 'decision_take', value: opts.decide, is_decision_take: true } } }))
    await wait(1400)
    const after = ((await (await fetch('/api/territory?address=' + encodeURIComponent(addr))).json()).identity) || {}
    log('take-flips-state', before === 'pending' && after.state === 'decided' && after.decided_value === opts.decide,
        { before, after: after.state, decided_value: after.decided_value })
    // LEG 5 — the REFRESH loop: the take's write fired gallery:rerender → host re-rendered the decided card.
    log('rerender-refresh', reRendered === true, { hostReRendered: reRendered })
  } else {
    log('take-flips-state', null, 'skipped — pass opts.decide=<option label> on a THROWAWAY to test the take; on a REAL decision let the operator choose')
    log('rerender-refresh', null, 'skipped (depends on the take)')
  }

  return done(mode)
}

if (typeof window !== 'undefined') window.proveDecision = proveDecision
if (typeof module !== 'undefined') module.exports = { proveDecision }
