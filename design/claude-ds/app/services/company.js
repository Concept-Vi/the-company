// services/company.js — the COMPANY runtime kind ('company-http') for CV_AI/CV_HOST.
//
// A2 of the AI FUSION (union, not bridge): the Company is the ONE home of the AI;
// this file is the browser-side WIRE that lets the projection (CV_AI) fire entries
// through it. It registers a RUNTIME KIND into the CV_HOST seam (A1's registerKind)
// — so ai-registry.js needs no edit: a provider record declaring
//   runtime:{ kind:'company-http', api:'/api/cognition', completeRole:'complete' }
// resolves here. ALL config (routes, the completion role id) lives on the PROVIDER
// RECORD (one home, ai-seed.js) — nothing is hardcoded in this service.
//
// TRANSPORT (READ-5, verified): the bridge (:8770) sends no CORS and binds loopback.
// This service fetches SAME-ORIGIN relative paths (/api/...), so it works on any
// surface served same-origin to the bridge (the vite /api proxy on :5174, or a
// bridge-served page) and FAILS LOUD anywhere else (e.g. the static :8775 Studio)
// — honest unavailability, never a silent fallback.
//
// THE TRAP (READ-6, verified in cognition.py:431/450): run_role frames requests as
//   system = role.prompt_template · user = "Utterance: {utterance}".
// So complete() fires a PASSTHROUGH ROLE (default id 'complete', a ~/company
// roles/*.py data drop whose template says "the utterance IS the prompt") — the
// union way: the plain completion is a ROLE like everything else, no second
// engine path, no double-prompt (the browser prompt rides as the utterance).
//
// GUARDS (READ-4/5/6 — the silent-failure traps, all loud here):
//   · non-2xx → throw          · transport error → throw with the same-origin hint
//   · ok:false inside HTTP-200 → throw   · JSON-parse failure → throw
//   · missing output/vector → throw      · embed: no ensure:true (fails loud if embedder down)
(function () {
  'use strict';

  function fail(msg) { throw new Error('[cvCompany] ' + msg); }

  // ---- the one fetch discipline (loud on every failure mode) ---------------
  async function post(api, path, body) {
    const url = String(api).replace(/\/$/, '') + path;
    let res;
    try {
      res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
    } catch (e) {
      fail('transport error POSTing ' + url + ' — this surface must be SAME-ORIGIN to the bridge ' +
           '(vite /api proxy on :5174, or bridge-served); the static Studio (:8775) cannot reach it. (' + e.message + ')');
    }
    const txt = await res.text();
    if (!res.ok) fail(url + ' → HTTP ' + res.status + ': ' + txt.slice(0, 300));
    let json;
    try { json = JSON.parse(txt); } catch (e) { fail(url + ' returned non-JSON: ' + txt.slice(0, 300)); }
    if (json && json.ok === false) fail(url + ' returned ok:false inside HTTP 200 (the silent-fail trap): ' + txt.slice(0, 300));
    if (json && json.error) fail(url + ' returned error: ' + String(json.error).slice(0, 300));
    return json;
  }

  // ---- flatten CV_AI's promptOrOpts into ONE utterance string ---------------
  // CV_AI.complete accepts a string OR { messages:[{role,content}...] } OR { prompt }.
  // The Company's run_role takes ONE utterance; messages flatten with role labels.
  function toUtterance(promptOrOpts) {
    if (typeof promptOrOpts === 'string') return promptOrOpts;
    if (promptOrOpts && Array.isArray(promptOrOpts.messages)) {
      return promptOrOpts.messages
        .map(m => (m.role ? m.role.toUpperCase() + ': ' : '') + String(m.content == null ? '' : m.content))
        .join('\n\n');
    }
    if (promptOrOpts && typeof promptOrOpts.prompt === 'string') return promptOrOpts.prompt;
    fail('complete(): unsupported prompt shape — expected string | {messages} | {prompt}, got ' + typeof promptOrOpts);
  }

  // ---- the runtime a provider record resolves to ---------------------------
  // p = the full provider record; cfg = p.runtime ({kind, api, completeRole, ...}).
  function makeRuntime(p) {
    const cfg = (p && p.runtime) || {};
    const api = cfg.api;
    if (!api) fail('provider "' + (p && p.id) + '" runtime declares no api base (runtime.api) — refusing to guess a route');
    return {
      kind: 'company-http',
      providerId: p.id,

      // text completion → the passthrough role via run_role (the union path).
      async complete(promptOrOpts) {
        const role = cfg.completeRole;
        if (!role) fail('provider "' + p.id + '" declares no runtime.completeRole — the passthrough role id must live on the provider record');
        const utterance = toUtterance(promptOrOpts);
        const j = await post(api, '/run_role', { role: role, utterance: utterance });
        const out = j && j.output;
        if (out == null) fail('/run_role (' + role + ') returned no output: ' + JSON.stringify(j).slice(0, 200));
        // a passthrough role's schema is {text}; tolerate a bare-string output but never fabricate.
        if (typeof out === 'string') return out;
        if (typeof out.text === 'string') return out.text;
        fail('/run_role (' + role + ') output has no text field: ' + JSON.stringify(out).slice(0, 200));
      },

      // fire ANY role with structured output (the capabilities-become-roles path; A5's extract/compose ride this).
      async runRole(role, utterance, extra) {
        if (!role) fail('runRole(): role id required');
        const body = Object.assign({ role: role, utterance: String(utterance == null ? '' : utterance) }, extra || {});
        const j = await post(api, '/run_role', body);
        if (j && j.output == null) fail('/run_role (' + role + ') returned no output: ' + JSON.stringify(j).slice(0, 200));
        return j;   // { role, op, output, address, turn_id }
      },

      // embed → a real vector (2560-dim pplx today; dim asserted non-empty, never assumed).
      async embed(text) {
        if (typeof text !== 'string' || !text.trim()) fail('embed(): non-empty text required');
        const j = await post(api, '/embed', { text: text });
        const v = j && j.output && j.output.vector;
        if (!Array.isArray(v) || v.length === 0) fail('/embed returned no vector: ' + JSON.stringify(j).slice(0, 200));
        return { vector: v, dim: v.length, model: j.output.model || null };
      },
    };
  }

  // ---- register the KIND into the CV_HOST seam (A1 built exactly this) ------
  const HOST = (typeof window !== 'undefined') && window.CV_HOST;
  if (!HOST || typeof HOST.registerKind !== 'function') {
    fail('CV_HOST.registerKind unavailable — services/company.js must load AFTER ai/host-runtime.js (check app/index.html order)');
  }
  HOST.registerKind('company-http', makeRuntime);

  // the service surface (debug/direct use mirrors cvOpenAI's window-global shape)
  window.cvCompany = { makeRuntime: makeRuntime };
})();
